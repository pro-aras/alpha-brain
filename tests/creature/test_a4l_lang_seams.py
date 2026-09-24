# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:53 +0400 — A4L-LANG task 9 (docs/briefs/A4L-LANG.md): the seams
# where the chat road meets every organ it must NOT move — tested at the seam, on one learned record with chats interleaved,
# beside its own blind-chat twin (the same rows, the chats ignored).
from __future__ import annotations

import json
import shutil
import tempfile
import threading
import time
import unittest
import unittest.mock as mock
from pathlib import Path

import numpy as np

from creature import ask as ask_door
from creature import replay
from creature.body import Body
from creature.mind import Mind
from creature.senses import chat as chat_sense
from creature.tape import Tape, read_tape
from genome import gaze, world
from genome.sentence import find_frames
from tests.creature import _chat_tape as T


def _mouth_says(journal):
    return [(j["seq"], j["say"].get("frame"), j["say"].get("heard"), tuple(j["say"].get("episodes") or []))
            for j in journal if isinstance(j.get("say"), dict) and j["say"].get("kind") != "chat"]


class TestSeamsOnOneRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp())
        tape = T.build(cls.root, per_thing=15, lines=T.lines_it_is(30))
        T.drop_chat(cls.root, tape, "c0001", "what is this", T.held_render("star", 1))
        T.drop_grade(cls.root, tape, "c0001", True, False)
        tape = T.build(cls.root, per_thing=15, lines=T.lines_it_is(30, fillers=30), k0=5000)
        T.drop_chat(cls.root, tape, "c0002", "is it a ring or a cross", T.held_render("ring", 2))
        tape = T.build(cls.root, per_thing=10, lines=T.lines_it_is(30, fillers=30), k0=9000)
        cls.rows = list(read_tape(cls.root))
        cls.mind = Mind(T.LANG_GENOME, cls.root)
        for r in cls.rows:
            cls.mind.consume(r)
        cls.live = T.journal_rows(cls.root)
        cls.twin_root = Path(tempfile.mkdtemp()); (cls.twin_root / "tape").mkdir()
        (cls.twin_root / "tape" / "payload").symlink_to((cls.root / "tape" / "payload").resolve())
        cls.twin = Mind(T.LANG_GENOME, cls.twin_root, blind=frozenset({"chat"}))
        for r in cls.rows:
            cls.twin.consume(r)
        cls.twin_journal = T.journal_rows(cls.twin_root)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mind.close(); cls.twin.close()
        shutil.rmtree(cls.root, ignore_errors=True); shutil.rmtree(cls.twin_root, ignore_errors=True)

    def test_chat_x_mouth_the_think_mouths_says_are_unchanged(self) -> None:
        live, twin = _mouth_says(self.live), _mouth_says(self.twin_journal)
        self.assertGreaterEqual(len(live), 1, "a seam test with no think-mouth say would prove nothing")
        self.assertEqual(live, twin, "the same say rows at the same seqs")
        self.assertEqual(self.mind.think_counters["said"], self.twin.think_counters["said"])

    def test_the_whole_non_chat_journal_is_the_twins_including_hash(self) -> None:
        self.assertIsNone(replay.compare(self.twin_journal, [j for j in self.live if not replay.is_chat_journal_row(j)]))
        self.assertEqual(self.mind.org.state_hash(), self.twin.org.state_hash())

    def test_chat_x_readiness_a_chat_grade_never_moves_d(self) -> None:
        self.assertEqual((self.mind._grades_total, self.mind._grades_right, list(self.mind._novel_grades)),
                         (self.twin._grades_total, self.twin._grades_right, list(self.twin._novel_grades)))
        self.assertEqual(self.mind._readiness_readings(), self.twin._readiness_readings())
        self.assertEqual(self.mind.chat_counters["graded"], 1)

    def test_chat_x_sentence_the_frames_are_the_same_before_and_after_a_chat(self) -> None:
        tape = Tape(self.root)
        before = find_frames(self.mind.episodes); n = self.mind.episodes.n_written
        self.mind.consume(T.drop_chat(self.root, tape, "s0101", "what is this", T.held_render("cross", 9)))
        self.assertEqual(find_frames(self.mind.episodes), before)
        self.assertEqual(self.mind.episodes.n_written, n)
        self.assertGreaterEqual(len(before), 1)

    def test_chat_x_surprise_and_predict_no_expectation_is_written_or_read(self) -> None:
        tape = Tape(self.root)
        m = self.mind
        lw = m.predictor._last_winner.copy() if m.predictor._last_winner is not None else None
        exp = {t: m.org.expected_sight(world.encode_word(t)) for t in T.THINGS}
        conf = (m.glances_confirmed, m.glances_surprised)
        seen = []
        real = gaze.glances
        def spy(*a, **k):
            seen.append(k.get("predicted")); return real(*a, **k)
        with mock.patch.object(gaze, "glances", spy):
            m.consume(T.drop_chat(self.root, tape, "s0102", "what is this", T.held_render("ring", 10)))
        self.assertEqual(seen, [None], "the chat glances with NO expectation (SURPRISE's residual is never computed for a chat)")
        self.assertTrue((lw is None and m.predictor._last_winner is None) or np.array_equal(lw, m.predictor._last_winner))
        for t in T.THINGS:
            a, b = exp[t], m.org.expected_sight(world.encode_word(t))
            self.assertTrue((a is None and b is None) or np.array_equal(a, b), t)
        self.assertEqual((m.glances_confirmed, m.glances_surprised), conf)


