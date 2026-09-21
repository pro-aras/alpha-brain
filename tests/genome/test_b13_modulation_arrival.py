"""test_b13_modulation_arrival.py — B13 re-run (docs/G4-WAVE3-CLAUSES.md, W3-2's NOTE; docs/G4-PREREG.md
§10 Amendment 2, §16 addendum 1): MODULATION as SURPRISE AT ARRIVAL, re-read on genome/predict.py's NEW
error() — W3-2b, the nearest RESONATING cell's cosine over EVERY alive sight cell (genome/predict.py's
own docstring), not the OLD `expect()` (a single remembered last-winner). This REPLACES the file's
earlier content (kept only in git history) rather than layering a second apparatus beside it — the point
of W3-2b is that the bars are the LITERAL PREREG ones again, with no per-front ceiling relaxation needed:
the earlier version built an elaborate `ceiling_bands`/per-thing-ceiling machinery specifically BECAUSE
the old error's steady-state baseline (~.09-.11 under window-1 shuffling) sat too close to 3xF for the
literal bar to be meaningful; W3-2b's error has a completely different SHAPE (see below), so re-using
that apparatus would misdescribe the new signal, not describe it honestly.

edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:xx +0400 — D1 (docs/briefs/W3-BUILDER-D.md): re-run
with the new error, the SAME bars the brief states verbatim (matching §16 addendum 1 exactly): spike =
median error over a new thing's first 3 showings >= 3x the median error over the 50 canvases before the
arrival; settle = the 10th showing's error <= 1.25x that SAME pre-arrival median (not F+0.05 — §16
addendum 1 replaced that toy-front arithmetic); graded as a MAJORITY of the window's new things (the
conjunction, spike AND settle, per thing); null = a FAKE boundary in the MIDDLE of ONE window of OLD
things (things continuing throughout — PREREG §16 addendum 1's own words, quoted there from Amendment 2
§10) must show no spike, every ratio < 1.5.

**The honest finding, measured not guessed (3 seeds x 2 new things = 6 (seed, thing) pairs):** the new
error is BIMODAL by construction (genome/predict.py's law: either a cell resonates, error in
[0, 1-THETA_N], or nothing does, error = exactly 1.0) — so a "spike ratio" swings between near-1 (a thing
that happens to resonate an existing OLD cell within its first 3 showings, reading close to the already-
tiny baseline) and 50-60x (a thing that reads the maximal 1.0 for several showings running). Measured:
moon/house ratios at seeds 9/10/11 were 1.907 / 53.951, 0.948 / 56.418, 63.175 / 1.504 — in EVERY seed
exactly ONE of the two new things spikes hugely (>=53x) while the OTHER reads BELOW the literal 3x bar
(0.948-1.907) because it resonates something close enough within its first 3 showings not to register as
"new" at all. Settle mirrors this: the thing that never resonated by showing 3 mostly has NOT resonated
by showing 10 either (e10 stuck at 1.0, settle ratio 54-63x, a FAIL) while the thing that resonated early
settles comfortably (ratio 0.24-0.81, a PASS) — with one exception (seed 10 moon, whose spike missed but
whose settle passed: it resonated slowly, not within 3 showings but within 10). CONJUNCTION (spike AND
settle) per (seed, thing): PASS at (9,house), (10,house), (11,moon); FAIL at (9,moon), (10,moon),
(11,house) — exactly 3 of 6, a TIE, not a majority, and NO single seed's own 2 new things both pass (1/2
at every seed). RAISED, `expectedFailure`, matching PREREG's own "a toy that fails is a result you
report with its numbers, never forced to pass". F (this front's within-median-derived floor, printed for
context, not used by either bar under §16 addendum 1's rule) = 0.0310, matching B8/B13's earlier reading
exactly (F is a property of the RETINA+jitter, untouched by the error redefinition).

**The null (a fake boundary in the middle of ONE 300-showing window of circle/square/triangle, nothing
new at canvas 150): every one of 9 (seed, thing) ratios reads well under 1.5 (0.333-1.279)** — the
literal "must show no spike" bar PASSES for real, at every seed and every thing, no leniency needed.
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


def _F(seed: int = 100) -> float:
    """F = 1 - within-thing median cosine of OLD's raw glance features (gate G-a's own bands) — a
    property of the retina+jitter, printed for context only; neither bar below reads it (§16 addendum
    1's rule: both bars are relative to the pre-arrival median, not F)."""
    genome = skeleton_genome()
    rng = np.random.default_rng(seed)
    feats = {}
    for t in OLD:
        rows = []
        for _ in range(40):
            rgb, _truth = world.render_canvas(t, rng)
            rows.append(first_fixation_feature(genome, rgb, pic_id=f"{t}-{len(rows)}"))
        feats[t] = np.stack(rows)
    b = gate_ga.bands_feats(feats, np.random.default_rng(seed + 1))
    return 1.0 - b["within"]["median"]


def _window_stream(rng: np.random.Generator, things: List[str], per_thing: int) -> List[Tuple[str, np.ndarray]]:
    seq = []
    for t in things:
        for _ in range(per_thing):
            rgb, _truth = world.render_canvas(t, rng)
            seq.append((t, rgb))
    rng.shuffle(seq)
    return seq


def _feed(genome, org: Organism, pred: Predictor, seq: List[Tuple[str, np.ndarray]]) -> Tuple[List[float], List[str]]:
    """error() BEFORE org.moment() — the same order creature/mind.py uses (W3-2b's own law: a newborn
    from THIS glance must not count toward its own error)."""
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


def _real_arm(seed: int) -> Dict[str, object]:
    """w1 (OLD, 50 each, shuffled — the 'previous window') then w2 (NEW, 15 each, shuffled — the
    arrival), ONE continuous (Organism, Predictor) pair (a real arrival follows naturally from the
    previous window's cells; there is nothing to decontaminate here, unlike the null below)."""
    genome = skeleton_genome()
    rng = np.random.default_rng(seed)
    w1 = _window_stream(rng, OLD, 50)
    w2 = _window_stream(rng, NEW, 15)
    org = Organism(genome); pred = Predictor(org)
    errs1, _order1 = _feed(genome, org, pred, w1)
    last50_pre = float(np.median(errs1[-50:]))
    errs2, order2 = _feed(genome, org, pred, w2)
    per_thing = {t: [e for e, o in zip(errs2, order2) if o == t] for t in NEW}
    result: Dict[str, Dict[str, object]] = {}
    for t in NEW:
        e = per_thing[t]
        first3 = float(np.median(e[:3]))
        e10 = e[9] if len(e) > 9 else None
        spike_ratio = (first3 / last50_pre) if last50_pre > 0 else float("inf")
        settle_ratio = (e10 / last50_pre) if (e10 is not None and last50_pre > 0) else None
        result[t] = {
            "first3_med": first3, "e_at_10": e10,
            "spike_ratio": spike_ratio, "settle_ratio": settle_ratio,
            "spike_pass": spike_ratio >= 3.0,
            "settle_pass": (settle_ratio is not None and settle_ratio <= 1.25),
        }
    return {"seed": seed, "last50_pre": last50_pre, "real": result}


def _null_arm(seed: int) -> Dict[str, object]:
    """A FAKE boundary in the MIDDLE of ONE window of OLD things (things continuing throughout — PREREG
    §16 addendum 1's own words). ONE continuous 300-showing stream of circle/square/triangle (100 each,
    shuffled across the WHOLE stream, matching the real arm's w1 rule); the midpoint (canvas 150) is the
    fake boundary. Pre-boundary baseline = median error over the 50 canvases immediately before it; per
    thing, the 'spike' is its first 3 showings AFTER the midpoint (stream order) against that SAME
    baseline. A separate rng stream from the real arm's (seed+1000) — this arm shares no state with it."""
    genome = skeleton_genome()
    rng = np.random.default_rng(seed + 1000)
    seq = _window_stream(rng, OLD, 100)
    mid = len(seq) // 2
    org = Organism(genome); pred = Predictor(org)
    errs, order = _feed(genome, org, pred, seq)
    last50_pre = float(np.median(errs[mid - 50:mid]))
    result: Dict[str, Dict[str, object]] = {}
    for t in OLD:
        post_idx = [i for i in range(mid, len(seq)) if order[i] == t][:3]
        vals = [errs[i] for i in post_idx]
        first3 = float(np.median(vals)) if vals else float("nan")
        ratio = (first3 / last50_pre) if last50_pre > 0 else float("inf")
        result[t] = {"first3_med": first3, "ratio": ratio}
    return {"seed": seed, "last50_pre": last50_pre, "null": result}


def _all_real() -> List[Dict[str, object]]:
    return [_real_arm(s) for s in SEEDS]


def _all_null() -> List[Dict[str, object]]:
    return [_null_arm(s) for s in SEEDS]


class TestF(unittest.TestCase):
    def test_F_matches_the_earlier_reading(self) -> None:
        """F is a property of the retina+jitter (gate G-a's bands on RAW features), untouched by the
        error redefinition — printed for context, read by neither bar (§16 addendum 1)."""
        F = _F()
        print(f"[B13] F={F:.4f} (context only — neither bar below reads it, §16 addendum 1)")
        self.assertAlmostEqual(F, 0.0310, delta=0.005)


class TestSpikeAndSettle(unittest.TestCase):
    def test_per_thing_numbers_printed(self) -> None:
        """Every per-thing number, unconditionally printed (PREREG: 'print every per-thing number') —
        run once, shared by the two assertions below via the module-level cache."""
        results = _all_real()
        for r in results:
            for t in NEW:
                d = r["real"][t]
                print(f"[B13] seed={r['seed']} thing={t} last50_pre={r['last50_pre']:.4f} "
                      f"first3_med={d['first3_med']:.4f} spike_ratio={d['spike_ratio']:.3f} "
                      f"(bar >=3.0, {'PASS' if d['spike_pass'] else 'FAIL'}) "
                      f"e_at_10={d['e_at_10']} settle_ratio={d['settle_ratio']} "
                      f"(bar <=1.25, {'PASS' if d['settle_pass'] else 'FAIL'})")
        self.assertEqual(len(results), len(SEEDS))

    @unittest.expectedFailure
    def test_conjunction_majority_of_new_things(self) -> None:
        """PREREG's own conjunction ('spike AND settle ... graded as a majority of the window's new
        things'), pooled over all 3 seeds x 2 new things = 6 pairs. Measured: PASS at (9,house),
        (10,house), (11,moon); FAIL at (9,moon), (10,moon), (11,house) — exactly 3 of 6, a TIE, not a
        majority (and no single seed's own 2 new things both pass: 1/2 at every seed). The new error's
        bimodality (module docstring) means exactly one of the two new things per seed fails to resonate
        anything within its first 3 showings while the other does — RAISED, expectedFailure, never
        forced to pass."""
        results = _all_real()
        pairs = [(r["seed"], t, r["real"][t]["spike_pass"] and r["real"][t]["settle_pass"])
                 for r in results for t in NEW]
        cleared = sum(1 for *_r, ok in pairs if ok)
        print(f"[B13] conjunction (spike AND settle): {cleared}/{len(pairs)} — {pairs}")
        self.assertGreater(cleared, len(pairs) / 2, f"conjunction not a majority: {pairs}")


class TestFakeBoundaryNull(unittest.TestCase):
    def test_null_literal_no_spike_under_1_5x(self) -> None:
        """SS10/PREREG's literal null: 'must show no spike (< 1.5x)', on a FAKE boundary in the middle
        of one window of OLD things (nothing new at the boundary). Measured at all 3 seeds x 3 things =
        9 pairs: every ratio 0.333-1.279, well under 1.5 — PASSES for real, no leniency needed (contrast
        with the earlier version of this file, whose OLD-error null missed the literal bar at one seed)."""
        results = _all_null()
        misses = []
        for r in results:
            for t in OLD:
                d = r["null"][t]
                print(f"[B13] NULL seed={r['seed']} thing={t} last50_pre={r['last50_pre']:.4f} "
                      f"first3_med={d['first3_med']:.4f} ratio={d['ratio']:.3f} (bar <1.5)")
                if not (d["ratio"] < 1.5):
                    misses.append((r["seed"], t, d["ratio"]))
        self.assertEqual(misses, [], f"fake-boundary null missed <1.5x: {misses}")


if __name__ == "__main__":
    unittest.main()
