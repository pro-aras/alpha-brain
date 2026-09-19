# G4 — THE WHOLE SMALL CREATURE: the design for his yes
*edit: Claude (Fable 5.1), 2026-09-19 21:11 +0400 — a DESIGN for Ahmad's yes. Not a PREREG, not code. Nothing here runs. Alpha 3 stays closed (his pause).*

**His word (2026-09-19 20:53 +04, verbatim):** «Ok let's leave this idea of this and move to next part. For starter we need something that truly is alive, can't waste time in spending and refining parts. That can come later. So first we need something that works, a small but working system, but based on all the advanced mechanism we so far in our research discussed.»

## 0 · What it is, in one paragraph
One Python process, a user service called `creature` (never `alpha3`), that never stops. A **body** of sense threads (eye, ear, the world door) publishes what it took in onto a **tape**; one **mind** thread, the only writer of memory, reads the tape and lives moments under the genome's laws. Memory is **fast** (one-shot episodes) and **slow** (G0b's grown cells and edges). A **predict** gene says what comes next; its error is the one modulator: it grades the act, scales learning, and ranks what **sleep** replays into the slow store. **Attention** chooses only what to think about. **Thinking** files predictions that can be wrong, parks questions no road can answer, and turns repeated episodes into rules. **Language** is two-word sentences from his own record under a judge. **Hands** and the **world door** are acts whose outcome he perceives. The **ask door** answers from what he holds. It is tested **as a whole**: alive 24 h, the marks, twins each blind to one thing, a plant per mechanism, the replay gate, a cost bar.

## 1 · Every mechanism of his research, one row each
Columns: his research item → the gene → its source (a file on this box, sha-pinnable) → the toy that can refuse it → the whole-creature mark that reads it. "new, minimal" = no source exists; the gene is written in tens of lines from the rule.

