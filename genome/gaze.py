"""gaze.py — THE GAZE GENE: Alpha 2's V0.1 retina + gaze organs, imported VERBATIM (docs/G1-PREREG.md §1).

edit: Claude (Fable 5.1), 2026-09-19 17:35 +0400 — §6 amendment 1: the `border` INK rule (background from the window's rim); `contrast` kept as the first run's record.
edit: Claude (Fable 5.1), 2026-09-19 17:21 +0400 — G1 rung 1, on Ahmad's 17:10 «Ok go for it» (D-G4 road (a)).

Nothing of the saliency or the fixation rule is written here: `organs/retina.py` and `organs/gaze.py`
are imported from /data/dev/alpha2 and refused if their sha256 is not the pinned one. This file only
(a) turns a canvas into the organ's frame dict (the bytes its own PPM reader would produce),
(b) cuts a 32×32 glance window around each fixated cell, (c) applies the declared INK rule, and
(d) hands the window to the genome's RETINA steps (machinery.retina — the G0b eye, unchanged).
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

from .machinery import GenomeError, retina

A2 = Path("/data/dev/alpha2")
PINS = {
    "organs/retina.py": "aa95693dcd29f1f5d9432160ac7f5a520db9cbec5719f73112b7b6337fa81dc4",
    "organs/gaze.py": "2ccea9b449efd4452cb3c4fc0a5d4d439e456b18bc365595f3c90c6fe230ae73",
}
_ORGANS: Optional[Tuple[object, object]] = None


def organs():
    """(gaze, retina) — Alpha 2's organs, sha-pinned. GenomeError if a byte differs."""
    global _ORGANS
    if _ORGANS is None:
        for rel, sha in PINS.items():
            h = hashlib.sha256((A2 / rel).read_bytes()).hexdigest()
            if h != sha:
                raise GenomeError(f"GAZE gene refused: {rel} sha256 {h[:16]}… is not the pinned {sha[:16]}…")
        if str(A2) not in sys.path:
            sys.path.insert(0, str(A2))
        from organs import gaze as _g, retina as _r    # noqa: E402
        _ORGANS = (_g, _r)
    return _ORGANS


def frame_of(rgb: np.ndarray) -> Dict[str, object]:
    """The organ's frame dict from an (h, w, 3) uint8 canvas — exactly what its read_ppm returns for the P6 file of it."""
    assert rgb.dtype == np.uint8 and rgb.ndim == 3 and rgb.shape[2] == 3
    return {"w": int(rgb.shape[1]), "h": int(rgb.shape[0]), "pix": np.ascontiguousarray(rgb).tobytes()}


def ppm_bytes(rgb: np.ndarray) -> bytes:
    return b"P6\n%d %d\n255\n" % (rgb.shape[1], rgb.shape[0]) + np.ascontiguousarray(rgb).tobytes()


def luminance(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.float64) for i in range(3))
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def ink_contrast(grey: np.ndarray) -> np.ndarray:
    """INK contrast (G1 §1): |g − mean(g)| / max — ink wherever the window departs from its own mean; a flat window is all zero."""
    d = np.abs(grey - grey.mean())
    m = d.max()
    return d / m if m > 0 else np.zeros_like(d)


def ink_border(grey: np.ndarray, rim: int = 2) -> np.ndarray:
    """INK border (G1 §6, amendment 1): |g − median of the window's 2-px BORDER| / max — the background read from the rim, so a
    filled shape keeps its interior and a dark thing on a bright ground still becomes ink; a flat window is all zero."""
    b = np.concatenate([grey[:rim].ravel(), grey[-rim:].ravel(), grey[:, :rim].ravel(), grey[:, -rim:].ravel()])
    d = np.abs(grey - np.median(b))
    m = d.max()
    return d / m if m > 0 else np.zeros_like(d)


INK_RULES = {"contrast": ink_contrast, "border": ink_border}


def fixations(rgb: np.ndarray, F: int, mode: str = "surprise", pic_id: str = "") -> List[Tuple[int, int]]:
    """The organ's fixations over one canvas: (y, x) cells on its 16×16 grid. mode: surprise (the gene) | random (V0.1's twin)."""
    g, r = organs()
    an = r.analyse(frame_of(rgb))
    rows = g.gaze_sequence(an, max_fixations=F, predicted=None) if mode == "surprise" else g.random_gaze(an, seed=pic_id, max_fixations=F)
    return [(int(z["y"]), int(z["x"])) for z in rows]


def saliency_of(rgb: np.ndarray) -> np.ndarray:
    _g, r = organs()
    return np.asarray(r.analyse(frame_of(rgb))["saliency"], dtype=np.float64)


def glance_window(grey: np.ndarray, cell: Tuple[int, int], grid: int, glance: int) -> Tuple[np.ndarray, Tuple[int, int]]:
    """The glance×glance window centred on the cell's centre, clamped inside the canvas. Returns (window, (top, left))."""
    h, w = grey.shape
    cy, cx = (cell[0] + 0.5) * (h / grid), (cell[1] + 0.5) * (w / grid)
    top = int(min(max(round(cy - glance / 2), 0), h - glance)); left = int(min(max(round(cx - glance / 2), 0), w - glance))
    return grey[top:top + glance, left:left + glance], (top, left)


def glances(rgb: np.ndarray, spec: Sequence[str], gaze: Dict[str, object], mode: str = "surprise", pic_id: str = "") -> Dict[str, object]:
    """One picture → its glance features. mode: surprise (the gene) | random (T-random-gaze) | one (T-one-glance: the whole
    canvas at glance×glance, one feature vector). Returns {"feats": [...], "fix": [(y, x), ...], "windows": [(top, left), ...]}."""
    F, grid, glance = int(gaze["fixations"]), int(gaze["grid"]), int(gaze["glance"])
    ink_rule = INK_RULES[str(gaze.get("ink", "contrast"))]
    grey = luminance(rgb)
    if mode == "one":
        small = np.asarray(Image.fromarray(rgb).convert("L").resize((glance, glance), Image.BOX), dtype=np.float64) / 255.0
        return {"feats": [retina(ink_rule(small), tuple(spec))], "fix": [], "windows": []}
    fix = fixations(rgb, F, mode, pic_id)
    feats, wins = [], []
    for cell in fix:
        win, tl = glance_window(grey, cell, grid, glance)
        feats.append(retina(ink_rule(win), tuple(spec))); wins.append(tl)
    return {"feats": feats, "fix": fix, "windows": wins}


def canvas_of_picture(path: Path, canvas: int = 128) -> np.ndarray:
    """His picture → an RGB canvas: longest side to `canvas` (BOX), padded to canvas×canvas with the picture's own mean colour."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    k = canvas / max(w, h)
    nw, nh = max(1, round(w * k)), max(1, round(h * k))
    small = im.resize((nw, nh), Image.BOX)
    arr = np.asarray(small, dtype=np.uint8)
    mean = tuple(int(round(v)) for v in arr.reshape(-1, 3).mean(axis=0))
    out = np.empty((canvas, canvas, 3), dtype=np.uint8); out[...] = np.array(mean, dtype=np.uint8)
    top, left = (canvas - nh) // 2, (canvas - nw) // 2
    out[top:top + nh, left:left + nw] = arr
    return out
