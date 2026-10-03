"""Tests for TOY C's two nulls (docs/research/toys/PREREG-TOY-FRAMES.md §3 NULL-1 and NULL-2, with AMENDMENT-1 §4 (a)-(b)): NULL-1, the DEALT set (same size, same frequency profile, chance
pairing); NULL-2, the ABLATED SELECTION CRITERION (a random ADJACENT pair of the same adjacent count). Written FIRST, STAGE 3b (red, then green, a log each).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:15 +0400 — STAGE 3b. Every bin below is worked by hand: bin(count) = floor(2 log2 count) (width 0.5 in log2): 1 -> 0, 2 -> 2, 3 -> 3, 4 and 5 -> 4,
# 6 and 7 -> 5, 8, 9, 10 -> 6, 70 -> 12, 100 -> 13 (2 log2 70 = 12.26, 2 log2 100 = 13.29, 2 log2 8 = 6, 2 log2 10 = 6.64).
"""
from __future__ import annotations

import math
import unittest
from collections import Counter
from typing import List

import numpy as np

from tools.toys.frames import compress as CO
from tools.toys.frames import null as NL
from tools.toys.frames import streams as ST


class TestBins(unittest.TestCase):
    def test_log2_bin_of_a_count_by_hand(self):
        want = {1: 0, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 5, 8: 6, 9: 6, 10: 6, 11: 6, 12: 7, 16: 8, 70: 12, 100: 13}
        for c, b in want.items():
            self.assertEqual(NL.log2_bin(c), b, c)

    def test_a_non_positive_count_is_refused(self):
        with self.assertRaises(ValueError):
            NL.log2_bin(0)


# ====================================================================================================================== NULL-2: the adjacent-bigram pool
def bigram_stream() -> List[List[str]]:
    """Two-word moments with HAND-SET adjacent counts: (x1,y1) 8, (x2,y2) 9, (x3,y3) 10, (x7,y7) 8, (x8,y8) 9 -> bin 6; (x4,y4) 2, (x5,y5) 2 -> bin 2; (x6,y6) 3 -> bin 3; four unique bigrams
    (u1,v1)..(u4,v4) -> bin 0. z1 and z2 are train words that are never adjacent (one-word moments)."""
    ms: List[List[str]] = []
    for name, c in (("1", 8), ("2", 9), ("3", 10), ("7", 8), ("8", 9), ("4", 2), ("5", 2), ("6", 3)):
        ms += [[f"x{name}", f"y{name}"]] * c
    ms += [[f"u{i}", f"v{i}"] for i in range(1, 5)]
    ms += [["z1"], ["z2"]]
    return ms


def held_for(ms) -> List[List[str]]:
    return [[f"x{i}", f"y{i}"] for i in (1, 3, 4, 6, 8)] * 4 + [["u1", "v1"], ["z1"], ["q"]]


