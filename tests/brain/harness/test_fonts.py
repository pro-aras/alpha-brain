# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:3x +0400 — tests for brain/world/fonts.py
# (B1-PREREG.md §2.2). Reads the REAL library files under /data/alpha3-library (read-only) — this is not a
# synthetic-fixture test: the whole point is that `compute()` reproduces numbers independently checked by
# hand against the live files before this module was written (see fonts.py's own docstring).
from __future__ import annotations

import copy
import unittest

from brain.world import fonts


class TestFontsCompute(unittest.TestCase):
    def setUp(self) -> None:
        self.f = fonts.compute()

    def test_teach_is_the_pinned_four(self) -> None:
        self.assertEqual(self.f["teach"], fonts.TEACH_FONTS_ORDER)
        self.assertEqual(len(self.f["teach"]), 4)

    def test_teach_3_is_first_three(self) -> None:
        self.assertEqual(self.f["teach_3"], fonts.TEACH_FONTS_ORDER[:3])

    def test_test_counts_match_prereg(self) -> None:
        # edit: Claude (Opus 5.5), 2026-09-26 11:20 +0400 — R30: §2.2's 15/12/17 less the three fonts that are not a whole,
        # true alphabet (StandardSymbolsPS.otf, cmsy10.ttf upper; NotoSerifDisplay-Italic.ttf lower).
        self.assertEqual(self.f["counts"]["test"], {"latin-upper": 13, "latin-lower": 11, "digits": 17})

    # ---- R30 (edit: Claude (Opus 5.5), 2026-09-26 11:20 +0400): the graded tape died on (C, StandardSymbolsPS.otf) ----
    def test_r30_excludes_exactly_the_measured_fonts(self) -> None:
        self.assertEqual(self.f["excluded_r30"], {
            "latin-upper": {"incomplete": {"StandardSymbolsPS.otf": "CDFUV", "cmsy10.ttf": "Y"},
                            "misnamed": ["StandardSymbolsPS.otf"]},
            "latin-lower": {"incomplete": {"NotoSerifDisplay-Italic.ttf": "y"}, "misnamed": []},
            "digits": {"incomplete": {}, "misnamed": []}})

    def test_every_test_pair_is_in_the_pool(self) -> None:
        """The property whose absence crashed the tape: every (character, TEST font) pair the schedule can form exists."""
        from brain.world.glyphs import GlyphLibrary
        for s in fonts.SCRIPTS:
            lib = GlyphLibrary(s)
            holes = [(c, f) for f in self.f["test"][s] for c in fonts.SCRIPT_CHARS[s] if not lib.has(c, f)]
            self.assertEqual(holes, [], f"{s}: TEST pairs missing from the base-32 pool")

    def test_the_pre_r30_rule_had_holes(self) -> None:
        """Negative control: the rule before R30 (holdout − train − tower) DID admit pairs missing from the pool, so the
        test above can fail — it is not true of every font list by construction."""
        from brain.world.glyphs import GlyphLibrary
        lib = GlyphLibrary("latin-upper")
        old = set(self.f["test"]["latin-upper"]) | set(self.f["excluded_r30"]["latin-upper"]["incomplete"])
        self.assertTrue(any(not lib.has(c, f) for f in old for c in fonts.SCRIPT_CHARS["latin-upper"]))

    def test_validate_refuses_a_planted_symbol_font(self) -> None:
        corrupt = copy.deepcopy(self.f)
        corrupt["test"]["latin-upper"] = corrupt["test"]["latin-upper"] + ["StandardSymbolsPS.otf"]
        with self.assertRaises(fonts.FontsError):
            fonts.validate(corrupt)

    def test_validate_refuses_a_planted_incomplete_font(self) -> None:
        corrupt = copy.deepcopy(self.f)
        corrupt["test"]["latin-lower"] = corrupt["test"]["latin-lower"] + ["NotoSerifDisplay-Italic.ttf"]
        with self.assertRaises(fonts.FontsError):
            fonts.validate(corrupt)


    def test_confound_counts_match_prereg(self) -> None:
        self.assertEqual(self.f["counts"]["confound"], {"latin-upper": 6, "latin-lower": 4, "digits": 5})

    def test_clean_in_both_cases(self) -> None:
        clean_both = sorted(set(self.f["test"]["latin-upper"]) & set(self.f["test"]["latin-lower"]))
        self.assertEqual(clean_both, ["NimbusRoman-Bold.otf", "NotoSansCJK-Bold.ttc", "P052-Roman.otf",
                                       "URWBookman-DemiItalic.otf"])

    def test_clean_in_all_three(self) -> None:
        clean_all = sorted(set(self.f["test"]["latin-upper"]) & set(self.f["test"]["latin-lower"]) &
                            set(self.f["test"]["digits"]))
        self.assertEqual(clean_all, ["P052-Roman.otf"])

    def test_tower_training_fonts_count(self) -> None:
        self.assertEqual(len(self.f["tower_training_fonts"]), 20)

    def test_test_sets_disjoint_from_teach_and_tower(self) -> None:
        teach = set(self.f["teach"])
        tower = set(self.f["tower_training_fonts"])
        for s in fonts.SCRIPTS:
            test_s = set(self.f["test"][s])
            self.assertFalse(test_s & teach, f"{s}: TEST overlaps TEACH")
            self.assertFalse(test_s & tower, f"{s}: TEST overlaps the tower's training fonts")

    def test_validate_accepts_the_real_computation(self) -> None:
        fonts.validate(self.f)   # must not raise

    def test_validate_refuses_a_planted_tower_font_in_test(self) -> None:
        """§2.2's own test: "a planted font (a tower-training font inserted into the TEST set) must be
        refused"."""
        corrupt = copy.deepcopy(self.f)
        planted = sorted(self.f["tower_training_fonts"])[0]
        corrupt["test"]["latin-upper"] = corrupt["test"]["latin-upper"] + [planted]
        with self.assertRaises(fonts.FontsError):
            fonts.validate(corrupt)

    def test_validate_refuses_a_planted_teach_font_in_test(self) -> None:
        corrupt = copy.deepcopy(self.f)
        planted = self.f["teach"][0]
        corrupt["test"]["digits"] = corrupt["test"]["digits"] + [planted]
        with self.assertRaises(fonts.FontsError):
            fonts.validate(corrupt)


