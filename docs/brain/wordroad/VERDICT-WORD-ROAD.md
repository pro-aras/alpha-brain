# VERDICT WORD-ROAD, stage 1 — the organism meets every word of an utterance (the gene `HEAR`), graded on replays of the closed lean lives

*Claude (Fable 5.1, the seat), 2026-09-29 14:53 +0400. The law: `PREREG-WORD-ROAD.md` in this folder, signed by both on the final text (sha256 7ed1d132…). The gate was read once. Every figure below is read from `/data/dev/brain-runs/day0929/wordroad/read/gate.json`.*

## The verdict
1. **`HEAR` is NOT adopted as written.** The mark that failed: P. The decision rule of §4 asks for every mark at every seed.
2. **Do the cells point by a size or colour word they now hear?** On the items that NEED the word, the whole phrase is right 0.605 of the time on test 1 and 0.305 on test 3; the shape word alone, in the same cells, 0.544 and 0.274. The gaps are +0.061 (n 228, p 6.6e-04) and +0.031 (n 226, p 1.2e-01); the bar is + 0.10 with p < 0.001.
3. **The old ability:** test 1 on the phrases OFF could already answer reads ON 0.736 against OFF 0.732 (n 235); «I don't know» by the grader's rule reads ON 0.944 against OFF 0.889 (n 288).
4. **The price:** the mind's cost per training canvas is × 1.367 / 1.338 / 1.356 of OFF's at the three seeds (bar ≤ 1.5).

## The marks, per world seed (20261101 / 20261102 / 20261103)
| Mark | What was read | The reading | Bar | Verdict |
|---|---|---|---|---|
| I1 | the line absent: the twin's replay against rung 2's recorded twin journal; the BRAIN genome's against the life's journal | exits 0 / 0 / 0 (rows 24475 / 24471 / 24466) and 0 / 0 / 0 (rows 34481 / 34477 / 34472) | every row equal | **PASS** |
| I2 | ON against OFF, `words` masked: the first difference | seq 6 / 3 / 3; the first multi-word canvas is scene 1 / 0 / 0, eye seq 6 / 3 / 3 | they differ, first there | **PASS** |
| A · test 1 | phrases the road can be asked (not «unheard») | ON 794 / 793 / 794 of 794 / 793 / 794; OFF 181 / 178 / 170 | = 1.000 | **PASS** |
| A · test 3 | phrases the road can be asked (not «unheard») | ON 120 / 120 / 120 of 120 / 120 / 120; OFF 0 / 0 / 0 | = 1.000 | **PASS** |
| P · test 1 | NEEDED items (n 79 / 73 / 76): the whole phrase · the shape word alone · the gap | 0.671 / 0.521 / 0.618 · 0.620 / 0.507 / 0.500 · 0.051 / 0.014 / 0.118 | pooled gap ≥ 0.10, p < 0.001; above 0 at every seed; above every NULL-10 draw | **FAIL** |
| P · test 3 | NEEDED items (n 77 / 75 / 74): the whole phrase · the shape word alone · the gap | 0.325 / 0.293 / 0.297 · 0.286 / 0.280 / 0.257 · 0.039 / 0.013 / 0.041 | pooled gap ≥ 0.10, p < 0.001; above 0 at every seed; above every NULL-10 draw | **FAIL** |
| K | test 1 where OFF could answer (n 80 / 81 / 74): ON · OFF | 0.738 / 0.728 / 0.743 · 0.750 / 0.704 / 0.743 | pooled ON − OFF ≥ − 0.05 | **PASS** |
| K2 | never-taught shapes, both sets (n 96 / 96 / 96): ON · OFF | 0.958 / 0.917 / 0.958 · 0.896 / 0.885 / 0.885 | pooled ON − OFF ≥ − 0.05 | **PASS** |
| G | word cells; canvases where the word cells born are not the words first heard | ON 14 / 14 / 14 cells, OFF 7 / 7 / 7; wrong canvases 0 / 0 / 0 of 10000 / 10000 / 10000 | 14 words, each born where first heard | **PASS** |
| C | ms per training canvas, scenes 9,000–9,999: ON · OFF · ratio | 94.30 / 92.81 / 93.14 · 68.98 / 69.38 / 68.66 · 1.367 / 1.338 / 1.356 | ≤ 1.5 | **PASS** |

