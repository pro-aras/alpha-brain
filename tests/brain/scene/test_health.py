# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:30 +0400 — PREREG-TMEM2 (final 4d03f79, sha b785b54f…) §2–§4, §7 step 2,
# test-first (red on scene-s1b1r 01e784b: brain/scene/health.py does not exist there): the HEALTH row kept without the world —
# a CLAIM (the LAW road's own step 1, read-only), ITS GRADE through the learner's own attribution FILED UNDER THE CLAIMED
# WORD (the said word's MISSED count apart), cal_20 over the last 20 graded, the 20-claim windows, Δ and the drift READING
# in both forms (median |Δ|, and floored at 1/20); the gate (n_graded ≥ 20 AND cal_20 ≥ 0.80; «no row» / «not held lately»);
# the road with ONE difference in `sayable` (the refused words recorded); the null's derangement; ECE and type-2 AUROC;
# the row's toy (gate step 2: A 95 % kept, B 50 % refused, the deranged null flips them, an ungraded claim moves nothing).
from __future__ import annotations

import copy
import unittest

import numpy as np

from brain.scene import health as H
from brain.scene import learners as Lr


def _row(outcomes, claims=None):
    r = H.HealthRow()
    r.outcomes = list(outcomes)
    r.n_claims = len(outcomes) if claims is None else claims
    return r


class TestRow(unittest.TestCase):
    def test_cal20_windows_deltas(self) -> None:
        r = _row([1] * 20 + [1] * 15 + [0] * 5 + [1] * 20 + [1] * 7)
        self.assertEqual(r.n_graded, 67)
        self.assertEqual(r.windows(), [1.0, 0.75, 1.0])                         # the partial tail (7) is no window
        self.assertEqual(r.deltas(), [-0.25, 0.25])
        self.assertEqual(r.delta_last(), 0.25)
        self.assertEqual(r.median_abs_delta(), 0.25)
        self.assertEqual(r.cal20(), 1.0)                                         # the LAST 20 graded (sliding)
        r2 = _row([1, 0, 1])
        self.assertAlmostEqual(r2.cal20(), 2 / 3)
        self.assertEqual((r2.windows(), r2.deltas(), r2.delta_last(), r2.median_abs_delta()), ([], [], None, None))
        self.assertIsNone(H.HealthRow().cal20())

    def test_the_drift_reading_in_both_forms(self) -> None:
        """Fable's edit: a word confirmed 100 % has median |Δ| = 0, so the unfloored clause fires on ONE miss; the 1/20
        floor does not. Both are READINGS (out of the gate)."""
        r = _row([1] * 60 + [1] * 19 + [0])                                     # windows 1, 1, 1, 0.95
        self.assertEqual(r.deltas(), [0.0, 0.0, -0.050000000000000044])
        self.assertEqual(r.drift_firings(), 1)
        self.assertEqual(r.drift_firings(floor=H.DRIFT_FLOOR), 0)
        self.assertEqual(_row([1] * 20 + [0] * 20).drift_firings(), 0)          # the first Δ never fires (|Δ| is its own median)

    def test_an_ungraded_claim_moves_nothing_but_n_claims(self) -> None:
        r = _row([1] * 25)
        before = (r.n_graded, r.cal20(), H.row_gate(r))
        r.n_claims += 1
        self.assertEqual((r.n_graded, r.cal20(), H.row_gate(r)), before)


class TestGrades(unittest.TestCase):
    REC = {"types": [("circle", "star"), ("blue", "red")],
           "believed": [["circle", "star", "circle"], ["red", "red", "blue"]],
           "confident": [[True, True, False], [True, False, True]]}

    def test_filed_under_the_claimed_word(self) -> None:
        # «star» said about h0, believed a circle (confident) → a REFUTATION filed under «circle»; «red» said about h1 → the
        # claim about h1 in the colour type was not confident → ungraded; «big» is of no learned type → ungraded
        g = H.grades(self.REC, {"star": 0, "red": 1, "big": 0})
        self.assertEqual(g, [("circle", False, "star")])
        g = H.grades(self.REC, {"circle": 0, "blue": 2})
        self.assertEqual(g, [("circle", True, "circle"), ("blue", True, "blue")])
        self.assertEqual(H.grades(self.REC, {"star": None}), [])                # never attributed: ungraded
        self.assertEqual(H.grades(self.REC, {"circle": 2}), [])                 # the claim about h2 was not confident

    def test_the_book_counts_claims_grades_and_the_said_words_misses(self) -> None:
        b = H.HealthBook()
        b.add_claims(self.REC)
        self.assertEqual({w: r.n_claims for w, r in b.rows.items()}, {"circle": 1, "star": 1, "red": 1, "blue": 1})
        b.add_grades([("circle", False, "star"), ("circle", True, "circle")])
        self.assertEqual(b.rows["circle"].outcomes, [0, 1])
        self.assertEqual(b.rows["star"].missed, 1)
        self.assertEqual(b.rows["star"].outcomes, [])


