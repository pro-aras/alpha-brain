# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 17:50 +0400 — RunningBinariser (A2/A3's
#   shared 'threshold at the median over TEACH glances, computed once' rule, PREREG §4 rows
#   A2/A3). Declared timing: freeze() fires at the Arm wrapper's first SLEEP row; this test
#   pins the class's own contract (accumulate until frozen, then fixed) independent of that.
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.logic.engine import RunningBinariser  # noqa: E402


class TestRunningBinariser(unittest.TestCase):
    def test_freeze_computes_exact_per_dim_median(self):
        b = RunningBinariser(dim=3)
        rows = [torch.tensor([1.0, 10.0, -5.0]), torch.tensor([2.0, 20.0, 0.0]), torch.tensor([3.0, 0.0, 5.0])]
        for r in rows:
            b.observe(r)
        thr = b.freeze()
        expected = torch.stack(rows).median(dim=0).values
        self.assertTrue(torch.equal(thr, expected))

    def test_binarise_uses_strict_greater_than(self):
        b = RunningBinariser(dim=2)
        # torch's Tensor.median (unlike numpy's) is the LOWER of the two middle values for an
        # even count, not their average -- for [0,2] it returns 0, not 1. Declared: this class
        # inherits torch's own median convention rather than reimplementing numpy's.
        b.observe(torch.tensor([0.0, 0.0]))
        b.observe(torch.tensor([2.0, 2.0]))
        thr = b.freeze()
        self.assertTrue(torch.equal(thr, torch.tensor([0.0, 0.0])), "torch median([0,2]) is 0 (lower), not 1")
        out = b.binarise(torch.tensor([0.0, 1.5]))
        self.assertTrue(torch.equal(out, torch.tensor([0.0, 1.0])), "at exactly the threshold: NOT set (strict >)")

    def test_observations_after_freeze_are_ignored(self):
        b = RunningBinariser(dim=1)
        b.observe(torch.tensor([1.0]))
        b.observe(torch.tensor([3.0]))
        thr1 = b.freeze().clone()
        b.observe(torch.tensor([1000.0]))  # must NOT move the frozen threshold
        thr2 = b.freeze()
        self.assertTrue(torch.equal(thr1, thr2))

    def test_empty_freeze_defaults_to_zero_threshold(self):
        b = RunningBinariser(dim=4)
        thr = b.freeze()
        self.assertTrue(torch.equal(thr, torch.zeros(4)))


if __name__ == "__main__":
    unittest.main()
