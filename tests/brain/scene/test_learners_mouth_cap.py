# edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05 13:28 +0400 — PREREG-MOUTH-CAP §4 (M-IDENT, M-BUDGET, M-TIME)
# + §3 (G-CALLERS): the mouth-cap's corpus against the OLD enumeration lifted verbatim, the plants, the budget path.
"""PREREG-MOUTH-CAP's gates and marks. The reference `_produce_believed_reference` is the OLD `produce_believed`
lifted VERBATIM from git 5b0942c:brain/scene/learners.py (G-EQUIV's named sha); only its name changed."""
import re
import subprocess
import time
import unittest
from pathlib import Path

import numpy as np

from brain.scene import learners as Lr
from brain.scene.learners import Ear

REPO = Path(__file__).resolve().parents[3]


def _produce_believed_reference(road, X: np.ndarray, target: int, rng_factory):
    X = np.atleast_2d(X)
    t = int(target)
    n_hyp = X.shape[0]
    types = [tuple(T) for T in road.types()]
    B = road.believed(X)
    base = {"target": t, "believed": {str(k): B[k][t] for k in range(len(types)) if B[k][t] is not None},
            "sayable": [], "n_candidates": 0, "n_unique": 0, "n_accepted": 0}
    say = [(k, B[k][t]) for k in range(len(types)) if B[k][t] is not None and road.sayable(X[t], B[k][t])]
    base["sayable"] = [w for _k, w in say]
    if not say:
        return {"spoken": None, "reason": "no sayable word", **base}
    cands = [[say[i] for i in range(len(say)) if mask >> i & 1] for mask in range(1, 1 << len(say))]
    uniq = [c for c in cands if not any(all(B[k][h] == w for k, w in c) for h in range(n_hyp) if h != t)]
    base["n_candidates"], base["n_unique"] = len(cands), len(uniq)
    if not uniq:
        return {"spoken": None, "reason": "no believed-unique phrase", **base}
    one = road.one_alone()
    ear = road.ear
    accepted = []
    fired = 0
    for c in uniq:
        phrase = ear.order([w for _k, w in c])
        a = road.answer_point(X, phrase, rng_factory())
        if a.get("point") is None or int(a["point"]) != t:
            continue
        if a.get("none"):
            fired += 1
            continue
        sc = np.asarray(a["scores"], dtype=np.float64)
        others = np.delete(sc, t)
        margin = float(sc[t] - np.max(others)) if others.size else float("inf")
        alone = 0 if (one is not None and any(k == one for k, _w in c)) else 1
        rank = (len(phrase), -margin, alone, tuple(ear.key(w) for w in phrase),
                tuple(ear.first.get(w, 10 ** 6) for w in phrase))
        accepted.append((rank, phrase, int(a["point"]), margin))
    base["n_accepted"] = len(accepted)
    if not accepted:
        return {"spoken": None, "reason": "none" if fired else "the read-back", **base}
    accepted.sort(key=lambda z: z[0])
    _rank, phrase, point, margin = accepted[0]
    return {"spoken": list(phrase), "reason": None, "readback_point": point, "margin": margin, **base}


class FakeRoad:
    """A road whose every answer is fixed by its tables; outcomes memoized per phrase so the reference and the new
    code read the SAME road. `table` maps a phrase tuple -> (point, none, scores); a phrase outside the table falls
    back to `default` (a (point, none) pair with random scores)."""

    def __init__(self, types, believed, sayable, table, *, ear_utts=(), one_alone=None, default=(None, False),
                 rng_outcomes=None):
        self._types = [tuple(T) for T in types]
        self._believed = believed
        self._sayable = set(sayable)
        self._table = {tuple(k): v for k, v in table.items()}
        self._one = one_alone
        self._default = default
        self._memo = {}
        self._rng_outcomes = rng_outcomes
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
        return self._one

    def answer_point(self, X, phrase, rng):
        key = tuple(phrase)
        if key in self._table:
            point, none, scores = self._table[key]
            return {"point": point, "none": none, "scores": np.asarray(scores, dtype=float)}
        if key not in self._memo:
            if self._rng_outcomes is not None:
                # the rng-consuming form: the outcome DEPENDS on the generator's draw (plant (ii): with a same-seed
                # factory every candidate sees the same stream whatever the evaluation order)
                draw = float(rng.random())
                point, none = (int(rng.integers(0, X.shape[0])), False) if draw < 0.5 else (None, False)
            else:
                point, none = self._default
            self._memo[key] = (point, none, self._rng_outcomes.random(X.shape[0]) if self._rng_outcomes is not None
                               else np.zeros(X.shape[0]))
        point, none, scores = self._memo[key]
        return {"point": point, "none": none, "scores": np.asarray(scores, dtype=float)}


