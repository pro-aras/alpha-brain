# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 23:20 +0400 — A6 tests: a live 200-canvas tape replays
# byte-identical; a corrupted payload copy (sha left stale) diverges at that seq; --blind gaze is itself
# replay-identical and differs from the surprise-gaze journal.
from __future__ import annotations

import io
import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature import replay, world_maker
from creature.body import Body
from creature.tape import read_tape

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"


def _run_live_200(root: Path) -> None:
    """A live body, maker at period 0.05, run until >= 200 eye rows are on the tape, drain the mind's
    queue before stopping (so the reference journal covers every published row)."""
    body = Body(root, GENOME_PATH)
    maker = body.add_sense("maker", lambda p, se: world_maker.sense(p, se, root=root, period=0.05))
    body.start()
    deadline = time.time() + 60.0
    while time.time() < deadline:
        eye_rows = [r for r in read_tape(root) if r["sense"] == "eye"]
        if len(eye_rows) >= 200:
            break
        time.sleep(0.2)
    else:
        body.stop()
        raise AssertionError("did not reach 200 eye rows within 60 s")
    maker.stop()
    maker.join(timeout=5.0)
    drain_deadline = time.time() + 20.0
    while not body.q.empty() and time.time() < drain_deadline:
        time.sleep(0.1)
    time.sleep(1.0)   # grace for the in-flight consume() call to finish
    body.stop()


def _single_journal_and_tape_files(root: Path) -> tuple[Path, Path]:
    tape_files = sorted((root / "tape").glob("*.jsonl"))
    journal_files = sorted((root / "journal").glob("*.jsonl"))
    assert len(tape_files) == 1, f"test expects one tape day file, got {tape_files}"
    assert len(journal_files) == 1, f"test expects one journal day file, got {journal_files}"
    return tape_files[0], journal_files[0]


class TestReplayGate43(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp())
        _run_live_200(cls.root)
        cls.tape_path, cls.journal_path = _single_journal_and_tape_files(cls.root)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_replay_matches_live_journal(self) -> None:
        out_dir = Path(tempfile.mkdtemp())
        rc = replay.main(["--genome", str(GENOME_PATH), "--tape", str(self.tape_path),
                           "--against", str(self.journal_path), "--out", str(out_dir)])
        self.assertEqual(rc, 0)

    def test_corrupted_payload_copy_diverges_at_that_seq(self) -> None:
        corrupt_root = Path(tempfile.mkdtemp())
        shutil.copytree(self.root / "tape", corrupt_root / "tape")
        tape_path = corrupt_root / "tape" / self.tape_path.name

        rows = [json.loads(l) for l in self.tape_path.read_text().splitlines() if l.strip()]
        eye_rows = [r for r in rows if r["sense"] == "eye"]
        target = eye_rows[len(eye_rows) // 2]     # a mid-stream eye row
        target_seq = target["seq"]
        payload_path = corrupt_root / "tape" / target["payload"]
        rgb = np.asarray(Image.open(payload_path).convert("RGB"), dtype=np.uint8)
        # a single flipped byte/pixel this far from the thing is (measured) too small for gaze's
        # saliency-pooled fixations to notice -- corrupt a block squarely inside the thing's own
        # bounding box (its truth, never on the tape, PREREG §2.1) so the content genuinely changes.
        truth = json.loads((self.root / "truth" / f"{target_seq:09d}.json").read_text())
        ty, tx = truth["top"], truth["left"]
        corrupted = rgb.copy()
        corrupted[ty:ty + 16, tx:tx + 16, :] = 0
        buf = io.BytesIO()
        Image.fromarray(corrupted, mode="RGB").save(buf, format="PNG")
        payload_path.write_bytes(buf.getvalue())              # the row's own "sha" field is left AS IS (stale)

        out_dir = Path(tempfile.mkdtemp())
        rc = replay.main(["--genome", str(GENOME_PATH), "--tape", str(tape_path),
                           "--against", str(self.journal_path), "--out", str(out_dir)])
        self.assertEqual(rc, 1)

        out_journal = out_dir / "journal.jsonl"
        got = replay.read_mind_journal(out_journal)
        want = replay.read_mind_journal(self.journal_path)
        diff = replay.compare(got, want)
        self.assertIsNotNone(diff)
        seq, _field = diff
        self.assertEqual(seq, target_seq, "the first divergence must be the corrupted row's own seq")
        shutil.rmtree(corrupt_root, ignore_errors=True)
        shutil.rmtree(out_dir, ignore_errors=True)

    def test_blind_gaze_twin_is_replay_identical_and_differs_from_surprise(self) -> None:
        out_normal = Path(tempfile.mkdtemp())
        journal_normal = replay.run_replay(GENOME_PATH, self.tape_path, out_normal, blind=frozenset())

        out_blind_1 = Path(tempfile.mkdtemp())
        journal_blind_1 = replay.run_replay(GENOME_PATH, self.tape_path, out_blind_1, blind=frozenset({"gaze"}))
        out_blind_2 = Path(tempfile.mkdtemp())
        journal_blind_2 = replay.run_replay(GENOME_PATH, self.tape_path, out_blind_2, blind=frozenset({"gaze"}))

        rows_normal = replay.read_mind_journal(journal_normal)
        rows_blind_1 = replay.read_mind_journal(journal_blind_1)
        rows_blind_2 = replay.read_mind_journal(journal_blind_2)

        self.assertIsNone(replay.compare(rows_blind_1, rows_blind_2), "the blind-gaze twin must itself be replay-identical")
        self.assertIsNotNone(replay.compare(rows_blind_1, rows_normal), "the blind-gaze twin must differ from the surprise-gaze journal")
        for d in (out_normal, out_blind_1, out_blind_2):
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
