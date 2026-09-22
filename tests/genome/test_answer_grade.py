"""test_answer_grade.py — L-6/ANSWER (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4 L-6;
docs/briefs/LIFE-A-ANSWER-SELF.md #2): `ANSWER resembles under own-band; unknown below <f>` —
`recall`/`recall_many` gain two NEW fields, `grade` in {"sure","unsure","unknown"} and `own_floor`
(float|null), changing NO existing field (`cell`/`lit`/`reason`/`best`/`second`/`cos` are all untouched
byte for byte). A THIRD, additive field `resembles_cell` carries the SIGHT cell id the grade was
computed against — `lit` itself (already present for noedge/ratio/close) for every reason but `novel`,
where `lit` is (and stays) None; there `resembles_cell` is the nearest ALIVE sight cell by raw cosine
(genome/think.py:_nearest_in's own algorithm, mirrored inline here rather than imported -- think.py
imports machinery.Organism, so the reverse import would be circular).

Grading is scoped to side=="sight" only (THRESH's own band tracks sight cells; ANSWER's whole purpose,
per the plan, is the what-is/picture-recognition road) -- side=="words" always reads
(grade, own_floor, resembles_cell) == (None, None, None), by design, documented here.

edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:1x +0400 — #2 (docs/briefs/LIFE-A-ANSWER-SELF.md).
"""
from __future__ import annotations

import unittest

import numpy as np

from genome.machinery import GenomeError, Organism, parse_genome

from ._toy import mini_genome, onehot


def _answer_genome(unknown_below: float = 0.6, theta_n: float | None = None, extra: str = ""):
    text = mini_genome().text if theta_n is None else mini_genome(theta_n=theta_n).text
    text += f"ANSWER resembles under own-band; unknown below {unknown_below}\n" + extra
    return parse_genome(text)


def _unit_mix(i: int, j: int, cos_i: float, dim: int = 64) -> np.ndarray:
    """A unit vector whose cosine to onehot(i, dim) is exactly cos_i (mixing in onehot(j, dim))."""
    sin_i = (1.0 - cos_i ** 2) ** 0.5
    v = np.zeros(dim); v[i] = cos_i; v[j] = sin_i
    return v


class TestAnswerParser(unittest.TestCase):
    def test_parses(self) -> None:
        g = _answer_genome(0.911)
        self.assertEqual(g.declared["ANSWER"], {"unknown_below": 0.911})

    def test_bad_syntax_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(mini_genome().text + "ANSWER resembles; unknown below 0.9\n")


class TestGatingUndeclaredOrWordsSide(unittest.TestCase):
    def test_undeclared_answer_leaves_new_fields_none(self) -> None:
        org = Organism(mini_genome())
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        r = org.recall("sight", xs0)
        self.assertEqual(r["reason"], "answer")
        self.assertIsNone(r.get("grade")); self.assertIsNone(r.get("own_floor")); self.assertIsNone(r.get("resembles_cell"))

    def test_words_side_is_always_none_even_when_declared(self) -> None:
        org = Organism(_answer_genome(0.6))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        r = org.recall("words", xw0)
        self.assertEqual(r["reason"], "answer")
        self.assertIsNone(r.get("grade")); self.assertIsNone(r.get("own_floor")); self.assertIsNone(r.get("resembles_cell"))

    def test_existing_fields_are_byte_for_byte_unchanged(self) -> None:
        """The brief's own promise: cell/lit/reason/best/second/cos never move when ANSWER is added."""
        plain = Organism(mini_genome())
        graded = Organism(_answer_genome(0.6))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for org in (plain, graded):
            org.moment(xs0, xw0); org.moment(xs0, xw0)
        r_plain = plain.recall("sight", xs0); r_graded = graded.recall("sight", xs0)
        for key in ("cell", "lit", "reason", "best", "second", "cos"):
            self.assertEqual(r_plain[key], r_graded[key], key)


