# edit: Claude (Fable 5.1), 2026-09-22 10:29 +0400 — two reader marks corrected on the 2 h smokes of 2026-09-22 (six lives):
# (1) W3-1's bar «≤ 1 raw belief row per word» contradicts the clash law (genome/think.py decision 5: a genuine clash FIRST writes the
#     new observation as its own fresh `belief` row, then a `clash` row naming [standing, new]) — so every life that ever clashed fails
#     the bar by design (L4 max 2, L5/seam-1 max 4; all 24 extra rows on the six lives were the named second side of a clash row,
#     measured 2026-09-22 10:1x). The corrected bar: every belief row beyond the first for a word is NAMED as clashes[1] of a clash
#     row of that word — life 2's 1,473 unnamed rows still fail it.
# (2) (viii) COST compared STATUS.mind_ms_median_1min (the median of `mind.consume(row)` over EVERY tape row — ear, outcome, body
#     rows included) with the probe's ms per CANVAS (all rows' time ÷ canvases): different denominators (#162), so 0.168 ms ≤ 2 × 13 ms
#     passed in every life to date. The corrected mark reads STATUS.mind_ms_per_canvas_1min when the body writes it, and is NOT
#     GRADED (never PASS) on a status that carries only the per-row median.
from __future__ import annotations

import unittest

from tools import verdict_g4


def _belief(line, word, cells):
    return {"line": line, "kind": "belief", "word": word, "cells": cells, "episodes": [], "moment": 10 * line, "clashes": []}


class TestW3_1BeliefsBar(unittest.TestCase):
    DECL = {"BELIEF": {"clash": "opens"}}

    def test_a_second_belief_row_named_by_a_clash_row_passes(self) -> None:
        rows = [_belief(0, "diamond", [1, 2]), {"line": 1, "kind": "revisit", "word": "diamond", "of": 0},
                _belief(2, "diamond", [3, 4]), {"line": 3, "kind": "clash", "word": "diamond", "clashes": [0, 2], "moment": 30}]
        m = verdict_g4.w3_1_beliefs(rows, self.DECL, heard=["diamond"])
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m)
        self.assertEqual(m["extra_belief_rows"], 1); self.assertEqual(m["clash_rows"], 1); self.assertEqual(m["unaccounted"], [])
        self.assertEqual(m["max_belief_rows_per_word"], 2)

    def test_a_second_belief_row_with_no_clash_fails_and_is_named(self) -> None:
        """life 2's shape: the same belief re-filed with no clash (the dedupe defect D-G12) must still fail."""
        rows = [_belief(0, "ring", [1]), {"line": 1, "kind": "revisit", "word": "ring", "of": 0}, _belief(2, "ring", [1])]
        m = verdict_g4.w3_1_beliefs(rows, self.DECL, heard=["ring"])
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"])
        self.assertEqual(m["unaccounted"], [["ring", 2]])

    def test_a_clash_naming_the_wrong_line_does_not_account_for_the_extra_row(self) -> None:
        rows = [_belief(0, "bar", [1]), {"line": 1, "kind": "revisit", "word": "bar", "of": 0}, _belief(2, "bar", [5]),
                {"line": 3, "kind": "clash", "word": "bar", "clashes": [0, 1], "moment": 30}]
        m = verdict_g4.w3_1_beliefs(rows, self.DECL, heard=["bar"])
        self.assertFalse(m["pass"]); self.assertEqual(m["unaccounted"], [["bar", 2]])

    def test_not_declared_is_not_graded(self) -> None:
        m = verdict_g4.w3_1_beliefs([_belief(0, "bar", [1])], {}, heard=["bar"])
        self.assertFalse(m["graded"])


class TestCostMarkUnits(unittest.TestCase):
    def test_per_canvas_field_within_two_times_solo_passes(self) -> None:
        st = {"rss_mb": 400.0, "mind_ms_median_1min": 0.17, "mind_ms_per_canvas_1min": 20.0}
        m = verdict_g4.viii_cost(st, solo_ms=13.0, unblinded_ms=39.0, cpu_ns=None)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"]); self.assertEqual(m["live_ms_per_canvas"], 20.0)

    def test_per_canvas_field_over_two_times_solo_fails(self) -> None:
        st = {"rss_mb": 400.0, "mind_ms_median_1min": 0.17, "mind_ms_per_canvas_1min": 40.0}
        m = verdict_g4.viii_cost(st, solo_ms=13.0, unblinded_ms=39.0, cpu_ns=None)
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"])

    def test_a_status_with_only_the_per_row_median_is_not_graded(self) -> None:
        """every life before 2026-09-22 wrote only the per-row median: the mark must read NOT GRADED, never PASS (#162)."""
        st = {"rss_mb": 400.0, "mind_ms_median_1min": 0.17}
        m = verdict_g4.viii_cost(st, solo_ms=13.0, unblinded_ms=39.0, cpu_ns=None)
        self.assertFalse(m["graded"]); self.assertIsNone(m["pass"]); self.assertIn("per-row", m["reason"])

    def test_rss_over_two_gb_fails_whatever_the_speed(self) -> None:
        st = {"rss_mb": 2100.0, "mind_ms_median_1min": 0.17, "mind_ms_per_canvas_1min": 5.0}
        m = verdict_g4.viii_cost(st, solo_ms=13.0, unblinded_ms=39.0, cpu_ns=None)
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"])


if __name__ == "__main__":
    unittest.main()