class TestMisnamedDerivation(unittest.TestCase):
    """R30 (ii) derived from the font files (fontTools: /usr/bin/python3 has it; the brain venv skips)."""

    @classmethod
    def setUpClass(cls) -> None:
        try:
            import fontTools  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("fontTools not importable in this interpreter")
        import csv
        rows = csv.DictReader((fonts.GLYPH_ROOT / "latin-upper" / "fonts.tsv").open(encoding="utf-8"), delimiter="\t")
        cls.paths = {r["font"]: r["path"] for r in rows}

    def test_symbol_font_is_flagged_with_greek_names(self) -> None:
        d = fonts.misnamed_fonts("latin-upper", ["StandardSymbolsPS.otf"], self.paths)
        self.assertIn("StandardSymbolsPS.otf", d)
        self.assertIn("A->Alpha", d["StandardSymbolsPS.otf"])

    def test_calligraphic_and_cid_fonts_pass(self) -> None:
        """Positive controls: a calligraphic font whose glyphs are named for their letters (cmsy10), a blackboard font
        (msbm10) and a CID-keyed font (NotoSansCJK-Bold.ttc, unnamed glyphs) are NOT flagged."""
        d = fonts.misnamed_fonts("latin-upper", ["cmsy10.ttf", "msbm10.ttf", "NotoSansCJK-Bold.ttc"], self.paths)
        self.assertEqual(d, {})

    def test_compute_checked_the_pin(self) -> None:
        self.assertTrue(fonts.compute()["misnamed_checked_by_fonttools"])


if __name__ == "__main__":
    unittest.main()
