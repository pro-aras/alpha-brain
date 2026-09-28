# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:33 +0400 — PREREG-TMEM2 (final 4d03f79, sha b785b54f…) §1, §3–§5, §7, test-first
# (red on scene-s1b1r 01e784b: brain/scene/run_tmem2.py does not exist there): the HEALTH life on SMALL real caches (a temp root
# laid out as S1b-1R's) reproduces S1b-1R's own A-RW-R record — `answers.point`, `answers.roads.LAW` and `learner.summary()`
# byte for byte under canonical JSON, a planted one-byte change CAUGHT (Test B2's compare_prefix discipline) — so the read-only
# hook changes no state; the four HEALTH roads answer every mark with the row's refusals recorded; the decision marks
# (ERROR-RECALL, TRUE-RETENTION over the control's own spoken phrases); the bars as co-signed and ruled (B2's null clause
# with the estate's 95 % binomial half-width; B3 read on its predictions; B4 pooled); step 3's STOP with its 0.10 tolerance;
# the law's sha checked.
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from brain.scene import cache as C
from brain.scene import health as H
from brain.scene import run as R
from brain.scene import run_tmem2 as T

TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))
WS = 20261101


class TestLifeEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TMP.mkdir(parents=True, exist_ok=True)
        cls._td = tempfile.TemporaryDirectory(dir=str(TMP), prefix="scene-tmem2-test-")
        cls.root_in = Path(cls._td.name) / "s1b1r"
        cls.root_out = Path(cls._td.name) / "tmem2"
        C.build("train", WS, C.cache_dir(cls.root_in, WS, "train"), limit=90, recheck_n=2)
        for split, lim in (("test", 24), ("m2b", None), ("m6", None), ("m3", None), ("speak", None), ("decline", None),
                           ("speak2", None)):
            C.build(split, WS, C.cache_dir(cls.root_in, WS, split, "fresh"), limit=lim, recheck_n=2, tset="fresh")
        R.build_questions_r(cls.root_in, WS)
        R.run_arm_r("A-RW-R", cls.root_in, WS, n_train=90, reading_points=(30, 90), eps=0.3, log=lambda s: None)
        loads = []
        real = C.load_truth
        with mock.patch.object(C, "load_truth", side_effect=lambda d: (loads.append(str(d)), real(d))[1]):
            cls.rec = T.run_life(WS, cls.root_in, cls.root_out, eps=0.3, rps=(30, 90), n_train=90, log=lambda s: None)
        cls.loads = loads
        cls.marks = T.grade_seed_tmem2(cls.root_in, cls.root_out, WS, rp=90)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._td.cleanup()

    def test_identity_with_the_reference_and_the_planted_byte_caught(self) -> None:
        idn = self.rec["identity"]
        self.assertTrue(idn["pass"], idn)
        for part in ("point", "LAW", "summary"):
            self.assertTrue(idn["parts"][part]["same"], part)
            self.assertTrue(idn["parts"][part]["planted_caught"], part)
            self.assertGreater(idn["parts"][part]["n_bytes"], 10)

    def test_the_rows_start_at_the_first_reading_point(self) -> None:
        self.assertEqual(self.rec["rows_by_rp"]["30"]["free"], {})              # no claim before the READER has types
        self.assertGreater(sum(r["n_claims"] for r in self.rec["rows_by_rp"]["90"]["free"].values()), 0)
        free, fed = self.rec["rows"]["free"], self.rec["rows"]["fed"]
        self.assertEqual({w: r["n_claims"] for w, r in free.items()}, {w: r["n_claims"] for w, r in fed.items()})

    def test_the_offline_ceiling_reads_the_train_referents_and_every_road_is_answered(self) -> None:
        self.assertTrue(any(p.endswith("/train") for p in self.loads))           # the referent's hypothesis for the fed row
        A = json.loads((self.root_out / str(WS) / "life" / "answers_00090.json").read_text())
        self.assertEqual(set(A["roads"]), {"LAW", *T.HEALTH_ROADS})

    def test_every_health_road_answers_every_mark_and_records_the_row(self) -> None:
        A = json.loads((self.root_out / str(WS) / "life" / "answers_00090.json").read_text())
        Q = json.loads((R.r_seed_root(self.root_in, WS) / "questions.json").read_text())["questions"]
        n = sum(len(Q[m]) for m in ("M2b", "NAME", "SPEAK", "SPEAK2", "DECLINE"))
        for road in T.HEALTH_ROADS:
            self.assertEqual(len(A["roads"][road]), n, road)
            for q in Q["SPEAK"] + Q["SPEAK2"]:
                a = A["roads"][road][q["item_id"]]
                if not a.get("uncovered"):
                    self.assertIn("row_refused", a)
        # 90 scenes: every row is short, so the truth-free gate says «no row» wherever the band held a word
        reasons = self.marks["roads"]["HEALTH-MOUTH"]["MOUTH"]["speak"]["reasons"]
        self.assertTrue(set(reasons) <= {"no row", "not held lately", "no sayable word", "no believed-unique phrase",
                                         "the read-back", "none", "uncovered"}, reasons)

    def test_the_control_is_read_from_the_reference_record(self) -> None:
        mk = self.marks
        self.assertEqual(mk["roads"]["CONTROL"]["MOUTH"], mk["roads"]["LAW"]["MOUTH"])   # identical by §1
        d = mk["decision"]["HEALTH-MOUTH"]
        self.assertEqual(d["n_err"] + d["n_true"], mk["decision"]["CONTROL"]["n_spoken"])
        self.assertEqual(mk["decision"]["CONTROL"]["er"], 0.0 if mk["decision"]["CONTROL"]["n_err"] else None)

    def test_ece_auroc_rows_read_on_the_roads_b_t(self) -> None:
        cal = self.marks["calibration"]
        self.assertEqual(set(cal), {"free", "fed", "null"})
        self.assertEqual(cal["free"]["n_pred"] + cal["free"]["n_excluded"], len(self.rec["name_preds"]))
        self.assertTrue(all(p["type"] in ("shape", "colour", "size") for p in self.rec["name_preds"]))


