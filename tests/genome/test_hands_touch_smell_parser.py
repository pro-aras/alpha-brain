# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 2/3/4:
# the parser side of HANDS's extended grammar (jail <path> shelf <dir> cpu <n> mem <n> wall <n>) and the two
# new SENSE shapes (smell, touch). The pre-existing SHORT form of HANDS ("HANDS jail <path>", no shelf/cpu/
# mem/wall) must keep parsing to EXACTLY {"jail": <path>} -- tests/genome/test_parse_g4.py:111's own pin
# against tests/genome/G4-draft.genome, untouched by this brief.
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
G5_GENOME_PATH = ROOT / "genome" / "G5.genome"


def _replace_line(text: str, prefix: str, new_line: str) -> str:
    out, replaced = [], False
    for line in text.splitlines():
        if line.strip().startswith(prefix):
            out.append(new_line)
            replaced = True
        else:
            out.append(line)
    assert replaced, f"no {prefix!r} line found to replace"
    return "\n".join(out) + "\n"


def _add_line(text: str, new_line: str) -> str:
    return text.rstrip("\n") + "\n" + new_line + "\n"


class TestHandsExtendedGrammar(unittest.TestCase):
    def test_short_form_still_parses_unchanged(self) -> None:
        """Regression: the short HANDS form (no shelf/cpu/mem/wall) is byte-identical to before this
        brief -- test_parse_g4.py's own pin, re-asserted here so a regex mistake fails loudly in BOTH
        places."""
        text = _add_line(G5_GENOME_PATH.read_text(), "HANDS jail alpha3/hands/jail_run")
        g = parse_genome(text)
        self.assertEqual(g.declared["HANDS"], {"jail": "alpha3/hands/jail_run"})

    def test_full_form_parses_shelf_cpu_mem_wall(self) -> None:
        text = _add_line(
            G5_GENOME_PATH.read_text(),
            "HANDS    jail alpha3/hands/jail_run shelf world/programs cpu 10 mem 512 wall 20",
        )
        g = parse_genome(text)
        self.assertEqual(
            g.declared["HANDS"],
            {"jail": "alpha3/hands/jail_run", "shelf": "world/programs", "cpu": 10, "mem": 512, "wall": 20},
        )

    def test_malformed_full_form_refuses(self) -> None:
        text = _add_line(G5_GENOME_PATH.read_text(), "HANDS    jail alpha3/hands/jail_run shelf world/programs cpu ten mem 512 wall 20")
        with self.assertRaises(GenomeError):
            parse_genome(text)

    def test_shelf_without_cpu_mem_wall_refuses(self) -> None:
        text = _add_line(G5_GENOME_PATH.read_text(), "HANDS    jail alpha3/hands/jail_run shelf world/programs")
        with self.assertRaises(GenomeError):
            parse_genome(text)


class TestSenseSmell(unittest.TestCase):
    def test_smell_parses(self) -> None:
        text = _add_line(G5_GENOME_PATH.read_text(), "SENSE    smell kind size folder age")
        g = parse_genome(text)
        self.assertEqual(g.declared["SENSE_SMELL"], {"fields": ["kind", "size", "folder", "age"]})

    def test_smell_garbage_refuses(self) -> None:
        text = _add_line(G5_GENOME_PATH.read_text(), "SENSE    smell kind size folder ageXXX")
        with self.assertRaises(GenomeError):
            parse_genome(text)

    def test_smell_wrong_order_refuses(self) -> None:
        text = _add_line(G5_GENOME_PATH.read_text(), "SENSE    smell size kind folder age")
        with self.assertRaises(GenomeError):
            parse_genome(text)


class TestSenseTouch(unittest.TestCase):
    def test_touch_parses(self) -> None:
        text = _add_line(G5_GENOME_PATH.read_text(), "SENSE    touch from hands: exit rate stalls retries bytes")
        g = parse_genome(text)
        self.assertEqual(
            g.declared["SENSE_TOUCH"],
            {"from": "hands", "fields": ["exit", "rate", "stalls", "retries", "bytes"]},
        )

    def test_touch_garbage_refuses(self) -> None:
        text = _add_line(G5_GENOME_PATH.read_text(), "SENSE    touch from hands: exit rate stalls retries")
        with self.assertRaises(GenomeError):
            parse_genome(text)


if __name__ == "__main__":
    unittest.main()
