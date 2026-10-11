# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 12:4x +0400 — the N2 bench's own tests
# (PREREG-N2-TRAJECTORY §2's instrument discipline, test_precision_bench.py's form): the world slice is
# deterministic to the last float; the derangement twin keeps the diff multiset and kills the order; the
# frozen-r plant reads w == 1 and tpe == spe EXACTLY; the ramp injection consumes le + s*k pinned against
# a manually stepped twin; the margin helper's arithmetic pinned on a scripted stream; the report carries
# every mark of the law with presence counts (never a bare number).
from __future__ import annotations

import unittest

import numpy as np

from genome.machinery import Organism, parse_genome
from genome.predict import Predictor
from tools.brain.precision_bench import BENCH_SEED, N_A, N_B, build_rows
from tools.brain.trajectory_bench import (LEARN_STRETCHES, NULL_SEEDS, PILOT_SEED, RAMP_SLOPE, TOY,
                                          FrozenRPredictor, RampPredictor, drive, path_margin,
                                          pilot_readings, twin_run, twin_stream, verdicts)


class TestTrajectoryBench(unittest.TestCase):
    def test_world_slice_deterministic(self) -> None:
        g = parse_genome(TOY)
        rows_a = build_rows(g, BENCH_SEED)[:N_A + N_B]
        rows_b = build_rows(g, BENCH_SEED)[:N_A + N_B]
        self.assertEqual(len(rows_a), N_A + N_B, "presence: the law's phases A+B and no more")
        same = sum(1 for (ka, ta, xa), (kb, tb, xb) in zip(rows_a, rows_b)
                   if ka == kb and ta == tb and np.array_equal(xa, xb))
        self.assertEqual(same, len(rows_a), "two builds of the declared seed are identical to the last bit")

    def test_twin_keeps_distribution_destroys_order(self) -> None:
        g = parse_genome(TOY)
        recs, _ = drive(build_rows(g, BENCH_SEED)[:N_A + N_B], g)
        le_a = [r["le"] for r in recs[:N_A]]
        le_b = [r["le"] for r in recs[N_A:N_A + N_B]]
        twin = twin_stream(le_a, le_b, NULL_SEEDS[0])
        self.assertEqual(len(twin), N_A + N_B, "the twin keeps the row count")
        for le_phase, twin_phase in ((le_a, twin[:N_A]), (le_b, twin[N_A:])):
            real_diffs = sorted(np.diff(le_phase).tolist())
            twin_diffs = sorted(np.diff(twin_phase).tolist())
            self.assertEqual(len(real_diffs), len(twin_diffs))
            for rd, td in zip(real_diffs, twin_diffs):
                self.assertAlmostEqual(rd, td, places=12,
                                       msg="the diff MULTISET is kept per phase to rebuild dust "
                                           "(the distribution kept; cumsum->diff returns the permuted "
                                           "diffs to ~1e-15 relative, never bit-exact)")
            self.assertNotEqual(np.diff(le_phase).tolist(), np.diff(twin_phase).tolist(),
                                "the order is destroyed (the trends killed)")
            self.assertAlmostEqual(twin_phase[-1], le_phase[-1], places=8,
                                   msg="the endpoint is preserved to float dust (the variation sums equal)")
            self.assertEqual(twin_phase[0], le_phase[0], "each phase starts at the real le[0]")
        twin2 = twin_stream(le_a, le_b, NULL_SEEDS[0])
        self.assertEqual(twin, twin2, "the fixed seeds make the twins deterministic")
        twin3 = twin_stream(le_a, le_b, NULL_SEEDS[1])
        self.assertNotEqual(twin, twin3, "distinct seeds draw distinct twins")

    def test_plant_register_frozen_r(self) -> None:
        """The doctored register reads w == 1.0 EXACTLY and tpe == spe EXACTLY over a real drive —
        G-PLANT's planted form caught by construction here, caught by the bench's M-PATH at full scale."""
        g = parse_genome(TOY)
        rows = build_rows(g, BENCH_SEED)[:80]
        recs = drive(rows, g, cls=FrozenRPredictor)[0]
        ws = [r["w"] for r in recs]
        self.assertTrue(all(w is not None for w in ws), "presence: the plant arm reads weights")
        self.assertTrue(all(w == 1.0 for w in ws), f"the frozen-r register must read w == 1, got {sorted(set(ws))[:5]}")
        self.assertTrue(all(r["tpe"] == r["spe"] for r in recs), "r == 0: the path and the point read the same")

    def test_ramp_injection_arithmetic(self) -> None:
        """The ramped register consumes le + s*k exactly: pinned against a manually stepped twin fed the
        planted stream by hand; k counts RAMPED calls only."""
        g = parse_genome(TOY)
        ramped = RampPredictor(Organism(g), trajectory=True, slope=RAMP_SLOPE)
        manual = Predictor(Organism(g), trajectory=True)
        c = -1.0
        ramped._trajectory_step(c)                       # not ramping yet: k stays 0
        manual._trajectory_step(c)
        ramped.ramping = True
        for k in range(5):                               # ramped calls add s*0, s*1, ... (k counts ramped calls)
            ramped._trajectory_step(c)
            manual._trajectory_step(c + RAMP_SLOPE * k)
            self.assertEqual(ramped._t_m, manual._t_m, "the value register reads the planted stream")
            self.assertEqual(ramped._t_r, manual._t_r, "the rate register reads the planted stream")
            self.assertEqual(ramped.last_tpe, manual.last_tpe, "tpe is taken against the planted stream")
            self.assertEqual(ramped.last_spe, manual.last_spe, "spe is taken against the planted stream")
        self.assertEqual(ramped._ramp_k, 5, "k counted the RAMPED calls only")

    def test_margin_helper_arithmetic(self) -> None:
        """path_margin on a scripted stream: mean|spe| - mean|tpe| over the pooled stretches, computed by
        hand — the instrument's own arithmetic pinned."""
        g = parse_genome(TOY)
        pred = Predictor(Organism(g), trajectory=True)
        recs = []
        for i in range(200):
            pred._trajectory_step(-1.0 + 0.01 * i)       # a scripted rising ramp
            recs.append({"i": i, "tpe": pred.last_tpe, "spe": pred.last_spe})
        got = path_margin(recs)
        want_tpe = [r["tpe"] for r in recs if any(lo <= r["i"] < hi for lo, hi in LEARN_STRETCHES)]
        want_spe = [r["spe"] for r in recs if any(lo <= r["i"] < hi for lo, hi in LEARN_STRETCHES)]
        self.assertEqual(got["n"], 200, "both stretches pooled (100 + 100)")
        self.assertEqual(got["margin"],
                         float(np.mean(np.abs(want_spe))) - float(np.mean(np.abs(want_tpe))))
        self.assertGreater(got["margin"], 0.0, "on a rising ramp the path must beat the point (the law's arithmetic)")

    def test_report_carries_all_marks(self) -> None:
        """verdicts() returns every mark of the law with presence counts — never a bare number."""
        g = parse_genome(TOY)
        rows = build_rows(g, BENCH_SEED)[:N_A + N_B]
        arms = {"real": drive(rows, g), "off": drive(rows, g, trajectory=False),
                "plant": drive(rows, g, cls=FrozenRPredictor), "ramp": drive(rows, g, cls=RampPredictor)}
        le_a = [r["le"] for r in arms["real"][0][:N_A]]
        le_b = [r["le"] for r in arms["real"][0][N_A:N_A + N_B]]
        twins = []
        for s in NULL_SEEDS[:2]:
            trecs = twin_run(twin_stream(le_a, le_b, s), g)
            twins.append({"seed": s, "margin": path_margin(trecs)["margin"], "recs": trecs})
        pilot = pilot_readings(build_rows(g, PILOT_SEED)[:N_A + N_B], g)
        eps = max(0.005, 2.0 * pilot["phaseB_gap"])
        v, cost = verdicts(arms, twins, eps)
        for mark in ("M-PATH", "M-STAT", "M-RAMP", "M-SCALE", "M-COST", "G-PLANT"):
            self.assertIn(mark, v, f"the report carries {mark}")
            self.assertIn("bar", v[mark])
            self.assertIn("pass", v[mark])
        self.assertEqual(v["M-PATH"]["n"], 200, "M-PATH's presence count is the pooled stretches")
        self.assertEqual(v["M-STAT"]["n"], N_B, "M-STAT's presence count is phase B's length")
        self.assertEqual(v["M-RAMP"]["n_tail"], 100, "M-RAMP's tail presence")
        self.assertEqual(v["M-SCALE"]["n"], N_A + N_B, "M-SCALE spans the whole run")
        self.assertIn("cpu_real_s", cost)
        # G-PLANT's substance: the frozen-r margin is dead against the real one
        self.assertLess(v["G-PLANT"]["plant_margin"], v["M-PATH"]["margin"],
                        "the plant's margin dies where the mechanism's lives")


if __name__ == "__main__":
    unittest.main()
