#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 23:5x +0400 — the mutation sweeps of THE SEAT'S RULING ON A3b (23:36): the analysis module (Stage B rule M, A′ by default in every branch, the null provenance) and the bands module
# (the strict loader), each mutant with a NAMED catching test, against a COMMITTED, DETACHED checkout (the twin comparison and the queue are unchanged since run_sweeps_a3b.sh and are not re-swept).
# usage: bash run_sweeps_ruled.sh <detached checkout of the commit under test> <out dir>
set -u
TREE=${1:?tree}; O=${2:?out}
cd "$TREE" || exit 2
mkdir -p scratch "$O"
git -C "$TREE" rev-parse HEAD > "$O/CODE-SHA.txt"
SW=docs/organism/evolve/scripts
export OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
python3 -B $SW/mutsweep.py --tree . --module tools/evolve_cal_analyse.py --tests tests.tools.test_evolve_cal_analyse --mutants $SW/mutants_cal_analyse.json --out $O/analyse > $O/analyse.out 2>&1; echo "analyse exit $?" >> $O/SWEEPS.done
python3 -B $SW/mutsweep.py --tree . --module tools/evolve_bands.py --tests tests.tools.test_evolve_cal_gate --mutants $SW/mutants_cal_bands.json --out $O/bands > $O/bands.out 2>&1; echo "bands exit $?" >> $O/SWEEPS.done
echo "ALL SWEEPS RAN" >> $O/SWEEPS.done
