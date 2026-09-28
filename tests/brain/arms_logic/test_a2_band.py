# edit: Claude (Opus 5.5), 2026-09-26 12:57 +0400 — A2 ANSWERS once trained. In B1's first graded run A2 answered UNKNOWN to
# every NAME test ask: its abstention band was learned from the RELAXED logits' margins and compared with the DISCRETISED
# group sums the answer uses (#162: a gate in other units than its variable), and an abstained ask was never corrected.
# This pins the ROAD (A2 answers on the toy, and its band is in the tested units); A2's accuracy is B1's measurement, not a test.
# Fails on the old arm (6 of 6 UNKNOWN).
import os
import shutil
import sys
import tempfile
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.logic.arm import ArmA2  # noqa: E402
from brain.protocol import AnswerKind  # noqa: E402
from tests.brain.arms_soft.name_toy import run_name_toy  # noqa: E402
from tests.brain.arms_soft.test_arm_a1_conformance import _build_synthetic_cache  # noqa: E402


class TestA2Band(unittest.TestCase):
    def test_a2_answers_once_trained_and_its_band_is_in_tested_units(self):
        torch.set_num_threads(1)
        tmp = tempfile.mkdtemp(prefix="b1_a2_band_", dir="/data/dev/brain-runs/tmp")
        try:
            cache_dir, rows = _build_synthetic_cache(tmp)
            arm = ArmA2(seed=42, config={"cache_dir": cache_dir, "run_dir": tmp, "seed": 42, "interpreter": "venv"})
            res = run_name_toy(arm, rows)
            kinds = [k for _, k, _ in res]
            self.assertLessEqual(kinds.count(AnswerKind.UNKNOWN), 1, f"A2 abstained: {kinds}")
            margins = arm.net._train_margins
            self.assertTrue(margins, "no training margin observed")
            self.assertTrue(all(float(m).is_integer() for m in margins), "the band must come from DISCRETISED group sums")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
