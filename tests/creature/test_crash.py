# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 22:15 +0400 — A3 test: crash isolation (PREREG §2.6, gate G4-4's
# shape). A synthetic sense (not world_maker, task A4) drives Body/SenseThread directly so this test does not depend
# on A4 landing first. The plant fires once (eye:20); the mind's counters must keep moving after the restart.
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

from creature.body import Body
from genome import world

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"


def _synthetic_sense(publish, stop_event, period: float = 0.25) -> None:
    """Publishes ear then eye for a real drawn canvas every `period` seconds, forever, until stopped."""
    i = 0
    things = ("circle", "square", "diamond")
    while not stop_event.is_set():
        thing = things[i % len(things)]
        moment = f"s{i:06d}"
        publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        rgb, _truth = world.render_canvas(thing, np.random.default_rng(1000 + i))
        buf = io.BytesIO()
        Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
        publish("eye", buf.getvalue(), {"moment": moment, "source": "test"}, "png")
        i += 1
        stop_event.wait(period)


def _journal_rows(root: Path):
    out = []
    jdir = root / "journal"
    if not jdir.exists():
        return out
    for f in sorted(jdir.glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


class TestCrashIsolation(unittest.TestCase):
    def test_plant_restarts_once_and_mind_keeps_moving(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        body.add_sense("eye", lambda publish, stop_event: _synthetic_sense(publish, stop_event, period=0.25), plant="eye:20")
        body.start()
        try:
            time.sleep(30.0)
        finally:
            body.stop()

        rows = _journal_rows(root)
        restarts = [r for r in rows if r.get("event") == "sense_restart"]
        self.assertEqual(len(restarts), 1, f"expected exactly one sense_restart row, got {len(restarts)}: {restarts}")
        self.assertEqual(restarts[0]["sense"], "eye")

        status = json.loads((root / "STATUS.json").read_text())
        self.assertGreater(status["moments"], 0)
        self.assertEqual(status["sense_restarts"], 1)
        self.assertIsNone(status["crash"])

        # the tape kept rising after the restart: rows published strictly after the restart's own timestamp
        restart_at = restarts[0]["at"]
        from creature.tape import read_tape
        tape_rows = list(read_tape(root))
        after = [r for r in tape_rows if r["at"] > restart_at]
        self.assertGreater(len(after), 0, "the tape must keep growing after the sense restarted")
        shutil.rmtree(root, ignore_errors=True)

    def test_no_plant_means_no_restarts(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        body.add_sense("eye", lambda publish, stop_event: _synthetic_sense(publish, stop_event, period=0.5))
        body.start()
        try:
            time.sleep(3.0)
        finally:
            body.stop()
        rows = _journal_rows(root)
        restarts = [r for r in rows if r.get("event") == "sense_restart"]
        self.assertEqual(len(restarts), 0)
        status = json.loads((root / "STATUS.json").read_text())
        self.assertGreater(status["moments"], 0)
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
