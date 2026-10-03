# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:15 +0400 — PREREG-EVOLVE-CAL AMENDMENT 3 (A3.4, A3.6, A3.7): the N1 analysis, tests FIRST.
"""tests/tools/test_evolve_cal_analyse.py — tools/evolve_cal_analyse.py: from the twins' readings to the null arrays, the staged decisions and the BANDS file.

The staged design (A3.6): Stage A0 (the incumbent + one twin at 1e-3 and one at 1e-2 on the full slice) is NON-DEGENERATE iff at least one epsilon twin's readings
differ from the incumbent's; if neither does, Stage A0+ (four more) reads DEGENERATE iff all six equal the incumbent in every reading (the 95 % upper bound on the per-twin
chance of a reading flip is then 1 − 0.05^(1/6)); Stage B (the other 15 twins at the chosen level) runs only if the chosen level's six values hold >= 3 distinct values in
some gated dimension. A3.4: a twin EQUALS the incumbent iff its journal has no DISCRETE keyed difference and its three readings are equal. A3.7: a degenerate dimension has
NO band (reading A) or the band of its null's own range with a floor of one resolvable step (reading B).
"""
from __future__ import annotations

import math
import unittest

import tools.evolve_bands as eb
import tools.evolve_cal as cal
import tools.evolve_cal_analyse as an


def rd(q1=104, frames=26, share=0.45, cpu=2000.0, **kw):
    r = {"q1_seen": q1 / 110, "frames_filed": frames, "confirmed_share": share, "cpu_s": cpu, "state_hash": "s", "journal_sha256": "j",
         "detail": {"surprise": {"canvases": 1000}}}
    r.update(kw)
    return r


class TestReadingsEqual(unittest.TestCase):
    def test_equal_readings_are_equal_and_any_gated_difference_is_not(self) -> None:
        self.assertTrue(an.readings_equal(rd(), rd(cpu=2500.0, state_hash="other")), "CPU and the state digest are not readings of the gate")
        self.assertFalse(an.readings_equal(rd(), rd(q1=105)))
        self.assertFalse(an.readings_equal(rd(), rd(frames=27)))
        self.assertFalse(an.readings_equal(rd(), rd(share=0.4500001)))

    def test_a_missing_reading_is_not_equal(self) -> None:
        self.assertFalse(an.readings_equal({**rd(), "q1_seen": None}, rd()))
        self.assertFalse(an.readings_equal(rd(), {**rd(), "confirmed_share": None}))


class TestNullArrays(unittest.TestCase):
    def test_the_null_is_the_incumbent_plus_the_twins_for_each_dimension_and_ln_cpu(self) -> None:
        inc = rd(q1=104, frames=26, share=0.45, cpu=2000.0)
        twins = [rd(q1=104 + (i % 3) - 1, frames=26 + (i % 5) - 2, share=0.45 + 0.001 * i, cpu=2000.0 + 10 * i) for i in range(20)]
        n = an.null_arrays(inc, twins)
        self.assertEqual({k: len(v) for k, v in n.items()}, {"q1_seen": 21, "frames_filed": 21, "confirmed_share": 21, "ln_cpu": 21})
        self.assertEqual(n["q1_seen"][0], 104 / 110)
        self.assertAlmostEqual(n["ln_cpu"][1], math.log(twins[0]["cpu_s"]))

    def test_a_none_reading_is_refused_not_dropped(self) -> None:
        with self.assertRaises(ValueError):
            an.null_arrays(rd(), [rd(), {**rd(), "frames_filed": None}])
        with self.assertRaises(ValueError):
            an.null_arrays(rd(), [rd(), {**rd(), "cpu_s": None}])


