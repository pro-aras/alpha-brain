"""test_thresh_own_band.py — L-6/THRESH (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4 L-6;
docs/briefs/LIFE-A-ANSWER-SELF.md #1): `THRESH cell own band history 30` — each SIGHT cell keeps a ring
of the last <history> cosines of the glances it answered CORRECTLY (inside Organism.moment, the winning
sight cell's `_answer_of` equals the word cell of the moment's word — the plain resonance road, no new
learning, ADAPTS). State: Area.own_band (float32, nmax x history) + Area.own_band_n (int64, nmax),
inside the live-block state_hash ONLY once at least one entry has been pushed (own_band_n.any()) — an
untouched ring at all zero is byte-indistinguishable from "the gene was never declared", which is what
lets an old (pre-THRESH) snapshot load under a THRESH genome without a digest mismatch (the two "old
snapshot" tests below).

edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:47 +0400 — #1 (docs/briefs/LIFE-A-ANSWER-SELF.md).
"""
from __future__ import annotations

import pathlib
import tempfile
import unittest

import numpy as np

from genome.machinery import GenomeError, Organism, parse_genome

from ._toy import mini_genome, onehot


def _thresh_genome(history: int = 30):
    return parse_genome(mini_genome().text + f"THRESH cell own band history {history}\n")


class TestThreshParser(unittest.TestCase):
    def test_parses(self) -> None:
        g = _thresh_genome(30)
        self.assertEqual(g.declared["THRESH"], {"history": 30})

    def test_bad_syntax_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(mini_genome().text + "THRESH cell own band 30\n")

    def test_placeholder_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(mini_genome().text + "THRESH cell own band history N\n")


class TestThreshState(unittest.TestCase):
    def test_undeclared_own_band_is_none(self) -> None:
        org = Organism(mini_genome())
        self.assertIsNone(org.sight.own_band)
        self.assertIsNone(org.sight.own_band_n)
        self.assertIsNone(org.words.own_band, "THRESH tracks SIGHT cells only")

    def test_declared_allocates_shape(self) -> None:
        org = Organism(_thresh_genome(30))
        self.assertEqual(org.sight.own_band.shape, (200, 30))
        self.assertEqual(org.sight.own_band.dtype, np.float32)
        self.assertEqual(org.sight.own_band_n.shape, (200,))
        self.assertIsNone(org.words.own_band, "THRESH tracks SIGHT cells only")

    def test_correct_answer_pushes_cosine(self) -> None:
        org = Organism(_thresh_genome(30))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0)             # birth only -- nothing ESTABLISHED yet, so no push
        self.assertEqual(int(org.sight.own_band_n[0]), 0)
        org.moment(xs0, xw0)             # now cell0's established answer (word0) == T[0] -> a push
        self.assertEqual(int(org.sight.own_band_n[0]), 1)
        self.assertAlmostEqual(float(org.sight.own_band[0, 0]), 1.0, places=5)

    def test_wrong_answer_does_not_push(self) -> None:
        org = Organism(_thresh_genome(30))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        xw1 = onehot(1, 208)
        org.moment(xs0, xw0)
        org.moment(xs0, xw0)             # one push (now established)
        n_before = int(org.sight.own_band_n[0])
        self.assertGreater(n_before, 0)
        org.moment(xs0, xw1)             # SAME sight cell, a DIFFERENT word -> a mismatch, no push
        self.assertEqual(int(org.sight.own_band_n[0]), n_before)

    def test_ring_wraps_at_history(self) -> None:
        org = Organism(_thresh_genome(history=3))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for _ in range(6):
            org.moment(xs0, xw0)
        # moment 1 births (no push); moments 2..6 each push (5 pushes) -- ring length 3 wraps
        self.assertEqual(int(org.sight.own_band_n[0]), 5)
        self.assertEqual(org.sight.own_band.shape[1], 3)


