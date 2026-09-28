# T-MEM-2 «METACOGNITION DECIDES» — the builder's hand-back: THE FIRST GATE read STOP at step 3; no unit ran

*edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:05 +0400 — the hand-back at the gate's STOP, as the brief orders.*

*The law: PREREG-TMEM2 final (brain-design-3 4d03f79, sha b785b54f…), with the coordinator's rulings (1) and (2) and the declared readings (a)–(i). Reading (b) carries its 0.10 tolerance.*

## 0 · The answer
- **THE FIRST GATE: STOP at step 3.** On seed 20261101's stream, five trained words read their truth-free cal_20 below their truth-fed cal_20 by more than 0.10:

  | word | truth-free | truth-fed |
  |---|---|---|
  | big | 0.70 | 0.90 |
  | circle | 0.70 | 1.00 |
  | green | 0.75 | 0.95 |
  | small | 0.80 | 0.95 |
  | square | 0.80 | 1.00 |

  By reading (b) as ruled, that is §6's declared instrument fault, so the gate stops.
- **No unit ran.** `scene-tmem2` was never launched, no report exists, and B1–B4 are unread.
- **The other steps passed:**
  - step 0: the control's record is as recorded;
  - step 1: the identity holds on all three seeds, and every planted change was caught;
  - step 2: the row's toy passes on seeds 0–2;
  - step 4: the smoke's wiring pin holds;
  - step 5: the price is 1.1 CPU-min, against ≤ 5 declared.
- **It is not a fault in the build.** A read-only diagnostic (§5) committed its predictions before it ran. It reproduces the gate's rows exactly, and it finds three things:
  - **Where the attribution IS the referent** (class A, 14,181 grades), the two rows agree on every grade.
  - **The reversal comes from scenes whose referent the gaze never saw** (class C, 10.8 % of the graded said words). There, §2 gives the fed row nothing to grade: the referent has no hypothesis. The free row still grades the learner's attribution, which falls on a seen distractor. That gives 1,924 grades, 1,437 of them refuted. Of those refutations, 1,371 (95 %) refute a claim that was TRUE of the thing it was made about.
  - **Without class C**, the two rows' whole-life precisions agree within 0.02 on all 13 words.
- **It replicates.** The gate reads step 3 on seed 20261101 only. The other two gate lives, read the same way, show the same shape:
  - 20261102: 10 of 13 words reversed, 3 by more than 0.10;
  - 20261103: 10 of 13 reversed, 3 by more than 0.10;
  - on every word of every seed, the free row grades more claims than the fed row.
- **Raised, not fixed — the population question.** Step 3 compares two different POPULATIONS.
  - §6's declared sign reasons about wrong attributions among SEEN things. That is class B, and there the sign holds: the free row reads 0.900 against the fed row's 0.868.
  - The sign does not count scenes whose referent was never a hypothesis. The fed row's «ceiling» is the same claims graded at the referent, and in those scenes no such claim exists.
  - The coordinator decides which of two things this is:
    - §6 refutation (d)'s FINDING — «the truth-free and truth-fed rows disagree by > 0.10 on ≥ 3 words → the row is calibrated to its own attributions (T5's limit) — B3 / B4 are then read on the truth-fed row as the ceiling and the truth-free row is the finding»;
    - an instrument to change before the unit.
  - I propose no fix.

## 1 · The tree, the commits, the pin
- **Worktree:** `/data/dev/genome-wt-scene-r`, branch `scene-tmem2` from scene-s1b1r 01e784b. **Run root:** `/data/dev/brain-runs/scene-tmem2/`. S1b-1R's root was only read.
- **Commits:**
  - **d01b7d3** — health.py, run_tmem2.py and their tests, test-first; the truth fence's allow-list gains health.py;
  - **96a00bd** — the unit script `tools/scene/run_tmem2.sh` and the pin script `tools/scene/pin_code_tmem2.sh`;
  - **15b047e** — the `logp_answer` guard and its test (§3);
  - **e213b09** — the step-3 diagnostic `tools/scene/diag_tmem2_step3.py`, with its predictions;
  - this hand-back.
- **The pin the gate ran:** `/data/dev/brain-runs/scene-tmem2/code-15b047e` (CODE_SHA 15b047e1fd8d…). Verified from the pin before the launch:
  - PREREG-TMEM2's sha b785b54f…;
  - the control's `report.txt` sha b695ae5c…;
  - the WORLD_CODE files: all 13 are unchanged since 0b1857b, so `cache.check_code` accepts all 42 of S1b-1R's caches in place (reading (i)).

## 2 · Red on 01e784b
- **The T-MEM-2 modules:** `Ran 4 tests … FAILED (errors=3)`. Two test modules cannot import `health`/`run_tmem2`, and the fence's allow-list test errors on the missing health.py. The planted-offender fence test passes by design. Log: `redcheck-01e784b/red.log`.
- **The guard's test:** `Ran 1 test … FAILED (errors=1)`, with `IndexError: index 5 is out of bounds for axis 0 with size 5`. Log: `redcheck-01e784b/red-guard.log`.

## 3 · The first launch crashed before any verdict (17:41) — fixed test-first
- **The crash:** `scene-tmem2-gate` from code-96a00bd died after 4.8 CPU-s in the first identity life, with `IndexError: index 13 is out of bounds for axis 0 with size 13` in `learners.logp_answer`, reached through `health.claims → RWRoad.believed`.
- **The cause:** §2's claims read the LAW road's step 1 BETWEEN reading points. There a word met since the last calibration («dax», scene 2,700) sits beyond the reading point's band cache. S1b-1R only ever answered right after a calibration, so its roads never met the case.
- **The fix (15b047e):** a word newer than the cache takes its band fresh, from the function the cache is built from. Every earlier call is unchanged, and the gate's identity step re-proves it on all three seeds (§4).
- **Evidence:** `gate-crash-1741/` holds the journal and the empty gate log. The unit was reset before the relaunch.

## 4 · THE FIRST GATE (17:51:24 – 17:52:29 +0400, 67 s wall, 67 CPU-s, from code-15b047e) — `gate/gate.txt`, verbatim
```
== THE FIRST GATE (PREREG-TMEM2 §7; each step a STOP on a miss; printed whole) ==
0. the CONTROL's record: /data/dev/brain-runs/scene-s1b1r/report.txt sha as recorded (b695ae5c94d13a85…)
1. THE IDENTITY (S1b-1R's A-RW-R record at 10,000; canonical JSON; the planted one-byte change first):
   20261101: point = (188211 bytes; planted CAUGHT) · LAW = (72118 bytes; planted CAUGHT) · summary = (1465 bytes; planted CAUGHT) · cpu 22.0 s → PASS
   20261102: point = (187763 bytes; planted CAUGHT) · LAW = (75822 bytes; planted CAUGHT) · summary = (1458 bytes; planted CAUGHT) · cpu 22.0 s → PASS
   20261103: point = (187927 bytes; planted CAUGHT) · LAW = (75263 bytes; planted CAUGHT) · summary = (1464 bytes; planted CAUGHT) · cpu 22.2 s → PASS
2. the row's toy (A 95 %, B 50 %, 200 graded claims each): seed 0: cal_20 A 0.95 B 0.65 · kept {'A': True, 'B': False} · the null {'A': False, 'B': True} · an ungraded claim moves nothing True · seed 1: cal_20 A 1.00 B 0.45 · kept {'A': True, 'B': False} · the null {'A': False, 'B': True} · an ungraded claim moves nothing True · seed 2: cal_20 A 0.95 B 0.50 · kept {'A': True, 'B': False} · the null {'A': False, 'B': True} · an ungraded claim moves nothing True → PASS
3. agreement and coverage on seed 20261101's stream (claims on 9750 scenes), per word n_graded · cal_20 truth-free / truth-fed:
   big        2155 · 0.700 / 0.900  REVERSED BY > 0.10 — the declared instrument fault
   blue        825 · 0.900 / 0.950  reversed (a reading)
   circle     1788 · 0.700 / 1.000  REVERSED BY > 0.10 — the declared instrument fault
   cross      1364 · 1.000 / 1.000
   green      1063 · 0.750 / 0.950  REVERSED BY > 0.10 — the declared instrument fault
   red         708 · 1.000 / 1.000
   ring       1253 · 0.950 / 0.900
   small      2222 · 0.800 / 0.950  REVERSED BY > 0.10 — the declared instrument fault
   square     1266 · 0.800 / 1.000  REVERSED BY > 0.10 — the declared instrument fault
   star       1568 · 1.000 / 1.000
   triangle   1516 · 0.950 / 1.000  reversed (a reading)
   white       899 · 0.700 / 0.800  reversed (a reading)
   yellow      776 · 0.850 / 0.950  reversed (a reading)
   «no row»: none · reversed: ['big', 'blue', 'circle', 'green', 'small', 'square', 'triangle', 'white', 'yellow'] · the fault (> 0.10): ['big', 'circle', 'green', 'small', 'square'] → MISS
4. the smoke — seed 20261101's fresh items under all four roads (the tables whole):
      big       claims  6311 · graded  2155 (fed  1848) · cal_20 0.700 / 0.900 · |diff| 0.200 · median |Δ| 0.050 · drift 10 / 9 · missed  279 · gate not held lately · oracle 0.984
      blue      claims  2520 · graded   825 (fed   771) · cal_20 0.900 / 0.950 · |diff| 0.050 · median |Δ| 0.100 · drift 0 / 0 · missed  224 · gate open · oracle 1.000
      circle    claims  2572 · graded  1788 (fed  1453) · cal_20 0.700 / 1.000 · |diff| 0.300 · median |Δ| 0.100 · drift 6 / 6 · missed   34 · gate not held lately · oracle 1.000
      cross     claims  2190 · graded  1364 (fed  1263) · cal_20 1.000 / 1.000 · |diff| 0.000 · median |Δ| 0.050 · drift 4 / 4 · missed  133 · gate open · oracle 1.000
      green     claims  3436 · graded  1063 (fed   929) · cal_20 0.750 / 0.950 · |diff| 0.200 · median |Δ| 0.050 · drift 2 / 2 · missed  144 · gate not held lately · oracle 0.900
      red       claims  2124 · graded   708 (fed   642) · cal_20 1.000 / 1.000 · |diff| 0.000 · median |Δ| 0.100 · drift 3 / 3 · missed  159 · gate open · oracle 0.871
      ring      claims  1682 · graded  1253 (fed  1183) · cal_20 0.950 / 0.900 · |diff| 0.050 · median |Δ| 0.050 · drift 8 / 1 · missed  576 · gate open · oracle 0.886
      small     claims  6768 · graded  2222 (fed  2009) · cal_20 0.800 / 0.950 · |diff| 0.150 · median |Δ| 0.050 · drift 5 / 5 · missed  251 · gate open · oracle 0.886
      square    claims  1887 · graded  1266 (fed  1057) · cal_20 0.800 / 1.000 · |diff| 0.200 · median |Δ| 0.050 · drift 8 / 8 · missed   31 · gate open · oracle 1.000
      star      claims  2505 · graded  1568 (fed  1438) · cal_20 1.000 / 1.000 · |diff| 0.000 · median |Δ| 0.050 · drift 7 / 5 · missed   75 · gate open · oracle 1.000
      triangle  claims  2380 · graded  1516 (fed  1382) · cal_20 0.950 / 1.000 · |diff| 0.050 · median |Δ| 0.050 · drift 4 / 4 · missed   65 · gate open · oracle 1.000
      white     claims  2715 · graded   899 (fed   760) · cal_20 0.700 / 0.800 · |diff| 0.100 · median |Δ| 0.050 · drift 6 / 6 · missed  187 · gate not held lately · oracle 0.762
      yellow    claims  2212 · graded   776 (fed   634) · cal_20 0.850 / 0.950 · |diff| 0.100 · median |Δ| 0.100 · drift 0 / 0 · missed  129 · gate open · oracle 1.000
   the roads (S1b-1R's graders, covered targets): SPOKEN · TRUTH (n) · ×spoken · READ-BACK · SPEAK2 spoken · TRUTH-NEED (n) · MINIMAL (n) · ORDER (n) · DECLINE (reading) · M2b (the band, unchanged)
      CONTROL          0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      LAW              0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      HEALTH-MOUTH     0.737 · 0.804 (n 56) · 0.592 · 1.000 · 0.489 · 0.174 (n 23) · 1.000 (n 49) · 1.000 (n 5) · DECLINE 0.676 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 5, 'the read-back': 2, 'not held lately': 2} · SPEAK2 {'no believed-unique phrase': 13, 'not held lately': 3, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 5} · the row refused {'big:not held lately': 52, 'circle:not held lately': 21, 'green:not held lately': 25, 'white:not held lately': 20}
      HEALTH-ORACLE    0.803 · 0.836 (n 61) · 0.671 · 1.000 · 0.681 · 0.281 (n 32) · 1.000 (n 60) · 1.000 (n 10) · DECLINE 0.676 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 3, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 7, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 4} · the row refused {'white:not held lately': 20}
      HEALTH-TRUTHFED  0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      NULL             0.750 · 0.807 (n 57) · 0.605 · 1.000 · 0.468 · 0.227 (n 22) · 1.000 (n 51) · 1.000 (n 5) · DECLINE 0.919 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 6, 'the read-back': 1, 'not held lately': 1} · SPEAK2 {'no believed-unique phrase': 18, 'no sayable word': 7} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 8} · the row refused {'blue:not held lately': 22, 'green:not held lately': 25, 'small:not held lately': 45, 'yellow:not held lately': 15}
   the decision (over the CONTROL's spoken phrases on SPEAK + SPEAK2, covered): ERROR-RECALL (declined + replaced true / errors) · TRUE-RETENTION (true / true):
      CONTROL          ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
      HEALTH-MOUTH     ER 0.171 (6 + 0 / 35) · TR 0.790 (49 / 62)
      HEALTH-ORACLE    ER 0.057 (2 + 0 / 35) · TR 0.968 (60 / 62)
      HEALTH-TRUTHFED  ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
      NULL             ER 0.200 (7 + 0 / 35) · TR 0.823 (51 / 62)
      calibration of the truth-free row (the law's): ECE 0.106 · type-2 AUROC 0.567 · n 453 (errors 33; no row 0) · curve [0.7: n 159 conf 0.71 acc 0.91] [0.8: n 119 conf 0.81 acc 0.92] [0.9: n 175 conf 0.97 acc 0.95]
      calibration of the truth-fed row (its ceiling): ECE 0.012 · type-2 AUROC 0.654 · n 453 (errors 33; no row 0) · curve [0.8: n 42 conf 0.80 acc 0.76] [0.9: n 411 conf 0.95 acc 0.94]
      calibration of the deranged rows (the floor): ECE 0.142 · type-2 AUROC 0.464 · n 453 (errors 33; no row 0) · curve [0.7: n 166 conf 0.71 acc 0.92] [0.8: n 96 conf 0.81 acc 0.99] [0.9: n 191 conf 0.96 acc 0.90]
      the CONTROL re-graded vs S1b-1R's report.json: TRUTH [0.8225806451612904, 0.8225806451612904] · SPOKEN [0.8157894736842105, 0.8157894736842105] · TRUTH-NEED [0.3142857142857143, 0.3142857142857143] → EQUAL
   the wiring pin (READ-BACK 1.000 wherever something was spoken): PASS
5. the price, solo (the three lives above ran one at a time): lives 22.0 / 22.0 / 22.2 CPU-s · one seed's grading 0.3 CPU-s → the unit ≈ 67 CPU-s ≈ 1.1 CPU-min against ≤ 5 declared → within
GATE: STOP — the declared sign reversed by > 0.10 (step 3) · 67 s wall · 67 CPU-s
```

