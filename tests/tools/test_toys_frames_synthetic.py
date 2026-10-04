"""Tests for TOY C's structure-free synthetic streams — the architect's 17:1x check («does NULL-1's q95 let a noise frame read LOUD by the denominator effect alone?»), settled on SYNTHETIC data before any
real SHUFFLE is read. Written FIRST, STAGE 3f (red, then green).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:49 +0400 — STAGE 3f. S1 = G6's sampler at G4's size with its words shuffled the law's way; S2 = a stream in ALPHA4's REGIME built from numbers the law's §0
# already prints (the words-a-moment histogram and the words each source delivered), words i.i.d. from a mixture with a Zipf shelf tail: structure-free by construction, never a draw from the real stream.
"""
from __future__ import annotations

import unittest
from collections import Counter

import numpy as np

from tools.toys.frames import scene as SC
from tools.toys.frames import streams as ST
from tools.toys.frames import synthetic as SY


class TestStructureFreeScene(unittest.TestCase):
    def test_it_is_the_generators_words_shuffled_the_laws_way(self):
        tr, he = SY.structure_free_scene(3000, 1)
        self.assertEqual((len(tr), len(he)), (1800, 1200))
        ms = SC.sample_moments(3000, np.random.default_rng([20261103, 8, 1]))
        a, b = ST.split(ms)
        self.assertEqual(sorted(w for m in tr for w in m.words), sorted(w for m in a for w in m.words))      # each part keeps its own word multiset
        self.assertEqual(sorted(w for m in he for w in m.words), sorted(w for m in b for w in m.words))
        self.assertEqual([len(m.words) for m in tr], [len(m.words) for m in a])                              # the moments' sizes kept
        self.assertNotEqual([m.words for m in tr], [m.words for m in a])                                      # and it really shuffled

    def test_it_is_deterministic(self):
        a = SY.structure_free_scene(600, 2)
        b = SY.structure_free_scene(600, 2)
        self.assertEqual([m.words for m in a[0]], [m.words for m in b[0]])
        self.assertNotEqual([m.words for m in a[0]], [m.words for m in SY.structure_free_scene(600, 3)[0]])


class TestStructureFreeAlphaRegime(unittest.TestCase):
    def test_the_sizes_and_the_source_mix_follow_the_laws_section_0_numbers(self):
        tr, he = SY.structure_free_alpha(20000, 1)
        self.assertEqual((len(tr), len(he)), (12000, 8000))
        allm = tr + he
        sizes = Counter(len(m.words) for m in allm)
        n = len(allm)
        self.assertAlmostEqual(sizes[1] / n, 73088 / 84275, delta=0.01)                                       # §0: 73,088 of 84,275 moments hold one word
        self.assertAlmostEqual(sizes[4] / n, 8179 / 84275, delta=0.01)
        self.assertAlmostEqual(sum(len(m.words) for m in allm) / n, 112489 / 84275, delta=0.03)               # 1.3348 words a moment
        words = Counter(w for m in allm for w in m.words)
        total = sum(words.values())
        maker = sum(c for w, c in words.items() if w.startswith("mk"))
        self.assertAlmostEqual(maker / total, 35294 / 112489, delta=0.01)                                     # the maker's share of the words heard
        shelf_words = {w for w in words if w.startswith("sh")}
        self.assertGreater(len(shelf_words), 1500)                                                            # a heavy tail of shelf words, as the real shelf's 3,290 distinct
        shelf_total = sum(c for w, c in words.items() if w.startswith("sh"))
        h = sum(1.0 / i for i in range(1, 3291))                                                              # Zipf, exponent 1, over 3,290 words: the top word has the share 1 / H(3290) = 0.1153
        self.assertAlmostEqual(words["sh0000"] / shelf_total, 1.0 / h, delta=0.015)
        self.assertGreater(words["sh0000"], 20 * words["sh0100"])                                             # a head, not a flat vocabulary (Zipf: 101 times; a flat one would read about 1)

    def test_the_words_are_independent_of_their_neighbours(self):
        """structure-free by construction: the most frequent adjacent pair's count sits within a chance band of the independence expectation (a plant of one hot pair must leave it)."""
        tr, _he = SY.structure_free_alpha(20000, 1)
        pairs = Counter((m.words[i], m.words[i + 1]) for m in tr for i in range(len(m.words) - 1))
        words = Counter(w for m in tr for w in m.words)
        total_pos = sum(max(0, len(m.words) - 1) for m in tr)
        total_w = sum(words.values())
        worst = max(pairs.items(), key=lambda kv: kv[1] / max(1e-9, total_pos * (words[kv[0][0]] / total_w) * (words[kv[0][1]] / total_w)) if kv[1] >= 5 else 0.0)
        (a, b), c = worst
        expected = total_pos * (words[a] / total_w) * (words[b] / total_w)
        self.assertLess(c, expected * 4 + 12)                                                                 # chance (Poisson) wiggle only: no hot pair
        planted = dict(pairs)
        planted[("mk00", "mk01")] = planted.get(("mk00", "mk01"), 0) + 200
        c2 = planted[("mk00", "mk01")]
        e2 = total_pos * (words["mk00"] / total_w) * (words["mk01"] / total_w)
        self.assertGreater(c2, e2 * 4 + 12)                                                                   # the plant of a hot pair breaks the band: the check can see structure

    def test_it_is_deterministic(self):
        a = SY.structure_free_alpha(2000, 1)
        b = SY.structure_free_alpha(2000, 1)
        self.assertEqual([m.words for m in a[0]], [m.words for m in b[0]])
        self.assertNotEqual([m.words for m in a[0]], [m.words for m in SY.structure_free_alpha(2000, 2)[0]])


if __name__ == "__main__":
    unittest.main()
