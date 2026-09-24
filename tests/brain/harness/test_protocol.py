# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:2x +0400 — tests for brain/protocol.py, the FIRST
# thing built for B1 (docs/brain/B1-PREREG.md §9 row 1: "write it, test it with a dummy arm, COMMIT it
# FIRST"). Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/tmp nice -n 19
# /data/dev/venvs/brain/bin/python -m unittest discover -s tests/brain/harness -t . -v
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from brain.protocol import (
    ANSWER_KIND_FAMILIES, Answer, AnswerKind, CUE_MARKS, EXAMPLE_ROWS, HarnessContract, ProtocolError,
    RELATION_CUES, TAPE_KINDS, VALENCE_NO, VALENCE_REWARD, canonical_json, check_arm, has_rule, has_why,
    is_name_operand, is_row_operand, make_arm, make_row, op_name, op_row, right_matches, row_sha,
    validate_tape_row, verify_row,
)
from brain.harness.dummy_arm import DummyArm


class TestCueVocabulary(unittest.TestCase):
    def test_fourteen_marks(self) -> None:
        self.assertEqual(len(CUE_MARKS), 14, CUE_MARKS)
        self.assertEqual(len(set(CUE_MARKS)), 14, "duplicate cue mark")

    def test_relation_cues_excludes_naming(self) -> None:
        self.assertNotIn("NAME", RELATION_CUES)
        self.assertNotIn("POINT", RELATION_CUES)
        self.assertNotIn("IS", RELATION_CUES)
        self.assertEqual(len(RELATION_CUES), 11)


class TestOperands(unittest.TestCase):
    def test_row_operand_roundtrip(self) -> None:
        op = op_row(7)
        self.assertTrue(is_row_operand(op))
        self.assertFalse(is_name_operand(op))
        self.assertEqual(op["value"], 7)

    def test_name_operand_roundtrip(self) -> None:
        op = op_name("a")
        self.assertTrue(is_name_operand(op))
        self.assertFalse(is_row_operand(op))
        self.assertEqual(op["value"], "a")


class TestTapeRows(unittest.TestCase):
    def test_example_rows_cover_every_kind(self) -> None:
        self.assertEqual(set(EXAMPLE_ROWS), set(TAPE_KINDS))

    def test_example_rows_validate_and_verify(self) -> None:
        for kind, row in EXAMPLE_ROWS.items():
            with self.subTest(kind=kind):
                validate_tape_row(row)   # must not raise
                self.assertTrue(verify_row(row))

    def test_verify_row_catches_planted_corruption(self) -> None:
        for kind, row in EXAMPLE_ROWS.items():
            with self.subTest(kind=kind):
                corrupt = copy.deepcopy(row)
                # flip one byte's worth of meaning in the payload without touching `sha`.
                if "seq" in corrupt.get("payload", {}):
                    corrupt["payload"]["seq"] = corrupt["payload"].get("seq", 0) + 1
                else:
                    corrupt["payload"]["_planted"] = True
                self.assertFalse(verify_row(corrupt), f"{kind}: planted corruption was not caught")

    def test_make_row_rejects_unknown_kind(self) -> None:
        with self.assertRaises(ProtocolError):
            make_row(1, "BOGUS", "L1", "x", {})

    def test_row_sha_is_deterministic_and_order_independent(self) -> None:
        a = row_sha({"a": 1, "b": 2})
        b = row_sha({"b": 2, "a": 1})
        self.assertEqual(a, b)

    def test_validate_rejects_unknown_cue(self) -> None:
        bad = make_row(1, "ASK", "L4", "x", {
            "cues": ["ZORTCH"], "operands": [op_row(0)], "candidate_rows": None, "answer_kind": "NAME"})
        with self.assertRaises(ProtocolError):
            validate_tape_row(bad)

    def test_validate_rejects_name_operand_on_relation_cue(self) -> None:
        bad = make_row(1, "ASK", "L4", "x", {
            "cues": ["AFTER"], "operands": [op_name("a")], "candidate_rows": None, "answer_kind": "NAME"})
        with self.assertRaises(ProtocolError):
            validate_tape_row(bad)

    def test_validate_rejects_missing_name_operand_on_point(self) -> None:
        bad = make_row(1, "ASK", "L4", "x", {
            "cues": ["POINT"], "operands": [op_row(0)], "candidate_rows": [1, 2, 3, 4], "answer_kind": "PICK"})
        with self.assertRaises(ProtocolError):
            validate_tape_row(bad)

    def test_validate_accepts_is_with_both_operand_kinds(self) -> None:
        ok = make_row(1, "ASK", "L4", "x", {
            "cues": ["IS"], "operands": [op_name("a"), op_row(3)], "candidate_rows": None, "answer_kind": "YESNO"})
        validate_tape_row(ok)   # must not raise

    def test_validate_rejects_pick_without_candidates(self) -> None:
        bad = make_row(1, "ASK", "L4", "x", {
            "cues": ["POINT"], "operands": [op_name("a")], "candidate_rows": None, "answer_kind": "PICK"})
        with self.assertRaises(ProtocolError):
            validate_tape_row(bad)


