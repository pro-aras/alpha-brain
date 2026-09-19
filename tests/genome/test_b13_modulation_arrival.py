"""test_b13_modulation_arrival.py — B13 (docs/G4-PREREG.md §10 Amendment 2, §11.2's "wave 2 opening"
toy): MODULATION re-specified as SURPRISE AT ARRIVAL, on the creature's own front.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — new file, Wave 2 B13.

PREREG §10 (verbatim, the mark): "at every window change that brings NEW things ..., the median error
over the first 3 showings of each new thing >= 3x the median error over the previous window's last 50
showings, AND it falls under F + 0.05 within 10 showings of that thing." Null: a window change bringing
NO new things must show no such spike (< 1.5x). Ceiling: "a new thing's first showing has error
1 - cos(its glance, the nearest existing cell) <= 1 - between-p95 ... printed from the gate's bands
beside the bar — if the tower front's between-p95 makes a new thing look like an old one ..., the
spike's ceiling is below 3x F and the mark is reported against THAT ceiling, not the 3x." Toy version
(this file): "3 things x 50 showings then 2 NEW things — the spike and the settle, at 3 seeds, with the
no-new-things null."

**Stream design** (a genuine ambiguity the PREREG leaves to the builder, decided and documented here):
window 1 = circle/square/triangle, 50 jittered showings each (150 total), SHUFFLED across the whole
window (not per-thing blocks) — so the baseline ("the previous window's last 50 showings") already
reflects the ordinary noise of a mind that keeps re-predicting a DIFFERENT thing's cell whenever the
stream switches identity, and a genuine arrival has to stand out above THAT, not above a artificially
clean F. Window 2 (the REAL arm) = moon/house (world.THINGS_ARRIVAL2[:2]), interleaved and shuffled,
15 showings each (30 total) — each new thing's OWN showing sequence is tracked separately (so "first 3
showings of each new thing" and "within 10 showings of that thing" are per-thing, not per-canvas-index).
Window 2' (the NULL arm) = circle/square/triangle again (10 more showings each, 30 total, freshly
jittered, shuffled) — a window change that brings NO new things.

**F and the ceiling, measured first (gate G-a's bands, this front, this world):** F = 0.0310
(circle/square/triangle, within-median 0.9690 — the same reading as B8's, this is the same front and
the same three things). Ceiling = 1 - between-p95 over all five things (circle/square/triangle/moon/
house) = 0.0521 (between-p95 = 0.9479). **Ceiling (0.0521) < 3xF (0.0930)** — exactly the case the
PREREG's own text names: the spike's ceiling is below 3x F, so the bar is reported against the ceiling
ratio (ceiling/F = 1.68x) rather than the literal 3x, per the PREREG's own instruction.

**The honest finding, measured not guessed, at 3 seeds x 2 new things = 6 (seed, thing) pairs:**
  spike >= ceiling-ratio (1.68x): 5/6 clear (seed 9 moon 1.82x, house 1.76x; seed 10 moon 2.65x,
    house 1.97x; seed 11 house 2.42x; seed 11 moon 0.59x is the one miss — its error actually fell).
    A majority — PASSES.
  settle (< F+0.05=0.0810 by the thing's 10th showing): EXACTLY 3/6 (seed 10 both: 0.055, 0.014; seed
    11 moon 0.079, barely; the other three sit at 0.20-0.36, still elevated at showing 10) — a TIE, not
    a majority. RAISED, `expectedFailure`.
  CONJUNCTIVE (spike-vs-ceiling AND settle, i.e. the PREREG's own "AND"): 2/6 — seed 10's two new
    things only. NOT a majority. RAISED, `expectedFailure`.
  null (< 1.5x, PREREG's own literal number, at 3 seeds): 2/3 clear (seed 10: 1.13x, seed 11: 0.56x;
    seed 9: 1.67x MISSES — the shuffled old-things baseline is itself noisy enough that one seed's
    "no new things" window already reads above 1.5x).
Two components (spike-vs-ceiling, null-majority) individually clear their own bars; settle and the
literal conjunction do not — reported honestly, not forced.
"""
from __future__ import annotations

