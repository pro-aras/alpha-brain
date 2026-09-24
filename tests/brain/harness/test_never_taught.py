# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 19:0x +0400 — tests for brain/harness/never_taught.py.
# Real never-taught glyphs (hebrew/arabic/devanagari/greek) through the real organs. Must run under
# /usr/bin/python3.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from brain.harness.ceilings import between_class_p95, teach_exemplars_pool
from brain.harness.never_taught import (
    MIN_PLANT_FONTS, NeverTaughtError, PLANT_N, U2_N, U5_N, U6_REFUSAL_N, candidate_pool, select_pools,
)
from brain.world import fonts

SEED = 20261001


class TestNeverTaughtPool(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self._tmp.name) / "cache"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_candidate_pool_on_real_data(self) -> None:
        teach_X, teach_y = teach_exemplars_pool("latin-upper", list("ABCDEFGHIJ"), fonts.TEACH_FONTS_ORDER[:2],
                                                 SEED, self.cache_dir / "teach")
        theta = between_class_p95(teach_X, teach_y)
        kept = candidate_pool(teach_X, theta, SEED, self.cache_dir / "nt")
        # every never-taught script should contribute at least one row to the raw candidate scan
        self.assertGreater(len(kept), 0)
        for c in kept:
            self.assertLess(c["max_cos_to_teach"], theta)
            self.assertIn(c["script"], ("hebrew", "arabic", "devanagari", "greek"))

    def test_select_pools_disjoint_and_sized(self) -> None:
        # a synthetic "kept" pool large enough to avoid the shrink branch, with a few plant-eligible entries.
        kept = []
        for i in range(70):
            kept.append({"script": "greek", "char": chr(0x3B1 + (i % 24)), "font": f"font{i}",
                         "max_cos_to_teach": 0.1, "n_fonts_available": 15 if i < 5 else 3})
        pools = select_pools(kept, SEED)
        self.assertEqual(pools["counts"], {"u2": U2_N, "u6_refusal": U6_REFUSAL_N, "u5": U5_N, "plant": 1})
        all_ids = [id(pools["plant"])] + [id(x) for x in pools["u2"]] + [id(x) for x in pools["u6_refusal"]] + [id(x) for x in pools["u5_after_never_taught"]]
        self.assertEqual(len(all_ids), len(set(all_ids)), "the four sub-pools are not disjoint")
        self.assertGreaterEqual(pools["plant"]["n_fonts_available"], MIN_PLANT_FONTS)

    def test_select_pools_raises_when_too_small(self) -> None:
        kept = [{"script": "greek", "char": "a", "font": "f", "max_cos_to_teach": 0.1, "n_fonts_available": 2}]
        with self.assertRaises(NeverTaughtError):
            select_pools(kept, SEED)

    def test_select_pools_deterministic(self) -> None:
        kept = [{"script": "greek", "char": chr(0x3B1 + i), "font": f"f{i}", "max_cos_to_teach": 0.1,
                 "n_fonts_available": 15 if i < 3 else 5} for i in range(65)]
        p1 = select_pools(kept, SEED)
        p2 = select_pools(kept, SEED)
        self.assertEqual([c["char"] for c in p1["u2"]], [c["char"] for c in p2["u2"]])
        self.assertEqual(p1["plant"]["char"], p2["plant"]["char"])


if __name__ == "__main__":
    unittest.main()
