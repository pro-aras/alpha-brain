# edit: Claude (Opus 5.5), 2026-09-26 18:32 +0400 — R40: PREREG §5.5 «a failing control VOIDS the arm, never "fails" it». results.py
# had no VOID state: a failed control was an ordinary failed mark, the selection read a voided candidate as FAILED, and D1's
# comparisons read the readings of arms §5.5 voids. These pin the VOID state on planted marks and on seed 20261001's committed
# marks (A5, E′ and F each fail SAME there), the exemptions a construction guarantees (KEY's canary, SHIFTED-KEY, the shuffled
# twins' relation controls), and that a VOID twin supplies no null.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from brain.harness import graders as G
from brain.harness import results as R

ROOT = Path(__file__).resolve().parents[3]
SEED1 = ROOT / "docs" / "brain" / "b1" / "results" / "20261001" / "results.json"


def ctl(name: str, passed, graded: bool = True, reason: str = ""):
    return G._mark(name, reading=(1.0 if passed else 0.3), graded=graded, passed=(passed if graded else None),
                   reason_code=reason, klass="CONTROL")


def u3(fam: str, reading: float, passed: bool = True):
    return G._mark(f"U3_{fam}@T_L", reading=reading, graded=True, passed=passed, bar=1, klass="U3")


def controls(**failing):
    out = {}
    for k in ("C0a_CONST", "C0a_SAME", "C0d_CANARY", "C0e_FROZEN"):
        out[k] = ctl(k, not failing.get(k, False))
    return out


def arm(marks):
    return {"marks": marks, "partition": G.partition(marks)}


def learner(twoafter: float, chain: float, **failing):
    m = controls(**failing)
    m.update({"U3_TWO_AFTER@T_L": u3("TWO_AFTER", twoafter, twoafter >= 0.5), "U3_CHAIN@T_L": u3("CHAIN", chain, chain >= 0.5)})
    return m


class TestDecisionsReadVoid(unittest.TestCase):
    def test_a_candidate_failing_a_control_reads_void_not_failed(self) -> None:
        arms = {"A5": arm(learner(0.4, 0.4, C0a_SAME=True)), "F": arm(learner(0.9, 0.8))}
        d = R._decisions(arms, {"d1_pp": 5.0})
        self.assertEqual(d["selection"]["candidates"]["A5"], "VOID")
        self.assertIs(d["selection"]["candidates"]["F"], True)

    def test_d1_does_not_read_a_void_arm(self) -> None:
        arms = {"A5": arm(learner(0.4, 0.4, C0a_SAME=True)), "F": arm(learner(0.9, 0.8))}
        d1 = R._decisions(arms, {"d1_pp": 5.0})["d1_i"]
        self.assertFalse(d1["computable"])
        self.assertIn("A5", d1.get("void", {}))
        self.assertNotIn("verdict_this_seed", d1)

    def test_d1_reads_two_arms_whose_controls_pass(self) -> None:
        """Negative control: with every control passing, D1 (i) is computed as before."""
        arms = {"A5": arm(learner(0.4, 0.4)), "F": arm(learner(0.9, 0.8))}
        d1 = R._decisions(arms, {"d1_pp": 5.0})["d1_i"]
        self.assertTrue(d1["computable"])
        self.assertEqual(d1["verdict_this_seed"], "STAYS")

    def test_seed_1s_committed_candidates_read_void(self) -> None:
        """A5, E′ and F each fail (0a′) SAME on seed 20261001's committed record (0.3 · 0.15 · 0.2)."""
        rec = json.loads(SEED1.read_text())
        arms = {n: arm(a["marks"]) for n, a in rec["arms"].items()}
        cand = R._decisions(arms, {})["selection"]["candidates"]
        for a in ("A5", "E′", "F"):
            self.assertEqual(cand[a], "VOID", a)


