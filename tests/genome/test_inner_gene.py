# edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:26 +0400 — PREREG-INNER-1 §2 + AMENDMENT 1 A4 (the law: research-1003 @ 9c589b2, file
# sha256 127b063c…168d; the co-signed TEXT 857e07b2…faa82), test-first: red on the hears head 33f68f9 (the machinery knows no gene INNER:
# «Ran 6 … FAILED (errors=3)», scratch/inner-gene-red.log — and the refusal tests then PASSED BY ABSENCE on the unknown-gene message,
# so they assert the branch's OWN refusal, never the parser's ignorance, #243 (4)).
"""tests/genome/test_inner_gene.py — the gene INNER in the PARSER: ONE form, every value read, any other word refused by name.

    INNER    every body row when idle; walk lift; inhibit <n>; restart <m>

`walk lift` is the only walk the genome accepts (A4: the greedy rule is a test parameter of the walk function, never a genome value).
The gene lives in genome/machinery.py (PINNED, cache.WORLD_CODE): its price is the one redraw window. The mind-side laws (refused
beside no BRAIN / no SENSE body line; the trigger; the chain) are tests/creature/test_inner_mind.py's."""
from __future__ import annotations

import unittest
from pathlib import Path

from creature import genes
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
LEAN = (ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()
LINE = "INNER    every body row when idle; walk lift; inhibit 2; restart 5"


def text(line: str = LINE) -> str:
    return LEAN + "\n" + (line + "\n" if line else "")


class TheOneForm(unittest.TestCase):
    def test_the_law_line_parses_and_every_value_is_read(self) -> None:
        d = parse_genome(text()).declared["INNER"]
        self.assertEqual(d, {"trigger": "body idle", "walk": "lift", "inhibit": 2, "restart": 5})

    def test_the_numbers_are_the_line_s_own(self) -> None:
        d = parse_genome(text("INNER    every body row when idle; walk lift; inhibit 3; restart 7")).declared["INNER"]
        self.assertEqual((d["inhibit"], d["restart"]), (3, 7))
        d0 = parse_genome(text("INNER    every body row when idle; walk lift; inhibit 0; restart 1")).declared["INNER"]
        self.assertEqual((d0["inhibit"], d0["restart"]), (0, 1))

    def test_absent_the_line_declares_nothing(self) -> None:
        self.assertNotIn("INNER", parse_genome(text("")).declared)

    def test_the_registry_knows_the_gene(self) -> None:
        # creature/genes.py's refusal law: a declared gene with no wired site is named at Mind.__init__ — INNER must have a site
        declared = parse_genome(text()).declared
        self.assertEqual(genes.unwired(declared), [])
        site = genes.RUNS["mind"].get("INNER")
        self.assertIsNotNone(site)
        self.assertIn("creature/mind.py", site)


class Refusals(unittest.TestCase):
    BAD = (
        "INNER    every body row when busy; walk lift; inhibit 2; restart 5",      # the trigger's words
        "INNER    every eye row when idle; walk lift; inhibit 2; restart 5",
        "INNER    every body row when idle; walk greedy; inhibit 2; restart 5",    # A4: only `walk lift`
        "INNER    every body row when idle; walk count; inhibit 2; restart 5",
        "INNER    every body row when idle; walk lift; inhibit 2",                 # a clause missing
        "INNER    every body row when idle; inhibit 2; restart 5",
        "INNER    every body row when idle; walk lift; inhibit two; restart 5",    # not a number
        "INNER    every body row when idle; walk lift; inhibit 2; restart 0",      # a chain of 0 thoughts
        "INNER    every body row when idle; walk lift; inhibit -1; restart 5",
        "INNER    every body row when idle; walk lift; inhibit 2; restart 5; says 1",   # an unknown trailing clause
    )

    def test_every_other_form_is_refused_by_name(self) -> None:
        for bad in self.BAD:
            with self.subTest(bad=bad):
                with self.assertRaises(GenomeError) as e:
                    parse_genome(text(bad))
                msg = str(e.exception)
                self.assertIn("INNER", msg)
                # the branch's OWN refusal (it names the one form), never the parser's «unknown gene» — a test that passed by absence
                self.assertNotIn("unknown gene", msg)
                self.assertIn("every body row when idle; walk lift; inhibit <n>; restart <m>", msg)

    # A repeated gene line is refused for NO gene (parse_genome's `seen` set is written and never read; the last line wins) — not this
    # law's to change, so no test asserts it here (a first draft did, and failed on the parser's own convention).


if __name__ == "__main__":
    unittest.main()
