# S1b-1 — the builder's hand-back

*edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 14:17 +0400.*
- **The law:** `PREREG-S1B1.md` (genome-wt-brain3, co-signed by Fable 5.1 at 13:29 and the seat at 13:34, sha `caace482d890bfd655c45907edf0f9ec71aed68a5773e6f6b9670e7dd42cb6b3`, checked before the gate and by the unit), extending `PREREG-R3-TONIGHT.md` §S1a (18250d20…) with AMENDMENT 2 (6e58191f…).
- **The branch:** `scene-s1b1` of `/data/dev/genome-wt-scene`, from 4093ff9.
- **The run root:** `/data/dev/brain-runs/scene-s1b1/`.

## 0 · The verdict
- **THE FIRST GATE: PROCEED (§2).**
  - The eye 3/3.
  - Identity with S1a: 15/15 caches (32,994 rows) and 15/15 item sets; stage −1's text byte-equal.
  - The toy at lr 0.01: 0.994.
  - The lock-in pin: 1.000 vs 0.520.
  - The order-key pin, with its control failing.
  - The verdict re-read equal to S1a's.
  - All four arms beat N-SHUF at 300 scenes.
  - The wiring pin 1.000.
  - No σ dimension at the floor.
- **The full run:** ONE unit `scene-s1b1` from the pinned copy code-dee656e, 14:09:15 → 14:10:17 +0400, Result=success, exit 0, NRestarts 0, 18 arms exit 0.
- **S1b-1 does not pass** (the re-graded report, §4). Per seed:
  - M1 PASS / PASS / PASS
  - M2a FAIL / FAIL / FAIL
  - M2b FAIL / FAIL / FAIL
  - M6 NOT GRADABLE / UNDERPOWERED / PASS
  - M3 PASS / PASS / PASS
  - SPOKEN PASS / PASS / PASS
  - TRUTH FAIL / FAIL / FAIL
  - READ-BACK PASS / PASS / PASS
  - ORDER NOT GRADABLE ×3
  - DECLINE CEILING-BOUND ×3
  - N-SHUF (M1) FAIL / FAIL / PASS
  - N-SHUF (M3) PASS / FAIL / PASS
- **The refutations (§9):**
  - T1 not refuted.
  - The lr law STANDS: A-RW 0.990 / 0.980 / 0.981 against A-RW-LR10's 0.891 / 0.905 / 0.919.
  - T2 not refuted: M3 0.966 / 0.982 / 1.000 — **the words compose on the six held-out pairs.**
  - **T3 REFUTED at all three seeds:** TRUTH 0.671 / 0.716 / 0.600 < 0.80, n ≥ 70, M1 passing.
  - **T4′ — the one prediction the PREREG made in bold failed at every seed.** §3 predicted A-RW's M2b ≥ 0.80 under the diagonal band.
    - The diagonal band reads **0.188 / 0.146 / 0.229**: above (ii)'s Euclidean 0.062 / 0.104 / 0.083 and above S1a's logistic 0.000 / 0.083 / 0.104, but far under the oracle's 0.958 / 0.938 / 0.917.
    - So none of T4′'s three clauses fires. Not «(ii) no worse than the law», because the diagonal helped a little; not «(ii) above the law»; and not «M2b ≥ 0.80», the learner refusing from its own store.
  - One-meeting: n/g, no, no.
- **Beside S1a on the IDENTICAL items (A-RW):**

  | mark | S1a | S1b-1 |
  |---|---|---|
  | M1 | 0.891 / 0.905 / 0.919 | **0.990 / 0.980 / 0.981** |
  | M2a refusal | 0.603 / 0.497 / 0.598 | 0.522 / 0.482 / 0.463 |
  | M2b | 0.000 / 0.083 / 0.104 | 0.188 / 0.146 / 0.229 |
  | M6 | n/g · 0.724 · 0.812 | n/g · 0.759 · 0.719 |

## 1 · What was built (commits on `scene-s1b1`; every step's tests red on its parent, green on the commit)

| commit | what | red on the parent |
|---|---|---|
| 17182a3 | world.py: m3 / speak / decline scenes (twins redrawn; kinds from the index; S1a's split functions untouched); learners.py: Ear (order key, first-heard, exclusion), the diagonal refusal from the store (σ_w, d_w, B_w; young words keep S1a's answer), held words whole, the phrase fit and τ_none at 0.95 on ≥ 2-hypothesis scenes, readings (i) (ii), the σ-floor count, the oracle's hearing and τ_point level/population, `produce()` (the shared mouth); marks.py: M3, SPEAK, DECLINE graders | 4093ff9 (§1.1) |
| dee656e | cache.py: the fresh root, the six test splits, `identity_with` (plain files; a planted change caught); run.py: the arms (A-RW 0.01, A-RW-LR10 0.1, N-SHUF / P-ORACLE-RW 0.01), the questions (SPEAK / DECLINE pointers), the answers (the readings, the mouth, the purple organ fact), the grader, the §7 bars with S1a beside, the §9 refutations, THE FIRST GATE's nine steps, `cache-all`; tools/scene/run_s1b1.sh (the unit) | 4093ff9 (§1.1) |
| c0ad24c | after the unit, report-only: DECLINE's organ clause read as written; T4′'s «spread is the limit» with (ii) ≥ the law (§5) | dee656e: 2 errors |
| 302db7d | tools/scene/diag/s1b1_mechanisms.py (§6, read by no verdict) | — |
| (the final commit) | this hand-back | — |

### 1.1 · Red on 4093ff9
The new and changed test modules (test_world_s1b1, test_learners_s1b1, test_marks_s1b1, test_run, test_cache, test_amend2) were run against 4093ff9's code: `Ran 48 tests … FAILED (failures=1, errors=28)`, log `/data/dev/brain-runs/scene-s1b1/redcheck-4093ff9/red.log`. The 19 that pass there are unchanged S1a-era tests.

## 2 · THE FIRST GATE, as it printed (`/data/dev/brain-runs/scene-s1b1/gate/gate.txt`; 17 s wall at load 4.6, from code-dee656e)

```
== THE FIRST GATE (PREREG-S1B1 §8; each step stops the run on a miss) ==
1. the eye fixture under /usr/bin/python3 from this tree: 3/3 byte-equal (module /data/dev/brain-runs/scene/code-dee656e/brain/__init__.py) → PASS
2. identity with S1a: 15/15 caches carry S1a's specs, canvas shas and glances (rows 32994); 15/15 item sets equal S1a's keys; stage −1's text byte-equal: True → PASS
3. THE TOY at lr 0.01 (no fallback): M1 covered 0.994 (n 169; all 0.857; chance 0.558) ≥ 0.9 → PASS
   P-ORACLE's ε on the toy seed (S1a's rule): 0.0001: 0.960 · 1.000 · 0.001: 0.965 · 1.000 · 0.01: 0.967 · 1.000 · 0.03: 0.967 · 1.000 · 0.1: 0.970 · 1.000 · 0.3: 0.974 · 1.000 → ε 0.3
4. the lock-in pin (machinery toy, seeds 11 / 12, 1,500 scenes): lr 0.01 1.000 · lr 0.1 0.520 (> 0.90 and ≥ 0.10 below) → PASS
5. the ORDER-KEY pin on seed 20261101's first 300 utterances: keys size [0.0, 0.0] < colour [0.3, 0.242, 0.261, 0.202, 0.304] < shape [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]: True; the shuffled control fails: True → PASS
6. S1a's instrument verdict re-read on the fresh caches (LOO on the 113 one-thing gate scenes): shape 1.000 vs 0.7173 (S1a 1.000) · colour 0.894 vs 0.8397 (S1a 0.894) · size 0.938 vs 0.7803 (S1a 0.938) → PROCEED; equal to S1a's: True
7. 6 arms × 300 scenes of seed 20261101, M1 on the graded 2- and 3-thing items (n 229, covered 192; chance 0.544):
   A-RW           0.891 (size2 0.890 · size3 0.893 · pooled all sizes 0.942) · beats N-SHUF: yes
   A-RW-LR10      0.792 (size2 0.801 · size3 0.768 · pooled all sizes 0.890) · a reading arm
   N-SHUF         0.484 (size2 0.500 · size3 0.446 · pooled all sizes 0.727)
   P-ORACLE-RW    0.911 (size2 0.912 · size3 0.911 · pooled all sizes 0.953) · beats N-SHUF: yes
   P-ORACLE       1.000 (size2 1.000 · size3 1.000 · pooled all sizes 1.000) · beats N-SHUF: yes
   ORACLE-TRUTH   1.000 (size2 1.000 · size3 1.000 · pooled all sizes 1.000) · beats N-SHUF: yes
8. the SPEAK road's smoke (A-RW at 300 scenes): spoken 0.949 (n 78) · READ-BACK 1.000 on 74 spoken (the wiring pin = 1.000) · truth 0.757 (no bar at 300) · reasons {'no held word': 3, 'no unique read-back': 1} · DECLINE reasons {'no held word': 4} → PASS
9. per word, the dimensions of σ_w at the 1e-3 floor (A-RW at 300; printed): cross 0 · small 0 · yellow 0 · circle 0 · star 0 · blue 0 · ring 0 · triangle 0 · white 0 · square 0 · green 0 · red 0 · big 0
GATE: PROCEED
```

