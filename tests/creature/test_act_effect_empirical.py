# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 12:00 +0400 — PREREG-ACT-EFFECT RESULT instrument (the architect's order, 11:5x): the EMPIRICAL ceilings of M2/M3/M4 — the same screen on forward's effect process
# BLOCK-BOOTSTRAPPED from the world's own recorded series (fixed random-3 play, NO candidate run), beside the iid ceilings the signed law used. Tests first; each instrument carries a planted control:
#   - the bootstrap keeps RUNS (a series of runs of exactly 10 re-sampled in blocks of 40 keeps ~95 % of adjacent pairs equal; iid would keep 50 %);
#   - on an IID input the empirical instrument reproduces the exact closed form (the cross-check), so any gap on the real series is the series' clustering, not the simulator;
#   - a PLANTED clustered series (long blocked runs, the SAME marginal rate) must read a much larger dead-time than iid (caught), a constant series reads zero.
from __future__ import annotations

import math
import unittest

import numpy as np

from tools.toys import act_effect_empirical as E


def _cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _exact_dead_time(n, k, p, lam_a=0.9 / 3 + 0.1 / 7, lam_d=0.1 / 7):
    pd = _cdf(k - 1, n, p)
    return (pd / lam_d) / (pd / lam_d + (1 - pd) / lam_a)


class TestBootStream(unittest.TestCase):
    def test_blocks_keep_the_runs(self) -> None:
        series = ([0] * 10 + [1] * 10) * 40                     # runs of exactly 10
        s = E.BootStream([series], block=40, rng=np.random.default_rng(1))
        x = [s.next() for _ in range(20_000)]
        same = sum(1 for a, b in zip(x, x[1:]) if a == b) / (len(x) - 1)
        # runs of 10 in blocks of 40: ~3-4 transitions per block of 39 adjacent pairs (+ one coin-flip pair at each join) -> ~0.90 expected; iid keeps 0.5
        self.assertGreater(same, 0.85, "the runs survive the bootstrap (iid would keep 0.5)")
        self.assertLess(same, 0.97)

    def test_values_come_only_from_the_series(self) -> None:
        s = E.BootStream([[1, 1, 0, 1]], block=3, rng=np.random.default_rng(2))
        self.assertTrue(all(s.next() in (0, 1) for _ in range(1000)))

    def test_a_block_longer_than_the_series_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            E.BootStream([[1, 0, 1]], block=10, rng=np.random.default_rng(3))

    def test_the_marginal_rate_is_kept(self) -> None:
        series = [1] * 568 + [0] * 432
        s = E.BootStream([series], block=100, rng=np.random.default_rng(4))
        x = [s.next() for _ in range(50_000)]
        self.assertAlmostEqual(sum(x) / len(x), 0.568, delta=0.02)


class TestSimulatorAgreesWithTheExactInstrument(unittest.TestCase):
    def test_on_iid_input_the_dead_time_matches_the_closed_form(self) -> None:
        """The cross-check: the empirical instrument fed an IID Bernoulli series reproduces the renewal closed form (forward at 0.5: 2.76 %)."""
        rng = np.random.default_rng(10)
        series = [int(x) for x in (rng.random(20_000) < 0.5)]
        got = []
        for r in range(6):
            res = E.simulate_lives(forward=[series], noops=None, lives=60, acts=3000, block=200, seed=100 + r)
            got.append(res["forward_dead_time"])
        m = float(np.mean(got))
        se = float(np.std(got, ddof=1) / math.sqrt(len(got)))
        exact = _exact_dead_time(20, 4, 0.5)
        self.assertLess(abs(m - exact), 4 * se + 0.004, f"simulated {m:.4f} ± {se:.4f} vs exact {exact:.4f}")

    def test_a_constant_series_reads_zero_dead_time(self) -> None:
        res = E.simulate_lives(forward=[[1] * 500], noops=None, lives=20, acts=2000, block=100, seed=5)
        self.assertEqual(res["forward_dead_time"], 0.0)

    def test_the_planted_clustered_series_is_caught(self) -> None:
        """Same marginal rate (0.5), but the blocked outcomes come in runs of 40: the dead-time must be many times the iid reading."""
        clustered = ([0] * 40 + [1] * 40) * 60
        iid = [int(x) for x in (np.random.default_rng(6).random(4800) < 0.5)]
        a = np.mean([E.simulate_lives(forward=[clustered], noops=None, lives=40, acts=3000, block=160, seed=200 + r)["forward_dead_time"] for r in range(3)])
        b = np.mean([E.simulate_lives(forward=[iid], noops=None, lives=40, acts=3000, block=160, seed=300 + r)["forward_dead_time"] for r in range(3)])
        self.assertGreater(a, 3 * b, f"clustered {a:.4f} vs iid {b:.4f}")
        self.assertGreater(a, 0.05)
        self.assertNotEqual(sum(clustered), 0)          # the plant changed the bytes (it is not the all-ones control)


class TestMarkCeilings(unittest.TestCase):
    def test_a_result_row_names_every_mark_it_prices(self) -> None:
        series = [int(x) for x in (np.random.default_rng(7).random(6000) < 0.57)]
        res = E.simulate_lives(forward=[series], noops=None, lives=20, acts=1500, block=100, seed=9)
        for k in ("forward_dead_time", "m2_pass_960", "m2_pass_1500", "m3_pass", "m4a_pass", "m4b_pass", "m4b_median", "forward_share", "noop_share", "lives"):
            self.assertIn(k, res)
        self.assertEqual(res["lives"], 20)

    def test_the_lock_detector_is_the_signed_one(self) -> None:
        """The simulator's M2 reading is the toy's `lock_pass` (two best acts >= 0.9 in <= 2 % of windows), not a re-derivation."""
        from tools.toys import act_chooser_toy as toy
        self.assertIs(E.lock_pass, toy.lock_pass)
        self.assertIs(E.noop_share, toy.noop_share)
        self.assertIs(E.m4_readings, toy.m4_readings)


if __name__ == "__main__":
    unittest.main()
