#!/bin/bash
# the three diagnosis scripts on the OLD tree (commit 724865d), each output to its own file; run through slot. The exit code is captured BEFORE the date call (SOLUTIONS #244 (7)).
set -u
OLD=/data/dev/genome-wt-toys-1003/scratch/tmp/old724865d
COPIES=/data/dev/genome-wt-toys-1003/scratch/toys-frames/copies
OUT=/data/dev/genome-wt-toys-1003/scratch/gates-run1-reruns
rm -rf "$OUT"; mkdir -p "$OUT"
cd "$OLD" || exit 97
export PYTHONPATH="$OLD" OPENBLAS_NUM_THREADS=1 PYTHONUNBUFFERED=1
echo "$(date '+%F %T %z') start; code of the tree: 724865d (git archive tools genome brain); load $(cut -d' ' -f1-3 /proc/loadavg); pressure $(grep -a '^some' /proc/pressure/cpu)" > "$OUT/before.clock"
for s in g5_cost_diag g5_cost_prof g5_cost_count; do
  /usr/bin/python3 -B -u scratch/$s.py "$COPIES" > "$OUT/before-$s.log" 2>&1
  rc=$?
  echo "$(date '+%H:%M:%S') $s exit $rc" >> "$OUT/before.clock"
done
echo "$(date '+%F %T %z') end; load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$OUT/before.clock"
