# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:08 +0400 — PREREG-EVOLVE-CAL §1 (the bands) + A1 (i), A2.2, A4, A7: tests FIRST for the calibration's arithmetic.
"""tests/tools/test_evolve_cal_bands_build.py — building a BANDS file from a merit-neutral null (tools/evolve_cal.py, scipy).

The law (A4): σ̂ is estimated from the 21 values of a dimension on S1 (the incumbent + 20 twins, 20 df); the production Δ is a difference of
TWO draws, so under no merit difference it is centred at 0 with σ_Δ = √2 · σ̂, and the band edge is t(20, 1 − 0.0083) · σ_Δ = 2.614 · σ_Δ ≈ 3.70 σ̂.
A dimension whose null holds fewer than 3 distinct values or σ̂ = 0 has NO band (A1 (i)). A null that is not normal at p < 0.01 (Shapiro–Wilk)
uses its rank band, «outside all draws»: the range of the null's readings (A4 (iii)). Integer readings carry their grid. A2.2: for frames_filed the seed
twins' σ̂ is printed beside the ε null's and RULES only where it is larger by an F-test at p < 0.05. A7: N2's transfer test is an F-test on two variances,
two-sided 0.05.
"""
from __future__ import annotations

import math
import statistics
import unittest

import numpy as np

import tools.evolve_bands as eb
import tools.evolve_cal as cal

T_20 = 2.6144354208011977      # scipy.stats.t.ppf(1 - 0.0083, 20), the law's «2.6144»


def ints(*vals):
    return [float(v) for v in vals]


NORMALISH = ints(100, 102, 99, 101, 100, 98, 103, 101, 100, 99, 102, 100, 101, 99, 100, 102, 98, 101, 100, 99, 101)   # n = 21


class TestMakeBand(unittest.TestCase):
    def test_a_normal_null_gives_the_t_times_root_two_times_sigma_edge(self) -> None:
        b = cal.make_band("frames_filed", NORMALISH, grid=1.0)
        sigma = statistics.stdev(NORMALISH)
        self.assertEqual(b["kind"], "normal")
        self.assertEqual((b["n"], b["df"], b["distinct"]), (21, 20, len(set(NORMALISH))))
        self.assertAlmostEqual(b["sigma_hat"], sigma, places=12)
        self.assertAlmostEqual(b["t"], T_20, places=9)
        self.assertAlmostEqual(b["edge"], T_20 * math.sqrt(2) * sigma, places=9)
        self.assertAlmostEqual(b["edge"] / sigma, 3.697, places=3, msg="the law's «≈ 3.70 σ̂»")
        self.assertEqual(b["grid"], 1.0)
        self.assertEqual(b["range"], max(NORMALISH) - min(NORMALISH))
        self.assertEqual(b["normality"]["test"], "shapiro")
        self.assertGreaterEqual(b["normality"]["p"], 0.01)

    def test_the_edge_is_printed_in_grid_steps_and_the_steps_a_reading_must_clear(self) -> None:
        vals = [v / 110 for v in NORMALISH]
        b = cal.make_band("q1_seen", vals, grid=1 / 110)
        self.assertAlmostEqual(b["edge_grid"], b["edge"] * 110, places=9)
        self.assertEqual(b["min_clear_grid"], math.floor(round(b["edge_grid"], 9)) + 1)

    def test_a_constant_null_has_no_band_and_says_why(self) -> None:
        b = cal.make_band("q1_seen", [104 / 110] * 21, grid=1 / 110)
        self.assertEqual(b["kind"], "none")
        self.assertEqual(b["distinct"], 1)
        self.assertIn("1 distinct", b["reason"])
        self.assertEqual(eb.position(0.5, b), "no-band")

    def test_fewer_than_three_distinct_values_has_no_band_even_with_spread(self) -> None:
        b = cal.make_band("frames_filed", ints(*([26] * 11 + [27] * 10)), grid=1.0)
        self.assertEqual(b["kind"], "none")
        self.assertEqual(b["distinct"], 2)
        self.assertGreater(b["sigma_hat"], 0)

    def test_a_non_normal_null_uses_the_rank_band_and_says_so(self) -> None:
        vals = ints(*([0] * 10 + [10] * 11))            # bimodal: Shapiro–Wilk rejects far below 0.01 (and 3 distinct values are needed)
        vals[0] = 5.0
        b = cal.make_band("frames_filed", vals, grid=1.0)
        self.assertLess(b["normality"]["p"], 0.01)
        self.assertEqual(b["kind"], "rank")
        self.assertEqual(b["range"], 10.0)
        self.assertIsNone(b["edge"])
        self.assertIn("rank band", b["note"])
        self.assertIn("4.5 %", b["note"], "A4 (iii): the rank band's error at n = 21 is 1/22 per side, so the 0.025 family-wise holds only for the normal band")

    def test_the_n_is_the_number_of_values_and_df_follows(self) -> None:
        b = cal.make_band("confirmed_share", [0.40 + 0.003 * i for i in range(11)] , grid=None)
        self.assertEqual((b["n"], b["df"]), (11, 10))
        from scipy import stats
        self.assertAlmostEqual(b["t"], stats.t.ppf(1 - 0.0083, 10), places=9)

    def test_too_few_values_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            cal.make_band("frames_filed", ints(1, 2), grid=1.0)

    def test_a_none_reading_in_the_null_is_refused_not_dropped(self) -> None:
        with self.assertRaises(ValueError):
            cal.make_band("frames_filed", ints(*([26] * 20)) + [None], grid=1.0)


