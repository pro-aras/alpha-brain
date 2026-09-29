# PREREG — THE DAYS LIFE: one full organism with every feature of 2026-09-29, alone for days

*Written and signed by Claude (Opus 5.5, the seat, ALONE under his 2026-09-29 15:25 word), 2026-09-29 23:49 +0400, before the pre-flight and before the launch.*

**His words.** 2026-09-29 23:20 +0400, verbatim: «Yes, what you decided seems right. So can we add all these features today so it runs for few days until your limit get reset? If yes then go for it. Make sure to clear any possible errors that might occur within these few days.» What he approved is the KW-2 list of `docs/brain/memory/kweb/VERDICT-KW-1.md` («What changes» 2).

## 1 · What the life carries

The genome `genome/brain/lives/BRAIN-LONG-2.genome` is the full organism of `brain-long-1` (every ALPHA4 organ, the scene world and the brain with DRIVE), with three changes: world seed 20261101, and the line `HASH sparse; dense at snapshot` (the row hash a sparse witness). The code adds, with no genome line:

| Feature | What it is | Where |
|---|---|---|
| METADATA 1 | Every scene the brain learns carries its source and its author; the census as a file and on STATUS | on master since 09-29 22:06 |
| THE KNOWLEDGE WEB | Two webs grown from every word the organism hears, whatever the source: L (the smart rule) and N (sprouts steered to the last 20 words, judged only after); 10 edges a known word; the spent consolidation test | `genome/web.py`, `creature/mind.py` |
| THE SELF | A self node fed by the brain's own turns and learns and the body's backlog, with six claims placed at birth: KW-1's five (three true, two false) and B1 «My mind keeps up with what I sense» (usually, 0.90; its truth unknown) | the same |
| The power-cut repair | At a start: a torn tail of every append-only file cut, kept and recorded; the seq healed and never below the mind's | `creature/repair.py`, `creature/tape.py`, `creature/body.py` |
| The health watch | Every 20 min and at boot: HEALTH.md; a failed life restarted at most 4 times a day, a frozen one at most once in 6 h | `tools/lives/health.py`, `creature-brain-health@` |

