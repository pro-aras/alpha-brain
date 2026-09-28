# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 20:00 +0400 — A3's required positive
#   control (B1-PREREG.md §5.5 (0b)) plus a negative control, empirically chosen the same way
#   A2's was after its first design turned out wrong: a full 2-CLASS argmax comparison (two
#   independent clause banks, decision = argmax of their votes) reconstructs XOR even at C=2
#   (confirmed by a scratch run before this file was written — the same "extra degrees of
#   freedom from comparing two independently-trained scorers" shape as
#   tests/brain/arms_logic/test_xor_toy.py's corrected negative control). The airtight control
#   drops to a SINGLE bank whose OWN vote-sign (not compared against a second bank) makes the
#   decision: empirically, C=2 (one positive + one negative clause) caps at EXACTLY 0.75 across
#   three seeds, and C>=8 reliably reaches 1.0 — the same textbook Minsky-Papert 0.75 ceiling
#   this corpus's other two engines' negative controls also land on, for a different structural
#   reason each time.
import os
import sys
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.clauses.engine import TsetlinClauseBank, new_generator  # noqa: E402

XOR_X = [torch.tensor([0.0, 0.0]), torch.tensor([0.0, 1.0]), torch.tensor([1.0, 0.0]), torch.tensor([1.0, 1.0])]
XOR_Y = [0, 1, 1, 0]


def _train_two_class(C: int, seed: int, epochs: int = 300, N=100, T=15, s=3.9):
    bank0 = TsetlinClauseBank(2, C, N, T, s, seed, "toy_c0")
    bank1 = TsetlinClauseBank(2, C, N, T, s, seed + 1000, "toy_c1")
    best = 0.0
    for ep in range(epochs):
        for i, (x, y) in enumerate(zip(XOR_X, XOR_Y)):
            gen = new_generator(seed, "tm", ep * 4 + i)
            bank0.train(x, y_c=(y == 0), gen=gen)
            bank1.train(x, y_c=(y == 1), gen=gen)
        correct = 0
        for x, y in zip(XOR_X, XOR_Y):
            pred = 0 if int(bank0.vote(x)) >= int(bank1.vote(x)) else 1
            correct += int(pred == y)
        best = max(best, correct / 4)
    return best, bank0, bank1


def _train_single_bank_vote_sign(C: int, seed: int, epochs: int = 300, N=100, T=15, s=3.9):
    bank = TsetlinClauseBank(2, C, N, T, s, seed, "toy_single")
    best = 0.0
    for ep in range(epochs):
        for i, (x, y) in enumerate(zip(XOR_X, XOR_Y)):
            gen = new_generator(seed, "tm", ep * 4 + i)
            bank.train(x, y_c=bool(y), gen=gen)
        correct = sum(int((1 if int(bank.vote(x)) > 0 else 0) == y) for x, y in zip(XOR_X, XOR_Y))
        best = max(best, correct / 4)
    return best


class TestA3XorToy(unittest.TestCase):
    def test_two_class_argmax_solves_xor_100_percent(self):
        best, _, _ = _train_two_class(C=20, seed=20261001)
        self.assertEqual(best, 1.0, f"A3's 2-class Tsetlin machine must solve XOR at 100%%, got {best}")

    def test_negative_control_single_bank_c2_caps_at_0_75(self):
        for seed in (1, 2, 3):
            best = _train_single_bank_vote_sign(C=2, seed=seed)
            self.assertLessEqual(best, 0.75 + 1e-9, f"seed {seed}: a single C=2 bank must not exceed the 0.75 ceiling")
        self.assertTrue(
            any(_train_single_bank_vote_sign(C=2, seed=s) >= 0.75 - 1e-9 for s in (1, 2, 3)),
            "at least one seed should reach the achievable 0.75 ceiling",
        )

    def test_negative_control_positive_control_ceiling_recovers_with_more_clauses(self):
        # the SAME single-bank harness, given enough clauses, must recover 100% — proving the
        # 0.75 cap above is a capacity limit of C=2, not a bug in the training rule itself.
        best = _train_single_bank_vote_sign(C=20, seed=1)
        self.assertEqual(best, 1.0)

    def test_determinism_same_seed_same_trajectory(self):
        _, b0a, b1a = _train_two_class(C=6, seed=42, epochs=20)
        _, b0b, b1b = _train_two_class(C=6, seed=42, epochs=20)
        self.assertTrue(torch.equal(b0a.state, b0b.state), "same seed must give byte-identical clause states")
        self.assertTrue(torch.equal(b1a.state, b1b.state))

    def test_vacuous_clause_convention_train_vs_predict(self):
        # PREREG's own convention: a clause with NO included literals fires (1) during
        # training, never (0) during prediction — pinned directly, not inferred from a
        # trained model's incidental behaviour.
        bank = TsetlinClauseBank(2, 2, 100, 15, 3.9, seed=1, site="vacuous_test")
        self.assertTrue(torch.equal(bank.state, torch.full_like(bank.state, 50)), "init must start borderline-excluded")
        out_train = bank.clause_outputs(torch.tensor([0.0, 1.0]), training=True)
        out_pred = bank.clause_outputs(torch.tensor([0.0, 1.0]), training=False)
        self.assertTrue(bool((out_train == 1).all()), "every clause is vacuous at init: must fire (1) in TRAINING")
        self.assertTrue(bool((out_pred == 0).all()), "every clause is vacuous at init: must NOT fire (0) in PREDICTION")


if __name__ == "__main__":
    unittest.main()
