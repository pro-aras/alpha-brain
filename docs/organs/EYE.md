# THE EYE — biology reverse-engineered, software added
*edit: Claude (Opus 5, organ researcher), 2026-09-21 14:16 +0400*

Written on the brief `docs/organs/BRIEF.md` (Ahmad's 2026-09-21 13:30 and 13:39 words). **Organs prefilter and deliver; the mind learns.** Every mechanism below carries one bin — **FIXED** (set at development, never changes in a life) · **ADAPTS** (changes at runtime without learning) · **LEARNS** (belongs to the mind; the organ delivers a trait). Proposals, never laws.

**Road tags on every claim.** `[fetched: URL]` full text read · `[abstract: URL]` abstract only · `[PMC: URL]` · `[secondary: URL]` · `[from disk: path]` · `[measured here]` a number I ran on this box in this session (the command is named) · `[unverified]`. No number is quoted from a summary or from memory without a road. Where two disk documents disagree, his paste wins and the resolution is stated (§0.4).

---

# 0 · ON DISK ALREADY

## 0.1 The documents read first, and what each already settled

| document | what it settled for the eye | what it left open |
|---|---|---|
| `/data/dev/alpha3/docs/proposals/research/ahmad-2026-09-19-AGI-QA.reportlab.py` **(Ahmad verbatim — highest authority)** | *"Photoreceptors transduce photons … that signal is already filtered inside the retina itself (retinal ganglion cells perform edge, contrast, and motion detection before the signal even leaves the eye)"*; *"the retina and cochlea only perform literal, low-level cleanup (contrast, edges, frequency decomposition); semantic invariance only emerges several layers deep … the invariance is learned, not designed in at the input stage"*; *"human eyes make rapid jumps (saccades) to bring one small region into high-resolution focus"*; *"the brain actively sends a prediction down to the organ, which reports back confirmation or error"*; store **traits, not bitmaps**; a **prefiltration / novelty gate** before the brain; the eyes need not be physical hardware | which channels; how WHERE and WHEN reach the mind; what the organ may adapt |
| `docs/G4-DESIGN.md` §1 rows 2a/2b/5c + §9 | row 2a EYE = the sealed tower + canvas + GAZE; row 2b TRAITS = a learned contrast head **over** the frozen tower; row 5c READ-EYE declared OFF | row 2b is the contradiction his 13:30 word settles (§0.4) |
| `…/alpha3-research/R2-VISION-TRAITS-COGNITION.md` §1.0–1.13 | the deepest eye file on disk: 39 primaries, every mechanism with a test, a twin and a pass mark. §1.0 lists what Alpha 2's eye lacked, verbatim, in seven numbered items | every test in it is still unrun except the ones E29/E51/G1/G2 took |
| `…/alpha3-research/RESEARCH-2026-09-16-HUMAN-MECHANISMS-FOR-THE-FAILING-ORGANS.md` §3.1, §4 | §3.1: *"the trunk stays shape-only and the context comes from the page"* — the label needs a CONTEXT input, not a bigger eye. §4: the six things software can do that a brain cannot | who supplies the context in a creature with no pages |
| `…/proposals/ALPHA-2-DEEP-RESEARCH-2026-09-06.md` §2.8 | the 12-row human-limit table; the eye's row is *"Single body, single sensor set → Eyes as PROFILES (Program V) … PARTLY"* | no per-species eye numbers |
| `…/proposals/alpha1-organism-capabilities-research-2026-08-24.md` | the 17-animal register, two-axis graded (Mapping × Grade) | **it has ZERO eye rows.** §1.6 below EXTENDS it in its own format; nothing in it is rebuilt |

## 0.2 The measured record — what has already been tried on this eye and what it read

| run | question | reading | verdict |
|---|---|---|---|
| `docs/G0-PREREG.md` amendment 1 + §11 finding | can a hand-built fixed front band ten drawn things at 24×24? | 22 fixed fronts measured; the declared fallback **3-orientation filter bank margin −0.19**; scale-normalised fronts tighten within-thing to 0.99 but make **circle = dot BY CONSTRUCTION** and are excluded (#228c); the chosen front `thresh0.25 centre blur0.8 pool3 hog8 hogcells8x6 unit`, 126 numbers, within-p5 0.540 / median 0.951, between-p95 0.827 | a fixed front CAN band drawn shapes |
| `docs/G0b-PREREG.md` §2b | the sealed glyph tower's raw bands at 32×32 on eleven things | raw 112 features: within p5 **0.541** / median **0.818**; between p95 **0.808** / max **0.967**; closest pairs circle/diamond **0.944**, circle/square **0.936** — **gate STOPPED**. Centring before the tower lifts within-median to **0.957**; a fixed square root after it to **0.968** (between p95 0.903). The tower's inner maps (448–960 numbers) do worse | the front in force today: `thresh0.25 centre tower:eye-tower-g2 sqrt unit` |
| G1 (`docs/G1-PREREG.md`, `runs/g1-*`) | does a surprise gaze find the thing? | **220/220** against random **26/220** | the gaze is the strongest single result on this eye |
| G1 §6 amendment 1 (the ink rule) | `\|g − mean(window)\|/max` made a FILLED shape's background as bright as its ink (a filled window's mean ≈ 0.5), so circle/square/diamond became one shape | replaced by `border`: `\|g − median(the window's 2-px rim)\|/max` | SOLUTIONS #231 (1) |
| `docs/G2-EYE-PREREG.md` + `runs/eye-photo-g1` | grow an eye ON photographs (Caltech-101, 92 held-out folders, 64×64, 3 convs, **768 features**, 18,928 trunk parameters) | **G-4 FAIL.** trained margin (within-median − between-p95) **−0.1109**; untrained twin of the same shape **−0.0416**; glyph tower **−0.0863**; raw pixels **−0.126**. The trained eye is **0.069 WORSE than its own untrained twin** | no fixed front, learned or not, bands photographs |
| `/data/dev/alpha3/experiments/E51-the-eyes-richer-channels/results/VERDICT.md` | do colour / position / motion channels carry? | **the channels carry perfectly**: A0 **1.000 / 0.997 / 1.000** against the grey twin's **0.500 exactly** — and the 0.500 is by construction (the two classes' 32×32 frames are byte-identical; only the side channel differs). The grey twin retrained at 3× the budget is **still exactly 0.500**. But **cost 5.110×** the grey tower against a 3× bar, and motion reads **−6.0 / −7.7 pp** outside the drift speeds it was trained on | **FAIL on conjunction; not adopted.** The finding stands: the information is real, this build of it is too dear |
| `/data/dev/alpha3/experiments/E29-developmental-encoding-eye-tower/VERDICT.md` | should a growth RULE encode the eye's shape? | grown tower **75.29 / 75.60** vs directly-searched **87.68 / 78.63**; the best of **48 random draws beat the evolved rule by 10.93 pp** | **FAIL.** The eye's shape is searched directly, never grown by a rule |
| `runs/g4-verdict-life2-20260921-1215/VERDICT.md` (the 24 h life, read 12:15 today) | how does the eye read inside a living creature? | **(x)** gaze **1.000** vs random **0.082** (×12.22) in the first 2 fixations. **(xi)** Q1 gaze **0.956**; one-glance twin **0.819**; **first-fixation-only 0.975**; random-gaze **0.363**. COST: live median **26.53 ms a canvas** | **the eye's marks all PASS** — and glances 2–4 cost 1.9 pp (§0.3 item 4) |
| `docs/atlas-sections/failures-and-theory.md` | the estate's failure classes | *"a FIXED feature front (the retina) under a learned trait space"* is the fix named for the growth/pruning class | — |
| `~/.ai-context/SOLUTIONS.md` #228 (b)(c), #231, #225, #227 | how an eye may be TESTED here | **(b)** compute a gate's CEILING under its own sampling rule before declaring its bar. **(c)** a control's blindness is derived from the ARCHITECTURE, not the rendering — the strongest form is inputs byte-identical between classes (E51 A1.2 did exactly this). #231: a mark's null is measured on the twin's OWN structure. #225: a loss on a nameable subset with a nameable twin is a LABEL fact, not a capacity fact | constraints on §4's tests |

