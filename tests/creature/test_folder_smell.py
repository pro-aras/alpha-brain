# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 4
# (BODY-SENSES.md §4.5): the folder door publishes a `smell` row BEFORE it opens a picture (`meta.source:
# "smell"`), gated on a new `smell: bool = False` parameter (byte-identical to before when False, matching
# every other additive-parameter convention this file already uses — C2's `period`, EAR's own gate shape).
from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.senses import folder as folder_sense
from creature.tape import Tape, read_tape

ROOT = Path(__file__).resolve().parents[2]


def _write_picture(world_dir: Path, folder: str, name: str) -> Path:
    d = world_dir / folder
    d.mkdir(parents=True, exist_ok=True)
    arr = np.zeros((32, 32, 3), dtype=np.uint8)
    arr[:, :] = (200, 30, 30)
    p = d / name
    Image.fromarray(arr, mode="RGB").save(p, format="PNG")
    return p


def _rows(root: Path):
    return sorted(read_tape(root), key=lambda r: r["seq"])


class TestSmellOffByDefault(unittest.TestCase):
    def test_smell_false_publishes_no_smell_rows(self) -> None:
        world_dir = Path(tempfile.mkdtemp())
        _write_picture(world_dir, "circle", "pic1.png")
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: folder_sense.sense(
            tape.publish, stop_event, world_dir=world_dir, root=root, canvas=128, period=0.1, smell=False), daemon=True)
        t.start()
        time.sleep(0.6)
        stop_event.set(); t.join(timeout=5.0)
        rows = _rows(root)
        self.assertEqual([r["sense"] for r in rows if r["sense"] == "smell"], [])


class TestSmellOn(unittest.TestCase):
    def test_smell_row_published_before_eye_row_same_moment(self) -> None:
        world_dir = Path(tempfile.mkdtemp())
        _write_picture(world_dir, "circle", "pic1.png")
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: folder_sense.sense(
            tape.publish, stop_event, world_dir=world_dir, root=root, canvas=128, period=0.1, smell=True), daemon=True)
        t.start()
        deadline = time.time() + 10.0
        rows = []
        while time.time() < deadline:
            rows = _rows(root)
            if len(rows) >= 3:
                break
            time.sleep(0.1)
        stop_event.set(); t.join(timeout=5.0)

        senses = [r["sense"] for r in rows]
        self.assertIn("smell", senses)
        smell_idx = senses.index("smell")
        eye_idx = senses.index("eye")
        self.assertLess(smell_idx, eye_idx, "smell must be published BEFORE the eye row (before any picture is opened)")
        smell_row = rows[smell_idx]
        self.assertEqual(smell_row["meta"]["source"], "smell")
        self.assertIn("sha_prefix", smell_row["meta"])
        self.assertEqual(smell_row["meta"]["moment"], rows[eye_idx]["meta"]["moment"], "the smell and eye rows of one picture share one moment")

        trait = np.frombuffer((root / "tape" / smell_row["payload"]).read_bytes(), dtype="float32")
        self.assertEqual(trait.shape, (4,))
        for v in trait:
            self.assertTrue(np.isfinite(float(v)), f"smell trait must be finite: {trait}")

    def test_folder_field_is_a_hash_never_the_name(self) -> None:
        """BODY-SENSES §4.5's own words: "folder (a stable hash of the folder name — never the name,
        which is the answer)"."""
        world_dir = Path(tempfile.mkdtemp())
        _write_picture(world_dir, "circle", "pic1.png")
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: folder_sense.sense(
            tape.publish, stop_event, world_dir=world_dir, root=root, canvas=128, period=0.1, smell=True), daemon=True)
        t.start()
        deadline = time.time() + 10.0
        rows = []
        while time.time() < deadline:
            rows = [r for r in _rows(root) if r["sense"] == "smell"]
            if rows:
                break
            time.sleep(0.1)
        stop_event.set(); t.join(timeout=5.0)
        self.assertTrue(rows)
        text = json.dumps(rows[0]["meta"])
        self.assertNotIn("circle", text, "the folder's own NAME must never appear on the tape row (it is the answer)")


if __name__ == "__main__":
    unittest.main()
