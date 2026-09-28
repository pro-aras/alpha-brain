# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 20:20 +0400 — ArmA3 conformance + a
#   §3.1-STYLE replay-identity test, same declared caveat as the other two arm families: no
#   real cache/tape exists yet (stage −1 has not run), so every number here is from a
#   SYNTHETIC cache/tape built in this file.
import os
import shutil
import sys
import tempfile
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from brain.arms.clauses.arm import ArmA3  # noqa: E402
from brain.glance_cache import CacheWriter, FEATURES_PER_GLANCE, GLANCES_PER_ROW  # noqa: E402
from brain.protocol import HarnessContract, check_arm, make_row, op_name, op_row, row_sha  # noqa: E402


def _build_synthetic_cache(tmp_dir: str):
    out = os.path.join(tmp_dir, "cache")
    w = CacheWriter(out)
    rng = np.random.default_rng(2024)
    rows = {}
    for ch in "abc":
        rows[ch] = []
        for variant in range(2):
            feats = rng.normal(size=(GLANCES_PER_ROW, FEATURES_PER_GLANCE)).astype(np.float64)
            r = w.add(item_id=f"{ch}-{variant}", script="latin-lower", char=ch, font="synthetic",
                      variant=str(variant), seed=1, canvas_png_sha256="0" * 64, feats=feats)
            rows[ch].append(r)
    w.finalize(seed=1, genome_sha="synthetic", organ_pins={}, interpreter={}, library_versions={})
    return out, rows


def _build_synthetic_tape(rows) -> list:
    tape = []
    seq = 1

    def add(kind, phase, item, payload):
        nonlocal seq
        r = make_row(seq, kind, phase, item, payload)
        seq += 1
        tape.append(r)
        return r

    add("TEACH", "L1", "a", {"glance_row": rows["a"][0], "name": "a"})
    add("TEACH", "L1", "b", {"glance_row": rows["b"][0], "name": "b"})
    ask1 = add("ASK", "L4", "a-name", {"cues": ["NAME"], "operands": [op_row(rows["a"][1])],
                                        "candidate_rows": None, "answer_kind": "NAME"})
    add("FEEDBACK", "L4", "a-name", {"ask_seq": ask1["seq"], "right": "a"})
    add("TEACH", "L2", "c", {"glance_row": rows["c"][0], "name": "c"})
    ask2 = add("ASK", "L4", "point-a", {"cues": ["POINT"], "operands": [op_name("a")],
                                         "candidate_rows": [rows["a"][1], rows["b"][1], rows["c"][1]],
                                         "answer_kind": "PICK"})
    add("FEEDBACK", "L4", "point-a", {"ask_seq": ask2["seq"], "right": 0})
    add("SLEEP", "L1", "-", {"steps": 50})
    add("TEST_BEGIN", "T_L", "-", {"sitting": "T_L"})
    add("ASK", "T_L", "a-name-test", {"cues": ["NAME"], "operands": [op_row(rows["a"][1])],
                                        "candidate_rows": None, "answer_kind": "NAME"})
    add("TEST_END", "T_L", "-", {"sitting": "T_L"})
    return tape


def _run_tape(arm, tape):
    pending, families = {}, {}
    in_test = False
    test_answers = []
    for row in tape:
        k = row["kind"]
        if k == "TEACH":
            HarnessContract.teach(arm, row)
        elif k == "ARRIVAL":
            HarnessContract.arrival(arm, row)
        elif k == "SLEEP":
            HarnessContract.sleep(arm, row)
        elif k == "TEST_BEGIN":
            in_test = True
        elif k == "TEST_END":
            in_test = False
        elif k == "ASK":
            if in_test:
                test_answers.append(HarnessContract.test_ask(arm, row))
            else:
                ans = HarnessContract.training_ask(arm, row)
                pending[row["seq"]] = ans
                families[row["seq"]] = row["payload"]["answer_kind"]
        elif k == "FEEDBACK":
            ask_seq = row["payload"]["ask_seq"]
            HarnessContract.feedback(arm, row, pending[ask_seq], families[ask_seq])
    return test_answers


def _config(cache_dir: str, **extra):
    cfg = {"cache_dir": cache_dir, "run_dir": "/data/dev/brain-runs/tmp", "seed": 314, "interpreter": "venv",
           "C": 4, "N": 100, "T": 15, "s": 3.9, "name_cap": 8}
    cfg.update(extra)
    return cfg


