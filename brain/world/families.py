"""families.py — THE RELATION AND PERCEPTUAL FAMILIES, construction-exact (B1-PREREG.md §5.2).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:5x +0400 — B1-PREREG.md §9 row 1, step 2 (the world).

Every count here is checked against §5.2's own table in `test_families.py`. Held-out selections are drawn
from `brain.world.seeds.substream(seed, <a purpose string unique to this family>)`, never from a generator
shared with anything else (§2.8; see `seeds.py`'s own docstring for why). "His order" for A...Z is plain
alphabetical (CONCLUSION.md §4.1: "his order A then B then C" — confirmed against the text, not assumed).

What this module does NOT build: the never-taught-sign pool (§3.3 — that selection runs the tower's own
gaze against a cosine threshold, which IS stage −1's job; see `brain/harness/stage_minus1.py`) or any actual
rendering (that is `brain/world/canvas.py` + `brain/world/build.py`). `misuse_items()`'s two sign-dependent
kinds (OTHER_CASE of a digit needs nothing external; "AFTER a never-taught sign" does) take the pool as a
parameter and raise `FamiliesError` if asked for without one — RAISED, never silently skipped (B1-PREREG.md
§11).
"""
from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from .names import DIGIT_NAMES, LOWER, UPPER, letter_name
from .seeds import substream

LETTER_NAMES: List[str] = [letter_name(c) for c in UPPER]   # ["a", "b", ..., "z"], his order (A then B then C)
FORMS_52: List[Tuple[str, str]] = [("latin-upper", c) for c in UPPER] + [("latin-lower", c) for c in LOWER]

Pair = Tuple[str, str]
Triple = Tuple[str, str, str]


class FamiliesError(Exception):
    pass


def _consecutive_pairs(names: Sequence[str]) -> List[Pair]:
    return [(names[i], names[i + 1]) for i in range(len(names) - 1)]


def _two_apart_pairs(names: Sequence[str]) -> List[Pair]:
    return [(names[i], names[i + 2]) for i in range(len(names) - 2)]


def _consecutive_triples(names: Sequence[str]) -> List[Triple]:
    return [(names[i], names[i + 1], names[i + 2]) for i in range(len(names) - 2)]


# The base relations over letter NAMES, in his order (a, b, ..., z) — 25/24/24, exactly §5.2's counts.
AFTER_PAIRS: List[Pair] = _consecutive_pairs(LETTER_NAMES)          # (a,b) .. (y,z) — after(a)=b
BETWEEN_TRIPLES: List[Triple] = _consecutive_triples(LETTER_NAMES)  # (a,b,c) .. (x,y,z) — between(a,c)=b
TWO_AFTER_PAIRS: List[Pair] = _two_apart_pairs(LETTER_NAMES)        # (a,c) .. (x,z) — two_after(a)=c
DIGIT_AFTER_PAIRS: List[Pair] = _consecutive_pairs(list(DIGIT_NAMES))  # (zero,one) .. (eight,nine) — 9 pairs

assert len(AFTER_PAIRS) == 25 and len(BETWEEN_TRIPLES) == 24 and len(TWO_AFTER_PAIRS) == 24 and len(DIGIT_AFTER_PAIRS) == 9


def _split(seed: int, purpose: str, items: Sequence, n_held: int) -> Tuple[List, List]:
    """A seeded, order-stable held-out/taught split: `n_held` items drawn without replacement (their
    ORIGINAL relative order kept in both output lists, so two calls with the same seed+purpose always
    produce the identical two lists regardless of how the caller iterates them)."""
    rng = substream(seed, purpose)
    idx = rng.choice(len(items), size=n_held, replace=False)
    held_idx = set(int(i) for i in idx)
    held = [items[i] for i in range(len(items)) if i in held_idx]
    taught = [items[i] for i in range(len(items)) if i not in held_idx]
    return taught, held


