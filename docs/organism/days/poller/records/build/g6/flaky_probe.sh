#!/bin/bash
# alternate the unchanged BASE (master 233a4cb) and the FIX tree (9d43829) on ONE wall-clock test, N times, under whatever load the box has; every line carries the load.
BASE=/data/dev/genome-wt-poller-base; FIX=/data/dev/genome-wt-poller-g1
T=tests.creature.test_gene_values.TestTapeDeclaredPath.test_declared_run_tape2_moves_the_directory
N=${1:-6}
for i in $(seq 1 $N); do
  for tree in $BASE $FIX; do
    cd $tree && mkdir -p scratch/tmp && export TMPDIR=$tree/scratch/tmp
    PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python3 -B -m unittest $T > scratch/tmp/probe.log 2>&1; rc=$?
    echo "$(date +%T) $(basename $tree) rc=$rc load=$(cut -d' ' -f1-3 /proc/loadavg) $(grep -a -E '^(OK|FAILED|AssertionError)' scratch/tmp/probe.log | tr '\n' ' ')"
  done
done
