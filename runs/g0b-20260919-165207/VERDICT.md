# G0b rung 0 — VERDICT: **FAIL** (failed: iv_grows_alone; SCALE untested)

run `20260919-165207` · genome `/data/dev/genome/runs/g0b-20260919-165207/G0b.genome` · PREREG docs/G0-PREREG.md §1–§11 + docs/G0b-PREREG.md · every number below is read from results.json

## The nine marks, bars as written before the run (§5), predictions of G0b §4 beside each

| mark | bar | read | pass | G0b §4 predicted |
|---|---|---|---|---|
| (i) it answers | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.995 · Q2 1.00 · Q3 0.995 (ceiling 0.998) · Q4 0.995 | True | PASS |
| (ii) the meeting is real | T-shuffle, T-nowire Q1 ≤ .20 | T-shuffle Q1 band [0.0, 0.132, 0.055] · T-nowire Q1 0.000 (abstain {'novel': 1, 'noedge': 219, 'ratio': 0}) | True | PASS |
| (iii) growth matters | T-frozen ≥ 30 pp under (i) | T-frozen Q1 0.191 vs design 0.995 | True | PASS |
| (iv) it grows on its own | ≥ 50 born · 0 refused · 5-thing < full world · ≥ 5 % pruned · 0 by disuse | born 86 · refused 0 · 5-thing 20 vs full world 43 at the end of development · pruned 1/72 = 1.4 % (cross-thing born 2, cross-thing pruned 1) · disuse 0 | False | pruning FAILS the 5 % bar unless the near-pair conflates at THETA_N |
| (v) it keeps what it learned | within 5 pp after arrival 2 | Q1 first-10 at 600 0.995 → at 900 0.995 (+0.0 pp) | True | PASS |
| (vi) it knows what it does not know | plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20 | plant zog answered 0.55 (as {'zog': 11}) · null vex abstains 0.90 (answered as {'ring': 2}) · Q5 spiral abstains 1.00 (by {'novel': 20, 'noedge': 0, 'ratio': 0}; answered as {}) · false abstention on seen 0.005 (by {'novel': 1, 'noedge': 0, 'ratio': 0}) | True | the plant PASSES (showings from the gate); Q5 uncertain |
| (vii) replay | two lives byte-identical | True (sha256 cfbc80b3231f8755…) | True | PASS |
| (viii) cost | ≤ 300 s, one process | 2.39 s | True | PASS |
| (ix) not luck | top quartile of 20 random genomes | design composite 0.997 ranks 1 of 21 (best random 0.959) | True | unknown (E29) |
| SCALE | — | 0 events | UNTESTED | — |

## The design life, every number

