#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 23:0x +0400 — AMENDMENT 3b's mutation sweeps: the analysis module, the twin comparison and the queue's list writer, each mutant with a
# NAMED catching test, against a COMMITTED, DETACHED checkout (run_sweeps.sh's rule: an edit in the working tree must not contaminate a sweep).
# usage: bash run_sweeps_a3b.sh <detached checkout of the commit under test> <out dir>
set -u
TREE=${1:?tree}; O=${2:?out}
cd "$TREE" || exit 2
mkdir -p scratch "$O"
git -C "$TREE" rev-parse HEAD > "$O/CODE-SHA.txt"
SW=docs/organism/evolve/scripts
export OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
python3 -B $SW/mutsweep.py --tree . --module tools/evolve_cal_analyse.py --tests tests.tools.test_evolve_cal_analyse --mutants $SW/mutants_cal_analyse.json --out $O/analyse > $O/analyse.out 2>&1; echo "analyse exit $?" >> $O/SWEEPS.done
python3 -B $SW/mutsweep.py --tree . --module tools/evolve_cal_queue.py --tests tests.tools.test_evolve_cal_queue --mutants $SW/mutants_cal_queue.json --out $O/queue > $O/queue.out 2>&1; echo "queue exit $?" >> $O/SWEEPS.done
python3 -B $SW/mutsweep.py --tree . --module tools/evolve_cal.py --tests tests.tools.test_evolve_cal_twin --mutants $SW/mutants_cal_twin.json --out $O/twin > $O/twin.out 2>&1; echo "twin exit $?" >> $O/SWEEPS.done
echo "ALL SWEEPS RAN" >> $O/SWEEPS.done