class TestOwnFloor(unittest.TestCase):
    def test_below_five_entries_is_theta_n(self) -> None:
        org = Organism(_thresh_genome(30))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for _ in range(4):        # 1 birth + 3 pushes < 5
            org.moment(xs0, xw0)
        self.assertLess(int(org.sight.own_band_n[0]), 5)
        self.assertEqual(org.own_floor(0), org.g.theta_n)

    def test_five_or_more_is_the_p5(self) -> None:
        org = Organism(_thresh_genome(30))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for _ in range(7):        # 1 birth + 6 pushes >= 5
            org.moment(xs0, xw0)
        n = int(org.sight.own_band_n[0])
        self.assertGreaterEqual(n, 5)
        hist = org.sight.own_band[0, : min(n, org.sight.own_band.shape[1])]
        self.assertAlmostEqual(org.own_floor(0), float(np.percentile(hist, 5)), places=5)

    def test_undeclared_thresh_is_always_theta_n(self) -> None:
        org = Organism(mini_genome())
        self.assertEqual(org.own_floor(0), org.g.theta_n)


class TestThreshHash(unittest.TestCase):
    def test_hash_matches_plain_genome_before_any_push(self) -> None:
        """Nothing pushed yet -- THRESH-declared and plain must hash IDENTICALLY (the own_band gate)."""
        thresh_org, plain_org = Organism(_thresh_genome(30)), Organism(mini_genome())
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        thresh_org.moment(xs0, xw0)   # a birth only -- nothing established, no push
        plain_org.moment(xs0, xw0)
        self.assertEqual(int(thresh_org.sight.own_band_n[0]), 0)
        self.assertEqual(thresh_org.state_hash(), plain_org.state_hash())

    def test_hash_diverges_once_a_push_happens(self) -> None:
        thresh_org, plain_org = Organism(_thresh_genome(30)), Organism(mini_genome())
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for _ in range(2):
            thresh_org.moment(xs0, xw0)
            plain_org.moment(xs0, xw0)
        self.assertGreater(int(thresh_org.sight.own_band_n[0]), 0)
        self.assertNotEqual(thresh_org.state_hash(), plain_org.state_hash())
        # the underlying learned state is otherwise identical -- only the ring differs
        self.assertEqual(thresh_org.c, plain_org.c)
        np.testing.assert_array_equal(thresh_org.W, plain_org.W)

    def test_replay_byte_identical_with_thresh_declared(self) -> None:
        g = _thresh_genome(30)
        stream = [(onehot(i % 3, 64), onehot(i % 3, 208)) for i in range(12)]
        org_a, org_b = Organism(g), Organism(g)
        for xs, xw in stream:
            org_a.moment(xs, xw)
        for xs, xw in stream:
            org_b.moment(xs, xw)
        self.assertEqual(org_a.state_hash(), org_b.state_hash())
        np.testing.assert_array_equal(org_a.sight.own_band, org_b.sight.own_band)
        np.testing.assert_array_equal(org_a.sight.own_band_n, org_b.sight.own_band_n)


class TestThreshSaveLoad(unittest.TestCase):
    def test_round_trip_preserves_own_band(self) -> None:
        g = _thresh_genome(30)
        org = Organism(g)
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for _ in range(5):
            org.moment(xs0, xw0)
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "organism"
            org.save(p)
            loaded = Organism.load(p, g)
        np.testing.assert_array_equal(loaded.sight.own_band, org.sight.own_band)
        np.testing.assert_array_equal(loaded.sight.own_band_n, org.sight.own_band_n)
        self.assertEqual(loaded.state_hash(), org.state_hash())

    def test_load_old_snapshot_without_own_band_under_a_new_thresh_genome(self) -> None:
        """The toy's other half: a snapshot saved BEFORE THRESH existed loads under a genome that newly
        declares THRESH -- the history starts empty (own_floor == theta_n on every cell) and the digest
        still matches (own_band stays all-zero, so state_hash's own gate excludes it, exactly as it
        would for the SAME snapshot loaded back under its ORIGINAL, THRESH-less genome)."""
        plain_g = mini_genome()
        org = Organism(plain_g)
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for _ in range(5):
            org.moment(xs0, xw0)
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "organism"
            org.save(p)                                   # an OLD-format snapshot: no sight_own_band key
            thresh_g = _thresh_genome(30)
            loaded = Organism.load(p, thresh_g)            # must NOT raise
        self.assertIsNotNone(loaded.sight.own_band)
        self.assertEqual(int(loaded.sight.own_band_n[0]), 0)
        self.assertEqual(loaded.own_floor(0), loaded.g.theta_n)


if __name__ == "__main__":
    unittest.main()
