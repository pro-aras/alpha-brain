# PREREG-HOMEOSTASIS — the drives law (Law 1 of the developmental road)

*edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 — DRAFT, NOT SIGNED. The queue of record:
`/data/research/advisor-opus/2026-10-12_opus46-developmental-road-FINAL-PLAN.md` (the advisor's two rounds,
his 10-12 order). Signature waits for: §0's bench numbers (the bench fires today), the constants chosen
from them (§2.2), and the adversarial walk (§8) answered against the real bench, in that order.
The house rules bind: law before code; bars never loosen; the OFF form is byte-identical; the planted
controls must be caught. The seat signs alone (his 09-29 word); this walk stands in place of a co-signer.*

## §0 · What was known before this text (the bench reading)

**Method (declared before the run).** TWO sources:
(a) the LIVE tape of brain-long-6's first day (production code ce628fa, the real shelf) — read 2026-10-12,
    the rates the drives will modulate;
(b) the CONTROLLED bench life `brain-long-6-h0s0` — production code ce628fa, the declared genome
    `genome/brain/lives/BRAIN-LONG-6-PREFLIGHT.genome` UNCHANGED (SEED 20261211, the declared toy shelf
    `/data/dev/brain-runs/alpha-6/bl5-preflight-toy/video-shelf`, REGISTERS armed — the pre-flights' own
    form, so §0 is comparable with the pre-flight records), fenced 4G, run to ≥ 52,000 moments
    (≥ 10,000 canvases), closed clean, then read by `tools/brain/homeostasis_s0.py` (the instrument, with
    its planted control). The GATE's runs (§3) get a FRESH never-used seed at signature — §0's seed is
    declared and reused, so no constant is fitted to the gate's world.

**§0(a) — the live baselines (measured 2026-10-12 on bl6's journals, the first 9.5 h).** The mouth rate
falls 26,184 → 1,544 says/h as the mean canvas err falls 0.601 → 0.255; the ask rate falls 757 (hour 1)
→ ~1/h by hour 3; fixations 2.00 per moment row (genome-fixed); state snapshots every 500 moments; sleep
boundaries every 2,500 moments (genome-fixed). THE FINDING THAT MOTIVATES THIS LAW: as the world becomes
predictable the organism goes quiet and stops asking — nothing seeks novelty. (The silence spiral.)

**§0(b) — the controlled bench table.** Per-1000-canvas windows: err (mean/std), the lr stream (precision's
fingerprint), says, asks, fixations, sleep boundaries observed — PLUS the three SHADOW drive series
computed offline over the real tape with the candidate update rules (§2.2's form, candidate constants):
arousal / boredom / fatigue, each printed min/max/mean/std per window.
**PENDING — the bench runs 2026-10-12; the table lands in this section before signature.**

## §1 · The question

Do three internal state variables — arousal, boredom, fatigue — perturbed by the organism's own experience
and modulating its behavior, produce measurably different and developmentally useful behavior vs a
flat-state organism? (The advisor's causal argument: compositionality and «why» are downstream of wanting;
wanting is downstream of drives. This law builds the drives.)

## §2 · The law

### §2.1 · The gene

```
HOMEOSTASIS  arousal boredom fatigue
```

One genome line after the FILE line (the REGISTERS line's own precedent). The parser gains ONE branch in
the pinned window's form (machinery.py — a pinned file: a fresh run root + the array-identity check, the
bl6 window's price paid again and declared in §6). Garbage (bare `HOMEOSTASIS`, unknown variable names,
repeats) refuses by name. ABSENT = byte-identical (every closed life replays equal; I1/I2 below).

### §2.2 · The state model (the candidate form; the CONSTANTS are chosen from §0(b)'s table at signature)

Discrete updates per canvas, all variables in [0, 1]:
- **arousal** — driven toward the canvas's surprise: `a ← clip(a + α·(s − a) + β·(REST_A − a))`, surprise
  `s` = the canvas's prediction error (the brain's own err row, the same stream precision reads);
  REST_A ≈ 0.3. Modulates: the global learning gain (multiplying into `modulate()` ALONGSIDE precision —
  the H-PRECISION arm decides interaction), fixations per canvas (+1 when a > 0.7), and sleep onset.
- **boredom** — rises only on SUSTAINED low surprise: `b ← clip(b + γ)` when `s < κ·s̄` (s̄ = the slow
  running mean surprise, its own EMA), else `b ← clip(b − δ·b)` toward 0. Modulates: the ask probability,
  the mouth's babble probability (speak without a say-target — §2.4), and at ceiling a SEEK act (the next
  world source in the round-robin).
