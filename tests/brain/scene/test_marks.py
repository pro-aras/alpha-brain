# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:15 +0400 — S1a's marks (PREREG-R3-TONIGHT §S1a «The marks»): M1 items are true
# of EXACTLY one thing and drawn by the parent's own rule; M2a phrases are allowed pairs true of nothing; the NECESSARY
# word types; the questions carry no key; the hypothesis→thing rule (strict plurality, a tie is no thing); covered;
# the verdict thresholds computed from the PREREG's probe numbers; LOO nearest-class-mean = the probe's own rule.
from __future__ import annotations

import collections
import unittest

import numpy as np

from brain.scene import marks as M
from brain.scene import world as W


def _truth_rows(scenes):
    rows = []
    for r, s in enumerate(scenes):
        d = s.to_dict()
        d.update({"row": r, "fix_thing": [], "centroids": [[0.0, 0.0]] * len(s.things)})
        rows.append(d)
    return rows


class TestItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenes = W.scenes_for("test", 20261201)
        cls.truth = _truth_rows(cls.scenes)

    def test_m1_true_of_exactly_one_thing(self) -> None:
        items = M.m1_items(self.truth, 20261201)
        self.assertGreater(len(items), 350)
        for it in items:
            things = M.things_of(self.truth[it["row"]])
            hits = [k for k, t in enumerate(things) if W.phrase_true_of(it["phrase"], t)]
            self.assertEqual(hits, [it["target"]])
            self.assertEqual(tuple(it["phrase"]), W.template_words(it["template"], things[it["target"]]))
            if len(things) == 1:
                self.assertEqual(it["types"], [])
        self.assertEqual(items, M.m1_items(self.truth, 20261201))          # deterministic
        tpl = collections.Counter(it["template"] for it in items if it["n_things"] == 1)
        self.assertEqual(set(tpl), set(W.TEMPLATES))

    def test_m2a_true_of_nothing_allowed_pairs(self) -> None:
        items = M.m2a_items(self.truth, 20261201)
        self.assertEqual(len(items), 400)
        for it in items:
            things = M.things_of(self.truth[it["row"]])
            c, s = it["phrase"]
            self.assertIn((s, c), W.ALLOWED)
            self.assertFalse(any(W.phrase_true_of(it["phrase"], t) for t in things))

    def test_questions_carry_no_key(self) -> None:
        for it in M.m1_items(self.truth, 20261201)[:20] + M.m2a_items(self.truth, 20261201)[:20]:
            q = M.question(it)
            self.assertEqual(set(q), {"item_id", "mark", "row", "phrase"})

    def test_m2b_m6(self) -> None:
        m2b = M.m2b_items(_truth_rows(W.scenes_for("m2b", 20261201)))
        self.assertEqual(sum(it["graded"] for it in m2b), 48)
        self.assertEqual(sum(not it["graded"] for it in m2b), 8)
        self.assertTrue(all(it["shape"] == "diamond" for it in m2b if not it["graded"]))
        m6 = M.m6_items(_truth_rows(W.scenes_for("m6", 20261201)))
        self.assertEqual(len(m6), 42)
        self.assertTrue(all(it["phrase"] == ["dax"] for it in m6))


class TestNecessaryTypes(unittest.TestCase):
    def test_examples(self) -> None:
        rc = W.Thing("circle", "red", "big", 0, 0)
        bc = W.Thing("circle", "blue", "big", 0, 60)
        rs = W.Thing("square", "red", "small", 60, 0)
        self.assertEqual(M.necessary_types(("red", "circle"), [rc, bc]), ("colour",))
        self.assertEqual(M.necessary_types(("red", "circle"), [rc, rs]), ("shape",))
        self.assertEqual(M.necessary_types(("big", "red", "circle"), [rc, bc, rs]), ("colour",))
        self.assertEqual(M.necessary_types(("circle",), [rc]), ())
        self.assertEqual(M.necessary_types(("circle",), [rc, rs]), ("shape",))
        self.assertEqual(M.absent_types(("blue", "square"), [rc, rs]), ("colour",))
        self.assertEqual(M.absent_types(("red", "star"), [rc]), ("shape",))
        self.assertEqual(M.absent_types(("green", "star"), [rc]), ())


