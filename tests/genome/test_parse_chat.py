# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:27 +0400 — A4L-LANG task 1 (docs/briefs/A4L-LANG.md;
# docs/A4-LADDER-PREREG.md §3.2): the CHAT gene's parser branch. Every number on the line is a clause the parser
# reads; a mis-spelt form REFUSES with a named error; a genome that never declares CHAT is byte-identical (the
# negative control: the FLOOR's declared dict is exactly what it was).
from __future__ import annotations

import unittest
from pathlib import Path

from creature import genes as genes_module
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
FLOOR = ROOT / "genome" / "ladder" / "A4L-FLOOR.genome"

CHAT_LINE = ("CHAT door chat/in chat/out; chain of frames + one pivot slot; links adjacent 5; "
             "pivot 10 distinct 20 instants; at most 6 words; a question never teaches")


def _with(line: str) -> str:
    return FLOOR.read_text().rstrip("\n") + "\n" + line + "\n"


class TestChatParses(unittest.TestCase):
    def test_the_line_verbatim_parses_to_its_numbers(self) -> None:
        g = parse_genome(_with(CHAT_LINE))
        self.assertEqual(g.declared["CHAT"], {
            "in": "chat/in", "out": "chat/out", "links_adjacent": 5, "pivot_distinct": 10,
            "pivot_instants": 20, "max_words": 6, "teaches": False,
        })

    def test_every_number_is_read(self) -> None:
        line = CHAT_LINE.replace("adjacent 5", "adjacent 7").replace("pivot 10", "pivot 12") \
                        .replace("distinct 20", "distinct 30").replace("at most 6", "at most 5")
        d = parse_genome(_with(line)).declared["CHAT"]
        self.assertEqual((d["links_adjacent"], d["pivot_distinct"], d["pivot_instants"], d["max_words"]), (7, 12, 30, 5))

    def test_the_door_paths_are_read(self) -> None:
        d = parse_genome(_with(CHAT_LINE.replace("chat/in chat/out", "talk/in talk/out"))).declared["CHAT"]
        self.assertEqual((d["in"], d["out"]), ("talk/in", "talk/out"))

    def test_extra_whitespace_is_the_same_line(self) -> None:
        g = parse_genome(_with(CHAT_LINE.replace("; ", ";   ").replace("CHAT door", "CHAT     door")))
        self.assertEqual(g.declared["CHAT"]["max_words"], 6)

    def test_a_trailing_comment_is_a_comment(self) -> None:
        g = parse_genome(_with(CHAT_LINE + "   # A4L-LANG"))
        self.assertIn("CHAT", g.declared)

    def test_a_declared_chat_has_a_real_site(self) -> None:
        """W3-0's generic refusal (creature/genes.py:unwired) must find CHAT wired."""
        self.assertEqual(genes_module.unwired(parse_genome(_with(CHAT_LINE)).declared), [])


class TestChatRefusesMisspelt(unittest.TestCase):
    BAD = [
        CHAT_LINE.replace("a question never teaches", "a question teaches"),
        CHAT_LINE.replace("; a question never teaches", ""),
        CHAT_LINE.replace("chain of frames + one pivot slot", "chain of frames + two pivot slots"),
        CHAT_LINE.replace("links adjacent 5", "links adjacent five"),
        CHAT_LINE.replace("links adjacent 5", "links adjacent"),
        CHAT_LINE.replace("20 instants", "20 instant"),
        CHAT_LINE.replace("at most 6 words", "at most 6 word"),
        CHAT_LINE.replace("pivot 10 distinct", "pivot distinct"),
        CHAT_LINE.replace("door chat/in chat/out", "door chat/in"),
        CHAT_LINE.replace("door ", "doors "),
        "CHAT",
    ]

    def test_each_misspelt_form_refuses_by_name(self) -> None:
        for bad in self.BAD:
            with self.subTest(line=bad):
                with self.assertRaises(GenomeError) as ctx:
                    parse_genome(_with(bad))
                self.assertTrue(str(ctx.exception).startswith("CHAT"), str(ctx.exception))   # from the CHAT branch, never "unknown gene"

    def test_zero_and_escaping_values_refuse(self) -> None:
        for bad in (CHAT_LINE.replace("links adjacent 5", "links adjacent 0"),
                    CHAT_LINE.replace("pivot 10", "pivot 0"),
                    CHAT_LINE.replace("distinct 20", "distinct 0"),
                    CHAT_LINE.replace("at most 6", "at most 1"),
                    CHAT_LINE.replace("chat/in chat/out", "/abs/in chat/out"),
                    CHAT_LINE.replace("chat/in chat/out", "../in chat/out"),
                    CHAT_LINE.replace("chat/in chat/out", "chat/in chat/in")):
            with self.subTest(line=bad):
                with self.assertRaises(GenomeError) as ctx:
                    parse_genome(_with(bad))
                self.assertTrue(str(ctx.exception).startswith("CHAT"), str(ctx.exception))


class TestUndeclaredIsUntouched(unittest.TestCase):
    def test_the_floor_declares_no_chat(self) -> None:
        g = parse_genome(FLOOR.read_text())
        self.assertNotIn("CHAT", g.declared)

    def test_declaring_chat_adds_exactly_one_key(self) -> None:
        base = parse_genome(FLOOR.read_text()).declared
        with_chat = parse_genome(_with(CHAT_LINE)).declared
        self.assertEqual(set(with_chat) - set(base), {"CHAT"})
        for k in base:
            self.assertEqual(with_chat[k], base[k], k)


if __name__ == "__main__":
    unittest.main()
