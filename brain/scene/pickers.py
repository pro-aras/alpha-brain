"""pickers.py — S1c «THE NOISY ROOM»: the held-window LOSS and the six PICKERS (which room next). LEARNER side.

edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:05 +0400 — new module, written to docs/brain/r3/PREREG-S1C.md (genome-wt-brain3 9ef2583,
sha a552515a…) §2 and its AMENDMENT 1 §3–§4 (PREREG-S1C-AMEND-1.md, 1eba85d, sha 825f4ad8…). The one-line READINGS the PREREG
leaves open are marked «declared» and listed in docs/brain/r3/S1C-HANDBACK.md.

THE FENCE: this module imports numpy, math, typing, the named substreams (brain.world.seeds) and the learner's own sigmoid;
never the world, the rooms, the cache's truth reader or the marks (tests/brain/scene/test_truth_fence.py, with planted
offenders). The vocabulary arrives as an ARGUMENT. The ORACLE's gains arrive as a CALLBACK from run_s1c.py — the grader's
road, the only place the fixed test set's truth meets a picker.

  window_loss   L_k: the mean over room k's window scenes of the learner's OWN objective under the CURRENT state, frozen
                (standardised by the running statistics as they stand, never observed; no weight moves): the noisy-OR
                cross-entropy −Σ_w [y_w log P(w|scene) + (1 − y_w) log(1 − P(w|scene))], P(w|scene) = 1 − Π_t (1 − p_w(t))
                over the scene's hypotheses, p_w(t) = σ(v_w · z_t + b_w) for EVERY word (never the young-word band —
                AMENDMENT 1 §4), a word not yet heard at its prior σ(0) = 0.5, the sum over the FIXED 13-word vocabulary.
                Declared: the clip [1e-6, 1 − 1e-6] is on the scene-level P (a scene with no hypothesis has P = 0 → 1e-6;
                such scenes are counted, `n_empty`).
  PROGRESS      drop_k = L_k(before the block) − L_k(after it); the estimate = the mean of the room's last 2 drops (one
                until it has two); the pick = argmax with probability 1 − ε, uniform over the rooms with probability ε = 0.10
                (from substream `explore:<block>`; recorded as «explore»); ties → the room visited least recently.
  ERROR         argmax of L_k now; the same ε, the same tie rule.
  RANDOM        uniform over the rooms every policy block (substream `<prefix>pick:<block>`; the band runs of AMENDMENT 1
                §3 (b) use the prefix `random-band:<seed>:<k>:` — declared).
  ORACLE        the gains (words-learned gain, M1 gain) of a CLONE trained on each room's next block, from the callback;
                gains within 1 word of the best tie (≤ 1, AMENDMENT 1 §4) → the largest M1 gain → least recently visited;
                no ε.
  NULL          PROGRESS with the CREDIT of every block-drop misassigned: drop_k is credited to π(k), π a derangement
                of the rooms drawn from substream `null:seed` (rejection of permutations with a fixed point — declared);
                the pin RAISES if a credit would land on the room that produced it (AMENDMENT 1 §3 (c)).
  PROGRESS-DRIFT  PROGRESS's rule on ‖θ_after − θ_before‖₂ ÷ Σ_scenes ‖Δθ_scene‖₂ (θ = V and b over the FIXED vocabulary;
                an unheard word's θ is zero; no path → 0, declared) instead of the window drop.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.world.seeds import substream

from .learners import sigmoid

EPS = 0.10                  # ε
SMOOTH = 2                  # the estimate = the mean of the room's last 2 drops
P_CLIP = 1e-6               # the scene-level probability clip
BLOCK = 10                  # B = 10 scenes per block
N_BLOCKS = 200              # the life: 200 blocks = 2,000 scenes
WITHIN_WORDS = 1            # the ORACLE's tie: gains within 1 word of the best (≤ 1)
PICKERS: Tuple[str, ...] = ("RANDOM", "ERROR", "PROGRESS", "ORACLE", "NULL", "PROGRESS-DRIFT")
EPS_PICKERS: Tuple[str, ...] = ("ERROR", "PROGRESS", "NULL", "PROGRESS-DRIFT")


class PickerError(Exception):
    pass


# ================================================================================================ the held-window LOSS
class WindowSet:
    """One room's window: per scene its hypotheses' raw inputs (H, 146) and what the parent said with it (the recorded
    utterance — what was HEARD, never the truth), stacked once for the loss."""

    def __init__(self, Xs: Sequence[np.ndarray], words: Sequence[Sequence[str]], vocab: Sequence[str]):
        self.Xs = [np.atleast_2d(np.asarray(X, dtype=np.float64)) for X in Xs]
        self.words = [list(w) for w in words]
        self.vocab = list(vocab)
        self.n = len(self.Xs)
        self.h = np.array([X.shape[0] for X in self.Xs], dtype=np.int64)
        self.n_empty = int((self.h == 0).sum())
        nz = [X for X in self.Xs if X.shape[0]]
        self.X = np.concatenate(nz, axis=0) if nz else np.zeros((0, 0))
        self.starts = np.concatenate([[0], np.cumsum(self.h)])
        self.Y = np.array([[1.0 if w in said else 0.0 for w in self.vocab] for said in self.words]).reshape(self.n, len(self.vocab))


def hyp_probs(learner, X: np.ndarray, vocab: Sequence[str]) -> np.ndarray:
    """p_w(t) = σ(v_w · z_t + b_w) for every word of the FIXED vocabulary (an unheard word: σ(0) = 0.5), z the raw inputs
    standardised by the learner's running statistics AS THEY STAND (never observed). (rows, |vocab|)."""
    if X.shape[0] == 0:
        return np.zeros((0, len(vocab)))
    Z = learner.stats.standardise(X)
    logit = np.zeros((Z.shape[0], len(vocab)))
    cols = [(c, learner.index[w]) for c, w in enumerate(vocab) if w in learner.index]
    if cols:
        cc = [c for c, _j in cols]
        jj = [j for _c, j in cols]
        logit[:, cc] = Z @ learner.V[jj].T + learner.b[jj][None, :]
    return sigmoid(logit)


