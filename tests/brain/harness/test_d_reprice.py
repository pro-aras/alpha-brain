# edit: Claude (Opus 5.5), 2026-09-26 19:31 +0400 — the projection rule's re-price (B1-PREREG §12): N' = ⌊N ÷ r⌋ rounded down to a thousand,
# the curve scaled by N'/N, the old budget and the firing reading kept; a ratio ≤ 1 is refused (a re-price only lowers).
from __future__ import annotations

import unittest

from tools.b1.d_reprice import reprice

B = {"candidates_per_sleep": 703000, "predicted_total_cpu_h": 19.18,
     "predicted_cum_cpu_s": {"4": 2744.6, "5": 4806.8, "17": 69055.2}, "margin": 0.8}
READING = {"search": "20261001/SHUFFLED-RELATION_D", "sleep": 5, "cpu_h": 1.8, "at": "t"}


class TestReprice(unittest.TestCase):
    def test_the_number_and_curve_scale_by_the_ratio(self) -> None:
        out = reprice(B, 1.35, READING)
        self.assertEqual(out["candidates_per_sleep"], 520000)          # ⌊703,000 / 1.35⌋ = 520,740 → 520,000
        scale = 520000 / 703000
        self.assertAlmostEqual(out["predicted_total_cpu_h"], round(19.18 * scale, 2))
        self.assertAlmostEqual(out["predicted_cum_cpu_s"]["5"], round(4806.8 * scale, 1))
        self.assertLessEqual(out["predicted_total_cpu_h"] * 1.35, 24.0)  # the fired search predicted back under the allowance

    def test_the_old_budget_and_the_reading_are_kept(self) -> None:
        out = reprice(B, 1.35, READING)
        last = out["repriced"][-1]
        self.assertEqual(last["from"]["candidates_per_sleep"], 703000)
        self.assertEqual(last["reading"]["search"], READING["search"])
        self.assertEqual(B["candidates_per_sleep"], 703000)            # the input is never mutated

    def test_a_ratio_at_or_below_one_is_refused(self) -> None:
        for r in (1.0, 0.8):
            with self.assertRaises(ValueError):
                reprice(B, r, READING)


if __name__ == "__main__":
    unittest.main()
