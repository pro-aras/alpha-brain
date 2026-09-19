# G1 rung 1 — G1-toy (canvases, known truth) — VERDICT: **FAIL** (failed: i_answers, v_keeps, vi_knows_unknown; gating marks: i_answers, ii_meeting_real, iii_growth_matters, v_keeps, vi_knows_unknown, vii_replay, viii_cost, ix_not_luck, xi_gaze_earns_place, x_gaze_finds_thing)

run `20260919-172810` · genome `G1.genome` · PREREG docs/G1-PREREG.md · GAZE {'fixations': 4, 'grid': 16, 'canvas': 128, 'glance': 32, 'ink': 'contrast'} · every number below is read from results.json

## The marks, bars as written before the run (G1 §3), predictions of §4 beside each

| mark | bar | read | pass | §4 predicted |
|---|---|---|---|---|
| (i) it answers | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.777 (171/220) · Q2 0.82 (9/11) · Q3 0.891 (196/220; ceiling 0.939) · Q4 0.986 (217/220) | False | PASS on the toy; his: unknown |
| (ii) the meeting is real | T-shuffle, T-nowire Q1 ≤ .20 | T-shuffle Q1 0.027 · T-nowire Q1 0.000 (abstains {'novel': 0, 'noedge': 220, 'ratio': 0}) | True | PASS |
| (iii) growth matters | T-frozen ≥ 30 pp under (i) | T-frozen Q1 0.173 vs 0.777 | True | PASS |
| (iv) it grows on its own | ≥ 50 born · 0 refused · smaller life < full world · ≥ 5 % pruned · 0 by disuse | born 387 · refused 0 · smaller life 164 vs full 230 · pruned 580/1062 = 54.6 % (cross-thing born 555, pruned 368) · disuse 0 · births by glance {'on_thing': 349, 'off_thing': 21, 'moments_on': 3738, 'moments_off': 122} | True (reported, not gating) | toy: births above G0b's 86, refusals possible, pruning under 5 % — REPORTED; his: GATING, unknown |
| (v) it keeps what it learned | within 5 pp after arrival 2 | Q1 0.832 → 0.777 | False | PASS (toy); not gradable on his pictures |
| (vi) it knows what it does not know | plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20 | plant answered 0.60 (as {'zog': 12}) · null abstains 0.20 (as {'ring': 16}) · Q5 abstains 0.95 of 20 (by {'novel': 19, 'noedge': 0, 'ratio': 0}; answered as {'ring': 1}) · false abstention 0.123 (by {'novel': 0, 'noedge': 0, 'ratio': 27}) | False | plant PASS, spiral uncertain (toy); his: unknown |
| (vii) replay | two lives byte-identical | identical True (hash ecc09a70426e877a) | True | PASS |
| (viii) cost | ≤ 600 s | 1.91 s a design life, one process | True | PASS |
| (ix) not luck | rank ≤ 5 of 21 | rank 1 of 21 (design 0.868; best random 0.824, seed 19) | True | unknown |
| (x) the gaze finds the thing | ≥ .90 within the first 2 fixations · ≥ 1.5× random | gaze 1.000 (220/220) · random twin 0.118 (26/220; expected ceiling 0.069) · ratio 8.5× | True | PASS: first fixation on the thing on > 95 %; random near 0.07 |
| (xi) the gaze earns its place | Q1(gaze) − Q1(one glance) ≥ .10 | gaze 0.777 − one glance 0.291 = +0.486 | True | PASS: one glance leaves the thing at 8 px; T-one-glance Q1 under 0.6 |

SCALE: SCALE every 1000 fired 3 times in a 3860-moment life — UNTESTED.

## Gate G-a on the first-fixation glances (toy first-fixation glances)
within-thing: median 0.950 p5 0.817 p95 0.994 · between-thing: median 0.704 p95 0.929 max 0.995 · closest pair circle/diamond p95 0.990 · strict rule NOT MET · THETA_N 0.95 THETA_M 0.997 · plant showings 5 (p_res 0.500)

## The design life
3860 moments (4 glances a showing) · cells 357+17 (born 370+17: novelty 246/17, error 124/0; refused budget 0, redundant 313) · edges born 1062 pruned 580 alive 469 · merged 13+0 · multi-thing sight cells 0 · ledger-corruption plant left the organism unchanged: True · cells per thing {'circle': 29, 'square': 37, 'triangle': 25, 'cross': 31, 'ring': 25, 'bar': 7, 'dot': 9, 'star': 15, 'arrow': 10, 'wave': 13, 'diamond': 21, 'moon': 7, 'house': 42, 'tree': 30, 'cup': 39, 'key': 8} · 1.91 s