## 0.3 The eye AS IT RUNS TODAY — read from the live files, 2026-09-21

The chain, per canvas, with the file and the measured cost. `[from disk]` for the code; `[measured here]` for every millisecond (timed in this session with `python3` on `/data/dev/genome`, read-only, single process).

| # | step | file | what it computes | cost |
|---|---|---|---|---|
| 1 | a picture becomes a canvas | `genome/gaze.py:canvas_of_picture` | longest side → 128, BOX, padded with the picture's own mean colour | not timed (PIL) |
| 2 | **the retina** | `/data/dev/alpha2/organs/retina.py` (sha-pinned, imported verbatim) | on a **16×16** cell grid, **8 channels**: `lum`, `rg` (R−G), `by` (B−(R+G)/2), `contrast` (centre minus the 8-neighbour mean), and four orientation energies `orient_h/v/d1/d2` (absolute first differences of luminance). Saliency = \|contrast\| + \|rg\| + \|by\| + the four orientation energies | **5.42 ms**, of which **4.77 ms (88 %)** is `cell_means`, a pure-Python loop over all 16,384 pixels |
| 3 | **the gaze** | `/data/dev/alpha2/organs/gaze.py` (sha-pinned) | fixation 1 = the saliency peak; then the most-surprising-unvisited cell, falling back to the most-salient-unvisited (inhibition of return by the `visited` set). `genome/gaze.py:fixations` passes **`predicted=None`** — hardcoded — so within the creature *surprise ≡ saliency* and nothing is ever subtracted | **0.116 ms** for 4 fixations |
| 4 | the glance window | `genome/gaze.py:glance_window` | a **32×32** window centred on each fixated cell, clamped inside the canvas, cut from `luminance(rgb)` — **the colour is discarded here** | — |
| 5 | the ink rule | `genome/gaze.py:ink_border` | \|g − median(the window's 2-px rim)\| / max — a per-window, stateless contrast normalisation | — |
| 6 | **the fixed front** | `genome/machinery.py:retina` + `genome/eye.py` | `thresh0.25 centre tower:eye-tower-g2 sqrt unit`. The tower: 32×32 → conv 8@5×5 → ReLU → 2×2 max → conv 7@3×3 → ReLU → **4×4 mean pool** → 4×4×7 = **112 features**, unit length. **719 trunk parameters** (W1 200, b1 8, W2 504, b2 7); the 108-class head (12,204 more, 12,923 total) is **discarded** — sha-refused if a byte differs | **0.457 ms a glance**; **1.83 ms** for 4 |
| 7 | what reaches the mind | `creature/mind.py:_consume_eye` | `self.org.moment(x, xw, lr_scale=…)` is handed **only the 112-vector `x`**. The fixation cells `g["fix"]`, the window origins, the instant `row["at"]` and the glance ORDER are written to the journal for a human and **never reach the organism** | — |
| | **the eye's share of a canvas** | | | **≈ 7.4 ms** of the life's measured **26.53 ms** median canvas — **28 %**, and 65 % of that is one Python pixel loop |

**Four facts about today's eye that the gap table turns on.**

1. **Eight channels are computed and seven are thrown away.** `rg`, `by` and the four orientation energies exist, cost part of the 5.42 ms, decide *where to look* — and then step 4 calls `luminance()` and the tower sees grey. Colour opponency and orientation energy never reach the mind in any form. E51 proved the information is real and separable (0.500 → 1.000); the creature computes it and drops it.

   **And two of the eight are identically zero anyway, by construction.** `genome/world.py:render_canvas` ends `rgb = np.repeat(u8[:, :, None], 3, axis=2)` — the maker's canvas is one grey plane replicated three times. Run on a real maker canvas: **max \|rg\| = 0.0 and max \|by\| = 0.0, exactly** `[measured here: genome.world.render_canvas("circle", …) → organs.retina.analyse]`. Life 2's folder door delivered **0 pictures** `[from disk: VERDICT.md, DOOR row]`, so **the creature has never seen a coloured pixel.** Any colour proposal placed on the maker's world is a plant placed where the mechanism cannot fire (#228 a); colour becomes a real question only when the folder door carries his photographs, which `G4.genome` armed at 13:14 today for life 3.
2. **Nothing in the eye adapts.** `predicted=None` (step 3) means the mind's prediction never reaches the organ; `SURPRISE` is declared `#OFF` in `genome/G4.genome` with the reason *"no sense on the maker/folder streams needs it yet"*; the ink rule is per-window and stateless. The organ subtracts nothing, ever. His AGI-QA line — *"the brain actively sends a prediction down to the organ"* — has no implementation.
3. **WHERE, WHEN and the ACT do not exist for the mind.** This is precisely the hole his 13:30 sentence names: *«the mind is where those traits and geometric time space combined»*. The traits arrive; the geometry and the time do not. `FAST` carries the moment counter `t_at_f0` but no position; `SLOW` carries neither.
4. **Four glances are four unrelated moments wired to one word.** `for x in g["feats"]: self.org.moment(x, xw, …)` — nothing binds a canvas's glances into one thing. The life's own twins price it: **first-fixation-only 0.975 > 4-fixation gaze 0.956 > one-glance 0.819 > random-gaze 0.363**. Glances 2–4 *cost* 1.9 pp today. The gaze is right (it finds the thing, ×12.22); what is missing is the machinery to use more than one look. `[from disk: runs/g4-verdict-life2-20260921-1215/VERDICT.md]`

## 0.4 The one contradiction, resolved HIS way

`G4-DESIGN.md` §1 row 2b puts **TRAITS** — a 32-wide contrast head learned by InfoNCE at sleep — inside the EYE. His **13:30** word removes it: *«that trait system is for mind, not the eyes or ears, or any organs … no learning at organ level»*. The record agrees with him: `G4.genome` carries TRAITS as `#OFF` with the measured reason — *"InfoNCE over canvas instances learns instance identity after 5 sleeps (margin −0.116 < raw 0.009)"* — and W3-4's learned eye head was dropped on 2026-09-21 13:30. **Resolved his way, and no primary evidence contradicts it.** This document treats every learned front as a proposal about the MIND, and asks of each biological learning mechanism: *what trait must the fixed eye deliver so the mind can learn what the biology learned in the organ?* The mind-side home already exists — the SLOW area's BIRTH / HEBB / DELTA / PRUNE / MERGE over the fixed traits is where V1's learning lands under his rule.

---

# 1 · BIOLOGY — how the eye works

## 1.1 The chain, photon to optic nerve, each step binned

| # | stage | what it does, with the number | bin | why that bin |
|---|---|---|---|---|
| 1 | **photoreceptors** | ~**4.6 million cones** and ~**92 million rods** in a human retina; peak foveal cone density **199,000 /mm²** (range 100,000–324,000 between individuals); density falls an order of magnitude 1 mm from the foveal centre; the rod-free zone is **1.25°** across `[abstract: https://europepmc.org/abstract/MED/2324310 — Curcio et al., J Comp Neurol 292:497, 1990]` | **FIXED** | the mosaic is built in development and does not change in a life |
| 2 | **the outer plexiform layer** — horizontal cells | a lateral feedback that subtracts a neighbourhood average from each cone: the physical origin of centre–surround `[fetched: Hosoya et al. 2005 §intro — "neural circuits in the retina predict the local intensity from values at nearby points in space and preceding points in time, and subtract this predicted value from the actual intensity"]` | **FIXED** (its gain ADAPTS, row 8) | the wiring is genomic; only the weight moves |
| 3 | **bipolar cells** | split the signal into ON and OFF at the first synapse; ~15 types in mouse | **FIXED** | |
| 4 | **amacrine cells** | ~40+ inhibitory types; build direction selectivity, the surround, and the plastic term of row 10 | **FIXED** wiring, **ADAPTS** weights | Hosoya's model (row 10) makes exactly these synapses plastic |
| 5 | **retinal ganglion cells — the output channels** | §1.2 | **FIXED** | |
| 6 | **the optic nerve** | ~1 M fibres from ~100 M receptors — a **~100:1 compression** performed before anything leaves the eye `[unverified — the ratio is standard; I did not fetch a primary for it, and it is used only as an order of magnitude]` | **FIXED** | |

**The sentence this chain settles, and it is Ahmad's own:** the retina is a *literal low-level* prefilter — contrast, edges, motion — and *"'Knowledge' isn't located in the eye at all"* `[from disk: ahmad-2026-09-19-AGI-QA.reportlab.py §2]`. Everything below is a refinement of that sentence, never a contradiction of it.

## 1.2 The parallel channels — the part the creature has no analogue of

A retina is not one filter. It is **tens of filters run in parallel on the same photons**, each with its own spatial scale, its own time constant and its own axon.

| finding | what it says | the number | road |
|---|---|---|---|
| **The frog** — the first measurement of the idea | *"There are four separate operations on the image in the frog's eye. Each has its result transmitted by a particular group of fibers, uniformly distributed across the retina, and they are all nearly independent of the general illumination. The operations are: 1) sustained contrast detection; 2) net convexity detection; 3) moving edge detection; and 4) net dimming detection."* Receptive fields range **~2° for operation 1 to ~15° for operation 4** (the scan's OCR drops the degree signs: *"about 2° diameter for the first operation, to about 15° for the last"*). Operation 2 is the "bug detector": *"responds best when a dark object, smaller than a receptive field, enters that field, stops, and moves about intermittently thereafter. The response is not affected if the lighting changes or if the background (say a picture of grass and flowers) is moving"* | 4 operations, 5 fibre types | `[fetched: https://hearingbrain.org/docs/letvin_ieee_1959.pdf — Lettvin, Maturana, McCulloch & Pitts, Proc. IRE 47:1940, 1959]` |
| **The mouse** — the modern census | *"In the mouse, anatomical estimates range from 15 to 20 channels, and only a handful are functionally understood. By combining two-photon calcium imaging … and unsupervised clustering of the resulting sample of more than 11,000 cells, here we show that the mouse retina harbours substantially more than 30 functional output channels."* The framework yielded **46 groups (n = 7,982 cells, 71.2 %)**, split into **32 RGC groups** and 14 displaced-amacrine groups. The 32: non-direction-selective (**9 OFF, 12 ON, 3 ON–OFF**) and direction-selective (**2 ON–OFF, 4 ON, 2 OFF**), plus *suppressed-by-contrast* cells (G31, G32). Average coverage factor **2.0 ± 0.7**. The paper's own closing analogy: *"suggesting an encoding strategy resembling that used in state-of-the-art artificial vision systems"* | **≥ 32** | `[fetched: https://www.cns.nyu.edu/~tony/vns/readings/baden-etal-2016.pdf — Baden et al., Nature 529:345, 2016]` |
| **The primate** | macaque: **18 peripheral and 16 foveal** ganglion-cell clusters from 165,000 single cells | 16–18 | `[secondary: https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2021.661938/full — reporting Peng et al., Cell 176:1222, 2019]` |
| **The non-image channel** | melanopsin ipRGCs: *"melanopsin is most likely the visual pigment of phototransducing RGCs that set the circadian clock and initiate other non-image-forming visual functions"*; **five to six morphological types (M1–M6)**; M2–M5 have centre–surround receptive fields and all types *"responded robustly to a wide range of motion speeds, and M1–M4 cells appeared tuned to different speeds"*. In Baden's sample, ipRGCs were **18 of 905 cells** | ~2 % of RGCs | `[PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC2885915/ — Hattar et al., Science 295:1065, 2002]` · `[abstract: https://europepmc.org/abstract/MED/24396062 — Zhao et al., J Physiol 592:1619, 2014]` · `[fetched: Baden 2016]` |

**Bin: FIXED.** Every one of these types is specified by development; a mouse does not grow a new RGC class from experience. **What each channel delivers is a NUMBER per channel** (an ON/OFF sign, a temporal bandwidth, a receptive-field diameter, a latency) — which is exactly the shape of a trait under his rule: *a channel value with its where and when*.

**The transferable law, stated so §4 can use it:** the biological prefilter is **wide and shallow** — ~32 cheap, differently-tuned filters over the same input — where the creature's is **narrow and deep**: one 719-parameter two-layer tower producing 112 numbers that are all the same kind of number. The 8-channel Alpha 2 retina (step 2 of §0.3) is *already* the wide-and-shallow shape; it just does not reach the mind.

## 1.3 ADAPTS — what a retina changes at runtime, without learning anything

| mechanism | the measurement | bin | the discriminator I applied |
|---|---|---|---|
| **light adaptation** | *"Even highlights and shadows within a single visual scene can differ approximately 10,000-fold in intensity — exceeding the range of distinct neural signals by a factor of approximately 100."* Two mechanisms adjust sensitivity *"in the approximately 200 ms intervals between saccades"*: cone receptor adaptation and a post-receptor site between cone bipolar and ganglion cells, and *"the two adaptive mechanisms are essentially mutually exclusive: as light levels increase the main site of adaptation switches from the circuitry to the cones"* `[abstract: https://europepmc.org/abstract/MED/17851533 — Dunn, Lankheet & Rieke, Nature 449:603, 2007]` | **ADAPTS** | it is a gain, it is reversible, and it is timed to the saccade interval — no memory of any particular scene survives it |
| **multiple concurrent gain controls** | *"Adaptational mechanisms must balance the competing demands of adapting quickly, locally, and reliably … Multiple adaptational mechanisms in different locations within the retina act in concert, with lighting conditions dictating which mechanisms dominate"* `[abstract: https://europepmc.org/abstract/MED/20005818 — Rieke & Rudd, Neuron 64:605, 2009]` | **ADAPTS** | |
| **dynamic predictive coding in the retina** — the hard case | The spatio-temporal receptive fields *"change after a few seconds in a new environment. The changes are adaptive, in that the new receptive field improves predictive coding under the new image statistics."* Measured: after adaptation to a checkerboard, a cell's sensitivity to checkerboard stimuli falls by **×0.57** while its sensitivity to the novel uniform stimulus rises **×1.4**, and *"The reverse changes occurred during adaptation to environment A"*. **About half** the ganglion cells have an adaptation index significantly > 1; **a ≥ 2 is not uncommon**; the same holds in salamander and rabbit. Time course: *"The adaptation index adjusted with a time constant of several seconds"*, against a light response *"at least tenfold faster"*. It fires on orientation alone, with *"all image statistics identical except for the difference in orientation"*. The mechanism proposed is an **anti-Hebbian** plastic inhibitory synapse: *"when signals in the presynaptic and postsynaptic neurons are correlated, the synapse becomes stronger; if the two neurons are anticorrelated, the synapse becomes weaker. Note that this is an anti-hebbian rule"* `[fetched: https://meisterlab.caltech.edu/documents/8137/hosoya_2005_dynamic.pdf — Hosoya, Baccus & Meister, Nature 436:71, 2005]` | **ADAPTS** — decided, not assumed, and **disputable** | **The discriminator: does it REVERT when the statistic goes away, or accumulate over the life?** The protocol interleaves A and B for 13.5 s each and the receptive field follows both ways, with a several-second time constant and nothing measured past 10 s. **The bin rests on that ratio: a memory of ≤ 10 s inside a 24 h life stores nothing about any thing he saw.** That is where I drew the line between ADAPTS and LEARNS, and Ahmad may draw it elsewhere — because *the paper's own mechanism is a synaptic plasticity rule* (anti-Hebbian). "Not learning" here means "keeps no lasting content", not "no synapse moved". |
| **saccadic suppression** | visual sensitivity and cortical firing drop around a saccade; in V4 *"neurons in the input layer show changes in firing rate and inter-neuronal correlations **prior to** saccade onset"* — i.e. the suppression is driven by a copy of the motor command, not by the image `[abstract: https://europepmc.org/abstract/MED/37392385 — Zanos et al., Cell Reports 42:112720, 2023]` | **ADAPTS** | the organ is told what the body did and discounts the consequence |
| **corollary discharge / efference copy** | *"The major hypothesis is that a corollary discharge (CD) or efference copy signal provides information that the eye has moved, and this information is used to compensate for the motion"* `[PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC2556215/ — Wurtz, Vision Research 48:2070, 2008]` | **ADAPTS** | |
| **predictive remapping** | *"For some parietal neurons, the location of the receptive field is shown to shift transiently **before** an eye movement. In addition, nearly all parietal neurons respond when an eye movement brings the site of a previously flashed stimulus into the receptive field. Parietal cortex both anticipates the retinal consequences of eye movements and updates the retinal coordinates of remembered stimuli to generate a continuously accurate representation of visual space."* `[abstract: https://europepmc.org/abstract/MED/1553535 — Duhamel, Colby & Goldberg, Science 255:90, 1992]` | **ADAPTS in the organ's address space; the STABLE MAP is the mind's** | this is the mechanism that turns *retinotopic* (where on the retina) into *craniotopic* (where in the world). It needs exactly one input the creature does not deliver: the eye's own position |
| **microsaccades** | miniature movements during fixation contributing to *"the control of fixation position, the reduction of perceptual fading and the continuity of perception, the generation of synchronized visual transients, visual acuity, scanning of small spatial regions, shifts of spatial attention"* `[abstract: https://europepmc.org/abstract/MED/19683016 — Rolfs, Vision Research 49:2415, 2009]` | **ADAPTS** | they refresh a stalled sensor; they store nothing |
| **the pupil** | a fast mechanical gain stage, partly driven by the ipRGCs of §1.2 | **ADAPTS** | |

**The one sentence §3 needs:** every ADAPTS mechanism above is a **gain or an offset that reverts**, and three of them (suppression, corollary discharge, remapping) run on **a copy of the body's own act**, not on the image. A creature whose eye never learns what the body just did cannot have any of the three.

## 1.4 LEARNS — where the biology puts learning, and where his rule puts it instead

| mechanism | the measurement | biology's bin | **the mind-side equivalent under his rule** |
|---|---|---|---|
| **V1 orientation columns** | *"Cortical maps for orientation and ocular dominance in the primary visual cortex of cats were found to be present by 2 weeks. Early pattern vision appeared unimportant because these cortical maps developed identically until nearly 3 weeks of age, whether or not the eyes were open … **The basic structure of cortical maps is therefore innate, but experience is essential for specific features of these maps, as well as for maintaining the responsiveness and selectivity of cortical neurons.**"* `[PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC2453000/ — Crair, Gillespie & Stryker, Science 279:566, 1998]` | **FIXED at birth, LEARNS only at the margin — and it is CORTEX, not retina** | this is the strongest biological support for his rule that exists. The oriented front is genomic; experience tunes and *maintains* it. → the creature's fixed front is right in kind; what experience must shape is the SLOW area above it |
| **retinal waves** | *"waves of spontaneous retinal activity are present and propagate throughout the entire visual system **before eye opening** … Retinal waves were the primary source of activity in the midbrain and primary visual cortex"* `[PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3962269/ — Ackman, Burbridge & Crair, Nature 490:219, 2012]` | **FIXED** (a genomic self-test that wires the map before any world exists) | a startup self-check of the eye→mind path before the first canvas — an ALIVE-style proof, not a learning road |
| **a task-emergent fovea** | a learned sampling lattice *"resembles the eccentricity dependent sampling lattice of the primate retina, with a high resolution region in the fovea surrounded by a low resolution periphery"* `[from disk: R2 §1.1, Cheung, Weiss & Olshausen, ICLR 2017, arXiv:1611.09430]` | **LEARNS**, in the literature | **refused at the organ under his rule.** The layout is FIXED by the genome; if a better layout exists it is found by a search over genomes between lives (E29's road — and E29 says the direct search wins), never inside one |
| **the learned front of every deep vision model** | the whole of CLIP / I-JEPA / the `TRAITS` head | **LEARNS** | **refused at the organ** (his 13:30; §0.4). Measured here twice: the TRAITS head made the margin **−0.116 against a raw 0.009**, and the photograph tower was **0.069 worse than its own untrained twin**. The mind-side equivalent is the SLOW area: fixed traits in, cells born on novelty, edges grown by HEBB/DELTA, pruned when wrong — learning *over* the front, not *in* it |
| **retinal predictive-coding plasticity** (§1.3) | anti-Hebbian, reverts in seconds | **ADAPTS, not LEARNS** — decided by the reversion test | if it were ever given a longer time constant it would become learning, and under his rule it would belong in the mind |

## 1.5 Gaze — an ACT, not a filter

| mechanism | number / verbatim | bin |
|---|---|---|
| **why a saccade exists at all** | the fovea is a ~1°-wide patch of the 199,000 /mm² mosaic (§1.1); everything else is periphery. His own sentence: *"human eyes make rapid jumps (saccades) to bring one small region into high-resolution focus at a time"* `[from disk: AGI-QA §2]` | **FIXED** (the mechanism); **the choice is the mind's** |
| **the priority map** | the superior colliculus holds topographic maps whose *"organization … is thought to underlie attentional priority by assessing which regions of the visual field contain behaviorally relevant information"*; measured in rat slices, the circuit *"is hard-wired to give higher priority to more peripheral targets"* through a rostrally-directed inhibitory circuit `[PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC4512250/ — Phongphanphanee et al., J Neurophysiol 114:1310, 2015]` | **FIXED bias + a map the mind writes into** |
| **a saccade is an experiment** | *"saccadic eye movements are optimal experiments, in which data are gathered to test hypotheses"*; *"salience is the precision of counterfactual beliefs that depend on where or how sensory data are sampled"*; and the line that matters for our own design — *"There is no principled reason why we should include inhibition of return"* | **the POLICY is the mind's**; the map is the organ's `[from disk: R2 §1.3, Friston et al. 2012, PMC3361132]` |
| **fixation durations** | ~200–300 ms in reading, longer and more variable in scene viewing `[secondary: https://europepmc.org/abstract/MED/9849112 — Rayner, Psychol Bull 124:372, 1998 — the review is the road; I read its abstract, not the body, and the two numbers are the field's standard figures]` | **ADAPTS** (duration is set by how hard the current fixation is) |
| **inhibition of return** | in the creature it is the `visited` set in `organs/gaze.py` | **FIXED**, and R2 §1.3 already specifies the OFF/ON control that would decide whether it earns its place |
| **two foveae** | many raptors carry a deep central and a shallow temporal fovea; behavioural acuity of the wedge-tailed eagle is **132–143 cycles/degree**, with the deep fovea's anatomical resolving power computed at **140 c/deg**, against the eye's diffraction ceiling of 157 c/deg `[abstract: https://europepmc.org/abstract/MED/4090282 — Reymond, Vision Research 25:1477, 1985]`. A generalist raptor (chimango caracara) reads only **15–40 c/deg** `[abstract: https://europepmc.org/abstract/MED/26821187 — Potier et al., Physiol Behav 157:125, 2016]` — *acuity is a diet, not a taxon* | **FIXED** |

## 1.6 The best parts, by species — **an EXTENSION of the 17-animal register**

`alpha1-organism-capabilities-research-2026-08-24.md` has 17 rows and **no eye row**. These are new rows in that file's own two-axis format — **Mapping** (HAVE / PARTIAL / MISSING-and-buildable / N-A) × **Grade** (TRUE / OVERSTATED / EARLY / N-A) — against the creature as it runs today (§0.3). Nothing in the original register is rebuilt or restated.

| # | animal | the mechanism, with its number | algorithmic content | mapping | grade |
|---|---|---|---|---|---|
| **18** | **Mantis shrimp** (stomatopod) | **12 photoreceptor types, each a narrow band from 300 to 720 nm.** And the famous correction: *"Behavioral wavelength discrimination tests (Δλ functions) in stomatopods revealed a surprisingly poor performance, ruling out color vision that makes use of the conventional color-opponent coding system. Instead, our experiments suggest that stomatopods use a previously unknown color vision system based on **temporal signaling combined with scanning eye movements**, enabling a type of color **recognition rather than discrimination**"* `[abstract: https://europepmc.org/abstract/MED/24458639 — Thoen, How, Chiou & Marshall, Science 343:411, 2014]` | many narrow channels read **in time by a scan**, never compared against one another in the organ. The comparison, if any, happens downstream | **MISSING-and-buildable** — and it is the single closest animal to his rule: the organ scans and reports per-channel; nothing is combined in the eye | **TRUE** (the 12 channels and the poor Δλ are both measured; the scanning account is the authors' inference from them) |
| **19** | **Wedge-tailed eagle** | **132–143 c/deg** behavioural, **140 c/deg** anatomical in the deep fovea `[abstract: MED/4090282]`; a generalist raptor **15–40 c/deg** `[abstract: MED/26821187]` | resolution concentrated in a tiny patch, spent by an active gaze | **PARTIAL** — the creature has a fovea (a 32×32 window) and a gaze, but only ONE resolution and no periphery | **TRUE** |
| **20** | **Frog** | four operations, fields **2°–15°**, the convexity/"bug" detector independent of illumination and of a moving background `[fetched: Lettvin 1959]` | the prefilter is a **small set of purpose-built, illumination-invariant detectors**, not a general feature bank | **MISSING-and-buildable** | **TRUE** |
| **21** | **Mouse / primate retina** | **≥ 32** functional output channels in mouse from >11,000 cells (anatomy had said 15–20); 16–18 in macaque `[fetched: Baden 2016]` `[secondary: Frontiers 2021 / Peng 2019]` | wide-and-shallow parallelism at the sensor | **PARTIAL** — Alpha 2's retina computes 8 channels and delivers 1 | **TRUE** |
| **22** | **Jumping spider** (*Portia*, *Salticidae*) | depth from **monocular defocus** across four stacked retinal layers, with the red-light behavioural control `[from disk: R2 §1.7, Nolte et al. 2017, PMC6477618]`; and a **scanning** principal retina that moves behind a fixed lens — in *Portia*, *"at the beginning of the scanning routine, the spiders scanned both the complete and the incomplete route but … by the end … they predominantly scanned only the complete route"* `[abstract: https://europepmc.org/abstract/MED/10458876 — Tarsitano & Jackson, Anim Behav 58:255, 1999]` | (a) a second channel from a **known physical transform of the same image**; (b) the scan is the *search*, and its end state is the decision | **MISSING-and-buildable**; (b) is close to what the creature's gaze already does and could be read the same way | **TRUE** |
| **23** | **Cephalopods** (octopus, squid, cuttlefish) | a **single** unfiltered photoreceptor type, yet chromatic behaviour. Proposed and modelled: *"An off-axis pupil and the principle of chromatic aberration … can combine to provide 'color-blind' animals with a way to distinguish colors"* — spectral information recovered from **how blurred** the image is, at the cost of an inherent range/colour ambiguity `[PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC4961147/ — Stubbs & Stubbs, PNAS 113:8206, 2016]` | **a second channel for free from one sensor, by exploiting a transform whose parameters are known** — the same shape as the spider's defocus depth | **MISSING-and-buildable** | **EARLY** — the paper is a computational model consistent with the behaviour, not a recording |
| **24** | **Pit viper** | *"TRPA1 orthologues from pit-bearing snakes (vipers, pythons and boas) are the most heat-sensitive vertebrate ion channels thus far identified"*; the pit detects infrared *"through a mechanism involving radiant heating of the pit organ, rather than photochemical transduction"* `[PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC2855400/ — Gracheva et al., Nature 464:1006, 2010]` | a **second imaging modality on a different physics**, fused with vision downstream | **N-A for a creature whose world is rendered canvases** — there is no heat in it. Kept as the precedent for §2(b): a channel outside the animal's band is a normal thing for an organ to have | **TRUE** |
| **25** | **Chameleon** | *"highly independent, large-amplitude eye movements"*, full optic-nerve decussation and sparse inter-hemispheric commissures — and even so, group-level lateralisation of which eye is used `[abstract: https://europepmc.org/abstract/MED/23994262 — Lustig et al., Behav Processes 100:110, 2013]` | **two gazes at once**, over one mind | **MISSING-and-buildable and nearly free** — `BODY service creature threads eye ear door mind voice` already gives each sense its own thread | **TRUE** |
| **26** | **Four-eyed fish** (*Anableps anableps*) | one eye split into an aerial and an aquatic half with **different opsins in each half**: `lws` only dorsally, `rh2-1` largely ventral `[PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3259961/ — Owens et al., Biol Lett 8:86, 2012]` | **one organ, two differently-tuned regions for two different worlds, reported separately** | **MISSING-and-buildable** — his world already has two streams (the maker's drawn canvases and his own folder photographs) whose statistics are measurably different, and one front serves both | **TRUE** |
| **27** | **Blowfly** | the spatial tuning of the motion-vision system *"maximizes the open-loop Hankel singular values … jointly optimizing observability and controllability"*, i.e. the sensor is tuned to the body's own dynamics rather than to a general estimate of the world `[abstract: https://europepmc.org/abstract/MED/41811979 — Science Robotics, 2026]` | **the prefilter is matched to the ACT it serves**, not to the scene | **MISSING** and, honestly, not yet meaningful — the creature's only act on the world is where to look | **EARLY** |

---

# 2 · SOFTWARE / MACHINE — what we add

Costs are **measured on this box in this session** (a 16-core CPU, no GPU, single process, numpy) against the life's own budget: **26.53 ms median a canvas, live, with every thread running** `[from disk: runs/g4-verdict-life2-20260921-1215/VERDICT.md, mark (viii)]`. *(The same row prints a solo probe of 46.32 ms — i.e. slower than live, which the verdict does not explain and I do not; nothing here rests on it, and every cost below is compared against the live 26.53.)* Today's whole eye is **≈ 7.4 ms** of that (§0.3).

## 2 (a) · What MIMICS biology in code

| the biology | the code that mimics it | status here | cost on this box |
|---|---|---|---|
| centre–surround (§1.1 row 2) | a difference-of-Gaussians kernel; a 3-level DoG pyramid pooled to 8×8 = 192 numbers | Alpha 2's `contrast` channel is a 1-cell-radius DoG already, at 16×16 | **0.365 ms a canvas** `[measured here: scipy.ndimage, 200 reps]` |
| orientation energy / simple cells (§1.4 V1) | a steerable/Gabor bank; 4 orientations × 2 scales pooled to 8×8 = 512 numbers | Alpha 2 computes 4 orientation energies at 16×16 and drops them; `hog8`/`hogcells8x6` are in the RETINA grammar and were the G0 front | **0.883 ms a canvas** `[measured here]` — and G0 measured a 3-orientation bank's **margin at −0.19** on drawn shapes, so this is a *cheap* proposal, not a *promising* one |
| the ON/OFF split | a signed rectification: keep `max(d,0)` and `max(−d,0)` as two planes | absent (the ink rule takes \|·\|, collapsing them) | ≈ free |
| colour opponency (§1.2) | `rg = R−G`, `by = B−(R+G)/2` | **computed at 16×16 and discarded at `luminance()`** | already paid |
| the ≥32 parallel channels (§1.2) | run the same cheap front over several transformed planes | the creature runs ONE plane through ONE tower | 3 colour planes through the grey tower: **≈ 0.94 ms a glance** upper bound `[measured here]` |
| the saccade (§1.5) | a priority map + argmax + a visited set | **present and it is the eye's best result** (220/220; ×12.22) | **0.116 ms** for 4 fixations `[measured here]` |
| depth from defocus (spider, row 22) | two blur levels of one frame, the ratio of local high-frequency energy | absent; R2 §1.7 has the test and the red-light control written | ≈ 2× a blur ≈ 0.1 ms |
| predictive coding (Rao & Ballard) | feedback carries the prediction, feedforward the residual | `organs/gaze.py` accepts a `predicted=` map and `genome/gaze.py` **hardcodes it to `None`** | ≈ free |

## 2 (b) · What biology CANNOT do and this machine can

| affordance | the number | what it buys the eye | cost here |
|---|---|---|---|
| **event sensing** — a retina in silicon | a DVS pixel: **120 dB dynamic range, 15 µs latency**, asynchronous address-events, at 128×128 `[secondary: https://publications.ait.ac.at/en/publications/a-128x128-120db-15%C2%B5s-latency-asynchronous-temporal-contrast-visio/ — Lichtsteiner, Posch & Delbruck, IEEE JSSC 43:566, 2008]`; the survey figure the estate already carries is **140 dB vs 60 dB** `[from disk: R2 §1.5, Gallego et al., TPAMI 2020]` | a change sense with no hardware: a per-pixel log-intensity threshold over any frame source | **0.235 ms** for a 128×128 canvas `[measured here]` — and useless until something in his world MOVES (§4, G-EYE-5) |
| **channels outside any animal's band** | his own word: *"A microphone and ADC are not limited to the 20 Hz–20 kHz range of human hearing"* `[from disk: AGI-QA §1]`; the eye's analogue is a renderer that can emit IR/UV/polarisation/depth planes. **E51 built exactly this and measured it**: A0 with 8 channels reads **1.000** where the grey twin reads **0.500 exactly, by construction, at any budget** `[from disk: E51 VERDICT]` | information a human eye provably cannot have | E51's build cost **5.11×** — the reason it was not adopted. §4 costs a cheaper carrier |
| **exact replay of every glance** | the life-2 tape replays **18,959 mind rows byte-identical, with a planted divergence at seq 602 CAUGHT** `[from disk: VERDICT.md]` | any eye change can be judged on the SAME stream the old eye saw — the built-in control of #233 | ≈ free; the road exists |
| **the same picture to two twins** | the six blinds already run as replays (`--blind gaze` reads 0.363 against 0.956) | a twin blind to exactly one channel, everything else intact (#228 addendum) | ≈ free |
| **provenance on every trait** | nothing in a retina carries its receipts | each delivered number can name its channel, its window and its instant, so the mind can ask *why* | ≈ free |
| **parallel senses on 16 cores** | `BODY service creature threads eye ear door mind voice`; the chameleon row (25) is free here | two gazes, or an eye and an event layer, at once | GIL-bounded; numpy releases it |
| **an eye that never sleeps and never ages** | 23.999 h on tape, **sense restarts 0**, max eye gap **5.2 s** `[from disk: VERDICT.md]` | — | — |
| **a pretrained organ where no growth road can reach** | `judge/eye-tower-g2`: 719 trunk parameters, **112 features**, sha-refused if one byte differs `[measured here: genome.eye.tower('eye-tower-g2')]` | a front nobody on this box could grow in a life | 0.315 ms a frame |

**The honest boundary, stated once.** Rows 1 and 2 of this table are real and measured, and **both were refused on cost**, not on doubt. The design question for the eye is therefore never *"can we add a channel?"* — E51 settled that — but *"what does a channel cost against 26.53 ms, and does the MIND have any road that consumes it?"* A channel the mind cannot consume is #180's class: a value computed and never used.

---

# 3 · BENEFITS AND GAPS — against the creature as it runs today

"Today" = §0.3, `G4.genome`, and the 12:15 life-2 verdict.

| # | gap in the creature today | filled by BIOLOGY (which mechanism) | filled by SOFTWARE / MACHINE (which feature) | still open |
|---|---|---|---|---|
| 1 | **WHERE is journaled and never delivered.** `org.moment(x, xw)` receives only the 112-vector; `g["fix"]`, the window origin and the glance order stop at the journal | **predictive remapping** (§1.3, Duhamel 1992): the organ reports in retinal coordinates *and* the eye's own position, and the map is built above | the fixation cell is already computed — delivering it is a field on the tape row, not a computation | **whether the mind's SLOW area can use a position at all.** It compares cosines; a position must arrive BESIDE the vector, never inside it (§4 G-EYE-1) |
| 2 | **WHEN is delivered only as a counter.** `FAST` carries `moment=t_at_f0`; `SLOW` carries nothing temporal; there is no duration, no order-within-canvas | fixation duration is itself a signal (§1.5); ipRGCs are tuned to different **speeds** (§1.2) | the tape already stamps every row with a real instant (`row["at"]`) — `B8: the tape is the world's clock` | what a mind with no motion in its world would do with a duration |
| 3 | **The ACT is invisible.** The eye chooses 4 fixations and never tells the mind it moved | **corollary discharge / saccadic suppression** (§1.3): the organ is told what the body did, before it happens | a fixation is an act the creature performed; naming it on the tape costs nothing | this is the seam where CURIOSITY could eventually choose a look (§5 Q2) |
| 4 | **Four glances are four unrelated moments.** first-fixation-only **0.975** beats 4-fixation **0.956** | one object, several fixations, ONE percept — this is what remapping and transsaccadic memory are FOR (§1.3) | the glances of one canvas share a canvas id on the tape already | **the binding rule itself.** Gaps 1–3 are inputs; this is a mechanism, and it is the mind's |
| 5 | **Seven of eight computed channels are thrown away** (`rg`, `by`, 4 orientations) — and on the maker's world **`rg` and `by` are exactly 0.0**, because the canvas is one grey plane repeated three times | **≥32 parallel output channels** (§1.2); the frog's four operations | E51: the information is real and a grey eye is at **exactly 0.500** on it, at any budget | **the world, before the cost.** Colour cannot be tested on canvases that have none; the four orientation energies, however, are non-zero today and still discarded — that half of the gap is live now |
| 6 | **Nothing in the eye adapts.** `predicted=None`; `SURPRISE` OFF; the ink rule is stateless per window | **light adaptation** across a 10,000-fold within-scene range, re-set in the ~200 ms between saccades; **dynamic predictive coding** reverting with a several-second constant (§1.3) | `organs/gaze.py` already takes a `predicted=` map — one argument, sha-pinned and unchanged | what the mind should predict. The mind's PREDICT lives in **112-feature space**; saliency lives in **16×16 cell space**. They do not meet, and nothing on disk says which should move |
| 7 | **No fixed front bands photographs** — trained −0.111, untrained −0.042, glyph −0.086, raw pixels −0.126 | **the retina cannot do this either.** His own correction: *"semantic invariance only emerges several layers deep … it is a product of training"* | HUMAN-MECHANISMS §3.1: the fix is a **CONTEXT input at the label stage**, not a better eye | who supplies the context. In a creature with no "page", the honest candidate is the **folder name** — which is the word, i.e. the answer, so it cannot be an input to reading it (§5 Q3) |
| 8 | **One resolution, no periphery.** The glance is 32×32 at one scale; the canvas is 128×128 | the fovea/periphery gradient (§1.1: an order of magnitude per mm); raptors carry **two** foveae (§1.5) | a second tower pass over the whole canvas at 32×32 is **+0.457 ms**; the one-glance twin already reads 0.819, so the coarse view alone carries most of the answer | whether a coarse-plus-fine pair helps or just doubles the cost |
| 9 | **The eye costs 7.4 ms of 26.53, and 4.77 ms of that is a Python loop over 16,384 pixels** | — | the whole 8-channel analysis, vectorised in numpy, reads **0.462 ms against 5.42 ms — 11.7×**, returning **≈ 4.3 ms a canvas, 16 % of the life's budget** `[measured here]` | the pinned bytes. `organs/retina.py` is sha-pinned in `genome/gaze.py:PINS`; a rewrite is a new pin and needs a byte-identity proof against the old one on the life's own tape |
| 10 | **No change sense** (nothing in his world moves, so nothing is lost yet) | moving-edge and net-dimming detectors are 2 of the frog's 4 operations (§1.2) | an event layer at **0.235 ms** (§2b) | the world. The world-maker draws still canvases; §4 G-EYE-5 is declared OFF for exactly that reason |
| 11 | **The tower is a pretrained organ, not a genome-set one** — its 719 weights came from a gradient run over 108 glyph classes | a retina's filters ARE genome-set; V1's are innate and only refined (§1.4, Crair 1998) | a DoG pyramid (**0.365 ms**) or a Gabor bank (**0.883 ms**) whose numbers sit in the genome file | **G0 already measured the strike against it: a 3-orientation bank's margin was −0.19**, and no front keeping absolute size reached a positive margin. This gap is real and the obvious fix is measured-to-fail |
| 12 | **One front for two worlds** — drawn canvases and his folder photographs share `thresh0.25 centre tower sqrt` | *Anableps*: different opsins in the two halves of one eye (§1.6 row 26) | the tape already carries `source: "folder"` vs the maker's rows | whether a second front helps when neither front bands photographs (gap 7) |

---

# 4 · THE GROWTH INSTRUCTIONS PROPOSED

Draft lines in the genome's own syntax (`NAME  value words  # source`). **Proposals, not laws.** Every line says whether today's parser accepts it. Read from the code, not the docstring (#194): `genome/machinery.py:199-200` ends the gene chain with `else: raise GenomeError(f"unknown gene {gene!r} … the organism does not start")`, and every known gene is a strict `re.fullmatch`, so an unknown NAME **or an extra word on a known one** refuses to start. RETINA whitelists exactly `thresh<n> | centre | blur<n> | pool<k> | hog<n> | hogcells<k>x<n> | tower:<name> | sqrt | unit`; GAZE takes exactly one shape. Anything else below is **new vocabulary** — a parser clause + an interpreter + a toy, and until all three exist the machinery refuses, which is the right behaviour. Costs are §2's measured ones against 26.53 ms.

Each line carries: **source · the test that could refuse it · the twin · the ceiling before the bar (#228 b) · where the plant fires**.

---

**G-EYE-1 — WHERE, WHEN and the ACT delivered BESIDE the traits**

```
DELIVER  where fixation when instant act glance     # new vocabulary
```
*The design point, and it is load-bearing.* The three numbers go into the **FAST episode and the tape row**, never into the vector the SLOW area compares. Concatenating a position into a cosine-compared vector makes the same shape at two places into two cells — that is the organ doing the mind's job, refused by his 13:30 word, and it is #228 (c)'s lesson (the 4×4 pool already leaks coarse position into the 112 features by construction, which is why E51's first position plant had to be re-declared as a window on a canvas).
- **Source:** his 13:30 «traits and geometric time space combined»; Duhamel/Colby/Goldberg 1992 `[abstract: MED/1553535]`; §0.3 item 3.
- **Test that could refuse it:** E51's position plant in its A1.2 form — two classes whose 32×32 frames are **byte-identical**, differing only in where the window was taken. The creature must answer above chance through the mind. **Ceiling first:** assert the byte-identity and that the 112-vectors are equal to float tolerance, so chance is a fact, not a hope.
- **Twin:** `--blind where` — the same tape, the field dropped. Must sit at exactly chance.
- **Parity control:** with `DELIVER` declared, every existing mark must be **byte-identical** to life 2's (nothing entered the cosine). If the state hash moves, the line is wrong.
- **Cost:** ≈ 0.

---

**G-EYE-2 — the glances of one canvas are ONE look**

```
BIND     glances per canvas                          # new vocabulary
```
- **Source:** the life's own twins — **first-fixation-only 0.975 > 4-fixation 0.956**; transsaccadic integration (§1.3, Wurtz 2008 `[PMC: PMC2556215]`).
- **The diagnostic that decides WHICH fix is right, and it should be run before the gene is written.** Two hypotheses explain the 1.9 pp: *binding* (four looks at one thing should be one percept) and *noise* (glances 2–4 land on the three faint clutter strokes `render_canvas` draws, birth cells on them, and those cells then compete at recall). They call for opposite genes — `BIND`, or `GAZE … fixations 1`. Life 2's journal already carries the evidence: every row has `fix` (the cells) and `births` (with the birth moment), and `org.t` advances once per glance, so **each birth can be attributed to its glance index**. If births on glances 2–4 are disproportionately the cells that later misfire, binding is the fix; if the extra glances birth nothing unusual, one glance is the design. **One query, on a record that already exists.**
- **Test:** Q1 on all 16 words must reach **≥ 0.975** (the first-fixation-only twin is the bar, because today's extra glances are a net loss). **Ceiling before the bar:** Q1 is already 0.956 and the first-fixation twin 0.975, so the room is 1.9 pp — a bar above 0.99 would be above the arithmetic ceiling of a 160-item exam (#228 b).
- **Twin:** the unbound 4-glance road = life 2 itself.
- **Refusal is informative:** if binding does not beat 0.975, the honest line is `GAZE surprise fixations 1`, and one glance is the design.
- **Cost:** ≈ 0.

---

**G-EYE-3 — keep the colour the retina already computes**

```
RETINA   thresh0.25 centre opp3 tower:eye-tower-g2 sqrt unit     # `opp3` = new vocabulary
```
`opp3`: run the tower over three planes — luminance, `R−G`, `B−(R+G)/2` — and concatenate the three unit-length 112-blocks (336 numbers). The two opponency planes are **already computed** by `organs/retina.py` at 16×16; this computes them at glance resolution.
- **Source:** §1.2 (≥32 channels); E51's colour plant (**1.000 vs 0.500 exactly**); §0.3 item 1 (the creature computes opponency and throws it away).
- **THE GATE BEFORE THE GATE, and it fails today.** On the maker's world `rg ≡ 0` and `by ≡ 0` **exactly** — the canvas is one grey plane repeated three times, and life 2's folder door delivered 0 pictures. So `opp3` would today deliver two identically-zero 112-blocks: a channel placed where it cannot fire (#228 a, E49's defect). **This line is refused until the folder door has delivered ≥ N coloured pictures, and the check is one line: `max|rg|` over the last 100 canvases > 0.** Naming that before proposing it is the whole point.
- **Test, once the world has colour:** E51's colour-only family — identical glyph, different colour. **Twin:** the grey front (life 2's), which must sit at chance **by construction** — assert the grey frames are byte-identical between the two classes before training anything (#228 c).
- **The regression bar that could refuse it (#231 (6)):** gate G-a must re-run, and the drawn world's bands must not lose — today's THETA_N 0.952 with floor 0.9113 and within-p5 0.8412.
- **Cost: ≈ 0.94 ms a glance upper bound, ×4 glances ≈ 3.8 ms** — against E51's 5.11× this is the cheaper carrier E51's verdict asked for, because it reuses the sealed trunk instead of retraining a wider one. **14 % of the canvas for a channel that is currently constant zero: it is a line for the day his folder pictures arrive, not for the maker's world.**

---

**G-EYE-4 — a genome-set front beside the pretrained one**

```
RETINA   thresh0.25 centre dog3 hogcells8x6 unit     # `dog3` = new vocabulary; the tower dropped
```
- **Source:** gap 11; §1.4 (V1's structure is innate); the estate's own preference for a fixed front under a learned trait space `[from disk: atlas-sections/failures-and-theory.md]`.
- **Test:** gate G-a on the drawn world; the front is admitted only if its margin is **not worse** than `tower sqrt`'s (within-median 0.968, between-p95 0.903).
- **Printed beside it, because it is the prediction:** G0 measured a 3-orientation bank at **margin −0.19**, and no absolute-size-keeping front reached a positive margin at 24×24. **This line is expected to fail**, and saying so before the run is the point of proposing it — the value is a genome-set front we can *mutate between lives* (E29's direct-search road, the one that won) rather than a sealed binary nobody on this box can grow.
- **Cost:** 0.365 ms a glance — **cheaper than the tower's 0.457 ms.**

---

**G-EYE-5 — the mind's prediction reaches the organ**

```
SURPRISE floor 0.05 predicted last-canvas            # NOT an extension: SURPRISE parses `re.fullmatch(r"floor (<num>)")` (machinery.py:209), so the extra words REFUSE — this is a parser change
```
Pass the previous canvas's saliency map as `gaze_sequence(..., predicted=...)` — the argument `organs/gaze.py` already takes and `genome/gaze.py` hardcodes to `None`. The organ then reports the **residual**, and the prediction is the mind's, exactly as the BRIEF's ADAPTS bin requires.
- **Source:** his AGI-QA — *"the brain actively sends a prediction down to the organ, which reports back confirmation or error"*; Rao & Ballard `[from disk: R2 §1.2]`; Hosoya `[fetched]` for the biological precedent that a retina really does re-tune to recent statistics.
- **Test:** on a canvas repeated twice, the second canvas's fixations must move OFF the cells the first explained; on a changed canvas they must land on the change. **Plant placed where it can fire:** a two-canvas pair differing in exactly one cell — the fixation must find it. Today's road cannot fire this test at all (`predicted=None`), which is why it is a proposal and not a claim.
- **The seam that may refuse it (gap 6):** the mind's PREDICT works in 112-feature space and saliency in 16×16 cell space. This line predicts the **saliency map**, which the mind does not currently hold. Either the mind gains a cheap map-predictor, or the line is refused as unwireable and said so.
- **Cost:** ≈ 0; but it **breaks the byte-identical replay of any earlier tape**, so it is a new life.

---

**G-EYE-6 — a coarse view with every glance (fovea + periphery)**

```
GAZE     surprise fixations 4 grid 16 canvas 128 glance 32 ink border coarse 32   # `coarse` = new vocabulary
```
Each canvas also delivers ONE whole-canvas 32×32 feature vector (the existing `mode="one"` road), beside the fixated glances — the fovea/periphery pair of §1.1, and the *Anableps* two-region idea of row 26 in its cheapest form.
- **Test:** Q1 must beat **0.975** (G-EYE-2's bar). **Ceiling:** the one-glance twin alone already reads **0.819**, so most of the answer is in the coarse view and the marginal room is small — declare that before the run.
- **Cost:** +0.457 ms a canvas (one extra tower pass), **+1.7 %**.

---

**G-EYE-7 — the scan as the channel (the mantis shrimp line)**

```
SCAN     channels lum rg by across fixations         # new vocabulary; requires G-EYE-1
```
Rather than widening the vector (G-EYE-3), give **successive fixations different channels** and let the MIND bind them — *"temporal signaling combined with scanning eye movements … color recognition rather than discrimination"* `[abstract: MED/24458639]`. This is the proposal that fits his rule most exactly: the organ never combines anything; the mind does, using the WHEN and the ACT that G-EYE-1 delivers.
- **Test:** the same colour plant as G-EYE-3. **Twin:** the channels shuffled across fixations (the binding is destroyed, the information kept) — must fall to chance, or the mind was not binding.
- **Cost:** **0** extra tower passes — it re-spends the four glances it already pays for, and that is the whole attraction.
- **What it costs instead:** the four glances stop covering four places. It trades space for spectrum; the twin against G-EYE-3 decides which the creature needs.

---

**G-EYE-8 — declared OFF, with reasons (so nothing is smuggled in)**

```
#OFF EVENT  log-threshold 0.15 over canvases   # 0.235 ms; OFF: nothing in the maker's world MOVES, so the channel would be constant-zero (#228 a: a plant placed where the mechanism cannot fire)
#OFF DEFOCUS two-blur depth ratio              # R2 §1.7 (the spider); OFF: the canvases are flat renders with no depth to recover — the plant has no ground truth
#OFF MICRO   jitter ±1 px, features averaged    # §1.3 microsaccades; OFF: the renderer already jitters position ±3 px, scale 0.8-1.2, rotation ±15 deg, noise sigma 0.05 (genome/world.py:129-132), so this would measure the renderer, not the eye (#171)
#OFF EYES2   two gazes on two threads           # §1.6 row 25 (chameleon); OFF: one canvas at a time — a second gaze has nothing to look at
```

**And one thing that is NOT proposed as a gene, because it is a repair:** gap 9. `organs/retina.py:cell_means` is a Python loop costing **4.77 ms of every canvas**; the whole 8-channel analysis vectorised reads **0.462 ms against 5.42 ms**. That is **≈ 4.3 ms a canvas, 16 % of the life's budget**, for no change in behaviour. It is sha-pinned in `genome/gaze.py:PINS`, so the only honest road is: rewrite, prove **byte-identical saliency maps and byte-identical fixation sequences on life 2's own 18,959-row tape**, re-pin, and say in the register that the pin moved and why. Nothing about the eye's design changes.

---

# 5 · WHAT THIS DOCUMENT DOES NOT CLAIM

1. **It does not claim any of §4 will help.** G-EYE-4 is predicted to fail and is proposed anyway, for the reason stated. **G-EYE-3 and G-EYE-7 cannot even be tested today** — the maker's canvas is grey replicated three times and `rg`/`by` are exactly zero, so both are refused until the folder door delivers coloured pictures. G-EYE-6's own ceiling (the one-glance twin already reads 0.819) leaves it little room. **The only two lines with a live, measured hole behind them are G-EYE-1** (his own 13:30 sentence; §0.3 item 3) **and G-EYE-2** (first-fixation-only 0.975 beats four fixations 0.956, in his creature's own verdict), and the largest single win in the whole document is not a gene at all — it is the 4.77 ms Python loop of gap 9.
2. **It does not claim the photograph problem is an eye problem.** Four fronts were measured and all four overlap; his own research says invariance is not the sensor's job. If the fix is a context input, the eye is not where it goes.
3. **It does not re-litigate E51 or E29.** Their verdicts stand as read: the channels carry and were too dear; the eye's shape is searched directly and not grown by a rule.
4. **It contains no gate, bar or threshold that anything will be judged by.** Every number in §4 is a proposed bar for a proposed test, and every one is written with its ceiling beside it precisely so it can be refused before it is run.
5. **What it did not source, named rather than smoothed over.**
   - the 100:1 optic-nerve compression (§1.1) — `[unverified]`, and used only as an order of magnitude;
   - the 200–300 ms reading fixation (§1.5) — the review is the road but I read its abstract, not its body, so the number is the field's standard figure and is tagged `[secondary]`;
   - **free-viewing fixation durations (~100–1,000 ms) — NOT SOURCED.** The brief asked for them; I found no primary I could read and did not want a number with no road, so §1.5 carries the reading figure only;
   - **the fly's Reichardt/Hassenstein correlator and its flicker-fusion frequency — NOT SOURCED.** Row 27 of §1.6 is a 2026 optic-flow-tuning paper, which is a *different* claim; **the fly is not covered by this document** and no ~250 Hz figure appears anywhere in it;
   - Hubel & Wiesel's own 1963 kitten paper (Europe PMC carries no abstract for it). The innate-then-refined claim rests entirely on **Crair 1998**, read in PMC, which states it more precisely anyway.
6. **The `[measured here]` numbers are mine, from one process on an idle box**, not from inside a running life. The 26.53 ms they are compared against is the life's own live median with every thread running — a solo probe is not a live one (#195/#233), so every cost above is an **under**-estimate of what it would cost inside the creature.

## The three questions only Ahmad can answer

**Q1 — Is the pretrained tower an organ you accept, or a debt?**
`judge/eye-tower-g2` is 719 weights produced by a gradient run over 108 glyph classes. It never changes in a life, so it obeys your 13:30 rule *in operation*; but it was not written by the genome, and no road on this box could grow it. `HUMAN-MECHANISMS §4`'s last row says a pretrained organ needs **your word each time**. G-EYE-4 is the genome-set alternative and G0's measurement says it is worse. **Do we keep the tower and say plainly that the eye's front is inherited, or spend a rung on a front the genome owns and accept a weaker eye to get a mutable one?**

**Q2 — Does the gaze belong to the eye or to the mind?**
Today the eye picks its own 4 fixations from a saliency map (FIXED), and it works — 220/220, ×12.22. Biology says the *map* is the organ's and the *choice* is the mind's (§1.5: the superior colliculus's hard-wired bias under a priority map the rest of the brain writes into); Friston's line is that a saccade is an **experiment**. Your 13:30 rule says learning is the mind's — but choosing where to look is not obviously learning. **Should CURIOSITY eventually choose the look — making a fixation an act the creature decides and can be wrong about — or does the eye keep its own cheap rule and the mind only choose what to think about afterwards?**

**Q3 — What is the creature's "context", when he has no page?**
The photograph failure (gap 7) has one fix on disk and it is not a better eye: a **context input at the label stage** — the reader knows the page's script, the film knows its subtitle track, the exam bank names the family. His creature's only context is the folder name, and the folder name **is the word he is trying to read**, so it cannot be an input to reading it. **Is there a context you are willing to give him that is not the answer** — the source (maker / folder / web), the arrival, the time of day — **or does the eye stay script-blind and photographs stay a reported band that never gates anything?**
