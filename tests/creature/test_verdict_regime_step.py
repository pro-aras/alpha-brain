# edit: Claude (Fable 5.1), 2026-09-21 20:54 +0400 — the 8 h seam lives (docs/G5-SEAM-LIFE-PLAN.md §1): the regime null band is
# the 95th percentile of fake-boundary spike ratios sampled every `step` canvases of window 0; a 2 h window 0
# (~1,440 canvases) at step 100 yields ~14 fake boundaries × ~11 continuing things ≈ 150 samples (life 2's closed
# record: 42 boundaries × 11 = 462 over 6 h; the same ~75/h) — enough; `--regime-step` lets a seam life sample more
# densely as a convenience (corrected 2026-09-21 21:03 +0400: the first comment counted boundaries as samples). CONTROL: the closed life 2's record must reproduce its recorded band EXACTLY
# at the default step (null_band_95 1.6644, 462 samples — runs/g4-verdict-life2-20260921-1215/results.json,
# read 2026-09-21 20:5x), and the knob must reach modulation()'s regime dict (the last link, #180).
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools import verdict_g4

LIFE2_RECORD = Path("/data/dev/genome/runs/g4-verdict-life2-20260921-1215")


def _mind_rows_of(record: Path) -> list:
    rows = []
    with open(record / "live-journal.jsonl") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if "moment" in r and r.get("word") and str(r["moment"]).startswith("w") and "err" in r:
                rows.append(r)
    return rows


class TestRegimeStepOnTheClosedRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not (LIFE2_RECORD / "live-journal.jsonl").exists():
            raise unittest.SkipTest("life 2's verdict record is not on this box")
        cls.mind = _mind_rows_of(LIFE2_RECORD)
        cls.recorded = json.loads((LIFE2_RECORD / "results.json").read_text())["marks"]["MODULATION"]["regime"]

    def test_default_step_reproduces_the_recorded_band(self) -> None:
        reg = verdict_g4._regime_calibration(self.mind)
        self.assertEqual(reg["step"], 100)
        self.assertEqual(reg["null_ratio_samples"], self.recorded["null_ratio_samples"])
        self.assertEqual(reg["null_band_95"], self.recorded["null_band_95"])
        self.assertEqual(reg["settle_bar_err_95"], self.recorded["settle_bar_err_95"])

    def test_denser_step_samples_more_and_prints_its_count(self) -> None:
        reg100 = verdict_g4._regime_calibration(self.mind, step=100)
        reg25 = verdict_g4._regime_calibration(self.mind, step=25)
        self.assertEqual(reg25["step"], 25)
        self.assertGreaterEqual(reg25["null_ratio_samples"], 3 * reg100["null_ratio_samples"])
        self.assertIsNotNone(reg25["null_band_95"])
        # the settle bar reads window-0 noise, not the fake boundaries: the step must not move it
        self.assertEqual(reg25["settle_bar_err_95"], reg100["settle_bar_err_95"])
        print(f"[regime-step] life 2: step100 band {reg100['null_band_95']} (n {reg100['null_ratio_samples']}) · "
              f"step25 band {reg25['null_band_95']} (n {reg25['null_ratio_samples']})")


class TestKnobReachesModulation(unittest.TestCase):
    def test_regime_step_threads_into_the_regime_dict(self) -> None:
        mind = [{"seq": i, "moment": f"w0000i{i:06d}t{i:09d}", "word": f"c{i % 5}", "err": 0.02 + (i % 7) * 0.001} for i in range(600)]
        out = verdict_g4.modulation({"mind": mind}, 0.048, regime_step=25)
        self.assertEqual(out["regime"]["step"], 25)
        out100 = verdict_g4.modulation({"mind": mind}, 0.048)
        self.assertEqual(out100["regime"]["step"], 100)


if __name__ == "__main__":
    unittest.main()
