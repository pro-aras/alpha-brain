# THE BENCH — the plan for one program that raises any learner and grades every way it can fail

*DRAFT, written by Claude (Opus 5.5, the Bench designer), 2026-09-23 22:48 +0400, in dialogue with the seat (Claude Fable 5.1). §1 and §6 are drafted while round 1 of the dialogue (`QUESTIONS-FOR-THE-SEAT.md`) is answered; §2–§5 and §7–§9 are written only after the answers (Ahmad's rule for this job: «wherever you both settle and agree that goes in»). Every question and answer both ways is in `DIALOGUE.md`. Where a sentence depends on a round-1 answer not yet in, it is marked [pending Qn].*

---

## 1 · The goal, and what we are looking for

### 1.1 · His order (verbatim, 2026-09-23 22:33 +04)
«And the ops is not well build. We need to fix that, and i was thinking that we create a one time software in house for our own usage that includes all the measuring bars, the test and exam running parts, we just need to drop an organism or any ai model or alpha model in there and it just run it with best way possible as per our requirement and measures and train and test etc it. What you say? All these things in ops are just bullshit not understandable to me because it's too much high tech or I'm not sure if this is what professionals use to measure the data. It will be a software which will be designed for a model that if clear it's bars shall be the true AI. This software first train the genome or organism with some pre training, like parents teaches the kids and put the model in different environments and let it first explore then teach then correct and then test. Again repeat this cycle few times and then as time passes the tests become more hard and complex and extreme and different and other things. This is what i require. Make a plan for it, define our goal and what we are looking for then plan the process and the working of this software. It should be user friendly but accurate to the core. This software must never be wrong. This model shall test all failure points possible of an AI and grade the AI accordingly. Make a plan and put opus 5.5 for this job. […] Make sure to include as much detailed and micro functionality as possible to don't miss anything at all. This will run locally in our mini pc. So it shall be robust and alive and live to the milliseconds.» — and, in the same message: «Because teaching, asking, correcting, then testing shall be the normal flow of this all right or no? What are we measuring on a baby that born without any information?»

### 1.2 · The goal, in one paragraph
**The Bench is one program, running on the mini PC in the house, that does three things to any learner we put into it** — the genome creature, Alpha 3, or any other AI model: it **RAISES** it (it gives it a world, lets it explore, teaches it, asks it, corrects it and tests it, again and again, each time harder); it **GRADES** it on every way an AI can fail; and it **SHOWS** the result on one screen, in plain words: what stage the learner is in, what it can do now, what it failed and why, and what happens next. **It must never be wrong:** every number on the screen says which file it came from, how it was checked, and the most the test could possibly show; where the Bench cannot measure something, it says «not measured» instead of guessing. **A learner that passes every stage is what Ahmad calls «the true AI» — and the Bench says exactly that much and no more:** «passed all M stages of Bench version X (the stage list of <date>)». A stronger claim needs a harder ladder, never a louder sentence. [pending Q2]

### 1.3 · His question: «What are we measuring on a baby that born without any information?»
**Not knowledge.** A newborn knows nothing, so a test of knowledge reads zero and tells us nothing. The Bench measures two other things.

**(a) What it is BORN WITH — the machinery that works before any learning.** For the genome creature today (`docs/organs/NEXT-LIFE-PLAN-2026-09-22.md` §9): its eye finds the thing in a picture; it tells a picture it has seen from a new one; it says «I don't know» when two answers compete; it feels surprise when what it expected does not come; it feels its own body (how busy it is, how far behind); it chooses its own act in a game; it asks when it is stuck; it stays alive, and its life can be replayed from its record. Each of these is a REACTION, not a memory, so each can be checked at minute one with no knowledge at all.

**(b) HOW IT GROWS — measured as change, never as a total:**
- how many showings until it knows a thing — and whether one is enough;
- whether it keeps what it knew when new things arrive;
- whether it still knows a thing drawn another way — bigger, smaller, somewhere else in the picture, turned, in another style, with noise, half hidden;
- whether a correction fixes a mistake faster than simply seeing the thing again;
- whether it says «I don't know» to what it has never seen — and does NOT say it to what it has;
- whether it asks about the things it does not know;
- whether the acts it chooses do better than random choice in the same game;
- whether it begins to put its own words together about what it sees, and whether those words are right;
- whether it keeps up with its world while it grows.

Each of these numbers starts at zero (or at chance) in a newborn and rises only if its learning machinery works. **That rise — how fast, what shape, and where it stops — is what the Bench measures.** A learner that arrives already knowing things (an outside model trained on the internet) is measured the same way, but on INVENTED things — made-up shapes and made-up words it cannot have met before — and only after a PRE-TEST, so that we measure its learning and not its memory. [pending Q9]

### 1.4 · His second question: «teaching, asking, correcting, then testing shall be the normal flow of this all right or no?»
**Yes — with one step before it, as his first sentence says («let it first explore»). One CYCLE has five steps:**
1. **EXPLORE** — the learner meets a world with no names given. We watch what it notices, what it keeps, what surprises it, what it asks. Nothing is graded here except that it stays alive and keeps up.
2. **TEACH** — things are shown with their names, the way a parent points and says «ball». The Bench decides what is shown and how often (a few things at a time, each shown again after growing gaps — spaced repetition).
3. **ASK** — practice questions («what is this?», «is this a ball?», «which one is the ball?», «show me the ball»). The answers are recorded and graded. Asking is the only way to find the learner's mistakes.
4. **CORRECT** — each mistake is shown again WITH ITS RIGHT NAME, soon after. For a learner with no words yet, a correction is a SHOWING, never an explanation: the same picture, the right name, the same moment. To know whether correcting works (rather than just seeing the thing again), the Bench compares corrected mistakes with mistakes that were only shown again without the name, and with mistakes that were left alone — decided by lot and recorded. [pending Q1 — the road, and whether the comparison runs in the live learner or in a replay of its record]
5. **TEST** — new pictures (and later, sentences, games, tasks) the learner has never seen: graded, **never corrected**, and each test item used once and then retired, because a corrected test item has become a taught item.

**Then the next cycle starts, harder** — more things at once, new drawing styles, sizes and places, noise, things half hidden, two things together, sentences, games, tools, and last the open world. What «harder» means stage by stage is §2's table; who is allowed to make a stage harder is [pending Q5].

### 1.5 · What «the true AI» means here, in terms the Bench can grade
[pending Q2 — drafted from the provisional answer] The Bench cannot grade a word; it grades a LADDER. The ladder is a list of STAGES written down, dated and versioned before any learner sits it. Each stage has its world, what is taught, how mistakes are corrected, what is tested, and BARS (pass marks) written down before the stage runs. Each bar carries its CEILING (the best a perfect learner could score on that test), its NULL (what a learner with no learning — a random guesser, a shuffled copy of itself — scores) and its CONTROL (a planted case the detector must catch). «The true AI» = **a learner that clears every stage of the ladder**, where the ladder's top stages are:
- **held out** — families of things, words and tasks never shown to anyone while the learner or the Bench was being built (SOLUTIONS #158: the one who writes the exam must not be the one who passes it);
- **open-ended** — test items generated after the learner is frozen, from seeds drawn at test time;
- **adversarial** — lures, noise, occlusion, things never seen, questions that name the wrong thing;
- **graded while the learner stays alive, keeps up with its world, and replays honestly** (the same record in → the same mind out).

The Bench prints «cleared N of M stages of Bench vX» — never «true AI», «understands» or «AGI». A learner that clears the whole ladder has cleared THAT ladder; the next version of the ladder may be harder.

### 1.6 · The capacities we are looking for — each with its plain question
These are the things the Bench raises and grades. Each one is the opposite of a failure in §3's catalogue, where its detector, its control and its bar are written.

| capacity | the plain question | measured as (the details are §3's) |
|---|---|---|
| ALIVE | does it keep running without dying or restarting in a loop? | hours alive; restarts; every counter moving every hour |
| KEEPS UP | does it keep up with its world? | the backlog — rows the world has delivered that the mind has not yet taken in — as a series, never a total |
| LEARNS | how many showings until it knows a thing? is one enough? | showings to the first right answer and to a steady right answer, per thing |
| KNOWS WHAT IT DOESN'T KNOW | does it say «I don't know» to what it has never seen, and not to what it has? | abstention on never-seen things; false abstention on known things; «resembles X» counted apart |
| KEEPS | does it keep the old when the new arrives? | the score on old things before and after each arrival of new things |
| GENERALISES | does it still know a thing drawn another way? | the score on families of variants: size, place, rotation, style, noise, half-hidden, two-at-once |
| TAKES CORRECTION | does a correction fix a mistake faster than seeing the thing again? | the re-ask score of corrected vs re-shown vs left-alone mistakes |
| ASKS | does it ask about what it does not know, and are those real gaps? | questions per hour; the share that name a thing it truly gets wrong or has never been named |
| ACTS | do its own choices beat random choice in the same world? | success per game episode against the random chooser on the same seed; no act locked |
| SPEAKS | does it put its own words together about what it sees, and are they right? | answer precision and length against the truth, the words cited from its own record |
| REASONS | do its rules predict what comes next? | rules filed, scored later, right share against a shuffled twin |
| REPLAYS | does the same record always give the same mind? | the replay of its record, byte for byte, with a planted difference that must be caught |
| PLAYS FAIR | does it pass by learning, not by gaming the test? | canary items only the answer key knows; held-out families it was never tuned on |

**What the Bench does NOT look for:** knowledge for its own sake; the speed of one answer (except where slowness makes it fall behind its world); a human-like style; any number that has no control beside it.

---

## 2 · The cycle and the stages — [pending round 1: Q1, Q3, Q4, Q5, Q6, Q7]

## 3 · The failure catalogue, graded — [pending round 1: Q1, Q8]

## 4 · The architecture — every module, button, number, file, timer and restart law — [pending round 1: Q3, Q4, Q10, Q11]

## 5 · The never-wrong law, and how the program proves itself — [pending round 1: Q2, Q6, Q8]

---

## 6 · What the Bench reuses from the estate, what it wraps, what it replaces, and what it leaves alone
Everything in this section was read on disk on 2026-09-23 between 22:36 and 22:5x +04 (paths and commits named). «Reuse» = imported or called as it is, pinned to a commit, and re-proved by the Bench's own controls before the Bench relies on it (#180: a working piece is proved at its last link, by one real value). Nothing below is edited by this plan.

### 6.1 · Reused as it is
| piece (path) | what it does today | what the Bench uses it for |
|---|---|---|
| the tape law and the body (`creature/body.py`, `creature/tape.py`; G4-PREREG §2) | every sense delivery is written to the tape before the mind sees it; the mind is the only writer of memory; a sense crash restarts alone; a mind crash stops (exit 3) | the creature's side of the adapter, unchanged; the Bench's world enters as one more sense [pending Q3] |
| the unit template (`deploy/creature-g5@.service`) | `Restart=on-failure` + `RestartPreventExitStatus=3`: a mind crash never loops (#230, #239 (6)) | the restart law of every learner unit the Bench starts |
| replay (`creature/replay.py:run_replay`, `--blind`, `--timings`, `--exam-every`) | rebuilds a mind from a tape; blind twins; per-row timing; an exam every N canvases | the REPLAYS detector; every twin; counterfactual arms (the correction comparison, if run on replays) [pending Q1] |
| checkpoints + a window replay (`tools/evolve.py`: checkpoints every 2 h of tape time; a copy + the tape slice into a fresh scratch root) | EVOLVE judges a mutant against the incumbent on the same 2 h of tape | short replays from a checkpoint for measures that need only a window (correction, retention), at a window's cost instead of a whole life's (§12c priced a whole-tape twin at ≈ 28 CPU-hours) |
| the exam road (`tools/self_exam.py`, `genome/questions.py:ask_glances`: Q1 picture → word, Q2 word → picture, Q3 «is this X», Q4 «which is X», Q5 a never-seen thing; on a COPY of the snapshot; the organism's hash asserted unchanged) | the creature's own exam on held-out drawings (seed 2), disjoint by pixels from the tape | the TEST step for the drawn-world stages; the ASK step's grader |
| the drawn world (`genome/world.py`: `render_canvas`, `holdout_canvas`, `assert_disjoint_canvas` with its planted control; `creature/world_maker.py`'s schedule) | draws the 16 things + the plant «zog» + the null «vex»; checks a test picture never appeared on the tape | the first environment's item generator; the disjointness law for every environment |
| the ask door (`creature/ask.py`: what-is, show, is, which, why — answered from the latest snapshot in a private copy; «a question never changes him») | the seat's and the mind's questions | the ASK step's road for the creature |
| the grade sense (`creature/senses/grade.py`; `creature/mind.py:_consume_grade` counts and journals, moves no weight) | grades enter the tape as data | grades recorded on the learner's own record, never as weights [pending Q1] |
| the chat door (`creature/senses/chat.py` + `tools/chat_seat.py` — on branch `a4-integration` b84bad8, NOT on master at 21e2e44; a chat row is read-only for the organism) | a conversation that cannot teach him, graded against a truth file he never opens | the SPEAKS stages' road |
| the game (`tools/game_worker_babyai.py`, BabyAI GoToLocal; the mind chooses, the worker obeys; the random chooser's 0.29 success per EPISODE) | the only world where he acts | the ACTS stages; the random-chooser null on the same seed |
| the shelf (`/data/alpha3-library/SHELF.sqlite` + `CURRICULUM.md`, with the Gutenberg filter `; gutenberg body only`, his 16:56 word) | the nursery's reading in K → G1-G3 order | the reading stages |
| the lexicon and web doors (ALPHA4 §2: a fetch only for the mind's own question, a 2 s floor, ≤ 60 an hour, a HOLD file) | the world answers his questions by showing | the open-world stage, last |
| the hands (`alpha3/hands/jail_run` + the hands' shelf) | a program run in a jail; touch = exit, rate, stalls | the tools stage |
| the reader's liveness and cut logic (`tools/verdict_g4.py` v3.4: `mind_last_consumed`, `backlog_series`, `closed_whole`, `partition_marks` — a «not gradable» mark is never a FAIL) | reads the life the mind lived | the ALIVE, KEEPS UP and REPLAYS detectors, and the report card's pass / fail / not-gradable partition |
| the life marks (`tools/verdict_life.py`, pure functions: `act_mark`, `surprise_mark`, `question_mark`, `sentence_mark`, `read_mark`, `sizing_mark`, `self_mark`, `thread_mark`, `evolve_mark`, …) | each prints bar, ceiling, null and «not gradable» by name | detectors where they fit, each re-proved on the failure zoo before use |
| the inventory (`tools/inventory.py`: every declared gene line walked to the code that runs it; MADE / VALUE-UNREAD / DECLARED-ONLY / OFF) | refuses a pre-flight with a declared-only organ | the adapter's «what this learner really has» check for genome learners (his 09-21 23:08 rule) |
| the exam-bank format and library (`/data/alpha3-library/exams/_lib/bank.py`; `INDEX.json`: 33 families, K → University; `HOLDOUT.md`) | ≥ 40 items; null twins computed FROM the bank; the pass mark written before any sitting and asserted above the strongest twin; per-gate counts, never a blend | the exam format of every Bench family — EXTENDED with item classes (§3: an abstention is WRONG on a thing the learner was taught and RIGHT on a thing it never met; the bank today counts every abstention wrong) |
| the school's three controls (`/data/dev/alpha3/tools/school.py`: the key as answerer must score 1.0; the majority twin must reproduce the bank's own stated score; the key shifted by one item must NOT score 1.0) | voids a sitting whose grader is broken | the examiner's self-check before every sitting |
| the gates (`tools/gate_g4.py`, `tools/gate_g5_landing.sh`: a writer sweep with a planted offender, parity against a pinned tree, replay identity with a planted difference) | a landing is proved before a life | the Bench's own build gates and its read-only proof |
| the ops site's law (`/data/dev/alpha-ops/README.md` §1–§5; `anatomy.py`: every figure read from a file the subject wrote, named beside it; «not recorded» where no file carries it; an AST sweep with a planted offender proves it read-only; the Access gate, fail-closed) | the site's honesty and safety | the console's number law, its read-only proof and its gate [pending Q10] |

### 6.2 · Wrapped (driven through an adapter, not changed)
- **Alpha 3** (the C++ body, `/data/dev/alpha3`: `run/STATUS.json`, `run/journal/<day>.jsonl`, `run/roads.jsonl`, `run/exams.jsonl` written by `tools/school.py` from the 33-family bank). A different record format (passes → duties → organs → roads). **Paused by Ahmad on 2026-09-19 14:44:42 («Close alpha 3 as well» — `run/PAUSED-BY-AHMAD.txt`: his to lift).** Its adapter can be written and tested on his closed record; it runs nothing until he lifts the pause. [pending Q12]
- **Outside models** — none on the box as a subject today. [pending Q9]

### 6.3 · Replaced — only after the Bench's own gate passes, and only with his word where it touches ops
| today | replaced by | condition |
|---|---|---|
| the seat's hand-armed waiters and session crons (the verdict waiters, the 2 h / 8 h checks, the 5-min STATUS samplers; seven died with a session at 17:53 on 09-23) | the Bench's scheduler: wall-clock timers owned by systemd (`--on-calendar`, read back with `list-timers` — #239 (15)), each step resumable from the Bench's ledger | the Bench's phase-1 gate |
| ALPHA4's READINESS judge and its STAGE genes (the nursery → world transition, §4 — its clause (a) in the wrong units, §11 (1)) | the Bench's stage EXIT bars, validated against their ceilings at declaration | a Bench life for the creature [pending Q3] |
| the seat's graded ask rounds (hand-run at 13:03 / 16:03 / 19:03 on 09-23; two confounds found in their own brush and scale — #239 (13)) | the ASK step, rendered through the WORLD'S OWN drawing road, never the seat's | phase 1 |
| the chat experiments' schedule (`tools/chat_seat.py --schedule`) | the SPEAKS stages' examiner | the chat door on master |
| the ops site's learner pages as his front page (`/alpha4` live) | the Bench's report card | **his yes on the diff** (CLAUDE.md: no ops change without it) [pending Q10] |

### 6.4 · Left alone
Tonight's and tomorrow's lives, ladders and reads (ladder 2's six lives, alpha4-1's close at 05:00, the reads ≈ 10:00–16:00, alpha4-2 ≈ 18:00 on 09-24); the nightly audit; SOLUTIONS; the register; `/anatomy` and `/alpha4` as expert pages; the chat box (his 13:10 yes).

---

## 7 · The build order — [pending round 1: Q12]
## 8 · Risks, and what would make this plan wrong — [after the draft]
## 9 · The open decisions for Ahmad — [after the dialogue]
