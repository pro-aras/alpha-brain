#!/bin/bash
# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:57 +0400 — S1b-1's FULL RUN as ONE user unit (PREREG-S1B1 §11): S1a's waves under the
# FRESH run root /data/dev/brain-runs/scene-s1b1, six arms (A-RW at lr 0.01 · A-RW-LR10 · N-SHUF · P-ORACLE-RW · P-ORACLE ·
# ORACLE-TRUTH) × three seeds = 18 at once. Launched from a PINNED copy:
#   systemd-run --user --unit=scene-s1b1 -p Restart=no -p Nice=19 --setenv=PYTHONUNBUFFERED=1 \
#       --setenv=OPENBLAS_NUM_THREADS=1 --setenv=OMP_NUM_THREADS=1 --setenv=TMPDIR=/data/dev/brain-runs/tmp \
#       /bin/bash /data/dev/brain-runs/scene/code-<sha>/tools/scene/run_s1b1.sh
# (below: S1a's script, copied; its own header lines kept as the record of where it came from)
# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:25 +0400 — S1a's FULL RUN as ONE user unit (PREREG-R3-TONIGHT §S1a; brief step 8).
# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:04 +0400 — AMENDMENT 2: six arms (+ A-RW-LR01, a reading arm) × three seeds = 18 at once.
# Run from a PINNED copy of the code (tools/scene/pin_code.sh), never from a worktree a builder may still edit:
#   systemd-run --user --unit=scene-s1a -p Restart=no -p Nice=19 --setenv=PYTHONUNBUFFERED=1 \
#       --setenv=OPENBLAS_NUM_THREADS=1 --setenv=OMP_NUM_THREADS=1 --setenv=TMPDIR=/data/dev/brain-runs/tmp \
#       /bin/bash /data/dev/brain-runs/scene/code-<sha>/tools/scene/run_s1a.sh
# Waves: (1) any missing per-seed cache (in parallel), (2) the questions, (3) the 15 arms at once (5 arms × 3 seeds),
# (4) the grader and the report. Every wave waits on ITS OWN pids and reads each exit code (never a bare `wait`).
set -u
CODE="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT=/data/dev/brain-runs/scene-s1b1
PY=/usr/bin/python3
SEEDS="20261101 20261102 20261103"
ARMS="A-RW A-RW-LR10 N-SHUF P-ORACLE-RW P-ORACLE ORACLE-TRUTH"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/data/dev/brain-runs/tmp
mkdir -p "$ROOT/logs" "$TMPDIR"
LOG="$ROOT/logs/full-run.log"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %z') $*" | tee -a "$LOG"; }
cd "$CODE" || exit 2
say "S1b-1 full run from $CODE (CODE_SHA $(cat "$CODE/CODE_SHA" 2>/dev/null || echo none)) under $PY"
$PY -B -c "from brain.scene import run as R; R.check_prereg(); from pathlib import Path; g = R.gate_or_chosen(Path('/data/dev/brain-runs/scene-s1b1')); print('gate', g['verdict'], 'lr', g['lr'], 'eps', g['eps'])" >> "$LOG" 2>&1 \
  || { say "STOP: the PREREG's sha or THE FIRST GATE refuses the run (see $LOG)"; exit 3; }

# (1) caches: only the seeds not yet written (a cache is written once)
declare -A CP=()
for ws in $SEEDS; do
  if [ ! -f "$ROOT/$ws/cache/disjoint.json" ]; then
    nice -n 19 $PY -B -m brain.scene.run cache-world --root "$ROOT" --world-seed "$ws" > "$ROOT/logs/cache-world-$ws.out" 2>&1 &
    CP[$ws]=$!
    say "cache-world $ws started pid ${CP[$ws]}"
  fi
done
for ws in "${!CP[@]}"; do
  wait "${CP[$ws]}"; rc=$?
  say "cache-world $ws exit $rc"
  [ "$rc" = 0 ] || { say "STOP: cache-world $ws failed"; exit 2; }
done

# (2) the questions (deterministic from the truth; rewritten identically)
for ws in $SEEDS; do
  $PY -B -m brain.scene.run questions --root "$ROOT" --world-seed "$ws" >> "$LOG" 2>&1 || { say "STOP: questions $ws failed"; exit 2; }
done

# (3) the launch's shape: 6 arms × 3 seeds at once (AMENDMENT 2 §5 adds the reading arm A-RW-LR01)
declare -A AP=()
for ws in $SEEDS; do
  for arm in $ARMS; do
    nice -n 19 $PY -B -m brain.scene.run arm --root "$ROOT" --arm "$arm" --world-seed "$ws" > "$ROOT/logs/arm-$ws-$arm.out" 2>&1 &
    AP["$ws/$arm"]=$!
  done
done
say "18 arms started: $(for k in "${!AP[@]}"; do printf '%s=%s ' "$k" "${AP[$k]}"; done)"
fail=0
for k in "${!AP[@]}"; do
  wait "${AP[$k]}"; rc=$?
  say "arm $k exit $rc"
  [ "$rc" = 0 ] || fail=1
done
[ "$fail" = 0 ] || { say "STOP: an arm failed — no grade"; exit 2; }

# (4) the grader and the report
for ws in $SEEDS; do
  $PY -B -m brain.scene.run grade --root "$ROOT" --world-seed "$ws" >> "$LOG" 2>&1 || { say "STOP: grade $ws failed"; exit 2; }
done
$PY -B -m brain.scene.run report --root "$ROOT" >> "$LOG" 2>&1 || { say "STOP: report failed"; exit 2; }
say "S1b-1 DONE — $ROOT/report.txt"
exit 0
