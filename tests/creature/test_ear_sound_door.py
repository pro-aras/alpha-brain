# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 22:2x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 2.
"""test_ear_sound_door.py — the sound ear door: silence publishes nothing (BOTH halves: no file at all,
AND a file that IS silence), a real recording publishes EVENT rows shaped per EAR.md §4's TRAIT line, a
restart never re-publishes, and T7's own gate is exercised directly against genome/cochlea.py (the count a
hunk of REAL audio would publish, measured before anything is wired -- the brief's own discipline, item 2:
"T7 FIRST... before any event reaches the tape")."""
from __future__ import annotations

import json
import shutil
import tempfile
import threading
import time
import unittest
import wave
from pathlib import Path

import numpy as np

from creature.senses import ear as ear_sense
from creature.tape import Tape, read_tape
from genome import cochlea

LIBRISPEECH_CLIP = Path("/data/alpha3-library/audio/librispeech/dev-clean-wav/1272/128104/1272-128104-0000.wav")
A3_PRESENT = Path("/data/dev/alpha3/experiments/E52-hearing-the-cochlear-front/code/gammatone.py").exists()


def _write_wav(path: Path, x: np.ndarray, rate: int = 16000) -> None:
    x16 = np.clip(x * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(x16.tobytes())


def _ear_rows(root: Path):
    return [r for r in read_tape(root) if r["sense"] == "ear-sound"]


@unittest.skipUnless(A3_PRESENT, "E52's sha-pinned tree is not present on this box")
class TestSilencePublishesNothing(unittest.TestCase):
    """EAR.md §4/§5 Q1: "while silent it publishes nothing" -- BOTH readings of "silent" proven
    separately: (a) the door armed, no audio file present at all; (b) a wav file that IS digital silence."""

    def test_no_file_at_all_publishes_zero_rows(self) -> None:
        root = Path(tempfile.mkdtemp())
        audio_dir = Path(tempfile.mkdtemp())   # empty -- never gets a file
        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: ear_sense.sense(
            tape.publish, stop_event, audio_dir=audio_dir, root=root, rate=16000, period=0.1), daemon=True)
        t.start()
        time.sleep(1.5)   # several scans of an empty door
        stop_event.set(); t.join(timeout=5.0)
        self.assertEqual(_ear_rows(root), [], "an empty door must publish ZERO ear-sound rows")
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(audio_dir, ignore_errors=True)

    def test_a_silent_wav_publishes_zero_rows(self) -> None:
        root = Path(tempfile.mkdtemp())
        audio_dir = Path(tempfile.mkdtemp())
        _write_wav(audio_dir / "silence.wav", np.zeros(16000 * 3, dtype=np.float64))
        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: ear_sense.sense(
            tape.publish, stop_event, audio_dir=audio_dir, root=root, rate=16000, period=0.1), daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while (root / "ear_sound" / "SEEN.json").exists() is False and time.time() < deadline:
            time.sleep(0.1)
        time.sleep(0.5)   # a couple more scans -- must find nothing new
        stop_event.set(); t.join(timeout=5.0)
        self.assertEqual(_ear_rows(root), [], "a digitally-silent wav must publish ZERO ear-sound rows")
        seen = json.loads((root / "ear_sound" / "SEEN.json").read_text())
        self.assertEqual(len(seen), 1, "the silent file must still be marked SEEN (never re-scanned forever)")
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(audio_dir, ignore_errors=True)

    def test_cochlea_analyse_zero_events_on_zero_signal_directly(self) -> None:
        """The same fact one layer down, against the organ itself (not the sense thread's polling)."""
        r = cochlea.analyse(np.zeros(16000 * 5, dtype=np.float64))
        self.assertEqual(r["events"], [])
        self.assertEqual(r["duration_s"], 5.0)