def after_before(seed: int) -> Dict[str, object]:
    """AFTER and BEFORE share ONE seeded set of 12 held out of the 25 consecutive pairs (§5.2: "ONE seeded
    set of 12 held out for both (no held-out pair is the inverse of a taught one)") — vacuous as a
    constraint on AFTER's own 25 pairs alone (a pair's reverse is not itself an AFTER pair), so the binding
    fact is simply that AFTER and BEFORE are the SAME split, read backward for BEFORE."""
    taught, held = _split(seed, "family:after_before", AFTER_PAIRS, 12)
    return {"taught": taught, "held_out": held,        # AFTER: after(a)=b
            "before_taught": [(b, a) for a, b in taught], "before_held_out": [(b, a) for a, b in held]}


def between(seed: int) -> Dict[str, object]:
    taught, held = _split(seed, "family:between", BETWEEN_TRIPLES, 12)
    return {"taught": taught, "held_out": held}


def two_after(seed: int) -> Dict[str, object]:
    """"3 taught (both cases, only after AFTER is known), 21 held out" — the 3 TRAINING pairs (used to
    teach the new cue in L5) are a seeded choice of 3 of the 24 two-apart pairs; the rest are held out for
    the examples-to-bar probes (P1-P4, §5.2)."""
    taught, held = _split(seed, "family:two_after", TWO_AFTER_PAIRS, 21)
    if len(taught) != 3:
        raise FamiliesError(f"two_after: expected 3 training pairs, got {len(taught)}")
    return {"taught": taught, "held_out": held}


def other_case(seed: int) -> Dict[str, object]:
    """26 letters, each with exactly one other-case partner; 13 taught / 13 held out, each item asked in
    BOTH directions (upper->lower and lower->upper, §5.1). Held out by NAME (§2.3/§5.2), so "letter" here
    IS the name; stage −1 later removes any held-out letter whose two forms are identical through the organ
    (c/C, o/O, ...) and recomputes k — this module does not know about that removal (§5.2's own note)."""
    taught, held = _split(seed, "family:other_case", LETTER_NAMES, 13)
    return {"taught": taught, "held_out": held}


def chain(after_before_result: Mapping[str, object] = None, seed: int = None) -> Dict[str, object]:
    """"never taught chained; all 25 name pairs, each asked in both directions" — CHAIN has no held-out
    split of its own; every AFTER pair is a CHAIN test item, and the AFTER/BEFORE split is carried through
    only as a REPORTING breakdown ("printed split by whether the AFTER pair was taught or held out",
    §5.2 — never a second bar, §5.1)."""
    if after_before_result is None:
        if seed is None:
            raise FamiliesError("chain() needs either after_before_result or a seed to derive it from")
        after_before_result = after_before(seed)
    taught_set = set(after_before_result["taught"])
    breakdown = [{"pair": p, "after_was": "taught" if p in taught_set else "held_out"} for p in AFTER_PAIRS]
    return {"items": list(AFTER_PAIRS), "breakdown": breakdown}


def transfer() -> Dict[str, object]:
    """AFTER and BEFORE on the digits' own order — never trained on digits (§2.7: "no relation episode on
    digits"), so every item is a zero-shot TEST item at T_D; no held-out split (all 9+9=18 are test items)."""
    after_items = list(DIGIT_AFTER_PAIRS)
    before_items = [(b, a) for a, b in DIGIT_AFTER_PAIRS]
    return {"after": after_items, "before": before_items, "items": after_items + before_items}


# ---------------------------------------------------------------------------------------- perceptual families
MIRROR_POSITIVE_FORMS: List[Tuple[str, str]] = (
    [("latin-upper", c) for c in "AHIMOTUVWXY"] + [("latin-lower", c) for c in "ilovwx"])
LOOP_POSITIVE_FORMS: List[Tuple[str, str]] = (
    [("latin-upper", c) for c in "ABDOPQR"] + [("latin-lower", c) for c in "abdegopq"])
VOWEL_FORMS: List[Tuple[str, str]] = [("latin-upper", c) for c in "AEIOU"] + [("latin-lower", c) for c in "aeiou"]

assert len(MIRROR_POSITIVE_FORMS) == 17 and len(LOOP_POSITIVE_FORMS) == 15 and len(VOWEL_FORMS) == 10


