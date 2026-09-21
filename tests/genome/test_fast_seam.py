"""test_fast_seam.py — G-MIND-1 (docs/organs/MIND-MEMORY.md §4; docs/briefs/G5-I-SEAM-DELIVER-MOMENT.md):
Episodes' four new fields (where/when/act/source) + glance, at the unit level (no genome parsing, no
Mind) — write/get round-trips, absence defaults, save/load persistence, and `nearest_where`.

edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400 — kept SEPARATE from test_fast.py (B3,
Builder B's file) rather than folding in, matching B8's "adds NEW tests beside them" discipline — B3's
file stays untouched.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome.fast import Episodes

from ._toy import onehot


class TestSeamFieldsWriteAndGet(unittest.TestCase):
    def test_seam_fields_round_trip(self) -> None:
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        eid = ep.write(moment=1, x_s=onehot(0, 8), x_w=onehot(0, 4), word="circle", surprise=0.1,
                        where=(20, 44), when="2026-09-21T20:57:00.000Z", act="glance", source="maker", glance=0)
        rec = ep.get(eid)
        self.assertEqual(rec["where"], (20, 44))
        self.assertEqual(rec["when"], "2026-09-21T20:57:00.000Z")
        self.assertEqual(rec["act"], "glance")
        self.assertEqual(rec["source"], "maker")
        self.assertEqual(rec["glance"], 0)

    def test_absent_seam_fields_read_back_as_none(self) -> None:
        """The pre-existing call shape (no seam kwargs) — exactly what every caller wrote before this
        gene existed — must still read back as "nothing here", never a fabricated value."""
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        eid = ep.write(moment=1, x_s=onehot(0, 8), x_w=onehot(0, 4), word="circle", surprise=0.1)
        rec = ep.get(eid)
        self.assertIsNone(rec["where"]); self.assertIsNone(rec["when"])
        self.assertIsNone(rec["act"]); self.assertIsNone(rec["source"]); self.assertIsNone(rec["glance"])

    def test_glance_zero_is_not_confused_with_absent(self) -> None:
        """glance=0 (a real, valid glance ordinal) must not read back as None -- -1 is the sentinel, not 0."""
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        eid = ep.write(moment=1, x_s=onehot(0, 8), x_w=onehot(0, 4), word="circle", surprise=0.1, glance=0)
        self.assertEqual(ep.get(eid)["glance"], 0)

    def test_where_does_not_alter_x_s_or_cosine_recall(self) -> None:
        """The load-bearing claim of G-EYE-1/G-MIND-1: `where` never touches x_s. Two episodes with
        IDENTICAL x_s but DIFFERENT `where` must still tie at cosine 1.0 under `nearest` -- `where`
        carries no information into the cosine-compared store."""
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        x0 = onehot(0, 8)
        e1 = ep.write(moment=1, x_s=x0, x_w=onehot(0, 4), word="a", surprise=0.1, where=(1, 1))
        e2 = ep.write(moment=2, x_s=x0, x_w=onehot(0, 4), word="b", surprise=0.1, where=(99, 99))
        r = ep.nearest(x0, k=2)
        self.assertEqual({i for i, _c in r}, {e1, e2})
        self.assertEqual(r[0][1], r[1][1], "identical x_s must tie exactly regardless of `where`")


class TestNearestWhere(unittest.TestCase):
    def test_finds_the_exact_match_first(self) -> None:
        ep = Episodes(cap=10, dim_s=4, dim_w=4)
        near = ep.write(moment=1, x_s=onehot(0, 4), x_w=onehot(0, 4), word="near", surprise=0.0, where=(10, 10))
        far = ep.write(moment=2, x_s=onehot(1, 4), x_w=onehot(0, 4), word="far", surprise=0.0, where=(90, 90))
        r = ep.nearest_where((10, 10), k=2)
        self.assertEqual(r[0][0], near)
        self.assertEqual(r[0][1], 0.0)
        self.assertEqual(r[1][0], far)

    def test_never_reads_x_s(self) -> None:
        """Two episodes with byte-identical x_s but different `where` -- nearest_where must still tell
        them apart (it is blind to x_s by construction, not by luck)."""
        ep = Episodes(cap=10, dim_s=4, dim_w=4)
        x0 = onehot(0, 4)
        a = ep.write(moment=1, x_s=x0, x_w=onehot(0, 4), word="a", surprise=0.0, where=(0, 0))
        b = ep.write(moment=2, x_s=x0, x_w=onehot(0, 4), word="b", surprise=0.0, where=(50, 50))
        r = ep.nearest_where((0, 0), k=1)
        self.assertEqual(r[0][0], a)

    def test_episodes_with_no_where_are_never_candidates(self) -> None:
        ep = Episodes(cap=10, dim_s=4, dim_w=4)
        ep.write(moment=1, x_s=onehot(0, 4), x_w=onehot(0, 4), word="blind", surprise=0.0)   # no where
        seeing = ep.write(moment=2, x_s=onehot(1, 4), x_w=onehot(0, 4), word="seeing", surprise=0.0, where=(5, 5))
        r = ep.nearest_where((5, 5), k=5)
        self.assertEqual([i for i, _d in r], [seeing])

    def test_empty_or_all_blind_store_returns_empty(self) -> None:
        ep = Episodes(cap=5, dim_s=4, dim_w=4)
        self.assertEqual(ep.nearest_where((0, 0), 3), [])
        ep.write(moment=1, x_s=onehot(0, 4), x_w=onehot(0, 4), word="blind", surprise=0.0)
        self.assertEqual(ep.nearest_where((0, 0), 3), [])

    def test_ring_overwrite_drops_where_too(self) -> None:
        """The ring's own law (B3): an overwritten episode's `where` is gone with the rest of the row,
        never a stale coordinate surviving under a new id."""
        ep = Episodes(cap=2, dim_s=4, dim_w=4)
        e0 = ep.write(moment=1, x_s=onehot(0, 4), x_w=onehot(0, 4), word="a", surprise=0.0, where=(1, 1))
        ep.write(moment=2, x_s=onehot(1, 4), x_w=onehot(0, 4), word="b", surprise=0.0, where=(2, 2))
        ep.write(moment=3, x_s=onehot(2, 4), x_w=onehot(0, 4), word="c", surprise=0.0, where=(3, 3))  # overwrites e0's slot
        self.assertIsNone(ep.get(e0))
        r = ep.nearest_where((1, 1), k=5)
        self.assertNotIn(e0, [i for i, _d in r])


class TestSaveLoadRoundTrip(unittest.TestCase):
    def test_seam_fields_survive_save_and_load(self) -> None:
        ep = Episodes(cap=4, dim_s=4, dim_w=4)
        ep.write(moment=1, x_s=onehot(0, 4), x_w=onehot(0, 4), word="a", surprise=0.1,
                  where=(7, 9), when="2026-09-21T20:57:00.000Z", act="glance", source="folder", glance=0)
        ep.write(moment=2, x_s=onehot(1, 4), x_w=onehot(0, 4), word="b", surprise=0.2)  # no seam fields

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "episodes.npz"
            ep.save(path)
            loaded = Episodes.load(path)

        self.assertEqual(loaded.get(0)["where"], (7, 9))
        self.assertEqual(loaded.get(0)["when"], "2026-09-21T20:57:00.000Z")
        self.assertEqual(loaded.get(0)["act"], "glance")
        self.assertEqual(loaded.get(0)["source"], "folder")
        self.assertEqual(loaded.get(0)["glance"], 0)
        self.assertIsNone(loaded.get(1)["where"])
        self.assertIsNone(loaded.get(1)["source"])

    def test_loading_a_pre_seam_file_defaults_to_absent_everywhere(self) -> None:
        """A store saved before this gene existed (life 3a's own episodes.npz, for instance) has none of
        the new npz keys -- loading it must default to "nowhere, no clock, no act, no source, no glance",
        never raise."""
        ep = Episodes(cap=3, dim_s=4, dim_w=4)
        ep.write(moment=1, x_s=onehot(0, 4), x_w=onehot(0, 4), word="a", surprise=0.1)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "pre_seam.npz"
            # write the file the OLD way (no where_y/where_x/has_where/when/act/source/glance keys),
            # exactly what genome/fast.py wrote before this gene existed.
            meta = np.array([ep.cap, ep.dim_s, ep.dim_w, ep.n_written, ep._next_slot], dtype=np.int64)
            np.savez_compressed(path, meta=meta, moment=ep.moment, ids=ep.ids, x_s=ep.x_s, x_w=ep.x_w,
                                 word=ep.word, surprise=ep.surprise, x_s2=ep.x_s2, has_s2=ep.has_s2)
            loaded = Episodes.load(path)
        self.assertIsNone(loaded.get(0)["where"])
        self.assertIsNone(loaded.get(0)["when"])
        self.assertIsNone(loaded.get(0)["act"])
        self.assertIsNone(loaded.get(0)["source"])
        self.assertIsNone(loaded.get(0)["glance"])


if __name__ == "__main__":
    unittest.main()
