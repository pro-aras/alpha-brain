"""Tests for TOY B's analysis: on a SYNTHETIC world of lives the verdict machinery must classify a planted null-space protector, a planted protector-by-shrinking, a planted
freezer and a planted nothing correctly, catch the ANTI plant, and refuse a world where PLAIN does not forget or where the standardiser eats the whole ceiling.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:50 +0400 — written FIRST (red before tools/toys/nullspace/report.py exists); law: docs/research/toys/PREREG-TOY-NULLSPACE.md §3
# (the bars, gradability, the verdict classes, co-signed 2026-10-03 11:24 +0400).

The synthetic world: ten seeds; the task pair counts 139 / 141 / 192 (T-MEM-1's); a life is described by its accuracy matrix R[j][i] (task i's shape words after room j) and each pair
set is drawn from those accuracies, so the paired standard errors are real. PLAIN forgets (BWT_3 -0.21, BWT_4 -0.67); STD-ONLY is the ceiling (BWT_3 -0.04, BWT_4 -0.07).
"""
from __future__ import annotations

import unittest

import numpy as np

from tools.toys.nullspace import report as RN

SEEDS = list(range(20261301, 20261311))
NPAIRS = {1: 139, 2: 141, 3: 192}
READ = (50, 100, 150, 200)
TAUS = ("0.1", "0.01", "0.001")


def mk(R, rng, cpu=2.0):
    """R[(j, i)] = the accuracy of task i after room j (j = 1..4, i <= min(j, 3)); returns a life summary."""
    pairs = {}
    for j in (1, 2, 3, 4):
        pairs[READ[j - 1]] = {i: (rng.random(NPAIRS[i]) < R[(j, i)]).astype(int) for i in (1, 2, 3) if (j, i) in R}
    acc = {(j, i): float(pairs[READ[j - 1]][i].mean()) for j in (1, 2, 3, 4) for i in (1, 2, 3) if (j, i) in R}
    bwt = {j: float(np.mean([acc[(j, i)] - acc[(i, i)] for i in range(1, min(j, 4)) if (j, i) in acc])) for j in (2, 3, 4)}
    plast = {i: acc[(i, i)] for i in (1, 2, 3)}
    return {"bwt": bwt, "plast": plast, "pairs": pairs, "cpu": cpu, "A": 0.4, "eq50": True}


def table(r31, r32, r41, r42, r43, p2=0.95, p3=0.95, r21=0.82):
    return {(1, 1): 0.95, (2, 1): r21, (2, 2): p2, (3, 1): r31, (3, 2): r32, (3, 3): p3, (4, 1): r41, (4, 2): r42, (4, 3): r43}


PLAIN = table(0.70, 0.78, 0.30, 0.25, 0.30)
STD2 = table(0.90, 0.92, 0.0, 0.0, 0.0)             # frozen after room 2: BWT_3 only is read from it
STD3 = table(0.70, 0.78, 0.85, 0.88, 0.90)           # frozen after room 3: BWT_4
STD1 = table(0.70, 0.78, 0.30, 0.25, 0.30, r21=0.93)


def world(rng):
    S = {}

    def put(name, spec, reps=1, jitter=0.0):
        S[name] = {s: [mk({k: min(0.999, max(0.001, v + (rng.normal(0, jitter) if jitter else 0.0))) for k, v in spec.items()}, rng) for _ in range(reps)] for s in SEEDS}

    put("PLAIN", PLAIN)
    put("STD-ONLY@1", STD1)
    put("STD-ONLY@2", {**STD2, (4, 1): 0.3, (4, 2): 0.25, (4, 3): 0.3})
    put("STD-ONLY@3", STD3)
    # the planted NULL-SPACE protector at tau 0.01: protects, keeps learning, beats its nulls and its matched shrink
    good = table(0.88, 0.90, 0.80, 0.82, 0.85, p2=0.93, p3=0.92, r21=0.92)
    put("OWM@0.01", good)
    put("ROT@0.01", table(0.74, 0.80, 0.34, 0.30, 0.34), reps=10, jitter=0.02)
    put("SHRINK-OWM@0.01", table(0.74, 0.80, 0.36, 0.31, 0.36))
    # tau 0.1: «protects BY SHRINKING»: its null protects as well
    put("OWM@0.1", table(0.90, 0.92, 0.72, 0.74, 0.78, p2=0.94, p3=0.94))
    put("ROT@0.1", table(0.90, 0.92, 0.72, 0.74, 0.78, p2=0.94, p3=0.94), reps=10, jitter=0.02)
    put("SHRINK-OWM@0.1", table(0.74, 0.80, 0.36, 0.31, 0.36))
    # tau 0.001: protects hard and FREEZES (room 2 and 3 learning collapses)
    put("OWM@0.001", table(0.93, 0.55, 0.88, 0.55, 0.40, p2=0.55, p3=0.40))
    put("ROT@0.001", table(0.74, 0.80, 0.34, 0.30, 0.34), reps=10, jitter=0.02)
    put("SHRINK-OWM@0.001", table(0.74, 0.80, 0.36, 0.31, 0.36))
    for t in TAUS:                                     # NSCL: nothing
        put(f"NSCL@{t}", PLAIN)
        put(f"RANDRANK@{t}", PLAIN, reps=10, jitter=0.02)
        put(f"SHRINK-NSCL@{t}", PLAIN)
    put("ANTI-OWM@0.01", table(0.50, 0.55, 0.15, 0.12, 0.15))
    return S


