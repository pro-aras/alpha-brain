# edit: Claude (Fable 5.1), 2026-09-22 12:0x +0400 — reader v3.1, from the first 8 h reads of the ladder (L1, L2, L3, g5-seam-1; PREREG §18
# addendum 4): (1) MODULATION graded a window whose only NEW thing was the PLANT — shown 5 times by design — on «settled by the 10th
# showing» it can never reach (#228 (b): a bar above its ceiling read as FAIL on every rung); a window is graded over the new things
# with ≥ 10 showings, and a window with none is reported NOT GRADABLE, never FAIL. (2) (iv) «0 refused» read `births_refused_budget`
# only and PASSED on g5-seam-1 with 1,988 births refused at NMAX (the sight area's 2,000 ids spent by hour ~6; the plant could not be
# learned) — every CAP refusal (budget, nmax, frozen) counts; `redundant` (the ordinary no-birth path) is printed, never a failure.
# (3) W3-2's reason said «VOID by the wiring» when the failing clause was the own-cells share (L1: two circle clusters at .47) — the
# reason names the clause that failed.
from __future__ import annotations

import unittest

from tools import verdict_g4


def _thing(kind="new", n=180, spike=True, settled=True):
    return {"kind": kind, "n_showings": n, "spike": spike, "spike_regime": spike, "settled": settled, "settled_regime": settled}


class TestModulationWindowsGradable(unittest.TestCase):
    def test_a_window_of_five_arrivals_is_graded_by_majority(self) -> None:
        windows = {"1": {"per_thing": {"cup": _thing(settled=False), "house": _thing(settled=False), "key": _thing(), "moon": _thing(), "tree": _thing(),
                                       "arrow": _thing(kind="returning")}}}
        fixed, regime, skipped = verdict_g4.grade_modulation_windows(windows)
        self.assertEqual(skipped, [])
        self.assertEqual(regime, [{"window": "1", "new": 5, "spike": 5, "settled": 3, "pass": True}])

    def test_the_plants_window_is_not_gradable_not_fail(self) -> None:
        windows = {"3": {"per_thing": {"zog": _thing(n=5, settled=False), "cup": _thing(kind="returning")}}}
        fixed, regime, skipped = verdict_g4.grade_modulation_windows(windows)
        self.assertEqual(regime, []); self.assertEqual(fixed, [])
        self.assertEqual(len(skipped), 1); self.assertEqual(skipped[0]["window"], "3")
        self.assertIn("10 showings", skipped[0]["reason"]); self.assertEqual(skipped[0]["new_under_min"], ["zog"])

    def test_a_mixed_window_grades_only_the_things_with_enough_showings(self) -> None:
        windows = {"1": {"per_thing": {"zog": _thing(n=5, settled=False), "key": _thing(), "moon": _thing(settled=False)}}}
        fixed, regime, skipped = verdict_g4.grade_modulation_windows(windows)
        self.assertEqual(skipped, [])
        self.assertEqual(regime, [{"window": "1", "new": 2, "spike": 2, "settled": 1, "pass": False}])

    def test_a_window_with_no_new_thing_is_neither_graded_nor_skipped(self) -> None:
        windows = {"2": {"per_thing": {"arrow": _thing(kind="returning")}}}
        fixed, regime, skipped = verdict_g4.grade_modulation_windows(windows)
        self.assertEqual((fixed, regime, skipped), ([], [], []))


class TestNullFakeBoundaryMajority(unittest.TestCase):
    """§18 addendum 4 (b2): the regime band is the 95th percentile of the fake-boundary ratios; a null that demands ALL eleven
    continuing things under it fails by construction ~43 % of the time (0.95^11 ≈ .57 — L1: ten of eleven under 2.27, «wave» 3.73).
    The null clears when the MAJORITY of continuing things sit under the band (the spike rule's own majority); the share is printed."""
    PER = {"arrow": 1.71, "bar": 0.89, "circle": 1.18, "cross": 1.08, "diamond": 0.33, "dot": 2.14, "ring": 1.55, "square": 0.33, "star": 0.65, "triangle": 1.45, "wave": 3.73}

    def test_ten_of_eleven_under_the_band_clears(self) -> None:
        ok, share = verdict_g4.null_clears(self.PER, 2.27)
        self.assertTrue(ok); self.assertAlmostEqual(share, 10 / 11, places=6)

    def test_a_real_spike_at_the_fake_boundary_fails(self) -> None:
        per = {k: v * 3.0 for k, v in self.PER.items()}   # most things over the band
        ok, share = verdict_g4.null_clears(per, 2.27)
        self.assertFalse(ok); self.assertLess(share, 0.5)

    def test_no_band_or_no_things_is_none(self) -> None:
        self.assertEqual(verdict_g4.null_clears(self.PER, None), (None, None))
        self.assertEqual(verdict_g4.null_clears({}, 2.27), (None, None))


class TestIvRefusals(unittest.TestCase):
    C = {"births_refused_budget": 0, "births_refused_nmax": 1988, "births_refused_frozen": 0, "births_refused_redundant": 4369}

    def test_nmax_refusals_count_as_refused(self) -> None:
        r = verdict_g4.iv_refusals(self.C)
        self.assertEqual(r["caps_total"], 1988); self.assertEqual(r["nmax"], 1988); self.assertEqual(r["redundant"], 4369)

    def test_redundant_alone_is_not_a_refusal_at_a_cap(self) -> None:
        r = verdict_g4.iv_refusals({**self.C, "births_refused_nmax": 0})
        self.assertEqual(r["caps_total"], 0)


class TestW3_2Reason(unittest.TestCase):
    def test_ok_is_empty(self) -> None:
        self.assertEqual(verdict_g4.w3_2_reason(28, 15, []), "")

    def test_reach_under_floor_is_void_by_the_wiring(self) -> None:
        s = verdict_g4.w3_2_reason(21, 1, [])
        self.assertTrue(s.strip().startswith("VOID by the wiring"), s); self.assertIn("1 of 21", s)

    def test_own_cells_clause_is_named_not_void(self) -> None:
        s = verdict_g4.w3_2_reason(28, 15, [{"word": "circle", "own_share": 0.469}, {"word": "circle", "own_share": 0.471}])
        self.assertNotIn("VOID", s); self.assertIn("own", s); self.assertIn("circle", s); self.assertIn("0.469", s)


if __name__ == "__main__":
    unittest.main()
