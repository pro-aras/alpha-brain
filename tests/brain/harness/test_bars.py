# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 19:1x +0400 — tests for brain/harness/bars.py. Pure
# logic, no rendering — runs under either interpreter.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brain.harness.bars import (
    BarsError, assert_bars_not_moved_after_grading, binomial_half_width_95, ceilings_sha256, is_not_gradable,
    validate_bar, validate_bars_line,
)


def _entry(max_ceiling: float, n: int, k_min: int) -> dict:
    return {"organ_ceiling": {"nn": max_ceiling, "linear": max_ceiling, "max": max_ceiling}, "n": n, "k_min": k_min}


class TestIsNotGradable(unittest.TestCase):
    def test_high_ceiling_is_gradable(self) -> None:
        self.assertFalse(is_not_gradable(_entry(0.95, 100, 4)))

    def test_ceiling_at_the_floor_is_not_gradable(self) -> None:
        # k_min/n = 4/100 = 0.04; a ceiling of 0.05 is inside the binomial band of that floor.
        self.assertTrue(is_not_gradable(_entry(0.05, 100, 4)))


class TestValidateBar(unittest.TestCase):
    def test_accepts_a_bar_between_floor_and_ceiling(self) -> None:
        validate_bar("X", _entry(0.9, 100, 4), 0.7)   # must not raise

    def test_rejects_bar_above_ceiling(self) -> None:
        with self.assertRaises(BarsError):
            validate_bar("X", _entry(0.9, 100, 4), 0.95)

    def test_rejects_bar_below_k_min_over_n(self) -> None:
        with self.assertRaises(BarsError):
            validate_bar("X", _entry(0.9, 100, 4), 0.01)

    def test_rejects_any_bar_on_a_not_gradable_family(self) -> None:
        with self.assertRaises(BarsError):
            validate_bar("X", _entry(0.05, 100, 4), 0.045)


class TestValidateBarsLine(unittest.TestCase):
    def test_missing_family_raises(self) -> None:
        with self.assertRaises(BarsError):
            validate_bars_line({}, {"X": 0.5})

    def test_valid_line(self) -> None:
        ceilings = {"X": _entry(0.9, 100, 4), "Y": _entry(0.8, 50, 3)}
        out = validate_bars_line(ceilings, {"X": 0.7, "Y": 0.6})
        self.assertEqual(set(out), {"X", "Y"})
        self.assertEqual(out["X"]["ceiling"], 0.9)


class TestCeilingsSha(unittest.TestCase):
    def test_reproducible_and_sensitive_to_a_byte(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ceilings.json"
            p.write_text('{"a": 1}')
            sha1 = ceilings_sha256(p)
            self.assertEqual(sha1, ceilings_sha256(p))
            p.write_text('{"a": 2}')
            self.assertNotEqual(sha1, ceilings_sha256(p))


class TestBarsNotMovedAfterGrading(unittest.TestCase):
    def test_none_first_graded_is_always_fine(self) -> None:
        assert_bars_not_moved_after_grading("2026-09-24T18:00:00Z", None)

    def test_declared_before_grading_is_fine(self) -> None:
        assert_bars_not_moved_after_grading("2026-09-24T18:00:00Z", "2026-09-24T19:00:00Z")

    def test_declared_after_grading_raises(self) -> None:
        with self.assertRaises(BarsError):
            assert_bars_not_moved_after_grading("2026-09-24T20:00:00Z", "2026-09-24T19:00:00Z")


if __name__ == "__main__":
    unittest.main()


class TestCostBoundRule(unittest.TestCase):
    """edit: Claude (Opus 5.5), 2026-09-26 12:07 +0400 — the seat's COST rule (bars_line.py docstring): 8 wall-hours for one
    world-day of alpha4-1's body (93,652 rows) = 307.521 ms per event, whatever the solo probe says about A0; the draft
    3 × A0 is carried beside it as the counterfactual, never as the bar."""

    def test_cost_bar_is_the_body_rule_not_three_times_a0(self) -> None:
        from brain.harness import bars_line as BL
        solo = {"probes": {"A0": {"ms_per_event_arm": 1.595}, "A1-H64": {"ms_per_event_arm": 11.451},
                           "A1-H512": {"ms_per_event_arm": 33.973}}}
        out = BL.build({"families": {}}, solo)
        self.assertEqual(out["bars"]["COST"], round(8.0 * 3600 * 1000 / 93652, 3))
        self.assertEqual(out["bars"]["COST"], 307.521)
        cf = out["detail"]["COST"]["counterfactual"]
        self.assertEqual(cf["value"], 4.785)
        self.assertGreater(cf["a1_h64_ms"], cf["value"], "the counterfactual's reason: A1 at H 64 exceeds 3 × A0")
        self.assertIn("NOT used", out["line"])

    def test_cost_bar_needs_no_probe(self) -> None:
        from brain.harness import bars_line as BL
        self.assertEqual(BL.build({"families": {}}, None)["bars"]["COST"], 307.521)
