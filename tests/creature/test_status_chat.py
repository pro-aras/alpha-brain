# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:39 +0400 — A4L-LANG task 10 (docs/briefs/A4L-LANG.md):
# the ten chat keys on EVERY STATUS write (#164) — FLOOR included (zeros/None) — moving with the mind's own counters, and
# the counters surviving a resume under CHAT (the FLOOR's ledger.json byte-identical: no chat key without the gene).
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from creature.body import Body, CHAT_STATUS_KEYS
from creature.mind import Mind
from creature.tape import Tape
from tests.creature import _chat_tape as T


def _body(root: Path, genome: Path) -> Body:
    b = Body(root, genome)
    b.mind = Mind(genome, root)          # no threads: _build_status reads only the mind and the body's own counters
    return b


class TestChatStatus(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_the_ten_keys_are_on_a_floor_lifes_status(self) -> None:
        b = _body(self.root, T.FLOOR_GENOME)
        st = b._build_status()
        self.assertEqual(len(CHAT_STATUS_KEYS), 10)
        for k in CHAT_STATUS_KEYS:
            self.assertIn(k, st)
        self.assertEqual({k: st[k] for k in CHAT_STATUS_KEYS if k != "chat_words_mean"}, {k: 0 for k in CHAT_STATUS_KEYS if k != "chat_words_mean"})
        self.assertIsNone(st["chat_words_mean"], "no answer yet: no mean (never a fabricated 0, #175)")
        b.mind.close()

    def test_the_keys_move_with_the_minds_own_counters(self) -> None:
        tape = Tape(self.root)
        b = _body(self.root, T.LANG_GENOME)
        b.mind.consume(T.drop_chat(self.root, tape, "c0001", "what is this", T.held_render("ring")))
        b.mind.consume(T.drop_grade(self.root, tape, "c0001", False, True))
        st = b._build_status()
        self.assertEqual((st["chats"], st["chat_abstained"], st["chat_graded"], st["chat_graded_right"], st["chat_graded_novel"]), (1, 1, 1, 0, 1))
        b.mind.chat_counters.update({"answered": 2, "words_total": 7, "longest": 4})
        st = b._build_status()
        self.assertEqual((st["chat_answered"], st["chat_words_mean"], st["chat_longest"]), (2, 3.5, 4))
        b.mind.close()

    def test_the_counters_survive_a_resume_under_chat(self) -> None:
        m = Mind(T.LANG_GENOME, self.root)
        m.chat_counters.update({"chats": 5, "answered": 3, "abstained": 2, "words_total": 9, "longest": 4, "graded": 1})
        m.close()
        m2, _ = Mind.resume(T.LANG_GENOME, self.root)
        self.assertEqual(m2.chat_counters, m.chat_counters)
        m2.close()

    def test_the_floor_ledger_carries_no_chat_key(self) -> None:
        m = Mind(T.FLOOR_GENOME, self.root)
        m.close()
        self.assertNotIn("chat_counters", json.loads((self.root / "state" / "ledger.json").read_text()))


if __name__ == "__main__":
    unittest.main()
