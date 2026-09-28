# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 15:57 +0400 — PREREG-S1B1R §2 (sha 879a22fb…) with AMENDMENT 1 §2 (sha a198f0b4…):
# the FRESH test seeds 20261401 / 02 / 03 (paired with the world seeds; S1c's world seeds 2026130x are a different role) and
# SPEAK2, the NEED items — 60 THREE-thing scenes per seed in three kinds of 20 (CS i 0–19, SC i 20–39, SS i 40–59), each
# drawn WHOLE (the target and both distractors) by REJECTION from its own substream `scene:speak2:<i>` until the §2 pin
# (no single word unique; some 2-word phrase unique) AND the kind's pin (the kind's 2-word phrase unique, its other two
# 2-word phrases NOT unique) hold. Test-first: red on scene-s1b1 7706371 (no fresh seeds, no speak2 there).
from __future__ import annotations

import collections
import itertools
import unittest

import numpy as np

from brain.scene import world as W

FRESH = (20261401, 20261402, 20261403)


def _unique(phrase, things, t):
    return W.phrase_true_of(phrase, things[t]) and not any(W.phrase_true_of(phrase, u) for k, u in enumerate(things) if k != t)


class TestFreshSeeds(unittest.TestCase):
    def test_pairs_and_roles(self) -> None:
        self.assertEqual(W.FRESH_TEST_SEEDS, {20261101: 20261401, 20261102: 20261402, 20261103: 20261403})
        self.assertEqual(W.TEST_SETS["s1b1"], W.TEST_SEEDS)                       # S1b-1's own, unchanged
        self.assertEqual(W.TEST_SETS["fresh"], W.FRESH_TEST_SEEDS)
        used = set(W.WORLD_SEEDS) | set(W.TEST_SEEDS.values()) | {W.TOY_SEED, W.STAGE_SEED} | {20261301, 20261302, 20261303}
        self.assertFalse(used & set(W.FRESH_TEST_SEEDS.values()))                 # no second role for one number

    def test_the_old_splits_are_unmoved(self) -> None:
        """S1b-1's generators are untouched: a fresh seed runs them as they are (the byte identity of S1b-1's own caches
        is the gate's step 2)."""
        for maker in (W.test_scene, W.m2b_scene, W.m6_scene, W.m3_scene, W.speak_scene, W.decline_scene):
            self.assertEqual(maker(20261401, 5), maker(20261401, 5))
        self.assertEqual(W.train_scene(20261101, 2699).to_dict()["things"][1]["shape"], "moon")
        self.assertEqual([W.split_size(s) for s in ("test", "m2b", "m6", "m3", "speak", "decline")], [400, 56, 42, 60, 96, 48])