## 5 · The step-3 diagnostic (17:58 – 17:59 +0400, 22.9 CPU-s, the same pin; read-only; it changes no verdict)
- **What it does:** it re-runs seed 20261101's life with the gate's hook subclassed to RECORD the class of each graded said word:
  - A: the attribution h* equals the referent's hypothesis;
  - B: the referent was seen, but h* is another hypothesis;
  - C: the referent was never a hypothesis;
  - N: h* is None.

  It reuses `health.claims`, `health.attribution`, `health.grades` and `run.referent_index`, and it first reproduces the gate's own rows. The script is `tools/scene/diag_tmem2_step3.py` (e213b09, predictions P1–P4 in its header), and the output is in `gate-diag/diag.txt` and `diag.json` (per-record).
- **Output, verbatim:**
```
== T-MEM-2 step-3 DIAGNOSTIC (seed 20261101; pin 15b047e; identity PASS; read-only, the gate's verdict unchanged) ==
0. the gate's own rows reproduced from this accounting (n_graded and cal_20, free and fed, 13 words; the gate life's record.json AND this life's hook): ALL EQUAL
1. graded said words by class (free = the learner's attribution; fed = the referent):
   class  said-words  free graded (confirmed)  fed graded (confirmed)  A: free≠fed
   A           15898   14181 ( 13461)            14181 ( 13461)         0
   B            1455    1298 (  1168)             1188 (  1031)         
   C            2102    1924 (   487)                0 (     0)         
   N               0       0 (     0)                0 (     0)         
   the referent unseen (class C) in 2102 of 19455 graded-type said words (0.108); class A's share of the referent-seen: 0.916
2. free-row REFUTATIONS in B and C — the claim b_T(h*) against the TRUE value of h*'s majority thing:
   B: refuted 130 · the claim TRUE of its thing 93 · the said word true of that thing 28 · h* on no thing 0
   C: refuted 1437 · the claim TRUE of its thing 1371 · the said word true of that thing 28 · h* on no thing 0
3. per claimed word — whole-life precision free (all · without C) / fed · cal_20 free (all · without C) / fed · C grades (confirmed):
   big       0.884 · 0.942 / 0.936   ·   0.70 · 0.80 / 0.90   ·   C  285 ( 142)
   blue      0.838 · 0.863 / 0.864   ·   0.90 · 0.95 / 0.95   ·   C   49 (  21)
   circle    0.818 · 0.998 / 0.998   ·   0.70 · 1.00 / 1.00   ·   C  326 (   3)
   cross     0.928 · 0.991 / 0.992   ·   1.00 · 1.00 / 1.00   ·   C   98 (  11)
   green     0.848 · 0.917 / 0.914   ·   0.75 · 0.95 / 0.95   ·   C  113 (  30)
   red       0.797 · 0.863 / 0.852   ·   1.00 · 1.00 / 1.00   ·   C   71 (  14)
   ring      0.958 · 0.962 / 0.960   ·   0.95 · 0.90 / 0.90   ·   C   73 (  65)
   small     0.874 · 0.892 / 0.882   ·   0.80 · 0.95 / 0.95   ·   C  194 ( 135)
   square    0.835 · 0.992 / 0.993   ·   0.80 · 1.00 / 1.00   ·   C  204 (   3)
   star      0.926 · 0.996 / 0.997   ·   1.00 · 1.00 / 1.00   ·   C  121 (  11)
   triangle  0.926 · 0.999 / 0.999   ·   0.95 · 1.00 / 1.00   ·   C  129 (  19)
   white     0.771 · 0.878 / 0.872   ·   0.70 · 0.85 / 0.80   ·   C  136 (  23)
   yellow    0.746 · 0.874 / 0.890   ·   0.85 · 0.95 / 0.95   ·   C  125 (  10)
cpu 22.9 s
```
- **The predictions, read:**
  - P1 holds: class A has 0 disagreements, so there is no build fault.
  - P2 holds: class A is 0.916 of the referent-seen said words.
  - P3 holds: the free row grades 2,034 more claims than the fed row (17,403 against 15,369). 1,924 of them are class C's, which the fed row cannot grade; the other 110 are class B's (claims confident at h* but not at the referent). Of C's 1,924, 1,437 are refuted, and 1,371 of those refuted claims are TRUE of the thing they were made about.
  - P4 holds: without C, the whole-life precisions agree within 0.02 on every word. Without C, cal_20 would reverse by at most 0.10 (big: 0.80 against 0.90, not more than 0.10). That is context only: the STOP stands on cal_20 as ruled.
- **Why the rows are charged:** the claimed word carries the charge. When «big» is said about an unseen big thing, the attribution falls on a seen small thing, and the refutation is filed under «small». When «circle» is said about an unseen circle, the refutation is filed under whatever the seen distractor is believed to be. So «circle» and «square» collect refutations from the other shapes' unseen referents, while their fed rows read 1.00.
- **What the gate would do with this row:** the smoke (§4) already shows it. HEALTH-MOUTH refuses big, circle, green and white as «not held lately», but by HEALTH-ORACLE's truth circle names correctly 1.000 and big 0.984.

## 6 · Rulings and declared readings, as adopted (carried into the code)
- **Ruling (1), B2's null clause:** hw = 1.96·√(p(1−p)/n), where p is the NULL's pooled ERROR-RECALL and n is the control's 78 pooled errors (`bars.binomial_half_width_95`). B2's null clause passes iff ER(HM) − ER(NULL) ≥ hw, and iff the difference is > 0 when hw = 0. It is recorded as a declared reading.
- **Ruling (2), B3:** B3 is read per seed on its n predictions (≈ 450 per seed), with the errors printed beside. The error-count UNDERPOWERED rule applies to B2 and B4 (pooled).
- **(a) The ECE / AUROC population:** every covered fresh NAME thing × every learned type, with the ROAD's b_T, whether or not the band holds it. The confidence is that word's cal_20. Words with no graded claim are excluded, and counted.
- **(b) Step 3:** a reversal is printed as a reading. It is a STOP only when it is MORE THAN 0.10. A word under 20 graded claims reads «no row», printed and not a stop.
- **(c) The truth-fed row:** it grades at the referent's hypothesis (`marks.thing_hypothesis`), filed under b_T(h_ref). A referent with no hypothesis is ungraded — the population §0 raises.
- **(d) HEALTH-ORACLE:** a word that no NAME thing is believed to be is not sayable («no row»).
- **(e) Windows and drift:**
  - windows are consecutive, non-overlapping blocks of 20 graded claims;
  - cal_20 slides over the last 20;
  - drift firings are counted at each completed window, in both forms (no floor, and the 1/20 floor).
- **(f) The null:** the 13 trained words, sorted, deranged by `nshuf_permutation(substream(ws, "tmem2-null:<ws>"), 13)`.
- **(g) Reading points:** the life calibrates at every reading point, and answers only at 10,000.
- **(h) The reasons:** «not held lately» or «no row» replaces the mouth's «no sayable word» when the row refused a word the band held. The mouth's own reason is kept beside.
- **(i) S1b-1R's caches and records** are read in place.
- **Also as built:**
  - refutation (d): the bars stay on the truth-free row, and the fed row's ECE/AUROC print as the ceiling;
  - B1's order: a SPOKEN miss FAILS first, then TRUTH with n < 30 reads UNDERPOWERED.

## 7 · A latent gap in the gate's code (moot this time)
- Step 5 prints `OVER` when the price exceeds 5 CPU-min, but it adds no STOP reason. §7 says each step is a STOP on a miss.
- The price read 1.1 CPU-min (within), so the verdict is unaffected.
- If the gate is re-run under an amendment, step 5 should STOP on OVER.

