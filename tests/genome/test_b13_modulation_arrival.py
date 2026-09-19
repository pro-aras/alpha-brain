"""test_b13_modulation_arrival.py — B13 (docs/G4-PREREG.md §10 Amendment 2, §11.2's "wave 2 opening"
toy): MODULATION re-specified as SURPRISE AT ARRIVAL, on the creature's own front.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — new file, Wave 2 B13.
edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 23:2x +0400 — revised after an advisor review caught
two instrument defects in the first version: (1) the null arm was fed the SAME (org, pred) pair as the
real arm, AFTER the real arm's 2 new things had already been shown — the "no new things" window was
therefore measured on a predictor whose last winner was a moon/house cell, an artifact, not a clean
null. Fixed: the null arm now runs on a SEPARATE, freshly-built (Organism, Predictor) pair, fed the
IDENTICAL w1 stream (deterministic replay — `baseline_identical` asserted True at every seed) before
w2_null, so neither arm's window 2 can see the other's. (2) the "ceiling" was computed as
`1 - between-p95` pooled over ALL FIVE things' pairwise combinations, which is dominated by whichever
pair happens to read highest regardless of whether it involves a NEW thing at all. Fixed to the PREREG's
own two-part instruction: (a) `ceiling_bands` = 1 - the MAX p95 among only the OLD-vs-NEW pairs (never
old-old or new-new); (b) `ceiling_direct` = the PREREG's literal per-instance definition, measured live
at each new thing's actual first showing in the real arm: `1 - max(cos to every currently-alive sight
cell)`. Both are printed beside F. Neither fix changes the REAL arm's spike/settle numbers (they were
never contaminated — the real arm ran before the null arm in the original code too); only F/ceiling and
the null numbers move.
edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 23:4x +0400 — a SECOND advisor pass on the same file
caught that the pooled `ceiling_bands` from the first fix was itself applied uniformly to BOTH new
things, when the PREREG's relaxation is explicitly CONDITIONAL, per new thing: "if the tower front's
between-p95 makes A NEW THING look like an old one ... reported against THAT ceiling". Moon's own
worst old-vs-new p95 (0.8181) gives ceiling_moon/F = 5.9x > 3x — the relaxation does NOT apply to moon,
whose bar is therefore the LITERAL 3x (which it never reaches: max 2.65x, 0/3). House's worst pair
(0.9515) gives 1.56x < 3x — the relaxation DOES apply to house (3/3). The POOLED reading (one ratio for
both things, 5/6) is kept as a named, distinct test — a legitimate single-number summary — but the
PER-THING reading (the PREREG's actual conditional, 3/6, a tie) is the one that should govern the live
life; it is `@unittest.expectedFailure`. The same pass also found the null bar has no "majority" clause
in SS10 (unlike B8's, which Amendment 1 explicitly said to read that way) — the literal "must show no
such spike (< 1.5x)" is tested directly (all 3 seeds; seed 9 misses at 1.547, `expectedFailure`), with
the majority reading kept as a clearly-labelled secondary leniency.

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
window (not per-thing blocks) — so the baseline ("the previous window's last 50 showings") reflects the
ordinary noise of a mind that keeps re-predicting a DIFFERENT thing's cell whenever the stream switches
identity mid-window. **This is a real, load-bearing design choice, not a free one**: under this shuffle,
last50_med reads ~0.09-0.11 (about 3x F), so the spike bar's arithmetic (literal 3xF) is being asked to
clear a baseline that is ALREADY elevated by ordinary within-window switching noise. Under a BLOCKED
old-things phase instead (same-thing runs, as B8's `repeating_block_stream` used), last50_med would sit
near F (B8 measured last50 at 0.043-0.048 on this exact front/world under blocking) and the SAME
new-thing first-3 errors (~0.18-0.24, unaffected by how window 1 was ordered) would read roughly 4-6x
that baseline instead of ~2x. **This was NOT re-run under blocking to chase a cleaner number — that
would be config-shopping.** The finding to carry forward: the spike verdict is sensitive to the window-1
ORDERING RULE, which belongs to Builder A's `world_maker.py` (the maker schedules real arrivals), not to
this toy; the PREREG should say which ordering the live maker uses before this mark is read off the
live life.

Window 2 (the REAL arm) = moon/house (`world.THINGS_ARRIVAL2[:2]`), interleaved and shuffled, 15
showings each (30 total) — each new thing's OWN showing sequence is tracked separately (so "first 3
showings of each new thing" and "within 10 showings of that thing" are per-thing, not per-canvas-index).
Window 2' (the NULL arm, a SEPARATE run from the SAME post-w1 state) = circle/square/triangle again (10
more showings each, 30 total, freshly jittered, shuffled) — a window change that brings NO new things.

**F and the ceiling, measured first (gate G-a's bands, this front, this world):** F = 0.0310
(circle/square/triangle, within-median 0.9690 — the same reading as B8's). `ceiling_bands` (1 - the
WORST/highest p95 among old-vs-new pairs only) = **0.0485** (the worst pair is house/square at p95
0.9515 — house happens to look almost like an old thing on this front; moon's own old-vs-new p95s are
much lower, 0.73-0.82, i.e. moon looks much MORE distinct). `ceiling_bands/F` = **1.56x** — still under
3x, so the PREREG's own instruction still applies: the bar is reported against `ceiling_bands`, not the
literal 3x. **`ceiling_direct`** (the PREREG's literal per-instance definition, measured live at each
new thing's actual arrival) confirms this is thing-SPECIFIC, not a single shared number: moon reads
0.195-0.252 across seeds (it really is quite novel-looking to this front), house reads 0.053-0.067
(close to `ceiling_bands`, confirming house is the pair driving that pooled worst case). Reported, not
used to pick a per-thing bar — the bands ceiling is what the PREREG says to print beside the bar.

**The honest finding, measured not guessed, at 3 seeds x 2 new things = 6 (seed, thing) pairs:**
  spike vs POOLED ceiling_bands-ratio (1.56x, applied to both new things alike): 5/6 clear — a
    majority, PASSES (`test_spike_vs_pooled_worst_case_ceiling_majority_clears`).
  spike vs PER-THING ceiling (the PREREG's actual conditional): moon's own bar is the literal 3x (its
    ceiling, 0.1819, sits at 5.9xF > 3x, so the relaxation does not apply to it) — moon clears 0/3
    (1.82x, 2.65x, 0.59x, none reach 3x). House's own bar is 1.56x (its ceiling DOES sit under 3xF) —
    house clears 3/3. Combined: **3/6, a TIE, not a majority.** RAISED, `expectedFailure`
    (`test_spike_vs_per_thing_ceiling_prereg_conditional`) — this is the reading that should govern.
  settle (< F+0.05=0.0810 by the thing's 10th showing): EXACTLY 3/6 (seed 10 both: 0.055, 0.014; seed
    11 moon 0.079, barely; the other three sit at 0.20-0.36, still elevated at showing 10) — a TIE, not
    a majority. RAISED, `expectedFailure`.
  CONJUNCTIVE (per-thing spike AND settle, the PREREG's own "AND"): moon 0/3 (never clears its own
    spike bar), house 1/3 (clears spike every time, settles only at seed 10) — combined **1/6**. NOT a
    majority. RAISED, `expectedFailure`.
  null, majority reading (a leniency this file adds, not SS10's own word): seed 9 **1.547x MISSES**
    (barely, just above 1.5), seed 10 **0.516x clears**, seed 11 **0.752x clears**. 2/3 — PASSES.
  null, LITERAL reading (SS10's actual word, "must show no such spike"): 2/3 is not "no spike, ever" —
    seed 9 misses. RAISED, `expectedFailure`. Paired against that seed's own real arm (#215's
    discipline — compare matched pairs): seed 9's real spikes (moon 1.82x, house 1.76x) sit within 0.3x
    of that SAME seed's null (1.55x) — barely distinguishable from no arrival at all. At seed 11, moon's
    real spike (0.60x) reads BELOW that seed's own null (0.75x).
Only two readings clear a majority unqualified: the pooled (not per-thing) ceiling reading, and the
null under a majority (not literal) reading. Every literal PREREG bar — per-thing ceiling, settle,
the conjunction, and the null's literal "must" — misses on this toy. Reported honestly, not forced.
"""
from __future__ import annotations

