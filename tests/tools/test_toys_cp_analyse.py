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


if __name__ == "__main__":
    unittest.main()
