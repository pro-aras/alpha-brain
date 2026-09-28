# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:59 +0400 — AMENDMENT 2 (docs/brain/r3/PREREG-R3-TONIGHT-AMEND-2.md, genome-wt-brain3
# d54e6c0, sha 414b3201…), test-first: red on scene-talk 3d3f5d2, green after.
#   §1 P-ORACLE / ORACLE-TRUTH read with a TYPE-AWARE reader: one StreamingLDA per word type (the types passed in by the
#      caller — the oracle may know them, the learners never), pointing = argmax Σ log p(w | x) within w's type, «none»
#      and «what is this?» by the posterior's conformal 0.90 bands over each word's training referents.
#   §2 M1's graded items are the 2- and 3-thing scenes only (the one-thing items a sanity reading).
#   §3 M6 counts at a seed only if the one meeting reached the learner (≥ 1 fixation on the dax at its scene).
#   §4 a word never heard reads NOT GRADABLE, never 0.0.
#   §5 the reading arm A-RW-LR01: A-RW with lr 0.01, one difference, no bar.
# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:07 +0400 — AMENDMENT 2 as CO-SIGNED (Fable 5.1, 74be9e0, sha 6e58191f…): «none» on the pointing score's conformal threshold; «what is this?» keeps the DISTANCE band under the type's own Λ.
from __future__ import annotations

import unittest

import numpy as np

from brain.scene import learners as Lr
from brain.scene import marks as M
from brain.scene import run as R

TYPES = {"red": "colour", "blue": "colour", "circle": "shape", "star": "shape", "big": "size", "small": "size",
         "dax": "shape"}


def _typed_world(rng, n=400, eps=0.1):
    """Colour lives in dims 0..9, shape in 10..19, size in 20..29; every thing carries all three (each thing is a sample
    of three classes at once — the case that broke the pooled reader)."""
    mu = {w: np.zeros(144) for w in TYPES}
    for k, w in enumerate(("red", "blue")):
        mu[w][0:10] = 3.0 * (1 if k else -1)
    for k, w in enumerate(("circle", "star")):
        mu[w][10:20] = 3.0 * (1 if k else -1)
    for k, w in enumerate(("big", "small")):
        mu[w][20:30] = 3.0 * (1 if k else -1)

    def thing(c, s, z):
        return mu[c] + mu[s] + mu[z] + rng.normal(size=144)

    Rd = Lr.TypedLDAReader(eps, TYPES)
    for _ in range(n):
        c, s, z = str(rng.choice(["red", "blue"])), str(rng.choice(["circle", "star"])), str(rng.choice(["big", "small"]))
        tpl = int(rng.integers(4))
        words = [[s], [c, s], [z, s], [z, c, s]][tpl]
        Rd.train_scene(thing(c, s, z), words)
    return Rd, thing


