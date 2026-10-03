# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 12:04 +0400 — PREREG-ACT-EFFECT RESULT renderer (tools/toys/act_effect_result.py): every figure of the RESULT document is read from the bench's JSON files by script
# (#242: a number written from memory), and each SHORTFALL is classed against the iid and the empirical (block-bootstrap) ceilings by a rule fixed here, before any graded number existed:
#   a mark that PASSES is «passes»; a miss with the EMPIRICAL ceiling below the bar = «bar above its empirical ceiling» (the law's iid arithmetic); a miss within 2 binomial SE of the empirical ceiling
#   = «inside the empirical ceiling's reach»; a miss below that = «BELOW the empirical ceiling» (mechanism: the hard screen's feedback trap).
from __future__ import annotations

import unittest

from tests.creature import test_act_effect_verdict as tv
from tools.toys import act_effect_result as R
from tools.toys import act_effect_verdict as V


class TestClassify(unittest.TestCase):
    def test_a_pass_is_a_pass(self) -> None:
        self.assertEqual(R.classify(0.97, 0.95, iid=1.0, emp=0.97, n=50), "passes")

    def test_a_bar_above_the_empirical_ceiling_is_the_laws_arithmetic(self) -> None:
        self.assertIn("bar above its empirical ceiling", R.classify(0.70, 0.95, iid=0.99, emp=0.80, n=50))

    def test_a_miss_inside_two_se_of_the_empirical_ceiling_is_noise(self) -> None:
        # emp 0.97 >= bar 0.95; measured 0.92 on 50 lives: SE = sqrt(.92*.08/50) = 0.038 -> 0.92 >= 0.97 - 0.076
        self.assertIn("inside the empirical ceiling's reach", R.classify(0.92, 0.95, iid=1.0, emp=0.97, n=50))

    def test_a_miss_far_below_the_empirical_ceiling_is_the_mechanism(self) -> None:
        c = R.classify(0.50, 0.95, iid=1.0, emp=0.97, n=50)
        self.assertIn("BELOW the empirical ceiling", c)
        self.assertNotIn("bar above its empirical ceiling", c)

    def test_both_facts_are_reported_when_both_hold(self) -> None:
        c = R.classify(0.30, 0.90, iid=1.0, emp=0.70, n=50)
        self.assertIn("bar above its empirical ceiling", c)
        self.assertIn("BELOW the empirical ceiling", c)

    def test_the_gap_is_named(self) -> None:
        # iid 1.00, empirical 0.80: a measured 0.78 against a bar 0.95 is inside the iid-to-empirical gap's arithmetic
        self.assertIn("bar above its empirical ceiling", R.classify(0.78, 0.95, iid=1.0, emp=0.80, n=50))


class TestRender(unittest.TestCase):
    def _inputs(self):
        sq, b, b2, lv, eq = tv.statusquo(), tv.bench(), tv.bench(), tv.lives(), {"pass": True, "steps": 20000, "mismatches": 0}
        verdict = V.verdict(sq, b, b2, lv, eq, True)
        ceil = {"rows": [
            {"kind": "iid at forward 0.568", "forward_dead_time": 0.0006, "m2_pass_960": 1.0, "m2_pass_4920": 1.0, "m3_pass": 1.0, "m4a_pass": 1.0, "m4b_pass": 1.0, "m4b_median": 0.999, "forward_share": 0.31, "noop_share": 0.06},
            {"kind": "block bootstrap, block 100 (forward + no-ops from the recorded series)", "forward_dead_time": 0.09, "m2_pass_960": 0.9, "m2_pass_4920": 0.7, "m3_pass": 1.0, "m4a_pass": 1.0, "m4b_pass": 0.6, "m4b_median": 0.93, "forward_share": 0.29, "noop_share": 0.06}],
            "lives": 600, "acts": 4920}
        return verdict, b, lv, ceil

    def test_every_graded_mark_and_every_ceiling_appears(self) -> None:
        verdict, b, lv, ceil = self._inputs()
        md = R.render(verdict, b, lv, ceil, transfer=None, oracle=None, equiv={"pass": True, "steps": 20000, "mismatches": 0})
        for token in ("M1", "M2", "M3", "M4", "M5", "M7", "M8", "R-NULL", "R-3", "R-SCR", "C-SCR", "iid", "empirical", "ADMIT"):
            self.assertIn(token, md)

    def test_the_figures_in_the_text_are_the_files_figures(self) -> None:
        verdict, b, lv, ceil = self._inputs()
        md = R.render(verdict, b, lv, ceil, transfer=None, oracle=None, equiv={"pass": True, "steps": 20000, "mismatches": 0})
        self.assertIn(f"{verdict['readings']['c_scr_mean']:.4f}", md)
        self.assertIn(f"{verdict['readings']['null_mean']:.4f}", md)
        self.assertIn(f"{verdict['readings']['r3_mean']:.4f}", md)

    def test_a_shortfall_row_carries_both_facts_when_both_hold(self) -> None:
        """Measured 0.30 on 50 lives against the bar 0.90 and an empirical ceiling of 0.70: the bar sits above the ceiling (arithmetic) AND the reading is below it (mechanism)."""
        verdict, b, lv, ceil = self._inputs()
        lv["arms"]["C-SCR"]["summary"]["h4920"]["lock_pass_share"] = 0.30
        verdict = V.verdict(tv.statusquo(), tv.bench(), tv.bench(), lv, {"pass": True, "steps": 20000, "mismatches": 0}, True)
        md = R.render(verdict, b, lv, ceil, transfer=None, oracle=None, equiv={"pass": True, "steps": 20000, "mismatches": 0})
        self.assertIn("bar above its empirical ceiling", md)
        self.assertIn("BELOW the empirical ceiling", md)

    def test_a_shortfall_that_only_the_arithmetic_explains(self) -> None:
        verdict, b, lv, ceil = self._inputs()
        lv["arms"]["C-SCR"]["summary"]["h4920"]["lock_pass_share"] = 0.68
        verdict = V.verdict(tv.statusquo(), tv.bench(), tv.bench(), lv, {"pass": True, "steps": 20000, "mismatches": 0}, True)
        md = R.render(verdict, b, lv, ceil, transfer=None, oracle=None, equiv={"pass": True, "steps": 20000, "mismatches": 0})
        row = [l for l in md.splitlines() if l.startswith("| M2 (4920")][0]
        self.assertIn("bar above its empirical ceiling", row)
        self.assertNotIn("BELOW the empirical ceiling", row)


if __name__ == "__main__":
    unittest.main()
