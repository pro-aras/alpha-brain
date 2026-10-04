# records/part4 — the RED → GREEN logs of the re-sit reader's build, part 4 (the SERIES helpers and DAILY mode) and its mutation sweeps

*edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 18:08 +0400 — written from the files' own lines and mtimes (RULES section 14). Law: `docs/organism/resit/PREREG-RESIT-READER.md` v4, signed ×3 (5a4cefa). Earlier parts: `../part2/`, `../part3/`, `../r1-brain-long-2/`, `../rruns-brain-long-2/`.*

Test modules: `tests/tools/test_resit_series.py` (17), `tests/tools/test_resit_daily.py` (32), and the earlier `test_resit.py` (85), `test_resit_children.py` (35), `test_resit_gate.py` (53). The daily and series tests were written BEFORE the code (`tools/brain/resit.py` Part 4 and `run_daily`).

## The tests, RED first

| file | mtime | what it ran | the line it carries | exit |
|---|---|---|---|---|
| `resit-series-red.log` | 17:38 | the series helpers' tests (class tables, per-item vectors, R6's partition check, the grader/life genome line hashes, EYE-CHANGED's two forms) before the helpers existed | `Ran 17 tests … FAILED (errors=17)` | 1 |
| `resit-series-green1.log` | 17:42 | the same on the helpers | `Ran 17 tests … OK` | 0 |
| `resit-daily-red.log` | 17:45 | the daily-mode tests before `run_daily` and `scan_life_events` existed | `Ran 27 tests … FAILED (failures=18, errors=9)` («--mode daily is not built yet», a missing function) | 1 |
| `resit-daily-g1.log` | 17:47 | the same on the first implementation | `Ran 27 tests … OK` | 0 |
| `resit-daily-g2.log` | 17:48 | after four tests were added that the first green could not have caught: the GRADE child is handed the ITEMS genome (the row only printed it), a failing partition is a refused row, a tampered items pin is a refused row, the cold/warm cap | `Ran 30 tests … OK` | 0 |
| `resit-daily-g3.log` | 17:50 | after three more found while planning the sweep: the answer child reads the COPY, the items journal's restart duplicates are counted, the grader pin is checked before any child | `Ran 31 tests … OK` | 0 |
| `resit-daily-g4.log` | 17:57 | after the phantom-item test (a graded item the tape never asked has no class and is refused by name) | `Ran 32 tests … OK` | 0 |

## The mutation sweep of daily mode (the sweep ran on a detached COPY of the worktree, so the watched working tree was never mutated — the lesson of the 17:07 incident, `../part3/INDEX.md`)

`mutate_daily.py` breaks ONE thing the law relies on per mutation (17 of them) and runs `test_resit_daily.py`; the original is restored in a `finally` and its sha256 checked.

| file | mtime | result |
|---|---|---|
| `mutate-daily-1.first.log` | 17:57 | **16 CAUGHT, 1 SURVIVED** — D13 («every item is given a class»). The survivor was MY mutation's fault as much as a test gap: it assigned classes only to items present on the tape, so a phantom item was refused anyway and nothing could differ. A first re-run after the phantom-item test SURVIVED again (its console line is quoted, not kept: the next run overwrote its log) for the same reason |
| `mutate-daily-2.d13.log` | 17:59 | D13 re-anchored in `records_from_grade`'s own refusal (an item with no class is given one instead of being refused): **CAUGHT** by the phantom-item test |
| `mutate-daily-final.log` | 18:06 | the whole sweep once more on the final driver and tests: **17 of 17 CAUGHT, survivors `[]`**, `restored: sha256 equal (53a5bb115e74c6e7)`. Exit 0 |

## The suite on the committed bytes

`tools-suite-daily.log` / `.exit` / `.bytes`: the whole `tests/tools` suite on exactly the reader and test bytes this commit carries (their sha256 are in the `.bytes` file) — `Ran 432 tests … OK`, exit 0 (210 of the tools suite's own, 85 + 35 + 53 + 17 + 32 of the resit modules), through slot (`SLOT_MEM=4G`).

## What this part does NOT show

That daily mode answers right on a REAL life: it ran on the stub life only. The real-data checks follow: a daily run on the closed brain-long-2 itself (its real grade's per-item rows, `grader_m2a_rows` on the real grader's internals, R6 on the real aggregates). The units `deploy/creature-brain-resit@.service` and `.timer` are WRITTEN, NOT ENABLED and were NOT run through `systemd-analyze` (it cannot start a manager in this sandbox); they follow the existing units' syntax.
