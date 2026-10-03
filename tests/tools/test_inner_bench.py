# edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:48 +0400 — PREREG-INNER-1 §3 K / K-ablated / K-plant / G2 / G3 + the readings, AMENDMENT 1 A8 (the
# law signed by all three at research-1003 @ 7c49f62, file sha256 b489209c…; the co-signed TEXT 857e07b2…faa82). Test-first for
# tools/brain/inner_bench.py: every grader on SYNTHETIC rows, each with a planted control that must be caught (RULES §11).
"""tests/tools/test_inner_bench.py — the bench's graders, on data whose truth is known.

The world here is three hand-placed things (the scene world's own Thing, boxes ≥ 24 px apart); the «turns» are dicts the grader reads
(said words, the target's cells, the things). A PERFECT mouth must pass K against its dealt-phrase null; a CONSTANT mouth must fail (its
null equals it); the plant must read FALSE; EXIST must catch a moment on no tape; the lock detector must see the greedy cycle and not a
cover; the age deciles, the pairing and the Spearman null must read a planted signal and a planted absence."""
from __future__ import annotations

import unittest

import numpy as np

from brain.scene import world as W
from tools.brain import inner_bench as B

THINGS = (W.Thing("star", "red", "big", 8, 8), W.Thing("ring", "blue", "small", 72, 8), W.Thing("square", "green", "big", 8, 80))
# one fixation cell inside each thing's box (cell centre = cell*8+4): (1,1) → px (12,12) in star; (9,1) → (76,12) in ring; (1,10) → (12,84) in square
CELLS = ([[1, 1]], [[9, 1]], [[1, 10]])


def turn(said, cells, things=THINGS):
    return {"said": said, "cells": cells, "things": things}


class TheRule(unittest.TestCase):
    def test_true_iff_every_said_word_is_an_attribute_of_the_thing_under_the_target(self) -> None:
        self.assertTrue(B.k_true(["star"], CELLS[0], THINGS))
        self.assertTrue(B.k_true(["big", "red", "star"], CELLS[0], THINGS))
        self.assertFalse(B.k_true(["ring"], CELLS[0], THINGS))                 # the wrong thing's word
        self.assertFalse(B.k_true(["small", "star"], CELLS[0], THINGS))        # one word false of it
        self.assertFalse(B.k_true(None, CELLS[0], THINGS))                     # a silent turn
        self.assertFalse(B.k_true(["star"], None, THINGS))
        self.assertFalse(B.k_true(["star"], [[5, 5]], THINGS))                # a target on no thing (cell (5,5) → px (44,44): empty)
        self.assertEqual(B.thing_under(CELLS[1], THINGS), 1)
        self.assertIsNone(B.thing_under([[1, 1], [9, 1]], THINGS))            # a tie between two things


class K(unittest.TestCase):
    def perfect(self, n=60):
        out = []
        for i in range(n):
            t = i % 3
            out.append(turn([THINGS[t].shape] if i % 2 else [THINGS[t].colour, THINGS[t].shape], CELLS[t]))
        return out

    def test_a_perfect_mouth_passes_against_the_dealt_phrase_null(self) -> None:
        g = B.k_grade(self.perfect(), draws=100)
        self.assertEqual((g["n"], g["observed"]), (60, 60))
        self.assertLess(g["null_p95"], 60)
        self.assertTrue(g["pass"])
        self.assertEqual(g["null_draws"], 100)

    def test_a_constant_mouth_fails_its_own_null_and_the_ablation_says_so(self) -> None:
        const = [turn(["star"], CELLS[i % 3]) for i in range(60)]              # true on every star, false elsewhere: 20 of 60
        g = B.k_grade(const, draws=100)
        self.assertEqual(g["observed"], 20)
        self.assertEqual(g["null_p95"], 20.0)                                   # dealing a constant phrase changes nothing
        self.assertFalse(g["pass"])
        self.assertEqual(g["ablated"]["phrase"], ["star"])
        self.assertTrue(g["ablated"]["failed_as_it_must"])

    def test_the_ablation_of_a_perfect_mouth_fails_while_the_mouth_passes(self) -> None:
        g = B.k_grade(self.perfect(), draws=100)
        self.assertTrue(g["pass"])
        self.assertTrue(g["ablated"]["failed_as_it_must"])

    def test_the_plant_reads_false(self) -> None:
        g = B.k_grade(self.perfect(), draws=20)
        self.assertTrue(g["plant"]["caught"], g["plant"])
        self.assertTrue(g["plant"]["was_true"])
        self.assertFalse(g["plant"]["reads"])

    def test_silent_turns_count_as_not_true_and_the_rate_divides_by_all(self) -> None:
        rows = self.perfect(30) + [turn(None, None) for _ in range(30)]
        g = B.k_grade(rows, draws=20)
        self.assertEqual((g["n"], g["n_said"], g["observed"]), (60, 30, 30))
        self.assertAlmostEqual(g["rate"], 0.5)

    def test_the_null_is_seeded(self) -> None:
        a = B.k_grade(self.perfect(), draws=30)["null_p95"]
        b = B.k_grade(self.perfect(), draws=30)["null_p95"]
        self.assertEqual(a, b)


