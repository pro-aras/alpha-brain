# N2 PRICING PROBES (scratch-born, flagged — the verdict's evidence; run after the bench's honest FAIL,
# never a graded run, never a bar moved)

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 13:0x +0400.

All probes read the run of record (`records/bench-run1/arms.jsonl`, the real arm's le journal) and drive
fresh registers via the register's OWN step (`_trajectory_step` — never a re-implementation). Numbers
verbatim from the probe outputs.

## Probe 0 — the register exoneration (the ramp-arm composite reading)

The ramp arm's CONSUMED stream (le + 0.01·k over phase B, k=200 ramped calls confirmed) fed through a
fresh register: r tracks the consumed stream's 50-moment windowed mean slope, lagged — k=50 slope
+0.14971 → r 0.03898; k=100 slope −0.07020 → r 0.00180; k=150 slope +0.11265 → r 0.00340; k=199 slope
−0.11940 → r −0.00732. The injection adds exactly +0.01 on average (consumed mean slope over B +0.0234
vs the real part's +0.0134). The register truthfully reads the composite; the planted 0.01 is swamped
by the phase-B carrier's own ±0.07–0.15 per-window motion. The organism's le is NOT changed by the
trajectory weight at bench scale (the off-arm's and the trajectory-arm's le streams are identical:
B-half means −2.8103/−3.1189 both — the modulation-feedback hypothesis measured and REFUSED).

## Probe 1 — the row-shuffle null (the first amendment candidate)

The law's shuffled-DELTA twin is a random-walk generator (margins 0.0353–0.2583 over the ten seeds —
the path exploits a random walk BETTER than the real learning stream; the null cannot grade). The
row-shuffle form (le VALUES permuted per phase, 10 seeds 20261740–20261749), pooled stretches [0,200):
margins +0.005791 … +0.008621, MAX 0.008621. The real margin 0.007568 sits INSIDE (below the MAX).
The phase-A value distribution's two-level spread gives even a value-permuted stream a jump structure
the path exploits at the same order as the real learning trend.

## Probe 2 — the concentrated window [0,100) + the A-tail carrier candidate

- Real margin [0,100): +0.014632. Row-shuffle null [0,100): +0.013281 … +0.019116, MAX 0.019116 —
  the real margin is INSIDE (below) the null.
- The phase-A converged tail (moments 200..400) as a candidate QUIET ramp carrier is NOT quiet:
  windowed mean slopes (4×50) +0.036117, −0.006766, −0.041396, −0.135841 — as wild as phase B's.
- The planted ramp (s=0.01) riding the A tail: r at the window's end 0.008412 ∈ [0.005, 0.02] (the
  window binds) BUT the tail's one-lag-unit arithmetic does NOT: gap +0.0003 vs the arithmetic's ~s
  (mean|tpe| 1.151427 vs mean|spe| 1.151726 — the carrier's noise floor washes the arithmetic out).

## Probe 3 — the self-paired statistic (learning-window margin minus stationary-window margin)

Real: [0,100) +0.014632, [300,400) −0.001743, self-paired +0.016375. Row-shuffle twins self-paired:
+0.015905 … +0.021389, MAX 0.021389 — INSIDE again. Cause measured: the [0,100) window reads the
register's OWN warm-up transient (m₀/r₀ priors settling) on ANY stream — the twins' +0.016…+0.021
self-paired margins are the warm-up artifact, not the stream. Shuffled-DELTA twins under the same
statistic: −0.165758 … +0.061891 (wild, as a random walk's windows are).

## Probe 4 — warm-up-controlled (200-moment shared stationary run-in before the graded stream)

Real [0,100) after run-in: +0.005032. Row-shuffle twins after run-in: +0.002921 … +0.006816,
MAX 0.006816 — STILL inside (the real margin at ~the null's 60th percentile). The real margin's
profile after warm-up control: [0,100) +0.005032, [100,200) +0.000318, [200,400) −0.000694 — the
advantage CONCENTRATES in the learning window and dies (the law's predicted direction, honestly
positive) — but not separable from the nulls at this toy's scale.

## What the probes establish

1. The mechanism is NOT refuted: every real-stream margin is honestly positive where the law predicts
   it, M-STAT's no-harm holds (+0.0009 ≤ ε), the plant is caught (margin exactly 0), and the G-UNIT
   clean-ramp arithmetic is exact (r → s ∈ [s/2, 2s]; the one-lag-unit tail).
2. The toy CANNOT certify the law's M-PATH claim: the path's advantage on the real learning stretch is
   not separable from its advantage on ANY permutation twin — four null/statistic forms priced, all
   inside. The path exploits temporal structure GENERICALLY (random-walk margins 0.035–0.258), which is
   exactly why a permutation null cannot isolate «learning» at this scale.
3. The planted 0.01 slope is unreadable against ANY organism-scale carrier measured (phase B's
   ±0.07–0.15/window; phase A tail's ±0.04–0.14/window); the tail's one-lag-unit arithmetic binds only
   on a clean carrier (the G-UNIT form).
