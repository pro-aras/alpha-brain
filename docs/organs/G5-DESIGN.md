# G5 — THE CREATURE REVERSE-ENGINEERED FROM BIOLOGY, WITH SOFTWARE ADDED — the design for Ahmad's yes
*edit: Claude (Fable 5.1), 2026-09-21 16:07 +0400. Assembled from the six organ documents under `docs/organs/` (EYE, EAR, BODY-SENSES, MOTOR-HANDS, MIND-MEMORY, MIND-THINKING-LANGUAGE — ~580 KB, ~600 road-tagged claims, written today by six Opus 5 researchers on his 13:30 and 13:39 words) and from what I verified myself in the live tree. Nothing here is switched on. No code before his yes.*

## 0 · In five lines
1. **The rule that decides everything:** organs are FIXED prefilters (with runtime ADAPTS that never learn); the MIND is the only place that learns — and the mind must RECEIVE, with every trait, the WHERE, the WHEN and the ACT that produced it. Today it receives none of the three.
2. **The creature today perceives and does almost nothing:** its five sampling roads are chosen by nothing; no act has a sensory consequence; the exam it sits never comes back to it; 39 % of its CPU goes to a hash of memory that is 99.6 % empty; and two mind mechanisms could not fire at all (INDUCE fixed today at the life-3b boundary; DEDUCE deferred to life 4 with its seam).
3. **G5 = the same genome and machinery, upgraded on exactly these features:** the seam contract on every organ (trait + where + when + act + whose + provenance), an error that is a SURPRISE (expectation vs input) rather than a NOVELTY (input vs memory), one canvas = one episode, acts with outcomes (the exam score returns; the first hand), a body sense, and the language in HIS order — all as lines in the genome's own syntax, each with the test that could refuse it.
4. **ONE life** on the G5 genome, its multi-exam (the nine marks + one new mark per line switched on, with ceilings and nulls measured BEFORE it), a small exploration world (drawn things + his folder + his own exam score + the shelf of programs; sound only if he gives it a voice), every claim beside its twin.
5. **What is his:** 18 questions (§8), of which six change the build; my recommendation is printed on each. Everything else is decided under the 09-05 delegation and journaled.

## 1 · His words, and the rule they make
13:30: «…the organs prefilter and get the continuous inputs, the mind is where those traits and geometric time space combined, memories are stored and also the thinking and reasoning and learning happens, not at organ level. So catching traits and prefiltration is separate then learning, so we need a genome, a life that is grown on exactly these features … update our instructions at extreme levels after deep research on each organ and other things and run a single life with it's multi testing exam and small scale environment for exploration.»
13:39: «…purely inspired and reverse Engineered from biological life and advancements added at software level. So biology says how organ works and then software is what we can add as advancements, features and upgrade the instructions.»

**The rule, as every document applied it.** Every mechanism is in exactly one bin: **FIXED** (set by the genome at development), **ADAPTS** (changes at runtime without learning: gain, adaptation, the residual after the mind's prediction is subtracted), **LEARNS** (the mind's; delivered by the organ as a trait). Where biology learns inside an organ (V1's refinement, the cochlear efferent's experience-dependence, the owl's ITD map, the cerebellum's forward model, the fly's mushroom-body output synapse, the retina's re-tuning to statistics), each document says so, bins it his way, and names the trait the fixed organ delivers instead. The bin calls he might dispute are listed in §8.

