# edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:05 +0400 — ALPHA4-G.md task 3 (docs/ALPHA4-PREREG.md
# §2/§3): BUDGET's regenerate clause — the anti-flood LAW as a RATE, never a ceiling.
"""test_budget_regen.py — BUDGET N per arrival; regenerate <n> per <m> moments: a budget spent, no new
word, births resume at the regenerated rate; the old (regen 0) twin keeps refusing."""
from __future__ import annotations

import unittest

import numpy as np

from genome.machinery import Organism

from ._toy import mini_genome, unit


def _spend_budget_with_one_word(org: Organism, n_births: int, rng) -> None:
    """A synthetic stream: one FIXED word (so words never grows/refuses), many distinct sight vectors so
    almost every moment births — spends the budget down without ever calling new_arrival() again (a fresh
    arrival would reset it, defeating the point of this toy)."""
    xw0 = unit(rng, 208)
    for _ in range(n_births):
        org.moment(unit(rng, 64), xw0)


class TestBudgetRegen(unittest.TestCase):
    def test_old_form_keeps_refusing_after_budget_spent(self) -> None:
        """The twin: regen 0 (the old "BUDGET N per arrival" form) — once spent, refusals accumulate
        forever until the next arrival; births_regenerated stays 0."""
        org = Organism(mini_genome(budget=20))
        org.new_arrival()
        rng = np.random.default_rng(1)
        _spend_budget_with_one_word(org, 40, rng)
        self.assertEqual(org.budget_left, 0)
        self.assertGreater(org.c["births_refused_budget"], 0)
        self.assertEqual(org.budget_regenerated, 0)
        refused_at_40 = org.c["births_refused_budget"]
        _spend_budget_with_one_word(org, 200, rng)
        self.assertGreater(org.c["births_refused_budget"], refused_at_40, "refusals must keep piling up -- no regeneration under the old form")
        self.assertEqual(org.budget_regenerated, 0)

    def test_regen_form_resumes_births_after_budget_spent(self) -> None:
        """The real thing: BUDGET 20 per arrival; regenerate 1 per 5 moments. Spend the budget, then feed
        moments past several regeneration boundaries -- births must resume (novelty birth succeeds again
        once budget_left > 0), and budget_regenerated counts each unit."""
        org = Organism(mini_genome(budget=20, budget_regen=(1, 5)))
        org.new_arrival()
        rng = np.random.default_rng(2)
        _spend_budget_with_one_word(org, 40, rng)   # budget exhausted quickly, refusals accumulate
        # NOTE: regeneration is a continuous rate ("never a ceiling"), so it fires DURING this same
        # spend phase too (every 5 moments) -- budget_left need not land at exactly 0, only near it, well
        # under the full 20 (spending -- 1/moment on a near-orthogonal stream -- vastly outpaces 1/5).
        self.assertLess(org.budget_left, 20)
        refused_after_spend = org.c["births_refused_budget"]
        self.assertGreater(refused_after_spend, 0, "spending 1/moment against regen of 1/5 moments must still outpace it and cause real refusals")
        # feed moments (fixed word -> no births consumed by wiring the SAME word again) so t advances past
        # many regeneration boundaries without spending the newly-regenerated budget on THIS same loop
        xw0 = unit(np.random.default_rng(99), 208)
        xs_repeat = unit(np.random.default_rng(100), 64)
        org.moment(xs_repeat, xw0)   # birth once (novel) -- costs 1 of whatever just regenerated, harmless
        moments_before = org.t
        for _ in range(300):
            org.moment(xs_repeat, xw0)   # SAME vectors every time -> resonates, never births, never spends budget
        self.assertGreater(org.t, moments_before)
        self.assertGreater(org.budget_regenerated, 0, "regeneration must have fired at least once over 300 idle moments at every-5")
        self.assertGreater(org.budget_left, 0, "budget_left must have climbed back above 0")
        # NOW feed fresh novel vectors -- a birth must succeed again (not refused), proving regeneration
        # actually unblocks the birth budget, not just the counter
        refused_before_resume = org.c["births_refused_budget"]
        sight_before = org.sight.n
        for _ in range(5):
            org.moment(unit(rng, 64), xw0)
        self.assertGreater(org.sight.n, sight_before, "a novel vector must birth again once budget regenerated")
        self.assertEqual(org.c["births_refused_budget"], refused_before_resume, "no NEW refusals once budget is available again")

    def test_regen_never_exceeds_the_arrival_ceiling(self) -> None:
        """`budget_left < budget` gates the regen tick -- it must never push budget_left past the genome's
        own per-arrival BUDGET value (a rate, never a ceiling ITSELF pushed past its own declared max)."""
        org = Organism(mini_genome(budget=5, budget_regen=(100, 1)))   # absurdly fast regen, to try to overshoot
        org.new_arrival()
        rng = np.random.default_rng(3)
        xw0 = unit(rng, 208)
        for _ in range(50):
            org.moment(unit(rng, 64), xw0)
        self.assertLessEqual(org.budget_left, 5)

    def test_regen_ticks_on_moment_sight_too(self) -> None:
        """moment_sight() (a sight-only moment, no MEET) shares the tail's homeostasis tick."""
        org = Organism(mini_genome(budget=5, budget_regen=(1, 3)))
        org.new_arrival()
        rng = np.random.default_rng(4)
        for _ in range(20):
            org.moment_sight(unit(rng, 64))
        self.assertGreater(org.budget_regenerated, 0)

    def test_new_arrival_still_resets_to_full_budget(self) -> None:
        """new_arrival()'s own law is unchanged: a fresh arrival resets budget_left to the full per-arrival
        BUDGET regardless of any regeneration in progress."""
        org = Organism(mini_genome(budget=20, budget_regen=(1, 5)))
        org.new_arrival()
        rng = np.random.default_rng(5)
        _spend_budget_with_one_word(org, 40, rng)
        self.assertLess(org.budget_left, 20)
        org.new_arrival()
        self.assertEqual(org.budget_left, 20)


if __name__ == "__main__":
    unittest.main()
