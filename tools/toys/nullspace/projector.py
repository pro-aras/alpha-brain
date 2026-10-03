"""projector.py — TOY B: the projectors (OWM soft, NSCL hard, their random-direction nulls, the anti-projector), the arms' hooks, and the pre-pass.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:44 +0400 — new module, written to docs/research/toys/PREREG-TOY-NULLSPACE.md §1, §3, §4 (text co-signed
# 2026-10-03 11:24 +0400, sha256 d15a6353…); red-first (tests/tools/test_toys_nullspace.py). Nothing under brain/ is edited: the arms act through the learner's own
# `train_scene(..., project=hook)` door (added for T-MEM-1's GATE): the hook receives the step [dV | db] before it is applied.

THE MATHEMATICS. A word unit is `sigma(v . z + b)`; its input is `x = [z || 1]` (147 numbers, the bias a weight on a constant). The step of the delta rule is
`U = [dV | db]` (words x 147), a combination of the scene's inputs. OWM (Zeng et al.): `P = I - A (A'A + alpha I)^-1 A' = alpha (alpha I + G)^-1`, G = A A' the Gram of
EVERY previously trained input row (the paper's main-text definition; equal to its RLS recursion run over SINGLE rows); the step becomes `U P`; the first task is
unprojected. NSCL (Wang et al.): `U2 U2'`, U2 the eigenvectors of the uncentred covariance with the smallest eigenvalues (here `<= tau * lambda_max`, a RELATIVE
threshold). The paper's Methods recursion over batch MEANS is a looser projector (rank <= #batches), kept as a reading arm. Resolution: `alpha_tau = tau *
lambda_max(G_1)`, derived once from room 1 and FIXED (OWM's constant alpha); NSCL re-relativizes `tau * lambda_max(C_j)` at every room — «the same tau» is the same
resolution at room 1 only.

WHY THE PRE-PASS: the running standardiser sees only the scenes, so the rows `[z || 1]` — and with them every Gram, projector, alpha and U2 — are the SAME functions of
(seed, tau) for every arm. `Projectors` computes them once per seed; a life is then a replay with a hook that multiplies by the right matrix.
"""
from __future__ import annotations

import copy
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from brain.scene import learners as Lr
from brain.scene import run_s1c as S
from brain.world.seeds import substream

DIM = Lr.RW_DIM + 1                                    # 146 inputs + the bias's constant 1
ROOMS: Tuple[str, ...] = tuple(S.WORLDS["law"])        # R1, R2, R3, N — T-MEM-1's sequential order
BLOCKS_PER_ROOM = 50
BLOCK = 10
TAUS: Tuple[float, ...] = (0.1, 0.01, 0.001)


# ================================================================================================ the mathematics
def gram(rows: np.ndarray) -> np.ndarray:
    return rows.T @ rows


def owm_projector(G: np.ndarray, alpha: float) -> np.ndarray:
    """P = alpha (alpha I + G)^-1 = I - A (A'A + alpha I)^-1 A' (G = A A'), by the eigendecomposition: symmetric, eigenvalues alpha / (alpha + E) in (0, 1]."""
    E, U = np.linalg.eigh(G)
    E = np.maximum(E, 0.0)
    P = (U * (alpha / (alpha + E))) @ U.T
    return (P + P.T) / 2.0


def rls_rows(X: np.ndarray, alpha: float, P0: Optional[np.ndarray] = None) -> np.ndarray:
    """OWM's recursion (eq. 2) run over SINGLE rows with P(0) = I: P <- P - (P x)(P x)' / (alpha + x' P x); equals owm_projector(X'X, alpha) exactly."""
    d = X.shape[1]
    P = np.eye(d) if P0 is None else P0.copy()
    for x in X:
        Px = P @ x
        P = P - np.outer(Px, Px) / (alpha + float(x @ Px))
    return (P + P.T) / 2.0


def rls_batches(Xbar: np.ndarray, alpha: float, P0: Optional[np.ndarray] = None) -> np.ndarray:
    """The SAME recursion over BATCH MEANS (OWM's Methods): it is the all-rows form of the MEANS, a different, looser projector than the all-rows one."""
    return rls_rows(Xbar, alpha, P0)


def nscl_projector(G: np.ndarray, n: int, tau: float) -> Tuple[np.ndarray, int]:
    """The hard projector onto the eigen-directions of C = G / n with eigenvalue <= tau * lambda_max; returns (P, d) with d the null dimension kept."""
    ev, U = np.linalg.eigh(G / float(n))
    keep = ev <= tau * ev.max()
    U2 = U[:, keep]
    P = U2 @ U2.T
    return (P + P.T) / 2.0, int(keep.sum())


