# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 20:10 +0400 — the Arm-conforming wrapper
#   for A3 (multi-class Tsetlin machine), written after brain/protocol.py froze at ac7d2ff.
#
# A3 is NOT recurrent — a Tsetlin machine is a pure feedforward classifier over ONE flat bit
# vector per event (unlike A1/A2, which carry state across a row's own sub-steps). PREREG §4
# row A3 names the feature set ("the same binarised glance bits (5x144), letters, cue and kind
# bits, and a 64-bit register holding the previous TEACH name's one-hot") but not how a
# MULTI-OPERAND ask (AFTER/BEFORE take 2 glyph operands, BETWEEN takes 3) becomes one vector,
# since there is no sequence to walk. Declared here (D23-D25), RAISED to the seat alongside
# D1-D22:
#   D23. Up to MAX_OPERANDS=3 glance blocks (720 bits each, one per operand SLOT in the ask's
#        own operand order; an unused slot is all-zero) — order-sensitive relations (AFTER(X,Y)
#        != AFTER(Y,X)) need operand IDENTITY, which concatenation-by-slot preserves and a
#        single shared 720-bit block (OR'd across operands) would destroy.
#   D24. A name operand (POINT/IS only, per the protocol's own validate_tape_row rule: a cue is
#        either all-glyph-operand or POINT/IS with a name operand, never mixed) uses a
#        BAG-OF-LETTERS encoding (27 bits, one per letter incl. END, PRESENCE not position) —
#        Tsetlin clauses are inherently unordered conjunctions, so this is the natural fit, at
#        the declared cost of losing letter ORDER (an anagram of a taught name would look
#        identical; checked against B1's own name list — a-z singles and the ten digit words —
#        and no two are anagrams of each other, so this costs nothing on B1's actual vocabulary,
#        but is named as a real limitation for a future vocabulary that might collide).
#   D25. The "previous TEACH name" register (64 bits, one-hot, PREREG's own count) updates on
#        every TEACH row's fit_event and stays fixed until the next TEACH — a genuinely
#        stateful register, unlike everything else in this file's input, and the ONLY thing
#        that makes two otherwise-identical asks (asked before vs after a different TEACH)
#        distinguishable to a memoryless classifier.
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

import torch

from brain.arms.clauses.engine import MultiClassTsetlinMachine, TwoClassMatchMachine
from brain.arms.soft.steps import CUE_DIM, GLANCE_DIM, GLANCES_PER_ROW, KIND_DIM, LETTER_DIM, SlotTable, TAPE_KINDS
from brain.glance_cache import Cache
from brain.protocol import Answer, AnswerKind, VALENCE_NO, VALENCE_REWARD, canonical_json, is_name_operand, is_row_operand

MAX_OPERANDS = 3  # D23 (BETWEEN's own arity, the widest relation cue takes)
PREV_NAME_REGISTER_BITS = 64  # PREREG §4 row A3, verbatim
GLANCE_FLAT_BITS = GLANCES_PER_ROW * GLANCE_DIM  # 720

N_FEATURES = MAX_OPERANDS * GLANCE_FLAT_BITS + LETTER_DIM + CUE_DIM + KIND_DIM + PREV_NAME_REGISTER_BITS

_KIND_INDEX = {k: i for i, k in enumerate(TAPE_KINDS)}


def _binarise_glance(flat: torch.Tensor, thresholds: torch.Tensor) -> torch.Tensor:
    return (flat > thresholds).float()


