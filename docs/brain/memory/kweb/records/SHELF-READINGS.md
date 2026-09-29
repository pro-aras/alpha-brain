# KW-1 · the organism's shelf (written by tools/web/kw1_shelf.py)

{'words': 15222, 'bad_lines': 0, 'grow': 9133, 'held_out': 6089, 'V_grow': 826, 'B': 1652, 'held_out_strong_pairs': 1522}

G1 recount (seed 1, the growth part): [{'rule': 'H', 'errors': 0, 'first': []}, {'rule': 'F', 'errors': 0, 'first': []}, {'rule': 'L', 'errors': 0, 'first': []}, {'rule': 'S', 'errors': 0, 'first': []}, {'rule': 'R', 'errors': 0, 'first': []}, {'rule': 'S0', 'errors': 0, 'first': []}] · plant caught: True
G3 budget held: True (42 runs)

| rule | runs | consolidated (mean) | enrichment (mean) | per seed | recall of the held-out's strong pairs (mean) |
|---|---|---|---|---|---|
| H | 1 | 560.0 | 1.80 | 1.80 | 0.063 |
| F | 1 | 123.0 | 1.73 | 1.73 | 0.011 |
| L | 1 | 303.0 | 1.70 | 1.70 | 0.032 |
| S | 10 | 346.4 | 1.75 | 1.74 1.70 1.79 1.73 1.76 1.86 1.73 1.66 1.77 1.73 | 0.040 |
| R | 10 | 35.8 | 1.73 | 1.66 2.56 1.77 1.62 1.30 1.90 1.67 1.70 1.63 1.51 | 0.005 |
| S0 | 10 | 64.9 | 1.17 | 0.00 0.00 0.80 0.67 0.00 5.13 0.00 0.00 1.52 3.59 | 0.000 |
| H on the SHUFFLED growth part | 1 | 106.0 | 0.95 | 0.95 | — |
| S on the SHUFFLED growth part | 10 | 83.1 | 0.96 | 0.97 0.90 0.99 0.88 1.06 0.95 0.92 1.12 0.95 0.91 | — |

**K6 IT PREDICTS SPEECH NOT YET HEARD:** S enrichment 1.75 (bar ≥ 2 and ≥ 0.8 × H's 1.80 = 1.44) → FAIL
**K7 THE INSTRUMENT FINDS NOTHING IN A SHUFFLE:** H: consolidated 106.0, enrichment 0.95 → PASS; S: consolidated 83.1, enrichment 0.96 → PASS
K8 reading, H (seed 1) as a web: {'nodes': 251, 'edges': 560, 'mean_degree': 4.46215139442231, 'max_degree': 81, 'clustering': 0.39662170894038823, 'random_clustering': 0.01784860557768924, 'largest_component': 245, 'mean_path': 3.324255603880897, 'random_path': 3.694395774218743, 'hubs': [(81, 'the'), (44, 'a'), (40, 'and'), (30, 'in'), (25, 'to'), (25, 'is'), (24, 'you'), (24, 'it')]}
K8 reading, H (seed 1), its 25 strongest associations: in–the (158), of–the (106), is–the (85), the–to (80), on–the (64), is–it (49), has–the (49), a–is (46), pond–the (42), and–to (41), in–it (40), it–to (39), a–has (38), will–you (35), at–the (35), man–the (33), hen–the (32), girl–illustra (32), the–words (30), is–on (29), do–you (29), letters–the (28), a–with (28), i–will (27), dog–the (27)
K8 reading, S (seed 1) as a web: {'nodes': 188, 'edges': 326, 'mean_degree': 3.4680851063829787, 'max_degree': 63, 'clustering': 0.38584480481826433, 'random_clustering': 0.018545909659802025, 'largest_component': 166, 'mean_path': 3.5350127783862724, 'random_path': 4.210703617565179, 'hubs': [(63, 'the'), (33, 'a'), (22, 'and'), (17, 'is'), (15, 'illustra'), (14, 'to'), (14, 'has'), (13, 'in')]}
K8 reading, S (seed 1), its 25 strongest associations: in–the (156), of–the (106), on–the (64), has–the (48), a–the (45), pond–the (42), is–it (42), a–is (42), the–to (36), a–has (36), will–you (32), man–the (32), girl–illustra (31), at–the (31), the–words (30), is–on (29), hen–the (29), do–you (29), a–and (28), dog–the (27), a–with (27), letters–the (25), illustra–script (25), can–it (25), the–then (24)
