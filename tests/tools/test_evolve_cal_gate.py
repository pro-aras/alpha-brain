# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:55 +0400 — PREREG-EVOLVE-CAL §1 (the calibrated gate, D1/D4/D5/D6/D7/D8): tests FIRST.
"""tests/tools/test_evolve_cal_gate.py — the pure parts of the calibrated gate and of the proposer.

  tools/evolve_bands.py (stdlib only; the worker reads it):  position / calibrated_verdict / not_gradable_block / confirm_decision /
                                                             validate_bands / load_bands
  tools/evolve.py:  draw_stream / mutate_distinct (D8, A8)

THE LAW (docs/organism/evolve/PREREG-EVOLVE-CAL.md §1 + A1–A4, A8): three verdicts (REGRESSED, IMPROVED, NO EVIDENCE); a reading is
below / within / above its BAND — the band is a half-width around Δ = 0 (the production Δ is a difference of two draws, so under no merit
difference it is centred at 0, A4 (ii)); integer readings compare on their own grid; a dimension whose null could not give a band has NO
band and does not gate; the cost is REGRESSED only if its CPU ratio is outside its band AND above the 1.2 policy cap (A3); reward_mean,
act_pass and sentence_pass are printed as NOT GRADABLE with their reason and presence count and never enter the bar; an IMPROVED mutant
is adopted only after it is IMPROVED again on the NEXT disjoint slice; the proposer never emits the incumbent's own value.
"""
from __future__ import annotations

import json
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import tools.evolve as ev
import tools.evolve_bands as eb
from creature import genes
from creature.genes import MUTABLE_KEYS, apply_mutation, draw_mutation, mutate_genome_text

ROOT = Path(__file__).resolve().parent.parent.parent
V0 = (ROOT / "genome" / "brain" / "lives" / "BRAIN-LONG-2.genome").read_text()      # brain-long-2's life genome (SEED 20261101)
V1 = apply_mutation(V0, "KWTA.k", 4)                                              # after #5's adoption (the recorded GENOME.v1)


def band(kind="normal", edge=None, grid=None, rng=None, **kw):
    b = {"kind": kind, "grid": grid, "edge": edge, "range": rng, "sigma_hat": (edge / 3.70 if edge else None), "n": 21, "distinct": 5}
    b.update(kw)
    return b


def bands(q1_items=5.5, frames=3.2, share=0.03, ln_cpu=0.25, **over):
    d = {"q1_seen": band(edge=q1_items / 110, grid=1 / 110),
         "frames_filed": band(edge=frames, grid=1.0),
         "confirmed_share": band(edge=share),
         "ln_cpu": band(edge=ln_cpu)}
    d.update(over)
    return {"law": "PREREG-EVOLVE-CAL", "slice": "S1", "n": 21, "df": 20, "alpha_side": 0.0083, "dims": d, "cost_policy_cap": 1.2}


def reading(q1_items=100, frames=30, share=0.45, cpu=2000.0, **kw):
    r = {"q1_seen": (None if q1_items is None else q1_items / 110), "frames_filed": frames, "confirmed_share": share, "cpu_s": cpu,
         "reward_mean": 0.0, "act_pass": True, "sentence_pass": None, "detail": {"sentence": {"missions": 7}}}
    r.update(kw)
    return r