class ArmA3:
    """Conforms to `brain.protocol.Arm`. See module docstring for D23-D25."""

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.seed = int(seed)
        self.config = dict(config)
        self.C = int(self.config.get("C", 8))  # PREREG default 200; small for tests (declared, not tuned, at scale)
        self.N = int(self.config.get("N", 100))
        self.T = int(self.config.get("T", 15))
        self.s = float(self.config.get("s", 3.9))
        self.name_cap = int(self.config.get("name_cap", PREV_NAME_REGISTER_BITS))

        self.tm = MultiClassTsetlinMachine(N_FEATURES, self.C, self.N, self.T, self.s, self.seed, self.name_cap)
        self.pick_machine = TwoClassMatchMachine(N_FEATURES, self.C, self.N, self.T, self.s, self.seed + 500000)

        self.cache: Optional[Cache] = None
        if self.config.get("cache_dir"):
            self.cache = Cache(self.config["cache_dir"])
        self.slots = SlotTable()

        self._glance_thresholds: Optional[torch.Tensor] = None  # frozen at first SLEEP, over TEACH glances
        self._glance_obs: List[torch.Tensor] = []
        self._frozen_binariser = False

        self.prev_name_idx: Optional[int] = None  # index into self.tm.names, or None before any TEACH
        self._pending: Dict[int, Dict[str, Any]] = {}
        self._events = 0
        self._ms = 0.0

    # ------------------------------------------------------------------------------- encoding
    def _flat_glance_bits(self, cache_row: int) -> torch.Tensor:
        feats = self.cache.glances(cache_row)  # (5,144) float64
        flat = torch.from_numpy(feats.reshape(-1).astype("float32"))  # (720,)
        thr = self._glance_thresholds if self._glance_thresholds is not None else torch.zeros(GLANCE_FLAT_BITS)
        return _binarise_glance(flat, thr)

    def _letter_bag(self, name: str) -> torch.Tensor:
        from brain.arms.soft.steps import LETTERS

        v = torch.zeros(LETTER_DIM)
        for ch in name:
            v[LETTERS.index(ch)] = 1.0
        v[len(LETTERS)] = 1.0  # END always present (D24: presence-only bag)
        return v

    def _prev_name_register(self) -> torch.Tensor:
        v = torch.zeros(PREV_NAME_REGISTER_BITS)
        if self.prev_name_idx is not None and self.prev_name_idx < PREV_NAME_REGISTER_BITS:
            v[self.prev_name_idx] = 1.0
        return v

    def _encode(self, cues: List[str], operands: List[Mapping[str, Any]], kind: str) -> torch.Tensor:
        glance_blocks = [torch.zeros(GLANCE_FLAT_BITS) for _ in range(MAX_OPERANDS)]
        letter_block = torch.zeros(LETTER_DIM)
        gi = 0
        for op in operands:
            if is_row_operand(op):
                if gi < MAX_OPERANDS:
                    glance_blocks[gi] = self._flat_glance_bits(int(op["value"]))
                    gi += 1
            elif is_name_operand(op):
                letter_block = self._letter_bag(str(op["value"]))
        cue_block = torch.zeros(CUE_DIM)
        for mark in cues:
            cue_block[self.slots.slot_of(mark)] = 1.0  # D-earlier (steps.py): a compound sets BOTH bits
        kind_block = torch.zeros(KIND_DIM)
        kind_block[_KIND_INDEX[kind]] = 1.0
        return torch.cat(glance_blocks + [letter_block, cue_block, kind_block, self._prev_name_register()])

    def _teach_vector(self, glance_row: int) -> torch.Tensor:
        return self._encode(cues=[], operands=[{"kind": "row", "value": glance_row}], kind="TEACH")

    # ------------------------------------------------------------------------------- fit_event
    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        t0 = time.perf_counter()
        kind = row["kind"]
        if kind == "TEACH":
            p = row["payload"]
            if not self._frozen_binariser:
                feats = self.cache.glances(int(p["glance_row"]))
                self._glance_obs.append(torch.from_numpy(feats.reshape(-1).astype("float32")))
            self.tm.hear_name(p["name"])
            self.prev_name_idx = self.tm.names.index(p["name"]) if p["name"] in self.tm.names else self.prev_name_idx
        elif kind == "ASK":
            pass  # a Tsetlin machine has no recurrent state an ASK's own content would advance
        elif kind == "FEEDBACK":
            self._fit_feedback(row, valence)
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
        # edit: Claude (Opus 5.5), 2026-09-26 13:01 +0400 — a PICK entry carries no `x` (each candidate is encoded on its own);
        # the old guard never held an abstained PICK, so `entry["x"]` here was only ever reached by NAME/YESNO entries.
        x = entry.get("x")
        event_seq = ask_seq
        if family == "NAME":
            if right not in self.tm.names:
                return
            self.tm.train_event(x, target_class=right, event_seq=event_seq, eligible=list(self.tm.names))
        elif family == "YESNO":
            self.tm.train_event(x, target_class=right, event_seq=event_seq, eligible=["YES", "NO"])
        elif family == "PICK":
            cand_rows = entry["candidate_rows"]
            target_idx = int(right)
            for i, cr in enumerate(cand_rows):
                x_cand = self._encode_pick_candidate(entry["cues"], entry["op_for_pick"], cr)
                self.pick_machine.train_event(x_cand, is_match=(i == target_idx), event_seq=event_seq * 100 + i)

    # ------------------------------------------------------------------------------- answer
    def _encode_pick_candidate(self, cues: List[str], base_operands: List[Mapping[str, Any]], candidate_row: int):
        ops = list(base_operands) + [{"kind": "row", "value": candidate_row}]
        return self._encode(cues, ops, kind="ASK")

    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        t0 = time.perf_counter()
        try:
            return self._answer_impl(ask_row, learn)
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    def _answer_impl(self, ask_row: Mapping[str, Any], learn: bool) -> Answer:
        p = ask_row["payload"]
        family = p["answer_kind"]
        cues = p["cues"]
        operands = p["operands"]
        entry: Dict[str, Any] = {"answer_kind": family}
        ans: Answer

        if family == "PICK":
            cand_rows = list(p["candidate_rows"] or [])
            entry["candidate_rows"] = cand_rows
            entry["cues"] = cues
            entry["op_for_pick"] = operands
            scores = [self.pick_machine.score(self._encode_pick_candidate(cues, operands, cr)) for cr in cand_rows]
            if not scores or max(scores) <= 0:
                ans = Answer(kind=AnswerKind.NOTHING)
            else:
                given_idx = int(torch.tensor(scores).argmax())
                ans = Answer(kind=AnswerKind.PICK, value=given_idx)
                entry["given_index"] = given_idx
        else:
            x = self._encode(cues, operands, kind="ASK")
            entry["x"] = x
            votes = self.tm.votes(x)
            if family == "NAME":
                name_votes = {c: v for c, v in votes.items() if c in self.tm.names}
                if not name_votes or max(name_votes.values()) <= 0:
                    ans = Answer(kind=AnswerKind.UNKNOWN)
                else:
                    given = max(name_votes, key=name_votes.get)
                    ans = Answer(kind=AnswerKind.NAME, value=given)
            elif family == "YESNO":
                yv, nv = votes.get("YES", 0), votes.get("NO", 0)
                if yv <= 0 and nv <= 0:
                    ans = Answer(kind=AnswerKind.NOTHING)
                else:
                    ans = Answer(kind=(AnswerKind.YES if yv >= nv else AnswerKind.NO))
            else:
                ans = Answer(kind=AnswerKind.NOTHING)

        # edit: Claude (Opus 5.5), 2026-09-26 12:52 +0400 — EVERY training ask is held for its FEEDBACK, an abstention included.
        # The old guard dropped the correction whenever the arm said UNKNOWN / NOTHING, so an arm that begins by abstaining
        # (a Tsetlin machine's zero votes; a gate net under its band) was never corrected and abstained forever: in B1's
        # seed-20261001 run A2 and A3 answered UNKNOWN to every NAME test ask. The teacher's answer teaches whether or not
        # the arm answered; the extra «wrongly given» term still needs a given answer (`given_index`).
        if learn:
            self._pending[int(ask_row["seq"])] = entry
        return ans

    # ------------------------------------------------------------------------------- sleep
    def sleep(self, steps: int) -> None:
        t0 = time.perf_counter()
        if not self._frozen_binariser:
            if self._glance_obs:
                self._glance_thresholds = torch.stack(self._glance_obs).median(dim=0).values
            else:
                self._glance_thresholds = torch.zeros(GLANCE_FLAT_BITS)
            self._glance_obs = []
            self._frozen_binariser = True
        self._events += int(steps)
        self._ms += (time.perf_counter() - t0) * 1000.0

    # ------------------------------------------------------------------------------- identity
    def state_sha(self) -> str:
        parts = [self.tm.state_sha_bytes(), self.pick_machine.state_sha_bytes()]
        parts.append(b"slots=" + self.slots.state_bytes())
        parts.append(b"prev_name=" + repr(self.prev_name_idx).encode())
        thr = self._glance_thresholds
        parts.append(b"thr=" + (thr.numpy().tobytes() if thr is not None else b"unfrozen"))
        parts.append(b"obs=" + b"".join(t.numpy().tobytes() for t in self._glance_obs))
        return hashlib.sha256(b"|".join(parts)).hexdigest()

    def snapshot(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "tm": self.tm.state_dict(),
                "pick": self.pick_machine.state_dict(),
                "slots": self.slots.to_dict(),
                "prev_name_idx": self.prev_name_idx,
                "glance_thresholds": self._glance_thresholds,
                "glance_obs": self._glance_obs,
                "frozen_binariser": self._frozen_binariser,
                "events": self._events,
                "ms": self._ms,
            },
            path / "state.pt",
        )

    def load(self, path: Union[str, Path]) -> None:
        # weights_only=False: same trusted-internal-checkpoint rationale as the other two arms'
        # Arm.load (never untrusted input; written and read only by this same class).
        d = torch.load(Path(path) / "state.pt", weights_only=False)
        self.tm.load_state_dict(d["tm"])
        self.pick_machine.load_state_dict(d["pick"])
        self.slots = SlotTable.from_dict(d["slots"])
        self.prev_name_idx = d["prev_name_idx"]
        self._glance_thresholds = d["glance_thresholds"]
        self._glance_obs = list(d["glance_obs"])
        self._frozen_binariser = d["frozen_binariser"]
        self._events = d["events"]
        self._ms = d["ms"]
        self._pending = {}

    def cost(self) -> Dict[str, float]:
        return {"events": self._events, "ms": self._ms}
