# Builder A (Sonnet 5) — REPORT: THE SELF (docs/briefs/LIFE-A-ANSWER-SELF.md)
*edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:48 +0400, final (first written 19:18, revised after the coordinator's two follow-ups — the behind-belief fix and the stamp-drift correction, §3 clause 6 and §5 — then once more after the third, final suite run). Branch `life-answer-self` off `g5-integration` aed56d5, worktree `/data/dev/genome-wt-r`. Nothing here touched `/data/dev/genome`, `/data/dev/genome-lives`, `world/`, or systemd.*

## 0 · What landed, file:line

| clause | file:line | what it is |
|---|---|---|
| THRESH parser | `genome/machinery.py:411` | `THRESH cell own band history <n>` → `declared["THRESH"]={"history":n}` |
| ANSWER parser | `genome/machinery.py:415` | `ANSWER resembles under own-band; unknown below <f>` → `declared["ANSWER"]={"unknown_below":f}` |
| SELF parser | `genome/machinery.py:423` | `SELF from body; beliefs about itself; skip thinks when backlog > <n>` → `declared["SELF"]={"backlog_threshold":n}` |
| ASK parser generalised | `genome/machinery.py:331-339` | literal six-verb line → any space-separated subset of the six known verbs (L-14) |
| Area.own_band / own_band_n | `genome/machinery.py:558-559` | allocated on `sight` only, only when THRESH declared (`Organism.__init__`, `machinery.py:626-630`) |
| the push | `genome/machinery.py:714-730` | inside `Organism.moment`, BEFORE the wire block (the pre-this-moment established answer) |
| `_own_band_push` / `own_floor` | `genome/machinery.py:786-812` | the ring write; p5-or-θ_N read |
| `_attach_grade` | `genome/machinery.py:928-941` | one shared helper, called at all 5 `recall()` return sites and all 5 `recall_many()` sites |
| `state_hash()` gating | `genome/machinery.py:1170-1189` | own_band bytes included only once `own_band_n.any()` — see §2 |
| `save()`/`load()` | `genome/machinery.py:1105-1117, 1124-1135` | own-band round-trip; an old npz without the keys loads clean |
| genes.py registry | `creature/genes.py:55-56` (THRESH/ANSWER), `:125` (SELF) | `unwired()` now accepts genomes declaring these three |
| `render_what_is` | `creature/ask.py:60-82` | the graded sentence, split out of `answer()` for testability |
| `why` wired | `creature/ask.py:111-114` | renders `questions.why()`'s `{cells, episodes, edges}` |
| `_args_for` gains `why` | `creature/ask.py:137-138` | |
| SELF tracking fields | `creature/mind.py:215-236` | `_body_pair` (:233), `_last_body_reading`, `_self_worked_seq`, `think_skipped_for_backlog` in `think_counters` (:221) |
| `_consume_body` | `creature/mind.py:345-372` | records the (seq, reading) pair |
| `_think_pool` self item | `creature/mind.py:727` | kind-fair with word/sight/due/rule/outcome |
| `_think_work` "self" branch | `creature/mind.py:884-908` | the comparison + `believe()` call (stall, no_room only — see §3 clause 6) |
| `_self_trigger` | `creature/mind.py:933-940` | the TWO comparison triggers (stall, no_room) |
| `_file_behind_belief` | `creature/mind.py:943-964` | **the coordinator's fix**: "I am behind" filed on RESUME, not on a comparison — see §3 clause 6 |
| `_maybe_think` backlog skip + resume | `creature/mind.py:1016-1039` | skip reads `_last_body_reading`; resume (`_skip_run_skips>0`) files the belief; both never the live queue |
| `questions.py` `_grade_bucket`/`_new_graded_counts` | `genome/questions.py:51-59`, applied in `ask`, `ask_glances`, `ask_plant`, `ask_plant_glances` | Q1's `hedge_rate`, Q5/plant's `graded` counts |
| `body_sense.py` field map | `creature/senses/body_sense.py:25-32` | `"backlog"→mind_backlog_rows`, `"refused_nmax"→births_refused_nmax` |
| `genome/LIFE.genome:22` | extended | `SENSE body …` gains `refused_nmax` (needed by SELF's «no room» trigger; not literally in the brief's "+ backlog" sentence — see §3 clause 5) |

## 1 · Tests, RED → GREEN

- `tests/genome/test_thresh_own_band.py` (16 tests): RED — `GenomeError: unknown gene 'THRESH'` (every test, before the parser branch existed) → GREEN after machinery.py's THRESH branch + Area fields + push + `own_floor` + hash/save/load landed.
- `tests/genome/test_answer_grade.py` (12 tests): RED — `KeyError: 'grade'` / `KeyError: 'resembles_cell'` (6 errors) → GREEN after `_attach_grade` + the 10 return-site edits.
- `tests/creature/test_ask_answer_grade.py` (10 tests): written once `render_what_is`/`why` existed (not strict RED-first for the rendering — the underlying grade mechanism WAS red-green'd above; said plainly, not silently).
- `tests/creature/test_self_gene.py` (19 tests): RED — `AssertionError: 0 != 1` (`test_births_stalled_while_moments_moved_files_a_self_belief`, beliefs count) → GREEN after `_consume_body`/`_think_pool`/`_think_work`/`_self_trigger`/`_maybe_think` landed. Two of my own first-draft tests (`refused_nmax`/`backlog_crossing`) failed for a TEST reason (my fixture also triggered the stall condition) and were fixed, not the code.
- **`TestBehindBeliefOnResume` (4 tests, the coordinator's fix — §3 clause 6):** written test-first, RED against the pre-fix code —
  ```
  FAIL: test_three_skipped_rows_then_one_resume_files_exactly_one_behind_belief
    AssertionError: 0 != 1   (len(rows) == 0 -- no belief filed)
  FAIL: test_run_state_resets_after_filing_a_second_run_files_a_second_belief
    AssertionError: Lists differ: [] != ['self:behind', 'self:behind']
  FAIL: test_replay_of_the_skip_then_resume_tape_is_byte_identical
    AssertionError: 0 != 1   (len(b1) == 0)
  ```
  → GREEN (4/4) after `_file_behind_belief` + the `_maybe_think` resume branch landed (`test_no_backlog_files_none` was GREEN from the start — the null case needed no new code).
- `tests/creature/test_gene_values.py::TestAskVerbGating::test_a_declared_verb_with_no_interpreter_is_refused_by_name`: broke on landing (its premise — "`why` has no interpreter" — is exactly what this task changes); fixed to test `next` (still unwired) and moved `why` to the implemented-verb control group, with the CORRECT control (why answers cleanly on empty ledgers, per its own documented graceful shape — it does not raise like `show` does).
- `tests/genome/test_parse_g4.py::test_each_new_gene_missing_number_or_malformed_is_refused` (gene='ASK'): broke on landing — its "malformed" fixture (`"what-is show is which next"`, missing `why`) is now VALID syntax under L-14's generalised grammar (a subset is fine). Fixed to a genuinely unknown verb (`"what-is bogus"`).
- `tests/creature/test_exam_one_word.py::TestExamUnchangedOnTheStandardMind`: its golden hash moved because `ask_glances` gained two ADDITIVE keys (`hedge_rate`, `graded`); verified the move is additive-only (stripping the two new keys reproduces the prior golden exactly) and re-pinned with that proof in the comment.
- `tests/creature/test_self_gene.py::TestBodySenseFieldMap` (2 tests): GREEN on first run (body_sense.py's map is a pure lookup dict addition).

## 2 · The toy — both halves, on real L1 data (never a live root)

Hard-link copy verified same-inode (`stat` before use), never under `2>&1 /dev/null`: `scratch/thresh-toy/snapshot-old` ← `/data/dev/genome-lives/g5-ladder-L1/state` (`cp -al`, same filesystem `/data`). Toy script: `scratch/thresh_answer_toy.py`.

**Half A — the SNAPSHOT, history empty.** `own_band` allocated, `own_band_n[0]==0`; `own_floor(0) == θ_N (0.952)`. **Q1 on seen words WITH and WITHOUT the two lines: 108/110 both ways, per-thing table byte-equal** — the cell is unchanged, on the real closed record. Grade distribution with empty history: every hit is "sure" (own_floor==θ_N, so any resonance passes) — vex sure_bare 7/10 (the un-fixed baseline; this is WHY half B matters).

**Half B — history BUILT by replaying L1's full tape (both day files, 16,653 rows) through a fresh Mind on L1.genome + the two new lines**, in a temp root under `scratch/thresh-toy/`. `org.t=36908`; 1,514 sight cells born; **679/1,514 got ≥1 own-band push**.

```
vex (the null): graded={'sure_bare': 0, 'unsure': 7, 'abstain_with_resemblance': 3, 'abstain': 0}  n=10
BAR: vex sure_bare <= 1/10: True (0/10); unsure+abstain >= 8/10: True (10/10)      -- PASSES at p5, no p10/p0 table needed
```
Per-thing grade distribution (real history) — circle 10/0, square 5/5, triangle 7/3, cross 4/6, ring 9/1, bar 3/7, dot 0/10, star 4/6, arrow 10/0, wave 5/5, diamond 6/4 (sure/unsure). **Seen-words hedge rate: 0.426** — the plan's own prediction was "< 10 %"; the measured rate is 4× that. **FINDING, reported as a finding and NOT tuned (the coordinator's instruction — this number is not a bar, the mechanism is what belongs in the register):** the own-band holds the cosines of glances the cell answered CORRECTLY during the LIVE tape — real, in-life renders with the life's own jitter, many of them near-repeats of the SAME rendering that lit that cell many times, so a cell's history skews tight and high (its p5 floor sits close to 1.0). The exam's Q1 queries HELD-OUT canvases (seed 2), a disjoint draw the own-band never saw a single cosine from. A held-out render's cosine to the same cell is a genuinely different sample and typically reads a little lower than the seen-history's own p5 — not because the answer is less correct, but because own_floor is calibrated on the TRAIN distribution and applied to the TEST distribution. The hedge rate is therefore mostly measuring that gap, not genuine uncertainty about the answer.

## 3 · Every clause raised, verbatim reasons

1. **`_nearest_in` not imported** — `genome/think.py` imports `machinery.Organism`; the reverse import would be circular. The SAME algorithm (raw-cosine argmax over the query's `_lit`-computed cosine array) is inlined in `recall`/`recall_many`'s "novel" branches instead.
2. **A THIRD additive field, `resembles_cell`** — the brief says "two NEW fields" but also promises `lit` stays whatever it already was for `reason:novel` (None) while separately demanding a reference cell for grading that case. Resolved by NOT touching `lit` and adding `resembles_cell` (the grading reference: `lit` itself when non-None, else the nearest-alive-cell for novel). Documented at `machinery.py:928-941`'s docstring.
3. **Grading is `side=="sight"` only** — `words` side always reads `(grade, own_floor, resembles_cell)==(None,None,None)`. THRESH's own band tracks sight cells; the brief's own toy/mark are entirely about the what-is (picture→word) road. Not raised as a blocker — a deliberate, documented scope choice within the letter of the brief ("Each SIGHT cell keeps…").
4. **`why`'s "episodes" is always `[]`** — `creature/ask.py:load_snapshot()` never loads `episodes.npz` (only the Organism + ledgers). `questions.why()` already documents `episodes=None` as a valid, honest call. Wiring the episode store into the ask door's snapshot loader is outside this task's four numbered items; raised, not built.
5. **`refused_nmax` added to `SENSE body`'s field list** — the brief's clause 3 needs `births_refused_nmax` for the «I have no room» trigger, but its own literal instruction only names "+ backlog". STATUS already carries `births_refused_nmax` (landed pre-existing); `body_sense.py`'s STATUS_FIELD_MAP is a pure lookup table designed for exactly this extension. Added and documented as a DRAFT-line extension in `LIFE.genome:22`, not silently.
6. **FINDING, then FIXED (the coordinator's instruction) — `self:behind` was unreachable by construction in the live pipeline.** SELF's original backlog TRIGGER (a comparison inside `_self_trigger`, worked as a "self" pool item like the other two) and its backlog SKIP both read the SAME field (`_last_body_reading["backlog"]`) against the SAME threshold. The first THINK boundary that could ever see a pair whose SECOND reading has crossed the threshold was ALSO the first boundary where `_maybe_think`'s skip check read that exact (now-crossed) reading — so the skip preempted the self item before it was ever chosen, every time, and the belief could never actually be filed. Proven before the fix: `_self_trigger` alone correctly read a crossing, but the full pipeline over the same two readings filed nothing, because that boundary was a skip, not a think.
   **The fix (a rule, not a threshold change, per the coordinator's instruction):** "I am behind" is no longer a comparison. `_maybe_think` now tracks a RUN of consecutive skips (`_skip_run_seqs`/`_skip_run_skips`/`_skip_run_max_backlog`, `creature/mind.py:236-246`) — every skip appends the body row it read; the FIRST think that actually RUNS after the run (backlog back at or under the threshold) calls `_file_behind_belief()` (`creature/mind.py:943-964`), which files ONE `"self:behind"` belief (`cells=[]`, `episodes` = the DISTINCT seqs of the body rows the skips read — never the resuming, now-under-threshold row) and writes a human-readable `"note"` into that boundary's journal row: `"I was behind: max backlog N rows over K skipped thinks, from seq A to seq B"`. The skip itself is byte-for-byte unchanged (still protects liveness); the stall/no_room triggers are byte-for-byte unchanged (`_self_trigger` now carries only those two). Replay is identical by construction — the run state, like the skip and the pair it compares, is built purely from RECORDED body rows in tape order, never the live queue.
   **Test-first, RED confirmed before the fix** (§1's `TestBehindBeliefOnResume` block) **→ GREEN after the fix, 4/4.** A synthetic tape (three body rows at backlog 300, each skipped and counted; a fourth at backlog 0) files exactly one belief citing the three seqs; two separate runs each file their own belief (no cross-run leakage); a tape with no backlog files none; replay of the skip-then-resume tape is byte-identical.
7. **`LIFE.genome` does not parse whole** — confirmed directly: it refuses at `GAZE … coarse 32` (Builder B's L-7 clause, not landed). My four lines were verified (a) individually against `G4-skeleton.genome`/mini-genome bases (the whole test suite above), and (b) together, end-to-end, against a full WORKING genome: `G5.genome` + my SENSE-body/ASK/THRESH/ANSWER/SELF/THINK/BELIEF edits parses clean, `Organism(g)` builds, `creature.genes.unwired(g.declared) == []`. The pre-flight re-checks `LIFE.genome` itself against the landed parser once every builder's lines are in — not this report's job.
8. **`RECALL k=3` removal (L-14's other clause) — not done.** "RECALL k reached no call site, removed" is L-14 but not one of my four numbered tasks; `recall_k` stays in `parse_genome`'s `required` list. Untouched, named here so it is not silently assumed done.
9. **Seen-words hedge rate on real L1 data: 42.6 %**, far above the plan's "< 10 %" prediction — printed as a FINDING, not tuned (the coordinator's instruction: this is not a bar). The one-sentence mechanism (full statement in §2): own_floor is calibrated on the SEEN (training) distribution of cosines, which skews tight and high; the exam grades HELD-OUT renders, a disjoint draw whose cosines to the same cell read a little lower — the hedge rate is mostly measuring that train/test gap, not genuine uncertainty.
10. **`genome/sleep.py` replays episodes through `moment()`** — SLEEP's replay therefore also pushes own-band entries (the exact same "plain resonance road", no special-casing needed, no extra code) — noted, not a defect.
11. **`_last_body_reading`/`_body_pair`/`_self_worked_seq` are not in `Organism`/`Mind` snapshot state** — a resumed mind starts these fresh (same pre-existing gap `_filed_predictions`/Park/Interests already have, per existing code comments). Named, not fixed (out of this task's scope).

## 4 · Suites, on the final bytes (after the coordinator's two fixes: the behind belief, and the stamp correction)

```
$ export TMPDIR=$PWD/scratch/tmp
$ python3 -m unittest discover -s tests/genome -t .   > scratch/suite-genome-final3.log
Ran 249 tests in 64.445s
OK (skipped=1, expected failures=6)

$ python3 -m unittest discover -s tests/creature -t . > scratch/suite-creature-final3.log
Ran 289 tests in 310.463s
OK (skipped=1)
```
Run a THIRD time (`…-final3.log`) after the stamp-drift correction (§5) and the un-corruption of three lines that were never mine to touch (§5's addendum) — comment-only changes, confirmed behaviourally identical to the `…-final2.log` pass (also 249/289, both OK). 289 = 286 (the pre-fix commit) + the 4 new `TestBehindBeliefOnResume` tests − 1 net (`test_self_trigger_formula_recognises_a_backlog_crossing` and `test_backlog_crossing_is_preempted_by_its_own_skip_a_raised_finding` removed, `test_self_trigger_no_longer_handles_backlog` added). All logs kept under `scratch/`. Zero failures, zero errors, on the final committed bytes.

## 5 · `date` stamps — DRIFTED, then corrected (SOLUTIONS #50, caught by the coordinator)
The first commit's stamps were TYPED, incrementing a guessed clock through the session (18:47 → 18:5x → 19:1x → … → 21:5x) rather than read from `date` at each edit — by the end they were **~2 h 31 min ahead of the box's real clock** (guessed "21:5x" against the box's actual 19:2x). Caught by the coordinator, not by me. Fixed by reading each touched file's OWN mtime (`stat -c %y <file>`, captured 2026-09-22 19:27 +0400, right before the correction — never by arithmetic on the wrong stamps) and setting every stamp in that file to that one value:

| file | WRONG stamp(s) it carried | CORRECTED to (the file's own mtime) | drift |
|---|---|---|---|
| `genome/machinery.py` | 18:5x, 19:1x, 19:2x | **18:43** | ≈ 15–47 min ahead |
| `creature/genes.py` | 19:3x, 20:0x | **18:43** | ≈ 47 min – 1 h 17 min ahead |
| `tests/genome/test_answer_grade.py` | 19:1x | **18:42** | ≈ 18–28 min ahead |
| `tests/genome/test_thresh_own_band.py` | 18:47 | **18:36** | ≈ 11 min ahead |
| `creature/ask.py` | 19:5x | **18:45** | ≈ 65–74 min ahead |
| `tests/creature/test_ask_answer_grade.py` | 20:1x | **18:46** | ≈ 1 h 14 min – 1 h 24 min ahead |
| `tests/creature/test_refusal.py` | 19:3x | **18:43** | ≈ 47–57 min ahead |
| `genome/questions.py` | 20:2x | **18:47** | ≈ 1 h 33 min – 1 h 43 min ahead |
| `tests/creature/test_exam_one_word.py` | 20:3x | **18:48** | ≈ 1 h 42 min – 1 h 52 min ahead |
| `creature/senses/body_sense.py` | 21:0x | **19:00** | ≈ 2 h – 2 h 9 min ahead |
| `tests/genome/test_parse_g4.py` | 21:4x | **19:02** | ≈ 2 h 38 min – 2 h 48 min ahead |
| `tests/creature/test_gene_values.py` | 21:5x | **19:10** | ≈ 2 h 40 min – 2 h 50 min ahead |
| `creature/mind.py` | 21:1x (pre-fix stamps) | **19:25** | ≈ 1 h 45 min – 1 h 55 min ahead |
| `tests/creature/test_self_gene.py` | 21:3x | **19:24** | ≈ 1 h 56 min – 2 h 6 min ahead |
| `genome/LIFE.genome` | n/a — this file's "DRAFT (builder A)" comments carry no `date` stamp at all (the genome-line convention, unlike the `# edit: Claude …` code convention) | n/a | — |

All corrections applied by one script reading each file's `stat -c %y` and rewriting every "LIFE builder A" stamp in that file to that single value — no per-line reconstruction, no arithmetic. Every stamp `creature/mind.py` and `tests/creature/test_self_gene.py` gained during the coordinator's SECOND instruction (the «I am behind» fix, §3 clause 6) was corrected the same way, against each file's own final mtime.

**A near-miss caught by re-scanning, not trusted on the first pass:** the correction script's regex matched ANY `2026-09-22 HH:MM +0400` text, not text scoped to "LIFE builder A" lines — it silently overwrote THREE lines that were never mine to touch: `genome/LIFE.genome`'s own file-header stamp (Claude (Fable 5.1)'s "18:2x"), and two of Claude (Fable 5.1)'s pre-existing comments in `genome/questions.py` ("10:3x", the Q3/Q4-distractor note, appearing twice) and `tests/creature/test_exam_one_word.py` (its own file-header stamp "10:26" and a docstring's factual timestamp "10:27", both Fable's). Caught by re-scanning every file's diff for a changed `2026-09-22 …` line NOT containing "LIFE builder A" — found all three, reverted them to their original text with `sed`, byte for byte, then re-scanned and confirmed clean. **Applies whenever a scripted find/replace is used to fix an attribution line: scope the match to the OWN author's lines, and verify by re-diffing for anything outside that scope, not just by checking the intended lines landed.**
