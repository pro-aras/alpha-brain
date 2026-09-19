"""test_moment_sight.py — B2: Organism.moment_sight(x_s) — resonance + novelty birth on sight only.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B2 (docs/G4-PREREG.md §3, docs/briefs/
G4-BUILDER-B-GENES.md): 50 sight-only moments birth cells and 0 edges; the hash differs from a life
without them; moment()'s own behaviour stays byte-identical (proven by test_pin_skeleton.py, run in the
same suite — moment_sight touches no code moment() executes, and adds no self.c key).
"""
from __future__ import annotations

import unittest

import numpy as np

from genome.machinery import Organism

from ._toy import mini_genome, unit


class TestMomentSight(unittest.TestCase):
    def test_50_sight_only_moments_birth_cells_and_no_edges(self) -> None:
        g = mini_genome(nmax=200, budget=200)
        org = Organism(g)
        rng = np.random.default_rng(7)
        for _ in range(50):
            org.moment_sight(unit(rng))
        self.assertEqual(org.moments_sight_only, 50)
        self.assertEqual(org.t, 50)
        self.assertGreater(org.sight.n, 0, "50 near-orthogonal 64-d draws against theta_n=0.5 must birth cells")
        self.assertEqual(org.words.n, 0, "moment_sight must never touch the words area")
        self.assertEqual(int(org.mask.sum()), 0, "moment_sight must birth 0 edges (no MEET)")
        self.assertEqual(org.c["edges_born"], 0)
        self.assertEqual(org.c["cells_merged_sight"], 0)
        self.assertEqual(org.c["cells_merged_words"], 0)
        self.assertEqual(len(org.births), org.sight.n, "every birth logged, sight cells only")
        self.assertTrue(all(area == "sight" for _m, area, _c, _r in org.births))

    def test_hash_differs_from_a_life_without_them(self) -> None:
        g = mini_genome(nmax=200, budget=200)
        org_a = Organism(g)
        rng = np.random.default_rng(7)
        for _ in range(50):
            org_a.moment_sight(unit(rng))
        org_b = Organism(g)   # a life that never calls moment_sight
        self.assertNotEqual(org_a.state_hash(), org_b.state_hash())

    def test_summary_carries_the_counter_never_in_c(self) -> None:
        g = mini_genome(nmax=200, budget=200)
        org = Organism(g)
        rng = np.random.default_rng(1)
        for _ in range(5):
            org.moment_sight(unit(rng))
        self.assertEqual(org.summary()["moments_sight_only"], 5)
        self.assertNotIn("moments_sight_only", org.c, "the pin trap: a self.c key moves state_hash even at value 0")

    def test_scale_tail_mirrors_moment(self) -> None:
        """SCALE fires on the shared t-clock, exactly as moment()'s tail does."""
        g = mini_genome(nmax=200, budget=200)
        text = g.text.replace("SCALE every 1000 moments", "SCALE every 3 moments")
        from genome.machinery import parse_genome
        g3 = parse_genome(text)
        org = Organism(g3)
        rng = np.random.default_rng(3)
        for _ in range(3):
            org.moment_sight(unit(rng))
        self.assertEqual(org.c["scale_events"], 1)


if __name__ == "__main__":
    unittest.main()
