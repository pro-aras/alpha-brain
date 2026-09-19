"""test_b8_sleep.py — B8(2): the SLEEP toy re-specified on the creature's OWN front
(docs/G4-PREREG.md §9 Amendment 1).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 23:40 +0400 — B8 (coordinator's task). Does NOT
re-grade B7's pool3 reading (it stands FAIL as written). CYCLE's toy (already passing, untouched —
27 = 0.9*30 reached, 0 births for 5 ticks, cycle() merges 25, births resume) stands as PASS per the
amendment's own words, no rerun needed.

**A/B, computed and named (gate G-a's bands, this front, first-fixation features, 40/thing over all of
world.THINGS_11, ranked by within-median minus between-median gap):** the best-separated PAIR is
square/dot (gap 0.420); the next-best pair DISJOINT from it (positions 2-4 in the ranking all re-use
"dot") is ring/bar (gap 0.309) — square/circle/ring/dot/diamond dominate the ranking because "dot" (a
small, simple mark) is unlike everything else on this front. **A = [square, dot], B = [ring, bar].**

**The no-sleep loss, measured FIRST as instructed:** two arrivals (A then B, 80 canvas showings each,
`world.stream_canvas`), Q1 on A's held-out (`world.holdout_canvas`, seed 2) before and after B. Base Q1
0.875-0.90 (3 dev-seed pairs tried: 1/2, 5/6, 11/12); final Q1 IDENTICAL to base every time — **loss =
0.0 pp at every seed pair tried**, well under the 10 pp bar. This matches Amendment 1's own prediction in
so many words: "the G0b machinery retains without sleep: budget per arrival, no disuse decay — G0b (v)
read +0". **NOT GRADABLE on this world** — skipped with the measured number, never manufactured; SLEEP's
retention mark lives only in the 24 h life's alternating windows (PREREG §5 TWINS no-sleep), not here.

One fix needed to run the toy at all: the skeleton's own `STAGE 2 meet moments 200..` never fires within
one 80-showing (160-moment) arrival, so Q1 would read 0.0 by construction (every recall NOEDGE, no
wiring ever happened) — an artifact of the toy's LENGTH, not a finding about retention. Used
`_creature_front.skeleton_genome_immediate_meet()`: the SAME front/thetas/every other gene, STAGE moved
to meet from moment 0 (see that module's docstring).
"""
from __future__ import annotations

import unittest
from typing import Dict, List

import numpy as np

from genome import world
from genome.machinery import Organism
from genome.questions import ask_glances, build_ledgers

from ._creature_front import first_fixation_feature, skeleton_genome_immediate_meet

A_THINGS = ["square", "dot"]
B_THINGS = ["ring", "bar"]
PER_THING = 80


def _held_features(genome, things: List[str], n: int, seed: int) -> Dict[str, list]:
    rng = np.random.default_rng(seed)
    hc = world.holdout_canvas(things, n, rng)
    out: Dict[str, list] = {}
    for t, rows in hc.items():
        out[t] = [[first_fixation_feature(genome, rgb, pic_id=f"{t}-{i}")] for i, (rgb, _truth) in enumerate(rows)]
    return out


def _q1(genome, org: Organism, moment_thing: dict, things: List[str], held: dict) -> float:
    ledgers = build_ledgers(org, moment_thing)
    r = ask_glances(org, ledgers, things, held, {}, genome.ear_blank_zero)
    return r["Q1"]["acc"]


def _two_arrival_no_sleep(genome, dev_seed_a: int, dev_seed_b: int, held_seed: int):
    heldA = _held_features(genome, A_THINGS, 20, seed=held_seed)
    org = Organism(genome)
    moment_thing: dict = {}

    def feed(things, seed):
        rng = np.random.default_rng(seed)
        for t, rgb, _truth in world.stream_canvas(things, PER_THING, rng):
            x = first_fixation_feature(genome, rgb, pic_id=str(org.t))
            xw = world.encode_word(t, genome.ear_blank_zero)
            moment_thing[org.t] = t
            org.moment(x, xw)

    org.new_arrival(); feed(A_THINGS, dev_seed_a)
    acc_base = _q1(genome, org, moment_thing, A_THINGS, heldA)
    org.new_arrival(); feed(B_THINGS, dev_seed_b)
    acc_final = _q1(genome, org, moment_thing, A_THINGS, heldA)
    return acc_base, acc_final


class TestB8Sleep(unittest.TestCase):
    def test_no_sleep_loss_not_gradable_on_this_world(self) -> None:
        """Measures the no-sleep loss at three independent dev-seed pairs (held-out fixed at seed=2, as
        specified). If EVERY reading is < 10 pp, this mark is NOT GRADABLE on this world — skip with the
        measured numbers, per Amendment 1's own instruction, rather than manufacture a loss."""
        genome = skeleton_genome_immediate_meet()
        readings = []
        for dev_a, dev_b in ((1, 2), (5, 6), (11, 12)):
            base, final = _two_arrival_no_sleep(genome, dev_a, dev_b, held_seed=2)
            loss_pp = 100 * (base - final)
            readings.append((dev_a, dev_b, base, final, loss_pp))
        max_loss = max(r[4] for r in readings)
        if max_loss < 10.0:
            raise unittest.SkipTest(
                f"NOT GRADABLE on this world: no-sleep loss < 10 pp at every seed pair tried "
                f"(readings [dev_a, dev_b, base, final, loss_pp]: {readings}; max loss {max_loss:.2f} pp). "
                f"G0b's machinery retains without sleep here (budget per arrival, no disuse decay). "
                f"SLEEP's retention mark lives only in the 24h life's alternating windows (PREREG §5)."
            )
        # only reached if a future change to the world/genome produces real forgetting on this front —
        # then the bar becomes gradable and this test must be replaced with the ceiling-relative one
        # Amendment 1 describes (a bar this file does not compute because it is not needed here).
        self.fail(f"loss now >= 10 pp ({readings}) — this test must be replaced by the ceiling-relative SLEEP bar")


if __name__ == "__main__":
    unittest.main()
