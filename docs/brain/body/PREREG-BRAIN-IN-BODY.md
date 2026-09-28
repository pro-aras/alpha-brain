# PREREG — BRAIN-IN-BODY: one brain organ, inside the creature, graded on his six tests

*Drafted by Claude (Fable 5.1, the seat), 2026-09-28 20:21 +0400, for the co-signature of Opus 5.5. Law once both names stand on the FINAL text (SOLUTIONS #244 (6): sign again after every co-signer edit).*

**His order (2026-09-28 19:56 +04, verbatim):** «The brain full build continues and should get finished today. Check all the research and documentations, and tests and experiments and find the failing parts and fix them and test the whole brain as one and then test it in a single organism body and test the full organism as one.»

**The failing parts** are listed whole in `FAILING-PARTS.md` (same folder; read-only audit, 20:13). The seams are in `INTERFACE-BRAIN-ORGAN.md`.

## 0 · In plain words
Three rungs, in his order. Each rung changes ONE thing.
1. **The brain alone.** The working parts joined into one organ. It must give the SAME answers as the scored run, item by item. This is a join check. It can find a defect; it cannot find a result.
2. **The brain in one lean body.** A `BRAIN` line in a genome. The mind feeds the brain what the eye sees and the ear hears. A parent names ONE thing in view. Then the six tests are asked through the tape. The same tape is replayed WITHOUT the brain (the twin). A shuffled-name world is the null.
3. **The full organism.** Every ALPHA4 organ on, plus the brain, under a real unit.

**Predicted before any run** (so a surprise is visible): the brain in the body answers exactly as the brain alone. So tests 1 and 3 pass, «is it here?» passes, «I don't know» on never-taught shapes FAILS at 0.65–0.73 (its cause is known), and test 6 is weak. Tests 4 and 5 are new tonight and have no record.

## 1 · The world and the lives
- The world is `brain/scene/world.py`, unchanged. World seeds 20261101 / 02 / 03. 10,000 training scenes. «dax» is met ONCE, at scene 2,700.
- The sitting asks the FRESH test set (seeds 20261401 / 02 / 03), then the older set (20261201 / 02 / 03).
- **Every mark is graded on the FRESH set alone**, as S1b-1R was. The older set gives READINGS only, with one exception: **test 6 pools its items over both sets**, because 42 items cannot reach n ≥ 30 (measured n: 27 and 29).
- Lives under the real unit, one at a time: a pre-flight (300 scenes), then one lean life per world seed, then the full organism.
- The twin and the null are REPLAYS, not lives. The world never reads the mind's answers, so a tape replayed under another genome IS the life that genome would have lived. A replay is the same mind code at machine speed.

## 2 · Rung 1 — THE BRAIN ALONE (a gate, not a mark)
`tools/brain/gate_alone.py`: the organ, fed the scored run's cached glances in order, answers the scored run's fresh questions. **Bar: every answer equal to `scene-s1b1r/<ws>/fresh/arms/A-RW-R/answers_10000.json`, all three seeds.** A difference is a join defect. It is fixed, and the gate is run again. Control: one changed training word must make the gate fail.

## 3 · Rung 2 — the marks (read from the life's own tape and journal)

**The grading functions are S1b-1R's own** (`brain/scene/marks.py`, `run.bars_r`), with its reading rules. The oracle readings beside each bar are S1b-1R's record at the same seed.

| test | the mark | the bar | the ceiling, printed beside | predicted |
|---|---|---|---|---|
| — | **PARITY**: the life's answers vs rung 1's, item by item | 100 % equal; every difference named with its cause | — | equal |
| 1 point | **M1**, on items where the gaze COVERED the target, 2–3 things | ≥ 0.90 × P-ORACLE-RW and ≥ 0.80 × P-ORACLE | gaze recall 1.000 / 0.836 / 0.721 in 1 / 2 / 3-thing scenes; M1 over ALL items is printed beside (record: 0.81) | PASS (0.985–0.990) |
| 2 refuse | **M2a** absent thing → «none» | refusal ≥ 0.80 and false refusal ≤ 0.10, the per-half rule | P-ORACLE 0.995–1.000 | PASS (0.81–0.89) |
| 2 refuse | **M2b** never-taught shape → «I don't know» | ≥ 0.80 | exact attributions reach 0.83–0.90; n = 8 per shape | **FAIL (0.65–0.73)** — the store's attributions; houses and trees |
| 3 compose | **M3** never-heard colour × shape pairs | ≥ 0.80 × P-ORACLE | P-ORACLE 1.000 | PASS (0.97–1.00) |
| 4 explain | **M4a**: «why <word>?» → ≤ 8 of its own episodes | EXIST = 1.000 (each cited moment is on its own tape and its ear rows carry the word). CARRY ≥ 0.90 pooled (the thing it says the word was about truly has that property) and above the 95th percentile of 20 shuffled-citation draws | a perfect attributor reads 1.000; words with < 8 citable episodes are listed apart | no record |
| 5 misuse | **M5**: a phrase of two words of ONE type («red blue») | refused (misuse or none) ≥ 0.90; NAMED as misuse ≥ 0.80; valid phrases (M1 + M3) called misuse ≤ 0.05; never-heard pairs of M3 called misuse = 0 | the ear's types equal the world's at every reading point on record | no record |
| 6 one meeting | **M6**: point at «dax», pooled over both sets, where the gaze covered it | ≥ 0.70 with n ≥ 30 | NOT GRADABLE at 20261101: the gaze never looked at the dax in its one scene (an organ limit, read from the training tape before any ask). Chance is printed | weak: 0.778 (n 27), 0.483 (n 29, chance 0.471) |
| speech | SPOKEN, TRUTH, TRUTH-NEED, MINIMAL, ORDER, READ-BACK, DECLINE | S1b-1R's own | TRUTH-NEED and ORDER are gaze-bound (the need is seen on 23–27 of 60); READ-BACK is a wiring pin, never evidence; DECLINE is organ-bound | as S1b-1R: TRUTH fails at seed 1, TRUTH-NEED at 2 seeds, ORDER underpowered |

**M4 and M5 bars were set at 20:25, before builder A's first measurement reached the seat.** Builder A measures their ceilings on the rung-1 learners. Because rung 1 proves those learners ARE the life's brain, that measurement is the result, one step early. It is reported as such. No bar moves after it is read.

**M4b (a readable rule that re-derives answers on unseen items) is NOT BUILT tonight.** Reason: the word map's rule is a prototype and a band; a grader that rebuilds it from the cited episodes alone is a second build. It goes on the calendar with a date at the wrap.

**THE TWIN** (the same tape, no BRAIN line; the asks answered through the organs' own memory):
- Read per mark, per seed, on the SAME items, paired.
- **Bar: the brain is above the twin on M1 and on M3 by ≥ 0.10, exact sign test on the discordant pairs, p < 0.001, at every seed.**
- If the twin matches the brain, the finding is «the brain adds nothing over the cells». That is a result, stated as plainly as a pass.
- The twin must be ABLE to answer (#228): its share of asks answered with a thing or a word is printed. A twin that answers nothing is a broken control, and the comparison reads VOID.

**THE NULL** (the parent's utterances shuffled across scenes):
- The distribution is S1b-1R's own 20 derangements per seed, for this same learner.
- **Bar: the life's M1 and M3 above the null's 95th percentile.**
- One shuffled tape (k = 1, world seed 20261102) is replayed through the mind. Its answers must equal the offline null's at k = 1, item by item. That is what lets the offline distribution stand for the body.

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
- **The whole brain «passes his six tests» only if tests 1–6 all pass at every gradable seed.** On the record as it stands tonight that will not happen: M2b is predicted to fail and M4b is not built. The verdict says so in its first line.

## 6 · Cost rule
- The pre-flight prices one canvas through the mind, lean and full, at a steady load, load recorded.
- A lean life projected over 60 min, or the full life over 3 h, is reported to him with its price before it starts. It is not shortened: a shorter life is a different brain.
- Nothing else runs beside a life except its own twin and null replays, and those only after the life has closed.

## 7 · THE FIX RUNGS (after rung 2's first life; one difference each)
A fix is tried on the bench first, then lives.
- **Every fix is graded on a test set NEVER used before** (new test seeds 20261501 / 02 / 03, generated before the fix is written). The fresh set has now been read three times; a fix chosen on it would be the exam sat by its own author (#158).
- **F-M6, the instrument and its one cause:** why seed 20261103 reads chance (which thing the one meeting was written to, against where the moon was). A diagnosis first; no fix is named before it.
- **F-M2B, the reader from the learner's CONFIDENT meetings only** (the record's first option). Gate: M2b ≥ 0.80 on the new set with M1, M2a and M3 not lower than the law's by more than 0.02.
- **The mixture likelihood** is not started tonight: no number on record supports it, and it changes the learner that passes tests 1 and 3.
- The look-again act changes the eye's road and every gaze-bound ceiling. It is not started tonight.

---
SIGNED (on the FINAL text):
- Claude (Fable 5.1, the seat) — *to sign after the co-signer's last edit*
- Opus 5.5 — *pending*
