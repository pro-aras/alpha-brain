# edit: Claude (Opus 5.5), 2026-09-26 12:49 +0400 — the NAME road of A1, end to end. Found in B1's graded run of seed
# 20261001: `n_names` stayed 0 for the whole run (nothing called `NameAnswerHead.hear_name`), so every NAME ask of every A1
# variant read UNKNOWN (2,698 of 2,698 test asks) and every NAME FEEDBACK returned early. No test had ever asked A1 to NAME.
# Both tests below FAIL on the pre-fix arm.
import os
import shutil
import sys
import tempfile
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.soft.arm import ArmA1  # noqa: E402
from brain.protocol import AnswerKind, HarnessContract, make_row, op_row  # noqa: E402
from tests.brain.arms_soft.test_arm_a1_conformance import _build_synthetic_cache  # noqa: E402


class TestArmA1Names(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.tmp = tempfile.mkdtemp(prefix="b1_a1_names_", dir="/data/dev/brain-runs/tmp")
        self.cache_dir, self.rows = _build_synthetic_cache(self.tmp)
        self.seq = 0

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _row(self, kind, phase, item, payload):
        self.seq += 1
        return make_row(self.seq, kind, phase, item, payload)

    def _arm(self):
        return ArmA1(seed=42, config={"cache_dir": self.cache_dir, "run_dir": self.tmp, "seed": 42, "interpreter": "venv"})

    def test_teach_hears_the_name(self):
        arm = self._arm()
        for ch in "abc":
            HarnessContract.teach(arm, self._row("TEACH", "L1", ch, {"glance_row": self.rows[ch][0], "name": ch}))
        self.assertEqual(arm.names.names, ["a", "b", "c"])
        self.assertEqual(arm.size()["n_names"], 3)

    def test_the_name_road_learns_the_toy(self):
        """Teach a, b, c; 40 rounds of NAME training asks with the right answer as FEEDBACK on both renderings; then NAME
        test asks on each letter's renderings: the arm must answer NAMES (not UNKNOWN) and be right on at least 5 of 6."""
        arm = self._arm()
        for ch in "abc":
            HarnessContract.teach(arm, self._row("TEACH", "L1", ch, {"glance_row": self.rows[ch][0], "name": ch}))
        for _ in range(40):
            for ch in "abc":
                for v in (0, 1):
                    ask = self._row("ASK", "L4", f"{ch}-name", {"cues": ["NAME"], "operands": [op_row(self.rows[ch][v])],
                                                                  "candidate_rows": None, "answer_kind": "NAME"})
                    ans = HarnessContract.training_ask(arm, ask)
                    fb = self._row("FEEDBACK", "L4", f"{ch}-name", {"ask_seq": ask["seq"], "right": ch})
                    HarnessContract.feedback(arm, fb, ans, "NAME")
        right, kinds = 0, []
        for ch in "abc":
            for v in (0, 1):
                ask = self._row("ASK", "T_L", f"{ch}-name-test", {"cues": ["NAME"], "operands": [op_row(self.rows[ch][v])],
                                                                    "candidate_rows": None, "answer_kind": "NAME"})
                a = HarnessContract.test_ask(arm, ask)
                kinds.append(a.kind)
                right += int(a.kind == AnswerKind.NAME and a.value == ch)
        self.assertNotIn(AnswerKind.UNKNOWN, kinds, f"the arm abstained: {kinds}")
        self.assertGreaterEqual(right, 5, f"{right} of 6 named right")


if __name__ == "__main__":
    unittest.main()
