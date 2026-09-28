# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:11 +0400 — S1a steps 4–5 (PREREG-R3-TONIGHT §S1a «The learner A-RW», «Arms»):
# A-RW's update checked against the PREREG's formulas computed by hand on one scene; the PROPORTIONAL responsibility
# (never a softmax); noisy-OR; a word with < 3 meetings answers by prototype and band; the episodic write picks the thing
# farthest from every known prototype in band units; P-ORACLE-RW is A-RW with a said word's responsibility 1 on the
# marked referent and NOTHING else (A-RW is blind to a referent passed to it); the conformal thresholds; the pointing
# ties broken by the item's generator, never by order; the LDA reader's distances equal StreamingLDA's own; N-SHUF's
# permutation is a derangement.
from __future__ import annotations

import math
import unittest

import numpy as np

from brain.scene import learners as Lr
from brain.scene.slda import StreamingLDA


class TestConformal(unittest.TestCase):
    def test_lower_and_upper(self) -> None:
        a = list(range(100))                                   # n = 100 → k = ⌈101 · 0.9⌉ = 91
        self.assertEqual(Lr.conformal_lower(a), 9.0)          # the 10th smallest: 91 of 100 accepted (score ≥ τ)
        self.assertEqual(Lr.conformal_upper(a), 90.0)         # the 91st smallest: 91 of 100 accepted (d ≤ q)
        self.assertIsNone(Lr.conformal_lower(list(range(8))))  # n < 9: k > n
        self.assertIsNone(Lr.conformal_upper([1.0]))
        self.assertEqual(Lr.conformal_lower(list(range(9))), 0.0)
        self.assertEqual(Lr.conformal_upper(list(range(9))), 8.0)
        self.assertIsNone(Lr.conformal_lower([]))

    def test_weighted_quantile(self) -> None:
        self.assertEqual(Lr.weighted_quantile(np.array([1.0, 2.0, 3.0]), np.array([1.0, 1.0, 1.0]), 0.5), 2.0)
        self.assertEqual(Lr.weighted_quantile(np.array([1.0, 2.0, 3.0]), np.array([0.0, 0.0, 1.0]), 0.9), 3.0)
        self.assertEqual(Lr.weighted_quantile(np.array([1.0, 2.0, 3.0]), np.array([10.0, 0.1, 0.1]), 0.9), 1.0)
        self.assertIsNone(Lr.weighted_quantile(np.array([1.0]), np.array([0.0]), 0.9))


class TestPick(unittest.TestCase):
    def test_ties_are_uniform_by_the_items_generator_never_by_order(self) -> None:
        counts = np.zeros(3)
        for k in range(600):
            counts[Lr.pick(np.array([0.0, 0.0, 0.0]), np.random.default_rng(k))] += 1
        self.assertTrue(np.all(np.abs(counts / 600 - 1 / 3) < 0.07), counts)
        self.assertEqual(Lr.pick(np.array([0.0, 1.0, -1.0]), np.random.default_rng(0)), 1)
        self.assertEqual(Lr.pick(np.array([0.0, 1.0, -1.0]), np.random.default_rng(0), "min"), 2)
        # the same item generator gives the same pick in every arm
        self.assertEqual(Lr.pick(np.zeros(4), np.random.default_rng(77)), Lr.pick(np.zeros(4), np.random.default_rng(77)))


class TestStandardiser(unittest.TestCase):
    def test_welford_floor_clip(self) -> None:
        st = Lr.RunningStandardiser(3)
        X = np.array([[1.0, 5.0, 0.0], [3.0, 5.0, 0.0], [5.0, 5.0, 100.0]])
        st.observe(X)
        self.assertTrue(np.allclose(st.mean, X.mean(axis=0)))
        sd = st.sd()
        self.assertAlmostEqual(sd[0], float(np.std(X[:, 0], ddof=1)))
        self.assertEqual(sd[1], 1e-3)                          # a constant unit: the floor
        z = st.standardise(np.array([[1.0, 6.0, 0.0]]))
        self.assertEqual(z[0, 1], 8.0)                         # 1 / 1e-3 clipped at +8
        self.assertEqual(Lr.RunningStandardiser(2).sd().tolist(), [1e-3, 1e-3])


def _scene(rng, h=2):
    return rng.normal(size=(h, Lr.RW_DIM))