import unittest
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from genome import gate_ga, world
from genome.machinery import Organism
from genome.predict import Predictor

from ._creature_front import first_fixation_feature, skeleton_genome

OLD = ["circle", "square", "triangle"]
NEW = list(world.THINGS_ARRIVAL2[:2])  # ["moon", "house"]
SEEDS = (9, 10, 11)


def _F_and_ceiling(seed: int = 100, per_thing: int = 40) -> Tuple[float, float, Dict, Dict]:
    """F from the OLD things' own bands; ceiling_bands from the WORST (highest-p95, hence lowest-
    ceiling) pair among OLD-vs-NEW combinations only — never old-old or new-new."""
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
    old_new_p95 = {pair: p95 for pair, p95 in b_all["pair_p95"].items()
                    if (pair.split("/")[0] in OLD) != (pair.split("/")[1] in OLD)}
    ceiling_bands = 1.0 - max(old_new_p95.values())
    return F, ceiling_bands, b_old, {**b_all, "old_new_p95": old_new_p95}


def _per_thing_ceiling_bands(new_thing: str, old_new_p95: Dict[str, float]) -> float:
    """The PREREG's relaxation is CONDITIONAL, per new thing: 'if the tower front's between-p95 makes
    A NEW THING look like an old one ... reported against THAT ceiling' — not a single pooled number
    for every new thing at once (an advisor review caught this reading error in the first pass: a
    pooled worst-case ceiling was applied to BOTH new things, when only one of them is actually close
    to an old thing on this front). This returns 1 - the WORST (highest) old-vs-NEW-THING p95 among
    pairs naming that one new thing."""
    worst = max(p95 for pair, p95 in old_new_p95.items() if new_thing in pair.split("/"))
    return 1.0 - worst


