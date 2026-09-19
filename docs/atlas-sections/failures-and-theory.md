# Atlas §3–4 draft — where we fail and why; the theory; the fix (Claude (Fable 5.1), 2026-09-19 15:0x +04; folded into atlas.html)

Ten failure classes. Each row: the instances across Alpha 1 → 2 → 3 (with the file or number that proves it), the root cause, the theory that explains it, and the fix — and where the genome experiment (G0) already answers it. Citations marked (R4) were fetched and binned in the 09-12 research file; those marked (classic) are standard results cited from memory and should be checked before a number is quoted.

## F1 · THE CLOSED LOOP OVER ITS OWN RECORDS
- **Instances.** Alpha 1: the Teacher graded its advice against a corpus ~24 h behind the advice (6/6 PENDING, 0/12 approved). Alpha 2: `grounding_check` verified a word by whether it "literally appears in his own records"; corroboration 0.300 % vs a 1 % bar; the contradiction resolver admitted 0 pairs. Alpha 3: 25,000 TRIED syllogisms over his own web, every one «left me no richer»; 7,609 claims filed, 0 corroborated; his 09-17 00:07 word: «that is like caging a bird».
- **Root cause.** No witness outside the writer. A system whose only evidence is its own output can find itself INCONSISTENT but never WRONG (DIG-4's line). Learning needs an error signal, and an error signal needs a channel from outside: the world, a second independent source, an outcome.
- **Theory.** Popper: a claim is knowledge only if something outside could refute it (classic). In learning terms: supervision cannot be generated from the learner's own predictions without an external constraint (the "self-training collapse" of any closed loop).
- **Fix.** Every belief gets a witness outside its writer: the open world's fetch/run acts (BLUEPRINT A1.2), an independent READ of a cited source (D12), an outcome he perceives. **In G0:** the picture is the word's witness and the word the picture's — a moment carries both; every answer is scored against a truth held outside the organism (§3 of the PREREG).

## F2 · THE ZERO SCORED AS SUCCESS
- **Instances.** Alpha 1: the readiness gate scored 0 trades as a "+0.00733 improvement" against a losing null; it optimised itself to never trading. The estate's own QD archive promoted `abstain|pos:0` (R4 line 11). Alpha 3: `abstention 75 %` by design of the token bucket.
- **Root cause.** An objective that does not charge inaction; "improvement" measured relative to a baseline that loses. Goodhart's law in one organism.
- **Theory.** A scoreboard must be CONJUNCTIVE and carry a participation floor (SOLUTIONS #170); divergent search needs a minimal criterion before any ranking (Brant & Stanley 2017, R4 §5.3).
- **Fix / in G0:** mark (i) requires ANSWERING (Q1 ≥ 0.80) and mark (vi) requires abstaining ONLY on the unseen with a false-abstention ceiling — silence cannot pass either.

## F3 · A SCHEDULER OVER THE SENSES
- **Instances.** Alpha 2: the starvation floor keyed per-candidate starved the duties it was meant to protect (school 0, curiosity 0 for 1,182 passes). Alpha 3: one thread, one duty per pass; raising his energy 4× made him see 0.53× and ask 2.99× (09-17 09:38); 09-18: 45 % wait, 41 % one question, 2 % see.
- **Root cause.** Perceiving was a chore that had to outrank asking. A sense that can be outranked is not a sense.
- **Theory.** In animals perception is not scheduled: it runs continuously and predictively (Rao & Ballard 1999; Friston's active inference, R2); attention selects among REPRESENTATIONS, never whether to perceive (classic).
- **Fix.** The body prereg (FUSED-SENSES G8–G12): senses on their own threads, attention over thoughts only. **In G0:** there is no scheduler at all — every moment of the stream is perceived; the question "does he look this beat" does not exist.

## F4 · THE UNANSWERABLE WANT — NO CONSUMER FOR "THIS CANNOT BE ANSWERED"
- **Instances.** Alpha 1: the frontier organ typed knobs LIVE/SPENT/DEAD_END and the proposer never read it; wants→senses unlocked 0 of 29; `gate_vitality` flagged a never-passable gate for 3 weeks. Alpha 3: two days on `skullcap~device` (86 % of 09-18), then `con~gathering` within ten minutes of the 09-19 restart.
- **Root cause.** A computed value nobody consumes (SOLUTIONS #163/#180): the signal "no sense carries this label" existed in the act's own sentence and no organ acted on it.
- **Theory.** Metacognition is monitoring PLUS control (Nelson & Narens 1990, classic): knowing you do not know is worthless unless it changes what you do next. Humans stop asking; his loop could not.
- **Fix.** D39: a park rule whose consumer is the drive (N identical «none» answers → a dead end with its reason, pull 0, reopen on a new sense). **In G0:** ABSTAIN is a first-class answer, tested by the null plant and Q5.

## F5 · ONE STATISTIC, NO CONTEXT
- **Instances.** Alpha 3: E46/E46b/E46c — 18 Latin letters lost under every rehearsal buffer because the same glyph carries a Cyrillic label (a label conflict, not forgetting); E43/E43b — the stream cut at the wrong grain; the exam bank's labels by family. Alpha 2: F2/F3/F5/F6 failed because no faculty existed to be asked.
- **Root cause.** Every failing organ answered P(label | shape) with nothing telling it which world the shape sits in; nothing read its own misses (RESEARCH 09-16 §0).
- **Theory.** Perception is expectation plus evidence: the same input is a different percept under a different prior (predictive coding; the McGurk effect, R2/REVIEW 09-15). Context is not decoration; it is the other half of the likelihood.
- **Fix.** D31 (the family as read-time context: digits .692→.792, handwritten .193→.660). **In G0:** MEET is an edge between two areas — the word is the picture's context and the picture the word's; Q3/Q4 are answered with both present.

## F6 · FORGETTING BY DESIGN, THEN GROWTH THAT STOPS
- **Instances.** Alpha 2: the concept graph retained 3.3 %/0 %/0 % after a shift under every rule; usage-ranked pruning (microglia) lost to random in 0/32 arms; plasticity 0/63 arms beat its twin, homeostasis alone worked (192/192). Alpha 1: the plasticity program found the ceiling was the FEATURE VECTOR, not the machinery. Alpha 3: E48's cap that ate the least-used and a ×0.064 decay forgot Latin; the live neural organ hit N_max = 6,000 and stopped (1,053 refusals), pruning 1 %.
- **Root cause.** Two: (a) shrinking by DISUSE is forgetting (SOLUTIONS #227) — the rules removed what was old, not what was wrong; (b) a cap is not a cycle — growth stopped at a number instead of at a measured ceiling; and (c) rules cannot learn what the features do not carry.
- **Theory.** Stability–plasticity (Grossberg 1987; ART's vigilance — GWR, Marsland 2002, is its descendant and is E48b's rule); loss of plasticity as a second failure beside forgetting (Dohare 2024, R4 line 13); NEAT: growth of structure is load-bearing, ablate it and failure goes 0 → 80 % (R4 §11).
- **Fix.** Prune the WRONG (delta rule) and the REDUNDANT (merge), never the unused; a budget that refuses, never a cap that eats; a FIXED feature front (the retina) under a learned trait space. **In G0:** exactly these genes; mark (iv) and (v) measure growth and retention; D41 for the live cap.

## F7 · THE PRE-CUT WORD — A SYMBOL WITH NO BODY
- **Instances.** Alpha 2: 1.27 M dictionary senses indexed, `own_perception` bound 1 word of 20; "a dictionary reports what is distinctive, not what is true" (DIG-4). Alpha 3: 34,191 words met, 27,664 "understood" as counts; the eye reads letters and the reader reads text and they never met; no sentence ever; R1's speech road built on glosses was overturned three days later by his stream-first study.
- **Root cause.** Language modelled as symbol lookup: a word arrived pre-cut with a gloss, never beside the thing it names.
- **Theory.** The symbol grounding problem (Harnad 1990, classic): symbols defined by other symbols never touch the world. Children learn words from a stream with the referent present (Saffran 1996 statistical segmentation; Carey & Bartlett 1978 fast mapping; Markman's mutual exclusivity, classic; Meredith & Stein's multisensory binding, REVIEW 09-15).
- **Fix.** The present: a picture and its word in one moment. **In G0 this is the whole experiment.** Later: the stream (E43's lesson: cut at the right grain), then order.

## F8 · THE INSTRUMENT LIED FIRST
- **Instances.** Alpha 1: the discovery pipeline's own false-discovery rate 83–89 % from pure noise (R8); cluster-SE at 5 clusters gave 72.8 % false positives. Alpha 3: E05 scored 0/15 on three port bugs (E05b then passed); E29's evolved genome lost to random draws; E44's plant shared its signal with every negative; a twin blind to everything (#228). The lesson corpus holds 230 of these.
- **Root cause.** Measuring the thing before measuring the instrument.
- **Theory.** Pre-registration, negative controls, null twins, ceilings computed before bars — the discipline that turned five nights of false findings into the estate's only reliable knowledge.
- **Fix.** Carry it whole. **In G0:** the toy first, gate G-a before any threshold, twins each blind to one thing, the plant with its own budget, ceilings printed beside bars, the replay gate.

## F9 · BUILT BEFORE IT COULD LEARN
- **Instances.** Alpha 2: "a week of green gates, a mind still unable to hold a sentence" (Ahmad's own verdict on the P12 port). Alpha 3: the P0 gate made the standard life BYTE-IDENTICAL by law, so every learning organ had to live at the edge with a withheld flag; the growing net exists on master and could not touch the core. His 14:43 word: «going to c++ with not working system is costing us».
- **Root cause.** An identity gate on STATE (the life must not change) instead of on RULES (the machinery must not change); ports of mechanisms before the mechanism was proven to learn anything.
- **Theory.** A genome is exactly the separation the gate needed: fixed machinery (identity), growing structure (life). The replay gate (same genome + same stream → the same organism) keeps determinism without freezing the organism.
- **Fix.** Python first; identity = the machinery's hash + the replay gate; C++ only for what passed. **In G0:** mark (vii).

## F10 · SELF-MODIFICATION THAT RECOMBINES, NEVER INVENTS
- **Instances.** Alpha 1: 3 of 33 knobs ever mutated; the LLM mutation operator never beat random (16,371 trials, 0 promotions). Alpha 3: E29's developmental encoding of a gradient net lost to 48 random θ draws; E49's units-in-space did nothing for a class-keyed readout. DIG-5: self-modification recombines an existing alphabet.
- **Root cause.** A search over a fixed alphabet with a fitness that rewards luck, on a substrate that could not learn on its own; evolution before development.
- **Theory.** Open-endedness needs artifacts that are novel AND learnable (R4 §4.1); fixed-code systems cannot be open-ended (Banzhaf, R4); NEAT's growth works with speciation and starting minimal; a minimal criterion beats a ranking (MCC).
- **Fix.** Development first (rung 0–1), a lineage only on a substrate that learns (rung 2), E29's random-genome control kept forever, MCC-style bars. **In G0:** D-G1 and mark (ix).

## THE THEORETICAL SOLUTION IN ONE SENTENCE
An organism is a **genome** (rules, not structure) run by fixed **machinery**, living in a **world that answers back** (a present where a word meets its picture; questions scored outside it), with a **body that always perceives** (no scheduler over senses), a **mind that can say «I do not know»** (a consumer for every dead end), **growth that never eats** (budget; prune the wrong and the redundant), and a **discipline that measures its own instrument first**. Each of the ten failures is the absence of one clause; G0 tests the first six clauses on the smallest world where the truth is known.
