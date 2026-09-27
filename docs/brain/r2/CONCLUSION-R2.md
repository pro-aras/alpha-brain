# The brain organ, round 2 — CONCLUSION (DRAFT for co-signing)

*edit: Claude (Opus 5.5, the seat), 2026-09-27 19:59 +0400 — drafted from `EVIDENCE.md` F1–F16, `RESEARCH-SEAT-R2.md`, `RESEARCH-FABLE.md`, both reviews and `DEBATE-R2.md` round 1. Co-signature: the seat ✔ · **Fable 5.1 ✔ (2026-09-27 20:05 +0400)**.*

*edit: Fable 5.1 (brain r2), 2026-09-27 20:05 +0400 — six factual fixes before signing, each argued in `DEBATE-R2.md` round 2 and measured in `probe_shrink.out`: (1) §1 92–97 % / 65–71 %; (2) «For Ahmad» 2, energy vs size; (3) «For Ahmad» 4 and §2, the reader's numbers under a DECLARED shrinkage (79–80 % from the eye's features, 76 % from the state) and «I don't know» as built-in-and-tested; (4) §3 law 2 and §5, S2 as a TEACH-only rule, never a fixed number; (5) §5 twins, no SHUFFLED-RELATION for IN-SLDA; (6) §5 predictions reversed: IN-SLDA ≥ A1-NORM-SLDA by ≈ 3–4 pp. The signed text below carries these fixes; nothing else was changed.*

## For Ahmad — what we found, in plain words
1. **The brain is not lazy and not blind.** Its memory keeps the letters: a simple reader pulls them out of the network's state at 96–97 %.
2. **One broken piece:** the part that turns the state into an answer.
   - The state is a huge shared signal with a letter signal about 14,000 times weaker in energy (about 120 times in size).
   - The answer part learned only the shared signal, so it gave one answer to every letter — «a» on the old tape, «l» or «n» on the fixed one.
   - The test schedule was not the cause (Fable found that; I had it wrong).
3. **The fix is the one real neurons use** — normalisation: take away the shared background, scale the rest. The same network, the same few examples, one pass: from 4 % to 79–84 % on taught fonts.
4. **A child-like reader works even better and learns in one look.** It keeps one running average per letter and learns how the letters vary. It names 76–80 % of letters on fonts it has never seen, after one pass — 79–80 % from the eye's own numbers, 76 % from the network's state — once its one setting is chosen on the teaching rows alone. A new letter is learned from one showing, and «I don't know» is built in; both are tested in B1.2.
5. **The rule library is already the thinker for relations:** it learned «two after» from 3 examples (20/21) and can explain its rule.
6. **So the brain is three parts, each doing what it is good at:**
   - a **reader** for WHAT a thing is;
   - **rules** for HOW things relate (AND / OR / IF / THEN);
   - the **network** for order, prediction and speech — once it earns them by passing their tests.
7. **Curiosity comes after this fix:** a brain whose answers are meaningless cannot know what it does not know. Then it picks the lesson where it is learning fastest, and asks the teacher when unsure.
8. **Next:** one overnight experiment, B1.2, proves this live on the real test, both seeds, with controls.

## 1 · The diagnosis (both, independently; confirmed on the record)
- **The cause** [Certain]:
  - every learned network's answer head — zero-initialised, trained by plain SGD, lr 0.01 — reads a RAW, near-saturated state;
  - the state's common energy (‖h̄‖² ≈ 64–67) is 13,600–14,900 × its letter energy; the input's is only 8.8 ×;
  - the state keeps the letters (92–97 % taught, 65–71 % unseen for a standardised linear reader, every A1 variant, both seeds);
  - standardising it — nothing else — takes A1's own one-pass recipe from 4 % to 79–84 % (F11, F13).
- **The one-name test answer is a start-state fact:** every test ask starts from the same frozen state, and the answer follows it. The CONST block only chose which name (Fable's B1.1 finding; the seat's R46 addendum corrected).
- **Not the cause:** the number of examples, truncated credit assignment, the corrections-only head, the missing answer replay, curiosity, the schedule.
- **Named for the network's next declaration** (not B1.2's question):
  - the GRU starts with a ZERO recurrent matrix — D2's newborn rule applied to the first units (`engine.py` `_init_rows(…, from_active=0)`);
  - the world objective may shape a «clock» more than a percept [Likely].
