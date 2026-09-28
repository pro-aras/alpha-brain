# FAILING PARTS — the brain's record, read whole before tonight's fixing

*edit: Claude (Opus 5.5, read-only auditor), 2026-09-28 20:13 +0400. Read-only. No file was changed except this one. No unit, run or experiment was started.*

**What was read, and at which commit:**
- genome master `1ae2d42`;
- genome-wt-brain3 `brain-design-3` `0b35155` (round 3, the memory round);
- genome-wt-scene `scene-tmem5` `1aea7c5`;
- genome-wt-scene-r `scene-tmem2` `583afb5`;
- genome-wt-b1-tape2 `f393e5a` (B1.0 / B1.1 verdicts);
- genome-wt-rprior `40d01e6`; genome-wt-rthink `d25b837`; genome-wt-b12 `b1-reader` `45c883e`;
- the T-MEM-1 hand-back from git: `scene-tmem1` `c3ce420` (it is on no checked-out worktree);
- genome-wt-organ `brain-organ`: it moved from `45362e3` to `abc00f6` while I read. Every code grep below was run at **`abc00f6`**.

**Rules of this file:**
- «Latest» means the newest graded run. For the scene learner that is **S1b-1R on the FRESH test seeds 20261401 / 02 / 03**, not S1a or S1b-1.
- Every number is quoted from the named file. **[inferred]** marks what I concluded rather than read.
- «Fix on record» means a file proposes it. «No fix on record» means I found none.

---

## Table A — the parts that go into tonight's organ

The organ is the scene-world learner: the Ear, the RWLearner word map, the READER, the store, the «none» gate and the mouth, all in `brain/scene/`. Test numbers refer to CONCLUSION.md §2: (1) point · (2) refuse · (3) compose · (4) explain · (5) reject misuse · (6) one meeting.

