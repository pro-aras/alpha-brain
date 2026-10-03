# records/part3 — the RED → GREEN logs of the re-sit reader's build, part 3 (the ORCHESTRATOR, gate mode) and its mutation sweeps

*edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:19 +0400 — written from the files' own lines and mtimes (RULES section 14). Law: `docs/organism/resit/PREREG-RESIT-READER.md` v3, signed ×3. Part 1 and 2 records: `../part2/`.*

Every row below is read from the file named. Exit files hold the exit code of the run that wrote the log. Test modules: `tests/tools/test_resit.py` (part 1, 85), `test_resit_children.py` (part 2, 24 + the later additions), `test_resit_gate.py` (this part).

## The tests, RED first

| file | mtime | what it ran | the line it carries | exit |
|---|---|---|---|---|
| `resit-jsonable-1.log` | 16:49 | the `jsonable` parity pin of the law's section 1.4 (the copy against `creature.mind._jsonable`; two plants that must make the comparison fail) — the pin is on existing behaviour, so it is green at once; the plants are its red | `Ran 4 tests … OK` | 0 |
| `resit-red-3.log` | 16:53 | the child's R3 nudge and R2 BLAS-reading tests, before the child had either | `Ran 7 tests … FAILED (failures=3, errors=3)` | 1 |
| `resit-g3.log` | 16:55 | both existing modules (`test_resit.py`, `test_resit_children.py`) after the child gained the nudge (`V += eps · std(V) · u`, the state hash asserted to move) and a declared BLAS reading | `Ran 120 tests … OK` (85 + 24 + 4 + 7) | 0 |
| `resit-red-4.log` | 17:00 | `test_resit_gate.py` before the orchestrator existed (a first run showed 28 `KeyError: 'form'` — a fault of MY fixture's stub grader, which did not filter the journal to answer rows as the real grader does; fixed, then this run) | `Ran 49 tests … FAILED (failures=19, errors=33)`; every cause is «the orchestrator is not built yet» or a missing helper | 1 |
| `resit-gate-run1.log` | 17:04 | the same module on the first implementation | `Ran 49 tests … OK` | 0 |
| `resit-gate-run2.log` | 17:12 | after the sweep's two survivors were closed with tests (M13, M14) and `check_grader_pin` was made fail-closed with two tests | `Ran 53 tests … OK` | 0 |

## The mutation sweep (a green gate can lie, #229; 49 of 49 green on the first run is exactly when to doubt it)

`mutate_gate.py` breaks ONE thing the law relies on per mutation, runs `test_resit_gate.py`, and restores `tools/brain/resit.py` in a `finally`, checking the sha256 (its own line, and the job's own before/after lines). The mutations are written with a `<<NEVER>>` token, so no literal always-false branch sits in any committed file.

| file | mtime | result |
|---|---|---|
| `mutate-gate-1.log` | 17:10 | **12 CAUGHT, 2 SURVIVED** — the survivors named two test gaps: M13 (unanswered asks did not count against R1 (a): a re-sit that answered 8 of 10 asks, every written row equal, would have passed) and M14 (a run without a reference grade could read PASS). Both closed with a test each (`test_a_resit_that_leaves_asks_unanswered_…`, `test_without_a_reference_grade_the_gate_reads_partial_…`). Exit 1. |
| `mutate-gate-2.log` | 17:18 | **15 of 15 CAUGHT, survivors `[]`**, `restored: sha256 equal (498f052eb8acd23d)`. M07 re-anchored on the fail-closed comparison and M15 added (the `modules_digest` skip made unconditional). Exit 0. |

**An incident worth keeping.** During the first sweep (17:07) the seat's automated review saw M07's mutated line in the working tree (`tools/brain/resit.py` with the grader pin's comparison made never-true) and flagged it as a fail-open gate. It was the plant, restored by the driver's `finally` at the end of the sweep; the seat asked for two checks before any commit — the sha256 equal to the pre-sweep value, and `grep -c` of the always-false pattern over `tools/brain/resit.py` reading 0 — and for `check_grader_pin` to fail closed (compare EVERY pin key; skip `modules_digest` only on the pre-check, where the grade child has not yet run and it is legitimately unknown). Both done: 498f052eb8acd23d before and after the second sweep, and the pattern count 0. Lesson: a mutation sweep over the file a reviewer is watching needs the reviewer told before it starts, or runs on a copy of the worktree.

## The suite on the committed bytes

`tools-suite-wip.log` / `.exit` / `.bytes`: the whole `tests/tools` suite on exactly the reader and test bytes this commit carries (the sha256 of each is in the `.bytes` file), through slot (`SLOT_MEM=4G`). Its result line is read from the file at the commit; the commit is gated on its exit file.
