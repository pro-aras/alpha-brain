# RESEARCH — COGNITIVE MAPS, IMAGINATION, SETTLEMENT, AND GAP-DIRECTED EXPLORATION (his 10-08 share, second wave)

> edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-08 — Ahmad's continuing research order of
> 2026-10-08 («Continue and do check these papers too and other things», «These too»). The shares: three
> screenshots (`/data/research/shared-images/2026-10-08_*.png`) and three PDFs (filed under
> `/data/research/`). This document is the seat's synthesis of five read-only extractions; it follows
> RESEARCH-COMPILED-CIRCUITS-AND-REASONING.md (this morning's first wave — its blocked-paper flag is now
> UPGRADED: Ahmad fetched Mueller's theory paper from his own browser, and it has been read whole).

## 1 · The sources and their honest read-status

| source | identity | read-status |
|---|---|---|
| **Agreement and Surprise: Global Equilibrium from Local Repair** | Bernhard Mueller, Pragma Research (his own imprint), draft 2026-10-06, 26 pp — the theory of his Cadence program (this morning's blocked MUEAAS-2, fetched by Ahmad) | **WHOLE** — every definition, theorem, and proof VERIFIED LINE BY LINE (all elementary and correct: Brouwer, Banach, coordinate descent, telescoping, residual bounds); the soundness audit was the point, since the imprint is his own |
| **Extending cognitive maps from navigation to language learning** | Shaoqi Pan & Patrick C.M. Wong, *Trends Open* (Elsevier), Open Access Opinion, doi:10.1016/j.treopn.2026.07.014, 15 pp | **WHOLE** (text, all sections, 129 references by title; figure pixels as captions — flagged) |
| **Beyond Thinking: Imagining in 360° for Humanoid Visual Search** | Zhang, Wang, Tu, Li, Wang, Zhan — arXiv:2605.09146 (cs.CV), 2026-05-09 | **WHOLE** (main text + appendix, arXiv HTML; tables as prose-quoted numbers — flagged; a 1.96M/1.92M sample-count inconsistency stands) |
| **The Geometry of Cortical Computation (VCNet)** | Hill, Zhang, Prasetio — NeurIPS 2025 NeurReps + CogInterp workshops, arXiv:2508.02995v3 | **WHOLE** (v3 text + references; no code found anywhere — flagged; the X-post's «handles occlusions» has NO experiment in the paper — flagged) |
| **A Tale of Two Graphs (DualGraph)** | Shi, Ma, Yao, …, Zhang (Microsoft) — arXiv:2602.13830v3 (cs.IR), 2026-08-25, 29 pp | **WHOLE** (text layer incl. all appendices; figures image-only — flagged) |

## 2 · The clues, ranked by what they change for the organism

**CLUE 1 — Averages agree where states do not rest (Mueller's Prop 8 + his fly measurement — the deepest
clue for a stream-living creature).** The organism never rests by design — the world stream keeps it
detuned. The paper proves the time-averages obey the wiring's balance law anyway (‖x̄ − R̄‖ ≤ diam/T,
exact), and *measured* on the fly connectome: an average-readout carries 15/29 held-out facts vs the
rest-readout's 9/29. Our organs read INSTANTANEOUS winners everywhere (`machinery.py:1513-1519`);
a leaky-average readout layer is ABSENT. **Buildable under the pure road** (one line per cell; the
instantaneous read as its twin). The counter-warning is measured too: the worm's average settled
*stimulus-independently* — «keeps the wiring and little of the evidence» — so the twin must check
stimulus-dependence, never just fact-passing. → **the readout road's first candidate law.**

**CLUE 2 — Settle-with-refusal is a certified form, and the meter exists (Mueller's Thm 12 + §5.2).** When
a step map contracts with measured q, the residual is a two-sided certificate of distance-to-agreement
(D/(1+q) ≤ Δ ≤ D/(1+q⁻¹)); when it doesn't contract, the honest report is «not at rest within budget» —
his engines refuse an answer whose residual exceeds tolerance, and our organs already carry the refusal
SHAPE in four places (budget-refusing births `machinery.py:1506-1510`; the mouth's read-back sufficiency
`learners.py:1396-1403`; the brain's conformal refusal `genome/brain.py:349-359`; ABSTAIN). What the paper
adds is the METER. **Buildable under the pure road** — the first-law form is the budgeted-residual
refusal + honest non-settlement report, with q-estimation as a named pre-reg question. → **N1's
quantitative frame: precision as a displacement bound** (Graepel's sentence, now with a meter).

**CLUE 3 — Imagine the unobserved as a weighted SET in representation space — never pixels, never one
bare guess, never unstructured (the 360° paper's three negative results, independently measured).** Their
pixel-space imagination ablation LOST to the baseline (46.17 < 48.04); layout-less priors were worse than
none (41.00 < 48.04); one deterministic guess lost to a sampled distribution (61.54 < 62.75). This is
independent machine evidence for **N7's exact commitments**: predict in the organism's own representation
space (candidate cells/hypotheses as a weighted set via the existing Hebbian edges + KWTA), relational
structure always, a distribution never a point. Their models are trained transformers — architecture
clues only, never the training.

**CLUE 4 — Value-guided looking converges in 1–3 steps where unguided agents sweep blind (the 360°
paper's actor-over-imagination split) — evidence for G-EYE-5's undeclared form.** Our fixation selection
is bottom-up saliency with `predicted=None` hardcoded (gaze.py:254 — the documented «other form»).
The value analog for a task-free organism is **expected information gain / expected residual**, which
plugs into the curiosity organ and the EYE.md instrument already written (fixations must move OFF
explained cells, ONTO change). A law for value-driven fixation is the eye road's next rung after E2 —
its own PREREG, pre-registered constants, never learned weights.

**CLUE 5 — The cognitive-map account of language: multistep trajectory simulation, the successor
instrument, gaze-as-navigation (Pan & Wong, whole — Opinion-weight, «indirect evidence» by their own
declaration).** Three ABSENT-and-law-worthy forms, all pure-road buildable: (i) **multistep walks**
through the word map with a read-back gate (the inner turn walks single-step today — mind.py:1799);
(ii) the **successor-structure instrument**: do words with similar web neighbourhoods (shared predicted
futures) behave alike, better than surface/co-occurrence similarity predicts? — a bench law on our own
tape; (iii) **gaze-as-navigation**: the fixation trajectories over the 16×16 grid are a logged
navigation signal nothing reads as a map. Their design cue (separate surface form from role; simulate
trajectories; replay to consolidate/revise) is our form already; their five key references must be
whole-read before any law leans on them.

**CLUE 6 — Gap-directed exploration over the web (DualGraph, whole — LLM machinery, but the ablated
shape is ours to re-derive).** Enrich-the-weak + Explore-the-missing are BOTH necessary (ablated), and
topology beyond raw co-occurrence is necessary (their only-EntityRelation ablation LOSES). Our inner
walk wanders only what EXISTS (the anti-DualGraph). The pure-road surrogates are mapped exactly:
communities = connected components over consolidated edges; their SBM null = the web's own Poisson
chance expectation (web.py:175); their zero-evidence-first chains = our rule-N sprouts — which deserve
PRIORITY, not the miss rule's neglect. → **the curiosity/inner-walk's next law family** (PREREG ×3,
twin: gap-directed walk vs today's lift walk, planted control).

**CLUE 7 — The dual-stream (feat, pos) split has external convergent evidence (VCNet), and E2's form
sharpens.** Their what/where manifolds ≈ our `Hypothesis(feat, pos)` — already built, purer than theirs.
Their top-down error targets the LOWEST feature level, per-feature signed — E1 failed one level up with
a scalar steering (FAIL-TRANSFER); E2's law should back-project the expectation onto the front's own
ON/OFF/T-ON/T-OFF channel maps and read a per-channel signed error. **Buildable under the pure road**
(Hebbian back-projection, no gradient). VCNet itself: workshop-grade, no code, no occlusion experiment,
no matched-capacity baseline, the «geometry» never measured — architecture principles only, flagged.

**CLUE 8 — Learning as two-state contrast: the FORM is ours already, the theorem needs an energy we do
not have (Mueller's Thm 13, honestly refused).** The free/nudged two-state contrast is Hebbian in shape
with no backward pass — but it requires an energy-generated dynamics, and the paper itself warns the
directed-wiring contrast ≠ gradient. Our error-gated delta is already the local-surprise form; the
paper adds meters, not a better engine. **Architecture clue only.**

**CLUE 9 — Detuning named and metered (Mueller).** Perfect agreement is stillness; only CHANGING evidence
keeps a system alive (Thm 12: no disagreement, no motion). Our WORLD stream + CURIOSITY + PREDICT are
the organism's detuning machinery; the paper gives the definition (Δ(e) = D at the old rest) and the
displacement bound — a falsifiable meter for a future world-dynamics reading. Vocabulary + instrument,
pure road.

## 3 · What none of it gives us (honest limits)

- Mueller's **physics identifications** (the detuning law P=φ+π√α, the Standard Model Lie type, the
  Einstein-equation reconstruction) are declared premises of his sibling program with five undischarged
  obligations — quarantined; nothing beyond his finite consensus layer may enter a law. His Cadence
  *trained* nets stay outside the pure road; only the dynamics and certificate forms cross.
- VCNet is a workshop paper with no code, no ablation, no measured manifold, and X-post claims beyond its
  evidence — cited for architecture principles only.
- The 360° Imaginator and DualGraph are LLM/transformer machinery — every clue re-derived from counts
  over our own ledger or it does not exist for us.
- Pan & Wong is an Opinion article whose authors call their own evidence «indirect»; the framework's
  key references are NOT yet read whole — flagged until they are.
- Nothing here trains anything in the organism. Weights, teachers, fitting procedures stay outside;
  forms, meters, instruments, and validation discipline cross.

## 4 · Where the clues land on the road (no queue-jumping)

The queue stands: the cover law's verdict → V3's deferred marks (its AMENDMENT 1) → the Alpha 6 build +
launch → W2 (~10-12) → the N-road. The clues enter when their laws are written:
- **N1**: Graepel's sentence + Thm 12's displacement bound as the precision meter.
- **N2**: the integrator (this morning's CLUE) + VCNet's anchored recurrent settling form.
- **N5**: the schema gate — DualGraph's granularity lesson (over-fine relation extraction destroys gap
  detection) + the myth's quality-of-the-field.
- **N6**: dream-completions sleep (this morning's CLUE 1) + cognitive maps' inferential replay.
- **N7**: the weighted-set imaginer in representation space (CLUE 3) + predicted-vs-realized evaluation
  (the myth) + drift/retry counters.
- **The eye road**: E2 with the lowest-level per-channel signed error (CLUE 7); then the value-driven
  fixation law (CLUE 4).
- **The web road**: gap-directed exploration (CLUE 6) + the successor-structure instrument (CLUE 5.ii) +
  multistep walks (CLUE 5.i).
- **The readout road**: the leaky-average layer with the stimulus-dependence twin (CLUE 1).

## 5 · Sources

All five at §1 with their canonical URLs; the two law-citable-in-full: Mueller's A&S (whole, math
verified sound) and the 360° paper (whole; the five measured claims named). Citable with flags: Pan &
Wong (Opinion-weight; key refs unread), DualGraph (whole text; LLM-regime machinery quarantined), VCNet
(architecture principles only; no code). The morning's three (the compiled fish brain's engine/receipts,
CURBD, the myth essay) stand as synthesized in RESEARCH-COMPILED-CIRCUITS-AND-REASONING.md — with the
MUEAAS-2 flag now upgraded to whole-read by Ahmad's own fetch.

*Cost of this research: 5 read-only extraction agents across two waves; the synthesis the seat's; the
box's jobs (the ON replay, the cover-law build) undisturbed.*
