# edit: Claude (Sonnet 5, builder H), 2026-09-21 18:44 +0400 — G5-H-MODULATION-BARS-W32B: tests for
# tools/verdict_g4.py's `_regime_calibration` and `modulation()`'s regime-derived reading (§18 addendum 3).
# Synthetic `mind` rows only (no replay, no root) — deterministic, no randomness, so every number here is
# hand-traceable. The moment format matches the reader's own `win = lambda r: int(r["moment"][1:5])`
# (`w<window 4-digit><anything>`), copied from a real journal row (`w0000i000001t000000000`).
from __future__ import annotations

import random
import unittest

import numpy as np

from tools import verdict_g4


def _row(seq: int, window: int, word: str, err: float) -> dict:
    return {"seq": seq, "moment": f"w{window:04d}i{seq:06d}t{seq:09d}", "word": word, "err": err}


def _jitter(seq: int, scale: float) -> float:
    """A deterministic (fixed-seed-per-row), continuous-valued perturbation — real err series never repeat
    an exact float, and a perfectly periodic synthetic pattern produces exact ties at a percentile boundary
    that no real tape would ever hit (np.percentile picks one of several tied values, and a strict `<` around
    that exact tie is a coin flip). Deterministic so the test is still fully reproducible."""
    return random.Random(seq).uniform(-scale, scale)


class TestRegimeCalibration(unittest.TestCase):
    def test_settle_bar_is_the_95th_percentile_of_window0s_own_noise_excluding_bootstrap(self):
        # 10 things cycling through window 0, 100 rounds (1000 rows). Every thing's own FIRST 3 showings
        # are a bootstrap transient at err=1.0 (excluded by settle_skip=3 by construction); every showing
        # after that cycles through a fixed 10-value noise pattern, so the steady-state noise population is
        # exactly that pattern repeated ~97 times per thing — its 95th percentile is computable independently.
        pattern = [0.014, 0.015, 0.016, 0.017, 0.018, 0.016, 0.015, 0.014, 0.019, 0.026]
        things = [f"c{i}" for i in range(10)]
        mind = []
        seq = 0
        counts = {t: 0 for t in things}
        for rnd in range(100):
            for t in things:
                seq += 1
                counts[t] += 1
                if counts[t] <= 3:
                    err = 1.0  # bootstrap transient, must be excluded from the noise sample
                else:
                    err = pattern[(counts[t] - 4) % len(pattern)]
                mind.append(_row(seq, 0, t, err))
        reg = verdict_g4._regime_calibration(mind, settle_skip=3)
        # independent reference: same exclusion rule, computed here without calling the SUT's own loop shape
        import numpy as np
        ref_noise = []
        c2 = {t: 0 for t in things}
        for r in mind:
            c2[r["word"]] += 1
            if c2[r["word"]] > 3:
                ref_noise.append(r["err"])
        self.assertEqual(reg["settle_noise_n"], len(ref_noise))
        self.assertAlmostEqual(reg["settle_bar_err_95"], float(np.percentile(ref_noise, 95)), places=6)
        # the bootstrap transient (err=1.0) must never leak into the settle bar — the pattern's own max is 0.026
        self.assertLess(reg["settle_bar_err_95"], 0.05)
        self.assertGreater(reg["settle_bar_err_95"], 0.0)

    def test_null_band_sees_a_planted_ratio_and_a_flat_stream_does_not_clear_it(self):
        # Baseline noise at 0.016 throughout window 0 for 9 quiet things; thing "loud" repeats a genuine
        # elevated triple (0.05, 0.05, 0.05 — a real 3-in-a-row elevation, not filtered out by the median)
        # every 10th round from round 20 on, so several fake boundaries land right before an elevation and
        # several don't — a real, non-degenerate distribution of ratios, most ~1.0, some clearly elevated.
        quiet = [f"q{i}" for i in range(9)]
        mind = []
        seq = 0
        for rnd in range(300):
            for t in quiet:
                seq += 1
                mind.append(_row(seq, 0, t, 0.016 + _jitter(seq, 0.0015)))
            seq += 1
            loud_err = 0.05 if (20 <= rnd < 260 and rnd % 10 == 0) else 0.016 + _jitter(seq, 0.0015)
            mind.append(_row(seq, 0, "loud", loud_err))
        reg = verdict_g4._regime_calibration(mind)
        self.assertIsNotNone(reg["null_band_95"])
        self.assertGreater(reg["null_ratio_samples"], 0)
        # the calibration set is (by construction) ~95th-percentile-bounded: the printed share must be high
        self.assertGreaterEqual(reg["null_share_within_band"], 0.80)
        # the band must sit strictly below the planted elevation's own ratio (0.05/0.016 = 3.125x) — otherwise
        # the plant would be indistinguishable from noise, which defeats the point of deriving a band at all
        self.assertLess(reg["null_band_95"], 0.05 / 0.016)
        # and strictly above 1.0 — flat noise (ratio 1.0) must sit inside the band, never at its edge
        self.assertGreater(reg["null_band_95"], 1.0)