## 3 · Prices
- **The caches.** Every cache was redrawn by one process (`cache-all`, one at a time), with Test B's two units beside it:
  - 397 CPU-s and 6:38 wall at load 4.4–5.1;
  - ≈ 115–133 CPU-s per world seed, against S1a's 92 idle.
- **The arms.** Priced after Test B ended (14:07:14), at load 1.0:
```
== PRICE (first 2000 scenes, reading points [250, 500, 1000, 2000]; × 5 to 10,000) ==
solo A-RW seed 20261101: cpu 14.8 s, wall 15.2 s → ≈ 1.2 CPU-min per arm-seed
launch shape 6 arms × 3 seeds at once: cpu 285.7 s total (per process A-RW/20261101 22.5, A-RW-LR10/20261101 18.4, N-SHUF/20261101 29.7, P-ORACLE-RW/20261101 10.6, P-ORACLE/20261101 9.0, ORACLE-TRUTH/20261101 9.9, A-RW/20261102 18.9, A-RW-LR10/20261102 18.8, N-SHUF/20261102 27.1, P-ORACLE-RW/20261102 10.1, P-ORACLE/20261102 7.7, ORACLE-TRUTH/20261102 8.9, A-RW/20261103 18.5, A-RW-LR10/20261103 20.9, N-SHUF/20261103 27.8, P-ORACLE-RW/20261103 9.5, P-ORACLE/20261103 8.1, ORACLE-TRUTH/20261103 9.4), wall 32.7 s → ≈ 0.40 CPU-h and ≈ 2.7 min wall for the arms at 10,000
```
- **The unit itself:** the arms took 545 CPU-s (0.15 CPU-h), 62 s wall. Per arm: A-RW 34–44, A-RW-LR10 35–42, N-SHUF 48–52, P-ORACLE-RW 21–25, P-ORACLE 15–17, ORACLE-TRUTH 16–17.
- **Against the declarations:**
  - the PREREG declared ≤ 6 CPU-min for the run; it cost ≈ 9.1 (a 1.5× overrun);
  - the price's linear extrapolation over-read by ≈ 2.6×: the mouth's read-backs do not grow with the stream.

## 4 · The marks, exactly as the grader printed them (`/data/dev/brain-runs/scene-s1b1/report.txt`, re-graded from code-c0ad24c)
The unit's own report is `report-unit-dee656e.txt`.
- **The re-grade is report-only:** every seed's `marks.json` is byte-identical to the unit's (cmp).
- **It differs in exactly 12 lines,** shown below the report:
  - DECLINE ×3: PASS → CEILING-BOUND by the organ clause;
  - the per-seed line;
  - the «all seeds» line: DECLINE PASS → no;
  - the refutation line: T4′'s spread clause yes → no.

