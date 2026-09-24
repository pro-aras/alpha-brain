"""glyphs.py — READING THE LIBRARY'S BASE-32 GLYPHS (B1-PREREG.md §2.1).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:3x +0400 — B1-PREREG.md §9 row 1, step 2 (the world).

Reads `/data/alpha3-library/K/glyphs/<script>/{glyphs.bin,glyphs.idx}` (read-only — the library is never
written by B1). §2.1: "B1 uses the BASE variant at size 32 (rot 0, blur 0, noise 0) only." Independently
checked on this box, 2026-09-24 (before this module existed): every one of the 60 kept fonts in each of
latin-upper/latin-lower/digits shares exactly ONE line-box height across all its base-32 characters (0 fonts
with >1 distinct h), and 0 base-32 crops are wider than tall — the two invariants §2.1 states.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from .fonts import GLYPH_ROOT, SCRIPTS

# §3.3's never-taught candidate scripts (Hebrew, Arabic, Devanagari, Greek — Cyrillic is OUT, the tower
# trained on it). Independently checked on this box, 2026-09-24: base-32 font counts 20/12/4/60 (matches
# §3.3's own "Hebrew 20, Arabic 12, Greek ≈ 60, Devanagari 4" exactly), and both of §2.1's invariants
# (one line-box height per font, never wider than tall) hold here too — 0 violations in all four.
NEVER_TAUGHT_SCRIPTS: tuple = ("hebrew", "arabic", "devanagari", "greek")


class GlyphsError(Exception):
    pass


_BASE_VARIANT = {"size": "32", "rot": "0.0", "blur": "0.0", "noise": "0.00"}


class GlyphLibrary:
    """One script's base-32 glyphs, indexed by (char, font). `render_glyphs.py`'s own idx columns:
    offset bytes w h label script font_id font size rot blur noise split — read here verbatim, never
    re-derived."""

    def __init__(self, script: str):
        if script not in SCRIPTS and script not in NEVER_TAUGHT_SCRIPTS:
            raise GlyphsError(f"unknown script {script!r} (must be one of {SCRIPTS + NEVER_TAUGHT_SCRIPTS})")
        self.script = script
        self.root = GLYPH_ROOT / script
        idx_path = self.root / "glyphs.idx"
        if not idx_path.exists():
            raise GlyphsError(f"missing {idx_path}")
        with idx_path.open(newline="", encoding="utf-8") as f:
            all_rows = list(csv.DictReader(f, delimiter="\t"))
        self._by_key: Dict[Tuple[str, str], Dict[str, str]] = {}
        self._heights: Dict[str, int] = {}
        for r in all_rows:
            if not all(r[k] == v for k, v in _BASE_VARIANT.items()):
                continue
            key = (r["label"], r["font"])
            if key in self._by_key:
                raise GlyphsError(f"{script}: duplicate base-32 row for {key}")
            self._by_key[key] = r
            h = int(r["h"])
            prev = self._heights.get(r["font"])
            if prev is not None and prev != h:
                raise GlyphsError(f"{script}/{r['font']}: base-32 line-box height varies ({prev} vs {h}) "
                                   f"— §2.1's own invariant is violated; RAISE to the seat")
            self._heights[r["font"]] = h
            if int(r["w"]) > h:
                raise GlyphsError(f"{script}/{r['font']}/{r['label']}: base-32 crop is wider ({r['w']}) than tall ({h})")
        self._bin_path = self.root / "glyphs.bin"
        if not self._bin_path.exists():
            raise GlyphsError(f"missing {self._bin_path}")

    def has(self, char: str, font: str) -> bool:
        return (char, font) in self._by_key

    def line_box_height(self, font: str) -> int:
        """h_line for `font` at size 32 (§2.4: "h_line = the crop's line-box height, asserted common to the
        font at that size") — constant across every character of this script rendered in this font."""
        if font not in self._heights:
            raise GlyphsError(f"{self.script}: no base-32 rows at all for font {font!r}")
        return self._heights[font]

    def get(self, char: str, font: str) -> np.ndarray:
        """The raw grey crop for (char, font) as float64 in [0, 1] — ink white(255) on black(0), the SAME
        convention `genome.world.render` returns (§2.1's own docstring citation)."""
        r = self._by_key.get((char, font))
        if r is None:
            raise GlyphsError(f"{self.script}: no base-32 row for (char={char!r}, font={font!r})")
        offset, nbytes, w, h = int(r["offset"]), int(r["bytes"]), int(r["w"]), int(r["h"])
        if nbytes != w * h:
            raise GlyphsError(f"{self.script}/{font}/{char}: bytes={nbytes} != w*h={w * h}")
        with self._bin_path.open("rb") as f:
            f.seek(offset)
            data = f.read(nbytes)
        if len(data) != nbytes:
            raise GlyphsError(f"{self.script}/{font}/{char}: short read ({len(data)} of {nbytes} bytes at offset {offset})")
        arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w).astype(np.float64) / 255.0
        return arr

    def fonts_available_for(self, char: str) -> List[str]:
        return sorted(font for (c, font) in self._by_key if c == char)
