# A42-B1 — WIP (session closing; not done — see NEXT STEP)

**Status at 2026-09-23 16:36 +0400: orientation/research complete for all 8 task items; ZERO code and ZERO
tests written yet.** No RED test has been run. Nothing is committed except this report. The session was
cut short by Ahmad's word before implementation began — this file is the hand-off so a fresh session does
not repeat the investigation below. Branch `a42-b1`, worktree `/data/dev/genome-wt-b1`, off `a4-integration`
(a50b0f3). House rules (test-first, RAISE what cannot be built, nice -n 19 / BLAS threads 1, `date` for every
stamp, nothing under `/data/dev/genome-lives/`) still apply to whoever continues this.

## NEXT STEP, in order
1. M3 (creature/mind.py `_coarse_row`) — plan below is solid; first unresolved question: confirm the exact
   hour-1 fixture directory and `genome/ladder/A4L-FLOOR.genome`'s real path (not yet located — search
   `/data/dev/a4-ladder/fixtures/` and `docs/A4-LADDER-PREREG.md` for "FLOOR").
2. M4 (creature/exam.py + creature/senses/sit.py) — plan below is solid; find/create the test file
   (`tests/creature/test_exam.py` / `test_sit.py` — existence not yet checked).
3. M5 (creature/think_thread.py + creature/mind.py + creature/body.py STATUS) — plan below is solid and
   grounded in the codebase's own no-clock law; find the STATUS-field test pattern (grep `think_ms_median`
   under `tests/`) before writing M5's RED test.
4. tools/lives/check.py SIZING-under-GROW fix — plan below is solid; read `tests/creature/test_lives_check.py`
   in full (only located, not read) before writing tests.
5. tools/lives/check.py by-hour coarse-row `when` fix — plan below is solid; same test file.
6. tools/inventory.py `<BASE>_<X>` fix — NOT INVESTIGATED. Read `tools/inventory.py` and
   `docs/briefs/A4L-EXPLORE-REPORT.md` §0 item 10 (a) first (path:
   `/data/dev/genome-wt-a4l-explore/docs/briefs/A4L-EXPLORE-REPORT.md`, or the same file already copied into
   this worktree at `docs/briefs/A4L-EXPLORE-REPORT.md` if present — check).
7. `explore_lock_mark` wired into the reader's conjunction — NOT INVESTIGATED. Read `tools/verdict_life.py`
   (X1/X2 marks already exist per ALPHA4-2-PREREG §5.4 — `explore_lock_mark`/`explore_success_mark`) and
   `tools/verdict_g4.py` (or wherever "the reader's conjunction" — the all-marks-pass gate — lives) plus
   `docs/briefs/A4L-EXPLORE-REPORT.md` §0 item 9 (a).
8. tools/pin_g1.py step (1) re-pin — NOT INVESTIGATED. Read `tools/pin_g1.py` and
   `docs/briefs/A4L-ANSWER-REPORT.md` "not-done 5"; confirm commit `85bf792` (`git show 85bf792 --stat`) is
   the GROW hash-law commit before citing it in the pin comment.

After all 8: RED→GREEN tests from log files, both suites green (`-t .`, TMPDIR under scratch),
`gate_g4 --only 1,2,3,6`, `tools/gate_g5_landing.sh a42-b1`, then rewrite this report as the real
deliverable (this WIP text replaced, not appended-to) before commit.

---

## Findings (verified by reading the live code — safe to build on directly)

### M3 — one hash per canvas
Two calls to `Organism.row_hash()` happen per worded/sight-only canvas in `creature/mind.py`'s
`_consume_eye` (def at :1554): once building the canvas's own journal dict (branch "word/x_snd present" —
the dict is `journal_row`, its `"hash"` key at what is currently :1769; branch "sight-only + FAST" — an
inline dict at current :1847), and again inside `_coarse_row` (def :1867, its own `self.org.row_hash()` at
current :1882). **Nothing mutates `self.org` between the two calls**: the only statement in between is
`self._write_journal(row["at"], journal_row)` (or the inline-dict equivalent), and `_write_journal` (def
:3094) touches only `self.journal_rows_written` (a plain int) plus file I/O — never `self.org`. This is why
the two digests are identical in 9,331/9,331 canvases on the record (PREREG §2 M3 row).