class TestGate(unittest.TestCase):
    def test_row_gate(self) -> None:
        self.assertEqual(H.row_gate(None), (False, H.REASON_NO_ROW))
        self.assertEqual(H.row_gate(_row([1] * 19)), (False, H.REASON_NO_ROW))
        self.assertEqual(H.row_gate(_row([1] * 16 + [0] * 4)), (True, None))    # 0.80 exactly: open
        self.assertEqual(H.row_gate(_row([1] * 15 + [0] * 5)), (False, H.REASON_NOT_HELD))

    def test_book_gate_the_null_and_the_accuracy_gate(self) -> None:
        book = H.HealthBook()
        book.rows = {"a": _row([1] * 20), "b": _row([0] * 20)}
        g, n = H.book_gate(book), H.book_gate(book, {"a": "b", "b": "a"})
        self.assertEqual((g("a")[0], g("b")[0], n("a")[0], n("b")[0]), (True, False, False, True))
        self.assertEqual(g("c"), (False, H.REASON_NO_ROW))
        acc = H.accuracy_gate({"a": 0.9, "b": 0.7, "c": None})
        self.assertEqual((acc("a"), acc("b"), acc("c"), acc("d")),
                         ((True, None), (False, H.REASON_NOT_HELD), (False, H.REASON_NO_ROW), (False, H.REASON_NO_ROW)))


class TestRowToy(unittest.TestCase):
    """§7 step 2: two words, A's claims confirmed 95 %, B's 50 %, 200 claims each, seeds 0–2."""

    def test_the_toy(self) -> None:
        for seed in (0, 1, 2):
            t = H.row_toy(seed)
            self.assertEqual(t["keeps"], {"A": True, "B": False}, t)
            self.assertEqual(t["null"], {"A": False, "B": True}, t)
            self.assertTrue(t["ungraded_moves_nothing"], t)
            self.assertEqual(t["n_graded"], {"A": 200, "B": 200})


def _store_learner(seed=0, n=500):
    rng = np.random.default_rng(seed)
    A = {f"a{i}": rng.normal(size=Lr.RW_DIM) * 2 for i in range(3)}
    B = {f"b{i}": rng.normal(size=Lr.RW_DIM) * 2 for i in range(2)}
    L = Lr.RWLearner(lr=0.01)
    seen = []
    for k in range(n):
        a, b = f"a{rng.integers(3)}", f"b{rng.integers(2)}"
        raw = (A[a] + B[b] + 0.5 * rng.normal(size=Lr.RW_DIM))[None, :]
        L.train_scene(raw, [a, b], rng=np.random.default_rng(k))
        seen.append((raw, [a, b], None))
    L.calibrate(seen)
    L.calibrate_r(0.3)
    return L, A, B, rng


class TestHealthRoad(unittest.TestCase):
    def test_one_difference_in_sayable_and_the_refusals_recorded(self) -> None:
        L, A, B, rng = _store_learner()
        x = A["a1"] + B["b0"]
        law = Lr.RWRoad(L)
        self.assertTrue(law.sayable(x, "a1") and law.sayable(x, "b0"))
        road = H.HealthRoad(L, lambda w: (False, H.REASON_NOT_HELD) if w == "a1" else (True, None))
        road.begin_item()
        self.assertFalse(road.sayable(x, "a1"))
        self.assertTrue(road.sayable(x, "b0"))
        self.assertFalse(road.sayable(x, "a0"))                                 # the band refuses: nothing recorded
        self.assertEqual(road.end_item(), [{"word": "a1", "why": H.REASON_NOT_HELD}])
        self.assertEqual(road.end_item(), [])
        self.assertEqual((road.mode, road.band, road.mature, road.none), ("ear", "reader", True, "tau_point"))

    def test_an_open_gate_is_the_law_word_for_word(self) -> None:
        L, A, B, rng = _store_learner()
        X = np.stack([A["a0"] + B["b0"], A["a1"] + B["b0"], A["a0"] + B["b1"]]) + 0.3 * rng.normal(size=(3, Lr.RW_DIM))
        open_road = H.HealthRoad(L, lambda w: (True, None))
        for t in range(3):
            f = lambda: np.random.default_rng(t)
            self.assertEqual(Lr.produce_believed(open_road, X, t, f), Lr.produce_believed(Lr.RWRoad(L), X, t, f))
        shut = H.HealthRoad(L, lambda w: (False, H.REASON_NO_ROW))
        shut.begin_item()
        out = Lr.produce_believed(shut, X, 0, lambda: np.random.default_rng(0))
        self.assertIsNone(out["spoken"])
        self.assertEqual(out["reason"], "no sayable word")                      # the mouth's own reason; the road records why
        self.assertTrue(all(r["why"] == H.REASON_NO_ROW for r in shut.end_item()))


