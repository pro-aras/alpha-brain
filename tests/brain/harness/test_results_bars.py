# edit: Claude (Opus 5.5), 2026-09-26 16:57 +0400 — the first graded read of B1 (seed 20261001) died in results.main:
# «AFTER: declared bar 8 is ABOVE its organ ceiling 0.886» — bars.json's U3 bars are COUNTS (k of n, what the grader compares),
# and the validator compares SHARES. These pin the conversion on the SIGNED bars.json and ceilings.json.
from __future__ import annotations

import json
import unittest
from pathlib import Path

from brain.harness import bars as B
from brain.harness.results import u3_bar_shares

ROOT = Path(__file__).resolve().parents[3]
BARS = ROOT / "docs" / "brain" / "b1" / "bars.json"
CEIL = ROOT / "docs" / "brain" / "b1" / "stage-1" / "ceilings.json"


class TestResultsBarsUnits(unittest.TestCase):
    def setUp(self) -> None:
        self.bars_doc = json.loads(BARS.read_text())
        self.families = json.loads(CEIL.read_text()).get("families", {})

    def test_the_signed_bars_validate_as_shares(self) -> None:
        shares = u3_bar_shares(self.bars_doc)
        self.assertEqual(set(shares), set(self.bars_doc["bars"]["U3"]))
        self.assertAlmostEqual(shares["AFTER"], 8 / 12)
        B.validate_bars_line(self.families, shares)   # must not raise

    def test_counts_are_refused_the_old_call(self) -> None:
        """Negative control: the old call (counts handed to a share validator) raises — so the test above can fail."""
        counts = {k: v for k, v in self.bars_doc["bars"]["U3"].items() if isinstance(v, (int, float))}
        with self.assertRaises(B.BarsError):
            B.validate_bars_line(self.families, counts)


if __name__ == "__main__":
    unittest.main()