class TestSpeak2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sc = {ts: W.scenes_for("speak2", ts) for ts in FRESH}

    def test_counts_and_kinds(self) -> None:
        self.assertEqual(W.split_size("speak2"), 60)
        self.assertEqual(W.SPEAK2_KINDS, ("CS", "SC", "SS"))
        self.assertEqual([W.speak2_kind(i) for i in (0, 19, 20, 39, 40, 59)], ["CS", "CS", "SC", "SC", "SS", "SS"])
        for ts, sc in self.sc.items():
            self.assertEqual(len(sc), 60)
            self.assertEqual(collections.Counter(W.speak2_kind(s.index) for s in sc), {"CS": 20, "SC": 20, "SS": 20})

    def test_every_item_three_trained_things_no_twins_the_learner_hears_nothing(self) -> None:
        for ts, sc in self.sc.items():
            for s in sc:
                self.assertEqual(len(s.things), 3)
                self.assertEqual(s.words, ())
                self.assertTrue(0 <= s.referent < 3)
                self.assertEqual(len({(u.shape, u.colour, u.size) for u in s.things}), 3)
                for u in s.things:
                    self.assertIn((u.shape, u.colour), W.ALLOWED)
                for a, b in itertools.combinations(s.things, 2):
                    self.assertGreaterEqual(W.box_gap(a, b), W.SEPARATION_PX)

    def test_the_pins_hold_on_every_item(self) -> None:
        """No single word of the target is unique; the kind's 2-word phrase is; the kind's other two 2-word phrases are
        not (so the kind's phrase is the ONLY unique 2-word phrase) — checked here by an independent enumeration."""
        order = {"CS": ("colour", "shape"), "SC": ("size", "colour"), "SS": ("size", "shape")}
        for ts, sc in self.sc.items():
            for s in sc:
                t, th = s.referent, s.things
                words = {"size": th[t].size, "colour": th[t].colour, "shape": th[t].shape}
                for w in words.values():
                    self.assertFalse(_unique([w], th, t), (ts, s.index, w))
                kind = W.speak2_kind(s.index)
                uniq = [pair for pair in itertools.combinations(("size", "colour", "shape"), 2)
                        if _unique([words[x] for x in pair], th, t)]
                self.assertEqual(uniq, [order[kind]], (ts, s.index))
                p = W.speak2_pin(th, t, kind)
                self.assertTrue(p["pass"], p)

    def test_the_kinds_structure(self) -> None:
        """AMENDMENT 1 §2's table: CS — one distractor has the target's colour and size and another shape, the other the
        target's shape and size and another colour; SC — the target's shape and colour at the other size, and the target's
        shape and size in another colour; SS — the target's shape and colour at the other size, and another shape with the
        target's size AND colour."""
        for ts, sc in self.sc.items():
            for s in sc:
                t = s.things[s.referent]
                d = sorted(((u.shape == t.shape, u.colour == t.colour, u.size == t.size)
                            for k, u in enumerate(s.things) if k != s.referent))
                want = {"CS": sorted([(False, True, True), (True, False, True)]),
                        "SC": sorted([(True, True, False), (True, False, True)]),
                        "SS": sorted([(True, True, False), (False, True, True)])}[W.speak2_kind(s.index)]
                self.assertEqual(d, want, (ts, s.index))

    def test_the_pin_catches_planted_offenders(self) -> None:
        T = lambda s, c, z: W.Thing(s, c, z, 0, 0)
        t = T("circle", "red", "big")
        ok = [t, T("circle", "red", "small"), T("triangle", "red", "big")]              # Fable's SS example
        self.assertTrue(W.speak2_pin(ok, 0, "SS")["pass"])
        bad = [t, T("circle", "red", "small"), T("triangle", "green", "big")]           # d2 green: «big red» unique too
        self.assertFalse(W.speak2_pin(bad, 0, "SS")["pass"])
        two = [t, T("circle", "blue", "big")]                                            # 2 things: «red» unique alone
        self.assertFalse(W.speak2_pin(two, 0, "CS")["pass"])
        self.assertFalse(W.speak2_pin(ok, 0, "CS")["pass"])                             # right scene, wrong kind
        cs = [t, T("triangle", "red", "big"), T("circle", "green", "big")]              # Fable's CS example
        self.assertTrue(W.speak2_pin(cs, 0, "CS")["pass"])
        sc = [t, T("circle", "red", "small"), T("circle", "green", "big")]              # Fable's SC example
        self.assertTrue(W.speak2_pin(sc, 0, "SC")["pass"])

    def test_drawn_whole_from_its_own_substream(self) -> None:
        a, b = W.speak2_scene(20261401, 7), W.speak2_scene(20261401, 7)
        self.assertEqual(a, b)
        ra, _ = W.render_scene(a)
        rb, _ = W.render_scene(b)
        self.assertTrue(np.array_equal(ra, rb))
        self.assertNotEqual(W.speak2_scene(20261401, 7).to_dict()["things"], W.speak2_scene(20261402, 7).to_dict()["things"])
        self.assertEqual(a.item_id, "speak2:20261401:00007")
        with self.assertRaises(W.WorldError):
            W.speak2_scene(20261401, 60)

    def test_every_trained_target_admits_every_kind(self) -> None:
        """Fable's check, by enumeration: for every trained (shape, colour, size) and every kind, a pair of trained
        distractors meeting the kind's pin exists — the rejection can always end."""
        T = lambda s, c, z: W.Thing(s, c, z, 0, 0)
        things = [(s, c, z) for s, c in W.ALLOWED for z in W.SIZE_NAMES]
        for tgt in things:
            for kind in W.SPEAK2_KINDS:
                self.assertTrue(any(W.speak2_pin([T(*tgt), T(*a), T(*b)], 0, kind)["pass"]
                                    for a, b in itertools.combinations(things, 2)), (tgt, kind))


if __name__ == "__main__":
    unittest.main()
