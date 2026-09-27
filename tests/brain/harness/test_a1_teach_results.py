# edit: Claude (Sonnet 5, A1-TEACH builder), 2026-09-27 13:55 +0400 — R46 (docs/brain/b1/SEAT-DECISIONS.md; brief
#   docs/dev/briefs/a1-teach.md, Tests item 7): A1-TEACH joins RELATION_TWINNED (a missing SHUFFLED-RELATION:A1-TEACH
#   reads TWIN_MISSING on its U3), and the `a1_teach` diagnostic decision reads U1a's own dict for A1-TEACH, A1 and
#   SHUFFLED-NAME:A1-TEACH — never through `_reading()`, which reads None for a dict (pinned here as the negative
#   control the brief names). Red on the old code: `RELATION_TWINNED` lacks "A1-TEACH" and `_decisions(...)` carries
#   no `a1_teach` key at all (`KeyError: 'a1_teach'`).
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brain.harness import graders as G
from brain.harness import results as R

U1A_BAR = {"latin-upper": 0.6692, "latin-lower": 0.7776}


def u1a_mark(upper: float, lower: float, passed: bool = False):
    reading = {"latin-upper": upper, "latin-lower": lower}
    return G._mark("U1a_NAME@T_L", reading=reading, graded=True, passed=passed, bar=dict(U1A_BAR), klass="U1")


def arm_with_u1a(upper: float, lower: float, passed: bool = False):
    marks = {"U1a_NAME@T_L": u1a_mark(upper, lower, passed)}
    return {"marks": marks, "partition": G.partition(marks)}


class TestA1TeachRelationTwinned(unittest.TestCase):
    def test_a1_teach_is_in_relation_twinned(self) -> None:
        self.assertIn("A1-TEACH", R.RELATION_TWINNED)

    def test_a1_teach_missing_twin_reads_twin_missing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="b1-a1teach-r44-") as d:
            gaps = R.missing_relation_twins(Path(d), ["A1-TEACH"])
        self.assertEqual(gaps["A1-TEACH"]["reason_code"], "TWIN_MISSING")
        self.assertEqual(gaps["A1-TEACH"]["by"], ["MISSING: no SHUFFLED-RELATION:A1-TEACH record"])

    def test_a1_teachs_own_twin_present_is_no_gap(self) -> None:
        with tempfile.TemporaryDirectory(prefix="b1-a1teach-r44-") as d:
            gaps = R.missing_relation_twins(Path(d), ["A1-TEACH", "SHUFFLED-RELATION:A1-TEACH"])
        self.assertEqual(gaps, {})


class TestU1aReadingHelper(unittest.TestCase):
    """U1a's reading is a DICT {case: share} (graders.grade_u1a) — `_reading()` (float-or-None) reads None for
    it; `_u1a_reading()` must read the dict directly."""

    def test_u1a_reading_returns_the_planted_dict(self) -> None:
        arms = {"A1": arm_with_u1a(0.04, 0.03)}
        self.assertEqual(R._u1a_reading(arms, "A1"), {"latin-upper": 0.04, "latin-lower": 0.03})

    def test_reading_would_have_read_none_the_bug_this_avoids(self) -> None:
        arms = {"A1": arm_with_u1a(0.04, 0.03)}
        self.assertIsNone(R._reading(arms, "A1", "U1a_NAME@T_L"))

    def test_u1a_reading_is_none_for_a_missing_arm(self) -> None:
        self.assertIsNone(R._u1a_reading({}, "A1-TEACH"))

    def test_u1a_reading_is_none_when_the_mark_is_absent(self) -> None:
        self.assertIsNone(R._u1a_reading({"A1-TEACH": {"marks": {}}}, "A1-TEACH"))


