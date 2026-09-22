# Builder I report — THE WEB DOOR, THE STAGES and THE READINESS JUDGE
*by Claude Sonnet 5, ALPHA4 builder I, 2026-09-23. Branch `alpha4-world`, worktree `/data/dev/genome-wt-z`.*

**For the integrator, up front: STAGE 4 cannot open in `alpha4-1` as shipped.** This is finding 1 below,
not a bug — the READINESS judge's (b) read-proxy is RAISED and fails closed by design — but its
consequence reaches past this brief: the web door's real-fetch path, `read_common`'s real renderer, and
the H×I seam it exercises all stay UNTESTED-BY-A-REAL-LIFE until (b) is resolved (my own tests prove the
mechanism with a test-only override; nothing in the shipped code can trigger it). PREREG §9's own
prediction — "the internet door: NOT open by hour 12 [Likely], open by hour 24 [Guessing]" — is false by
construction as of this commit and should be re-stated before launch, not discovered at hour 24.

## What is NOT done, and why

1. **§4(b)'s read-proxy half is RAISED — the shipped judge cannot reach STAGE 4 today.** "the mind's own
   answer rate on the last 50 shelf lines from its journaled answers" has no honest implementation from
   counters the mind already holds. FAST episodes carry what the ear TOLD the mind at a moment (`word`),
   never what the mind ANSWERED when it later saw that glance again; no per-episode "was this read
   correctly" field exists anywhere. Computing one at judge time would mean calling `org.recall_many`
   against stored episodes — a fresh computation over the organism, not a read of a counter or a journaled
   fact — which the advisor's 2026-09-23 00:34 amendment rules out in as many words: *"the judge reads
   only rows and counters the mind already holds."* `creature/mind.py:Mind._read_proxy()` always returns
   `None`; `_readiness_readings()` treats `None` as NOT held (fail-closed — the PREREG's own stance: *"a
   life that never opens the door is a FAIL of nothing, it is a reading of the bar"*). A named candidate
   for a future gene sits in the code comment above `_read_proxy`: SURPRISE's confirmed-share computed
   specifically over `source=="shelf"` episodes, buildable once builder H's reader lands and a life has run
   long enough to carry SURPRISE + shelf episodes together. `_read_proxy_override` (test-only, never set by
   production code) lets the streak/commit machinery and conditions (a)/(c)/(d)/(e) be proven independent
   of this open question; a dedicated test (`test_read_proxy_absent_by_default_blocks_stage_4_honestly`)
   proves the SHIPPED code stays fail-closed with the override absent.

2. **The unanswered-questions queue format is INVENTED, not builder H's real one.** H's lexicon door had
   not landed on this tree when this was built (a sibling worktree, `/data/dev/genome-wt-y`). I designed a
   concrete, isolated, documented contract: `$ROOT/world/questions/<id>.json = {"id","q","word"}` + a
   sidecar `$ROOT/world/questions/<id>.status.json = {"status":"answered"|"unanswered"}` (note: `$ROOT` is
   the LIFE's run root, e.g. `/data/dev/genome-lives/alpha4-1`, never this repo's own `world/` directory,
   which is the maker's picture folder for a different door). The reader is ONE function,
   `creature/senses/web.py:unanswered_questions()`, so a format change at integration is a one-function
   patch. Reconcile against H's actual format when it lands.

3. **`creature/senses/read_common.py` is a STUB**, per my own orchestrator's explicit instruction (H lands
   first). `IS_STUB = True`; every function raises `NotImplementedError`. `web.py` calls into it defensively
   — checked before the record row is published (so the row can honestly self-report `rendered: false`),
   and every individual call is separately guarded, so a PARTIAL landing (some functions real, some still
   raising) degrades exactly like a total stub, never crashes the sense thread into `SenseThread`'s restart
   loop (which would burn the door's own rate budget re-fetching the same question — SOLUTIONS #230's
   class).

4. **The I×J seam ("an epoch never crosses a stage event", PREREG §8) is untested.** Builder J's EVOLVE
   work is a separate, unmerged worktree; there is no code here to test against. This is squarely the
   integration lane's job once both land (PREREG §8 point 3 names the seam tests as the landing script's
   own responsibility, not a single builder's).

5. **`SENSE_GRADE`'s poll period (2.0 s) and `DOOR_WEB`'s idle poll period (2.0 s) are code-side
   defaults**, not gene-derived — `SENSE grade from ask/graded` carries no rate clause at all in the
   PREREG's own genome line, and DOOR web's `floor_s` (gene-derived, 2.0 s) governs the FETCH pacing, not
   the idle "nothing to do yet" poll cadence.

6. **PREREG §5's WEB mark text says "the four readings that decided it"; my brief (task 1, twice) and
   PREREG §4 itself say five, lettered (a)–(e).** I followed the more specific, more recent, internally
   consistent source (my own brief) and implemented five. Flagging the inconsistency rather than silently
   picking one.

## Findings A–D: two shared-tool gaps and two corrections, found while proving my own deliverables (not asked for, but blocking)

Every one of these four is the SAME shape (#162's class, three times in one night): a check that tested
for the SHAPE of a thing instead of the NAMED thing it actually meant — an `event` key (any of them) stood
in for "a body-only bookkeeping row"; a bare AST `Name` node stood in for "wherever this path is used"; a
raw count `>= 8` stood in for "the last 10, filled." Each was found by building the exact case the shape
and the meaning disagree on, not by inspection.

**A. `tools/gate_g4.py`'s writer sweep had a real blind spot.** Its `sweep()` built a write target's text
from `_literal_text(fn.value)` — a bare AST walk of the receiver expression — which sees an INLINE write
(`(Path(root)/'memory'/'x').write_text(...)`) but is blind to the two-step form EVERY real sense module on
this tree actually uses (`p = Path(root)/'memory'/'x'; p.write_text(...)` — folder.py, game.py, sit.py, my
own grade.py/web.py). Proven with a planted probe before touching the fix: the inline form was caught, the
two-step form read zero offenders. Fixed by porting `tests/creature/test_writer_sweep.py`'s own
`_build_env`/`_flatten` variable-resolution technique into `gate_g4.py` (`_resolve`/`_build_env`, additive
— every node shape the old code already understood falls through to the identical `_literal_text` walk).
Verified: `gate1` still reports 0 offenders over the real tree (14 files) with its own control caught; the
real sense modules re-swept clean; my own planted "web sense that writes memory" (the two-step form) is now
caught by BOTH this file's sweep and `tests/creature/test_writer_sweep.py`'s independent one
(`test_planted_web_sense_that_writes_memory_is_caught_by_both_sweeps`).

**B. `creature/replay.py` (and its own duplicate in `tools/replay_diff.py`) silently dropped MIND-level
semantic event rows from replay comparison.** Found while trying to prove "a tape carrying a stage/web row
replays identically" through the CANONICAL tool (not just my own two-Mind comparison) per the advisor's
review. The old law (G4-PREREG §2.4, written before any mind-level event existed) filtered ANY row
carrying an `"event"` key — correct for the four BODY-only bookkeeping events
(`start`/`sense_restart`/`snapshot`/`stop`, `creature/body.py`'s own `_journal_event`) and for `exam`
(`creature/exam.py`'s own separate, direct writer, found only after the FULL suite caught
`test_exam_event_row_excluded_from_mind_journal_reader` failing on my first, four-name-only fix) — but ALSO
silently dropped `"stage"` (this brief) and, by the same shape, would drop EVOLVE's future `"epoch"` event
(PREREG §6). Not live-breaking today (no genome on this tree ever declared STAGE_READY/EVOLVE before this
brief, so no existing comparison ever had one to drop), but it would have SILENTLY defeated replay
verification the moment any life actually reached stage 4 — exactly when that proof matters most, and in a
way indistinguishable from "the event never fired" (both sides of any comparison equally blind). Fixed by
naming the five NON-mind event types explicitly (`creature/replay.py:NON_MIND_EVENTS`,
grep-verified exhaustive against `creature/*.py` and `genome/*.py`) instead of testing for the bare
presence of `"event"`; `tools/replay_diff.py` had its OWN duplicate of the same filter — fixed by
importing `creature.replay.is_mind_row` instead of re-implementing it a second time, so the two cannot
drift apart again. Verified additive: `gate_g4.py`'s gate2/gate3/gate6, the FULL `tests/creature/
test_exam.py` suite, and life 3a's replay-diff (2,576 rows) all re-ran byte-identical after both fixes.

**C. `tests/creature/test_refusal.py`'s `TestRegistryPinnedToParser` fixture needed extending** — a
pre-existing, well-designed cross-check (every prior builder who added a `genes.py` RUNS entry has hit
this exact gate on their first full-suite run, per that file's own comments) — for my three new entries
(`DOOR_WEB`, `SENSE_GRADE`, `STAGE_READY`). Caught on the first full run after landing everything else;
fixed immediately.

**D. A real correctness bug the advisor caught before I called this done:** `_readiness_readings()`'s
condition (d) checked `len(self._novel_grades) >= 8`, letting as few as 8 novel grades (all right) satisfy
it before the last-10 window ever filled. PREREG §4(d) and §8 point 7 both name TEN as the denominator
("8 of the last 10"; "ten of them never-seen pictures, so the judge's (d) can ever be true"). Fixed to
`== 10` (the deque's own `maxlen=10` caps it, so `==` and `>=` agree once full — the bug was only ever
reachable BEFORE the window filled). A regression test
(`test_d_removed_novel_window_not_yet_full_blocks_even_when_all_seen_are_right`) locks it in.

## Also found, NOT fixed (out of my scope, noted for the record)

**A pre-existing, environment-load-induced flaky test, unrelated to this work:**
`tests/creature/test_g5k_outcome.py::TestSitLiveWiring::test_sense_publishes_the_newest_exam_files_score_as_they_appear`
did NOT fail in any of my three FULL-suite runs this session (the one full-suite failure I saw — 4
failures, one run — was entirely `test_refusal.py`'s registry-pinning gap, finding C below; 0 elsewhere).
It DID fail 2 of 3 times when I ran it ALONE, in isolation, while the box was under heavy concurrent load
from sibling builders' processes, e.g. `tools/evolve.py --negative-control` at 126% CPU, the live
`g5-seam-2` body, and at least two other worktrees' own full test suites running at the same time. Proven
innocent by isolation: `git stash`-ing every change on this branch and re-running the SAME test 3 times
against the completely unmodified tree still failed 3/3, with the identical `AssertionError: 0 != 1` — the
sense thread's own 5 s deadline (`tests/creature/test_g5k_outcome.py:453`, this file's own comment already
acknowledges "generous margin under this box's contended CPU") is simply not generous enough under
TODAY's specific multi-worktree load. Not touched — not my file, not caused by my changes, would need K's
(or the orchestrator's) own call on whether to widen it further.

## Tests: RED → GREEN (the interesting ones)

- **web.py's fetch/refuse/render decision** went through three real bugs caught by my OWN sanity scripts
  before the formal test suite existed: (1) a muddled `ok`/`extract`/`status` computation where a 200
  response with an empty summary was wrongly marked `"failed"`; (2) the 61-questions test initially
  produced 60 made + **518** `refused_rate` rows (not 1) because a refusal was journaled on every poll tick
  while blocked — fixed with a de-dup guard (one row per distinct (reason, candidate), not per tick); (3) a
  fake-clock sanity check that advanced simulated time on every `now()` call (not once per "tick") produced
  nonsense rate-window behaviour — replaced with a small real floor for that check, and a real fake-clock
  design (a single mutable cell the test advances explicitly) for the transient-retry-after-the-hour test.
- **`_readiness_readings()`'s condition (b)** was verified against the REAL `genome.sentence.find_frames()`
  (never a stub): a deliberately skewed synthetic episode corpus (3 target word-pairs at lift 4.2, a noise
  pool of 12 pairs each below `min_count`) produces exactly 3 qualifying rows before any test was written
  against it, confirming the judge's own lift computation is a faithful re-derivation of what THINK's own
  frame-filing already checks.
- **`tools/gate_g4.py`'s writer-sweep gap** (found A, above) — before/after: the two-step planted offender
  read `sweep([plant]) == []` (MISSED) against the unfixed sweep, `!= []` (CAUGHT) after; the real sense
  modules (folder/game/sit/hands/ear/body_sense, my own web/grade) stayed clean under BOTH the fixed sweep
  and the independent `test_writer_sweep.py` walker.
- **`creature/replay.py`'s event-filter gap** (found B) — before/after, both empirically probed: RAW
  journal carried 1 "stage" event; the OLD filter dropped it to 0; the NEW filter keeps it (1), while a
  hand-built journal mixing all five NON-mind event names alongside a "stage" event and an "epoch" event
  keeps only the latter two (`test_read_mind_journal_keeps_stage_but_drops_body_only_events`,
  `tests/tools/test_replay_diff.py`'s own mirror of the same law).
- **`tests/creature/test_refusal.py`'s registry gate** (found C) — 4 failures on the first full-suite run,
  all in `TestRegistryPinnedToParser`; 0 after adding the three sample lines.
- **The condition-(d) bug** (found D) — the advisor's review caught it before any test run; a fresh
  regression test proves the fix without moving any of the 19 pre-existing readiness-judge tests.

## The numbers

**Pre-edit baselines** (this tree, before any of my changes):
genome suite `Ran 277 tests … OK (skipped=1, expected failures=6)`; creature suite
`Ran 494 tests … OK (skipped=1)`.

**Final bytes** (every fix above applied):
- genome suite: `Ran 291 tests in 70.351s` / `OK (skipped=1, expected failures=6)` — same
  skip/expected-failure counts as baseline, +14 new (`tests/genome/test_parse_alpha4_stage_door_grade.py`).
- creature suite: `Ran 551 tests in 526.413s` / `OK (skipped=1)` on the run immediately after the
  `test_refusal.py` fix (4 real failures → 0). The TRULY FINAL run — after the condition-(d) fix, the
  `replay.py`/`replay_diff.py` fixes, and STATUS's `web_refused_hold` — is the one that counts:
  **`Ran 553 tests in 546.844s` / `OK (skipped=1)`**, exit 0 (`scratch/truly-final-suite-creature.log`,
  this worktree). +59 tests over the 494-test baseline; the same single skip as baseline
  (unrelated — `TestSitPreregistrationOnLife2`, skipped when a closed-life fixture copy is absent).
- `tests/tools` suite (new): `Ran 16 tests in 24.706s` / `OK`.
- `tools/gate_g4.py --only 1,2,3,6`: `{'1': 'PASS', '2': 'PASS', '3': 'PASS', '6': 'PASS'}`, re-verified
  after every subsequent fix, always green, always with every control (`CAUGHT`) firing correctly.
- `tools/inventory.py` on `scratch/alpha4-mine-only.genome` (= `genome/LIFE.genome` + my four landed
  lines — the checked-in `genome/ALPHA4.genome` draft does not parse yet: builders G/H/J's own lines are
  not landed on this tree, confirmed by running inventory on it directly: `REFUSED by the parser -
  BUDGET: cannot read '400 per arrival; regenerate 1 per 60 moments'`, builder G's clause, not mine):
  `61 rows - DECLARED-ONLY 0 - VALUE-UNREAD 3 - OFF 8 -> clear`, exit 0. The three VALUE-UNREAD rows
  (HEBB/MEET/RECALL) are pre-existing and unrelated (this file's own POSITIVE CONTROL comment names
  the same three on a comparable genome). `DOOR_WEB`, `STAGE_READY`, `SENSE_GRADE`, and `SENSE grade`
  (the sense-channel check) all read **MADE**.
- life 3a's tape (`/data/dev/genome/run-g4-life3a-20260921-1314/tape/2026-09-21.jsonl`, 2,576 mind rows)
  replayed under this tree via `creature.replay` + `tools/replay_diff.py` against a pre-edit master
  baseline generated from this same starting commit: **IDENTICAL except ['hash']: True**, re-verified after
  every subsequent change (four separate runs, all clean).

## Files touched

Parser + wiring: `genome/machinery.py` (STAGE "by READY" form + DOOR web + SENSE grade), `creature/genes.py`
(three RUNS entries), `creature/body.py` (arming + STATUS), `creature/mind.py` (the judge, the three new
consumers, snapshot/resume persistence), `genome/ALPHA4.genome` (added the missing `SENSE grade` line).
New sense modules: `creature/senses/web.py`, `creature/senses/grade.py`, `creature/senses/read_common.py`
(stub). Extended: `creature/senses/sit.py` (`composite`, additive, dogfooded against the same fixture
`tests/creature/test_g5k_outcome.py` already uses). Verdict: `tools/verdict_life.py` (`web_mark`,
`stage_mark`), `tools/verdict_g4.py` (wired `M["WEB"]`/`M["STAGE"]` in — the SAME call pattern every other
builder's mark already uses there; without this they would have been DECLARED-ONLY in the sense #180
exists to catch). Shared-tool fixes: `tools/gate_g4.py`, `creature/replay.py`, `tools/replay_diff.py`.
Tests: `tests/creature/test_readiness_judge.py`, `test_grade_door.py`, `test_web_door.py`,
`test_web_and_grade_arming.py` (new); `tests/genome/test_parse_alpha4_stage_door_grade.py` (new);
`tests/tools/test_replay_diff.py` (new); `tests/creature/test_verdict_life_marks.py`,
`test_writer_sweep.py`, `test_refusal.py` (extended).

## Gate status (final)

- Both suites green on the final bytes: genome `Ran 291 … OK`, creature `Ran 553 tests in 546.844s … OK
  (skipped=1)` — exit 0, the SAME single pre-existing, unrelated skip as baseline
  (`TestSitPreregistrationOnLife2`, a closed-life fixture not present on this box).
- `tools/gate_g4.py` 1/2/3/6: green, including a planted "web sense that writes memory" offender caught
  by both independent sweeps (see finding A).
- `tools/inventory.py`: `DOOR_WEB`/`STAGE_READY`/`SENSE_GRADE`/`SENSE grade` all MADE, 0 DECLARED-ONLY.
- Life 3a's tape: replays identical minus hash, four independent runs across this session.

## Commit

Code commit: **0157b94** (branch `alpha4-world`, worktree `/data/dev/genome-wt-z`) — "ALPHA4 builder I: THE
WEB DOOR, THE STAGES and THE READINESS JUDGE", 23 files changed. This report is committed separately,
immediately after, citing this sha.
