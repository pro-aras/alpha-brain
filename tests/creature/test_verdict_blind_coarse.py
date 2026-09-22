# edit: Claude (Fable 5.1), 2026-09-22 20:4x +0400 — builder B's clause 9 (docs/briefs/LIFE-B-REPORT.md §6): the reader's twin exam honoured
# no --blind flag, so a `--blind coarse` twin LEARNED on four glances and was ASKED on five («learned without, asked with»). The fix B wrote
# and left to the reader's owner: `_force_no_coarse()` — a gaze.glances monkeypatch (the sibling of `_force_one_glance()`) that asks with the
# four located glances only — and the worker routes a coarse-blind twin's exam through the in-process branch the monkeypatch can reach.
import unittest
from pathlib import Path

import numpy as np

TREE = Path(__file__).resolve().parent.parent.parent


class BlindCoarseExam(unittest.TestCase):
    def test_force_no_coarse_asks_with_four_glances_on_a_coarse_genome(self):
        from genome import gaze as _gaze
        from genome.machinery import parse_genome
        from tools.verdict_g4 import _force_no_coarse
        text = (TREE / "genome" / "G5.genome").read_text().replace("ink border", "ink border coarse 32")
        g = parse_genome(text)
        self.assertEqual(g.gaze.get("coarse"), 32)
        rng = np.random.default_rng(1); rgb = (rng.random((128, 128, 3)) * 255).astype(np.uint8)
        orig = _gaze.glances
        try:
            five = _gaze.glances(rgb, g.retina, g.gaze, "surprise", "pic0")
            self.assertEqual(len(five["feats"]), 5)                    # the coarse genome asks with five
            _force_no_coarse()
            four = _gaze.glances(rgb, g.retina, g.gaze, "surprise", "pic0")
            self.assertEqual(len(four["feats"]), 4)                    # the blind-coarse twin asks with four
            self.assertEqual(len(four["residual"]), 4)
            for a, b in zip(four["feats"], five["feats"][:4]):
                np.testing.assert_array_equal(a, b)                    # the four located glances untouched
        finally:
            _gaze.glances = orig

    def test_worker_routes_a_coarse_blind_twin_through_the_in_process_exam(self):
        import inspect
        from tools import verdict_g4
        src = inspect.getsource(verdict_g4.worker)
        self.assertIn('"coarse" in', src)
        self.assertIn("_force_no_coarse()", src)


if __name__ == "__main__":
    unittest.main()
