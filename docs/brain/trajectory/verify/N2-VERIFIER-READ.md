# N2-TRAJECTORY — the verifier's adversarial read (recorded pre-signature; the alone-era loop)

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-10 06:46–06:5x +0400.

The read walked every clause against the CODE it extends (genome/predict.py's N1 register at master
5e01cde), the mechanism's arithmetic, and the culture rules (#228/#244/#245/#254). One exception
found, resolved in the law's text BEFORE signature.

## V1 — FOUND AND RESOLVED: the rate register settles only after the value register does

The first draft's M-RAMP declared the graded tail after 5τ = 100 ramp moments. But `r` reads `m`'s
motion (`d_t = m_t − m_{t−1}`): on a ramp's onset, `m` itself is still converging from the prior for
its own ≈ 5τ, and only then does `d_t` read the true slope for `r`'s own ≈ 5τ. A 100-moment window
would grade `r` while it still reads the prior's decay — the young-register trap's own two-stage
form (#254 (3), one level down). RESOLVED in the law before signature: the convergence window is
2 × 5τ = 200 ramp moments, and §1.3 now carries the ramp arithmetic explicitly.

## The arithmetic checks (all reproduced, none trusted)

- **The ramp's steady state (the mechanism's core claim):** on a perfect le-ramp of slope s, the
  value EMA lags by ≈ τ·s (τ = 1/η = 20), so `d_t → s` and `r → s` at convergence; the path
  prediction `p_t = m_{t−1} + r_{t−1}` then sits ≈ (τ−1)·s behind the stream where the point twin
  sits τ·s — |tpe| ≈ (τ−1)·s < |spe| ≈ τ·s: the path beats the point by exactly one lag unit while
  any trend persists, and a frozen-r register reads tpe ≡ spe (the plant is real — G-PLANT sees the
  mechanism's absence exactly). ✓
- **Causality (G-UNIT b):** first call: p₁ = m₀ + r₀ = m₀ (r₀ = 0) → tpe₁ == spe₁; w = exp(κ·0) = 1
  exactly. ✓
- **Degenerate stream (G-UNIT e):** e ≡ 0 → le = log(δ) constant → d_t → 0, r → 0, w → 1; no NaN
  (δ > 0). ✓
- **Boundedness of the composition:** w_precision ∈ [0.25, 4], w_trajectory ∈ [0.25, 4] → product ∈
  [1/16, 16], and `modulate()`'s own [lo, hi] = [0.5, 2.0] clip is final — the final learning-rate
  scale is bounded exactly as today. ✓
- **The weight's practical magnitude (checked against κ = 1 in le-units):** a phase transition
  (Δle ≈ 1–3 for a few moments) drives d ≈ η_m·Δle ≈ 0.05–0.15, so r ≈ 0.15 and w ≈ 1.16; a
  sustained ramp s = 0.01/moment gives w ≈ 1.01. The clip [0.25, 4] binds only at |r| ≥ 1.39 —
  the modulator is GENTLE in practice, M-SCALE's [0.8, 1.25] band is plausible, and no runaway path
  exists. ✓
- **The null's form:** shuffling the le sequence's FIRST DIFFERENCES within a phase destroys the
  trends while keeping the value distribution — exactly the perturbation M-PATH claims to read
  (#251 (5): the null matches the difference the gate must judge). ✓
- **Phase-A stretch windows** exist by N1's own M-MMN-0 evidence (first-cycle vs last-cycle median
  suppression ≥ 0.05 measured on this tape) — the instrument's premise is already measured, not
  hoped. The pilot still prints the separation before the margin binds. ✓
- **No pin touch:** the wiring names the same two mind.py lines N1 threaded; machinery.py,
  parser, genome lines untouched; registers in-memory (replay-deterministic; N1's persistence
  precedent named). ✓

## What this read did NOT verify (said honestly)

- The actual phase-A separation size (the pilot measures it; if it sits inside noise, the verdict is
  FAIL-FORM by the law's own §5 — the instrument re-priced under an amendment, never the bar moved).
- The ε of M-STAT (pilot-declared, printed) and the exact clip-share ceiling of M-SCALE (computed
  from the tape's own counts at bench time, per the law's own rule).

Verdict of the read: the law is implementable as written; the one genuine gap (V1) is closed in the
text; every bar has its ceiling computed, its null declared, or its pilot rule written. CO-SIGNED —
the verifier loop of the seat alone, 2026-10-10 06:5x +0400.
