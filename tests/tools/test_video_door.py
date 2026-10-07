# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-07 — PREREG-OPEN-WORLD-1 §2/§3 build (the law signed at f682314)
"""tests/tools/test_video_door.py — the gates of PREREG-OPEN-WORLD-1 §3 on tools/worlds/video_door.py (§2's build).

Fixtures are synthesized by ffmpeg itself, deterministic, no network: a 12 s video = 6 s `testsrc2` + 6 s solid
crimson (one true scene cut at t=6), and a hand-written captions.srt whose words are known by construction
(including digits/symbol tokens that must be dropped AND COUNTED, and a >8-letter word that must truncate to the
ear's own WORD_SLOTS form, creature/senses/read_common.py:59's rule). Written FIRST, run RED before
tools/worlds/video_door.py existed.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.worlds import video_door as VD

ROOT = Path(__file__).resolve().parents[2]
GENOME_SRC = Path("/data/dev/genome-wt-mouthcap/scratch/bl2/GENOME.genome")   # the bench's genome — COPIED, never written
DATE = "2026-10-07"                                                            # pinned: two conversions must be byte-identical

SRT = """1
00:00:00,500 --> 00:00:02,000
Red apple, red apple!

2
00:00:03,000 --> 00:00:05,000
The strawberry is round.

3
00:00:06,500 --> 00:00:09,000
One two 1 2 3!

4
00:00:10,000 --> 00:00:11,500
Red apple.

5
00:00:11,500 --> 00:00:11,900
Bye bye!
"""

VTT = """WEBVTT

00:00.500 --> 00:02.000
Red apple, red apple!

00:03.000 --> 00:05.000
The strawberry is round.

00:06.500 --> 00:09.000
One two 1 2 3!

00:10.000 --> 00:11.500
Red apple.