import unittest
from typing import Dict, List, Tuple

import numpy as np

from genome import gate_ga, world
from genome.machinery import Organism
from genome.predict import Predictor

from ._creature_front import first_fixation_feature, skeleton_genome

OLD = ["circle", "square", "triangle"]
NEW = list(world.THINGS_ARRIVAL2[:2])  # ["moon", "house"]
SEEDS = (9, 10, 11)


def _F_and_ceiling(seed: int = 100, per_thing: int = 40) -> Tuple[float, float, Dict, Dict]:
    genome = skeleton_genome()
    rng = np.random.default_rng(seed)
    feats = {}
    for t in OLD + NEW:
        rows = []
        for _ in range(per_thing):
            rgb, _truth = world.render_canvas(t, rng)
            rows.append(first_fixation_feature(genome, rgb, pic_id=f"{t}-{len(rows)}"))
        feats[t] = np.stack(rows)
    b_old = gate_ga.bands_feats({k: feats[k] for k in OLD}, np.random.default_rng(seed + 1))
    F = 1.0 - b_old["within"]["median"]
    b_all = gate_ga.bands_feats(feats, np.random.default_rng(seed + 2))
    ceiling = 1.0 - b_all["between"]["p95"]
    return F, ceiling, b_old, b_all


def _window_stream(rng: np.random.Generator, things: List[str], per_thing: int) -> List[Tuple[str, np.ndarray]]:
    seq = []
    for t in things:
        for _ in range(per_thing):
            rgb, _truth = world.render_canvas(t, rng)
            seq.append((t, rgb))
    rng.shuffle(seq)
    return seq


def _feed(genome, org: Organism, pred: Predictor, seq: List[Tuple[str, np.ndarray]]) -> Tuple[List[float], List[str]]:
    errs: List[float] = []
    order: List[str] = []
    for t, rgb in seq:
        x = first_fixation_feature(genome, rgb, pic_id=f"{t}-{len(errs)}")
        e = pred.error(x)
        errs.append(e); order.append(t)
        xw = world.encode_word(t, genome.ear_blank_zero)
        S, T = org.moment(x, xw)
        pred.note_winners(S)
    return errs, order


def _run_seed(seed: int) -> Dict[str, object]:
    genome = skeleton_genome()
    org = Organism(genome)
    pred = Predictor(org)
    rng = np.random.default_rng(seed)

    w1 = _window_stream(rng, OLD, 50)          # 150 showings, the arrival's "previous window"
    w2_real = _window_stream(rng, NEW, 15)     # 30 showings, 2 NEW things, interleaved
    rng_null = np.random.default_rng(seed + 1000)
    w2_null = _window_stream(rng_null, OLD, 10)  # 30 showings, NO new things

    errs1, _order1 = _feed(genome, org, pred, w1)
    last50_med = float(np.median(errs1[-50:]))

    errs2r, order2r = _feed(genome, org, pred, w2_real)
    per_thing: Dict[str, List[float]] = {t: [e for e, o in zip(errs2r, order2r) if o == t] for t in NEW}
    real: Dict[str, Dict[str, float]] = {}
    for t in NEW:
        e = per_thing[t]
        first3 = float(np.median(e[:3]))
        real[t] = {
            "first3_med": first3,
            "spike": (first3 / last50_med) if last50_med > 0 else float("inf"),
            "e_at_10": e[9] if len(e) > 9 else None,
        }

    errs2n, _order2n = _feed(genome, org, pred, w2_null)
    null_first3 = float(np.median(errs2n[:3]))
    null_spike = (null_first3 / last50_med) if last50_med > 0 else float("inf")

    return {"seed": seed, "last50_med": last50_med, "real": real, "null_spike": null_spike}


def _all_results() -> List[Dict[str, object]]:
    return [_run_seed(s) for s in SEEDS]


