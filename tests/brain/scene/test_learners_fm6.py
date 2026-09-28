# edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:18 +0400 — PREREG-BRAIN-IN-BODY AMENDMENT 1 §2 (sha 45abeca2…), test-first (red on
# brain-organ-fm6 52d7662): F-M6 lives in RWLearner.answer_point's choice of `point` ALONE, behind the attribute `young_rule`
# (class default "band" = the law). A pointing ask whose phrase is ONE young word (meetings < p_from) points at the hypothesis
# NEAREST the word's prototype under reader["ear"]["lam"][one_alone] (DIAG-M6's distance); an exact tie → the item's generator;
# four fall-backs to the law (no reader · one_alone None · that type's Λ None · proto_w 0). best / scores / none / none_i /
# none_ii and their fits stay the law's numbers; `young_d` and `point_rule` appear ONLY when the rule acted. calibrate's τ_point
# (it reads logp_answer, never answer_point) is equal with the rule on and off.
"""tests/brain/scene/test_learners_fm6.py — F-M6 on a small synthetic learner (three shapes, two colours, one «dax» meeting)."""
from __future__ import annotations

import copy
import unittest

import numpy as np

from brain.scene import learners as Lr

SH, CO = ("sa", "sb", "sc"), ("cx", "cy")
SLOTS = ((2.0, 2.0), (2.0, 9.0), (9.0, 5.0))
DAX_AT = 2                  # early: the known words still carry an infinite episodic band, so dax's band is +inf and the LAW ties every thing
N = 150


def _protos(seed: int = 5):
    r = np.random.default_rng(seed)
    return ({s: r.normal(size=144) * 2.0 for s in SH}, {c: r.normal(size=144) for c in CO}, r.normal(size=144) * 2.0)


def _thing(ps, pc, pdax, s, c, k, r):
    v = (pdax if s == "dax" else ps[s]) + pc[c] + r.normal(size=144) * 0.3
    return Lr.rw_input(v, SLOTS[k])


def toy_learner(young_rule=None, seed: int = 5):
    """The same life for every call with one seed: shapes said alone or with a colour (the ear's one-alone type is the shapes),
    ONE «dax» meeting (a lone moon-like thing at scene DAX_AT), calibrated at the end (calibrate + calibrate_r(0.3))."""
    ps, pc, pdax = _protos(seed)
    r = np.random.default_rng(seed + 1)
    L = Lr.RWLearner(lr=0.01)
    if young_rule is not None:
        L.young_rule = young_rule
    seen = []
    for i in range(N):
        if i == DAX_AT:
            raw = np.stack([_thing(ps, pc, pdax, "dax", CO[0], 0, r)])
            words = ["dax"]
        else:
            m = 1 + i % 3
            things = [(SH[int(r.integers(3))], CO[int(r.integers(2))]) for _ in range(m)]
            raw = np.stack([_thing(ps, pc, pdax, s, c, k, r) for k, (s, c) in enumerate(things)])
            s, c = things[int(r.integers(m))]
            words = [c, s] if i % 2 == 0 else [s]
        L.train_scene(raw, words, rng=np.random.default_rng(1000 + i))
        seen.append((raw, words, None))
    cal = L.calibrate(seen)
    cr = L.calibrate_r(0.3)
    return L, seen, cal, cr


def test_scenes(n: int = 24, seed: int = 5):
    """Test canvases with 2–3 things, one of them «dax»-shaped (its colour random), the rest trained things."""
    ps, pc, pdax = _protos(seed)
    r = np.random.default_rng(seed + 99)
    out = []
    for i in range(n):
        m = 2 + i % 2
        things = [(SH[int(r.integers(3))], CO[int(r.integers(2))]) for _ in range(m)]
        things[int(r.integers(m))] = ("dax", CO[int(r.integers(2))])
        out.append(np.stack([_thing(ps, pc, pdax, s, c, k, r) for k, (s, c) in enumerate(things)]))
    return out


PHRASES = [["dax"], ["sa"], ["sb"], ["cx"], ["cx", "sa"], ["cy", "sc"], ["dax", "cx"], ["cx", "dax"], ["never"], ["sa", "sa"]]


