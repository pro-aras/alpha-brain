"""test_b8_modulation.py — B8(1): the MODULATION toy re-specified on the creature's OWN front
(docs/G4-PREREG.md §9 Amendment 1).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 23:40 +0400 — B8 (coordinator's task, after Amendment
1). This does NOT re-grade B6(a)'s pool3 reading (docs/briefs/G4-BUILDER-B-REPORT.md; it stands FAIL as
written, per Amendment 1's own words: "these readings stand"). This is a NEW toy beside it, on
`RETINA thresh0.25 centre tower:eye-tower-g2 sqrt unit` over 32x32 glances of `world.render_canvas`
canvases at 128, "one glance per showing" = **the first surprise fixation** (chosen over the amendment's
other offered option, the whole-canvas-at-32x32 "one" mode — tried FIRST: `gate_ga.bands_feats` on
circle/square/triangle's whole-canvas features reads within-median 0.9934 vs between-p95 0.9950, an
OVERLAP — shrinking the WHOLE 128px canvas to 32px shrinks the 32px thing itself to ~8px, losing exactly
the detail the sealed tower needs; the first fixation does not have this problem, see F below).

**F (gate G-a's bands, this world, this front, first-fixation features, 40/thing, circle/square/
triangle):** within-median 0.9690, within-p5 0.8882, between-median 0.8756, between-p95 0.9540 — NO
OVERLAP (within-median > between-p95, unlike pool3 or the whole-canvas front). **F = 1 - 0.9690 =
0.0310.**

**The honest finding, computed not guessed — a DIFFERENT shape from B6(a)'s:** on the exact-repeat
control the mechanism converges to error 0.0 essentially instantly (positive control, PASS). On the
jittered repeating stream, error is ALREADY near F from the very first moment — a single canvas'
example (seed 9): [1.000, 0.048, 0.009, 0.003, 0.005, 0.062, 0.012, 0.003, 0.025, ...] — moment 0 is the
organism's very first-ever prediction (no cells exist yet, `expect()` returns zeros, cos=0, e=1.0 by
construction) and moment 1 already reads 0.048, near F=0.031. Because the sealed tower is THIS good on
this world, first50's median (0.024-0.053 across 3 seeds) is ALREADY close to F, sometimes even reading
BELOW it by chance (seed 11: first50=0.0236 < F=0.0310 — 50-sample median noise around a true gap near
zero). The bar `(last50-F) <= 0.3*(first50-F)` implicitly assumes headroom between first50 and F for a
learning curve to close; here there is almost none to measure — 0 of 3 seeds clear it (not a majority),
for a reason opposite to B6(a)'s (front too WEAK there; front already CONVERGED here before the window
even opens). RAISED, `expectedFailure`, exact numbers below.
"""
from __future__ import annotations

import unittest

import numpy as np

from genome import gate_ga, world
from genome.machinery import Organism
from genome.predict import Predictor

from ._creature_front import first_fixation_feature, repeating_block_stream, skeleton_genome

THINGS = ["circle", "square", "triangle"]
SEEDS = (9, 10, 11)


def _compute_F(genome, seed: int = 100, per_thing: int = 40) -> float:
    rng = np.random.default_rng(seed)
    feats = {}
    for t in THINGS:
        rows = []
        for _ in range(per_thing):
            rgb, _truth = world.render_canvas(t, rng)
            rows.append(first_fixation_feature(genome, rgb, pic_id=f"{t}-{len(rows)}"))
        feats[t] = np.stack(rows)
    b = gate_ga.bands_feats(feats, np.random.default_rng(seed + 1))
    return 1.0 - b["within"]["median"], b


def _run(genome, seq, words=None):
    org = Organism(genome)
    pred = Predictor(org)
    errors = []
    for i, (t, rgb) in enumerate(seq):
        x = first_fixation_feature(genome, rgb, pic_id=str(i))
        w = words[i] if words is not None else t
        xw = world.encode_word(w, genome.ear_blank_zero)
        e = pred.error(x)
        errors.append(e)
        S, T = org.moment(x, xw)
        pred.note_winners(S)
    errs = np.array(errors)
    return errs, float(np.median(errs[:50])), float(np.median(errs[-50:]))