class TestPosition(unittest.TestCase):
    def test_a_grid_band_compares_in_items_and_is_strict(self) -> None:
        b = band(edge=5.5 / 110, grid=1 / 110)
        self.assertEqual(eb.position(5 / 110, b), "within")
        self.assertEqual(eb.position(6 / 110, b), "above")
        self.assertEqual(eb.position(-5 / 110, b), "within")
        self.assertEqual(eb.position(-6 / 110, b), "below")

    def test_an_edge_that_is_a_whole_number_of_items_needs_one_more(self) -> None:
        b = band(edge=5.0 / 110, grid=1 / 110)
        self.assertEqual(eb.position((105 - 100) / 110, b), "within", "Δ equal to the edge is not outside it")
        self.assertEqual(eb.position((106 - 100) / 110, b), "above")
        self.assertEqual(eb.position((100 - 105) / 110, b), "within")
        self.assertEqual(eb.position((100 - 106) / 110, b), "below")

    def test_float_noise_in_a_grid_difference_does_not_move_a_reading_across_the_edge(self) -> None:
        b = band(edge=5.0 / 110, grid=1 / 110)
        for lo in range(60, 105):
            self.assertEqual(eb.position((lo + 5) / 110 - lo / 110, b), "within", lo)
            self.assertEqual(eb.position((lo + 6) / 110 - lo / 110, b), "above", lo)

    def test_integer_frames_compare_on_their_own_grid(self) -> None:
        b = band(edge=3.2, grid=1.0)
        self.assertEqual(eb.position(3, b), "within")
        self.assertEqual(eb.position(4, b), "above")
        self.assertEqual(eb.position(-3, b), "within")
        self.assertEqual(eb.position(-4, b), "below")

    def test_a_continuous_band_has_no_grid(self) -> None:
        b = band(edge=0.03)
        self.assertEqual(eb.position(0.03, b), "within")
        self.assertEqual(eb.position(0.0301, b), "above")
        self.assertEqual(eb.position(-0.0301, b), "below")
        self.assertEqual(eb.position(0.0, b), "within")

    def test_a_rank_band_is_outside_all_draws_by_the_null_range(self) -> None:
        b = band(kind="rank", edge=None, grid=1 / 110, rng=3 / 110)
        self.assertEqual(eb.position(3 / 110, b), "within")
        self.assertEqual(eb.position(4 / 110, b), "above")
        self.assertEqual(eb.position(-4 / 110, b), "below")

    def test_a_dimension_without_a_band_does_not_position(self) -> None:
        b = {"kind": "none", "reason": "the null held 1 distinct value (σ = 0)"}
        self.assertEqual(eb.position(0.5, b), "no-band")
        self.assertEqual(eb.position(None, band(edge=1.0)), "missing")