class Exist(unittest.TestCase):
    def test_exist_and_its_plant(self) -> None:
        ear = {"m1": ["big", "star"], "m2": ["ring"], "m3": ["square", "green"]}
        rows = [{"moment": "m1", "topic": "star"}, {"moment": "m2", "topic": "ring"}, {"moment": "m3", "topic": "green"}]
        g = B.exist_grade(rows, ear)
        self.assertEqual((g["exist"], g["ok"], g["pass"]), (1.0, 3, True))
        self.assertTrue(g["plant"]["caught"])
        bad = rows + [{"moment": "m2", "topic": "star"}]                      # the topic not among that moment's words
        g2 = B.exist_grade(bad, ear)
        self.assertEqual((g2["ok"], g2["pass"]), (3, False))
        self.assertEqual(g2["missing_first"], ["m2:star"])


class Coverage(unittest.TestCase):
    def test_coverage_counts_mature_words_only_and_the_lock_detector_sees_the_cycle(self) -> None:
        mature = [f"w{i}" for i in range(13)]
        rows = [{"topic": mature[i % 11], "topic_source": "web"} for i in range(300)]
        g = B.coverage_grade(rows, mature)
        self.assertEqual((g["covered"], g["pass"]), (11, True))
        rows2 = [{"topic": mature[i % 4], "topic_source": "web"} for i in range(300)]
        g2 = B.coverage_grade(rows2, mature)
        self.assertEqual((g2["covered"], g2["pass"], g2["lock"]), (4, False, 4))
        self.assertTrue(B.lock_grade([mature[i % 2] for i in range(300)])["caught"])
        self.assertFalse(B.lock_grade([mature[i % 13] for i in range(300)])["caught"])     # period 13 > 4, distinct 13 > 5
        self.assertFalse(B.lock_grade([f"u{i}" for i in range(300)])["caught"])


class Readings(unittest.TestCase):
    def test_age_deciles_read_a_planted_slope(self) -> None:
        ages = list(range(100))
        truth = [a < 50 for a in ages]                                           # old scenes true, new ones false
        d = B.age_deciles(ages, truth)
        self.assertEqual(len(d), 10)
        self.assertEqual([x["rate"] for x in d], [1.0] * 5 + [0.0] * 5)
        flat = B.age_deciles(ages, [True] * 100)
        self.assertTrue(all(x["rate"] == 1.0 for x in flat))

    def test_pairing_counts_the_discordants_and_prints_the_smallest_gap(self) -> None:
        inner = [True] * 30 + [False] * 10
        live = [True] * 20 + [False] * 20
        p = B.paired(inner, live)
        self.assertEqual((p["n"], p["both"], p["inner_only"], p["live_only"], p["neither"]), (40, 20, 10, 0, 10))
        self.assertAlmostEqual(p["smallest_passing_gap"], 0.25)
        self.assertLess(p["sign_test_p_inner_better"], 0.01)
        self.assertEqual(B.paired([], [])["n"], 0)

    def test_spearman_with_a_label_permutation_null(self) -> None:
        rel = {f"w{i}": i / 12 for i in range(13)}
        agree = {f"w{i}": 0.5 + i / 24 for i in range(13)}
        g = B.self_grade(rel, agree, draws=300)
        self.assertAlmostEqual(g["rho"], 1.0)
        self.assertLess(g["p_label_permutation"], 0.02)
        rng = np.random.default_rng(3)
        noise = {f"w{i}": float(rng.random()) for i in range(13)}
        g2 = B.self_grade(rel, noise, draws=300)
        self.assertIsNotNone(g2["rho"])
        self.assertGreater(g2["p_label_permutation"], 0.05, g2)
        self.assertIsNone(B.self_grade({"a": 1.0}, {"a": 1.0}, draws=10)["rho"])

    def test_assoc_against_a_frequency_matched_null(self) -> None:
        mature = ["big", "ring", "star", "small", "white", "red"]
        counts = {"big": 100, "small": 100, "ring": 20, "star": 21, "white": 60, "red": 61}
        hops = [{"topic": "ring", "say": {"words": ["ring"]}}, {"topic": "star", "say": {"words": ["star"]}}] * 20
        g = B.assoc_grade(hops, counts, mature, draws=50)
        self.assertEqual((g["n"], g["share"]), (40, 1.0))
        self.assertTrue(g["above_null_p95"])                                    # the matched words (star↔ring) are never in the say
        none = [{"topic": "ring", "say": {"words": ["big"]}}] * 20
        g2 = B.assoc_grade(none, counts, mature, draws=50)
        self.assertEqual(g2["share"], 0.0)
        self.assertFalse(g2["above_null_p95"])
        self.assertEqual(B.assoc_grade([], counts, mature)["n"], 0)