| part | test | latest score per seed | bar | verdict | the NAMED cause (quote) | fix on record | source |
|---|---|---|---|---|---|---|---|
| **Ear** (word types by exclusion clique cover) | supports 1, 3 | types = the world's three at every reading point, all 3 seeds; one young word «dax» | gate step 3: equal to the world's types | PASS | — | — | S1B1R-HANDBACK.md:68–70, :130 |
| **RWLearner: M1 point** (covered items, 2–3 things) | 1 | 0.985 / 0.989 / 0.990 | ≥ 0.90 × P-ORACLE-RW and ≥ 0.80 × P-ORACLE | PASS | — | — | VERDICT-S1B1R.md:36; S1B1R-HANDBACK.md:405, :421, :437 |
| — M1 over ALL items (targets the gaze missed included) | 1 | 0.816 / 0.809 / 0.809 | no bar (a reading) | reading | gaze coverage (Table E) | look again (Table B) | S1B1R-HANDBACK.md:405, :421, :437 |
| — the lr law (0.01) | 1 | lr 0.1 reads 0.891 / 0.905 / 0.919 on the same items | the law must beat lr 0.1 | STANDS | «lr 0.1 … LOCKS IN early random assignments» | — | VERDICT-S1B1.md:52; S1A-HANDBACK.md §6 item 16 |
| — the shuffled null (20 derangements) | 1, 3 | the learner clears the null's 95th percentile by 0.32–0.38 at every seed | learner > null p95 | PASS | — | — | VERDICT-S1B1R.md:29, :37–38 |
| **RWLearner: M3 compose** (never-seen colour × shape pairs) | 3 | 0.966 / 1.000 / 0.983 | ≥ 0.80 × P-ORACLE (1.000) | PASS | — | — | VERDICT-S1B1R.md:42 |
| **M2a «is it here?» → «none»** (τ_point on the MAP) | 2 | refusal 0.868 / 0.810 / 0.892; false refusal 0.079 / 0.059 / 0.052 | refusal ≥ 0.80 and false ≤ 0.10 | PASS | — | — | VERDICT-S1B1R.md:39 |
| — the store-distance «none» (R-NONE-DIST), same state | 2 | 0.525 / 0.468 / 0.450 | (a reading) | would FAIL | — | the law is τ_point, not distance | VERDICT-S1B1R.md:39 |
| **READER: M2b never-taught shape → «I don't know»** | 2 | **0.646 / 0.708 / 0.729** | ≥ 0.80 (P-ORACLE 0.979 / 0.938 / 0.896) | **FAIL ×3** | «**The limit is its own attributions**: which thing each word was about» | «a READER built from the learner's CONFIDENT meetings only, or a SLEEP re-attribution of old meetings under the current state» (but see the next row) | VERDICT-S1B1R.md:14–20, :40–41, :65 |
| — per shape | 2 | house 0.000 / 0.125 / 0.000 · tree 0.000 / 0.125 / 0.375 · arrow, wave, cup, key 0.875–1.000 | — | the two failing shapes | «It calls them a known shape» | as above | VERDICT-S1B1R.md:16, :41 |
| — the exact-attribution ceiling (P-ORACLE-RW) | 2 | 0.896 / 0.875 / 0.833 | — | the fix's ceiling | R-6: it «still sits 0.083 / 0.063 / 0.063 below P-ORACLE … T5's three-way rule does not explain» | **no fix on record** for this gap | S1B1R-HANDBACK.md:111–116 |
| — re-attribution by the READER itself (EM) | 2 | attributions got WORSE for most words (e.g. big 0.618 → 0.326 at block 100) | — | counter-evidence to the SLEEP re-attribution option | «the reader re-confirms its own mistakes … it needs new evidence, a second look or a context» | a second look or a context | VERDICT-TMEM1.md:34; TMEM1-HANDBACK (scene-tmem1 c3ce420) :27 |
| **M6 one meeting** («dax», pointing only) | 6 | **NOT GRADABLE / 0.778 (n 27) / 0.483 (n 29; chance 0.471)** | ≥ 0.70 where the meeting was seen, n ≥ 30 | **UNDERPOWERED ×2, NOT GRADABLE ×1** | seed 1: «the meeting was never seen (0 fixations on the dax at its scene)»; n < 30: «by design, not by chance»; **seed 3 at chance: no cause found** (looked in S1B1R-HANDBACK §0, §3, §6 and VERDICT-S1B1R) | no fix on record for the count; [inferred] more M6 items (Table D) | S1B1R-HANDBACK.md:413, :429, :445; S1A-HANDBACK.md:130–150, :512 |
| **Mouth: SPOKEN** | (speech) | 0.816 / 0.875 / 0.882 | ≥ 0.80 × P-ORACLE | PASS | — | — | VERDICT-S1B1R.md:44 |
| **Mouth: TRUTH** (the spoken phrase is true of the target and of nothing else seen) | 1, (speech) | **0.823** / 0.968 / 0.955 | ≥ 0.90 × P-ORACLE (0.845 / 0.900 / 0.822) | **FAIL at seed 1**, PASS ×2 | no cause named for seed 1; over things the gaze SAW it reads 0.887 [inferred: gaze-limited in part] | look again | VERDICT-S1B1R.md:45; S1B1R-HANDBACK.md:415 |
| **Mouth: TRUTH-NEED** (a second word is needed) | 3, (speech) | **0.314** / 0.561 / **0.375** | ≥ 0.90 × P-ORACLE (0.409 / 0.517 / 0.390) | **FAIL ×2** | «TRUTH-NEED is a GAZE limit. The mouth cannot know about a distractor it never looked at.» | «look again before speaking, one more fixation on the unseen part of the scene. That is S1b-2's "one act".» | VERDICT-S1B1R.md:46, :66 |
| **Mouth: MINIMAL** | (speech) | 1.000 / 0.988 / 1.000 | ≥ 0.90 × P-ORACLE | PASS | — | — | VERDICT-S1B1R.md:47 |
| **Mouth: ORDER** | (speech) | 1.000 at n 12 / 25 / 13 | ≥ 0.95 × P-ORACLE with n ≥ 30 | **UNDERPOWERED ×3** | «n ≥ 30 was above the gaze's ceiling» | «≈ 150 per seed … gives n ≥ 30 … or an n bar computed from the gaze's own coverage» | VERDICT-S1B1R.md:27, :48, :67 |
| **Mouth: READ-BACK** | (speech) | 1.000 ×3 | the wiring pin | PASS — **by construction** | «the wiring pin, 1.000 by construction» | — (Table D) | VERDICT-S1B1.md:46; VERDICT-S1B1R.md:49 |
| **Mouth: DECLINE** (purple) | 2 | 0.649 / 0.649 / 0.658 (P-ORACLE 0.676 / 0.622 / 0.632) | a reading | ORGAN-LIMITED | «the organ puts purple inside blue» | no fix on record (eye) | VERDICT-S1B1R.md:50 |
| **Mouth: young words mute** («dax» never spoken) | 6 | «dax» emitted 0 times; S1b-1's roads said it 2 / 4 / 10 times | — | works as declared | — | — | S1B1R-HANDBACK.md:48 |
| **The store** (T-MEM-1: answer names from the store, L3) | 1, 2 (keeping) | backward transfer **0.000 / 0.000** after R2 / R3 at every seed; the map alone forgets 24 / 27 / 32 % | BWT ≥ the Šidák floor | PASS | — | — | VERDICT-TMEM1.md:12–13, :39 |
| — the store's own «none» (the READER's) in the rooms world | 2 | 0.515 / 0.507 / 0.517 **before** the noise room; false refusal on M1 ≈ 0.17; after the noise room 0.168 / 0.172 / 0.158 | would-be M2a bar ≥ 0.80, ≤ 0.10 | would FAIL [inferred: not graded there] | «The noise room pollutes the memory»; shrinkage 0.757 / 0.764 / 0.770 | «the store needs WHERE» (T-MEM-5, refuted as built — Table C) | TMEM1-HANDBACK (c3ce420) :25; VERDICT-TMEM1.md:28–33, :61 |
| — the GATE (protect the strong; OWM) | keeping | GATE − random anchors 0.014 / 0.007 / 0.022 against 2 paired SE 0.017 / 0.010 / 0.017 | ≥ 2 paired SE at every seed | **FAIL** (1 of 3) | «any protection helps, and choosing the strong did not add a measurable amount» | — | VERDICT-TMEM1.md:27, :42 |
| — DRIFT (replay what drifts) | keeping | the permuted null meets DRIFT's bar at 3 / 3 | null must not meet it | **VOID** | «Forgetting is DIFFUSE, not item by item» | «the repair that works is architectural» | VERDICT-TMEM1.md:26, :41 |
| **The «none» gate** (T-MEM-2, the learner's own «nothing I see fits that») | 2 (perception metacognition) | sets aside 0.769 / 0.775 / 0.740 of claims whose referent the gaze never saw (pooled 0.761; predicted ≈ 0.8); false-unseen per claim 0.099 / 0.108 / 0.083 | no bar (a reading) | a READING | — | — | VERDICT-TMEM2.md:10–12; TMEM2-HANDBACK.md:425 |
| — what the gate DOES as built | — | it only filters the health row's calibration; it changes no answer and no learning | — | **[Certain from code]** read-only | docstring: «Read-only» | using it to gate learning or speech is NOT BUILT (Table B) | scene-r `brain/scene/run_tmem2.py`:225–255; `health.py`:71–78 |
| — the health row as a mouth gate (B1–B4) | 2 | B1 met by the CONTROL (identical numbers) · B2 CEILING-BOUND (oracle gate catches 6 of 78) · B3 ECE 0.032 / 0.041 / 0.036 PASS · B4 type-2 AUROC 0.502 / 0.430 / 0.553, pooled **0.495** | B4 ≥ 0.70 | **does not pass** | «One number per word knows the word's average, not the answer in front of it» · «The mouth's errors are the GAZE's» | «a per-ANSWER confidence: the reader's own posterior margin on this thing, or the recollection check's episodic vote (Fable's T-MEM-4)» | VERDICT-TMEM2.md:14–20, :25–28, :47 |
| **The learner's likelihood** (noisy-OR over things) | all | T-MEM-5 gate stop: all-words gain drags a normal room down (one learnable room's last-10 mean under 0.8 at every seed: 0.60 / 0.68 / 0.78; minima 0.472 / 0.437 / 0.686); said-only gain never separates the noise room (g_B 1.00–1.28) | the toy's pass rule | **REFUTED as a model of the parent** | «It assumes the parent says every word true of anything in view (a noisy-OR). The real parent picks ONE thing and names it (a mixture).» | «the MIXTURE likelihood over the named thing» — untested | VERDICT-TMEM5.md:24–28, :37–41; PREREG-R3-TONIGHT.md §S1a «The learner A-RW» (P(w | scene) = 1 − Π (1 − p_w(t))) |
| **The gaze / eye** (as it caps the above) | 1, 2, 3, 6 | see Table E | — | ORGAN LIMIT | — | look again; T8 later | Table E |

