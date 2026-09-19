# G0 rung 0 — VERDICT: **FAIL** (failed: iv_grows_alone, vi_knows_unknown; SCALE untested)

run `20260919-161632` · genome `runs/g0-20260919-161632/G0.genome` · PREREG docs/G0-PREREG.md §1–§11 · every number below is read from results.json

## The nine marks, bars as written before the run (§5), predictions of §7 beside each

| mark | bar | read | pass | §7 predicted |
|---|---|---|---|---|
| (i) it answers | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.990 · Q2 1.00 · Q3 0.990 (ceiling 0.995) · Q4 0.990 | True | likely PASS |
| (ii) the meeting is real | T-shuffle, T-nowire Q1 ≤ .20 | T-shuffle Q1 band [0.075, 0.01, 0.13] · T-nowire Q1 0.000 (abstain {'novel': 1, 'noedge': 199, 'ratio': 0}) | True | PASS |
| (iii) growth matters | T-frozen ≥ 30 pp under (i) | T-frozen Q1 0.245 vs design 0.990 | True | PASS |
| (iv) it grows on its own | ≥ 50 born · 0 refused · 5-thing < 10-thing · ≥ 5 % pruned · 0 by disuse | born 96 · refused 0 · 5-thing 29 vs 10-thing 50 at 600 · pruned 1/80 = 1.2 % · disuse 0 | False | births 100–300; pruning may FAIL the 5 % bar |
| (v) it keeps what it learned | within 5 pp after arrival 2 | Q1 first-10 at 600 0.990 → at 900 0.990 (+0.0 pp) | True | PASS |
| (vi) it knows what it does not know | plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20 | plant zog answered 0.50 (as {'zog': 10}) · null vex abstains 1.00 · Q5 spiral abstains 0.80 (by {'novel': 16, 'noedge': 0, 'ratio': 0}; answered as {'circle': 4}) · false abstention on seen 0.010 (by {'novel': 1, 'noedge': 1, 'ratio': 0}) | False | the uncertain one |
| (vii) replay | two lives byte-identical | True (sha256 f20232c6e0022871…) | True | PASS by construction |
| (viii) cost | ≤ 300 s, one process | 1.69 s | True | — |
| (ix) not luck | top quartile of 20 random genomes | design composite 0.992 ranks 1 of 21 (best random 0.986) | True | unknown |
| SCALE | — | 0 events | UNTESTED | — |

## The design life, every number

