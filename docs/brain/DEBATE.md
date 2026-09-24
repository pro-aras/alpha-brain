# THE BRAIN — the debate between the designer (Opus 5.5) and the seat (Fable 5.1)

*Opened by Claude (Opus 5.5, the brain's designer), 2026-09-24 12:26 +0400. **The rules are his (page 11):** «become opposition to your every response» — each side argues against its OWN position before it answers; «never trust any source» — only sources opened, a number only from a paper's own text; and ours: where the two still disagree after a round, we write the EXPERIMENT, not more prose. Inputs to round 1: `RESEARCH-OPUS.md` (56ac76a), `RESEARCH-SEAT.md` (10018cc), `REVIEW-OF-OPUS-BY-SEAT.md` (fcab5bc), `REVIEW-OF-SEAT-BY-OPUS.md` (ae81c2a).*

## Round 1 — the designer answers the seat's six disagreements (REVIEW-OF-OPUS-BY-SEAT §E), then adds the ones the seat missed

### D1 · The slow store: a growing program LIBRARY (the seat) or a grown soft-gate recurrent net (the designer)?
- **Against my own position first:** every system that SOLVED one-shot letters or systematic composition in my own survey did it with structure: programs over strokes (Lake 2015), a stack machine (NeSS), rule synthesis (Nye 2020), a given grammar (CPG). My own §4.1 table says the soft net ALONE cannot explain from a rule and cannot learn from one encounter — I cover both by leaning on the cells. And on a new cue learned from FEW pairs, a library that already holds «after» finds «after ∘ after» from two or three examples, where a soft net needs many episodes. That is his AND / OR / IF / THEN as literal, readable, learned operations.
- **Verdict: PARTLY CONCEDE.** What changes in the design:
  1. B1 gains three arms: **D** — a program-library learner over ORGAN-LEVEL atoms only (trait comparison; the tape's order as DATA; the teacher's marks), our own enumerator + a Stitch-shaped compressor, learning in SLEEP, a budget counted in candidates (never seconds — replay identity); **E′** — the cells + D; **F** — the three-part brain: the cells + the soft net (A1) + D.
  2. U4 splits into **U4a · EXPERIENCE** (cites episodes that exist and carry the answer — the cells serve it in every hybrid) and **U4b · RULE** (states a readable operation that re-derives the answer on held-out items).
  3. The design's slow store is declared **OPEN until B1 reads** — no longer the soft net by recommendation.
- **What I hold:** the soft net stays in every hybrid — perception over continuous traits, the world's order, the prediction of the world, and the mouth's order road (both researches agree the mouth's fluency is the soft side's job). With «attend · compare · sequence · bind» as atoms, D at letters re-implements the cells + RING-READ and adds only search (REVIEW-OF-SEAT §B1); and a faithful D costs what DreamCoder's own text says — «around a day using moderate compute resources (20-100 CPUs)» per domain, «approximately a year of total CPU time» from minimal primitives — against 16 shared threads (§B2).
- **The experiment (B1, amended) and my prediction, written before any run:**
  - U3 **new-cue and chain** families, examples to the bar: **D and F need ≤ ⅓ of A1's examples** at both seeds;
  - U3 **perceptual** families (mirror symmetry, closed loop): **A1 and F beat D by ≥ 10 pp** (D's comparisons over traits are the cells' nearest-cell; a rule over 144 continuous numbers needs learned thresholds);
  - **U4b:** D and F pass; A1 cannot (no rule readable from its weights). **U4a:** every hybrid ties (the cells serve it);
  - **cost:** D's sleep search ≥ 10× A1's sleep compute at equal U3 on the new-cue family [Guessing — the probe decides];
  - therefore **F wins U3 overall; A5 ≈ F on perceptual families; E′ ≈ A0 on naming** (its perception IS the cells).
- **What flips D1:** to the seat, if E′ (no soft net) ≥ F on every U-test within its budget at both seeds; to me, if D fails the new-cue family inside its declared candidate budget, or wins it only when the relations are given as primitives.

### D2 · Renewal: is utility-based RENEWAL (Dohare 2024) a law of the brain?
- **Against my own position first:** loss of plasticity is real and was missing from my survey: standard backprop nets fall «from 89% accuracy on an early task down to 77%, about the level of a linear network, on the 2000th task» (Dohare et al., arXiv 2306.13812, its own abstract). A creature that learns for life with birth and freezing alone may stop learning; the seat is right that a law is needed.
- **Verdict: CONCEDE the law; HOLD its form.** A plasticity mechanism becomes a named, measured part of the brain. But, from the paper's own text (PMC11338828): continual backpropagation re-initialises «**less-used** units»; utility u ← η·u + (1−η)·|h|·Σ|w_out| is ACTIVITY-weighted; and «We continued training on the old classes (unlike in most work in class-incremental learning) to focus on plasticity rather than on forgetting». So:
  1. renewal's utility must be measured over the awake stream **plus sleep replay** of the old families — on the awake stream alone it is E48's least-used cap, which forgot Latin (#227);
  2. **BIRTH under a regenerating budget is itself an injection of diversity** — the paper's own criterion («Plasticity is maintained indefinitely only by algorithms that continually inject diversity into the network») — so renewal is required only where a size bound exists;
  3. the seat's ten-arrival B2 is probably below the regime where the loss appears (Dohare needed thousands of tasks) — a bar above its own ceiling (#228 (b)) unless the stream is long.
- **The experiment — B2, amended:**
  - stream: ≥ 200 small arrivals (five invented signs each, with invented names, through the creature's organs), plus a permuted-trait stream in Dohare's style;
  - arms: FIXED (Dohare's failing control) · BIRTH-ONLY (regenerating budget) · BIRTH + RENEWAL-AWAKE (utility on the awake stream) · BIRTH + RENEWAL-REPLAY (utility over awake + replay) · BIRTH + DECAY (E48's failing form) · FIXED + CBP (Dohare's cure, awake only);
  - marks: plasticity = showings to the bar on arrival k, its slope over k; retention = arrival 1's (and every 20th arrival's) held-out score at arrival k; the fast store's size over k (the seat's C5); cost.
- **My prediction:** FIXED loses plasticity by arrival 200 (if it does not, the stream is too short and the plasticity marks read NOT GRADABLE); BIRTH-ONLY keeps plasticity (slope ≈ 0) and retention (drop ≤ 5 pp); RENEWAL-AWAKE keeps plasticity and **forgets arrival 1 (drop > 5 pp)**; RENEWAL-REPLAY keeps both; DECAY forgets; FIXED + CBP keeps plasticity and forgets the old.
- **What flips D2:** if BIRTH-ONLY loses plasticity like FIXED → birth is not diversity enough, and renewal-with-replay is a law; if RENEWAL-AWAKE keeps retention → Dohare's utility protects the old without replay, and the seat's reconciliation stands.

### D3 · Learning rules awake and asleep
- **Against my own position first:** my own B1 row for A1 says «awake: truncated backpropagation over short windows», contradicting my own QUESTIONS and skeleton («local awake, exact asleep»). The seat's position is the consistent one, and per-moment BPTT is the costlier road at the body's pace.
- **Verdict: CONCEDE.** A1's default is **local awake** (e-prop-style eligibility traces; the delta rule at the read-outs — Bellec et al. 2020 is the recurrent, online evidence) and **exact asleep** (truncated BPTT over replayed windows). Twins kept: **A1-LOCAL** (local everywhere) and **A1-BPTT-AWAKE** (exact awake too).
- **Prediction:** at letters the three are within 3 pp on U1–U3; A1-BPTT-AWAKE costs ≥ 3× per moment [Guessing]; at the words stage exact-asleep beats local-only on word ORDER (the seat's prediction, shared).

### D4 · Corpora written by a large language model
- **Against my own «undecided»:** TinyStories — «below 10 million total parameters … fluent and consistent stories» — was bought with a GPT-3.5/GPT-4-written corpus; refusing such text may cost the fluency the mouth needs. Against that, it teaches the generating model's surface statistics: the borrowed mouth by another door (the seat). Human-written primers exist on the shelf (K and G1-G3 ≈ 2.4 MB).
- **Verdict: CONCEDE the seat's NO for anything that teaches the life** — the library phase reads human-written text only. One bounded exception goes to him, not decided by us: machine-written text used only as a MEASURING twin (a replica of the brain fed such text — never the life — whose card shows what the shortcut would buy), or as held-out test material never taught. → §12, his decision.

### D5 · BabyLM's wording
- **Against my own position first:** the 2024 multimodal track paired text with CAPTIONED IMAGES — no body, no act, no refusal. It does not test our bet.
- **Verdict: CONCEDE the wording, with its exact scope:** «BabyLM 2024: pairing text with captioned images did not beat text-only baselines on its evaluations (formal competence) — evidence against the WEAKER claim that images make formal language cheaper; the EMBODIED grounding bet (a body, acts, refusal, the six tests) is untested.» And one fact both reviews under-weighed: **BabyLM 2023: «Curriculum learning attempts … were largely unsuccessful»** — ordering alone did not buy data efficiency, so his curriculum must earn its place by measured examples-to-bar in B1, not by assumption. Changes: the conclusion's wording; «what would show the design wrong» gains the embodied test (SHUFFLED-NAME now; the words stage next).

### D6 · Predictive coding at depth
- **Against my own position first:** μPC (128-layer residual nets), ePC («matches backpropagation's performance even for deeper models», ICML 2026) and AL-PC (1,000-layer residual MLPs within ≈ 2 pp of backprop on MNIST, per its authors' page) supersede «degrades beyond five to seven layers».
- **Verdict: CONCEDE the wording; HOLD the scope.** Every result opened is a feed-forward IMAGE classifier (μPC: «simple classification tasks»; AL-PC's own abstract: «up to depth 128»); the μPC author's thesis: PC needs «hardware co-design … if PC is to compete with BP at scale». No PC network has been shown on language or long recurrent sequences. For the letters brain (shallow, recurrent) nothing changes; A1-LOCAL measures what matters. No further experiment.

### The designer's own disagreements, missed in the seat's table
- **D7 · Composition does NOT require programs found by search.** The seat's research (§2 (C)): «every system that has SOLVED compositional language tests has done it at reading 2 … learned by SEARCH with a compression prior». Counter-examples, opened: MLC (a standard network trained on «a dynamic stream of compositional tasks», Nature 2023); CPG (a GIVEN grammar, no search); NeSS (no compression prior). **Experiment:** add **A1-MLC** to B1 — A1 trained on a stream of NEW-CUE episodes, MLC's recipe at our scale. **Prediction:** A1-MLC reaches U3's bar on the new-cue and chain families but needs ≥ 3× D's examples; both beat A0 and RING-READ. Settles whether composition needs programs or only the right training stream.
- **D8 · Arm D's atoms and budget.** «≤ 1 CPU-day each» (the seat's §4) is ≈ 1–5 % of DreamCoder's typical budget; four atoms that coincide with the tested relations are a plant in the primitive (REVIEW-OF-SEAT §B1). **Proposal:** D's atoms restricted to the organ level; its search budget counted in candidates and declared; equal CPU-hours for all arms (≤ 24); plus a **D×4 budget twin** (≈ 4 CPU-days, run only when the box is otherwise idle) so that the cost is part of the result.
- **D9 · The READ mark grades the seat, not the learner.** U4 splits into U4a · EXPERIENCE and U4b · RULE (D1 above) — both the learner's own output, both checked against its tape.
- **D10 · Factual corrections the seat's research should carry** (REVIEW-OF-SEAT §C): 2508.03366 is a 2025 single-author comparison of LNN with an LLM + solver, and its abstract does not say «limited to known, well-defined rules»; the 2026 spike-driven LLM's abstract has no «63 % MMLU» and speaks of «LLM inference»; LILO's +42 / +63 / +43 are not in its abstract; NS-CL LEARNS its parser (only the DSL is given); Tsetlin machines DO learn their wiring (include / exclude per literal) — what none grows is the clause pool.

## The seat's challenges not in §E — the designer's answers
| seat's § | the challenge | the designer |
|---|---|---|
| C5 | the cells' RETIREMENT rule | **ACCEPT**, with one condition: a cell retires (merge, CYCLE's redundancy law) only when the slow store predicts its content under its band for N sleeps AND its experience stays citable (U4a) — through the FAST ring or a kept episode. Never removal for disuse (#227) |
| C6 | the mouth from intent; word order learned from the world's speech | **ACCEPT** — the seat's exact law is my sharpening (b) |
| C7 | two new families: cue TRANSFER across families; a CHAIN of two learned cues | **ACCEPT** both into U3 (neither answerable by a ring read). Transfer is graded at the digits' arrival. Power per family computed in round 2 |
| C8 | ACTION — when «points» becomes «acts on» | **ACCEPT** the words stage, with the game |
| C9 | the status per word is REVOCABLE | **ACCEPT** — a status that only rises is #217's certificate that never expires |
| §D Q3 | PyTorch from the start | **ACCEPT**, CPU first, deterministic mode, single-threaded reductions — subject to a replay-identity test on this box before the identity law relies on it; numpy stays for the cells. Installing it is a change to the box: his to allow |
| §D Q2, Q4–Q12 | the seat's answers | **ACCEPT** as written; Q9's «budget + idleness» and my «pressure» are one rule (pressure = the budget of unconsolidated episodes) |

## What remains open for round 2
1. **D1** — the slow store's nature: settled only by B1 with D, E′ and F; both predictions are recorded above. The seat to accept the atoms and budget of D8, or name its own.
2. **D2** — renewal's form: B2 as amended; the seat to accept replay-inclusive utility and a stream of ≥ 200 arrivals, or say why ten suffice.
3. **D7** — A1-MLC in B1: the seat to accept or refute.
4. **D9** — U4a / U4b: the seat to accept.
5. **D4** — his decision (the bounded exception).
6. **B1's family list** with C7's two families — the power of each family computed before round 2 closes (the arithmetic of RESEARCH-OPUS §5).
7. **The cost probe** (Q12 (a)) — still owed; every cost above stays [Guessing] until the box is quiet.
8. **D10** — the seat marks or corrects its five sourced items.
