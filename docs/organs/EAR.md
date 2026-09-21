# THE EAR — biology reverse-engineered, software added
*edit: Claude (Opus 5, organ researcher), 2026-09-21 14:12 +0400*

> Written to the shared brief `/data/dev/genome/docs/organs/BRIEF.md` on Ahmad's 2026-09-21 13:30 and 13:39 words.
> Every mechanism is sorted into exactly one bin — **FIXED** (set at development, never changes in a life),
> **ADAPTS** (changes at runtime without learning), **LEARNS** (belongs to the mind; the organ delivers a trait).
> Every factual claim carries its road. **Road tags:** `[fetched: URL]` = the page itself was read; `[secondary: URL]` =
> a search result that named the primary and quoted its number — the primary was NOT opened (§5 states this plainly);
> `[from disk: path]` = read on this box this session; `[unverified]` = stated without a road.
> Proposals, not decisions. The creature at `/data/dev/genome` was never touched.

---

## 0 · ON DISK ALREADY — what was read first, and what it settled

### 0.1 The one fact that frames everything

**The creature has no ear.** What the genome calls `ear` is a **symbol channel**, not a sense of sound:

| the line | what it actually is | road |
|---|---|---|
| `SENSE    ear    letters 8` | a word string → 8 slots × 27 symbols = 216 numbers, one-hot, unit length; a word > 8 letters is REFUSED | [from disk: `/data/dev/genome/genome/G4.genome`; `genome/world.py::encode_word`] |
| `#OFF EAR-SOUND cochlear gammatone agc` | E52's front, **declared and switched off**, with the reason written beside it: *"the loudness path proven, the frequency path untested"* | [from disk: `/data/dev/genome/genome/G4.genome`] |
| the seam | the ear thread's row carries `{moment, word}`; `Mind.consume` holds it in `pending[moment]` until the eye's row of the SAME moment arrives, then both are one canvas: `f0` (112 sight features) and `xw` (216 word numbers) light `AREA sight` and `AREA words`, and `MEET sight words` wires the two by Hebb in the same moment | [from disk: `/data/dev/genome/creature/mind.py` lines 175–232] |
| the rate | 18,959 mind rows in 24.0 h = **0.219 rows/s**; the world draws every 5 s; max eye/ear gap 5.2 s | [from disk: `runs/g4-verdict-life2-20260921-1215/VERDICT.md`; `genome/G4.genome` `WORLD drawn every 5 s`] |

The alpha3 estate says the same in one line: **"ears — none. E52 built and proved a cochlear front; it was never made an organ."** [from disk: `/data/dev/alpha3/docs/FUSED-SENSES-PREREG.md` §the-table]

### 0.2 What was MEASURED here about hearing (five attempts, one pass)

| id | question | verdict | the number | road |
|---|---|---|---|---|
| E43 | do transition probabilities over LETTERS find word boundaries? | FAIL at (iii) | boundary F1 0.574 vs twin 0.276 (2.08×) PASS; headword share 0.727 vs twin **0.747** — the mark was saturated before the mechanism touched it | [from disk: `docs/atlas-sources/alpha3-experiments-sweep.md`; `E43b/VERDICT.md`] |
| E43b | a syllable grain read off letters by rule? | FAIL | **chunker ceiling 0.515** — only 51.5 % of true word boundaries fall where the rule can cut (3,758,452 of 7,293,453); S1 word-token F1 0.0435 (ratio 6.14× PASS, floor FAIL); mean segment 9.70 letters against words of 4.34 | [from disk: `/data/dev/alpha3/experiments/E43b-.../VERDICT.md`] |
| E44 | sound tied to the word? | **VOID at its own control** | the 8-bit plant reached 0.910 held-out against a 0.99 bar; U 0.504, twin 0.513 | [from disk: `E44/VERDICT.md`] |
| E44b / E44c | fix the gate (bands spread; budget; width)? | VOID / FAIL | 0.878 · 0.934 (arm A) · 0.840 (arm B); **C0 syllable ceiling r = 0.470** | [from disk: `alpha3-experiments-sweep.md`] |
| E44d | fit the syllable front on train speakers, judge on held-out? | FAIL by 0.008 | held-out r(rates) **0.492** vs a 0.50 bar; peaks/rule **0.789**; 3.01 peaks/s vs the rule's 3.84 syllables/s. Reading: *"what the envelope finds is the stress beat, not the syllable"* — English is stress-timed, an unstressed function-word syllable rides on its neighbours' energy | [from disk: `E44d/VERDICT.md`] |
| E47 | peel the words he already knows, run statistics on the residue? | **PASS** | word-token F1 **0.4874**, 12.6× its twin, 2.09× pure statistics — the first pass on the stream road; **not wired into anything** | [from disk: `alpha3-experiments-sweep.md`] |
| E52 | a cochlear front, human-inspired? | **G0 PASS** — the first hearing gate in five attempts | 1.000 on 553 held-out utterances, both plants | [from disk: `E52/results/g0-full.json`] |

### 0.3 E52 read precisely — what it proved, and the three things it did not

E52's front, as built: a **gammatone filterbank on ERB-spaced centre frequencies, 50 Hz → 7,800 Hz, 32 bands** (128 declared as a machine arm); half-wave rectification with a **power law 0.3**; a per-channel AGC with a **fast and a slow EMA**, gain clamped to [0.1, 10], causal (no look-ahead); **one onset channel per band** (rectified derivative of the compressed envelope) plus a broadband onset sum; a **modulation filterbank at 2–4, 4–8, 8–16, 16–32 Hz** on the AGC'd envelope; everything resampled to a common **100 Hz (10 ms hop)**. [from disk: `E52/IMPLEMENTATION-NOTE.md` §2–§7]

**What PASSED.** Both plants read **1.000** held-out (4-bit stamp, joint decode 1.000, per-bit [1,1,1,1]) under a negative rule of Hamming distance exactly 1 — a rule written into the file *because* the inherited random-negative rule made the 0.99 bar unreachable (ceiling **0.9688**), which would have produced a fifth false "hearing failed". [from disk: `E52/PREREG.md` ADDENDUM 1; `results/g0-full.json`]

**The five-cell ablation, read from the JSON, not from prose:**

| cell | what changed | audio-plant held-out | units-plant held-out | verdict in the file |
|---|---|---|---|---|
| full front | — | **1.000** | 1.000 | PASS |
| no-filterbank | gammatone → E44's **64-band log-mel** | **1.000** | 0.998 | PASS |
| no-compression | exponent 1.0 (rectify only) | **0.9837** | 1.000 | FRONT LOSSY |
| no-agc | gain fixed at 1 | **0.9539** | 1.000 | FRONT LOSSY |
| no-onset | onset group dropped | **1.000** | — | audio only |
| no-modulation | modulation group dropped | **1.000** | — | audio only |

[from disk: `E52/results/g0-{full,no-filterbank,no-compression,no-agc,no-onset,no-modulation}.json`]

**Three corrections this document is built on, each sharper than the summary that has been quoted since:**

1. **Frequency analysis itself was never ablated.** The `no-filterbank` cell swapped gammatone for **64-band log-mel** — still a frequency analyser. The ladder compared two frequency decompositions on a plant whose message rides in the amplitude envelope. The honest sentence is: *gammatone vs mel did not matter for an envelope plant; having a frequency analysis at all was never tested.* This is the gap §4's first proposed test closes.
2. **The plant's carriers sat at the bank's own centre frequencies** (`carrier_freqs_from_cf`), placing each tone where one band is maximally excited by construction. The builder wrote this down himself: *"a 1.000 here is evidence the front CAN carry a signal placed at its most sensitive frequencies, not evidence it hears an arbitrary signal."* [from disk: `E52/results/REPORT-builder.md` §2]
3. **G1, G2 and every machine arm were never run.** The results directory holds `g0-*` and `gammatone-selftest.json` and nothing else: the syllable ceiling against CMUdict, the cost bar, the binding arms (U, U-voice, S) and the four machine arms — **128 vs 32 bands, exact vs jittered timing, with and without a 0.5×/2× replay pass** — are all `TODO` in the builder's own report. Nothing in §2 of this document may cite E52 as evidence that a machine advantage helps. [from disk: `ls E52/results/`; `E52/results/REPORT-builder.md` §4–§6]

