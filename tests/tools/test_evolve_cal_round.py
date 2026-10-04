# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:58 +0400 — PREREG-EVOLVE-CAL §1 (D6 CPU cost, the calibrated round, the confirmation round, D8 wiring): tests FIRST.
"""tests/tools/test_evolve_cal_round.py — tools/evolve.py's judging round with the calibrated gate.

`run_judging_round(…, bands=None)` is the LEGACY two-verdict round (every existing test of tests/tools/test_evolve_worker.py keeps its meaning); with a
BANDS dict it adds `gate` (the three-verdict reading of the twins' paired readings: incumbent FIRST, Δ = mutant − incumbent), `not_gradable` (D4/D5)
and never says PASS by itself: an IMPROVED mutant waits for its confirmation round on the next disjoint slice (`finalize_calibrated_round`, a
pending record under evolve/). Both twins' readings carry the PROCESS CPU-seconds (D6) and the load / pressure at start and end (A3).
"""
from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import numpy as np
from PIL import Image

import tools.evolve as ev
import tools.evolve_bands as eb
from creature.genes import apply_mutation
from creature.tape import Tape
from genome import world

ROOT = Path(__file__).resolve().parent.parent.parent
BASE = (ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome").read_text()
FIXTURE = ROOT / "tests" / "creature" / "G4-evolve-test.genome"
if not FIXTURE.exists():
    FIXTURE.write_text(BASE.rstrip("\n") + "\n" + (
        "CURIOSITY interests 50 operators recombine generalize specialize bridge\n"
        "PARK     after 3 identical dead-ends reopen on new-sense\n"
        "EVOLVE   every 6 h; mutate 1 gene within bounds; judge on the last 2 h; adopt at sleep under the regression bar\n"))


def _png(rgb) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _at(i: int) -> str:
    return f"2026-09-23T{(i * 2) // 60:02d}:{(i * 2) % 60:02d}:00.000Z"


def _build_tape(root: Path, n: int, seed: int = 4242, start: int = 0) -> None:
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    for i in range(start, start + n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        if i % 7 != 0:
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt", at=_at(i))
        tape.publish("eye", _png(rgb), {"moment": moment, "source": "test"}, "png", at=_at(i))


def band(kind="normal", edge=None, grid=None, rng=None):
    return {"kind": kind, "grid": grid, "edge": edge, "range": rng, "sigma_hat": None, "n": 21, "distinct": 5}


def bands(edge_scale=1.0):
    return {"law": "PREREG-EVOLVE-CAL", "slice": "S1", "n": 21, "df": 20, "alpha_side": 0.0083, "cost_policy_cap": 1.2,
            "dims": {"q1_seen": band(edge=5.5 / 110 * edge_scale, grid=1 / 110), "frames_filed": band(edge=3.2 * edge_scale, grid=1.0),
                     "confirmed_share": band(edge=0.03 * edge_scale), "ln_cpu": band(edge=0.25 * edge_scale)}}


def crafted(q1_items, frames=30, share=0.45, cpu=2000.0, wall=2000.0):
    return {"q1_seen": q1_items / 110, "confirmed_share": share, "confirmed_graded": True, "reward_mean": 0.0, "act_pass": True,
            "act_graded": True, "frames_filed": frames, "sentence_pass": None, "sentence_graded": False, "wall_s": wall, "cpu_s": cpu,
            "tape_rows": 100, "journal_rows": 90, "detail": {"surprise": {}, "sentence": {"missions": 5}, "act": {}}}


class _Life(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="evolve-cal-round-"))
        cls.root = cls.tmp / "life"
        _build_tape(cls.root, 40)
        cls.shadow = ev.build_or_resume_shadow(cls.tmp / "shadow", FIXTURE, cls.root)
        ev.advance_shadow(cls.shadow, cls.root)
        cls.cps = cls.tmp / "checkpoints"
        ev.checkpoint_shadow(cls.shadow, cls.cps, "2026-09-23T02:00:00.000Z")
        _build_tape(cls.root, 60, seed=9999, start=40)
        ev.advance_shadow(cls.shadow, cls.root)
        cls.n = 0

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def judge(self, **kw) -> dict:
        type(self).n += 1
        return ev.run_judging_round(self.root, self.shadow, self.cps, "2026-09-23T09:05:00.000Z", judge_h=2.0, seed=20260923,
                                    proposal_no=self.n, runs_dir=self.tmp / f"runs-{self.n}", **kw)


class TestGradeTwinCost(unittest.TestCase):
    def test_grade_twin_records_the_cpu_seconds_and_the_machine_beside_the_wall(self) -> None:
        import types
        mind = types.SimpleNamespace(think_counters={}, acts_chosen={}, act_mismatches=0, glances_confirmed=0, glances_surprised=0,
                                     genome=types.SimpleNamespace(declared={}))
        root = Path(tempfile.mkdtemp())
        (root / "journal").mkdir()
        machine = {"load0": [1.0, 1.0, 1.0], "load1": [2.0, 1.5, 1.2], "psi0": {"cpu_some_avg10": 0.5}, "psi1": {"cpu_some_avg10": 1.5}}
        r = ev.grade_twin(mind, root, root / "GENOME.genome", [], 12.5, cpu_s=11.25, machine=machine)
        self.assertEqual(r["cpu_s"], 11.25)
        self.assertEqual(r["wall_s"], 12.5)
        self.assertEqual(r["load1"], [2.0, 1.5, 1.2])
        self.assertEqual(r["psi1"], {"cpu_some_avg10": 1.5})
        r2 = ev.grade_twin(mind, root, root / "GENOME.genome", [], 12.5)
        self.assertIsNone(r2["cpu_s"], "no CPU reading is a missing reading, never a zero")


class TestRound(_Life):
    def test_a_legacy_round_keeps_its_vocabulary_and_gains_the_cost_fields(self) -> None:
        p = self.judge(forced_mutation=("KWTA.k", 8))
        self.assertIn(p["verdict"], ("PASS", "REFUSED"))
        self.assertNotIn("gate", p)
        for side in ("incumbent", "mutant"):
            self.assertGreater(p[side]["cpu_s"], 0, side)
            self.assertGreater(p[side]["wall_s"], 0, side)
            self.assertEqual(len(p[side]["load0"]), 3)
            self.assertEqual(len(p[side]["load1"]), 3)
            self.assertIn("cpu_some_avg10", p[side]["psi0"])
        self.assertEqual(p["gene"], "KWTA.k")

    def test_a_calibrated_round_carries_gate_and_not_gradable_and_never_passes_by_itself(self) -> None:
        p = self.judge(forced_mutation=("KWTA.k", 8), bands=bands(edge_scale=1000.0))
        self.assertEqual(p["gate"]["verdict"], "NO EVIDENCE", "bands a thousand times wide: nothing is outside them")
        self.assertEqual(p["verdict"], "REFUSED")
        self.assertEqual(sorted(p["not_gradable"]), ["act_pass", "reward_mean", "sentence_pass"])
        self.assertIn("identical by construction", p["not_gradable"]["reward_mean"]["reason"])
        self.assertIsNotNone(p["gate"]["cost"]["wall_ratio"], "the wall ratio is printed beside the CPU ratio")
        self.assertIsNotNone(p["gate"]["cost"]["ratio"])
        self.assertEqual(p["gate"]["reason"], p["reason"])

    def test_the_gate_reads_incumbent_first_and_delta_is_mutant_minus_incumbent(self) -> None:
        def grade(mind, twin_root, genome_path, tape_slice, wall_s, cpu_s=None, machine=None):
            return crafted(100) if Path(twin_root).name == "incumbent" else crafted(108)
        with unittest.mock.patch.object(ev, "grade_twin", side_effect=grade):
            p = self.judge(forced_mutation=("KWTA.k", 8), bands=bands())
        self.assertEqual(p["gate"]["dims"]["q1_seen"]["incumbent"], 100 / 110)
        self.assertEqual(p["gate"]["dims"]["q1_seen"]["mutant"], 108 / 110)
        self.assertEqual(p["gate"]["verdict"], "IMPROVED")
        self.assertEqual(p["verdict"], "REFUSED", "an IMPROVED round is not a PASS: the confirmation round decides (edit 21:05, a gap the sweep named)")
        def grade_bad(mind, twin_root, genome_path, tape_slice, wall_s, cpu_s=None, machine=None):
            return crafted(108) if Path(twin_root).name == "incumbent" else crafted(100)
        with unittest.mock.patch.object(ev, "grade_twin", side_effect=grade_bad):
            q = self.judge(forced_mutation=("KWTA.k", 8), bands=bands())
        self.assertEqual(q["gate"]["verdict"], "REGRESSED", "the swapped readings read the opposite verdict")

    def test_the_cost_regression_reads_cpu_not_wall(self) -> None:
        def grade(mind, twin_root, genome_path, tape_slice, wall_s, cpu_s=None, machine=None):
            inc = Path(twin_root).name == "incumbent"
            return crafted(100 if inc else 108, cpu=2000.0 if inc else 3200.0, wall=2000.0)    # CPU ×1.6, wall flat
        with unittest.mock.patch.object(ev, "grade_twin", side_effect=grade):
            p = self.judge(forced_mutation=("KWTA.k", 8), bands=bands())
        self.assertTrue(p["gate"]["cost"]["regressed"])
        self.assertEqual(p["gate"]["verdict"], "REGRESSED")
        def grade_wall(mind, twin_root, genome_path, tape_slice, wall_s, cpu_s=None, machine=None):
            inc = Path(twin_root).name == "incumbent"
            return crafted(100 if inc else 108, cpu=2000.0, wall=2000.0 if inc else 3200.0)     # wall ×1.6, CPU flat (a load change)
        with unittest.mock.patch.object(ev, "grade_twin", side_effect=grade_wall):
            q = self.judge(forced_mutation=("KWTA.k", 8), bands=bands())
        self.assertFalse(q["gate"]["cost"]["regressed"], "a load change moves wall, not the process CPU")
        self.assertEqual(q["gate"]["verdict"], "IMPROVED")

    def test_the_twins_cpu_seconds_come_from_process_time_around_each_twin(self) -> None:
        # edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:05 +0400 — pins D6: the CPU handed to grade_twin is the process_time delta around
        # EACH twin (incumbent 7.0 s, mutant 12.0 s here), never the wall time
        seen = {}
        def grade(mind, twin_root, genome_path, tape_slice, wall_s, cpu_s=None, machine=None):
            seen[Path(twin_root).name] = (wall_s, cpu_s, machine)
            return crafted(100)
        ticks = iter([100.0, 107.0, 200.0, 212.0, 300.0, 400.0])
        with unittest.mock.patch.object(ev.time, "process_time", side_effect=lambda: next(ticks)), \
                unittest.mock.patch.object(ev, "grade_twin", side_effect=grade):
            self.judge(forced_mutation=("KWTA.k", 8))
        self.assertEqual(seen["incumbent"][1], 7.0)
        self.assertEqual(seen["mutant"][1], 12.0)
        self.assertNotEqual(seen["incumbent"][1], seen["incumbent"][0], "CPU is not the wall time")
        self.assertEqual(sorted(seen["mutant"][2]), ["load0", "load1", "psi0", "psi1"])

    def test_an_unforced_round_draws_through_the_redraw(self) -> None:
        inc_text = (self.cps / "1" / "GENOME.genome").read_text()
        fake = (apply_mutation(inc_text, "KWTA.k", 7), "KWTA.k", 7, 3)
        # both proposers are patched to the same KWTA 7: a mutant that bypasses mutate_distinct must fail the call-count assertion QUICKLY, not run a real
        # random mutation (the sweep's first run of that mutant ran 41 minutes before it was killed)
        with unittest.mock.patch.object(ev, "mutate_distinct", return_value=fake) as m, \
                unittest.mock.patch.object(ev, "mutate_genome_text", return_value=fake[:3]):
            p = self.judge()
        self.assertEqual(m.call_count, 1)
        self.assertEqual((p["gene"], p["value"]), ("KWTA.k", 7))
        self.assertEqual(p["draws"], 3, "the number of draws taken is on the record (1 = nothing collided)")
        self.assertEqual(m.call_args[0][0], inc_text, "the redraw reads the CHECKPOINT's own incumbent text")
        self.assertEqual(m.call_args[0][2], self.shadow.evolve_epoch + 1)

    def test_a_not_gradable_round_has_no_gate(self) -> None:
        p = ev.run_judging_round(self.root, self.shadow, self.cps, "2026-09-23T03:00:00.000Z", judge_h=2.0, seed=20260923, proposal_no=99,
                                 runs_dir=self.tmp / "runs-ng", forced_mutation=("KWTA.k", 8), bands=bands())
        self.assertIn("not gradable", p["reason"])
        self.assertNotIn("gate", p)


def _proposal(no, verdict, lo, hi, gene="KWTA.k", value=4, with_gate=True):
    p = {"no": no, "epoch": 0, "gene": gene, "value": value, "slice_from_seq": lo, "slice_to_seq": hi, "verdict": "REFUSED", "reason": "x"}
    if with_gate:
        p["gate"] = {"verdict": verdict, "reason": f"{verdict}: x"}
    return p


class TestConfirmationRound(unittest.TestCase):
    def d(self) -> Path:
        return Path(tempfile.mkdtemp(prefix="evolve-cal-pending-"))

    def test_a_first_improved_waits_and_is_not_a_pass(self) -> None:
        d = self.d()
        out = ev.finalize_calibrated_round(_proposal(6, "IMPROVED", 1000, 1500), d, shadow_epoch=0)
        self.assertEqual(out["verdict"], "REFUSED")
        self.assertIn("awaiting confirmation", out["state"])
        pending = ev.load_pending(d)
        self.assertEqual((pending["proposal"]["gene"], pending["proposal"]["value"], pending["epoch"]), ("KWTA.k", 4, 0))
        self.assertEqual(ev.pending_forced_mutation(d, shadow_epoch=0)[0], ("KWTA.k", 4))

    def test_no_evidence_or_regressed_leaves_no_pending(self) -> None:
        for v in ("NO EVIDENCE", "REGRESSED"):
            d = self.d()
            out = ev.finalize_calibrated_round(_proposal(6, v, 1000, 1500), d, shadow_epoch=0)
            self.assertEqual(out["verdict"], "REFUSED")
            self.assertIsNone(ev.load_pending(d), v)

    def test_improved_twice_on_disjoint_slices_passes_and_clears_the_pending(self) -> None:
        d = self.d()
        ev.finalize_calibrated_round(_proposal(6, "IMPROVED", 1000, 1500), d, shadow_epoch=0)
        out = ev.finalize_calibrated_round(_proposal(7, "IMPROVED", 2000, 2500), d, shadow_epoch=0)
        self.assertEqual(out["verdict"], "PASS")
        self.assertTrue(out["confirmation"]["adopt"])
        self.assertEqual(out["confirmation"]["of"], 6)
        self.assertIsNone(ev.load_pending(d))

    def test_a_confirmation_that_reads_no_evidence_refuses_and_clears(self) -> None:
        d = self.d()
        ev.finalize_calibrated_round(_proposal(6, "IMPROVED", 1000, 1500), d, shadow_epoch=0)
        out = ev.finalize_calibrated_round(_proposal(7, "NO EVIDENCE", 2000, 2500), d, shadow_epoch=0)
        self.assertEqual(out["verdict"], "REFUSED")
        self.assertFalse(out["confirmation"]["adopt"])
        self.assertIsNone(ev.load_pending(d))

    def test_an_overlapping_confirmation_keeps_the_pending(self) -> None:
        d = self.d()
        ev.finalize_calibrated_round(_proposal(6, "IMPROVED", 1000, 1500), d, shadow_epoch=0)
        out = ev.finalize_calibrated_round(_proposal(7, "IMPROVED", 1400, 2000), d, shadow_epoch=0)
        self.assertEqual(out["verdict"], "REFUSED")
        self.assertTrue(out["confirmation"]["keep_pending"])
        self.assertIsNotNone(ev.load_pending(d))

    def test_a_pending_from_an_older_epoch_is_dropped_with_a_note(self) -> None:
        d = self.d()
        ev.finalize_calibrated_round(_proposal(6, "IMPROVED", 1000, 1500), d, shadow_epoch=0)
        forced, note = ev.pending_forced_mutation(d, shadow_epoch=1)
        self.assertIsNone(forced)
        self.assertIn("epoch", note)
        self.assertIsNone(ev.load_pending(d), "the stale pending was cleared")

    def test_a_proposal_without_a_gate_is_untouched_and_so_is_the_pending(self) -> None:
        d = self.d()
        ev.finalize_calibrated_round(_proposal(6, "IMPROVED", 1000, 1500), d, shadow_epoch=0)
        legacy = _proposal(7, "IMPROVED", 2000, 2500, with_gate=False)
        before = json.dumps(legacy, sort_keys=True)
        out = ev.finalize_calibrated_round(legacy, d, shadow_epoch=0)
        self.assertEqual(json.dumps(out, sort_keys=True), before)
        self.assertIsNotNone(ev.load_pending(d))

    def test_no_pending_means_no_forced_mutation(self) -> None:
        self.assertEqual(ev.pending_forced_mutation(self.d(), shadow_epoch=0), (None, None))


class TestWorkerBandsFlag(_Life):
    def test_a_malformed_bands_file_stops_the_worker_before_it_builds_a_shadow(self) -> None:
        bad = self.tmp / "bad-bands.json"
        b = bands()
        del b["dims"]["frames_filed"]
        bad.write_text(json.dumps(b))
        with self.assertRaises(ValueError):
            ev.main(["--root", str(self.root), "--genome", str(FIXTURE), "--bands", str(bad), "--stop-file", str(self.tmp / "STOP-x")])

    def test_a_good_bands_file_is_named_in_the_workers_first_line(self) -> None:
        good = self.tmp / "good-bands.json"
        good.write_text(json.dumps(bands()))
        stop = self.tmp / "STOP-y"
        stop.write_text("x")
        buf = io.StringIO()
        with unittest.mock.patch("sys.stdout", buf):
            rc = ev.main(["--root", str(self.root), "--genome", str(FIXTURE), "--bands", str(good), "--stop-file", str(stop)])
        self.assertEqual(rc, 0)
        self.assertIn("calibrated gate", buf.getvalue())
        self.assertIn("slice S1", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
