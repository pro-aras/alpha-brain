# S1a «THE SCENE-TALK WORLD» — the builder's hand-back

*edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:39 +0400 — written at THE FIRST GATE's STOP. The law: `docs/brain/r3/PREREG-R3-TONIGHT.md` §S1a in genome-wt-brain3, sha256 `18250d201b6aecbdc95058267f6cab163ca1450e82f4f1d8f9724a1849215968` (checked before the gate: equal). Branch `scene-talk` of `/data/dev/genome-wt-scene`, from b1-tape2 f393e5a.*

> **UPDATE (2026-09-28 13:19 +0400): AMENDMENT 2 is implemented. THE FIRST GATE re-ran and PROCEEDED, and the full run ran as one unit. §13 is the current state; §0–§12 are the record of the first gate's STOP.**

## 0 · The verdict: THE FIRST GATE says STOP. No full stream was run.

- **The instrument verdict fires for COLOUR.** P-ORACLE's per-type naming, leave-one-scene-out on the 113 one-thing scenes among the first 300 of seed 20261101, reads colour **0.832 = 94/113**, against 0.90 × the probe's 0.933 = **0.8397**. One item decides it: 95/113 = 0.8407 would not fire.
- **The brief's own stop (ORACLE-TRUTH < 0.95) fires only under the builder's declared POINTING rule.** ORACLE-TRUTH reads **0.790** under it, but **0.986** under the reader's own posterior (§2b, RAISED). So the STOP rests on the instrument verdict alone. That verdict is the same under every pointing rule: for a fixed thing, d²_k = xᵀΛx − 2δ_k(x), so the forced argmin within a type does not depend on the rule.
- Under the builder's declared reader, the firing is **a property of the reader, not of the features** (§3):
  - the same 113 scenes read colour 0.929 by the probe's own nearest-class-mean;
  - a type-aware Σ (a diagnostic, read by no verdict) reads 0.894;
  - a shuffled-utterance control reads chance.
  
  The ruling is the seat's. Nothing was re-read to make the gate pass, and `gate.json` refuses the full run until a new gate reads PROCEED.
- **A gaze fact that decides M6 at seed 1 whatever the ruling:** at the one meeting (scene 2,700) the gaze put all 4 fixations on the green square and **none on the moon** (§4).

## 1 · What was built (commits on `scene-talk`)

| commit | what |
|---|---|
| 0876bf3 | step 0, the eye fixture as the first test (3/3 byte-equal under /usr/bin/python3 from this tree); step 1, `brain/scene/world.py` + its tests |
| 2cb0d38 | step 2: `eye.py` (one `glances` call a scene; union-find hypotheses; the forced window pinned byte-for-byte to the eye) and `cache.py` (brain.glance_cache + sidecars, written once) |
| 2716457 | steps 4–5: `learners.py` (A-RW, P-ORACLE-RW, the LDA reader, the feeds), `slda.py` (StreamingLDA copied from genome-wt-b12 45c883e, text-pinned), the AST truth fence with planted offenders |
| d102d80 | `marks.py`, `run.py` (stage −1, the toy, THE FIRST GATE, arms, grader, report, price), `tools/scene/run_s1a.sh` (the unit), `pin_code.sh`; a cache is read only by the code that drew it |
| fa0dfd1 | THE FIRST GATE's STOP recorded; the diagnosis scripts (`tools/scene/diag/diag_verdict*.py`); this hand-back |
| 043efc6 | the oracles' pointing rule RAISED (`diag_pointing.py`) |
| d6f28e2 | the gate's M1 per scene size (`diag_gate_sizes.py`); the grader's «unheard → 0.0» defect; prices with their load |
| (the final commit) | §12's suite lines — this file only |

The runs read a pinned copy: `/data/dev/brain-runs/scene/code-d102d80` (`CODE_SHA` d102d80…). The eye fixture re-run from that copy reproduced B1.1 3/3, with the modules' own `__file__` inside the copy.

**New tests:** `tests/brain/scene/` (8 modules). Run against f393e5a's code they are red: `Ran 10 tests … FAILED (errors=8)`, 7 modules `ModuleNotFoundError: No module named 'brain.scene'` (log `/data/dev/brain-runs/scene/redcheck-f393e5a/red.log`). Two pass there by design:
- the eye fixture (it pins f393e5a's own eye);
- the fence's planted-offender test (it checks the checker).

## 2 · THE FIRST GATE, as the gate printed it (`/data/dev/brain-runs/scene/gate/gate.txt`)

```
== THE FIRST GATE (PREREG-R3-TONIGHT §S1a) ==
1. THE TOY: A-RW trained on 1000 one-thing scenes (seed 20261099), M1 on 196 two-thing items: lr 0.1: covered 0.959 (n 169) all 0.827 chance 0.558 → lr 0.1 PASS (bar ≥ 0.9; fallback grid not needed)
   P-ORACLE's ε on the toy seed only (mean per-type forced naming · toy M1): 0.0001: 0.899 · 0.645 · 0.001: 0.902 · 0.645 · 0.01: 0.921 · 0.621 · 0.03: 0.929 · 0.615 · 0.1: 0.941 · 0.633 · 0.3: 0.960 · 0.669 → ε 0.3
2. THE INSTRUMENT VERDICT: P-ORACLE (ε 0.3) per-type naming, leave-one-scene-out on the 113 one-thing scenes among the first 300 of seed 20261101:
   shape  1.000 (n 113) vs 0.90 × probe 0.797 = 0.7173 → does not fire · best-subset probe tower 112 0.903 (read by no verdict)
   colour 0.832 (n 113) vs 0.90 × probe 0.933 = 0.8397 → FIRES · best-subset probe colour 32 0.925 (read by no verdict)
   size   0.912 (n 113) vs 0.90 × probe 0.867 = 0.7803 → does not fire · best-subset probe tower 112 0.875 (read by no verdict)
3. FIVE ARMS × 300 scenes of seed 20261101, M1 on its 399 test items (covered 362; chance covered 0.758):
   A-RW           M1 covered 0.890 · all 0.807 · beats N-SHUF: yes
   N-SHUF         M1 covered 0.713 · all 0.647
   P-ORACLE-RW    M1 covered 0.914 · all 0.830 · beats N-SHUF: yes
   P-ORACLE       M1 covered 0.815 · all 0.739 · beats N-SHUF: yes
   ORACLE-TRUTH   M1 covered 0.790 · all 0.777 · beats N-SHUF: yes
   (the brief's step 6 asked for ORACLE-TRUTH < 0.95 → STOP; the signed PREREG's STOP is the instrument verdict. ORACLE-TRUTH reads 0.790 here.)
GATE: STOP — the instrument verdict fires for ['colour']
```

Readings from the gate:
- **P-ORACLE and ORACLE-TRUTH read BELOW A-RW** (0.815 and 0.790 against 0.890) under the declared pointing rule. §2b shows the cause is that rule, not the reader's features.
- **ORACLE-TRUTH reads a little below P-ORACLE under both rules:**
  - 0.790 vs 0.815 under rule (a), 0.986 vs 0.994 under rule (b);
  - one forced window at the centroid is compared against a hypothesis that averages 1–4 fixations;
  - stage −1 agrees: forced-window shape NCM 0.667, against 0.756 for the hypothesis.
- **The pooled M1 line hides the test: its 170 one-thing items are trivially right for every arm.** Per scene size (`tools/scene/diag/diag_gate_sizes.py`, the gate's own code and items; its pooled rows equal gate.json's, output `/data/dev/brain-runs/scene/gate/diag_gate_sizes.out`):
  ```
  A-RW           pooled covered 0.890 (gate.json 0.890, SAME) · size1: 1.000 vs chance 1.000 (n 170) · size2: 0.801 vs chance 0.585 (n 136) · size3: 0.768 vs chance 0.446 (n 56)
  N-SHUF         pooled covered 0.713 (gate.json 0.713, SAME) · size1: 1.000 vs chance 1.000 (n 170) · size2: 0.493 vs chance 0.585 (n 136) · size3: 0.375 vs chance 0.446 (n 56)
  P-ORACLE-RW    pooled covered 0.914 (gate.json 0.914, SAME) · size1: 1.000 vs chance 1.000 (n 170) · size2: 0.838 vs chance 0.585 (n 136) · size3: 0.839 vs chance 0.446 (n 56)
  P-ORACLE       pooled covered 0.815 (gate.json 0.815, SAME) · size1: 1.000 vs chance 1.000 (n 170) · size2: 0.669 vs chance 0.585 (n 136) · size3: 0.607 vs chance 0.446 (n 56)
  ORACLE-TRUTH   pooled covered 0.790 (gate.json 0.790, SAME) · size1: 1.000 vs chance 1.000 (n 170) · size2: 0.640 vs chance 0.500 (n 136) · size3: 0.518 vs chance 0.333 (n 56)
  ```
  - **N-SHUF sits systematically BELOW 1/n on the multi-thing items** (0.493 vs 0.585; 0.375 vs 0.446). The pooled «≤ chance + 0.05» bar is met through the trivially-right items.
  - **A-RW is well above chance where there is a choice** (0.801 and 0.768).
  - A gaze arm's chance at size 2 is 0.585, not 0.5: when only the target is covered, the scene shows one hypothesis and the pointing is trivially right.
- **ε landed at the grid's end** (0.3, R49's grid {1e-4 … 0.3}). ε 0.6 and 0.9 give the same colour reading (0.832), so ε does not move the verdict (§3).

## 2b · The oracles' POINTING rule (diagnostic, read by no verdict; `tools/scene/diag/diag_pointing.py`, output `/data/dev/brain-runs/scene/gate/diag_pointing.out`)

