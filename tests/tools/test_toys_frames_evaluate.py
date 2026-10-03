"""Tests for TOY C's condition evaluator: every rule on one train/held-out split, its gain, anatomy, adjacency readings and both nulls, as ONE JSON-able record
(docs/research/toys/PREREG-TOY-FRAMES.md §2-§4). Written FIRST, STAGE 3e (red, then green).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:46 +0400 — STAGE 3e. The fixture is a small synthetic stream from the SCENE generator's constants with a PLANT after every 10th moment
# (the law's SCENE+PLANT), 3 WEB-S seeds and 20 draws so the module runs in seconds; the real run uses 10 seeds and 100 draws.
"""
from __future__ import annotations

import json
import math
import unittest

import numpy as np

from tools.toys.frames import anatomy as AN
from tools.toys.frames import compress as CO
from tools.toys.frames import evaluate as EV
from tools.toys.frames import null as NL
from tools.toys.frames import rules as RL
from tools.toys.frames import scene as SC
from tools.toys.frames import streams as ST

RULES = ["WEB-H", "WEB-S", "WEB-S", "WEB-S", "SENTENCE", "MDL-GREEDY"]


def fixture():
    ms = SC.sample_moments(1500, np.random.default_rng([20261103, 8, 9]))
    tr, he = ST.split(ST.with_plant(ms, 10))
    return tr, he


