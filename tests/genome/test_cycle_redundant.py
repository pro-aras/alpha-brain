# edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:20 +0400 — ALPHA4-G.md task 4 (docs/ALPHA4-PREREG.md
# §2/§3): CYCLE consolidate when redundant > <share> of alive — the cycle keyed on redundancy, not a cap.
"""test_cycle_redundant.py — CYCLE's redundant-share form: genome/sleep.py's cycle() trigger, the "since
the last cycle" baseline, and the old form's own toy (G4-PREREG B7) staying PASS under NMAX."""
from __future__ import annotations

import unittest

import numpy as np

from genome.machinery import GenomeError, Organism, parse_genome
from genome.sleep import cycle

from ._toy import mini_genome, unit


def _seed_alive_cells(org: Organism, n: int, rng) -> None:
    """Births `n` distinct sight cells the cheap way (real moment() calls, one fixed word so words never
    grows) -- gives cycle() a real, non-zero `alive` denominator to divide by."""
    xw0 = unit(rng, 208)
    while org.total_cells() < n:
        org.moment(unit(rng, 64), xw0)


class TestCycleRedundantTrigger(unittest.TestCase):
    def test_fires_when_ratio_exceeds_share(self) -> None:
        org = Organism(mini_genome(grow=True, cycle_share=0.05, budget=100000))
        org.new_arrival()
        rng = np.random.default_rng(1)
        _seed_alive_cells(org, 20, rng)
        alive = org.total_cells()
        # simulate 2 redundant refusals since the last cycle (never fired: baseline is 0) on `alive` cells
        # -> ratio 2/alive; pick alive small enough that 2/alive > 0.05 (alive=20 -> 0.10 > 0.05)
        org.c["births_refused_redundant"] = 2
        self.assertGreater(2 / alive, 0.05)
        ran = cycle(org)
        self.assertTrue(ran)
        self.assertEqual(org._cycle_baseline_redundant, 2, "the baseline resets to the CURRENT count once a cycle actually runs")

    def test_does_not_fire_below_share(self) -> None:
        org = Organism(mini_genome(grow=True, cycle_share=0.5, budget=100000))
        org.new_arrival()
        rng = np.random.default_rng(2)
        _seed_alive_cells(org, 20, rng)
        org.c["births_refused_redundant"] = 1   # 1/20 = 0.05 < 0.5
        self.assertFalse(cycle(org))
        self.assertEqual(org._cycle_baseline_redundant, 0, "an untriggered check never moves the baseline")

    def test_since_the_last_cycle_not_since_the_beginning(self) -> None:
        """The trigger reads the DELTA since the last actual cycle, not the running total -- a genome
        with a low share that fired once must not immediately refire on the SAME old refusals."""
        org = Organism(mini_genome(grow=True, cycle_share=0.05, budget=100000))
        org.new_arrival()
        rng = np.random.default_rng(3)
        _seed_alive_cells(org, 20, rng)
        org.c["births_refused_redundant"] = 3
        self.assertTrue(cycle(org))
        self.assertEqual(org._cycle_baseline_redundant, 3)
        # no NEW redundant refusals since -- must not fire again
        self.assertFalse(cycle(org))
        # 2 more redundant refusals since the last cycle, on a small alive count -> fires again
        # (merge/prune found nothing to consolidate among these distinct random cells, so `alive` is
        # unchanged at 20 here -- 1/20 lands exactly ON the bar, not over it, so this uses 2 for margin)
        alive_now = org.total_cells()
        org.c["births_refused_redundant"] = 5   # delta = 2 since baseline 3
        self.assertGreater(2 / alive_now, 0.05)
        self.assertTrue(cycle(org))
        self.assertEqual(org._cycle_baseline_redundant, 5)

    def test_zero_alive_never_divides_by_zero(self) -> None:
        org = Organism(mini_genome(grow=True, cycle_share=0.05))
        org.c["births_refused_redundant"] = 5
        self.assertEqual(org.total_cells(), 0)
        self.assertFalse(cycle(org))   # must not raise ZeroDivisionError

    def test_undeclared_cycle_returns_false(self) -> None:
        org = Organism(mini_genome(grow=True))
        self.assertNotIn("CYCLE", org.g.declared)
        self.assertFalse(cycle(org))

    def test_old_grow_to_form_under_nmax_toy_still_passes(self) -> None:
        """The negative control (G4-PREREG B7's own toy, verbatim): the old form's ceiling-based trigger
        is completely untouched by this task's new "share" branch."""
        text = """\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 8 blank=zero
AREA sight from retina
AREA words from ear
MEET sight words
BIRTH novelty cos<0.995
BIRTH error misfires 10
BUDGET 2000 per arrival
NMAX 30
KWTA 1
HEBB window 1
DELTA lr 0.1
PRUNE w<0.02 after 3 chances
MERGE cos>0.9 same-answer
SCALE every 1000000 moments
STAGE 1 senses moments 0..0
STAGE 2 meet moments 0..
RECALL k=1
ABSTAIN second/best > 0.85
CYCLE grow to 0.9 nmax then consolidate
"""
        g = parse_genome(text)
        self.assertEqual(g.declared["CYCLE"], {"grow_to": 0.9})
        org = Organism(g)
        rng = np.random.default_rng(0)
        dim_s, dim_w = g.sight_dim(), g.words_dim()
        v0 = np.zeros(dim_s); v0[0] = 1.0
        xw = np.zeros(dim_w); xw[0] = 1.0

        def tick():
            noise = rng.normal(size=dim_s) * 0.02
            x = v0 + noise; x /= np.linalg.norm(x)
            org.moment(x, xw)

        ceiling = 0.9 * g.nmax
        for _ in range(40):
            if org.total_cells() >= ceiling:
                break
            tick()
        self.assertGreaterEqual(org.total_cells(), ceiling)
        ran = cycle(org)
        self.assertTrue(ran)
        self.assertLess(org.total_cells(), ceiling)


if __name__ == "__main__":
    unittest.main()
