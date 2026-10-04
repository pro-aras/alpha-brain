# records/r1-brain-long-2 — R1, THE GATE, run for real on the closed brain-long-2

*edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:28 +0400 — every figure below is read from the file named beside it (RULES section 14). Law: `docs/organism/resit/PREREG-RESIT-READER.md` v3, signed ×3 (a472f09). Reader of record: a detached checkout of `resit-1003` @ feb777e (`tools/brain/resit.py` sha256 498f052eb8acd23d…, the bytes the suite and both mutation sweeps ran).*

## The run

`python3 -B -I tools/brain/resit.py run --mode gate --label r1 --root /data/dev/genome-lives/brain-long-2 --code …/brain-long-2/code --items-root …/brain-long-2 --grader-code /data/dev/genome-wt-claims-grader-d2fe75b --out /data/dev/brain-runs/resit-gate/bl2 --scored /data/dev/brain-runs/scene-s1b1r --reference-grade /data/dev/brain-runs/day0929/days/grade-brain-long-2-2026-09-30/grade-bl2-new/grade.json`, under `SLOT_MEM=6G` and `/usr/bin/time -v`, started 17:25:37 +0400 (slot 6, after a 60 s admission wait), ended 17:26:28, exit 0 (`exit`, `slot-ledger-lines.txt`). R14 (`--check-turn`) is deliberately NOT in this run: a refusal there must not hide R1.

## The reading — R1 PASSES (`gate.json`, `stdout.txt`)

| what | figure | file / path in gate.json |
|---|---|---|
| (a) every re-sit answer row equals the life's own journal row in every key but `hash` | **3,011 of 3,011** equal; 0 different; 0 without a life row; 0 life rows not re-sat; 0 unanswered; 3,011 asks on the tape | `r1a` |
| (b) the graded marks equal the reference grade.json's | **7 mark groups equal to 1e-12** (fresh and s1b1 × M1, M2a, M3, and M5), 4,667 leaves compared, 0 differences | `r1b` |
| P0 (the brain did not move after the first sitting ask) | first sitting ask seq 162,597; 100,008 `kind: "brain"` rows seen; 0 of any act above it | `p0` |
| restarts inside a sitting (AM1 d) | 0 asks with two answer rows | `restart_duplicates` |
| the genome in force (AM3) | epoch 0 (`GENOME.genome`, sha256 ac6631a6d745…) for both sets; epochs 0 and 1 carry EQUAL RETINA, GAZE, SENSE-colour and BRAIN lines (the reading AM3 asks for); their whole-genome hashes differ (one line, KWTA) | `genome` |
| the state copy | `state/prev` of the closed life, `last_seq` 331,518, prints OK on the first attempt; `n_learned` 50,000 = `calibrated_at` 50,000 before and after (it owes no calibration) | `state` |
| the items | 3,011 asks, 1,464 sitting canvases, world seed 20261101; `ITEMS.json` written | `items`, `ITEMS.json` |
| the grader | commit d2fe75b1d5db… (clean checkout), `grade_life.py` sha256 557f1bf8f0e7…, modules digest d1710acae1a2…; `GRADER.json` written | `grader`, `GRADER.json` |
| the subject | 25 modules of genome/brain/creature, every one under the life's own `code/` (R11), digest 1ad353349747…; code commit 9f19879bb119 (clean) | `subject`, `code_commit` |
| the glance cache | COLD: 0 hits, 1,464 misses — every answer was recomputed from the tape's PNGs, none copied from the life's rows | `answer_meta.glance_cache` |
| R5 (b) nothing written into the life | an own marker, then the in-process walk of `/data/dev/genome-lives/brain-long-2`: **435,291 entries walked, 0 newer than the marker** | `nothing_written` |
| M6 (R1 (c)), a READING, never graded | «NOT GRADABLE — the one meeting was not seen by the gaze» (the reference said the same); `read_by` is now «the grader's own look» because the re-sit journal holds no learn row (the reference's was «the brain's learn row») | `m6_reading` |
| the live STATUS (R12) | the closed life's last STATUS: backlog 0, 3,323.4 ms per canvas (start and end) | `live_load` |

## The price (RULES 6d: memory beside CPU)

| process | CPU | peak RSS |
|---|---|---|
| ANSWER child | 28.2 s | **1,314 MB** |
| GRADE child | 4.4 s | **643 MB** (its `Life` loads the whole tape's 331,616 rows into a list) |
| orchestrator | 4.8 s | 75 MB |
| the run | **37.3 CPU-s** (the law's cold cap is 1,800 s) in 51 s of wall | `/usr/bin/time -v` maximum resident set size 1,345,692 kB (`time.txt`); the slot's cgroup peak (RSS + page cache, an upper bound) 2,035 MB (`slot-ledger-lines.txt`) |

How it scales: the ANSWER child's peak is the brain's state in memory (state/prev on disk: 29.6 MB json + 180 MB npz) plus a second copy during `state_hash()`; it does not grow with the tape (the tape is a generator). The GRADE child's peak grows with the TAPE's row count (the grader holds every row), so an origin run over a live life's longer tape needs the measured cap, not a guess (the seat's rule, 17:2x).

## What this run does NOT show

That the reader is sensitive (R3's nudge), deterministic across processes (R2), that `Brain.turn` is read-only (R14), or that brain-long-3's code answers alike (R1′): each is its own run. A PASS of R1 shows only that, on the real life, the reader's answers equal the life's, row by row, from glances it computed itself.

## Files

`gate.json` (the whole row), `answers.jsonl` (the 3,011 re-sit rows), `grade.json` (the pinned grader's grade of them), `answer-meta.json`, `grade-meta.json`, `answer-spec.json`, `grade-spec.json`, `ITEMS.json`, `GRADER.json`, `stdout.txt`, `stderr.txt` (empty), `time.txt`, `exit`, `slot-ledger-lines.txt`, `SHA256SUMS`. The cold glance cache (9,277,341 bytes) is kept outside git at `/data/dev/swarm/2026-10-03/claims-records/r1/glances.pkl`; its sha256 is in `glances.pkl.sha256`.
