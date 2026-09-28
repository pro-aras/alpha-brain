#!/bin/bash
# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:25 +0400 — S1b-1R's FULL RUN as ONE user unit (PREREG-S1B1R §7 with AMENDMENT 1), from a
# PINNED copy of the final code (tools/scene/pin_code_s1b1r.sh), never from a worktree a builder may still edit:
#   systemd-run --user --unit=scene-s1b1r -p Restart=no -p Nice=19 --setenv=PYTHONUNBUFFERED=1 \
#       --setenv=OPENBLAS_NUM_THREADS=1 --setenv=OMP_NUM_THREADS=1 --setenv=TMPDIR=/data/dev/brain-runs/tmp \
#       /bin/bash /data/dev/brain-runs/scene-s1b1r/code-<sha>/tools/scene/run_s1b1r.sh
# Waves: (0) the law's shas and THE FIRST GATE's PROCEED, (1) the fresh questions (pure functions of the caches drawn once
# by cache-r), (2) the four arms × three seeds = 12 at once, (3) the null draws k = 0..20, one process per seed, (4) the
# grader per seed, (5) the report. Every wave waits on ITS OWN pids and reads each exit code (never a bare `wait`).
set -u
CODE="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT=/data/dev/brain-runs/scene-s1b1r
PY=/usr/bin/python3
SEEDS="20261101 20261102 20261103"
ARMS="A-RW-R P-ORACLE-RW P-ORACLE ORACLE-TRUTH"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/data/dev/brain-runs/tmp
mkdir -p "$ROOT/logs" "$TMPDIR"
LOG="$ROOT/logs/full-run-r.log"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %z') $*" | tee -a "$LOG"; }
cd "$CODE" || exit 2
say "S1b-1R full run from $CODE (CODE_SHA $(cat "$CODE/CODE_SHA" 2>/dev/null || echo none)) under $PY"
$PY -B -c "from brain.scene import run as R; R.check_prereg(); from pathlib import Path; g = R.gate_or_chosen_r(Path('$ROOT')); print('gate', g['verdict'], 'lr', g['lr'], 'eps', g['eps'])" >> "$LOG" 2>&1 \
  || { say "STOP: the law's shas or THE FIRST GATE refuse the run (see $LOG)"; exit 3; }

# (1) the fresh questions
for ws in $SEEDS; do
  $PY -B -m brain.scene.run questions-r --root "$ROOT" --world-seed "$ws" >> "$LOG" 2>&1 || { say "STOP: questions-r $ws failed"; exit 2; }
done

# (2) the arms: 4 × 3 at once
declare -A AP=()
for ws in $SEEDS; do
  for arm in $ARMS; do
    nice -n 19 $PY -B -m brain.scene.run arm-r --root "$ROOT" --arm "$arm" --world-seed "$ws" > "$ROOT/logs/arm-r-$ws-$arm.out" 2>&1 &
    AP["$ws/$arm"]=$!
  done
done
say "12 arms started: $(for k in "${!AP[@]}"; do printf '%s=%s ' "$k" "${AP[$k]}"; done)"
fail=0
for k in "${!AP[@]}"; do
  wait "${AP[$k]}"; rc=$?
  say "arm $k exit $rc"
  [ "$rc" = 0 ] || fail=1
done
[ "$fail" = 0 ] || { say "STOP: an arm failed — no grade"; exit 2; }

# (3) the null: k = 0..20 per seed, one process per seed
declare -A NP=()
for ws in $SEEDS; do
  nice -n 19 $PY -B -m brain.scene.run null-r --root "$ROOT" --world-seed "$ws" --ks 0-20 > "$ROOT/logs/null-r-$ws.out" 2>&1 &
  NP["$ws"]=$!
done
say "3 null processes started: $(for k in "${!NP[@]}"; do printf '%s=%s ' "$k" "${NP[$k]}"; done)"
for k in "${!NP[@]}"; do
  wait "${NP[$k]}"; rc=$?
  say "null $k exit $rc"
  [ "$rc" = 0 ] || fail=1
done
[ "$fail" = 0 ] || { say "STOP: a null process failed — no grade"; exit 2; }

# (4) the grader and (5) the report
for ws in $SEEDS; do
  $PY -B -m brain.scene.run grade-r --root "$ROOT" --world-seed "$ws" >> "$LOG" 2>&1 || { say "STOP: grade-r $ws failed"; exit 2; }
done
$PY -B -m brain.scene.run report-r --root "$ROOT" >> "$LOG" 2>&1 || { say "STOP: report-r failed"; exit 2; }
say "S1b-1R DONE — $ROOT/report.txt"
exit 0
