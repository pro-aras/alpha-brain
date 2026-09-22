# Builder A (Sonnet 5) — REPORT: THE SELF (docs/briefs/LIFE-A-ANSWER-SELF.md)
*edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:18 +0400. Branch `life-answer-self` off `g5-integration` aed56d5, worktree `/data/dev/genome-wt-r`. Nothing here touched `/data/dev/genome`, `/data/dev/genome-lives`, `world/`, or systemd.*

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
| `_think_work` "self" branch | `creature/mind.py:884-908` | the comparison + `believe()` call |
| `_self_trigger` | `creature/mind.py:919-933` | the three triggers, in the plan's own order |
| `_maybe_think` backlog skip | `creature/mind.py:983-993` | reads `_last_body_reading`, never the live queue |
| `questions.py` `_grade_bucket`/`_new_graded_counts` | `genome/questions.py:51-59`, applied in `ask`, `ask_glances`, `ask_plant`, `ask_plant_glances` | Q1's `hedge_rate`, Q5/plant's `graded` counts |
| `body_sense.py` field map | `creature/senses/body_sense.py:25-32` | `"backlog"→mind_backlog_rows`, `"refused_nmax"→births_refused_nmax` |
| `genome/LIFE.genome:22` | extended | `SENSE body …` gains `refused_nmax` (needed by SELF's «no room» trigger; not literally in the brief's "+ backlog" sentence — see §3 clause 5) |

## 1 · Tests, RED → GREEN

