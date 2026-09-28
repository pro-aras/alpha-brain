# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:45 +0400 — PREREG-S1B1 §2, §3, §5 (sha caace482…), test-first (red on 4093ff9):
# the EAR every arm shares (the learned ORDER KEY, first-heard order, the EXCLUSION counts) and its pin on seed 20261101's
# first 300 utterances (a shuffled-position control must FAIL it); the learner's refusal by its own per-word DIAGONAL
# distance (σ_w per dimension, floor 1e-3; the band B_w = S1a's weighted 0.90 quantile; «what is this?» = every held
# word, whole) and the PHRASE-level «none» (f(t) = max_w d_w / B_w, τ_none = conformal 0.95 over training scenes with ≥ 2
# hypotheses); readings (i) S1a's rules and (ii) σ ≡ 1 from the same state; the σ-floor count; the lock-in pinned on the
# machinery toy; the oracle hears every utterance and calibrates τ_point at 0.95 on ≥ 2-hypothesis scenes; the shared
# production road (shortest accepted candidate, the read-back's unique maximum, the exclusion filter, the reasons).
from __future__ import annotations

import unittest

import numpy as np

from brain.scene import learners as Lr
from brain.scene import world as W


class TestEar(unittest.TestCase):
    def test_order_key_first_heard_and_exclusion(self) -> None:
        e = Lr.Ear()
        for ws in (("big", "red", "circle"), ("red", "circle"), ("circle",), ("small", "star")):
            e.hear(ws)
        self.assertEqual(e.key("big"), 0.0)
        self.assertAlmostEqual(e.key("red"), (0.5 + 0.0) / 2)                  # T4 middle 1/2, T2 first 0
        self.assertEqual(e.key("circle"), 1.0)                                  # the 1-word utterance does not count
        self.assertEqual(e.key("star"), 1.0)
        self.assertEqual(e.key("blue"), 0.5)                                    # never heard in an L ≥ 2 utterance
        self.assertEqual(e.order(["circle", "red", "big"]), ["big", "red", "circle"])
        self.assertEqual(e.count("red", "circle"), 2)
        self.assertEqual(e.count("big", "red"), 1)
        self.assertEqual(e.count("red", "star"), 0)
        self.assertTrue(e.excluded(["red", "star"]))
        self.assertFalse(e.excluded(["big", "red", "circle"]))
        self.assertFalse(e.excluded(["star"]))                                  # a single word has no pair
        e2 = Lr.Ear()
        e2.hear(("small", "star"))
        e2.hear(("tiny",))
        self.assertEqual(e2.key("tiny"), 0.5)                                   # heard only alone
        self.assertEqual(e2.order(["star", "tiny"]), ["tiny", "star"])          # 0.5 < 1.0


def order_pin(ear: "Lr.Ear", words) -> bool:
    size = [ear.key(w) for w in words if w in W.SIZES]
    colour = [ear.key(w) for w in words if w in W.COLOURS]
    shape = [ear.key(w) for w in words if w in W.SHAPES]
    return bool(size and colour and shape and max(size) < min(colour) and max(colour) < min(shape))


class TestOrderKeyPin(unittest.TestCase):
    """§5: from seed 20261101's first 300 utterances the keys read size < colour < shape for every word; a shuffled-
    position control (each utterance's words permuted by a seeded generator) fails the pin."""

    def test_pin_and_its_control(self) -> None:
        utts = [W.train_scene(20261101, i).words for i in range(300)]
        heard = sorted({w for u in utts for w in u})
        ear = Lr.Ear()
        for u in utts:
            ear.hear(u)
        self.assertTrue(order_pin(ear, heard), {w: ear.key(w) for w in heard})
        rng = np.random.default_rng(20261101)
        ctrl = Lr.Ear()
        for u in utts:
            ctrl.hear(tuple(u[k] for k in rng.permutation(len(u))))
        self.assertFalse(order_pin(ctrl, heard))


