# Review before rung 3 — the brain organ in the FULL organism

Reviewer: Claude (Opus 5.5, independent reviewer, read-only), written 2026-09-28 21:40 +0400.
Commit reviewed: `brain-organ` **fac461d** (worktree `/data/dev/genome-wt-organ`), base `master` 1ae2d42.
Method: I read the code only. I ran no suite, replay or life.

## What I read
- `git diff master..brain-organ` of `creature/mind.py`, `creature/body.py`, `creature/genes.py`, `creature/replay.py` and `genome/machinery.py`.
- `genome/brain.py`: the class, `learn`, `ask`, `summary`, `save` and `load`.
- `creature/senses/scene.py`, read whole.
- `creature/think_thread.py`: `freeze_inputs` and `freeze_recall_view`.
- `creature/mind.py`:
  - `_maybe_think_threaded` and `_think_apply_pending`;
  - `_maybe_adopt_evolve_proposal` and `_maybe_sleep`;
  - `consume`, the head of `_consume_eye` and the sight-only QUESTION trigger;
  - `_maybe_ask` and `_latest_tape_moment_for_word`;
  - `snapshot`, `close` and `resume`.
- `creature/body.py`: `SenseThread`, `_publish`, `start`, `_mind_loop`, `_handle_mind_crash`, `_status_loop`, `_build_status` and `stop`.
- `tools/evolve.py`: `main`, `advance_shadow`, `run_judging_round` and `build_twin`.
- `creature/senses/evolve.py`: `sense` and `stop_worker`.
- `creature/world_maker.py`: `_answer_one_question`.
- `creature/replay.py`: `run_replay`, `compare` and `read_mind_journal`.
- `tools/brain/`: `grade_life.py` (`Life`, `SetCtx`, `meeting_seen`), `journal_diff.py` and `rung2_replays.sh`. I grepped `parity.py`, `null_identity.py` and `seed_genome.py` for their file reads.
- The lives tooling: `tools/lives/run_brain_life_full.sh`, `launch_brain.sh`, `close_brain.sh` and `deploy/creature-brain@.service`.
- The genomes: `genome/brain/lives/BRAIN-FULL-20261102.genome`, diffed against BRAIN-LEAN-20261102 and BRAIN-FULL-PREFLIGHT.

## What I did NOT read
- The PREREG and INTERFACE documents and the three HANDBACK files. I checked the code against the questions in the brief, not against the signed text.
- `creature/organs_road.py` beyond its moment regex.
- `grade_life.py`'s grading functions: `offline_answers`, `grade_m5`, `grade_m4a`, `pair` and `grade`.
- `parity.py`, `null_identity.py` and `seed_genome.py`, apart from the grep.
- These senses: `game`, `read`, `lexicon`, `web`, `hands`, `sit` and `grade`.
- `creature/exam.py`, apart from a grep.
- The `brain/scene` learner internals.

---

## BLOCKERS

### B1. The rung-3 replay gates will FAIL falsely because the live mind stops with rows left on its tape. This covers identity, the twin, the «disturbance» journal_diff and «blind».
- **Where:**
  - `creature/body.py:310-321`: `_mind_loop` leaves at `stop_event` and does not drain `self.q`.
  - `creature/body.py:500-512`: `stop()` sets `stop_event` first and only then stops and joins the sense threads, which may still publish during the join.
  - `creature/replay.py:141-156`: a replay consumes EVERY row of the tape, then calls `close()`.
  - `tools/brain/journal_diff.py:37-51`: the verdict requires equal row counts and an equal last hash.
  - `tools/brain/rung2_replays.sh:16-18,34`: the recipe to be copied for rung 3.