class TestFAndCeiling(unittest.TestCase):
    def test_F_and_ceiling_below_3x(self) -> None:
        F, ceiling, b_old, b_all = _F_and_ceiling()
        print(f"[B13] F={F:.4f} (within-median {b_old['within']['median']:.4f}) "
              f"ceiling={ceiling:.4f} (between-p95 over 5 things {b_all['between']['p95']:.4f}) "
              f"3xF={3 * F:.4f} ceiling/F={ceiling / F:.3f}x")
        self.assertAlmostEqual(F, 0.0310, delta=0.005)
        self.assertLess(ceiling, 3 * F, "expected this front's ceiling to sit below the literal 3x bar")


class TestSpikeVsCeiling(unittest.TestCase):
    def test_spike_vs_ceiling_majority_clears(self) -> None:
        F, ceiling, _b_old, _b_all = _F_and_ceiling()
        bar_ratio = ceiling / F  # ~1.68x — the PREREG's own "report against the ceiling" instruction
        results = _all_results()
        pairs = []
        for r in results:
            for t in NEW:
                pairs.append((r["seed"], t, r["real"][t]["spike"]))
        for seed, t, spike in pairs:
            print(f"[B13] seed={seed} thing={t} spike={spike:.3f} vs ceiling-ratio={bar_ratio:.3f}")
        cleared = sum(1 for _s, _t, sp in pairs if sp >= bar_ratio)
        print(f"[B13] spike-vs-ceiling: {cleared}/{len(pairs)} clear")
        self.assertGreater(cleared, len(pairs) / 2, f"spike-vs-ceiling not a majority: {pairs}")


class TestSettleAndConjunction(unittest.TestCase):
    @unittest.expectedFailure
    def test_settle_under_F_plus_005_within_10_showings(self) -> None:
        """Measured: exactly 3 of 6 (seed, new-thing) pairs settle under F+0.05 by the thing's 10th
        showing — a TIE, not a majority (module docstring has every number). RAISED, expectedFailure."""
        F, _ceiling, _b_old, _b_all = _F_and_ceiling()
        threshold = F + 0.05
        results = _all_results()
        hits = []
        for r in results:
            for t in NEW:
                e10 = r["real"][t]["e_at_10"]
                hits.append((r["seed"], t, e10, e10 is not None and e10 < threshold))
        for seed, t, e10, ok in hits:
            print(f"[B13] seed={seed} thing={t} e_at_10={e10} settled(<{threshold:.4f})={ok}")
        cleared = sum(1 for *_r, ok in hits if ok)
        print(f"[B13] settle-within-10: {cleared}/{len(hits)} clear")
        self.assertGreater(cleared, len(hits) / 2, f"settle-within-10 not a majority: {hits}")

    @unittest.expectedFailure
    def test_conjunctive_bar_prereg_b13(self) -> None:
        """The PREREG's literal "AND": spike >= ceiling-ratio AND settled by showing 10. Measured:
        2 of 6 (seed, new-thing) pairs clear both — NOT a majority (module docstring has every number).
        RAISED: the two component bars each individually clear on their own majority (spike-vs-ceiling
        5/6, null 2/3) but rarely land on the SAME (seed, thing) pair as the settle requirement, on
        this small a toy (3 seeds x 2 new things = 6 trials)."""
        F, ceiling, _b_old, _b_all = _F_and_ceiling()
        bar_ratio = ceiling / F
        threshold = F + 0.05
        results = _all_results()
        both = []
        for r in results:
            for t in NEW:
                spike = r["real"][t]["spike"]
                e10 = r["real"][t]["e_at_10"]
                ok = spike >= bar_ratio and e10 is not None and e10 < threshold
                both.append(ok)
        cleared = sum(both)
        self.assertGreater(cleared, len(both) / 2, f"conjunctive bar: {cleared}/{len(both)}")


class TestNoNewThingsNull(unittest.TestCase):
    def test_null_majority_under_1_5x(self) -> None:
        results = _all_results()
        for r in results:
            print(f"[B13] seed={r['seed']} null_spike={r['null_spike']:.3f} (bar < 1.5x)")
        cleared = sum(1 for r in results if r["null_spike"] < 1.5)
        print(f"[B13] null under 1.5x: {cleared}/{len(results)}")
        self.assertGreaterEqual(cleared, 2, f"null spikes: {[r['null_spike'] for r in results]}")


if __name__ == "__main__":
    unittest.main()