class TestGradeFormula(unittest.TestCase):
    """theta_n=0.5 (mini_genome's default), unknown_below=0.6 -- deliberately ABOVE theta_n so every
    branch of the sure/unsure/unknown formula is reachable through reason=="answer" alone (in LIFE.genome
    itself unknown_below=0.911 < theta_n=0.952, so a lit cell's own cos can never fall under it -- only
    reason=="novel" ever reads "unknown" there; that ordering is a genome CHOICE, not a law this formula
    enforces, so both orderings are exercised here)."""

    def _wired_org(self, unknown_below: float = 0.6):
        org = Organism(_answer_genome(unknown_below))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0)   # birth
        org.moment(xs0, xw0)   # wired: cell0 -> word0
        return org

    def test_sure_when_cos_at_or_above_own_floor(self) -> None:
        org = self._wired_org()
        r = org.recall("sight", onehot(0, 64))       # cos == 1.0, own_floor == theta_n == 0.5 (no THRESH)
        self.assertEqual(r["reason"], "answer")
        self.assertEqual(r["grade"], "sure")
        self.assertEqual(r["own_floor"], org.g.theta_n)
        self.assertEqual(r["resembles_cell"], r["lit"])

    def test_unsure_between_unknown_below_and_own_floor(self) -> None:
        org = self._wired_org(unknown_below=0.6)      # own_floor == theta_n == 0.5 < cos below needs own_floor > cos
        # raise own_floor above the query's cos by declaring THRESH too, with a tight all-1.0 history
        text = _answer_genome(0.6).text + "THRESH cell own band history 30\n"
        org = Organism(parse_genome(text))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for _ in range(7):
            org.moment(xs0, xw0)                       # 1 birth + 6 pushes, all cos==1.0 -> own_floor==1.0
        self.assertEqual(org.own_floor(0), 1.0)
        q = _unit_mix(0, 1, 0.8)                        # cos to cell0 == 0.8: < 1.0 (own_floor), >= 0.6 (unknown_below), >= 0.5 (theta_n, still lights)
        r = org.recall("sight", q)
        self.assertEqual(r["reason"], "answer")
        self.assertAlmostEqual(r["cos"], 0.8, places=5)
        self.assertEqual(r["grade"], "unsure")
        self.assertEqual(r["own_floor"], 1.0)

    def test_unknown_when_cos_below_unknown_below_but_still_answers(self) -> None:
        # own_floor must be RAISED above the query's cos too (sure is checked first) -- so THRESH is
        # declared with a tight all-1.0 history (own_floor == 1.0), and unknown_below sits ABOVE the
        # query's cos of 0.55 but below own_floor: theta_n 0.5 <= cos 0.55 < unknown_below 0.85 < own_floor 1.0.
        text = _answer_genome(unknown_below=0.85).text + "THRESH cell own band history 30\n"
        org = Organism(parse_genome(text))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for _ in range(7):
            org.moment(xs0, xw0)
        self.assertEqual(org.own_floor(0), 1.0)
        q = _unit_mix(0, 1, 0.55)                       # cos 0.55: >= theta_n 0.5 (still lights, reason=answer), < unknown_below 0.85
        r = org.recall("sight", q)
        self.assertEqual(r["reason"], "answer")
        self.assertAlmostEqual(r["cos"], 0.55, places=5)
        self.assertEqual(r["grade"], "unknown")

    def test_novel_reason_resolves_resembles_cell_to_nearest_alive_and_grades_it(self) -> None:
        """theta_n=0.9, unknown_below=0.5: a query at cos 0.6 to cell0 is a genuine NOVEL (below theta_n)
        yet 'unsure' (above unknown_below) -- `lit` stays None (unchanged); `resembles_cell` names cell0."""
        org = Organism(_answer_genome(unknown_below=0.5, theta_n=0.9))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        q = _unit_mix(0, 1, 0.6)
        r = org.recall("sight", q)
        self.assertEqual(r["reason"], "novel")
        self.assertIsNone(r["cell"]); self.assertIsNone(r["lit"], "lit must stay unchanged (None) for novel")
        self.assertEqual(r["resembles_cell"], 0)
        self.assertAlmostEqual(r["cos"], 0.6, places=5)
        self.assertEqual(r["grade"], "unsure")

    def test_novel_reason_unknown_when_below_unknown_below_too(self) -> None:
        org = Organism(_answer_genome(unknown_below=0.5, theta_n=0.9))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        q = _unit_mix(0, 1, 0.3)
        r = org.recall("sight", q)
        self.assertEqual(r["reason"], "novel")
        self.assertEqual(r["resembles_cell"], 0)
        self.assertEqual(r["grade"], "unknown")

    def test_noedge_reason_gets_a_grade_too(self) -> None:
        """A sight cell born with no edge to any word: lit fires (it resonates), reason=noedge -- and it
        still has an own floor/grade (theta_n, since no THRESH history)."""
        org = Organism(_answer_genome(0.6))
        xs0 = onehot(0, 64)
        org.moment_sight(xs0)          # a sight-only moment: births cell0, wires nothing
        r = org.recall("sight", xs0)
        self.assertEqual(r["reason"], "noedge")
        self.assertEqual(r["lit"], 0)
        self.assertEqual(r["resembles_cell"], 0)
        self.assertEqual(r["grade"], "sure")     # cos==1.0 >= theta_n==own_floor (no THRESH)
        self.assertEqual(r["own_floor"], org.g.theta_n)

    def test_recall_many_single_glance_matches_recall(self) -> None:
        """G1's own parity law extended to the new fields: for ONE glance, recall_many == recall."""
        org = self._wired_org()
        for q in (onehot(0, 64), _unit_mix(0, 1, 0.3)):
            self.assertEqual(org.recall("sight", q), org.recall_many("sight", [q]))


if __name__ == "__main__":
    unittest.main()
