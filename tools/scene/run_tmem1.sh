#!/bin/bash
# edit: Claude (Opus 5.5, T-MEM-1 builder), 2026-09-28 17:34 +0400 — T-MEM-1's FULL RUN as ONE user unit (PREREG-TMEM1 §5, sha 0a87fefc…): the eight
# training lives × two schedules × three seeds = 48 lives, one life kind per wave (6 processes: 3 seeds × 2 schedules), then
# the report. The pools were redrawn and TESTED equal to S1c's before THE FIRST GATE. Every wave waits on ITS OWN pids and
# reads each exit code (never a bare `wait`). Launched from a PINNED copy:
#   systemd-run --user --unit=scene-tmem1 -p Restart=no -p Nice=19 --setenv=PYTHONUNBUFFERED=1 \
#       --setenv=OPENBLAS_NUM_THREADS=1 --setenv=OMP_NUM_THREADS=1 --setenv=TMPDIR=/data/dev/brain-runs/tmp \
#       /bin/bash /data/dev/brain-runs/scene/code-<sha>/tools/scene/run_tmem1.sh
set -u
CODE="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT=/data/dev/brain-runs/scene-tmem1
PY=/usr/bin/python3
SEEDS="20261301 20261302 20261303"
LIVES="BASE GATE GATE-RANDOM ORACLE-DRIFT DRIFT DRIFT-NULL SURPRISE UNIFORM"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/data/dev/brain-runs/tmp
mkdir -p "$ROOT/logs" "$TMPDIR"
LOG="$ROOT/logs/full-run.log"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %z') $*" | tee -a "$LOG"; }
cd "$CODE" || exit 2
say "T-MEM-1 full run from $CODE (CODE_SHA $(cat "$CODE/CODE_SHA" 2>/dev/null || echo none)) under $PY"
$PY -B -c "from brain.scene import run_tmem1 as T; print('shas', T.check_prereg()); print('gate', T.gate_ok()['verdict'])" >> "$LOG" 2>&1 \
  || { say "STOP: the shas or THE FIRST GATE refuse the run (see $LOG)"; exit 3; }
w=0
for life in $LIVES; do
  w=$((w + 1))
  declare -A AP=()
  for s in $SEEDS; do
    for sch in seq random; do
      nice -n 19 $PY -B -m brain.scene.run_tmem1 run --root "$ROOT" --life "$life" --schedule "$sch" --seed "$s" > "$ROOT/logs/run-$s-$sch-$life.out" 2>&1 &
      AP["$s/$sch"]=$!
    done
  done
  say "wave $w ($life): ${#AP[@]} lives started: $(for k in "${!AP[@]}"; do printf '%s=%s ' "$k" "${AP[$k]}"; done)"
  fail=0
  for k in "${!AP[@]}"; do
    wait "${AP[$k]}"; rc=$?
    say "life $life $k exit $rc"
    [ "$rc" = 0 ] || fail=1
  done
  unset AP
  [ "$fail" = 0 ] || say "a $life life FAILED — it reads NOT GRADABLE BY NAME; the run goes on"
done
$PY -B -m brain.scene.run_tmem1 report --root "$ROOT" >> "$LOG" 2>&1 || { say "STOP: report failed"; exit 2; }
say "T-MEM-1 DONE — $ROOT/report.txt"
exit 0
