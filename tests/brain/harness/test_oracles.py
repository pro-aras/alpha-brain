# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:4x +0400 — tests for brain/harness/oracles.py, all on
# SYNTHETIC data (fast, no rendering) — the real-data integration is stage_minus1's own test.
from __future__ import annotations

import unittest

import numpy as np

from brain.harness.oracles import (
    LinearReadoutOracle, NearestNeighbourOracle, OracleError, accuracy, f_cat, f_pool, permutation_null,
)


class TestFPool(unittest.TestCase):
    def test_unit_norm_and_order_free(self) -> None:
        rng = np.random.default_rng(1)
        glances = rng.normal(size=(5, 144))
        v1 = f_pool(glances)
        v2 = f_pool(glances[::-1].copy())   # order-free: reversing the glances must not change the pool
        self.assertAlmostEqual(float(np.linalg.norm(v1)), 1.0, places=8)
        np.testing.assert_allclose(v1, v2, atol=1e-12)

    def test_f_cat_is_order_sensitive_unlike_f_pool(self) -> None:
        rng = np.random.default_rng(2)
        glances = rng.normal(size=(3, 4))
        c1 = f_cat(glances)
        c2 = f_cat(glances[::-1].copy())
        self.assertAlmostEqual(float(np.linalg.norm(c1)), 1.0, places=8)
        self.assertFalse(np.allclose(c1, c2))


def _unit_rows(X: np.ndarray) -> np.ndarray:
    return X / np.linalg.norm(X, axis=1, keepdims=True)


class TestNearestNeighbourOracle(unittest.TestCase):
    def test_separates_two_clusters(self) -> None:
        rng = np.random.default_rng(3)
        a = _unit_rows(rng.normal(loc=1.0, scale=0.01, size=(10, 8)) + np.array([5] + [0] * 7))
        b = _unit_rows(rng.normal(loc=1.0, scale=0.01, size=(10, 8)) + np.array([0] * 7 + [5]))
        X = np.vstack([a, b])
        y = ["a"] * 10 + ["b"] * 10
        oracle = NearestNeighbourOracle().fit(X, y)
        pred = oracle.predict(X)
        self.assertEqual(accuracy(pred, y), 1.0)

    def test_tie_broken_by_label_order(self) -> None:
        v = np.array([1.0, 0.0])
        oracle = NearestNeighbourOracle().fit(np.array([v, v]), ["zzz", "aaa"])
        self.assertEqual(oracle.predict_one(v), "aaa")

    def test_predict_before_fit_raises(self) -> None:
        with self.assertRaises(OracleError):
            NearestNeighbourOracle().predict_one(np.array([1.0, 0.0]))


class TestLinearReadoutOracle(unittest.TestCase):
    def test_separable_data_near_perfect_train_accuracy(self) -> None:
        rng = np.random.default_rng(4)
        a = rng.normal(loc=0.0, scale=0.05, size=(30, 5)) + np.array([3, 0, 0, 0, 0])
        b = rng.normal(loc=0.0, scale=0.05, size=(30, 5)) + np.array([0, 3, 0, 0, 0])
        c = rng.normal(loc=0.0, scale=0.05, size=(30, 5)) + np.array([0, 0, 3, 0, 0])
        X = _unit_rows(np.vstack([a, b, c]))
        y = ["a"] * 30 + ["b"] * 30 + ["c"] * 30
        oracle = LinearReadoutOracle().fit(X, y)
        pred = oracle.predict(X)
        self.assertGreaterEqual(accuracy(pred, y), 0.95)

    def test_deterministic_fit(self) -> None:
        rng = np.random.default_rng(5)
        X = _unit_rows(rng.normal(size=(20, 4)))
        y = (["a"] * 10) + (["b"] * 10)
        o1 = LinearReadoutOracle().fit(X, y)
        o2 = LinearReadoutOracle().fit(X, y)
        np.testing.assert_array_equal(o1.W, o2.W)
        np.testing.assert_array_equal(o1.b, o2.b)

    def test_single_class_raises(self) -> None:
        X = np.ones((5, 2))
        with self.assertRaises(OracleError):
            LinearReadoutOracle().fit(X, ["a"] * 5)


class TestAccuracy(unittest.TestCase):
    def test_basic(self) -> None:
        self.assertEqual(accuracy(["a", "b", "c"], ["a", "b", "x"]), 2 / 3)

    def test_length_mismatch_raises(self) -> None:
        with self.assertRaises(OracleError):
            accuracy(["a"], ["a", "b"])

    def test_empty_raises(self) -> None:
        with self.assertRaises(OracleError):
            accuracy([], [])


class TestPermutationNull(unittest.TestCase):
    def test_shuffled_labels_read_near_chance(self) -> None:
        rng = np.random.default_rng(6)
        a = rng.normal(size=(20, 6)) + np.array([4, 0, 0, 0, 0, 0])
        b = rng.normal(size=(20, 6)) + np.array([0, 4, 0, 0, 0, 0])
        X_train = _unit_rows(np.vstack([a, b]))
        y_train = ["a"] * 20 + ["b"] * 20
        X_test, y_test = X_train, y_train   # fine for a null check

        def fit_predict(Xtr, ytr, Xte):
            return LinearReadoutOracle().fit(Xtr, ytr).predict(Xte)

        null = permutation_null(fit_predict, X_train, y_train, X_test, y_test, seed=42, n_perm=20)
        self.assertEqual(null["n_perm"], 20)
        # chance for a balanced 2-class problem is 0.5; a real (unshuffled) fit would read ~1.0
        self.assertLess(null["mean"], 0.75)

    def test_deterministic_given_seed(self) -> None:
        X = _unit_rows(np.random.default_rng(1).normal(size=(10, 3)))
        y = ["a"] * 5 + ["b"] * 5

        def fit_predict(Xtr, ytr, Xte):
            return NearestNeighbourOracle().fit(Xtr, ytr).predict(Xte)

        n1 = permutation_null(fit_predict, X, y, X, y, seed=7, n_perm=5)
        n2 = permutation_null(fit_predict, X, y, X, y, seed=7, n_perm=5)
        self.assertEqual(n1["scores"], n2["scores"])


if __name__ == "__main__":
    unittest.main()