class TestArmStatus(unittest.TestCase):
    def test_a_failed_control_voids_a_learner(self) -> None:
        s = R.arm_status("A5", learner(0.4, 0.4, C0a_SAME=True))
        self.assertTrue(s["void"])
        self.assertEqual(s["by"], ["C0a_SAME"])

    def test_a_control_not_graded_never_voids(self) -> None:
        m = learner(0.4, 0.4)
        m["C0a_CONST"] = ctl("C0a_CONST", None, graded=False, reason="NO_SLEEP_BEFORE_SITTING")
        self.assertFalse(R.arm_status("D", m)["void"])

    def test_keys_canary_is_exempt_by_construction(self) -> None:
        s = R.arm_status("KEY", controls(C0d_CANARY=True))
        self.assertFalse(s["void"])
        self.assertIn("C0d_CANARY", s["exempt"])

    def test_shifted_key_is_exempt_from_every_control(self) -> None:
        self.assertFalse(R.arm_status("SHIFTED-KEY", controls(C0a_CONST=True, C0a_SAME=True, C0e_FROZEN=True))["void"])

    def test_shuffled_relation_twin_exempt_only_where_its_transform_rewrites(self) -> None:
        self.assertFalse(R.arm_status("SHUFFLED-RELATION:A5", controls(C0a_CONST=True, C0a_SAME=True))["void"])
        s = R.arm_status("SHUFFLED-RELATION:A5", controls(C0a_CONST=True, C0e_FROZEN=True))
        self.assertTrue(s["void"])
        self.assertEqual(s["by"], ["C0e_FROZEN"])

    def test_shuffled_name_twin_exempt_only_from_const(self) -> None:
        self.assertFalse(R.arm_status("SHUFFLED-NAME:A5", controls(C0a_CONST=True))["void"])
        self.assertEqual(R.arm_status("SHUFFLED-NAME:A5", controls(C0a_SAME=True))["by"], ["C0a_SAME"])

    def test_a_forced_twin_is_judged_like_its_base(self) -> None:
        self.assertTrue(R.arm_status("FORCED:A5", controls(C0a_SAME=True))["void"])


class TestVoidPartitionAndTwinBands(unittest.TestCase):
    def test_a_void_arm_fails_nothing_and_keeps_its_readings(self) -> None:
        m = learner(0.4, 0.4, C0a_SAME=True)
        p = R.read_partition("A5", m)
        self.assertEqual(p["failed"], [])
        self.assertTrue(p["void"])
        self.assertEqual(p["void_by"], ["C0a_SAME"])
        self.assertEqual(sorted(p["failed_if_read"]), sorted(G.partition(m)["failed"]))

    def test_an_exempt_control_is_not_a_failure(self) -> None:
        p = R.read_partition("KEY", controls(C0d_CANARY=True))
        self.assertEqual(p["failed"], [])
        self.assertFalse(p["void"])
        self.assertIn("C0d_CANARY", p["exempt"])

    def test_a_read_arm_partitions_as_before(self) -> None:
        m = learner(0.4, 0.9)
        p = R.read_partition("A5", m)
        self.assertFalse(p["void"])
        self.assertEqual(p["failed"], G.partition(m)["failed"])

    def test_a_void_twin_supplies_no_null(self) -> None:
        m = learner(0.9, 0.8)
        out = R.without_void_twin(m, ["C0e_FROZEN"])
        for k in ("U3_TWO_AFTER@T_L", "U3_CHAIN@T_L"):
            self.assertFalse(out[k]["graded"], k)
            self.assertEqual(out[k]["reason_code"], "TWIN_VOID", k)
            self.assertEqual(out[k]["reading"], m[k]["reading"], k)
        self.assertTrue(out["C0a_CONST"]["graded"])

    def test_the_verdict_names_void_and_never_failed(self) -> None:
        m = learner(0.4, 0.4, C0a_SAME=True)
        res = {"seed": 1, "tape_sha": "0" * 64, "smoke": False, "bars_line": "x",
               "instrument": {"void": False, "key_present": True, "shifted_key_present": True, "key_graded_marks": 1,
                              "key_failed": [], "shifted_key_failed": ["U1"]},
               "arms": {"A5": {"marks": m, "partition": R.read_partition("A5", m), "cost": None, "size": None}},
               "decisions": R._decisions({"A5": {"marks": m, "partition": R.read_partition("A5", m)}}, {})}
        text = R.render_verdict(res)
        sec = text.split("## A5", 1)[1].split("\n## ", 1)[0]
        self.assertIn("VOID", sec)
        self.assertIn("C0a_SAME", sec)
        self.assertNotIn("failed ['", sec)


