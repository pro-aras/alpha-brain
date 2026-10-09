# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-09 04:36 +0400 — PREREG-ALPHA-6 §2 B2/B3 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…; test-first): the video world's arming in creature/body.py and the body's opt-in
# `--eye-front` pass-through (V2's declared parameter, creature/replay.py:276-283's form mirrored — absent =
# byte-identical).
"""tests/creature/test_video_arming.py — the body wiring of PREREG-ALPHA-6: WORLD_VIDEO's arming (the scene
door's own shape) and `--eye-front` into a LIFE's runner.

The integration pins run REAL bodies (subprocess, genome/G4-skeleton.genome + the one video line, the toy
shelf of tests/creature/_video_shelf.py): the video rows flow onto the life's tape with their provenance
untouched, the mind consumes them (moments move), STATUS carries the "video" key; and with --eye-front the
journal's canvas rows carry V2's `front` key while the unwired twin carries NONE."""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from creature import body as B
from creature.senses import video as video_sense
from genome.machinery import parse_genome
from tests.creature import _video_shelf as F

REPO = Path(__file__).resolve().parents[2]
SKELETON = (REPO / "genome" / "G4-skeleton.genome").read_text()


def _genome_with_video(shelf: Path, every_s: int = 1) -> str:
    return SKELETON + f"\nWORLD    video shelf {shelf} every {every_s} s; loop; manifest sha256\n"


class DeclaredVideoConfig(unittest.TestCase):
    def test_undeclared_arms_nothing(self) -> None:
        self.assertIsNone(B._declared_video_config({}))

    def test_declared_returns_its_own_dict(self) -> None:
        cfg = {"shelf": "/x", "every_s": 2, "loop": True, "manifest": "sha256"}
        self.assertEqual(B._declared_video_config({"WORLD_VIDEO": cfg}), cfg)

    def test_gated_on_the_module_constant(self) -> None:
        self.assertTrue(video_sense.VIDEO_DOOR_GATED,
                        "the gate must be True for _declared_video_config to return anything")

    def test_the_registry_names_its_call_sites(self) -> None:
        from creature import genes
        d = parse_genome(_genome_with_video(Path("/x"))).declared
        self.assertIn("WORLD_VIDEO", d)
        self.assertEqual(genes.unwired(d), [])

    def test_body_carries_no_front_and_no_video_progress_by_default(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="video-arming-"))
        try:
            gp = tmp / "g.genome"
            gp.write_text(SKELETON)
            b = B.Body(tmp / "root", gp)
            self.assertIsNone(b.eye_front)
            self.assertIsNone(b.video_progress)
            marker = object()
            b2 = B.Body(tmp / "root2", gp, eye_front=marker)
            self.assertIs(b2.eye_front, marker)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class _BodyRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="video-body-"))
        cls.shelf = cls.tmp / "shelf"
        F.build_toy_tape(cls.shelf)
        video_sense.write_manifest(cls.shelf)
        cls.genome = cls.tmp / "g.genome"
        cls.genome.write_text(_genome_with_video(cls.shelf))

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def _run(cls, name: str, extra=(), seconds: float = 5.0):
        root = cls.tmp / name
        env = dict(os.environ, PYTHONPATH=str(REPO))
        p = subprocess.Popen([sys.executable, "-B", "-m", "creature.body", "--root", str(root),
                              "--genome", str(cls.genome), "--no-maker", *extra],
                             cwd=REPO, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(seconds)
        p.send_signal(signal.SIGTERM)
        out, err = p.communicate(timeout=90)
        rows = []
        for f in sorted((root / "tape").glob("*.jsonl")):
            rows.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
        journal = []
        jdir = root / "journal"
        if jdir.exists():
            for f in sorted(jdir.glob("*.jsonl")):
                journal.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
        status = json.loads((root / "STATUS.json").read_text()) if (root / "STATUS.json").exists() else {}
        return p.returncode, rows, journal, status, err


class TheVideoWorldFlows(_BodyRun):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.rc, cls.rows, cls.journal, cls.status, cls.err = cls._run("plain")

    def test_the_body_lived_and_stopped_clean(self) -> None:
        self.assertEqual(self.rc, 0, self.err[-800:])

    def test_the_tape_carries_the_video_rows_with_their_provenance_untouched(self) -> None:
        eye = [r for r in self.rows if r["sense"] == "eye" and r["meta"].get("source") == "video"]
        ear = [r for r in self.rows if r["sense"] == "ear" and r["meta"].get("source") == "video-caption"]
        self.assertGreaterEqual(len(eye), 2, f"the presence count (rows: {len(self.rows)})")
        self.assertGreaterEqual(len(ear), 1)
        for r in eye + ear:
            self.assertEqual(r["meta"]["video"], "toy-song")       # the tape's `video` meta, carried untouched
            self.assertIn("moment", r["meta"])
        self.assertEqual(eye[0]["meta"]["t"], 0.0)
        self.assertEqual(ear[0]["meta"]["word"], "red")

    def test_the_mind_consumed_them(self) -> None:
        self.assertGreaterEqual(int(self.status.get("moments", 0)), 2, json.dumps(self.status)[:400])
        v = self.status.get("video") or {}
        self.assertGreaterEqual(v.get("published_canvases", 0), 2)
        self.assertIn("published_rows", v)
        self.assertIn("loop", v)
        self.assertFalse(v["ended"])

    def test_the_cursor_advanced(self) -> None:
        cur = json.loads((self.tmp / "plain" / "video" / "VIDEO-CURSOR").read_text())
        self.assertGreaterEqual(cur["row"] + cur["loop"], 2)


class TheFrontPassThrough(_BodyRun):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.rc, cls.rows, cls.journal, cls.status, cls.err = cls._run("wired", extra=("--eye-front",))
        cls.rc0, _r0, cls.journal0, _s0, cls.err0 = cls._run("unwired-twin")

    def test_the_wired_lifes_canvas_rows_carry_the_front_key(self) -> None:
        self.assertEqual(self.rc, 0, self.err[-800:])
        canvas = [r for r in self.journal if "cells" in r and "err" in r]     # the canvas rows (DELIVER-less genome: no "glance" key)
        self.assertGreaterEqual(len(canvas), 2, f"the presence count (journal rows: {len(self.journal)})")
        for r in canvas:
            self.assertIn("front", r)
            self.assertIn("t_mass", r["front"])
            self.assertIn("o", r["front"])

    def test_the_unwired_life_carries_no_front_key(self) -> None:
        self.assertEqual(self.rc0, 0, self.err0[-800:])
        canvas = [r for r in self.journal0 if "cells" in r and "err" in r]
        self.assertGreaterEqual(len(canvas), 2, "the presence count")
        self.assertEqual(sum("front" in r for r in canvas), 0)


if __name__ == "__main__":
    unittest.main()
