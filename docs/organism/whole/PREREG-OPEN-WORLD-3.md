# PREREG-OPEN-WORLD-3 (V2) — THE INNATE VIDEO FRONT: the retina's machine form beside the scene world's own eye

*Law before code (RULES law 1). Author: Kimi K3 (kimi-code, acting seat, alone — Ahmad's words of 2026-10-05;
this road ordered by his word of 2026-10-07). Read first: `docs/brain/RESEARCH-OPEN-WORLD.md` WHOLE (W3's
mechanism: the retina's output is not pictures — a signed ON/OFF split, center-surround, two bandwidths,
adaptation; the machine form: per-channel signed difference streams + pooled normalization + operating-point
adaptation, never raw frames inward) and `records/open-world-2/VERDICT-OPEN-WORLD-2.md` (V1's PASS and its
three planning inputs: the calibration cadence vs tape length; the boundary-set distinctiveness at this
density; the residual-as-error-stream caveat — «V2's own question»).*

**Read-status, honestly:** Schiller 2010 (PNAS 107:17087–17094, PMC2951406) was **read whole on 2026-10-07**
(the ordered research; its extraction recorded in RESEARCH-OPEN-WORLD.md §2 W3 and §6). The seat's re-read
tonight for constant-level precision was BLOCKED by the hosts' anti-bot walls (PMC reCAPTCHA; Europe PMC
500/403; PNAS 403) and no local copy exists on the box (a filesystem sweep found none). Every constant below
is therefore a **DECLARED machine-form choice grounded in the recorded whole-reading** — a 128×128 canvas
carries no visual-angle calibration, so physiological exactness is not claimed, now or ever. Every constant is
fixed before any reading and never tuned after one.

## 0 · The question, what a pass settles, what it cannot

**The question.** (i) Can the retina's machine form exist as an organ of the organism — signed ON/OFF
channels, center-surround, the two bandwidths (sustained spatial/colour, transient motion), pooled
normalization and operating-point adaptation — BESIDE the scene world's own eye, with the undeclared world
byte-identical (the mouth-cap pattern)? (ii) Do the form's own signatures hold EXACTLY under planted
conditions (the split, DC-free, signed motion, gain invariance, adaptation decay)? (iii) Does the brain still
ENGAGE the real-world tape when its sight arrives only through the front (never raw frames inward)? (iv) What
does the front do to the error stream the cutter reads — V1's planning input, read honestly?

