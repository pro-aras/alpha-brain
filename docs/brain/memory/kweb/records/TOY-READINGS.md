# KW-1 · the toy (written by tools/web/kw1_toy.py)
G1 recount (POSITIVE, seed 1): [{'rule': 'H', 'errors': 0, 'first': []}, {'rule': 'F', 'errors': 0, 'first': []}, {'rule': 'L', 'errors': 0, 'first': []}, {'rule': 'S', 'errors': 0, 'first': []}, {'rule': 'R', 'errors': 0, 'first': []}, {'rule': 'S0', 'errors': 0, 'first': []}] · plant caught: True
G2 determinism: {'same_seed_identical': True, 'other_seed_differs': True}
G3 budget held in every budgeted run: True (150 runs)

| rule | POSITIVE recall (mean) | POSITIVE precision (mean) | consolidated (mean) | NULL consolidated (mean) | CHANGE recall new | CHANGE recall old |
|---|---|---|---|---|---|---|
| H | 0.914 | 0.693 | 156.6 | 68.6 | 0.635 | 0.813 |
| F | 0.143 | 0.907 | 18.7 | 2.1 | 0.050 | 0.131 |
| L | 0.239 | 0.564 | 50.4 | 25.7 | 0.086 | 0.214 |
| S | 0.238 | 0.542 | 51.8 | 25.9 | 0.083 | 0.213 |
| R | 0.294 | 0.736 | 47.6 | 17.1 | 0.133 | 0.233 |
| S0 | 0.070 | 0.071 | 116.7 | 115.4 | 0.069 | 0.066 |

Per seed, POSITIVE recall: H: 0.87 0.92 0.91 0.93 0.89 0.92 0.93 0.93 0.93 0.92; F: 0.17 0.14 0.15 0.10 0.15 0.16 0.19 0.13 0.12 0.12; L: 0.25 0.23 0.24 0.23 0.21 0.24 0.29 0.28 0.23 0.19; S: 0.27 0.17 0.28 0.19 0.20 0.28 0.27 0.23 0.23 0.26; R: 0.29 0.30 0.29 0.31 0.29 0.32 0.35 0.27 0.29 0.24; S0: 0.03 0.07 0.05 0.09 0.07 0.08 0.09 0.12 0.05 0.05
Per seed, NULL consolidated: H: 60 59 69 62 71 76 74 86 54 75; F: 2 3 2 3 1 5 0 1 2 2; L: 18 24 27 28 24 28 26 34 26 22; S: 22 26 24 27 26 30 25 30 25 24; R: 16 15 22 18 15 22 11 17 17 18; S0: 115 118 114 115 118 113 114 114 117 116

**K1 RANDOM GROWTH STORES:** S recall 0.238 vs 0.8 × H 0.731; S precision 0.542 vs H − 0.05 0.643 → FAIL
**K2 NO INVENTION:** NULL world, S consolidated 25.9 vs H + 2 = 70.6 → PASS
**K3 THE NULL IS BLIND:** S0 recall 0.070 vs bar 0.203 → PASS · beside it, S0 on the SHUFFLED toy stream: 0.061 (AMENDMENT 1's named leak)
K4 reading, S vs L: recall 0.238 vs 0.239 (sign test {'up': 4, 'down': 5, 'p': 1.0}); precision 0.542 vs 0.564 ({'up': 3, 'down': 7, 'p': 0.34375})
K4 reading, R vs S: recall 0.294 vs 0.238 (sign test {'up': 9, 'down': 1, 'p': 0.021484375}); precision 0.736 vs 0.542 ({'up': 10, 'down': 0, 'p': 0.001953125})
K4 reading, L vs F: recall 0.239 vs 0.143 (sign test {'up': 10, 'down': 0, 'p': 0.001953125}); precision 0.564 vs 0.907 ({'up': 0, 'down': 10, 'p': 0.001953125})
