# A4L-ANSWER — builder report
Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:1x +0400. Branch `a4l-answer` off master at the
dispatch commit `a17cb0e`. Brief: `docs/briefs/A4L-ANSWER.md`. Law: `docs/A4-LADDER-PREREG.md` §1, §2.2, §4, §6 M2.

## What is NOT done, and why

1. **A4 (THE LOOP) and A5 (HEDGE) are not computed from a live life.** Both are "printed, no bar" marks read
   from an 8 h rung's own tape (what-is questions formed from `minority` abstentions; the `minority` share on
   the folder's photographs) — this builder has no launched rung to read from; that is the orchestrator's job
   at pre-flight/read time (§4 schedule). As an early proxy I ran `tools/answer_readtwin.py` against
   alpha4-1's snapshot copy: Q1 `hedge_rate` reads **0.324** under BOTH laws (unchanged — seen-word Q1 rarely
   falls under the majority ceiling on a ~4,500-cell organism, so the hedge population barely moves). Not a
   substitute for A4/A5; printed as a data point only.
2. **Control (c), the #231(5) trap, is INCONCLUSIVE in the toy I built** (`scratch/task4_controls.py`, real
   front, alpha4-1's snapshot copy, plant "zog" shown 5 times via `moment()`): after 5 showings the NEW law
   answers "zog" correctly on its own held-out renders **0/10**, which looks like a costly regression — but
   the **OLD law answers 0/10 too** (its actual answers: mostly the empty-string cell, once "ratio", never
   "zog" — see the numbers below). Diagnosed correctly (compare against the read-side override, never the
   raw minority count alone), this is a pre-existing 5-showing generalisation limit unrelated to the clause,
   not a cost it introduces. A3's real reading needs alpha4-1's own close (plant shown ≈ hour 21, a properly-
   progressing organism) — scheduled after 05:00, not reproducible in a snapshot toy today. RAISED, not
   worked around.
3. **Task 7's tape twin found ZERO divergent decisions** between `A4L-ANSWER.genome` and `A4L-FLOOR.genome`
   replayed over alpha4-1's hour-1 fixture (4,322 mind rows, byte-identical including every `think` outcome
   count). This is an honest finding, not a bug: `tools/answer_readtwin.py` run on the real (much larger,
   ~4,500-cell) snapshot shows the clause IS active and changes real decisions there (spiral 10/10 "dot"
   sure-bare under the old law → 10/10 `minority` under the new law) — the hour-1 cut is simply too early
   and too short for THINK's word work (the only decision-bearing `recall_many` consumer a replay exercises)
   to accumulate 5 episodes of a word with fewer than a majority lighting. Said here, not hidden.
4. **One PRE-EXISTING test failure, confirmed unrelated** (`tests/genome/test_read_lexicon_parser.py::
   TestSenseReadParses::test_the_real_deployed_line_in_alpha4_genome_parses_identically`, `AssertionError:
   20 != 5`): a stale pin against `genome/ALPHA4.genome`'s own SENSE read cadence, which a later commit
   (7bbc995, "the reader at every 20 s / 4 words on pre-3's final reading") changed from 5 s to 20 s without
   re-pinning this test. Verified via `git stash` (all my edits removed, dispatch commit `a17cb0e` restored):
   the SAME failure reproduces identically. I never touched `genome/ALPHA4.genome` or this test file
   (`git diff --stat genome/ALPHA4.genome` is empty). RAISED, not fixed — outside this rung's one-difference
   surface.
