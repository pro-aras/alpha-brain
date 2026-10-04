"""PREREG-W2 (SIGNED x3) — the reference census's tests, written FIRST (red).

# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:08 +0400 — new file for the W2 build; law §3 item 3 (the
# reference census and its gate G-CENSUS: equal to the saved census at every calibration point, the planted byte caught).

  meeting_counts: per canvas, every word's meetings BEFORE the canvas (the m_before form, from the moment word lists
  alone). compare_saved: the gate against one saved census file — every word's meetings equal on BOTH sides
  (presence counts), the first difference named; a planted byte is CAUGHT and named.
"""
from __future__ import annotations

import unittest

from tools.toys.w2 import census as C

LISTS = [["cross"], ["cross", "red"], ["ring"], ["cross", "red", "cross"]]


class TestMeetingCounts(unittest.TestCase):
    def test_counts_before_each_canvas(self):
        counts = C.meeting_counts(LISTS)
        self.assertEqual(counts[0], {})
        self.assertEqual(counts[1], {"cross": 1})
        self.assertEqual(counts[2], {"cross": 2, "red": 1})
        self.assertEqual(counts[3], {"cross": 2, "red": 1, "ring": 1})
        self.assertEqual(counts[3]["cross"], 2)                          # the 4th canvas's own meetings never count early

    def test_meetings_at_a_calibration_point(self):
        counts = C.meeting_counts(LISTS)
        self.assertEqual(C.at(counts, 4), {"cross": 4, "red": 2, "ring": 1})


class TestCompareSaved(unittest.TestCase):
    def _saved(self):
        return {"words": {"cross": {"meetings": 4, "mature": True}, "red": {"meetings": 2, "mature": False},
                          "ring": {"meetings": 1, "mature": False}}}

    def test_matches_the_saved_census_with_presence_counts(self):
        out = C.compare_saved(LISTS, self._saved(), at=4)
        self.assertTrue(out["ok"])
        self.assertEqual(out["n_words"], 3)
        self.assertEqual(out["n_checked"], 3)                          # presence: words compared across both sides

    def test_a_planted_byte_is_caught_and_named(self):
        saved = self._saved()
        saved["words"]["cross"]["meetings"] = 99                       # the planted corruption
        out = C.compare_saved(LISTS, saved, at=4)
        self.assertFalse(out["ok"])
        self.assertEqual(out["first_diff"], ("cross", 4, 99))

    def test_a_word_missing_on_either_side_is_a_difference(self):
        saved = self._saved()
        saved["words"]["ghost"] = {"meetings": 4, "mature": True}
        out = C.compare_saved(LISTS, saved, at=4)
        self.assertFalse(out["ok"])
        self.assertEqual(out["n_checked"], 4)
        saved2 = self._saved()
        del saved2["words"]["ring"]
        out2 = C.compare_saved(LISTS, saved2, at=4)
        self.assertFalse(out2["ok"])
        self.assertEqual(out2["first_diff"][0], "ring")


if __name__ == "__main__":
    unittest.main()
