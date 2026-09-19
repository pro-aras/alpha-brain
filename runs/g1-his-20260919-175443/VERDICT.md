# G1 rung 1 — G1-his (his pictures) — VERDICT: **FAIL** (failed: i_answers, iii_growth_matters, iv_grows_alone, vi_knows_unknown; gating marks: i_answers, ii_meeting_real, iii_growth_matters, iv_grows_alone, vi_knows_unknown, vii_replay, viii_cost, ix_not_luck, xi_gaze_earns_place)

run `20260919-175443` · genome `G1-his.genome` · PREREG docs/G1-PREREG.md · GAZE {'fixations': 4, 'grid': 16, 'canvas': 128, 'glance': 32, 'ink': 'border'} · every number below is read from results.json

## The marks, bars as written before the run (G1 §3), predictions of §6 beside each

| mark | bar | read | pass | §6 predicted |
|---|---|---|---|---|
| (i) it answers | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.109 (10/92) · Q2 0.50 (5/10) · Q3 0.522 (48/92; ceiling 0.707) · Q4 0.370 (34/92) | False | §6: Q1 ≥ .80 (the trio separates; circle/diamond may stay close) |
| (ii) the meeting is real | T-shuffle, T-nowire Q1 ≤ .20 | T-shuffle Q1 0.054 · T-nowire Q1 0.000 (abstains {'novel': 49, 'noedge': 43, 'ratio': 0}) | True | PASS |
| (iii) growth matters | T-frozen ≥ 30 pp under (i) | T-frozen Q1 0.011 vs 0.109 | False | PASS |
| (iv) it grows on its own | ≥ 50 born · 0 refused · smaller life < full world · ≥ 5 % pruned · 0 by disuse | born 400 · refused 197 · smaller life 280 vs full 390 · pruned 24/344 = 7.0 % (cross-thing born 105, pruned 4) · disuse 0 · births by glance None | False | §6: reported; §4 said under 5 % — MISSED on the first run (54.6 %) |
| (v) it keeps what it learned | within 5 pp, read in COUNTS: lost ≤ ceil(0.05 · n) | not gradable (one arrival) | — (reported, not gating) | §6: uncertain (triangle→tree, diamond→house are a context fact) |
| (vi) it knows what it does not know | plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20 | none on his pictures (G1 §2) · «vex» on the ear: novel · Q5 abstains 0.60 of 30 (by {'novel': 18, 'noedge': 0, 'ratio': 0}; answered as {'camera': 9, 'beaver': 2, 'bonsai': 1}) · false abstention 0.587 (by {'novel': 49, 'noedge': 0, 'ratio': 5}) | False | §6: the null plant abstains ≥ .5 |
| (vii) replay | two lives byte-identical | identical True (hash d358fdfe456b9c5b) | True | PASS |
| (viii) cost | ≤ 600 s | 0.35 s a design life, one process — EXCLUDES the glancing (the gaze + the eye run ONCE per picture before any life: see the log's 'glanced' lines, ~10 s for all pictures); G0b's seconds included its retina | True | PASS |
| (ix) not luck | rank ≤ 5 of 21 | rank 2 of 21 (design 0.375; best random 0.424, seed 7) | True | unknown |
| (x) the gaze finds the thing | — | not gradable on his pictures (no truth for the thing's position) | — | — |
| (xi) the gaze earns its place | Q1(gaze) − Q1(one glance) ≥ .10 | gaze 0.109 − one glance 0.000 = +0.109 | True | PASS as before |

SCALE: SCALE every 1000 fired 0 times in a 736-moment life — UNTESTED.

## His world
Words shown: ['ahmad', 'anchor', 'ant', 'bass', 'beaver', 'bonsai', 'brain', 'buddha', 'camera', 'cannon'] · withheld for Q5: **barrel** · development pictures 184 · held-out per word {'ahmad': 2, 'anchor': 10, 'ant': 10, 'bass': 10, 'beaver': 10, 'bonsai': 10, 'brain': 10, 'buddha': 10, 'camera': 10, 'cannon': 10, 'barrel': 30} · folders short of the minimum: none · unreadable: none

## Gate G-a on the first-fixation glances (his first-fixation glances)
within-thing: median 0.836 p5 0.676 p95 0.926 · between-thing: median 0.832 p95 0.921 max 0.983 · closest pair beaver/camera p95 0.947 · strict rule NOT MET · THETA_N None THETA_M None
**The bands OVERLAP under the INK rule — thetas not written; the run used the toy's.**

## The design life
736 moments (4 glances a showing) · cells 390+10 (born 390+10: novelty 390/10, error 0/0; refused budget 197, redundant 27) · edges born 344 pruned 24 alive 320 · merged 0+0 · multi-thing sight cells 0 · ledger-corruption plant left the organism unchanged: True · cells per thing {'ahmad': 4, 'anchor': 55, 'ant': 53, 'bass': 39, 'beaver': 39, 'bonsai': 35, 'brain': 50, 'buddha': 51, 'camera': 36, 'cannon': 28} · 0.35 s

## Twins (each blind to exactly one thing)

- **T-random-gaze**: Q1 0.087 (abstain {'novel': 46, 'noedge': 1, 'ratio': 11}) Q2 0.00 Q3 0.522 Q4 0.250 · cells 390 born 390 refused 216 · edges born 309 pruned 4 · error births 0 merges 0 · 0.3 s
- **T-one-glance**: Q1 0.000 (abstain {'novel': 76, 'noedge': 16, 'ratio': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 173 born 173 refused 0 · edges born 0 pruned 0 · error births 0 merges 0 · 0.13 s
- **T-shuffle-5**: Q1 0.054 (abstain {'novel': 49, 'noedge': 0, 'ratio': 7}) Q2 0.00 Q3 0.500 Q4 0.163 · cells 390 born 390 refused 196 · edges born 364 pruned 4 · error births 0 merges 0 · 0.32 s
- **T-frozen**: Q1 0.011 (abstain {'novel': 88, 'noedge': 1, 'ratio': 0}) Q2 0.10 Q3 0.500 Q4 0.022 · cells 8 born 8 refused 0 · edges born 2 pruned 0 · error births 0 merges 0 · 0.15 s
- **T-nowire**: Q1 0.000 (abstain {'novel': 49, 'noedge': 43, 'ratio': 0}) Q2 0.00 Q3 0.500 Q4 0.000 · cells 390 born 390 refused 195 · edges born 0 pruned 0 · error births 0 merges 0 · 0.22 s
- **smaller life** (5 things ['ahmad', 'anchor', 'ant', 'bass', 'beaver'], 336 moments): cells born 280 vs the full world's 390 at the end of development; Q1 0.214.

## 20 random genomes within the declared bounds (the GAZE gene fixed)
| seed | composite | Q1 | Q2 | Q3 | Q4 | θN | kwta | lr | budget | cells |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.191 | 0.022 | 0.20 | 0.511 | 0.033 | 0.966 | 2 | 0.285 | 76 | 68 |
| 2 | 0.280 | 0.011 | 0.00 | 0.500 | 0.609 | 0.646 | 10 | 0.032 | 360 | 197 |
| 3 | 0.299 | 0.043 | 0.10 | 0.467 | 0.587 | 0.616 | 10 | 0.177 | 186 | 52 |
| 4 | 0.272 | 0.043 | 0.00 | 0.522 | 0.522 | 0.751 | 12 | 0.029 | 756 | 100 |
| 5 | 0.311 | 0.011 | 0.20 | 0.489 | 0.543 | 0.896 | 7 | 0.089 | 402 | 184 |
| 6 | 0.199 | 0.109 | 0.10 | 0.500 | 0.087 | 0.668 | 5 | 0.115 | 760 | 5 |
| 7 | 0.424 | 0.141 | 0.60 | 0.543 | 0.413 | 0.940 | 10 | 0.071 | 484 | 449 |
| 8 | 0.175 | 0.000 | 0.20 | 0.500 | 0.000 | 0.984 | 4 | 0.238 | 182 | 174 |
| 9 | 0.210 | 0.109 | 0.10 | 0.500 | 0.130 | 0.641 | 8 | 0.234 | 135 | 3 |
| 10 | 0.229 | 0.109 | 0.10 | 0.500 | 0.207 | 0.602 | 10 | 0.049 | 645 | 12 |
| 11 | 0.280 | 0.000 | 0.00 | 0.500 | 0.620 | 0.745 | 8 | 0.013 | 493 | 247 |
| 12 | 0.169 | 0.022 | 0.10 | 0.511 | 0.043 | 0.964 | 3 | 0.058 | 98 | 88 |
| 13 | 0.272 | 0.033 | 0.10 | 0.522 | 0.435 | 0.919 | 10 | 0.082 | 102 | 94 |
| 14 | 0.196 | 0.109 | 0.10 | 0.500 | 0.076 | 0.677 | 9 | 0.259 | 116 | 3 |
| 15 | 0.227 | 0.065 | 0.30 | 0.511 | 0.033 | 0.900 | 5 | 0.018 | 231 | 203 |
| 16 | 0.254 | 0.098 | 0.20 | 0.511 | 0.207 | 0.711 | 2 | 0.108 | 625 | 8 |
| 17 | 0.177 | 0.109 | 0.10 | 0.500 | 0.000 | 0.579 | 7 | 0.114 | 393 | 1 |
| 18 | 0.180 | 0.065 | 0.10 | 0.489 | 0.065 | 0.852 | 4 | 0.029 | 702 | 64 |
| 19 | 0.262 | 0.076 | 0.20 | 0.554 | 0.217 | 0.954 | 4 | 0.023 | 334 | 325 |
| 20 | 0.223 | 0.109 | 0.10 | 0.500 | 0.185 | 0.726 | 2 | 0.159 | 722 | 7 |

**Read as written.** G1-his (his pictures): FAIL; failed ['i_answers', 'iii_growth_matters', 'iv_grows_alone', 'vi_knows_unknown']. Whole run 16.2 s.