## Twins (each blind to exactly one thing)

- **T-random-gaze**: Q1 0.059 (abstain {'novel': 113, 'noedge': 15, 'ratio': 22}) Q2 0.36 Q3 0.532 Q4 0.250 · cells 800 born 800 refused 2591 · edges born 1010 pruned 442 · error births 5 merges 0 · 1.52 s
- **T-one-glance**: Q1 0.291 (abstain {'novel': 0, 'noedge': 0, 'ratio': 44}) Q2 0.91 Q3 0.641 Q4 0.945 · cells 87 born 149 refused 0 · edges born 428 pruned 101 · error births 145 merges 62 · 0.67 s
- **T-shuffle-5**: Q1 0.027 (abstain {'novel': 0, 'noedge': 0, 'ratio': 51}) Q2 0.09 Q3 0.486 Q4 0.327 · cells 386 born 491 refused 121 · edges born 3792 pruned 2784 · error births 278 merges 105 · 2.12 s
- **T-frozen**: Q1 0.173 (abstain {'novel': 146, 'noedge': 0, 'ratio': 0}) Q2 0.36 Q3 0.586 Q4 0.177 · cells 6 born 6 refused 0 · edges born 8 pruned 1 · error births 0 merges 0 · 0.42 s
- **T-nowire**: Q1 0.000 (abstain {'novel': 0, 'noedge': 220, 'ratio': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 241 born 241 refused 0 · edges born 0 pruned 0 · error births 0 merges 0 · 0.56 s
- **smaller life** (5 things ['circle', 'square', 'triangle', 'cross', 'ring'], 2640 moments): cells born 164 vs the full world's 230 at the end of development; Q1 0.780.

## 20 random genomes within the declared bounds (the GAZE gene fixed)
| seed | composite | Q1 | Q2 | Q3 | Q4 | θN | kwta | lr | budget | cells |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.549 | 0.377 | 0.73 | 0.700 | 0.391 | 0.966 | 2 | 0.285 | 76 | 76 |
| 2 | 0.387 | 0.000 | 0.27 | 0.500 | 0.777 | 0.646 | 10 | 0.032 | 360 | 174 |
| 3 | 0.147 | 0.005 | 0.00 | 0.505 | 0.077 | 0.616 | 10 | 0.177 | 186 | 40 |
| 4 | 0.276 | 0.000 | 0.18 | 0.500 | 0.423 | 0.751 | 12 | 0.029 | 756 | 84 |
| 5 | 0.476 | 0.264 | 0.36 | 0.627 | 0.650 | 0.896 | 7 | 0.089 | 402 | 69 |
| 6 | 0.147 | 0.000 | 0.00 | 0.500 | 0.086 | 0.668 | 5 | 0.115 | 760 | 31 |
| 7 | 0.760 | 0.600 | 0.82 | 0.805 | 0.818 | 0.940 | 10 | 0.071 | 484 | 194 |
| 8 | 0.518 | 0.268 | 0.82 | 0.641 | 0.345 | 0.984 | 4 | 0.238 | 182 | 262 |
| 9 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.641 | 8 | 0.234 | 135 | 5 |
| 10 | 0.235 | 0.091 | 0.18 | 0.518 | 0.150 | 0.602 | 10 | 0.049 | 645 | 39 |
| 11 | 0.574 | 0.195 | 0.55 | 0.586 | 0.968 | 0.745 | 8 | 0.013 | 493 | 409 |
| 12 | 0.588 | 0.414 | 0.73 | 0.709 | 0.500 | 0.964 | 3 | 0.058 | 98 | 84 |
| 13 | 0.577 | 0.395 | 0.45 | 0.705 | 0.755 | 0.919 | 10 | 0.082 | 102 | 106 |
| 14 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.677 | 9 | 0.259 | 116 | 7 |
| 15 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.900 | 5 | 0.018 | 231 | 69 |
| 16 | 0.250 | 0.091 | 0.18 | 0.545 | 0.182 | 0.711 | 2 | 0.108 | 625 | 15 |
| 17 | 0.157 | 0.000 | 0.09 | 0.500 | 0.036 | 0.579 | 7 | 0.114 | 393 | 3 |
| 18 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.852 | 4 | 0.029 | 702 | 30 |
| 19 | 0.824 | 0.686 | 0.82 | 0.855 | 0.936 | 0.954 | 4 | 0.023 | 334 | 304 |
| 20 | 0.170 | 0.000 | 0.09 | 0.500 | 0.091 | 0.726 | 2 | 0.159 | 722 | 21 |

**Read as written.** G1-toy (canvases, known truth): FAIL; failed ['i_answers', 'v_keeps', 'vi_knows_unknown']. Whole run 72.9 s.
