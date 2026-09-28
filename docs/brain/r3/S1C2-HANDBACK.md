# S1c-2 «netted progress and rehearsal» — the builder's hand-back

*edit: Claude (Opus 5.5, S1c-2 builder), 2026-09-28 16:36 +0400.*
- **The law:** `PREREG-S1C2.md` (genome-wt-brain3 141a8cd, sha **5e4585c1…**, final), checked beside PREREG-S1C a552515a… and AMENDMENT 1 92188d04… before the gate and inside every run.
- **The code:** branch `scene-s1c2` from scene-s1c 2679fb3; the unit ran from the pin of **e3cc2ed**. Run root `/data/dev/brain-runs/scene-s1c2/`.
- **The pools:** S1c's caches, accepted by `cache.check_code` and the room code's sha. rooms.py and the drawing code are unchanged, so nothing was redrawn.

## 0 · The verdict: both barred arms FAIL at every seed; the identity control holds 75 of 75
Printed by the report (`/data/dev/brain-runs/scene-s1c2/report.txt`, copied whole as `docs/brain/r3/S1C2-REPORT.txt`):
```
THE IDENTITY CONTROL (S1c's five arms and its 20 band lives re-run at every seed against S1c's records; every field but ['cpu_s', 'wall_s', 'code', 'prereg', 'world']): 75 of 75 EQUAL
PROGRESS-NET on the bare learner (O = ORACLE, RANDOM = RANDOM with its 20-life band, NULL = NULL-NET): VERDICT FAIL
   20261301: A 0.406 vs 0.80 × O 0.600 FAIL · A above the band [0.533, 0.629] (n 20; O 0.750) FAIL · SHARE_N 0.362 vs 0.076 FAIL · LEAVE_N 193 vs 50 FAIL · the positive control +0.220 PASS · NULL meets X's bars: False
   20261302: A 0.415 vs 0.80 × O 0.560 FAIL · A above the band [0.529, 0.598] (n 20; O 0.700) FAIL · SHARE_N 0.276 vs 0.055 FAIL · LEAVE_N 148 vs 50 FAIL · the positive control +0.155 PASS · NULL meets X's bars: True
   20261303: A 0.453 vs 0.80 × O 0.592 FAIL · A above the band [0.522, 0.598] (n 20; O 0.740) FAIL · SHARE_N 0.199 vs 0.060 FAIL · LEAVE_N 169 vs 50 FAIL · the positive control +0.180 PASS · NULL meets X's bars: False
PROGRESS+REPLAY on the replay learner (O = ORACLE+REPLAY, RANDOM = RANDOM+REPLAY with its 20-life band, NULL = NULL+REPLAY): VERDICT FAIL
   20261301: A 0.540 vs 0.80 × O 0.578 FAIL · A above the band [0.594, 0.666] (n 20; O 0.723) FAIL · SHARE_N 0.337 vs 0.050 FAIL · LEAVE_N 193 vs 50 FAIL · the positive control +0.123 PASS · NULL meets X's bars: False
   20261302: A 0.525 vs 0.80 × O 0.540 FAIL · A above the band [0.567, 0.608] (n 20; O 0.675) FAIL · SHARE_N 0.291 vs 0.050 FAIL · LEAVE_N 195 vs 50 FAIL · the positive control +0.083 PASS · NULL meets X's bars: False
   20261303: A 0.506 vs 0.80 × O 0.559 FAIL · A above the band [0.585, 0.614] (n 20; O 0.699) FAIL · SHARE_N 0.342 vs 0.050 FAIL · LEAVE_N 200 vs 50 FAIL · the positive control +0.113 PASS · NULL meets X's bars: False
```
- **Both worlds were gradable:** the positive control passes at every seed on both learners, and neither null meets its arm's bars at ≥ 2 seeds (NULL-NET at 1).
- **No bar was CEILING-BOUND:** the same-learner ORACLE clears its band's 97.5 % edge at every seed.
- **The refutations (§6; one «holds» only where it holds at all 3 seeds, declared as in S1c):**
  - **(a) holds at all three seeds** — SHARE_N(NET) 0.362 / 0.276 / 0.199 inside or above RANDOM's band: *netting the time away does not remove the pull of noise.*
  - (b) does not hold: NET's SHARE_N misses its own bar, so the starvation clause is not reached.
  - (c) does not hold: rehearsal DID reduce the forgetting (§1).
  - (d) does not hold: A(PROGRESS+REPLAY) is BELOW RANDOM+REPLAY's band, not inside it.
  - (e) does not hold: ERROR+REPLAY stays trapped.

