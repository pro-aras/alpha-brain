# edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 23:40 +0400 — B8 (docs/G4-PREREG.md §9 Amendment 1):
# shared helpers for the two re-specified toys, on the CREATURE'S OWN FRONT — G4-skeleton.genome's
# RETINA (thresh0.25 centre tower:eye-tower-g2 sqrt unit) over 32x32 glances of world.render_canvas
# canvases at 128 (G1's world), never the ad hoc pool3/world.render toys B6/B7 used (those readings
# stand on record as FAIL, re-graded here on the real front per the amendment).
"""_creature_front.py — not a test module itself (no Test* class)."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

from genome import gaze, world
from genome.machinery import Genome, parse_genome

ROOT = Path(__file__).resolve().parent.parent.parent
SKELETON_TEXT = (ROOT / "genome" / "G4-skeleton.genome").read_text()


def skeleton_genome() -> Genome:
    """The real, calibrated skeleton genome (THETA_N=0.955, THETA_M=0.9975 — gate G-a's own numbers on
    this exact front) — unmodified. Use for the MODULATION toy, whose STAGE 1..200 window is well under
    the 200-moment repeating stream anyway (STAGE 2 meet starts at 200, and the toy IS ~200 moments —
    see the module docstring in test_b8_modulation.py for why this is fine there but not for SLEEP's
    two 80-showing arrivals, 160 moments each, which never reach it)."""
    return parse_genome(SKELETON_TEXT)


def skeleton_genome_immediate_meet() -> Genome:
    """The skeleton's genome text with ONLY the STAGE gene changed (meet from moment 0, not 200) — same
    front, same thetas, same everything else. STAGE governs WHEN wiring starts, not the retina/eye/gaze
    front the amendment is about; a life shorter than 200 moments (SLEEP's two 80-showing arrivals, 160
    moments each) would otherwise never leave STAGE 1 and every recall would read NOEDGE by construction
    — that is an artifact of the toy's length choice, not a finding about SLEEP."""
    text = SKELETON_TEXT.replace(
        "STAGE  1 senses   moments 0..200", "STAGE  1 senses   moments 0..0"
    ).replace(
        "STAGE  2 meet     moments 200..", "STAGE  2 meet     moments 0.."
    )
    assert "STAGE  1 senses   moments 0..0" in text and "STAGE  2 meet     moments 0.." in text, \
        "STAGE replace did not match the skeleton text exactly"
    return parse_genome(text)


def first_fixation_feature(genome: Genome, rgb: np.ndarray, pic_id: str) -> np.ndarray:
    """One glance per showing = the FIRST surprise fixation (the saliency peak) — the amendment's other
    offered option, "the whole canvas at 32x32 as T-one-glance does", was tried FIRST and produces
    OVERLAPPING bands (within-median 0.993 vs between-p95 0.995 on circle/square/triangle): shrinking
    the WHOLE 128px canvas to 32px shrinks the 32px thing itself to ~8px, losing the detail the sealed
    tower needs. The first fixation (this function) does not have that problem — see
    test_b8_modulation.py's module docstring for both readings."""
    g = gaze.glances(rgb, genome.retina, genome.gaze, "surprise", pic_id=pic_id)
    return g["feats"][0]


def repeating_block_stream(seed: int, things: Sequence[str], cycles: int = 4, block: int = 17) -> List[Tuple[str, np.ndarray]]:
    """A repeating N-thing stream of jittered CANVAS showings: `cycles` passes, `block` fresh canvases
    of each thing in a row per pass — consecutive showings SHARE a thing most of the time (B6's own
    lesson: an A-B-C round-robin never repeats a thing on consecutive moments, so a persistence
    predictor's `expect()` always predicts a DIFFERENT thing than what comes next, by construction)."""
    rng = np.random.default_rng(seed)
    out: List[Tuple[str, np.ndarray]] = []
    for _c in range(cycles):
        for t in things:
            for _ in range(block):
                rgb, _truth = world.render_canvas(t, rng)
                out.append((t, rgb))
    return out
