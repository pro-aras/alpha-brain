#!/bin/bash
# edit: Claude (Opus 5.5, S1c-2 builder), 2026-09-28 16:22 +0400 — S1c-2's FULL RUN as ONE user unit (PREREG-S1C2 §8, sha 5e4585c1…): 14 arms ×
# 3 seeds in five waves (the slow ORACLEs first), then RANDOM's band on each learner (20 lives per seed, 6 processes of 10 per
# learner), then the report (the identity control against S1c's records, the bars, the readings). The pools are S1c's.
# Every wave waits on ITS OWN pids and reads each exit code (never a bare `wait`). Launched from a PINNED copy:
#   systemd-run --user --unit=scene-s1c2 -p Restart=no -p Nice=19 --setenv=PYTHONUNBUFFERED=1 \
#       --setenv=OPENBLAS_NUM_THREADS=1 --setenv=OMP_NUM_THREADS=1 --setenv=TMPDIR=/data/dev/brain-runs/tmp \
#       /bin/bash /data/dev/brain-runs/scene/code-<sha>/tools/scene/run_s1c2.sh
set -u
CODE="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT=/data/dev/brain-runs/scene-s1c2
PY=/usr/bin/python3
SEEDS="20261301 20261302 20261303"
WAVES=("ORACLE ORACLE+REPLAY RANDOM" "PROGRESS ERROR NULL" "PROGRESS-NET NULL-NET PROGRESS-UCB" \
       "PROGRESS+REPLAY ERROR+REPLAY RANDOM+REPLAY" "NULL+REPLAY PROGRESS+REPLAY-V")
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/data/dev/brain-runs/tmp
mkdir -p "$ROOT/logs" "$TMPDIR"
LOG="$ROOT/logs/full-run.log"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %z') $*" | tee -a "$LOG"; }
cd "$CODE" || exit 2
say "S1c-2 full run from $CODE (CODE_SHA $(cat "$CODE/CODE_SHA" 2>/dev/null || echo none)) under $PY"
$PY -B -c "from brain.scene import run_s1c2 as S2; print('shas', S2.check_prereg()); print('gate', S2.gate_ok()['verdict'])" >> "$LOG" 2>&1 \
  || { say "STOP: the shas or THE FIRST GATE refuse the run (see $LOG)"; exit 3; }

w=0
for picks in "${WAVES[@]}"; do
  w=$((w + 1))
  declare -A AP=()
  for s in $SEEDS; do
    for a in $picks; do
      nice -n 19 $PY -B -m brain.scene.run_s1c2 run --root "$ROOT" --arm "$a" --seed "$s" > "$ROOT/logs/run-$s-$a.out" 2>&1 &
      AP["$s/$a"]=$!
    done
  done
  say "wave $w: ${#AP[@]} lives started: $(for k in "${!AP[@]}"; do printf '%s=%s ' "$k" "${AP[$k]}"; done)"
  fail=0
  for k in "${!AP[@]}"; do
    wait "${AP[$k]}"; rc=$?
    say "life $k exit $rc"
    [ "$rc" = 0 ] || fail=1
  done
  unset AP
  [ "$fail" = 0 ] || say "a life of wave $w FAILED — it reads NOT GRADABLE BY NAME; the run goes on"
done

for learner in bare replay; do
  declare -A BP=()
  for s in $SEEDS; do
    for ks in 1-10 11-20; do
      nice -n 19 $PY -B -m brain.scene.run_s1c2 band --root "$ROOT" --learner "$learner" --seed "$s" --k "$ks" > "$ROOT/logs/band-$learner-$s-$ks.out" 2>&1 &
      BP["$s/$ks"]=$!
    done
  done
  say "$learner band: ${#BP[@]} processes started: $(for k in "${!BP[@]}"; do printf '%s=%s ' "$k" "${BP[$k]}"; done)"
  fail=0
  for k in "${!BP[@]}"; do
    wait "${BP[$k]}"; rc=$?
    say "band $learner $k exit $rc"
    [ "$rc" = 0 ] || fail=1
  done
  unset BP
  [ "$fail" = 0 ] || say "a band process of $learner FAILED — its band reads NOT GRADABLE BY NAME (printed with its n)"
done

$PY -B -m brain.scene.run_s1c2 report --root "$ROOT" >> "$LOG" 2>&1 || { say "STOP: report failed"; exit 2; }
say "S1c-2 DONE — $ROOT/report.txt"
exit 0
