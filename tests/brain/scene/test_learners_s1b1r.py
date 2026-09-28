# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:06 +0400 — PREREG-S1B1R §1 (sha 879a22fb…; AMENDMENT 1 a198f0b4…), test-first (red on
# scene-s1b1 7706371): (a) the ear's TYPE COVER — greedy largest maximal clique of the MATURE words' exclusion graph, ties to
# the lexicographically smallest sorted tuple, a lone word its own type; (b) THE READER — the responsibility-weighted pooled
# covariance per learned type about each word's prototype, Λ_T = [(1 − ε)Σ_T + ε(tr Σ_T / d) I]⁻¹, d_w, B_w = the weighted
# 0.90 quantile over the word's own store (pinned: weighted = unweighted when every r = 1); (c) production waits for
# maturity (a word of < 3 meetings is never EMITTED, and still POINTS); (d) «none» = S1a's τ_point (S1b-1's none_i); (e)
# the mouth says what it BELIEVES (believed names per learned type, SAYABLE by the band, believed-UNIQUE categorically,
# accepted with the read-back first and «none» off, the shortest, ties by margin → the one-alone type → the order key,
# the decline reasons); the roads stay selectable (S1b-1's own road is byte-for-byte S1b-1's).
from __future__ import annotations

import unittest

import numpy as np

from brain.scene import learners as Lr
from brain.scene import world as W

SHAPES, COLOURS, SIZES = list(W.SHAPES), list(W.COLOUR_NAMES), list(W.SIZE_NAMES)


def _world_ear(heldout=W.HELDOUT, extra=()):
    """An ear that heard the parent's templates over the trained pairs: every cross-type pair co-heard except the six
    held-out colour × shape pairs (c = 0), words of one type never together."""
    e = Lr.Ear()
    for s in SHAPES:
        e.hear((s,))
        for z in SIZES:
            e.hear((z, s))
        for c in COLOURS:
            if (s, c) in heldout:
                continue
            e.hear((c, s))
            for z in SIZES:
                e.hear((z, c, s))
    for u in extra:
        e.hear(u)
    return e


class TestEarCover(unittest.TestCase):
    def test_the_six_heldout_mixed_cliques_do_not_win(self) -> None:
        e = _world_ear()
        self.assertEqual(e.count("square", "red"), 0)                           # a held-out pair: an exclusion edge
        cover = e.cover(SHAPES + COLOURS + SIZES)
        self.assertEqual(cover, [tuple(sorted(SHAPES)), tuple(sorted(COLOURS)), tuple(sorted(SIZES))])

    def test_a_mixed_clique_that_outranks_a_true_type_is_caught_by_the_gate(self) -> None:
        """«square» never co-heard with any colour: {5 colours + square} is a clique of 6 that ties the shapes and wins the
        tie (('blue', …) < ('circle', …)); the cover is wrong and gate step 3's check must report a MISS."""
        from brain.scene import run as R
        e = _world_ear(heldout=tuple((s, c) for s, c in W.ALLOWED if s == "square") + W.HELDOUT)
        cover = e.cover(SHAPES + COLOURS + SIZES)
        self.assertEqual(cover[0], tuple(sorted(COLOURS + ["square"])))
        chk = R.types_check(cover, SHAPES + COLOURS + SIZES)
        self.assertFalse(chk["pass"])
        self.assertTrue(R.types_check(_world_ear().cover(SHAPES + COLOURS + SIZES), SHAPES + COLOURS + SIZES)["pass"])

    def test_a_lone_word_is_its_own_type_and_ties_go_lexicographic(self) -> None:
        e = Lr.Ear()
        for u in (("a", "x"), ("a", "y"), ("b", "x"), ("b", "y"), ("c", "x"), ("c", "y"), ("a", "z"), ("b", "z"), ("c", "z"),
                  ("x", "q"), ("y", "q"), ("z", "q"), ("a", "q"), ("b", "q"), ("c", "q")):
            e.hear(u)
        # edges (never co-heard): a-b, a-c, b-c, x-y, x-z, y-z → two cliques of 3 tie; «q» co-heard with all: alone
        self.assertEqual(e.cover(["q", "z", "y", "x", "c", "b", "a"]), [("a", "b", "c"), ("x", "y", "z"), ("q",)])

    def test_alone_counts_the_one_word_utterances(self) -> None:
        e = _world_ear()
        self.assertEqual(e.alone["circle"], 1)
        self.assertNotIn("red", e.alone)
        e.hear(("dax",))
        self.assertEqual(e.alone["dax"], 1)


