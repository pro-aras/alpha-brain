"""test_predict.py — B6: PREDICT + FILE (genome/predict.py) — the one modulator, and falsifiability.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 22:20 +0400 — B6 (docs/G4-PREREG.md §3, docs/briefs/
G4-BUILDER-B-GENES.md).

(a)'s honest finding, read from an advisor review of this file's first draft (kept here so the numbers
are not re-litigated by a future reader): `expect()`'s only knob is prototype DENSITY (machinery.py's
cells are FIXED — DELTA changes edge weights, never a cell vector), so the error a persistence predictor
can reach on a JITTERED stream has a CEILING set by the retina + jitter, not by learning: floor = 1 −
within-thing median cosine. On this toy's pool3 front over circle/square/triangle, floor ~= 0.19-0.20 and
first50 ~= 0.24-0.26, so ratio's own ceiling is ~= 0.75-0.80 — the PREREG's 0.7x bar sits BELOW that
ceiling. Measured at 3 fixed seeds the design arm's ratio is 0.70/0.73/0.90 (mean 0.78): error genuinely
FALLS every time (ratio < 1.0, robust) but does not reliably clear 0.7x (a RAISED finding, `expectedFailure`,
never forced to pass). The canvas/GAZE glance feed (4 glances/canvas) was tried FIRST and is a dead end
reported once, not re-run: consecutive glances are different spatial windows of the canvas with no
feature-level persistence for expect() to exploit — median error stayed flat (~0.55-0.58) over 2,400
moments. The exact-repeat run (below) is the positive control that the mechanism itself is correct.

The null story (word-shuffled / picture-shuffled) did not come out clean at this toy's scale (N=204,
pool3, 3 near-symmetric shapes): word-shuffled ratio was BELOW design's at 2 of 3 seeds — a genuine
second-order effect (word-shuffling changes which sight cells MERGE, since merge requires the SAME
answer, so it changes the surviving cell population, not just the wiring) rather than the "blind, falls
identically" a sight-only predictor would naively suggest. gate_ga's own bands on this front for these
three things read between-p95 (0.92) ABOVE within-median (0.81) — an OVERLAP under gate G-a's amended
rule — so the retina itself cannot cleanly separate the population this toy draws its nulls from; the
noise is in the FRONT, not a defect in Predictor. Reported as numbers (test_nulls_reported), not forced
into a pass/fail claim the data does not support.

edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 10:46 +0400 — W3-2b (docs/G4-WAVE3-CLAUSES.md):
`error()` no longer reads `expect()` (the last moment's single remembered winner) — it reads
`org.sight.cos(x_actual)` over EVERY alive sight cell and takes the max (module docstring in
genome/predict.py). The "persistence predictor's ceiling is set by prototype DENSITY" story above was
true of a SINGLE remembered vector; it is not true of a max over the whole population, which several
jittered exemplars of one thing can collectively cover far more tightly than one prototype ever could.
Re-measured on this exact toy (same genome, same THETA_N-from-the-stream, same 3-seed repeating-block
stream): last50 now reads 0.0436 / 0.0439 / 0.0495 (seeds 9/10/11) against the SAME floor (0.198, still
1 − within-thing-median-cosine — that number describes the RETINA+jitter, not the predictor, and is
unchanged) — the new mechanism reads WELL BELOW that floor at all three seeds, because it is no longer
bound by it. `test_floor_explains_the_ratio_ceiling` is rewritten below to state this (the new error
BEATS the old ceiling, not "lands near" it) rather than deleted — the floor number is still worth
printing, now as a lower bound the new mechanism clears, not a ceiling it approaches.
`test_bar_0_7x_prereg_b6a`'s bar (mean ratio < 0.7x) now PASSES for real: mean ratio 0.439 (0.405 /
0.430 / 0.482 at seeds 9/10/11), well under 0.7 — `@unittest.expectedFailure` removed (an unexpected
success under the OLD mechanism would have failed the suite; #197's "pin in both directions" did its
job and caught the flip). Kept as a real, asserted PASS with the new numbers in its own docstring, not
silently deleted — the OLD numbers (mean 0.78, FAIL) stand on the record above as what the OLD `expect()`
read on this same toy.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import world
from genome.machinery import Organism, parse_genome, retina, retina_dim
from genome.predict import FILE_FIELDS, Predictor, append_ledger, file, score

THINGS = ["circle", "square", "triangle"]
SPEC = ("pool3", "unit")


def _build_genome(theta_n: float) -> "object":
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
BUDGET 2000 per arrival
NMAX 200
KWTA 5
HEBB window 1
DELTA lr 0.1
PRUNE w<0.02 after 3 chances
MERGE cos>0.99 same-answer
SCALE every 1000 moments
STAGE 1 senses moments 0..0
STAGE 2 meet moments 0..
RECALL k=1
ABSTAIN second/best > 0.85
"""
    return parse_genome(text)


