"""estimators.py — TOY A: the pickers (which room next): the eight factorial cells, LP-OUDEYER, the controls, the stage-2 nulls, the adapter
that lets S1c's own pickers run through this toy's life.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:29 +0400 — new module, written to docs/research/toys/PREREG-TOY-CP.md §3 and
# PREREG-TOY-CP-AMEND-1.md §2 (LP-OUDEYER's null); red-first (tests/tools/test_toys_cp.py). The learner-side fence of pickers.py holds: this
# module imports numpy, the standard library, the named substreams and pickers.py's own helpers; never the world, the rooms' truth or the marks.

THE INTERFACE (one for every arm): `estimates()`, `pick(block, ctx)` -> (room, flag), `observe_block(info)` -> the room credited. `Info`
is what the life hands over after a block: the room, the window losses of EVERY room before and after (the learner's loss `L` and the second
loss `C`), the scenes experienced per room (the history's composition), S1c's own-window drop and drift, and the block's PREQUENTIAL losses.

  own reward   block b in room r:   l_r(b - 1) - l_r(b)                                        (S1c's drop)
  hist reward  block b:             sum_j n_j(b) [l_j(b - 1) - l_j(b)] / sum_j n_j(b)          (the history so far, A.5)
  last2        the mean of the room's last 2 rewards   ema   (1 - a) est + a r over ALL its visits, the first reward initialising, a = 0.1
  LP-OUDEYER   the room's own PREQUENTIAL losses in order trained; LP = (the mean of the window [n - theta - tau, n - theta)) - (the mean of
               [n - tau, n)), tau = theta = 20 scenes; defined from 40 scenes; an undefined room is picked first, least recently visited
  NULL         the credit of every reading misassigned: room k's reward (LP: the block's prequential losses) lands on pi(k), pi a derangement
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.scene import pickers as PK
from brain.world.seeds import substream

CELLS: Tuple[str, ...] = ("L-own-last2", "L-own-ema", "L-hist-last2", "L-hist-ema", "C-own-last2", "C-own-ema", "C-hist-last2", "C-hist-ema")
EMA_A = 0.1                       # declared once (PREREG §3), informed by phase 0, never tuned
LP_TAU = 20
LP_THETA = 20


class EstimatorError(Exception):
    pass


@dataclass
class Info:
    block: int
    room: str
    L_before: Dict[str, float]
    L_after: Dict[str, float]
    C_before: Dict[str, float]
    C_after: Dict[str, float]
    n_after: Optional[Dict[str, int]]
    drop: float
    drift: float
    preq: List[float] = field(default_factory=list)


def own_reward(before: Dict[str, float], after: Dict[str, float], room: str) -> float:
    return before[room] - after[room]


def hist_reward(before: Dict[str, float], after: Dict[str, float], weights: Dict[str, float]) -> float:
    """The compressor's improvement on the HISTORY SO FAR: each room's window drop weighted by the share of the history in that room
    (weights = the scenes experienced per room; they need not sum to 1). A history with no weight has no reward — it RAISES."""
    tot = float(sum(weights.values()))
    if not tot > 0.0:
        raise EstimatorError("the history has no weight (every room's scene count is zero)")
    return float(sum(w * (before[j] - after[j]) for j, w in weights.items() if w) / tot)


def ema(values: Sequence[float], a: float = EMA_A) -> float:
    s = float(values[0])
    for y in values[1:]:
        s = (1.0 - a) * s + a * float(y)
    return s


def explore_draw_rep(seed: int, block: int, rooms: Sequence[str], rep: int) -> Optional[str]:
    """The ε coin and, on heads, the uniform room. Replicate 0 IS S1c's `explore:<block>` stream; replicate k >= 1 is
    `toy-rep:<k>:explore:<block>` (the coin first, then the room, as S1c's)."""
    if int(rep) == 0:
        return PK.explore_draw(seed, block, rooms)
    rng = substream(seed, f"toy-rep:{int(rep)}:explore:{int(block)}")
    if rng.random() < PK.EPS:
        return rooms[int(rng.integers(len(rooms)))]
    return None


class _Base:
    name = ""

    def __init__(self, rooms: Sequence[str], seed: int, rep: int = 0, credit: Optional[Dict[str, str]] = None, allow_identity: bool = False):
        self.rooms = list(rooms)
        self.seed = int(seed)
        self.rep = int(rep)
        self.is_null = credit is not None
        self.allow_identity = bool(allow_identity)
        self.credit = dict(credit) if credit is not None else {r: r for r in self.rooms}
        if self.is_null and not self.allow_identity and not PK.is_derangement(self.credit):
            raise EstimatorError(f"the null's credit map is not a derangement: {self.credit}")

    @property
    def pi(self) -> Optional[Dict[str, str]]:
        return dict(self.credit) if self.is_null else None

    def _credited(self, room: str) -> str:
        to = self.credit[room]
        if self.is_null and not self.allow_identity and to == room:
            raise EstimatorError(f"the null's credit would land on the room that produced it ({room})")
        return to

    def _explore(self, block: int) -> Optional[Tuple[str, str]]:
        d = explore_draw_rep(self.seed, block, self.rooms, self.rep)
        return None if d is None else (d, "explore")

    def estimates(self) -> Dict[str, Optional[float]]:
        raise NotImplementedError

    def observe_block(self, info: Info) -> Optional[str]:
        raise NotImplementedError


class CellPicker(_Base):
    """One cell of the factorial: loss L | C  x  scope own | hist  x  scale last2 | ema."""

    def __init__(self, rooms: Sequence[str], seed: int, loss: str, scope: str, scale: str, rep: int = 0, a: float = EMA_A,
                 credit: Optional[Dict[str, str]] = None, allow_identity: bool = False):
        if loss not in ("L", "C") or scope not in ("own", "hist") or scale not in ("last2", "ema"):
            raise EstimatorError(f"no such cell: {loss}-{scope}-{scale}")
        super().__init__(rooms, seed, rep, credit, allow_identity)
        self.loss, self.scope, self.scale, self.a = loss, scope, scale, float(a)
        self.name = f"{loss}-{scope}-{scale}"
        self.rewards: Dict[str, List[float]] = {r: [] for r in self.rooms}

    def estimates(self) -> Dict[str, Optional[float]]:
        out: Dict[str, Optional[float]] = {}
        for r in self.rooms:
            v = self.rewards[r]
            if not v:
                out[r] = None
            elif self.scale == "last2":
                out[r] = float(np.mean(v[-PK.SMOOTH:]))
            else:
                out[r] = ema(v, self.a)
        return out

    def observe_block(self, info: Info) -> Optional[str]:
        before, after = (info.L_before, info.L_after) if self.loss == "L" else (info.C_before, info.C_after)
        if self.scope == "own":
            reward = own_reward(before, after, info.room)
        else:
            if info.n_after is None:
                raise EstimatorError("a history-scope cell needs the scenes experienced per room")
            reward = hist_reward(before, after, info.n_after)
        to = self._credited(info.room)
        self.rewards[to].append(float(reward))
        return to

    def pick(self, block: int, ctx: PK.Context) -> Tuple[str, str]:
        e = self._explore(block)
        if e is not None:
            return e
        return PK.argmax_lrv(self.estimates(), ctx.last_visit), "policy"


class LPPicker(_Base):
    """Oudeyer & Kaplan's windowed learning progress on the room's own PREQUENTIAL error stream (IAC's practice, as read)."""
    name = "LP-OUDEYER"

    def __init__(self, rooms: Sequence[str], seed: int, rep: int = 0, tau: int = LP_TAU, theta: int = LP_THETA,
                 credit: Optional[Dict[str, str]] = None, allow_identity: bool = False):
        super().__init__(rooms, seed, rep, credit, allow_identity)
        self.tau, self.theta = int(tau), int(theta)
        self.err: Dict[str, List[float]] = {r: [] for r in self.rooms}

    def estimates(self) -> Dict[str, Optional[float]]:
        need = self.theta + self.tau
        out: Dict[str, Optional[float]] = {}
        for r in self.rooms:
            v = self.err[r]
            if len(v) < need:
                out[r] = None
            else:
                out[r] = float(np.mean(v[-need:-self.theta]) - np.mean(v[-self.tau:]))
        return out

    def observe_block(self, info: Info) -> Optional[str]:
        to = self._credited(info.room)
        self.err[to].extend(float(x) for x in info.preq)
        return to

    def pick(self, block: int, ctx: PK.Context) -> Tuple[str, str]:
        e = self._explore(block)
        if e is not None:
            return e
        est = self.estimates()
        undefined = [r for r in self.rooms if est[r] is None]
        if undefined:                                      # optimism under uncertainty, declared (PREREG §3)
            return min(undefined, key=lambda r: (ctx.last_visit.get(r, 0), r)), "policy"
        return PK.argmax_lrv(est, ctx.last_visit), "policy"


class ROnlyPicker:
    """The ceiling of escaping noise: uniform over the learnable rooms every policy block, never N (the band k's own stream)."""
    name = "R-ONLY"

    def __init__(self, rooms: Sequence[str], seed: int, k: int):
        self.rooms = list(rooms)
        self.learnable = [r for r in self.rooms if r != "N"]
        self.seed, self.k = int(seed), int(k)
        self.pi = None

    def estimates(self) -> Dict[str, Optional[float]]:
        return {r: None for r in self.rooms}

    def pick(self, block: int, ctx: PK.Context) -> Tuple[str, str]:
        rng = substream(self.seed, f"ronly:{self.seed}:{self.k}:pick:{int(block)}")
        return self.learnable[int(rng.integers(len(self.learnable)))], "policy"

    def observe_block(self, info: Info) -> Optional[str]:
        return None


class NOnlyPicker:
    """The floor, a plant: always the noisy room."""
    name = "N-ONLY"

    def __init__(self, rooms: Sequence[str], seed: int):
        self.rooms = list(rooms)
        self.seed = int(seed)
        self.pi = None

    def estimates(self) -> Dict[str, Optional[float]]:
        return {r: None for r in self.rooms}

    def pick(self, block: int, ctx: PK.Context) -> Tuple[str, str]:
        return "N", "policy"

    def observe_block(self, info: Info) -> Optional[str]:
        return None


class S1cAdapter:
    """S1c's own pickers (RandomPicker, ErrorPicker, ProgressPicker, NullPicker, ...) behind this toy's interface."""

    def __init__(self, picker):
        self.p = picker
        self.name = picker.name

    @property
    def pi(self):
        return getattr(self.p, "pi", None)

    def estimates(self):
        return self.p.estimates()

    def pick(self, block: int, ctx: PK.Context):
        return self.p.pick(block, ctx)

    def observe_block(self, info: Info):
        return self.p.observe(info.block, info.room, drop=info.drop, drift=info.drift)


class ErrorRep(PK.ErrorPicker):
    """S1c's ERROR rule with this toy's replicate ε stream (replicate 0 is S1c's exactly)."""

    def __init__(self, rooms: Sequence[str], seed: int, rep: int = 0):
        super().__init__(rooms, seed)
        self.rep = int(rep)

    def _explore(self, block: int):
        d = explore_draw_rep(self.seed, block, self.rooms, self.rep)
        return None if d is None else (d, "explore")


def make_arm(name: str, rooms: Sequence[str], seed: int, rep: int = 0, null: bool = False):
    """The arm `name` for one life: `rep` is the replicate (the ε stream) for the ε-greedy arms, the band index k for RANDOM and R-ONLY.
    `null=True` is the stage-2 NULL (S1c's credit derangement π from `null:seed`), defined for the nine arms that read a credit."""
    rooms = list(rooms)
    pi = PK.null_derangement(seed, rooms) if null else None
    if name in CELLS:
        loss, scope, scale = name.split("-")
        return CellPicker(rooms, seed, loss, scope, scale, rep=rep, credit=pi)
    if name == "LP-OUDEYER":
        return LPPicker(rooms, seed, rep=rep, credit=pi)
    if null:
        raise EstimatorError(f"{name} reads no credit: it has no stage-2 null")
    if name == "ERROR":
        return S1cAdapter(ErrorRep(rooms, seed, rep))
    if name == "RANDOM":
        return S1cAdapter(PK.RandomPicker(rooms, seed, prefix=PK.band_prefix(seed, rep)))
    if name == "R-ONLY":
        return ROnlyPicker(rooms, seed, rep)
    if name == "N-ONLY":
        return NOnlyPicker(rooms, seed)
    if name == "RANDOM-PLANT":
        return S1cAdapter(PK.RandomPicker(rooms, seed, prefix="plant:"))
    raise EstimatorError(f"no such arm: {name!r}")
