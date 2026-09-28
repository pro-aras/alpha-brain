# edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:22 +0400 — PREREG-BRAIN-IN-BODY AMENDMENT 1 §2 (sha 45abeca2…), test-first (red on
# brain-organ-fm6 1ab55f8): THE NEW TEST SET «held» — test seeds 20261501 / 02 / 03 for world seeds 20261101 / 02 / 03, every split
# drawn as on the fresh set (SPEAK2 included); M6 has 84 items on «held» and 42 on «fresh» and «s1b1»; item i < 42 is today's
# m6_scene(ts, i) byte for byte, i ≥ 42 follows the same rule on i − 42 (two things below 28, else three) from its OWN stream
# (scene:m6:<i>). Pinned against fixtures computed by the UNCHANGED code (tests/brain/scene/fixtures/*_pre_fm6.json).
"""tests/brain/scene/test_world_fm6.py — the «held» test set in world.py, cache.py and run.py (specs only; no pixels)."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from brain.scene import cache as C
from brain.scene import world as W

FIXD = Path(__file__).resolve().parent / "fixtures"
M6_OLD = json.loads((FIXD / "m6_scenes_pre_fm6.json").read_text())
WORLD_OLD = json.loads((FIXD / "world_pre_fm6.json").read_text())
HELD = {20261101: 20261501, 20261102: 20261502, 20261103: 20261503}
TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))


def _spec(s: W.Scene):
    """A scene's content without its seed / item id: the things (shape, colour, size, box) and the parent's words."""
    d = s.to_dict()
    return json.dumps({"things": d["things"], "words": d["words"]}, sort_keys=True)


class TestSeeds(unittest.TestCase):
    def test_the_held_set(self):
        self.assertEqual(W.HELD_TEST_SEEDS, HELD)
        self.assertEqual(W.TEST_SETS["held"], HELD)
        self.assertEqual(W.TEST_SETS["fresh"], W.FRESH_TEST_SEEDS)
        self.assertEqual(W.TEST_SETS["s1b1"], W.TEST_SEEDS)
        used = set(W.TEST_SEEDS.values()) | set(W.FRESH_TEST_SEEDS.values()) | set(W.WORLD_SEEDS)
        self.assertFalse(set(HELD.values()) & used)

    def test_sizes(self):
        self.assertEqual(W.split_size("m6"), 42)
        self.assertEqual(W.split_size("m6", "fresh"), 42)
        self.assertEqual(W.split_size("m6", "s1b1"), 42)
        self.assertEqual(W.split_size("m6", "held"), 84)
        for s in ("test", "m2b", "m3", "speak", "decline", "speak2"):
            self.assertEqual(W.split_size(s, "held"), W.split_size(s))
        self.assertEqual(len(W.scenes_for("m6", 20261502)), 84)
        self.assertEqual(len(W.scenes_for("m6", 20261402)), 42)
        self.assertEqual(len(W.scenes_for("m6", 20261202)), 42)
        with self.assertRaises(W.WorldError):
            W.m6_scene(20261402, 42)                  # the fresh and older sets keep 42
        with self.assertRaises(W.WorldError):
            W.m6_scene(20261502, 84)


class TestM6(unittest.TestCase):
    def test_items_below_42_are_todays_byte_for_byte(self):
        for ts in ("20261201", "20261401", "20261202", "20261402", "20261203", "20261403"):
            got = [W.m6_scene(int(ts), i).to_dict() for i in range(42)]
            self.assertEqual(json.loads(json.dumps(got)), M6_OLD["scenes"][ts], ts)
        for ts, old in WORLD_OLD["m6_held_seeds"].items():
            got = [W.m6_scene(int(ts), i).to_dict() for i in range(42)]
            self.assertEqual(json.loads(json.dumps(got)), old, ts)

    def test_the_84_mix_and_rule(self):
        for ts in HELD.values():
            sc = W.scenes_for("m6", ts)
            n = [len(s.things) for s in sc]
            self.assertEqual((n.count(2), n.count(3)), (56, 28))
            for i, s in enumerate(sc):
                self.assertEqual(s.index, i)
                self.assertEqual(len(s.things), 2 if (i % 42) < W.M6_TWO else 3)
                self.assertEqual(s.words, (W.DAX_WORD,))
                self.assertEqual(s.things[s.referent].shape, W.DAX_SHAPE)
            specs = [_spec(s) for s in sc]
            self.assertEqual(len(set(specs)), 84)       # item i ≥ 42 is drawn from its own stream, never a copy of i − 42


class TestNothingOldMoves(unittest.TestCase):
    def test_fresh_and_older_sets_every_split_sampled(self):
        for key, blk in WORLD_OLD["sample"].items():
            tset, split = key.split("/")
            ts = blk["test_seed"]
            self.assertEqual(W.split_size(split, tset), blk["n"], key)
            full = W.scenes_for(split, ts, tset=tset)
            self.assertEqual(len(full), blk["n"], key)
            for i, d in blk["scenes"].items():
                self.assertEqual(json.loads(json.dumps(full[int(i)].to_dict())), d, f"{key}[{i}]")


class TestDisjoint(unittest.TestCase):
    def test_held_specs_meet_no_old_set_and_no_training(self):
        for ws, ts in HELD.items():
            held = {_spec(s) for split in C.test_splits("held") for s in W.scenes_for(split, ts, tset="held")}
            old = {_spec(s) for tset in ("s1b1", "fresh") for split in C.test_splits(tset)
                   for s in W.scenes_for(split, W.TEST_SETS[tset][ws], tset=tset)}
            train = {_spec(s) for s in W.train_stream(ws, 3000)}
            self.assertFalse(held & old, ws)
            self.assertFalse(held & train, ws)


class TestCacheAndRun(unittest.TestCase):
    def test_cache_paths_seeds_and_splits(self):
        r = Path("/x")
        self.assertEqual(C.test_splits("held"), C.FRESH_SPLITS)
        self.assertEqual(C.cache_dir(r, 20261102, "m6", "held"), r / "20261102" / "held" / "cache" / "m6")
        self.assertEqual(C.cache_dir(r, 20261102, "train", "held"), r / "20261102" / "cache" / "train")
        self.assertEqual(C.split_seed("m6", 20261103, "held"), 20261503)
        self.assertEqual(C.split_seed("speak2", 20261101, "held"), 20261501)

    def test_a_held_m6_cache_builds_past_42(self):
        TMP.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=str(TMP), prefix="scene-fm6-cache-") as td:
            d = C.cache_dir(Path(td), 20261102, "m6", "held")
            sh = C.build("m6", 20261102, d, limit=3, recheck_n=1, tset="held")
            self.assertEqual((sh["seed"], sh["rows"], sh["test_set"]), (20261502, 3, "held"))

    def test_the_held_split_count_reaches_the_cache(self):
        # C.build draws W.scenes_for(split, seed, limit, tset=…): on «held» the m6 split has 84 rows (checked on the spec list
        # the builder draws, without rendering 84 canvases)
        self.assertEqual(len(W.scenes_for("m6", C.split_seed("m6", 20261101, "held"), None, tset="held")), 84)

    def test_run_takes_a_test_set(self):
        from brain.scene import run as R
        self.assertEqual(R.R_TSET, "fresh")
        self.assertEqual(R.r_seed_root(Path("/x"), 20261102), Path("/x") / "20261102" / "fresh")
        self.assertEqual(R.r_seed_root(Path("/x"), 20261102, "held"), Path("/x") / "20261102" / "held")
        self.assertIn("held", R.CACHE_R_TSETS)
        self.assertEqual(R.CACHE_R_TSETS[:2], ("s1b1", "fresh"))


if __name__ == "__main__":
    unittest.main()
