# edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:28 +0400 — PREREG-INNER-1 §2 «the re-seeing» + AMENDMENT 1 (the law: research-1003 @ 9c589b2,
# file sha256 127b063c…168d; the co-signed TEXT 857e07b2…faa82), test-first: red on afe3909 (the organ has no turn_remembered).
"""tests/genome/test_brain_remembered.py — THE BRAIN RE-SEES A REMEMBERED SCENE (genome/brain.py: Brain.turn_remembered, Brain.scenes_with).

The inner turn feeds the STORED scene back to the turn: X = seen[o][0], [fix, members] = canvas[o], pos = the members' mean cell
(brain/scene/eye.py:hypotheses's own arithmetic). The pin is PARITY: right after a scene is learned, turn(glance) and
turn_remembered(order) are the same turn, key for key — and a planted member shift must break it (a parity that cannot fail pins
nothing). The small life is tests/genome/test_brain_organ.py's synthetic toy."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import brain as B
from tests.genome import test_brain_organ as T

CFG = dict(T.CFG)
WS = T.WS
LIVED = 120                       # three calibrations (40, 80, 120)
TURN_KEYS = ("scene", "n_hyp", "order", "members", "held", "expected", "say", "ask", "reason")


def grown() -> "B.Brain":
    b = B.Brain(CFG)
    T.live(b, LIVED)
    return b


def plain(d):
    """A turn's dict with numpy scalars/arrays made plain, so two turns compare by value."""
    if isinstance(d, dict):
        return {k: plain(v) for k, v in d.items()}
    if isinstance(d, (list, tuple)):
        return [plain(v) for v in d]
    if isinstance(d, np.generic):
        return d.item()
    if isinstance(d, np.ndarray):
        return d.tolist()
    return d


class Parity(unittest.TestCase):
    def test_at_one_state_the_remembered_turn_is_the_glance_s_turn(self) -> None:
        """The pin: the STORED scene (X, canvas, the members' mean cell) reconstructs the turn the glance gives — at the SAME brain
        state. The DRIVE turn runs BEFORE the brain learns the scene, so «the live turn» and the remembered one are one learn apart
        (a first draft compared those and failed on the margin: 1.18 before the learn, 1.03 after — the delta rule moved it)."""
        b = B.Brain(CFG)
        T.live(b, LIVED)
        n_pairs = moved = 0
        for i in range(LIVED, LIVED + 30):
            g, words, _t, _b = T.toy_scene(i)
            before = b.turn(g, scene=i, world_seed=WS)        # the DRIVE turn: before the brain hears (recorded, not the pin)
            b.learn(g, words, moment=f"m{i}", scene=i, world_seed=WS)
            o = b.n_learned - 1
            same_state = b.turn(g, scene=i, world_seed=WS)    # the glance's turn at the state the remembered turn reads
            rem = b.turn_remembered(o, world_seed=WS)
            self.assertEqual({k: plain(rem[k]) for k in TURN_KEYS}, {k: plain(same_state[k]) for k in TURN_KEYS}, f"scene {i}")
            self.assertEqual((rem["learned"], rem["moment"], rem["world"], rem["heard"]), (o, f"m{i}", "scene", list(words)))
            moved += plain(before) != {k: plain(same_state[k]) for k in TURN_KEYS}
            n_pairs += 1
        self.assertEqual(n_pairs, 30)
        # the presence counts: the pairs include turns that SAY (a parity over silence pins nothing), and learning moved SOME turn
        said = sum(b.turn_remembered(o, world_seed=WS)["say"] is not None for o in range(LIVED, LIVED + 30))
        self.assertGreater(said, 0, "no remembered turn said anything: the parity was read over silence")
        self.assertGreater(moved, 0, "no turn moved across its own learn: the before/after distinction is untested here")

    def _saying_scene(self, b: "B.Brain") -> int:
        for cand in range(b.n_learned - 1, -1, -1):
            t = b.turn_remembered(cand, world_seed=WS)
            if t["n_hyp"] >= 2 and t["say"] is not None:
                return cand
        self.fail("no learned scene with two things and a say")

    def test_a_planted_fixation_shift_on_the_saying_thing_breaks_the_parity(self) -> None:
        b = grown()
        o = self._saying_scene(b)
        before = plain(b.turn_remembered(o, world_seed=WS))
        fix, members = copy.deepcopy(b.canvas[o])
        h = before["say"]["hyp"]
        other = next(k for k in range(len(members)) if k != h)
        # the plant: the SAYING thing's first fixation moved to another thing's cell — its reported cells and position must move
        # (a first draft moved a fixation the turn never reports, and the plant was MISSED)
        planted = [list(f) for f in fix]
        planted[members[h][0]] = list(fix[members[other][0]])
        self.assertNotEqual(planted, [list(f) for f in fix], "the plant changed nothing")
        b.canvas[o] = [planted, members]
        after = plain(b.turn_remembered(o, world_seed=WS))
        self.assertNotEqual(before["say"]["pos"], after["say"]["pos"], "the plant moved the stored canvas and the say's position did not")

    def test_a_planted_feature_swap_breaks_the_parity(self) -> None:
        b = grown()
        o = self._saying_scene(b)
        before = plain(b.turn_remembered(o, world_seed=WS))
        X, heard, third = b.seen[o]
        Xp = np.array(X, dtype=np.float64, copy=True)
        Xp[[0, 1]] = Xp[[1, 0]]                               # the plant: two things' features exchanged in the STORE
        self.assertFalse(np.array_equal(Xp, X), "the plant changed nothing")
        b.seen[o] = (Xp, heard, third)
        after = plain(b.turn_remembered(o, world_seed=WS))
        self.assertNotEqual((before["held"], before["expected"]), (after["held"], after["expected"]),
                            "the plant exchanged the stored features and the remembered turn did not move")

    def test_the_positions_are_the_eye_s_own_arithmetic(self) -> None:
        b = grown()
        o = b.n_learned - 1
        g = T.toy_scene(o)[0]
        hyps, _X = B.things_in_view(g)
        rem = b.turn_remembered(o, world_seed=WS)
        fix, members = b.canvas[o]
        for h, hyp in enumerate(hyps):
            pos = [float(np.mean([fix[i][0] for i in members[h]])), float(np.mean([fix[i][1] for i in members[h]]))]
            self.assertEqual(pos, [float(hyp.pos[0]), float(hyp.pos[1])])
        if rem["say"] is not None:
            self.assertEqual(rem["say"]["pos"], [float(hyps[rem["say"]["hyp"]].pos[0]), float(hyps[rem["say"]["hyp"]].pos[1])])