class TestNull2(unittest.TestCase):
    def setUp(self):
        self.train = bigram_stream()
        self.sc = CO.Scorer(self.train, held_for(self.train))

    def test_the_pool_is_the_distinct_adjacent_train_bigrams_by_their_own_count_bin(self):
        pools = NL.bigram_bins(self.sc)
        self.assertEqual(sorted(pools[6]), [("x1", "y1"), ("x2", "y2"), ("x3", "y3"), ("x7", "y7"), ("x8", "y8")])
        self.assertEqual(sorted(pools[2]), [("x4", "y4"), ("x5", "y5")])
        self.assertEqual(sorted(pools[3]), [("x6", "y6")])
        self.assertEqual(sorted(pools[0]), [(f"u{i}", f"v{i}") for i in range(1, 5)])
        self.assertEqual(sorted(pools), [0, 2, 3, 6])
        self.assertEqual(sum(len(v) for v in pools.values()), len(self.sc.train_bigrams()))      # every distinct adjacent pair once

    def test_a_replacement_comes_from_the_same_bin_not_the_frame_itself_and_every_member_appears(self):
        r = NL.null2(self.sc, {("x1", "y1")}, rule_tag=3, seed=0, draws=60, keep_pairs=True)
        got = {p[0] for p in r.pairs}
        self.assertEqual(got, {("x2", "y2"), ("x3", "y3"), ("x7", "y7"), ("x8", "y8")})          # bin 6 minus the frame itself; all four seen in 60 draws
        self.assertEqual(r.fallbacks, 0)
        self.assertEqual((r.draws, r.k, len(r.values)), (60, 1, 60))

    def test_a_bin_with_one_admissible_member_gives_it_every_time(self):
        r = NL.null2(self.sc, {("x4", "y4")}, rule_tag=3, seed=0, draws=20, keep_pairs=True)
        self.assertEqual({p[0] for p in r.pairs}, {("x5", "y5")})                                # bin 2 = {(x4,y4), (x5,y5)}
        self.assertEqual(r.fallbacks, 0)

    def test_a_bin_with_no_admissible_member_falls_back_to_the_nearest_non_empty_bin_and_is_counted(self):
        """F = both members of bin 2. Frame 1 ((x4,y4), the smaller name first): bin 2 has nothing admissible -> distance 1: bin 1 is empty, bin 3 = {(x6,y6)} -> that one. Frame 2 ((x5,y5)): bin 2
        nothing; distance 1: bin 3's only member is already USED, bin 1 empty; distance 2: bin 0 (four bigrams), bin 4 empty -> one of bin 0. So 2 fallbacks a draw."""
        F = {("x4", "y4"), ("x5", "y5")}
        r = NL.null2(self.sc, F, rule_tag=3, seed=0, draws=30, keep_pairs=True)
        self.assertEqual(r.fallbacks, 2 * 30)
        for p in r.pairs:
            self.assertEqual(p[0], ("x6", "y6"))
            self.assertIn(p[1], {(f"u{i}", f"v{i}") for i in range(1, 5)})

    def test_a_frame_never_adjacent_is_matched_into_the_lowest_bin(self):
        r = NL.null2(self.sc, {("z1", "z2")}, rule_tag=3, seed=0, draws=40, keep_pairs=True)    # train_adjacent((z1, z2)) = 0 -> counted as 1 -> bin 0
        self.assertTrue({p[0] for p in r.pairs} <= {(f"u{i}", f"v{i}") for i in range(1, 5)})
        self.assertEqual(r.fallbacks, 0)
        self.assertEqual(len({p[0] for p in r.pairs}), 4)

    def test_replacements_are_distinct_never_in_F_and_the_sets_have_the_frames_size(self):
        F = {("x1", "y1"), ("x2", "y2")}
        r = NL.null2(self.sc, F, rule_tag=3, seed=0, draws=50, keep_pairs=True)
        for p in r.pairs:
            self.assertEqual(len(set(p)), 2)                                                      # distinct within a draw
            self.assertFalse(set(p) & F)
        # the stat is the compressor's own G of the dealt set
        for p, v in zip(r.pairs, r.values):
            self.assertAlmostEqual(v, self.sc.gain(set(p)).G, places=9)

    def test_it_is_deterministic_in_its_key_and_the_key_matters(self):
        F = {("x1", "y1"), ("x2", "y2")}
        a = NL.null2(self.sc, F, rule_tag=3, seed=0, draws=40)
        b = NL.null2(self.sc, F, rule_tag=3, seed=0, draws=40)
        self.assertEqual(a.values, b.values)
        self.assertNotEqual(a.values, NL.null2(self.sc, F, rule_tag=3, seed=1, draws=40).values)
        self.assertNotEqual(a.values, NL.null2(self.sc, F, rule_tag=4, seed=0, draws=40).values)

    def test_a_frame_with_no_other_pair_anywhere_is_an_error_not_a_silent_self_draw(self):
        sc = CO.Scorer([["a", "b"]] * 3, [["a", "b"]])
        with self.assertRaises(NL.NullError):
            NL.null2(sc, {("a", "b")}, rule_tag=3, seed=0, draws=3)


# ====================================================================================================================== NULL-1: the dealt set
def word_stream() -> List[List[str]]:
    """One-word moments with HAND-SET counts: g1 8, g2 9, g3 10, g4 8 (bin 6); h1 6, h2 7 (bin 5); a 100 (bin 13); c 70 (bin 12); b 3 (bin 3); d 2 (bin 2); e 4 (bin 4)."""
    ms: List[List[str]] = []
    for w, c in (("g1", 8), ("g2", 9), ("g3", 10), ("g4", 8), ("h1", 6), ("h2", 7), ("a", 100), ("c", 70), ("b", 3), ("d", 2), ("e", 4)):
        ms += [[w]] * c
    return ms


