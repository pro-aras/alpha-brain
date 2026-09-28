# T-MEM-5 (= S1c-3) «WHERE SEPARATES» — the builder's hand-back

*edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 19:20 +0400.*
- **The law:** `PREREG-TMEM5.md` (genome-wt-brain3 ce41448, sha **30121082…**, final) with AMENDMENT 1 (95b6e48, **ab9a5fca…**), AMENDMENT 2 (3c28401, **8638072d…**) and AMENDMENT 3 (b90e180, **035d29f2…**), all final. It extends PREREG-S1C / AMENDMENT 1 / PREREG-S1C2, and PREREG-TMEM1 + CONCLUSION-MEMORY for the READER. Every sha was checked before each gate.
- **The code:** branch `scene-tmem5`, built from scene-tmem1 2609670:
  - efed314: the build;
  - f2f2892: AMENDMENT 2;
  - 7069da0: a serialisation fix and the gain-collapse diagnosis;
  - 9e23231: AMENDMENT 3;
  - 1541261: the stop's records.
  
  Each gate ran from a PINNED copy (`/data/dev/brain-runs/scene/code-<sha>`).
- **The run root:** `/data/dev/brain-runs/scene-tmem5/`. The last gate is in `gate/`; the earlier ones are in `gate-archive/`.
- **No unit ran.** Tonight's finding is THE FIRST GATE's stop at step 2 under AMENDMENT 3.

## 0 · The finding (AMENDMENT 3 §3: «if the new toy fails at every grid value, STOP and hand back — that is the finding»)
**Neither gain rule passes a toy that has what the life has** (two learnable rooms sharing words, a noise room, 1–3 things per scene with ONE named): the all-words gain separates B but drags a learnable room under 0.8 at every seed; the said-only gain keeps the learnable rooms but never separates B.

| the gain's step | the noise room B | the learnable rooms | the toy |
|---|---|---|---|
| **every word** (PREREG-TMEM5 §1) | separates: g_B's last-10 mean 0.020 / 0.037 / 0.045 | **dragged down**: g_A1 / g_A2 last-10 means 0.60 / 0.98, 0.94 / 0.68, 0.83 / 0.78 — one learnable room under 0.8 at every seed (minima 0.47, 0.44, 0.69) | MISS at every seed (both g_A ≥ 0.8 fails) |
| **the SAID words only** (AMENDMENT 3 §2) | **never falls**: g_B's last-10 mean 1.00–1.28 at every lr_g | drift UP with lr_g (each room's last-10 mean): 1.21–1.30 (0.001), 1.39–1.55 (0.002), 1.82–2.11 (0.005), 2.32–2.67 (0.01) | MISS at every lr_g, every seed |

(The all-words row is at lr_g 0.005, from the diagnosis on the same toy. The said-only row spans the whole grid; its per-seed rows are in the gate output, `tools/scene/diag/tmem5_first_gate_amend3_stop.out`.)

- **Why the all-words gain drags a learnable room down** (`tools/scene/diag/tmem5_gain_collapse.out`, on the life, at the f2f2892 re-gate):
  - The noisy-OR reads every unsaid word as FALSE of every thing in view. But the parent names ONE thing of 1–3, so the map rightly predicts words for the unnamed things, and their silence reads as «features mislead here».
  - Summed over R1's scenes by block 60: the said words push +187, the unsaid pull **−368**, and g_R1 falls 0.988 → 0.096.
  - By the chain rule the low gain slows R1's own map, so the fall feeds itself.
