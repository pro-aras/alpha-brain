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
