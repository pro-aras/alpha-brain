"""test_park.py — B4: PARK (genome/park.py's Park) — metacognition's day-1 gene.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B4 (docs/G4-PREREG.md §3, docs/briefs/
G4-BUILDER-B-GENES.md): 3 identical reasons park; the 4th ask returns "parked" with no work; a different
reason does not count; reopen(want, "document") reopens, reopen(want, "same-sense") does not; state()
lists parked wants with reasons and counts.
"""
from __future__ import annotations

import unittest

from genome.park import Park


class TestPark(unittest.TestCase):
    def test_three_identical_reasons_park_the_fourth_is_free(self) -> None:
        p = Park(n=3)
        self.assertEqual(p.answer("skullcap~device", "no sense carries it"), "open")
        self.assertEqual(p.answer("skullcap~device", "no sense carries it"), "open")
        self.assertEqual(p.answer("skullcap~device", "no sense carries it"), "parked")
        # the 4th ask: parked, and no work — the counters must not move (state() proves it below)
        before = p.state()
        self.assertEqual(p.answer("skullcap~device", "no sense carries it"), "parked")
        after = p.state()
        self.assertEqual(before, after, "a parked want's ask must do no work")

    def test_a_different_reason_does_not_count_toward_n(self) -> None:
        p = Park(n=3)
        self.assertEqual(p.answer("w", "A"), "open")
        self.assertEqual(p.answer("w", "A"), "open")
        self.assertEqual(p.answer("w", "B"), "open")   # a different reason: its own counter, A's stays at 2
        self.assertNotIn("w", p.state()["parked"], "B must not have contributed to A's count")
        self.assertEqual(p.answer("w", "A"), "parked", "A's own 3rd occurrence parks it")
        self.assertEqual(p.state()["parked"]["w"]["reason"], "A")

    def test_reopen_document_reopens_same_sense_does_not(self) -> None:
        p = Park(n=3)
        for _ in range(3):
            p.answer("w", "no sense carries it")
        self.assertIn("w", p.state()["parked"])
        self.assertFalse(p.reopen("w", "same-sense"), "asking again with the same kind of evidence never reopens")
        self.assertIn("w", p.state()["parked"], "a refused reopen must leave the want parked")
        self.assertTrue(p.reopen("w", "document"), "a document naming the want reopens it")
        self.assertNotIn("w", p.state()["parked"])
        # reopened: it takes a fresh n dead-ends to park again
        self.assertEqual(p.answer("w", "no sense carries it"), "open")
        self.assertEqual(p.answer("w", "no sense carries it"), "open")

    def test_reopen_new_sense_also_reopens(self) -> None:
        p = Park(n=2)
        p.answer("w", "R"); p.answer("w", "R")
        self.assertIn("w", p.state()["parked"])
        self.assertTrue(p.reopen("w", "new-sense"))
        self.assertNotIn("w", p.state()["parked"])

    def test_reopen_a_never_parked_want_returns_false(self) -> None:
        p = Park(n=3)
        self.assertFalse(p.reopen("never-asked", "document"))

    def test_state_lists_parked_wants_with_reasons_and_counts(self) -> None:
        p = Park(n=2)
        p.answer("x", "no sense"); p.answer("x", "no sense")
        p.answer("y", "ambiguous"); p.answer("y", "ambiguous")
        st = p.state()
        self.assertEqual(st["total_parked"], 2)
        self.assertEqual(st["parked"]["x"], {"reason": "no sense", "count": 2})
        self.assertEqual(st["parked"]["y"], {"reason": "ambiguous", "count": 2})

    def test_park_refuses_n_below_1(self) -> None:
        with self.assertRaises(ValueError):
            Park(n=0)


if __name__ == "__main__":
    unittest.main()
