# edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05 17:50 +0400 — PREREG-MOUTH-INCREMENTAL §3/§4 (G-EQUIV2,
# M-INCREMENT, M-INDELIBLE, M-SKIP, M-BAIL, M-COST): the incremental mouth's corpus, the literature fixtures computed
# by hand from the papers, the indelibility pin, and the twin implementation.
"""PREREG-MOUTH-INCREMENTAL's gates and marks. `_produce_incremental_twin` is the TWIN implementation written from
§2's text of the law (the twin-implementation form, G-EQUIV2). The literature fixtures' expected phrases are computed
BY HAND from Dale & Reiter 1995 (arXiv:cmp-lg/9504020) §2.2 and §3.1.2, quoted beside each test."""
import unittest

import numpy as np

from brain.scene import learners as Lr
from brain.scene.learners import Ear


def _produce_incremental_twin(road, X, target, rng_factory, budget=Lr.MOUTH_BUDGET):
    """The TWIN, from the law's §2 lines 1–6 verbatim: walk, skip the powerless, add + read-back, stop at sufficiency,
    indelible, bail."""
    X = np.atleast_2d(X)
    t = int(target)
    n_hyp = X.shape[0]
    types = [tuple(T) for T in road.types()]
    B = road.believed(X)
    say = [(k, B[k][t]) for k in range(len(types)) if B[k][t] is not None and road.sayable(X[t], B[k][t])]
    out = {"target": t, "believed": {str(k): B[k][t] for k in range(len(types)) if B[k][t] is not None},
           "sayable": [w for _k, w in say], "n_say": len(say), "n_readbacks": 0, "skipped": [], "added": []}
    if not say:
        return {"spoken": None, "reason": "no sayable word", **out}
    ear = road.ear
    phrase = []
    for k, w in say:
        if all(B[k][h] == w for h in range(n_hyp) if h != t):
            out["skipped"].append(w)
            continue
        phrase = ear.order(phrase + [w])
        out["added"].append(w)
        if out["n_readbacks"] >= budget:
            return {"spoken": None, "reason": "the mouth's budget", "budget": int(budget), **out}
        out["n_readbacks"] += 1
        a = road.answer_point(X, phrase, rng_factory())
        if a.get("point") is None or int(a["point"]) != t or a.get("none"):
            continue
        sc = np.asarray(a["scores"], dtype=np.float64)
        others = np.delete(sc, t)
        margin = float(sc[t] - np.max(others)) if others.size else float("inf")
        return {"spoken": list(phrase), "reason": None, "readback_point": int(a["point"]), "margin": margin, **out}
    return {"spoken": None, "reason": "the read-back", **out}


class FakeRoad:
    """A road whose read-backs come from a phrase table; memoized defaults per phrase."""

    def __init__(self, types, believed, sayable, table, *, ear_utts=(), default=(None, False)):
        self._types = [tuple(T) for T in types]
        self._believed = believed
        self._sayable = set(sayable)
        self._table = {tuple(k): v for k, v in table.items()}
        self._default = default
        self._memo = {}
        self.ear = Ear()
        for u in ear_utts:
            self.ear.hear(u)

    def types(self):
        return list(self._types)

    def believed(self, X):
        return [list(col) for col in self._believed]

    def sayable(self, x, w):
        return w in self._sayable

    def one_alone(self):
        return None

    def answer_point(self, X, phrase, rng):
        key = tuple(phrase)
        if key in self._table:
            point, none, scores = self._table[key]
            return {"point": point, "none": none, "scores": np.asarray(scores, dtype=float)}
        if key not in self._memo:
            self._memo[key] = self._default
        point, none = self._memo[key]
        return {"point": point, "none": none, "scores": np.zeros(X.shape[0])}


def _f():
    return np.random.default_rng(20261101)


