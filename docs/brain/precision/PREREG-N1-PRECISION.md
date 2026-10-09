# PREREG-N1-PRECISION — precision-weighted surprise (the N-road's first law)

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 13:58 +0400 — authored under Ahmad's 10-09 word
(«go on the building and experiments. Try short experiments first and then if there's some long experiment is
needed, put that to last»). The N-road opens with its shortest rung.

## §0 · His word, the road, and where this sits

- Research of record: `docs/brain/RESEARCH-HUMAN-PREDICTIVE-NORMALIZATION.md` (2026-10-07): §2 maps P4
  **ABSENT** — surprise is a raw word-overlap / novelty count, «no precision register anywhere»; §3 names
  N1 the first law (S class): *surprise becomes precision-weighted — every error channel carries a learned
  inverse-variance register, updated to match expected vs observed squared error (Friston 2008's M-step
  rule); the instrument that proves it is the repetition-suppression analogue (first exposure large error,
  Nth near zero, a deviant row re-evokes it — Friston 2005's MMN shape). Why first: it is the cheapest and
  it normalizes every later surprise measurement.*
- Sources and read-status (carried from the research doc §5): Friston 2005, 2008 and Bastos et al. 2012
  read whole at research time; Nassar (NE/unexpected-uncertainty) and the 2025–2026 literature scanned
  2026-10-09 (abstracts; flagged as such) — they inform the DESIGN only, never the bars.
- The one-body framing (Ahmad's 10-09 question, answered in the design record): this register is the
  first strand of the organism's ONE modulation layer — a single broadcast error-currency the organs
  share (the brainstem's neuromodulator broadcast is the human form). Later laws (N2 trajectories, N5
  schema gate, B7's two doubts) EXTEND this register home; there will never be per-organ forks of the
  precision idea.

## §1 · The mechanism (machine form; every constant declared BEFORE any reading)

The raw error `e` stays exactly as today (all four PREDICT arms untouched; `last_error` carries the RAW
value — the journal, act grading and sleep-replay ranking keep reading raw, byte-comparable records).

New, behind a flag (default OFF):

- Two variance registers on the raw error stream: `v_fast` (EMA, η_f = 0.05) and `v_slow` (EMA,
  η_s = 0.005), floor δ = 1e-6. Machine-form constants, fixed here before any reading (the OW-3 pattern).
- The precision weight: `w = clip(v_slow / (v_fast + δ), 0.25, 4.0)`.
- Causal order: the weight is READ from the registers first; THEN both registers update with this `e`.
  First error call: the registers initialize at `e²` and `w = 1` — the exact old road's first moment.
- `modulate()`: flag OFF — byte-identical (`lr × clip(0.5 + 3e, lo, hi)`). Flag ON — the SAME formula on
  the weighted error: `lr × clip(0.5 + 3·(e·w), lo, hi)`. The `[lo, hi]` clip is unchanged: the worst-case
  learning-rate scale is identical with the flag on (bounded by construction).
- Instruments read `Predictor.last_weight` (None when off). Read-only; nothing else sees it.

**Why the two-timescale ratio is the mechanism** (the design walk, recorded): precision weighting must
answer «how surprising, GIVEN this stream's own recent reliability». A single-register inverse-variance
ratio (π/π̄ over one EMA) is ≈ 1 at every stationarity — it carries no signal (walked and rejected). The
fast/slow variance ratio separates exactly at regime changes: after a stable stretch a deviant reads
w > 1 (amplification — the trained-predictable context), inside a noisy stretch the same deviant reads
w ≤ 1 (discounting). That is the MMN analogue's modulator form, and it costs two float EMAs.

**Wiring** (the OW-3 pattern): `Predictor(..., precision: bool = False)`; `Mind(..., precision: bool =
False)` threaded at BOTH construction sites (creature/mind.py:597 the init, :4351 the rebuild). NO genome
line, NO parser branch, NO `genome/machinery.py` edit — the WORLD_CODE pin (machinery.py, world.py,
cache.py) is not touched; no cache redraw, no fresh run root. Registers are in-memory only, not persisted
at resume (the G5-E `_word_seen` precedent, named honestly; a live-life clause is a later law's business —
this law benches only).

## §2 · Gates (instruments first)

- **G-UNIT** — `tests/genome/test_predict_precision.py`:
  (a) flag OFF: a scripted error sequence's `modulate()` outputs are byte-identical to master's (the
      regression pin, the G5-E `test_novelty_arm_is_byte_identical_to_pre_g5e` form);
  (b) causality: the first weighted call reads w = 1 exactly;
  (c) register response: after a scripted stable run a planted deviant reads w > 1; after a scripted
      noisy run the same deviant reads w ≤ 1;
  (d) determinism: two identical runs give identical w sequences to the last digit;
  (e) degenerate stream (e ≡ 0): w stays inside the clip, never NaN/inf.
- **G-IDENTITY** — flag OFF: (i) the toy tape (§3) replayed byte-identical master vs new code;
  (ii) a 500-row brain-long-2 tape segment (copied from the w2 lane's scratch copy into this worktree's
  own scratch — lives never touched in place) replayed byte-identical master vs new.
- **G-PLANT** — a doctored build with the register frozen (`v_fast ≡ v_slow` at every update) must yield
  w ≡ 1 and MUST BE CAUGHT by M-MMN-1: the instrument proves it can see the mechanism's absence before any
  pass is trusted (#246 (1), #247 (5)).

## §3 · The toy world and the marks (every bar written BEFORE the arms run)

**The toy** (deterministic): genome `genome/G4-skeleton.genome`; 8 things drawn by
`genome/world.render_canvas` (fixed seeds); ear+eye moments.

- Phase A (a predictable world): 400 moments, 4 things in a fixed cycle.
- Phase B (a noisy world): 200 moments, all 8 things in a seeded irregular order.
- Six planted deviant canvases of a held-out 9th thing (never shown in the cycle): moments 350/375/399 of
  phase A and 50/100/150 of phase B (phase-B deviants sit past v_fast's ~20-moment time constant).
- The tape ≈ 1,200 rows; a full bench run is minutes.

**Marks:**

- **M-MMN-0** (instrument control): the RAW error shows repetition suppression in phase A — first-cycle
  median e ≥ last-cycle median e + 0.05 (the G5-E table's own absolute form). If the toy cannot show
  suppression the instrument is at fault (FAIL-FORM), never the mechanism.
- **M-MMN-1** (the mechanism's mark): over the planted deviants, median w(late phase A) ≥ 1.25 ×
  median w(phase B). The 1.25 is the declared bar; the null (§4) supplies the ceiling.
- **M-MMN-2** (suppression never shallower): phase A's weighted-error suppression slope (first-cycle
  median minus last-cycle median) is positive and ≥ the raw slope's. (Protective form: with last-cycle
  errors at ~0 the weighted and raw slopes coincide — this bar's job is to catch a precision path that
  DAMPENS suppression; M-MMN-1 carries the mechanism's signal.)
- **M-SCALE**: (i) median w over the whole run ∈ [0.80, 1.25] — the register calibrates, it must not
  systematically inflate; (ii) the clip-bound share (w at 0.25 or 4.0) printed with its presence count,
  with the ceiling computed from the tape's own counts (#228): clip_share ≤ (share of moments whose raw
  e ≡ 0 exactly) + 0.05 — pinning is admissible only where the world went perfectly predictable (after an
  exactly-learned canvas, e = 1 − cmax = 0, v_fast decays toward 0, and w at the top clip is the CORRECT
  signal: a maximally trusted channel). A register that clips beyond what exact-zero errors explain is
  inflating, caught.
- **M-COST**: ON vs OFF per-row process_time overhead ≤ 5 %, both directions timed and printed.

## §4 · The null

10 shuffled twins: moment order shuffled WITHIN each phase (10 fixed seeds; the rows kept, the repetition
structure destroyed). M-MMN-1's ratio is computed for every twin; the real run's ratio must exceed the
null distribution's MAX. (≥ 10 draws, never one — #244 (2).)

## §5 · Verdict forms

- **PASS**: every gate + M-MMN-1 + M-MMN-2 + M-SCALE + M-COST, the plant CAUGHT.
- **FAIL-FORM**: M-MMN-0 fails — the toy cannot show suppression; instrument fault; fix under a written
  AMENDMENT naming the cause.
- **FAIL-MECHANISM**: the instrument works and M-MMN-1/2 fail — precision-weighting does nothing here. A
  result; the road re-thinks. Bars never loosened.
- **VOID**: G-IDENTITY or G-PLANT fails anywhere.

## §6 · Price

Ceilings declared (measured values replace them in the verdict, RULES §6d/§6f): the toy build + all arms +
the 10-draw null ≤ 30 CPU-min; the bl2 segment replay ≤ 10 CPU-min; peak memory ≤ 1 GB (SLOT_MEM=1G).
Total law < 1 CPU-h. Every run through `/data/dev/swarm/bin/slot`.

## §7 · Adversarial walk (where can the mechanism fire wrongly)

- `modulate()`'s organism caller is machinery.py:1555's per-moment DELTA scaling: w is clipped
  [0.25, 4.0] and modulate's own [lo, hi] clip is unchanged — the worst-case learning-rate scale is
  IDENTICAL with the flag on. No runaway path exists.
- `last_error` stays raw: act grading, the journal and sleep replay rank by the same numbers as today;
  master-vs-new twins are byte-comparable.
- The ablated system is scored on the mark's own items BEFORE the mark is trusted (G-PLANT; #246 (1)).
- Every «first / by N / every» clause in this law is counted against the record at verdict time.
- Persistence: the registers are in-memory (replay benches build fresh Minds); no live-life clause is
  claimed here; a resumed bench run re-derives nothing (the gap is named, as G5-E named `_word_seen`).

## §8 · Signatures

- Author: Kimi Code (K3, kimi-code, builder) — 2026-10-09 13:58 +0400.
- Verifier loop: the seat's own adversarial read, recorded in `verify/N1-VERIFIER-READ.md` beside this
  law (the seat-alone pattern under Ahmad's standing word — PREREG-W2 AMENDMENT 1's precedent: the
  verifier loop still run).
- The seat: SIGNED under Ahmad's 10-09 word. SEAT-LINE: sha256 of this file (pre-signature) recorded in
  `SEAT-LINE-N1.txt` beside this law.