def _theta_n_from_the_stream(seed: int = 100) -> float:
    """THETA_N derived the way gate G-a derives it (within-thing median cosine) — adaptive, so nobody
    picks it by hand; a fixed seed, independent of the life seeds below, keeps the whole test deterministic."""
    from genome import gate_ga
    b = gate_ga.bands(THINGS, 60, np.random.default_rng(seed), SPEC, side=24)
    return round(b["within"]["median"], 3)


def _repeating_block_stream(seed: int, cycles: int = 4, block: int = 17):
    """A repeating 3-thing stream: `cycles` passes over circle/square/triangle, `block` fresh (jittered)
    renderings of each thing in a row per pass — consecutive moments SHARE a thing most of the time (the
    precondition a persistence predictor needs), unlike an A-B-C round-robin (tried and rejected: a
    round-robin never repeats a thing on two consecutive moments, so `expect()` — the LAST winner — always
    predicts a DIFFERENT thing than what comes next, by construction)."""
    rng = np.random.default_rng(seed)
    return [(t, world.render(t, rng, side=24)) for _ in range(cycles) for t in THINGS for _ in range(block)]


def _run(g, seq, blank_zero: bool, words=None):
    org = Organism(g)
    pred = Predictor(org)
    errors = []
    for i, (t, pic) in enumerate(seq):
        x = retina(pic, g.retina)
        w = words[i] if words is not None else t
        xw = world.encode_word(w, blank_zero)
        e = pred.error(x)
        errors.append(e)
        S, T = org.moment(x, xw)
        pred.note_winners(S)
    errs = np.array(errors)
    return errs, float(np.median(errs[:50])), float(np.median(errs[-50:]))


SEEDS = (9, 10, 11)


