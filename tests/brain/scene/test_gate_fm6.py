# edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:29 +0400 — tools/brain/gate_fm6.py (PREREG-BRAIN-IN-BODY AMENDMENT 1 §2) on a TINY
# glance cache built here (train 40 scenes; every split of «held», «fresh» and «s1b1» at 2–6 scenes), light: the two organs in
# lockstep, IDENTITY PASS for the real fix, FAIL for the planted control, the answer files in gate_alone's shape, the pool's
# arithmetic, and the refusal to write under a scored / glances / life root. Written AFTER the tool (no red log: RAISED).
"""tests/brain/scene/test_gate_fm6.py — the F-M6 bench gate, small."""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

from brain.scene import cache as C
from brain.scene import run as R

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("gate_fm6", str(ROOT / "tools" / "brain" / "gate_fm6.py"))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))
WS = 20261102
TINY = {"calibrate_at": [20, 40]}


class TestGateTiny(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TMP.mkdir(parents=True, exist_ok=True)
        cls._td = tempfile.TemporaryDirectory(dir=str(TMP), prefix="gate-fm6-test-")
        cls.root = Path(cls._td.name) / "caches"
        cls.out = Path(cls._td.name) / "out"
        C.build("train", WS, C.cache_dir(cls.root, WS, "train"), limit=40, recheck_n=1)
        for tset in ("held", "fresh"):
            for split in C.test_splits(tset):
                C.build(split, WS, C.cache_dir(cls.root, WS, split, tset), limit=6 if split == "test" else 2, recheck_n=1,
                        tset=tset)
            R.build_questions_r(cls.root, WS, tset)
        for split in C.test_splits("s1b1"):
            C.build(split, WS, C.cache_dir(cls.root, WS, split, "s1b1"), limit=6 if split == "test" else 2, recheck_n=1,
                    tset="s1b1")
        R.build_questions(cls.root, WS)
        cls.res = G.run_seed(WS, cls.root, cls.root, cls.out, cfg_over=TINY, log=lambda s: None)
        cls.planted = G.run_seed(WS, cls.root, cls.root, cls.out, do_plant=True, cfg_over=TINY, log=lambda s: None)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._td.cleanup()

    def test_the_fix_passes_identity_and_learns_as_the_law(self):
        r = self.res
        self.assertEqual(r["learn_rows_differing"], 0)
        self.assertEqual(set(r["identity"]), {"held", "fresh", "s1b1"})
        for s, b in r["identity"].items():
            self.assertGreater(b["compared"], 0, s)
            self.assertEqual(b["compared"], b["equal"], (s, b["first"]))
            self.assertEqual(b["acted_outside_young"], 0, s)
        self.assertTrue(r["identity_pass"])

    def test_the_planted_control_fails_identity(self):
        p = self.planted
        self.assertFalse(p["identity_pass"])
        self.assertGreater(sum(b["acted_outside_young"] for b in p["identity"].values()), 0)

    def test_answer_files_in_gate_alones_shape(self):
        d = self.out / str(WS)
        for who in ("law", "fix"):
            gate = json.loads((d / f"{who}-gate-answers.json").read_text())
            held = json.loads((d / f"{who}-held-answers.json").read_text())
            Qf = json.loads((self.root / str(WS) / "fresh" / "questions.json").read_text())["questions"]
            Qo = json.loads((self.root / str(WS) / "questions.json").read_text())["questions"]
            Qh = json.loads((self.root / str(WS) / "held" / "questions.json").read_text())["questions"]
            want = ({q["item_id"] for qs in Qf.values() for q in qs}
                    | {"older/" + q["item_id"] for m in G.GA.POINT_MARKS for q in Qo.get(m, [])})
            self.assertEqual(set(gate), want)
            self.assertEqual(set(held), {q["item_id"] for qs in Qh.values() for q in qs})
            for a in list(gate.values()) + list(held.values()):
                self.assertIn("kind", a)
                self.assertIn("raw", a)
        self.assertTrue((d / "fm6.json").exists() and (d / "fm6.txt").exists() and (d / "planted.json").exists())

    def test_m6_block(self):
        m = self.res["M6_held"]
        self.assertEqual(m["n_items"], 2)                              # the tiny «held» m6 cache: 2 rows
        self.assertIn("NOT GRADABLE", m["verdict"])                    # 40 scenes hold no «dax» meeting
        self.assertIsNone(self.res["meeting_seen"])
        self.assertEqual(len(m["items"]), 2)

    def test_refuses_to_write_under_a_root(self):
        for bad in (C.S1B1R_RUNS / "x", C.RUNS / "y", Path("/data/dev/genome-lives/brain-lean-20261102/z"), C.SCENE_ORGAN_RUNS):
            with self.assertRaises(SystemExit):
                G.refuse_out(bad)
        with self.assertRaises(SystemExit):
            G.refuse_out(self.root / "sub", (self.root,))
        G.refuse_out(self.out)


class TestYoungBranch(unittest.TestCase):
    """The tiny cache holds no «dax» meeting, so the gate's young branch is exercised here on the organ's toy life."""

    def test_is_young_point_and_strip(self):
        from tests.genome import test_brain_fm6 as TB
        law, _l = TB.young_life(TB.T.CFG)
        fix, _f = TB.young_life(TB.NEAREST)
        g, p = TB.young_asks(1)[0]
        self.assertTrue(G.is_young_point(law, p))
        self.assertFalse(G.is_young_point(law, {**p, "phrase": ["sa"]}))           # a mature word
        self.assertFalse(G.is_young_point(law, {**p, "phrase": ["zz", "sa"]}))     # two words
        self.assertFalse(G.is_young_point(law, {**p, "phrase": ["never"]}))        # never heard
        self.assertFalse(G.is_young_point(law, {**p, "form": "what"}))
        a, f = G.GA.canon(law.ask(p, g)), G.GA.canon(fix.ask(p, g))
        self.assertIn("point_rule", f["raw"])
        self.assertIsNone(G.GA.first_diff(G.strip(a), G.strip(f)))
        f2 = json.loads(json.dumps(f))
        f2["raw"]["best"] = f2["raw"]["best"] + 1.0                                  # a moved law number is caught
        self.assertIsNotNone(G.GA.first_diff(G.strip(a), G.strip(f2)))


class TestPool(unittest.TestCase):
    def _rec(self, d: Path, ws: int, pairs, seen=True):
        items = [{"item_id": f"M6:{ws}:{i}", "covered": True, "gradable": True, "law": bool(l), "fix": bool(f), "chance": 0.5}
                 for i, (l, f) in enumerate(pairs)]
        rec = {"world_seed": ws, "meeting_seen": seen, "identity_pass": True, "M6_held": {"items": items, "verdict": "PASS"}}
        (d / str(ws)).mkdir(parents=True, exist_ok=True)
        (d / str(ws) / "fm6.json").write_text(json.dumps(rec))
        return d / str(ws)

    def test_the_pooled_sign_test(self):
        self.assertAlmostEqual(G.binom_tail(10, 10), 1 / 1024)
        self.assertIsNone(G.binom_tail(0, 0))
        with tempfile.TemporaryDirectory(dir=str(TMP)) as td:
            d = Path(td)
            a = self._rec(d, 20261102, [(0, 1)] * 6 + [(1, 1)] * 20)
            b = self._rec(d, 20261103, [(0, 1)] * 6 + [(1, 1)] * 20 + [(0, 0)] * 4)
            r = G.pool([a, b], log=lambda s: None)
            self.assertEqual((r["n"], r["b"], r["c"]), (56, 12, 0))
            self.assertAlmostEqual(r["p"], 1 / 4096)
            self.assertAlmostEqual(r["gap"], 12 / 56)
            self.assertEqual(r["verdict"], "PASS")
            c = self._rec(d, 20261101, [(0, 1)] * 30, seen=False)
            r2 = G.pool([c, b], log=lambda s: None)
            self.assertEqual(r2["pooled_seeds"], [20261103])
            e = self._rec(Path(td) / "e", 20261102, [(0, 1)] * 5 + [(1, 0)] * 1 + [(1, 1)] * 20)
            r3 = G.pool([e, b], log=lambda s: None)
            self.assertEqual(r3["verdict"], "FAIL")                    # b 11, c 1: p ≈ 0.003 > 0.001


if __name__ == "__main__":
    unittest.main()
