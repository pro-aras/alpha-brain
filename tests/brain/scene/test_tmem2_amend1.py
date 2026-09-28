# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:15 +0400 — PREREG-TMEM2 AMENDMENT 1 (final a7dceea, sha 6da8ff67…), its
# own rows, test-first (red on scene-tmem2 2b7d800): a said word w of type T is graded at h* ONLY IF w's own band holds h* (the
# READER under the learner's state — read, as declared, from the claim step's own «what is this?» at h*, the call that made the
# claim CONFIDENT); otherwise the claim is UNGRADED «about a thing I did not see», counted under the claimed word b_T(h*);
# confirmed / refuted as before. The truth-fed row applies the SAME rule at the referent's hypothesis — one difference, the
# hypothesis (declared: the ceiling of the amended row). Beside it, offline: the metacognition-of-perception reading (of the
# claims whose referent the gaze never saw, the fraction set aside) and Fable's false-unseen rate (of the claims whose referent
# the gaze DID see, the fraction set aside). Step 3 read after the rule; step 5's price a STOP when OVER.
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from brain.scene import health as H
from brain.scene import learners as Lr
from brain.scene import run_tmem2 as T


class TestTheRule(unittest.TestCase):
    # shape type: h0 believed «circle», h1 believed «star»; colour type: h0 «blue», h1 «red» — every claim CONFIDENT.
    # the held words (the band's «what is this?») per hypothesis:
    REC = {"types": [("circle", "star"), ("blue", "red")],
           "believed": [["circle", "star"], ["blue", "red"]],
           "confident": [[True, True], [True, True]],
           "held": [("blue", "circle"), ("circle", "red", "star")]}

    def test_the_reason(self) -> None:
        self.assertEqual(H.REASON_UNSEEN, "about a thing I did not see")

    def test_a_said_word_whose_band_refuses_the_attributed_thing_is_set_aside(self) -> None:
        # «star» said, attributed to h0 (believed a circle): «star»'s band does not hold h0 → set aside, under «circle»
        self.assertEqual(H.grades(self.REC, {"star": 0}), [("circle", None, "star")])
        self.assertEqual(H.grades(self.REC, {"red": 0}), [("blue", None, "red")])

    def test_a_said_word_whose_band_holds_it_is_graded_as_before(self) -> None:
        # «circle» said, attributed to h1 (believed a star): «circle»'s band holds h1 → REFUTED, under «star»
        self.assertEqual(H.grades(self.REC, {"circle": 1}), [("star", False, "circle")])
        self.assertEqual(H.grades(self.REC, {"circle": 0, "blue": 0}), [("circle", True, "circle"), ("blue", True, "blue")])
        # unchanged: never attributed, a claim not confident, a word of no learned type → nothing
        rec = dict(self.REC, confident=[[False, True], [True, True]])
        self.assertEqual(H.grades(rec, {"circle": 0}), [])
        self.assertEqual(H.grades(self.REC, {"star": None, "big": 0}), [])

    def test_the_book_counts_a_set_aside_claim_under_the_claimed_word_and_moves_nothing_else(self) -> None:
        b = H.HealthBook()
        b.add_grades([("circle", True, "circle")] * 20)
        r = b.rows["circle"]
        before = (r.n_graded, r.cal20(), H.row_gate(r), list(r.outcomes))
        b.add_grades([("circle", None, "star")])
        self.assertEqual((r.n_graded, r.cal20(), H.row_gate(r), list(r.outcomes)), before)
        self.assertEqual(r.unseen, 1)
        self.assertEqual(b.row("star").missed, 0)                             # a set-aside claim is no miss of the said word
        self.assertEqual(r.summary()["unseen"], 1)
        b.add_grades([("circle", False, "star")])                              # a refutation: as before
        self.assertEqual((r.outcomes[-1], b.rows["star"].missed, r.unseen), (0, 1, 1))


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


class TestOnALearner(unittest.TestCase):
    def test_the_claim_records_the_held_words_and_a_confirmation_is_never_set_aside(self) -> None:
        L, A, B, rng = _learner()
        road = Lr.RWRoad(L)
        n_conf = 0
        for k in range(60):
            X = np.stack([A[f"a{rng.integers(3)}"] + B[f"b{rng.integers(2)}"] + 0.5 * rng.normal(size=Lr.RW_DIM)
                          for _ in range(3)])
            rec = H.claims(road, X)
            self.assertEqual(rec["held"], [tuple(sorted(road.held_words(X[h]))) for h in range(3)])
            for t, bs in enumerate(rec["believed"]):
                for h, b in enumerate(bs):
                    if rec["confident"][t][h]:
                        n_conf += 1
                        self.assertEqual(H.grades(rec, {b: h}), [(b, True, b)])          # b is held at h by confidence
        self.assertGreater(n_conf, 50)