**Fix:** give `_coarse_row` a `digest: str` parameter; both call sites pass the already-computed hash
(`journal_row["hash"]` for branch 1; hoist branch 2's `self.org.row_hash()` into a local `canvas_hash`
used in both the dict literal and the `_coarse_row(...)` call) instead of letting `_coarse_row` call
`row_hash()` itself.

**Proofs still to write:**
- RED: monkeypatch/wrap `Organism.row_hash` with a call counter around one worded canvas's processing;
  assert count == 2 today (will become 1).
- GREEN / regression: hour-1 fixture replayed under `genome/ALPHA4.genome` and under (need to confirm
  exact path) the FLOOR ladder genome, byte-identical INCLUDING `hash` to
  `/data/dev/genome-wt-induce/scratch/replays/h1-alpha4-master/journal.jsonl` (mask the `readiness` field —
  the judge branch moved it) and `/data/dev/a4-ladder/fixtures/ref-floor/journal.jsonl`. **Not yet
  confirmed these two files exist at these paths** — check first (`ls -la` both) before writing the diff
  harness; likely reuse `creature/replay.py`'s row-compare or `tools/replay_diff.py`.
- AST/seam test: parse `creature/mind.py`, find `_consume_eye`, and for the statement list between (a) the
  hash-computing statement and (b) the `_coarse_row(...)` call, assert no `ast.Attribute` node with
  `.value` naming `self.org` appears (i.e., no `self.org.*` access at all between the two markers). This
  is the "assert nothing moves between them" the spec asks for.
- Positive control for the AST sweep itself: run the same scanner against a small synthetic source string
  that DOES insert a `self.org.moment(...)` call between the two markers, and assert the scanner flags it
  — proves the seam test isn't vacuously passing.

