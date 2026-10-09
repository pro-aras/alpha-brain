# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 20:56 +0400 — PREREG-ALPHA-6 §2 B1 (the law SIGNED; SEAT-LINE
# sha256 1d00a35f…; test-first): the MOUTH line's ONE new optional word «incremental» — the rung's clause the mouth
# verdict (VERDICT-MOUTH-INCREMENTAL, PASS) opened. Absent: the declared dict is EXACTLY the old one, every genome on
# disk byte-identical; present: ONE more key. A misspelt clause refuses BY NAME.
"""tests/genome/test_parse_mouth_incremental.py — the MOUTH clause «incremental» (PREREG-ALPHA-6 §1.3/§2 B1).

The line's full form: `MOUTH    say one frame per think and the brain's phrase per canvas; journaled; incremental`.
The clause selects learners.produce_incremental at genome/brain.py's two `produce_believed` call sites (the
selection itself is pinned in tests/genome/test_brain_mouth_incremental.py and
tests/creature/test_mouth_incremental_mind.py); here the parser, whole and only."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE = (ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()
LEAN, _n = re.subn(r"^DRIVE    .*\n", "", _TEMPLATE, count=1, flags=re.M)
assert _n == 1, "the lean template carries one DRIVE line"

MOUTH_OLD = "MOUTH    say one frame per think; journaled"
MOUTH_VOICE = "MOUTH    say one frame per think and the brain's phrase per canvas; journaled"
MOUTH_OLD_INC = "MOUTH    say one frame per think; journaled; incremental"
MOUTH_VOICE_INC = "MOUTH    say one frame per think and the brain's phrase per canvas; journaled; incremental"


def lean_text(*lines: str) -> str:
    return LEAN + "\n" + ("\n".join(lines) + "\n" if lines else "")


class TheOldSpellingsAreByteIdentical(unittest.TestCase):
    def test_the_old_spelling_parses_to_exactly_the_old_dict(self) -> None:
        self.assertEqual(parse_genome(lean_text(MOUTH_OLD)).declared["MOUTH"],
                         {"say": "one frame per think", "journaled": True})

    def test_the_voice_spelling_parses_to_exactly_its_old_dict(self) -> None:
        self.assertEqual(parse_genome(lean_text(MOUTH_VOICE)).declared["MOUTH"],
                         {"say": "one frame per think", "journaled": True, "brain": "phrase per canvas"})


class TheClause(unittest.TestCase):
    def test_the_clause_adds_exactly_one_key_on_the_bare_spelling(self) -> None:
        self.assertEqual(parse_genome(lean_text(MOUTH_OLD_INC)).declared["MOUTH"],
                         {"say": "one frame per think", "journaled": True, "incremental": True})

    def test_the_clause_adds_exactly_one_key_on_the_voice_spelling(self) -> None:
        self.assertEqual(parse_genome(lean_text(MOUTH_VOICE_INC)).declared["MOUTH"],
                         {"say": "one frame per think", "journaled": True, "brain": "phrase per canvas",
                          "incremental": True})

    def test_the_one_difference_is_the_mouth_key(self) -> None:
        a = parse_genome(lean_text(MOUTH_VOICE)).declared
        b = parse_genome(lean_text(MOUTH_VOICE_INC)).declared
        self.assertEqual({k: v for k, v in b.items() if k != "MOUTH"}, {k: v for k, v in a.items() if k != "MOUTH"})
        self.assertEqual(set(b["MOUTH"]) - set(a["MOUTH"]), {"incremental"})

    def test_every_misspelling_refuses_by_name(self) -> None:
        for bad in ("MOUTH    say one frame per think; journaled; incrementa",
                    "MOUTH    say one frame per think; journaled; incrementals",
                    "MOUTH    say one frame per think; journaled; incrementally",
                    "MOUTH    say one frame per think; journaled; incremental; incremental",
                    "MOUTH    say one frame per think; incremental; journaled",
                    "MOUTH    say one frame per think and the brain's phrase per canvas; incremental; journaled",
                    "MOUTH    say one frame per think; journaled; foo",
                    "MOUTH    say one frame per think; journaled incremental"):
            with self.subTest(line=bad):
                with self.assertRaises(GenomeError) as e:
                    parse_genome(lean_text(bad))
                self.assertIn("MOUTH", str(e.exception))

    def test_every_genome_on_disk_declares_it_exactly_when_its_line_says_so(self) -> None:
        # the clause is OPT-IN: for every genome on disk (BRAIN-LONG-5's own included), the parsed dict carries
        # the key iff the line carries the word — never silently, never by default.
        for gp in sorted((ROOT / "genome").rglob("*.genome")):
            with self.subTest(genome=gp.name):
                text = gp.read_text()
                d = parse_genome(text).declared
                self.assertEqual("incremental" in (d.get("MOUTH") or {}), "; incremental" in text, gp.name)


if __name__ == "__main__":
    unittest.main()
