"""losses.py — TOY A: the second loss C, the snapshot stand-in for the drop's anatomy, the prequential loss.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:28 +0400 — new module, written to docs/research/toys/PREREG-TOY-CP.md §3 (`C`) and §4
# (the drop's anatomy) and AMEND-1; red-first (tests/tools/test_toys_cp.py). Nothing under brain/ is edited; this module IMPORTS the
# learner-side loss (`pickers.window_loss`, `pickers.hyp_probs`) and builds on it.

  window_L      S1c's loss: the mean noisy-OR cross-entropy over the FIXED 13 words on a held window (a delegate: identity with S1c).
  window_C      THE SECOND LOSS: per window scene, per type T in {shape, colour, size} for which the parent SAID a word w* of that type,
                C(i, T) = -log q_i(w*), q_i(w) = P_i(w) / sum_{w' in T} P_i(w'), P_i(w) the scene-level noisy-OR probability of w (an unheard
                word at sigma(0), the clip [1e-6, 1 - 1e-6]); C_k = the mean over the window's (scene, type) pairs. It reads what the parent
                SAID, never the truth. The word -> type map is the VOCABULARY's: an ORACLE element (the learner holds no types, R-TT).
  scene_loss_pre  a scene's own loss (the L arithmetic) under the CURRENT state, frozen — the PREQUENTIAL error LP-OUDEYER reads, taken
                before the update on the scene.
  Snap          a duck-typed learner state (`stats`, `index`, `V`, `b` over the 13 words, an unheard word at zero) that `pickers.hyp_probs`
                reads exactly as it reads a learner; `Snap.mix` takes the named components from the later state and the rest from the
                earlier one — the single-factor drops of PREREG-TOY-CP §4's anatomy (bias-only, weight-only, statistics-only).
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

import numpy as np

from brain.scene import learners as Lr
from brain.scene import pickers as PK
from brain.scene import rooms as RM
from brain.scene import run_s1c as S

VOCAB: Tuple[str, ...] = RM.VOCAB13
TYPE_WORDS: Dict[str, Tuple[str, ...]] = {t: tuple(ws) for t, ws in S.TYPE_WORDS.items()}
TYPES: Tuple[str, ...] = tuple(TYPE_WORDS)
TYPE_OF: Dict[str, str] = {w: t for t, ws in TYPE_WORDS.items() for w in ws}
TYPE_IDX: Dict[str, List[int]] = {t: [VOCAB.index(w) for w in ws] for t, ws in TYPE_WORDS.items()}
_TYPE_COL = {t: c for c, t in enumerate(TYPES)}
# the (T, 13) 0/1 membership matrix: a scene's per-type denominator is P @ MEMBER.T
MEMBER = np.zeros((len(TYPES), len(VOCAB)))
for _t, _idx in TYPE_IDX.items():
    MEMBER[_TYPE_COL[_t], _idx] = 1.0


def window_L(learner, ws) -> float:
    """S1c's held-window loss, unchanged (identity with the earlier rounds' tables)."""
    return PK.window_loss(learner, ws)


def _pairs(ws):
    """The window's (scene row, word column, type column) triples — what the parent said, per type — built once per WindowSet."""
    got = getattr(ws, "_toy_cp_pairs", None)
    if got is None:
        si: List[int] = []
        wc: List[int] = []
        tc: List[int] = []
        for i in range(ws.n):
            for w in ws.words[i]:
                t = TYPE_OF.get(w)
                if t is not None:
                    si.append(i)
                    wc.append(VOCAB.index(w))
                    tc.append(_TYPE_COL[t])
        got = (np.array(si, dtype=np.int64), np.array(wc, dtype=np.int64), np.array(tc, dtype=np.int64))
        ws._toy_cp_pairs = got
    return got


def scene_P(learner, ws) -> np.ndarray:
    """The scene-level noisy-OR probability of every one of the 13 words for every window scene, clipped (n, 13); a scene with no
    hypothesis reads P = 0 -> the clip (S1c's rule), so its per-type q is uniform."""
    if list(ws.vocab) != list(VOCAB):
        raise ValueError("the window's vocabulary is not the fixed 13-word vocabulary")
    p = PK.hyp_probs(learner, ws.X, ws.vocab)
    P = np.zeros((ws.n, len(VOCAB)))
    for i in range(ws.n):
        a, b = int(ws.starts[i]), int(ws.starts[i + 1])
        if b > a:
            P[i] = 1.0 - np.prod(1.0 - p[a:b], axis=0)
    return np.clip(P, PK.P_CLIP, 1.0 - PK.P_CLIP)


def window_C(learner, ws) -> float:
    """C_k, §3 of the law: the mean over the window's (scene, type) pairs of -log q_i(w*)."""
    si, wc, tc = _pairs(ws)
    if si.size == 0:
        return 0.0
    P = scene_P(learner, ws)
    den = P @ MEMBER.T                                    # (n, 3): the sum of P over each type's words
    q = P[si, wc] / den[si, tc]
    return float(np.mean(-np.log(q)))


def scene_loss_pre(learner, X, words: Sequence[str]) -> float:
    """A scene's own L-loss under the current state, frozen: pickers.scene_losses' arithmetic on one scene (the prequential error)."""
    p = PK.hyp_probs(learner, np.atleast_2d(np.asarray(X, dtype=np.float64)), VOCAB)
    P = 1.0 - np.prod(1.0 - p, axis=0) if p.shape[0] else np.zeros(len(VOCAB))
    P = np.clip(P, PK.P_CLIP, 1.0 - PK.P_CLIP)
    y = np.array([1.0 if w in words else 0.0 for w in VOCAB])
    return -float(np.sum(y * np.log(P) + (1.0 - y) * np.log(1.0 - P)))


class Snap:
    """A learner's state over the fixed 13 words as `pickers.hyp_probs` reads it: `stats` (a copy of the running standardiser), `index`
    (word -> row), `V` (13 x 146) and `b` (13), an unheard word at zero (its unit's start, the loss's own sigma(0) prior)."""

    def __init__(self, stats: Lr.RunningStandardiser, V: np.ndarray, b: np.ndarray):
        self.stats, self.V, self.b = stats, V, b
        self.index = {w: i for i, w in enumerate(VOCAB)}

    @staticmethod
    def of(learner) -> "Snap":
        V = np.zeros((len(VOCAB), learner.dim))
        b = np.zeros(len(VOCAB))
        for c, w in enumerate(VOCAB):
            j = learner.index.get(w)
            if j is not None:
                V[c] = learner.V[j]
                b[c] = learner.b[j]
        st = Lr.RunningStandardiser(learner.dim)
        st.n = learner.stats.n
        st.mean = learner.stats.mean.copy()
        st.m2 = learner.stats.m2.copy()
        return Snap(st, V, b)

    @staticmethod
    def mix(before: "Snap", after: "Snap", bias: bool = False, weights: bool = False, stats: bool = False) -> "Snap":
        """`before` with the named components taken from `after` (read-only sharing of the arrays)."""
        return Snap(after.stats if stats else before.stats, after.V if weights else before.V, after.b if bias else before.b)
