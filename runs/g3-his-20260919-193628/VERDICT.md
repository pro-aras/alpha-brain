# G1 rung 1 — G1-his (his pictures) — VERDICT: **FAIL** (failed: i_answers, iii_growth_matters, vi_knows_unknown, xi_gaze_earns_place; gating marks: i_answers, ii_meeting_real, iii_growth_matters, iv_grows_alone, vi_knows_unknown, vii_replay, viii_cost, ix_not_luck, xi_gaze_earns_place)

run `20260919-193628` · genome `G3-his.genome` · PREREG docs/G1-PREREG.md · GAZE {'fixations': 4, 'grid': 16, 'canvas': 128, 'glance': 64, 'ink': 'border'} · every number below is read from results.json

## The marks, bars as written before the run (G1 §3), predictions of §6 beside each

| mark | bar | read | pass | §6 predicted |
|---|---|---|---|---|
| (i) it answers | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.087 (8/92) · Q2 0.40 (4/10) · Q3 0.511 (47/92; ceiling 0.804) · Q4 0.630 (58/92) | False | §6: Q1 ≥ .80 (the trio separates; circle/diamond may stay close) |
| (ii) the meeting is real | T-shuffle, T-nowire Q1 ≤ .20 | T-shuffle Q1 0.098 · T-nowire Q1 0.000 (abstains {'novel': 0, 'noedge': 92, 'ratio': 0, 'close': 0}) | True | PASS |
| (iii) growth matters | T-frozen ≥ 30 pp under (i) | T-frozen Q1 0.109 vs 0.087 | False | PASS |
| (iv) it grows on its own | ≥ 50 born · 0 refused · smaller life < full world · ≥ 5 % pruned · 0 by disuse | born 208 · refused 0 · smaller life 53 vs full 198 · pruned 143/799 = 17.9 % (cross-thing born 636, pruned 127) · disuse 0 · births by glance None | True | §6: reported; §4 said under 5 % — MISSED on the first run (54.6 %) |
| (v) it keeps what it learned | within 5 pp, read in COUNTS: lost ≤ ceil(0.05 · n) | not gradable (one arrival) | — (reported, not gating) | §6: uncertain (triangle→tree, diamond→house are a context fact) |
| (vi) it knows what it does not know | plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20 | none on his pictures (G1 §2) · «vex» on the ear: novel · Q5 abstains 0.27 of 30 (by {'novel': 0, 'noedge': 0, 'ratio': 8, 'close': 0}; answered as {'buddha': 6, 'bass': 2, 'cannon': 7, 'camera': 3, 'beaver': 3, 'ahmad': 1}) · false abstention 0.391 (by {'novel': 0, 'noedge': 0, 'ratio': 36, 'close': 0}) | False | §6: the null plant abstains ≥ .5 |
| (vii) replay | two lives byte-identical | identical True (hash c2d7030ff2c561af) | True | PASS |
| (viii) cost | ≤ 600 s | 0.53 s a design life, one process — EXCLUDES the glancing (the gaze + the eye run ONCE per picture before any life: see the log's 'glanced' lines, ~10 s for all pictures); G0b's seconds included its retina | True | PASS |
| (ix) not luck | rank ≤ 5 of 21 | rank 5 of 21 (design 0.407; best random 0.473, seed 10) | True | unknown |
| (x) the gaze finds the thing | — | not gradable on his pictures (no truth for the thing's position) | — | — |
| (xi) the gaze earns its place | Q1(gaze) − Q1(one glance) ≥ .10 | gaze 0.087 − one glance 0.000 = +0.087 | False | PASS as before |

SCALE: SCALE every 1000 fired 0 times in a 736-moment life — UNTESTED.

## His world
Words shown: ['ahmad', 'anchor', 'ant', 'bass', 'beaver', 'bonsai', 'brain', 'buddha', 'camera', 'cannon'] · withheld for Q5: **barrel** · development pictures 184 · held-out per word {'ahmad': 2, 'anchor': 10, 'ant': 10, 'bass': 10, 'beaver': 10, 'bonsai': 10, 'brain': 10, 'buddha': 10, 'camera': 10, 'cannon': 10, 'barrel': 30} · folders short of the minimum: none · unreadable: none

## Gate G-a on the first-fixation glances (his first-fixation glances (G3-his))
within-thing: median 0.496 p5 0.366 p95 0.656 · between-thing: median 0.480 p95 0.612 max 0.803 · closest pair ahmad/buddha p95 0.675 · strict rule NOT MET · THETA_N 0.36 THETA_M 0.8278 · plant showings 5 (p_res 0.958)

## The design life
736 moments (4 glances a showing) · cells 161+10 (born 198+10: novelty 2/10, error 196/0; refused budget 0, redundant 39) · edges born 799 pruned 143 alive 618 · merged 37+0 · multi-thing sight cells 0 · ledger-corruption plant left the organism unchanged: True · cells per thing {'ahmad': 3, 'anchor': 13, 'ant': 14, 'bass': 19, 'beaver': 16, 'bonsai': 24, 'brain': 16, 'buddha': 15, 'camera': 21, 'cannon': 20} · 0.53 s

## Twins (each blind to exactly one thing)

- **T-random-gaze**: Q1 0.109 (abstain {'novel': 0, 'noedge': 0, 'ratio': 37, 'close': 0}) Q2 0.30 Q3 0.533 Q4 0.620 · cells 162 born 187 refused 0 · edges born 926 pruned 175 · error births 184 merges 25 · 0.49 s
- **T-one-glance**: Q1 0.000 (abstain {'novel': 0, 'noedge': 92, 'ratio': 0, 'close': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 1 born 1 refused 0 · edges born 0 pruned 0 · error births 0 merges 0 · 0.12 s
- **T-shuffle-5**: Q1 0.098 (abstain {'novel': 0, 'noedge': 0, 'ratio': 33, 'close': 0}) Q2 0.00 Q3 0.522 Q4 0.250 · cells 159 born 200 refused 0 · edges born 939 pruned 161 · error births 198 merges 41 · 0.5 s
- **T-frozen**: Q1 0.109 (abstain {'novel': 0, 'noedge': 0, 'ratio': 0, 'close': 0}) Q2 0.00 Q3 0.511 Q4 0.152 · cells 2 born 2 refused 0 · edges born 33 pruned 20 · error births 0 merges 0 · 0.29 s
- **T-nowire**: Q1 0.000 (abstain {'novel': 0, 'noedge': 92, 'ratio': 0, 'close': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 2 born 2 refused 0 · edges born 0 pruned 0 · error births 0 merges 0 · 0.16 s
- **smaller life** (5 things ['ahmad', 'anchor', 'ant', 'bass', 'beaver'], 336 moments): cells born 53 vs the full world's 198 at the end of development; Q1 0.310.

## 20 random genomes within the declared bounds (the GAZE gene fixed)
| seed | composite | Q1 | Q2 | Q3 | Q4 | θN | kwta | lr | budget | cells |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.966 | 2 | 0.285 | 76 | 68 |
| 2 | 0.259 | 0.098 | 0.10 | 0.522 | 0.315 | 0.646 | 10 | 0.032 | 360 | 193 |
| 3 | 0.360 | 0.033 | 0.30 | 0.489 | 0.620 | 0.616 | 10 | 0.177 | 186 | 139 |
| 4 | 0.366 | 0.033 | 0.90 | 0.500 | 0.033 | 0.751 | 12 | 0.029 | 756 | 448 |
| 5 | 0.391 | 0.022 | 1.00 | 0.522 | 0.022 | 0.896 | 7 | 0.089 | 402 | 392 |
| 6 | 0.414 | 0.163 | 0.60 | 0.543 | 0.348 | 0.668 | 5 | 0.115 | 760 | 223 |
| 7 | 0.383 | 0.011 | 1.00 | 0.511 | 0.011 | 0.940 | 10 | 0.071 | 484 | 474 |
| 8 | 0.150 | 0.000 | 0.10 | 0.500 | 0.000 | 0.984 | 4 | 0.238 | 182 | 174 |
| 9 | 0.374 | 0.152 | 0.40 | 0.522 | 0.424 | 0.641 | 8 | 0.234 | 135 | 125 |
| 10 | 0.473 | 0.207 | 0.50 | 0.554 | 0.630 | 0.602 | 10 | 0.049 | 645 | 76 |
| 11 | 0.364 | 0.152 | 0.50 | 0.554 | 0.250 | 0.745 | 8 | 0.013 | 493 | 442 |
| 12 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.964 | 3 | 0.058 | 98 | 90 |
| 13 | 0.125 | 0.000 | 0.00 | 0.500 | 0.000 | 0.919 | 10 | 0.082 | 102 | 94 |
| 14 | 0.372 | 0.217 | 0.40 | 0.587 | 0.283 | 0.677 | 9 | 0.259 | 116 | 107 |
| 15 | 0.150 | 0.000 | 0.10 | 0.500 | 0.000 | 0.900 | 5 | 0.018 | 231 | 222 |
| 16 | 0.444 | 0.217 | 0.70 | 0.576 | 0.283 | 0.711 | 2 | 0.108 | 625 | 358 |
| 17 | 0.321 | 0.120 | 0.00 | 0.533 | 0.630 | 0.579 | 7 | 0.114 | 393 | 45 |
| 18 | 0.375 | 0.000 | 1.00 | 0.500 | 0.000 | 0.852 | 4 | 0.029 | 702 | 564 |
| 19 | 0.350 | 0.000 | 0.90 | 0.500 | 0.000 | 0.954 | 4 | 0.023 | 334 | 325 |
| 20 | 0.432 | 0.130 | 0.90 | 0.533 | 0.163 | 0.726 | 2 | 0.159 | 722 | 388 |

**Read as written.** G1-his (his pictures): FAIL; failed ['i_answers', 'iii_growth_matters', 'vi_knows_unknown', 'xi_gaze_earns_place']. Whole run 21.1 s.