def _store_learner(seed=0, n=600, lr=0.01):
    """A learner with a real store over a two-type toy (words a0..a2 × b0..b1, one thing a scene, both words said)."""
    rng = np.random.default_rng(seed)
    A = {f"a{i}": rng.normal(size=Lr.RW_DIM) * 2 for i in range(3)}
    B = {f"b{i}": rng.normal(size=Lr.RW_DIM) * 2 for i in range(2)}
    L = Lr.RWLearner(lr=lr)
    seen = []
    for k in range(n):
        a, b = f"a{rng.integers(3)}", f"b{rng.integers(2)}"
        raw = (A[a] + B[b] + 0.5 * rng.normal(size=Lr.RW_DIM))[None, :]
        L.train_scene(raw, [a, b], rng=np.random.default_rng(k))
        seen.append((raw, [a, b], None))
    return L, seen, A, B, rng


class TestReader(unittest.TestCase):
    def test_types_are_the_ears_cover_over_the_mature_words(self) -> None:
        L, seen, A, B, rng = _store_learner()
        L.train_scene(rng.normal(size=(1, Lr.RW_DIM)), ["dax"], rng=np.random.default_rng(7))   # one meeting: young
        L.calibrate(seen)
        info = L.calibrate_r(0.3)
        self.assertEqual(info["types"], [["a0", "a1", "a2"], ["b0", "b1"]])
        self.assertNotIn("dax", L.mature_words())
        self.assertEqual(info["one_alone"], None)                              # no one-word utterance of a mature word

    def test_pooled_covariance_metric_and_band(self) -> None:
        L, seen, A, B, rng = _store_learner()
        L.calibrate(seen)
        eps = 0.3
        L.calibrate_r(eps)
        st = L.reader["ear"]
        for k, T in enumerate(st["types"]):
            num, den = np.zeros((Lr.RW_DIM, Lr.RW_DIM)), 0.0
            for w in T:
                j = L.index[w]
                Z = np.concatenate(L.store_z[j])
                R = np.concatenate(L.store_r[j])
                D = Z - L.prototype(j)
                num += (D * R[:, None]).T @ D
                den += R.sum()
            S = num / den
            lam = np.linalg.inv((1 - eps) * S + eps * np.trace(S) / Lr.RW_DIM * np.eye(Lr.RW_DIM))
            self.assertTrue(np.allclose(st["lam"][k], lam, rtol=1e-9, atol=1e-12))
            for w in T:
                j = L.index[w]
                Z = np.concatenate(L.store_z[j])
                R = np.concatenate(L.store_r[j])
                D = Z - L.prototype(j)
                d = np.sqrt(np.einsum("ij,jk,ik->i", D, lam, D))
                self.assertAlmostEqual(st["word"][w]["band"], Lr.weighted_quantile(d, R, 0.90), places=9)

    def test_weighted_equals_unweighted_when_every_r_is_one(self) -> None:
        """The pin: with every responsibility 1, the weighted pooled covariance is the plain pooled covariance about each
        word's prototype (its plain mean) — built here from a hand-made store with no learner arithmetic."""
        rng = np.random.default_rng(5)
        L = Lr.RWLearner(lr=0.01)
        groups = {"p": rng.normal(size=(7, Lr.RW_DIM)) + 3, "q": rng.normal(size=(11, Lr.RW_DIM)) - 1}
        for w, Z in groups.items():
            j = L._add_word(w)
            L.store_z[j] = [Z[:3], Z[3:]]
            L.store_r[j] = [np.ones(3), np.ones(len(Z) - 3)]
            L.proto_sum[j] = Z.sum(axis=0)
            L.proto_w[j] = float(len(Z))
            L.meetings[j] = 5
        S = Lr.pooled_covariance(L, ["p", "q"])
        plain = sum((Z - Z.mean(0)).T @ (Z - Z.mean(0)) for Z in groups.values()) / sum(len(Z) for Z in groups.values())
        self.assertTrue(np.allclose(S, plain, rtol=1e-10, atol=1e-12))
        # and a planted non-uniform r moves it (the pin is not vacuous)
        L.store_r[L.index["p"]] = [np.full(3, 0.2), np.ones(4)]
        self.assertFalse(np.allclose(Lr.pooled_covariance(L, ["p", "q"]), plain))

    def test_what_is_this_reader_emits_mature_words_only_and_refuses_far_things(self) -> None:
        L, seen, A, B, rng = _store_learner()
        x = rng.normal(size=Lr.RW_DIM)
        L.train_scene(x[None, :], ["dax"], rng=np.random.default_rng(3))
        L.calibrate(seen)
        L.calibrate_r(0.3)
        road = Lr.RWRoad(L)
        near = A["a1"] + B["b0"]                                               # the class's own mean: well inside
        em = road.held_words(near)
        self.assertIn("a1", em)
        self.assertIn("b0", em)
        self.assertNotIn("dax", road.held_words(x))                            # (c): the young word is never emitted …
        self.assertIn("dax", L.held_words(x))                                  # … though S1b-1's road holds it
        far = A["a1"] + 30.0 * rng.normal(size=Lr.RW_DIM)
        self.assertEqual(road.held_words(far), [])


