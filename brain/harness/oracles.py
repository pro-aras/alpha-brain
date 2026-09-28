"""oracles.py — STAGE -1 CLAUSE 3: the two organ-ceiling oracles, F_pool, and the permutation null
(B1-PREREG.md §3.3).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:4x +0400 — B1-PREREG.md §9 row 1, step 4 (stage −1).

"The features an oracle sees — two, because the order of the located glances follows surprise and changes
from canvas to canvas: F_cat(canvas) = the gaze's feature vectors concatenated in their order, unit-
normalised; F_pool(canvas) = the creature's own BIND pooling — creature/mind.py:_bind_pool applied to the
gaze's feats (their mean, unit-normalised), order-free. Every θ, cosine filter and identity test below uses
F_pool." `f_cat` is implemented here for completeness (a caller MAY want it for a report) but nothing in
`stage_minus1.py` uses it for a ceiling, θ or identity test, per that sentence.

"Two oracles ... (a) 1-NN — the label of the nearest TEACH exemplar by cosine of F, ties by label order;
(b) a linear read-out — multinomial logistic regression with an L2 penalty of 1.0, fitted on the TEACH
exemplars by scipy.optimize.minimize(method='L-BFGS-B') in float64 from a zero start, maxiter 500, under
/usr/bin/python3 (no sklearn on the box; deterministic by construction)."

This module's regularisation convention (since §3.3 names the penalty's MAGNITUDE, 1.0, but not its exact
functional form): `loss = mean_cross_entropy + 0.5 * penalty * mean(||W||^2)`, bias unpenalised — a
standard multinomial softmax form, declared here once so every fit is reproducible against this same
convention, not against scipy's or sklearn's differing defaults (sklearn is not on the box at all).
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy.optimize import minimize

from creature.mind import _bind_pool   # the creature's OWN pooling, reused verbatim (§3.3)


def f_pool(glances: np.ndarray) -> np.ndarray:
    """(5, 144) (or any (k, d)) glance features -> ONE order-free unit vector, via the creature's own
    `_bind_pool` (mean, then unit-renormalise)."""
    pooled = _bind_pool(list(np.asarray(glances, dtype=np.float64)))
    return pooled[0]


def f_cat(glances: np.ndarray) -> np.ndarray:
    """The gaze's feature vectors concatenated IN THEIR GIVEN ORDER, unit-normalised. Declared for
    completeness (§3.3 names it as the reason F_pool is needed) — not used by any ceiling/θ/identity test."""
    v = np.asarray(glances, dtype=np.float64).reshape(-1)
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


class OracleError(Exception):
    pass


class NearestNeighbourOracle:
    """1-NN over unit-norm F_pool vectors (cosine == dot product); ties broken by LABEL ORDER (alphabetical
    string order of the label name)."""

    def __init__(self) -> None:
        self.exemplars: np.ndarray = np.zeros((0, 0))
        self.labels: List[str] = []

    def fit(self, X: np.ndarray, y: Sequence[str]) -> "NearestNeighbourOracle":
        X = np.asarray(X, dtype=np.float64)
        if X.shape[0] != len(y):
            raise OracleError(f"fit: {X.shape[0]} exemplars but {len(y)} labels")
        self.exemplars = X
        self.labels = list(y)
        return self

    def predict_one(self, query: np.ndarray) -> str:
        if self.exemplars.shape[0] == 0:
            raise OracleError("predict on an unfitted NearestNeighbourOracle")
        cos = self.exemplars @ np.asarray(query, dtype=np.float64)
        best = float(cos.max())
        tied = sorted({self.labels[i] for i in np.flatnonzero(np.isclose(cos, best))})
        return tied[0]

    def predict(self, X: np.ndarray) -> List[str]:
        return [self.predict_one(x) for x in np.asarray(X, dtype=np.float64)]


class LinearReadoutOracle:
    """Multinomial logistic regression, L2 penalty 1.0 (this module's convention, see the header docstring),
    fit by L-BFGS-B in float64 from an all-zero start, maxiter 500 — deterministic by construction (no
    random initialisation, no stochastic solver)."""

    PENALTY = 1.0
    MAXITER = 500

    def __init__(self) -> None:
        self.classes_: List[str] = []
        self.W: np.ndarray = np.zeros((0, 0))
        self.b: np.ndarray = np.zeros((0,))

    def fit(self, X: np.ndarray, y: Sequence[str]) -> "LinearReadoutOracle":
        X = np.asarray(X, dtype=np.float64)
        classes = sorted(set(y))
        if len(classes) < 2:
            raise OracleError(f"fit: need >= 2 classes, got {classes}")
        C = len(classes)
        N, D = X.shape
        idx = {lbl: i for i, lbl in enumerate(classes)}
        y_idx = np.array([idx[lbl] for lbl in y], dtype=np.int64)
        Y = np.zeros((N, C), dtype=np.float64)
        Y[np.arange(N), y_idx] = 1.0
        penalty = self.PENALTY

        def unpack(theta: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
            return theta[:D * C].reshape(D, C), theta[D * C:]

        def loss_and_grad(theta: np.ndarray) -> Tuple[float, np.ndarray]:
            W, b = unpack(theta)
            Z = X @ W + b
            Z = Z - Z.max(axis=1, keepdims=True)
            expZ = np.exp(Z)
            P = expZ / expZ.sum(axis=1, keepdims=True)
            nll = -float(np.sum(Y * np.log(np.clip(P, 1e-15, None)))) / N
            l2 = 0.5 * penalty * float(np.sum(W * W)) / N
            loss = nll + l2
            dZ = (P - Y) / N
            dW = X.T @ dZ + penalty * W / N
            db = dZ.sum(axis=0)
            return loss, np.concatenate([dW.reshape(-1), db])

        theta0 = np.zeros(D * C + C, dtype=np.float64)
        res = minimize(loss_and_grad, theta0, jac=True, method="L-BFGS-B", options={"maxiter": self.MAXITER})
        self.W, self.b = unpack(res.x)
        self.classes_ = classes
        return self

    def predict(self, X: np.ndarray) -> List[str]:
        if not self.classes_:
            raise OracleError("predict on an unfitted LinearReadoutOracle")
        X = np.asarray(X, dtype=np.float64)
        Z = X @ self.W + self.b
        return [self.classes_[i] for i in np.argmax(Z, axis=1)]


def accuracy(pred: Sequence[str], truth: Sequence[str]) -> float:
    if len(pred) != len(truth):
        raise OracleError(f"accuracy: {len(pred)} predictions vs {len(truth)} truths")
    if len(pred) == 0:
        raise OracleError("accuracy: empty")
    return sum(1 for p, t in zip(pred, truth) if p == t) / len(pred)


def permutation_null(fit_predict, X_train: np.ndarray, y_train: Sequence[str], X_test: np.ndarray,
                      y_test: Sequence[str], seed: int, n_perm: int = 20) -> Dict[str, object]:
    """§3.3's own null: "the linear oracle refitted with labels permuted among the TEACH exemplars (20
    seeded permutations; mean and p95 printed)." `fit_predict(X_train, y_perm, X_test) -> List[str]` lets
    the caller reuse this for either oracle, not just the linear one."""
    rng = np.random.default_rng(seed)
    y_train = list(y_train)
    scores = []
    for _ in range(n_perm):
        perm = rng.permutation(len(y_train))
        y_shuffled = [y_train[i] for i in perm]
        pred = fit_predict(X_train, y_shuffled, X_test)
        scores.append(accuracy(pred, y_test))
    arr = np.array(scores, dtype=np.float64)
    return {"n_perm": n_perm, "scores": scores, "mean": float(arr.mean()), "p95": float(np.percentile(arr, 95))}
