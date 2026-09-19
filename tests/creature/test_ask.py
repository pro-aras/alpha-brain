# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 23:48 +0400 — A7 test: an answer is produced for a held-out
# canvas, and the LIVE mind's org.state_hash() is unchanged by 10 questions (a question never changes him).
#
# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 00:04 +0400 — fixed a self-inflicted race: calling
# mind.snapshot() from the TEST thread while the mind thread could still be mid-consume() corrupted the
# snapshot (ValueError: could not broadcast ... shape (79,112) into (81,112) -- org.sight.n changing under
# a save() reading it). Mind.snapshot() must only ever run on the mind's own thread; the fix drains the
# queue fully (as A6's replay test does) and relies on consume()'s OWN automatic snapshot at 500 moments,
# never calling snapshot() from outside. Noted in the builder report as a thread-safety finding.
from __future__ import annotations

import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature import ask as creature_ask
from creature import world_maker
from creature.body import Body
from genome import world

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"


def _run_body_to_snapshot(root: Path) -> Body:
    """Runs a body until the mind has automatically snapshotted at least once (every 500 moments,
    PREREG §2.7), then drains the sense/queue fully before returning -- so nothing external ever
    calls Mind.snapshot() while the mind thread might still be mutating org (that races)."""
    body = Body(root, GENOME_PATH)
    maker = body.add_sense("maker", lambda p, se: world_maker.sense(p, se, root=root, period=0.03))
    body.start()
    deadline = time.time() + 90.0
    while body.mind.snapshot_count < 1 and time.time() < deadline:
        time.sleep(0.5)
    if body.mind.snapshot_count < 1:
        body.stop()
        raise AssertionError("mind did not snapshot within 90 s")
    maker.stop()
    maker.join(timeout=5.0)
    drain_deadline = time.time() + 20.0
    while not body.q.empty() and time.time() < drain_deadline:
        time.sleep(0.1)
    time.sleep(1.0)   # grace for the in-flight consume() call to finish
    return body


class TestAskDoor(unittest.TestCase):
    def test_answer_produced_and_mind_unchanged_by_ten_questions(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = _run_body_to_snapshot(root)
        try:
            self.assertTrue((root / "state" / "organism.json").exists())

            pic_rgb, _truth = world.render_canvas("circle", np.random.default_rng(2))   # a held-out-style canvas
            pic_path = root / "held_out.png"
            Image.fromarray(pic_rgb, mode="RGB").save(pic_path, format="PNG")

            hash_before = body.mind.org.state_hash()
            answers = [creature_ask.answer(root, "what-is", [str(pic_path)]) for _ in range(10)]
            hash_after = body.mind.org.state_hash()

            self.assertEqual(len(answers), 10)
            for a in answers:
                self.assertIsInstance(a, str)
                self.assertTrue(a.startswith("what-is "))
            self.assertEqual(len(set(answers)), 1, "the same question against the same snapshot must answer the same way every time")
            self.assertEqual(hash_before, hash_after, "a question must never change the live mind")
        finally:
            body.stop()
            shutil.rmtree(root, ignore_errors=True)

    def test_inbox_loop_answers_without_touching_the_mind(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = _run_body_to_snapshot(root)
        try:
            pic_rgb, _truth = world.render_canvas("square", np.random.default_rng(2))
            pic_path = root / "held_out2.png"
            Image.fromarray(pic_rgb, mode="RGB").save(pic_path, format="PNG")

            hash_before = body.mind.org.state_hash()
            (root / "ask" / "in").mkdir(parents=True, exist_ok=True)
            (root / "ask" / "in" / "q1.json").write_text(json.dumps({"q": "what-is", "pic": str(pic_path)}))

            out_path = root / "ask" / "out" / "q1.json"
            deadline2 = time.time() + 15.0
            while not out_path.exists() and time.time() < deadline2:
                time.sleep(0.2)
            self.assertTrue(out_path.exists(), "the voice thread must answer the inbox request")
            result = json.loads(out_path.read_text())
            self.assertIsNone(result["error"])
            self.assertIn("what-is", result["answer"])
            self.assertEqual(body.mind.org.state_hash(), hash_before)
        finally:
            body.stop()
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
