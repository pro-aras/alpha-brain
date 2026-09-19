"""eye.py — THE EYE GENE: Alpha 3's sealed eye tower, loaded from its seal and run in numpy.

edit: Claude (Fable 5.1), 2026-09-19 16:4x +04 — G0b (docs/G0b-PREREG.md, gene EYE), on Ahmad's 16:27
«You didn't put all the advancements from all the builds we had. Why?» and his 16:33 «Ok go».

Source build: E09d's tower (seed 20260913), grown by E46d arm (b) into one shape-blind trunk
over 108 merged shape-classes and ADOPTED 2026-09-16 17:3x as `/data/dev/alpha3/judge/eye-tower-g2`
(NOTES 09-16 17:3x). Proof carried: the C++ organ `src/eye_tower.cpp` replays E09d's 2,356 held-out
frames byte for byte (argmax on every one, logits to 1e-3). This file is that organ's FEATURES
road, written in numpy from the same arithmetic:
    x = u8/255 → conv F1 @ 5x5 (pad 2) → ReLU → 2x2 max-pool → conv F2 @ 3x3 (pad 1) → ReLU
    → 4x4 mean pool → (4, 4, F2) flattened as index (py*4 + px)*F2 + g → F2*16 features.
The HEAD (Wh, bh) is deliberately NOT used: the organism grows its own words over the features.
Nothing here is trained, tuned or re-derived; load() refuses a tower.bin whose sha-256 is not the seal's.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

DEFAULT_DIR = Path("/data/dev/alpha3/judge/eye-tower-g2")
KIN, K1, K2, POOL = 32, 5, 3, 4


class EyeTower:
    def __init__(self, d: Path = DEFAULT_DIR):
        self.dir = Path(d)
        self.seal: Dict[str, object] = json.loads((self.dir / "SEAL.json").read_text())
        raw = (self.dir / "tower.bin").read_bytes()
        self.sha = hashlib.sha256(raw).hexdigest()
        if self.sha != self.seal["tower_bin_sha256"]:
            raise RuntimeError(f"eye tower refused: tower.bin sha256 {self.sha[:16]}… is not the seal's {str(self.seal['tower_bin_sha256'])[:16]}…")
        if raw[:6] != b"A3EYE1":
            raise RuntimeError("eye tower refused: wrong magic")
        at = 8                                  # 6-byte magic + 2 bytes, as the C++ loader reads it
        arrays = {}
        for name in ("W1", "b1", "W2", "b2", "Wh", "bh"):
            (ndim,) = struct.unpack_from("<i", raw, at); at += 4
            shape = []
            for _ in range(ndim):
                (dd,) = struct.unpack_from("<i", raw, at); at += 4; shape.append(dd)
            n = int(np.prod(shape))
            arrays[name] = np.frombuffer(raw, dtype="<f4", count=n, offset=at).reshape(shape).copy(); at += 4 * n
            if list(shape) != list(self.seal["shapes"][name]):
                raise RuntimeError(f"eye tower refused: {name} shape {shape} is not the seal's {self.seal['shapes'][name]}")
        self.W1 = arrays["W1"]; self.b1 = arrays["b1"]; self.W2 = arrays["W2"]; self.b2 = arrays["b2"]
        self.f1, self.f2 = int(self.W1.shape[0]), int(self.W2.shape[0])
        self.n_feat = self.f2 * (KIN // 2 // POOL) ** 2

    def features(self, frame_u8: np.ndarray) -> np.ndarray:
        """frame: 32×32 uint8, ink high. Returns n_feat float32 features, the tower's own arithmetic."""
        assert frame_u8.shape == (KIN, KIN) and frame_u8.dtype == np.uint8
        x = frame_u8.astype(np.float32) / np.float32(255.0)
        xp = np.zeros((KIN + 4, KIN + 4), dtype=np.float32); xp[2:-2, 2:-2] = x
        # conv1: F1 @ 5x5, pad 2, via im2col in the C++ order (ky, kx)
        cols = np.empty((KIN * KIN, K1 * K1), dtype=np.float32)
        i = 0
        for ky in range(K1):
            for kx in range(K1):
                cols[:, i] = xp[ky:ky + KIN, kx:kx + KIN].reshape(-1); i += 1
        a1 = cols @ self.W1.T + self.b1                       # (1024, F1)
        a1 = np.maximum(a1, np.float32(0.0)).reshape(KIN, KIN, self.f1)
        # 2x2 max-pool -> (16, 16, F1)
        h2 = KIN // 2
        p = a1.reshape(h2, 2, h2, 2, self.f1).max(axis=(1, 3))
        pp = np.zeros((h2 + 2, h2 + 2, self.f1), dtype=np.float32); pp[1:-1, 1:-1, :] = p
        # conv2: F2 @ 3x3 over F1 channels, pad 1; column order (channel, ky, kx) as the C++ reads W2
        cols2 = np.empty((h2 * h2, self.f1 * K2 * K2), dtype=np.float32)
        i = 0
        for c in range(self.f1):
            for ky in range(K2):
                for kx in range(K2):
                    cols2[:, i] = pp[ky:ky + h2, kx:kx + h2, c].reshape(-1); i += 1
        a2 = cols2 @ self.W2.T + self.b2                      # (256, F2)
        a2 = np.maximum(a2, np.float32(0.0)).reshape(h2, h2, self.f2)
        # 4x4 mean pool -> (4, 4, F2), flattened as (py*4 + px)*F2 + g
        h3 = h2 // POOL
        out = a2.reshape(h3, POOL, h3, POOL, self.f2).mean(axis=(1, 3)).reshape(-1)
        return out.astype(np.float32)


_CACHE: Dict[str, EyeTower] = {}


def tower(name: str = "eye-tower-g2") -> EyeTower:
    if name not in _CACHE:
        _CACHE[name] = EyeTower(DEFAULT_DIR.parent / name)
    return _CACHE[name]
