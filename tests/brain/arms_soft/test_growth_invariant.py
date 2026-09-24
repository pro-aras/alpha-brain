# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 16:45 +0400 — the Dohare et al. 2024
#   invariant B1-PREREG.md §4 row A1 declares for A1's births: "incoming weights from the init
#   distribution, outgoing weights ZERO ... a birth never changes what it already computes"
#   (CONCLUSION.md §3 law 3). Proven directly (not asserted): run identical inputs through the
#   engine before and after a birth and assert the OLD units' hidden values and every head's
#   output are bit-identical, then assert the new unit itself is NOT silently inert (it must
#   have a nonzero incoming row, or growth is cosmetic).
import os
import sys
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.soft.engine import GrowingGRUEngine, YesNoHead, new_generator  # noqa: E402


class TestGrowthInvariant(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(0)

    def test_birth_does_not_move_old_units_or_heads(self):
        seed = 555
        engine = GrowingGRUEngine(input_dim=4, h0=4, hmax=16, seed=seed, arrival_budget=8, arrival_regen=10)
        head = YesNoHead(hmax=16)
        gen = new_generator(seed, "head_init", 0)
        head.init_block(4, gen)
        engine.register_growth_listener(head)

        x = torch.tensor([0.3, -0.1, 0.7, 0.2])
        h0 = engine.zero_state()
        h_before = engine.step(x, h0)
        active_before = engine.active
        logits_before = head(h_before, active_h=active_before)

        got = engine.grow(3)
        self.assertEqual(got, 3, "grow(3) should be fully granted (budget=8, hmax room=12)")
        self.assertEqual(engine.active, 7)

        h_after = engine.step(x, engine.pad_state(h0))
        # the OLD units' post-step values must be bit-identical (D2's invariant)
        self.assertTrue(
            torch.equal(h_before[:active_before], h_after[:active_before]),
            "a birth moved an OLD unit's hidden value — the outgoing-zero invariant is broken",
        )
        logits_after = head(h_after, active_h=engine.active)
        self.assertTrue(
            torch.equal(logits_before, logits_after),
            "a birth changed an existing head's output — a birth must change nothing already computed",
        )

        # the new units must not be silently inert: they should have a NONZERO incoming row
        # (else "growth" would be cosmetic — a unit that can never learn anything)
        new_rows_nonzero = any(
            float(getattr(engine, f"W_ih_{g}")[active_before:engine.active].detach().abs().sum()) > 0.0
            for g in ("r", "z", "n")
        )
        self.assertTrue(new_rows_nonzero, "a newborn unit's incoming input weights must be randomly initialised")

        # and the new units' OUTGOING weights (their column in W_hh) must be exactly zero
        for g in ("r", "z", "n"):
            Whh = getattr(engine, f"W_hh_{g}")
            col_block = Whh[: engine.active, active_before:engine.active]
            self.assertEqual(float(col_block.detach().abs().sum()), 0.0, f"W_hh_{g}: a newborn's outgoing column is not zero")

    def test_hmax_bound_refuses_and_counts_never_eats(self):
        engine = GrowingGRUEngine(input_dim=2, h0=6, hmax=8, seed=1, arrival_budget=100, arrival_regen=1)
        got = engine.grow(10)  # only 2 rooms left under hmax=8
        self.assertEqual(got, 2)
        self.assertEqual(engine.active, 8)
        self.assertEqual(engine.refused_hmax, 8, "refusals at hmax must be COUNTED (#227/#233), never silently eaten")
        got2 = engine.grow(1)
        self.assertEqual(got2, 0, "no room left under hmax: a further birth must be refused, not evict anyone")
        self.assertEqual(engine.refused_hmax, 9)

    def test_budget_regenerates_and_is_a_series_not_a_total(self):
        engine = GrowingGRUEngine(input_dim=2, h0=2, hmax=64, seed=2, arrival_budget=2, arrival_regen=5)
        self.assertEqual(engine.grow(2), 2)  # spends the whole budget
        self.assertEqual(engine.grow(1), 0)  # none left
        engine.budget.tick(5)  # one regen tick fires
        self.assertEqual(engine.budget.remaining, 1)
        self.assertEqual(engine.grow(1), 1)
        series = engine.budget.series()
        self.assertEqual(series["granted"], 3)
        self.assertEqual(series["refused"], 1)
        self.assertIn("remaining", series)


if __name__ == "__main__":
    unittest.main()
