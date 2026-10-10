# PREREG-N2-TRAJECTORY — expectations as short paths: generalised coordinates [value, rate] on the error stream (the N-road's second law)

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-10 06:46 +0400 — authored under the queue named
at CONTEMPLATE-1's and N1's signings («N2 (trajectories) may be written»), Ahmad's 10-09 «go ahead» on
the N-road, and N1's §0 design record («Later laws — N2 trajectories … — EXTEND this register home»).

## §0 · The road, the reading taken, and the scope named honestly

- Research of record: `docs/brain/RESEARCH-HUMAN-PREDICTIVE-NORMALIZATION.md` (2026-10-07): §2 maps P6
  **ABSENT** — «predictions are point expectations over the instant's words; no state carries a
  rate/velocity»; §3 names N2 (S class): *the brain's tracked quantities carry [value, rate] (order-2
  generalised coordinates); expectations become short paths — measured by: does a trajectory-bearing
  expectation score better on the tape's predictable stretches than the point form, at matched cost
  (twin, planted control, the null).*
- Sources and read-status (carried): Friston 2008 (generalised coordinates) and 2005 read whole at
  research time; Nassar's unexpected-uncertainty/volatility line scanned 2026-10-09 (abstracts,
  flagged) — it informs the DESIGN (the sign choice at §1.4) only, never a bar.
- **The scope choice, said plainly:** P6's row describes the WORD-level expectation (brain.py's
  `turn["expected"]` — the forced names per hypothesis). N2 v1 closes the absence at the MODULATION
  register's level — the seat's own N1 §0 framing («N2 extends the register home»): the organism's one
  error-currency gains generalised coordinates, so every later consumer of the stream reads a path,
  not a point. The WORD-level trajectory form (expectation sets that extrapolate) is a LATER rung,
  not claimed here. N1's registers stay byte-exact — this law is ADDITIVE (a sibling register behind
  its own flag); the composition when both flags are on is declared at §1.5.

## §1 · The mechanism (machine form; every constant declared BEFORE any reading)

