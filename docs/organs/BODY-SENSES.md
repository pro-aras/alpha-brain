# BODY SENSES — touch and the skin, smell and taste, balance and the body's own report, and the copy of every act
*edit: Claude (Opus 5, organ researcher), 2026-09-21 14:20 +0400*

**The frame this document obeys** (`docs/organs/BRIEF.md`, Ahmad 2026-09-21 13:30/13:39): the organs prefilter and deliver; the mind learns. Every mechanism below carries one bin — **FIXED** (set at development, never changes in a life), **ADAPTS** (changes at runtime without learning: gain, habituation, a subtraction against a prediction the mind sent down), **LEARNS** (belongs to the mind; the organ delivers it as a trait with its where and its when). Biology says how the organ works; software says what we can add. Every factual claim carries its road: **[fetched]** (full text read), **[PDF read]** (the paper's own pages read here), **[secondary]** (two or more independent search results agreeing, no primary read), **[from disk]** (a file on this box, path given), **[unverified]**.

---

## 0 · On disk already — and what was simply not there

### 0.1 What was read first, and what each already settled

| path | what it settled for THESE organs |
|---|---|
| `/data/dev/genome/docs/organs/BRIEF.md` | the three bins, the three-part shape, the verification roads [from disk] |
| `/data/dev/genome/docs/organs/INVENTORY-2026-09-21.md` §0, §3 | names TOUCH/WHISKERS and SMELL/TASTE **near-empty**, BALANCE/PROPRIOCEPTION **thin**, and records that "efference" is absent from R1–R5 [from disk] |
| `/data/dev/alpha3/docs/proposals/research/ahmad-2026-09-19-AGI-QA.reportlab.py` §1–§2 | **his own words**: always-on organs rather than a request/response loop; **separate OS processes per organ, ROS-style** (camera node, mic node, planner node, motor node), because "one organ crashing without taking the others down" favours processes over threads; **a prefiltration or novelty gate before the brain** that "only promotes what changed, overwriting the rest", asynchronous, **"with a timestamp and a modality tag on every event"**; sense organs are not limited to the animal's band; the retina and cochlea do "literal, low-level cleanup" only, invariance is learned deep; and **"the brain actively sends a prediction down to the organ, which reports back confirmation or error (active inference)"** — that last sentence is the efference-copy requirement in his own hand [from disk] |
| `…/alpha3-research/R5-FLY-CONNECTOME-…md` §1.4, §1.7 | the ONE olfactory circuit study on disk: ~2,000 Kenyon cells, a sparse random expansion (visual KCs take 1–7 PN inputs, **median 3**, indistinguishable from shuffled — Ganguly 2024), global inhibition (APL), **ONE plastic layer** (KC→MBON) gated by a scalar dopamine wire, K\* = 7 (Litwin-Kumar 2017). Its ruling: **take the algorithm, refuse the adjacency matrix** [from disk] |
| `…/alpha3-research/R6-DIFFERENT-ANGLES.md` §C-4 | **the efference-copy study DOES exist on disk** — Crapse & Sommer 2008 read at PMC5153363, with the lower-order (reflex inhibition, sensory filtration) vs higher-order (analysis, stability, planning) split, and the E21 design [from disk] |
| `/data/dev/alpha3/experiments/E21-efference-copy-desk/VERDICT.md` | **E21 PASSED**: self/world discrimination **120/120 = 100.00 %** on held-out trials from the prediction error alone; median error self **0.000000** vs world **0.410017**, AUC **1.0000**; the shuffled-prediction twin **53.33 %** and the magnitude-only twin **59.17 %** (the separation is carried by the prediction, 40.83 pp); degraded model: 100 % at noise 0.05/0.10, 98.33 % at 0.20, 93.33 % at 0.40, 61.67 % at 0.80. The verdict's own first line: this was an INSTRUMENT with a SCRIPTED agent and says nothing about any organism [from disk] |
| `…/experiments/E15…/VERDICT.md`, `E22…/VERDICT.md` | E15 tested the mushroom-body expansion as a **supervised 62-class glyph classifier** over a 22-dimension hand-built eye vector and lost: arm A **27.48 %** against a plain ridge readout's **53.42 ± 1.73 %**; the shuffled-label twin read 1.75 % against a chance of 1.6129 %, so the split did not leak. E22 then showed the inhibition step is worth **+6.45 pp** inside that arm and that ungated plasticity falls to chance [from disk] |
| `…/RESEARCH-2026-09-16-HUMAN-MECHANISMS-…md` §3.5, §4 | the self-diagnosis organ he lacks (a reader of his own sittings, a percept clash, a drive), and the six-row "the brain cannot / the law it obeys here" table: exact replay, forked selves, provenance, own twins, parallel senses on 16 cores, a pretrained organ [from disk] |
| `…/ALPHA-2-DEEP-RESEARCH-2026-09-06.md` §2.8, §3.5 | its own verdict row: **"Where humans still win: grounding in a rich world (touch, smell, social)"**; and Cataglyphis path integration (stride-count + optic-flow odometers + a sky compass) as the only body-sense entry in the animal chapter [from disk] |
| `…/alpha1-organism-capabilities-research-2026-08-24.md` | the 17-animal register, two-axis graded (Mapping × Grade). **Extended in §1.6 below, never rebuilt** [from disk] |
| `~/.ai-context/SOLUTIONS.md` #230, #233 | the two interoception incidents on this box, both the same shape: a monitor reading `active` through 90 aborts, and a budget whose remaining and refusals sat in a persisted snapshot that no surface showed [from disk] |

### 0.2 What was NOT there — counted, not asserted

A term sweep over `/data/dev/genome/docs`, `/data/dev/alpha3/docs` and `/data/shariah-shadow/live/docs/proposals` (`*.md`, `*.txt`, `*.py`), counting FILES that contain the term [from disk, run 2026-09-21 14:0x]:

| term | files | what the hits actually are |
|---|---|---|
| `vibrissa` · `neuromast` · `Merkel` · `Pacinian` · `Meissner` · `Ruffini` · `Piezo2` · `mechanorecept` · `muscle spindle` · `vestibular` · `otolith` · `semicircular` · `haltere` · `vagus` · `allostasis` · `olfactory receptor` | **0 each** | nothing at all, anywhere |
| `whisker` | 3 | the BRIEF's own example sentence; the inventory's own "near-empty" row; one metaphor ("his fur-and-whiskers") in an Alpha 1 proposal |
| `star-nosed` · `lateral line` · `propriocept` · `somatosens` (as a sense) | 1 each | the inventory's own row naming them missing |
| `glomerul` | 1 | the string `glomerul.us` — a URL host in R5's source list. **The one olfaction study on disk never names a glomerulus** |
| `gustat` | 1 | the inventory's own row |
| `efference copy` | 8 | all of them 2026-09-13 or later: R6 §C-4, E21's sweep row, the audit, one review, one register line |

So: **touch, the skin, whiskers, the lateral line, balance, proprioception, smell as an organ, and taste have no research on this disk at all.** Interoception is the exception and is stated correctly below.

### 0.3 Three corrections to what the task brief assumed — each verified, each changing a proposal

1. **"Efference appears in none of R1–R5" is true and incomplete.** R6 (2026-09-13) researched it, quoted the primary, and E21 built and PASSED the instrument. What has never existed is an **organism** with one. `grep -n "expect\|error" creature/mind.py` and `genome/predict.py` settle it: the creature's PREDICT gene, as amended on 2026-09-21 (W3-2b), computes `error = 1 − max cos(actual glance, nearest resonating sight cell)` — **a memory-relative novelty reading that takes no act as an argument** [from disk: `genome/predict.py` docstring, `creature/mind.py:198–202`]. It cannot tell "the world changed" from "I looked somewhere else", which is exactly von Holst's problem. The estate has already measured the consequence without naming it: PREREG §18 records that under this error "a new thing whose look already resonates with an old cell (moon ≈ circle/ring, 0.9–1.9×) is not a surprise … while a thing that births its own cell spikes 54–63×" [from disk].
2. **The folder door does not read what the maker wrote.** The world-maker publishes `ear` then `eye` and writes its truth to `root/truth/<seq>.json`, **never onto the tape** [from disk: `creature/world_maker.py:_publish_canvas`]; the folder door reads Ahmad's own pictures out of `world/` [from disk: `creature/senses/folder.py`]. **And the fact that matters more, checked rather than assumed: NO act of the creature today has a sensory consequence at all.** The gaze looks like one and is not — `gaze.glances(rgb, …)` runs **inside the mind**, on a payload the eye has already delivered and decoded, and its four fixations are **crops of that one PNG** [from disk: `creature/mind.py:188–190`, `genome/gaze.py:102`]; choosing where to look changes nothing that arrives, because the next canvas is `make(seed, window, i)` either way. The body starts exactly two sense threads, `maker` and `folder` [from disk: `creature/body.py:372, 383`] — one seeded, one driven by Ahmad. `HANDS` is declared OFF, and the `WORLD` line's `web 6 per hour by curiosity` is **parsed into `web_per_hour` and implemented by nothing** [from disk: `genome/machinery.py:257–259` against the two `add_sense` calls]. So the first efference copy has no act to attach to yet, and §4.2 is written accordingly — finding this changed that proposal.
3. **Interoception is not empty on disk — it is RETIRED.** Alpha 2 had a working interoception organ (a typed body vector where "every reading names its CONSUMER and unit": energy, health, drill availability) and Alpha 1's metacognition organ was literally code-named `insula` [from disk: `ALPHA-2-DOSSIER-2026-09-03.md` §9, `alpha2-sweep.md` row M "WORKED, 914 tests", `ALPHA-1-metacognition-organ-2026-08-27.md` §2]. Both organisms were retired 2026-09-12. The creature has none of it, and the proposals below re-derive rather than re-import.

### 0.4 What the creature's body IS today — read from the running code

| fact | file:line | reading |
|---|---|---|
| threads | `creature/body.py:34` | the declared roster is `{eye, ear, door, mind, voice}`; a sense thread's exception is journaled and restarted after 1 s, the mind is unaffected |
| the tape | `creature/tape.py:Tape.publish` | one row per sense delivery: `{seq, at, sense, sha, payload, meta}`. **The only wall-clock read in the creature.** Payload durable before the row; SEQ persisted after it |
| the mind's road | `creature/mind.py:220, 248` | `org.moment(x, xw, lr_scale)` / `org.moment_sight(x)` — **only the feature vector and the word cross into memory** |
| the WHERE | `creature/mind.py:230` | `"fix": [[int(y), int(x)] …]` — the fixation coordinates are written to the **journal** and go no further. Nothing in the cell vectors carries them |
| the body's own numbers | `creature/body.py:260 _build_status` | `rss_mb`, `moments`, `tape_rows`, `births`, `arrivals`, `budget_left`, `births_refused_budget`, `sense_restarts`, `mind_ms_median_1min`, `crash` — written every 10 s on every branch |
| **the mind's reading of them** | `grep -nE "STATUS\|resource\|psutil\|rss\|cpu\|load" creature/mind.py` | **zero hits.** The body measures itself and the mind cannot see one number of it |
| live, this hour | `run/STATUS.json`, 09:57:49 Z | moments 2,612 · tape rows 1,205 · births 447 · arrivals 15 · budget_left 324 · refused 0 · cells 435 · rss 251.23 MB · mind 21.26 ms median |

**Two conditions every proposal in §4 obeys, because the body already has them.** (a) *Anything the mind consumes arrives as a tape row* — the mind is a pure function of (genome, SEED, tape) and the replay gate catches a one-row divergence [from disk: `docs/G4-DESIGN.md` §2 B4]. A "gut channel" that reads `/proc` inside `mind.py` would break replay; the interoceptive organ must therefore be a SENSE THREAD that publishes a reading onto the tape. (b) *Senses never write memory* — a sense publishes an immutable snapshot and nothing else [from disk: §2 B3]. So an "active sense" (a whisker) is split at the tape: the mind commands, the organ acts, the outcome arrives as a row, and the mind computes the residual against an expectation it journaled **before** the act. That is E21's shape exactly, and it is replay-safe.

---

## 1 · BIOLOGY — how each organ works, with its bin

### 1.1 TOUCH, SKIN, WHISKERS, THE LATERAL LINE

#### 1.1.1 The human skin: four FIXED channels, each a different filter on the same contact

The glabrous skin transduces one physical quantity — deformation — into four afferent classes that differ in receptive-field size, depth and pass-band. The channel set is genomic; nothing in a life changes a Pacinian corpuscle's corner frequency. [fetched: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2022.862344/full]

| afferent | end organ | receptive field | pass-band | depth | density, fingertip | what it carries | bin |
|---|---|---|---|---|---|---|---|
| **SA1** | Merkel | median **11 mm²** (min 5) | to **100 Hz**, peak **0.3–5 Hz** | 0.5–1 mm | **~100 /cm²**, RF spacing 1 mm | static form and roughness; "coarse features (>0.1–0.2 mm)" | **FIXED** |
| **RA1** | Meissner | median **12.6 mm²** (min 5) | **1–300 Hz**, peak **5–50 Hz** | 0.5–1 mm | **~150 /cm²**, spacing 0.82 mm | change in applied load; slip | **FIXED** |
| **RA2 / PC** | Pacinian | **5–10× SA1** | **5–800 Hz**, peak **30–500 Hz** | 2–3 mm | sparse; **one afferent per corpuscle** | "sub-micron vibrations of the skin"; fine features during motion; **vibration transmitted through a held tool** | **FIXED** |
| **SA2** | Ruffini | large | not quantified in this review | nail bed, deep dermis | — | skin stretch, applied force, limb posture | **FIXED** |

The molecular transducer under the touch classes and under proprioception is the same channel, **PIEZO2**; humans carrying PIEZO2 loss-of-function lose vibration detection, touch discrimination on glabrous skin, and joint proprioception together [secondary: https://pubmed.ncbi.nlm.nih.gov/28728817/ · https://www.nejm.org/doi/full/10.1056/NEJMoa1602812]. **The design lesson is the shared transducer with different MECHANICAL housings**: one detector, four filters, because the corpuscle is the filter. That is cheap to copy.

#### 1.1.2 The rat whisker: the act and the sense are ONE loop, and texture lives in the STATISTICS of failure

- **Active whisking 5–15 Hz** during exploratory palpation; the animal moves the sensor rather than waiting for the world [secondary: scholarpedia/Vibrissal texture decoding · https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.0060215]. **The motor command and the sense are the same loop** — which is why the whisker system is the standard preparation for reafference.
- **The resonance hypothesis was tested and lost.** Whiskers do resonate — fundamentals from **~35 Hz (the long Delta whisker) to ~110 Hz (the shorter D3)** — but "whiskers resonate in air and on surfaces, [and] these resonance vibrations do not vary with, and therefore do not encode, texture". What does carry texture is **slip-stick**: "discrete, high-velocity and high-acceleration slip-stick events … the rate and magnitude of slip-stick events varied systematically with texture" [secondary: Wolfe et al., *PLoS Biol* 2008, 10.1371/journal.pbio.0060215]. **FIXED** (the mechanics and the bank of differently-tuned whiskers) delivering an event stream the mind reads.
- One barrel per whisker in cortex: the topography is **FIXED**; what the barrel's population learns is the mind's.
- **The lesson for the creature, stated as a rule:** a texture is not a value a sensor reports; it is the *rate and size distribution of the sensor's own failures to move smoothly*. The analogue on this box is exact — running a program and reading where it sticks is a slip-stick stream, not a measurement.

#### 1.1.3 The star-nosed mole: touch that saccades, with a tactile fovea, at 13 Hz

This is the single most transferable animal in this document, because its touch is organised exactly like the creature's gaze — and it was measured to the millisecond. [PDF read: Catania & Remple, *Tactile Foveation in the Star-Nosed Mole*, Brain Behav Evol 2004;63:1–12, read in full here]

| quantity | value | bin |
|---|---|---|
| appendages | **22** (11 bilaterally symmetric pairs) | FIXED |
| the fovea | **the 11th pair**, "relatively small … just above the mouth" | FIXED |
| Eimer's organs on the star | **~25,000**; the star is innervated by **>100,000 myelinated fibres** against **~17,000 mechanoreceptors in the whole human hand** [secondary: Catania lab, Vanderbilt] | FIXED |
| one touch | **26 ms (SD 5)** | — |
| one saccade of the star | **50 ms (SD 2)**; duration typically 20–50 ms, mean **37 ms** — against human visual saccades of **30–60 ms** | — |
| touch + saccade = one search unit | **76 ms (SD 5)** → **~13 touches/second**, up to **17** | — |
| a foveal (11th-ray) contact on prey | **30 ms (SD 2.1)** | — |
| trials in which prey was found and eaten that ended in a saccade putting the 11th ray on it | **100 % of 526** | — |
| chance of a random first contact being the 11th ray | **1/22 = 4.5 %** | — |
| star velocity during a saccade | mean ~18 cm/s, peak ~40 cm/s, with acceleration and deceleration phases "resembl[ing] primate eye movements" | — |
| corrective saccades | observed, and "generally of shorter duration" | — |
| cortical area per Eimer's organ | ~900 µm² for ray 11 against ~150–250 µm² for rays 1–8 — magnification matches the contact distribution | FIXED |

**Three rules fall out, and all three apply to a creature that already has fixations.** (a) **A fovea is a POLICY, not just an anatomy**: exploration is random, and the *stereotyped* part is that first contact is followed by a saccade to put the high-resolution patch on the thing. (b) **The corrective saccade is built in** — the first foveation is often inaccurate and a second, shorter one follows. (c) **The unit of sensing is touch + saccade**, one period, 76 ms; the sensor is never still and the cost of moving it is a declared part of the budget. The creature's GAZE gene (`fixations 4 … glance 32`) is the same shape and has no corrective step and no foveal ray.

#### 1.1.4 The lateral line: the cleanest case of an organ that subtracts its own body's motion — and it does NOT simply cancel

- The cholinergic efferent system onto lateral-line hair cells is conserved across vertebrates. In zebrafish, spontaneous spiking in posterior lateral-line afferents falls during motor activity and **was absent for more than half of swimming trials**, and **photoablating the efferent neurons abolishes that inhibition** — so the efferent is necessary, and it is a corollary discharge of the swim command, not a mechanical consequence [secondary: *J Neurophysiol* 2020, 10.1152/jn.00594.2019].
- The 2021 result is the one worth copying, and it corrects the textbook. Verbatim from the abstract [fetched: https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3001420]:

  > "Commonly, CD in the peripheral nervous system cancels reafference to protect sensors and the central nervous system from being fatigued and overwhelmed by self-generated feedback. However, cancellation also limits the feedback that contributes to an animal's awareness of its body position and motion within the environment, the sense of proprioception. We propose that, rather than cancellation, CD to the fish lateral line organ **restructures** reafference to maximize proprioceptive information content. … CD interacts synergistically with sensor polarization to sharpen sensitivity along sensors' preferred axes. The sharpening of sensitivity regulates spiking to a narrow interval coinciding with peak reafferent stimulation, which prevents adaptation and homogenizes the otherwise variable sensor output. … which we term **external proprioception**."

  Mechanically: CD "hyperpolarizes hair cells so that a larger cupular deflection … is required to achieve the same evoked spike rate" — and the paper's own Results sentence for the size of it: *"On average, R_S and R_E were approximately 50 % (p < 0.001 … 5,859 total swims), comparable to previous studies"* — R_S the spontaneous-rate ratio, R_E the evoked-rate ratio [fetched, same]. (An earlier reading of this page gave a "0.1–0.9" range and an inverted quote saying CD cancels the *unpredictable* part; both were artefacts of the summariser and are corrected here against the paper's own words — the instrument, not the paper, was wrong.)
- **Bin: ADAPTS.** The gain change is commanded by the motor system and is not learned. **And the finding that matters most here: the residual is not waste — it IS the body-position sense.** An organ that cancels its own body's contribution perfectly is an organ that has destroyed its proprioception.

#### 1.1.5 Four more touch organs worth one row each

| animal | mechanism, with its number | bin | what it is FOR |
|---|---|---|---|
| **Platypus** | ~**100,000** separately innervated mechanoreceptors *and* electroreceptors in the bill skin; electroreceptors in rostro-caudal rows, mechanoreceptors uniform; range is computed from **the arrival-time difference between the fast electrical signal and the slow mechanical pressure pulse** of the same prey twitch [secondary: Scheich et al., *Electroreception and electrolocation in platypus*, **Nature** 1986, https://www.nature.com/articles/319401a0; *Electroreception in monotremes*, **J Exp Biol** 1999] | FIXED | **two modalities of one event, differing in propagation speed, give distance for free** — a pure timing computation, no learning |
| **Elephant** | Pacinian corpuscles concentrated in the foot pads (Bouley, *J Anat* 2007); rumble fundamentals **12–20 Hz**; ground propagation **~240–270 m/s** vs air **~309 m/s**; calculated maxima **16 km** (rumble), **32 km** (foot stomp) [secondary] | FIXED | the same message on two channels with different speeds and reaches |
| **Octopus sucker** | cephalopod-specific **chemotactile receptors (CRs)** that detect poorly soluble molecules on contact — "a form of contact-dependent, aquatic chemosensation"; **separate** chemo- and mechanosensory cells with distinct electrical signatures; "the peripherally distributed octopus nervous system exhibits exceptional signal **filtering** properties" [secondary: *Molecular Basis of Chemotactile Sensation in Octopus*, **Cell** 2020, https://www.sciencedirect.com/science/article/pii/S0092867420311491] | FIXED | touching IS tasting; and the filtering is done at the periphery, before anything central sees it — his prefilter, in an animal |
| **Spider web** | the web is an **extended sensory organ** — silk material properties tune which vibrations propagate; species differ in whether they monitor the web directly or through a signal thread to a retreat ("outsourced hearing") [secondary: Mortimer, Soler, Siviour, Zaera & Vollrath, *Tuning the instrument: sonic properties in the spider's web*, **J R Soc Interface** 2016, https://royalsocietypublishing.org/rsif/article/13/122/20160341] | FIXED, and **built** | the sense organ can be a STRUCTURE THE ANIMAL MADE. The creature already makes things; it does not yet read them as a sense |
| **Insect campaniform sensilla** | strain gauges in the cuticle; the *Drosophila* haltere carries **~140** of them against **<50** on the wing; afferents "entrain their firing to a preferred phase of the haltere stroke cycle" [secondary: *Encoding properties of haltere neurons enable motion feature detection in a biological gyroscope*, **PNAS** 2010, https://www.pnas.org/doi/10.1073/pnas.0912548107; *J Exp Biol* 2015] | FIXED | load sensing **phase-locked to the animal's own motor rhythm** — self-timed sampling |

---

### 1.2 SMELL AND TASTE — the cheap first channel, and a random expansion that is a hash

#### 1.2.1 Smell: a combinatorial code over a large FIXED receptor set

- Buck & Axel found the olfactory receptor gene family in 1991 (Nobel 2004). **Humans carry fewer than 400 functional OR genes; dogs 800–1,200; the mouse genome gives 913 intact OR genes and 296 pseudogenes** [secondary: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0000708 · https://pubmed.ncbi.nlm.nih.gov/14659017/]. One receptor type per sensory neuron; all neurons of a type converge on one or two **glomeruli**, so the glomerular sheet is a FIXED channel bank — the nose's tonotopy. An odour is a **pattern across channels**, never one channel's value. **Bin: FIXED.**
- Receptor desensitisation and central habituation give seconds-scale **ADAPTS**: the background stops being reported.

#### 1.2.2 The fly's mushroom body: the canonical sparse random expansion, and exactly where his rule cuts it

Numbers read from the paper itself [fetched: https://www.biorxiv.org/content/10.1101/180471v1.full — Dasgupta, Stevens & Navlakha, *Science* 358:793 (2017)]:

| stage | the fly | bin under his rule |
|---|---|---|
| input | "There are 50 ORN types" → a point in 50 dimensions | **FIXED** (the channel bank) |
| expansion | "The PNs expand the dimensionality, projecting to **2000 KCs**, connected by a sparse, binary random projection matrix" — a **40-fold expansion**; "Each Kenyon cell receives and sums the firing rates from about **6** randomly selected PNs" | **FIXED** — the matrix is random and never trained; R5 on disk adds that for *visual* KCs the input count is 1–7, **median 3**, "indistinguishable from shuffled" [from disk] |
| sparsification | "all but the highest firing **5 %** of Kenyon cells are silenced" by APL | **ADAPTS** — a runtime normalisation to a fixed sparsity, not learning |
| the tag | the surviving 5 % IS the hash for that odour | delivered to the mind |
| the readout | KC→MBON, ONE plastic layer, gated by a scalar dopamine wire that depresses exactly the synapses that were active, in the right temporal order [from disk: R5 §1.4, Hige 2015 / Aso 2014] | **LEARNS — and this is the MIND's half** |

**His rule cuts it between the tag and the readout**, and the anatomy agrees: everything before the tag is fixed wiring plus a gain control; the single plastic layer is the only thing that learns. The paper's three named departures from conventional LSH are worth quoting because each is a design choice we can take separately [fetched]: *"the fly uses sparse, binary random projections, whereas LSH functions typically use dense, i.i.d. Gaussian random projections that are much more expensive to compute. Second, the fly expands the dimensionality of the input after projection (d ≪ m), whereas LSH contracts the dimension (d ≫ m). Third, the fly sparsifies the higher-dimensionality representation using a winner-take-all mechanism, whereas LSH preserves a dense representation."* On MNIST at hash length k = 4 the fly scheme reads **44.8 %** against conventional LSH's **16.0 %** on the paper's own similarity-search metric [fetched — the number is quoted; the metric's name is not, so it is stated as the paper's own].

**Reconciling this with E15's FAIL — they are not the same claim, and the disk proves it.** E15 built the expansion as a **supervised 62-class glyph classifier** over a 22-dimension hand-built eye vector and it lost to a plain ridge readout (27.48 % vs 53.42 %) [from disk]. Dasgupta's claim is about **similarity preservation for nearest-neighbour search on an already-structured high-dimensional input** — not classification, and not on 22 dimensions, where a 40× expansion of a hand-built vector has nothing to spread. E22 then showed that inside the sparse arm the inhibition step is worth **+6.45 pp** and that removing the gate drops it to chance [from disk]. **The honest reading: E15 refuted the expansion as a feature learner for the eye; it did not test, and does not refute, the expansion as a HASH for recall.** The creature's recall today is a cosine over cells — the place where the fly's claim would actually apply — and nobody has measured it there. Named in §4 as a proposal with the test that could refuse it, not as a result.

#### 1.2.3 Taste: five FIXED channels and nothing else

Five qualities, with receptor families that are essentially labelled lines: **T1R2/T1R3** sweet, **T1R1/T1R3** umami, **25 human T2Rs** bitter (some narrow — T2R3, T2R5 — some broad — T2R14, T2R10, T2R46), **ENaC** salty; sour transduction is still not settled [secondary: https://pmc.ncbi.nlm.nih.gov/articles/PMC4764331/ · https://www.cell.com/fulltext/S0092-8674(03)00844-4]. **Bin: FIXED, all of it.** Taste is the smallest interesting sense in biology: five numbers, hard-wired to approach or reject, attached to *contact*. Smell surveys at a distance and is ambiguous; taste is unambiguous and requires commitment. That pairing — a cheap wide-ranging survey and an expensive committing check — is the transferable structure, not the chemistry.

#### 1.2.4 Two chemical navigators: the simplest possible prefilter, and the search when the signal is intermittent

- ***E. coli* run-and-tumble.** Runs of **~1 s** broken by tumbles of **~0.1 s**; ~**15,000** chemoreceptors per cell; the comparison is TEMPORAL — fast excitation against slow methylation-driven adaptation (tens of seconds) makes the output a **derivative**, and the methylation state IS the memory; adaptation makes the cell respond to **fractional, not absolute** concentration changes (logarithmic sensing) [secondary: multiple, incl. https://pmc.ncbi.nlm.nih.gov/articles/PMC2913400/ · bionumbers 100181]. **ADAPTS**, and it is the cheapest complete prefilter in biology: two timescales and a sign. Already proven on this box — the chemotaxis simulation WORKED and became Alpha 2's scheduler [from disk: DIG-2].
- **The moth's plume.** The signal is not a gradient but intermittent **filaments**; the strategy is **surge** upwind on contact and **cast** crosswind on loss. Vickers & Baker's model: "odor hits **suppress** an otherwise persistent internal counterturning mechanism, allowing moths to maintain straight trajectories if odors are frequent or long", and moths fly "faster and straighter upwind within odor plumes with lower odor plume intermittency" [secondary: *J Exp Biol* 10.1242/jeb.250945 · *Annu Rev Entomol* 2020]. **Bin: FIXED** (the default is the search; evidence *inhibits* it). The inversion is the lesson: the organism's baseline behaviour is casting about, and a hit does not *command* the surge, it *releases* it by suppressing the counterturn. A creature whose default is "keep looking" and whose evidence merely suppresses the looking has a different failure mode from one whose default is "wait" — it never stalls.

---

### 1.3 BALANCE, THE VESTIBULAR SENSE, AND PROPRIOCEPTION — knowing what your own body is doing

| organ | what it transduces | numbers | bin |
|---|---|---|---|
| **semicircular canals** (3 per ear, near-orthogonal) | angular head motion; fluid inertia deflects the cupula | three axes; integrate acceleration toward velocity over the behavioural band [secondary: *J Neurophysiol* 2019 10.1152/jn.00708.2018] | **FIXED** |
| **otoliths** (utricle, saccule) | linear acceleration **and gravity — the same signal** | two organs; "measure linear accelerations, including detection of the effects of gravity" [secondary: Kandel ch. 27] | **FIXED** |
| **VOR** | eye counter-rotation against head rotation | **latency 6–14 ms**, "the short latency resulting from the 3 neuronal reflex arc" [secondary: Physiopedia; Kandel ch. 27] | **FIXED** arc |
| **VOR gain** | the multiplier from head velocity to eye velocity | changed by magnifying/minifying lenses or reversing prisms; "learning requires the presence of the cerebellum"; the site is flocculus parallel-fibre→Purkinje LTD (Marr–Albus–Ito) [secondary: https://pmc.ncbi.nlm.nih.gov/articles/PMC2041974/ · https://pmc.ncbi.nlm.nih.gov/articles/PMC5871328/] | **LEARNS — see the ruling below** |
| **muscle spindle Ia** | muscle length **and velocity** | group Ia; gamma fusimotor drive sets its operating point during movement | **FIXED** sensor, **ADAPTS** gain |
| **muscle spindle II** | length only | group II | **FIXED** |
| **Golgi tendon organ Ib** | muscle **tension** | group Ib [secondary: *Molecular correlates of muscle spindle and Golgi tendon organ afferents*, **Nat Commun** 2021, https://www.nature.com/articles/s41467-021-21880-3] | **FIXED** |
| **halteres** | body rotation, via **Coriolis force** on a club oscillating at wingbeat frequency | "the only true biological gyroscope"; ~140 campaniform sensilla per haltere; afferents phase-locked to the stroke cycle [secondary: **PNAS** 2010 10.1073/pnas.0912548107; *J Exp Biol* 2015] | **FIXED** |

**The VOR-gain ruling, and why it is arguable.** Under the brief's bins this is **LEARNS**, and I am calling it that, because: the canals never change, the three-neuron arc never changes, and what changes is a *multiplier* acquired over hours-to-days by LTD in the cerebellar cortex — a central structure, driven by an error signal (retinal slip), and it persists. The counter-case Ahmad may make is that the flocculus is not "the mind" in any sense he cares about: it is a fixed circuit that computes a gain, it stores no episode and answers no question, and the organism cannot tell you what it learned. **Both readings are defensible and they lead to different designs**, so it is question 2 in §5. My call and its reason: *if the update rule reads an error and the change persists, it is learning wherever it sits* — the alternative makes "ADAPTS" mean "learning I did not want to call learning".

**Path integration, the only body-sense entry already on disk.** *Cataglyphis* returns home on a straight line by integrating **two independent odometers** (stride count and optic flow) against **a sky-polarisation compass**, correcting by landmarks, in a 0.1 mg brain [from disk: `ALPHA-2-DEEP-RESEARCH §3.5`]. **FIXED** integrator, **ADAPTS** correction. The transferable part is *two independent estimates of the same quantity plus a third, absolute reference* — a design that detects its own drift.

---

### 1.4 INTEROCEPTION — the body reporting on itself

- **The channel.** The vagus is ~**80 % afferent**; at the cervical level unmyelinated C-fibres are **65–85 %** of all fibres [secondary: *Human organ donor-derived vagus nerve biopsies…*, **Sci Rep** 2021, https://www.nature.com/articles/s41598-021-03248-1; and multiple reviews agreeing on the ~80 % figure]. Biology spends most of a major nerve carrying the body's own state *inward*. The proportion is the point: interoception is not a small side channel.
- **The computation is predictive, not a gauge read.** The EPIC / interoceptive-inference account (Barrett & Simmons, *Interoceptive predictions in the brain*, **Nat Rev Neurosci** 2015, https://www.nature.com/articles/nrn3950; and Seth's interoceptive-inference work): "interoceptive experience may largely reflect limbic predictions about the expected state of the body that are constrained by ascending visceral sensations", with agranular visceromotor cortices issuing predictions and the posterior insula carrying the sensation they are checked against [secondary: https://www.nature.com/articles/nrn3950 · PMC12092441]. **Allostasis** (Sterling) is the framing: "the continual process by which the brain **anticipates** the needs of the body and attempts to meet those needs **before they arise**" — against Cannon's homeostasis, which reacts to a deviation. **Bin: the readings are the organ's (FIXED channels); the prediction is the MIND's (ADAPTS at the organ, LEARNS centrally).**
- **A set point is not enough, measured.** AgRP "hunger" neurons are **inhibited within seconds by the sight and smell of food, or by cues that predict it — before a single bite**, and "these responses were much too fast to be mediated by a hormonal signal" [secondary: Chen, Lin, Kuo & Knight, *Sensory Detection of Food Rapidly Modulates Arcuate Feeding Circuits*, **Cell** (2015), https://www.cell.com/fulltext/S0092-8674(15)00076-8 — my first draft credited this to "Betley et al." from recall; the authorship was checked and corrected]. So the drive is *already* a prediction about future body state, not a reading of the present one. A creature whose drives move only when its meters move is a Cannon creature; biology is a Sterling creature.
- **Sleep pressure is the honest model of a FIXED timer.** The two-process model: Process S rises as a saturating exponential during waking and declines exponentially in sleep, interacting with circadian Process C; slow-wave activity is its measurable proxy; adenosine is among the biochemical carriers [secondary: Borbély, *The two-process model of sleep regulation: Beginnings and outlook*, **J Sleep Res** 2022, https://onlinelibrary.wiley.com/doi/10.1111/jsr.13598]. **FIXED.** The organism does not decide it is tired.
- **What this box has already proved about interoception, twice, and it is the sharpest evidence in this document:** SOLUTIONS **#230** — one bad glyph aborted the organism 90 times in 20 minutes while `minipc-health` and `alpha3-memwatch` both stayed green, "because the unit read `active` … and neither reads restarts or the counter's MOTION"; SOLUTIONS **#233** — a per-arrival birth budget the mind never refreshed, found only by a per-1,000-rows **series** of births (161 · 46 · … · **0 · 0 · 0 · 0 · 0 · 0**), invisible to every surface showing the total [from disk]. **Both are interoceptive failures of exactly the kind biology solved with a vagus: the body was in trouble and nothing inside could feel it.** The rule those incidents produced — "the moment a design has a budget, its remaining and its refusals belong on the surface" — is the interoceptive channel specification, already written, for one variable.

---

### 1.5 EFFERENCE COPY AND COROLLARY DISCHARGE — the mechanism no organism here has ever had

#### 1.5.1 The theory and its two names

Both 1950, independently [fetched: https://pmc.ncbi.nlm.nih.gov/articles/PMC7403230/]:

- **von Holst & Mittelstaedt — the reafference principle.** An "efference copy" is used to **subtract** self-generated sensory input (*reafference*) from externally caused input (*exafference*). Their evidence was a fly whose head was rotated 180°: with the sign of the visual feedback inverted, the animal circles without end.
- **Sperry — corollary discharge.** "An internal signal that is the direct result of a motor command", integrated in the optic tectum; his preparation was a surgically eye-rotated fish, which also circled.
- **The two words are not synonyms** and the distinction decides a design: "Efference copy has a narrower meaning (subtractive signal for canceling predictable input), while corollary discharge is broader, encompassing **inhibition, facilitation, and modulation** of sensorimotor processing." Crapse & Sommer's own split, already on disk: *lower-order* CD does "reflex inhibition and sensory filtration"; *higher-order* CD serves "sensory analysis and stability, and sensorimotor planning and learning" [from disk: R6 §C-4].

#### 1.5.2 The mormyrid electric fish — the best-measured case, and the bin question

The fish discharges its own electric organ and must read the field distortion caused by objects through the distortion caused by itself. [fetched: PMC7403230 · secondary: Kennedy & Sawtell, *A temporal basis for predicting the sensory consequences of motor commands in an electric fish*, **Nat Neurosci** 2014 — the full text redirected to an authorisation page, so this is read through the PMC history review and search results, never the paper; Bell, *Synaptic plasticity in the mormyrid electrosensory lobe*, **J Exp Biol** 1999]

- After pairing a command with a sensory input, ELL cells' responses to the command alone become **"a faithful negative image of the cell's response to the paired sensory input"**; when the input is removed, the negative image is what is left, and it then decays — "a constant process of updating the negative image as the sensory consequences of behavior changed".
- The rule is **anti-Hebbian spike-timing-dependent plasticity** at parallel-fibre synapses onto Purkinje-like cells: "EPSPs … **preceding** broad spikes induced synaptic **depression**, whereas EPSPs **following** broad spikes induced synaptic **potentiation**" — the exact inverse of Hebb, which is what makes it build a *negative*.
- Corollary-discharge facilitation in the mormyromast pathway sits in a narrow window of **6–11 ms** after command onset.
- The 2014 result names the missing piece: a *brief* command cannot cancel a *prolonged* response, so granule cells (via unipolar brush cells) supply a **temporal basis** — "delayed responses that closely match the timing of self-generated sensory inputs" — and plasticity at granule-cell→medium-ganglion-cell synapses fits a weighted sum of that basis to the shape of the reafference.

**The bin call, and it is the one Ahmad is most likely to dispute. I split it, and the split is the design:**

| the half | what it is | bin |
|---|---|---|
| the **subtraction** at the ELL cell: incoming minus the negative image, residual out | runs every discharge, no error signal, nothing stored | **ADAPTS** |
| the **negative image** itself: a weighted sum over a temporal basis, fitted by anti-Hebbian STDP, decaying and continuously re-fitted | an error-driven, persisting, learned model of the body's own effect | **LEARNS** |

A single bin is wrong here and would produce the wrong organ. If the whole thing is ADAPTS, one writes a fixed subtraction and the organ cannot follow a body that changes. If the whole thing is LEARNS, one puts the subtraction in the mind and pays the mind's latency on every sample. **Biology puts the learned model in a cerebellum-like structure that is not the animal's mind, and the subtraction at the sensor.** Under his rule that reads cleanly: *the prediction is the mind's and is sent down; the organ subtracts and delivers the residual.* That is exactly the ADAPTS definition in `BRIEF.md` line 11, and the mormyrid is its existence proof.

#### 1.5.3 Four more, each adding one thing the mormyrid does not

| system | the finding, with its number | what it adds | bin |
|---|---|---|---|
| **Cricket** (Poulet & Hedwig — *A corollary discharge maintains auditory sensitivity during sound production*, **Nature** 2002, https://www.nature.com/articles/nature00919; *The Cellular Basis of a Corollary Discharge*, **Science** 2006, https://www.science.org/doi/10.1126/science.1120847) | pre- and postsynaptic inhibition of auditory neurons **in phase with the song pattern**, persisting in a **fictively singing, isolated CNS** — so it is a copy of the motor command, not an acoustic consequence; and the 2006 paper found **ONE multisegmental interneuron** does it [secondary] | the whole thing can be **one cell**, and its purpose is stated as *"maintains auditory sensitivity"* — it prevents DESENSITISATION, it is not only about attribution | ADAPTS |
| **Tickle** (Blakemore, Wolpert & Frith, *Why can't you tickle yourself?*, **NeuroReport** 11(11), 3 Aug 2000, pp. R11–R16 — read in full here; and *Central cancellation of self-produced tickle sensation*, **Nat Neurosci** 1998, https://www.nature.com/articles/nn1198_635) | 16 subjects; self-produced tactile stimulus rated significantly less tickly (p < 0.001); tickliness rises **progressively** as the delay between the moving hand and the stimulus goes **0 → 100 → 200 → 300 ms** (p < 0.0005) and as trajectory rotation goes **0 → 30 → 60 → 90°** (p < 0.01) — at 300 ms and at 90° it is rated essentially as externally produced. Right anterior cerebellum "selectively deactivated by self-produced movement that resulted in a tactile stimulus, but not by movement alone" [PDF read] | **the attenuation is GRADED by the size of the mismatch, in time and in content** — this is the single most useful number in this section, because it says the prediction must be precise in *when* as well as *what*, and that the residual is a continuous quantity, not a flag | ADAPTS, with a LEARNS model |
| **Cerebellum as a forward model** (Wolpert, Miall & Kawato, *Internal models in the cerebellum*, **Trends Cogn Sci** 2(9):338–347, 1998) | forward models "predict the consequences of actions and can be used to overcome time delays associated with feedback control"; paired forward/inverse models [secondary] | the reason to build one at all is not only self/world attribution — **it is that a prediction is available before the feedback is** | LEARNS |
| **Songbird** | "Auditory synapses to song premotor neurons are **gated off** during vocalization in zebra finches" [secondary: *Auditory synapses to song premotor neurons are gated off during vocalization in zebra finches*, **eLife** 2014, https://elifesciences.org/articles/01833] | the crudest form — a **gate**, not a subtraction — is sometimes the whole mechanism; cheap, and it throws the residual away | ADAPTS |
| **Saccadic suppression and remapping** | handed to the EYE document; one line here: the visual system's version of this mechanism is where "the world does not jump when the eye does" comes from, and it is the same principle applied to the creature's gaze | — | — |

#### 1.5.4 What an organ that ACTS needs, named per act, for this creature

Under his rule — *the mind's prediction goes down, the organ subtracts, the residual comes up* — every act the creature performs needs one. **The finding of §0.3.2 is that it performs none.** The four candidates, and what each actually is today:

| the act | who causes the sensory change | what the mind should send down before the act | what the residual would mean | status |
|---|---|---|---|---|
| **GAZE** — the mind chooses 4 fixations | **nobody — it is not an act on the world.** The four fixations are crops of one already-delivered PNG, computed inside the mind (§0.3.2) | — there is no reafference to copy | — | **not a candidate.** The related and real question — whether the mind should predict what a *chosen* crop will look like, i.e. a saccade as an experiment — is R2's territory and is handed to the EYE document |
| **the folder door** — Ahmad adds a picture | the world, never the creature | — (a pure exafference channel; its provenance is already exact) | — | live; correctly has none |
| **the maker's world** | a seeded generator, not the creature | — | — | live; correctly has none |
| **HANDS** — run what he writes in the jail | **the creature** | the expected output of the program | "the program did something I did not predict" = the only learning signal a maker has | **declared OFF** [from disk: `genome/G4.genome`]. **This is the first real candidate**, and the forward model must exist before it is switched on, or the first act is uninterpretable |
| **the web door** — `WORLD … web 6 per hour by curiosity` | **the creature**, if it chooses which page to open | the expected content of the page it chose | "what I chose to fetch was not what I expected" | **parsed and unimplemented** — `web_per_hour` reaches `declared` and no sense thread reads it [from disk: `genome/machinery.py:257–259`]. The second candidate, and it arrives whenever that door is built |

**And the deepest point in this section, which the tape makes unusual:** biology needs corollary discharge for **attribution** because it has no provenance — a hair cell cannot know what moved it. The creature's tape stamps `meta.source` ("maker" / "folder") on every row, so **attribution is free here** and E21's 100 % discrimination is, for this creature, measuring something it already knows. What is *not* free, and what the forward model is actually for, is **content**: did my act produce what I expected? That is the residual, and no provenance field can supply it. **And a creature with no acts has no residual to compute — which is why §4.2 is written as a precondition on the first act rather than as a gene to add now.**

---

### 1.6 The animal register — EXTENDED, not rebuilt

`alpha1-organism-capabilities-research-2026-08-24.md` holds 17 rows on two axes (**Mapping**: HAVE / PARTIAL / MISSING-and-buildable / N-A; **Grade**: TRUE / OVERSTATED / EARLY / N-A). It has no body-sense row. These are proposed as rows 18–28, in its format, each graded against the **creature** as it runs today.

| # | organism | capability, with its number | Mapping | Grade | note |
|---|---|---|---|---|---|
| 18 | **Star-nosed mole** | touch that saccades: touch 26 ms + saccade 50 ms = 76 ms, ~13/s; 11th-ray tactile fovea used in 100 % of 526 successful trials; corrective saccades [PDF read] | **PARTIAL** — GAZE picks 4 fixations by saliency but has no fovea ray and no corrective step | **TRUE** | the closest animal to the creature's existing machinery |
| 19 | **Rat whisker system** | active whisking 5–15 Hz; texture in slip-stick rate/magnitude, **not** in resonance (35–110 Hz fundamentals do not vary with texture) [secondary] | **MISSING-and-buildable** — the creature acts (HANDS, declared OFF) but never senses the act's own roughness | **TRUE** | the "act and sense are one loop" case |
| 20 | **Zebrafish lateral line** | efferent CD cuts spontaneous afferent rate ~50 %, absent in >half of swim trials; ablation abolishes it; CD **restructures rather than cancels**, yielding "external proprioception" [fetched] | **MISSING** | **TRUE** | the best argument for keeping the residual |
| 21 | **Mormyrid electric fish** | negative image built by anti-Hebbian STDP over a granule-cell temporal basis; CD facilitation window 6–11 ms [fetched/secondary] | **MISSING** | **TRUE** | the split-bin case (§1.5.2) |
| 22 | **Cricket** | one multisegmental interneuron; pre+postsynaptic auditory inhibition in phase with the song, in a fictively singing isolated CNS [secondary] | **MISSING** | **TRUE** | proof that the organ can be tiny |
| 23 | **Fly mushroom body** | 50 → 2,000 (40×) sparse binary random expansion, ~6 PNs per KC, APL keeps top 5 %; MNIST k=4: 44.8 % vs LSH 16.0 % on the paper's own metric [fetched] | **PARTIAL** — E15 refuted it as a supervised feature learner (27.48 % vs ridge 53.42 %); **untested as a recall hash**, which is its actual claim [from disk] | **EARLY** | the E15/Dasgupta reconcile of §1.2.2 |
| 24 | ***E. coli*** | runs ~1 s / tumbles ~0.1 s; derivative from fast excitation vs slow methylation; ~15,000 receptors; **fractional**, not absolute, sensing [secondary] | **HAVE** (as a scheduler — Alpha 2, retired) / **MISSING** in the creature | **TRUE** | already proved on this box [from disk: DIG-2] |
| 25 | **Moth** | surge/cast on an intermittent plume; hits **suppress** a persistent counterturn rather than commanding the surge [secondary] | **MISSING-and-buildable** — CURIOSITY chooses what to think about but has no "keep casting" default | **TRUE** | the never-stall default |
| 26 | **Platypus** | ~100,000 bill receptors; **range from the arrival-time difference** between the electrical and mechanical signatures of one event [secondary] | **MISSING** | **TRUE** | two speeds of one event = distance, free |
| 27 | **Octopus sucker** | cephalopod-specific chemotactile receptors; taste by touch; separate chemo- and mechano-cells; peripheral **filtering** [secondary] | **MISSING** | **TRUE** | his own prefilter idea, in an animal, at the periphery |
| 28 | **Spider** | the **web** as an extended sense organ whose material properties tune what propagates; some species monitor it remotely by a signal thread [secondary] | **MISSING-and-buildable** — the creature will make things (HANDS) and has no way to read what it made as a sense | **EARLY** | the deepest one; see §4 line 6 |

---

## 2 · SOFTWARE AND MACHINE — the two lists, kept apart

### 2.1 (a) What MIMICS biology in code — and what each costs on this box

The box: **16 cores, no GPU**. Life 2's verdict reads the mind's moment as **"COST live 26.3 ms vs solo 47.7"** [from disk: PREREG §18, quoted as written — the live figure is the lower of the two]; the live hour reads **21.26 ms** median; RSS 251 MB now, 397 MB at the end of life 2 [from disk: `run/STATUS.json`, `docs/G4-PREREG.md` §18]. Every cost below is against a ~26 ms moment.

| the biology | the code | cost per moment | bin it keeps |
|---|---|---|---|
| four mechanoreceptor classes = one transducer in four **housings** | one event stream read through N fixed filters (a pass-band each), never N sensors | O(N) over a short buffer; microseconds | FIXED |
| slip-stick texture coding | the **rate and size distribution of discrete failures** in a stream (a program's stalls, retries, non-zero exits), not its mean | counters; free | FIXED |
| the star-nosed mole's touch+saccade unit | the existing `GAZE` loop plus **a corrective fixation**: one more glance per canvas | +1 glance ≈ +25 % of the glance cost of a canvas; measurable, small | FIXED policy |
| a tactile fovea | one fixation designated high-resolution (a larger window or a second pass at finer grain) | one extra window crop | FIXED |
| the lateral line's efferent gain | scale the delivered residual by a factor the mind sent down; never a mute | one multiply | **ADAPTS** |
| glomeruli as a channel bank | a fixed, seeded set of cheap feature extractors over the *pre-look* metadata of a thing | negligible | FIXED |
| the fly's sparse binary random expansion + top-k | a seeded sparse binary matrix (≈6 ones per row) and a k-WTA | 50→2,000 with 6 nonzeros per row is 12,000 adds — **well under 1 ms in numpy**; the storage is the cost, not the compute | FIXED wiring, ADAPTS gain |
| run-and-tumble | two exponential moving averages at different time constants and the sign of their difference | two floats | ADAPTS |
| the moth's counterturn suppression | a default search that evidence **inhibits**, rather than an idle state that evidence triggers | free, and it is a control-flow choice not a module | FIXED |
| path integration with two odometers and a compass | two independent estimates of one quantity plus an absolute reference; **disagreement is the drift alarm** | two counters | FIXED |
| the mormyrid's negative image over a temporal basis | a small weighted sum over a basis of delayed copies of the act, fitted by an anti-Hebbian rule | a dot product per sample; the basis is the memory cost | **LEARNS** (the model) + **ADAPTS** (the subtraction) |
| interoceptive prediction | the mind's expected next STATUS row, subtracted from the arriving one | one vector difference every 10 s | ADAPTS |
| sleep pressure | a saturating exponential rise on waking work and an exponential decay in sleep — a **FIXED timer**, not a decision | one float | FIXED |

### 2.2 (b) What biology CANNOT do, and this machine can

Kept separate because these are not mimicry and none of them has a bin — they are properties of the substrate. The six rows of `RESEARCH-2026-09-16-HUMAN-MECHANISMS §4` stand [from disk]; these are the body-sense-specific ones, and the first three are the important ones.

| the affordance | why no animal has it | what it buys a BODY sense | the condition it must obey here |
|---|---|---|---|
| **Provenance on every sensory event.** The tape stamps `meta.source` on every row | a hair cell cannot know what moved it — which is *why* corollary discharge exists | **self/world attribution is free.** E21's 100 % is therefore not the creature's problem; the forward model is needed for CONTENT (did my act produce what I expected), not for authorship | the stamp must be written by the sense, never inferred by the mind |
| **Exact, replayable proprioception.** `moments`, `births`, `arrivals`, `budget_left`, `refused`, `sense_restarts`, `mind_ms` are counted, not estimated | no animal knows its own neuron count, its refusal count, or its own latency | a body sense with **zero measurement noise** — the thing biology spends 80 % of a vagus approximating | it must reach the mind **through the tape**, or the replay gate breaks |
| **The residual can be kept forever.** Every predicted-vs-actual pair is a row | biology discards the residual after use | the forward model's own training set accumulates without a rehearsal buffer | the row must carry the prediction, not only the error |
| **Senses outside any animal's band.** A file's size, type, mtime, hash; a process's RSS; a socket's latency | no receptor exists for these | a **smell** channel that is genuinely free and genuinely informative — see §4 line 5 | it is still a prefilter: cheap, wide, ambiguous, never a decision |
| **N bodies.** Forked selves on 16 cores, each with its own root | one body, one attention | the twin that is blind to exactly one sense is a real experiment, not a thought one | already the estate's practice [from disk] |
| **No fatigue, no adaptation drift** | every biological sensor adapts whether or not you want it to | a channel that means the same thing on hour 1 and hour 24 | **and this is a LOSS as well as a gain** — adaptation is what makes biology report *change*. If we want change, we must build the derivative on purpose (row: run-and-tumble) |
| **A sense organ that is a structure the creature MADE** | the spider is the only animal that really has this, and its web is fixed silk | a file, a folder, a program's output can be *both* an act and a sensor | the read must come back through a sense thread onto the tape, never by the mind opening the file |

---

## 3 · BENEFITS AND GAPS — against the creature as it runs today

"Today" = `docs/G4-DESIGN.md` §1, `docs/G4-PREREG.md` §11/§17/§18, life 2's verdict (`runs/g4-verdict-life2-20260921-1215/VERDICT.md`: FAIL on exactly (v) and MODULATION, every other mark PASS), and the live `run/STATUS.json` read at 09:57 today.

| gap in the creature today | filled by BIOLOGY (which mechanism) | filled by SOFTWARE / MACHINE (which feature) | still open |
|---|---|---|---|
| **The mind cannot feel its own body.** `mind.py` contains zero reads of STATUS, rss, cpu or load; the body measures itself every 10 s and the mind never sees a number of it | the vagus (~80 % afferent); interoceptive predictive coding; allostasis | a `body` sense thread publishing the STATUS vector onto the tape; every field exact, no noise | what the mind should *do* with it — drives are the mind's, and that is the mind document's question. **This organ delivers readings only** |
| **The creature has no forward model of its own acts — and no acts.** PREDICT computes `1 − max cos(glance, nearest resonating cell)`, memory-relative and act-blind; and the body starts two sense threads, both driven from outside it [from disk: `genome/predict.py`, `creature/body.py:372, 383`] | efference copy (von Holst); the mormyrid negative image; the cerebellum as a forward model that beats the feedback delay | E21 already built and passed the instrument on this box (AUC 1.0, still 93.33 % with the model 40 % corrupted) | **the gap is real and not yet reachable** — it opens the day `HANDS` or the web door is switched on, and it must be closed before that day, not after (§4.2) |
| **The WHERE is thrown away.** `mind.py:230` journals `"fix": [[y,x],…]`; `org.moment(x, xw)` receives only the feature. Nothing the creature remembers knows where it was looking | the BRIEF's own definition of a trait ("a channel value with its where and when"); the mole's cortical map; place/grid cells | the coordinates are already computed, already exact, already on the journal — the cost of carrying them is two integers | whether adding them helps or merely widens the vector: **testable, untested** |
| **MODULATION failed twice**, and §18 names the mechanism: a memory-relative error cannot see a new thing that resembles an old cell (moon ≈ circle, 0.9–1.9×) while a thing that births its own cell spikes 54–63× | the lateral line: CD **restructures** rather than cancels, and the residual is the signal; the tickle result: attenuation is **graded** by mismatch in time and content | a residual computed against an expectation of *what comes next in the stream*, rather than against the nearest thing already held | **this one is NOT about acts** — the creature's canvases arrive whatever it does, so the fix here is a better world-model, not an efference copy; the two were conflated in my first draft and are separated here. Whether it fixes MODULATION is open, and the mark would have to be re-derived either way |
| **The gaze has no fovea and no corrective step.** `GAZE surprise fixations 4 …` — four saliency-picked fixations, no second look | the star-nosed mole: 100 % of 526 successful trials ended in a saccade putting the 11th ray on the prey; corrective saccades are routine | one extra glance per canvas, ~25 % more glance cost, measurable against the existing (x)/(xi) marks | whether it buys anything on *drawn* worlds, where the things are already simple |
| **Nothing the creature senses is cheap.** Every canvas costs 4 glances through the tower; there is no survey channel | smell vs taste: a wide ambiguous distance sense that decides what the expensive contact sense commits to | file type, size, folder name, hash — a **free** channel available before any picture is decoded | whether a cheap channel that never decides anything earns its place |
| **The creature does not act.** `HANDS` declared OFF; `web 6 per hour by curiosity` parsed into `web_per_hour` and implemented by nothing; the gaze is a crop, not a movement [from disk] | the whisker (the act and the sense are one loop); the platypus (two signatures of one event); the moth (the act *is* the search) | the jail already returns exit code, stdout and timing — a slip-stick stream for free the day it is on | the forward model must exist **before** the first act, not after; and until then §4.2 cannot even be measured |
| **No sense of what it has made.** The maker writes truth files the mind never reads; the creature will write programs and never read them back as a world | the spider's web as an extended sense organ | a sense thread that reads the creature's own output directory the way the folder door reads Ahmad's | this is the deepest and least urgent; named, not proposed for now |
| **A budget's refusals reached no surface until they cost a life** (#233); a crash loop ran 90 times under two green monitors (#230) | interoception as a first-class nerve, not a side channel | the fields already exist in `_build_status`; the fix is that the **mind** and a **series** read them | fixed for one variable, unfixed as a principle |

---

## 4 · The growth instructions proposed

Drafts in the genome's own syntax (`NAME  value words  # source`), read from `genome/G4.genome` and `docs/G4-DESIGN.md` §9. **Proposals, not decisions.** Each carries its source and the small test that could refuse it. Ordered by what each would settle, not by ease. Nothing here is written to any genome file.

### 4.1 The body's own report — an interoceptive sense

```
SENSE    body   every 60 s fields moments births arrivals budget_left refused restarts mind_ms rss
```
**Source:** the vagus is ~80 % afferent [secondary]; interoceptive predictive coding (Barrett & Simmons 2015) [secondary]; and on this box, SOLUTIONS #230 (90 aborts under two green monitors) and #233 (a budget whose refusals no surface showed) [from disk].
**How it obeys the body's two conditions:** it is a SENSE THREAD, so it publishes a row onto the tape (`sense: "body"`, payload = the STATUS vector as bytes, `meta.source: "body"`) and the mind reads it as it reads any row — replay stays exact, because the reading enters through the tape's instants like everything else. It writes no memory. The 60 s period is a proposal; the body already writes STATUS every 10 s, so 60 s is 1 row per minute against the maker's 720 canvases per hour — a genuinely slow sense, like the folder door.
**The test that could refuse it:** run one life with the sense armed and one without, on the same tape, and count the moments in which any journaled decision differs. **If the count is zero, the channel is a no-op and the gene is refused** — computing a value and consuming it are two features (SOLUTIONS #163/#180). A second, cheaper refusal: if the row's fields do not move over an hour in which the body's own STATUS moved, the sense is reading the wrong thing.
**What it explicitly does NOT do:** it delivers readings. Hunger, tiredness and a set point are the MIND's, by his rule; this gene must not carry a threshold.

### 4.2 The copy of an act — a precondition on the first act, not a gene to add now

```
COPY     hands  expect before the act; organ delivers residual; mind keeps both   # OFF until HANDS or the web door is on
```
**Why it is written as a precondition:** §0.3.2 found, by reading the code rather than assuming, that **the creature performs no act with a sensory consequence today**. The gaze is a crop of an already-delivered payload; the maker is seeded; the folder door is Ahmad's act, not his. So there is nothing yet for a copy to be a copy *of*. The moment that changes — `HANDS` switched on, or the `web` door built — this becomes the first thing to build, and it must be built **before** the act, not after.
**Source:** his own sentence in the AGI Q&A — *"the brain actively sends a prediction down to the organ, which reports back confirmation or error"* [from disk]; von Holst & Mittelstaedt 1950 and Sperry 1950 [fetched]; the mormyrid's negative image and its anti-Hebbian rule [fetched]; the graded tickle attenuation across 0–300 ms of delay and 0–90° of rotation [PDF read]; and E21's own PASS on this box [from disk].
**The shape:** before the act, the mind journals what it expects the act to produce; the act is performed; the outcome arrives as a tape row; the residual is `actual − expected`, and the residual — not the raw outcome and not a memory-relative novelty — is what grades the act, scales learning and ranks replay. **The subtraction is ADAPTS; the expectation is the mind's and LEARNS.** That is the split the mormyrid makes (§1.5.2) and what `BRIEF.md` line 11 already describes. The tickle result fixes the demand on the expectation: attenuation is **graded by the mismatch in time as well as in content**, so the prediction must name *when* the outcome is due, not only *what* it will be — which is exactly the four fields `FILE` already requires (claim, route, decider, due) [from disk].
**The test that could refuse it, with its controls — and the plant must be placed where the mechanism can fire (#228 (a)):** for `HANDS`, (i) a **world plant**: the same program run while something outside it changed its input; (ii) an **act plant**: a different program run against an unchanged world. The residual must be large on (i) and small on (ii). **If it is large on both, the residual is reading change magnitude and not prediction** — the twin E21 already ran (magnitude-only 59.17 % against the model's 100 %, 40.83 pp apart) [from disk], and it must be run here too. The third control, also E21's: a **constant predictor** ("nothing changes"); if it scores the same, the forward model is decoration.
**What would make me drop it:** if, when the first act exists, the act plant's residual is already small under today's memory-relative error, the creature does not have the problem. That measurement costs an afternoon on a closed life's record and should be made **before** any code — and it cannot be made at all until there is an act.

### 4.3 The where, carried with the trait

```
TRAIT    where  fixation y x of canvas; delivered with every glance feature
```
**Source:** `BRIEF.md`'s own definition — a trait is "a channel value with its **where** and **when**"; the mole's cortical map, in which contact frequency and cortical area track each other [PDF read]; and the fact that the coordinates are already computed and already journaled and simply stop there [from disk: `creature/mind.py:230` vs `:220`].
**The test that could refuse it:** a **position-only family** — the same drawn thing in the upper vs the lower half of the canvas, byte-identical windows, differing only in the window's coordinates. With the where carried, the creature must separate them; without it, it must be at chance. **The control has to be structural, not hoped for** (SOLUTIONS #228 (c): the tower's 4×4 pool keeps coarse position by construction, so a family built by *rendering* the thing in two places is not blind to today's eye — the two classes' 32×32 frames must be byte-identical and only the window's coordinates differ).
**And the refusal that matters more:** on the ordinary held-out marks (i)–(vi), carrying the where must cost **nothing**. If the wider vector dilutes the cosine and (i) falls, the gene is refused however well it does on the position family.

### 4.4 A fovea and a corrective look

```
GAZE     surprise fixations 4 grid 16 canvas 128 glance 32 ink border fovea 1 correct 1
```
**Source:** Catania & Remple 2004, read in full: touch 26 ms + saccade 50 ms = 76 ms, ~13 touches/s; the 11th ray used in **100 % of 526** successful trials; corrective saccades routine and shorter; cortical magnification matching the contact distribution [PDF read].
**The shape:** after the first four fixations, one more glance is taken at a finer grain, centred on the strongest-responding fixation — the creature's version of "put the fovea on the thing you just found". `correct 1` allows exactly one such re-look, as the mole's corrective saccade allows one.
**The test that could refuse it:** the existing marks (x) (the gaze finds the thing: 1.0 vs random 0.082 in life 2) and (xi) (the multi-glance gain: +0.14 over the one-glance twin) [from disk], re-read with and without the corrective glance on the same held-out canvases. **The cost bar must be declared with it** — one extra glance is ~25 % more glance cost per canvas, and SOLUTIONS #228 (d) is the warning: a cost bar that forces a budget can silently turn an accuracy comparison into a convergence-speed comparison. If the gain is inside noise on drawn worlds, the honest verdict is "not gradable on this world", not a fail.

### 4.5 The cheap wide channel — a smell

```
SENSE    smell  kind size folder age; before any picture is opened
```
**Source:** the smell/taste pairing (a wide ambiguous distance survey deciding what the expensive committing contact sense is spent on) [secondary]; the octopus's peripheral filtering [secondary]; and his own words — "a prefiltration or novelty gate that only promotes what changed", "with a timestamp and a modality tag on every event" [from disk].
**The shape:** the folder door already scans `world/` every 30 s and picks one unseen picture in bytewise order. A smell channel reads what is knowable **before decoding**: suffix, byte size, folder name, mtime, sha prefix — and publishes it as its own tape row with `meta.source: "smell"`. It **decides nothing**; it is a channel the mind may use.
**The test that could refuse it — and this one is a real risk of a null:** measure whether the smell vector predicts anything the creature cares about *better than chance* — e.g. whether two pictures with the same folder word have closer smell vectors than two with different words. **If the AUC is ≈ 0.5, the channel is noise and is refused** (SOLUTIONS #217's law: a channel with no separation cannot be rescued by anything downstream). The second refusal: if arming it changes no journaled decision, it is a no-op (as §4.1).

### 4.6 The act's own texture — gated on HANDS

```
SENSE    touch  from hands: exit rate stalls retries bytes; slip-stick counts per act   # OFF until HANDS is on
```
**Source:** the rat whisker — the act and the sense are one loop, and texture lives in "the rate and magnitude of slip-stick events" rather than in a resonance code [secondary]; the platypus's two-signature ranging [secondary].
**The shape:** when HANDS is switched on, every program the creature runs returns an exit code, stdout, a duration and a byte count. Read as a **stream of discrete failures** — stalls, non-zero exits, retries — rather than as a result, that is a texture. It is delivered as a sense row, not as a return value the mind reads synchronously.
**The condition, and it is the important line here:** §4.2's forward model must exist first. Without it, the first program's output is indistinguishable from something the world did, and the creature's only learning signal from acting is uninterpretable.
**The test that could refuse it:** two programs that produce the *same* output by different roads (one clean, one stalling) must give different touch vectors; two runs of the same program must give the same one.

### 4.7 A mind-side proposal this organ research raised, named because the brief requires it

The fly's expansion is **FIXED wiring plus an ADAPTS gain** delivering a tag, and then **one plastic layer that LEARNS** — and that layer is the mind's under his rule. So the hash belongs in the mind document, not this one. It is named here because the organ research is what raises it, and because the disk carries a live contradiction worth settling: E15 refuted the expansion as a supervised feature learner (27.48 % vs ridge 53.42 %) and **nobody has tested it as a recall hash**, which is Dasgupta's actual claim (MNIST k=4: 44.8 % vs LSH 16.0 % on the paper's own metric) [from disk; fetched]. The creature's recall is a cosine over cells — precisely where the claim applies. The test that could refuse it is a one-file measurement on a closed life's snapshot: build the tag for every stored cell, and ask whether tag-overlap ranks the true nearest cell as well as the cosine does. **If it does not, the fly's algorithm is refused for this creature twice over and that is worth writing down.**

---

## 5 · What this document does not claim, and the three questions for Ahmad

### 5.1 Does not claim

1. **That any of it is needed.** Every proposal in §4 carries a refusal test, and three of them (4.1, 4.5, and the §4.7 note) have a realistic chance of a clean null. The task these organs were researched for is a creature that today passes ALIVE, REPLAY and nine of eleven marks without any of them.
2. **That the animal numbers transfer.** A mole's 26 ms touch and a fly's 40× expansion are facts about bodies made of cells with those costs. The only thing that transfers is the *shape* — a search unit of act-plus-look, a fixed random expansion with a gain control — and the shape has to be re-measured here.
3. **That the bins are settled.** Three calls in §1 are arguable and one of them (the mormyrid) I deliberately **split** rather than force into one bin. If Ahmad rules the other way on any of them, the organ changes shape, not just its label.
4. **That E21's 100 % says anything about the creature.** E21's own verdict says it first: a scripted forward model on a deterministic terminal, ceiling declared before the run, "says NOTHING about any organism". And for this creature the discrimination it measured is partly free anyway, because the tape carries provenance (§2.2). What is not free is content.
5. **That anything here was tested.** No code was written, nothing was run, nothing under `/data/dev/genome` was modified but this file.
6. **Coverage.** I found no research on: thermoreception and nociception (deliberately out of scope), the trigeminal chemesthesis channel, hygroreception, magnetoreception, and the human proprioceptive *body schema* literature beyond the spindle/GTO level. I could not read Kennedy & Sawtell 2014 in full (Nature redirected to an authorisation page) and its numbers above are **[secondary]**; I could not read the PNAS "two predators" paper (403); the Dasgupta PDF copies would not parse and its numbers come from the **bioRxiv full text**, which I did read. **Three of my own first-draft errors are corrected in place rather than silently:** the creature's gaze was described as a self-caused sensory consequence (it is a crop — §0.3.2); the AgRP paper was credited to "Betley et al." from recall (it is Chen, Lin, Kuo & Knight); and the lateral-line evoked-rate ratio was written as "0.1–0.9" from a summariser's output rather than the paper's own "approximately 50 %". Where a number in the task brief did not survive checking, the checked value is what is written above — the Pacinian peak is **30–500 Hz** within a 5–800 Hz band (not "250 Hz"), the mole's decision unit is **26 ms touch + 50 ms saccade** (not "~25 ms decisions"), and the VOR latency is **6–14 ms** (not "10 ms").

### 5.2 The three bin calls he may dispute, stated so he can overrule one line

| the mechanism | my call | why | what changes if he rules the other way |
|---|---|---|---|
| **The mormyrid's ELL** | **SPLIT**: the subtraction ADAPTS, the negative image LEARNS | a rule that reads an error and whose change persists is learning wherever it sits; but the subtraction itself runs every discharge with no error and nothing stored | if it is all ADAPTS, the organ gets a fixed subtraction and cannot follow a body that changes. If it is all LEARNS, the subtraction moves into the mind and pays the mind's latency on every sample |
| **VOR gain** | **LEARNS** | the canals and the 3-neuron arc never change; the multiplier is acquired over hours by cerebellar LTD from an error signal, and it persists | if he rules it ADAPTS, then "gain that changes from error and persists" is organ-level, and §4.2's efference copy could be built entirely inside the organ with no mind-side model at all — a much smaller build |
| **The fly's mushroom body** | expansion **FIXED**, APL **ADAPTS**, KC→MBON **LEARNS** (and therefore the mind's) | the anatomy agrees with his rule almost exactly: one plastic layer, everything upstream fixed wiring and a normaliser | if he wants the plastic layer at the organ, the organ starts learning and his 13:30 sentence is the thing being amended, not this document |

### 5.3 The three questions

1. **Does the creature's body get a sense of itself, and if so does it stop at readings?** The readings are unambiguous and free (§4.1). The line I will not cross without his word is the next one: a *drive* — a set point, a hunger, a tiredness that changes what he does. Biology puts the reading in the organ and the drive in the mind, and AgRP says the drive is itself predictive. **My recommendation: build the sense, leave the drive to the mind document, and let one life say whether the readings change a single decision** — if they change none, the drive question never has to be asked.
2. **Should the efference copy be a precondition on the first act — on HANDS, and on the web door?** My reading of the evidence says yes and says it fairly strongly: an organism that acts and cannot predict the consequence of its act cannot tell what it caused, and every one of his own reasoning layers (predict the checkable consequence, design the cheapest probe, update only on the verification outcome) assumes it can. **But it is his call, because it puts one more thing between today and the creature making something.** Two facts sharpen the question rather than answer it: the creature has **no act at all** today (§0.3.2), so nothing is being lost right now; and the web door is already *declared in the genome and implemented by nothing*, which is a separate thing worth his eye — a declared value the machinery does not run is the shape §14 of the creature's own record says must be settled before a life, not inside one.
3. **Is a sense organ allowed to be a thing the creature made?** The spider is the one animal that really does this, and it is the row I graded EARLY rather than TRUE-and-buildable. The creature is about to start making things. If reading its own output back as a *world* (through a sense thread, onto the tape, with its own provenance stamp) is something he wants, it changes what HANDS is for — from an act with an outcome into an act that builds the next sense. **I did not propose it in §4 because I do not think it should be built yet; I am asking whether it should be on the list at all.**
