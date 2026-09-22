# edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:30 +0400 — ALPHA4-G.md task 1 (docs/ALPHA4-PREREG.md
# §2/§3, his 00:17 word «no cap»): Area/Organism growth mechanics under GROW unbounded -- Area doubles its
# own per-cell arrays, W/mask/strikes grow by a fixed +2048 chunk PER AXIS, decoupled schedules, `_birth`
# never refuses for room, and the recall-path fix for when the two schedules diverge (found by the advisor's
# review before any real closed root would have crashed on it: a mask row/column and an Area.alive array can
# have different lengths the moment Area's doubling and W's chunking disagree).
"""test_grow_mechanics.py — GROW unbounded: Area doubling, W/mask/strikes chunked growth, no refusal for
room, and the recall-path slicing fix for asymmetric growth."""
from __future__ import annotations

import unittest

import numpy as np

from genome.machinery import AREA_INITIAL_CAPACITY, GROW_CHUNK, Organism

from ._toy import mini_genome, unit


class TestInitialCapacity(unittest.TestCase):
    def test_areas_start_at_256_under_grow(self) -> None:
        org = Organism(mini_genome(grow=True))
        self.assertEqual(org.sight.nmax, AREA_INITIAL_CAPACITY)
        self.assertEqual(org.words.nmax, AREA_INITIAL_CAPACITY)
        self.assertEqual(AREA_INITIAL_CAPACITY, 256)

    def test_w_starts_at_one_chunk_under_grow(self) -> None:
        org = Organism(mini_genome(grow=True))
        self.assertEqual(org.W.shape, (GROW_CHUNK, GROW_CHUNK))
        self.assertEqual(org.mask.shape, (GROW_CHUNK, GROW_CHUNK))
        self.assertEqual(org.strikes.shape, (GROW_CHUNK, GROW_CHUNK))
        self.assertEqual(GROW_CHUNK, 2048)

    def test_negative_control_nmax_road_untouched(self) -> None:
        """A genome with NMAX and no GROW: Area/W capacity is genome.nmax, exactly as before this task —
        AREA_INITIAL_CAPACITY/GROW_CHUNK never enter the picture."""
        org = Organism(mini_genome())   # NMAX 200, no GROW
        self.assertEqual(org.sight.nmax, 200)
        self.assertEqual(org.words.nmax, 200)
        self.assertEqual(org.W.shape, (200, 200))
        self.assertFalse(org._grow)


class TestAreaGrow(unittest.TestCase):
    def test_grow_doubles_capacity_and_preserves_data(self) -> None:
        org = Organism(mini_genome(grow=True))
        area = org.sight
        # fill the live prefix with recognisable, non-zero data up to the initial capacity
        area.n = area.nmax
        area.cells[:] = np.arange(area.nmax * area.dim, dtype=np.float64).reshape(area.nmax, area.dim)
        area.alive[:] = 1
        area.misfires[:] = 7
        old_cells = area.cells.copy()
        area.grow()
        self.assertEqual(area.nmax, AREA_INITIAL_CAPACITY * 2)
        self.assertEqual(area.cells.shape, (AREA_INITIAL_CAPACITY * 2, area.dim))
        np.testing.assert_array_equal(area.cells[:AREA_INITIAL_CAPACITY], old_cells)
        np.testing.assert_array_equal(area.alive[:AREA_INITIAL_CAPACITY], np.ones(AREA_INITIAL_CAPACITY, dtype=np.uint8))
        np.testing.assert_array_equal(area.misfires[:AREA_INITIAL_CAPACITY], np.full(AREA_INITIAL_CAPACITY, 7, dtype=np.int64))
        # the new region is zero -- a fresh Area's own initial state
        self.assertFalse(area.alive[AREA_INITIAL_CAPACITY:].any())
        self.assertFalse(area.cells[AREA_INITIAL_CAPACITY:].any())

    def test_grow_preserves_own_band_when_thresh_declared(self) -> None:
        g = mini_genome(grow=True)
        text = g.text + "THRESH cell own band history 10\n"
        from genome.machinery import parse_genome
        org = Organism(parse_genome(text))
        self.assertIsNotNone(org.sight.own_band)
        self.assertEqual(org.sight.own_band.shape, (AREA_INITIAL_CAPACITY, 10))
        org.sight.own_band[3, 0] = 0.77
        org.sight.own_band_n[3] = 1
        org.sight.n = org.sight.nmax
        org.sight.grow()
        self.assertEqual(org.sight.own_band.shape, (AREA_INITIAL_CAPACITY * 2, 10))
        self.assertAlmostEqual(float(org.sight.own_band[3, 0]), 0.77, places=5)
        self.assertEqual(int(org.sight.own_band_n[3]), 1)


