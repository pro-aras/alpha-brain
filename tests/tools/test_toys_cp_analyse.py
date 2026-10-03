"""Tests for TOY A's analysis: on a SYNTHETIC world of lives, the verdict machinery must classify a planted winner, a planted escaper, a locked-in noisy arm and a
blind arm correctly — the instrument's own positive and negative controls (#247 (5)).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:36 +0400 — written FIRST (red before report.analyse exists); law: PREREG-TOY-CP §5 and AMEND-1 §4–§5.

The synthetic world: ten seeds, RANDOM 20 lives a seed (A ~ N(0.55, 0.025), SHARE_N ~ N(0.25, 0.03)), R-ONLY 20 (A ~ N(0.68, 0.025), SHARE_N 0), ERROR 10 (A 0.15,
SHARE_N 0.72), N-ONLY 1 (A 0.05), and the nine arms as planted below, 10 replicates each.
"""
from __future__ import annotations

import unittest

import numpy as np

from tools.toys.cp import estimators as ES
from tools.toys.cp import report as RP

SEEDS = list(range(20261301, 20261311))


def life(a, sn, snl=None, lock=5, m1=0.9):
    return {"A": float(a), "SN": float(sn), "SNL": float(sn if snl is None else snl), "lock": lock, "M1": m1,
            "LR": {"R1": 0.8, "R2": 0.8, "R3": 0.8}, "LRfinal": {"R1": 0.9, "R2": 0.9, "R3": 0.9}, "histN": [sn] * 10,
            "ear_full_first": 12, "ear_last_wrong": 11, "ear_end_ok": True}


def world(planted, seed=7):
    """planted: {arm: (A mean, A sd, SN mean, SN sd)} for the nine arms; the controls are fixed."""
    rng = np.random.default_rng(seed)
    arms = {}

    def put(name, n, am, asd, sm, ssd):
        arms[name] = {s: [life(rng.normal(am, asd), max(0.0, rng.normal(sm, ssd))) for _ in range(n)] for s in SEEDS}

    put("RANDOM", 20, 0.55, 0.025, 0.25, 0.03)
    put("R-ONLY", 20, 0.68, 0.025, 0.0, 0.0)
    put("ERROR", 10, 0.15, 0.01, 0.72, 0.02)
    put("N-ONLY", 1, 0.05, 0.0, 1.0, 0.0)
    for name, (am, asd, sm, ssd) in planted.items():
        put(name, 10, am, asd, sm, ssd)
    return arms


PLANTED = {
    "L-own-last2": (0.55, 0.025, 0.25, 0.03),      # = RANDOM: must pass nothing
    "L-own-ema": (0.60, 0.025, 0.18, 0.03),        # a modest real gain and a modest escape: passes both bars
    "L-hist-last2": (0.30, 0.03, 0.80, 0.03),      # trapped: worse than random
    "L-hist-ema": (0.20, 0.03, 0.85, 0.03),
    "C-own-last2": (0.55, 0.025, 0.25, 0.03),
    "C-own-ema": (0.55, 0.025, 0.25, 0.03),
    "C-hist-last2": (0.66, 0.025, 0.02, 0.01),     # the planted winner: near R-ONLY
    "C-hist-ema": (0.62, 0.20, 0.10, 0.20),        # a LOCKED-IN noisy arm: a replicate SD far above RANDOM's -> FLAGGED
    "LP-OUDEYER": (0.55, 0.025, 0.25, 0.03),
}


