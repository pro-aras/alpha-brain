# edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 00:55 +0400 — ALPHA4-G.md task 1/3/4 (docs/ALPHA4-PREREG.md
# §2/§3): the parser side of GROW unbounded, BUDGET's regenerate clause, and CYCLE's redundant-share form.
"""test_parse_grow.py — GROW unbounded, BUDGET's regenerate clause, CYCLE's redundant form: the parser."""
from __future__ import annotations

import unittest

from genome.machinery import GenomeError, parse_genome

from ._toy import mini_genome


class TestGrowParses(unittest.TestCase):
    def test_grow_unbounded_declared(self) -> None:
        g = mini_genome(grow=True)
        self.assertIn("GROW", g.declared)
        self.assertIsNone(g.nmax, "NMAX absent under GROW -> Genome.nmax is None")

    def test_grow_bad_value_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(mini_genome().text.replace("NMAX 200\n", "GROW capped\n"))

    def test_nmax_and_no_grow_is_required_as_before(self) -> None:
        """The negative control: a genome with NMAX and no GROW never even reaches the GROW code path —
        Genome.nmax is the plain int it always was."""
        g = mini_genome()
        self.assertNotIn("GROW", g.declared)
        self.assertEqual(g.nmax, 200)

    def test_missing_nmax_without_grow_still_refuses(self) -> None:
        """`required`'s nmax entry is dropped ONLY when GROW is declared -- a genome with neither NMAX nor
        GROW still refuses exactly as before (the old failure mode, untouched)."""
        text = mini_genome().text.replace("NMAX 200\n", "")
        with self.assertRaises(GenomeError) as ctx:
            parse_genome(text)
        self.assertIn("nmax", str(ctx.exception))

    def test_grow_organism_starts_with_no_nmax(self) -> None:
        """Genome() construction itself must not choke on nmax=None (a dataclass field-ordering trap --
        `nmax` used to sit before several non-default fields)."""
        g = mini_genome(grow=True)
        self.assertIsNone(g.nmax)
        # every other required field still reads correctly (the reorder touched nothing else)
        self.assertEqual(g.kwta, 5)
        self.assertEqual(g.budget, 400)


class TestBudgetRegenParses(unittest.TestCase):
    def test_old_form_still_parses_regen_zero(self) -> None:
        g = mini_genome()
        self.assertEqual(g.budget, 400)
        self.assertIsNone(g.budget_regen_every)
        self.assertEqual(g.budget_regen_n, 0)

    def test_regen_form_parses(self) -> None:
        g = mini_genome(budget_regen=(1, 60))
        self.assertEqual(g.budget, 400)
        self.assertEqual(g.budget_regen_n, 1)
        self.assertEqual(g.budget_regen_every, 60)

    def test_regen_bad_syntax_refuses(self) -> None:
        text = mini_genome().text.replace("BUDGET 400 per arrival", "BUDGET 400 per arrival; regen 1 per 60 moments")
        with self.assertRaises(GenomeError):
            parse_genome(text)

    def test_regen_placeholder_refuses(self) -> None:
        text = mini_genome().text.replace("BUDGET 400 per arrival", "BUDGET 400 per arrival; regenerate N per 60 moments")
        with self.assertRaises(GenomeError):
            parse_genome(text)


class TestCycleRedundantParses(unittest.TestCase):
    def test_redundant_form_declared(self) -> None:
        g = mini_genome(cycle_share=0.05)
        self.assertEqual(g.declared["CYCLE"], {"share": 0.05})

    def test_old_form_declared_dict_unchanged(self) -> None:
        """The negative control: the OLD form's declared dict is EXACTLY {"grow_to": f} -- no "kind" tag
        added (test_parse_g4.py:104 already pins this exact shape)."""
        g = mini_genome(cycle_grow_to=0.9)
        self.assertEqual(g.declared["CYCLE"], {"grow_to": 0.9})

    def test_redundant_bad_syntax_refuses(self) -> None:
        text = mini_genome().text.replace("SCALE every 1000 moments", "SCALE every 1000 moments\nCYCLE consolidate over 0.05 of alive")
        with self.assertRaises(GenomeError):
            parse_genome(text)

    def test_old_form_with_grow_refuses_named(self) -> None:
        """Task 4: under GROW, the old "grow to N nmax" form is refused -- a cycle keyed on a cap that does
        not exist -- even though each line parses fine on its own."""
        text = mini_genome(grow=True).text.replace("SCALE every 1000 moments", "SCALE every 1000 moments\nCYCLE grow to 0.9 nmax then consolidate")
        with self.assertRaises(GenomeError) as ctx:
            parse_genome(text)
        self.assertIn("cap", str(ctx.exception).lower())

    def test_redundant_form_with_grow_is_fine(self) -> None:
        g = mini_genome(grow=True, cycle_share=0.05)
        self.assertIn("GROW", g.declared)
        self.assertEqual(g.declared["CYCLE"], {"share": 0.05})

    def test_redundant_form_without_grow_is_also_fine(self) -> None:
        """The new form doesn't require GROW -- it's a separate, orthogonal switch (a genome could in
        principle keep a fixed NMAX and still consolidate by redundancy rather than by grow_to*nmax)."""
        g = mini_genome(cycle_share=0.05)
        self.assertNotIn("GROW", g.declared)
        self.assertEqual(g.declared["CYCLE"], {"share": 0.05})


if __name__ == "__main__":
    unittest.main()