```
S1b-1 report · PREREG-S1B1 sha caace482d890bfd655c45907edf0f9ec71aed68a5773e6f6b9670e7dd42cb6b3 · PREREG-R3-TONIGHT 18250d201b6aecbd… · AMEND-2 6e58191fbfd8c758…

== S1b-1 marks · world seed 20261101 (test seed 20261201) · the one meeting seen: False ==
M1 (covered, the graded 2- and 3-thing items) / M3 (covered) by reading point — A-RW-LR10 is S1a's law, a reading:
   arm                    250         500        1000        2000        5000       10000
   A-RW           0.932/0.831 0.922/0.881 0.979/0.864 0.974/0.898 0.984/0.966 0.990/0.966
   A-RW-LR10      0.818/0.763 0.781/0.763 0.786/0.780 0.859/0.847 0.885/0.864 0.891/0.881
   N-SHUF         0.526/0.610 0.510/0.441 0.464/0.508 0.625/0.712 0.417/0.441 0.651/0.542
   P-ORACLE-RW    0.932/0.881 0.948/0.898 0.974/0.881 0.969/0.932 0.990/0.966 0.990/0.983
   P-ORACLE       1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000
   ORACLE-TRUTH   1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000
At 10000 scenes (covered · all), chance and n from A-RW's items:
   M1 graded   cov 0.838 chance 0.544 n 192/229 | A-RW 0.990·0.830 | A-RW-LR10 0.891·0.747 | N-SHUF 0.651·0.546 | P-ORACLE-RW 0.990·0.830 | P-ORACLE 1.000·0.838 | ORACLE-TRUTH 1.000·1.000
   M1 size2    cov 0.889 chance 0.585 n 136/153 | A-RW 0.993·0.882 | A-RW-LR10 0.890·0.791 | N-SHUF 0.676·0.601 | P-ORACLE-RW 0.993·0.882 | P-ORACLE 1.000·0.889 | ORACLE-TRUTH 1.000·1.000
   M1 size3    cov 0.737 chance 0.446 n 56/76 | A-RW 0.982·0.724 | A-RW-LR10 0.893·0.658 | N-SHUF 0.589·0.434 | P-ORACLE-RW 0.982·0.724 | P-ORACLE 1.000·0.737 | ORACLE-TRUTH 1.000·1.000
   M1 size1    cov 1.000 chance 1.000 n 170/170 | A-RW 1.000·1.000 | A-RW-LR10 1.000·1.000 | N-SHUF 1.000·1.000 | P-ORACLE-RW 1.000·1.000 | P-ORACLE 1.000·1.000 | ORACLE-TRUTH 1.000·1.000
   M3 all                    chance 0.559 n 59/60 | A-RW 0.966 | A-RW-LR10 0.881 | N-SHUF 0.542 | P-ORACLE-RW 0.983 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 kind:colour            chance 0.650 n 20/20 | A-RW 1.000 | A-RW-LR10 0.900 | N-SHUF 0.700 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 kind:shape             chance 0.600 n 20/20 | A-RW 0.950 | A-RW-LR10 0.850 | N-SHUF 0.400 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 kind:both              chance 0.421 n 19/20 | A-RW 0.947 | A-RW-LR10 0.895 | N-SHUF 0.526 | P-ORACLE-RW 0.947 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 size2                  chance 0.625 n 40/40 | A-RW 0.975 | A-RW-LR10 0.875 | N-SHUF 0.550 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 size3                  chance 0.421 n 19/20 | A-RW 0.947 | A-RW-LR10 0.895 | N-SHUF 0.526 | P-ORACLE-RW 0.947 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:circle-blue       chance 0.700 n 10/10 | A-RW 1.000 | A-RW-LR10 1.000 | N-SHUF 0.700 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:cross-yellow      chance 0.537 n 9/10 | A-RW 1.000 | A-RW-LR10 0.778 | N-SHUF 0.333 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:square-red        chance 0.567 n 10/10 | A-RW 0.900 | A-RW-LR10 0.700 | N-SHUF 0.600 | P-ORACLE-RW 0.900 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:square-white      chance 0.583 n 10/10 | A-RW 1.000 | A-RW-LR10 1.000 | N-SHUF 0.700 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:star-red          chance 0.433 n 10/10 | A-RW 1.000 | A-RW-LR10 1.000 | N-SHUF 0.500 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:triangle-yellow   chance 0.533 n 10/10 | A-RW 0.900 | A-RW-LR10 0.800 | N-SHUF 0.400 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   A-RW           M2a refusal 0.522 false 0.094 [(i) 0.892/0.068 · (ii) 0.265/0.094] · M2b 0.188 (idk 0.083; diamond 0.000) [(i) 0.208 · (ii) 0.062] · M6 NOT GRADABLE · NAME emits the true word: shape 0.947 colour 0.935 size 0.929 [(i) 0.953/0.947/0.888]
                  SPEAK spoken 0.974 (n 78; all 0.792) · truth 0.671 (n 76; seen 0.711; ×spoken 0.654) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 2} · DECLINE 0.778 (n 36; A spoken 1.000 truth 0.864; B decline 0.143)
   A-RW-LR10      M2a refusal 0.490 false 0.104 [(i) 0.603/0.099 · (ii) 0.255/0.094] · M2b 0.188 (idk 0.083; diamond 0.000) [(i) 0.000 · (ii) 0.062] · M6 NOT GRADABLE · NAME emits the true word: shape 0.935 colour 0.918 size 0.929 [(i) 0.941/0.894/0.888]
                  SPEAK spoken 0.974 (n 78; all 0.792) · truth 0.579 (n 76; seen 0.632; ×spoken 0.564) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 2} · DECLINE 0.778 (n 36; A spoken 1.000 truth 0.636; B decline 0.143)
   N-SHUF         M2a refusal 0.175 false 0.115 [(i) 0.068/0.083 · (ii) 0.170/0.109] · M2b 0.104 (idk 0.104; diamond 0.000) [(i) 0.000 · (ii) 0.104] · M6 NOT GRADABLE · NAME emits the true word: shape 0.918 colour 0.912 size 0.924 [(i) 0.941/0.741/0.876]
                  SPEAK spoken 0.885 (n 78; all 0.719) · truth 0.217 (n 69; seen 0.232; ×spoken 0.192) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 7, 'none fired': 2} · DECLINE 0.722 (n 36; A spoken 0.955 truth 0.095; B decline 0.214)
   P-ORACLE-RW    M2a refusal 0.675 false 0.031 [(i) 0.858/0.036 · (ii) 0.250/0.089] · M2b 0.667 (idk 0.208; diamond 0.500) [(i) 0.500 · (ii) 0.083] · M6 NOT GRADABLE · NAME emits the true word: shape 0.918 colour 0.918 size 0.918 [(i) 0.924/0.924/0.924]
                  SPEAK spoken 0.962 (n 78; all 0.781) · truth 0.840 (n 75; seen 0.893; ×spoken 0.808) · read-back 1.000 · order 1.000 (n 1) · lengths {'1': 0.9866666666666667, '2': 0.013333333333333334, '3': 0.0} · reasons {'no held word': 3} · DECLINE 0.889 (n 36; A spoken 1.000 truth 0.818; B decline 0.214)
   P-ORACLE       M2a refusal 1.000 false 0.042 · M2b 0.958 (idk 0.688; diamond 0.500) · M6 NOT GRADABLE · NAME emits the true word: shape 0.935 colour 0.941 size 0.941
                  SPEAK spoken 0.885 (n 78; all 0.719) · truth 0.884 (n 69; seen 0.986; ×spoken 0.782) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 8, 'no unique read-back': 1} · DECLINE 0.722 (n 36; A spoken 0.909 truth 0.750; B decline 0.357)
   ORACLE-TRUTH   M2a refusal 1.000 false 0.047 · M2b 0.938 (idk 0.729; diamond 0.625) · M6 NOT GRADABLE · NAME emits the true word: shape 0.924 colour 0.924 size 0.929
                  SPEAK spoken 0.910 (n 78; all 0.906) · truth 0.972 (n 71; seen 0.972; ×spoken 0.885) · read-back 1.000 · order 1.000 (n 1) · lengths {'1': 0.9859154929577465, '2': 0.014084507042253521, '3': 0.0} · reasons {'no held word': 7} · DECLINE 0.722 (n 36; A spoken 1.000 truth 0.818; B decline 0.286)
   the organ fact (P-ORACLE's colour d_w / B_w of the purple targets): blue mean 0.85 inside 0.86 · green mean 1.33 inside 0.00 · red mean 0.95 inside 0.69 · white mean 1.18 inside 0.31 · yellow mean 1.38 inside 0.00

== S1b-1 marks · world seed 20261102 (test seed 20261202) · the one meeting seen: True ==
M1 (covered, the graded 2- and 3-thing items) / M3 (covered) by reading point — A-RW-LR10 is S1a's law, a reading:
   arm                    250         500        1000        2000        5000       10000
   A-RW           0.871/0.789 0.940/0.860 0.965/0.965 0.980/0.982 0.995/0.982 0.980/0.982
   A-RW-LR10      0.791/0.667 0.811/0.719 0.826/0.772 0.856/0.895 0.891/0.930 0.905/0.895
   N-SHUF         0.562/0.561 0.507/0.544 0.597/0.614 0.512/0.649 0.493/0.614 0.597/0.667
   P-ORACLE-RW    0.905/0.825 0.940/0.842 0.990/0.982 0.995/0.982 0.995/0.982 0.995/1.000
   P-ORACLE       1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000
   ORACLE-TRUTH   1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000
At 10000 scenes (covered · all), chance and n from A-RW's items:
   M1 graded   cov 0.820 chance 0.543 n 201/245 | A-RW 0.980·0.804 | A-RW-LR10 0.905·0.743 | N-SHUF 0.597·0.490 | P-ORACLE-RW 0.995·0.816 | P-ORACLE 1.000·0.820 | ORACLE-TRUTH 1.000·1.000
   M1 size2    cov 0.879 chance 0.579 n 152/173 | A-RW 0.987·0.867 | A-RW-LR10 0.895·0.786 | N-SHUF 0.638·0.561 | P-ORACLE-RW 1.000·0.879 | P-ORACLE 1.000·0.879 | ORACLE-TRUTH 1.000·1.000
   M1 size3    cov 0.681 chance 0.432 n 49/72 | A-RW 0.959·0.653 | A-RW-LR10 0.939·0.639 | N-SHUF 0.469·0.319 | P-ORACLE-RW 0.980·0.667 | P-ORACLE 1.000·0.681 | ORACLE-TRUTH 1.000·1.000
   M1 size1    cov 1.000 chance 1.000 n 153/153 | A-RW 1.000·1.000 | A-RW-LR10 1.000·1.000 | N-SHUF 1.000·1.000 | P-ORACLE-RW 1.000·1.000 | P-ORACLE 1.000·1.000 | ORACLE-TRUTH 1.000·1.000
   M3 all                    chance 0.541 n 57/60 | A-RW 0.982 | A-RW-LR10 0.895 | N-SHUF 0.667 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 kind:colour            chance 0.575 n 20/20 | A-RW 1.000 | A-RW-LR10 0.900 | N-SHUF 0.650 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 kind:shape             chance 0.550 n 20/20 | A-RW 0.950 | A-RW-LR10 1.000 | N-SHUF 0.800 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 kind:both              chance 0.490 n 17/20 | A-RW 1.000 | A-RW-LR10 0.765 | N-SHUF 0.529 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 size2                  chance 0.562 n 40/40 | A-RW 0.975 | A-RW-LR10 0.950 | N-SHUF 0.725 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 size3                  chance 0.490 n 17/20 | A-RW 1.000 | A-RW-LR10 0.765 | N-SHUF 0.529 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:circle-blue       chance 0.481 n 9/10 | A-RW 1.000 | A-RW-LR10 0.889 | N-SHUF 0.333 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:cross-yellow      chance 0.600 n 10/10 | A-RW 1.000 | A-RW-LR10 1.000 | N-SHUF 0.900 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:square-red        chance 0.583 n 10/10 | A-RW 1.000 | A-RW-LR10 0.700 | N-SHUF 0.600 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:square-white      chance 0.537 n 9/10 | A-RW 1.000 | A-RW-LR10 1.000 | N-SHUF 0.889 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:star-red          chance 0.556 n 9/10 | A-RW 1.000 | A-RW-LR10 0.778 | N-SHUF 0.889 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:triangle-yellow   chance 0.483 n 10/10 | A-RW 0.900 | A-RW-LR10 1.000 | N-SHUF 0.400 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   A-RW           M2a refusal 0.482 false 0.065 [(i) 0.845/0.055 · (ii) 0.295/0.080] · M2b 0.146 (idk 0.125; diamond 0.000) [(i) 0.146 · (ii) 0.104] · M6 0.759 (n 29) · NAME emits the true word: shape 0.954 colour 0.935 size 0.902 [(i) 0.935/0.954/0.882]
                  SPEAK spoken 0.925 (n 80; all 0.771) · truth 0.716 (n 74; seen 0.757; ×spoken 0.662) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 5, 'no unique read-back': 1} · DECLINE 0.806 (n 36; A spoken 0.900 truth 0.722; B decline 0.188)
   A-RW-LR10      M2a refusal 0.475 false 0.070 [(i) 0.497/0.075 · (ii) 0.300/0.080] · M2b 0.146 (idk 0.146; diamond 0.000) [(i) 0.083 · (ii) 0.104] · M6 0.724 (n 29) · NAME emits the true word: shape 0.954 colour 0.902 size 0.889 [(i) 0.935/0.856/0.863]
                  SPEAK spoken 0.912 (n 80; all 0.760) · truth 0.603 (n 73; seen 0.616; ×spoken 0.550) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 5, 'no unique read-back': 2} · DECLINE 0.778 (n 36; A spoken 0.900 truth 0.667; B decline 0.125)
   N-SHUF         M2a refusal 0.165 false 0.090 [(i) 0.058/0.060 · (ii) 0.163/0.080] · M2b 0.188 (idk 0.167; diamond 0.000) [(i) 0.000 · (ii) 0.188] · M6 0.276 (n 29) · NAME emits the true word: shape 0.876 colour 0.889 size 0.882 [(i) 0.915/0.719/0.837]
                  SPEAK spoken 0.838 (n 80; all 0.698) · truth 0.149 (n 67; seen 0.164; ×spoken 0.125) · read-back 1.000 · order 1.000 (n 1) · lengths {'1': 0.9850746268656716, '2': 0.0, '3': 0.014925373134328358} · reasons {'no held word': 8, 'none fired': 5} · DECLINE 0.833 (n 36; A spoken 0.900 truth 0.333; B decline 0.188)
   P-ORACLE-RW    M2a refusal 0.632 false 0.035 [(i) 0.845/0.035 · (ii) 0.280/0.085] · M2b 0.667 (idk 0.229; diamond 0.125) [(i) 0.583 · (ii) 0.104] · M6 0.724 (n 29) · NAME emits the true word: shape 0.935 colour 0.902 size 0.895 [(i) 0.902/0.902/0.837]
                  SPEAK spoken 0.925 (n 80; all 0.771) · truth 0.797 (n 74; seen 0.892; ×spoken 0.738) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 6} · DECLINE 0.972 (n 36; A spoken 0.850 truth 0.882; B decline 0.312)
   P-ORACLE       M2a refusal 0.998 false 0.065 · M2b 0.938 (idk 0.688; diamond 0.500) · M6 1.000 (n 29) · NAME emits the true word: shape 0.961 colour 0.902 size 0.928
                  SPEAK spoken 0.887 (n 80; all 0.740) · truth 0.887 (n 71; seen 1.000; ×spoken 0.787) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 9} · DECLINE 0.556 (n 36; A spoken 0.800 truth 0.438; B decline 0.375)
   ORACLE-TRUTH   M2a refusal 1.000 false 0.060 · M2b 0.917 (idk 0.750; diamond 0.750) · M6 1.000 (n 29) · NAME emits the true word: shape 0.895 colour 0.915 size 0.895
                  SPEAK spoken 0.912 (n 80; all 0.906) · truth 0.986 (n 73; seen 1.000; ×spoken 0.900) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 7} · DECLINE 0.722 (n 36; A spoken 0.650 truth 0.615; B decline 0.312)
   the organ fact (P-ORACLE's colour d_w / B_w of the purple targets): blue mean 0.95 inside 0.69 · green mean 1.50 inside 0.00 · red mean 1.05 inside 0.50 · white mean 1.36 inside 0.11 · yellow mean 1.53 inside 0.00

== S1b-1 marks · world seed 20261103 (test seed 20261203) · the one meeting seen: True ==
M1 (covered, the graded 2- and 3-thing items) / M3 (covered) by reading point — A-RW-LR10 is S1a's law, a reading:
   arm                    250         500        1000        2000        5000       10000
   A-RW           0.929/0.909 0.953/0.873 0.957/0.927 0.986/1.000 0.986/1.000 0.981/1.000
   A-RW-LR10      0.806/0.800 0.853/0.873 0.796/0.818 0.900/0.945 0.905/0.982 0.919/0.891
   N-SHUF         0.550/0.527 0.445/0.527 0.460/0.527 0.445/0.491 0.531/0.636 0.469/0.509
   P-ORACLE-RW    0.943/0.927 0.962/0.891 0.962/0.945 0.986/1.000 0.986/0.982 0.995/1.000
   P-ORACLE       1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000
   ORACLE-TRUTH   1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000 1.000/1.000
At 10000 scenes (covered · all), chance and n from A-RW's items:
   M1 graded   cov 0.854 chance 0.540 n 211/247 | A-RW 0.981·0.838 | A-RW-LR10 0.919·0.785 | N-SHUF 0.469·0.401 | P-ORACLE-RW 0.995·0.850 | P-ORACLE 1.000·0.854 | ORACLE-TRUTH 1.000·1.000
   M1 size2    cov 0.892 chance 0.581 n 148/166 | A-RW 0.980·0.873 | A-RW-LR10 0.932·0.831 | N-SHUF 0.520·0.464 | P-ORACLE-RW 0.993·0.886 | P-ORACLE 1.000·0.892 | ORACLE-TRUTH 1.000·1.000
   M1 size3    cov 0.778 chance 0.444 n 63/81 | A-RW 0.984·0.765 | A-RW-LR10 0.889·0.691 | N-SHUF 0.349·0.272 | P-ORACLE-RW 1.000·0.778 | P-ORACLE 1.000·0.778 | ORACLE-TRUTH 1.000·1.000
   M1 size1    cov 1.000 chance 1.000 n 149/149 | A-RW 1.000·1.000 | A-RW-LR10 1.000·1.000 | N-SHUF 1.000·1.000 | P-ORACLE-RW 1.000·1.000 | P-ORACLE 1.000·1.000 | ORACLE-TRUTH 1.000·1.000
   M3 all                    chance 0.542 n 55/60 | A-RW 1.000 | A-RW-LR10 0.891 | N-SHUF 0.509 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 kind:colour            chance 0.550 n 20/20 | A-RW 1.000 | A-RW-LR10 0.900 | N-SHUF 0.700 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 kind:shape             chance 0.550 n 20/20 | A-RW 1.000 | A-RW-LR10 0.950 | N-SHUF 0.400 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 kind:both              chance 0.522 n 15/20 | A-RW 1.000 | A-RW-LR10 0.800 | N-SHUF 0.400 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 size2                  chance 0.550 n 40/40 | A-RW 1.000 | A-RW-LR10 0.925 | N-SHUF 0.550 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 size3                  chance 0.522 n 15/20 | A-RW 1.000 | A-RW-LR10 0.800 | N-SHUF 0.400 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:circle-blue       chance 0.519 n 9/10 | A-RW 1.000 | A-RW-LR10 1.000 | N-SHUF 0.667 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:cross-yellow      chance 0.611 n 9/10 | A-RW 1.000 | A-RW-LR10 0.889 | N-SHUF 0.667 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:square-red        chance 0.556 n 9/10 | A-RW 1.000 | A-RW-LR10 0.778 | N-SHUF 0.667 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:square-white      chance 0.550 n 10/10 | A-RW 1.000 | A-RW-LR10 1.000 | N-SHUF 0.200 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:star-red          chance 0.479 n 8/10 | A-RW 1.000 | A-RW-LR10 0.875 | N-SHUF 0.375 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   M3 pair:triangle-yellow   chance 0.533 n 10/10 | A-RW 1.000 | A-RW-LR10 0.800 | N-SHUF 0.500 | P-ORACLE-RW 1.000 | P-ORACLE 1.000 | ORACLE-TRUTH 1.000
   A-RW           M2a refusal 0.463 false 0.062 [(i) 0.880/0.057 · (ii) 0.297/0.062] · M2b 0.229 (idk 0.125; diamond 0.125) [(i) 0.062 · (ii) 0.083] · M6 0.719 (n 32) · NAME emits the true word: shape 0.966 colour 0.960 size 0.966 [(i) 0.966/0.946/0.899]
                  SPEAK spoken 0.972 (n 72; all 0.729) · truth 0.600 (n 70; seen 0.657; ×spoken 0.583) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 2} · DECLINE 0.706 (n 34; A spoken 1.000 truth 0.737; B decline 0.067)
   A-RW-LR10      M2a refusal 0.455 false 0.057 [(i) 0.598/0.043 · (ii) 0.290/0.062] · M2b 0.229 (idk 0.125; diamond 0.125) [(i) 0.104 · (ii) 0.083] · M6 0.812 (n 32) · NAME emits the true word: shape 0.960 colour 0.960 size 0.966 [(i) 0.946/0.926/0.893]
                  SPEAK spoken 0.972 (n 72; all 0.729) · truth 0.600 (n 70; seen 0.643; ×spoken 0.583) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 2} · DECLINE 0.618 (n 34; A spoken 0.947 truth 0.444; B decline 0.067)
   N-SHUF         M2a refusal 0.140 false 0.071 [(i) 0.043/0.100 · (ii) 0.135/0.071] · M2b 0.125 (idk 0.125; diamond 0.125) [(i) 0.000 · (ii) 0.125] · M6 0.562 (n 32) · NAME emits the true word: shape 0.946 colour 0.933 size 0.946 [(i) 0.886/0.765/0.765]
                  SPEAK spoken 0.944 (n 72; all 0.708) · truth 0.176 (n 68; seen 0.176; ×spoken 0.167) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 3, 'none fired': 1} · DECLINE 0.618 (n 34; A spoken 0.842 truth 0.062; B decline 0.067)
   P-ORACLE-RW    M2a refusal 0.640 false 0.024 [(i) 0.882/0.028 · (ii) 0.282/0.047] · M2b 0.625 (idk 0.146; diamond 0.250) [(i) 0.354 · (ii) 0.104] · M6 0.750 (n 32) · NAME emits the true word: shape 0.919 colour 0.953 size 0.953 [(i) 0.913/0.913/0.899]
                  SPEAK spoken 0.972 (n 72; all 0.729) · truth 0.686 (n 70; seen 0.757; ×spoken 0.667) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 2} · DECLINE 1.000 (n 34; A spoken 0.947 truth 0.833; B decline 0.267)
   P-ORACLE       M2a refusal 0.995 false 0.081 · M2b 0.917 (idk 0.688; diamond 0.625) · M6 1.000 (n 32) · NAME emits the true word: shape 0.960 colour 0.960 size 0.960
                  SPEAK spoken 0.903 (n 72; all 0.677) · truth 0.846 (n 65; seen 0.969; ×spoken 0.764) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 7} · DECLINE 0.618 (n 34; A spoken 0.895 truth 0.706; B decline 0.133)
   ORACLE-TRUTH   M2a refusal 1.000 false 0.076 · M2b 0.938 (idk 0.792; diamond 0.875) · M6 1.000 (n 32) · NAME emits the true word: shape 0.913 colour 0.913 size 0.913
                  SPEAK spoken 0.903 (n 72; all 0.896) · truth 0.954 (n 65; seen 0.985; ×spoken 0.861) · read-back 1.000 · order   —   (n 0) · lengths {'1': 1.0, '2': 0.0, '3': 0.0} · reasons {'no held word': 6, 'no unique read-back': 1} · DECLINE 0.647 (n 34; A spoken 0.947 truth 0.778; B decline 0.067)
   the organ fact (P-ORACLE's colour d_w / B_w of the purple targets): blue mean 0.88 inside 0.82 · green mean 1.41 inside 0.06 · red mean 0.99 inside 0.62 · white mean 1.26 inside 0.21 · yellow mean 1.49 inside 0.00

== S1b-1 BARS at 10,000 scenes (A-RW, the law lr 0.01; P-ORACLE beside every mark; S1a's A-RW on the identical items beside) ==
20261101 M1 0.990 (all 0.830; n 192/229; chance 0.544) bars ≥ 0.891 (0.90 × P-ORACLE-RW 0.990) and ≥ 0.800 (0.80 × P-ORACLE 1.000) → PASS · A-RW-LR10 0.891 · S1a 0.891
          M1 size2: 0.993 (n 136, chance 0.585) → PASS · A-RW-LR10 0.890
          M1 size3: 0.982 (n 56, chance 0.446) → PASS · A-RW-LR10 0.893
          M2a refusal 0.522 (n 400) · false refusal 0.094 (n 192; expected 0.05) · P-ORACLE 1.000 / 0.042 → FAIL (the learner fails: refusal; whole-bar: FAIL) · (i) 0.892/0.068 · (ii) 0.265/0.094 · A-RW-LR10 0.490/0.104 · S1a 0.603/0.099
          M2b 0.188 (n 48; «I don't know» 0.083) · P-ORACLE 0.958 → FAIL · (i) 0.208 · (ii) 0.062 · A-RW-LR10 0.188 · S1a 0.000 · diamond (apart) 0.000 · P-ORACLE 0.500 · shape words said {'circle': 5, 'cross': 25, 'dax': 2, 'ring': 35, 'square': 4, 'star': 7, 'triangle': 10}
          M6 NOT GRADABLE — the meeting was never seen (0 fixations on the dax at its scene) · S1a 0.481
          M3 0.966 (all 0.950; n 59/60; chance 0.559) bar ≥ 0.800 (0.80 × P-ORACLE 1.000) → PASS · kinds colour 1.000 shape 0.950 both 0.947 · P-ORACLE-RW 0.983 (0.90× 0.885, a reading) · A-RW-LR10 0.881
          SPOKEN 0.974 (n 78) ≥ 0.708 (0.80 × P-ORACLE 0.885) → PASS · reasons {'no held word': 2} · A-RW-LR10 0.974 · N-SHUF 0.885
          TRUTH 0.671 (n 76) ≥ 0.796 (0.90 × P-ORACLE 0.884, n 69) → FAIL · seen 0.711 · ×spoken 0.654 (P-ORACLE 0.782) · A-RW-LR10 0.579 · N-SHUF 0.217 vs a random true phrase 0.034
          READ-BACK 1.000 (n 76; the wiring pin = 1.000) → PASS · ORDER   —   (n 0) ≥   —   (0.95 × P-ORACLE   —  ) → NOT GRADABLE · lengths {'1': 1.0, '2': 0.0, '3': 0.0} vs the parent's {'1': 0.25, '2': 0.5, '3': 0.25}
          DECLINE 0.778 (n 36) ≥ 0.650 (0.90 × P-ORACLE 0.722; the fraction met) → CEILING-BOUND (the organ clause: P-ORACLE < 0.80 — purple inside a trained colour's band) · kind A spoken 1.000 truth 0.864 · kind B decline 0.143 · A-RW-LR10 0.778
          N-SHUF M1 0.651 ≤ 0.594 → FAIL · M3 0.542 ≤ 0.609 → PASS
20261102 M1 0.980 (all 0.804; n 201/245; chance 0.543) bars ≥ 0.896 (0.90 × P-ORACLE-RW 0.995) and ≥ 0.800 (0.80 × P-ORACLE 1.000) → PASS · A-RW-LR10 0.905 · S1a 0.905
          M1 size2: 0.987 (n 152, chance 0.579) → PASS · A-RW-LR10 0.895
          M1 size3: 0.959 (n 49, chance 0.432) → PASS · A-RW-LR10 0.939
          M2a refusal 0.482 (n 400) · false refusal 0.065 (n 201; expected 0.05) · P-ORACLE 0.998 / 0.065 → FAIL (the learner fails: refusal; whole-bar: FAIL) · (i) 0.845/0.055 · (ii) 0.295/0.080 · A-RW-LR10 0.475/0.070 · S1a 0.497/0.075
          M2b 0.146 (n 48; «I don't know» 0.125) · P-ORACLE 0.938 → FAIL · (i) 0.146 · (ii) 0.104 · A-RW-LR10 0.146 · S1a 0.083 · diamond (apart) 0.000 · P-ORACLE 0.500 · shape words said {'circle': 6, 'cross': 26, 'dax': 2, 'ring': 39, 'square': 5, 'star': 9, 'triangle': 12}
          M6 0.759 (all 0.524; n 29/42; chance 0.460) · P-ORACLE 1.000 → UNDERPOWERED · S1a 0.724
          M3 0.982 (all 0.933; n 57/60; chance 0.541) bar ≥ 0.800 (0.80 × P-ORACLE 1.000) → PASS · kinds colour 1.000 shape 0.950 both 1.000 · P-ORACLE-RW 1.000 (0.90× 0.900, a reading) · A-RW-LR10 0.895
          SPOKEN 0.925 (n 80) ≥ 0.710 (0.80 × P-ORACLE 0.887) → PASS · reasons {'no held word': 5, 'no unique read-back': 1} · A-RW-LR10 0.912 · N-SHUF 0.838
          TRUTH 0.716 (n 74) ≥ 0.799 (0.90 × P-ORACLE 0.887, n 71) → FAIL · seen 0.757 · ×spoken 0.662 (P-ORACLE 0.787) · A-RW-LR10 0.603 · N-SHUF 0.149 vs a random true phrase 0.034
          READ-BACK 1.000 (n 74; the wiring pin = 1.000) → PASS · ORDER   —   (n 0) ≥   —   (0.95 × P-ORACLE   —  ) → NOT GRADABLE · lengths {'1': 1.0, '2': 0.0, '3': 0.0} vs the parent's {'1': 0.25, '2': 0.5, '3': 0.25}
          DECLINE 0.806 (n 36) ≥ 0.500 (0.90 × P-ORACLE 0.556; the fraction met) → CEILING-BOUND (the organ clause: P-ORACLE < 0.80 — purple inside a trained colour's band) · kind A spoken 0.900 truth 0.722 · kind B decline 0.188 · A-RW-LR10 0.778
          N-SHUF M1 0.597 ≤ 0.593 → FAIL · M3 0.667 ≤ 0.591 → FAIL
20261103 M1 0.981 (all 0.838; n 211/247; chance 0.540) bars ≥ 0.896 (0.90 × P-ORACLE-RW 0.995) and ≥ 0.800 (0.80 × P-ORACLE 1.000) → PASS · A-RW-LR10 0.919 · S1a 0.919
          M1 size2: 0.980 (n 148, chance 0.581) → PASS · A-RW-LR10 0.932
          M1 size3: 0.984 (n 63, chance 0.444) → PASS · A-RW-LR10 0.889
          M2a refusal 0.463 (n 400) · false refusal 0.062 (n 211; expected 0.05) · P-ORACLE 0.995 / 0.081 → FAIL (the learner fails: refusal; whole-bar: FAIL) · (i) 0.880/0.057 · (ii) 0.297/0.062 · A-RW-LR10 0.455/0.057 · S1a 0.598/0.043
          M2b 0.229 (n 48; «I don't know» 0.125) · P-ORACLE 0.917 → FAIL · (i) 0.062 · (ii) 0.083 · A-RW-LR10 0.229 · S1a 0.104 · diamond (apart) 0.125 · P-ORACLE 0.625 · shape words said {'circle': 7, 'cross': 21, 'dax': 8, 'ring': 35, 'square': 4, 'star': 8, 'triangle': 10}
          M6 0.719 (all 0.548; n 32/42; chance 0.474) · P-ORACLE 1.000 → PASS · S1a 0.812
          M3 1.000 (all 0.917; n 55/60; chance 0.542) bar ≥ 0.800 (0.80 × P-ORACLE 1.000) → PASS · kinds colour 1.000 shape 1.000 both 1.000 · P-ORACLE-RW 1.000 (0.90× 0.900, a reading) · A-RW-LR10 0.891
          SPOKEN 0.972 (n 72) ≥ 0.722 (0.80 × P-ORACLE 0.903) → PASS · reasons {'no held word': 2} · A-RW-LR10 0.972 · N-SHUF 0.944
          TRUTH 0.600 (n 70) ≥ 0.762 (0.90 × P-ORACLE 0.846, n 65) → FAIL · seen 0.657 · ×spoken 0.583 (P-ORACLE 0.764) · A-RW-LR10 0.600 · N-SHUF 0.176 vs a random true phrase 0.033
          READ-BACK 1.000 (n 70; the wiring pin = 1.000) → PASS · ORDER   —   (n 0) ≥   —   (0.95 × P-ORACLE   —  ) → NOT GRADABLE · lengths {'1': 1.0, '2': 0.0, '3': 0.0} vs the parent's {'1': 0.25, '2': 0.5, '3': 0.25}
          DECLINE 0.706 (n 34) ≥ 0.556 (0.90 × P-ORACLE 0.618; the fraction met) → CEILING-BOUND (the organ clause: P-ORACLE < 0.80 — purple inside a trained colour's band) · kind A spoken 1.000 truth 0.737 · kind B decline 0.067 · A-RW-LR10 0.618
          N-SHUF M1 0.469 ≤ 0.590 → PASS · M3 0.509 ≤ 0.592 → PASS
per seed: M1 PASS/PASS/PASS · M2a FAIL/FAIL/FAIL · M2b FAIL/FAIL/FAIL · M6 NOT GRADABLE/UNDERPOWERED/PASS · M3 PASS/PASS/PASS · SPOKEN PASS/PASS/PASS · TRUTH FAIL/FAIL/FAIL · READ-BACK PASS/PASS/PASS · ORDER NOT GRADABLE/NOT GRADABLE/NOT GRADABLE · DECLINE CEILING-BOUND/CEILING-BOUND/CEILING-BOUND · N-SHUF FAIL/FAIL/PASS · N-SHUF-M3 PASS/FAIL/PASS
every bar at all 3 seeds (M6 where the meeting was seen: 20261102, 20261103): M1 PASS · M2a no · M2b no · M6 no · M3 PASS · SPOKEN PASS · TRUTH no · READ-BACK PASS · ORDER no · DECLINE no · N-SHUF no · N-SHUF-M3 no → S1b-1 does not pass
refutations (§9): T1 20261101:no 20261102:no 20261103:no · the lr law (A-RW below A-RW-LR10 on M1 at ≥ 2 seeds) stands (20261101:not below 20261102:not below 20261103:not below) · T2 20261101:no 20261102:no 20261103:no · T3 20261101:REFUTED 20261102:REFUTED 20261103:REFUTED · T4′ spread-is-the-limit 20261101:no 20261102:no 20261103:no · (ii) above the law by ≥ 0.05 at ≥ 2 seeds: no · the learner refuses (M2b ≥ 0.80) 20261101:no 20261102:no 20261103:no · one-meeting 20261101:n/g 20261102:no 20261103:no
```

