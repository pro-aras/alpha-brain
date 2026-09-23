# REPORT — SIT-ATOMIC-SWEEP-0923: SIT's torn-read cursor + atomic exam writes (FIX 1); per-function scope for both writer sweeps (FIX 2)

Builder: Claude (Fable 5.1). Written 2026-09-23 17:05 +0400. Worktree `/data/dev/genome-wt-sit`, branch `sit-atomic-0923`, **branched from `a4-integration` at
`a50b0f3`**; `a4-integration` moved to `51f71ba` (the a4l-explore merge) during the build and was merged into this branch BEFORE the final gate
(`64fb283`; the merge touched none of the six files below). Source brief: `docs/briefs/SEAM5-WITNESS-SOUND-REPORT.md` items 2 and 5.

## NOT done (read this first)

- **The 10× counts (both ways) — __COUNTS_STATUS__.** They are the last stage of the final gate on the merged bytes `64fb283` (10× the SIT class alone,
  then `gate_g4 --only 1`, then the genome suite once, then the creature suite 10×, serially, `nice -n 19`, single-threaded BLAS, TMPDIR under
  `scratch/tmp`, waiting while the 1-min load > 12). The numbers are in §4; where a cell says PENDING the run had not finished when this line was written.
- **The lottery RED did not reproduce at this load.** The old bytes (`a50b0f3`) read **10/10 green** for `TestSitLiveWiring` alone at load ≈ 5
  (`scratch/sit-atomic/red-old-alone/`); the seam-5 report's 8/10 was read at load 20+. The RED for FIX 1 is therefore the DETERMINISTIC one: the new
  torn-read control run against the OLD `sit.py` (§2) — it reads `0 != 1` every time, load or no load.
