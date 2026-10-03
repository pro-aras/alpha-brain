"""Tests for TOY C's verdicts: the law's bars and gates (docs/research/toys/PREREG-TOY-FRAMES.md §4; AMENDMENT-1 §1, §4 (e)) as pure functions over condition records. Written FIRST, STAGE 4c (red, then green).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:02 +0400 — STAGE 4c. The records here are HAND-MADE (only the fields a verdict reads), so each verdict is checked by eye: GAIN = G > q95 of NULL-1 AND G > 0 (WEB-S: >= 8 of 10 seeds,
# exact sign p = 56/1024 = 0.0547); SHUFFLE-QUIET = F empty or G <= q95 (WEB-S: >= 8 of 10 quiet); the PLANT gate in both modes; GATE FIRST per stream (a rule that fails its PLANT or SHUFFLE gate on ALPHA4 reads NOT GRADABLE there,
# a failure on SCENE+PLANT gates SCENE's readings only); CRITERION-MATTERS = G > q95 of NULL-2 AND G > 0, NOT GRADABLE when PLANT-BEATS-NULL-2 fails; the eye's reading; overlaps; the oracle's recall.
"""
from __future__ import annotations

import unittest

from tools.toys.frames import streams as ST
from tools.toys.frames import verdicts as VD

P = list(ST.PLANT)


def rec(rule, seed, n_frames, G, q1=None, q2=None, plant=None, frames=None, err1=False):
    r = {"rule": rule, "seed": seed, "n_frames": n_frames, "gain": {"G": G}, "frames": frames if frames is not None else [[f"a{i}", f"b{i}"] for i in range(n_frames)]}
    r["null1"] = {"error": "x"} if err1 else {"q95": q1, "mean": 0.0, "sd": 1.0}
    r["null2"] = {"q95": q2 if q2 is not None else q1, "mean": 0.0, "sd": 1.0}
    if plant is not None:
        r["plant"] = plant
    return r


def cond(name, records, kind="plain", B=None, beats2=True):
    c = {"name": name, "kind": kind, "records": records}
    if kind == "plant":
        c["plant_stream"] = {"B": B, "plant_beats_null2": beats2}
    return c


def webs(rule_recs):
    return [r for r in rule_recs]


class TestGain(unittest.TestCase):
    def test_a_deterministic_rule_needs_g_above_q95_and_above_zero(self):
        cases = [(5.0, 3.0, True), (5.0, 7.0, False), (-1.0, -5.0, False), (0.0, -2.0, False), (2.0, 2.0, False)]           # G > q95 strictly; G > 0
        for G, q, want in cases:
            v = VD.gain_verdicts(cond("A", [rec("MDL-GREEDY", 0, 3, G, q1=q)]))["MDL-GREEDY"]
            self.assertEqual(v["passes"], want, (G, q))
            self.assertEqual((v["n"], v["n_pass"]), (1, int(want)))

    def test_an_empty_set_does_not_pass_and_a_missing_null_does_not_pass(self):
        self.assertFalse(VD.gain_verdicts(cond("A", [rec("SENTENCE", 0, 0, 0.0, q1=-1.0)]))["SENTENCE"]["passes"])
        v = VD.gain_verdicts(cond("A", [rec("SENTENCE", 0, 2, 9.0, err1=True)]))["SENTENCE"]
        self.assertFalse(v["passes"])
        self.assertEqual(v["no_null"], 1)

    def test_web_s_passes_at_eight_of_ten_seeds_and_prints_the_exact_sign_p(self):
        def seeds(k):
            return [rec("WEB-S", s, 4, 5.0 if s <= k else -3.0, q1=0.0) for s in range(1, 11)]
        v8 = VD.gain_verdicts(cond("A", seeds(8)))["WEB-S"]
        v7 = VD.gain_verdicts(cond("A", seeds(7)))["WEB-S"]
        self.assertTrue(v8["passes"])
        self.assertEqual((v8["n"], v8["n_pass"], v8["need"]), (10, 8, 8))
        self.assertAlmostEqual(v8["exact_sign_p"], 56 / 1024, places=12)                       # P(X >= 8 | Bin(10, 1/2)) = (45 + 10 + 1) / 1024
        self.assertFalse(v7["passes"])
        self.assertAlmostEqual(v7["exact_sign_p"], 176 / 1024, places=12)                      # (120 + 45 + 10 + 1) / 1024