class TestPredictor(unittest.TestCase):
    def test_mechanism_perfect_on_exact_repeat(self) -> None:
        """The positive control: with NO jitter (the exact same rendering repeated), expect() should
        predict the next glance perfectly (error -> 0) after the very first exposure of each thing —
        proof the mechanism itself (winner tracking, cosine error) is correct, independent of the
        jittered-stream ceiling discussed in this file's module docstring."""
        g = _build_genome(theta_n=0.85)
        rng = np.random.default_rng(9)
        fixed = {t: world.render(t, rng, side=24) for t in THINGS}
        seq = [(t, fixed[t]) for _ in range(4) for t in THINGS for _ in range(17)]
        errs, _first, _last = _run(g, seq, blank_zero=True)
        # every moment except the very first occurrence of each thing (3 of them) and thing-CHANGE
        # boundaries (one wrong prediction each) must read exactly 0.0
        near_zero = int((errs < 1e-9).sum())
        self.assertGreaterEqual(near_zero, len(errs) - 3 - 12, f"exact repeats should predict almost perfectly: {sorted(set(np.round(errs, 3)))}")
        self.assertEqual(errs[2], 0.0, "the 3rd moment of a thing's very first block must already be exact")

    def test_error_falls_on_the_repeating_stream_at_three_seeds(self) -> None:
        """(a), the robust half: median error of the last 50 < the first 50 (ratio < 1.0) — TRUE at
        every one of 3 independent seeds. THETA_N is derived from the stream itself (gate G-a's rule),
        never hand-picked."""
        theta_n = _theta_n_from_the_stream()
        g = _build_genome(theta_n)
        ratios = []
        for seed in SEEDS:
            seq = _repeating_block_stream(seed)
            _errs, first, last = _run(g, seq, blank_zero=True)
            ratio = last / first
            ratios.append(ratio)
            self.assertLess(ratio, 1.0, f"seed {seed}: error must fall (first {first:.3f} -> last {last:.3f})")
        # not asserted, just carried for the report:
        self.ratios_design = ratios

    def test_bar_0_7x_prereg_b6a(self) -> None:
        """(a)'s LITERAL bar: median error of the last 50 < 0.7x the first 50. UNDER THE OLD `expect()`
        (a single remembered winner), this bar FAILED (mean ratio ~0.78, `expectedFailure`, see the
        module docstring). W3-2b (2026-09-21) moved error()'s target to the max cosine over EVERY alive
        sight cell, which several jittered exemplars of a thing cover far more tightly than one
        prototype — mean ratio now reads 0.439 (0.405 / 0.430 / 0.482 at seeds 9, 10, 11), clearing 0.7x
        at every seed. `expectedFailure` removed; this is now a real, asserted PASS (a future regression
        that pushes the ratio back up is caught as a real failure, not silently absorbed)."""
        theta_n = _theta_n_from_the_stream()
        g = _build_genome(theta_n)
        ratios = []
        for seed in SEEDS:
            _errs, first, last = _run(g, _repeating_block_stream(seed), blank_zero=True)
            ratios.append(last / first)
        mean_ratio = sum(ratios) / len(ratios)
        self.assertLess(mean_ratio, 0.7, f"mean ratio over seeds {SEEDS}: {mean_ratio:.3f} (per-seed: {[round(r,3) for r in ratios]})")

    def test_floor_beaten_not_approached(self) -> None:
        """RENAMED and re-read (was test_floor_explains_the_ratio_ceiling; W3-2b, 2026-09-21): under the
        OLD `expect()` the last-50 median landed NEAR 1 - within-thing-median-cosine (a ceiling set by
        remembering one prototype). Under the NEW error (max cosine over every alive cell) that number is
        no longer a ceiling — several jittered exemplars collectively cover a thing's neighbourhood more
        tightly than any one of them alone, so the new error reads WELL BELOW it. Measured at all three
        seeds: floor=0.198, last50 = 0.044 / 0.044 / 0.049 (seeds 9/10/11) — every one below the floor,
        not near it. Asserted at all three seeds (not just seed 9, as the old version read), both
        directions pinned: `last < floor` at every seed, and the gap is not vanishingly small (>= 0.05)."""
        from genome import gate_ga
        theta_n = _theta_n_from_the_stream()
        g = _build_genome(theta_n)
        b = gate_ga.bands(THINGS, 60, np.random.default_rng(200), SPEC, side=24)
        floor = 1.0 - b["within"]["median"]
        for seed in SEEDS:
            with self.subTest(seed=seed):
                _errs, _first, last = _run(g, _repeating_block_stream(seed), blank_zero=True)
                self.assertLess(last, floor, f"seed {seed}: last50={last:.4f} should now beat the old ceiling floor={floor:.4f}")
                self.assertGreaterEqual(floor - last, 0.05, f"seed {seed}: last50={last:.4f} floor={floor:.4f} — gap too small to trust")

    def test_word_shuffled_and_picture_shuffled_streams_reported(self) -> None:
        """(a)'s null half: computed and reported for the record, at all 3 seeds — see the module
        docstring for why this toy's scale (N=204, a pool3 front that OVERLAPS between circle/square/
        triangle under gate G-a's own amended rule) does not produce a clean "nulls fall less" story;
        asserting one would misrepresent the data. Kept as a smoke test: every arm computes a finite,
        non-negative ratio at every seed."""
        theta_n = _theta_n_from_the_stream()
        g = _build_genome(theta_n)
        rows = []
        for seed in SEEDS:
            seq = _repeating_block_stream(seed)
            wrng = np.random.default_rng(seed + 1000)
            shuffled_words = [THINGS[i] for i in wrng.integers(0, 3, size=len(seq))]
            prng = np.random.default_rng(seed + 2000)
            order = prng.permutation(len(seq))
            shuffled_order = [seq[i] for i in order]
            _e, fd, ld = _run(g, seq, blank_zero=True)
            _e, fw, lw = _run(g, seq, blank_zero=True, words=shuffled_words)
            _e, fp, lp = _run(g, shuffled_order, blank_zero=True)
            for f, l in ((fd, ld), (fw, lw), (fp, lp)):
                self.assertGreater(f, 0.0); self.assertGreaterEqual(l, 0.0)
            rows.append({"seed": seed, "design": ld / fd, "word_shuffled": lw / fw, "picture_shuffled": lp / fp})
        self.null_rows = rows   # carried for the report; not asserted, see module docstring


class TestRetinaDim(unittest.TestCase):
    """retina_dim's fix (machinery.py, this task): pool/hogcells sizing reads the genome's OWN eye side
    instead of a hardcoded 24 (discovered building this toy's 32x32-eye canvas attempt — the dead end
    described in the module docstring — where SENSE eye 32x32 + RETINA pool4 crashed on a shape mismatch:
    retina_dim said 36, the real feature vector was 64). Never exercised by the pin (G4-skeleton.genome's
    only feature block is `tower:`, untouched by this change) — pinned here in both directions."""

    def test_default_side_24_unchanged(self) -> None:
        self.assertEqual(retina_dim(("pool3", "unit")), 64)          # (24 // 3) ** 2
        self.assertEqual(retina_dim(("pool4", "unit")), 36)          # the OLD hardcoded-24 answer, still what a 24-side genome gets

    def test_side_32_now_correct(self) -> None:
        self.assertEqual(retina_dim(("pool4", "unit"), side=32), 64)  # (32 // 4) ** 2 — was wrongly 36 before this fix


