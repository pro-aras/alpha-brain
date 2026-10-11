# VERDICT-DRAFT-N2-TRAJECTORY — the evidence for the seat's walk

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 13:1x +0400 — the builder's reading, written
after the bench's honest FAIL and the four pricing probes (records/PROBES.md). The law:
docs/brain/trajectory/PREREG-N2-TRAJECTORY.md (signed 2026-10-10, n2-1010 @ ffd2901).

**WHAT FAILED (named first): M-PATH and M-RAMP, measured, never tuned.** The reading of record is the
law's §5 FAIL-FORM row: the toy's trends are too weak to read — the pilot's phase-A separation sits
inside the nulls' noise, measured four ways (below). The mechanism is NOT refuted: every gate green,
the no-harm marks pass, the plant is caught, and the clean-carrier arithmetic is exact.

## Gates

- **G-UNIT — PASS (7/7).** RED proven on the merged branch (1 import error: the module absent;
  scratch/n2/gunit-red.log exit 1) → GREEN (records/gunit-green2.log exit 0): (a) flag OFF
  byte-identical to the old formula, the registers never touched; (b) causality — the first call reads
  w = exp(κ·0) = 1 EXACTLY, tpe == spe EXACTLY; (c) the scripted clean ramp — r ∈ [s/2, 2s] at the
  declared window (2×5τ = 200), the one-lag-unit tail arithmetic (gap ∈ [s/2, 2s]); (d) determinism to
  the last digit; (e) the degenerate e ≡ 0 stream bounded, r decays toward 0, w in the clip; (f) the
  Mind thread; (g) the composition pin — w_total = clip(w_p)·clip(w_t) mirrored inline to the last
  float digit. One test-order fault of the builder's own caught by the pin ((3.0·e)·w vs 3.0·(e·w),
  one ULP — the mirror now follows production's order; named, fixed before GREEN).
- **G-IDENTITY — PASS, to the digit.** Both of the N1 gate's own inputs replayed flag-OFF master vs
  branch: the toy tape **a7280723…** and the bl2 500-row segment **26dc80c6…** REPRODUCE the journals
  of record exactly (records/identity-shas.txt; cmp exit 0 ×2; branch n2-1010 @ 39781fe, master
  5a997b7; through slot, 2G caps; journal rows 200/662 > 0 — the empty-replay trap guarded).
