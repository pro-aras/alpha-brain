#!/bin/bash
# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:40 +0400 — T-MEM-2's run as ONE user unit (PREREG-TMEM2 §8), from a PINNED copy of the
# final code (tools/scene/pin_code_tmem2.sh), never beside another unit:
#   systemd-run --user --unit=scene-tmem2 -p Restart=no -p Nice=19 --setenv=PYTHONUNBUFFERED=1 \
#       --setenv=OPENBLAS_NUM_THREADS=1 --setenv=OMP_NUM_THREADS=1 --setenv=TMPDIR=/data/dev/brain-runs/tmp \
#       /bin/bash /data/dev/brain-runs/scene-tmem2/code-<sha>/tools/scene/run_tmem2.sh
# Waves: (0) the laws' shas and THE FIRST GATE's PROCEED; (1) the three HEALTH lives at once (each checks its identity with
# S1b-1R's record and exits 3 on a miss — a STOP before any grade); (2) the grader per seed; (3) the report. Every wave waits on
# ITS OWN pids and reads each exit code (never a bare `wait`).
set -u
CODE="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT=/data/dev/brain-runs/scene-tmem2
PY=/usr/bin/python3
SEEDS="20261101 20261102 20261103"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/data/dev/brain-runs/tmp
mkdir -p "$ROOT/logs" "$TMPDIR"
LOG="$ROOT/logs/full-run.log"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %z') $*" | tee -a "$LOG"; }
cd "$CODE" || exit 2
say "T-MEM-2 run from $CODE (CODE_SHA $(cat "$CODE/CODE_SHA" 2>/dev/null || echo none)) under $PY"
$PY -B -c "from brain.scene import run_tmem2 as T; T.check_prereg_tmem2(); g = T.gate_or_chosen_tmem2(); print('gate', g['verdict'], 'sha', g['prereg_tmem2_sha256'][:16])" >> "$LOG" 2>&1 \
  || { say "STOP: the law's shas or THE FIRST GATE refuse the run (see $LOG)"; exit 3; }

# (1) the three HEALTH lives at once
declare -A LP=()
for ws in $SEEDS; do
  nice -n 19 $PY -B -m brain.scene.run_tmem2 life --world-seed "$ws" > "$ROOT/logs/life-$ws.out" 2>&1 &
  LP[$ws]=$!
done
say "3 lives started: $(for k in "${!LP[@]}"; do printf '%s=%s ' "$k" "${LP[$k]}"; done)"
fail=0
for k in "${!LP[@]}"; do
  wait "${LP[$k]}"; rc=$?
  say "life $k exit $rc"
  [ "$rc" = 0 ] || fail=1
done
[ "$fail" = 0 ] || { say "STOP: a life failed or its identity missed — no grade"; exit 3; }

# (2) the grader and (3) the report
for ws in $SEEDS; do
  $PY -B -m brain.scene.run_tmem2 grade --world-seed "$ws" >> "$LOG" 2>&1 || { say "STOP: grade $ws failed"; exit 2; }
done
$PY -B -m brain.scene.run_tmem2 report >> "$LOG" 2>&1 || { say "STOP: report failed"; exit 2; }
say "T-MEM-2 DONE — $ROOT/report.txt"
exit 0