## 8 · The suites on the final code (e213b09)
- **The scene package under /usr/bin/python3:** `Ran 193 tests in 51.532s` / `OK`, with 0 ERROR/FAIL blocks. Log: `logs/suite-scene-sys-e213b09.log`.
- **The whole brain suite under the venv:** `Ran 595 tests in 265.298s` / `OK (skipped=3)`, exit 0, with 0 ERROR/FAIL blocks. The log's `[record] … → FAIL` line is a test's own printed planted case, not a failure. Command: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/tmp nice -n 19 /data/dev/venvs/brain/bin/python -m unittest discover -s tests/brain -t .`. Log: `logs/suite-venv-e213b09.log`.

## 9 · Files
- The gate: `/data/dev/brain-runs/scene-tmem2/gate/gate.txt` and `gate.json`, plus its three lives in `gate/lives/<ws>/life/`.
- The diagnostic: `/data/dev/brain-runs/scene-tmem2/gate-diag/diag.txt`, `diag.json` and `run.log`, plus its life in `gate-diag/lives/`.
- The crash: `/data/dev/brain-runs/scene-tmem2/gate-crash-1741/`.
- The pins: `/data/dev/brain-runs/scene-tmem2/code-15b047e` (the gate's) and `code-96a00bd` (the crashed launch's).
- Nothing was written under `/data/dev/brain-runs/scene-s1b1r/`, and no unit other than `scene-tmem2-gate` was launched.

---

## 10 · AMENDMENT 1 — built test-first, re-gated: STOP again at step 3; the rule sets almost nothing aside

*edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:33 +0400 — appended; §0–§9 above are the 17:51 record the amendment cites (2b7d800), unchanged. That STOP's gate files now sit in `/data/dev/brain-runs/scene-tmem2/gate-1751-stop/` (moved aside before the re-gate; §9's `gate/` paths read there).*

### 10.1 · The answer
- **THE FIRST GATE, re-run under PREREG-TMEM2 + AMENDMENT 1: STOP at step 3.** The same five words read truth-free cal_20 below truth-fed by more than 0.10, and the free row's cal_20 did not move on any of the 13 words:

  | word | truth-free | truth-fed |
  |---|---|---|
  | big | 0.70 | 0.90 |
  | circle | 0.70 | 1.00 |
  | green | 0.75 | 0.95 |
  | small | 0.80 | 0.95 |
  | square | 0.80 | 1.00 |

- **No unit ran.** Steps 0, 1, 2, 4 and 5 passed: identity 3 of 3 with every planted change caught, the toy with the set-aside clause, the wiring pin, and the price at 1.1 CPU-min.
- **The rule barely fires.** It set aside:
  - of the claims whose referent the gaze never saw: 45 / 1,924 = **0.023** (seed 20261101), 34 / 1,896 = **0.018** (20261102), 52 / 1,893 = **0.027** (20261103);
  - of the claims whose referent it saw (the false-unseen rate): 29 / 15,479 = **0.002**, 46 / 15,418 = **0.003**, 29 / 15,475 = **0.002**. That is far BELOW the predicted 0.05–0.08. It is not #162's rule that sets everything aside; it is the opposite.
- **Why (the diagnostic, §10.5):** the check is right. It agrees with an independent recomputation on 17,403 of 17,403 claims, and it reproduces the gate's counts. But the READER's band holds nearly every word of a type at the attributed thing h*, in all three classes alike:
  - shape: 5.4 of 6 words;
  - colour: 4.8 of 5;
  - size: 2.0 of 2.

  The said word's d / band at the attributed thing has a median of 0.59–0.64 in every class, with or without a seen referent. So «w's own band holds h*» is true about 98 % of the time whatever the eye saw, and it cannot separate class C.
- **RAISED, not fixed:** the rule reads a band that does not discriminate between the words of a type. The same band decides every claim's CONFIDENT. The coordinator decides. I propose no fix.

### 10.2 · The build
- **Commits on `scene-tmem2`:**
  - **8767cf6** — the rule (`health.grades`), the claim record carrying its held words, the row's `unseen` count, the toy's set-aside clause, both rows graded through the rule, the two readings, step 3's residual print, step 5 a STOP, and the amendment's sha checked beside the law's. The unit also requires both shas in `gate.json`.
  - **95a6439** — the read-only diagnostic `tools/scene/diag_tmem2_amend1.py`, with its predictions committed before its run. It is PIN-guarded to code-8767cf6.
  - this section.
- **Red on 2b7d800:** `Ran 24 tests … FAILED (failures=2, errors=8)`. Log: `redcheck-2b7d800/red.log`.
- **Green:**
  - the T-MEM-2 modules: `Ran 42 tests … OK`;
  - the scene suite on the amended bytes: `Ran 204 tests in 51.733s` / `OK` (log `logs/suite-scene-sys-amend1-precommit.log`);
  - the suites on the final commit: §10.6.
- **The old instrument:** `tools/scene/diag_tmem2_step3.py` (e213b09) is PIN-guarded to code-15b047e and reads a grade as a bool. It is a historical instrument for that pin only; it does not run from the new one.
- **The pin the gate ran:** `/data/dev/brain-runs/scene-tmem2/code-8767cf6`. Verified from the pin before the launch:
  - PREREG-TMEM2 b785b54f… and AMENDMENT 1 6da8ff67…;
  - the control's report.txt b695ae5c…;
  - 42 of 42 of S1b-1R's caches accepted by `check_code`;
  - the 13 WORLD_CODE files unchanged since 0b1857b.

### 10.3 · Declared readings of the amendment
1. **«w's own band holds h*»** is read from the claim step's own «what is this?» at h*: the held words that made the claim CONFIDENT, now carried in the claim record, in the same learner state.
   - It follows that a confirmation is never set aside: b = w is held at h* by its own confidence.
   - The alternative, re-reading the band after `train_scene`, differs only by one scene's update of the standardisation statistics. The reader's μ, Λ and bands change only at reading points.
2. **Both rows go through the rule.** The truth-fed row applies it at the referent's hypothesis: one difference, the hypothesis, so it is the ceiling of the AMENDED row.
   - The alternative applies the rule to the truth-free row only. Its fed row is exactly the 17:51 gate's (same life, same claims): big 0.900, circle 1.000, green 0.950, small 0.950, square 1.000.
   - Against the unchanged free row, that alternative gives the SAME five faults. **The verdict is STOP under both readings.** Mine is the stricter reading: it removes only refutations from the fed row, so the fed row's cal_20 can only stay or rise.
3. **The two readings count gradable claims of the truth-free row** (graded or set aside); that is the headline figure. The scene-level figure is printed beside it: a scene counts as set aside when all its gradable claims are.
   - Every training scene has a referent (30,000 of 30,000), so «never seen» is the same as `referent_index` returning None.
4. **A set-aside claim is counted under the claimed word b_T(h*)** (the row's `unseen`). It is never a MISSED of the said word.
5. **Step 5 is a STOP** when the unit's price exceeds 300 CPU-s.

### 10.4 · The amended gate (18:23:11 – 18:24:18 +0400, exit 3, 66 s wall, 66 CPU-s, from code-8767cf6) — `gate/gate.txt`, verbatim
```
== THE FIRST GATE (PREREG-TMEM2 §7 + AMENDMENT 1 §4; each step a STOP on a miss; printed whole) ==
   the law: PREREG-TMEM2 b785b54f97c6c2bc… · AMENDMENT 1 6da8ff679a317166… · code 8767cf6339ee28120887dcdf2a3f37cdeb52e2de
0. the CONTROL's record: /data/dev/brain-runs/scene-s1b1r/report.txt sha as recorded (b695ae5c94d13a85…)
1. THE IDENTITY (S1b-1R's A-RW-R record at 10,000; canonical JSON; the planted one-byte change first):
   20261101: point = (188211 bytes; planted CAUGHT) · LAW = (72118 bytes; planted CAUGHT) · summary = (1465 bytes; planted CAUGHT) · cpu 21.9 s → PASS
   20261102: point = (187763 bytes; planted CAUGHT) · LAW = (75822 bytes; planted CAUGHT) · summary = (1458 bytes; planted CAUGHT) · cpu 21.9 s → PASS
   20261103: point = (187927 bytes; planted CAUGHT) · LAW = (75263 bytes; planted CAUGHT) · summary = (1464 bytes; planted CAUGHT) · cpu 22.1 s → PASS
2. the row's toy (A 95 %, B 50 %, 200 graded claims each): seed 0: cal_20 A 0.95 B 0.65 · kept {'A': True, 'B': False} · the null {'A': False, 'B': True} · an ungraded claim moves nothing True · a claim set aside «unseen» moves nothing True · seed 1: cal_20 A 1.00 B 0.45 · kept {'A': True, 'B': False} · the null {'A': False, 'B': True} · an ungraded claim moves nothing True · a claim set aside «unseen» moves nothing True · seed 2: cal_20 A 0.95 B 0.50 · kept {'A': True, 'B': False} · the null {'A': False, 'B': True} · an ungraded claim moves nothing True · a claim set aside «unseen» moves nothing True → PASS
3. agreement and coverage on seed 20261101's stream (claims on 9750 scenes), AFTER AMENDMENT 1's rule — per word: graded truth-free / truth-fed · set aside «unseen» truth-free / truth-fed · cal_20 truth-free / truth-fed · the residual (free − fed):
   big        2151 /  1845 ·    4 /    3 · 0.700 / 0.900 · -0.200  REVERSED BY > 0.10 — the declared instrument fault
   blue        819 /   768 ·    6 /    3 · 0.900 / 0.950 · -0.050  reversed (a reading)
   circle     1781 /  1453 ·    7 /    0 · 0.700 / 1.000 · -0.300  REVERSED BY > 0.10 — the declared instrument fault
   cross      1361 /  1263 ·    3 /    0 · 1.000 / 1.000 · +0.000
   green      1051 /   922 ·   12 /    7 · 0.750 / 0.950 · -0.200  REVERSED BY > 0.10 — the declared instrument fault
   red         692 /   634 ·   16 /    8 · 1.000 / 1.000 · +0.000
   ring       1239 /  1174 ·   14 /    9 · 0.950 / 0.950 · +0.000
   small      2222 /  2009 ·    0 /    0 · 0.800 / 0.950 · -0.150  REVERSED BY > 0.10 — the declared instrument fault
   square     1257 /  1056 ·    9 /    1 · 0.800 / 1.000 · -0.200  REVERSED BY > 0.10 — the declared instrument fault
   star       1567 /  1438 ·    1 /    0 · 1.000 / 1.000 · +0.000
   triangle   1514 /  1382 ·    2 /    0 · 0.950 / 1.000 · -0.050  reversed (a reading)
   white       899 /   760 ·    0 /    0 · 0.700 / 0.800 · -0.100  reversed (a reading)
   yellow      776 /   634 ·    0 /    0 · 0.850 / 0.950 · -0.100  reversed (a reading)
   the residual within 0.05 on 6 of 13 words (predicted: most [Likely]; a reading)
   «no row»: none · reversed: ['big', 'blue', 'circle', 'green', 'small', 'square', 'triangle', 'white', 'yellow'] · the fault (> 0.10): ['big', 'circle', 'green', 'small', 'square'] → MISS
   AMENDMENT 1's readings (offline, the tape's truth; readings, never bars), every gate life:
      20261101: the metacognition-of-perception reading (the referent never seen): claims set aside 45 / 1924 = 0.023 (scenes 11 / 977 = 0.011) · the false-unseen rate (the referent seen): 29 / 15479 = 0.002 (scenes 8 / 8042 = 0.001; predicted 0.05–0.08)
      20261102: the metacognition-of-perception reading (the referent never seen): claims set aside 34 / 1896 = 0.018 (scenes 11 / 995 = 0.011) · the false-unseen rate (the referent seen): 46 / 15418 = 0.003 (scenes 14 / 8002 = 0.002; predicted 0.05–0.08)
      20261103: the metacognition-of-perception reading (the referent never seen): claims set aside 52 / 1893 = 0.027 (scenes 22 / 986 = 0.022) · the false-unseen rate (the referent seen): 29 / 15475 = 0.002 (scenes 7 / 8064 = 0.001; predicted 0.05–0.08)