---

## Table B — NOT BUILT (called for, no code found)

| missing piece | which test | who calls for it | what exists instead |
|---|---|---|---|
| **M4 explain from experience** (4a: cite its own episodes; 4b: a readable rule) in the scene world | 4 | CONCLUSION.md §2 :28, :34; VERDICT-S1B1.md:107 («Then S1b-2 proper: M4 explain, M5 misuse …») | Nothing in `brain/scene/*.py` (grep for M4 / explain: 0 hits). Letters-stage graders exist: `brain/harness/graders.py`:251 `grade_u4a`, :292 `grade_u4b`. The store keeps every meeting's raw row (store_x / store_t, TMEM1-HANDBACK §4 item 2), so episodes exist to cite [inferred]. |
| **M5 reject misuse** («a red sound») in the scene world | 5 | CONCLUSION.md §2 :28, :43 | Nothing in `brain/scene` (grep misuse: 0). Letters grader `graders.py`:345 `grade_u5`. At letters every arm failed it: U5 ≤ 0.14 (CONCLUSION-R3.md:16). |
| **Test (6)'s second half**: use the new word elsewhere the same day, and refuse it on unrelated things | 6 | CONCLUSION.md §2 :28 («uses it elsewhere the same day»), :44 («refused on 10 unrelated signs») | M6 grades POINTING only. PREREG-S1B1R.md:36 mutes production («A word of < 3 meetings is never EMITTED»). No refusal half of M6 found. |
| **Composition beyond attribute pairs** (IF … THEN, relations over named things, «one namer») | 3 | CONCLUSION.md §2 :28 («AND, IF…THEN»); CONCLUSION-R3.md §3 T2 | M3 is colour × shape conjunction only. Relations exist only as D at letters (b1-tape2 `brain/arms/library/`), with no name constant (VERDICT-B1.1.md:60; no commit found). |
| **The look-again act** (one more fixation before speaking / before «none») | 1, 3, speech | VERDICT-S1B1R.md:66; VERDICT-TMEM2.md:19, :49 | Nothing (grep look.?again: 0). |
| **The one act** («take the red ball» → it leaves → «gone») and the world head against SHUFFLED-ACTION | 4a (experience of an outcome) | PREREG-R3-TONIGHT.md:18; CONCLUSION-R3.md §3 T5 and Fable's T3 | Nothing found. |
| **Per-answer confidence** (T-MEM-4; «confidence before the check», learning scaled by surprise) | 2 (knows what it knows) | VERDICT-TMEM2.md:47; CONCLUSION.md §9 addition 2 (:176) | Only per-word health rows (health.py), which never closed. |
| **The mixture likelihood** | all | VERDICT-TMEM5.md:37–41 | Nothing (grep mixture in brain/scene: 0). `context.py` is the REFUTED gain; only `run_tmem5.py`:57 imports it. |
| **Word status UNDERSTOOD / HEARD-OF, revocable** | all six (the mark) | CONCLUSION.md §2 :32–33 | Nothing (grep understood / heard-of / revok: 0 in brain/scene). |
| **The mouth's k re-compositions, then «I cannot say it yet»** | speech | CONCLUSION.md §9 addition 1 (:175) | The read-back and decline reasons exist; a k-recompose loop not found [inferred from the reason lists in S1B1R-HANDBACK §4]. |
| **The body wiring**: a `BRAIN` clause and its parser, `genome/brain.py`, `creature/mind.py` feeding it and journalling its acts, a «scene-talk» WORLD kind, `BRAIN.genome` + its no-BRAIN twin + the null life | all (in the body) | CONCLUSION.md §3 :50; CONCLUSION-R3.md §6 :89–95; PENDING.md top block | 0 `BRAIN` in `genome/*.genome`, 0 in `genome/machinery.py` and `creature/mind.py` (master and organ). |
| **Replay identity / state hash for a life with a brain** | (identity law) | CONCLUSION.md §3 law 8 (:65); CONCLUSION-R3.md :95 | Not found for the scene learner in the body. |
| **A SLEEP rule other than «by surprise»** | keeping | VERDICT-TMEM1.md:58–60 (A/B before any new life) | **The parser accepts ONLY «replay N by surprise»**: `genome/machinery.py`:446–447 (`re.fullmatch(r"every (\d+) moments replay (\d+) by surprise", a)`). `ALPHA4.genome`:53 uses it. A uniform / protect-strong replay needs a parser change, not a knob. |
| **The creature's closed-tape SLEEP A/B and W-forgetting reading** | keeping | VERDICT-TMEM1.md:60; CONCLUSION-MEMORY.md :140; PENDING.md next 09-29 | Not run. |
| **L2 experience graph / T-MEM-3** (NEXT, DERIVED-FROM, MEMBER-OF; WHERE / WHEN indices) | 4a | CONCLUSION-MEMORY.md §2, §4 | Not built. |
| **Readers for the creature's nine write-only stores** | 4a | CONCLUSION-MEMORY.md §0, §5 | Not built. |
| **B2 «staying able to learn»** (plasticity over 200 arrivals) | 6, keeping | CONCLUSION.md §4.2 | B2-PREREG.md :5 «STATUS: DRAFT»; no verdict anywhere (searched every brain docs dir). |
| **S0b / T8** (a style-invariant eye from more fonts) | 2 at letters | CONCLUSION-R3.md §3 T8 | Not run (PENDING.md: 09-30 →). |
| **D's name constant** | 3 at letters | VERDICT-B1.1.md:60 | Not built (no commit after f393e5a on b1-tape2). |
| **The network's next readout questions** (zero recurrent matrix at birth; a batch reader at the sitting over zero-start states) | 1 (network) | VERDICT-TESTB.md:45; VERDICT-TESTB2.md:58 | Not built; out of tonight's organ. |

