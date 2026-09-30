# edit: Claude (Fable 5.1, the seat), 2026-09-30 10:3x +0400 — PREREG-HEARS-2 §1 / §2 X: the grader's test 4a reads EXIST by ANY hand (a cited moment of
# the maker exists when its eye row is on the tape and the word among its ear rows), CARRY and its null over the cited episodes
# that have a TRUTH, the count cited by world beside them; the planted control: a citation of a moment on no tape reads EXIST < 1.
"""tests/tools/test_grade_exist_any_hand.py — tools/brain/grade_life.py:grade_m4a on a stub life of two hands (no truth files: the
scene-cited path is the scored record's own and is pinned by the days life's grade, unchanged but for the two new keys)."""
from __future__ import annotations

import collections
import unittest

from tools.brain import grade_life as G


class _Life:
    """The fields grade_m4a reads, and nothing else."""

    def __init__(self, cited):
        self.ws = 20261101
        self.asks = {f"M4:{w}": {"form": "why", "word": w, "_seq": i} for i, w in enumerate(sorted({c[0] for c in cited}))}
        by_word = collections.defaultdict(list)
        for w, m, hyps in cited:
            by_word[w].append({"moment": m, "scene": 0, "hyp": 0, "pos": [1.0, 1.0], "fix": [[1, 1], [9, 9]], "hyps": hyps})
        self.answer_of = {f"M4:{w}": {"answer": {"kind": "because", "word": w, "episodes": eps}} for w, eps in by_word.items()}
        self.moment_eye = {}                    # no scene training moment among the cited (no truth needed)
        self.moment_words = collections.defaultdict(list)
        self.moment_eye_any = {"w0000i000003t000000003": {"seq": 3}, "w0000i000007t000000007": {"seq": 7}}
        self.moment_words_any = collections.defaultdict(list, {"w0000i000003t000000003": ["star"], "w0000i000007t000000007": ["bar"]})
        self.moment_world = {"w0000i000003t000000003": "maker", "w0000i000007t000000007": "maker"}

    def truth_of_eye(self, eye):
        raise AssertionError("no scene-cited episode here: the truth must not be asked for")


class ExistByAnyHand(unittest.TestCase):
    def test_a_makers_memory_exists_and_is_counted_by_world_and_carry_has_no_population(self) -> None:
        life = _Life([("star", "w0000i000003t000000003", [[0], [1]]), ("bar", "w0000i000007t000000007", [[0], [1]])])
        a = G.grade_m4a(life)
        self.assertEqual(a["n_cited"], 2)
        self.assertEqual(a["exist"], 1.0)
        self.assertEqual(a["cited_by_world"], {"maker": 2})
        self.assertEqual(a["n_with_truth"], 0)
        self.assertIsNone(a["carry"])
        self.assertEqual(a["null_carry"], [None] * G.M4_TWIN_DRAWS)

    def test_the_planted_control_a_moment_on_no_tape_reads_exist_under_one(self) -> None:
        life = _Life([("star", "w0000i000003t000000003", [[0], [1]]), ("star", "nowhere-on-any-tape", [[0], [1]])])
        a = G.grade_m4a(life)
        self.assertEqual(a["n_cited"], 2)
        self.assertEqual(a["exist"], 0.5)
        self.assertEqual(a["cited_by_world"], {"?": 1, "maker": 1})

    def test_a_makers_moment_without_the_word_among_its_ear_rows_does_not_exist_for_that_word(self) -> None:
        life = _Life([("bar", "w0000i000003t000000003", [[0], [1]])])       # the moment heard «star», not «bar»
        a = G.grade_m4a(life)
        self.assertEqual(a["exist"], 0.0)


if __name__ == "__main__":
    unittest.main()
