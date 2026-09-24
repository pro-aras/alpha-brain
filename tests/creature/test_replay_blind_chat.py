# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:40 +0400 — A4L-LANG task 7 (docs/briefs/A4L-LANG.md;
# A4-LADDER-PREREG §3.4 L1): the READ-ONLY law's replay twin. `--blind chat` removes every `chat` row and every kind-chat
# `grade` row from the tape before the replay (and the Mind is blind to them besides); its journal must equal the live
# journal's NON-chat rows field for field INCLUDING `hash`. Both roads (the filtered tape; the blind Mind on the whole
# tape) must agree, and the unblinded replay must reproduce the live journal, chat rows included (REPLAY identity).
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from creature import replay
from creature.mind import Mind
from creature.tape import read_tape
from tests.creature import _chat_tape as T


class TestBlindChatTwin(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp())
        tape = T.build(cls.root, per_thing=20, lines=T.lines_it_is(30))
        T.drop_chat(cls.root, tape, "c0001", "what is this", T.held_render("star", 1))
        T.drop_grade(cls.root, tape, "c0001", True, False)
        tape = T.build(cls.root, per_thing=10, k0=1000)
        T.drop_chat(cls.root, tape, "c0002", "is it a ring or a cross", T.held_render("ring", 2))
        T.drop_chat(cls.root, tape, "s0001", "hello there")
        T.drop_grade(cls.root, tape, "s0001", False, True)
        T.build(cls.root, per_thing=10, k0=2000)
        mind = Mind(T.LANG_GENOME, cls.root)
        for row in read_tape(cls.root):
            mind.consume(row)
        cls.live = T.journal_rows(cls.root)
        cls.tape_path = cls.root / "tape" / f"{T.AT[:10]}.jsonl"
        cls.work = Path(tempfile.mkdtemp())
        cls.blind = replay.read_mind_journal(replay.run_replay(T.LANG_GENOME, cls.tape_path, cls.work / "blind", blind=frozenset({"chat"})))
        cls.full = replay.read_mind_journal(replay.run_replay(T.LANG_GENOME, cls.tape_path, cls.work / "full"))
        mind.close()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.root, ignore_errors=True); shutil.rmtree(cls.work, ignore_errors=True)

    def test_the_live_record_carries_its_chats(self) -> None:
        says = [j for j in self.live if replay.is_chat_journal_row(j) and "say" in j]
        grades = [j for j in self.live if replay.is_chat_journal_row(j) and "grade" in j]
        self.assertEqual((len(says), len(grades)), (3, 2))

    def test_the_blind_twin_equals_the_live_non_chat_rows_including_hash(self) -> None:
        live_non_chat = [j for j in self.live if not replay.is_chat_journal_row(j)]
        self.assertTrue(any("hash" in j for j in live_non_chat))
        self.assertIsNone(replay.compare(self.blind, live_non_chat), "L1: the chat-dropped twin must reproduce every other row")
        self.assertFalse(any(replay.is_chat_journal_row(j) for j in self.blind))

    def test_the_unblinded_replay_reproduces_the_live_journal_chats_included(self) -> None:
        self.assertIsNone(replay.compare(self.full, self.live))

    def test_a_physically_filtered_tape_gives_the_same_twin(self) -> None:
        rows = [json.loads(l) for l in self.tape_path.read_text().splitlines() if l.strip()]
        kept = [r for r in rows if not replay.is_chat_row(r)]
        self.assertEqual(len(rows) - len(kept), 5)
        filt = self.tape_path.parent / "FILTERED.jsonl"
        filt.write_text("".join(json.dumps(r) + "\n" for r in kept))
        got = replay.read_mind_journal(replay.run_replay(T.LANG_GENOME, filt, self.work / "filtered"))
        filt.unlink()
        self.assertIsNone(replay.compare(got, self.blind))

    def test_the_cli_takes_blind_chat(self) -> None:
        live_non_chat = self.work / "live-non-chat.jsonl"
        live_non_chat.write_text("".join(json.dumps(j) + "\n" for j in self.live if not replay.is_chat_journal_row(j)))
        rc = replay.main(["--genome", str(T.LANG_GENOME), "--tape", str(self.tape_path), "--out", str(self.work / "cli"),
                          "--blind", "chat", "--against", str(live_non_chat)])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
