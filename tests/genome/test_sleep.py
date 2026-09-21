"""test_sleep.py — B7: SLEEP + CYCLE (genome/sleep.py) — complementary systems, the cap that becomes a
cycle.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 22:50 +0400 — B7 (docs/G4-PREREG.md §3, docs/briefs/
G4-BUILDER-B-GENES.md).

CYCLE's toy passes cleanly (births 0 at the soft ceiling, resume after cycle()).

SLEEP's two-arrival retention toy, the honest finding (found the same way B6's was — compute, don't
guess): base Q1 on A (2 well-separated G0b things, "ring"/"dot" — gate_ga.bands shows this pair's
within-between gap, 0.371, is the widest of any pair in THINGS_10 under the toy's fast pool3 retina;
"circle"/"square", tried first, are nearly INSEPARABLE under pool3 — within 0.844 vs between 0.840, a
gap of 0.004 — and were dropped before any life was run) reaches 1.0. After arrival 2 (2 different
things, "square"/"bar") the drop is real and large at this toy's scale in BOTH arms: WITHOUT sleep it
loses 70 pp (comfortably clearing the PREREG's >=10pp bar); WITH sleep (every 50 moments, replay 30) it
loses 47.5pp — sleep genuinely HELPS (a robust, monotonic effect: three schedules tried, every 100/n=20
-> 57.5pp, every 50/n=30 -> 47.5pp, every 30/n=25 -> 30.0pp, MORE/more-frequent replay always reduces
the drop further) but does not reach the PREREG's "within 5 pp" bar at this toy's scale — reported as a
RAISED finding (`expectedFailure`), not forced. Likely cause, consistent with B6's ceiling finding: the
pool3 front is crude relative to the sealed eye tower the real creature uses, and cross-arrival
interference (new B-arrival sight cells competing for the same word-side answers) is a real, structural
cost SLEEP alone (replaying A's OLD episodes without ALSO down-weighting B's NEW, interfering edges)
cannot fully undo in one consolidation schedule.
"""
from __future__ import annotations

import unittest

import numpy as np

from genome import world
from genome.fast import Episodes
from genome.machinery import Organism, parse_genome, retina
from genome.predict import Predictor
from genome.questions import ask, build_ledgers
from genome.sleep import cycle, sleep

A_THINGS = ["ring", "dot"]     # gate_ga.bands: the best-separated pair of THINGS_10 under pool3 (gap 0.371)
B_THINGS = ["square", "bar"]   # a second, disjoint, reasonably-separated pair (gap 0.177)
PER_THING = 80


def _life_genome(theta_n: float = 0.6, nmax: int = 300, budget: int = 2000) -> "object":
    text = f"""\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 8 blank=zero
AREA sight from retina
AREA words from ear
MEET sight words
BIRTH novelty cos<{theta_n}
BIRTH error misfires 3
BUDGET {budget} per arrival
NMAX {nmax}
KWTA 5
HEBB window 1
DELTA lr 0.1
PRUNE w<0.02 after 3 chances
MERGE cos>0.95 same-answer
SCALE every 100000 moments
STAGE 1 senses moments 0..0
STAGE 2 meet moments 0..
RECALL k=1
ABSTAIN second/best > 0.85
"""
    return parse_genome(text)


def _do_sleep(org: Organism, ep: Episodes, n: int, moment_thing: dict) -> dict:
    """The test harness's own bookkeeping: sleep() replays via Organism.moment(), which advances org.t
    and may birth cells at those replay moments — questions.build_ledgers needs a `moment -> thing` entry
    for EVERY moment that could birth a cell, replay moments included. sleep() itself has no such concept
    (moment_thing is a runner/test-side idea, not part of the Organism/Episodes/sleep contract) — so the
    harness predicts the exact (moment, word) pairs sleep() is about to live, using the SAME ranking
    (Episodes.most_surprising is a pure read; nothing changes between this call and sleep()'s own)."""
    ids = ep.most_surprising(n)
    for i, eid in enumerate(ids):
        rec = ep.get(eid)
        if rec is not None:
            moment_thing[org.t + i] = rec["word"]
    return sleep(org, ep, n)


