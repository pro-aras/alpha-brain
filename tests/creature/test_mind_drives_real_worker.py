# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:46 +0400 — LIFE-D-ACT-SOUND.md item 2's closing
# clause: "Then the real worker under the game-worlds venv for 20 frames on a temp root (the door already
# launches it): the manifests carry chosen_by: 'mind'." The FULL real chain, no test driver standing in
# for anything: a real Mind, the real door sense (creature/senses/game.py), the real venv worker subprocess
# (tools/game_worker_babyai.py --act-file). The sense thread's own `publish` callback also feeds the row
# straight to `mind.consume` (single-threaded, in publish order -- the same order creature/body.py's queue
# preserves, simplified here since this test has no other sense competing for the mind).
from __future__ import annotations

import json
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path

from creature.mind import Mind
from creature.senses import game as game_sense
from creature.tape import Tape, read_tape

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME_PATH = ROOT / "genome" / "G4.genome"
ACT_LINE = "ACT      glance open ask turn step say run"
OUTCOME_LINE = "OUTCOME  act to episode; error grades it; ranks replay"
VENV_PYTHON = Path(game_sense.VENV_PYTHON)


def _g4_with(*lines: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(G4_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


def _tmp() -> Path:
    return Path(tempfile.mkdtemp())


def _game_rows(root: Path):
    return [r for r in read_tape(root) if r["meta"].get("source") == "game"]


@unittest.skipUnless(VENV_PYTHON.exists(), "the game-worlds venv is not present on this box")
class TestMindDrivesTheRealWorkerEndToEnd(unittest.TestCase):
    def test_twenty_frames_manifests_carry_chosen_by_mind(self) -> None:
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        root = _tmp()
        door = _tmp()
        mind = Mind(gpath, root)
        tape = Tape(root)

        def publish_and_consume(sense, payload, meta, ext):
            row = tape.publish(sense, payload, meta, ext)
            mind.consume(row)
            return row

        act_file = root / "game" / "ACT"
        n_steps = 20
        proc = game_sense.start_worker(door, seed=20260922, tile=32, period_s=0.0, steps=n_steps, act_file=act_file)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: game_sense.sense(
            publish_and_consume, stop_event, door_dir=door, root=root, canvas=128, poll_period=0.05), daemon=True)
        t.start()
        try:
            deadline = time.time() + 90.0
            while time.time() < deadline and proc.poll() is None:
                time.sleep(0.1)
            self.assertEqual(proc.returncode, 0, "the worker must exit 0 after writing its --steps manifests")
            proc.wait(timeout=15)

            d2 = time.time() + 20.0
            while time.time() < d2 and len(_game_rows(root)) < (2 + (n_steps - 1) * 3):
                time.sleep(0.1)
        finally:
            stop_event.set(); t.join(timeout=5.0)
            if proc.poll() is None:
                game_sense.stop_worker(proc)

        manifests = sorted(door.glob("step-*.json"))
        self.assertEqual(len(manifests), n_steps)
        for i, mpath in enumerate(manifests):
            data = json.loads(mpath.read_text())
            if i == 0:
                self.assertEqual(data.get("chosen_by"), "schedule", "the reset frame carries no act")
            else:
                self.assertEqual(data.get("chosen_by"), "mind", f"step {i} must have been chosen by the mind, not the schedule")
                self.assertEqual(data.get("act_seq"), data.get("act_seq"))  # present (any int) -- the real assertion is the next block

        rows = _game_rows(root)
        outs = [r for r in rows if r["sense"] == "outcome"]
        self.assertEqual(len(outs), n_steps - 1)
        for r in outs:
            m = r["meta"]
            self.assertEqual(m["chosen_by"], "mind")
            self.assertEqual(m["road"], "mind")
            self.assertIsNotNone(m["act_seq"])
        mismatch_rows = [r["outcome"].get("act_mismatch")
                          for f in sorted((root / "journal").glob("*.jsonl"))
                          for line in f.read_text().splitlines() if line.strip()
                          for r in [json.loads(line)] if "outcome" in r]
        self.assertEqual(len(mismatch_rows), n_steps - 1)
        self.assertEqual(mismatch_rows, [False] * (n_steps - 1),
                          f"the real worker obeyed every act the real mind chose -- no mismatch: {mismatch_rows}")
        # the mind chooses ONE act per eye row it sees, including the reset frame's -- n_steps total
        # (the LAST choice, made on consuming the final manifest's own eye row, is never obeyed: the
        # worker's --steps budget is already spent, so no outcome row ever follows it -- one dangling
        # entry left in mind._act_choices, by design, not a bug).
        self.assertEqual(sum(mind.acts_chosen.values()), n_steps)
        self.assertEqual(len(mind._act_choices), 1, "exactly the final, never-obeyed choice should remain pending")
        self.assertEqual(mind.act_mismatches, 0)
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(door, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