class TestShuffleQuiet(unittest.TestCase):
    def test_empty_or_at_most_q95_is_quiet_above_is_loud(self):
        for n, G, q, want in [(0, 0.0, -9.0, True), (3, -4.0, -3.0, True), (3, -3.0, -3.0, True), (3, -2.9, -3.0, False)]:
            v = VD.shuffle_quiet(cond("S", [rec("WEB-H", 0, n, G, q1=q)], kind="shuffle"))["WEB-H"]
            self.assertEqual(v["quiet"], want, (n, G, q))

    def test_web_s_is_quiet_when_at_least_eight_of_ten_seeds_are(self):
        def seeds(k):
            return [rec("WEB-S", s, 4, -5.0 if s <= k else 5.0, q1=0.0) for s in range(1, 11)]
        self.assertTrue(VD.shuffle_quiet(cond("S", seeds(8), kind="shuffle"))["WEB-S"]["quiet"])
        v = VD.shuffle_quiet(cond("S", seeds(7), kind="shuffle"))["WEB-S"]
        self.assertFalse(v["quiet"])
        self.assertEqual((v["n"], v["n_quiet"], v["need"]), (10, 7, 8))


class TestPlantGatesPerStream(unittest.TestCase):
    def plant_cond(self, B, rows):
        recs = [rec(rule, seed, 3, 0.0, q1=0.0, plant=pl) for (rule, seed, pl) in rows]
        return cond("P", recs, kind="plant", B=B)

    def test_amend1_reads_keeps_B_and_C_and_ignores_the_whole_set(self):
        rows = [("WEB-H", 0, {"kept": True, "A": -50.0, "C": 4.0}), ("SENTENCE", 0, {"kept": True, "A": -9.0, "C": -1.0}), ("MDL-GREEDY", 0, {"kept": False, "A": 3.0, "C": None})]
        g = VD.plant_gates(self.plant_cond(7.0, rows), "amend1")
        self.assertTrue(g["WEB-H"]["pass"])
        self.assertFalse(g["SENTENCE"]["pass"])
        self.assertFalse(g["MDL-GREEDY"]["pass"])
        self.assertFalse(VD.plant_gates(self.plant_cond(-1.0, rows), "amend1")["WEB-H"]["pass"])        # B <= 0 fails every rule

    def test_law_mode_reads_the_whole_set(self):
        rows = [("WEB-H", 0, {"kept": True, "A": -50.0, "C": 4.0}), ("SENTENCE", 0, {"kept": True, "A": 2.0, "C": -1.0})]
        g = VD.plant_gates(self.plant_cond(7.0, rows), "law")
        self.assertFalse(g["WEB-H"]["pass"])
        self.assertTrue(g["SENTENCE"]["pass"])