class TestTypedReader(unittest.TestCase):
    def test_one_reader_per_type_and_types_never_mix(self) -> None:
        Rd = Lr.TypedLDAReader(0.1, TYPES)
        x = np.ones(144)
        Rd.train_scene(x, ["red", "circle"])
        Rd.train_scene(2 * x, ["blue"])
        self.assertEqual(Rd.names_of("colour"), ["red", "blue"])
        self.assertEqual(Rd.names_of("shape"), ["circle"])
        self.assertEqual(Rd.names_of("size"), [])
        self.assertEqual(Rd.readers["shape"].counts, [1])            # «blue» never touched the shape reader

    def test_a_word_of_no_declared_type_is_refused(self) -> None:
        Rd = Lr.TypedLDAReader(0.1, TYPES)
        with self.assertRaises(KeyError):
            Rd.train_scene(np.ones(144), ["purple"])

    def test_posterior_within_type_and_forced_naming(self) -> None:
        rng = np.random.default_rng(1)
        Rd, thing = _typed_world(rng)
        Rd.prepare()
        x = thing("blue", "circle", "big")
        lp = {w: float(Rd.log_posterior(x[None, :], w)[0]) for w in ("red", "blue")}
        self.assertAlmostEqual(np.exp(lp["red"]) + np.exp(lp["blue"]), 1.0, places=9)   # a softmax WITHIN colour
        self.assertGreater(lp["blue"], lp["red"])
        self.assertEqual(Rd.name_forced(x, ["red", "blue"]), "blue")
        self.assertEqual(Rd.name_forced(x, ["circle", "star"]), "circle")
        self.assertEqual(Rd.name_forced(x, ["big", "small"]), "big")

    def test_pointing_is_argmax_of_summed_log_posteriors(self) -> None:
        rng = np.random.default_rng(2)
        Rd, thing = _typed_world(rng)
        Rd.prepare()
        X = np.stack([thing("red", "star", "big"), thing("blue", "star", "big"), thing("blue", "circle", "small")])
        for phrase, want in ((["blue", "star"], 1), (["circle"], 2), (["red", "star"], 0), (["small", "blue", "circle"], 2)):
            a = Rd.answer_point(X, phrase, np.random.default_rng(0))
            s = sum(Rd.log_posterior(X, w) for w in phrase)
            self.assertEqual(a["point"], int(np.argmax(s)))
            self.assertEqual(a["point"], want, phrase)

    def test_none_reads_the_pointing_score_against_its_conformal_threshold(self) -> None:
        """AMENDMENT 2 §1 as co-signed (Fable 5.1, 13:02): «none» = the best phrase score Σ log p(w | x) below the
        conformal 0.90 threshold of the said-phrase scores on the training referents (the builder's rule, new score)."""
        rng = np.random.default_rng(3)
        Rd, thing = _typed_world(rng, n=600)
        info = Rd.prepare()
        scores = [sum(float(Rd.log_posterior(x[None, :], w)[0]) for w in ws) for x, ws in zip(Rd.train_x, Rd.train_words)]
        self.assertAlmostEqual(Rd.tau_point, Lr.conformal_lower(scores), places=12)
        self.assertEqual(info["n"]["point"], len(scores))
        X = np.stack([thing("red", "circle", "big"), thing("blue", "star", "big")])
        for phrase in (["blue", "circle"], ["red", "circle"], ["star"], ["small", "red", "star"]):
            a = Rd.answer_point(X, phrase, np.random.default_rng(0))
            self.assertEqual(a["none"], a["best"] < Rd.tau_point, phrase)
        self.assertTrue(Rd.answer_point(X, ["blue", "circle"], np.random.default_rng(0))["none"])
        self.assertFalse(Rd.answer_point(X, ["red", "circle"], np.random.default_rng(0))["none"])

    def test_what_is_this_keeps_the_distance_band_under_the_types_own_metric(self) -> None:
        """AMENDMENT 2 §1 as co-signed: «what is this?» emits w when d_w(x) ≤ w's conformal 0.90 DISTANCE band over its
        training referents, d under w's own type's Λ — a posterior sums to 1 over the taught words and cannot refuse a
        never-taught shape; the distance band can (the far thing below emits NOTHING)."""
        rng = np.random.default_rng(5)
        # n = 6,000 scenes: the band is calibrated IN-SAMPLE under a metric fitted to the same referents, so it covers a
        # fresh thing near 0.90 only when a type's referents far outnumber the 144 dims — measured on this world, fresh
        # «red» coverage 0.007 / 0.587 / 0.820 at 147 / 450 / 1,471 red referents (a reading for the hand-back, not a bug)
        Rd, thing = _typed_world(rng, n=6000)
        info = Rd.prepare()
        for w in ("red", "blue", "circle", "star", "big", "small"):
            t = Rd.type_of(w)
            k = Rd.readers[t].names.index(w)
            d = [float(Rd._dist(t, x[None, :])[0, k]) for x, ws in zip(Rd.train_x, Rd.train_words) if w in ws]
            self.assertAlmostEqual(Rd.band[w], Lr.conformal_upper(d), places=12)
            self.assertGreaterEqual(info["n"][f"word:{w}"], 9)
        # a conformal 0.90 band covers ≈ 90 % of fresh things of its word (one draw alone would be a 1-in-10 flake):
        ems = [Rd.what_is_this(thing("red", "circle", "small")) for _ in range(300)]
        rate = lambda w: sum(w in e for e in ems) / len(ems)
        self.assertGreater(rate("red"), 0.7)
        self.assertGreater(rate("circle"), 0.7)
        self.assertLess(rate("blue"), 0.05)
        self.assertLess(rate("star"), 0.05)
        far = thing("red", "circle", "small") + 40.0 * rng.normal(size=144)
        self.assertEqual(Rd.what_is_this(far), [])
        lp = float(Rd.log_posterior(far[None, :], Rd.name_forced(far, ["circle", "star"]))[0])
        self.assertGreater(np.exp(lp), 0.5)                  # the posterior alone would have named it

    def test_unheard_word_is_not_answered(self) -> None:
        rng = np.random.default_rng(4)
        Rd, thing = _typed_world(rng, n=50)
        Rd.prepare()
        a = Rd.answer_point(np.stack([thing("red", "star", "big")]), ["dax"], np.random.default_rng(0))
        self.assertIsNone(a["point"])
        self.assertEqual(a["unheard"], ["dax"])

    def test_the_oracle_arms_use_the_typed_reader_and_the_learners_never_see_types(self) -> None:
        for arm in ("P-ORACLE", "ORACLE-TRUTH"):
            self.assertIsInstance(R.make_learner(arm, 0.1, 0.3), Lr.TypedLDAReader)
        for arm in ("A-RW", "N-SHUF", "P-ORACLE-RW", "A-RW-LR01"):
            L = R.make_learner(arm, 0.1, 0.3)
            self.assertIsInstance(L, Lr.RWLearner)
            self.assertFalse(hasattr(L, "word_types"))


