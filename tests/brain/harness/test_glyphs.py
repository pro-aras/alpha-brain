# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:4x +0400 — tests for brain/world/glyphs.py and
# brain/world/canvas.py's glyph_box (reads the REAL library, read-only).
from __future__ import annotations

import unittest

import numpy as np

from brain.world import fonts
from brain.world.canvas import CANVAS, THING_SIDE, glyph_box, render_glyph_canvas
from brain.world.glyphs import NEVER_TAUGHT_SCRIPTS, GlyphLibrary, GlyphsError


class TestGlyphLibrary(unittest.TestCase):
    def test_loads_latin_upper_and_reads_a_teach_font(self) -> None:
        lib = GlyphLibrary("latin-upper")
        teach_font = fonts.TEACH_FONTS_ORDER[0]
        self.assertTrue(lib.has("A", teach_font))
        crop = lib.get("A", teach_font)
        h = lib.line_box_height(teach_font)
        self.assertEqual(crop.shape[0], h)
        self.assertLessEqual(crop.shape[1], h)   # §2.1: never wider than tall
        self.assertTrue(0.0 <= crop.min() and crop.max() <= 1.0)

    def test_unknown_script_raises(self) -> None:
        with self.assertRaises(GlyphsError):
            GlyphLibrary("klingon")

    def test_missing_char_font_pair_raises(self) -> None:
        lib = GlyphLibrary("digits")
        with self.assertRaises(GlyphsError):
            lib.get("Q", fonts.TEACH_FONTS_ORDER[0])   # digits script has no letters

    def test_every_teach_font_has_every_letter_and_digit(self) -> None:
        """The 4 TEACH fonts must actually carry every character B1 needs to teach from them — a gap here
        would silently shrink phase L1/L2/D's own 12-round schedule (§2.7)."""
        for script, chars in (("latin-upper", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                               ("latin-lower", "abcdefghijklmnopqrstuvwxyz"),
                               ("digits", "0123456789")):
            lib = GlyphLibrary(script)
            for font in fonts.TEACH_FONTS_ORDER:
                missing = [c for c in chars if not lib.has(c, font)]
                self.assertEqual(missing, [], f"{script}/{font} is missing {missing}")


class TestNeverTaughtScripts(unittest.TestCase):
    def test_all_four_load_and_have_base32_rows(self) -> None:
        for script in NEVER_TAUGHT_SCRIPTS:
            lib = GlyphLibrary(script)
            self.assertGreater(len(lib._by_key), 0, script)

    def test_font_counts_match_prereg_section_3_3(self) -> None:
        expected = {"hebrew": 20, "arabic": 12, "devanagari": 4, "greek": 60}
        for script, n in expected.items():
            lib = GlyphLibrary(script)
            self.assertEqual(len(lib._heights), n, script)

    def test_a_greek_glyph_boxes_like_a_latin_one(self) -> None:
        lib = GlyphLibrary("greek")
        any_font = next(iter(lib._heights))
        any_char = next(c for (c, f) in lib._by_key if f == any_font)
        box = glyph_box(lib, any_char, any_font)
        self.assertEqual(box.shape, (THING_SIDE, THING_SIDE))


class TestGlyphBoxAndCanvas(unittest.TestCase):
    def test_glyph_box_shape_and_range(self) -> None:
        lib = GlyphLibrary("latin-upper")
        box = glyph_box(lib, "A", fonts.TEACH_FONTS_ORDER[0])
        self.assertEqual(box.shape, (THING_SIDE, THING_SIDE))
        self.assertTrue(0.0 <= box.min() and box.max() <= 1.0)
        self.assertGreater(box.max(), 0.0, "an all-black glyph box means the paste/scale lost the ink")

    def test_narrow_glyph_is_horizontally_centred(self) -> None:
        """"I" is narrow; its scaled box should have zero ink at the far left and right columns and some
        ink nearer the centre column (a loose but real check that centring, not left-alignment, happened)."""
        lib = GlyphLibrary("latin-upper")
        box = glyph_box(lib, "I", fonts.TEACH_FONTS_ORDER[0])
        col_ink = box.sum(axis=0)
        centre = THING_SIDE // 2
        # the column with the most ink should be within a few columns of centre, not pinned to the edge.
        peak = int(np.argmax(col_ink))
        self.assertLess(abs(peak - centre), THING_SIDE // 4, f"peak ink column {peak} is not near centre {centre}")

    def test_render_glyph_canvas_shape_and_truth(self) -> None:
        lib = GlyphLibrary("latin-upper")
        rng = np.random.default_rng(1)
        rgb, truth = render_glyph_canvas(lib, "A", fonts.TEACH_FONTS_ORDER[0], rng)
        self.assertEqual(rgb.shape, (CANVAS, CANVAS, 3))
        self.assertEqual(rgb.dtype, np.uint8)
        for key in ("top", "left", "centroid", "cell"):
            self.assertIn(key, truth)

    def test_render_glyph_canvas_deterministic_under_same_seed(self) -> None:
        lib = GlyphLibrary("latin-upper")
        rgb1, truth1 = render_glyph_canvas(lib, "B", fonts.TEACH_FONTS_ORDER[1], np.random.default_rng(5))
        rgb2, truth2 = render_glyph_canvas(lib, "B", fonts.TEACH_FONTS_ORDER[1], np.random.default_rng(5))
        np.testing.assert_array_equal(rgb1, rgb2)
        self.assertEqual(truth1, truth2)


if __name__ == "__main__":
    unittest.main()