def ask(L, raw, phrase, i=0, rule=None):
    """One answer under the rule `rule` (None = the class default, the law) on the SAME learned state, with the item's own
    generator (a fresh one per call)."""
    M = L
    if rule is not None:
        M = copy.copy(L)
        M.young_rule = rule
    return M.answer_point(raw, phrase, np.random.default_rng(7000 + i))


def reader_d(L, raw, w):
    """DIAG-M6's distance (tools/brain/diag/diag_m6_metric.py), computed here independently of the fix."""
    st = L.reader["ear"]
    lam = st["lam"][st["one_alone"]]
    E = L.stats.standardise(np.atleast_2d(raw)) - L.prototype(L.index[w])[None, :]
    return np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", E, lam, E), 0.0))


class TestToy(unittest.TestCase):
    """The toy is what the tests below need: dax young with a prototype, the shapes the one-alone type with a Λ."""

    @classmethod
    def setUpClass(cls):
        cls.L, cls.seen, cls.cal, cls.cr = toy_learner()

    def test_the_toy_holds_a_young_dax_and_a_one_alone_shape_type(self):
        L = self.L
        j = L.index["dax"]
        self.assertEqual(int(L.meetings[j]), 1)
        self.assertLess(int(L.meetings[j]), L.p_from)
        self.assertGreater(float(L.proto_w[j]), 0.0)
        st = L.reader["ear"]
        self.assertIsNotNone(st["one_alone"])
        self.assertEqual(sorted(st["types"][st["one_alone"]]), sorted(SH))
        self.assertIsNotNone(st["lam"][st["one_alone"]])
        self.assertEqual(Lr.RWLearner.young_rule, "band")                      # the class default is the law


