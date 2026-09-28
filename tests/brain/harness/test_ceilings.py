# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 18:5x +0400 — tests for brain/harness/ceilings.py: real
# glyphs through the real pinned organs, but a TINY subset (fast). Must run under /usr/bin/python3.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from brain.harness.ceilings import (
    CeilingsError, between_class_p95, family_relation_ceiling, label_conflicts, naming_ceiling,
    other_case_removed_pairs, relation_ceiling, teach_exemplars_pool,
)
from brain.world import fonts

SEED = 20261001


class TestLabelConflicts(unittest.TestCase):
    def test_finds_a_20pct_confusion(self) -> None:
        # "a" confused as "b" in 2 of 5 (40%) -> a conflict; "c" never confused -> none.
        pred = ["a", "b", "a", "a", "a", "c", "c", "c"]
        truth = ["a", "a", "a", "a", "a", "c", "c", "c"]
        self.assertEqual(label_conflicts(pred, truth, threshold=0.20), {("a", "b")})

    def test_below_threshold_not_flagged(self) -> None:
        pred = ["a"] * 9 + ["b"]
        truth = ["a"] * 10
        self.assertEqual(label_conflicts(pred, truth, threshold=0.20), set())


class TestRelationCeiling(unittest.TestCase):
    def test_product_over_operands(self) -> None:
        acc = {"a": 0.8, "b": 0.5}
        self.assertAlmostEqual(relation_ceiling(["a", "b"], acc), 0.4)

    def test_pick_factor(self) -> None:
        acc = {"a": 0.8}
        self.assertAlmostEqual(relation_ceiling(["a"], acc, is_pick=True, pick_accuracy=0.5), 0.4)

    def test_family_mean(self) -> None:
        acc = {"a": 1.0, "b": 0.0}
        self.assertAlmostEqual(family_relation_ceiling([["a"], ["b"]], acc), 0.5)


class TestBetweenClassP95(unittest.TestCase):
    def test_raises_with_one_class(self) -> None:
        X = np.eye(3)
        with self.assertRaises(CeilingsError):
            between_class_p95(X, ["a", "a", "a"])

    def test_reasonable_value_for_orthogonal_classes(self) -> None:
        X = np.eye(4)
        p95 = between_class_p95(X, ["a", "b", "c", "d"])
        self.assertAlmostEqual(p95, 0.0, places=8)   # orthonormal vectors -> all between-class cos are 0


class TestNamingCeilingSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self._tmp.name) / "cache"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_naming_ceiling_on_a_tiny_real_subset(self) -> None:
        chars = list("ABCDEFGH")   # 8 letters, enough classes for a meaningful fit
        teach_fonts = fonts.TEACH_FONTS_ORDER
        test_fonts = fonts.compute()["test"]["latin-upper"][:3]
        result = naming_ceiling("latin-upper", chars, teach_fonts, test_fonts, SEED, self.cache_dir,
                                 n_teach_variants=(4,), n_perm=5)
        self.assertIn("4", result)
        oc = result["4"]["organ_ceiling"]
        self.assertGreaterEqual(oc["max"], oc["nn"] - 1e-9)
        self.assertGreaterEqual(oc["max"], oc["linear"] - 1e-9)
        self.assertGreater(oc["max"], 0.5, "8-way naming with real fonts through the real tower should beat chance")
        self.assertEqual(result["4"]["n_train"], len(chars) * len(teach_fonts))

    def test_per_name_accuracy_is_not_uniform_across_names(self) -> None:
        """The advisor's review (2026-09-24): a uniform aggregate accuracy across every name is
        structurally wrong once OTHER_CASE and other per-letter uses need it — per_name_accuracy must be a
        REAL per-item breakdown, not the aggregate repeated for every key."""
        chars = list("ABCDEFGHIJ")
        teach_fonts = fonts.TEACH_FONTS_ORDER
        test_fonts = fonts.compute()["test"]["latin-upper"][:4]
        result = naming_ceiling("latin-upper", chars, teach_fonts, test_fonts, SEED, self.cache_dir,
                                 n_teach_variants=(4,), n_perm=3)
        per_name = result["4"]["per_name_accuracy"]
        self.assertEqual(set(per_name), {c.lower() for c in chars})
        for v in per_name.values():
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)
        # a real per-item breakdown over only 4 test fonts almost never lands on the exact same float for
        # every one of 10 classes — the uniform-aggregate bug this test guards against would fail this.
        self.assertGreater(len(set(per_name.values())), 1, per_name)


class TestOtherCaseRemoval(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self._tmp.name) / "cache"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_runs_on_a_tiny_letter_set_and_returns_cosines(self) -> None:
        letters = ["c", "a", "s"]   # c/C and s/S are the library's own likely near-identical-case examples
        teach_X, teach_y = teach_exemplars_pool("latin-upper", list("ABCDEFGHIJ"), fonts.TEACH_FONTS_ORDER[:1],
                                                 SEED, self.cache_dir / "teach")
        theta = between_class_p95(teach_X, teach_y)
        removed = other_case_removed_pairs("latin-upper", "latin-lower", letters, fonts.TEACH_FONTS_ORDER[0],
                                            SEED, self.cache_dir / "oc", theta)
        for r in removed:
            self.assertIn(r["letter"], letters)
            self.assertGreater(r["cosine"], theta)


if __name__ == "__main__":
    unittest.main()


class TestPerceptualCeilingsWalkTheFullRunPath(unittest.TestCase):
    """edit: Claude (Fable 5.1), 2026-09-24 19:03 +0400 — the perceptual ceilings (MIRROR/LOOP's `binary_perceptual_ceiling`,
    `vowel_ceiling`) were skipped at --smoke and never called by any test: the FULL stage −1 died on 2026-09-24
    19:0x at a wrong relative import inside them (`from .seeds …` in brain/harness — #173's class, a green suite
    that never loads the road). This walks both at a tiny scale (two forms, two fonts) under the real organs."""

    def test_binary_and_vowel_ceilings_run_at_smoke_scale(self) -> None:
        import os
        import tempfile
        from pathlib import Path
        from brain.harness.ceilings import binary_perceptual_ceiling, vowel_ceiling
        from brain.world import fonts
        tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"), prefix="ceil-perc-")
        cache = Path(tmp.name)
        teach = fonts.TEACH_FONTS_ORDER[:2]
        f = fonts.compute()
        test_by_case = {"latin-upper": f["test"]["latin-upper"][:2], "latin-lower": f["test"]["latin-lower"][:2]}
        pos_t, neg_t = [("latin-upper", "A"), ("latin-upper", "H")], [("latin-upper", "F"), ("latin-lower", "g")]
        pos_h, neg_h = [("latin-upper", "M")], [("latin-lower", "r")]
        r = binary_perceptual_ceiling(pos_t, neg_t, pos_h, neg_h, teach, test_by_case, 20261001, cache / "mirror", "mirror")
        self.assertIn("accuracy", r)
        self.assertEqual(r["n"], 2)
        v = vowel_ceiling([("latin-upper", "A"), ("latin-lower", "e")], [("latin-upper", "B"), ("latin-lower", "r"), ("latin-upper", "T")],
                          [("latin-upper", "B"), ("latin-lower", "r")], teach, test_by_case, 20261001, cache / "vowel")
        self.assertIn("accuracy", v)
        self.assertGreater(v["n"], 0)
        tmp.cleanup()
