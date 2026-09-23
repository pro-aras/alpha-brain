# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:36 +0400 — A4L-LANG tasks 3/5/10 (docs/briefs/A4L-LANG.md;
# docs/A4-LADDER-PREREG.md §3.2 items 2-6): the mind's READ-ONLY chat branch, test-first. «A question never teaches»: a
# chat row is routed to ONE branch that glances, reads, composes, judges, writes chat/out/<id>.json and journals ONE say
# row — and moves nothing (hash_before == hash_after, asserted; the mind-level road untouched).
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import chain
from tests.creature import _chat_tape as T


def _consume_all(mind: Mind, root: Path, after_seq: int = 0) -> None:
    for row in read_tape(root):
        if row["seq"] > after_seq:
            mind.consume(row)


def _road(mind: Mind) -> dict:
    """Everything the chat branch must never touch (the brief's list): the clock, the canvas index, the MEET road's
    pending words, the moment->word ledger, the heard set, every ring's size, the sleep cursor, the act census, the think
    counters, SURPRISE's counts, the READINESS judge's (d) tallies."""
    rings = {k: (getattr(mind, k).n_written if getattr(mind, k) is not None else None)
             for k in ("episodes", "outcome_episodes", "sound_episodes", "touch_episodes", "smell_episodes")}
    return {"t": mind.org.t, "canvas_index": mind._canvas_index, "pending": dict(mind.pending),
            "pending_words": {k: list(v) for k, v in mind.pending_words.items()}, "moment_word": len(mind.moment_word),
            "heard": sorted(mind._heard), "rings": rings, "last_sleep_at": mind._last_sleep_at, "sleeps": mind.sleep_count,
            "acts": dict(mind.acts_chosen), "think": dict(mind.think_counters), "confirmed": mind.glances_confirmed,
            "surprised": mind.glances_surprised, "grades": (mind._grades_total, mind._grades_right, list(mind._novel_grades)),
            "filed": len(mind._filed_predictions), "ask_out_n": mind._ask_out_n, "frames": sorted(mind._frames)}


class TestInertWithoutTheGene(unittest.TestCase):
    def test_the_floor_consumes_a_chat_row_and_writes_nothing(self) -> None:
        root = Path(tempfile.mkdtemp()); tape = Tape(root)
        row = T.drop_chat(root, tape, "c0001", "what is this", T.held_render("ring"))
        mind = Mind(T.FLOOR_GENOME, root)
        h, road = mind.org.state_hash(), _road(mind)
        mind.consume(row)
        self.assertEqual(T.journal_rows(root), [])
        self.assertFalse((root / "chat" / "out").exists())
        self.assertEqual(mind.org.state_hash(), h); self.assertEqual(_road(mind), road)
        self.assertEqual(mind.chat_counters["chats"], 0)
        mind.close(); shutil.rmtree(root, ignore_errors=True)


