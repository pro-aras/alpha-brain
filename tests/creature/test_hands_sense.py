# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 2/5
# (MOTOR-HANDS.md G-MOT-4). Exercises creature/senses/hands.py against the REAL jail binary at
# /data/dev/alpha3/hands/jail_run (never a stub -- G-MOT-4's own controls each need a real jailed process:
# the fence control's Permission denied and the crash control's U+FFFD are facts about the jail/kernel, not
# about this module's own code). Mirrors tests/creature/test_ear_sound_door.py's own thread-driven style for
# the sense() loop.
from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.senses import hands as hands_sense
from creature.tape import Tape

JAIL_PATH = Path("/data/dev/alpha3/hands/jail_run")


def _write_program(shelf: Path, name: str, body: str) -> Path:
    p = shelf / f"{name}.py"
    p.write_text(body)
    return p


class TestRenderAscii(unittest.TestCase):
    def test_hash_becomes_ink_space_becomes_ground(self) -> None:
        text = "#" * 32 + "\n" + (" " * 32 + "\n") * 31
        rgb = hands_sense._render_ascii(text)
        self.assertEqual(rgb.shape, (128, 128, 3))
        self.assertEqual(rgb.dtype, np.uint8)
        self.assertTrue((rgb[0:4, 0:4] == 255).all())     # first char's 4x4 block: ink
        self.assertTrue((rgb[4:8, 0:4] == 0).all())        # second row's block (all-space line): ground

    def test_short_text_padded_never_crashes(self) -> None:
        rgb = hands_sense._render_ascii("#\n")
        self.assertEqual(rgb.shape, (128, 128, 3))
        self.assertTrue((rgb[0:4, 0:4] == 255).all())
        self.assertTrue((rgb[0:4, 4:8] == 0).all())

    def test_empty_text_all_ground(self) -> None:
        rgb = hands_sense._render_ascii("")
        self.assertTrue((rgb == 0).all())

    def test_overlong_text_truncated_never_crashes(self) -> None:
        text = "\n".join(["#" * 40] * 40)
        rgb = hands_sense._render_ascii(text)
        self.assertEqual(rgb.shape, (128, 128, 3))


class TestGotFingerprint(unittest.TestCase):
    def test_deterministic_and_in_range(self) -> None:
        a = hands_sense._got_fingerprint(b"hello\n")
        b = hands_sense._got_fingerprint(b"hello\n")
        self.assertEqual(a, b)
        self.assertGreaterEqual(a, 0.0)
        self.assertLess(a, 1.0)

    def test_different_bytes_different_fingerprint(self) -> None:
        a = hands_sense._got_fingerprint(b"hello\n")
        b = hands_sense._got_fingerprint(b"world\n")
        self.assertNotEqual(a, b)


class TestManifest(unittest.TestCase):
    def test_shape_manifest_read(self) -> None:
        d = Path(tempfile.mkdtemp())
        p = _write_program(d, "circle_0", '# shape: circle\nprint("#"*4)\n')
        self.assertEqual(hands_sense._manifest(p), {"shape": "circle", "control": None})

    def test_control_manifest_read(self) -> None:
        d = Path(tempfile.mkdtemp())
        p = _write_program(d, "positive", '# control: positive\nprint("x")\n')
        self.assertEqual(hands_sense._manifest(p), {"shape": None, "control": "positive"})

    def test_no_manifest_both_none(self) -> None:
        d = Path(tempfile.mkdtemp())
        p = _write_program(d, "nomanifest", 'print("x")\n')
        self.assertEqual(hands_sense._manifest(p), {"shape": None, "control": None})


