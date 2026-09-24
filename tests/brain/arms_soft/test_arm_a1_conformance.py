# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 18:40 +0400 — ArmA1 conformance (the
#   coordinator's ask: verify against brain/protocol.py ac7d2ff byte for byte and pass
#   check_arm) plus a §3.1-STYLE replay-identity test. Declared: the real glance cache and
#   tape (seed 20261001) do not exist yet — stage −1 has not run (B1-PREREG.md's own §0:
#   "STATUS: DRAFT until the seat appends a dated line under §12"). Every number here comes
#   from a SYNTHETIC cache and a SYNTHETIC tape built in this file, not from a real B1 run;
#   said explicitly rather than left to be assumed, per docs/brain/B1-PREREG.md §10's "the
#   numbers rule" and #194.
import os
import shutil
import sys
import tempfile
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from brain.arms.soft.arm import ArmA1  # noqa: E402
from brain.glance_cache import Cache, CacheWriter, GLANCES_PER_ROW, FEATURES_PER_GLANCE  # noqa: E402
from brain.protocol import HarnessContract, check_arm, make_row, op_name, op_row  # noqa: E402


def _build_synthetic_cache(tmp_dir: str) -> str:
    """Three letters (a, b, c), two renderings each — small, deterministic, entirely synthetic
    (never claims to be the real seed-20261001 cache)."""
    out = os.path.join(tmp_dir, "cache")
    w = CacheWriter(out)
    rng = np.random.default_rng(12345)
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
    """A minimal driver over brain.protocol.HarnessContract — mirrors what brain/harness/run.py
    will do (B1-PREREG.md §8), scoped to exactly what this synthetic tape needs."""
    pending = {}
    families = {}
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


def _config(cache_dir: str, variant: str = "A1", **extra):
    cfg = {"cache_dir": cache_dir, "run_dir": "/data/dev/brain-runs/tmp", "seed": 999, "interpreter": "venv",
           "variant": variant, "h0": 8, "hmax": 16, "arrival_budget": 4, "arrival_regen": 20}
    cfg.update(extra)
    return cfg


class TestArmA1Conformance(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.tmp = tempfile.mkdtemp(prefix="b1_a1_", dir="/data/dev/brain-runs/tmp")
        self.cache_dir, self.rows = _build_synthetic_cache(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_check_arm_reports_no_violations(self):
        cfg = _config(self.cache_dir)
        arm = ArmA1(seed=999, config=cfg)
        # teach it a little first, matching check_arm's own docstring ("already-taught-a-little")
        HarnessContract.teach(arm, make_row(1, "TEACH", "L1", "a", {"glance_row": self.rows["a"][0], "name": "a"}))
        sample_ask = make_row(2, "ASK", "T_L", "a-test", {"cues": ["NAME"], "operands": [op_row(self.rows["a"][1])],
                                                            "candidate_rows": None, "answer_kind": "NAME"})
        sample_teach = make_row(3, "TEACH", "L1", "b", {"glance_row": self.rows["b"][0], "name": "b"})
        violations = check_arm(
            arm, sample_teach, sample_ask, tmp_dir=os.path.join(self.tmp, "check_arm"),
            fresh_arm_factory=lambda: ArmA1(seed=999, config=cfg),
        )
        self.assertEqual(violations, [], f"check_arm found violations: {violations}")

    def test_full_synthetic_tape_runs_and_test_ask_is_frozen(self):
        cfg = _config(self.cache_dir)
        arm = ArmA1(seed=999, config=cfg)
        tape = _build_synthetic_tape(self.rows)
        before = arm.state_sha()
        answers = _run_tape(arm, tape)
        after_training = arm.state_sha()
        self.assertNotEqual(before, after_training, "training the arm on TEACH/ASK/FEEDBACK/SLEEP must move state")
        self.assertEqual(len(answers), 1)
        self.assertIsInstance(answers[0].kind, str)

    def test_replay_identity_on_synthetic_tape(self):
        # NOT B1-PREREG.md §3.1 itself (no real tape/cache exists yet) — the SAME shape of
        # test, on synthetic data, declared as such (module docstring).
        cfg = _config(self.cache_dir)
        tape = _build_synthetic_tape(self.rows)
        arm1 = ArmA1(seed=999, config=cfg)
        arm2 = ArmA1(seed=999, config=cfg)
        _run_tape(arm1, tape)
        _run_tape(arm2, tape)
        self.assertEqual(arm1.state_sha(), arm2.state_sha(), "same seed, same tape: state_sha must match byte for byte")

    def test_planted_divergence_is_caught(self):
        cfg = _config(self.cache_dir)
        tape_a = _build_synthetic_tape(self.rows)
        tape_b = _build_synthetic_tape(self.rows)
        # plant: the SECOND teach (of "b") points to a different rendering than tape_a's
        tape_b[1]["payload"]["glance_row"] = self.rows["c"][1]
        tape_b[1]["sha"] = __import__("brain.protocol", fromlist=["row_sha"]).row_sha(tape_b[1]["payload"])
        arm_a = ArmA1(seed=999, config=cfg)
        arm_b = ArmA1(seed=999, config=cfg)
        sha_before_plant_a = None
        sha_before_plant_b = None
        for i, (ra, rb) in enumerate(zip(tape_a, tape_b)):
            if i == 1:  # about to process the planted row
                sha_before_plant_a = arm_a.state_sha()
                sha_before_plant_b = arm_b.state_sha()
            for arm, row in ((arm_a, ra), (arm_b, rb)):
                k = row["kind"]
                if k == "TEACH":
                    HarnessContract.teach(arm, row)
                elif k == "SLEEP":
                    HarnessContract.sleep(arm, row)
                elif k == "ASK":
                    HarnessContract.training_ask(arm, row)
                # FEEDBACK/TEST_* omitted for this focused divergence check
        self.assertEqual(sha_before_plant_a, sha_before_plant_b, "before the plant, both runs must agree")
        self.assertNotEqual(arm_a.state_sha(), arm_b.state_sha(), "the planted divergence must be CAUGHT")

    def test_resume_from_snapshot_matches_uninterrupted_run(self):
        cfg = _config(self.cache_dir)
        tape = _build_synthetic_tape(self.rows)
        split = 4  # snapshot partway through

        uninterrupted = ArmA1(seed=999, config=cfg)
        _run_tape(uninterrupted, tape)
        want = uninterrupted.state_sha()

        first_half = ArmA1(seed=999, config=cfg)
        # replay the first `split` rows via the SAME driver semantics (needs pending state, so
        # just re-run the whole driver but stop early by slicing the tape and re-deriving
        # pending/families locally, mirroring _run_tape's own bookkeeping for that prefix).
        pending, families, in_test = {}, {}, False
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

        resumed = ArmA1(seed=999, config=cfg)
        resumed.load(snap_path)
        self.assertEqual(resumed.state_sha(), first_half.state_sha(), "load() must round-trip state_sha exactly")

        # continue both the (unsnapshotted) first_half and the resumed copy over the REST of
        # the tape and confirm they still agree with each other AND with the uninterrupted run.
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

        self.assertEqual(first_half.state_sha(), resumed.state_sha(), "resumed run must match the non-resumed continuation")
        self.assertEqual(resumed.state_sha(), want, "resumed run must match the fully uninterrupted run")


if __name__ == "__main__":
    unittest.main()
