# B1 VERDICT — seed 20261002 (graded)

tape sha `bcc7a4f5251cdcdf…` · results b1-results-v4.1 · bars: §12 (the seat, 2026-09-26 12:08 +0400): bars from ceilings.json by ONE rule — AFTER k=8 of 12 (ceiling 0.886, k_min 4); BEFORE k=8 of 12 (ceiling 0.917, k_min 4); BETWEEN k=8 of 12 (ceiling 0.755, k_min 4); TWO_AFTER k=11 of 21 (ceiling 0.861, k_min 6); CHAIN k=11 of 25 (ceiling 0.873, k_min 6); TRANSFER k=13 of 18 (ceiling 0.869, k_min 8); NAME latin-upper 0.6692, latin-lower 0.7776; U1b 24/52 · U2b 69/104 · U6 4/10 · U4a 0.5 · U5 0.8 · KEEPS 5.0 pp · COST ≤ 307.521 ms per event (one world-day of alpha4-1's body, 93,652 rows, in 8 wall-hours on one thread; a tape event and a body row taken as one unit of work [Guessing]; the draft 3 × A0 = 4.785 ms is NOT used: A1-FIXED at H 64 reads 11.451 ms, so every network-bearing arm would fail it by construction (#228 b)); margins D1 10.0 pp · GROWS 5.0 pp · MA 3.0 pp at ≤ +10.0 % cost · interface 5.0 pp; NOT GRADABLE (organ limit): OTHER_CASE, MIRROR, LOOP, VOWEL

## The instrument (0c) — sound
- KEY: present; graded marks 19; failed []
- SHIFTED-KEY: present; failed 4 marks

## A0
failed ['U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['C0a_CONST', 'C0a_SAME', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 1.382 ms per event over 9755 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NOT_APPLICABLE |
| C0a_SAME | no | — | 0.000 | 0.950 | None | None | 20 /  | NOT_APPLICABLE |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.130, latin-lower 0.164 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 11, refusals 29 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.654 | 69 | None | 0.500 | 104 / 68 |  |
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
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.071, U1a_NAME:latin-lower 7.343, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.382 | 307.521 | None | None |  |  |

## A1
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 363.993 ms per event over 10826 events · size {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.269 | 24 | None | 0.250 | 52 / 14 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 363.993 | 307.521 | None | None |  |  |

## A1-ATT
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 29.368 ms per event over 10826 events · size {'h0': 89, 'h_alive': 89, 'hmax': 89, 'match': {'a1_final_names': 37, 'a1_final_params': 142852, 'solved_h': 89, 'twin_params_at_h_plus_1': 143699, 'twin_params_at_solved_h': 141822}, 'n_names': 37, 'n_params_active': 141822, 'variant': 'A1-ATT'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.250 | 24 | None | 0.250 | 52 / 13 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 29.368 | 307.521 | None | None |  |  |

## A1-BPTT-AWAKE
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 164.004 ms per event over 10826 events · size {'h0': 70, 'h_alive': 70, 'hmax': 1024, 'n_names': 37, 'n_params_active': 78687, 'variant': 'A1-BPTT-AWAKE'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.231 | 24 | None | 0.250 | 52 / 12 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 164.004 | 307.521 | None | None |  |  |

## A1-FIXED
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 27.625 ms per event over 10826 events · size {'h0': 111, 'h_alive': 111, 'hmax': 111, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1-FIXED'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.308 | 24 | None | 0.250 | 52 / 16 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 27.625 | 307.521 | None | None |  |  |

## A1-LOCAL
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 310.403 ms per event over 10826 events · size {'h0': 116, 'h_alive': 116, 'hmax': 1024, 'n_names': 37, 'n_params_active': 151597, 'variant': 'A1-LOCAL'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.288 | 24 | None | 0.250 | 52 / 15 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 1/75; latin-lower->latin-upper: 1/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.056 | 13 | None | 0.111 | 18 / 1 |  · AFTER: 0/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.102 | 0.800 | None | None | 49 / 5 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 310.403 | 307.521 | None | None |  |  |

## A1-MA
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 33.226 ms per event over 10826 events · size {'h0': 90, 'h_alive': 90, 'hmax': 90, 'match': {'a1_final_names': 37, 'a1_final_params': 142852, 'solved_h': 90, 'twin_params_at_h_plus_1': 143856, 'twin_params_at_solved_h': 142035}, 'n_names': 37, 'n_params_active': 142035, 'variant': 'A1-MA'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.288 | 24 | None | 0.250 | 52 / 15 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| U5_REJECTS_MISUSE | yes | FAIL | 0.122 | 0.800 | None | None | 49 / 6 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 33.226 | 307.521 | None | None |  |  |

## A1-MLC
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 261.102 ms per event over 16334 events · size {'h0': 113, 'h_alive': 113, 'hmax': 1024, 'n_names': 37, 'n_params_active': 146326, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.231 | 24 | None | 0.250 | 52 / 12 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 261.102 | 307.521 | None | None |  |  |

## A1-NO-SLEEP
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 134.374 ms per event over 10826 events · size {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1-NO-SLEEP'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.250 | 24 | None | 0.250 | 52 / 13 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 134.374 | 307.521 | None | None |  |  |

## A1-TEACH
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 321.204 ms per event over 10826 events · size {'h0': 115, 'h_alive': 115, 'hmax': 1024, 'n_names': 37, 'n_params_active': 149832, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.327 | 24 | None | 0.250 | 52 / 17 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 321.204 | 307.521 | None | None |  |  |

## A2
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 95.006 ms per event over 10826 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.308 | 24 | None | 0.250 | 52 / 16 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 95.006 | 307.521 | None | None |  |  |

## A3
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 142.210 ms per event over 10826 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.950 | 1.000 | None | None | 20 / 19 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.035 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.000 | 24 | None | 0.250 | 52 / 0 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.490 | 69 | None | 0.500 | 104 / 51 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 8/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 11/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.224 | 0.800 | None | None | 49 / 11 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 7.143, VOWEL 2.500 | 5.000 | None | None |  |  |
| COST | yes | PASS | 142.210 | 307.521 | None | None |  |  |

## A4
**VOID** — failed controls ['C0a_CONST'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 22.894 ms per event over 9755 events · size {'d_model': 92, 'ffn': 37, 'n_names': 37, 'n_params': 157086, 'n_params_numel': 157086, 'target': 142852, 'transcript_steps': 20397, 'within_10pct': True}

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
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.040 | 11 | 0.873 | 0.038 | 25 / 1 |  · latin-upper->latin-lower: 2/75; latin-lower->latin-upper: 4/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER -4.762, OTHER_CASE 0.000, CHAIN 4.000, MIRROR -6.250, LOOP 7.143, VOWEL 7.500 | 5.000 | None | None |  |  |
| COST | yes | PASS | 22.894 | 307.521 | None | None |  |  |

## A5
**VOID** — failed controls ['C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 80.920 ms per event over 16301 events · size {'net': {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1'}, 'routed': {'cells': 1659, 'fallback': 449, 'lib': 0, 'net': 3661, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | FAIL | 0.150 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.139, latin-lower 0.175 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.615 | 24 | None | 0.250 | 52 / 32 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 32, refusals 8 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.654 | 69 | None | 0.500 | 104 / 68 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.941 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.959, U1a_NAME:latin-lower 8.392, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 80.920 | 307.521 | None | None |  |  |

## D
failed ['U2a_REFUSES@T_L', 'U3_TRANSFER@T_D', 'U4a_EXPLAINS_EXPERIENCE', 'U5_REJECTS_MISUSE', 'KEEPS'] · not gradable ['C0a_CONST', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 110.543 ms per event over 9790 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NO_SLEEP_BEFORE_SITTING |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | PASS | latin-upper 0.769, latin-lower 0.853 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.769 | 24 | None | 0.250 | 52 / 40 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | PASS | 0.933 | 69 | None | 0.500 | 104 / 97 |  |
| U3_AFTER@T_L | yes | PASS | 0.917 | 8 | 0.886 | 0.040 | 12 / 11 |  · latin-upper: 27/36; latin-lower: 32/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | PASS | 0.750 | 8 | 0.917 | 0.040 | 12 / 9 |  · latin-upper: 26/36; latin-lower: 28/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | PASS | 0.833 | 8 | 0.755 | 0.040 | 12 / 10 |  · latin-upper: 24/36; latin-lower: 29/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | PASS | 0.952 | 11 | 0.861 | 0.040 | 21 / 20 |  · latin-upper: 48/63; latin-lower: 58/63 |
| U3_OTHER_CASE@T_L | no | — | 1.000 | None | 0.861 | 0.038 | 5 / 5 | NO_BAR · latin-upper->latin-lower: 14/15; latin-lower->latin-upper: 12/15 |
| U3_CHAIN@T_L | yes | PASS | 0.840 | 11 | 0.873 | 0.038 | 25 / 21 |  · latin-upper->latin-lower: 56/75; latin-lower->latin-upper: 63/75 |
| U3_MIRROR@T_L | no | — | 0.562 | None | 0.500 | 0.500 | 16 / 9 | NO_BAR · latin-upper: 12/24; latin-lower: 14/24 |
| U3_LOOP@T_L | no | — | 0.571 | None | 0.500 | 0.500 | 14 / 8 | NO_BAR · latin-upper: 11/18; latin-lower: 13/24 |
| U3_VOWEL@T_L | no | — | 0.575 | None | 0.500 | 0.500 | 40 / 23 | NO_BAR · latin-upper: 11/20; latin-lower: 12/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.611 | 13 | None | 0.111 | 18 / 11 |  · AFTER: 17/27; BEFORE: 17/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | FAIL | 0.000 | 0.500 | None | None | 26 /  |  |
| U4b_EXPLAINS_RULE | yes | PASS | AFTER 11, BEFORE 9, BETWEEN 10, TWO_AFTER 20, OTHER_CASE 5, CHAIN 21, MIRROR 9, LOOP 8, VOWEL 23 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.143 | 0.800 | None | None | 49 / 7 |  |
| U6_ONE_MEETING | yes | PASS | 0.600 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.479, U1a_NAME:latin-lower 4.196, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 9.524, OTHER_CASE 0.000, CHAIN 4.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 110.543 | 307.521 | None | None |  |  |

## E′
**VOID** — failed controls ['C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['C0a_CONST', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 0.976 ms per event over 14199 events · size {'routed': {'cells': 2108, 'fallback': 0, 'lib': 3212, 'net': 0, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NO_SLEEP_BEFORE_SITTING |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.130, latin-lower 0.164 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 11, refusals 29 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.654 | 69 | None | 0.500 | 104 / 68 |  |
| U3_AFTER@T_L | yes | PASS | 0.917 | 8 | 0.886 | 0.040 | 12 / 11 |  · latin-upper: 27/36; latin-lower: 32/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | PASS | 0.750 | 8 | 0.917 | 0.040 | 12 / 9 |  · latin-upper: 26/36; latin-lower: 28/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | PASS | 0.833 | 8 | 0.755 | 0.040 | 12 / 10 |  · latin-upper: 24/36; latin-lower: 29/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | PASS | 0.952 | 11 | 0.861 | 0.040 | 21 / 20 |  · latin-upper: 48/63; latin-lower: 58/63 |
| U3_OTHER_CASE@T_L | no | — | 1.000 | None | 0.861 | 0.038 | 5 / 5 | NO_BAR · latin-upper->latin-lower: 14/15; latin-lower->latin-upper: 12/15 |
| U3_CHAIN@T_L | yes | PASS | 0.840 | 11 | 0.873 | 0.038 | 25 / 21 |  · latin-upper->latin-lower: 56/75; latin-lower->latin-upper: 63/75 |
| U3_MIRROR@T_L | no | — | 0.562 | None | 0.500 | 0.500 | 16 / 9 | NO_BAR · latin-upper: 12/24; latin-lower: 14/24 |
| U3_LOOP@T_L | no | — | 0.571 | None | 0.500 | 0.500 | 14 / 8 | NO_BAR · latin-upper: 11/18; latin-lower: 13/24 |
| U3_VOWEL@T_L | no | — | 0.575 | None | 0.500 | 0.500 | 40 / 23 | NO_BAR · latin-upper: 11/20; latin-lower: 12/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.611 | 13 | None | 0.111 | 18 / 11 |  · AFTER: 17/27; BEFORE: 17/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | yes | PASS | AFTER 11, BEFORE 9, BETWEEN 10, TWO_AFTER 20, OTHER_CASE 5, CHAIN 21, MIRROR 9, LOOP 8, VOWEL 23 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.143 | 0.800 | None | None | 49 / 7 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.071, U1a_NAME:latin-lower 7.343, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 9.524, OTHER_CASE 0.000, CHAIN 4.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 0.976 | 307.521 | None | None |  |  |

## F
**VOID** — failed controls ['C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 29.149 ms per event over 21957 events · size {'net': {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1'}, 'routed': {'cells': 1659, 'fallback': 449, 'lib': 1884, 'net': 1777, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.139, latin-lower 0.175 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.615 | 24 | None | 0.250 | 52 / 32 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 32, refusals 8 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.654 | 69 | None | 0.500 | 104 / 68 |  |
| U3_AFTER@T_L | yes | PASS | 0.917 | 8 | 0.886 | 0.040 | 12 / 11 |  · latin-upper: 27/36; latin-lower: 32/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | PASS | 0.750 | 8 | 0.917 | 0.040 | 12 / 9 |  · latin-upper: 26/36; latin-lower: 28/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | PASS | 0.833 | 8 | 0.755 | 0.040 | 12 / 10 |  · latin-upper: 24/36; latin-lower: 29/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | PASS | 0.952 | 11 | 0.861 | 0.040 | 21 / 20 |  · latin-upper: 48/63; latin-lower: 58/63 |
| U3_OTHER_CASE@T_L | no | — | 1.000 | None | 0.861 | 0.038 | 5 / 5 | NO_BAR · latin-upper->latin-lower: 14/15; latin-lower->latin-upper: 12/15 |
| U3_CHAIN@T_L | yes | PASS | 0.840 | 11 | 0.873 | 0.038 | 25 / 21 |  · latin-upper->latin-lower: 56/75; latin-lower->latin-upper: 63/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.278 | 13 | None | 0.111 | 18 / 5 |  · AFTER: 17/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.941 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | yes | PASS | AFTER 11, BEFORE 9, BETWEEN 10, TWO_AFTER 20, OTHER_CASE 5, CHAIN 21, MIRROR 9, LOOP 8, VOWEL 23 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.143 | 0.800 | None | None | 49 / 7 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.959, U1a_NAME:latin-lower 8.392, AFTER 0.000, BEFORE 75.000, BETWEEN 0.000, TWO_AFTER 9.524, OTHER_CASE 0.000, CHAIN 4.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 29.149 | 307.521 | None | None |  |  |

## FORCED:A0
failed ['U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['C0a_CONST', 'C0a_SAME', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 1.601 ms per event over 9755 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NOT_APPLICABLE |
| C0a_SAME | no | — | 0.000 | 0.950 | None | None | 20 /  | NOT_APPLICABLE |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.133, latin-lower 0.164 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.577 | 24 | None | 0.250 | 52 / 30 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 11, refusals 29 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.654 | 69 | None | 0.500 | 104 / 68 |  |
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
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.944 | 0.500 | None | None | 18 /  |  |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.071, U1a_NAME:latin-lower 7.343, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.601 | 307.521 | None | None |  |  |

## FORCED:A1
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 111.179 ms per event over 10826 events · size {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.269 | 24 | None | 0.250 | 52 / 14 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.040 | 11 | 0.873 | 0.038 | 25 / 1 |  · latin-upper->latin-lower: 3/75; latin-lower->latin-upper: 3/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.056 | 13 | None | 0.111 | 18 / 1 |  · AFTER: 0/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 111.179 | 307.521 | None | None |  |  |

## FORCED:A1-TEACH
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 333.170 ms per event over 10826 events · size {'h0': 115, 'h_alive': 115, 'hmax': 1024, 'n_names': 37, 'n_params_active': 149832, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.327 | 24 | None | 0.250 | 52 / 17 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 2/75; latin-lower->latin-upper: 3/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.111 | 13 | None | 0.111 | 18 / 2 |  · AFTER: 3/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 333.170 | 307.521 | None | None |  |  |

## FORCED:A5
**VOID** — failed controls ['C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 63.292 ms per event over 16301 events · size {'net': {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1'}, 'routed': {'cells': 1659, 'fallback': 449, 'lib': 0, 'net': 3661, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | FAIL | 0.150 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.150 | <= 4 of 20 | None | 0.037 | 20 / 3 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.139, latin-lower 0.175 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.615 | 24 | None | 0.250 | 52 / 32 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 32, refusals 8 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.654 | 69 | None | 0.500 | 104 / 68 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.040 | 11 | 0.873 | 0.038 | 25 / 1 |  · latin-upper->latin-lower: 3/75; latin-lower->latin-upper: 2/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.056 | 13 | None | 0.111 | 18 / 1 |  · AFTER: 0/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.941 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.959, U1a_NAME:latin-lower 8.392, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 63.292 | 307.521 | None | None |  |  |

## KEY
failed none · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0d_CANARY': 'R26: KEY answers the canary from the truth by construction'}
cost: 0.000 ms per event over 9755 events · size {}

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
cost: 0.000 ms per event over 9755 events · size {}

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
cost: 0.000 ms per event over 9755 events · size {}

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
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 0.000 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A0
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING'] · not gradable ['C0a_CONST', 'C0a_SAME', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 1.936 ms per event over 9755 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NOT_APPLICABLE |
| C0a_SAME | no | — | 0.000 | 0.950 | None | None | 20 /  | NOT_APPLICABLE |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.050, latin-lower 0.035 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.231 | 24 | None | 0.250 | 52 / 12 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 11, refusals 29 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
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
| U4a_EXPLAINS_EXPERIENCE | no | — | 0.750 | 0.500 | None | None | 4 /  | NOT_GRADABLE_N_LT_13 |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 2.367, U1a_NAME:latin-lower 3.147, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.936 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A1
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R22: every name the tape teaches is mapped, CONST's answer `a` too"}
cost: 506.712 ms per event over 10826 events · size {'h0': 90, 'h_alive': 90, 'hmax': 1024, 'n_names': 37, 'n_params_active': 108307, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.000, latin-lower 0.000 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.231 | 24 | None | 0.250 | 52 / 12 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper -3.846, U1a_NAME:latin-lower -3.846, AFTER -8.333, BEFORE 0.000, BETWEEN -8.333, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 506.712 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A1-TEACH
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R22: every name the tape teaches is mapped, CONST's answer `a` too"}
cost: 341.703 ms per event over 10826 events · size {'h0': 90, 'h_alive': 90, 'hmax': 1024, 'n_names': 37, 'n_params_active': 108307, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.000, latin-lower 0.000 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.212 | 24 | None | 0.250 | 52 / 11 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
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
| U5_REJECTS_MISUSE | yes | FAIL | 0.082 | 0.800 | None | None | 49 / 4 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper -3.846, U1a_NAME:latin-lower -3.846, AFTER -8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 341.703 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A5
**VOID** — failed controls ['C0a_SAME'] (§5.5: a failing control VOIDS the arm, never «fails» it; its marks are printed for the record and read by no decision) · would-be failures, read by nothing: ['C0a_SAME', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'COST']
not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R22: every name the tape teaches is mapped, CONST's answer `a` too"}
cost: 334.242 ms per event over 16316 events · size {'net': {'h0': 90, 'h_alive': 90, 'hmax': 1024, 'n_names': 37, 'n_params_active': 108307, 'variant': 'A1'}, 'routed': {'cells': 1644, 'fallback': 464, 'lib': 0, 'net': 3676, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.150 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.050, latin-lower 0.035 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.308 | 24 | None | 0.250 | 52 / 16 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 32, refusals 8 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.510 | 69 | None | 0.500 | 104 / 53 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | 0.750 | 0.500 | None | None | 4 /  | NOT_GRADABLE_N_LT_13 |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 2.071, U1a_NAME:latin-lower 2.797, AFTER -8.333, BEFORE 0.000, BETWEEN -8.333, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 334.242 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:A1
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, CONST's too"}
cost: 498.912 ms per event over 10826 events · size {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1'}

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
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 498.912 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:A1-TEACH
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, CONST's too"}
cost: 328.335 ms per event over 10826 events · size {'h0': 112, 'h_alive': 112, 'hmax': 1024, 'n_names': 37, 'n_params_active': 144585, 'variant': 'A1'}

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
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 328.335 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:A5
failed ['U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, CONST's too", 'C0a_SAME': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, SAME's too"}
cost: 336.538 ms per event over 16301 events · size {'net': {'h0': 110, 'h_alive': 110, 'hmax': 1024, 'n_names': 37, 'n_params_active': 141127, 'variant': 'A1'}, 'routed': {'cells': 1659, 'fallback': 449, 'lib': 0, 'net': 3661, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.150 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.142, latin-lower 0.171 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.596 | 24 | None | 0.250 | 52 / 31 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 32, refusals 8 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.654 | 69 | None | 0.500 | 104 / 68 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.941 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.254, U1a_NAME:latin-lower 8.042, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 336.538 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:D
failed ['U2a_REFUSES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · not gradable ['C0a_CONST', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_SAME': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, SAME's too"}
cost: 218.822 ms per event over 9790 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NO_SLEEP_BEFORE_SITTING |
| C0a_SAME | yes | FAIL | 0.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | PASS | latin-upper 0.769, latin-lower 0.853 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.769 | 24 | None | 0.250 | 52 / 40 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | PASS | 0.933 | 69 | None | 0.500 | 104 / 97 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.375 | None | 0.500 | 0.500 | 16 / 6 | NO_BAR · latin-upper: 6/24; latin-lower: 13/24 |
| U3_LOOP@T_L | no | — | 0.429 | None | 0.500 | 0.500 | 14 / 6 | NO_BAR · latin-upper: 7/18; latin-lower: 11/24 |
| U3_VOWEL@T_L | no | — | 0.425 | None | 0.500 | 0.500 | 40 / 17 | NO_BAR · latin-upper: 9/20; latin-lower: 8/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | FAIL | 0.000 | 0.500 | None | None | 26 /  |  |
| U4b_EXPLAINS_RULE | yes | FAIL | AFTER 0, BEFORE 0, BETWEEN 0, TWO_AFTER 0, OTHER_CASE 0, CHAIN 0, MIRROR 6, LOOP 6, VOWEL 17 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | PASS | 0.600 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 1.479, U1a_NAME:latin-lower 4.196, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR -18.750, LOOP 0.000, VOWEL -7.500 | 5.000 | None | None |  |  |
| COST | yes | PASS | 218.822 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:E′
failed ['U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U4b_EXPLAINS_RULE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['C0a_CONST', 'U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_SAME': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, SAME's too"}
cost: 0.801 ms per event over 14199 events · size {'routed': {'cells': 2108, 'fallback': 0, 'lib': 3212, 'net': 0, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | no | — | 0.000 | 1.000 | None | None | 20 / 0 | NO_SLEEP_BEFORE_SITTING |
| C0a_SAME | yes | FAIL | 0.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.130, latin-lower 0.164 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 11, refusals 29 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.654 | 69 | None | 0.500 | 104 / 68 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.375 | None | 0.500 | 0.500 | 16 / 6 | NO_BAR · latin-upper: 6/24; latin-lower: 13/24 |
| U3_LOOP@T_L | no | — | 0.429 | None | 0.500 | 0.500 | 14 / 6 | NO_BAR · latin-upper: 7/18; latin-lower: 11/24 |
| U3_VOWEL@T_L | no | — | 0.425 | None | 0.500 | 0.500 | 40 / 17 | NO_BAR · latin-upper: 9/20; latin-lower: 8/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | yes | FAIL | AFTER 0, BEFORE 0, BETWEEN 0, TWO_AFTER 0, OTHER_CASE 0, CHAIN 0, MIRROR 6, LOOP 6, VOWEL 17 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 2.071, U1a_NAME:latin-lower 7.343, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR -18.750, LOOP 0.000, VOWEL -7.500 | 5.000 | None | None |  |  |
| COST | yes | PASS | 0.801 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:F
failed ['U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U4b_EXPLAINS_RULE', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
controls failed by construction, never voiding (R40): {'C0a_CONST': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, CONST's too", 'C0a_SAME': "§4 / R23: every relation FEEDBACK answer is rewritten per cue, SAME's too"}
cost: 28.815 ms per event over 21957 events · size {'net': {'h0': 110, 'h_alive': 110, 'hmax': 1024, 'n_names': 37, 'n_params_active': 141127, 'variant': 'A1'}, 'routed': {'cells': 1659, 'fallback': 449, 'lib': 0, 'net': 3661, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.150 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.142, latin-lower 0.171 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.596 | 24 | None | 0.250 | 52 / 31 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 32, refusals 8 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.654 | 69 | None | 0.500 | 104 / 68 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.083 | 8 | 0.755 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 9/24; latin-lower: 15/24 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 9/18; latin-lower: 12/24 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/20; latin-lower: 10/20 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.941 | 0.500 | None | None | 17 /  |  |
| U4b_EXPLAINS_RULE | yes | FAIL | AFTER 0, BEFORE 0, BETWEEN 0, TWO_AFTER 0, OTHER_CASE 0, CHAIN 0, MIRROR 6, LOOP 6, VOWEL 17 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.254, U1a_NAME:latin-lower 8.042, AFTER 8.333, BEFORE 0.000, BETWEEN 8.333, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 28.815 | 307.521 | None | None |  |  |

## The decisions (§6, §4.1, §4.2) — this seed's inputs; the rule needs BOTH seeds
- selection candidates (all bars this seed; VOID = a failed control, §5.5): {'A5': 'VOID', 'E′': 'VOID', 'F': 'VOID'} · void by {'A5': ['C0a_SAME'], 'E′': ['C0a_SAME'], 'F': ['C0a_SAME']}
- D1 (i) F − A5 on TWO_AFTER / CHAIN: not computable — VOID {'F': ['C0a_SAME'], 'A5': ['C0a_SAME']}
- D1 (iii) D − A1 (diagnostic): diff pp {'AFTER': 91.7, 'BEFORE': 66.7, 'BETWEEN': 83.3, 'TWO_AFTER': 95.2, 'OTHER_CASE': 100.0, 'CHAIN': 84.0, 'MIRROR': 6.2, 'LOOP': 7.1, 'VOWEL': 7.5} · inputs {'D': {'AFTER': 0.9166666666666666, 'BEFORE': 0.75, 'BETWEEN': 0.8333333333333334, 'TWO_AFTER': 0.9523809523809523, 'OTHER_CASE': 1.0, 'CHAIN': 0.84, 'MIRROR': 0.5625, 'LOOP': 0.5714285714285714, 'VOWEL': 0.575}, 'A1': {'AFTER': 0.0, 'BEFORE': 0.08333333333333333, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.5, 'LOOP': 0.5, 'VOWEL': 0.5}} · 
- GROWS A1 − A1-FIXED: diff pp {'AFTER': 0.0, 'BEFORE': 0.0, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.0, 'LOOP': 0.0, 'VOWEL': 0.0} · inputs {'A1': {'AFTER': 0.0, 'BEFORE': 0.08333333333333333, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.5, 'LOOP': 0.5, 'VOWEL': 0.5}, 'A1-FIXED': {'AFTER': 0.0, 'BEFORE': 0.08333333333333333, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.5, 'LOOP': 0.5, 'VOWEL': 0.5}} · growth bought nothing at letters
- D1 (ii) E′ vs F: not computable — VOID {'E′': ['C0a_SAME'], 'F': ['C0a_SAME']}
- Memory Attention: claim {'AFTER': 0.0, 'BEFORE': 0.0, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.0, 'LOOP': 0.0, 'VOWEL': 0.0} · isolation {'AFTER': 0.0, 'BEFORE': 0.0, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.0, 'LOOP': 0.0, 'VOWEL': 0.0} attention's, not the memory's
- interface: {'arms_present': [], 'void': {'A5': ['C0a_SAME']}}
- examples-to-bar (TWO_AFTER): {'A1-MLC': {'reading': '> 36', 'ladder': [{'probe': 'P1', 'episodes': 6, 'n': 21, 'known': 0}, {'probe': 'P2', 'episodes': 12, 'n': 21, 'known': 0}, {'probe': 'P3', 'episodes': 18, 'n': 21, 'known': 0}, {'probe': 'P4', 'episodes': 36, 'n': 21, 'known': 0}]}, 'D': {'reading': 6, 'ladder': [{'probe': 'P1', 'episodes': 6, 'n': 21, 'known': 19}, {'probe': 'P2', 'episodes': 12, 'n': 21, 'known': 20}, {'probe': 'P3', 'episodes': 18, 'n': 21, 'known': 19}, {'probe': 'P4', 'episodes': 36, 'n': 21, 'known': 19}]}, 'A1': {'reading': '> 36', 'ladder': [{'probe': 'P1', 'episodes': 6, 'n': 21, 'known': 0}, {'probe': 'P2', 'episodes': 12, 'n': 21, 'known': 0}, {'probe': 'P3', 'episodes': 18, 'n': 21, 'known': 0}, {'probe': 'P4', 'episodes': 36, 'n': 21, 'known': 0}]}}
- A1-TEACH (R46 — a diagnostic; decides nothing by itself): U1a {'A1-TEACH': {'latin-upper': 0.038461538461538464, 'latin-lower': 0.038461538461538464}, 'A1': {'latin-upper': 0.038461538461538464, 'latin-lower': 0.038461538461538464}, 'SHUFFLED-NAME:A1-TEACH': {'latin-upper': 0.0, 'latin-lower': 0.0}}

## Reading rules
- A mark NOT GRADED is never counted as failed; «no road» names a capability the arm does not have; INSTRUMENT-VOID (0c) names the instrument, never the arm; an arm VOID names a §5.5 control that arm failed — never «failed» (R40).
- REACH families are printed beside RING-READ (reach given the name); the U3 verdict rests on the discriminating families TWO_AFTER · OTHER_CASE · CHAIN.
