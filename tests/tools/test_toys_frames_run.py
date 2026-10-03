"""Tests for TOY C's runner: the five conditions from a copies directory, their records with the provenance header, the SCENE ceiling block, the grade and readings, and the refusals
(a changed law, gates not passed). Written FIRST, STAGE 5a (red, then green).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:06 +0400 — STAGE 5a. The fixture copies are tiny synthetic tapes in the REAL row format (ear rows with meta.moment / source / word, journal say rows), so the pipeline
# runs end to end in seconds with 5 null draws and two WEB-S seeds; the real unit uses 10 seeds and 100 draws through slot.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import List

import numpy as np

from tools.toys.common import prereg as PR
from tools.toys.frames import run as RN
from tools.toys.frames import scene as SC
from tools.toys.frames import streams as ST
from tools.toys.frames import synthetic as SY

REPO = Path(__file__).resolve().parents[2]


def write_tape(path: Path, moments: List[ST.Moment], start_seq: int = 1, extra_rows=()):
    path.parent.mkdir(parents=True, exist_ok=True)
    seq = start_seq
    lines = []
    for m in moments:
        for w in m.words:
            lines.append(json.dumps({"seq": seq, "at": "2026-09-23T00:00:00Z", "sense": "ear", "sha": "x", "payload": "p", "meta": {"moment": m.name, "source": m.source, "word": w}}))
            seq += 1
    for r in extra_rows:
        lines.append(json.dumps(r))
    path.write_text("\n".join(lines) + "\n")
    return seq


def make_copies(root: Path) -> Path:
    tr, he = SY.structure_free_alpha(2500, 3)
    alpha = [ST.Moment("shelf" if len(m.words) > 1 else "maker", m.name, m.words, m.seqs) for m in tr + he]
    write_tape(root / "alpha4-1" / "tape" / "2026-09-23.jsonl", alpha)
    journal = root / "alpha4-1" / "journal"
    journal.mkdir(parents=True)
    (journal / "2026-09-23.jsonl").write_text("\n".join(json.dumps({"seq": i, "say": {"frame": f, "heard": h}}) for i, (f, h) in enumerate(
        [("red box", "yes"), ("red box", "no"), ("the letters", "no"), ("to the", "no")], 1)) + "\n" + json.dumps({"seq": 9, "act": "glance"}) + "\n")
    scene = SC.sample_moments(1500, np.random.default_rng([20261103, 8, 11]))
    other = [ST.Moment("maker", f"mk{i}", ("bar",), (0.0,)) for i in range(5)]
    write_tape(root / "brain-full-20261102" / "tape" / "2026-09-28.jsonl", scene[:700] + other + scene[700:])
    return root


class TestLoadStreams(unittest.TestCase):
    def test_alpha_is_every_source_and_scene_is_only_the_scene_moments(self):
        d = Path(tempfile.mkdtemp())
        try:
            make_copies(d)
            s = RN.load_streams(d)
            self.assertEqual(sorted(s), ["alpha4", "scene"])
            self.assertEqual(len(s["alpha4"]), 2500)
            self.assertEqual(len(s["scene"]), 1500)
            self.assertTrue(all(m.source == "scene" for m in s["scene"]))
        finally:
            shutil.rmtree(d)


class TestUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = Path(tempfile.mkdtemp())
        make_copies(cls.d / "copies")
        cls.out = cls.d / "runs"
        cls.code = RN.run_unit(cls.d / "copies", cls.out, draws=5, seeds=(1, 2), require_gates=False)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d)

    def test_five_condition_records_one_results_file_and_a_clean_exit(self):
        self.assertEqual(self.code, 0)
        names = sorted(p.name for p in self.out.glob("*.json"))
        self.assertEqual(names, ["ALPHA4+PLANT.json", "ALPHA4+SHUFFLE.json", "ALPHA4.json", "RESULTS.json", "SCENE+PLANT.json", "SCENE.json"])

    def test_each_record_carries_both_signed_shas_the_code_sha_and_the_gate_mode(self):
        for name, kind in (("ALPHA4", "plain"), ("ALPHA4+PLANT", "plant"), ("ALPHA4+SHUFFLE", "shuffle"), ("SCENE", "plain"), ("SCENE+PLANT", "plant")):
            c = json.loads((self.out / f"{name}.json").read_text())
            self.assertEqual((c["name"], c["kind"]), (name, kind))
            h = c["header"]
            self.assertEqual(h["prereg_frames_sha256"], PR.SIGNED["frames"][1])
            self.assertEqual(h["prereg_frames_amend1_sha256"], PR.SIGNED["frames_amend1"][1])
            self.assertIn("toys_git_sha", h)
            self.assertIn("toys_tree_dirty", h)
            self.assertEqual(h["gate_mode"], "amend1")
            self.assertEqual(c["draws"], 5)
            self.assertEqual(len(c["records"]), 1 + 2 + 1 + 1)                                      # WEB-H, WEB-S x 2 seeds, SENTENCE, MDL-GREEDY

    def test_the_conditions_are_the_laws_five_streams(self):
        a = json.loads((self.out / "ALPHA4.json").read_text())
        p = json.loads((self.out / "ALPHA4+PLANT.json").read_text())
        s = json.loads((self.out / "ALPHA4+SHUFFLE.json").read_text())
        self.assertEqual(a["n_train_moments"] + a["n_held_moments"], 2500)
        self.assertEqual(p["n_train_moments"] + p["n_held_moments"], 2500 + 25)                    # a plant after every 100th moment
        self.assertEqual(s["n_train_moments"] + s["n_held_moments"], 2500)
        sc = json.loads((self.out / "SCENE.json").read_text())
        scp = json.loads((self.out / "SCENE+PLANT.json").read_text())
        self.assertEqual(sc["n_train_moments"] + sc["n_held_moments"], 1500)
        self.assertEqual(scp["n_train_moments"] + scp["n_held_moments"], 1500 + 150)               # a plant after every 10th
        self.assertEqual(p["plant_stream"]["plants_train"] + p["plant_stream"]["plants_held"], 25)

    def test_results_hold_the_grade_in_both_modes_the_readings_and_the_instrument_checks(self):
        r = json.loads((self.out / "RESULTS.json").read_text())
        self.assertEqual(r["grade"]["mode"], "amend1")
        self.assertEqual(r["grade_law"]["mode"], "law")
        for rule in ("WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY"):
            self.assertIn(r["grade"]["alpha4"][rule]["gain_verdict"], ("PASS", "FAIL", "NOT GRADABLE"))
        self.assertEqual(r["plant_tokens"]["ALPHA4"], {t: 0 for t in ST.PLANT})
        self.assertEqual(r["eye"]["distinct_said"], 3)                                               # red box, the letters, to the
        self.assertEqual(r["eye"]["says"], 4)
        self.assertIn("WEB-H|SENTENCE", r["overlaps"]["ALPHA4"])
        self.assertIn("chi2", r["scene"])
        self.assertIn("G_max", r["scene"])
        self.assertFalse(r["scene"]["stop"])
        self.assertEqual(r["scene"]["oracle"]["n_frames"], 24)

    def test_a_second_run_skips_the_records_already_on_disk(self):
        before = {p.name: p.stat().st_mtime_ns for p in self.out.glob("*.json") if p.name != "RESULTS.json"}
        code = RN.run_unit(self.d / "copies", self.out, draws=5, seeds=(1, 2), require_gates=False)
        after = {p.name: p.stat().st_mtime_ns for p in self.out.glob("*.json") if p.name != "RESULTS.json"}
        self.assertEqual(code, 0)
        self.assertEqual(before, after)


class TestRefusals(unittest.TestCase):
    def test_a_changed_law_text_stops_the_unit_before_anything_is_written(self):
        d = Path(tempfile.mkdtemp())
        try:
            make_copies(d / "copies")
            docs = d / "docs"
            docs.mkdir()
            for name in ("PREREG-TOY-FRAMES.md", "PREREG-TOY-FRAMES-AMEND-1.md"):
                shutil.copy(PR.DOCS / name, docs / name)
            amend = docs / "PREREG-TOY-FRAMES-AMEND-1.md"
            text = amend.read_bytes()
            amend.write_bytes(text.replace(b"> 0 on that stream", b"> 1 on that stream", 1))              # the plant: the threshold of gate (B)
            self.assertNotEqual(amend.read_bytes(), text)
            with self.assertRaises(PR.PreregError):
                RN.run_unit(d / "copies", d / "runs", draws=5, seeds=(1,), require_gates=False, prereg_root=docs)
            self.assertFalse((d / "runs").exists() and any((d / "runs").iterdir()))
        finally:
            shutil.rmtree(d)

    def test_the_unit_refuses_without_a_passed_gates_record(self):
        d = Path(tempfile.mkdtemp())
        try:
            make_copies(d / "copies")
            with self.assertRaises(RN.RunError):
                RN.run_unit(d / "copies", d / "runs", draws=5, seeds=(1,), require_gates=True)
            (d / "runs").mkdir(parents=True, exist_ok=True)
            (d / "runs" / "GATES.json").write_text(json.dumps({"passed": False}))
            with self.assertRaises(RN.RunError):
                RN.run_unit(d / "copies", d / "runs", draws=5, seeds=(1,), require_gates=True)
        finally:
            shutil.rmtree(d)


class TestSceneBlock(unittest.TestCase):
    def test_a_g_above_g_max_plus_twenty_stops_the_run(self):
        ms = SC.sample_moments(1200, np.random.default_rng([20261103, 8, 12]))
        tr, he = ST.split(ms)
        from tools.toys.frames import evaluate as EV
        cond = EV.evaluate_condition(tr, he, name="SCENE", draws=5, web_seeds=(1,), kind="plain")
        block = RN.scene_block(ms, cond)
        self.assertFalse(block["stop"])
        self.assertTrue(block["gmax_gated"])
        cond["records"][0]["gain"]["G"] = block["G_max"] + 20.0001                                     # the plant: one record above the ceiling
        with self.assertRaises(SC.CeilingStop):
            RN.scene_block(ms, cond)

    def test_the_rows_carry_the_margin_and_the_oracle_block_the_oracles_own_g(self):
        ms = SC.sample_moments(1200, np.random.default_rng([20261103, 8, 12]))
        tr, he = ST.split(ms)
        from tools.toys.frames import evaluate as EV
        cond = EV.evaluate_condition(tr, he, name="SCENE", draws=5, web_seeds=(1,), kind="plain")
        b = RN.scene_block(ms, cond)
        for row, r in zip(b["rows"], cond["records"]):
            self.assertAlmostEqual(row["margin"], b["G_max"] - r["gain"]["G"], places=9)
            self.assertFalse(row["violation"])
        self.assertAlmostEqual(b["oracle"]["margin"], b["G_max"] - b["oracle"]["G"], places=9)
        self.assertAlmostEqual(b["G_max"], b["bits0"] - sum(-__import__("math").log2(SC.p_gen(m.words)) for m in he), places=6)

    def test_the_ceiling_is_gated_only_when_the_chi_square_fit_holds(self):
        """a stream that fails G1's fit (all two-word utterances) makes G_max a READING: a record above it is printed as a violation but the run does not stop."""
        ms = SC.sample_moments(3000, np.random.default_rng([20261103, 8, 13]))
        skew = [m for m in ms if len(m.words) == 2]
        tr, he = ST.split(skew)
        from tools.toys.frames import evaluate as EV
        cond = EV.evaluate_condition(tr, he, name="SCENE", draws=5, web_seeds=(1,), kind="plain")
        gm = RN.scene_block(skew, cond)["G_max"]
        cond["records"][0]["gain"]["G"] = gm + 1000.0
        b = RN.scene_block(skew, cond)
        self.assertFalse(b["gmax_gated"])
        self.assertFalse(b["stop"])
        self.assertTrue(b["rows"][0]["violation"])

    def test_an_utterance_the_generator_cannot_produce_in_the_held_out_part_is_a_stop(self):
        ms = SC.sample_moments(1200, np.random.default_rng([20261103, 8, 12]))
        bad = ms[:-1] + [ST.Moment("scene", "ho", ("blue", "circle"), (99999.0, 99999.5))]             # a held-out colour-shape pair, last = held-out part
        tr, he = ST.split(bad)
        from tools.toys.frames import evaluate as EV
        cond = EV.evaluate_condition(tr, he, name="SCENE", draws=5, web_seeds=(1,), kind="plain")
        with self.assertRaises(SC.CeilingStop):
            RN.scene_block(bad, cond)


if __name__ == "__main__":
    unittest.main()