class TestVerdict(unittest.TestCase):
    def test_nothing_outside_any_band_is_no_evidence(self) -> None:
        v = eb.calibrated_verdict(reading(100), reading(102, frames=31, share=0.46), bands())
        self.assertEqual(v["verdict"], "NO EVIDENCE")
        self.assertEqual({d: x["position"] for d, x in v["dims"].items()}, {"q1_seen": "within", "frames_filed": "within", "confirmed_share": "within"})

    def test_the_records_one_adoption_reads_no_evidence(self) -> None:
        # the law's own prediction (§5.2): #5's +2 items of 110 under an edge of about 3.6-5.5 items is NO EVIDENCE
        v = eb.calibrated_verdict(reading(90, frames=39, share=None), reading(92, frames=39, share=None), bands(q1_items=3.7))
        self.assertEqual(v["verdict"], "NO EVIDENCE")

    def test_one_reading_above_its_band_with_none_below_is_improved(self) -> None:
        v = eb.calibrated_verdict(reading(100), reading(107), bands())
        self.assertEqual(v["verdict"], "IMPROVED")
        self.assertEqual(v["dims"]["q1_seen"]["position"], "above")

    def test_a_reading_below_its_band_is_regressed_even_beside_one_above(self) -> None:
        v = eb.calibrated_verdict(reading(100, frames=30), reading(107, frames=24), bands())
        self.assertEqual(v["verdict"], "REGRESSED")
        self.assertEqual(v["dims"]["frames_filed"]["position"], "below")
        self.assertEqual(v["dims"]["q1_seen"]["position"], "above")
        self.assertIn("frames_filed", v["reason"])

    def test_a_missing_reading_is_neither_regression_nor_improvement(self) -> None:
        v = eb.calibrated_verdict(reading(100, share=None), reading(107, share=0.9), bands())
        self.assertEqual(v["dims"]["confirmed_share"]["position"], "missing")
        self.assertEqual(v["verdict"], "IMPROVED", "the q1 reading above its band still counts")
        v2 = eb.calibrated_verdict(reading(None, share=None), reading(107, share=None), bands())
        self.assertEqual(v2["verdict"], "NO EVIDENCE")

    def test_a_dimension_with_no_band_does_not_gate(self) -> None:
        b = bands(q1_seen={"kind": "none", "reason": "σ = 0"})
        v = eb.calibrated_verdict(reading(100), reading(60), b)
        self.assertEqual(v["dims"]["q1_seen"]["position"], "no-band")
        self.assertEqual(v["verdict"], "NO EVIDENCE", "a fall of 40 items cannot refuse a dimension that has no band — the law says so")
        v2 = eb.calibrated_verdict(reading(100, frames=30), reading(60, frames=40), b)
        self.assertEqual(v2["verdict"], "IMPROVED")

    def test_cost_regressed_needs_the_band_and_the_policy_cap(self) -> None:
        inc = reading(100, cpu=2000.0)
        # ratio 1.5: ln 0.405 > edge 0.25 AND > 1.2: regressed, even with q1 above
        v = eb.calibrated_verdict(inc, reading(107, cpu=3000.0), bands(ln_cpu=0.25))
        self.assertEqual(v["verdict"], "REGRESSED")
        self.assertTrue(v["cost"]["regressed"])
        # ratio 1.3 inside a wide band (edge 0.5): not regressed
        v = eb.calibrated_verdict(inc, reading(107, cpu=2600.0), bands(ln_cpu=0.5))
        self.assertFalse(v["cost"]["regressed"])
        self.assertEqual(v["verdict"], "IMPROVED")
        # ratio 1.15: outside a tight band (edge 0.05) but under the 1.2 cap: not regressed
        v = eb.calibrated_verdict(inc, reading(107, cpu=2300.0), bands(ln_cpu=0.05))
        self.assertFalse(v["cost"]["regressed"])
        self.assertEqual(v["verdict"], "IMPROVED")

    def test_a_cheaper_mutant_is_never_cost_regressed(self) -> None:
        v = eb.calibrated_verdict(reading(100, cpu=2000.0), reading(107, cpu=900.0), bands(ln_cpu=0.05))
        self.assertFalse(v["cost"]["regressed"])
        self.assertEqual(v["verdict"], "IMPROVED")

    def test_the_bands_high_side_decides_not_the_cap_alone_even_under_an_absurdly_low_cap(self) -> None:
        # the sweep's one survivor (a-cheaper-mutant-regresses) is EQUIVALENT for every cap >= 1: a ratio below 1 never exceeds it. A cap below 1 makes it
        # observable, so this pins that only the HIGH side of the band can regress the cost
        b = bands(ln_cpu=0.05)
        b["cost_policy_cap"] = 0.5
        v = eb.calibrated_verdict(reading(100, cpu=2000.0), reading(107, cpu=1200.0), b)       # ratio 0.6: below the band, above the silly cap
        self.assertEqual(v["cost"]["position"], "below")
        self.assertFalse(v["cost"]["regressed"])

    def test_without_a_cost_band_the_policy_cap_alone_decides(self) -> None:
        b = bands()
        del b["dims"]["ln_cpu"]
        self.assertEqual(eb.calibrated_verdict(reading(100, cpu=2000.0), reading(107, cpu=2300.0), b)["verdict"], "IMPROVED")
        self.assertEqual(eb.calibrated_verdict(reading(100, cpu=2000.0), reading(107, cpu=2600.0), b)["verdict"], "REGRESSED")

    def test_cpu_missing_on_a_side_is_a_missing_cost_not_a_regression(self) -> None:
        v = eb.calibrated_verdict(reading(100, cpu=None), reading(107, cpu=2600.0), bands())
        self.assertIsNone(v["cost"]["ratio"])
        self.assertFalse(v["cost"]["regressed"])
        self.assertEqual(v["verdict"], "IMPROVED")

    def test_swapping_the_two_sides_flips_the_verdict(self) -> None:
        # Δ is mutant − incumbent: the wiring plant that would swap them reads the opposite verdict
        a, b = reading(100), reading(107)
        self.assertEqual(eb.calibrated_verdict(a, b, bands())["verdict"], "IMPROVED")
        self.assertEqual(eb.calibrated_verdict(b, a, bands())["verdict"], "REGRESSED")

    def test_reward_and_act_and_sentence_never_enter_the_bar(self) -> None:
        a = reading(100, reward_mean=0.9, act_pass=True, sentence_pass=True)
        b = reading(101, reward_mean=0.0, act_pass=False, sentence_pass=False)
        v = eb.calibrated_verdict(a, b, bands())
        self.assertEqual(v["verdict"], "NO EVIDENCE", "act_pass True → False and a reward collapse cannot refuse: they are blind by construction")

    def test_the_reason_names_the_edges_in_items(self) -> None:
        v = eb.calibrated_verdict(reading(100), reading(107), bands(q1_items=5.5))
        self.assertAlmostEqual(v["dims"]["q1_seen"]["delta_grid"], 7.0)
        self.assertAlmostEqual(v["dims"]["q1_seen"]["edge_grid"], 5.5)
        self.assertEqual(v["dims"]["q1_seen"]["min_clear_grid"], 6)


