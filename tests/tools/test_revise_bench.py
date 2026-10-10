# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 17:55 +0400 — REVISE-1's bench tests
# (tests FIRST, RED on the law commit 66eaffa): the toy world is deterministic to the last bit; the
# planted naming flip renames EXACTLY thing A's showings from the flip moment on (and the plant arm's
# world never changes though the driver claims the flip — G-PLANT (a)); G-CHAIN — the tier-2 bench's
# belief calls go through the SAME two functions creature/mind.py:3350/3385 calls (imported, never
# copied), pinned by identity AND by the call form AND at the seam's own source; one tier-2 life twice,
# byte-identical (G-DET's unit form); the pilot's NOT-GRADABLE refusal fires on the doctored
# no-flip-landed arm (never grades); the gained-cell reading (the flip-driven error births carry the
# flipped thing's canvas — the direction road's presence count). Law: docs/brain/revise/PREREG-REVISE-1.md.
from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import mkdtemp
from unittest import mock

import numpy as np

import creature.mind as mind_mod
from tools.brain import revise_bench as RB


class TestToyWorldDeterminism(unittest.TestCase):
    def test_one_life_twice_byte_identical(self):
        """G-DET's unit form: the flip twin lived twice from one seed — checkpoint rows, answering
        sets and the belief store's bytes identical to the last bit."""
        a = RB.live_toy(RB.T2_FLIP_SEED, True, mkdtemp(), arm="det-a")
        b = RB.live_toy(RB.T2_FLIP_SEED, True, mkdtemp(), arm="det-b")
        self.assertEqual(json.dumps(a["checkpoints"], sort_keys=True),
                         json.dumps(b["checkpoints"], sort_keys=True))
        self.assertEqual(a["store_bytes"], b["store_bytes"], "the belief stores are byte-identical")
        self.assertEqual(a["counts"], b["counts"])

    def test_flip_renames_exactly_thing_a(self):
        arm = RB.live_toy(RB.T2_PILOT_SEED, True, mkdtemp(), arm="naming")
        mt = arm["moment_thing"]
        pre = [m for m in mt if m < RB.T2_FLIP_MOMENT]
        post = [m for m in mt if m >= RB.T2_FLIP_MOMENT]
        self.assertEqual(len(pre), RB.T2_FLIP_MOMENT, "presence: every pre-flip moment named")
        self.assertTrue(all(mt[m] == arm["things"][m % len(arm["things"])] for m in pre),
                        "pre-flip: every thing carries its own name")
        a_post = [m for m in post if arm["things"][m % len(arm["things"])] == RB.T2_A_THING]
        self.assertEqual(len(a_post), RB.T2_R_POST, "presence: thing A shown once per post-flip round")
        self.assertTrue(all(mt[m] == RB.T2_B_WORD for m in a_post),
                        "post-flip: thing A's visual is named with thing B's word, every time")
        others = [m for m in post if arm["things"][m % len(arm["things"])] != RB.T2_A_THING]
        self.assertTrue(all(mt[m] == arm["things"][m % len(arm["things"])] for m in others),
                        "post-flip: every other thing keeps its own name")

    def test_plant_arm_world_never_changes(self):
        """G-PLANT (a)'s world half: the driver claims the flip; the taught names never flip."""
        arm = RB.live_toy(RB.T2_FLIP_SEED, True, mkdtemp(), arm="plant", plant=True)
        mt = arm["moment_thing"]
        self.assertTrue(all(mt[m] == arm["things"][m % len(arm["things"])] for m in mt),
                        "the plant's world is the UNCHANGED world at every moment")
        self.assertTrue(arm["flip"] and arm["plant"], "the driver did claim the flip schedule")
        self.assertEqual(len(arm["checkpoints"]), 1 + len(RB.T2_CHECK_POST),
                         "the plant arm drove the full checkpoint schedule (it claims the flip)")


