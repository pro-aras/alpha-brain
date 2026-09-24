"""build.py — RENDER + GLANCE: THE ONE PATH FROM A LIBRARY ASSET TO A CACHE ROW (B1-PREREG.md §2.4-§2.5).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:2x +0400 — B1-PREREG.md §9 row 1, step 3 (the cache).

Runs ONLY under `/usr/bin/python3` (§3.0). This is the SHARED renderer both stage −1 (which needs TEACH/
TEST naming renderings, the perceptual families and the never-taught candidate pool — see
`brain/harness/stage_minus1.py`) and the full training tape (`brain/world/tape.py`, built once stage −1's
bars are declared) render through — one path, so a byte rendered for a ceiling and the "same" item rendered
later for the tape are produced by the identical code, never two slightly-different reimplementations.

The order this module enforces (the advisor's review, before any code here was written): ENUMERATE every
rendering needed (a flat list of `RenderRequest`, each with a UNIQUE `item_id` — the §2.4 rng purpose key)
BEFORE any cache exists, THEN render+glance+write each one ONCE. Nothing here decides WHICH renderings are
needed (that is each caller's own job — stage −1's oracle construction, or the tape's schedule); this module
only turns a request into a cache row, and self-checks the result (§2.5's own test: 10 rows chosen by the
seed are re-glanced and compared byte for byte to the cached row).
"""
from __future__ import annotations

import hashlib
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import PIL
import scipy
from PIL import Image

from genome import gaze as genome_gaze

from brain.glance_cache import Cache, CacheWriter, FEATURES_PER_GLANCE, GLANCES_PER_ROW

from . import organs, seeds
from .canvas import render_glyph_canvas
from .glyphs import GlyphLibrary


class BuildError(Exception):
    pass


@dataclass(frozen=True)
class RenderRequest:
    item_id: str    # UNIQUE per occurrence (§2.4's rng purpose key) — never reused for two different draws
    script: str
    char: str
    font: str
    variant: str = "base-32"


def canvas_png_sha256(rgb: np.ndarray) -> str:
    """§2.4's own test names a "PNG sha" — encode, don't hash the raw buffer, so a rendering saved to disk
    later (for a human to look at) hashes to the SAME value already on record."""
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return hashlib.sha256(buf.getvalue()).hexdigest()


def render_and_glance(req: RenderRequest, lib: GlyphLibrary, seed: int, spec, gaze_cfg: Dict[str, object],
                       colour: Optional[Dict[str, object]]) -> Tuple[np.ndarray, np.ndarray, Dict[str, object], str]:
    """-> (feats shape (5,144) float64, rgb canvas uint8, truth dict, canvas_png_sha256)."""
    rng = seeds.rendering_rng(seed, req.item_id)
    rgb, truth = render_glyph_canvas(lib, req.char, req.font, rng)
    sha = canvas_png_sha256(rgb)
    out = genome_gaze.glances(rgb, spec, gaze_cfg, mode="surprise", pic_id=sha, colour=colour, predicted=None)
    feats = np.stack(out["feats"], axis=0)
    if feats.shape != (GLANCES_PER_ROW, FEATURES_PER_GLANCE):
        raise BuildError(f"{req.item_id}: genome.gaze.glances returned shape {feats.shape}, "
                          f"expected {(GLANCES_PER_ROW, FEATURES_PER_GLANCE)}")
    return feats, rgb, truth, sha


def _interpreter_versions() -> Dict[str, str]:
    return {"executable": sys.executable, "python": sys.version.split()[0],
            "numpy": np.__version__, "scipy": scipy.__version__, "PIL": PIL.__version__}


def build_cache(requests: List[RenderRequest], out_dir: Path, seed: int, recheck_n: int = 10) -> Tuple[Dict[str, int], Dict[str, object], Dict[str, Dict[str, object]]]:
    """Render + glance every request in order, write the cache, then self-check `recheck_n` of them
    (§2.5's own test). Returns (item_id -> cache row, header dict, item_id -> truth dict). `truth` is
    returned to the CALLER (never written into the cache itself, §2.4: "the truth ... goes to the truth
    file only") so the caller can build truth.jsonl."""
    if len(requests) == 0:
        raise BuildError("build_cache: empty request list")
    ids = [r.item_id for r in requests]
    if len(set(ids)) != len(ids):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise BuildError(f"build_cache: duplicate item_id(s), each rendering must be unique: {dupes[:10]}")

    g = organs.load_genome()
    spec, gaze_cfg, colour = organs.gaze_config(g)
    pins = organs.organ_pins()

    libs: Dict[str, GlyphLibrary] = {}
    writer = CacheWriter(out_dir)
    item_to_row: Dict[str, int] = {}
    truths: Dict[str, Dict[str, object]] = {}
    for req in requests:
        lib = libs.setdefault(req.script, GlyphLibrary(req.script))
        feats, rgb, truth, sha = render_and_glance(req, lib, seed, spec, gaze_cfg, colour)
        row = writer.add(item_id=req.item_id, script=req.script, char=req.char, font=req.font,
                          variant=req.variant, seed=seed, canvas_png_sha256=sha, feats=feats)
        item_to_row[req.item_id] = row
        truths[req.item_id] = truth

    versions = _interpreter_versions()
    header = writer.finalize(seed=seed, genome_sha=organs.genome_sha(), organ_pins=pins,
                              interpreter=versions, library_versions=versions)

    _self_check(requests, item_to_row, out_dir, seed, recheck_n, spec, gaze_cfg, colour, libs)
    return item_to_row, header, truths


def _self_check(requests: List[RenderRequest], item_to_row: Dict[str, int], out_dir: Path, seed: int,
                 n: int, spec, gaze_cfg: Dict[str, object], colour: Optional[Dict[str, object]],
                 libs: Dict[str, GlyphLibrary]) -> None:
    """§2.5: "10 rows chosen by the seed are re-glanced at build and must equal their cached rows byte for
    byte." Re-runs `render_and_glance` FRESH (a new rng from the same (seed, item_id), a new gaze call) and
    compares to what the cache actually holds — this catches both a cache-writer bug and a non-determinism
    in the render/glance road itself."""
    rng = seeds.substream(seed, "cache_self_check")
    n = min(n, len(requests))
    chosen = rng.choice(len(requests), size=n, replace=False)
    cache = Cache(out_dir)
    for i in chosen:
        req = requests[int(i)]
        feats, _rgb, _truth, _sha = render_and_glance(req, libs[req.script], seed, spec, gaze_cfg, colour)
        cached = cache.glances(item_to_row[req.item_id])
        if not np.array_equal(feats, cached):
            raise BuildError(f"cache self-check FAILED for item_id={req.item_id!r} (row {item_to_row[req.item_id]}): "
                              f"a fresh re-glance differs from the cached row")