**The seam contract (the one design point every document reached independently).** Every event an organ delivers carries: TRAIT (a unit vector or a code) · WHERE (fixation position; azimuth) · WHEN (the instant, sample-exact) · ACT (which act produced it, and the expected outcome the mind sent down, so the organ can deliver the residual) · WHOSE (own / other) · PROVENANCE (front, file, offset, parameters). The three numbers go BESIDE the trait — into the episode row and the tape row — never INTO the cosine vector the SLOW area compares (a position concatenated into a compared vector makes the same shape at two places two cells: the organ doing the mind's job; and E49 measured a coordinate on every cell and it bought nothing).

## 2 · What the six documents found about the creature TODAY (the findings that change the design)
The last column says who measured it: **me** = verified by me in the live tree or on a copy of the live snapshot today; **researcher** = the Opus 5 researcher's own measurement, with the document and road; I did not repeat those.
| # | finding | where · who |
| 1 | The mind receives ONLY the 112-vector: `org.moment(x, xw, lr_scale)`; the fixation cells, the window origin, the instant, the glance order are journaled for a human and never reach the organism. WHERE, WHEN and the ACT do not exist for the mind. | EYE §0.3; `mind.py:220` · me |
| 2 | Four glances are four unrelated moments wired to one word: first-fixation-only .975 > 4-fixation .956 (life 2's own twins). The extra glances cost 1.9 pp. | EYE §3; the life-2 verdict · me (the verdict's own rows) |
| 3 | Nothing in the eye adapts: `predicted=None` hardcoded (`gaze.py:85`); SURPRISE OFF. His «the brain sends a prediction down to the organ» has no implementation. | EYE §3; `gaze.py:85` · me |
| 4 | The maker's canvas is ONE GREY PLANE ×3: max\|rg\| = max\|by\| = 0.0 exactly; life 2's folder door delivered 0 pictures. Every colour line is refused today by a one-line check. | EYE §4 · researcher (measured on a real canvas; `world.py:render_canvas` read by me) |
| 5 | The creature has NO ear: `SENSE ear letters 8` is a symbol channel; the word is GIVEN by the world-maker (his 09-15 paste: backwards). E52's front was built and never made an organ; its ablation was mis-read — the `no-filterbank` cell substituted 64-band log-mel, so FREQUENCY ANALYSIS WAS NEVER ABLATED. | EAR §0 · researcher (read from E52's own logs) |
| 6 | An ear must deliver EVENTS, not frames: 100 Hz frames = 456× the tape's 0.219 rows/s; syllables 14–36×. | EAR §1.3 · researcher (the tape rate is mine: 0.219 rows/s from life 2's record) |
| 7 | NO act of the creature has a sensory consequence: the gaze runs inside the mind on an already-delivered PNG (four crops of one buffer); the body starts exactly two senses (maker, folder); HANDS OFF; `WORLD … web 6 per hour by curiosity` is parsed (`machinery.py:259`) and consumed by NOTHING. | BODY-SENSES §3; MOTOR §0.3 · me (`body.py:372/383`, `machinery.py:259`, 0 consumers) |
| 8 | The mind reads 0 of STATUS's 11 numbers. It cannot feel its own body. | BODY-SENSES §3 · me (grep) |
| 9 | The exam the creature sits (life 2 wrote 10 files) reaches the journal — the mind's OUTPUT — and never the tape, its only INPUT: no reader in `mind.py`/`body.py`/`genes.py`. The cheapest closed loop on the estate is one publishing thread. | MOTOR G-MOT-3 · me (grep: no reader) |
| 10 | E21 (a scripted OUTCOME model: AUC 1.0, the magnitude-only twin 59 %) vs E28 (a learned pixel predictor 0.6656; 97 parameters = an 8,000-parameter GRU = a frozen random state): a forward model is written against ACT SEMANTICS, never pixels. | MOTOR §0.2 · researcher (from E21/E28's records) |
| 11 | HANDS «writes a program» (the design) vs «NOT writes» (`alpha3/src/hands.hpp:7-8`, the only implementation): rung 1 chooses from a shelf, rung 2 composes. The jail's tail: p50 1,051 ms · p99 11,010 ms · 302 of 4,135 rows hit the 20 s wall → an act that can hit the wall never runs on the mind's thread. | MOTOR §0.4–0.5 · me (`hands.hpp:7-8` read); the jail's tail · researcher (`alpha3/run/roads.jsonl`) |
| 12 | MODULATION failed twice because the creature computes NOVELTY (1 − max cos to memory) and calls it SURPRISE; a look-alike new thing cannot spike by construction (Barto/Mirolli/Baldassarre's line). Three errors that can are REPLAYABLE on life 2's 18,959-row tape with no new life; `_misfire` already computes the comparator and PREDICT never reads it. | MIND-MEMORY G-MIND-3 · researcher (the definitions and the arms); the MODULATION FAILs · the verdicts |
| 13 | `state_hash()` hashes W in full (32 MB) on EVERY eye canvas (`mind.py:235/253`): 32.6 ms ≈ 39 % of life 2's CPU bill, while ≥ 99.6 % of the block can never be non-zero. A pin-moving repair, not a gene. | MIND-MEMORY R1 · me (the full-W hash per canvas at `mind.py:235/253`); the 32.6 ms / 39 % · researcher (a solo probe) |
| 14 | The 26.53 ms "canvas cost" is the median over ALL consume calls on a tape that is exactly half ear rows (one dict assignment) and half eye rows (life 3: 1,359 · 1,360): per eye row ≥ 33 ms; the eye's own 7.4 ms (4.77 ms of it a Python loop; 0.46 ms vectorised) is nearer 15 % than 28 %. | MIND-MEMORY B · me (life 3's tape: ear 1,359 · eye 1,360); the eye's ms · researcher |
| 15 | Tononi's SHY vs #227: not a contradiction — SCALE (norm down, never up, never removed) IS proportional down-selection; E48's ×0.98 decay was not. Davis & Zhong (forgetting is the brain's default) vs #227: a live contradiction, resolved HIS way and escalated (Q). | MIND-MEMORY §0.4 · researcher (the reading of the sources); SCALE's arithmetic · the code |
| 16 | INDUCE compared a sight cell id to a words index (`think.py:411`): 20 of 21 words could never induce; life 3a's 12 rules were all «bar» by a coincidence of ids. FIXED at today's boundary (one key), pinned by a test whose id spaces are disjoint, the reader given a REACH control (VOID on life 3a's record — caught). | MIND-THINKING-LANGUAGE §0; PREREG §18 add. 2 · me (on a copy of life 3a's snapshot; the test; the control) |
| 16b | With INDUCE able to fire, every inducible word is a rule item on every think and CURIOSITY worked rules almost exclusively (175 of 181 thinks in the fixed replay of life 3a; ten think-counter tests formed no belief) → a fixed mind rule at the boundary: the KIND chosen first, fairly; CURIOSITY within the kind. | PREREG §18 add. 2 · me (the suite; the replay) |
| 16c | 79 % of life 3a's thinks (168 of 213) went to «due» items the think step can never score (a filed prediction is scored when its word is next shown, not in the think step): dead weight in the pool, pre-existing; kind fairness cuts it to a quarter, and life 4's clause removes it. | PREREG §18 add. 2 · me (life 3a's journal) |
| 17 | DEDUCE's routable branch is unreachable by construction (0 of 619 cells belong to two words); its fix opens a permanent clash stream unless `believe()`'s rule 2 is closed in the same commit → life 4. ABSTAIN's `close` can never be returned under the ratio form; `RECALL k=3` reaches no call site; `induce()` costs 136.5 ms against a 21.7 ms canvas. | MIND-THINKING-LANGUAGE §0 · researcher (measured on a copy) |
| 18 | The actionable doubt is 12 of 2,430 exam items (0.49 %): the creature almost never does not know. The world is too easy for metacognition to be graded. | MIND-THINKING-LANGUAGE §5 · researcher (2,430 life-2 exam items) |
| 19 | E21's efference-copy instrument PASSED on this box (120/120); no organism has one. E15 refuted the fly's expansion as a FEATURE LEARNER; nobody has tested it as a RECALL HASH — the creature's recall is a cosine over cells, exactly where the claim applies. | BODY-SENSES §0, §4.7 · researcher (E21/E15/E22's records) |
| 20 | The animal register was extended per organ (eye rows 18–27, ear 18–24, body 18–28, motor M1–M10 — the numbering collided; one renumbering owed at the merge). | all four organ docs · me |

## 3 · The organs of G5 — FIXED and ADAPTS lines only; what each delivers
Lines are in the genome's own syntax (`NAME  value words  # source`). "parser change" = the machinery must learn a word; "extension" = it parses today. Each line's refusing test is in the document named.

**EYE** (EYE.md §4; BODY-SENSES §4.3–4.4)
```
DELIVER  where fixation when instant act glance     # G-EYE-1: the seam contract; fields on the episode + tape row, never in the cosine (parser change)
BIND     glances per canvas                          # G-EYE-2 (= G-MIND-2): one canvas = one episode; bar .975 = the first-fixation twin; the diagnostic on life 2's journal decides BIND vs `fixations 1`
SURPRISE floor 0.05 predicted last-canvas            # G-EYE-5: the mind's prediction reaches the organ; the organ reports the residual (parser change; breaks earlier tapes' replay → a life boundary). CAVEAT (MOTOR §0.3): gaze's `predicted` slot is the PREVIOUS FRAME's map, not a top-down socket — what it accepts is read before this line is written
GAZE     surprise fixations 4 grid 16 canvas 128 glance 32 ink border fovea 1 correct 1   # BODY 4.4: a coarse view + one corrective look (the mole's 11th ray; G-EYE-6)
#OFF RETINA … opp3 …                                 # G-EYE-3 colour: REFUSED until the door has delivered ≥ N coloured pictures (rg ≡ 0 today)
#OFF RETINA … dog3 hogcells8x6 …                     # G-EYE-4 a genome-set front beside the pretrained tower: predicted to FAIL (G0 −0.19), proposed for the mutable front it would give
#OFF EVENT / DEFOCUS / MICRO / EYES2                 # declared OFF with reasons (nothing in the world moves; flat renders; the renderer jitters; one canvas at a time)
```
Not a gene: the retina vectorised (5.42 → 0.46 ms a canvas; a new sha-pin + byte-identity on life 2's tape).

**EAR** (EAR.md §4) — only if the world has sound (EAR §5's own caution: an ear with nothing to hear passes its own tests and teaches nothing). T7 first: count the events an hour of real audio would publish against the tape's rate BEFORE the sense is armed.
```
SENSE    ear-sound wav 16000 mono · COCHLEA gammatone erb 32 from 50 to 7800 · HAIRCELL rectify power 0.3 · AGC per-channel fast slow clamp 0.1..10
ONSET    derivative rectified per band · MODBANK 2-4 4-8 8-16 16-32 hz · EVENT publish on onset peak; prominence 2 db gap 60 ms
TRAIT    sound band 32 + onset-shape 4 + level 1 unit · WHEN instant sample-exact · WHERE itd us ild db · OWNVOICE subtract predicted; flag the event · PROVENANCE front file offset params
AREA     sound from cochlea · MEET sight sound · MEET sound words
#OFF ALARM / FOVEA / RHYTHM / WIDE                    # the moth, the bat/frog, the cricket, his own «no 20 Hz–20 kHz floor»
```
The one test E52 could not do: a plant whose message is in the FREQUENCY path (two neighbouring carriers, identical amplitude and schedule; the envelope twin at chance, measured not assumed).

**BODY** (BODY-SENSES.md §4)
```
SENSE    body every 60 s fields moments births arrivals budget_left refused restarts mind_ms rss   # 4.1: the readings; the DRIVE stays the mind's
SENSE    smell kind size folder age; before any picture is opened                                # 4.5: the cheap wide channel before the expensive contact sense
COPY     hands expect before the act; organ delivers residual; mind keeps both                    # 4.2: the efference copy — a PRECONDITION on the first act, OFF until HANDS/the web door
SENSE    touch from hands: exit rate stalls retries bytes                                          # 4.6: OFF until HANDS
```

**HANDS / ACTS** (MOTOR-HANDS.md §4)
```
ACT      glance open ask                                    # G-MOT-1: only what is reachable now (his Q); fetch/run/say join as they are built
OUTCOME  act to episode; error grades it; ranks replay      # G-MOT-2: the existing modulator pointed at a new source; plant = an act whose outcome the world-maker knows (root/truth) and the mind does not
SIT      exam every 2000 canvases; the score returns as a sense   # G-MOT-3: one publishing thread; the file selected digit-prefixed, never by pointer; refuse if the score is constant (life 2's slid .995 → .952, so it moves)
HANDS    jail alpha3/hands/jail_run shelf world/programs cpu 10 mem 512 wall 20   # G-MOT-4: choose from a shelf (rung 1), compose (rung 2); off the mind's thread
PROBE    doors by want; rate by surprise; order is a seed function                 # G-MOT-5: the sampling act is chosen, not scheduled
MOUTH    emit sentence; gate refuses uncited; abstention reported                  # G-MOT-6: the mouth is the mind's fixed emitter (SENTENCE composed, judged, never next-token)
WORLD    … consequence: what he opens changes what is drawn next                    # G-MOT-7: a world that answers back
#OFF BABBLE / EXPLORE                                       # no ear to grade a babble; one live verb has nothing to vary
```

## 4 · The mind of G5 (MIND-MEMORY.md §4; MIND-THINKING-LANGUAGE.md §4)
```
MOMENT   keys sight words surprise where when act source     # G-MIND-1 (= G-EYE-1): the episode row carries where/when/act/source (parser change); #OFF PLACE — E49's coordinate-on-every-cell is NOT this
PREDICT  arrival and glance signed; error scales delta 0.5..2.0; ranks replay; grades act   # G-MIND-3/6: the error is a SURPRISE — arms A (the never-heard word, held 3 showings) and C (the comparator `_misfire` already computes) admissible; B needs the mark restated; DECIDED BY REPLAY of life 2's tape, not by a life; the zog plant every arm must spike on
SLEEP    every 2000 moments replay 200 by gain need           # G-MIND-4: Mattar & Daw's EVB — replay what would CHANGE an answer, not what was most surprising when it happened (parser change)
THRESH   cell own bcm                                          # G-MIND-5: a threshold that is the cell's own (BCM), beside KWTA/SCALE/MERGE
CURIOSITY interests 50 by learning-progress …                  # G-MIND-7: curiosity by learning progress, not popularity
TRACE    eligibility 3 moments                                 # G-MIND-8: what happens later can change what a moment learned
INDUCE   rule from 5 episodes no counter                       # the cluster = the word's OWN cells (fixed today); the reader's reach control
THINK    every 10 canvases; kinds fair                          # the pool-composition rule (found by the suite today): the KIND is chosen first, uniformly; CURIOSITY chooses within it — or rule items starve the beliefs (175 of 181 thinks were rules in the fixed replay)
DEDUCE   one step                                              # life 4: `word in s` + believe() rule 2 closed in the same commit; graded VOID until then
ABSTAIN  second/best > 0.85 margin cos<…                       # so that `close` can exist (both forms parsed; today only one is)
CONFIDENCE from decision variable; hypercorrection             # THINKING 4.4: confidence computed per decision (ADAPTS); a confident error teaches more (LEARNS)
WHY      addresses                                             # the ask door's «why» = the cells/episodes/edges `questions.why()` already returns (his Q3: the addresses, or a story)
SENTENCE two-word frames is near under-judge                   # in HIS order: stream → words the mind cuts → frames; CONDITIONAL on a stream existing (today the word is given)
BELIEF   clash opens never overwrites; entrench by evidence     # AGM's minimal change with an entrenchment ordering (his Q2: evidence / age / confidence = three creatures)
#OFF FORGET / RECONSOLIDATE / SR / SEPARATE / PRESSURE         # OFF with measured reasons (0/32 disuse arms beat random; reconsolidation and byte-identical REPLAY cannot both be true; no transitions to map; E15 lost; sleep's trigger not gradable)
```
Not genes: R1 the `state_hash` repair (hash the live block; the pin moves; row-for-row digest agreement live vs replay on life 2's tape); the recall-hash test of the fly's expansion (a test on the exam's recall, never a gene until it wins).

## 5 · The ONE life — the multi-exam and the small world
- **ONE life, his 13:30 word — not a ladder.** `G5.genome` = `G4.genome` + EVERY admissible line above ON at once, one code version for the whole life (REPLAY identity). What is decided BEFORE the life costs no life: the error arm (A or C) by replaying life 2's tape; BIND vs `fixations 1` by the diagnostic on life 2's journal; the repairs of §6. What is NOT in the first life, each because its precondition does not hold today and a one-line check says so: the ear (no sound in the world), HANDS/COPY/touch (no act yet — SIT and OUTCOME on glance·open·ask are the first acts), colour (rg ≡ 0 until the door delivers pictures). Those join at the next boundary when their checks pass — a second life, not a rung of the first.
- **Before the life (the discipline of #222/#228/#231):** every new mark's ceiling and null measured on the twin's own structure and printed beside the bar; every plant placed where its mechanism can fire (the colour lines, the ear, touch/copy are REFUSED today by one-line checks); the cost of each line measured in the shape the mind runs it (per eye row, not the mixed median); the closed lives (1, 2, 3a) as the reader's controls.
- **The multi-exam:** the nine marks of §5/§16/§18 + one mark per line ON, read by the pre-written reader at 24 h, with a 2 h smoke as the reader's positive control; each mark beside its twin (`--blind <field>`; the frozen twin; the shuffled twin; the random genomes).
- **The small exploration world:** the maker's drawn things on their cadence (with COLOUR the day the door delivers it, and MOTION only if a change sense is ON) + his folder + his own exam score returning + a shelf of programs the jail runs + (his call) sound. The world answers back: what he opens changes what is drawn next.
- **The readings that would refuse the design as a whole:** DELIVER's parity control (every existing mark byte-identical to life 2's when nothing entered the cosine); BIND's bar (.975, the first-fixation twin); the error's zog plant; SIT's constant-score refusal; OUTCOME's predictable/unpredictable pair with E21's magnitude twin.

**Said once:** today's two code changes (the INDUCE key; the kind-fair think chooser with the park filter) are G4 §14 repairs at a life boundary — declared machinery that ran wrongly, fixed before a life — not G5 lines; «no code before his yes» holds for everything in §3–§5.

## 6 · Repairs that are not genes (do before the life; each a pin that moves)
1. `state_hash` over the live block only (39 % of CPU) — digest agreement row-for-row on life 2's tape; the mind-parity pin moves and the register says so.
2. The retina vectorised (5.42 → 0.46 ms) — a new sha-pin; byte-identity on life 2's tape.
3. The cost columns re-based on the per-eye-row figure (≥ 33 ms), never the mixed median.
4. The web door: parsed and implemented by nothing — either implemented as an ACT with OUTCOME, or the line removed from the genome until it is (a declared gene the machinery does not run refuses, by the genome's own rule).
5. `RECALL k` reaching a call site, or the gene removed; `ABSTAIN` parsing both forms.
6. A think-step cost in STATUS (induce 136.5 ms vs a 21.7 ms canvas: the think step needs its own budget, off the eye's cadence).
7. DEDUCE's reachability + the clash seam (life 4).
8. A pool item that can do no work leaves the pool (the «due» items; and a wordless sight already filed is not re-filed on every sight think) — life 4.

## 7 · What the documents disagreed on, and how it was settled (his pastes > his compiled Q&A > agent syntheses)
R1 (words pre-cut) vs his 09-15 paste (stream first): HIS way, and the disk agrees (E43b's .515 ceiling vs E47's .487 peel). His 09-02 order (alphabets → words → sentences) vs his 09-15 paste: the later word stands; the 09-02 order becomes the MOUTH's order. G4-DESIGN row 2b (TRAITS learned in the eye) vs 13:30: his way; the record agrees (`#OFF TRAITS`, margin −0.116). Tononi vs #227: no contradiction. Davis & Zhong vs #227: his way, escalated. The superior colliculus as «a learned these-go-together detector» (his paste) vs 13:30: split — a FIXED window, the association the mind's (MEET + HEBB). E49 (a coordinate on every unit bought nothing) vs «traits × geometric time space»: two different claims — fields on the episode row, never on the cell.

## 8 · The questions that are his (18 from the six documents; the six that change the build first)
**Change the build:**
1. **(MIND-MEMORY Q1) Should the moon be a surprise?** Arm A (a never-heard NAME is the event), B (a thing with no exact memory near it), C (the winning cell's answer disagrees with the word that arrived) are three creatures. *Recommendation: decide by REPLAY of life 2's tape (no life spent), C first because it costs nothing and its denominator is well-behaved.*
2. **(MOTOR Q1) When the creature acts, what does REPLAY mean?** A jail run is not reproducible. *Recommendation: the outcome is a RECORDED tape row that replay reads — the creature can never re-do an act, and byte-identity stays the one check it has never failed.*
3. **(MOTOR Q3) Where does the first consequence come from?** *Recommendation: his own exam score returning (SIT), then his folder, then the jail; the open web is his alone.*
4. **(EAR Q2) Where does sound come from — his 09-15 subtitled-video road, LibriSpeech, or the drawn world given a voice?** *Recommendation: no ear in the first G5 life unless he wants one; if he does, the drawn world given a voice (simultaneity by construction).*
5. **(EYE Q1) Is the pretrained tower an organ he accepts, or a debt?** It never changes in a life (FIXED in operation) but no road on this box could grow it. *Recommendation: keep it and say so; G-EYE-4's genome-set front runs beside it as the mutable candidate, expected to lose.*
6. **(MIND-MEMORY Q3) Should remembering change the memory?** Reconsolidation and byte-identical REPLAY cannot both be true. *Recommendation: no — the exam does not change him; the tape is the memory that never lies.*

**Design choices (my recommendation in brackets):** EYE Q2 does the gaze belong to the eye or the mind [the eye keeps its cheap rule; CURIOSITY chooses which DOOR, not which pixel — until a fixation can be wrong] · EYE Q3 what is his «context» when he has no page [source/arrival/time as fields — never the folder name, which is the answer] · EAR Q1 events or frames [events; a held vowel is an event with a duration] · EAR Q3 uniform bands or bands dense where his world speaks [uniform until there is a world that speaks] · BODY Q1 does the body get a sense of itself [yes, the readings; the drive is the mind's] · BODY Q2 is the efference copy a precondition on the first act [yes] · BODY Q3 may a sense organ be a thing the creature MADE [not in the first life] · MOTOR Q2 the act set [glance · open · ask] · MIND-MEMORY Q2 should he ever forget [no mechanism reaching the cells; the FAST ring's age stays] · THINKING Q1 reason about what he does not know when he almost never does not know [make the world harder first] · THINKING Q2 what he gives up when he contradicts himself [entrench by evidence] · THINKING Q3 «why» = the addresses or the story [the addresses now; the story is the mouth's].

**Bin calls he might dispute (each stated in its document with what changes if he rules otherwise):** the pretrained tower FIXED; Hosoya's retina ADAPTS on a ≤ 10 s memory; the gaze FIXED though a saccade is an act; the MOC efferent ADAPTS while an experience-set gain bias LEARNS; Knudsen's ITD map LEARNS (mind); the SC window FIXED / the association the mind's; the mormyrid's ELL SPLIT; VOR gain LEARNS; the mushroom body's plastic layer the mind's; the cerebellum's forward model ADAPTS (if he prefers the biology, it is the ONE LEARNS the body gets, named); SCALE ADAPTS; CURIOSITY ADAPTS; PREDICT ADAPTS while the surprise it freezes LEARNS; the working-memory gate FIXED / its policy LEARNS; PARK's 3 FIXED (no biological warrant for any small integer — biology gives rates and hazards).

## 9 · What this design does not claim
- That any line will help. Each carries the test that could refuse it; G-EYE-4 is proposed expecting to fail; three of the six documents say their central line has a real chance of a clean null.
- That the creature needs an ear, hands or colour today: each is refused by a one-line check on the world as it is, and the checks are printed in §3.
- That the numbers in the documents are all primary: ~600 claims carry roads; `[secondary:]` on this estate means a search result that named the primary and quoted its number — before any number is written into a growth line, its primary is fetched at its open mirror (SOLUTIONS #196).
- That the six documents agree on numbering: the animal register's rows collided (one renumbering owed); the cost columns of EYE/EAR are re-based by MIND-MEMORY's finding (§2 row 14).
- That life 3b's verdict tomorrow decides G5: it decides W3-2 on the fixed key and reads MODULATION FAIL by the mechanism named in §18; G5's error line is decided by replay before any G5 life.

*Sources: `docs/organs/EYE.md` · `EAR.md` · `BODY-SENSES.md` · `MOTOR-HANDS.md` · `MIND-MEMORY.md` · `MIND-THINKING-LANGUAGE.md` (all committed on master today) · `docs/organs/BRIEF.md` (his words) · `docs/organs/INVENTORY-2026-09-21.md` · `docs/G4-PREREG.md` §18 + addenda · the life-2 verdict `runs/g4-verdict-life2-20260921-1215/VERDICT.md` · the smoke and its control `runs/g4-smoke-life3-2h*/`.*
