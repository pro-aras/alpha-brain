# RESEARCH-OPEN-WORLD — the child's open world: from a fixed 25-word world to the planet (the video door)

> edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-07 15:48 +0400 — Ahmad's order of 2026-10-07 (verbatim,
> from the chat): «Why the world is so small? Why can't we download videos from youtube for our use case and show
> them? There are alot of videos for kids learning and stuff like that? And that was my reason to ask you about taking
> in complex information that a brain can convert it to information and understanding and learning part of his life.
> So the world opens up to him because the creature itself is bottlenecked because of this. A human doesn't need
> specific environment around him. A human continues and develop itself to adapt the environment and convert it into
> his learning, and improving domain. That's the path we have to follow as well. Deep research on it and start this
> part.»
>
> Method: reasoning-craft §7 (the whole loop first; every part mapped or named ABSENT; read-status flagged; never
> cheat). Five read-only research extractions ran inside this session (research he ordered); the synthesis, the code
> map, and the design are the seat's. This document follows RESEARCH-HUMAN-PREDICTIVE-NORMALIZATION.md (the
> normalization/prediction stack) — this one is its world-side twin.

## 1 · Why the world is so small (the honest answer)

The scene world is small **by design, not by oversight**: it is a *controlled instrument* — 25 words, three
attributes, regenerated truth — so that every claim about learning could be measured against a known ground truth
(the W1/W2 benches' whole power). The measured cost of that choice is now in: brain-long-4 saturated it (24 of 25
words mature; `brain.learned` decelerating — 3,165 → 60,722 → 71,359 and flattening). A bench proves a mechanism;
it cannot grow a mind past its own vocabulary. Ahmad's diagnosis is exactly the record's: **the creature is
bottlenecked by its world.** The human child it is modeled on never had this problem — the planet is its world.
This document is the road from the bench to the planet, with the planet arriving *through the organism's own
senses* (video frames through the eye, caption speech through the ear), never through text injection into its mind.

## 2 · The human mechanism (the whole loop, five parts)

**W1 · Statistical stream segmentation — words/objects out of a continuous stream, from minute one, no labels.**
8-month-olds segment words from pause-free syllable streams using only conditional probabilities:
TP(Y|X) = count(XY)/count(X), a local *dip* in TP marking a boundary (Saffran, Aslin & Newport 1996 — read whole;
the confound fixed by Aslin, Saffran & Newport 1998 — read whole: it is the CONDITIONAL statistic, not raw counts —
an instrument-design law for us: frequency and conditionals must be decoupled in test items). The budget: ~2 minutes
of exposure, ~45 occurrences per word. The same computation works on the *visual* stream: infants chunk visual
feature combinations by conditional probability after ~5 exposures per scene, no labels, no reward (Fiser & Aslin
2002 — read whole). Machine form: running unigram/bigram counters + a dip detector — online, one pass, cheap from
the first minute.

**W2 · Event segmentation — cutting the stream into moments by prediction failure.** The brain runs a continuous
next-moment predictor; a *transient error spike* opens the gate: the current "what is happening now" model resets
and full sensory write-in briefly opens, then the gate swings shut (Zacks et al. 2007 — read whole). A boundary IS
the reset transient. A multi-scale bank of error integrators (different time constants) yields nested fine/coarse
events for free. The economics: stable phases are cheap, boundaries are expensive — compute concentrates where the
stream is least predicted. The neural-net existence proof (Reynolds/Zacks/Braver): gated event models self-organize
unlabeled and *improve* prediction. The warnings that bind us: raw surprise ≠ boundary once sequence structure is
learned (Avrahami & Kareev); wrong boundaries actively corrupt memory; the error-detector's neural seat is
unconfirmed (the paper's own negative result) — the COMPUTATION is what we copy, not the anatomy.

**W3 · The sensory front ends — continuous physics to discrete events.** The cochlea is a tonotopic filterbank
("a Fourier analysis") with an active, level-dependent amplifier (40–60 dB gain near threshold, saturating at high
levels), adaptation that keeps every channel in range, a timing code below ~2 kHz and a rate code above, and 10–20
staggered-threshold afferents per cell covering ~120 dB (Fettiplace 2017 — read whole). The retina's output is not
pictures: a signed ON/OFF split (increments and decrements are separate machines), center-surround, and two
bandwidths — sustained high-resolution colour (midget/parvocellular) and transient motion/flicker
(parasol/magnocellular) (Schiller 2010 — read whole; complements our E1 eye research). Machine form for us:
per-channel signed difference streams + pooled normalization + operating-point adaptation — never raw frames inward.

**W4 · The curriculum is shaped: child-directedness and its warning.** Kids' learning videos are motherese rendered
as media: slower tempo, shorter simpler utterances, repetition, isolated words, the target word at the utterance's
pitch-peak final position, the label *synchronized with the object's motion* (the co-reference channel), and an
annealing schedule (exaggerated early, adult-like later) (Saint-Georges et al. 2013, 144-study systematic review —
read whole; Soderstrom 2007 — abstract-only, flagged). THE WARNING, measured: infants did NOT learn a foreign
language's phonetic categories from audiovisual/TV input where live interaction succeeded (Kuhl's result, quoted in
the review) — **passive video is a weaker signal than a contingent partner.** Our W2 mentor world is the contingent
channel (it answers the organism); the video door is the breadth channel. Both, in that order of strength — and the
video door's measures must never claim the contingent kind of learning from a non-contingent tape.