class TestAnalyse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rng = np.random.default_rng(11)
        cls.summ = world(cls.rng)
        cls.an = RN.analyse(cls.summ, SEEDS)

    def test_the_world_is_gradable(self):
        g = self.an["gradable"]
        self.assertTrue(g["c1"]["ok"], g)
        self.assertTrue(g["c2"]["ok"], g)
        self.assertTrue(g["ok"])

    def test_the_planted_null_space_protector_is_class_one(self):
        a = self.an["arms"]["OWM@0.01"]
        self.assertTrue(a["B_PROTECT"]["ok"], a)
        self.assertTrue(a["B_NULLSPACE"]["ok"], a)
        self.assertTrue(a["B_SHRINK"]["ok"], a)
        self.assertTrue(a["B_PLASTIC"]["ok"], a)
        self.assertEqual(a["class"], "NULL-SPACE-PROTECTS")

    def test_the_planted_protector_by_shrinking_fails_its_nulls(self):
        a = self.an["arms"]["OWM@0.1"]
        self.assertTrue(a["B_PROTECT"]["ok"], a)
        self.assertFalse(a["B_NULLSPACE"]["ok"], a)
        self.assertFalse(a["B_SHRINK"]["ok"] and a["B_NULLSPACE"]["ok"])
        self.assertEqual(a["class"], "PROTECTS-BY-SHRINKING")

    def test_the_planted_freezer_protects_but_fails_plasticity(self):
        a = self.an["arms"]["OWM@0.001"]
        self.assertTrue(a["B_PROTECT"]["ok"] and a["B_NULLSPACE"]["ok"] and a["B_SHRINK"]["ok"], a)
        self.assertFalse(a["B_PLASTIC"]["ok"], a)
        self.assertEqual(a["class"], "PROTECTS-BUT-FREEZES")

    def test_nscl_that_does_nothing_is_class_nothing(self):
        for t in TAUS:
            self.assertEqual(self.an["arms"][f"NSCL@{t}"]["class"], "NOTHING")

    def test_the_headline_is_the_best_class_reached(self):
        self.assertEqual(self.an["headline"], "NULL-SPACE-PROTECTS")

    def test_the_anti_plant_loses(self):
        self.assertTrue(self.an["PB1"]["ok"], self.an["PB1"])

    def test_forgetting_removed_share_is_computed_against_the_ceiling(self):
        share = self.an["arms"]["OWM@0.01"]["removed_share"]
        self.assertGreater(share[3], 0.7)
        self.assertLess(share[3], 1.3)
        self.assertAlmostEqual(self.an["arms"]["NSCL@0.01"]["removed_share"][3], 0.0, delta=0.15)

    def test_plain_that_does_not_forget_is_not_gradable(self):
        rng = np.random.default_rng(3)
        S = world(rng)
        mild = table(0.93, 0.94, 0.92, 0.93, 0.94)
        S["PLAIN"] = {s: [mk(mild, rng)] for s in SEEDS}
        an = RN.analyse(S, SEEDS)
        self.assertFalse(an["gradable"]["c1"]["ok"])
        self.assertFalse(an["gradable"]["ok"])
        self.assertEqual(an["headline"], "NOT-GRADABLE")

    def test_a_ceiling_the_standardiser_eats_makes_protection_not_gradable(self):
        rng = np.random.default_rng(4)
        S = world(rng)
        S["STD-ONLY@2"] = {s: [mk({**PLAIN}, rng)] for s in SEEDS}                 # freezing the weights changes nothing: the standardiser is the whole forgetting
        S["STD-ONLY@3"] = {s: [mk({**PLAIN}, rng)] for s in SEEDS}
        an = RN.analyse(S, SEEDS)
        self.assertFalse(an["gradable"]["c2"]["ok"])
        self.assertEqual(an["headline"], "NOT-GRADABLE")

    def test_rank_among_the_null_draws(self):
        self.assertEqual(RN.rank_among(0.9, [0.1] * 10), 1)
        self.assertEqual(RN.rank_among(0.5, [0.9] + [0.1] * 9), 2)
        self.assertEqual(RN.rank_among(0.0, [0.5] * 10), 11)
        self.assertTrue(RN.rank_among(0.9, [0.1] * 9 + [0.95]) <= 2)

    def test_the_pb4_check_counts_arms_that_differ_from_plain_before_block_50(self):
        summ = {a: {s: [dict(v[0], eq50=True)] for s, v in d.items()} for a, d in self.summ.items()}
        summ["OWM@0.01"][SEEDS[0]][0]["eq50"] = False                               # the plant: an arm that differs from PLAIN inside room 1
        an = RN.analyse(summ, SEEDS)
        self.assertEqual(an["PB4"]["violations"], [("OWM@0.01", SEEDS[0])])

    def test_render_runs_and_names_the_headline(self):
        text = "\n".join(RN.render(self.an, self.summ, SEEDS))
        self.assertIn("HEADLINE: NULL-SPACE-PROTECTS", text)
        self.assertIn("GRADABILITY", text)
        self.assertIn("THE FRONTIER", text)


if __name__ == "__main__":
    unittest.main()