The diff, the unit's report against the re-graded one:

```
134c134
<           DECLINE 0.778 (n 36) ≥ 0.650 (0.90 × P-ORACLE 0.722) → PASS · kind A spoken 1.000 truth 0.864 · kind B decline 0.143 · A-RW-LR10 0.778
---
>           DECLINE 0.778 (n 36) ≥ 0.650 (0.90 × P-ORACLE 0.722; the fraction met) → CEILING-BOUND (the organ clause: P-ORACLE < 0.80 — purple inside a trained colour's band) · kind A spoken 1.000 truth 0.864 · kind B decline 0.143 · A-RW-LR10 0.778
146c146
<           DECLINE 0.806 (n 36) ≥ 0.500 (0.90 × P-ORACLE 0.556) → PASS · kind A spoken 0.900 truth 0.722 · kind B decline 0.188 · A-RW-LR10 0.778
---
>           DECLINE 0.806 (n 36) ≥ 0.500 (0.90 × P-ORACLE 0.556; the fraction met) → CEILING-BOUND (the organ clause: P-ORACLE < 0.80 — purple inside a trained colour's band) · kind A spoken 0.900 truth 0.722 · kind B decline 0.188 · A-RW-LR10 0.778
158c158
<           DECLINE 0.706 (n 34) ≥ 0.556 (0.90 × P-ORACLE 0.618) → PASS · kind A spoken 1.000 truth 0.737 · kind B decline 0.067 · A-RW-LR10 0.618
---
>           DECLINE 0.706 (n 34) ≥ 0.556 (0.90 × P-ORACLE 0.618; the fraction met) → CEILING-BOUND (the organ clause: P-ORACLE < 0.80 — purple inside a trained colour's band) · kind A spoken 1.000 truth 0.737 · kind B decline 0.067 · A-RW-LR10 0.618
160,162c160,162
< per seed: M1 PASS/PASS/PASS · M2a FAIL/FAIL/FAIL · M2b FAIL/FAIL/FAIL · M6 NOT GRADABLE/UNDERPOWERED/PASS · M3 PASS/PASS/PASS · SPOKEN PASS/PASS/PASS · TRUTH FAIL/FAIL/FAIL · READ-BACK PASS/PASS/PASS · ORDER NOT GRADABLE/NOT GRADABLE/NOT GRADABLE · DECLINE PASS/PASS/PASS · N-SHUF FAIL/FAIL/PASS · N-SHUF-M3 PASS/FAIL/PASS
< every bar at all 3 seeds (M6 where the meeting was seen: 20261102, 20261103): M1 PASS · M2a no · M2b no · M6 no · M3 PASS · SPOKEN PASS · TRUTH no · READ-BACK PASS · ORDER no · DECLINE PASS · N-SHUF no · N-SHUF-M3 no → S1b-1 does not pass
< refutations (§9): T1 20261101:no 20261102:no 20261103:no · the lr law (A-RW below A-RW-LR10 on M1 at ≥ 2 seeds) stands (20261101:not below 20261102:not below 20261103:not below) · T2 20261101:no 20261102:no 20261103:no · T3 20261101:REFUTED 20261102:REFUTED 20261103:REFUTED · T4′ spread-is-the-limit 20261101:yes 20261102:yes 20261103:yes · (ii) above the law by ≥ 0.05 at ≥ 2 seeds: no · the learner refuses (M2b ≥ 0.80) 20261101:no 20261102:no 20261103:no · one-meeting 20261101:n/g 20261102:no 20261103:no
---
> per seed: M1 PASS/PASS/PASS · M2a FAIL/FAIL/FAIL · M2b FAIL/FAIL/FAIL · M6 NOT GRADABLE/UNDERPOWERED/PASS · M3 PASS/PASS/PASS · SPOKEN PASS/PASS/PASS · TRUTH FAIL/FAIL/FAIL · READ-BACK PASS/PASS/PASS · ORDER NOT GRADABLE/NOT GRADABLE/NOT GRADABLE · DECLINE CEILING-BOUND/CEILING-BOUND/CEILING-BOUND · N-SHUF FAIL/FAIL/PASS · N-SHUF-M3 PASS/FAIL/PASS
> every bar at all 3 seeds (M6 where the meeting was seen: 20261102, 20261103): M1 PASS · M2a no · M2b no · M6 no · M3 PASS · SPOKEN PASS · TRUTH no · READ-BACK PASS · ORDER no · DECLINE no · N-SHUF no · N-SHUF-M3 no → S1b-1 does not pass
> refutations (§9): T1 20261101:no 20261102:no 20261103:no · the lr law (A-RW below A-RW-LR10 on M1 at ≥ 2 seeds) stands (20261101:not below 20261102:not below 20261103:not below) · T2 20261101:no 20261102:no 20261103:no · T3 20261101:REFUTED 20261102:REFUTED 20261103:REFUTED · T4′ spread-is-the-limit 20261101:no 20261102:no 20261103:no · (ii) above the law by ≥ 0.05 at ≥ 2 seeds: no · the learner refuses (M2b ≥ 0.80) 20261101:no 20261102:no 20261103:no · one-meeting 20261101:n/g 20261102:no 20261103:no
```

