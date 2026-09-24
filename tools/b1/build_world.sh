#!/bin/bash
# tools/b1/build_world.sh — THE QUIET-WINDOW ROAD: stage −1 FULL, then the graded tape for one seed (B1-PREREG.md §3, §2).
# edit: Claude (Fable 5.1), 2026-09-24 18:56 +0400 — the seat, alone.
# Usage: tools/b1/build_world.sh <seed> [--force]     (from the b1 tree; /usr/bin/python3 for both steps, §3.0)
# Refuses to start stage −1 above load 8 unless --force (stage −1's own cadence rule); the tape follows only if
# stage −1 wrote its ceilings.json; every step's exit code is read from the step itself, never from a pipe (#191).
set -u
SEED="${1:?seed}"; FORCE="${2:-}"
cd "$(dirname "$0")/../.." || exit 2
ROOT=/data/dev/brain-runs/b1
LOGDIR=$ROOT/logs; mkdir -p "$LOGDIR"
TS=$(date +%Y%m%d-%H%M)
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/tmp
echo "[world] $(date '+%F %T') seed $SEED · load $(cut -d' ' -f1 /proc/loadavg) · tree $(git rev-parse --short HEAD)"
if [ ! -f docs/brain/b1/stage-1/ceilings.json ] || ! python3 -c "import json,sys; d=json.load(open('docs/brain/b1/stage-1/ceilings.json')); sys.exit(0 if not d.get('smoke') and 'never_taught_pools' in d else 1)"; then
  echo "[world] stage −1 FULL → $LOGDIR/stage1-$TS.log"
  nice -n 19 /usr/bin/python3 -m brain.harness.stage_minus1 --seed "$SEED" ${FORCE:+--force} > "$LOGDIR/stage1-$TS.log" 2>&1
  rc=$?
  echo "[world] stage −1 exit $rc"
  if [ $rc -ne 0 ]; then tail -n 20 "$LOGDIR/stage1-$TS.log"; exit $rc; fi
else
  echo "[world] stage −1 ceilings.json present (FULL) — kept"
fi
if [ -f "$ROOT/$SEED/tape.jsonl" ]; then echo "[world] tape for $SEED exists — a tape is written ONCE (§2.6); nothing to do"; exit 0; fi
echo "[world] tape seed $SEED → $LOGDIR/tape-$SEED-$TS.log"
nice -n 19 /usr/bin/python3 -m brain.world.tape --seed "$SEED" --stage1 docs/brain/b1/stage-1/ceilings.json --out-root "$ROOT" > "$LOGDIR/tape-$SEED-$TS.log" 2>&1
rc=$?
echo "[world] tape exit $rc"
grep -a -E '^\[tape\] (schedule|cache built|rows|sleeps|plant|mlc|DISJOINT|tape.jsonl)' "$LOGDIR/tape-$SEED-$TS.log"
exit $rc