class TestNotGradable(unittest.TestCase):
    def test_each_dead_dimension_is_printed_with_its_reason_and_presence_count(self) -> None:
        blk = eb.not_gradable_block(reading(100, sentence_pass=None), reading(100, sentence_pass=None))
        self.assertEqual(sorted(blk), ["act_pass", "reward_mean", "sentence_pass"])
        self.assertEqual(blk["reward_mean"]["present"], 2)
        self.assertTrue(blk["reward_mean"]["equal"])
        self.assertIn("identical by construction", blk["reward_mean"]["reason"])
        self.assertIn("identical by construction", blk["act_pass"]["reason"])
        self.assertEqual(blk["sentence_pass"]["present"], 0)
        self.assertEqual(blk["sentence_pass"]["missions"], 7)
        self.assertIn("needs ≥ 100 missions, the slice holds 7", blk["sentence_pass"]["reason"])

    def test_presence_counts_the_sides_that_carry_the_field(self) -> None:
        blk = eb.not_gradable_block(reading(100, reward_mean=0.5), reading(100, reward_mean=None))
        self.assertEqual(blk["reward_mean"]["present"], 1)
        self.assertFalse(blk["reward_mean"]["equal"])


class TestConfirm(unittest.TestCase):
    def first(self, verdict="IMPROVED", lo=1000, hi=1500, gene="KWTA.k", value=4):
        return {"gate": {"verdict": verdict}, "gene": gene, "value": value, "slice_from_seq": lo, "slice_to_seq": hi, "no": 6}

    def test_improved_twice_on_disjoint_slices_adopts(self) -> None:
        d = eb.confirm_decision(self.first(), self.first(lo=2000, hi=2500))
        self.assertTrue(d["adopt"])
        self.assertFalse(d["keep_pending"])

    def test_the_second_slice_may_start_exactly_where_the_first_ended(self) -> None:
        self.assertTrue(eb.confirm_decision(self.first(), self.first(lo=1500, hi=2000))["adopt"])

    def test_no_evidence_or_regressed_the_second_time_does_not_adopt(self) -> None:
        for v in ("NO EVIDENCE", "REGRESSED"):
            d = eb.confirm_decision(self.first(), self.first(verdict=v, lo=2000, hi=2500))
            self.assertFalse(d["adopt"], v)
            self.assertFalse(d["keep_pending"], v)
            self.assertIn(v, d["reason"])

    def test_an_overlapping_confirmation_slice_is_not_a_confirmation_and_keeps_the_pending(self) -> None:
        d = eb.confirm_decision(self.first(), self.first(lo=1400, hi=2000))
        self.assertFalse(d["adopt"])
        self.assertTrue(d["keep_pending"])
        self.assertIn("overlap", d["reason"])

    def test_a_different_mutation_is_not_a_confirmation(self) -> None:
        d = eb.confirm_decision(self.first(), self.first(gene="DELTA.lr", value=0.07, lo=2000, hi=2500))
        self.assertFalse(d["adopt"])
        d = eb.confirm_decision(self.first(), self.first(value=5, lo=2000, hi=2500))
        self.assertFalse(d["adopt"])

    def test_a_first_round_that_was_not_improved_has_nothing_to_confirm(self) -> None:
        d = eb.confirm_decision(self.first(verdict="NO EVIDENCE"), self.first(lo=2000, hi=2500))
        self.assertFalse(d["adopt"])


