# B1 VERDICT — seed 20261001 (graded)

tape sha `ce0d65d92ed99e05…` · results b1-results-v1 · bars: §12 (the seat, 2026-09-26 12:08 +0400): bars from ceilings.json by ONE rule — AFTER k=8 of 12 (ceiling 0.886, k_min 4); BEFORE k=8 of 12 (ceiling 0.917, k_min 4); BETWEEN k=8 of 12 (ceiling 0.755, k_min 4); TWO_AFTER k=11 of 21 (ceiling 0.861, k_min 6); CHAIN k=11 of 25 (ceiling 0.873, k_min 6); TRANSFER k=13 of 18 (ceiling 0.869, k_min 8); NAME latin-upper 0.6692, latin-lower 0.7776; U1b 24/52 · U2b 69/104 · U6 4/10 · U4a 0.5 · U5 0.8 · KEEPS 5.0 pp · COST ≤ 307.521 ms per event (one world-day of alpha4-1's body, 93,652 rows, in 8 wall-hours on one thread; a tape event and a body row taken as one unit of work [Guessing]; the draft 3 × A0 = 4.785 ms is NOT used: A1-FIXED at H 64 reads 11.451 ms, so every network-bearing arm would fail it by construction (#228 b)); margins D1 10.0 pp · GROWS 5.0 pp · MA 3.0 pp at ≤ +10.0 % cost · interface 5.0 pp; NOT GRADABLE (organ limit): OTHER_CASE, MIRROR, LOOP, VOWEL

## The instrument (0c) — sound
- KEY: present; graded marks 19; failed []
- SHIFTED-KEY: present; failed 4 marks

## A0
failed ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 1.538 ms per event over 9755 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.098, latin-lower 0.126 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 9, refusals 31 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.635 | 69 | None | 0.500 | 104 / 66 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/27; latin-lower: 0/21 |
| U3_LOOP@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 14 / 0 | NO_BAR · latin-upper: 0/30; latin-lower: 0/12 |
| U3_VOWEL@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 40 / 0 | NO_BAR · latin-upper: 0/18; latin-lower: 0/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 15 /  |  |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 1.775, U1a_NAME:latin-lower 1.748, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.538 | 307.521 | None | None |  |  |

## A1
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 353.059 ms per event over 10826 events · size {'h0': 114, 'h_alive': 114, 'hmax': 1024, 'n_names': 37, 'n_params_active': 148075, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.135 | 24 | None | 0.250 | 52 / 7 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 353.059 | 307.521 | None | None |  |  |

## A1-ATT
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 37.762 ms per event over 10826 events · size {'h0': 92, 'h_alive': 92, 'hmax': 92, 'match': {'a1_final_names': 37, 'a1_final_params': 148075, 'solved_h': 92, 'twin_params_at_h_plus_1': 149378, 'twin_params_at_solved_h': 147477}, 'n_names': 37, 'n_params_active': 147477, 'variant': 'A1-ATT'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
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
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.122 | 0.800 | None | None | 49 / 6 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 37.762 | 307.521 | None | None |  |  |

## A1-BPTT-AWAKE
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 333.774 ms per event over 10826 events · size {'h0': 70, 'h_alive': 70, 'hmax': 1024, 'n_names': 37, 'n_params_active': 78687, 'variant': 'A1-BPTT-AWAKE'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.192 | 24 | None | 0.250 | 52 / 10 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 1/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 1/75; latin-lower->latin-upper: 3/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/27; latin-lower: 9/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 18/30; latin-lower: 3/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 8/18; latin-lower: 12/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 333.774 | 307.521 | None | None |  |  |

## A1-FIXED
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 29.237 ms per event over 10826 events · size {'h0': 114, 'h_alive': 114, 'hmax': 114, 'n_names': 37, 'n_params_active': 148075, 'variant': 'A1-FIXED'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.173 | 24 | None | 0.250 | 52 / 9 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 29.237 | 307.521 | None | None |  |  |

## A1-LOCAL
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 358.351 ms per event over 10826 events · size {'h0': 116, 'h_alive': 116, 'hmax': 1024, 'n_names': 37, 'n_params_active': 151597, 'variant': 'A1-LOCAL'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.192 | 24 | None | 0.250 | 52 / 10 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.056 | 13 | None | 0.111 | 18 / 1 |  · AFTER: 0/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 358.351 | 307.521 | None | None |  |  |

## A1-MA
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 34.738 ms per event over 10826 events · size {'h0': 93, 'h_alive': 93, 'hmax': 93, 'match': {'a1_final_names': 37, 'a1_final_params': 148075, 'solved_h': 93, 'twin_params_at_h_plus_1': 149367, 'twin_params_at_solved_h': 147522}, 'n_names': 37, 'n_params_active': 147522, 'variant': 'A1-MA'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.212 | 24 | None | 0.250 | 52 / 11 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 34.738 | 307.521 | None | None |  |  |

## A1-MLC
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 260.255 ms per event over 16334 events · size {'h0': 105, 'h_alive': 105, 'hmax': 1024, 'n_names': 37, 'n_params_active': 132622, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.173 | 24 | None | 0.250 | 52 / 9 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 260.255 | 307.521 | None | None |  |  |

## A1-NO-SLEEP
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 133.558 ms per event over 10826 events · size {'h0': 111, 'h_alive': 111, 'hmax': 1024, 'n_names': 37, 'n_params_active': 142852, 'variant': 'A1-NO-SLEEP'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.212 | 24 | None | 0.250 | 52 / 11 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 133.558 | 307.521 | None | None |  |  |

## A2
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 84.083 ms per event over 10826 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
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
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/27; latin-lower: 9/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 18/30; latin-lower: 3/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 8/18; latin-lower: 12/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 84.083 | 307.521 | None | None |  |  |

## A3
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 140.871 ms per event over 10826 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.000 | 24 | None | 0.250 | 52 / 0 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 33, refusals 7 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/27; latin-lower: 9/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 18/30; latin-lower: 3/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 8/18; latin-lower: 12/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.224 | 0.800 | None | None | 49 / 11 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 140.871 | 307.521 | None | None |  |  |

## A4
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 24.010 ms per event over 9755 events · size {'d_model': 96, 'ffn': 25, 'n_names': 37, 'n_params': 162726, 'n_params_numel': 162726, 'target': 148075, 'transcript_steps': 20397, 'within_10pct': True}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.365 | 24 | None | 0.250 | 52 / 19 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 1/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 2/75; latin-lower->latin-upper: 2/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 15/27; latin-lower: 9/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.183, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER -4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 24.010 | 307.521 | None | None |  |  |

## A5
failed ['C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 82.840 ms per event over 16335 events · size {'net': {'h0': 113, 'h_alive': 113, 'hmax': 1024, 'n_names': 37, 'n_params_active': 146326, 'variant': 'A1'}, 'routed': {'cells': 1611, 'fallback': 497, 'lib': 0, 'net': 3709, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.112, latin-lower 0.147 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.635 | 69 | None | 0.500 | 104 / 66 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.938 | 0.500 | None | None | 16 /  |  |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.254, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 82.840 | 307.521 | None | None |  |  |

## D
failed ['C0a_CONST', 'U2a_REFUSES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 6.902 ms per event over 9790 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | PASS | latin-upper 0.778, latin-lower 0.857 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.923 | 24 | None | 0.250 | 52 / 48 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | PASS | 0.837 | 69 | None | 0.500 | 104 / 87 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.800 | None | 0.861 | 0.038 | 5 / 4 | NO_BAR · latin-upper->latin-lower: 10/15; latin-lower->latin-upper: 9/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/27; latin-lower: 0/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 18/30; latin-lower: 3/12 |
| U3_VOWEL@T_L | no | — | 0.600 | None | 0.500 | 0.500 | 40 / 24 | NO_BAR · latin-upper: 10/18; latin-lower: 14/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | FAIL | 0.000 | 0.500 | None | None | 26 /  |  |
| U4b_EXPLAINS_RULE | yes | FAIL | AFTER 0, BEFORE 0, BETWEEN 0, TWO_AFTER 0, OTHER_CASE 4, CHAIN 0, MIRROR 0, LOOP 7, VOWEL 24 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.796 | 0.800 | None | None | 49 / 39 |  |
| U6_ONE_MEETING | yes | FAIL | 0.200 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.183, U1a_NAME:latin-lower 0.350, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 20.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 6.902 | 307.521 | None | None |  |  |

## E′
failed ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U4b_EXPLAINS_RULE', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 1.095 ms per event over 14199 events · size {'routed': {'cells': 2108, 'fallback': 0, 'lib': 3212, 'net': 0, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.150 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.098, latin-lower 0.126 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 9, refusals 31 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.635 | 69 | None | 0.500 | 104 / 66 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.800 | None | 0.861 | 0.038 | 5 / 4 | NO_BAR · latin-upper->latin-lower: 10/15; latin-lower->latin-upper: 9/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/27; latin-lower: 0/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 18/30; latin-lower: 3/12 |
| U3_VOWEL@T_L | no | — | 0.600 | None | 0.500 | 0.500 | 40 / 24 | NO_BAR · latin-upper: 10/18; latin-lower: 14/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 15 /  |  |
| U4b_EXPLAINS_RULE | yes | FAIL | AFTER 0, BEFORE 0, BETWEEN 0, TWO_AFTER 0, OTHER_CASE 4, CHAIN 0, MIRROR 0, LOOP 7, VOWEL 24 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.796 | 0.800 | None | None | 49 / 39 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.775, U1a_NAME:latin-lower 1.748, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 20.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.095 | 307.521 | None | None |  |  |

## F
failed ['C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U4b_EXPLAINS_RULE', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 60.871 ms per event over 21991 events · size {'net': {'h0': 113, 'h_alive': 113, 'hmax': 1024, 'n_names': 37, 'n_params_active': 146326, 'variant': 'A1'}, 'routed': {'cells': 1611, 'fallback': 497, 'lib': 105, 'net': 3604, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | FAIL | 0.200 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.112, latin-lower 0.147 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.635 | 69 | None | 0.500 | 104 / 66 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.938 | 0.500 | None | None | 16 /  |  |
| U4b_EXPLAINS_RULE | yes | FAIL | AFTER 0, BEFORE 0, BETWEEN 0, TWO_AFTER 0, OTHER_CASE 4, CHAIN 0, MIRROR 0, LOOP 7, VOWEL 24 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.254, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 60.871 | 307.521 | None | None |  |  |

## FORCED:A0
failed ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 1.538 ms per event over 9755 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.098, latin-lower 0.126 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 14, refusals 26 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.635 | 69 | None | 0.500 | 104 / 66 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/27; latin-lower: 0/21 |
| U3_LOOP@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 14 / 0 | NO_BAR · latin-upper: 0/30; latin-lower: 0/12 |
| U3_VOWEL@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 40 / 0 | NO_BAR · latin-upper: 0/18; latin-lower: 0/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 15 /  |  |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 1.775, U1a_NAME:latin-lower 1.748, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.538 | 307.521 | None | None |  |  |

## FORCED:A1
failed ['U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 501.488 ms per event over 10826 events · size {'h0': 114, 'h_alive': 114, 'hmax': 1024, 'n_names': 37, 'n_params_active': 148075, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.135 | 24 | None | 0.250 | 52 / 7 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 1/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 3/75; latin-lower->latin-upper: 4/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.056 | 13 | None | 0.111 | 18 / 1 |  · AFTER: 0/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 501.488 | 307.521 | None | None |  |  |

## FORCED:A5
failed ['C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 336.916 ms per event over 16335 events · size {'net': {'h0': 113, 'h_alive': 113, 'hmax': 1024, 'n_names': 37, 'n_params_active': 146326, 'variant': 'A1'}, 'routed': {'cells': 1611, 'fallback': 497, 'lib': 0, 'net': 3709, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | PASS | 1.000 | 1.000 | None | None | 20 / 20 |  |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.112, latin-lower 0.147 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.635 | 69 | None | 0.500 | 104 / 66 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.083 | 8 | 0.917 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 1/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 3/75; latin-lower->latin-upper: 3/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.056 | 13 | None | 0.111 | 18 / 1 |  · AFTER: 0/27; BEFORE: 3/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.938 | 0.500 | None | None | 16 /  |  |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.000 | 0.800 | None | None | 49 / 0 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.254, U1a_NAME:latin-lower 3.846, AFTER 0.000, BEFORE 8.333, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 336.916 | 307.521 | None | None |  |  |

## KEY
failed ['C0d_CANARY'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
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
| U3_MIRROR@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 16 / 16 | NO_BAR · latin-upper: 27/27; latin-lower: 21/21 |
| U3_LOOP@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 14 / 14 | NO_BAR · latin-upper: 30/30; latin-lower: 12/12 |
| U3_VOWEL@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 40 / 40 | NO_BAR · latin-upper: 18/18; latin-lower: 22/22 |
| U3_TRANSFER@T_D | yes | PASS | 1.000 | 13 | None | 0.111 | 18 / 18 |  · AFTER: 27/27; BEFORE: 27/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | PASS | 1.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 0.000 | 307.521 | None | None |  |  |

## RING-READ
failed ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U6_ONE_MEETING'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 0.000 ms per event over 9755 events · size {}

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
| U2a_REFUSES@T_L | yes | FAIL | sure_names 0, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.000 | 69 | None | 0.500 | 104 / 0 |  |
| U3_AFTER@T_L | yes | PASS | 1.000 | 8 | 0.886 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 36/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | PASS | 1.000 | 8 | 0.917 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 36/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | PASS | 1.000 | 8 | 0.755 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 36/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/27; latin-lower: 0/21 |
| U3_LOOP@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 14 / 0 | NO_BAR · latin-upper: 0/30; latin-lower: 0/12 |
| U3_VOWEL@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 40 / 0 | NO_BAR · latin-upper: 0/18; latin-lower: 0/22 |
| U3_TRANSFER@T_D | yes | PASS | 1.000 | 13 | None | 0.111 | 18 / 18 |  · AFTER: 27/27; BEFORE: 27/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 0.000 | 307.521 | None | None |  |  |

## SHIFTED-KEY
failed ['C0a_CONST', 'C0a_SAME', 'U1b_PICK@T_L', 'U2b_LURES@T_L'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 0.000 ms per event over 9755 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.950 | 1.000 | None | None | 20 / 19 |  |
| C0a_SAME | yes | FAIL | 0.050 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.100 | <= 4 of 20 | None | 0.037 | 20 / 2 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | PASS | latin-upper 0.923, latin-lower 0.909 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.192 | 24 | None | 0.250 | 52 / 10 |  |
| U2a_REFUSES@T_L | yes | PASS | sure_names 1, refusals 39 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.000 | 69 | None | 0.500 | 104 / 0 |  |
| U3_AFTER@T_L | yes | PASS | 1.000 | 8 | 0.886 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 24/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | PASS | 1.000 | 8 | 0.917 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 24/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | PASS | 1.000 | 8 | 0.755 | 0.040 | 12 / 12 |  · latin-upper: 36/36; latin-lower: 24/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | PASS | 1.000 | 11 | 0.861 | 0.040 | 21 / 21 |  · latin-upper: 63/63; latin-lower: 42/63 |
| U3_OTHER_CASE@T_L | no | — | 1.000 | None | 0.861 | 0.038 | 5 / 5 | NO_BAR · latin-upper->latin-lower: 15/15; latin-lower->latin-upper: 10/15 |
| U3_CHAIN@T_L | yes | PASS | 1.000 | 11 | 0.873 | 0.038 | 25 / 25 |  · latin-upper->latin-lower: 75/75; latin-lower->latin-upper: 50/75 |
| U3_MIRROR@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 16 / 16 | NO_BAR · latin-upper: 27/27; latin-lower: 19/21 |
| U3_LOOP@T_L | no | — | 1.000 | None | 0.500 | 0.500 | 14 / 14 | NO_BAR · latin-upper: 30/30; latin-lower: 10/12 |
| U3_VOWEL@T_L | no | — | 0.950 | None | 0.500 | 0.500 | 40 / 38 | NO_BAR · latin-upper: 18/18; latin-lower: 20/22 |
| U3_TRANSFER@T_D | yes | PASS | 1.000 | 13 | None | 0.111 | 18 / 18 |  · AFTER: 18/27; BEFORE: 18/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | 6 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 0.980 | 0.800 | None | None | 49 / 48 |  |
| U6_ONE_MEETING | yes | PASS | 0.900 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL -2.500 | 5.000 | None | None |  |  |
| COST | yes | PASS | 0.000 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A0
failed ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U6_ONE_MEETING'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 1.499 ms per event over 9755 events · size {}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.000, latin-lower 0.000 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.135 | 24 | None | 0.250 | 52 / 7 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 9, refusals 31 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.490 | 69 | None | 0.500 | 104 / 51 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/27; latin-lower: 0/21 |
| U3_LOOP@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 14 / 0 | NO_BAR · latin-upper: 0/30; latin-lower: 0/12 |
| U3_VOWEL@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 40 / 0 | NO_BAR · latin-upper: 0/18; latin-lower: 0/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_WHY_FILE |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | PASS | 1.000 | 0.800 | None | None | 49 / 49 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | PASS | U1a_NAME:latin-upper 0.000, U1a_NAME:latin-lower 0.000, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 1.499 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A1
failed ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 505.355 ms per event over 10826 events · size {'h0': 90, 'h_alive': 90, 'hmax': 1024, 'n_names': 37, 'n_params_active': 108307, 'variant': 'A1'}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | PASS | 1.000 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.038, latin-lower 0.038 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.192 | 24 | None | 0.250 | 52 / 10 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 40, refusals 0 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.500 | 69 | None | 0.500 | 104 / 52 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 505.355 | 307.521 | None | None |  |  |

## SHUFFLED-NAME:A5
failed ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 340.301 ms per event over 16351 events · size {'net': {'h0': 90, 'h_alive': 90, 'hmax': 1024, 'n_names': 37, 'n_params_active': 108307, 'variant': 'A1'}, 'routed': {'cells': 1595, 'fallback': 513, 'lib': 0, 'net': 3725, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.015, latin-lower 0.010 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | FAIL | 0.192 | 24 | None | 0.250 | 52 / 10 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.490 | 69 | None | 0.500 | 104 / 51 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | 0.000 | 0.500 | None | None | 1 /  | NOT_GRADABLE_N_LT_13 |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.479, U1a_NAME:latin-lower 1.049, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 340.301 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:A1
failed ['C0a_CONST', 'U1a_NAME@T_L', 'U1b_PICK@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4a_EXPLAINS_EXPERIENCE', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 489.139 ms per event over 10826 events · size {'h0': 112, 'h_alive': 112, 'hmax': 1024, 'n_names': 37, 'n_params_active': 144585, 'variant': 'A1'}

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
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | no | — | None | 0.500 | None | None |  | NO_ROAD |
| U4b_EXPLAINS_RULE | no | — | None | None | None | None |  | NO_ROAD |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.846, U1a_NAME:latin-lower 3.846, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 489.139 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:A5
failed ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS', 'COST'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER', 'U4b_EXPLAINS_RULE'] · missing-graded none
cost: 331.763 ms per event over 16335 events · size {'net': {'h0': 114, 'h_alive': 114, 'hmax': 1024, 'n_names': 37, 'n_params_active': 148075, 'variant': 'A1'}, 'routed': {'cells': 1611, 'fallback': 497, 'lib': 0, 'net': 3709, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.300 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.115, latin-lower 0.133 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.635 | 69 | None | 0.500 | 104 / 66 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.933 | 0.500 | None | None | 15 /  |  |
| U4b_EXPLAINS_RULE | no | — | AFTER None, BEFORE None, BETWEEN None, TWO_AFTER None, OTHER_CASE None, CHAIN None, MIRROR None, LOOP None, VOWEL None | None | None | None |  | NO_BAR |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.550, U1a_NAME:latin-lower 2.448, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | FAIL | 331.763 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:E′
failed ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U4b_EXPLAINS_RULE', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 5.371 ms per event over 14199 events · size {'routed': {'cells': 2108, 'fallback': 0, 'lib': 3212, 'net': 0, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.150 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.098, latin-lower 0.126 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 9, refusals 31 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.635 | 69 | None | 0.500 | 104 / 66 |  |
| U3_AFTER@T_L | yes | FAIL | 0.000 | 8 | 0.886 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.000 | 11 | 0.861 | 0.040 | 21 / 0 |  · latin-upper: 0/63; latin-lower: 0/63 |
| U3_OTHER_CASE@T_L | no | — | 0.800 | None | 0.861 | 0.038 | 5 / 4 | NO_BAR · latin-upper->latin-lower: 10/15; latin-lower->latin-upper: 9/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.000 | None | 0.500 | 0.500 | 16 / 0 | NO_BAR · latin-upper: 0/27; latin-lower: 0/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 18/30; latin-lower: 3/12 |
| U3_VOWEL@T_L | no | — | 0.600 | None | 0.500 | 0.500 | 40 / 24 | NO_BAR · latin-upper: 10/18; latin-lower: 14/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 1.000 | 0.500 | None | None | 15 /  |  |
| U4b_EXPLAINS_RULE | yes | FAIL | AFTER 0, BEFORE 0, BETWEEN 0, TWO_AFTER 0, OTHER_CASE 4, CHAIN 0, MIRROR 0, LOOP 7, VOWEL 24 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.796 | 0.800 | None | None | 49 / 39 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 1.775, U1a_NAME:latin-lower 1.748, AFTER 0.000, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 0.000, OTHER_CASE 20.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 5.371 | 307.521 | None | None |  |  |

## SHUFFLED-RELATION:F
failed ['C0a_CONST', 'C0a_SAME', 'U1a_NAME@T_L', 'U2a_REFUSES@T_L', 'U2b_LURES@T_L', 'U3_AFTER@T_L', 'U3_BEFORE@T_L', 'U3_BETWEEN@T_L', 'U3_TWO_AFTER@T_L', 'U3_CHAIN@T_L', 'U3_TRANSFER@T_D', 'U4b_EXPLAINS_RULE', 'U5_REJECTS_MISUSE', 'U6_ONE_MEETING', 'KEEPS'] · not gradable ['U3_OTHER_CASE@T_L', 'U3_MIRROR@T_L', 'U3_LOOP@T_L', 'U3_VOWEL@T_L', 'EXAMPLES_TO_BAR_TWO_AFTER'] · missing-graded none
cost: 250.512 ms per event over 21991 events · size {'net': {'h0': 114, 'h_alive': 114, 'hmax': 1024, 'n_names': 37, 'n_params_active': 148075, 'variant': 'A1'}, 'routed': {'cells': 1611, 'fallback': 497, 'lib': 105, 'net': 3604, 'no_road': 0, 'partner': 0}}

| mark | graded | pass | reading | bar | ceiling | null | n / k | note |
|---|---|---|---|---|---|---|---|---|
| C0a_CONST | yes | FAIL | 0.000 | 1.000 | None | None | 20 / 0 |  |
| C0a_SAME | yes | FAIL | 0.150 | 0.950 | None | None | 20 /  |  |
| C0d_CANARY | yes | PASS | 0.000 | <= 4 of 20 | None | 0.037 | 20 / 0 |  |
| C0e_FROZEN | yes | PASS | True | state_sha before = after every sitting | None | None |  |  |
| C0f_DISJOINT | yes | PASS | True | None | None | None |  |  |
| C0g_MLC_LEAK | yes | PASS | True | None | None | None |  |  |
| U1a_NAME@T_L | yes | FAIL | latin-upper 0.115, latin-lower 0.133 | latin-lower 0.778, latin-upper 0.669 | latin-upper 0.769, latin-lower 0.878 | 0.000 |  |  |
| U1b_PICK@T_L | yes | PASS | 0.558 | 24 | None | 0.250 | 52 / 29 |  |
| U2a_REFUSES@T_L | yes | FAIL | sure_names 34, refusals 6 | max_sure_names 4, min_refusals 32 | None | None | 40 /  |  |
| U2b_LURES@T_L | yes | FAIL | 0.635 | 69 | None | 0.500 | 104 / 66 |  |
| U3_AFTER@T_L | yes | FAIL | 0.083 | 8 | 0.886 | 0.040 | 12 / 1 |  · latin-upper: 3/36; latin-lower: 3/36 · REACH (read beside RING-READ) |
| U3_BEFORE@T_L | yes | FAIL | 0.000 | 8 | 0.917 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_BETWEEN@T_L | yes | FAIL | 0.000 | 8 | 0.755 | 0.040 | 12 / 0 |  · latin-upper: 0/36; latin-lower: 0/36 · REACH (read beside RING-READ) |
| U3_TWO_AFTER@T_L | yes | FAIL | 0.048 | 11 | 0.861 | 0.040 | 21 / 1 |  · latin-upper: 3/63; latin-lower: 3/63 |
| U3_OTHER_CASE@T_L | no | — | 0.000 | None | 0.861 | 0.038 | 5 / 0 | NO_BAR · latin-upper->latin-lower: 0/15; latin-lower->latin-upper: 0/15 |
| U3_CHAIN@T_L | yes | FAIL | 0.000 | 11 | 0.873 | 0.038 | 25 / 0 |  · latin-upper->latin-lower: 0/75; latin-lower->latin-upper: 0/75 |
| U3_MIRROR@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 16 / 8 | NO_BAR · latin-upper: 12/27; latin-lower: 12/21 |
| U3_LOOP@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 14 / 7 | NO_BAR · latin-upper: 12/30; latin-lower: 9/12 |
| U3_VOWEL@T_L | no | — | 0.500 | None | 0.500 | 0.500 | 40 / 20 | NO_BAR · latin-upper: 10/18; latin-lower: 10/22 |
| U3_TRANSFER@T_D | yes | FAIL | 0.000 | 13 | None | 0.111 | 18 / 0 |  · AFTER: 0/27; BEFORE: 0/27 |
| EXAMPLES_TO_BAR_TWO_AFTER | no | — | > 36 | 11 | None | None |  | DIAGNOSTIC |
| U4a_EXPLAINS_EXPERIENCE | yes | PASS | 0.933 | 0.500 | None | None | 15 /  |  |
| U4b_EXPLAINS_RULE | yes | FAIL | AFTER 0, BEFORE 0, BETWEEN 0, TWO_AFTER 0, OTHER_CASE 4, CHAIN 0, MIRROR 0, LOOP 7, VOWEL 24 | AFTER 8, BEFORE 8, BETWEEN 8, CHAIN 11, TWO_AFTER 11 | None | None |  |  |
| U5_REJECTS_MISUSE | yes | FAIL | 0.204 | 0.800 | None | None | 49 / 10 |  |
| U6_ONE_MEETING | yes | FAIL | 0.000 | 4 | None | 0.037 | 10 /  |  |
| KEEPS | yes | FAIL | U1a_NAME:latin-upper 3.550, U1a_NAME:latin-lower 2.448, AFTER 8.333, BEFORE 0.000, BETWEEN 0.000, TWO_AFTER 4.762, OTHER_CASE 0.000, CHAIN 0.000, MIRROR 0.000, LOOP 0.000, VOWEL 0.000 | 5.000 | None | None |  |  |
| COST | yes | PASS | 250.512 | 307.521 | None | None |  |  |

## The decisions (§6, §4.1, §4.2) — this seed's inputs; the rule needs BOTH seeds
- selection candidates (all bars this seed): {'A5': False, 'E′': False, 'F': False}
- D1 (i) F − A5 on TWO_AFTER / CHAIN: diff pp {'TWO_AFTER': 0.0, 'CHAIN': 0.0} · inputs {'F': {'TWO_AFTER': 0.0, 'CHAIN': 0.0}, 'A5': {'TWO_AFTER': 0.0, 'CHAIN': 0.0}} · OPEN
- D1 (iii) D − A1 (diagnostic): diff pp {'AFTER': 0.0, 'BEFORE': -8.3, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 80.0, 'CHAIN': 0.0, 'MIRROR': -50.0, 'LOOP': 0.0, 'VOWEL': 10.0} · inputs {'D': {'AFTER': 0.0, 'BEFORE': 0.0, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.8, 'CHAIN': 0.0, 'MIRROR': 0.0, 'LOOP': 0.5, 'VOWEL': 0.6}, 'A1': {'AFTER': 0.0, 'BEFORE': 0.08333333333333333, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.5, 'LOOP': 0.5, 'VOWEL': 0.5}} · 
- GROWS A1 − A1-FIXED: diff pp {'AFTER': 0.0, 'BEFORE': 0.0, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.0, 'LOOP': 0.0, 'VOWEL': 0.0} · inputs {'A1': {'AFTER': 0.0, 'BEFORE': 0.08333333333333333, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.5, 'LOOP': 0.5, 'VOWEL': 0.5}, 'A1-FIXED': {'AFTER': 0.0, 'BEFORE': 0.08333333333333333, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.5, 'LOOP': 0.5, 'VOWEL': 0.5}} · growth bought nothing at letters
- D1 (ii) E′ vs F: E′ below F on ['C0a_CONST', 'C0a_SAME', 'U3_BEFORE@T_L', 'COST'] → network stays
- Memory Attention: claim {'AFTER': 0.0, 'BEFORE': 0.0, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.0, 'LOOP': 0.0, 'VOWEL': 0.0} · isolation {'AFTER': 0.0, 'BEFORE': 0.0, 'BETWEEN': 0.0, 'TWO_AFTER': 0.0, 'OTHER_CASE': 0.0, 'CHAIN': 0.0, 'MIRROR': 0.0, 'LOOP': 0.0, 'VOWEL': 0.0} attention's, not the memory's
- interface: {'arms_present': ['A5']}
- examples-to-bar (TWO_AFTER): {'A1-MLC': {'reading': '> 36', 'ladder': [{'probe': 'P1', 'episodes': 6, 'n': 21, 'known': 0}, {'probe': 'P2', 'episodes': 12, 'n': 21, 'known': 0}, {'probe': 'P3', 'episodes': 18, 'n': 21, 'known': 0}, {'probe': 'P4', 'episodes': 36, 'n': 21, 'known': 0}]}, 'D': {'reading': '> 36', 'ladder': [{'probe': 'P1', 'episodes': 6, 'n': 21, 'known': 0}, {'probe': 'P2', 'episodes': 12, 'n': 21, 'known': 0}, {'probe': 'P3', 'episodes': 18, 'n': 21, 'known': 0}, {'probe': 'P4', 'episodes': 36, 'n': 21, 'known': 0}]}, 'A1': {'reading': '> 36', 'ladder': [{'probe': 'P1', 'episodes': 6, 'n': 21, 'known': 0}, {'probe': 'P2', 'episodes': 12, 'n': 21, 'known': 0}, {'probe': 'P3', 'episodes': 18, 'n': 21, 'known': 0}, {'probe': 'P4', 'episodes': 36, 'n': 21, 'known': 0}]}}

## Reading rules
- A mark NOT GRADED is never counted as failed; «no road» names a capability the arm does not have; VOID names the instrument, never the arm.
- REACH families are printed beside RING-READ (reach given the name); the U3 verdict rests on the discriminating families TWO_AFTER · OTHER_CASE · CHAIN.
