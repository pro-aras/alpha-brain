# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 00:35 +0400 — A1-A8 report (worktree /data/dev/genome-wt-a, branch g4-body).

# G4 BUILDER A — THE BODY: REPORT

All 8 tasks (A1-A8) done, in order, each committed after its own passing test. Full suite at the end:
**`Ran 34 tests in 209.938s — OK`** (`tests/creature/`, `python3 -m unittest discover -s tests/creature -t .`).

No PREREG clause was left unmet. Two places needed a documented reading rather than a literal one
(both flagged below, both left as comments in the code itself for Claude to overturn); one place needed
a small mechanical adaptation to a numpy/pathlib interaction the PREREG's literal path text doesn't survive.

## A1 — the tape (`creature/tape.py`, `tests/creature/test_tape.py`)
**Test log:** `Ran 2 tests in 0.051s — OK` · **Commit:** `11b6f2b`
Straightforward. `publish()` writes the payload, appends the row, then persists SEQ, all under one lock
(so concurrent threads get strictly increasing, unique seqs — verified 3×100 threads → 300 consecutive
seqs). `read_tape()` sorts day files lexically then reads in append order. A second `Tape` on the same
root reads `tape/SEQ` at construction and continues from there.

## A2 — the mind (`creature/mind.py`, `tests/creature/test_mind_parity.py`)
**Test log:** `Ran 7 tests in 94.692s — OK` · **Commit:** `de50eef`
**Gate G4-2: PASS, exact.** `mind.org.state_hash()` over the 660 dev canvases (fed as a tape, ear-then-eye
per canvas) equals `d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86` — both the PREREG's
literal pin and a fresh `run_g1.live(...)["hash_dev"]` computed in the same test. Control (two canvases
swapped) produces a different hash.

**The pic_id question, resolved by direct measurement:** `genome/gaze.py::fixations()` only reads
`pic_id` for `mode == "random"` (`g.random_gaze(an, seed=pic_id, ...)`); for `mode == "surprise"` it calls
`g.gaze_sequence(an, max_fixations=F, predicted=None)`, which never touches `pic_id` at all. So feeding
`row["sha"]` (the tape's own field, a 64-char sha256 hex) as `pic_id` — instead of `run_g1`'s `_pid(rgb)`
(a 16-char truncated sha256 of the raw array bytes) — is provably inert for the live mind (mode
"surprise") and only matters for the `--blind gaze` twin (mode "random"), where it becomes the seed for a
DIFFERENT deterministic stream than `run_g1`'s twin would use — which is fine, since G4-2 only pins the
surprise-mode hash and the blind twin's own gate (A6) only requires it to be internally replay-identical,
which it is (measured in A6).

**`state/ledger.json`'s shape (per the orchestrator's mid-task note):** carries the PREREG's
`{"last_seq", "moment_word", "moments"}` — where `moment_word` is keyed by the ORGANISM's own moment
counter (`org.t`, one entry per glance, not per tape seq or per canvas) — PLUS derived `{"sight", "words"}`
ledgers built via `genome.questions.build_ledgers(org, moment_word)`, in the exact shape `genome/ask.py`'s
`load()` reads. I added one more field beyond the PREREG's three, `"ear_pending"` (the mind's own
in-flight ear-without-eye moments — `self.pending`), so a resume never loses an ear row consumed just
before a crash; this is additive, not a PREREG violation.