@unittest.skipUnless(LIBRISPEECH_CLIP.exists(), "LibriSpeech dev-clean corpus not present on this box")
class TestRealRecordingPublishesEvents(unittest.TestCase):
    def test_events_published_shaped_per_ear_md_trait_line(self) -> None:
        root = Path(tempfile.mkdtemp())
        audio_dir = Path(tempfile.mkdtemp())
        shutil.copy(LIBRISPEECH_CLIP, audio_dir / "clip.wav")
        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: ear_sense.sense(
            tape.publish, stop_event, audio_dir=audio_dir, root=root, rate=16000, period=0.2), daemon=True)
        t.start()
        deadline = time.time() + 15.0
        rows = []
        while time.time() < deadline:
            rows = _ear_rows(root)
            if rows:
                break
            time.sleep(0.2)
        time.sleep(0.5)
        stop_event.set(); t.join(timeout=5.0)

        self.assertGreater(len(rows), 0, "a real LibriSpeech clip must publish at least one event")
        for r in rows:
            m = r["meta"]
            self.assertEqual(m["source"], "ear_sound")
            self.assertEqual(m["file"], "clip.wav")
            self.assertIsInstance(m["when"], float)
            self.assertGreaterEqual(m["when"], 0.0)
            self.assertEqual(len(m["band"]), cochlea.N_BANDS)
            self.assertEqual(len(m["onset_shape"]), 4)
            self.assertIsInstance(m["level"], float)
            self.assertIsNone(m["ownvoice"], "no top-down prediction is wired on this branch -- must read None, never a guessed False")
            self.assertIn("provenance", m)
            self.assertEqual(m["provenance"]["file"], "clip.wav")
            # the TRAIT vector itself (band 32 + onset-shape 4 + level 1 = 37, unit length) is the payload
            trait = np.frombuffer(tape.payload_dir.joinpath(Path(r["payload"]).name).read_bytes(), dtype="float32")
            self.assertEqual(trait.shape, (37,))
            self.assertAlmostEqual(float(np.linalg.norm(trait)), 1.0, places=4)
        # events strictly ordered by their own onset instant within the file
        whens = [r["meta"]["when"] for r in rows]
        self.assertEqual(whens, sorted(whens))
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(audio_dir, ignore_errors=True)

    def test_restart_never_republishes(self) -> None:
        root = Path(tempfile.mkdtemp())
        audio_dir = Path(tempfile.mkdtemp())
        shutil.copy(LIBRISPEECH_CLIP, audio_dir / "clip.wav")
        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: ear_sense.sense(
            tape.publish, stop_event, audio_dir=audio_dir, root=root, rate=16000, period=0.2), daemon=True)
        t.start()
        deadline = time.time() + 15.0
        while time.time() < deadline and not _ear_rows(root):
            time.sleep(0.2)
        time.sleep(0.5)
        stop_event.set(); t.join(timeout=5.0)
        n1 = len(_ear_rows(root))
        self.assertGreater(n1, 0)

        stop_event2 = threading.Event()
        t2 = threading.Thread(target=lambda: ear_sense.sense(
            tape.publish, stop_event2, audio_dir=audio_dir, root=root, rate=16000, period=0.1), daemon=True)
        t2.start()
        time.sleep(1.5)
        stop_event2.set(); t2.join(timeout=5.0)
        self.assertEqual(len(_ear_rows(root)), n1, "a restart on the same root/audio_dir must never re-publish")
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(audio_dir, ignore_errors=True)


@unittest.skipUnless(LIBRISPEECH_CLIP.parent.parent.parent.exists(), "LibriSpeech dev-clean corpus not present on this box")
class TestT7EventRateGate(unittest.TestCase):
    """The brief's own T7 discipline (item 2), pinned as a real gate: an hour of real recording's own
    event rate must sit closer to the 5/s floor than the 100/s ceiling BEFORE the EVENT rule is trusted --
    measured here on a real (if short, for test speed) LibriSpeech sample, never assumed."""

    def test_event_rate_closer_to_five_than_hundred_per_second(self) -> None:
        import glob
        lib_dir = "/data/alpha3-library/audio/librispeech/dev-clean-wav"
        files = sorted(glob.glob(f"{lib_dir}/**/*.wav", recursive=True))[:15]   # a fast subset for a unit test; the full ~11-min T7 measurement is in the builder report
        self.assertGreater(len(files), 0)
        total_events = 0
        total_dur = 0.0
        for p in files:
            x = cochlea.read_wav_mono(Path(p))
            r = cochlea.analyse(x)
            total_events += len(r["events"])
            total_dur += r["duration_s"]
        rate = total_events / total_dur if total_dur > 0 else 0.0
        self.assertGreater(rate, 0.0, "a real speech sample must produce at least some events")
        import math
        log_r = math.log10(rate)
        self.assertLess(abs(log_r - math.log10(5.0)), abs(log_r - math.log10(100.0)),
                         f"event rate {rate:.3f}/s is closer to the 100/s ceiling than the 5/s floor -- "
                         f"the EVENT rule's parameters (prominence/gap) must be refused per the brief's own T7 gate")


if __name__ == "__main__":
    unittest.main()