def scene_losses(learner, ws: WindowSet) -> np.ndarray:
    """Each window scene's −Σ_w [y log P + (1 − y) log(1 − P)] under the current state, frozen."""
    p = hyp_probs(learner, ws.X, ws.vocab)
    out = np.zeros(ws.n)
    for i in range(ws.n):
        a, b = int(ws.starts[i]), int(ws.starts[i + 1])
        P = 1.0 - np.prod(1.0 - p[a:b], axis=0) if b > a else np.zeros(len(ws.vocab))
        P = np.clip(P, P_CLIP, 1.0 - P_CLIP)
        y = ws.Y[i]
        out[i] = -float(np.sum(y * np.log(P) + (1.0 - y) * np.log(1.0 - P)))
    return out


def window_loss(learner, ws: WindowSet) -> float:
    return float(np.mean(scene_losses(learner, ws)))


# ================================================================================================ θ and the drift reading
def theta(learner, vocab: Sequence[str]) -> np.ndarray:
    """θ = [V ‖ b] over the FIXED vocabulary (|vocab|, dim + 1); a word not yet heard is zero (its unit's start)."""
    out = np.zeros((len(vocab), learner.dim + 1))
    for c, w in enumerate(vocab):
        j = learner.index.get(w)
        if j is not None:
            out[c, :-1] = learner.V[j]
            out[c, -1] = learner.b[j]
    return out


def drift_reading(thetas: Sequence[np.ndarray]) -> float:
    """‖θ_last − θ_first‖₂ ÷ Σ ‖θ_i − θ_{i−1}‖₂ over a block's snapshots (before it, then after each scene); 1 when
    every step points one way, ≈ 1/√B for a random walk; 0 when nothing moved (declared)."""
    path = float(sum(np.linalg.norm(thetas[i] - thetas[i - 1]) for i in range(1, len(thetas))))
    if path <= 0.0:
        return 0.0
    return float(np.linalg.norm(thetas[-1] - thetas[0])) / path


# ================================================================================================ the draws
def explore_draw(seed: int, block: int, rooms: Sequence[str]) -> Optional[str]:
    """ε's coin and, on heads, the uniform room — both from substream `explore:<block>` (the coin first; declared)."""
    rng = substream(seed, f"explore:{int(block)}")
    if rng.random() < EPS:
        return rooms[int(rng.integers(len(rooms)))]
    return None


def band_prefix(seed: int, k: int) -> str:
    return f"random-band:{int(seed)}:{int(k)}:"


def is_derangement(pi: Dict[str, str]) -> bool:
    keys = sorted(pi)
    return sorted(pi.values()) == keys and all(pi[k] != k for k in keys)