---

## Table C — parts that FAILED and are deliberately OUT of tonight's organ

| part | score (from the file) | named cause | fix on record? | source |
|---|---|---|---|---|
| **Growing GRU A1 and its twins, A2 gates, A3 Tsetlin, A4 transformer, A1-TEACH** (letters) | U1a 0.035–0.038, one answer to every letter, both seeds (B1.0); VOID by CONST on B1.1 | «every learned network's answer head … reads a RAW, near-saturated state» | Yes: standardise the state (offline 4 % → 79–84 %, F11 / F13). But live it failed twice: Test B (DELTA) and Test B2 (RESET), below | CONCLUSION-R2.md:26–30; VERDICT-B1.0.md:18; VERDICT-B1.1.md:20 |
| **GROWS** (A1 − A1-FIXED) and **Memory Attention** | 0 on every family, both seeds; MA 0 | twins were two chance readings | NOT GRADABLE until the readout is fixed | VERDICT-B1.0.md:44–45; CONCLUSION-R2.md:36 |
| **Test B — the DELTA readout** | 2 / 3 distinct answers; U1a 0.070 / 0.056 and 0.035 / 0.050; its one-pass ceiling 0.115 / 0.038 and 0.171 / 0.172 | «the frozen start is not the (only) mechanism» | next: zero recurrent matrix at birth; glance-only delta RAISED | VERDICT-TESTB.md:6–8, :32, :36, :45 |
| **Test B2 — RESET to a zero start** | U1a 0.073 / 0.053 and 0.038 / 0.047; ceiling 0.119 / 0.130 and 0.115 / 0.083 → CEILING-BOUND | «the one-pass ESTIMATOR itself … reads 3–5 % of T_L's own vectors: the letter is in the state, the recipe cannot read it»; LOO class mean 0.61–0.65 (a reading) | a BATCH reader at the sitting (named, not built) | VERDICT-TESTB2.md:1, :6–8, :32, :36, :58 |
| **B1.2 «THE READER» network ladder** | HELD at the smoke (R50), never run | «the refusal bands decide U1a (0.84–0.89 → 0.51–0.59)», the frozen start's offset, CONST VOIDs the ladder | fixes to the design, none run | B12-HANDBACK.md §0 items 1–3; b1-tape2 commit 617b5fe |
| **Hybrids A5, E′, F** | VOID by C0a_SAME at both seeds (B1.0); + CONST (B1.1) | «its NAME and SAME answers come from different parts» | «one namer for the whole hybrid» (named, not built) | VERDICT-B1.0.md:6, :62; CONCLUSION-R2.md:69 |
| **D, the rule library** (letters; a passenger at most) | names unseen fonts 0.857 / 0.778 and 0.853 / 0.769; relations pass on seed 2 (AFTER 11/12 … CHAIN 21/25); FAILS U2a 0 / 40, U4a 0.0, U5 0.04 / 0.14, KEEPS; TRANSFER 11/18 (seed 2); U6 2/10 (seed 1); VOID by CONST on B1.1 (0/20) | «Its program language seems to have no constant» | a name constant (named; not built) | VERDICT-B1.0.md:7–17; VERDICT-B1.1.md:9, :36–53, :60 |
| **IN-SLDA at letters** (the READER's letters form) | with bands U1a 0.486 / 0.317 and 0.580 / 0.405 FAIL; forced 0.860 / 0.867 and 0.881 / 0.846; U2a 38 / 36 refused PASS; U6 0 / 10 | «ONE band does both jobs»; S0: CEILING-BOUND at letters (AUC 0.835 / 0.859) | move refusal to scenes (done: S1b-1R's READER, Table A) | r2/EVIDENCE.md F19 (:74–86); S0-READINGS.md:24, :38–39 |
| **R-PRIOR** (a random-program childhood) | «THE FIXED PRIOR DOES NOT TRANSFER»: 6–10 bits per byte WORSE; A1 11–21 % worse | the machine prints 0x00 / 0xFF / 0x01, printable ASCII 2.7 % | STOPPED on his word 09-27 13:30; THE SCHOOL replaces it | rprior/VERDICT.md:7, :12–13, :39–40, :92 |
| **R-THINK** (a THINK step) | Q1 INCONCLUSIVE: the seeds disagree; circuits d16+ ≈ 0.5; chains L32 0.30–0.50; two runs not converged | — | no fix on record | rthink/VERDICT.md:5–26; r2/EVIDENCE.md F8 |
| **S1c — curiosity by PROGRESS** | A 0.593 / 0.498 / 0.523 against bars 0.600 / 0.560 / 0.592; SHARE_N 0.18–0.21; LEAVE_N 169–200 — every bar FAIL | «this learner FORGETS and re-learning reads as progress» | S1c-2 (below) | VERDICT-S1C.md:16–18, :37–39 |
| **S1c-2 — PROGRESS-NET and PROGRESS+REPLAY** | every bar FAILS at every seed (A 0.406–0.540) | «the noise room CONTRADICTS the other rooms inside one shared map … the learner has no WHERE» | WHERE context → T-MEM-5 (refuted as built) | VERDICT-S1C2.md:22–29, :37–42 |
| **T-MEM-5 — the WHERE gain** (`context.py`) | gate stop after three amendments; no unit | «the learner's model of the parent is wrong» | the mixture likelihood first, then re-run (untested) | VERDICT-TMEM5.md:25–28, :33 |
| **T-MEM-1 DRIFT scheduler / A-READ-EM** | DRIFT VOID; EM made attributions worse | «forgetting is diffuse»; «the reader re-confirms its own mistakes» | architectural: answer from the store, protect the strong | VERDICT-TMEM1.md:26, :34 |
| **The health-row mouth gate** (T-MEM-2) | never closed; B4 0.495 | per-word, not per-answer | per-answer confidence (not built) | VERDICT-TMEM2.md:17–20, :47 |