## 5 · RAISED (can move a verdict or needs the seat)
1. **DECLINE's organ clause, read as written, after the unit.**
   - The unit's report gave PASS (A-RW 0.778 / 0.806 / 0.706 ≥ 0.90 × P-ORACLE 0.722 / 0.556 / 0.618).
   - The PREREG says «P-ORACLE's DECLINE < 0.80 → CEILING-BOUND (purple inside a trained colour's band)», so the mark reads CEILING-BOUND at all seeds. The fraction reading is printed beside.
   - The organ fact agrees: purple lies inside P-ORACLE's blue band for 0.86 / 0.69 / 0.82 of the purple things and inside red's for 0.69 / 0.50 / 0.62.
2. **T4′'s «spread is the limit» clause.** The unit's report compared (ii) ≤ the law, reversing the text's «(ii) no worse than the law». Fixed test-first: it reads no at all seeds, because (ii) is WORSE than the law (0.062 / 0.104 / 0.083 against 0.188 / 0.146 / 0.229).
3. **The mouth speaks ONE word. With continuous scores, a «unique maximum» almost never fails.**
   - Every arm's spoken phrases are ≥ 98.5 % single words, P-ORACLE and ORACLE-TRUTH included. So ORDER is NOT GRADABLE at every seed (A-RW and P-ORACLE both n 0).
   - The co-signature note's «every colourless phrase ties at the read-back» (kind B) does not hold: two things never score exactly alike. Kind B's decline rate is 0.143 / 0.188 / 0.067.
   - The acceptance rule is the PREREG's; the consequence is the seat's to weigh (§6 (b)).
