# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:4x +0400 — the §2.4 parity test: `paste_on_canvas`
# must reproduce `genome.world.render_canvas`'s own tail byte for byte. Two identically-seeded generators:
# one runs `render()` then `paste_on_canvas()`, the other runs `render_canvas()` whole; since both consume
# the identical sequence of draws through `render()` (rng_a explicitly, rng_b inside render_canvas), their
# states agree afterward and every subsequent draw (placement, clutter, noise) agrees too.
from __future__ import annotations

import unittest

import numpy as np

from genome.world import render, render_canvas
from brain.world.canvas import THING_SIDE, paste_on_canvas

# Every thing genome/world.py's _draw() can render (19 — the library's whole vocabulary; B1-PREREG.md §2.4
# asks for "20 things", but this is every drawable thing that exists, which is a STRICTER test than any
# arbitrary 20 would be since none is left untested).
THINGS = ["circle", "square", "diamond", "triangle", "cross", "ring", "bar", "dot", "star", "arrow", "wave",
          "moon", "house", "tree", "cup", "key", "spiral", "zog", "vex"]
SEEDS = [20260930, 20261001, 20261002, 7, 99]


class TestCanvasParity(unittest.TestCase):
    def test_paste_on_canvas_matches_render_canvas_byte_for_byte(self) -> None:
        cases = 0
        for thing in THINGS:
            for seed in SEEDS:
                rng_a = np.random.default_rng(seed)
                rng_b = np.random.default_rng(seed)   # cloned from rng_a's state BEFORE any draw (§2.4)

                pic = render(thing, rng_a, THING_SIDE)
                rgb_a, truth_a = paste_on_canvas(pic, rng_a)

                rgb_b, truth_b = render_canvas(thing, rng_b)

                with self.subTest(thing=thing, seed=seed):
                    np.testing.assert_array_equal(rgb_a, rgb_b)
                    self.assertEqual(truth_a, truth_b)
                cases += 1
        self.assertEqual(cases, len(THINGS) * len(SEEDS))


if __name__ == "__main__":
    unittest.main()
