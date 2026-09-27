# B1 VERDICT — seed 20261002 (graded)

tape sha `8f52116d0d241ca6…` · results b1-results-v4 · bars: §12 (the seat, 2026-09-26 12:08 +0400): bars from ceilings.json by ONE rule — AFTER k=8 of 12 (ceiling 0.886, k_min 4); BEFORE k=8 of 12 (ceiling 0.917, k_min 4); BETWEEN k=8 of 12 (ceiling 0.755, k_min 4); TWO_AFTER k=11 of 21 (ceiling 0.861, k_min 6); CHAIN k=11 of 25 (ceiling 0.873, k_min 6); TRANSFER k=13 of 18 (ceiling 0.869, k_min 8); NAME latin-upper 0.6692, latin-lower 0.7776; U1b 24/52 · U2b 69/104 · U6 4/10 · U4a 0.5 · U5 0.8 · KEEPS 5.0 pp · COST ≤ 307.521 ms per event (one world-day of alpha4-1's body, 93,652 rows, in 8 wall-hours on one thread; a tape event and a body row taken as one unit of work [Guessing]; the draft 3 × A0 = 4.785 ms is NOT used: A1-FIXED at H 64 reads 11.451 ms, so every network-bearing arm would fail it by construction (#228 b)); margins D1 10.0 pp · GROWS 5.0 pp · MA 3.0 pp at ≤ +10.0 % cost · interface 5.0 pp; NOT GRADABLE (organ limit): OTHER_CASE, MIRROR, LOOP, VOWEL

## The instrument (0c) — sound
- KEY: present; graded marks 19; failed []
- SHIFTED-KEY: present; failed 4 marks

## The composition nulls (SHUFFLED-RELATION, §4) — VOID or missing
- E′: ["VOID_BY_COST: SHUFFLED-RELATION:D — R45 at the floor (50,000 per sleep): the projection watch's lower bound fired inside sleep 6 (CPU 2.75 h ÷ pred_6 0.1558 h = r 17.6 > 24 ÷ 1.36); no re-price exists below the floor, so only this twin stops (B1.1, R47)"] — its U3 marks read NOT GRADABLE (R40, R44), never a pass on the bar alone
- F: ["VOID_BY_COST: SHUFFLED-RELATION:D — R45 at the floor (50,000 per sleep): the projection watch's lower bound fired inside sleep 6 (CPU 2.75 h ÷ pred_6 0.1558 h = r 17.6 > 24 ÷ 1.36); no re-price exists below the floor, so only this twin stops (B1.1, R47)"] — its U3 marks read NOT GRADABLE (R40, R44), never a pass on the bar alone

## A0
failed ['U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['C0a_CONST', 'C0a_SAME', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 1.719 ms per event over 9756 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NOT_APPLICABLE |
| C0a_SAME | no | — | 0.000 | 0.950 | None | None | 20 /  | NOT_APPLICABLE |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.118, latin-lower 0.140 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.538 | 24 | None | 0.250 | 52 / 28 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 9, refusals 31 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.644 | 69 | None | 0.500 | 104 / 67 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/24; latin-lower: 0/24 |
| U3_LOOP@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 14 / 0 | NO_BAR · latin-upper: 0/18; latin-lower: 0/24 |
| U3_VOWEL@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 40 / 0 | NO_BAR · latin-upper: 0/20; latin-lower: 0/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 16 /  |  |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.479, U1a_NAME:latin-lower 6.294, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.719 | 307.521 | None | None |  |  |

## A1
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 436.371 ms per event over 10890 events · size {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.100 | <= 4 of 20 | None | 0.037 | 20 / 2 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.231 | 24 | None | 0.250 | 52 / 12 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 436.371 | 307.521 | None | None |  |  |

## A1-ATT
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 47.764 ms per event over 10890 events · size {'h0': 89, 'h_alive': 89, 'hmax': 89, 'match': {'a1_final_names': 37, 'a1_final_params': 142852, 'solved_h': 89, 'twin_params_at_h_plus_1': 143699, 'twin_params_at_solved_h': 141822}, 'n_names': 37, 'n_params_active': 141822, 'variant': 'A1-ATT'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.100 | <= 4 of 20 | None | 0.037 | 20 / 2 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.231 | 24 | None | 0.250 | 52 / 12 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 47.764 | 307.521 | None | None |  |  |

## A1-BPTT-AWAKE
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 178.074 ms per event over 10890 events · size {'h0': 70, 'h_alive': 70, 'hmax': 1024, 'n_names': 37, 'n_params_active': 78687, 'variant': 'A1-BPTT-AWAKE'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.269 | 24 | None | 0.250 | 52 / 14 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.040 | 11 | 0.873 | 0.038 | 25 / 1 |  · latin-upper->latin-lower: 3/75; latin-lower->latin-upper: 3/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 178.074 | 307.521 | None | None |  |  |

## A1-FIXED
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 43.257 ms per event over 10890 events · size {'h0': 111, 'h_alive': 111, 'hmax': 111, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1-FIXED'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.100 | <= 4 of 20 | None | 0.037 | 20 / 2 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.212 | 24 | None | 0.250 | 52 / 11 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 43.257 | 307.521 | None | None |  |  |

## A1-LOCAL
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 262.116 ms per event over 10890 events · size {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1-LOCAL'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.308 | 24 | None | 0.250 | 52 / 16 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.056 | 13 | None | 0.111 | 18 / 1 |  · AFTER: 0/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 262.116 | 307.521 | None | None |  |  |

## A1-MA
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 47.811 ms per event over 10890 events · size {'h0': 90, 'h_alive': 90, 'hmax': 90, 'match': {'a1_final_names': 37, 'a1_final_params': 142852, 'solved_h': 90, 'twin_params_at_h_plus_1': 143856, 'twin_params_at_solved_h': 142035}, 'n_names': 37, 'n_params_active': 142035, 'variant': 'A1-MA'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.100 | <= 4 of 20 | None | 0.037 | 20 / 2 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.308 | 24 | None | 0.250 | 52 / 16 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 47.811 | 307.521 | None | None |  |  |

## A1-MLC
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 326.253 ms per event over 16398 events · size {'h0': 117, 'h_alive': 117, 'hmax': 1024, 'n_names': 37, 'n_params_active': 153370, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.308 | 24 | None | 0.250 | 52 / 16 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 326.253 | 307.521 | None | None |  |  |

## A1-NO-SLEEP
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 147.724 ms per event over 10890 events · size {'h0': 112, 'h_alive': 112, 'hmax': 1024, 'n_names': 37, 'n_params_active': 144585, 'variant': 'A1-NO-SLEEP'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.100 | <= 4 of 20 | None | 0.037 | 20 / 2 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.250 | 24 | None | 0.250 | 52 / 13 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 147.724 | 307.521 | None | None |  |  |

## A1-TEACH
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 438.565 ms per event over 10890 events · size {'h0': 110, 'h_alive': 110, 'hmax': 1024, 'n_names': 37, 'n_params_active': 141127, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.100 | <= 4 of 20 | None | 0.037 | 20 / 2 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.288 | 24 | None | 0.250 | 52 / 15 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 438.565 | 307.521 | None | None |  |  |

## A2
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 92.634 ms per event over 10890 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.050 | <= 4 of 20 | None | 0.037 | 20 / 1 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.050, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.308 | 24 | None | 0.250 | 52 / 16 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 4/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 2/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.592, U1a_NAME:latin-lower -1.049, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 92.634 | 307.521 | None | None |  |  |

## A3
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 160.928 ms per event over 10890 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.000, latin-lower 0.000 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.000 | 24 | None | 0.250 | 52 / 0 |  |
| U2a_REFUSES@T_L | yes | PASS | sure_names 0, refusals 40 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.404 | 69 | None | 0.500 | 104 / 42 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.438 | None | 0.500 | 0.500 | 16 / 7 | NO_BAR · latin-upper: 7/24; latin-lower: 13/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 11/24 |
| U3_VOWEL@T_L | no | — | 0.475 | None | 0.500 | 0.500 | 40 / 19 | NO_BAR · latin-upper: 10/20; latin-lower: 9/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 0.980 | 0.800 | None | None | 49 / 48 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR -6.250, LOOP 0.000, VOWEL -2.500 | 5.000 | None | None |  |  |
| COST | yes | PASS | 160.928 | 307.521 | None | None |  |  |

## A4
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 16.808 ms per event over 9756 events · size {'d_model': 92, 'ffn': 37, 'n_names': 37, 'n_params': 157086, 'n_params_numel': 157086, 'target': 142852, 'transcript_steps': 20397, 'within_10pct': True}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.000, latin-lower 0.000 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.192 | 24 | None | 0.250 | 52 / 10 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 0, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.040 | 11 | 0.873 | 0.038 | 25 / 1 |  · latin-upper->latin-lower: 3/75; latin-lower->latin-upper: 2/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper -3.846, U1a_NAME:latin-lower -3.846, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 4.000, MIRROR 12.500, LOOP 7.143, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 16.808 | 307.521 | None | None |  |  |

## A5
**VOID** — failed controls ['C0a_CONST', 'C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 115.251 ms per event over 16378 events · size {'net': {'h0': 112, 'h_alive': 112, 'hmax': 1024, 'n_names': 37, 'n_params_active': 144585, 'variant': 'A1'}, 'routed': {'cells': 1655, 'fallback': 453, 'lib': 0, 'net': 3665, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.133, latin-lower 0.147 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.596 | 24 | None | 0.250 | 52 / 31 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.644 | 69 | None | 0.500 | 104 / 67 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 16 /  |  |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.959, U1a_NAME:latin-lower 6.993, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 115.251 | 307.521 | None | None |  |  |

## D
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U2a_REFUSES@T_L', 'U3_TRANSFER@T_D', 'U4a_EXPLAINS_EXPERIENCE', 'U5_REJECTS_MISUSE', 'KEEPS', 'COST']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 498.303 ms per event over 9791 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | PASS | latin-upper 0.769, latin-lower 0.853 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.942 | 24 | None | 0.250 | 52 / 49 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | PASS | 0.933 | 69 | None | 0.500 | 104 / 97 |  |
| U3_AFTER@T_L | yes | PASS | 0.917 | 8 | 0.886 | 0.040 | 12 / 11 |  · latin-upper: 27/36; latin-lower: 32/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | PASS | 0.750 | 8 | 0.917 | 0.040 | 12 / 9 |  · latin-upper: 26/36; latin-lower: 28/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | PASS | 0.833 | 8 | 0.755 | 0.040 | 12 / 10 |  · latin-upper: 24/36; latin-lower: 29/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | PASS | 0.952 | 11 | 0.861 | 0.040 | 21 / 20 |  · latin-upper: 48/63; latin-lower: 58/63 |
| U3_OTHER_CASE@T_L | no | — | 0.600 | None | 0.861 | 0.038 | 5 / 3 | NO_BAR · latin-upper->latin-lower: 10/15; latin-lower->latin-upper: 8/15 |
| U3_CHAIN@T_L | yes | PASS | 0.640 | 11 | 0.873 | 0.038 | 25 / 16 |  · latin-upper->latin-lower: 45/75; latin-lower->latin-upper: 46/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 14/24 |
| U3_LOOP@T_L | no | — | 0.571 | None | 0.500 | 0.500 | 14 / 8 | NO_BAR · latin-upper: 11/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.575 | None | 0.500 | 0.500 | 40 / 23 | NO_BAR · latin-upper: 11/20; latin-lower: 12/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.611 | 13 | None | 0.111 | 18 / 11 |  · AFTER: 17/27; BEFORE: 17/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | FAIL | 0.000 | 0.500 | None | None | 26 /  |  |
| U4b_EXPLAINS_RULE | yes | PASS | AFTER 11, BEFORE 9, BETWEEN 10, TWO_AFTER 20, OTHER_CASE 3, CHAIN 16, MIRROR 8, LOOP 8, VOWEL 23 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.020 | 0.800 | None | None | 49 / 1 |  |
| U6_ONE_MEETING | yes | PASS | 0.600 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.479, U1a_NAME:latin-lower 4.196, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 9.524, OTHER_CASE 0.000, CHAIN 20.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 498.303 | 307.521 | None | None |  |  |

## E′
**VOID** — failed controls ['C0a_CONST', 'C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_OTHER_CASE@T_L', 'U3_CHAIN@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'U3_TRANSFER@T_D', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 2.451 ms per event over 14201 events · size {'routed': {'cells': 2108, 'fallback': 0, 'lib': 3212, 'net': 0, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.250 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.118, latin-lower 0.140 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.538 | 24 | None | 0.250 | 52 / 28 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 9, refusals 31 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.644 | 69 | None | 0.500 | 104 / 67 |  |
| U3_AFTER@T_L | no | — | 0.917 | 8 | 0.886 | 0.040 | 12 / 11 | TWIN_VOID · latin-upper: 27/36; latin-lower: 32/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | no | — | 0.750 | 8 | 0.917 | 0.040 | 12 / 9 | TWIN_VOID · latin-upper: 26/36; latin-lower: 28/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | no | — | 0.833 | 8 | 0.755 | 0.040 | 12 / 10 | TWIN_VOID · latin-upper: 24/36; latin-lower: 29/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | no | — | 0.952 | 11 | 0.861 | 0.040 | 21 / 20 | TWIN_VOID · latin-upper: 48/63; latin-lower: 58/63 |
| U3_OTHER_CASE@T_L | no | — | 0.600 | None | 0.861 | 0.038 | 5 / 3 | NO_BAR · latin-upper->latin-lower: 10/15; latin-lower->latin-upper: 8/15 |
| U3_CHAIN@T_L | no | — | 0.640 | 11 | 0.873 | 0.038 | 25 / 16 | TWIN_VOID · latin-upper->latin-lower: 45/75; latin-lower->latin-upper: 46/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 14/24 |
| U3_LOOP@T_L | no | — | 0.571 | None | 0.500 | 0.500 | 14 / 8 | NO_BAR · latin-upper: 11/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.575 | None | 0.500 | 0.500 | 40 / 23 | NO_BAR · latin-upper: 11/20; latin-lower: 12/20 |
| U3_TRANSFER@T_D | no | — | 0.611 | 13 | None | 0.111 | 18 / 11 | TWIN_VOID · AFTER: 17/27; BEFORE: 17/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 16 /  |  |
| U4b_EXPLAINS_RULE | yes | PASS | AFTER 11, BEFORE 9, BETWEEN 10, TWO_AFTER 20, OTHER_CASE 3, CHAIN 16, MIRROR 8, LOOP 8, VOWEL 23 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.020 | 0.800 | None | None | 49 / 1 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.479, U1a_NAME:latin-lower 6.294, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 9.524, OTHER_CASE 0.000, CHAIN 20.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 2.451 | 307.521 | None | None |  |  |

## F
**VOID** — failed controls ['C0a_CONST', 'C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_OTHER_CASE@T_L', 'U3_CHAIN@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'U3_TRANSFER@T_D', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 80.767 ms per event over 22035 events · size {'net': {'h0': 112, 'h_alive': 112, 'hmax': 1024, 'n_names': 37, 'n_params_active': 144585, 'variant': 'A1'}, 'routed': {'cells': 1655, 'fallback': 453, 'lib': 1977, 'net': 1688, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.250 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.133, latin-lower 0.157 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.596 | 24 | None | 0.250 | 52 / 31 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.644 | 69 | None | 0.500 | 104 / 67 |  |
| U3_AFTER@T_L | no | — | 0.917 | 8 | 0.886 | 0.040 | 12 / 11 | TWIN_VOID · latin-upper: 27/36; latin-lower: 32/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | no | — | 0.750 | 8 | 0.917 | 0.040 | 12 / 9 | TWIN_VOID · latin-upper: 26/36; latin-lower: 28/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | no | — | 0.833 | 8 | 0.755 | 0.040 | 12 / 10 | TWIN_VOID · latin-upper: 24/36; latin-lower: 29/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | no | — | 0.952 | 11 | 0.861 | 0.040 | 21 / 20 | TWIN_VOID · latin-upper: 48/63; latin-lower: 58/63 |
| U3_OTHER_CASE@T_L | no | — | 0.600 | None | 0.861 | 0.038 | 5 / 3 | NO_BAR · latin-upper->latin-lower: 10/15; latin-lower->latin-upper: 8/15 |
| U3_CHAIN@T_L | no | — | 0.640 | 11 | 0.873 | 0.038 | 25 / 16 | TWIN_VOID · latin-upper->latin-lower: 45/75; latin-lower->latin-upper: 46/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | no | — | 0.611 | 13 | None | 0.111 | 18 / 11 | TWIN_VOID · AFTER: 17/27; BEFORE: 17/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.941 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | yes | PASS | AFTER 11, BEFORE 9, BETWEEN 10, TWO_AFTER 20, OTHER_CASE 3, CHAIN 16, MIRROR 8, LOOP 8, VOWEL 23 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.020 | 0.800 | None | None | 49 / 1 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.959, U1a_NAME:latin-lower 8.042, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 9.524, OTHER_CASE 0.000, CHAIN 20.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 80.767 | 307.521 | None | None |  |  |

## FORCED:A0
failed ['U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['C0a_CONST', 'C0a_SAME', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 1.699 ms per event over 9756 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NOT_APPLICABLE |
| C0a_SAME | no | — | 0.000 | 0.950 | None | None | 20 /  | NOT_APPLICABLE |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.121, latin-lower 0.140 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 11, refusals 29 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.644 | 69 | None | 0.500 | 104 / 67 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/24; latin-lower: 0/24 |
| U3_LOOP@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 14 / 0 | NO_BAR · latin-upper: 0/18; latin-lower: 0/24 |
| U3_VOWEL@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 40 / 0 | NO_BAR · latin-upper: 0/20; latin-lower: 0/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.941 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.183, U1a_NAME:latin-lower 6.294, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.699 | 307.521 | None | None |  |  |

## FORCED:A1
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 547.984 ms per event over 10890 events · size {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.100 | <= 4 of 20 | None | 0.037 | 20 / 2 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.231 | 24 | None | 0.250 | 52 / 12 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.040 | 11 | 0.873 | 0.038 | 25 / 1 |  · latin-upper->latin-lower: 3/75; latin-lower->latin-upper: 3/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.056 | 13 | None | 0.111 | 18 / 1 |  · AFTER: 0/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 547.984 | 307.521 | None | None |  |  |

## FORCED:A1-TEACH
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 222.966 ms per event over 10890 events · size {'h0': 110, 'h_alive': 110, 'hmax': 1024, 'n_names': 37, 'n_params_active': 141127, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.100 | <= 4 of 20 | None | 0.037 | 20 / 2 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.288 | 24 | None | 0.250 | 52 / 15 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.040 | 11 | 0.873 | 0.038 | 25 / 1 |  · latin-upper->latin-lower: 3/75; latin-lower->latin-upper: 3/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.111 | 13 | None | 0.111 | 18 / 2 |  · AFTER: 3/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 222.966 | 307.521 | None | None |  |  |

## FORCED:A5
**VOID** — failed controls ['C0a_CONST', 'C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 377.164 ms per event over 16378 events · size {'net': {'h0': 112, 'h_alive': 112, 'hmax': 1024, 'n_names': 37, 'n_params_active': 144585, 'variant': 'A1'}, 'routed': {'cells': 1655, 'fallback': 453, 'lib': 0, 'net': 3665, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.133, latin-lower 0.147 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.596 | 24 | None | 0.250 | 52 / 31 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.644 | 69 | None | 0.500 | 104 / 67 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.040 | 11 | 0.873 | 0.038 | 25 / 1 |  · latin-upper->latin-lower: 3/75; latin-lower->latin-upper: 3/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.056 | 13 | None | 0.111 | 18 / 1 |  · AFTER: 0/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 16 /  |  |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.959, U1a_NAME:latin-lower 6.993, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 377.164 | 307.521 | None | None |  |  |

## KEY
failed none · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0d_CANARY': 'R26: KEY answers the canary from the truth by construction'}
cost: 0.000 ms per event over 9756 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | FAIL | 1.000 | <= 4 of 20 | None | 0.037 | 20 / 20 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | PASS | latin-upper 1.000, latin-lower 1.000 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 1.000 | 24 | None | 0.250 | 52 / 52 |  |
| U2a_REFUSES@T_L | yes | PASS | sure_names 0, refusals 40 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | PASS | 1.000 | 69 | None | 0.500 | 104 / 104 |  |
| U3_AFTER@T_L | yes | PASS | 1.000 | 8 | 0.886 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 36/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | PASS | 1.000 | 8 | 0.917 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 36/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | PASS | 1.000 | 8 | 0.755 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 36/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | PASS | 1.000 | 11 | 0.861 | 0.040 | 21 / 21 |  · latin-upper: 63/63; latin-lower: 63/63 |
| U3_OTHER_CASE@T_L | no | — | 1.000 | None | 0.861 | 0.038 | 5 / 5 | NO_BAR · latin-upper->latin-lower: 15/15; latin-lower->latin-upper: 15/15 |
| U3_CHAIN@T_L | yes | PASS | 1.000 | 11 | 0.873 | 0.038 | 25 / 25 |  · latin-upper->latin-lower: 75/75; latin-lower->latin-upper: 75/75 |
| U3_MIRROR@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 16 / 16 | NO_BAR · latin-upper: 24/24; latin-lower: 24/24 |
| U3_LOOP@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 14 / 14 | NO_BAR · latin-upper: 18/18; latin-lower: 24/24 |
| U3_VOWEL@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 40 / 40 | NO_BAR · latin-upper: 20/20; latin-lower: 20/20 |
| U3_TRANSFER@T_D | yes | PASS | 1.000 | 13 | None | 0.111 | 18 / 18 |  · AFTER: 27/27; BEFORE: 27/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | PASS | 1.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 0.000 | 307.521 | None | None |  |  |

## RING-READ
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U6_ONE_MEETING'] · not gradable ['C0a_CONST', 'C0a_SAME', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 0.000 ms per event over 9756 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NOT_APPLICABLE |
| C0a_SAME | no | — | 1.000 | 0.950 | None | None | 20 /  | NOT_APPLICABLE |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.000, latin-lower 0.000 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.000 | 24 | None | 0.250 | 52 / 0 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 0, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.000 | 69 | None | 0.500 | 104 / 0 |  |
| U3_AFTER@T_L | yes | PASS | 1.000 | 8 | 0.886 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 36/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | PASS | 1.000 | 8 | 0.917 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 36/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | PASS | 1.000 | 8 | 0.755 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 36/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/24; latin-lower: 0/24 |
| U3_LOOP@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 14 / 0 | NO_BAR · latin-upper: 0/18; latin-lower: 0/24 |
| U3_VOWEL@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 40 / 0 | NO_BAR · latin-upper: 0/20; latin-lower: 0/20 |
| U3_TRANSFER@T_D | yes | PASS | 1.000 | 13 | None | 0.111 | 18 / 18 |  · AFTER: 27/27; BEFORE: 27/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 0.000 | 307.521 | None | None |  |  |

## SHIFTED-KEY
failed ['U1b_PICK@T_L', 'U2b_LURES@T_L'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': '(0c): built to fail the graders; read only by the instrument rule', 'C0a_SAME': '(0c): built to fail the graders; read only by the instrument rule'}
cost: 0.000 ms per event over 9756 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.950 | 1.000 | None | None | 20 / 19 |  |
| C0a_SAME | yes | FAIL | 0.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.050 | <= 4 of 20 | None | 0.037 | 20 / 1 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | PASS | latin-upper 0.923, latin-lower 0.909 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.212 | 24 | None | 0.250 | 52 / 11 |  |
| U2a_REFUSES@T_L | yes | PASS | sure_names 1, refusals 39 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.000 | 69 | None | 0.500 | 104 / 0 |  |
| U3_AFTER@T_L | yes | PASS | 1.000 | 8 | 0.886 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 24/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | PASS | 1.000 | 8 | 0.917 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 24/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | PASS | 1.000 | 8 | 0.755 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 24/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | PASS | 1.000 | 11 | 0.861 | 0.040 | 21 / 21 |  · latin-upper: 63/63; latin-lower: 42/63 |
| U3_OTHER_CASE@T_L | no | — | 1.000 | None | 0.861 | 0.038 | 5 / 5 | NO_BAR · latin-upper->latin-lower: 15/15; latin-lower->latin-upper: 10/15 |
| U3_CHAIN@T_L | yes | PASS | 1.000 | 11 | 0.873 | 0.038 | 25 / 25 |  · latin-upper->latin-lower: 75/75; latin-lower->latin-upper: 50/75 |
| U3_MIRROR@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 16 / 16 | NO_BAR · latin-upper: 24/24; latin-lower: 22/24 |
| U3_LOOP@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 14 / 14 | NO_BAR · latin-upper: 18/18; latin-lower: 22/24 |
| U3_VOWEL@T_L | no | — | 0.950 | None | 0.500 | 0.500 | 40 / 38 | NO_BAR · latin-upper: 20/20; latin-lower: 18/20 |
| U3_TRANSFER@T_D | yes | PASS | 1.000 | 13 | None | 0.111 | 18 / 18 |  · AFTER: 18/27; BEFORE: 18/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 0.980 | 0.800 | None | None | 49 / 48 |  |
| U6_ONE_MEETING | yes | PASS | 0.900 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL -2.500 | 5.000 | None | None |  |  |
| COST | yes | PASS | 0.000 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A0
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING'] · not gradable ['C0a_CONST', 'C0a_SAME', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 1.938 ms per event over 9756 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NOT_APPLICABLE |
| C0a_SAME | no | — | 0.000 | 0.950 | None | None | 20 /  | NOT_APPLICABLE |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.041, latin-lower 0.031 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.250 | 24 | None | 0.250 | 52 / 13 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 9, refusals 31 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.510 | 69 | None | 0.500 | 104 / 53 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/24; latin-lower: 0/24 |
| U3_LOOP@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 14 / 0 | NO_BAR · latin-upper: 0/18; latin-lower: 0/24 |
| U3_VOWEL@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 40 / 0 | NO_BAR · latin-upper: 0/20; latin-lower: 0/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | 0.667 | 0.500 | None | None | 3 /  | NOT_GRADABLE_N_LT_13 |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 1.479, U1a_NAME:latin-lower 2.797, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.938 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A1
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R22: every name the tape teaches is mapped, CONST's answer `a` too"}
cost: 556.749 ms per event over 10890 events · size {'h0': 90, 'h_alive': 90, 'hmax': 1024, 'n_names': 37, 'n_params_active': 108307, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.000, latin-lower 0.000 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.269 | 24 | None | 0.250 | 52 / 14 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 1/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper -3.846, U1a_NAME:latin-lower -3.846, AFTER -8.333, BEFORE 0.000, BETWEEN -8.333, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 556.749 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A1-TEACH
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R22: every name the tape teaches is mapped, CONST's answer `a` too"}
cost: 586.687 ms per event over 10890 events · size {'h0': 90, 'h_alive': 90, 'hmax': 1024, 'n_names': 37, 'n_params_active': 108307, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.250 | 24 | None | 0.250 | 52 / 13 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 586.687 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A5
**VOID** — failed controls ['C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_SAME', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R22: every name the tape teaches is mapped, CONST's answer `a` too"}
cost: 370.175 ms per event over 16393 events · size {'net': {'h0': 90, 'h_alive': 90, 'hmax': 1024, 'n_names': 37, 'n_params_active': 108307, 'variant': 'A1'}, 'routed': {'cells': 1640, 'fallback': 468, 'lib': 0, 'net': 3680, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.050 | <= 4 of 20 | None | 0.037 | 20 / 1 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.062, latin-lower 0.052 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.327 | 24 | None | 0.250 | 52 / 17 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.510 | 69 | None | 0.500 | 104 / 53 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 1/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | 0.500 | 0.500 | None | None | 4 /  | NOT_GRADABLE_N_LT_13 |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.184 | 0.800 | None | None | 49 / 9 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.550, U1a_NAME:latin-lower 4.895, AFTER 0.000, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 370.175 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:A1
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, CONST's too"}
cost: 558.632 ms per event over 10890 events · size {'h0': 112, 'h_alive': 112, 'hmax': 1024, 'n_names': 37, 'n_params_active': 144585, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.212 | 24 | None | 0.250 | 52 / 11 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 558.632 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:A1-TEACH
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, CONST's too"}
cost: 240.825 ms per event over 10890 events · size {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.288 | 24 | None | 0.250 | 52 / 15 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 240.825 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:A5
failed ['U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, CONST's too", 'C0a_SAME': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, SAME's too"}
cost: 364.633 ms per event over 16378 events · size {'net': {'h0': 112, 'h_alive': 112, 'hmax': 1024, 'n_names': 37, 'n_params_active': 144585, 'variant': 'A1'}, 'routed': {'cells': 1655, 'fallback': 453, 'lib': 0, 'net': 3665, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.127, latin-lower 0.147 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.596 | 24 | None | 0.250 | 52 / 31 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.644 | 69 | None | 0.500 | 104 / 67 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/24; latin-lower: 9/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.938 | 0.500 | None | None | 16 /  |  |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.367, U1a_NAME:latin-lower 6.993, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 364.633 | 307.521 | None | None |  |  |

## The decisions (§6, §4.1, §4.2) — this seed's inputs; the rule needs BOTH seeds
- selection candidates (all bars this seed; VOID = a failed control, §5.5): {'A5': 'VOID', 'E′': 'VOID', 'F': 'VOID'} · void by {'A5': ['C0a_CONST', 'C0a_SAME'], 'E′': ['C0a_CONST', 'C0a_SAME'], 'F': ['C0a_CONST', 'C0a_SAME']}
- D1 (i) F − A5 on TWO_AFTER / CHAIN: not computable — VOID {'F': ['C0a_CONST', 'C0a_SAME'], 'A5': ['C0a_CONST', 'C0a_SAME']}
- D1 (iii) D − A1 (diagnostic): not computable — VOID {'D': ['C0a_CONST'], 'A1': ['C0a_CONST']}
- GROWS A1 − A1-FIXED: not computable — VOID {'A1': ['C0a_CONST'], 'A1-FIXED': ['C0a_CONST']}
- D1 (ii) E′ vs F: not computable — VOID {'E′': ['C0a_CONST', 'C0a_SAME'], 'F': ['C0a_CONST', 'C0a_SAME']}
- Memory Attention: claim VOID {'A1-MA': ['C0a_CONST'], 'A1': ['C0a_CONST']} · isolation VOID {'A1-MA': ['C0a_CONST'], 'A1-ATT': ['C0a_CONST']} 
- interface: {'arms_present': [], 'void': {'A5': ['C0a_CONST', 'C0a_SAME']}}
- examples-to-bar (TWO_AFTER): {'A1-MLC': {'void': ['C0a_CONST']}, 'D': {'void': ['C0a_CONST']}, 'A1': {'void': ['C0a_CONST']}}
- A1-TEACH (R46 — a diagnostic; decides nothing by itself): NOT COMPUTABLE — void {'A1-TEACH': ['C0a_CONST'], 'A1': ['C0a_CONST']} · U1a so far {'A1-TEACH': {'latin-upper': 0.038461538461538464, 'latin-lower': 0.038461538461538464}, 'A1': {'latin-upper': 0.038461538461538464, 'latin-lower': 0.038461538461538464}, 'SHUFFLED-NAME:A1-TEACH': {'latin-upper': 0.038461538461538464, 'latin-lower': 0.038461538461538464}}

## Reading rules
- A mark NOT GRADED is never counted as failed; «no road» names a capability the arm does not have; INSTRUMENT-VOID (0c) names the instrument, never the arm; an arm VOID names a §5.5 control that arm failed — never «failed» (R40).
- REACH families are printed beside RING-READ (reach given the name); the U3 verdict rests on the discriminating families TWO_AFTER · OTHER_CASE · CHAIN.
