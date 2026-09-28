# edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 17:50 +0400 — PREREG-TMEM5 §1 and §3 (genome-wt-brain3 ce41448, sha 30121082…, final): the
# CONTEXT learner. Frozen (g ≡ 1, c ≡ 0, neither learned) it is S1c's A-RW bit for bit, and its context window loss is
# pickers.window_loss bit for bit (THE FIRST GATE 1's pin on the learner); the chain rule's factor g_r rides ΔV exactly once
# (a finite-difference check of ∂L/∂V, ∂L/∂g, ∂L/∂c on a one-thing scene, where the delta rule IS the cross-entropy's
# gradient — a doubled factor is CAUGHT); g stays ≥ 0; a room's bias moves only in its own room. Test-first: red on
# scene-tmem1 2609670 (context.py does not exist there).
# edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 18:12 +0400 — PREREG-TMEM5-AMEND-1 (95b6e48, sha ab9a5fca…) §4 (10): the stored ACT
# beside every row is the context the learner was in at the meeting, and row_contexts aligns with StoreRows' rows.
from __future__ import annotations

import copy
import unittest

import numpy as np

from brain.scene import context as CX
from brain.scene import learners as Lr
from brain.scene import memory as MEM
from brain.scene import pickers as PK

ROOMS = ("R1", "R2", "R3", "N")
WORDS = ("big", "small", "red", "blue", "circle", "square")


