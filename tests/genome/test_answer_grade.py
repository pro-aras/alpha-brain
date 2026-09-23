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

edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:42 +0400 — #2 (docs/briefs/LIFE-A-ANSWER-SELF.md).
"""
from __future__ import annotations

import unittest
from pathlib import Path

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


# ============================================================================ A4L-ANSWER (A4-LADDER-PREREG §2.2)
# edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:11 +0400 — the ANSWER line's optional trailing
# "; sure only when a majority of the glances light" clause. Fast, hermetic toys (mini_genome's pool retina, no
# GAZE/tower) exercising the STRUCTURAL gate in genome/machinery.py:Organism.recall_many; the real-front controls
# named in the brief (a seen thing's held-out canvas, the spiral canvas) are run separately on alpha4-1's snapshot
# fixture (not committed here -- an external, un-tracked fixture copied under scratch/ per the brief's own rule;
# their numbers are in the builder report, task 0/4).
def _majority_genome(unknown_below: float = 0.6, theta_n: float | None = None):
    text = mini_genome().text if theta_n is None else mini_genome(theta_n=theta_n).text
    text += (f"ANSWER resembles under own-band; unknown below {unknown_below}; "
             "sure only when a majority of the glances light\n")
    return parse_genome(text)


class TestMajorityClauseParser(unittest.TestCase):
    def test_parses_with_majority_clause(self) -> None:
        g = _majority_genome(0.911)
        self.assertEqual(g.declared["ANSWER"], {"unknown_below": 0.911, "majority": True})

    def test_old_form_still_parses_without_the_majority_key(self) -> None:
        """The negative control (A4-LADDER-PREREG §1.1): the OLD line, byte-identical, still parses to
        exactly {"unknown_below": f} -- no "majority" key appears merely because this clause now exists."""
        g = _answer_genome(0.911)
        self.assertEqual(g.declared["ANSWER"], {"unknown_below": 0.911})

    def test_missing_article_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(mini_genome().text + "ANSWER resembles under own-band; unknown below 0.6; "
                                                "sure only when majority of the glances light\n")

    def test_wrong_case_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(mini_genome().text + "ANSWER resembles under own-band; unknown below 0.6; "
                                                "Sure Only When A Majority Of The Glances Light\n")

    def test_extra_trailing_word_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(mini_genome().text + "ANSWER resembles under own-band; unknown below 0.6; "
                                                "sure only when a majority of the glances light now\n")


class TestRecallManyMajorityGate(unittest.TestCase):
    """cell0 <-> word0 wired (cos 1.0 to `onehot(0, 64)`/`onehot(0, 208)`); `onehot(50, 64)` is orthogonal
    (cos 0.0) to cell0's own birth vector, so it never lights (0.0 < theta_n 0.5) -- a clean, deterministic
    stand-in for GAZE's own "a located glance replaced by a blank canvas" (the brief's control (a)/(b))."""

    def _wired(self, unknown_below: float = 0.6):
        org = Organism(_majority_genome(unknown_below))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)   # birth, then wired
        return org

    def _wired_plain(self, unknown_below: float = 0.6):
        """The SAME organism, but ANSWER carries no majority clause at all -- the negative control."""
        org = Organism(_answer_genome(unknown_below))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        return org

    def test_majority_met_answers_normally(self) -> None:
        """5 glances, 3 lit (>= floor(5/2)+1 == 3): the gate does not fire -- reason stays "answer"."""
        org = self._wired()
        lit_glance = onehot(0, 64); dark = onehot(50, 64)
        r = org.recall_many("sight", [lit_glance, lit_glance, lit_glance, dark, dark])
        self.assertEqual(r["reason"], "answer")
        self.assertEqual(r["cell"], 0)
        self.assertEqual((r["lit_n"], r["n"]), (3, 5))

    def test_majority_missed_abstains_minority(self) -> None:
        """5 glances, only 2 lit (< 3): the WOULD-BE answer becomes an abstention -- new reason "minority",
        cell None, still graded (own-band) on the resonating cell, resembles rendering the same X."""
        org = self._wired()
        lit_glance = onehot(0, 64); dark = onehot(50, 64)
        r = org.recall_many("sight", [lit_glance, lit_glance, dark, dark, dark])
        self.assertEqual(r["reason"], "minority")
        self.assertIsNone(r["cell"])
        self.assertEqual(r["lit"], 0)
        self.assertEqual((r["lit_n"], r["n"]), (2, 5))
        self.assertIn(r["grade"], ("sure", "unsure", "unknown"))
        self.assertEqual(r["resembles_cell"], 0)

    def test_zero_lit_glances_stays_novel(self) -> None:
        """lit_n == 0 reads "novel" exactly as before this clause existed -- lit_n/n are still attached
        (the clause is declared), the reason and every other field are untouched."""
        org = self._wired()
        dark = onehot(50, 64)
        r = org.recall_many("sight", [dark] * 5)
        self.assertEqual(r["reason"], "novel")
        self.assertIsNone(r["cell"]); self.assertIsNone(r["lit"])
        self.assertEqual((r["lit_n"], r["n"]), (0, 5))

    def test_single_glance_can_never_trip_the_gate(self) -> None:
        """floor(1/2) + 1 == 1: lit_n can only be 0 or 1 with one glance, so "minority" is unreachable --
        a lighting single glance still answers, a dark one is still "novel", never "minority"."""
        org = self._wired()
        self.assertEqual(org.recall_many("sight", [onehot(0, 64)])["reason"], "answer")
        self.assertEqual(org.recall_many("sight", [onehot(50, 64)])["reason"], "novel")

    def test_undeclared_clause_never_gates_and_carries_no_new_keys(self) -> None:
        """The plain ANSWER line (no majority clause): even 1 of 5 glances lighting still answers as
        today, and the result carries neither "lit_n" nor "n" -- the negative control."""
        org = self._wired_plain()
        lit_glance = onehot(0, 64); dark = onehot(50, 64)
        r = org.recall_many("sight", [lit_glance, dark, dark, dark, dark])
        self.assertEqual(r["reason"], "answer")
        self.assertNotIn("lit_n", r); self.assertNotIn("n", r)

    def test_minority_names_the_same_cell_the_old_law_would_have_answered(self) -> None:
        """A2's own promise (the ceiling clause): the abstention's resemblance is the SAME X the old law
        would have named, not a re-derived or weaker guess -- verified by asking the SAME organism and the
        SAME glances under both laws via the read-side override."""
        org = self._wired()
        xs = [onehot(0, 64), onehot(0, 64), onehot(50, 64), onehot(50, 64), onehot(50, 64)]
        old = org.recall_many("sight", xs, majority=False)
        new = org.recall_many("sight", xs, majority=True)
        self.assertEqual(old["reason"], "answer")
        self.assertEqual(new["reason"], "minority")
        self.assertEqual(new["lit"], old["lit"])
        self.assertEqual(new["cos"], old["cos"])
        self.assertEqual(new["resembles_cell"], old["lit"])

    def test_minority_falls_back_to_the_first_lit_cell_when_no_edge_exists_at_all(self) -> None:
        """A sight-only birth (moment_sight -- no word wiring, no edges, ever): the "noedge" branch's own
        reference (lit_union[0]) is what a minority abstention falls back to when there is no evidence to
        pick a best-edge cell from at all."""
        org = Organism(_majority_genome(0.6))
        xs0 = onehot(0, 64)
        org.moment_sight(xs0)             # births cell0, wires nothing
        lit_glance = onehot(0, 64); dark = onehot(50, 64)
        r = org.recall_many("sight", [lit_glance, dark, dark, dark, dark])
        self.assertEqual(r["reason"], "minority")
        self.assertEqual(r["lit"], 0)
        self.assertEqual((r["lit_n"], r["n"]), (1, 5))

    def test_read_side_override_false_suppresses_a_declared_clause(self) -> None:
        """self_exam.py's "old law" pass (A4-LADDER-PREREG §2.2 task 3): majority=False reads the OLD law
        even though the genome declares the new one -- no minority, no lit_n/n keys either."""
        org = self._wired()
        lit_glance = onehot(0, 64); dark = onehot(50, 64)
        r = org.recall_many("sight", [lit_glance, lit_glance, dark, dark, dark], majority=False)
        self.assertEqual(r["reason"], "answer")
        self.assertNotIn("lit_n", r); self.assertNotIn("n", r)

    def test_read_side_override_true_forces_the_gate_when_undeclared(self) -> None:
        """The sitter's `lit_counts_seen` diagnostic (task 3): majority=True reads the NEW law even on a
        genome that never declared it -- used to count lit glances on every rung's own snapshot."""
        org = self._wired_plain()
        lit_glance = onehot(0, 64); dark = onehot(50, 64)
        r = org.recall_many("sight", [lit_glance, lit_glance, dark, dark, dark], majority=True)
        self.assertEqual(r["reason"], "minority")
        self.assertEqual((r["lit_n"], r["n"]), (2, 5))

    def test_recall_many_single_glance_still_matches_recall_with_the_clause_declared(self) -> None:
        """G1's parity law (#171's class): for ONE glance, recall_many differs from recall by AT MOST the
        two new keys -- never in cell/lit/reason/best/second/cos/grade/own_floor/resembles_cell -- and
        those two keys are exactly {lit_n in {0, 1}, n == 1} when the clause is declared."""
        org = self._wired()
        for q, want_lit in ((onehot(0, 64), 1), (onehot(50, 64), 0)):
            single = org.recall("sight", q)
            many = org.recall_many("sight", [q])
            self.assertEqual(many.get("lit_n"), want_lit)
            self.assertEqual(many.get("n"), 1)
            many_stripped = {k: v for k, v in many.items() if k not in ("lit_n", "n")}
            self.assertEqual(single, many_stripped)


