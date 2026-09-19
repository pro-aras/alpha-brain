# G1 rung 1 — G1b-toy (canvases, known truth; §6 amendment 1, ink border) — VERDICT: **FAIL** (failed: i_answers, v_keeps, vi_knows_unknown; gating marks: i_answers, ii_meeting_real, iii_growth_matters, v_keeps, vi_knows_unknown, vii_replay, viii_cost, ix_not_luck, xi_gaze_earns_place, x_gaze_finds_thing)

run `20260919-193438` · genome `G3-toy.genome` · PREREG docs/G1-PREREG.md · GAZE {'fixations': 4, 'grid': 16, 'canvas': 128, 'glance': 32, 'ink': 'border'} · every number below is read from results.json

## The marks, bars as written before the run (G1 §3), predictions of §6 beside each

| mark | bar | read | pass | §6 predicted |
|---|---|---|---|---|
| (i) it answers | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.582 (128/220) · Q2 1.00 (11/11) · Q3 0.795 (175/220; ceiling 0.793) · Q4 1.000 (220/220) | False | §6: Q1 ≥ .80 (the trio separates; circle/diamond may stay close) |
| (ii) the meeting is real | T-shuffle, T-nowire Q1 ≤ .20 | T-shuffle Q1 0.000 · T-nowire Q1 0.000 (abstains {'novel': 0, 'noedge': 220, 'ratio': 0, 'close': 0}) | True | PASS |
| (iii) growth matters | T-frozen ≥ 30 pp under (i) | T-frozen Q1 0.091 vs 0.582 | True | PASS |
| (iv) it grows on its own | ≥ 50 born · 0 refused · smaller life < full world · ≥ 5 % pruned · 0 by disuse | born 313 · refused 0 · smaller life 99 vs full 200 · pruned 604/1000 = 60.4 % (cross-thing born 693, pruned 570) · disuse 0 · births by glance {'on_thing': 274, 'off_thing': 22, 'moments_on': 3738, 'moments_off': 122} | True (reported, not gating) | §6: reported; §4 said under 5 % — MISSED on the first run (54.6 %) |
| (v) it keeps what it learned | within 5 pp, read in COUNTS: lost ≤ ceil(0.05 · n) | Q1 0.859 → 0.605 (189 → 133 of 220; lost 56, allowed 11) | False | §6: uncertain (triangle→tree, diamond→house are a context fact) |
| (vi) it knows what it does not know | plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20 | plant answered 0.70 (as {'zog': 14}) · null abstains 0.60 (as {'ring': 8}) · Q5 abstains 0.75 of 20 (by {'novel': 0, 'noedge': 0, 'ratio': 2, 'close': 13}; answered as {'ring': 5}) · false abstention 0.414 (by {'novel': 0, 'noedge': 0, 'ratio': 8, 'close': 83}) | False | §6: the null plant abstains ≥ .5 |
| (vii) replay | two lives byte-identical | identical True (hash a2875ffa6fd47d54) | True | PASS |
| (viii) cost | ≤ 600 s | 2.62 s a design life, one process — EXCLUDES the glancing (the gaze + the eye run ONCE per picture before any life: see the log's 'glanced' lines, ~10 s for all pictures); G0b's seconds included its retina | True | PASS |
| (ix) not luck | rank ≤ 5 of 21 | rank 2 of 21 (design 0.844; best random 0.887, seed 19) | True | unknown |
| (x) the gaze finds the thing | ≥ .90 within the first 2 fixations · ≥ 1.5× random | gaze 1.000 (220/220) · random twin 0.118 (26/220; expected ceiling 0.069) · ratio 8.5× | True | PASS as before |
| (xi) the gaze earns its place | Q1(gaze) − Q1(one glance) ≥ .10 | gaze 0.582 − one glance 0.091 = +0.491 | True | PASS as before |

SCALE: SCALE every 1000 fired 3 times in a 3860-moment life — UNTESTED.

## Gate G-a on the first-fixation glances (toy first-fixation glances (G3-toy))
within-thing: median 0.955 p5 0.847 p95 0.995 · between-thing: median 0.766 p95 0.906 max 0.984 · closest pair circle/diamond p95 0.967 · strict rule NOT MET · THETA_N 0.576 THETA_M 0.9975 · plant showings 5 (p_res 1.000)

## The design life
3860 moments (4 glances a showing) · cells 208+17 (born 296+17: novelty 2/17, error 294/0; refused budget 0, redundant 77) · edges born 1000 pruned 604 alive 308 · merged 88+0 · multi-thing sight cells 0 · ledger-corruption plant left the organism unchanged: True · cells per thing {'circle': 17, 'square': 19, 'triangle': 10, 'cross': 9, 'ring': 11, 'bar': 10, 'dot': 5, 'star': 8, 'arrow': 11, 'wave': 8, 'diamond': 29, 'moon': 6, 'house': 21, 'tree': 18, 'cup': 14, 'key': 10} · 2.62 s

## Twins (each blind to exactly one thing)

- **T-random-gaze**: Q1 0.000 (abstain {'novel': 0, 'noedge': 0, 'ratio': 110, 'close': 107}) Q2 0.27 Q3 0.500 Q4 0.523 · cells 425 born 476 refused 132 · edges born 8268 pruned 6766 · error births 472 merges 51 · 3.23 s
- **T-one-glance**: Q1 0.091 (abstain {'novel': 0, 'noedge': 0, 'ratio': 39, 'close': 161}) Q2 0.91 Q3 0.541 Q4 0.959 · cells 99 born 159 refused 0 · edges born 448 pruned 106 · error births 158 merges 60 · 0.81 s
- **T-shuffle-5**: Q1 0.000 (abstain {'novel': 0, 'noedge': 0, 'ratio': 61, 'close': 136}) Q2 0.09 Q3 0.495 Q4 0.332 · cells 281 born 444 refused 244 · edges born 3823 pruned 2869 · error births 442 merges 163 · 2.6 s
- **T-frozen**: Q1 0.091 (abstain {'novel': 0, 'noedge': 0, 'ratio': 0, 'close': 0}) Q2 0.09 Q3 0.500 Q4 0.041 · cells 1 born 1 refused 0 · edges born 76 pruned 70 · error births 0 merges 0 · 0.85 s
- **T-nowire**: Q1 0.000 (abstain {'novel': 0, 'noedge': 220, 'ratio': 0, 'close': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 2 born 2 refused 0 · edges born 0 pruned 0 · error births 0 merges 0 · 0.4 s
- **smaller life** (5 things ['circle', 'square', 'triangle', 'cross', 'ring'], 2640 moments): cells born 99 vs the full world's 200 at the end of development; Q1 0.840.

## 20 random genomes within the declared bounds (the GAZE gene fixed)
| seed | composite | Q1 | Q2 | Q3 | Q4 | θN | kwta | lr | budget | cells |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.616 | 0.482 | 0.73 | 0.732 | 0.523 | 0.966 | 2 | 0.285 | 76 | 71 |
| 2 | 0.412 | 0.009 | 0.27 | 0.500 | 0.868 | 0.646 | 10 | 0.032 | 360 | 132 |
| 3 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.616 | 10 | 0.177 | 186 | 37 |
| 4 | 0.295 | 0.000 | 0.27 | 0.500 | 0.409 | 0.751 | 12 | 0.029 | 756 | 67 |
| 5 | 0.545 | 0.245 | 0.55 | 0.623 | 0.768 | 0.896 | 7 | 0.089 | 402 | 63 |
| 6 | 0.183 | 0.036 | 0.09 | 0.514 | 0.091 | 0.668 | 5 | 0.115 | 760 | 29 |
| 7 | 0.811 | 0.650 | 0.82 | 0.823 | 0.955 | 0.940 | 10 | 0.071 | 484 | 155 |
| 8 | 0.623 | 0.400 | 1.00 | 0.691 | 0.400 | 0.984 | 4 | 0.238 | 182 | 221 |
| 9 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.641 | 8 | 0.234 | 135 | 5 |
| 10 | 0.170 | 0.000 | 0.09 | 0.500 | 0.091 | 0.602 | 10 | 0.049 | 645 | 39 |
| 11 | 0.789 | 0.450 | 1.00 | 0.705 | 1.000 | 0.745 | 8 | 0.013 | 493 | 332 |
| 12 | 0.708 | 0.568 | 0.82 | 0.800 | 0.645 | 0.964 | 3 | 0.058 | 98 | 73 |
| 13 | 0.582 | 0.300 | 0.55 | 0.650 | 0.832 | 0.919 | 10 | 0.082 | 102 | 96 |
| 14 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.677 | 9 | 0.259 | 116 | 7 |
| 15 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.900 | 5 | 0.018 | 231 | 63 |
| 16 | 0.127 | 0.000 | 0.00 | 0.500 | 0.009 | 0.711 | 2 | 0.108 | 625 | 13 |
| 17 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.579 | 7 | 0.114 | 393 | 2 |
| 18 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.852 | 4 | 0.029 | 702 | 27 |
| 19 | 0.887 | 0.700 | 1.00 | 0.859 | 0.991 | 0.954 | 4 | 0.023 | 334 | 216 |
| 20 | 0.342 | 0.200 | 0.27 | 0.591 | 0.305 | 0.726 | 2 | 0.159 | 722 | 22 |

**Read as written.** G1b-toy (canvases, known truth; §6 amendment 1, ink border): FAIL; failed ['i_answers', 'v_keeps', 'vi_knows_unknown']. Whole run 79.1 s.
