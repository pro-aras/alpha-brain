# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:42 +0400 — found by THE FIRST GATE's first launch (17:41, a crash before any verdict):
# PREREG-TMEM2 §2's claims read the LAW road's step 1 BETWEEN reading points, where a word met since the last calibration
# («dax», scene 2,700) sits beyond the reading point's band cache — `logp_answer` indexed the cache by the word and raised
# IndexError. S1b-1R only ever answered right after calibrating (its cache covered every word), so its roads never met this.
# Test-first: RED on 01e784b (the IndexError), green with the guard (a word newer than the cache takes its band fresh — the same
# function the cache is built from), and every column of the words the cache covers unchanged.
from __future__ import annotations

import copy
import unittest

import numpy as np

from brain.scene import learners as Lr


def _calibrated(seed=0, n=400):
    rng = np.random.default_rng(seed)
    A = {f"a{i}": rng.normal(size=Lr.RW_DIM) * 2 for i in range(3)}
    B = {f"b{i}": rng.normal(size=Lr.RW_DIM) * 2 for i in range(2)}
    L = Lr.RWLearner(lr=0.01)
    seen = []
    for k in range(n):
        a, b = f"a{rng.integers(3)}", f"b{rng.integers(2)}"
        raw = (A[a] + B[b] + 0.5 * rng.normal(size=Lr.RW_DIM))[None, :]
        L.train_scene(raw, [a, b], rng=np.random.default_rng(k))
        seen.append((raw, [a, b], None))
    L.calibrate(seen)
    L.calibrate_r(0.3)
    return L, A, B, rng


class TestAWordNewerThanTheBandCache(unittest.TestCase):
    def test_the_laws_step_1_between_reading_points(self) -> None:
        L, A, B, rng = _calibrated()
        X = np.stack([A["a0"] + B["b0"], A["a1"] + B["b1"]])
        L.train_scene(X, ["dax"], rng=np.random.default_rng(3))                # a new word AFTER the calibration
        self.assertEqual(len(L._bands_cache), len(L.words) - 1)
        got = Lr.RWRoad(L).believed(X)                                          # 01e784b: IndexError
        fresh = copy.deepcopy(L)
        fresh._bands_cache = fresh.bands()                                      # the cache a calibration would build now
        self.assertEqual(got, Lr.RWRoad(fresh).believed(X))
        Z = L.stats.standardise(X)
        a, b = L.logp_answer(Z, L._bands_cache), fresh.logp_answer(Z, fresh._bands_cache)
        self.assertTrue(np.array_equal(a, b))                                   # the young word's column: its band, fresh
        old = [j for j in range(len(L.words) - 1)]
        self.assertTrue(np.array_equal(a[:, old], L.logp_answer(Z, None)[:, old]))


if __name__ == "__main__":
    unittest.main()
