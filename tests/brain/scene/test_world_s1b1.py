# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:42 +0400 — PREREG-S1B1 §1, §4, §5 (genome-wt-brain3 docs/brain/r3/PREREG-S1B1.md,
# sha caace482…): the three NEW splits of each test seed, drawn from named substreams of the TEST seed and placed by
# _place, the parent silent — M3 COMPOSE (60: the six held-out pairs, the distractor kinds), SPEAK (96: trained things,
# twins redrawn), DECLINE (48: a PURPLE target; kind B = the distractor shares shape and size, kind A = other shapes).
# Test-first: red on scene-talk 4093ff9 (the splits do not exist there).
from __future__ import annotations

import collections
import itertools
import unittest

from brain.scene import world as W

TS = 20261201


def _twins(things):
    return any((a.shape, a.colour, a.size) == (b.shape, b.colour, b.size) for a, b in itertools.combinations(things, 2))


class TestCounts(unittest.TestCase):
    def test_constants_are_the_preregs(self) -> None:
        self.assertEqual((W.M3_TWO, W.M3_THREE), (40, 20))
        self.assertEqual((W.SPEAK_TWO, W.SPEAK_THREE), (64, 32))
        self.assertEqual((W.DECLINE_TWO, W.DECLINE_THREE), (32, 16))
        self.assertEqual([W.split_size(s) for s in ("m3", "speak", "decline")], [60, 96, 48])
        for s, n in (("m3", 60), ("speak", 96), ("decline", 48)):
            self.assertEqual(len(W.scenes_for(s, TS)), n)


class TestM3(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sc = {ts: W.scenes_for("m3", ts) for ts in W.TEST_SEEDS.values()}

    def test_target_is_a_heldout_pair_and_the_phrase_is_uniquely_true(self) -> None:
        for ts, sc in self.sc.items():
            for s in sc:
                t = s.things[s.referent]
                shape, colour = W.HELDOUT[s.index % 6]
                self.assertEqual((t.shape, t.colour), (shape, colour))
                self.assertNotIn((t.shape, t.colour), W.ALLOWED)
                self.assertEqual(s.words, (colour, shape))                      # «⟨colour⟩ ⟨shape⟩» (T2)
                self.assertEqual([k for k, u in enumerate(s.things) if W.phrase_true_of(s.words, u)], [s.referent])
                self.assertEqual(len(s.things), 2 if s.index < 40 else 3)
                self.assertFalse(_twins(s.things))
                for k, u in enumerate(s.things):
                    if k != s.referent:
                        self.assertIn((u.shape, u.colour), W.ALLOWED)          # distractors are trained things

    def test_distractor_kinds_make_the_words_necessary(self) -> None:
        """2-thing i even: the distractor shares the target's COLOUR (its shape is never the target's — the pair is held
        out); i odd: shares the SHAPE; 3-thing: one of each, so BOTH words are necessary there."""
        for ts, sc in self.sc.items():
            for s in sc:
                t = s.things[s.referent]
                others = [u for k, u in enumerate(s.things) if k != s.referent]
                kind = W.m3_kind(s.index)
                colour_sharers = [u for u in others if u.colour == t.colour]
                shape_sharers = [u for u in others if u.shape == t.shape]
                for u in colour_sharers:
                    self.assertNotEqual(u.shape, t.shape)
                if kind == "colour":
                    self.assertEqual((len(colour_sharers), len(shape_sharers)), (1, 0))
                elif kind == "shape":
                    self.assertEqual((len(colour_sharers), len(shape_sharers)), (0, 1))
                else:
                    self.assertEqual(kind, "both")
                    self.assertEqual((len(colour_sharers), len(shape_sharers)), (1, 1))
                    self.assertEqual(len(s.things), 3)
        per_pair = collections.Counter(W.HELDOUT[s.index % 6] for s in self.sc[TS])
        self.assertEqual(set(per_pair.values()), {10})


class TestSpeak(unittest.TestCase):
    def test_trained_things_no_twins_a_target(self) -> None:
        for ts in W.TEST_SEEDS.values():
            for s in W.scenes_for("speak", ts):
                self.assertEqual(len(s.things), 2 if s.index < 64 else 3)
                self.assertFalse(_twins(s.things))
                for u in s.things:
                    self.assertIn((u.shape, u.colour), W.ALLOWED)
                self.assertTrue(0 <= s.referent < len(s.things))
                self.assertEqual(s.words, ())                                    # the learner hears nothing


class TestDecline(unittest.TestCase):
    def test_purple_target_and_the_two_kinds(self) -> None:
        kinds = collections.Counter()
        for ts in W.TEST_SEEDS.values():
            for s in W.scenes_for("decline", ts):
                t = s.things[s.referent]
                others = [u for k, u in enumerate(s.things) if k != s.referent]
                self.assertEqual(t.colour, "purple")
                self.assertIn(t.shape, W.SHAPES)
                self.assertFalse(_twins(s.things))
                for u in others:
                    self.assertIn((u.shape, u.colour), W.ALLOWED)
                kind = W.decline_kind(s.index)
                kinds[kind] += 1
                if kind == "B":
                    self.assertEqual(len(s.things), 2)
                    self.assertEqual(s.index % 2, 0)
                    self.assertEqual((others[0].shape, others[0].size), (t.shape, t.size))
                else:
                    self.assertTrue(all(u.shape != t.shape for u in others))
  # edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 20:3x +0400 — PREREG-BRAIN-LONG-6 §1.2
  # (the law SIGNED; SEAT-LINE sha256 2c6bb22b…): the pin gains the law's declared content (the scene world
  # lawful at the life's seed 20261211; the 10-09 launch-verdict item repaired) — the pin working, caught at
  # the launch gate's first full run and updated under the law, never loosened.
        self.assertEqual(kinds, collections.Counter({"A": 32 * 4, "B": 16 * 4}))  # the law's 4th world seed (20261211) carries its own 48


class TestDeterminismAndPixels(unittest.TestCase):
    def test_specs_and_pixels_are_functions_of_seed_and_index(self) -> None:
        import numpy as np
        for maker, i in ((W.m3_scene, 7), (W.speak_scene, 70), (W.decline_scene, 40)):
            a, b = maker(TS, i), maker(TS, i)
            self.assertEqual(a, b)
            ra, _ = W.render_scene(a)
            rb, _ = W.render_scene(b)
            self.assertTrue(np.array_equal(ra, rb))
        self.assertNotEqual(W.m3_scene(20261201, 3).to_dict()["things"], W.m3_scene(20261202, 3).to_dict()["things"])

    def test_the_new_splits_do_not_move_the_old_ones(self) -> None:
        """S1a's splits are drawn by the same code as before: a spec digest of the first scenes, fixed here from S1a's own
        world (the full byte-identity against S1a's caches is the gate's identity step)."""
        self.assertEqual(W.train_scene(20261101, 2699).to_dict()["things"][1]["shape"], "moon")
        self.assertEqual(W.test_scene(20261201, 17), W.test_scene(20261201, 17))
        self.assertEqual(W.scenes_for("m6", 20261201, 3), [W.m6_scene(20261201, i) for i in range(3)])


if __name__ == "__main__":
    unittest.main()
