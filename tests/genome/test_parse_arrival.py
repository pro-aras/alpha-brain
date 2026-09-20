# edit: Claude (Fable 5.1), 2026-09-20 12:01 +0400 — PREREG §15 (Amendment 5): the ARRIVAL gene's parser clause.
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]


class TestArrivalParses(unittest.TestCase):
    def test_declared_rule(self) -> None:
        g = parse_genome((ROOT / "genome" / "G4.genome").read_text())
        self.assertEqual(g.declared["ARRIVAL"], {"rule": "never-heard word"})

    def test_misspelt_rule_refused_by_name(self) -> None:
        base = (ROOT / "tests" / "creature" / "G4-wave2-test.genome").read_text()
        with self.assertRaises(GenomeError) as cm:
            parse_genome(base + "\nARRIVAL  by schedule\n")
        self.assertIn("ARRIVAL", str(cm.exception))

    def test_pin_genomes_never_declare_it(self) -> None:
        for name in ("G4-skeleton.genome", "G1.genome"):
            g = parse_genome((ROOT / "genome" / name).read_text())
            self.assertNotIn("ARRIVAL", g.declared, name)


if __name__ == "__main__":
    unittest.main()
