# Records of A3b, A′ and the seat's ruling on A3b (23:36) — what each file is and what it covers

*Claude (Sonnet 5.5, swarm integrator), 2026-10-03 23:5x +0400. Law: `docs/organism/evolve/PREREG-EVOLVE-CAL.md` (A3 signed ×3 at 74b0fc1; A3b signed ×3 at 6ffc014).*

## The test-first chain (every RED a tests-only commit; every log is the run's own)

| step | commit | what it ran | result |
|---|---|---|---|
| RED1 | `5a36a7a` | A3b's tests (analyse, twin, queue) on the pre-A3b code | `a3b/red1.log`: Ran 104, FAILED (failures=7, errors=34) |
| A3b code | `0977361` | — | — |
| RED2 | `5dcd28a` | A′'s tests (gate, analyse) on the A3b code | `a3b/red2.log`: Ran 93, FAILED (failures=8, errors=2) |
| A′ code | `5b30662` | the 8 evolve-cal modules | `a3b/green-all.log`: Ran 216 OK |
| RED3 | `7ab03ec` | the seat's ruling's tests (analyse, gate) on the `5b30662` code | `a3c/red3.log`: Ran 109, FAILED (failures=3, errors=12) |
| ruling code | `67d620f` | the 8 evolve-cal modules | `a3c/green3-all.log`: Ran 232 OK |

## Mutation sweeps (a NAMED catching test per mutant; a COMMITTED, DETACHED checkout; `scripts/mutsweep.py`)

| module under sweep | mutants | at | table | note |
|---|---|---|---|---|
| `tools/evolve_cal_analyse.py` | 59 caught by the named test, 0 other | `67d620f` | `a3c/sweeps/analyse.out` (+ `analyse-mutsweep.json`) | the CURRENT table; `a3b/sweeps/analyse.out` (44 mutants at `5b30662`) is the earlier file's record and is superseded by it |
| `tools/evolve_bands.py` | 42 caught by the named test, 0 other | `67d620f` | `a3c/sweeps/bands.out` | the CURRENT table; `a3b/sweeps/bands.out` (37 of 38 at `5b30662` + one REFUSED mutant whose line the A′ edit had moved) and `bands-fix.out` (that one mutant re-aimed and CAUGHT) are the earlier record |
| `tools/evolve_cal.py` (twin comparison) | 33 caught, 0 other | `5b30662` | `a3b/sweeps/twin.out` | the file is unchanged since (`git diff 5b30662 67d620f -- tools/evolve_cal.py` is empty) |
| `tools/evolve_cal_queue.py` | 8 caught, 0 other | `5b30662` | `a3b/sweeps/queue.out` | unchanged since |

The rest of the instrument's sweeps (`evolve_pure`, `evolve_round`, `bandsbuild`) are the earlier files' (`/data/dev/swarm/2026-10-03/evolve-cal-records/sweeps*/`), on code this work did not touch.

## Re-running anything

    git worktree add --detach <copy> <sha>; cd <copy>
    SLOT_MEM=2G /data/dev/swarm/bin/slot integrator <label> -- env PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python3 -B -u -m unittest <modules>      # the modules are listed in scripts/a3b_chain.sh (MODS8)
    SLOT_MEM=2G /data/dev/swarm/bin/slot integrator <label> -- bash docs/organism/evolve/scripts/run_sweeps_ruled.sh <copy> <out>              # the CURRENT sweeps; run_sweeps_a3b.sh is the earlier four-module script

`SHA256SUMS` beside each directory lists its files; `a3b/a3b_arith.out` carries the arithmetic with the verifier's figures as aborting controls.
