# edit: Claude (Opus 5.5), 2026-09-26 17:25 +0400 — the graded run of 13:03 ran D at the arm's TOY default (2,000 candidates
# per sleep) because the seat's §12 line named no number and the registry passed none (SEAT-DECISIONS R37). These pin the
# registry's number to the committed derivation (tools/b1/d_budget.py → docs/brain/b1/stage-1/d-budget.json), and pin that
# a twin of D inherits it.
from __future__ import annotations

import json
import unittest
from pathlib import Path

from brain.harness import run as R

ROOT = Path(__file__).resolve().parents[3]
BUDGET = ROOT / "docs" / "brain" / "b1" / "stage-1" / "d-budget.json"


class TestDBudget(unittest.TestCase):
    def test_the_registry_carries_the_derived_number(self) -> None:
        want = json.loads(BUDGET.read_text())["candidates_per_sleep"]
        self.assertEqual(R.spec_for("D").config.get("candidates_per_sleep"), want)

    def test_the_number_is_not_the_toy_default(self) -> None:
        n = R.spec_for("D").config.get("candidates_per_sleep")
        self.assertIsNotNone(n, "D must never run a graded seed at the arm's default")
        self.assertGreater(n, 2000)

    def test_the_twin_search_runs_at_the_same_number(self) -> None:
        self.assertEqual(R.spec_for("SHUFFLED-RELATION:D").config.get("candidates_per_sleep"),
                         R.spec_for("D").config.get("candidates_per_sleep"))

    def test_the_derivation_stays_under_the_allowance(self) -> None:
        b = json.loads(BUDGET.read_text())
        self.assertLessEqual(b["predicted_total_cpu_h"], 24.0)
        self.assertEqual(b["budget_cpu_s"], 24 * 3600)


if __name__ == "__main__":
    unittest.main()
