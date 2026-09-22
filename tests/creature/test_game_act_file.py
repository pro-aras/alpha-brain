# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:34 +0400 — LIFE-D-ACT-SOUND.md item 1 (L-8):
# tools/game_worker_babyai.py's `--act-file` -- the worker WAITS (no timeout) for a JSON {"seq","act","at"}
# whose seq is newer than the one it last consumed (persisted at <door_dir>/ACT_CURSOR, advanced only AFTER
# the manifest naming it is durable, #230), steps that act, and writes the manifest with act/chosen_by/
# act_seq. Without --act-file the old seeded schedule is BYTE-IDENTICAL (chosen_by "schedule", no act_seq
# key) -- proven here directly against the real venv worker script, before creature/senses/game.py (the
# door) is involved at all.
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from creature.senses import game as game_sense

VENV_PYTHON = Path(game_sense.VENV_PYTHON)
ACT_NAMES = game_sense.ACT_NAMES  # ["left","right","forward","pickup","drop","toggle","done"], 7 acts


def _tmp() -> Path:
    return Path(tempfile.mkdtemp())


def _atomic_write_json(path: Path, obj: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj))
    os.replace(tmp, path)


@unittest.skipUnless(VENV_PYTHON.exists(), "the game-worlds venv is not present on this box")
class TestActFileDrivesTheWorker(unittest.TestCase):
    def test_worker_obeys_a_test_driver_writing_the_act_file(self) -> None:
        door = _tmp()
        act_dir = _tmp()
        act_file = act_dir / "ACT"
        n_steps = 6
        proc = subprocess.Popen(
            [str(VENV_PYTHON), str(game_sense.WORKER_SCRIPT), "--game", "babyai-gotolocal",
             "--door-dir", str(door), "--seed", "20260922", "--steps", str(n_steps),
             "--act-file", str(act_file)],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.time() + 60.0
            reset_manifest = door / "step-000000000.json"
            while time.time() < deadline and not reset_manifest.exists():
                time.sleep(0.02)
            self.assertTrue(reset_manifest.exists(), "the worker must write its reset manifest without waiting on the act file")
            reset_data = json.loads(reset_manifest.read_text())
            self.assertIsNone(reset_data["act"])
            self.assertIn("n_actions", reset_data, "the manifest must publish env.action_space.n -- never hardcode 7")
            self.assertEqual(reset_data["n_actions"], 7)
            self.assertEqual(reset_data.get("chosen_by"), "schedule", "the reset frame carries no act -- chosen_by is unset/absent (defaults to schedule), never fabricated as 'mind'")

            rng = random.Random(20260922)
            seq = 0
            for step_idx in range(1, n_steps):
                seq += 1
                act = rng.randrange(reset_data["n_actions"])
                _atomic_write_json(act_file, {"seq": seq, "act": act, "at": "2026-09-22T18:44:00.000Z"})
                man_path = door / f"step-{step_idx:09d}.json"
                d2 = time.time() + 30.0
                while time.time() < d2 and not man_path.exists():
                    time.sleep(0.02)
                self.assertTrue(man_path.exists(), f"worker never wrote step {step_idx} after act seq {seq}")
                data = json.loads(man_path.read_text())
                self.assertEqual(data["act"], act, f"step {step_idx}: worker did not obey the act it was told")
                self.assertEqual(data["chosen_by"], "mind")
                self.assertEqual(data["act_seq"], seq)
                self.assertEqual(data["n_actions"], 7)

            proc.wait(timeout=15)
            self.assertEqual(proc.returncode, 0, proc.stderr.read().decode())
            manifests = sorted(door.glob("step-*.json"))
            self.assertEqual(len(manifests), n_steps)

            cursor_path = door / "ACT_CURSOR"
            self.assertTrue(cursor_path.exists(), "the persisted cursor must exist beside the door (#230)")
            self.assertEqual(int(cursor_path.read_text().strip()), seq)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            shutil.rmtree(door, ignore_errors=True)
            shutil.rmtree(act_dir, ignore_errors=True)

    def test_without_act_file_the_old_seeded_schedule_is_unchanged(self) -> None:
        """Regression: no --act-file -> chosen_by 'schedule', no act_seq key -- byte-identical to the
        pre-L-8 shape test_game_door.py already pins (m["chosen_by"] == "schedule")."""
        door = _tmp()
        n_steps = 4
        r = subprocess.run([str(VENV_PYTHON), str(game_sense.WORKER_SCRIPT), "--game", "babyai-gotolocal",
                             "--door-dir", str(door), "--seed", "20260922", "--steps", str(n_steps)],
                            capture_output=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        manifests = sorted(door.glob("step-*.json"))
        self.assertEqual(len(manifests), n_steps)
        for m in manifests:
            data = json.loads(m.read_text())
            self.assertEqual(data.get("chosen_by"), "schedule")
            self.assertNotIn("act_seq", data)
            self.assertEqual(data["n_actions"], 7)
        self.assertFalse((door / "ACT_CURSOR").exists(), "no --act-file -> no cursor is ever written")
        shutil.rmtree(door, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
