# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 15:05 +0400 — the N1 bench's own tests
# (PREREG-N1-PRECISION §2's instrument discipline): the world builder is deterministic to the last float,
# the plant arm's register is truly frozen (w ≡ 1 — G-PLANT's doctored form), and the report carries every
# mark of the law with presence counts (never a bare number).
from __future__ import annotations

import unittest

import numpy as np

from genome.machinery import parse_genome, retina_dim
from genome.predict import Predictor
from tools.brain.precision_bench import (BENCH_SEED, DEV_A, DEV_B, N_A, N_B, FrozenPredictor,
                                         build_rows, drive, TOY)


class TestPrecisionBench(unittest.TestCase):
    def test_world_build_deterministic(self) -> None:
        g = parse_genome(TOY)
        rows_a = build_rows(g, BENCH_SEED)
        rows_b = build_rows(g, BENCH_SEED)
        self.assertEqual(len(rows_a), len(rows_b))
        self.assertEqual(len(rows_a), N_A + N_B + 1200, "presence: the world's declared size")
        same = sum(1 for (ka, ta, xa), (kb, tb, xb) in zip(rows_a, rows_b)
                   if ka == kb and ta == tb and np.array_equal(xa, xb))
        self.assertEqual(same, len(rows_a), "two builds of the declared seed are identical to the last bit")

    def test_null_twin_differs_only_in_the_noise_slots(self) -> None:
        g = parse_genome(TOY)
        real = build_rows(g, BENCH_SEED)
        twin = build_rows(g, BENCH_SEED, no_noise=True)
        real_noise = [r for r in real if r[0] == "noise"]
        twin_noise = [r for r in twin if r[0] == "noise"]
        self.assertGreater(len(real_noise), 0, "presence: the real world has noise rows")
        self.assertEqual(len(twin_noise), 0, "the twin removed exactly the noise rows")
        self.assertEqual(len(real), len(twin), "the twin keeps the row count")
        # deviants untouched
        self.assertEqual([r[1] for r in real if r[0] == "deviant"],
                         [r[1] for r in twin if r[0] == "deviant"])

    def test_plant_register_frozen(self) -> None:
        """The doctored register reads w ≡ 1 over a real drive — G-PLANT's planted form caught by
        construction here, caught by the bench's M-MMN-1 at full scale."""
        g = parse_genome(TOY)
        rows = build_rows(g, BENCH_SEED)[:80]
        org_rows = drive(rows, g, precision=True, plant=True)[0]
        ws = [r["w"] for r in org_rows]
        self.assertTrue(all(w is not None for w in ws), "presence: the plant arm reads weights")
        self.assertTrue(all(w == 1.0 for w in ws), f"the frozen register must read w ≡ 1, got {sorted(set(ws))[:5]}")

    def test_deviant_positions_declared(self) -> None:
        """The deviants sit where the law puts them (AMENDMENT 2.2), one showing each."""
        g = parse_genome(TOY)
        rows = build_rows(g, BENCH_SEED)
        dev = [(i, r[1]) for i, r in enumerate(rows) if r[0] == "deviant"]
        self.assertEqual([i for i, _ in dev], sorted(list(DEV_A) + [N_A + k for k in sorted(DEV_B)]))
        self.assertEqual(len({t for _, t in dev}), 6, "six distinct one-showing things")


if __name__ == "__main__":
    unittest.main()
