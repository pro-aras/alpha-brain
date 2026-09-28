# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:41 +0400 — PREREG-TMEM2 AMENDMENT 2 (final b1e2b15, sha 76d8ac86…), its own
# rows, test-first (red on scene-tmem2 75ef77e): «a thing I did not see» is the learner's own M2a «none». On each training scene,
# after the parent's phrase is heard and BEFORE train_scene, the LAW road points for that phrase over the scene's SEEN
# hypotheses (τ_point — S1a's rule, S1b-1R's none_i — under the current state); if «none» fires, every claim the phrase would
# grade is UNGRADED «about a thing I did not see» (counted under the claimed word); otherwise it is graded as PREREG-TMEM2 §2.
# No band rule any more (AMENDMENT 1 §2's, replaced). The truth-fed row is UNCHANGED — no rule on it; beside it (Fable's edit)
# the fed row RESTRICTED to the claims the rule keeps. The readings: the metacognition-of-perception reading and the
# false-unseen rate, per claim, per scene and per phrase. Step 3's one-sided STOP reads the whole fed row, unchanged.
from __future__ import annotations

import copy
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from brain.scene import health as H
from brain.scene import learners as Lr
from brain.scene import run_tmem2 as T


class TestTheGrade(unittest.TestCase):
    # shape type: h0 believed «circle», h1 «star»; colour type: h0 «blue», h1 «red» — every claim CONFIDENT; the held words
    # (AMENDMENT 1's record, read by no rule now) per hypothesis:
    REC = {"types": [("circle", "star"), ("blue", "red")],
           "believed": [["circle", "star"], ["blue", "red"]],
           "confident": [[True, True], [True, True]],
           "held": [("blue", "circle"), ("circle", "red", "star")]}

    def test_no_band_rule_any_more(self) -> None:
        # «star» said, attributed to h0 (believed a circle; «star» is not among h0's held words): REFUTED, as PREREG-TMEM2 §2
        self.assertEqual(H.grades(self.REC, {"star": 0}), [("circle", False, "star")])
        self.assertEqual(H.grades(self.REC, {"circle": 0, "blue": 0}), [("circle", True, "circle"), ("blue", True, "blue")])

    def test_none_sets_aside_every_claim_the_phrase_would_grade(self) -> None:
        self.assertEqual(H.grades(self.REC, {"star": 0, "blue": 0}, set_aside=True), [("circle", None, "star"), ("blue", None, "blue")])
        rec = dict(self.REC, confident=[[False, True], [True, True]])
        self.assertEqual(H.grades(rec, {"circle": 0, "big": 0, "red": None}, set_aside=True), [])   # never gradable: nothing


def _learner(seed=0, n=500):
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


class TestTheLearnersOwnNone(unittest.TestCase):
    def test_heard_none_is_the_law_roads_none_and_changes_nothing(self) -> None:
        L, A, B, rng = _learner()
        road = Lr.RWRoad(L)
        snap = copy.deepcopy(L)
        fired = []
        for k in range(80):
            X = np.stack([A["a0"] + B["b0"], A["a1"] + B["b0"]]) + 0.5 * rng.normal(size=(2, Lr.RW_DIM))
            phrase = [["a0", "b0"], ["a1", "b0"], ["a2", "b1"]][k % 3]          # the third fits nothing in view
            got = H.heard_none(road, X, phrase, np.random.default_rng(k))
            ref = road.answer_point(X, phrase, np.random.default_rng(k))
            self.assertIs(got["none"], ref["none"])
            self.assertIs(got["none"], ref["none_i"])
            self.assertEqual(got["best"], ref["best"])
            fired.append(got["none"])
        self.assertTrue(any(fired) and not all(fired), fired)                    # it fires on some phrases, not on all
        absent = [fired[k] for k in range(2, 80, 3)]
        present = [fired[k] for k in range(80) if k % 3 != 2]
        self.assertGreater(np.mean(absent), np.mean(present))                    # more on the phrase that fits nothing in view
        self.assertEqual(L.summary(), snap.summary())
        self.assertEqual(L.tau_point, snap.tau_point)
        self.assertTrue(np.array_equal(L.V, snap.V) and np.array_equal(L.b, snap.b))

    def test_an_unheard_word_points_at_nothing_and_sets_nothing_aside(self) -> None:
        L, A, B, rng = _learner()
        X = np.stack([A["a0"] + B["b0"], A["a1"] + B["b1"]])
        self.assertIsNone(H.heard_none(Lr.RWRoad(L), X, ["a0", "zzz"], np.random.default_rng(0))["none"])


