# records/daily-bl2-smoke — daily mode on REAL data: the closed brain-long-2 standing in as both the «live» life and the items

*edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 18:16 +0400 — every figure is read from the file named (RULES section 14). Law: v4, signed ×3 (5a4cefa). This is a SMOKE of the mechanism on real files, NOT a series row of brain-long-3: the «life» is the closed brain-long-2 itself (its `state/prev`, its journal, its genomes) and the items root is the same closed life, so what the row says is only that the reader, the real grader and the real aggregates agree; the OUT folder is `/data/dev/brain-runs/resit-gate/bl2-daily`, not the production OUT.*

## A defect the real data found (and the stub could not)

The first run (`first-run-refused.stdout`, reader of record a detached checkout of 68ff83a, 18:08) was REFUSED by the reader's own R6 check:

> R6 PARTITION: the classes do not sum to the grade's own aggregate for M1/fresh (classes n 353 k 349 items 395, grade n 202 k 198 items 395); M1/s1b1 (classes n 362 k 356 items 399, grade n 192 k 186 items 399)

Cause (read in `brain/scene/marks.py summarise_pointing`): the grader's `M1.graded` block is the **2- and 3-thing items only** (the bars read it; `all` adds the trivial one-thing items), and the law's own R6 figure («brain-long-2: M1 fresh 202 covered») is that block, while my class tables counted every gradable covered item. The stub items carried no `n_things`, so no test could see it. Fixed test-first (`../part4/resit-series-red2.log` RED → `resit-series-green2.log` GREEN, commit bc7f807): an M1 row now carries a graded flag, a covered one-thing item stays among the class's items and out of its covered rate, a row with no `n_things` is refused by name. The partition check refused a wrong row exactly as designed.

## The reading of the second run (reader of record: a detached checkout of bc7f807, `d2.stdout`, `RESIT.jsonl`)

| what | figure (path in the row) |
|---|---|
| refused or skipped | neither: one series line |
| answers | `answers_sha256` d1f48c074254634a… **equal to R1's** (`answers.sha256`): the daily road, under the genome in force at the copy, answers the closed life byte for byte as the gate did |
| the genome in force (S1) | **epoch 1** (`GENOME.v1.genome`; the adoption row's seq 211,015 is at or below the copy's `last_seq` 331,518) — R1 ran under epoch 0 (the gate rule); the four eye/brain line hashes of the two epochs are equal, so the answers are too |
| the grader's genome | brain-long-2's `GENOME.genome` (the items root's); the life's WORLD scene, TAPE, RETINA, GAZE, SENSE colour line hashes equal the grader genome's, and so does the BRAIN hash (same life); EYE-CHANGED false; form (i) «NO ORIGIN» |
| R6 PARTITION | **all six (mark × set) rows OK against the grade's own aggregates:** M1 fresh n 202 k 198 (items 395), s1b1 n 192 k 186 (399); M2a fresh n 400 k 341, s1b1 n 400 k 337; M3 fresh n 58 k 58 (60), s1b1 n 59 k 58 (60) |
| the class counts (law §2's table) | M1 fresh items 86 shape_only / 254 colour_or_size / 55 white; s1b1 95 / 264 / 40; M2a fresh 0 / 315 / 85, s1b1 0 / 317 / 83; M3 0 / 50 / 10 on both sets — **every count equals the law's own** |
| the pooled reading unit (covered rate by class) | M1: shape_only n 80 k 80 (1.000), colour_or_size n 263 k 255 (0.970), white n 51 k 49 (0.961); white is UNDERPOWERED in each single set (n 29 and 22, under 30) and not pooled; M2a refusal: colour_or_size 531 / 632 (0.840), white 147 / 168 (0.875), shape_only `n/a (0 items)`, never 0; M3: 97 / 98 and 19 / 19, white UNDERPOWERED |
| the vectors | M1 794 items (394 in the covered graded population = 202 + 192), M2a 800 (all), M3 120 (117 = 58 + 59), keyed by item NAME |
| M5 (fresh) | n 400, PASS (named 1.0, refused 1.0) |
| the journal scan | 382,078 lines read (the journal's own line count), 1 epoch row, 1 start row, 0 torn lines; 0 restart duplicates in the items root |
| `vs_origin` | none: «NO ORIGIN: a daily copy is never one — no g_c is printed» |
| price | answer child 33.4 CPU-s (its glance cache was cold) and 1,315 MB peak RSS; grade child 9.1 CPU-s (it also takes the per-item M2a rows from the grader's own functions) and 643 MB; orchestrator 4.6 CPU-s and 61 MB; **47.1 CPU-s** in all; slot cgroup peak 2,013 MB (`slot-ledger-lines.txt`) |
| nothing written | 435,291 entries of the closed life walked, 0 newer than the run's marker |

## What this smoke does NOT show

That a series row of brain-long-3 reads sensibly (its state is early, its origin does not exist yet), that pairing against a real origin works on real vectors (no origin exists: pairing is tested on fixtures only), or that the daily timer behaves under systemd (the units are written, not enabled, and could not be run through `systemd-analyze` in this sandbox).