- Gate G-a wrote THETA_N = 0.968, THETA_M = 0.9986; retina `thresh0.25 centre tower:eye-tower-g2 sqrt unit` (112 numbers); §2's strict rule NOT MET, §11's amended rule met (see the genome file's last line).
- Toy (circle, bar; 2 × 150 moments): Q1 1.000 → PASS.
- The eye: the numpy forward vs the sealed E09d tower's own 2356-frame gate features — max |diff| 0.00e+00, 2356 of 2356 within 1e-4, planted shifted frame caught True; the gene's tower eye-tower-g2 (sha 6abc6d7553d8b8c7…, 112 features) runs the same arithmetic on its seal-checked bytes.
- Things: circle, square, triangle, cross, ring, bar, dot, star, arrow, wave, diamond at 32×32; plant showings 5 (gate: within-thing share ≥ THETA_N 0.503); closest pair circle/diamond between-p95 0.963.
- At the end of development (moment 660): cells 43 sight + 11 words; Q1 0.995 Q2 1.00 Q3 0.995 Q4 0.995; abstain by {'novel': 1, 'noedge': 0, 'ratio': 0}.
- Edges by the ledger's reading: cross-thing born 2 of 75, cross-thing pruned 1 of 1 pruned in all (G0b §3 diagnostic; a same-thing edge is one whose two cells were born on the same thing).
- At the end of arrival 2 (moment 960): cells 70 + 16 (born novelty 70/16, error 0/0 — the error road FIRED 27 times and every birth was refused as redundant (§11 am. 4); refused by budget 0, by arrival [0, 0, 0]); edges alive 71, born 72, pruned 1; merged cells 0/0; removed for disuse 0.
- Q1 per thing at 900: {"circle": 1.0, "square": 1.0, "triangle": 1.0, "cross": 1.0, "ring": 0.95, "bar": 1.0, "dot": 1.0, "star": 1.0, "arrow": 1.0, "wave": 1.0, "diamond": 1.0}; arrival-2 things Q1 1.000 per thing {"moon": 1.0, "house": 1.0, "tree": 1.0, "cup": 1.0, "key": 1.0}.
- Q2 detail (word → the thing of the cell it lit): {"circle": "circle", "square": "square", "triangle": "triangle", "cross": "cross", "ring": "ring", "bar": "bar", "dot": "dot", "star": "star", "arrow": "arrow", "wave": "wave", "diamond": "diamond"}.
- Cells per thing (alive, single-thing): {"circle": 2, "square": 3, "triangle": 5, "cross": 7, "ring": 3, "bar": 5, "dot": 2, "star": 1, "arrow": 5, "wave": 5, "diamond": 5, "moon": 2, "house": 6, "tree": 5, "cup": 11, "key": 3}; multi-thing sight cells 0; answers from multi-word cells 0.
- After the plant (moment 965): Q1 on the first things 0.995; ledger-corruption plant: hash unchanged True.
- Time: design life 2.39 s; replay identical True.

## Twins (§4) — each blind to one thing

- **T-shuffle-5**: Q1 0.000 (abstain {'novel': 0, 'noedge': 0, 'ratio': 95}) · Q2 0.27 · Q3 0.464 · Q4 0.168 · cells 93+16 (error births 31/0, redundant refused 69) · edges alive 442 born 506 pruned 56 (11.1 %) · merged 7/0 · refused budget 0 frozen 0 · 1.97 s
- **T-shuffle-6**: Q1 0.132 (abstain {'novel': 0, 'noedge': 0, 'ratio': 69}) · Q2 0.09 · Q3 0.541 · Q4 0.523 · cells 90+16 (error births 26/0, redundant refused 62) · edges alive 408 born 464 pruned 51 (11.0 %) · merged 5/0 · refused budget 0 frozen 0 · 1.95 s
- **T-shuffle-7**: Q1 0.055 (abstain {'novel': 0, 'noedge': 0, 'ratio': 102}) · Q2 0.09 · Q3 0.514 · Q4 0.400 · cells 90+16 (error births 27/0, redundant refused 74) · edges alive 407 born 467 pruned 53 (11.3 %) · merged 7/0 · refused budget 0 frozen 0 · 1.94 s
- **T-frozen**: Q1 0.191 (abstain {'novel': 173, 'noedge': 0, 'ratio': 0}) · Q2 0.45 · Q3 0.591 · Q4 0.191 · cells 5+5 (error births 0/0, redundant refused 0) · edges alive 5 born 5 pruned 0 (0.0 %) · merged 0/0 · refused budget 0 frozen 1475 · 1.36 s
- **T-nowire**: Q1 0.000 (abstain {'novel': 1, 'noedge': 219, 'ratio': 0}) · Q2 0.00 · Q3 0.500 · Q4 0.000 · cells 70+16 (error births 0/0, redundant refused 0) · edges alive 0 born 0 pruned 0 (0.0 %) · merged 0/0 · refused budget 0 frozen 0 · 1.68 s
- **five-thing life** (660 moments, 132/thing): cells born 20 vs the full world's 43 at the end of development; Q1 1.000.

## Twenty random genomes (§4, E29's control) — composite = mean(Q1..Q4) at 900

| seed | composite | Q1 | Q2 | Q3 | Q4 | theta_n | misfires | budget | kwta | lr | prune | theta_m | stage1 | abstain | cells | refused |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 19 | 0.959 | 0.895 | 1.00 | 0.950 | 0.991 | 0.954 | 4 | 334 | 4 | 0.023 | 0.063 | 0.971 | 236 | 0.76 | 44 | 0 |
| 7 | 0.895 | 0.800 | 0.91 | 0.918 | 0.955 | 0.940 | 6 | 484 | 10 | 0.071 | 0.061 | 0.986 | 378 | 0.90 | 36 | 0 |
| 12 | 0.874 | 0.809 | 0.91 | 0.900 | 0.877 | 0.964 | 3 | 98 | 3 | 0.058 | 0.071 | 0.923 | 245 | 0.56 | 40 | 0 |
| 1 | 0.833 | 0.759 | 0.91 | 0.877 | 0.786 | 0.966 | 5 | 76 | 2 | 0.285 | 0.063 | 0.942 | 189 | 0.70 | 37 | 25 |
| 8 | 0.816 | 0.709 | 1.00 | 0.845 | 0.709 | 0.984 | 3 | 182 | 4 | 0.238 | 0.174 | 0.939 | 288 | 0.68 | 85 | 0 |
| 13 | 0.709 | 0.395 | 0.82 | 0.686 | 0.936 | 0.919 | 7 | 102 | 10 | 0.082 | 0.016 | 0.994 | 359 | 0.50 | 26 | 0 |
| 11 | 0.649 | 0.373 | 0.55 | 0.691 | 0.986 | 0.745 | 2 | 493 | 8 | 0.013 | 0.030 | 0.992 | 53 | 0.56 | 154 | 0 |
| 5 | 0.622 | 0.345 | 0.64 | 0.677 | 0.827 | 0.896 | 7 | 402 | 7 | 0.089 | 0.012 | 0.938 | 268 | 0.52 | 21 | 0 |
| 2 | 0.351 | 0.000 | 0.27 | 0.500 | 0.632 | 0.646 | 3 | 360 | 10 | 0.032 | 0.120 | 0.972 | 335 | 0.53 | 56 | 0 |
| 15 | 0.273 | 0.164 | 0.18 | 0.582 | 0.164 | 0.900 | 6 | 231 | 5 | 0.018 | 0.115 | 0.914 | 373 | 0.67 | 22 | 0 |
| 4 | 0.182 | 0.000 | 0.09 | 0.500 | 0.136 | 0.751 | 8 | 756 | 12 | 0.029 | 0.122 | 0.937 | 291 | 0.59 | 24 | 0 |
| 20 | 0.168 | 0.000 | 0.09 | 0.500 | 0.082 | 0.726 | 3 | 722 | 2 | 0.159 | 0.082 | 0.907 | 357 | 0.98 | 9 | 0 |
| 10 | 0.147 | 0.082 | 0.00 | 0.495 | 0.009 | 0.602 | 8 | 645 | 10 | 0.049 | 0.103 | 0.913 | 311 | 0.91 | 5 | 0 |
| 3 | 0.143 | 0.000 | 0.00 | 0.500 | 0.073 | 0.616 | 1 | 186 | 10 | 0.177 | 0.020 | 0.943 | 325 | 0.58 | 28 | 1184 |
| 6 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.668 | 5 | 760 | 5 | 0.115 | 0.198 | 0.963 | 178 | 0.66 | 11 | 0 |
| 9 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.641 | 7 | 135 | 8 | 0.234 | 0.143 | 0.991 | 169 | 0.95 | 3 | 0 |
| 14 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.677 | 7 | 116 | 9 | 0.259 | 0.129 | 0.954 | 60 | 0.85 | 4 | 0 |
| 16 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.711 | 5 | 625 | 2 | 0.108 | 0.125 | 0.902 | 215 | 0.92 | 7 | 0 |
| 17 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.579 | 7 | 393 | 7 | 0.114 | 0.044 | 0.938 | 297 | 0.80 | 1 | 0 |
| 18 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.852 | 4 | 702 | 4 | 0.029 | 0.194 | 0.956 | 358 | 0.78 | 13 | 0 |

The design genome's composite 0.997 ranks 1 of 21; the best random genome is seed 19 at 0.959.

## What the design life did and did not exercise, read from the numbers

- Error births 0/0 (the road fired 27 times; every birth refused as redundant, §11 am. 4); merges 0/0 (THETA_M 0.9986); edges pruned 1 of 72; cross-thing edges born 2 of 75, cross-thing pruned 1; scale 0. THETA_N 0.968 against between-thing p95 0.903, max 0.970: 2 cross-thing edges were born and 1 of them pruned — the SHRINK genes had that much work and did it.
- In T-shuffle-5 (random pairings) 506 edges were born and 56 pruned (11.1 %), with 31 error births and 7 merges: the PRUNE, error-birth and MERGE genes work when there is something to prune, birth or merge; the design world gives them little.
- The plant: «zog» shown 5 times birthed 3 cells; 0.55 of its 20 held-out renderings were answered «zog», 0.45 abstained (by {'novel': 9, 'noedge': 0, 'ratio': 0}); the gate's within-thing share at THETA_N was 0.503 — the showings formula assumed independent cells, and same-thing cells are not independent.
- Q5: the spiral abstains at 1.00 (by {'novel': 20, 'noedge': 0, 'ratio': 0}; answered as nothing) against its 0.80 bar; the spiral was never in gate G-a's measurement, so the threshold carries no guarantee for a never-shown thing.

## What this verdict does and does not say

- The truth never entered the organism: `genome/machinery.py` imports neither `world` nor `questions` and carries no label field; the ledger is the runner's, built from the stream (clause 12; the hash check proves only that the runner did not touch the organism).
- SCALE is untested here (0 events in 965 moments). §2's strict gate rule was not met; the amended rule was, at the price of several cells per thing — the cells-per-thing line above is that price, measured.
- No sentences, no reasoning, no reward, no sleep, no evolution (§6). Rung 1 is his pictures through the folder door; rung 2 a lineage, only after rung 1.
