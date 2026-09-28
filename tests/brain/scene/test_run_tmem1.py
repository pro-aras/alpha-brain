# edit: Claude (Opus 5.5, T-MEM-1 builder), 2026-09-28 17:24 +0400 — PREREG-TMEM1 (genome-wt-brain3 ce41448, sha 0a87fefc…, final): the
# runner. The shas (a planted foreign one refuses); the BWT arithmetic (R_{j,i}, BWT_j = mean_{i<j}(R_{j,i} − R_{i,i}), the
# binomial SE of the pooled accuracy), the paired gate difference and its SE; the two schedules (the sequential rooms by
# block; S1c's band stream 1 with its round-robin); a BASE life reads its five roads over ONE training and keeps its
# ORDER-FREE PIN; a replay life draws only consumed scenes; the SURPRISE life replays the top-R by the loss at storage;
# the GATE life counts no step on which an anchor's loss rose; the gate's two-word toy. Test-first: red on scene-tmem1
# 51126f2 (run_tmem1 does not exist there).
from __future__ import annotations

import unittest
from unittest import mock

import numpy as np

from brain.scene import pickers as PK
from brain.scene import run_tmem1 as T
from tests.brain.scene.test_run_s1c import HAVE_TEST_SET, FakeRooms

LAW = ("R1", "R2", "R3", "N")


class TestShasAndConstants(unittest.TestCase):
    def test_the_shas(self) -> None:
        got = T.check_prereg()
        self.assertEqual(got["prereg_tmem1"], "0a87fefcef415a8b2964008f986577f90c0e6c2fb5141711b2ef00fb9ad59423")
        self.assertEqual(got["conclusion_memory"], "015da3e66da89cb57c9080e5cb3ab9760ecdb7410ffd744dab71f045330c2b12")
        with mock.patch.object(T, "PREREG_TMEM1_SHA256", "0" * 64):
            with self.assertRaises(T.TmemError):
                T.check_prereg()

    def test_the_constants(self) -> None:
        self.assertEqual(T.READ_POINTS, (50, 100, 150, 200))
        self.assertEqual(T.SHAPE_TASKS, (("circle", "square"), ("triangle", "cross"), ("ring", "star")))
        self.assertEqual(len(T.LIVES), 8)
        self.assertEqual(T.chosen_eps(), 0.3)


class TestMarks(unittest.TestCase):
    def test_the_bwt_arithmetic(self) -> None:
        n = {"a": 10, "b": 10, "c": 20}
        rates = {50: {"a": 1.0, "b": 0.0, "c": 0.0}, 100: {"a": 0.8, "b": 0.9, "c": 0.0},
                 150: {"a": 0.5, "b": 0.6, "c": 1.0}, 200: {"a": 0.5, "b": 0.6, "c": 0.5}}
        s = T.bwt_series(rates, [("a",), ("b",), ("c",)], n)
        self.assertAlmostEqual(s["BWT"][2], 0.8 - 1.0)
        self.assertAlmostEqual(s["BWT"][3], ((0.5 - 1.0) + (0.6 - 0.9)) / 2)
        p = (0.5 * 10 + 0.6 * 10) / 20
        self.assertAlmostEqual(s["SE"][3], (p * (1 - p) / 20) ** 0.5)

    def test_the_paired_gate_difference(self) -> None:
        g = {"pairs": {50: {1: [1, 1, 1, 1]}, 100: {2: [1, 1, 0, 0]}, 150: {1: [1, 1, 1, 0], 2: [1, 1, 0, 0]}}}
        r = {"pairs": {50: {1: [1, 1, 1, 1]}, 100: {2: [1, 0, 0, 0]}, 150: {1: [1, 0, 0, 0], 2: [0, 0, 0, 0]}}}
        pg = T.paired_gate(g, r, {})
        self.assertAlmostEqual(pg["diff"], (0.5 + 0.25) / 2)
        self.assertEqual(pg["n"], [4, 4])
        self.assertGreater(pg["se"], 0)

    def test_the_schedules(self) -> None:
        self.assertEqual([T.schedule_room("seq", b, LAW, None, {}, {})[0] for b in (1, 50, 51, 100, 101, 150, 151, 200)],
                         ["R1", "R1", "R2", "R2", "R3", "R3", "N", "N"])
        p = PK.RandomPicker(LAW, 20261301, prefix=PK.band_prefix(20261301, 1))
        self.assertEqual([T.schedule_room("random", b, LAW, p, {}, {})[0] for b in (1, 2, 3, 4)], list(LAW))
        self.assertEqual(T.schedule_room("random", 9, LAW, p, {}, {}), p.pick(9, None))

    def test_the_gate_toy(self) -> None:
        self.assertTrue(T.gate_toy()["pass"])


@unittest.skipUnless(HAVE_TEST_SET, "the fixed test set's caches are not on this box")
class TestLives(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test = T.TestSetM()
        cls.data = FakeRooms(rooms=LAW)

    def test_base_reads_its_roads_over_one_training_and_keeps_its_pin(self) -> None:
        b = T.life_m1(self.data, self.test, "BASE", "seq", n_blocks=52, eps=0.3)
        self.assertEqual(sorted(b["roads"]["READ"]), list(range(1, 53)))
        self.assertEqual(sorted(b["roads"]["TIME-WINDOW"]), [50])
        self.assertTrue(b["order_free_pin"]["pass"])
        self.assertEqual([x["room"] for x in b["record"]], ["R1"] * 50 + ["R2"] * 2)
        self.assertIn(50, b["pairs"])

    def test_a_replay_life_draws_only_consumed_scenes_and_surprise_takes_the_top(self) -> None:
        for name in ("UNIFORM", "DRIFT", "SURPRISE", "ORACLE-DRIFT", "DRIFT-NULL"):
            r = T.life_m1(self.data, self.test, name, "random", n_blocks=12, eps=0.3)
            consumed = set()
            for x in r["record"]:
                consumed |= {(x["room"], i) for i in range(x["start"], x["start"] + PK.BLOCK)}
                self.assertEqual(len(x["replay"]), T.R_REPLAY)
                for q, i in x["replay"]:
                    self.assertIn((q, i), consumed, name)

    def test_the_gate_life_counts_no_rise(self) -> None:
        g = T.life_m1(self.data, self.test, "GATE", "seq", n_blocks=30, eps=0.3)
        self.assertEqual(g["gate_rises_total"], 0)
        self.assertTrue(all("gate" in x for x in g["record"]))


if __name__ == "__main__":
    unittest.main()
