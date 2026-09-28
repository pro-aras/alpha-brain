# S1a «THE SCENE-TALK WORLD» — the builder's hand-back

*edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:39 +0400 — written at THE FIRST GATE's STOP. The law: `docs/brain/r3/PREREG-R3-TONIGHT.md` §S1a in genome-wt-brain3, sha256 `18250d201b6aecbdc95058267f6cab163ca1450e82f4f1d8f9724a1849215968` (checked before the gate: equal). Branch `scene-talk` of `/data/dev/genome-wt-scene`, from b1-tape2 f393e5a.*

## 0 · The verdict: THE FIRST GATE says STOP. No full stream was run.

- **The instrument verdict fires for COLOUR.** P-ORACLE's per-type naming, leave-one-scene-out on the 113 one-thing scenes among the first 300 of seed 20261101, reads colour **0.832 = 94/113**, against 0.90 × the probe's 0.933 = **0.8397**. One item decides it: 95/113 = 0.8407 would not fire.
- **The brief's own stop fires too.** Step 6 says ORACLE-TRUTH < 0.95 on 300 scenes → STOP; ORACLE-TRUTH reads **0.790**.
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
| (this commit) | the diagnosis scripts `tools/scene/diag/*.py` and this hand-back |

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
- **ORACLE-TRUTH reads BELOW P-ORACLE** (0.790 vs 0.815). One forced window at the centroid is compared against a hypothesis that averages 1–4 fixations. So «the organ's ceiling without the gaze» is not a ceiling at 300 scenes. Stage −1 agrees: forced-window shape NCM 0.667, against 0.756 for the hypothesis.
- **N-SHUF reads under its own chance** (0.713 vs 0.758 on covered items). Chance is high because most items are one-thing scenes with a single hypothesis.
- **ε landed at the grid's end** (0.3, R49's grid {1e-4 … 0.3}). ε 0.6 and 0.9 give the same colour reading (0.832), so ε does not move the verdict (§3).

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
    - STOP = the instrument verdict, where the brief says ORACLE-TRUTH < 0.95. Both fire here.

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

- **The eye / cache, solo, idle box** (load 1.2, 12:26): seed 1's 10,498 canvases took 91.9 CPU-s user and 1:32 wall, ≈ 8.8 ms a canvas. That covers render, `glances`, png sha, the forced windows and the 10-row self-check. RSS was 247 MB.
- **Stage −1's 300 canvases:** 3.2 s.
- **THE FIRST GATE:** 19.4 s wall, covering the toy caches (1,200 canvases), the toy, 6 ε fits, 113 LOO fits, and 5 arms × 300 with their answers.
- **Load fact:** at 12:22, with Test B's 8 pricing processes running (load 9), the seat's own `seat_eye_probe.py` read **48.6 ms a call**, against 5.7 ms idle.
- **After a ruling:**
  - seeds 2–3's caches are one command each (≈ 92 CPU-s each), or the unit's first wave builds them;
  - `run.py price` (solo, then 5 × 3 at once) is one command.

  Estimate, not a price [Likely]: the arms are ≈ 1 s per 60 scenes in the smoke test, so the full run is well under the PREREG's 1 CPU-h.

## 9 · What a PROCEED needs (none of it done by the builder)

1. A ruling on P-ORACLE's reader, recorded on the PREREG (a dated amendment, a new sha passed to the builder). The reader is type-blind as built, or a per-type Σ. The verdict's protocol is LOO on the gate's scenes as built, or another. And the verdict thresholds, if the reader changes.
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

## 11 · The suite on the final code

@@SUITE@@
