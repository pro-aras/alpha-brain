# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:03 +0400 — S1a step 1 (PREREG-R3-TONIGHT §S1a «The world»): the world
# exactly as the PREREG fixes it. Deterministic by seed; the parent never lies (10,000 scenes walked per world seed); no
# held-out pair, no purple and no never-taught shape in training; dax exactly once, at scene 2,700, alone with one
# trained thing; the separation rule and the fixation→thing rule proved against the PREREG's own claim («fixations on two
# different things can never join» under the 2-cell merge rule). Interpreter-agnostic (spec walks + same-interpreter
# render comparisons), so it passes under /usr/bin/python3 and the brain venv alike.
from __future__ import annotations

import collections
import itertools
import unittest

import numpy as np

from brain.scene import world as W


class TestConstantsAreThePreregs(unittest.TestCase):
    def test_things_colours_sizes(self) -> None:
        self.assertEqual(W.SHAPES, ("circle", "square", "triangle", "cross", "ring", "star"))
        self.assertEqual(W.COLOURS, {"red": (230, 50, 50), "blue": (60, 90, 240), "green": (50, 200, 70),
                                     "yellow": (235, 220, 50), "white": (245, 245, 245)})
        self.assertEqual(W.PURPLE, ("purple", (150, 60, 200)))
        self.assertEqual(W.SIZES, {"big": 32, "small": 22})
        self.assertEqual(set(W.NEVER_TAUGHT), {"arrow", "wave", "diamond", "house", "tree", "cup", "key"})
        self.assertEqual(W.SCENE_MIX, ((1, 0.4), (2, 0.4), (3, 0.2)))
        self.assertEqual(W.SEPARATION_PX, 24)
        self.assertEqual((W.DAX_SHAPE, W.DAX_WORD, W.DAX_SCENE), ("moon", "dax", 2700))
  # edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 20:3x +0400 — PREREG-BRAIN-LONG-6 §1.2
  # (the law SIGNED; SEAT-LINE sha256 2c6bb22b…): the pin gains the law's declared content (the scene world
  # lawful at the life's seed 20261211; the 10-09 launch-verdict item repaired) — the pin working, caught at
  # the launch gate's first full run and updated under the law, never loosened.
        self.assertEqual(W.WORLD_SEEDS, (20261101, 20261102, 20261103, 20261211))
        self.assertEqual(W.TEST_SEEDS, {20261101: 20261201, 20261102: 20261202, 20261103: 20261203, 20261211: 20261321})
        self.assertEqual((W.TOY_SEED, W.STAGE_SEED, W.HELDOUT_SEED), (20261099, 20261100, 20260928))
        self.assertEqual(W.READING_POINTS, (250, 500, 1000, 2000, 5000, 10000))
        self.assertEqual((W.N_TRAIN, W.N_TEST, W.GATE_N, W.STAGE_N, W.TOY_TRAIN_N, W.TOY_TEST_N), (10000, 400, 300, 300, 1000, 200))
        self.assertEqual(len(W.M2B_SHAPES) * W.M2B_PER_SHAPE, 48)
        self.assertEqual((W.M6_TWO + W.M6_THREE, W.M6_TWO, W.M6_THREE), (42, 28, 14))

    def test_templates(self) -> None:
        t = W.Thing("star", "green", "small", 0, 0)
        self.assertEqual(W.template_words("T1", t), ("star",))
        self.assertEqual(W.template_words("T2", t), ("green", "star"))
        self.assertEqual(W.template_words("T3", t), ("small", "star"))
        self.assertEqual(W.template_words("T4", t), ("small", "green", "star"))


class TestHeldOut(unittest.TestCase):
    def test_six_pairs_each_shape_and_colour_keeps_three(self) -> None:
        h = W.heldout_pairs()
        self.assertEqual(h, W.HELDOUT)                      # deterministic: seeded 20260928
        self.assertEqual(len(set(h)), 6)
        for s in W.SHAPES:
            self.assertGreaterEqual(sum(1 for c in W.COLOUR_NAMES if (s, c) not in h), 3, s)
        for c in W.COLOUR_NAMES:
            self.assertGreaterEqual(sum(1 for s in W.SHAPES if (s, c) not in h), 3, c)
        self.assertEqual(len(W.ALLOWED), 24)
        self.assertFalse(set(W.ALLOWED) & set(h))


