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
# SENSE ear letters 8 blank=zero -> words_dim = 8 * 26 = 208 (world.encode_word's WORD_SLOTS is fixed at
# 8 regardless of the genome's own ear_letters — this genome's ear MUST say 8 to match world.encode_word's
# actual output shape, or Organism._birth's shape assert fails the moment a words-area moment is fed).
MINI_GENOME_TEXT = """\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 8 blank=zero
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
WORDS_DIM = 8 * 26


# edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 00:52 +0400 — ALPHA4-G.md task 1/3/4: three additive
# overrides (grow, budget_regen, cycle_share) for the GROW/BUDGET-regen/CYCLE-redundant toys. `grow=True`
# removes the "NMAX 200" line and adds "GROW unbounded" instead (so `nmax`/`grow` are mutually exclusive —
# combining them is not a shape this helper needs to support, and is left unhandled on purpose). Every
# existing override untouched byte-for-byte; the four EXISTING call sites (theta_n/nmax/budget alone) see
# no behaviour change (verified: tests/genome/test_thresh_own_band.py and every other `_toy.py` consumer
# stay green, see the report).
def mini_genome(**overrides) -> Genome:
    """Parse MINI_GENOME_TEXT, with simple line-replace overrides for the knobs the toys below need."""
    text = MINI_GENOME_TEXT
    if overrides.get("grow"):
        text = text.replace("NMAX 200\n", "GROW unbounded\n")
    if "nmax" in overrides:
        text = text.replace("NMAX 200", f"NMAX {overrides['nmax']}")
    if "budget" in overrides:
        text = text.replace("BUDGET 400 per arrival", f"BUDGET {overrides['budget']} per arrival")
    if "budget_regen" in overrides:
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:10 +0400 — bugfix, caught by
        # test_budget_regen.py RED: a literal `.replace("BUDGET 400 per arrival", ...)` here silently
        # no-ops when the `budget` override above already changed "400" to something else, so
        # mini_genome(budget=5, budget_regen=(1, 3)) parsed budget_regen_every=None (no regen clause
        # ever landed in the text) — a bug in this HELPER, not in genome/machinery.py (confirmed by two
        # failing toys that both silently read every=None). A regex substitution matches whatever number
        # is CURRENTLY on the BUDGET line, whether or not `budget` was also overridden.
        import re as _re
        n, every = overrides["budget_regen"]
        text = _re.sub(r"BUDGET (\d+) per arrival", lambda m: f"BUDGET {m.group(1)} per arrival; regenerate {n} per {every} moments", text)
    if "cycle_share" in overrides:
        text = text.replace("SCALE every 1000 moments", f"SCALE every 1000 moments\nCYCLE consolidate when redundant > {overrides['cycle_share']} of alive")
    if "cycle_grow_to" in overrides:
        text = text.replace("SCALE every 1000 moments", f"SCALE every 1000 moments\nCYCLE grow to {overrides['cycle_grow_to']} nmax then consolidate")
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