class TestMakeBands(unittest.TestCase):
    def null(self, **over):
        rng = np.random.default_rng(7)
        d = {"q1_seen": [(104 + int(x)) / 110 for x in np.round(rng.normal(0, 1.5, 21))],
             "frames_filed": [float(26 + int(x)) for x in np.round(rng.normal(0, 3, 21))],
             "confirmed_share": [float(0.45 + x) for x in rng.normal(0, 0.01, 21)],
             "ln_cpu": [float(math.log(2000.0) + x) for x in rng.normal(0, 0.05, 21)]}
        d.update(over)
        return d

    def test_the_bands_file_validates_and_carries_the_laws_fields(self) -> None:
        b = cal.make_bands(self.null(), slice_name="S1", scope="mid-life (S1)")
        eb.validate_bands(b)
        self.assertEqual((b["slice"], b["n"], b["df"], b["alpha_side"], b["cost_policy_cap"]), ("S1", 21, 20, 0.0083, 1.2))
        self.assertEqual(b["dims"]["q1_seen"]["grid"], 1 / 110)
        self.assertEqual(b["dims"]["frames_filed"]["grid"], 1.0)
        self.assertIsNone(b["dims"]["confirmed_share"]["grid"])
        self.assertEqual(b["scope"], "mid-life (S1)")

    def test_a_planted_difference_reads_above_and_a_third_of_it_reads_within(self) -> None:
        b = cal.make_bands(self.null(), slice_name="S1", scope="x")
        e = b["dims"]["confirmed_share"]["edge"]
        self.assertEqual(eb.position(1.6 * e, b["dims"]["confirmed_share"]), "above")
        self.assertEqual(eb.position(-1.6 * e, b["dims"]["confirmed_share"]), "below")
        self.assertEqual(eb.position(0.34 * e, b["dims"]["confirmed_share"]), "within")

    def test_a_dead_dimension_is_written_as_no_band_not_dropped(self) -> None:
        b = cal.make_bands(self.null(q1_seen=[104 / 110] * 21), slice_name="S1", scope="x")
        self.assertEqual(b["dims"]["q1_seen"]["kind"], "none")
        eb.validate_bands(b)

    def test_the_cost_band_is_built_on_the_log_cpu(self) -> None:
        b = cal.make_bands(self.null(), slice_name="S1", scope="x")
        self.assertIn("ln_cpu", b["dims"])
        self.assertIsNone(b["dims"]["ln_cpu"]["grid"])
        self.assertLess(b["dims"]["ln_cpu"]["edge"], 0.5)

    def test_a_missing_gated_dimension_is_refused(self) -> None:
        n = self.null()
        del n["frames_filed"]
        with self.assertRaises(ValueError):
            cal.make_bands(n, slice_name="S1", scope="x")


