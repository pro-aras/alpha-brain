# RESEARCH-HUMAN-PREDICTIVE-NORMALIZATION — the brain's understanding stack, and the road to build it into Alpha 5

> edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-07 14:45 +0400 — Ahmad's research order of 2026-10-07
> (verbatim, from the chat): «why don't we look at a much harder and complex part of a brain an AI child which is
> Alpha 5, that like humans, humans always normalize the complex data to understand it easily and efficiently. Or in
> more accurate term, human brain predict and normalize the predictions of next moments in short to long horizons.
> That normalization and understanding of any complex information or input or data on entire planet or in entire
> human existence from old age to modern age. That capability, what is it called and how it works in humans and how
> can we even maturely and even with more advancement we can add to the Alpha 5 brain… So deep research on this topic,
> find as many clues and data that is connecting in even a slightest way and design a…»
>
> Method: the house's reasoning-craft §7 (whole-loop parts list first; every part mapped to Alpha 5's code with
> file:line or named ABSENT; primaries read with read-status flagged; evidence over elegance; NEVER CHEAT). Twelve
> source extractions were run as read-only research subagents inside this session (his «only you» rule: no separate
> workforce — the extraction notes are tools' output, every quote and figure below was taken from them, and each
> source carries its read-status); the synthesis, the code map, and the design are the seat's own.

## 0 · The answer in one paragraph — what it is called

The capability has no single name because it is a STACK, not a trick. Its three names in the literature:
**efficient coding** (Barlow 1961: recode the input so redundancy is stripped and only the informative residue
costs anything), **predictive coding / the predictive brain** (Rao & Ballard 1999; Friston 2005, 2008: the brain
predicts the next moment at every level and only the *prediction error* travels upward — to understand an input is
to already expect it), and **schema theory / cognitive maps** (Bartlett → Tolman 1948 → Tse 2007: new complex data
is understood *quickly and exactly* when it lands inside a pre-existing structure that does the work). Underneath
them all sits one ubiquitous neural computation, **divisive normalization** (Carandini & Heeger 2012): every
response is divided by the pooled activity of its population, which is what makes complex inputs comparable,
bounded, and context-relative at every stage. The short-to-long-horizon part of Ahmad's phrase is the **process-memory
hierarchy** (Hasson 2015): cortex is a stack of levels whose integration windows grow from milliseconds to minutes,
and prediction far ahead is possible only because the higher levels hold more of the past. «Understanding quickly
and exactly as it had to be understood» is the measured phenomenon of **schema assimilation**: with a stable schema,
a new consistent fact is learned in ONE trial and becomes cortex-resident within 48 hours (Tse et al. 2007); without
one, the same fact takes weeks or never sticks. That is the mechanism this document maps onto Alpha 5.

## 1 · The whole-loop parts list (the human mechanism, ten parts)

P1. **Divisive normalization** — the unit's response divided by the pooled drive of its population:
`R_j = γ·D_j^n / (σ^n + Σ_k α_k D_k^n)` (Carandini & Heeger 2012, Box 1). Buys: bounded signals, saturation by
contrast not by size, context-dependence for free (a stimulus that cannot drive a unit can still suppress it), and
two regimes from one equation (averaging when inputs are equal, winner-take-all when one dominates). Found in every
system examined (retina, V1, MT, V4/IT, A1, LIP value, fly olfaction) — «what seems to be common is not necessarily
the biophysical mechanism but rather the computation».