## P, pooled over the three seeds
| Test | n | the whole phrase | the shape word alone | gap | pairs for / against | p (exact, one-sided) | above 0 at every seed | NULL-10 at 20261102: ON against the draws' highest | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 228 | 0.605 | 0.544 | +0.061 | 16 / 2 | 6.56e-04 | True | 0.521 against 0.644: above every draw False | **FAIL** |
| 3 | 226 | 0.305 | 0.274 | +0.031 | 17 / 10 | 1.24e-01 | True | 0.293 against 0.520: above every draw False | **FAIL** |

NULL-10's ten draws (the whole phrase, the same items, utterances shuffled among the scenes): test 1 0.479, 0.507, 0.644, 0.534, 0.507, 0.425, 0.548, 0.521, 0.507, 0.493 · test 3 0.413, 0.440, 0.413, 0.453, 0.387, 0.427, 0.427, 0.360, 0.400, 0.520.

**Readings beside P, never graded** (per seed):
- test 1: chance (1 / hypotheses) 0.532 / 0.527 / 0.537, exact p of the whole phrase against it 5.2e-03 / 6.0e-01 / 8.1e-02; a road with a perfect shape word and no other 0.568 / 0.587 / 0.601; the most-fixations pointer 0.525 / 0.541 / 0.592; «none» read forced: 15 / 16 / 15 of the whole phrase, 22 / 19 / 19 of the shape word alone; items with an «unheard» phrase 0 / 0 / 0.
- test 3: chance (1 / hypotheses) 0.489 / 0.498 / 0.505, exact p of the whole phrase against it 1.0e+00 / 1.0e+00 / 1.0e+00; a road with a perfect shape word and no other 0.565 / 0.587 / 0.581; the most-fixations pointer 0.526 / 0.580 / 0.554; «none» read forced: 25 / 25 / 25 of the whole phrase, 36 / 42 / 38 of the shape word alone; items with an «unheard» phrase 0 / 0 / 0.

