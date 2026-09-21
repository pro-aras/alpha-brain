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

from .machinery import GenomeError, retina, _unit

A2 = Path("/data/dev/alpha2")
PINS = {
    "organs/retina.py": "aa95693dcd29f1f5d9432160ac7f5a520db9cbec5719f73112b7b6337fa81dc4",
    "organs/gaze.py": "2ccea9b449efd4452cb3c4fc0a5d4d439e456b18bc365595f3c90c6fe230ae73",
}
# edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:20 +0400 — G-EYE task 3, the THIRD pin (F's report §3
# named this the orchestrator's decision; taken here). genome/retina_fast.py is proven byte-identical to
# organs/retina.py's own analyse() on every canvas of life 2's tape (G5-F-REPORT.md §3) and on life 3a's
# (this branch's own test, tests/genome/test_retina_fast_life3a.py) — a numpy-vectorised drop-in for the
# 4.77 ms/canvas pure-Python pixel loop. This digest is of THIS repo's own genome/retina_fast.py file (git-
# tracked, unlike the external alpha2/ oracle) — it differs from F's reported 452602160658d8253c4779… because
# this copy carries this branch's own edit-attribution header line (content otherwise untouched, byte-for-
# byte); recomputed here, never typed from memory.
_RETINA_FAST_PIN = "90305a986e6b489cacdbe652392ed8557317a8d38de9b68ad4c1aa0a26e9008d"
_ORGANS: Optional[Tuple[object, object]] = None
_analyse = None   # type: ignore[assignment]   # set by organs(): either the oracle's analyse or retina_fast's analyse_fast


def organs():
    """(gaze, retina) — Alpha 2's organs, sha-pinned. GenomeError if a byte differs. As a side effect, also
    verifies and adopts genome/retina_fast.py's vectorised analyse (the third pin, above) — silent, additive:
    every caller of _analyse_frame() below gets the same numbers either way (proven byte-identical)."""
    global _ORGANS, _analyse
    if _ORGANS is None:
        for rel, sha in PINS.items():
            h = hashlib.sha256((A2 / rel).read_bytes()).hexdigest()
            if h != sha:
                raise GenomeError(f"GAZE gene refused: {rel} sha256 {h[:16]}… is not the pinned {sha[:16]}…")
        if str(A2) not in sys.path:
            sys.path.insert(0, str(A2))
        from organs import gaze as _g, retina as _r    # noqa: E402
        _ORGANS = (_g, _r)
        here = Path(__file__).resolve().parent / "retina_fast.py"
        h = hashlib.sha256(here.read_bytes()).hexdigest()
        if h != _RETINA_FAST_PIN:
            raise GenomeError(f"GAZE gene refused: genome/retina_fast.py sha256 {h[:16]}… is not the pinned {_RETINA_FAST_PIN[:16]}…")
        from . import retina_fast as _rf   # noqa: E402  (its own oracle() call re-verifies organs/retina.py's pin independently)
        _analyse = _rf.analyse_fast
    return _ORGANS


def _analyse_frame(rgb: np.ndarray) -> dict:
    """The one per-canvas retina call every fixation/colour road below shares — retina_fast's vectorised
    cell_means_fast + the oracle's own unmodified channels()/saliency() (organs(), above), proven byte-
    identical to the oracle's own analyse() (G5-F-REPORT.md §3; this branch's life-3a test)."""
    organs()
    return _analyse(frame_of(rgb))


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
    g, _r = organs()
    an = _analyse_frame(rgb)
    rows = g.gaze_sequence(an, max_fixations=F, predicted=None) if mode == "surprise" else g.random_gaze(an, seed=pic_id, max_fixations=F)
    return [(int(z["y"]), int(z["x"])) for z in rows]


def saliency_of(rgb: np.ndarray) -> np.ndarray:
    return np.asarray(_analyse_frame(rgb)["saliency"], dtype=np.float64)


