# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:46 +0400 — PREREG-ACT-EFFECT §5/§7: the MECHANICAL VERDICT (tools/toys/act_effect_verdict.py) — the admission is read by code from the bench's JSON, not by
# a person. RED first, each mark with a planted failure that must flip exactly that mark, and a plant that is NOT caught must VOID the bench (§5 M5: «a plant not caught = the instrument is wrong»).
from __future__ import annotations

import copy
import unittest
from typing import Dict, List

from tools.toys import act_effect_verdict as V

SEEDS = [20260923 + 1_000_000 * k for k in range(12)]
NULL = [0.274, 0.293, 0.267, 0.251, 0.264, 0.265, 0.279, 0.264, 0.256, 0.304, 0.279, 0.268]      # the landed R-NULL rows (§5)
R3 = [0.419, 0.458, 0.409, 0.433, 0.434, 0.456, 0.429, 0.419, 0.433, 0.45, 0.439, 0.428]
CEIL = [0.462, 0.497, 0.506, 0.461, 0.478, 0.527, 0.494, 0.494, 0.477, 0.49, 0.496, 0.472]


def _arm(per_seed: List[float]) -> Dict[str, object]:
    return {"per_seed": list(per_seed), "success_mean": sum(per_seed) / len(per_seed),
            "runs": [{"seed": s, "success_rate": x, "successes": int(round(x * 1000)), "episodes": 1000, "steps": 54000} for s, x in zip(SEEDS, per_seed)]}


def statusquo() -> Dict[str, object]:
    return {"seeds": SEEDS, "arms": {"ii": _arm(NULL), "iii": _arm(R3), "iv-0.5": _arm(CEIL)}}


def bench() -> Dict[str, object]:
    arms = {"R-NULL2": _arm([x + d for x, d in zip(NULL, [0.004, -0.006, 0.002, 0.007, -0.003, 0.001, -0.002, 0.005, -0.004, 0.003, 0.0, -0.001])]),
            "R-SCR": _arm([x - 0.015 for x in R3]),
            "C-SCR": _arm([x + 0.142 + e for x, e in zip(NULL, [0.01, -0.012, 0.02, 0.0, -0.01, 0.015, 0.0, -0.008, 0.012, -0.02, 0.005, 0.0])]),
            "A-PROP": _arm([x + 0.11 for x in NULL]), "A-UCB": _arm(NULL), "A-RATE": _arm([x + 0.03 for x in NULL]),
            "A-BOTH": _arm([x + 0.17 for x in NULL]), "K-ARGMAX": _arm([0.1] * 12), "P-DEAL": _arm([0.05] * 12),
            "R-WSLS": _arm([0.5] * 12), "R-WALK": _arm([0.52] * 12),
            "R-NULL": _arm(NULL)}
    return {"seeds": SEEDS, "arms": arms}


def lives_summary(h960: float, h4920: float, noop_le: float = 1.0, noop_ge: float = 0.0, m4a=None, m4b=None) -> Dict[str, object]:
    s = {"h960": {"lock_pass_share": h960, "single_act_flag_share": 0.0, "x1_pass_share": 0.9, "top2_max_median": 0.8, "top1_max_median": 0.5},
         "h4920": {"lock_pass_share": h4920, "single_act_flag_share": 0.0, "x1_pass_share": 0.9, "top2_max_median": 0.82, "top1_max_median": 0.52},
         "noop_share": {"median": 0.06, "le_0.25_share": noop_le, "ge_0.5_share": noop_ge},
         "x2_printed": {"episodes_median": 13, "success_mean": 0.4}}
    if m4a is not None:
        s.update({"m4a_ge_0.95_share": m4a, "m4b_ge_0.95_share": m4b, "m4a_median": 0.997, "m4b_median": 0.995, "exact_set_median": 0.98,
                  "latency_first_act_set_holds_60": {"lives_with_it": 50, "median": 165}})
    return s


def lives() -> Dict[str, object]:
    arms = {"C-SCR": lives_summary(0.98, 0.94, 1.0, 0.0, 1.0, 0.98),
            "P-OLD": lives_summary(0.0, 0.0, 1.0, 0.0), "K-ARGMAX": lives_summary(0.0, 0.0, 1.0, 0.0),
            "P-DEAL": lives_summary(0.9, 0.9, 0.0, 1.0, 1.0, 1.0), "R-NULL": lives_summary(1.0, 1.0, 0.0, 1.0),
            "R-3": lives_summary(1.0, 1.0, 1.0, 0.0), "A-VAL": lives_summary(1.0, 1.0, 0.0, 1.0), "A-RATE": lives_summary(1.0, 1.0, 0.0, 1.0),
            "A-BOTH": lives_summary(0.99, 0.95, 1.0, 0.0, 1.0, 1.0)}
    return {"acts": 4920, "n": 50, "arms": {k: {"summary": v} for k, v in arms.items()}}