def null_derangement(seed: int, rooms: Sequence[str]) -> Dict[str, str]:
    """π: a derangement of the rooms, fixed per seed, from substream `null:seed` (AMENDMENT 1 §3 (c)); declared: uniform
    permutations drawn until one has no fixed point."""
    rng = substream(seed, "null:seed")
    for _ in range(10_000):
        perm = rng.permutation(len(rooms))
        pi = {rooms[i]: rooms[int(perm[i])] for i in range(len(rooms))}
        if is_derangement(pi):
            return pi
    raise PickerError("no derangement in 10,000 draws")


def argmax_lrv(values: Dict[str, float], last_visit: Dict[str, int]) -> str:
    """argmax over the rooms that carry a value; ties → the room visited least recently (the smallest last block)."""
    cand = {r: v for r, v in values.items() if v is not None}
    if not cand:
        raise PickerError("no room carries a value")
    best = max(cand.values())
    tied = [r for r, v in cand.items() if v == best]
    return min(tied, key=lambda r: (last_visit.get(r, 0), r))


def exploration_mismatches(record: Sequence[Dict[str, object]], seed: int, rooms: Sequence[str]) -> List[int]:
    """The blocks whose «explore» flag (or explored room) disagrees with the ε draw of `explore:<block>` — the planted
    control of the exploration flag (THE FIRST GATE 4)."""
    bad = []
    for r in record:
        if r.get("flag") not in ("policy", "explore"):
            continue
        d = explore_draw(seed, int(r["block"]), rooms)
        if (d is not None) != (r["flag"] == "explore") or (d is not None and r["room"] != d):
            bad.append(int(r["block"]))
    return bad


@dataclass
class Context:
    last_visit: Dict[str, int] = field(default_factory=dict)
    L_now: Dict[str, float] = field(default_factory=dict)


# ================================================================================================ the pickers
class _Picker:
    name = ""
    uses_eps = False

    def __init__(self, rooms: Sequence[str], seed: int):
        self.rooms = list(rooms)
        self.seed = int(seed)

    def estimates(self) -> Dict[str, Optional[float]]:
        return {r: None for r in self.rooms}

    def observe(self, block: int, room: str, drop: float, drift: float) -> Optional[str]:
        return None

    def _explore(self, block: int) -> Optional[Tuple[str, str]]:
        d = explore_draw(self.seed, block, self.rooms)
        return None if d is None else (d, "explore")


class RandomPicker(_Picker):
    name = "RANDOM"

    def __init__(self, rooms: Sequence[str], seed: int, prefix: str = ""):
        super().__init__(rooms, seed)
        self.prefix = prefix

    def pick(self, block: int, ctx: Optional[Context]) -> Tuple[str, str]:
        rng = substream(self.seed, f"{self.prefix}pick:{int(block)}")
        return self.rooms[int(rng.integers(len(self.rooms)))], "policy"


class ErrorPicker(_Picker):
    name = "ERROR"
    uses_eps = True

    def pick(self, block: int, ctx: Context) -> Tuple[str, str]:
        e = self._explore(block)
        if e is not None:
            return e
        return argmax_lrv({r: float(ctx.L_now[r]) for r in self.rooms}, ctx.last_visit), "policy"

    def estimates(self) -> Dict[str, Optional[float]]:
        return {r: None for r in self.rooms}


class ProgressPicker(_Picker):
    """PROGRESS; with `credit` a map room → room (the NULL's π) the drop of a block in k is credited to credit[k]."""
    name = "PROGRESS"
    uses_eps = True
    reads = "drop"

    def __init__(self, rooms: Sequence[str], seed: int, credit: Optional[Dict[str, str]] = None):
        super().__init__(rooms, seed)
        self.credit = dict(credit) if credit is not None else {r: r for r in self.rooms}
        self.credited: Dict[str, List[float]] = {r: [] for r in self.rooms}

    def estimates(self) -> Dict[str, Optional[float]]:
        return {r: (float(np.mean(v[-SMOOTH:])) if v else None) for r, v in self.credited.items()}

    def observe(self, block: int, room: str, drop: float, drift: float) -> Optional[str]:
        to = self.credit[room]
        self.credited[to].append(float(drop if self.reads == "drop" else drift))
        return to

    def pick(self, block: int, ctx: Context) -> Tuple[str, str]:
        e = self._explore(block)
        if e is not None:
            return e
        return argmax_lrv(self.estimates(), ctx.last_visit), "policy"