**Mechanical adaptation, not a raised clause:** the PREREG says `snapshot()` writes
`org.save(run_root/state/organism.npz.tmp)` then renames. Measured directly: `np.savez_compressed`
appends `.npz` to any filename that doesn't already end in `.npz` — so `"organism.npz.tmp"` becomes
`"organism.npz.tmp.npz"` on disk — and `Organism.save`'s own `path.with_suffix(".json")` on that same
input produces `"organism.npz.json"`, NOT a `.tmp` file at all. Fed back through `Organism.load`'s own
`path.with_suffix(".npz")`/`.with_suffix(".json")` convention, that pairing is unloadable as a clean
`organism`/`organism.npz`/`organism.json` triple. I used the base name `organism_tmp` instead (produces
`organism_tmp.npz` + `organism_tmp.json`, both `os.replace`'d onto `organism.npz`/`organism.json`) — same
write-tmp-then-rename atomicity the PREREG asks for, compatible with `Organism.save`/`load`'s own suffix
mechanics, which are Claude's/`genome/machinery.py`'s and not mine to change.

**Determinism law:** pinned by an AST sweep (`test_mind_has_no_clock`) — `creature/mind.py` imports none
of `time`, `datetime`, `random`, and no `os.urandom` attribute access anywhere in the file.

## A3 — the body (`creature/body.py`, `tests/creature/test_crash.py`)
**Test log:** `Ran 9 tests in 129.196s — OK` · **Commit:** `530558b` (later edited in A7, commit `4cba3df`)
`SenseThread` counts each sense's publishes on ITSELF (not inside `fn`'s own loop variable), so a plant
(`"eye:20"`) fires exactly once across restarts even though `fn` restarts its own internal counter from
zero every time it's re-entered — measured directly: one `sense_restart` row over a 30 s run with the
plant, zero without it, and the tape keeps growing after the restart. `test_crash.py` uses a synthetic
sense (not `world_maker`, which is A4) so it never depended on task ordering.
STATUS is written on every branch (§2.5) including at shutdown; `mind_ms_median_1min` comes from a
body-owned deque of per-row wall times, pruned to the last 60 s at read time.

## A4 — the world-maker (`creature/world_maker.py`, `tests/creature/test_world_maker.py`)
**Test log:** `Ran 18 tests in 136.291s — OK` · **Commit:** `9284ae0`
`schedule(seed, window)` and `make(seed, window, i)` are pure (verified: same args -> equal arrays/lists).
`make`'s ONE rng (`default_rng([seed, window, i])`) both picks the thing (its first draw, indexing into
`schedule`'s list) and renders it (its remaining draws, fed to `world.render_canvas`) — reading PREREG
§2.8's "one thing (rng) is rendered ... with rng=default_rng([SEED,window,i])" as one rng doing both jobs
in sequence, not two separate rngs. `schedule`'s own "3 of THINGS_11" draw uses a dedicated seed-tuple
offset (`_PLANT_MARKER = 10**6` as the third element) kept apart from `make`'s per-canvas `(seed,window,i)`
draws so the two streams never collide; the plant's canvases use the same marker with a distinct third
slot. `DEFAULT_SEED = 20260920` (never `2`, G1's held-out seed — measured disjoint against
`world.holdout_canvas(THINGS_11, 10, default_rng(2))` over 200 maker canvases). Plant thresholds
(`plant_after_canvases`, `plant_window_s`, `plant_showings`) are constructor kwargs whose defaults match
the PREREG exactly, but are overridable so the mechanism is testable in seconds instead of hours (the test
verifies it fires 1-3 times under `plant_after_canvases=5, plant_window_s=2.0, plant_showings=3`, and that
`THING_NULL`/`THING_NEVER` never appear).

## A5 — STATUS watcher + units (`tools/creature_watch.py`, `deploy/`, `tests/creature/test_watch.py`)
**Test log:** `Ran 24 tests in 136.111s — OK` · **Commit:** `fcc8e3b`
`check()` compares two STATUS-shaped dicts by their OWN `heartbeat_at` stamps (not the watcher's own poll
time), so "frozen 61 min apart" and "moving" are both driven directly with synthetic dicts — no real
sleeping. Moved counters -> the kept baseline updates to the current reading; unmoved AND
`elapsed >= 60 min` since the kept baseline -> pages (`root/pages.jsonl` append + `root/PAGE.json`
write) and the baseline is left as-is (so a still-frozen creature keeps paging on every 5-min tick,
rather than going silent after one page). `STATUS.json` itself is never touched by the watcher — a
would-be `STATUS.page` field lives in its own `root/PAGE.json` file, one writer per file, per the PREREG's
own parenthetical. `deploy/install.sh` copies + `daemon-reload`s only; never enables or starts (verified
by reading the script — no `systemctl ... enable`/`start` anywhere in it).

