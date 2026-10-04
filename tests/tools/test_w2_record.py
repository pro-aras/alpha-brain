"""PREREG-W2 (SIGNED x3) — the record readers' and the offline state constructor's tests, written FIRST (red), read on
brain-long-2's COPIED record (scratch/bl2 — RULES §7; never the life root).

# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:22 +0400 — new file for the W2 build; law §3 items 2-4.

  The assembly: scene canvases in order (0..299 here), each with its moment, seq, scene index, the parent's words in
  tape order, fix cells, hyps, the turn and learn rows, the truth spec and the store's real X rows. The truth specs
  regenerate from (world_seed, scene) to the files' own content (G-TRUTH's form). The reference census equals the saved
  census at 250 and 500 with presence counts (G-CENSUS). The DOUBT label reads the journal's own per-hyp `held` list and
  a reference learner re-driven over the pure stream AGREES at sampled canvases (G-STATE's two-way form). The state
  coordinates are the declared six (doubt, young, ask_prev, say_prev, cnt, fit).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from tools.toys.w2 import census as C
from tools.toys.w2 import record as R
from tools.toys.w2 import state as ST

BL2 = Path("scratch/bl2")
N = 300


class TestAssembly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canvases = R.assemble(BL2, 0, N)

    def test_three_hundred_canvases_in_order(self):
        cs = self.canvases
        self.assertEqual(len(cs), N)
        self.assertEqual([c.order for c in cs], list(range(N)))
        for i, c in enumerate(cs):
            self.assertEqual(c.scene, i)
            self.assertEqual(c.moment, f"sc20261101t{i:06d}")
            self.assertTrue(c.words)
            self.assertTrue(c.fix)
            self.assertTrue(c.hyps)
            X = c.X
            self.assertEqual(X.ndim, 2)
            self.assertEqual(X.shape[1], 146)
            self.assertGreaterEqual(X.shape[0], 1)

    def test_the_parents_words_match_the_truth_specs_said(self):
        for c in self.canvases[::37]:
            self.assertEqual(list(c.words), list(c.spec["said"]))
            self.assertEqual(list(c.words), list(c.spec["scene_dict"]["words"]))

    def test_the_truth_specs_regenerate(self):
        for c in self.canvases[::37]:
            regen = R.regenerate_spec(c.spec["world_seed"], c.scene)
            self.assertEqual(regen["scene_dict"], c.spec["scene_dict"])

    def test_the_reference_census_equals_the_saved_census_at_250_and_500(self):
        cs500 = R.assemble(BL2, 0, 500)
        lists = [c.words for c in cs500]
        for point in (250, 500):
            saved = json.loads((BL2 / "census" / f"{point:08d}.json").read_text())
            out = C.compare_saved(lists, saved, at=point)
            self.assertTrue(out["ok"], out)
            self.assertGreater(out["n_words"], 0)
            self.assertEqual(out["n_checked"], out["n_words"])


class TestStates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canvases = R.assemble(BL2, 0, N)
        cls.census = C.meeting_counts([c.words for c in cls.canvases])

    def test_doubt_two_ways_agree_at_sampled_canvases(self):
        held_j, held_ref = ST.held_two_ways(self.canvases, self.census, every=25)
        self.assertEqual(len(held_j), len(held_ref))
        self.assertGreater(len(held_j), 0)
        self.assertEqual(held_j, held_ref)                                  # G-STATE: n of n sampled

    def test_the_state_coordinates(self):
        for c in self.canvases[::37]:
            s = ST.state_of(self.canvases, self.census, c.order)
            self.assertEqual(len(s), 6)
            self.assertIn(s[0], (0.0, 1.0))
            self.assertIn(s[1], (0.0, 1.0))
            self.assertIn(s[2], (0.0, 1.0))
            self.assertIn(s[3], (0.0, 1.0))
            self.assertGreaterEqual(s[4], 0.0)

    def test_ask_prev_and_say_prev_read_the_previous_canvas(self):
        s1 = ST.state_of(self.canvases, self.census, 251)
        ask_prev_expected = 1.0 if (self.canvases[250].turn.get("ask") is not None) else 0.0
        say_prev_expected = 1.0 if (self.canvases[250].turn.get("say") is not None) else 0.0
        self.assertEqual(s1[2], ask_prev_expected)
        self.assertEqual(s1[3], say_prev_expected)


if __name__ == "__main__":
    unittest.main()
