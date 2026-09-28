# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:2x +0400 — end-to-end smoke test for
# brain/world/build.py: real glyphs, the real pinned tower/gaze, a small request list (fast). Must run
# under /usr/bin/python3 (§3.0).
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from brain.glance_cache import Cache
from brain.world import fonts
from brain.world.build import BuildError, RenderRequest, build_cache, canvas_png_sha256

SEED = 20261001
FONT = fonts.TEACH_FONTS_ORDER[0]


def _small_requests() -> list:
    reqs = []
    for i, char in enumerate("ABCD"):
        reqs.append(RenderRequest(item_id=f"smoke:latin-upper:{char}:{i}", script="latin-upper", char=char, font=FONT))
    for i, char in enumerate("ab"):
        reqs.append(RenderRequest(item_id=f"smoke:latin-lower:{char}:{i}", script="latin-lower", char=char, font=FONT))
    for i, char in enumerate("01"):
        reqs.append(RenderRequest(item_id=f"smoke:digits:{char}:{i}", script="digits", char=char, font=fonts.TEACH_FONTS_ORDER[1]))
    return reqs


class TestBuildCacheSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name) / "cache" / str(SEED)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_builds_a_real_cache_and_self_checks(self) -> None:
        reqs = _small_requests()
        item_to_row, header, truths = build_cache(reqs, self.dir, SEED, recheck_n=10)
        self.assertEqual(len(item_to_row), len(reqs))
        self.assertEqual(header["row_count"], len(reqs))
        self.assertEqual(len(header["organ_pins"]), 4)
        self.assertEqual(set(truths), {r.item_id for r in reqs})

        cache = Cache(self.dir)
        self.assertEqual(len(cache), len(reqs))
        for req in reqs:
            row = item_to_row[req.item_id]
            feats = cache.glances(row)
            self.assertEqual(feats.shape, (5, 144))
            # not all-zero (a real gaze pass over real ink)
            self.assertGreater(float(np.abs(feats).sum()), 0.0)
            meta = cache.meta(row)
            self.assertEqual(meta["char"], req.char)
            self.assertEqual(meta["font"], req.font)

    def test_one_glyph_library_per_script(self) -> None:
        """edit: Claude (Opus 5.5), 2026-09-26 11:40 +0400 — the render loop builds ONE GlyphLibrary per script, not one per
        request (the eager `setdefault` default built 9,707 for the 20261001 tape). 8 requests over 3 scripts → 3 builds; the old
        loop builds 8, so this test fails on the old code."""
        from unittest import mock
        import brain.world.build as B
        real = B.GlyphLibrary
        built = []

        def counting(script):
            built.append(script)
            return real(script)

        with mock.patch.object(B, "GlyphLibrary", side_effect=counting):
            build_cache(_small_requests(), self.dir, SEED, recheck_n=2)
        self.assertEqual(sorted(built), ["digits", "latin-lower", "latin-upper"])

    def test_duplicate_item_id_raises(self) -> None:
        reqs = _small_requests()
        reqs.append(RenderRequest(item_id=reqs[0].item_id, script="latin-upper", char="Z", font=FONT))
        with self.assertRaises(BuildError):
            build_cache(reqs, self.dir, SEED)

    def test_deterministic_across_two_independent_builds(self) -> None:
        """The same seed + same requests -> byte-identical cache (the identity law, §2.8)."""
        reqs = _small_requests()
        dir1 = self.dir.parent / "run1"
        dir2 = self.dir.parent / "run2"
        i1, h1, _t1 = build_cache(reqs, dir1, SEED)
        i2, h2, _t2 = build_cache(reqs, dir2, SEED)
        self.assertEqual(i1, i2)
        self.assertEqual(h1["npy_sha256"], h2["npy_sha256"])

    def test_different_item_id_same_char_font_gives_different_rendering(self) -> None:
        """Two TEACH showings of the SAME (char, font) must NOT render identically — "a fresh rendering per
        showing" (§2.7) depends on item_id (not (char,font)) driving the rng."""
        reqs = [
            RenderRequest(item_id="showing:1", script="latin-upper", char="A", font=FONT),
            RenderRequest(item_id="showing:2", script="latin-upper", char="A", font=FONT),
        ]
        item_to_row, _header, _truths = build_cache(reqs, self.dir, SEED)
        cache = Cache(self.dir)
        f1 = cache.glances(item_to_row["showing:1"])
        f2 = cache.glances(item_to_row["showing:2"])
        self.assertFalse(np.array_equal(f1, f2), "two different item_ids of the same (char,font) rendered identically")

    def test_canvas_png_sha256_deterministic(self) -> None:
        rgb = np.zeros((128, 128, 3), dtype=np.uint8)
        rgb[0, 0, 0] = 7
        self.assertEqual(canvas_png_sha256(rgb), canvas_png_sha256(rgb))


if __name__ == "__main__":
    unittest.main()
