"""Tests for TOY C's SCENE generator constants, the ceiling gate and G6 (docs/research/toys/PREREG-TOY-FRAMES.md §3 THE CEILING, §7 G1 (χ²) and G6). Written FIRST, STAGE 3c (red, then green).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:42 +0400 — STAGE 3c. The generator (brain/scene/world.py): a template uniform over T1 «shape», T2 «colour shape», T3 «size shape», T4 «size colour shape»; the
# referent's (shape, colour) uniform over the 24 ALLOWED pairs (shapes circle 4, square 3, triangle 4, cross 4, ring 5, star 4 of 24; the six held-out pairs: circle-blue, cross-yellow, square-red,
# square-white, star-red, triangle-yellow); its size uniform over big / small. Every probability below is worked on paper from those counts, never read back from the code under test.
"""
from __future__ import annotations

import math
import unittest

import numpy as np

from tools.toys.frames import compress as CO
from tools.toys.frames import scene as SC
from tools.toys.frames import streams as ST

N_S = {"circle": 4, "square": 3, "triangle": 4, "cross": 4, "ring": 5, "star": 4}       # allowed (shape, colour) pairs a shape has: 24 in all


class TestPGen(unittest.TestCase):
    def test_probabilities_by_hand(self):
        want = {
            ("circle",): 1 / 24,                  # 1/4 * 4/24
            ("square",): 1 / 32,                  # 1/4 * 3/24
            ("ring",): 5 / 96,                    # 1/4 * 5/24
            ("red", "circle"): 1 / 96,            # 1/4 * [allowed] / 24
            ("big", "circle"): 1 / 48,            # 1/4 * 1/2 * 4/24
            ("small", "square"): 1 / 64,          # 1/4 * 1/2 * 3/24
            ("big", "red", "circle"): 1 / 192,    # 1/4 * 1/2 * [allowed] / 24
            ("small", "green", "star"): 1 / 192,
        }
        for words, p in want.items():
            self.assertAlmostEqual(SC.p_gen(words), p, places=14, msg=words)

    def test_an_utterance_the_four_templates_cannot_produce_is_a_stop(self):
        for words in (("blue", "circle"),               # a held-out pair: the generator never draws it
                      ("dax",), ("big", "big", "circle"), (), ("red", "blue", "circle", "big"), ("red", "big"), ("circle", "red"), ("big", "circle", "red")):
            with self.assertRaises(SC.CeilingStop, msg=words):
                SC.p_gen(words)

    def test_the_support_is_ninety_utterances_and_sums_to_one(self):
        sup = SC.support()
        self.assertEqual(len(sup), 6 + 24 + 12 + 48)                                              # T1, T2, T3, T4
        self.assertAlmostEqual(sum(sup.values()), 1.0, places=12)
        for u in sup:
            self.assertAlmostEqual(sup[u], SC.p_gen(u), places=15)

    def test_entropy_and_the_length_split(self):
        hs = -sum((n / 24) * math.log2(n / 24) for n in N_S.values())                              # H(shape) = 2.5698
        hand = 2 + 0.25 * hs + 0.25 * math.log2(24) + 0.25 * (1 + hs) + 0.25 * (1 + math.log2(24))   # the law's closed form
        self.assertAlmostEqual(hs, 2.5698, places=4)
        self.assertAlmostEqual(SC.entropy(), hand, places=12)
        self.assertAlmostEqual(SC.entropy(), 6.0774, places=4)
        self.assertAlmostEqual(SC.h_length(), 1.5, places=12)                                      # lengths 1, 2, 3 with probabilities 1/4, 1/2, 1/4
        self.assertAlmostEqual(SC.h_given_length(), 4.5774, places=4)
        self.assertAlmostEqual(SC.h_given_length(), SC.entropy() - SC.h_length(), places=12)

    def test_g_max_by_hand(self):
        held = [("circle",), ("red", "circle")]
        s = math.log2(24) + math.log2(96)                                                          # -log2(1/24) - log2(1/96)
        self.assertAlmostEqual(SC.g_max(held, 100.0), 100.0 - s, places=12)

    def test_the_ceiling_check_is_strictly_above_the_slack(self):
        self.assertFalse(SC.ceiling_violation(120.0, 100.0))                                       # exactly G_max + 20: not a violation
        self.assertTrue(SC.ceiling_violation(120.0001, 100.0))
        self.assertFalse(SC.ceiling_violation(-5000.0, 100.0))

    def test_the_oracle_is_the_allowed_pairs_as_colour_then_shape(self):
        o = SC.oracle_frames()
        self.assertEqual(len(o), 24)
        self.assertIn(("red", "circle"), o)
        self.assertNotIn(("blue", "circle"), o)                                                    # held out
        self.assertNotIn(("circle", "red"), o)                                                     # the order of T2 / T4


