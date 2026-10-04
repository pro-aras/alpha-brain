"""tools/toys/w2/tl4_arith.py — the arms' arithmetic, VENDORED VERBATIM from tools/toys/tl4/arms.py at t-l4-1003
(source file sha256 396d556c27a029d2f321aa4e4f64b32b32bfe505dad8694cedb4a614ed22764c; the T-L4 branch is not merged
into master, so the W2 bench carries the functions it cites; the bodies below are byte-identical to the source's
oracle_fit / oracle_scores / const_scores / scene_scores / row_probs / score_window — see tools/toys/w2/VENDORED.md).

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:44 +0400 — vendored for the W2 build; law
docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 item 2 (the ORACLE's fit, the scene scorer, CONST — T-L4's own forms).
"""
from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np

from brain.scene import learners as Lr


def oracle_fit(Z: np.ndarray, y: np.ndarray, ridge: float = 1e-3, max_iter: int = 30, tol: float = 1e-6) -> Dict[str, object]:
    """Logistic regression by IRLS (Newton) on ROW-level targets, ridge on the weights (not the bias), at most max_iter iterations; the number of
    rows fed, the iteration count and the last change in the penalised loss are returned (the plant's assertions, §4)."""
    Z = np.asarray(Z, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    N, d = Z.shape
    Xa = np.concatenate([Z, np.ones((N, 1))], axis=1)
    theta = np.zeros(d + 1)
    reg = np.full(d + 1, ridge); reg[d] = 0.0

    def loss(th):
        eta = Xa @ th
        return float(np.sum(np.logaddexp(0.0, eta) - y * eta) + 0.5 * ridge * th[:d] @ th[:d])

    prev = loss(theta)
    last = float("inf")
    n_iter = 0
    for it in range(max_iter):
        eta = Xa @ theta
        p = Lr.sigmoid(eta)
        w = np.maximum(p * (1.0 - p), 1e-12)
        H = Xa.T @ (w[:, None] * Xa) + np.diag(reg)
        g = Xa.T @ (y - p) - reg * theta
        step = np.linalg.solve(H, g)
        theta = theta + step
        cur = loss(theta)
        last = abs(prev - cur)
        prev = cur
        n_iter = it + 1
        if last < tol:
            break
    return {"v": theta[:d].copy(), "b": float(theta[d]), "n_iter": int(n_iter), "last_change": float(last), "rows_fed": int(N),
            "converged": bool(last < tol), "loss": float(prev)}


def oracle_scores(stats: Lr.RunningStandardiser, v: np.ndarray, b: float, matrices: Sequence[np.ndarray]) -> np.ndarray:
    """The ORACLE's scene score with the SAME readout: noisy-OR over the rows of sigma(Z v + b), Z by the frozen standardiser."""
    out = np.zeros(len(matrices))
    for i, M in enumerate(matrices):
        Z = stats.standardise(M)
        p = Lr.sigmoid(Z @ v + b)
        out[i] = 1.0 - np.prod(1.0 - p)
    return out


def const_scores(rate: float, n: int) -> np.ndarray:
    """CONST: every moment scores the word's TRAIN rate (zero variance)."""
    return np.full(n, float(rate))


def scene_scores(L, X):
    """The learner's own scene prediction for every word: Z = standardise(X) (the statistics as frozen), P = sigma(Z V^T + b),
    score_w = 1 - prod_i (1 - P[i, w]). Rows and the learner, never the words (M6)."""
    Z = L.stats.standardise(X)
    P = Lr.sigmoid(Z @ L.V.T + L.b[None, :])
    return 1.0 - np.prod(1.0 - P, axis=0)


def row_probs(L, X) -> np.ndarray:
    """P[i, w] for every row and word (R-LOCUS, M4 (a))."""
    Z = L.stats.standardise(X)
    return Lr.sigmoid(Z @ L.V.T + L.b[None, :])


def score_window(L, matrices: Sequence[np.ndarray]) -> np.ndarray:
    return np.stack([scene_scores(L, M) for M in matrices], axis=0)