class TestAnswer(unittest.TestCase):
    def test_pick_requires_int_value(self) -> None:
        with self.assertRaises(ProtocolError):
            Answer(kind=AnswerKind.PICK, value="not-an-int")
        Answer(kind=AnswerKind.PICK, value=2)   # must not raise

    def test_name_requires_str_value(self) -> None:
        with self.assertRaises(ProtocolError):
            Answer(kind=AnswerKind.NAME, value=3)
        Answer(kind=AnswerKind.NAME, value="a")   # must not raise

    def test_unknown_kind_rejected(self) -> None:
        with self.assertRaises(ProtocolError):
            Answer(kind="MAYBE")

    def test_to_dict_from_dict_roundtrip(self) -> None:
        a = Answer(kind=AnswerKind.RESEMBLES, value="b", raw={"cos": 0.9})
        b = Answer.from_dict(a.to_dict())
        self.assertEqual(a, b)
        # and the dict itself must be JSON-canonical-serialisable (crosses a pipe/log file intact).
        canonical_json(a.to_dict())


class TestRightMatches(unittest.TestCase):
    def test_name_match_and_mismatch(self) -> None:
        self.assertTrue(right_matches("NAME", Answer(kind=AnswerKind.NAME, value="b"), "b"))
        self.assertFalse(right_matches("NAME", Answer(kind=AnswerKind.NAME, value="c"), "b"))

    def test_pick_match_by_index(self) -> None:
        self.assertTrue(right_matches("PICK", Answer(kind=AnswerKind.PICK, value=2), 2))
        self.assertFalse(right_matches("PICK", Answer(kind=AnswerKind.PICK, value=1), 2))

    def test_yesno_match(self) -> None:
        self.assertTrue(right_matches("YESNO", Answer(kind=AnswerKind.YES), "YES"))
        self.assertFalse(right_matches("YESNO", Answer(kind=AnswerKind.YES), "NO"))

    def test_abstentions_never_match(self) -> None:
        for kind in (AnswerKind.UNKNOWN, AnswerKind.NOTHING, AnswerKind.SILENT):
            self.assertFalse(right_matches("NAME", Answer(kind=kind), "anything"))


def _config(tmp: Path) -> Dict[str, Any]:
    return {"cache_dir": str(tmp / "cache"), "run_dir": str(tmp / "run"), "seed": 20261001, "interpreter": "venv"}


def _name_ask(row: int, seq: int = 100) -> Dict[str, Any]:
    return make_row(seq, "ASK", "T_L", "probe", {
        "cues": ["NAME"], "operands": [op_row(row)], "candidate_rows": None, "answer_kind": "NAME"})


