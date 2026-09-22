# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE), brief
# item 2: tools/evolve.py — the worker's shadow/checkpoint/twin/grading/regression-bar machinery.
"""tests/tools/test_evolve_worker.py"""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import tools.evolve as ev
from creature.genes import apply_mutation
from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import world

ROOT = Path(__file__).resolve().parent.parent.parent
BASE = (ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome").read_text()
FIXTURE = ROOT / "tests" / "creature" / "G4-evolve-test.genome"
if not FIXTURE.exists():
    # created by tests/creature/test_evolve_adoption.py's own module-level _write_fixture() -- but a
    # solo run of THIS file (unittest discovery may import files in any order) must not depend on that.
    FIXTURE.write_text(BASE.rstrip("\n") + "\n" + (
        "CURIOSITY interests 50 operators recombine generalize specialize bridge\n"
        "PARK     after 3 identical dead-ends reopen on new-sense\n"
        "EVOLVE   every 6 h; mutate 1 gene within bounds; judge on the last 2 h; adopt at sleep under the regression bar\n"
    ))


def _tmp() -> Path:
    return Path(tempfile.mkdtemp())


def _png(rgb) -> bytes:
    buf = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(buf, format="PNG"); return buf.getvalue()


def _build_tape(root: Path, n: int, at_fn, seed: int = 4242, start: int = 0) -> None:
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    for i in range(start, start + n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        at = at_fn(i)
        if i % 7 != 0:
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt", at=at)
        tape.publish("eye", _png(rgb), {"moment": moment, "source": "test"}, "png", at=at)


def _at(i: int) -> str:
    # 2 fake minutes per canvas -- 300 canvases spans ~10 fake hours
    return f"2026-09-23T{(i * 2) // 60:02d}:{(i * 2) % 60:02d}:00.000Z"


class TestRegressionBar(unittest.TestCase):
    def test_improvement_with_no_regression_passes(self) -> None:
        inc = {"q1_seen": 0.80, "confirmed_share": None, "reward_mean": None, "frames_filed": None,
               "act_pass": None, "sentence_pass": None, "wall_s": 10.0}
        mut = {"q1_seen": 0.82, "confirmed_share": None, "reward_mean": None, "frames_filed": None,
               "act_pass": None, "sentence_pass": None, "wall_s": 10.5}
        verdict, reason = ev.regression_bar(inc, mut)
        self.assertEqual(verdict, "PASS")
        self.assertIn("q1_seen", reason)

    def test_no_improvement_refuses(self) -> None:
        inc = {"q1_seen": 0.80, "wall_s": 10.0}
        mut = {"q1_seen": 0.805, "wall_s": 10.0}   # under the 0.01 margin
        verdict, reason = ev.regression_bar(inc, mut)
        self.assertEqual(verdict, "REFUSED")
        self.assertIn("no reading cleared", reason)

    def test_a_regression_on_one_mark_refuses_even_if_another_improves(self) -> None:
        inc = {"q1_seen": 0.80, "reward_mean": 0.30, "wall_s": 10.0}
        mut = {"q1_seen": 0.75, "reward_mean": 0.40, "wall_s": 10.0}   # q1 regressed, reward improved
        verdict, reason = ev.regression_bar(inc, mut)
        self.assertEqual(verdict, "REFUSED")
        self.assertIn("regressed", reason)

    def test_cost_over_1_2x_refuses_even_with_an_improvement(self) -> None:
        inc = {"q1_seen": 0.80, "wall_s": 10.0}
        mut = {"q1_seen": 0.90, "wall_s": 13.0}   # 1.3x
        verdict, reason = ev.regression_bar(inc, mut)
        self.assertEqual(verdict, "REFUSED")
        self.assertIn("cost", reason)

    def test_cost_at_exactly_1_2x_passes_the_cost_clause(self) -> None:
        inc = {"q1_seen": 0.80, "wall_s": 10.0}
        mut = {"q1_seen": 0.90, "wall_s": 12.0}   # exactly 1.2x
        verdict, reason = ev.regression_bar(inc, mut)
        self.assertEqual(verdict, "PASS")

    def test_graded_pass_regressing_to_fail_refuses(self) -> None:
        inc = {"q1_seen": 0.80, "act_pass": True, "wall_s": 10.0}
        mut = {"q1_seen": 0.90, "act_pass": False, "wall_s": 10.0}
        verdict, reason = ev.regression_bar(inc, mut)
        self.assertEqual(verdict, "REFUSED")
        self.assertIn("act_pass", reason)

    def test_missing_readings_on_either_side_are_neither_regression_nor_improvement(self) -> None:
        inc = {"q1_seen": None, "reward_mean": 0.30, "wall_s": 10.0}
        mut = {"q1_seen": 0.90, "reward_mean": 0.35, "wall_s": 10.0}
        verdict, reason = ev.regression_bar(inc, mut)
        self.assertEqual(verdict, "PASS")   # reward_mean improved by 0.05 >= its 0.02 margin


class TestHoursBetween(unittest.TestCase):
    def test_two_hours(self) -> None:
        self.assertAlmostEqual(ev.hours_between("2026-09-23T00:00:00.000Z", "2026-09-23T02:00:00.000Z"), 2.0)

    def test_zero(self) -> None:
        self.assertAlmostEqual(ev.hours_between("2026-09-23T00:00:00.000Z", "2026-09-23T00:00:00.000Z"), 0.0)


class TestShadowAndCheckpoints(unittest.TestCase):
    def test_build_advance_checkpoint_and_find_near(self) -> None:
        root = _tmp()
        _build_tape(root, 60, _at)
        shadow_root = _tmp() / "shadow"
        shadow = ev.build_or_resume_shadow(shadow_root, FIXTURE, root)
        n = ev.advance_shadow(shadow, root)
        self.assertGreater(n, 0)
        self.assertEqual(shadow.evolve_epoch, 0)

        checkpoints_dir = _tmp() / "checkpoints"
        cp1 = ev.checkpoint_shadow(shadow, checkpoints_dir, "2026-09-23T01:00:00.000Z")
        self.assertTrue((cp1 / "state" / "organism.npz").exists())
        self.assertTrue((cp1 / "GENOME.genome").exists())
        meta = json.loads((cp1 / "META.json").read_text())
        self.assertEqual(meta["n"], 1)
        self.assertEqual(meta["last_seq"], shadow.last_seq)

        found = ev.checkpoint_near(checkpoints_dir, "2026-09-23T02:00:00.000Z")
        self.assertIsNotNone(found)
        self.assertEqual(found["n"], 1)

        too_early = ev.checkpoint_near(checkpoints_dir, "2026-09-23T00:00:00.000Z")
        self.assertIsNone(too_early, "a checkpoint AFTER the target must never be returned")

        latest = ev.latest_checkpoint(checkpoints_dir)
        self.assertEqual(latest["n"], 1)

    def test_advance_shadow_up_to_seq_stops_there(self) -> None:
        root = _tmp()
        _build_tape(root, 60, _at)
        shadow_root = _tmp() / "shadow"
        shadow = ev.build_or_resume_shadow(shadow_root, FIXTURE, root)
        rows = list(read_tape(root))
        cut = rows[len(rows) // 2]["seq"]
        n = ev.advance_shadow(shadow, root, up_to_seq=cut)
        self.assertEqual(shadow.last_seq, cut)
        self.assertLess(n, len(rows))

    def test_shadow_resumes_and_is_epoch_aware(self) -> None:
        root = _tmp()
        _build_tape(root, 60, _at)
        shadow_root = _tmp() / "shadow"
        shadow = ev.build_or_resume_shadow(shadow_root, FIXTURE, root)
        ev.advance_shadow(shadow, root)
        last_seq = shadow.last_seq
        shadow2 = ev.build_or_resume_shadow(shadow_root, FIXTURE, root)
        self.assertEqual(shadow2.last_seq, last_seq)
        self.assertEqual(shadow2.evolve_epoch, 0)


class TestTapeSlice(unittest.TestCase):
    def test_slice_bounds_are_exclusive_inclusive(self) -> None:
        root = _tmp()
        _build_tape(root, 20, _at)
        rows = list(read_tape(root))
        seqs = sorted(int(r["seq"]) for r in rows)
        lo, hi = seqs[5], seqs[15]
        s = ev.tape_slice(root, lo, hi)
        self.assertTrue(all(lo < int(r["seq"]) <= hi for r in s))
        self.assertEqual(len(s), sum(1 for x in seqs if lo < x <= hi))


class TestJudgingRoundEndToEnd(unittest.TestCase):
    """Formalizes the scratch-validated two-stage flow: checkpoint early, more tape arrives, judge the
    real slice with a FORCED mutation (never the rng — this class tests the MACHINERY, not the draw)."""

    def _two_stage_shadow(self):
        root = _tmp()
        _build_tape(root, 100, _at)
        shadow_root = _tmp() / "shadow"
        shadow = ev.build_or_resume_shadow(shadow_root, FIXTURE, root)
        ev.advance_shadow(shadow, root)
        checkpoints_dir = _tmp() / "checkpoints"
        ev.checkpoint_shadow(shadow, checkpoints_dir, "2026-09-23T02:00:00.000Z")
        _build_tape(root, 200, _at, seed=9999, start=100)
        ev.advance_shadow(shadow, root)
        return root, shadow, checkpoints_dir

    def test_a_real_slice_is_graded_and_the_bar_reads_a_verdict(self) -> None:
        root, shadow, checkpoints_dir = self._two_stage_shadow()
        runs_dir = _tmp()
        proposal = ev.run_judging_round(root, shadow, checkpoints_dir, "2026-09-23T09:05:00.000Z", judge_h=2.0,
                                         seed=20260923, proposal_no=1, runs_dir=runs_dir, forced_mutation=("KWTA.k", 8))
        self.assertIn(proposal["verdict"], ("PASS", "REFUSED"))
        self.assertGreater(proposal["slice_rows"], 0)
        self.assertIsNotNone(proposal["incumbent"]["q1_seen"])
        self.assertIsNotNone(proposal["mutant"]["q1_seen"])
        self.assertIsNotNone(proposal["q1_seen_start"])
        self.assertEqual(proposal["gene"], "KWTA.k")
        self.assertEqual(proposal["value"], 8)
        # PAIRED on the same rows -- both twins graded over the identical slice
        self.assertEqual(proposal["incumbent"]["tape_rows"], proposal["mutant"]["tape_rows"])

    def test_no_checkpoint_old_enough_is_not_gradable(self) -> None:
        root, shadow, checkpoints_dir = self._two_stage_shadow()
        runs_dir = _tmp()
        # judge "now" only 1 h after the checkpoint's own "at" -- judge_h=2 means target = now-2h, which
        # precedes the checkpoint -- checkpoint_near must find nothing.
        proposal = ev.run_judging_round(root, shadow, checkpoints_dir, "2026-09-23T03:00:00.000Z", judge_h=2.0,
                                         seed=20260923, proposal_no=1, runs_dir=runs_dir, forced_mutation=("KWTA.k", 8))
        self.assertEqual(proposal["verdict"], "REFUSED")
        self.assertIn("not gradable", proposal["reason"])

    def test_write_proposal_and_next_proposal_no(self) -> None:
        root, shadow, checkpoints_dir = self._two_stage_shadow()
        runs_dir = _tmp()
        proposal = ev.run_judging_round(root, shadow, checkpoints_dir, "2026-09-23T09:05:00.000Z", judge_h=2.0,
                                         seed=20260923, proposal_no=1, runs_dir=runs_dir, forced_mutation=("KWTA.k", 8))
        evolve_dir = _tmp()
        self.assertEqual(ev._next_proposal_no(evolve_dir), 1)
        path = ev.write_proposal(evolve_dir, proposal)
        self.assertTrue(path.exists())
        self.assertEqual(json.loads(path.read_text())["no"], 1)
        self.assertEqual(ev._next_proposal_no(evolve_dir), 2)


class TestNegativeControlOnSyntheticTape(unittest.TestCase):
    """Brief item 4's own shape, run end to end on a small synthetic closed-tape stand-in (the REAL
    seam-1 negative control is run separately, out of the suite — see the report — because it needs a
    copy of a real closed life's tape under scratch/, far too large/slow for a unit test)."""

    def test_planted_bad_and_null_are_both_refused(self) -> None:
        root = _tmp()
        _build_tape(root, 300, _at)
        out = _tmp()
        results = ev.run_negative_control(root, FIXTURE, out, judge_h=2.0)
        self.assertIn("planted_bad", results)
        self.assertIn("null", results)
        self.assertEqual(results["planted_bad"]["gene"], "BIRTH.theta_n")
        self.assertEqual(results["planted_bad"]["value"], 0.5)
        self.assertEqual(results["null"]["gene"], "DELTA.lr")
        self.assertEqual(results["null"]["value"], 0.051)
        self.assertTrue((out / "NEGATIVE-CONTROL-planted_bad.json").exists())
        self.assertTrue((out / "NEGATIVE-CONTROL-null.json").exists())
        # both are printed regardless of verdict (never silently loosened) -- and on THIS toy tape both
        # are expected to read REFUSED, matching the mechanism's own design intent.
        self.assertEqual(results["planted_bad"]["verdict"], "REFUSED")
        self.assertEqual(results["null"]["verdict"], "REFUSED")


if __name__ == "__main__":
    unittest.main()