## What the cells hold — a reading made AFTER the read, from the gate's own files
*(the seat, 2026-09-29 14:54 +0400. It changes no mark. It is here so the failure has a measured shape and not a guessed cause (#243). Source: `records/edges-reading.json`, read from ON's answers' `scores_by_word`; items with both a target hypothesis and another thing's hypothesis in view: 69 / 66 / 67 on test 1 and 72 / 70 / 69 on test 3.)*

| On the NEEDED items, in ON's cells | test 1 | test 3 (never-seen colour × shape pairs) |
|---|---|---|
| items read | 69 / 66 / 67 | 72 / 70 / 69 |
| the TARGET has no edge at all to its shape word | 25 / 35 / 33 | **72 / 69 / 69** |
| the OTHER thing has no edge to that shape word | 37 / 30 / 30 | 31 / 38 / 33 |
| the size or colour word's edge is larger on the TARGET | 32 / 21 / 36 | 13 / 7 / 15 |
| … larger on the OTHER thing | 12 / 13 / 6 | 18 / 20 / 14 |
| … equal (both 0 included) | 25 / 32 / 25 | 41 / 43 / 40 |
| the TARGET has no edge to its size or colour word | 30 / 41 / 27 | 56 / 63 / 51 |
| mean size or colour edge: on the target · on the other thing | 0.075 / 0.094 / 0.086 · 0.023 / 0.036 / 0.034 | 0.021 / 0.010 / 0.035 · 0.041 / 0.034 / 0.029 |

1. **On test 1 the cells did take a trace of the size and colour words.** The word's edge is larger on the target 89 times and larger on the other thing 31 times, of 202 items. But it is weak (a mean edge under 0.1) and absent on 98 of 202 targets. So the pointing moves by + 0.061, in the right direction (16 pairs against 2), under the margin of + 0.10.
2. **At 20261102 that reading sits inside the shuffled-utterance draws.** ON reads 0.521; of the ten draws 3 are higher and 1 equal.
3. **On test 3 the cells hold NOTHING for the target.** A never-seen colour × shape pair has no edge to its own shape word on 210 of 211 items. The other thing, a look the cells have seen, has one on about half. So the road points at the look it knows and reads 0.305, under chance (0.49–0.51) and under every shuffled draw (ON 0.293; the draws 0.360–0.520). **A cell is a whole look.** It cannot compose a colour with a shape it never saw together. The brain composes these pairs at 0.966 / 1.000 / 0.983 (VERDICT-BRAIN-IN-BODY, test 3).
4. **What this does not show:** why an edge is absent (a glance that lit no cell, a cell with no edge yet, or a pruned edge). The three are not told apart here.

## K and K2 are point rules (the PREREG says so)
- **K**, pooled n 235: ON − OFF +0.004 ± 0.007; pairs 2 for ON, 1 for OFF; the exact sign test for «ON lower» p 0.8750.
- **K2**, pooled n 288: ON − OFF +0.056 ± 0.014; pairs 17 for ON, 1 for OFF; the exact sign test for «ON lower» p 1.0000.
- **K2's words.** «I don't know» share: ON 0.885 / 0.885 / 0.854, OFF 0.896 / 0.885 / 0.885. Words emitted by kind, ON: {'colour': 7, 'shape': 4} / {'colour': 3, 'shape': 8} / {'colour': 10, 'shape': 4}; OFF: {'shape': 10} / {'shape': 11} / {'shape': 11}.

## G's readings (they decide nothing here; they price stage 2)
- Sight cells ON / OFF at the end: 1.000 / 1.000 / 1.000. Births refused by the budget ON / OFF: 1.008 / 1.002 / 1.002. Refused as redundant ON / OFF: 1.937 / 1.931 / 1.934.
- Refused by the cap: {'off': 0, 'on': 0} / {'off': 0, 'on': 0} / {'off': 0, 'on': 0}. A word cell two words lit: 0 / 0 / 0. Words the ear refused: 0 / 0 / 0.

The series at 20261102, every 1,000 worded canvases (ON / OFF):

| canvases | sight cells | refused by budget | refused redundant |
|---|---|---|---|
| 1,000 | 499 / 501 | 1,466 / 1,494 | 1,174 / 632 |
| 2,000 | 582 / 582 | 3,115 / 3,160 | 2,432 / 1,291 |
| 3,000 | 1,006 / 1,008 | 4,169 / 4,226 | 3,895 / 2,054 |
| 4,000 | 1,139 / 1,141 | 5,148 / 5,203 | 5,400 / 2,824 |
| 5,000 | 1,222 / 1,224 | 6,056 / 6,109 | 6,889 / 3,608 |
| 6,000 | 1,305 / 1,306 | 7,009 / 7,055 | 8,427 / 4,404 |
| 7,000 | 1,389 / 1,390 | 7,895 / 7,930 | 10,017 / 5,203 |
| 8,000 | 1,471 / 1,470 | 8,701 / 8,710 | 11,581 / 6,021 |
| 9,000 | 1,554 / 1,553 | 9,532 / 9,524 | 13,229 / 6,826 |
| 10,000 | 1,637 / 1,637 | 10,297 / 10,272 | 14,813 / 7,673 |
| 10,000 | 1,637 / 1,637 | 10,297 / 10,272 | 14,813 / 7,673 |

## The runs
```
2026-09-29 13:30:13 +0400 the gate starts at 0ca9a74; PREREG sha256 7ed1d132cd458fde
13:30:13 pair 20261101 starts; load 0.93 0.74 1.10; other python processes 8
13:46:42 pair 20261101 done: off (against the recorded twin) exit 0 · on exit 0; load 1.06 1.47 1.52
13:46:42 pair 20261102 starts; load 1.06 1.47 1.52; other python processes 6
14:02:58 pair 20261102 done: off (against the recorded twin) exit 0 · on exit 0; load 1.33 1.55 1.67
14:02:58 pair 20261103 starts; load 1.33 1.55 1.67; other python processes 6
14:19:26 pair 20261103 done: off (against the recorded twin) exit 0 · on exit 0; load 1.04 1.46 1.70
2026-09-29 14:19:26 +0400 phase 1 done
14:49:06 null-9 exit 0
14:49:55 null-8 exit 0
14:49:55 null-5 exit 0
14:50:26 null-4 exit 0
14:50:26 null-7 exit 0
14:50:27 null-6 exit 0
14:50:31 null-1 exit 0
14:50:31 null-3 exit 0
14:50:31 null-2 exit 0
14:50:31 grade-on-20261101 exit 0
14:50:31 grade-on-20261103 exit 0
14:50:31 grade-on-20261102 exit 0
14:50:31 brain-20261101 exit 0
14:50:31 brain-20261102 exit 0
14:50:31 brain-20261103 exit 0
14:50:31 null-10 exit 0
14:50:31 grade-off-20261103 exit 0
14:50:31 grade-off-20261102 exit 0
14:50:31 grade-off-20261101 exit 0
i1-brain-20261101 exit 0
i1-brain-20261102 exit 0
i1-brain-20261103 exit 0
2026-09-29 14:50:31 +0400 phase 2 done (a step failed: 0)
2026-09-29 14:51:52 +0400 the ONE read starts (tools/brain/wordroad_gate.py at 0ca9a74)
reader exit 1
2026-09-29 14:52:11 +0400 the read is done
```

## The suites on the gate's commit
```
the five suites on 0ca9a74 (2026-09-29 14:19:37 +0400 → 2026-09-29 14:43:55 +0400), BLAS threads 1
== scene exit=0
Ran 368 tests in 231.572s
OK
== brainvenv exit=0
Ran 770 tests in 697.275s
OK (skipped=2)
== genome exit=0
Ran 629 tests in 303.208s
OK (skipped=1, expected failures=6)
== creature exit=1
Ran 1199 tests in 1455.716s
FAILED (failures=1, skipped=6)
FAIL: test_61_questions_60_fetches_1_refused_rate (tests.creature.test_web_door.TestWebDoorGating.test_61_questions_60_fetches_1_refused_rate)
== tools exit=0
Ran 80 tests in 268.505s
OK

the creature suite's ONE failure above was a wall-clock test (60 fetches in 2.0 s) run beside the gate's phase 2 (load about 15): 46 were made.
that test alone on an idle box: 3 runs, 3 OK (2.0 s each; /data/dev/brain-runs/day0929/wordroad/logs/webdoor-alone-{1,2,3}.log).
the creature suite WHOLE again on 0ca9a74, 14:52:59 to 15:08:44 +0400, load 1 to 3: exit 0
Ran 1199 tests in 945.466s
OK (skipped=6)
```

## What follows (the seat, under his 2026-09-29 00:48 word; his to overturn)
- **The line is NOT adopted.** No template carries `HEAR`. The cells stay on the last word. The brain stays the one hearer of every word.
- **Stage 2 is NOT built.** It was the widening of the full organism's consumers under `HEAR`; with the line refused by its own gate there is nothing to widen.
- **The first LONG life (dated 2026-10-01) no longer waits on the word road.** It runs the full organism with the brain (`young 3 nearest`) and the cells as they are.
- **The gene stays in the tree, OFF, behind its fence**, with its gate, its reader and its records, so the result can be re-read. With the line absent every row of every life is what it was (I1, six replays, every row equal).
- **What the day changed in the plan for words:** the cells are not the road to size, colour or composition. The brain organ is. The next build for words is the wiring that lets the organism USE its brain (its thinking, its speaking, its questions read the brain's answers), not a wider road into the cells.

## What this does and does not show
- **Shown:** under the line every word has a cell named by itself; every pointing phrase can be asked; and the figures above.
- **Not shown:** anything about the full organism. Stage 2 widens SLEEP, PREDICT, SURPRISE and the think road, each under its own signed line, before `HEAR` stands beside them.
- **Not shown:** that the organism uses its brain. That wiring is its own build.
- A and G are wiring pins. K and K2 are point rules, underpowered as tests. NULL-10 is one seed. C prices a replay of the lean body, never a life under the unit.
- The test sets were read before for the brain. For the organs' road under `HEAR` this was the first read, and no value of the law was chosen on them.
