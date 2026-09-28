"""a4.py — ARM A4, THE MARKET'S ENGINE (a CHECK, never a candidate) — B1-PREREG.md §4's table, row A4;
docs/brain/b1/SEAT-DECISIONS.md R29.

edit: Claude (Fable 5.1), 2026-09-24 18:50 +0400 — the seat, alone (Builder 2's row).

A 2-layer causal transformer (d_model 128, 4 heads, context 256 steps) over THE SAME STEPS as A1
(`brain.arms.soft.steps.StepEncoder` — the identical row → step decomposition, the identical 24-slot cue
table), with the same three answer heads (NAME over the names heard, PICK by a bilinear score against each
candidate's state, YES/NO) and a WORLD head (next-step prediction). OFFLINE: `offline_train(rows_so_far)` is
called by the runner at T_L's and T_D's TEST_BEGIN (10 epochs over the tape's events before the sitting, in
tape order: next-step + answer losses); nothing is learned online — `fit_event` only appends the row's steps
to the transcript, and a FEEDBACK row enters the transcript as the shown answer's letter steps (a supervised
transcript, the way the market's engines are fed). A4 sits no probe: an ask whose phase is L5 (the probes
P1–P4) reads NOTHING. Size matched to A1's final parameter count ± 10 % (`config["match_params"]`, read from
A1's own summary by the runner): d_model stays 128 while the FFN width can absorb the match; if even the
narrowest FFN exceeds the target, d_model steps down by 4 — both counts on the record, and `within_10pct`
says whether the match held (never silently). The optimiser is Adam(1e-3) — declared (R29): A4 is a check of
what the market's engine does with this tape, and a transformer under plain SGD would be a check of the
optimiser instead.

Identity (§3.1): `torch.manual_seed(seed)` at init; a `torch.Generator` per draw site; float32; 1 thread;
the transcript is a pure function of the rows seen; `state_sha` = sha256 over the state_dict tensors' bytes
in sorted key order + the names heard + the abstention band + the size fields. Abstains (NOTHING) when the
answer head's max probability falls under the p5 of its confidences on the TRAINING asks of the last offline
epoch — the same band A1 keeps, so the U2/U5 comparison is like for like; the would-be answer travels in
`raw["forced"]` (R24).
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from brain.arms.soft.steps import GLANCE_DIM, GLANCE_IDX_DIM, KIND_DIM, LETTER_DIM, STEP_DIM, LETTERS, SlotTable, StepEncoder
from brain.glance_cache import Cache
from brain.protocol import Answer, AnswerKind, canonical_json, is_row_operand

CONTEXT = 256
N_HEADS = 4
D_MODEL_DEFAULT = 128
N_LAYERS = 2
NAMES_CAP = 64
EPOCHS_DEFAULT = 10
STRIDE = 128
BAND_CAP = 0.90


class A4Error(Exception):
    pass


def param_count(d: int, f: int, n_layers: int = N_LAYERS, context: int = CONTEXT, names_cap: int = NAMES_CAP) -> int:
    """The exact parameter count of `A4Net(d, f)` — kept beside the class so the match is arithmetic, not a
    numel() after the fact (both are asserted equal in the tests)."""
    inp = STEP_DIM * d + d
    pos = context * d
    per_layer = (4 * d * d + 4 * d) + (2 * d * f + d + f) + (2 * (2 * d))
    heads = (d * GLANCE_DIM + GLANCE_DIM) + (d * LETTER_DIM + LETTER_DIM) + (d * KIND_DIM + KIND_DIM) \
        + (d * names_cap + names_cap) + (d * 2 + 2) + (d * d)
    final_norm = 2 * d
    return inp + pos + n_layers * per_layer + heads + final_norm


def solve_size(target: Optional[int], tol: float = 0.10) -> Dict[str, Any]:
    """d_model 128 with the FFN width solved to land within ± tol of the target; if F=16 still exceeds
    target·(1+tol), d steps down by N_HEADS; if there is no target, d=128 / f=256 (the plain engine)."""
    if not target:
        return {"d_model": D_MODEL_DEFAULT, "ffn": 256, "n_params": param_count(D_MODEL_DEFAULT, 256), "target": None, "within_10pct": None}
    hi = int(target * (1 + tol))
    d = D_MODEL_DEFAULT
    while d >= N_HEADS:
        if param_count(d, 16) <= hi:
            # the largest f with count <= hi (count is affine in f): double to bracket, then bisect the bracket
            lo_f, hi_f = 16, 32
            while param_count(d, hi_f) <= hi and hi_f < 1 << 20:
                lo_f, hi_f = hi_f, hi_f * 2
            while lo_f < hi_f:
                mid = (lo_f + hi_f + 1) // 2
                if param_count(d, mid) <= hi:
                    lo_f = mid
                else:
                    hi_f = mid - 1
            n = param_count(d, lo_f)
            return {"d_model": d, "ffn": lo_f, "n_params": n, "target": int(target), "within_10pct": abs(n - target) <= tol * target}
        d -= N_HEADS
    n = param_count(N_HEADS, 16)
    return {"d_model": N_HEADS, "ffn": 16, "n_params": n, "target": int(target), "within_10pct": False}


class A4Net(nn.Module):
    def __init__(self, d: int, f: int) -> None:
        super().__init__()
        self.d = d
        self.inp = nn.Linear(STEP_DIM, d)
        self.pos = nn.Parameter(torch.zeros(CONTEXT, d))
        layer = nn.TransformerEncoderLayer(d_model=d, nhead=N_HEADS, dim_feedforward=f, dropout=0.0, batch_first=True, norm_first=True, activation="gelu")
        self.blocks = nn.TransformerEncoder(layer, num_layers=N_LAYERS, enable_nested_tensor=False)
        self.final_norm = nn.LayerNorm(d)
        self.world_glance = nn.Linear(d, GLANCE_DIM)
        self.world_letter = nn.Linear(d, LETTER_DIM)
        self.world_kind = nn.Linear(d, KIND_DIM)
        self.names = nn.Linear(d, NAMES_CAP)
        self.yesno = nn.Linear(d, 2)
        self.pick = nn.Linear(d, d, bias=False)
        self.register_buffer("mask", torch.triu(torch.full((CONTEXT, CONTEXT), float("-inf")), diagonal=1), persistent=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (B, T, STEP_DIM), T <= CONTEXT → (B, T, d) states."""
        T = x.shape[1]
        h = self.inp(x) + self.pos[:T]
        h = self.blocks(h, mask=self.mask[:T, :T], is_causal=True)
        return self.final_norm(h)


