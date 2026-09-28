#!/bin/bash
# edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 18:28 +0400 — T-MEM-5's FULL RUN as ONE user unit (PREREG-TMEM5 §6, sha 30121082…, with its
# AMENDMENT 1, sha ab9a5fca…): 14 arms × 3 seeds in five waves (the slow ORACLEs first), then RANDOM-CTX's band on each learner
# (20 lives per seed, 6 processes of 10 per learner), then the report (the identity against S1c's records, MEMORY, CURIOSITY,
# the readings). The pools are scene-tmem1's. Every wave waits on ITS OWN pids and reads each exit code (never a bare
# `wait`). Launched from a PINNED copy, after scene-tmem1, never beside another scene unit:
#   systemd-run --user --unit=scene-tmem5 -p Restart=no -p Nice=19 --setenv=PYTHONUNBUFFERED=1 \
#       --setenv=OPENBLAS_NUM_THREADS=1 --setenv=OMP_NUM_THREADS=1 --setenv=TMPDIR=/data/dev/brain-runs/tmp \
#       /bin/bash /data/dev/brain-runs/scene/code-<sha>/tools/scene/run_tmem5.sh
set -u
CODE="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT=/data/dev/brain-runs/scene-tmem5
PY=/usr/bin/python3
SEEDS="20261301 20261302 20261303"
WAVES=("ORACLE-CTX ORACLE-CTX+REPLAY" "PROGRESS-CTX PROGRESS-CTX+REPLAY RANDOM-CTX" "RANDOM-CTX+REPLAY NULL-CTX NULL-CTX+REPLAY" \
       "SHUFFLED-CTX SHUFFLED-CTX-RANDOM BIAS-ONLY-RANDOM" "BIAS-ONLY-PROGRESS FROZEN-PROGRESS FROZEN-RANDOM")
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/data/dev/brain-runs/tmp
mkdir -p "$ROOT/logs" "$TMPDIR"
LOG="$ROOT/logs/full-run.log"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %z') $*" | tee -a "$LOG"; }
cd "$CODE" || exit 2
say "T-MEM-5 full run from $CODE (CODE_SHA $(cat "$CODE/CODE_SHA" 2>/dev/null || echo none)) under $PY"
$PY -B -c "from brain.scene import run_tmem5 as T; print('shas', T.check_prereg()); print('gate', T.gate_ok()['verdict'])" >> "$LOG" 2>&1 \
  || { say "STOP: the shas or THE FIRST GATE refuse the run (see $LOG)"; exit 3; }

w=0
for picks in "${WAVES[@]}"; do
  w=$((w + 1))
  declare -A AP=()
  for s in $SEEDS; do
    for a in $picks; do
      nice -n 19 $PY -B -m brain.scene.run_tmem5 run --root "$ROOT" --arm "$a" --seed "$s" > "$ROOT/logs/run-$s-$a.out" 2>&1 &
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

for learner in ctx ctx-replay; do
  declare -A BP=()
  for s in $SEEDS; do
    for ks in 1-10 11-20; do
      nice -n 19 $PY -B -m brain.scene.run_tmem5 band --root "$ROOT" --learner "$learner" --seed "$s" --k "$ks" > "$ROOT/logs/band-$learner-$s-$ks.out" 2>&1 &
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

$PY -B -m brain.scene.run_tmem5 report --root "$ROOT" >> "$LOG" 2>&1 || { say "STOP: report failed"; exit 2; }
say "T-MEM-5 DONE — $ROOT/report.txt"
exit 0
