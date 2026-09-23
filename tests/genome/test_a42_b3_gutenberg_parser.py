# edit: Claude (Sonnet 5, ALPHA4-2 builder B3), 2026-09-23 17:2x +0400 — A42-B3 task 2 (docs/ALPHA4-2-PREREG.md
# §2.3, branch A, ADOPTED by Ahmad 2026-09-23 16:56 +0400: "yes fix that Gutenberg part"). The parser side of
# the optional "; gutenberg body only" clause on SENSE read, built UNDECLARED (this task does not add the line
# to any genome file). tests/genome/test_read_lexicon_parser.py's own test_valid_line_parses (the WHOLE
# SENSE_READ dict, exactly 5 keys) is the byte-identical-when-absent control and is deliberately left
# untouched by this file -- reproduced by import below rather than duplicated.
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

from .test_read_lexicon_parser import LIFE_GENOME_TEXT, VALID_READ_LINE, _life_plus


class TestGutenbergClauseParses(unittest.TestCase):
    def test_line_without_the_clause_is_still_exactly_five_keys(self) -> None:
        """The byte-identical-when-absent control, reproduced here beside the new tests (not just trusted from
        the other file): the exact same VALID_READ_LINE this file extends must still parse to the pre-task 2
        five-key dict."""
        g = parse_genome(_life_plus(VALID_READ_LINE))
        self.assertEqual(g.declared["SENSE_READ"], {
            "shelf": "/data/alpha3-library/SHELF.sqlite",
            "curriculum": "/data/alpha3-library/CURRICULUM.md",
            "every_s": 5, "words": 8, "canvas": 128,
        })
        self.assertNotIn("gutenberg_body_only", g.declared["SENSE_READ"])

    def test_line_with_the_clause_gains_exactly_one_new_key(self) -> None:
        g = parse_genome(_life_plus(VALID_READ_LINE + "; gutenberg body only"))
        self.assertEqual(g.declared["SENSE_READ"], {
            "shelf": "/data/alpha3-library/SHELF.sqlite",
            "curriculum": "/data/alpha3-library/CURRICULUM.md",
            "every_s": 5, "words": 8, "canvas": 128,
            "gutenberg_body_only": True,
        })

    def test_the_real_alpha42_prereg_spelling_with_no_space_before_the_semicolon(self) -> None:
        """A42-B3-PREREG.md §2 G10's OWN literal branch-A line reads `canvas 128; gutenberg body only` -- the
        semicolon glued directly to the digits, no space. After the tokenizer's split()+' '.join() round trip
        the reconstructed `rest` string carries this exact shape (proven independently by the HASH gene's own
        "sparse; dense at snapshot" literal, which the same round trip must already preserve for HASH to parse
        at all) -- pinned here rather than assumed."""
        line = "SENSE    read shelf /data/alpha3-library/SHELF.sqlite curriculum /data/alpha3-library/CURRICULUM.md every 20 s words 4 canvas 128; gutenberg body only"
        g = parse_genome(LIFE_GENOME_TEXT + "\n" + line + "\n")
        self.assertEqual(g.declared["SENSE_READ"]["canvas"], 128)
        self.assertTrue(g.declared["SENSE_READ"]["gutenberg_body_only"])

    def test_misspelt_clause_refuses_naming_the_clause(self) -> None:
        with self.assertRaises(GenomeError) as ctx:
            parse_genome(_life_plus(VALID_READ_LINE + "; gutenburg body only"))
        self.assertIn("gutenberg body only", str(ctx.exception), "the refusal names the clause, not just 'SENSE read'")

    def test_extra_trailing_junk_after_the_clause_still_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(_life_plus(VALID_READ_LINE + "; gutenberg body only; extra"))


if __name__ == "__main__":
    unittest.main()
