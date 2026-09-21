# edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:15 +0400 -- copied VERBATIM from branch g5-repairs
# (worktree /data/dev/genome-wt-k, commit 0e9be70); not one byte changed. This branch's own identity test
# against life 3a's tape lives in tests/genome/test_retina_fast_life3a.py, added below.
# edit: Claude (Sonnet 5, builder F), 2026-09-21 17:14 +0400 -- G5-F task 3 (docs/briefs/G5-F-BIND-DIAGNOSTIC-AND-REPAIRS.md
# item 3; EYE.md §0.3 row 2 / gap 9): tests for genome/retina_fast.py, the numpy-vectorised drop-in for
# organs/retina.py's cell_means. Full byte-identity over life 2's 17,768-canvas tape is reported in
# docs/briefs/G5-F-REPORT.md (too slow for a unit test); this file pins byte-identity on fast synthetic
# fixtures plus a NEGATIVE CONTROL proving the identity check can actually catch a real divergence.
from __future__ import annotations

import unittest

import numpy as np

from genome import gaze as ggaze
from genome import retina_fast as rfast
from genome import world


def _frame_from_rng(rng: np.random.Generator, w: int = 128, h: int = 128) -> dict:
    rgb = rng.integers(0, 256, size=(h, w, 3), dtype=np.uint8)
    return ggaze.frame_of(rgb)


class TestRetinaFastIdentity(unittest.TestCase):
    def setUp(self) -> None:
        self.gaze_mod, self.oracle = ggaze.organs()
        self.assertIs(rfast.oracle(), self.oracle, "retina_fast must resolve to the SAME pinned oracle module")

    def test_random_frames_byte_identical(self) -> None:
        rng = np.random.default_rng(20260921)
        for i in range(20):
            frame = _frame_from_rng(rng)
            an_old = self.oracle.analyse(frame)
            an_fast = rfast.analyse_fast(frame)
            self.assertTrue(np.array_equal(np.asarray(an_old["saliency"]), np.asarray(an_fast["saliency"])), f"saliency mismatch on random frame {i}")
            for ch in self.oracle.CHANNELS:
                self.assertTrue(np.array_equal(np.asarray(an_old["channels"][ch]), np.asarray(an_fast["channels"][ch])), f"channel {ch} mismatch on random frame {i}")

    def test_rendered_things_byte_identical_and_fixations_match(self) -> None:
        rng = np.random.default_rng(1)
        for thing in world.THINGS_11:
            rgb, truth = world.render_canvas(thing, rng)
            frame = ggaze.frame_of(rgb)
            an_old = self.oracle.analyse(frame)
            an_fast = rfast.analyse_fast(frame)
            self.assertTrue(np.array_equal(np.asarray(an_old["saliency"]), np.asarray(an_fast["saliency"])), f"saliency mismatch on {thing}")
            fx_old = [(int(z["y"]), int(z["x"])) for z in self.gaze_mod.gaze_sequence(an_old, max_fixations=4, predicted=None)]
            fx_fast = [(int(z["y"]), int(z["x"])) for z in self.gaze_mod.gaze_sequence(an_fast, max_fixations=4, predicted=None)]
            self.assertEqual(fx_old, fx_fast, f"fixation mismatch on {thing}")

    def test_non_uniform_grid_mapping(self) -> None:
        """A frame whose w/h are not exact multiples of grid=16 (the general non-uniform cy/cx mapping,
        organs/retina.py's own `min(grid-1, y*grid//h)` rule) -- life 2's canvases are always 128x128
        (an exact multiple), so this is the generality claim, checked directly."""
        rng = np.random.default_rng(7)
        rgb = rng.integers(0, 256, size=(37, 53, 3), dtype=np.uint8)   # deliberately NOT a multiple of 16
        frame = {"w": 53, "h": 37, "pix": np.ascontiguousarray(rgb).tobytes()}
        an_old = self.oracle.analyse(frame)
        an_fast = rfast.analyse_fast(frame)
        self.assertTrue(np.array_equal(np.asarray(an_old["saliency"]), np.asarray(an_fast["saliency"])))

    def test_negative_control_catches_a_real_divergence(self) -> None:
        """The identity check itself must be able to FAIL: a one-bit corruption in the fast path's
        output must not compare equal to the oracle's. Proves the assertIs/array_equal checks above are
        not vacuously true."""
        rng = np.random.default_rng(3)
        frame = _frame_from_rng(rng)
        an_old = self.oracle.analyse(frame)
        an_fast = rfast.analyse_fast(frame)
        corrupted = np.asarray(an_fast["saliency"], dtype=np.float64).copy()
        corrupted[0, 0] += 1e-9   # a real, tiny divergence -- np.array_equal (bit-exact) must catch it
        self.assertFalse(np.array_equal(np.asarray(an_old["saliency"]), corrupted), "the negative control was not planted correctly")


if __name__ == "__main__":
    unittest.main()
