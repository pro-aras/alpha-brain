"""PREREG-W2 AMENDMENT 1 (SIGNED x3, w2-1005 1893280) + the seat's G-PICTURE ruling (the board, 2026-10-06 17:5x):
the verdict reader's margin-form necessity mark and the law's own train/test split.

# edit: Kimi Code (K3, kimi-code, acting seat, alone), 2026-10-06 18:15 +0400 — new file, written RED before
# report.py / bench.py were touched. A1.2 (b): G-PICTURE is a READING (printed, never a void); the NECESSITY mark =
# gain_margin = (AUC_CONT - AUC_NOSTATE) / (1 - AUC_NOSTATE) >= 0.5, with NOSTATE >= 1 - eps (eps = 0.001) NOT GRADABLE
# by name (the divide-by-zero guard); a state word whose necessity is unproven does not bind, and is NAMED. A1.3: fewer
# than two gradable-and-binding states on a seed reads PARTIAL, never PASS. A1.1: the graded split is the law's
# 16,000/4,000 — the bench's default train_end is 16,250.
"""
from __future__ import annotations

import inspect
import unittest

from tools.toys.w2 import bench as B
from tools.toys.w2 import report as R

SEEDS = (20261701, 20261702, 20261703)


def _rec(nostate, cont, m1_pass=True, pos=400):
    """One minimal seed record, every field report.read touches, hand-set. Default: the pilot's own shape
    (NOSTATE 0.8551, CONT 1.0 -> margin 1.0) with doubt + ask_prev gradable and young structurally absent."""
    words = ("unsure", "fresh", "asked")
    return {
        "gates": {"census": [{"ok": True, "n_checked": 3}],
                  "truth": {"planted_caught": True, "n_equal": 5, "n": 5},
                  "stream_hash": "abcdef0123456789"},
        "const": {w: 0.5 for w in words},
        "nostate": {"auc": {w: nostate.get(w) for w in words}},
        "cont": {"auc": {w: cont.get(w) for w in words},
                 "naming": {"cont": 0.99, "nostate": 0.98, "n": 2000, "gradable": True, "pass": True}},
        "blind": {w: 0.85 for w in words},
        "oracle": {w: {"c_read": 1.0} for w in words},
        "dealt_diag": {w: [0.50] * 10 for w in words},
        "test_n": {"doubt": {"pos": pos, "neg": 3600}, "young": {"pos": 0, "neg": 4000},
                   "ask_prev": {"pos": 300, "neg": 3700}},
        "m1": {w: {"pass": m1_pass, "auc": 0.99, "skill": 0.96, "q95": 0.6} for w in words},
        "proto_home": {"n_on_state": 0, "n_present": 7, "n": 2000, "smallest_gap": 0.4},
        "marks_truth": {
            "m_true": {"pass": True, "first_false": None, "n_productions": 50, "n_rows": 50},
            "m_attrib": {"pass": True, "n_rows": 50, "n_unparseable": 0, "coverage": {"share": 0.9, "sayable": 100}},
            "m_joint": {"pass": True, "share": 0.9, "n_rows": 50, "null": {"q95": 0.6, "mean": 0.55}},
            "m_contingent_i": {"pass": True, "n_aligned": 10, "n_tokens": 10},
            "m_selfvoice_answers": {"pass": True, "n_ear_rows": 20, "n_answer_rows_off_referent": 0}},
    }


def _recs(mods=()):
    recs = {s: _rec({"unsure": 0.8551, "fresh": None, "asked": 0.62},
                    {"unsure": 1.0, "fresh": None, "asked": 0.95}) for s in SEEDS}
    for seed, word, key, val in mods:
        recs[seed][key][word] = val
    return recs


