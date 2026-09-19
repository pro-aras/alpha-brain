"""test_fast.py — B3: FAST (genome/fast.py's Episodes) — one-shot recall, the ring, save/load.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B3 (docs/G4-PREREG.md §3, docs/briefs/
G4-BUILDER-B-GENES.md): an episode written at moment t is the nearest at t+1 with its word (one-shot); a
shuffled query does not recall it; the ring overwrites the oldest at cap; save/load round-trips byte-exact.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome.fast import Episodes

from ._toy import onehot


class TestFast(unittest.TestCase):
    def test_one_shot_recall_at_next_moment_with_its_word(self) -> None:
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        x0 = onehot(0, 8)
        eid0 = ep.write(moment=5, x_s=x0, x_w=onehot(0, 4), word="circle", surprise=0.4)
        # "at t+1": the very next query, immediately after the write, recalls it exactly (one-shot —
        # no repetition needed, unlike SLOW's resonance-threshold birth).
        r = ep.nearest(x0, k=1)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], (eid0, 1.0))
        rec = ep.get(eid0)
        self.assertIsNotNone(rec)
        self.assertEqual(rec["word"], "circle")
        self.assertEqual(rec["moment"], 5)

    def test_shuffled_query_does_not_recall_it(self) -> None:
        ep = Episodes(cap=5, dim_s=8, dim_w=4)
        eid0 = ep.write(moment=1, x_s=onehot(0, 8), x_w=onehot(0, 4), word="circle", surprise=0.1)
        ep.write(moment=2, x_s=onehot(1, 8), x_w=onehot(1, 4), word="square", surprise=0.1)
        ep.write(moment=3, x_s=onehot(2, 8), x_w=onehot(2, 4), word="triangle", surprise=0.1)
        # a query orthogonal to everything written (the "shuffled" one-hot lands on a dimension no
        # episode used): cosine to the true match is 0.0, not 1.0 — no genuine recall happened, whatever
        # id the tie-break returns.
        shuffled = onehot(5, 8)
        r = ep.nearest(shuffled, k=1)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0][1], 0.0, "a shuffled query must not score a genuine (cos=1.0) match")
        self.assertNotEqual(r[0], (eid0, 1.0))

    def test_ring_overwrites_the_oldest_at_cap(self) -> None:
        ep = Episodes(cap=3, dim_s=4, dim_w=2)
        ids = [ep.write(moment=t, x_s=onehot(t % 4, 4), x_w=onehot(0, 2), word=f"w{t}", surprise=float(t))
               for t in range(4)]      # one more write than cap
        self.assertEqual(len(ep), 3)
        self.assertIsNone(ep.get(ids[0]), "the oldest episode must be gone once the ring wraps")
        for eid in ids[1:]:
            self.assertIsNotNone(ep.get(eid))
        # the ring holds exactly the 3 most recent ids — nearest/most_surprising never see the evicted one
        ms = ep.most_surprising(10)
        self.assertEqual(sorted(ms), sorted(ids[1:]))
        self.assertNotIn(ids[0], ms)

    def test_most_surprising_ranks_descending_ties_by_id(self) -> None:
        ep = Episodes(cap=5, dim_s=4, dim_w=2)
        a = ep.write(0, onehot(0, 4), onehot(0, 2), "a", surprise=0.5)
        b = ep.write(1, onehot(1, 4), onehot(0, 2), "b", surprise=0.9)
        c = ep.write(2, onehot(2, 4), onehot(0, 2), "c", surprise=0.9)   # ties with b; smaller id first
        d = ep.write(3, onehot(3, 4), onehot(0, 2), "d", surprise=0.1)
        self.assertEqual(ep.most_surprising(4), [b, c, a, d])
        self.assertEqual(ep.most_surprising(2), [b, c])

    def test_save_load_round_trips_byte_exact(self) -> None:
        ep = Episodes(cap=3, dim_s=6, dim_w=3)
        rng = np.random.default_rng(0)
        for t in range(5):     # more than cap: exercises the wrap on reload too
            v = rng.normal(size=6); v /= np.linalg.norm(v)
            w = rng.normal(size=3); w /= np.linalg.norm(w)
            ep.write(moment=t, x_s=v, x_w=w, word=f"thing{t}", surprise=float(t) * 0.1)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "episodes.npz"
            ep.save(path)
            self.assertTrue(path.exists())
            self.assertFalse((Path(d) / "episodes.npz.tmp").exists(), "the tmp file must be renamed away")
            loaded = Episodes.load(path)
        self.assertEqual(loaded.cap, ep.cap)
        self.assertEqual(loaded.dim_s, ep.dim_s)
        self.assertEqual(loaded.dim_w, ep.dim_w)
        self.assertEqual(loaded.n_written, ep.n_written)
        self.assertEqual(loaded._next_slot, ep._next_slot)
        self.assertTrue(np.array_equal(loaded.moment, ep.moment))
        self.assertTrue(np.array_equal(loaded.ids, ep.ids))
        self.assertTrue(np.array_equal(loaded.x_s, ep.x_s))
        self.assertTrue(np.array_equal(loaded.x_w, ep.x_w))
        self.assertTrue(np.array_equal(loaded.word, ep.word))
        self.assertTrue(np.array_equal(loaded.surprise, ep.surprise))
        self.assertEqual(loaded._id_to_slot, ep._id_to_slot)
        # functional equivalence too
        q = ep.x_s[0]
        self.assertEqual(loaded.nearest(q, 3), ep.nearest(q, 3))
        self.assertEqual(loaded.most_surprising(5), ep.most_surprising(5))


if __name__ == "__main__":
    unittest.main()
