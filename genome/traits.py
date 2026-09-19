"""genome/traits.py — B12 (docs/G4-PREREG.md §11.2): TRAITS, the learned contrast head. A seeded random
orthogonal projection at birth, refined by InfoNCE contrastive learning at sleep (two glances of the
same canvas pulled near, different canvases pushed apart) over the last 256 episodes that carry a
second glance (genome/fast.py's B12 extension, `Episodes.write(..., x_s2=...)`).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — new module, Wave 2 B12.

Interface fixed for Builder A:
    class Traits(dim_in=112, dim_out=32, lr, rng)
        H                       # (dim_out, dim_in) — a seeded random orthogonal projection at birth
        apply(x) -> np.ndarray  # H @ x (raw, unnormalised — genome/machinery.py's Area.cos normalises)
        learn(episodes, steps<=20) -> dict   # InfoNCE, in-place update of H

genome/machinery.py's Area.cos reads `self.traits.H` and `self.traits.version` (bumped once per learn()
call that actually ran a step) when `org.sight.traits` is set — TRAITS undeclared -> that attribute
stays None for the whole life -> Area.cos's untouched two-line path -> the pin is unaffected.

Design decisions made and documented here:

  1. H's construction. A random (dim_in, dim_in) matrix is QR-decomposed; the first `dim_out` COLUMNS
     of the orthogonal factor Q are orthonormal by construction, and their TRANSPOSE is a (dim_out,
     dim_in) matrix whose ROWS are orthonormal (H @ H.T == I_{dim_out}) — "a seeded random orthogonal
     projection", read literally. An optional `H=` constructor kwarg lets a caller supply an exact H
     (used by the identity control below, and only there) without changing the four-argument interface
     Builder A depends on (it is keyword-only and defaults to None).

  2. `apply(x)` returns the RAW projection `H @ x`, unnormalised — cosine normalisation happens once,
     at the point that actually needs a cosine (Area.cos, or `learn`'s own InfoNCE loss), never twice.

  3. `learn`'s InfoNCE. Batch = every episode with `has_s2` true, most recent first (by id), capped at
     256. Embeddings z1 = H @ x_s, z2 = H @ x_s2, each L2-normalised; similarity S = (z1n @ z2n.T) / tau
     (tau = 0.1, a fixed, documented temperature — the PREREG names InfoNCE but not a temperature);
     softmax cross-entropy with the diagonal as the positive (canvas i's two glances are its own
     positive pair; every OTHER episode in the batch, same canvas or not, is a negative for row i — with
     one row per DISTINCT canvas in the batch this is exactly "different canvases far"). Gradient is the
     standard softmax-CE-through-L2-normalise derivation (worked out in `_infonce_grad`'s docstring);
     `steps` is clipped to at most 20 (the PREREG's own bound) and to at least 0; fewer than 2 usable
     episodes -> a no-op (0 steps, reported, never an error — nothing to contrast against fewer than 2
     positives).

  4. The identity control (B12's toy (b)). The PREREG's own text — "H = I (first 32 rows) reproduces
     raw cos exactly" — is only true when dim_out == dim_in: a 32-row slice of a 112x112 identity is a
     112->32 SUBSPACE projection, and cos of a 32-d sub-vector is provably NOT the raw 112-d cosine (it
     drops 80 of the vector's coordinates, including all of the norm they carry) — this is checked and
     RAISED in tests/genome/test_traits.py as a clause that cannot be met as literally written for
     dim_out < dim_in. The identity control that IS honestly checkable is dim_out == dim_in == 112,
     H = I(112): Area.cos with that head must reproduce the raw (untraited) cos EXACTLY.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

TAU = 0.1  # InfoNCE temperature — fixed, documented (decision 3 above); not read from any gene


def _orthogonal_rows(dim_out: int, dim_in: int, rng: np.random.Generator) -> np.ndarray:
    """A (dim_out, dim_in) matrix with orthonormal ROWS (H @ H.T == I), dim_out <= dim_in required.
    Draws a random (dim_in, dim_in) matrix, QR-decomposes it, and transposes the first dim_out columns
    of the orthogonal factor (decision 1 above)."""
    if dim_out > dim_in:
        raise ValueError(f"Traits: dim_out ({dim_out}) must be <= dim_in ({dim_in})")
    a = rng.normal(size=(dim_in, dim_in))
    q, _r = np.linalg.qr(a)
    return np.ascontiguousarray(q[:, :dim_out].T)


def _l2_normalize_rows(m: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(m, axis=1, keepdims=True)
    n = np.where(n == 0.0, 1.0, n)
    return m / n


class Traits:
    def __init__(self, dim_in: int = 112, dim_out: int = 32, lr: float = 0.01, rng: Optional[np.random.Generator] = None,
                 *, H: Optional[np.ndarray] = None) -> None:
        self.dim_in = int(dim_in)
        self.dim_out = int(dim_out)
        self.lr = float(lr)
        self.rng = rng if rng is not None else np.random.default_rng()
        if H is not None:
            H = np.array(H, dtype=np.float64)
            if H.shape != (self.dim_out, self.dim_in):
                raise ValueError(f"Traits: H must be shape ({self.dim_out}, {self.dim_in}), got {H.shape}")
            self.H = H
        else:
            self.H = _orthogonal_rows(self.dim_out, self.dim_in, self.rng)
        self.version = 0  # bumped once per learn() call that actually took a step — Area.cos's cache key

    def apply(self, x: np.ndarray) -> np.ndarray:
        """H @ x — the raw projection, unnormalised (decision 2 above)."""
        return self.H @ x

    # ------------------------------------------------------------------------------------- learn
    def learn(self, episodes, steps: int = 20) -> Dict[str, object]:
        """InfoNCE over the last <=256 episodes carrying a second glance (decision 3 above). Updates
        `self.H` in place (`steps` gradient steps, each `lr`-scaled) and bumps `self.version` once if
        at least one step ran. Returns a report dict — always, never raises on an empty/small batch."""
        steps = max(0, min(int(steps), 20))
        if episodes is None or len(episodes) == 0:
            return {"steps": 0, "batch": 0, "reason": "no episodes"}
        idx = [i for i in range(len(episodes)) if bool(episodes.has_s2[i])]
        if len(idx) < 2:
            return {"steps": 0, "batch": len(idx), "reason": "fewer than 2 episodes carry a second glance"}
        idx.sort(key=lambda i: -int(episodes.ids[i]))
        idx = idx[:256]
        X1 = np.array([episodes.x_s[i] for i in idx], dtype=np.float64)
        X2 = np.array([episodes.x_s2[i] for i in idx], dtype=np.float64)

        loss_before = self._infonce_loss(X1, X2)
        for _ in range(steps):
            self._infonce_step(X1, X2)
        loss_after = self._infonce_loss(X1, X2) if steps > 0 else loss_before
        if steps > 0:
            self.version += 1
        return {"steps": steps, "batch": len(idx), "loss_before": loss_before, "loss_after": loss_after}

    def _forward(self, X1: np.ndarray, X2: np.ndarray):
        Z1 = X1 @ self.H.T          # (B, dim_out)
        Z2 = X2 @ self.H.T
        n1 = np.linalg.norm(Z1, axis=1, keepdims=True); n1 = np.where(n1 == 0.0, 1.0, n1)
        n2 = np.linalg.norm(Z2, axis=1, keepdims=True); n2 = np.where(n2 == 0.0, 1.0, n2)
        Zn1, Zn2 = Z1 / n1, Z2 / n2
        S = (Zn1 @ Zn2.T) / TAU     # (B, B)
        S = S - S.max(axis=1, keepdims=True)  # numerically stable softmax
        P = np.exp(S)
        P = P / P.sum(axis=1, keepdims=True)
        return Z1, Z2, n1, n2, Zn1, Zn2, P

    def _infonce_loss(self, X1: np.ndarray, X2: np.ndarray) -> float:
        *_rest, P = self._forward(X1, X2)
        B = P.shape[0]
        diag = np.clip(np.diag(P), 1e-12, None)
        return float(-np.mean(np.log(diag)))

    def _infonce_step(self, X1: np.ndarray, X2: np.ndarray) -> None:
        """One gradient step of InfoNCE (decision 3): the diagonal of the batch is the positive pair
        (canvas i's two glances), every other row is a negative. Standard softmax-cross-entropy-through-
        L2-normalise backprop, worked out by hand (no autodiff library in this estate's numpy-only
        machinery):

            S_ij = (H x1_i / ||H x1_i||) . (H x2_j / ||H x2_j||) / tau
            P = softmax(S, axis=1);  L = -mean_i log P[i, i]
            dL/dS = (P - I) / B
            dL/dZn1_i = (dL/dS[i,:] @ Zn2) / tau           (and symmetrically for Zn2)
            dL/dz  = (g - (g . zn) zn) / ||z||              (L2-normalise backward, z=H@x, zn=z/||z||)
            dL/dH  = dZ1.T @ X1 + dZ2.T @ X2
        """
        B = X1.shape[0]
        Z1, Z2, n1, n2, Zn1, Zn2, P = self._forward(X1, X2)
        dS = (P - np.eye(B)) / B
        dZn1 = (dS @ Zn2) / TAU
        dZn2 = (dS.T @ Zn1) / TAU

        def _unnorm_grad(g: np.ndarray, zn: np.ndarray, n: np.ndarray) -> np.ndarray:
            dot = np.sum(g * zn, axis=1, keepdims=True)
            return (g - dot * zn) / n

        dZ1 = _unnorm_grad(dZn1, Zn1, n1)
        dZ2 = _unnorm_grad(dZn2, Zn2, n2)
        dH = dZ1.T @ X1 + dZ2.T @ X2
        self.H = self.H - self.lr * dH
