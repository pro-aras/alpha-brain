# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:59 +0400 — AMENDMENT 2 (docs/brain/r3/PREREG-R3-TONIGHT-AMEND-2.md, genome-wt-brain3
# d54e6c0, sha 414b3201…), test-first: red on scene-talk 3d3f5d2, green after.
#   §1 P-ORACLE / ORACLE-TRUTH read with a TYPE-AWARE reader: one StreamingLDA per word type (the types passed in by the
#      caller — the oracle may know them, the learners never), pointing = argmax Σ log p(w | x) within w's type, «none»
#      and «what is this?» by the posterior's conformal 0.90 bands over each word's training referents.
#   §2 M1's graded items are the 2- and 3-thing scenes only (the one-thing items a sanity reading).
#   §3 M6 counts at a seed only if the one meeting reached the learner (≥ 1 fixation on the dax at its scene).
#   §4 a word never heard reads NOT GRADABLE, never 0.0.
#   §5 the reading arm A-RW-LR01: A-RW with lr 0.01, one difference, no bar.
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

    def test_bands_none_and_what_is_this(self) -> None:
        rng = np.random.default_rng(3)
        Rd, thing = _typed_world(rng, n=600)
        info = Rd.prepare()
        for w in ("red", "blue", "circle", "star", "big", "small"):
            tau = Rd.band[w]
            self.assertTrue(0.0 < tau <= 1.0, (w, tau))                        # a lower threshold on p(w | x)
            self.assertGreaterEqual(info["n"][f"word:{w}"], 9)
        x = thing("red", "circle", "small")
        em = Rd.what_is_this(x)
        self.assertIn("red", em)
        self.assertIn("circle", em)
        self.assertNotIn("blue", em)
        # «none»: the pointed thing fails a band of the phrase — a red circle and a blue star, asked «blue circle»
        X = np.stack([thing("red", "circle", "big"), thing("blue", "star", "big")])
        self.assertTrue(Rd.answer_point(X, ["blue", "circle"], np.random.default_rng(0))["none"])
        self.assertFalse(Rd.answer_point(X, ["red", "circle"], np.random.default_rng(0))["none"])

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