class TestBandsFile(unittest.TestCase):
    def test_a_round_trip_through_json_validates(self) -> None:
        b = bands()
        eb.validate_bands(json.loads(json.dumps(b)))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "BANDS.json"
            p.write_text(json.dumps(b))
            self.assertEqual(eb.load_bands(p)["dims"]["q1_seen"]["kind"], "normal")

    def test_a_malformed_file_is_refused_by_name(self) -> None:
        good = bands()
        for mutate in (
            lambda b: b.pop("dims"),
            lambda b: b["dims"]["q1_seen"].pop("kind"),
            lambda b: b["dims"]["q1_seen"].update(kind="gaussian"),
            lambda b: b["dims"]["q1_seen"].update(edge=-0.1),
            lambda b: b["dims"]["frames_filed"].update(edge=None),
            lambda b: b["dims"]["confirmed_share"].update(kind="rank", range=None),
            lambda b: b.pop("cost_policy_cap"),
            lambda b: b["dims"].pop("frames_filed"),
        ):
            b = json.loads(json.dumps(good))
            before = json.dumps(b, sort_keys=True)
            mutate(b)
            self.assertNotEqual(json.dumps(b, sort_keys=True), before, "the plant changed the bytes")
            with self.assertRaises(ValueError):
                eb.validate_bands(b)


class TestProposerRedraw(unittest.TestCase):
    def test_the_stream_starts_with_exactly_the_draw_mutation_draw(self) -> None:
        # the duplicate of draw_mutation's body is pinned to the original over a grid that reaches both kinds of gene
        kinds = set()
        for epoch in (1, 2, 3):
            for no in range(1, 61):
                first = next(ev.draw_stream(20261101, epoch, no))
                self.assertEqual(first, draw_mutation(20261101, epoch, no), (epoch, no))
                kinds.add(genes.BOUNDS[first[0]]["kind"])
        self.assertEqual(kinds, {"int", "float"})

    def test_the_known_collision_is_a_collision_and_is_redrawn(self) -> None:
        self.assertEqual(draw_mutation(20261101, 1, 3), ("BIRTH.misfires", 3))
        self.assertIn("misfires 3", V0, "the incumbent already carries BIRTH.misfires 3")
        text, key, value, draws = ev.mutate_distinct(V0, 20261101, 1, 3)
        self.assertNotEqual((key, value), ("BIRTH.misfires", 3))
        self.assertGreaterEqual(draws, 2)
        self.assertNotEqual(text, V0)
        # the redraw is the SAME generator's next draws
        stream = ev.draw_stream(20261101, 1, 3)
        self.assertEqual(next(stream), ("BIRTH.misfires", 3))
        self.assertEqual((key, value), next(stream))

    def test_a_non_colliding_draw_is_unchanged_from_mutate_genome_text(self) -> None:
        n_same = 0
        for epoch, base in ((1, V0), (2, V1), (3, V1)):
            for no in range(1, 51):
                old_text, old_key, old_value = mutate_genome_text(base, 20261101, epoch, no)
                text, key, value, draws = ev.mutate_distinct(base, 20261101, epoch, no)
                if draws == 1:
                    n_same += 1
                    self.assertEqual((text, key, value), (old_text, old_key, old_value), (epoch, no))
        self.assertGreater(n_same, 130, "most draws are untouched")

    def test_c5_the_proposer_never_emits_the_incumbents_value_over_150_draws(self) -> None:
        raw = redrawn = 0
        for epoch, base in ((1, V0), (2, V1), (3, V1)):
            for no in range(1, 51):
                k0, v0 = draw_mutation(20261101, epoch, no)
                raw += int(_collides(base, k0, v0))
                text, key, value, draws = ev.mutate_distinct(base, 20261101, epoch, no)
                redrawn += int(_collides(base, key, value))
        self.assertGreaterEqual(raw, 1, "the check can fire: the raw proposer collides at least once (the (20261101, 1, 3) draw)")
        self.assertEqual(redrawn, 0, "C5: 0 of 150")

    def test_the_redraw_is_bounded_and_refuses_a_text_that_cannot_differ(self) -> None:
        # a gene range of one value cannot be redrawn away from: the call must stop, not loop
        spec = genes.BOUNDS["KWTA.k"]
        saved = (spec["lo"], spec["hi"])
        try:
            spec["lo"], spec["hi"] = 4, 4
            with unittest.mock.patch.object(ev, "MUTABLE_KEYS", ("KWTA.k",)):
                with self.assertRaises(RuntimeError):
                    ev.mutate_distinct(V1, 20261101, 2, 1, max_draws=50)
        finally:
            spec["lo"], spec["hi"] = saved