class TestGradedItemsAndUnheard(unittest.TestCase):
    def _rows(self):
        truth = [{"row": 0, "things": [{}], "fix_thing": [0, 0]},
                 {"row": 1, "things": [{}, {}], "fix_thing": [0, 1]},
                 {"row": 2, "things": [{}, {}, {}], "fix_thing": [0, 1, 2]}]
        items = [{"item_id": f"i{r}", "row": r, "target": 0, "n_things": len(truth[r]["things"]), "types": [],
                  "template": "T1"} for r in range(3)]
        members = lambda r: ([(k,) for k in range(len(truth[r]["fix_thing"]))], [(0, 0)] * len(truth[r]["fix_thing"]))
        return truth, items, members

    def test_m1_graded_block_is_two_and_three_thing_items_only(self) -> None:
        truth, items, members = self._rows()
        g = M.grade_pointing(items, {f"i{r}": {"point": 0, "none": False} for r in range(3)}, truth, members, "gaze")
        s = M.summarise_pointing(g)
        self.assertEqual(s["graded"]["n_all"], 2)
        self.assertEqual(s["size1"]["n_all"], 1)
        self.assertEqual(s["all"]["n_all"], 3)

    def test_unheard_is_not_gradable_never_zero(self) -> None:
        truth, items, members = self._rows()
        ans = {f"i{r}": {"point": None, "none": None, "unheard": ["dax"]} for r in range(3)}
        g = M.grade_pointing(items, ans, truth, members, "gaze")
        self.assertTrue(all(not r["gradable"] for r in g))
        s = M.summarise_pointing(g)
        self.assertIsNone(s["graded"]["covered"])
        self.assertIsNone(s["all"]["all"])
        self.assertEqual(s["all"]["n_unheard"], 3)
        # mixed: one heard and right, one unheard → 1/1, the unheard one counted apart
        ans["i1"] = {"point": 0, "none": False}
        s = M.summarise_pointing(M.grade_pointing(items, ans, truth, members, "gaze"))
        self.assertEqual((s["graded"]["covered"], s["graded"]["n_covered"], s["graded"]["n_unheard"]), (1.0, 1, 1))


class TestM6Meeting(unittest.TestCase):
    def test_meeting_seen_reads_the_dax_scene(self) -> None:
        self.assertFalse(M.meeting_seen({"referent": 1, "fix_thing": [0, 0, 0, 0]}))
        self.assertTrue(M.meeting_seen({"referent": 1, "fix_thing": [0, 1, 0, 0]}))


class TestReadingArm(unittest.TestCase):
    def test_a_rw_lr01_is_a_rw_at_lr_001_and_carries_no_bar(self) -> None:
        self.assertIn("A-RW-LR01", R.ARMS)
        L = R.make_learner("A-RW-LR01", 0.1, 0.3)
        self.assertEqual(L.lr, 0.01)
        self.assertFalse(L.oracle)
        self.assertEqual(R.make_learner("A-RW", 0.1, 0.3).lr, 0.1)
        self.assertIn("A-RW-LR01", R.READING_ARMS)


if __name__ == "__main__":
    unittest.main()


class TestVerdictReadings(unittest.TestCase):
    """The report's verdicts, after the full run showed two readings the grader printed wrongly: a mark with n < 30 at a
    seed READS UNDERPOWERED (the signed PREREG), never PASS; and M2a is a CONJUNCTIVE bar, so CEILING-BOUND is read per
    half — the learner's failing half must be one the oracle fails too (#170: a blend hides which half failed)."""

    def test_underpowered_reads_underpowered(self) -> None:
        self.assertEqual(R._verdict({"pass": True, "underpowered": True, "not_gradable": False}), "UNDERPOWERED")
        self.assertEqual(R._verdict({"pass": False, "underpowered": True, "ceiling_bound": True}), "UNDERPOWERED")
        self.assertEqual(R._verdict({"pass": True, "underpowered": False}), "PASS")
        self.assertEqual(R._verdict({"pass": False, "not_gradable": "x", "underpowered": False}), "NOT GRADABLE")

    def test_m2a_ceiling_is_read_per_half(self) -> None:
        # the learner fails REFUSAL (0.497), which the oracle reaches (1.000); the oracle misses FALSE REFUSAL (0.119)
        v = M.m2a_verdict(0.497, 0.075, 1.000, 0.119)
        self.assertEqual((v["pass"], v["ceiling_bound"], v["whole_bar_ceiling"]), (False, False, True))
        self.assertEqual(v["failing_halves"], ["refusal"])
        # the learner fails only the half the oracle fails too → CEILING-BOUND
        v = M.m2a_verdict(0.900, 0.150, 1.000, 0.119)
        self.assertEqual((v["pass"], v["ceiling_bound"]), (False, True))
        # both halves met → PASS
        self.assertTrue(M.m2a_verdict(0.85, 0.05, 1.0, 0.08)["pass"])
        # a missing reading is never a pass
        self.assertFalse(M.m2a_verdict(None, 0.05, 1.0, 0.08)["pass"])