- **Why the said-only gain cannot see the noise room** (`tools/scene/diag/tmem5_said_only_toy.out`, on the rebuilt toy; its control reproduces the gate's toy record at every block):
  - B's said-word term per scene is −0.21 with ONE thing (a random word misfits, as it should), but **+0.17 with two things and +0.27 with three**. The responsibilities choose, among the things in view, the one the map finds most compatible with the random word, so a selected match reads as fit.
  - B's total is +55. The learnable rooms read +0.36 to +0.54 per scene at every H.
  - With no negative evidence, nothing bounds any gain from above: Fable's AMENDMENT 3 edit, observed.
- **The rebuilt toy is the instrument AMENDMENT 3 asked for.** It catches both failure modes: the all-words rule's collapse of a learnable room, which the one-learnable-room toy could not show, and the said-only rule's blindness.
- **Both point to AMENDMENT 3 §1's learner finding:** the learner's likelihood of the parent is mis-specified. A noisy-OR over things treats silence as evidence; its posterior responsibilities, once the silence is dropped, treat selection as evidence. The principled fix is a mixture likelihood over the named thing, which is a later slice's one difference.

## 1 · THE FIRST GATE, three times

### Gate 1 (efed314, lr_g 0.001, the one-learnable-room toy): STOP at step 2
- **Step 1: EQUAL.** The context learner FROZEN reproduces S1c's PROGRESS and RANDOM records at 20261301, every field but the five masked by name. The pools, the test set and the fence are all the same.
- **Step 2 (the toy) missed:**
  - g_B after its 500 B-scenes read 0.312 / 0.320 / 0.236 against ≤ 0.1, falling almost linearly at about 0.07 per 50 B-scenes;
  - g_A's minimum was 0.898 / 0.907 / 0.896;
  - A's forced naming was 0.77–0.94;
  - without biases, g_B ended at 0.39 / 0.39 / 0.35.
- **The diagnosis** (`tools/scene/diag/tmem5_toy_lr_grid.out`, whose 0.001 row reproduces the gate) ran the same toy at 0.001–0.01.
  - Read on the bar's own statistic (g_B's last-10 mean ≤ 0.1 × g_A), 0.005 passed at all 3 seeds.
  - Read on g_A's minimum, no value passed.
- AMENDMENT 2 ruled on this.

### Gate 2 (f2f2892, lr_g 0.005, the all-words gain): all five steps PASSED; the unit was HELD
- Step 2: g_B's last-10 mean .027 / .072 / .041 against .084 / .090 / .086; g_A's last-10 mean .84–.90.
- Step 3: FD errors ≤ 6e-12, and the planted doubled factor was caught.
- Step 5: every pin passed.
- **A fault of mine:** a numpy.bool in step 3's record stopped `first_gate.json` from being written after PROCEED was printed. The log is kept (`tools/scene/diag/tmem5_regate_f2f2892_lrg0005.log`). It is fixed test-first at 7069da0.
- **Step 4 (RANDOM-CTX, 60 blocks) is why the unit was held:**
  - N separated: g_N 0.84 → **0.000** by block 59, on 210 N-scenes. N's fraction over 21–60 read 0.125, against 0.253 for the context-blind learner on the same picks.
  - **But g_R1 fell at every R1 visit** while R1 was still learning: 0.988 → 0.784 → 0.434 → 0.303 → 0.190 → **0.096** by block 60. g_R2 was 0.82 and g_R3 1.11.
  - By R50's rule (a smoke that shows the graded run's outcome) I HELD the unit. The decomposition above named the cause, and AMENDMENT 3 ruled on it.

### Gate 3 (9e23231, the said-only gain, the rebuilt toy): STOP at step 2
- **Step 1: EQUAL** again.
- **Step 2:** the whole grid {0.001, 0.002, 0.005, 0.01} × 3 seeds MISSES, as in §0. The smallest passing lr_g is None, so the gate stops by AMENDMENT 3 §3's own clause.
- **Beside it:**
  - the toy's naming falls as lr_g rises: shape 0.62–0.72 at 0.001, 0.45–0.50 at 0.01;
  - the gain-only toy at 0.005 ends g_B 1.01–1.10.

## 2 · What is built, ready for the next rule (tested; the suites below)
- **`brain/scene/context.py` (LEARNER side, inside the truth fence).**
  - The context learner: logit = g_r · (v · z) + b + c_{r,w}, with g_r ≥ 0.
  - The chain rule's g_r is applied ONCE, to ΔV.
  - The gain's step is over the said words (AMENDMENT 3), a one-line switch for any next rule.
  - `said_loss` is the pin's target.
  - The stored act sits beside every stored row.
  - FROZEN, it is S1c's A-RW bit for bit.