- **fatigue** — `f ← clip(f + ε)` per canvas processed (NOT wall-clock — §8's attack 4), reset toward 0 by
  sleep: `f ← f·(1 − ζ)` at each sleep boundary. Modulates: a global precision decay (the modulate gain
  scaled by (1 − 0.5f)) and, at ceiling (f ≥ 0.95), FORCES the sleep boundary early.

**PENDING: every constant's value + its source (fitted to §0(b) / chosen by design) declared here at
signature.** H-DYNAMICS's dynamic ranges are the fitting target.

### §2.3 · The effectors (exact code paths declared at signature)

arousal → modulate() gain · fixation count · sleep onset. boredom → ask probability · mouth probability ·
world-source seek. fatigue → precision decay · forced sleep. Nothing else changes: the brain's learning,
calibration, exams, the DRIVE turns, the precision register (its own stream untouched), every other organ.

### §2.4 · The mouth driven by state

boredom > θ_babble: the mouth speaks WITHOUT a say-target (babble — the filed frames' own words, never
invented ones). arousal > θ_exclaim right after a surprise: the mouth repeats the last say once
(exclamation). fatigue > θ_silent: the mouth is suppressed. The thresholds declared with §2.2's constants.

### §2.5 · What does not change

Everything not named in §2.3/§2.4. OFF = byte-identical, proven by I1/I2.

## §3 · The runs

- **G** — the gate world: a FRESH never-used seed (drawn only at signature; the bl6 law's own never-used
  check form: the grep printed empty in the gate record).
- **B-OFF / B-ON** — closed-life replays (the bl6 first-segment form) with the line absent / present.
- **Solo arms** — arousal-only, boredom-only, fatigue-only, all-three, the flat twin (all fixed at rest).
- **H-NULL** — the inverted-arousal twin (surprise drives arousal DOWN).
- **H-PRECISION** — four arms: arousal-only / precision-only / both / neither.

## §4 · The marks (the plan §2's table, adopted whole)

H-DYNAMICS (each variable visits both halves of its range; none constant; none diverges) · H-DRIVE-EFFECT
(tests 1–6 not degraded > 0.02; KS p < 0.01 vs the flat twin) · H-SLEEP-TRIGGER (fatigue-driven boundary
differs from the count-driven one ≥ 10 % of canvases) · H-BOREDOM-ASK (ask rate at b > 0.7 ≥ 2× at
b < 0.3) · H-BOREDOM-MOUTH (≥ 1.5×) · H-AROUSAL-LEARN (Spearman ρ > 0.3, p < 0.001, surprise vs Hebb step
in the same window) · H-AROUSAL-EYE (fixations at a > 0.7 ≥ 1.3× at a < 0.3) · H-FATIGUE-DEGRADE (test 1
lower ≥ 0.02 pre-sleep; recovery within 0.01 post-sleep) · H-NULL (inverted drives degrade S or U ≥ 0.05)
· H-PLANT (500 zero-surprise canvases drive boredom ≥ 0.95) · H-PRECISION (both ≥ each solo on ≥ 4 of 6
tests, or redundancy declared as the finding) · I1 (OFF replay == the closed journal; the planted change
breaks it) · I2 (ON journal minus drive rows == the OFF journal). **Readings, never graded:** the variables'
per-window means; the mouth's content distribution at high vs low boredom; the attended world-source at
boredom ceiling; the arousal × precision interaction surface.

## §5 · The controls

The planted zero-surprise series (H-PLANT) · the identity plant (one genome value changed → the replay
diverges) · the inverted drive (H-NULL — the strongest negative control: if inversion does not hurt, the
drives are decorative and this law is NOT adopted) · the flat twin (the baseline) · the instrument's own
planted control (`homeostasis_s0.py --selftest`: a synthetic tape with a planted err ramp must move the
shadow series in the declared direction — CAUGHT or the instrument is refused).

## §6 · The decision rule + the price

Every mark PASS → HOMEOSTASIS enters the genome templates and rides bl7 (the ladder: bl7 = bl6 + this ONE
line). I1/I2 fail → wiring defect, repair test-first, never loosen. H-NULL fails → the drives are
decorative: NOT adopted, the failure reported. H-PRECISION redundant → absorb precision into arousal in
the NEXT law. THE PRICE (declared, measured at the bench): the pinned window's fresh run root + cache
redraw (the bl6 form: ~1 h + the identity check), the bench arms' replays (each ≤ 1 CPU-h at the bl2
segment's measured rate), the two pre-flights. Memory peaks measured per arm through slot (SLOT_MEM
declared per run; never above 12G without his word).

