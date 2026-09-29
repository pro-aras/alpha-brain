# edit: Claude (Fable 5.1, the seat), 2026-09-29 16:24 +0400 — PREREG-BRAIN-DRIVES §2, test-first (red on master 262cc20: the organ has no `turn`).
"""tests/genome/test_brain_turn.py — THE BRAIN TAKES ITS TURN (genome/brain.py: Brain.turn, Brain.surprise).

The turn is what the brain does BY ITSELF at a canvas, before it hears: it expects, it says, it asks. It never learns.
The small life is tests/genome/test_brain_organ.py's synthetic toy (three shapes, two colours, one fixation a thing)."""
from __future__ import annotations

import unittest

import numpy as np

from brain.world.seeds import substream
from genome import brain as B
from tests.genome import test_brain_organ as T

CFG = dict(T.CFG)
WS = T.WS
LIVED = 120                       # three calibrations (40, 80, 120)
FRESH = 10_000                    # toy scenes the brain never learned


def grown() -> "B.Brain":
    b = B.Brain(CFG)
    T.live(b, LIVED)
    return b


def true_words(thing) -> set:
    return {thing[0], thing[1]}


class BeforeTheFirstCalibration(unittest.TestCase):
    def test_it_orders_the_things_and_says_and_asks_nothing(self) -> None:
        b = B.Brain(CFG)
        T.live(b, 10)
        g, _w, things, _b = T.toy_scene(FRESH)
        t = b.turn(g, scene=FRESH, world_seed=WS)
        self.assertEqual(t["n_hyp"], len(things))
        self.assertEqual(sorted(t["order"]), list(range(len(things))))
        self.assertEqual(t["reason"], "not calibrated")
        self.assertIsNone(t["say"])
        self.assertIsNone(t["ask"])
        self.assertEqual(t["expected"], [])
        self.assertIsNone(B.Brain.surprise(t, ["sa"]))

    def test_nothing_in_view(self) -> None:
        b = grown()
        t = b.turn({"feats": [np.ones(144) / 12.0], "fix": [], "windows": [], "residual": [None]}, scene=1, world_seed=WS)
        self.assertEqual((t["n_hyp"], t["reason"], t["say"], t["ask"]), (0, "nothing in view", None, None))


class TheTurnNeverLearns(unittest.TestCase):
    def test_the_state_is_what_it_was_after_every_turn(self) -> None:
        b = grown()
        h0 = b.state_hash()
        for i in range(FRESH, FRESH + 40):
            g = T.toy_scene(i)[0]
            b.turn(g, scene=i, world_seed=WS)
            self.assertEqual(b.state_hash(), h0, f"the turn at toy scene {i} changed the brain")

    def test_a_life_with_turns_is_the_life_without_them(self) -> None:
        a, b = B.Brain(CFG), B.Brain(CFG)
        for i in range(LIVED):
            g, words, _t, _b = T.toy_scene(i)
            b.turn(g, scene=i, world_seed=WS)
            ra = a.learn(g, words, moment=f"m{i}", scene=i, world_seed=WS)
            rb = b.learn(g, words, moment=f"m{i}", scene=i, world_seed=WS)
            self.assertEqual(ra, rb)
        self.assertEqual(a.state_hash(), b.state_hash())

    def test_the_same_canvas_gives_the_same_turn(self) -> None:
        a, b = grown(), grown()
        for i in range(FRESH, FRESH + 25):
            g = T.toy_scene(i)[0]
            ta = a.turn(g, scene=i, world_seed=WS)
            self.assertEqual(ta, a.turn(g, scene=i, world_seed=WS))
            self.assertEqual(ta, b.turn(g, scene=i, world_seed=WS))