def all_conditions(web_h_gain=True, web_h_kept=True, sent_loud=False, scene_plant_ok=True, beats2=True):
    """ALPHA4 + its three satellites and SCENE + its PLANT, four rules, ten WEB-S seeds."""
    def rules(G_by_rule, q1, q2=None, plant=None, shuffle=None):
        out = []
        for rule, seeds in (("WEB-H", [0]), ("WEB-S", list(range(1, 11))), ("SENTENCE", [0]), ("MDL-GREEDY", [0])):
            for s in seeds:
                g = G_by_rule[rule]
                pl = (plant[rule] if plant else None)
                out.append(rec(rule, s, 3, g, q1=q1, q2=q2, plant=pl))
        return out
    plant_ok = {"kept": True, "A": -10.0, "C": 3.0}
    a4 = cond("ALPHA4", rules({"WEB-H": 5.0 if web_h_gain else -5.0, "WEB-S": 5.0, "SENTENCE": -5.0, "MDL-GREEDY": -2.0}, q1=0.0, q2=-1.0))
    a4p = cond("ALPHA4+PLANT", rules({"WEB-H": 0.0, "WEB-S": 0.0, "SENTENCE": 0.0, "MDL-GREEDY": 0.0}, q1=0.0, plant={
        "WEB-H": ({"kept": True, "A": -10.0, "C": 3.0} if web_h_kept else {"kept": False, "A": -10.0, "C": None}), "WEB-S": plant_ok, "SENTENCE": plant_ok, "MDL-GREEDY": plant_ok}),
        kind="plant", B=100.0, beats2=beats2)
    a4s = cond("ALPHA4+SHUFFLE", rules({"WEB-H": -5.0, "WEB-S": -5.0, "SENTENCE": (5.0 if sent_loud else -5.0), "MDL-GREEDY": -5.0}, q1=0.0), kind="shuffle")
    sc = cond("SCENE", rules({"WEB-H": 1.0, "WEB-S": 1.0, "SENTENCE": 1.0, "MDL-GREEDY": 1.0}, q1=0.0))
    scp = cond("SCENE+PLANT", rules({"WEB-H": 0.0, "WEB-S": 0.0, "SENTENCE": 0.0, "MDL-GREEDY": 0.0}, q1=0.0, plant={
        "WEB-H": plant_ok, "WEB-S": plant_ok, "SENTENCE": (plant_ok if scene_plant_ok else {"kept": False, "A": 0.0, "C": None}), "MDL-GREEDY": plant_ok}),
        kind="plant", B=50.0)
    return {"ALPHA4": a4, "ALPHA4+PLANT": a4p, "ALPHA4+SHUFFLE": a4s, "SCENE": sc, "SCENE+PLANT": scp}


class TestGrade(unittest.TestCase):
    def test_gain_is_graded_pass_or_fail_when_both_gates_hold(self):
        g = VD.grade(all_conditions(), "amend1")
        a = g["alpha4"]
        self.assertEqual(a["WEB-H"]["gain_verdict"], "PASS")                                           # G 5 > q95 0 and > 0
        self.assertEqual(a["WEB-S"]["gain_verdict"], "PASS")
        self.assertEqual(a["SENTENCE"]["gain_verdict"], "FAIL")                                        # a rule whose frames do not pay FAILS GAIN (graded, not silenced)
        self.assertEqual(a["MDL-GREEDY"]["gain_verdict"], "FAIL")
        for rule in a:
            self.assertTrue(a[rule]["gate_first_ok"], rule)

    def test_a_rule_that_fails_its_plant_gate_on_alpha4_is_not_gradable_there(self):
        g = VD.grade(all_conditions(web_h_kept=False), "amend1")
        self.assertEqual(g["alpha4"]["WEB-H"]["gain_verdict"], "NOT GRADABLE")                          # although its GAIN would have passed
        self.assertFalse(g["alpha4"]["WEB-H"]["gate_first_ok"])
        self.assertEqual(g["alpha4"]["WEB-S"]["gain_verdict"], "PASS")                                  # the others are untouched

    def test_a_loud_shuffle_makes_that_rule_not_gradable(self):
        g = VD.grade(all_conditions(sent_loud=True), "amend1")
        self.assertEqual(g["alpha4"]["SENTENCE"]["gain_verdict"], "NOT GRADABLE")
        self.assertFalse(g["alpha4"]["SENTENCE"]["shuffle_quiet"]["quiet"])

    def test_a_scene_plant_failure_gates_scene_only(self):
        g = VD.grade(all_conditions(scene_plant_ok=False), "amend1")
        self.assertFalse(g["scene"]["SENTENCE"]["gradable"])
        self.assertTrue(g["scene"]["WEB-H"]["gradable"])
        self.assertEqual(g["alpha4"]["SENTENCE"]["gain_verdict"], "FAIL")                               # ALPHA4's grade is not moved by SCENE's plant

    def test_the_law_mode_gates_on_the_whole_set(self):
        g = VD.grade(all_conditions(), "law")
        self.assertEqual(g["mode"], "law")
        self.assertEqual(g["alpha4"]["WEB-H"]["gain_verdict"], "NOT GRADABLE")                          # A = −10 on the plant stream: the junk sinks it in the base text's reading
        self.assertEqual(g["alpha4"]["WEB-S"]["gain_verdict"], "NOT GRADABLE")
        self.assertEqual(g["alpha4"]["SENTENCE"]["gain_verdict"], "NOT GRADABLE")

    def test_criterion_matters_is_not_gradable_when_the_plant_does_not_beat_null2(self):
        ok = VD.grade(all_conditions(beats2=True), "amend1")["alpha4"]
        no = VD.grade(all_conditions(beats2=False), "amend1")["alpha4"]
        self.assertEqual(ok["WEB-H"]["criterion"]["verdict"], "YES")                                     # G 5 > q95(NULL-2) −1 and > 0
        self.assertEqual(ok["SENTENCE"]["criterion"]["verdict"], "NO")
        self.assertEqual(no["WEB-H"]["criterion"]["verdict"], "NOT GRADABLE")
        self.assertEqual(VD.grade(all_conditions(beats2=False), "amend1")["plant_beats_null2"]["ALPHA4+PLANT"], False)

    def test_an_unknown_mode_is_refused(self):
        with self.assertRaises(ValueError):
            VD.grade(all_conditions(), "loose")


