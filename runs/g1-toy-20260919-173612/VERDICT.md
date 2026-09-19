# G1 rung 1 — G1-toy (canvases, known truth) — VERDICT: **FAIL** (failed: vi_knows_unknown; gating marks: i_answers, ii_meeting_real, iii_growth_matters, v_keeps, vi_knows_unknown, vii_replay, viii_cost, ix_not_luck, xi_gaze_earns_place, x_gaze_finds_thing)

run `20260919-173612` · genome `G1.genome` · PREREG docs/G1-PREREG.md · GAZE {'fixations': 4, 'grid': 16, 'canvas': 128, 'glance': 32, 'ink': 'border'} · every number below is read from results.json

## The marks, bars as written before the run (G1 §3), predictions of §4 beside each

| mark | bar | read | pass | §4 predicted |
|---|---|---|---|---|
| (i) it answers | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.936 (206/220) · Q2 1.00 (11/11) · Q3 0.973 (214/220; ceiling 0.991) · Q4 1.000 (220/220) | True | PASS on the toy; his: unknown |
| (ii) the meeting is real | T-shuffle, T-nowire Q1 ≤ .20 | T-shuffle Q1 0.045 · T-nowire Q1 0.000 (abstains {'novel': 0, 'noedge': 220, 'ratio': 0}) | True | PASS |
| (iii) growth matters | T-frozen ≥ 30 pp under (i) | T-frozen Q1 0.205 vs 0.936 | True | PASS |
| (iv) it grows on its own | ≥ 50 born · 0 refused · smaller life < full world · ≥ 5 % pruned · 0 by disuse | born 297 · refused 0 · smaller life 100 vs full 175 · pruned 264/529 = 49.9 % (cross-thing born 165, pruned 128) · disuse 0 · births by glance {'on_thing': 264, 'off_thing': 16, 'moments_on': 3738, 'moments_off': 122} | True (reported, not gating) | toy: births above G0b's 86, refusals possible, pruning under 5 % — REPORTED; his: GATING, unknown |
| (v) it keeps what it learned | within 5 pp after arrival 2 | Q1 0.986 → 0.936 | True | PASS (toy); not gradable on his pictures |
| (vi) it knows what it does not know | plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20 | plant answered 0.60 (as {'zog': 12}) · null abstains 0.30 (as {'ring': 14}) · Q5 abstains 0.95 of 20 (by {'novel': 19, 'noedge': 0, 'ratio': 0}; answered as {'ring': 1}) · false abstention 0.018 (by {'novel': 0, 'noedge': 0, 'ratio': 4}) | False | plant PASS, spiral uncertain (toy); his: unknown |
| (vii) replay | two lives byte-identical | identical True (hash af51cd78d7a9b656) | True | PASS |
| (viii) cost | ≤ 600 s | 1.78 s a design life, one process | True | PASS |
| (ix) not luck | rank ≤ 5 of 21 | rank 1 of 21 (design 0.977; best random 0.930, seed 19) | True | unknown |
| (x) the gaze finds the thing | ≥ .90 within the first 2 fixations · ≥ 1.5× random | gaze 1.000 (220/220) · random twin 0.118 (26/220; expected ceiling 0.069) · ratio 8.5× | True | PASS: first fixation on the thing on > 95 %; random near 0.07 |
| (xi) the gaze earns its place | Q1(gaze) − Q1(one glance) ≥ .10 | gaze 0.936 − one glance 0.391 = +0.545 | True | PASS: one glance leaves the thing at 8 px; T-one-glance Q1 under 0.6 |

SCALE: SCALE every 1000 fired 3 times in a 3860-moment life — UNTESTED.

## Gate G-a on the first-fixation glances (toy first-fixation glances)
within-thing: median 0.955 p5 0.847 p95 0.995 · between-thing: median 0.766 p95 0.906 max 0.984 · closest pair circle/diamond p95 0.967 · strict rule NOT MET · THETA_N 0.955 THETA_M 0.9975 · plant showings 5 (p_res 0.504)

## The design life
3860 moments (4 glances a showing) · cells 270+17 (born 280+17: novelty 210/17, error 70/0; refused budget 0, redundant 257) · edges born 529 pruned 264 alive 255 · merged 10+0 · multi-thing sight cells 0 · ledger-corruption plant left the organism unchanged: True · cells per thing {'circle': 16, 'square': 16, 'triangle': 6, 'cross': 17, 'ring': 26, 'bar': 8, 'dot': 15, 'star': 5, 'arrow': 10, 'wave': 18, 'diamond': 30, 'moon': 9, 'house': 13, 'tree': 15, 'cup': 44, 'key': 15} · 1.78 s

