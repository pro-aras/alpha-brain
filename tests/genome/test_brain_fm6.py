# edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:20 +0400 — PREREG-BRAIN-IN-BODY AMENDMENT 1 §2 (sha 45abeca2…), test-first (red on
# brain-organ-fm6 e4f175a): genome/brain.py reads the BRAIN line's `young_rule` and sets the learner's attribute; the LAW organ is
# byte-for-byte the organ it was (state hash, learn rows, answers, summary — pinned against a fixture computed by bc45156's code
# BEFORE any F-M6 edit); a brain saved under one rule refuses to load under the other BY NAME; summary() names the rule.
"""tests/genome/test_brain_fm6.py — the organ under `young <n> nearest` (F-M6) on test_brain_organ's synthetic toy life."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tests.genome import test_brain_organ as T

ROOT = Path(__file__).resolve().parents[2]
FIX = json.loads((ROOT / "tests" / "genome" / "fixtures_brain_law_pre_fm6.json").read_text())
NEAREST = {**T.CFG, "young_rule": "nearest"}


def _sha(o) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()


def young_life(cfg):
    """The toy life (120 scenes), then ONE meeting of a new word «zz» on a lone thing, then `begin` (a calibration)."""
    from genome import brain as B
    b = B.Brain(cfg)
    learned = T.live(b, 120)
    g, _w, _t, _b = T.toy_scene(120)
    one = {"feats": [g["feats"][0], g["feats"][-1]], "fix": [g["fix"][0]], "windows": [], "residual": [None, None]}
    learned.append(b.learn(one, ["zz"], moment=f"sc{T.WS}t{120:06d}", scene=120, world_seed=T.WS))
    b.ask({"form": "begin", "set": "fresh", "test_seed": 4242}, None)
    return b, learned


def young_asks(n: int = 16):
    rows = []
    for i in range(n):
        g, _words, _things, _boxes = T.toy_scene(20_000 + i)
        rows.append((g, {"form": "point", "item": f"Z:{i}", "mark": "M6", "phrase": ["zz"], "box": None, "word": None,
                         "test_seed": 4242}))
    return rows


def run(brain, rows):
    return [json.loads(json.dumps(brain.ask(p, g), sort_keys=True)) for g, p in rows]


class LawUnchanged(unittest.TestCase):
    def test_the_law_organ_equals_its_pre_fm6_fixture(self):
        from genome import brain as B
        b = B.Brain(T.CFG)
        learned = T.live(b, 120)
        self.assertEqual(b.state_hash(), FIX["state_hash"])
        self.assertEqual(_sha(learned), FIX["learned_sha256"])
        self.assertEqual(_sha(T.answers(b)), FIX["answers_sha256"])
        self.assertEqual(json.loads(json.dumps(b.summary())), FIX["summary"])
        self.assertNotIn("young_rule", vars(b.L))
        self.assertNotIn("young_rule", b.cfg)


class Config(unittest.TestCase):
    def test_nearest_sets_the_instance_attribute(self):
        from genome import brain as B
        b = B.Brain(NEAREST)
        self.assertEqual(b.L.young_rule, "nearest")
        self.assertEqual(b.cfg["young_rule"], "nearest")
        self.assertEqual(B.Brain(T.CFG).L.young_rule, "band")

    def test_band_is_the_law_and_leaves_no_trace(self):
        from genome import brain as B
        b = B.Brain({**T.CFG, "young_rule": "band"})
        self.assertNotIn("young_rule", b.cfg)
        self.assertNotIn("young_rule", vars(b.L))

    def test_another_word_refuses_by_name(self):
        from genome import brain as B
        with self.assertRaises(B.BrainError) as cm:
            B.Brain({**T.CFG, "young_rule": "euclid"})
        self.assertIn("young_rule", str(cm.exception))
        self.assertIn("'euclid'", str(cm.exception))

    def test_the_genome_line_reaches_the_learner(self):
        from genome import brain as B
        from genome.machinery import parse_genome
        alpha4 = (ROOT / "genome" / "ALPHA4.genome").read_text()
        line = ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3 nearest; "
                "calibrate at 250 500 1000 2000 5000 10000 and before a sitting; replay none; hears scene")
        b = B.Brain(parse_genome(alpha4 + "\n" + line + "\n").declared["BRAIN"])
        self.assertEqual(b.L.young_rule, "nearest")
        self.assertEqual(b.summary()["young_rule"], "nearest")


class Organ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.law, cls.law_learned = young_life(T.CFG)
        cls.fix, cls.fix_learned = young_life(NEAREST)

    def test_learning_is_the_laws(self):
        self.assertEqual(json.loads(json.dumps(self.fix_learned)), json.loads(json.dumps(self.law_learned)))
        for k in vars(self.law.L):
            a, b = getattr(self.law.L, k), getattr(self.fix.L, k)
            if isinstance(a, np.ndarray):
                self.assertTrue(np.array_equal(a, b), k)

    def test_every_other_ask_equals_the_law(self):
        self.assertEqual(run(self.fix, T.asks_for()), run(self.law, T.asks_for()))

    def test_one_young_word_points_by_nearest(self):
        law, fix = run(self.law, young_asks()), run(self.fix, young_asks())
        acted = 0
        for a, b in zip(law, fix):
            self.assertEqual(b["kind"], a["kind"])
            if b["kind"] in ("thing", "none"):
                self.assertEqual(b["raw"]["point_rule"], "nearest")
                acted += 1
                self.assertEqual({k: v for k, v in b["raw"].items() if k not in ("point", "young_d", "point_rule")},
                                 {k: v for k, v in a["raw"].items() if k != "point"})
                self.assertNotIn("point_rule", a["raw"])
        self.assertGreater(acted, 0)

    def test_state_hash_save_load(self):
        from genome import brain as B
        self.assertNotEqual(self.fix.state_hash(), self.law.state_hash())
        with tempfile.TemporaryDirectory(prefix="brain-fm6-") as td:
            base = Path(td) / "fix"
            self.fix.save(base)
            b2 = B.Brain.load(base, NEAREST)
            self.assertEqual(b2.state_hash(), self.fix.state_hash())
            self.assertEqual(b2.L.young_rule, "nearest")
            self.assertEqual(run(b2, young_asks()), run(self.fix, young_asks()))
            with self.assertRaises(B.BrainError) as cm:
                B.Brain.load(base, T.CFG)
            self.assertIn("young_rule", str(cm.exception))
            lb = Path(td) / "law"
            self.law.save(lb)
            with self.assertRaises(B.BrainError) as cm2:
                B.Brain.load(lb, NEAREST)
            self.assertIn("young_rule", str(cm2.exception))
            self.assertEqual(B.Brain.load(lb, T.CFG).state_hash(), self.law.state_hash())

    def test_summary_names_the_rule_only_when_nearest(self):
        self.assertEqual(self.fix.summary()["young_rule"], "nearest")
        self.assertNotIn("young_rule", self.law.summary())


if __name__ == "__main__":
    unittest.main()