**Useful facts from the failed runs, for tonight:** replay cut forgetting 65–84 % (VERDICT-S1C2.md:11, :59). Surprise replay is the worst rule measured: 49–64 % forgetting (VERDICT-TMEM1.md:23).

---

## Table D — instrument and method defects still OPEN (they would make tonight's grading lie if copied unchanged)

| defect | what the ceiling or n really is | source |
|---|---|---|
| **M6's item count is below its own n bar.** 42 fixed items × gaze coverage ≈ 0.69 on 2–3-thing scenes | «≈ 23.4 + 10.1 ≈ 33 covered items expected … any seed can land under 30. Re-rolling will not fix the item count.» Measured n: 29, 32 (S1a); 29, 32 (S1b-1); 27, 29 (S1b-1R) | S1A-HANDBACK.md:512; VERDICT-S1B1R.md:43 |
| **M6 at world seed 20261101 is never gradable.** The gaze never fixates the moon in its one scene | NOT GRADABLE in S1a, S1b-1 and S1b-1R alike (the same world seed) | S1A-HANDBACK.md:130–140; S1B1R-HANDBACK.md:413 |
| **ORDER's n ≥ 30 sits above the gaze's ceiling** | the need is seen on only 23 / 27 / 24 of 60 SPEAK2 items; P-ORACLE speaks 15 / 24 / 14 multi-word phrases | S1B1R-HANDBACK.md:104–107 |
| **SPEAK2's pin cannot be built on 2-thing scenes** | 0 of 2,256 twin-free 2-thing configurations; resolved only with 3-thing items (AMENDMENT 1) | S1B1R-HANDBACK.md:96–98 |
| **A single-draw null against chance + 0.05** | ten fresh derangements read 0.380–0.620; a true null fails ≥ 1 of 3 seeds ≈ 34 % of the time. The working form is ≥ 10–20 draws and the learner above the null's 95th percentile. [inferred] One shuffled-name LIFE per seed in the body is again a single draw | VERDICT-S1B1.md:155–162; VERDICT-S1B1R.md:29 |
| **A null that collapses to a constant scores chance by arithmetic** | Test B2's shuffled twin gave «h» × 624 (seed 1) and «three» × 537 (seed 2): «no band»; «a stronger null … would hold the answer-set size fixed» | VERDICT-TESTB2.md:23, :53 |
| **M1 covered vs all** | covered 0.985–0.990; all 0.809–0.816. The bar reads covered. Which one the body's «point» mark reads must be declared | S1B1R-HANDBACK.md:405, :421, :437 |
| **M2a's oracle can sit above the false-refusal bar** | S1a's P-ORACLE false refusal 0.119 / 0.109 > 0.10 (hence the per-half reading); S1b-1R's is 0.050 / 0.048 / 0.073. Copy the per-half rule, not S1a's bar | VERDICT-S1A.md:22, :41–43; VERDICT-S1B1R.md:39 |
| **READ-BACK is 1.000 by construction** | a wiring pin, never evidence of truth; S1b-1 read 1.000 while TRUTH was 0.60–0.72 | VERDICT-S1B1.md:45–46 |
| **DECLINE is organ-bound** | purple inside the oracle's blue band 0.70 / 0.92 / 0.76 (S1b-1R) — no reader can decline reliably | S1B1R-HANDBACK.md:251, :326, :401 |
| **M2b per shape has n 8** | 48 items over 6 shapes; one item moves a shape by 0.125 [inferred from the 0.125 steps]. The oracle's own tree reads 0.875 / 0.625 / 0.500 | VERDICT-S1B1R.md:40–41 |
| **T-MEM-2's B1 is met by the control** | HEALTH-MOUTH = CONTROL = NULL on every seed, so B1 is «NOT evidence» | VERDICT-TMEM2.md:25 |
| **T-MEM-2's B2 is CEILING-BOUND** | the oracle gate catches 0.077 (6 / 78) < 0.30 | VERDICT-TMEM2.md:26 |
| **T-MEM-2's step-3 check read one seed** | seed 20261103 reads circle and square truth-free 0.850 vs truth-fed 1.000; «The next version of the step-3 check reads every seed» | VERDICT-TMEM2.md:37–42 |
| **T-MEM-1's A-READ floor is 0 when SE is 0** | at accuracy 1.000 the Šidák floor is 0 and BWT 0.000 meets it; the TIME-WINDOW positive control (BWT −1.000) shows the mark CAN fail | TMEM1-HANDBACK (c3ce420) :16; VERDICT-TMEM1.md:54 |
| **«answer from what does not forget» vs the passing «none»** [inferred] | M2a passes by τ_point on the MAP (which forgets 24–32 % in the sequential rooms world); the store's own «none» read 0.51 with ≈ 0.17 false refusal there. No file reconciles the two | VERDICT-S1B1R.md:39; TMEM1-HANDBACK (c3ce420) :25; CONCLUSION-MEMORY.md :35 |
| **A control that decides the experiment** | CONST VOIDed every letters learner (B1.1); B1.2's smoke: every network arm VOID by CONST | VERDICT-B1.1.md:6; B12-HANDBACK.md §0 item 3 |
| **COST read under crowding** | D 110 ms solo vs 389 / 498 crowded; read COST solo (R48) | VERDICT-B1.1.md:11, :53; CONCLUSION-R2.md §3 law 4 |
| **FIXED already** (listed so nobody re-fixes it): an unheard word scored 0.0 | now NOT GRADABLE, counted as n_unheard | S1A-HANDBACK.md:144–150; scene-r `brain/scene/marks.py`:23, :195–196 |
| **The READER's ε = 0.3 sits at the end of its grid** | chosen on the toy seed, «ties go to the larger ε. It chose 0.3, the grid's end»; the gate's step 0 rises 0.960 → 0.974 up to 0.3 and was never extended — a plateau or a grid too narrow, not settled | S1A-HANDBACK.md §6 item 3; S1B1R-HANDBACK.md:122 |
| **Refuted code sits in the organ tree** | `context.py` came in with the scene-tmem5 merge; only `run_tmem5.py`:57 imports it (not learners.py, not run.py) | organ abc00f6 grep |