- **Scenario:**
  - In the full organism the maker (every 5 s), the shelf (20 s), the game (30 s), body (60 s), grade and the evolve proposals keep publishing after the scene world has ENDED.
  - At `close_brain.sh` the mind thread exits with whatever is in the queue unconsumed. A sense can also publish between `stop_event.set()` and its own join. Those rows are on the tape beyond `state/ledger.json` `last_seq`.
  - A replay run with the rung-2 recipe (`--tape $R/tape --closed`) consumes them. The replay journal then has extra rows at the tail, and `Mind.close()` lands a pending think at a different last eye row (`mind.py:3579-3580` uses `_cur_seq`).
  - Results:
    - identity `--against` reports `<missing from --against>`;
    - journal_diff (live vs twin replay) prints `DIFFERENT`, with the last hash NOT equal: a false «the brain disturbed the organism»;
    - twin vs blind is unaffected, since both are replays of the same tape.
- **Why rung 2 did not show it:** the lean genome has no drawn `WORLD` line, so the maker is not armed (`body.py:_maker_should_arm`). Every lean sense was idle at the stop, so there was no tail.
- **Certainty:**
  - [Certain] that the code leaves the tail and that a replay consumes it.
  - [Likely] that a tail exists at a given stop. The mind is busy on maker, shelf and game canvases for a good share of the time, and publishing continues through the join window.
- **What settles it:** after the close, compare `state/ledger.json` `last_seq` with the maximum `seq` in `tape/*.jsonl`. Any gap is the tail.
- **Smallest fix:**
  - For every rung-3 replay, build a CUT tape directory: the rows with `seq <= ledger.last_seq`. SOLUTIONS #239 already records «the reader cuts at the lived seq».
  - The cut directory needs a `payload` symlink to the real payload directory, because `run_replay` reads `tape_root / "payload"`.
  - Always pass `--closed`, as rung 2 did. The live `close()` always runs; if no think was pending, both sides add zero rows.
  - Feed the cut replay's journals to journal_diff.

### B2. A life that crosses 00:00 UTC (04:00 +04) cannot be identity-checked with the rung-2 recipe.
- **Where:**
  - `tools/brain/rung2_replays.sh:16` runs `J=$(ls $R/journal/*.jsonl | head -1)`, which takes the first day file only.
  - `creature/replay.py:93-99,222-225` (`read_mind_journal` → `_read_jsonl`) takes a FILE only. It calls `path.read_text()`, so a directory raises IsADirectoryError.
- **Scenario:** a launch at about 22:00 +04 crosses 04:00 +04 if the 10,000-scene full life takes more than about 6 h. The full organism costs about 0.5 s or more per canvas at thousands of cells, and it has sittings and EVOLVE besides, so this is plausible. `--against` then holds day 1 only, and the replay reports `<missing from --against>` at the first day-2 seq: a false FAIL.
- **Also crosses cleanly:** `read_tape`, `grade_life.read_journal`, `parity.py`, `null_identity.py`, `journal_diff.rows` and `run_replay` with a tape DIRECTORY all glob every day file. The monitor in `run_brain_life_full.sh` globs every day too.
- **Certainty:** [Certain] for the code. Whether the crossing happens depends on the launch time.
- **Smallest fix:** concatenate the mind rows of every journal day file, in order, into one file and pass that to `--against`. Or teach `read_mind_journal` to accept a directory, as `run_replay` now does for the tape.

---

## RISKS (ranked)

### R1. EVOLVE runs a SECOND full brain and organism over the whole scene tape, and two more at every judging round.
- **Where:**
  - `tools/evolve.py:511-512` with `232-245`: the shadow `Mind` built from the birth genome declares BRAIN, so it learns every scene canvas and answers every ask, and it snapshots, including the ~42 MB `brain.npz`, after every 30 s poll that consumed rows.
  - `tools/evolve.py:380-395`: every 6 h two twins replay the last 2 h of tape with brains, one at a time.
  - `tools/evolve.py:524`: the first round is REFUSED at once, because it finds no checkpoint 2 h old. The first real round fires 6 h later.
- **Effect:**
  - About 2× the life's CPU (3× during a round), on a box already running three organisms.
  - The live mind is slowed only by contention. The scene world is paced by the live backlog alone.
  - Disk: `evolve/shadow/journal` duplicates the whole journal, and checkpoints every 2 h copy `state/` including the brain.
  - The worker's stderr goes to DEVNULL (`creature/senses/evolve.py:53`), so a shadow crash is silent.
  - None of this touches the life's own `journal/`: `grade_life` reads `root/journal/*.jsonl` only (`grade_life.py:117-121`).
