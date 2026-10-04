"""tools/toys/w2/arms.py — PREREG-W2 §3 item 2 / §5: the arms' own primitives over the REAL stream (T-L4 §4-§5's forms).

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:44 +0400 — new file, written after tests/tools/test_w2_bench.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 item 2. The learner is the organism's own
`brain.scene.learners.RWLearner(lr = 0.01, p_from = 3)`, never edited; the per-canvas generator is
`substream(seed, "w2:episodic:<t>")` (T-L4's arms.py:245's form). The ORACLE's fit, the scorer, CONST and the grader are
the bench's own vendored arithmetic (tools/toys/w2/grade.py and tl4_arith.py — see VENDORED.md).
"""
from __future__ import annotations

from typing import List, Sequence

import numpy as np

from brain.scene import learners as Lr
from brain.world.seeds import substream
from tools.toys.w2 import tl4_arith as TA

STATE_WORDS = ("unsure", "fresh", "asked")
oracle_fit = TA.oracle_fit
oracle_scores = TA.oracle_scores
const_scores = TA.const_scores


def train_arm(matrices: Sequence[np.ndarray], utterances: Sequence[Sequence[str]], seed: int, lr: float = 0.01,
              dim: int = 146) -> Lr.RWLearner:
    """Drive `RWLearner(lr, dim)` over the TRAIN canvases with rng = substream(seed, "w2:episodic:<t>") (the bench seed's
    name is NOT in the moment's name, so every arm shares its tie draws)."""
    L = Lr.RWLearner(lr=lr, dim=dim)
    for t, (M, words) in enumerate(zip(matrices, utterances)):
        rng = substream(seed, f"w2:episodic:{t}")
        L.train_scene(M, list(words), referent=None, rng=rng)
    return L


def score_window(L: Lr.RWLearner, matrices: Sequence[np.ndarray]) -> np.ndarray:
    return TA.score_window(L, matrices)


def state_word_columns(L: Lr.RWLearner) -> List[int]:
    return [L.index[w] for w in STATE_WORDS if w in L.index]
