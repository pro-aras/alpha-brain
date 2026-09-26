# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 19:05 +0400 — check_arm run for EVERY A1
#   variant Builder 3 owns (the coordinator's ask, 2026-09-24 ~19:00: "a dummy-arm conformance
#   run per arm"). A1-MLC is not separately listed: B1-PREREG.md's own row says it differs
#   from A1 only in what stream the HARNESS feeds it, so its Arm code path IS "A1" (variant
#   defaults to "A1" either way) — covered by test_arm_a1_conformance.py already.
import os
import shutil
import sys
import tempfile
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.soft.arm import ArmA1  # noqa: E402
from brain.protocol import check_arm, make_row, op_row  # noqa: E402

from tests.brain.arms_soft.test_arm_a1_conformance import _build_synthetic_cache  # noqa: E402


class TestArmA1AllVariantsConform(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.tmp = tempfile.mkdtemp(prefix="b1_a1_variants_", dir="/data/dev/brain-runs/tmp")
        self.cache_dir, self.rows = _build_synthetic_cache(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _base_config(self, **extra):
        cfg = {"cache_dir": self.cache_dir, "run_dir": self.tmp, "seed": 42, "interpreter": "venv",
               "h0": 8, "hmax": 16, "arrival_budget": 4, "arrival_regen": 20}
        cfg.update(extra)
        return cfg

    def _check(self, variant: str, **extra):
        cfg = self._base_config(variant=variant, **extra)
        arm = ArmA1(seed=42, config=cfg)
        HarnessTeach = make_row(1, "TEACH", "L1", "a", {"glance_row": self.rows["a"][0], "name": "a"})
        arm.fit_event(HarnessTeach, valence=None)
        sample_ask = make_row(2, "ASK", "T", "a-t", {"cues": ["NAME"], "operands": [op_row(self.rows["a"][1])],
                                                       "candidate_rows": None, "answer_kind": "NAME"})
        sample_teach = make_row(3, "TEACH", "L1", "b", {"glance_row": self.rows["b"][0], "name": "b"})
        violations = check_arm(
            arm, sample_teach, sample_ask, tmp_dir=os.path.join(self.tmp, f"check_{variant}"),
            fresh_arm_factory=lambda: ArmA1(seed=42, config=cfg),
        )
        self.assertEqual(violations, [], f"{variant}: check_arm violations: {violations}")
        return arm

    def test_a1_plain(self):
        self._check("A1")

    def test_a1_fixed_never_grows(self):
        arm = self._check("A1-FIXED")
        self.assertEqual(arm.engine.hmax, arm.engine.active, "A1-FIXED must have no room to grow at all")
        self.assertEqual(arm.engine.budget.capacity, 0)

    def test_a1_fixed_takes_the_runners_fixed_h(self):
        """edit: Claude (Opus 5.5), 2026-09-26 11:52 +0400 — the seam: run.py passes A1's final H as `fixed_h`; A1-FIXED must
        START at that width (PREREG §4). The base config's h0 is 8, so the pre-fix code read 8 here: the assertion fails on it."""
        arm = self._check("A1-FIXED", fixed_h=12)
        self.assertEqual((arm.engine.hmax, arm.engine.active), (12, 12))
        self.assertEqual(arm.size()["h_alive"], 12)

    def test_a1_no_sleep_is_a_noop(self):
        arm = self._check("A1-NO-SLEEP")
        before = arm.state_sha()
        arm.sleep(500)
        after = arm.state_sha()
        self.assertEqual(before, after, "A1-NO-SLEEP's sleep() must be a true no-op on state")

    def test_a1_local_twin(self):
        self._check("A1-LOCAL")

    def test_a1_bptt_awake_twin(self):
        self._check("A1-BPTT-AWAKE")

    def test_a1_att(self):
        arm = self._check("A1-ATT", fixed_h=8, arrival_budget=0)
        self.assertEqual(arm.engine.active, arm.engine.hmax, "A1-ATT must be fixed-width (no growth)")
        self.assertIsNotNone(arm.readout)

    def test_a1_ma(self):
        arm = self._check("A1-MA", fixed_h=8, arrival_budget=0, ma_n_tokens=63)
        self.assertEqual(arm.engine.active, arm.engine.hmax, "A1-MA must be fixed-width (no growth)")
        self.assertIsNotNone(arm.readout)


if __name__ == "__main__":
    unittest.main()