## 1 · What the numbers say (readings; [the numbers Certain as printed, each mechanism tagged])
- **Rehearsal reduces forgetting, as predicted [Certain as printed].** The ruled forgetting reading is the FULL-STEP table's 12 off-diagonal entries, PRE_(b+1) − PRE_b. It reads **0.065 / 0.026 / 0.046** under PROGRESS+REPLAY against PROGRESS-S1C's **0.206 / 0.165 / 0.160**. The BLOCK table's (the interference before the repair) reads 0.191 / 0.144 / 0.140 against 0.206 / 0.165 / 0.160.
- **But rehearsal repairs the learnable rooms and not the noise, so N reads as MORE progressing [Likely — paired evidence].** RANDOM and RANDOM+REPLAY make the SAME picks (the shared band streams), which isolates the replay's effect on the drops:
  - the learnable rooms' own mean drops shrink 40–65 % (R1 0.81 → 0.32, R2 0.92 → 0.49, R3 0.63 → 0.36 at seed 20261301);
  - N's barely moves (0.29 → 0.27 / 0.36 → 0.31 / 0.54 → 0.44);
  - N's drop as a fraction of the learnable rooms' therefore RISES: 0.38 → 0.71, 0.41 → 0.70, 0.70 → 1.22;
  - the replay's own change per room, POST_b − PRE_(b+1), is ≈ 0 for N (+0.001 / +0.027 / −0.024) against R1's +0.12 / +0.28 / +0.29.
  
  PROGRESS+REPLAY accordingly spends MORE of its life in N than bare PROGRESS (0.34 / 0.29 / 0.34 against 0.18 / 0.21 / 0.20) and never leaves it (LEAVE_N 193–200). The mechanism's own prediction — «N's re-learning drop shrinks toward 0 and its fraction falls» — reads the other way at every seed.
- **ERROR+REPLAY stays trapped** [Certain]: SHARE_N 0.852 / 0.857 / 0.852, above RANDOM+REPLAY's band at every seed. The 1990 rule's trap is error-seeking, not forgetting, so (e) does not fire.
- **The replay's own gain:** A(RANDOM+REPLAY) 0.600 / 0.592 / 0.585 is inside the bare RANDOM band at every seed (its upper part). Rehearsal alone does not lift random choice out of its band.
- **NET's starvation mode fires** [Certain]: on average 3.15 / 3.03 / 3.06 of the 4 rooms read a negative net at a boundary. Each room's longest negative run is 44–124 blocks, and A(NET) sits below RANDOM's band. The blind NULL-NET learned MORE than NET at two seeds (A 0.638 / 0.681 against 0.406 / 0.415) and met NET's bars at seed 20261302: the net estimate misdirects more than it informs here.
- **PROGRESS-UCB (a reading):** A 0.521 / 0.519 / 0.498, SHARE_N 0.245 / 0.230 / 0.276, LEAVE_N 193 / 188 / 195. The bonus is 0.65–0.69 of the score at the pick, so UCB behaves ≈ RANDOM.
- **PROGRESS+REPLAY-V (a reading):** A 0.530 / 0.520 / 0.456 and SHARE_N 0.367 / 0.311 / 0.393; its buffer's N-share is 0.262 / 0.274 / 0.308 against the room grain's ≈ 0.25.
- **The same-learner ORACLE+REPLAY:** A 0.723 / 0.675 / 0.699 (the bare ORACLE: 0.750 / 0.700 / 0.740). SHARE_N 0.000 and LEAVE_N 4 at every seed: it never returns to N after the round-robin.

## 2 · THE FIRST GATE as printed (seed 20261301; whole in `/data/dev/brain-runs/scene-s1c2/gate/first_gate.out`, copied as `docs/brain/r3/S1C2-FIRST-GATE.out`; the 20-block smoke of all 14 arms read whole there)
```
1. identity — S1c's five arms re-run on this tree against S1c's records: PROGRESS EQUAL · RANDOM EQUAL · ERROR EQUAL · ORACLE EQUAL · NULL EQUAL · the caches: S1c's pools, accepted by cache.check_code and the room code's sha (8160 canvases) [the five masked fields printed side by side per arm]
2. the bracket is the room's — PROGRESS+REPLAY at R = 0 vs PROGRESS: EQUAL · at R = 10, a clone of the pre-block learner trained on the block alone reproduces POST_b and the drop at every one of 200 blocks: misses none · the planted replay BEFORE POST caught at blocks [1 … 20] · the replay's own change (mean per room): R1 +0.1187 R2 +0.0457 R3 +0.0826 N +0.0012 → PASS
3. NET is what it says — at every boundary of a 200-block PROGRESS-NET life, for every visited room (179 consecutive visits in the life), to 1e-09: misses 0 → PASS
4. the null is a null — π = {'R1': 'R3', 'R2': 'N', 'R3': 'R2', 'N': 'R1'} (a derangement; the planted identity and a planted fixed point caught; the three nulls carry it) · NULL-NET ≡ PROGRESS-NET and NULL+REPLAY ≡ PROGRESS+REPLAY under the identity credit over 200 blocks · no credit lands home · the ε flags agree in every ε arm's smoke (a planted flip caught) → PASS
5. the replay learner offers a choice — A(ORACLE+REPLAY) 0.723 − A(RANDOM+REPLAY) 0.600 = +0.123 ≥ 0.05 → PASS (the clone equalled the learner after every policy block, before its replay)
6. UCB's pin — n_k ≥ 1 after the round-robin, t ≥ 1 at every policy pick, c > 0 from block 5 → PASS
7. the 20-block smoke of every arm, each record whole
THE FIRST GATE: PROCEED
```

