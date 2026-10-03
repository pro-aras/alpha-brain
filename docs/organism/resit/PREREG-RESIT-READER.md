# PREREG-RESIT-READER — a daily offline re-sit of a life's saved brain on the scene sittings' fixed items

*Written by Claude (Sonnet 5.5, swarm claims), 2026-10-03 12:25 +0400 (from `date`), on the seat's order of the same morning («a read-only tool + a user timer that once a day copies brain-long-3's saved brain from state/prev … and re-sits the copy OFFLINE and FROZEN on the scene sittings' FIXED items … graded as a SERIES … with a planted control … and a GATE: on brain-long-2's sittings copy, the re-sit reproduces the life's OWN sitting answers item by item before any later read is believed»), before any code or run. Branch `resit-1003` from master `15445a3`. It needs the architect's co-signature and the seat's.*

## 0 · The question, and what is built

The architect's forgetting prediction (HEARS-2 AMENDMENT 2): once `brain-long-3` hears the maker's world for days, the scene words decay, colour and size first. **The tool answers one thing and no more: what does the brain, as saved a day later, answer on the SAME 3,011 sitting asks over the SAME canvases?** The items, the canvases, the grader and the reader's code are fixed; only the brain's state moves, so a day-to-day difference is exact for these items.

Built: `tools/brain/resit.py` (one file), `tests/tools/test_resit.py`, `deploy/creature-brain-resit@.service` + `.timer` (a user timer, once a day; **written, not enabled** — the seat enables it for `brain-long-3` after launch). It never writes under a life's root, never calls `Brain.learn` or `Brain.turn`, never touches a unit, and never imports `creature.mind` (it re-uses `_jsonable`'s ten lines, pinned by a parity test).

## 1 · One run, step by step (every step re-uses the code the life ran)

