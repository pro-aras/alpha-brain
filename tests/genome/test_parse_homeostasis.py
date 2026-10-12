# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 — PREREG-HOMEOSTASIS §2.1 (the law SIGNED;
# SEAT-LINE-H0.txt sha256 edda32e7…; test-first): the HOMEOSTASIS clause — the ONE new genome line
# declaring the drives for the life that carries them. Absent: NO "HOMEOSTASIS" key in declared (every
# genome on disk byte-identical). Present: exactly the declared words under declared["HOMEOSTASIS"][word]
# = True, 1..3 words from {arousal, boredom, fatigue}. A bare line, an unknown word, or a repeated word
# all refuse BY NAME. Modeled whole on tests/genome/test_parse_registers.py (the REGISTERS precedent).
"""tests/genome/test_parse_homeostasis.py — the HOMEOSTASIS clause (PREREG-HOMEOSTASIS §2.1).

The line's full form: `HOMEOSTASIS arousal boredom fatigue`. The Mind self-wires the three state
variables from the declaration (creature/mind.py — the wiring tests' home); here the parser, whole
and only."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE = (ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()
LEAN, _n = re.subn(r"^DRIVE    .*\n", "", _TEMPLATE, count=1, flags=re.M)
assert _n == 1, "the lean template carries one DRIVE line"

DRIVES = ("arousal", "boredom", "fatigue")


def lean_text(*lines: str) -> str:
    return LEAN + "\n" + ("\n".join(lines) + "\n" if lines else "")


class AbsentIsByteIdentical(unittest.TestCase):
    def test_no_line_means_no_key(self) -> None:
        self.assertNotIn("HOMEOSTASIS", parse_genome(lean_text()).declared)

    def test_every_genome_on_disk_has_no_key(self) -> None:
        genomes = sorted(ROOT.glob("genome/**/*.genome"))
        self.assertGreater(len(genomes), 0, "presence: the repo carries genome files")
        for path in genomes:
            with self.subTest(genome=path):
                self.assertNotIn("HOMEOSTASIS", parse_genome(path.read_text()).declared,
                                 "a carrier genome must be declared BY NAME here before it exists "
                                 "(PREREG-HOMEOSTASIS §2.1: no silent carriers)")


class PresentDeclaresExactlyItsWords(unittest.TestCase):
    def test_the_full_form(self) -> None:
        self.assertEqual(parse_genome(lean_text("HOMEOSTASIS arousal boredom fatigue")).declared["HOMEOSTASIS"],
                         {"arousal": True, "boredom": True, "fatigue": True})

    def test_a_subset(self) -> None:
        self.assertEqual(parse_genome(lean_text("HOMEOSTASIS fatigue")).declared["HOMEOSTASIS"],
                         {"fatigue": True})

    def test_order_does_not_matter(self) -> None:
        self.assertEqual(parse_genome(lean_text("HOMEOSTASIS fatigue arousal")).declared["HOMEOSTASIS"],
                         {"arousal": True, "fatigue": True})

    def test_other_lines_untouched(self) -> None:
        before = parse_genome(lean_text()).declared
        after = parse_genome(lean_text("HOMEOSTASIS boredom")).declared
        self.assertEqual({k: v for k, v in after.items() if k != "HOMEOSTASIS"}, before,
                         "the line must change NOTHING else in the declared dict")


class GarbageRefusedByName(unittest.TestCase):
    def test_bare_refused(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(lean_text("HOMEOSTASIS"))
        self.assertIn("HOMEOSTASIS", str(cm.exception))
        self.assertNotIn("unknown gene", str(cm.exception),
                         "the refusal must come from the HOMEOSTASIS branch itself, not the unknown-gene fallthrough")

    def test_unknown_word_refused(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(lean_text("HOMEOSTASIS arousal hunger"))
        self.assertIn("hunger", str(cm.exception))
        self.assertNotIn("unknown gene", str(cm.exception))

    def test_repeated_word_refused(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(lean_text("HOMEOSTASIS boredom boredom"))
        self.assertIn("repeated", str(cm.exception))
        self.assertIn("boredom", str(cm.exception))

    def test_four_words_refused(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(lean_text("HOMEOSTASIS arousal boredom fatigue hunger"))
        self.assertIn("HOMEOSTASIS", str(cm.exception))
        self.assertNotIn("unknown gene", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