- `tests/genome/test_thresh_own_band.py` (16 tests): RED — `GenomeError: unknown gene 'THRESH'` (every test, before the parser branch existed) → GREEN after machinery.py's THRESH branch + Area fields + push + `own_floor` + hash/save/load landed.
- `tests/genome/test_answer_grade.py` (12 tests): RED — `KeyError: 'grade'` / `KeyError: 'resembles_cell'` (6 errors) → GREEN after `_attach_grade` + the 10 return-site edits.
- `tests/creature/test_ask_answer_grade.py` (10 tests): written once `render_what_is`/`why` existed (not strict RED-first for the rendering — the underlying grade mechanism WAS red-green'd above; said plainly, not silently).
- `tests/creature/test_self_gene.py` (16 tests): RED — `AssertionError: 0 != 1` (`test_births_stalled_while_moments_moved_files_a_self_belief`, beliefs count) → GREEN after `_consume_body`/`_think_pool`/`_think_work`/`_self_trigger`/`_maybe_think` landed. Two of my own first-draft tests (`refused_nmax`/`backlog_crossing`) failed for a TEST reason (my fixture also triggered the stall condition) and were fixed, not the code.
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
Per-thing grade distribution (real history) — circle 10/0, square 5/5, triangle 7/3, cross 4/6, ring 9/1, bar 3/7, dot 0/10, star 4/6, arrow 10/0, wave 5/5, diamond 6/4 (sure/unsure). **Seen-words hedge rate: 0.426** — the plan's own prediction was "< 10 %"; the measured rate is 4× that. Reported as a finding (§3 clause 9), not corrected — the brief names no bar on this number, only "printed."

## 3 · Every clause raised, verbatim reasons

1. **`_nearest_in` not imported** — `genome/think.py` imports `machinery.Organism`; the reverse import would be circular. The SAME algorithm (raw-cosine argmax over the query's `_lit`-computed cosine array) is inlined in `recall`/`recall_many`'s "novel" branches instead.
2. **A THIRD additive field, `resembles_cell`** — the brief says "two NEW fields" but also promises `lit` stays whatever it already was for `reason:novel` (None) while separately demanding a reference cell for grading that case. Resolved by NOT touching `lit` and adding `resembles_cell` (the grading reference: `lit` itself when non-None, else the nearest-alive-cell for novel). Documented at `machinery.py:928-941`'s docstring.
3. **Grading is `side=="sight"` only** — `words` side always reads `(grade, own_floor, resembles_cell)==(None,None,None)`. THRESH's own band tracks sight cells; the brief's own toy/mark are entirely about the what-is (picture→word) road. Not raised as a blocker — a deliberate, documented scope choice within the letter of the brief ("Each SIGHT cell keeps…").
4. **`why`'s "episodes" is always `[]`** — `creature/ask.py:load_snapshot()` never loads `episodes.npz` (only the Organism + ledgers). `questions.why()` already documents `episodes=None` as a valid, honest call. Wiring the episode store into the ask door's snapshot loader is outside this task's four numbered items; raised, not built.
5. **`refused_nmax` added to `SENSE body`'s field list** — the brief's clause 3 needs `births_refused_nmax` for the «I have no room» trigger, but its own literal instruction only names "+ backlog". STATUS already carries `births_refused_nmax` (landed pre-existing); `body_sense.py`'s STATUS_FIELD_MAP is a pure lookup table designed for exactly this extension. Added and documented as a DRAFT-line extension in `LIFE.genome:22`, not silently.
6. **MAJOR FINDING — `self:behind` is unreachable by construction in the live pipeline.** SELF's backlog TRIGGER and its backlog SKIP read the SAME field (`_last_body_reading["backlog"]`) against the SAME threshold. The first THINK boundary that could ever see a pair whose SECOND reading has crossed the threshold is ALSO the first boundary where `_maybe_think`'s skip check reads that exact (now-crossed) reading — so the skip preempts the self item before it is ever chosen, every time, and the belief can never actually be filed by the live pipeline. Proven by two tests: `_self_trigger` alone correctly reads a crossing (`test_self_trigger_formula_recognises_a_backlog_crossing`); the full pipeline over the same two readings files NOTHING, because that boundary was a skip (`test_backlog_crossing_is_preempted_by_its_own_skip_a_raised_finding`). Implemented exactly as the brief specifies — the skip law and the trigger law are each built to their own letter — never silently redesigned to "fix" the interaction. Left for Ahmad/Fable's call: decouple the two threshold-reads (e.g. run the self-comparison before the skip decision) if `self:behind` should ever actually fire.
7. **`LIFE.genome` does not parse whole** — confirmed directly: it refuses at `GAZE … coarse 32` (Builder B's L-7 clause, not landed). My four lines were verified (a) individually against `G4-skeleton.genome`/mini-genome bases (the whole test suite above), and (b) together, end-to-end, against a full WORKING genome: `G5.genome` + my SENSE-body/ASK/THRESH/ANSWER/SELF/THINK/BELIEF edits parses clean, `Organism(g)` builds, `creature.genes.unwired(g.declared) == []`. The pre-flight re-checks `LIFE.genome` itself against the landed parser once every builder's lines are in — not this report's job.
8. **`RECALL k=3` removal (L-14's other clause) — not done.** "RECALL k reached no call site, removed" is L-14 but not one of my four numbered tasks; `recall_k` stays in `parse_genome`'s `required` list. Untouched, named here so it is not silently assumed done.
9. **Seen-words hedge rate on real L1 data: 42.6 %**, far above the plan's "< 10 %" prediction (§2 above) — printed per the brief ("no bar"), flagged as a finding since it is a real surprise, not silently absorbed.
10. **`genome/sleep.py` replays episodes through `moment()`** — SLEEP's replay therefore also pushes own-band entries (the exact same "plain resonance road", no special-casing needed, no extra code) — noted, not a defect.
11. **`_last_body_reading`/`_body_pair`/`_self_worked_seq` are not in `Organism`/`Mind` snapshot state** — a resumed mind starts these fresh (same pre-existing gap `_filed_predictions`/Park/Interests already have, per existing code comments). Named, not fixed (out of this task's scope).

## 4 · Suites, on the final bytes

```
$ export TMPDIR=$PWD/scratch/tmp
$ python3 -m unittest discover -s tests/genome -t .   > scratch/suite-genome-final.log
Ran 249 tests in 64.011s
OK (skipped=1, expected failures=6)

$ python3 -m unittest discover -s tests/creature -t . > scratch/suite-creature-final.log
Ran 286 tests in 311.229s
OK (skipped=1)
```
Both logs kept under `scratch/`. Zero failures, zero errors, on the final committed bytes.

## 5 · `date` stamps used in edit comments
`2026-09-22 18:47`, `18:5x`, `19:1x`–`19:5x`, `20:0x`–`20:3x`, `21:0x`–`21:5x` +0400 (each read from `date "+%Y-%m-%d %H:%M %z"` at write time, never typed from memory — spot-checked against the box's clock at 19:18).