class TestChatXAskDoor(unittest.TestCase):
    def test_the_two_inboxes_are_independent(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "chat" / "in").mkdir(parents=True); (root / "ask" / "in").mkdir(parents=True)
        (root / "chat" / "in" / "c0001.json").write_text(json.dumps({"id": "c0001", "text": "what is this"}))
        (root / "ask" / "in" / "a1.json").write_text(json.dumps({"q": "show", "word": "ring"}))
        rows = []
        chat_sense.scan_once(lambda s, p, m, e: rows.append((s, m)) or {"seq": 1}, root)
        self.assertEqual([(s, m["id"]) for s, m in rows], [("chat", "c0001")], "the chat door never reads ask/in")

        class Once:
            def __init__(self): self.n = 0
            def is_set(self): self.n += 1; return self.n > 1
            def wait(self, t): pass
        ask_door.inbox_loop(root, Once())
        self.assertEqual(sorted(p.name for p in (root / "ask" / "out").glob("*.json")), ["a1.json"], "the ask door answers only ask/in")
        self.assertFalse((root / "chat" / "out").exists(), "the ask door never writes the chat's outbox")
        shutil.rmtree(root, ignore_errors=True)


class TestChatXGrow(unittest.TestCase):
    def test_a_chat_right_after_a_growth_step_reads_the_grown_organism(self) -> None:
        root = Path(tempfile.mkdtemp())
        T.build(root, things=world.THINGS_11, per_thing=20, lines=T.lines_varied(160))   # rendered text births: GROW's first doubling (256) is crossed
        mind = Mind(T.LANG_GENOME, root); tape = Tape(root)
        cap0 = mind.org.sight.nmax; grew_at = None
        for r in read_tape(root):
            mind.consume(r)
            if r["sense"] == "eye" and mind.org.sight.nmax > cap0:
                grew_at = r["seq"]; break
        self.assertIsNotNone(grew_at, "the record must cross a GROW step (a seam test that never grows proves nothing)")
        self.assertGreater(mind.org.sight.n, cap0)
        last_hash = [j["hash"] for j in T.journal_rows(root) if "hash" in j][-1]
        mind.consume(T.drop_chat(root, tape, "g1", "what is this", T.held_render("star", 11)))
        say = [j for j in T.journal_rows(root) if isinstance(j.get("say"), dict) and j["say"].get("kind") == "chat"][-1]["say"]
        self.assertEqual(say["hash_before"], last_hash, "the chat read the organism exactly as the growth step left it")
        self.assertEqual(say["hash_after"], say["hash_before"])
        mind.close(); shutil.rmtree(root, ignore_errors=True)

    def test_the_one_writer_law_a_chat_is_consumed_on_the_mind_thread_in_tape_order(self) -> None:
        """Through a real Body: the door publishes onto the tape; the ONE mind thread consumes the chat at its own seq,
        after every row before it — the say row's hash_before is the hash the previous hashed row journaled."""
        root = Path(tempfile.mkdtemp())
        body = Body(root, T.LANG_GENOME)
        body.start()
        try:
            for k in range(12):
                rgb, _t = world.render_canvas(T.THINGS[k % 3], np.random.default_rng([7, k]))
                m = f"w0000i{k:06d}t{k:09d}"
                body._publish("ear", T.THINGS[k % 3].encode(), {"moment": m, "source": "maker", "word": T.THINGS[k % 3]}, "txt")
                body._publish("eye", T._png(rgb), {"moment": m, "source": "maker"}, "png")
            (root / "chat" / "in").mkdir(parents=True, exist_ok=True)
            (root / "chat" / "in" / "b1.json").write_text(json.dumps({"id": "b1", "text": "hello"}))
            chat_sense.scan_once(body._publish, root)
            deadline = time.time() + 60
            while time.time() < deadline and not (root / "chat" / "out" / "b1.json").exists():
                time.sleep(0.2)
            self.assertTrue((root / "chat" / "out" / "b1.json").exists())
            rows = T.journal_rows(root)
            i = next(n for n, j in enumerate(rows) if isinstance(j.get("say"), dict) and j["say"].get("kind") == "chat")
            prev = [j["hash"] for j in rows[:i] if "hash" in j][-1]
            self.assertEqual(rows[i]["say"]["hash_before"], prev)
            self.assertEqual(threading.current_thread().name, "MainThread")
        finally:
            body.stop(); shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