class TestFile(unittest.TestCase):
    def test_each_missing_field_refused_by_name(self) -> None:
        base = {"claim": "circle-cell-3 answers circle", "route": "ask Q1 on a held-out circle",
                "decider": "held-out accuracy", "due": "moment 1000"}
        for missing_field in FILE_FIELDS:
            with self.subTest(missing=missing_field):
                args = dict(base); args[missing_field] = ""
                row = file(**args)
                self.assertFalse(row["accepted"])
                self.assertEqual(row["refused"], [missing_field])
                self.assertEqual(row["row"][missing_field], "")

    def test_complete_claim_accepted(self) -> None:
        row = file("circle-cell-3 answers circle", "ask Q1 on a held-out circle", "held-out accuracy", "moment 1000")
        self.assertTrue(row["accepted"])
        self.assertEqual(row["refused"], [])
        self.assertIsNone(row["outcome"])

    def test_score_marks_it_right_against_planted_evidence(self) -> None:
        row = file("circle-cell-3 answers circle", "ask Q1", "the held-out accuracy reads >= .9", "moment 1000")
        planted_evidence_right = {"held_out_accuracy": 0.94}
        decider = lambda r: planted_evidence_right["held_out_accuracy"] >= 0.9
        graded = score(row, decider)
        self.assertTrue(graded["outcome"])
        self.assertTrue(row["outcome"] is None, "score() must not mutate the input row")
        planted_evidence_wrong = {"held_out_accuracy": 0.3}
        decider2 = lambda r: planted_evidence_wrong["held_out_accuracy"] >= 0.9
        graded2 = score(row, decider2)
        self.assertFalse(graded2["outcome"])

    def test_score_with_a_plain_value(self) -> None:
        row = file("a", "b", "c", "d")
        self.assertTrue(score(row, True)["outcome"])
        self.assertFalse(score(row, False)["outcome"])
        self.assertFalse(score(row, 0)["outcome"])

    def test_score_refuses_a_refused_row(self) -> None:
        refused = file("", "b", "c", "d")
        with self.assertRaises(ValueError):
            score(refused, True)

    def test_append_ledger_round_trip(self) -> None:
        import json
        row1 = file("a", "b", "c", "d")
        row2 = score(file("e", "f", "g", "h"), True)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "sub" / "predictions.jsonl"
            append_ledger(path, row1)
            append_ledger(path, row2)
            lines = path.read_text().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["row"]["claim"], "a")
        self.assertEqual(json.loads(lines[1])["outcome"], True)


class TestModulate(unittest.TestCase):
    def test_clipped_to_0_5_and_2_0(self) -> None:
        g = _build_genome(theta_n=0.85)
        org = Organism(g)
        pred = Predictor(org)
        x = np.zeros(g.sight_dim())   # zero-norm expect() and actual -> cos=0 -> error=1.0 initially; force exact errors instead:
        pred.last_error = 0.0
        self.assertAlmostEqual(pred.modulate(1.0), 0.5)              # floor
        pred.last_error = 0.1
        self.assertAlmostEqual(pred.modulate(1.0), 0.8)              # 0.5 + 3*0.1, no clip
        pred.last_error = 2.0
        self.assertAlmostEqual(pred.modulate(1.0), 2.0)              # 0.5 + 6.0 -> clipped to ceiling
        pred.last_error = 0.5
        self.assertAlmostEqual(pred.modulate(2.0), 2.0 * 2.0)        # 0.5+1.5=2.0, exactly the ceiling; lr scales through

    def test_lr_scale_threads_into_delta_default_is_exact(self) -> None:
        """Organism.moment(x_s, x_w, lr_scale=1.0)'s default must be byte-identical to moment(x_s, x_w)
        (B6's own pin discipline, alongside the whole-skeleton pin in test_pin_skeleton.py)."""
        g = _build_genome(theta_n=0.85)
        rng = np.random.default_rng(1)
        seq = _repeating_block_stream(seed=1, cycles=1, block=5)
        org_a = Organism(g); org_b = Organism(g)
        for t, pic in seq:
            x = retina(pic, g.retina); xw = world.encode_word(t, True)
            org_a.moment(x.copy(), xw.copy())
            org_b.moment(x.copy(), xw.copy(), lr_scale=1.0)
        self.assertEqual(org_a.state_hash(), org_b.state_hash())


if __name__ == "__main__":
    unittest.main()