def _stream(n=120, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        h = 1 + int(rng.integers(3))
        X = rng.normal(size=(h, Lr.RW_DIM)) + (i % 4)
        words = [WORDS[int(k)] for k in rng.choice(len(WORDS), size=1 + int(rng.integers(2)), replace=False)]
        out.append((ROOMS[i % 4], X, words))
    return out


class TestFrozenIsS1c(unittest.TestCase):
    def test_the_frozen_context_learner_is_a_rw_bit_for_bit(self) -> None:
        a = Lr.RWLearner(lr=Lr.LR_S1B1)
        b = CX.CtxLearner(ROOMS, learn_gain=False, learn_bias=False)
        for i, (room, X, w) in enumerate(_stream()):
            a.train_scene(X, w, rng=np.random.default_rng(i))
            b.set_context(room)
            b.train_scene(X, w, rng=np.random.default_rng(i))
        self.assertEqual(a.words, b.words)
        for k in ("V", "b", "meetings", "proto_sum", "proto_w"):
            self.assertTrue(np.array_equal(getattr(a, k), getattr(b, k)), k)
        self.assertTrue(all(np.array_equal(x, y) for sa, sb in zip(a.store_r, b.store_r) for x, y in zip(sa, sb)))
        self.assertEqual(b.g, {r: 1.0 for r in ROOMS})
        self.assertTrue(all(not v.any() for v in b.c.values()))
        rng = np.random.default_rng(9)
        ws = PK.WindowSet([rng.normal(size=(2, Lr.RW_DIM)) for _ in range(6)],
                          [[WORDS[k]] for k in range(6)], WORDS)
        for room in ROOMS:
            self.assertEqual(CX.ctx_window_loss(b, ws, room), PK.window_loss(a, ws))


class TestChainRule(unittest.TestCase):
    def _trained(self):
        L = CX.CtxLearner(ROOMS, lr=0.05, lr_g=0.01)
        for i, (room, X, w) in enumerate(_stream(80, 3)):
            L.set_context(room)
            L.train_scene(X, w, rng=np.random.default_rng(i))
        return L

    def test_the_finite_difference_pin(self) -> None:
        L = self._trained()
        room, raw, words = "R2", np.random.default_rng(5).normal(size=(1, Lr.RW_DIM)) + 1.0, ["red", "circle"]
        L2 = copy.deepcopy(L)
        L2.set_context(room)
        L2.train_scene(raw, words, rng=np.random.default_rng(0))
        dV, db, dg, dc = L2.V - L.V, L2.b - L.b, L2.g[room] - L.g[room], L2.c[room] - L.c[room]
        # the gradient at the SAME standardisation the step used (the scene observed first)
        P = copy.deepcopy(L)
        P.stats.observe(raw)
        P.set_context(room)
        h = 1e-6

        def loss():
            return P.scene_loss(raw, words, room)

        j = P.index["red"]
        for kk in (0, 7, 50):
            P.V[j, kk] += h; up = loss(); P.V[j, kk] -= 2 * h; dn = loss(); P.V[j, kk] += h
            self.assertAlmostEqual(dV[j, kk], -L.lr * (up - dn) / (2 * h), delta=1e-6 * max(1.0, abs(dV[j, kk])))
        g0 = P.g[room]
        P.g[room] = g0 + h; up = loss(); P.g[room] = g0 - h; dn = loss(); P.g[room] = g0
        self.assertAlmostEqual(dg, -L.lr_g * (up - dn) / (2 * h), delta=1e-6 * max(1.0, abs(dg)))
        for jj in (P.index["red"], P.index["big"]):
            P.c[room][jj] += h; up = loss(); P.c[room][jj] -= 2 * h; dn = loss(); P.c[room][jj] += h
            self.assertAlmostEqual(dc[jj], -L.lr * (up - dn) / (2 * h), delta=1e-6 * max(1.0, abs(dc[jj])))
            self.assertAlmostEqual(db[jj], dc[jj], places=15)

    def test_a_doubled_factor_is_caught(self) -> None:
        L = self._trained()
        L.g["R2"] = 0.5
        room, raw, words = "R2", np.random.default_rng(6).normal(size=(1, Lr.RW_DIM)), ["blue"]
        good = copy.deepcopy(L)
        good.set_context(room)
        good.train_scene(raw, words, rng=np.random.default_rng(0))
        dV = good.V - L.V
        doubled = dV * L.g["R2"]                                  # a builder scaling by g twice
        P = copy.deepcopy(L)
        P.stats.observe(raw)
        j, h = P.index["blue"], 1e-6
        kk = int(np.argmax(np.abs(dV[j])))                        # the coordinate the step moves most
        P.V[j, kk] += h; up = P.scene_loss(raw, words, room); P.V[j, kk] -= 2 * h; dn = P.scene_loss(raw, words, room)
        grad = -L.lr * (up - dn) / (2 * h)
        self.assertLess(abs(dV[j, kk] - grad), 1e-6)
        self.assertGreater(abs(doubled[j, kk] - grad), 1e-4)


class TestGainAndBias(unittest.TestCase):
    def test_g_stays_non_negative_and_a_bias_moves_only_in_its_room(self) -> None:
        L = CX.CtxLearner(ROOMS, lr_g=5.0)                        # a huge rate drives g toward its clip
        for i, (room, X, w) in enumerate(_stream(60, 1)):
            before = {r: L.c[r].copy() for r in ROOMS}
            L.set_context(room)
            L.train_scene(X, w, rng=np.random.default_rng(i))
            for r in ROOMS:
                self.assertGreaterEqual(L.g[r], 0.0)
                if r != room and before[r].size:
                    self.assertTrue(np.array_equal(L.c[r][:before[r].size], before[r]))
        bias_only = CX.CtxLearner(ROOMS, learn_gain=False)
        for i, (room, X, w) in enumerate(_stream(40, 2)):
            bias_only.set_context(room)
            bias_only.train_scene(X, w, rng=np.random.default_rng(i))
        self.assertEqual(bias_only.g, {r: 1.0 for r in ROOMS})
        self.assertTrue(any(v.any() for v in bias_only.c.values()))


class TestStoredAct(unittest.TestCase):
    def test_the_act_rides_beside_every_stored_row(self) -> None:
        L = CX.CtxLearner(ROOMS)
        acts = {}
        for i, (room, X, w) in enumerate(_stream(90, 4)):
            L.set_context(room)
            L.train_scene(X, w, rng=np.random.default_rng(i))
            acts[L.scenes] = room
        for j in range(len(L.words)):
            self.assertEqual(len(L.store_c[j]), len(L.store_t[j]))
            self.assertEqual(L.store_c[j], [acts[t] for t in L.store_t[j]])
        rows = MEM.StoreRows.from_learner(L)
        rc = CX.row_contexts(L)
        self.assertEqual(len(rc), len(rows))
        self.assertEqual(rc, [acts[int(t)] for t in rows.t])
        self.assertEqual(set(rc), set(ROOMS))


if __name__ == "__main__":
    unittest.main()