class TestRWUpdateByHand(unittest.TestCase):
    """The PREREG's formulas, computed independently on one scene from a known state."""

    def test_one_scene_update(self) -> None:
        rng = np.random.default_rng(3)
        L = Lr.RWLearner()
        for _ in range(5):                                     # a history: words exist, weights non-zero
            L.train_scene(_scene(rng, 2), ["red", "circle"], rng=np.random.default_rng(1))
        L.train_scene(_scene(rng, 3), ["big", "star"], rng=np.random.default_rng(2))
        V0, b0 = L.V.copy(), L.b.copy()
        raw = _scene(rng, 3)
        # expected, by hand
        st = Lr.RunningStandardiser(Lr.RW_DIM)
        st.n, st.mean, st.m2 = L.stats.n, L.stats.mean.copy(), L.stats.m2.copy()
        st.observe(raw)
        Z = st.standardise(raw)
        said = {"red", "circle"}
        V, b = V0.copy(), b0.copy()
        for j, w in enumerate(L.words):
            p = 1.0 / (1.0 + np.exp(-(Z @ V0[j] + b0[j])))
            P = 1.0 - np.prod(1.0 - p)
            e = (1.0 if w in said else 0.0) - P
            r = p / p.sum()                                     # the PROPORTIONAL rule
            for t in range(3):
                V[j] += 0.1 * e * r[t] * Z[t]
                b[j] += 0.1 * e * r[t]
        L.train_scene(raw, ["red", "circle"], rng=np.random.default_rng(3))
        self.assertTrue(np.allclose(L.V, V, atol=1e-12))
        self.assertTrue(np.allclose(L.b, b, atol=1e-12))

    def test_a_rw_is_blind_to_a_referent(self) -> None:
        rng = np.random.default_rng(5)
        scenes = [(_scene(rng, 2), ["red", "circle"] if k % 2 else ["star"]) for k in range(20)]
        a, b = Lr.RWLearner(), Lr.RWLearner()
        for k, (raw, ws) in enumerate(scenes):
            a.train_scene(raw, ws, referent=None, rng=np.random.default_rng(k))
            b.train_scene(raw, ws, referent=1, rng=np.random.default_rng(k))
        self.assertTrue(np.array_equal(a.V, b.V))
        self.assertTrue(np.array_equal(a.proto_sum, b.proto_sum))


class TestOracleRWOneDifference(unittest.TestCase):
    def test_said_word_responsibility_is_one_hot_on_the_referent(self) -> None:
        rng = np.random.default_rng(9)
        L = Lr.RWLearner(oracle=True)
        L.train_scene(_scene(rng, 2), ["red", "circle"], referent=0)
        raw = _scene(rng, 3)
        V0, b0 = L.V.copy(), L.b.copy()
        st = Lr.RunningStandardiser(Lr.RW_DIM)
        st.n, st.mean, st.m2 = L.stats.n, L.stats.mean.copy(), L.stats.m2.copy()
        st.observe(raw)
        Z = st.standardise(raw)
        L.train_scene(raw, ["circle"], referent=2)
        j = L.index["circle"]
        p = 1.0 / (1.0 + np.exp(-(Z @ V0[j] + b0[j])))
        e = 1.0 - (1.0 - np.prod(1.0 - p))
        self.assertTrue(np.allclose(L.V[j], V0[j] + 0.1 * e * Z[2]))          # all of it on thing 2
        k = L.index["red"]                                                      # unsaid: proportional, as A-RW
        p = 1.0 / (1.0 + np.exp(-(Z @ V0[k] + b0[k])))
        e = 0.0 - (1.0 - np.prod(1.0 - p))
        self.assertTrue(np.allclose(L.V[k], V0[k] + 0.1 * e * (p / p.sum()) @ Z))

    def test_unseen_referent_skips_the_said_words(self) -> None:
        rng = np.random.default_rng(10)
        L = Lr.RWLearner(oracle=True)
        L.train_scene(_scene(rng, 2), ["red", "circle"], referent=1)
        V0 = L.V.copy()
        L.train_scene(_scene(rng, 2), ["red"], referent=None)
        self.assertTrue(np.array_equal(L.V[L.index["red"]], V0[L.index["red"]]))
        self.assertFalse(np.array_equal(L.V[L.index["circle"]], V0[L.index["circle"]]))
        self.assertEqual(L.skipped_said, 1)


