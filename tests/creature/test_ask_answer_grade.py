"""test_ask_answer_grade.py — L-6/L-14 (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4 L-6/L-14;
docs/briefs/LIFE-A-ANSWER-SELF.md #2/#4): the ASK door's graded sentence (`creature.ask.render_what_is`,
split out from `answer()` so it is testable without a real picture on disk), and `why`'s wiring +
ablation ("remove a cell the answer names and the answer must change; remove one it does not and it must
not" — G-MIND-8's own test).

edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 20:1x +0400 — #2/#4 (docs/briefs/LIFE-A-ANSWER-SELF.md).
"""
from __future__ import annotations

import unittest

from creature.ask import render_what_is
from genome.machinery import GenomeError, Organism, parse_genome
from genome.questions import why as questions_why

from tests.genome._toy import mini_genome, onehot


class TestAskParserGeneralised(unittest.TestCase):
    """L-14: the ASK line's literal six-verb regex generalised to any space-separated subset of the
    known verbs, so LIFE.genome's own 5-verb line (no `next` -- 'no mechanism predicts a next thing')
    parses; the existing 6-verb line (G4.genome/G5.genome) parses byte-identically."""

    def test_five_verb_life_genome_line_parses(self) -> None:
        g = parse_genome(mini_genome().text + "ASK what-is show is which why\n")
        self.assertEqual(g.declared["ASK"]["verbs"], ["what-is", "show", "is", "which", "why"])

    def test_six_verb_line_unchanged(self) -> None:
        g = parse_genome(mini_genome().text + "ASK what-is show is which next why\n")
        self.assertEqual(g.declared["ASK"]["verbs"], ["what-is", "show", "is", "which", "next", "why"])

    def test_a_bogus_verb_still_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(mini_genome().text + "ASK what-is bogus\n")

    def test_next_refused_by_name_when_absent_from_the_declared_line(self) -> None:
        from creature.genes import unwired
        g = parse_genome(mini_genome().text + "ASK what-is show is which why\n")
        from creature.ask import _ask_refusal
        self.assertEqual(_ask_refusal(g, "next"), "refused: next is not an ASK verb")
        self.assertEqual(_ask_refusal(g, "why"), None)