class TestNull1(unittest.TestCase):
    def setUp(self):
        self.train = word_stream()
        self.sc = CO.Scorer(self.train, [["g1"], ["a"], ["q"]])
        self.counts = Counter(w for m in self.train for w in m)

    def test_the_word_bins_by_hand(self):
        bins = NL.word_bins(self.sc)
        self.assertEqual(sorted(bins[6]), ["g1", "g2", "g3", "g4"])
        self.assertEqual(sorted(bins[5]), ["h1", "h2"])
        self.assertEqual(bins[13], ["a"])
        self.assertEqual(bins[12], ["c"])
        self.assertEqual(bins[3], ["b"])
        self.assertEqual(bins[2], ["d"])
        self.assertEqual(bins[4], ["e"])

    def test_the_profile_is_kept_the_pair_is_new_and_every_admissible_pair_appears(self):
        """F = {(g1, g2)}: both words in bin 6 = {g1..g4}; the admissible pairs are the 16 pairs of bin 6 minus (g1, g2) itself = 15."""
        r = NL.null1(self.sc, {("g1", "g2")}, rule_tag=3, seed=0, draws=300, keep_pairs=True)
        self.assertEqual(r.fallbacks, 0)
        seen = {p[0] for p in r.pairs}
        self.assertEqual(len(seen), 15)
        self.assertNotIn(("g1", "g2"), seen)
        for a, b in seen:
            self.assertEqual(NL.log2_bin(self.counts[a]), 6)
            self.assertEqual(NL.log2_bin(self.counts[b]), 6)

    def test_sets_have_the_frames_size_and_never_meet_F(self):
        F = {("g1", "g2"), ("g2", "g1"), ("g3", "g3")}
        r = NL.null1(self.sc, F, rule_tag=3, seed=0, draws=100, keep_pairs=True)
        for p in r.pairs:
            self.assertEqual(len(set(p)), 3)
            self.assertFalse(set(p) & F)
        for p, v in zip(r.pairs, r.values):
            self.assertAlmostEqual(v, self.sc.gain(set(p)).G, places=9)

    def test_a_pair_of_unique_bins_falls_back_to_wider_bins_and_is_counted(self):
        """F = {(a, b)}: a is alone in bin 13 and b alone in bin 3, so the only pair of the two bins is the frame itself: no admissible pair. Distance 1 widens BOTH sides:
        bins 12..14 = {c, a} and bins 2..4 = {d, b, e}: 6 pairs minus (a, b) = 5 admissible. One fallback a draw."""
        r = NL.null1(self.sc, {("a", "b")}, rule_tag=3, seed=0, draws=200, keep_pairs=True)
        self.assertEqual(r.fallbacks, 200)
        seen = {p[0] for p in r.pairs}
        self.assertEqual(seen, {("a", "d"), ("a", "e"), ("c", "d"), ("c", "b"), ("c", "e")})

    def test_it_is_deterministic_in_its_key_and_the_key_matters(self):
        """compared on the dealt PAIRS: in this one-word-moment fixture no pair can ever fire, so EVERY draw's G is the same constant (-L and the K effect) — the sd ≈ 0 that the architect's
        17:1x RAISE names (a NULL-1 draw merges nothing in train); the values themselves cannot show the key."""
        F = {("g1", "g2"), ("h1", "h2")}
        a = NL.null1(self.sc, F, rule_tag=3, seed=0, draws=40, keep_pairs=True)
        self.assertEqual(a.pairs, NL.null1(self.sc, F, rule_tag=3, seed=0, draws=40, keep_pairs=True).pairs)
        self.assertNotEqual(a.pairs, NL.null1(self.sc, F, rule_tag=3, seed=1, draws=40, keep_pairs=True).pairs)
        self.assertNotEqual(a.pairs, NL.null1(self.sc, F, rule_tag=2, seed=0, draws=40, keep_pairs=True).pairs)
        self.assertEqual(len(set(a.values)), 1)                                                   # the architect's point, pinned: a null that never fires has one value
        self.assertEqual(a.sd, 0.0)

    def test_an_empty_frame_set_has_an_empty_null_of_zeros(self):
        r = NL.null1(self.sc, set(), rule_tag=3, seed=0, draws=7, keep_pairs=True)
        self.assertEqual((r.k, r.draws, r.values, r.fallbacks, r.pairs), (0, 7, (0.0,) * 7, 0, ((),) * 7))
        r2 = NL.null2(CO.Scorer(bigram_stream(), held_for(None)), set(), rule_tag=3, seed=0, draws=7)
        self.assertEqual((r2.k, r2.values), (0, (0.0,) * 7))