class TestEpisodicWriteAndYoungWords(unittest.TestCase):
    def test_new_word_takes_the_thing_farthest_in_bands_and_the_median_band(self) -> None:
        L = Lr.RWLearner()
        rng = np.random.default_rng(0)
        base = rng.normal(size=(1, Lr.RW_DIM))
        for k in range(40):                                    # teach «circle» around one region
            L.train_scene(base + 0.05 * rng.normal(size=(1, Lr.RW_DIM)), ["circle"], rng=np.random.default_rng(k))
        near = base + 0.05 * rng.normal(size=(1, Lr.RW_DIM))
        far = base + 3.0 * rng.normal(size=(1, Lr.RW_DIM))
        known_band = L.band(L.index["circle"])
        raw = np.vstack([near, far])
        Zexp = None
        L.train_scene(raw, ["dax"], rng=np.random.default_rng(1))
        j = L.index["dax"]
        Zexp = L.stats.standardise(raw)
        self.assertTrue(np.allclose(L.prototype(j), Zexp[1]))  # the far thing (standardised as the scene was)
        self.assertEqual(L.band(j), known_band)                  # the median band of the known words (one known)
        self.assertEqual(int(L.meetings[j]), 1)
        # < 3 meetings → answers by prototype and band: p ∈ {0, 1}
        lp = L.logp_answer(L.stats.standardise(raw))
        self.assertTrue(set(np.unique(lp[:, j])).issubset({0.0, -np.inf}))
        self.assertEqual(lp[1, j], 0.0)

    def test_first_word_ever_has_an_infinite_band_until_its_second_meeting(self) -> None:
        L = Lr.RWLearner()
        rng = np.random.default_rng(4)
        L.train_scene(_scene(rng, 2), ["star"], rng=np.random.default_rng(0))
        self.assertEqual(L.band(0), float("inf"))
        L.train_scene(_scene(rng, 2), ["star"], rng=np.random.default_rng(1))
        self.assertTrue(math.isfinite(L.band(0)))

    def test_new_words_of_one_utterance_share_one_thing(self) -> None:
        L = Lr.RWLearner()
        rng = np.random.default_rng(6)
        L.train_scene(_scene(rng, 3), ["big", "red", "circle"], rng=np.random.default_rng(3))
        P = np.stack([L.prototype(i) for i in range(3)])
        self.assertTrue(np.array_equal(P[0], P[1]) and np.array_equal(P[1], P[2]))

    def test_third_meeting_switches_to_the_logistic(self) -> None:
        L = Lr.RWLearner()
        rng = np.random.default_rng(8)
        for k in range(3):
            L.train_scene(_scene(rng, 2), ["ring"], rng=np.random.default_rng(k))
        lp = L.logp_answer(L.stats.standardise(_scene(rng, 2)))
        self.assertTrue(np.all(np.isfinite(lp)) and np.all(lp < 0))


class TestRWLearnsAToy(unittest.TestCase):
    """A synthetic MACHINERY toy (NOT the PREREG's toy, which alone decides the lr): each word lives on its own planted
    direction; after ambiguous two-thing scenes the learner points to the named thing far above chance, and N-SHUF-style
    shuffled words teach nothing. Run at lr 0.01: at the PREREG's 0.1 on a standardised 146-dim input one update moves a
    logit by ≈ 0.1 · e · r · ‖z‖² ≈ 3.6 and this toy's early random assignments LOCK IN (measured 2026-09-28, the
    builder's scratch dbg_toy.py: word «d» at p 0.999 on direction a) — a reading for the hand-back, not a defect."""

    def _world(self, rng, n, shuffle=False):
        dirs = {w: rng.normal(size=Lr.RW_DIM) for w in ("a", "b", "c", "d")}
        scenes = []
        for _ in range(n):
            ws = rng.choice(list(dirs), size=2, replace=False)
            raw = np.stack([dirs[w] + 0.3 * rng.normal(size=Lr.RW_DIM) for w in ws])
            said = str(ws[rng.integers(2)])
            scenes.append((raw, [said], list(ws)))
        if shuffle:
            perm = Lr.nshuf_permutation(rng, n)
            scenes = [(scenes[i][0], scenes[perm[i]][1], scenes[i][2]) for i in range(n)]
        return dirs, scenes

    def _score(self, L, dirs, rng, n=200):
        ok = 0
        for k in range(n):
            ws = rng.choice(list(dirs), size=2, replace=False)
            raw = np.stack([dirs[w] + 0.3 * rng.normal(size=Lr.RW_DIM) for w in ws])
            a = L.answer_point(raw, [str(ws[0])], np.random.default_rng(k))
            ok += a["point"] == 0
        return ok / n

    def test_learns_and_its_shuffle_does_not(self) -> None:
        rng = np.random.default_rng(11)
        dirs, scenes = self._world(rng, 1500)
        L = Lr.RWLearner(lr=0.01)
        for k, (raw, ws, _t) in enumerate(scenes):
            L.train_scene(raw, ws, rng=np.random.default_rng(k))
        L.calibrate([(raw, ws, None) for raw, ws, _t in scenes])
        self.assertGreater(self._score(L, dirs, np.random.default_rng(12)), 0.9)
        rng2 = np.random.default_rng(11)
        dirs2, sh = self._world(rng2, 1500, shuffle=True)
        N = Lr.RWLearner(lr=0.01)
        for k, (raw, ws, _t) in enumerate(sh):
            N.train_scene(raw, ws, rng=np.random.default_rng(k))
        N.calibrate([(raw, ws, None) for raw, ws, _t in sh])
        self.assertLess(abs(self._score(N, dirs2, np.random.default_rng(12)) - 0.5), 0.12)