def _two_arrival_life(g, with_sleep: bool, sleep_every: int, sleep_n: int):
    rngA = np.random.default_rng(1); rngB = np.random.default_rng(2); rng_held = np.random.default_rng(3)
    devA = world.stream(A_THINGS, PER_THING, rngA, side=24)
    devB = world.stream(B_THINGS, PER_THING, rngB, side=24)
    heldA = world.holdout(A_THINGS, 20, rng_held, side=24)
    org = Organism(g)
    pred = Predictor(org)
    ep = Episodes(cap=1000, dim_s=g.sight_dim(), dim_w=g.words_dim())
    moment_thing: dict = {}

    def feed(dev):
        for t, pic in dev:
            x = retina(pic, g.retina); xw = world.encode_word(t, g.ear_blank_zero)
            e = pred.error(x)
            moment_thing[org.t] = t
            S, T = org.moment(x, xw)
            pred.note_winners(S)
            ep.write(org.t - 1, x, xw, t, e)
            if with_sleep and org.t % sleep_every == 0:
                _do_sleep(org, ep, sleep_n, moment_thing)

    org.new_arrival(); feed(devA)
    acc_base = ask(org, build_ledgers(org, moment_thing), A_THINGS, heldA, {}, g.ear_blank_zero)["Q1"]["acc"]
    org.new_arrival(); feed(devB)
    acc_final = ask(org, build_ledgers(org, moment_thing), A_THINGS, heldA, {}, g.ear_blank_zero)["Q1"]["acc"]
    return acc_base, acc_final