class TestOnAFreshOrganism(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp()); self.tape = Tape(self.root)
        self.mind = Mind(T.LANG_GENOME, self.root)

    def tearDown(self) -> None:
        self.mind.close(); shutil.rmtree(self.root, ignore_errors=True)

    def test_a_chat_is_one_say_row_and_one_out_file_and_moves_nothing(self) -> None:
        row = T.drop_chat(self.root, self.tape, "c0001", "what is this", T.held_render("ring"))
        h, road = self.mind.org.state_hash(), _road(self.mind)
        self.mind.consume(row)
        rows = T.journal_rows(self.root)
        self.assertEqual(len(rows), 1, rows)
        say = rows[0]["say"]
        self.assertEqual(rows[0]["seq"], row["seq"])
        self.assertEqual((say["kind"], say["id"], say["heard"]), ("chat", "c0001", ["what", "is", "this"]))
        self.assertEqual(say["hash_before"], say["hash_after"])
        self.assertEqual(say["hash_before"], h)
        self.assertIsNone(say["content"], "a newborn knows nothing")
        self.assertEqual(say["abstain_reason"], "novel")
        out = json.loads((self.root / "chat" / "out" / "c0001.json").read_text())
        self.assertEqual((out["id"], out["answer"], out["hash_before"]), ("c0001", None, h))
        self.assertEqual(self.mind.org.state_hash(), h)
        self.assertEqual(_road(self.mind), road)
        self.assertEqual({k: self.mind.chat_counters[k] for k in ("chats", "answered", "abstained")},
                         {"chats": 1, "answered": 0, "abstained": 1})
        for key in ("said", "heard_yes", "heard_no"):
            self.assertEqual(self.mind.think_counters[key], 0, "a chat say is never the think-mouth's say")
        self.assertNotIn("say", self.mind.acts_chosen)

    def test_the_mind_blind_to_chat_ignores_chats_and_chat_grades(self) -> None:
        mind = Mind(T.LANG_GENOME, self.root, blind=frozenset({"chat"}))
        mind.consume(T.drop_chat(self.root, self.tape, "c0001", "what is this", T.held_render("ring")))
        mind.consume(T.drop_grade(self.root, self.tape, "c0001", True, False))
        self.assertEqual(T.journal_rows(self.root), [])
        self.assertEqual(mind.chat_counters["chats"] + mind.chat_counters["graded"], 0)
        mind.close()

    def test_a_chat_grade_is_counted_apart_and_never_reaches_the_readiness_judge(self) -> None:
        g = T.drop_grade(self.root, self.tape, "c0001", True, True)
        self.mind.consume(g)
        self.assertEqual((self.mind._grades_total, self.mind._grades_right, len(self.mind._novel_grades)), (0, 0, 0))
        self.assertEqual({k: self.mind.chat_counters[k] for k in ("graded", "graded_right", "graded_novel")},
                         {"graded": 1, "graded_right": 1, "graded_novel": 1})
        self.assertEqual(T.journal_rows(self.root)[-1]["grade"], {"id": "c0001", "right": True, "novel": True, "kind": "chat"})

    def test_an_ask_door_grade_still_reaches_the_readiness_judge(self) -> None:
        row = self.tape.publish("grade", b"{}", {"moment": "grade1", "source": "grade", "id": "q1", "right": True, "novel": False}, "json", at=T.AT)
        self.mind.consume(row)
        self.assertEqual(self.mind._grades_total, 1)
        self.assertEqual(self.mind.chat_counters["graded"], 0)

    def test_a_writing_chat_is_caught_by_the_hash_assertion(self) -> None:
        """Control (iii): a planted test double inside the real branch calls org.moment() once — the crash law fires."""
        import numpy as np
        row = T.drop_chat(self.root, self.tape, "c0001", "what is this", T.held_render("ring"))
        real = chain.compose
        def writing_compose(*a, **k):
            x = np.zeros(self.mind.genome.sight_dim()); x[0] = 1.0
            self.mind.org.moment(x, np.zeros(self.mind.genome.words_dim()))
            return real(*a, **k)
        with mock.patch.object(chain, "compose", writing_compose):
            with self.assertRaises(RuntimeError) as ctx:
                self.mind.consume(row)
        self.assertIn("a chat changed the organism", str(ctx.exception))
        self.assertEqual([r for r in T.journal_rows(self.root) if "say" in r], [], "a chat that changed him is never logged as a result")
        # the planted write left a birth no moment_word names: this organism is corrupt by design — never snapshot it
        if self.mind._think_executor is not None:
            self.mind._think_executor.shutdown(wait=True)
        self.mind = Mind(T.LANG_GENOME, self.root)


