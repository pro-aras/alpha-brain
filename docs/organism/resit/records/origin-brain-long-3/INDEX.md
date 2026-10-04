# records/origin-brain-long-3 — the PRODUCTION FALLBACK ORIGIN of brain-long-3 (the seat's order of 2026-10-03 21:34 +0400)

*(edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 22:17 +0400 (from `date`). Every figure below is generated from the three runs' own JSON and slot-ledger lines by `make_bl3_index.py`, none is typed by hand (RULES section 14). Law: `docs/organism/resit/PREREG-RESIT-READER.md` v4 (signed x3) + erratum E1 (verifier + seat signed). Reader of record: resit-1003 @ 916f741, `tools/brain/resit.py` sha256 bacf8fc3418099f7… (the bytes the 74-mutant FINAL sweep ran on, `../origin-sweep/`). The daily timer is NOT enabled; brain-long-3's root, units and timers were read, never written.)*

## The three steps the seat ordered, in order

| step | what | where | result |
|---|---|---|---|
| 1 MEASURE | the reader's own `build_source_copy` on the live root (read-only opens), timed, no child; run with the reader a82ea77 (`reader_sha256` 44f8786a…), whose `build_source_copy`, `verify_source_copy` and `dax_index_of` are byte-identical in the production reader 916f741 (`measure/function-compare.txt`) | `measure/` | 166,368 tape rows (cut at the last sitting's end ask), 55,943 manifest entries, 181,243,741 bytes, 4,476 payloads kept, 51,464 truth files, 0 + 0 torn lines; built in 18.157 s, re-verified in 3.924 s, problems []; the script's own peak RSS 327.3 MB; the slot cgroup peak 979 MB (21:46:34–21:46:57) |
| 2 REHEARSAL (**my addition, not ordered**: the seat ordered measure, then the origin run; I priced SLOT_MEM from a full run in a scratch OUT before the written-once production run) | the whole origin run into a scratch OUT | `rehearsal/` | ORIGIN WRITTEN in 94.14 s, 87.851 CPU-s; RSS answer child 1392.9 MB, grade child 376.7 MB, life-grade child 1065.3 MB; the slot cgroup peak **2,319 MB** against its 4G cap. **SLOT_MEM for the production run: 4G >= 1.3 x 2,319 MB = 3,015 MB** |
| 3 PRODUCTION | `run_bl3_origin_production.sh` through slot, SLOT_MEM=4G, the seat's `--reason` verbatim, `--origin-kind fallback_copy`, `--state` the seat's copy of 19:30:14 | `production/` | ORIGIN WRITTEN 22:02:31–22:04:12 (stdout.txt), exit 0, 101.423 s, 89.11 CPU-s, the slot cgroup peak 2,261 MB, stderr empty |

## The row (`production/ORIGIN.json`, which equals the one line of `/data/dev/brain-runs/resit/brain-long-3/RESIT.jsonl`, checked)

