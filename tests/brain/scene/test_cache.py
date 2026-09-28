# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:06 +0400 — S1a step 2 (brief: «A per-seed glance cache is written once and
# shared by every arm»): a small real cache built through brain.glance_cache's own writer; ONE genome.gaze.glances call
# per scene (+ the self-check's fresh re-glances, counted); the sidecars align row for row; a cache is written once;
# no test canvas's sha may appear in training (a planted duplicate is caught).
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from brain.scene import PREREG_SHA256, cache, eye
from brain.scene import world as W

TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))


class TestSceneCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TMP.mkdir(parents=True, exist_ok=True)
        cls._td = tempfile.TemporaryDirectory(dir=str(TMP), prefix="scene-cache-test-")
        cls.dir = Path(cls._td.name) / "stage"
        calls = {"n": 0}
        real = eye.G.glances

        def counting(*a, **k):
            calls["n"] += 1
            return real(*a, **k)

        with mock.patch.object(eye.G, "glances", side_effect=counting):
            cls.header = cache.build("stage", None, cls.dir, limit=12, recheck_n=4)
        cls.calls = calls["n"]

    @classmethod
    def tearDownClass(cls) -> None:
        cls._td.cleanup()

    def test_one_glances_call_per_scene_plus_the_self_check(self) -> None:
        self.assertEqual(self.header["rows"], 12)
        self.assertEqual(len(self.header["self_check_rows"]), 4)
        self.assertEqual(self.calls, 12 + 4)

    def test_sidecars_align(self) -> None:
        p = cache.ScenePercepts(self.dir)
        truth = cache.load_truth(self.dir)
        scenes = W.scenes_for("stage", W.STAGE_SEED)[:12]
        self.assertEqual(len(p), 12)
        self.assertEqual(len(truth), 12)
        for r, s in enumerate(scenes):
            self.assertEqual(p.glances.meta(r)["item_id"], s.item_id)
            self.assertEqual(truth[r]["item_id"], s.item_id)
            self.assertEqual(p.forced(r).shape, (len(s.things), 144))
            fix, loc = p.located(r)
            self.assertEqual(len(fix), int(p.n_fix[r]))
            self.assertEqual([tuple(x) for x in truth[r]["fix"]], fix)
            self.assertEqual(len(truth[r]["fix_thing"]), len(fix))
            self.assertEqual(p.words(r), [])
            hs = p.hypotheses(r)
            self.assertEqual(sum(h.count for h in hs), len(fix))

    def test_headers(self) -> None:
        sh = json.loads((self.dir / "scene_header.json").read_text())
        self.assertEqual(sh["prereg_sha256"], PREREG_SHA256)
        self.assertEqual(sh["seed"], W.STAGE_SEED)
        self.assertEqual(sh["glance_header"]["row_count"], 12)
        self.assertEqual(len(sh["glance_header"]["organ_pins"]), 4)
        for name in ("glances.npy", "index.jsonl", "header.json", "percept.npz", "forced.npz", "hear.jsonl", "truth.jsonl"):
            self.assertIn(name, sh["files"])

    def test_written_once(self) -> None:
        with self.assertRaises(cache.SceneCacheError):
            cache.build("stage", None, self.dir, limit=2)


class TestDisjoint(unittest.TestCase):
    def test_planted_duplicate_is_caught(self) -> None:
        self.assertEqual(cache.assert_disjoint(["a", "b"], ["c", "d"]), 2)
        with self.assertRaises(cache.SceneCacheError):
            cache.assert_disjoint(["a", "b", "c"], ["x", "b"])

    def test_real_caches_when_present(self) -> None:
        """On the real per-seed caches (when built): every test / m2b / m6 canvas sha is absent from training."""
        found = 0
        for ws in W.WORLD_SEEDS:
            tr = cache.cache_dir(cache.RUNS, ws, "train")
            if not tr.exists():
                continue
            shas = cache.ScenePercepts(tr).shas()
            self.assertEqual(len(shas), 10000)
            for split in ("test", "m2b", "m6"):
                d = cache.cache_dir(cache.RUNS, ws, split)
                self.assertTrue(d.exists(), d)
                cache.assert_disjoint(shas, cache.ScenePercepts(d).shas())
                found += 1
        if not found:
            self.skipTest("no per-seed cache built on this box yet")


if __name__ == "__main__":
    unittest.main()
