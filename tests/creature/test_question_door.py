# edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:3x +0400 — L-10 (docs/briefs/LIFE-C-QUESTION-SENTENCE.md
# task 1): the world-maker's own door -- it polls `run/ask/out/`, answers a `what-is` whose moment id
# names a canvas IT DREW by showing that thing again, and renames the question file. Kept separate from
# test_world_maker.py (that file's own discipline: new tests beside it, not folded in).
from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from creature import world_maker
from creature.body import Body
from creature.tape import read_tape

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"
SEED = 20260920


def _tmp() -> Path:
    return Path(tempfile.mkdtemp())


class TestAnswerOneQuestionUnit(unittest.TestCase):
    """`_answer_one_question` at the unit level: a fake `publish` accumulator, no threads."""

    def setUp(self) -> None:
        self.rows = []

    def _publish(self, sense, payload, meta, kind):
        seq = len(self.rows)
        self.rows.append({"sense": sense, "payload": payload, "meta": meta, "kind": kind, "seq": seq})
        return {"seq": seq, "sha": "x" * 8}

    def test_answers_a_real_moment_and_renames_the_file(self) -> None:
        root = _tmp()
        # the SAME moment shape sense() actually writes -- i=1 in the string, i_used=0 the real make() arg
        # (the discovered off-by-one, see world_maker._answer_one_question's own comment).
        moment = "w0000i000001t000000000"
        thing0, _rgb0, _truth0 = world_maker.make(SEED, 0, 0)
        ask_out = root / "ask" / "out"
        ask_out.mkdir(parents=True)
        (ask_out / "q-1.json").write_text(json.dumps({"q": "what-is", "args": [moment], "from": "mind", "seq": 0}))

        new_total = world_maker._answer_one_question(self._publish, root, SEED, total=42)

        self.assertEqual(new_total, 43)
        self.assertEqual(len(self.rows), 2, "ear then eye")
        ear, eye = self.rows
        self.assertEqual(ear["sense"], "ear")
        self.assertEqual(eye["sense"], "eye")
        self.assertEqual(ear["meta"]["word"], thing0, "the SAME thing the original moment actually drew")
        self.assertEqual(ear["meta"]["answering"], "q-1")
        self.assertEqual(eye["meta"]["answering"], "q-1")
        self.assertEqual(ear["meta"]["moment"], eye["meta"]["moment"])
        self.assertTrue(ear["meta"]["moment"].startswith("w0000i000001t"))
        self.assertNotEqual(ear["meta"]["moment"], moment, "a FRESH total, not the original moment string")
        self.assertFalse((ask_out / "q-1.json").exists())
        self.assertTrue((ask_out / "q-1.answered.json").exists())

    def test_a_folder_moment_is_left_untouched(self) -> None:
        """A moment this door never drew (the folder door's own "f<sha>" shape) -- no answering row, the
        question file stays exactly where it is (PARK's own reopen-on-new-sense is its consumer)."""
        root = _tmp()
        ask_out = root / "ask" / "out"
        ask_out.mkdir(parents=True)
        (ask_out / "q-2.json").write_text(json.dumps({"q": "what-is", "args": ["f0123456789ab"], "from": "mind", "seq": 0}))

        new_total = world_maker._answer_one_question(self._publish, root, SEED, total=7)

        self.assertIsNone(new_total)
        self.assertEqual(self.rows, [])
        self.assertTrue((ask_out / "q-2.json").exists(), "an unanswerable question is left in place, never renamed")

    def test_a_non_what_is_question_is_left_untouched(self) -> None:
        root = _tmp()
        ask_out = root / "ask" / "out"
        ask_out.mkdir(parents=True)
        (ask_out / "q-3.json").write_text(json.dumps({"q": "is", "args": ["w0000i000001t000000000", "circle"], "from": "mind"}))

        new_total = world_maker._answer_one_question(self._publish, root, SEED, total=7)

        self.assertIsNone(new_total)
        self.assertEqual(self.rows, [])

    def test_no_ask_out_directory_returns_none(self) -> None:
        root = _tmp()
        self.assertIsNone(world_maker._answer_one_question(self._publish, root, SEED, total=0))

    def test_asked_ledger_is_never_mistaken_for_a_question(self) -> None:
        """ASKED.json (creature/mind.py's own want-ledger) lives beside q-*.json in the same directory but
        never matches the "q-*.json" glob -- proven directly rather than assumed."""
        root = _tmp()
        ask_out = root / "ask" / "out"
        ask_out.mkdir(parents=True)
        (ask_out / "ASKED.json").write_text(json.dumps({"sight:3": "what-is"}))
        self.assertIsNone(world_maker._answer_one_question(self._publish, root, SEED, total=0))


class TestQuestionDoorLive(unittest.TestCase):
    """The real `sense()` thread, a real Body/Tape -- mirrors TestPlantMechanism's own pattern."""

    def test_a_planted_question_is_answered_within_a_few_canvases_and_the_tape_carries_it(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        body.add_sense("maker", lambda publish, stop_event: world_maker.sense(
            publish, stop_event, root=root, period=0.05, seed=SEED))
        body.start()
        try:
            time.sleep(0.6)   # let a handful of ordinary canvases publish first
            rows = [r for r in read_tape(root) if r["sense"] == "ear"]
            self.assertGreater(len(rows), 0)
            asked_moment = rows[0]["meta"]["moment"]
            thing0 = rows[0]["meta"]["word"]
            (root / "ask" / "out").mkdir(parents=True, exist_ok=True)
            (root / "ask" / "out" / "q-9.json").write_text(json.dumps({"q": "what-is", "args": [asked_moment], "from": "mind"}))

            deadline = time.time() + 5.0
            answering_rows = []
            while time.time() < deadline and not answering_rows:
                answering_rows = [r for r in read_tape(root) if r["sense"] == "ear" and r["meta"].get("answering") == "q-9"]
                time.sleep(0.1)
        finally:
            body.stop()

        self.assertEqual(len(answering_rows), 1, "exactly one answering showing")
        self.assertEqual(answering_rows[0]["meta"]["word"], thing0)
        self.assertTrue((root / "ask" / "out" / "q-9.answered.json").exists())
        self.assertFalse((root / "ask" / "out" / "q-9.json").exists())

        # "within its next 10 canvases": count ordinary (non-answering) ear rows published between the
        # question being planted and the answer appearing.
        all_ears = [r for r in read_tape(root) if r["sense"] == "ear"]
        answer_seq = answering_rows[0]["seq"]
        planted_after_seq = rows[0]["seq"]
        between = [r for r in all_ears if planted_after_seq < r["seq"] < answer_seq and not r["meta"].get("answering")]
        self.assertLessEqual(len(between), 10)

    def test_world_pin_still_holds_after_the_door_change(self) -> None:
        """schedule()/make() are untouched -- the same pin test_world_pin.py checks, re-asserted here as a
        belt-and-braces regression control for this file's own change."""
        from tests.creature.test_world_pin import _world_pin_hash, WORLD_PIN_SHA256
        self.assertEqual(_world_pin_hash(), WORLD_PIN_SHA256)


if __name__ == "__main__":
    unittest.main()