class TestMissingRelationTwin(unittest.TestCase):
    """edit: Claude (Opus 5.5), 2026-09-27 11:40 +0400 — R44. §4 feeds SHUFFLED-RELATION to A1, A5, E′ and F (the composition null for
    U3), and §5 grades U3 as «≥ its bar AND above SHUFFLED-RELATION's 95 % band». `graders.grade_u3_family` passes a mark on
    the bar alone when the band is None, and `assemble` voided a twin only for a failed control (R40): a twin that left NO
    record (stopped VOID by cost under R43, or never run) handed its arm a U3 pass without its null. These pin the reading
    of such a gap: NOT GRADABLE, named — by cost when the stop's marker is on the twin or on the search it loads (E′ and F
    run no search: their twins load SHUFFLED-RELATION:D's library, R36), missing otherwise."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="b1-r44-")
        self.run = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _stop_d_twin(self) -> None:
        d = self.run / "SHUFFLED-RELATION_D"
        d.mkdir()
        (d / R.VOID_BY_COST).write_text(json.dumps({"why": "planted: the lower bound passed 4.32 in sleep 9 (R43)"}) + "\n")

    def test_e_prime_and_f_read_void_by_cost_from_the_search_they_load(self) -> None:
        self._stop_d_twin()
        gaps = R.missing_relation_twins(self.run, ["D", "E′", "F", "A1", "SHUFFLED-RELATION:A1", "A5", "SHUFFLED-RELATION:A5"])
        self.assertEqual(sorted(gaps), ["E′", "F"])
        for b in ("E′", "F"):
            self.assertEqual(gaps[b]["reason_code"], "TWIN_VOID", b)
            self.assertTrue(gaps[b]["by"] and gaps[b]["by"][0].startswith("VOID_BY_COST"), gaps[b])
            self.assertIn("SHUFFLED-RELATION:D", gaps[b]["by"][0])
            self.assertIn("planted", gaps[b]["by"][0])

    def test_a_twin_that_left_no_record_and_no_marker_reads_missing(self) -> None:
        gaps = R.missing_relation_twins(self.run, ["E′", "A5"])
        self.assertEqual(sorted(gaps), ["A5", "E′"])
        for b in ("A5", "E′"):
            self.assertEqual(gaps[b]["reason_code"], "TWIN_MISSING", b)
            self.assertEqual(gaps[b]["by"], [f"MISSING: no SHUFFLED-RELATION:{b} record"], b)

    def test_a5s_twin_is_its_own_search_not_ds(self) -> None:
        self._stop_d_twin()
        self.assertEqual(R.missing_relation_twins(self.run, ["A5"])["A5"]["reason_code"], "TWIN_MISSING")

    def test_the_arms_4_does_not_twin_are_never_a_gap(self) -> None:
        self._stop_d_twin()
        self.assertEqual(R.missing_relation_twins(self.run, ["D", "A0", "A2", "A3", "A4", "A1-FIXED", "A1-MA", "KEY", "RING-READ"]), {})

    def test_a_present_twin_is_no_gap(self) -> None:
        """The positive control: a twin record present is read as before (its band, or R40's control VOID)."""
        self._stop_d_twin()
        names = ["A1", "SHUFFLED-RELATION:A1", "A5", "SHUFFLED-RELATION:A5", "E′", "SHUFFLED-RELATION:E′", "F", "SHUFFLED-RELATION:F"]
        self.assertEqual(R.missing_relation_twins(self.run, names), {})

    def test_the_gap_reads_through_without_void_twin_with_its_own_reason(self) -> None:
        m = learner(0.9, 0.8)
        out = R.without_void_twin(m, ["MISSING: no SHUFFLED-RELATION:E′ record"], reason_code="TWIN_MISSING")
        for k in ("U3_TWO_AFTER@T_L", "U3_CHAIN@T_L"):
            self.assertFalse(out[k]["graded"], k)
            self.assertEqual(out[k]["reason_code"], "TWIN_MISSING", k)
            self.assertEqual(out[k]["fields"]["twin_void_by"], ["MISSING: no SHUFFLED-RELATION:E′ record"], k)
        self.assertEqual(R.without_void_twin(m, ["C0e_FROZEN"])["U3_CHAIN@T_L"]["reason_code"], "TWIN_VOID")   # R40's default stands

    def test_the_verdict_names_the_null_that_is_gone(self) -> None:
        m = R.without_void_twin(learner(0.9, 0.8), ["MISSING: no SHUFFLED-RELATION:E′ record"], reason_code="TWIN_MISSING")
        res = {"seed": 1, "tape_sha": "0" * 64, "smoke": False, "bars_line": "x",
               "instrument": {"void": False, "key_present": True, "shifted_key_present": True, "key_graded_marks": 1,
                              "key_failed": [], "shifted_key_failed": ["U1"]},
               "arms": {"E′": {"marks": m, "partition": R.read_partition("E′", m), "cost": None, "size": None}},
               "twin_void": {"E′": ["MISSING: no SHUFFLED-RELATION:E′ record"]},
               "decisions": R._decisions({"E′": {"marks": m, "partition": R.read_partition("E′", m)}}, {})}
        text = R.render_verdict(res)
        self.assertIn("MISSING: no SHUFFLED-RELATION:E′ record", text.split("## E′", 1)[0])
        self.assertIn("TWIN_MISSING", text)


if __name__ == "__main__":
    unittest.main()
