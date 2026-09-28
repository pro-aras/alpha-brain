# edit: Claude (Opus 5.5), 2026-09-26 17:32 +0400 — PREREG §5.5 (0a): «Both apply to every arm that learns cues; A0 and
# RING-READ answer no relation cue by design — for them (0a)/(0a′) read NOT APPLICABLE, named.» The grader graded them for
# every arm, so A0 (and its twins) and RING-READ read CONST 0.0 / SAME 0.0 as FAILED controls on both seeds
# (SEAT-DECISIONS R38). These pin the declared reading; the arm that learns cues is still graded (the control can fail).
from __future__ import annotations

import unittest

from brain.harness import graders as G


def _record(arm: str, const_correct: bool, same_equal: bool):
    answers = []
    for i in range(20):
        answers.append({"sitting": "T_L", "family": "CONTROL_CONST", "item": f"const:{i}", "correct": const_correct,
                        "answer": {"kind": "NAME", "value": "a" if const_correct else "b"}})
        ref = {"kind": "NAME", "value": f"n{i}"}
        answers.append({"sitting": "T_L", "family": "SAME_NAME_REF", "item": f"ref:{i}:same-ref", "correct": True, "answer": ref})
        answers.append({"sitting": "T_L", "family": "CONTROL_SAME", "item": f"same:{i}", "correct": same_equal,
                        "answer": ref if same_equal else {"kind": "NOTHING", "value": None}})
    return {"answers": answers, "sittings": {}, "summary": {"arm": arm}, "why": [], "rules": [], "missing": []}


class TestControlsNotApplicable(unittest.TestCase):
    def test_a0_and_ring_read_read_not_applicable(self) -> None:
        for arm in ("A0", "RING-READ", "SHUFFLED-NAME:A0", "FORCED:A0"):
            m = G.grade_controls(_record(arm, False, False))
            for k in ("C0a_CONST", "C0a_SAME"):
                self.assertFalse(m[k]["graded"], (arm, k))
                self.assertEqual(m[k]["reason_code"], "NOT_APPLICABLE", (arm, k))
            part = G.partition({k: m[k] for k in ("C0a_CONST", "C0a_SAME")})
            self.assertEqual(part["failed"], [], arm)

    def test_an_arm_that_learns_cues_is_still_graded(self) -> None:
        """Negative control: the same failing answers FAIL for an arm that learns cues."""
        for arm in ("A1", "D", "E′", "F", "A5"):
            m = G.grade_controls(_record(arm, False, False))
            self.assertTrue(m["C0a_CONST"]["graded"], arm)
            self.assertFalse(m["C0a_CONST"]["pass"], arm)
            self.assertFalse(m["C0a_SAME"]["pass"], arm)

    def test_passing_answers_still_pass(self) -> None:
        m = G.grade_controls(_record("A1", True, True))
        self.assertTrue(m["C0a_CONST"]["pass"])
        self.assertTrue(m["C0a_SAME"]["pass"])


if __name__ == "__main__":
    unittest.main()