| # | his research (AGI Q&A, 09-19) | gene | source | the toy that refuses it | mark |
|---|---|---|---|---|---|
| 1a | always-on organs, not a discrete loop | **BODY** (threads over one memory; the tape) | `/data/dev/alpha3/docs/FUSED-SENSES-PREREG.md` A1.3 (his 09-17 10:23 word; 0 built) → new, minimal | two sense threads publish 1,000 snapshots while the mind writes; a planted sense that writes memory is CAUGHT by the writer sweep | ALIVE, REPLAY |
| 1b | organs isolated; one glyph must not kill everything | **CRASH** (a sense's error is journaled and the thread restarted; a mind error PAGES, never loops) | the 09-19 crash loop (SOLUTIONS #230) → new, minimal | a planted exception in the eye thread: journal row written, the mind's counters keep moving | ALIVE |
| 1c | a novelty (predictive-coding) gate before the brain | **SURPRISE** (a sense publishes when \|actual − predicted\| > floor) | Alpha 2 `organs/gaze.py` V0.1's surprise rule, generalised to every sense | a static frame publishes once; a changing frame every time | publish-share diagnostic |
| 2a | store traits, not bitmaps; saccades; top-down prediction to the organ | **EYE** = the sealed tower + canvas + **GAZE** | `judge/eye-tower-g2` (G0b), `genome/gaze.py` (Alpha 2 V0.1 verbatim, sha-pinned, G1) | G1's toy: the gaze finds the thing 220/220 vs random 26/220 | (x), (xi) |
| 2b | connections as geometry; invariance learned deep, not at the sensor | **TRAITS** (a small head over the frozen tower, learned by CONTRAST at sleep: one moment's glances near, other moments far) | G2's finding (`docs/G2-EYE-PREREG.md` G-4 FAIL: the eye learned neighbourhoods, not bands) + the trainer road `genome/train_eye.py` → new, minimal | a 3-thing drawn world where the untrained head overlaps and the trained head's within-median clears between-p95 | BANDS (gating on drawn, REPORTED on photographs) |
| 2c | nearest-neighbour memory | **FAST** (episodes: moment, traits, word, surprise; nearest-neighbour recall) | new, minimal | an episode written at moment t is recalled at t+1 with its word (one-shot) | (i) via «why» |
| 3a | Hebbian plasticity, online, no forgetting | **SLOW** = BIRTH / BUDGET / KWTA / HEBB / DELTA / PRUNE / MERGE / SCALE | `genome/G0b.genome` + `genome/machinery.py` (E48b arm A1, #227) | G0b's toy (circle/bar Q1 = 1.0); T-shuffle proves the shrink genes work | (i)–(v), (vii), (ix) |
| 3b | a reward / prediction-error layer | **PREDICT** (the next moment expected; the error grades the act, scales DELTA's lr, ranks replay) | his research §3/§4 (predictive coding); `docs/THINKING-RUNG1-PREREG.md` §1 → new, minimal | no-predict twin (error ≡ 0): learning unmodulated; the plant: a predictable stream's error falls, a shuffled stream's does not | MODULATION |
| 3c | one-shot learning | FAST (row 2c) | — | — | — |
| 3d | complementary systems: fast store → sleep replay → slow store | **SLEEP** (every N moments, replay the most surprising episodes into SLOW; the TRAITS head learns then) | E46b (rows buy retention); Alpha 2 `organs/sleep.py` (the cursor discipline only) → new, minimal | a two-arrival life: with sleep arrival-1 retention within 5 pp; the no-sleep twin loses ≥ 10 pp | (v) |
| 4a | think / reason / learn told apart; a prediction that can be wrong | **FILE** (the falsifiability law: claim, route, decider, due — or refused BY NAME) | `docs/THINKING-RUNG1-PREREG.md` §1 (Alpha 2 `organs/prediction_ledger.py`'s law, reimplemented) | the planted unfalsifiable claim REFUSED; the planted falsifiable one ACCEPTED and scored right | PREDICTIONS |
| 4b | belief revision, minimal change, provenance (AGM) | **BELIEF** (a clash OPENS a row, never overwrites; every belief names its episodes) | Alpha 2 `organs/belief_ledger.py` scope law, reimplemented minimal | a planted contradiction opens a clash row; the old belief is still readable | record diagnostic |
| 4c | metacognition: knowing what he cannot answer | **PARK** (N identical dead-end answers → parked; reopened on a new sense or document) — **day-1 gene** | D39 (Alpha 3's two days on `skullcap~device`, 86 % of 09-18) → new, minimal | a want no sense can answer parks after N = 3; the duty mix moves; a new document reopens it | PARK |
| 4d | induction, deduction | **INDUCE** (a rule from ≥ k agreeing episodes and no counter-example, filed as a prediction), **DEDUCE** (two beliefs → one-step prediction) | new, minimal | a planted rule is found; a planted counter-example blocks it | PREDICTIONS |
| 4e | analogy validated by its prediction (Hesse) | ANALOGY | **declared OFF** — no structure to map yet; said plainly | — | — |
| 4f | audience design, theory of mind | AUDIENCE | **declared OFF**; the door's «why» (the record behind an answer) is its first cell | — | — |
| 5a | words as vectors shaped by exposure; the word tied to the eye | **MEET** (sight × words edges; the ear as G0b) | `genome/G0b.genome` | G0b | (i), (vi) |
| 5b | composition; language enabling thought | **SENTENCE** (two-word frames «X is Y», «X near Y» composed from the record, back-parsed, judged, repaired; never next-token) | Alpha 2 `organs/speech_v2.py` + `constructions.py` + the frozen judge `speech.py` → reimplemented minimal | an utterance about a planted episode back-parses to its intent; a shuffled record's utterance is refused by the judge | VOICE |
| 5c | character → word through his eye | READ-EYE | **declared OFF** (E43/E47's stream cut; not in the skeleton) | — | — |
| 6 | concepts first, grounding later; act in the world | **HANDS** (run what he writes in the jail) | `/data/dev/alpha3/hands/jail_run` (C++ binary, reused as-is by subprocess) — switched on LAST | a program he writes runs; its output is an episode | acts diagnostic |
| 7 | overproduction and pruning as a CYCLE | **CYCLE** (grow to a ceiling → consolidate at sleep → grow again; the cap becomes a cycle) | D41; #227 (never prune by disuse) → new, minimal | T-shuffle: pruning > 0 when wrong edges exist; a life reaching the ceiling resumes births after a sleep | (iv) |
| 8 | a childhood environment with consequences | **WORLD** (the world-maker: drawn things on a cadence with new arrivals; his folder; web frames he CHOOSES to open) + **CURIOSITY** (the interest population picks what to think about and which door to open; the outcome grades it) | Alpha 2 `organs/curiosity_genome.py` (L2: the four operators, beat its null twin) → reimplemented minimal; `tools/capture_frames.py` (headless Chrome → PPM) | curiosity vs its random twin on which door yields surprise; the world-maker replays byte-identical from its seed | CURIOSITY |
| 9 | one unifying mind over tested organs | **THE MIND** (one thread, the only writer; every organ's toy passed before it is armed) | FUSED A1.3 I1 | the writer sweep with a planted offender | ALIVE, REPLAY |
| T1 | catastrophic forgetting | SLEEP + no disuse decay | #227 | the no-sleep twin | (v) |
| T2 | belief revision | BELIEF | row 4b | | |
| T3 | analogy | OFF | | | |
| T4 | metacognition | ABSTAIN («I do not know») + PARK | G0 §11; D39 | | (vi), PARK |
| T5 | theory of mind | OFF (the listener is Ahmad; «why» is the first cell) | | | |
| T6 | the Chinese Room | the whole creature's bet: a word tied to what the eye saw (MEET) | | | (i) |
| T7 | decoding neural signals | out (his own ruling) | | | |
| T8 | a self-writing genetic code | rung 2: mutate + select over the genome's numbers and switches, judged on held-out worlds against random genomes — AFTER the whole passes; today the genome is READ, never written by him | E29 (never the shape of a trained net); #163 | | |
| T9 | one unifying mind | row 9 | | | |

## 2 · The body
- **B1 one process.** A user unit `creature.service`, `Restart=on-failure`; a mind exception writes `STATUS.crash`, pages (journal + the health timer), and does NOT loop: any persisted cursor advances only AFTER the row it names is written (#230).
- **B2 threads.** Senses (eye, ear, door) each on their own thread; the mind on ONE thread; the voice (the ask door) on a thread that reads a snapshot and never writes (a question never changes him — G0's law).
- **B3 I1 — senses never write memory.** A sense publishes an immutable snapshot (payload bytes, sha256, instant) onto the **tape** `run/tape/<date>.jsonl`; the mind is the only reader of the tape and the only writer of memory. A test greps every sense module for a writer of a store it does not own, with a planted offender CAUGHT.
- **B4 I2 — the replay gate.** The mind's decisions are a pure function of (genome, SEED, tape). Wall clock enters only through the tape's instants. `creature replay <tape>` reproduces the mind's journal byte for byte, and a planted one-row divergence is CAUGHT. **This gate exists and catches before the second thread is armed.**
- **B5 a dead sense is restarted**, journaled, and the mind's counters keep moving (row 1b's toy).
- **B6 liveness is motion.** `run/STATUS.json` carries {moments, tape_rows, births, episodes, predictions_filed, sleep_cycles, parked, heartbeat_at} written every 10 s on EVERY branch; a watcher pages on a counter that has not moved in an hour. «Alive 24 h» = no restart AND every counter moved every hour.
- **B7 the GIL.** The senses are I/O + numpy and the mind is numpy; both release the GIL. Cost is measured at REAL concurrency (G12, #195), never solo.
- **B8 the tape is the world's clock.** The world-maker's cadence, his folder's mtimes, web frames' capture instants all become tape instants; nothing else reads time.

## 3 · The genome vocabulary is a machinery change
`parse_genome` today refuses unknown genes, requires exactly the areas {sight, words}, and runs RECALL k=1 only. Every G4 gene = a parser clause + an interpreter + a toy; the rung-0 constraints are lifted deliberately (an `episodes` area; RECALL k=3 for the record's «why»). `#OFF` genes stay declared with their source. A gene the machinery cannot run is a GenomeError, so nobody can "declare" a mechanism into existence.

## 4 · Minimal means the RULE, not the module
Alpha 2's organs (prediction_ledger 1,329 lines, belief_ledger 1,242, sleep 780, curiosity_genome 701) reach for `_load_sibling` / `_bridge()` and Alpha 2's stores. G4 reimplements each LAW in tens of lines, cites the source file and clause, and inherits the source's own null twin. Verbatim imports only where already sha-pinned (gaze + retina, V0.1) and the jail binary. **Rule for builders: no import from `/data/dev/alpha2` or `/data/dev/alpha3` except those three.**

## 5 · PARK is a day-1 gene
Without it the creature repeats Alpha 3's two days on one want within ten minutes of the door opening (it happened at 14:19 on 09-19). N identical dead-end answers → the want is parked with the reason; reopened only by a new sense or document naming it; the duty mix is the mark.

## 6 · Worlds, the stream, and what gates
- **Gating marks run on held-out DRAWN worlds** (G0b's eleven things; G1's canvases). **Photographs** (the Caltech words, his six pictures) are **REPORTED with their bands printed beside them**, never gating — the photograph eye failed its band mark today (G2 G-4) and contrastive training is unbuilt; a bar on photographs would fail for a known reason (#228).
- **The stream for a 24 h life is a design item:** the world-maker draws a canvas every S seconds from a seeded stream with a new ARRIVAL every H hours (new things, fresh budget); his folder `world/<word>/` is watched; web frames come through the capture road at most K per hour, and only when CURIOSITY opens that door. Every source is replayable (seed → same tape).

## 7 · Build order — the walking skeleton first, then genes switch on inside the living creature
1. **Day 1, alive:** the body service + the tape + the replay gate CATCHING a planted divergence + eye/gaze (G1 verbatim) + SLOW (G0b) + FAST + the ask door + heartbeat + STATUS motion + PARK armed (fires when wants exist). Runs on the world-maker.
2. **PREDICT + FILE** (the modulator), **SLEEP + CYCLE**.
3. **CURIOSITY + WORLD door** (his folder, web frames), **INDUCE / DEDUCE / BELIEF**.
4. **SENTENCE**, the door's «what comes next» and «why», **HANDS**.
5. **The 24 h life and the VERDICT, once, on the whole.**
Each gene's toy passes before it is armed. A gene switched on is a genome edit, so it is a new life (restart, journaled; the tape kept for replay); the 24 h ALIVE mark is measured on the final genome. This honours both his sentences: something that works first, tested as a whole at the end.

## 8 · The verdict, outlined (bars, ceilings and nulls are set in the PREREG after his yes — #222, #228)
- **ALIVE:** 24 h, NRestarts 0, every counter moved every hour, no sense thread dead > 60 s.
- **REPLAY:** the day's tape replays to a byte-identical mind journal; a planted divergence CAUGHT.
- **The nine marks + (x)(xi)** on held-out drawn worlds, sat by the creature itself nightly (a SELF-EXAM duty whose answers land in his record; the answer key stays outside him).
- **Twins, each blind to exactly ONE thing and able to do everything else** (#228 addendum): no-sleep, no-predict, no-curiosity (random choice of what to think), random-gaze, frozen, no-park.
- **A plant per mechanism, placed where it can fire:** SLEEP (a surprising episode only replay consolidates), PREDICT (refused / accepted-and-scored), PARK (an unanswerable want), CURIOSITY (a novel thing behind one door), BELIEF (a contradiction), the G0b plant and null plant.
- **Cost at real concurrency:** the mind's moment ≤ X ms with every thread running; RSS bound; the 24 h CPU bill.
- **BANDS** reported for drawn worlds, photographs and his pictures, each with the gate's within-median vs between-p95.

## 9 · The genome — a DRAFT (no machinery reads it yet)
```
# G4.genome — THE WHOLE SMALL CREATURE (DRAFT; thetas written by gate G-a; bars in the PREREG)
SEED     20260920
# BODY
BODY     service creature threads eye ear door mind voice
TAPE     run/tape                                  # every sense delivery: instant, sense, sha256; the mind reads only the tape
HEART    every 10 s                                # STATUS counters on every branch; liveness = motion
CRASH    sense restart journal; mind page          # a sense's error never kills the mind; a mind error pages, never loops (#230)
# SENSES
SENSE    eye    32x32 grey                         # the sealed tower's frame (G0b)
RETINA   thresh0.25 centre tower:eye-tower-g2 sqrt unit
GAZE     surprise fixations 12 grid 16 canvas 128 glance 32 ink border   # G1 §6
TRAITS   contrast head 32 lr 0.01 at sleep         # NEW: a small head over the frozen tower, learned by contrast from replayed episodes
SENSE    ear    letters 8
SURPRISE floor 0.05                                # a sense publishes when |actual − predicted| > floor (V0.1's rule on every sense)
# AREAS + MEET (G0b)
AREA     sight  from retina
AREA     words  from ear
AREA     episodes from fast
MEET     sight  words
# GROW / WIRE / SHRINK (G0b verbatim)
BIRTH    novelty  cos<THETA_N
BIRTH    error    misfires 3
BUDGET   400 per arrival
NMAX     2000
KWTA     5
HEBB     window 1
DELTA    lr 0.05
PRUNE    w<0.02 after 3 chances
MERGE    cos>THETA_M same-answer
SCALE    every 1000 moments
CYCLE    grow to 0.9 nmax then consolidate         # NEW: the cap becomes a cycle (D41)
# MEMORY, fast and slow
FAST     episodes 20000 keys sight words surprise  # one-shot rows; nearest-neighbour recall
SLEEP    every 2000 moments replay 200 by surprise # the most surprising episodes replayed into SLOW; TRAITS learns then
# PREDICT — the one modulator
PREDICT  next glance; error scales delta 0.5..2.0; ranks replay; grades act
FILE     claim route decider due                   # the falsifiability law: four fields or refused by name
# ATTENTION / CURIOSITY / METACOGNITION
CURIOSITY interests 50 operators recombine generalize specialize bridge   # chooses what to THINK about and which door to open, never whether to perceive
PARK     after 3 identical dead-ends reopen on new-sense                  # D39
# THINKING
INDUCE   rule from 5 episodes no counter           # a rule is a prediction
DEDUCE   one step                                  # two beliefs → a prediction
BELIEF   clash opens never overwrites              # Alpha 2's scope law
# LANGUAGE
SENTENCE two-word frames is near under-judge       # speech_v2's road, minimal; never next-token
# HANDS + WORLD
WORLD    drawn every 5 s arrivals every 6 h; folder world/; web 6 per hour by curiosity
HANDS    jail alpha3/hands/jail_run                # switched on last
# ANSWER
RECALL   k=3
ABSTAIN  second/best > 0.85
ASK      what-is show is which next why
# STAGES
STAGE    1 senses   moments 0..200
STAGE    2 meet     moments 200..
#OFF ANALOGY   hesse                               # declared; no structure to map yet
#OFF AUDIENCE  listener-model                      # declared; «why» is its first cell
#OFF EAR-SOUND cochlear gammatone agc              # E52's front (the loudness path proven, the frequency path untested)
#OFF READ-EYE  words through the eye               # E43/E47
```

## 10 · Two builders (after his yes)
- **Builder A — the body:** the service, threads, tape, replay gate, STATUS + watcher, crash isolation, the world-maker and the doors (folder, web frames), the ask door's threads.
- **Builder B — the genes:** FAST, PREDICT + FILE, SLEEP + CYCLE, CURIOSITY + PARK, INDUCE / DEDUCE / BELIEF, SENTENCE — each a parser clause + interpreter + toy under the machinery.
- **Claude:** the genome text, the laws, the PREREG (bars, ceilings, nulls), the gates, the unit, the verdict, and every merge.

## 11 · What is HIS
- **The yes on this design.**
- **(a)** gating marks on drawn worlds, photographs reported — or a bar on photographs too (it would fail for G2's known reason).
- **(b)** the skeleton first, genes switched on one at a time inside the living creature, the verdict once on the whole — or every gene before first breath.

## 12 · What this design does not claim
- It will not band photographs (G2's finding stands); TRAITS is the attempt, reported.
- Analogy, audience design, sound and reading words through the eye are declared OFF with their sources.
- No self-writing genome here; that is rung 2, after the whole passes.
- Nothing is built; every number above is a draft to be set in the PREREG with its ceiling and null computed before the run.
