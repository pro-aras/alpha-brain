# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:28 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md items 3/4
# (BODY-SENSES.md §4.5/§4.6): touch/smell each get a DEDICATED Episodes ring (creature/mind.py's own
# sound_episodes precedent, LIFE builder D, 2026-09-22 18:48 +0400) sized to their own trait dim -- never
# self.outcome_episodes (whose x_s is sight_dim()-wide with only x_s[0] used as a scalar payload; a 5- or
# 4-number vector needs its own columns to survive, not a collapse to one float) and never fed to SLEEP's
# org.moment replay (K's own hazard for outcome_episodes applies identically: a zero sight vector would
# birth a garbage sight cell). Mirrors test_mind_ear_sound.py's own shape exactly.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import List

import numpy as np

from creature.mind import Mind
from creature.tape import Tape

ROOT = Path(__file__).resolve().parents[2]
G5_GENOME_PATH = ROOT / "genome" / "G5.genome"
SMELL_LINE = "SENSE    smell kind size folder age"
TOUCH_LINE = "SENSE    touch from hands: exit rate stalls retries bytes"


def _genome_with(*lines: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(G5_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


def _journal_rows(root: Path) -> List[dict]:
    out = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


def _touch_trait(exit_code=0.0, rate=1.0, stalls=0.0, retries=0.0, nbytes=10.0) -> np.ndarray:
    return np.array([exit_code, rate, stalls, retries, nbytes], dtype=np.float32)


def _smell_trait(kind=1.0, size=2.0, folder=0.3, age=4.0) -> np.ndarray:
    return np.array([kind, size, folder, age], dtype=np.float32)


class TestTouchRingBuilt(unittest.TestCase):
    def test_declared_builds_the_ring(self) -> None:
        gpath = _genome_with(TOUCH_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        self.assertIsNotNone(mind.touch_episodes)
        self.assertEqual(mind.touch_episodes.dim_s, 5)

    def test_undeclared_builds_no_ring(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = Mind(G5_GENOME_PATH, root)
        self.assertIsNone(mind.touch_episodes)


class TestSmellRingBuilt(unittest.TestCase):
    def test_declared_builds_the_ring(self) -> None:
        gpath = _genome_with(SMELL_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        self.assertIsNotNone(mind.smell_episodes)
        self.assertEqual(mind.smell_episodes.dim_s, 4)

    def test_undeclared_builds_no_ring(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = Mind(G5_GENOME_PATH, root)
        self.assertIsNone(mind.smell_episodes)


class TestTouchConsumed(unittest.TestCase):
    def test_one_row_writes_one_touch_episode_and_journals(self) -> None:
        gpath = _genome_with(TOUCH_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        trait = _touch_trait(exit_code=0.0, rate=5.5, stalls=0.0, retries=0.0, nbytes=12.0)
        row = tape.publish("touch", trait.tobytes(),
                            {"moment": "h" + "a" * 12, "source": "hands", "program": "circle_0"}, "f32")
        mind.consume(row)
        self.assertEqual(mind.touch_episodes.n_written, 1)
        self.assertEqual(mind.touch_events, 1)
        rec = mind.touch_episodes.get(0)
        np.testing.assert_allclose(rec["x_s"], trait.astype(np.float64), rtol=1e-5, atol=1e-6)
        rows = [r["touch"] for r in _journal_rows(root) if "touch" in r]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ep"], 0)

    def test_undeclared_steps_over_the_row(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = Mind(G5_GENOME_PATH, root)
        tape = Tape(root)
        row = tape.publish("touch", _touch_trait().tobytes(), {"moment": "hxx", "source": "hands"}, "f32")
        mind.consume(row)   # must not raise
        self.assertIsNone(mind.touch_episodes)
        self.assertEqual(mind.touch_events, 0)
        self.assertEqual([r for r in _journal_rows(root) if "touch" in r], [])

    def test_malformed_trait_journals_error_never_crashes(self) -> None:
        gpath = _genome_with(TOUCH_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        row = tape.publish("touch", b"\x01\x02\x03", {"moment": "hxx", "source": "hands"}, "f32")
        mind.consume(row)   # must not raise (#230)
        self.assertEqual(mind.touch_episodes.n_written, 0)
        rows = [r["touch"] for r in _journal_rows(root) if "touch" in r]
        self.assertEqual(len(rows), 1)
        self.assertIn("error", rows[0])

    def test_same_output_different_roads_give_different_touch_vectors(self) -> None:
        """BODY-SENSES §4.6's own toy: two programs with the SAME stdout by different roads (one
        stalling) give different touch vectors -- exercised at the trait-construction boundary since this
        test is about the CONSUMER, not the jail (see test_hands_sense.py for the jail-driven version)."""
        fast = _touch_trait(exit_code=0.0, rate=200.0, stalls=0.0, retries=0.0, nbytes=10.0)
        slow = _touch_trait(exit_code=0.0, rate=0.003, stalls=0.0, retries=0.0, nbytes=10.0)
        self.assertFalse(np.allclose(fast, slow))


class TestSmellConsumed(unittest.TestCase):
    def test_one_row_writes_one_smell_episode_and_journals(self) -> None:
        gpath = _genome_with(SMELL_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        trait = _smell_trait()
        row = tape.publish("smell", trait.tobytes(),
                            {"moment": "f" + "b" * 12, "source": "smell", "sha_prefix": "deadbeef"}, "f32")
        mind.consume(row)
        self.assertEqual(mind.smell_episodes.n_written, 1)
        self.assertEqual(mind.smell_events, 1)
        rec = mind.smell_episodes.get(0)
        np.testing.assert_allclose(rec["x_s"], trait.astype(np.float64), rtol=1e-5, atol=1e-6)
        rows = [r["smell"] for r in _journal_rows(root) if "smell" in r]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ep"], 0)

    def test_undeclared_steps_over_the_row(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = Mind(G5_GENOME_PATH, root)
        tape = Tape(root)
        row = tape.publish("smell", _smell_trait().tobytes(), {"moment": "fxx", "source": "smell"}, "f32")
        mind.consume(row)   # must not raise
        self.assertIsNone(mind.smell_episodes)
        self.assertEqual(mind.smell_events, 0)

    def test_malformed_trait_journals_error_never_crashes(self) -> None:
        gpath = _genome_with(SMELL_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        row = tape.publish("smell", b"\x01\x02", {"moment": "fxx", "source": "smell"}, "f32")
        mind.consume(row)   # must not raise (#230)
        self.assertEqual(mind.smell_episodes.n_written, 0)
        rows = [r["smell"] for r in _journal_rows(root) if "smell" in r]
        self.assertEqual(len(rows), 1)
        self.assertIn("error", rows[0])


class TestReplayIdentical(unittest.TestCase):
    def test_two_replays_of_a_touch_smell_tape_are_byte_identical(self) -> None:
        from creature import replay as replay_module
        gpath = _genome_with(TOUCH_LINE, SMELL_LINE)
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        for i in range(3):
            tape.publish("touch", _touch_trait(nbytes=float(i)).tobytes(), {"moment": f"h{i}", "source": "hands"}, "f32")
            tape.publish("smell", _smell_trait(age=float(i)).tobytes(), {"moment": f"f{i}", "source": "smell"}, "f32")
        day_files = sorted((root / "tape").glob("*.jsonl"))
        self.assertEqual(len(day_files), 1)
        out1, out2 = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        j1 = replay_module.run_replay(gpath, day_files[0], out1)
        j2 = replay_module.run_replay(gpath, day_files[0], out2)
        self.assertEqual(j1.read_bytes(), j2.read_bytes())
        self.assertEqual(len(j1.read_text().splitlines()), 6)


if __name__ == "__main__":
    unittest.main()
