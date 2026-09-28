"""eye.py — the creature's eye on a scene, and the eye's own segmentation (PREREG-R3-TONIGHT §S1a «The eye», «The eye's
segmentation»).

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:06 +0400 — new module.

  look()            ONE `genome.gaze.glances(rgb, spec, gaze, mode="surprise", pic_id=<canvas png sha>, colour=…,
                    predicted=None)` call per scene, exactly as brain/world/build.py makes it, with spec / gaze / colour
                    parsed from genome/ALPHA4.genome by brain.world.organs. Runs under /usr/bin/python3 (the cache road).
  hypotheses()      the 4 located fixations grouped by union-find: two fixations within 2 grid cells (Chebyshev) join.
                    Each group is a THING HYPOTHESIS: the unit mean of its fixations' 144 numbers, its mean grid
                    position (y, x), its fixation count. The coarse glance is kept beside, unused in S1a.
  forced_glance()   ORACLE-TRUTH's one window at a thing's centroid: the SAME composition genome.gaze.glances makes for a
                    fixated cell (luminance → the declared INK rule → machinery.retina → ⊕ colour_block under the window →
                    unit), with the window's top-left from the centroid by genome.gaze.glance_window's own clamp — the way
                    game-worlds/code/bands.py's forced road places it. Pinned: at a fixation cell's centre it reproduces
                    that fixation's glance byte for byte (tests/brain/scene/test_eye.py).

This module never reads the world's truth: a centroid is an ARGUMENT (the cache builder passes it); the learner's
things in view are `hypotheses()` alone (tests/brain/scene/test_truth_fence.py).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from genome import gaze as G
from genome.machinery import _unit, retina

from brain.world import organs
from brain.world.build import canvas_png_sha256

MERGE_CELLS = 2          # «two fixations within 2 grid cells (Chebyshev) join»
GLANCES_PER_ROW = 5      # 4 located + 1 coarse (brain.glance_cache's row shape)
FEATS = 144


def eye_config() -> Tuple[Tuple[str, ...], Dict[str, object], Optional[Dict[str, object]]]:
    """(RETINA spec, GAZE dict, SENSE colour) exactly as ALPHA4.genome declares them (brain.world.organs)."""
    return organs.gaze_config(organs.load_genome())


def look(rgb: np.ndarray, spec, gaze_cfg: Dict[str, object], colour) -> Tuple[str, np.ndarray, List[Tuple[int, int]]]:
    """-> (canvas png sha256, feats (k + 1, 144) = k located glances then the coarse one, fixation cells (k,)). k ≤ 4:
    gaze_sequence may stop early, so k is returned, never assumed."""
    sha = canvas_png_sha256(rgb)
    out = G.glances(rgb, spec, gaze_cfg, mode="surprise", pic_id=sha, colour=colour, predicted=None)
    fix = [(int(y), int(x)) for y, x in out["fix"]]
    feats = np.stack([np.asarray(v, dtype=np.float64) for v in out["feats"]], axis=0)
    if feats.shape != (len(fix) + 1, FEATS):
        raise ValueError(f"glances returned {feats.shape} for {len(fix)} fixations (expected {len(fix) + 1} × {FEATS})")
    return sha, feats, fix


def glance_row(feats: np.ndarray, n_fix: int) -> np.ndarray:
    """The (5, 144) cache row: located glances in rows 0..n_fix−1, zeros up to row 3, the coarse glance in row 4."""
    row = np.zeros((GLANCES_PER_ROW, FEATS), dtype=np.float64)
    row[:n_fix] = feats[:n_fix]
    row[GLANCES_PER_ROW - 1] = feats[n_fix]
    return row


@dataclass(frozen=True)
class Hypothesis:
    members: Tuple[int, ...]          # indices into the scene's located fixations, ascending
    feat: np.ndarray                  # (144,) the unit mean of the members' glances
    pos: Tuple[float, float]          # the members' mean grid cell (y, x)

    @property
    def count(self) -> int:
        return len(self.members)


def groups(fix: Sequence[Tuple[int, int]], radius: int = MERGE_CELLS) -> List[Tuple[int, ...]]:
    """Union-find over the fixations: i and j join when max(|Δy|, |Δx|) ≤ radius; the groups ordered by their first
    fixation (the gaze's own order)."""
    n = len(fix)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(n):
        for j in range(i + 1, n):
            if max(abs(fix[i][0] - fix[j][0]), abs(fix[i][1] - fix[j][1])) <= radius:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[max(ri, rj)] = min(ri, rj)
    out: Dict[int, List[int]] = {}
    for i in range(n):
        out.setdefault(find(i), []).append(i)
    return [tuple(sorted(m)) for _r, m in sorted(out.items(), key=lambda kv: min(kv[1]))]


def hypotheses(fix: Sequence[Tuple[int, int]], located: np.ndarray) -> List[Hypothesis]:
    """The scene's THING HYPOTHESES from its located fixations `fix` and their glances `located` (len(fix), 144)."""
    located = np.asarray(located, dtype=np.float64)
    if located.shape != (len(fix), FEATS):
        raise ValueError(f"located glances {located.shape} do not match {len(fix)} fixations")
    hyps = []
    for m in groups(fix):
        v = _unit(located[list(m)].mean(axis=0))
        pos = (float(np.mean([fix[i][0] for i in m])), float(np.mean([fix[i][1] for i in m])))
        hyps.append(Hypothesis(m, v, pos))
    return hyps


def forced_top_left(centroid: Tuple[float, float], h: int, w: int, glance: int) -> Tuple[int, int]:
    """genome.gaze.glance_window's clamp, centred on a pixel instead of a cell centre (bands.py's forced road)."""
    cy, cx = centroid
    top = int(min(max(round(cy - glance / 2), 0), h - glance))
    left = int(min(max(round(cx - glance / 2), 0), w - glance))
    return top, left


def forced_glance(rgb: np.ndarray, centroid: Tuple[float, float], spec, gaze_cfg: Dict[str, object], colour,
                  an: Optional[dict] = None, grey: Optional[np.ndarray] = None) -> np.ndarray:
    """ONE window at `centroid` (px) through the eye's own pieces; `an` / `grey` may be passed in to reuse one retina
    analysis per canvas (they are pure functions of the canvas)."""
    glance = int(gaze_cfg["glance"])
    ink_rule = G.INK_RULES[str(gaze_cfg.get("ink", "contrast"))]
    if grey is None:
        grey = G.luminance(rgb)
    top, left = forced_top_left(centroid, grey.shape[0], grey.shape[1], glance)
    win = grey[top:top + glance, left:left + glance]
    v = retina(ink_rule(win), tuple(spec))
    if colour is not None:
        if an is None:
            an = G._analyse_frame(rgb)
        v = _unit(np.concatenate([v, G.colour_block(an, top, left)]))
    return np.asarray(v, dtype=np.float64)


def cell_centre_px(cell: Tuple[int, int], canvas: int, grid: int) -> Tuple[float, float]:
    """A grid cell's centre in pixels — glance_window's own (cell + 0.5) · canvas / grid."""
    return ((cell[0] + 0.5) * (canvas / grid), (cell[1] + 0.5) * (canvas / grid))