def _stored_learner(seed=0):
    """A learner with a real store: two words on planted clusters, taught over ambiguous 2-thing scenes at lr 0.01."""
    rng = np.random.default_rng(seed)
    dirs = {w: rng.normal(size=Lr.RW_DIM) for w in ("a", "b", "c")}
    L = Lr.RWLearner(lr=0.01)
    seen = []
    for k in range(600):
        ws = rng.choice(list(dirs), size=2, replace=False)
        raw = np.stack([dirs[w] + 0.3 * rng.normal(size=Lr.RW_DIM) for w in ws])
        said = [str(ws[rng.integers(2)])]
        L.train_scene(raw, said, rng=np.random.default_rng(k))
        seen.append((raw, said, None))
    return L, seen, dirs, rng


class TestDiagonalRefusal(unittest.TestCase):
    def test_sigma_distance_band_from_the_store(self) -> None:
        L, seen, dirs, rng = _stored_learner()
        L.calibrate(seen)
        for w in ("a", "b"):
            j = L.index[w]
            Z = np.concatenate(L.store_z[j])
            R = np.concatenate(L.store_r[j])
            mu = L.prototype(j)
            sd = np.sqrt((R[:, None] * (Z - mu) ** 2).sum(0) / R.sum())
            sig = np.maximum(sd, 1e-3)
            st = L.refusal["diag"][w]
            self.assertTrue(np.allclose(st["mu"], mu))
            self.assertTrue(np.allclose(st["sigma"], sig))
            d = np.linalg.norm((Z - mu) / sig, axis=1)
            self.assertAlmostEqual(st["band"], Lr.weighted_quantile(d, R, 0.90), places=10)
            self.assertEqual(st["floor_count"], int((sd < 1e-3).sum()))
            # reading (ii): σ ≡ 1 — its band is S1a's own Euclidean band
            self.assertAlmostEqual(L.refusal["euclid"][w]["band"], L.band(j), places=10)

    def test_held_words_are_emitted_whole_and_a_far_thing_is_refused(self) -> None:
        L, seen, dirs, rng = _stored_learner()
        L.calibrate(seen)
        near = dirs["a"] + 0.3 * rng.normal(size=Lr.RW_DIM)
        em = L.what_is_this_readings(near[None, :])
        self.assertIn("a", em["law"])
        far = dirs["a"] + 25.0 * rng.normal(size=Lr.RW_DIM)
        em = L.what_is_this_readings(far[None, :])
        self.assertEqual(em["law"], [])                                        # «I don't know» by distance
        self.assertEqual(set(em), {"law", "i", "ii"})

    def test_phrase_none_is_conformal_095_on_two_hypothesis_scenes(self) -> None:
        L, seen, dirs, rng = _stored_learner()
        one = [(r[:1], w, None) for r, w, _ in seen[:30]]                     # 1-hypothesis scenes: not the population
        info = L.calibrate(seen + one)
        fits = []
        for raw, words, _ in seen:
            Z = L.stats.standardise(raw)
            fits.append(float(np.min(L.phrase_fit(Z, words, "diag"))))
        self.assertAlmostEqual(L.tau_none["diag"], Lr.conformal_upper(fits, 0.95), places=12)
        self.assertEqual(info["n"]["none"], len(seen))
        X = np.stack([dirs["a"], dirs["b"]]) + 0.3 * rng.normal(size=(2, Lr.RW_DIM))
        a = L.answer_point(X, ["a"], np.random.default_rng(0))
        f = L.phrase_fit(L.stats.standardise(X), ["a"], "diag")
        self.assertEqual(a["none"], bool(np.min(f) > L.tau_none["diag"]))
        self.assertEqual(set(a) >= {"point", "none", "none_i", "none_ii", "scores", "best"}, True)
        self.assertEqual(len(a["scores"]), 2)

    def test_young_word_keeps_s1as_answer(self) -> None:
        L, seen, dirs, rng = _stored_learner()
        x = dirs["a"] * 0 + 7.0
        L.train_scene(np.stack([x, dirs["b"]]), ["dax"], rng=np.random.default_rng(1))
        L.calibrate(seen)
        j = L.index["dax"]
        st = L.refusal["diag"]["dax"]
        self.assertEqual(st["young"], True)
        self.assertTrue(np.allclose(st["sigma"], 1.0))
        self.assertEqual(st["band"], L.band(j))