class TestOnALearnedOrganism(unittest.TestCase):
    """One learned mind for the class: three things shown 45 times each + thirty «it is X» lines (a frame, a link, a
    pivot) — then chats on held-out (seed 3) renders."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp()); cls.tape = T.build(cls.root, lines=T.lines_it_is(30))
        cls.mind = Mind(T.LANG_GENOME, cls.root)
        _consume_all(cls.mind, cls.root)
        cls.last = cls.mind.last_seq

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mind.close(); shutil.rmtree(cls.root, ignore_errors=True)

    def _ask(self, cid: str, text: str, picture=None) -> dict:
        row = T.drop_chat(self.root, self.tape, cid, text, picture)
        h, road = self.mind.org.state_hash(), _road(self.mind)
        self.mind.consume(row)
        self.assertEqual(self.mind.org.state_hash(), h)
        self.assertEqual(_road(self.mind), road)
        say = [r for r in T.journal_rows(self.root) if r.get("seq") == row["seq"] and "say" in r]
        self.assertEqual(len(say), 1)
        return say[0]["say"]

    def test_what_is_answers_its_own_content_in_a_composed_sentence(self) -> None:
        say = self._ask("w1", "what is this", T.held_render("star", 1))
        self.assertEqual(say["content"], "star")
        self.assertEqual(say["road"], "recall")
        self.assertEqual(say["chain"], ["it", "is", "star"], say)
        self.assertEqual(say["form"], ["it", "is"]); self.assertEqual(say["pivot"], "is")
        self.assertIsNone(say["refused"])
        self.assertEqual(say["links"], [["it", "is", 30, 30]])
        self.assertTrue(say["grounded"]["ok"])

    def test_yes_no_with_a_wrong_lure_answers_the_canvas_never_the_lure(self) -> None:
        say = self._ask("y1", "is this a cross", T.held_render("ring", 2))
        self.assertEqual(say["content"], "ring")
        self.assertNotEqual(say["content"], "cross")

    def test_which_names_two_things_and_the_content_is_chosen_among_them(self) -> None:
        say = self._ask("h1", "is it a cross or a ring", T.held_render("ring", 3))
        self.assertEqual(say["road"], "choose")
        self.assertEqual(say["content"], "ring")

    def test_where_points_at_a_located_glance_on_the_asked_thing(self) -> None:
        say = self._ask("p1", "where is the star", T.held_render("star", 4))
        self.assertIsNotNone(say["point"])
        self.assertEqual(say["point"]["word"], "star")
        self.assertEqual(len(say["point"]["window"]), 2)

    def test_the_answer_is_at_most_max_words(self) -> None:
        say = self._ask("m1", "what is this", T.held_render("cross", 5))
        self.assertLessEqual(len(say["chain"]), 6)

    def test_an_ungrounded_content_is_never_said(self) -> None:
        mind = self.mind
        real = Mind._chat_content
        def planted(self_, *a, **k):
            c = real(self_, *a, **k); c = dict(c); c["content"] = "zzz"; c["abstain_reason"] = None; return c
        with mock.patch.object(Mind, "_chat_content", planted):
            say = self._ask("u1", "what is this", T.held_render("ring", 6))
        self.assertEqual(say["refused"], "content")
        self.assertEqual(say["chain"], [])
        out = json.loads((self.root / "chat" / "out" / "u1.json").read_text())
        self.assertIsNone(out["answer"])

    def test_a_failing_form_falls_back_to_the_content_alone(self) -> None:
        real = chain.compose
        def planted(*a, **k):
            r = dict(real(*a, **k)); r["form"] = ["big", "is"]; r["pivot"] = "is"
            r["answer"] = ["big", "is"] + ([a[1]] if a[1] else []); return r
        with mock.patch.object(chain, "compose", planted):
            say = self._ask("f1", "what is this", T.held_render("star", 7))
        self.assertEqual(say["refused"], "form")
        self.assertEqual(say["chain"], ["star"])

    def test_a_free_line_is_answered_from_its_own_rendered_canvas(self) -> None:
        say = self._ask("s1", "hello there")
        self.assertEqual(say["heard"], ["hello", "there"])
        self.assertIn(say["abstain_reason"], (None, "novel", "noedge", "ratio", "close", "not_one_word", "tie"))

    def test_the_counters_add_up(self) -> None:
        c = self.mind.chat_counters
        self.assertEqual(c["chats"], c["answered"] + c["abstained"] + c["refused_content"])
        self.assertGreaterEqual(c["longest"], 0)


if __name__ == "__main__":
    unittest.main()