**W5 · The machine road, honestly priced (no borrowed weights, ever).** (a) The classical unsupervised video stack —
dense/frame sampling → optical flow (Farnebäck) → short trajectory tracking (15-frame caps) → histogram descriptors
(HOG/HOF/MBH) → codebooks — is CPU-era, fully comprehensible, and every stage implementable from first principles;
its measured 2009 costs (0.9–4.6 frames/s on a dual-core) are trivially met by this box (the dense-sampling result is
a named negative: salient-point detectors LOST to dense grids on realistic video). (b) The self-supervised mechanism
worth copying *as a mechanism*: mask tubelets → predict the masked latents from an EMA target with stop-gradient
(the anti-collapse pair — V-JEPA, read-partial flagged) — and it survives at 194 LOC on CPU (keon/jepa, README read)
— while paper-grade scale (GPU-years) is closed to us and named so. (c) Captions: timed `{text, start, duration}`
triples with provenance flags (ASR vs authored) — a free cross-modal co-occurrence stream; the access endpoint is
undocumented and rate-limited — **a noisy, revocable sensor, never infrastructure** (youtube-transcript-api's own
warning). (d) The frontier learner excludes language from pretraining entirely and aligns later — the captions are a
separate alignment channel for us too, not the visual objective.

## 3 · The map against Alpha 5 (file:line or ABSENT)

- The eye today: located features on a 128×128 canvas of a *generated* world (`brain/scene/eye.py`; the world's own
  renderer `brain/scene/world.py:539`), the residual filed (E1), the forced-glance road built. **ABSENT: any
  transducer for natural video** (no ON/OFF split, no adaptation, no motion channel — E2's learned front is its own
  planned law; the video door needs the *innate* transducer first, the classical channels).
- The ear today: word streams per moment from the world's own rows (`mind.py:_consume_eye` merges them per canvas).
  **ABSENT: any audio/caption ingestion** — captions arrive as timed text, which is exactly the ear's existing
  currency (words per moment): the ear's door is a *format converter*, not a new organ.
