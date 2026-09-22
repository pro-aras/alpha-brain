# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 02:35 +0400 — A13: the self-exam duty (PREREG §11.4).
# tools/self_exam.py's own functions, via import; a journal EVENT row; the mind's hash unmoved by the exam.
from __future__ import annotations

import io
import json
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature import exam as exam_mod
from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import world

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_snapshot(root: Path, n: int = 140, seed: int = 4242) -> Mind:
    """Enough canvases (4 glances each -> >= 500 org.t) to force at least one automatic snapshot."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = list(world.THINGS_11)
    for i in range(n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")
    mind = Mind(GENOME_PATH, root)
    for r in read_tape(root):
        mind.consume(r)
    if mind.snapshot_count == 0:
        mind.snapshot()
    return mind


class TestRunExam(unittest.TestCase):
    def test_run_exam_writes_report_and_leaves_the_mind_untouched(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = _build_snapshot(root)
        hash_before = mind.org.state_hash()

        result = exam_mod.run_exam(root, GENOME_PATH, held=5, check_tape=50)
        self.assertTrue(Path(result["path"]).exists())
        data = result["data"]
        self.assertIn("cells", data)
        self.assertIn("moments", data)
        self.assertIn("organism_hash_unchanged_by_exam", data)
        self.assertTrue(data["organism_hash_unchanged_by_exam"], "self_exam's OWN before/after check on its private organism")

        self.assertEqual(mind.org.state_hash(), hash_before, "the live mind must be completely untouched by the exam")

    def test_run_and_journal_writes_an_exam_event_row(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = _build_snapshot(root)
        hash_before = mind.org.state_hash()

        result = exam_mod.run_and_journal(root, GENOME_PATH, held=5, check_tape=50)
        self.assertEqual(mind.org.state_hash(), hash_before)

        journal_files = sorted((root / "journal").glob("*.jsonl"))
        rows = [json.loads(l) for l in journal_files[-1].read_text().splitlines() if l.strip()]
        exam_events = [r for r in rows if r.get("event") == "exam"]
        self.assertEqual(len(exam_events), 1)
        ev = exam_events[0]
        self.assertEqual(ev["path"], result["path"])
        self.assertIn("q1", ev); self.assertIn("cells", ev)

    def test_exam_event_row_excluded_from_mind_journal_reader(self) -> None:
        """replay.read_mind_journal filters on "event" not in r -- confirm the exam row is correctly
        excluded (it must never be mistaken for a mind row by the replay gate)."""
        from creature import replay as replay_mod
        root = Path(tempfile.mkdtemp())
        _build_snapshot(root)
        exam_mod.run_and_journal(root, GENOME_PATH, held=5, check_tape=50)
        journal_files = sorted((root / "journal").glob("*.jsonl"))
        mind_rows = replay_mod.read_mind_journal(journal_files[-1])
        self.assertTrue(all("event" not in r for r in mind_rows))
        all_rows = [json.loads(l) for l in journal_files[-1].read_text().splitlines() if l.strip()]
        self.assertTrue(any(r.get("event") == "exam" for r in all_rows))


class TestVoiceLoopCadence(unittest.TestCase):
    def test_voice_loop_fires_once_per_boundary_and_persists_its_cursor(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = _build_snapshot(root)
        hash_before = mind.org.state_hash()

        stop_event = threading.Event()
        # every_canvases small enough that the snapshot's own "moments" already crosses it
        fixations = int(mind.genome.gaze["fixations"])
        canvases_so_far = mind.org.t // fixations
        every = max(1, canvases_so_far // 2)
        t = threading.Thread(target=exam_mod.voice_loop, args=(root, GENOME_PATH, stop_event),
                              kwargs={"every_canvases": every, "poll_period": 0.2}, daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while not (root / "exam" / "LAST.json").exists() and time.time() < deadline:
            time.sleep(0.2)
        time.sleep(0.5)
        stop_event.set()
        t.join(timeout=5.0)

        self.assertTrue((root / "exam" / "LAST.json").exists())
        exam_files = list((root / "exam").glob("*.json"))
        exam_reports = [p for p in exam_files if p.name != "LAST.json"]
        self.assertGreaterEqual(len(exam_reports), 1)
        self.assertEqual(mind.org.state_hash(), hash_before, "the voice's exam thread must never touch the live mind")


if __name__ == "__main__":
    unittest.main()


# edit: Claude (Fable 5.1), 2026-09-23 02:13 +0400 — the J × exam seam (ALPHA4-J-REPORT.md "not done" 1): after an EVOLVE adoption the voice
# thread must sit the exam under the ADOPTED genome (GENOME.v<n>.genome, the highest n — numerically, never lexically), and
# under the birth genome when none exists.
class ExamSitsUnderTheAdoptedGenome(unittest.TestCase):
    def test_genome_for_sitting_prefers_the_highest_epoch_numerically(self):
        import tempfile
        from creature import exam as exam_module
        root = Path(tempfile.mkdtemp()); birth = root / "birth.genome"; birth.write_text("SEED 1\n")
        self.assertEqual(exam_module.genome_for_sitting(root, birth), birth)
        (root / "GENOME.v3.genome").write_text("SEED 3\n"); (root / "GENOME.v10.genome").write_text("SEED 10\n")
        self.assertEqual(exam_module.genome_for_sitting(root, birth), root / "GENOME.v10.genome")

    def test_voice_loop_sits_under_the_adopted_genome(self):
        import tempfile, threading, json
        from unittest import mock
        from creature import exam as exam_module
        root = Path(tempfile.mkdtemp()); (root / "state").mkdir(); (root / "exam").mkdir()
        birth = root / "birth.genome"; birth.write_text("SEED 1\n")
        (root / "GENOME.v2.genome").write_text("SEED 2\n")
        (root / "state" / "ledger.json").write_text(json.dumps({"moments": 5000}))
        seen = []
        stop = threading.Event()
        def fake_run(r, gp, held=10, check_tape=400):
            seen.append(Path(gp)); stop.set(); return {}
        fake_genome = mock.Mock(); fake_genome.gaze = {"fixations": 4}
        with mock.patch.object(exam_module, "run_and_journal", side_effect=fake_run), \
             mock.patch("genome.machinery.parse_genome", return_value=fake_genome):
            exam_module.voice_loop(root, birth, stop, every_canvases=10, poll_period=0.01)
        self.assertEqual(seen, [root / "GENOME.v2.genome"])