class TestTrainingStream(unittest.TestCase):
    """10,000 scenes walked per world seed (specs only — the pixels are not needed to know what the parent said)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.streams = {s: W.train_stream(s) for s in W.WORLD_SEEDS}

    def test_the_parent_never_lies(self) -> None:
        for seed, sc in self.streams.items():
            self.assertEqual(len(sc), 10000)
            for s in sc:
                self.assertIsNotNone(s.referent)
                ref = s.things[s.referent]
                self.assertTrue(W.phrase_true_of(s.words, ref), (seed, s.index, s.words, ref))
                if s.index == W.DAX_INDEX:
                    self.assertEqual(s.words, ("dax",))
                    self.assertEqual(ref.shape, "moon")
                else:
                    # ONE utterance from the finite list only: a template of the referent
                    self.assertIn(s.template, W.TEMPLATES)
                    self.assertEqual(s.words, W.template_words(s.template, ref))

    def test_no_heldout_pair_no_purple_no_never_taught_in_training(self) -> None:
        for seed, sc in self.streams.items():
            for s in sc:
                for t in s.things:
                    self.assertNotEqual(t.colour, "purple")
                    self.assertNotIn(t.shape, W.NEVER_TAUGHT)
                    if t.shape != "moon":
                        self.assertIn(t.shape, W.SHAPES)
                        self.assertNotIn((t.shape, t.colour), W.HELDOUT, (seed, s.index))
                    self.assertIn(t.colour, W.COLOURS)
                for w in s.words:
                    self.assertIn(w, W.VOCAB)
                    self.assertNotEqual(w, "purple")

    def test_dax_exactly_once_at_2700_alone_with_one_trained_thing(self) -> None:
        for seed, sc in self.streams.items():
            moons = [s.index for s in sc for t in s.things if t.shape == "moon"]
            daxes = [s.index for s in sc if "dax" in s.words]
            self.assertEqual(moons, [2699], seed)
            self.assertEqual(daxes, [2699], seed)
            s = sc[2699]
            self.assertEqual(len(s.things), 2)
            other = [t for t in s.things if t.shape != "moon"][0]
            self.assertIn((other.shape, other.colour), W.ALLOWED)

    def test_scene_mix_and_uniform_parent(self) -> None:
        for seed, sc in self.streams.items():
            reg = [s for s in sc if s.index != W.DAX_INDEX]
            n = len(reg)
            cnt = collections.Counter(len(s.things) for s in reg)
            for k, p in W.SCENE_MIX:
                sd = (p * (1 - p) / n) ** 0.5
                self.assertLess(abs(cnt[k] / n - p), 4 * sd, (seed, k, cnt))
            tpl = collections.Counter(s.template for s in reg)
            for t in W.TEMPLATES:
                self.assertLess(abs(tpl[t] / n - 0.25), 4 * (0.25 * 0.75 / n) ** 0.5, (seed, tpl))
            pairs = collections.Counter((t.shape, t.colour) for s in reg for t in s.things)
            self.assertEqual(set(pairs), set(W.ALLOWED))

    def test_boxes_inside_and_separated(self) -> None:
        for seed, sc in self.streams.items():
            for s in sc:
                for t in s.things:
                    self.assertTrue(0 <= t.top <= 128 - t.side and 0 <= t.left <= 128 - t.side)
                for a, b in itertools.combinations(s.things, 2):
                    self.assertGreaterEqual(W.box_gap(a, b), 24, (seed, s.index))


class TestDeterminism(unittest.TestCase):
    def test_specs_are_a_function_of_seed_and_index(self) -> None:
        for i in (0, 7, 2699, 9999):
            self.assertEqual(W.train_scene(20261101, i), W.train_scene(20261101, i))
        a = [W.train_scene(20261101, i).to_dict() for i in range(50)]
        b = [W.train_scene(20261102, i).to_dict() for i in range(50)]
        self.assertNotEqual([x["things"] for x in a], [x["things"] for x in b])
        # order independence: the 40th scene does not depend on whether scenes 0..39 were drawn first
        self.assertEqual(W.train_scene(20261103, 40), W.train_stream(20261103, 41)[40])

    def test_pixels_are_a_function_of_the_scene(self) -> None:
        for s in (W.train_scene(20261101, 3), W.train_scene(20261102, 2699), W.m2b_scene(20261201, 50),
                  W.m6_scene(20261203, 30), W.toy_test_scene(5)):
            r1, c1 = W.render_scene(s)
            r2, c2 = W.render_scene(s)
            self.assertEqual(r1.dtype, np.uint8)
            self.assertEqual(r1.shape, (128, 128, 3))
            self.assertTrue(np.array_equal(r1, r2))
            self.assertEqual(c1, c2)
            for t, (cy, cx) in zip(s.things, c1):     # the ink centroid lies inside the thing's box
                self.assertTrue(t.top <= cy < t.top + t.side and t.left <= cx < t.left + t.side)


class TestTestSets(unittest.TestCase):
    def test_regular_test_scenes_carry_no_heldout_no_never_taught_no_moon(self) -> None:
        for seed in W.TEST_SEEDS.values():
            sc = W.scenes_for("test", seed)
            self.assertEqual(len(sc), 400)
            for s in sc:
                self.assertEqual(s.words, ())               # the parent is silent at test
                for t in s.things:
                    self.assertIn((t.shape, t.colour), W.ALLOWED)

    def test_m2b_is_one_never_taught_shape_alone(self) -> None:
        sc = W.scenes_for("m2b", 20261201)
        self.assertEqual(len(sc), 56)
        shapes = collections.Counter(s.things[0].shape for s in sc)
        self.assertEqual(shapes, collections.Counter({s: 8 for s in W.M2B_SHAPES + ("diamond",)}))
        for s in sc:
            self.assertEqual(len(s.things), 1)
            self.assertIn(s.things[0].colour, W.COLOURS)
            self.assertIn(s.things[0].size, W.SIZES)

    def test_m6_is_dax_among_two_or_three_in_a_2_to_1_mix(self) -> None:
        sc = W.scenes_for("m6", 20261202)
        self.assertEqual(collections.Counter(len(s.things) for s in sc), collections.Counter({2: 28, 3: 14}))
        for s in sc:
            self.assertEqual(s.words, ("dax",))
            self.assertEqual([t.shape for t in s.things].count("moon"), 1)
            self.assertEqual(s.things[s.referent].shape, "moon")

    def test_toy_and_stage(self) -> None:
        self.assertEqual({len(s.things) for s in W.scenes_for("toy-train", W.TOY_SEED)}, {1})
        self.assertEqual({len(s.things) for s in W.scenes_for("toy-test", W.TOY_SEED)}, {2})
        self.assertEqual(len(W.scenes_for("stage", W.STAGE_SEED)), 300)


class TestFixationTruthRule(unittest.TestCase):
    """The PREREG's own claim, proved under the declared fixation→thing rule (the probe's box ± 4 px): with boxes ≥ 24 px
    apart, a cell maps to at most one thing, and two cells on two different things are ≥ 3 grid cells apart (Chebyshev),
    so the 2-cell union-find can never join them directly. Exhaustive over every alignment of the gap."""

    def test_cells_on_two_things_are_three_cells_apart(self) -> None:
        worst = 99
        for side_a, side_b in itertools.product((22, 32), repeat=2):
            for top_a in range(0, 16):
                for gap in (24, 25, 26, 30):
                    a = W.Thing("circle", "red", "big" if side_a == 32 else "small", top_a, 40)
                    top_b = top_a + side_a + gap
                    if top_b + side_b > 128:
                        continue
                    b = W.Thing("star", "blue", "big" if side_b == 32 else "small", top_b, 40)
                    self.assertGreaterEqual(W.box_gap(a, b), 24)
                    cells = [(y, x) for y in range(16) for x in range(16)]
                    on = {k: [c for c in cells if W.fixation_thing(c, (a, b)) == k] for k in (0, 1)}
                    self.assertTrue(on[0] and on[1])
                    d = min(max(abs(p[0] - q[0]), abs(p[1] - q[1])) for p in on[0] for q in on[1])
                    worst = min(worst, d)
        self.assertGreaterEqual(worst, 3)

    def test_a_violating_scene_is_refused(self) -> None:
        a = W.Thing("circle", "red", "big", 0, 0)
        b = W.Thing("star", "blue", "big", 0, 32)            # touching boxes: the planted offender
        self.assertLess(W.box_gap(a, b), 24)
        with self.assertRaises(W.WorldError):                  # cell (1, 3)'s centre (12, 28) lies in both ± 4 px boxes
            W.fixation_thing((1, 3), (a, b))


if __name__ == "__main__":
    unittest.main()
