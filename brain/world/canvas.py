"""canvas.py — THE GLYPH -> CANVAS ROAD (B1-PREREG.md §2.4), the SAME road for stage −1, every arm, every
twin.

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:3x +0400 — B1-PREREG.md §9 row 1, step 2 (the world).

Two pieces, kept SEPARATE on purpose (§2.4 draws the same line): `glyph_box` turns a library crop into a
THING_SIDE x THING_SIDE grey box — no randomness at all, since a glyph is a fixed library asset, never
jittered — and `paste_on_canvas` is `genome.world.render_canvas`'s OWN BODY, every line after its
`pic = render(thing, rng, THING_SIDE)` call KEPT IN ORDER, with `pic` supplied from outside instead. The
module's own parity test proves the second piece is byte-identical to `render_canvas`'s tail by running two
identically-seeded generators — one through `render()` then `paste_on_canvas()`, the other straight through
`render_canvas()` — and comparing the two (rgb, truth) results.

CANVAS/THING_SIDE/GRID/CLUTTER_STROKES/CLUTTER_INK are IMPORTED from `genome.world`, never re-typed (§2.4).
"""
from __future__ import annotations

import math
from typing import Dict, Tuple

import numpy as np
from PIL import Image, ImageDraw

from genome.world import CANVAS, CLUTTER_INK, CLUTTER_STROKES, GRID, THING_SIDE

from .glyphs import GlyphLibrary


class CanvasError(Exception):
    pass


def glyph_box(lib: GlyphLibrary, char: str, font: str) -> np.ndarray:
    """The library's (char, font) crop scaled to exactly THING_SIDE x THING_SIDE (§2.4): one factor per
    (font, size) `s = THING_SIDE / h_line`, width scaled by the SAME s, resampled by PIL's BOX filter (as
    `render` does), centred HORIZONTALLY in a THING_SIDE x THING_SIDE box — vertically the scaled crop
    already fills the whole box exactly (h_line * s == THING_SIDE, since every character of one font shares
    h_line, `glyphs.py`'s own invariant), so "vertical = the line box" means top=0, no vertical centring."""
    h_line = lib.line_box_height(font)
    crop = lib.get(char, font)   # shape (h_line, w), float64 in [0, 1], ink 1.0 on ground 0.0
    h, w = crop.shape
    if h != h_line:
        raise CanvasError(f"{lib.script}/{font}/{char}: crop height {h} != this font's line-box height {h_line}")
    s = THING_SIDE / h_line
    new_w = int(round(w * s))
    new_w = max(1, min(new_w, THING_SIDE))   # §2.1: no base-32 crop is wider than tall, so w*s <= h_line*s == THING_SIDE
    img = Image.fromarray(np.clip(np.rint(crop * 255.0), 0, 255).astype(np.uint8), mode="L")
    scaled = img.resize((new_w, THING_SIDE), Image.BOX)
    arr = np.asarray(scaled, dtype=np.float64) / 255.0
    box = np.zeros((THING_SIDE, THING_SIDE), dtype=np.float64)
    left = (THING_SIDE - new_w) // 2
    box[:, left:left + new_w] = arr
    return box


def paste_on_canvas(pic: np.ndarray, rng: np.random.Generator) -> Tuple[np.ndarray, Dict[str, object]]:
    """`genome.world.render_canvas`'s own body, every line kept in order, starting from where that function
    calls `render(thing, rng, THING_SIDE)` — `pic` takes that call's place (§2.4). Parity with the real
    `render_canvas` is `tests/brain/harness/test_canvas.py`'s own job (20 things x 5 seeds, per §2.4)."""
    if pic.shape != (THING_SIDE, THING_SIDE):
        raise CanvasError(f"pic must be {(THING_SIDE, THING_SIDE)}, got {pic.shape}")
    ty, tx = (int(v) for v in rng.integers(0, CANVAS - THING_SIDE + 1, size=2))
    cv = np.zeros((CANVAS, CANVAS), dtype=np.float64)
    cv[ty:ty + THING_SIDE, tx:tx + THING_SIDE] = pic
    layer = Image.new("L", (CANVAS, CANVAS), 0)
    d = ImageDraw.Draw(layer)
    for _ in range(CLUTTER_STROKES):
        x0, y0 = rng.uniform(0, CANVAS, size=2)
        ang = rng.uniform(0, math.pi)
        L = rng.uniform(8, 16)
        d.line([(x0, y0), (x0 + L * math.cos(ang), y0 + L * math.sin(ang))], fill=255, width=1)
    cl = np.asarray(layer, dtype=np.float64) / 255.0 * CLUTTER_INK
    cv = np.maximum(cv, cl)
    cv = np.clip(cv + rng.normal(0.0, 0.05, size=cv.shape), 0.0, 1.0)
    tot = pic.sum()
    ys, xs = np.mgrid[0:THING_SIDE, 0:THING_SIDE]
    cy = ty + ((ys * pic).sum() / tot if tot > 0 else THING_SIDE / 2)
    cx = tx + ((xs * pic).sum() / tot if tot > 0 else THING_SIDE / 2)
    cell = (int(cy // (CANVAS / GRID)), int(cx // (CANVAS / GRID)))
    u8 = np.clip(np.rint(cv * 255.0), 0, 255).astype(np.uint8)
    rgb = np.repeat(u8[:, :, None], 3, axis=2)
    return rgb, {"top": ty, "left": tx, "centroid": (float(cy), float(cx)), "cell": cell}


def render_glyph_canvas(lib: GlyphLibrary, char: str, font: str, rng: np.random.Generator) -> Tuple[np.ndarray, Dict[str, object]]:
    """The whole road: a library crop -> a THING_SIDE box -> a pasted CANVAS x CANVAS rgb canvas + truth."""
    pic = glyph_box(lib, char, font)
    return paste_on_canvas(pic, rng)
