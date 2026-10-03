"""Tests for TOY C's report (docs/research/toys/RESULT-TOY-FRAMES-REPORT.txt): every figure the RESULT quotes comes from this file, and this file from the records; it regenerates BYTE-IDENTICALLY from them.
Written FIRST, STAGE 6a (red, then green).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:17 +0400 — STAGE 6a. The fixture is the runner's own end-to-end output on tiny synthetic copies (5 draws, 2 WEB-S seeds) plus a HAND-MADE GATES.json in the final structure (G4 with TWO streams,
# AMENDMENT-2 §2), so the tests can plant what the report must print: a stream-A WEB-S miss that is PRINTED (the seat's 18:2x test for signing: the small-V failure stays printed, never erased), a NOT GRADABLE label, a changed record.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.toys.frames import report as RP
from tools.toys.frames import run as RN

from tests.tools.test_toys_frames_run import make_copies

HEADERS = ["== 0 · PROVENANCE", "== 1 · GATES", "== 2 · THE FIVE CONDITIONS", "== 3 · THE PLANT GATE", "== 4 · SHUFFLE-QUIET", "== 5 · GAIN", "== 6 · CRITERION-MATTERS (NULL-2)",
           "== 7 · THE EYE'S READING", "== 8 · OVERLAPS", "== 9 · SCENE", "== 10 · PREDICTIONS"]


def stream(label, web_s_counted, required):
    gates = {r: {"pass": True, "n_seeds": 1, "n_counted": 1, "need": 1, "mode": "amend1", "B": 700.0} for r in ("WEB-H", "SENTENCE", "MDL-GREEDY")}
    gates["WEB-S"] = {"pass": web_s_counted >= 9, "n_seeds": 10, "n_counted": web_s_counted, "need": 9, "mode": "amend1", "B": 700.0}
    return {"label": label, "n_moments": 3000, "every": 10, "plants": [180, 120], "V": 15, "budget": 30, "B": 700.0, "plant_beats_null2": True, "gates": gates, "required": required,
            "control": {"caught": True, "bytes_changed": True, "B_honest": 700.0, "C_honest": 699.0, "B_broken": -8.0, "C_broken": -8.0}}


def gates_json():
    return {"passed": True, "failures": [], "header": {"toys_git_sha": "abc", "toys_tree_dirty": False, "gate_mode": "amend1"}, "cpu_seconds": 12.5, "peak_rss_kb": 104000,
            "g1": {"ok": True, "failures": [], "copies_verified": 10, "alpha4": {"moments": 84275, "words": 112489}, "scene": {"moments": 10000}, "says": [526, 86, 40],
                   "plant_tokens": {"ALPHA4": {"zzq": 0, "qxk": 0}, "SCENE": {"zzq": 0, "qxk": 0}}, "chi2": {"gated": True, "n": 9999, "dax_excluded": 1, "heldout_pairs_seen": 0,
                                                                                                                 "length": {"p": 0.41}, "shape": {"p": 0.52}, "colour": {"p": 0.33}, "size": {"p": 0.77}, "pairs": {"p": 0.29}}},
            "g2": {"ok": True, "frames": [["blue", "ball"], ["green", "key"], ["red", "box"]], "n_rows": 3},
            "g3": {"ok": True, "compressor_cases": 160, "max_abs_diff": 3.0e-13, "mdl_problems": [], "mdl_steps": 28, "mdl_seeds": 8},
            "g4": {"ok": True, "failures": [], "streams": {"A": stream("SCENE-regime (as signed)", 6, ["WEB-H", "SENTENCE", "MDL-GREEDY"]), "B": stream("ALPHA4-regime", 10, ["WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY"])}},
            "g5": {"ok": True, "failures": [], "pilots": [{"draws": 10, "cpu_seconds": 50.0, "peak_rss_kb": 100000}, {"draws": 20, "cpu_seconds": 66.0, "peak_rss_kb": 101000}],
                   "cpu_slope_per_draw": 1.6, "rss_slope_kb_per_draw": 100.0, "predicted_alpha4_cpu_seconds_at_100": 194.0, "predicted_unit_cpu_minutes": 16.2, "predicted_peak_rss_mb": 105.0,
                   "peak_rss_mb": 99.0, "cpu_ceiling_min": 40.0, "rss_ceiling_mb": 1024.0},
            "g6": {"ok": True, "failures": [], "replicates": [{"k": 1, "G_oracle": 10.0, "G_max": 5000.0, "margin": 4990.0, "violation": False}], "min_margin": 4990.0,
                   "cheat": {"caught": True, "G_cheat": 9000.0, "G_max": 5000.0}, "exact": {"sum_p": 1.0, "entropy": 6.0774, "h_length": 1.5, "h_given_length": 4.5774, "support_size": 90}}}


class TestReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = Path(tempfile.mkdtemp())
        make_copies(cls.d / "copies")
        cls.out = cls.d / "runs"
        RN.run_unit(cls.d / "copies", cls.out, draws=5, seeds=(1, 2), require_gates=False)
        (cls.out / "GATES.json").write_text(json.dumps(gates_json()))
        cls.text = RP.render(RP.load(cls.out))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d)

    def test_every_section_is_present_in_order(self):
        pos = [self.text.find(h) for h in HEADERS]
        self.assertTrue(all(p >= 0 for p in pos), [h for h, p in zip(HEADERS, pos) if p < 0])
        self.assertEqual(pos, sorted(pos))

    def test_the_figures_come_from_the_records(self):
        a = json.loads((self.out / "ALPHA4.json").read_text())
        mdl = [r for r in a["records"] if r["rule"] == "MDL-GREEDY"][0]
        self.assertIn(f"{mdl['gain']['G']:.2f}", self.text)
        self.assertIn(f"{a['V']}", self.text)
        res = json.loads((self.out / "RESULTS.json").read_text())
        for rule, v in res["grade"]["alpha4"].items():
            self.assertIn(f"GAIN {rule}: {v['gain_verdict']}", self.text)

    def test_the_small_vocabulary_failure_of_g4_stream_a_stays_printed(self):
        self.assertIn("WEB-S 6 of 10 seeds count (need 9)", self.text)
        self.assertIn("PRINTED, not required", self.text)
        self.assertIn("V 15, budget B = 2V = 30", self.text)

    def test_the_text_is_deterministic_and_main_writes_the_same_bytes(self):
        self.assertEqual(self.text, RP.render(RP.load(self.out)))
        target = self.d / "report.txt"
        self.assertEqual(RP.main(["--root", str(self.out), "--out", str(target)]), 0)
        self.assertEqual(target.read_text(), self.text)

    def test_the_provenance_lists_every_record_file_with_its_sha256(self):
        import hashlib
        for name in ("ALPHA4.json", "ALPHA4+PLANT.json", "ALPHA4+SHUFFLE.json", "SCENE.json", "SCENE+PLANT.json", "RESULTS.json", "GATES.json"):
            h = hashlib.sha256((self.out / name).read_bytes()).hexdigest()
            self.assertIn(f"{h}  {name}", self.text)

    def test_a_planted_change_in_a_record_changes_the_report_and_its_number_appears(self):
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(self.out, d / "runs")
            p = d / "runs" / "ALPHA4.json"
            c = json.loads(p.read_text())
            mdl = [r for r in c["records"] if r["rule"] == "MDL-GREEDY"][0]
            before = mdl["gain"]["G"]
            mdl["gain"]["G"] = before + 123.45
            p.write_text(json.dumps(c, sort_keys=True))
            t2 = RP.render(RP.load(d / "runs"))
            self.assertNotEqual(t2, self.text)                                                           # the plant changed the bytes AND the report
            self.assertIn(f"{before + 123.45:.2f}", t2)
        finally:
            shutil.rmtree(d)

    def test_a_missing_condition_record_is_an_error_not_a_blank(self):
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(self.out, d / "runs")
            (d / "runs" / "SCENE+PLANT.json").unlink()
            with self.assertRaises(RP.ReportError):
                RP.load(d / "runs")
        finally:
            shutil.rmtree(d)

    def test_without_a_gates_record_the_report_says_so(self):
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(self.out, d / "runs")
            (d / "runs" / "GATES.json").unlink()
            t = RP.render(RP.load(d / "runs"))
            self.assertIn("GATES.json: not present", t)
        finally:
            shutil.rmtree(d)

    def test_the_predictions_are_read_mechanically(self):
        res = json.loads((self.out / "RESULTS.json").read_text())
        a = json.loads((self.out / "ALPHA4.json").read_text())
        G = {}
        for r in a["records"]:
            G.setdefault(r["rule"], []).append(r["gain"]["G"])
        mean_s = sum(G["WEB-S"]) / len(G["WEB-S"])
        mdl = G["MDL-GREEDY"][0]
        holds = mdl >= max(G["WEB-H"][0], mean_s, G["SENTENCE"][0])
        self.assertIn(f"P-C1 {'holds' if holds else 'does not hold'}", self.text)
        for k in ("P-C2", "P-C3", "P-C4", "P-C5", "P-C6"):
            self.assertIn(k, self.text)
        self.assertIn("kept «the letters»", self.text)                                                   # P-C5's three named pairs are read as booleans
        self.assertEqual(res["mode"], "amend1")

    def test_a_not_gradable_verdict_is_printed_as_such(self):
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(self.out, d / "runs")
            p = d / "runs" / "RESULTS.json"
            r = json.loads(p.read_text())
            r["grade"]["alpha4"]["WEB-H"]["gain_verdict"] = "NOT GRADABLE"
            r["grade"]["scene"]["WEB-S"]["gradable"] = False
            p.write_text(json.dumps(r, sort_keys=True))
            t = RP.render(RP.load(d / "runs"))
            self.assertIn("GAIN WEB-H: NOT GRADABLE", t)
            self.assertIn("SCENE WEB-S: NOT GRADABLE", t)
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