The estate already carries the lesson in its own words: *"an ablation ranks the stages YOUR PLANT needs, not the stages the TASK needs… a stage the plant cannot exercise is UNTESTED rather than unnecessary."* [from disk: `~/.ai-context/SOLUTIONS.md` #228 ADDENDUM 2]

### 0.4 The measured cost of that front on this box

| measurement | value | derivation |
|---|---|---|
| full front, 1,153 LibriSpeech utterances, 32 bands | **1,638.0 s** wall, `nice -n 10`, `OMP_NUM_THREADS=2` | [from disk: `E52/results/g0-full-run.log` line 12; `IMPLEMENTATION-NOTE.md` §11] |
| mean utterance length, dev-clean | **7.13 s** (400 files sampled, this session) | measured here: `wave` over `/data/alpha3-library/audio/librispeech/dev-clean-wav/**/*.wav` |
| audio processed | ≈ 8,221 s = 2.28 h | 1,153 × 7.13 |
| **front cost per second of audio** | **≈ 0.20 wall-s on ≤ 2 threads**, i.e. **0.20–0.40 core-s per audio-second** (the log records wall clock under `OMP_NUM_THREADS=2`; the true core-second bill lies between one and two threads’ worth and was never separately measured) | 1,638.0 / 8,221 |
| the log-mel substitute | 2,814.3 s → 0.34 s/s — **slower than the IIR gammatone bank** | `ablation-run.log` |
| the onset group | ≈ 220 s of the 1,638 (13 %) | full − no-onset |
| the modulation group | ≈ 239 s of the 1,638 (15 %) | full − no-modulation |

**Reading: a 32-band cochlear front in numpy runs at about 2.5–5× real time on this box** (16 cores, no GPU, 26 GB), depending on where in the 0.20–0.40 core-s band the true bill falls. One or two cores carry a real-time ear with margin, or a replay at 2×–5×. This is a favourable number and it was never stated anywhere on disk; E52's own cost bar (G2) never ran.

### 0.5 His words, and the one contradiction on disk

**His 2026-09-15 paste (the richest EAR document on this box, and the highest authority):** the order P0 assumed is backwards — *"a baby is never taught word #1, then word #2… the word boundary is something that emerges from exposure to the whole stream"* (Saffran, Aslin & Newport 1996); *"it's not just hearing. It's hearing + seeing tied together in the same moment"*; the convergence point is the **superior colliculus**, *"a small midbrain structure with neurons that fire especially strongly when a sound and a sight happen at the same place and the same time"*; **McGurk** proves the brain fuses rather than picks; *"the thing that makes two streams get bound together in the first place is mostly timing"*; and the practical road — a subtitled video gives **three streams already aligned by construction** (vision, audio, text at one timestamp). [from disk: `/data/shariah-shadow/live/docs/proposals/alpha3-research/AHMAD-PASTE-2026-09-15-stream-first-language.md`]

**His 2026-09-19 AGI Q&A:** *"The retina and cochlea only perform literal, low-level cleanup (contrast, edges, frequency decomposition); semantic invariance only emerges several layers deep… the invariance is learned, not designed in at the input stage."* And: *"A microphone and ADC are not limited to the 20 Hz–20 kHz range of human hearing; the ceiling is set by sample rate, so a 'digital ear' reading an existing recording can register ultrasonic or infrasonic content no human ear ever could."* And the prefilter: *"a prefiltration or novelty gate that only promotes what changed… it needs to run asynchronously with a timestamp and a modality tag on every event."* [from disk: `/data/dev/alpha3/docs/proposals/research/ahmad-2026-09-19-AGI-QA.reportlab.py` §1–§2]

**His 2026-09-03 speech research** gives the loop the ear closes on the mouth: *"As you start speaking, your brain runs a continuous State Feedback Control loop. Your ears listen to your own voice in real-time. If your auditory cortex hears that you slightly mispronounced a syllable… your brain instantly calculates the error and adjusts your mouth muscles mid-word"* (DIVA). [from disk: `/data/shariah-shadow/live/docs/proposals/ahmad-research-speech-2026-09-03.md`]

**THE CONTRADICTION, and how it is resolved.** `R1-ORGANISM-SPEECH.md` (2026-09-12) builds speech on **pre-segmented words and dictionary glosses**; his paste (2026-09-15) says that road is backwards. The estate's own index already flags it: *"Same question, opposite answers."* [from disk: `docs/atlas-sources/alpha3-research-digests-sweep.md`, Closing] **Resolved his way**, and the disk evidence agrees with him rather than with R1 — E43b proved a letter-rule grain cannot find words (ceiling 0.515), and E47 proved that peeling known words and running statistics on the residue does (F1 0.4874, 12.6× its twin). R1's hearing/phoneme content is thin in any case: a grep for `phoneme|hear|cochlea|prosody|syllab|acoustic` over R1 returns three hits, none about the ear. **R1 contributes nothing to this document that his paste does not overrule.**

**A second contradiction, between his paste and his own rule.** His paste calls the superior colliculus *"literally a learned 'these go together' detector"*; his 13:30 rule says learning is the mind's, never the organ's. Resolved in §1.6: the **binding WINDOW is FIXED** (a physical constant of the organ), the **association is the mind's** — which is exactly what `MEET sight words` + `HEBB window 1` already is in the creature. The biology puts it subcortical; his rule moves it one layer in. Said plainly rather than smoothed over.

---

## 1 · BIOLOGY — how the ear works, mechanism by mechanism

### 1.1 The chain, in the order the ear does it (human unless named)

| # | stage | what it computes | the number | bin | road |
|---|---|---|---|---|---|
| 1 | pinna + concha + ear canal | direction-dependent filtering; a resonant boost where speech lives | two-peak structure in the **2–6 kHz** range (ear-canal + concha resonances); pinna adds ~5 dB at 2–3 kHz; canal resonance ~3 kHz in adults (4.4 kHz at 1 month → 2.9 kHz at 24 months) | **FIXED** (the shape is grown once; it is a body part, not a parameter) | [secondary: https://www.nature.com/articles/s41598-022-21245-w] |
| 2 | middle ear (ossicles) | impedance match air → fluid; a band-pass | combined outer+middle transfer peaks at **1–3 kHz**; mean middle-ear pressure gain **23.5 dB at 1.2 kHz** | **FIXED** | [secondary: https://www.nature.com/articles/s41598-022-21245-w] |
| 3 | stapedius (acoustic) reflex | pulls the chain stiff on loud low-frequency sound | threshold ≈ **85 dB HL** (70–100 dB SPL); latency ≈ **10 ms** — which is why it cannot protect against an impulse | **ADAPTS** | [secondary: https://en.wikipedia.org/wiki/Acoustic_reflex] |
| 4 | basilar membrane | a mechanical frequency analyser: place = frequency | the **Greenwood map**, `f = A(10^(ax) − K)`, human constants **A = 165.4, a = 2.1, K = 0.88**, x = fraction of BM length from apex; covers ~20–20,000 Hz; derived 1961, constants 1990 | **FIXED** | [fetched: https://en.wikipedia.org/wiki/Greenwood_function] |
| 5 | the filter's width | each place is a band-pass, not a line | **ERB(f) = 24.7 · (4.37·f/1000 + 1) Hz**, Glasberg & Moore 1990, valid 100 Hz–10 kHz; ERB-rate `21.4·log₁₀(1 + 4.37·f_kHz)` | **FIXED** | [fetched: https://en.wikipedia.org/wiki/Equivalent_rectangular_bandwidth]; cross-checked against the on-disk implementation (EarQ 9.26449, minBW 24.7) [from disk: `E52/IMPLEMENTATION-NOTE.md` §2] |
| 6 | outer hair cells (prestin) | the cochlear amplifier — a **compressive** gain that is large for quiet sound and small for loud | BM gain relative to stapes **~10,000× at low SPL, ~100× at high SPL**; ~3 OHC rows to 1 IHC row; boosts the dynamic range across ~6 orders of pressure | **ADAPTS** — the gain is set moment to moment by the signal itself, and by the efferent (row 12); the *mechanism* is FIXED | [secondary: https://www.sciencedirect.com/science/article/pii/S0896627305008810] |
| 7 | inner hair cells | transduction: mechanical → neural; one row, ~**3,500** cells, each reading one place on the map | IHCs synapse with **90–95 %** of type-I auditory-nerve fibres; ~**20** fibres per IHC | **FIXED** | [secondary: https://en.wikipedia.org/wiki/Greenwood_function]; [secondary: https://anatomypubs.onlinelibrary.wiley.com/doi/10.1002/ar.23815] |
| 8 | the auditory nerve — **channel count** | how many parallel wires leave the ear | **30,000–35,000** bipolar spiral-ganglion neurons in humans; type I > 90 % | **FIXED** | [secondary: https://anatomypubs.onlinelibrary.wiley.com/doi/10.1002/ar.23815] |
| 9 | the auditory nerve — **three spontaneous-rate classes** | one place is read by three populations with different thresholds, so ONE channel spans a huge level range | Liberman 1978: low SR ≤ 0.5 spikes/s, medium 0.5–18, high > 18; ≈ **60 % high / 25–30 % medium / 10–15 % low**; high-SR = low threshold, narrow dynamic range, saturates; low-SR = high threshold, non-saturating | **FIXED** (it is a channel design, not a state) | [secondary: https://pmc.ncbi.nlm.nih.gov/articles/PMC2538332/] |
| 10 | the auditory nerve — **phase locking** | spike TIMES carry the waveform's fine structure, not only its level | mammals lock usefully to ≈ **4–5 kHz**; the **barn owl to ~9–10 kHz** (Köppl 1997), giving microsecond spike-timing resolution | **FIXED** | [secondary: https://pubmed.ncbi.nlm.nih.gov/9096164/]; [fetched: https://pmc.ncbi.nlm.nih.gov/articles/PMC13268026/] |
| 11 | adaptation at the nerve | the response to a steady sound decays; onsets are re-emphasised | rapid component **1–10 ms** (shrinks with level), short-term **≈ 60 ms** (level-independent) — Westerman & Smith 1984 | **ADAPTS** | [secondary: https://pubmed.ncbi.nlm.nih.gov/6501113/] |
| 12 | cochlear nucleus — three temporal filters on the same input | the one place in the chain where "what happened" splits into "when it started" vs "how loud it stays" | **bushy cells → primary-like** (endbulbs of Held, timing preserved); **stellate → chopper** (a regular train for the stimulus duration); **octopus → onset** (a brief, precisely timed burst at a transient, little adaptation to a sustained tone) | **FIXED** | [secondary: https://www.sciencedirect.com/topics/neuroscience/cochlear-nucleus]; [secondary: https://pubmed.ncbi.nlm.nih.gov/9566317/] |
| 13 | superior olive — WHERE | two cues, two nuclei: **ITD** (time) and **ILD** (level) | birds/mammals resolve ITDs as small as **10–20 µs**; the owl's nucleus laminaris is an axonal **delay line + coincidence detector** array (Carr & Konishi 1990), the Jeffress place map | **FIXED** | [secondary: https://pmc.ncbi.nlm.nih.gov/articles/PMC4575979/] |
| 13b | …but the mammal is NOT a Jeffress map | the standard delay-line story is contested for mammals | Grothe, Pecka & McAlpine 2010, *Physiol Rev* 90:983–1012: *"an increasing number of studies report findings that are inconsistent with the standard Jeffress model"* for MSO anatomy, physiology and the nature of the ITD representation | **FIXED** (whichever code it is) | [secondary: https://pubmed.ncbi.nlm.nih.gov/20664077/] |
| 14 | inferior colliculus | the obligatory relay: nearly every ascending path converges here before the forebrain | receives from cochlear nucleus, superior olive and lateral lemniscus; projects to medial geniculate → cortex | **FIXED** | [secondary: https://pmc.ncbi.nlm.nih.gov/articles/PMC10718034/] |
| 15 | modulation filterbank | how fast the loudness wobbles — where syllable and stress rhythm live | Dau, Kollmeier & Kohlrausch 1997 (*JASA* 102:2892): **constant 5 Hz bandwidth below 10 Hz, log spacing at Q = 2 from 10 Hz to 1 kHz** | **FIXED** | [secondary: https://pubmed.ncbi.nlm.nih.gov/9373976/] |
| 16 | auditory cortex | tonotopy + **spectro-temporal receptive fields** — a cell answers to a pattern in time × frequency, not a tone | one coherent best-frequency gradient around mid-Heschl's gyrus = the primary field; >2,000 ferret A1 STRFs: response peaks roughly aligned in time, widely spread in frequency | **FIXED** as a machine; its tuning is where **LEARNS** begins (§1.5) | [secondary: https://www.sciencedirect.com/science/article/pii/S1053811921004997]; [secondary: https://pubs.aip.org/asa/jasa/article/146/6/EL459/955628/] |

**The shape of the chain, in one sentence:** the ear is a **bank of overlapping band-pass filters whose outputs are compressed, adapted, and read twice — once for level and once for time** — and everything above the cochlear nucleus is recombination, not transduction. Nothing in rows 1–16 needs to learn for the chain to work.

### 1.2 What ADAPTS — runtime change without learning

| mechanism | what it does | the number | why not LEARNS | road |
|---|---|---|---|---|
| OHC cochlear amplifier | compressive gain: amplifies the quiet, not the loud | gain ~10,000× at low SPL → ~100× at high SPL | the gain returns when the sound goes; nothing persists | [secondary: https://www.sciencedirect.com/science/article/pii/S0896627305008810] |
| **medial olivocochlear (MOC) reflex** | the brainstem turns the amplifier's gain DOWN on the cochlea — an efferent wire running the wrong way, the only one in the senses that does | *"MOC-induced reduction in cochlear gain can enhance the response to signals presented in masking noise"*; AN fibres fire less to sustained noise and become MORE sensitive to a tone in it | it is gain control with a reflex arc; it is reset by silence | [secondary: https://journals.physiology.org/doi/full/10.1152/jn.00222.2011] |
| **the MOC's disputed half** | whether the MOC benefit is reflexive or **attention- and experience-dependent** | the literature is explicitly equivocal: *"an alternative… proposes that the MOC system benefits speech-in-noise processing through dynamic (e.g. attention- and experience-dependent), rather than reflexive, control of cochlear gain"* | **This is the one place the biology genuinely disputes his rule.** Called here: the reflex arc is **ADAPTS**; any lasting, experience-set bias on the gain is **LEARNS, and belongs to the mind** — the mind sends a gain, the organ applies it. That keeps the organ stateless across lives. | [secondary: https://journals.physiology.org/doi/full/10.1152/jn.00222.2011] |
| stapedius reflex | stiffens the ossicles on loud low-frequency sound | 85 dB HL, 10 ms latency | reflex | [secondary: https://en.wikipedia.org/wiki/Acoustic_reflex] |
| AN adaptation | onsets re-emphasised, steady state suppressed | 1–10 ms rapid, ~60 ms short-term | a decay, not a memory | [secondary: https://pubmed.ncbi.nlm.nih.gov/6501113/] |
| **precedence effect / echo suppression** | the FIRST arrival wins the direction; its reflections are folded into it | lead and lag fuse at 0–1 ms; **localization dominance at 1–5 ms**; a reflection at 5–30 ms can be **10 dB louder** than the direct sound and still not be heard as an echo; buildup raises the echo threshold to ~26 ms | it is a rule about arrival order, applied per sound | [secondary: https://en.wikipedia.org/wiki/Precedence_effect] |
| **corollary discharge — "was that me?"** | the motor system tells the auditory system what it is about to produce; the auditory system subtracts it | Eliades & Wang 2008, *Nature* 453:1102–1106: auditory neurons are **suppressed during vocalization**, yet the surviving marmoset A1 neurons are **MORE sensitive to a perturbation of the vocal feedback** than they are to the same sound heard passively | this is the BRIEF's own definition of ADAPTS: *"a top-down PREDICTION sent by the mind that the organ subtracts (the organ only computes the residual; the prediction is the mind's)"* | [secondary: https://www.nature.com/articles/nature06910] |

**The corollary-discharge row is the one to take whole.** It answers two different questions with one wire: *did I make that sound* (a tag on the event), and *did it come out as I meant it* (the residual — which is the DIVA feedback loop his own speech research describes). In the creature's vocabulary the prediction already has a home: `PREDICT next glance; error scales delta` — the same gene, pointed at the ear.

### 1.3 The stream — what leaves the ear per unit time

This is the question that decides the whole design, because the creature's body is built around a **tape of discrete rows paired by instant**, and a waveform has no instants.

| candidate | rate | what it costs the tape | what the mind gets |
|---|---|---|---|
| raw waveform | 16,000 samples/s | 73,000× the tape's current 0.219 rows/s | everything, unusable |
| frames (E52's front) | **100/s** (10 ms hop) | **456×** the tape's row rate | a picture of time × frequency, one slice at a time, with no unit |
| **syllables / onsets** | speech is **3–8 /s**; the theta band the cortex tracks is **4–8 Hz**; E44d's own detector found 3.01 peaks/s against the rule's 3.84 | **14–36×** the tape's row rate — the only candidate of the same order as the rest of the body | a UNIT with a start time, a band profile, a direction and an own-voice flag |
| words | ~2–3 /s **[unverified]** — no road; stated for the shape of the table only | ~10× | not available: the boundary is what must be discovered (his paste) |

- **Syllable rate and the theta rhythm:** *"typical syllable rates are observed to lie approximately within the same range as theta oscillations, conventionally delimited to 4–8 Hz"*; Giraud & Poeppel 2012 propose that cortical oscillations in distinct bands parse the stream at the syllabic and phonemic timescales in parallel. [secondary: https://pmc.ncbi.nlm.nih.gov/articles/PMC3839250/]
- **Who cuts, under his rule?** Two mechanisms are on the table and they are NOT the same bin:

| mechanism | what it is | bin | evidence |
|---|---|---|---|
| **onset detection from the amplitude envelope** (octopus cells; the theta-band envelope peak) | a parameter-free physical rule: the envelope rises, an event fires | **FIXED — the organ's** | biology rows 12, 15; E52 built it and never graded it |
| **word-boundary discovery** (Saffran transition probabilities; E47's known-word peel) | a statistic over the units the organ delivered | **LEARNS — the mind's** | Saffran, Aslin & Newport 1996: 8-month-olds segment an artificial language after **2 minutes** of exposure, on transitional probabilities alone [secondary: https://www.science.org/doi/10.1126/science.274.5294.1926]; E47 PASS [from disk] |

**The 51.5 % ceiling's lesson, stated as a rule and not as a result:** E43b's chunker could place only 51.5 % of true word boundaries *where it is able to cut at all*, so its word-token F1 of 0.0435 was a statement about the RULE, not about the statistic — the ratio clause passed everywhere (6.14×) while the floor failed. **Any grain rule the ear proposes ships with its ceiling measured and printed beside the mark, before the mark is scored.** [from disk: `E43b/VERDICT.md`; `~/.ai-context/SOLUTIONS.md` #224]

**The three things the mind needs WITH each unit** (his AGI Q&A: *"a timestamp and a modality tag on every event"*):

| field | what it is | from which biology | bin |
|---|---|---|---|
| **WHEN** | the onset instant, to the sample | octopus cells' precisely timed burst; phase locking | FIXED |
| **WHERE** | azimuth from ITD, elevation/side from ILD | superior olive; the owl's 1–2° | FIXED (the cue); LEARNS for the map's calibration (§1.5) |
| **WHAT** | the band profile at the onset + the envelope shape over the unit | the filterbank + modulation bank | FIXED |
| **WHOSE** | was that my own voice | corollary discharge | ADAPTS (the mind predicts, the organ subtracts) |

### 1.4 The number that makes the ear worth having at all: TIME

Sight in this creature is a 32×32 grey frame through a sealed tower — a **spatial** sense with no clock inside it. The ear is the opposite: its whole content is **temporal**, and the biology spends its precision there.

| where the precision is | resolution | road |
|---|---|---|
| auditory nerve phase locking | fine structure to **4–5 kHz** (mammal), **~9–10 kHz** (owl) | [secondary: https://pubmed.ncbi.nlm.nih.gov/9096164/] |
| interaural time difference | **10–20 µs** discriminated | [secondary: https://pmc.ncbi.nlm.nih.gov/articles/PMC4575979/] |
| bat echo delay | ~**1 µs** resolved in the brainstem | [from disk: `ALPHA-2-DEEP-RESEARCH-2026-09-06.md` §3.5, tagged [Likely, S56–S58] there] |
| dolphin jittered echo-delay threshold | **1–2 µs** (at the measurement hardware's own floor) | [secondary: https://pmc.ncbi.nlm.nih.gov/articles/PMC6394490/] |

**This is the gap the ear closes in this creature and nothing else does:** his paste says binding is *"mostly timing"*, and the creature's only clock today is a 5-second world cadence.

### 1.5 What LEARNS — and where his rule puts it

| the biology | what changes | where his 13:30 rule puts it | what the FIXED ear delivers instead | road |
|---|---|---|---|---|
| **perceptual narrowing to native phonemes** (Werker & Tees 1984) — English-learning infants discriminate non-native contrasts at 6–8 months and decline over the first year | nothing in the cochlea changes; the CATEGORIES change | **MIND.** The ear keeps delivering the same band profile at 12 months as at 6. | the band profile + onset shape; the mind's cells merge or split on it (`MERGE cos>θ same-answer`, `BIRTH error misfires 3` are already that mechanism) | [secondary: https://www.sciencedirect.com/science/article/abs/pii/S0163638325000098] |
| **wav2vec 2.0 / HuBERT learned front** — a 7-layer CNN over the raw waveform, **25 ms receptive field, 20 ms stride**, 512 channels, strides [5,2,2,2,2,2,2] | the FIRST layer is learned from data | **LEARNS → refused at the organ.** A learned front makes the ear a trained model; his rule says the organ prefilters and the mind learns. | the ERB band-energy + onset + modulation trait vector — the same 20 ms grain, **fixed**. The honest cost is named in §2 and in §5's questions: a fixed front will lose to a learned one on any benchmark that rewards phonetic detail. | [secondary: https://arxiv.org/pdf/2106.07447] |
| **auditory cortex plasticity** — STRFs re-tune with input statistics | the cortical filter | **MIND** (cortex is not the organ) | — | [secondary: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002123] |
| **the owl's ITD map calibrated by VISION** (Knudsen & Brainard) — juveniles raised in prisms displacing the visual field 23° re-tune ITD selectivity to match the displaced visual receptive field; the change sits in the ICX / the ICCls→ICX projection, in the **midbrain**, with a sensitive period | a brainstem/midbrain map, i.e. **learning inside the sensory pathway** | **This is the sharpest case against his rule, and it is decided his way:** the organ delivers **raw ITD in microseconds**; any mapping of microseconds → a place in the creature's world is the MIND's, learned against sight. The biology puts it below cortex; his rule moves it up. The biology also gives the reason it is safe to move: the teaching signal is VISION, which in this creature already lives in the mind (`MEET sight sound`). | ITD/ILD as two numbers on the event | [secondary: https://www.science.org/doi/10.1126/science.2063209]; [secondary: https://www.jneurosci.org/content/17/17/6820] |
| **the superior colliculus "these go together" detector** (his paste) | a space-and-time coincidence association | **the WINDOW is FIXED, the ASSOCIATION is the mind's** — and the creature already has the association as `MEET sight words` + `HEBB window 1` | the event's instant, so the window can be applied | [from disk: his 09-15 paste; `genome/G4.genome`] |

### 1.6 Best parts across species — EXTENDING the 17-animal register, never rebuilding it

The register at `/data/shariah-shadow/live/docs/proposals/alpha1-organism-capabilities-research-2026-08-24.md` already holds **#6 electric fish (EARLY)** and **#7 bat/dolphin echolocation (TRUE, HAVE)**. Its two axes are kept: **Mapping** = HAVE / PARTIAL / MISSING-and-buildable / N-A; **Grade** = TRUE / OVERSTATED / EARLY / N-A. New rows are numbered 18+; **no existing row is renumbered or restated.**

| # | species | mechanism, with its number | algorithmic content | mapping to the creature | grade | road |
|---|---|---|---|---|---|---|
| **18** | **Barn owl** (*Tyto alba*) | asymmetric ear openings (right higher than left) → **ITD gives azimuth, ILD gives elevation**; localization error **< 2°** frontally in both axes; phase locking to **9–10 kHz**; nucleus laminaris = axonal delay lines + coincidence detectors | **two cues, two axes, one physical asymmetry** — a body shape that turns a 1-D cue pair into a 2-D direction, with no learning | **MISSING-and-buildable.** Two microphone channels (or the two channels of any stereo file) give ITD+ILD for free; the asymmetry is a filter applied to one channel. | **TRUE** | [fetched: https://pmc.ncbi.nlm.nih.gov/articles/PMC13268026/]; [secondary: https://en.wikipedia.org/wiki/Sound_localization_in_owls]; [secondary: https://pmc.ncbi.nlm.nih.gov/articles/PMC4575979/] |
| **19** (extension to **#7**, a different mechanism) | **Greater horseshoe bat** (*Rhinolophus*) | the **acoustic fovea**: a disproportionate number of cochlear receptors and IC neurons devoted to a narrow band centred on **61.1–61.2 kHz**; **Doppler-shift compensation** — the bat lowers its emitted CF2 in small steps so the returning echo lands back inside that band | **a fixed, over-resourced band + a motor loop that keeps the signal inside it.** The fovea does not move; the ANIMAL moves the signal. | **MISSING-and-buildable, and cheap:** a non-uniform band allocation (more ERB channels where the thing he must tell apart lives) is one array; the "Doppler" half becomes *re-request the stream at the rate that lands it in the dense band* (re-read at 0.5×/2× — E52's own unrun machine arm). | **TRUE** | [secondary: https://link.springer.com/article/10.1007/BF00617731]; [secondary: https://link.springer.com/article/10.1007/s00359-010-0569-6] |
| **20** | **Noctuid moth** | an ear of **two receptor cells (A1, A2)** on each side and nothing else; A1 ≈ **10×** more sensitive than A2 (threshold tympanal displacement **140 pm vs 2,510 pm**); A1 alone steers turning-away, A2 fires only when the bat is close and triggers the dive | **the smallest useful ear in nature: one sensitive channel for "far" and one insensitive channel for "near", and the DECISION is which fired.** No spectrum, no map. | **MISSING-and-buildable, and the cheapest row here.** A two-threshold level detector is ~10 lines and gives the creature an alarm channel that costs nothing and never needs the front. | **TRUE** | [secondary: https://journals.biologists.com/jeb/article/216/21/3954/]; [secondary: https://link.springer.com/article/10.1007/s00114-011-0851-7] |
| **21** | **Cricket** (*Gryllus bimaculatus*) | Schöneich, Kostarakos & Hedwig 2015, *Sci. Adv.* 1:e1500325 — **five brain neurons** form the feature detector for the male's calling song; LN2→LN5 delays a pulse by the inter-pulse gap, **LN3 is the coincidence detector** (band-pass for interval duration built by summing direct + delayed excitation, one locked to pulse onset and one to offset); LN4's pulse-rate tuning matches the band-pass tuning of the behaviour | **a delay line + a coincidence detector recognises a RHYTHM with five cells.** Pattern recognition in time, no template, no learning. | **MISSING-and-buildable.** This is the rhythm half of what the modulation filterbank does, at 1/1000 the cost — and it is the mechanism a "does this stream have speech in it" detector wants. **NOTE: the task brief says "4 interneurons"; the paper says FIVE.** Corrected here from the source. | **TRUE** | [secondary: https://pubmed.ncbi.nlm.nih.gov/26601259/]; [secondary: https://www.cam.ac.uk/research/news/neural-circuit-in-the-cricket-brain-detects-the-rhythm-of-the-right-mating-call] |
| **22** | **Elephant** (*Loxodonta*) | infrasonic calls, most energy **14–24 Hz** (range 1–20 Hz generated/detected); airborne range **> 10 km**; a SECOND channel — **seismic**, through bone conduction and foot mechanoreceptors; seismic waveforms from locomotion travel up to **32 km**, from vocalisations ~**16 km** (one source gives ~2 km for vocalisation-borne seismic under ideal conditions — the sources disagree and both are printed) | **the same message on two physically different channels with different ranges**, read by two different organs and fused centrally | **N-A for the ear; HAND TO BODY-SENSES.** The airborne infrasound half is free in software (§2b: there is no 20 Hz floor). The seismic half is a different sense. | **TRUE** (frequency and airborne range); **OVERSTATED as commonly quoted** (the seismic ranges conflict between sources by ~8×) | [secondary: https://en.wikipedia.org/wiki/Elephant_communication]; [secondary: https://journals.physiology.org/doi/full/10.1152/physiol.00008.2007] |
| **23** | **Mosquito** (*Culex*, *Anopheles*) | **Johnston's organ**: several thousand mechanosensory neurons arranged radially in the antenna's second segment, transducing **nanometre-scale** vibration; at least **eight groups** of auditory neurons distinct in frequency tuning, individual best frequencies **85–470 Hz** | **an ear built from the mechanics of a hair, not a membrane** — direction and frequency from one antenna | **MISSING, low value here.** Kept in the register because it is the one ear whose channel count is in the thousands with no cochlea. **NOTE: the task brief's "15,000 neurons" was not found; the sources say "several thousand".** Corrected here. | **EARLY** | [secondary: https://journals.biologists.com/jeb/article/220/21/3927/]; [secondary: https://www.biorxiv.org/content/10.1101/608778v1.full] |
| **24** | **Frog** (anuran) | **two separate acoustic end organs and no basilar membrane**: the **amphibian papilla** (≈ 50 Hz–1 kHz) and the **basilar papilla** (> 1 kHz), the latter argued to be a species-specific organ evolved to catch the high-frequency energy of the conspecific call — in *coqui*, the AP is tuned to the "co" note and the BP to the "qui" note | **a matched filter built into the anatomy**: the ear's passbands ARE the signal the animal must hear, so recognition is most of the way done before any neuron counts anything | **MISSING-and-buildable, and it is the cheapest "advancement" in this whole document:** the creature's ear does not have to span 20 Hz–20 kHz uniformly. Give it bands where ITS world's sounds are, and the discrimination is half-done by the filter. This is row 19's acoustic fovea generalised, and it is FIXED by definition. | **TRUE** | [secondary: https://pubmed.ncbi.nlm.nih.gov/18386018/]; [secondary: https://www.britannica.com/science/sound-reception/Auditory-sensitivity-of-amphibians] |

**Handed over, one line:** the **fish lateral line** (flow and pressure-gradient sensing over the body surface, a distributed near-field "touch at a distance") is not an ear and belongs in **BODY-SENSES**, together with the elephant's seismic channel (row 22) and any vibration sense.

**The register's own load-bearing warning, carried forward:** its #7 already grades echolocation TRUE/HAVE while noting that *"the literal echolocation SIGNAL-PROCESSING content… has no analog in a symbolic brain with no continuous sensor stream."* That caveat expires the moment this ear exists — which is precisely what row 19 proposes to collect on.

---

## 2 · SOFTWARE / MACHINE — what we add

### 2a · What MIMICS the biology in code (and what it costs on this box: 16 cores, no GPU, 26 GB; the mind runs ~26.5 ms a canvas)

| mimic | which biology row | status here | measured or estimated cost |
|---|---|---|---|
| **gammatone / ERB filterbank** | 4, 5 | **BUILT** — E52's front, 32 bands, 50–7,800 Hz, IIR | **0.20 wall-s (0.20–0.40 core-s) per second of audio** for the WHOLE front [from disk: `g0-full-run.log` ÷ measured audio] |
| half-wave rectify + power 0.3 | 6, 7 | BUILT | included above; removing it cost 0 s and **1.6 pp** of the audio plant (0.9837) |
| per-channel AGC, fast + slow EMA, causal | 6, 11, 12 | BUILT | included; removing it cost 0 s and **4.6 pp** (0.9539) — **the single most load-bearing stage in the whole front, by measurement** |
| onset channels (rectified derivative) | 12 (octopus cells) | BUILT, **never graded** | ≈ 220 s of 1,638 = **13 %** of the front |
| modulation filterbank 2–32 Hz | 15 | BUILT, **never graded** | ≈ 239 s of 1,638 = **15 %** |
| **CARFAC** (Lyon) — cascade of asymmetric resonators with fast-acting compression: pole–zero filter cascade modelling the travelling wave, plus a **multi-time-scale coupled AGC network**, i.e. the OHC amplifier as a network rather than a per-channel EMA | 4, 6, 12 | **NOT built.** v2 exists in Matlab, NumPy **and JAX**, open source under `google/carfac` | a drop-in alternative to E52's front whose AGC is exactly the stage E52 measured as load-bearing — worth one comparison, not an assumption [secondary: https://arxiv.org/abs/2404.17490]; [secondary: https://github.com/google/carfac] |
| ITD/ILD cross-correlation over two channels | 13 | NOT built | one cross-correlation per band per event; microseconds of CPU |
| a delay-line + coincidence rhythm detector | row 21 (cricket) | NOT built | ~5 state variables; free |
| **MFCC / mel** — the industry default | — | E44's road; **substituted into E52 as the `no-filterbank` cell and measured SLOWER (0.34 vs 0.20 s/s)** | **what mel throws away, named:** (i) **phase** — *"by taking the magnitude of each mel-scale frequency component, phase information… is discarded"*, so fine temporal structure, ITD and any own-voice residual are gone before the mind sees anything; (ii) the **DCT** step keeps low coefficients and discards the rest as "fast changes in the filterbank coefficients", which is exactly where an onset lives; (iii) it is **not invertible**, so nothing downstream can ever go back to the sound. For an organism whose ear is supposed to carry WHEN and WHERE, mel is the wrong mimic at any cost. [secondary: https://jonathan-hui.medium.com/speech-recognition-feature-extraction-mfcc-plp-5455f5a69dd9] |
| **wav2vec 2.0 / HuBERT** | §1.5 | **refused at the organ by his rule** — it is a LEARNED front | named here so the refusal is a decision with a cost attached, not an omission |

### 2b · What biology CANNOT do and software can

| # | the machine's advantage | why biology cannot | cost on this box | the catch |
|---|---|---|---|---|
| 1 | **Any band, no 20 Hz–20 kHz floor or ceiling.** HIS OWN WORDS: *"A microphone and ADC are not limited to the 20 Hz–20 kHz range… the ceiling is set by sample rate."* Infrasound (elephant, row 22) and ultrasound (bat, row 19) are the same array with different `lowFreq`/`highFreq`. | the cochlea is a physical structure of fixed length | **zero** — it is two numbers in the ERB spacing | the SOURCE must contain them; a 16 kHz LibriSpeech file has nothing above 8 kHz. The advantage is real only on audio recorded wide. |
| 2 | **No masking: every channel is exact.** A loud band does not suppress a quiet neighbour unless we write a rule that says so. | the travelling wave couples neighbouring places; the amplifier's compression is global within a band | zero | masking is also *useful* (it is why speech survives noise). This advantage should be **declared as an arm**, not assumed: an unmasked ear may be a noisier ear. |
| 3 | **Exact replay of every sound, forever — the tape.** Byte-identical, re-listenable at 0.5× or 2×, from any instant, with the front recomputed under a different parameter set. | no animal hears the same second twice | storage: 16 kHz mono PCM = **32 kB/s = 2.7 GB/day**; recomputing the front over a day = **4.8–9.6 core-hours**, i.e. ~20–40 min on 16 cores | the creature's replay discipline already demands byte-identity [from disk: life-2 VERDICT, REPLAY PASS] — a float front must be pinned exactly as the eye's tower is |
| 4 | **Phase preserved.** The waveform is kept beside the front (E52 declared this and never used it). ITD, own-voice residual and any fine-structure cue remain computable later. | phase locking dies above ~5 kHz in mammals | zero (it is the file) | nothing consumes it yet |
| 5 | **Sample-exact onsets.** No jitter, no refractory period, no 1–10 ms adaptation smear; the instant is the sample index. | AN spikes have jitter and a floor | zero | **E52 declared "exact vs jittered timing" as a machine arm and never ran it** — this is untested here, and must not be claimed |
| 6 | **N parallel ears on 16 cores.** The same second through four different fronts (32-band, 128-band, infrasound-shifted, two-cell moth alarm) at once, and the mind sees all four. | one cochlea, one set of parameters, grown once | 0.20–0.40 core-s per audio-second per front; **four fronts = 0.8–1.6 cores**, of 16, at real time | the mind must then be told which front an event came from — **a provenance field, not an option** |
| 7 | **Provenance on every trait.** Each event carries: which front, which file, which byte offset, which parameters. | memory carries no receipts | ~100 bytes/event at 3–8 events/s | none; the estate's belief law already demands this shape |
| 8 | **A sense that never sleeps, and one that can sleep on demand.** The ear thread runs continuously; or the whole day's audio is consumed in 1/5 of the time it took to happen. | attention is single and sleep is compulsory | the **2.5–5× real-time margin measured in §0.4** is what buys this | the tape's row rate (§1.3) is the real constraint, not the CPU |
| 9 | **A silicon-cochlea future, costed.** Event-based binaural silicon cochleae exist: 64 band-pass channels per ear, ~50 Hz–20 kHz log-spaced, cascaded second-order sections → half-wave rectifiers (IHC) → pulse-frequency modulators (ganglion cells), asynchronous address-event output, **55 µW**. | — | **not on this box** (it is hardware) | named because it proves the event-stream design is the one the hardware world converged on too [secondary: https://inilabs.com/products/dynamic-audio-sensor/]; [secondary: https://spectrum.ieee.org/silicon-cochlea-mimics-human-hearing] |

**The costing sentence, stated once:** a 32-band cochlear front costs **0.20–0.40 core-seconds per second of audio** here (0.20 wall-s measured on ≤ 2 threads; the bound was never split). The mind costs **26.5 ms a canvas** and the world draws every **5 s**. **The ear is not the expensive part; the tape is.** Any design that publishes 100 frames a second is a design about the tape, not about hearing.

---

## 3 · BENEFITS AND GAPS — against the creature as it runs today

"Today" = the G4 creature: life 2 alive 24.0 h, ALIVE and REPLAY PASS, `SENSE ear letters 8`, `#OFF EAR-SOUND`. [from disk: `runs/g4-verdict-life2-20260921-1215/VERDICT.md`; `genome/G4.genome`]

| gap in the creature today | filled by BIOLOGY (which mechanism) | filled by SOFTWARE / MACHINE (which feature) | still open |
|---|---|---|---|
| **There is no sound sense at all.** The thing called `ear` is a 216-number symbol channel; the world-maker hands it the name of the thing it drew. | rows 4–7: a filterbank + transduction; §1.3: an event stream | E52's front, already built and measured at 0.20–0.40 core-s/s (§0.4) | whether an ear helps THIS creature, whose world is drawn shapes with no sound. **Sound needs a world that makes sound** (§5 Q2). |
| **The word is GIVEN, never discovered.** `encode_word` refuses anything over 8 letters; the moment's word is the world-maker's label. His paste calls this backwards. | Saffran 1996: boundaries emerge from the stream in 2 minutes | E47's known-word peel (F1 0.4874, 12.6× twin) — **PASS on disk and wired into nothing** | the peel is an adult's road; the infant's road needs the ear to supply the grain (E43b's own conclusion) |
| **No clock finer than 5 s.** The world draws every 5 s; the tape carries 0.219 rows/s; binding is by `moment` equality, not by time. | §1.4: the ear's whole content is time — 10–20 µs ITD, 1–10 ms adaptation, 4–8 Hz syllables | a sample-exact onset instant on every event (2b #5) | the mind has nowhere to PUT a microsecond; `MEET` is an equality test on a moment id, and a sub-second binding window is a machinery change |
| **No WHERE.** Nothing in the creature has a direction. | row 13: ITD/ILD; row 18: the owl's two cues on two axes | two channels of any stereo file; a cross-correlation per band | the mind has no space to put a direction in (E49 FAIL: 3-D positions bought no sparsity) |
| **No "was that me".** The voice writes; nothing hears it. | Eliades & Wang 2008: suppression during vocalization, heightened sensitivity to feedback error | the `PREDICT` gene pointed at the ear: the mind predicts the sound of what it is about to say; the organ publishes the residual | `SENTENCE` is OFF in this life; there is no voice to hear yet |
| **`MEET` has only two areas** (sight × words), and `words` is a symbol. | his paste: the superior colliculus binds by simultaneity; McGurk proves fusion | `AREA sound from cochlea` + `MEET sight sound` + `MEET sound words` — three areas, the same Hebb rule | this is a machinery change, not a gene value; the tape's row schema gains a sense |
| **The frequency path has never been tested** — five hearing experiments, and not one of them put its message in frequency. | rows 4, 5, 16: everything above the BM assumes a spectrum exists | §4's first proposed test, with a control that is blind **by construction** | nothing; this is buildable now and costs hours |
| **A machine advantage has never been measured.** 128 vs 32 bands, exact vs jittered timing, replay at 0.5×/2× — all declared as E52 arms, none run. | — | §4's fourth proposed test | they may not matter at this size; the reading rule must say so rather than say "no advantage" |
| **Nothing carries provenance from a sense.** The tape has `{instant, sense, sha256}`; a trait has no receipt. | memory has no receipts either — this is a pure machine gain | 2b #7 | — |

---

## 4 · THE GROWTH INSTRUCTIONS PROPOSED — draft lines, each with its source and the test that could refuse it

Syntax as the genome parses it: `NAME  value words  # source`. Lines beginning `#OFF` are declared but not switched on.
**These are proposals. Nothing below is switched on, and the creature's genome was not edited.**

```
# ---- THE SOUND EAR (proposed; replaces nothing — the letter ear stays) ----
SENSE    ear-sound  wav 16000 mono          # a waveform sense beside SENSE ear; the letter ear keeps naming drawn things
COCHLEA  gammatone erb 32 from 50 to 7800   # E52's front: the arm every one of its gates actually ran on
HAIRCELL rectify power 0.3                  # the loudness exponent's neighbourhood; removing it cost 1.6 pp (E52 no-compression)
AGC      per-channel fast slow clamp 0.1..10  # the ear's automatic volume; removing it cost 4.6 pp — the most load-bearing stage measured
ONSET    derivative rectified per band; broadband sum   # octopus cells: a syllable is a CHANGE, not a loudness peak
MODBANK  2-4 4-8 8-16 16-32 hz on the agc envelope      # Dau/Kollmeier/Kohlrausch 1997; where syllable and stress rhythm live
EVENT    publish on onset peak; prominence 2 db gap 60 ms  # WHAT LEAVES THE EAR IS AN EVENT, NOT A FRAME (§1.3)
TRAIT    sound band 32 + onset-shape 4 + level 1 unit     # one unit vector per event, the shape AREA sound takes
WHEN     instant sample-exact                # the machine's advantage #5: no jitter, no refractory floor
WHERE    itd us ild db from two channels     # the owl's two cues, delivered RAW; the map is the mind's (§1.5)
OWNVOICE subtract predicted; flag the event  # ADAPTS: the mind predicts, the organ publishes the residual (Eliades & Wang 2008)
PROVENANCE front file offset params on every event   # what no animal can do (2b #7)
AREA     sound  from cochlea
MEET     sight  sound                        # his paste: binding is simultaneity (superior colliculus)
MEET     sound  words                        # the third area; the word is still the world's, until the mind cuts its own
#OFF ALARM   two-cell a1 a2 thresholds       # the moth's ear (row 20): far/near on two thresholds, no front needed
#OFF FOVEA   dense bands where his world speaks   # the horseshoe bat (row 19) / the frog (row 24): non-uniform ERB allocation
#OFF RHYTHM  delay gap coincidence           # the cricket (row 21): five cells recognise a rhythm with a delay line
#OFF WIDE    from 1 to 24000                 # his own line: no 20 Hz-20 kHz floor; needs audio recorded wide
```

### The tests that could refuse each line

| # | proposed line | its source | the test that could refuse it | what it costs |
|---|---|---|---|---|
| **T1 — THE ONE E52 COULD NOT DO: a plant whose message is in the FREQUENCY path** | `COCHLEA`, `TRAIT sound band 32` | §0.3 correction 1; the whole of rows 4–5 | **Design.** A 4-bit code where each bit chooses between **two neighbouring carrier frequencies of identical amplitude and identical on/off schedule** — identical *in construction* (tone count, amplitude, timing), so the broadband amplitude envelope carries no intended message and only the frequency differs. **It is NOT byte-identical**: two tones at f₁ vs f₂ added to the same speech beat differently against its harmonics, and the envelopes differ by that residue. Negative = exactly one bit flipped (E52's own Hamming-1 rule; **ceiling 1.0**, printed beside the bar, with the inherited random-negative ceiling 0.9688 printed too). **The blind control is derived from the architecture, and its residual is MEASURED, not assumed:** a front with NO frequency decomposition (one broadband channel: rectify → compress → AGC → onset → modulation) is blind to frequency by architecture, but its sensitivity to the beat residue above is an empirical question. It must sit **within the shuffled twin’s noise band around 0.5**, with its own ceiling printed beside it. **If it rises above chance, the plant leaks through the envelope and the design is refused before the front is judged at all** — a control that reads chance by hope rather than by measurement is this estate’s #175/#228 class. **Beside it, the comparison E52 thought it was making:** gammatone-32 vs the 64-band log-mel twin — now on a message that is actually in frequency. Carriers placed **off** the bank's centre frequencies, with an on-CF arm reported beside it (§0.3 correction 2). **Refuses the line if:** the full front does not clear the bar while the broadband control sits at chance. | hours: the front is 0.20 s/s and the corpus is 2.28 h of audio already on disk |
| **T2 — the grain, with its ceiling FIRST** | `ONSET`, `EVENT` | E44d FAIL at 0.492; E43b's 0.515 ceiling; #224 | Onset-event rate against a **pronouncing dictionary** (CMUdict; his D27 YES) on **held-out speakers**. The **ceiling is printed before any statistic**: the share of the corpus's words the dictionary covers, and the share of true syllables the peak-picker can express at all. Marks beside E44d's own numbers (r 0.492, peaks/rule 0.789, 3.01 vs 3.84 /s). **Twin:** peaks on a **time-shuffled envelope**. **Refuses the line if:** the ceiling itself reads under the bar — in which case the finding is about the rule, and the line is not built on it. | E44d's whole grid ran in 21 s on 8 processes |
| **T3 — the binding: does a sound event MEET a sight?** | `AREA sound`, `MEET sight sound` | his paste (simultaneity); G0b's own MEET | A stream where a drawn thing and a sound event share an instant. Mark: recall of the thing from the sound alone, and of the sound from the thing. **Twin:** the pairing shuffled (must fall to chance). **Second twin:** the sound delivered at a random instant within ±N seconds — which measures the **binding window** rather than the binding. **Refuses the line if:** the shuffled twin does not fall, i.e. the edges grew from something other than co-occurrence. | one short life; the machinery is the Hebb rule that already runs |
| **T4 — the machine arms, none of which have ever been measured** | `COCHLEA ... 32` vs 128; `WHEN`; a 0.5×/2× replay pass | E52 §3's four declared arms, **all TODO** | Each arm at **two seeds**, with the reading rule declared first: *an arm becomes the design only if it beats the base at BOTH seeds; if they tie within 1 pp the row reads "this advantage did not matter at this size", never "the machine has no advantage"* (E52's own wording, which is the right wording). **Refuses:** any arm that does not clear both seeds. | 4 arms × 0.2 s/s × 2.28 h ≈ 1.1 core-hours per seed |
| **T5 — "was that me"** | `OWNVOICE` | Eliades & Wang 2008; his DIVA research | Plant the creature's own rendered utterance into the stream. Mark: the event is flagged own-voice, AND a **perturbed** own utterance produces a larger residual than an unperturbed one (the marmoset result's shape). **Twin:** the same text from a different speaker, which must NOT be flagged. **Refuses:** if the flag fires on the twin, the organ is detecting the text and not the prediction. | needs `SENTENCE` on; not orderable today |
| **T6 — the cheapest row in the document** | `#OFF ALARM two-cell` | row 20, the moth | Two thresholds, two channels, no front. Mark: A2 fires only inside the near-threshold, A1 fires outside it, on a stream where the loud event's arrival time is known. **Refuses:** if a single threshold does as well — in which case the second cell buys nothing and the row is one line, not two. | minutes |
| **T7 — the tape's rate, before anything is switched on** | `EVENT` | §1.3's table; the creature's own 0.219 rows/s | Count the events a real hour of audio would publish, against the tape's current row rate, **before** the sense is armed. **Refuses the whole design if:** the event rate is closer to 100/s than to 5/s, in which case the publish rule (not the ear) is what needs designing. | free: it is a count on a file |

**One discipline carried over from E43b/E44d and stated here so it is not re-learned:** a grain rule, a mark, or a bar is never scored before its **ceiling** is computed and printed beside it — E43b's 0.515, E44c's 0.470, E44d's 0.492 and E52's 0.9688 are four instances of the same lesson on this one organ.

---

## 5 · WHAT THIS DOCUMENT DOES NOT CLAIM — and the three questions

### It does not claim

1. **That the road tags mean more than they say.** Most numbers in §1 carry `[secondary: URL]`, and on this document that means **a search result which named the primary and quoted its number — the primary itself was not opened**. Four pages were actually fetched (Greenwood, ERB, the barn-owl PMC review, and the disk documents). Nature, Science, J Neurosci and PubMed all refused (403 / cookie wall) — the same refusals `ALPHA-2-DEEP-RESEARCH` recorded on 09-06. **Before any of these numbers is written into a growth line, its primary is fetched at its open mirror** (#194, #196).
2. **That the creature needs an ear.** Its world is drawn shapes on a 5-second cadence. An ear with nothing to hear is an organ that will pass its own gates and change no decision — which is exactly the shape this estate has failed on before (a value computed and a value consumed are two different features). §5 Q2 puts this to him rather than assuming it.
3. **That E52's front works.** E52 proved a 4-bit stamp **placed at the filterbank's own centre frequencies** survives the chain. It did not test the frequency path, did not reach the syllable ceiling, did not run its cost bar, and did not run one machine arm. Everything in §4 treats E52 as a **built instrument with one passing liveness check**, not as a working ear.
4. **That a fixed front matches a learned one.** It does not, and the literature is not ambiguous about it: wav2vec/HuBERT learn their first layer from the waveform and that is where their advantage begins. His rule refuses it at the organ. **The cost of obeying the rule is real and is named here rather than hidden.**
5. **Anything about speech production.** The mouth is a different organ and `SENTENCE` is OFF in this life.
6. **That the animal rows transfer.** Row 18 (owl) and row 21 (cricket) are algorithms that can be written in tens of lines; row 23 (mosquito) is in the register for completeness and graded EARLY for a reason. The estate's own precedent is the rule: **take the algorithm, refuse the adjacency matrix** — and E15 is the reminder that a beautiful circuit can still lose to a dense baseline.
7. **Two numbers in the task brief were corrected against their sources** and both corrections are in §1.6: the cricket circuit is **five** neurons, not four (Schöneich et al. 2015); the mosquito's Johnston's organ is documented as **"several thousand"** neurons, and the figure of 15,000 was not found.

### Three questions for Ahmad

**Q1 — Does the ear deliver EVENTS or FRAMES?**
This is the one decision everything else hangs on, and it is not a parameter — it is the shape of his creature's tape. Biology says events: the octopus cell fires at a change, the syllable is 3–8 a second, and the cortex tracks the envelope at 4–8 Hz. His body says events too: the tape carries 0.219 rows a second and pairs senses by a moment id. A 100 Hz frame stream is **456×** that and would make the ear the only thing the creature does. **The recommendation is EVENTS** — one row per onset, carrying band profile, instant, direction and an own-voice flag. **But an event stream throws away everything between onsets**, and if he wants the creature to hear a held vowel, a tone, or a silence that means something, that is a different design. *Which is it?*

**Q2 — Where does the sound COME FROM?**
An ear needs a world that makes sound, and today's world is drawn shapes on a 5-second cadence with a label. Three roads, and they are not the same creature:
(a) **his own 09-15 road** — subtitled video, where vision, audio and text are already aligned by construction and nothing needs labelling;
(b) **speech only** (LibriSpeech is on the box, 2,703 utterances, and every hearing experiment used it) — clean, held-out speakers, no vision;
(c) **the drawn world given a voice** — each thing emits a made sound when it is drawn, so sight and sound are simultaneous by construction and the creature's own world stays the world.
(c) is the cheapest and the most controllable; (a) is his own proposal and the only one that is real. *Which world does the ear open onto?*

**Q3 — Does the ear get a band allocation shaped to HIS world, or a uniform human one?**
The frog and the horseshoe bat both say the same thing: put the channels where the animal's own signals are, and the recognition is half-done before a single neuron counts anything — 61.1 kHz for the bat, the "co" and "qui" notes for the coqui. In software this costs nothing: it is the spacing array. But it is a **commitment made at development and never revisited in a life**, which is what FIXED means, and it makes the ear specific to a world he has not yet chosen (Q2). The uniform 50–7,800 Hz ERB spacing E52 built is the safe default and the weaker one. *Uniform and general, or dense where his world speaks?*

---

## Appendix — road-tag census

Counted by `grep -o` over this file at write time; the counts are printed so that a reader can see how much of this document rests on a fetched page versus a search summary. See §5(1) for what `[secondary:]` means here.

| tag | count |
|---|---|
| `[fetched: …]` | 4 |
| `[secondary: …]` | 54 |
| `[from disk: …]` | 30 |
| `[abstract only: …]` | 0 |
| `[PMC copy: …]` | 0 |
| `[unverified]` | 1 |