- **`brain/scene/run_tmem5.py`:**
  - the 14 arms, including NULL-CTX + REPLAY (AMENDMENT 1 §3);
  - the per-block context derangement;
  - replay under each scene's own act;
  - the ORACLE's clone check covering g and c;
  - A read at ḡ_R;
  - A-READ+WHERE keyed by (word, room), with the STRONG rule per room;
  - the MEMORY grader (the null VOIDs iff it meets the fraction clause at ≥ 2 seeds; the context-blind fraction and the null's four gains printed; g_N read three ways, relative to ḡ_R, with its slope and the REALISED N-budget; the drift named);
  - the CURIOSITY grader (each barred arm with its own null; «0.80 × O» a reading);
  - the two toys, the grid, the chain-rule pin with two planted offenders, THE FIRST GATE's five steps, the price and the report.
- **`tools/scene/run_tmem5.sh`:** the unit (14 arms × 3 seeds, 120 band lives), never launched.

## 3 · Declared in code (beyond the 13 rulings of AMENDMENT 1 §4)
- **The toys:**
  - TOY_SIGNAL 3.0; a thing = the three values' prototype directions (norm 3.0 in 144 dims) + unit noise ‖ [y/16, x/16];
  - S1's 1 / 2 / 3-thing mix;
  - the parent names one thing with a template T1–T4; B follows N's rule;
  - the rebuilt toy: A1 = circle, square, triangle; A2 = cross, ring, star; the colour and size words shared; 50 blocks per room in a seeded order.
- **The chain-rule pin:**
  - the error is normalised by max(1, |step|), at a tolerance of 1e-6;
  - it is taken on a one-thing scene of heard words from visit 1,000 on, in R2 and N, at the learner's own g and at g = 0.5.
- **The clone check** (`same_state5`) includes the learner's current act.
- **The ε-flag pins** cover every PROGRESS- and NULL-picked arm.
- **Step 4's STOP** reads each learnable room's MINIMUM over blocks 1–60.
- **Refutation (a)** reads g_N at block 200 against 0.3 · ḡ_R, with ḡ_R the bar's own reading.
- **The cause of a «slow» reading:**
  - «budget» if the realised N-budget is under the toy's fastest first passage;
  - «rate» if it is at or over the slowest;
  - «undecided» otherwise.

## 4 · Suites, prices, and where each diagnosis's control now looks
- **The diagnoses' `.out` files are the record.** Each ran from a pin, against the gate record of its own gate. Two of those records have since been moved into `gate-archive/`, so a RERUN must point its control at the archived path:
  - `tmem5_toy_lr_grid.py` ran on code-efed314 against what is now `gate-archive/gate-stop-lrg0001/step2/toy.json`;
  - `tmem5_gain_collapse.py` ran on code-f2f2892 against what is now `gate-archive/gate-f2f2892-lrg0005-allwords/step4/RANDOM-CTX-60.json`;
  - `tmem5_said_only_toy.py` ran on code-9e23231 against the current `gate/step2/toy.json`.
- **The suites on the final code commit** (1541261 = 9e23231's code + the stop's records): venv `Ran 695 tests in 304.710s` / `OK (skipped=3)`; scene `Ran 293 tests in 91.408s` / `OK` (logs `/data/dev/brain-runs/scene-tmem5/suites/*-1541261.log`).
- **Every gate's step 1** (the frozen identity) read EQUAL.
- **The red checks:**
  - on 2609670 (the build): FAILED (errors = 3) — context.py and run_tmem5.py do not exist there;
  - on d452470 (AMENDMENT 2): 10 of 26 fail;
  - on 7069da0 (AMENDMENT 3): 12 of 34 fail.
- **Cost:**
  - each gate ran in under a minute (the toys 0.4–1.1 CPU-s per life);
  - the diagnoses took seconds;
  - the unit's price was never run; the estimate is ≈ 9–10 CPU-min (159 lives).

## 5 · What the next slice needs (the seat's and Fable's call)
- **The instrument is ready.** The rebuilt toy separates the two failure modes, and the gate's step 4 prints every room's g under RANDOM-CTX.
- **A next gain rule, or the mixture likelihood,** drops into `context.py`'s one line (or its likelihood) and meets the same toy and the same gate.
- **The toy's pass rule** is a separation that must hold for BOTH learnable rooms and against the noise room, at N's budget.
