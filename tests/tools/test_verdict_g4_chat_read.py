# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 12:00 +0400 — A4L-LANG task 7: the reader's LAST link (#180) —
# tools/verdict_g4.py:chat_read gathers a real record (chat/out written by the mind, chat/truth by the seat, the pictures, the
# tape, the live journal, the blind-chat twin's journal as the verdict's worker writes it) and grades it; a record without CHAT
# reads «not gradable» and adds nothing to the verdict's failed list.
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from creature import replay
from creature.mind import Mind
from creature.tape import read_tape
from genome.machinery import parse_genome
from tests.creature import _chat_tape as T
from tools import chat_seat
from tools import verdict_g4


class TestChatRead(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp())
        tape = T.build(cls.root, per_thing=15, lines=T.lines_it_is(30))
        for k, (thing, text) in enumerate((("star", "what is this"), ("ring", "is this a cross"))):
            plan = {"id": f"c{k:04d}", "family": "what-is" if k == 0 else "yes-no", "thing": thing, "lure": None if k == 0 else "cross",
                    "options": [], "phrasing": text, "text": text, "picture": T.held_render(thing, 20 + k),
                    "bboxes": {thing: [0, 0, 32, 32]}}
            chat_seat.write_chat(cls.root, plan)
            T.drop_chat(cls.root, tape, plan["id"], text, plan["picture"])
        mind = Mind(T.LANG_GENOME, cls.root)
        cls.rows = list(read_tape(cls.root))
        for r in cls.rows:
            mind.consume(r)
        mind.close()
        cls.live = replay.read_mind_journal(next((cls.root / "journal").glob("*.jsonl")))
        cls.twins = Path(tempfile.mkdtemp())
        tw_root = cls.twins / "blind-chat"; (tw_root / "tape").mkdir(parents=True)
        (tw_root / "tape" / "payload").symlink_to((cls.root / "tape" / "payload").resolve())
        tw = Mind(T.LANG_GENOME, tw_root, blind=frozenset({"chat"}))
        for r in cls.rows:
            tw.consume(r)
        tw.close()
        rows = [json.loads(l) for l in next((tw_root / "journal").glob("*.jsonl")).read_text().splitlines() if l.strip()]
        (tw_root / "mind-journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows if "event" not in r))
        cls.decl = parse_genome(T.LANG_GENOME.read_text()).declared

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.root, ignore_errors=True); shutil.rmtree(cls.twins, ignore_errors=True)

    def test_the_record_is_read_and_l1_holds_on_the_real_twin(self) -> None:
        C = verdict_g4.chat_read(self.root, self.rows, self.live, [], self.decl, self.twins, 0.78, T.AT)
        self.assertNotIn("error", C, C.get("error"))
        self.assertTrue(C["L1"]["graded"]); self.assertTrue(C["L1"]["pass"], C["L1"])
        self.assertEqual(C["L1"]["say_rows"], 2)
        self.assertTrue(C["L7"]["graded"])
        self.assertEqual(C["disjoint"]["checked"], 2); self.assertTrue(C["disjoint"]["ok"]); self.assertTrue(C["disjoint"]["control_caught"])
        self.assertTrue(C["graded"])

    def test_without_the_twin_l1_fails_by_name(self) -> None:
        C = verdict_g4.chat_read(self.root, self.rows, self.live, [], self.decl, Path(tempfile.mkdtemp()), 0.78, T.AT)
        self.assertFalse(C["L1"]["pass"]); self.assertIn("not run", C["L1"]["reason"]); self.assertFalse(C["pass"])

    def test_a_record_without_chat_is_not_gradable_and_never_fails_the_verdict(self) -> None:
        floor = parse_genome(T.FLOOR_GENOME.read_text()).declared
        C = verdict_g4.chat_read(self.root, self.rows, self.live, [], floor, self.twins, 0.78, T.AT)
        self.assertFalse(C["graded"]); self.assertFalse(any(C[k]["graded"] for k in ("L1", "L2", "L7")))


if __name__ == "__main__":
    unittest.main()