class TestEyeReading(unittest.TestCase):
    def test_the_kept_and_dropped_says_and_the_frames_never_said(self):
        says = [("red box", "yes", 1), ("red box", "yes", 2), ("red box", "no", 3), ("to the", "no", 4), ("to the", "no", 5), ("the letters", "no", 6), ("blue ball", "yes", 7), ("one two three", "no", 8)]
        # distinct said frames: red box (3 says, 2 yes), to the (2, 0), the letters (1, 0), blue ball (1, 1), one two three (1, 0; not a pair): 5 distinct, 8 says, 3 yes
        c = cond("ALPHA4", [rec("MDL-GREEDY", 0, 3, 1.0, q1=0.0, frames=[["red", "box"], ["to", "the"], ["zz", "yy"]])])
        e = VD.eye_reading(c, says)
        self.assertEqual((e["distinct_said"], e["says"], e["yes"]), (5, 8, 3))
        self.assertAlmostEqual(e["base_rate"], 3 / 8, places=12)
        r = e["records"][0]
        self.assertEqual(r["said_kept"], 2)                                                              # red box, to the
        self.assertEqual((r["says_kept"], r["yes_kept"]), (5, 2))
        self.assertAlmostEqual(r["rate_kept"], 2 / 5, places=12)
        self.assertEqual((r["says_not_kept"], r["yes_not_kept"]), (3, 1))                                # the letters (0 yes), blue ball (1), one two three (0)
        self.assertAlmostEqual(r["rate_not_kept"], 1 / 3, places=12)
        self.assertEqual(r["kept_never_said"], 1)                                                       # (zz, yy)

    # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 21:39 +0400 — the law's §4 asks for «the cells' 40 distinct said frames, EACH with its says and its yes-count»; the reading carried only the
    # aggregates. Written FIRST (red: KeyError 'frames'): the per-frame table, sorted (most says first, ties by the frame's text), the pair as a list or None for a said text that is not two words.
    def test_the_per_frame_table_each_said_frame_with_its_says_and_its_yes_count(self):
        says = [("red box", "yes", 1), ("red box", "yes", 2), ("red box", "no", 3), ("to the", "no", 4), ("to the", "no", 5), ("the letters", "no", 6), ("blue ball", "yes", 7), ("one two three", "no", 8)]
        c = cond("ALPHA4", [rec("MDL-GREEDY", 0, 1, 1.0, q1=0.0, frames=[["red", "box"]])])
        e = VD.eye_reading(c, says)
        self.assertEqual(e["frames"], [{"frame": "red box", "pair": ["red", "box"], "says": 3, "yes": 2},
                                       {"frame": "to the", "pair": ["to", "the"], "says": 2, "yes": 0},
                                       {"frame": "blue ball", "pair": ["blue", "ball"], "says": 1, "yes": 1},
                                       {"frame": "one two three", "pair": None, "says": 1, "yes": 0},
                                       {"frame": "the letters", "pair": ["the", "letters"], "says": 1, "yes": 0}])
        self.assertEqual(len(e["frames"]), e["distinct_said"])                                           # every distinct said frame is in the table
        self.assertEqual(sum(f["says"] for f in e["frames"]), e["says"])                                 # and the table's says and yes-counts add up to the totals
        self.assertEqual(sum(f["yes"] for f in e["frames"]), e["yes"])
        self.assertEqual(VD.eye_reading(c, [])["frames"], [])                                            # no says: an empty table (and a base rate of None, as before)

    def test_an_empty_set_has_no_rate(self):
        c = cond("ALPHA4", [rec("SENTENCE", 0, 0, 0.0, q1=0.0, frames=[])])
        r = VD.eye_reading(c, [("red box", "yes", 1)])["records"][0]
        self.assertEqual((r["said_kept"], r["says_kept"], r["kept_never_said"]), (0, 0, 0))
        self.assertIsNone(r["rate_kept"])
        self.assertAlmostEqual(r["rate_not_kept"], 1.0, places=12)