4. **With ONE hypothesis in view every margin is +∞**, so the builder's declared tie-break (the order-key sequence, then first-heard order) decides the spoken word. This is arbitrary with respect to the world.
   - It is not the driver: a tie-break by the target's own Σ log p (a counterfactual reading, §6 (b″)) moves seed 1's TRUTH only from 0.671 to 0.697.
5. **N-SHUF reads above chance + 0.05 on M1 at seeds 1–2** (0.651 > 0.594; 0.597 > 0.593) and on M3 at seed 2 (0.667 > 0.591). S1a's null at lr 0.1 read 0.552 / 0.587 / 0.479.
   - A fixation-count salience pointer reads 0.568 (chance 0.544) and agrees with N-SHUF on 0.583, so that is not the mechanism.
   - The mechanism is open. The null's failure makes «every bar at all seeds» impossible independently of the learner.
6. **The store's standardisation.** μ_w, σ_w and B_w are computed from `store_z` / `store_r` as stored (each meeting's standardisation, «built from those alone»). τ_none's f(t*) re-standardises the training scenes' raw inputs under the current state (as S1a's calibrate).
7. **M3's «both words necessary by construction»** holds on the 3-thing items. On 2-thing items one word is necessary, and the distractor kind names which. Tested, and printed per kind.
8. **Smaller declared readings:**
   - the ear, the order key and the exclusion are learned from every heard utterance by every arm; the oracle hears even when its referent is unseen;
   - one fresh `tie:<item_id>` generator per read-back candidate;
   - the reason priority for «I cannot say it yet»: no held word, then «none» fired, then no unique read-back;
   - TRUTH-SEEN is read over the things with ≥ 1 fixation;
   - N-SHUF's chance is the parent's 108-phrase grammar;
   - the draw orders of the three new splits (world.py docstrings);
   - kind A's distractors are drawn by rejecting a trained draw while its shape is the target's;
   - M1's per-size bars are printed; the pooled 2–3 line is the verdict (as in S1a).
9. **Nothing was cut** (§11's cut order): reading (ii), TRUTH-SEEN, the length mix and the per-pair M3 rows are all in the report.
10. **The report's «S1a» on M6 at seed 20261101** prints S1a's raw covered reading (0.481) beside a NOT GRADABLE line. S1a's own verdict there was NOT GRADABLE too (the meeting was never seen); the number is a raw reading, not a grade.

## 6 · The diagnoses (read by no verdict; `tools/scene/diag/s1b1_mechanisms.py`, output `/data/dev/brain-runs/scene-s1b1/gate/diag_mechanisms.out`)

```
(a) τ_none(diag) = 0.999 over n 4647 training scenes with ≥ 2 hypotheses; the referent UNCOVERED in 371 (0.080) — median f 0.80 vs 0.64 covered; f > τ_none: uncovered 0.129 · covered 0.043
    a counterfactual τ over the COVERED-referent scenes only (a reading, not the law): 0.982
    M2a under the law's τ_none 0.999: refusal 0.522 (n 400) · false refusal on the graded covered M1 0.094 (n 192)
    M2a under the covered-only τ 0.982: refusal 0.547 (n 400) · false refusal on the graded covered M1 0.104 (n 192)
(b) A-RW's spoken phrases at 10,000 (seed 20261101): 76, of lengths [1]; also true of ANOTHER thing in view: 8 (0.105); read-back margin median true 4.68 (n 51) · false inf (n 25)
(c) the salience pointer (the most-fixated hypothesis) on M1's graded covered items: 0.568 (n 192); N-SHUF agrees with it on 0.583
(b′) the false spoken phrases, by cause and the word's type: {('false of the target', 'shape', 'one hypothesis'): 11, ('false of the target', 'colour', 'several'): 6, ('also true of an UNSEEN thing', 'size'): 2, ('false of the target', 'size', 'one hypothesis'): 3, ('also true of a SEEN thing', 'colour'): 2, ('also true of an UNSEEN thing', 'colour'): 1}
(b″) seed 20261101, A-RW at 10,000: TRUTH with the declared tie-break 0.671 (n 76) · with ties at +∞ broken by the target's own Σ log p 0.697 (a counterfactual reading) · items whose HELD words include a word uniquely true of the target: 74/78
```

What they say [Likely; the numbers are Certain as printed]:
- **(a) M2a's distance «none» refuses about half the absent phrases, and the gaze is not the cause.** Scenes whose referent the gaze missed are 8 % of τ_none's population. Calibrating without them (0.982 against 0.999) moves refusal only from 0.522 to 0.547. The word bands admit a thing in view for most absent phrases.
  - From the same state, reading (i) (S1a's τ_point rule at lr 0.01) refuses 0.892 / 0.845 / 0.880 with false refusal 0.068 / 0.055 / 0.057. That would meet M2a's bar at every seed, **as a reading only**: the law's «none» chose the distance, and the distance is what failed; the learner does not pass M2a.
- **The counterfactuals in (a) and (b″) RULE MECHANISMS OUT; they are not proposals.** A covered-only τ moves refusal by 0.025; a Σ-log-p tie-break moves TRUTH by 0.026.
- **(b) The false spoken words are mostly wrong words, not ambiguous ones.** 20 of 25 false phrases are false of the TARGET itself; 14 of those had one hypothesis in view, where the read-back cannot test a word. The learner HOLDS a uniquely true word in 74 of 78 items. The held set is broad (the same band that fails M2b), and nothing in the mouth prefers the true word when the read-back cannot discriminate.
- **(c) N-SHUF above chance is not fixation-count salience.** The mechanism is open (§5.5).

## 7 · The suite on the final code

Run on **302db7d**, the last commit that touches anything but this file (`git diff --stat 302db7d..HEAD` names only this .md). Each line is read from its log, and each log has 0 `ERROR:` / `FAIL:` blocks:
- **The whole brain suite under the venv:** `Ran 520 tests in 234.892s` / `OK (skipped=3)`; log `/data/dev/brain-runs/scene-s1b1/logs/suite-venv-302db7d.log`. That is 487 at S1a's final, plus S1b-1's 33 new tests.
- **The scene package under /usr/bin/python3:** `Ran 118 tests in 20.709s` / `OK`; log `/data/dev/brain-runs/scene-s1b1/logs/suite-scene-sys-302db7d.log`.
- **Red on the parents:** 4093ff9 (29 of the 48 new/changed tests, §1.1); dee656e (the 2 post-run reading tests).

## 8 · CORRECTION to §6 (b), and the follow-up readings (added 2026-09-28 14:45 +0400 by Claude (Opus 5.5, S1b-1 builder); read by no verdict)

Script `tools/scene/diag/s1b1_followup.py` (run from the pinned copy of 6064165); its whole output is `/data/dev/brain-runs/scene-s1b1/gate/diag_followup.out`, copied beside the script as `tools/scene/diag/s1b1_followup.out`. Every control reproduced the unit: N-SHUF's own draw (0.651 / 0.597 / 0.469), the law's TRUTH (0.671 / 0.716 / 0.600), and the law's spoken phrase on every SPEAK item (78/78, 80/80, 72/72).

**The correction.** §6 (b) says «14 of those had one hypothesis in view, where the read-back cannot test a word». That is FALSE. (b′) labelled a +∞ read-back margin as «one hypothesis». A word of fewer than 3 meetings answers by its band (p ∈ {0, 1}), so its margin is +∞ with several hypotheses in view, and it wins the mouth's margin tie-break. The true split at seed 20261101, by X's rows:
- 20 of 25 false phrases are false of the target (this part stands). They split into three parts, 3 + 11 + 6 = 20:
  - 3 other words with one hypothesis in view;
  - **11 «dax»**, 10 of them with ≥ 2 hypotheses in view and 1 with one (so 4 of the 20 had one hypothesis, not 14);
  - 6 other words with ≥ 2 hypotheses and a finite margin.
- Every spoken «dax» is false, at every seed: 11 / 5 / 13.

The sentence «nothing in the mouth prefers the true word» is also wrong in kind: the mouth prefers the young word. A counterfactual mouth with the words of < 3 meetings dropped from HELD reads TRUTH 0.816 / 0.757 / 0.700 against the law's 0.671 / 0.716 / 0.600. This is a reading that names the mechanism, not a proposal.

**(A1) N-SHUF's stream is no truer than chance.** A deranged utterance is true of ≥ 1 thing in its paired scene 0.124 / 0.135 / 0.138 of the time, against the independent-draws base rate of 0.136 / 0.134 / 0.135 (1.000 for the true stream). Per type it is the same. Seed 20261103 does not differ.

**(A2) §5.5's «N-SHUF above chance» was the draw.** Over 10 fresh derangements per seed, N-SHUF's M1 ranges 0.380–0.620 (medians 0.557 / 0.545 / 0.512); 4 of 30 draws clear chance + 0.05. The unit's own draw sat above 10/10, 9/10 and 1/10 of the fresh draws. One derangement per seed cannot tell a null above chance from a null's spread. Price: 33 runs, 1.8 CPU-min.

**(A3) The within-type forced name on SPEAK** (TRUTH; caveat: NAME's 0.93–0.95 is read on one-thing scenes, and SPEAK is 2–3-thing scenes):
- One hypothesis in view (n 5 / 10 / 8), shape · colour · size · by margin · the law:
  - 0.800 · 0.200 · 0.800 · 0.600 · 0.000
  - 0.800 · 0.500 · 0.400 · 0.400 · 0.222
  - 1.000 · 0.875 · 0.750 · 0.875 · 0.375
- Several hypotheses (n 73 / 70 / 64):
  - 0.767 · 0.548 · 0.384 · 0.603 · 0.718
  - 0.800 · 0.686 · 0.386 · 0.629 · 0.785
  - 0.734 · 0.656 · 0.312 · 0.484 · 0.629
- On several hypotheses, the margin chose size most often (40 / 32 / 36), and size is the worst forced type.
