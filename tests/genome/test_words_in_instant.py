# edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 2 (docs/briefs/LIFE-C-QUESTION-SENTENCE.md):
# Episodes' two new fields (`words_in_instant`, `tape_moment`), at the unit level (no genome parsing, no
# Mind) -- write/get round-trips, absence defaults, save/load persistence. Kept SEPARATE from test_fast.py
# and test_fast_seam.py, matching that file's own "adds NEW tests beside them" discipline.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from genome.fast import Episodes

from ._toy import onehot


class TestWordsInInstantWriteAndGet(unittest.TestCase):
    def test_two_words_round_trip_in_order(self) -> None:
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        eid = ep.write(moment=1, x_s=onehot(0, 8), x_w=onehot(0, 4), word="ball", surprise=0.1,
                        words_in_instant=["red", "ball"], tape_moment="g1234000000001s000000001")
        rec = ep.get(eid)
        self.assertEqual(rec["words_in_instant"], ["red", "ball"])
        self.assertEqual(rec["tape_moment"], "g1234000000001s000000001")

    def test_absent_reads_back_as_empty_list_and_none(self) -> None:
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        eid = ep.write(moment=1, x_s=onehot(0, 8), x_w=onehot(0, 4), word="circle", surprise=0.1)
        rec = ep.get(eid)
        self.assertEqual(rec["words_in_instant"], [])
        self.assertIsNone(rec["tape_moment"])

    def test_one_word_round_trips_as_a_single_element_list(self) -> None:
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        eid = ep.write(moment=1, x_s=onehot(0, 8), x_w=onehot(0, 4), word="circle", surprise=0.1,
                        words_in_instant=["circle"], tape_moment="w0000i000001t000000001")
        rec = ep.get(eid)
        self.assertEqual(rec["words_in_instant"], ["circle"])

    def test_never_touches_x_s_or_word(self) -> None:
        """words_in_instant/tape_moment are new COLUMNS -- nothing that computes a cosine reads them."""
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        eid = ep.write(moment=1, x_s=onehot(0, 8), x_w=onehot(0, 4), word="ball", surprise=0.1,
                        words_in_instant=["red", "ball"], tape_moment="m1")
        rec = ep.get(eid)
        self.assertTrue((rec["x_s"] == onehot(0, 8)).all())
        self.assertEqual(rec["word"], "ball")


class TestSaveLoadRoundTrip(unittest.TestCase):
    def test_words_in_instant_survives_save_and_load(self) -> None:
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        ep.write(moment=1, x_s=onehot(0, 8), x_w=onehot(0, 4), word="ball", surprise=0.1,
                  words_in_instant=["red", "ball"], tape_moment="g1s1")
        ep.write(moment=2, x_s=onehot(1, 8), x_w=onehot(1, 4), word="circle", surprise=0.2)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "episodes.npz"
            ep.save(path)
            loaded = Episodes.load(path)
        self.assertEqual(loaded.get(0)["words_in_instant"], ["red", "ball"])
        self.assertEqual(loaded.get(0)["tape_moment"], "g1s1")
        self.assertEqual(loaded.get(1)["words_in_instant"], [])

    def test_loading_a_pre_sentence_file_defaults_to_absent_everywhere(self) -> None:
        """A store saved before this gene existed has neither column at all in the npz -- load() must not
        KeyError, and every row reads back as if words_in_instant/tape_moment were never written."""
        ep = Episodes(cap=3, dim_s=4, dim_w=2)
        ep.write(moment=1, x_s=onehot(0, 4), x_w=onehot(0, 2), word="x", surprise=0.0)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "pre_sentence.npz"
            tmp = path.with_name(path.name + ".tmp")
            import numpy as np
            with open(tmp, "wb") as f:
                np.savez_compressed(f, meta=np.array([ep.cap, ep.dim_s, ep.dim_w, ep.n_written, ep._next_slot], dtype=np.int64),
                                     moment=ep.moment, ids=ep.ids, x_s=ep.x_s, x_w=ep.x_w, word=ep.word, surprise=ep.surprise)
            tmp.replace(path)
            loaded = Episodes.load(path)
        self.assertEqual(loaded.get(0)["words_in_instant"], [])
        self.assertIsNone(loaded.get(0)["tape_moment"])


if __name__ == "__main__":
    unittest.main()