class TestLockInPin(unittest.TestCase):
    """§2: on the machinery toy (planted directions, ambiguous 2-thing scenes, seeds 11 / 12, 1,500 scenes) lr 0.01 reads
    > 0.90 AND lr 0.1 on the SAME scenes reads ≥ 0.10 below it — a test that would pass without the lock-in is refused."""

    def _world(self):
        rng = np.random.default_rng(11)
        dirs = {w: rng.normal(size=Lr.RW_DIM) for w in ("a", "b", "c", "d")}
        scenes = []
        for _ in range(1500):
            ws = rng.choice(list(dirs), size=2, replace=False)
            raw = np.stack([dirs[w] + 0.3 * rng.normal(size=Lr.RW_DIM) for w in ws])
            scenes.append((raw, [str(ws[rng.integers(2)])]))
        return dirs, scenes

    def _acc(self, lr, dirs, scenes):
        L = Lr.RWLearner(lr=lr)
        for k, (raw, ws) in enumerate(scenes):
            L.train_scene(raw, ws, rng=np.random.default_rng(k))
        rng = np.random.default_rng(12)
        ok = 0
        for k in range(200):
            ws = rng.choice(list(dirs), size=2, replace=False)
            raw = np.stack([dirs[w] + 0.3 * rng.normal(size=Lr.RW_DIM) for w in ws])
            ok += L.answer_point(raw, [str(ws[0])], np.random.default_rng(k))["point"] == 0
        return ok / 200

    def test_lr_001_learns_and_lr_01_locks_in(self) -> None:
        dirs, scenes = self._world()
        a001 = self._acc(0.01, dirs, scenes)
        a01 = self._acc(0.1, dirs, scenes)
        self.assertGreater(a001, 0.90)
        self.assertGreaterEqual(a001 - a01, 0.10, (a001, a01))


class FakeArm:
    """A stub arm for the production road: fixed held words and a table of read-back scores per phrase."""

    def __init__(self, held, table, nones=(), ear_utts=()):
        self._held, self.table, self.nones = held, table, set(nones)
        self.ear = Lr.Ear()
        for u in ear_utts:
            self.ear.hear(u)

    def held_words(self, x):
        return list(self._held)

    def answer_point(self, X, phrase, rng):
        s = np.asarray(self.table[tuple(phrase)], dtype=np.float64)
        return {"point": int(np.argmax(s)), "none": tuple(phrase) in self.nones, "scores": s.tolist(), "best": float(s.max())}