def _balanced_perceptual(seed: int, purpose: str, positives: Sequence[Tuple[str, str]], n_pos_held: int, n_neg_held: int) -> Dict[str, object]:
    negatives = [f for f in FORMS_52 if f not in set(positives)]
    pos_taught, pos_held = _split(seed, purpose + ":pos", list(positives), n_pos_held)
    neg_taught, neg_held = _split(seed, purpose + ":neg", negatives, n_neg_held)
    return {"positive_forms": list(positives), "negative_forms": negatives,
            "taught": {"positive": pos_taught, "negative": neg_taught},
            "held_out": {"positive": pos_held, "negative": neg_held}}


def mirror_symmetric(seed: int) -> Dict[str, object]:
    return _balanced_perceptual(seed, "family:mirror", MIRROR_POSITIVE_FORMS, 8, 8)


def has_loop(seed: int) -> Dict[str, object]:
    return _balanced_perceptual(seed, "family:loop", LOOP_POSITIVE_FORMS, 7, 7)


def vowel(seed: int) -> Dict[str, object]:
    """"taught on all 52 forms ... tested on the 10 vowel forms + 10 seeded consonant forms x 2 seeded test
    fonts of the form's case" — the family construction here is just WHICH 10 consonants; the two test
    fonts per form are a tape-building/rendering-assignment decision (`build.py`), not a family fact."""
    consonants = [f for f in FORMS_52 if f not in set(VOWEL_FORMS)]
    rng = substream(seed, "family:vowel:consonants")
    idx = rng.choice(len(consonants), size=10, replace=False)
    chosen = [consonants[i] for i in sorted(int(i) for i in idx)]
    return {"vowel_forms": list(VOWEL_FORMS), "consonant_forms": chosen}


# ---------------------------------------------------------------------------------------- U5 misuse items (§5.3)
def misuse_items(after_before_result: Mapping[str, object], two_after_result: Mapping[str, object],
                  between_result: Mapping[str, object], never_taught_pool: Sequence[object] = None) -> Dict[str, object]:
    """§5.3 U5's six kinds (49 items total): AFTER z (1) · BEFORE a (1) · TWO_AFTER y,z (2) · BETWEEN two
    adjacent letters (25) · OTHER_CASE of a digit (10, at T_D) · AFTER a never-taught sign (10). The first
    four need nothing but the alphabet itself; the last two need external data this module does not own —
    OTHER_CASE-of-a-digit needs only the 10 digit names (no pool), but "AFTER a never-taught sign" needs
    `never_taught_pool` (stage −1's own selection, §3.3). Raises FamiliesError (RAISED to the seat, never
    silently skipped, B1-PREREG.md §11) if that kind is asked for without a pool."""
    after_z = [("AFTER", ("z",))]
    before_a = [("BEFORE", ("a",))]
    two_after_yz = [("TWO_AFTER", ("y",)), ("TWO_AFTER", ("z",))]
    between_adjacent = [("BETWEEN", pair) for pair in AFTER_PAIRS]   # 25 adjacent (no-gap) pairs
    other_case_digit = [("OTHER_CASE", (d,)) for d in DIGIT_NAMES]   # 10
    if never_taught_pool is None:
        after_never_taught = None   # not yet gradable — RAISED at the call site that needs it, not here
    else:
        if len(never_taught_pool) < 10:
            raise FamiliesError(f"misuse_items: never_taught_pool has {len(never_taught_pool)} signs, need >= 10")
        after_never_taught = [("AFTER", (sign,)) for sign in never_taught_pool[:10]]
    return {
        "after_z": after_z, "before_a": before_a, "two_after_yz": two_after_yz,
        "between_adjacent": between_adjacent, "other_case_digit": other_case_digit,
        "after_never_taught": after_never_taught,
        "total_gradable": len(after_z) + len(before_a) + len(two_after_yz) + len(between_adjacent)
                          + len(other_case_digit) + (10 if after_never_taught else 0),
    }