class TestNecessityMarginForm(unittest.TestCase):
    def test_pilot_shape_passes_and_the_margin_is_printed(self):
        out = R.read(_recs())
        self.assertEqual(out["verdict"]["verdict"], "PASS", out["lines"][-2:])
        self.assertEqual(out["verdict"]["row"], 2)
        nec = out["necessity"]["unsure"]["20261701"]
        self.assertAlmostEqual(nec["margin"], 1.0, places=6)      # (1.0 - 0.8551) / (1 - 0.8551)
        self.assertTrue(nec["pass"])
        self.assertTrue(any("G-PICTURE" in l and "READING" in l for l in out["lines"]))

    def test_g_picture_never_voids(self):
        # NOSTATE 0.95 > the old 0.60 gate: the SIGNED law's form would VOID; under the ruling it must PASS
        recs = {s: _rec({"unsure": 0.95, "fresh": None, "asked": 0.62},
                        {"unsure": 1.0, "fresh": None, "asked": 0.95}) for s in SEEDS}
        out = R.read(recs)
        self.assertEqual(out["verdict"]["verdict"], "PASS", out["lines"][-2:])

    def test_epsilon_guard_names_not_gradable(self):
        recs = {s: _rec({"unsure": 0.9995, "fresh": None, "asked": 0.62},
                        {"unsure": 1.0, "fresh": None, "asked": 0.95}) for s in SEEDS}
        out = R.read(recs)
        nec = out["necessity"]["unsure"]["20261701"]
        self.assertFalse(nec["gradable"])
        self.assertIn("gap is zero", nec["why"])
        self.assertNotEqual(out["verdict"]["verdict"], "VOID")           # the guard names, never voids
        self.assertEqual(out["verdict"]["verdict"], "PARTIAL")           # only asked binds now
        self.assertTrue(any("unsure" in l and "NECESSITY" in l and "NOT GRADABLE" in l for l in out["lines"]))

    def test_necessity_failure_excludes_the_word(self):
        # CONT 0.90 vs NOSTATE 0.8551 -> margin ~0.31 < 0.5: the state row closes less than half the gap
        recs = {s: _rec({"unsure": 0.8551, "fresh": None, "asked": 0.62},
                        {"unsure": 0.90, "fresh": None, "asked": 0.95}) for s in SEEDS}
        out = R.read(recs)
        nec = out["necessity"]["unsure"]["20261701"]
        self.assertTrue(nec["gradable"])
        self.assertFalse(nec["pass"])
        self.assertEqual(out["verdict"]["verdict"], "PARTIAL", out["lines"][-2:])

    def test_fewer_than_two_gradable_and_binding_on_a_seed_reads_partial(self):
        # seeds 01/02 bind unsure+asked; seed 03's unsure FAILS M-BIND -> one gradable-and-binding state on seed 03
        recs = _recs()
        recs[20261703]["m1"]["unsure"] = {"pass": False, "auc": 0.70, "skill": 0.60, "q95": 0.6}
        out = R.read(recs)
        self.assertEqual(out["verdict"]["verdict"], "PARTIAL", out["lines"][-2:])
        self.assertTrue(any("gradable-and-binding" in l for l in out["lines"]))

    def test_the_walk_still_fails_loudly(self):
        # the negative control: nothing binds anywhere -> FAIL-STRUCTURE (row 6), never a silent pass
        out = R.read(_recs())
        recs = {s: _rec({"unsure": 0.8551, "fresh": None, "asked": 0.62},
                        {"unsure": 1.0, "fresh": None, "asked": 0.95}, m1_pass=False) for s in SEEDS}
        out = R.read(recs)
        self.assertEqual(out["verdict"]["verdict"], "FAIL-STRUCTURE", out["lines"][-2:])
        # and a truth-family plant missed -> VOID (row 1): the other gates are untouched by the ruling
        recs = _recs()
        for s in SEEDS:
            recs[s]["gates"]["truth"]["planted_caught"] = False
        out = R.read(recs)
        self.assertEqual(out["verdict"]["verdict"], "VOID")
        self.assertEqual(out["verdict"]["row"], 1)


class TestTheLawsSplit(unittest.TestCase):
    def test_the_benchs_default_split_is_the_laws_16000_4000(self):
        self.assertEqual(inspect.signature(B.arms_bench).parameters["train_end"].default, 16250)


if __name__ == "__main__":
    unittest.main()
