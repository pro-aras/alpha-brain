"""Tests for TOY C's plant machinery (docs/research/toys/PREREG-TOY-FRAMES.md §3 PLANT, §4 PLANT-FOUND, §7 G4). Written FIRST, STAGE 3a (red, then green, a log each).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:01 +0400 — STAGE 3a: the PERFECT-MECHANISM reading the seat asked for (17:0x: what the ORIGINAL whole-set clause «each such set's G > 0»
# reads for a mechanism that finds the planted frame EXACTLY and keeps nothing else): the one-frame set {(zzq, xxv)} on the planted split, against its own control on the
# plain split. Every number is compared with the SLOW recount of compress.py (slow_gain), never with the code under test.
"""
from __future__ import annotations

import unittest

import numpy as np

from tools.toys.frames import compress as CO
from tools.toys.frames import plants as PL
from tools.toys.frames import streams as ST


def words_stream(n: int, seed: int = 0, vocab: int = 30):
    rng = np.random.default_rng(seed)
    return [ST.Moment("s", f"m{i}", (f"w{int(rng.integers(0, vocab))}",), (float(i + 1),)) for i in range(n)]


def parts(ms):
    tr, he = ST.split(ms)
    return [m.words for m in tr], [m.words for m in he]


class TestPerfectReading(unittest.TestCase):
    def test_the_split_is_taken_after_planting_and_the_plants_are_counted_by_part(self):
        ms = words_stream(500)
        r = PL.perfect_reading(ms, every=10)
        self.assertEqual(r["n_moments"], 550)                                     # 500 + one plant after every 10th
        self.assertEqual(r["n_train"], ST.split_index(550))                       # 330
        self.assertEqual(r["n_held"], 550 - 330)
        planted = ST.with_plant(ms, 10)
        tr, he = ST.split(planted)
        self.assertEqual(r["plants_train"], sum(1 for m in tr if m.source == "plant"))
        self.assertEqual(r["plants_held"], sum(1 for m in he if m.source == "plant"))
        self.assertEqual(r["plants_train"] + r["plants_held"], 50)
        self.assertNotEqual(r["n_moments"], len(ms))                              # the plant changed the stream

    def test_the_reading_equals_the_slow_recount_on_the_planted_split(self):
        ms = words_stream(500, seed=3)
        r = PL.perfect_reading(ms, every=10)
        slow = CO.slow_gain(*parts(ST.with_plant(ms, 10)), {ST.PLANT})
        self.assertAlmostEqual(r["G"], slow["G"], places=9)
        for k in ("bits0", "bitsF", "L"):
            self.assertAlmostEqual(r[k], slow[k], places=9, msg=k)
        for k in ("N", "K", "V"):
            self.assertEqual(r[k], slow[k], k)

    def test_a_frequent_plant_pays_and_the_same_frame_on_the_plain_stream_does_not(self):
        ms = words_stream(500, seed=4)
        r = PL.perfect_reading(ms, every=5)
        self.assertGreater(r["G"], 0.0)                                            # a frame found exactly, on a stream that carries it, saves bits net of its own cost
        slow_plain = CO.slow_gain(*parts(ms), {ST.PLANT})
        self.assertAlmostEqual(r["control_plain_G"], slow_plain["G"], places=9)    # the control IS the same one-frame set on the unplanted split
        self.assertAlmostEqual(r["control_plain_L"], slow_plain["L"], places=9)
        self.assertLess(r["control_plain_G"], -r["control_plain_L"] + 1e-9)        # it never fires: every held-out bit it changes is a loss, and K only grows
        self.assertLess(r["control_plain_G"], 0.0)

    def test_a_plant_that_is_too_rare_to_repay_its_model_cost_reads_negative(self):
        """the instrument can say NO: with one plant in train and one in the held-out part the frame cannot repay 2 log2 V bits."""
        r = PL.perfect_reading(words_stream(200, seed=5), every=100)               # 202 moments: split 121, plants after 100 (train) and 200 (held)
        self.assertEqual((r["plants_train"], r["plants_held"]), (1, 1))
        self.assertLess(r["G"], 0.0)


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:09 +0400 — the plant tokens' premise («two tokens in no vocabulary», law §3) is a GATE now: xxv is a REAL word of alpha4-1's shelf text (a chapter
# heading, 4 moments: docs/research/toys/records/frames/ORIENT-plant_tokens_outside.out), so the second plant token is replaced (AMENDMENT-1) and every run counts both tokens' real occurrences.
class TestPlantTokens(unittest.TestCase):
    def test_occurrences_are_counted_outside_the_plant_moments_only(self):
        first, second = ST.PLANT
        ms = [ST.Moment("shelf", "a", ("lesson", second), (1.0, 2.0)), ST.Moment("shelf", "b", ("x",), (3.0,)), ST.Moment("shelf", "c", (first, "y"), (4.0, 5.0))]
        self.assertEqual(PL.plant_token_occurrences(ms), {first: 1, second: 1})
        planted = ST.with_plant(ms, 1)                                              # three plant moments added: they must not be counted
        self.assertEqual(sum(1 for m in planted if m.source == "plant"), 3)
        self.assertEqual(PL.plant_token_occurrences(planted), {first: 1, second: 1})
        self.assertEqual(PL.plant_token_occurrences([ST.Moment("shelf", "d", ("w",), (6.0,))]), {first: 0, second: 0})

    def test_the_plant_is_two_distinct_tokens(self):
        self.assertEqual(len(ST.PLANT), 2)
        self.assertNotEqual(*ST.PLANT)

    @unittest.skipUnless((ST.COPIES / "alpha4-1" / "tape").is_dir() and (ST.COPIES / "brain-full-20261102" / "tape").is_dir(), "the copies are not made yet")
    def test_the_plant_tokens_occur_in_no_real_stream_G1(self):
        """G1 (law §7, extended by AMENDMENT-1): both plant tokens occur in ZERO rows of every copied stream (the premise «in no vocabulary» is read, not assumed)."""
        a4 = ST.load_moments(sorted((ST.COPIES / "alpha4-1" / "tape").glob("*.jsonl")))
        sc = ST.scene_moments(ST.load_moments(sorted((ST.COPIES / "brain-full-20261102" / "tape").glob("*.jsonl"))))
        for name, ms in (("ALPHA4", a4), ("SCENE", sc)):
            self.assertEqual(PL.plant_token_occurrences(ms), {t: 0 for t in ST.PLANT}, name)


if __name__ == "__main__":
    unittest.main()
