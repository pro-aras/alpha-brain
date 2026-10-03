# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:15 +0400 — PREREG-EVOLVE-CAL AMENDMENT 3 (A3.4, A3.6, A3.7): the N1 analysis, tests FIRST.
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:5x +0400 — AMENDMENT 3b (the verifier's E1, E2, E3 and limits (1), (5)), tests FIRST: ONE test (MOVE) for the release of
# Stage A and the choice of epsilon; EQUALS counts an unmatched moment row; Stage B's two candidate rules; ceilings printed on both sides for all three dimensions. The tests
# of A3's superseded clauses (a frames_filed-only move releases Stage A; the level is chosen by discrete flips; twins carry `discrete_differing`) are REWRITTEN below, each
# with the clause of A3b that replaces it named in its docstring or comment; none was loosened, and the old behaviour is asserted as the OLD behaviour's contrast where useful.
"""tests/tools/test_evolve_cal_analyse.py — tools/evolve_cal_analyse.py: from the twins' readings to the null arrays, the staged decisions and the BANDS file.

The staged design (A3.6 as amended by A3b): an epsilon twin MOVES iff its q1_seen or confirmed_share differs from the incumbent's (frames_filed is printed, never releases).
Stage A0 (the incumbent + one twin at 1e-3 and one at 1e-2 on the full slice) is NON-DEGENERATE iff at least one epsilon twin MOVES; if neither does, Stage A0+ (four more)
reads DEGENERATE iff none of the six MOVES (the 95 % upper bound on the per-twin chance of a move is then 1 − 0.05^(1/6)); the chosen level is the smallest at which a twin MOVES;
Stage B (the other 15 twins at the chosen level) runs under rule S (as signed: >= 3 distinct values in some gated dimension) or rule M (whenever a twin of the chosen level MOVES).
A3b.1: a twin EQUALS the incumbent iff no moment row is unmatched or discretely different and its three readings are equal. A3.7: a degenerate dimension has NO band (reading
A) or the band of its null's own range with a floor of one resolvable step (reading B).
"""
from __future__ import annotations

import json
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


def tw(label, reading, flips=0, other=None):
    """A twin record as `an.twin_record` builds it from a keyed comparison: its readings, its moment FLIPS (A3b.1) and the other kinds' discrete payloads."""
    return {"label": label, "reading": reading, "moment_flips": flips, "other_discrete": other or {}}


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


class TestMove(unittest.TestCase):
    """A3b.2 (the verifier's E2 and limit (1)): ONE test, MOVE, for the release of Stage A and the choice of epsilon."""

    def test_a_twin_moves_iff_q1_seen_or_confirmed_share_differs_from_the_incumbents(self) -> None:
        inc = rd()
        self.assertEqual(an.moved_dims(inc, rd()), [])
        self.assertEqual(an.moved_dims(inc, rd(q1=103)), ["q1_seen"])
        self.assertEqual(an.moved_dims(inc, rd(share=0.4500001)), ["confirmed_share"])
        self.assertEqual(an.moved_dims(inc, rd(q1=105, share=0.46)), ["q1_seen", "confirmed_share"])

    def test_frames_filed_alone_is_not_a_move(self) -> None:
        # frames_filed moves with the think stream, which the seed twins bound; it is printed beside every decision and releases nothing
        self.assertEqual(an.moved_dims(rd(), rd(frames=24)), [])
        self.assertEqual(an.MOVE_DIMS, ("q1_seen", "confirmed_share"))

    def test_a_missing_reading_is_refused_never_read_as_a_move_or_a_hold(self) -> None:
        with self.assertRaises(ValueError):
            an.moved_dims(rd(), {**rd(), "q1_seen": None})
        with self.assertRaises(ValueError):
            an.moved_dims({**rd(), "confirmed_share": None}, rd())
        with self.assertRaises(ValueError):
            an.moved_dims(rd(), {k: v for k, v in rd().items() if k != "confirmed_share"})


class TestTwinEquals(unittest.TestCase):
    """A3b.1 (the verifier's E1): EQUALS = no flip on the moment rows (an unmatched row counts) AND the three readings equal."""

    def test_equal_iff_no_flip_and_the_three_readings_equal(self) -> None:
        inc = rd()
        self.assertTrue(an.twin_equals(inc, tw("a", rd())))
        self.assertFalse(an.twin_equals(inc, tw("b", rd(), flips=1)))
        self.assertFalse(an.twin_equals(inc, tw("c", rd(frames=27))), "frames_filed is one of the three readings of EQUALS (it is only excluded from MOVE)")
        self.assertFalse(an.twin_equals(inc, tw("d", rd(q1=105))))

    def test_a_missing_flip_count_is_refused(self) -> None:
        t = tw("a", rd())
        del t["moment_flips"]
        with self.assertRaises(ValueError):
            an.twin_equals(rd(), t)

    def test_the_verifiers_plants_read_through_the_real_comparison(self) -> None:
        # the plants of v7_plants.out on the branch's own comparator: an act changed at one seq; two of four moment rows missing; a changed edge count (the control)
        def moment(seq):
            return {"seq": seq, "moment": f"m{seq}", "act": "glance", "glance": 0, "cells": [10, 5], "err": 0.5, "hash": f"h{seq}", "word": "circle", "fix": [[1, 2]]}
        a = [moment(s) for s in (1, 2, 3, 4)]
        wait = json.loads(json.dumps(a))
        wait[2]["act"] = "wait"
        miss = [x for x in json.loads(json.dumps(a)) if x["seq"] in (1, 4)]
        edge = json.loads(json.dumps(a))
        edge[1]["cells"] = [11, 5]
        same = json.loads(json.dumps(a))
        same[0]["hash"] = "other"
        for name, b, equal in (("wait", wait, False), ("missing", miss, False), ("edge", edge, False), ("hash-only", same, True)):
            t = an.twin_record(name, rd(), cal.compare_twins_keyed(a, b))
            self.assertEqual(an.twin_equals(rd(), t), equal, name)
        self.assertEqual(an.twin_record("w", rd(), cal.compare_twins_keyed(a, wait))["moment_flips"], 2)

    def test_twin_record_refuses_a_comparison_without_flips(self) -> None:
        with self.assertRaises(ValueError):
            an.twin_record("x", rd(), {"moment": {"matched": 1, "only_a": 0, "only_b": 0, "discrete_differing": 0}, "other": {}})


class TestStagedDecisions(unittest.TestCase):
    def test_a0_is_non_degenerate_iff_an_epsilon_twin_moves_q1_seen_or_confirmed_share(self) -> None:
        inc = rd()
        d = an.a0_decision(inc, {"eps1e-3-k01": rd(), "eps1e-2-k01": rd()})
        self.assertFalse(d["non_degenerate"])
        self.assertEqual(d["moved"], {})
        d = an.a0_decision(inc, {"eps1e-3-k01": rd(), "eps1e-2-k01": rd(q1=103)})
        self.assertTrue(d["non_degenerate"])
        self.assertEqual(d["moved"], {"q1_seen": ["eps1e-2-k01"]})
        self.assertEqual(d["release_dims"], ["q1_seen"])
        d = an.a0_decision(inc, {"eps1e-3-k01": rd(share=0.46), "eps1e-2-k01": rd()})
        self.assertTrue(d["non_degenerate"])
        self.assertEqual(d["release_dims"], ["confirmed_share"])

    def test_a_frames_filed_only_move_releases_nothing_and_is_printed(self) -> None:
        # AMENDS A3.6 (1): A3 read ANY of the three readings; the verifier's limit (1): frames_filed is the think stream the 10 seed twins already bound
        d = an.a0_decision(rd(), {"eps1e-3-k01": rd(), "eps1e-2-k01": rd(frames=24)})
        self.assertFalse(d["non_degenerate"])
        self.assertEqual(d["moved"], {"frames_filed": ["eps1e-2-k01"]})
        self.assertEqual(d["release_dims"], [])
        self.assertTrue(d["frames_only"])

    def test_a0_refuses_a_missing_reading(self) -> None:
        with self.assertRaises(ValueError):
            an.a0_decision(rd(), {"a": {**rd(), "q1_seen": None}, "b": rd()})

    def test_a0plus_reads_degenerate_only_if_none_of_the_six_moves_and_prints_the_bound(self) -> None:
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

    def test_a0plus_a_frames_only_move_among_the_six_is_still_degenerate_for_the_epsilon_dimensions(self) -> None:
        six = {f"t{i}": rd() for i in range(6)}
        six["t2"] = rd(frames=30)
        d = an.a0plus_decision(rd(), six)
        self.assertTrue(d["degenerate"])
        self.assertEqual(d["moved"], {"frames_filed": ["t2"]}, "printed, never hidden")

    def test_a0plus_refuses_fewer_than_six_twins(self) -> None:
        with self.assertRaises(ValueError):
            an.a0plus_decision(rd(), {f"t{i}": rd() for i in range(5)})

    def test_stage_b_rule_s_runs_only_where_a_band_could_exist(self) -> None:
        inc = rd()
        flat = [rd() for _ in range(5)]
        self.assertFalse(an.stage_b_condition(inc, flat, rule="S")["run"])
        two = [rd(q1=104)] * 4 + [rd(q1=103)]
        self.assertFalse(an.stage_b_condition(inc, two, rule="S")["run"], "two distinct values give no band under A1 (i)")
        three = [rd(q1=104)] * 3 + [rd(q1=103), rd(q1=105)]
        r = an.stage_b_condition(inc, three, rule="S")
        self.assertTrue(r["run"])
        self.assertEqual(r["dims"], ["q1_seen"])
        self.assertEqual(r["rule"], "S")

    def test_stage_b_rule_m_runs_whenever_a_twin_of_the_chosen_level_moves(self) -> None:
        # A3b.3: the builder's alternative to rule S; at the chosen level a twin MOVED by construction, so M is «always» there, evaluated on the data and never assumed
        inc = rd()
        self.assertFalse(an.stage_b_condition(inc, [rd() for _ in range(5)], rule="M")["run"])
        one = [rd()] * 4 + [rd(q1=103)]
        r = an.stage_b_condition(inc, one, rule="M")
        self.assertTrue(r["run"])
        self.assertEqual((r["dims"], r["rule"]), (["q1_seen"], "M"))
        self.assertFalse(an.stage_b_condition(inc, one, rule="S")["run"], "one deviating value is two distinct values: S needs three")
        self.assertFalse(an.stage_b_condition(inc, [rd()] * 4 + [rd(frames=30)], rule="M")["run"], "a frames_filed-only difference is not a move")

    def test_stage_b_needs_an_explicit_rule_the_signers_have_not_chosen(self) -> None:
        with self.assertRaises(TypeError):
            an.stage_b_condition(rd(), [rd()] * 5)
        with self.assertRaises(ValueError):
            an.stage_b_condition(rd(), [rd()] * 5, rule="X")


class TestChooseLevel(unittest.TestCase):
    def levels(self, spec):
        # spec: {eps: (n_moving_twins, shift_items, n_flipping_twins)}; a moving twin reads q1_seen shift_items away from the incumbent's; a flipping twin carries moment_flips 1
        out = {}
        for eps, (n_move, shift, n_flip) in spec.items():
            out[eps] = [tw(f"e{eps}-{i}", rd(q1=104 + (shift if i < n_move else 0)), flips=(1 if i < n_flip else 0)) for i in range(5)]
        return out

    def test_the_chosen_level_is_the_smallest_at_which_a_twin_moves(self) -> None:
        c = an.choose_level(rd(), self.levels({1e-4: (0, 0, 0), 1e-3: (2, 1, 2), 1e-2: (5, 1, 5)}))
        self.assertEqual(c["chosen"], 1e-3)
        self.assertEqual(c["per_level"][1e-4]["twins_moved"], 0)
        self.assertEqual(c["per_level"][1e-3]["twins_moved"], 2)
        self.assertEqual(c["per_level"][1e-3]["twins_equal_to_incumbent"], 3)
        self.assertEqual(c["per_level"][1e-4]["twins_equal_to_incumbent"], 5)

    def test_the_verifiers_plant_1e3_flips_no_reading_and_1e2_moves_one_item_chooses_1e2(self) -> None:
        # E2's plant: A3.4 as signed chose 1e-3 (a discrete flip) while A3.6 released Stage A on 1e-2's reading: 17.5 CPU-h with the answer fixed. ONE test: the level moves.
        c = an.choose_level(rd(), self.levels({1e-4: (0, 0, 0), 1e-3: (0, 0, 5), 1e-2: (1, 1, 5)}))
        self.assertEqual(c["chosen"], 1e-2)
        self.assertTrue(c["per_level"][1e-3]["flip_without_move"])
        self.assertFalse(c["per_level"][1e-2]["flip_without_move"])
        self.assertEqual(c["per_level"][1e-3]["flips"], 5)

    def test_flips_with_no_reading_moved_choose_nothing(self) -> None:
        # the shape of the real ladder at 1e-3 and 1e-2 (edges / cells flipped, every reading equal): printed, and nothing is chosen
        c = an.choose_level(rd(), self.levels({1e-4: (0, 0, 0), 1e-3: (0, 0, 2), 1e-2: (0, 0, 5)}))
        self.assertIsNone(c["chosen"])
        self.assertTrue(c["per_level"][1e-3]["flip_without_move"])
        self.assertTrue(c["per_level"][1e-2]["flip_without_move"])
        self.assertFalse(c["per_level"][1e-4]["flip_without_move"])

    def test_a_reading_that_moved_with_no_flip_is_a_move_and_is_flagged(self) -> None:
        lv = self.levels({1e-4: (0, 0, 0), 1e-3: (0, 0, 0), 1e-2: (0, 0, 0)})
        lv[1e-3][2] = tw("x", rd(q1=102), flips=0)
        c = an.choose_level(rd(), lv)
        self.assertEqual(c["chosen"], 1e-3)
        self.assertTrue(c["per_level"][1e-3]["reading_move_without_flip"])
        self.assertFalse(c["per_level"][1e-2]["reading_move_without_flip"])

    def test_a_frames_filed_only_move_chooses_nothing_and_is_printed(self) -> None:
        lv = self.levels({1e-4: (0, 0, 0), 1e-3: (0, 0, 0), 1e-2: (0, 0, 0)})
        lv[1e-3][0] = tw("f", rd(frames=24))
        c = an.choose_level(rd(), lv)
        self.assertIsNone(c["chosen"])
        self.assertEqual(c["per_level"][1e-3]["frames_moved"], ["f"])
        self.assertEqual(c["per_level"][1e-3]["twins_moved"], 0)

    def test_an_unmatched_moment_row_makes_a_twin_not_equal_and_a_flip_without_a_move(self) -> None:
        lv = self.levels({1e-4: (0, 0, 0), 1e-3: (0, 0, 0), 1e-2: (0, 0, 0)})
        lv[1e-3][1] = tw("u", rd(), flips=2)          # two unmatched moment rows; no reading moved
        c = an.choose_level(rd(), lv)
        self.assertEqual(c["per_level"][1e-3]["twins_equal_to_incumbent"], 4)
        self.assertTrue(c["per_level"][1e-3]["flip_without_move"])
        self.assertEqual(c["per_level"][1e-3]["flips"], 2)
        self.assertIsNone(c["chosen"])

    def test_an_other_kind_flip_with_equal_moment_rows_is_flagged_and_decides_nothing(self) -> None:
        lv = self.levels({1e-4: (0, 0, 0), 1e-3: (0, 0, 0), 1e-2: (0, 0, 0)})
        lv[1e-3][0] = tw("o", rd(), flips=0, other={"sleep": {"rows": 1, "paths": {"sleep.pruned": 1}}})
        c = an.choose_level(rd(), lv)
        self.assertIsNone(c["chosen"])
        self.assertTrue(c["per_level"][1e-3]["other_kind_flip_moment_rows_equal"])
        self.assertEqual(c["per_level"][1e-3]["twins_equal_to_incumbent"], 5, "an other-kind payload is outside EQUALS")
        self.assertFalse(c["per_level"][1e-2]["other_kind_flip_moment_rows_equal"])

    def test_a_larger_level_whose_spread_exceeds_flat_factor_times_the_chosens_is_labelled_not_chosen(self) -> None:
        c = an.choose_level(rd(), self.levels({1e-4: (0, 0, 0), 1e-3: (3, 1, 3), 1e-2: (5, 6, 5)}))
        self.assertEqual(c["chosen"], 1e-3)
        self.assertTrue(c["per_level"][1e-2]["spread_grows"])
        self.assertFalse(c["per_level"][1e-3]["spread_grows"])
        self.assertEqual(c["flat_factor"], 2.0)
        self.assertIn("respond to epsilon above", c["flatness_note"])

    def test_the_flatness_factor_is_strict_and_exactly_twice_is_not_a_growth(self) -> None:
        # all five twins of each level shifted by the same number of items: rms 1, then 2 (= 2.0 x, NOT more), then 3 (more)
        lv = self.levels({1e-4: (0, 0, 0), 1e-3: (5, 1, 5), 1e-2: (5, 2, 5)})
        self.assertFalse(an.choose_level(rd(), lv)["per_level"][1e-2]["spread_grows"])
        lv = self.levels({1e-4: (0, 0, 0), 1e-3: (5, 1, 5), 1e-2: (5, 3, 5)})
        self.assertTrue(an.choose_level(rd(), lv)["per_level"][1e-2]["spread_grows"])

    def test_no_flatness_note_when_nothing_grows(self) -> None:
        c = an.choose_level(rd(), self.levels({1e-4: (0, 0, 0), 1e-3: (3, 1, 3), 1e-2: (3, 1, 3)}))
        self.assertEqual(c["chosen"], 1e-3)
        self.assertIsNone(c["flatness_note"])

    def test_the_chosen_levels_band_is_never_replaced_by_a_larger_level(self) -> None:
        # the consequence A3b.2 states: spread_grows is a LABEL; `chosen` stays the smallest moving level whatever the larger levels read
        c = an.choose_level(rd(), self.levels({1e-4: (0, 0, 0), 1e-3: (1, 1, 1), 1e-2: (5, 9, 5)}))
        self.assertEqual(c["chosen"], 1e-3)
        self.assertTrue(c["per_level"][1e-2]["spread_grows"])

    def test_no_level_moves_means_no_choice(self) -> None:
        self.assertIsNone(an.choose_level(rd(), self.levels({1e-4: (0, 0, 0), 1e-3: (0, 0, 0), 1e-2: (0, 0, 0)}))["chosen"])

    def test_a_missing_reading_or_flip_count_is_refused(self) -> None:
        lv = self.levels({1e-4: (0, 0, 0)})
        lv[1e-4][0] = {"label": "x", "reading": {**rd(), "q1_seen": None}, "moment_flips": 0}
        with self.assertRaises(ValueError):
            an.choose_level(rd(), lv)
        lv = self.levels({1e-4: (0, 0, 0)})
        del lv[1e-4][0]["moment_flips"]
        with self.assertRaises(ValueError):
            an.choose_level(rd(), lv)


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
        self.assertEqual(b["dims"]["frames_filed"]["n"], 11, "the seed null is the incumbent + the 10 seed twins")
        self.assertEqual(b["frames_rule"], "seed")

    def test_the_ceiling_of_q1_seen_is_printed_beside_its_band(self) -> None:
        b = an.bands_from_twins(rd(q1=104), self.spread_twins(), seed_twins=None, slice_name="S1", scope="x")
        self.assertEqual(b["dims"]["q1_seen"]["ceiling_items"], 6)
        self.assertIn("reachable", b["dims"]["q1_seen"]["ceiling_note"])

    # ---- A3b.5 (the verifier's limit (5)): every band is printed beside its dimension's ceiling, on BOTH sides, for all three dimensions
    def test_every_dimension_carries_both_sides_of_its_ceiling(self) -> None:
        b = an.bands_from_twins(rd(q1=104, frames=26, share=0.45), self.spread_twins(), seed_twins=None, slice_name="S1", scope="x")
        for d in ("q1_seen", "frames_filed", "confirmed_share"):
            c = b["dims"][d]["ceiling"]
            for k in ("reading", "up_room", "down_room", "improved_reachable", "regressed_reachable", "basis", "note"):
                self.assertIn(k, c, f"{d}.{k}")
        q = b["dims"]["q1_seen"]["ceiling"]
        self.assertEqual((q["reading"], q["up_room"], q["down_room"]), (104, 6, 104), "items of 110")
        f = b["dims"]["frames_filed"]["ceiling"]
        self.assertEqual((f["reading"], f["down_room"]), (26, 26))
        self.assertIsNone(f["up_room"], "no ceiling is known for frames_filed")
        self.assertTrue(f["improved_reachable"], "an unbounded side is reachable")
        s = b["dims"]["confirmed_share"]["ceiling"]
        self.assertAlmostEqual(s["up_room"], 0.55, places=9)
        self.assertAlmostEqual(s["down_room"], 0.45, places=9)

    def test_improved_is_unreachable_when_the_edge_is_not_below_the_headroom(self) -> None:
        # q1_seen 108 of 110: headroom 2 items against an edge of about 5: IMPROVED can never fire (a bar above its own ceiling, #228 (b))
        b = an.bands_from_twins(rd(q1=108), [rd(q1=108 + (i % 5) - 2) for i in range(20)], seed_twins=None, slice_name="S1", scope="x")
        c = b["dims"]["q1_seen"]["ceiling"]
        self.assertIn(b["dims"]["q1_seen"]["kind"], ("normal", "rank"), "a band exists (either kind has a half-width at or above the headroom)")
        self.assertFalse(c["improved_reachable"])
        self.assertTrue(c["regressed_reachable"])
        self.assertIn("UNREACHABLE", c["note"])

    def test_regressed_is_unreachable_when_the_edge_is_not_below_the_incumbents_own_reading(self) -> None:
        # frames_filed 5 against an edge of about 7: a fall cannot be larger than the reading itself
        b = an.bands_from_twins(rd(frames=5), [rd(frames=5 + (i % 7) - 3) for i in range(20)], seed_twins=None, slice_name="S1", scope="x")
        c = b["dims"]["frames_filed"]["ceiling"]
        self.assertIn(b["dims"]["frames_filed"]["kind"], ("normal", "rank"), "a band exists (either kind has a half-width at or above the reading)")
        self.assertFalse(c["regressed_reachable"])
        self.assertTrue(c["improved_reachable"])
        self.assertIn("UNREACHABLE", c["note"])

    def test_confirmed_share_near_one_has_no_headroom_for_a_band(self) -> None:
        b = an.bands_from_twins(rd(share=0.999), [rd(share=0.999 - 0.002 * (i % 6)) for i in range(20)], seed_twins=None, slice_name="S1", scope="x")
        c = b["dims"]["confirmed_share"]["ceiling"]
        self.assertIn(b["dims"]["confirmed_share"]["kind"], ("normal", "rank"), "a band exists")
        self.assertFalse(c["improved_reachable"])

    def test_a_bandless_dimension_is_printed_against_the_legacy_tolerance(self) -> None:
        # A' (the seat's ruling 22:32): a gated dimension without a measured band keeps the LEGACY tolerance; its ceiling is read against the legacy margin
        flat = [rd(cpu=2000.0 + 15 * i) for i in range(20)]
        b = an.bands_from_twins(rd(q1=104), flat, seed_twins=None, slice_name="S1", scope="x", degenerate="none")
        c = b["dims"]["q1_seen"]["ceiling"]
        self.assertEqual(b["dims"]["q1_seen"]["kind"], "none")
        self.assertIn("legacy", c["basis"])
        self.assertTrue(c["improved_reachable"], "a rise of the legacy margin (0.01) fits in 6 items of headroom")
        flat_hi = an.bands_from_twins(rd(q1=110), flat, seed_twins=None, slice_name="S1", scope="x", degenerate="none")
        self.assertFalse(flat_hi["dims"]["q1_seen"]["ceiling"]["improved_reachable"], "110 of 110: nothing to gain")
        self.assertTrue(flat_hi["dims"]["q1_seen"]["ceiling"]["regressed_reachable"], "any fall regresses under the legacy tolerance")
        one = an.bands_from_twins(rd(q1=109), flat, seed_twins=None, slice_name="S1", scope="x", degenerate="none")
        self.assertFalse(one["dims"]["q1_seen"]["ceiling"]["improved_reachable"], "109 of 110: one item of headroom is below the legacy margin (0.01 = 1.1 items)")
        two = an.bands_from_twins(rd(q1=108), flat, seed_twins=None, slice_name="S1", scope="x", degenerate="none")
        self.assertTrue(two["dims"]["q1_seen"]["ceiling"]["improved_reachable"], "108 of 110: two items clear the margin")
        low = an.bands_from_twins(rd(q1=1), flat, seed_twins=None, slice_name="S1", scope="x", degenerate="none")
        self.assertTrue(low["dims"]["q1_seen"]["ceiling"]["regressed_reachable"], "1 of 110: a fall of one item is still ANY fall, which the legacy tolerance regresses")
        zero = an.bands_from_twins(rd(q1=0), flat, seed_twins=None, slice_name="S1", scope="x", degenerate="none")
        self.assertFalse(zero["dims"]["q1_seen"]["ceiling"]["regressed_reachable"], "0 of 110: nothing left to fall")


if __name__ == "__main__":
    unittest.main()