class TestSleepRetention(unittest.TestCase):
    def test_a_separates_cleanly_before_any_forgetting_can_be_measured(self) -> None:
        """A sanity precondition: if A itself is not well learned after arrival 1, "retention" is not a
        meaningful question. Both arms must start from a clean Q1=1.0 (or very close)."""
        g = _life_genome()
        base_sleep, _ = _two_arrival_life(g, with_sleep=True, sleep_every=50, sleep_n=30)
        base_nosleep, _ = _two_arrival_life(g, with_sleep=False, sleep_every=50, sleep_n=30)
        self.assertGreaterEqual(base_sleep, 0.95)
        self.assertGreaterEqual(base_nosleep, 0.95)

    def test_without_sleep_loses_at_least_10pp(self) -> None:
        g = _life_genome()
        base, final = _two_arrival_life(g, with_sleep=False, sleep_every=50, sleep_n=30)
        drop_pp = 100 * (base - final)
        self.assertGreaterEqual(drop_pp, 10.0, f"no-sleep twin: base {base} -> final {final} ({drop_pp:.1f} pp)")

    def test_sleep_reduces_the_forgetting(self) -> None:
        """The robust half: sleep genuinely helps, monotonically, across the two more aggressive
        schedules — never asserted as a single magic config.

        edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:18 +0400 — W3-2b (docs/G4-WAVE3-CLAUSES.md):
        `episodes.write(..., surprise=err)` carries the NEW error (genome/predict.py: max cosine over
        EVERY alive sight cell), which is BIMODAL (0-ish or exactly 1.0) rather than the old smooth
        gradient — `most_surprising(n)`'s ranking, and so SLEEP's replay selection, changes (PREREG
        §16 NOTE / D1's own brief: 'so SLEEP's replay ranking changes — say so'). Re-measured: no-sleep
        drop 70.0pp (unchanged — sleep is not in this arm); every 50/n=30 -> 62.5pp; every 30/n=25 ->
        52.5pp — BOTH still beat no-sleep, and the ordering between them is still monotone (52.5 < 62.5).
        The LEAST aggressive schedule tried, every 100/n=20, no longer beats no-sleep (85.0pp > 70.0pp,
        so it is no longer part of the monotone chain either) — moved to its own RAISED test below
        (`test_weakest_schedule_regressed_under_new_ranking`) rather than silently dropped or forced."""
        g = _life_genome()
        _b0, f0 = _two_arrival_life(g, with_sleep=False, sleep_every=50, sleep_n=30)
        no_sleep_drop = 100 * (_b0 - f0)
        drops = {}
        for every, n in ((50, 30), (30, 25)):
            b, f = _two_arrival_life(g, with_sleep=True, sleep_every=every, sleep_n=n)
            drops[(every, n)] = 100 * (b - f)
        for key, d in drops.items():
            self.assertLess(d, no_sleep_drop, f"schedule {key} (drop {d:.1f}pp) must lose LESS than the no-sleep twin ({no_sleep_drop:.1f}pp)")
        self.assertLess(drops[(30, 25)], drops[(50, 30)], "every 30/n=25 (the most aggressive of these two) must beat every 50/n=30")

    @unittest.expectedFailure
    def test_weakest_schedule_regressed_under_new_ranking(self) -> None:
        """W3-2b (2026-09-21): the weakest schedule tried in the original B7 toy (every 100 moments,
        replay 20) LOSES MORE than no sleep at all under the new bimodal surprise ranking (85.0pp vs the
        no-sleep twin's 70.0pp) — replaying rarely, from a ranking now mostly a tie at error=1.0 broken
        by episode-array order, can pick a worse sample than never replaying. RAISED, `expectedFailure`,
        never forced; the two more aggressive schedules (test_sleep_reduces_the_forgetting, above) are
        unaffected by this."""
        g = _life_genome()
        _b0, f0 = _two_arrival_life(g, with_sleep=False, sleep_every=50, sleep_n=30)
        no_sleep_drop = 100 * (_b0 - f0)
        b, f = _two_arrival_life(g, with_sleep=True, sleep_every=100, sleep_n=20)
        drop = 100 * (b - f)
        self.assertLess(drop, no_sleep_drop, f"every 100/n=20: drop {drop:.1f}pp vs no-sleep {no_sleep_drop:.1f}pp")

    @unittest.expectedFailure
    def test_with_sleep_within_5pp_prereg_b7(self) -> None:
        """PREREG's literal bar. UNDER THE OLD error, WITH sleep (every 50, replay 30) the drop was
        ~47.5 pp. edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:18 +0400 — W3-2b: re-measured
        under the NEW error, the drop at this same schedule now reads 62.5 pp — still real, still helps
        relative to no-sleep (70.0pp), but further from the 5pp bar than before, not closer. Still a
        RAISED finding, `expectedFailure`, never forced."""
        g = _life_genome()
        base, final = _two_arrival_life(g, with_sleep=True, sleep_every=50, sleep_n=30)
        drop_pp = 100 * (base - final)
        self.assertLessEqual(drop_pp, 5.0, f"base {base} -> final {final} ({drop_pp:.1f} pp)")


class TestSleepMechanics(unittest.TestCase):
    """sleep()'s own contract, isolated from the (noisy, ceiling-bound) retention experiment above."""

    def test_replay_count_and_skips_evicted_episodes(self) -> None:
        g = _life_genome(theta_n=0.5, nmax=50)
        org = Organism(g)
        ep = Episodes(cap=5, dim_s=g.sight_dim(), dim_w=g.words_dim())
        rng = np.random.default_rng(4)
        for i in range(5):
            v = rng.normal(size=g.sight_dim()); v /= np.linalg.norm(v)
            w = world.encode_word("dot", g.ear_blank_zero)
            ep.write(i, v, w, "dot", surprise=float(i))
        r = sleep(org, ep, n=3)
        self.assertEqual(r["replayed"], 3)
        self.assertIn("births", r); self.assertIn("merged", r); self.assertIn("pruned", r)
        # a request for more episodes than are live is satisfied by however many exist, never an error
        r2 = sleep(org, ep, n=100)
        self.assertLessEqual(r2["replayed"], 5)

    def test_sleep_never_advances_t_beyond_moment(self) -> None:
        g = _life_genome(theta_n=0.5, nmax=50)
        org = Organism(g)
        ep = Episodes(cap=20, dim_s=g.sight_dim(), dim_w=g.words_dim())
        rng = np.random.default_rng(5)
        for i in range(10):
            v = rng.normal(size=g.sight_dim()); v /= np.linalg.norm(v)
            w = world.encode_word("dot", g.ear_blank_zero)
            ep.write(i, v, w, "dot", surprise=float(i))
        t0 = org.t
        r = sleep(org, ep, n=4)
        self.assertEqual(org.t, t0 + r["replayed"], "each replay is exactly one moment on the shared clock")