class TestEvaluateCondition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tr, cls.he = fixture()
        cls.cond = EV.evaluate_condition(cls.tr, cls.he, name="synthetic", draws=20, web_seeds=(1, 2, 3))
        cls.sc = CO.Scorer([m.words for m in cls.tr], [m.words for m in cls.he])

    def test_one_record_per_rule_and_seed_in_a_fixed_order(self):
        self.assertEqual([r["rule"] for r in self.cond["records"]], RULES)
        self.assertEqual([r["seed"] for r in self.cond["records"]], [0, 1, 2, 3, 0, 0])
        self.assertEqual(self.cond["name"], "synthetic")
        self.assertEqual((self.cond["n_train_moments"], self.cond["n_held_moments"]), (len(self.tr), len(self.he)))
        self.assertEqual(self.cond["V"], self.sc.V)
        self.assertEqual(self.cond["n_held_words"], self.sc.n_held_words)

    def test_each_records_gain_is_the_compressors_gain_of_its_own_frames(self):
        for r in self.cond["records"]:
            F = {tuple(f) for f in r["frames"]}
            self.assertEqual(r["n_frames"], len(F))
            g = self.sc.gain(F)
            self.assertAlmostEqual(r["gain"]["G"], g.G, places=9)
            self.assertAlmostEqual(r["gain"]["L"], g.L, places=9)
            self.assertEqual(r["frames"], sorted(r["frames"]))

    def test_the_anatomy_identity_holds_in_every_record(self):
        for r in self.cond["records"]:
            a = r["anatomy"]
            self.assertAlmostEqual(a["M"] + a["D"] + a["C"] - a["L"], r["gain"]["G"], places=8, msg=r["rule"])
            self.assertAlmostEqual(a["T"], a["D"] + a["C"], places=12)

    def test_the_nulls_have_the_draws_the_rule_tag_key_and_the_dealt_statistic(self):
        for r in self.cond["records"]:
            F = {tuple(f) for f in r["frames"]}
            tag = RL.RULE_TAG[r["rule"]]
            seed = r["seed"] if r["rule"] == "WEB-S" else 0
            for key, fn in (("null1", NL.null1), ("null2", NL.null2)):
                got = r[key]
                if "error" in got:
                    continue
                want = fn(self.sc, F, tag, seed, draws=20)
                self.assertEqual(tuple(got["values"]), want.values, (r["rule"], key))
                self.assertEqual((got["draws"], got["k"], got["fallbacks"]), (20, want.k, want.fallbacks))
                self.assertAlmostEqual(got["q95"], want.q95, places=12)
                self.assertEqual(got["beats_q95"], bool(r["gain"]["G"] > want.q95))

    def test_adjacency_readings_count_what_the_law_says_to_print(self):
        for r in self.cond["records"]:
            F = [tuple(f) for f in r["frames"]]
            adj = r["adjacency"]
            if not F:
                self.assertIsNone(adj["train_adjacent_share"])
                continue
            share = sum(1 for f in F if self.sc.train_adjacent(f) > 0) / len(F)
            self.assertAlmostEqual(adj["train_adjacent_share"], share, places=12)
            self.assertEqual(adj["held_adjacent_zero"], sum(1 for f in F if self.sc.held_adjacent(f) == 0))
            if r["rule"].startswith("WEB"):
                self.assertEqual(adj["train_adjacent_share"], 1.0)                                    # the web's edges are oriented by adjacency, never-adjacent ones dropped

    def test_the_record_is_json_serialisable_and_the_evaluation_is_deterministic(self):
        again = EV.evaluate_condition(self.tr, self.he, name="synthetic", draws=20, web_seeds=(1, 2, 3))
        self.assertEqual(json.dumps(self.cond, sort_keys=True), json.dumps(again, sort_keys=True))
        back = json.loads(json.dumps(self.cond))
        self.assertEqual(len(back["records"]), len(RULES))

    def test_the_planted_frame_is_found_by_the_rules_on_a_plant_stream(self):
        kept = {(r["rule"], r["seed"]): [tuple(f) for f in r["frames"]].count(ST.PLANT) for r in self.cond["records"]}
        self.assertEqual(kept[("WEB-H", 0)], 1)
        self.assertEqual(kept[("SENTENCE", 0)], 1)
        self.assertEqual(kept[("MDL-GREEDY", 0)], 1)

    def test_without_nulls_the_records_carry_none(self):
        c = EV.evaluate_condition(self.tr, self.he, name="x", draws=5, web_seeds=(1,), with_nulls=False)
        for r in c["records"]:
            self.assertNotIn("null1", r)
            self.assertNotIn("null2", r)
        self.assertEqual([r["rule"] for r in c["records"]], ["WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY"])


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:48 +0400 — added after a MUTATION sweep of evaluate.py: two mutants of the adjacency readings survived because every frame the scene fixture yields is the
# (adjacent) plant. This fixture holds a frame SENTENCE files (find_frames counts every ordered pair of a moment) that is NEVER adjacent.
class TestANeverAdjacentFrame(unittest.TestCase):
    def test_a_frame_standing_two_words_apart_is_read_as_never_adjacent(self):
        """train: 24 x [p, xk, q] (k cycling 8 values) + 60 two-word noise moments (each noise pair 3 times). find_frames' N = 84 moments with >= 2 distinct words; (p, q): count 24 against 24 * 24 / 84 = 6.86
        expected: 24 >= 5 and 24 > 13.7 -> a frame, although p and q are never adjacent; every (p, xk) and (xk, q) has count 3 < 5."""
        def mk(prefix, rows):
            return [ST.Moment("s", f"{prefix}{i}", tuple(w), tuple(float(i * 10 + j) for j in range(len(w)))) for i, w in enumerate(rows)]
        train_rows = [["p", f"x{i % 8}", "q"] for i in range(24)] + [[f"n{i % 20:02d}", f"m{(i * 7) % 20:02d}"] for i in range(60)]
        held_rows = [["p", f"x{i % 8}", "q"] for i in range(12)] + [["n00", "m00"]] * 6
        cond = EV.evaluate_condition(mk("t", train_rows), mk("h", held_rows), name="never-adjacent", draws=10, web_seeds=(1,))
        sent = [r for r in cond["records"] if r["rule"] == "SENTENCE"][0]
        self.assertEqual(sent["frames"], [["p", "q"]])
        self.assertEqual(sent["adjacency"]["train_adjacent_share"], 0.0)
        self.assertEqual(sent["adjacency"]["held_adjacent_zero"], 1)
        self.assertEqual(sent["adjacency"]["held_firings"], 0)
        self.assertEqual(sent["adjacency"]["held_adjacent_total"], 0)
        self.assertLess(sent["gain"]["G"], 0.0)                                                        # a frame that never fires costs its model bits and saves none


class TestQuietTable(unittest.TestCase):
    def test_the_table_names_each_rule_loud_or_quiet_by_the_gain_against_null1(self):
        tr, he = fixture()
        cond = EV.evaluate_condition(tr, he, name="synthetic", draws=20, web_seeds=(1, 2))
        rows = EV.quiet_rows(cond)
        self.assertEqual(len(rows), len(cond["records"]))
        for row, r in zip(rows, cond["records"]):
            if r["n_frames"] == 0:
                self.assertEqual(row["verdict"], "EMPTY")
            elif "error" in r["null1"]:
                self.assertEqual(row["verdict"], "NO-NULL")
            else:
                self.assertEqual(row["verdict"], "LOUD" if r["gain"]["G"] > r["null1"]["q95"] else "QUIET")
            for k in ("rule", "seed", "n_frames", "G", "null1_mean", "null1_sd", "null1_q95", "M", "D", "C", "T", "L"):
                self.assertIn(k, row)
        text = EV.quiet_text(cond)
        self.assertIn("synthetic", text)
        self.assertTrue(all(v in text for v in {row["verdict"] for row in rows}))


if __name__ == "__main__":
    unittest.main()