- **Watch:** `/proc/loadavg` and `ms_per_canvas_1min` in `SERIES.tsv`, and `evolve/PROPOSAL-*.json` `shadow_lag_rows`.
- **Mitigation, if wanted for this rung:** `--blind brain` for the shadow and twins cannot be passed today, so the practical choice is to declare EVOLVE's cost in the PREREG.

### R2. A cross-thread read of the brain and `pending_asks` from the STATUS thread can kill that thread silently, and then the run script can never see ENDED.
- **Where:**
  - `creature/body.py:334-338`: `_status_loop` has no try/except.
  - `creature/body.py:484` calls `mind.brain_status()` from the status thread.
  - `creature/mind.py:1515-1521` iterates `self.pending_asks.values()`. The mind thread inserts and pops keys there on every sitting canvas.
  - `genome/brain.py:376-380` `summary()` iterates `self.episodes.values()` and runs `L.mature_words()`, which indexes `meetings[j]` over `words`, while the mind thread may be inside `learn` or `calibrate`.
- **Effect:**
  - A `RuntimeError: dictionary changed size during iteration`, or an IndexError, ends the status thread.
  - STATUS.json freezes while the unit stays `active`, so `run_brain_life_full.sh:22-44` never reads `ended True`. It runs to MAX and closes with verdict `TIME-LIMIT`.
  - The life's data stays gradable.
- **Probability:** low per write, since each iteration is short. The earlier status fields share the class and have been tolerated across long lives.
- **Watch:** STATUS.json mtime going stale while the unit is `active`.
- **Fix:** wrap the `brain` field in try/except in `_build_status`, returning `{"error": repr(e)}`. Or snapshot `len(...)` under a lock the mind holds while it mutates.

### R3. The multi-file snapshot now has a longer torn window, and the brain can end up AHEAD of `ledger.last_seq` without anyone noticing.
- **Where:** `creature/mind.py:3459-3553`. The order is:
  1. organism replaced;
  2. `build_ledgers`;
  3. the brain saved (~42 MB npz plus a hash over it) and its two files replaced;
  4. ledger replaced.
- **Scenario:** a SIGKILL or power loss after step 3 and before step 4. On resume, the tape rows after the OLD `last_seq` are consumed again, and `brain.learn` is called a second time on scenes it already holds (`seen` gets duplicates). The hash matches, so `load` accepts it.
  - The organism has the same pre-existing class. The brain save lengthens the window to about a second per snapshot, one snapshot every 100 canvases.
  - A crash BETWEEN `brain.npz` and `brain.json` is loud instead: `load` raises BrainError on the hash, and then 5 failed starts leave the unit FAILED.
- **Watch:** `brain.learned` on STATUS greater than the count of distinct train moments on the tape.
- **Fix, one line:** at resume, compare `mind.brain.n_learned` with `ledger["asks"]["learned"]` and mark `brain_restored = "MISMATCH"`. The ledger already carries `learned`.

### R4. The scene sense republishes a whole moment after a mid-moment restart, which duplicates ear rows and asks.
- **Where:** `creature/senses/scene.py:372-383,402-411`. The cursor advances only after all rows and the truth file are written.
- **Scenario:** a `sense_restart` (any exception in render or publish), or a process kill, between an ear row or ask row and its eye row.
  - The moment is published again under new seqs, and the first attempt's ears stay in `pending_words[moment]`. The brain learns `[w1, w2, w1, w2]`.
  - A duplicated ask is answered twice. That part is loud: `grade_life.py:182-183` raises `answered more than once`.
- **Watch:** `sense_restarts` on SERIES.tsv, and more `ear` rows than distinct (moment, word) pairs for any `sc…t…` moment.

