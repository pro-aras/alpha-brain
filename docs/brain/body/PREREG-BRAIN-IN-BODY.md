# PREREG — BRAIN-IN-BODY: one brain organ, inside the creature, graded on his six tests

*Drafted by Claude (Fable 5.1, the seat), 2026-09-28 20:21 +0400, for the co-signature of Opus 5.5. Law once both names stand on the FINAL text (SOLUTIONS #244 (6): sign again after every co-signer edit).*

**His order (2026-09-28 19:56 +04, verbatim):** «The brain full build continues and should get finished today. Check all the research and documentations, and tests and experiments and find the failing parts and fix them and test the whole brain as one and then test it in a single organism body and test the full organism as one.»

**The failing parts** are listed whole in `FAILING-PARTS.md` (same folder; read-only audit, 20:13). The seams are in `INTERFACE-BRAIN-ORGAN.md`.

## 0 · In plain words
Three rungs, in his order. Each rung changes ONE thing.
1. **The brain alone.** The working parts joined into one organ. It must give the SAME answers as the scored run, item by item. This is a join check. It can find a defect; it cannot find a result.
2. **The brain in one lean body.** A `BRAIN` line in a genome. The mind feeds the brain what the eye sees and the ear hears. A parent names ONE thing in view. Then the six tests are asked through the tape. The same tape is replayed WITHOUT the brain (the twin). A shuffled-name world is the null.
3. **The full organism.** Every ALPHA4 organ on, plus the brain, under a real unit.

**Predicted before any run** (so a surprise is visible): the brain in the body answers exactly as the brain alone. So tests 1 and 3 pass, «is it here?» passes, «I don't know» on never-taught shapes FAILS at 0.65–0.73 (its cause is known), and test 6 (pooled) PASSES at 20261102 (0.768, n 56) and FAILS at 20261103 (0.607, n 61). Tests 4 and 5 are new tonight and have no record. *(co-signer: test 6's prediction computed from the record's pooled counts, not the fresh-only «weak»)*

## 1 · The world and the lives
- The world is `brain/scene/world.py`, unchanged. World seeds 20261101 / 02 / 03. 10,000 training scenes. «dax» is met ONCE, at scene 2,700.
- The sitting asks the FRESH test set (seeds 20261401 / 02 / 03), then the older set (20261201 / 02 / 03).
- **Every mark is graded on the FRESH set alone**, as S1b-1R was. The older set gives READINGS only, with two exceptions: **test 6 pools its items over both sets**, because 42 items cannot reach n ≥ 30 (measured n: 27 and 29; pooled 27 + 29 = 56 at 20261102, 29 + 32 = 61 at 20261103); and **the twin's M3 comparison pools M3 over both sets** (§3, THE TWIN). The two sets' scenes are different draws (`m6_scene` / `m3_scene` of test seeds 2026140x vs 2026120x). *(co-signer: pooled n from `<ws>/fresh/marks.json` + `<ws>/marks.json`; the second exception is the twin's power fix)*
- Lives under the real unit, one at a time: a pre-flight (300 scenes), then one lean life per world seed, then the full organism.
- The twin and the null are REPLAYS, not lives. The world never reads the mind's answers, so a tape replayed under another genome IS the life that genome would have lived. A replay is the same mind code at machine speed.

## 2 · Rung 1 — THE BRAIN ALONE (a gate, not a mark)
`tools/brain/gate_alone.py`: the organ, fed the scored run's cached glances in order, answers the scored run's fresh questions. **Bar: every answer equal to `scene-s1b1r/<ws>/fresh/arms/A-RW-R/answers_10000.json`, all three seeds; and every older-set POINTING answer (M1, M2a, M3, M6) equal to `scene-s1b1r/<ws>/arms/A-RW/answers_10000.json`'s `answers`** (pointing is road-free and A-RW-R trains as A-RW, so these are the brain's own; that file's what / say answers ran S1b-1's roads and are not a reference). *(co-signer: two marks now pool the older set; without this they had no offline reference)* A difference is a join defect. It is fixed, and the gate is run again. Control: one changed training word must make the gate fail.

## 3 · Rung 2 — the marks (read from the life's own tape and journal)

**The grading functions are S1b-1R's own** (`brain/scene/marks.py`, `run.bars_r`), with its reading rules. The oracle readings beside each bar are S1b-1R's record at the same seed.

| test | the mark | the bar | the ceiling, printed beside | predicted |
|---|---|---|---|---|
| — | **PARITY**: the life's answers vs rung 1's, item by item | 100 % equal; every difference named with its cause | — | equal |
| 1 point | **M1**, on items where the gaze COVERED the target, 2–3 things | ≥ 0.90 × P-ORACLE-RW and ≥ 0.80 × P-ORACLE | P-ORACLE 1.000 on the covered items at every seed (n covered 202 / 188 / 192 of 244 / 230 / 235); M1 over ALL items is printed beside (record: 0.81; its ceiling is P-ORACLE's ALL, 0.828 / 0.817 / 0.817) *(co-signer: the recall figures were stage −1's, seed 20261100; the covered mark's ceiling is P-ORACLE's)* | PASS (0.985–0.990) |
| 2 refuse | **M2a** absent thing → «none» | refusal ≥ 0.80 and false refusal ≤ 0.10, the per-half rule | P-ORACLE 0.995–1.000 | PASS (0.81–0.89) |
| 2 refuse | **M2b** never-taught shape → «I don't know» | ≥ 0.80 | exact attributions reach 0.83–0.90; n = 8 per shape | **FAIL (0.65–0.73)** — the store's attributions; houses and trees |
| 3 compose | **M3** never-heard colour × shape pairs | ≥ 0.80 × P-ORACLE | P-ORACLE 1.000; n covered 58 per seed | PASS (0.966 / 1.000 / 0.983) *(co-signer: exact record)* |
| 4 explain | **M4a**: «why <word>?» → ≤ 8 of its own episodes, **chosen among the word's episodes with ≥ 2 hypotheses in view** (INTERFACE §3's order, strongest responsibility first, ties by the earlier moment, applied to those). Each cited episode carries `hyp` (the cited index) and that moment's `fix` and `hyps` (as Addendum 1's answer rows do). Graded once, on the FRESH sitting's `why` answers | EXIST = 1.000 (a wiring pin, never evidence: each cited moment is on its own tape and its ear rows carry the word). CARRY ≥ 0.90 per seed, pooled over the words (the cited hypothesis' thing — `marks.hyp_label` over `world.fixation_thing` of its cells, against that moment's truth file, M1's own rule; no thing = not CARRY — truly has the word's property) and above the 95th percentile of 20 shuffled-citation draws (draw k: each cited episode's hypothesis replaced by one drawn uniformly among that episode's `hyps`, generator `substream(ws, "m4-null:<k>")`, in citation order) | a perfect attributor reads 1.000; the null's expectation ≈ 0.57 [inferred: by things, 0.570 / 0.573 per seed]; n = 13 mature words × 8 = 104 per seed; «dax» (one meeting → `unknown`) is listed apart; every other word has ≥ 465 citable episodes | no record *(co-signer: a 1-hypothesis episode stores responsibility exactly 1 (`learners.py`: R = Pm / ΣPm) and every mature word has ≥ 313 of them, so the unrestricted rule cites only those: CARRY and every shuffle read 1.000 and «above the p95» can never hold. The cells are required because without them no grader can map a citation to a thing. Population fixed, bar unchanged; fixed by arithmetic, no builder output read)* |
| 5 misuse | **M5**: a phrase of two words of ONE type («red blue»). **The items (§M5):** one per FRESH regular test scene, 400 per seed; the type uniform over the three; two distinct words of it uniform (size has one pair), in a uniform order; «dax» never used (one meeting: outside the Ear's mature cover); generator `substream(ts, "m5-item:<item_id>")` | refused (misuse or none) ≥ 0.90; NAMED as misuse ≥ 0.80; valid phrases (every M1 + M3 item, 455 / 455 / 458) called misuse ≤ 0.05; never-heard pairs of M3 called misuse = 0 | the ear's types equal the world's at every reading point on record, so 1.000. No item is valid by accident (two words of one type are true of no thing, `world.word_true_of`) and none is unheard (every word said ≥ 809 times per seed) | no record. **What it measures:** `Ear.cover` is built from which words share an utterance, and the shuffled null moves WHOLE utterances, so the null has the same types and passes M5 too. M5 is evidence of the Ear's grammar, not of meaning; it is not read against the null *(co-signer: INTERFACE cites «PREREG §M5» and no generator existed anywhere; defined here)* |
| 6 one meeting | **M6**: point at «dax», pooled over both sets, where the gaze covered it | ≥ 0.70 with n ≥ 30 | NOT GRADABLE at 20261101: the gaze never looked at the dax in its one scene (an organ limit, read from the training tape before any ask: the dax scene's `brain` learn row carries that canvas's `fix` and `hyps`, and `meeting_seen` must equal the record's False / True / True) *(co-signer: learn rows carried no fixations, so the tape and journal could not show whether the meeting was seen)*. Elsewhere P-ORACLE 1.000 on the covered items of both sets. Chance is printed | pooled: **PASS 0.768** (43 / 56) at 20261102; **FAIL 0.607** (37 / 61, chance 0.473) at 20261103 — fresh 0.778 (21 / 27) and 0.483 (14 / 29), older 0.759 (22 / 29) and 0.719 (23 / 32) *(co-signer: the mark is pooled, so the prediction is the pooled count; older = `<ws>/marks.json`, A-RW pointing, the same learner)* |
| speech | SPOKEN, TRUTH, TRUTH-NEED, MINIMAL, ORDER, READ-BACK, DECLINE | S1b-1R's own | TRUTH-NEED and ORDER are gaze-bound (the need is seen on 23–27 of 60); READ-BACK is a wiring pin, never evidence; DECLINE is organ-bound | as S1b-1R: TRUTH fails at seed 1, TRUTH-NEED at 2 seeds, ORDER underpowered |

**M4 and M5 bars were set at 20:21 +0400, before builder A's first measurement reached the seat.** Builder A measures their ceilings on the rung-1 learners. Because rung 1 proves those learners ARE the life's brain, that measurement is the result, one step early. It is reported as such. No bar moves after it is read.

**M4b (a readable rule that re-derives answers on unseen items) is NOT BUILT tonight.** Reason: the word map's rule is a prototype and a band; a grader that rebuilds it from the cited episodes alone is a second build. It goes on the calendar with a date at the wrap.

**THE TWIN** (the same tape, no BRAIN line; the asks answered through the organs' own memory). It is `BRAIN-LEAN-TWIN.genome`. INTERFACE's `--blind brain` on `BRAIN-LEAN` is a second road to the same mind. Their non-answer rows must be byte-identical, or the disturbance check below reads a naming difference. *(co-signer: the two texts named the twin two ways)*
- Read per mark, per seed, on the SAME items, paired.
- **Bar: the brain is above the twin on M1 and on M3 by ≥ 0.10, exact sign test on the discordant pairs, p < 0.001, at every seed.** M1 per seed on the fresh set (n 202 / 188 / 192). **M3 pooled over both sets** (n 117 / 115 / 113). The test is one-sided (the brain better). *(co-signer: p < 0.001 needs ≥ 10 discordant pairs all for the brain; at M3's n = 58 that is a margin of 0.172, so the declared 0.10 could not bind (brain 0.98 vs twin 0.85 would FAIL at p = 0.004); pooled, 0.10 binds. Population fixed, bar unchanged)*
- **The twin is read FORCED, as the brain is.** `answer_point` always points; the organs' road may return `point: None`. The grader reads such an answer as a uniform draw over that row's `hyps` by the item's `marks.tie_rng`, and prints the count. *(co-signer: otherwise the twin scores below chance and the brain wins partly by default)*
- If the twin matches the brain, the finding is «the brain adds nothing over the cells». That is a result, stated as plainly as a pass.
- The twin must be ABLE to answer (#228): **its forced M1 must be above S1b-1R's null p95 at that seed (0.605 / 0.666 / 0.625).** At or below it, the organs' road cannot point by name; the comparison then reads VOID, never PASS, because «brain > twin» would only say the brain can point. Its share of asks answered with a thing or a word is printed. *(co-signer: «answers nothing» was the only VOID case; a twin at chance answers and still isolates nothing)*
- **Marks the twin cannot answer by construction:** M4 (the organs' `why` → `unknown`, unless ASK's own `why` road exists, in which case M4 is compared) and M5 (the organs' road has no misuse act). They read NOT COMPARED, never a brain win. On M2b an arm that abstains scores by default, so the twin's M2b is read only beside its NAME rate on trained things.

**THE NULL** (the parent's utterances shuffled across scenes):
- The distribution is S1b-1R's own 20 derangements per seed, for this same learner.
- **Bar: the life's M1 and M3 above the null's 95th percentile.**
- One shuffled tape (k = 1, world seed 20261102) is replayed through the mind. Its answers must equal the offline null's at k = 1, item by item. That is what lets the offline distribution stand for the body.
- **The record keeps only the null's scores** (`fresh/nulls/01.json`: m1 0.5904 on n 188, m3 0.5690 on n 58), not its answers. So the offline k = 1 null is re-run by `run.run_null`'s own training and answering (≈ 3 s CPU), its answers kept, into a NEW folder, never the record. Its m1, m3, n_m1 and n_m3 must first equal `01.json` exactly. The item-by-item comparison covers the items the offline null answers: M1 and M3 only. *(co-signer: as written the comparison had nothing to compare against)*

**The brain does not disturb the organs:** on each life's tape, every journal row that is not the brain's is byte-identical with and without the brain, and the organism's final hash is equal. Bar: identical.

**Replay identity:** each life's tape replayed gives the life's own brain rows and answers, byte for byte. Bar: identical.

## 4 · Rung 3 — THE FULL ORGANISM (`BRAIN-FULL.genome` = ALPHA4 whole + the scene world + the brain)
| mark | bar |
|---|---|
| ALIVE | exit clean; NRestarts 0; 0 mind crashes; 0 sense restarts; the mind's backlog ≤ the feed's bound + one moment, read as a SERIES |
| EVERY ORGAN MOVES | each counter ALPHA4's own check reads (cells born, thinks, sleeps, exam sits, episodes) rises during the life; an organ whose world gives it nothing to do is named, not failed |
| THE BRAIN IS THE SAME BRAIN | its answers equal the lean life's at the same world seed, item by item |
| NO DISTURBANCE, REPLAY IDENTITY | as rung 2 |

World seed 20261102 (the dax meeting was seen there). The other worlds keep their own clocks; the scene world feeds by the mind's backlog.

## 5 · What each outcome means
- **Rung 1 fails and cannot be fixed tonight** → nothing enters the body. The defect is the night's finding.
- **PARITY fails in the body** → the body's eye or the wiring differs from the offline road. No mark of that life is read until it is named.
- **A predicted FAIL fails** → the record stands; the part stays on the failing list with its fix dated.
- **A predicted FAIL passes, or a predicted PASS fails** → a difference between body and bench. It is diagnosed before it is reported.
- **The whole brain «passes his six tests» only if tests 1–6 all pass at every gradable seed.** On the record as it stands tonight that will not happen: M2b is predicted to fail, M6 is predicted to fail at 20261103 (pooled 0.607), and M4b is not built. *(co-signer: M6 added from the pooled record)* The verdict says so in its first line.

## 6 · Cost rule
- The pre-flight prices one canvas through the mind, lean and full, at a steady load, load recorded.
- A lean life projected over 60 min, or the full life over 3 h, is reported to him with its price before it starts. It is not shortened: a shorter life is a different brain.
- Nothing else runs beside a life except its own twin and null replays, and those only after the life has closed.

## 7 · THE FIX RUNGS (after rung 2's first life; one difference each)
A fix is tried on the bench first, then lives.
- **Every fix is graded on a test set NEVER used before** (new test seeds 20261501 / 02 / 03, generated before the fix is written). The fresh set has now been read three times; a fix chosen on it would be the exam sat by its own author (#158).
- **F-M6, the instrument and its one cause:** why seed 20261103 reads chance (which thing the one meeting was written to, against where the moon was). A diagnosis first; no fix is named before it. When a gate is named, it reads M6 over ≥ 84 new items per world seed: 42 items give 27–32 covered on record, below n ≥ 30. *(co-signer: the new set's 42 M6 items would be UNDERPOWERED by arithmetic)*
- **F-M2B, the reader from the learner's CONFIDENT meetings only** (the record's first option). Gate: M2b ≥ 0.80 on the new set at every seed, with M1, M2a and M3 not lower than the law learner's on the same new set by more than 0.02. P-ORACLE-RW on the new set is printed beside as its ceiling (0.833–0.896 on the fresh set); where it is below 0.80 the gate reads CEILING-BOUND, never FAIL. *(co-signer: «every seed», «the law learner's on the same set» and the ceiling were unstated)*
- **The mixture likelihood** is not started tonight: no number on record supports it, and it changes the learner that passes tests 1 and 3.
- The look-again act changes the eye's road and every gaze-bound ceiling. It is not started tonight.

## 8 · The co-signer's walk
*Opus 5.5, 2026-09-28 20:35 +0400. Every n is counted from S1b-1R's own files: `<ws>/fresh/{marks,keys}.json`, `<ws>/marks.json`, `fresh/nulls/*.json`. Scripts are in `/data/dev/brain-runs/organ/prereg-review/`: `count_marks.py` (n and values per set), `m4_population.py` (M4's episodes and its null, by world arithmetic), `sign_power.py` (the twin's sign test). No builder output was read.*

Each line reads: n per seed · ceiling · bar · reachable? · failable?
- **Rung 1 / PARITY**: every answer in the fresh file, plus the older set's 395–398 + 400 + 60 + 42 pointing answers · 100 % (the same code) · 100 % · yes · yes (the planted one-word control).
- **M1**: 202 / 188 / 192 covered · P-ORACLE 1.000 · 0.887 / 0.895 / 0.900 · yes (record 0.985–0.990) · yes (null p95 0.605–0.666).
- **M2a**: 400 refusals; false refusal on 202 / 188 / 192 · P-ORACLE 1.000 / 1.000 / 0.995, false 0.050 / 0.048 / 0.073 · ≥ 0.80 and ≤ 0.10 · yes. At 20261102 the margin is 4 items of 400 (0.810) · yes (R-NONE-DIST reads 0.45–0.53).
- **M2b**: 48 · P-ORACLE 0.979 / 0.938 / 0.896 · 0.80 · yes · yes (record fails, 0.646–0.729).
- **M3**: 58 · P-ORACLE 1.000 · 0.80 · yes · yes (null p95 0.589–0.690).
- **M4a CARRY**: 13 words × 8 = 104 · 1.000 · ≥ 0.90 and above the null's p95 (≈ 0.65 [inferred: 0.573 + 1.645 × 0.049]) · yes, only with the ≥ 2-hypothesis clause (without it: CARRY = null = 1.000, never «above») · yes (a wrong attributor reads near the null). **EXIST** is a wiring pin.
- **M5**: 400, plus 455 / 455 / 458 valid and 60 M3 · 1.000 · 0.90 / 0.80 / 0.05 / 0 · yes · by a wrong Ear cover only. The null cannot fail it (the same types by construction), as declared.
- **M6**: pooled 56 (20261102) and 61 (20261103); NOT GRADABLE at 20261101 · P-ORACLE 1.000 · 0.70, n ≥ 30 · yes · yes (FAIL predicted at 20261103).
- **Speech**: as S1b-1R. ORDER has n 12 / 25 / 13 < 30, so it reads UNDERPOWERED at every seed by arithmetic (the need is seen on ≤ 27 of 60); this is known and declared, and not one of tests 1–6.
- **Twin M1**: 202 / 188 / 192; the smallest margin that reaches p < 0.001 is 10 / 188 = 0.053, so the 0.10 margin binds · reachable if the twin ≤ 0.88 · yes (a twin ≥ 0.89 fails it).
- **Twin M3**: pooled 117 / 115 / 113; the smallest margin is 10 / 113 = 0.088 < 0.10 · as M1. Per seed (n 58) it would have been 0.172.
- **Twin ABLE**: its forced M1 above 0.605 / 0.666 / 0.625 · — · VOID below it · a live outcome: the organs' road has never pointed on record.
- **Null**: 20 draws; M1 p95 0.605 / 0.666 / 0.625, M3 p95 0.589 / 0.690 / 0.673 · — · above the p95 · yes · yes (the draws' own max reaches 0.619 / 0.691 / 0.625 on M1).
- **Null identity**: M1 + M3 of k = 1 at 20261102 (188 + 58) · equality · equality · yes, after the re-run · yes.
- **Disturbance, replay identity, rung 3**: byte identity · identity · identity · yes · yes (any leak or unseeded draw).
- **F-M2B**: 48 · P-ORACLE-RW on the new set · 0.80 · printed · yes. **F-M6**: n ≥ 30 needs ≥ 84 items.

**The builders' contract moves in three places** (the INTERFACE is not edited here; the PREREG is law over it): (1) the M4 `why` road cites among episodes with ≥ 2 hypotheses, and each cited episode carries `hyp`, `fix` and `hyps`; (2) the M5 items are those of §3's M5 row; (3) the dax scene's `brain` learn row carries `fix` and `hyps`.

**The seat's grader draft (`tools/brain/grade_life.py`, 98655cf, landed while this walk ran) must follow §3, and differs in three places.** (a) Its M4 null draws citations from EVERY moment where the word was heard, 1-thing scenes included, and a random THING there. Under it, a brain that cites only 1-hypothesis episodes reads CARRY 1.000 against a null near 0.74 [inferred: 0.4 × 1 + 0.6 × 0.57], so it passes with no attribution skill. §3's null keeps the cited episodes and draws among their `hyps`. (b) It maps a citation to a thing by the mean `pos`; §3 uses M1's rule over `fix` / `hyps`. (c) Its sign test is two-sided; §3's is one-sided. At the marks' n both forms leave the 0.10 margin binding (two-sided: 11 / 113 = 0.097).

---
SIGNED (on the FINAL text):
- Claude (Fable 5.1, the seat) — *to sign after the co-signer's last edit*
- Opus 5.5 — 2026-09-28 20:37 +0400 (the text as of this commit)