class TestIdentityComparator(unittest.TestCase):
    def test_canonical_json_and_a_planted_byte(self) -> None:
        a = {"x": [1.5, float("inf")], "b": {"z": 1, "y": None}}
        b = {"b": {"y": None, "z": 1}, "x": [1.5, float("inf")]}
        self.assertEqual(T.canon(a), T.canon(b))
        self.assertTrue(T.compare(T.canon(a), T.canon(b))["same"])
        planted = T.plant(T.canon(a))
        self.assertNotEqual(planted, T.canon(a))
        self.assertEqual(len(planted), len(T.canon(a)))
        r = T.compare(T.canon(a), planted)
        self.assertFalse(r["same"])
        self.assertIsNotNone(r["first_diff"])


class TestDecision(unittest.TestCase):
    def test_error_recall_and_true_retention(self) -> None:
        ctrl = {"i1": {"covered": True, "spoken": True, "true": False}, "i2": {"covered": True, "spoken": True, "true": False},
                "i3": {"covered": True, "spoken": True, "true": True}, "i4": {"covered": True, "spoken": True, "true": True},
                "i5": {"covered": True, "spoken": False, "true": False}, "i6": {"covered": False, "spoken": True, "true": False}}
        arm = {"i1": {"spoken": False, "true": False}, "i2": {"spoken": True, "true": False},
               "i3": {"spoken": True, "true": True}, "i4": {"spoken": False, "true": False}, "i5": {"spoken": True, "true": True},
               "i6": {"spoken": False, "true": False}}
        d = T.decision(ctrl, arm)
        self.assertEqual((d["n_err"], d["n_true"], d["n_spoken"]), (2, 2, 4))
        self.assertEqual((d["er"], d["tr"]), (0.5, 0.5))