def _gene(text: str, key: str) -> str:
    import tools.evolve_cal as cal
    return cal.gene_text(text, key)


def _fmt_value(key: str, value) -> str:
    spec = genes.BOUNDS[key]
    return str(int(round(value))) if spec["kind"] == "int" else f"{float(value):.{int(spec['decimals'])}f}"


def _collides(text: str, key: str, value) -> bool:
    """The drawn value, printed as the genome prints it, equals the number the incumbent text already carries."""
    return float(_fmt_value(key, value)) == float(_gene(text, key))


# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 23:03 +0400 — A′, the seat's ruling on A3.7 (22:32; binding only if A0/A0+ read the null degenerate): a gated dimension WITHOUT a
# measured band keeps the LEGACY tolerance — any fall REGRESSES, a rise needs its margin (tools/evolve.py MARGINS: q1_seen +0.01 = 2 items of 110, confirmed_share +0.02, frames_filed
# +1). The band file says so with a `legacy` field on a `none` band; a `none` band without it still does not gate (reading A). Tests FIRST.
def legacy_band(margin, grid=None):
    return {"kind": "none", "grid": grid, "reason": "the null held fewer than 3 distinct values (A1 (i))", "legacy": {"fall": "any", "rise_margin": margin}}


# the 13 rounds of brain-long-2 as the verifier re-read them (verify/evolve-cal-a3/v6_rereads.out): PREREG-EVOLVE-CAL §0's table gives q1_seen (items of 110) and frames_filed, records/e3/e3-regrade.json
# gives confirmed_share's Δ; (round, Δ q1 items, Δ frames, Δ confirmed_share, the verifier's A′ verdict). Under A′: 1 IMPROVED, 8 REGRESSED, 4 NO EVIDENCE.
ROUNDS_A_PRIME = [(2, -4, +6, -0.0053, "REGRESSED"), (3, 0, 0, 0.0, "NO EVIDENCE"), (4, -7, +2, -0.0310, "REGRESSED"), (5, +2, 0, +0.0030, "IMPROVED"),
                  (6, 0, 0, 0.0, "NO EVIDENCE"), (7, -2, 0, -0.0023, "REGRESSED"), (8, -2, -3, -0.0008, "REGRESSED"), (9, +1, 0, +0.0037, "NO EVIDENCE"),
                  (10, -8, 0, +0.0030, "REGRESSED"), (11, 0, 0, +0.0028, "NO EVIDENCE"), (12, +2, -2, -0.0025, "REGRESSED"), (13, -2, 0, +0.0162, "REGRESSED"),
                  (14, 0, -1, -0.0208, "REGRESSED")]


