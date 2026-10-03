# records/origin-bl2-fallback-smoke — ORIGIN MODE on REAL data: the closed brain-long-2 standing in as the life (fallback kind)

*edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:04 +0400 (from `date`) — every figure below is read from the file named beside it (RULES section 14). Law: `docs/organism/resit/PREREG-RESIT-READER.md` v4 (signed ×3, 5a4cefa) + erratum E1 (verifier co-signed 21:02). Reader of record: a detached checkout of `resit-origin-wip` @ a82ea77 (`tools/brain/resit.py` sha256 starts 44f8786a…, the bytes the 339-test resit group ran on, resit-all-3.log). This is a SMOKE of the mechanism on real files, NOT an origin of brain-long-3 and not a series row: the «life» is the CLOSED brain-long-2 (its tape, journal, truth and `state/prev`), the items root is the same closed life, the OUT folder is the scratch `/data/dev/brain-runs/resit-gate/bl2-origin-fallback`, and `--origin-kind fallback_copy` carries a stated reason. Nothing under any life was written; brain-long-3 was not touched.*

## The run

`python3 -B -I tools/brain/resit.py run --mode origin --origin-kind fallback_copy --reason "claims real-data SMOKE of origin mode: the CLOSED brain-long-2 stands in as the life; the OUT folder is a scratch folder, not an origin of record" --root /data/dev/genome-lives/brain-long-2 --code …/brain-long-2/code --items-root …/brain-long-2 --grader-code /data/dev/genome-wt-claims-grader-d2fe75b --out /data/dev/brain-runs/resit-gate/bl2-origin-fallback --scored /data/dev/brain-runs/scene-s1b1r`, under `SLOT_MEM=4G` and `/usr/bin/time -v`, started 21:00:33 +0400, ended 21:01:51, exit 0 (`exit`, `slot-ledger-lines.txt`). No `--state`: the fallback copies the life's own `state/prev` (S3).

## The reading (`ORIGIN.json`; the same row is the RESIT.jsonl line, `NOT-COMMITTED-sha256.txt`)

| what | figure | path in the row |
|---|---|---|
| status | **ORIGIN WRITTEN** (`stdout.txt`, `attempt-origin.json`) | — |
| the source copy (§1.6, R16) | 55,949 manifest entries, 234,065,601 bytes of content, **167,650 tape rows** cut at seq 167,650 (the last sitting's end ask), 0 torn lines on the tape and in the journal, 4,476 payloads kept (3,011 asks + 1,464 sitting canvases + 1 dax training canvas), 51,464 truth files, **built in 24.4 s**; `source_copy_sha256` c3fb7d34… (equal to the sha256 of the MANIFEST file, `NOT-COMMITTED-sha256.txt`); the re-verification at the END of the run read `[]` | `source_copy` |
| ITEMS-MATCH (R15), first, before either child | ok: 3,011 asks, 1,464 canvases, ask digest f0d7517b…, canvas digest 42b89af3… | `items_match` |
| the answers | **3,011 answered of 3,011 asks, 0 unanswered**; `answers_sha256` d1f48c07…, **byte-identical to R1's** (`records/r1-brain-long-2/answers.jsonl`, checked with `cmp`) | `answer_meta`, `answers_sha256` |
| R9 (a READING for a fallback; E1's counts) | **0 of 3,011 EARLY items differ** from the life's own rows (every key but `hash`); LATE items 0; tested EARLY items per set: fresh 1,722 (of 1,724 EARLY), s1b1 1,285 (of 1,287); life rows with no origin row 0; origin rows with no life row or class 0; the act census inside both sittings is empty (no brain-moving row lies inside a sitting, P0's own reading) | `r9`, `r9_reading`, `r9_untested_sets` (empty) |
| the row's own line | «R9 is a READING (a fallback copy is late by construction): 0 of 3011 EARLY items differ from the life's own rows (tested EARLY items per set: fresh 1722, s1b1 1285); LATE items 0, discordant 0» — the same text in `RESIT.md`'s note cell | `r9_reading`, `RESIT.md` |
| R6 partition | the origin's grade OK; the life's own grade OK | `partition.ok`, `life_own.partition.ok` |
| the genome | `eye_changed` False; the genome in force for the state is epoch 1 (the fallback rule: the highest epoch whose row seq is ≤ the snapshot's `last_seq`, 331,518; the one adoption is at 211,015); the label «FALLBACK ORIGIN — late by at most one snapshot» is on the row | `eye_changed`, `states[0].genome_epoch`, `label` |
| the items | 3,011 asks, begin asks at seq 162,597 (fresh) and 165,403 (s1b1) — the law's and R1's own figures; 0 restart duplicates | `begin_seqs`, `restart_duplicates` |
| the grader | commit d2fe75b1d5db…, clean; `GRADER.json` written; modules digest d1710acae1a2… (the digest R1 recorded) | `grader`, `GRADER.json` |

## The price (RULES 6d: memory beside CPU) — the measured numbers the seat's SLOT_MEM for a brain-long-3 origin starts from

| process | CPU | peak RSS |
|---|---|---|
| ANSWER child | 24.7 s | 1,318 MB |
| GRADE child (the origin's answers) | 4.4 s | 380 MB |
| GRADE child (the life's own journal, R9) | 13.6 s | 1,359 MB |
| orchestrator | 20.8 s | 280 MB |
| the run | **63.5 CPU-s** (the law's cold cap is 1,800 s) in **78.1 s** of wall | `/usr/bin/time -v` maximum resident set size 1,391,176 kB (`time.txt`); the slot's cgroup peak (RSS + page cache, an upper bound) **2,595 MB** against its 4 GB cap (`slot-ledger-lines.txt`) |

How it scales: the source copy's size and build time grow with the tape up to the last sitting's end and with `truth/scene` (WHOLE, 51,464 files here); brain-long-3's scene stream ended at 51,496 published, so its copy is of the same order (a measurement on its own tape is the seat's call before the run, §1.6). The two GRADE children hold every row of the copy's tape (here 167,650); a 4 GB cap carried both with 1.4 GB to spare.

## What this run does NOT show

That the rebuilt kind works on real data (no rebuilt state exists; the rebuild is deferred); that R9 refuses on a real difference (every EARLY item here is equal: the refusing path is tested on stubs and by the mutation sweep); that a LIVE life's copy is clean under writes (this life is closed; the same builder reads only complete lines and cuts at the last sitting's end — fixtures plant a torn tail and a later row, R16).

## Hand check (not in the row): nothing was written into the closed life

`find /data/dev/genome-lives/brain-long-2 -newer <origin/20261003T170033Z/START.marker>` printed nothing over the life's 435,291 entries (read 21:02 +0400, after the run; the marker was written at 21:00:33). Origin mode records no `nothing_written` field (daily and gate modes do): on a LIVE life such a find cannot be empty, so the origin's protection is the read-only opens and the fixtures' before/after sizes and mtimes (R16), not a find.

## Not committed (large; sha256 in `NOT-COMMITTED-sha256.txt`)

`RESIT.jsonl` (the row again), `origin/<stamp>/answers.jsonl` (1.8 MB), `grade.json` (474 KB), `life-grade/grade.json`, the source copy `origin/<stamp>/src/` (420 MB on disk) and `states/` (201 MB), and the glance cache `glances.pkl` (9 MB), all under `/data/dev/brain-runs/resit-gate/bl2-origin-fallback/`.
