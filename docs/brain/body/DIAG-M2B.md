# DIAG-M2B — why «I don't know» fails, and why a reader from CONFIDENT meetings does not repair it

*Claude (Fable 5.1, the seat), 2026-09-29 12:56 +0400. A diagnosis on TRAINING rows, with one reading of test sets already read. No gate was run. The never-used test set is unspent.*

**The question (PREREG-BRAIN-IN-BODY §7, F-M2B):** build the READER from the learner's CONFIDENT meetings only. «Confident» had no threshold on record.

**The answer:** no rule built from the brain's own signals makes its store right enough. Five signals were tried. Each stops at about 0.96 right. The reader needs about 0.98 or more. On the fresh test set, already read, the best rule at each seed reads 0.688 / 0.750 / 0.729 against the law's 0.646 / 0.708 / 0.729 and the bar 0.80. **F-M2B is not taken to its gate.**

## 1 · Method
- The tool: `tools/brain/diag/probe_fm2b.py`. Outputs: `/data/dev/brain-runs/day0929/fm2b/` (`run1` … `run4` keep each earlier run; `write_diag.py` wrote this file from them).
- The brain is the organ (`genome/brain.py`) under the template's BRAIN line, fed the training scenes in order, as the gate feeds it.
- **Training rows only:** the brain learns the first 8,000 training scenes of a world seed. The other 2,000 are validation rows: never learned, never a test scene.
- **The proxy for a never-taught shape:** one trained shape is taken OUT of the reader (its mean, its band, its rows in its type's covariance). A validation thing of that shape is CORRECT when no shape word holds it. This is test 2b's own rule.
- The truth is read by the bench only, to count what is right. No rule below reads it, except the two named readings (the exact-attribution reader and the dose).

## 2 · Controls
- The probe's reader at «keep everything» IS the organ's own reader: 13 words compared at each seed, band differences 0 / 0 / 0, largest difference of a mean 4.0e-15.
- The probe's «held» equals the organ's own road on 770 of 770 validation things (20261102).
- **Against the record:** on the fresh test set the probe's law reader reads 0.646 / 0.708 / 0.729; the record says 0.646 / 0.708 / 0.729. Its exact-attribution reader reads 0.896 / 0.875 / 0.833; the record's P-ORACLE-RW says 0.896 / 0.875 / 0.833. Both equal.

## 3 · What the store holds (shape words, 8,000 scenes)
| | 20261101 | 20261102 | 20261103 |
|---|---|---|---|
| stored meetings of shape words | 7,994 | 7,997 | 7,996 |
| views with ONE hypothesis (responsibility 1 by construction) | 0.537 | 0.537 | 0.524 |
| the named thing was seen by the eye | 0.894 | 0.890 | 0.896 |
| the attribution is right, every meeting | 0.844 | 0.839 | 0.845 |
| the attribution is right, ONE-hypothesis views (responsibility exactly 1) | 0.872 | 0.865 | 0.872 |
| «none» fired at the meeting, when the attribution was WRONG | 0.450 | 0.470 | 0.436 |
| «none» fired at the meeting, when it was RIGHT | 0.076 | 0.084 | 0.064 |

**The first finding.** A view with one hypothesis has responsibility 1 and is still wrong about 1 time in 8: the eye saw a distractor and missed the named thing. So a high responsibility is not a right attribution.

## 4 · Five signals, one ceiling
Each row: the share of meetings kept · the share of kept attributions that are right (three seeds).

| The signal (all the brain's own) | kept | right among kept |
|---|---|---|
| every meeting (the law) | 1.000 / 1.000 / 1.000 | 0.844 / 0.839 / 0.845 |
| 1 · responsibility ≥ 0.9 | 0.792 / 0.795 / 0.784 | 0.904 / 0.901 / 0.907 |
| 2 · «none» did not fire | 0.866 / 0.854 / 0.879 | 0.901 / 0.900 / 0.901 |
| 1 + 2 · responsibility ≥ 0.9 and «none» did not fire | 0.695 / 0.690 / 0.700 | 0.961 / 0.958 / 0.959 |
| 1 + 2 · responsibility ≥ 0.95 and «none» did not fire | 0.628 / 0.625 / 0.633 | 0.961 / 0.956 / 0.957 |
| 3 · the utterance's joint attribution ≥ 0.9, «none» did not fire (per scene) | 0.737 / 0.728 / 0.743 | 0.960 / 0.957 / 0.959 |
| 4 · every word points at the same thing, each ≥ 0.9, «none» did not fire (per scene) | 0.571 / 0.555 / 0.564 | 0.955 / 0.950 / 0.952 |
| 5 · pointed at AGAIN by the learner as it stands at the reading point, margin ≥ 0.0 (per scene) | 0.900 / 0.900 / 0.900 | 0.915 / 0.922 / 0.926 |
| 5 · pointed at AGAIN by the learner as it stands at the reading point, margin ≥ 2.0 (per scene) | 0.813 / 0.823 / 0.823 | 0.954 / 0.958 / 0.958 |
| 5 · pointed at AGAIN by the learner as it stands at the reading point, margin ≥ 4.0 (per scene) | 0.695 / 0.729 / 0.725 | 0.956 / 0.958 / 0.960 |

**The second finding.** Every signal stops near 0.96. What is left are scenes where the eye missed the named thing and a distractor fits the phrase. The learner's «none», asked again at the reading point, fires on 0.564 / 0.610 / 0.597 of the scenes whose named thing was unseen, and on 0.045 / 0.037 / 0.042 of the others. It cannot see the rest.

## 5 · How right the store must be (the dose)
The exact-attribution reader, with a share of its several-hypothesis rows replaced by a wrong hypothesis of the same view. The proxy of §1, three seeds.

| rows made wrong (of the several-hypothesis rows) | never-taught shape refused | another shape's name holds a taught shape |
|---|---|---|
| 0.00 | 0.766 / 0.838 / 0.802 | 0.349 / 0.343 / 0.336 |
| 0.01 | 0.753 / 0.816 / 0.786 | 0.375 / 0.366 / 0.366 |
| 0.02 | 0.748 / 0.786 / 0.770 | 0.395 / 0.406 / 0.386 |
| 0.04 | 0.692 / 0.736 / 0.719 | 0.534 / 0.488 / 0.515 |
| 0.06 | 0.684 / 0.708 / 0.686 | 0.547 / 0.668 / 0.635 |
| 0.08 | 0.632 / 0.610 / 0.626 | 0.636 / 0.697 / 0.711 |
| 0.12 | 0.498 / 0.484 / 0.463 | 0.785 / 0.819 / 0.811 |
| 0.16 | 0.454 / 0.327 / 0.369 | 0.844 / 0.875 / 0.856 |

**The third finding.** The reader is fragile. About half the rows are several-hypothesis rows, so «0.08» is about 4 in 100 of all rows. The wrong rows are other SHAPES: they put the scatter between shapes into the covariance that should hold the scatter within a shape, and the bands then hold every shape.

## 6 · The readers built from each rule
The proxy of §1 on the validation rows (three seeds). The last column is the worst seed's change against the law in: a taught shape held by its own name · its size word · its colour word.

| The reader's store | never-taught shape refused | worst change: shape · size · colour |
|---|---|---|
| every meeting, weighted by responsibility (the law) | 0.280 / 0.251 / 0.266 | +0.000 · +0.000 · +0.000 |
| «none» did not fire | 0.337 / 0.335 / 0.359 | -0.004 · -0.011 · -0.017 |
| responsibility ≥ 0.9, «none» did not fire | 0.399 / 0.425 / 0.429 | -0.016 · -0.030 · -0.034 |
| responsibility ≥ 0.95, «none» did not fire | 0.415 / 0.442 / 0.463 | -0.022 · -0.034 · -0.032 |
| the utterance's joint attribution ≥ 0.95 | 0.398 / 0.416 / 0.440 | -0.021 · -0.022 · -0.025 |
| every word agrees, each ≥ 0.9 | 0.399 / 0.434 / 0.441 | -0.025 · -0.031 · -0.039 |
| pointed at again, margin ≥ 2 | 0.399 / 0.395 / 0.378 | -0.008 · -0.014 · -0.010 |
| pointed at again, margin ≥ 4 | 0.434 / 0.430 / 0.405 | -0.018 · -0.021 · -0.013 |
| responsibility ≥ 0.95, «none» did not fire; mean and covariance fitted on inliers (1 round) | 0.390 / 0.395 / 0.411 | -0.021 · -0.022 · -0.033 |
| responsibility ≥ 0.95, «none» did not fire; rows beyond the band dropped (1 round) | 0.636 / 0.612 / 0.660 | -0.116 · -0.129 · -0.134 |
| THE TRUE referent of every meeting (a reading: the bench's truth) | 0.766 / 0.838 / 0.802 | +0.000 · +0.011 · +0.005 |
| the same, rows beyond the band dropped (1 round) | 0.939 / 0.981 / 0.943 | -0.093 · -0.090 · -0.097 |

- Dropping the rows beyond the band raises the refusal only by lowering the hold rate about 0.09 a round, the exact-attribution reader's too. It moves along the trade; it is not a repair.
- Fitting the mean and covariance on inliers does not help.

## 7 · The real mark, on test sets already read
This is a diagnostic. Both sets have been read before. It is not the gate and chooses nothing. The brain learned all 10,000 scenes. n = 48 at each seed.

| The reader's store | fresh set (2026140x) | older set (2026120x) | house, fresh | tree, fresh |
|---|---|---|---|---|
| the law | 0.646 / 0.708 / 0.729 | 0.688 / 0.583 / 0.625 | 0.00 / 0.12 / 0.00 | 0.00 / 0.12 / 0.38 |
| «none» did not fire | 0.646 / 0.729 / 0.729 | 0.688 / 0.583 / 0.688 | 0.00 / 0.12 / 0.00 | 0.00 / 0.25 / 0.38 |
| responsibility ≥ 0.9, «none» did not fire | 0.667 / 0.750 / 0.729 | 0.688 / 0.625 / 0.688 | 0.00 / 0.25 / 0.00 | 0.00 / 0.25 / 0.38 |
| responsibility ≥ 0.95, «none» did not fire | 0.688 / 0.750 / 0.729 | 0.688 / 0.646 / 0.708 | 0.12 / 0.25 / 0.00 | 0.00 / 0.25 / 0.38 |
| joint attribution ≥ 0.95 | 0.667 / 0.750 / 0.729 | 0.688 / 0.646 / 0.688 | 0.00 / 0.25 / 0.00 | 0.00 / 0.25 / 0.38 |
| every word agrees | 0.688 / 0.750 / 0.729 | 0.688 / 0.667 / 0.688 | 0.12 / 0.25 / 0.00 | 0.00 / 0.25 / 0.38 |
| pointed at again, margin ≥ 2 | 0.667 / 0.729 / 0.729 | 0.688 / 0.583 / 0.688 | 0.00 / 0.12 / 0.00 | 0.00 / 0.25 / 0.38 |
| pointed at again, margin ≥ 4 | 0.688 / 0.750 / 0.729 | 0.688 / 0.625 / 0.688 | 0.12 / 0.25 / 0.00 | 0.00 / 0.25 / 0.38 |
| THE TRUE referent (a reading) | 0.896 / 0.875 / 0.833 | 0.896 / 0.812 / 0.896 | 0.88 / 0.88 / 0.62 | 0.50 / 0.38 / 0.38 |

**The fourth finding.** No rule reaches 0.80 at any seed on either set: the highest reading is 0.750. A rule changes the law's reading by +0.000 to +0.083. Houses and trees stay «a known shape».

## 8 · Decision, and what follows
- **F-M2B is closed as NOT A FIX.** It is not built into the organ and not taken to its gate. The never-used test set is kept for a fix that the bench predicts can pass.
- **The cause is the eye, not the reader's threshold.** About 1 meeting in 10 the eye never saw the named thing. «None» catches a little over half of those. The rest enter the store as clean pictures of the wrong shape.
- **The fix that attacks the cause is the look-again act** (dated 2026-09-30): one more fixation before a meeting is stored. It removes unseen referents at the source. Its ceiling here is the exact-attribution reader's: 0.83 to 0.90.
- **A second road, not tried:** a reader whose covariance does not take a wrong shape for scatter. The dose table is its first gate: a candidate must hold its refusal at 0.04 wrong rows.

## 9 · What this does not show
- It does not show that the look-again act passes test 2b. No look-again run exists.
- The proxy is harsher than the real mark: taught shapes are nearer to each other than the never-taught shapes are to them. It ranks rules; it does not predict a value.
- The readings of §7 are on sets read before. They are not evidence for or against a future gate on a new set, beyond their plain size.
- Every figure is at lr 0.01, eps 0.3, young 3 nearest, 8,000 or 10,000 scenes, three world seeds.