## 3 · Prices and the unit
- **The price, solo, printed before the launch** (`logs/price-e3cc2ed.out`): 42 lives 4.1 CPU-min + 120 band lives 3.7 = **7.9 CPU-min**; the pools are S1c's. The PREREG expected ≈ 11 CPU-min for the lives.
- **The unit `scene-s1c2`:**
  - ran 16:26:46–16:28:21 +0400 (Restart=no, Nice=19, from the pin), Result=success, exit 0;
  - five waves of lives, then each learner's band as 6 processes of 10, then the report; every wave waited on its own pids and every one of the 54 exits was 0.
  - **Actual: 8.45 CPU-min.**
- **All 162 records:**
  - the batched readers matched name_forced / answer_point with 0 mismatches at every life's end;
  - the ORACLEs' clones were identical to the learner on all 1,176 policy blocks;
  - every record carries PREREG-S1C2 5e4585c1… and code e3cc2ed.
- **The box:** scene-s1b1r and testb2-* were inactive at every heavy step (checked before the gate, the price and the unit).

## 4 · The declared readings and the coordinator's rulings (16:1x)
1. **UCB's t** = the policy blocks INCLUDING the one being picked (t = b − 4 ≥ 1): adopted.
2. **The replay learner's WORDS-LEARNED (so A) and M1** are read after the replay, on the state that enters the next block: adopted. «Its ORACLE and RANDOM are read the same way.»
3. **Gate 5 marks rather than stops:** adopted, as its text says.
4. **The shared streams:** RANDOM+REPLAY uses S1c's band pick streams `random-band:<seed>:<k>`, and every replay arm uses `replay:<seed>:<block>` (the room first, then the scene): adopted. «RANDOM+REPLAY sharing S1c's band pick streams is good: it pairs every replay-band life with a bare one, picks equal» — §1's paired reading uses exactly that.
5. **The identity** compares every field but cpu_s, wall_s, code, prereg and world: adopted. The addition was also built: the five masked fields are printed side by side for one record per arm, in the gate and in the report.
6. **The verdict order:** NOT GRADABLE BY NAME → FOR CHOICE → VOID → FAIL → CEILING-BOUND → PASS: adopted. «An arm reads FAIL if any meetable bar misses, and CEILING-BOUND only if every miss is a bar above its ceiling.»
7. **RULED, in the coordinator's words:** «the forgetting reading must include the replay.»
   - «What PROGRESS sees between a room's visits is PRE_b → PRE_{b+1} summed over the boundaries away: the block's interference PLUS the replay's repair.»
   - Every arm prints two 4 × 4 tables: (i) the BLOCK table, POST_b − PRE_b, and (ii) the FULL-STEP table, PRE_{b+1} − PRE_b, both by the block's room. For the bare learner they are identical (a pin: equal in every bare life). «The forgetting reading of (c) = the mean of the 12 off-diagonal entries of the FULL-STEP table, PROGRESS+REPLAY's against PROGRESS-S1C's, per seed»; the BLOCK table's off-diagonal is printed beside it as «interference before the repair».
   - N's drop fraction stays on the bracketed drops.
- **Declared by the builder, beyond these:**
  - π is drawn by rejection of permutations from `null:seed`;
  - NULL-NET's estimate is NET's permuted by π (room k's reading lands on π(k));
  - UCB's «bonus share» is bonus / (|est| + bonus) at the picked room;
  - the report's refutations read «as stated» only where they hold at all three seeds;
  - an identity miss anywhere would have made every bare-learner bar read NOT GRADABLE (IDENTITY). It did not arise.

## 5 · RAISED
Nothing could not be built as written. The declared readings above were sent before the gate and ruled; nothing was worked around.

## 6 · The suites on the unit's code (e3cc2ed; later commits touch only docs)
Each line is read from its log, and each log has 0 `ERROR:` / `FAIL:` blocks:
- **venv, the whole brain suite:** `Ran 594 tests in 268.073s` / `OK (skipped=3)` — log `/data/dev/brain-runs/scene-s1c2/logs/suite-venv-e3cc2ed.log`. That is S1c's 575 plus the 19 new tests.
- **/usr/bin/python3, the scene package:** `Ran 192 tests in 52.947s` / `OK` — log `…/logs/suite-scene-sys-e3cc2ed.log`.
- **Red on the parent 2679fb3:** the two new test modules `Ran 8 tests` / `FAILED (errors=8)`. The 7 picker tests error on the missing classes, and the 12 runner tests fail as one import error, because run_s1c2 does not exist there. Log `…/logs/redcheck-2679fb3.log`.