**A pass settles:** (i) the front exists as an instrument-true organ of the organism (its signatures planted
and held, its doctored twin caught); (ii) the undeclared paths are byte-identical (the video bench's own
journal of record reproduced; the scene world's replay reproduced); (iii) the brain engages the video tape
through the front (turns > 0, printed with presence counts); (iv) the error-stream reading is printed under
the front (the mind's residual; the front's own transient channel beside it). **A pass opens:** V3 (the
curriculum — with the sizing note carried: tapes sized past the brain's first calibration cadence of 250),
the N-road's first real channels (N1's precision-weighted surprise gains candidate streams), and E2's innate
baseline (the learned front's law will beat or refuse this one).

**It cannot settle (each said now):** any claim about a LIFE (the bench only; the front's temporal state
across a life's resume is V4's own problem, named); any contingent-learning claim (Kuhl, carried); any
semantic claim (segmentation/transduction ≠ understanding); physiological exactness of the constants (no
visual-angle calibration exists at 128 px — declared machine form, said above); the audio/cochlea front
(W3's other half — its own later law).

## 1 · The bench and the one declared change

- The bench is V1's own, UNCHANGED: the tape `records/open-world-2/bench/tape-502` (502 frames, 'The Shape
  Song #1' + '#2'; sha-verified against its record, never re-converted) and the bench genome
  `records/open-world-2/bench/GENOME.genome` (bl2's copy + the one declared hears line).
- **THE ONE DECLARED CHANGE:** the replay is constructed with the front WIRED — `creature/mind.py`'s
  `Mind` gains an optional construction parameter (default None) and `creature/replay.py` passes it; when
  None, every byte of behavior is unchanged (the gates prove it). No genome edit, no parser edit,
  **no `genome/machinery.py` touch — the pinned files stay byte-identical** (the declaration is a
  construction parameter, printed in the record; a life's own declaration form is V4's law, not this one).
- When the front is wired, EVERY eye row's canvas is transduced by it — the raw-frame feature path
  (`luminance → INK rule → retina tower`) is REPLACED for that consumption (never raw frames inward). The
  ONE raw-path piece left: fixation SELECTION stays on Alpha 2's own analyse/`gaze_sequence` (the attention
  organ, unchanged) — DECLARED as the attention/transduction split: where to look is the gaze gene's; what
  the look READS is the front's.

## 2 · The build (`creature/senses/vfront.py`, tests first)

The organism's own sense organ (creature/senses/, beside ear.py/read.py — never `tools/`: it is not a
converter; never `genome/machinery.py`: pinned). Reuses, never re-derives: `genome.gaze.luminance`
(gaze.py:92), the Alpha-2 analyse's rg/by opponent channels (gaze.py:74), `genome.machinery.retina`
(machinery.py:1004, the tower), `genome.machinery._unit`, and `gaze.glances`'s own window/colour-block
roads.

1. **Center-surround (the spatial machine):** luminance L (the organism's own); C = L∗G(σc) − L∗G(σs) —
   the difference of Gaussians, **σc = 1.0 px, σs = 3.0 px** (surround ≈ 3× center, the classical ratio —
   DECLARED).
2. **The signed ON/OFF split:** ON = max(C, 0), OFF = max(−C, 0) — increments and decrements are separate
   machines, never one wire. The colour opponents rg/by (already opponent, already the organism's) ride the
   sustained path unchanged.
3. **Pooled normalization (the sustained gain):** each sustained channel R̃ = R / (β + mean|R| over the
   map), **β = 0.01** DECLARED — the channel's own pooled activity sets its operating point, per frame,
   stateless.
4. **The transient bandwidth (parasol/magnocellular):** D = L̃_t − L̃_{t−1} over the NORMALIZED luminance;
   T-ON = max(D, 0), T-OFF = max(−D, 0). The first frame of a tape: T maps exactly 0 (DECLARED).
5. **Operating-point adaptation (the transient gain):** causal — output uses the operating point of the
   PAST, o_{t−1}, then o updates: o_t = (1−α)·o_{t−1} + α·mean|D_t|, out = D/(β + o_{t−1}), **α = 0.2**,
   o_0 = 0 (DECLARED). The present never sets its own gain.
6. **The glance feature (what a look reads):** per fixated window (the gaze gene's own windows),
   `[tower(ON) · tower(OFF) · tower(T-ON) · tower(T-OFF) · colour_block]` = 4×112 + 32 = **480 numbers**,
   unit-normalised ONCE at the end (the fixed-gain pattern of colour_block's own docstring); the coarse
   glance likewise when the bench genome declares it. The front path returns the glances dict's own shape
   (`feats`/`fix`/`windows`/`residual`) so `_consume_eye` (mind.py:2414) reads it unchanged. The front's
   temporal state is exactly one previous normalized frame + the operating points — held by the front
   object across a replay, never in the genome.
7. **The declared journal field:** when (and only when) the front is wired, each eye row's journal glance
   row carries one additive key `front` = {t_mass: mean|T-ON|+mean|T-OFF|, o: the operating points} — the
   instrument stream M-ERR reads; additive, absent otherwise (the identity gates cover both cases).

## 3 · The gates (instrument)

| gate | asserts | read on |
|---|---|---|
| **G-IDENTITY** | (i) the bench genome over tape-502 under the NEW code with the front None → journal **byte-identical to V1's journal of record** (the sha at records/open-world-2/bench/); (ii) with the front wired, two independent replays → byte-identical journals (the front is deterministic, temporal state included); (iii) a 500-row segment of brain-long-2's closed tape (the program's standard scene tape) under master vs under the new code, front None → byte-identical journals | the bench |
| **G-TAPE** | tape-502 and the bench genome are sha-identical to V1's records (never re-converted, never re-declared) | the bench |
| **G-PLANT** | the planted streams below fire their bars AND a doctored front (OFF map zeroed; normalization removed) is CAUGHT by them — the instrument CAN fail | the plants |

## 4 · The marks

| # | mark | what is read | bar |
|---|---|---|---|
| **M-SIGN** | the signed split's signatures, planted: (P1) per pixel ON·OFF == 0 and T-ON·T-OFF == 0 (rectification, exact); a vertical step edge: ON edge-mass on the increment side ≥ 4× the decrement side, OFF the mirror; (P3) a uniform full-field canvas → sustained maps exactly 0 (center-surround kills DC); (P4) a bright square translated 8 px right: T-ON mass at the leading band ≥ 4× trailing, T-OFF the mirror | **P1/P3/P4 hold exactly as declared** (the doctored twin fails them) |
| **M-ADAPT** | (P2) the same step edge at contrast g and 2g: cosine of the pooled-normalized ON maps **≥ 0.99** (derived: a linear filter under R/(β+mean‖R‖) is gain-invariant up to β; printed); (P5) a square flashed 8 times (present/absent per frame): the normalized transient mass of the 8th flash ≤ **0.5** × the 1st — derived from the declared form (out uses o_{t−1}: r8/r1 = (β + o_1·…)/(β + o_7), the o-recursion's asymptote ≈ 0.13–0.39 for the plant's declared flash strength mean‖D‖ ≥ 0.05; the derivation printed with the reading) | **P2 ≥ 0.99, P5 ≤ 0.5, both derived-never-fitted** |
| **M-ENGAGE-2** | the brain over tape-502 WITH the front: turns, learns, said, surprise with presence counts, printed BESIDE V1's (69 turns, 69 learns, said 0, reasons {'not calibrated': 69}) | **turns > 0**; births > 0; the rest a reading (the cadence sizing note carried to V3, never a moved bar) |
| **M-ERR** | V1's planning input: the cutter (event_cutter, UNCHANGED — never edited under this law) over (a) the wired journal's residual stream: the memory effect at its boundaries vs matched controls AND the shuffled-boundary control — **V1's M-MEM bar** (real > control; the shuffled shows nothing); (b) the journal's `front.t_mass` stream: boundaries, nesting, the memory pair — **a READING, no bar** (a candidate instrument, never the mind's own signal); (c) V1's residual stream of record printed beside (never re-run); every boundary count printed with its chance expectation (V1's caveat form) | **(a) holds V1's bar; (b)/(c) printed, never graded** |
| **M-COST** | the front's per-canvas price, the replay totals, the identity-gate replays | inside §6's bounds |

## 5 · The verdict rule (TOTAL and ORDERED)

| # | the marks read (in this order) | verdict |
|---|---|---|
| 1 | a gate fails (G-IDENTITY, G-TAPE, G-PLANT) | **VOID** — an AMENDMENT names the cause |
| 2 | M-SIGN or M-ADAPT fails | **FAIL-FRONT** — the build is not the retina's form; named, the constants' declaration re-thought in a NEW law (never tuned in place) |
| 3 | M-ENGAGE-2 fails (zero brain turns through the front) | **FAIL-SENSE** — the transduction loses what the brain engages; named, the composition re-thought |
| 4 | M-ERR's (a) fails (no memory effect under the front, or an effect on the shuffled control) | **FAIL-FORM** — the front corrupts the error stream the organism learns from; the (b) reading printed beside |
| 5 | M-COST fails | **FAIL-COST** — re-priced in a NEW law |
| 6 | the gates hold, every mark inside its bar | **PASS** — the innate video front exists beside the scene world's own eye; V3's law may be written with this bench as its planning input |

## 6 · The price and the stop rules

- The replays: the wired video replay ≈ V1's measured 9.5 s + the front's per-canvas overhead (four towers
  + the DoG over 128² — estimated < 3× per canvas, printed never assumed); the identity replays ≈ 9.5 s
  each; the scene-gate replays: 500 rows × 2 at the OFF replay's measured ~1.56 s/canvas ≈ 26 CPU-min
  total; the plants: seconds on synthetic canvases.
- Every job through `slot` at SLOT_MEM 4G; ONE bench job at a time beside brain-long-4 and the ON replay
  (the night's headroom rule). **STOP:** S1 any job's CPU > 1 CPU-h → STOP; S2 any job's peak > 3,800 MB at
  4G → STOP; S3 a gate → VOID, an AMENDMENT names it.
- The network is used ZERO times (every input is a hashed file of record).

## 7 · Never

No borrowed pretrained weights; no LM anywhere; no tuned constants after a reading (a FAIL names the
declaration, a NEW law re-declares); no `genome/machinery.py` edit, no parser change, no cache redraw (the
front is a construction parameter — the pinned files byte-identical); no raw-frame features when the front
is wired (the one declared exception: fixation SELECTION, §1); no provenance edits; no journal content
written by hand; no semantic, contingent, or life claims from a bench; the shuffled and doctored controls
always printed beside the real; a FAIL told honestly is a result.

Signed: **Kimi K3 (kimi-code, author and acting seat, alone — Ahmad's standing words of 2026-10-05; this
road ordered by his word of 2026-10-07)**, 2026-10-08 00:46 +0400 (from `date` at signing), on this file's
sha256 carried by the SEAT-LINE file beside it in `records/open-world-3/`.
