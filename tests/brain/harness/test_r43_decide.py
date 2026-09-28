# edit: Claude (Opus 5.5), 2026-09-27 09:58 +0400 — R43's reading of R42's second fire (SEAT-DECISIONS R43, declared before any second fire): after a
# LOWER-BOUND fire, a twin is VOID by cost the moment cpu ÷ pred_k exceeds 4.32 (216,000 ÷ 50,000) before its sleep closes; a close
# reads r_k = cpu at the close ÷ pred_k — r ≤ 4.32 re-prices to ⌊216,000 ÷ r⌋ (to a thousand), r > 4.32 is VOID; before either,
# WAIT. On planted numbers, never a live run.
from __future__ import annotations

import unittest

from tools.b1.r43_decide import FIRE_R, FLOOR_R, decide


class TestR43Decide(unittest.TestCase):
    def test_the_two_constants(self) -> None:
        self.assertAlmostEqual(FIRE_R, 4.0747, places=4)        # R43: 24 ÷ 5.89, as the watch reads the budget
        self.assertAlmostEqual(FLOOR_R, 4.32)

    def test_wait_while_the_lower_bound_is_under_the_floor(self) -> None:
        self.assertEqual(decide(cpu_h=13.5, pred_k_h=3.259, closed_cpu_h=None)["action"], "WAIT")

    def test_void_as_soon_as_the_lower_bound_passes_the_floor(self) -> None:
        d = decide(cpu_h=14.2, pred_k_h=3.259, closed_cpu_h=None)
        self.assertEqual(d["action"], "VOID")
        self.assertGreater(d["r"], 4.32)

    def test_a_close_under_the_floor_reprices(self) -> None:
        d = decide(cpu_h=13.9, pred_k_h=3.259, closed_cpu_h=13.8)       # r = 4.234
        self.assertEqual(d["action"], "REPRICE")
        self.assertEqual(d["n_new"], 51000)                                # ⌊216,000 ÷ 4.2344⌋ = 51,010 → 51,000

    def test_a_close_over_the_floor_is_void(self) -> None:
        self.assertEqual(decide(cpu_h=14.5, pred_k_h=3.259, closed_cpu_h=14.3)["action"], "VOID")


if __name__ == "__main__":
    unittest.main()