class TestClaimsAndAttributionAreReadOnly(unittest.TestCase):
    def test_claims_and_attribution_change_no_state(self) -> None:
        L, A, B, rng = _store_learner()
        X = np.stack([A["a0"] + B["b0"], A["a2"] + B["b1"]])
        snap = copy.deepcopy(L)
        rec = H.claims(Lr.RWRoad(L), X)
        self.assertEqual(len(rec["types"]), 2)
        self.assertEqual([len(v) for v in rec["believed"]], [2, 2])
        law = Lr.RWRoad(L)
        for k in range(2):
            for h in range(2):
                self.assertEqual(rec["confident"][k][h], law.sayable(X[h], rec["believed"][k][h]))
        L.train_scene(X, ["a0", "b0"], rng=np.random.default_rng(99))
        snap.train_scene(X, ["a0", "b0"], rng=np.random.default_rng(99))
        att = H.attribution(L, X, ["a0", "b0"], [])
        self.assertEqual(att, {"a0": int(np.argmax(L.store_r[L.index["a0"]][-1])), "b0": int(np.argmax(L.store_r[L.index["b0"]][-1]))})
        for name in ("V", "b", "meetings", "proto_sum", "proto_w"):
            self.assertTrue(np.array_equal(getattr(L, name), getattr(snap, name)), name)
        self.assertTrue(np.array_equal(L.stats.mean, snap.stats.mean) and L.stats.n == snap.stats.n)
        self.assertEqual(L.summary(), snap.summary())

    def test_a_first_meeting_is_attributed_to_the_episodic_thing(self) -> None:
        L, A, B, rng = _store_learner()
        X = np.stack([A["a0"] + B["b0"], rng.normal(size=Lr.RW_DIM) * 4])
        L.train_scene(X, ["dax"], rng=np.random.default_rng(5))
        att = H.attribution(L, X, ["dax"], ["dax"])
        z = L.store_z[L.index["dax"]][0][0]
        self.assertTrue(np.array_equal(L.stats.standardise(X)[att["dax"]], z))


class TestNullAndGraders(unittest.TestCase):
    def test_derangement(self) -> None:
        words = ["red", "big", "circle", "small", "blue"]
        p = H.derange(words, np.random.default_rng(7))
        self.assertEqual(sorted(p), sorted(words))
        self.assertEqual(sorted(p.values()), sorted(words))
        self.assertTrue(all(p[w] != w for w in words))
        self.assertEqual(p, H.derange(list(reversed(words)), np.random.default_rng(7)))   # order-free: the words are sorted

    def test_ece_and_the_curve(self) -> None:
        e = H.ece([0.95, 0.95, 0.95, 0.95, 0.35, 0.35], [1, 1, 1, 0, 0, 1])
        # bin 9: conf 0.95, acc 0.75 (n 4); bin 3: conf 0.35, acc 0.5 (n 2) → ECE = 4/6·0.20 + 2/6·0.15
        self.assertAlmostEqual(e["ece"], 4 / 6 * 0.2 + 2 / 6 * 0.15)
        self.assertEqual((e["n"], e["n_err"]), (6, 2))
        self.assertEqual([c["bin"] for c in e["curve"]], [3, 9])
        self.assertEqual(H.ece([1.0, 0.8, 0.3], [1, 1, 0])["curve"][-1]["bin"], 9)   # 1.0 sits in the last bin
        self.assertIsNone(H.ece([], [])["ece"])

    def test_type2_auroc(self) -> None:
        self.assertAlmostEqual(H.auroc([0.9, 0.8, 0.8, 0.1], [1, 1, 0, 0]), 3.5 / 4)
        self.assertIsNone(H.auroc([0.9, 0.8], [1, 1]))
        self.assertEqual(H.auroc([0.5, 0.5, 0.5], [1, 0, 1]), 0.5)


if __name__ == "__main__":
    unittest.main()