class TestGrowW(unittest.TestCase):
    def test_grow_w_adds_one_chunk_on_the_given_axis(self) -> None:
        org = Organism(mini_genome(grow=True))
        org.W[5, 7] = 0.42; org.mask[5, 7] = 1; org.strikes[5, 7] = 2
        org._grow_W(axis=0)
        self.assertEqual(org.W.shape, (GROW_CHUNK * 2, GROW_CHUNK))
        self.assertEqual(org.mask.shape, (GROW_CHUNK * 2, GROW_CHUNK))
        self.assertEqual(org.strikes.shape, (GROW_CHUNK * 2, GROW_CHUNK))
        self.assertAlmostEqual(float(org.W[5, 7]), 0.42)
        self.assertEqual(int(org.mask[5, 7]), 1)
        self.assertEqual(int(org.strikes[5, 7]), 2)
        org._grow_W(axis=1)
        self.assertEqual(org.W.shape, (GROW_CHUNK * 2, GROW_CHUNK * 2))


class TestBirthNeverRefusesUnderGrow(unittest.TestCase):
    def test_many_births_no_refusal_and_asymmetric_growth(self) -> None:
        """The end-to-end proof: ~2,100 real moment() calls, one fixed word (words area stays at n=1,
        never grows) against ~2,100 distinct random sight vectors (almost every one novel -> births).
        Reproduces exactly the scenario the advisor flagged: sight's capacity crosses BOTH its own
        doubling schedule (256 -> 512 -> 1024 -> 2048 -> 4096) and W's chunk schedule (2048 -> 4096) while
        words' side of everything never moves -- W ends up asymmetric, (4096, 2048)."""
        org = Organism(mini_genome(grow=True, budget=100000))
        org.new_arrival()
        rng = np.random.default_rng(20260923)
        xw0 = unit(rng, 208)
        for _ in range(2100):
            xs = unit(rng, 64)
            org.moment(xs, xw0)
        self.assertEqual(org.c["births_refused_nmax"], 0, "GROW must never refuse a birth for room")
        self.assertGreater(org.sight.n, 2048, "the random-vector stream must have crossed the first W chunk boundary")
        self.assertEqual(org.words.n, 1, "the fixed word must never grow the words area (the asymmetry the test needs)")
        self.assertEqual(org.sight.nmax, 4096)
        self.assertEqual(org.words.nmax, 256, "words capacity must stay untouched -- decoupled from sight's growth")
        self.assertEqual(org.W.shape, (4096, 2048), "W is NOT square under GROW -- the two axes grow independently")
        self.assertEqual(org.mask.shape, (4096, 2048))
        self.assertEqual(org.strikes.shape, (4096, 2048))

    def test_recall_after_asymmetric_growth_does_not_crash(self) -> None:
        """The advisor's flagged crash: recall()/recall_many()/expected_sight() AND a mask row/column
        against an Area.alive array whose length has diverged from it. Exercises `side="words"` (which
        reads `other = self.sight`, the area whose capacity ran far ahead of W's OTHER axis) -- the
        shape most likely to explode."""
        org = Organism(mini_genome(grow=True, budget=100000))
        org.new_arrival()
        rng = np.random.default_rng(1)
        xw0 = unit(rng, 208)
        xs_first = None
        for i in range(2100):
            xs = unit(rng, 64)
            if i == 0:
                xs_first = xs
            org.moment(xs, xw0)
        self.assertGreater(org.sight.nmax, org.W.shape[1], "the fixture must actually exercise the divergent-capacity path")
        # recall(side="words"): other=self.sight, whose alive[] (nmax=4096) is longer than W's row (2048) -- would ValueError pre-fix
        r = org.recall("words", xw0)
        self.assertIn(r["reason"], ("answer", "ratio", "close", "noedge", "novel"))
        # recall(side="sight"): other=self.words (alive nmax=256) vs W's column (2048) -- the other direction
        r2 = org.recall("sight", xs_first)
        self.assertIn(r2["reason"], ("answer", "ratio", "close", "noedge", "novel"))
        # recall_many, same two directions
        rm = org.recall_many("words", [xw0])
        self.assertEqual(rm["reason"], r["reason"])
        rm2 = org.recall_many("sight", [xs_first])
        self.assertEqual(rm2["reason"], r2["reason"])
        # expected_sight: mask[:, t] (length W.shape[0]=4096) vs sight.alive (nmax=4096) -- same length here,
        # so this exercises the OTHER direction of the fix (still sliced, still correct, never a crash).
        exp = org.expected_sight(xw0)
        self.assertIsNotNone(exp)
        self.assertEqual(exp.shape, (64,))


if __name__ == "__main__":
    unittest.main()
