# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §3/§6: EVOLVE's
# parser branch (genome/machinery.py). A REFUSING test (a mis-spelt form is rejected by name — brief's own
# "RULES FOR EVERY BUILDER") plus a positive parse against the exact genome/ALPHA4.genome line and
# LIFE.genome's own byte-identity (an unrelated genome that never declares EVOLVE must be untouched).
"""tests/genome/test_parse_evolve.py — EVOLVE every <n> h; mutate 1 gene within bounds; judge on the last
<m> h; adopt at sleep under the regression bar (ALPHA4-PREREG.md §3/§6)."""
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parent.parent.parent
LIFE_TEXT = (ROOT / "genome" / "LIFE.genome").read_text()
ALPHA4_LINE = ("EVOLVE   every 6 h; mutate 1 gene within bounds; judge on the last 2 h; "
               "adopt at sleep under the regression bar")


class TestEvolveParses(unittest.TestCase):
    def test_the_alpha4_genome_line_parses(self) -> None:
        g = parse_genome(LIFE_TEXT + "\n" + ALPHA4_LINE + "\n")
        self.assertIn("EVOLVE", g.declared)
        self.assertEqual(g.declared["EVOLVE"], {"every_h": 6, "judge_h": 2})

    def test_other_hour_values_parse(self) -> None:
        g = parse_genome(LIFE_TEXT + "\n" + "EVOLVE every 12 h; mutate 1 gene within bounds; "
                          "judge on the last 4 h; adopt at sleep under the regression bar\n")
        self.assertEqual(g.declared["EVOLVE"], {"every_h": 12, "judge_h": 4})

    def test_life_genome_alone_does_not_declare_evolve(self) -> None:
        """LIFE.genome itself (no EVOLVE line) must parse byte-identically to before this branch touched
        machinery.py — an unrelated genome is unaffected by an ADDITIVE parser branch."""
        g = parse_genome(LIFE_TEXT)
        self.assertNotIn("EVOLVE", g.declared)


class TestEvolveRefuses(unittest.TestCase):
    """The refusing test the brief's own rules require: a mis-spelt/placeholder EVOLVE line is rejected
    by name, never silently ignored or silently accepted with the wrong meaning."""

    def _refuses(self, line: str) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(LIFE_TEXT + "\n" + line + "\n")
        self.assertIn("EVOLVE", str(cm.exception))

    def test_wrong_literal_wording_refuses(self) -> None:
        self._refuses("EVOLVE   every 6 h; mutate one gene within bounds; judge on the last 2 h; "
                       "adopt at sleep under the regression bar")

    def test_missing_hours_refuses(self) -> None:
        self._refuses("EVOLVE   every h; mutate 1 gene within bounds; judge on the last 2 h; "
                       "adopt at sleep under the regression bar")

    def test_extra_words_refuse(self) -> None:
        self._refuses("EVOLVE   every 6 h; mutate 2 genes within bounds; judge on the last 2 h; "
                       "adopt at sleep under the regression bar")

    def test_missing_judge_clause_refuses(self) -> None:
        self._refuses("EVOLVE   every 6 h; mutate 1 gene within bounds; adopt at sleep under the regression bar")


if __name__ == "__main__":
    unittest.main()