# ====================================================================================================================== the summary
class TestSummary(unittest.TestCase):
    def test_mean_sd_q95_and_the_reading_of_a_value(self):
        sc = CO.Scorer(word_stream(), [["g1"], ["a"]])
        r = NL.null1(sc, {("g1", "g2")}, rule_tag=3, seed=0, draws=100)
        v = np.array(r.values)
        self.assertAlmostEqual(r.mean, float(v.mean()), places=12)
        self.assertAlmostEqual(r.sd, float(v.std(ddof=1)), places=12)
        self.assertAlmostEqual(r.q95, float(np.percentile(v, 95)), places=12)
        rd = r.read(r.q95 + 1.0)
        self.assertTrue(rd["beats_q95"])
        self.assertAlmostEqual(rd["z"], (r.q95 + 1.0 - r.mean) / r.sd, places=12)
        self.assertFalse(r.read(r.q95 - 1.0)["beats_q95"])

    def test_a_zero_sd_has_no_z(self):
        r = NL.NullResult(kind="NULL-1", draws=3, k=1, values=(1.0, 1.0, 1.0), fallbacks=0, pairs=None)
        self.assertIsNone(r.read(2.0)["z"])
        self.assertTrue(r.read(2.0)["beats_q95"])


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:39 +0400 — added after a MUTATION SWEEP of null.py (five single-line mutations): two survived and named two holes in these tests — the summary test used a
# CONSTANT-valued null (sd = 0 with ddof 0 or 1), and every fixture pool held <= 64 members, so the rejection-sampling branch (the one the real run uses for the count-1 bin of thousands of bigrams) was never run.
class TestSummaryByHand(unittest.TestCase):
    def test_mean_sd_q95_z_of_five_values_worked_on_paper(self):
        """values 1, 2, 3, 4, 10: mean 4; squared deviations 9 + 4 + 1 + 0 + 36 = 50, sample sd = sqrt(50 / 4) = 3.5355339; the 95th percentile (linear) sits at position 0.95 * 4 = 3.8
        of the sorted values, 4 + 0.8 * (10 - 4) = 8.8; the z of 9.0 is (9 - 4) / 3.5355339 = 1.4142136."""
        r = NL.NullResult(kind="NULL-1", draws=5, k=1, values=(1.0, 2.0, 3.0, 4.0, 10.0), fallbacks=0, pairs=None)
        self.assertAlmostEqual(r.mean, 4.0, places=12)
        self.assertAlmostEqual(r.sd, math.sqrt(12.5), places=12)
        self.assertAlmostEqual(r.q95, 8.8, places=12)
        rd = r.read(9.0)
        self.assertAlmostEqual(rd["z"], 5.0 / math.sqrt(12.5), places=12)
        self.assertTrue(rd["beats_q95"])
        self.assertFalse(r.read(r.q95)["beats_q95"])                                               # strictly above, not equal (to ITS OWN q95: numpy's 8.8 is 8.799999999999999)
        self.assertFalse(r.read(8.7)["beats_q95"])


def large_bigram_stream() -> List[List[str]]:
    """300 UNIQUE two-word moments a000 b000 ... a299 b299 (adjacent count 1: bin 0, a pool far above the enumerate-or-reject threshold), (x, y) 8 times and (r, s) 9 times (bin 6, two members)."""
    return [[f"a{i:03d}", f"b{i:03d}"] for i in range(300)] + [["x", "y"]] * 8 + [["r", "s"]] * 9