class WhatItSays(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.b = grown()
        cls.turns = []
        for i in range(FRESH, FRESH + 200):
            g, _w, things, _b = T.toy_scene(i)
            cls.turns.append((cls.b.turn(g, scene=i, world_seed=WS), things, g))

    def test_it_speaks_on_most_canvases_and_what_it_says_is_true(self) -> None:
        said = [(t, th) for t, th, _g in self.turns if t["say"] is not None]
        self.assertGreater(len(said), 100, "the presence count: a mouth that says nothing passes the truth mark")
        true = sum(all(w in true_words(th[t["say"]["hyp"]]) for w in t["say"]["words"]) for t, th in said)
        self.assertGreaterEqual(true / len(said), 0.9, (true, len(said)))

    def test_a_say_carries_its_thing_its_cells_and_its_read_back(self) -> None:
        t, _th, g = next(x for x in self.turns if x[0]["say"] is not None)
        s = t["say"]
        self.assertEqual(sorted(s), ["fix", "hyp", "margin", "pos", "readback", "words"])
        self.assertEqual(s["readback"], s["hyp"], "spoken only when its own pointing, given the phrase, lands on the thing")
        self.assertEqual(s["fix"], [[int(y), int(x)] for y, x in [g["fix"][s["hyp"]]]])
        self.assertTrue(all(isinstance(w, str) for w in s["words"]) and s["words"])

    def test_the_mouth_is_the_scored_mouth(self) -> None:
        # the say of the turn is learners.produce_believed over the LAW road, with the turn's own tie generator
        from brain.scene import learners as Lr
        n = 0
        for t, _th, g in self.turns[:60]:
            if t["say"] is None:
                continue
            h = t["say"]["hyp"]
            _hy, X = B.things_in_view(g)
            a = Lr.produce_believed(self.b.road(), X, h, lambda: substream(WS, f"turn-say:{t['scene']}:{h}"))
            self.assertEqual(a["spoken"], t["say"]["words"])
            n += 1
        self.assertGreater(n, 20)

    def test_a_young_word_is_never_said(self) -> None:
        b = grown()
        ps, pc = T._protos()
        r = substream(WS, "turn-young")
        v = r.normal(size=144)
        v = v / np.linalg.norm(v)
        g = {"feats": [v, np.ones(144) / 12.0], "fix": [(5, 5)], "windows": [], "residual": [None, None]}
        b.learn(g, ["dax"], moment="young-1", scene=900_001, world_seed=WS)      # ONE meeting: «dax» is young (young 3)
        b.calibrate()
        t = b.turn(g, scene=900_002, world_seed=WS)
        self.assertTrue(t["say"] is None or "dax" not in t["say"]["words"], t["say"])


class WhatItLooksAtFirst(unittest.TestCase):
    def test_the_order_is_by_fixations_then_by_index(self) -> None:
        b = grown()
        ps, pc = T._protos()
        f = lambda s, c: (ps[s] + pc[c]) / np.linalg.norm(ps[s] + pc[c])            # noqa: E731
        # thing 0: one fixation at (2, 2); thing 1: TWO fixations at (9, 9) and (9, 10) — one hypothesis (within 2 cells)
        g = {"feats": [f("sa", "cg"), f("sb", "cr"), f("sb", "cr"), np.ones(144) / 12.0], "fix": [(2, 2), (9, 9), (9, 10)],
             "windows": [], "residual": [None] * 4}
        t = b.turn(g, scene=5, world_seed=WS)
        self.assertEqual(t["n_hyp"], 2)
        self.assertEqual(t["members"], [[0], [1, 2]])
        self.assertEqual(t["order"], [1, 0], "the thing it looked at twice comes first")
        self.assertEqual(t["say"]["hyp"], 1)


class WhatItAsks(unittest.TestCase):
    def test_it_asks_about_the_thing_it_holds_no_word_for(self) -> None:
        b = grown()
        ps, pc = T._protos()
        known = (ps["sa"] + pc["cg"]) / np.linalg.norm(ps["sa"] + pc["cg"])
        r = substream(WS, "turn-strange")
        strange = r.normal(size=144) * 5.0                                   # far from every prototype: no band holds it
        g = {"feats": [known, strange, np.ones(144) / 12.0], "fix": [(2, 2), (9, 9)], "windows": [], "residual": [None] * 3}
        t = b.turn(g, scene=6, world_seed=WS)
        self.assertEqual(t["held"][1], [])
        self.assertIsNotNone(t["ask"])
        self.assertEqual(t["ask"]["hyp"], 1)
        self.assertEqual(t["ask"]["fix"], [[9, 9]])
        self.assertNotEqual((t["say"] or {}).get("hyp"), 1, "and it does not name what it cannot hold")

    def test_it_asks_nothing_when_it_holds_a_word_for_every_thing(self) -> None:
        b = grown()
        n = 0
        for i in range(FRESH, FRESH + 100):
            t = b.turn(T.toy_scene(i)[0], scene=i, world_seed=WS)
            if all(t["held"][h] for h in range(t["n_hyp"])):
                self.assertIsNone(t["ask"])
                n += 1
        self.assertGreater(n, 20, "the presence count")


class ItsSurprise(unittest.TestCase):
    def turn_with(self, expected):
        return {"n_hyp": len(expected), "order": list(range(len(expected))), "expected": expected, "reason": None}

    def test_the_share_of_the_heard_words_no_one_thing_was_expected_to_carry(self) -> None:
        t = self.turn_with([["cg", "sa"], ["cr", "sb"]])
        self.assertEqual(B.Brain.surprise(t, ["cr", "sb"]), 0.0)
        self.assertEqual(B.Brain.surprise(t, ["sb"]), 0.0)
        self.assertEqual(B.Brain.surprise(t, ["cr", "sa"]), 0.5)
        self.assertEqual(B.Brain.surprise(t, ["cx", "sz"]), 1.0)
        self.assertEqual(B.Brain.surprise(t, ["cr", "cr", "sb"]), 0.0, "a word said twice is one word")

    def test_no_expectation_or_no_word_is_no_surprise(self) -> None:
        self.assertIsNone(B.Brain.surprise(self.turn_with([]), ["sa"]))
        self.assertIsNone(B.Brain.surprise(self.turn_with([["sa"]]), []))

    def test_a_type_with_no_mature_word_expects_nothing(self) -> None:
        t = self.turn_with([[None, "sa"]])
        self.assertEqual(B.Brain.surprise(t, ["sa"]), 0.0)
        self.assertEqual(B.Brain.surprise(t, ["cg"]), 1.0)

    def test_it_falls_as_the_brain_lives(self) -> None:
        b = B.Brain(CFG)
        early, late = [], []
        for i in range(400):
            g, words, _t, _b = T.toy_scene(i)
            s = B.Brain.surprise(b.turn(g, scene=i, world_seed=WS), words)
            if s is not None:
                (early if i < 120 else late).append(s)
            b.learn(g, words, moment=f"m{i}", scene=i, world_seed=WS)
        self.assertGreater(len(early), 30)
        self.assertGreater(len(late), 200)
        self.assertLess(np.mean(late), 0.5)


class TheFenceStands(unittest.TestCase):
    def test_the_organ_still_imports_no_truth(self) -> None:
        import ast
        tree = ast.parse(T.BRAIN_PY.read_text())
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                names.add(node.module or "")
                names.update(f"{node.module}.{a.name}" for a in node.names)
            elif isinstance(node, ast.Import):
                names.update(a.name for a in node.names)
        for bad in ("brain.scene.world", "brain.scene.marks", "brain.scene.cache", "brain.scene.run"):
            self.assertNotIn(bad, names)


if __name__ == "__main__":
    unittest.main()
