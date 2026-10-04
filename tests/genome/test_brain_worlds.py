# edit: Claude (Fable 5.1, the seat), 2026-09-30 10:2x +0400 — PREREG-HEARS-2 §1 (docs/organism/hears/), test-first: the organ keeps the WORLD of every
# scene it learned (index-aligned with `moments`), the census counts by world, the saved bytes of a scene-only brain are what they
# were, the hash of what was LEARNED ignores the tag, a version-2 state without the tag loads as all scene, `inherit` carries it.
"""tests/genome/test_brain_worlds.py — genome/brain.py under several hands (PREREG-HEARS-2 §1). Red on dfec420: learn() takes no world."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import brain as B
from tests.genome import test_brain_organ as T


def _brain(cfg=None) -> "B.Brain":
    c = dict(T.CFG)
    if cfg:
        c.update(cfg)
    return B.Brain(c)


def live_two_hands(brain: "B.Brain", n_scene: int = 30, n_maker: int = 10):
    """n_scene toy scenes by the scene hand, then n_maker by the maker (the same toy, the world tagged `maker`, its own indexes)."""
    T.live(brain, n_scene)
    for i in range(n_maker):
        g, words, _t, _b = T.toy_scene(5000 + i)
        brain.learn(g, words, moment=f"w0000i{i:06d}t{i:09d}", scene=i, world_seed=T.WS + 1, world="maker")
    return brain


class TheWorldOfEveryScene(unittest.TestCase):
    def test_learn_keeps_the_world_index_aligned_with_the_moments(self) -> None:
        b = live_two_hands(_brain())
        self.assertEqual(len(b.worlds), len(b.moments))
        self.assertEqual(b.worlds[:30], ["scene"] * 30)
        self.assertEqual(b.worlds[30:], ["maker"] * 10)

    def test_learn_without_a_world_is_the_scene_hand(self) -> None:
        b = _brain()
        T.live(b, 5)
        self.assertEqual(b.worlds, ["scene"] * 5)

    def test_the_census_counts_by_world(self) -> None:
        b = live_two_hands(_brain())
        c = b.census()
        self.assertEqual(c["scenes_by_world"], {"maker": 10, "scene": 30})
        self.assertEqual(c["scenes"], 40)
        for w, d in c["words"].items():
            by = d["meetings_by_world"]
            self.assertEqual(sum(by.values()), d["meetings"], (w, by, d["meetings"]))
        # a word met by both hands carries both counts; the maker's ten scenes name at least one word the scene hand named
        shared = [w for w, d in c["words"].items() if set(d["meetings_by_world"]) == {"scene", "maker"}]
        self.assertTrue(shared, c["words"])

    def test_a_scene_only_brain_saves_no_world_key_and_its_bytes_are_what_they_were(self) -> None:
        b = _brain()
        T.live(b, 20)
        meta, _arrays = b._state()
        self.assertNotIn("worlds", meta["brain"])
        self.assertEqual(meta["version"], B.STATE_VERSION)

    def test_a_brain_of_two_hands_saves_the_worlds_and_loads_them_back(self) -> None:
        b = live_two_hands(_brain())
        meta, _arrays = b._state()
        self.assertEqual(meta["brain"]["worlds"], b.worlds)
        with tempfile.TemporaryDirectory() as d:
            base = Path(d) / "brain"
            b.save(base)
            b2 = B.Brain.load(base, dict(T.CFG))
            self.assertEqual(b2.worlds, b.worlds)
            self.assertEqual(b2.census(), b.census())
            self.assertEqual(b2.state_hash(), b.state_hash())

    def test_the_hash_of_what_was_learned_ignores_the_tag(self) -> None:
        """Two brains learn the same canvases and words; one tags them maker. What they LEARNED is one thing (METADATA-1 AMENDMENT 1's
        law: the runs are not learning); the saved FILE's own hash differs, because the file differs."""
        a, b = _brain(), _brain()
        for i in range(12):
            g, words, _t, _b = T.toy_scene(i)
            a.learn(g, words, moment=f"m{i}", scene=i, world_seed=T.WS)
            b.learn(g, words, moment=f"m{i}", scene=i, world_seed=T.WS, world="maker")
        self.assertEqual(a.state_hash(), b.state_hash())
        ma, _ = a._state()
        mb, _ = b._state()
        self.assertNotEqual(json.dumps(ma, sort_keys=True), json.dumps(mb, sort_keys=True))

    def test_a_version_2_state_without_the_tag_loads_as_all_scene(self) -> None:
        b = _brain()
        T.live(b, 15)
        with tempfile.TemporaryDirectory() as d:
            base = Path(d) / "brain"
            b.save(base)
            meta = json.loads(Path(str(base) + ".json").read_text())
            self.assertNotIn("worlds", meta["brain"])
            b2 = B.Brain.load(base, dict(T.CFG))
            self.assertEqual(b2.worlds, ["scene"] * 15)
            self.assertEqual(b2.census()["scenes_by_world"], {"scene": 15})

    def test_a_tag_list_of_the_wrong_length_refuses_by_name(self) -> None:
        b = live_two_hands(_brain())
        with tempfile.TemporaryDirectory() as d:
            base = Path(d) / "brain"
            b.save(base)
            p = Path(str(base) + ".json")
            meta = json.loads(p.read_text())
            meta["brain"]["worlds"] = meta["brain"]["worlds"][:-1]
            meta.pop("state_hash")
            p.write_text(json.dumps(meta, sort_keys=True, separators=(",", ":")) + "\n")
            with self.assertRaises(B.BrainError) as e:
                B.Brain.load(base, dict(T.CFG))
            self.assertIn("worlds", str(e.exception))

    def test_inherit_carries_the_worlds(self) -> None:
        b = live_two_hands(_brain())
        with tempfile.TemporaryDirectory() as d:
            base = Path(d) / "brain"
            b.save(base)
            child, info = B.Brain.inherit(base, dict(T.CFG))
            self.assertEqual(child.worlds, b.worlds)
            self.assertEqual(info["learned"], 40)

    def test_why_cites_by_any_hand_and_names_the_world_of_a_maker_episode_only(self) -> None:
        """A cited episode of another hand carries `world`; a scene episode carries no new key (a closed life's `why` answers are
        journaled whole, so they stay byte-identical)."""
        b = live_two_hands(_brain(), n_scene=45, n_maker=40)
        b.calibrate()
        cited = {"scene": 0, "maker": 0}
        for w in T.SHAPES + T.COLOURS:
            a = b.why(w)
            if a.get("kind") != "because":
                continue
            for e in a["episodes"]:
                order = b.moments.index(e["moment"])
                if b.worlds[order] == "maker":
                    self.assertEqual(e["world"], "maker")
                else:
                    self.assertNotIn("world", e)
                cited[b.worlds[order]] += 1
        self.assertGreater(cited["scene"] + cited["maker"], 0, "the presence count: some word was explained")


if __name__ == "__main__":
    unittest.main()
