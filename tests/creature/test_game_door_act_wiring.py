# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:36 +0400 — LIFE-D-ACT-SOUND.md item 1 (L-8):
# creature/senses/game.py's own half of the act loop -- `mind_drives_acts()` (the ONE gate shared with
# creature/body.py:main so the two can never disagree, #180), `start_worker(..., act_file=...)` forwarding
# `--act-file`, and `sense()` publishing `n_actions`/`act_names` on every eye row (so the mind can build its
# act pool without hardcoding 7) and reading `chosen_by`/`act_seq`/`act_idx` off the worker's OWN manifest
# (defaulting to "schedule"/None/None -- test_game_door.py's own pin on the pre-L-8 shape, unchanged).
# edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 16:51 +0400 — the seat's decision 16:4x on the verifier's chain-A ruling (LOAD; a race
# in THIS test, on master since 0a640f0): the wait stopped at a row COUNT («>= 11 = 2 + 3*3») that Builder C's L-11 (f28a794, a second ear row
# per manifest) made stale — the door publishes 15 rows for 4 manifests — so a poll landing while rows 11–14 were the newest read «3 != 4» /
# «2 != 3» (int/logs/inner-creature-141ce30.log, 15:53:18, 2.3 min after the 15:50:57 OOM; reproduced on both shas by delaying every
# Tape.publish 0.08 s: verify/chainA-141ce30/repro-SUMMARY.txt). Now the poll breaks when the LAST step's rows are present (_last_step_present:
# eye rows >= 4 and outcome rows >= 3 — the counts the asserts check) and the tape is RE-READ after the settle and the door's stop, so the
# asserts read the tape, never a poll's snapshot. Every assert byte-identical.
from __future__ import annotations

import json
import shutil
import subprocess
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


def _last_step_present(rows) -> bool:
    """The wait's condition: the LAST step's rows are on the tape — 4 eye rows (one per manifest) and 3 outcome rows (one per step
    after the reset), the counts the asserts below check. Never a total row count: the door's rows per manifest changed once (L-11)
    and a count the test does not assert goes stale without any test noticing (the edit of 2026-10-03 above)."""
    eyes = sum(1 for r in rows if r["sense"] == "eye")
    outs = sum(1 for r in rows if r["sense"] == "outcome")
    return eyes >= 4 and outs >= 3


class TestMindDrivesActsGate(unittest.TestCase):
    def test_both_turn_and_step_present_is_true(self) -> None:
        self.assertTrue(game_sense.mind_drives_acts({"ACT": {"verbs": ["glance", "open", "ask", "turn", "step", "say", "run"]}}))

    def test_missing_turn_is_false(self) -> None:
        self.assertFalse(game_sense.mind_drives_acts({"ACT": {"verbs": ["glance", "open", "ask"]}}))

    def test_undeclared_act_is_false(self) -> None:
        self.assertFalse(game_sense.mind_drives_acts({}))

    def test_only_one_of_the_two_is_false(self) -> None:
        self.assertFalse(game_sense.mind_drives_acts({"ACT": {"verbs": ["turn"]}}))
        self.assertFalse(game_sense.mind_drives_acts({"ACT": {"verbs": ["step"]}}))


class TestStartWorkerForwardsActFile(unittest.TestCase):
    def test_act_file_given_appends_the_flag(self) -> None:
        captured = {}

        class _FakePopen:
            def __init__(self, argv, **kw):
                captured["argv"] = argv

        import unittest.mock as mock
        with mock.patch.object(game_sense.subprocess, "Popen", _FakePopen):
            game_sense.start_worker(_tmp(), seed=1, act_file=Path("/tmp/x/ACT"))
        self.assertIn("--act-file", captured["argv"])
        self.assertEqual(captured["argv"][captured["argv"].index("--act-file") + 1], "/tmp/x/ACT")

    def test_act_file_absent_omits_the_flag(self) -> None:
        captured = {}

        class _FakePopen:
            def __init__(self, argv, **kw):
                captured["argv"] = argv

        import unittest.mock as mock
        with mock.patch.object(game_sense.subprocess, "Popen", _FakePopen):
            game_sense.start_worker(_tmp(), seed=1)
        self.assertNotIn("--act-file", captured["argv"])


