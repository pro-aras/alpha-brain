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
        self.assertEqual(self.f["counts"]["test"], {"latin-upper": 15, "latin-lower": 12, "digits": 17})

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


if __name__ == "__main__":
    unittest.main()