4. the smoke — seed 20261101's fresh items under all four roads (the tables whole):
      big       claims  6311 · graded  2151 (fed  1845) · unseen    4 (fed    3) · cal_20 0.700 / 0.900 · |diff| 0.200 · median |Δ| 0.050 · drift 9 / 9 · missed  279 · gate not held lately · oracle 0.984
      blue      claims  2520 · graded   819 (fed   768) · unseen    6 (fed    3) · cal_20 0.900 / 0.950 · |diff| 0.050 · median |Δ| 0.100 · drift 1 / 1 · missed  221 · gate open · oracle 1.000
      circle    claims  2572 · graded  1781 (fed  1453) · unseen    7 (fed    0) · cal_20 0.700 / 1.000 · |diff| 0.300 · median |Δ| 0.100 · drift 4 / 4 · missed   30 · gate not held lately · oracle 1.000
      cross     claims  2190 · graded  1361 (fed  1263) · unseen    3 (fed    0) · cal_20 1.000 / 1.000 · |diff| 0.000 · median |Δ| 0.050 · drift 5 / 5 · missed  127 · gate open · oracle 1.000
      green     claims  3436 · graded  1051 (fed   922) · unseen   12 (fed    7) · cal_20 0.750 / 0.950 · |diff| 0.200 · median |Δ| 0.100 · drift 4 / 4 · missed  142 · gate not held lately · oracle 0.900
      red       claims  2124 · graded   692 (fed   634) · unseen   16 (fed    8) · cal_20 1.000 / 1.000 · |diff| 0.000 · median |Δ| 0.050 · drift 4 / 3 · missed  159 · gate open · oracle 0.871
      ring      claims  1682 · graded  1239 (fed  1174) · unseen   14 (fed    9) · cal_20 0.950 / 0.950 · |diff| 0.000 · median |Δ| 0.050 · drift 5 / 1 · missed  576 · gate open · oracle 0.886
      small     claims  6768 · graded  2222 (fed  2009) · unseen    0 (fed    0) · cal_20 0.800 / 0.950 · |diff| 0.150 · median |Δ| 0.050 · drift 5 / 5 · missed  247 · gate open · oracle 0.886
      square    claims  1887 · graded  1257 (fed  1056) · unseen    9 (fed    1) · cal_20 0.800 / 1.000 · |diff| 0.200 · median |Δ| 0.050 · drift 7 / 5 · missed   28 · gate open · oracle 1.000
      star      claims  2505 · graded  1567 (fed  1438) · unseen    1 (fed    0) · cal_20 1.000 / 1.000 · |diff| 0.000 · median |Δ| 0.050 · drift 7 / 6 · missed   62 · gate open · oracle 1.000
      triangle  claims  2380 · graded  1514 (fed  1382) · unseen    2 (fed    0) · cal_20 0.950 / 1.000 · |diff| 0.050 · median |Δ| 0.050 · drift 4 / 4 · missed   55 · gate open · oracle 1.000
      white     claims  2715 · graded   899 (fed   760) · unseen    0 (fed    0) · cal_20 0.700 / 0.800 · |diff| 0.100 · median |Δ| 0.050 · drift 6 / 6 · missed  171 · gate not held lately · oracle 0.762
      yellow    claims  2212 · graded   776 (fed   634) · unseen    0 (fed    0) · cal_20 0.850 / 0.950 · |diff| 0.100 · median |Δ| 0.100 · drift 0 / 0 · missed  116 · gate open · oracle 1.000
   AMENDMENT 1's readings (offline, the tape's truth; readings, never bars): 20261101: the metacognition-of-perception reading (the referent never seen): claims set aside 45 / 1924 = 0.023 (scenes 11 / 977 = 0.011) · the false-unseen rate (the referent seen): 29 / 15479 = 0.002 (scenes 8 / 8042 = 0.001; predicted 0.05–0.08)
   the roads (S1b-1R's graders, covered targets): SPOKEN · TRUTH (n) · ×spoken · READ-BACK · SPEAK2 spoken · TRUTH-NEED (n) · MINIMAL (n) · ORDER (n) · DECLINE (reading) · M2b (the band, unchanged)
      CONTROL          0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      LAW              0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      HEALTH-MOUTH     0.737 · 0.804 (n 56) · 0.592 · 1.000 · 0.489 · 0.174 (n 23) · 1.000 (n 49) · 1.000 (n 5) · DECLINE 0.676 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 5, 'the read-back': 2, 'not held lately': 2} · SPEAK2 {'no believed-unique phrase': 13, 'not held lately': 3, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 5} · the row refused {'big:not held lately': 52, 'circle:not held lately': 21, 'green:not held lately': 25, 'white:not held lately': 20}
      HEALTH-ORACLE    0.803 · 0.836 (n 61) · 0.671 · 1.000 · 0.681 · 0.281 (n 32) · 1.000 (n 60) · 1.000 (n 10) · DECLINE 0.676 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 3, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 7, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 4} · the row refused {'white:not held lately': 20}
      HEALTH-TRUTHFED  0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      NULL             0.750 · 0.807 (n 57) · 0.605 · 1.000 · 0.468 · 0.227 (n 22) · 1.000 (n 51) · 1.000 (n 5) · DECLINE 0.919 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 6, 'the read-back': 1, 'not held lately': 1} · SPEAK2 {'no believed-unique phrase': 18, 'no sayable word': 7} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 8} · the row refused {'blue:not held lately': 22, 'green:not held lately': 25, 'small:not held lately': 45, 'yellow:not held lately': 15}
   the decision (over the CONTROL's spoken phrases on SPEAK + SPEAK2, covered): ERROR-RECALL (declined + replaced true / errors) · TRUE-RETENTION (true / true):
      CONTROL          ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
      HEALTH-MOUTH     ER 0.171 (6 + 0 / 35) · TR 0.790 (49 / 62)
      HEALTH-ORACLE    ER 0.057 (2 + 0 / 35) · TR 0.968 (60 / 62)
      HEALTH-TRUTHFED  ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
      NULL             ER 0.200 (7 + 0 / 35) · TR 0.823 (51 / 62)
      calibration of the truth-free row (the law's): ECE 0.106 · type-2 AUROC 0.567 · n 453 (errors 33; no row 0) · curve [0.7: n 159 conf 0.71 acc 0.91] [0.8: n 119 conf 0.81 acc 0.92] [0.9: n 175 conf 0.97 acc 0.95]
      calibration of the truth-fed row (its ceiling): ECE 0.017 · type-2 AUROC 0.635 · n 453 (errors 33; no row 0) · curve [0.8: n 42 conf 0.80 acc 0.76] [0.9: n 411 conf 0.96 acc 0.94]
      calibration of the deranged rows (the floor): ECE 0.142 · type-2 AUROC 0.464 · n 453 (errors 33; no row 0) · curve [0.7: n 166 conf 0.71 acc 0.92] [0.8: n 96 conf 0.81 acc 0.99] [0.9: n 191 conf 0.96 acc 0.90]
      the CONTROL re-graded vs S1b-1R's report.json: TRUTH [0.8225806451612904, 0.8225806451612904] · SPOKEN [0.8157894736842105, 0.8157894736842105] · TRUTH-NEED [0.3142857142857143, 0.3142857142857143] → EQUAL
   the wiring pin (READ-BACK 1.000 wherever something was spoken): PASS
5. the price, solo (the three lives above ran one at a time): lives 21.9 / 21.9 / 22.1 CPU-s · one seed's grading 0.3 CPU-s → the unit ≈ 67 CPU-s ≈ 1.1 CPU-min against ≤ 5 declared → within → PASS
GATE: STOP — the declared sign reversed by > 0.10 (step 3) · 66 s wall · 66 CPU-s
```

The amendment's predictions, read:
- **The residual** «within 0.05 on most words» [Likely]: 6 of 13 words. REFUTED.
- **The false-unseen rate** «≈ 0.05–0.08» [Likely]: 0.002 / 0.003 / 0.002. REFUTED, by being far below the range.
- **The metacognition-of-perception reading:** no prediction was written. It reads 0.023 / 0.018 / 0.027: by this rule, the learner does not know when its eye missed the referent.

### 10.5 · The diagnostic (18:27 +0400, 29.0 CPU-s, from code-8767cf6; read-only; it changes no verdict) — `gate-diag-amend1/diag.txt`, verbatim
```
== T-MEM-2 AMENDMENT 1 DIAGNOSTIC (seed 20261101; pin 8767cf6; identity PASS; read-only, the gate's verdict unchanged) ==
0. the gate's readings reproduced: never seen 45 / 1924 (gate 45 / 1924) · seen 29 / 15479 (gate 29 / 15479) → EQUAL
1. the rule's check (the said word among the held words at h*) against d_w(h*) ≤ band_w recomputed from the claim step's distances: 17403 / 17403 agree
2. per class — gradable · set aside · the said word's d_w / band_w at h*: p10 / median / p90 · held (≤ 1) · the type's words the band holds at h* (mean, of the type's n):
   A:  14181 ·   28 · 0.462 / 0.593 / 0.828 ·  14153 · shape 5.41 of 6 · colour 4.81 of 5 · size 1.98 of 2
   B:   1298 ·    1 · 0.470 / 0.598 / 0.847 ·   1297 · shape 5.41 of 6 · colour 4.82 of 5 · size 1.98 of 2
   C:   1924 ·   45 · 0.497 / 0.644 / 0.871 ·   1879 · shape 5.40 of 6 · colour 4.80 of 5 · size 1.98 of 2
3. class C by type — gradable · set aside · refuted (graded) · d_w / band_w median:
   shape    951 ·   27 ·   812 · 0.654
   colour   494 ·   16 ·   380 · 0.646
   size     479 ·    2 ·   200 · 0.614
cpu 29.0 s
```

The predictions, read:
- **P1 holds:** the rule's check agrees with the recomputation on 17,403 of 17,403 claims, and both counts reproduce, so there is no build fault.
- **P2 holds:** in class C the median d / band is 0.644, so the band holds the seen distractor.
- **P3 holds, and more strongly than written:** the band holds 5.4 of the 6 shapes and 4.8 of the 5 colours at a thing.
- **P4 holds:** 1.98 of the 2 sizes.

The band in the claims (S1b-1R's READER: a weighted 0.90 band over responsibility-weighted distances) is wide enough to hold nearly every word of a type. So the band cannot tell the thing the parent meant from a seen neighbour of the same type.

### 10.6 · The suites on the final code (95a6439)
- **The whole brain suite under the venv:** `Ran 606 tests in 266.232s` / `OK (skipped=3)`, with 0 ERROR/FAIL blocks. Log: `logs/suite-venv-95a6439.log`.
- **The scene package under /usr/bin/python3:** `Ran 204 tests in 54.930s` / `OK`, with 0 ERROR/FAIL blocks. Log: `logs/suite-scene-sys-95a6439.log`.

### 10.7 · Files
- **The amended gate:** `/data/dev/brain-runs/scene-tmem2/gate/` — `gate.txt`, `gate.json`, `journal.txt`, and `lives/<ws>/life/`.
- **The diagnostic:** `/data/dev/brain-runs/scene-tmem2/gate-diag-amend1/` — `diag.txt`, `diag.json`, `run.log`, and `lives/`.
- **The 17:51 STOP:** `/data/dev/brain-runs/scene-tmem2/gate-1751-stop/`.
- **The pins:** `code-8767cf6` (the amended gate's) and `code-15b047e` (the 17:51 gate's).
- **Untouched:** nothing was written under `/data/dev/brain-runs/scene-s1b1r/`. No unit other than `scene-tmem2-gate` was launched, and it is reset.

---

## 11 · AMENDMENT 2 — built test-first, gated PROCEED, the unit ran: T-MEM-2 does not pass

*edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 19:00 +0400 — appended. The law: PREREG-TMEM2 (b785b54f…), AMENDMENT 1 (6da8ff67…) and AMENDMENT 2 (final b1e2b15, sha 76d8ac86…), all three checked by the runner and required of the gate by the unit.*

*Gate records moved aside:*
- *§10's `gate/` (18:23, AMENDMENT 1's STOP) → `gate-1823-amend1-stop/`;*
- *the 18:45 PROCEED under code-0c811b9 → `gate-1845-amend2-proceed/`.*

### 11.1 · The answer
**The unit `scene-tmem2` ran 18:53:27–18:53:57 +0400 (exit 0, from code-00dc818). T-MEM-2 does not pass.**

| bar | result |
|---|---|
| B1 | PASS on all three seeds, but «met by the control» on all three. HEALTH-MOUTH's marks equal the CONTROL's on every seed. |
| B2 | CEILING-BOUND. HEALTH-ORACLE's pooled ERROR-RECALL is 0.077 (6 / 78), under 0.30, so the control's errors are the gaze's. HEALTH-MOUTH's is 0.000. |
| B3 | PASS. ECE 0.032 / 0.041 / 0.036, with the NULL's 0.022 / 0.023 / 0.049 printed beside. |
| B4 | FAIL. Pooled type-2 AUROC 0.495 over 93 errors (chance 0.50). |

A pass needs B4, so T-MEM-2 does not pass.

**Why it fails:**
- **The gate never closed.** After AMENDMENT 2, the truth-free row reads cal_20 ≥ 0.80 for every trained word on every seed. So HEALTH-MOUTH = CONTROL = NULL on all three seeds: it declined 0 of the 78 errors and kept all 222 true phrases.
- **The row cannot tell which names are wrong.** Its 13 per-word confidences (0.80–1.00 on the truth-free row) are calibrated in aggregate (ECE ≤ 0.041). They are blind to which believed name is wrong (AUROC 0.495).
- **A perfect per-word gate would not have helped.** HEALTH-ORACLE catches 6 of 78 errors: the errors are not the words'.

**Refutations (§6):**
- (a) The row buys silence: no.
- (b) The null clause is not met: YES. The NULL equals HEALTH-MOUTH because the gate refuses nothing.
- (c) CEILING-BOUND: YES.
- (d) The rows disagree by more than 0.10 on ≥ 3 words: no (0 / 1 / 2 words).

**The declared sign (§6), read on every seed:**
- Seed 20261103 reads circle and square at truth-free 0.850 against truth-fed 1.000. That is more than 0.10, the instrument-fault form, and the kept fed row reads 1.000 for both too.
- The gate's step 3 reads seed 20261101 only, as §7 says, and passed there: no word more than 0.10 below; circle exactly −0.100.
- This is printed as the report prints it; it is not a stop.

**AMENDMENT 2's readings** (offline, per gradable claim; per scene and per phrase beside):

| reading | 20261101 | 20261102 | 20261103 | pooled | predicted |
|---|---|---|---|---|---|
| metacognition-of-perception | 0.769 | 0.775 | 0.740 | 0.761 | ≈ 0.8 |
| false-unseen, per claim | 0.099 | 0.108 | 0.083 | 0.096 | 0.05–0.08 |
| false-unseen, per phrase | 0.075 | 0.085 | 0.066 | 0.075 | — |

The false-unseen rate per claim sits above the predicted range. Per phrase it sits within the range. A phrase with more claims is set aside more often when «none» fires on a seen referent.

### 11.2 · The build
- **Commits on `scene-tmem2`:**
  - **0c811b9** — AMENDMENT 2, test-first:
    - `health.heard_none`;
    - `health.grades(..., set_aside=)`, with AMENDMENT 1's band rule removed;
    - the hook's `heard` step, between the claims and `train_scene`;
    - the truth-fed row with no rule, and its kept twin;
    - the readings per claim, scene and phrase;
    - the three shas.
  - **00dc818** — the report fix, test-first.
  - this section.
- **Red:**
  - AMENDMENT 2's rows on 75ef77e: `Ran 30 tests … FAILED (failures=4, errors=7)` (log `redcheck-75ef77e/red.log`);
  - the report test on 0c811b9: `Ran 16 tests … FAILED (errors=1)`, the same TypeError as the unit's (log `redcheck-0c811b9/red.log`).
- **Green:**
  - the T-MEM-2 modules: `Ran 48 tests … OK`;
  - the scene suite on the fixed bytes: `Ran 211 tests in 51.490s` / `OK`;
  - the suites on the final commit: §11.6.
- **Declared readings of AMENDMENT 2:**
  1. **The pointing.** «None» is `RWRoad.answer_point`: the LAW road, with «none» = S1b-1R's none_i, the best phrase score below τ_point.
     - It runs over the scene's hypotheses (the things the gaze landed on), with the phrase exactly as said.
     - It runs in the state before `train_scene`: the ear has not heard the phrase and the statistics have not observed the scene's things.
     - Its generator is the hook's own, `substream(ws, "tmem2-none:<scene>")`. It is drawn only on a tie of the pick, and «none» reads the best score, not the pick.
  2. **A phrase with a never-heard word** points at nothing («none» None), so nothing is set aside. This is the «dax» scene only.
  3. **The truth-fed row carries no rule.** Its kept twin (Fable's edit) is the fed grades from scenes where «none» did not fire. Both are printed, and step 3's STOP reads the whole fed row, unchanged.
  4. **The readings count gradable claims of the truth-free row**, graded or set aside, as the amendment defines them. Beside them, per scene (every gradable claim set aside) and per phrase heard.
  5. **The claim record still carries AMENDMENT 1's held words**, read by no rule.
- **The unit's first launch** (18:47:54, from code-0c811b9) ran the three lives (identity PASS) and all three graders, then crashed at the REPORT step:
  - the error was `TypeError: '<' not supported between instances of 'str' and 'int'`: run.dump's `sort_keys` over bars_tmem2's refutations, a dict mixing the seeds (ints) with two pooled names (strs);
  - no test had run the report before, because it needs three seeds' marks;
  - fixed test-first in 00dc818: the per-seed refutations now sit under `per_seed`;
  - the crashed unit's outputs are kept in `unit-1847-report-crash/`. Its marks equal the final unit's on all three seeds, apart from the life CPU;
  - the gate was re-run from code-00dc818 (18:51:54 – 18:53:16, PROCEED). Its gate.txt equals the 18:45 gate's except for the lives' CPU seconds. Then the unit ran.

### 11.3 · THE FIRST GATE under AMENDMENT 2 (from code-00dc818) — `gate/gate.txt`, verbatim
```
== THE FIRST GATE (PREREG-TMEM2 §7 + AMENDMENT 1 §4 + AMENDMENT 2 §4; each step a STOP on a miss; printed whole) ==
   the law: PREREG-TMEM2 b785b54f97c6c2bc… · AMENDMENT 1 6da8ff679a317166… · AMENDMENT 2 76d8ac86c0af8320… · code 00dc818a45a50d39edb24a227a6383fe90130cab
0. the CONTROL's record: /data/dev/brain-runs/scene-s1b1r/report.txt sha as recorded (b695ae5c94d13a85…)
1. THE IDENTITY (S1b-1R's A-RW-R record at 10,000; canonical JSON; the planted one-byte change first):
   20261101: point = (188211 bytes; planted CAUGHT) · LAW = (72118 bytes; planted CAUGHT) · summary = (1465 bytes; planted CAUGHT) · cpu 25.9 s → PASS
   20261102: point = (187763 bytes; planted CAUGHT) · LAW = (75822 bytes; planted CAUGHT) · summary = (1458 bytes; planted CAUGHT) · cpu 25.7 s → PASS
   20261103: point = (187927 bytes; planted CAUGHT) · LAW = (75263 bytes; planted CAUGHT) · summary = (1464 bytes; planted CAUGHT) · cpu 25.9 s → PASS
2. the row's toy (A 95 %, B 50 %, 200 graded claims each): seed 0: cal_20 A 0.95 B 0.65 · kept {'A': True, 'B': False} · the null {'A': False, 'B': True} · an ungraded claim moves nothing True · a claim set aside «unseen» moves nothing True · seed 1: cal_20 A 1.00 B 0.45 · kept {'A': True, 'B': False} · the null {'A': False, 'B': True} · an ungraded claim moves nothing True · a claim set aside «unseen» moves nothing True · seed 2: cal_20 A 0.95 B 0.50 · kept {'A': True, 'B': False} · the null {'A': False, 'B': True} · an ungraded claim moves nothing True · a claim set aside «unseen» moves nothing True → PASS
3. agreement and coverage on seed 20261101's stream (claims on 9750 scenes), AFTER AMENDMENT 2's rule — per word: graded truth-free / truth-fed / fed-kept · set aside «unseen» (truth-free) · cal_20 truth-free / truth-fed (the whole row: the STOP) / fed-kept (the claims the rule keeps: a reading) · the residual free − fed · free − fed-kept:
   big        1660 /  1848 /  1625 ·  495 · 0.850 / 0.900 / 0.900 · -0.050 · -0.050  reversed (a reading)
   blue        661 /   771 /   652 ·  164 · 0.900 / 0.950 / 0.950 · -0.050 · -0.050  reversed (a reading)
   circle     1487 /  1453 /  1380 ·  301 · 0.900 / 1.000 / 1.000 · -0.100 · -0.100  reversed (a reading)
   cross      1221 /  1263 /  1182 ·  143 · 1.000 / 1.000 / 1.000 · +0.000 · +0.000
   green       846 /   929 /   820 ·  217 · 1.000 / 0.950 / 1.000 · +0.050 · +0.000
   red         541 /   642 /   535 ·  167 · 1.000 / 1.000 / 1.000 · +0.000 · +0.000
   ring       1117 /  1183 /  1078 ·  136 · 0.900 / 0.900 / 0.900 · +0.000 · +0.000
   small      1801 /  2009 /  1761 ·  421 · 0.900 / 0.950 / 0.900 · -0.050 · +0.000  reversed (a reading)
   square     1065 /  1057 /  1002 ·  201 · 0.950 / 1.000 / 1.000 · -0.050 · -0.050  reversed (a reading)
   star       1373 /  1438 /  1330 ·  195 · 1.000 / 1.000 / 1.000 · +0.000 · +0.000
   triangle   1341 /  1382 /  1292 ·  175 · 0.950 / 1.000 / 1.000 · -0.050 · -0.050  reversed (a reading)
   white       705 /   760 /   696 ·  194 · 0.900 / 0.800 / 0.850 · +0.100 · +0.050
   yellow      576 /   634 /   567 ·  200 · 0.900 / 0.950 / 0.950 · -0.050 · -0.050  reversed (a reading)
   the residual (free − the whole fed row) within 0.05 on 11 of 13 words; more than 0.10 below the kept fed row (a reading): none
   «no row»: none · reversed: ['big', 'blue', 'circle', 'small', 'square', 'triangle', 'yellow'] · the fault (> 0.10): none → PASS
   AMENDMENT 1's readings (offline, the tape's truth; readings, never bars), every gate life:
      20261101: the metacognition-of-perception reading (the referent never seen): claims set aside 1480 / 1924 = 0.769 (scenes 647 / 977 = 0.662; phrases «none» 673 / 1039 = 0.648; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1529 / 15479 = 0.099 (scenes 594 / 8042 = 0.074; phrases «none» 656 / 8711 = 0.075; predicted 0.05–0.08)
      20261102: the metacognition-of-perception reading (the referent never seen): claims set aside 1469 / 1896 = 0.775 (scenes 670 / 995 = 0.673; phrases «none» 701 / 1056 = 0.664; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1661 / 15418 = 0.108 (scenes 658 / 8002 = 0.082; phrases «none» 742 / 8694 = 0.085; predicted 0.05–0.08)
      20261103: the metacognition-of-perception reading (the referent never seen): claims set aside 1401 / 1893 = 0.740 (scenes 619 / 986 = 0.628; phrases «none» 640 / 1028 = 0.623; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1280 / 15475 = 0.083 (scenes 501 / 8064 = 0.062; phrases «none» 572 / 8722 = 0.066; predicted 0.05–0.08)
4. the smoke — seed 20261101's fresh items under all four roads (the tables whole):
      big       claims  6311 · graded  1660 (fed  1848) · unseen  495 (fed    0) · cal_20 0.850 / 0.900 (kept 0.900) · |diff| 0.050 · median |Δ| 0.050 · drift 3 / 3 · missed  151 · gate open · oracle 0.984
      blue      claims  2520 · graded   661 (fed   771) · unseen  164 (fed    0) · cal_20 0.900 / 0.950 (kept 0.950) · |diff| 0.050 · median |Δ| 0.050 · drift 1 / 1 · missed   48 · gate open · oracle 1.000
      circle    claims  2572 · graded  1487 (fed  1453) · unseen  301 (fed    0) · cal_20 0.900 / 1.000 (kept 1.000) · |diff| 0.100 · median |Δ| 0.050 · drift 5 / 5 · missed   18 · gate open · oracle 1.000
      cross     claims  2190 · graded  1221 (fed  1263) · unseen  143 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 6 / 1 · missed   32 · gate open · oracle 1.000
      green     claims  3436 · graded   846 (fed   929) · unseen  217 (fed    0) · cal_20 1.000 / 0.950 (kept 1.000) · |diff| 0.050 · median |Δ| 0.050 · drift 1 / 1 · missed   43 · gate open · oracle 0.900
      red       claims  2124 · graded   541 (fed   642) · unseen  167 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.100 · drift 0 / 0 · missed   57 · gate open · oracle 0.871
      ring      claims  1682 · graded  1117 (fed  1183) · unseen  136 (fed    0) · cal_20 0.900 / 0.900 (kept 0.900) · |diff| 0.000 · median |Δ| 0.050 · drift 5 / 0 · missed  198 · gate open · oracle 0.886
      small     claims  6768 · graded  1801 (fed  2009) · unseen  421 (fed    0) · cal_20 0.900 / 0.950 (kept 0.900) · |diff| 0.050 · median |Δ| 0.050 · drift 2 / 2 · missed   84 · gate open · oracle 0.886
      square    claims  1887 · graded  1065 (fed  1057) · unseen  201 (fed    0) · cal_20 0.950 / 1.000 (kept 1.000) · |diff| 0.050 · median |Δ| 0.050 · drift 0 / 0 · missed   16 · gate open · oracle 1.000
      star      claims  2505 · graded  1373 (fed  1438) · unseen  195 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 1 / 0 · missed   24 · gate open · oracle 1.000
      triangle  claims  2380 · graded  1341 (fed  1382) · unseen  175 (fed    0) · cal_20 0.950 / 1.000 (kept 1.000) · |diff| 0.050 · median |Δ| 0.000 · drift 14 / 2 · missed   16 · gate open · oracle 1.000
      white     claims  2715 · graded   705 (fed   760) · unseen  194 (fed    0) · cal_20 0.900 / 0.800 (kept 0.850) · |diff| 0.100 · median |Δ| 0.050 · drift 4 / 4 · missed  114 · gate open · oracle 0.762
      yellow    claims  2212 · graded   576 (fed   634) · unseen  200 (fed    0) · cal_20 0.900 / 0.950 (kept 0.950) · |diff| 0.050 · median |Δ| 0.050 · drift 0 / 0 · missed   71 · gate open · oracle 1.000
   AMENDMENT 1's readings (offline, the tape's truth; readings, never bars): 20261101: the metacognition-of-perception reading (the referent never seen): claims set aside 1480 / 1924 = 0.769 (scenes 647 / 977 = 0.662; phrases «none» 673 / 1039 = 0.648; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1529 / 15479 = 0.099 (scenes 594 / 8042 = 0.074; phrases «none» 656 / 8711 = 0.075; predicted 0.05–0.08)
   the roads (S1b-1R's graders, covered targets): SPOKEN · TRUTH (n) · ×spoken · READ-BACK · SPEAK2 spoken · TRUTH-NEED (n) · MINIMAL (n) · ORDER (n) · DECLINE (reading) · M2b (the band, unchanged)
      CONTROL          0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      LAW              0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      HEALTH-MOUTH     0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      HEALTH-ORACLE    0.803 · 0.836 (n 61) · 0.671 · 1.000 · 0.681 · 0.281 (n 32) · 1.000 (n 60) · 1.000 (n 10) · DECLINE 0.676 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 3, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 7, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 4} · the row refused {'white:not held lately': 20}
      HEALTH-TRUTHFED  0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
      NULL             0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                       reasons SPEAK {'no sayable word': 11, 'no believed-unique phrase': 2, 'the read-back': 1} · SPEAK2 {'no sayable word': 7, 'the read-back': 1, 'no believed-unique phrase': 4} · DECLINE {'no sayable word': 5, 'no believed-unique phrase': 3}
   the decision (over the CONTROL's spoken phrases on SPEAK + SPEAK2, covered): ERROR-RECALL (declined + replaced true / errors) · TRUE-RETENTION (true / true):
      CONTROL          ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
      HEALTH-MOUTH     ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
      HEALTH-ORACLE    ER 0.057 (2 + 0 / 35) · TR 0.968 (60 / 62)
      HEALTH-TRUTHFED  ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
      NULL             ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
      calibration of the truth-free row (the law's): ECE 0.032 · type-2 AUROC 0.502 · n 453 (errors 33; no row 0) · curve [0.8: n 63 conf 0.85 acc 0.98] [0.9: n 390 conf 0.93 acc 0.92]
      calibration of the truth-fed row (its ceiling): ECE 0.012 · type-2 AUROC 0.654 · n 453 (errors 33; no row 0) · curve [0.8: n 42 conf 0.80 acc 0.76] [0.9: n 411 conf 0.95 acc 0.94]
      calibration of the deranged rows (the floor): ECE 0.022 · type-2 AUROC 0.511 · n 453 (errors 33; no row 0) · curve [0.8: n 26 conf 0.85 acc 1.00] [0.9: n 427 conf 0.94 acc 0.92]
      the CONTROL re-graded vs S1b-1R's report.json: TRUTH [0.8225806451612904, 0.8225806451612904] · SPOKEN [0.8157894736842105, 0.8157894736842105] · TRUTH-NEED [0.3142857142857143, 0.3142857142857143] → EQUAL
   the wiring pin (READ-BACK 1.000 wherever something was spoken): PASS
5. the price, solo (the three lives above ran one at a time): lives 25.9 / 25.7 / 25.9 CPU-s · one seed's grading 0.3 CPU-s → the unit ≈ 78 CPU-s ≈ 1.3 CPU-min against ≤ 5 declared → within → PASS
GATE: PROCEED · 78 s wall · 78 CPU-s
```

### 11.4 · The unit's report — `report.txt`, verbatim
```
T-MEM-2 report · PREREG-TMEM2 sha b785b54f97c6c2bc300ce07cdc26aaa716bf9c7fcb3e7cc183294480b5fd2914 · AMENDMENT 1 sha 6da8ff679a317166c7a4e82bf9efd183785b5ecb90ad1bcb6fbae90d241386e6 · AMENDMENT 2 sha 76d8ac86c0af8320b1b96fa48621cf6a016e0c4037437489edbd186b56c758bf · PREREG-S1B1R 879a22fbe5341330… · the control's report.txt b695ae5c94d13a85…

== T-MEM-2 · world seed 20261101 (fresh test seed 20261401) ==
the identity with S1b-1R's A-RW-R record at 10,000 (canonical JSON; the planted byte first): LAW = (72118 bytes; planted CAUGHT) · point = (188211 bytes; planted CAUGHT) · summary = (1465 bytes; planted CAUGHT) → PASS
the learned types: (circle cross ring square star triangle) (blue green red white yellow) (big small) · claims recorded on 9750 training scenes
the rows at 10,000 (per word: confident claims · graded · set aside «unseen» · cal_20 truth-free / truth-fed (the fed row on the claims the rule keeps) · |diff| · median |Δ| · drift firings unfloored / floored 1/20 · the said word's MISSED · the gate · the oracle's accuracy):
   big       claims  6311 · graded  1660 (fed  1848) · unseen  495 (fed    0) · cal_20 0.850 / 0.900 (kept 0.900) · |diff| 0.050 · median |Δ| 0.050 · drift 3 / 3 · missed  151 · gate open · oracle 0.984
   blue      claims  2520 · graded   661 (fed   771) · unseen  164 (fed    0) · cal_20 0.900 / 0.950 (kept 0.950) · |diff| 0.050 · median |Δ| 0.050 · drift 1 / 1 · missed   48 · gate open · oracle 1.000
   circle    claims  2572 · graded  1487 (fed  1453) · unseen  301 (fed    0) · cal_20 0.900 / 1.000 (kept 1.000) · |diff| 0.100 · median |Δ| 0.050 · drift 5 / 5 · missed   18 · gate open · oracle 1.000
   cross     claims  2190 · graded  1221 (fed  1263) · unseen  143 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 6 / 1 · missed   32 · gate open · oracle 1.000
   green     claims  3436 · graded   846 (fed   929) · unseen  217 (fed    0) · cal_20 1.000 / 0.950 (kept 1.000) · |diff| 0.050 · median |Δ| 0.050 · drift 1 / 1 · missed   43 · gate open · oracle 0.900
   red       claims  2124 · graded   541 (fed   642) · unseen  167 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.100 · drift 0 / 0 · missed   57 · gate open · oracle 0.871
   ring      claims  1682 · graded  1117 (fed  1183) · unseen  136 (fed    0) · cal_20 0.900 / 0.900 (kept 0.900) · |diff| 0.000 · median |Δ| 0.050 · drift 5 / 0 · missed  198 · gate open · oracle 0.886
   small     claims  6768 · graded  1801 (fed  2009) · unseen  421 (fed    0) · cal_20 0.900 / 0.950 (kept 0.900) · |diff| 0.050 · median |Δ| 0.050 · drift 2 / 2 · missed   84 · gate open · oracle 0.886
   square    claims  1887 · graded  1065 (fed  1057) · unseen  201 (fed    0) · cal_20 0.950 / 1.000 (kept 1.000) · |diff| 0.050 · median |Δ| 0.050 · drift 0 / 0 · missed   16 · gate open · oracle 1.000
   star      claims  2505 · graded  1373 (fed  1438) · unseen  195 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 1 / 0 · missed   24 · gate open · oracle 1.000
   triangle  claims  2380 · graded  1341 (fed  1382) · unseen  175 (fed    0) · cal_20 0.950 / 1.000 (kept 1.000) · |diff| 0.050 · median |Δ| 0.000 · drift 14 / 2 · missed   16 · gate open · oracle 1.000
   white     claims  2715 · graded   705 (fed   760) · unseen  194 (fed    0) · cal_20 0.900 / 0.800 (kept 0.850) · |diff| 0.100 · median |Δ| 0.050 · drift 4 / 4 · missed  114 · gate open · oracle 0.762
   yellow    claims  2212 · graded   576 (fed   634) · unseen  200 (fed    0) · cal_20 0.900 / 0.950 (kept 0.950) · |diff| 0.050 · median |Δ| 0.050 · drift 0 / 0 · missed   71 · gate open · oracle 1.000
AMENDMENT 1's readings (offline, the tape's truth; readings, never bars): 20261101: the metacognition-of-perception reading (the referent never seen): claims set aside 1480 / 1924 = 0.769 (scenes 647 / 977 = 0.662; phrases «none» 673 / 1039 = 0.648; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1529 / 15479 = 0.099 (scenes 594 / 8042 = 0.074; phrases «none» 656 / 8711 = 0.075; predicted 0.05–0.08)
the roads (S1b-1R's graders, covered targets): SPOKEN · TRUTH (n) · ×spoken · READ-BACK · SPEAK2 spoken · TRUTH-NEED (n) · MINIMAL (n) · ORDER (n) · DECLINE (reading) · M2b (the band, unchanged)
   CONTROL          0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                    reasons SPEAK {'no believed-unique phrase': 2, 'no sayable word': 11, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 4, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 3, 'no sayable word': 5}
   LAW              0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                    reasons SPEAK {'no believed-unique phrase': 2, 'no sayable word': 11, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 4, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 3, 'no sayable word': 5}
   HEALTH-MOUTH     0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                    reasons SPEAK {'no believed-unique phrase': 2, 'no sayable word': 11, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 4, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 3, 'no sayable word': 5}
   HEALTH-ORACLE    0.803 · 0.836 (n 61) · 0.671 · 1.000 · 0.681 · 0.281 (n 32) · 1.000 (n 60) · 1.000 (n 10) · DECLINE 0.676 · M2b 0.646
                    reasons SPEAK {'no believed-unique phrase': 3, 'no sayable word': 11, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 7, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 4, 'no sayable word': 5} · the row refused {'white:not held lately': 20}
   HEALTH-TRUTHFED  0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                    reasons SPEAK {'no believed-unique phrase': 2, 'no sayable word': 11, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 4, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 3, 'no sayable word': 5}
   NULL             0.816 · 0.823 (n 62) · 0.671 · 1.000 · 0.745 · 0.314 (n 35) · 1.000 (n 62) · 1.000 (n 12) · DECLINE 0.649 · M2b 0.646
                    reasons SPEAK {'no believed-unique phrase': 2, 'no sayable word': 11, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 4, 'no sayable word': 7, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 3, 'no sayable word': 5}
the decision (over the CONTROL's spoken phrases on SPEAK + SPEAK2, covered): ERROR-RECALL (declined + replaced true / errors) · TRUE-RETENTION (true / true):
   CONTROL          ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
   HEALTH-MOUTH     ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
   HEALTH-ORACLE    ER 0.057 (2 + 0 / 35) · TR 0.968 (60 / 62)
   HEALTH-TRUTHFED  ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
   NULL             ER 0.000 (0 + 0 / 35) · TR 1.000 (62 / 62)
   calibration of the truth-free row (the law's): ECE 0.032 · type-2 AUROC 0.502 · n 453 (errors 33; no row 0) · curve [0.8: n 63 conf 0.85 acc 0.98] [0.9: n 390 conf 0.93 acc 0.92]
   calibration of the truth-fed row (its ceiling): ECE 0.012 · type-2 AUROC 0.654 · n 453 (errors 33; no row 0) · curve [0.8: n 42 conf 0.80 acc 0.76] [0.9: n 411 conf 0.95 acc 0.94]
   calibration of the deranged rows (the floor): ECE 0.022 · type-2 AUROC 0.511 · n 453 (errors 33; no row 0) · curve [0.8: n 26 conf 0.85 acc 1.00] [0.9: n 427 conf 0.94 acc 0.92]
   the CONTROL re-graded vs S1b-1R's report.json: TRUTH [0.8225806451612904, 0.8225806451612904] · SPOKEN [0.8157894736842105, 0.8157894736842105] · TRUTH-NEED [0.3142857142857143, 0.3142857142857143] → EQUAL

== T-MEM-2 · world seed 20261102 (fresh test seed 20261402) ==
the identity with S1b-1R's A-RW-R record at 10,000 (canonical JSON; the planted byte first): LAW = (75822 bytes; planted CAUGHT) · point = (187763 bytes; planted CAUGHT) · summary = (1458 bytes; planted CAUGHT) → PASS
the learned types: (circle cross ring square star triangle) (blue green red white yellow) (big small) · claims recorded on 9750 training scenes
the rows at 10,000 (per word: confident claims · graded · set aside «unseen» · cal_20 truth-free / truth-fed (the fed row on the claims the rule keeps) · |diff| · median |Δ| · drift firings unfloored / floored 1/20 · the said word's MISSED · the gate · the oracle's accuracy):
   big       claims  6288 · graded  1671 (fed  1848) · unseen  505 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 6 / 3 · missed  132 · gate open · oracle 0.961
   blue      claims  2569 · graded   650 (fed   753) · unseen  154 (fed    0) · cal_20 1.000 / 0.900 (kept 1.000) · |diff| 0.100 · median |Δ| 0.050 · drift 1 / 1 · missed   44 · gate open · oracle 0.791
   circle    claims  2503 · graded  1439 (fed  1411) · unseen  288 (fed    0) · cal_20 0.950 / 1.000 (kept 1.000) · |diff| 0.050 · median |Δ| 0.050 · drift 4 / 4 · missed   34 · gate open · oracle 1.000
   cross     claims  2236 · graded  1276 (fed  1313) · unseen  155 (fed    0) · cal_20 0.950 / 1.000 (kept 1.000) · |diff| 0.050 · median |Δ| 0.050 · drift 11 / 0 · missed   32 · gate open · oracle 1.000
   green     claims  3349 · graded   875 (fed  1005) · unseen  226 (fed    0) · cal_20 0.950 / 1.000 (kept 1.000) · |diff| 0.050 · median |Δ| 0.050 · drift 4 / 4 · missed   43 · gate open · oracle 0.931
   red       claims  2168 · graded   546 (fed   639) · unseen  152 (fed    0) · cal_20 0.900 / 0.750 (kept 0.850) · |diff| 0.150 · median |Δ| 0.050 · drift 2 / 2 · missed   41 · gate open · oracle 0.884
   ring      claims  1628 · graded  1060 (fed  1156) · unseen  159 (fed    0) · cal_20 0.950 / 0.900 (kept 0.950) · |diff| 0.050 · median |Δ| 0.050 · drift 2 / 2 · missed  217 · gate open · oracle 1.000
   small     claims  6622 · graded  1753 (fed  2005) · unseen  453 (fed    0) · cal_20 1.000 / 0.950 (kept 0.950) · |diff| 0.050 · median |Δ| 0.050 · drift 4 / 4 · missed   82 · gate open · oracle 0.932
   square    claims  1813 · graded  1038 (fed  1019) · unseen  198 (fed    0) · cal_20 0.950 / 1.000 (kept 1.000) · |diff| 0.050 · median |Δ| 0.050 · drift 4 / 4 · missed   28 · gate open · oracle 1.000
   star      claims  2415 · graded  1306 (fed  1375) · unseen  217 (fed    0) · cal_20 0.900 / 1.000 (kept 1.000) · |diff| 0.100 · median |Δ| 0.050 · drift 2 / 1 · missed    9 · gate open · oracle 0.964
   triangle  claims  2367 · graded  1340 (fed  1393) · unseen  185 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.000 · drift 9 / 0 · missed   19 · gate open · oracle 1.000
   white     claims  2580 · graded   697 (fed   770) · unseen  218 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 2 / 2 · missed  112 · gate open · oracle 0.793
   yellow    claims  2213 · graded   533 (fed   617) · unseen  220 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 3 / 2 · missed   71 · gate open · oracle 0.905
AMENDMENT 1's readings (offline, the tape's truth; readings, never bars): 20261102: the metacognition-of-perception reading (the referent never seen): claims set aside 1469 / 1896 = 0.775 (scenes 670 / 995 = 0.673; phrases «none» 701 / 1056 = 0.664; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1661 / 15418 = 0.108 (scenes 658 / 8002 = 0.082; phrases «none» 742 / 8694 = 0.085; predicted 0.05–0.08)
the roads (S1b-1R's graders, covered targets): SPOKEN · TRUTH (n) · ×spoken · READ-BACK · SPEAK2 spoken · TRUTH-NEED (n) · MINIMAL (n) · ORDER (n) · DECLINE (reading) · M2b (the band, unchanged)
   CONTROL          0.875 · 0.968 (n 63) · 0.847 · 1.000 · 0.891 · 0.561 (n 41) · 0.988 (n 84) · 1.000 (n 25) · DECLINE 0.649 · M2b 0.708
                    reasons SPEAK {'no believed-unique phrase': 1, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 1, 'no sayable word': 4} · DECLINE {'no sayable word': 2}
   LAW              0.875 · 0.968 (n 63) · 0.847 · 1.000 · 0.891 · 0.561 (n 41) · 0.988 (n 84) · 1.000 (n 25) · DECLINE 0.649 · M2b 0.708
                    reasons SPEAK {'no believed-unique phrase': 1, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 1, 'no sayable word': 4} · DECLINE {'no sayable word': 2}
   HEALTH-MOUTH     0.875 · 0.968 (n 63) · 0.847 · 1.000 · 0.891 · 0.561 (n 41) · 0.988 (n 84) · 1.000 (n 25) · DECLINE 0.649 · M2b 0.708
                    reasons SPEAK {'no believed-unique phrase': 1, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 1, 'no sayable word': 4} · DECLINE {'no sayable word': 2}
   HEALTH-ORACLE    0.819 · 0.932 (n 59) · 0.764 · 1.000 · 0.696 · 0.562 (n 32) · 0.986 (n 73) · 1.000 (n 19) · DECLINE 0.946 · M2b 0.708
                    reasons SPEAK {'no believed-unique phrase': 4, 'no sayable word': 8, 'the read-back': 1} · SPEAK2 {'no believed-unique phrase': 9, 'no sayable word': 4, 'not held lately': 1} · DECLINE {'no believed-unique phrase': 11, 'no sayable word': 2} · the row refused {'blue:not held lately': 14, 'white:not held lately': 29}
   HEALTH-TRUTHFED  0.847 · 0.951 (n 61) · 0.806 · 1.000 · 0.826 · 0.526 (n 38) · 1.000 (n 78) · 1.000 (n 21) · DECLINE 0.703 · M2b 0.708
                    reasons SPEAK {'no believed-unique phrase': 2, 'no sayable word': 8, 'not held lately': 1} · SPEAK2 {'no believed-unique phrase': 4, 'no sayable word': 4} · DECLINE {'no believed-unique phrase': 1, 'no sayable word': 2} · the row refused {'red:not held lately': 16}
   NULL             0.875 · 0.968 (n 63) · 0.847 · 1.000 · 0.891 · 0.561 (n 41) · 0.988 (n 84) · 1.000 (n 25) · DECLINE 0.649 · M2b 0.708
                    reasons SPEAK {'no believed-unique phrase': 1, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 1, 'no sayable word': 4} · DECLINE {'no sayable word': 2}
the decision (over the CONTROL's spoken phrases on SPEAK + SPEAK2, covered): ERROR-RECALL (declined + replaced true / errors) · TRUE-RETENTION (true / true):
   CONTROL          ER 0.000 (0 + 0 / 20) · TR 1.000 (84 / 84)
   HEALTH-MOUTH     ER 0.000 (0 + 0 / 20) · TR 1.000 (84 / 84)
   HEALTH-ORACLE    ER 0.200 (4 + 0 / 20) · TR 0.869 (73 / 84)
   HEALTH-TRUTHFED  ER 0.000 (0 + 0 / 20) · TR 0.929 (78 / 84)
   NULL             ER 0.000 (0 + 0 / 20) · TR 1.000 (84 / 84)
   calibration of the truth-free row (the law's): ECE 0.041 · type-2 AUROC 0.430 · n 495 (errors 34; no row 0) · curve [0.9: n 495 conf 0.97 acc 0.93]
   calibration of the truth-fed row (its ceiling): ECE 0.046 · type-2 AUROC 0.609 · n 495 (errors 34; no row 0) · curve [0.7: n 43 conf 0.75 acc 0.88] [0.9: n 452 conf 0.97 acc 0.94]
   calibration of the deranged rows (the floor): ECE 0.023 · type-2 AUROC 0.441 · n 495 (errors 34; no row 0) · curve [0.9: n 495 conf 0.95 acc 0.93]
   the CONTROL re-graded vs S1b-1R's report.json: TRUTH [0.9682539682539683, 0.9682539682539683] · SPOKEN [0.875, 0.875] · TRUTH-NEED [0.5609756097560976, 0.5609756097560976] → EQUAL

== T-MEM-2 · world seed 20261103 (fresh test seed 20261403) ==
the identity with S1b-1R's A-RW-R record at 10,000 (canonical JSON; the planted byte first): LAW = (75263 bytes; planted CAUGHT) · point = (187927 bytes; planted CAUGHT) · summary = (1464 bytes; planted CAUGHT) → PASS
the learned types: (circle cross ring square star triangle) (blue green red white yellow) (big small) · claims recorded on 9750 training scenes
the rows at 10,000 (per word: confident claims · graded · set aside «unseen» · cal_20 truth-free / truth-fed (the fed row on the claims the rule keeps) · |diff| · median |Δ| · drift firings unfloored / floored 1/20 · the said word's MISSED · the gate · the oracle's accuracy):
   big       claims  6514 · graded  1812 (fed  1945) · unseen  449 (fed    0) · cal_20 0.900 / 0.900 (kept 0.900) · |diff| 0.000 · median |Δ| 0.050 · drift 8 / 2 · missed  140 · gate open · oracle 0.947
   blue      claims  2671 · graded   679 (fed   778) · unseen  138 (fed    0) · cal_20 0.900 / 1.000 (kept 0.900) · |diff| 0.100 · median |Δ| 0.050 · drift 2 / 2 · missed   46 · gate open · oracle 1.000
   circle    claims  2640 · graded  1524 (fed  1475) · unseen  275 (fed    0) · cal_20 0.850 / 1.000 (kept 1.000) · |diff| 0.150 · median |Δ| 0.050 · drift 10 / 5 · missed   20 · gate open · oracle 1.000
   cross     claims  2249 · graded  1286 (fed  1323) · unseen  141 (fed    0) · cal_20 0.950 / 1.000 (kept 1.000) · |diff| 0.050 · median |Δ| 0.000 · drift 15 / 0 · missed   37 · gate open · oracle 0.963
   green     claims  3430 · graded   898 (fed   980) · unseen  188 (fed    0) · cal_20 0.950 / 0.900 (kept 0.950) · |diff| 0.050 · median |Δ| 0.050 · drift 2 / 2 · missed   60 · gate open · oracle 0.943
   red       claims  2102 · graded   534 (fed   607) · unseen  137 (fed    0) · cal_20 0.850 / 0.850 (kept 0.800) · |diff| 0.000 · median |Δ| 0.000 · drift 1 / 0 · missed   51 · gate open · oracle 0.913
   ring      claims  1749 · graded  1218 (fed  1268) · unseen  116 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 3 / 1 · missed  226 · gate open · oracle 1.000
   small     claims  6581 · graded  1697 (fed  1867) · unseen  370 (fed    0) · cal_20 0.800 / 0.750 (kept 0.800) · |diff| 0.050 · median |Δ| 0.050 · drift 4 / 4 · missed  106 · gate open · oracle 0.898
   square    claims  1813 · graded  1051 (fed  1017) · unseen  157 (fed    0) · cal_20 0.850 / 1.000 (kept 1.000) · |diff| 0.150 · median |Δ| 0.050 · drift 1 / 1 · missed   14 · gate open · oracle 1.000
   star      claims  2519 · graded  1410 (fed  1437) · unseen  185 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 3 / 2 · missed   19 · gate open · oracle 1.000
   triangle  claims  2307 · graded  1253 (fed  1290) · unseen  170 (fed    0) · cal_20 1.000 / 1.000 (kept 1.000) · |diff| 0.000 · median |Δ| 0.050 · drift 0 / 0 · missed   20 · gate open · oracle 1.000
   white     claims  2610 · graded   711 (fed   746) · unseen  186 (fed    0) · cal_20 1.000 / 0.950 (kept 1.000) · |diff| 0.050 · median |Δ| 0.050 · drift 3 / 3 · missed  123 · gate open · oracle 0.821
   yellow    claims  2226 · graded   614 (fed   660) · unseen  169 (fed    0) · cal_20 0.900 / 0.900 (kept 0.900) · |diff| 0.000 · median |Δ| 0.050 · drift 1 / 1 · missed   57 · gate open · oracle 1.000
AMENDMENT 1's readings (offline, the tape's truth; readings, never bars): 20261103: the metacognition-of-perception reading (the referent never seen): claims set aside 1401 / 1893 = 0.740 (scenes 619 / 986 = 0.628; phrases «none» 640 / 1028 = 0.623; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1280 / 15475 = 0.083 (scenes 501 / 8064 = 0.062; phrases «none» 572 / 8722 = 0.066; predicted 0.05–0.08)
the roads (S1b-1R's graders, covered targets): SPOKEN · TRUTH (n) · ×spoken · READ-BACK · SPEAK2 spoken · TRUTH-NEED (n) · MINIMAL (n) · ORDER (n) · DECLINE (reading) · M2b (the band, unchanged)
   CONTROL          0.882 · 0.955 (n 67) · 0.842 · 1.000 · 0.727 · 0.375 (n 32) · 1.000 (n 76) · 1.000 (n 13) · DECLINE 0.658 · M2b 0.729
                    reasons SPEAK {'no believed-unique phrase': 1, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 5, 'no sayable word': 6, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 2, 'no sayable word': 5, 'the read-back': 1}
   LAW              0.882 · 0.955 (n 67) · 0.842 · 1.000 · 0.727 · 0.375 (n 32) · 1.000 (n 76) · 1.000 (n 13) · DECLINE 0.658 · M2b 0.729
                    reasons SPEAK {'no believed-unique phrase': 1, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 5, 'no sayable word': 6, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 2, 'no sayable word': 5, 'the read-back': 1}
   HEALTH-MOUTH     0.882 · 0.955 (n 67) · 0.842 · 1.000 · 0.727 · 0.375 (n 32) · 1.000 (n 76) · 1.000 (n 13) · DECLINE 0.658 · M2b 0.729
                    reasons SPEAK {'no believed-unique phrase': 1, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 5, 'no sayable word': 6, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 2, 'no sayable word': 5, 'the read-back': 1}
   HEALTH-ORACLE    0.882 · 0.955 (n 67) · 0.842 · 1.000 · 0.727 · 0.375 (n 32) · 1.000 (n 76) · 1.000 (n 13) · DECLINE 0.658 · M2b 0.729
                    reasons SPEAK {'no believed-unique phrase': 1, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 5, 'no sayable word': 6, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 2, 'no sayable word': 5, 'the read-back': 1}
   HEALTH-TRUTHFED  0.868 · 0.955 (n 66) · 0.829 · 1.000 · 0.568 · 0.240 (n 25) · 1.000 (n 69) · 1.000 (n 7) · DECLINE 0.658 · M2b 0.729
                    reasons SPEAK {'no believed-unique phrase': 2, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 13, 'no sayable word': 6} · DECLINE {'no believed-unique phrase': 3, 'no sayable word': 5, 'the read-back': 1} · the row refused {'small:not held lately': 48}
   NULL             0.882 · 0.955 (n 67) · 0.842 · 1.000 · 0.727 · 0.375 (n 32) · 1.000 (n 76) · 1.000 (n 13) · DECLINE 0.658 · M2b 0.729
                    reasons SPEAK {'no believed-unique phrase': 1, 'no sayable word': 8} · SPEAK2 {'no believed-unique phrase': 5, 'no sayable word': 6, 'the read-back': 1} · DECLINE {'no believed-unique phrase': 2, 'no sayable word': 5, 'the read-back': 1}
the decision (over the CONTROL's spoken phrases on SPEAK + SPEAK2, covered): ERROR-RECALL (declined + replaced true / errors) · TRUE-RETENTION (true / true):
   CONTROL          ER 0.000 (0 + 0 / 23) · TR 1.000 (76 / 76)
   HEALTH-MOUTH     ER 0.000 (0 + 0 / 23) · TR 1.000 (76 / 76)
   HEALTH-ORACLE    ER 0.000 (0 + 0 / 23) · TR 1.000 (76 / 76)
   HEALTH-TRUTHFED  ER 0.043 (1 + 0 / 23) · TR 0.908 (69 / 76)
   NULL             ER 0.000 (0 + 0 / 23) · TR 1.000 (76 / 76)
   calibration of the truth-free row (the law's): ECE 0.036 · type-2 AUROC 0.553 · n 489 (errors 26; no row 0) · curve [0.8: n 153 conf 0.82 acc 0.93] [0.9: n 336 conf 0.95 acc 0.96]
   calibration of the truth-fed row (its ceiling): ECE 0.032 · type-2 AUROC 0.680 · n 489 (errors 26; no row 0) · curve [0.7: n 88 conf 0.75 acc 0.90] [0.8: n 23 conf 0.85 acc 0.91] [0.9: n 378 conf 0.96 acc 0.96]
   calibration of the deranged rows (the floor): ECE 0.049 · type-2 AUROC 0.516 · n 489 (errors 26; no row 0) · curve [0.8: n 163 conf 0.83 acc 0.96] [0.9: n 326 conf 0.94 acc 0.94]
   the CONTROL re-graded vs S1b-1R's report.json: TRUTH [0.9552238805970149, 0.9552238805970149] · SPOKEN [0.881578947368421, 0.881578947368421] · TRUTH-NEED [0.375, 0.375] → EQUAL

== AMENDMENT 1's READINGS (offline, the tape's truth; readings, never bars) ==
20261101: the metacognition-of-perception reading (the referent never seen): claims set aside 1480 / 1924 = 0.769 (scenes 647 / 977 = 0.662; phrases «none» 673 / 1039 = 0.648; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1529 / 15479 = 0.099 (scenes 594 / 8042 = 0.074; phrases «none» 656 / 8711 = 0.075; predicted 0.05–0.08)
20261102: the metacognition-of-perception reading (the referent never seen): claims set aside 1469 / 1896 = 0.775 (scenes 670 / 995 = 0.673; phrases «none» 701 / 1056 = 0.664; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1661 / 15418 = 0.108 (scenes 658 / 8002 = 0.082; phrases «none» 742 / 8694 = 0.085; predicted 0.05–0.08)
20261103: the metacognition-of-perception reading (the referent never seen): claims set aside 1401 / 1893 = 0.740 (scenes 619 / 986 = 0.628; phrases «none» 640 / 1028 = 0.623; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 1280 / 15475 = 0.083 (scenes 501 / 8064 = 0.062; phrases «none» 572 / 8722 = 0.066; predicted 0.05–0.08)
pooled: the metacognition-of-perception reading (the referent never seen): claims set aside 4350 / 5713 = 0.761 (scenes 1936 / 2958 = 0.654; phrases «none» 2014 / 3123 = 0.645; predicted ≈ 0.8) · the false-unseen rate (the referent seen): 4470 / 46372 = 0.096 (scenes 1753 / 24108 = 0.073; phrases «none» 1970 / 26127 = 0.075; predicted 0.05–0.08)

== T-MEM-2 BARS (fresh seeds; the ceiling beside every bar; the ruled forms of B2's null clause and B3's power) ==
20261101 B1 TRUTH(HEALTH-MOUTH) 0.823 (n 62) ≥ 0.752 (0.90 × HEALTH-ORACLE 0.836) AND SPOKEN 0.816 ≥ 0.653 (0.80 × CONTROL 0.816) → PASS · the CONTROL's TRUTH 0.823 — «met by the control»: NOT evidence for the gate (B2 carries the claim)
         B3 ECE(the truth-free row) 0.032 ≤ 0.10 (n 453 predictions; errors 33) → PASS · the NULL 0.022 (the floor) · the truth-fed row 0.012 (the row's ceiling)
         the decision per seed: CONTROL ER 0.000 (n 35) TR 1.000 (n 62) · HEALTH-MOUTH ER 0.000 (n 35) TR 1.000 (n 62) · HEALTH-ORACLE ER 0.057 (n 35) TR 0.968 (n 62) · HEALTH-TRUTHFED ER 0.000 (n 35) TR 1.000 (n 62) · NULL ER 0.000 (n 35) TR 1.000 (n 62)
         B4 per seed (a reading; the bar is pooled): AUROC 0.502 (errors 33)
20261102 B1 TRUTH(HEALTH-MOUTH) 0.968 (n 63) ≥ 0.839 (0.90 × HEALTH-ORACLE 0.932) AND SPOKEN 0.875 ≥ 0.700 (0.80 × CONTROL 0.875) → PASS · the CONTROL's TRUTH 0.968 — «met by the control»: NOT evidence for the gate (B2 carries the claim)
         B3 ECE(the truth-free row) 0.041 ≤ 0.10 (n 495 predictions; errors 34) → PASS · the NULL 0.023 (the floor) · the truth-fed row 0.046 (the row's ceiling)
         the decision per seed: CONTROL ER 0.000 (n 20) TR 1.000 (n 84) · HEALTH-MOUTH ER 0.000 (n 20) TR 1.000 (n 84) · HEALTH-ORACLE ER 0.200 (n 20) TR 0.869 (n 84) · HEALTH-TRUTHFED ER 0.000 (n 20) TR 0.929 (n 84) · NULL ER 0.000 (n 20) TR 1.000 (n 84)
         B4 per seed (a reading; the bar is pooled): AUROC 0.430 (errors 34)
20261103 B1 TRUTH(HEALTH-MOUTH) 0.955 (n 67) ≥ 0.860 (0.90 × HEALTH-ORACLE 0.955) AND SPOKEN 0.882 ≥ 0.705 (0.80 × CONTROL 0.882) → PASS · the CONTROL's TRUTH 0.955 — «met by the control»: NOT evidence for the gate (B2 carries the claim)
         B3 ECE(the truth-free row) 0.036 ≤ 0.10 (n 489 predictions; errors 26) → PASS · the NULL 0.049 (the floor) · the truth-fed row 0.032 (the row's ceiling)
         the decision per seed: CONTROL ER 0.000 (n 23) TR 1.000 (n 76) · HEALTH-MOUTH ER 0.000 (n 23) TR 1.000 (n 76) · HEALTH-ORACLE ER 0.000 (n 23) TR 1.000 (n 76) · HEALTH-TRUTHFED ER 0.043 (n 23) TR 0.908 (n 76) · NULL ER 0.000 (n 23) TR 1.000 (n 76)
         B4 per seed (a reading; the bar is pooled): AUROC 0.553 (errors 26)
POOLED B2 ERROR-RECALL(HEALTH-MOUTH) 0.000 ≥ 0.054 (0.70 × HEALTH-ORACLE 0.077) AND TRUE-RETENTION 1.000 ≥ 0.90 AND the NULL 0.000 below by ≥ its half-width 0.000 (gap 0.000) · n errors 78 → CEILING-BOUND — the control's errors are the gaze's, not the words' (CEILING-BOUND: the oracle's own recall < 0.30) · clauses {'recall': False, 'retention': True, 'null': False}
       pooled decision: CONTROL ER 0.000 (0/78) TR 1.000 (222/222) · HEALTH-MOUTH ER 0.000 (0/78) TR 1.000 (222/222) · HEALTH-ORACLE ER 0.077 (6/78) TR 0.941 (209/222) · HEALTH-TRUTHFED ER 0.013 (1/78) TR 0.941 (209/222) · NULL ER 0.000 (0/78) TR 1.000 (222/222)
POOLED B4 type-2 AUROC(the truth-free row) 0.495 ≥ 0.70 (errors 93; chance 0.50) → FAIL
refutations (§6): (a) the row buys silence 20261101:no 20261102:no 20261103:no · (b) the NULL ≈ HEALTH-MOUTH (the null clause not met) YES — the gate refuses, it does not know · (c) CEILING-BOUND YES · (d) the rows disagree by > 0.10 on ≥ 3 words 20261101:no (0) 20261102:no (1) 20261103:no (2)
the declared sign (§6: truth-free cal_20 ≥ truth-fed on every word): 20261101: reversed ['big', 'blue', 'circle', 'small', 'square', 'triangle', 'yellow'] 20261102: reversed ['circle', 'cross', 'green', 'square', 'star'] 20261103: reversed ['blue', 'circle', 'cross', 'square'] — FAULT (> 0.10) ['circle', 'square']
per seed: B1 PASS/PASS/PASS · B3 PASS/PASS/PASS · pooled: B2 CEILING-BOUND · B4 FAIL
A PASS is B1–B4, or B2 CEILING-BOUND with B1, B3, B4 met → T-MEM-2 does not pass
```

### 11.5 · Price
- **The gate:** 78 CPU-s. Its step 5 prices the unit at ≈ 78 CPU-s ≈ 1.3 CPU-min, against ≤ 5 declared.
- **The unit:** 18:53:27 – 18:53:57, three lives at once. systemd reports 1 min 22.654 s of CPU (≈ 83 CPU-s ≈ 1.4 CPU-min) over 29.9 s of wall time, within ≤ 5 CPU-min.

### 11.6 · The suites on the final code (00dc818)
- **The whole brain suite under the venv:** `Ran 613 tests in 272.143s` / `OK (skipped=3)`, with 0 ERROR/FAIL blocks. Log: `logs/suite-venv-00dc818.log`.
- **The scene package under /usr/bin/python3:** `Ran 211 tests in 52.432s` / `OK`. Log: `logs/suite-scene-sys-00dc818.log`.

### 11.7 · Files
- **The unit:** `/data/dev/brain-runs/scene-tmem2/`:
  - `report.txt` and `report.json`;
  - `<ws>/life/{record.json, answers_10000.json}` and `<ws>/marks.json` for each seed;
  - `logs/full-run.log` and `logs/unit-journal.txt`.
- **The gate:** `gate/` (gate.txt, gate.json, journal.txt, lives/).
- **The crashed first launch:** `unit-1847-report-crash/`.
- **The earlier gates:** `gate-1751-stop/`, `gate-1823-amend1-stop/` and `gate-1845-amend2-proceed/`.
- **The pins:** `code-00dc818` (the gate's and the unit's), `code-0c811b9`, `code-8767cf6`, `code-15b047e` and `code-96a00bd`.
- **Untouched:** nothing was written under `/data/dev/brain-runs/scene-s1b1r/`. No unit other than `scene-tmem2-gate` and `scene-tmem2` was launched.
