# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 02:12 +0400 — A12 test: the folder door (PREREG §11.3).
# A temp world dir with two pictures publishes ear-then-eye rows (source "folder"); after a restart
# (a fresh Body on the same root), the SAME pictures are never re-published.
# edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 12:4x +0400 — C2 (docs/G4-WAVE3-CLAUSES.md W3-6 step 4;
# PREREG §17): pacing (at most one new picture per scan, deterministic bytewise order) and the sight-only
# road (a loose picture under world/, or under a non-word folder, is eye-only, meta.word absent, and the
# mind journals "word": null for it once FAST is declared).
from __future__ import annotations

import json
import shutil
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image

from creature.body import Body
from creature.mind import Mind
from creature.tape import read_tape

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"
WAVE2_GENOME = Path(__file__).resolve().parents[2] / "tests" / "creature" / "G4-wave2-test.genome"


def _write_pictures(world_dir: Path) -> None:
    d = world_dir / "circle"
    d.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(1)
    for name, color in (("pic1.png", (200, 30, 30)), ("pic2.png", (30, 30, 200))):
        arr = np.zeros((64, 64, 3), dtype=np.uint8)
        arr[:, :] = color
        arr[16:48, 16:48] += rng.integers(0, 20, size=(32, 32, 3), dtype=np.uint8)   # a little texture, still deterministic per-seed
        Image.fromarray(arr, mode="RGB").save(d / name, format="PNG")


def _folder_rows(root: Path):
    return [r for r in read_tape(root) if r.get("meta", {}).get("source") == "folder"]


class TestFolderDoor(unittest.TestCase):
    def test_two_pictures_published_and_never_republished_after_restart(self) -> None:
        root = Path(tempfile.mkdtemp())
        world_dir = Path(tempfile.mkdtemp())
        _write_pictures(world_dir)

        body = Body(root, GENOME_PATH)
        folder_sense = None
        from creature.senses import folder as folder_mod
        import functools
        fn = functools.partial(folder_mod.sense, world_dir=world_dir, root=root, canvas=128, period=0.1)
        folder_sense = body.add_sense("folder", fn)
        body.start()
        try:
            deadline = time.time() + 15.0
            while len(_folder_rows(root)) < 4 and time.time() < deadline:
                time.sleep(0.2)
        finally:
            body.stop()

        rows1 = _folder_rows(root)
        self.assertEqual(len(rows1), 4, f"expected 2 pictures x (ear,eye) = 4 rows, got {len(rows1)}")
        ear1 = [r for r in rows1 if r["sense"] == "ear"]
        eye1 = [r for r in rows1 if r["sense"] == "eye"]
        self.assertEqual(len(ear1), 2); self.assertEqual(len(eye1), 2)
        for r in ear1:
            self.assertEqual(r["meta"]["word"], "circle")
            self.assertTrue(r["meta"]["moment"].startswith("f"))
        moments = {r["meta"]["moment"] for r in rows1}
        self.assertEqual(len(moments), 2, "two distinct pictures must get two distinct moment ids")
        for m in moments:
            self.assertEqual(sum(1 for r in rows1 if r["meta"]["moment"] == m and r["sense"] == "ear"), 1)
            self.assertEqual(sum(1 for r in rows1 if r["meta"]["moment"] == m and r["sense"] == "eye"), 1)
        # order law: ear precedes eye for each moment
        by_moment = {}
        for r in rows1:
            by_moment.setdefault(r["meta"]["moment"], {})[r["sense"]] = r["seq"]
        for m, d in by_moment.items():
            self.assertLess(d["ear"], d["eye"])

        self.assertTrue((root / "folder" / "SEEN.json").exists())

        # restart: a fresh Body on the SAME root, same world dir -- must not re-publish
        body2 = Body(root, GENOME_PATH)
        fn2 = functools.partial(folder_mod.sense, world_dir=world_dir, root=root, canvas=128, period=0.1)
        body2.add_sense("folder", fn2)
        body2.start()
        time.sleep(2.0)
        body2.stop()

        rows2 = _folder_rows(root)
        self.assertEqual(len(rows2), 4, "a restart must never re-publish already-seen pictures")

        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(world_dir, ignore_errors=True)


def _write_pacing_world(world_dir: Path) -> list:
    """3 word-folders x 2 pictures each, deterministic content -- returns the (folder, filename) pairs in
    the BYTEWISE (folder, filename) order C2's pacing rule must publish them in."""
    folders = ["alpha", "beta", "gamma"]
    names = ["pic1.png", "pic2.png"]
    rng = np.random.default_rng(3)
    expected = []
    for f in folders:
        d = world_dir / f
        d.mkdir(parents=True, exist_ok=True)
        for n in names:
            arr = np.zeros((64, 64, 3), dtype=np.uint8)
            arr[:, :] = rng.integers(0, 255, size=3, dtype=np.uint8)
            arr[16:48, 16:48] += rng.integers(0, 20, size=(32, 32, 3), dtype=np.uint8)
            Image.fromarray(arr, mode="RGB").save(d / n, format="PNG")
            expected.append((f, n))
    expected.sort()
    return expected