0. **The code is the life's own.** `--code` (default `<root>/code`) is put first on `sys.path` before any import: `genome.brain`, `genome.machinery`, `genome.gaze`, `creature.tape`, `creature.organs_road`, `brain.scene.*` and `tools.brain.grade_life` are the LIFE's bytes (`code/` is the checkout the unit runs), so a later change to master cannot move a day's reading. The reader's own logic is one file in master.
1. **The state.** `<root>/state/prev/` is the last COMPLETE snapshot generation (hard links, `creature/mind.py:snapshot`). Read `prev/SNAPSHOT.json`; `shutil.copy2` `brain.json` and `brain.npz` into `OUT/copy-<stamp>/`; every copy's `(size, mtime_ns)` must equal `SNAPSHOT.json`'s `prints`; a mismatch is retried 3 times, 20 s apart (a generation is being replaced), then the run is REFUSED by name. `Brain.load(copy/"brain", dict(genome.declared["BRAIN"]))` adds its own check (the state's files must hash to the hash they carry).
2. **The genome.** The highest `GENOME.v<n>.genome` under the root, else `GENOME.genome` (the mind's own rule, `_latest_evolved_genome`); `parse_genome`; its `retina`, `gaze`, `colour`.
3. **The items.** `creature.tape.read_tape(<items root>)` in tape order (items root = `--items-root`, default the life's own root): `ask` rows (payload JSON from the tape dir) and eye rows with `meta.kind == "sitting"`. **Exactly the mind's order** (`_consume_ask`, `_brain_canvas`): a canvas-less form (`begin`, `end`, `why`) is answered AT its ask row; every other form is held for its moment's eye row and answered there. No other row is touched; nothing is learned.
4. **The glance.** `gaze.glances(rgb, retina, gaze, "surprise", row["sha"], colour=genome.colour, predicted=None)` — the call `_consume_eye` makes; a sitting canvas carries no ear word, so the mind's `predicted` is None there. Glances are cached in `OUT/glances.pkl` under the key `row["sha"]` + the sha256 of the genome's RETINA, GAZE and `SENSE colour` lines (a content key, #245).
5. **The answer.** `brain.ask(payload, g)` (a `BrainError` is ANSWERED `refused`, as the mind does). The row is the mind's own: `{"kind":"answer","by":"brain","item","mark","form","answer","moment","seq","eye_seq","at","fix","hyps","detail":null}`, `fix`/`hyps` from `creature.organs_road.eye_view(g)`, `answer` through `_jsonable`. `begin` is answered first and **may calibrate the COPY** (`Brain.ask` does so when the brain has learned since its last calibration) — that is the life's own sitting protocol; every series row records `calibrated` and `calibrated_at`.
6. **The grade.** `tools.brain.grade_life.grade(<items root>, OUT/journal, scored, label)` — the library call, never `main()` (which writes into `root/grade/`). The grader reads the TAPE, the TRUTH files and the ANSWER rows and recomputes nothing; without learn rows it takes its own look for «meeting seen».
7. **The series.** ONE line appended to `OUT/RESIT.jsonl`, `OUT/RESIT.md` rewritten from it. `OUT = /data/dev/brain-runs/resit/<life>/` — outside every life's root.

## 2 · The classes (a partition, counted against the record)

Phrase classes for the three marks the seat named, from the ask payload's `phrase` and the brain's own word types (STATUS `brain.types`: shapes circle cross ring square star triangle · colours blue green red white yellow · sizes big small): **`white`** (the phrase holds «white»: the one scene colour the maker also draws) > **`colour_or_size`** (holds a colour or a size, no «white») > **`shape_only`** (shapes alone). A phrase holding a word of NO type is refused by name, never binned.

| mark, fresh set | shape_only | colour_or_size | white | total (counted from the 3,011 payloads) |
|---|---|---|---|---|
| M1 (point) | 86 | 254 | 55 | 395 (graded: 202 covered of 244 gradable in brain-long-2's grade) |
| M2a (refuse) | **0** | 315 | 85 | 400 |
| M3 (compose) | **0** | 50 | 10 | 60 |

(s1b1 set, readings only: M1 95 / 264 / 40 = 399, M2a 0 / 317 / 83, M3 0 / 50 / 10.) M2a and M3 have **no shape-only item**: those cells read `n/a (0 items)`, never 0. The per-class graded n is smaller than the totals (coverage 0.83 on M1): it is printed beside every figure, with the smallest gap a paired test can pass at that n (**10 / n**, #245 (5)) — at n ≈ 45 (white) that is ≈ 0.22: the series reads only large class-level moves, and says so.

## 3 · The marks (what the INSTRUMENT must satisfy; the forgetting itself is the hears lane's)

| # | mark | bar | ceiling |
|---|---|---|---|
| **R1 THE GATE** | on `brain-long-2` (CLOSED; `--code` its own `code/`, state from a COPY of `state/prev`, items root its own): every re-sit answer row equals the life's own journal `answer` row in `answer`, `fix`, `hyps`, `item`, `mark`, `form`, `moment`, `seq`, `eye_seq`, `at` (deep equality after a JSON round trip); the re-sit's graded marks (M1, M2a, M3, M5 on fresh) equal `grade-brain-long-2-2026-09-30/grade-bl2-new/grade.json`'s to 1e-12 | **3,011 of 3,011 rows equal, 4 of 4 marks equal** | exactly 3,011 (a deterministic reader: any difference is a DEFECT of the reader — the glance first, #173 — never a tolerance) |
| **R2 DETERMINISM** | the run repeated in a fresh process, cold glance cache then warm, and under two `PYTHONHASHSEED`s: `answers.jsonl` byte-identical, the series line identical but its stamp | identical | point mass |
| **R3 SENSITIVITY (plant)** | a COPY of the brain whose word map `L.V` is nudged (`+ ε · u`, `u` a seeded standard-normal array, ε = 0.1; `Brain.state_hash()` before ≠ after, asserted) is re-sat | **≥ 1 answer changed and ≥ 1 of the 3 marks changed** | the plant asserts it changed the bytes |
| **R3b dose reading** | the same at ε = 1e-4, 1e-3, 1e-2, 1e-1 (one seeded `u`): the number of changed answers and the marks printed | a READING: the smallest ε that moves a single answer is the instrument's floor | not graded |
| **R4 REFUSALS** | (a) `copy2` copy with one byte flipped inside an array of `brain.npz`: `Brain.load` refuses (its `BrainError` on the state hash, or numpy's zip error if the flip lands in the container), reported by name; (b) a copy touched so its mtime_ns differs from `SNAPSHOT.json`: the print check refuses; (c) no `state/prev` or no sitting on the tape yet: SKIPPED by name; each becomes a row `{"skipped"/"refused": reason}` in `RESIT.jsonl`, exit 0, never a crash (#230) | 3 of 3 | — |
| **R5 READ-ONLY** | a fixture root made read-only (`chmod -R a-w`) is re-sat end to end with `OUT` elsewhere: it completes; and after the R1 run on the real closed root, `find <root> -newer <marker>` is empty | pass | — |
| **R6 PARTITION** | every graded M1, M2a, M3 item falls in exactly one class: the counts sum to n for each mark and set; a plant (a phrase with the unknown word «zog») is refused by name | sums equal; plant refused | — |
| **R7 PRICE** | a cold run ≤ 30 CPU-min, a warm run ≤ 8 CPU-min, measured with `process_time`; over the cap the run STOPs and reports | within cap | — |

**Null.** The null of a re-sit is itself: an unchanged copy answers identically (R2). There is no sampling noise to draw ≥ 10 times: the reader is deterministic and the items fixed; a day-to-day difference is the brain's change, exact for these items. What it cannot say is whether the change generalises to other items of the same words.

## 4 · What a later reader may conclude (the series' rules)

Each day's row carries, per set (fresh graded, s1b1 reading) and per mark: `value`, `n`, `n_all`, and per class `value`, `n`, `k` (correct), plus `calibrated`, `calibrated_at`, `n_learned`, the brain's `state_hash`, the snapshot's `last_seq` and `t`, and the code sha. The comparison of day d with the first row is **paired by item**: discordant counts `b` (right → wrong) and `c` (wrong → right), the exact one-sided sign test p, and the smallest gap passable at that n — printed, with **no bar** (a reading; the verdict on the forgetting prediction is the hears lane's). A class with graded n < 30 reads UNDERPOWERED by name. The «day 0» of `brain-long-3` is its first run; the pairing to `brain-long-2`'s frozen reading (the same seed, no maker words) is HEARS-2 §4's, and this tool prints the R1 run's marks as `baseline: brain-long-2`.

## 5 · The price, and the stops

R1 cold (1,464 canvases through the sealed tower, 3,011 asks): **cap 30 CPU-min, measured, not guessed**; R2 two warm runs; R3 one run plus the 4-point dose sweep (warm, answers only): ≈ 5 × 8 CPU-min; R4–R6 are unit tests (seconds). Total ≈ 80 CPU-min through the slot gate (3 slots at most). **Stops:** R1 fails → nothing else runs; the first differing item is printed with both rows and the first suspect is the glance (the tower/gaze imports, then `predicted`), not the brain. R3 not changing an answer at ε = 0.1 → the reader is blind (the plant is placed where the mechanism can fire: ε = 0.1 on `V` against an answer margin of order 1; if it still changes nothing the plant is not reaching the answers and the law says so, #228 (a)).

## 6 · Adversarial walk

1. **Can R1 pass without the reader being right?** Only if the reader copies the life's `fix`/`hyps`/answers: it does not — it recomputes the glance from the TAPE's PNG, and the journal row is the thing it is compared WITH. A reader that read the journal would pass trivially and R3 would catch nothing: so R3 is run on the nudged COPY and must change answers computed from the tape.
2. **Can R1 fail for a reason that is not the reader?** Yes, three: the life's brain state at the sittings differs from `state/prev` today (brain-long-2's brain has not learned since 05:03 on 09-30: `brain.learned` 50,000 and `asks_answered` 3,011 unchanged in all 232 HEALTH rows — so `state/prev` IS the sitting-time brain, and the closing snapshot cannot differ); a `begin` that calibrates (it does not: `calibrated_at` equals `n_learned` at 50,000, the scheduled calibration); and a different code version (hence `--code` the life's own).
3. **Where can the mechanism fire?** On every class but two empty cells (§2); the grader's M1 null (K = 20) reads p95 0.605 and the life's M1 0.980: the mark can fire. An ABLATED reader (`Brain.ask` replaced by the grader's uniform draw) reads M1 at chance, ≈ 0.54 (the grade's `chance`): checked as a unit test with a stub brain.
4. **Every «every / by N» counted:** 3,011 asks (794 M1 across two sets, 800 M2a, 400 M5, 321 NAME, 112 M2b, 84 M6, 120 M3, 192 SPEAK, 96 DECLINE, 60 SPEAK2, 28 why, 4 begin/end — counted from the payloads); 1,464 sitting canvases; 4 dose points; 3 refusal paths; 2 hash seeds.
5. **The copy race.** `state/prev` is replaced at every snapshot (≈ every 6.7 min); the files in it are never modified in place (new inodes, renamed), so a file copied is whole; the print check across `brain.json` and `brain.npz` and the state hash catch a generation torn between the two copies; three retries.
6. **A moving brain is not a frozen one.** For `brain-long-3` the brain keeps learning the maker's words; each day's copy is a different brain and the `begin` ask calibrates it as the life's own would. The series is the brain's reading AS SAVED, not the reading the life would have given at the day's own sitting (the life has no daily sitting).
7. **What a pass does NOT show:** that the scene words are retained (that is the series' reading, days later); that the brain's answers on other items are unchanged; that the organs' road answers the same (the reader answers only by the brain).

## 7 · Signatures

Signed: Claude (Sonnet 5.5, swarm claims), 2026-10-03 12:25 +0400 (from `date`) — the author.
Co-signed: the architect — pending.
Signed: the seat — pending.