class ArmA4:
    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.seed = int(seed)
        self.config = dict(config)
        torch.manual_seed(self.seed)
        cache_dir = self.config.get("cache_dir")
        self.cache = Cache(cache_dir) if cache_dir else None
        self.slots = SlotTable()
        self.encoder = StepEncoder(self.cache, self.slots) if self.cache is not None else None
        self.size_spec = solve_size(self.config.get("match_params"))
        self.net = A4Net(self.size_spec["d_model"], self.size_spec["ffn"])
        self.net.eval()
        self.epochs = int(self.config.get("epochs", EPOCHS_DEFAULT))
        self.lr = float(self.config.get("lr", 1e-3))
        self.names: List[str] = []
        self.band: Optional[float] = None
        self.band_p5: Optional[float] = None
        self.trained_at: List[int] = []
        # the transcript: steps + the answer targets at ask positions
        self._steps: List[torch.Tensor] = []
        self._targets: Dict[int, Dict[str, Any]] = {}        # step index of an ASK's last step -> {family, target, cands}
        self._pending: Dict[int, Tuple[int, str, Optional[List[int]]]] = {}   # ask seq -> (step index, family, cands)
        self._events = 0
        self._ms = 0.0
        self._n_train_asks = 0

    # ------------------------------------------------------------------ plumbing
    def _enc(self) -> StepEncoder:
        if self.encoder is None:
            raise A4Error("A4 constructed without config['cache_dir'] — cannot encode any row")
        return self.encoder

    def _hear(self, name: str) -> None:
        if name not in self.names:
            if len(self.names) >= NAMES_CAP:
                raise A4Error(f"more than {NAMES_CAP} names heard — RAISE (the NAME head's cap)")
            self.names.append(name)

    def _letter_steps_of_answer(self, right: Any, kind: str) -> List[torch.Tensor]:
        enc = self._enc()
        if isinstance(right, str) and right in ("YES", "NO"):
            return enc.name_steps("y" if right == "YES" else "n", kind)
        if isinstance(right, str):
            return enc.name_steps(right, kind)
        return []   # a PICK index has no letters; the transcript carries the ask's own candidate steps

    # ------------------------------------------------------------------ ingestion (transcript only)
    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        t0 = time.perf_counter()
        enc = self._enc()
        kind = row["kind"]
        p = row["payload"]
        if kind == "TEACH":
            self._hear(p["name"])
            self._steps.extend(enc.teach_steps(p))
        elif kind == "ASK":
            for op in p["operands"]:
                if op.get("kind") == "name":
                    self._hear(op["value"])
            steps = enc.ask_steps(p)
            self._steps.extend(steps)
            self._pending[int(row["seq"])] = (len(self._steps) - 1, p["answer_kind"], list(p.get("candidate_rows") or []) or None)
        elif kind == "FEEDBACK":
            ask_seq = int(p["ask_seq"])
            pend = self._pending.pop(ask_seq, None)
            right = p["right"]
            if pend is not None:
                idx, family, cands = pend
                if family == "NAME" and isinstance(right, str):
                    self._hear(right)
                self._targets[idx] = {"family": family, "target": right, "cands": cands}
                self._n_train_asks += 1
            self._steps.extend(self._letter_steps_of_answer(right, "FEEDBACK"))
        elif kind == "ARRIVAL":
            self._steps.extend(enc.cue_steps([], "ARRIVAL") if False else [])
        self._events += 1
        self._ms += (time.perf_counter() - t0) * 1000.0

    def sleep(self, steps: int) -> None:
        self._events += 1      # nothing online; the offline epochs are A4's whole learning (§4)

    # ------------------------------------------------------------------ offline training
    def _window_batches(self, n_steps: int) -> List[Tuple[int, int]]:
        if n_steps <= CONTEXT:
            return [(0, n_steps)]
        starts = list(range(0, n_steps - CONTEXT + 1, STRIDE))
        if starts[-1] + CONTEXT < n_steps:
            starts.append(n_steps - CONTEXT)
        return [(s, s + CONTEXT) for s in starts]

    def _answer_loss_at(self, states: torch.Tensor, start: int, end: int, confidences: Optional[List[float]] = None) -> torch.Tensor:
        loss = states.new_zeros(())
        n = 0
        for idx in range(start, end):
            tgt = self._targets.get(idx)
            if tgt is None:
                continue
            h = states[idx - start]
            fam, target = tgt["family"], tgt["target"]
            if fam == "NAME" and isinstance(target, str) and target in self.names:
                logits = self.names_logits(h)
                loss = loss + F.cross_entropy(logits.unsqueeze(0), torch.tensor([self.names.index(target)]))
                if confidences is not None:
                    confidences.append(float(torch.softmax(logits, -1).max()))
                n += 1
            elif fam == "YESNO" and target in ("YES", "NO"):
                logits = self.net.yesno(h)
                loss = loss + F.cross_entropy(logits.unsqueeze(0), torch.tensor([1 if target == "YES" else 0]))
                if confidences is not None:
                    confidences.append(float(torch.softmax(logits, -1).max()))
                n += 1
            elif fam == "PICK" and tgt["cands"] and isinstance(target, int):
                scores = self._pick_scores(h, tgt["cands"])
                loss = loss + F.cross_entropy(scores.unsqueeze(0), torch.tensor([int(target)]))
                if confidences is not None:
                    confidences.append(float(torch.softmax(scores, -1).max()))
                n += 1
        return loss / max(n, 1)

    def names_logits(self, h: torch.Tensor) -> torch.Tensor:
        logits = self.net.names(h)[: max(len(self.names), 1)]
        return logits

    def _candidate_state(self, cand_row: int) -> torch.Tensor:
        """A candidate's own representation: the mean of its glance steps through the input projection (no
        context — a candidate is a picture on a sheet, not an event in the stream)."""
        steps = torch.stack(self._enc().candidate_steps(int(cand_row)))
        return self.net.inp(steps).mean(dim=0)

    def _pick_scores(self, h_query: torch.Tensor, cands: Sequence[int]) -> torch.Tensor:
        q = self.net.pick(h_query)
        return torch.stack([torch.dot(q, self._candidate_state(c)) for c in cands]) / math.sqrt(self.net.d)

    def _world_loss(self, states: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """Next-step prediction over the window: the glance block by MSE, the letter and kind blocks by CE."""
        if states.shape[0] < 2:
            return states.new_zeros(())
        h, nxt = states[:-1], x[1:]
        g_true = nxt[:, :GLANCE_DIM]
        l_true = nxt[:, GLANCE_DIM + GLANCE_IDX_DIM: GLANCE_DIM + GLANCE_IDX_DIM + LETTER_DIM]
        k_true = nxt[:, -KIND_DIM:]
        loss = F.mse_loss(self.net.world_glance(h), g_true)
        lm = l_true.sum(-1) > 0
        if lm.any():
            loss = loss + F.cross_entropy(self.net.world_letter(h)[lm], l_true[lm].argmax(-1))
        loss = loss + F.cross_entropy(self.net.world_kind(h), k_true.argmax(-1))
        return loss

    def offline_train(self, rows_so_far: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        """The runner calls this at T_L's and T_D's TEST_BEGIN with every row before the sitting. The transcript
        already holds those rows (fit_event appended them); `rows_so_far` is accepted for the contract and its
        length is recorded beside the transcript's, never used to re-encode (one encoding road)."""
        t0 = time.perf_counter()
        n_steps = len(self._steps)
        if n_steps == 0:
            return {"epochs": 0, "steps": 0}
        X = torch.stack(self._steps)
        self.net.train()
        opt = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        windows = self._window_batches(n_steps)
        confidences: List[float] = []
        last_loss = None
        for epoch in range(self.epochs):
            collect = confidences if epoch == self.epochs - 1 else None
            for (s, e) in windows:
                x = X[s:e]
                states = self.net(x.unsqueeze(0))[0]
                loss = self._world_loss(states, x) + self._answer_loss_at(states, s, e, collect)
                opt.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.net.parameters(), 1.0)
                opt.step()
                last_loss = float(loss.detach())
        self.net.eval()
        if confidences:
            cs = sorted(confidences)
            p5 = cs[max(0, int(0.05 * len(cs)) - 1)] if len(cs) > 1 else cs[0]
            # R29: A1's p5 band, CAPPED at BAND_CAP — an engine that memorises its training asks reads p5 ≈ 1.0
            # and would abstain on everything at test (measured on the XOR toy: training confidences 0.9998,
            # test 0.63–0.82); the cap keeps the band a band. Both numbers are on the record.
            self.band_p5 = float(p5)
            self.band = min(float(p5), BAND_CAP)
        self.trained_at.append(n_steps)
        self._ms += (time.perf_counter() - t0) * 1000.0
        return {"epochs": self.epochs, "steps": n_steps, "windows": len(windows), "rows_given": len(rows_so_far),
                "last_loss": last_loss, "band": self.band, "band_p5": self.band_p5, "train_asks_with_targets": len(self._targets), "seconds": round(time.perf_counter() - t0, 1)}

    # ------------------------------------------------------------------ answering (frozen)
    @torch.no_grad()
    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        t0 = time.perf_counter()
        try:
            p = ask_row["payload"]
            if ask_row.get("phase") == "L5":
                return Answer(kind=AnswerKind.NOTHING, raw={"why": "A4 sits no probe (§4)"})
            if not self.trained_at:
                return Answer(kind=AnswerKind.NOTHING, raw={"why": "untrained (offline epochs run at T_L/T_D only)"})
            enc = self._enc()
            steps = enc.ask_steps(p)
            ctx = self._steps[-(CONTEXT - len(steps)):] if len(steps) < CONTEXT else []
            x = torch.stack(list(ctx) + list(steps)[-CONTEXT:])
            h = self.net(x.unsqueeze(0))[0][-1]
            fam = p["answer_kind"]
            if fam == "NAME":
                if not self.names:
                    return Answer(kind=AnswerKind.NOTHING)
                logits = self.names_logits(h)
                probs = torch.softmax(logits, -1)
                conf, idx = float(probs.max()), int(probs.argmax())
                forced = {"kind": AnswerKind.NAME, "value": self.names[idx]}
                if self.band is not None and conf < self.band:
                    return Answer(kind=AnswerKind.NOTHING, raw={"conf": conf, "forced": forced})
                return Answer(kind=AnswerKind.NAME, value=self.names[idx], raw={"conf": conf})
            if fam == "YESNO":
                probs = torch.softmax(self.net.yesno(h), -1)
                conf, idx = float(probs.max()), int(probs.argmax())
                k = AnswerKind.YES if idx == 1 else AnswerKind.NO
                if self.band is not None and conf < self.band:
                    return Answer(kind=AnswerKind.NOTHING, raw={"conf": conf, "forced": {"kind": k, "value": None}})
                return Answer(kind=k, raw={"conf": conf})
            if fam == "PICK":
                cands = list(p.get("candidate_rows") or [])
                if not cands:
                    return Answer(kind=AnswerKind.NOTHING)
                probs = torch.softmax(self._pick_scores(h, cands), -1)
                conf, idx = float(probs.max()), int(probs.argmax())
                if self.band is not None and conf < self.band:
                    return Answer(kind=AnswerKind.NOTHING, raw={"conf": conf, "forced": {"kind": AnswerKind.PICK, "value": idx}})
                return Answer(kind=AnswerKind.PICK, value=idx, raw={"conf": conf})
            return Answer(kind=AnswerKind.NOTHING)
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    # ------------------------------------------------------------------ identity / persistence
    def _meta(self) -> Dict[str, Any]:
        return {"names": list(self.names), "band": self.band, "band_p5": self.band_p5, "size": self.size_spec, "trained_at": list(self.trained_at),
                "slots": self.slots.to_dict(), "n_steps": len(self._steps), "seed": self.seed}

    def state_sha(self) -> str:
        h = hashlib.sha256()
        sd = self.net.state_dict()
        for k in sorted(sd):
            h.update(k.encode()); h.update(sd[k].detach().cpu().contiguous().numpy().tobytes())
        h.update(canonical_json(self._meta()).encode())
        return h.hexdigest()

    def snapshot(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        blob = {"state_dict": self.net.state_dict(), "meta": self._meta(), "steps": (torch.stack(self._steps) if self._steps else torch.zeros(0, STEP_DIM)),
                "targets": {str(k): v for k, v in self._targets.items()}, "pending": {str(k): list(v) for k, v in self._pending.items()},
                "cost": {"events": self._events, "ms": self._ms}}
        torch.save(blob, str(path) + ".pt")

    def load(self, path: Union[str, Path]) -> None:
        blob = torch.load(str(Path(path)) + ".pt", weights_only=False)
        meta = blob["meta"]
        self.size_spec = meta["size"]
        self.net = A4Net(self.size_spec["d_model"], self.size_spec["ffn"])
        self.net.load_state_dict(blob["state_dict"])
        self.net.eval()
        self.names = list(meta["names"]); self.band = meta["band"]; self.band_p5 = meta.get("band_p5"); self.trained_at = list(meta["trained_at"])
        self.slots = SlotTable.from_dict(meta["slots"])
        self.encoder = StepEncoder(self.cache, self.slots) if self.cache is not None else None
        self._steps = [s for s in blob["steps"]] if blob["steps"].numel() else []
        self._targets = {int(k): v for k, v in blob["targets"].items()}
        self._pending = {int(k): tuple(v) for k, v in blob["pending"].items()}
        c = blob.get("cost", {})
        self._events, self._ms = int(c.get("events", 0)), float(c.get("ms", 0.0))

    def cost(self) -> Dict[str, float]:
        return {"events": self._events, "ms": self._ms}

    def size(self) -> Dict[str, Any]:
        n = sum(p.numel() for p in self.net.parameters())
        return {**self.size_spec, "n_params_numel": int(n), "n_names": len(self.names), "transcript_steps": len(self._steps)}
