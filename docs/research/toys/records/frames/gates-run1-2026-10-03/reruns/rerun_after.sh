#!/bin/bash
# the timing diagnosis on the NEW code (the working tree with the NULL-2 speed-up), output to a file; run through slot. Exit code captured before the date call.
set -u
WT=/data/dev/genome-wt-toys-1003
COPIES=$WT/scratch/toys-frames/copies
OUT=$WT/scratch/gates-run1-reruns
cd "$WT" || exit 97
export PYTHONPATH="$WT" OPENBLAS_NUM_THREADS=1 PYTHONUNBUFFERED=1
echo "$(date '+%F %T %z') start; code: $(git rev-parse --short HEAD) + the uncommitted null.py speed-up (sha256 $(sha256sum tools/toys/frames/null.py | cut -c1-16)); load $(cut -d' ' -f1-3 /proc/loadavg); pressure $(grep -a '^some' /proc/pressure/cpu)" > "$OUT/after.clock"
/usr/bin/python3 -B -u scratch/g5_cost_diag.py "$COPIES" > "$OUT/after-g5_cost_diag.log" 2>&1
rc=$?
echo "$(date '+%H:%M:%S') g5_cost_diag exit $rc" >> "$OUT/after.clock"
echo "$(date '+%F %T %z') end; load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$OUT/after.clock"
