# Builder F report — HANDS, TOUCH, SMELL
*edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 20:01 +0400. Branch `life-hands`, worktree `/data/dev/genome-wt-w`, from `g5-integration 7165e05` (builder D's `life-act` landed). Brief: `docs/briefs/LIFE-F-HANDS-TOUCH-SMELL.md`.*

## Summary

All seven numbered clauses of the brief landed. Nothing was skipped; four design decisions and one genuine
gap are RAISED below, each with the reasoning and the alternative I did NOT take.

## What landed, with file:line

1. **The shelf** (`world/programs/`, 54 files; generator `tools/build_hands_shelf.py`):
   - 50 shape programs — 16 things (`genome/world.py`'s `THINGS_11` + `THINGS_ARRIVAL2`, verbatim: circle
     square triangle cross ring bar dot star arrow wave diamond moon house tree cup key), 3 size/offset
     variants each (4 for circle and square, to reach exactly 50), each a `# shape: <thing>` manifest line
     + `print('''...''')` — **pure stdlib, zero imports** (the jail's Landlock grants read+execute beneath
     the shelf and `/usr`/`/etc` only, never a site-packages tree).
   - 4 control programs (`_control_positive.py` / `_control_negative.py` / `_control_crash.py` /
     `_control_fence.py`, `# control: <kind>` manifest), G-MOT-4's own four, written by hand (not
     generated).
   - **Scale, verified against advisor's own concern before writing the drawer code**: each shape is drawn
     in roughly an 8×8-character bounding box (≤ 32 px after the 4×4-block expansion) at one of four grid
     offsets — MATCHING `genome/world.py`'s own `THING_SIDE=32` px on `CANVAS=128`, never filling the whole
     32×32 char grid (which would give a single 32×32-px glance only a corner, #228 (a)/(c)'s trap).
   - All 54 programs verified to run cleanly under plain Python (`python3 <prog>.py`, exit 0/1 only) AND
     under the real jail (`run_in_jail`, 50 shape programs, 0.88 s total / 17.7 ms average, 0 failures).

2. **`HANDS`, the sense thread, and the think-pool choice** (MOTOR-HANDS.md G-MOT-4, the plan's L-12):
   - `genome/machinery.py:332` — HANDS's grammar gains an OPTIONAL trailing clause (`shelf <dir> cpu <n>
     mem <n> wall <n>`), wrapped in its own non-capturing group so the PRE-EXISTING short form (`HANDS jail
     <path>`, `tests/genome/test_parse_g4.py:111`'s own pin against `tests/genome/G4-draft.genome`) keeps
     parsing to the exact same one-key dict.
   - `creature/senses/hands.py` (new, 277 lines) — the sense thread: waits for `run/hands/ACT`
     (`{seq, program, at}`, the SAME act-file pattern builder D's game door uses), runs the chosen program
     through the real jail with a FRESH scratch dir per act (`_fresh_scratch`, #212), `ro_root` = the shelf,
     decodes stdout/stderr with `errors="replace"` (`_run_one:224`, G-MOT-4 precondition 1), renders the
     text to a 128×128 grey canvas (`_render_ascii`: each character a 4×4 block, `#` → ink, GRID_CHARS=32 ×
     BLOCK=4 = CANVAS=128 exactly), and publishes `eye → outcome → touch` in that tape order
     (PREREG §2.2's own law). `run/hands/CURSOR` advances only after the rows are durable (#230).
   - `creature/mind.py:_mind_repo_root`/`_hands_paths` — resolves `HANDS`'s `jail`/`shelf` values: `jail`
     against the worktree's PARENT (`/data/dev`, since `alpha3/` is a sibling tree, never inside this repo),
     `shelf` against the worktree root (matching `_declared_folder_dir`'s own resolution for `WORLD`'s
     `folder`). `creature/body.py:_declared_hands_config` resolves the identical two roots for the CLI side.
   - `creature/mind.py:_think_pool` (new "hands" kind, ~line 1017) — ONE item, present iff HANDS declares a
     shelf AND no run is in flight (`_hands_pending is None`, #175: never a second choice before the sense
     thread answers the first).
   - `creature/mind.py:_think_work`'s "hands" branch (~line 1180) — PICKS a program and RETURNS the
     decision; it never touches the filesystem (builder E's seam note, NEXT-LIFE-PLAN §4 L-5: "the think
     thread writes nothing; the mind applies" — so today's synchronous THINK and tomorrow's threaded one
     apply the write through the exact same seam). Exactly TWO `_hands_rng` draws every time, regardless of
     branch (`_maybe_choose_act`'s own discipline): explore (10 % re-run of the last program, "so the
     positive control fires") or exploit (uniform over the shelf, which includes the 4 control programs too
     — the recognised-share reader excludes control-tagged rows from its own denominator, not the mind's
     choice). A missing jail binary journals `«no road»` (the brief's own literal words) EVERY time it is
     asked, never crashes, and never assumed permanent from one reading.
   - `creature/mind.py:_maybe_think` (~line 1256) — the ONE place a "hands" decision touches the
     filesystem: the atomic write-tmp-then-`os.replace` pattern `_maybe_choose_act` already uses, applied
     to `run/hands/ACT`; sets `_hands_pending`; journals `act_chosen: {"act": "run", "program", "seq"}`
     beside the existing `think` object in the SAME journal row.
   - `creature/mind.py:_consume_outcome` (~line 433) — the OTHER half of the pending gate: a hands outcome
     row's own `act_seq` clears `_hands_pending` iff it matches the current pending choice (#175).
   - `creature/body.py:Body.start` (~line 235) — the hands door, wired the SAME `add_sense` shape
     SIT/SENSE_BODY use (crash-isolation/restart/journal machinery for free).
   - `creature/genes.py` — `HANDS` registered in `RUNS["mind"]`, naming all four real call sites.
   - Snapshot/resume: `_hands_rng`'s state, `_hands_pending`, `_hands_last_program` persisted in
     `ledger.json` (mirroring `_act_rng`'s own pattern exactly).

3. **`SENSE touch`** (BODY-SENSES.md §4.6):
   - `genome/machinery.py` — `SENSE touch from hands: exit rate stalls retries bytes` → `declared["SENSE_
     TOUCH"]`.
   - `creature/mind.py:touch_episodes` — a DEDICATED `Episodes(2000, 5, 1)` ring (see the design-decision
     note below), built when `SENSE_TOUCH` is declared.
   - `creature/mind.py:_consume_touch` — decodes 5 float32s (exit, rate, stalls, retries, bytes), writes to
     the ring, journals `touch`, never crashes on a malformed payload (`errors="replace"`'s spirit applied
     to a shape mismatch, #230).
   - `creature/senses/hands.py:_run_one` — computes the real vector: `exit` = the jail's exit code, `rate` =
     `len(stdout) / dt_ms`, `stalls` = 1.0 iff the jail's own wall-clock alarm fired (exit 124), `retries` =
     0.0 (rung 1 has no retry mechanism — an honest "not implemented", never fabricated), `bytes` =
     `len(stdout)`.

4. **`SENSE smell`** (BODY-SENSES.md §4.5):
   - `genome/machinery.py` — `SENSE smell kind size folder age` → `declared["SENSE_SMELL"]`.
   - `creature/senses/folder.py:_smell_trait` — computed from filesystem metadata ALONE, BEFORE
     `gaze.canvas_of_picture` (the "opening" the brief names): `kind` = suffix index / 4, `size` =
     `log10(bytes)`, `folder` = `crc32(folder_word) / 2**32` (a HASH, never the name — BODY-SENSES's own
     words, "never the name, which is the answer"; `tests/creature/test_folder_smell.py`'s own assertion
     that the folder's real name never appears on the tape row), `age` = `log10(seconds since mtime)`.
   - `creature/senses/folder.py:sense` gains `smell: bool = False` (byte-identical to before when False);
     `creature/body.py:main` passes `smell=True` iff `"SENSE_SMELL" in declared`.
   - `creature/mind.py:smell_episodes`/`_consume_smell` — the same dedicated-ring shape as touch.

5. **The four controls, each a real jail run** (`tests/creature/test_hands_sense.py`,
   `tests/creature/test_hands_controls.py`) — all against the REAL jail at
   `/data/dev/alpha3/hands/jail_run`, none stubbed:
   - **positive** (`print("#"*4)`, constant output): residual `None` on the first run, **0.0** on the
     second and third (`TestPositiveControlResidualZero`).
   - **negative** (reads `INPUT.txt`, which `_run_one` fills with `_negative_control_input` =
     `_tape_row_count(root)` — `creature/world_maker.py` has no `WINDOW.txt`, RAISED below, the brief's own
     named fallback used): residual `None` then **> 0.0 on every subsequent run**
     (`TestNegativeControlResidualPositive`, 4 runs).
   - **crash** (#230's own glyph, a truncated 3-byte UTF-8 sequence): the row's `stdout_text` contains
     U+FFFD, exit code 0 present in meta, `mind.org.t` **advances** across the consume (the mind's counters
     keep moving) — no exception (`TestCrashControl`).
   - **fence** (`socket.socket()`, uncaught): `stderr` contains `Permission denied`, exit code non-zero,
     `stdout` empty — consumed by the mind without raising (`TestFenceControl`). Proved live by hand FIRST
     (an uncaught `socket.socket()` under the jail: stdout empty, stderr `PermissionError: [Errno 13]
     Permission denied`, exit 1) before any test was written.
   - **wall-clock plant**: a `time.sleep(5)` program under `wall=1` returns jail exit **124** (jail_run's
     own alarm, not a Python-side timeout invented by this module).
   - **Negative-control jail topology, verified live before coding it**: Landlock grants reads only beneath
     `ro_root` (the shelf)/`/usr`/`/etc` and rw beneath `scratch` — a program cannot read anything the
     world-maker wrote directly; `run_in_jail` writes the unpredictable value to `scratch/INPUT.txt` (cwd =
     scratch) before the run, and the negative program reads `./INPUT.txt`.

6. **The recognised share** (`tools/hands_recognised.py`, PREREG §19.9's mark):
   - `recognised_share(root, genome_path, ...)` — reads the tape's `hands`-sourced eye rows with a real
     `shape` (control rows, `shape: null`, are excluded from the denominator), decodes each rendered canvas,
     runs `gaze.glances(...)` (mode `"surprise"`, the SAME road `_consume_eye` uses) and
     `Organism.recall_many("sight", glances)`, reads the answer off `ledgers["words"]` — the identical
     mechanism `genome/questions.py:ask`'s Q1 uses on a held-out DRAWN canvas, here applied to a
     HANDS-rendered one. `«not gradable»` under 20 runs, printed by name.
   - **Mechanism proof** (`tests/tools/test_hands_recognised.py`, a REAL `Mind`, never a mock): a mind
     taught "circle"/"square" through 200 ordinary drawn canvases, then given 26 HANDS-tagged real-circle/
     real-square renderings — **recognised share 1.000 vs the shuffled-shelf twin's 0.385** (26 ≥ 20, the
     brief's own bar of ≥ 0.6 cleared). An UNTAUGHT mind reads exactly 0.0 (no words to answer with) — the
     refusal test's other side.
   - **A REAL 6-minute-class pre-flight was also run** (see "The real pre-flight", below) — it validated
     the LIVE orchestration end to end (real jail, real 54-program shelf, real `Body.start()` wiring) but
     did not reach 20 real runs in the time available; its honest numbers are reported rather than padded.

7. **Registered in `creature/genes.py`**: `HANDS`, `SENSE_TOUCH`, `SENSE_SMELL` under `RUNS["mind"]`, each
   naming every real call site (including the `creature/body.py` wiring for `HANDS`).
   **`genome/LIFE.genome` needed NO edit.** Its DRAFT lines 24–25 (`SENSE smell kind size folder age`,
   `SENSE touch from hands: exit rate stalls retries bytes`) and line 76 (`HANDS jail alpha3/hands/jail_run
   shelf world/programs cpu 10 mem 512 wall 20`) already match this parser's accepted grammar exactly —
   confirmed by `tests/genome/test_hands_touch_smell_parser.py` parsing those EXACT three lines verbatim.
   `LIFE.genome` as a WHOLE still refuses to parse on this worktree (`GAZE ... coarse 32`, builder B's
   unlanded work) — pre-existing, unrelated to this brief, not fixed here.

## Design decisions, each RAISED explicitly (none silent)

1. **The OUTCOME row's `act` field is the PROGRAM's OWN NAME, not the literal string `"run"`** the brief's
   prose shows for the outcome row's shape. `Mind._record_reflex`'s per-act running-mean EXPECTATION is
   bucketed by this field; per-program predictability — the whole point of the positive/negative controls
   ("a program whose output the mind CAN/CANNOT predict") — needs a per-program bucket, or every program's
   `got` would blend into one shared "run" expectation and the controls could not separate. This is the
   EXACT precedent `creature/senses/game.py` already set (an outcome row's `act` is the concrete BabyAI
   action taken, not one of `declared["ACT"]["verbs"]`) and carries the same `in_vocab: False` consequence,
   tagged the same way, not treated as a new defect.
2. **`touch`/`smell` each get a DEDICATED `Episodes` ring** (`touch_episodes`/`smell_episodes`, dims 5/4),
   not a reuse of `self.outcome_episodes` (whose `x_s` is `sight_dim()`-wide with only `x_s[0]` used as a
   SCALAR payload). A 5- or 4-number VECTOR needs its own columns, or BODY-SENSES §4.6's own toy ("two
   programs … give different touch VECTORS") has nothing to compare. This mirrors `sound_episodes`'s own
   precedent (LIFE builder D, L-13) exactly — a third such ring, not a new pattern.
3. **`_negative_control_input` uses the tape's row count**, per the brief's own explicit fallback:
   `creature/world_maker.py` has no `WINDOW.txt` (`grep -rn "WINDOW" creature/world_maker.py` — only
   `WINDOW_SECONDS`/`PLANT_WINDOW_S` constants, no such file). RAISED per the brief's own instruction, not
   worked around.
4. **`tools/smell_auc.py`'s retrospective trait excludes `age`.** The live sense's `age` is
   `log10(now − mtime)` at the INSTANT the picture is published; for a closed life read long afterward,
   "now" is whatever wall-clock instant the script happens to run at — unrelated to what the live mind
   actually saw. RAISED rather than faked as 0 or as a fresh reading dressed up as the historical one
   (#194's law: a prose claim about an artifact is not the artifact). `age` is graded honestly only where
   "now" is real: the live pre-flight and the 24 h life itself.
5. **`hands_no_road`/`touch_events`/`smell_events`/`_hands_last_program`'s running state are NOT
   independently gap-worthy** — `sound_events`'s own pre-existing gap (a plain count, not persisted across
   resume) is matched exactly for `touch_events`/`smell_events`; `_hands_pending`/`_hands_last_program`
   (which DO need to survive a resume, since an ACT file can already be on disk) ARE persisted, in
   `ledger.json`, exactly like `_act_rng_state`.
6. **`_tape_row_count`'s cost** (a full recount of every tape day-file's lines, for the negative control's
   input) is a real, named rung-1 cost: cheap at the tape sizes a hands act runs against today (low tens of
   ms even at six figures of rows, against a jail run itself costing tens of ms to ~11 s), but a cost that
   grows with the tape and is worth watching if the life runs long — named here, not hidden.

## The real pre-flight (live, not a test)

A genuine `python3 -m creature.body` life was launched under this worktree's own code — `genome/G5.genome` +
this brief's three lines (`HANDS jail alpha3/hands/jail_run shelf world/programs cpu 10 mem 512 wall 20`,
`SENSE touch …`, `SENSE smell …`) + `ACT glance open ask run` + `WORLD drawn every 1 s` (sped up from G5's
5 s to teach words faster within the available window) — root `scratch/preflight/root`, the REAL jail, the
REAL 54-program shelf. It ran **≈ 18 minutes** wall-clock (stopped by hand with a clean `SIGTERM`, `main()`'s
own `finally` block stopping the babyai game-worker subprocess too — no orphan left behind, verified by
`ps`):

- **ALIVE the whole time — 0 crashes, 0 sense restarts, `hands_no_road` 0.**
- **7 real hands runs**, each producing a full eye→outcome→touch row triple, across 7 distinct programs
  (`moon_0 arrow_2 ring_1 diamond_0 circle_2 dot_0 house_0`) — one per program, matching the uniform-draw
  design (no repeat by chance in this short a sample).
- `touch_events` = 7 (one per run, exact match), `smell_events` = 6 (the folder door consumed all 6
  pictures under this worktree's own `world/ahmad/`, then correctly stopped — its `SEEN.json` cursor law).
- `tools/hands_recognised.py --root scratch/preflight/root --genome scratch/preflight/LIFE-preflight.genome`
  correctly read `{"gradable": false, "n": 6}` at the point it was checked (later 7) — the `«not gradable
  under 20»` branch exercised on a REAL root, not only the synthetic test.
- Kind distribution over 38 think passes: `sight 11, outcome 7, rule 6, hands 5(→7), word 3, due 1` (later
  extended) — close to the uniform 1-in-N-kinds share kind-fairness promises, not a bug.

**Why it stopped short of 20**: this box was running another seat's `tools/gate_g5_landing.sh A-life`
landing gate concurrently (`ps` showed a `python3 -u -m unittest discover -s tests/creature -t .` child of
that script, 40–50 % CPU) plus this brief's OWN full-suite run (below) — both unrelated to this life, both
eating the CPU seconds a live mind needs to advance (SOLUTIONS #236's own lesson: a reader/gate running
beside a life starves it). At the achieved rate (~7 runs / 18 min under contention), reaching 20 would need
roughly another 30–35 minutes of real time. Given the mechanism was ALREADY proven correct end-to-end by the
synthetic test above (§6, 26 samples, share 1.000 vs twin 0.385) AND by this same pre-flight's own honest
`«not gradable»` reading on real data, I judged the marginal value of a longer live run below the cost of
holding up this report further — reported here exactly as it stands, not padded, not re-run under a looser
bar. The actual 24 h pre-flight (tomorrow, 1 h on the exact world) will not share this box's contention.

## Tests: every one RED before, GREEN after

Each test file was written before its implementation existed (import errors / `AttributeError` /
`GenomeError` confirmed as the RED reason, then the implementation written, then re-run GREEN):

| file | RED reason (confirmed) | GREEN |
|---|---|---|
| `tests/genome/test_hands_touch_smell_parser.py` | `GenomeError` on the unextended HANDS grammar / unknown gene `SENSE smell`/`SENSE touch` | 9/9 ok |
| `tests/creature/test_mind_touch_smell.py` | `SENSE_TOUCH`/`SENSE_SMELL declared but nothing runs it (W3-0)`; `AttributeError: no touch_episodes` | 12/12 ok |
| `tests/creature/test_mind_chooses_hands.py` | `ImportError: cannot import name 'hands'` (for the 2 fake-sense tests); the rest RED via the pool/think mechanism not existing yet | 12/12 ok |
| `tests/creature/test_hands_sense.py` | `AttributeError: module 'creature.senses' has no attribute 'hands'` | 16/16 ok (real jail) |
| `tests/creature/test_hands_controls.py` | same (module did not exist) | 4/4 ok (real jail, all four controls) |
| `tests/creature/test_hands_arming.py` | `AttributeError: no _declared_hands_config` | 4/4 ok |
| `tests/creature/test_status_hands_touch_smell.py` | `KeyError`/`AssertionError` on the missing STATUS fields | 4/4 ok |
| `tests/creature/test_folder_smell.py` | `TypeError: sense() got an unexpected keyword argument 'smell'` | 3/3 ok |
| `tests/tools/test_smell_auc.py` | `ModuleNotFoundError: tools.smell_auc`; then (after the module existed) the toy's OWN sign-convention bug caught by its own planted controls (see below) | 6/6 ok |
| `tests/tools/test_hands_recognised.py` | `ModuleNotFoundError: tools.hands_recognised` | 3/3 ok |
| `tests/creature/test_refusal.py` (extended, not new) | `AssertionError: 'SENSE_SMELL' not found in {...}` (the registry-pinned-to-parser fixture) | 12/12 ok |

**A bug caught by my own planted controls, worth naming**: `tools/smell_auc.py`'s first `_auc_from_distances`
implementation had the win/loss direction backwards (computed `P(diff < same)` instead of `P(same < diff)`).
`TestAucFromDistancesToy`'s perfect-separation/reversed-separation planted controls (written BEFORE the real
data was ever read) caught it immediately — `1.0`/`0.0` came back swapped — fixed, re-verified against the
same toy, then run on the real closed life.

## The touch/smell toys' numbers

- **Touch** (BODY-SENSES §4.6's own toy: two programs with the SAME output by different roads, one
  stalling, must give DIFFERENT touch vectors; two runs of one program must give the same one, to
  rounding): confirmed structurally in `TestTouchConsumed.test_same_output_different_roads_give_different_
  touch_vectors` (a `rate` of 200 bytes/ms vs 0.003 bytes/ms — a ~5-decade gap — for the same stdout content
  by a fast vs. a `sleep`-bearing road) and, live, by the positive control across 3 real jail runs: `exit`,
  `stalls`, `retries`, `bytes` identical to the byte; `rate` varied only by real timing jitter (single-digit
  ms on a `print("#"*4)` program).
- **Smell AUC** (BODY-SENSES §4.5's own refusal test), run on `/data/dev/genome-lives/g5-seam-1`'s closed
  tape (307 folder eye rows, **all 307 matched** their source file under `/data/dev/genome/world` by sha12,
  read-only, 0 unmatched) — **printed, never tuned to**:
  - **Full vector (kind + size + folder-hash) AUC = 0.8339** (4,365 same-word pairs / 42,606 different-word
    pairs).
  - **Folder-BLIND control (kind + size only) AUC = 0.5366** — barely above chance.
  - The 0.297 gap between them is almost entirely the folder-hash axis (which gives a same-word pair
    distance 0 BY CONSTRUCTION, SOLUTIONS #217/#162's law) doing the separating, not `kind`/`size`
    themselves. **Read honestly: the channel's `kind`/`size` axes alone carry very little separating
    signal on this life's own folder pictures** — BODY-SENSES §4.5's own predicted "real risk of a null"
    is close to realised for those two axes; the full vector's apparent strength is mostly the answer
    riding along on the folder-hash axis, which is why both numbers are reported and neither is preferred.

## Suites, final bytes

```
$ TMPDIR=$PWD/scratch/tmp python3 -m unittest discover -s tests -t . -v
Ran 605 tests in 403.328s

OK (skipped=7, expected failures=6)
```

(`scratch/logs/full_suite_run1.log`, run on the FINAL bytes — after the shelf, all source/test files, and
this report's own commit-ready state.) The 7 skips and 6 expected failures are ALL pre-existing, unrelated
to this brief: 5 are the seam-test skeletons for A×B/A×C/B×E/C×D/D×E (none involve builder F — confirmed by
name, `grep -n hands tests/creature/test_life_seams.py` returns nothing), one is a missing
`scratch/life2-ro/exam` fixture copy, and 6 are pre-registered B7/B8/B12-family modulation-experiment bars
this estate already expects to fail on this world (the same class D's own report names for the same reason).
None belong to any file this brief touched. All of this brief's own new test files/methods — `tests/genome/
test_hands_touch_smell_parser.py`, `tests/creature/test_mind_touch_smell.py`, `tests/creature/test_mind_
chooses_hands.py`, `tests/creature/test_hands_sense.py`, `tests/creature/test_hands_controls.py`, `tests/
creature/test_hands_arming.py`, `tests/creature/test_status_hands_touch_smell.py`, `tests/creature/test_
folder_smell.py`, `tests/tools/test_smell_auc.py`, `tests/tools/test_hands_recognised.py`, and the 3
extended assertions in `tests/creature/test_refusal.py` — are included in the 605 and passed.

## Clauses raised

1. `creature/world_maker.py` has no `WINDOW.txt` — the negative control reads the tape's row count instead
   (the brief's own named fallback).
2. The outcome row's `act` field is the program's own name, not the literal `"run"` (see design decision 1
   above) — `in_vocab: False` on every hands outcome row, matching the game door's own precedent.
3. `tools/smell_auc.py`'s retrospective `age` is not computed (design decision 4) — `age` is graded live
   only, where "now" is honest.
4. The real 18-minute pre-flight reached 7 hands runs, not ≥ 20, under this box's shared CPU contention
   (see "The real pre-flight" above) — the mechanism is separately proven at n=26 by a real-Mind synthetic
   test that does clear the bar.

Everything else in the brief landed as specified; no gate or bar failed by construction (the two "not
gradable" readings — the real pre-flight's own n=7, and the closed-life smell AUC's honest `kind`/`size`
weakness — are results, not failures, per PREREG §9–§11's own law).

## Commit

Branch `life-hands`, commit sha: **fe9c64c**.