class TestLegacyTolerance(unittest.TestCase):
    def test_a_fall_of_any_size_is_below_and_a_rise_needs_its_margin_on_a_grid_dimension(self) -> None:
        b = legacy_band(0.01, grid=1 / 110)
        self.assertEqual(eb.position(-1 / 110, b), "below", "any fall regresses")
        self.assertEqual(eb.position(0.0, b), "within")
        self.assertEqual(eb.position(1 / 110, b), "within", "one item (0.0091) is under the 0.01 margin")
        self.assertEqual(eb.position(2 / 110, b), "above", "two items clear it")
        self.assertEqual(eb.position(8 / 110, b), "above")
        self.assertEqual(eb.position(None, b), "missing")
        self.assertEqual(eb.position(-1e-15, b), "within", "float noise below one grid step is not a fall of one item")
        self.assertEqual(eb.position(0.0105, b), "within", "round(Δ / grid) first: 0.0105 is one item (0.0091), under the 0.01 margin; unrounded it would clear it")

    def test_a_continuous_dimension_falls_on_any_negative_and_rises_at_its_margin(self) -> None:
        b = legacy_band(0.02)
        self.assertEqual(eb.position(-1e-6, b), "below")
        self.assertEqual(eb.position(0.0, b), "within")
        self.assertEqual(eb.position(0.0199, b), "within")
        self.assertEqual(eb.position(0.02, b), "above", "mv >= iv + margin, as tools/evolve.py regression_bar reads it")
        self.assertEqual(eb.position(0.47 - 0.45, b), "above", "float noise in a difference of two readings does not move one across the margin")

    def test_integer_frames_rise_at_one_frame_and_fall_at_any(self) -> None:
        b = legacy_band(1, grid=1.0)
        self.assertEqual([eb.position(d, b) for d in (-1.0, 0.0, 1.0, 2.0)], ["below", "within", "above", "above"])

    def test_the_legacy_field_is_read_only_on_a_none_band(self) -> None:
        b = band(edge=5.5 / 110, grid=1 / 110)
        b["legacy"] = {"fall": "any", "rise_margin": 0.01}
        self.assertEqual(eb.position(-1 / 110, b), "within", "a measured band rules; the legacy field on it is ignored")
        self.assertEqual(eb.position(-7 / 110, b), "below")

    def test_a_none_band_without_the_legacy_field_still_does_not_gate(self) -> None:
        self.assertEqual(eb.position(-0.5, {"kind": "none", "grid": None, "reason": "x"}), "no-band")

    def test_the_verdict_regresses_on_one_item_and_improves_only_on_two(self) -> None:
        b = bands(q1_seen=legacy_band(0.01, grid=1 / 110), confirmed_share=legacy_band(0.02))
        self.assertEqual(eb.calibrated_verdict(reading(100), reading(99), b)["verdict"], "REGRESSED")
        self.assertEqual(eb.calibrated_verdict(reading(100), reading(101), b)["verdict"], "NO EVIDENCE")
        self.assertEqual(eb.calibrated_verdict(reading(100), reading(102), b)["verdict"], "IMPROVED")
        self.assertEqual(eb.calibrated_verdict(reading(100, share=0.45), reading(100, share=0.44), b)["verdict"], "REGRESSED")
        self.assertEqual(eb.calibrated_verdict(reading(100, share=0.45), reading(100, share=0.48), b)["verdict"], "IMPROVED")
        v = eb.calibrated_verdict(reading(100), reading(101), b)
        self.assertIn("legacy", v["reason"])
        self.assertEqual(v["dims"]["q1_seen"]["legacy_rise_margin"], 0.01)
        self.assertIsNone(eb.calibrated_verdict(reading(100), reading(101), bands())["dims"]["q1_seen"]["legacy_rise_margin"], "a measured band carries no legacy margin")

    def test_a_fall_beside_a_rise_regresses(self) -> None:
        b = bands(q1_seen=legacy_band(0.01, grid=1 / 110), confirmed_share=legacy_band(0.02))
        self.assertEqual(eb.calibrated_verdict(reading(100, share=0.45), reading(110, share=0.44), b)["verdict"], "REGRESSED")

    def test_c2_and_c3_stay_reachable_under_a_prime(self) -> None:
        b = bands(q1_seen=legacy_band(0.01, grid=1 / 110), confirmed_share=legacy_band(0.02), frames=100.0)
        self.assertEqual(eb.calibrated_verdict(reading(104), reading(96), b)["verdict"], "REGRESSED", "C2: P-BAD, a fall of 8 items")
        self.assertEqual(eb.calibrated_verdict(reading(96), reading(104), b)["verdict"], "IMPROVED", "C3: P-GOOD's restoration, +8 items against a margin of 2")

    def test_the_thirteen_recorded_rounds_reread_under_a_prime_as_the_verifier_read_them(self) -> None:
        b = bands(q1_seen=legacy_band(0.01, grid=1 / 110), confirmed_share=legacy_band(0.02), frames=100.0)
        got = []
        for no, dq, dfr, dcs, want in ROUNDS_A_PRIME:
            v = eb.calibrated_verdict(reading(100, frames=30, share=0.45), reading(100 + dq, frames=30 + dfr, share=0.45 + dcs), b)
            self.assertEqual(v["verdict"], want, f"round {no}: {v['reason']}")
            got.append(v["verdict"])
        self.assertEqual({k: got.count(k) for k in set(got)}, {"REGRESSED": 8, "NO EVIDENCE": 4, "IMPROVED": 1})

    def test_the_replay_table_matches_the_committed_e3_record_for_confirmed_share(self) -> None:
        # the Δ column is read from records/e3 (confirmed_share) and never typed alone: a table that drifted from its source fails here
        rec = json.loads((ROOT / "docs" / "organism" / "evolve" / "records" / "e3" / "e3-regrade.json").read_text())
        by_round = {r["round"]: r["confirmed_share"]["delta"] for r in rec["rounds"]}
        for no, _dq, _dfr, dcs, _want in ROUNDS_A_PRIME:
            self.assertAlmostEqual(by_round[no], dcs, places=4, msg=f"round {no}")