---

## Table E — limits of the ORGANS (eye / gaze) that cap the brain

| limit | measured | source |
|---|---|---|
| **Gaze per-thing recall, 1 / 2 / 3-thing scenes — on the built S1a world** (stage −1, seed 20261100, 300 scenes, ≥ 24 px separation) | **1.000 / 0.836 / 0.721**; all things covered 1.000 / 0.672 / 0.309; merge, split and no-thing 0.000 | S1A-HANDBACK.md:156–158 |
| — the same, from the seat's earlier probe (before the world was built) | 1.000 / 0.875 / 0.767; all covered 1.00 / 0.75 / 0.38 | seat_scene_probe.out:2–4; CONCLUSION-R3.md:32 |
| Coverage of the graded M1 items | 0.84 / 0.82 / 0.85 (S1a) | VERDICT-S1A.md:29 |
| The referent never seen, in graded said words | 2,102 of 19,455 = 0.108 | TMEM2-HANDBACK.md:149 |
| SPEAK2 items where the gaze sees the need | 23 / 27 / 24 of 60 | S1B1R-HANDBACK.md:105 |
| TRUTH-NEED over seen things vs all | 0.743 / 0.927 / 0.875 vs 0.314 / 0.561 / 0.375 | S1B1R-HANDBACK.md:108 |
| Salience | «the brighter things took the fixations» — an anecdote, not measured | S1A-HANDBACK.md §5 |
| The one-meeting scene at world seed 20261101 | the moon got 0 fixations | S1A-HANDBACK.md:130–140 |
| Input separability, all 144 features (LOO nearest mean) | shape 0.797 · colour 0.933 · size 0.867; the tower's 112 alone read shape 0.903 | CONCLUSION-R3.md:32; S1A-HANDBACK.md:159 |
| **Purple inside blue** | inside P-ORACLE's blue band for 0.86 / 0.69 / 0.82 (S1b-1) and 0.70 / 0.92 / 0.76 (S1b-1R); inside red's 0.69 / 0.50 / 0.62 (S1b-1) | VERDICT-S1B1.md:25, :81; S1B1R-HANDBACK.md:251, :326, :401 |
| Never-taught shapes the ORACLE also misses | tree 0.875 / 0.625 / 0.500; diamond (apart) 0.625 / 0.500 / 0.500 | VERDICT-S1B1R.md:41; S1B1R-HANDBACK.md:411, :427, :443 |
| Letters: plants vs unseen fonts | distance AUC 0.835 / 0.859 (Fable) and 0.833 / 0.860 (the seat's exact replay); no τ refuses one and names the other | CONCLUSION-R3.md:28–31; S0-READINGS.md:24 |
| BabyAI things | gaze 0.226 against the maker world's 0.993; 21 of 22 classes below the band | CONCLUSION-R3.md:33 |

---

## The 10 fixes that would move the six tests most (ranked)

1. **Build M4 (explain: cite own episodes; state a rule) and M5 (reject misuse) for the scene world.** Tests (4) and (5) read NOTHING today; that is a different failure from a low score. Effect: no estimate on record. Cost: letters graders exist to adapt (`graders.py`:251, :292, :345), and the store holds every meeting's raw row. Risk: writing the exam and sitting it the same night (#158); each item set needs its ceiling computed first. **[Certain]** that they are missing; **[Guessing]** on cost.
2. **Build the body wiring**: the `BRAIN` clause and parser, `genome/brain.py`, the `mind.py` feed and journal, a scene-talk WORLD kind, `BRAIN.genome` + a no-BRAIN twin + the null. It moves no score by itself, but without it no test is graded «in a single organism body». Effect: no estimate on record. Cost: the largest item. Risk: replay identity (CONCLUSION.md §3 law 8); the mind falling behind its world (#236). **[Certain]** it is missing.
3. **Look again before speaking and before «none»** (one more fixation on the unseen part). On-record ceilings: TRUTH-NEED over seen things 0.743 / 0.927 / 0.875 against 0.314 / 0.561 / 0.375 over all; TRUTH seen 0.887 against 0.823 at seed 1; T-MEM-2's oracle gate catches only 6 of 78 because «the mouth's errors are the GAZE's». Cost: a new act in the gaze road. Risk: it changes the tape and every gaze-bound ceiling, so bars must be re-derived. **[Likely]**
4. **Fix the M6 instrument before trusting test (6)**: more one-meeting items, and a meeting scene the gaze actually fixates. Today it is NOT GRADABLE / UNDERPOWERED everywhere, and seed 3's 0.483 sits at chance (0.471) with no cause on record. Effect: no estimate on record; [inferred] ≥ ≈ 45 items at coverage 0.69 to expect n ≥ 30. Cost: small. Risk: the fixed mark may show test (6) truly failing. **[Likely]**
5. **M2b «I don't know» on houses and trees: a READER from the learner's CONFIDENT meetings only** (the record's first option). On-record ceiling: P-ORACLE-RW 0.896 / 0.875 / 0.833 against 0.646 / 0.708 / 0.729; R-6's further 0.06–0.08 gap to P-ORACLE is unexplained. The record's second option (SLEEP re-attribution) already has a negative reading: EM made attributions worse (T-MEM-1). Risk: the oracle itself reads tree 0.500 at seed 3. **[Likely]**
6. **Give the brain its own replay rule, uniform or protect-the-strong; never «by surprise».** On record (T-MEM-1, sequential rooms): surprise 49–64 % forgetting, none 24–32 %, uniform 1–4 %, protect-strong ≤ 0.4 %. Cost: the SLEEP parser only accepts «by surprise» (`machinery.py`:446–447), so a parser change or a BRAIN-own replay line is needed. Risk: in a random (not sequential) world forgetting was ≈ 0 (schedule (b)), so the gain in tonight's world may be small [inferred]. **[Certain]** on the numbers; **[Likely]** on the transfer to the body.
7. **Replace the noisy-OR with the mixture likelihood over the named thing.** Effect: untested, no number on record. [inferred] It may help the store's attributions (Table A's M2b cause); no file states that link — S1b-1R names «attributions», T-MEM-5 names «noisy-OR», separately. Cost: one learner change, with T-MEM-5's two-room toy as its first gate. Risk: it touches the learner that passes M1 and M3, so re-gate both. **[Guessing]**
8. **Run nulls and twins as distributions in the body**: ≥ 10–20 shuffled-name draws per seed, the learner above the null's 95th percentile, and the answer-set size held fixed. On record: a single draw fails a true null about a third of the time (≈ 0.34). Cost: K null lives or K offline replays per seed [inferred]. Risk: cost if the nulls run as lives. **[Certain]** on the defect.
9. **Add a per-ANSWER confidence** (the READER's posterior margin on this thing, or the episodic vote — T-MEM-4), and use it for the word's UNDERSTOOD / HEARD-OF status and its revocation. On record: per-word confidence is calibrated (ECE 0.03–0.04) but blind per answer (AUROC 0.495). Effect: no estimate on record. Risk: a band calibrated on one population refuses another (F18). **[Likely]**
10. **Size the speech items to the gaze**: ≈ 150 SPEAK2 items per seed (the record's estimate for n ≥ 30 at ≈ 40 % visibility), and declare M1 covered-vs-all, M2a per-half and READ-BACK as a pin, not evidence. Effect: turns ORDER from UNDERPOWERED into gradable; no score estimate. Cost: small. Risk: low. **[Certain]** on the defect.

---

## Contradictions between documents

1. **Gaze recall.** CONCLUSION-R3.md:32 (11:38–11:42) and remember.md (19:53) give 1.000 / 0.875 / 0.767 (seat_scene_probe.out). S1A-HANDBACK.md:156–158 (stage −1 on the BUILT world, later that day) gives 1.000 / 0.836 / 0.721. The later figure is on the world actually graded. remember.md plans to use the earlier one as tonight's ceiling.
2. **M6.** remember.md says «M6 one-meeting 0.72–0.81 where the eye saw it». Those are S1a / S1b-1 on the OLD test seeds. The latest (S1b-1R, fresh seeds) reads 0.778 (n 27) and **0.483 (n 29, chance 0.471)**, both UNDERPOWERED.
3. **The «none» gate.** remember.md lists T-MEM-2's «none» gate as a part to merge. The code says it is read-only: it filters the health row and changes no answer or learning (`run_tmem2.py`:225–255).
4. **The reader at letters.** CONCLUSION-R2.md:16, :41 say 76–80 % on unseen fonts (an offline probe with a TEACH-chosen shrinkage). EVIDENCE F19 says 85–88 % (the graded FORCED reader on B1.1). These are different instruments, not a conflict of fact.
5. **T-MEM-5 minima.** Commit 1541261's message says «minima 0.44–0.47». VERDICT-TMEM5.md:24 was corrected at 19:22 to 0.472 / 0.437 / 0.686; the hand-back agrees. The correction is later.
6. **S1b-1 Finding B.** VERDICT-S1B1.md:67 says «14 … with ONE hypothesis»; its own ADDENDUM (:134–140) corrects this to 4, with 11 of 20 being «dax».
7. **Test (6) vs the maturity rule** [inferred tension]. CONCLUSION.md §2 :28 wants the new word «used elsewhere the same day»; PREREG-S1B1R.md:36 forbids speaking a word of < 3 meetings. M6 grades pointing only.
8. **«Answer from what does not forget»** (CONCLUSION-MEMORY.md :35) vs the passing M2a law, which answers «none» from the map that forgets [inferred tension; no file reconciles them].
9. **remember.md** says scene-tmem5 contains T-MEM-1. Its code does (2609670); its hand-back docs do not (c3ce420 is only on scene-tmem1).

---

## Files actually read

- /data/shariah-shadow/live/docs/PENDING.md (lines 1–150)
- /home/ahmad/.remember/remember.md
- /data/dev/genome-wt-brain3/docs/brain/CONCLUSION.md (and diffs against genome master and genome-wt-scene)
- /data/dev/genome/docs/brain/BRAIN-DESIGN.md (lines 1–40)
- /data/dev/genome/docs/brain/B2-PREREG.md (lines 1–12, grep)
- /data/dev/genome/docs/brain/r2/CONCLUSION-R2.md
- /data/dev/genome/docs/brain/r2/EVIDENCE.md (the F-list and F19)
- /data/dev/genome-wt-brain3/docs/brain/r3/CONCLUSION-R3.md
- /data/dev/genome-wt-brain3/docs/brain/r3/VERDICT-S1A.md
- /data/dev/genome-wt-brain3/docs/brain/r3/VERDICT-S1B1.md
- /data/dev/genome-wt-brain3/docs/brain/r3/VERDICT-S1B1R.md
- /data/dev/genome-wt-brain3/docs/brain/r3/VERDICT-S1C.md
- /data/dev/genome-wt-brain3/docs/brain/r3/VERDICT-S1C2.md
- /data/dev/genome-wt-brain3/docs/brain/r3/VERDICT-TESTB.md
- /data/dev/genome-wt-brain3/docs/brain/r3/VERDICT-TESTB2.md
- /data/dev/genome-wt-brain3/docs/brain/r3/S0-READINGS.md
- /data/dev/genome-wt-brain3/docs/brain/r3/PREREG-R3-TONIGHT.md (lines 1–80)
- /data/dev/genome-wt-brain3/docs/brain/r3/seat_scene_probe.out (grep)
- /data/dev/genome-wt-brain3/docs/brain/r3/PREREG-S1B1.md, PREREG-S1B1R.md, PREREG-S1B1R-AMEND-1.md, PREREG-S0-S1A.md (grep only)
- /data/dev/genome-wt-brain3/docs/brain/memory/CONCLUSION-MEMORY.md
- /data/dev/genome-wt-brain3/docs/brain/memory/VERDICT-TMEM1.md
- /data/dev/genome-wt-brain3/docs/brain/memory/VERDICT-TMEM2.md
- /data/dev/genome-wt-brain3/docs/brain/memory/VERDICT-TMEM5.md
- /data/dev/genome-wt-brain3/docs/brain/memory/PREREG-TMEM2-AMEND-1.md, PREREG-TMEM5*.md (grep only)
- /data/dev/genome-wt-scene-r/docs/brain/r3/S1B1R-HANDBACK.md
- /data/dev/genome-wt-scene-r/docs/brain/memory/TMEM2-HANDBACK.md (§11 and greps)
- /data/dev/genome-wt-scene/docs/brain/r3/S1A-HANDBACK.md (§4–§6, §13.5–§13.6)
- /data/dev/genome-wt-scene/docs/brain/r3/S1B1-HANDBACK.md (§5–§6)
- /data/dev/genome-wt-scene/docs/brain/r3/S1C-HANDBACK.md (§0–§1, §4)
- /data/dev/genome-wt-scene/docs/brain/r3/S1C2-HANDBACK.md (§0–§1, §4–§6)
- /data/dev/genome-wt-scene/docs/brain/memory/TMEM5-HANDBACK.md
- git `scene-tmem1` c3ce420: docs/brain/memory/TMEM1-HANDBACK.md
- /data/dev/genome-wt-b1-tape2/docs/brain/b1/results-b1.0/VERDICT-B1.0.md
- /data/dev/genome-wt-b1-tape2/docs/brain/b1/results-b1.1/VERDICT-B1.1.md
- /data/dev/genome-wt-rprior/docs/brain/rprior/VERDICT.md
- /data/dev/genome-wt-rthink/docs/brain/rthink/VERDICT.md (lines 1–63, 450–520)
- /data/dev/genome-wt-b12/docs/brain/b1/B12-HANDBACK.md
- code: /data/dev/genome/genome/machinery.py (grep, :446–447); /data/dev/genome/genome/ALPHA4.genome (:53); /data/dev/genome-wt-scene-r/brain/scene/health.py (:71–101); /data/dev/genome-wt-scene-r/brain/scene/run_tmem2.py (:222–262); /data/dev/genome-wt-scene-r/brain/scene/marks.py (grep); /data/dev/genome-wt-organ/brain/scene/*.py (greps; memory.py def list); /data/dev/genome-wt-organ/brain/harness/graders.py (grep); /data/dev/genome-wt-b1-tape2/brain/arms/library/*.py (grep)

**Not read in full** (say so, not implied): B1-PREREG.md, RPRIOR-PREREG.md, the rthink HANDBACK-B.md, A1-TEACH-HANDBACK.md, the per-seed `results/*/VERDICT.md` files, the RESEARCH-* and DEBATE-* files, the PREREG-TMEM* texts beyond greps.