## Twins (each blind to exactly one thing)

- **T-random-gaze**: Q1 0.091 (abstain {'novel': 148, 'noedge': 7, 'ratio': 11}) Q2 0.73 Q3 0.559 Q4 0.191 · cells 802 born 802 refused 2781 · edges born 801 pruned 307 · error births 2 merges 0 · 1.45 s
- **T-one-glance**: Q1 0.391 (abstain {'novel': 0, 'noedge': 0, 'ratio': 32}) Q2 0.91 Q3 0.677 Q4 0.955 · cells 90 born 140 refused 0 · edges born 395 pruned 83 · error births 134 merges 50 · 0.66 s
- **T-shuffle-5**: Q1 0.045 (abstain {'novel': 0, 'noedge': 0, 'ratio': 58}) Q2 0.09 Q3 0.482 Q4 0.318 · cells 372 born 486 refused 89 · edges born 3063 pruned 2149 · error births 297 merges 114 · 2.07 s
- **T-frozen**: Q1 0.205 (abstain {'novel': 167, 'noedge': 0, 'ratio': 0}) Q2 0.36 Q3 0.605 Q4 0.205 · cells 6 born 6 refused 0 · edges born 7 pruned 1 · error births 0 merges 0 · 0.39 s
- **T-nowire**: Q1 0.000 (abstain {'novel': 0, 'noedge': 220, 'ratio': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 210 born 210 refused 0 · edges born 0 pruned 0 · error births 0 merges 0 · 0.54 s
- **smaller life** (5 things ['circle', 'square', 'triangle', 'cross', 'ring'], 2640 moments): cells born 100 vs the full world's 175 at the end of development; Q1 0.990.

## 20 random genomes within the declared bounds (the GAZE gene fixed)
| seed | composite | Q1 | Q2 | Q3 | Q4 | θN | kwta | lr | budget | cells |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.624 | 0.505 | 0.73 | 0.741 | 0.523 | 0.966 | 2 | 0.285 | 76 | 71 |
| 2 | 0.412 | 0.009 | 0.27 | 0.500 | 0.868 | 0.646 | 10 | 0.032 | 360 | 132 |
| 3 | 0.168 | 0.014 | 0.09 | 0.505 | 0.064 | 0.616 | 10 | 0.177 | 186 | 40 |
| 4 | 0.295 | 0.000 | 0.27 | 0.500 | 0.409 | 0.751 | 12 | 0.029 | 756 | 67 |
| 5 | 0.551 | 0.259 | 0.55 | 0.632 | 0.768 | 0.896 | 7 | 0.089 | 402 | 63 |
| 6 | 0.183 | 0.036 | 0.09 | 0.514 | 0.091 | 0.668 | 5 | 0.115 | 760 | 29 |
| 7 | 0.852 | 0.750 | 0.82 | 0.886 | 0.955 | 0.940 | 10 | 0.071 | 484 | 155 |
| 8 | 0.623 | 0.400 | 1.00 | 0.691 | 0.400 | 0.984 | 4 | 0.238 | 182 | 221 |
| 9 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.641 | 8 | 0.234 | 135 | 5 |
| 10 | 0.176 | 0.082 | 0.00 | 0.545 | 0.077 | 0.602 | 10 | 0.049 | 645 | 39 |
| 11 | 0.824 | 0.550 | 1.00 | 0.745 | 1.000 | 0.745 | 8 | 0.013 | 493 | 332 |
| 12 | 0.720 | 0.605 | 0.82 | 0.814 | 0.645 | 0.964 | 3 | 0.058 | 98 | 73 |
| 13 | 0.598 | 0.345 | 0.55 | 0.668 | 0.832 | 0.919 | 10 | 0.082 | 102 | 96 |
| 14 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.677 | 9 | 0.259 | 116 | 7 |
| 15 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.900 | 5 | 0.018 | 231 | 63 |
| 16 | 0.127 | 0.000 | 0.00 | 0.500 | 0.009 | 0.711 | 2 | 0.108 | 625 | 13 |
| 17 | 0.151 | 0.000 | 0.09 | 0.500 | 0.014 | 0.579 | 7 | 0.114 | 393 | 2 |
| 18 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.852 | 4 | 0.029 | 702 | 27 |
| 19 | 0.930 | 0.818 | 1.00 | 0.909 | 0.991 | 0.954 | 4 | 0.023 | 334 | 216 |
| 20 | 0.370 | 0.273 | 0.27 | 0.632 | 0.305 | 0.726 | 2 | 0.159 | 722 | 22 |

**Read as written.** G1-toy (canvases, known truth): FAIL; failed ['vi_knows_unknown']. Whole run 74.6 s.
