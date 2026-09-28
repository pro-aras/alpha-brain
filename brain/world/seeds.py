"""seeds.py — NAMED, INDEPENDENT RANDOM STREAMS FROM ONE TOP-LEVEL SEED (B1-PREREG.md §2.8).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:5x +0400 — B1-PREREG.md §9 row 1, step 2 (the world).

§2.8: "The seed governs: which of each family's pairs are held out; which test fonts carry each item's
renderings; every rendering's placement and noise; every arm's initialisation and its sampling generators."
§2.4: "one numpy.random.Generator per rendering, seeded from (seed, item_id)."

A SINGLE shared `np.random.Generator` threaded through every one of those uses would make the whole tape
fragile to reordering: add one rendering anywhere and every later draw (a held-out split, a font
assignment, a placement) silently shifts (the identity law, CONCLUSION.md §3.8, would then read a changed
tape as a changed WORLD even though nothing about the PREREG's construction changed). `substream` instead
derives an INDEPENDENT, reproducible generator per named purpose from `numpy.random.SeedSequence` — the
family split for "AFTER" and the placement for item "TEACH:latin-upper:A:round3" never interact, in either
direction, no matter what order the caller asks for them in.
"""
from __future__ import annotations

import hashlib

import numpy as np


def _purpose_hash(purpose: str) -> int:
    """A stable (non-Python-hash-randomised) 64-bit int from a purpose string."""
    return int(hashlib.sha256(purpose.encode("utf-8")).hexdigest()[:16], 16)


def substream(seed: int, purpose: str) -> np.random.Generator:
    """An independent `Generator` for `purpose`, reproducible from (`seed`, `purpose`) alone — the SAME
    generator every time this is called with the same two arguments, in any process, in any order relative
    to other calls."""
    return np.random.default_rng(np.random.SeedSequence([int(seed) & 0xFFFFFFFF, _purpose_hash(purpose) & 0xFFFFFFFF]))


def rendering_rng(seed: int, item_id: str) -> np.random.Generator:
    """§2.4's own rule: "one numpy.random.Generator per rendering, seeded from (seed, item_id)"."""
    return substream(seed, f"render:{item_id}")
