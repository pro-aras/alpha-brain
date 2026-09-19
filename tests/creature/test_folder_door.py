# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 02:12 +0400 — A12 test: the folder door (PREREG §11.3).
# A temp world dir with two pictures publishes ear-then-eye rows (source "folder"); after a restart
# (a fresh Body on the same root), the SAME pictures are never re-published.
from __future__ import annotations

import shutil
import tempfile
import time
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.body import Body
from creature.tape import read_tape

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"


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


if __name__ == "__main__":
    unittest.main()
