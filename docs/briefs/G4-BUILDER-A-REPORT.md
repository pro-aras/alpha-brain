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

---

# WAVE 2 (A9–A13)

*edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 23:0x +0400 (the builder's own stamp read «2026-09-20 03:10 +0400», four hours ahead of the box's clock; corrected by Claude (Fable 5.1) at 2026-09-19 23:10 +0400, #50's class) — worktree fast-forwarded to master 0cb21f7 (both
builders' wave 1 merged + PREREG §11); this section covers A9–A13, committed c309fbb..41afc28.*

**Full suite at the end (all wave-1 + wave-2 tests together):**
`Ran 60 tests in 447.030s — OK (skipped=2)` — `python3 -m unittest discover -s tests/creature -t .`.
The 2 skips are both `unittest.skipUnless(importable)` on Builder B modules not on master at commit
time (named below, per task). Gate G4-2's pin (`d4b5c6b8…`) and gate G4-1 (the writer sweep) were
both re-verified green after every task; nothing outside `creature/`, `tests/creature/`,
`docs/briefs/G4-BUILDER-A-REPORT.md` was touched, and `run/` (the live creature under
`creature.service`, active throughout this work) was never written to, restarted, or read except
by `systemctl --user is-active` (a status check, not a control action) and one benchmark that shared
the same idle box CPU with it.

## A9 — PREDICT + FAST in the mind (PREREG §11.1 steps 1–2)
**Test log:** `Ran 5 tests in 36.661s — OK` (`tests/creature/test_wave2_predict_fast.py`) · **Commit:** `c309fbb`
`err`/`lr`/`ep` now land on every eye-row mind row (0.0/1.0/`None` when the gene is absent or blind,
still journaled, per the PREREG's own "still journaled" clause); sight-only canvases with FAST
declared run `Organism.moment_sight` per glance (word `null`) instead of the skeleton's old
skip-and-count row; `Mind.episodes`/`Mind.predictor` persist across snapshot/resume.
`tests/creature/G4-wave2-test.genome` = `G4-skeleton.genome` + `PREDICT` + `FAST`. Gate G4-2 re-run
as a regression on the untouched skeleton genome: still reaches the exact pin
`d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86`; `mind.episodes`/`mind.predictor`
are both `None` on that genome, so every new branch is provably dead code for it.
**No clause unmet.** Two bugs caught before shipping (both fixed, both re-verified — see A9's own
commit message for the full detail): `questions.build_ledgers` needs `moment_thing[m]` for every
birth's moment, and a sight-only `moment_sight` glance can birth a cell with no `moment_word` entry
recorded for it (`KeyError` on the first such birth); and `Mind.resume()` replacing `self.org` left
the predictor's closure pointing at the pre-load organism (rebuilt after the load, before its
persisted `last_winner` is restored).

## A10 — SLEEP in the mind + the six blinds (PREREG §11.1 step 4)
**Test log:** `Ran 6 tests in 144.720s — OK` (`tests/creature/test_wave2_sleep_and_blinds.py`) · **Commit:** `f55510f`
SLEEP/`cycle`/(TRAITS when available) wired in `_maybe_sleep`; journaled as a SECOND mind row
sharing its triggering canvas's own seq, which required `creature/replay.py`'s `compare()` to group
mind rows by seq into ordered lists instead of a dict keyed by seq (a genuine format change, not
scope creep — both changes shipped together in `c309fbb` since `_maybe_sleep` sits in the same
per-canvas method as PREDICT/FAST). All six blinds (`gaze`, `sleep`, `predict`, `frozen`,
`curiosity`, `park`) replay byte-identical to themselves; four (`gaze`, `sleep`, `predict`,
`frozen`) are measured to differ from the unblinded journal; `curiosity`/`park` do **not** differ
yet — asserted as an honest documented negative (`test_curiosity_and_park_blinds_currently_inert`),
since THINK (A11) is their only mechanism and did not exist yet when this task ran.
**No clause unmet.** Two bugs caught before shipping: `genome.sleep.sleep()` calls `org.moment()`
once per replayed episode, advancing `org.t` and birthing cells my per-glance loops never saw
(fixed by pre-recording `moment_word` via a second, read-only `Episodes.most_surprising(n)` call in
the same order `sleep()` will replay); and `--blind frozen` showed **zero** observable divergence on
a 60-canvas tape (only 28 total cells born, under the default-absent FROZEN threshold of 50 — a
control that didn't control anything, #91's class) — fixed by growing the test tape to 150 canvases
(measured: 60 total cells unblinded, 11 refusals blind).

## A11 — THINK in the mind (PREREG §11.1 step 3)
**Test log:** `Ran 10 tests in 10.807s — OK (skipped=2)` (`tests/creature/test_wave2_think.py`) · **Commit:** `867663d`
**RAISED, not worked around:** THINK's own gene clause (`THINK every <n> canvases`) has no parser
clause on `master` at commit time — confirmed, not assumed, by
`test_think_gene_line_is_currently_unparseable` (a `GenomeError` on that exact line). No genome this
worktree can parse ever sets `"THINK" in genome.declared`, so the gate the whole step lives behind
can never fire end-to-end through a real genome file today. To still exercise the gated path, the
tests mutate the **already-parsed** `Genome` object's `declared` dict in memory
(`mind.genome.declared["THINK"] = {"every": N}`) — no file under `genome/` is touched, the same
technique as building any other in-memory test fixture; documented at the top of the test module.
**skipUnless-gated (2 tests, both skipped in this run):**
- `TestThinkBeliefFormation.test_word_item_forms_a_belief_when_answered` — `skipUnless(_THINK_LAWS_AVAILABLE)`; `genome.think` (needed for kind "word" → `think.believe`) not on master.
- `TestThinkCuriosityChoice.test_curiosity_declared_uses_interests_choose` — `skipUnless(_CURIOSITY_AVAILABLE)`; `genome.curiosity` not on master (the `CURIOSITY` gene ITSELF already parses, from wave 1's B1 — only the module is missing).

Implemented and exercised without either missing module: the 3-part POOL (words of the last 200
episodes whose `recall` abstains; episodes with word `""`; filed-and-due predictions),
`_think_choose` (no `CURIOSITY` declared → first item; blind `curiosity` → a **genome-seeded** rng's
uniform pick, `np.random.default_rng([genome.seed, 0x71494e4b])` — never wall clock or
`os.urandom`, the determinism law holds and is re-pinned by `test_mind_has_no_clock`), kind (b)
(sight → nearest word via `Episodes.nearest` → `FILE` a prediction) with PARK's dead-end wiring
(`genome/park.py`, already on master), and kind (c)'s due-prediction scoring via `predict.score`.
**Documented simplifications (interpretive choices, not violations — the PREREG's prose underspecifies
the exact mechanics here):** kind (b)'s "nearest word by FAST's nearest over episodes with a word"
searches the top-10 nearest OVERALL episodes for the first one carrying a word, since
`Episodes.nearest()` has no word filter; a filed prediction's decider `"recall == word"` is evaluated
via a fresh word-cell lookup (`questions.build_ledgers`) rather than a persisted per-edge index —
correct, O(births) per score, acceptable at this life's scale, worth revisiting if THINK's cadence
is ever high-frequency in the 24 h life.
Also caught here: `--folder`'s canvas size was read from `body.mind.genome`, which does not exist
until `start()` runs — fixed by parsing the genome file directly in `main()` before this ever ran live.

## A12 — the folder door (PREREG §11.3)
**Test log:** `Ran 1 test in 3.776s — OK` (`tests/creature/test_folder_door.py`); G4-1 re-verified green with the new module: `Ran 5 tests in 0.012s — OK` · **Commit:** `37ecedd`
`creature/senses/folder.py` watches `world/<word>/` (a–z ≤ 8 letters, ≥ 1 picture) by **sha256**
(never mtime alone — a touched-but-byte-unchanged file must not re-publish); ear (word = folder
name) then eye, source `"folder"`, `meta.moment = "f" + sha[:12]`; `root/folder/SEEN.json` is
written **after** the rows are durable on the tape (the cursor law, #230) — a crash between
publishing and marking-seen safely re-publishes on restart, never silently drops a picture. Armed
only by an explicit `--folder PATH` on `creature.body`, default OFF (`--folder-period`, default 30s).
Verified directly, not assumed: two pictures → 4 rows (ear-then-eye per moment, ear seq < eye seq
for both); a **second, fresh `Body` on the same root** (the restart the task asks for) publishes
zero new rows for the same two pictures.
**No clause unmet.**

## A13 — the self-exam duty (PREREG §11.4)
**Test log:** `Ran 4 tests in 30.624s — OK` (`tests/creature/test_exam.py`) · **Commit:** `41afc28`
`creature/exam.py`'s `run_exam()` reuses `tools/self_exam.py`'s own `main()` (a scoped `sys.argv`
swap, restored in a `finally` — never copying its orchestration) over the latest snapshot in a
PRIVATE Organism; `run_and_journal()` adds the PREREG's `{"event":"exam","path","q1","cells"}` row.
Measured directly, not assumed: the live mind's `org.state_hash()` is byte-identical before and
after every exam, both through a direct `run_and_journal()` call and through the cadence-driven
`voice_loop()` thread running concurrently with a live `Body`.
Deliberately **not** walked by gate G4-1's writer sweep (scoped to `creature/senses/*.py`,
`creature/world_maker.py`, `creature/ask.py`): `creature/exam.py` is neither a sense nor the voice's
own core file, so its journal write sits outside that gate's fixed file list — a design choice
recorded in the module's own docstring, not an oversight (§11.4 explicitly requires the journal
write A8's sweep would otherwise have had to special-case around).
`voice_loop()`'s cadence is read from the snapshot's own `"moments"` (`state/ledger.json`) divided
by the genome's fixations-per-canvas — the voice never reads a live counter off the mind (§2.7's
law: it never touches the mind's objects). **EXAM's own gene clause is not on master's parser at
commit time** (same gap as THINK), so `Body`'s wiring (committed with A12, `37ecedd`, since its hunks
sit interleaved with `--folder`'s in `main()`/`start()`/`stop()`) is gated on `"EXAM" in declared`
and untested end-to-end through a real genome file; the direct `voice_loop()` test bypasses that
gate the same way A11's THINK tests do, by starting the thread explicitly rather than through `Body`.
**No clause unmet.**

## Cost: ms per canvas, skeleton vs. every wave-2 step ON
Measured fresh, this session, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, solo (no other creature
threads in the SAME process) — but **not** an idle box: `creature.service` was live throughout
(`systemctl --user is-active` → `active`, PID running since 22:29) and Builder B's own test suite
ran concurrently for part of this session. 150 canvases each, 4 glances/canvas:

| genome | median ms/canvas (eye row) | mean ms/canvas | n |
|---|---|---|---|
| `G4-skeleton.genome` (no wave-2 gene) | 37.98 | 39.38 | 150 |
| `G4-wave2-sleep-test.genome` (PREDICT + FAST + SLEEP, mixed worded/sight-only) | 38.35 | 43.43 | 150 |

**Ratio (mean, wave-2-on / skeleton): 1.10×.** RSS at the end of both runs in the same process: 170.3 MB.

This does not match a cited skeleton baseline of 19 ms — flagged rather than quietly reconciled: A1–A8's
own report (measured on an idle box, before the creature went live) read **39.3 ms median** for the
skeleton, i.e. consistent with THIS session's 37.98 ms, not with 19 ms. The likely explanation is
that the 19 ms figure was read on different hardware or under different load than either of my two
measurements (both taken on this box, one before and one after `creature.service` went live) — but I
have not independently reproduced 19 ms anywhere, so I am reporting what I measured rather than
reconciling the discrepancy. G4-7 (cost at REAL concurrency, every thread running) is explicitly
Claude's own gate, not mine, per the PREREG's Order section (§7) and A13's "the voice never touches
the mind" boundary — these solo numbers are the input to that gate, not a substitute for it.

## Ownership check (wave 2)
`git status --short` was clean after every one of the 5 commits above. Touched only `creature/`
(`mind.py`, `body.py`, `replay.py`, `exam.py`, `senses/folder.py`), `tests/creature/` (5 new test
files + 3 new `.genome` fixtures), and this report. Never touched `genome/`, `docs/G4-PREREG.md`, or
`/data/dev/genome` (the master tree, read-only via the worktree's own fast-forward). `run/` (the
live creature) was never written to or restarted; the only interaction with it was one
`systemctl --user is-active creature.service` status read while investigating the ms/canvas
discrepancy above. No `systemctl enable/start/stop/restart` call anywhere in this session. Every
test and manual run used `tempfile.mkdtemp()`.

## Commits (g4-body, wave 2)
```
c309fbb A9: PREDICT + FAST in the mind — G4-8 skeleton hash unchanged
f55510f A10: SLEEP in the mind + the six blinds
867663d A11: THINK in the mind — pool/choose/work/park
37ecedd A12: the folder door — armed by --folder, default OFF
41afc28 A13: the self-exam duty — voice thread, journal EVENT row
```
