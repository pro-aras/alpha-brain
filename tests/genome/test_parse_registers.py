# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 18:4x +0400 — PREREG-BRAIN-LONG-6 §2 B1
# (the law SIGNED; SEAT-LINE sha256 2c6bb22b…; test-first): the REGISTERS clause — the ONE new genome line
# declaring the verdicted registers {content-web, muse, precision} for the life that carries them. Absent:
# NO "REGISTERS" key in declared (every genome on disk byte-identical); present: exactly the declared words
# under declared["REGISTERS"][word] = True. A bare line, an unknown word, an underscore form, or a repeated
# word all refuse BY NAME.
"""tests/genome/test_parse_registers.py — the REGISTERS clause (PREREG-BRAIN-LONG-6 §1.3/§2 B1).

The line's full form: `REGISTERS content-web muse precision`. The Mind self-wires its tri-state flags from
the declaration (creature/mind.py — pinned in tests/creature/test_mind_registers_wiring.py); here the
parser, whole and only."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE = (ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()
LEAN, _n = re.subn(r"^DRIVE    .*\n", "", _TEMPLATE, count=1, flags=re.M)
assert _n == 1, "the lean template carries one DRIVE line"


def lean_text(*lines: str) -> str:
    return LEAN + "\n" + ("\n".join(lines) + "\n" if lines else "")


class AbsentIsByteIdentical(unittest.TestCase):
    def test_no_line_means_no_key(self) -> None:
        self.assertNotIn("REGISTERS", parse_genome(lean_text()).declared)

    def test_every_genome_on_disk_has_no_key(self) -> None:
        genomes = sorted(ROOT.glob("genome/**/*.genome"))
        self.assertGreater(len(genomes), 0, "presence: the repo carries genome files")
        for path in genomes:
            if path.name == "BRAIN-LONG-6.genome":
                continue   # the law's own first carrier (PREREG-BRAIN-LONG-6 §1.3) — declared, never silent
            with self.subTest(genome=path):
                self.assertNotIn("REGISTERS", parse_genome(path.read_text()).declared)


class PresentDeclaresExactlyItsWords(unittest.TestCase):
    def test_the_full_form(self) -> None:
        self.assertEqual(parse_genome(lean_text("REGISTERS content-web muse precision")).declared["REGISTERS"],
                         {"content-web": True, "muse": True, "precision": True})

    def test_a_subset(self) -> None:
        self.assertEqual(parse_genome(lean_text("REGISTERS muse")).declared["REGISTERS"],
                         {"muse": True})

    def test_order_does_not_matter(self) -> None:
        self.assertEqual(parse_genome(lean_text("REGISTERS precision content-web")).declared["REGISTERS"],
                         {"content-web": True, "precision": True})

    def test_other_lines_untouched(self) -> None:
        before = parse_genome(lean_text()).declared
        after = parse_genome(lean_text("REGISTERS muse")).declared
        self.assertEqual({k: v for k, v in after.items() if k != "REGISTERS"}, before,
                         "every other declared key is byte-identical beside the new line")


class GarbageRefusedByName(unittest.TestCase):
    def test_bare_line_refused(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(lean_text("REGISTERS"))
        self.assertIn("REGISTERS", str(cm.exception))

    def test_unknown_word_refused(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(lean_text("REGISTERS trajectory"))
        self.assertIn("trajectory", str(cm.exception))

    def test_underscore_form_refused(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(lean_text("REGISTERS content_web"))
        self.assertIn("content_web", str(cm.exception))

    def test_repeated_word_refused(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(lean_text("REGISTERS muse muse"))
        self.assertIn("muse", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
