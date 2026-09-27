# The brain organ, round 2 — the seat's research

*edit: Claude (Opus 5.5, the seat), 2026-09-27 19:00 +0400 — written INDEPENDENTLY: before opening Fable 5.1's `RESEARCH-FABLE.md`. Sources: `EVIDENCE.md` F1–F13 (our record, re-computed today) and the literature named in §9. Paper ids are cited from memory unless marked read today; no paper NUMBER is quoted, only its idea — the review checks every id.*

## In plain words (for Ahmad)
1. **The brain does see the letters.** Inside its memory the letters are all there: a simple reader pulls them out at 96 %.
2. **Its "answer" part could not read them.** Every state carries a big shared background signal and only a tiny letter signal. The answer part learned the background and gave one answer to everything.
3. **One fix, the one real neurons use:** subtract the background and scale the rest (normalization). Same brain, same few examples, one pass: from 4 % to 84 % on taught fonts.
4. **So it is not lazy and not unable. It was deaf in one place.** Curiosity, growth and composition come next, but this block comes first.
5. **The next experiment** puts that fix into the real brain arms on the fixed B1.1 tape, both seeds, with controls, tonight-sized.

## Q1 — the diagnosis

**The finding** (F11, F13; seed 1, A1's own final states):
- a standardised linear reader decodes the letter from A1's state at **96 %** (taught fonts) and **69 %** (unseen);
- A1's own head, on the same states, answers **0/156**;
- A1's own learning recipe, replayed as one online pass over the tape's 624 «this is x» rows on those states, reproduces the failure (**4 %**, one answer);
- the same recipe on the standardised state reaches **84 % / 55 %**.

**Why** — ranked, with the evidence for each:
1. **Ill-conditioning of the readout — the cause** [Certain for the effect, Likely for the full account]. Each state is a large common vector (mean |h| 0.735 per unit, near saturation) plus a letter-specific deviation of size ≈ 0.06 (the mean distance from the mean state).
   - A cross-entropy step moves every class row by (p − y) ⊗ h. That is almost entirely along the common vector, the same direction for every letter.
   - Every class row therefore grows along one shared direction. The class updated most, or most recently (the CONST block's «a» at T_L, whatever came last before it), wins every input, because every input is nearly the same vector.
   - Discriminating learning runs at roughly (0.06 / 0.735)² ≈ 1/150 of the rate the common part gets. With 6 corrections per letter at lr 0.01, it never starts.
   - This is the textbook case for centring and scaling a learner's inputs (LeCun et al. 1998) and the reason normalisation layers exist (Ba et al. 2016). In brains, divisive normalisation and homeostatic scaling do the same job (Carandini & Heeger 2012; Turrigiano 2008).
   - F13 isolates it: nothing but the standardisation changed, and chance became 84 %.
2. **Too few effective updates** [Likely a second-order factor]. One pass, one small step per example. RLS — the exact online least-squares solution from the same one pass — reaches 83 % / 63 %, about the same as standardised SGD on taught fonts and better on unseen fonts. So once the readout is conditioned, the number of examples is enough (24 per letter). A child-like 3–4 is the next bar, not this one.
3. **The state's generalisation to unseen fonts** [Likely the ceiling]. Even the offline ceiling on the state is 69 % unseen against 73 % on the raw input, so the representation loses a little. The rule library reads 0.853 / 0.769 on U1a. This bounds what any readout of A1's state can do on U1a; it must be computed per case against the bars before a new pre-registration (#228 (b)).
4. **Not the cause:**
   - truncated credit assignment — the exact-gradient twin A1-BPTT-AWAKE fails the same way, with the same 0.060 spread;
   - recency over 5 glances — the standardised reader of the same 5-glance state works;
   - «no curiosity» — the tape gives every arm the same asks;
   - small input values (0–0.42) — they matter only through the conditioning above.
5. **The other networks** (A2 soft gates, A3 clauses, A4 transformer) share the step encoder and a corrections-driven readout. The same conditioning is the first suspect for A2 [Guessing until probed]. A3 and A4 never answered before CONST (always silent), so their abstention bands reject everything. That is a separate defect in their own code, to be probed the same way.

**The measurement that separates the top two:** already made (F13): standardised SGD (conditioning fixed, one small step) against RLS (conditioning fixed, the exact solution). Both succeed, so conditioning dominates. Seed 2 and the arms' own twins are running (`probe_online_readout.out`).

## Q2 — what learns from a few grounded examples, online, on this CPU
Four families, all cheap here (the state has H ≈ 110 units):
- **A normalised readout** (running mean / variance per unit, Welford; then any linear rule). Cost O(H) per event. It is the smallest change that works (F13). Biologically it is homeostasis: each unit keeps its own firing statistics.
- **Recursive least squares** on the centred state. The FORCE principle: a fixed recurrent network plus a readout trained online by RLS (Sussillo & Abbott 2009). It is the classic reservoir readout (Jaeger 2001) and the fastest online linear learner. Cost O(H²) per labelled event ≈ 12k multiply-adds: microseconds. It learns from one pass (F13: 83 % / 63 %).
- **Prototypes:**
  - a running class mean of the normalised state, answer = the nearest (Snell et al. 2017; iCaRL's nearest-mean-of-exemplars, Rebuffi et al. 2017);
  - one-shot by construction: a new name is born as its first example, the network's own «imprinting» of U6;
  - weaker here than RLS (71 % / 47 %) because the cosine prototype ignores the within-class shape.
- **The cells and the library.**
  - The cells (A0) are one-shot but generalise poorly to new fonts (11–15 % on T_L).
  - The library (D) composes and names at 77–85 % but costs ≈ 110 ms per event and cannot refuse (0 refusals).
- **The brain these make.** Complementary learning systems (McClelland et al. 1995; Kumaran et al. 2016):
  - a FAST store (the cells: episodes, one-shot);
  - a SLOW learner (the network: a representation grown by prediction error);
  - a readout that learns fast from few examples because it is normalised (and RLS or prototypes where one pass must be enough);
  - sleep consolidating labelled episodes from the fast store into the slow readout;
  - the library holding rules.
  
  The record now supports this partnership with each part in the right role. CONCLUSION.md had them backwards (§8).

## Q3 — curiosity (his «not curious enough»)
- **In B1 the tape is fixed:** the learner cannot choose what it sees, so «not curious» is not what failed. Curiosity has two homes.
- **In sleep:** replay chosen by learning progress or error (prioritised replay, Schaul et al. 2015; learning-progress curiosity, Oudeyer, Kaplan & Hafner 2007). The brain revisits what it is improving on, not a uniform sample. It is measurable as a twin (uniform against progress-prioritised replay, the same budget).
- **Awake, in THE SCHOOL:** the learner ASKS when its confidence is low (active learning; Settles 2009), and the teacher answers in his flow (right → reward; wrong → «No» + the felt signal + teach again). The grade: the share of its questions that land on its weakest items, and the examples-to-bar with asking against without.
- **Both need the readout fixed first.** A learner whose confidence is meaningless (0/156 answered at 97 % confidence, F3/F11) cannot know what it does not know.

## Q4 — growth from the genome
- **The representation keeps E48's laws:** births on prediction error under a regenerating budget, no disuse decay, delta rule on the wrong.
- **Two new genes, both «like the organs»:**
  - **HOMEOSTASIS** — every readout reads its inputs through per-unit running statistics (mean and variance), updated awake and frozen in sittings. It is state of the organ, persisted and hashed like any other.
  - **IMPRINT** — a new name's readout row is born from its first grounded example (the normalised state it was heard with), never from zero. The law «a name is not guessable before it is heard» still holds: it is born only when heard.
- **Sleep consolidates the answers too:** the labelled episodes the cells hold are replayed through the readout, not only the world head.

## Q5 — composition and reasoning (his AND / OR / IF / THEN)
- **The rule library is the only learner that composed on the tape:** AFTER 11/12, BEFORE 9/12, BETWEEN 10/12, CHAIN 21/25, TWO_AFTER 20/21, and its shuffled twin reads 0 (F6). Its DSL is his list made concrete (conjunction, conditionals, order).
- **The network's role in composition is to deliver the grounded symbols** — names, cases, shapes — fast and reliably, so the library's programs run on the network's perceptions rather than on a cache read.
- **The hybrids (A5, E′, F) must be repaired before they can be judged:** they fail SAME while D alone passes it (F7). That is a routing defect, found and fixed test-first before B1.2's hybrids run.
- **R-THINK stays INCONCLUSIVE.** A think step is not the bottleneck until the brain can name.

## Q6 — from names to sentences
- **The road, each stage one declared experiment on THE SCHOOL's flow:**
  - **letters** (B1: names + relations);
  - **arrivals without forgetting** (B2);
  - **words** (B3): a word is a letter sequence bound to a thing — the cells bind it, the network recognises it, the library holds its spelling;
  - **small sentences** — a relation over grounded things, IS(apple, red), held by the library, grounded by the network's recognisers, spoken by the mouth only after it reads its own sentence back (adopted 09-26).
- **It never predicts the next token.** It predicts the world and says the relation it holds, so each sentence can be checked against the six marks.
- **Honest distance:** we are at stage 1. Sentences are at least three declared experiments away. No date is promised.

## Q7 — the experiment: B1.2 «READOUT» (to be pre-registered after the debate)
- **Question:** does the brain's network learn to name — and then compose — once its readout is normalised, on the fixed tape (B1.1), at both seeds?
- **Pre-flight gate (before any arm is built):** the F13 probe replicated on B1.1's A1 states at both seeds.
  - The standardised one-pass reader must reach ≥ 70 % on taught fonts.
  - The per-case offline ceilings (F11's logistic reader on the state, U1a's own items) are computed and printed beside the U1a bars (0.778 / 0.669).
  - A bar above its ceiling is not declared (#228 (b)).
- **Arms** — all A1's engine, representation and laws unchanged, B1.1 tapes, both seeds:
  - **A1** (B1.1's own record — the control);
  - **A1-NORM:** the heads read the running-standardised state; everything else A1;
  - **A1-NORM-TEACH:** + R46's switch (TEACH trains the head) — F13's recipe in the live arm;
  - **A1-NORM-RLS:** the heads learn by RLS on the centred state from every labelled event (TEACH + FEEDBACK);
  - **A1-NORM-TEACH-IMPRINT:** + a new name's row born from its first example.
- **Twins:** SHUFFLED-NAME (U1's grounding null), SHUFFLED-RELATION (U3's null), FORCED (U2/U5's null) for every new arm. The identity control: every switch off ≡ A1, byte for byte.
- **Positive controls:** the F13 probe on each arm's own final states (the online reader must be within 10 pp of the arm's live U1a on taught fonts, or the arm's live road differs from the probe's). A planted toy: a TEACH-only stream where A1's head does not move and A1-NORM's does.
- **Bars:** B1's U1a–U6 as declared. The decision — **the network is REINSTATED** as a learner if an A1-NORM arm passes U1a above its SHUFFLED-NAME twin at both seeds. The hybrids get the fix in the next declared step; their SAME defect is fixed first.
- **Cost:** normalisation O(H), RLS O(H²) per labelled event; A1 runs 11–34 ms per event against the 307 ms bar. ≈ 4 new arms × 4 runs (arm + 3 twins) × 2 seeds ≈ 32 runs × ~1.5 CPU-h ≈ 48 CPU-h — one night at 12 in parallel.

## §8 — where I now disagree with CONCLUSION.md (co-signed 09-24)
1. **The roles.** It made the network the fast front and the library a measured passenger. On the record the library is the only learner that names and composes from the tape's few examples. The network is slow and, until its readout is normalised, deaf. The partnership stands with the roles corrected (Q2).
2. **The laws.**
   - «Local awake / exact asleep» is not what failed: the exact-gradient twin fails too.
   - Two laws are MISSING: HOMEOSTASIS (normalised readouts) and IMPRINT (a heard name is born from its example).
   - Sleep must consolidate answers, not only the world.
3. **Measure the readout before the architecture.** Five architectures were compared in B1 while none of them could read its own state. The first gate of every future brain arm is F11 + F13 on its own states (a ceiling and a one-pass reader), before any architecture question is asked.

## §9 — references (ids from memory, to be checked in review)
- LeCun, Bottou, Orr & Müller 1998, «Efficient BackProp» (centring inputs; conditioning).
- Ba, Kiros & Hinton 2016, «Layer Normalization», arXiv:1607.06450.
- Carandini & Heeger 2012, «Normalization as a canonical neural computation», Nat Rev Neurosci 13:51.
- Turrigiano 2008, «The self-tuning neuron: synaptic scaling of excitatory synapses», Cell 135:422.
- Jaeger 2001, «The "echo state" approach…», GMD Report 148.
- Sussillo & Abbott 2009, «Generating coherent patterns of activity from chaotic neural networks», Neuron 63:544 (FORCE, RLS).
- Snell, Swersky & Zemel 2017, «Prototypical Networks for Few-shot Learning», arXiv:1703.05175.
- Rebuffi, Kolesnikov, Sperl & Lampert 2017, «iCaRL», arXiv:1611.07725.
- McClelland, McNaughton & O'Reilly 1995, Psychological Review 102:419.
- Kumaran, Hassabis & McClelland 2016, Trends Cogn Sci 20:512.
- Schaul, Quan, Antonoglou & Silver 2015, «Prioritized Experience Replay», arXiv:1511.05952.
- Oudeyer, Kaplan & Hafner 2007, IEEE Trans Evol Comput 11:265.
- Settles 2009, «Active Learning Literature Survey», UW–Madison TR 1648.
- Bellec et al. 2020, Nat Commun 11:3625 (e-prop).
- Dohare et al. 2024, «Loss of plasticity in deep continual learning», Nature 632:768.
- Ramsauer et al. 2020, «Hopfield Networks is All You Need», arXiv:2008.02217.
- Lake, Salakhutdinov & Tenenbaum 2015, Science 350:1332.
- Ellis et al. 2021, DreamCoder, arXiv:2006.08381.