5. **`tools/pin_g1.py` step (1) fails pre-existing too** (development hash `7686da77162b6179` vs recorded
   `0d51df0db87dbdfd`), confirmed via the same `git stash` test on the dispatch commit — a G0b-era reference
   (2026-09-19) never re-pinned after the ALPHA4/GROW hash-law change (`85bf792`, "RE-PIN the skeleton digest
   … G's declared hash-law change"). Step (2), the K=1 `recall_many`/`recall` reduction this rung actually
   touches, verified SAME in isolation (`scratch/pin_g1_step2_only.py`): 397 questions, 2,280 edge pairs, all
   matching, on G0b.genome where ANSWER is undeclared (the majority gate structurally inert).
6. **No planted offender added to `tools/gate_g4.py`'s writer sweep.** Its scope is `creature/world_maker.py`,
   `creature/ask.py`, `creature/tape.py`, `creature/think_thread.py` + `creature/senses/*.py`. A4L-ANSWER adds
   no new SENSE module — every file I touched (`genome/machinery.py`, `genome/questions.py`, `creature/
   genes.py`, `tools/self_exam.py`, `tools/verdict_life.py`, `tools/answer_readtwin.py`, tests) is outside
   that sweep, so no offender applies. Confirmed gate 1 stays green as a pure regression check.

## Tests, RED → GREEN

Task-first re-derivation of M2 with my own instrument (`org._lit` directly, never the not-yet-written gate) —
`scratch/task0_measure.py` / `scratch/task0_early.py`, logs `scratch/task0_out.txt` / `scratch/task0_early_out.txt`.
STOP rule (§ task 0): seen ≥3-glance share 160/160 (1.0000, ≥ 0.150 needed) and spiral ≥3-glance count 0/10
(≤ 2 needed) — **clear, proceeded**.

Core (`genome/machinery.py` parser + `Organism.recall_many` + `genome/questions.py` widened) —
`tests/genome/test_answer_grade.py` (extended: `TestMajorityClauseParser`, `TestRecallManyMajorityGate`,
`TestRungGenomeOneDifference`), RED confirmed by `git stash` on the three source files (10 ERRORs — every
test that depends on the clause), GREEN after:
```
Ran 30 tests in 0.03x s
OK
```
(the 27+3 genome-pin tests; log `scratch/test_answer_grade_green.log`)

The marks (`tools/verdict_life.py::answer_null_mark/answer_seen_mark`) — `tests/creature/
test_verdict_life_marks.py::AnswerNullMark/AnswerSeenMark`, RED confirmed by stashing `tools/verdict_life.py`
alone (10 ImportErrors), GREEN:
```
Ran 10 tests in 0.016s
OK
```

The sitter, both laws (`tools/self_exam.py`) — `tests/creature/test_exam_one_word.py::TestSelfExamBothLaws`
(a real Mind + a real snapshot through `creature/exam.py:run_exam`, exactly the voice thread's own call),
RED confirmed by stashing `tools/self_exam.py` alone (2 ERRORs), GREEN:
```
Ran 6 tests in 8.2s
OK
```
Re-pinned `TestExamUnchangedOnTheStandardMind`'s golden hash (an ADDITIVE-only move: every abstain dict in
`genome/questions.py` gained `"minority": 0`, even on G4-skeleton.genome which never declares the clause —
#235's own instruction). Verified additive-only exactly as builder A's own precedent: hashing `data` with
every `"minority"` key stripped reproduces the PRIOR golden `25e16cd8…` bit for bit; new golden `4598b746…`.

The four seams (`tests/creature/test_a4l_answer_seams.py`) — ask door, THINK's word work (both the inline
road and its threaded twin share ONE `recall_many`, so one test covers both), SURPRISE/THRESH (a minority
abstention never pushes the own-band — proven both empirically and by source inspection of `moment()`), and
QUESTION (proven by construction that NO consumer today can ever see `reason=="minority"` on a wordless
sight — grepped exhaustively, both "sight"-kind roads call `recall`/`episodes.nearest`, never `recall_many`).
RED confirmed by stashing the three source files (3 of 6 ERROR; the other 3 are negative controls, correctly
unaffected either way), GREEN:
```
Ran 6 tests in 2.5s
OK
```

All five of the above together, one run: **`Ran 52 tests in 12.150s` / `OK`** (`scratch/final_targeted_green.log`).

## The numbers

**Task 0 — M2 re-derived, my own instrument, `scratch/alpha4-1-snapshot` (moments=55200, sight_alive=4487,
words_alive=753):**
- seen things (16×10): `{3: 1, 4: 3, 5: 156}` — **matches the PREREG's own M2 exactly**.
- spiral: `{1: 10}` (the lit one always the coarse glance, cos 0.986–0.996) — matches exactly.
- vex: `{1: 5, 2: 2, 3: 1, 4: 1, 5: 1}` — matches exactly.
- zog (never shown yet): `{1: 9, 2: 1}` — matches exactly.
- AUC(lit_n; seen-correct 155 vs null-answered 10) = **1.0**.

**Early organism** (hour-1 fixture replayed under master+FLOOR — this replay doubles as the negative-control
reference; moments=9690, sight_alive=1534, words_alive=276):
- seen (16×10): `{1: 34, 2: 7, 3: 5, 4: 7, 5: 107}`; **A2 ceiling: 119/160 = 0.7438** (below the 0.95 bar —
  confirms A2's own per-exam-ceiling design is load-bearing, not defensive).
- spiral: `{1: 10}`; vex: `{1: 8, 2: 1, 3: 1}`.

**Negative control** (`scratch/negative_control.py`): the CURRENT (post-edit) branch code, given
`A4L-FLOOR.genome`, replays the hour-1 fixture byte-identical to the pre-edit reference INCLUDING hash:
```
post-edit FLOOR replay: 4322 mind rows vs pre-edit reference: 4322 mind rows
NEGATIVE CONTROL: PASS -- byte-identical INCLUDING hash
final hash: e266659aea2601dc6f5af62adc4d71fc8a88bd2cd3e90a9fe4adb589629f41f8
```

**Tape twin** (task 7, `scratch/tape_twin.py`): A4L-ANSWER vs FLOOR on the hour-1 fixture — **identical**,
4,322 mind rows, think_outcomes on both sides: `{"run":26,"no_cell_answers":13,"reflected":20,"no_change":18,
"filed":69,"belief":13,"not_yet_due":22}` (see "not done" §3 for why).

**Real-front controls** (`scratch/task4_controls.py`, on `scratch/alpha4-1-snapshot` under `A4L-ANSWER.genome`):
- (a) thing="circle": full 5-glance canvas → `answer`/"circle" (lit_n=5/5, sanity check). 1 located + coarse
  only (3 blanked) → **`minority`**, lit_n=2/5, grade=sure, resembles **"dot"** (the coarse glance's own
  dominant pull, consistent with the whole regression story). **PASS.**
- (b) spiral: full 5-glance → `minority` (lit_n=1/5 — under the OLD law this was "answer"/dot, sure). Coarse
  removed (4 located only) → **`novel`** (lit_n=0/4). **PASS.**
- organism hash unchanged by both controls: **CONFIRMED**.

**`tools/answer_readtwin.py`** run on `scratch/alpha4-1-snapshot` (both laws, one load, no replay) — the
headline the whole rung exists to fix:
| | new law | old law |
|---|---|---|
| spiral (Q5) | `sure_bare 0/10`, `abstain_with_resemblance 10/10` (all `minority`) | `sure_bare 10/10`, answered "dot" 10/10 |
| vex | `sure_bare 3/10`, `abstain_with_resemblance 7/10` | `sure_bare 7/10`, `unsure 3/10` |
| Q1 (seen words) | acc 0.9545, hedge 0.324 | acc 0.9545, hedge 0.324 (unchanged — mature organism clears the ceiling) |
organism hash unchanged across both passes: **CONFIRMED**.

## Gates
- `python3 -m unittest discover -s tests/genome -t .` (`nice -n 19`, `TMPDIR=scratch/tmp`):
  `Ran 378 tests in 78.689s` — **FAILED (failures=1, skipped=1, expected failures=6)** — the ONE failure is
  the pre-existing, confirmed-unrelated `test_read_lexicon_parser.py` defect (§"not done" 4); the skip is an
  unrelated, self-explanatory "NOT GRADABLE" sleep-retention test; the 6 expected-failures are pre-existing
  `@expectedFailure` markers untouched by this rung.
- `python3 -m unittest discover -s tests/creature -t .`: `Ran 735 tests in 634.885s` — **OK (skipped=1)**.
- `tools/gate_g4.py --tree . --only 1,2,3,6`: **`{'1': 'PASS', '2': 'PASS', '3': 'PASS', '6': 'PASS'}`** —
  every planted control caught (writer-sweep offender, swapped-canvas, payload-byte-flip, folder-divergence).
- `tools/gate_g5_landing.sh a4l-answer`: life 3a's tape replayed and diffed vs master — **IDENTICAL except
  `hash`**; overall script result reads FAIL solely because of the one pre-existing genome-suite failure
  above (the script ANDs both suites' exit codes with no exception for a pre-existing defect) — G4 gates,
  the creature suite and the replay-diff all individually PASS.
- `tools/pin_g1.py`: step (1) pre-existing FAIL (§"not done" 5); step (2), this rung's own K=1 pin, verified
  SAME in isolation.
- `tools/inventory.py genome/ladder/A4L-ANSWER.genome`: `ANSWER MADE genes.RUNS` — **`DECLARED-ONLY 0`**,
  `clear`.
- Genome pin (`TestRungGenomeOneDifference`): `A4L-ANSWER.genome` = `A4L-FLOOR.genome` + exactly one header
  line + the ANSWER line's new clause — nothing else, checked by `difflib`.

## Commit
Branch `a4l-answer`. Files touched: `genome/machinery.py` (the parser + `Organism.recall_many`),
`genome/questions.py` (`ask_glances`/`ask_plant_glances` widened + `majority` override), `creature/genes.py`
(the RUNS description), `tools/self_exam.py` (both-laws sitting, conditional), `tools/verdict_life.py`
(`answer_null_mark`/`answer_seen_mark`), `tools/answer_readtwin.py` (new, A3's tool),
`genome/ladder/A4L-ANSWER.genome` (new), `tests/genome/test_answer_grade.py`,
`tests/creature/test_verdict_life_marks.py`, `tests/creature/test_exam_one_word.py`,
`tests/creature/test_a4l_answer_seams.py` (new).
