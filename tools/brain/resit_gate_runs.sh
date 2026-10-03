#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:29 +0400 — PREREG-RESIT-READER R14, R2, R3 and R1': the law's gate runs on a CLOSED life, one orchestrator call each, sequentially, each with /usr/bin/time -v.
# The caller wraps the whole script in `slot` (one scope, one cap). Nothing here is written under a life; the OUT folder is the reader's own.
#
# usage: resit_gate_runs.sh <reader-checkout> <out> <records-dir> <life-root> <life-code> <grader-code> <scored> <reference-grade> <other-code> <step>...
#   steps:  r14   the turn pin (Brain.turn read-only on a second load of the state)
#           r2    cold cache, warm, a third time (three processes, three hash seeds), and one warm run under OPENBLAS_NUM_THREADS=4 (a READING)
#           r3    the nudge plant at eps 0.001 0.01 0.1 0.5 (the bar is eps 0.5; the others are readings)
#           r1p   R1' — the OTHER code (brain-long-3's) answering the closed life's brain on the same items
set -u
if [ "$#" -lt 10 ]; then echo "usage: resit_gate_runs.sh <reader-checkout> <out> <records-dir> <life-root> <life-code> <grader-code> <scored> <reference-grade> <other-code> <step>..." >&2; exit 64; fi
READER=$1; OUT=$2; REC=$3; ROOT=$4; CODE=$5; GRADER=$6; SCORED=$7; REF=$8; OTHER=$9; shift 9
mkdir -p "$REC"

run() {      # run <label> <code-dir> [extra orchestrator args...]
  label=$1; code=$2; shift 2
  /usr/bin/time -v -o "$REC/$label.time" env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
    python3 -B -I "$READER/tools/brain/resit.py" run --mode gate --label "$label" --root "$ROOT" --code "$code" --items-root "$ROOT" \
    --grader-code "$GRADER" --out "$OUT" --scored "$SCORED" --reference-grade "$REF" "$@" > "$REC/$label.stdout" 2> "$REC/$label.stderr"
  rc=$?
  echo "$rc" > "$REC/$label.exit"
  echo "$(date '+%F %T %z') $label rc=$rc" >> "$REC/runs.log"
}

for step in "$@"; do
  case "$step" in
    r14) run r14 "$CODE" --check-turn ;;
    r2)
      CACHE="$OUT/glances-r2.pkl"
      rm -f "$CACHE"
      run r2-cold "$CODE" --cache "$CACHE"
      run r2-warm "$CODE" --cache "$CACHE"
      run r2-third "$CODE" --cache "$CACHE"
      run r2-blas4 "$CODE" --cache "$CACHE" --blas-reading 4
      ;;
    r3)
      for e in 0.001 0.01 0.1 0.5; do run "r3-$e" "$CODE" --nudge "$e" --nudge-seed 20261003; done
      ;;
    r1p)
      CACHE="$OUT/glances-r1p.pkl"
      rm -f "$CACHE"
      run r1p "$OTHER" --cache "$CACHE"
      ;;
    *) echo "unknown step $step" >&2; exit 64 ;;
  esac
done
echo "$(date '+%F %T %z') done: $*" >> "$REC/runs.log"
