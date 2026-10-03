"""Tests for TOY C's gates G1-G6 (docs/research/toys/PREREG-TOY-FRAMES.md §7; AMENDMENT-1 §1.4, §3, §4 (f)-(g)): the checks the unit REQUIRES before it runs. Written FIRST, STAGE 5b (red, then green).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:10 +0400 — STAGE 5b. G1 runs here on FIXTURE copies (the real counts are asserted against the real copies by tests/tools/test_toys_frames.py and by the real `gates` run); each gate
# carries a planted failure it must NAME: a count one off (G1), a corrupted copy (G1), a ceiling set below the measured price (G5), a plant stream the rules cannot keep (G4).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.toys.frames import gates as GT
from tools.toys.frames import streams as ST
from tools.toys.frames.evaluate import SEEDS as EV_SEEDS

from tests.tools.test_toys_frames_run import make_copies


def write_manifest(copies: Path):
    man = {}
    for sub in ("tape", "journal"):
        for p in sorted(copies.glob(f"*/{sub}/*.jsonl")):
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            man[str(p.relative_to(copies))] = {"source_sha256": h, "copy_sha256": h, "bytes": p.stat().st_size}
    (copies / "MANIFEST.json").write_text(json.dumps(man))
    return man


def expected_from(copies: Path):
    a4 = ST.load_moments(sorted((copies / "alpha4-1" / "tape").glob("*.jsonl")))
    c = ST.section0_counts(a4)
    sc = ST.scene_moments(ST.load_moments(sorted((copies / "brain-full-20261102" / "tape").glob("*.jsonl"))))
    from collections import Counter
    says = ST.load_says(sorted((copies / "alpha4-1" / "journal").glob("*.jsonl")))
    return {"alpha4": {"moments": c["moments"], "words": c["words"], "by_source": c["by_source"]},
            "scene": {"moments": len(sc), "per_moment": dict(sorted(Counter(len(m.words) for m in sc).items())), "dax_index": None},
            "says": (len(says), sum(1 for s in says if s[1] == "yes"), len({s[0] for s in says}))}


class TestG1(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        make_copies(self.d)
        write_manifest(self.d)
        self.exp = expected_from(self.d)

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_it_passes_when_every_count_is_the_expected_one_and_the_copies_hash_to_their_manifest(self):
        r = GT.g1(self.d, self.exp)
        self.assertTrue(r["ok"], r["failures"])
        self.assertEqual(r["failures"], [])
        self.assertEqual(r["plant_tokens"], {"ALPHA4": {t: 0 for t in ST.PLANT}, "SCENE": {t: 0 for t in ST.PLANT}})
        self.assertIn("gated", r["chi2"])

    def test_a_count_one_off_is_named(self):
        bad = json.loads(json.dumps(self.exp, default=str))
        bad = {**self.exp, "alpha4": {**self.exp["alpha4"], "moments": self.exp["alpha4"]["moments"] + 1}}
        r = GT.g1(self.d, bad)
        self.assertFalse(r["ok"])
        self.assertTrue(any("alpha4.moments" in f for f in r["failures"]), r["failures"])

    def test_a_per_source_count_one_off_is_named(self):
        by = {k: dict(v) for k, v in self.exp["alpha4"]["by_source"].items()}
        src = sorted(by)[0]
        by[src]["words"] += 1
        r = GT.g1(self.d, {**self.exp, "alpha4": {**self.exp["alpha4"], "by_source": by}})
        self.assertFalse(r["ok"])
        self.assertTrue(any(f"alpha4.{src}.words" in f for f in r["failures"]), r["failures"])

    def test_a_scene_histogram_or_says_count_one_off_is_named(self):
        r = GT.g1(self.d, {**self.exp, "scene": {**self.exp["scene"], "moments": self.exp["scene"]["moments"] - 1}})
        self.assertTrue(any("scene.moments" in f for f in r["failures"]))
        s = self.exp["says"]
        r2 = GT.g1(self.d, {**self.exp, "says": (s[0], s[1] + 1, s[2])})
        self.assertTrue(any("says" in f for f in r2["failures"]))

    def test_a_corrupted_copy_is_named_by_its_path(self):
        p = self.d / "alpha4-1" / "tape" / "2026-09-23.jsonl"
        b = bytearray(p.read_bytes())
        b[40] ^= 1
        p.write_bytes(bytes(b))
        r = GT.g1(self.d, self.exp)
        self.assertFalse(r["ok"])
        self.assertTrue(any("alpha4-1/tape/2026-09-23.jsonl" in f for f in r["failures"]), r["failures"])

    def test_a_plant_token_found_in_a_real_stream_is_named(self):
        """AMENDMENT-1 §2: both plant tokens must occur in ZERO real rows. The plant: one real moment carrying the first token (the manifest and the counts are rebuilt so ONLY this check can fail)."""
        p = self.d / "alpha4-1" / "tape" / "2026-09-23.jsonl"
        last = [json.loads(x) for x in p.read_text().splitlines() if x.strip()][-1]["seq"]
        row = {"seq": last + 1, "at": "2026-09-23T00:00:00Z", "sense": "ear", "sha": "x", "payload": "p", "meta": {"moment": "planted-real", "source": "shelf", "word": ST.PLANT[0]}}
        p.write_text(p.read_text() + json.dumps(row) + "\n")
        write_manifest(self.d)
        exp = expected_from(self.d)
        r = GT.g1(self.d, exp)
        self.assertFalse(r["ok"])
        self.assertEqual(len(r["failures"]), 1, r["failures"])
        self.assertIn("plant tokens occur in the real ALPHA4 stream", r["failures"][0])

    def test_the_dax_moment_is_checked_at_its_index_when_the_law_names_one(self):
        r = GT.g1(self.d, {**self.exp, "scene": {**self.exp["scene"], "dax_index": 5}})
        self.assertFalse(r["ok"])                                                                     # scene moment 5 of the fixture is not the one-word «dax» scene
        self.assertTrue(any("dax" in f for f in r["failures"]))


class TestG2G3(unittest.TestCase):
    def test_g2_the_stand_in_store_equals_the_real_episodes_store(self):
        r = GT.g2()
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["frames"], [["blue", "ball"], ["green", "key"], ["red", "box"]])

    def test_g3_the_fast_compressor_and_the_greedys_incremental_gain_equal_their_recounts(self):
        r = GT.g3(n_streams=6, mdl_seeds=3)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["compressor_cases"], 6 * 4)
        self.assertLess(r["max_abs_diff"], 1e-9)
        self.assertEqual(r["mdl_problems"], [])
        self.assertGreater(r["mdl_steps"], 3)                                                          # the loop took steps (a vacuous pass would be zero)


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:22 +0400 — G4 under AMENDMENT-2 §2 (written FIRST; red: g4 takes no stream sizes yet): TWO planted streams, (A) the SCENE-regime stream as signed in AMENDMENT-1 §4 (g) where WEB-H, SENTENCE and
# MDL-GREEDY are required and WEB-S is PRINTED, and (B) an ALPHA4-regime stream where all four are required; the seat's 18:2x test for signing: the small-vocabulary failure stays printed, never erased.
class TestG4(unittest.TestCase):
    def test_both_streams_every_required_rule_keeps_the_plant_and_both_controls_are_caught(self):
        r = GT.g4(draws=20, seeds=(1, 2, 3), scene_moments=2500, alpha_moments=6000)
        self.assertTrue(r["ok"], r["failures"])
        a, b = r["streams"]["A"], r["streams"]["B"]
        self.assertEqual(sorted(a["required"]), ["MDL-GREEDY", "SENTENCE", "WEB-H"])
        self.assertEqual(a["printed_only"], ["WEB-S"])
        self.assertEqual(sorted(b["required"]), ["MDL-GREEDY", "SENTENCE", "WEB-H", "WEB-S"])
        self.assertEqual(b["printed_only"], [])
        for rule in b["required"]:
            self.assertTrue(b["gates"][rule]["pass"], (rule, b["gates"][rule]))
        for s in (a, b):
            self.assertTrue(s["plant_beats_null2"])
            self.assertTrue(s["control"]["caught"])
            self.assertTrue(s["control"]["bytes_changed"])
            self.assertEqual(s["budget"], 2 * s["V"])
        self.assertGreater(b["V"], 500)                                                                 # stream B's vocabulary is the regime where B = 2V can hold a plant (stream A's is 15 words)
        self.assertLess(a["V"], 20)

    def test_stream_a_as_signed_prints_web_s_failure_and_does_not_fail_the_gate(self):
        """the signed stream (3,000 moments, replicate seed 1, a plant after every 10th, ten WEB-S seeds): WEB-S keeps the frame at 6 of 10 seeds (records/frames/ORIENT-g4_diag.out) — PRINTED in the output,
        never erased, and not a failure of G4 (AMENDMENT-2 §2 (A))."""
        r = GT.g4(draws=10, seeds=EV_SEEDS, scene_moments=3000, alpha_moments=6000)
        a = r["streams"]["A"]
        self.assertFalse(a["gates"]["WEB-S"]["pass"])
        self.assertEqual((a["gates"]["WEB-S"]["n_counted"], a["gates"]["WEB-S"]["n_seeds"], a["gates"]["WEB-S"]["need"]), (6, 10, 9))
        self.assertEqual((a["V"], a["budget"]), (15, 30))
        for rule in ("WEB-H", "SENTENCE", "MDL-GREEDY"):
            self.assertTrue(a["gates"][rule]["pass"], rule)
        self.assertTrue(r["ok"], r["failures"])                                                         # the required rules and stream B carry the gate
        self.assertFalse(any("WEB-S" in f and "stream A" in f for f in r["failures"]))

    def test_a_stream_too_short_to_carry_the_plant_fails_and_says_so(self):
        r = GT.g4(draws=10, seeds=(1, 2, 3), scene_moments=300, scene_every=100, alpha_moments=300, alpha_every=100)      # a few plants in 300 moments: nothing can repay 2 log2 V
        self.assertFalse(r["ok"])
        self.assertTrue(r["failures"])

    def test_a_required_rule_that_fails_on_stream_b_stops_the_gate(self):
        r = GT.g4(draws=10, seeds=(1, 2, 3), scene_moments=2500, alpha_moments=300, alpha_every=100)    # stream B too short for the web: required there
        self.assertFalse(r["ok"])
        self.assertTrue(any("stream B" in f for f in r["failures"]), r["failures"])


class TestG5(unittest.TestCase):
    def test_the_pilot_extrapolates_cpu_linearly_in_the_draws_and_reports_peak_memory(self):
        d = Path(tempfile.mkdtemp())
        try:
            make_copies(d)
            r = GT.g5(d, sizes=(3, 6), cpu_ceiling_min=1000.0, rss_ceiling_mb=100000.0, seeds=(1, 2))
            self.assertTrue(r["ok"], r)
            a, b = r["pilots"]
            self.assertEqual((a["draws"], b["draws"]), (3, 6))
            slope = (b["cpu_seconds"] - a["cpu_seconds"]) / 3
            self.assertAlmostEqual(r["cpu_slope_per_draw"], slope, places=9)
            self.assertAlmostEqual(r["predicted_alpha4_cpu_seconds_at_100"], a["cpu_seconds"] + slope * 97, places=6)
            self.assertAlmostEqual(r["predicted_unit_cpu_minutes"], 5 * r["predicted_alpha4_cpu_seconds_at_100"] / 60.0, places=9)
            self.assertGreater(r["peak_rss_mb"], 0.0)
            # the plant: a ceiling below the measured price must STOP
            tight = GT.g5(d, sizes=(3, 6), cpu_ceiling_min=1e-6, rss_ceiling_mb=100000.0, seeds=(1, 2))
            self.assertFalse(tight["ok"])
            self.assertTrue(any("CPU" in f for f in tight["failures"]))
            tight_mem = GT.g5(d, sizes=(3, 6), cpu_ceiling_min=1000.0, rss_ceiling_mb=1.0, seeds=(1, 2))
            self.assertFalse(tight_mem["ok"])
            self.assertTrue(any("memory" in f for f in tight_mem["failures"]))
        finally:
            shutil.rmtree(d)


class TestG6(unittest.TestCase):
    def test_the_ceiling_gate_controls_pass_and_a_planted_cheat_is_caught(self):
        r = GT.g6(replicates=3, n_moments=3000)
        self.assertTrue(r["ok"], r)
        self.assertEqual(len(r["replicates"]), 3)
        self.assertTrue(all(not x["violation"] for x in r["replicates"]))
        self.assertTrue(r["cheat"]["caught"])
        self.assertLess(abs(r["exact"]["sum_p"] - 1.0), 1e-12)


class TestRunGates(unittest.TestCase):
    def test_gates_json_says_passed_on_fixtures_and_the_unit_accepts_it(self):
        d = Path(tempfile.mkdtemp())
        try:
            make_copies(d / "copies")
            write_manifest(d / "copies")
            exp = expected_from(d / "copies")
            out = d / "runs"
            code = GT.run_gates(d / "copies", out, expected=exp, g3_kw={"n_streams": 4, "mdl_seeds": 2}, g4_kw={"scene_moments": 2500, "alpha_moments": 6000, "draws": 20, "seeds": (1, 2, 3)},
                                g5_kw={"sizes": (3, 6), "cpu_ceiling_min": 1000.0, "rss_ceiling_mb": 100000.0, "seeds": (1, 2)}, g6_kw={"replicates": 2, "n_moments": 3000})
            self.assertEqual(code, 0)
            g = json.loads((out / "GATES.json").read_text())
            self.assertTrue(g["passed"])
            self.assertEqual(g["failures"], [])
            for k in ("g1", "g2", "g3", "g4", "g5", "g6", "header"):
                self.assertIn(k, g)
            self.assertIn("toys_git_sha", g["header"])
        finally:
            shutil.rmtree(d)

    def test_a_failing_gate_writes_passed_false_and_exits_nonzero(self):
        d = Path(tempfile.mkdtemp())
        try:
            make_copies(d / "copies")
            write_manifest(d / "copies")
            exp = expected_from(d / "copies")
            exp["alpha4"]["moments"] += 1                                                               # the plant: one count off
            out = d / "runs"
            code = GT.run_gates(d / "copies", out, expected=exp, g3_kw={"n_streams": 2, "mdl_seeds": 1}, g4_kw={"scene_moments": 2500, "alpha_moments": 6000, "draws": 10, "seeds": (1, 2, 3)},
                                g5_kw={"sizes": (3, 6), "cpu_ceiling_min": 1000.0, "rss_ceiling_mb": 100000.0, "seeds": (1, 2)}, g6_kw={"replicates": 1, "n_moments": 3000})
            self.assertNotEqual(code, 0)
            g = json.loads((out / "GATES.json").read_text())
            self.assertFalse(g["passed"])
            self.assertTrue(any("alpha4.moments" in f for f in g["failures"]))
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
