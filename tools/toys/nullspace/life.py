"""life.py — TOY B's life: T-MEM-1's BASE sequential path (R1 x 50 blocks, R2 x 50, R3 x 50, N x 50, 10 scenes a block, no replay) with an arm's hook on the learner's step.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:45 +0400 — new module, written to docs/research/toys/PREREG-TOY-NULLSPACE.md §2, §4 (G2); red-first
# (tests/tools/test_toys_nullspace.py). It is a COPY of the BASE / seq path of brain/scene/run_tmem1.py `life_m1` (the answer roads, replay, gate and the other lives
# removed) with one difference: `train_scene(..., project=arm)`. For PlainArm the hook is None, so the learner's calls are T-MEM-1's own; the identity is not assumed —
# tests/tools/test_toys_nullspace.py::TestLife and the unit's gate G2 compare the record with T-MEM-1's BASE.json field for field (rates_rw, pairs, table, first_meet, every row).
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional

import numpy as np

from brain.scene import learners as Lr
from brain.scene import pickers as PK
from brain.scene import run_s1c as S
from brain.scene import run_tmem1 as T1
from brain.world.seeds import substream

from . import projector as NP

ROOMS = NP.ROOMS


def episodic_rng(seed: int, room: str, i: int):
    return substream(seed, f"episodic:room:{room}:visit:{i}")


def new_learner(lr_scale: float = 1.0):
    """S1b-1's A-RW at lr 0.01 (run_s1c.new_learner); for the LRSHRINK frontier arms the same learner with lr x s."""
    if lr_scale == 1.0:
        return S.new_learner()
    return Lr.RWLearner(lr=Lr.LR_S1B1 * float(lr_scale), oracle=False)


def learner_rows(data, blocks_per_room: int = NP.BLOCKS_PER_ROOM) -> Dict[str, np.ndarray]:
    """G4's measurement: the rows [z || 1] a learner ACTUALLY receives in T-MEM-1's sequential order — an unhooked training pass in which, after each `train_scene`, the learner's
    own running statistics standardise the scene's inputs (the statistics the update just used: observe first, then standardise). Compared with the pre-pass's rows by the gate.
    edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:48 +0400 — added with run.py's gate."""
    L = S.new_learner()
    rooms = list(ROOMS)
    got: Dict[str, List[np.ndarray]] = {r: [] for r in rooms}
    cursor = {r: 0 for r in rooms}
    for block in range(1, len(rooms) * blocks_per_room + 1):
        room = rooms[(block - 1) // blocks_per_room]
        for i in range(cursor[room], cursor[room] + PK.BLOCK):
            X, words = data.visit_scene(room, i)
            L.train_scene(X, words, referent=None, rng=episodic_rng(data.seed, room, i))
            Xa = np.atleast_2d(np.asarray(X, dtype=np.float64))
            if Xa.shape[0]:
                got[room].append(np.hstack([L.stats.standardise(Xa), np.ones((Xa.shape[0], 1))]))
        cursor[room] += PK.BLOCK
    return {r: np.vstack(v) for r, v in got.items()}


def life_ns(data, test, arm: NP.Arm, label: str, n_blocks: int = 200, rep: Optional[int] = None,
            prereg: Optional[Dict[str, str]] = None) -> Dict[str, object]:
    cpu0, wall0 = time.process_time(), time.time()
    seed, rooms = data.seed, list(ROOMS)
    L = new_learner(arm.lr_scale)
    project = None if isinstance(arm, NP.PlainArm) else arm
    cursor = {r: 0 for r in rooms}
    Lk = {r: PK.window_loss(L, data.window[r]) for r in rooms}
    table = [dict(Lk)]
    _wl, rates0 = test.words_learned(L)
    rates_rw = [rates0]
    first_meet: Dict[str, int] = {}
    pairs: Dict[int, object] = {}
    rec: List[Dict[str, object]] = []
    for block in range(1, n_blocks + 1):
        room_idx = (block - 1) // NP.BLOCKS_PER_ROOM + 1
        room = rooms[room_idx - 1]
        arm.begin_block(block, room_idx, L)
        start = cursor[room]
        for i in range(start, start + PK.BLOCK):
            X, words = data.visit_scene(room, i)
            L.train_scene(X, words, referent=None, rng=episodic_rng(seed, room, i), project=project)
            for w in dict.fromkeys(words):
                first_meet.setdefault(w, block)
        cursor[room] += PK.BLOCK
        Lpost = {r: PK.window_loss(L, data.window[r]) for r in rooms}
        drop = Lk[room] - Lpost[room]
        wl, rates = test.words_learned(L)
        rates_rw.append(rates)
        if block in T1.READ_POINTS:
            pairs[block] = test.pairs_rw(L, T1.SHAPE_TASKS)
        rec.append({"block": block, "room": room, "flag": "seq", "start": start, "L": Lpost, "drop": drop, "wl": wl})
        table.append(dict(Lpost))
        Lk = Lpost
    out: Dict[str, object] = {"seed": seed, "life": label, "schedule": "seq", "rooms": rooms, "n_blocks": n_blocks, "record": rec, "table": table,
                              "rates_rw": rates_rw, "pairs": pairs, "first_meet": first_meet, "word_n": test.word_n,
                              "cpu_s": time.process_time() - cpu0, "wall_s": time.time() - wall0, "prereg": dict(prereg or {})}
    out["extra"] = {"arm": label, "rep": rep, "rho": {str(k): v for k, v in getattr(arm, "rho", {}).items()}, "lr_scale": arm.lr_scale,
                    "n_words_end": len(L.words), "scenes": L.scenes}
    return out