```
eps 0.3 toy M1 (a) argmin Σ d² [declared]: covered 0.669 (n 169) · all 0.577
eps 0.3 toy M1 (b) argmax Σ log posterior: covered 0.994 (n 169) · all 0.857
eps 0.3 toy M1 (c) argmax Σ δ (Λ-norm removed): covered 0.698 (n 169) · all 0.602
   the things' own Λ-norm xᵀΛx on the toy test: min 212.3 median 294.0 max 530.3
gate 300 · P-ORACLE     rule (a): M1 covered 0.815 (n 362) · all 0.739
gate 300 · P-ORACLE     rule (b): M1 covered 0.994 (n 362) · all 0.902
gate 300 · ORACLE-TRUTH rule (a): M1 covered 0.790 (n 362) · all 0.777
gate 300 · ORACLE-TRUTH rule (b): M1 covered 0.986 (n 362) · all 0.987
```

- **The declared rule (a) is not a ceiling for M1.** It compares Σ_w d_w(x)² across DIFFERENT things. Removing each thing's Λ-norm (c) barely helps.
- **The reader's own posterior over words (b) works.** Σ_w log p(w | x), where p is the LDA's softmax over its classes, is A-RW's pointing rule (Σ log p_w(t)) with the reader's p. It reads 0.994 on the toy and 0.994 / 0.986 at the gate.
- Rule (a) reproduces the gate's own 0.815 / 0.790 exactly, so the diagnostic is on the gate's items and tie generators.
- **The rule was not changed after the gate.** P-ORACLE's «none» threshold is calibrated on the same score, so it moves with the rule (RAISED, §6 item 1b).

## 3 · The diagnosis of the colour verdict (diagnostics, read by no verdict)

The scripts are `tools/scene/diag/diag_verdict.py`, `diag_verdict2.py` and `diag_verdict_null.py`. Their outputs, as printed, are in `/data/dev/brain-runs/scene/gate/diag_*.out`.

```
n one-thing 113
NCM LOO on these hypotheses (the probe's rule): {'shape': 0.735, 'colour': 0.929, 'size': 0.814}
type-blind LDA LOO eps 0.0001 {'shape': 0.973, 'colour': 0.522, 'size': 0.823}
type-blind LDA LOO eps 0.01 {'shape': 1.0, 'colour': 0.673, 'size': 0.885}
type-blind LDA LOO eps 0.1 {'shape': 1.0, 'colour': 0.761, 'size': 0.912}
type-blind LDA LOO eps 0.3 {'shape': 1.0, 'colour': 0.832, 'size': 0.912}
type-blind LDA LOO eps 0.6 {'shape': 0.982, 'colour': 0.832, 'size': 0.938}
type-blind LDA LOO eps 0.9 {'shape': 0.894, 'colour': 0.832, 'size': 0.929}
type-blind LDA LOO eps 1.0 {'shape': 0.779, 'colour': 0.858, 'size': 0.867}
per-type-Σ LDA LOO eps 0.3, shape {'shape': 1.0, 'colour': None, 'size': None}
per-type-Σ LDA LOO eps 0.3, colour {'shape': None, 'colour': 0.894, 'size': None}
per-type-Σ LDA LOO eps 0.3, size {'shape': None, 'colour': None, 'size': 0.938}
observations per word class: {'cross': 41, 'small': 60, 'yellow': 27, 'circle': 43, 'star': 58, 'blue': 25, 'ring': 35, 'triangle': 49, 'white': 41, 'square': 37, 'green': 29, 'red': 20, 'big': 70}
eps 0.3 fit on 300 gate scenes → test one-thing scenes: {'shape': (1.0, 170), 'colour': (0.871, 170), 'size': (0.894, 170)}
   in-sample on the gate's one-thing scenes: {'shape': (1.0, 113), 'colour': (0.903, 113), 'size': (0.947, 113)}
   test colour confusions (true → named): {('green', 'white'): 2, ('red', 'white'): 2, ('green', 'yellow'): 4, ('blue', 'white'): 9, ('red', 'yellow'): 1, ('yellow', 'green'): 1, ('white', 'blue'): 1, ('yellow', 'white'): 2}
shuffled-utterance LOO, permutation 0: {'shape': '33/113 = 0.292', 'colour': '18/113 = 0.159', 'size': '45/113 = 0.398'} chance: shape 0.167 colour 0.200 size 0.500
shuffled-utterance LOO, permutation 1: {'shape': '27/113 = 0.239', 'colour': '20/113 = 0.177', 'size': '67/113 = 0.593'} chance: shape 0.167 colour 0.200 size 0.500
shuffled-utterance LOO, permutation 2: {'shape': '10/113 = 0.088', 'colour': '29/113 = 0.257', 'size': '52/113 = 0.460'} chance: shape 0.167 colour 0.200 size 0.500
```

What this says [Likely; each line above is Certain as printed]:
- **The LOO is clean.** With the utterances shuffled, the same protocol reads chance (mean shape 0.206, colour 0.198, size 0.484), so shape's 1.000 is a fact about the reader, not a leak.
- **The features carry colour:** NCM reads 0.929 on these same 113 scenes, and stage −1's colour block alone reads 0.959.
- **The firing comes from ONE shared metric over every word.**
  - Shape words are said in every scene, so their within-class scatter, which includes all the colour variation, dominates the pooled Σ. Λ then discounts the colour directions: colour falls as shrinkage falls (0.522 at ε 1e-4).
  - A Σ pooled within the colour classes only reads 0.894.
- **The out-of-sample reading does not fire.** Fit on the 300 gate scenes and read on seed 1's 170 test one-thing scenes, colour is 0.871. The verdict's protocol (LOO on the gate's scenes) is the builder's declared reading of «on the first gate's scenes» (RAISED, §6).
- **The errors are mostly blue → white** (9 of 22 on the test scenes).

## 4 · The one meeting at seed 1 is invisible to the gaze

```
20261101 [('square', 'green', 'big'), ('moon', 'blue', 'small')] moon index 1 fix_thing [0, 0, 0, 0] moon covered: False
20261102 [('ring', 'yellow', 'big'), ('moon', 'red', 'small')] moon index 1 fix_thing [0, 1, 0, 0] moon covered: True
20261103 [('ring', 'white', 'small'), ('moon', 'blue', 'small')] moon index 1 fix_thing [0, 1, 0, 0] moon covered: True
```

At seed 1 the scene has one hypothesis, the green square. The consequence per arm:
- **A-RW:** its episodic write can only bind «dax» to the square.
- **P-ORACLE-RW and P-ORACLE:** no referent hypothesis exists, so they never hear «dax». Their M6 at seed 1 is unanswerable, which makes the M6 bar CEILING-BOUND there by the PREREG's own rule.
- **ORACLE-TRUTH:** it sees the moon.

So M6 at seed 1 is a gaze fact, never a test of the one-meeting write. The image is `/data/dev/brain-runs/scene/look/train-20261101-02699.png`, with the fixations drawn.

**A defect in the grader as built, to fix with any PROCEED.** At seed 1, P-ORACLE's M6 would print as **0.0** with n = the covered items:
- `answer_point` returns `point: None` (with `unheard: ["dax"]`) for a word never heard;
- `grade_pointing` scores that as not correct;
- `bars_for` then reads 0.0 < 0.70 → CEILING-BOUND.

That is the right verdict for the wrong reason: a zero reported by the instrument, not a measured reading (#162's class). The grader must read `unheard` as NOT GRADABLE by name, never as a score (#243 (4)).

## 5 · Stage −1, as printed (`/data/dev/brain-runs/scene/stage/stage_minus1.txt`)

```
== STAGE −1 (organ facts, printed only) · 300 scenes of seed 20261100 ==
1-thing scenes (123): gaze per-thing recall 1.000 (n 123) · all things covered 1.000 · merge (hypotheses on 2 things) 0.000 of 123 · hypotheses on no thing 0.000 · split (a thing → ≥ 2 hypotheses) 0.000 of 123
2-thing scenes (122): gaze per-thing recall 0.836 (n 244) · all things covered 0.672 · merge (hypotheses on 2 things) 0.000 of 204 · hypotheses on no thing 0.000 · split (a thing → ≥ 2 hypotheses) 0.000 of 204
3-thing scenes (55): gaze per-thing recall 0.721 (n 165) · all things covered 0.309 · merge (hypotheses on 2 things) 0.000 of 119 · hypotheses on no thing 0.000 · split (a thing → ≥ 2 hypotheses) 0.000 of 119
input separability, LOO nearest-class-mean, 123 one-thing scenes (the probe read all 144: shape 0.797 · colour 0.933 · size 0.867; tower 112 shape 0.903 · colour 32 colour 0.925 · tower 112 size 0.875):
   hypothesis shape: all 0.756 tower 0.911 colour 0.252 · colour: all 0.951 tower 0.341 colour 0.959 · size: all 0.846 tower 0.862 colour 0.480
   truth      shape: all 0.756 tower 0.911 colour 0.252 · colour: all 0.951 tower 0.341 colour 0.959 · size: all 0.846 tower 0.862 colour 0.480
   forced     shape: all 0.667 tower 0.894 colour 0.252 · colour: all 0.959 tower 0.415 colour 0.967 · size: all 0.862 tower 0.870 colour 0.577
```

With merge, split and no-thing all at 0.000, the gaze's hypotheses ARE its covered things (the hypothesis and truth roads read identically). The gaze's whole cost is coverage. In both scenes looked at, the brighter things took the fixations:
- seed 1 index 4: the white circle took 3 and the white triangle 1, while the green triangle (the referent) got 0;
- index 2699: the green square took 4 and the blue moon 0.

That is an anecdote, not measured by colour. The images are in `/data/dev/brain-runs/scene/look/`.

## 6 · Declared readings of what the PREREG leaves open (RAISED = can move a bar or the gate)

1. **RAISED — P-ORACLE's reader.** The reader is ONE type-blind StreamingLDA over every word as a class, on the hypothesis's 144 unit-mean (unstandardised, no position). Its decision rules use the per-word Mahalanobis distances under the shared Λ:
   - point: argmin Σ_w d²;
   - «none»: the best score is worse than the conformal 0.90 threshold of its training referents' said-phrase scores;
   - «what is this?»: emits w when d_w ≤ its conformal 0.90 band over w's referents (a word with n < 9 takes the median band);
   - per-type naming: the forced argmin over the grader's word set for that type.

   This reading is what makes the verdict fire (§3). R49's `answer()` bands are not used.
1b. **RAISED — the oracles' POINTING rule** (P-ORACLE and ORACLE-TRUTH): argmin over things of Σ_w d_w². As built, it reads BELOW A-RW on M1 (toy 0.669 against 0.959; gate 0.815 against 0.890). The reader's posterior Σ log p(w | x) reads 0.994 (§2b). «Every mark prints P-ORACLE's reading on the SAME items as its ceiling» needs a rule that is a ceiling. This is the seat's ruling, with item 1.
2. **RAISED — the verdict's protocol.** «On the first gate's scenes» is read as leave-one-scene-out on the one-thing scenes among the gate's 300: P-ORACLE is fitted on the other 299 with the referent marked. This is like-for-like with the probe's LOO NCM.
3. **RAISED — ε.** R49's grid, chosen on the toy seed by the max mean per-type forced naming over the toy's 200 two-thing scenes' covered things; ties go to the larger ε. It chose 0.3, the grid's end. ORACLE-TRUTH shares it.
4. **RAISED — no canvas-wide noise.** σ 0.05 is render()'s own picture noise (the PREREG's words under Things). The ground is black plus render_canvas's three clutter strokes, maxed in.
5. **RAISED — M2b's 56 and M6's 42 are EXTRA to the 400** regular test scenes, each from the test seed's named substreams.
6. **RAISED — «per word type» for M1.** A type counts when its word is NECESSARY: removing it leaves the phrase true of ≥ 2 things. For M2a: removing it makes the phrase true of some thing. Items with no necessary type go to «none». Per template is printed beside. This decides «left out of the aggregate M1».
7. **RAISED — M6's bar reads COVERED items** (M1's precedent); ALL is printed beside.
8. **RAISED — N-SHUF's permutation and the tie-break generators.** The PREREG names no seed for either:
   - N-SHUF: a derangement from `substream(world seed, "n-shuf-permutation")`;
   - each pointing item: `substream(test seed, "tie:<item_id>")`, the same in every arm, drawn only on a tie.