## A6 — replay (`creature/replay.py`, `tests/creature/test_replay.py`)
**Test log:** `Ran 27 tests in 187.533s — OK` · **Commit:** `222fcc8`
A live 200-canvas run (maker at period 0.05 s, queue fully drained before stopping so the reference
journal covers every published row) replays byte-identical: `replay.main(["--against", ...])` -> exit 0.
**Corruption test, one honest failed-then-fixed attempt worth recording:** flipping a single pixel's
single channel at a fixed canvas corner (byte-level "one payload byte flipped") produced **zero
divergence** — measured directly, not assumed. The corner pixel is background, far from the fixation grid
cells the saliency-pooled gaze mechanism actually weighs, so a one-pixel change there is invisible to it.
Fixed by corrupting a 16x16 block squarely inside the thing's own bounding box, read from
`root/truth/<seq>.json` (never the tape, PREREG §2.1) — that reliably diverges, and the reported seq is
exactly the corrupted row's own (`DIVERGED at seq 204: births` in the last run). `--blind gaze` produces a
journal that (a) differs from the surprise-gaze journal and (b) is itself byte-identical across two
independent replays of the same tape — both measured, matching A2's finding that mode "random" seeds on
`pic_id` (deterministically reproducible) while "surprise" ignores it.

## A7 — the ask door (`creature/ask.py`, wired into `creature/body.py`)
**Test log:** `Ran 29 tests in 207.933s — OK` · **Commit:** `4cba3df`
`load_snapshot()` derives the `Genome` from `organism.json`'s own stored `genome_text`
(`Organism.save` already persists it) — no `--genome` argument needed for the voice. Ten `what-is`
questions against a held-out canvas answer identically and leave the LIVE mind's `org.state_hash()`
unchanged (measured before/after). The inbox thread (`inbox_loop`) is wired into `Body.start()`/`stop()`
alongside the mind and STATUS threads, sharing `Body.stop_event`.
**Schema gap, resolved as an extension, not a blocker:** PREREG §2.7's inbox shape
`{"q", "pic", "word"}` has no second picture, but `"which"` needs two (`edge(a) vs edge(b)`). Added an
optional `"pic_b"` key for that one command; `"what-is"`/`"show"`/`"is"` use exactly the PREREG's fields.
**Thread-safety finding (from a test bug, not a body bug):** my first draft of the test called
`mind.snapshot()` directly from the test thread right after stopping the maker sense, racing the mind
thread's own in-flight `consume()` — `org.sight.n` could be read as `81` while `org.sight.cells[:n]`'s
underlying array had already been resized to `79` mid-save, producing
`ValueError: could not broadcast input array from shape (79,112) into shape (81,112)` on the reload. Fixed
by never calling `snapshot()` from outside the mind's own thread — the test now drains the queue and
waits for `consume()`'s own automatic 500-moment snapshot instead. Nothing in `mind.py`/`body.py` needed
to change; this confirms the "ONE mind thread" law (§2.3) is load-bearing, not decorative.