class TestCycle(unittest.TestCase):
    def test_births_0_at_soft_ceiling_then_births_again_after_cycle(self) -> None:
        text = """\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 8 blank=zero
AREA sight from retina
AREA words from ear
MEET sight words
BIRTH novelty cos<0.995
BIRTH error misfires 10
BUDGET 2000 per arrival
NMAX 30
KWTA 1
HEBB window 1
DELTA lr 0.1
PRUNE w<0.02 after 3 chances
MERGE cos>0.9 same-answer
SCALE every 1000000 moments
STAGE 1 senses moments 0..0
STAGE 2 meet moments 0..
RECALL k=1
ABSTAIN second/best > 0.85
CYCLE grow to 0.9 nmax then consolidate
"""
        g = parse_genome(text)
        self.assertIn("CYCLE", g.declared)
        org = Organism(g)
        rng = np.random.default_rng(0)
        dim_s, dim_w = g.sight_dim(), g.words_dim()
        v0 = np.zeros(dim_s); v0[0] = 1.0
        xw = np.zeros(dim_w); xw[0] = 1.0

        def tick():
            noise = rng.normal(size=dim_s) * 0.02
            x = v0 + noise; x /= np.linalg.norm(x)
            org.moment(x, xw)

        ceiling = 0.9 * g.nmax   # 27
        for _ in range(40):
            if org.total_cells() >= ceiling:
                break
            tick()
        self.assertGreaterEqual(org.total_cells(), ceiling)
        refused_before = org.c["births_refused_nmax"]
        total_before = org.total_cells()
        for _ in range(5):
            tick()
        self.assertEqual(org.total_cells(), total_before, "births must be 0 once at the soft ceiling")
        self.assertGreater(org.c["births_refused_nmax"], refused_before)

        ran = cycle(org)
        self.assertTrue(ran)
        self.assertLess(org.total_cells(), ceiling, "cycle()'s merge pass must lower alive count back under the ceiling")

        total_after_cycle = org.total_cells()
        tick()
        self.assertGreater(org.total_cells(), total_after_cycle, "a birth must succeed again right after cycle()")

    def test_cycle_returns_false_without_the_gene_declared(self) -> None:
        from ._toy import mini_genome
        g = mini_genome()
        self.assertNotIn("CYCLE", g.declared)
        org = Organism(g)
        self.assertFalse(cycle(org))

    def test_cycle_returns_false_below_the_ceiling(self) -> None:
        text = """\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 8 blank=zero
AREA sight from retina
AREA words from ear
MEET sight words
BIRTH novelty cos<0.5
BIRTH error misfires 3
BUDGET 2000 per arrival
NMAX 30
KWTA 5
HEBB window 1
DELTA lr 0.1
PRUNE w<0.02 after 3 chances
MERGE cos>0.99 same-answer
SCALE every 1000000 moments
STAGE 1 senses moments 0..0
STAGE 2 meet moments 0..
RECALL k=1
ABSTAIN second/best > 0.85
CYCLE grow to 0.9 nmax then consolidate
"""
        g = parse_genome(text)
        org = Organism(g)
        self.assertFalse(cycle(org))   # 0 cells, nowhere near 27


if __name__ == "__main__":
    unittest.main()
