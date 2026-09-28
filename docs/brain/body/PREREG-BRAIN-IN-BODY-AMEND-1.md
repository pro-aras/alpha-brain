# PREREG BRAIN-IN-BODY — AMENDMENT 1: light work beside a life, the fix for test 6, and three reading rules met on the way

*Drafted by Claude (Fable 5.1, the seat), 2026-09-28 21:46 +0400, for the co-signature of Opus 5.5. It changes no bar of the signed text (12bdea6, sha256 e39b512e…). Law once both names stand on the FINAL text.*

**What was known when this was written** (so the reader can judge what is a prediction and what is hindsight):
- Rung 1 passed (the seat's run: 2,209 / 2,222 / 2,221 answers equal; the plant fails).
- One full-length rehearsal by the replay road was graded at 20261102, and one 300-scene seam life with its twin.
- The pre-flight life and the first lean life (20261101) ended clean under the real unit. **No lean life has been graded.**
- DIAG-M6 (f6db70c) is on record. Its readings were taken on the fresh test set.

## 1 · §6 amended — what may run beside a life
**The signed line:** «Nothing else runs beside a life except its own twin and null replays, and those only after the life has closed.»

**Added:** light work may run beside a life: reading, editing, and unit tests of at most 60 seconds on ONE core at nice 19. Never a replay, a cache draw, a suite, a gate or a second life.
- ONE core means the BLAS threads pinned too: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`, or `taskset -c <one core>`. A numpy test uses every core by default. *(co-signer: «one core» was not true of a numpy test as worded)*
- Nothing is written under a life's root, its `code/` copy included. A test's TMPDIR is on disk, never /tmp (a RAM disk, #236). *(co-signer: the life runs from `<root>/code`; that is what makes editing the worktree safe)*

**Why this is safe, from the record — and where it stops:**
- **A LEAN life's rows do not depend on the load, except their wall-clock `at` stamps.** The pre-flight life replays to itself (3,386 rows identical), and its 1,721 answers equal the replay of a separately made tape of the same world. Its only world feeds by the mind's own backlog, so a slower mind makes a longer life, not a different one. *(co-signer: every tape row carries `at`; «content» was too wide)*
- **This rests on four facts of `BRAIN-LEAN.genome` as it stands:** no `SELF` line (the backlog skip), no `THINK` line, `SENSE body` OFF, and the scene sense the only publisher (`_publish_moment` publishes the eye, ear and colour rows itself; `backlog()` only gates WHEN). If any of these lines turns on, the claim lapses and §6's signed line applies again. *(co-signer: the claim named no condition; these are the genes that could read load into a row)*
- **In the FULL organism only the BRAIN's answers are load-independent.** The maker, the reader and the game keep their own wall clocks, so a slower mind meets their rows at other places between the scene's rows. The organism's cells then differ from run to run. The brain hears the scene world alone, in the scene's own order, so its answers do not. EVOLVE cannot move the brain: its `BOUNDS` (`creature/genes.py`) name no BRAIN value. *(co-signer: EVOLVE is a wall-clock gene; this is why it cannot break the claim)*
- The life's load and its backlog are written every 10 s in `SERIES.tsv`. A disturbance is visible there.

**What it does not cover:** a price. A life's cost per canvas is read only from a life that ran alone.

## 2 · §7 F-M6, named after its diagnosis
**The cause on record (DIAG-M6):** a word met fewer than 3 times answers by an inside / outside band test, so ties are broken at random; and one meeting stores colour, size and place with the shape.

**The fix, one difference:** a word under `young` meetings points at the hypothesis NEAREST its stored meetings under the reader's own metric (the pooled covariance of the type its ear heard alone most). «None» stays the band's job. Every mature word answers as today.
- **Nearest, exactly:** the distance from each hypothesis to the word's prototype μ_w (the responsibility-weighted mean of its stored meetings; with one meeting, that meeting), under `reader["ear"]["lam"][one_alone]` at the BRAIN line's `eps`. This is what DIAG-M6 read. An exact tie goes to the item's tie generator (DIAG used a bare argmin). *(co-signer: «nearest its stored meetings» had two readings once a word has 2 meetings)*
- **It acts only on a pointing ask whose phrase is ONE young word** (M6's «dax»). Every other phrase answers by the law. *(co-signer: a mixed phrase was undefined; no test item holds one)*
- **It falls back to the law's pointing** when there is no reader yet (no calibration), when `one_alone` is None, when that type's Λ is None, or when the word has no prototype (`proto_w` 0). *(co-signer: before the first calibration `self.reader` does not exist)*
- **Where it must live, so that IDENTITY can pass:** in `RWLearner.answer_point`'s choice of `point` alone. `logp_answer`, `phrase_scores`, `best`, `scores`, the three «none» flags, `calibrate`, `calibrate_r`, `train_scene`, `believed` and `held_words` are the law's, untouched. The distances go in a new field of the answer. Reason: `calibrate` reads `logp_answer` for τ_point (the best phrase score of every training scene, the «dax» scene included). A finite young-word score there can move τ_point, and then `none_i` moves on mature items. *(co-signer: as worded the fix could be written where IDENTITY fails by construction)*

It is a BRAIN line value, `young 3 nearest`. The signed line `young 3` keeps the law. The parser refuses any other word there.

**The test set:** new test seeds 20261501 / 02 / 03, never drawn before this amendment was signed, with **84** M6 items per world seed (42 give 27–32 covered on record, under n ≥ 30).
- **Every split is drawn on the new set**, as on the fresh set. Otherwise IDENTITY has no item. *(co-signer: IDENTITY was vacuous if only M6 is drawn)*
- **The 84 keep the old sets' scenes.** Item i < 42 is today's `m6_scene(ts, i)`, byte for byte. Item i ≥ 42 follows the same rule on i − 42 (two things below 28, else three), so the mix stays 2:1. `split_size("m6")` takes the test set: 84 on the new set, 42 on the fresh and older sets. *(co-signer: raising `M6_TWO, M6_THREE` would turn items 28–41 into two-thing scenes and change every lean life's sitting)*

**The hidden cost, and the order of operations.** `young 3 nearest` changes `genome/machinery.py`; the new set changes `brain/scene/world.py` and `brain/scene/cache.py`. All three are `WORLD_CODE`, so `check_code` refuses every cache in the run root. Therefore, in this order:
1. Every life is closed first. A redraw is a cache draw (§1).
2. Every cache is redrawn in a FRESH run root. The fresh and older sets' caches must be array-identical to the scored ones (`tools/brain/diag/cache_identity.py`, its planted bit caught).
3. Rung 1's gate is run again on the fix's commit, under `young 3`. The law's answers must still equal the record.
4. Only then does the bench read the new set.
*(co-signer: the cost was not said; it decides tonight's schedule)*

**The gate, on the bench, all of it on the new set:**
| clause | bar | why |
|---|---|---|
| IDENTITY | on every ask that is not a pointing ask on one young word, the fixed brain's answer EQUALS the law's, item by item, the whole answer row but the new distance field. Read on the new, fresh and older sets (≈ 1,300 asks a set a seed) | the fix may touch young words only. This is the control: a fix that moves a mature word's answer is a different learner *(co-signer: `what`, `say` and `why` asks have no phrase; the used sets are read too, because the fixed life sits them)* |
| M6 | covered ≥ 0.70 with n ≥ 30, at 20261102 and at 20261103 | the signed bar |
| M6 against the law | the fixed brain is above the law on the same items by ≥ 0.10, exact one-sided sign test p < 0.001, pooled over the two gradable seeds | a fix that only matches the law is no fix |
| 20261101 | NOT GRADABLE, as before | the eye never saw the meeting; the fix cannot help it |

- The law's own M6 on the new set is printed beside. It is a reading with no record.
- **The power, by arithmetic** (§5): n ≈ 56 and 61 covered; pooled ≈ 117. p < 0.001 needs at least 10 discordant pairs, all for the fix. On DIAG's rates the sign test reaches p ≈ 3e-5 to 7e-9. It can fail: a fix that re-ranks ties at random is the law in distribution; plain Euclid reads a pooled gap of 0.089 on the record, and 0.552 at 20261103. *(co-signer: the gate's power was not stated)*
- If the gate passes, one lean life at 20261102 runs with `young 3 nearest` and is graded by the signed text, with PARITY read against the fixed brain's bench answers **on the sets that life sits (fresh and older)**. *(co-signer: the bench must answer those sets, not only the new one)*
- **That life's M6 is a READING, never evidence for the fix.** The fresh set is the set the fix was diagnosed on (#158), and the older set was read in the pooled prediction. The evidence is the bench gate on 2026150x, plus PARITY. *(co-signer: otherwise the verdict could cite the fix's own diagnosis set as its proof)*
- If the gate fails, the fix is not adopted. The reading is filed and test 6 stays on the failing list.

**F-M2B is not started tonight.** Its «confident» needs a threshold, and no record says where to put it. It is dated at the wrap.

## 3 · Three reading rules met on the way (each would otherwise read as a result)
They were met on the seam life and the rehearsal, before any lean life was graded. They change how a row is READ, never a bar.

1. **The twin's pairs.** The organism's own word road keeps only the LAST word of an utterance, so its cells hold no colour or size word. On a phrase with such a word the twin answers «unheard», and «unheard» is not gradable (S1b-1R's own rule).
   - A pair is read on the items gradable in BOTH.
   - With no such item the pair reads **NOT COMPARED**. Under n 30 it reads **UNDERPOWERED**. Neither is a PASS or a FAIL.
   - The signed text expected the M3 pair to be computable. It is not: every M3 phrase holds a colour word. **This is a finding about the body, and the verdict states it in its first lines.**
   - **The M1 pair shrinks to the one-word shape phrases (template T1).** Covered on the fresh set: 40 / 37 / 38 (M3: 0 of 60 at every seed). At that n, p < 0.001 needs a gap of at least 10 / n = 0.25–0.27, so the 0.10 margin never binds. The M1 pair is therefore pooled over the fresh and older sets, as M3 was: n 80 / 81 / 74, smallest passable gap 0.125–0.135. The grader's line `("M1", True, (GRADED_SET,))` changes to both sets. Population moved, bar unchanged. *(co-signer: counted from S1b-1R's keys and truth files)*
   - Every pair prints its smallest passable gap, 10 / n, beside the bar.
   - **The twin's own pointing is printed.** On the seam life 37 of the twin's 46 gradable M1 answers were the grader's uniform draws. So every paired line prints the twin's OWN-pointing share on the paired items, and ABLE prints its n. A PASS where the twin pointed on its own on under half the paired items reads «the brain points where the organs' road does not», never «the brain adds over the cells». *(co-signer: a reading rule on wording; no bar moved)*
2. **The null's identity.** The offline null was never calibrated (`run.run_null` trains and answers, with no reading point), so its «none» flags are computed without a threshold. The replayed null calibrates before its sitting.
   - Identity is read on POINTING (`point`, `best`, `scores`), item by item.
   - The whole-answer equality is printed beside, with the keys that differ.
3. **A `why` asked twice.** The sense asks `why` in every sitting under one item name. The signed text grades the FRESH sitting's. The first answer stands; it is the fresh sitting's because the WORLD line sits `fresh s1b1` in that order. The repeats are counted and printed. *(co-signer: why «first» means «fresh»)*

## 4 · Rung 3, two additions from the independent review (REVIEW-BEFORE-RUNG3.md)
- **Every rung-3 replay runs on the tape CUT at the last row the mind lived** (`state/ledger.json` `last_seq`). The full organism's other worlds publish after the scene world has ended, and the body's stop leaves its queue unconsumed. The tail's rows are counted and printed by sense.
- **EVOLVE is part of the full organism and is left on.** Its shadow mind declares the BRAIN line too, so it learns every scene a second time under `evolve/`. That costs about twice the life's processor (a prediction). It writes nothing the grader reads. The full life's `ms_per_canvas_1min` is printed beside the lean life's at the same seed. EVOLVE's own share cannot be read from the root: `SERIES.tsv` has no per-process CPU and the unit file carries no CPU figure. *(co-signer: «printed from the series» was not computable)*
- Every rung-3 replay runs from the life's pinned `<root>/code`, never the worktree (as `rung3_replays.sh` does), because the F-M6 fix lands in the worktree. *(co-signer: says why the fix cannot reach a closed life's replay)*

## 5 · The co-signer's walk
*Opus 5.5, 2026-09-28 22:02 +0400. Read-only: code, keys, truth files, DIAG's outputs, the reports. No learner was run. Scripts are in `/data/dev/brain-runs/organ/prereg-review/amend1/`: `twin_m1_gradable.py` (the twin's gradable items, from S1b-1R's keys and truth), `fm6_power.py` (F-M6's n, sign-test power, failability, the twin pair's smallest gap).*

Each line reads: n · ceiling · bar · reachable? · failable?
- **§1 light work**: — · — · the four genome facts hold today · yes · yes (any of SELF, THINK, SENSE body or a second publisher turns it off).
- **§2 IDENTITY**: ≈ 1,300 asks a set a seed, three sets · 1.000 when the fix lives in `answer_point` alone · equal · yes · yes (a fix in `logp_answer` can move τ_point and every `none_i`).
- **§2 M6 per seed**: ≈ 56 / 61 covered of 84 (P(n < 30) ≈ 1e-9) · P-ORACLE 1.000 · ≥ 0.70 · likely at 20261102 (DIAG 0.963); **at risk at 20261103**: DIAG's 22 / 29 = 0.759 has a 95 % interval 0.60–0.91, and even at a true 0.759 the read falls under 0.70 about 13 % of the time at n 61 · yes (Euclid read 0.552 there).
- **§2 M6 against the law**: pooled ≈ 117 · — · gap ≥ 0.10 and p < 0.001 (≥ 10 discordant) · yes: DIAG's rates give a gap ≈ 0.23, p 3e-5 (independent errors) to 7e-9 (nested) · yes (random tie re-ranking: b ≈ c; Euclid's pooled gap 0.089).
- **§2 20261101**: NOT GRADABLE, as signed.
- **§3 rule 1**: M1 twin-gradable 40 / 37 / 38 fresh, 80 / 81 / 74 pooled; M3 0 · — · gap ≥ 0.10, p < 0.001; smallest passable gap 0.125–0.135 pooled · reachable only if the twin is ≥ 0.13 below the brain on one-word shape phrases · yes. M3 reads NOT COMPARED by arithmetic.
- **§3 rule 2**: M1 + M3 of k = 1 · equality · equality on `point`, `best`, `scores` · yes: calibration moves none of the three (`_bands_cache` equals the fresh bands at the same state) · yes.
- **§3 rule 3**: 13 words · — · the first (fresh) answer · yes · —.
- **§4 cut tape**: `state/ledger.json` carries `last_seq` (read on brain-lean-20261101: 34,443) · computable · yes.
- **§4 EVOLVE's cost**: its share is NOT computable from the root; only the life's ms per canvas is. Worded so.

**Not in this amendment, and not to be claimed tonight:** the fix, if adopted, repairs M6 only where the eye saw the meeting (20261101 stays NOT GRADABLE). M2b still fails, and M4b is not built. So «the brain passes his six tests» stays false whatever the gate reads.

---
SIGNED (on the FINAL text):
- Claude (Fable 5.1, the seat) — *to sign after the co-signer's last edit*
- Opus 5.5 — 2026-09-28 22:02 +0400 (the text as of this commit)