class TestArmA3Conformance(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.tmp = tempfile.mkdtemp(prefix="b1_a3_", dir="/data/dev/brain-runs/tmp")
        self.cache_dir, self.rows = _build_synthetic_cache(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_check_arm_reports_no_violations(self):
        cfg = _config(self.cache_dir)
        arm = ArmA3(seed=314, config=cfg)
        HarnessContract.teach(arm, make_row(1, "TEACH", "L1", "a", {"glance_row": self.rows["a"][0], "name": "a"}))
        sample_ask = make_row(2, "ASK", "T_L", "a-test", {"cues": ["NAME"], "operands": [op_row(self.rows["a"][1])],
                                                            "candidate_rows": None, "answer_kind": "NAME"})
        sample_teach = make_row(3, "TEACH", "L1", "b", {"glance_row": self.rows["b"][0], "name": "b"})
        violations = check_arm(
            arm, sample_teach, sample_ask, tmp_dir=os.path.join(self.tmp, "check_arm"),
            fresh_arm_factory=lambda: ArmA3(seed=314, config=cfg),
        )
        self.assertEqual(violations, [], f"check_arm found violations: {violations}")

    def test_full_synthetic_tape_runs(self):
        cfg = _config(self.cache_dir)
        arm = ArmA3(seed=314, config=cfg)
        tape = _build_synthetic_tape(self.rows)
        before = arm.state_sha()
        answers = _run_tape(arm, tape)
        after = arm.state_sha()
        self.assertNotEqual(before, after, "training must move state")
        self.assertEqual(len(answers), 1)

    def test_replay_identity_on_synthetic_tape(self):
        cfg = _config(self.cache_dir)
        tape = _build_synthetic_tape(self.rows)
        arm1 = ArmA3(seed=314, config=cfg)
        arm2 = ArmA3(seed=314, config=cfg)
        _run_tape(arm1, tape)
        _run_tape(arm2, tape)
        self.assertEqual(arm1.state_sha(), arm2.state_sha())

    def test_planted_divergence_is_caught(self):
        cfg = _config(self.cache_dir)
        tape_a = _build_synthetic_tape(self.rows)
        tape_b = _build_synthetic_tape(self.rows)
        tape_b[1]["payload"]["glance_row"] = self.rows["c"][1]
        tape_b[1]["sha"] = row_sha(tape_b[1]["payload"])
        arm_a, arm_b = ArmA3(314, cfg), ArmA3(314, cfg)
        before_a = before_b = None
        for i, (ra, rb) in enumerate(zip(tape_a, tape_b)):
            if i == 1:
                before_a, before_b = arm_a.state_sha(), arm_b.state_sha()
            for arm, row in ((arm_a, ra), (arm_b, rb)):
                k = row["kind"]
                if k == "TEACH":
                    HarnessContract.teach(arm, row)
                elif k == "SLEEP":
                    HarnessContract.sleep(arm, row)
                elif k == "ASK":
                    HarnessContract.training_ask(arm, row)
        self.assertEqual(before_a, before_b)
        self.assertNotEqual(arm_a.state_sha(), arm_b.state_sha())

    def test_resume_from_snapshot_matches_uninterrupted_run(self):
        cfg = _config(self.cache_dir)
        tape = _build_synthetic_tape(self.rows)
        split = 4

        uninterrupted = ArmA3(314, cfg)
        _run_tape(uninterrupted, tape)
        want = uninterrupted.state_sha()

        first_half = ArmA3(314, cfg)
        pending, families = {}, {}
        for row in tape[:split]:
            k = row["kind"]
            if k == "TEACH":
                HarnessContract.teach(first_half, row)
            elif k == "ASK":
                ans = HarnessContract.training_ask(first_half, row)
                pending[row["seq"]] = ans
                families[row["seq"]] = row["payload"]["answer_kind"]
            elif k == "FEEDBACK":
                ask_seq = row["payload"]["ask_seq"]
                HarnessContract.feedback(first_half, row, pending[ask_seq], families[ask_seq])
        snap_path = os.path.join(self.tmp, "snap")
        first_half.snapshot(snap_path)
        resumed = ArmA3(314, cfg)
        resumed.load(snap_path)
        self.assertEqual(resumed.state_sha(), first_half.state_sha())

        for arm in (first_half, resumed):
            in_test = False
            for row in tape[split:]:
                k = row["kind"]
                if k == "TEACH":
                    HarnessContract.teach(arm, row)
                elif k == "SLEEP":
                    HarnessContract.sleep(arm, row)
                elif k == "TEST_BEGIN":
                    in_test = True
                elif k == "TEST_END":
                    in_test = False
                elif k == "ASK":
                    if in_test:
                        HarnessContract.test_ask(arm, row)
                    else:
                        ans = HarnessContract.training_ask(arm, row)
                        pending[row["seq"]] = ans
                        families[row["seq"]] = row["payload"]["answer_kind"]
                elif k == "FEEDBACK":
                    ask_seq = row["payload"]["ask_seq"]
                    HarnessContract.feedback(arm, row, pending[ask_seq], families[ask_seq])
        self.assertEqual(first_half.state_sha(), resumed.state_sha())
        self.assertEqual(resumed.state_sha(), want)


if __name__ == "__main__":
    unittest.main()
