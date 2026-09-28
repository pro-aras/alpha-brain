#!/bin/bash
# edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:15 +0400 — S1c's FULL RUN as ONE user unit (PREREG-S1C §8, AMENDMENT 1 §1 and §3 (b)):
# the pools of the seeds THE FIRST GATE did not draw, then 6 pickers × 3 seeds = 18 lives in two waves of 9 (RANDOM, ERROR,
# PROGRESS; then ORACLE, NULL, PROGRESS-DRIFT), then RANDOM's band (20 extra lives per seed, 6 processes of 10), then the
# report. Every wave waits on ITS OWN pids and reads each exit code (never a bare `wait`). Launched from a PINNED copy:
#   systemd-run --user --unit=scene-s1c -p Restart=no -p Nice=19 --setenv=PYTHONUNBUFFERED=1 \
#       --setenv=OPENBLAS_NUM_THREADS=1 --setenv=OMP_NUM_THREADS=1 --setenv=TMPDIR=/data/dev/brain-runs/tmp \
#       /bin/bash /data/dev/brain-runs/scene/code-<sha>/tools/scene/run_s1c.sh
set -u
CODE="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT=/data/dev/brain-runs/scene-s1c
PY=/usr/bin/python3
SEEDS="20261301 20261302 20261303"
WAVE1="RANDOM ERROR PROGRESS"
WAVE2="ORACLE NULL PROGRESS-DRIFT"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/data/dev/brain-runs/tmp
mkdir -p "$ROOT/logs" "$TMPDIR"
LOG="$ROOT/logs/full-run.log"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %z') $*" | tee -a "$LOG"; }
cd "$CODE" || exit 2
say "S1c full run from $CODE (CODE_SHA $(cat "$CODE/CODE_SHA" 2>/dev/null || echo none)) under $PY"
$PY -B -c "from brain.scene import run_s1c as S; print('shas', S.check_prereg()); print('rooms', S.gate_rooms())" >> "$LOG" 2>&1 \
  || { say "STOP: the shas or THE FIRST GATE refuse the run (see $LOG)"; exit 3; }

# (0) the pools of every seed whose twelve caches are not all written (a cache is written once; existing ones are kept)
declare -A CP=()
for s in $SEEDS; do
  n=$(ls -d "$ROOT/$s/rooms/"*-visit "$ROOT/$s/rooms/"*-window 2>/dev/null | grep -vc building)
  if [ "$n" != 12 ]; then
    nice -n 19 $PY -B -m brain.scene.run_s1c cache-rooms --root "$ROOT" --seed "$s" > "$ROOT/logs/cache-rooms-$s.out" 2>&1 &
    CP[$s]=$!
    say "cache-rooms $s started pid ${CP[$s]} ($n of 12 written)"
  fi
done
for s in "${!CP[@]}"; do
  wait "${CP[$s]}"; rc=$?
  say "cache-rooms $s exit $rc"
  [ "$rc" = 0 ] || { say "STOP: cache-rooms $s failed"; exit 2; }
done

# (1)–(2) the lives: two waves of 9
for wave in 1 2; do
  [ "$wave" = 1 ] && PICKS="$WAVE1" || PICKS="$WAVE2"
  declare -A AP=()
  for s in $SEEDS; do
    for p in $PICKS; do
      nice -n 19 $PY -B -m brain.scene.run_s1c run --root "$ROOT" --picker "$p" --seed "$s" > "$ROOT/logs/run-$s-$p.out" 2>&1 &
      AP["$s/$p"]=$!
    done
  done
  say "wave $wave: ${#AP[@]} lives started: $(for k in "${!AP[@]}"; do printf '%s=%s ' "$k" "${AP[$k]}"; done)"
  fail=0
  for k in "${!AP[@]}"; do
    wait "${AP[$k]}"; rc=$?
    say "life $k exit $rc"
    [ "$rc" = 0 ] || fail=1
  done
  unset AP
  [ "$fail" = 0 ] || { say "STOP: a life of wave $wave failed — no report"; exit 2; }
done

# (3) RANDOM's band (AMENDMENT 1 §3 (b)): 20 extra lives per seed, 6 processes of 10
declare -A BP=()
for s in $SEEDS; do
  for ks in 1-10 11-20; do
    nice -n 19 $PY -B -m brain.scene.run_s1c band --root "$ROOT" --seed "$s" --k "$ks" > "$ROOT/logs/band-$s-$ks.out" 2>&1 &
    BP["$s/$ks"]=$!
  done
done
say "the band: ${#BP[@]} processes started: $(for k in "${!BP[@]}"; do printf '%s=%s ' "$k" "${BP[$k]}"; done)"
fail=0
for k in "${!BP[@]}"; do
  wait "${BP[$k]}"; rc=$?
  say "band $k exit $rc"
  [ "$rc" = 0 ] || fail=1
done
[ "$fail" = 0 ] || { say "STOP: a band process failed — no report"; exit 2; }

# (4) the report
$PY -B -m brain.scene.run_s1c report --root "$ROOT" >> "$LOG" 2>&1 || { say "STOP: report failed"; exit 2; }
say "S1c DONE — $ROOT/report.txt"
exit 0
