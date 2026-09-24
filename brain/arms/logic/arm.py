# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 19:20 +0400 — the Arm-conforming wrapper
#   for A2 (recurrent differentiable logic-gate network), written after brain/protocol.py
#   froze at ac7d2ff. Reuses brain.arms.soft.steps' StepEncoder/SlotTable/dimension constants
#   DELIBERATELY (both directories are Builder 3's own — B1-PREREG.md §9's fence forbids
#   touching OTHER builders' arms, not re-using one's own encoding across one's own arms; a
#   second, independent tokenizer for the identical tape-row shapes would be pure duplication
#   with no isolation benefit).
#
# What differs from A1 (brain/arms/soft/arm.py), per B1-PREREG.md §4 row A2's own words:
#   - Inputs are BINARISED (the glance block thresholded at its median over TEACH glances,
#     RunningBinariser, frozen at the first SLEEP row — same declared timing as
#     brain/arms/logic/engine.py's own docstring); the letter/cue/kind one-hot blocks are
#     already 0/1 and pass through unchanged.
#   - No WORLD head: A2's row names no self-supervised next-step objective, only "trained
#     through its relaxation" from FEEDBACK — so `fit_event` on TEACH/ASK rows only ADVANCES
#     the recurrent bit-state (a plain forward pass, no gradient); the only backward pass in
#     this arm happens in `_fit_feedback`.
#   - "Awake: truncated BPTT over the last 8 steps per event" — implemented the SAME way A1's
#     fix ended up needing anyway (build the graph FRESH at feedback time, from a stored
#     `h_start` + the ask's own steps, CAPPED to the last 8): never a stale graph across the
#     answer()/fit_event() boundary in the first place.
#   - PICK has no bilinear scorer of its own (PREREG's shared A2/A3 note): each candidate is
#     scored by re-running the network on (cue, operands, THIS candidate) and reading ONE
#     dedicated MATCH group; the highest-scoring candidate wins.
#   - Group layout (declared, D21): groups [0, name_cap) = NAME classes (index = order of
#     first hearing, mirroring NameAnswerHead.names); group[name_cap] = NO, group[name_cap+1]
#     = YES; group[name_cap+2] = MATCH (PICK). `n_gates` (the final layer's width) must be a
#     multiple of `n_groups = name_cap + 3` — RAISED to the seat for the real run's config
#     (2048 is not a multiple of any name_cap between 1 and 64 plus 3 that also matches the
#     PREREG's other declared widths; a toy/small-scale run picks its own compatible sizes,
#     as this file's tests do).
from __future__ import annotations

import collections
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

import torch
import torch.nn.functional as F

from brain.arms.logic.engine import LogicBPTTTrainer, RecurrentDiffLogicGateNetwork, RunningBinariser
from brain.arms.soft.steps import GLANCE_DIM, SlotTable, StepEncoder
from brain.glance_cache import Cache
from brain.protocol import Answer, AnswerKind, VALENCE_NO, VALENCE_REWARD, canonical_json

RING_CAPACITY = 20000
BPTT_WINDOW = 8  # PREREG §4 row A2: "truncated BPTT over the last 8 steps per event"


def _binarise_step(step: torch.Tensor, binariser: RunningBinariser) -> torch.Tensor:
    glance = step[:GLANCE_DIM]
    rest = step[GLANCE_DIM:]
    return torch.cat([binariser.binarise(glance), (rest > 0.5).float()])