00:11.500 --> 00:11.900
Bye bye!
"""

# the SRT's own truth: cue -> (kept words, dropped non-words)
KEPT_WORDS = ["red", "apple", "red", "apple", "the", "strawber", "is", "round", "one", "two", "red", "apple"]
LATE_WORDS = ["bye", "bye"]            # cue 5 starts at 11.5 s, past the last sampled frame (t=11) — dropped and COUNTED
DROPPED_NONWORD = 3                    # the "1 2 3" tokens of cue 3
SEG_BOUNDARIES = 4                     # apple|red, apple|the, apple|bye at TP 1/3 and bye|bye at TP 1/2 — median TP 1.0, MAD 0


def _run(cmd: list, **kw) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise AssertionError(f"{cmd[:3]}… exit {p.returncode}: {p.stderr[-800:]}")
    return p


def _make_video(path: Path) -> None:
    _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
          "-f", "lavfi", "-i", "testsrc2=duration=6:size=160x90:rate=10",
          "-f", "lavfi", "-i", "color=crimson:size=160x90:rate=10:duration=6",
          "-filter_complex", "[0:v][1:v]concat=n=2:v=1[out]", "-map", "[out]",
          "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(path)])


def _dir_digest(d: Path) -> str:
    h = hashlib.sha256()
    files = sorted(p for p in d.rglob("*") if p.is_file())
    for p in files:
        h.update(str(p.relative_to(d)).encode())
        h.update(p.read_bytes())
    return h.hexdigest(), files


def _rows(tape_dir: Path) -> list:
    days = sorted(tape_dir.glob("*.jsonl"))
    assert len(days) == 1, f"one day file, got {days}"
    return [json.loads(l) for l in days[0].read_text().splitlines() if l.strip()], days[0]


class Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="video-door-test-"))
        cls.video = cls.tmp / "lesson.mp4"
        cls.srt = cls.tmp / "captions.srt"
        cls.vtt = cls.tmp / "captions.vtt"
        _make_video(cls.video)
        cls.srt.write_text(SRT)
        cls.vtt.write_text(VTT)
        # the plant: one byte flipped mid-file; decode stays clean (verified at fixture build), the sha changes
        raw = bytearray(cls.video.read_bytes())
        raw[len(raw) // 2] ^= 0x01
        cls.bad_video = cls.tmp / "lesson_corrupt.mp4"
        cls.bad_video.write_bytes(raw)
        _run(["ffmpeg", "-hide_banner", "-v", "error", "-i", str(cls.bad_video), "-f", "null", "-"])

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def convert(self, name: str, video: Path = None) -> Path:
        out = self.tmp / name
        VD.convert(video or self.video, self.srt, out, date=DATE)
        return out


class CaptionsParse(Fixture):
    def test_srt_and_vtt_parse_to_the_same_cues(self) -> None:
        a, b = VD.parse_captions(self.srt), VD.parse_captions(self.vtt)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 5)
        self.assertEqual(a[0], {"start": 0.5, "duration": 1.5, "text": "Red apple, red apple!"})

    def test_word_form_is_the_organisms_own(self) -> None:
        toks, dropped = VD.caption_tokens(VD.parse_captions(self.srt))
        self.assertEqual([t["word"] for t in toks], KEPT_WORDS + LATE_WORDS)
        self.assertEqual(dropped, DROPPED_NONWORD)                       # digits/symbols dropped AND counted
        self.assertIn("strawber", [t["word"] for t in toks])             # truncated to the ear's own 8 letters


class EyeRows(Fixture):
    def test_eye_rows_parse_sha_and_canvas(self) -> None:
        out = self.convert("tape-a")
        rows, day = _rows(out)
        self.assertEqual(day.name, f"{DATE}.jsonl")                      # the conversion date's day file (the law §2.3)
        self.assertEqual([r["seq"] for r in rows], list(range(1, len(rows) + 1)))
        eyes = [r for r in rows if r["sense"] == "eye"]
        self.assertEqual(len(eyes), 12)                                  # 1 Hz over [0,6) and [6,12)
        for r in rows:
            self.assertEqual(set(r), {"seq", "at", "sense", "sha", "payload", "meta"})
            self.assertTrue(r["at"].startswith(DATE))
        for r in eyes:
            payload = out / r["payload"]
            self.assertTrue(payload.is_file())
            self.assertEqual(hashlib.sha256(payload.read_bytes()).hexdigest(), r["sha"])
            im = Image.open(io.BytesIO(payload.read_bytes()))
            self.assertEqual((im.size, im.mode), ((128, 128), "RGB"))    # the eye's own canvas form
        moments = [r["meta"]["moment"] for r in eyes]
        self.assertEqual(len(set(moments)), 12)
        self.assertTrue(all(r["meta"]["source"] == "video" for r in eyes))


class EarRows(Fixture):
    def test_words_meta_drops_and_the_order_law(self) -> None:
        out = self.convert("tape-b")
        rows, _ = _rows(out)
        ears = [r for r in rows if r["sense"] == "ear"]
        self.assertEqual([r["meta"]["word"] for r in ears], KEPT_WORDS)  # the SRT's known words, the tape's own form
        for r in ears:
            m = r["meta"]
            self.assertEqual(m["source"], "video-caption")
            self.assertEqual(m["track_kind"], "authored")
            self.assertIsInstance(m["start"], float)
            self.assertIsInstance(m["duration"], float)
            self.assertEqual((out / r["payload"]).read_bytes(), m["word"].encode())
        eye_seq_of_moment = {r["meta"]["moment"]: r["seq"] for r in rows if r["sense"] == "eye"}
        for r in ears:                                                   # PREREG §2.2's order law: the ear row precedes
            self.assertIn(r["meta"]["moment"], eye_seq_of_moment)        # the eye row of its own moment
            self.assertLess(r["seq"], eye_seq_of_moment[r["meta"]["moment"]])
        rec = json.loads((out / "record.json").read_text())
        self.assertEqual(rec["stats"]["dropped_nonword"], DROPPED_NONWORD)   # planted non-words: dropped and COUNTED
        self.assertEqual(rec["stats"]["dropped_late"], 2)                    # cue 5's two words past the last frame
        self.assertEqual(rec["stats"]["caption_tokens"], len(KEPT_WORDS) + DROPPED_NONWORD + len(LATE_WORDS))


class Identity(Fixture):
    def test_g_identity_two_conversions_byte_identical(self) -> None:
        a = self.convert("tape-c1")
        b = self.convert("tape-c2")
        da, fa = _dir_digest(a)
        db, fb = _dir_digest(b)
        self.assertEqual([str(p.relative_to(a)) for p in fa], [str(p.relative_to(b)) for p in fb])
        self.assertEqual(da, db)                                         # every file byte-identical


class Plant(Fixture):
    def test_g_plant_one_flipped_byte_is_caught(self) -> None:
        good = self.convert("tape-d1")
        bad = self.convert("tape-d2", video=self.bad_video)
        self.assertNotEqual(_dir_digest(good)[0], _dir_digest(bad)[0])   # the tape's hash changes
        self.assertEqual(VD.verify(good, video=self.video, captions=self.srt), 0)
        self.assertNotEqual(VD.verify(good, video=self.bad_video, captions=self.srt), 0)   # the tool refuses/flags
        # the payload sha table's own road: tamper one payload byte of an honest tape and verify must catch it
        payload = sorted((good / "payload").iterdir())[3]
        raw = bytearray(payload.read_bytes())
        raw[0] ^= 0x01
        payload.write_bytes(raw)
        self.assertNotEqual(VD.verify(good, video=self.video, captions=self.srt), 0)


class TpDip(unittest.TestCase):
    def test_planted_units_internal_boundaries_never_cut(self) -> None:
        units = [["ba", "be", "bo"], ["da", "de", "do"], ["ga", "ge", "go"]]
        seq = [u for u in units for _ in range(40)]
        random.Random(7).shuffle(seq)                                    # deterministic interleave
        tokens = [s for u in seq for s in u]
        d = VD.tp_dips(tokens)
        self.assertEqual(d["median"], 1.0)                               # internal TPs dominate -> median 1.0
        self.assertEqual(d["mad"], 0.0)                                  # the strict-dip edge case, pinned
        cuts = set(d["boundaries"])                                      # a boundary AFTER token i
        unit_bounds = {i for i in range(len(tokens) - 1) if (i + 1) % 3 == 0}
        internal = {i for i in range(len(tokens) - 1) if (i + 1) % 3 != 0}
        self.assertTrue(unit_bounds <= cuts)                             # every boundary between units IS cut
        self.assertFalse(cuts & internal)                                # no internal boundary is ever cut

    def test_degenerate_streams(self) -> None:
        self.assertEqual(VD.tp_dips([])["boundaries"], [])
        self.assertEqual(VD.tp_dips(["alone"])["boundaries"], [])


class Cli(Fixture):
    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        env = dict(os.environ, PYTHONPATH=str(ROOT))
        return _run([sys.executable, "-B", "-m", "tools.worlds.video_door", *args], cwd=ROOT, env=env)

    def test_convert_segment_verify(self) -> None:
        out = self.tmp / "tape-cli"
        self._cli("convert", "--video", str(self.video), "--captions", str(self.srt), "--out", str(out), "--date", DATE)
        self.assertTrue((out / f"{DATE}.jsonl").is_file())
        p = self._cli("segment", "--captions", str(self.srt))
        self.assertEqual(p.stdout.count("boundary"), SEG_BOUNDARIES)     # known by construction on the SRT's own stream
        p = self._cli("verify", "--tape", str(out), "--video", str(self.video), "--captions", str(self.srt))
        self.assertIn("VERIFY OK", p.stdout)
        p = subprocess.run([sys.executable, "-B", "-m", "tools.worlds.video_door", "verify", "--tape", str(out),
                            "--video", str(self.bad_video), "--captions", str(self.srt)],
                           capture_output=True, text=True, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT)))
        self.assertNotEqual(p.returncode, 0)                             # the converter's own check refuses
        self.assertIn("VERIFY FAIL", p.stdout)


class ReplaySmoke(Fixture):
    def test_g_format_the_replays_own_reader_zero_special_casing(self) -> None:
        from creature.replay import run_replay
        out = self.convert("tape-f")
        work = self.tmp / "replay"
        work.mkdir()
        genome = work / "GENOME.genome"
        shutil.copy(GENOME_SRC, genome)                                  # the bench's genome, COPIED into the work area
        journal = run_replay(genome, out, work / "out")                  # creature/replay.py unchanged, as-is
        rows = [json.loads(l) for l in journal.read_text().splitlines() if l.strip()]
        self.assertGreater(len(rows), 0)                                 # a journal, no exception, no special-casing
        print(f"replay smoke: {len(rows)} journal rows over {len(_rows(out)[0])} tape rows")


if __name__ == "__main__":
    unittest.main()