### R5. The close can overrun the stop timeout, or race the mind thread.
- **Where:** `creature/body.py:506-521`. About 11 sense threads are joined one after another at 5 s each, then the mind, ask and exam threads at 5 s each, then `mind.close()`: the think apply, the snapshot and the brain save.
- **The race:** if the mind thread is mid-consume past its 5 s join (a SLEEP replaying 200 episodes at many cells), `close()`→`snapshot()` runs on the main thread while the mind thread still mutates the org and brain. The result is a torn final state or an exception out of `stop()`.
  - The 120 s stop timeout is unlikely to be reached, since the sense stops honour the event, but it is not bounded by construction.
  - With the default KillMode, systemd sends SIGTERM to the game and evolve workers at the same moment.
- **Watch:** the `journal` `{"event":"stop"}` row is present, and `CLOSE.log` shows no traceback.

### R6. QUESTION wants that cite `sc…` moments pile up in `ask/out/`.
- **Where:** `creature/mind.py:2105-2126`. Sitting canvases are sight-only, so a wordless cell seen twice opens a `what-is` with `[moment]`. `world_maker.py:137-147` rescans and reads EVERY unanswered `q-*.json` at every 5 s tick. A `sc…` moment never matches `w(\d{4})i(\d{6})t(\d{9})`, so these files are never renamed.
- **Effect:** CPU and IO that grow with the number of such cells. There is no crash.

### R7. The think-thread copy cost is multiplied by the scene rate.
- **Where:** `creature/think_thread.py:133`. `copy.deepcopy(mind.episodes)` copies a FAST ring of 20,000 episodes (tens of MB) for every `word`/`self` think, which runs every 10 canvases.
- **Effect:** at the scene world's maximum rate this runs about every 3–5 s, where Alpha 4 ran it about every minute. It costs the mind thread's time, and it does not touch the brain.

---

## CLEARED (the ten questions)

1. **Think thread and brain.**
   - `freeze_inputs` (`creature/think_thread.py:127-146`) copies the sliced organism, `episodes`, the park, `moment_word`, `declared` (shared) and a fresh rng. It never touches `mind.brain` or `pending_asks`.
   - Only `word`/`self` kinds go to the thread (`mind.py:3214-3235`). The apply and every journal row run on the mind thread (`mind.py:3243-3276`).
   - No brain or answer row is written from the think thread. The per-ask read-only assert (`mind.py:1466-1469`) compares `org.row_hash()`, which the think thread cannot move.
2. **EVOLVE adoption.**
   - `_maybe_adopt_evolve_proposal` (`mind.py:2225-2240`) swaps only `self.genome`/`self.org.g` and two cached ints. It never rebuilds the Mind, so `self.brain` survives an adoption.
   - Every BOUNDS pattern is anchored `^(GENE\s+…)` with MULTILINE on BIRTH, DELTA, KWTA, BUDGET, SLEEP, THINK, PRUNE, MERGE, ABSTAIN, CURIOSITY, SCALE and PARK (`creature/genes.py:303-380`). None can match a `WORLD scene` or `BRAIN` line.
   - A resume after an adoption uses `GENOME.v<n>.genome`. That text is derived from the checkpoint's birth text, so it keeps both lines, and `Brain.load`'s cfg check passes.
   - The shadow and twins write under `$ROOT/evolve/…`, never into `root/journal` or `root/state`. The cost is R1.
3. **Scene back-pressure.**
   - `while backlog() >= k` (`scene.py:397-403`) checks `stop_event` before and after every 5 ms wait, so it cannot hang a stop.
   - The queue is bounded by k plus one moment's rows plus the other senses' inflow. The scene cannot starve unless the mind stays slower than the non-scene inflow, about 1 row/s.
   - The cursor is written tmp→replace (`scene.py:357-362`). The restart case is R4.
4. **Row ordering.**
   - Binding is by moment key in every map: `pending`/`pending_words` at `mind.py:779-789` and `1833-1834`, `pending_asks` at `mind.py:1422` and `1431`. A foreign row between an ear and its eye changes nothing.
   - Scene moments (`sc<ws>t…`, `sc<ws>q-…`) cannot collide with the maker's `w…i…t…` format.
   - Learning is gated by `brain.hears(meta.source)` (`genome/brain.py:190-191`). A missing source returns False and the canvas is skipped silently.