class TestB8Modulation(unittest.TestCase):
    def test_F_no_overlap(self) -> None:
        genome = skeleton_genome()
        F, b = _compute_F(genome)
        self.assertLess(abs(F - 0.0310), 0.005, f"F={F:.4f} (expected ~0.0310 at seed 100)")
        self.assertGreater(b["within"]["median"], b["between"]["p95"], "the front's bands must not overlap")

    def test_exact_repeat_control_reaches_F_plus_0_01(self) -> None:
        genome = skeleton_genome()
        F, _b = _compute_F(genome)
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            fixed = {t: world.render_canvas(t, rng) for t in THINGS}
            seq = [(t, fixed[t][0]) for _c in range(4) for t in THINGS for _ in range(17)]
            errs, _first, _last = _run(genome, seq)
            final = float(np.median(errs[-20:]))
            self.assertLessEqual(final, F + 0.01, f"seed {seed}: final={final:.5f} vs F+0.01={F+0.01:.5f}")

    @unittest.expectedFailure
    def test_null_does_not_clear_the_bar(self) -> None:
        """The null: picture order shuffled AND word labels shuffled, together (one arm, both
        perturbations) — must not clear the bar at a majority of seeds.

        edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:18 +0400 — W3-2b (docs/G4-WAVE3-CLAUSES.md):
        re-measured under the NEW error (genome/predict.py: max cosine over EVERY alive sight cell, not
        the old single last-winner). Under the OLD error this null read 0/3 (matching the design arm's
        own 0/3 — this file's whole point, per B8's docstring, was that this front's ratio bar was near-
        degenerate for BOTH arms). Under the NEW error the null now clears at 3/3 (first/last: seed 9
        0.0254/0.0141, seed 10 0.0240/0.0155, seed 11 0.0170/0.0146) — but so does the DESIGN arm (see
        `test_design_bar_majority_of_three_seeds`, now a real PASS at 3/3 too): the new error resonates
        over the WHOLE alive-cell population, which several jittered exemplars cover so tightly that a
        shuffled-word/shuffled-picture stream converges just as well as the honestly-ordered one on this
        small (3-thing, well-separated) toy — this ratio-bar design cannot discriminate signal from null
        here any more, in EITHER direction. This is the toy B13's arrival-based re-specification (§10
        Amendment 2, W3-2b's re-run in test_b13_modulation_arrival.py) exists to replace; kept here,
        RAISED and `expectedFailure`, as the honest record of why the ratio-bar shape itself stopped
        being informative once the target moved inside the organism, rather than silently deleted or
        forced to a misleading pass."""
        genome = skeleton_genome()
        F, _b = _compute_F(genome)
        clears = 0
        for seed in SEEDS:
            seq = repeating_block_stream(seed, THINGS)
            wrng = np.random.default_rng(seed + 1000)
            shuffled_words = [THINGS[i] for i in wrng.integers(0, 3, size=len(seq))]
            prng = np.random.default_rng(seed + 2000)
            order = prng.permutation(len(seq))
            shuffled_seq = [seq[i] for i in order]
            _errs, first, last = _run(genome, shuffled_seq, words=shuffled_words)
            if (last - F) <= 0.3 * (first - F):
                clears += 1
        self.assertLess(clears, 2, f"the null cleared the bar at {clears}/3 seeds — must not be a majority")

    def test_design_bar_majority_of_three_seeds(self) -> None:
        """PREREG §9 Amendment 1's literal bar: (last50-F) <= 0.3*(first50-F), majority of 3 seeds.

        UNDER THE OLD error: 0 of 3 (seed 9: first=0.0317 last=0.0484 lhs=0.0174 rhs=0.0002; seed 10:
        first=0.0532 last=0.0426 lhs=0.0116 rhs=0.0067; seed 11: first=0.0236 last=0.0473 lhs=0.0163
        rhs=-0.0022) — see the module docstring: first50 was already near (sometimes below, by sampling
        noise) F, so the bar's denominator was near zero and the ratio framing was close to degenerate.

        edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:18 +0400 — W3-2b: re-measured under the NEW
        error, this bar now clears at 3/3 (seed 9: first=0.0206 last=0.0140 lhs=-0.0170 rhs=-0.0031;
        seed 10: first=0.0145 last=0.0119 lhs=-0.0191 rhs=-0.0050; seed 11: first=0.0141 last=0.0114
        lhs=-0.0196 rhs=-0.0051 — every lhs comfortably below rhs). `expectedFailure` removed: this is a
        real, asserted PASS now. Read together with `test_null_does_not_clear_the_bar` above (which ALSO
        now clears, RAISED there): the design arm passing alone is not evidence of discrimination — see
        that test's docstring for why this specific ratio-bar toy is superseded by B13's re-run."""
        genome = skeleton_genome()
        F, _b = _compute_F(genome)
        passes = 0
        readings = []
        for seed in SEEDS:
            seq = repeating_block_stream(seed, THINGS)
            _errs, first, last = _run(genome, seq)
            lhs, rhs = last - F, 0.3 * (first - F)
            readings.append((seed, first, last, lhs, rhs))
            if lhs <= rhs:
                passes += 1
        self.assertGreaterEqual(passes, 2, f"majority (>=2/3) required; got {passes}/3 — readings: {readings}")


if __name__ == "__main__":
    unittest.main()
