# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 19:0x +0400 — tests for brain/harness/probes.py: real
# renderings of genome.world's own "square"/"ring"/"circle" through the real pinned organs. Must run under
# /usr/bin/python3.
from __future__ import annotations

import unittest

from brain.harness.probes import distinguishable_control, identical_control, run_both

SEED = 20261001


class TestDistinguishableControl(unittest.TestCase):
    def test_square_vs_ring_separates_cleanly(self) -> None:
        r = distinguishable_control(SEED, n_per_class=20)
        self.assertTrue(r["pass"], r)
        self.assertGreaterEqual(r["accuracy"], 0.99)


class TestIdenticalControl(unittest.TestCase):
    def test_arbitrary_label_on_one_thing_reads_near_chance(self) -> None:
        r = identical_control(SEED, n=60)
        self.assertTrue(r["pass"], r)
        self.assertLess(abs(r["accuracy"] - 0.5), r["band_95"] + 1e-9)


class TestRunBoth(unittest.TestCase):
    def test_both_controls_pass_together(self) -> None:
        r = run_both(SEED)
        self.assertTrue(r["pass"], r)


if __name__ == "__main__":
    unittest.main()