class TestAnalyse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arms = world(PLANTED)
        cls.an = RP.analyse(cls.arms, SEEDS, draws=3000)

    def test_positive_controls_hold_on_the_world(self):
        pc = self.an["controls"]
        self.assertTrue(pc["PC1"]["ok"])           # R-ONLY beats RANDOM by ~0.13 at every seed
        self.assertTrue(pc["PC2"]["ok"])           # ERROR is trapped
        self.assertTrue(pc["PC3"]["ok"])           # N-ONLY far below RANDOM's band
        self.assertTrue(pc["gradable"])

    def test_the_planted_winner_passes_both_bars(self):
        a = self.an["arms"]["C-hist-last2"]
        self.assertTrue(a["BEAT"], a)
        self.assertTrue(a["LEAVE"], a)
        self.assertGreater(a["escaped_share"], 0.5)

    def test_random_like_arms_pass_nothing(self):
        for name in ("L-own-last2", "C-own-last2", "C-own-ema", "LP-OUDEYER"):
            a = self.an["arms"][name]
            self.assertFalse(a["BEAT"], name)
            self.assertFalse(a["LEAVE"], name)

    def test_trapped_arms_are_below_random_and_do_not_leave(self):
        for name in ("L-hist-last2", "L-hist-ema"):
            a = self.an["arms"][name]
            self.assertFalse(a["BEAT"], name)
            self.assertFalse(a["LEAVE"], name)
            self.assertLess(a["D"], 0)

    def test_the_locked_in_noisy_arm_is_flagged_and_judged_by_the_sign_count_alone(self):
        a = self.an["arms"]["C-hist-ema"]
        self.assertTrue(a["sd_flag_A"] or a["sd_flag_N"], a)
        self.assertGreater(a["sd_ratio_A"], 2.0)

    def test_an_ema_cell_is_read_on_the_held_out_seeds_too(self):
        a = self.an["arms"]["L-own-ema"]
        self.assertIsNotNone(a["held_out"])
        self.assertEqual(a["held_out"]["n_seeds"], 7)
        self.assertIsNone(self.an["arms"]["L-own-last2"]["held_out"])      # last2 cells and LP are not ema cells: no held-out reading

    def test_contaminated_when_it_holds_on_all_seeds_but_not_on_04_to_10(self):
        # a planted arm whose gain exists ONLY on seeds 01-03
        arms = world(PLANTED)
        rng = np.random.default_rng(9)
        for s in SEEDS:
            gain = 0.08 if s <= 20261303 else 0.0
            arms["L-own-ema"][s] = [life(rng.normal(0.55 + gain, 0.02), max(0.0, rng.normal(0.25 - 3 * gain, 0.02))) for _ in range(10)]
        an = RP.analyse(arms, SEEDS, draws=3000)
        a = an["arms"]["L-own-ema"]
        self.assertFalse(a["held_out"]["BEAT"])
        self.assertTrue(a["CONTAMINATED"] or not a["BEAT"], a)             # it must never be counted clean

    def test_verdict_class_names_the_planted_winner_and_asks_for_stage_2(self):
        v = self.an["verdict"]
        self.assertIn("C-hist-last2", v["stage2_arms"])
        self.assertEqual(v["class"], "FIXED-PENDING-STAGE-2")

    def test_a_world_with_no_choice_is_not_gradable(self):
        planted = dict(PLANTED)
        arms = world(planted)
        rng = np.random.default_rng(3)
        arms["R-ONLY"] = {s: [life(rng.normal(0.55, 0.025), 0.0) for _ in range(20)] for s in SEEDS}      # R-ONLY = RANDOM: escaping noise buys nothing
        an = RP.analyse(arms, SEEDS, draws=2000)
        self.assertFalse(an["controls"]["gradable"])
        self.assertEqual(an["verdict"]["class"], "NOT-GRADABLE")

    def test_main_effects_of_the_planted_world_point_the_right_way(self):
        me = self.an["main_effects_A"]
        self.assertGreater(me["scope"]["mean"], -1.0)                      # present and finite
        for f in ("loss", "scope", "time"):
            self.assertIn(f, me)
            self.assertEqual(len(me[f]["per_seed"]), 10)

    def test_escaped_share_is_not_clipped_in_the_analysis(self):
        arms = world(PLANTED)
        rng = np.random.default_rng(5)
        arms["C-hist-last2"] = {s: [life(rng.normal(0.80, 0.02), 0.0) for _ in range(10)] for s in SEEDS}   # beats R-ONLY (0.68)
        an = RP.analyse(arms, SEEDS, draws=2000)
        self.assertGreater(an["arms"]["C-hist-last2"]["escaped_share"], 1.0)

    def test_render_runs_on_the_synthetic_world_and_prints_the_verdict(self):
        rows = [{"block": b, "room": "N" if b % 4 == 0 else "R1", "own": {"total": 1.0, "bias": 0.7, "weight": 0.1, "stats": 0.05},
                 "hist": {"total": 0.5, "bias": 0.3, "weight": 0.05, "stats": 0.02}} for b in range(1, 201)]
        counts = {a: sum(len(v) for v in self.arms[a].values()) for a in self.arms}
        text = "\n".join(RP.render(self.an, self.arms, rows, counts, SEEDS))
        self.assertIn("VERDICT CLASS: FIXED-PENDING-STAGE-2", text)
        self.assertIn("THE CONTROLS", text)
        self.assertIn("HELD-OUT READING", text)
        self.assertIn("THE DROP'S ANATOMY", text)
        self.assertIn("HOLDS", text)                                          # the planted anatomy: bias is the majority in N's blocks

    def test_summarise_life_on_a_real_short_life(self):
        from brain.scene import run_s1c as S
        from tools.toys.common import pools as POOLS
        from tools.toys.cp import life as LF
        if not all(POOLS.present(POOLS.ROOT, 20261301).values()):
            self.skipTest("pools absent")
        data = S.RoomData(POOLS.ROOT, 20261301, list(S.WORLDS["law"]))
        rec = LF.life_cp(data, S.FixedTestSet(), ES.make_arm("C-hist-ema", list(S.WORLDS["law"]), 20261301, 0), "C-hist-ema", list(S.WORLDS["law"]), n_blocks=30)
        s = RP.summarise_life(rec)
        self.assertTrue(0.0 <= s["A"] <= 1.0)
        self.assertEqual(set(s["LR"]), {"R1", "R2", "R3"})
        self.assertEqual(len(s["histN"]), 10)
        self.assertIsNotNone(s["ear_end_ok"])
        self.assertIn(s["ear_full_first"], [None] + list(range(1, 31)))

    def test_load_all_reads_a_tree_of_real_records(self):
        """The loader on records written by the real life (found by the smoke on the unit's own files: `Path` was never imported in report.py)."""
        import tempfile
        import shutil
        from pathlib import Path as P
        from brain.scene import run_s1c as S
        from tools.toys.common import pools as POOLS
        from tools.toys.cp import life as LF
        from tools.toys.cp import run as RUN
        if not all(POOLS.present(POOLS.ROOT, 20261301).values()):
            self.skipTest("pools absent")
        rooms = list(S.WORLDS["law"])
        data, test = S.RoomData(POOLS.ROOT, 20261301, rooms), S.FixedTestSet()
        root = P(tempfile.mkdtemp())
        try:
            for arm, rep in (("RANDOM", 1), ("L-own-ema", 0)):
                rec = LF.life_cp(data, test, ES.make_arm(arm, rooms, 20261301, rep), arm, rooms, n_blocks=12, decompose=(arm == "RANDOM"), rep=rep)
                RUN.write_json(root / arm / "20261301" / f"{rep:02d}.json", rec)
            arms, decomp, counts = RP.load_all(root, [20261301])
            self.assertEqual(counts, {"RANDOM": 1, "L-own-ema": 1})
            self.assertEqual(len(decomp), 12)                                   # RANDOM's anatomy rows
            self.assertEqual(set(arms), {"RANDOM", "L-own-ema"})
            self.assertTrue(0.0 <= arms["RANDOM"][20261301][0]["A"] <= 1.0)
        finally:
            shutil.rmtree(root)

    def test_the_anatomy_summary_reads_the_planted_split(self):
        rows = []
        for b in range(5, 205):
            room = "N" if b % 4 == 0 else "R1"
            rows.append({"block": b, "room": room, "own": {"total": 1.0, "bias": 0.8 if room == "N" else 0.1, "weight": 0.1, "stats": 0.05},
                         "hist": {"total": 0.5, "bias": 0.4, "weight": 0.05, "stats": 0.02}})
        an = RP.anatomy(rows)
        self.assertGreater(an["N"]["own"]["share_bias"], 0.5)
        self.assertLess(an["R"]["own"]["share_bias"], 0.5)
        self.assertTrue(an["mechanism_holds"])
        flipped = [{**r, "own": {**r["own"], "bias": 0.1 if r["room"] == "N" else 0.8}} for r in rows]
        self.assertFalse(RP.anatomy(flipped)["mechanism_holds"])           # the plant: bias is NOT the majority in N's blocks -> refuted


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 12:17 +0400 — STAGE 2 of the signed law (PREREG-TOY-CP §6: «for each arm that passes BEAT, its NULL … 10 replicates ×
# 10 seeds; the arm is VOID if its NULL also passes BEAT»; §5: «FIXED — some arm passes BEAT and LEAVE and its NULL (stage 2) does not pass BEAT»). Written FIRST: the stage-1
# report printed «FIXED-PENDING-STAGE-2» and had no code that read a NULL. «Passes BEAT» for the NULL is the PLAIN 10-seed bar (p ≤ 0.0056 AND d_s > 0 at ≥ 8 of 10, ≥ 9 if
# its replicate SD is flagged): the lenient reading, so that a doubtful null can only make the verdict MORE conservative; the held-out-counted form is printed beside it.
class TestStage2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = world(PLANTED)
        cls.an0 = RP.analyse(cls.base, SEEDS, draws=3000)
        cls.s2 = list(cls.an0["verdict"]["stage2_arms"])

    def with_nulls(self, spec, seed=21, reps=10):
        """spec: {arm: (A mean, A sd, SN mean, SN sd)} → the world plus a NULL-<arm> (10 replicates a seed) for each."""
        rng = np.random.default_rng(seed)
        arms = dict(self.base)
        for arm, (am, asd, sm, ssd) in spec.items():
            arms["NULL-" + arm] = {s: [life(rng.normal(am, asd), max(0.0, rng.normal(sm, ssd))) for _ in range(reps)] for s in SEEDS}
        return arms

    BLIND = (0.55, 0.025, 0.25, 0.03)        # the NULL blind to WHERE: RANDOM-like
    STRONG = (0.66, 0.02, 0.02, 0.01)        # a null that gains as much as the winner: the credit's address did not matter

    def test_the_planted_world_asks_for_stage_2_and_names_the_winner(self):
        self.assertIn("C-hist-last2", self.s2)
        self.assertEqual(self.an0["verdict"]["class"], "FIXED-PENDING-STAGE-2")
        self.assertEqual(sorted(self.an0["stage2"]["missing"]), sorted(self.s2))      # no NULL record yet: every arm is missing

    def test_nulls_that_are_blind_leave_the_arms_fixed(self):
        an = RP.analyse(self.with_nulls({a: self.BLIND for a in self.s2}), SEEDS, draws=3000)
        s2 = an["stage2"]["arms"]["C-hist-last2"]
        self.assertFalse(s2["beat"], s2)
        self.assertFalse(s2["void"], s2)
        self.assertEqual(an["stage2"]["missing"], [])
        self.assertEqual(an["verdict"]["class"], "FIXED")
        self.assertIn("C-hist-last2", an["verdict"]["fixed_arms"])
        self.assertGreaterEqual(s2["gain_signs"], 8)                                   # the arm beats its own null at ≥ 8 of 10 seeds

    def test_a_null_that_gains_as_much_voids_the_arm_and_the_decision_flips(self):
        blind = RP.analyse(self.with_nulls({a: self.BLIND for a in self.s2}), SEEDS, draws=3000)["stage2"]["arms"]["C-hist-last2"]
        an = RP.analyse(self.with_nulls({a: self.STRONG for a in self.s2}), SEEDS, draws=3000)
        strong = an["stage2"]["arms"]["C-hist-last2"]
        self.assertTrue(strong["beat"], strong)
        self.assertTrue(strong["void"], strong)
        self.assertNotEqual(blind["void"], strong["void"])                             # the plant changes the decision: the check is not blind
        self.assertGreater(strong["D"], strong["smallest_D"])
        self.assertEqual(an["verdict"]["fixed_arms"], [])
        self.assertEqual(an["verdict"]["class"], "NOT-FIXED-ALL-VOID")

    def test_a_mixed_world_fixes_only_the_arm_whose_null_fails(self):
        spec = {a: self.STRONG for a in self.s2}
        spec["C-hist-last2"] = self.BLIND
        an = RP.analyse(self.with_nulls(spec), SEEDS, draws=3000)
        self.assertEqual(an["verdict"]["class"], "FIXED")
        self.assertEqual(an["verdict"]["fixed_arms"], ["C-hist-last2"])
        for a in an["verdict"]["void_arms"]:
            self.assertNotEqual(a, "C-hist-last2")

    def test_a_trapped_null_is_not_a_void(self):
        trapped = (0.30, 0.03, 0.80, 0.03)                  # the NULL locked onto the noise room: worse than random
        an = RP.analyse(self.with_nulls({a: trapped for a in self.s2}), SEEDS, draws=3000)
        s2 = an["stage2"]["arms"]["C-hist-last2"]
        self.assertFalse(s2["beat"], s2)
        self.assertFalse(s2["void"], s2)
        self.assertLess(s2["D"], 0)
        self.assertEqual(an["verdict"]["class"], "FIXED")

    def test_a_missing_null_keeps_the_class_pending(self):
        spec = {a: self.BLIND for a in self.s2 if a != "C-hist-last2"}
        an = RP.analyse(self.with_nulls(spec), SEEDS, draws=3000)
        self.assertEqual(an["stage2"]["missing"], ["C-hist-last2"])
        self.assertEqual(an["verdict"]["class"], "FIXED-PENDING-STAGE-2")

    def test_too_few_replicates_count_as_missing(self):
        spec = {a: self.BLIND for a in self.s2}
        an = RP.analyse(self.with_nulls(spec, reps=4), SEEDS, draws=3000)
        self.assertEqual(sorted(an["stage2"]["missing"]), sorted(self.s2))             # the law asks 10 replicates a seed: 4 is not a stage 2
        self.assertEqual(an["verdict"]["class"], "FIXED-PENDING-STAGE-2")

    def test_the_arm_minus_its_null_is_kept_by_seed(self):
        an = RP.analyse(self.with_nulls({a: self.BLIND for a in self.s2}), SEEDS, draws=3000)
        s2 = an["stage2"]["arms"]["C-hist-last2"]
        self.assertEqual(len(s2["gain_over_null_s"]), 10)
        self.assertGreater(float(np.mean(s2["gain_over_null_s"])), 0.05)               # 0.66 against 0.55 planted

    def test_a_flagged_null_passes_beat_only_by_the_sign_count_of_nine(self):
        noisy = (0.62, 0.20, 0.10, 0.20)                    # a locked-in-looking null: replicate SD far above RANDOM's
        an = RP.analyse(self.with_nulls({a: noisy for a in self.s2}), SEEDS, draws=3000)
        s2 = an["stage2"]["arms"]["C-hist-last2"]
        self.assertTrue(s2["flagged"], s2)
        self.assertEqual(s2["beat"], s2["signs"] >= 9)

    def test_the_render_prints_stage_2_and_the_final_class(self):
        spec = {a: self.STRONG for a in self.s2}
        spec["C-hist-last2"] = self.BLIND
        arms = self.with_nulls(spec)
        an = RP.analyse(arms, SEEDS, draws=3000)
        rows = [{"block": b, "room": "N" if b % 4 == 0 else "R1", "own": {"total": 1.0, "bias": 0.7, "weight": 0.1, "stats": 0.05},
                 "hist": {"total": 0.5, "bias": 0.3, "weight": 0.05, "stats": 0.02}} for b in range(1, 201)]
        counts = {a: sum(len(v) for v in arms[a].values()) for a in arms}
        text = "\n".join(RP.render(an, arms, rows, counts, SEEDS))
        self.assertIn("STAGE 2", text)
        self.assertIn("VOID", text)
        self.assertIn("C-hist-last2", text)
        self.assertIn("VERDICT CLASS: FIXED", text)
        self.assertNotIn("VERDICT CLASS: FIXED-PENDING-STAGE-2", text)


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 12:30 +0400 — two READINGS added after the unit and before the RESULT (no bar, no class depends on them; the law's main
# effects alone would misstate the scope effect, which has the OPPOSITE sign for L and for C, and say nothing about WHY the quantity matters). Written FIRST.
#  · simple_effects: the effect of one factor within each level of another (the interaction), per seed, with a bootstrap interval over seeds.
#  · signal_stats / ranking_probe: on RANDOM's own visit streams (an unbiased sample of every room), the per-visit own-window drop of L and of C in N against R1-R3
#    (mean, sd, cv), and the OPEN-LOOP ranking probe — how often «argmax of the last-2 / EMA estimate» would name N — with a dealt null (room labels permuted) and planted signals.
class TestReadings(unittest.TestCase):
    def cells(self, f, seed=5):
        rng = np.random.default_rng(seed)
        return {RP.cell_name(l, s, t): {sd: f(l, s, t) + float(rng.normal(0, 0.01)) for sd in SEEDS}
                for l in ("L", "C") for s in ("own", "hist") for t in ("last2", "ema")}

    def test_simple_effects_find_a_planted_interaction(self):
        cells = self.cells(lambda l, s, t: 0.5 + (0.2 if l == "C" else 0.0) + (0.0 if s == "own" else (-0.30 if l == "L" else 0.05)))
        se = RP.simple_effects(cells, SEEDS, "scope", "loss")
        self.assertAlmostEqual(se["L"]["mean"], -0.30, delta=0.02)
        self.assertAlmostEqual(se["C"]["mean"], 0.05, delta=0.02)
        self.assertAlmostEqual(se["diff"]["mean"], 0.35, delta=0.03)
        self.assertEqual(se["L"]["neg"], 10)
        self.assertEqual(se["C"]["pos"], 10)
        self.assertGreater(se["diff"]["ci95"][0], 0.0)                       # the interaction's interval excludes zero
        self.assertEqual(len(se["diff"]["per_seed"]), 10)

    def test_no_interaction_gives_a_difference_that_includes_zero(self):
        cells = self.cells(lambda l, s, t: 0.5 + (0.2 if l == "C" else 0.0) + (0.0 if s == "own" else -0.10))
        se = RP.simple_effects(cells, SEEDS, "scope", "loss")
        self.assertAlmostEqual(se["L"]["mean"], se["C"]["mean"], delta=0.02)
        lo, hi = se["diff"]["ci95"]
        self.assertLess(lo, 0.0)
        self.assertGreater(hi, 0.0)

    def test_simple_effects_of_the_loss_within_each_scope(self):
        cells = self.cells(lambda l, s, t: 0.5 + (0.2 if (l == "C" and s == "hist") else 0.0))
        se = RP.simple_effects(cells, SEEDS, "loss", "scope")
        self.assertAlmostEqual(se["own"]["mean"], 0.0, delta=0.02)
        self.assertAlmostEqual(se["hist"]["mean"], 0.2, delta=0.02)
        self.assertAlmostEqual(se["diff"]["mean"], 0.2, delta=0.03)

    def visits(self, dN, dR, n=60, seed=3, key="dL"):
        """RANDOM-like lives: the room of each block uniform over the four; the own-window drop of each visit drawn from (mean, sd) by class N / R."""
        rng = np.random.default_rng(seed)
        out = []
        for _ in range(n):
            rooms = [("R1", "R2", "R3", "N")[int(rng.integers(4))] for _ in range(200)]
            d = [float(rng.normal(*(dN if r == "N" else dR))) for r in rooms]
            out.append({"vis": {"room": rooms, "dL": d, "dC": list(d)}})
        return out

    def test_signal_stats_read_the_mean_sd_and_cv_by_class(self):
        lives = self.visits((0.5, 0.5), (0.9, 1.9))
        st = RP.signal_stats(lives, min_block=5)
        n_, r_ = st["L"]["N"], st["L"]["R"]
        self.assertAlmostEqual(n_["mean"], 0.5, delta=0.05)
        self.assertAlmostEqual(n_["sd"], 0.5, delta=0.05)
        self.assertAlmostEqual(r_["mean"], 0.9, delta=0.1)
        self.assertAlmostEqual(r_["sd"], 1.9, delta=0.1)
        self.assertAlmostEqual(r_["cv"], 1.9 / 0.9, delta=0.3)
        self.assertGreater(n_["n"], 1000)
        self.assertGreater(r_["n"], 3 * 1000 * 0.9)                              # three R rooms to one N

    def test_the_ranking_probe_reads_a_planted_perfect_signal_as_never_N(self):
        lives = self.visits((-1.0, 0.05), (1.0, 0.05))
        for kind in ("last2", "ema"):
            p = RP.ranking_probe(lives, key="dL", kind=kind)
            self.assertLess(p["p_N"], 0.02, (kind, p))
            self.assertAlmostEqual(p["p_dealt"], 0.25, delta=0.06)               # the dealt null is blind to rooms: about 1 of 4
            self.assertGreater(p["n"], 5000)

    def test_the_ranking_probe_reads_a_planted_trap_as_always_N(self):
        lives = self.visits((5.0, 0.05), (1.0, 0.05))
        p = RP.ranking_probe(lives, key="dL", kind="last2")
        self.assertGreater(p["p_N"], 0.98, p)

    def test_the_ranking_probe_of_a_signal_with_no_room_structure_is_about_a_quarter(self):
        lives = self.visits((0.7, 0.5), (0.7, 0.5))
        for kind in ("last2", "ema"):
            p = RP.ranking_probe(lives, key="dL", kind=kind)
            self.assertAlmostEqual(p["p_N"], 0.25, delta=0.06, msg=(kind, p))

    def test_a_noisy_signal_ranks_N_first_more_often_than_the_same_means_with_little_noise(self):
        clean = RP.ranking_probe(self.visits((0.5, 0.15), (0.9, 0.15)), key="dL", kind="last2")["p_N"]
        noisy = RP.ranking_probe(self.visits((0.5, 0.5), (0.9, 1.9)), key="dL", kind="last2")["p_N"]
        # the analytic values (the first draft of this test guessed «a gap of 0.10», which the code refused — the code was right, the guess was not): with the last-2 mean of
        # a visit's drop, N's estimate ~ N(0.5, 0.5/√2) and each R room's ~ N(0.9, 1.9/√2), P(N has the maximum of the four) = E_x[Φ((x − 0.9)/1.344)³] = 0.0691; clean (sd 0.15): 8e-5
        self.assertLess(clean, 0.01)
        self.assertAlmostEqual(noisy, 0.0691, delta=0.025)
        self.assertGreater(noisy - clean, 0.04)                                  # the signal-to-noise mechanism, on a planted world

    def test_a_probe_skips_the_blocks_where_a_room_has_no_estimate_yet(self):
        lives = [{"vis": {"room": ["R1"] * 200, "dL": [1.0] * 200, "dC": [1.0] * 200}}]          # R2, R3 and N are never visited
        p = RP.ranking_probe(lives, key="dL", kind="last2")
        self.assertEqual(p["n"], 0)
        self.assertEqual(p["skipped"], 200 - 39)                                 # blocks 40..200 are all skipped

    def test_the_render_prints_the_two_readings(self):
        arms = world(PLANTED)
        for s in SEEDS:                                                           # RANDOM's lives carry the visit streams
            arms["RANDOM"][s] = [dict(l, **self.visits((0.5, 0.5), (0.9, 1.9), n=1, seed=s)[0]) for l in arms["RANDOM"][s]]
        an = RP.analyse(arms, SEEDS, draws=2000)
        rows = [{"block": b, "room": "N" if b % 4 == 0 else "R1", "own": {"total": 1.0, "bias": 0.7, "weight": 0.1, "stats": 0.05},
                 "hist": {"total": 0.5, "bias": 0.3, "weight": 0.05, "stats": 0.02}} for b in range(1, 201)]
        counts = {a: sum(len(v) for v in arms[a].values()) for a in arms}
        text = "\n".join(RP.render(an, arms, rows, counts, SEEDS))
        self.assertIn("THE SIMPLE EFFECTS", text)
        self.assertIn("THE PER-VISIT SIGNAL", text)
        self.assertIn("OPEN-LOOP RANKING PROBE", text)


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 15:20 +0400 — two more READINGS, added while writing the RESULT (no bar or class depends on them): the law's prediction P4
# («no arm reaches R-ONLY's A at any seed») failed at ONE seed (20261305: L-hist-ema, all ten replicates, SHARE_N 0.000, A 0.702 against R-ONLY's 0.700) and the report printed no
# per-seed number that could say why; a figure the RESULT cites must come from the report. (1) the per-seed A and SHARE_N of every arm; (2) the FIRST POLICY PICK: the
# estimates at block 5 (the first policy pick; blocks 1-4 are the round-robin, identical for every replicate of a cell) and whether N is the greedy choice — a greedy rule with
# one reading per room falls the way its first reading points. Written FIRST.
class TestFirstPick(unittest.TestCase):
    def mk(self, n_top, est=None, a=0.5, sn=0.2):
        """a life summary carrying the first policy pick's estimates: N the top estimate if n_top, else R2 (the same shape `summarise_life` writes)."""
        e = est or ({"R1": 0.1, "R2": 0.2, "R3": 0.0, "N": 0.9} if n_top else {"R1": 0.1, "R2": 0.9, "R3": 0.0, "N": -1.0})
        out = life(a, sn)
        out["est_first"] = e
        out["first_policy"] = "N" if n_top else "R2"
        return out

    def arms(self):
        arms = world(PLANTED)
        for cell in ("L-hist-ema", "L-hist-last2", "C-hist-ema"):
            arms[cell] = {s: [self.mk(n_top=(s != 20261305 or cell == "C-hist-ema"), a=(0.70 if (s == 20261305 and cell != "C-hist-ema") else 0.15), sn=(0.0 if (s == 20261305 and cell != "C-hist-ema") else 0.70)) for _ in range(10)] for s in SEEDS}
        return arms

    def test_per_seed_returns_one_value_per_seed_in_seed_order(self):
        arms = self.arms()
        t = RP.per_seed(arms, SEEDS, "A")
        self.assertEqual(len(t["L-hist-ema"]), 10)
        self.assertAlmostEqual(t["L-hist-ema"][SEEDS.index(20261305)], 0.70, places=9)        # the planted anomaly sits at the fifth seed
        self.assertAlmostEqual(t["L-hist-ema"][0], 0.15, places=9)
        sn = RP.per_seed(arms, SEEDS, "SN")
        self.assertAlmostEqual(sn["L-hist-ema"][SEEDS.index(20261305)], 0.0, places=9)
        self.assertAlmostEqual(sn["L-hist-ema"][1], 0.70, places=9)

    def test_first_top_counts_read_the_greedy_choice_at_block_5(self):
        arms = self.arms()
        c = RP.first_top_counts(arms, SEEDS, ("L-hist-ema", "C-hist-ema"))
        self.assertEqual(c["L-hist-ema"][20261305], (0, 10))                                  # N is never the top estimate at the anomalous seed
        self.assertEqual(c["L-hist-ema"][20261301], (10, 10))
        self.assertEqual(c["C-hist-ema"][20261305], (10, 10))                                 # the control cell is not anomalous there
        self.assertEqual(sum(v[0] for v in c["L-hist-ema"].values()), 90)

    def test_first_top_counts_ignore_a_life_with_no_estimates(self):
        arms = self.arms()
        arms["L-hist-ema"][20261301][0]["est_first"] = {"R1": None, "R2": None, "R3": None, "N": None}   # an arm with no estimate yet (RANDOM-like)
        c = RP.first_top_counts(arms, SEEDS, ("L-hist-ema",))
        self.assertEqual(c["L-hist-ema"][20261301], (9, 9))                                   # nine lives had estimates, all nine put N on top

    def test_a_tie_for_the_top_estimate_counts_for_n_only_when_n_wins_the_tie_break(self):
        arms = world(PLANTED)
        arms["L-hist-ema"] = {s: [self.mk(False, est={"R1": 0.5, "R2": 0.5, "R3": 0.0, "N": 0.5})] * 10 for s in SEEDS}
        c = RP.first_top_counts(arms, SEEDS, ("L-hist-ema",))
        self.assertEqual(c["L-hist-ema"][20261301], (0, 10))                                  # a tie is not N «on top»: the law's tie-break is the least recently visited, and N was visited LAST of the round-robin

    def test_summarise_life_carries_the_first_policy_pick_on_a_real_short_life(self):
        from brain.scene import run_s1c as S
        from tools.toys.common import pools as POOLS
        from tools.toys.cp import life as LF
        if not all(POOLS.present(POOLS.ROOT, 20261301).values()):
            self.skipTest("pools absent")
        rooms = list(S.WORLDS["law"])
        data = S.RoomData(POOLS.ROOT, 20261301, rooms)
        rec = LF.life_cp(data, S.FixedTestSet(), ES.make_arm("C-hist-ema", rooms, 20261301, 0), "C-hist-ema", rooms, n_blocks=12)
        s = RP.summarise_life(rec)
        self.assertIn(s["first_policy"], ("R1", "R2", "R3", "N"))
        self.assertEqual(set(s["est_first"]), {"R1", "R2", "R3", "N"})
        self.assertTrue(all(v is not None for v in s["est_first"].values()))                  # after the round-robin every room has a reward
        row5 = next(x for x in rec["record"] if x["block"] == 5)
        self.assertEqual(s["est_first"], row5["est"])                                         # exactly the record's block-5 estimates
        self.assertEqual(s["first_policy"], row5["room"])

    def test_the_render_prints_the_per_seed_tables_and_the_first_pick_table(self):
        arms = self.arms()
        an = RP.analyse(arms, SEEDS, draws=2000)
        rows = [{"block": b, "room": "N" if b % 4 == 0 else "R1", "own": {"total": 1.0, "bias": 0.7, "weight": 0.1, "stats": 0.05},
                 "hist": {"total": 0.5, "bias": 0.3, "weight": 0.05, "stats": 0.02}} for b in range(1, 201)]
        counts = {a: sum(len(v) for v in arms[a].values()) for a in arms}
        text = "\n".join(RP.render(an, arms, rows, counts, SEEDS))
        self.assertIn("PER-SEED A", text)
        self.assertIn("PER-SEED SHARE_N", text)
        self.assertIn("THE FIRST POLICY PICK", text)
        import re
        lines = [l for l in text.splitlines() if l.strip().startswith("L-hist-ema") and re.search(r"(^|\s)0/10(\s|$)", l)]
        self.assertEqual(len(lines), 1, lines)                                                # the anomalous seed's cell «0/10» (not «10/10») is visible in ONE printed row


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 15:30 +0400 — a third reading, found while writing the RESULT: it said the stage-2 NULLs «lock into one room», and the report
# printed the NULLs' longest run with no reference (RANDOM's is 4.5 blocks, the NULLs' 38-40). The LOCK-IN reading prints it for every arm, so the claim has its comparison. Written FIRST.
class TestLockIn(unittest.TestCase):
    def test_lock_in_stats_are_the_mean_median_and_max_of_the_longest_run(self):
        arms = {"X": {s: [dict(life(0.5, 0.2), lock=v) for v in (3, 5, 10)] for s in SEEDS}}
        st = RP.lock_in(arms, SEEDS)
        self.assertAlmostEqual(st["X"]["mean"], 6.0, places=9)
        self.assertEqual(st["X"]["median"], 5.0)
        self.assertEqual(st["X"]["max"], 10)
        self.assertEqual(st["X"]["n"], 30)

    def test_a_life_with_no_longest_run_is_not_counted(self):
        arms = {"X": {SEEDS[0]: [dict(life(0.5, 0.2), lock=None), dict(life(0.5, 0.2), lock=8)]}}
        st = RP.lock_in(arms, SEEDS)
        self.assertEqual(st["X"]["n"], 1)
        self.assertEqual(st["X"]["max"], 8)

    def test_an_arm_with_no_lives_with_a_run_is_absent(self):
        arms = {"X": {SEEDS[0]: [dict(life(0.5, 0.2), lock=None)]}}
        self.assertNotIn("X", RP.lock_in(arms, SEEDS))

    def test_the_render_prints_the_lock_in_reading_with_random_as_the_reference(self):
        arms = world(PLANTED)
        for s in SEEDS:
            arms["RANDOM"][s] = [dict(l, lock=4) for l in arms["RANDOM"][s]]
            arms["C-hist-ema"][s] = [dict(l, lock=30) for l in arms["C-hist-ema"][s]]
        an = RP.analyse(arms, SEEDS, draws=2000)
        rows = [{"block": b, "room": "N" if b % 4 == 0 else "R1", "own": {"total": 1.0, "bias": 0.7, "weight": 0.1, "stats": 0.05},
                 "hist": {"total": 0.5, "bias": 0.3, "weight": 0.05, "stats": 0.02}} for b in range(1, 201)]
        counts = {a: sum(len(v) for v in arms[a].values()) for a in arms}
        text = "\n".join(RP.render(an, arms, rows, counts, SEEDS))
        self.assertIn("LOCK-IN", text)
        section = text.split("LOCK-IN", 1)[1].split("PREDICTIONS", 1)[0]                           # only the lock-in section: «RANDOM» and the cells also appear in other tables
        self.assertIn("max", section.splitlines()[0])                                             # the header names what is printed
        rnd = [l for l in section.splitlines() if l.strip().startswith("RANDOM")]
        cell = [l for l in section.splitlines() if l.strip().startswith("C-hist-ema")]
        self.assertEqual(len(rnd), 1)
        self.assertEqual(len(cell), 1)
        self.assertIn("mean    4.0", rnd[0])
        self.assertIn("max    4", rnd[0])
        self.assertIn("mean   30.0", cell[0])
        self.assertIn("max   30", cell[0])


if __name__ == "__main__":
    unittest.main()
