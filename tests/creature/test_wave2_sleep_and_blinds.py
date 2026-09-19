# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 01:15 +0400 — A10: SLEEP in the mind (PREREG §11.1 step 4)
# + the six blinds (sleep/predict/frozen/curiosity/park/gaze) through Mind(blind=...) and creature.replay --blind.
# Test: replay with each blind is itself replay-identical, and differs from the unblinded journal only where
# that gene actually acts (curiosity/park have no mechanism yet -- THINK is A11 -- so they are NOT asserted to differ).
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature import replay as replay_mod
from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import world
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
SLEEP_GENOME = ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome"

BLINDS = ("gaze", "sleep", "predict", "frozen", "curiosity", "park")
KNOWN_TO_ACT = ("gaze", "sleep", "predict", "frozen")   # curiosity/park have no mechanism until A11 (THINK)


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_tape(root: Path, n: int = 90, seed: int = 555) -> None:
    """Enough worded canvases to cross the test genome's SLEEP boundary (every 40 moments = 10 canvases
    at 4 fixations each) more than once, and a few sight-only canvases mixed in."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    for i in range(n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        if i % 7 != 0:      # most canvases worded; every 7th sight-only
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")


class TestSleepGenomeParses(unittest.TestCase):
    def test_sleep_test_genome_declares_sleep(self) -> None:
        genome = parse_genome(SLEEP_GENOME.read_text())
        self.assertIn("SLEEP", genome.declared)
        self.assertIn("PREDICT", genome.declared)
        self.assertIn("FAST", genome.declared)


class TestSleepJournaling(unittest.TestCase):
    def test_sleep_row_journaled_sharing_the_triggering_seq(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root)
        mind = Mind(SLEEP_GENOME, root)
        for r in read_tape(root):
            mind.consume(r)
        self.assertGreater(mind._last_sleep_at, 0, "the tape must be long enough to cross at least one SLEEP boundary")

        journal_files = sorted((root / "journal").glob("*.jsonl"))
        rows = [json.loads(l) for l in journal_files[0].read_text().splitlines() if l.strip()]
        sleep_rows = [r for r in rows if "sleep" in r]
        self.assertGreater(len(sleep_rows), 0)
        for sr in sleep_rows:
            self.assertIn("seq", sr); self.assertIn("hash", sr)
            self.assertIn("replayed", sr["sleep"]); self.assertIn("cycle", sr["sleep"])
            # the sleep row's seq must belong to some real tape/canvas row (it shares the triggering canvas's seq)
            canvas_rows_same_seq = [r for r in rows if r.get("seq") == sr["seq"] and "sleep" not in r]
            self.assertEqual(len(canvas_rows_same_seq), 1)

    def test_replay_reproduces_the_sleep_rows(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root)
        mind = Mind(SLEEP_GENOME, root)
        for r in read_tape(root):
            mind.consume(r)

        tape_files = sorted((root / "tape").glob("*.jsonl"))
        journal_files = sorted((root / "journal").glob("*.jsonl"))
        out_dir = Path(tempfile.mkdtemp())
        rc = replay_mod.main(["--genome", str(SLEEP_GENOME), "--tape", str(tape_files[0]),
                               "--against", str(journal_files[0]), "--out", str(out_dir)])
        self.assertEqual(rc, 0)


class TestBlindsReplayIdentical(unittest.TestCase):
    """Each of the six blinds: two independent replays of the SAME tape with that blind are
    byte-identical to each other (the twin is itself deterministic)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp())
        # 150 canvases: measured directly (not assumed) to grow total cells to 60 unblinded -- past the
        # default FROZEN threshold (50, FROZEN's own parser clause not yet on master -- PREREG §11.1 step
        # 5's documented default) so --blind frozen actually refuses births and is observably different.
        # A shorter, 60-canvas tape reached only 28 total cells and --blind frozen produced NO divergence
        # at all, which the first draft of this test would have missed.
        _build_tape(cls.root, n=150, seed=777)
        cls.tape_path = sorted((cls.root / "tape").glob("*.jsonl"))[0]

    def test_each_blind_is_internally_replay_identical(self) -> None:
        for blind in BLINDS:
            with self.subTest(blind=blind):
                out1 = Path(tempfile.mkdtemp())
                j1 = replay_mod.run_replay(SLEEP_GENOME, self.tape_path, out1, blind=frozenset({blind}))
                out2 = Path(tempfile.mkdtemp())
                j2 = replay_mod.run_replay(SLEEP_GENOME, self.tape_path, out2, blind=frozenset({blind}))
                rows1 = replay_mod.read_mind_journal(j1)
                rows2 = replay_mod.read_mind_journal(j2)
                self.assertIsNone(replay_mod.compare(rows1, rows2), f"--blind {blind} must itself be replay-identical")

    def test_blinds_known_to_act_differ_from_unblinded(self) -> None:
        out0 = Path(tempfile.mkdtemp())
        j0 = replay_mod.run_replay(SLEEP_GENOME, self.tape_path, out0, blind=frozenset())
        rows0 = replay_mod.read_mind_journal(j0)
        for blind in KNOWN_TO_ACT:
            with self.subTest(blind=blind):
                out = Path(tempfile.mkdtemp())
                j = replay_mod.run_replay(SLEEP_GENOME, self.tape_path, out, blind=frozenset({blind}))
                rows = replay_mod.read_mind_journal(j)
                self.assertIsNotNone(replay_mod.compare(rows0, rows), f"--blind {blind} must differ from the unblinded journal")

    def test_curiosity_and_park_blinds_currently_inert(self) -> None:
        """Honest negative, not a bug: THINK (A11) does not exist yet, so blinding curiosity/park has
        no mechanism to remove -- the journals are identical to the unblinded one. Re-run this assertion
        once A11 lands; it should then flip to "differ", matching the other four."""
        out0 = Path(tempfile.mkdtemp())
        j0 = replay_mod.run_replay(SLEEP_GENOME, self.tape_path, out0, blind=frozenset())
        rows0 = replay_mod.read_mind_journal(j0)
        for blind in ("curiosity", "park"):
            with self.subTest(blind=blind):
                out = Path(tempfile.mkdtemp())
                j = replay_mod.run_replay(SLEEP_GENOME, self.tape_path, out, blind=frozenset({blind}))
                rows = replay_mod.read_mind_journal(j)
                self.assertIsNone(replay_mod.compare(rows0, rows), f"--blind {blind} is expected inert before A11 (THINK)")


if __name__ == "__main__":
    unittest.main()