class CrossCheck(unittest.TestCase):
    """AMENDMENT 2 A2.2: the regenerated spec against the life's truth/scene/<seq>.json, field for field; a one-field plant caught."""

    def setUp(self) -> None:
        import json
        import tempfile
        from pathlib import Path
        self.tmp = Path(tempfile.mkdtemp(prefix="inner-cross-"))
        (self.tmp / "scene").mkdir()
        self.sc = W.train_scene(20261101, 7)
        self.rows = [{"moment": "m7", "world_seed": 20261101, "scene": 7}, {"moment": "m8", "world_seed": 20261101, "scene": 8}]
        self.eye_seq = {"m7": 70, "m8": 80}
        (self.tmp / "scene" / "000000070.json").write_text(json.dumps({"kind": "train", "scene": 7, "world_seed": 20261101,
                                                                      "scene_dict": self.sc.to_dict(), "said": list(self.sc.words)}))
        # m8 has no file: REPORTED, never graded

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_true_file_passes_a_missing_file_is_reported_and_the_plant_is_caught(self) -> None:
        c = B.cross_check(self.rows, [0, 1], self.eye_seq, self.tmp)
        self.assertEqual((c["checked"], c["mismatch"], c["no_file"], c["no_eye"]), (1, 0, 1, 0))
        self.assertTrue(c["plant_caught"])
        self.assertTrue(c["pass"])
        self.assertTrue(c["dir"].endswith("scene"))

    def test_a_wrong_file_is_a_mismatch(self) -> None:
        import json
        d = json.loads((self.tmp / "scene" / "000000070.json").read_text())
        d["scene_dict"]["things"][0]["colour"] = "zzz"
        (self.tmp / "scene" / "000000070.json").write_text(json.dumps(d))
        c = B.cross_check(self.rows[:1], [0], self.eye_seq, self.tmp)
        self.assertEqual((c["checked"], c["mismatch"]), (1, 1))
        self.assertFalse(c["pass"])
        self.assertEqual(c["first_mismatch"]["row"], 0)

    def test_a_row_without_an_eye_row_is_reported(self) -> None:
        c = B.cross_check(self.rows[:1], [0], {}, self.tmp)
        self.assertEqual((c["checked"], c["no_eye"], c["pass"]), (0, 1, False))


class Prints(unittest.TestCase):
    """AMENDMENT 2 A2.3: the self is printed with B1 masked; B1's own observation moves only its delta; any other change shows."""

    def test_b1_is_masked_and_counted(self) -> None:
        from genome import web as _web

        class _Brain:
            def state_hash(self):
                return "h"

        class _Mind:
            pass

        m = _Mind()
        m.brain = _Brain()
        m.webs = None
        m.self_node = _web.SelfNode(author="toy")
        for cid in ("B1", "T1"):
            m.self_node.place(_web.Claim(cid, "x", "usually", 0.9, author="toy"))
        p0 = B.prints(m)
        m.self_node.claims["B1"].observe(True, at=1)
        p1 = B.prints(m)
        self.assertEqual(p0["self_but_B1"], p1["self_but_B1"])
        self.assertEqual(p1["B1_observed"] - p0["B1_observed"], 1)
        m.self_node.claims["T1"].observe(True, at=2)
        p2 = B.prints(m)
        self.assertNotEqual(p1["self_but_B1"], p2["self_but_B1"], "a change outside B1 must show")


class Rows(unittest.TestCase):
    def test_a_synthetic_body_row_carries_its_reading_inline(self) -> None:
        r = B.body_row(5, "2026-10-03T12:00:00.000Z", 0, "m")
        self.assertEqual((r["sense"], r["meta"]["reading"]["backlog"], r["meta"]["source"]), ("body", 0, "body"))
        self.assertNotIn("backlog", B.body_row(6, "2026-10-03T12:01:00.000Z", None, "m")["meta"]["reading"])


if __name__ == "__main__":
    unittest.main()
