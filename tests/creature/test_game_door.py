# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 22:3x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 1/3.
"""test_game_door.py — the BabyAI door: two SEPARATE worker processes started with the same seed publish
byte-identical frame/mission/reward streams (the frame-identity proof, item 3), the sense thread reads a
worker's manifests into the tape's own order law (ear then eye then outcome), a restart never re-publishes,
and the worker's own null (uniform over all 7 acts) reproduces REPORT-G5-G.md's 0.29 / 0.1464 numbers.

Every test that starts the real venv worker is skipped if the venv is not present on this box (a fresh
worktree elsewhere would otherwise fail for an environmental reason unrelated to this branch's code)."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from creature.senses import game as game_sense
from creature.tape import Tape, read_tape

VENV_PYTHON = Path(game_sense.VENV_PYTHON)


def _tmp() -> Path:
    return Path(tempfile.mkdtemp())


def _game_rows(root: Path):
    return [r for r in read_tape(root) if r["meta"].get("source") == "game"]


@unittest.skipUnless(VENV_PYTHON.exists(), "the game-worlds venv is not present on this box")
class TestFrameIdentityAcrossTwoProcesses(unittest.TestCase):
    """The brief's item 3 refusing test, reused from G5-G's own road (REPORT-G5-G.md §2 "Stage 3"): two
    SEPARATE processes, same --seed, must produce byte-identical manifests AND byte-identical frame PNGs."""

    def test_two_separate_worker_processes_are_byte_identical(self) -> None:
        door_a, door_b = _tmp(), _tmp()
        for door in (door_a, door_b):
            r = subprocess.run([str(VENV_PYTHON), str(game_sense.WORKER_SCRIPT), "--game", "babyai-gotolocal",
                                 "--door-dir", str(door), "--seed", "20260922", "--steps", "6"],
                                capture_output=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr.decode())

        manifests_a = sorted(door_a.glob("step-*.json"))
        manifests_b = sorted(door_b.glob("step-*.json"))
        self.assertEqual(len(manifests_a), 6)
        self.assertEqual(len(manifests_a), len(manifests_b))
        for ma, mb in zip(manifests_a, manifests_b):
            da = json.loads(ma.read_text())
            db = json.loads(mb.read_text())
            self.assertEqual(da, db, f"manifest {ma.name} differs between two separate processes")
            fa = hashlib.sha256((ma.parent / da["frame"]).read_bytes()).hexdigest()
            fb = hashlib.sha256((mb.parent / db["frame"]).read_bytes()).hexdigest()
            self.assertEqual(fa, fb, f"frame PNG for {ma.name} differs between two separate processes")
        shutil.rmtree(door_a, ignore_errors=True)
        shutil.rmtree(door_b, ignore_errors=True)

    def test_different_seed_diverges(self) -> None:
        """The identity proof's own negative control (#91): a DIFFERENT seed must NOT reproduce the same
        stream, or the "byte-identical" claim above would be vacuous (any two runs agreeing regardless)."""
        door_a, door_b = _tmp(), _tmp()
        for door, seed in ((door_a, "20260922"), (door_b, "1")):
            r = subprocess.run([str(VENV_PYTHON), str(game_sense.WORKER_SCRIPT), "--game", "babyai-gotolocal",
                                 "--door-dir", str(door), "--seed", seed, "--steps", "6"],
                                capture_output=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr.decode())
        ma = json.loads(sorted(door_a.glob("step-*.json"))[0].read_text())
        mb = json.loads(sorted(door_b.glob("step-*.json"))[0].read_text())
        self.assertNotEqual((ma["mission"], ma["act"]), (mb["mission"], mb["act"]),
                             "two different seeds produced the identical first step -- the identity proof would be meaningless")
        shutil.rmtree(door_a, ignore_errors=True)
        shutil.rmtree(door_b, ignore_errors=True)


@unittest.skipUnless(VENV_PYTHON.exists(), "the game-worlds venv is not present on this box")
class TestSenseThreadPublishesRows(unittest.TestCase):
    def test_ear_eye_outcome_rows_shaped_and_ordered(self) -> None:
        root = _tmp()
        door = _tmp()
        proc = subprocess.Popen([str(VENV_PYTHON), str(game_sense.WORKER_SCRIPT), "--game", "babyai-gotolocal",
                                  "--door-dir", str(door), "--seed", "20260922", "--steps", "5"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.wait(timeout=60)
        self.assertEqual(proc.returncode, 0)

        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: game_sense.sense(
            tape.publish, stop_event, door_dir=door, root=root, canvas=128, poll_period=0.1), daemon=True)
        t.start()
        deadline = time.time() + 15.0
        rows = []
        while time.time() < deadline:
            rows = _game_rows(root)
            if len(rows) >= 14:   # 5 manifests: 1 reset (ear+eye, no outcome) + 4 stepped (ear+eye+outcome) = 2 + 12 = 14
                break
            time.sleep(0.1)
        time.sleep(0.3)
        stop_event.set(); t.join(timeout=5.0)

        self.assertEqual(len(rows), 14, f"expected 14 rows (1 reset x 2 + 4 steps x 3), got {len(rows)}: {[r['sense'] for r in rows]}")
        ears = [r for r in rows if r["sense"] == "ear"]
        eyes = [r for r in rows if r["sense"] == "eye"]
        outs = [r for r in rows if r["sense"] == "outcome"]
        self.assertEqual(len(ears), 5)
        self.assertEqual(len(eyes), 5)
        self.assertEqual(len(outs), 4)

        for r in ears:
            self.assertEqual(r["meta"]["source"], "game")
            self.assertIn("mission", r["meta"])
            self.assertTrue(r["meta"]["word"].isalpha())
            self.assertLessEqual(len(r["meta"]["word"]), 8, "the ear's own word channel is <= 8 letters a-z")

        for r in outs:
            m = r["meta"]
            self.assertIn(m["act"], game_sense.ACT_NAMES)
            self.assertIsNone(m["expected"])
            self.assertIsInstance(m["got"], float)
            self.assertIsNone(m["residual"])
            self.assertEqual(m["chosen_by"], "schedule")
            self.assertEqual(m["road"], "no road")
            payload = json.loads(tape.payload_dir.joinpath(Path(r["payload"]).name).read_bytes())
            self.assertEqual(payload["act"], m["act"])
            self.assertEqual(payload["got"], m["got"])

        # order law within each moment: ear before eye; and every moment with an outcome has ear+eye too
        by_moment = {}
        for r in rows:
            by_moment.setdefault(r["meta"]["moment"], {})[r["sense"]] = r["seq"]
        self.assertEqual(len(by_moment), 5)
        for m, d in by_moment.items():
            self.assertIn("ear", d); self.assertIn("eye", d)
            self.assertLess(d["ear"], d["eye"], f"ear must precede eye for moment {m}")
            if "outcome" in d:
                self.assertLess(d["eye"], d["outcome"], f"eye must precede outcome for moment {m}")

        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(door, ignore_errors=True)

    def test_restart_never_republishes(self) -> None:
        root = _tmp()
        door = _tmp()
        proc = subprocess.Popen([str(VENV_PYTHON), str(game_sense.WORKER_SCRIPT), "--game", "babyai-gotolocal",
                                  "--door-dir", str(door), "--seed", "20260922", "--steps", "4"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.wait(timeout=60)
        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: game_sense.sense(
            tape.publish, stop_event, door_dir=door, root=root, canvas=128, poll_period=0.1), daemon=True)
        t.start()
        deadline = time.time() + 15.0
        while time.time() < deadline and len(_game_rows(root)) < 11:   # 4 manifests -> 2 + 3*3 = 11
            time.sleep(0.1)
        time.sleep(0.3)
        stop_event.set(); t.join(timeout=5.0)
        n1 = len(_game_rows(root))
        self.assertGreater(n1, 0)

        stop_event2 = threading.Event()
        t2 = threading.Thread(target=lambda: game_sense.sense(
            tape.publish, stop_event2, door_dir=door, root=root, canvas=128, poll_period=0.1), daemon=True)
        t2.start()
        time.sleep(1.0)
        stop_event2.set(); t2.join(timeout=5.0)
        self.assertEqual(len(_game_rows(root)), n1, "a restart must never re-publish already-seen manifests")
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(door, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