def colour_block(an: Dict[str, object], top: int, left: int) -> np.ndarray:
    """G-EYE-3/§3.6, Researcher G's measured form (game-worlds/code/bands.py:colour_block, reused here so
    the LIVE creature's own gaze door computes the identical 32 numbers, not a copy of the formula): the
    FIXED rg/by channels the retina already computes (an["channels"]), read over the 4x4 cells of the
    16x16 grid the glance window covers (the window is `glance` px wide on a `canvas`-px canvas; each
    grid cell is canvas/16 px — 8 px on the G4 canvas=128/glance=32 pair, so 32/8=4 cells per side, exactly
    "4x4"), one 4x4 block each for rg and by, flattened and /255 (raw R-G / B-(R+G)/2 values run roughly
    -255..255). FIXED GAIN (#231(1)): the 112-tower block is unit-normalised by its own RETINA `unit` step
    before this is concatenated (see glances(), below) — this block itself is left RAW, never separately
    unit-normalised, so a window with no colour contributes a true zero instead of amplified noise."""
    ch = an["channels"]
    r0, c0 = top // 8, left // 8
    out = []
    for key in ("rg", "by"):
        m = np.asarray(ch[key], dtype=np.float64)
        out.append(m[r0:r0 + 4, c0:c0 + 4].reshape(-1) / 255.0)
    return np.concatenate(out)


def glance_window(grey: np.ndarray, cell: Tuple[int, int], grid: int, glance: int) -> Tuple[np.ndarray, Tuple[int, int]]:
    """The glance×glance window centred on the cell's centre, clamped inside the canvas. Returns (window, (top, left))."""
    h, w = grey.shape
    cy, cx = (cell[0] + 0.5) * (h / grid), (cell[1] + 0.5) * (w / grid)
    top = int(min(max(round(cy - glance / 2), 0), h - glance)); left = int(min(max(round(cx - glance / 2), 0), w - glance))
    return grey[top:top + glance, left:left + glance], (top, left)


def glances(rgb: np.ndarray, spec: Sequence[str], gaze: Dict[str, object], mode: str = "surprise", pic_id: str = "",
            colour: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """One picture → its glance features. mode: surprise (the gene) | random (T-random-gaze) | one (T-one-glance: the whole
    canvas at glance×glance, one feature vector). Returns {"feats": [...], "fix": [(y, x), ...], "windows": [(top, left), ...]}.

    `colour` (G-EYE-3/§3.6, new — Genome.colour, None unless SENSE colour is declared): when not None, each
    feature vector is RETINA's own unit-length tower block concatenated with colour_block()'s 32 RAW (never
    separately unit-normalised) numbers, THEN the WHOLE 144-vector is unit-normalised once more — Researcher
    G's exact measured "fixed-gain" form (game-worlds/code/bands.py: `_unit(np.concatenate([_unit(v),
    colour_block(...)]))`, colour="raw" branch), reused here rather than re-derived so the LIVE gaze door
    computes the identical numbers. The outer unit-step is what makes the block INERT on a colourless window
    (concatenating a unit vector with a true zero and re-normalising returns the same unit vector exactly —
    the maker's world's own guarantee, asserted in tests) and FIXED-GAIN on a coloured one: a window with
    more colour drives the colour block's raw norm up, and the shared outer normalisation shrinks the tower
    block's share by exactly the same factor — colour contributes IN PROPORTION TO HOW COLOURED THE WINDOW
    IS, never independently rescaled to the tower's own unit length (that alternative, "block-unit", is
    G's OTHER measured form and amplifies a legitimately-zero block's own floating-point noise to norm 1,
    #231(1) — SENSE colour's grammar above accepts only "fixed-gain", on purpose).
    Undeclared (colour=None, every existing caller): byte-identical to before this gene existed — the SAME
    single `_analyse_frame` call this function always made (via `fixations()`), no new call, no new branch."""
    F, grid, glance = int(gaze["fixations"]), int(gaze["grid"]), int(gaze["glance"])
    ink_rule = INK_RULES[str(gaze.get("ink", "contrast"))]
    grey = luminance(rgb)
    if mode == "one":
        if colour is not None:
            raise GenomeError("SENSE colour: gaze mode 'one' (T-one-glance) has no per-glance window to read the colour cells from — not implemented, refuse loudly rather than guess")
        small = np.asarray(Image.fromarray(rgb).convert("L").resize((glance, glance), Image.BOX), dtype=np.float64) / 255.0
        return {"feats": [retina(ink_rule(small), tuple(spec))], "fix": [], "windows": []}
    g, _r = organs()
    an = _analyse_frame(rgb)
    rows = g.gaze_sequence(an, max_fixations=F, predicted=None) if mode == "surprise" else g.random_gaze(an, seed=pic_id, max_fixations=F)
    fix = [(int(z["y"]), int(z["x"])) for z in rows]
    feats, wins = [], []
    for cell in fix:
        win, tl = glance_window(grey, cell, grid, glance)
        v = retina(ink_rule(win), tuple(spec))
        if colour is not None:
            v = _unit(np.concatenate([v, colour_block(an, tl[0], tl[1])]))
        feats.append(v); wins.append(tl)
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
