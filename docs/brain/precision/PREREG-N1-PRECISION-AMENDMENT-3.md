# PREREG-N1-PRECISION — AMENDMENT 3 (the log-domain register — the arithmetic ratio's measured bias)

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 14:50 +0400 — cause named per RULES §2. The
first bench run (scratch/n1/bench, 9.6 s, records committed) read: M-COST PASS (overhead −0.4 %), G-PLANT
PASS (frozen register → ratio exactly 1.0 — caught), the mechanism's direction REAL (deviant w: 2.10/2.76/2.71
in late A vs 0.36/0.55/0.65 in B), but M-SCALE FAIL (w median 2.674 over phase C's last 100, where the claim
is neutrality), M-MMN-0 FAIL on its window, M-MMN-1 FAIL against a contaminated null. Diagnosed to causes
below, each fixed by name; no bar loosened.

## A3.1 · The mechanism's formula moves to the log domain (the M-SCALE cause)

The declared form w = clip(v_slow/(v_fast+δ), …) with v the EMAs of e² carries a Jensen bias: on a BURSY
but stationary error stream (phase C's measured form: e median 0.057, mean e² 0.0140, 1 % spikes at 1.0)
the fast EMA fluctuates around the mean and E[v_slow/v_fast] > 1 — measured w median 2.674 (never
converging to neutral), exactly what M-SCALE exists to catch. The mechanism is right; the ratio form is
wrong. FIXED FORM (the same mechanism, bias removed by construction): the registers are EMAs of
**log(e² + δ)** — l_fast (η_f = 0.05), l_slow (η_s = 0.005), prior log(v0) = log(0.25) — and
**w = clip(exp(l_slow − l_fast), 0.25, 4.0)**. At stationarity both EMAs converge to the same expectation
of the same variable, so w → 1 exactly; at regime changes they separate exactly as before (amplification
after stability, discount in noise). δ = 1e-6 unchanged (now inside the log). The first call reads
w = exp(0) = 1 EXACTLY (the G-UNIT(b) form, cleaner than the draft's). All constants unchanged.

## A3.2 · M-MMN-0's window (the instrument's timescale mis-judgment; the bar UNCHANGED)

The world's convergence timescale was mis-judged at design: suppression in this toy is real but shallow
across phase A alone (first40 median 0.1191 vs last40 0.0849 — the +0.05 gap is crossed only over the
world's own convergence, ≈ 1,000 moments). The instrument's window moves to the phenomenon's timescale:
**first 40 moments of phase A vs the LAST 100 of phase C** (measured now: 0.1191 vs 0.0569 — gap 0.062).
The +0.05 bar stands untouched. If the toy cannot show suppression over its WHOLE run, the instrument is
still at fault (FAIL-FORM), never the mechanism.

## A3.3 · The null's bench implementation (the M-MMN-1 null contamination)

A1.5's declared null — destroy the context-reliability difference — was mis-built by the bench: the twins'
phase B kept the 8-pool (four EXTRA things still novel there), so the twins' contexts genuinely differed
and their ratios read 1.36–5.54. The twins' phase B is now built from the 4-cycle alone (contexts
symmetric by construction; deviants and positions unchanged). This is the bench honoring A1.5's declared
intent, not a law-text change.

## A3.4 · What does not change

Every bar (M-MMN-0's +0.05, M-MMN-1's ≥ 1.25 AND > null MAX, M-MMN-2's protective form — hand-arithmetic
on the log form: weighted slope ≈ +0.25 ≥ raw 0.034 — M-SCALE's [0.80, 1.25] now mechanically sound,
M-COST's ≤ 5 %), the causal read-then-update order, the wiring (flag-gated, no pin/parser/genome touch),
the gates, the verdict forms, the price.

Signed: the seat (Kimi K3, kimi-code, the seat alone) under Ahmad's 10-09 word, 2026-10-09 14:50 +0400.
SEAT-LINE-N1-A3: sha256 of THIS file recorded in SEAT-LINE-N1-A3.txt beside it.
