"""fonts.py — THE TEACH/TEST FONT SETS, "the clean-font rule" (B1-PREREG.md §2.2).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:3x +0400 — B1-PREREG.md §9 row 1, step 2 (the world).

TEACH (fixed, all scripts) = the fonts that are TRAIN in latin-upper AND latin-lower AND digits.
TEST (per script) = HOLDOUT in that script, AND never TRAIN in any of the three taught scripts, AND never
one of the sealed eye tower's own 20 training fonts (E09a's fixture, matched by file STEM, per §2.2).

Every number below was independently recomputed against the live files on this box on 2026-09-24 (before
this module existed, as a hand-run check) and matches B1-PREREG.md §2.2 exactly: TEACH = {DejaVuSansMono-
Bold.ttf, DejaVuSansMono.ttf, UbuntuSans[wdth,wght].ttf, cmr10.ttf}; TEST counts 15/12/17 for upper/lower/
digits; the "4 fonts clean in both cases" = {NimbusRoman-Bold.otf, NotoSansCJK-Bold.ttc, P052-Roman.otf,
URWBookman-DemiItalic.otf}; "1 in all three" = P052-Roman.otf; the confound counts (tower-trained fonts
inside each script's own 30 holdout fonts) = 6/4/5. This module's own `compute()` reproduces every one of
those numbers from the source files directly — nothing here is a typed-in constant except the two source
paths and the fixed TEACH-font ORDER (below), which is text from the PREREG, checked against the computed
set rather than derived from it (a sort order that happens to match today is not a citation — #171's law:
never let a coincidence stand in for a pinned fact)."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, FrozenSet, List, Mapping, Set

GLYPH_ROOT = Path("/data/alpha3-library/K/glyphs")
TOWER_FIXTURE = Path("/data/dev/alpha3/experiments/E09d-readout-on-the-tower/inputs/e09a_gate_fixture.json")
TOWER_SEED = "20260913"
SCRIPTS: tuple = ("latin-upper", "latin-lower", "digits")

# §2.2's own prose order (verbatim) — an ASSERTED fact about the data (checked in `compute()`), not derived
# from a sort that happens to agree with it today.
TEACH_FONTS_ORDER: List[str] = ["DejaVuSansMono-Bold.ttf", "DejaVuSansMono.ttf", "UbuntuSans[wdth,wght].ttf", "cmr10.ttf"]
# "stage −1 also measures 3 (the first 3 in this list's order)":
TEACH_FONTS_3 = TEACH_FONTS_ORDER[:3]


class FontsError(Exception):
    """Raised on any mismatch between this module's assumptions and the live library files — RAISED to the
    seat (B1-PREREG.md §11), never silently patched over."""


def _load_fonts_tsv(script: str) -> List[Dict[str, str]]:
    path = GLYPH_ROOT / script / "fonts.tsv"
    if not path.exists():
        raise FontsError(f"missing {path}")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _kept_where(rows: List[Dict[str, str]], split: str) -> Set[str]:
    return {r["font"] for r in rows if r["verdict"] == "kept" and r["split"] == split}


def tower_training_fonts() -> FrozenSet[str]:
    """The sealed eye tower's own 20 Latin training fonts, matched by file STEM against the library's font
    filenames (§2.2: "matched by file stem") — a stem can appear in several scripts' fonts.tsv under the
    identical filename string (asserted in `compute()`), so this reads latin-upper's own font column as the
    representative set."""
    if not TOWER_FIXTURE.exists():
        raise FontsError(f"missing tower fixture {TOWER_FIXTURE}")
    fixture = json.loads(TOWER_FIXTURE.read_text())
    try:
        stems = set(fixture["per_seed"][TOWER_SEED]["train_fonts"])
    except KeyError as e:
        raise FontsError(f"tower fixture missing per_seed[{TOWER_SEED!r}].train_fonts: {e!r}")
    rows = _load_fonts_tsv("latin-upper")
    all_fonts = {r["font"] for r in rows}
    matched = {f for f in all_fonts if Path(f).stem in stems}
    unmatched_stems = stems - {Path(f).stem for f in matched}
    if unmatched_stems:
        raise FontsError(f"tower training stems with no matching library font: {sorted(unmatched_stems)}")
    return frozenset(matched)


def compute() -> Dict[str, object]:
    """Recompute TEACH/TEST/confound from the live files. Returns the exact shape `fonts.json` stores."""
    rows = {s: _load_fonts_tsv(s) for s in SCRIPTS}
    font_name_sets = {s: {r["font"] for r in rows[s]} for s in SCRIPTS}
    if not (font_name_sets["latin-upper"] == font_name_sets["latin-lower"] == font_name_sets["digits"]):
        raise FontsError("the three scripts' fonts.tsv do not list the identical set of font filenames")

    train = {s: _kept_where(rows[s], "train") for s in SCRIPTS}
    holdout = {s: _kept_where(rows[s], "holdout") for s in SCRIPTS}
    for s in SCRIPTS:
        if len(train[s]) != 30 or len(holdout[s]) != 30:
            raise FontsError(f"{s}: expected 30 train / 30 holdout, got {len(train[s])} / {len(holdout[s])}")

    train_any = set().union(*train.values())
    tower = tower_training_fonts()

    teach = train["latin-upper"] & train["latin-lower"] & train["digits"]
    if teach != set(TEACH_FONTS_ORDER):
        raise FontsError(f"TEACH set computed from the data {sorted(teach)} != the pinned order {TEACH_FONTS_ORDER} "
                          f"— the library changed under this PREREG; RAISE to the seat, do not silently reorder")

    test = {s: sorted(holdout[s] - train_any - tower) for s in SCRIPTS}
    confound = {s: sorted(holdout[s] & tower) for s in SCRIPTS}

    return {
        "teach": list(TEACH_FONTS_ORDER),
        "teach_3": list(TEACH_FONTS_3),
        "test": test,
        "tower_training_fonts": sorted(tower),
        "confound_holdout_is_tower_trained": confound,
        "counts": {"test": {s: len(test[s]) for s in SCRIPTS}, "confound": {s: len(confound[s]) for s in SCRIPTS}},
        "sources": {"glyph_root": str(GLYPH_ROOT), "tower_fixture": str(TOWER_FIXTURE), "tower_seed": TOWER_SEED},
    }


def validate(fonts: Mapping[str, object]) -> None:
    """Raise FontsError if `fonts` (as `compute()` or `fonts.json` produces) violates its own law: no TEST
    font is a tower-training font, and no TEST font is TRAIN anywhere. The planted-font-refusal test (§2.2's
    own "a planted font ... must be refused") calls this on a deliberately corrupted copy."""
    tower = set(fonts["tower_training_fonts"])
    teach = set(fonts["teach"])
    for s in SCRIPTS:
        test_s = set(fonts["test"][s])
        bad_tower = test_s & tower
        if bad_tower:
            raise FontsError(f"{s}: TEST contains tower-training font(s) {sorted(bad_tower)}")
        bad_teach = test_s & teach
        if bad_teach:
            raise FontsError(f"{s}: TEST contains a TEACH font {sorted(bad_teach)}")


def write(out_path: Path) -> Dict[str, object]:
    fonts = compute()
    validate(fonts)
    out_path.write_text(json.dumps(fonts, sort_keys=True, indent=2) + "\n")
    return fonts