def haar(seed: int, name: str, dim: int = DIM) -> np.ndarray:
    """A Haar-distributed orthogonal matrix from substream `name` of the seed (QR of a Gaussian, signs fixed)."""
    A = substream(seed, name).standard_normal((dim, dim))
    Q, R = np.linalg.qr(A)
    return Q * np.sign(np.diag(R))


def rotate(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """ROT: the same spectrum, a random eigenbasis (the projector built in coordinates rotated by Q)."""
    R = Q @ P @ Q.T
    return (R + R.T) / 2.0


def random_subspace(Q: np.ndarray, d: int) -> np.ndarray:
    """RAND-RANK: the projector onto a random d-dimensional subspace (the first d columns of Q)."""
    B = Q[:, :d]
    return B @ B.T


def anti(P: np.ndarray) -> np.ndarray:
    return np.eye(P.shape[0]) - P


def anti_all(by_room: Mapping[int, np.ndarray]) -> Dict[int, np.ndarray]:
    return {r: anti(P) for r, P in by_room.items()}


# ================================================================================================ the arms' hooks
class Arm:
    """An arm: what is done to the learner's step `[dV | db]` before it is applied. `begin_block(block, room_idx, L)` is called before every block (room_idx 1-based);
    `__call__(L, upd, db)` is the learner's `project` hook. `rho` = the realised ratio ||step after|| / ||step before|| per scene (L.scenes)."""
    name = "PLAIN"
    lr_scale = 1.0

    def __init__(self):
        self.rho: Dict[int, float] = {}

    def begin_block(self, block: int, room_idx: int, L) -> None:
        pass

    def __call__(self, L, upd: np.ndarray, db: np.ndarray):
        return upd, db

    def _record(self, L, before: np.ndarray, after: np.ndarray) -> None:
        nb = float(np.linalg.norm(before))
        self.rho[int(L.scenes)] = float(np.linalg.norm(after) / nb) if nb > 0 else 1.0


class PlainArm(Arm):
    """The unprojected learner (T-MEM-1's BASE): the life passes `project=None` for it."""
    name = "PLAIN"


class OwmArm(Arm):
    """Rooms >= 2: `[dV | db] <- [dV | db] P_room`; room 1 (no matrix) is untouched. Used for OWM, NSCL, ROT, RAND-RANK, ANTI and OWM-BM by handing it their matrices."""
    name = "OWM"

    def __init__(self, P_by_room: Mapping[int, np.ndarray]):
        super().__init__()
        self.P_by_room = dict(P_by_room)
        self.P: Optional[np.ndarray] = None

    def begin_block(self, block: int, room_idx: int, L) -> None:
        self.P = self.P_by_room.get(room_idx)

    def __call__(self, L, upd: np.ndarray, db: np.ndarray):
        if self.P is None:
            return upd, db
        U = np.hstack([upd, db[:, None]])
        Up = U @ self.P
        self._record(L, U, Up)
        return Up[:, :-1], Up[:, -1]


class RestdArm(OwmArm):
    """OWM-RESTD: the matrix is rebuilt at every block from the earlier rooms' stored RAW rows standardised by the CURRENT statistics (Projectors.restd_P)."""
    name = "OWM-RESTD"

    def __init__(self, proj: "Projectors", tau: float):
        super().__init__({})
        self.proj, self.tau = proj, tau

    def begin_block(self, block: int, room_idx: int, L) -> None:
        self.P = self.proj.restd_P(self.tau, block, room_idx) if room_idx >= 2 else None


class NbArm(Arm):
    """OWM-NB: the projector built on the 146 inputs WITHOUT the constant; dV is projected, db is free."""
    name = "OWM-NB"

    def __init__(self, Pz_by_room: Mapping[int, np.ndarray]):
        super().__init__()
        self.Pz_by_room = dict(Pz_by_room)
        self.P: Optional[np.ndarray] = None

    def begin_block(self, block: int, room_idx: int, L) -> None:
        self.P = self.Pz_by_room.get(room_idx)

    def __call__(self, L, upd: np.ndarray, db: np.ndarray):
        if self.P is None:
            return upd, db
        up = upd @ self.P
        self._record(L, upd, up)
        return up, db


class OldOnlyArm(OwmArm):
    """OWM-OLDONLY: only the rows of the units that EXISTED when the room began are projected; words first heard in the room learn plain."""
    name = "OWM-OLDONLY"

    def __init__(self, P_by_room: Mapping[int, np.ndarray]):
        super().__init__(P_by_room)
        self.cur_room = 0
        self.w_start = 0

    def begin_block(self, block: int, room_idx: int, L) -> None:
        if room_idx != self.cur_room:
            self.cur_room = room_idx
            self.w_start = len(L.words)
        self.P = self.P_by_room.get(room_idx)

    def __call__(self, L, upd: np.ndarray, db: np.ndarray):
        if self.P is None:
            return upd, db
        U = np.hstack([upd, db[:, None]])
        Up = U @ self.P
        out = U.copy()
        out[:self.w_start] = Up[:self.w_start]
        self._record(L, U, out)
        return out[:, :-1], out[:, -1]


class FreezeArm(Arm):
    """STD-ONLY(j) (only_old=False): no weight or bias update after room j. FREEZE-OLD(j) (only_old=True): only the units that existed when room j ended stop updating."""

    def __init__(self, after_room: int, only_old: bool):
        super().__init__()
        self.after_room, self.only_old = int(after_room), bool(only_old)
        self.name = f"{'FREEZE-OLD' if only_old else 'STD-ONLY'}({after_room})"
        self.room = 0
        self.w_end: Optional[int] = None

    def begin_block(self, block: int, room_idx: int, L) -> None:
        self.room = room_idx
        if room_idx > self.after_room and self.w_end is None:
            self.w_end = len(L.words)                      # the words heard through the end of room `after_room`

    def __call__(self, L, upd: np.ndarray, db: np.ndarray):
        if self.room <= self.after_room:
            return upd, db
        if not self.only_old:
            return np.zeros_like(upd), np.zeros_like(db)
        a, b = upd.copy(), db.copy()
        a[:self.w_end] = 0.0
        b[:self.w_end] = 0.0
        return a, b


class ScaleArm(Arm):
    """SHRINK: the plain step multiplied by the parent's realised scalar at the same scene (1 where the parent has none: room 1)."""
    name = "SHRINK"

    def __init__(self, rho: Mapping[int, float]):
        super().__init__()
        self.sched = {int(k): float(v) for k, v in rho.items()}

    def __call__(self, L, upd: np.ndarray, db: np.ndarray):
        r = self.sched.get(int(L.scenes), 1.0)
        self.rho[int(L.scenes)] = r
        return upd * r, db * r


# ================================================================================================ the pre-pass
class Projectors:
    """Everything an arm needs that depends only on (seed, tau): the rows [z || 1] as the learner saw them (T-MEM-1's sequential order, the first 500 scenes of each
    room), the cumulative Grams, alpha_tau, every projector and null, the null dimensions. Rooms are 1-based; a projector used in room r is built from rooms 1..r-1."""

    def __init__(self, data, seed: int, rooms: Sequence[str] = ROOMS, blocks_per_room: int = BLOCKS_PER_ROOM):
        self.seed, self.rooms = int(seed), list(rooms)
        st = Lr.RunningStandardiser(Lr.RW_DIM)
        self.rows: Dict[str, np.ndarray] = {}
        self.raw: Dict[str, np.ndarray] = {}
        self.block_rows: Dict[int, np.ndarray] = {}
        self.stats_at: Dict[int, Lr.RunningStandardiser] = {}
        cursor = {r: 0 for r in self.rooms}
        per_room: Dict[str, List[np.ndarray]] = {r: [] for r in self.rooms}
        raw_room: Dict[str, List[np.ndarray]] = {r: [] for r in self.rooms}
        for block in range(1, len(self.rooms) * blocks_per_room + 1):
            room = self.rooms[(block - 1) // blocks_per_room]
            self.stats_at[block] = copy.deepcopy(st)       # the statistics at the START of the block
            blk: List[np.ndarray] = []
            for i in range(cursor[room], cursor[room] + BLOCK):
                X, _words = data.visit_scene(room, i)
                X = np.atleast_2d(np.asarray(X, dtype=np.float64))
                if X.shape[0] == 0:
                    continue                                # train_scene returns before observing an empty scene
                st.observe(X)
                Z = st.standardise(X)
                row = np.hstack([Z, np.ones((Z.shape[0], 1))])
                blk.append(row)
                per_room[room].append(row)
                raw_room[room].append(X)
            cursor[room] += BLOCK
            self.block_rows[block] = np.vstack(blk) if blk else np.zeros((0, DIM))
        for r in self.rooms:
            self.rows[r] = np.vstack(per_room[r])
            self.raw[r] = np.vstack(raw_room[r])
        self.G: Dict[int, np.ndarray] = {}
        self.n: Dict[int, int] = {}
        cum = np.zeros((0, DIM))
        for j in range(1, len(self.rooms)):                 # the spans a projector for rooms j+1.. protects
            cum = np.vstack([cum, self.rows[self.rooms[j - 1]]])
            self.G[j] = gram(cum)
            self.n[j] = int(cum.shape[0])
        self.lam1 = float(np.linalg.eigvalsh(self.G[1])[-1])
        self._cache: Dict[Tuple, object] = {}

    # ---- the resolution
    def alpha(self, tau: float) -> float:
        return tau * self.lam1

    # ---- OWM (soft, all rows)
    def owm(self, tau: float) -> Dict[int, np.ndarray]:
        key = ("owm", tau)
        if key not in self._cache:
            a = self.alpha(tau)
            self._cache[key] = {j + 1: owm_projector(self.G[j], a) for j in self.G}
        return self._cache[key]

    def capacity(self, tau: float, j: int) -> float:
        """The OWM paper's own measure: trace(I - P_j), the soft rank removed after rooms 1..j."""
        return float(DIM - np.trace(self.owm(tau)[j + 1]))

    # ---- NSCL (hard)
    def nscl(self, tau: float) -> Tuple[Dict[int, np.ndarray], Dict[int, int]]:
        key = ("nscl", tau)
        if key not in self._cache:
            mats, dims = {}, {}
            for j in self.G:
                P, d = nscl_projector(self.G[j], self.n[j], tau)
                mats[j + 1] = P
                dims[j] = d
            self._cache[key] = (mats, dims)
        return self._cache[key]

    # ---- the nulls
    def rot(self, tau: float, k: int) -> Dict[int, np.ndarray]:
        Q = haar(self.seed, f"ns:rot:{k}")
        return {r: rotate(P, Q) for r, P in self.owm(tau).items()}

    def rank(self, tau: float, k: int) -> Dict[int, np.ndarray]:
        Q = haar(self.seed, f"ns:rank:{k}")
        _mats, dims = self.nscl(tau)
        return {j + 1: random_subspace(Q, dims[j]) for j in dims}

    # ---- the readings
    def nb(self, tau: float) -> Dict[int, np.ndarray]:
        """OWM-NB: the projector on the 146 inputs without the constant, alpha = tau * lambda_max(G_1 restricted to them)."""
        Gz = {j: self.G[j][:-1, :-1] for j in self.G}
        a = tau * float(np.linalg.eigvalsh(Gz[1])[-1])
        return {j + 1: owm_projector(Gz[j], a) for j in Gz}

    def bm(self, tau: float) -> Dict[int, np.ndarray]:
        """OWM-BM: the Methods recursion over BATCH-MEAN inputs (a batch = one block of 10 scenes), alpha_BM = tau * lambda_max(G_1^BM); P_j over rooms 1..j."""
        means: Dict[int, np.ndarray] = {}
        for j in range(1, len(self.rooms)):
            bl = range((j - 1) * BLOCKS_PER_ROOM + 1, j * BLOCKS_PER_ROOM + 1)
            means[j] = np.vstack([self.block_rows[b].mean(axis=0, keepdims=True) for b in bl if self.block_rows[b].shape[0]])
        a = tau * float(np.linalg.eigvalsh(gram(means[1]))[-1])
        out: Dict[int, np.ndarray] = {}
        P = np.eye(DIM)
        for j in range(1, len(self.rooms)):
            P = rls_batches(means[j], a, P0=P)             # eq. (2) continued from the previous room's projector
            out[j + 1] = P.copy()
        return out

    def restd_P(self, tau: float, block: int, room_idx: int) -> np.ndarray:
        """The projector used in `block` (room `room_idx` >= 2) by OWM-RESTD: rooms < room_idx's RAW rows standardised by the statistics at the block's start."""
        key = ("restd", tau, block)
        if key not in self._cache:
            st = self.stats_at[block]
            rows = []
            for r in self.rooms[:room_idx - 1]:
                Z = st.standardise(self.raw[r])
                rows.append(np.hstack([Z, np.ones((Z.shape[0], 1))]))
            self._cache[key] = owm_projector(gram(np.vstack(rows)), self.alpha(tau))
        return self._cache[key]
