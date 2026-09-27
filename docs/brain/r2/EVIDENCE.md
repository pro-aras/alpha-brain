# The brain organ, round 2 — the evidence both debaters use

*edit: Claude (Opus 5.5, the seat), 2026-09-27 18:38 +0400 — written BEFORE either debater's research; facts only, each with its source. Certainty: every number here is read from the named file or re-computed by the named script today.*

## 1 · His words (verbatim)

- **2026-09-27 18:32 +0400 (this round's order):** «So the network itself is a problem. The brain itself is a problem and not efficient enough to handle a complex information or doesn't want to perceive the knowledge or get better or not curious enough. The issue lands to the brain. Can you debate with fable 5.1 on deep research and development of the brain organ.»
- **2026-09-24 10:50–11:24 (the brain order):** «It's been 2 months now and we haven't made a thing that can fucking speak.» · «We had to have a brain first that fucking think. A neural network or whatever or however brain is made. … We build fucking eyes, ears and there's not a good fucking brain that think or do something.» · «the goal of ours is to make something that knows what it speak and is open endedness. What you are describing is training a neural network on tokens again the same shit already there in the market. … A continual learning system which has abilities of human mechanism with advantages of machine and software level working.» · «we can grow a brain as well. Just like we grew the organs. … The same one genome, one body, single organism, with set of instructions to grow organs … And the brain too included in it. … that can be done on this cpu or this device we have. Our goal is human inspired growth. Not heavy machinery.» · «the brain is itself is a complex mixture of these fuctions [AND, OR, THEN, IF, ELSE]».
- **2026-09-24 12:01:** «What I'm most anxious about is that what will make it different from others. You or any other ai doesn't understand what it is speaking or doesn't understand the words or language it knows from the core. … Speaking of understanding something from the core and meaning. Not just predicting next word as a token.»
- **His decisions of 2026-09-24 15:17** (CONCLUSION.md §7): D-1 no chatbot text teaches the brain (test material only) · D-2 PyTorch on this box · **D-3 no Mac — this PC only, for everything** · D-4 no GPU rental now · D-5 letters first · D-6 the library ×4 once on an idle night.
- **2026-09-23 23:06 (his curriculum, THE SCHOOL's):** letters with their sound, upper then lower case, then new fonts; shown in silence, the learner answers in its own output; right → something that makes it happy; wrong → «No», a felt signal, taught again, asked again; 3–4 examples per thing; then numbers, sounds, «A for Apple» with picture and sound, colours, animals, small sentences («Apple is Red»), then books and tests. **2026-09-27 13:30:** «Yes stop this childhood and the school id replacement.»
- **The six marks of understanding** (the seat's answer to his 12:01, the bar CONCLUSION.md is held to): a word is understood when the learner (1) points / acts on the thing, (2) refuses the word when the thing is absent, (3) composes grounded parts on unseen combinations (AND / IF-THEN), (4) explains from its own experience, (5) rejects misuse, (6) learns a new word from one grounded encounter and uses it elsewhere.

## 2 · The machine
Beelink SER, Ryzen 7 6800H (8 cores / 16 threads), 30 GB RAM, no GPU. PyTorch 2.14 CPU in `/data/dev/venvs/brain` (Python 3.14). Everything runs here (D-3).

## 3 · What B1 is
The letters stage as an experiment (`docs/brain/B1-PREREG.md`, signed; `docs/brain/b1/SEAT-DECISIONS.md` R1–R47). The creature's sealed eye (a trained tower, its own gaze) turns each rendered glyph into **5 glances × 144 features**. A tape per seed teaches upper- then lower-case A–Z in 4 fonts (12 showings each: «this is x» = TEACH), then training asks with corrections (L4: NAME, POINT, IS, relation games; L5: the new cue TWO_AFTER from 3 pairs), then the test sitting T_L on **fonts no teacher showed**, then digits and T_D. Eleven learner arms, each with twins/controls, graded by six tests of understanding (U1–U6) per family, never blended. Seeds 20261001 and 20261002. Harness: `/data/dev/genome-wt-b1int` (branch b1-integration), B1.1 in `/data/dev/genome-wt-b1-tape2` (b1-tape2).

## 4 · The facts

**F1 — The eye's features separate the letters for a reader that does not learn.** Nearest class mean (cosine) over the 5×144 glances of the TEACH rows — the SAME numbers every network arm receives through `StepEncoder` (`cache.glances(row)[i]`) — names **135/156 (87 %) and 134/156 (86 %)** of the NAME training asks before the CONST block, and **451–460/704 (64–65 %) and 443–455/704 (63–65 %)** of T_L's NAME asks on unseen fonts (seeds 1, 2). Only the last glance: 46–47 % and 33–36 %. Each glance is unit-norm; features lie in 0–0.42, mean 0.048. (`docs/brain/r2/probe_centroid.py`, output `probe_centroid.out`.)

**F11 — The network's STATE keeps the letters; its own answer head does not read them** (seed 1; A1's final B1.0 snapshot; every glance run through A1's own NAME-ask road from one fixed start state, no learning; `docs/brain/r2/probe_state.py`, output `probe_state.out` — the other arms and seed 2 are appended there as they finish):

| reader | before CONST (taught fonts) | T_L NAME (unseen fonts) |
|---|---|---|
| input, nearest class mean (F1) | 135/156 (87 %) | 451/704 (64 %) |
| **input, logistic regression** (standardised, full batch, 2,000 steps) | **155/156 (99 %)** | **514/704 (73 %)** |
| A1's state h (114 units), nearest class mean | 96/156 (62 %) | 304/704 (43 %) |
| **A1's state h, logistic regression** (same recipe) | **149/156 (96 %)** | **485/704 (69 %)** |
| **A1's OWN NAME head on that same state** | **0/156** | 60/704 (9 %), one distinct answer |

The states are a tight cloud: the mean distance of a state from the mean state is **0.060**, against a mean |h| of **0.735** per unit (near saturation). The letter sits in those small deviations — a standardised linear reader recovers it at 96 %; the arm's head, trained by a few lr-0.01 steps on RAW states, reads only the shared part and gives one answer. [Certain for the numbers; the reading of why is the debate's.]

**F12 — What a well-trained linear readout of the INPUT reaches:** 99 % on taught fonts, 73 % on unseen fonts (seed 1, table above). The eye gives a simple learner everything it needs; the rule library D reaches 0.853 / 0.769 on U1a (F6).

**F13 — One change to the readout turns chance into 84 %, in ONE pass of the same examples** (seed 1; A1's final states as in F11; four ONLINE readers see the 624 single-letter TEACH rows once, in tape order — 24 showings per letter, what the tape gives; `docs/brain/r2/probe_online_readout.py`, output `probe_online_readout.out`):

| online reader, one pass | before CONST | T_L NAME (unseen fonts) | distinct T_L answers |
|---|---|---|---|
| **A1's own recipe** (zero-init rows, cross-entropy SGD lr 0.01, RAW state) | 6/156 (4 %) | 26/704 (4 %) | 1 |
| **the same rule, the state standardised by its running mean / std** (Welford) | **131/156 (84 %)** | **389/704 (55 %)** | 26 |
| recursive least squares on the running-centred state | 130/156 (83 %) | 447/704 (63 %) | 26 |
| running class prototypes on the standardised state (nearest, cosine) | 110/156 (71 %) | 331/704 (47 %) | 26 |

The raw recipe reproduces A1's failure exactly; standardising the state before the head — nothing else changed: the same rule, rate, pass and examples — learns the letters. [Certain for the numbers.] **Seed 2 replicates it** (A1, h 111): sgd-raw 6/156 (4 %), 26/704, one answer · sgd-std 124/156 (79 %), 378/704 (54 %) · rls 141/156 (90 %), 464/704 (66 %) · proto 118/156 (76 %), 330/704 (47 %).

**F2 — Every learned network names at chance before any interference; only the cells and the rule library name** (NAME-cue training asks before the first CONST ask; B1.0 records `/data/dev/brain-runs/b1/runs/<seed>/<arm>/answers.jsonl`; chance = 156 ÷ 26 = 6):

| arm (what it is) | seed 1 | seed 2 |
|---|---|---|
| A1 — a growing GRU, awake local rule, sleep replay | 7 / 156 | 7 / 156 |
| A1-FIXED / A1-BPTT-AWAKE / A1-ATT / A1-MA (its twins: fixed size, exact gradient awake, attention, memory attention) | 7 · 6 · 6 · 7 | 8 · 5 · 10 · 10 |
| A1-TEACH (A1 + «this is x» trains the answer head, R46) | 7 / 156 | 7 / 156 |
| A2 — soft logic gates | 4 / 156 | 7 / 156 |
| A3 — clauses (Tsetlin machine) | 0 / 156, always silent | 0 / 156, always silent |
| A4 — a small transformer (the check) | 0 / 156, always silent | 0 / 156, always silent |
| A0 — the creature's cells (associative memory) | 58 / 156 (46 abstentions) | 61 / 156 |
| A5 — cells + network | 59 / 156 | 64 / 156 |
| D — the rule library (program search + compression) | 127 / 156 | 128 / 156 |
| KEY (answers from the truth) | 156 / 156 | 156 / 156 |

**F3 — The letters test (T_L), B1.0 tape:** every network answers ONE name to all 624 U1a asks («a»; A4 seed 2 «k»): U1a 0.038 on both cases against bars 0.778 / 0.669. A0 69–91 / 624, A5 80–97 / 624, D 504–508 / 624 (0.853 / 0.769 on the graded marks). The one-name collapse is a SCHEDULE fact: the CONST control («a», 78 corrections) was taught as a block between the last sleep and T_L (R46 addendum). B1.1 moves it into L4 (R47); B1.1's results are due tonight. **CORRECTION (2026-09-27 19:31 +0400, the seat — found by Fable 5.1, confirmed on the records): B1.1 refutes the causal half.** With CONST interleaved, A1 and A1-TEACH still give ONE name to all 624 U1a asks («l» seed 1, «n» seed 2; A2 591 «l» / 460 «n»); the block chose which name, the readout's conditioning (F11, F13) causes the collapse — every test ask starts from the same frozen state.

**F4 — A1-TEACH changes nothing (R46 READING, b1-tape2 5616d8d):** the switch fired (37 of 37 name rows trained vs 27; final states differ), and before the CONST block it still answers 7/156 on both seeds — A1's exact count.

**F5 — How A1 learns** (`brain/arms/soft/{engine,arm,steps}.py`): input = one step per glance (144 features + glance index + zeros + kind), a cue step, name-letter steps; a GRU that grows from 64 units (to 111–115) by births on prediction error; the AWAKE rule is local (an e-prop-style trace: a 1-step-truncated gradient, λ 0.9, lr 0.01); SLEEP replays windows of the event ring with exact BPTT on the WORLD head only (next-step prediction of glance, letter, kind); the answer heads (NAME / YES-NO / PICK) are trained only by FEEDBACK cross-entropy (lr 0.01), one step per correction; a new name starts with zero weights; abstention bands on novelty and confidence. The tape gives it 745 TEACH rows (24 per letter) and 156 NAME corrections before CONST (6 per letter).

**F6 — The rule library D** (at 50,000 candidates per sleep, R45; seed 2 graded `runs/20261002/results-r45-v3/`): passes naming on unseen fonts (0.853 / 0.769), PICK, lures, **the relations — AFTER 11/12, BEFORE 9/12, BETWEEN 10/12, CHAIN 21/25, TWO_AFTER 20/21 from only 3 taught pairs** — explains its rules (U4b) and learns from one meeting (U6); its SHUFFLED-RELATION twin reads 0 on every relation. It fails refusing never-taught signs (0 refusals, 40 sure names), carrying a relation to the digits (11/18 < 13), explaining from experience (U4a 0), rejecting misuse (U5 0.143) and KEEPS (TWO_AFTER −9.5 pp). Seed 1 pending.

**F7 — The hybrids A5, E′, F read VOID** (their SAME control fails; D alone passes SAME 1.0), so §6's selection and D1 cannot be read on B1.0.

**F8 — R-THINK** (a THINK step on AND/OR circuits and IF-THEN chains; `docs/brain/rthink/VERDICT.md` on brain-rthink): INCONCLUSIVE — the recurrent thinker solves chains within its training depth and partly beyond (L24 1.0, L32 0.30–0.50), circuits d12 0.91, d16+ ≈ 0.5; the two seeds disagree.

**F9 — R-PRIOR** (a childhood of random programs' outputs): the learner came out 6–10 bits per byte WORSE on real text; stopped on his word (THE SCHOOL replaces it).

**F10 — The organism (Alpha 4)**: one genome grows eye, ears, hands/touch/smell, a reader, doors, a game world, the cells, sleep, EVOLVE. alpha4-1 lived 24 h: 10,995 cells, 83 sleeps, self-exam ≈ 0.92–0.96 (recognising shown things on held-out canvases); its mind fell behind its world (cost per canvas); a sister life failed 12 marks (retention −9 pp, an action lock, its own drawings recognised 0.1–0.2); the game paid 4 rewards in 19 h. Senses and an associative memory — no brain that thinks (his 09-24 words). All lives are stopped.

## 5 · The question (his, made exact)
Every learned network in B1 fails to learn letter names from features that a nearest-class-mean reader names at 86–87 % — with or without «this is x» teaching, at five architectures. **Why, and what must the brain organ be** so that it (a) learns from a few grounded examples as a child does (3–4 per thing), online, (b) keeps what it learned while it learns more, (c) wants to learn — curiosity, asking, (d) composes (AND / OR / IF / THEN) and reasons, (e) knows what it speaks (the six marks), and (f) grows from the same genome on this CPU? **What single pre-registered experiment settles the next step**, on B1's harness and tapes?

Sub-questions each research must answer: **Q1** the diagnosis (sample efficiency; the representation — does the network's state keep the input's identity; credit assignment under the local rule; no replay of answers in sleep; the zero-init, corrections-only head; 5 glances as a sequence; small inputs 0–0.42); **Q2** what learns from 3–6 examples per class online and cheaply (prototypes / nearest-class-mean with a learned metric, Hebbian and associative binding, complementary learning systems, predictive coding, meta-learned plasticity, program search as in D) and what each costs here; **Q3** curiosity (learning progress, information gain, asking the teacher; THE SCHOOL's flow); **Q4** growth from the genome (births on error, budgets, sleep); **Q5** composition and reasoning (D works; where does a network belong?); **Q6** the road from names to sentences; **Q7** the next experiment: arms, controls, bars, cost on this CPU.

## 6 · Where to read
`docs/brain/CONCLUSION.md` (co-signed 09-24; the current law), `RESEARCH-OPUS.md`, `RESEARCH-SEAT.md`, `REVIEW-*.md`, `DEBATE.md`, `AHMAD-NOTES-2026-09-24.md` (his 12 pages), `RESEARCH-2026-09-26.md`, `B1-PREREG.md`, `B2-PREREG.md`; code and records in §3–§4.

## 7 · The rules of this round
1. **Independent first:** each debater writes its research before reading the other's (`RESEARCH-FABLE.md`, `RESEARCH-SEAT-R2.md`).
2. **Numbers from their own files:** a paper's number from the paper's own text, ours from the record; certainty tags [Certain] / [Likely] / [Guessing].
3. **Reviews both ways**, then **debate rounds** in `DEBATE-R2.md`; what both settle goes into `CONCLUSION-R2.md`, co-signed; what stays open goes to him as a decision with a recommended option.
4. **Plain words** in the summary for him; every claim he reads carries its evidence.