class TestTheToy(unittest.TestCase):
    def test_a_set_aside_claim_moves_nothing_in_the_toy(self) -> None:
        for seed in (0, 1, 2):
            t = H.row_toy(seed)
            self.assertTrue(t["unseen_moves_nothing"], t)
            self.assertTrue(T.toy_passes(t), t)
        self.assertFalse(T.toy_passes(dict(H.row_toy(0), unseen_moves_nothing=False)))


class TestTheHook(unittest.TestCase):
    """The hook grades BOTH rows through the rule — the truth-free row at the learner's attribution, the truth-fed row at the
    referent's hypothesis — and keeps the two readings beside, offline."""

    REC = TestTheRule.REC

    def _hook(self, truth):
        return T._Hook(L=None, train=None, truth=truth)

    def _after(self, hook, i, att, ref, words):
        with mock.patch.object(T.H, "attribution", return_value=att), mock.patch.object(T.R, "referent_index", return_value=ref):
            hook.after(i, np.zeros((2, 3)), words, [], self.REC)

    def test_when_the_attribution_is_the_referent_the_two_rows_are_one(self) -> None:
        hook = self._hook([{"referent": 0}] * 3)
        self._after(hook, 0, {"star": 0, "red": 0}, 0, ["star", "red"])       # both set aside at h0
        self._after(hook, 1, {"circle": 1}, 1, ["circle"])                     # refuted at h1
        self._after(hook, 2, {"circle": 0, "blue": 0}, 0, ["circle", "blue"])  # confirmed at h0
        self.assertEqual(hook.free.summary(), hook.fed.summary())
        self.assertEqual((hook.free.rows["circle"].unseen, hook.free.rows["circle"].outcomes), (1, [1]))   # «star» at h0, under «circle»
        self.assertEqual((hook.free.rows["blue"].unseen, hook.free.rows["star"].outcomes), (1, [0]))

    def test_the_perception_readings(self) -> None:
        hook = self._hook([{"referent": 1}] * 3)
        self._after(hook, 0, {"star": 0}, None, ["star"])        # the referent never seen; the rule sets it aside
        self._after(hook, 1, {"circle": 1}, 1, ["circle"])       # the referent seen; graded (refuted) — not set aside
        self._after(hook, 2, {"star": 0}, 1, ["star"])           # the referent seen, h* elsewhere: set aside → a false-unseen
        p = hook.perception
        self.assertEqual(p["unseen"], {"gradable": 1, "set_aside": 1, "scenes": 1, "scenes_set_aside": 1})
        self.assertEqual(p["seen"], {"gradable": 2, "set_aside": 1, "scenes": 2, "scenes_set_aside": 1})
        self.assertEqual(hook.fed.rows["star"].outcomes, [0, 1])  # the fed row at h1: «circle» refuted, then «star» confirmed
        self.assertEqual(sum(r.unseen for r in hook.fed.rows.values()), 0)   # no hypothesis for the unseen referent: nothing
        r = T.perception_rates(p)
        self.assertEqual((r["metacognition"], r["false_unseen"]), (1.0, 0.5))
        self.assertEqual(T.perception_rates({"unseen": {"gradable": 0, "set_aside": 0, "scenes": 0, "scenes_set_aside": 0},
                                             "seen": {"gradable": 0, "set_aside": 0, "scenes": 0, "scenes_set_aside": 0}})
                         ["metacognition"], None)


class TestTheLawAndTheGate(unittest.TestCase):
    def test_the_amendments_sha_is_checked(self) -> None:
        self.assertEqual(T.PREREG_TMEM2_AMEND1_SHA256, "6da8ff679a317166c7a4e82bf9efd183785b5ecb90ad1bcb6fbae90d241386e6")
        self.assertEqual(T.PREREG_TMEM2_AMEND1_PATH.name, "PREREG-TMEM2-AMEND-1.md")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("not the amendment\n")
        try:
            with mock.patch.object(T, "PREREG_TMEM2_AMEND1_PATH", Path(f.name)):
                with self.assertRaises(T.TMem2Error):
                    T.check_prereg_tmem2()
        finally:
            os.unlink(f.name)

    def test_step5_the_price_is_a_stop_when_over(self) -> None:
        self.assertEqual(T.price_verdict(67.0), {"within": True, "stop": False})
        self.assertEqual(T.price_verdict(300.0), {"within": True, "stop": False})       # ≤ 5 CPU-min
        self.assertEqual(T.price_verdict(300.5), {"within": False, "stop": True})


if __name__ == "__main__":
    unittest.main()