## A8 — the writer sweep (`tests/creature/test_writer_sweep.py`)
**Test log:** `Ran 34 tests in 209.938s — OK` (full suite) · **Commit:** `13a9eab`
**Gate G4-1: PASS, 0 offenders** over `creature/senses/*.py` (empty package so far) and
`creature/world_maker.py`, `creature/ask.py` (writer check only, see below).
**Reading, left as a comment in the test file for Claude to overturn:** the "no `Organism` import" clause
is checked only against `creature/senses/*.py` and `creature/world_maker.py` — the true SENSES
(`B3`/`I1`: "the mind is the only reader of the tape and the only writer of memory") — never against
`creature/ask.py`, since PREREG §2.7 explicitly requires the voice to construct a private `Organism`
(`Organism.load + ledger`); applying the import ban there would contradict its own contract in the same
document. The write-path check (no `open()`/`.write_*`/`np.save` whose first argument contains
`state`/`journal`/`memory`) is applied to all three files per this brief's own wording (a plain substring
check on any call, any mode) — a superset of the PREREG table row's narrower "`open(…, "w"/"a")` under
`run/state`" form, so nothing the narrower form would catch escapes the broader one.
**Self-caught bug in the walker (worth recording — a control that didn't control anything, #91's class):**
the first version of `find_offenders` only flattened INLINE path expressions. A planted offender written
as `p = Path(root) / "state" / "hack.json"; open(p, "w")` — exactly the style `creature/ask.py`'s own
`out_path = ...; out_path.write_text(...)` uses — passed the "planted offender is caught" control, because
`open(p, ...)`'s first argument is a bare `Name` node the flattener didn't resolve back to its assignment.
Fixed with a same-module `name -> flattened text` map built from simple assignments
(`_build_env`); re-verified the control now catches the planted offender, and added a second, negative
control (a planted CLEAN module, writing outside state/journal/memory) that is correctly NOT flagged, so
the sweep isn't merely "catch everything" either.

## Measured numbers
- **G4-2 parity + its swap control + PNG round-trip + determinism sweep + snapshot/resume round-trip:**
  94.7 s for 7 tests (two full 660-canvas x 4-glance gazing passes inside that).
- **A live 200-canvas replay round (A6's class):** ~53 s for setUpClass (one live run + drain) plus three
  replay passes (normal, blind x2) in the same class.
- **Mind.consume() cost, solo, measured directly** (150 eye rows, 11-thing mix, `OPENBLAS_NUM_THREADS=1
  OMP_NUM_THREADS=1`, this box): **median 39.3 ms/eye-row, mean 41.2 ms, p95 41.2 ms** (4 glances each,
  so ~10 ms/glance). RSS at that point: **135.9 MB** (`resource.getrusage(RUSAGE_SELF).ru_maxrss`, this
  process, single-threaded, no other senses/threads running — a true "solo" number, not G4-7's real-
  concurrency number, which is Claude's gate to run once all threads are wired together).
- **Full suite:** `Ran 34 tests in 209.938s — OK`, `python3 -m unittest discover -s tests/creature -t .`.

## Ownership check
`git status --short` at every commit showed nothing outside `creature/`, `tests/creature/`, `deploy/`,
`tools/creature_watch.py`, and this report under `docs/briefs/`. Never touched `genome/`, `run/`,
`docs/G4-PREREG.md`, `/data/dev/genome` (master tree), `/data/dev/alpha3`, or `/data/dev/alpha2` (only
read, via the sha-pinned `genome/gaze.py` import chain, which is Claude's/Builder B's code, not mine).
Every run and test used `tempfile.mkdtemp()` — grepped my own files to confirm no reference to
`/data/dev/genome/run` or `/data/dev/genome-wt-a/run` anywhere. No sudo, no `systemctl enable`/`start`
(only `daemon-reload` in `install.sh`), no file sent anywhere, no PDF. The crash test's longest single
run was 30 s; the replay test's live-run component targeted 200 canvases at period 0.05 s (~1-2 min
including gazing) — nothing run in the background that outlives this process.

## Commits (g4-body)
```
11b6f2b A1: the tape
de50eef A2: the mind — gate G4-2 PASS
530558b A3: the body — SenseThread, Body, STATUS, crash isolation
9284ae0 A4: the world-maker — schedule/make (pure), the maker sense thread
fcc8e3b A5: STATUS watcher + units
222fcc8 A6: replay — mind rows byte-identical, corrupted-payload divergence, --blind gaze twin
4cba3df A7: the ask door — voice thread wired into body.py
13a9eab A8: the writer sweep — gate G4-1
```
