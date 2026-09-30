# edit: Claude (Fable 5.1, the seat), 2026-09-30 10:3x +0400 — PREREG-HEARS-2 §1: the reader of the brain's turns per hand, tested on a journal the REAL
# mind wrote over tests/creature/test_hears_mind.py's two-hand tape (a fixture from the real producer, #246 (8)), plus a planted
# journal whose numbers are known by construction.
"""tests/tools/test_worlds_read.py — tools/brain/worlds_read.py."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import creature.mind as MM
from tests.creature import _scene_tape as S
from tests.creature import test_hears_mind as HM
from tools.brain import worlds_read as R


def _turn(world, heard, say, surprise, n_hyp=2):
    r = {"kind": "brain", "act": "turn", "moment": "m", "seq": 1, "at": "t", "heard": heard, "say": ({"words": say} if say else None),
         "surprise": surprise, "n_hyp": n_hyp, "ask": None, "expected": [[None]]}
    if world != "scene":
        r["world"] = world
    return r


def _learn(world, words):
    r = {"kind": "brain", "act": "learn", "moment": "m", "seq": 1, "at": "t", "words": words}
    if world != "scene":
        r["world"] = world
    return r


class Planted(unittest.TestCase):
    def test_the_numbers_known_by_construction(self) -> None:
        rows = []
        for i in range(10):                                   # the scene hand learns «star» before the maker names one
            rows += [_turn("scene", ["star", "red"], ["star"] if i % 2 == 0 else ["blue"], 0.0 if i % 2 == 0 else 0.5), _learn("scene", ["star", "red"])]
        for i in range(4):                                    # the maker: star (shared) ×2 then bar (maker-only) ×2
            w = "star" if i < 2 else "bar"
            rows += [_turn("maker", [w], [w] if i != 3 else ["star"], 0.0 if i != 3 else 1.0, n_hyp=1), _learn("maker", [w])]
        o = R.read(rows, window=5, k=3)
        sc, mk = o["worlds"]["scene"], o["worlds"]["maker"]
        self.assertEqual((sc["turns"], sc["learned"]), (10, 10))
        self.assertEqual([c["n"] for c in sc["windows"]], [5, 5])
        self.assertEqual(sc["windows"][0]["say_rate"], 1.0)
        self.assertAlmostEqual(sc["windows"][0]["agree_rate"], 3 / 5)
        self.assertAlmostEqual(sc["windows"][0]["surprise"], 0.2)
        self.assertEqual(sc["first_meeting"], {"star": 0, "red": 0})
        self.assertEqual(sc["first_agreed_say"], {"star": 0})
        self.assertEqual((mk["turns"], mk["learned"]), (4, 4))
        self.assertEqual(mk["n_hyp"], {1: 4})
        self.assertEqual(mk["first_meeting"], {"star": 0, "bar": 2})
        self.assertEqual(mk["first_agreed_say"], {"star": 0, "bar": 2})
        t = o["transfer"]
        self.assertEqual((t["shared"]["n"], t["shared"]["agreed"], t["shared"]["words"]), (2, 2, ["star"]))
        self.assertEqual((t["maker-only"]["n"], t["maker-only"]["agreed"], t["maker-only"]["words"]), (2, 1, ["bar"]))
        lines = R.report(o)
        self.assertTrue(any("TRANSFER" in l for l in lines))


class OnTheRealProducer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="worlds-read-"))
        tape_root = cls.tmp / "tape-root"
        tape_root.mkdir()
        cls.info = HM.build(tape_root, n_train=60, every=4)
        rows = S.rows(tape_root)
        root = S.link_root(tape_root, cls.tmp / "run" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(HM.lean_text("scene maker"))
        m = MM.Mind(gp, root)
        try:
            for row in rows:
                m.consume(row)
        finally:
            m.close()
        cls.root = root

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_it_reads_the_journal_the_mind_wrote(self) -> None:
        out = self.tmp / "out"
        self.assertEqual(R.main(["--journal", str(self.root / "journal"), "--window", "20", "--out", str(out)]), 0)
        o = json.loads((out / "worlds.json").read_text())
        self.assertEqual(sorted(o["worlds"]), ["maker", "scene"])
        self.assertEqual(o["worlds"]["scene"]["turns"], 60)
        self.assertEqual(o["worlds"]["maker"]["turns"], len(self.info["maker"]))
        self.assertEqual(o["worlds"]["maker"]["learned"], len(self.info["maker"]))
        self.assertEqual(set(o["worlds"]["maker"]["first_meeting"]), set(HM.MAKER_WORDS))
        self.assertIn("star", o["transfer"]["shared"]["words"] + o["transfer"]["maker-only"]["words"])
        self.assertTrue((out / "worlds.txt").read_text().startswith("WORLDS the brain heard"))


if __name__ == "__main__":
    unittest.main()
