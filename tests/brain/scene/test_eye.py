# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:06 +0400 — S1a step 2 (PREREG-R3-TONIGHT §S1a «The eye's segmentation»): the
# union-find thing hypotheses (2 grid cells, Chebyshev, transitive), their unit-mean features and mean positions, the
# cache row's padding, and ORACLE-TRUTH's forced window PINNED to the eye: a forced window at a fixation cell's centre
# reproduces that fixation's glance byte for byte (same interpreter on both sides, so it holds under either).
from __future__ import annotations

import unittest

import numpy as np

from brain.scene import eye
from brain.scene import world as W


class TestGroups(unittest.TestCase):
    def test_chebyshev_two_cells_join_three_do_not(self) -> None:
        self.assertEqual(eye.groups([(0, 0), (2, 2)]), [(0, 1)])
        self.assertEqual(eye.groups([(0, 0), (3, 0)]), [(0,), (1,)])
        self.assertEqual(eye.groups([(0, 0), (0, 3)]), [(0,), (1,)])
        self.assertEqual(eye.groups([(5, 5), (7, 3)]), [(0, 1)])

    def test_union_find_is_transitive(self) -> None:
        self.assertEqual(eye.groups([(0, 0), (2, 0), (4, 0), (10, 10)]), [(0, 1, 2), (3,)])
        self.assertEqual(eye.groups([(9, 9), (0, 0), (4, 0), (2, 0)]), [(0,), (1, 2, 3)])

    def test_mixed(self) -> None:
        self.assertEqual(eye.groups([(0, 0), (2, 2), (5, 5), (0, 3)]), [(0, 1, 3), (2,)])


class TestHypotheses(unittest.TestCase):
    def test_unit_mean_and_mean_position(self) -> None:
        rng = np.random.default_rng(1)
        loc = rng.normal(size=(3, 144))
        loc /= np.linalg.norm(loc, axis=1, keepdims=True)
        h = eye.hypotheses([(1, 1), (2, 2), (9, 9)], loc)
        self.assertEqual([x.members for x in h], [(0, 1), (2,)])
        m = loc[:2].mean(axis=0)
        self.assertTrue(np.allclose(h[0].feat, m / np.linalg.norm(m)))
        self.assertAlmostEqual(float(np.linalg.norm(h[0].feat)), 1.0, places=12)
        self.assertEqual(h[0].pos, (1.5, 1.5))
        self.assertEqual(h[0].count, 2)
        self.assertTrue(np.array_equal(h[1].feat, loc[2] / np.linalg.norm(loc[2])))

    def test_shape_mismatch_refused(self) -> None:
        with self.assertRaises(ValueError):
            eye.hypotheses([(0, 0)], np.zeros((2, 144)))


class TestGlanceRow(unittest.TestCase):
    def test_padding_keeps_coarse_in_row_four(self) -> None:
        f = np.arange(4 * 144, dtype=np.float64).reshape(4, 144)       # 3 located + coarse
        r = eye.glance_row(f, 3)
        self.assertTrue(np.array_equal(r[:3], f[:3]))
        self.assertTrue(np.array_equal(r[3], np.zeros(144)))
        self.assertTrue(np.array_equal(r[4], f[3]))


class TestForcedWindowIsTheEye(unittest.TestCase):
    """The forced road composes the eye's own pieces; at a fixated cell's centre it must BE the eye."""

    def test_forced_at_fixation_centre_equals_the_glance_byte_for_byte(self) -> None:
        spec, gcfg, colour = eye.eye_config()
        checked = 0
        for s in (W.train_scene(20261101, 3), W.train_scene(20261101, 2699), W.test_scene(20261201, 17),
                  W.m2b_scene(20261201, 9)):
            rgb, _c = W.render_scene(s)
            _sha, feats, fix = eye.look(rgb, spec, gcfg, colour)
            self.assertEqual(feats.shape, (len(fix) + 1, 144))
            for k, cell in enumerate(fix):
                c = eye.cell_centre_px(cell, int(gcfg["canvas"]), int(gcfg["grid"]))
                v = eye.forced_glance(rgb, c, spec, gcfg, colour)
                self.assertTrue(np.array_equal(v, feats[k]), (s.item_id, cell))
                checked += 1
        self.assertGreaterEqual(checked, 12)

    def test_forced_window_moves_with_the_centroid(self) -> None:
        spec, gcfg, colour = eye.eye_config()
        s = W.train_scene(20261101, 2699)
        rgb, cents = W.render_scene(s)
        a = eye.forced_glance(rgb, cents[0], spec, gcfg, colour)
        b = eye.forced_glance(rgb, cents[1], spec, gcfg, colour)
        self.assertFalse(np.array_equal(a, b))
        self.assertAlmostEqual(float(np.linalg.norm(a)), 1.0, places=12)
        self.assertEqual(eye.forced_top_left((2.0, 126.0), 128, 128, 32), (0, 96))       # clamped inside the canvas


if __name__ == "__main__":
    unittest.main()
