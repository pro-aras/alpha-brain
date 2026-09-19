# G1 rung 1 — G1-his (his pictures) — VERDICT: **FAIL** (failed: i_answers, iii_growth_matters, iv_grows_alone, vi_knows_unknown, ix_not_luck, xi_gaze_earns_place; gating marks: i_answers, ii_meeting_real, iii_growth_matters, iv_grows_alone, vi_knows_unknown, vii_replay, viii_cost, ix_not_luck, xi_gaze_earns_place)

run `20260919-174825` · genome `G1-his.genome` · PREREG docs/G1-PREREG.md · GAZE {'fixations': 4, 'grid': 16, 'canvas': 128, 'glance': 32, 'ink': 'border'} · every number below is read from results.json

## The marks, bars as written before the run (G1 §3), predictions of §6 beside each

| mark | bar | read | pass | §6 predicted |
|---|---|---|---|---|
| (i) it answers | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.067 (6/90) · Q2 0.11 (1/9) · Q3 0.522 (47/90; ceiling 0.656) · Q4 0.356 (32/90) | False | §6: Q1 ≥ .80 (the trio separates; circle/diamond may stay close) |
| (ii) the meeting is real | T-shuffle, T-nowire Q1 ≤ .20 | T-shuffle Q1 0.033 · T-nowire Q1 0.000 (abstains {'novel': 45, 'noedge': 45, 'ratio': 0}) | True | PASS |
| (iii) growth matters | T-frozen ≥ 30 pp under (i) | T-frozen Q1 0.000 vs 0.067 | False | PASS |
| (iv) it grows on its own | ≥ 50 born · 0 refused · smaller life < full world · ≥ 5 % pruned · 0 by disuse | born 400 · refused 182 · smaller life 321 vs full 391 · pruned 7/337 = 2.1 % (cross-thing born 109, pruned 2) · disuse 0 · births by glance None | False | §6: reported; §4 said under 5 % — MISSED on the first run (54.6 %) |
| (v) it keeps what it learned | within 5 pp, read in COUNTS: lost ≤ ceil(0.05 · n) | not gradable (one arrival) | — (reported, not gating) | §6: uncertain (triangle→tree, diamond→house are a context fact) |
| (vi) it knows what it does not know | plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20 | none on his pictures (G1 §2) · «vex» on the ear: novel · Q5 abstains 0.63 of 30 (by {'novel': 18, 'noedge': 0, 'ratio': 1}; answered as {'camera': 7, 'bonsai': 2, 'ant': 1, 'bass': 1}) · false abstention 0.689 (by {'novel': 44, 'noedge': 0, 'ratio': 18}) | False | §6: the null plant abstains ≥ .5 |
| (vii) replay | two lives byte-identical | identical True (hash 4edfa98c301f507f) | True | PASS |
| (viii) cost | ≤ 600 s | 0.36 s a design life, one process — EXCLUDES the glancing (the gaze + the eye run ONCE per picture before any life: see the log's 'glanced' lines, ~10 s for all pictures); G0b's seconds included its retina | True | PASS |
| (ix) not luck | rank ≤ 5 of 21 | rank 9 of 21 (design 0.264; best random 0.372, seed 5) | False | unknown |
| (x) the gaze finds the thing | — | not gradable on his pictures (no truth for the thing's position) | — | — |
| (xi) the gaze earns its place | Q1(gaze) − Q1(one glance) ≥ .10 | gaze 0.067 − one glance 0.000 = +0.067 | False | PASS as before |

SCALE: SCALE every 1000 fired 0 times in a 720-moment life — UNTESTED.

## His world
Words shown: ['anchor', 'ant', 'bass', 'beaver', 'bonsai', 'brain', 'buddha', 'camera', 'cannon'] · withheld for Q5: **barrel** · development pictures 180 · held-out per word {'anchor': 10, 'ant': 10, 'bass': 10, 'beaver': 10, 'bonsai': 10, 'brain': 10, 'buddha': 10, 'camera': 10, 'cannon': 10, 'barrel': 30} · folders short of the minimum: none · unreadable: none

## Gate G-a on the first-fixation glances (his first-fixation glances)
within-thing: median 0.836 p5 0.675 p95 0.926 · between-thing: median 0.833 p95 0.921 max 0.983 · closest pair beaver/camera p95 0.947 · strict rule NOT MET · THETA_N None THETA_M None
**The bands OVERLAP under the INK rule — thetas not written; the run used the toy's.**

## The design life
720 moments (4 glances a showing) · cells 391+9 (born 391+9: novelty 390/9, error 1/0; refused budget 182, redundant 38) · edges born 337 pruned 7 alive 330 · merged 0+0 · multi-thing sight cells 0 · ledger-corruption plant left the organism unchanged: True · cells per thing {'anchor': 46, 'ant': 55, 'bass': 41, 'beaver': 42, 'bonsai': 41, 'brain': 46, 'buddha': 53, 'camera': 38, 'cannon': 29} · 0.36 s

## Twins (each blind to exactly one thing)

- **T-random-gaze**: Q1 0.044 (abstain {'novel': 54, 'noedge': 0, 'ratio': 15}) Q2 0.44 Q3 0.500 Q4 0.189 · cells 391 born 391 refused 216 · edges born 303 pruned 8 · error births 0 merges 0 · 0.29 s
- **T-one-glance**: Q1 0.000 (abstain {'novel': 74, 'noedge': 16, 'ratio': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 169 born 169 refused 0 · edges born 0 pruned 0 · error births 0 merges 0 · 0.13 s
- **T-shuffle-5**: Q1 0.033 (abstain {'novel': 45, 'noedge': 0, 'ratio': 15}) Q2 0.00 Q3 0.489 Q4 0.256 · cells 391 born 391 refused 185 · edges born 352 pruned 18 · error births 0 merges 0 · 0.3 s
- **T-frozen**: Q1 0.000 (abstain {'novel': 74, 'noedge': 16, 'ratio': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 8 born 8 refused 0 · edges born 0 pruned 0 · error births 0 merges 0 · 0.14 s
- **T-nowire**: Q1 0.000 (abstain {'novel': 45, 'noedge': 45, 'ratio': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 391 born 391 refused 185 · edges born 0 pruned 0 · error births 0 merges 0 · 0.21 s
- **smaller life** (5 things ['anchor', 'ant', 'bass', 'beaver', 'bonsai'], 400 moments): cells born 321 vs the full world's 391 at the end of development; Q1 0.120.

## 20 random genomes within the declared bounds (the GAZE gene fixed)
| seed | composite | Q1 | Q2 | Q3 | Q4 | θN | kwta | lr | budget | cells |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.142 | 0.022 | 0.00 | 0.511 | 0.033 | 0.966 | 2 | 0.285 | 76 | 68 |
| 2 | 0.272 | 0.000 | 0.00 | 0.500 | 0.589 | 0.646 | 10 | 0.032 | 360 | 187 |
| 3 | 0.303 | 0.100 | 0.00 | 0.522 | 0.589 | 0.616 | 10 | 0.177 | 186 | 53 |
| 4 | 0.247 | 0.033 | 0.00 | 0.500 | 0.456 | 0.751 | 12 | 0.029 | 756 | 92 |
| 5 | 0.372 | 0.044 | 0.33 | 0.533 | 0.578 | 0.896 | 7 | 0.089 | 402 | 186 |
| 6 | 0.183 | 0.111 | 0.00 | 0.500 | 0.122 | 0.668 | 5 | 0.115 | 760 | 7 |
| 7 | 0.344 | 0.078 | 0.44 | 0.478 | 0.378 | 0.940 | 10 | 0.071 | 484 | 440 |
| 8 | 0.153 | 0.000 | 0.11 | 0.500 | 0.000 | 0.984 | 4 | 0.238 | 182 | 173 |
| 9 | 0.225 | 0.111 | 0.11 | 0.500 | 0.178 | 0.641 | 8 | 0.234 | 135 | 4 |
| 10 | 0.156 | 0.111 | 0.00 | 0.500 | 0.011 | 0.602 | 10 | 0.049 | 645 | 4 |
| 11 | 0.308 | 0.022 | 0.11 | 0.500 | 0.600 | 0.745 | 8 | 0.013 | 493 | 239 |
| 12 | 0.139 | 0.011 | 0.00 | 0.511 | 0.033 | 0.964 | 3 | 0.058 | 98 | 90 |
| 13 | 0.261 | 0.022 | 0.00 | 0.500 | 0.522 | 0.919 | 10 | 0.082 | 102 | 93 |
| 14 | 0.211 | 0.111 | 0.11 | 0.500 | 0.122 | 0.677 | 9 | 0.259 | 116 | 5 |
| 15 | 0.356 | 0.111 | 0.67 | 0.544 | 0.100 | 0.900 | 5 | 0.018 | 231 | 200 |
| 16 | 0.306 | 0.111 | 0.22 | 0.500 | 0.389 | 0.711 | 2 | 0.108 | 625 | 7 |
| 17 | 0.194 | 0.111 | 0.00 | 0.489 | 0.178 | 0.579 | 7 | 0.114 | 393 | 2 |
| 18 | 0.197 | 0.111 | 0.11 | 0.500 | 0.067 | 0.852 | 4 | 0.029 | 702 | 58 |
| 19 | 0.247 | 0.044 | 0.22 | 0.511 | 0.211 | 0.954 | 4 | 0.023 | 334 | 325 |
| 20 | 0.269 | 0.122 | 0.00 | 0.511 | 0.444 | 0.726 | 2 | 0.159 | 722 | 11 |

**Read as written.** G1-his (his pictures): FAIL; failed ['i_answers', 'iii_growth_matters', 'iv_grows_alone', 'vi_knows_unknown', 'ix_not_luck', 'xi_gaze_earns_place']. Whole run 15.6 s.