class ArmA2:
    """Conforms to `brain.protocol.Arm`. See module docstring for D21 (group layout) and the
    differences from ArmA1 this file's own docstring lists."""

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.seed = int(seed)
        self.config = dict(config)
        self.name_cap = int(self.config.get("name_cap", 16))
        self.n_groups = self.name_cap + 3
        n_gates = int(self.config.get("n_gates", self.n_groups * 2))
        if n_gates % self.n_groups != 0:
            raise ValueError(f"n_gates ({n_gates}) must be a multiple of n_groups ({self.n_groups}) — D21")

        from brain.arms.soft.steps import STEP_DIM  # local import: avoids a hard cycle at module load

        self.net = RecurrentDiffLogicGateNetwork(
            n_input_bits=STEP_DIM,
            n_layers=int(self.config.get("n_layers", 2)),
            n_gates=n_gates,
            recurrent_bits=int(self.config.get("recurrent_bits", 16)),
            n_groups=self.n_groups,
            seed=self.seed,
        )
        self.trainer = LogicBPTTTrainer(
            self.net.parameters(), lr=float(self.config.get("lr", 0.05)), momentum=0.9, clip=1.0
        )
        self.binariser = RunningBinariser(dim=GLANCE_DIM)
        self._frozen_binariser = False

        self.cache: Optional[Cache] = None
        cache_dir = self.config.get("cache_dir")
        if cache_dir:
            self.cache = Cache(cache_dir)
        self.slots = SlotTable()
        self.encoder = StepEncoder(self.cache, self.slots) if self.cache is not None else None

        self.names: List[str] = []  # heard names; index = NAME group index (D21)
        self.names_refused = 0  # #233's law: a cap's refusals are a SERIES, never silently eaten
        self.h_bits = self.net.zero_state()
        self._pending: Dict[int, Dict[str, Any]] = {}
        self._arrival_id = 0
        self._events = 0
        self._ms = 0.0

    # ------------------------------------------------------------------------------- helpers
    def _require_encoder(self) -> StepEncoder:
        if self.encoder is None:
            raise RuntimeError("ArmA2 constructed without config['cache_dir'] — cannot encode any row")
        return self.encoder

    def _bin_steps(self, steps: List[torch.Tensor]) -> List[torch.Tensor]:
        return [_binarise_step(s, self.binariser) for s in steps]

    def _advance_bits(self, steps: List[torch.Tensor]) -> None:
        """Pure forward: advances self.h_bits, no gradient (D-earlier: A2 has no self-
        supervised WORLD objective; see module docstring). Calibration is the CALLER's job
        (fit_event's TEACH branch only, PREREG: 'thresholded at its median over the TEACH
        glances') — a real bug caught by re-reading this file before its own test ran: an
        earlier draft observed here too, on the ALREADY-BINARISED (0/1) glance block rather
        than the raw one, for every ASK step as well as every TEACH step. Observing a bit
        instead of the raw value would have corrupted the running median outright, and
        observing ASK operands would have calibrated against a population the PREREG never
        names."""
        with torch.no_grad():
            h = self.h_bits
            for x in self._bin_steps(steps):
                _, h = self.net(x, h, discretise=False)
            self.h_bits = h

    # ------------------------------------------------------------------------------- fit_event
    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        t0 = time.perf_counter()
        kind = row["kind"]
        enc = self._require_encoder()
        if kind == "TEACH":
            steps = enc.teach_steps(row["payload"])
            if not self._frozen_binariser:
                for s in steps:
                    self.binariser.observe(s[:GLANCE_DIM])
            self._advance_bits(steps)
            name = row["payload"]["name"]
            if name not in self.names:
                if len(self.names) < self.name_cap:
                    self.names.append(name)
                else:
                    self.names_refused += 1
        elif kind == "ASK":
            steps = enc.ask_steps(row["payload"])
            self._advance_bits(steps)
        elif kind == "FEEDBACK":
            self._fit_feedback(row, valence)
        elif kind == "ARRIVAL":
            self._arrival_id += 1
        elif kind == "SLEEP":
            pass  # SLEEP never reaches fit_event (HarnessContract calls arm.sleep() instead)
        self._events += 1
        self._ms += (time.perf_counter() - t0) * 1000.0

    def _fit_feedback(self, row: Mapping[str, Any], valence: Optional[str]) -> None:
        p = row["payload"]
        ask_seq = int(p["ask_seq"])
        entry = self._pending.pop(ask_seq, None)
        if entry is None:
            return
        right = p["right"]
        family = entry["answer_kind"]
        if family == "NAME":
            if right not in self.names:
                return
            target_idx = self.names.index(right)
        elif family == "YESNO":
            target_idx = self.name_cap if right == "NO" else self.name_cap + 1
        elif family == "PICK":
            target_idx = int(right)  # index into candidate_rows; scored against MATCH group per candidate
        else:
            return

        h_start = entry["h_start"]
        window_steps = self._bin_steps(entry["ask_steps"][-BPTT_WINDOW:])
        h = h_start
        for x in window_steps:
            groups, h = self.net(x, h, discretise=False)
        if family == "PICK":
            cand_rows = entry["candidate_rows"]
            scores = []
            for cr in cand_rows:
                hc = h
                for x in self._bin_steps(self.encoder.candidate_steps(int(cr))):
                    g, hc = self.net(x, hc, discretise=False)
                scores.append(g[self.name_cap + 2])  # the MATCH group
            logits = torch.stack(scores) if scores else torch.zeros(0)
        elif family == "NAME":
            logits = groups[: self.name_cap]
        else:  # YESNO
            logits = groups[self.name_cap : self.name_cap + 2]
            target_idx = target_idx - self.name_cap

        if logits.numel() == 0 or target_idx >= logits.shape[-1]:
            return
        loss = F.cross_entropy(logits.unsqueeze(0), torch.tensor([target_idx]))
        given_idx = entry.get("given_index")
        if valence == VALENCE_NO and given_idx is not None and given_idx != target_idx and given_idx < logits.shape[-1]:
            loss = loss + torch.clamp(logits[given_idx], min=-10.0)
        self.trainer.step(loss)
        self.net.observe_training_margin(logits.detach())

    # ------------------------------------------------------------------------------- answer
    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        t0 = time.perf_counter()
        try:
            return self._answer_impl(ask_row, learn)
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    def _answer_impl(self, ask_row: Mapping[str, Any], learn: bool) -> Answer:
        enc = self._require_encoder()
        p = ask_row["payload"]
        family = p["answer_kind"]
        with torch.no_grad():
            h_start = self.h_bits.clone()
            steps = enc.ask_steps(p)
            h = h_start
            for x in self._bin_steps(steps):
                groups, h = self.net(x, h, discretise=True)

            entry: Dict[str, Any] = {"answer_kind": family, "h_start": h_start, "ask_steps": steps}
            ans: Answer

            if family == "NAME":
                if not self.names:
                    ans = Answer(kind=AnswerKind.UNKNOWN)
                else:
                    logits = groups[: len(self.names)]
                    given_idx = int(logits.argmax())
                    if self.net.should_abstain(logits):
                        ans = Answer(kind=AnswerKind.UNKNOWN)
                    else:
                        ans = Answer(kind=AnswerKind.NAME, value=self.names[given_idx])
                        entry["given_index"] = given_idx
            elif family == "YESNO":
                logits = groups[self.name_cap : self.name_cap + 2]
                given_idx = int(logits.argmax())
                if self.net.should_abstain(logits):
                    ans = Answer(kind=AnswerKind.NOTHING)
                else:
                    ans = Answer(kind=(AnswerKind.NO if given_idx == 0 else AnswerKind.YES))
                    entry["given_index"] = given_idx + self.name_cap
            elif family == "PICK":
                cand_rows = list(p["candidate_rows"] or [])
                entry["candidate_rows"] = cand_rows
                scores = []
                for cr in cand_rows:
                    hc = h
                    for x in self._bin_steps(enc.candidate_steps(int(cr))):
                        g, hc = self.net(x, hc, discretise=True)
                    scores.append(g[self.name_cap + 2])
                scores_t = torch.stack(scores) if scores else torch.zeros(0)
                if scores_t.numel() == 0 or self.net.should_abstain(scores_t):
                    ans = Answer(kind=AnswerKind.NOTHING)
                else:
                    given_idx = int(scores_t.argmax())
                    ans = Answer(kind=AnswerKind.PICK, value=given_idx)
                    entry["given_index"] = given_idx
            else:
                ans = Answer(kind=AnswerKind.NOTHING)

        if learn and ans.kind not in (AnswerKind.UNKNOWN, AnswerKind.NOTHING, AnswerKind.SILENT):
            self._pending[int(ask_row["seq"])] = entry
        return ans

    # ------------------------------------------------------------------------------- sleep
    def sleep(self, steps: int) -> None:
        t0 = time.perf_counter()
        if not self._frozen_binariser:
            self.binariser.freeze()
            self._frozen_binariser = True
        self._events += int(steps)
        self._ms += (time.perf_counter() - t0) * 1000.0

    # ------------------------------------------------------------------------------- identity
    def state_sha(self) -> str:
        parts = []
        for name, t in sorted(self.net.state_dict().items()):
            parts.append(name.encode())
            parts.append(t.detach().contiguous().numpy().tobytes())
        parts.append(b"names=" + canonical_json(self.names).encode())
        parts.append(b"slots=" + self.slots.state_bytes())
        parts.append(b"h_bits=" + self.h_bits.detach().numpy().tobytes())
        thr = self.binariser.thresholds
        parts.append(b"binariser_thr=" + (thr.detach().numpy().tobytes() if thr is not None else b"unfrozen"))
        # the PRE-FREEZE accumulated rows affect future behaviour (what freeze() will compute)
        # even though thresholds is still None — a real bug this file's own resume test caught
        # (see RunningBinariser.state_dict's docstring) is exactly two binarisers with
        # identical thresholds=None but different accumulated populations; include them here
        # too so state_sha can no longer be blind to that difference.
        parts.append(b"binariser_rows=" + b"".join(t.detach().numpy().tobytes() for t in self.binariser._rows))
        parts.append(canonical_json({"margins": self.net._train_margins}).encode())
        return hashlib.sha256(b"|".join(parts)).hexdigest()

    def snapshot(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "net": self.net.state_dict(),
                "trainer": self.trainer.state_dict(),
                "names": self.names,
                "names_refused": self.names_refused,
                "h_bits": self.h_bits,
                "slots": self.slots.to_dict(),
                "binariser": self.binariser.state_dict(),
                "binariser_frozen": self._frozen_binariser,
                "margins": self.net._train_margins,
                "arrival_id": self._arrival_id,
                "events": self._events,
                "ms": self._ms,
            },
            path / "state.pt",
        )

    def load(self, path: Union[str, Path]) -> None:
        # weights_only=False: same trusted-internal-checkpoint rationale as brain/arms/soft/
        # arm.py's ArmA1.load (never untrusted input; written and read by this same class only).
        d = torch.load(Path(path) / "state.pt", weights_only=False)
        self.net.load_state_dict(d["net"])
        self.trainer.load_state_dict(d["trainer"])
        self.names = list(d["names"])
        self.names_refused = d.get("names_refused", 0)
        self.h_bits = d["h_bits"]
        self.slots = SlotTable.from_dict(d["slots"])
        self.encoder = StepEncoder(self.cache, self.slots) if self.cache is not None else None
        self.binariser.load_state_dict(d["binariser"])
        self._frozen_binariser = d["binariser_frozen"]
        self.net._train_margins = list(d["margins"])
        self._arrival_id = d["arrival_id"]
        self._events = d["events"]
        self._ms = d["ms"]
        self._pending = {}

    def cost(self) -> Dict[str, float]:
        return {"events": self._events, "ms": self._ms}