| what | figure | path in the row |
|---|---|---|
| identity | stamp 20261003T180231Z, kind origin, `origin_kind` fallback_copy, label «FALLBACK ORIGIN — late by at most one snapshot»; `reason` is the seat's text, byte-equal to `production/reason.txt` | `kind`, `origin_kind`, `label`, `reason` |
| the state | the seat's read-only copy of `state/prev` (19:30:14): snapshot `last_seq` 166,243, 51,365 learned, genome epoch 0, genome sha256 1567b684e954…, state hash 88ac50e599fe… | `states[0]` |
| the source copy | 166,368 rows cut at seq 166,368, 55,943 entries, 181,508,015 bytes, 51,464 truth files, 0 torn lines, built in 18.544 s; `source_copy_sha256` e341e5e88582… equal to the sha256 of its MANIFEST; the end-of-run re-verification read [] | `source_copy` |
| ITEMS-MATCH (R15) | ok: 3,011 asks, 1,464 canvases, ask digest f0d7517b1bf9…, canvas digest 42b89af3416b… | `items_match` |
| the answers | **3,011 answered of 3,011 asks, 0 unanswered**; `answers_sha256` d2bda8ff41cf… | `answer_meta`, `answers_sha256` |
| R9, a READING for a fallback | «R9 is a READING (a fallback copy is late by construction): 12 of 13 TESTED EARLY items differ from the life's own rows (tested EARLY items per set: fresh 6, s1b1 7); the structural begin/end rows differ on 2 of 2 (not counted as tests); LATE items 2996, discordant 2386» (the same text is `RESIT.md`'s note cell); untested sets [] | `r9`, `r9_reading` |
| R6 partition | the origin's grade ok: True; the life's own grade ok: True | `partition`, `life_own` |
| genome | `eye_changed` False; begin asks at seq 161,464 (fresh) and 164,148 (s1b1); 0 restart duplicates | `eye_changed`, `begin_seqs` |
| the grader pin | commit d2fe75b1d5db…, clean, at `/data/dev/brain-runs/resit/grader-d2fe75b` (the daily unit's own path; I created that checkout as a detached worktree of d2fe75b); `GRADER.json` written once by this run | `grader`, `production/GRADER.json` |

## Production against rehearsal (same inputs, 14 minutes apart; compared by script)

`answers.jsonl` is **byte-identical** (`cmp`; sha256 d2bda8ff41cf… in both). `r9_reading`, `items_match`, `partition`, `states`, `begin_seqs`, `genome_lines`, `code_commit`, `eye_changed`, `restart_duplicates`, `reason` and `reader_sha256` are equal. Two things differ and each has its cause on the files: `source_copy_sha256` (08d451600396… against e341e5e88582…) because exactly ONE MANIFEST line differs, the LIVE journal (`journal/2026-10-03.jsonl`, 101,878,230 against 102,107,259 bytes: the life writes on; the answers read only its epoch and start rows); and the grade files' sha256, because each `grade.json` carries the run's stamp as its label.

## What this origin says, and what it does not

- **It is a baseline for the daily series, not a verification of the state at asking time.** The state is the seat's fallback copy (the end of the scene stream), so R9 is a READING: only 13 TESTED EARLY items exist (fresh 6, s1b1 7) because brain-moving rows lie INSIDE the sittings (the act census inside them: fresh 31 learn and 31 turn rows, s1b1 29 and 29), so 2,996 of the 3,011 asked items are LATE by R9's own rule. 12 of the 13 tested EARLY items differ from the life's own rows (the first, in the key `['answer']`), which is what «late by construction» predicts. brain-long-2's smoke (`../origin-bl2-fallback-smoke/`) read 0 of 3,011 because that life had no brain-moving row inside its sittings: the two lives are not comparable on this reading.
- **Not shown:** the exact (rebuilt) origin, which stays deferred; R9 refusing on real data (stubs and the sweep only).
- **The seat's copy of `state/prev`** (`--state`): 12 files, none newer than the production run's START.marker (0 paths), the newest mtime 19:25:46 against the marker's 22:02:31 (`production/state-copy-untouched.txt`).
- **The live life.** The top-level names of its root: 29 before and 29 after, identical (`production/live-root-top-level-*.txt`); no file with an output name of this reader (ORIGIN, RESIT, GRADER, ITEMS, glances, answers, grade, MANIFEST, START.marker, *.pyc) lies under it; the files newer than the run's marker lie in the directories of the life's own writers (tape, evolve, truth, game_door, read, game, ask, world, watch, state, journal, STATUS.json), none of them carrying an output name of this reader. `live_load` in the row: ms per canvas 460.668 at the start of the run and 336.9391 at its end, backlog 0 and 0: a box-wide reading (other lanes' jobs were running, slot ledger), and no share of it is claimed for or against this run.

## For the seat (done by me / not done by me)

- DONE: the pinned grader checkout exists at `/data/dev/brain-runs/resit/grader-d2fe75b` (a detached worktree of d2fe75b, `grade_life.py` sha256 557f1bf8…, identical to the checkout the earlier runs used); the production OUT `/data/dev/brain-runs/resit/brain-long-3` holds the origin only.
- NOT DONE (yours): enabling `creature-brain-resit@brain-long-3.timer`; the unit calls `/data/dev/genome/tools/brain/resit.py`, so master must carry resit-1003's `tools/brain/resit.py` (sha256 bacf8fc3418099f7…, the bytes this origin was made by) before the first daily row, or the row records another reader.

## Not committed (large; sha256 in `production/NOT-COMMITTED-sha256.txt` and `rehearsal/NOT-COMMITTED-sha256.txt`)

`RESIT.jsonl` (the row again), `origin/<stamp>/answers.jsonl`, `grade.json`, `life-grade/grade.json`, the source copy `origin/<stamp>/src/` and `states/`, and the glance cache `glances.pkl`, all under `/data/dev/brain-runs/resit/brain-long-3/` (production) and `/data/dev/brain-runs/resit-gate/bl3-origin-fallback-rehearsal/` (the rehearsal, a scratch folder, not a record of the series).
