"""tools/toys/w2/feed.py — PREREG-W2 §3: the SHARED feed over the REAL rows (T-L4 §3.2's interface, verbatim in kind).

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:35 +0400 — new file, written after tests/tools/test_w2_bench.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 item 2 (the SHARED state row constructed offline; always
present; the thresholded flags; thing-feature dims at thing scale; the corner kind tag; NEVER the wide channel).

build(Xs, states, interface, window, frozen_mean): one matrix per canvas. SHARED ("S"): the state row appended after the
canvas's real X rows — dims 0-5 the CODE-F six, dims 6-143 the NEUTRAL FILL (the standardiser's running mean as it stands
when the moment is handed over), dims 144-145 = (0.0, 0.0) the declared kind tag. NOSTATE ("N"): the X rows alone. TRAIN:
a SHADOW standardiser observes each matrix as the learner will (so the fill is the mean as it stands); the learner's own
standardiser must end byte-identical to it (the G0g form). TEST: the fill is the frozen mean, nothing is observed.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np

from brain.scene import learners as Lr

DIM = 146
STATE_DIM = 6
FEATS = 144


def build(Xs: Sequence[np.ndarray], states: Sequence[np.ndarray], interface: str, window: str = "train",
          frozen_mean: Optional[np.ndarray] = None) -> Tuple[List[np.ndarray], Lr.RunningStandardiser]:
    assert interface in ("S", "N")
    assert len(Xs) == len(states)
    stats = Lr.RunningStandardiser(DIM)
    if window == "test":
        assert frozen_mean is not None and np.asarray(frozen_mean).shape == (DIM,), "a TEST feed needs the learner's frozen mean"
    mats: List[np.ndarray] = []
    for X, s in zip(Xs, states):
        X = np.asarray(X, dtype=np.float64)
        if interface == "N":
            M = X.copy()
        else:
            mean = stats.mean if window == "train" else np.asarray(frozen_mean, dtype=np.float64)
            r = np.zeros(DIM)
            r[:STATE_DIM] = np.asarray(s, dtype=np.float64)
            r[STATE_DIM:FEATS] = mean[STATE_DIM:FEATS]
            M = np.vstack([X, r[None, :]])
        mats.append(M)
        if window == "train":
            stats.observe(M)
    return mats, stats
