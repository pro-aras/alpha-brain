"""slda.py — a VERBATIM copy of b1-reader's StreamingLDA (P-ORACLE's and ORACLE-TRUTH's reader; PREREG-R3-TONIGHT §S1a:
«the streaming LDA reader, the namer of F19 (brain/arms/soft/readers.py's StreamingLDA: within-class covariance, relative
ε chosen on the toy seed only)»).

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:07 +0400 — copied, not imported: the source tree /data/dev/genome-wt-b12 (branch
b1-reader, 45c883e) is another worktree this builder must not modify or depend on at run time. Copied by `ast` source
segments (SLDA_RING, _f64, _fbytes, class StreamingLDA) from
  /data/dev/genome-wt-b12/brain/arms/soft/readers.py
  sha256 db4915b27149664a605d2ffcf2021fe08151dd83ac316911eb8d3dc8801499d5
tests/brain/scene/test_slda_copy.py pins every copied segment's text against that file (skipped where it is absent).
Only the reader's MEANS, its within-class Σ and Λ = [(1 − ε)Σ + ε (trace Σ / d) I]⁻¹ (sleep) and `distances()` are read
by S1a; its own p95 / p5 bands and `answer()` are R49's and are NOT used (the PREREG's bands are conformal 0.90 per word,
computed in brain/scene/learners.py).
"""
from __future__ import annotations

import collections
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

SOURCE_PATH = "/data/dev/genome-wt-b12/brain/arms/soft/readers.py"
SOURCE_SHA256 = "db4915b27149664a605d2ffcf2021fe08151dd83ac316911eb8d3dc8801499d5"
SOURCE_COMMIT = "45c883e"

SLDA_RING = 4096


def _f64(x) -> np.ndarray:
    return np.asarray(x, dtype=np.float64).ravel()


def _fbytes(v: Optional[float]) -> bytes:
    return b"none" if v is None else np.float64(v).tobytes()


