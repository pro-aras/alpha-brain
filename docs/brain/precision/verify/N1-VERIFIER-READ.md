# N1 — the verifier read (the seat running the verifier loop on its own draft, recorded)

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 14:05 +0400 — adversarial read of
PREREG-N1-PRECISION draft 1, BEFORE signature. Two exceptions, both resolved in the signed text.

## Exceptions

**V1 (material) — M-SCALE's first form contradicted the mechanism's own correct behavior.** Draft 1
barred mean w outside [0.90, 1.10] over the whole run. But after an exactly-learned canvas the raw error
is e = 1 − cmax = 0.0 EXACTLY; with δ = 1e-6 the fast register decays geometrically toward 0 and w pins
at the top clip 4.0 for the tail of a stable phase — the register behaving CORRECTLY (a maximally trusted
channel) while the bar reads it as inflation. A law that fails its own mechanism's correct mode is a
defective instrument. RESOLVED in the signed text: M-SCALE is now (i) median w ∈ [0.80, 1.25] and (ii) the
clip-bound share with its presence count, ceilinged by the tape's own counts (clip_share ≤ exact-zero-error
share + 0.05, #228's own form). δ stays 1e-6 (declared, unchanged).

**V2 (clarity) — M-MMN-2's signal is thin.** With last-cycle errors at ~0 the weighted and raw suppression
slopes coincide, so «steepened» reads ≈ equal. RESOLVED: the bar stands as the protective form (weighted
slope ≥ raw slope — never shallower), its purpose recorded; M-MMN-1 carries the mechanism's signal.

## Verified clean (each checked against the code, not the draft's say-so)

- The causal order (weight read BEFORE the registers update) and the first-call w = 1 form.
- The deviant positions: phase-B deviants at 50/100/150 sit past v_fast's time constant (η_f = 0.05 →
  τ ≈ 20 moments); late phase-A deviants (350/375/399) read v_slow's early-transient anchor.
- The plant: a frozen register (v_fast ≡ v_slow) yields w ≡ 1 → M-MMN-1's ratio ≈ 1 < 1.25 → CAUGHT.
- Determinism: two float EMAs, no RNG anywhere on the new path.
- Flag-off byte-identity: every new arithmetic line sits behind `if self.precision:` — the OFF path runs
  the same instructions in the same order (the G5-E pin form).
- The worst-case bound: w ∈ [0.25, 4.0] and modulate's [lo, hi] clip unchanged → the worst-case learning
  rate scale is identical with the flag on (no runaway path).
- Both construction sites named in §1 exist: creature/mind.py:595-598 (init) and :4351 (the resume-path
  rebuild — a resumed future life under a precision clause re-threads through it; replay benches never
  resume, the G5-E `_word_seen` precedent for non-persisted registers).
- The pin is untouched: §1's diff names genome/predict.py + creature/mind.py only; machinery.py,
  world.py, cache.py absent → no cache redraw, no fresh run root.
- The null: 10 shuffled twins, real ratio must exceed the null MAX (≥ 10 draws — #244 (2)).
- mind.py's `Mind.__init__` signature verified: (genome_path, run_root, blind, eye_front) — the
  `precision: bool = False` thread follows the eye_front precedent exactly.

VERDICT OF THE READ: the two exceptions resolved in text, the rest clean — the law is signable.
