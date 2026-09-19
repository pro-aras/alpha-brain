"""test_parse_g4_wave2.py — B9: the three Wave 2 parser genes (THINK, EXAM, FROZEN).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — B9 (docs/G4-PREREG.md §11.2): THINK,
EXAM, FROZEN each a strict re.fullmatch clause in genome/machinery.py's parse_genome, storing its
parsed sub-dict in Genome.declared[GENE] — interface fixed for Builder A: declared["THINK"] ==
{"every": int}, declared["EXAM"] == {"every": int}, declared["FROZEN"] == {"after": int}. None of the
three are in `required`; none touch self.c (the pin holds — see test_pin_skeleton.py, re-run after
this file was added). Kept separate from test_parse_g4.py (B1's twenty genes) rather than folding in,
matching B8's "adds NEW tests beside them" discipline — B1's file and its NEW_GENES enumeration stay
untouched.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import Genome, GenomeError, parse_genome

ROOT = Path(__file__).resolve().parent.parent.parent
SKELETON_TEXT = (ROOT / "genome" / "G4-skeleton.genome").read_text()

# (gene, a VALID line, a line missing the number / malformed)
WAVE2_GENES = {
    "THINK":  ("THINK  every 4 canvases", "THINK  every canvases"),
    "EXAM":   ("EXAM   every 10 canvases", "EXAM   every canvases"),
    "FROZEN": ("FROZEN after 500 cells", "FROZEN after cells"),
}


class TestParseWave2Genes(unittest.TestCase):
    def test_each_gene_valid_line_parses_alone(self) -> None:
        for gene, (valid_line, _broken) in WAVE2_GENES.items():
            with self.subTest(gene=gene):
                try:
                    parse_genome(valid_line + "\n")
                except GenomeError as e:
                    self.assertIn("genome lacks", str(e), f"{gene}'s own VALID line was refused: {e}")

    def test_each_gene_missing_number_is_refused(self) -> None:
        for gene, (_valid, broken_line) in WAVE2_GENES.items():
            with self.subTest(gene=gene):
                with self.assertRaises(GenomeError, msg=f"{gene} accepted a malformed line: {broken_line!r}") as cm:
                    parse_genome(broken_line + "\n")
                self.assertIn(gene, str(cm.exception))

    def test_declared_dict_shape(self) -> None:
        # appended to the full (required-fields-complete) skeleton text so parsing reaches the
        # declared-dict assertions rather than tripping the unrelated "genome lacks [...]" check.
        g = parse_genome(SKELETON_TEXT + "\nTHINK  every 4 canvases\n")
        self.assertEqual(g.declared["THINK"], {"every": 4})
        g = parse_genome(SKELETON_TEXT + "\nEXAM   every 10 canvases\n")
        self.assertEqual(g.declared["EXAM"], {"every": 10})
        g = parse_genome(SKELETON_TEXT + "\nFROZEN after 500 cells\n")
        self.assertEqual(g.declared["FROZEN"], {"after": 500})

    def test_undeclared_means_absent(self) -> None:
        # a genome that never writes THINK/EXAM/FROZEN simply lacks the key — no default is invented.
        g = parse_genome(SKELETON_TEXT)
        self.assertNotIn("THINK", g.declared)
        self.assertNotIn("EXAM", g.declared)
        self.assertNotIn("FROZEN", g.declared)

    def test_misspelt_still_refused_by_name(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome("THNIK every 4 canvases\n")
        self.assertIn("unknown gene", str(cm.exception))
        self.assertIn("THNIK", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