### M4 — the sitter's canvas unit
Confirmed in both readers: `creature/exam.py:108` (inside `voice_loop`) and `creature/senses/sit.py:89`
(inside `sense`) both compute `canvas_count = moments // max(1, fixations)` from `state/ledger.json`'s
`"moments"` field (`= org.t`, the raw glance counter). This over-counts: each worded canvas advances `t` by
5 (4 located glances + 1 coarse) while `fixations` (GAZE's declared count) is 4, and every SLEEP replay
adds `SLEEP.replay` more moments (not real canvases at all) on top. Net: the exam/SIT cadence fires at
~400 real canvases instead of 500 (matches PREREG's own claim, and review §4/§7).

The mind's own true canvas counter is `self._canvas_index` (mind.py :496 init, incremented exactly once
per `_consume_eye` call at current :1863 — **outside** the branch if/elif/else, so it counts every canvas
including the "sight-only, FAST undeclared, skip entirely" branch too).

**Fix:**
1. `Mind.snapshot()` (mind.py, the `ledger = {...}` dict starting at current :3123) gains
   `"canvas_index": self._canvas_index` — a ledger-only key, never `org.c` (G's hash-law lesson: this must
   never move any digest).
2. `creature/exam.py`'s `voice_loop` reads `ledger.get("canvas_index")`; if present, use it directly as
   `canvas_count`; else fall back to the current `moments // fixations` arithmetic (an old ledger with no
   key).
3. Same fallback pattern in `creature/senses/sit.py`'s `sense()`.

**Proofs still to write:** RED on a toy ledger (5 moments/canvas + 200/sleep) showing today's arithmetic
firing at ~canvas 400 against a declared "at 500"; GREEN with `canvas_index` present firing at the mind's
real count, AND an old ledger (key absent) still using the fallback unchanged. Confirm (quick sanity, low
risk) that this change touches no journal/hash parity — exam.py/sit.py run in separate sense threads
reading files, not mind.py's tape-consume path, so the hour-1 fixture replay should be untouched by
construction; still worth one confirming run. Report must state the consequence PREREG already gives
(≈25–35% fewer sittings) rather than re-deriving it.

**Not yet checked:** whether `tests/creature/test_exam.py` / `test_sit.py` exist already (need `ls
tests/creature/ | grep -i 'exam\|sit'`) — decide the right test file before writing.

### M5 — the think thread's real cost (STATUS: think_freeze_ms / think_apply_ms)
**Hard law, confirmed by reading the code (not assumed):** `creature/mind.py` must never `import time` /
`datetime` / `random` nor touch `os.urandom` — enforced by an AST sweep,
`tests/creature/test_mind_parity.py::TestMindHasNoClock::test_mind_has_no_clock` (reads the file's own
`ast.parse`, fails on any forbidden import or `os.urandom` attribute access). The file's own header comment
states the reason and the existing workaround pattern: "The actual wall-clock read ... lives in
creature/think_thread.py, which this law does not bind; this file only ever does ARITHMETIC on the float ms
numbers that module hands back" — exactly what `wait_for()` (think_thread.py, times `future.result()`) and
`worker_run()` (times `decide()`) already do for `think_wait_ms`/`think_ms`.

Two places need timing, per the PREREG (M5 row + review §7 "the freeze and the apply land on the mind
thread"):
1. **Freeze** — `_maybe_think_threaded` (mind.py, current :2888): `frozen =
   think_thread.freeze_inputs(self, item, self._canvas_index)`. Plan: add
   `think_thread.freeze_inputs_timed(mind, item, boundary) -> (FrozenThinkInputs, freeze_ms)` — a thin
   wrapper in think_thread.py (where `time` may be imported) that calls the existing `freeze_inputs` and
   times it; mind.py calls the `_timed` wrapper and stores the float into a new attribute
   `self.think_freeze_ms_last`.
2. **Apply** — `_think_apply_pending` (mind.py, current :2925): `applied = self._think_apply_plan(item,
   plan, launched_at)`. `_think_apply_plan` is a Mind method that performs the real ONE-WRITER writes, so it
   can't move to think_thread.py — instead add a generic `think_thread.timed_call(fn, *args, **kwargs) ->
   (result, ms)` helper (the `time.perf_counter()` calls physically live in think_thread.py's frame even
   though `fn` is a bound Mind method); mind.py calls
   `applied, apply_ms = think_thread.timed_call(self._think_apply_plan, item, plan, launched_at)` and
   stores `self.think_apply_ms_last`.

Init both new attributes (`None` default) near `self.think_ms_last` (mind.py current :478).

STATUS: `creature/body.py`'s `_build_status()` — add, right beside the existing `think_ms_last` /
`think_ms_median` lines (current :407-408), the identical None-safe/rounded pattern:
```python
"think_freeze_ms": (round(float(v), 3) if (v := getattr(self.mind, "think_freeze_ms_last", None)) is not None else None),
"think_apply_ms": (round(float(v), 3) if (v := getattr(self.mind, "think_apply_ms_last", None)) is not None else None),
```

**Proofs still to write:** RED (keys absent from `_build_status()`'s output today); GREEN (present on every
write, `None` when threading never ran); re-run `test_mind_has_no_clock` unchanged/still green (no `import
time` added to mind.py); confirm the hour-1 fixture journal is untouched (these two numbers are STATUS-only,
never journaled).

**Not yet checked:** the exact test file for STATUS-field additions (grep `think_ms_median` under `tests/`
to find the established pattern other builders used for this same kind of #164 addition).

### Tool fix — check.py SIZING line under GROW
Confirmed bug in the CURRENT code (already touched once, 2026-09-23 07:38 +0400, but still wrong):
`tools/lives/check.py`'s `cap_kind = "capacity (GROW: no cap)" if status.get("sight_capacity") is not None
else "NMAX"` tests the wrong thing. `creature/body.py` writes `"sight_capacity": int(org.sight.nmax)`
**unconditionally** (current :338, no gate on GROW) — so `status.get("sight_capacity")` is not None for
EVERY modern body regardless of whether the genome declares GROW. The "else NMAX" branch is dead for any
current run; the tool will never print "CROSSES NMAX" even on a genome with a real, refusing NMAX cap.

Real signal available: `tools/lives/launch.sh` copies the run's genome text to `$ROOT/GENOME.genome`
(confirmed: `cp "$CODE/$GENOME_REL" "$ROOT/GENOME.genome"`). Fix: add `_genome_declares_grow(root) ->
Optional[bool]` that parses `root/GENOME.genome` via `genome.machinery.parse_genome` and returns `"GROW" in
genome.declared`, `None` if the file is missing/unparseable (an older/partial run — treat as False, the
conservative/old default, for the wording choice). Replace the `sight_capacity` test with this. Use the
PREREG's own phrase: under confirmed GROW, the crosses-message reads "capacity doubles (GROW re-allocates:
not a refusal)"; otherwise keep the literal "CROSSES NMAX".

**Not yet checked:** full contents of `tests/creature/test_lives_check.py` (only located it, not read) —
read it fully before adding tests, to match its existing fixture-building style.

### Tool fix — check.py by-hour buckets for the coarse row (writes no `when`)
Confirmed via `docs/briefs/A4L-DROP-REPORT.md` (lines 11 and 42, "What is NOT done" + task 3's note):
`_coarse_row` (creature/mind.py) never writes a `"when"` key — verified by reading its returned dict:
`{"seq", "moment", "act": "coarse", "glance", "fix": None, "windows": None, "hash", [+residual/confirmed if
SURPRISE]}`, no "when" anywhere. `check.py`'s `births_by_hour()` / `confirmed_share_by_hour()` bucket every
row by `(d.get("when") or "")[:13]`, so every coarse row's counts (materially, its `"confirmed"` bool when
SURPRISE is declared) land under the bogus `""` hour instead of their real hour — verified against
A4L-DROP-REPORT's own number (the `""` bucket's share, 0.0253, equals exactly 46/1818, the report's own
coarse-glance confirmed count).

**Fix belongs in check.py only** — NOT in `_coarse_row` (adding a `"when"` key there would change the
on-disk journal shape and break M3's own "no declared difference on the hour-1 fixture" requirement, since
that fixture-replay diff is byte-for-byte against a reference journal). Plan: in `check.py`, build a `seq ->
when` map from every row carrying `"moment"` and a truthy `"when"` (the coarse row shares its triggering
canvas row's exact `seq` — confirmed at both `_coarse_row(row["seq"], ...)` call sites in mind.py); have
`births_by_hour`/`confirmed_share_by_hour` look up that map when a row's own `"when"` is missing, before
taking `[:13]`.

**Not yet checked:** same `tests/creature/test_lives_check.py` file — read it fully, add a fixture row
shaped like a real coarse row (no "when", "seq" matching a sibling canvas row that has one) and assert its
confirmed count lands in the sibling's hour, not `""`.

### Tool fixes NOT YET INVESTIGATED AT ALL (no code read)
- **tools/inventory.py** resolving a `<BASE>_<X>` key only through its OWN RUNS row (A4L-EXPLORE-REPORT §0
  item 10 (a)). Have not opened either file.
- **explore_lock_mark wired into the reader's conjunction** (A4L-EXPLORE-REPORT §0 item 9 (a)). PREREG §5.4
  already names `tools/verdict_life.py:explore_lock_mark` (X1) as built and says "wired into the conjunction
  by B1" — i.e. this report's own author is on the hook for the wiring; have not opened
  `tools/verdict_life.py` or found "the reader's conjunction" (likely an all-marks-pass gate in
  `tools/verdict_g4.py` or `tools/verdict_life.py` itself).
- **tools/pin_g1.py step (1)** re-pinned with the GROW hash-law commit `85bf792` cited (A4L-ANSWER-REPORT
  "not-done 5"). Have not opened `tools/pin_g1.py`, that report section, or confirmed `85bf792` in `git log`.

## What was NOT done (raised, not worked around — just not reached)
Everything above is a plan grounded in the live code, not a guess, but none of it has been implemented,
tested, or gated yet. No RED test exists. No suite has been run in this worktree. No commit before this one
exists on `a42-b1`. This is a research hand-off only.