class TestRungGenomeOneDifference(unittest.TestCase):
    """A4-LADDER-PREREG §1.1: a rung's genome = the floor + ONE mechanism. `difflib` against
    `A4L-FLOOR.genome` must show exactly the declared ANSWER line + one edit-note header line -- nothing
    else, and no line of the floor touched (checked byte-for-byte on every OTHER line)."""

    ROOT = Path(__file__).resolve().parents[2]

    def test_diff_is_exactly_the_header_and_the_answer_line(self) -> None:
        import difflib
        floor = (self.ROOT / "genome" / "ladder" / "A4L-FLOOR.genome").read_text().splitlines()
        rung = (self.ROOT / "genome" / "ladder" / "A4L-ANSWER.genome").read_text().splitlines()
        diff = list(difflib.unified_diff(floor, rung, lineterm=""))
        added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
        removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
        self.assertEqual(len(removed), 1, f"exactly one floor line should change: {removed}")
        self.assertTrue(removed[0].startswith("-ANSWER"), removed[0])
        self.assertEqual(len(added), 2, f"one changed ANSWER line + one edit-note header: {added}")
        self.assertTrue(any(l.startswith("+# A4L-ANSWER.genome") for l in added), added)
        self.assertTrue(any(l.startswith("+ANSWER") and "sure only when a majority of the glances light" in l for l in added), added)

    def test_rung_genome_parses_with_the_clause_declared(self) -> None:
        g = parse_genome((self.ROOT / "genome" / "ladder" / "A4L-ANSWER.genome").read_text())
        self.assertEqual(g.declared["ANSWER"], {"unknown_below": 0.911, "majority": True})

    def test_floor_genome_unchanged_undeclared(self) -> None:
        g = parse_genome((self.ROOT / "genome" / "ladder" / "A4L-FLOOR.genome").read_text())
        self.assertEqual(g.declared["ANSWER"], {"unknown_below": 0.911})


if __name__ == "__main__":
    unittest.main()