@unittest.skipUnless(VENV_PYTHON.exists(), "the game-worlds venv is not present on this box")
class TestDoorPublishesActFields(unittest.TestCase):
    def test_eye_rows_carry_n_actions_and_outcome_rows_default_schedule(self) -> None:
        """No --act-file at the worker -> the door's outcome rows keep test_game_door.py's own pin
        (chosen_by "schedule", road "no road") AND the eye row now additionally carries n_actions/
        act_names (additive; the old fields are untouched)."""
        root = _tmp()
        door = _tmp()
        proc = subprocess.Popen([str(VENV_PYTHON), str(game_sense.WORKER_SCRIPT), "--game", "babyai-gotolocal",
                                  "--door-dir", str(door), "--seed", "20260922", "--steps", "4"],
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
            if _last_step_present(rows):   # the LAST step's rows (eye >= 4, outcome >= 3), never a row count (edit 2026-10-03)
                break
            time.sleep(0.1)
        time.sleep(0.3)
        stop_event.set(); t.join(timeout=5.0)
        rows = _game_rows(root)   # re-read after the settle and the stop: the asserts read the tape, never a poll's snapshot

        eyes = [r for r in rows if r["sense"] == "eye"]
        outs = [r for r in rows if r["sense"] == "outcome"]
        self.assertEqual(len(eyes), 4)
        self.assertEqual(len(outs), 3)
        for r in eyes:
            self.assertEqual(r["meta"]["n_actions"], 7)
            self.assertEqual(r["meta"]["act_names"], game_sense.ACT_NAMES)
        for r in outs:
            m = r["meta"]
            self.assertEqual(m["chosen_by"], "schedule")
            self.assertEqual(m["road"], "no road")
            self.assertIsNone(m.get("act_seq"))
            self.assertIn(m["act_idx"], range(7))
            self.assertEqual(game_sense.ACT_NAMES[m["act_idx"]], m["act"])
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(door, ignore_errors=True)

    def test_act_file_present_outcome_rows_carry_mind_and_act_seq(self) -> None:
        """With --act-file (via start_worker's own act_file kwarg) and a test driver standing in for the
        mind, the door's outcome rows read chosen_by/act_seq straight off the worker's own manifest,
        never hardcoded."""
        import os as _os
        root = _tmp()
        door = _tmp()
        act_dir = _tmp()
        act_file = act_dir / "ACT"
        proc = game_sense.start_worker(door, seed=20260922, tile=32, period_s=0.0, steps=4, act_file=act_file)
        try:
            deadline = time.time() + 60.0
            reset = door / "step-000000000.json"
            while time.time() < deadline and not reset.exists():
                time.sleep(0.02)
            self.assertTrue(reset.exists())
            import random
            rng = random.Random(1)
            for i, step_idx in enumerate((1, 2, 3), start=1):
                act = rng.randrange(7)
                tmp = act_file.with_suffix(".tmp")
                tmp.write_text(json.dumps({"seq": i, "act": act, "at": "2026-09-22T19:00:00.000Z"}))
                _os.replace(tmp, act_file)
                man = door / f"step-{step_idx:09d}.json"
                d2 = time.time() + 30.0
                while time.time() < d2 and not man.exists():
                    time.sleep(0.02)
                self.assertTrue(man.exists())
            proc.wait(timeout=15)
            self.assertEqual(proc.returncode, 0)

            tape = Tape(root)
            stop_event = threading.Event()
            t = threading.Thread(target=lambda: game_sense.sense(
                tape.publish, stop_event, door_dir=door, root=root, canvas=128, poll_period=0.1), daemon=True)
            t.start()
            d3 = time.time() + 15.0
            rows = []
            while time.time() < d3:
                rows = _game_rows(root)
                if _last_step_present(rows):   # the LAST step's rows (eye >= 4, outcome >= 3), never a row count (edit 2026-10-03)
                    break
                time.sleep(0.1)
            time.sleep(0.3)
            stop_event.set(); t.join(timeout=5.0)
            rows = _game_rows(root)   # re-read after the settle and the stop: the asserts read the tape, never a poll's snapshot

            outs = [r for r in rows if r["sense"] == "outcome"]
            self.assertEqual(len(outs), 3)
            for i, r in enumerate(outs, start=1):
                m = r["meta"]
                self.assertEqual(m["chosen_by"], "mind")
                self.assertEqual(m["road"], "mind")
                self.assertEqual(m["act_seq"], i)
            shutil.rmtree(root, ignore_errors=True)
            shutil.rmtree(door, ignore_errors=True)
            shutil.rmtree(act_dir, ignore_errors=True)
        finally:
            if proc.poll() is None:
                game_sense.stop_worker(proc)


if __name__ == "__main__":
    unittest.main()