def _same_factory():
    return np.random.default_rng(20261101)


class TestMouthCapCorpus(unittest.TestCase):
    """M-IDENT: the new produce_believed vs the old enumeration, field by field, over a randomized corpus."""

    def _fixture(self, rng):
        n_types = int(rng.integers(1, 10))
        types = []
        words = []
        for k in range(n_types):
            if k and rng.random() < 0.25:
                T = (f"w{k}a", f"w{k}b")
            else:
                T = (f"w{k}",)
            types.append(T)
            words.extend(T)
        n_hyp = int(rng.integers(1, 4))
        believed = []
        for T in types:
            believed.append([rng.choice(list(T) + [None], p=[0.7 / len(T)] * len(T) + [0.3]) for _ in range(n_hyp)])
        sayable = {w for w in words if rng.random() < 0.7}
        table = {}
        for _ in range(int(rng.integers(0, 6))):
            ph = tuple(sorted(rng.choice(words, size=min(len(words), int(rng.integers(1, 3))), replace=False)))
            point = rng.choice([0, None, int(rng.integers(0, n_hyp))])
            none = bool(rng.random() < 0.2)
            table[ph] = (point, none, list(rng.random(n_hyp)))
        utts = [list(rng.choice(words, size=min(len(words), int(rng.integers(1, 4))), replace=False)) for _ in range(int(rng.integers(1, 5)))]
        one = int(rng.integers(0, n_types)) if rng.random() < 0.5 else None
        return types, believed, sayable, table, utts, one, n_hyp

    def test_corpus_200_fixtures(self):
        rng = np.random.default_rng(20261005)
        n = 0
        for _ in range(200):
            types, believed, sayable, table, utts, one, n_hyp = self._fixture(rng)
            road = FakeRoad(types, believed, sayable, table, ear_utts=utts, one_alone=one)
            X = np.zeros((n_hyp, 3))
            target = int(rng.integers(0, n_hyp))
            old = _produce_believed_reference(road, X, target, _same_factory)
            new = Lr.produce_believed(road, X, target, _same_factory)
            for field in ("spoken", "readback_point", "margin", "reason"):
                self.assertEqual(old.get(field), new.get(field), f"fixture {n} field {field}: {old} vs {new}")
            self.assertEqual(old["n_candidates"], new["n_candidates"])
            self.assertEqual(old["n_unique"], new["n_unique"])
            self.assertEqual(old["n_accepted"], new["n_accepted"])
            self.assertEqual(set(old), set(new))   # AMENDMENT 2: at say ≤ 12 the dict carries NO new keys
            n += 1

    def _say_fixture(self, rng, n_say, n_hyp=2):
        types = [(f"w{k}",) for k in range(n_say)]
        believed = [[f"w{k}"] + [f"x{h}" for h in range(1, n_hyp)] for k in range(n_say)]
        return types, believed, [f"w{k}" for k in range(n_say)], n_hyp

    def test_corpus_say13_early_stop_decisions_equal(self):
        # 20 fixtures at say 13–16 (the capped path): an accepted exists in class 1–2 — the decision fields equal the
        # old enumeration's; n_readbacks stays far under the budget (the early stop is what the cap is FOR)
        rng = np.random.default_rng(4242)
        for _ in range(20):
            n_say = int(rng.integers(13, 17))
            types, believed, sayable, n_hyp = self._say_fixture(rng, n_say)
            k1, k2 = int(rng.integers(0, n_say)), int(rng.integers(0, n_say - 1))
            k2 = k2 + 1 if k2 >= k1 else k2
            table = {(f"w{k1}",): (0, False, [2.0] + [-1.0] * (n_hyp - 1)),
                     tuple(sorted((f"w{k1}", f"w{k2}"))): (0, False, [99.0] + [-99.0] * (n_hyp - 1))}
            road = FakeRoad(types, believed, sayable, table)
            X = np.zeros((n_hyp, 3))
            old = _produce_believed_reference(road, X, 0, _same_factory)
            new = Lr.produce_believed(road, X, 0, _same_factory)
            for field in ("spoken", "readback_point", "margin", "reason"):
                self.assertEqual(old.get(field), new.get(field))
            self.assertEqual(new["spoken"], [f"w{k1}"])          # the rank's law: the shorter accepted wins
            self.assertLess(new["n_readbacks"], 4 * n_say)
            self.assertEqual(old["n_unique"], new["n_unique"])   # uniqueness is exact wherever the budget does not bind

    def test_corpus_say13_exhaustive_all_fields_equal(self):
        # 10 fixtures at say 13–14 where uniqueness keeps few candidates and nothing is accepted: both enumerate fully,
        # every field equal including the counters
        rng = np.random.default_rng(777)
        for _ in range(10):
            n_say = int(rng.integers(13, 15))
            types = [(f"w{k}",) for k in range(n_say)]
            believed = [[f"w{k}", f"w{k}"] for k in range(n_say)]          # shared names: nothing is unique
            road = FakeRoad(types, believed, [f"w{k}" for k in range(n_say)], {})
            X = np.zeros((2, 3))
            old = _produce_believed_reference(road, X, 0, _same_factory)
            new = Lr.produce_believed(road, X, 0, _same_factory)
            self.assertEqual(old["reason"], new["reason"])
            self.assertEqual(old["n_unique"], new["n_unique"])
            self.assertEqual(old["n_accepted"], new["n_accepted"])
            self.assertEqual(new["n_readbacks"], new["n_unique"])
            self.assertTrue(new["exhaustive"])

    def test_plant_rank_beats_margin(self):
        # plant (i): a length-2 accepted AND a length-3 accepted with a LARGER margin — the winner must be the length-2
        types = [("alpha",), ("big",), ("red",)]
        believed = [["alpha"], ["big"], ["red"]]
        table = {("big", "red"): (0, False, [5.0, -1.0]),
                 ("alpha", "big", "red"): (0, False, [99.0, -99.0])}
        road = FakeRoad(types, believed, ["alpha", "big", "red"], table, ear_utts=[["alpha", "big", "red"]])
        out = Lr.produce_believed(road, np.zeros((1, 3)), 0, _same_factory)
        self.assertEqual(out["spoken"], ["big", "red"])
        self.assertEqual(out["margin"], 6.0)

    def test_plant_rng_consuming_road_order_independent(self):
        # plant (ii): an answer_point whose outcome is decided by the generator's draw; the same-seed factory gives
        # every candidate the same stream — old and new must agree even though their evaluation orders differ
        rng = np.random.default_rng(7)
        types, believed, sayable, _t, utts, one, n_hyp = self._fixture(rng)
        road = FakeRoad(types, believed, sayable, {}, ear_utts=utts, one_alone=one,
                        rng_outcomes=np.random.default_rng(99))
        X = np.zeros((n_hyp, 3))
        old = _produce_believed_reference(road, X, 0, _same_factory)
        new = Lr.produce_believed(road, X, 0, _same_factory)
        for field in ("spoken", "readback_point", "margin", "reason"):
            self.assertEqual(old.get(field), new.get(field))

    def test_plant_nothing_accepted_reason_equal(self):
        # plant (iii): nothing accepted anywhere — the reason string must match the old code's exactly
        types = [("alpha",), ("big",)]
        believed = [["alpha"], ["big"]]
        table = {("alpha",): (None, False, [1.0]), ("big",): (1, False, [0.5, 0.5]), ("alpha", "big"): (1, True, [0.0, 0.0])}
        road = FakeRoad(types, believed, ["alpha", "big"], table)
        X = np.zeros((1, 3))
        old = _produce_believed_reference(road, X, 0, _same_factory)
        new = Lr.produce_believed(road, X, 0, _same_factory)
        self.assertEqual(old["reason"], new["reason"])
        self.assertEqual(new["reason"], "the read-back")