class TestLegacyBandsFile(unittest.TestCase):
    def test_a_legacy_field_validates_on_a_none_band_and_is_refused_elsewhere(self) -> None:
        good = bands(q1_seen=legacy_band(0.01, grid=1 / 110))
        eb.validate_bands(json.loads(json.dumps(good)))
        for mutate in (
            lambda b: b["dims"]["q1_seen"].update(kind="normal", edge=0.05),
            lambda b: b["dims"]["q1_seen"]["legacy"].update(rise_margin=-0.01),
            lambda b: b["dims"]["q1_seen"]["legacy"].update(rise_margin="0.01"),
            lambda b: b["dims"]["q1_seen"]["legacy"].update(rise_margin=True),
            lambda b: b["dims"]["q1_seen"]["legacy"].pop("rise_margin"),
            lambda b: b["dims"]["q1_seen"].update(legacy="any fall"),
            lambda b: b["dims"]["q1_seen"]["legacy"].update(fall="never"),
        ):
            b = json.loads(json.dumps(good))
            before = json.dumps(b, sort_keys=True)
            mutate(b)
            self.assertNotEqual(json.dumps(b, sort_keys=True), before, "the plant changed the bytes")
            with self.assertRaises(ValueError):
                eb.validate_bands(b)


if __name__ == "__main__":
    unittest.main()
