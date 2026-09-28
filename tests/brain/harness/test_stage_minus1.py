# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 19:1x +0400 — smoke-scale integration test for
# brain/harness/stage_minus1.py: real glyphs, real organs, a TINY subset (--smoke). The FULL-scale run
# (real TEACH/TEST font lists, all three scripts, perceptual + never-taught) is NOT run in this suite — the
# box's load this session (18-20) is above the PREREG's own load<8-or-after-21:00 cadence rule (§9); see
# docs/briefs/B1-BUILDER2-REPORT.md for the command to launch it later. Must run under /usr/bin/python3.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brain.harness.stage_minus1 import StageMinus1Error, run

SEED = 20261001


class TestStageMinus1Smoke(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.out_dir = Path(self._tmp.name) / "out"
        self.cache_dir = Path(self._tmp.name) / "cache"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_smoke_run_end_to_end(self) -> None:
        report = run(SEED, smoke=True, out_dir=self.out_dir, cache_dir=self.cache_dir)
        self.assertTrue(report["controls"]["pass"])
        self.assertIn("latin-upper", report["naming_raw"])
        self.assertIn("latin-lower", report["naming_raw"])
        self.assertIn("digits", report["naming_raw"])
        for k in ("NAMING_latin-upper_4fonts", "NAMING_latin-lower_4fonts", "NAMING_digits_4fonts"):
            self.assertIn(k, report["families"])
            self.assertIn("organ_ceiling", report["families"][k])
        for k in ("AFTER", "BEFORE", "TWO_AFTER", "BETWEEN", "CHAIN", "OTHER_CASE", "TRANSFER_AFTER", "TRANSFER_BEFORE"):
            self.assertIn(k, report["families"])
            ceiling = report["families"][k]["organ_ceiling"]["max"]
            self.assertGreaterEqual(ceiling, 0.0)
            self.assertLessEqual(ceiling, 1.0)
        self.assertIn("note_skipped_in_smoke", report)

    def test_full_scale_refuses_under_high_load_without_force(self) -> None:
        # This box's own load is well above 8 while this session runs; a direct call with smoke=False and
        # no force must refuse rather than spend the full ~1,900-rendering budget beside the graders.
        import os
        if os.getloadavg()[0] < 8:
            self.skipTest("load happens to be under 8 right now; the refusal path cannot be exercised")
        with self.assertRaises(StageMinus1Error):
            run(SEED, smoke=False, out_dir=self.out_dir, cache_dir=self.cache_dir, force=False)


if __name__ == "__main__":
    unittest.main()
