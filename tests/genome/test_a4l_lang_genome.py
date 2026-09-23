# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:27 +0400 — A4-LADDER-PREREG §1.1 (the ladder law: ONE
# difference) pinned for the LANG rung: `difflib` between genome/ladder/A4L-LANG.genome and the FLOOR shows exactly the
# declared CHAT line and one edit-note header line — nothing removed, nothing else added.
from __future__ import annotations

import difflib
import unittest
from pathlib import Path

from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
FLOOR = ROOT / "genome" / "ladder" / "A4L-FLOOR.genome"
LANG = ROOT / "genome" / "ladder" / "A4L-LANG.genome"

CHAT_LINE = ("CHAT door chat/in chat/out; chain of frames + one pivot slot; links adjacent 5; "
             "pivot 10 distinct 20 instants; at most 6 words; a question never teaches")


class TestOneDifference(unittest.TestCase):
    def _diff(self):
        a = FLOOR.read_text().splitlines(); b = LANG.read_text().splitlines()
        return [l for l in difflib.ndiff(a, b) if l[:2] in ("+ ", "- ")]

    def test_nothing_of_the_floor_is_removed_or_changed(self) -> None:
        self.assertEqual([l for l in self._diff() if l.startswith("- ")], [])

    def test_exactly_two_lines_added_the_chat_line_and_one_header_note(self) -> None:
        added = [l[2:] for l in self._diff() if l.startswith("+ ")]
        self.assertEqual(len(added), 2, added)
        chat = [l for l in added if l.startswith("CHAT ")]
        notes = [l for l in added if l.startswith("#")]
        self.assertEqual(len(chat), 1, added)
        self.assertEqual(len(notes), 1, added)
        self.assertEqual(chat[0].split("#", 1)[0].split(), CHAT_LINE.split(), "the CHAT line must be the brief's line verbatim")

    def test_the_lang_genome_parses_as_the_floor_plus_chat(self) -> None:
        f = parse_genome(FLOOR.read_text()).declared
        g = parse_genome(LANG.read_text()).declared
        self.assertEqual(set(g) - set(f), {"CHAT"})
        self.assertEqual({k: g[k] for k in f}, f)


if __name__ == "__main__":
    unittest.main()