5. **A sitting canvas as an ordinary canvas.**
   - No organism road reads `pending_asks`; the only readers are `_brain_canvas`, snapshot and status.
   - The only moment regexes are `world_maker.py:120` (fullmatch; a non-match is skipped) and `organs_road.py:33`, which serves the twin's `why`.
   - `creature/exam.py` parses no moment string.
   - A `sc…q-…` moment only produces the unanswerable questions of R6.
6. **Snapshot and resume.**
   - BRAIN absent while `brain.npz` exists: `mind.brain` is None and the files are ignored (`mind.py:3663`).
   - BRAIN present with no files: a newborn brain, with `brain_restored False` on STATUS.
   - A torn npz/json pair is refused by the hash (`genome/brain.py:420-422`). The silent case is R3.
7. **The close.** It is replay-reproducible only on a cut tape; see B1. The timing is R5.
8. **The graders.**
   - (a) Only the scene sense publishes `ask` rows (grep: `creature/senses/scene.py:222,277,304,309`). The journal kinds the grader filters on have one writer each; grep over `creature/`, `genome/` and `tools/evolve.py` found only these:
     - `"kind": "brain"` at `mind.py:1439`, `1449` and `1451`;
     - `"kind": "answer"` at `mind.py:1481`.
     
     `Life` also filters tape rows by `source == "scene"` (`grade_life.py:153`).
   - (b) Every held answer carries `fix`/`hyps` from `view`, computed before the brain call (`mind.py:1454-1459,1474-1475`), refused or not.
   - (c) `meeting_seen` reads `kind: "brain"` learn rows by `moment`, and those carry `fix` (`mind.py:1447-1450`).
   - (d) Not checked; see below.
   - (e) Body events carry `seq: None` (`body.py:210`) and are dropped by `journal_diff`. Think rows carry the triggering boundary's tape seq and `launched_at`, never a clock. SELF's backlog skip reads the tape's `body` rows. The only live-vs-replay difference found is the tail (B1).
9. **Nothing under `creature/` or `genome/` reads `truth/`.** The hits are writers only:
   - `creature/senses/scene.py:381-383` (writes `truth/scene/<seq>.json`);
   - `creature/world_maker.py:86,103` (writes `truth/` and `truth/voice`).
   
   Everything else is comments (`genome/brain.py:21`, `genome/voice.py:121`, `creature/senses/chat.py:10`).
10. **The day boundary.**
    - The only single-file reader is `tools/brain/rung2_replays.sh:16` (B2), and `creature/replay.py --against` accepts one file only.
    - Everything else reads every day file: `read_tape`, `grade_life.read_journal`, `parity.py:22`, `null_identity.py:28`, `journal_diff.py:20`, `run_replay` with a tape directory, and the monitor in `run_brain_life_full.sh`.

- **Also cleared: the exam thread and the brain files.** `creature/exam.py` opens only `state/organism.npz` and `ledger.json` (`exam.py:33`, `117-123`), and ledger reads are wrapped in try/except. It never loads `brain.npz`, so the torn brain pair of R3 cannot reach the exam thread.
- **Also cleared: SURPRISE does not move fixations.** `genome/gaze.py:120,254` call `gaze_sequence(..., predicted=None)` whatever `predicted` is; `predicted` only fills `residual` (`gaze.py:185-192,266`). The full genome's GAZE line is the lean one's. So the brain's input (`glance["fix"]` and the features) is not a function of the organism's SURPRISE state, and `meeting_seen`'s fallback look with `predicted=None` gives the same fixations.

## NOT CHECKED
- 8(d): the forced reading and `pair()` in `grade_life.py`. I did not read the grading functions.
- The game, read, lexicon, web, hands, sit and grade senses under a flood of scene canvases. In particular, whether the web door opens (STAGE 4 by READY) during rung 3.
- The cost of `org.row_hash()` twice per ask at the full organism's cell count.
- The calibrate time at 5,000 and 10,000 scenes.
- The HANDBACK RAISED lists and the PREREG and INTERFACE text.