class ReadOnly(unittest.TestCase):
    def test_the_state_is_what_it_was_after_every_remembered_turn(self) -> None:
        b = grown()
        h0 = b.state_hash()
        for o in range(0, b.n_learned, 7):
            b.turn_remembered(o, world_seed=WS)
        self.assertEqual(b.state_hash(), h0)

    def test_before_the_first_calibration_it_says_and_asks_nothing(self) -> None:
        b = B.Brain(CFG)
        T.live(b, 10)
        t = b.turn_remembered(3, world_seed=WS)
        self.assertEqual(t["reason"], "not calibrated")
        self.assertIsNone(t["say"])
        self.assertEqual(t["learned"], 3)

    def test_an_order_outside_the_life_is_refused(self) -> None:
        b = grown()
        for bad in (-1, b.n_learned, b.n_learned + 5):
            with self.assertRaises(B.BrainError):
                b.turn_remembered(bad, world_seed=WS)


class ScenesWith(unittest.TestCase):
    def brute(self, b: "B.Brain", word: str):
        return [o for o in range(b.n_learned) if word in b.seen[o][1]]

    def test_the_index_equals_a_scan_of_the_store_for_every_word(self) -> None:
        b = grown()
        words = sorted({w for o in range(b.n_learned) for w in b.seen[o][1]})
        self.assertGreater(len(words), 0)
        for w in words:
            self.assertEqual(b.scenes_with(w), self.brute(b, w), w)
        self.assertEqual(b.scenes_with("never-heard"), [])

    def test_the_index_follows_later_learning_and_a_load(self) -> None:
        b = grown()
        words = sorted({w for o in range(b.n_learned) for w in b.seen[o][1]})
        for w in words:
            b.scenes_with(w)                      # built now, before more scenes are learned
        T.live(b, LIVED + 25, start=LIVED)
        for w in words:
            self.assertEqual(b.scenes_with(w), self.brute(b, w), w)
        with tempfile.TemporaryDirectory() as td:
            b.save(Path(td) / "brain")
            c = B.Brain.load(Path(td) / "brain", CFG)
        for w in words:
            self.assertEqual(c.scenes_with(w), self.brute(c, w), w)


if __name__ == "__main__":
    unittest.main()