- **Not touched, by the coordination note:** builder B1 (branch `a42-b1`) owns `creature/senses/sit.py`'s canvas-count line (`canvas_count = moments //
  max(1, fixations)`, old :89 → now :96) and `creature/exam.py`'s (old :108 → now :109). Both lines are byte-identical to `a50b0f3`; my hunks in
  those two files are the cursor block (`sit.py` :103–:135) and the LAST.json write (`exam.py` :112–:117) plus one `import os` line each.
- **Not changed, by design (unchanged behaviour, stated so nobody reads it as a gap):** an exam report that PARSES but carries no `ask_seen_words.Q1.acc`
  still advances both cursors without a retry (the pre-existing "a malformed report is not re-tried forever" rule); only a read that fails to parse
  (`JSONDecodeError`/`OSError`) feeds the retry counter. The counter lives in memory like the cursors (a restart starts it at 0 — harmless: the
  restart can re-read the same file at most `MAX_TORN_RETRIES` more times).
- **Not in this branch:** the seam-5 report's other items (1, 3, 4) and its leaked `scratch/tmp` roots (1.1 GB, 1,456 — none deleted, none mine).
- **`tools/gate_g4.py` had a latent `NameError`-in-waiting:** `_resolve` was annotated `-> Optional[str]` with `Optional` never imported (harmless only
  because of `from __future__ import annotations`). One import line added; noted here because it is a change outside the two functions FIX 2 names.

## 1. What was wrong (as read in the live files, not the brief's line numbers)

**FIX 1 — `creature/senses/sit.py`.** The seam-5 report says "line 110 advances the cursor even when data is None". On these bytes line 110
(`last_published_name = latest.name`) was correctly guarded by `if data is not None:`; the boundary cursor was not: `last_canvas = canvas_count`
(old :98) ran the moment a NEW filename was seen, BEFORE `json.loads`. The gate is `canvas_count - last_canvas >= every_canvases`, so one torn read
(the empty file between the voice's `write_text` create and its write; a partial write) spent the boundary with nothing published and the file
waited for the NEXT boundary — 500 canvases on, and at a life's last boundary, forever. The comment beside the `except` ("skip this poll, try again
next one") described a retry the cursor above it had made impossible. The test had the same shape: its first exam file was written with
`write_text` AFTER `t.start()`, so the sense's first poll could read it torn.

**FIX 2 — `tools/gate_g4.py` `_build_env` / `tests/creature/test_writer_sweep.py` `_build_env`.** Both built ONE flat `name -> text` map for the
whole module (`ast.walk` over every `Assign`, last write wins). A local `p` in one function therefore overwrote a same-named `p` in an unrelated
function; with the leak's binding first and an innocent binding later in BFS order, the leak resolved to the innocent text and both sweeps read `[]`
— the seam-5 builder's own near-miss (COST's planted `p = root/'state'/'witness.json'; p.write_text(...)` hidden by an unrelated local `p`).

## 2. RED → GREEN, verbatim from the logs (`scratch/sit-atomic/<tag>/run-1.log`, gitignored)

**FIX 1 RED** — the new controls against the UNMODIFIED `sit.py` (`a50b0f3`), tag `red-fix1-new-tests-old-sit`:
```
FAIL: test_a_torn_first_read_is_retried_and_the_score_published_exactly_once
AssertionError: 0 != 1 : the torn file's score must be published exactly once after its content lands: []
ERROR: test_b_a_file_unreadable_for_five_polls_is_given_up_once_and_the_next_file_still_publishes
AttributeError: module 'creature.senses.sit' has no attribute 'MAX_TORN_RETRIES'
Ran 4 tests in 11.226s
FAILED (failures=1, errors=1)
```
(the old module has no counter at all, so the give-up control errors instead of failing — the same absence, a different shape.)

**FIX 1 GREEN** — the same four tests on the fixed bytes, tag `green-fix1-alone`: `Ran 4 tests in 2.061s` / `OK` (all four `... ok`).
The two writers under `root/exam/` were exercised by their own tests, tag `green-fix1-writesites` (`tests.creature.test_exam`,
`tests.creature.test_readiness_units`, `tests.tools.test_read_recognised`): `Ran 33 tests in 21.862s` / `OK`; no `*.json.tmp` left behind in the test roots.

**FIX 2 RED** — the new planted control against the UNMODIFIED sweeps, tag `red-fix2-new-test-old-sweeps`:
```
FAIL: test_a_leak_shadowed_by_a_same_named_local_in_another_function_is_caught_by_both_sweeps
AssertionError: 0 != 1 : leak_first=True: exactly the leak, never the innocent write, under this file's walker: []
Ran 1 test in 0.076s
FAILED (failures=1)
```
(the ORDER is load-bearing: leak first, innocent binding second is the order under which the old flat env hid the leak; the mirror order made the old
env flag BOTH writes — a false positive on the clean one. The fixed sweeps read exactly ONE offender, the leak's own line — :4 or :7 — in either order.)

**FIX 2 GREEN** — every module that calls either sweep, one process, tag `green-fix2-targeted` (`tests.creature.test_writer_sweep`,
`test_read_door`, `test_evolve_sense`, `test_chat_door`, `test_life_e_think_thread`, `tests.genome.test_a4l_cost_writer_sweep`):
`Ran 93 tests in 46.446s` / `OK` — every existing plant still CAUGHT, every real module still clean, `test_read_door`'s pinned expectation
(`test_gate_g4s_own_sweep_catches_the_inline_form_but_not_the_variable_form`: both forms caught) green. The real tree:
```
G4-1 writer sweep over 20 files: 0 offenders
G4-1 control: planted offender CAUGHT
G4-1 control: the chat sense's planted offender CAUGHT
G4 gates: {'1': 'PASS'}
```

## 3. What changed (commit `fce4f1d`; six files, +286 −25)

- `creature/senses/sit.py` — `MAX_TORN_RETRIES = 5` (module level, read by the tests); `torn_name`/`torn_count` beside the two cursors; the cursor block:
  a read that fails to parse leaves BOTH cursors untouched (the next poll re-reads the SAME file); the 5th consecutive failure on the same filename
  prints `sit: gave up on <file> after 5 unreadable polls (malformed exam report; never re-read)` and advances both cursors past it, once; a read that
  parses advances both cursors together AFTER the publish (`#230`), even when the score is None (as before). No other line of the file moved.