class TestFolderDoorPacing(unittest.TestCase):
    def test_one_picture_per_scan_in_bytewise_order_and_never_repeated_after_restart(self) -> None:
        root = Path(tempfile.mkdtemp())
        world_dir = Path(tempfile.mkdtemp())
        expected_order = _write_pacing_world(world_dir)
        self.assertEqual(len(expected_order), 6)
        period = 0.2

        from creature.senses import folder as folder_mod
        import functools
        body = Body(root, GENOME_PATH)
        fn = functools.partial(folder_mod.sense, world_dir=world_dir, root=root, canvas=64, period=period)
        body.add_sense("folder", fn)
        body.start()
        try:
            deadline = time.time() + 20.0
            while len(_folder_rows(root)) < 12 and time.time() < deadline:
                time.sleep(0.1)
        finally:
            body.stop()

        rows = _folder_rows(root)
        self.assertEqual(len(rows), 12, f"6 pictures x (ear,eye) = 12 rows, got {len(rows)}")

        def _at(row):
            return datetime.fromisoformat(row["at"].replace("Z", "+00:00"))

        elapsed = (_at(rows[-1]) - _at(rows[0])).total_seconds()
        self.assertGreaterEqual(elapsed, 3 * period,
                                 f"6 pictures at ONE per {period}s scan must span >= {3 * period}s (paced), spanned {elapsed}s")

        ear_words_in_order = [r["meta"]["word"] for r in rows if r["sense"] == "ear"]
        self.assertEqual(ear_words_in_order, [f for f, _n in expected_order],
                          "pictures must publish in deterministic (folder, filename) bytewise order")

        # restart: a fresh Body on the SAME root, same world dir -- must not re-publish
        body2 = Body(root, GENOME_PATH)
        fn2 = functools.partial(folder_mod.sense, world_dir=world_dir, root=root, canvas=64, period=period)
        body2.add_sense("folder", fn2)
        body2.start()
        time.sleep(1.0)
        body2.stop()
        self.assertEqual(len(_folder_rows(root)), 12, "a restart must never re-publish already-seen pictures")

        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(world_dir, ignore_errors=True)


class TestFolderDoorSightOnly(unittest.TestCase):
    def test_loose_picture_under_world_is_eye_only_and_journals_word_null(self) -> None:
        """Publishes through a bare Tape + the real folder.sense (never through Body -- Body's own live
        Mind, always started on GENOME_PATH which has no FAST, would ALSO consume the row and write its
        OWN "sight_only": true journal row into the SAME journal file, double-counting canvas_rows below).
        Then a SEPARATE Mind (FAST declared -- PREREG §11.1 step 2) replays the tape to journal the word:
        null row this toy is about."""
        import threading
        from creature.senses import folder as folder_mod
        from creature.tape import Tape

        root = Path(tempfile.mkdtemp())
        world_dir = Path(tempfile.mkdtemp())
        world_dir.mkdir(parents=True, exist_ok=True)
        arr = np.zeros((64, 64, 3), dtype=np.uint8)
        arr[:, :] = (10, 200, 10)
        rng = np.random.default_rng(9)
        arr[16:48, 16:48] += rng.integers(0, 20, size=(32, 32, 3), dtype=np.uint8)
        Image.fromarray(arr, mode="RGB").save(world_dir / "loose.png", format="PNG")

        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: folder_mod.sense(
            tape.publish, stop_event, world_dir=world_dir, root=root, canvas=128, period=0.1), daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while len(_folder_rows(root)) < 1 and time.time() < deadline:
            time.sleep(0.1)
        time.sleep(0.5)   # a couple more scans must find nothing new to publish
        stop_event.set()
        t.join(timeout=5.0)

        rows = _folder_rows(root)
        self.assertEqual(len(rows), 1, f"a loose sight-only picture must publish EYE ONLY, got {rows}")
        self.assertEqual(rows[0]["sense"], "eye")
        self.assertNotIn("word", rows[0]["meta"])

        mind = Mind(WAVE2_GENOME, root)
        for row in read_tape(root):
            mind.consume(row)
        journal_files = sorted((root / "journal").glob("*.jsonl"))
        self.assertEqual(len(journal_files), 1)
        journal_rows = [json.loads(l) for l in journal_files[0].read_text().splitlines() if l.strip()]
        canvas_rows = [r for r in journal_rows if "event" not in r and "sleep" not in r]
        self.assertEqual(len(canvas_rows), 1)
        self.assertIn("word", canvas_rows[0])
        self.assertIsNone(canvas_rows[0]["word"])

        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(world_dir, ignore_errors=True)

    def test_picture_under_non_word_folder_is_also_sight_only(self) -> None:
        root = Path(tempfile.mkdtemp())
        world_dir = Path(tempfile.mkdtemp())
        d = world_dir / "_unnamed"      # WORD_RE ([a-z]{1,8}) fails on this name -- leading underscore
        d.mkdir(parents=True, exist_ok=True)
        arr = np.zeros((64, 64, 3), dtype=np.uint8)
        arr[:, :] = (5, 5, 200)
        rng = np.random.default_rng(13)
        arr[16:48, 16:48] += rng.integers(0, 20, size=(32, 32, 3), dtype=np.uint8)
        Image.fromarray(arr, mode="RGB").save(d / "pic.png", format="PNG")

        from creature.senses import folder as folder_mod
        import functools
        body = Body(root, GENOME_PATH)
        fn = functools.partial(folder_mod.sense, world_dir=world_dir, root=root, canvas=128, period=0.1)
        body.add_sense("folder", fn)
        body.start()
        try:
            deadline = time.time() + 10.0
            while len(_folder_rows(root)) < 1 and time.time() < deadline:
                time.sleep(0.1)
            time.sleep(0.5)
        finally:
            body.stop()

        rows = _folder_rows(root)
        self.assertEqual(len(rows), 1, f"a picture under a non-word folder must publish EYE ONLY, got {rows}")
        self.assertEqual(rows[0]["sense"], "eye")
        self.assertNotIn("word", rows[0]["meta"])
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(world_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
