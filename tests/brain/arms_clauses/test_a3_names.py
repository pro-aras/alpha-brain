# edit: Claude (Opus 5.5), 2026-09-26 12:57 +0400 — A3 learns to NAME. In B1's first graded run A3 answered UNKNOWN to every
# NAME test ask: an untrained Tsetlin machine votes 0 → UNKNOWN, and the old guard held an ask for its FEEDBACK only when the
# arm had answered, so the machine was never corrected. Fails on the old arm (0 of 6, all UNKNOWN).
import os
import shutil
import sys
import tempfile
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.clauses.arm import ArmA3  # noqa: E402
from brain.protocol import AnswerKind  # noqa: E402
from tests.brain.arms_soft.name_toy import run_name_toy  # noqa: E402
from tests.brain.arms_soft.test_arm_a1_conformance import _build_synthetic_cache  # noqa: E402


class TestA3Names(unittest.TestCase):
    def test_a3_learns_the_name_toy(self):
        torch.set_num_threads(1)
        tmp = tempfile.mkdtemp(prefix="b1_a3_names_", dir="/data/dev/brain-runs/tmp")
        try:
            cache_dir, rows = _build_synthetic_cache(tmp)
            arm = ArmA3(seed=42, config={"cache_dir": cache_dir, "run_dir": tmp, "seed": 42, "interpreter": "venv",
                                         "C": 200, "T": 50, "s": 5.0})
            res = run_name_toy(arm, rows)
            right = sum(1 for ch, k, v in res if k == AnswerKind.NAME and v == ch)
            self.assertGreaterEqual(right, 5, f"{right} of 6: {res}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
