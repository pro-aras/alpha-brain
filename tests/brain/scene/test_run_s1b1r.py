# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:15 +0400 — PREREG-S1B1R §2–§5 with AMENDMENT 1 (shas 879a22fb… / a198f0b4…), test-first
# (red on 7706371): the runner end to end on SMALL real caches of the FRESH test set (a temp root) — the questions (SPEAK2
# with a pointer, no keys), the four arms over a short stream answering the law at every reading point and A-RW-R's five
# one-difference readings at the last, a K-draw null answering M1 and M3, the grader, the bars and the report; the
# wiring pin (READ-BACK 1.000) on every road that spoke; the gate's pieces: step 3's types check, step 4's READER toy
# (a positive control, with its trained-item hold printed beside), step 5's SPEAK2 pin; S1b-1's arm command takes an
# explicit lr / ε (the gate's step 2 re-runs S1b-1's arms before any gate record exists).
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from brain.scene import cache as C
from brain.scene import learners as Lr
from brain.scene import marks as M
from brain.scene import run as R
from brain.scene import world as W

TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))
WS = 20261101


class TestRunR(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TMP.mkdir(parents=True, exist_ok=True)
        cls._td = tempfile.TemporaryDirectory(dir=str(TMP), prefix="scene-s1b1r-run-test-")
        cls.root = Path(cls._td.name)
        C.build("train", WS, C.cache_dir(cls.root, WS, "train"), limit=80, recheck_n=2)
        for split, lim in (("test", 24), ("m2b", None), ("m6", None), ("m3", None), ("speak", None), ("decline", None),
                           ("speak2", None)):
            C.build(split, WS, C.cache_dir(cls.root, WS, split, "fresh"), limit=lim, recheck_n=2, tset="fresh")
        cls.counts = R.build_questions_r(cls.root, WS)
        cls.loads = {}
        real = C.load_truth
        for arm in R.R_ARMS:
            calls = []
            with mock.patch.object(R.C, "load_truth", side_effect=lambda d, _c=calls: (_c.append(str(d)), real(d))[1]):
                R.run_arm_r(arm, cls.root, WS, n_train=80, reading_points=(40, 80), eps=0.3, log=lambda s: None)
            cls.loads[arm] = calls
        for k in (0, 1, 2):
            R.run_null(cls.root, WS, k, n_train=80)
        cls.marks = R.grade_seed_r(cls.root, WS, log=lambda s: None)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._td.cleanup()

    def test_fresh_questions_hold_no_keys_and_speak2_has_a_pointer(self) -> None:
        Q = json.loads((R.r_seed_root(self.root, WS) / "questions.json").read_text())
        self.assertEqual(Q["test_seed"], 20261401)
        self.assertEqual(Q["prereg_s1b1r_sha256"], R.PREREG_S1B1R_SHA256)
        for mark, qs in Q["questions"].items():
            for q in qs:
                self.assertNotIn("target", q)
                self.assertNotIn("kind", q)
        self.assertEqual(self.counts["SPEAK2"], 60)
        self.assertTrue(all("hyp" in q for q in Q["questions"]["SPEAK2"]))
        K = json.loads((R.r_seed_root(self.root, WS) / "keys.json").read_text())
        self.assertEqual({it["kind"] for it in K["items"]["SPEAK2"]}, {"CS", "SC", "SS"})

    def test_only_oracle_arms_load_the_truth(self) -> None:
        self.assertEqual(self.loads["A-RW-R"], [])
        for arm in ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH"):
            self.assertTrue(any(p.endswith("/train") for p in self.loads[arm]), arm)

    def test_the_law_every_reading_point_the_readings_at_the_last(self) -> None:
        d = R.r_seed_root(self.root, WS) / "arms"
        a40 = json.loads((d / "A-RW-R" / "answers_00040.json").read_text())
        a80 = json.loads((d / "A-RW-R" / "answers_00080.json").read_text())
        self.assertEqual(set(a40["roads"]), {"LAW"})
        self.assertEqual(set(a80["roads"]), {"LAW", *R.R_READINGS})
        for arm in ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH"):
            self.assertEqual(list(json.loads((d / arm / "answers_00080.json").read_text())["roads"]), ["LAW"])
        rec = json.loads((d / "A-RW-R" / "record.json").read_text())
        for rp in ("40", "80"):
            self.assertIn("types", rec["reading_points"][rp]["reader"])      # the cover printed at every reading point
        self.assertIn("world", rec["reading_points"]["80"]["reader"])         # R-TT's types at the last

    def test_the_wiring_pin_on_every_road_that_spoke(self) -> None:
        spoke = 0
        for arm in R.R_ARMS:
            for road, g in self.marks["arms"][arm]["rp"]["80"]["roads"].items():
                m = g["MOUTH"]
                self.assertIn(m["readback_all"], (1.0, None), (arm, road))
                spoke += m["n_readback_all"]
        self.assertGreater(spoke, 0)                                          # the pin was READ, not vacuous

    def test_marks_bars_and_report(self) -> None:
        b = R.bars_r(self.marks, rp="80")
        self.assertEqual(set(b) - {"refute"}, set(R.R_MARK_ORDER))
        self.assertEqual(b["NULL-M1"]["dist"]["n"], 2)                        # k = 1, 2 (k = 0 printed apart)
        self.assertIsNotNone(b["NULL-M1"]["k0"])
        self.assertTrue(b["DECLINE"]["reading"])
        m2a = self.marks["arms"]["A-RW-R"]["rp"]["80"]["roads"]
        self.assertEqual(m2a["LAW"]["m2a_key"], "none_i")                     # (d): τ_point
        self.assertEqual(m2a["R-NONE-DIST"]["m2a_key"], "none")
        lines = R.print_seed_table_r(self.marks, rp="80", log=lambda s: None)
        self.assertTrue(any("types" in l for l in lines))
        self.assertTrue(any("one-alone" in l for l in lines))
        self.assertTrue(any("CS" in l and "TRUTH-NEED" in l for l in lines))

    def test_a_young_word_is_never_emitted_by_the_law(self) -> None:
        for rp in ("40", "80"):
            g = self.marks["arms"]["A-RW-R"]["rp"][rp]["roads"]["LAW"]["M2b"]["graded"]
            self.assertNotIn("dax", g["shape_words_emitted"])


class TestGatePieces(unittest.TestCase):
    def test_types_check(self) -> None:
        good = [tuple(sorted(W.SHAPES)), tuple(sorted(W.COLOUR_NAMES)), tuple(sorted(W.SIZE_NAMES))]
        words = list(W.SHAPES + W.COLOUR_NAMES + W.SIZE_NAMES)
        self.assertTrue(R.types_check(good, words)["pass"])
        self.assertFalse(R.types_check([good[0], good[1][:3], good[1][3:], good[2]], words)["pass"])

    def test_the_reader_toy_is_a_positive_control(self) -> None:
        for seed in R.READER_TOY_SEEDS:
            t = R.reader_toy(seed, 0.3)
            self.assertLessEqual(t["diag_refusal"], R.TOY_DIAG_MAX, t)
            self.assertGreaterEqual(t["reader_refusal"], R.TOY_READER_MIN, t)
            self.assertGreaterEqual(t["reader_holds_trained"], 0.5, t)        # it does not refuse everything
            self.assertLess(t["pin_weighted_vs_plain"], 1e-9, t)              # every r = 1 in the toy

    def test_speak2_pin_on_the_cache_rows(self) -> None:
        with tempfile.TemporaryDirectory(dir=str(TMP), prefix="scene-s1b1r-pin-") as td:
            d = C.cache_dir(Path(td), WS, "speak2", "fresh")
            C.build("speak2", WS, d, limit=6, recheck_n=1, tset="fresh")
            res = R.speak2_pin_rows(C.load_truth(d))
            self.assertEqual((res["n"], res["pass"]), (6, 6))

    def test_s1b1s_arm_takes_an_explicit_lr_and_eps(self) -> None:
        src = Path(R.__file__).read_text()                                    # the CLI accepts --lr / --eps
        self.assertIn('ap.add_argument("--lr"', src)
        self.assertIn('ap.add_argument("--eps"', src)

    def test_null_permutations(self) -> None:
        p0 = R.null_perm(WS, 0, 50)
        self.assertTrue(np.array_equal(p0, Lr.nshuf_permutation(R.substream(WS, "n-shuf-permutation"), 50)))
        p1 = R.null_perm(WS, 1, 50)
        self.assertTrue(np.array_equal(p1, Lr.nshuf_permutation(R.substream(WS, f"null:{WS}:1"), 50)))
        self.assertFalse(np.any(p1 == np.arange(50)))


if __name__ == "__main__":
    unittest.main()