class TestHypothesisRules(unittest.TestCase):
    def test_label_and_thing_hypothesis(self) -> None:
        ft = [0, 0, 1, None]
        members = [(0, 1), (2,), (3,)]
        c = M.hyp_counts(members, ft)
        self.assertEqual([M.hyp_label(x) for x in c], [0, 1, None])
        self.assertIsNone(M.hyp_label(collections.Counter({0: 1, 1: 1})))       # a merged tie is no thing
        self.assertEqual(M.hyp_label(collections.Counter({0: 2, 1: 1})), 0)
        self.assertEqual(M.thing_hypothesis(0, members, [(1, 1), (5, 5), (9, 9)], ft, (12.0, 12.0)), 0)
        self.assertIsNone(M.thing_hypothesis(2, members, [(1, 1), (5, 5), (9, 9)], ft, (0.0, 0.0)))
        # a split thing with a tie → the hypothesis nearer its centroid
        self.assertEqual(M.thing_hypothesis(0, [(0,), (1,)], [(1, 1), (4, 4)], [0, 0], (36.0, 36.0)), 1)
        self.assertTrue(M.covered(1, ft))
        self.assertFalse(M.covered(2, ft))


class TestThresholdsAndLoo(unittest.TestCase):
    def test_verdict_thresholds_are_computed(self) -> None:
        t = M.verdict_thresholds()
        self.assertAlmostEqual(t["shape"], 0.9 * 0.797)
        self.assertAlmostEqual(t["colour"], 0.9 * 0.933)
        self.assertAlmostEqual(t["size"], 0.9 * 0.867)

    def test_loo_ncm_matches_the_probes_own_loop(self) -> None:
        rng = np.random.default_rng(0)
        X = rng.normal(size=(40, 5))
        y = [str(k % 3) for k in range(40)]
        X[:, 0] += np.array([int(v) for v in y]) * 1.5
        # the probe's loop, verbatim in spirit (seat_scene_probe.py loo_ncm)
        yy = np.array(y)
        ok = 0
        for i in range(len(X)):
            m = np.ones(len(X), bool); m[i] = False
            cls = sorted(set(yy[m]))
            Mm = np.stack([X[m & (yy == c)].mean(0) for c in cls])
            ok += cls[int(np.argmin(((Mm - X[i]) ** 2).sum(1)))] == yy[i]
        self.assertAlmostEqual(M.loo_ncm(X, y), ok / len(X))


class TestGrading(unittest.TestCase):
    def test_pointing_grade_and_summary(self) -> None:
        truth = [{"row": 0, "things": [{}, {}], "fix_thing": [0, 1, 1, None]}]
        items = [{"item_id": "M1:x", "row": 0, "target": 1, "n_things": 2, "types": ["colour"], "template": "T2"}]
        members = lambda r: ([(0,), (1, 2), (3,)], [(0, 0), (5, 5), (9, 9)])
        g = M.grade_pointing(items, {"M1:x": {"point": 1, "none": False}}, truth, members, "gaze")
        self.assertTrue(g[0]["correct"] and g[0]["covered"])
        self.assertAlmostEqual(g[0]["chance"], 1 / 3)
        g2 = M.grade_pointing(items, {"M1:x": {"point": 2, "none": True}}, truth, members, "gaze")
        self.assertFalse(g2[0]["correct"])
        s = M.summarise_pointing(g + g2)
        self.assertEqual(s["all"]["covered"], 0.5)
        self.assertEqual(s["all"]["false_refusal"], 0.5)
        self.assertEqual(s["type:colour"]["n_covered"], 2)

    def test_m2b_dax_is_a_shape_word(self) -> None:
        items = [{"item_id": "a", "row": 0, "shape": "arrow", "colour": "red", "size": "big", "graded": True},
                 {"item_id": "b", "row": 1, "shape": "cup", "colour": "blue", "size": "small", "graded": True}]
        r = M.grade_m2b(items, {"a": {"emit": ["red", "big"]}, "b": {"emit": ["dax"]}})
        self.assertEqual(r["graded"]["correct"], 0.5)
        self.assertEqual(r["graded"]["shape_words_emitted"], {"dax": 1})


if __name__ == "__main__":
    unittest.main()