- **G-PLANT — CAUGHT.** The frozen-r register (w ≡ 1, tpe ≡ spe — pinned by
  tests/tools/test_trajectory_bench.py's test_plant_register_frozen_r to the exact float) reads M-PATH's
  margin EXACTLY 0.0 < the twins' MAX — the instrument sees the mechanism absent (report G-PLANT PASS).
- **G-DET — PASS.** Two full bench runs byte-identical except cost.json (records/gdet.diff, diff -r
  --exclude=cost.json exit 0).
- Neighbors: tests.genome.test_predict_precision + test_predict + test_b13_modulation_arrival 25 OK
  (records/gunit-neighbors.log) — the composition restructure is N1-byte-exact.
- Bench tests: 6/6 OK (records/bench-tests.log).

## Marks (the run of record: records/bench-run1; bench-run2 byte-identical)

- **M-PATH — FAIL.** margin = mean|spe| − mean|tpe| over the pooled learning stretches = **+0.007568**
  (n 200; per stretch: [0,100) +0.014632, [100,200) +0.000503); the 10 shuffled-delta twins read
  +0.0353 … +0.2583, MAX 0.258290 — the real margin does not exceed the null MAX (smallest passing gap
  −0.2507). The margin is honestly POSITIVE (the law's predicted direction) and NOT null-separable.
- **M-STAT — PASS.** phase B: mean|tpe| 2.850615 ≤ mean|spe| 2.849699 + ε (ε = 0.005, declared from the
  pilot: gap +0.000917, n 200). The trajectory never systematically hurts the stationary stream.
- **M-RAMP — FAIL.** The planted ramp (s = 0.01 riding phase B, 200 ramped calls confirmed): r_at_50
  0.0266, r_at_100 0.0087, r_at_150 0.0031, **r_end −0.00657** ∉ [0.005, 0.02]; the tail's gap
  −0.002907 (tpe ≥ spe). Cause measured (records/PROBES.md probe 0): the register truthfully reads the
  composite stream; the planted 0.01 is swamped by the carrier's own ±0.07–0.15/window motion.
- **M-SCALE — PASS.** median w over the whole run 0.996947 ∈ [0.80, 1.25]; clip share 0.0
  (presence 0 of 600 at either bound).
- **M-COST — PASS.** ON vs OFF process_time overhead ≤ 5 % (timings in cost.json; the report's
  D-cost form keeps report.json/report.txt byte-deterministic).

## The pilot (printed FIRST, before any mark bound)

Phase-A per-quarter margins: A[0,100) +0.015935, A[100,200) −0.001725, A[200,300) −0.000554,
A[300,400) −0.001538 — the advantage concentrates in the first learning window and dies; phase-B gap
+0.000830 → ε 0.005. This is the law §4's FAIL-FORM parenthetical, measured: the pilot's phase-A
separation is inside the nulls' noise.

## The four pricing probes (records/PROBES.md — the amendment candidates priced and REFUSED on numbers)

1. The shuffled-DELTA null is a random-walk generator (margins 0.035–0.258 — the path exploits a random
   walk BETTER than the real learning stream; the null cannot grade).
2. The row-shuffle null reads +0.0058…+0.0086 pooled / +0.0133…+0.0191 on [0,100) — the real margins
   (0.0076 / 0.0146) are inside both. The phase-A value distribution's two-level spread gives even
   value-permuted streams a jump structure the path exploits at the real trend's own order.
3. The self-paired statistic is contaminated by the register's own warm-up (twins read +0.016…+0.021
   from the artifact alone).
4. Warm-up-controlled, the real [0,100) margin +0.0050 vs the row-null MAX +0.0068 — STILL inside.
   (The honest map after warm-up control: [0,100) +0.0050, [100,200) +0.0003, [200,400) −0.0007.)

The A-tail «quiet carrier» candidate for M-RAMP is not quiet (windowed slopes +0.036/−0.007/−0.041/
−0.136); on it the ramp's r lands in-window (0.0084) but the tail arithmetic does not bind (gap
+0.0003 vs ~s). The one-lag-unit arithmetic binds only on a clean carrier — the G-UNIT (c) form,
which PASSES at unit scale.

## The builder's honest readings

- **The mechanism is not refuted.** The register executes the law's arithmetic exactly where the
  instrument can see it (G-UNIT (c)); the real-stream margins are positive exactly where the law
  predicts and die exactly as the learning completes; no-harm on stationary; no clip touch in 600
  moments; cost inside the bar; the organism's le stream is untouched by the weight at bench scale
  (probe 0's refused feedback hypothesis).
- **The toy cannot certify the claim.** The path's advantage is real but GENERIC: it exploits any
  temporal structure (random walks 0.035–0.258), so no permutation null at this scale can isolate
  «the learning trend». Certifying M-PATH wants a world whose mastery descent dominates the
  shuffle-exploitable structure by a declared factor — a NEW WORLD's law (a steep-descent curriculum
  world), not an amendment of this bench's constants. Certifying M-RAMP's organism-scale arithmetic
  wants a carrier whose own motion is declared-quiet at the window scale — the same world question.
- **The register code stays on the branch, flag-gated OFF, byte-identical OFF (G-IDENTITY's own
  proof).** Nothing merges on a FAIL. A future world law revives the branch's instrument as-is.
- The ramp arithmetic's assumption («the planted slope dominates the carrier») is the law's own
  mis-pricing, measured — named for the next law's author: an organism-scale planted control must be
  priced against the carrier's measured windowed motion FIRST (the probe-before-signature rule held
  here would have caught it at drafting).