class NullPicker(ProgressPicker):
    name = "NULL"

    def __init__(self, rooms: Sequence[str], seed: int, credit: Optional[Dict[str, str]] = None, allow_identity: bool = False):
        pi = dict(credit) if credit is not None else null_derangement(seed, rooms)
        self.allow_identity = bool(allow_identity)
        if not self.allow_identity and not is_derangement(pi):
            raise PickerError(f"the null's credit map is not a derangement: {pi}")
        super().__init__(rooms, seed, credit=pi)
        self.pi = self.credit

    def observe(self, block: int, room: str, drop: float, drift: float) -> Optional[str]:
        if not self.allow_identity and self.pi[room] == room:
            raise PickerError(f"block {block}: the null's credit would land on the room that produced it ({room})")
        return super().observe(block, room, drop, drift)


class DriftPicker(ProgressPicker):
    name = "PROGRESS-DRIFT"
    reads = "drift"


class OraclePicker(_Picker):
    """The reference: `gain_fn(rooms)` → {room: (words-learned gain, M1 gain)} of a clone trained on each room's next
    block (the callback is the grader's road; this module never reads the test set)."""
    name = "ORACLE"

    def __init__(self, rooms: Sequence[str], seed: int, gain_fn: Callable[[Sequence[str]], Dict[str, Tuple[float, float]]]):
        super().__init__(rooms, seed)
        self.gain_fn = gain_fn
        self.last_gains: Dict[str, Tuple[float, float]] = {}

    def pick(self, block: int, ctx: Context) -> Tuple[str, str]:
        g = self.gain_fn(self.rooms)
        self.last_gains = dict(g)
        best = max(g[r][0] for r in self.rooms)
        tied = [r for r in self.rooms if g[r][0] >= best - WITHIN_WORDS]
        m1 = {r: (g[r][1] if g[r][1] is not None else -math.inf) for r in tied}
        return argmax_lrv(m1, ctx.last_visit), "policy"


def make_picker(name: str, rooms: Sequence[str], seed: int, gain_fn=None, prefix: str = "",
                identity_credit: bool = False):
    if name == "RANDOM":
        return RandomPicker(rooms, seed, prefix=prefix)
    if name == "ERROR":
        return ErrorPicker(rooms, seed)
    if name == "PROGRESS":
        return ProgressPicker(rooms, seed)
    if name == "NULL":
        if identity_credit:
            return NullPicker(rooms, seed, credit={r: r for r in rooms}, allow_identity=True)
        return NullPicker(rooms, seed)
    if name == "PROGRESS-DRIFT":
        return DriftPicker(rooms, seed)
    if name == "ORACLE":
        if gain_fn is None:
            raise PickerError("the ORACLE needs its gain callback")
        return OraclePicker(rooms, seed, gain_fn)
    raise PickerError(f"no such picker: {name!r}")


# ================================================================================================ S1c-2 (PREREG-S1C2 §2)
# edit: Claude (Opus 5.5, S1c-2 builder), 2026-09-28 16:15 +0400 — PREREG-S1C2 (genome-wt-brain3 141a8cd, sha 5e4585c1…) §2: PROGRESS-NET and
# its NULL (the credit of room k's reading to π(k)), PROGRESS-UCB (a reading). S1c's classes above are unchanged byte for byte;
# the new ones read the PRE readings the life hands them (`wants_readings`).
class NetPicker(_Picker):
    """PROGRESS-NET: net_k = PRE_{v_k}(k) − PRE_now(k) — room k's loss just before its last visit minus its loss NOW (the
    latest PRE reading), re-read at every boundary (so it refreshes without a visit and cannot freeze); no smoothing; a room
    never visited has no estimate and is picked first (the least recently visited among such rooms, then by name); ε and the
    tie rule are PROGRESS's. With `credit` (the NULL's π) room k's reading is credited to credit[k]."""
    name = "PROGRESS-NET"
    uses_eps = True
    wants_readings = True

    def __init__(self, rooms: Sequence[str], seed: int, credit: Optional[Dict[str, str]] = None):
        super().__init__(rooms, seed)
        self.credit = dict(credit) if credit is not None else {r: r for r in self.rooms}
        self.pre_at_visit: Dict[str, float] = {}
        self.pre_now: Dict[str, float] = {}

    def net(self) -> Dict[str, Optional[float]]:
        return {r: (self.pre_at_visit[r] - self.pre_now[r] if r in self.pre_at_visit and r in self.pre_now else None)
                for r in self.rooms}

    def estimates(self) -> Dict[str, Optional[float]]:
        n = self.net()
        return {self.credit[r]: n[r] for r in self.rooms}

    def observe(self, block: int, room: str, drop: float, drift: float, pre_before: Optional[Dict[str, float]] = None,
                pre_after: Optional[Dict[str, float]] = None) -> Optional[str]:
        if pre_before is None or pre_after is None:
            raise PickerError("PROGRESS-NET reads the PRE readings: the life must hand them over")
        self.pre_at_visit[room] = float(pre_before[room])
        self.pre_now = {r: float(pre_after[r]) for r in self.rooms}
        return self.credit[room]

    def pick(self, block: int, ctx: Context) -> Tuple[str, str]:
        e = self._explore(block)
        if e is not None:
            return e
        est = self.estimates()
        undefined = [r for r in self.rooms if est[r] is None]
        if undefined:
            return min(undefined, key=lambda r: (ctx.last_visit.get(r, 0), r)), "policy"
        return argmax_lrv(est, ctx.last_visit), "policy"


