# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:20 +0400 — S1a's runner end to end on SMALL real caches (a temp root): caches
# → questions (no keys in them) → every arm over a short stream with two reading points → the grader → the bars. The
# oracle arms' referent is the referent's thing hypothesis; A-RW and N-SHUF never load the truth file (checked by
# spying on cache.load_truth).
# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:59 +0400 — AMENDMENT 2: the reading arm never loads the truth; M6 without the meeting reads NOT GRADABLE (never 0.0); the bars read the graded 2–3-thing items.
# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:55 +0400 — PREREG-S1B1: the smoke builds the three new splits; the reading arm is A-RW-LR10; the bars' set is §7's.
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from brain.scene import cache as C
from brain.scene import marks as M
from brain.scene import run as R
from brain.scene import world as W

TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))
WS = 20261101


class TestRunEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TMP.mkdir(parents=True, exist_ok=True)
        cls._td = tempfile.TemporaryDirectory(dir=str(TMP), prefix="scene-run-test-")
        cls.root = Path(cls._td.name)
        for split, lim in (("train", 60), ("test", 24), ("m2b", None), ("m6", None), ("m3", None), ("speak", None),
                           ("decline", None)):          # PREREG-S1B1: the three new test splits too
            C.build(split, WS, C.cache_dir(cls.root, WS, split), limit=lim, recheck_n=2)
        cls.counts = R.build_questions(cls.root, WS)
        cls.loads = {}
        real = C.load_truth
        for arm in R.ARMS:
            calls = []
            with mock.patch.object(R.C, "load_truth", side_effect=lambda d, _c=calls: (_c.append(str(d)), real(d))[1]):
                R.run_arm(arm, cls.root, WS, n_train=60, reading_points=(30, 60), lr=0.1, eps=0.1, log=lambda s: None)
            cls.loads[arm] = calls
        cls.marks = R.grade_seed(cls.root, WS, log=lambda s: None)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._td.cleanup()

    def test_questions_hold_no_keys(self) -> None:
        Q = json.loads((self.root / str(WS) / "questions.json").read_text())
        for mark, qs in Q["questions"].items():
            for q in qs:
                self.assertNotIn("target", q)
                self.assertNotIn("types", q)
                self.assertNotIn("shape", q)
        self.assertEqual(self.counts["M2b"], 56)
        self.assertEqual(self.counts["M6"], 42)
        self.assertEqual(self.counts["M2a"], 24)

    def test_only_oracle_arms_load_the_truth(self) -> None:
        self.assertEqual(self.loads["A-RW"], [])
        self.assertEqual(self.loads["N-SHUF"], [])
        self.assertEqual(self.loads["A-RW-LR10"], [])                  # the reading arm is A-RW's feed (PREREG-S1B1 §6)
        for arm in ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH"):
            self.assertTrue(any(p.endswith("/train") for p in self.loads[arm]), arm)

    def test_every_arm_answers_every_question_at_every_reading_point(self) -> None:
        Q = json.loads((self.root / str(WS) / "questions.json").read_text())
        n = sum(len(v) for v in Q["questions"].values())
        for arm in R.ARMS:
            for rp in (30, 60):
                A = json.loads((self.root / str(WS) / "arms" / arm / f"answers_{rp:05d}.json").read_text())["answers"]
                self.assertEqual(len(A), n, (arm, rp))

    def test_grades_and_bars_compute(self) -> None:
        mk = self.marks
        for arm in R.ARMS:
            m1 = mk["arms"][arm]["rp"]["60"]["M1"]["all"]
            self.assertEqual(m1["n_all"], self.counts["M1"])
            self.assertTrue(0.0 <= m1["all"] <= 1.0)
        b = R.bars_for(mk, rp="60")
        self.assertEqual(set(b), {"M1", "M2a", "M2b", "M6", "M3", "SPOKEN", "TRUTH", "READ-BACK", "ORDER", "DECLINE",
                                  "N-SHUF", "N-SHUF-M3", "refute"})              # PREREG-S1B1 §7's marks
        self.assertTrue(b["M2b"]["underpowered"] is False)
        lines = R.print_seed_table(mk, log=lambda s: None)
        self.assertTrue(any("by reading point" in l and "graded 2- and 3-thing" in l for l in lines))
        self.assertTrue(any(l.strip().startswith("A-RW-LR10") for l in lines))           # the reading arm printed beside

    def test_amend2_m6_without_the_meeting_reads_not_gradable_never_zero(self) -> None:
        """AMENDMENT 2 §3–§4: this 60-scene stream never reaches the meeting (scene 2,700), so M6 is NOT GRADABLE at
        the seed, and every arm's M6 answers are «unheard» — no 0.0 anywhere."""
        self.assertIsNone(self.marks["meeting_seen"])
        b = R.bars_for(self.marks, rp="60")
        self.assertIsNone(b["M6"]["value"])
        self.assertTrue(b["M6"]["not_gradable"])
        self.assertFalse(b["M6"]["pass"])
        for arm in R.ARMS:
            m6 = self.marks["arms"][arm]["rp"]["60"]["M6"]["all"]
            self.assertIsNone(m6["covered"], arm)
            self.assertEqual(m6["n_unheard"], 42, arm)

    def test_amend2_bars_read_the_graded_items(self) -> None:
        b = R.bars_for(self.marks, rp="60")
        g = self.marks["arms"]["A-RW"]["rp"]["60"]["M1"]["graded"]
        self.assertEqual(b["M1"]["value"], g["covered"])
        self.assertEqual(b["M1"]["n"], g["n_covered"])

    def test_s1b1_the_wiring_pin_on_the_smoke(self) -> None:
        """PREREG-S1B1 §5: READ-BACK is 1.000 by construction on every arm's spoken phrases — re-checked by the grader
        from the recorded point and the pointer the question carried; a reading below 1.000 is a broken road."""
        for arm in R.ARMS:
            for rp in ("30", "60"):
                sp = self.marks["arms"][arm]["rp"][rp]["SPEAK"]
                self.assertIn(sp["readback"], (1.0, None), (arm, rp, sp))
                if sp["readback"] is None:
                    self.assertEqual(sp["n_spoken"], 0)
        spoken = sum(self.marks["arms"][a]["rp"]["60"]["SPEAK"]["n_spoken"] for a in R.ARMS)
        self.assertGreater(spoken, 0)                                       # the pin was READ, not vacuous

    def test_s1b1_m3_speak_decline_are_graded_for_every_arm(self) -> None:
        for arm in R.ARMS:
            R60 = self.marks["arms"][arm]["rp"]["60"]
            self.assertEqual(R60["M3"]["all"]["n_all"], 60)
            self.assertEqual(R60["SPEAK"]["n_all"], 96)
            self.assertEqual(R60["DECLINE"]["n_all"], 48)
            self.assertEqual(set(R60["M2a"]), {"law", "i", "ii"})

    def test_oracle_truth_points_among_the_true_things(self) -> None:
        A = json.loads((self.root / str(WS) / "arms" / "ORACLE-TRUTH" / "answers_00060.json").read_text())["answers"]
        truth = C.load_truth(C.cache_dir(self.root, WS, "test"))
        K = json.loads((self.root / str(WS) / "keys.json").read_text())
        for it in K["items"]["M1"]:
            a = A[it["item_id"]]
            self.assertLess(a["point"], len(truth[it["row"]]["things"]))


if __name__ == "__main__":
    unittest.main()