class TestProduction(unittest.TestCase):
    UTTS = (("big", "red", "circle"), ("red", "circle"), ("big", "circle"), ("small", "blue", "star"))

    def _rng(self):
        return lambda: np.random.default_rng(0)

    def test_shortest_accepted_with_the_largest_margin(self) -> None:
        table = {("circle",): [1.0, 1.0], ("red",): [2.0, 0.5], ("big",): [3.0, 0.0], ("red", "circle"): [5.0, 0.0],
                 ("big", "circle"): [4.0, 1.0], ("big", "red"): [9.0, 0.0], ("big", "red", "circle"): [9.0, 0.0]}
        arm = FakeArm(["circle", "red", "big"], table, ear_utts=self.UTTS)
        out = Lr.produce(arm, np.zeros((2, 3)), 0, self._rng())
        self.assertEqual(out["spoken"], ["big"])                                 # 1 word; margin 3.0 > red's 1.5
        self.assertEqual(out["readback_point"], 0)
        self.assertEqual(out["target"], 0)

    def test_a_tie_is_not_accepted_and_none_is_not_accepted(self) -> None:
        table = {("circle",): [1.0, 1.0], ("red",): [2.0, 0.5], ("red", "circle"): [5.0, 0.0]}
        arm = FakeArm(["circle", "red"], table, nones=[("red",)], ear_utts=self.UTTS)
        out = Lr.produce(arm, np.zeros((2, 3)), 0, self._rng())
        self.assertEqual(out["spoken"], ["red", "circle"])                     # circle ties; red fires «none»
        self.assertEqual(out["n_candidates"], 3)

    def test_exclusion_filters_never_co_heard_pairs(self) -> None:
        table = {("red",): [1.0, 1.0], ("blue",): [1.0, 1.0], ("blue", "red"): [9.0, 0.0], ("red", "blue"): [9.0, 0.0]}
        arm = FakeArm(["red", "blue"], table, ear_utts=self.UTTS)
        out = Lr.produce(arm, np.zeros((2, 3)), 0, self._rng())
        self.assertIsNone(out["spoken"])                                       # «red blue» never co-heard: not a candidate
        self.assertEqual(out["n_candidates"], 2)
        self.assertEqual(out["reason"], "no unique read-back")

    def test_reasons(self) -> None:
        arm = FakeArm([], {}, ear_utts=self.UTTS)
        self.assertEqual(Lr.produce(arm, np.zeros((2, 3)), 0, self._rng())["reason"], "no held word")
        arm = FakeArm(["red"], {("red",): [3.0, 0.0]}, nones=[("red",)], ear_utts=self.UTTS)
        self.assertEqual(Lr.produce(arm, np.zeros((2, 3)), 0, self._rng())["reason"], "none fired")

    def test_one_thing_in_view_points_uniquely(self) -> None:
        arm = FakeArm(["red"], {("red",): [3.0]}, ear_utts=self.UTTS)
        out = Lr.produce(arm, np.zeros((1, 3)), 0, self._rng())
        self.assertEqual(out["spoken"], ["red"])
        self.assertEqual(out["margin"], float("inf"))


class TestOracleSide(unittest.TestCase):
    TYPES = {"red": "colour", "blue": "colour", "circle": "shape", "star": "shape", "big": "size", "small": "size"}

    def test_the_oracle_hears_every_utterance_even_unseen(self) -> None:
        R = Lr.TypedLDAReader(0.3, self.TYPES)
        R.train_scene(None, ["big", "red", "circle"], n_view=2)
        self.assertEqual(R.names, [])
        self.assertEqual(R.ear.count("red", "circle"), 1)
        self.assertEqual(R.ear.key("big"), 0.0)

    def test_tau_point_is_conformal_095_over_two_hypothesis_scenes(self) -> None:
        rng = np.random.default_rng(3)
        mu = {w: rng.normal(size=144) * 3 for w in self.TYPES}
        R = Lr.TypedLDAReader(0.3, self.TYPES, point_level=0.95, point_min_view=2)
        for k in range(400):
            c, s = str(rng.choice(["red", "blue"])), str(rng.choice(["circle", "star"]))
            R.train_scene(mu[c] + mu[s] + rng.normal(size=144), [c, s], n_view=1 + (k % 3))
        info = R.prepare()
        pts = [sum(float(R.log_posterior(x[None, :], w)[0]) for w in ws)
               for x, ws, nv in zip(R.train_x, R.train_words, R.train_nview) if nv >= 2]
        self.assertAlmostEqual(R.tau_point, Lr.conformal_lower(pts, 0.95), places=12)
        self.assertEqual(info["n"]["point"], len(pts))
        a = R.answer_point(np.stack([mu["red"] + mu["circle"], mu["blue"] + mu["star"]]), ["red", "circle"],
                           np.random.default_rng(0))
        self.assertEqual(len(a["scores"]), 2)
        fit = R.colour_fit(mu["red"] + mu["circle"])
        self.assertEqual(set(fit), {"red", "blue"})
        self.assertLess(fit["red"], fit["blue"])


if __name__ == "__main__":
    unittest.main()
