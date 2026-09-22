# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 00:54 +0400 — ALPHA4-H task 1: creature/senses/read_common.py,
# test-first (docs/briefs/ALPHA4-H.md task 1).
from __future__ import annotations

import io
import unittest

import numpy as np
from PIL import Image

from creature.senses import read_common


class TestSplitSentences(unittest.TestCase):
    def test_three_sentences_one_line(self) -> None:
        got = read_common.split_sentences("The cat sat. The dog ran! Is it big?")
        self.assertEqual(got, ["The cat sat.", "The dog ran!", "Is it big?"])

    def test_a_sentence_wrapped_across_newlines_is_one_string(self) -> None:
        text = "The cat sat\non the mat\nand slept. Then it woke."
        got = read_common.split_sentences(text)
        self.assertEqual(got, ["The cat sat on the mat and slept.", "Then it woke."])

    def test_empty_and_whitespace_only_text(self) -> None:
        self.assertEqual(read_common.split_sentences(""), [])
        self.assertEqual(read_common.split_sentences("   \n\n  "), [])

    def test_no_terminal_punctuation_is_still_one_sentence(self) -> None:
        self.assertEqual(read_common.split_sentences("no ending here"), ["no ending here"])

    def test_deterministic(self) -> None:
        text = "One. Two. Three."
        self.assertEqual(read_common.split_sentences(text), read_common.split_sentences(text))


class TestWordsOf(unittest.TestCase):
    def test_lowercase_and_strip_punctuation(self) -> None:
        self.assertEqual(read_common.words_of("The Cat, Sat.", max_words=8, letters=8), ["the", "cat", "sat"])

    def test_apostrophes_and_digits_stripped_not_word_breaks(self) -> None:
        self.assertEqual(read_common.words_of("don't 1900s go!", max_words=8, letters=8), ["dont", "s", "go"])

    def test_pure_punctuation_token_dropped(self) -> None:
        self.assertEqual(read_common.words_of("wait -- really ?!", max_words=8, letters=8), ["wait", "really"])

    def test_truncated_to_letters(self) -> None:
        self.assertEqual(read_common.words_of("beautiful", max_words=8, letters=8), ["beautifu"])
        self.assertEqual(len(read_common.words_of("beautiful", max_words=8, letters=8)[0]), 8)

    def test_a_word_that_is_exactly_the_limit_is_not_truncated_short(self) -> None:
        eight = "abcdefgh"
        self.assertEqual(read_common.words_of(eight, max_words=8, letters=8), [eight])

    def test_max_words_caps_the_output(self) -> None:
        import string
        tokens = [string.ascii_lowercase[i] * 2 for i in range(20)]   # aa bb cc ... distinct after cleaning
        got = read_common.words_of(" ".join(tokens), max_words=5, letters=8)
        self.assertEqual(got, tokens[:5])

    def test_max_words_large_returns_every_clean_word(self) -> None:
        import string
        tokens = [string.ascii_lowercase[i] * 2 for i in range(20)]
        got = read_common.words_of(" ".join(tokens), max_words=10 ** 6, letters=8)
        self.assertEqual(len(got), 20)

    def test_empty_sentence(self) -> None:
        self.assertEqual(read_common.words_of("", max_words=8, letters=8), [])

    def test_every_word_fits_the_ear_encoder(self) -> None:
        """A regression control for the crash this truncation exists to prevent: every returned word must
        be encodable by genome.world.encode_word (<= WORD_SLOTS letters, a-z only)."""
        from genome.world import encode_word, WORD_SLOTS
        words = read_common.words_of("supercalifragilisticexpialidocious is not a real word 42", max_words=8, letters=WORD_SLOTS)
        for w in words:
            encode_word(w)   # must not raise


class TestRenderLine(unittest.TestCase):
    def test_shape_and_dtype(self) -> None:
        rgb = read_common.render_line("the cat sat", 128, read_common.DEFAULT_FONT_PATH)
        self.assertEqual(rgb.shape, (128, 128, 3))
        self.assertEqual(rgb.dtype, np.uint8)

    def test_deterministic_same_bytes_twice(self) -> None:
        a = read_common.render_line("a fixed line of text", 128, read_common.DEFAULT_FONT_PATH)
        b = read_common.render_line("a fixed line of text", 128, read_common.DEFAULT_FONT_PATH)
        self.assertTrue(np.array_equal(a, b))
        self.assertEqual(read_common.png_bytes(a), read_common.png_bytes(b))

    def test_white_background_corner_and_some_black_ink(self) -> None:
        rgb = read_common.render_line("hello", 128, read_common.DEFAULT_FONT_PATH)
        self.assertTrue((rgb[0, 0] == [255, 255, 255]).all(), "the corner must be background white")
        self.assertTrue((rgb < 128).any(), "some pixel must carry dark ink")

    def test_different_text_renders_different_bytes(self) -> None:
        a = read_common.render_line("aaaaaaaa", 128, read_common.DEFAULT_FONT_PATH)
        b = read_common.render_line("zzzzzzzz", 128, read_common.DEFAULT_FONT_PATH)
        self.assertFalse(np.array_equal(a, b))

    def test_default_and_heldout_font_render_different_bytes(self) -> None:
        a = read_common.render_line("the cat sat", 128, read_common.DEFAULT_FONT_PATH)
        b = read_common.render_line("the cat sat", 128, read_common.HELDOUT_FONT_PATH)
        self.assertFalse(np.array_equal(a, b), "Sans and Serif must not render pixel-identical glyphs")

    def test_empty_sentence_is_blank_white(self) -> None:
        rgb = read_common.render_line("", 128, read_common.DEFAULT_FONT_PATH)
        self.assertTrue((rgb == 255).all())

    def test_a_long_line_still_fits_the_canvas(self) -> None:
        rgb = read_common.render_line("one two three four five six seven eight", 128, read_common.DEFAULT_FONT_PATH)
        self.assertEqual(rgb.shape, (128, 128, 3))


class TestPngBytes(unittest.TestCase):
    def test_round_trips_through_pil(self) -> None:
        rgb = read_common.render_line("round trip", 128, read_common.DEFAULT_FONT_PATH)
        data = read_common.png_bytes(rgb)
        back = np.asarray(Image.open(io.BytesIO(data)).convert("RGB"), dtype=np.uint8)
        self.assertTrue(np.array_equal(rgb, back))


if __name__ == "__main__":
    unittest.main()