def run(**over):
    sq, b, b2, lv, eq = statusquo(), bench(), bench(), lives(), {"pass": True, "steps": 20000, "mismatches": 0}
    sq.update(over.get("sq", {})); b.update(over.get("b", {})); lv.update(over.get("lv", {}))
    if "mutate" in over:
        over["mutate"](sq, b, b2, lv, eq)
    return V.verdict(sq, b, b2, lv, eq, unit_tests_ok=over.get("unit", True))


class TestAdmission(unittest.TestCase):
    def test_a_clean_set_is_admitted_and_every_mark_is_read(self) -> None:
        v = run()
        for k in ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"):
            self.assertIn(k, v["marks"])
            self.assertTrue(v["marks"][k]["pass"], (k, v["marks"][k]))
        self.assertTrue(v["admit"])
        self.assertFalse(v["void"])

    def test_the_candidate_is_reported_against_both_r3_and_r_scr(self) -> None:
        v = run()
        rd = v["readings"]
        for k in ("c_scr_minus_r3", "c_scr_minus_r_scr", "c_scr_minus_null", "r3_seedwise_p95", "r_scr_mean", "r3_mean", "ceiling_mean", "null_mean", "null_sd", "null2_minus_null_sd",
                  "smallest_detectable_gap_seed_level"):
            self.assertIn(k, rd)
        self.assertGreater(rd["c_scr_minus_null"], 0.10)
        self.assertLess(rd["c_scr_minus_r3"], 0.0)


class TestM1(unittest.TestCase):
    def test_gain_below_0_10_fails_clause_a(self) -> None:
        def m(sq, b, b2, lv, eq):
            b["arms"]["C-SCR"] = _arm([x + 0.09 for x in NULL])
        v = run(mutate=m)
        self.assertFalse(v["marks"]["M1"]["a"])
        self.assertFalse(v["marks"]["M1"]["pass"])
        self.assertFalse(v["admit"])

    def test_ten_of_twelve_positive_seeds_fails_clause_b(self) -> None:
        def m(sq, b, b2, lv, eq):
            x = [n + 0.16 for n in NULL]
            x[0] = NULL[0] - 0.01
            x[1] = NULL[1] - 0.01
            b["arms"]["C-SCR"] = _arm(x)
        v = run(mutate=m)
        self.assertFalse(v["marks"]["M1"]["b"])
        self.assertEqual(v["marks"]["M1"]["positive_seeds"], 10)

    def test_below_r_scr_minus_0_03_fails_clause_d(self) -> None:
        def m(sq, b, b2, lv, eq):
            b["arms"]["R-SCR"] = _arm([x + 0.20 for x in NULL])                    # its own stationary bound moved up: 0.472
            b["arms"]["C-SCR"] = _arm([x + 0.14 for x in NULL])                    # 0.412: 0.06 below it
        v = run(mutate=m)
        self.assertFalse(v["marks"]["M1"]["d"])

    def test_the_t_test_clause_c(self) -> None:
        """Clause (c) isolated: every seed positive (b holds), the mean just over +0.10 (a holds), but six seeds gain nothing and six gain 0.2 — t = 3.5 < 4.437."""
        def m(sq, b, b2, lv, eq):
            b["arms"]["C-SCR"] = _arm([n + g for n, g in zip(NULL, [0.0001] * 6 + [0.2] * 6)])
        v = run(mutate=m)
        self.assertTrue(v["marks"]["M1"]["a"])
        self.assertTrue(v["marks"]["M1"]["b"])
        self.assertFalse(v["marks"]["M1"]["c"], "a bimodal +0.10 is not p < 0.001")
        self.assertFalse(v["marks"]["M1"]["pass"])


