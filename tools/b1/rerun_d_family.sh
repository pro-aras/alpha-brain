#!/bin/bash
# tools/b1/rerun_d_family.sh — the RULE LIBRARY's family re-run at its declared budget (B1-PREREG §4 row D, §12).
# edit: Claude (Opus 5.5), 2026-09-26 17:14 +0400 — the graded run of 13:03 ran D at the arm's toy default (2,000 candidates
# per sleep) because the seat's §12 line of 12:08 omitted D's number; and SHUFFLED-RELATION:E′ / :F loaded the REAL D's
# library (R36). This re-runs, for ONE seed: D and SHUFFLED-RELATION:D (the two searches, in parallel), then E′, F,
# SHUFFLED-RELATION:E′ and SHUFFLED-RELATION:F (they load their D's snapshots; no search).
# Usage: tools/b1/rerun_d_family.sh <seed>        (from the b1 tree; the budget is the registry's, run.py _BASE["D"])
# The old records move to runs/<seed>.toy-d/ — OUTSIDE the seed's directory, so results.py never grades them; nothing is
# deleted. Each search runs under a CPU FENCE (RLIMIT_CPU, `ulimit -t`) of 1.25 × its 24 CPU-hour allowance — CPU, not
# wall: the declared quantity is CPU-hours, and a wall fence would fire early on a loaded box. The fence decides nothing
# inside the arm (no timeout enters a decision — §4 row D); if it fires (SIGXCPU, exit 152) the search ends incomplete,
# D reads VOID by cost, and the seat re-prices. Each arm's exit is read from its own process, never a pipe.
# edit: Claude (Opus 5.5), 2026-09-26 17:22 +0400 — the wall fence (timeout) became a CPU fence (ulimit -t).
set -u
SEED="${1:?seed}"
cd "$(dirname "$0")/../.." || exit 2
ROOT=/data/dev/brain-runs/b1; OUT=$ROOT/runs/$SEED; TAPE=$ROOT/$SEED; CACHE=$ROOT/cache/$SEED; LOGS=$OUT/logs
FENCE_S=108000   # 30 CPU-hours = 1.25 × 24 CPU-hours
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/tmp
VENV=/data/dev/venvs/brain/bin/python
[ -f "$TAPE/tape.jsonl" ] || { echo "[rerun_d] no tape at $TAPE"; exit 3; }
[ -d "$OUT" ] || { echo "[rerun_d] no graded run at $OUT"; exit 3; }
mkdir -p "$LOGS"
OLD="$ROOT/runs/$SEED.toy-d"
if [ -e "$OLD" ]; then echo "[rerun_d] $OLD exists — refusing to mix two old records"; exit 4; fi
mkdir -p "$OLD"
for d in D E′ F SHUFFLED-RELATION_D SHUFFLED-RELATION_E′ SHUFFLED-RELATION_F; do
  if [ -e "$OUT/$d" ]; then mv "$OUT/$d" "$OLD/$d" || { echo "[rerun_d] mv $d failed"; exit 5; }; echo "[rerun_d] kept the old $d at $OLD/$d"; fi
done
for f in D Eppp F SHUFFLED-RELATION_D SHUFFLED-RELATION_Eppp SHUFFLED-RELATION_F; do   # tr maps the 3 bytes of ′ to ppp
  [ -e "$LOGS/$f.log" ] && mv "$LOGS/$f.log" "$OLD/$f.log"
done
ls -la "$OLD"
run_arm() {  # $1 arm name, $2 fence seconds (0 = none)
  local arm="$1" fence="$2" tag rc; tag=$(echo "$arm" | tr ':′' '_p')
  echo "[rerun_d] $(date +%H:%M:%S) start $arm"
  if [ "$fence" -gt 0 ]; then
    ( ulimit -t "$fence"; exec nice -n 10 "$VENV" -m brain.harness.run --seed "$SEED" --arms "$arm" --out "$OUT" --tape-dir "$TAPE" --cache-dir "$CACHE" ) > "$LOGS/$tag.log" 2>&1
  else
    nice -n 10 "$VENV" -m brain.harness.run --seed "$SEED" --arms "$arm" --out "$OUT" --tape-dir "$TAPE" --cache-dir "$CACHE" > "$LOGS/$tag.log" 2>&1
  fi
  rc=$?
  [ "$rc" -eq 152 ] && echo "[rerun_d] $(date +%H:%M:%S) $arm HIT THE CPU FENCE ($fence CPU-s, SIGXCPU): VOID by cost; re-price"
  [ "$rc" -eq 137 ] && echo "[rerun_d] $(date +%H:%M:%S) $arm KILLED (exit 137: the CPU fence's hard limit OR the unit's memory cap — read the journal before calling it cost)"
  echo "[rerun_d] $(date +%H:%M:%S) $arm exit $rc · $(grep -a '^\[run\] '"$arm"':' "$LOGS/$tag.log" | tail -n 1 | cut -c1-160)"
  return $rc
}
# ---- the two searches
run_arm D "$FENCE_S" & P1=$!
run_arm SHUFFLED-RELATION:D "$FENCE_S" & P2=$!
wait $P1; R1=$?
wait $P2; R2=$?
# ---- the loaders (each needs its own D's snapshots)
if [ "$R1" -eq 0 ]; then
  run_arm E′ 0 & P3=$!; run_arm F 0 & P4=$!; wait $P3; wait $P4
else echo "[rerun_d] D exit $R1 — E′ and F not run"; fi
if [ "$R2" -eq 0 ]; then
  run_arm SHUFFLED-RELATION:E′ 0 & P5=$!; run_arm SHUFFLED-RELATION:F 0 & P6=$!; wait $P5; wait $P6
else echo "[rerun_d] SHUFFLED-RELATION:D exit $R2 — its twins not run"; fi
echo "[rerun_d] $(date +%H:%M:%S) done → $OUT ; results: $VENV -m brain.harness.results --run $OUT --tape-dir $TAPE --bars docs/brain/b1/bars.json --ceilings docs/brain/b1/stage-1/ceilings.json"