class TestStagedDecisions(unittest.TestCase):
    def test_a0_is_non_degenerate_iff_an_epsilon_twin_moved_a_reading(self) -> None:
        inc = rd()
        d = an.a0_decision(inc, {"eps1e-3-k01": rd(), "eps1e-2-k01": rd()})
        self.assertFalse(d["non_degenerate"])
        self.assertEqual(d["moved"], {})
        d = an.a0_decision(inc, {"eps1e-3-k01": rd(), "eps1e-2-k01": rd(frames=24)})
        self.assertTrue(d["non_degenerate"])
        self.assertEqual(d["moved"], {"frames_filed": ["eps1e-2-k01"]})

    def test_a0plus_reads_degenerate_only_if_all_six_equal_and_prints_the_bound(self) -> None:
        inc = rd()
        six = {f"t{i}": rd() for i in range(6)}
        d = an.a0plus_decision(inc, six)
        self.assertTrue(d["degenerate"])
        self.assertAlmostEqual(d["upper_bound_p"], 1 - 0.05 ** (1 / 6), places=9)
        self.assertAlmostEqual(d["upper_bound_p"], 0.393, places=3)
        six["t3"] = rd(q1=103)
        d = an.a0plus_decision(inc, six)
        self.assertFalse(d["degenerate"])
        self.assertEqual(d["moved"], {"q1_seen": ["t3"]})

    def test_a0plus_refuses_fewer_than_six_twins(self) -> None:
        with self.assertRaises(ValueError):
            an.a0plus_decision(rd(), {f"t{i}": rd() for i in range(5)})

    def test_stage_b_runs_only_where_a_band_could_exist(self) -> None:
        inc = rd()
        flat = [rd() for _ in range(5)]
        self.assertFalse(an.stage_b_condition(inc, flat)["run"])
        two = [rd(q1=104)] * 4 + [rd(q1=103)]
        self.assertFalse(an.stage_b_condition(inc, two)["run"], "two distinct values give no band under A1 (i)")
        three = [rd(q1=104)] * 3 + [rd(q1=103), rd(q1=105)]
        r = an.stage_b_condition(inc, three)
        self.assertTrue(r["run"])
        self.assertEqual(r["dims"], ["q1_seen"])


class TestChooseLevel(unittest.TestCase):
    def levels(self, flips):
        # flips: {eps: (n_twins_with_a_discrete_difference, spread_value)}; each twin reading differs from the incumbent by `spread_value` items when it flips
        out = {}
        for eps, (n_flip, spread) in flips.items():
            out[eps] = [{"label": f"e{eps}-{i}", "reading": rd(q1=104 + (spread if i < n_flip else 0)), "discrete_differing": (1 if i < n_flip else 0)} for i in range(5)]
        return out

    def test_the_chosen_level_is_the_smallest_whose_twins_differ_in_a_discrete_outcome(self) -> None:
        c = an.choose_level(rd(), self.levels({1e-4: (0, 0), 1e-3: (2, 1), 1e-2: (5, 1)}))
        self.assertEqual(c["chosen"], 1e-3)
        self.assertEqual(c["per_level"][1e-4]["twins_equal_to_incumbent"], 5)
        self.assertEqual(c["per_level"][1e-3]["twins_equal_to_incumbent"], 3)

    def test_a_level_whose_readings_move_but_whose_journal_does_not_still_differs(self) -> None:
        lv = self.levels({1e-4: (0, 0), 1e-3: (0, 0), 1e-2: (0, 0)})
        lv[1e-3][2] = {"label": "x", "reading": rd(q1=102), "discrete_differing": 0}
        self.assertEqual(an.choose_level(rd(), lv)["chosen"], 1e-3, "a reading that moved is a difference even with no discrete journal row")

    def test_no_level_differs_means_no_choice(self) -> None:
        c = an.choose_level(rd(), self.levels({1e-4: (0, 0), 1e-3: (0, 0), 1e-2: (0, 0)}))
        self.assertIsNone(c["chosen"])

    def test_a_chosen_level_whose_spread_is_larger_than_the_next_smaller_flipping_level_is_a_merit_step(self) -> None:
        # 1e-3 and 1e-2 both flip, but the spread GROWS by an order of magnitude from 1e-3 to 1e-2: the larger level is a merit step; the smallest flipping level stays the null
        lv = self.levels({1e-4: (0, 0), 1e-3: (3, 1), 1e-2: (5, 6)})
        c = an.choose_level(rd(), lv)
        self.assertEqual(c["chosen"], 1e-3)
        self.assertTrue(c["per_level"][1e-2]["spread_grows"])
        self.assertFalse(c["per_level"][1e-3]["spread_grows"])