The raw error `e` and N1's precision register stay exactly as verdicted. New, behind
`Predictor(..., trajectory: bool = False)` (default OFF: not one new line runs; the N1 wiring form),
threaded `Mind(..., trajectory: bool = False)` at BOTH construction sites (the init and the resume
rebuild — the same two lines N1 touched). NO genome/parser/machinery.py edit; registers in-memory
only, not persisted (N1's precedent, named honestly).

1. **The stream.** The register consumes the SAME log-error the precision register consumes:
   `le = log(e² + δ)`, δ = PRECISION_FLOOR (one stream, one δ — never a second constant).
2. **The register (generalised coordinates, order 2).** A value EMA `m` (η_m = 0.05, τ ≈ 20 moments —
   the present) and a rate EMA `r` (η_r = 0.05) over the value's own motion `d_t = m_t − m_{t−1}`
   (the smoothed difference — never the raw per-call difference, which is stream noise). Priors:
   `m_0 = log(0.25)` (N1's prior), `r_0 = 0`.
3. **Causal order (the predictive-coding form).** Per call: READ first — the path prediction from the
   previous state `p_t = m_{t−1} + r_{t−1}`; the trajectory's stream error `tpe_t = le_t − p_t` is
   journaled (the instruments' surface); the POINT twin's `spe_t = le_t − m_{t−1}` likewise (always
   both printed — the twin is inside the instrument); THEN `m` updates, THEN `r` updates with
   `d_t = m_t − m_{t−1}`. (The ramp arithmetic, checked at the verifier read: the value EMA lags a
   perfect ramp by ≈ τ·s, so tpe ≈ (τ−1)·s against spe ≈ τ·s — the path is better by exactly one
   lag unit while a trend persists, and r → s at convergence.)
4. **The weight (the organism-facing half).** `w = clip(exp(κ·r), 0.25, 4.0)` with κ = 1 declared:
   a sustained RISING error trend (the world changing — volatility) amplifies the modulator, a
   sustained falling trend (the stream being mastered) damps toward the floor. The sign choice is the
   Nassar volatility reading (flagged abstract-level); the bar never cites it — the bench's own
   arithmetic decides (§3). The clip is N1's exact [0.25, 4.0]: the worst-case learning-rate scale is
   identical to N1's; `modulate()`'s own [lo, hi] clip stands after, unchanged.
5. **Composition (declared, bounded).** precision ON + trajectory ON: `w_total = w_precision ·
   w_trajectory`, each clipped at its own register, `modulate()`'s clip final — the final scale is
   bounded by construction. Each flag ALONE reproduces exactly its own law's form (N1 byte-exact when
   trajectory is OFF).
6. **modulate()**: flag OFF — byte-identical (today's formula). Flag ON — the SAME formula on the
   weighted error `e·w` (N1's substitution form). `last_error` stays RAW; `last_weight`/`last_rate`
   are instrument reads only.

## §2 · Gates (instruments first)

- **G-UNIT** — `tests/genome/test_predict_trajectory.py`:
  (a) flag OFF: a scripted error sequence's `modulate()` outputs byte-identical to master's (the
      regression pin);
  (b) causality: the first call reads w = exp(κ·0) = 1 exactly, and `tpe_1 == spe_1` (r₀ = 0);
  (c) planted ramp: a scripted linear le-ramp (slope s planted) — r converges into [s/2, 2s] inside
      the declared window, and tpe < spe over the ramp's tail;
  (d) determinism: two identical runs give identical (m, r, w, tpe) sequences to the last digit;
  (e) degenerate stream (e ≡ 0): no NaN/inf; r decays toward 0; w stays inside the clip.
- **G-IDENTITY** — flag OFF: the N1 gate's own two inputs (the toy tape; the bl2 500-row segment —
  copied from the n1 lane's scratch copy into this worktree's own scratch; lives never touched in
  place) replayed byte-identical master vs new.
- **G-PLANT** — a doctored register with r frozen at 0 (w ≡ 1, tpe ≡ spe) MUST BE CAUGHT by M-PATH:
  the instrument proves it can see the mechanism's absence before any pass is trusted (#246 (1)).

## §3 · The toy world and the marks (every bar written BEFORE the arms run)

The N1 bench's own toy world and tape form (genome `genome/G4-skeleton.genome`, 8 things): phase A
(a predictable 4-thing cycle, 400 moments — the learning stretches carry a real error downtrend,
M-MMN-0's own evidence) and phase B (the 200-moment seeded-irregular world — stationary). The
planted ramp control rides phase B (a scripted linear addition to the le stream, slope declared).
Null: 10 shuffled-delta twins PER PHASE (the le sequence's first differences deranged within the
phase, 10 fixed seeds — the distribution kept, the trends destroyed).

- **M-PATH** (the mechanism's core mark): on phase A's declared learning stretches (the cycle-
  learning windows — N1's M-MMN-0 windows), mean |tpe| ≤ mean |spe| − margin, paired per-moment,
  the smallest passing gap printed (#245 (5)); the margin must EXCEED the null distribution's MAX
  (§4). Bar: null MAX, printed.
- **M-STAT** (matched cost where there is no trend): on phase B, mean |tpe| ≤ mean |spe| + ε,
  ε declared from the pilot and printed — the trajectory may never systematically hurt a stationary
  stream.
- **M-RAMP** (the planted control): on the planted ramp, r ∈ [s/2, 2s] after the declared convergence
  window (2 × 5τ = 200 ramp moments — #254 (3): a young register reads its prior, and r reads m's
  motion, so the rate settles only after the value does: 5τ for m, then 5τ for r), and tpe < spe
  over the ramp's tail (the arithmetic: on a perfect ramp the path removes one lag unit —
  |tpe| ≈ (τ−1)·s against |spe| ≈ τ·s; a frozen-r register reads tpe ≡ spe — the G-PLANT twin).
- **M-SCALE**: median w over the whole run ∈ [0.80, 1.25]; the clip-bound share printed with its
  presence count and the ceiling computed from the tape's own counts (#228).
- **M-COST**: ON vs OFF per-row process_time overhead ≤ 5 %, both directions timed and printed.

## §4 · The null

10 shuffled-delta twins per phase (the rows kept, the trends destroyed). M-PATH's margin (spe − tpe)
is computed for every twin; the real run's margin must exceed the null distribution's MAX (≥ 10
draws, never one — #244 (2)).

## §5 · Verdict forms

- **PASS**: every gate + M-PATH + M-STAT + M-RAMP + M-SCALE + M-COST, the plant CAUGHT.
- **FAIL-FORM**: the toy's trends are too weak to read (the pilot's phase-A separation inside noise)
  — instrument fault; fix under a written AMENDMENT naming the cause.
- **FAIL-MECHANISM**: the instrument works and the path never beats the point — trajectory-bearing
  expectation does nothing here. A result; the road re-thinks. Bars never loosened.
- **VOID**: G-IDENTITY or G-PLANT fails anywhere.

## §6 · Price

Ceilings declared (measured values replace them in the verdict, RULES §6d/§6f): the toy build + all
arms + the 10-draw null ≤ 30 CPU-min; the identity replays ≤ 10 CPU-min; peak memory ≤ 1 GB
(SLOT_MEM=1G). Total law < 1 CPU-h. Every run through `/data/dev/swarm/bin/slot`.

## §7 · Adversarial walk

- Log domain throughout (#254 (2): EMA-ratios are Jensen-biased in the arithmetic domain) — the
  register consumes le, never e² directly.
- The streams are sized ≥ 5τ at the declared η (#254 (3): a young register reads its prior) — every
  graded stretch is ≥ 100 moments; the convergence window is declared 5τ.
- The rate is the EMA's own motion, never the raw per-call difference (a one-line low-pass; the raw
  form's noise measured at drafting: le differences swing ± orders while m's motion is smooth).
- The composition's worst case is bounded (each w clipped, modulate's clip final); last_error raw —
  the journal, act grading and sleep ranking read the same numbers as today.
- The ablated system is scored on the mark's own items BEFORE the mark is trusted (G-PLANT).
- The weight's SIGN choice (amplify on rising volatility) is a design reading of the flagged
  literature; the bars that grade it come from the tape's own arithmetic, never the citation.
- Every «first / by N / every» clause in this law is counted against the record at verdict time.

## §8 · Signatures

- Author: Kimi Code (K3, kimi-code, the seat alone) — 2026-10-10 06:46 +0400.
- Verifier loop: the seat's own adversarial read, recorded in `verify/N2-VERIFIER-READ.md` beside
  this law before the seat signs (the alone-era pattern — PREREG-REVISE-1's precedent today).
- The seat: SIGNED under Ahmad's 10-09 words. SEAT-LINE: sha256 of this file (pre-signature)
  recorded in `SEAT-LINE-N2.txt` beside this law.