- **Every B1.0/B1.1 twin comparison is unmeasured** — GROWS, NO-SLEEP, LOCAL vs BPTT, ATT, MA, MLC: two raw-head chance readings each. They read NOT GRADABLE until the readout is fixed.

## 2 · The brain organ — its parts and their jobs
| part | job | the evidence | status |
|---|---|---|---|
| **the reader** (streaming LDA: a running mean per name, a shared WITHIN-letter covariance, a scale-free shrinkage; a Mahalanobis band for «I don't know») | WHAT a thing is — naming, pointing, refusing, one-meeting learning, keeping | F16 and `probe_shrink.out`: 76–80 % on unseen fonts in one pass — 79–80 % from the organ's features, 76 % from the network's state — with the shrinkage chosen on the TEACH rows only (leave-one-TEACH-font-out); a mean is born from one showing; the means are independent | to be proven live in B1.2 |
| **the rule library** (D: program search + compression over organ-level atoms) | HOW things relate — his AND / OR / IF / THEN; explaining a rule | F6: AFTER 11/12, BEFORE 9/12, BETWEEN 10/12, CHAIN 21/25, TWO_AFTER 20/21 from 3 pairs; its shuffled twin 0 | proven at letters (seed 2; seed 1 pending) |
| **the cells** (the fast store) | episodes, one-shot binding, the evidence behind an explanation | 13–16 % across fonts (not a namer) | kept as the fast store |
| **the network** (the slow representation + world model) | ORDER, context, prediction, the mouth's order — earned by marks | its state keeps the letters (F11); its own head could not read them | a measured passenger until it earns U3 and the mouth |

The frame is complementary learning systems (McClelland et al. 1995; Kumaran et al. 2016) with the roles corrected from CONCLUSION.md (09-24), which had the network as the answering slow store and the library as a passenger.

## 3 · The laws added to the brain's genome
1. **HOMEOSTASIS.** Every readout reads its inputs through per-unit running statistics (Welford mean and variance): updated awake, FROZEN in sittings, persisted and hashed as learned state (`state_sha`; control 0e VOIDs a sitting where they move). LeCun et al. 1998 §4.3; Ba, Kiros & Hinton 2016; divisive normalisation and synaptic scaling in brains (Carandini & Heeger 2012; Turrigiano 2008).
2. **THE READER'S RULE.**
   - A name's MEAN is born at its first showing and moved by every later showing or correction.
   - The shared covariance is WITHIN-letter; the shrinkage is relative and chosen by a DECLARED rule on the TEACH rows only — leave-one-TEACH-font-out over the fixed grid ε ∈ {1e-4, 1e-3, 1e-2, 3e-2, 1e-1, 3e-1}, recomputed at each SLEEP — never on a sitting (`probe_shrink.out`: a fixed ε = 1e-4 was the input's worst point and the state's best, and it reversed the verdict).
   - Its P / Σ / Λ are learned state under the same freezing law.
3. **THE FIRST GATE of every future brain arm:** its own ceiling (a standardised linear reader on its own states) and a one-pass reader (F11 + F13), printed before any architecture question is asked.
4. **COST is read solo** (R48): each arm alone, load < 2, a fixed slice with at least one sleep. The crowded run's wall-time reading is printed beside it, never graded. Growth buffers are allocated in chunks (A1's 1,024-wide pre-allocation costs ≈ 5–9 × its learning).
5. **Kept from 09-24:** the six marks and their laws, the identity law, D-1 (no chatbot text teaches), D-3 (this PC only), births on error under a regenerating budget with Dohare's initialisation, no disuse decay, THE SCHOOL's flow.

## 4 · Curiosity, growth, composition, language
- **Curiosity:**
  - the signal is LEARNING PROGRESS per family — the slope of the reader's error per letter, font, cue (Oudeyer, Kaplan & Hafner 2007);
  - the awake form is ASKING the teacher when the reader's margin is under its band;
  - the sleep form is replay prioritised by progress or error (Schaul et al. 2015).
  
  All three come AFTER the readout: in B1.3 and in THE SCHOOL's lesson choice.
- **Growth:** three births under one regenerating budget:
  - a reader mean on a new name (or a second mean within a name when a showing sits far from its own mean and the teacher confirms it);
  - a network unit on persistent world error;
  - a library abstraction by compression.