- Gate G-a wrote THETA_N = 0.951, THETA_M = 0.9967; retina `thresh0.25 centre blur0.8 pool3 hog8 hogcells8x6 unit` (126 numbers); §2's strict rule NOT MET, §11's amended rule met (see the genome file's last line).
- Toy (circle, bar; 2 × 150 moments): Q1 1.000 → PASS.
- At 600: cells 50 sight + 10 words; Q1 0.990 Q2 1.00 Q3 0.990 Q4 0.990; abstain by {'novel': 1, 'noedge': 1, 'ratio': 0}.
- At 900 (after arrival 2): cells 81 + 15 (born novelty 81/15, error 0/0 — the error road FIRED 22 times and every birth was refused as redundant (§11 am. 4); refused by budget 0, by arrival [0, 0, 0]); edges alive 79, born 80, pruned 1; merged cells 0/0; removed for disuse 0.
- Q1 per thing at 900: {"circle": 1.0, "square": 1.0, "triangle": 0.9, "cross": 1.0, "ring": 1.0, "bar": 1.0, "dot": 1.0, "star": 1.0, "arrow": 1.0, "wave": 1.0}; arrival-2 things Q1 0.930 per thing {"moon": 1.0, "house": 0.95, "tree": 0.85, "cup": 0.9, "key": 0.95}.
- Q2 detail (word → the thing of the cell it lit): {"circle": "circle", "square": "square", "triangle": "triangle", "cross": "cross", "ring": "ring", "bar": "bar", "dot": "dot", "star": "star", "arrow": "arrow", "wave": "wave"}.
- Cells per thing (alive, single-thing): {"circle": 2, "square": 4, "triangle": 10, "cross": 7, "ring": 3, "bar": 4, "dot": 2, "star": 2, "arrow": 6, "wave": 10, "moon": 2, "house": 7, "tree": 9, "cup": 8, "key": 5}; multi-thing sight cells 0; answers from multi-word cells 0.
- After the plant (905): Q1 on the first ten 0.990; ledger-corruption plant: hash unchanged True.
- Time: design life 1.69 s; replay identical True.

## Twins (§4) — each blind to one thing

- **T-shuffle-5**: Q1 0.075 (abstain {'novel': 1, 'noedge': 1, 'ratio': 58}) · Q2 0.00 · Q3 0.505 · Q4 0.385 · cells 103+15 (error births 35/0, redundant refused 59) · edges alive 422 born 470 pruned 37 (7.9 %) · merged 11/0 · refused budget 0 frozen 0 · 1.41 s
- **T-shuffle-6**: Q1 0.010 (abstain {'novel': 1, 'noedge': 1, 'ratio': 76}) · Q2 0.20 · Q3 0.475 · Q4 0.285 · cells 111+15 (error births 39/0, redundant refused 61) · edges alive 432 born 477 pruned 36 (7.5 %) · merged 8/0 · refused budget 0 frozen 0 · 1.43 s
- **T-shuffle-7**: Q1 0.130 (abstain {'novel': 1, 'noedge': 1, 'ratio': 54}) · Q2 0.00 · Q3 0.535 · Q4 0.405 · cells 98+15 (error births 29/0, redundant refused 64) · edges alive 395 born 440 pruned 35 (8.0 %) · merged 10/0 · refused budget 0 frozen 0 · 1.4 s
- **T-frozen**: Q1 0.245 (abstain {'novel': 151, 'noedge': 0, 'ratio': 0}) · Q2 0.50 · Q3 0.620 · Q4 0.245 · cells 5+5 (error births 0/0, redundant refused 0) · edges alive 5 born 5 pruned 0 (0.0 %) · merged 0/0 · refused budget 0 frozen 1347 · 0.96 s
- **T-nowire**: Q1 0.000 (abstain {'novel': 1, 'noedge': 199, 'ratio': 0}) · Q2 0.00 · Q3 0.500 · Q4 0.000 · cells 81+15 (error births 0/0, redundant refused 0) · edges alive 0 born 0 pruned 0 (0.0 %) · merged 0/0 · refused budget 0 frozen 0 · 1.17 s
- **five-thing life** (600 moments, 120/thing): cells born 29 vs the ten-thing life's 50 at 600; Q1 1.000.

## Twenty random genomes (§4, E29's control) — composite = mean(Q1..Q4) at 900

| seed | composite | Q1 | Q2 | Q3 | Q4 | theta_n | misfires | budget | kwta | lr | prune | theta_m | stage1 | abstain | cells | refused |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 0.986 | 0.980 | 1.00 | 0.985 | 0.980 | 0.940 | 6 | 484 | 10 | 0.071 | 0.061 | 0.986 | 378 | 0.90 | 73 | 0 |
| 13 | 0.981 | 0.965 | 1.00 | 0.975 | 0.985 | 0.919 | 7 | 102 | 10 | 0.082 | 0.016 | 0.994 | 359 | 0.50 | 55 | 0 |
| 19 | 0.975 | 0.965 | 1.00 | 0.970 | 0.965 | 0.954 | 4 | 334 | 4 | 0.023 | 0.063 | 0.971 | 236 | 0.76 | 83 | 0 |
| 5 | 0.959 | 0.900 | 1.00 | 0.945 | 0.990 | 0.896 | 7 | 402 | 7 | 0.089 | 0.012 | 0.938 | 268 | 0.52 | 43 | 0 |
| 1 | 0.858 | 0.785 | 1.00 | 0.860 | 0.785 | 0.966 | 5 | 76 | 2 | 0.285 | 0.063 | 0.942 | 189 | 0.70 | 69 | 58 |
| 12 | 0.834 | 0.745 | 1.00 | 0.845 | 0.745 | 0.964 | 3 | 98 | 3 | 0.058 | 0.071 | 0.923 | 245 | 0.56 | 61 | 34 |
| 11 | 0.730 | 0.490 | 0.70 | 0.730 | 1.000 | 0.745 | 2 | 493 | 8 | 0.013 | 0.030 | 0.992 | 53 | 0.56 | 168 | 0 |
| 8 | 0.666 | 0.465 | 1.00 | 0.735 | 0.465 | 0.984 | 3 | 182 | 4 | 0.238 | 0.174 | 0.939 | 288 | 0.68 | 185 | 19 |
| 4 | 0.557 | 0.105 | 0.70 | 0.550 | 0.875 | 0.751 | 8 | 756 | 12 | 0.029 | 0.122 | 0.937 | 291 | 0.59 | 20 | 0 |
| 2 | 0.376 | 0.000 | 0.20 | 0.500 | 0.805 | 0.646 | 3 | 360 | 10 | 0.032 | 0.120 | 0.972 | 335 | 0.53 | 78 | 0 |
| 15 | 0.371 | 0.235 | 0.40 | 0.615 | 0.235 | 0.900 | 6 | 231 | 5 | 0.018 | 0.115 | 0.914 | 373 | 0.67 | 44 | 0 |
| 18 | 0.346 | 0.235 | 0.30 | 0.625 | 0.225 | 0.852 | 4 | 702 | 4 | 0.029 | 0.194 | 0.956 | 358 | 0.78 | 29 | 0 |
| 20 | 0.318 | 0.150 | 0.20 | 0.565 | 0.355 | 0.726 | 3 | 722 | 2 | 0.159 | 0.082 | 0.907 | 357 | 0.98 | 16 | 0 |
| 16 | 0.277 | 0.050 | 0.30 | 0.515 | 0.245 | 0.711 | 5 | 625 | 2 | 0.108 | 0.125 | 0.902 | 215 | 0.92 | 15 | 0 |
| 3 | 0.227 | 0.000 | 0.10 | 0.495 | 0.315 | 0.616 | 1 | 186 | 10 | 0.177 | 0.020 | 0.943 | 325 | 0.58 | 48 | 674 |
| 10 | 0.168 | 0.100 | 0.00 | 0.530 | 0.040 | 0.602 | 8 | 645 | 10 | 0.049 | 0.103 | 0.913 | 311 | 0.91 | 6 | 0 |
| 17 | 0.161 | 0.100 | 0.00 | 0.520 | 0.025 | 0.579 | 7 | 393 | 7 | 0.114 | 0.044 | 0.938 | 297 | 0.80 | 5 | 0 |
| 6 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.668 | 5 | 760 | 5 | 0.115 | 0.198 | 0.963 | 178 | 0.66 | 11 | 0 |
| 9 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.641 | 7 | 135 | 8 | 0.234 | 0.143 | 0.991 | 169 | 0.95 | 8 | 0 |
| 14 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.677 | 7 | 116 | 9 | 0.259 | 0.129 | 0.954 | 60 | 0.85 | 11 | 0 |

The design genome's composite 0.992 ranks 1 of 21; the best random genome is seed 7 at 0.986.

## What did nothing in the design life, and why

- Four genes had no measurable work: error births 0 (the road fired 22 times, every birth refused as redundant), merges 0 (THETA_M 0.9967 was never met between two winners with the same answer), pruned 1 of 80 edges, scale 0. This follows from THETA_N (0.951) sitting ABOVE the between-thing maximum (gate G-a, §11 amendment 2): no cross-thing edge is ever born, so nothing is wrong, redundant or weak. In T-shuffle-5, where the pairings are random, 470 edges were born and 37 pruned (7.9 %) — that number says whether the PRUNE gene works at all when there is something to prune.
- The same threshold surfaced twice more. The plant: «zog» shown 5 times birthed 4 cells, and 10 of 20 held-out zog renderings resonated with none of them (at THETA_N = the within-thing MEDIAN, half of same-thing renderings do not resonate with a given cell) — the plant reads 0.50 against a majority bar. Q5: the spiral abstains at exactly 0.80, its bar, with 4 of 20 read as «circle»; the spiral was never in gate G-a's ten-thing measurement, so the threshold carries no guarantee for a never-shown thing — one more answered spiral fails (vi) a second way.

## What this verdict does and does not say

- The truth never entered the organism: `genome/machinery.py` imports neither `world` nor `questions` and carries no label field; the ledger is the runner's, built from the stream (clause 12; the hash check proves only that the runner did not touch the organism).
- SCALE is untested here (0 events in 905 moments). §2's strict gate rule was not met by any fixed front; §11's amended rule was, at the price of several cells per thing — the cells-per-thing line above is that price, measured.
- No sentences, no reasoning, no reward, no sleep, no evolution (§6). Rung 1 is his pictures through the folder door; rung 2 a lineage, only after rung 1.
