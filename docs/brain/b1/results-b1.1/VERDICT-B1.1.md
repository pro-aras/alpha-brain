# B1.1 — VERDICT (both seeds)

*edit: Claude (Opus 5.5), 2026-09-27 21:28 +0400 — written from the two graded records (b1-results-v4; `results-b1.1/20261001/results.sha256` 49672eab…, `20261002/` 4287c902…), by the rules declared before the runs: §5.5 / R40 (a failed control VOIDS an arm), R44 (a missing null reads NOT GRADABLE), R47 (the tape), R48 (how COST is read). Tapes: `/data/dev/brain-runs/b1.1/<seed>/` (91642649… / 8f52116d…). Code: genome-wt-b1-tape2 615376c (runs), 2b2b33d (grader).*

## In plain words
1. **The fixed tape did what it was built to do.** The CONST control is now taught before a sleep, so every learner can be graded on it. **Every learner that can be graded on it fails it.** By the rule written before the runs (a failed basic control VOIDS the arm), no learner can be READ on B1.1. The selection rule and D1 cannot be computed.
2. **The rule library D still does its job — on both seeds now — but it is VOID by the letter.**
   - It names letters on unseen fonts above the bars and passes all five relation families at both seeds, and it explains its rules.
   - It answers NOTHING to every CONST ask, 78 of 78 in training and 20 of 20 in the test: it never forms «the answer is always a». Its program language seems to have no constant.
3. **The networks still give one name to every letter** («l» / «n»), on the fixed tape too. The cause is their answer readout (brain r2, co-signed). B1.2 tests the fix tonight.
4. **COST fails for D and the A1 family, measured under crowding** (load 9–15 at the end of each run). D reads 110 ms per event in a quiet run; A1's cost is its 1,024-wide buffers (A1-FIXED at the same live width: 43–51). R48 prints this beside the marks; the marks stand.

## The instrument (0c) — sound at both seeds
KEY fails nothing; SHIFTED-KEY fails U1b and U2b (a shifted answer stream cannot pass the graders).

## Every learner arm, by the letter
| arm | seed 20261001 | seed 20261002 |
|---|---|---|
| D (rule library) | VOID by C0a_CONST (0/20) | VOID by C0a_CONST (0/20) |
| A1, A1-TEACH, A1 twins, A2, A3, A4 (networks) | VOID by C0a_CONST | VOID by C0a_CONST |
| A5, E′, F (hybrids) | VOID by C0a_CONST + C0a_SAME | VOID by C0a_CONST + C0a_SAME |
| A0 (cells) | read (CONST NOT APPLICABLE, R38): fails U1a (0.105 / 0.089), U2a, U2b, U3, U6 | read: fails U1a (0.140 / 0.118), U2a, U2b, U3, U6, KEEPS |

**Nulls:**
- seed 1 — every SHUFFLED-RELATION twin complete (the twin search closed all 17 sleeps; its loaders ran);
- seed 2 — the twin search was VOID by cost at 18:33 (R45 at the floor), so E′'s and F's U3 read NOT GRADABLE, TWIN_VOID by cost (R44). They are VOID by their controls anyway.

## §6's decisions — none computable
- **The selection** (A5, E′, F): VOID at both seeds.
- **D1 (i) F − A5 and (ii) E′ vs F:** not computable (VOID).
- **The A1-TEACH diagnostic:** A1 0.038, A1-TEACH 0.038, SHUFFLED-NAME:A1-TEACH 0.038 on both cases, both seeds — TEACH alone changes nothing (R46 READING, confirmed on B1.1).

## D's would-be readings — printed for the record, read by no decision (R40)
| mark | bar | seed 20261001 | seed 20261002 |
|---|---|---|---|
| U1a naming, unseen fonts (lower / upper) | 0.778 / 0.669 | **0.857 / 0.778** | **0.853 / 0.769** |
| U1b pick | 24 of 52 | 48/52 | 49/52 |
| U2b lures | 69 of 104 | 87/104 | 97/104 |
| U3 AFTER | 8 of 12 | **12/12** | **11/12** |
| U3 BEFORE | 8 of 12 | **12/12** | **9/12** |
| U3 BETWEEN | 8 of 12 | **10/12** | **10/12** |
| U3 TWO_AFTER (3 taught pairs) | 11 of 21 | **18/21** | **20/21** |
| U3 CHAIN (never shown chained) | 11 of 25 | **14/25** | **16/25** |
| U4b explains its rule | per family | passes | passes |
| U2a refuses never-taught signs | ≥ 32 of 40 refused | 0 refused | 0 refused |
| U3 TRANSFER to the digits | 13 of 18 | 11/18 | 11/18 |
| U4a explains from experience | 0.5 | 0.0 | 0.0 |
| U5 rejects misuse | 0.8 | 0.041 | 0.02 |
| U6 one meeting | 4 of 10 | 2/10 | 6/10 |
| KEEPS | ≤ 5 pp | fails (BETWEEN −16.7, CHAIN −12, OTHER_CASE −20) | fails (CHAIN −20, TWO_AFTER −9.5) |
| C0a SAME | 0.95 | 1.0 | 1.0 |
| **C0a CONST** | 1.0 | **0/20 — NOTHING** | **0/20 — NOTHING** |
| COST (R48: under crowding, load ≈ 15) | 307.5 ms | 389 | 498 |

## What B1.1 settles, and what follows
- **Settled:**
  - D's relation learning replicates on both seeds at the floor budget (50,000), with its shuffled twin at 0 where it exists (seed 1 here; seed 2 on B1.0).
  - The networks' one-name collapse survives the schedule fix: it is the readout (brain r2).
  - Every learner fails CONST.
- **Named, not yet declared:** D's constant gap. A rule library that cannot say «always a» fails the simplest rule there is (his IF / THEN includes «whatever it is, answer a»). The next D declaration adds a name constant to its program language and re-runs D and its twin — the only way D can be READ by the letter.
- **Tonight:** B1.2 «THE READER» (R49 + its addendum) on these tapes. Its network arms meet the same CONST control; a VOID there reads «not computable» under R49's rule, with the would-be marks printed. IN-SLDA answers NOTHING to every relation cue by design, so CONST is NOT APPLICABLE to it (R38).