class TestChainPin(unittest.TestCase):
    """G-CHAIN (the law §2): the seam tested at the seam — the bench drives the SAME two functions
    mind.py:3350/3385 calls (questions_why -> think_laws.believe), imported, never copied."""

    def test_same_two_function_objects(self):
        self.assertIs(RB.questions_why, mind_mod.questions_why,
                      "the bench's why() IS creature/mind.py's questions_why (one object)")
        self.assertIs(RB.think_laws, mind_mod.think_laws,
                      "the bench's think_laws IS creature/mind.py's think_laws (one module object)")
        self.assertIs(RB.think_laws.believe, mind_mod.think_laws.believe)

    def test_the_benchs_call_form_is_the_production_form(self):
        """mind.py:3373-3386's form: sight cells filtered from record['cells'], record['episodes'],
        org.t, the store path, ledgers= and clash_enabled= passed through."""
        record = {"cells": [("sight", 5), ("words", 9), ("sight", 7)], "episodes": [3, 4]}
        seen = {}

        class _Org:
            t = 4242

        def fake_why(org, ledgers, episodes, word):
            seen["why"] = (org, ledgers, episodes, word)
            return record

        def fake_believe(word, cells, episode_ids, moment, path, **kw):
            seen["believe"] = (word, cells, episode_ids, moment, path, kw)
            return {"kind": "belief"}

        org, ledgers, episodes = _Org(), {"sight": {5: {"w"}}}, object()
        with mock.patch.object(RB, "questions_why", fake_why):
            with mock.patch.object(RB.think_laws, "believe", fake_believe):
                RB.drive_belief(org, ledgers, episodes, "w", "/tmp/x.jsonl", clash_enabled=True)
        self.assertEqual(seen["why"], (org, ledgers, episodes, "w"),
                         "questions_why(org, ledgers, episodes, word) — mind.py:3350's own order")
        word, cells, episode_ids, moment, path, kw = seen["believe"]
        self.assertEqual((word, cells, episode_ids, moment), ("w", [5, 7], [3, 4], 4242),
                         "the word's SIGHT cells (its look), the record's episodes, org.t")
        self.assertEqual(kw.get("ledgers"), ledgers)
        self.assertIn("clash_enabled", kw)

    def test_the_seams_source_still_calls_them(self):
        src = Path(mind_mod.__file__).read_text()
        self.assertIn("record = questions_why(self.org, ledgers, self.episodes, word)", src,
                      "mind.py's word-item seam still asks questions_why (the pinned form)")
        self.assertIn('think_laws.believe(word, sight_cells, record["episodes"], self.org.t', src,
                      "mind.py's word-item seam still calls think_laws.believe (the pinned form)")


class TestPilotRefusal(unittest.TestCase):
    """G-PLANT (a), AMENDMENT 1's form: the doctored no-flip-landed tier-2 bench must read
    NOT-GRADABLE — the refusal's trigger is the flip's EVIDENCE absent (zero post-flip episodes
    carry the flipped naming), never a grade."""

    def test_unlanded_flip_refuses(self):
        arm = RB.live_toy(RB.T2_FLIP_SEED, True, mkdtemp(), arm="plant", plant=True)
        fb = RB.flip_born(arm)
        self.assertEqual(fb["flip_evidence_n"], 0,
                         "the refusal's trigger: the flip's evidence is ABSENT (the plant's world "
                         "never changed, though the driver claims it)")
        out = RB.grade_tier2({"arm": arm, "reading": RB.pilot_reading(arm)}, arm, [])
        self.assertFalse(out["gradable"], "no gradable run without the flip's evidence")

    def test_graded_marks_never_computed_on_a_refused_arm(self):
        out = RB.run_tier2(mkdtemp(), pilot_seed=RB.T2_FLIP_SEED, flip_seed=RB.T2_FLIP_SEED,
                           null_seeds=RB.T2_NULL_SEEDS[:2], plant=True)
        self.assertEqual(out["tier2_verdict"], "NOT-GRADABLE")
        for mark in ("M-T2-ACCRETE", "M-T2-DIR", "M-T2-LOCAL"):
            self.assertEqual(out["marks"][mark]["pass"], "NOT-GRADED",
                             f"{mark}: a refused bench never grades")


