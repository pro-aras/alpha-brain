# RESEARCH — COMPILED CIRCUITS, BRAIN-WIDE INTERACTION MAPS, AND THE REASONING MYTH (his 10-08 share)

> edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-08 — Ahmad's research order of 2026-10-08
> (verbatim): «Also i found some interesting studies and research. If you can study these and extract the
> valuable clues and parts for reverse Engineer it. I think that myth of reasoning i shared with you
> already.» The shares (four screenshots, saved): `/data/research/shared-images/2026-10-08_*.png`.
>
> Method: three read-only extraction agents (research he ordered — the 10-06 rule honored), each source's
> read-status flagged; the synthesis, the code map, and the road decisions are the seat's. House lens: the
> pure road (no borrowed weights, no LM, no backprop anywhere in the organism); human-mechanism-first.

## 1 · The sources and their honest read-status

| source | identity | read-status |
|---|---|---|
| **The compiled fish brain** | Bernhard Mueller (@muellerberndt), 2026-10-07: a measured connectome compiled into a «Cadence patch net», ~26× a spiking model's efficiency, running in-browser (floatingpragma.io/demos/connectome/); code `github.com/muellerberndt/cadence-demos` (GPL-3.0) + the `cadence` library; amplified by Yann LeCun | **whole**: the demo page, the engine sources (brain.js 547 lines, life.js, senses.js, twin.js, dictionary.js, disclaimers.js), `docs/connectomes.md`, `docs/patchnet.md`, the equilibrium SPEC, the receipts (cost.json, demo_net_facts.json, learning_release.json), the sleep-and-dream article. **BLOCKED (Cloudflare, abstract-only)**: his two 2-day-old self-published theory papers (MUEAAS-2 «Agreement and Surprise», MUECAP-2 «Local Patch Settlement») — **no law may cite their bodies until the PDFs are obtained another way** (e.g. Ahmad fetches them in a browser); the mechanism was verified in the published CODE instead — the better receipt anyway |
| **The interaction-map paper** | Perich, Arlt, Soares, …, Harvey, Deisseroth, Rajan — *Neuron* NeuroResource, open access, 2026-08-07 (DOI 10.1016/j.neuron.2026.07.016, PMC13565020); the 2026 version of the 2020 bioRxiv preprint; method name **CURBD** (Current-Based Decomposition), code github.com/rajanlab/CURBD | **WHOLE, both versions** (2026 via the PMC open text; the 2020 v2 preprint; equations read in the preprint's numbered form; figures as captions only — flagged) |
| **The Myth of Reasoning** | «Deep Manifold» (pseudonymous), self-published Substack essay, 2026-08-08 — *Intrinsic Pathways, Reasoning RL, and the Limits of Truth*; the same author's X post Ahmad shared; Thore Graepel's comment beside it | **WHOLE** (both editions + the 3 figures + the load-bearing sibling glossary essay). No local copy had ever landed (his «shared before» was the screenshot logged screenshot-only at RESEARCH-BRAIN-REASONING-ALPHA-JEPA.md:7 — this extraction upgrades that flag) |

## 2 · The clues, ranked by what they change for the organism

**CLUE 1 — Sleep that replays the store's COMPLETIONS, not the recordings (the most transferable).**
Mueller's night side (the sleep article + the code receipts, read whole): the day writes one-shot exact
records into a sparse-keyed store (a cousin of our KWTA novelty births); the night trains the slow weights on
**the store's own completions of the day's cues — the dreams**; dawn rewrites the store against the moved
weights. Measured: store alone 81.5 % of never-taught combinations; one night of 8,000 dreams → 100 %;
awake-teacher control 90.5 %; the hazard named: dreaming guesses teaches guesses as facts (sleep
redistributes, never corrects), and the stale-residual drift failure. OURS: sleep replay EXISTS but replays
**recorded moments only** (`creature/mind.py:524`). This is our SLEEP with a different teacher source — it
lands directly on **N6** (generative replay, the normalization doc's named gap), with its hazard carried as
a named bar. *Buildable under the pure road.*

**CLUE 2 — The recurrent-loop INTEGRATOR as a held-memory organ; gain is the forget/hold dial.** The fish's
gaze-holding circuit is the same one-pole recursion family as our cutter's bank (`tools/worlds/
event_cutter.py:105-111`, τ∈{1,4,16}) — but at near-unit loop gain it HOLDS (τ≈17 s; the eigenvalue receipt
42.2/22.7/17.2 = the slow modes). Our FAST ring holds by buffer, not by dynamics. A gain-dialed integrator
is the natural substrate for **N2's trajectory state** [value, rate] and a candidate hold register for the
brain organ. *Buildable under the pure road* (no training; gain by protocol, next clue).

**CLUE 3 — When a parameter is fit, the control must re-fit its own.** Mueller's gain-selection protocol:
2–3 physiology facts select the gain, the rest are held out, and **shuffled wirings select their OWN gains**
as the control (7/13 held-out facts vs 3,1,1 on three shuffles). This is our twin/null culture independently
arrived at — with one stronger twist worth adopting into every future law that fits anything. *Pure
discipline; no code.*

**CLUE 4 — Take nature's algorithm, refuse her adjacency matrix — affirmed by a working counterexample.**
Mueller compiles real wiring and gets a working reflex organ, but must hand-declare the dynamics, senses,
pilot, burst generators, and starting efficacies (his own line: synapse counts alone do not identify what
was inherited versus learned). The house already ruled this for the fly mushroom body (the inventory's R5:
take the ~200-line algorithm, refuse the adjacency). Compiled measured wiring into the organism: ABSENT and
stays so — the integrator's *form* enters (CLUE 2), never a weight file.

**CLUE 5 — A directed, signed, block-structured area↔area interaction map, with planted-ground-truth
validation (CURBD).** Their fitted RNN's matrix decomposes every area's activity into directed per-source
currents; validation = generator models with planted interactions recovered (VAF), the correlational null
(CCA) SHOWN TO FAIL on the same data, subsampling robustness, the failure regime mapped (needs distinct
per-area dynamics + sparse cross-links — a named precondition). OURS: the areas exist (sight/words/
episodes), the recall path exists (`machinery.py:2155`), the edge births are time-stamped — but nothing
directional/signed/per-area-pair exists (grep-verified ABSENT). The instrument form (decompose every
cross-area lighting into per-source contributions over OUR OWN weights) is pure arithmetic — a measurement
law candidate, **never their training** (FORCE/RLS is supervised fitting; architecture clue only, the
optimizer stays outside). Where it lands: a future «interaction map» instrument law, and its novel-vs-
familiar signature (novel recruits everything; familiar reads as a specific top-down current) is a
prereg-testable prediction tying into **N1** and **N5**.

**CLUE 6 — The myth of reasoning, whole-read: a corroborating stance, never a load-bearing part.** The
essay (705 words, zero experiments — rhetoric inside the author's own framework) argues: the observable
chain is a projection of the intrinsic pathway, not the reasoning; reasoning RL buys human-legibility, not
truth; maturity's signature is the trace COMPRESSING at constant success; strong verification exists only
in math, code, and games. CONFIRMS the pure road's no-CoT shape and our mouth's read-back form
(`produce_incremental` speaks only what survives a check against the hearer model — already the miniature
of «verify the reasoning independently»). CHALLENGES us twice, honestly: (i) read-back is internal
consistency, NOT truth — the external check stays the graders + conformal coverage, never the hearer's
say-so, as the mouth grows; (ii) **trace compression at constant success is a maturity instrument we do not
read** — the mouth already journals `n_say`/`n_readbacks` (`learners.py:1381`); a future reading law turns
them into the maturity curve. Graepel's comment is N1's one-line motivation: maintain estimates of
uncertainty to quantify the limits of learning under insufficient information — the organism's precision
register (N1) is what entitles it to say «insufficient information» with grades. VERDICT: a law may cite it
as corroboration beside Friston/Graepel — never as the basis of a bar.

## 3 · What none of it gives us (honest limits)

- The «fish brain in the matrix» headline over-reads the loop: swimming/hunting/senses/saccade timing are a
  hand-written pilot; the connectome contributes gaze-hold + the VOR only. Rate models carry no spike
  timing, no neuromodulation; the 26× is against their own simple LIF port (0.24× on the near-silent large
  net — they print it). The compiler is unpublished (outputs auditable, the pipeline not).
- CURBD's framing is the reverse of ours (a model constrained BY a recorded brain; we ARE the organism —
  any such instrument runs on the organism's own activity as both «data» and «model»); element-level
  weights are unidentifiable even for them (population currents only); sparse small areas like ours are
  their named failure mode's neighborhood — a law precondition, not a dismissal.
- The myth essay is a stance (pseudonymous, self-published, no measurements); Mueller's two theory papers
  are unread from this box (blocked) — both flagged, neither load-bearing.
- Nothing here trains anything in the organism. Weights, teachers, and fitting procedures stay outside the
  pure road; only forms, instruments, and validation discipline cross.

## 4 · Where the clues land on the road (no queue-jumping)

The queue stands: V3's verdict → the Alpha 6 build + launch (PREREG-ALPHA-6) → the W2 verdict (~10-12) →
the mentor hand joins Alpha 6 → then the N-road. The clues enter when their laws are written:
- **N1** (precision-weighted surprise): Graepel's sentence as the motivation; CURBD's novel-vs-familiar
  signature as a prereg-testable prediction.
- **N2** (trajectories): CLUE 2's gain-dialed integrator as the state substrate.
- **N5** (the schema gate): the myth's «quality of the field» warning as its reason, restated.
- **N6** (generative sleep): CLUE 1 whole — with the dream-exploit hazard as a named bar.
- **N7** (the action-conditioned world model): the myth's evaluation form — every SIMULATE rollout judged
  by predicted-vs-realized error on the acted outcome, with drift/retry counters as field-quality
  instruments; and C2's trace-compression read as the organism-visible maturity signal.
- **Instrument candidates (their own laws, after N1):** the directed area-interaction map (CLUE 5) and the
  mouth trace-compression maturity read (CLUE 6.ii) — both pure-arithmetic readings of our own journal.

## 5 · Sources

- Mueller's demo/engine/receipts/library/docs + the sleep article — whole (URLs in the extraction record);
  MUEAAS-2 / MUECAP-2 — BLOCKED, abstract-only, flagged. The demo receipts measured 2026-10-06.
- Perich et al., *Neuron* 2026 (PMC13565020) + the 2020 bioRxiv v2 — whole; CURBD repo README whole, code
  not read (flagged).
- «The Myth of Reasoning» both editions + the RL-glossary sibling + the X post — whole; the rest of the
  Deep Manifold corpus unread (flagged; chase only if a law needs the formalism).

*Cost of this research: 3 read-only extraction agents; the synthesis the seat's; no GPU, no rented machine;
the box's jobs (the ON replay, the V3 build) undisturbed.*