- `tools/self_exam.py` — the report is written `tmp = p.with_name(p.name + ".tmp"); tmp.write_text(...); os.replace(tmp, p)` (creature/body.py's
  `_write_status` pattern); `import os`. `<stamp>.json.tmp` matches no reader's `*.json` glob (`sit.py`, `creature/exam.py`, `tools/verdict_g4.py`,
  `tools/lives/view.py`, `tools/lives/check.py` — every one globs `*.json` and/or keeps digit-prefixed names only).
- `creature/exam.py` — the only OTHER writer under `root/exam/` (an exhaustive grep of genome/creature/tools): `LAST.json` written the same atomic way;
  `import os`. Its one reader is this loop's own restart read (a torn read fell back to 0 and re-sat at once), so this is consistency, not a live defect.
- `tests/creature/test_g5k_outcome.py` — `_write_atomically` helper; the live-wiring test's first file lands atomically BEFORE `t.start()` (the second
  write and the live-order ledger comment of 2026-09-22 12:35 are untouched); two new controls on `TestSitLiveWiring`:
  `test_a_torn_first_read_is_retried_and_the_score_published_exactly_once` (an EMPTY file before the sense starts, 1–2 torn polls at a 0.2 s period,
  the content lands atomically, exactly one row) and `test_b_a_file_unreadable_for_five_polls_is_given_up_once_and_the_next_file_still_publishes`
  (a file that never parses: the note captured from stdout, `published == []`, the healed file with the gate re-opened still NOT published — the name
  cursor moved past it — and a NEWER file published exactly once; one note, not one per poll: the counter is 5, not infinity).
- `tools/gate_g4.py` — `_SCOPE_NODES`, `_scope_map(tree)` (node → nearest enclosing def/lambda, the Module for top-level code; a def node itself belongs
  to the scope it is written in), `_build_env(tree, scope_of)` now returns `{scope: env}`: a def's env is a COPY of its enclosing scope's finished env
  (module-level names stay visible inside functions, as at run time) plus its OWN simple assignments in SOURCE order (last write wins within a scope);
  a sibling's locals never enter it; class bodies stay transparent (a widening only). `sweep()` looks up `envs[scope_of[node]]` for each write call.
  `_resolve` unchanged; the Import check unchanged; `from typing import Optional` added (see NOT done).
- `tests/creature/test_writer_sweep.py` — the same `_scope_map`/`_build_env` line for line (with `_flatten`); `find_offenders` looks up the call's own
  scope; the new control `_shadowed_plant(leak_first)` + `test_a_leak_shadowed_by_a_same_named_local_in_another_function_is_caught_by_both_sweeps`
  (both orders; `find_offenders` must read exactly one offender; `gate_g4.sweep` must read exactly `[leak line]` — :4 leak-first, :7 leak-second —
  and name `state`).

## 4. The final gate on the merged bytes (`64fb283` = `fce4f1d` + `a4-integration@51f71ba`)

Every stage serial, one process at a time, `nice -n 19`, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, `TMPDIR=scratch/tmp`, waiting while the 1-min
load > 12 (six lives alive; the rungs close 21:42). Logs: `scratch/sit-atomic/FINAL/{alone,genome,suite}/run-N.log` + `summary.txt`, `FINAL/summary-all.txt`.

__FINAL_GATE__

## 5. Discipline notes

- The RED lines above were read from a log written on the OLD bytes BEFORE any fix was applied (each stage's tag names the bytes it ran on); the GREEN
  lines were read from logs on the fixed bytes; the counts in §4 from logs on the merged bytes. Nothing in this report is quoted from memory.
- Every `# edit:` stamp in the six files was written from `date "+%Y-%m-%d %H:%M %z"` at write time; every heredoc that carried a backtick was quoted.
- `/data/dev/genome-lives/` and `/data/dev/genome-wt-a4int` were read (the seam-5 report, the torn probe) and never written.
