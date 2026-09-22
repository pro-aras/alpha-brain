# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:32 +0400 — LIFE-D-ACT-SOUND.md item 3 (L-13):
# FAST's parser accepts the extra key `sound` (genome/LIFE.genome:51 "FAST episodes 20000 keys sight
# words surprise sound" — the DRAFT line another builder already wrote into the shared genome text; this
# is the parser change that makes it readable). Additive only: the plain "keys sight words surprise" line
# (no "sound") must keep parsing to exactly the same dict as before (test_parse_g4.py's own pin, line 98).
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME_PATH = ROOT / "genome" / "G4.genome"


def _replace_fast_line(genome_text: str, new_line: str) -> str:
    out = []
    replaced = False
    for line in genome_text.splitlines():
        if line.strip().startswith("FAST "):
            out.append(new_line)
            replaced = True
        else:
            out.append(line)
    assert replaced, "G4.genome must declare a FAST line for this test to replace"
    return "\n".join(out) + "\n"


class TestFastSoundKey(unittest.TestCase):
    def test_sound_key_parses_as_fourth_key(self) -> None:
        text = _replace_fast_line(G4_GENOME_PATH.read_text(), "FAST     episodes 20000 keys sight words surprise sound")
        g = parse_genome(text)
        self.assertEqual(g.declared["FAST"], {"episodes": 20000, "keys": ["sight", "words", "surprise", "sound"]})

    def test_plain_line_without_sound_is_unchanged(self) -> None:
        """Regression: the pre-existing line (no "sound") must still parse to exactly the old dict shape
        (test_parse_g4.py:98's own pin) -- the sound key is additive, never required."""
        g = parse_genome(G4_GENOME_PATH.read_text())
        self.assertEqual(g.declared["FAST"], {"episodes": 20000, "keys": ["sight", "words", "surprise"]})

    def test_garbage_after_surprise_still_refuses(self) -> None:
        text = _replace_fast_line(G4_GENOME_PATH.read_text(), "FAST     episodes 20000 keys sight words surprise xyz")
        with self.assertRaises(GenomeError):
            parse_genome(text)

    def test_sound_before_surprise_refuses(self) -> None:
        """The word order is fixed (sight words surprise sound), not an unordered set -- "sound surprise"
        must refuse exactly like any other malformed FAST line."""
        text = _replace_fast_line(G4_GENOME_PATH.read_text(), "FAST     episodes 20000 keys sight words sound surprise")
        with self.assertRaises(GenomeError):
            parse_genome(text)


if __name__ == "__main__":
    unittest.main()
