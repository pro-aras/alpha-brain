# edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — a small, FAST genome (pool retina, no
# tower) shared by B2–B7's toys, so each test builds an Organism in milliseconds instead of paying the
# sealed eye tower's cost. Never used for the pin (test_pin_skeleton.py reads G4-skeleton.genome only).
"""_toy.py — a minimal, fast genome text + small helpers for the G4 gene toys (not a test module itself:
no `Test*` class, so `unittest discover` does not collect it)."""
from __future__ import annotations

from typing import Tuple

import numpy as np

from genome.machinery import Genome, parse_genome

# SENSE eye 24x24 grey + RETINA pool3 unit -> sight_dim = (24//3)**2 = 64
# SENSE ear letters 1 blank=zero -> words_dim = 1 * 26 = 26
MINI_GENOME_TEXT = """\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 1 blank=zero
AREA sight from retina
AREA words from ear
MEET sight words
BIRTH novelty cos<0.5
BIRTH error misfires 3
BUDGET 400 per arrival
NMAX 200
KWTA 5
HEBB window 1
DELTA lr 0.1
PRUNE w<0.02 after 3 chances
MERGE cos>0.99 same-answer
SCALE every 1000 moments
STAGE 1 senses moments 0..0
STAGE 2 meet moments 0..
RECALL k=1
ABSTAIN second/best > 0.85
"""

SIGHT_DIM = 64
WORDS_DIM = 26


def mini_genome(**overrides) -> Genome:
    """Parse MINI_GENOME_TEXT, with simple line-replace overrides for the knobs the toys below need."""
    text = MINI_GENOME_TEXT
    if "nmax" in overrides:
        text = text.replace("NMAX 200", f"NMAX {overrides['nmax']}")
    if "budget" in overrides:
        text = text.replace("BUDGET 400 per arrival", f"BUDGET {overrides['budget']} per arrival")
    if "theta_n" in overrides:
        text = text.replace("BIRTH novelty cos<0.5", f"BIRTH novelty cos<{overrides['theta_n']}")
    return parse_genome(text)


def unit(rng: np.random.Generator, dim: int = SIGHT_DIM) -> np.ndarray:
    """A random unit vector — cosines between independent draws in 64-d are near 0 with overwhelming
    probability, so successive draws almost always fail to resonate against theta_n=0.5 and birth."""
    v = rng.normal(size=dim)
    return v / np.linalg.norm(v)


def onehot(i: int, dim: int) -> np.ndarray:
    v = np.zeros(dim)
    v[i] = 1.0
    return v