class TestVarianceRatio(unittest.TestCase):
    def test_equal_spreads_are_not_different(self) -> None:
        # seeds 5 and 6 (seeds 1 and 2 happen to draw variances 0.33 and 1.30, F = 0.26: a 5 % event, not a defect of the test)
        a = [float(x) for x in np.random.default_rng(5).normal(0, 1, 21)]
        b = [float(x) for x in np.random.default_rng(6).normal(0, 1, 11)]
        r = cal.variance_ratio_test(a, b)
        self.assertFalse(r["different"])
        self.assertEqual(r["df"], (20, 10))
        from scipy import stats
        self.assertAlmostEqual(r["f_crit_hi"], stats.f.ppf(0.975, 20, 10), places=9)
        self.assertAlmostEqual(r["f_crit_hi"], 3.4185, places=3, msg="the law's F(0.975) for (20, 10) df")

    def test_the_one_sided_test_uses_the_full_alpha_in_one_tail(self) -> None:
        a = [float(x) for x in np.random.default_rng(5).normal(0, 1, 10)]
        b = [float(x) for x in np.random.default_rng(6).normal(0, 1, 21)]
        r = cal.variance_ratio_test(a, b, alpha=0.05, two_sided=False)
        from scipy import stats
        self.assertAlmostEqual(r["f_crit_hi"], stats.f.ppf(0.95, 9, 20), places=9)
        self.assertFalse(r["two_sided"])
        r2 = cal.variance_ratio_test(a, b, alpha=0.05, two_sided=True)
        self.assertAlmostEqual(r2["f_crit_hi"], stats.f.ppf(0.975, 9, 20), places=9)
        self.assertLess(r["f_crit_hi"], r2["f_crit_hi"])

    def test_a_threefold_spread_is_different_and_the_direction_is_named(self) -> None:
        a = [float(x) for x in np.random.default_rng(1).normal(0, 1, 21)]
        b = [float(x) for x in np.random.default_rng(2).normal(0, 3.5, 11)]
        r = cal.variance_ratio_test(a, b)
        self.assertTrue(r["different"])
        self.assertEqual(r["wider"], "b")
        r2 = cal.variance_ratio_test(b, a)
        self.assertTrue(r2["different"])
        self.assertEqual(r2["wider"], "a")

    def test_a_zero_variance_against_a_spread_is_different_with_a_zero_or_infinite_ratio(self) -> None:
        spread = [4.0, 6.0, 5.0, 7.0, 3.0, 5.0, 6.0, 4.0, 5.0, 5.0]
        r = cal.variance_ratio_test([5.0] * 21, spread)          # F = var_a / var_b
        self.assertTrue(r["different"])
        self.assertEqual(r["wider"], "b")
        self.assertEqual(r["F"], 0.0)
        r2 = cal.variance_ratio_test(spread, [5.0] * 21)
        self.assertTrue(r2["different"])
        self.assertEqual(r2["wider"], "a")
        self.assertTrue(math.isinf(r2["F"]))

    def test_two_zero_variances_are_not_different(self) -> None:
        r = cal.variance_ratio_test([5.0] * 21, [5.0] * 10)
        self.assertFalse(r["different"])
        self.assertIsNone(r["wider"])


class TestFramesBand(unittest.TestCase):
    """A2.2: one band rule for every dimension; for frames_filed the seed twins' σ̂ is printed beside the ε null's and RULES only where larger by an F-test."""

    def test_the_seed_null_rules_only_where_it_is_wider(self) -> None:
        eps = ints(*([26] * 21))                          # the ε twins never moved frames_filed
        seed = ints(24, 28, 27, 25, 29, 26, 22, 30, 26, 27)
        b = cal.frames_band(eps, seed)
        self.assertEqual(b["rules"], "seed")
        self.assertEqual(b["band"]["kind"], "normal")
        self.assertEqual(b["eps"]["sigma_hat"], 0.0)
        self.assertIsNotNone(b["seed"]["sigma_hat"])
        self.assertTrue(b["f_test"]["different"])

    def test_the_eps_null_rules_when_the_seed_null_is_not_wider(self) -> None:
        eps = [float(26 + x) for x in (-3, 2, 0, 1, -2, 3, 0, -1, 2, 1, 0, -2, 1, 0, 2, -1, 1, 0, -3, 2, 0)]
        seed = ints(24, 28, 27, 25, 29, 26, 22, 30, 26, 27)
        b = cal.frames_band(eps, seed)
        self.assertEqual(b["rules"], "eps")
        self.assertEqual(b["band"]["n"], 21)

    def test_without_seed_twins_the_eps_null_stands_and_says_so(self) -> None:
        b = cal.frames_band(ints(*([26] * 21)), None)
        self.assertEqual(b["rules"], "eps")
        self.assertEqual(b["band"]["kind"], "none")


if __name__ == "__main__":
    unittest.main()