class TestAmendment1Forms(unittest.TestCase):
    """AMENDMENT 1's pins (the seat, 2026-10-10 20:2x +0400): the margin is the law's constant, the
    accretion counter fires on the flip arm and never on a no-flip twin."""

    def test_the_margin_is_the_law_constant(self):
        self.assertEqual(RB.T2_MARGIN, 0.18, "the amendment's text: half the first pilot's 0.365, "
                                             "fixed, never tuned after a graded run")

    def test_accretion_fires_on_the_flip_arm_never_on_the_null(self):
        flip_arm = RB.live_toy(RB.T2_FLIP_SEED, True, mkdtemp(), arm="a-flip")
        fb = RB.flip_born(flip_arm)
        self.assertGreaterEqual(fb["flip_evidence_n"], 1, "presence: the flip landed")
        self.assertGreaterEqual(fb["flip_born_n"], 1,
                                "the flip twin's standing gains >= 1 flip-born cell")
        null_arm = RB.live_toy(RB.T2_NULL_SEEDS[0], False, mkdtemp(), arm="a-null")
        nfb = RB.flip_born(null_arm)
        self.assertEqual(nfb["flip_evidence_n"], 0, "no flip in the twin's world")
        self.assertEqual(nfb["flip_born_n"], 0,
                         "the no-flip twin gains ZERO cells born on the other thing's canvas")

    def test_grade_tier2_binds_when_the_flip_lands(self):
        pilot_arm = RB.live_toy(RB.T2_PILOT_SEED, True, mkdtemp(), arm="a-pilot")
        flip_arm = RB.live_toy(RB.T2_FLIP_SEED, True, mkdtemp(), arm="a-flip")
        null_arms = [RB.live_toy(s, False, mkdtemp(), arm=f"a-null{i}")
                     for i, s in enumerate(RB.T2_NULL_SEEDS)]     # the law's own 10, never a subset
        out = RB.grade_tier2({"arm": pilot_arm, "reading": RB.pilot_reading(pilot_arm)},
                             flip_arm, null_arms)
        self.assertTrue(out["gradable"])
        for mark in ("M-T2-ACCRETE", "M-T2-DIR", "M-T2-LOCAL"):
            self.assertIn(mark, out["marks"])
            self.assertIn("pass", out["marks"][mark])
        self.assertTrue(out["marks"]["M-T2-ACCRETE"]["pass"],
                        "the flip arm accretes, all 10 nulls read 0")
        self.assertTrue(out["marks"]["M-T2-LOCAL"]["pass"], "the bystanders' bytes never move")


class TestDirectionRoadPresence(unittest.TestCase):
    """The flip-driven error births: at least one cell gained by the flipped word's answering set
    holds the flipped THING's canvas (the direction road exists, presence printed)."""

    def test_gained_cells_carry_thing_as_canvas(self):
        arm = RB.live_toy(RB.T2_PILOT_SEED, True, mkdtemp(), arm="dir")
        reading = RB.pilot_reading(arm)
        gained = reading["gained_cells"]
        self.assertGreater(len(gained), 0, "presence: the answering set gained cells post-flip")
        toward = [g for g in gained if g["cos_to_a"] > g["cos_to_b"]]
        self.assertGreater(len(toward), 0,
                           "presence: >= 1 gained cell holds thing A's canvas (closer to A's cluster)")


class TestBenchReportShape(unittest.TestCase):
    def test_verdict_block_carries_every_mark_with_presence(self):
        t1 = RB.run_tier1(mkdtemp())
        order = RB.run_order_null(mkdtemp())
        bench_b = RB.run_bench_b()
        marks = RB.verdicts_tier1_and_b(t1, order, bench_b)
        for mark in ("M-T1-FORM", "M-T1-ORDER", "M-T1-LOCAL", "M-T1-DIR",
                     "M-B-DIR", "M-B-FLOOR", "M-B-SIGN"):
            self.assertIn(mark, marks)
            self.assertIn("pass", marks[mark])
            self.assertIn("bar", marks[mark])


if __name__ == "__main__":
    unittest.main()
