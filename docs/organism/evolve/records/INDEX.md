# EVOLVE-CAL — the builder's records, one page

*Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:2x +0400. Law: `docs/organism/evolve/PREREG-EVOLVE-CAL.md` (signed ×3 with A1, A2; AMENDMENT 3 drafted by the builder, awaiting the verifier and the seat). Branch `evolve-cal-1003` (worktree `/data/dev/genome-wt-evolve-cal-1003`), base master 3f9db48; it carries NO organism code (`git diff --name-only <base> HEAD -- creature brain genome/*.py genome/*/*.py` is empty) and merges cleanly into master 233a4cb.*

## What is built (code of the law's §1 and the calibration's instrument)

| file | what | its tests (written first, RED logs under `records/logs/`) |
|---|---|---|
| `tools/evolve.py` | D3 (the `surprise_mark` call), D6 (`grade_twin(cpu_s, machine)`), D8 (`draw_stream` / `mutate_distinct`: the proposer's redraw, `creature/` untouched), `run_judging_round(bands=)` (None = the legacy round), the confirmation round (`finalize_calibrated_round`, `PENDING-CONFIRM.json`), `--bands` | `tests/tools/test_evolve_cal_d3.py`, `…_gate.py` (proposer), `…_round.py` (the round, the confirmation) |
| `tools/evolve_bands.py` (stdlib only) | `position`, three verdicts, the banded cost under the 1.2 cap, NOT GRADABLE with presence counts, `confirm_decision`, `validate_bands` | `…_gate.py` |
| `tools/evolve_cal.py` | genome variants (one number), `stage-slice` / `stage-checkpoint` with verifiers, the twin runner, `compare_twins` and `compare_twins_keyed`, `make_band` / `make_bands` / `variance_ratio_test` / `frames_band` (scipy) | `…_twin.py`, `…_bands_build.py` |
| `tools/evolve_cal_queue.py` | a list of twins, ONE at a time through slot at 8G, resumable | `…_queue.py` |
| `tools/evolve_cal_analyse.py` | the staged decisions of AMENDMENT 3 (A0, A0+, Stage B), `choose_level`, `bands_from_twins` with both readings of A1 (i) | `…_analyse.py` |

## What was measured (the STOP stage; nothing is a full run)

`records/stop/` (README.md inside): seven twins, the replication and determinism controls, the SEED pair, the epsilon ladder 1e-5 … 1e-2, the report and its table; `records/stop/READING-RULE-LADDER.md` committed BEFORE the first probe finished (513f382). Also read now, no twin needed: `records/e3/` (E3 re-graded: `confirmed_share` graded on 13 of 13 judged rounds, the stripped plant caught, C4 PASS; 0 of 13 recorded verdicts change under the legacy bar once it is graded) and `records/c5/` (the raw proposer collides with the incumbent's own value 11 times in 150 draws, the redrawn one 0: C5 PASS). The staged queue's lists: `records/lists/`.

## How the instrument itself was checked

- RED then GREEN for every module (`records/logs/*-red.log`, `*-green*.log`); the full evolve-cal run with the existing worker tests: `all-green6.log` (Ran 133 OK).
- Mutation sweeps with a NAMED catching test per mutant, on a COMMITTED, DETACHED checkout (`scripts/mutsweep.py`, `scripts/run_sweeps.sh`, the mutant files `scripts/mutants_cal_*.json`); results under `/data/dev/swarm/2026-10-03/evolve-cal-records/sweeps-*` (the first sweep, at 73d059e, is superseded: it found the cheaper-twin equivalent mutant, an obsolete mutant and a runaway one, all fixed).
- A rehearsal of the landing gate on a scratch worktree (master + this branch merged, `scratch/dry_landing.sh`): genome «Ran 713 … OK (skipped=1, expected failures=6)», tools «Ran 512 … OK (skipped=25)» — the 25 skips are the pool-gated toys tests of a worktree that has no `scratch/toys-pools`; int-1003 has them and must read 0 skipped.
- An independent second path for the replication claim (plain `json`, not this branch's comparison): 935 of 935 rows equal, canonical bytes equal.
- Running a full run: `docs/organism/evolve/scripts/launch_queue.sh <sha> docs/organism/evolve/records/lists/N1-A0.tsv /data/dev/swarm/2026-10-03/evolve-cal-records/n1 a0` (a clean detached checkout of that sha, `DRY=1` prints the plan) — NOT before the verifier's co-signature and the seat's signature on AMENDMENT 3.
