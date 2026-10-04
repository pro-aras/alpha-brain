"""Tests for TOY C's ANATOMY of a gain: G(F) = M + D + C − L, an exact split of the held-out saving into the held-out MERGE savings (M), the DENOMINATOR credit (D) and the COUNT-SHIFT loss (C)
(the architect's 17:1x RAISE: «print G(F) split into the held-out merge savings and the train-merge term»; AMENDMENT-1 §1.3 for the plant). Written FIRST, STAGE 3d (red, then green).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:44 +0400 — STAGE 3d. The split, by token class: a held-out FRAME token (a firing) saves cost0(a) + cost0(b) − costF(frame) [M]; every other held-out token
# (an unmerged word or an END) has cost0 − costF = log2((cF + 1)/(c0 + 1)) [its own train count moved: C <= 0 for the words a frame consumed] + log2((N0 + K0)/(NF + KF)) [the shorter train: D > 0].
"""
from __future__ import annotations

import math
import unittest

from tools.toys.frames import anatomy as AN
from tools.toys.frames import compress as CO
from tests.tools.test_toys_frames import random_frames, random_stream


class TestByHand(unittest.TestCase):
    def test_the_stage_one_example_split_on_paper(self):
        """train [a b][a b][c], held [a b][a d][c], F = {(a, b)}. Under the empty set N0 = 8 (a 2, b 2, c 1, END 3), K0 = 5; under F N = 6 (F 2, c 1, END 3), K = 6.
        Held under F: [F END] [a UNK END] [c END]. M: the one firing, cost0(a) + cost0(b) − costF(F) = 2 log2(13/3) − log2(12/3) = 2 log2(13/3) − 2.
        Unmerged held tokens: END, a, UNK, END, c, END = 6; D = 6 log2(13/12). C: only `a` moved its train count (2 -> 0): log2(1/3) = −log2 3. L = 2 log2 3."""
        train = [["a", "b"], ["a", "b"], ["c"]]
        held = [["a", "b"], ["a", "d"], ["c"]]
        d = AN.decompose_gain(CO.Scorer(train, held), {("a", "b")})
        self.assertAlmostEqual(d["M"], 2 * math.log2(13 / 3) - 2, places=12)
        self.assertAlmostEqual(d["D"], 6 * math.log2(13 / 12), places=12)
        self.assertAlmostEqual(d["C"], -math.log2(3), places=12)
        self.assertAlmostEqual(d["L"], 2 * math.log2(3), places=12)
        self.assertEqual((d["firings"], d["unmerged"]), (1, 6))
        self.assertAlmostEqual(d["T"], d["D"] + d["C"], places=12)
        self.assertAlmostEqual(d["G"], -1.8310699, places=6)                                          # the stage-1 test's own hand figure
        self.assertAlmostEqual(d["M"] + d["D"] + d["C"] - d["L"], d["G"], places=12)

    def test_the_empty_set_has_nothing_to_split(self):
        d = AN.decompose_gain(CO.Scorer([["a", "b"], ["c"]], [["a"], ["b", "c"]]), set())
        self.assertEqual((d["M"], d["D"], d["C"], d["L"], d["G"], d["firings"]), (0.0, 0.0, 0.0, 0.0, 0.0, 0))


class TestIdentity(unittest.TestCase):
    def test_the_parts_sum_to_the_slow_recount_on_random_streams(self):
        n = 0
        for seed in range(40):
            train, held = random_stream(seed, unk_every=4)
            sc = CO.Scorer(train, held)
            for k in (1, 3, 6):
                F = random_frames(seed * 17 + k, k)
                d = AN.decompose_gain(sc, F)
                slow = CO.slow_gain(train, held, F)
                self.assertAlmostEqual(d["M"] + d["D"] + d["C"] - d["L"], slow["G"], places=8, msg=(seed, k))
                self.assertAlmostEqual(d["G"], slow["G"], places=8, msg=(seed, k))
                n += 1
        self.assertEqual(n, 120)

    def test_the_identity_check_can_see_a_wrong_part(self):
        train, held = random_stream(5, unk_every=4)
        sc = CO.Scorer(train, held)
        F = random_frames(5, 4)
        d = AN.decompose_gain(sc, F)
        slow = CO.slow_gain(train, held, F)
        self.assertGreater(abs(d["C"]), 1e-3)                                                          # the plant is only a plant if C is not ~0 here
        wrong = d["M"] + d["D"] - d["C"] - d["L"]                                                      # a sign error in one part
        self.assertGreater(abs(wrong - slow["G"]), 1e-3)
        self.assertAlmostEqual(d["M"] + d["D"] + d["C"] - d["L"], slow["G"], places=8)

    def test_a_frame_that_never_fires_has_no_merge_and_only_its_cost_and_the_k_effect(self):
        train, held = [["a"], ["b"]], [["a"], ["b"]]
        d = AN.decompose_gain(CO.Scorer(train, held), {("a", "b")})
        self.assertEqual((d["firings"], d["M"], d["C"]), (0, 0.0, 0.0))
        self.assertLess(d["D"], 0.0)                                                                   # K grew by one, N did not shrink: every held token pays a little
        self.assertAlmostEqual(d["G"], -d["L"] + d["D"], places=12)


if __name__ == "__main__":
    unittest.main()
