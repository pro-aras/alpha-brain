# edit: Claude (Sonnet 5, builder F), 2026-09-21 16:53 +0400 -- G5-F task 3 (docs/briefs/G5-F-BIND-DIAGNOSTIC-AND-REPAIRS.md
# item 3; EYE.md §0.3 row 2 / gap 9): a numpy-vectorised drop-in for organs/retina.py's `cell_means` --
# the pure-Python loop over every pixel that is 4.77 ms of the retina's 5.42 ms (88%, EYE.md §0.3).
# `channels()`/`saliency()`/`classes_at()` are REUSED UNCHANGED from the pinned oracle (imported, never
# copied, never re-derived) -- only the one-pass-over-pixels step changes. Never edits
# `/data/dev/alpha2/organs/retina.py` itself: its own header says it is "the ORACLE for the later C++
# port" (P12 law) and genome/gaze.py's sha-pin refuses the organism's start if a byte of it differs.
# This is an ADDITIVE new module with its OWN pin (below); genome/gaze.py is untouched and still calls
# the original oracle in production -- adopting this module (rewiring gaze.py's `organs()` to use it) is
# the orchestrator's decision, not made here. Proven byte-identical against the oracle on life 2's full
# tape (every canvas): docs/briefs/G5-F-REPORT.md.
"""genome/retina_fast.py -- `cell_means_fast` + `analyse_fast`: integer-exact numpy replacements for
organs/retina.py's per-pixel pass. Every pixel's contribution is an exact integer (0-255) and every
partial sum stays well inside float64's 53-bit exact-integer range (grid 16 on a <=4096-px-per-cell
frame: max sum 4096*255 = 1,044,480), so summing in a different order (numpy's bincount scan vs the
oracle's nested Python loop) cannot change the result -- floating-point addition of exactly-representable
integers whose running sum also stays exactly representable is exact regardless of order. The final
division (sum/count) is the same IEEE754 double division either way. This is the argument FOR byte
identity; docs/briefs/G5-F-REPORT.md is the measurement that checks it, never assumes it.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

A2 = Path("/data/dev/alpha2")
# Same pin as genome/gaze.py's PINS["organs/retina.py"] -- this module reuses that file's channels()/
# saliency() verbatim and must refuse exactly when gaze.py's own pin would refuse.
RETINA_PIN = "aa95693dcd29f1f5d9432160ac7f5a520db9cbec5719f73112b7b6337fa81dc4"

_ORACLE = None


def oracle():
    """The pinned organs/retina.py module -- sha-refused if a byte differs, exactly like genome/gaze.py's
    organs(). Kept independent of gaze.py so this module has no import-order dependency on it."""
    global _ORACLE
    if _ORACLE is None:
        path = A2 / "organs" / "retina.py"
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        if h != RETINA_PIN:
            raise RuntimeError(f"retina_fast refused: {path} sha256 {h[:16]}… is not the pinned {RETINA_PIN[:16]}…")
        if str(A2) not in sys.path:
            sys.path.insert(0, str(A2))
        from organs import retina as _r   # noqa: E402
        _ORACLE = _r
    return _ORACLE


def cell_means_fast(frame: Dict[str, object], grid: Optional[int] = None) -> List[List[Tuple[float, float, float]]]:
    """Byte-for-byte-argued replacement for organs/retina.py:cell_means -- same per-cell mean R,G,B over
    the same non-uniform grid partition (cy = min(grid-1, y*grid//h), same for x), computed with numpy
    integer accumulation instead of a Python loop over every pixel. Returns the identical nested
    list-of-tuples shape channels() consumes."""
    r = oracle()
    grid = int(grid) if grid is not None else r.GRID
    w, h, pix = int(frame["w"]), int(frame["h"]), frame["pix"]
    arr = np.frombuffer(pix, dtype=np.uint8).reshape(h, w, 3)
    cy = np.minimum(grid - 1, (np.arange(h, dtype=np.int64) * grid) // h)
    cx = np.minimum(grid - 1, (np.arange(w, dtype=np.int64) * grid) // w)
    idx = (cy[:, None] * grid + cx[None, :]).ravel()               # (h*w,) cell index per pixel, row-major (same y,x order as the oracle's loop)
    counts = np.bincount(idx, minlength=grid * grid).astype(np.float64)
    sums = np.empty((grid * grid, 3), dtype=np.float64)
    for c in range(3):
        sums[:, c] = np.bincount(idx, weights=arr[:, :, c].ravel().astype(np.float64), minlength=grid * grid)
    with np.errstate(invalid="ignore", divide="ignore"):
        means = np.where(counts[:, None] > 0, sums / counts[:, None], 0.0)
    means = means.reshape(grid, grid, 3)
    return [[(float(means[y, x, 0]), float(means[y, x, 1]), float(means[y, x, 2])) for x in range(grid)] for y in range(grid)]


def analyse_fast(frame: Dict[str, object], grid: Optional[int] = None) -> dict:
    """Drop-in for organs/retina.py:analyse: cell_means_fast, then the ORACLE's own (unmodified)
    channels()/saliency() -- so any divergence can only come from cell_means_fast, never from a
    re-derivation of the downstream math."""
    r = oracle()
    grid = int(grid) if grid is not None else r.GRID
    cells = cell_means_fast(frame, grid)
    ch = r.channels(cells)
    return {"grid": grid, "w": frame["w"], "h": frame["h"], "channels": ch, "saliency": r.saliency(ch)}


__all__ = ["oracle", "cell_means_fast", "analyse_fast", "RETINA_PIN"]