class TestLawUnchanged(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.L, _s, _c, _r = toy_learner()
        cls.scenes = test_scenes()

    def test_off_carries_no_new_field(self):
        for i, raw in enumerate(self.scenes):
            for p in PHRASES:
                a = ask(self.L, raw, p, i)
                self.assertNotIn("young_d", a)
                self.assertNotIn("point_rule", a)

    def test_band_explicit_equals_the_default(self):
        for i, raw in enumerate(self.scenes):
            for p in PHRASES:
                self.assertEqual(ask(self.L, raw, p, i, "band"), ask(self.L, raw, p, i))

    def test_an_unknown_rule_refuses_by_name(self):
        with self.assertRaises(ValueError) as cm:
            ask(self.L, self.scenes[0], ["dax"], 0, "euclid")
        self.assertIn("young_rule", str(cm.exception))


class TestNearest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.L, _s, _c, _r = toy_learner()
        cls.scenes = test_scenes()

    def test_every_other_ask_equals_the_law(self):
        n = 0
        for i, raw in enumerate(self.scenes):
            for p in PHRASES:
                if p == ["dax"]:
                    continue
                self.assertEqual(ask(self.L, raw, p, i, "nearest"), ask(self.L, raw, p, i), (i, p))
                n += 1
        self.assertGreater(n, 100)

    def test_a_mature_one_word_phrase_is_the_law(self):
        for w in SH:
            self.assertGreaterEqual(int(self.L.meetings[self.L.index[w]]), self.L.p_from)
        for i, raw in enumerate(self.scenes):
            self.assertEqual(ask(self.L, raw, ["sa"], i, "nearest"), ask(self.L, raw, ["sa"], i))

    def test_one_young_word_points_at_the_nearest(self):
        moved = 0
        for i, raw in enumerate(self.scenes):
            law, fix = ask(self.L, raw, ["dax"], i), ask(self.L, raw, ["dax"], i, "nearest")
            d = reader_d(self.L, raw, "dax")
            self.assertEqual(fix["point_rule"], "nearest")
            self.assertEqual(fix["young_d"], [float(v) for v in d])
            ties = np.flatnonzero(d == d.min())
            self.assertIn(fix["point"], [int(t) for t in ties])
            if ties.size == 1:
                self.assertEqual(fix["point"], int(np.argmin(d)))
            # best, scores, the three «none» flags and their fits: the law's numbers
            self.assertEqual({k: v for k, v in fix.items() if k not in ("point", "young_d", "point_rule")},
                             {k: v for k, v in law.items() if k != "point"})
            moved += int(fix["point"] != law["point"])
        self.assertGreater(moved, 0)                         # the rule is not the law on this toy (else the test tests nothing)

    def test_an_exact_tie_goes_to_the_items_generator(self):
        raw = self.scenes[0]
        tied = np.stack([raw[0], raw[0], raw[1]])            # two byte-identical hypotheses: an exact distance tie
        d = reader_d(self.L, tied, "dax")
        if d[2] < d[0]:
            tied = np.stack([raw[1], raw[1], raw[0]])
            d = reader_d(self.L, tied, "dax")
        self.assertEqual(d[0], d[1])
        self.assertLessEqual(d[0], d[2])
        got = set()
        for i in range(40):
            M = copy.copy(self.L)
            M.young_rule = "nearest"
            a = M.answer_point(tied, ["dax"], np.random.default_rng(i))
            want = Lr.pick(np.asarray(a["young_d"]), np.random.default_rng(i), "min")
            self.assertEqual(a["point"], want)
            got.add(a["point"])
        self.assertEqual(got, {0, 1})

    def test_the_four_fallbacks_are_the_law(self):
        cases = {}
        a = copy.deepcopy(self.L)
        del a.reader                                           # (1) no reader yet (never calibrated)
        cases["no reader"] = a
        b = copy.deepcopy(self.L)
        b.reader["ear"]["one_alone"] = None                    # (2) one_alone None
        cases["one_alone None"] = b
        c = copy.deepcopy(self.L)
        c.reader["ear"]["lam"][c.reader["ear"]["one_alone"]] = None   # (3) that type's Λ None
        cases["lam None"] = c
        e = copy.deepcopy(self.L)
        e.proto_w[e.index["dax"]] = 0.0                        # (4) the word has no prototype
        cases["proto_w 0"] = e
        for name, M in cases.items():
            for i, raw in enumerate(self.scenes[:8]):
                with self.subTest(fallback=name, i=i):
                    law = ask(M, raw, ["dax"], i)
                    fix = ask(M, raw, ["dax"], i, "nearest")
                    self.assertEqual(fix, law)
                    self.assertNotIn("point_rule", fix)

    def test_the_rule_never_writes_the_learner(self):
        M = copy.deepcopy(self.L)
        before = copy.deepcopy(vars(M))
        M.young_rule = "nearest"
        for i, raw in enumerate(self.scenes):
            M.answer_point(raw, ["dax"], np.random.default_rng(i))
        after = vars(M)
        after = {k: v for k, v in after.items() if k != "young_rule"}
        self.assertEqual(sorted(after), sorted(before))


class TestCalibrationUnmoved(unittest.TestCase):
    """AMENDMENT 1 §2: τ_point reads logp_answer (never answer_point), so a learner living under the rule calibrates to the
    law's thresholds — the clause that would break IDENTITY."""

    def test_calibrate_and_calibrate_r_equal_with_the_rule_on_and_off(self):
        L0, _s0, cal0, cr0 = toy_learner()
        L1, _s1, cal1, cr1 = toy_learner(young_rule="nearest")
        self.assertEqual(L1.young_rule, "nearest")
        self.assertEqual(cal1["tau_point"], cal0["tau_point"])
        self.assertIsNotNone(cal0["tau_point"])
        self.assertEqual(cal1["tau_word"], cal0["tau_word"])
        self.assertEqual(cal1["tau_none"], cal0["tau_none"])
        self.assertEqual(cal1["n"], cal0["n"])
        self.assertEqual(cr1["types"], cr0["types"])
        self.assertEqual(cr1["one_alone"], cr0["one_alone"])
        self.assertEqual(cr1["bands"], cr0["bands"])
        self.assertTrue(np.array_equal(L1.V, L0.V) and np.array_equal(L1.b, L0.b))


if __name__ == "__main__":
    unittest.main()