class TestRoads(unittest.TestCase):
    def test_s1b1s_road_is_s1b1s_answer(self) -> None:
        L, seen, A, B, rng = _store_learner()
        L.calibrate(seen)
        L.calibrate_r(0.3)
        X = np.stack([A["a0"] + B["b0"], A["a1"] + B["b1"]]) + 0.5 * rng.normal(size=(2, Lr.RW_DIM))
        old = Lr.RWRoad(L, types=None, band="diag", mature=False, none="dist")
        self.assertEqual(old.held_words(X[0]), L.held_words(X[0]))
        a, b = L.answer_point(X, ["a0"], np.random.default_rng(0)), old.answer_point(X, ["a0"], np.random.default_rng(0))
        self.assertEqual(a, b)
        law = Lr.RWRoad(L).answer_point(X, ["a0"], np.random.default_rng(0))
        self.assertEqual(law["none"], a["none_i"])                             # (d): «none» is S1a's τ_point
        self.assertEqual({k: v for k, v in law.items() if k != "none"}, {k: v for k, v in a.items() if k != "none"})
        f = lambda: np.random.default_rng(1)
        self.assertEqual(Lr.produce(old, X, 0, f), Lr.produce(L, X, 0, f))        # the old mouth over the old road = S1b-1's

    def test_a_young_word_still_points(self) -> None:
        L, seen, A, B, rng = _store_learner()
        x = rng.normal(size=Lr.RW_DIM) * 3
        L.train_scene(np.stack([x, A["a0"] + B["b0"]]), ["dax"], rng=np.random.default_rng(2))
        L.calibrate(seen)
        L.calibrate_r(0.3)
        j = L.index["dax"]
        self.assertLess(L.meetings[j], Lr.P_FROM_MEETING)
        X2 = np.stack([x, A["a2"] + B["b1"]])
        a = Lr.RWRoad(L).answer_point(X2, ["dax"], np.random.default_rng(0))
        self.assertIsNotNone(a["point"])                                       # comprehension before production
        self.assertEqual(a["point"], L.answer_point(X2, ["dax"], np.random.default_rng(0))["point"])   # S1a's answer


class FakeRoad:
    """A stub road for the believed-names mouth: per type the believed name of every hypothesis, the sayable words of the
    target, a read-back table per phrase (scores over hypotheses; the point = argmax), «none» per phrase, an ear."""

    def __init__(self, types, believed, sayable, table, nones=(), ear_utts=(), one_alone=None):
        self._types, self._believed, self._sayable = types, believed, set(sayable)
        self.table, self.nones, self._one = table, set(nones), one_alone
        self.ear = Lr.Ear()
        for u in ear_utts:
            self.ear.hear(u)

    def types(self):
        return self._types

    def believed(self, X):
        return self._believed

    def sayable(self, x, w):
        return w in self._sayable

    def one_alone(self):
        return self._one

    def answer_point(self, X, phrase, rng):
        s = np.asarray(self.table[tuple(phrase)], dtype=np.float64)
        return {"point": Lr.pick(s, rng, "max"), "none": tuple(phrase) in self.nones, "scores": s.tolist(),
                "best": float(s.max())}