class TestA1TeachDiagnosticDecision(unittest.TestCase):
    """The `a1_teach` decision (R46: a DIAGNOSTIC — decides nothing by itself, §6's selection never reads it)."""

    def test_computed_on_planted_marks_for_all_three_arms(self) -> None:
        arms = {
            "A1-TEACH": arm_with_u1a(0.50, 0.40),
            "A1": arm_with_u1a(0.04, 0.03),
            "SHUFFLED-NAME:A1-TEACH": arm_with_u1a(0.04, 0.04),
        }
        d = R._decisions(arms, {})
        a1t = d["a1_teach"]
        self.assertTrue(a1t["computable"])
        self.assertEqual(a1t["u1a"]["A1-TEACH"], {"latin-upper": 0.50, "latin-lower": 0.40})
        self.assertEqual(a1t["u1a"]["A1"], {"latin-upper": 0.04, "latin-lower": 0.03})
        self.assertEqual(a1t["u1a"]["SHUFFLED-NAME:A1-TEACH"], {"latin-upper": 0.04, "latin-lower": 0.04})
        self.assertNotIn("missing", a1t)
        self.assertNotIn("void", a1t)

    def test_not_computable_when_an_arm_is_missing(self) -> None:
        arms = {"A1-TEACH": arm_with_u1a(0.50, 0.40)}
        d = R._decisions(arms, {})
        a1t = d["a1_teach"]
        self.assertFalse(a1t["computable"])
        self.assertIn("A1", a1t["missing"])
        self.assertIn("SHUFFLED-NAME:A1-TEACH", a1t["missing"])
        self.assertNotIn("A1-TEACH", a1t["missing"])

    def test_not_computable_when_an_arm_is_void(self) -> None:
        void_marks = {
            "C0a_SAME": G._mark("C0a_SAME", reading=0.3, graded=True, passed=False, klass="CONTROL"),
            "U1a_NAME@T_L": u1a_mark(0.50, 0.40),
        }
        arms = {
            "A1-TEACH": {"marks": void_marks, "partition": R.read_partition("A1-TEACH", void_marks)},
            "A1": arm_with_u1a(0.04, 0.03),
            "SHUFFLED-NAME:A1-TEACH": arm_with_u1a(0.04, 0.04),
        }
        d = R._decisions(arms, {})
        a1t = d["a1_teach"]
        self.assertFalse(a1t["computable"])
        self.assertIn("A1-TEACH", a1t["void"])

    def test_absent_entirely_reads_missing_all_three_without_crashing(self) -> None:
        d = R._decisions({"A5": arm_with_u1a(0.9, 0.9)}, {})
        a1t = d["a1_teach"]
        self.assertFalse(a1t["computable"])
        self.assertEqual(sorted(a1t["missing"]), sorted(["A1-TEACH", "A1", "SHUFFLED-NAME:A1-TEACH"]))
        self.assertEqual(a1t["u1a"], {})


class TestA1TeachVerdictRendering(unittest.TestCase):
    def _res(self, arms) -> dict:
        return {"seed": 1, "tape_sha": "0" * 64, "smoke": False, "bars_line": "x",
                "instrument": {"void": False, "key_present": True, "shifted_key_present": True, "key_graded_marks": 1,
                                "key_failed": [], "shifted_key_failed": ["U1"]},
                "arms": {n: {"marks": a["marks"], "partition": a["partition"], "cost": None, "size": None} for n, a in arms.items()},
                "decisions": R._decisions(arms, {})}

    def test_computable_line_renders(self) -> None:
        arms = {"A1-TEACH": arm_with_u1a(0.50, 0.40), "A1": arm_with_u1a(0.04, 0.03),
                "SHUFFLED-NAME:A1-TEACH": arm_with_u1a(0.04, 0.04)}
        text = R.render_verdict(self._res(arms))
        dec = text.split("## The decisions", 1)[1]
        self.assertIn("R46", dec)
        self.assertIn("0.5", dec)
        self.assertNotIn("NOT COMPUTABLE", dec.split("A1-TEACH", 1)[1].split("\n", 1)[0])

    def test_not_computable_line_renders_without_crashing(self) -> None:
        text = R.render_verdict(self._res({"A5": arm_with_u1a(0.9, 0.9)}))
        self.assertIn("NOT COMPUTABLE", text)


if __name__ == "__main__":
    unittest.main()