9. **Separation.** The Chebyshev gap between the picture boxes is ≥ 24 px, placed by rejection. Proved: under the fixation→thing rule, cells on two different things are ≥ 3 grid cells apart (exhaustive test).
10. **Fixation→thing (grading only).** The probe's `thing_of`: the cell centre inside the box ± 4 px. A hypothesis's thing is the strict plurality of its fixations (a tie is no thing). A thing's hypothesis is the one with the most fixations on it (a tie goes to the nearest centroid).
11. **M1 and M2a items.**
    - M1: ONE per test scene, the parent's own rule conditioned on the phrase being true of exactly one thing. M1 is graded as forced pointing, with «none» printed as the false refusal.
    - M2a: ONE per scene, an allowed pair true of nothing, said «⟨colour⟩ ⟨shape⟩».
    - «dax» counts as a shape word for M2b.
12. **A-RW edges.**
    - The standardiser observes the scene first, then standardises, with the sample sd.
    - The episodic write reads the pre-scene state. Every new word of one utterance shares one thing. With no known word, the thing is drawn by the scene's generator and the band is +inf.
    - The episodic band holds while the word has one meeting. Its prototype sums start with the episodic thing at weight 1.
    - The band is the responsibility-weighted 0.90 quantile of Euclidean distances in the standardised space.
    - τ_point and τ_word are recomputed at each reading point over every training scene seen, under the current state, with n printed. A τ with n < 9 is conservative: emit only at p = 1.
13. **P-ORACLE-RW.** A said word's responsibility is one-hot on the referent's hypothesis; unsaid words stay proportional. With the referent unseen, the said words are not updated. The episodic write uses the marked referent. P-ORACLE with an unseen referent observes nothing.
14. **The gate's M1.** The arms trained on the gate's 300 scenes are read on seed 1's test M1 items (399; covered 362). N-SHUF uses the first 300 of the full-stream derangement.
15. **RAISED — brief vs the signed PREREG.** PREREG followed:
    - 5 arms, not 4;
    - the toy at 1,000 one-thing / 200 two-thing / ≥ 0.90, not 200 / ≥ 0.95;
    - STOP = the instrument verdict, where the brief says ORACLE-TRUTH < 0.95. The verdict fires under every pointing rule; the brief's condition fires only under the declared pointing rule (0.790), not under the posterior (0.986, §2b).

    STOP was read where the PREREG says STOP (the verdict) or «must» (the toy after its grid). «Each beat N-SHUF» is a RESULT; all four beat it.
16. **A reading on lr.** On a synthetic machinery toy (4 words on planted directions, ambiguous 2-thing scenes), lr 0.1 on the standardised 146-dim input LOCKS IN early random assignments: one update moves a logit by ≈ 0.1 · e · r · ‖z‖² ≈ 3.6. At 0.01 the same code learns. The PREREG's toy passed at 0.1 (0.959, no ambiguity). The risk is the ambiguous stream; A-RW read 0.890 at 300 scenes.

## 7 · Every declared constant (the PREREG's, as implemented)

**The world:**
- shapes circle, square, triangle, cross, ring, star;
- colours red (230, 50, 50), blue (60, 90, 240), green (50, 200, 70), yellow (235, 220, 50), white (245, 245, 245); purple (150, 60, 200) never drawn;
- sizes big 32 / small 22 px, by `genome.world.render` × RGB/255;
- never-taught arrow, wave, diamond, house, tree, cup, key;
- scene mix 1/2/3 things = 0.4/0.4/0.2; boxes ≥ 24 px apart; templates T1–T4;
- held-out pairs (seed 20260928): circle-blue, cross-yellow, square-red, square-white, star-red, triangle-yellow;
- dax = moon at scene 2,700 (index 2699), alone with one trained thing;
- world seeds 20261101/02/03 × 10,000 scenes; test seeds 20261201/02/03 × 400;
- toy seed 20261099 (1,000 / 200, giving 196 M1 items); stage seed 20261100 (300); gate = the first 300 of 20261101;
- reading points 250 / 500 / 1,000 / 2,000 / 5,000 / 10,000.

**The eye:**
- ALPHA4.genome's RETINA / GAZE / SENSE colour via `brain.world.organs`;
- `glances(…, mode="surprise", pic_id=<canvas png sha>, colour, predicted=None)` under /usr/bin/python3;
- union-find within 2 cells (Chebyshev); the coarse glance kept in the cache's row 4, unused.

**A-RW:**
- x = [144 ‖ y/16, x/16], standardised by running mean and sd (floor 1e-3, clip ±8);
- lr 0.1 (the toy passed, so no fallback); proportional responsibility; noisy-OR;
- prototype and band 0.90; < 3 meetings answer by the band; τ conformal 0.90.

**P-ORACLE / ORACLE-TRUTH:** StreamingLDA (source `genome-wt-b12/brain/arms/soft/readers.py`, sha256 db4915b2…), ε 0.3.

**Bars:** in `brain/scene/marks.py`, BARS; the verdict thresholds are computed as 0.90 × 0.797 / 0.933 / 0.867.

## 8 · Prices (measured; the launch-shape arm price was NOT taken — the gate refuses the run)

- **The eye / cache, solo, idle box** (load 1.2, 12:26): seed 1's 10,498 canvases took 91.9 CPU-s user and 1:32 wall, ≈ 8.8 ms a canvas. That covers render, `glances`, png sha, the forced windows and the 10-row self-check. max RSS was 246,512 kB (/usr/bin/time).
- **Stage −1's 300 canvases:** 3.2 s.
- **THE FIRST GATE:** 19.4 s wall at load 1.5 (12:28), covering the toy caches (1,200 canvases), the toy, 6 ε fits, 113 LOO fits, and 5 arms × 300 with their answers.
- **Load fact:** at 12:22, with Test B's 8 pricing processes running (load 9), the seat's own `seat_eye_probe.py` read **48.6 ms a call**, against 5.7 ms idle. The builder's smoke timings from 12:17–12:22 were read during that load and are not quoted as prices.
- **No arm price at 10,000 scenes was taken.** The gate refuses the run, and `run.py price` reads `gate.json`.
- **After a ruling:**
  - seeds 2–3's caches are one command each (≈ 92 CPU-s each at idle), or the unit's first wave builds them;
  - `run.py price` (solo, then 5 × 3 at once) is one command.

## 9 · What a PROCEED needs (none of it done by the builder)

1. A ruling on P-ORACLE's reader, recorded on the PREREG (a dated amendment, a new sha passed to the builder), covering:
   - the reader: type-blind as built, or a per-type Σ;
   - the verdict's protocol: LOO on the gate's scenes as built, or another;
   - the oracles' pointing rule: (a) as built, or the posterior (b);
   - the verdict thresholds, if the reader changes.
