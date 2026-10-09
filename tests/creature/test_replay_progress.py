# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 13:45 +0400 — run_replay's progress heartbeat tests
# (the 2026-10-09 F-plant lesson: a 17-h replay with zero external output reads as hung). The heartbeat is an optional
# stderr instrument, default OFF = byte-identical; the planted counts are asserted from the tape's own rows.
from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.replay import run_replay
from creature.tape import Tape
from genome import world

ROOT = Path(__file__).resolve().parents[2]
GENOME_PATH = ROOT / "genome" / "G4-skeleton.genome"


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_tape(root: Path) -> Path:
    """Four worded moments (ear + eye rows each), the wave3-seams form; returns the tape's day file."""
    mind = Mind(GENOME_PATH, root)
    tape = Tape(root)
    rng = np.random.default_rng(7)
    for i, thing in enumerate(("circle", "square", "triangle", "circle")):
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"s{i:03d}"
        at = f"2026-10-09T00:00:{i:02d}.000Z"
        mind.consume(tape.publish("ear", thing.encode("utf-8"),
                                  {"moment": moment, "source": "test", "word": thing}, "txt", at=at))
        mind.consume(tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png", at=at))
    days = sorted((root / "tape").glob("*.jsonl"))
    assert len(days) == 1, f"the toy expects one tape day file, got {days}"
    return days[0]


class TestReplayProgress(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.tape_day = _build_tape(self.root)
        self.n_rows = len(self.tape_day.read_text().splitlines())

    def test_default_is_silent(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            run_replay(GENOME_PATH, self.tape_day, Path(tempfile.mkdtemp()))
        self.assertEqual(err.getvalue(), "", "no progress_every argument: not one byte on stderr")

    def test_zero_is_silent(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            run_replay(GENOME_PATH, self.tape_day, Path(tempfile.mkdtemp()), progress_every=0)
        self.assertEqual(err.getvalue(), "")

    def test_heartbeat_cadence_and_planted_counts(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            run_replay(GENOME_PATH, self.tape_day, Path(tempfile.mkdtemp()), progress_every=2)
        lines = [l for l in err.getvalue().splitlines() if l.strip()]
        # cadence: one line every 2 rows + exactly one final line
        self.assertEqual(len(lines), self.n_rows // 2 + 1)
        self.assertIn(f"2/{self.n_rows}", lines[0])
        self.assertIn(f"done {self.n_rows}/{self.n_rows}", lines[-1])
        # the plant: the declared total IS the tape's own row count (a heartbeat that miscounts is caught here)
        for line in lines:
            self.assertIn(f"/{self.n_rows}", line)

    def test_journal_byte_identical_with_and_without(self) -> None:
        out_a, out_b = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            ja = run_replay(GENOME_PATH, self.tape_day, out_a, progress_every=1)
        jb = run_replay(GENOME_PATH, self.tape_day, out_b)
        self.assertEqual(ja.read_bytes(), jb.read_bytes(), "the heartbeat is outside the mind's road")
        self.assertGreater(len(err.getvalue().splitlines()), 0)


if __name__ == "__main__":
    unittest.main()