class TestLivesMarks(unittest.TestCase):
    def test_M2_thresholds_95_at_960_and_90_at_4920(self) -> None:
        def a(sq, b, b2, lv, eq): lv["arms"]["C-SCR"]["summary"]["h960"]["lock_pass_share"] = 0.94
        def c(sq, b, b2, lv, eq): lv["arms"]["C-SCR"]["summary"]["h4920"]["lock_pass_share"] = 0.88
        self.assertFalse(run(mutate=a)["marks"]["M2"]["pass"])
        self.assertFalse(run(mutate=c)["marks"]["M2"]["pass"])
        def ok(sq, b, b2, lv, eq):
            lv["arms"]["C-SCR"]["summary"]["h960"]["lock_pass_share"] = 0.95
            lv["arms"]["C-SCR"]["summary"]["h4920"]["lock_pass_share"] = 0.90
        self.assertTrue(run(mutate=ok)["marks"]["M2"]["pass"])

    def test_M3_needs_95_percent_of_lives_at_or_below_0_25(self) -> None:
        def m(sq, b, b2, lv, eq): lv["arms"]["C-SCR"]["summary"]["noop_share"]["le_0.25_share"] = 0.9
        self.assertFalse(run(mutate=m)["marks"]["M3"]["pass"])

    def test_M3_is_conjunctive_the_lock_alone_does_not_pass(self) -> None:
        def m(sq, b, b2, lv, eq):
            lv["arms"]["C-SCR"]["summary"]["h960"]["lock_pass_share"] = 0.0       # M2 fails; M3 reads fine
        v = run(mutate=m)
        self.assertTrue(v["marks"]["M3"]["alone"], "the no-op share reads fine by itself (the lock passes M3 alone)")
        self.assertFalse(v["marks"]["M3"]["pass"], "but M3 is only read jointly with M1 and M2")

    def test_M4_bars_a_and_b_in_90_percent_of_lives(self) -> None:
        def a(sq, b, b2, lv, eq): lv["arms"]["C-SCR"]["summary"]["m4a_ge_0.95_share"] = 0.85
        def c(sq, b, b2, lv, eq): lv["arms"]["C-SCR"]["summary"]["m4b_ge_0.95_share"] = 0.85
        self.assertFalse(run(mutate=a)["marks"]["M4"]["pass"])
        self.assertFalse(run(mutate=c)["marks"]["M4"]["pass"])


class TestPlantsM5(unittest.TestCase):
    def test_all_three_plants_caught_passes(self) -> None:
        self.assertTrue(run()["marks"]["M5"]["pass"])

    def test_a_plant_that_is_not_caught_voids_the_bench(self) -> None:
        for name, h in (("K-ARGMAX", "h960"), ("P-OLD", "h4920")):
            def m(sq, b, b2, lv, eq, name=name, h=h): lv["arms"][name]["summary"][h]["lock_pass_share"] = 0.5
            v = run(mutate=m)
            self.assertFalse(v["marks"]["M5"]["pass"], name)
            self.assertTrue(v["void"], f"{name} not caught: the instrument is wrong, the bench is VOID")
            self.assertFalse(v["admit"])

    def test_the_dealt_plant_must_not_beat_the_null(self) -> None:
        def m(sq, b, b2, lv, eq): b["arms"]["P-DEAL"] = _arm([x + 0.05 for x in NULL])
        v = run(mutate=m)
        self.assertFalse(v["marks"]["M5"]["pass"])
        self.assertTrue(v["void"])

    def test_the_dealt_plant_must_read_as_a_failure_of_m3(self) -> None:
        def m(sq, b, b2, lv, eq): lv["arms"]["P-DEAL"]["summary"]["noop_share"]["ge_0.5_share"] = 0.3
        self.assertFalse(run(mutate=m)["marks"]["M5"]["pass"])


class TestInstrumentsM6toM9(unittest.TestCase):
    def test_M7_the_null_through_the_new_path_must_equal_the_landed_rows_exactly(self) -> None:
        def m(sq, b, b2, lv, eq):
            b["arms"]["R-NULL"]["per_seed"][3] += 0.001
        v = run(mutate=m)
        self.assertFalse(v["marks"]["M7"]["pass"])
        self.assertTrue(v["void"])

    def test_M7_the_candidate_twice_must_be_identical(self) -> None:
        def m(sq, b, b2, lv, eq):
            b2["arms"]["C-SCR"]["per_seed"][5] += 0.002
        self.assertFalse(run(mutate=m)["marks"]["M7"]["pass"])

    def test_M8_a_mismatch_fails(self) -> None:
        def m(sq, b, b2, lv, eq):
            eq.update({"pass": False, "mismatches": 2})
        self.assertFalse(run(mutate=m)["marks"]["M8"]["pass"])

    def test_M6_and_M9_are_the_unit_tests(self) -> None:
        v = run(unit=False)
        self.assertFalse(v["marks"]["M6"]["pass"])
        self.assertFalse(v["marks"]["M9"]["pass"])
        self.assertFalse(v["admit"])


class TestPrintedReadings(unittest.TestCase):
    def test_alternatives_are_printed_never_admitted(self) -> None:
        v = run()
        alt = v["alternatives"]
        for k in ("A-PROP", "A-UCB", "A-RATE", "A-BOTH", "R-WSLS", "R-WALK", "A-VAL", "A-SMP"):
            if k in alt:
                self.assertIn("minus_null", alt[k])
        self.assertTrue(alt["A-BOTH"]["clears_r3_seedwise_p95"] is False or alt["A-BOTH"]["clears_r3_seedwise_p95"] is True)
        self.assertFalse(v["marks"].get("alternatives_admitted", False))

    def test_a_class_b_reference_above_r3_p95_is_flagged_as_the_next_laws_case(self) -> None:
        v = run()
        self.assertTrue(v["alternatives"]["R-WALK"]["clears_r3_seedwise_p95"])
        self.assertIn("R-WALK", v["next_law_cases"])


if __name__ == "__main__":
    unittest.main()