class TestIncrementalLiterature(unittest.TestCase):
    """The papers' own worked examples, mapped word-for-kind, expected phrases computed BY HAND (quoted)."""

    def test_dale_reiter_2_2_the_black_dog(self):
        # D&R §2.2: r = small black dog; contrast = {large white dog, small black cat}. Preference: colour then type.
        # Hand: «black» rules out the white dog → added; read-back NOT sufficient (the cat is black too) → «dog» rules
        # out the cat → phrase [black, dog] sufficient → STOP. Expected spoken: ["black", "dog"].
        types = [("black", "white"), ("dog", "cat"), ("small", "large")]
        believed = [["black", "white", "black"], ["dog", "dog", "cat"], ["small", "large", "small"]]
        table = {("black",): (1, False, [0.4, 0.6, 0.5]), ("black", "dog"): (0, False, [0.9, 0.1, 0.1])}
        road = FakeRoad(types, believed, ["black", "dog", "small"], table, ear_utts=[["black", "dog"], ["small"]])
        out = Lr.produce_incremental(road, np.zeros((3, 3)), 0, _f)
        self.assertEqual(out["spoken"], ["black", "dog"])
        self.assertEqual(out["added"], ["black", "dog"])
        self.assertEqual(out["skipped"], [])                 # the walk stops at sufficiency — «small» is never reached
        self.assertEqual(out["n_readbacks"], 2)

    def test_dale_reiter_3_1_2_seven_cups_indelible(self):
        # D&R §3.1.2: seven cups; the preference order material, size, colour; the algorithm's own non-minimality is
        # the POINT (the true minimal is «large red»; the incremental form keeps «plastic», as the human algorithm does).
        # Hand: «plastic» rules out cups 3,4,5,6 (paper) → added, read-back NOT sufficient (cup 7 is plastic too) →
        # «large» rules out cup 2 (small) → added, read-back NOT sufficient (cup 7 is large plastic) → «red» rules out
        # cup 7 (blue) → phrase [plastic, large, red] sufficient → STOP. Expected: those three words, ear order.
        cups = [("large", "red", "plastic"), ("small", "red", "plastic"), ("small", "red", "paper"),
                ("medium", "red", "paper"), ("large", "green", "paper"), ("large", "blue", "paper"),
                ("large", "blue", "plastic")]
        types = [("plastic", "paper"), ("large", "small", "medium"), ("red", "green", "blue")]
        believed = [[c[2] for c in cups], [c[0] for c in cups], [c[1] for c in cups]]
        table = {("plastic",): (1, False, [0.5, 0.6]),
                 ("plastic", "large"): (1, False, [0.5, 0.55]),
                 ("plastic", "large", "red"): (0, False, [0.9, 0.1] + [0.05] * 5)}
        road = FakeRoad(types, believed, ["plastic", "large", "red"], table,
                        ear_utts=[["plastic", "large", "red"]])
        out = Lr.produce_incremental(road, np.zeros((7, 3)), 0, _f)
        self.assertEqual(out["spoken"], ["plastic", "large", "red"])
        self.assertNotEqual(out["spoken"], ["large", "red"])   # never the minimal form — indelibility, by design
        self.assertEqual(out["n_readbacks"], 3)

    def test_white_bird_keeps_the_early_word(self):
        # M-INDELIBLE: target white bird; contrast {black cup, white cup}. Ear: colour first. «white» rules out the
        # black cup → added (read-back NOT sufficient: the white cup) → «bird» → sufficient. The output KEEPS «white»
        # though «bird» alone would have done — the human overinformativeness, pinned.
        types = [("white", "black"), ("bird", "cup")]
        believed = [["white", "black", "white"], ["bird", "cup", "cup"]]
        table = {("white",): (2, False, [0.4, 0.3, 0.5]), ("white", "bird"): (0, False, [0.9, 0.05, 0.05])}
        road = FakeRoad(types, believed, ["white", "bird"], table, ear_utts=[["white", "bird"]])
        out = Lr.produce_incremental(road, np.zeros((3, 3)), 0, _f)
        self.assertEqual(out["spoken"], ["white", "bird"])
        self.assertNotEqual(out["spoken"], ["bird"])           # the plant: an «optimized» drop-the-redundancy variant FAILS