class TestBelievedMouth(unittest.TestCase):
    UTTS = (("big", "red", "circle"), ("red", "circle"), ("big", "circle"), ("circle",), ("star",), ("small", "blue", "star"))
    TYPES = [("circle", "star"), ("blue", "red"), ("big", "small")]

    def _f(self):
        return lambda: np.random.default_rng(0)

    def test_two_things_with_the_same_believed_shape_make_the_shape_word_non_unique(self) -> None:
        # target 0 = a big red circle; hypothesis 1 = a small blue circle: «circle» is not unique, «red» is
        believed = [["circle", "circle"], ["red", "blue"], ["big", "small"]]
        table = {("red",): [2.0, -3.0], ("big",): [1.0, 0.5], ("red", "circle"): [1.0, -4.0], ("big", "circle"): [0.5, 0.1],
                 ("big", "red"): [3.0, -2.5], ("big", "red", "circle"): [2.0, -5.0]}
        road = FakeRoad(self.TYPES, believed, ["circle", "red", "big"], table, ear_utts=self.UTTS, one_alone=0)
        out = Lr.produce_believed(road, np.zeros((2, 3)), 0, self._f())
        self.assertEqual(out["spoken"], ["red"])                               # 1 word; margin 5.0 > big's 0.5
        self.assertEqual(out["n_unique"], 6)                                   # every subset but «circle» alone
        self.assertEqual((out["readback_point"], out["target"]), (0, 0))
        self.assertEqual(out["believed"], {"0": "circle", "1": "red", "2": "big"})

    def test_a_second_word_when_no_single_one_is_believed_unique(self) -> None:
        # three things: 1 shares the believed shape and colour, 2 shares the believed shape and size → «big red» (ordered)
        believed = [["circle", "circle", "circle"], ["red", "red", "blue"], ["big", "small", "big"]]
        table = {("big", "red"): [3.0, 0.0, 0.5], ("big", "red", "circle"): [2.0, -1.0, -1.0]}
        road = FakeRoad(self.TYPES, believed, ["circle", "red", "big"], table, ear_utts=self.UTTS, one_alone=0)
        out = Lr.produce_believed(road, np.zeros((3, 3)), 0, self._f())
        self.assertEqual(out["spoken"], ["big", "red"])                        # the order key: size < colour
        self.assertEqual(out["n_unique"], 2)

    def test_a_silent_type_the_readback_and_none(self) -> None:
        believed = [["circle", "star"], ["red", "red"], ["big", "big"]]
        table = {("circle",): [1.0, 2.0]}                                      # the read-back points elsewhere
        road = FakeRoad(self.TYPES, believed, ["circle"], table, ear_utts=self.UTTS, one_alone=0)
        out = Lr.produce_believed(road, np.zeros((2, 3)), 0, self._f())
        self.assertIsNone(out["spoken"])
        self.assertEqual(out["reason"], "the read-back")
        road = FakeRoad(self.TYPES, believed, ["circle"], {("circle",): [2.0, 1.0]}, nones=[("circle",)], ear_utts=self.UTTS)
        self.assertEqual(Lr.produce_believed(road, np.zeros((2, 3)), 0, self._f())["reason"], "none")
        road = FakeRoad(self.TYPES, believed, [], {}, ear_utts=self.UTTS)
        self.assertEqual(Lr.produce_believed(road, np.zeros((2, 3)), 0, self._f())["reason"], "no sayable word")
        believed = [["circle", "circle"], ["red", "red"], ["big", "big"]]
        road = FakeRoad(self.TYPES, believed, ["circle", "red", "big"], {}, ear_utts=self.UTTS)
        self.assertEqual(Lr.produce_believed(road, np.zeros((2, 3)), 0, self._f())["reason"], "no believed-unique phrase")

    def test_one_hypothesis_ties_go_to_the_one_alone_type_then_the_order_key(self) -> None:
        believed = [["circle"], ["red"], ["big"]]
        table = {("circle",): [1.0], ("red",): [1.0], ("big",): [1.0], ("red", "circle"): [1.0], ("big", "circle"): [1.0],
                 ("big", "red"): [1.0], ("big", "red", "circle"): [1.0]}
        road = FakeRoad(self.TYPES, believed, ["circle", "red", "big"], table, ear_utts=self.UTTS, one_alone=0)
        out = Lr.produce_believed(road, np.zeros((1, 3)), 0, self._f())
        self.assertEqual(out["spoken"], ["circle"])                            # every margin +∞: the type heard alone
        self.assertEqual(out["margin"], float("inf"))
        road = FakeRoad(self.TYPES, believed, ["circle", "red", "big"], table, ear_utts=self.UTTS, one_alone=None)
        self.assertEqual(Lr.produce_believed(road, np.zeros((1, 3)), 0, self._f())["spoken"], ["big"])   # the order key

    def test_an_exact_tie_at_the_readback_is_broken_by_the_items_generator(self) -> None:
        believed = [["circle", "star"], ["red", "blue"], ["big", "small"]]
        table = {("circle",): [1.0, 1.0]}
        road = FakeRoad(self.TYPES, believed, ["circle"], table, ear_utts=self.UTTS, one_alone=0)
        spoken = [Lr.produce_believed(road, np.zeros((2, 3)), 0, lambda s=s: np.random.default_rng(s))["spoken"] for s in range(40)]
        self.assertIn(["circle"], spoken)                                      # no «unique maximum» clause (Fable's edit)
        self.assertIn(None, spoken)


if __name__ == "__main__":
    unittest.main()
