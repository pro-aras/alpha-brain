# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 15:57 +0400 — PREREG-S1B1R §2 / AMENDMENT 1 §4 (c): the run root is FRESH
# (/data/dev/brain-runs/scene-s1b1r); S1b-1's root is READ only (plain files: the identity test and S1b-1's report). Two
# TEST SETS per world seed share ONE training cache: S1b-1's own (2026120x, at S1b-1's own relative paths, so the identity
# test compares like with like) and the FRESH one (2026140x, under <root>/<ws>/fresh/, with SPEAK2). Test-first: red on
# 7706371 (no test sets there).
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from brain.scene import cache as C
from brain.scene import world as W

TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))


class TestRoots(unittest.TestCase):
    def test_this_slice_writes_its_own_root_and_reads_s1b1s(self) -> None:
        # edit: Claude (Fable 5.1, the seat), 2026-09-28 20:49 +0400 — the organ tree's fresh root; S1b-1R's root is now the record
        # edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:24 +0400 — F-M6 changed WORLD_CODE: the tree's root is FRESH again
        self.assertEqual(C.HEAR_RUNS, Path("/data/dev/brain-runs/scene-organ-hear"))   # PREREG-BRAIN-DRIVES §8 (14), 2026-09-29 16:40 +0400
        # edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 15:39 +0400 — PREREG-INNER-1 (the landing): the tree's root is FRESH again
        self.assertEqual(C.DRIVE_RUNS, Path("/data/dev/brain-runs/scene-organ-drive"))
        # edit: Kimi K3 (kimi-code, builder lane kimi-w1, integrator hat), 2026-10-05 00:27 +0400 — PREREG-W1 + PREREG-SLEEP-IDLE (the
        # seat's ONE shared pinned window): the tree's root is FRESH again; the swarm-1003 root stays named, read as plain files only.
        self.assertEqual(C.INNER_RUNS, Path("/data/dev/brain-runs/scene-organ-swarm-1003"))
        # edit: Kimi K3 (kimi-code, acting seat), 2026-10-09 12:0x +0400 — PREREG-ALPHA-6 (the landing): the tree's root is FRESH
        # again; the swarm-1005 root stays named, read as plain files only (the window's own choreography, the 4 precedents above).
        self.assertEqual(C.SWARM1005_RUNS, Path("/data/dev/brain-runs/scene-organ-swarm-1005"))
  # edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 20:3x +0400 — PREREG-BRAIN-LONG-6 §1.2
  # (the law SIGNED; SEAT-LINE sha256 2c6bb22b…): the pin gains the law's declared content (the scene world
  # lawful at the life's seed 20261211; the 10-09 launch-verdict item repaired) — the pin working, caught at
  # the launch gate's first full run and updated under the law, never loosened.
        self.assertEqual(C.RUNS, Path("/data/dev/brain-runs/scene-organ-h0"))  # the H0 window (PREREG-HOMEOSTASIS §6, SIGNED 2026-10-12): the live root moves (the bl6 root stays, read as plain files only — C.BL6_RUNS)
        self.assertEqual(C.FM6_RUNS, Path("/data/dev/brain-runs/scene-organ-fm6"))
        self.assertEqual(C.SCENE_ORGAN_RUNS, Path("/data/dev/brain-runs/scene-organ"))
        self.assertEqual(C.S1B1R_RUNS, Path("/data/dev/brain-runs/scene-s1b1r"))
        self.assertEqual(C.S1B1_RUNS, Path("/data/dev/brain-runs/scene-s1b1"))
        self.assertEqual(C.S1A_RUNS, Path("/data/dev/brain-runs/scene"))


class TestTestSets(unittest.TestCase):
    def test_paths(self) -> None:
        r = Path("/x")
        self.assertEqual(C.cache_dir(r, 20261101, "train"), r / "20261101" / "cache" / "train")
        self.assertEqual(C.cache_dir(r, 20261101, "train", "fresh"), r / "20261101" / "cache" / "train")   # ONE train cache
        self.assertEqual(C.cache_dir(r, 20261101, "speak"), r / "20261101" / "cache" / "speak")            # S1b-1's layout
        self.assertEqual(C.cache_dir(r, 20261101, "speak", "fresh"), r / "20261101" / "fresh" / "cache" / "speak")
        self.assertEqual(C.cache_dir(r, 20261101, "speak2", "fresh"), r / "20261101" / "fresh" / "cache" / "speak2")
        self.assertEqual(C.cache_dir(r, None, "toy-train", "fresh"), r / "toy" / "cache" / "toy-train")

    def test_seeds_and_splits(self) -> None:
        self.assertEqual(C.split_seed("train", 20261102, "fresh"), 20261102)
        self.assertEqual(C.split_seed("test", 20261102), 20261202)
        self.assertEqual(C.split_seed("test", 20261102, "fresh"), 20261402)
        self.assertEqual(C.split_seed("speak2", 20261103, "fresh"), 20261403)
        self.assertEqual(C.test_splits("s1b1"), C.TEST_SPLITS)
        self.assertEqual(C.test_splits("fresh"), C.TEST_SPLITS + ("speak2",))
        with self.assertRaises(C.SceneCacheError):
            C.split_seed("speak2", 20261101)                                    # SPEAK2 exists only in the fresh set
        with self.assertRaises(C.SceneCacheError):
            C.test_splits("nonsense")

    def test_a_fresh_speak2_cache_builds_and_reads(self) -> None:
        TMP.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=str(TMP), prefix="scene-s1b1r-cache-") as td:
            root = Path(td)
            d = C.cache_dir(root, 20261101, "speak2", "fresh")
            sh = C.build("speak2", 20261101, d, limit=3, recheck_n=1, tset="fresh")
            self.assertEqual((sh["seed"], sh["rows"], sh["test_set"]), (20261401, 3, "fresh"))
            p = C.ScenePercepts(d)
            truth = C.load_truth(d)
            self.assertEqual([r["item_id"] for r in truth], [W.speak2_scene(20261401, i).item_id for i in range(3)])
            for r in truth:
                self.assertEqual(len(r["things"]), 3)
                self.assertEqual(p.forced(r["row"]).shape, (3, 144))


if __name__ == "__main__":
    unittest.main()