class TestBandsFromTwins(unittest.TestCase):
    def spread_twins(self):
        return [rd(q1=104 + (i % 5) - 2, frames=26 + (i % 7) - 3, share=0.45 + 0.002 * (i % 6), cpu=2000.0 + 15 * i) for i in range(20)]

    def test_a_spread_null_gives_normal_bands_and_the_file_validates(self) -> None:
        b = an.bands_from_twins(rd(), self.spread_twins(), seed_twins=None, slice_name="S1", scope="mid-life (S1)")
        eb.validate_bands(b)
        self.assertEqual(b["dims"]["q1_seen"]["kind"], "normal")
        self.assertEqual(b["dims"]["confirmed_share"]["kind"], "normal")
        self.assertEqual(b["n"], 21)

    def test_reading_a_a_degenerate_dimension_has_no_band(self) -> None:
        flat = [rd(cpu=2000.0 + 15 * i) for i in range(20)]
        b = an.bands_from_twins(rd(), flat, seed_twins=None, slice_name="S1", scope="x", degenerate="none")
        self.assertEqual(b["dims"]["q1_seen"]["kind"], "none")
        self.assertEqual(b["dims"]["confirmed_share"]["kind"], "none")
        self.assertEqual(eb.position(8 / 110, b["dims"]["q1_seen"]), "no-band")

    def test_reading_b_a_degenerate_dimension_gates_at_its_own_resolution(self) -> None:
        flat = [rd(cpu=2000.0 + 15 * i) for i in range(20)]
        b = an.bands_from_twins(rd(), flat, seed_twins=None, slice_name="S1", scope="x", degenerate="range")
        q = b["dims"]["q1_seen"]
        self.assertEqual((q["kind"], q["range"]), ("rank", 0.0))
        self.assertEqual(eb.position(0.0, q), "within")
        self.assertEqual(eb.position(1 / 110, q), "above", "one item of q1_seen clears a null that never moved")
        self.assertEqual(eb.position(-1 / 110, q), "below")
        c = b["dims"]["confirmed_share"]
        self.assertGreater(c["range"], 0.0, "a continuous reading needs a floor of one count of its own denominator, never exactly 0")
        self.assertEqual(eb.position(c["range"] / 2, c), "within")
        self.assertEqual(eb.position(c["range"] * 2, c), "above")
        eb.validate_bands(b)
        self.assertEqual(b["degenerate_reading"], "B: the null's own range, floored at one resolvable step")

    def test_the_seed_twins_give_frames_filed_its_band_where_the_epsilon_null_is_flat(self) -> None:
        flat = [rd(cpu=2000.0 + 15 * i) for i in range(20)]
        seeds = [rd(frames=f) for f in (24, 28, 27, 25, 29, 26, 22, 30, 26, 27)]
        b = an.bands_from_twins(rd(), flat, seed_twins=seeds, slice_name="S1", scope="x", degenerate="none")
        self.assertEqual(b["dims"]["frames_filed"]["kind"], "normal")
        self.assertEqual(b["dims"]["frames_filed"]["rule"], "seed")
        self.assertEqual(b["frames_rule"], "seed")

    def test_the_ceiling_of_q1_seen_is_printed_beside_its_band(self) -> None:
        b = an.bands_from_twins(rd(q1=104), self.spread_twins(), seed_twins=None, slice_name="S1", scope="x")
        self.assertEqual(b["dims"]["q1_seen"]["ceiling_items"], 6)
        self.assertIn("reachable", b["dims"]["q1_seen"]["ceiling_note"])


if __name__ == "__main__":
    unittest.main()
