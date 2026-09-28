# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 18:0x +0400 — tests for brain/harness/identity.py +
# identity_worker.py: real subprocesses, a synthetic tape, DummyArm (must PASS) and a planted
# non-deterministic arm (must be CAUGHT, #228's law). Uses /usr/bin/python3 (DummyArm needs no torch); the
# framework is interpreter-agnostic (identity_worker.py's torch pinning is guarded by ImportError).
from __future__ import annotations

import random
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Mapping

from brain.harness.identity import IdentityError, identity_test, plant_divergence, write_tape_jsonl
from brain.harness.dummy_arm import DummyArm
from brain.protocol import Answer, AnswerKind, make_row, op_row

REPO_ROOT = Path(__file__).resolve().parents[3]
PYTHON = Path(sys.executable)   # the interpreter running THIS test — DummyArm needs no torch either way


def _synthetic_tape(n_letters: int = 40) -> list:
    """A small, self-contained TEACH/ASK/FEEDBACK/SLEEP tape DummyArm can answer meaningfully (NAME only —
    every other cue reads NOTHING, which is fine for an identity test: determinism, not semantics, is what
    is being checked)."""
    rows = []
    seq = 1
    letters = [chr(ord("a") + i) for i in range(n_letters)]
    for i, letter in enumerate(letters):
        rows.append(make_row(seq, "TEACH", "L1", letter, {"glance_row": i, "name": letter})); seq += 1
        ask = make_row(seq, "ASK", "L4", letter, {"cues": ["NAME"], "operands": [op_row(i)],
                                                    "candidate_rows": None, "answer_kind": "NAME"}); seq += 1
        rows.append(ask)
        rows.append(make_row(seq, "FEEDBACK", "L4", letter, {"ask_seq": ask["seq"], "right": letter})); seq += 1
        if (i + 1) % 10 == 0:
            rows.append(make_row(seq, "SLEEP", "L1", "-", {"steps": 5})); seq += 1
    return rows


class TestPlantDivergence(unittest.TestCase):
    def test_only_the_targeted_row_changes(self) -> None:
        tape = _synthetic_tape(10)
        diverged = plant_divergence(tape, at_or_after_event=5, new_glance_row=777)
        changed = [i for i, (a, b) in enumerate(zip(tape, diverged)) if a != b]
        self.assertEqual(len(changed), 1)
        row = diverged[changed[0]]
        self.assertEqual(row["payload"]["glance_row"], 777)
        self.assertGreaterEqual(row["seq"], 5)
        self.assertEqual(row["kind"], "TEACH")

    def test_raises_when_no_teach_row_in_range(self) -> None:
        tape = _synthetic_tape(2)
        with self.assertRaises(IdentityError):
            plant_divergence(tape, at_or_after_event=10_000, new_glance_row=1)


class TestIdentityTestWithDummyArm(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.out_dir = Path(self._tmp.name)
        self.tape = _synthetic_tape(40)   # 40*3 + 4 sleeps = 124 rows

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_honest_dummy_arm_passes_the_whole_identity_test(self) -> None:
        report = identity_test(
            PYTHON, REPO_ROOT, "brain.harness.dummy_arm", "DummyArm", seed=1, config={},
            tape_rows=self.tape, out_dir=self.out_dir,
            checkpoints=(30, 60, 90, 120), n_events=120, plant_at_event=61, planted_row=999999,
            run_8_threads=True,
        )
        self.assertTrue(report["twice"]["answers_match"], report)
        self.assertTrue(report["twice"]["state_match"], report)
        self.assertTrue(report["planted_divergence"]["early_unchanged"], report)
        self.assertTrue(report["planted_divergence"]["late_diverged"], report)
        self.assertTrue(report["resume"]["ok"], report)
        self.assertTrue(report["pass"], report)


class TestIdentityTestCatchesNonDeterminism(unittest.TestCase):
    """#228's law: a test ships with a control that must FAIL. A dummy arm that folds an UNSEEDED random
    draw into its own state must be CAUGHT by the "twice" check — two honest runs of a deterministic
    protocol implementation must never need this, but the FRAMEWORK must notice if one ever did."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.out_dir = Path(self._tmp.name)
        self.tape = _synthetic_tape(10)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_nondeterministic_arm_fails_the_twice_check(self) -> None:
        report = identity_test(
            PYTHON, REPO_ROOT, "tests.brain.harness._nondeterministic_arm", "NonDeterministicArm",
            seed=1, config={}, tape_rows=self.tape, out_dir=self.out_dir,
            checkpoints=(10, 20, 30), n_events=30, plant_at_event=15, planted_row=999999,
            run_8_threads=False,
        )
        self.assertFalse(report["twice"]["state_match"], report)
        self.assertFalse(report["pass"], report)


if __name__ == "__main__":
    unittest.main()