2. `python3 -m brain.scene.run first-gate` re-run (≈ 20 s) until `gate.json` reads PROCEED.
3. `tools/scene/pin_code.sh <sha>`, then `run.py price`, then the unit:
   ```
   systemd-run --user --unit=scene-s1a -p Restart=no -p Nice=19 --setenv=PYTHONUNBUFFERED=1 --setenv=OPENBLAS_NUM_THREADS=1 \
     --setenv=OMP_NUM_THREADS=1 --setenv=TMPDIR=/data/dev/brain-runs/tmp /bin/bash <pinned>/tools/scene/run_s1a.sh
   ```
   Its waves are:
   - missing caches;
   - the questions;
   - 15 arms at once, each wave waiting on its own pids;
   - the grader and `report.txt`.

   The caches refuse any code other than the code that drew them (`cache.check_code`).
4. Read M6 at seed 1 as the gaze fact of §4.

## 10 · The marks table

None: the gate stopped the run before any full stream. `report.txt` does not exist.

## 11 · Candidate lessons for the seat to fold (SOLUTIONS; the builder touches nothing outside its worktree)

- **A ceiling reader pooled across word TYPES is not a ceiling for the minority type.** One LDA with a Σ pooled over every word class lets the always-said type's within-class scatter set the metric. Here the shape words carry the colour variation, and colour naming drops from NCM 0.929 to 0.832. Read a multi-type reader per type against a per-type-Σ twin before a verdict rests on it (in #228's family, as the SOLUTIONS index reads it: a control blind to the wrong thing).
- **Comparing a Mahalanobis likelihood across DIFFERENT things is not the reader's pointing rule.** The reader's posterior over its classes is (toy M1 0.669 → 0.994). A «ceiling» that reads below the learner is the tell (#162's family, as the index reads it: a filter reporting on itself).
- **A one-meeting test needs its meeting SEEN.** At seed 1 the gaze put 0 of 4 fixations on the moon, so M6 there grades the gaze. Print a mechanism mark's REACH (was the thing ever perceived?) beside the mark (#234 (2), as the index reads it).

## 12 · The suite on the final code

Run on **d6f28e2**, the last commit that touches anything but this file (`git diff --stat d6f28e2..HEAD` names only this .md). Each line is read from its log, never from a pipe, and each log has 0 `ERROR:` / `FAIL:` blocks:
- **The whole brain suite under the venv**: `Ran 471 tests in 223.442s` / `OK (skipped=3)`.
  - Command: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/tmp nice -n 19 /data/dev/venvs/brain/bin/python -m unittest discover -s tests/brain -t .`; log `/data/dev/brain-runs/scene/logs/suite-venv-d6f28e2.log`.
  - The 69 scene tests are inside the 471: 474 cases are discovered, and test_fonts' class-level SkipTest under the venv counts its class as one skip.
- **The scene package under /usr/bin/python3**: `Ran 69 tests in 8.359s` / `OK`; log `/data/dev/brain-runs/scene/logs/suite-scene-sys-d6f28e2.log`.
- **The same two on 043efc6**: 471 in 229.755 s OK (skipped=3), and 69 in 8.448 s OK. On fa0dfd1: 471 in 223.506 s OK (skipped=3).
- **The new tests on f393e5a (the base)** are red: `Ran 10 tests … FAILED (errors=8)`; log `/data/dev/brain-runs/scene/redcheck-f393e5a/red.log`.

## 13 · AMENDMENT 2 and the full run — 2026-09-28 13:19 +0400

*edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:19 +0400.*

**The law:**
- the signed PREREG, unchanged (sha 18250d20…);
- `PREREG-R3-TONIGHT-AMEND-2.md` as CO-SIGNED by Fable 5.1 at 13:02 (genome-wt-brain3 74be9e0, sha `6e58191fbfd8c758e926c30f83446a5585c4d4a75d137b00e62e162de26c025c`).

The co-signature changed two clauses after the builder's first implementation (4835449) was written against the seat's text (d54e6c0, sha 414b3201…). The builder's sha guard refused that text before anything ran, and 91f2495 implements the co-signed one.

### 13.1 · What changed (every step test-first: red on its parent, green on the commit)

| commit | what | red on the parent |
|---|---|---|
| 4835449 | AMENDMENT 2 §1–§5: `TypedLDAReader` (one StreamingLDA per word type, the types passed in by `run.py`); M1's «graded» block (2- and 3-thing items); `marks.meeting_seen`; an unheard word NOT GRADABLE (n_unheard); the reading arm A-RW-LR01 (lr 0.01); the unit runs 6 × 3 = 18 | 3d3f5d2: 14 of 18 (13 errors, 1 failure) |
| 91f2495 | the CO-SIGNED clauses: «none» = the best Σ log p(w \| x) below the conformal 0.90 threshold of the training referents' said-phrase scores; «what is this?» = the conformal 0.90 DISTANCE band under the word's own type's Λ; the gate prints the pooled M1 beside the graded one; the grader prints «what is this?»'s true-word rate (the 0.90 promise, checked) | 4835449: 2 errors |
| 311caff | report verdicts: a mark with n < 30 at a seed READS UNDERPOWERED; M2a's CEILING-BOUND read per half (RAISED, §13.6); «all seeds» counts a seed only where the mark reads PASS | 91f2495: 1 failure, 1 error |

The runs read pinned copies: code-91f2495 for the gate, the prices and the unit; code-311caff for the re-graded report.
- The eye fixture re-ran 3/3 from each copy.
- Every cache refuses code other than the code that drew it (`cache.check_code`, 7/7 caches read). No world, eye or cache file changed after the caches were drawn.

### 13.2 · THE FIRST GATE, re-run (13:10, load 1.7, 8.8 s wall; `/data/dev/brain-runs/scene/gate/gate.txt`; the first gate's record is `gate-1-stop-d102d80.txt` beside it)

```
== THE FIRST GATE (PREREG-R3-TONIGHT §S1a, as AMENDMENT 2 reads it) ==
1. THE TOY: A-RW trained on 1000 one-thing scenes (seed 20261099), M1 on 196 two-thing items: lr 0.1: covered 0.959 (n 169) all 0.827 chance 0.558 → lr 0.1 PASS (bar ≥ 0.9; fallback grid not needed)
   P-ORACLE's ε on the toy seed only (mean per-type forced naming · toy M1): 0.0001: 0.960 · 1.000 · 0.001: 0.965 · 1.000 · 0.01: 0.967 · 1.000 · 0.03: 0.967 · 1.000 · 0.1: 0.970 · 1.000 · 0.3: 0.974 · 1.000 → ε 0.3
2. THE INSTRUMENT VERDICT: P-ORACLE (ε 0.3) per-type naming, leave-one-scene-out on the 113 one-thing scenes among the first 300 of seed 20261101:
   shape  1.000 (n 113) vs 0.90 × probe 0.797 = 0.7173 → does not fire · best-subset probe tower 112 0.903 (read by no verdict)
   colour 0.894 (n 113) vs 0.90 × probe 0.933 = 0.8397 → does not fire · best-subset probe colour 32 0.925 (read by no verdict)
   size   0.938 (n 113) vs 0.90 × probe 0.867 = 0.7803 → does not fire · best-subset probe tower 112 0.875 (read by no verdict)
3. 6 ARMS × 300 scenes of seed 20261101, M1 on its GRADED 2- and 3-thing test items (n 229, covered 192; chance covered 0.544) — per size and the one-thing sanity reading beside:
   A-RW           M1 covered 0.792 · all 0.664 · size2 0.801 (chance 0.585) · size3 0.768 (chance 0.446) · size1 sanity 1.000 · pooled (all sizes) 0.890 · beats N-SHUF: yes
   A-RW-LR01      M1 covered 0.891 · all 0.747 · size2 0.890 (chance 0.585) · size3 0.893 (chance 0.446) · size1 sanity 1.000 · pooled (all sizes) 0.942 · a reading arm, no bar
   N-SHUF         M1 covered 0.458 · all 0.384 · size2 0.493 (chance 0.585) · size3 0.375 (chance 0.446) · size1 sanity 1.000 · pooled (all sizes) 0.713
   P-ORACLE-RW    M1 covered 0.839 · all 0.703 · size2 0.838 (chance 0.585) · size3 0.839 (chance 0.446) · size1 sanity 1.000 · pooled (all sizes) 0.914 · beats N-SHUF: yes
   P-ORACLE       M1 covered 1.000 · all 0.838 · size2 1.000 (chance 0.585) · size3 1.000 (chance 0.446) · size1 sanity 1.000 · pooled (all sizes) 1.000 · beats N-SHUF: yes
   ORACLE-TRUTH   M1 covered 1.000 · all 1.000 · size2 1.000 (chance 0.500) · size3 1.000 (chance 0.333) · size1 sanity 1.000 · pooled (all sizes) 1.000 · beats N-SHUF: yes
   (the brief's step 6: ORACLE-TRUTH < 0.95 → STOP; the signed PREREG's and AMENDMENT 2's STOP is the instrument verdict. ORACLE-TRUTH reads 1.000 on the graded items, 1.000 on all.)
GATE: PROCEED
```

### 13.3 · Prices (load 1.1–2.1)

- **The eye / caches, solo, one at a time:** 20261101 took 91.9 CPU-s (1:32 wall), 20261102 92.6 CPU-s (1:33), and 20261103 92.0 CPU-s (1:32). That is 10,498 canvases a seed, overlap 0 at every seed, max RSS 246 MB.
- **The arms**, as `run.py price` printed it (`/data/dev/brain-runs/scene/price/price.txt`):
```
== PRICE (first 2000 scenes, reading points [250, 500, 1000, 2000]; × 5 to 10,000) ==
solo A-RW seed 20261101: cpu 1.3 s, wall 1.6 s → ≈ 0.1 CPU-min per arm-seed
launch shape 6 arms × 3 seeds at once: cpu 50.8 s total (per process A-RW/20261101 2.4, A-RW-LR01/20261101 2.3, N-SHUF/20261101 2.3, P-ORACLE-RW/20261101 2.4, P-ORACLE/20261101 4.0, ORACLE-TRUTH/20261101 3.8, A-RW/20261102 2.3, A-RW-LR01/20261102 2.0, N-SHUF/20261102 2.4, P-ORACLE-RW/20261102 2.5, P-ORACLE/20261102 3.9, ORACLE-TRUTH/20261102 3.6, A-RW/20261103 2.3, A-RW-LR01/20261103 2.4, N-SHUF/20261103 2.4, P-ORACLE-RW/20261103 2.2, P-ORACLE/20261103 3.9, ORACLE-TRUTH/20261103 3.7), wall 5.0 s → ≈ 0.07 CPU-h and ≈ 0.4 min wall for the arms at 10,000
```
- **The unit itself** (13:14:56 → 13:15:12 +0400, Result=success, exit 0, NRestarts 0): 18 arms at once, 8.1–9.7 CPU-s each (≈ 157 CPU-s in all), 16 s wall.
- **S1a in all** is ≈ 527 CPU-s ≈ 0.15 CPU-h: caches 276, toy caches and stage −1 14, both gates 28, the prices 52, the unit 157 (the diagnosis scripts ≈ 40 more). The caches dominate.

### 13.4 · The marks, exactly as the grader printed them (`/data/dev/brain-runs/scene/report.txt`, re-graded from code-311caff)

The unit's own report is `report-unit-91f2495.txt`.
- **The re-grade is report-only:** every seed's `marks.json` is byte-identical to the unit's (cmp), and the per-seed tables are identical.
- **It differs in exactly 11 lines, all verdict lines:**
  - M2a at seeds 2–3: CEILING-BOUND → FAIL (per half, §13.6);
  - M6 at seed 2: PASS → UNDERPOWERED (n 29 < 30);
  - the «per seed» line added;
  - M6 in the «all seeds» line: PASS → no.

```
== S1a marks · world seed 20261101 (test seed 20261201) · the one meeting seen: False ==
M1 (covered, the GRADED 2- and 3-thing items) by reading point — A-RW-LR01 is a reading arm (no bar):
   arm                250     500    1000    2000    5000   10000
   A-RW             0.818   0.781   0.786   0.859   0.885   0.891
   A-RW-LR01        0.932   0.922   0.979   0.974   0.984   0.990
   N-SHUF           0.568   0.536   0.510   0.594   0.500   0.552
   P-ORACLE-RW      0.849   0.734   0.839   0.870   0.901   0.969
   P-ORACLE         1.000   1.000   1.000   1.000   1.000   1.000
   ORACLE-TRUTH     1.000   1.000   1.000   1.000   1.000   1.000
At 10000 scenes — M1 (covered · all) per block; chance and n from A-RW's items; size1 is the sanity reading:
   graded       cov 0.838 chance 0.544 n 192/229 | A-RW 0.891·0.747 | A-RW-LR01 0.990·0.830 | N-SHUF 0.552·0.463 | P-ORACLE-RW 0.969·0.812 | P-ORACLE 1.000·0.838 | ORACLE-TRUTH 1.000·1.000
   size2        cov 0.889 chance 0.585 n 136/153 | A-RW 0.890·0.791 | A-RW-LR01 0.993·0.882 | N-SHUF 0.566·0.503 | P-ORACLE-RW 0.963·0.856 | P-ORACLE 1.000·0.889 | ORACLE-TRUTH 1.000·1.000
   size3        cov 0.737 chance 0.446 n 56/76 | A-RW 0.893·0.658 | A-RW-LR01 0.982·0.724 | N-SHUF 0.518·0.382 | P-ORACLE-RW 0.982·0.724 | P-ORACLE 1.000·0.737 | ORACLE-TRUTH 1.000·1.000
   size1        cov 1.000 chance 1.000 n 170/170 | A-RW 1.000·1.000 | A-RW-LR01 1.000·1.000 | N-SHUF 1.000·1.000 | P-ORACLE-RW 1.000·1.000 | P-ORACLE 1.000·1.000 | ORACLE-TRUTH 1.000·1.000
   type:colour  cov 0.917 chance 0.500 n 22/24 | A-RW 0.909·0.833 | A-RW-LR01 1.000·0.917 | N-SHUF 0.455·0.417 | P-ORACLE-RW 1.000·0.917 | P-ORACLE 1.000·0.917 | ORACLE-TRUTH 1.000·1.000
   type:shape   cov 0.760 chance 0.550 n 76/100 | A-RW 0.855·0.650 | A-RW-LR01 0.987·0.750 | N-SHUF 0.526·0.400 | P-ORACLE-RW 0.934·0.710 | P-ORACLE 1.000·0.760 | ORACLE-TRUTH 1.000·1.000
   type:size    cov 0.867 chance 0.474 n 13/15 | A-RW 0.846·0.733 | A-RW-LR01 0.923·0.800 | N-SHUF 0.462·0.400 | P-ORACLE-RW 0.923·0.800 | P-ORACLE 1.000·0.867 | ORACLE-TRUTH 1.000·1.000
   type:none    cov 0.894 chance 0.556 n 84/94 | A-RW 0.929·0.830 | A-RW-LR01 1.000·0.894 | N-SHUF 0.595·0.532 | P-ORACLE-RW 1.000·0.894 | P-ORACLE 1.000·0.894 | ORACLE-TRUTH 1.000·1.000
   tpl:T1       cov 0.755 chance 0.583 n 40/53 | A-RW 0.900·0.679 | A-RW-LR01 1.000·0.755 | N-SHUF 0.625·0.472 | P-ORACLE-RW 0.975·0.736 | P-ORACLE 1.000·0.755 | ORACLE-TRUTH 1.000·1.000
   tpl:T2       cov 0.852 chance 0.503 n 52/61 | A-RW 0.904·0.770 | A-RW-LR01 1.000·0.852 | N-SHUF 0.577·0.492 | P-ORACLE-RW 1.000·0.852 | P-ORACLE 1.000·0.852 | ORACLE-TRUTH 1.000·1.000
   tpl:T3       cov 0.849 chance 0.574 n 45/53 | A-RW 0.889·0.755 | A-RW-LR01 0.978·0.830 | N-SHUF 0.578·0.491 | P-ORACLE-RW 0.956·0.811 | P-ORACLE 1.000·0.849 | ORACLE-TRUTH 1.000·1.000
   tpl:T4       cov 0.887 chance 0.530 n 55/62 | A-RW 0.873·0.774 | A-RW-LR01 0.982·0.871 | N-SHUF 0.455·0.403 | P-ORACLE-RW 0.945·0.839 | P-ORACLE 1.000·0.887 | ORACLE-TRUTH 1.000·1.000
   A-RW           M2a refusal 0.603 (n 400) · false refusal (graded M1 covered) 0.099 · M2b 0.000 (n 48; «I don't know» 0.000; diamond 0.000) · M6 NOT GRADABLE (the meeting was never seen) · NAME shape 0.871 colour 0.659 size 0.865 · «what is this?» emits the true word (the 0.90 promise) shape 0.941 colour 0.894 size 0.888
   A-RW-LR01      M2a refusal 0.892 (n 400) · false refusal (graded M1 covered) 0.068 · M2b 0.208 (n 48; «I don't know» 0.021; diamond 0.000) · M6 NOT GRADABLE (the meeting was never seen) · NAME shape 0.947 colour 0.888 size 0.900 · «what is this?» emits the true word (the 0.90 promise) shape 0.953 colour 0.947 size 0.888
   N-SHUF         M2a refusal 0.098 (n 400) · false refusal (graded M1 covered) 0.068 · M2b 0.000 (n 48; «I don't know» 0.000; diamond 0.000) · M6 NOT GRADABLE (the meeting was never seen) · NAME shape 0.159 colour 0.176 size 0.453 · «what is this?» emits the true word (the 0.90 promise) shape 0.900 colour 0.735 size 0.871
   P-ORACLE-RW    M2a refusal 0.675 (n 400) · false refusal (graded M1 covered) 0.057 · M2b 0.146 (n 48; «I don't know» 0.021; diamond 0.000) · M6 NOT GRADABLE (the meeting was never seen) · NAME shape 0.965 colour 0.824 size 0.882 · «what is this?» emits the true word (the 0.90 promise) shape 0.912 colour 0.924 size 0.841
   P-ORACLE       M2a refusal 1.000 (n 400) · false refusal (graded M1 covered) 0.078 · M2b 0.958 (n 48; «I don't know» 0.688; diamond 0.500) · M6 NOT GRADABLE (the meeting was never seen) · NAME shape 1.000 colour 0.982 size 0.953 · «what is this?» emits the true word (the 0.90 promise) shape 0.935 colour 0.941 size 0.941
   ORACLE-TRUTH   M2a refusal 1.000 (n 400) · false refusal (graded M1 covered) 0.099 · M2b 0.938 (n 48; «I don't know» 0.729; diamond 0.625) · M6 NOT GRADABLE (the meeting was never seen) · NAME shape 0.994 colour 1.000 size 0.959 · «what is this?» emits the true word (the 0.90 promise) shape 0.924 colour 0.924 size 0.929
   M2b arrow  A-RW 0.000 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.000 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 7, 'square': 5}
   M2b wave   A-RW 0.000 A-RW-LR01 0.250 N-SHUF 0.000 P-ORACLE-RW 0.375 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 6, 'ring': 6}
   M2b house  A-RW 0.000 A-RW-LR01 0.250 N-SHUF 0.000 P-ORACLE-RW 0.125 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'circle': 6, 'cross': 2, 'dax': 1, 'ring': 5, 'square': 5, 'triangle': 6}
   M2b tree   A-RW 0.000 A-RW-LR01 0.750 N-SHUF 0.000 P-ORACLE-RW 0.250 P-ORACLE 0.750 ORACLE-TRUTH 0.625 · A-RW emitted {'circle': 3, 'cross': 5, 'dax': 1, 'ring': 4, 'square': 4, 'star': 1, 'triangle': 5}
   M2b cup    A-RW 0.000 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.125 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 1, 'ring': 8, 'square': 5}
   M2b key    A-RW 0.000 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.000 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 8, 'square': 2, 'star': 1}
   the gaze's cost ORACLE-TRUTH − P-ORACLE on M1 (covered): graded 0.000 · size2 0.000 · size3 0.000

== S1a marks · world seed 20261102 (test seed 20261202) · the one meeting seen: True ==
M1 (covered, the GRADED 2- and 3-thing items) by reading point — A-RW-LR01 is a reading arm (no bar):
   arm                250     500    1000    2000    5000   10000
   A-RW             0.791   0.811   0.826   0.856   0.891   0.905
   A-RW-LR01        0.871   0.940   0.965   0.980   0.995   0.980
   N-SHUF           0.552   0.597   0.552   0.532   0.512   0.587
   P-ORACLE-RW      0.771   0.841   0.856   0.905   0.935   0.965
   P-ORACLE         1.000   1.000   1.000   1.000   1.000   1.000
   ORACLE-TRUTH     1.000   1.000   1.000   1.000   1.000   1.000
At 10000 scenes — M1 (covered · all) per block; chance and n from A-RW's items; size1 is the sanity reading:
   graded       cov 0.820 chance 0.543 n 201/245 | A-RW 0.905·0.743 | A-RW-LR01 0.980·0.804 | N-SHUF 0.587·0.482 | P-ORACLE-RW 0.965·0.792 | P-ORACLE 1.000·0.820 | ORACLE-TRUTH 1.000·1.000
   size2        cov 0.879 chance 0.579 n 152/173 | A-RW 0.895·0.786 | A-RW-LR01 0.987·0.867 | N-SHUF 0.618·0.543 | P-ORACLE-RW 0.974·0.855 | P-ORACLE 1.000·0.879 | ORACLE-TRUTH 1.000·1.000
   size3        cov 0.681 chance 0.432 n 49/72 | A-RW 0.939·0.639 | A-RW-LR01 0.959·0.653 | N-SHUF 0.490·0.333 | P-ORACLE-RW 0.939·0.639 | P-ORACLE 1.000·0.681 | ORACLE-TRUTH 1.000·1.000
   size1        cov 1.000 chance 1.000 n 153/153 | A-RW 1.000·1.000 | A-RW-LR01 1.000·1.000 | N-SHUF 1.000·1.000 | P-ORACLE-RW 1.000·1.000 | P-ORACLE 1.000·1.000 | ORACLE-TRUTH 1.000·1.000
   type:colour  cov 0.700 chance 0.536 n 14/20 | A-RW 0.857·0.600 | A-RW-LR01 0.857·0.600 | N-SHUF 0.714·0.500 | P-ORACLE-RW 0.929·0.650 | P-ORACLE 1.000·0.700 | ORACLE-TRUTH 1.000·1.000
   type:shape   cov 0.848 chance 0.543 n 78/92 | A-RW 0.936·0.793 | A-RW-LR01 0.987·0.837 | N-SHUF 0.577·0.489 | P-ORACLE-RW 0.974·0.826 | P-ORACLE 1.000·0.848 | ORACLE-TRUTH 1.000·1.000
   type:size    cov 0.867 chance 0.500 n 13/15 | A-RW 0.923·0.800 | A-RW-LR01 0.923·0.800 | N-SHUF 0.615·0.533 | P-ORACLE-RW 0.923·0.800 | P-ORACLE 1.000·0.867 | ORACLE-TRUTH 1.000·1.000
   type:none    cov 0.818 chance 0.547 n 99/121 | A-RW 0.879·0.719 | A-RW-LR01 0.990·0.810 | N-SHUF 0.576·0.471 | P-ORACLE-RW 0.960·0.785 | P-ORACLE 1.000·0.818 | ORACLE-TRUTH 1.000·1.000
   tpl:T1       cov 0.846 chance 0.545 n 44/52 | A-RW 0.932·0.788 | A-RW-LR01 1.000·0.846 | N-SHUF 0.568·0.481 | P-ORACLE-RW 1.000·0.846 | P-ORACLE 1.000·0.846 | ORACLE-TRUTH 1.000·1.000
   tpl:T2       cov 0.732 chance 0.542 n 52/71 | A-RW 0.865·0.634 | A-RW-LR01 0.962·0.704 | N-SHUF 0.500·0.366 | P-ORACLE-RW 0.962·0.704 | P-ORACLE 1.000·0.732 | ORACLE-TRUTH 1.000·1.000
   tpl:T3       cov 0.873 chance 0.542 n 48/55 | A-RW 0.958·0.836 | A-RW-LR01 0.979·0.855 | N-SHUF 0.625·0.545 | P-ORACLE-RW 0.958·0.836 | P-ORACLE 1.000·0.873 | ORACLE-TRUTH 1.000·1.000
   tpl:T4       cov 0.851 chance 0.544 n 57/67 | A-RW 0.877·0.746 | A-RW-LR01 0.982·0.836 | N-SHUF 0.649·0.552 | P-ORACLE-RW 0.947·0.806 | P-ORACLE 1.000·0.851 | ORACLE-TRUTH 1.000·1.000
   A-RW           M2a refusal 0.497 (n 400) · false refusal (graded M1 covered) 0.075 · M2b 0.083 (n 48; «I don't know» 0.000; diamond 0.125) · M6 covered 0.724 all 0.500 (n 29/42, chance 0.460, unheard 0) · NAME shape 0.954 colour 0.542 size 0.752 · «what is this?» emits the true word (the 0.90 promise) shape 0.935 colour 0.856 size 0.863
   A-RW-LR01      M2a refusal 0.845 (n 400) · false refusal (graded M1 covered) 0.055 · M2b 0.146 (n 48; «I don't know» 0.000; diamond 0.125) · M6 covered 0.759 all 0.524 (n 29/42, chance 0.460, unheard 0) · NAME shape 0.993 colour 0.876 size 0.895 · «what is this?» emits the true word (the 0.90 promise) shape 0.935 colour 0.954 size 0.882
   N-SHUF         M2a refusal 0.100 (n 400) · false refusal (graded M1 covered) 0.030 · M2b 0.000 (n 48; «I don't know» 0.000; diamond 0.000) · M6 covered 0.310 all 0.214 (n 29/42, chance 0.460, unheard 0) · NAME shape 0.340 colour 0.301 size 0.673 · «what is this?» emits the true word (the 0.90 promise) shape 0.922 colour 0.778 size 0.830
   P-ORACLE-RW    M2a refusal 0.620 (n 400) · false refusal (graded M1 covered) 0.075 · M2b 0.375 (n 48; «I don't know» 0.000; diamond 0.250) · M6 covered 0.724 all 0.500 (n 29/42, chance 0.460, unheard 0) · NAME shape 0.974 colour 0.745 size 0.804 · «what is this?» emits the true word (the 0.90 promise) shape 0.895 colour 0.889 size 0.843
   P-ORACLE       M2a refusal 1.000 (n 400) · false refusal (graded M1 covered) 0.119 · M2b 0.938 (n 48; «I don't know» 0.688; diamond 0.500) · M6 covered 1.000 all 0.690 (n 29/42, chance 0.460, unheard 0) · NAME shape 1.000 colour 0.928 size 0.928 · «what is this?» emits the true word (the 0.90 promise) shape 0.961 colour 0.902 size 0.928
   ORACLE-TRUTH   M2a refusal 1.000 (n 400) · false refusal (graded M1 covered) 0.124 · M2b 0.917 (n 48; «I don't know» 0.750; diamond 0.750) · M6 covered 1.000 all 1.000 (n 29/42, chance 0.443, unheard 0) · NAME shape 1.000 colour 0.974 size 0.928 · «what is this?» emits the true word (the 0.90 promise) shape 0.895 colour 0.915 size 0.895
   M2b arrow  A-RW 0.125 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.500 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 5, 'ring': 7}
   M2b wave   A-RW 0.000 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.125 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'ring': 8}
   M2b house  A-RW 0.125 A-RW-LR01 0.500 N-SHUF 0.000 P-ORACLE-RW 0.250 P-ORACLE 1.000 ORACLE-TRUTH 0.875 · A-RW emitted {'circle': 2, 'ring': 7, 'star': 1}
   M2b tree   A-RW 0.125 A-RW-LR01 0.375 N-SHUF 0.000 P-ORACLE-RW 0.250 P-ORACLE 0.625 ORACLE-TRUTH 0.625 · A-RW emitted {'cross': 2, 'dax': 1, 'ring': 7, 'triangle': 3}
   M2b cup    A-RW 0.125 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.250 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 1, 'ring': 7, 'square': 1}
   M2b key    A-RW 0.000 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.875 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 3, 'ring': 8}
   M6 size2: A-RW 0.947 A-RW-LR01 0.947 N-SHUF 0.368 P-ORACLE-RW 0.947 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · chance 0.500
   M6 size3: A-RW 0.300 A-RW-LR01 0.400 N-SHUF 0.200 P-ORACLE-RW 0.300 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · chance 0.383
   the gaze's cost ORACLE-TRUTH − P-ORACLE on M1 (covered): graded 0.000 · size2 0.000 · size3 0.000

== S1a marks · world seed 20261103 (test seed 20261203) · the one meeting seen: True ==
M1 (covered, the GRADED 2- and 3-thing items) by reading point — A-RW-LR01 is a reading arm (no bar):
   arm                250     500    1000    2000    5000   10000
   A-RW             0.806   0.853   0.796   0.900   0.905   0.919
   A-RW-LR01        0.929   0.953   0.957   0.986   0.986   0.981
   N-SHUF           0.507   0.479   0.521   0.493   0.526   0.479
   P-ORACLE-RW      0.829   0.929   0.853   0.915   0.919   0.962
   P-ORACLE         1.000   1.000   1.000   1.000   1.000   1.000
   ORACLE-TRUTH     1.000   1.000   1.000   1.000   1.000   1.000
At 10000 scenes — M1 (covered · all) per block; chance and n from A-RW's items; size1 is the sanity reading:
   graded       cov 0.854 chance 0.540 n 211/247 | A-RW 0.919·0.785 | A-RW-LR01 0.981·0.838 | N-SHUF 0.479·0.409 | P-ORACLE-RW 0.962·0.822 | P-ORACLE 1.000·0.854 | ORACLE-TRUTH 1.000·1.000
   size2        cov 0.892 chance 0.581 n 148/166 | A-RW 0.932·0.831 | A-RW-LR01 0.980·0.873 | N-SHUF 0.561·0.500 | P-ORACLE-RW 0.959·0.855 | P-ORACLE 1.000·0.892 | ORACLE-TRUTH 1.000·1.000
   size3        cov 0.778 chance 0.444 n 63/81 | A-RW 0.889·0.691 | A-RW-LR01 0.984·0.765 | N-SHUF 0.286·0.222 | P-ORACLE-RW 0.968·0.753 | P-ORACLE 1.000·0.778 | ORACLE-TRUTH 1.000·1.000
   size1        cov 1.000 chance 1.000 n 149/149 | A-RW 1.000·1.000 | A-RW-LR01 1.000·1.000 | N-SHUF 1.000·1.000 | P-ORACLE-RW 1.000·1.000 | P-ORACLE 1.000·1.000 | ORACLE-TRUTH 1.000·1.000
   type:colour  cov 0.893 chance 0.527 n 25/28 | A-RW 0.920·0.821 | A-RW-LR01 0.920·0.821 | N-SHUF 0.560·0.500 | P-ORACLE-RW 0.920·0.821 | P-ORACLE 1.000·0.893 | ORACLE-TRUTH 1.000·1.000
   type:shape   cov 0.792 chance 0.531 n 76/96 | A-RW 0.934·0.740 | A-RW-LR01 1.000·0.792 | N-SHUF 0.487·0.385 | P-ORACLE-RW 0.974·0.771 | P-ORACLE 1.000·0.792 | ORACLE-TRUTH 1.000·1.000
   type:size    cov 1.000 chance 0.625 n 8/8 | A-RW 0.875·0.875 | A-RW-LR01 0.875·0.875 | N-SHUF 0.500·0.500 | P-ORACLE-RW 0.875·0.875 | P-ORACLE 1.000·1.000 | ORACLE-TRUTH 1.000·1.000
   type:none    cov 0.880 chance 0.542 n 103/117 | A-RW 0.913·0.803 | A-RW-LR01 0.990·0.872 | N-SHUF 0.456·0.402 | P-ORACLE-RW 0.971·0.855 | P-ORACLE 1.000·0.880 | ORACLE-TRUTH 1.000·1.000
   tpl:T1       cov 0.857 chance 0.514 n 36/42 | A-RW 0.944·0.810 | A-RW-LR01 1.000·0.857 | N-SHUF 0.500·0.429 | P-ORACLE-RW 1.000·0.857 | P-ORACLE 1.000·0.857 | ORACLE-TRUTH 1.000·1.000
   tpl:T2       cov 0.822 chance 0.532 n 74/90 | A-RW 0.919·0.756 | A-RW-LR01 0.973·0.800 | N-SHUF 0.541·0.444 | P-ORACLE-RW 0.946·0.778 | P-ORACLE 1.000·0.822 | ORACLE-TRUTH 1.000·1.000
   tpl:T3       cov 0.870 chance 0.550 n 47/54 | A-RW 0.894·0.778 | A-RW-LR01 0.957·0.833 | N-SHUF 0.404·0.352 | P-ORACLE-RW 0.936·0.815 | P-ORACLE 1.000·0.870 | ORACLE-TRUTH 1.000·1.000
   tpl:T4       cov 0.885 chance 0.562 n 54/61 | A-RW 0.926·0.820 | A-RW-LR01 1.000·0.885 | N-SHUF 0.444·0.393 | P-ORACLE-RW 0.981·0.869 | P-ORACLE 1.000·0.885 | ORACLE-TRUTH 1.000·1.000
   A-RW           M2a refusal 0.598 (n 400) · false refusal (graded M1 covered) 0.043 · M2b 0.104 (n 48; «I don't know» 0.000; diamond 0.000) · M6 covered 0.812 all 0.619 (n 32/42, chance 0.474, unheard 0) · NAME shape 0.940 colour 0.644 size 0.799 · «what is this?» emits the true word (the 0.90 promise) shape 0.946 colour 0.926 size 0.893
   A-RW-LR01      M2a refusal 0.880 (n 400) · false refusal (graded M1 covered) 0.057 · M2b 0.062 (n 48; «I don't know» 0.000; diamond 0.125) · M6 covered 0.719 all 0.548 (n 32/42, chance 0.474, unheard 0) · NAME shape 1.000 colour 0.899 size 0.926 · «what is this?» emits the true word (the 0.90 promise) shape 0.966 colour 0.946 size 0.899
   N-SHUF         M2a refusal 0.070 (n 400) · false refusal (graded M1 covered) 0.081 · M2b 0.000 (n 48; «I don't know» 0.000; diamond 0.000) · M6 covered 0.594 all 0.452 (n 32/42, chance 0.474, unheard 0) · NAME shape 0.154 colour 0.201 size 0.255 · «what is this?» emits the true word (the 0.90 promise) shape 0.852 colour 0.792 size 0.752
   P-ORACLE-RW    M2a refusal 0.662 (n 400) · false refusal (graded M1 covered) 0.057 · M2b 0.188 (n 48; «I don't know» 0.000; diamond 0.000) · M6 covered 0.750 all 0.571 (n 32/42, chance 0.474, unheard 0) · NAME shape 0.940 colour 0.785 size 0.906 · «what is this?» emits the true word (the 0.90 promise) shape 0.893 colour 0.906 size 0.886
   P-ORACLE       M2a refusal 0.998 (n 400) · false refusal (graded M1 covered) 0.109 · M2b 0.917 (n 48; «I don't know» 0.688; diamond 0.625) · M6 covered 1.000 all 0.762 (n 32/42, chance 0.474, unheard 0) · NAME shape 1.000 colour 0.940 size 0.933 · «what is this?» emits the true word (the 0.90 promise) shape 0.960 colour 0.960 size 0.960
   ORACLE-TRUTH   M2a refusal 1.000 (n 400) · false refusal (graded M1 covered) 0.104 · M2b 0.938 (n 48; «I don't know» 0.792; diamond 0.875) · M6 covered 1.000 all 1.000 (n 32/42, chance 0.448, unheard 0) · NAME shape 1.000 colour 0.993 size 0.953 · «what is this?» emits the true word (the 0.90 promise) shape 0.913 colour 0.913 size 0.913
   M2b arrow  A-RW 0.125 A-RW-LR01 0.125 N-SHUF 0.000 P-ORACLE-RW 0.125 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 6, 'ring': 3}
   M2b wave   A-RW 0.000 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.125 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 3, 'ring': 8}
   M2b house  A-RW 0.375 A-RW-LR01 0.250 N-SHUF 0.000 P-ORACLE-RW 0.500 P-ORACLE 0.875 ORACLE-TRUTH 1.000 · A-RW emitted {'circle': 3, 'cross': 2, 'dax': 1, 'ring': 2, 'square': 1, 'star': 1}
   M2b tree   A-RW 0.000 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.125 P-ORACLE 0.625 ORACLE-TRUTH 0.625 · A-RW emitted {'cross': 8, 'dax': 4, 'ring': 5, 'square': 1, 'triangle': 4}
   M2b cup    A-RW 0.000 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.250 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 1, 'ring': 8, 'square': 2}
   M2b key    A-RW 0.125 A-RW-LR01 0.000 N-SHUF 0.000 P-ORACLE-RW 0.000 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · A-RW emitted {'cross': 7, 'ring': 2, 'square': 1}
   M6 size2: A-RW 0.773 A-RW-LR01 0.773 N-SHUF 0.636 P-ORACLE-RW 0.773 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · chance 0.500
   M6 size3: A-RW 0.900 A-RW-LR01 0.600 N-SHUF 0.500 P-ORACLE-RW 0.700 P-ORACLE 1.000 ORACLE-TRUTH 1.000 · chance 0.417
   the gaze's cost ORACLE-TRUTH − P-ORACLE on M1 (covered): graded 0.000 · size2 0.000 · size3 0.000

== S1a BARS at 10,000 scenes (A-RW; P-ORACLE's reading beside every mark; M1 on the 2- and 3-thing items) ==
20261101 M1 covered 0.891 (all 0.747; n 192/229; chance 0.544) bars ≥ 0.872 (0.90 × P-ORACLE-RW 0.969) and ≥ 0.800 (0.80 × P-ORACLE 1.000) → PASS · ORACLE-TRUTH 1.000 · A-RW-LR01 0.990 (reading)
          size2: 0.890 (n 136, chance 0.585) bars 0.867 · 0.800 (P-ORACLE-RW 0.963, P-ORACLE 1.000) → PASS · A-RW-LR01 0.993
          size3: 0.893 (n 56, chance 0.446) bars 0.884 · 0.800 (P-ORACLE-RW 0.982, P-ORACLE 1.000) → PASS · A-RW-LR01 0.982
          size1 (sanity): 1.000 (n 170)
          M2a refusal 0.603 (n 400) · false refusal 0.099 (n 192) · P-ORACLE 1.000 / 0.078 → FAIL (the learner fails: refusal; the whole-bar reading: FAIL)
          M2b 0.000 (n 48) · P-ORACLE 0.958 → FAIL · diamond (apart) 0.000 · P-ORACLE 0.500
          M6 NOT GRADABLE — the meeting was never seen (0 fixations on the dax at its scene)
          N-SHUF M1 0.552 ≤ chance 0.544 + 0.05 = 0.594 → PASS (size2 0.566 vs 0.585; size3 0.518 vs 0.446)
20261102 M1 covered 0.905 (all 0.743; n 201/245; chance 0.543) bars ≥ 0.869 (0.90 × P-ORACLE-RW 0.965) and ≥ 0.800 (0.80 × P-ORACLE 1.000) → PASS · ORACLE-TRUTH 1.000 · A-RW-LR01 0.980 (reading)
          size2: 0.895 (n 152, chance 0.579) bars 0.876 · 0.800 (P-ORACLE-RW 0.974, P-ORACLE 1.000) → PASS · A-RW-LR01 0.987
          size3: 0.939 (n 49, chance 0.432) bars 0.845 · 0.800 (P-ORACLE-RW 0.939, P-ORACLE 1.000) → PASS · A-RW-LR01 0.959
          size1 (sanity): 1.000 (n 153)
          M2a refusal 0.497 (n 400) · false refusal 0.075 (n 201) · P-ORACLE 1.000 / 0.119 → FAIL (the learner fails: refusal; the whole-bar reading: CEILING-BOUND)
          M2b 0.083 (n 48) · P-ORACLE 0.938 → FAIL · diamond (apart) 0.125 · P-ORACLE 0.500
          M6 covered 0.724 (all 0.500; n 29/42; chance 0.460) · P-ORACLE 1.000 → UNDERPOWERED
          N-SHUF M1 0.587 ≤ chance 0.543 + 0.05 = 0.593 → PASS (size2 0.618 vs 0.579; size3 0.490 vs 0.432)
          UNDERPOWERED (n < 30): M6
20261103 M1 covered 0.919 (all 0.785; n 211/247; chance 0.540) bars ≥ 0.866 (0.90 × P-ORACLE-RW 0.962) and ≥ 0.800 (0.80 × P-ORACLE 1.000) → PASS · ORACLE-TRUTH 1.000 · A-RW-LR01 0.981 (reading)
          size2: 0.932 (n 148, chance 0.581) bars 0.864 · 0.800 (P-ORACLE-RW 0.959, P-ORACLE 1.000) → PASS · A-RW-LR01 0.980
          size3: 0.889 (n 63, chance 0.444) bars 0.871 · 0.800 (P-ORACLE-RW 0.968, P-ORACLE 1.000) → PASS · A-RW-LR01 0.984
          size1 (sanity): 1.000 (n 149)
          M2a refusal 0.598 (n 400) · false refusal 0.043 (n 211) · P-ORACLE 0.998 / 0.109 → FAIL (the learner fails: refusal; the whole-bar reading: CEILING-BOUND)
          M2b 0.104 (n 48) · P-ORACLE 0.917 → FAIL · diamond (apart) 0.000 · P-ORACLE 0.625
          M6 covered 0.812 (all 0.619; n 32/42; chance 0.474) · P-ORACLE 1.000 → PASS
          N-SHUF M1 0.479 ≤ chance 0.540 + 0.05 = 0.590 → PASS (size2 0.561 vs 0.581; size3 0.286 vs 0.444)
per seed: M1 PASS/PASS/PASS · M2a FAIL/FAIL/FAIL · M2b FAIL/FAIL/FAIL · M6 NOT GRADABLE/UNDERPOWERED/PASS · N-SHUF PASS/PASS/PASS
every bar at all 3 seeds (M6 at the seeds where the meeting was seen: 20261102, 20261103): M1 PASS · M2a no · M2b no · N-SHUF PASS · M6 no → S1a does not pass
refutations: T1 (A-RW M1 < 0.6 × P-ORACLE-RW) 20261101:no 20261102:no 20261103:no · one-meeting (M6 < 0.5 while M1 passes) 20261101:n/g 20261102:no 20261103:no
```

### 13.5 · What the marks say [the numbers are Certain as printed; the readings Likely]

- **M1 PASSES at all three seeds** on the graded 2- and 3-thing items: A-RW 0.891 / 0.905 / 0.919, against 0.90 × P-ORACLE-RW ≈ 0.87 and 0.80 × P-ORACLE = 0.80. Every scene size passes too. T1 (A-RW < 0.6 × P-ORACLE-RW) is not refuted at any seed. **Words ground in this eye's space from ambiguous scenes by the delta rule.**
- **M2a FAILS at all three seeds**, on the REFUSAL half (0.603 / 0.497 / 0.598 < 0.80), which P-ORACLE reaches (1.000 / 1.000 / 0.998). The false-refusal half passes (0.099 / 0.075 / 0.043).
- **M2b FAILS at all three seeds:** 0.000 / 0.083 / 0.104. A-RW names never-taught shapes with a taught shape word; A-RW emitted mostly cross, ring and square. P-ORACLE's DISTANCE band refuses them (0.958 / 0.938 / 0.917).
  - So T4′ («refusing is a separate job») is NOT refuted in this world: A-RW's naming band cannot refuse, and a distance band can.
  - Diamond, read apart, gives A-RW 0.000 / 0.125 / 0.000 and P-ORACLE 0.500 / 0.500 / 0.625.
- **M6** reads NOT GRADABLE at 20261101 (the meeting was never seen), UNDERPOWERED at 20261102 (0.724 on 29 covered items), and PASS at 20261103 (0.812, n 32). P-ORACLE reads 1.000 at both gradable seeds. The one-meeting write is not refuted.
- **N-SHUF stays at chance** at all three seeds (0.552 ≤ 0.594; 0.587 ≤ 0.593, a margin of 0.006; 0.479 ≤ 0.590).
- **S1a does not pass** (M2a, M2b and M6's seed 2).
- **The reading arm A-RW-LR01 (lr 0.01, no bar) shows that the lock-in happens on the real stream.**
  - M1 is 0.990 / 0.980 / 0.981 against A-RW's 0.891 / 0.905 / 0.919.
  - M2a refusal is 0.892 / 0.845 / 0.880 against 0.603 / 0.497 / 0.598, with false refusal 0.068 / 0.055 / 0.057. It would meet M2a's bar at every seed (a reading, no bar).
  - Forced colour naming is 0.888 / 0.876 / 0.899 against A-RW's 0.659 / 0.542 / 0.644.
  - M2b stays low (0.208 / 0.146 / 0.062).
- **The gaze's cost is coverage alone.** On covered items both oracles read 1.000 (the gaze's cost on M1 is 0.000). On all items P-ORACLE reads 0.838 / 0.820 / 0.854 against ORACLE-TRUTH's 1.000.
- **The 0.90 promise, checked:** P-ORACLE's «what is this?» emits the true word 0.90–0.96 per type at 10,000 scenes. The in-sample distance band's under-coverage measured on the synthetic world (0.007 at 147 referents) is small at this n.

### 13.6 · RAISED in this section

1. **M2a's CEILING-BOUND is read PER HALF.** The bar reads CEILING-BOUND only when every half the learner fails is also failed by P-ORACLE.
   - The whole-bar reading («P-ORACLE fails the conjunction» → CEILING-BOUND) is printed beside, and it would read CEILING-BOUND at seeds 2–3.
   - The per-half reading reads FAIL there: A-RW fails the half the oracle reaches.
   - S1a's verdict is the same either way.
2. **UNDERPOWERED is read before PASS** (the signed «a mark with n < 30 items per seed reads UNDERPOWERED»). M6 at seed 2 has n = 29 covered items of 42: coverage is 0.69 on 2- and 3-thing scenes.
3. **M1's per-size bars** are printed with their own marks; the pooled 2–3 line is the verdict line. All pass here, so the two readings agree.
4. **The type-aware reader's declared details:**
   - equal class priors in the within-type posterior (StreamingLDA's own scores);
   - one ε for all three types;
   - a word with n < 9 referents takes the median distance band (dax: 1 referent);
   - the per-type and per-template M1 rows are computed over the graded items.
5. **The co-signature's change after the seat's text.** The builder implemented d54e6c0's text first (4835449) and caught the co-signed change by the sha guard before any run; 91f2495 implements 74be9e0. The seat named d54e6c0 in its message; the co-signed file is the one on disk.

### 13.7 · The suite on the final code

Run on **311caff**, the last commit that touches anything but this file. Each line is read from its log, never from a pipe, and each log has 0 `ERROR:` / `FAIL:` blocks:
- **The whole brain suite under the venv:** `Ran 487 tests in 490.824s` / `OK (skipped=3)`; log `/data/dev/brain-runs/scene/logs/suite-venv-311caff.log`.
  - 471 before, plus the 16 new scene tests.
  - It ran at twice fa0dfd1's wall time (223 s), with Test B launched beside it after the unit.
- **The scene package under /usr/bin/python3:** `Ran 85 tests in 17.357s` / `OK`; log `/data/dev/brain-runs/scene/logs/suite-scene-sys-311caff.log`.
- **Red on each parent:**
  - 3d3f5d2: `amend2-red-3d3f5d2.log`, 13 errors + 1 failure;
  - 4835449: `amend2b-red-4835449.log`, 2 errors;
  - 91f2495: 1 failure + 1 error (TestVerdictReadings).
