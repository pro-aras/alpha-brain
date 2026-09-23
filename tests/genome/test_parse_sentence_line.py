# edit: Claude (Fable 5.1, A42 builder B2), 2026-09-23 17:1x +0400 — A42-B2 PART 1 (ALPHA4-2-PREREG §2 G9 "the LINE scorer"): the
# SENTENCE line gains ONE optional clause, `judged by the eye on the line` — a shelf frame is due on the reader's SENTENCE moment
# (the rendered line, a multi-word shelf instant), never on a one-word per-word moment of the same chunk, and its evidence is ANY
# of the line's located glances recalling a cell of w2. Its CEILING was measured first (scratch/b2/ceiling.py; A42-B2-REPORT):
# 0.272 on a copy of alpha4-1's 10:54 snapshot (86/316, strict decider, located glances), 0.545 on the hour-1 replay (6/11);
# the old decider's evidence (glance 0 only) reads 0.089 on the same lines — below the 0.1 bar — so the clause's evidence is
# "any located glance", by measurement. RED first: the new text was refused by the parser's fullmatch before this build.
"""tests/genome/test_parse_sentence_line.py — the parser half of G9."""
from __future__ import annotations

import unittest

from genome.machinery import GenomeError, parse_genome
from tests.genome._toy import MINI_GENOME_TEXT

OLD = "SENTENCE two-word frames from co-occurring words; judged by the eye; never next-token"
NEW = "SENTENCE two-word frames from co-occurring words; judged by the eye on the line; never next-token"


def _with(line: str):
    return parse_genome(MINI_GENOME_TEXT + line + "\n")


class TestSentenceLineClause(unittest.TestCase):
    def test_the_old_line_parses_to_exactly_what_it_always_did(self) -> None:
        """No new key on the old line: every genome on disk declares the SAME dict it declared before this build."""
        g = _with(OLD)
        self.assertEqual(g.declared["SENTENCE"], {"frames": "co-occurring", "judged": "eye", "next_token": False})

    def test_the_line_clause_parses_and_is_named(self) -> None:
        g = _with(NEW)
        self.assertEqual(g.declared["SENTENCE"], {"frames": "co-occurring", "judged": "eye", "next_token": False, "line": True})

    def test_a_garbled_clause_is_refused_by_name(self) -> None:
        for bad in ("SENTENCE two-word frames from co-occurring words; judged by the eye on the lines; never next-token",
                    "SENTENCE two-word frames from co-occurring words; judged on the line; never next-token",
                    "SENTENCE two-word frames from co-occurring words; judged by the eye on the line"):
            with self.assertRaises(GenomeError, msg=bad):
                _with(bad)


if __name__ == "__main__":
    unittest.main()
