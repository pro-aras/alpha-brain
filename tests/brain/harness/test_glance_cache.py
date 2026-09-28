# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:2x +0400 — tests for brain/glance_cache.py, shipped
# in the same commit as brain/protocol.py (an ASK/TEACH row's glance_row/candidate_rows/operand ints index
# THIS reader). Synthetic cache only — the real cache (real glyphs through the real gaze) is built in
# brain/world/build_cache.py, B1-PREREG.md §2's world step.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from brain.glance_cache import Cache, CacheError, CacheWriter, FEATURES_PER_GLANCE, GLANCES_PER_ROW, sha256_file


def _feats(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(size=(GLANCES_PER_ROW, FEATURES_PER_GLANCE))


class TestCacheWriterReader(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name) / "cache" / "20261001"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _build(self, n: int = 5) -> dict:
        w = CacheWriter(self.dir)
        for i in range(n):
            row = w.add(item_id=f"item-{i}", script="latin-upper", char=chr(ord("A") + i), font="TestFont.ttf",
                        variant="base-32", seed=20261001, canvas_png_sha256=f"sha-{i}", feats=_feats(i))
            self.assertEqual(row, i)
        return w.finalize(seed=20261001, genome_sha="deadbeef", organ_pins={"tower": "abc"},
                           interpreter={"python": "3.14.4"}, library_versions={"numpy": "2.3.5"})

    def test_round_trip_byte_identical(self) -> None:
        self._build(5)
        c = Cache(self.dir)
        self.assertEqual(len(c), 5)
        for i in range(5):
            got = c.glances(i)
            want = _feats(i)
            np.testing.assert_array_equal(got, want)
            self.assertEqual(c.meta(i)["char"], chr(ord("A") + i))
        c.verify()   # must not raise

    def test_glances_returns_a_copy_not_the_mmap_view(self) -> None:
        self._build(2)
        c = Cache(self.dir)
        got = c.glances(0)
        got[:] = 0.0
        again = c.glances(0)
        self.assertFalse(np.all(again == 0.0), "mutating a returned row corrupted the cache")

    def test_out_of_range_row_raises(self) -> None:
        self._build(2)
        c = Cache(self.dir)
        with self.assertRaises(CacheError):
            c.glances(2)
        with self.assertRaises(CacheError):
            c.meta(-1)

    def test_verify_catches_planted_byte_corruption(self) -> None:
        self._build(3)
        npy_path = self.dir / "glances.npy"
        raw = bytearray(npy_path.read_bytes())
        # flip a byte well past the .npy header (the header is small; this lands in the float payload).
        flip_at = len(raw) - 1
        raw[flip_at] ^= 0xFF
        npy_path.write_bytes(bytes(raw))
        c = Cache(self.dir)   # shape/row_count checks alone don't see a single flipped byte
        with self.assertRaises(CacheError):
            c.verify()

    def test_row_count_mismatch_between_index_and_header_is_caught(self) -> None:
        self._build(3)
        index_path = self.dir / "index.jsonl"
        lines = index_path.read_text().splitlines()
        index_path.write_text("\n".join(lines[:-1]) + "\n")   # drop the last row
        with self.assertRaises(CacheError):
            Cache(self.dir)

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(CacheError):
            Cache(self.dir)   # nothing built yet

    def test_sha256_file_matches_header(self) -> None:
        header = self._build(4)
        self.assertEqual(header["npy_sha256"], sha256_file(self.dir / "glances.npy"))
        self.assertEqual(header["row_count"], 4)


if __name__ == "__main__":
    unittest.main()
