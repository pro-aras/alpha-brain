# records/part2 — the RED → GREEN logs of the re-sit reader's build, parts 1 and 2

*edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 16:48 +0400 — written on the relaunch after the 15:50:57 crash, from the files' own mtimes and lines (RULES section 14: a record a hand-back cites lives under `records/`, not in `scratch/`). Law: `docs/organism/resit/PREREG-RESIT-READER.md` v3, signed ×3 (a472f09, file sha256 c83cac59…e7be).*

Every figure below is read from the file named beside it. The exit files hold the exit code of the run that wrote the log.

| file | written | what it ran | the line it carries | exit |
|---|---|---|---|---|
| `resit-red-1.log` | 15:43:00 | part 1 tests, before `tools/brain/resit.py` existed | `ImportError: cannot import name 'resit'`, `Ran 1 test … FAILED (errors=1)` | 1 |
| `resit-g1.log` | 15:45:46 | part 1 (`tests/tools/test_resit.py`) on the pure helpers | `Ran 85 tests in 0.105s … OK` | 0 |
| `resit-red-2.log` | 15:49:04 | part 2 tests (`tests/tools/test_resit_children.py`) before the two children existed | `Ran 24 tests … FAILED (failures=11, errors=15)` | 1 |
| `resit-g2.log` | 15:50:46 | part 2 tests after `cmd_answer` / `cmd_grade` were written (the predecessor's last run, on `resit.py` of 15:50:34) | `Ran 24 tests in 10.398s … OK` | 0 |
| `resit-recheck-1.log` | 16:4x | **the relaunch's own re-run** of both modules (`-p "test_resit*.py"`) on the same bytes, through slot (`SLOT_MEM=1G`), before this commit | `Ran 109 tests in 5.602s … OK` (85 + 24) | 0 |

The predecessor (agent a3fcebae1c279bf9b) died at 15:50:57; its logs are kept as it left them. The re-run is mine and is what the commit is gated on.

Not yet pinned at this commit (named so that the next commit closes it, never silently): the law's section 1.4 says the `jsonable` copy is «pinned by a parity test» against `creature.mind._jsonable`; no test of part 2 did it. It is added, red first, in the commit after this one.
