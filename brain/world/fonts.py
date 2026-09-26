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
# edit: Claude (Opus 5.5), 2026-09-26 11:20 +0400 — R30 (docs/brain/b1/SEAT-DECISIONS.md): a TEST font must be a WHOLE,
# TRUE alphabet. The graded tape for seed 20261001 died at 19:13 on 09-24 on (C, StandardSymbolsPS.otf): §2.2 chooses TEST
# per FONT (the library's "kept — distinct alphabet" verdict), the base-32 pool is per (char, font), and the schedule pairs
# every letter with every TEST font. Measured 2026-09-26: StandardSymbolsPS.otf draws GREEK letters under the Latin codes
# (26 of 26 glyphs named Alpha, Beta, Chi, …: its S is Σ, its P is Π, its R is Ρ — a label conflict, #225) and lacks
# C D F U V in the pool; cmsy10.ttf lacks Y; NotoSerifDisplay-Italic.ttf lacks y. The rule: (i) every character of the
# script present in the base-32 pool, and (ii) every glyph NAMED for its own character (unnamed CID glyphs carry no claim).
# TEST counts 15/12/17 → 13/11/17.
from __future__ import annotations

import csv
import json
import re
import string
from pathlib import Path
from typing import Dict, FrozenSet, List, Mapping, Optional, Set

GLYPH_ROOT = Path("/data/alpha3-library/K/glyphs")
TOWER_FIXTURE = Path("/data/dev/alpha3/experiments/E09d-readout-on-the-tower/inputs/e09a_gate_fixture.json")
TOWER_SEED = "20260913"
SCRIPTS: tuple = ("latin-upper", "latin-lower", "digits")
SCRIPT_CHARS: Dict[str, str] = {"latin-upper": string.ascii_uppercase, "latin-lower": string.ascii_lowercase,
                                "digits": string.digits}
# R30 (ii)'s measured fact, PINNED: the fonts whose glyphs are named for OTHER characters. `compute()` re-derives it with
# fontTools whenever fontTools is importable (/usr/bin/python3 has it, the brain venv does not) and RAISES on any drift.
MISNAMED_PINNED: Dict[str, List[str]] = {"latin-upper": ["StandardSymbolsPS.otf"], "latin-lower": [], "digits": []}

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


def incomplete_fonts(script: str, candidates: List[str]) -> Dict[str, str]:
    """R30 (i): the candidates that lack any of the script's characters in the base-32 pool → the missing characters."""
    from .glyphs import GlyphLibrary  # local import: glyphs.py imports this module
    lib = GlyphLibrary(script)
    pool_chars = "".join(sorted({c for (c, _f) in lib._by_key}))
    if pool_chars != "".join(sorted(SCRIPT_CHARS[script])):
        raise FontsError(f"{script}: the base-32 pool's characters {pool_chars!r} are not the script's alphabet — RAISE to the seat")
    out: Dict[str, str] = {}
    for f in candidates:
        missing = "".join(c for c in SCRIPT_CHARS[script] if not lib.has(c, f))
        if missing:
            out[f] = missing
    return out


def _named_for(char: str, name: Optional[str], agl_name: Optional[str]) -> bool:
    if name is None:
        return False
    if name.startswith(("cid", "glyph")):   # an unnamed (CID-keyed) glyph makes no claim about its character
        return True
    base = re.split(r"[._]", name)[0]
    return base in {agl_name, f"uni{ord(char):04X}", f"u{ord(char):04X}", char}


def misnamed_fonts(script: str, candidates: List[str], paths: Mapping[str, str]) -> Optional[Dict[str, List[str]]]:
    """R30 (ii): the candidates whose glyph for a character of the script is NAMED for another character (a symbol-encoded
    font — StandardSymbolsPS maps S to "Sigma") → up to 5 `char->name` examples each. None when fontTools is absent."""
    try:
        from fontTools import agl
        from fontTools.ttLib import TTCollection, TTFont
    except ImportError:
        return None
    out: Dict[str, List[str]] = {}
    for f in candidates:
        p = paths[f]
        tt = TTCollection(p).fonts[0] if p.lower().endswith(".ttc") else TTFont(p, lazy=True)
        cmap = tt.getBestCmap() or {}
        bad = [f"{c}->{cmap.get(ord(c))}" for c in SCRIPT_CHARS[script]
               if not _named_for(c, cmap.get(ord(c)), agl.UV2AGL.get(ord(c)))]
        if bad:
            out[f] = bad[:5]
    return out


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

    candidates = {s: sorted(holdout[s] - train_any - tower) for s in SCRIPTS}
    incomplete = {s: incomplete_fonts(s, candidates[s]) for s in SCRIPTS}
    paths = {r["font"]: r["path"] for r in rows["latin-upper"]}
    misnamed: Dict[str, List[str]] = {}
    checked = True
    for s in SCRIPTS:
        derived = misnamed_fonts(s, candidates[s], paths)
        if derived is None:
            checked = False
        elif sorted(derived) != sorted(MISNAMED_PINNED[s]):
            raise FontsError(f"{s}: misnamed TEST candidates derived {derived} != pinned {MISNAMED_PINNED[s]} (R30) — RAISE to the seat")
        misnamed[s] = sorted(MISNAMED_PINNED[s])
    test = {s: sorted(set(candidates[s]) - set(incomplete[s]) - set(misnamed[s])) for s in SCRIPTS}
    confound = {s: sorted(holdout[s] & tower) for s in SCRIPTS}

    return {
        "teach": list(TEACH_FONTS_ORDER),
        "teach_3": list(TEACH_FONTS_3),
        "test": test,
        "tower_training_fonts": sorted(tower),
        "confound_holdout_is_tower_trained": confound,
        "excluded_r30": {s: {"incomplete": incomplete[s], "misnamed": misnamed[s]} for s in SCRIPTS},
        "misnamed_checked_by_fonttools": checked,
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
        bad_named = test_s & set(MISNAMED_PINNED[s])
        if bad_named:
            raise FontsError(f"{s}: TEST contains a font whose glyphs are named for other characters {sorted(bad_named)} (R30 ii)")
        holes = incomplete_fonts(s, sorted(test_s))
        if holes:
            raise FontsError(f"{s}: TEST font(s) missing characters in the base-32 pool {holes} (R30 i)")


def write(out_path: Path) -> Dict[str, object]:
    fonts = compute()
    validate(fonts)
    out_path.write_text(json.dumps(fonts, sort_keys=True, indent=2) + "\n")
    return fonts