def _window_stream(rng: np.random.Generator, things: List[str], per_thing: int) -> List[Tuple[str, np.ndarray]]:
    seq = []
    for t in things:
        for _ in range(per_thing):
            rgb, _truth = world.render_canvas(t, rng)
            seq.append((t, rgb))
    rng.shuffle(seq)
    return seq


def _feed(genome, org: Organism, pred: Predictor, seq: List[Tuple[str, np.ndarray]],
          ceiling_capture: Optional[Dict[str, Optional[float]]] = None,
          ceiling_seen: Optional[Set[str]] = None) -> Tuple[List[float], List[str]]:
    """Feeds one stream through one (org, pred) pair. When `ceiling_capture`/`ceiling_seen` are given,
    the FIRST time a thing named in `ceiling_capture` is shown, records the PREREG's literal ceiling —
    `1 - cos(its glance, the nearest currently-alive sight cell)` — BEFORE that showing's `org.moment`
    call can birth/wire anything."""
    errs: List[float] = []
    order: List[str] = []
    for t, rgb in seq:
        x = first_fixation_feature(genome, rgb, pic_id=f"{t}-{len(errs)}")
        if ceiling_capture is not None and t in ceiling_capture and t not in ceiling_seen:
            cos_vals = org.sight.cos(x)
            ceiling_capture[t] = 1.0 - (float(cos_vals.max()) if len(cos_vals) else 0.0)
            ceiling_seen.add(t)
        e = pred.error(x)
        errs.append(e); order.append(t)
        xw = world.encode_word(t, genome.ear_blank_zero)
        S, T = org.moment(x, xw)
        pred.note_winners(S)
    return errs, order


def _run_seed(seed: int) -> Dict[str, object]:
    genome = skeleton_genome()
    rng = np.random.default_rng(seed)
    w1 = _window_stream(rng, OLD, 50)          # 150 showings, the arrival's "previous window"
    w2_real = _window_stream(rng, NEW, 15)     # 30 showings, 2 NEW things, interleaved
    rng_null = np.random.default_rng(seed + 1000)
    w2_null = _window_stream(rng_null, OLD, 10)  # 30 showings, NO new things

    # REAL arm: its own fresh Organism/Predictor, fed w1 then w2_real.
    org_r = Organism(genome)
    pred_r = Predictor(org_r)
    errs1, _order1 = _feed(genome, org_r, pred_r, w1)
    last50_med = float(np.median(errs1[-50:]))
    ceiling_direct: Dict[str, Optional[float]] = {t: None for t in NEW}
    errs2r, order2r = _feed(genome, org_r, pred_r, w2_real, ceiling_capture=ceiling_direct, ceiling_seen=set())
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

    # NULL arm: a SEPARATE fresh Organism/Predictor, fed the IDENTICAL w1 (deterministic replay) then
    # w2_null — never touched by w2_real, so "no new things" is measured cleanly (advisor's fix #1).
    org_n = Organism(genome)
    pred_n = Predictor(org_n)
    errs1n, _order1n = _feed(genome, org_n, pred_n, w1)
    last50_med_null_arm = float(np.median(errs1n[-50:]))
    errs2n, _order2n = _feed(genome, org_n, pred_n, w2_null)
    null_first3 = float(np.median(errs2n[:3]))
    null_spike = (null_first3 / last50_med_null_arm) if last50_med_null_arm > 0 else float("inf")

    return {
        "seed": seed, "last50_med": last50_med,
        "baseline_identical": last50_med == last50_med_null_arm,
        "ceiling_direct": ceiling_direct, "real": real, "null_spike": null_spike,
    }