class NullNetPicker(NetPicker):
    """NULL-NET: PROGRESS-NET with the credit of every bracket misassigned (room k's readings credited to π(k), π the seed's
    derangement from `null:seed`) — blind to WHERE only. The pin RAISES if a credit would land on the room that produced it."""
    name = "NULL-NET"

    def __init__(self, rooms: Sequence[str], seed: int, credit: Optional[Dict[str, str]] = None, allow_identity: bool = False):
        pi = dict(credit) if credit is not None else null_derangement(seed, rooms)
        self.allow_identity = bool(allow_identity)
        if not self.allow_identity and not is_derangement(pi):
            raise PickerError(f"the null's credit map is not a derangement: {pi}")
        super().__init__(rooms, seed, credit=pi)
        self.pi = self.credit

    def observe(self, block: int, room: str, drop: float, drift: float, pre_before: Optional[Dict[str, float]] = None,
                pre_after: Optional[Dict[str, float]] = None) -> Optional[str]:
        if not self.allow_identity and self.pi[room] == room:
            raise PickerError(f"block {block}: the null's credit would land on the room that produced it ({room})")
        return super().observe(block, room, drop, drift, pre_before=pre_before, pre_after=pre_after)


class UCBPicker(ProgressPicker):
    """PROGRESS-UCB (a READING): score_k = est_k + c · √(2 ln t / n_k); est_k S1c's PROGRESS estimate (the mean of the last 2
    drops), c the running mean |drop| over every bracketed drop so far, n_k the room's visits so far, t the policy blocks so
    far INCLUDING the one being picked (declared: t = block − the round-robin's length ≥ 1, so ln t is defined at the first
    policy pick). A room unvisited for long gains score without a visit."""
    name = "PROGRESS-UCB"

    def __init__(self, rooms: Sequence[str], seed: int, n_round_robin: int):
        super().__init__(rooms, seed)
        self.n_rr = int(n_round_robin)
        self.visits: Dict[str, int] = {r: 0 for r in self.rooms}
        self.abs_drops: List[float] = []
        self.last_pick: Dict[str, object] = {}

    def c(self) -> float:
        return float(np.mean(self.abs_drops)) if self.abs_drops else 0.0

    def observe(self, block: int, room: str, drop: float, drift: float, **kw) -> Optional[str]:
        self.visits[room] += 1
        self.abs_drops.append(abs(float(drop)))
        return super().observe(block, room, drop, drift)

    def scores(self, block: int) -> Tuple[Dict[str, float], Dict[str, float]]:
        t = int(block) - self.n_rr
        if t < 1 or any(self.visits[r] < 1 for r in self.rooms):
            raise PickerError(f"UCB at block {block}: t = {t}, visits {self.visits} — the bonus is undefined")
        est = super().estimates()
        c = self.c()
        bonus = {r: c * math.sqrt(2.0 * math.log(t) / self.visits[r]) for r in self.rooms}
        return {r: float(est[r]) + bonus[r] for r in self.rooms}, bonus

    def pick(self, block: int, ctx: Context) -> Tuple[str, str]:
        e = self._explore(block)
        if e is not None:
            self.last_pick = {}
            return e
        score, bonus = self.scores(block)
        room = argmax_lrv(score, ctx.last_visit)
        self.last_pick = {"t": int(block) - self.n_rr, "c": self.c(), "score": score, "bonus": bonus,
                          "est": super().estimates(), "room": room}
        return room, "policy"