P2. **Efficient coding / redundancy reduction** — recode messages so the common ones cost little and the rare ones
cost much (Barlow 1961: rank inputs by past frequency, allot the cheapest outputs to the commonest; the stored rank
order IS the organism's model of its world). The quantitative toolkit: per-unit histogram equalization; PCA →
whitening → ICA; sparse codes under a reconstruction bound (Simoncelli & Olshausen 2001). The eye's retina already
works this way (sends errors/contrasts, not intensities — our E1 research).

P3. **Predictive coding, the cortical loop** — predictions descend, only precision-weighted prediction errors ascend
(Rao & Ballard 1999; Friston 2005, 2008; Bastos et al. 2012). The error unit is not a feature detector: it fires
when the input *violates learned regularities*. A well-predicted input self-quenches its error — understanding is
the quiet state. Learning's stopping condition is exact: no error component left explainable, and errors whitened.

P4. **Precision = learned gain on every error channel** — each error is divided by its expected variance before it
may update anything (Friston 2005's `ξ = Π ε`; Bastos 2012: precision sits on the error-broadcasting cells and IS
the attention gain; Friston 2008: precision is itself learned by matching expected precision to observed squared
error — a self-normalizing register). This is normalization living inside prediction.

P5. **The process-memory hierarchy (the horizons)** — every level's state IS its memory; the temporal receptive
window (TRW) grows up the stack: early areas tens-of-ms (phoneme→word), mid areas seconds (word→sentence), high
areas tens-to-hundreds of seconds (sentence→narrative) (Hasson et al. 2015). Windows are measured in *information
units*, not seconds — the brain rescales its dynamics to the input rate. Far prediction is possible only from long
windows: «computing predictions further into the future is made easier with more information about the past».

P6. **Trajectories, not points** — states are represented with their temporal derivatives (position + velocity +
acceleration…, generalised coordinates, truncated at ~6 orders because higher-order precision decays to nothing)
(Friston 2008). A prediction is a path, not a point; this is what confers memory on a state-space model and makes
the next *few* moments predictable, not just the next one.

P7. **Schemas — the fast absorber** — a schema is «a network of neocortical representations that are strongly
interconnected» (van Kesteren 2012's operational definition). With one: new consistent items are learned in ONE
trial and are hippocampus-independent within 48 h (Tse 2007); the mPFC-analog detects *resonance* between the input
and the active schema and potentiates the direct cortical link at encoding while *inhibiting* the episodic store
(SLIMM). Without one (or with an inconsistent one), the same item needs the slow route. The traps, measured:
partially-congruent input is remembered WORSE than both congruent and incongruent (the U-shape); and a novel row in
a structureless region produces LOW prediction error and little learning — «maximal overall novelty does not
necessarily entail maximal learning» (van Kesteren, Box 2).

P8. **Complementary learning systems + replay** — a fast, sparse, conjunctive episodic buffer (hippocampus) writes in
one trial without wrecking old knowledge; a slow, overlapping, distributed store (neocortex) extracts structure by
small interleaved updates; offline replay (sharp-wave ripples) is the teacher that interleaves new traces into the
old structure (McClelland, McNaughton & O'Reilly 1995). The slow store's learning rate must SHRINK as experience
grows (the optimal-estimator argument: step size ~1/n). Catastrophic interference is the price of violating this.

P9. **Chunking / recoding** — immediate memory is limited by the NUMBER OF ITEMS (~7±2 chunks), not by bits (Miller
1956, the paper's own negative result). The workaround: «group the input events, apply a new name to the group, and
remember the new name rather than the original input events» — recoding. Critical cost lesson: a recoding table pays
only once it is AUTOMATIC; an un-consolidated chunk steals capacity at recall (Smith's drill). Recall is
reconstruction from the code, and the reconstruction is systematically lossy (the eyewitness caveat).

P10. **Preplay and the chained horizon** — the hippocampus emits candidate sequences OFFLINE that prefigure
never-experienced structures (Dragoi & Tonegawa 2011: 14–16% of rest events, vs 3.2% chance, including in sleep
BEFORE any first exposure; ~80% of events match nothing — the background is honest noise). Long horizons are built
by CHAINING short replay chunks (reverse chunk for where-I-came-from + forward chunk for where-I-could-go; Wu &
Foster 2014), not by one long rollout. Generation is the free default of a recurrent graph («SPW bursts are not
induced but released»); THE BOTTLENECK IS THE READER: «the information does not lie in the rich variety of
sequences… but in the ability of hippocampal targets to differentiate among those sequences» (Buzsáki 2015).

**The machine echoes (the "more advancement" Ahmad asked about, with their warnings):** Ha & Schmidhuber 2018 —
a compressor (V) + an action-conditioned next-latent DISTRIBUTION predictor (M) + a deliberately tiny controller;
dreams are latent rollouts; but a policy trained in the dream CAN CHEAT the model (τ=0.1: dream score 2086 → reality
193, WORSE than random 210) — the dream must be kept slightly harder than reality (τ≈1.15) and the model's blind
spots are permanent on a fixed tape. LeCun 2022 (read-partial, flagged per section): predict in REPRESENTATION space
because pixel-space detail «cannot be predicted accurately, at least not over long time periods» — the encoder
learns to discard the unpredictable; H-JEPA stacks levels for multi-timescale prediction; and the trap: predicting
representations has a degenerate zero-loss solution (collapse) — any such build needs an anti-collapse guard from
day one. V-JEPA 2 (2025, abstract-only, flagged): the same skeleton at scale, action-conditioning post-trained,
planning by goal-embedding.

## 2 · The map against Alpha 5 (every part: organ + file:line, or ABSENT)

The live organism is brain-long-4 (genome master 4c6ef26). Read 2026-10-07.

| part | Alpha 5 today | verdict |
|---|---|---|
| P1 divisive normalization | nothing divides a population response by its pool anywhere in the sensory/learning path (grep-verified 10-07). The nearest: the READER's SLDA form — pooled covariance + shrunk inverse (brain/scene/learners.py:670) — a second-order whitening used ONLY for classification distances, never for gain/surprise | **ABSENT as gain; a covariance cousin exists** |
| P2 efficient coding | the eye sends located features and E1 files a residual; no whitening/equalization/sparse layer of the organism's own (E2's plan names this gap) | **ABSENT (E2 planned)** |
| P3 predictive coding loop | the DRIVE turn EXPECTS, then learns (creature/mind.py:1720s: turn before learn; genome/brain.py:Brain.turn); the eye's residual + E1's chosen look is the error-steering arrow; surprise exists | **PRESENT, one level deep, unweighted** |
| P4 precision gain | surprise = 1 − |overlap|/|U| over expected vs uttered words (genome/brain.py:602) — a raw word-overlap count, no variance, no precision register anywhere | **ABSENT** |
| P5 process-memory hierarchy | the FAST ring (recent episodes) vs SLOW store + sleep consolidation into it (mind.py:518's comment: SLEEP replays the n most-surprising moments into SLOW); the knowledge web (genome/web.py). But every level integrates at ONE timescale; there is no stack of growing windows | **PARTIAL: two stores, one timescale each** |
| P6 trajectories | predictions are point expectations over the instant's words; no state carries a rate/velocity | **ABSENT** |
| P7 schema gate | the web's words have types/cliques and census metadata (genome/brain.py:258; the cover types of learners.py); a new pattern is absorbed by the SAME slow learner every time — no resonance gate, no fast congruent path, no U-shape handling | **ABSENT (the substrate exists)** |
| P8 two-speed learning + replay | sleep replay by surprise EXISTS (SLEEP-IDLE graded PASS 10-05; the idle clause landed); interleaving/rate-decay not implemented; replay selects by surprise only (no goal/recency bias, no significance bar) | **PARTIAL** |
| P9 chunking/recoding | no group-and-rename operator; the web's words are born per-meeting, never by compressing a recurrent pattern into one node (KW-1's verdict had the seed of this) | **ABSENT** |
| P10 preplay / chained horizons | sleep replays RECORDED moments only; no candidate-sequence generation, no chaining, no significance testing of replays | **ABSENT** |
| predictions beyond the instant | THINK's kind-(b) predictions become scorable when their word recurs (mind.py:2852) — next-occurrence, single-horizon; frames = ordered word-pair co-occurrence with evidence (genome/sentence.py:30) — a two-step relational seed | **PARTIAL: one horizon, relational seeds exist** |
| curiosity | genome/curiosity.py (Interests) exists in the organism (mind.py:166) | **PRESENT** |
| action-conditioned world model | the game world has acts (act_policy outcome-weighted, act_weights learned) but NOTHING predicts the next state given the act — the reasoning research's named candidate (RESEARCH-BRAIN-REASONING-ALPHA-JEPA.md) | **ABSENT — the big one** |

## 3 · The design road (each its own law, in dependency order; every bar written FIRST; never a loosened bar)

Priced as classes only (S = a bench law, days; M = a law with a pinned window or a replay gate, about a week; L = a
rung of the organism, weeks). Nothing here jumps the W2→W3 queue — the mentor world is itself the schema channel
(P7's substrate arrives through the mentor's structured speech).

- **N1 · PRECISION (S).** Surprise becomes precision-weighted: every error channel carries a learned inverse-variance
  register, updated to match expected vs observed squared error (Friston 2008's M-step rule, one line of machine
  form). The instrument that proves it is the repetition-suppression analogue: first exposure large error, Nth near
  zero, a deviant row re-evokes it (Friston 2005's MMN shape). Byte-identity for every organism caller behind a flag,
  the mouth-cap pattern. *Why first: it is the cheapest and it normalizes every later surprise measurement.*
- **N2 · THE TRAJECTORY (S).** The brain's tracked quantities carry [value, rate] (order-2 generalised coordinates);
  expectations become short paths. Measured by: does a trajectory-bearing expectation score better on the tape's
  predictable stretches than the point form, at matched cost (twin, planted control, the null).
- **N3 · THE WINDOWS MAP (S, a measurement law).** Hasson's own instrument, run on our organism: scramble the tape at
  granularities (moments / episodes / days) and measure each level's reliability drop — the organism's TRW map,
  printed. The negative control is built in (a level that answers scrambled input identically has a short window).
  Its reading decides whether N4's new level is needed at all.
- **N4 · THE CHUNKER (M).** Group-and-rename: a recurrent row-pattern becomes ONE web node; thereafter the organism
  predicts and remembers the node, not the rows (Miller; Barlow's staging). The honest gate: a chunk is adopted only
  if it reduces the total description cost (compression-progress, Toy A's proven instrument), and it pays only after
  sleep makes it automatic (Miller's Smith lesson — a fresh chunk that costs at recall is a LIABILITY, measured).
- **N5 · THE SCHEMA GATE (M).** Resonance between the incoming row and the currently active web region chooses the
  write path: high → a direct web link at encoding (the congruent fast path); contradiction → an episodic instance;
  and the U-shape is MEASURED and printed (partially-congruent must land worse than both ends, or the gate is wrong).
  The novelty trap is a named bar: a row in a structureless region must produce LOW surprise and little learning
  (van Kesteren's Box 2), never a novelty-seeking write storm.
- **N6 · PREPLAY (M).** Sleep becomes generative: the web's own dynamics emit candidate sequences; each is matched
  against stored templates with a shuffle-tested significance bar (Dragoi & Tonegawa's own statistics); never-used
  words are recruited; emission is biased to the current frontier (the junction-end effect). The honest bar counts
  the background: ~80% of events should match NOTHING — a build where everything matches is overfitting, caught.
- **N7 · THE WORLD MODEL (L, the rung).** The action-conditioned latent predictor over the organism's own tape —
  the convergent candidate of the reasoning research, now grounded by this one: predict the next REPRESENTATION given
  the act (never the raw row — LeCun's argument and JEPA's form), with (a) the anti-collapse guard declared BEFORE
  the build (a constant representation is zero loss without one — VICReg-style variance/covariance pressure is the
  named candidate), (b) the dream-exploit hazard named (Ha & Schmidhuber's τ=0.1 disaster: dream success can be
  ANTI-correlated with world success — the organism's dream arm carries a τ knob and a held-reality check), and
  (c) MuZero's lesson carried: the model predicts what the ACT changes. This is the largest law of the road and it
  is drafted only after N1–N6's readings exist.
- **The eye's own rung (E2, already named):** the learned sparse-coding front over the organism's OWN canvases —
  P2's layer — stays where E1's road put it, beside this road, not inside it.

## 4 · What this design does NOT claim (the never-cheat section)

- No borrowed LM, no borrowed weights, no next-token head anywhere in the organism (the pure road; the machine
  echoes above inform the DESIGN and nothing else).
- Efficient coding ≠ compression (Simoncelli & Olshausen's own caveat): the laws above never claim a rate-distortion
  optimality, only measured redundancy reduction with its losses printed (compression is systematically lossy —
  Miller's eyewitness caveat is carried as an honesty instrument: which details were reconstructed).
- The human literature itself is unsettled where noted: SLIMM's clean division is empirically challenged (its own
  Box 3); preplay has a preformed-structure confound (Buzsáki 2015 names it); the laminar assignment of error vs
  expectation cells has flipped across formulations (Bastos 2012 carries both). Where the science is unsettled, the
  law's bars are written so the ORGANISM's measurement, not the literature's authority, decides.
- Ahmad's «more advancement»: the only advancement past the human mechanism allowed here is the one the evidence
  supports — the machine echoes' measured lessons (representation-space prediction, the tiny separable controller,
  the τ-hardened dream). Improving past the real mechanism is a cheat dressed as rigor (reasoning-craft §7).

## 5 · Sources and read-status (every citation carries it)

- Carandini & Heeger 2012, *Normalization as a canonical neural computation*, Nat Rev Neurosci 13:51–62, DOI
  10.1038/nrn3136 — **read whole** (PMC3273486).
- Friston 2008, *Hierarchical models in the brain*, PLoS Comput Biol 4(11):e1000211 — **read whole** (PMC2570625, OA).
- Friston 2005, *A theory of cortical responses*, Phil Trans R Soc B 360:815–836 — **read whole** (PMC1569488).
- Bastos et al. 2012, *Canonical microcircuits for predictive coding*, Neuron 76:695–711 — **read whole** (text;
  figures via captions) (PMC3777738).
- Hasson, Chen & Honey 2015, *Hierarchical process memory*, TiCS 19:304–313 — **read whole** (PMC4457571).
- Reynolds & Heeger 2009, *The normalization model of attention*, Neuron 61:168–185 — **read whole** (main text;
  the supplemental derivations PDF was inaccessible — flagged) (PMC2752446).
- Barlow 1961, *Possible principles underlying the transformations of sensory messages* — **read whole** (the NYU
  CNS scan; OCR noise in two passages flagged; no contemporary DOI).
- Simoncelli & Olshausen 2001, *Natural image statistics and neural representation*, Annu Rev Neurosci 24:1193–1216 —
  **read whole** (the authors' NYU reprint PDF).
- Miller 1956, *The magical number seven, plus or minus two*, Psych Review 63:81–97 — **read whole** (psychclassics).
- Tolman 1948, *Cognitive maps in rats and men*, Psych Review 55:189–208 — **read whole** (psychclassics; figure
  data image-only).
- McClelland, McNaughton & O'Reilly 1995, *Why there are complementary learning systems…*, Psych Review 102:419–457 —
  **read whole** (the author's Stanford PDF).
- van Kesteren et al. 2012, *How schema and novelty augment memory formation*, TiNS 35:211–219 — **read whole**
  (the author's MRC-CBU copy).
- Tse et al. 2007, *Schemas and memory consolidation*, Science 316:76–82 — **abstract-only** (paywalled), supplemented
  by Squire's companion commentary (read whole, PMC2271071) and van Kesteren 2012's Figure-1 account — FLAGGED;
  no law may cite the paper's unverified details until read whole.
- Dragoi & Tonegawa 2011, *Preplay of future place cell sequences*, Nature 469:397–401, DOI 10.1038/nature09633 —
  **read whole** (the accepted manuscript via MIT DSpace; the SI not read — flagged).
- Buzsáki 2015, *Hippocampal sharp wave-ripple…*, Hippocampus 25:1073–1188 — **read-partial, deep** (the mechanism,
  consolidation, constructive/preplay and synthesis sections whole; pharmacology/development/models sections not
  read line-by-line — flagged) (PMC4648295 via Europe PMC).
- Ha & Schmidhuber 2018, *World Models*, arXiv:1803.10122 — **read whole** (the official interactive full text;
  appendix corroborated at snippet level only — flagged).
- LeCun 2022, *A Path Towards Autonomous Machine Intelligence*, OpenReview — **read-partial**: pages 1–17 read whole
  from the PDF; §4.2 onward recovered as verbatim excerpts via secondary hosts — FLAGGED; any load-bearing §4.4+
  claim must be re-verified against the PDF before its law.
- Assran et al. 2025, *V-JEPA 2*, arXiv:2506.09985 — **abstract-only** — FLAGGED.
- Rao & Ballard 1999 — read-status carried from the E1 research (RESEARCH-HUMAN-EYE-MECHANISM.md).

*Cost of this research: 12 read-only extraction subagents inside the seat's own session (his 10-06 rule honoured:
research because he asked), one code-map pass, no GPU, no rented machine, no box jobs beside the running life and
the armed replays.*
