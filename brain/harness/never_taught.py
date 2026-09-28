"""never_taught.py — STAGE -1 CLAUSE 3: THE NEVER-TAUGHT CANDIDATE POOL (B1-PREREG.md §3.3).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 18:2x +0400 — B1-PREREG.md §9 row 1, step 4 (stage −1).

"Never-taught signs (U2) and the plant (U6): candidates = base-32 glyphs of Hebrew, Arabic, Devanagari and
Greek ... A candidate is kept only if its max F cosine to every TEACH exemplar of every taught letter and
digit is below theta = the between-class p95 of the TEACH letters' own F cosines ... From the kept pool,
seeded and disjoint: 40 for U2, 10 for U6's refusal check, 10 for U5's 'after a never-taught sign', and 1
plant drawn only from signs with >= 11 fonts ... A pool under 61 shrinks the four counts in proportion (k
recomputed) and is RAISED if any falls under its NOT GRADABLE line."

Theta's own denominator, as this module implements it (declared here since §3.3 names the QUANTITY —
"the between-class p95 of the TEACH letters" — but not exactly which exemplar set it is computed over):
the latin-upper TEACH exemplars at all 4 TEACH fonts, 26 classes (one per letter). This is the SAME
convention `stage_minus1.py` passes to `ceilings.other_case_removed_pairs` for its own theta, so one number
serves both uses the PREREG names it for (§3.3 uses the identical phrase in both places). If the seat wants
a different denominator (e.g. upper+lower combined, or per-script thetas), that is a one-line change here,
flagged in the builder's report as a convention choice, not a clause left unimplemented.

The "NOT GRADABLE line" for the proportional shrink is not given a number anywhere in §3 — this module
RAISES (NeverTaughtError) if the shrink would leave any of the four sub-pools at zero, the one floor that
needs no further number to be unambiguous, and leaves any FINER threshold to the seat's own §12 line.
"""
from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np

from brain.glance_cache import Cache
from brain.world.build import RenderRequest, build_cache
from brain.world.glyphs import NEVER_TAUGHT_SCRIPTS, GlyphLibrary

from brain.world.seeds import substream

from .oracles import f_pool

U2_N, U6_REFUSAL_N, U5_N, PLANT_N = 40, 10, 10, 1
MIN_PLANT_FONTS = 11


class NeverTaughtError(Exception):
    pass


def candidate_pool(teach_exemplars_X: np.ndarray, theta: float, seed: int, cache_dir) -> List[Dict[str, object]]:
    """One representative base-32 rendering per (script, char) across the four never-taught scripts (the
    first font, by sorted order, that has that character — a fixed, reproducible choice; the KEEP test only
    needs to know whether the sign resembles a taught form at all). Returns the KEPT candidates: those whose
    F_pool cosine to every row of `teach_exemplars_X` is below `theta`."""
    kept: List[Dict[str, object]] = []
    for script in NEVER_TAUGHT_SCRIPTS:
        lib = GlyphLibrary(script)
        chars = sorted({c for (c, _f) in lib._by_key})
        reqs, char_font, n_fonts = [], {}, {}
        for c in chars:
            fonts_for_c = lib.fonts_available_for(c)
            n_fonts[c] = len(fonts_for_c)
            if fonts_for_c:
                font = fonts_for_c[0]
                char_font[c] = font
                reqs.append(RenderRequest(item_id=f"nt:{script}:{c}", script=script, char=c, font=font))
        if not reqs:
            continue
        item_to_row, _header, _truths = build_cache(reqs, cache_dir, seed)
        cache = Cache(cache_dir)
        for c in chars:
            iid = f"nt:{script}:{c}"
            if iid not in item_to_row:
                continue
            v = f_pool(cache.glances(item_to_row[iid]))
            max_cos = float(np.max(teach_exemplars_X @ v))
            if max_cos < theta:
                kept.append({"script": script, "char": c, "font": char_font[c], "max_cos_to_teach": max_cos,
                             "n_fonts_available": n_fonts[c]})
    return kept


def select_pools(kept: Sequence[Dict[str, object]], seed: int) -> Dict[str, object]:
    """Seeded, DISJOINT draw of U2 (40) / U6-refusal (10) / U5 (10) / the plant (1, from signs with >= 11
    fonts). Shrinks all four in proportion if `len(kept) < 61`; raises if that would zero any of them."""
    n = len(kept)
    total_needed = U2_N + U6_REFUSAL_N + U5_N + PLANT_N
    plant_eligible_count = sum(1 for k in kept if k["n_fonts_available"] >= MIN_PLANT_FONTS)
    if n >= total_needed and plant_eligible_count >= 1:
        u2_n, u6_n, u5_n, plant_n = U2_N, U6_REFUSAL_N, U5_N, PLANT_N
    else:
        scale = n / total_needed if total_needed else 0.0
        u2_n, u6_n, u5_n = int(U2_N * scale), int(U6_REFUSAL_N * scale), int(U5_N * scale)
        plant_n = 1 if plant_eligible_count >= 1 else 0
        if min(u2_n, u6_n, u5_n, plant_n) <= 0:
            raise NeverTaughtError(
                f"never-taught pool has only {n} candidates ({plant_eligible_count} plant-eligible) — "
                f"the proportional shrink zeroes at least one of U2/U6/U5/plant; NOT GRADABLE, RAISE to the seat")

    rng = substream(seed, "never_taught:select")
    order = [int(i) for i in rng.permutation(n)]
    shuffled = [kept[i] for i in order]

    plant_pool_shuffled = [c for c in shuffled if c["n_fonts_available"] >= MIN_PLANT_FONTS]
    plant = plant_pool_shuffled[0]
    rest = [c for c in shuffled if c is not plant]

    u2 = rest[:u2_n]
    u6_refusal = rest[u2_n:u2_n + u6_n]
    u5 = rest[u2_n + u6_n:u2_n + u6_n + u5_n]

    return {"u2": u2, "u6_refusal": u6_refusal, "u5_after_never_taught": u5, "plant": plant,
            "counts": {"u2": len(u2), "u6_refusal": len(u6_refusal), "u5": len(u5), "plant": 1},
            "pool_size": n, "plant_eligible_count": plant_eligible_count}