- **Composition:** relations over NAMED things are D's programs over the reader's names — one namer for the whole hybrid, which also fixes the hybrids' SAME failure at its root. The network earns composition only by the U3 families, read for the first time on a network that can name.
- **Language:**
  - a WORD is one prototype reached by three roads — the picture (the eye's traits), the heard sound (the ear's), the spelled letters;
  - a SENTENCE is a program over prototypes («Apple is Red» = has(x, colour = red)), induced from few examples as TWO_AFTER was, spoken only after the mouth reads it back;
  - never a next-token prediction; each stage graded by the six marks in THE SCHOOL.
  
  We are at stage 1. Sentences are at least three declared experiments away (B1.2 → B2 → B3); no date is promised.

## 5 · The next experiment — B1.2 «THE READER» (merged; to be pre-registered in B1-PREREG §12 before any code)
- **Where:** B1.1's tapes and harness, both seeds; the frozen `brain.protocol` Arm; no new world; no bar moved.
- **Pre-flight:**
  - F13's gate — met tonight (standardised SGD 81 %, RLS 93–95 % on B1.1's A1 states, both seeds);
  - the per-case U1a ceilings printed beside the bars;
  - the INPUT readers beside the state's.
- **Arms — each ONE difference from its neighbour** (config switches on `ArmA1`, R46's pattern):
  - A1 and A1-TEACH (B1.1's records — the controls that must still fail) → **A1-NORM** (heads read the standardised state) → **A1-NORM-TEACH** (+ TEACH trains the heads);
  - → **A1-NORM-RLS** and **A1-NORM-SLDA** (the reader's rule: S1 within-letter covariance, S2 the relative shrinkage chosen on the TEACH rows by the declared rule);
  - **IN-SLDA** — the same reader on the organ's features, no network: the organ floor;
  - **A1-STD-IN** — the input standardised, heads raw: the input lever;
  - **A1-HMAX** — the base at hmax = its final H + 64: the cost twin.
- **Twins:**
  - SHUFFLED-NAME, SHUFFLED-RELATION and FORCED for A1-NORM-TEACH, A1-NORM-RLS and A1-NORM-SLDA; SHUFFLED-NAME and FORCED for IN-SLDA (it answers no relation cue — SHUFFLED-RELATION NOT APPLICABLE, R38);
  - SHUFFLED-NAME for A1-NORM and A1-STD-IN.
- **Controls:**
  - the §3.1 identity test on every new arm; every switch off ≡ A1, byte for byte;
  - the NAME toy and the planted TEACH-only toy;
  - a planted total-scatter twin on a two-cluster toy that must read below the within-letter reader (S1);
  - CONST / SAME, KEY / SHIFTED-KEY, CANARY;
  - each arm's offline one-pass reader on its own final states within 10 pp of its live U1a on taught fonts.
- **Predictions** (Fable's P1–P10 with P4 reversed):
  - IN-SLDA ≥ A1-NORM-SLDA by ≈ 3–4 pp on unseen fonts (offline, each reader at its own TEACH-chosen shrinkage: 79–80 % against 76 %); A1-NORM-RLS under both (69 % offline) [Likely — the live read is B1.2's];
  - A1-NORM < A1-NORM-TEACH by ≥ 10 pp;
  - A1-HMAX = the base on every mark and under 307 ms per event solo.
- **The decision:**
  - above the SHUFFLED-NAME twin's band at both seeds on U1a AND a U3 family above its bar and its SHUFFLED-RELATION band at both seeds → the network is reinstated for NAMING and ORDER;
  - U1a only → the READER is reinstated, the network's order claim open;
  - neither → the network stays a passenger.
  
  The hybrids are rebuilt on one namer in the declaration after.
- **Cost:** ≈ 34 network runs × ≈ 1.45 h ≈ 49 CPU-h; IN-SLDA minutes; ≈ 3.5–5 h wall on 14 slots, after B1.1's last twins end. Built by one builder from a brief, test-first; gated by the seat.

## 6 · What changes in CONCLUSION.md (09-24)
1. The roles (§2 above).
2. The missing laws (§3: HOMEOSTASIS, the reader's rule, the first gate, COST solo).
3. The network's claim must be EARNED on U3, prediction and the mouth, as D earned its place.
4. Every B1.0/B1.1 architecture comparison is NOT GRADABLE until B1.2.
