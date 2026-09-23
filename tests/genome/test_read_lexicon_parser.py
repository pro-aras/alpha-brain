# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:0x +0400 — ALPHA4-H tasks 2/3 (docs/briefs/ALPHA4-H.md;
# ALPHA4-PREREG.md §3): the genome parser branches for `SENSE read` and `DOOR lexicon`, test-first.
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
LIFE_GENOME_TEXT = (ROOT / "genome" / "LIFE.genome").read_text()
ALPHA4_GENOME_TEXT = (ROOT / "genome" / "ALPHA4.genome").read_text()

VALID_READ_LINE = "SENSE    read shelf /data/alpha3-library/SHELF.sqlite curriculum /data/alpha3-library/CURRICULUM.md every 5 s words 8 canvas 128"
VALID_DOOR_LINE = "DOOR     lexicon /data/alpha2-library/lexicon-enwiktionary-20260901.sqlite answers what-is by showing"


def _life_plus(*lines: str) -> str:
    return LIFE_GENOME_TEXT + "\n" + "\n".join(lines) + "\n"


class TestSenseReadParses(unittest.TestCase):
    def test_life_genome_alone_parses_without_the_new_lines(self) -> None:
        """The baseline this file appends to must itself be clean -- a control that the fixture is honest."""
        g = parse_genome(LIFE_GENOME_TEXT)
        self.assertNotIn("SENSE_READ", g.declared)
        self.assertNotIn("DOOR_LEXICON", g.declared)

    def test_valid_line_parses(self) -> None:
        g = parse_genome(_life_plus(VALID_READ_LINE))
        self.assertEqual(g.declared["SENSE_READ"], {
            "shelf": "/data/alpha3-library/SHELF.sqlite",
            "curriculum": "/data/alpha3-library/CURRICULUM.md",
            "every_s": 5, "words": 8, "canvas": 128,
        })

    def test_the_real_deployed_line_in_alpha4_genome_parses_identically(self) -> None:
        """A pin against the ACTUAL bytes of genome/ALPHA4.genome:95 (the trailing comment stripped exactly
        as parse_genome itself strips every comment) -- proves this branch reads the file that will launch
        the life, not just a hand-typed fixture."""
        real_line = next(l for l in ALPHA4_GENOME_TEXT.splitlines() if l.strip().startswith("SENSE") and " read " in l)
        stripped = real_line.split("#", 1)[0].strip()
        g = parse_genome(_life_plus(stripped))
        self.assertEqual(g.declared["SENSE_READ"]["shelf"], "/data/alpha3-library/SHELF.sqlite")
        self.assertEqual(g.declared["SENSE_READ"]["curriculum"], "/data/alpha3-library/CURRICULUM.md")
        # edit: Claude (Fable 5.1), 2026-09-23 12:17 +0400 — the deployed line reads `every 20 s words 4` since the pre-flight's cadence
        # decision (ALPHA4-PREREG §8b, 04:37 +04); the pin had stayed at the builder's 5 s / 8 words and master's genome
        # suite read FAILED (failures=1) from the launch commit on — found by the judge builder (JUDGE-UNITS-0923 §0.7).
        self.assertEqual(g.declared["SENSE_READ"]["every_s"], 20)
        self.assertEqual(g.declared["SENSE_READ"]["words"], 4)
        self.assertEqual(g.declared["SENSE_READ"]["canvas"], 128)

    def test_misspelt_keyword_refuses_by_name(self) -> None:
        bad = "SENSE    read shel /data/x curriculum /data/y every 5 s words 8 canvas 128"
        with self.assertRaises(GenomeError) as cm:
            parse_genome(_life_plus(bad))
        self.assertIn("SENSE read", str(cm.exception))

    def test_missing_words_clause_refuses(self) -> None:
        bad = "SENSE    read shelf /data/x curriculum /data/y every 5 s canvas 128"
        with self.assertRaises(GenomeError):
            parse_genome(_life_plus(bad))

    def test_non_numeric_every_refuses(self) -> None:
        bad = "SENSE    read shelf /data/x curriculum /data/y every five s words 8 canvas 128"
        with self.assertRaises(GenomeError):
            parse_genome(_life_plus(bad))


class TestDoorLexiconParses(unittest.TestCase):
    def test_valid_line_parses(self) -> None:
        g = parse_genome(_life_plus(VALID_DOOR_LINE))
        self.assertEqual(g.declared["DOOR_LEXICON"], {"sqlite": "/data/alpha2-library/lexicon-enwiktionary-20260901.sqlite"})

    def test_the_real_deployed_line_in_alpha4_genome_parses_identically(self) -> None:
        real_line = next(l for l in ALPHA4_GENOME_TEXT.splitlines() if l.strip().startswith("DOOR") and "lexicon" in l)
        stripped = real_line.split("#", 1)[0].strip()
        g = parse_genome(_life_plus(stripped))
        self.assertEqual(g.declared["DOOR_LEXICON"]["sqlite"], "/data/alpha2-library/lexicon-enwiktionary-20260901.sqlite")

    def test_misspelt_tail_refuses_by_name(self) -> None:
        bad = "DOOR     lexicon /data/x answers what-is by shown"
        with self.assertRaises(GenomeError) as cm:
            parse_genome(_life_plus(bad))
        self.assertIn("DOOR lexicon", str(cm.exception))

    def test_a_door_line_with_an_unknown_first_word_still_refuses_as_unknown_gene(self) -> None:
        """DOOR is dispatched on args[0], mirroring SENSE/WORLD -- a DOOR variant this branch does not know
        (e.g. builder I's own "web", not yet landed on this branch) must fall through to the generic
        unknown-gene refusal, never be silently accepted by the lexicon branch."""
        # edit: Claude (Fable 5.1), 2026-09-23 03:23 +0400 — the example was builder I's own `DOOR web …` line, which landed at the
        # merge and is now KNOWN (#232 (c): a test that pins the absence of another lane's feature flips at the merge);
        # a DOOR word nobody built keeps the fall-through under test.
        bad = "DOOR     gopher example.org answers what-is by showing"
        with self.assertRaises(GenomeError) as cm:
            parse_genome(_life_plus(bad))
        self.assertIn("unknown gene", str(cm.exception))

    def test_both_new_lines_together_parse(self) -> None:
        g = parse_genome(_life_plus(VALID_READ_LINE, VALID_DOOR_LINE))
        self.assertIn("SENSE_READ", g.declared)
        self.assertIn("DOOR_LEXICON", g.declared)


class TestGenesRegistry(unittest.TestCase):
    def test_sense_read_and_door_lexicon_are_wired(self) -> None:
        from creature.genes import unwired
        g = parse_genome(_life_plus(VALID_READ_LINE, VALID_DOOR_LINE))
        self.assertEqual(unwired(g.declared), [], f"a declared gene with no RUNS site: {unwired(g.declared)}")


if __name__ == "__main__":
    unittest.main()