## §7 · What this does not claim

Not that the organism feels. Not that arousal is consciousness. Not that the three variables are the RIGHT
three (they are the MINIMAL three). Not that the constants are optimal (they are the first values
satisfying H-DYNAMICS). (The plan §4.8, adopted verbatim.)

## §8 · The adversarial walk (12 attacks; the plan's six named first)

1. **«The constants were fitted to make the marks pass»** → the constants are fitted to §0(b)'s DECLARED
   bench seed; the gate's G run uses a FRESH seed never drawn before signature. A fit that only works on
   the fitting seed fails at the gate honestly.
2. **«Arousal duplicates precision»** → H-PRECISION's four arms decide; redundancy is a declared finding
   with its own decision rule (§6), not a shrug.
3. **«Boredom is just low surprise»** → boredom rises only on SUSTAINED low surprise (the running window
   κ·s̄), never on one low canvas; the H-PLANT form proves the sustained form and the threshold is declared.
4. **«Fatigue is just a clock»** → fatigue accumulates per CANVAS PROCESSED, never per wall second; a
   sleeping organism's fatigue falls; a paused life accrues nothing. The bench prints the proof (the
   fatigue series flat during a planted idle window).
5. **«The mouth's babble is random noise»** → H-BOREDOM-MOUTH ties the rate to the boredom variable, and
   the reading prints the babble's CONTENT distribution (filed frames' own words) — a noise mouth would
   not correlate with boredom (H-BOREDOM-MOUTH) nor with the frames.
6. **«The sleep boundary moved but nothing improved»** → H-FATIGUE-DEGRADE's pre-sleep degradation and
   post-sleep recovery, or the mark fails.
7. **«The drives just add noise to a working organism»** → H-DRIVE-EFFECT's non-degradation bars (tests
   1–6 within 0.02) plus I1/I2's byte forms.
8. **«Arousal's gain could fight precision's per-synapse scaling»** → arousal is a GLOBAL gain on the same
   modulate() path (multiplicative, bounded); the four-arm interaction surface is printed as a reading.
9. **«Babble/exclaim could flood the journal»** → the mouth's rates are capped by the same budget forms
   the MOUTH line already declares (journaled; the caps' values declared at signature).
10. **«The seek act could thrash world sources»** → the seek fires only at boredom's CEILING with a
    refractory window (declared); the reading prints the attended-source series.
11. **«Fatigue-forced sleep could starve training»** → the forced boundary is bounded below by the genome's
    own cadence (never sooner than half the count; declared), and H-SLEEP-TRIGGER's bar is on the
    DIFFERENCE, not the frequency.
12. **«The pinned window edit could contaminate the caches»** → the bl6 window's own price: a fresh run
    root, every cache redrawn, the array-identity check with a planted bit, all printed in the gate record.

## §9 · Signature

The seat signs alone (his 09-29 word) — after §0(b)'s table lands, the constants are declared, and this
walk is re-read against the real bench. **DRAFT 2026-10-12 — NOT SIGNED.**