class TestNull2LargePools(unittest.TestCase):
    def setUp(self):
        self.train = large_bigram_stream()
        self.sc = CO.Scorer(self.train, [["a000", "b000"], ["x", "y"], ["q"]])
        self.bin0 = {(f"a{i:03d}", f"b{i:03d}") for i in range(300)}

    def test_a_large_bin_is_sampled_without_fallback_never_returns_F_and_covers_the_pool(self):
        F = {("a000", "b000")}
        r = NL.null2(self.sc, F, rule_tag=3, seed=0, draws=2000, keep_pairs=True)
        got = [p[0] for p in r.pairs]
        self.assertEqual(r.fallbacks, 0)                                                           # a d = 0 pick is not a fallback, whichever branch sampled it
        self.assertTrue(set(got) <= self.bin0 - F)
        self.assertGreaterEqual(len(set(got)), 290)                                                # 299 admissible, 2000 uniform draws: expected unseen ≈ 0.4

    def test_a_large_exclusion_still_deals_exactly_the_complement(self):
        """F = 150 of the 300 unique bigrams; the dealt set must be the OTHER 150, whatever the order: late picks have 1-in-150 .. 1-in-300 chances per rejection draw, so the sampler's
        enumeration after 1000 rejections is exercised too."""
        F = {(f"a{i:03d}", f"b{i:03d}") for i in range(150)}
        r = NL.null2(self.sc, F, rule_tag=3, seed=0, draws=12, keep_pairs=True)
        want = self.bin0 - F
        for p in r.pairs:
            self.assertEqual(set(p), want)
            self.assertEqual(len(p), 150)
        self.assertEqual(r.fallbacks, 0)

    def test_a_far_fallback_into_a_large_ring_is_counted(self):
        """F = both members of bin 6 ((r, s) 9 times and (x, y) 8 times): nothing admissible in bin 6; the nearest non-empty bins are bin 0 (distance 6) with 300 members: the rejection
        branch at d > 0. Two fallbacks a draw, both replacements from bin 0."""
        F = {("x", "y"), ("r", "s")}
        r = NL.null2(self.sc, F, rule_tag=3, seed=0, draws=25, keep_pairs=True)
        self.assertEqual(r.fallbacks, 2 * 25)
        for p in r.pairs:
            self.assertTrue(set(p) <= self.bin0)
            self.assertEqual(len(set(p)), 2)


class TestNull1LargePools(unittest.TestCase):
    def test_a_large_pair_space_is_sampled_uniformly_over_the_admissible_pairs(self):
        """12 words with counts 8, 9, 10 (all bin 6): 144 pairs, 143 admissible for F = {(w00, w01)}: more than the enumerate threshold, so the rejection branch deals them."""
        ms: List[List[str]] = []
        for i in range(12):
            ms += [[f"w{i:02d}"]] * (8 + i // 4)
        sc = CO.Scorer(ms, [["w00"], ["q"]])
        r = NL.null1(sc, {("w00", "w01")}, rule_tag=3, seed=0, draws=3000, keep_pairs=True)
        seen = {p[0] for p in r.pairs}
        self.assertEqual(r.fallbacks, 0)
        self.assertNotIn(("w00", "w01"), seen)
        self.assertEqual(len(seen), 143)
        for a, b in seen:
            self.assertIn(a, {f"w{i:02d}" for i in range(12)})
            self.assertIn(b, {f"w{i:02d}" for i in range(12)})


# ====================================================================================================================== a planted frame can beat both nulls
def multiword_stream(seed: int, n: int = 600, vocab: int = 80, plant_every: int = 10):
    rng = np.random.default_rng(seed)
    p = 1.0 / np.arange(1, vocab + 1)
    p /= p.sum()
    ms = []
    for i in range(n):
        k = int(rng.integers(1, 4))
        ms.append(ST.Moment("s", f"m{i}", tuple(f"w{int(j):02d}" for j in rng.choice(vocab, size=k, p=p)), tuple(float(i * 10 + t) for t in range(k))))
    return ST.with_plant(ms, plant_every)


class TestAPlantedFrameCanBeatTheNulls(unittest.TestCase):
    def test_the_planted_frame_beats_the_q95_of_both_nulls_and_the_fallbacks_are_counted(self):
        planted = multiword_stream(1)
        tr, he = ST.split(planted)
        sc = CO.Scorer([m.words for m in tr], [m.words for m in he])
        F = {ST.PLANT}
        g = sc.gain(F).G
        self.assertGreater(g, 0.0)
        n1 = NL.null1(sc, F, rule_tag=5, seed=0, draws=100)
        n2 = NL.null2(sc, F, rule_tag=5, seed=0, draws=100)
        self.assertTrue(n1.read(g)["beats_q95"])
        self.assertTrue(n2.read(g)["beats_q95"])
        self.assertGreater(sc.train_adjacent(ST.PLANT), 30)                                       # a frequent plant: its count bin holds no real bigram, so NULL-2 fell back (counted)
        self.assertGreater(n2.fallbacks, 0)


if __name__ == "__main__":
    unittest.main()