class TestMouthCapBudget(unittest.TestCase):
    """M-BUDGET (the AMENDMENT 2 form): the capped path engages only at say > 12; the declared overflow form; the early
    stop landing BEFORE the budget when a winner exists."""

    def _big_road(self, n_say, n_hyp=2):
        types, believed, sayable, _ = TestMouthCapCorpus._say_fixture(self, np.random.default_rng(0), n_say, n_hyp)
        return FakeRoad(types, believed, sayable, {})

    def test_below_the_branch_the_old_code_runs_verbatim(self):
        # say 12: 4,095 candidates — under MOUTH_FULL_BELOW the budget does not exist (the old dict's own keys only)
        road = self._big_road(12)
        out = Lr.produce_believed(road, np.zeros((2, 3)), 0, _same_factory, budget=64)
        self.assertNotIn("n_readbacks", out)
        self.assertNotIn("exhaustive", out)
        self.assertEqual(out["reason"], "the read-back")
        self.assertEqual(out["n_unique"], 2 ** 12 - 1)      # every candidate unique (per-hyp believed names)
        self.assertEqual(out["n_accepted"], 0)

    def test_overflow_form(self):
        road = self._big_road(13)                      # every candidate unique; the default outcome never accepts
        self.assertGreater(2 ** 13 - 1, 64)            # the fixture asserts it changed the bytes: candidates > budget
        out = Lr.produce_believed(road, np.zeros((2, 3)), 0, _same_factory, budget=64)
        self.assertIsNone(out["spoken"])
        self.assertEqual(out["reason"], "the mouth's budget")
        self.assertEqual(out["n_readbacks"], 64)
        self.assertEqual(out["budget"], 64)
        self.assertEqual(out["n_say"], 13)
        self.assertFalse(out["exhaustive"])

    def test_early_stop_before_budget(self):
        road = self._big_road(13)
        road._table[("w0",)] = (0, False, [3.0, -1.0])     # accepted at class 1 (13 read-backs ≤ 64)
        out = Lr.produce_believed(road, np.zeros((2, 3)), 0, _same_factory, budget=64)
        self.assertEqual(out["spoken"], ["w0"])
        self.assertEqual(out["n_readbacks"], 13)

    def test_a_budget_break_discards_the_partial_class(self):
        # AMENDMENT 3: accepted ONLY at class 2, and 13 + 78 > 64 — the partial class's evaluated accepted counts for
        # nothing; the mouth says NOTHING (a partial winner could be a DIFFERENT phrase than the full enumeration's)
        road = self._big_road(13)
        road._table[("w0", "w1")] = (0, False, [3.0, -1.0])
        out = Lr.produce_believed(road, np.zeros((2, 3)), 0, _same_factory, budget=64)
        self.assertIsNone(out["spoken"])
        self.assertEqual(out["reason"], "the mouth's budget")
        self.assertEqual(out["n_readbacks"], 64)
        self.assertEqual(out["n_accepted"], 0)

    def test_overflow_winner_in_unevaluated_part_is_nothing_not_a_different_phrase(self):
        # the budget cuts before the class holding the only accepted candidate: the mouth says NOTHING (the declared trade)
        road = self._big_road(13)
        road._table[tuple(f"w{k}" for k in range(13))] = (0, False, [9.0, -9.0])  # accepted only at length 13
        out = Lr.produce_believed(road, np.zeros((2, 3)), 0, _same_factory, budget=64)
        self.assertIsNone(out["spoken"])
        self.assertEqual(out["reason"], "the mouth's budget")

    def test_full_budget_time_bound(self):
        # M-TIME: the overflow path at the FULL budget with a realistic read-back cost — ≤ 60 s wall, the load printed
        # (say 13: 8,191 candidates, so the 4,096 budget is what binds)
        class SlowRoad(FakeRoad):
            def answer_point(self, X, phrase, rng):
                Z = np.random.default_rng(0).random((500, 152))
                float(np.linalg.norm(Z - Z.mean(axis=0), axis=1).sum())
                return {"point": None, "none": False, "scores": np.zeros(X.shape[0])}
        road = SlowRoad([(f"w{k}",) for k in range(13)],
                        [[f"w{k}", "x"] for k in range(13)], [f"w{k}" for k in range(13)], {})
        t0 = time.perf_counter()
        out = Lr.produce_believed(road, np.zeros((2, 3)), 0, _same_factory)
        wall = time.perf_counter() - t0
        with open("/proc/loadavg") as f:
            load = f.read().strip()
        print(f"\nM-TIME: {wall:.2f}s wall for {out['n_readbacks']} read-backs at the full budget; loadavg {load}")
        self.assertEqual(out["reason"], "the mouth's budget")
        self.assertEqual(out["n_readbacks"], Lr.MOUTH_BUDGET)
        self.assertLessEqual(wall, 60.0)


class TestMouthCapCallers(unittest.TestCase):
    """G-CALLERS: no call site passes `budget`; the journaled say dict's keys are exactly the recorded six."""

    def test_no_caller_passes_budget(self):
        hits = subprocess.run(["grep", "-rn", "produce_believed(", "--include=*.py", str(REPO)],
                              capture_output=True, text=True).stdout.splitlines()
        callers = [h for h in hits if "def produce_believed" not in h and "test_learners_mouth_cap" not in h]
        for h in callers:
            self.assertNotIn("budget", h, f"a call site passes budget: {h}")
        self.assertTrue(any("genome/brain.py" in h for h in callers))

    def test_journaled_say_dict_keys(self):
        src = (REPO / "genome" / "brain.py").read_text()
        m = re.search(r'out\["say"\] = \{(.*?)\}', src, re.S)
        self.assertIsNotNone(m)
        keys = sorted(re.findall(r'"(\w+)":', m.group(1)))
        self.assertEqual(keys, ["fix", "hyp", "margin", "pos", "readback", "words"])


if __name__ == "__main__":
    unittest.main()