class TestBars(unittest.TestCase):
    def test_b1(self) -> None:
        b = T.b1(truth_hm=0.95, n_hm=40, truth_ho=1.0, spoken_hm=0.8, spoken_ctrl=0.9, truth_ctrl=0.82)
        self.assertEqual(b["verdict"], "PASS")
        self.assertFalse(b["met_by_control"])
        self.assertEqual(T.b1(0.95, 40, 1.0, 0.6, 0.9, 0.82)["verdict"], "FAIL")            # silence does not pass
        self.assertTrue(T.b1(0.95, 40, 1.0, 0.8, 0.9, 0.95)["met_by_control"])
        self.assertEqual(T.b1(0.95, 20, 1.0, 0.8, 0.9, 0.82)["verdict"], "UNDERPOWERED")

    def test_b2_with_the_ruled_null_clause_and_the_ceiling(self) -> None:
        b = T.b2(er_hm=0.40, er_ho=0.50, tr_hm=0.95, er_null=0.10, n_err=78)
        self.assertEqual(b["verdict"], "PASS")
        self.assertAlmostEqual(b["null_hw"], 1.96 * (0.10 * 0.90 / 78) ** 0.5)
        self.assertEqual(T.b2(0.20, 0.50, 0.95, 0.10, 78)["verdict"], "FAIL")                # < 0.70 × the oracle
        self.assertEqual(T.b2(0.40, 0.50, 0.85, 0.10, 78)["verdict"], "FAIL")                # TRUE-RETENTION < 0.90
        self.assertEqual(T.b2(0.40, 0.50, 0.95, 0.35, 78)["verdict"], "FAIL")                # the null meets it too
        self.assertEqual(T.b2(0.40, 0.29, 0.95, 0.10, 78)["verdict"], "CEILING-BOUND")       # the oracle's own recall < 0.30
        self.assertEqual(T.b2(0.0, 0.50, 0.95, 0.0, 78)["verdict"], "FAIL")                  # hw = 0: the null must sit BELOW
        self.assertEqual(T.b2(0.40, 0.50, 0.95, 0.10, 20)["verdict"], "UNDERPOWERED")

    def test_b3_on_predictions_and_b4_pooled(self) -> None:
        self.assertEqual(T.b3(0.08, n_pred=450)["verdict"], "PASS")
        self.assertEqual(T.b3(0.12, n_pred=450)["verdict"], "FAIL")
        self.assertEqual(T.b3(0.08, n_pred=20)["verdict"], "UNDERPOWERED")
        self.assertEqual(T.b4(0.75, n_err_pooled=31)["verdict"], "PASS")
        self.assertEqual(T.b4(0.65, n_err_pooled=31)["verdict"], "FAIL")
        self.assertEqual(T.b4(0.75, n_err_pooled=29)["verdict"], "UNDERPOWERED")

    def test_step3_stops_only_on_a_clear_reversal(self) -> None:
        free = {"a": {"n_graded": 40, "cal20": 0.95}, "b": {"n_graded": 40, "cal20": 0.90}, "c": {"n_graded": 5, "cal20": 1.0}}
        fed = {"a": {"n_graded": 40, "cal20": 1.00}, "b": {"n_graded": 40, "cal20": 0.85}, "c": {"n_graded": 5, "cal20": 1.0}}
        s = T.step3(free, fed, ["a", "b", "c", "d"])
        self.assertFalse(s["stop"])                                             # −0.05: a reading, printed
        self.assertEqual(s["reversed"], ["a"])
        self.assertEqual(s["no_row"], ["c", "d"])
        fed["a"]["cal20"] = 1.0
        free["a"]["cal20"] = 0.85                                               # −0.15: the declared instrument fault
        self.assertTrue(T.step3(free, fed, ["a", "b"])["stop"])


class TestLaw(unittest.TestCase):
    def test_the_prereg_sha_is_checked(self) -> None:
        self.assertEqual(T.PREREG_TMEM2_SHA256, "b785b54f97c6c2bc300ce07cdc26aaa716bf9c7fcb3e7cc183294480b5fd2914")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("not the law\n")
        try:
            with mock.patch.object(T, "PREREG_TMEM2_PATH", Path(f.name)):
                with self.assertRaises(T.TMem2Error):
                    T.check_prereg_tmem2()
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