class TestModulationRegimeGrading(unittest.TestCase):
    def _baseline_window0(self, n_things: int = 8, rounds: int = 200, bump_p: float = 0.10):
        # A mixture, not a fixed periodic pattern: 90% quiet rows uniform in [0.013, 0.019] (median ~0.016,
        # matching the W3-2b regime's own steady state — E's report §3), 10% genuine bumps in [0.022, 0.028] —
        # real per-canvas noise, not the earlier periodic-pattern draft, whose fixed period (relative to the
        # 8-things/100-canvas boundary step) phase-locked one thing's midpoint sample slightly above the
        # derived band on every seed tried — a real, if narrow, statistical trap the derivation itself must
        # tolerate on a real (non-periodic) tape, but not one this synthetic generator should manufacture.
        things = [f"b{i}" for i in range(n_things)]
        mind = []
        seq = 0
        counts = {t: 0 for t in things}
        for rnd in range(rounds):
            for t in things:
                seq += 1
                counts[t] += 1
                if counts[t] <= 3:
                    err = 1.0
                else:
                    rng = random.Random(seq * 7919 + 13)
                    err = rng.uniform(0.022, 0.028) if rng.random() < bump_p else rng.uniform(0.013, 0.019)
                mind.append(_row(seq, 0, t, err))
        return mind, seq

    def test_planted_spike_is_caught_a_flat_stream_is_not_and_a_bandonly_ratio_needs_both_bars(self):
        mind, seq = self._baseline_window0()
        # calibrate first (as the reader itself does), so the window-1 plants can be placed relative to the
        # SAME band the SUT will compute — no magic numbers hand-copied from a prior run
        F = 0.048
        reg = verdict_g4._regime_calibration(mind)
        band = reg["null_band_95"]
        self.assertIsNotNone(band)
        self.assertLess(band, 3.0, "the test needs headroom between the derived band and the fixed 3x bar")
        # window 1: three new things, 12 showings each (so a 10th showing exists). last50_med is computed
        # EXACTLY as modulation()'s own grading loop computes it (median of the last 50 mind rows before the
        # boundary) — never hand-typed, so the test cannot silently drift from the SUT's own arithmetic.
        last50_med = float(np.median([r["err"] for r in mind[-50:]]))
        spike_err = last50_med * 10.0     # ratio ~10x — clears both the fixed 3x bar and the band easily
        flat_err = last50_med * 1.1       # ratio ~1.1x — clears neither
        tight_ratio = (band + 3.0) / 2.0  # strictly between the band and the fixed 3x bar
        tight_err = last50_med * tight_ratio
        w1 = seq
        for t, err, settle_err in (("spike_thing", spike_err, 0.001), ("flat_thing", flat_err, flat_err), ("tight_thing", tight_err, tight_err)):
            for showing in range(12):
                w1 += 1
                e = err if showing < 3 else (settle_err if showing >= 9 else err)
                mind.append(_row(w1, 1, t, e))
        M = verdict_g4.modulation({"mind": mind}, F)
        pt = M["windows"]["1"]["per_thing"]
        self.assertTrue(pt["spike_thing"]["spike_regime"], pt["spike_thing"])
        self.assertTrue(pt["spike_thing"]["spike"])
        self.assertFalse(pt["flat_thing"]["spike_regime"], pt["flat_thing"])
        self.assertFalse(pt["flat_thing"]["spike"])
        # tight_thing clears the regime band but NOT the fixed 3x bar — "must exceed BOTH" means it still misses
        self.assertGreaterEqual(pt["tight_thing"]["spike_ratio"], band)
        self.assertLess(pt["tight_thing"]["spike_ratio"], 3.0)
        self.assertFalse(pt["tight_thing"]["spike_regime"], "a ratio that clears only the band, not the fixed 3x bar, must not count as a spike")
        self.assertFalse(pt["tight_thing"]["spike"])
        # the spike thing settles to near-zero by its 10th showing -> must pass under BOTH readings
        self.assertTrue(pt["spike_thing"]["settled_regime"])
        self.assertTrue(pt["spike_thing"]["settled"])
        self.assertIsNotNone(pt["spike_thing"]["first_settle_showing_regime"])

    def test_regime_settle_bar_admits_natural_noise_the_fixed_ratio_bar_refuses(self):
        # The core defect this brief exists to fix: when last50_med collapses near-zero, 1.25x of it is a
        # razor's edge a single glance's own noise can trip, while the life's OWN observed noise spread (the
        # regime settle bar) correctly admits it. Construct a 10th-showing error that sits strictly between
        # the fixed bar (1.25 * last50_med) and the regime bar (the 95th percentile of real noise, which by
        # construction of _baseline_window0's pattern reaches as high as 0.024/0.02).
        mind, seq = self._baseline_window0()
        F = 0.048
        reg = verdict_g4._regime_calibration(mind)
        last50_med = float(np.median([r["err"] for r in mind[-50:]]))
        fixed_bar = 1.25 * last50_med
        settle_bar = reg["settle_bar_err_95"]
        self.assertGreater(settle_bar, fixed_bar, "the test needs a real gap between the two bars to be meaningful")
        tenth_err = (fixed_bar + settle_bar) / 2.0
        w1 = seq
        spike_err = last50_med * 10.0
        for showing in range(12):
            w1 += 1
            e = spike_err if showing < 9 else tenth_err
            mind.append(_row(w1, 1, "edge_thing", e))
        M = verdict_g4.modulation({"mind": mind}, F)
        pt = M["windows"]["1"]["per_thing"]["edge_thing"]
        self.assertFalse(pt["settled"], "must MISS the fixed §16 bar")
        self.assertTrue(pt["settled_regime"], "must PASS the regime-derived bar")

    def test_no_window_change_yet_is_not_gradable_but_the_band_is_still_printed(self):
        mind, _ = self._baseline_window0(rounds=250)
        F = 0.048
        M = verdict_g4.modulation({"mind": mind}, F)
        self.assertEqual(M["windows"], {})
        self.assertFalse(M["pass"])
        self.assertFalse(M["pass_fixed_bars_record"])
        self.assertIn("reason", M)
        self.assertIn("not gradable", M["reason"])
        self.assertIsNotNone(M["regime"]["null_band_95"])
        self.assertIsNotNone(M["regime"]["settle_bar_err_95"])

    def test_pass_and_pass_fixed_bars_record_are_independent_fields(self):
        # a life whose window-1 things all spike hugely and settle to near-zero must PASS both readings —
        # proving pass/pass_fixed_bars_record are not just always-equal aliases of one boolean.
        mind, seq = self._baseline_window0()
        F = 0.048
        last50_med = float(np.median([r["err"] for r in mind[-50:]]))
        w1 = seq
        for t in ("t0", "t1", "t2"):
            for showing in range(12):
                w1 += 1
                e = last50_med * 20.0 if showing < 3 else (0.0005 if showing >= 9 else last50_med * 20.0)
                mind.append(_row(w1, 1, t, e))
        M = verdict_g4.modulation({"mind": mind}, F)
        self.assertTrue(M["pass"], M)
        self.assertTrue(M["pass_fixed_bars_record"], M)


if __name__ == "__main__":
    unittest.main()