class TestSampler(unittest.TestCase):
    def test_the_sampler_draws_the_generators_utterances_and_nothing_else(self):
        ms = SC.sample_moments(3000, np.random.default_rng([20261103, 8, 1]))
        self.assertEqual(len(ms), 3000)
        self.assertTrue(all(m.source == "scene" for m in ms))
        for m in ms:
            SC.p_gen(m.words)                                                                      # raises for anything the templates cannot produce
        flat = ST.flat_words(ms)
        self.assertEqual(len(flat), sum(len(m.words) for m in ms))
        seqs = [s for m in ms for s in m.seqs]
        self.assertEqual(seqs, sorted(seqs))

    def test_the_sampler_is_deterministic_in_its_generator(self):
        a = SC.sample_moments(200, np.random.default_rng([20261103, 8, 3]))
        b = SC.sample_moments(200, np.random.default_rng([20261103, 8, 3]))
        c = SC.sample_moments(200, np.random.default_rng([20261103, 8, 4]))
        self.assertEqual([m.words for m in a], [m.words for m in b])
        self.assertNotEqual([m.words for m in a], [m.words for m in c])


class TestChi2(unittest.TestCase):
    def test_a_sample_from_the_generator_fits_its_own_constants(self):
        ms = SC.sample_moments(10000, np.random.default_rng([20261103, 8, 2]))
        r = SC.chi2_checks(ms)
        self.assertEqual(r["n"], 10000)
        self.assertEqual(r["dax_excluded"], 0)
        for k in ("length", "shape", "colour", "size", "pairs"):
            self.assertGreater(r[k]["p"], 0.001, k)
        self.assertEqual(r["heldout_pairs_seen"], 0)
        self.assertTrue(r["gated"])

    def test_the_dax_moment_is_excluded_and_named(self):
        ms = SC.sample_moments(2000, np.random.default_rng([20261103, 8, 2]))
        ms = ms[:700] + [ST.Moment("scene", "dax", ("dax",), (99999.0,))] + ms[700:]
        r = SC.chi2_checks(ms)
        self.assertEqual((r["n"], r["dax_excluded"]), (2000, 1))

    def test_a_skewed_stream_is_seen(self):
        """the plant: a stream that is ALL two-word utterances (the law's 1/4, 1/2, 1/4 by length is violated) must read p < 0.001 on length and the gate must not be 'gated'."""
        ms = SC.sample_moments(6000, np.random.default_rng([20261103, 8, 5]))
        skew = [m for m in ms if len(m.words) == 2]
        self.assertNotEqual(len(skew), len(ms))                                                    # the plant changed the stream
        r = SC.chi2_checks(skew)
        self.assertLess(r["length"]["p"], 0.001)
        self.assertFalse(r["gated"])

    def test_a_held_out_pair_in_the_stream_is_counted(self):
        ms = SC.sample_moments(500, np.random.default_rng([20261103, 8, 6]))
        bad = ms + [ST.Moment("scene", "ho", ("blue", "circle"), (99999.0, 99999.5))]
        r = SC.chi2_checks(bad)
        self.assertEqual(r["heldout_pairs_seen"], 1)
        self.assertFalse(r["gated"])


class TestG6(unittest.TestCase):
    def test_the_oracle_stays_under_the_ceiling_on_synthetic_replicates_and_the_margin_is_printed(self):
        rows = [SC.g6_replicate(k, n_moments=4000) for k in (1, 2, 3)]
        for r in rows:
            self.assertFalse(r["violation"], r)
            self.assertGreater(r["margin"], 0.0)                                                    # G_max − G(F_oracle): the gate is loose by whole bits an utterance
            self.assertEqual(r["margin"], r["G_max"] - r["G_oracle"])                               # G(F_oracle)'s own sign is a READING (the law's P-C3 expects it thin), never asserted here
        self.assertEqual([r["k"] for r in rows], [1, 2, 3])

    def test_a_planted_cheat_is_caught_and_changed_the_bytes(self):
        """bits(held-out | F) replaced by 0.9 x the generator's own code length: it must exceed G_max + 20 (CAUGHT), and the plant must differ from the honest reading."""
        c = SC.g6_cheat(1, n_moments=4000)
        self.assertNotEqual(c["bitsF_honest"], c["bitsF_cheat"])
        self.assertTrue(c["caught"])
        self.assertGreater(c["G_cheat"], c["G_max"] + 20.0)
        self.assertFalse(SC.ceiling_violation(c["G_honest"], c["G_max"]))

    def test_the_exact_checks_of_the_generator(self):
        e = SC.g6_exact_checks()
        self.assertLess(abs(e["sum_p"] - 1.0), 1e-12)
        self.assertAlmostEqual(e["entropy"], 6.0774, places=4)
        self.assertAlmostEqual(e["h_length"], 1.5, places=12)
        self.assertAlmostEqual(e["h_given_length"], 4.5774, places=4)
        self.assertEqual(e["support_size"], 90)


if __name__ == "__main__":
    unittest.main()