class TestDummyArmAndCheckArm(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_honest_dummy_passes_check_arm(self) -> None:
        cfg = _config(self.tmp)
        arm = make_arm(DummyArm, 20261001, cfg)
        HarnessContract.teach(arm, make_row(1, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"}))
        violations = check_arm(
            arm,
            sample_teach_row=make_row(2, "TEACH", "L1", "b", {"glance_row": 1, "name": "b"}),
            sample_ask_row=_name_ask(row=0),
            tmp_dir=self.tmp / "check1",
            fresh_arm_factory=lambda: make_arm(DummyArm, 20261001, cfg),
        )
        self.assertEqual(violations, [], violations)

    def test_dummy_arm_recalls_a_taught_row(self) -> None:
        arm = make_arm(DummyArm, 1, _config(self.tmp))
        HarnessContract.teach(arm, make_row(1, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"}))
        ans = HarnessContract.test_ask(arm, _name_ask(row=0))
        self.assertEqual(ans.kind, AnswerKind.NAME)
        self.assertEqual(ans.value, "a")

    def test_dummy_arm_abstains_on_untaught_row(self) -> None:
        arm = make_arm(DummyArm, 1, _config(self.tmp))
        ans = HarnessContract.test_ask(arm, _name_ask(row=99))
        self.assertEqual(ans.kind, AnswerKind.UNKNOWN)

    def test_dummy_arm_has_no_road_for_relations(self) -> None:
        arm = make_arm(DummyArm, 1, _config(self.tmp))
        ask = make_row(1, "ASK", "L4", "x", {
            "cues": ["AFTER"], "operands": [op_row(0)], "candidate_rows": None, "answer_kind": "NAME"})
        ans = HarnessContract.test_ask(arm, ask)
        self.assertEqual(ans.kind, AnswerKind.NOTHING)

    def test_check_arm_catches_a_mutating_dummy(self) -> None:
        """#228's law: a test ships with a control that must FAIL. A dummy that secretly mutates its own
        state inside answer(learn=False) must be CAUGHT by check_arm, never waved through."""
        cfg = _config(self.tmp)

        class MutatingDummyArm(DummyArm):
            def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
                # cheat: remember something even when learn=False, which state_sha() will reflect.
                self._heard.setdefault("__leaked__", []).append(len(self._heard))
                return super().answer(ask_row, learn=learn)

        arm = make_arm(MutatingDummyArm, 1, cfg)
        violations = check_arm(
            arm,
            sample_teach_row=make_row(2, "TEACH", "L1", "b", {"glance_row": 1, "name": "b"}),
            sample_ask_row=_name_ask(row=0),
            tmp_dir=self.tmp / "check2",
            fresh_arm_factory=lambda: make_arm(MutatingDummyArm, 1, cfg),
        )
        self.assertTrue(violations, "check_arm must catch a dummy that mutates under learn=False")
        self.assertTrue(any("state_sha" in v for v in violations), violations)

    def test_snapshot_load_roundtrip(self) -> None:
        cfg = _config(self.tmp)
        arm = make_arm(DummyArm, 1, cfg)
        HarnessContract.teach(arm, make_row(1, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"}))
        path = self.tmp / "snap.json"
        arm.snapshot(path)
        fresh = make_arm(DummyArm, 1, cfg)
        fresh.load(path)
        self.assertEqual(arm.state_sha(), fresh.state_sha())

    def test_cost_accumulates(self) -> None:
        arm = make_arm(DummyArm, 1, _config(self.tmp))
        c0 = arm.cost()
        HarnessContract.teach(arm, make_row(1, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"}))
        c1 = arm.cost()
        self.assertGreater(c1["events"], c0["events"])

    def test_has_why_has_rule_false_for_dummy(self) -> None:
        arm = make_arm(DummyArm, 1, _config(self.tmp))
        self.assertFalse(has_why(arm))
        self.assertFalse(has_rule(arm))


class TestHarnessContractTrainingFeedback(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_reward_when_right_no_when_wrong(self) -> None:
        arm = make_arm(DummyArm, 1, _config(self.tmp))
        HarnessContract.teach(arm, make_row(1, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"}))
        ask = make_row(2, "ASK", "L4", "a", {
            "cues": ["NAME"], "operands": [op_row(0)], "candidate_rows": None, "answer_kind": "NAME"})
        ans = HarnessContract.training_ask(arm, ask)
        self.assertEqual(ans.value, "a")
        fb_right = make_row(3, "FEEDBACK", "L4", "a", {"ask_seq": 2, "right": "a"})
        v = HarnessContract.feedback(arm, fb_right, ans, "NAME")
        self.assertEqual(v, VALENCE_REWARD)

        ask2 = make_row(4, "ASK", "L4", "unseen", {
            "cues": ["NAME"], "operands": [op_row(999)], "candidate_rows": None, "answer_kind": "NAME"})
        ans2 = HarnessContract.training_ask(arm, ask2)
        self.assertEqual(ans2.kind, AnswerKind.UNKNOWN)
        fb_wrong = make_row(5, "FEEDBACK", "L4", "unseen", {"ask_seq": 4, "right": "z"})
        v2 = HarnessContract.feedback(arm, fb_wrong, ans2, "NAME")
        self.assertEqual(v2, VALENCE_NO)

    def test_test_ask_raises_on_state_drift(self) -> None:
        class DriftingArm(DummyArm):
            def answer(self, ask_row, learn: bool = False) -> Answer:
                self._heard.setdefault("__drift__", []).append(1)
                return super().answer(ask_row, learn=learn)

        arm = make_arm(DriftingArm, 1, _config(self.tmp))
        with self.assertRaises(ProtocolError):
            HarnessContract.test_ask(arm, _name_ask(row=0))


if __name__ == "__main__":
    unittest.main()
