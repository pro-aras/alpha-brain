# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:39 +0400 — LIFE-D-ACT-SOUND.md item 3 (L-13;
# EAR.md §4's own TRAIT line: band 32 + onset-shape 4 + level 1 = 37 floats): creature/mind.py gains the
# `elif sense == "ear-sound"` branch consume() lacked (the brief's own READ FIRST pointer: "no ear-sound
# branch -- :244-257"). Gated on FAST declaring the "sound" key (genome/machinery.py's parser, L-13's other
# half): a SEPARATE 37-wide Episodes ring (K's own hazard for the reflex ring applies identically -- never
# fed to SLEEP's org.moment replay, a zero-vector x_s would birth a garbage sight cell), journaled, STATUS
# sound_events on every branch (#164). Undeclared: a plain no-op step-over, byte-for-byte the pre-L-13
# behaviour (the twin, #228).
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import List

import numpy as np

from creature.mind import Mind
from creature.tape import Tape
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME_PATH = ROOT / "genome" / "G4.genome"
FAST_SOUND_LINE = "FAST     episodes 2000 keys sight words surprise sound"
FAST_PLAIN_LINE = "FAST     episodes 2000 keys sight words surprise"


def _g4_with(*lines: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(G4_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


def _trait(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.normal(size=37).astype(np.float32)
    v = (v / np.linalg.norm(v)).astype(np.float32)
    return v


def _event_meta(idx: int, when: float) -> dict:
    return {"moment": f"aFAKE{idx:04d}e0000", "source": "ear_sound", "file": "clip.wav", "sha_file": "deadbeef",
            "event_index": 0, "when": when, "level": -3.5,
            "band": [0.01 * i for i in range(32)], "onset_shape": [0.1, 0.2, 0.3, 0.4], "ownvoice": None,
            "provenance": {"front": "cochlea:gammatone-erb32-50-7800", "file": "clip.wav", "offset_s": when, "rate": 16000}}


def _journal_rows(root: Path) -> List[dict]:
    out = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


class TestParses(unittest.TestCase):
    def test_fast_with_sound_builds_the_ring(self) -> None:
        gpath = _g4_with(FAST_SOUND_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        self.assertIsNotNone(mind.sound_episodes)
        self.assertEqual(mind.sound_episodes.dim_s, 37)
        self.assertEqual(mind.sound_episodes.cap, 2000)

    def test_fast_without_sound_key_builds_no_ring(self) -> None:
        gpath = _g4_with(FAST_PLAIN_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        self.assertIsNone(mind.sound_episodes)

    def test_no_fast_at_all_builds_no_ring(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = Mind(G4_GENOME_PATH, root)
        self.assertIsNone(mind.sound_episodes)


class TestEventConsumed(unittest.TestCase):
    def test_one_event_writes_one_sound_episode(self) -> None:
        gpath = _g4_with(FAST_SOUND_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        trait = _trait(1)
        row = tape.publish("ear-sound", trait.tobytes(), _event_meta(1, 0.125), "f32")
        mind.consume(row)
        self.assertEqual(mind.sound_episodes.n_written, 1)
        self.assertEqual(mind.sound_events, 1)
        rec = mind.sound_episodes.get(0)
        np.testing.assert_allclose(rec["x_s"], trait.astype(np.float64), rtol=1e-5, atol=1e-6)
        self.assertEqual(rec["word"], "")
        sound_rows = [r["sound"] for r in _journal_rows(root) if "sound" in r]
        self.assertEqual(len(sound_rows), 1)
        self.assertEqual(sound_rows[0]["when"], 0.125)
        self.assertEqual(sound_rows[0]["file"], "clip.wav")
        self.assertEqual(sound_rows[0]["ep"], 0)

    def test_three_events_three_episodes_and_status_counts_on_every_branch(self) -> None:
        gpath = _g4_with(FAST_SOUND_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        for i in range(3):
            row = tape.publish("ear-sound", _trait(i + 10).tobytes(), _event_meta(i, 0.1 * i), "f32")
            mind.consume(row)
        self.assertEqual(mind.sound_episodes.n_written, 3)
        self.assertEqual(mind.sound_events, 3)

    def test_undeclared_sound_key_steps_over_the_row(self) -> None:
        """The twin (#228): FAST declared, but not the "sound" key -- an ear-sound row on the tape is
        harmless dead weight, exactly the pre-L-13 shape (ear.py's own docstring for outcome rows)."""
        gpath = _g4_with(FAST_PLAIN_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        row = tape.publish("ear-sound", _trait(2).tobytes(), _event_meta(2, 0.2), "f32")
        mind.consume(row)   # must not raise
        self.assertIsNone(mind.sound_episodes)
        self.assertEqual(mind.sound_events, 0)
        self.assertEqual([r for r in _journal_rows(root) if "sound" in r], [])

    def test_malformed_trait_bytes_journal_an_error_never_crash(self) -> None:
        gpath = _g4_with(FAST_SOUND_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        row = tape.publish("ear-sound", b"\x00\x01\x02\x03\x04", _event_meta(3, 0.3), "f32")  # not 37 float32s
        mind.consume(row)   # must not raise (#230: strict decoding of bytes the mind did not write)
        self.assertEqual(mind.sound_episodes.n_written, 0)
        rows = [r["sound"] for r in _journal_rows(root) if "sound" in r]
        self.assertEqual(len(rows), 1)
        self.assertIn("error", rows[0])


class TestReplayIdentical(unittest.TestCase):
    def test_two_replays_of_a_sound_tape_are_byte_identical(self) -> None:
        from creature import replay as replay_module
        gpath = _g4_with(FAST_SOUND_LINE)
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        for i in range(4):
            tape.publish("ear-sound", _trait(100 + i).tobytes(), _event_meta(i, 0.05 * i), "f32")
        day_files = sorted((root / "tape").glob("*.jsonl"))
        self.assertEqual(len(day_files), 1)
        out1, out2 = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        j1 = replay_module.run_replay(gpath, day_files[0], out1)
        j2 = replay_module.run_replay(gpath, day_files[0], out2)
        self.assertEqual(j1.read_bytes(), j2.read_bytes())
        self.assertEqual(len(j1.read_text().splitlines()), 4)


if __name__ == "__main__":
    unittest.main()