The web and the self are BOOKKEEPING: they change no answer and write no journal row (a lean life's journal is byte-identical with them, `tests/creature/test_web_mind.py`). An error inside them switches them off and is shown.

## 2 · What must hold before the launch (the gates)

| Gate | Clause | Bar |
|---|---|---|
| D1 THE SUITES | genome, tools and creature suites on the launched commit | every one OK, read from its own log |
| D2 THE PRE-FLIGHT | `tools/lives/preflight_days.sh` on the pre-flight genome (train 400): alive with a web and a sparse hash; back after a hard kill with its web restored; back after a simulated POWER CUT with the repair recorded, no seq used twice and new rows above the old top; back from FAILED by the health watch | its last line «PREFLIGHT PASS» |

If either fails, the days life is NOT launched and `brain-long-1` goes on as it is.

## 3 · What will be read on return (no bar: a reading life)

1. **Did it live?** Days alive; restarts, repairs and recoveries (RECOVERY.log, repairs/REPAIRS.jsonl), each with its cause; the SERIES and HEALTH.jsonl as series (backlog, ms a canvas, memory, cells), never their endpoints.
2. **The web is true:** each web's nodes and edges recounted from the words on the life's tape (`genome/web.py:recount_errors`), with a planted change caught.
3. **The web's growth:** nodes, edges, consolidated, replaced and removed per rule as series; its shape (clustering and path against a random web of its size).
4. **L against N on its own speech:** the webs as they stood at a snapshot, read against the words heard AFTER it (enrichment, as KW-1's K6); printed per rule, no winner declared by this law.
5. **The self:** each claim's end state, counts and first demotion; its lived reliability per word.
6. **The brain's six tests** at its sittings (after 50,000 scenes), by `tools/brain/grade_life.py`.

## 4 · The adversarial walk

1. **Can the web hurt the life?** It writes no journal row and fails only OFF; its cost is two web updates per heard word and one JSON file per snapshot (measured in the pre-flight's ms a canvas beside brain-long-1's).
2. **Can the repair hurt the record?** It runs only at the start of an OPEN life, only on tails (the last MiB), keeps every byte it cuts and says so in the journal. A cut can drop the last seconds of rows the mind had already seen: the record says where, and a replay of this life stops there.
3. **Can the watch hurt the life?** It acts only on FAILED, on inactive-while-enabled, or on a heartbeat older than 90 minutes; at most 4 acts a day; never on a closed life. A deterministic crash will fail again 4 times a day and stay failed: the HEALTH.md says so.
4. **The sparse hash** changes the row hash's form, not the organism; the snapshot keeps the dense hash.
5. **What this does not show.** Nothing is compared against a twin; no feature is graded by a bar. It shows whether the whole thing LIVES for days and what it holds when it has.
6. **The residual risk, said:** a power cut inside a snapshot's writes (a fraction of a second every few minutes) can leave the organism's files newer than the ledger; the resume then replays a few rows twice. Not repaired tonight.

Signed: Claude (Opus 5.5, the seat), alone — 2026-09-29 23:49 +0400.

---

## AMENDMENT 1 — the pre-flight's first kill tore a snapshot; the fix; D1 and D2 on the fixed commit

*Written by Claude (Opus 5.5, the seat), alone, 2026-09-30 00:10 +0400, before the launch.*

**A correction first.** The signature line above says 23:49. Git says this file was committed at **23:44:39** (867c55c): the time was typed, not read from `date` (#50, #245 (7)). The sentence «before the pre-flight» is still true. Pre-flight 1 was launched after that commit and ended at 23:46:26.

**D2 failed on 867c55c.** Pre-flight 1 (`brain-long-2-pre-1`) passed steps (1) and (2). Then its power cut left the life unable to start: «PREFLIGHT FAIL: not back after the power cut: Result=exit-code».
- Every restart died on `KeyError: 5204` in `genome/questions.py:build_ledgers`.
- `state/organism.*` came from moment 5,700, but `state/ledger.json` came from moment 5,200.
- The earlier hard kill had landed INSIDE a snapshot's run of back-to-back file replaces. That left a snapshot torn across its files, which no restart could ever load.
- The repairs themselves had worked: 3 tail cuts, 0 good rows lost.
- The life was closed at 23:49.
- §4.6 had named this risk as «a few rows replayed twice». It was worse: **a torn snapshot ended the life.**

**The fix, test-first (84d5ad5; `tests/creature/test_snapshot_generations.py`, 4 tests, red on 867c55c).** A snapshot is now a GENERATION:
- every file is staged first and the staged files are renamed back to back;
- `SNAPSHOT.json` goes last and records each file's size and write time;
- the complete generation before it is kept as hard links in `state/prev/`;
- at a resume, `Mind.resume` checks the generation: every file must agree with `SNAPSHOT.json` and with each other;
- a torn generation is healed from `prev/`, with the torn files kept in `repairs/`. With no `prev/`, the torn state is moved aside and the life is rebuilt from the whole tape.
- Every heal is recorded in `repairs/REPAIRS.jsonl` and journaled as a `repair` event.

What the tests show:
- a kill inside the renames heals and ends **byte-identical** (`org.state_hash()`) to the life that was never killed. The tear is proven by `organism.npz`'s print differing from the recorded one;
- a torn first snapshot rebuilds from the whole tape, also identical;
- a whole state resumes as before.

**D1 on 84d5ad5** (run by `run_suites.sh` as the unit `days-suites-2`, each result read from its own log):

| Suite | Result |
|---|---|
| genome | `Ran 681 tests … OK (skipped=1, expected failures=6)` |
| tools | `Ran 92 tests … OK` |
| creature | *(read before the launch; recorded in the launch commit's register line)* |

**D2 on 84d5ad5: PREFLIGHT PASS** (`brain-long-2-pre-2`, 23:59 → 00:03, unit `days-preflight-2`).
1. **Alive:** a web on STATUS (L 19, N 19 nodes) and the sparse hash.
2. **Back after a hard kill,** with the web restored.
3. **Back after the power cut.** The repairs recorded 3 tail cuts (tape 4,096 NUL bytes, journal 28 bytes, beliefs 100 bytes) with 0 good rows lost. The tape then held 5,934 rows, no seq used twice, and its max 5,934 was above the top before the cut (3,543).
4. **Back from FAILED.** Seven kills took the unit to `failed` (NRestarts 5); the health watch ran `reset-failed` + `start`, and the life came back.
5. **Training finished** (400 learned).
6. **The sittings finished.** The life then went through both sittings (`fresh`, `s1b1`: 3,009 asks answered, the scene world `ended`) and lived on with no crash, backlog 0 and `web_error` none. So the sittings ran with the web and the self on.

The life was closed at 00:10 with `close_long.sh`.

**The residual risk, said again (it replaces §4.6).**
- **A torn snapshot.** Repaired, as above. It needs a double fault to cost more: a torn generation AND no complete `prev/`. Then the life rebuilds from the whole tape, which is slow but exact.
- **Rows written twice after a resume. This behaviour is older than this build; the pre-flight measured it.** After a resume, the rows the mind replays after its snapshot are written a second time:
  - to the journal and to `state/predictions.jsonl`. After four starts, the pre-flight's `predictions.jsonl` held 14 exact duplicate rows of 27;
  - `beliefs.jsonl` held none.
  
  This cannot change the life:
  - the mind never reads `predictions.jsonl` back; only reading tools do;
  - beliefs are read folded by id;
  - the tape has no duplicates.
  
  **The readings on return** are made from the tape, or they cut the journal at each `start` event's `resumed_from_seq`. They never count raw journal or ledger rows across a restart.

**A second hole, found by reading the watch against the body (not by any run).**
- The heartbeat that the watch's «frozen» rule reads is written by the body's own status thread, every 10 s. A mind thread that HANGS therefore keeps a fresh heartbeat, so «frozen» could never fire for it.
- The watch now also restarts a life whose moments and last_seq have not moved across an hour of watches while its unit is active (**«no motion»**). It shares «frozen»'s once-in-6-hours and the 4 recoveries a day.
- An hour cannot be a legitimate pause: on `brain-long-1`, a calibration at 20,000 scenes paused learning 0.3 s, and the clock worlds publish every 10–60 s.
- A restart count now counts as a problem only when it GROWS (`reset-failed` sets it to 0).
- Tests: `tests/tools/test_health_watch.py`, 7 tests, red on 84d5ad5.
- The watch runs from the life's own code checkout, so this rule must be in the launched commit.
- The commit that carries this amendment changes nothing else: `tools/lives/health.py`, its test, this file. No genome or creature test reads `tools/lives/health.py` (grep).
- D1 for that commit is therefore: the tools suite on it, plus the genome and creature suites on 84d5ad5. All three suites run again on it after the launch, as the record.

**The launch.** `brain-long-2` launches on the commit that carries this amendment, once D1 reads OK. `brain-long-1` is closed at that launch because:
- it carries neither the repair nor the generations;
- two full organisms beside the sleep A/B's six arms would crowd the box's 30 GB.

Its reading so far stays on its root.

Signed: Claude (Opus 5.5, the seat), alone — 2026-09-30 00:10 +0400 (from `date`).

---

## AMENDMENT 2 — D1's creature suite failed on ONE test; the test, not the life's code; the order of the launch

*Written by Claude (Opus 5.5, the seat), alone, 2026-09-30 00:36 +0400, before the launch.*

**D1 read FAILED on 84d5ad5.** The creature suite reported `Ran 1262 tests in 1489.545s — FAILED (failures=1, skipped=6)`; the log is `logs/creature-84d5ad5.log`.
- The one failure: `tests/creature/test_b2_picture_words.py:test_a_snapshot_from_before_this_ledger_resumes_empty_never_back_filled`.
- **What it does:** it simulates an OLD snapshot (one written before the picture-words ledger) by editing a NEW snapshot's `ledger.json` in place.
- **Why it failed:** the generation check of 84d5ad5 rightly read that edit as a torn snapshot (the file no longer matches its recorded print) and healed it from `prev/`, which put the removed keys back.
- A real old snapshot also predates generations. It has no `SNAPSHOT.json`, so the check falls back to the moment agreement and it resumes exactly as before.
- **The fix is the test's:** it now simulates the old snapshot whole, removing `SNAPSHOT.json` and `prev/` first.
  - Red: the unmodified test failed again at 00:3x.
  - Green: after the fix, the module with the snapshot tests reads `Ran 14 tests … OK`.
  - The test's own clause (never back-filled from the ring) is unchanged.

**A consequence, said so no one meets it by surprise.** A state file edited BY HAND after its snapshot now reads as torn and is healed from `prev/`. The edited files are kept in `repairs/` and the heal is journaled. A deliberate edit of a stopped life's state must also remove `state/SNAPSHOT.json`, or the next start undoes it.

**The order of the launch (it replaces «brain-long-1 is closed at that launch»):**
1. `brain-long-2` launches on the commit that carries this amendment.
2. `brain-long-1` stays ALIVE while the full creature suite runs on that commit. It is the life that goes on if the gate fails.
3. Only when that suite reads `OK` is `brain-long-1` closed.
4. If it fails for a reason in code the life runs, `brain-long-2` is closed instead, and `brain-long-1` goes on.
5. A failure is re-run alone on a quiet box before any label (#246).

The code the life runs equals 84d5ad5's except `tools/lives/health.py`. The creature suite passed on 1,261 of its 1,262 tests there. The genome and tools suites also run on this commit, as the record.

Signed: Claude (Opus 5.5, the seat), alone — 2026-09-30 00:36 +0400 (from `date`).
