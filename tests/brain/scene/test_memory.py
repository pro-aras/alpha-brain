# edit: Claude (Opus 5.5, T-MEM-1 builder), 2026-09-28 17:24 +0400 — PREREG-TMEM1 §2–§3 (genome-wt-brain3 ce41448, sha 0a87fefc…, final) with
# CONCLUSION-MEMORY §2 (7cb72ca): the learner's store read back. The raw rows and storage times ride beside Z without moving
# the learner (the `project` hook left None is the old step, value for value); the READER in the store's own coordinates;
# THE ORDER-FREE PIN (a shuffled store rebuilds bit for bit); the label-permuted null falls to chance; the STRONG rule and
# the anchors; the OWM gate leaves every anchor's logit unchanged while the ungated step moves it; one EM pass; META's
# per-word terms add up to the window losses; the drift draw is ∝ the positive drift. Test-first: red on scene-tmem1
# 51126f2 (the merge: memory.py, store_x and the hook do not exist there).
from __future__ import annotations

import copy
import unittest

import numpy as np

from brain.scene import learners as Lr
from brain.scene import memory as MEM
from brain.scene import pickers as PK

WORDS = ("big", "small", "red", "blue", "circle", "square")
TYPES = [("big", "small"), ("red", "blue"), ("circle", "square")]


def _scene(rng, k):
    """A toy scene: 1–2 things; thing 0 carries (size, colour, shape) = k's bits and the parent names it."""
    size, colour, shape = ("big", "small")[k & 1], ("red", "blue")[(k >> 1) & 1], ("circle", "square")[(k >> 2) & 1]
    base = np.zeros(Lr.RW_DIM)
    base[0] = 3.0 if size == "big" else -3.0
    base[1] = 3.0 if colour == "red" else -3.0
    base[2] = 3.0 if shape == "circle" else -3.0
    h = 1 + int(rng.integers(2))
    X = rng.normal(size=(h, Lr.RW_DIM)) * 0.5
    X[0] += base
    words = [w for w, on in ((size, True), (colour, rng.random() < 0.7), (shape, True)) if on]
    return X, words, (size, colour, shape)


def _learner(n=240, seed=0):
    rng = np.random.default_rng(seed)
    L = Lr.RWLearner(lr=0.05)
    for i in range(n):
        X, words, _ = _scene(rng, int(rng.integers(8)))
        L.train_scene(X, words, rng=np.random.default_rng(i))
    return L


def _items(n=160, seed=7):
    rng = np.random.default_rng(seed)
    X, truth = [], []
    for i in range(n):
        x, _w, t = _scene(rng, i % 8)
        X.append(x[0])
        truth.append(t)
    return np.stack(X), truth


class TestStoreRows(unittest.TestCase):
    def test_raw_rows_and_times_ride_beside_z(self) -> None:
        L = _learner()
        for j in range(len(L.words)):
            self.assertEqual(len(L.store_x[j]), len(L.store_z[j]))
            self.assertEqual(len(L.store_t[j]), len(L.store_z[j]))
            for x, z in zip(L.store_x[j], L.store_z[j]):
                self.assertEqual(x.shape, z.shape)
            self.assertEqual(L.store_t[j], sorted(L.store_t[j]))
        self.assertEqual(max(max(t) for t in L.store_t if t), L.scenes)

    def test_the_hook_left_none_is_the_old_step(self) -> None:
        rng = np.random.default_rng(3)
        data = [_scene(rng, int(rng.integers(8)))[:2] for _ in range(80)]
        a, b = Lr.RWLearner(lr=0.05), Lr.RWLearner(lr=0.05)
        for i, (X, w) in enumerate(data):
            a.train_scene(X, w, rng=np.random.default_rng(i))
            b.train_scene(X, w, rng=np.random.default_rng(i), project=lambda L, u, d: (u, d))
        self.assertTrue(np.array_equal(a.V, b.V) and np.array_equal(a.b, b.b))


class TestReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.L = _learner()
        cls.rows = MEM.StoreRows.from_learner(cls.L)
        cls.rd = MEM.StoreReader(cls.rows, TYPES, 0.3)
        cls.X, cls.truth = _items()

    def test_the_stores_own_coordinates(self) -> None:
        X = self.rows.X
        self.assertTrue(np.allclose(self.rd.m, X.mean(axis=0)))
        self.assertTrue(np.allclose(self.rd.s, np.maximum(X.std(axis=0, ddof=1), 1e-3)))
        self.assertLessEqual(float(np.abs(self.rd.Z).max()), 8.0)
        w = "red"
        ii = [i for i in range(len(self.rd.rows)) if self.rd.rows.word[i] == w]
        rr = self.rd.rows.r[ii]
        self.assertTrue(np.allclose(self.rd.mu[w], (rr[:, None] * self.rd.Z[ii]).sum(axis=0) / rr.sum()))

    def test_it_names_what_it_stored(self) -> None:
        for c, ws in enumerate((("big", "small"), ("red", "blue"), ("circle", "square"))):
            names, _m = self.rd.names(self.X, ws)
            acc = np.mean([n == t[c] for n, t in zip(names, self.truth)])
            self.assertGreater(acc, 0.9, ws)

    def test_the_order_free_pin(self) -> None:
        other = MEM.StoreReader(self.rows.shuffled(np.random.default_rng(1)), TYPES, 0.3)
        for ws in (("big", "small"), ("red", "blue"), ("circle", "square")):
            n1, m1 = self.rd.names(self.X, ws)
            n2, m2 = other.names(self.X, ws)
            self.assertEqual(n1, n2)
            self.assertTrue(np.array_equal(m1, m2))

    def test_the_label_null_falls_to_chance(self) -> None:
        null = MEM.StoreReader(self.rows.permuted_labels(np.random.default_rng(2)), TYPES, 0.3)
        names, _m = null.names(self.X, ("circle", "square"))
        acc = np.mean([n == t[2] for n, t in zip(names, self.truth)])
        self.assertLess(acc, 0.75)

    def test_the_strong_rule_and_the_anchors(self) -> None:
        st = self.rd.strong()
        self.assertIn("circle", st)
        for w, v in st.items():
            self.assertGreaterEqual(v["n"], MEM.STRONG_MIN_ROWS)
            self.assertGreaterEqual(v["agree"], MEM.STRONG_AGREE)
        anc = self.rd.anchors(st)
        for w, a in anc.items():
            recent = sorted(st[w]["consistent"], key=lambda i: (int(self.rd.rows.t[i]), int(self.rd.rows.meeting[i])))[-MEM.K_ANCHORS:]
            self.assertTrue(np.array_equal(a, self.rd.rows.X[np.asarray(recent)]))       # the most RECENT self-consistent
        few = MEM.StoreReader(self.rows.take(list(range(0, len(self.rows), 12))), TYPES, 0.3)
        thin = [w for w in few.words if len(few.attributed(w)) < MEM.STRONG_MIN_ROWS]
        self.assertTrue(thin)
        self.assertFalse(set(thin) & set(few.strong()))                                   # < 20 rows is never STRONG
        rnd = self.rd.random_anchors(st, np.random.default_rng(5))
        self.assertEqual(sorted(rnd), sorted(st))

    def test_one_em_pass(self) -> None:
        resp = self.rd.em_responsibilities()
        for key, r in resp.items():
            self.assertAlmostEqual(float(r.sum()), 1.0, places=12)
        again = MEM.StoreRows.from_learner(self.L, resp=resp)
        self.assertEqual(len(again), len(self.rows))


class TestGate(unittest.TestCase):
    def test_owm_projection(self) -> None:
        rng = np.random.default_rng(0)
        A = rng.normal(size=(8, 147))
        u = rng.normal(size=147)
        u2 = MEM.owm_project(u, A)
        self.assertLess(float(np.abs(A @ u2).max()), 1e-9)
        self.assertTrue(np.array_equal(MEM.owm_project(u, np.zeros((0, 147))), u))

    def test_the_gate_keeps_the_anchors_the_ungated_step_moves_them(self) -> None:
        L = _learner()
        rd = MEM.StoreReader(MEM.StoreRows.from_learner(L), TYPES, 0.3)
        anc = rd.anchors(rd.strong())
        rng = np.random.default_rng(11)
        X, words, _ = _scene(rng, 5)
        for gated in (True, False):
            LL = copy.deepcopy(L)
            g = MEM.Gate(anc) if gated else None
            before = {w: (LL.V[LL.index[w]].copy(), LL.b[LL.index[w]]) for w in anc}
            LL.train_scene(X, words, rng=np.random.default_rng(0), project=g)
            moved = 0.0
            for w, a in anc.items():
                A = np.hstack([LL.stats.standardise(a), np.ones((a.shape[0], 1))])
                v0, b0 = before[w]
                moved = max(moved, float(np.abs(A @ np.concatenate([LL.V[LL.index[w]] - v0, [LL.b[LL.index[w]] - b0]])).max()))
            if gated:
                self.assertLess(moved, 1e-9)
                self.assertEqual(g.rises, 0)
                self.assertEqual(g.steps, 1)
            else:
                self.assertGreater(moved, 1e-6)


class TestMeta(unittest.TestCase):
    def test_word_terms_add_up_to_the_window_losses(self) -> None:
        L = _learner()
        rng = np.random.default_rng(4)
        wins = []
        for _ in range(2):
            sc = [_scene(rng, int(rng.integers(8)))[:2] for _ in range(10)]
            wins.append(PK.WindowSet([x for x, _w in sc], [w for _x, w in sc], WORDS))
        terms = MEM.word_terms(L, wins, WORDS)
        total = sum(PK.window_loss(L, w) * w.n for w in wins)
        self.assertAlmostEqual(sum(terms.values()), total, places=8)

    def test_draw_by_weight(self) -> None:
        rng = np.random.default_rng(0)
        d = MEM.draw_by_weight({"a": 3.0, "b": 1.0, "c": -5.0}, rng, 4000, ["a", "b", "c"])
        self.assertAlmostEqual(d.count("a") / 4000, 0.75, delta=0.03)
        self.assertEqual(d.count("c"), 0)
        u = MEM.draw_by_weight({"a": -1.0, "b": 0.0}, rng, 4000, ["a", "b"])
        self.assertAlmostEqual(u.count("a") / 4000, 0.5, delta=0.03)


if __name__ == "__main__":
    unittest.main()