@unittest.skipUnless(JAIL_PATH.exists(), "the real jail binary is not present on this box")
class TestRunInJailReal(unittest.TestCase):
    def test_a_simple_program_runs_and_returns_stdout(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        prog = _write_program(shelf, "const", '# control: positive\nprint("#"*4)\n')
        scratch = Path(tempfile.mkdtemp())
        result = hands_sense.run_in_jail(JAIL_PATH, shelf, prog, scratch, cpu=10, mem=512, wall=20)
        self.assertEqual(result["exit"], 0)
        self.assertEqual(result["stdout"], b"####\n")
        self.assertFalse(result["timed_out"])
        self.assertGreater(result["dt_ms"], 0.0)

    def test_negative_control_reads_input_txt_from_scratch(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        prog = _write_program(shelf, "neg", '# control: negative\nwith open("INPUT.txt") as f:\n    print(f.read().strip())\n')
        scratch = Path(tempfile.mkdtemp())
        result = hands_sense.run_in_jail(JAIL_PATH, shelf, prog, scratch, cpu=10, mem=512, wall=20, input_text="42")
        self.assertEqual(result["exit"], 0)
        self.assertEqual(result["stdout"], b"42\n")

    def test_fence_control_permission_denied_on_stderr_not_a_creature_error(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        prog = _write_program(shelf, "fence", '# control: fence\nimport socket\nsocket.socket()\n')
        scratch = Path(tempfile.mkdtemp())
        result = hands_sense.run_in_jail(JAIL_PATH, shelf, prog, scratch, cpu=10, mem=512, wall=20)
        self.assertNotEqual(result["exit"], 0)
        self.assertIn(b"Permission denied", result["stderr"])
        self.assertEqual(result["stdout"], b"")

    def test_crash_control_glyph_decodes_with_replacement_char(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        prog = _write_program(
            shelf, "crash",
            "# control: crash\n"
            "import sys\n"
            "sys.stdout.buffer.write(b'program 441\\n')\n"
            "sys.stdout.buffer.write('\\u25f9'.encode('utf-8')[:2])\n"
            "sys.stdout.buffer.flush()\n",
        )
        scratch = Path(tempfile.mkdtemp())
        result = hands_sense.run_in_jail(JAIL_PATH, shelf, prog, scratch, cpu=10, mem=512, wall=20)
        self.assertEqual(result["exit"], 0)
        text = result["stdout"].decode("utf-8", errors="replace")   # G-MOT-4 precondition 1
        self.assertIn("\ufffd", text)
        with self.assertRaises(UnicodeDecodeError):
            result["stdout"].decode("utf-8")   # the strict decode this module never uses -- proves the plant is real

    def test_wall_clock_plant_caught_by_jail_run_itself(self) -> None:
        """G-MOT-4's own wall-time plant: a program that sleeps past `wall` is killed and jail_run returns
        124 -- caught by the CONTRACT (jail_run.cpp's own alarm), not by this module inventing a timeout."""
        shelf = Path(tempfile.mkdtemp())
        prog = _write_program(shelf, "hang", "# control: hang\nimport time\ntime.sleep(5)\n")
        scratch = Path(tempfile.mkdtemp())
        result = hands_sense.run_in_jail(JAIL_PATH, shelf, prog, scratch, cpu=10, mem=512, wall=1)
        self.assertEqual(result["exit"], 124)


@unittest.skipUnless(JAIL_PATH.exists(), "the real jail binary is not present on this box")
class TestSenseThreadEndToEnd(unittest.TestCase):
    def test_act_file_triggers_a_run_publishes_eye_outcome_touch_in_order_and_advances_cursor(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        _write_program(shelf, "circle_0", '# shape: circle\nprint("#"*4)\n')
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)

        stop_event = threading.Event()
        t = threading.Thread(target=lambda: hands_sense.sense(
            tape.publish, stop_event, root=root, jail_path=JAIL_PATH, shelf_dir=shelf,
            cpu=10, mem=512, wall=20, poll_period=0.05), daemon=True)
        t.start()
        try:
            act_dir = root / "hands"
            act_dir.mkdir(parents=True, exist_ok=True)
            (act_dir / "ACT.tmp").write_text(json.dumps({"seq": 1, "program": "circle_0", "at": "2026-01-01T00:00:00.000Z"}))
            (act_dir / "ACT.tmp").rename(act_dir / "ACT")
            deadline = time.time() + 10.0
            rows = []
            while time.time() < deadline:
                rows = _tape_rows(root)
                if len(rows) >= 3:
                    break
                time.sleep(0.1)
        finally:
            stop_event.set()
            t.join(timeout=5.0)

        self.assertEqual([r["sense"] for r in rows], ["eye", "outcome", "touch"])
        self.assertEqual(rows[0]["meta"]["source"], "hands")
        self.assertEqual(rows[0]["meta"]["program"], "circle_0")
        self.assertEqual(rows[0]["meta"]["shape"], "circle")
        self.assertEqual(rows[1]["meta"]["act"], "circle_0")
        self.assertEqual(rows[2]["meta"]["program"], "circle_0")
        moments = {r["meta"]["moment"] for r in rows}
        self.assertEqual(len(moments), 1, "all three rows of one run share one moment")
        cursor_path = root / "hands" / "CURSOR"
        self.assertTrue(cursor_path.exists())
        self.assertEqual(cursor_path.read_text().strip(), "1")

        img = Image.open(root / "tape" / rows[0]["payload"]).convert("RGB")
        self.assertEqual(img.size, (128, 128))

    def test_stale_act_never_reserved_a_second_time(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        _write_program(shelf, "const", '# control: positive\nprint("#")\n')
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        act_dir = root / "hands"
        act_dir.mkdir(parents=True, exist_ok=True)
        (act_dir / "ACT.tmp").write_text(json.dumps({"seq": 1, "program": "const", "at": "x"}))
        (act_dir / "ACT.tmp").rename(act_dir / "ACT")

        stop_event = threading.Event()
        t = threading.Thread(target=lambda: hands_sense.sense(
            tape.publish, stop_event, root=root, jail_path=JAIL_PATH, shelf_dir=shelf,
            cpu=10, mem=512, wall=20, poll_period=0.05), daemon=True)
        t.start()
        time.sleep(1.5)   # give it several poll periods to (wrongly) re-serve seq 1 if it were going to
        stop_event.set(); t.join(timeout=5.0)

        rows = [r for r in _tape_rows(root) if r["sense"] == "eye"]
        self.assertEqual(len(rows), 1, "seq 1 must be served exactly once, however many poll periods pass")


def _tape_rows(root: Path):
    out = []
    for f in sorted((root / "tape").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return sorted(out, key=lambda r: r["seq"])


if __name__ == "__main__":
    unittest.main()
