# PREREG-N1-PRECISION — AMENDMENT 1 (the register init, the noisy world's true form, the M-SCALE repair, the null's repair)

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 14:15 +0400 — written BEFORE any code, in the
G-UNIT design walk (the verifier loop's continuation). The base law's gates, mechanism formula, wiring,
verdict forms and price are UNCHANGED except as named here. Cause named per RULES §2: three defects found
by hand-arithmetic on the draft's own design, before a line of code existed — exactly when amendments are
cheapest.

## A1.1 · The register init (cause: the first-call e² init inflates the anchor for hundreds of moments)

Draft §1 initialized the registers at the first error's square (e = 1.0 at birth, nothing alive). The slow
register (η_s = 0.005, τ ≈ 200) then carries the birth transient for ~400+ moments and poisons every
from-birth reading. FIXED FORM: both registers initialize at the declared prior **v0 = 0.25** (a
machine-form constant, the mid-scale variance of a [0, 2]-ranged error stream, fixed before any reading).
The first call's w = v0/(v0 + δ) = 1 falls out of the prior with no special case; the first moment's
modulate() is then identical to master's even with the flag ON (a maximal first error weighted by exactly
1). Causal order unchanged (read w, then update).

## A1.2 · The noisy world's true form (cause: 8 learnable things are not noisy — the birth machinery
absorbs them in one showing each, and phase B's error floor decays to phase A's level)

Phase B gains planted noise: every moment with i % 3 == 2 is a FRESH random-noise canvas (seeded per
moment, never repeated — nothing to learn; the world's error floor stays high). Phase-B deviants move to
moments **49 / 100 / 151** (all i % 3 == 1, clear of the noise slots, all past v_fast's τ ≈ 20). Phase B
is 200 moments as before (67 of them noise rows).

## A1.3 · The toy gains a stationary appendix (cause: the calibration claim was mis-specified)

The draft's M-SCALE (mean w ≈ 1 over the run) contradicted the mechanism's purpose: precision SHOULD sit
above 1 while a channel proves reliable and below 1 in a noisy one — the neutral point is only the claim
at TRUE stationarity. The toy gains phase C: moments 600–900, the phase-A cycle continued unchanged. At
phase C the slow register has converged (900 moments ≈ 4.5 slow time constants). **M-SCALE rewritten:**
(i) median w over the LAST 100 moments of phase C ∈ [0.80, 1.25] — at stationarity the weight is neutral,
  the calibration claim;
(ii) the clip-bound share over the whole run printed with its presence count — a READING, never a bar
  (pinning during reliability transitions is the mechanism being itself; inflation is caught by (i)).

## A1.4 · G-UNIT (c) rewritten comparative (cause: the absolute «noisy w ≤ 1» bar was mis-aimed — the
mechanism's claim is CONTRAST, not an absolute level)

(c) now reads: after the scripted stable stream a planted deviant reads w_stable > 1; after the scripted
noisy stream (every 3rd row fresh noise) the same deviant reads w_noisy < 1; and w_stable / w_noisy ≥
1.25. (Hand-arithmetic on the declared constants: stable ≈ clip-bound 4.0; noisy ≈ 0.27/0.33 ≈ 0.82.)

## A1.5 · The null repaired (cause: shuffling within a phase does not change a novelty error — resonance
is order-independent; the shuffled twins would reproduce the same w-contrast and the null would fail the
REAL run)

The null is re-aimed at the mechanism's claimed cause — the context-reliability difference: **10 no-noise
twins** (phase B's noise rows replaced by more cycle rows, 10 fixed seeds for the cycle orders; row counts
unchanged). In every twin, phase B is as reliable as phase A, so its deviants amplify the same way and the
M-MMN-1 ratio sits ≈ 1. The real run's ratio must exceed the null distribution's MAX (≥ 10 draws, never
one — #244 (2)). The shuffled-order form is dropped by name (it tests nothing for this mechanism).

## A1.6 · What does not change

The mechanism (§1's formula, the clip [0.25, 4.0], the causal order), the flag-gated wiring (no pin, no
parser, no genome edit; registers in-memory only), G-IDENTITY, G-PLANT (frozen register → w ≡ 1 → caught),
M-MMN-0 (phase A only, as written), M-MMN-1 (≥ 1.25), M-MMN-2 (protective form), M-COST (≤ 5 %), the
verdict forms, and the price (< 1 CPU-h; the appendix adds ~300 moments, still minutes-scale).

Signed: the seat (Kimi K3, kimi-code, the seat alone) under Ahmad's 10-09 word, 2026-10-09 14:15 +0400.
SEAT-LINE-N1-A1: sha256 of THIS file recorded in SEAT-LINE-N1-A1.txt beside it.