def _all_results() -> List[Dict[str, object]]:
    return [_run_seed(s) for s in SEEDS]


class TestFAndCeiling(unittest.TestCase):
    def test_F_and_ceiling_below_3x(self) -> None:
        F, ceiling, b_old, b_all = _F_and_ceiling()
        print(f"[B13] F={F:.4f} (within-median {b_old['within']['median']:.4f}) "
              f"ceiling_bands(old-new only)={ceiling:.4f} 3xF={3 * F:.4f} ceiling/F={ceiling / F:.3f}x")
        print(f"[B13] old-new pair p95s: {b_all['old_new_p95']}")
        self.assertAlmostEqual(F, 0.0310, delta=0.005)
        self.assertLess(ceiling, 3 * F, "expected this front's ceiling to sit below the literal 3x bar")

    def test_ceiling_direct_is_thing_specific(self) -> None:
        """The PREREG's literal per-instance ceiling, measured live at each new thing's actual arrival:
        house tracks the pooled `ceiling_bands` closely (within 2x — it IS the pair driving that pooled
        worst case); moon reads well above 3xF (it looks nothing like an old thing on this front) —
        asserted, not just printed, so a future change that erases this gap is caught."""
        F, ceiling_bands, _b_old, _b_all = _F_and_ceiling()
        results = _all_results()
        for r in results:
            print(f"[B13] seed={r['seed']} ceiling_direct={r['ceiling_direct']}")
        moon_vals = [r["ceiling_direct"]["moon"] for r in results]
        house_vals = [r["ceiling_direct"]["house"] for r in results]
        moon_mean, house_mean = float(np.mean(moon_vals)), float(np.mean(house_vals))
        print(f"[B13] ceiling_direct moon mean={moon_mean:.4f} house mean={house_mean:.4f} "
              f"ceiling_bands={ceiling_bands:.4f} 3xF={3 * F:.4f}")
        self.assertLess(house_mean, 2 * ceiling_bands, "house's direct ceiling should track the pooled bands ceiling")
        self.assertGreater(moon_mean, 3 * F, "moon's direct ceiling should sit well above 3xF (it looks distinct)")


class TestSpikeVsCeiling(unittest.TestCase):
    def test_spike_vs_pooled_worst_case_ceiling_majority_clears(self) -> None:
        """The POOLED reading: one ceiling ratio (the worst old-vs-new pair across BOTH new things,
        1.56x) applied to every (seed, thing) pair. A legitimate single-number reading, but not the
        PREREG's actual conditional (see the per-thing test below, which is the literal one)."""
        F, ceiling, _b_old, _b_all = _F_and_ceiling()
        bar_ratio = ceiling / F  # ~1.56x
        results = _all_results()
        pairs = []
        for r in results:
            for t in NEW:
                pairs.append((r["seed"], t, r["real"][t]["spike"]))
        for seed, t, spike in pairs:
            print(f"[B13] seed={seed} thing={t} spike={spike:.3f} vs POOLED ceiling-ratio={bar_ratio:.3f}")
        cleared = sum(1 for _s, _t, sp in pairs if sp >= bar_ratio)
        print(f"[B13] spike-vs-pooled-ceiling: {cleared}/{len(pairs)} clear")
        self.assertGreater(cleared, len(pairs) / 2, f"spike-vs-pooled-ceiling not a majority: {pairs}")

    @unittest.expectedFailure
    def test_spike_vs_per_thing_ceiling_prereg_conditional(self) -> None:
        """The PREREG's actual conditional, read literally: 'if the tower front's between-p95 makes A
        NEW THING look like an old one ... reported against THAT ceiling' — per new thing, not pooled.
        Moon's own worst old-vs-new p95 (0.8181, the circle/moon-square/moon-triangle/moon trio) gives
        ceiling_moon = 0.1819, ratio 5.9x > 3x — the relaxation does NOT apply to moon, so its bar is
        the LITERAL 3x, which moon clears 0/3 (max 2.65x). House's worst pair (0.9515) gives ratio
        1.56x < 3x — the relaxation DOES apply, and house clears 3/3. Combined: 3/6, a TIE, not a
        majority. RAISED, expectedFailure — this is the reading that should govern the live life, not
        the pooled test above."""
        F, _ceiling, _b_old, b_all = _F_and_ceiling()
        old_new_p95 = b_all["old_new_p95"]
        results = _all_results()
        outcomes = []
        for r in results:
            for t in NEW:
                ceiling_t = _per_thing_ceiling_bands(t, old_new_p95)
                # the relaxation ("report against the ceiling") applies only when that thing's OWN
                # ceiling sits below the literal 3x bar; otherwise the literal 3x stands for it.
                bar_ratio_t = (ceiling_t / F) if ceiling_t < 3 * F else 3.0
                spike = r["real"][t]["spike"]
                ok = spike >= bar_ratio_t
                outcomes.append((r["seed"], t, spike, bar_ratio_t, ok))
        for seed, t, spike, bar_ratio_t, ok in outcomes:
            print(f"[B13] seed={seed} thing={t} spike={spike:.3f} vs PER-THING ceiling-ratio={bar_ratio_t:.3f} ok={ok}")
        cleared = sum(1 for *_r, ok in outcomes if ok)
        print(f"[B13] spike-vs-per-thing-ceiling: {cleared}/{len(outcomes)} clear")
        self.assertGreater(cleared, len(outcomes) / 2, f"per-thing ceiling bar: {cleared}/{len(outcomes)}")


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
        """The PREREG's literal "AND": spike >= ceiling-ratio (per-thing, the PREREG's actual
        conditional — see TestSpikeVsCeiling's per-thing test) AND settled by showing 10. Measured:
        moon never clears its own 3x bar (0/3), so moon's conjunction is 0/3 regardless of settle;
        house clears its 1.56x bar every time (3/3) but only seed 10 also settles — house conjunction
        1/3. Combined: 1/6 — NOT a majority. RAISED, expectedFailure."""
        F, _ceiling, _b_old, b_all = _F_and_ceiling()
        old_new_p95 = b_all["old_new_p95"]
        threshold = F + 0.05
        results = _all_results()
        both = []
        for r in results:
            for t in NEW:
                ceiling_t = _per_thing_ceiling_bands(t, old_new_p95)
                bar_ratio_t = (ceiling_t / F) if ceiling_t < 3 * F else 3.0
                spike = r["real"][t]["spike"]
                e10 = r["real"][t]["e_at_10"]
                ok = spike >= bar_ratio_t and e10 is not None and e10 < threshold
                both.append(ok)
        cleared = sum(both)
        print(f"[B13] conjunctive (per-thing ceiling): {cleared}/{len(both)}")
        self.assertGreater(cleared, len(both) / 2, f"conjunctive bar: {cleared}/{len(both)}")