class TestIncrementalMechanism(unittest.TestCase):
    """M-SKIP, M-BAIL, M-COST, and the twin corpus (M-INCREMENT)."""

    def test_relevance_skip_costs_no_readback(self):
        types = [("circle", "square"), ("red", "blue")]
        believed = [["circle", "circle"], ["red", "blue"]]     # both hyps believe «circle»: it rules out nothing
        table = {("red",): (0, False, [0.8, 0.2])}
        road = FakeRoad(types, believed, ["circle", "red"], table)
        out = Lr.produce_incremental(road, np.zeros((2, 3)), 0, _f)
        self.assertEqual(out["skipped"], ["circle"])
        self.assertEqual(out["added"], ["red"])
        self.assertEqual(out["n_readbacks"], 1)
        self.assertEqual(out["spoken"], ["red"])

    def test_bail_readback_never_sufficient(self):
        types = [("circle", "square"), ("red", "blue")]
        believed = [["circle", "square"], ["red", "blue"]]
        road = FakeRoad(types, believed, ["circle", "red"], {})   # the default read-back never points
        out = Lr.produce_incremental(road, np.zeros((2, 3)), 0, _f)
        self.assertIsNone(out["spoken"])
        self.assertEqual(out["reason"], "the read-back")
        self.assertEqual(out["n_readbacks"], 2)

    def test_bail_budget_breach(self):
        types = [(f"w{k}",) for k in range(4)]
        believed = [[f"w{k}", f"x"] for k in range(4)]            # every word relevant
        road = FakeRoad(types, believed, [f"w{k}" for k in range(4)], {})
        out = Lr.produce_incremental(road, np.zeros((2, 3)), 0, _f, budget=3)
        self.assertIsNone(out["spoken"])
        self.assertEqual(out["reason"], "the mouth's budget")
        self.assertEqual(out["n_readbacks"], 3)

    def test_corpus_200_fixtures_twin_equal(self):
        rng = np.random.default_rng(20261005)
        for i in range(200):
            n_types = int(rng.integers(1, 10))
            types = []
            words = []
            for k in range(n_types):
                T = (f"w{k}a", f"w{k}b") if (k and rng.random() < 0.25) else (f"w{k}",)
                types.append(T)
                words.extend(T)
            n_hyp = int(rng.integers(1, 4))
            believed = [[rng.choice(list(T) + [None], p=[0.7 / len(T)] * len(T) + [0.3]) for _ in range(n_hyp)]
                        for T in types]
            sayable = {w for w in words if rng.random() < 0.7}
            table = {}
            for _ in range(int(rng.integers(0, 6))):
                ph = tuple(sorted(rng.choice(words, size=min(len(words), int(rng.integers(1, 3))), replace=False)))
                table[ph] = (rng.choice([0, None, int(rng.integers(0, n_hyp))]), bool(rng.random() < 0.2),
                             list(rng.random(n_hyp)))
            utts = [list(rng.choice(words, size=min(len(words), int(rng.integers(1, 4))), replace=False))
                    for _ in range(int(rng.integers(1, 5)))]
            road = FakeRoad(types, believed, sayable, table, ear_utts=utts)
            X = np.zeros((n_hyp, 3))
            target = int(rng.integers(0, n_hyp))
            mine = Lr.produce_incremental(road, X, target, _f)
            twin = _produce_incremental_twin(road, X, target, _f)
            for field in ("spoken", "readback_point", "margin", "reason", "n_readbacks", "skipped", "added"):
                self.assertEqual(mine.get(field), twin.get(field), f"fixture {i} field {field}")
            self.assertLessEqual(mine["n_readbacks"], mine["n_say"])          # M-COST, every fixture

    def test_the_hand_is_graded(self):
        # M-INCREMENT's plant: a mis-computed expectation ON PURPOSE — the test must catch the hand, not the code.
        # The correct expectation is computed in test_white_bird_keeps_the_early_word: ["white", "bird"].
        types = [("white", "black"), ("bird", "cup")]
        believed = [["white", "black", "white"], ["bird", "cup", "cup"]]
        table = {("white",): (2, False, [0.4, 0.3, 0.5]), ("white", "bird"): (0, False, [0.9, 0.05, 0.05])}
        road = FakeRoad(types, believed, ["white", "bird"], table, ear_utts=[["white", "bird"]])
        out = Lr.produce_incremental(road, np.zeros((3, 3)), 0, _f)
        wrong_hand = ["bird"]                                                # the deliberate mis-computation
        self.assertNotEqual(out["spoken"], wrong_hand, "the mis-computed hand must be CAUGHT")
        self.assertEqual(out["spoken"], ["white", "bird"])                   # the right hand passes


if __name__ == "__main__":
    unittest.main()