class TestOverlapsAndRecall(unittest.TestCase):
    def test_jaccard(self):
        self.assertAlmostEqual(VD.jaccard({1, 2, 3}, {2, 3, 4}), 2 / 4, places=12)
        self.assertIsNone(VD.jaccard(set(), set()))
        self.assertEqual(VD.jaccard({1}, set()), 0.0)

    def test_overlaps_between_the_rules_sets(self):
        recs = [rec("WEB-H", 0, 2, 0.0, q1=0.0, frames=[["a", "b"], ["c", "d"]]), rec("WEB-S", 1, 1, 0.0, q1=0.0, frames=[["a", "b"]]), rec("WEB-S", 2, 1, 0.0, q1=0.0, frames=[["x", "y"]]),
                rec("SENTENCE", 0, 2, 0.0, q1=0.0, frames=[["a", "b"], ["e", "f"]]), rec("MDL-GREEDY", 0, 1, 0.0, q1=0.0, frames=[["c", "d"]])]
        o = VD.overlaps(cond("ALPHA4", recs))
        self.assertAlmostEqual(o["WEB-H|SENTENCE"], 1 / 3, places=12)                                    # {ab, cd} vs {ab, ef}
        self.assertAlmostEqual(o["WEB-H|MDL-GREEDY"], 1 / 2, places=12)
        self.assertAlmostEqual(o["SENTENCE|MDL-GREEDY"], 0.0, places=12)
        self.assertAlmostEqual(o["WEB-S|WEB-H"], (1 / 2 + 0.0) / 2, places=12)                           # mean over the seeds: ab vs {ab, cd} = 1/2, xy vs {ab, cd} = 0

    def test_oracle_recall(self):
        oracle = {("red", "circle"), ("blue", "star"), ("green", "ring"), ("red", "star")}
        recs = [rec("MDL-GREEDY", 0, 3, 0.0, q1=0.0, frames=[["red", "circle"], ["blue", "star"], ["zz", "yy"]]), rec("SENTENCE", 0, 0, 0.0, q1=0.0, frames=[])]
        r = VD.oracle_recall(cond("SCENE", recs), oracle)
        self.assertAlmostEqual(r["MDL-GREEDY"], 2 / 4, places=12)
        self.assertEqual(r["SENTENCE"], 0.0)


if __name__ == "__main__":
    unittest.main()
