"""eye.py — THE EYE GENE: a sealed eye tower, loaded from its seal and run in numpy.

edit: Claude (Fable 5.1), 2026-09-19 18:10 +0400 — G2 (docs/G2-EYE-PREREG.md §1): the forward reads the seal's LAYER LIST (`arch`, `input_side`);
a seal without one is the glyph tower's shape (conv 8@5 → max2 → conv 7@3 → mean4 at 32 px), so `eye-tower-g2` replays
byte-identical (the eye parity gate of run_g0 and pin_g1 (1) rerun). Towers are looked up in the estate's judge/ and the genome's own judge/.
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
from typing import Dict, List, Tuple

import numpy as np

DEFAULT_DIR = Path("/data/dev/alpha3/judge/eye-tower-g2")
JUDGE_DIRS = [Path("/data/dev/alpha3/judge"), Path(__file__).resolve().parent.parent / "judge"]
DEFAULT_ARCH = [{"type": "conv", "f": 8, "k": 5}, {"type": "max", "p": 2}, {"type": "conv", "f": 7, "k": 3}, {"type": "mean", "p": 4}]


def read_tower_bin(raw: bytes, names: List[str]) -> Dict[str, np.ndarray]:
    if raw[:6] != b"A3EYE1":
        raise RuntimeError("eye tower refused: wrong magic")
    at = 8; arrays = {}
    for name in names:
        (ndim,) = struct.unpack_from("<i", raw, at); at += 4
        shape = []
        for _ in range(ndim):
            (dd,) = struct.unpack_from("<i", raw, at); at += 4; shape.append(dd)
        n = int(np.prod(shape))
        arrays[name] = np.frombuffer(raw, dtype="<f4", count=n, offset=at).reshape(shape).copy(); at += 4 * n
    return arrays


class EyeTower:
    def __init__(self, d: Path = DEFAULT_DIR):
        self.dir = Path(d)
        self.seal: Dict[str, object] = json.loads((self.dir / "SEAL.json").read_text())
        raw = (self.dir / "tower.bin").read_bytes()
        self.sha = hashlib.sha256(raw).hexdigest()
        if self.sha != self.seal["tower_bin_sha256"]:
            raise RuntimeError(f"eye tower refused: tower.bin sha256 {self.sha[:16]}… is not the seal's {str(self.seal['tower_bin_sha256'])[:16]}…")
        names = list(self.seal.get("arrays") or ("W1", "b1", "W2", "b2", "Wh", "bh"))
        arrays = read_tower_bin(raw, names)
        for name in names:
            if list(arrays[name].shape) != list(self.seal["shapes"][name]):
                raise RuntimeError(f"eye tower refused: {name} shape {list(arrays[name].shape)} is not the seal's {self.seal['shapes'][name]}")
        self.arch: List[Dict[str, object]] = list(self.seal.get("arch") or DEFAULT_ARCH)
        self.side = int(self.seal.get("input_side", 32))
        self.convs: List[Tuple[np.ndarray, np.ndarray, int]] = []
        i = 0
        for layer in self.arch:
            if layer["type"] == "conv":
                i += 1; self.convs.append((arrays[f"W{i}"], arrays[f"b{i}"], int(layer["k"])))
        side = self.side; f = 1
        for layer in self.arch:
            if layer["type"] == "conv": f = int(layer["f"])
            else: side //= int(layer["p"])
        self.n_feat = f * side * side
        self.f1, self.f2 = int(self.convs[0][0].shape[0]), int(self.convs[-1][0].shape[0])

    @staticmethod
    def _conv(x: np.ndarray, W: np.ndarray, b: np.ndarray, k: int) -> np.ndarray:
        """x (H, W, C) float32 → ReLU(conv) (H, W, F); pad k//2; column order (channel, ky, kx) as the C++ organ reads it."""
        H, Wd, C = x.shape; p = k // 2
        xp = np.zeros((H + 2 * p, Wd + 2 * p, C), dtype=np.float32); xp[p:p + H, p:p + Wd, :] = x
        cols = np.empty((H * Wd, C * k * k), dtype=np.float32); i = 0
        for c in range(C):
            for ky in range(k):
                for kx in range(k):
                    cols[:, i] = xp[ky:ky + H, kx:kx + Wd, c].reshape(-1); i += 1
        a = cols @ W.T + b
        return np.maximum(a, np.float32(0.0)).reshape(H, Wd, W.shape[0])

    def features(self, frame_u8: np.ndarray) -> np.ndarray:
        """frame: side×side uint8, ink high. Returns n_feat float32 features, the tower's own arithmetic."""
        assert frame_u8.shape == (self.side, self.side) and frame_u8.dtype == np.uint8
        x = (frame_u8.astype(np.float32) / np.float32(255.0))[:, :, None]
        ci = 0
        for layer in self.arch:
            if layer["type"] == "conv":
                W, b, k = self.convs[ci]; ci += 1; x = self._conv(x, W, b, k)
            elif layer["type"] == "max":
                p = int(layer["p"]); H, Wd, C = x.shape
                x = x.reshape(H // p, p, Wd // p, p, C).max(axis=(1, 3))
            elif layer["type"] == "mean":
                p = int(layer["p"]); H, Wd, C = x.shape
                x = x.reshape(H // p, p, Wd // p, p, C).mean(axis=(1, 3))
            else:
                raise RuntimeError(f"eye tower: unknown layer {layer}")
        return x.reshape(-1).astype(np.float32)          # (py*w + px)*F + g


_CACHE: Dict[str, EyeTower] = {}


def tower(name: str = "eye-tower-g2") -> EyeTower:
    if name not in _CACHE:
        for root in JUDGE_DIRS:
            if (root / name / "SEAL.json").exists():
                _CACHE[name] = EyeTower(root / name); break
        else:
            raise RuntimeError(f"eye tower {name!r} not found under {[str(r) for r in JUDGE_DIRS]}")
    return _CACHE[name]
