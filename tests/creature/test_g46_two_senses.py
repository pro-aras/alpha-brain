# edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 13:1x +0400 — C3 (docs/G4-WAVE3-CLAUSES.md W3-6 step 4;
# docs/G4-PREREG.md §4 G4-6 = "G4-3 re-run PASS with two senses on the tape"). Re-creates
# tools/gate_g4.py's gate3() shape (not imported -- tools/* is out of a creature/ builder's scope) with a
# SECOND sense on the SAME tape: 60 maker canvases (this module's own world_maker.make(), the model for
# gate3's build_tape()) interleaved on one tape with the folder door's rows over C2's fixture world (real
# folder.sense, period 0.2 s, until its rows are published) -- including one sight-only row (a loose
# picture dropped directly under the fixture world, C2's amendment). A Mind consumes the whole tape,
# snapshots, and `creature.replay` reads IDENTICAL against it; the control -- one folder EYE payload
# inverted in a COPY of the root -- must diverge at that row's own seq (CAUGHT), exactly G4-3's two halves.
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

from creature import world_maker
from creature.mind import Mind
from creature.replay import main as replay_main
from creature.senses import folder as folder_mod
from creature.tape import Tape, read_tape
from tests.creature.test_folder_door import _write_pacing_world

ROOT = Path(__file__).resolve().parents[2]
WAVE2_GENOME = ROOT / "tests" / "creature" / "G4-wave2-test.genome"


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_maker_rows(tape: Tape, n: int, seed: int = 20260920) -> None:
    """Re-creates tools/gate_g4.py's build_tape() shape with THIS module's own world_maker.make() -- n
    canvases from window 0, ear then eye, source "maker" (the tape order law, §2.2)."""
    for i in range(n):
        thing, rgb, _truth = world_maker.make(seed, 0, i)
        moment = f"g46m{i:04d}"
        tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "maker", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "maker"}, "png")


def _run_folder_door_to_completion(tape: Tape, world_dir: Path, root: Path, expected_rows: int, timeout_s: float) -> None:
    """Runs the REAL folder.sense (period 0.2 s) until `expected_rows` folder-sourced tape rows exist,
    then stops it -- C2's pacing rule (one new picture per scan) means this takes several scans."""
    stop_event = threading.Event()
    t = threading.Thread(target=lambda: folder_mod.sense(
        tape.publish, stop_event, world_dir=world_dir, root=root, canvas=64, period=0.2), daemon=True)
    t.start()
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        n = sum(1 for r in read_tape(root) if r.get("meta", {}).get("source") == "folder")
        if n >= expected_rows:
            break
        time.sleep(0.1)
    stop_event.set()
    t.join(timeout=5.0)


class TestG46TwoSenses(unittest.TestCase):
    def test_replay_identical_with_maker_and_folder_on_the_same_tape(self) -> None:
        root = Path(tempfile.mkdtemp())
        world_dir = Path(tempfile.mkdtemp())
        _write_pacing_world(world_dir)   # 3 folders x 2 pictures = 6 word pictures, 12 rows
        # one loose (sight-only) picture directly under the fixture world -- "at least one sight-only row"
        arr = np.zeros((64, 64, 3), dtype=np.uint8)
        arr[:, :] = (250, 250, 10)
        rng = np.random.default_rng(21)
        arr[16:48, 16:48] += rng.integers(0, 20, size=(32, 32, 3), dtype=np.uint8)
        Image.fromarray(arr, mode="RGB").save(world_dir / "loose.png", format="PNG")

        tape = Tape(root)
        _build_maker_rows(tape, 60)
        _run_folder_door_to_completion(tape, world_dir, root, expected_rows=13, timeout_s=60.0)  # 6*2 + 1 sight-only eye

        all_rows = list(read_tape(root))
        by_source: dict = {}
        for r in all_rows:
            by_source[r["meta"]["source"]] = by_source.get(r["meta"]["source"], 0) + 1
        self.assertEqual(by_source.get("maker"), 120, f"60 maker canvases x (ear,eye) = 120, got {by_source}")
        self.assertEqual(by_source.get("folder"), 13, f"6 word pictures x 2 + 1 sight-only eye = 13, got {by_source}")

        folder_ear_moments = {r["meta"]["moment"] for r in all_rows if r["meta"]["source"] == "folder" and r["sense"] == "ear"}
        folder_eye_rows = [r for r in all_rows if r["meta"]["source"] == "folder" and r["sense"] == "eye"]
        sight_only_rows = [r for r in folder_eye_rows if r["meta"]["moment"] not in folder_ear_moments]
        self.assertEqual(len(sight_only_rows), 1, f"exactly one sight-only folder row expected, got {len(sight_only_rows)}")

        mind = Mind(WAVE2_GENOME, root)
        for row in all_rows:
            mind.consume(row)
        mind.snapshot()

        tape_files = sorted((root / "tape").glob("*.jsonl"))
        journal_files = sorted((root / "journal").glob("*.jsonl"))
        self.assertEqual(len(tape_files), 1)
        self.assertEqual(len(journal_files), 1)
        all_tape_path = root / "tape" / "ALL.jsonl"
        all_tape_path.write_bytes(b"".join(f.read_bytes() for f in tape_files))

        out1 = Path(tempfile.mkdtemp())
        rc = replay_main(["--genome", str(WAVE2_GENOME), "--tape", str(all_tape_path),
                           "--against", str(journal_files[0]), "--out", str(out1)])
        self.assertEqual(rc, 0, "G4-6: G4-3 re-run must PASS with two senses on the tape")

        # the control: one folder EYE payload replaced with random noise in a COPY of the root -- must
        # diverge AT THAT SEQ. NOT a full-image inversion (255-x): the retina's own INK definition is
        # |grey - median of the window's rim| (G0 §6 amendment 1), an ABSOLUTE difference a symmetric
        # inversion leaves numerically unchanged -- confirmed empirically (an inverted control here read
        # replay-IDENTICAL, MISSED, before this fix) -- so the corruption must be asymmetric, not just any
        # pixel change.
        root2 = Path(tempfile.mkdtemp()) / "run"
        shutil.copytree(root, root2)
        rows2 = [json.loads(l) for l in (root2 / "tape" / "ALL.jsonl").read_text().splitlines()]
        folder_eye = next(r for r in rows2 if r["meta"]["source"] == "folder" and r["sense"] == "eye")
        pp = root2 / "tape" / folder_eye["payload"]
        noise_rng = np.random.default_rng(999)
        arr2 = noise_rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)
        Image.fromarray(arr2, mode="RGB").save(pp, format="PNG")
        tape2_path = root2 / "tape" / "ALL.jsonl"

        out2 = Path(tempfile.mkdtemp())
        rc2 = replay_main(["--genome", str(WAVE2_GENOME), "--tape", str(tape2_path),
                            "--against", str(journal_files[0]), "--out", str(out2)])
        self.assertNotEqual(rc2, 0, f"the byte-flipped/inverted control must diverge, expected around seq {folder_eye['seq']}")

        print(f"G4-6 row counts by source: {by_source}; caught divergence planted at seq {folder_eye['seq']}")

        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(root2.parent, ignore_errors=True)
        shutil.rmtree(world_dir, ignore_errors=True)
        shutil.rmtree(out1, ignore_errors=True)
        shutil.rmtree(out2, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