class TestTheHook(unittest.TestCase):
    REC = TestTheGrade.REC

    def _hook(self, truth):
        return T._Hook(L=None, train=None, truth=truth)

    def _scene(self, hook, i, att, ref, words, none):
        rec = dict(self.REC, none=none)
        with mock.patch.object(T.H, "attribution", return_value=att), mock.patch.object(T.R, "referent_index", return_value=ref):
            hook.after(i, np.zeros((2, 3)), words, [], rec)

    def test_none_sets_the_free_row_aside_and_leaves_the_fed_row(self) -> None:
        hook = self._hook([{"referent": 0}, {"referent": 1}])
        self._scene(hook, 0, {"star": 0, "blue": 0}, 0, ["star", "blue"], none=True)
        self.assertEqual((hook.free.rows["circle"].unseen, hook.free.rows["blue"].unseen), (1, 1))     # under the claimed words
        self.assertEqual(hook.free.rows["circle"].outcomes + hook.free.rows["blue"].outcomes, [])
        self.assertEqual((hook.fed.rows["circle"].outcomes, hook.fed.rows["blue"].outcomes), ([0], [1]))   # the fed row: no rule
        self.assertEqual(sum(r.n_graded for r in hook.fed_kept.rows.values()), 0)                    # the rule kept nothing here
        self._scene(hook, 1, {"circle": 1}, 1, ["circle"], none=False)                               # «none» silent: all three rows
        self.assertEqual((hook.free.rows["star"].outcomes, hook.fed.rows["star"].outcomes, hook.fed_kept.rows["star"].outcomes),
                         ([0], [0], [0]))

    def test_the_readings(self) -> None:
        hook = self._hook([{"referent": 1}] * 4)
        self._scene(hook, 0, {"star": 0}, None, ["star"], none=True)                 # never seen, «none» fired: set aside
        self._scene(hook, 1, {"star": 0}, None, ["star"], none=False)                # never seen, «none» silent: graded
        self._scene(hook, 2, {"circle": 1}, 1, ["circle"], none=False)               # seen: graded
        self._scene(hook, 3, {"star": 0, "red": 0}, 1, ["star", "red"], none=True)   # seen, «none» fired: two false-unseen
        p = hook.perception
        self.assertEqual(p["unseen"], {"gradable": 2, "set_aside": 1, "scenes": 2, "scenes_set_aside": 1, "phrases": 2, "phrases_none": 1})
        self.assertEqual(p["seen"], {"gradable": 3, "set_aside": 2, "scenes": 2, "scenes_set_aside": 1, "phrases": 2, "phrases_none": 1})
        r = T.perception_rates(p)
        self.assertEqual((r["metacognition"], r["false_unseen"]), (0.5, 2 / 3))
        self.assertEqual((r["metacognition_phrases"], r["false_unseen_phrases"]), (0.5, 0.5))

    def test_the_hook_hears_with_its_own_generator(self) -> None:
        hook = T._Hook(L=None, train=None, truth=[], ws=20261101)
        rec = {"x": 1}
        with mock.patch.object(T.H, "heard_none", return_value={"none": True, "best": -9.0, "unheard": None}) as hn, \
                mock.patch.object(T.Lr, "RWRoad", return_value="road"), mock.patch.object(T, "substream", wraps=T.substream) as ss:
            hook.heard(7, np.zeros((2, 3)), ["a"], rec)
        self.assertIs(rec["none"], True)
        ss.assert_called_once_with(20261101, "tmem2-none:7")
        self.assertEqual(hn.call_args[0][0], "road")
        hook.heard(8, np.zeros((2, 3)), ["a"], None)                                 # an inactive hook: nothing

    def test_train_hooked_hears_between_the_claims_and_the_training(self) -> None:
        calls = []

        class P:
            def words(self, i):
                return ["a0"]

        class Train:
            p = P()

            def for_arm(self, arm, i):
                return np.zeros((2, 3))

        class L:
            index = {}

            def train_scene(self, X, words, referent=None, rng=None):
                calls.append("train")

        class Spy:
            def before(self, i, X):
                calls.append("before")
                return {}

            def heard(self, i, X, words, rec):
                calls.append("heard")

            def after(self, i, X, words, new, rec):
                calls.append("after")

        T.train_hooked(L(), Train(), range(2), 20261101, [], Spy())
        self.assertEqual(calls, ["before", "heard", "train", "after"] * 2)


class TestTheKeptReading(unittest.TestCase):
    def test_the_residual_on_the_kept_claims_is_a_reading(self) -> None:
        free = {"a": {"n_graded": 40, "cal20": 0.80}, "b": {"n_graded": 40, "cal20": 0.95}}
        kept = {"a": {"n_graded": 30, "cal20": 0.95}, "b": {"n_graded": 30, "cal20": 0.90}}
        r = T.kept_residuals(free, kept, ["a", "b", "c"])
        self.assertAlmostEqual(r["residual"]["a"], -0.15)
        self.assertEqual(r["below"], ["a"])                                  # more than 0.10 below the kept fed row: printed
        self.assertIsNone(r["residual"]["c"])


class TestTheLaw(unittest.TestCase):
    def test_the_second_amendments_sha_is_checked(self) -> None:
        self.assertEqual(T.PREREG_TMEM2_AMEND2_SHA256, "76d8ac86c0af8320b1b96fa48621cf6a016e0c4037437489edbd186b56c758bf")
        self.assertEqual(T.PREREG_TMEM2_AMEND2_PATH.name, "PREREG-TMEM2-AMEND-2.md")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("not the amendment\n")
        try:
            with mock.patch.object(T, "PREREG_TMEM2_AMEND2_PATH", Path(f.name)):
                with self.assertRaises(T.TMem2Error):
                    T.check_prereg_tmem2()
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