class StreamingLDA:
    """The reader of CONCLUSION-R2 §3 law 2 (Hayes & Kanan 2020's streaming LDA with R49's S1 and S2, plus the two bands).
    `observe(x, name)` is one labelled showing; `sleep()` recomputes Λ and the bands; `answer(x)` →
    (kind ∈ {NAME, UNKNOWN, NOTHING}, name or None, info). Class order = first observed."""

    def __init__(self, eps: float, ring: int = SLDA_RING) -> None:
        self.eps = float(eps)
        if not (0.0 < self.eps <= 1.0):
            raise ValueError(f"StreamingLDA: ε must be in (0, 1], got {eps!r}")
        self.ring_cap = int(ring)
        self.names: List[str] = []
        self.means: List[np.ndarray] = []
        self.counts: List[int] = []
        self.dim = 0
        self.S = np.zeros((0, 0), dtype=np.float64)
        self.nS = 0
        self.Lam: Optional[np.ndarray] = None
        self.band_dist: Optional[float] = None
        self.band_margin: Optional[float] = None
        self.ring: collections.deque = collections.deque(maxlen=self.ring_cap)
        self.sleeps = 0

    # -- learning ---------------------------------------------------------------------------------
    def _grow(self, d: int) -> None:
        if d <= self.dim:
            return
        self.means = [np.concatenate([m, np.zeros(d - m.size)]) for m in self.means]
        S = np.zeros((d, d), dtype=np.float64)
        S[: self.dim, : self.dim] = self.S
        self.S = S
        self.dim = d

    def _pad(self, x: np.ndarray, d: int) -> np.ndarray:
        if x.size >= d:
            return x[:d]
        return np.concatenate([x, np.zeros(d - x.size)])

    def observe(self, x, name: str) -> None:
        x = _f64(x).copy()
        self._grow(x.size)
        x = self._pad(x, self.dim)
        name = str(name)
        if name not in self.names:
            self.names.append(name)
            self.means.append(x.copy())                      # a new name's mean = its first state
            self.counts.append(1)
            idx = len(self.names) - 1
        else:
            idx = self.names.index(name)
            self.counts[idx] += 1
            mu = self.means[idx]
            d = x - mu
            mu += d / self.counts[idx]
            self.S += np.outer(d, x - mu)                    # S1: deviations from the showing's OWN class mean
            self.nS += 1
        self.ring.append((idx, x))

    def sigma(self) -> np.ndarray:
        return self.S / max(self.nS, 1)

    def sleep(self) -> None:
        """S2: Λ = [(1 − ε)Σ + ε (trace Σ / d) I]⁻¹ at the current width, then the two bands over the ring (D27, D28)."""
        self.sleeps += 1
        d = self.dim
        if d == 0 or not self.names:
            return
        S = self.sigma()
        tr = float(np.trace(S))
        if not np.isfinite(tr) or tr <= 0.0:
            self.Lam = np.eye(d, dtype=np.float64)           # D27
        else:
            self.Lam = np.linalg.inv((1.0 - self.eps) * S + self.eps * (tr / d) * np.eye(d))
        self.band_dist, self.band_margin = self._bands()

    def _bands(self) -> Tuple[Optional[float], Optional[float]]:
        if not self.ring:
            return None, None
        dL = self.Lam.shape[0]
        X = np.stack([self._pad(x, dL) for _i, x in self.ring])
        y = np.array([i for i, _x in self.ring], dtype=np.int64)
        M = np.stack([m[:dL] for m in self.means])
        D = X - M[y]
        dist = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", D, self.Lam, D), 0.0))
        band_dist = float(np.quantile(dist, 0.95))
        if len(self.names) < 2:
            return band_dist, None
        W = M @ self.Lam
        c = -0.5 * np.einsum("ij,ij->i", W, M)
        s = X @ W.T + c
        top2 = np.partition(s, -2, axis=1)[:, -2:]
        margins = top2[:, 1] - top2[:, 0]
        return band_dist, float(np.quantile(margins, 0.05))

    # -- reading ----------------------------------------------------------------------------------
    def _metric(self) -> Tuple[int, np.ndarray]:
        if self.Lam is not None:
            return self.Lam.shape[0], self.Lam
        return self.dim, np.eye(self.dim, dtype=np.float64)          # D27: before the first sleep

    def scores(self, x) -> np.ndarray:
        if not self.names:
            return np.zeros(0)
        dL, L = self._metric()
        xv = self._pad(_f64(x), dL)
        M = np.stack([m[:dL] for m in self.means])
        W = M @ L
        return W @ xv - 0.5 * np.einsum("ij,ij->i", W, M)

    def distances(self, x) -> np.ndarray:
        if not self.names:
            return np.zeros(0)
        dL, L = self._metric()
        D = self._pad(_f64(x), dL)[None, :] - np.stack([m[:dL] for m in self.means])
        return np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", D, L, D), 0.0))

    def argmax(self, x) -> Optional[str]:
        s = self.scores(x)
        return self.names[int(np.argmax(s))] if s.size else None

    def answer(self, x) -> Tuple[str, Optional[str], Dict[str, Any]]:
        if not self.names:
            return "UNKNOWN", None, {"why": "no name heard"}
        s = self.scores(x)
        top = int(np.argmax(s))
        margin = float(s[top] - np.max(np.delete(s, top))) if s.size > 1 else float("inf")
        dist = float(np.min(self.distances(x)))
        info = {"dist": dist, "margin": margin, "band_dist": self.band_dist, "band_margin": self.band_margin,
                "forced": self.names[top]}
        if self.band_dist is not None and dist > self.band_dist:
            return "UNKNOWN", None, info
        if self.band_margin is not None and margin < self.band_margin:
            return "NOTHING", None, info
        return "NAME", self.names[top], info

    # -- identity ---------------------------------------------------------------------------------
    def state_bytes(self) -> bytes:
        h = hashlib.sha256()
        for part in (b"StreamingLDA", np.float64(self.eps).tobytes(), str(self.ring_cap).encode(), str(self.dim).encode(),
                     json.dumps(self.names).encode(), json.dumps(self.counts).encode(), str(self.nS).encode(),
                     str(self.sleeps).encode(), self.S.tobytes(), _fbytes(self.band_dist), _fbytes(self.band_margin),
                     (b"none" if self.Lam is None else str(self.Lam.shape).encode() + self.Lam.tobytes())):
            h.update(part)
            h.update(b"|")
        for m in self.means:
            h.update(m.tobytes())
            h.update(b"|")
        for i, x in self.ring:
            h.update(str(i).encode())
            h.update(x.tobytes())
            h.update(b"|")
        return h.digest()

    def to_dict(self) -> Dict[str, Any]:
        return {"eps": self.eps, "ring_cap": self.ring_cap, "names": list(self.names), "means": [m.copy() for m in self.means],
                "counts": list(self.counts), "dim": self.dim, "S": self.S.copy(), "nS": self.nS,
                "Lam": (None if self.Lam is None else self.Lam.copy()), "band_dist": self.band_dist,
                "band_margin": self.band_margin, "ring": [(int(i), x.copy()) for i, x in self.ring], "sleeps": self.sleeps}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StreamingLDA":
        r = cls(float(d["eps"]), int(d["ring_cap"]))
        r.names = list(d["names"])
        r.means = [np.array(m, dtype=np.float64, copy=True) for m in d["means"]]
        r.counts = [int(c) for c in d["counts"]]
        r.dim = int(d["dim"])
        r.S = np.array(d["S"], dtype=np.float64, copy=True)
        r.nS = int(d["nS"])
        r.Lam = None if d["Lam"] is None else np.array(d["Lam"], dtype=np.float64, copy=True)
        r.band_dist = None if d["band_dist"] is None else float(d["band_dist"])
        r.band_margin = None if d["band_margin"] is None else float(d["band_margin"])
        r.ring = collections.deque(((int(i), np.array(x, dtype=np.float64, copy=True)) for i, x in d["ring"]), maxlen=r.ring_cap)
        r.sleeps = int(d["sleeps"])
        return r