class TestRenderWhatIs(unittest.TestCase):
    def _org_word0(self, extra: str = ""):
        text = mini_genome().text + extra
        org = Organism(parse_genome(text))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        return org, xs0, xw0

    def test_grade_none_renders_exactly_as_before_answer_existed(self) -> None:
        org, xs0, _xw0 = self._org_word0()             # ANSWER undeclared
        r = org.recall("sight", xs0)
        self.assertIsNone(r.get("grade"))
        s = render_what_is("pic.png", r, org, {r["cell"]: {"ring"}})
        self.assertEqual(s, f"what-is pic.png -> ring ({r['reason']}; best {r['best']:.3f} second {r['second']:.3f} cos {r['cos']:.3f})")

    def test_sure_renders_bare_answer(self) -> None:
        org, xs0, _xw0 = self._org_word0("ANSWER resembles under own-band; unknown below 0.6\n")
        r = org.recall("sight", xs0)                    # cos == 1.0 -> grade sure (own_floor == theta_n, no THRESH)
        self.assertEqual(r["grade"], "sure")
        s = render_what_is("pic.png", r, org, {r["cell"]: {"ring"}})
        self.assertEqual(s, f"what-is pic.png -> ring ({r['reason']}; best {r['best']:.3f} second {r['second']:.3f} cos {r['cos']:.3f})")

    def test_unsure_renders_resembles_sentence_for_an_answer(self) -> None:
        text = mini_genome().text + "ANSWER resembles under own-band; unknown below 0.6\nTHRESH cell own band history 30\n"
        org = Organism(parse_genome(text))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        for _ in range(7):
            org.moment(xs0, xw0)                        # own_floor -> 1.0
        from tests.genome.test_answer_grade import _unit_mix
        q = _unit_mix(0, 1, 0.8)
        r = org.recall("sight", q)
        self.assertEqual((r["reason"], r["grade"]), ("answer", "unsure"))
        s = render_what_is("pic.png", r, org, {r["cell"]: {"ring"}})
        self.assertIn("I don't know what it is, but it resembles ring", s)
        self.assertIn("(unsure; cos", s)
        self.assertIn("ring's own floor", s)

    def test_novel_abstain_with_resemblance_names_the_reason(self) -> None:
        """A novel query that still reads as an 'unsure' resemblance -- the sentence's label is the
        ABSTAIN REASON (novel), never the literal word 'unsure' (that word is reserved for reason==answer)."""
        text = mini_genome(theta_n=0.9).text + "ANSWER resembles under own-band; unknown below 0.5\n"
        org = Organism(parse_genome(text))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        from tests.genome.test_answer_grade import _unit_mix
        q = _unit_mix(0, 1, 0.6)                         # < theta_n 0.9 (novel), >= unknown_below 0.5
        r = org.recall("sight", q)
        self.assertEqual((r["reason"], r["grade"], r["cell"]), ("novel", "unsure", None))
        s = render_what_is("pic.png", r, org, {0: {"ring"}})
        self.assertIn("I don't know what it is, but it resembles ring", s)
        self.assertIn("(novel; cos", s, "the abstain REASON labels the parenthetical, not the literal word 'unsure'")

    def test_unknown_renders_i_do_not_know(self) -> None:
        text = mini_genome(theta_n=0.9).text + "ANSWER resembles under own-band; unknown below 0.99\n"
        org = Organism(parse_genome(text))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        from tests.genome.test_answer_grade import _unit_mix
        q = _unit_mix(0, 1, 0.6)
        r = org.recall("sight", q)
        self.assertEqual(r["grade"], "unknown")
        s = render_what_is("pic.png", r, org, {0: {"ring"}})
        self.assertEqual(s, f"what-is pic.png -> I do not know this ({r['reason']}; best {r['best']:.3f} second {r['second']:.3f} cos {r['cos']:.3f})")


class TestWhyAblation(unittest.TestCase):
    """G-MIND-8's own test: remove a cell WHY names -> the SAME recall() answer must change; remove one
    it does not name -> it must not."""

    def test_removing_a_named_cell_changes_the_answer_removing_another_does_not(self) -> None:
        org = Organism(mini_genome())
        xs0, xw0 = onehot(0, 64), onehot(0, 208)          # word "ring" -> cell 0
        xs1, xw1 = onehot(1, 64), onehot(1, 208)          # word "bar" -> cell 1 (an unrelated word)
        for _ in range(2):
            org.moment(xs0, xw0)
        for _ in range(2):
            org.moment(xs1, xw1)
        ledgers = {"sight": {0: {"ring"}, 1: {"bar"}}, "words": {0: {"ring"}, 1: {"bar"}}}
        rec = questions_why(org, ledgers, None, "ring")
        named_sight_cells = [c for area, c in rec["cells"] if area == "sight"]
        self.assertEqual(named_sight_cells, [0])

        before = org.recall("sight", xs0)
        self.assertEqual(before["cell"], 0, "before ablation: 'ring' answers word cell 0")

        # (a) kill the NAMED cell -> the answer must change
        org.sight.alive[0] = 0
        after_named = org.recall("sight", xs0)
        self.assertNotEqual(after_named, before)
        self.assertNotEqual(after_named["cell"], before["cell"])
        org.sight.alive[0] = 1   # restore

        # (b) kill a cell WHY did NOT name (cell 1, "bar"'s own cell) -> the SAME question's answer must not change
        org.sight.alive[1] = 0
        after_other = org.recall("sight", xs0)
        self.assertEqual(after_other, before)


if __name__ == "__main__":
    unittest.main()