class TestLDAReader(unittest.TestCase):
    def _fit(self, rng, eps=0.1):
        R = Lr.LDAReader(eps)
        mus = {w: rng.normal(size=144) for w in ("red", "blue", "circle", "star")}
        for _ in range(300):
            c, s = str(rng.choice(["red", "blue"])), str(rng.choice(["circle", "star"]))
            x = mus[c] + mus[s] + 0.2 * rng.normal(size=144)
            R.train_scene(x, [c, s])
        return R, mus

    def test_distances_equal_streaming_ldas_own(self) -> None:
        rng = np.random.default_rng(2)
        R, _m = self._fit(rng)
        R.prepare()
        X = rng.normal(size=(5, 144))
        mine = R.distances(X)
        theirs = np.stack([R.lda.distances(x) for x in X])
        self.assertTrue(np.allclose(mine, theirs, rtol=1e-7, atol=1e-7))

    def test_point_name_band(self) -> None:
        rng = np.random.default_rng(3)
        R, mus = self._fit(rng)
        info = R.prepare()
        self.assertEqual(set(info["band"]), {"red", "blue", "circle", "star"})
        X = np.stack([mus["red"] + mus["circle"], mus["blue"] + mus["star"]]) + 0.2 * rng.normal(size=(2, 144))
        self.assertEqual(R.answer_point(X, ["blue", "star"], np.random.default_rng(0))["point"], 1)
        self.assertEqual(R.answer_point(X, ["red"], np.random.default_rng(0))["point"], 0)
        self.assertEqual(R.name_forced(X[0], ["circle", "star"]), "circle")
        self.assertEqual(R.name_forced(X[1], ["red", "blue"]), "blue")
        self.assertIn("red", R.what_is_this(X[0]))
        far = 50 * rng.normal(size=144)
        self.assertEqual(R.what_is_this(far), [])
        self.assertTrue(R.answer_point(np.stack([far, -far]), ["red", "circle"], np.random.default_rng(0))["none"])

    def test_unseen_referent_observes_nothing(self) -> None:
        R = Lr.LDAReader(0.1)
        R.train_scene(None, ["red"])
        self.assertEqual((R.names, R.skipped), ([], 1))


class TestFeeds(unittest.TestCase):
    def test_nshuf_is_a_derangement_fixed_by_its_seed(self) -> None:
        p = Lr.nshuf_permutation(np.random.default_rng(20261101), 10000)
        self.assertEqual(sorted(p.tolist()), list(range(10000)))
        self.assertFalse(np.any(p == np.arange(10000)))
        self.assertTrue(np.array_equal(p, Lr.nshuf_permutation(np.random.default_rng(20261101), 10000)))

    def test_rw_input(self) -> None:
        x = Lr.feed_rw(np.ones((2, 144)), np.array([[8.0, 4.0], [0.0, 16.0]]))
        self.assertEqual(x.shape, (2, 146))
        self.assertEqual(x[0, 144:].tolist(), [0.5, 0.25])
        self.assertIsNone(Lr.feed_oracle(np.ones((2, 144)), None))
        self.assertEqual(Lr.feed_oracle(np.eye(2, 144), 1)[1], 1.0)


if __name__ == "__main__":
    unittest.main()
