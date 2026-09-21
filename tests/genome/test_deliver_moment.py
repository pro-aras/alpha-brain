"""test_deliver_moment.py — G-EYE-1/G-MIND-1 (docs/briefs/G5-I-SEAM-DELIVER-MOMENT.md): the DELIVER and
MOMENT genes' parser clauses.

edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400 — two NEW, additive elif branches in
genome/machinery.py's parse_genome (nothing renamed, no existing branch touched): DELIVER (the eye's
promise: where/when/act travel beside the trait) and MOMENT (the mind's promise: FAST's episode row
carries them). Each is a strict re.fullmatch of the design's own literal line — same discipline as every
other gene in this file (ASK's six-verb literal, BODY's "service <name> threads …") — so a placeholder,
a misspelling or an extra word refuses by name, never silently.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
SKELETON_TEXT = (ROOT / "genome" / "G4-skeleton.genome").read_text()
G4_TEXT = (ROOT / "genome" / "G4.genome").read_text()

DELIVER_VALID = "DELIVER  where fixation when instant act glance"
MOMENT_VALID = "MOMENT   keys sight words surprise where when act source"


class TestDeliverParses(unittest.TestCase):
    def test_valid_line_parses_alone(self) -> None:
        try:
            parse_genome(DELIVER_VALID + "\n")
        except GenomeError as e:
            self.assertIn("genome lacks", str(e), f"DELIVER's own valid line was refused: {e}")

    def test_declared_dict_shape(self) -> None:
        g = parse_genome(SKELETON_TEXT + "\n" + DELIVER_VALID + "\n")
        self.assertEqual(g.declared["DELIVER"], {"where": "fixation", "when": "instant", "act": "glance"})

    def test_placeholder_or_extra_word_refused_by_name(self) -> None:
        for bad in ("DELIVER  where fixation when instant act",           # missing "glance"
                    "DELIVER  where fixation when instant act glance now", # extra word
                    "DELIVER  WHERE FIXATION WHEN INSTANT ACT GLANCE",     # wrong case
                    "DELIVER  where cell when instant act glance"):        # not the declared vocabulary
            with self.subTest(bad=bad):
                with self.assertRaises(GenomeError) as cm:
                    parse_genome(bad + "\n")
                self.assertIn("DELIVER", str(cm.exception))

    def test_undeclared_means_absent(self) -> None:
        g = parse_genome(SKELETON_TEXT)
        self.assertNotIn("DELIVER", g.declared)

    def test_g4_genome_does_not_declare_it_yet(self) -> None:
        # G5's lines are proposals, not laws (docs/organs/BRIEF.md): the live G4.genome must not
        # already declare DELIVER/MOMENT until Ahmad approves the seam going live.
        g = parse_genome(G4_TEXT)
        self.assertNotIn("DELIVER", g.declared)
        self.assertNotIn("MOMENT", g.declared)


class TestMomentParses(unittest.TestCase):
    def test_valid_line_parses_alone(self) -> None:
        try:
            parse_genome(MOMENT_VALID + "\n")
        except GenomeError as e:
            self.assertIn("genome lacks", str(e), f"MOMENT's own valid line was refused: {e}")

    def test_declared_dict_shape(self) -> None:
        g = parse_genome(SKELETON_TEXT + "\n" + MOMENT_VALID + "\n")
        self.assertEqual(g.declared["MOMENT"]["keys"],
                          ["sight", "words", "surprise", "where", "when", "act", "source"])

    def test_placeholder_or_extra_word_refused_by_name(self) -> None:
        for bad in ("MOMENT   keys sight words surprise where when act",          # missing "source"
                    "MOMENT   keys sight words surprise where when act source now",
                    "MOMENT   keys sight words surprise"):                        # FAST's own old literal, not MOMENT's
            with self.subTest(bad=bad):
                with self.assertRaises(GenomeError) as cm:
                    parse_genome(bad + "\n")
                self.assertIn("MOMENT", str(cm.exception))

    def test_undeclared_means_absent(self) -> None:
        g = parse_genome(SKELETON_TEXT)
        self.assertNotIn("MOMENT", g.declared)

    def test_fast_gene_is_untouched_by_moment(self) -> None:
        # HARD RULE 6: rename nothing, edit no existing branch. FAST's own literal
        # ("keys sight words surprise") must still be the only thing FAST accepts — MOMENT does not
        # widen it, it is a wholly separate, additive gene.
        g = parse_genome(SKELETON_TEXT + "\nFAST  episodes 500 keys sight words surprise\n" + MOMENT_VALID + "\n")
        self.assertEqual(g.declared["FAST"], {"episodes": 500, "keys": ["sight", "words", "surprise"]})
        with self.assertRaises(GenomeError):
            parse_genome(SKELETON_TEXT + "\nFAST  episodes 500 keys sight words surprise where when act source\n")


class TestBothDeclaredTogether(unittest.TestCase):
    def test_both_lines_parse_beside_each_other(self) -> None:
        g = parse_genome(SKELETON_TEXT + "\n" + DELIVER_VALID + "\n" + MOMENT_VALID + "\n")
        self.assertIn("DELIVER", g.declared)
        self.assertIn("MOMENT", g.declared)

    def test_misspelt_gene_names_refused_as_unknown(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome("DELIVR  where fixation when instant act glance\n")
        self.assertIn("unknown gene", str(cm.exception))
        with self.assertRaises(GenomeError) as cm:
            parse_genome("MOMENTS  keys sight words surprise where when act source\n")
        self.assertIn("unknown gene", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