class TestNoNewThingsNull(unittest.TestCase):
    def test_baselines_are_byte_identical_across_the_two_arms(self) -> None:
        """The decontamination check itself: the real arm's and the null arm's separate (Organism,
        Predictor) pairs, fed the IDENTICAL w1 stream, must reach the exact same last-50 median —
        proving neither arm's window 2 can leak into the other's baseline."""
        results = _all_results()
        for r in results:
            self.assertTrue(r["baseline_identical"], f"seed {r['seed']}: baselines diverged")

    def test_null_majority_under_1_5x(self) -> None:
        """A leniency this file adds, NOT something SS10 states (unlike B8's MODULATION null, which
        Amendment 1 explicitly said to read by majority) — kept as a secondary, softer reading."""
        results = _all_results()
        for r in results:
            print(f"[B13] seed={r['seed']} null_spike={r['null_spike']:.3f} (bar < 1.5x)")
        cleared = sum(1 for r in results if r["null_spike"] < 1.5)
        print(f"[B13] null under 1.5x (majority reading): {cleared}/{len(results)}")
        self.assertGreaterEqual(cleared, 2, f"null spikes: {[r['null_spike'] for r in results]}")

    @unittest.expectedFailure
    def test_null_all_seeds_under_1_5x_literal_must(self) -> None:
        """SS10's own word is "must show no such spike (< 1.5x)" — not "a majority of seeds". Measured:
        seed 9's null reads 1.547, just above 1.5 — MISSES under the literal "must". RAISED,
        expectedFailure. Paired against the same seed's real arrivals (#215's discipline: compare
        matched pairs, not two unpaired numbers): at seed 9 the real spikes (moon 1.818, house 1.761)
        sit within 0.3x of that seed's OWN null (1.547) — this seed's arrival is barely distinguishable
        from no arrival at all. At seed 11, moon's real spike (0.595) reads BELOW that seed's own null
        (0.752) — the "new" thing spiked LESS than the "no new things" control did."""
        results = _all_results()
        misses = [r for r in results if r["null_spike"] >= 1.5]
        for r in results:
            print(f"[B13] seed={r['seed']} null_spike={r['null_spike']:.3f} (literal bar: must be < 1.5x)")
        self.assertEqual(misses, [], f"seeds missing the literal <1.5x null bar: "
                                      f"{[(r['seed'], r['null_spike']) for r in misses]}")


if __name__ == "__main__":
    unittest.main()
