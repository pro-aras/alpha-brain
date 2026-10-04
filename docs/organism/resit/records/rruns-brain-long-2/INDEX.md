# records/rruns-brain-long-2 — R14, R2, R3 and R1′ on the real closed brain-long-2

*edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:40 +0400 — every figure is read from the file named (RULES section 14). Same reader of record as R1: a detached checkout of `resit-1003` @ feb777e, `tools/brain/resit.py` sha256 498f052eb8acd23d…; same grader (detached d2fe75b), same reference grade.json, same state copy source. The runner is `tools/brain/resit_gate_runs.sh` (sha256 in `script.sha256`), the comparison `../compare_runs.py`; the whole sequence ran as ONE slot job (`slot-ledger-lines.txt`: started 17:32:29 after a 150 s admission wait, `SLOT_MEM=5G`, ended 17:38:17 with exit 0, the slot's cgroup peak 3,904 MB for eleven sequential runs — an upper bound that includes page cache; the largest single process is R14's 1,936 MB).*

Each run's full row is `<label>.gate.json`; its orchestrator line `<label>.stdout` (stderr was empty for every run); `<label>.time` is `/usr/bin/time -v`. `answers.sha256` lists the sha256 of every run's `answers.jsonl` (R1's is in `../r1-brain-long-2/`). `compare_runs.out` is `compare_runs.py`'s printed comparison. Nothing was written under the closed life: every run's `nothing_written` reads 0 newer than its own marker over 435,291 entries (R1′: 436,999, which adds brain-long-3's `code/` directory).

## The readings

| run | the law's mark | result (file) |
|---|---|---|
| `r14` | **R14 TURN IS READ-ONLY** — `Brain.turn(g, scene, world_seed, says=1, asks=1)` on a SECOND load of the real brain, one real sitting canvas's glance | **PASS**: `state_hash` equal before and after, the answers to the 3 probe asks equal (`r14.gate.json` `turn_check`). The same run's R1 (a)/(b) pass (3,011 of 3,011; 7 groups). Price: answer child 34.9 CPU-s, peak RSS **1,936 MB** (the second brain load is ≈ +620 MB over R1's 1,314) |
| `r2-cold`, `r2-warm`, `r2-third` | **R2 DETERMINISM** — R1's run in fresh processes (hash randomisation ON under `-I`: three seeds), cold cache, then warm, then a third time | **PASS**: `answers.jsonl` byte-identical to R1's in all three (sha256 d1f48c074254634a…, `answers.sha256`); the gate rows identical but stamp, timings and run-folder paths (`compare_runs.out`); the glance cache read 0 hits / 1,464 misses cold and 1,464 / 0 warm. CPU of the answer child: 33.2 s cold, 17.0 s and 19.1 s warm (R1 was 28.2 s cold) |
| `r2-blas4` | R2's READING — one warm run with `OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=4` | the CHILD ran with both pins at 4 and `blas_reading: 4` (`r2-blas4/answer-meta.json` flags, read from the file); **0 of 3,011 rows differ** from the 1-thread answers, `answers.jsonl` byte-identical (sha256 d1f48c07…). A reading, not a bar: on this brain and these items four threads give the same bytes; the pin stays law. Whether OpenBLAS actually spawned threads for these small matrices is not measured here |
| `r3-0.5` (the bar), `r3-0.1`, `r3-0.01`, `r3-0.001` | **R3 SENSITIVITY** — the word map `V` of a COPY in memory nudged `V += eps · std(V) · u` (`u` seeded standard normal, seed 20261003), `state_hash` asserted to move (`hash_before` 8ff3bc7520… → `hash_after` differs in every dose) | **ε 0.5 — PLANT CAUGHT:** 2,398 of 3,011 answer rows changed, marks changed **M1, M2a, M3** (and M5). ε 0.1: 2,342 rows; M1, M2a, M3, M5. ε 0.01: 2,320 rows; M1, M5. ε 0.001: 2,317 rows, **no mark changed** (`r3-0.001.gate.json` status FAIL: «the plant does not reach the answers or the marks» is the run's own wording; the law's bar is at ε 0.5 and the other three are printed readings). «Answers changed» is a sensitivity of the ROWS, which carry float scores; MEASURED from `answers.jsonl` against R1's (kind, hyp, point and none_i compared): at ε 0.001 **0** pointings changed (all 2,317 differing rows differ only in float scores), at ε 0.01 **3**, at ε 0.5 **137** of 3,011 (the other 2,261 differing rows differ only in float scores) — the marks are what a pointing change moves. All four plants asserted the state hash moved (the child refuses a plant that changes nothing, R3) |
| `r1p` | **R1′ LAUNCH GATE** — `--code /data/dev/genome-lives/brain-long-3/code` (commit d2fe75b, clean), brain-long-2's `state/prev` copy and items, the pinned grader | **PASS**: 3,011 of 3,011 rows equal the LIFE's (brain-long-2's) journal rows, 7 mark groups equal to 1e-12, and `answers.jsonl` is **byte-identical to R1's** (sha256 d1f48c07…): the hears-only code answers exactly as 9f19879 on the same brain and items. The modules digest differs (0292bfa56faf… against R1's 1ad353349747…): the two code trees differ in some module file that does not reach the answers. Peak RSS 1,315 MB, 38.6 CPU-s |

## The eye pin (R13) on the real tree

`eye_pin` in every row: **15 mutable keys, 0 of them eye or brain keys** (the law's own figure), read from the life's own `creature/genes.py` in the ANSWER child under R11's realpath assertion (25 modules, every one under the code dir).

## The price of the runs (RULES 6d)

| run | answer CPU s | grade CPU s | total CPU s | answer peak MB | grade peak MB | wall s |
|---|---|---|---|---|---|---|
| r14 | 34.9 | 5.9 | 45.6 | 1,936 | 641 | 55.2 |
| r2-cold | 33.2 | 4.8 | 41.9 | 1,314 | 643 | 47.9 |
| r2-warm | 17.0 | 5.0 | 24.8 | 1,337 | 641 | 26.9 |
| r2-third | 19.1 | 4.6 | 26.6 | 1,337 | 641 | 28.6 |
| r2-blas4 | 16.9 | 4.1 | 23.7 | 1,337 | 641 | 26.5 |
| r3-0.001 | 19.2 | 4.2 | 25.8 | 1,337 | 643 | 27.7 |
| r3-0.01 | 19.3 | 5.1 | 26.9 | 1,337 | 641 | 28.9 |
| r3-0.1 | 22.7 | 4.6 | 30.1 | 1,337 | 642 | 32.1 |
| r3-0.5 | 21.3 | 4.6 | 28.5 | 1,336 | 643 | 30.5 |
| r1p | 30.7 | 4.7 | 38.6 | 1,315 | 642 | 41.5 |

All far under the law's caps (cold 1,800 CPU-s, warm 480). A warm gate or daily run is about 25 CPU-s and 1.3 GB.

## What these runs do NOT show

That the series is meaningful (daily and origin modes are not built yet), that the origin can be rebuilt, or that the reader answers right on a life whose BRAIN differs from the one its code was written against: R1′ shows only that brain-long-3's CODE answers brain-long-2's BRAIN alike. R4's refusals, R6, R8 and R9 are exercised on fixtures only until daily and origin modes exist.