- Stream segmentation: **ABSENT** — no TP dip-detector, no error-gated event cutter. The moment boundary today is
  the world's own cadence (a canvas per moment); real video needs the organism's OWN cutter (W2's mechanism is the
  law's own instrument).
- The curriculum: the mentor world (W2, in flight) is the contingent channel; **ABSENT: the breadth channel**
  (this document's road).
- The absorbing machinery (web, two stores, sleep replay, precision road N1): present or on the road — the video
  door feeds exactly these.

## 4 · The design — THE VIDEO DOOR road (each its own law, bars first)

- **V0 · THE CONVERTER + THE FIRST BENCH (S; the first build, this document's "start").** A tool
  `tools/worlds/video_door.py`: one downloaded kids'-learning video (ffmpeg scene-cut frames at the eye's own 128×128
  + the caption track) → the organism's TAPE format (eye rows with payload PNGs; ear rows with `word`, `start`,
  `duration`, and the provenance flag — the tape's own ear-row form). Then the bench: a FRESH mind replays the video
  tape (the replay machinery's own road); the measure: births/surprise over the tape, the TP-dip segmenter's
  boundaries over the caption stream measured against the video's own shot cuts (ffmpeg's scene detector as the
  EXTERNAL check — never the organism's input), and byte-identity of the replay's repeat. The plant: a corrupted
  frame must change the tape's hash. Nothing enters any life.
- **V1 · THE ORGANISM'S OWN CUTTER (S–M).** The error-gated event segmenter (W2's mechanism) replaces ffmpeg's knife:
  a bank of error integrators over the eye's residual stream; boundary = the reset transient; measured against the
  human-shaped shot structure AND by its memory effect (boundary frames preferentially encoded — Zacks's own
  prediction, our own bench). The naive "cut at max surprise" is a named, planted-against failure mode.
- **V2 · THE INNATE VIDEO FRONT (M).** ON/OFF signed channels + center-surround + the two bandwidths + adaptation
  (W3's machine form) as the eye's pre-processor for natural frames, beside (never replacing) the scene world's own
  eye. Byte-identity for the scene world, the mouth-cap pattern.
- **V3 · THE CURRICULUM (M).** Kids'-learning videos first, ordered by a simpleness gradient (W4's annealing), the
  caption-word stream feeding the ear with the provenance flag; the synchrony channel (a caption token's onset × a
  visual motion event) as the co-reference instrument. The honesty bar carried from W4: breadth-learning measured,
  never the contingent claim.
- **V4 · THE OPEN WORLD'S LIFE (L, the rung).** A life that lives in the video world — its own law, after W2/W3's
  readings and V0–V3's verdicts. The planet, through its own senses.

**Process speed (his order, «make the process faster and efficient»):** V0/V1 run on minutes-long clips at bench
scale (the replay price scales with tape length — measured 21.7 CPU-h per 50,000-canvas life-tape; a 5-minute clip
at 1 canvas/s ≈ 300 canvases ≈ CPU-minutes). Long tapes gate only the final identity checks.

## 5 · What this design does NOT claim

No borrowed pretrained weights, no LM anywhere in the organism (the pure road). No claim that passive video teaches
what a contingent partner teaches (Kuhl's negative result is carried, not hidden). The caption stream is ASR-noisy
and revocable — a sensor, named so. Segmentation ≠ understanding (Saffran's own scope note); the door opens the
world's *input* — understanding is the N-road's machinery absorbing it.

## 6 · Sources and read-status

- Saffran, Aslin & Newport 1996, *Statistical learning by 8-month-old infants*, Science 274:1926–1928 — **read whole**
  (two hosted full-text copies; the publisher paywalled).
- Aslin, Saffran & Newport 1998, *Computation of conditional probability statistics by 8-month-old infants*,
  Psych Science 9:321–324 — **read whole** (the authors' host).
- Zacks, Speer, Swallow, Braver & Reynolds 2007, *Event perception: a mind-brain perspective*, Psych Bull 133:273–293 —
  **read whole** (PMC2852534 + the authors' PDF).
- Fiser & Aslin 2002, *Statistical learning of new visual feature combinations by infants*, PNAS 99:15822–15826 —
  **read whole** (the vision lab's hosted PDF; the publisher 403).
- Saint-Georges et al. 2013, *Motherese in Interaction… (a systematic review)*, PLoS ONE 8:e78103 — **read whole**
  (open access). Soderstrom 2007 — **abstract-only**, flagged.
- Fettiplace 2017, *Hair cell transduction, tuning and synaptic transmission in the mammalian cochlea*, Compr
  Physiol 7:1197–1227 — **read whole** (PMC5658794 via efetch; figures/references not inline — flagged).
- Schiller 2010, *Parallel information processing channels created in the retina*, PNAS 107:17087–17094 —
  **read whole** (PMC2951406).
- Wang et al. 2009 (BMVC, local spatio-temporal features evaluation) — **read whole**; Wang & Schmid 2013 (IDT,
  ICCV) — **read whole**; Laptev 2005 — **inaccessible**, quoted via Wang 2009 §2.1, flagged.
- Assran et al. 2025, *V-JEPA 2*, arXiv:2506.09985 — **read-partial** (§1–§3 + abstracts; §4.1+ truncated — flagged);
  Bardes et al. 2024 (V-JEPA) via the official repo README — **read whole**; keon/jepa README — **read whole**.
- Tong et al. 2022, *VideoMAE* — **abstract-only**, flagged.
- YouTube Data API captions docs + youtube-transcript-api README — **read whole** (the fragility warning quoted).

*Cost of this research: 5 read-only extraction subagents inside the seat's session; the machine-side checks (ffmpeg,
PIL, cv2, the canvas spec) run on the box; no GPU, no rented machine, no new jobs beside the running life and the
armed ON replay.*
