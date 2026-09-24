#!/bin/bash
# tools/b1/run_seed.sh — ONE GRADED SEED, every arm and twin, in dependency order with bounded parallelism
# (B1-PREREG.md §8, §4, §6). edit: Claude (Fable 5.1), 2026-09-24 19:02 +0400 — the seat, alone.
# Usage: tools/b1/run_seed.sh <seed> [max_parallel=6]      (from the b1 tree)
#   lane 1 (system python, the cells' interpreter until §3.0 decides otherwise): KEY SHIFTED-KEY RING-READ A0 FORCED:A0 SHUFFLED-NAME:A0
#   lane 2 (venv): A1 → A1-FIXED A1-ATT A1-MA (need A1's size) ; A1-MLC A1-NO-SLEEP A1-LOCAL A1-BPTT-AWAKE ; A2 A3 ; D → E′ F (need D's snapshots) ; A4 (needs A1's size)
#   twins on the hybrids: A5 SHUFFLED-NAME:A1 SHUFFLED-NAME:A5 SHUFFLED-RELATION:A1 SHUFFLED-RELATION:A5 SHUFFLED-RELATION:E′ SHUFFLED-RELATION:F FORCED:A1 FORCED:A5
# Each arm is its own process (its own log, its own exit read from the process — never a pipe); nothing here decides a bar.
set -u
SEED="${1:?seed}"; MAXP="${2:-6}"
cd "$(dirname "$0")/../.." || exit 2
ROOT=/data/dev/brain-runs/b1; OUT=$ROOT/runs/$SEED; TAPE=$ROOT/$SEED; CACHE=$ROOT/cache/$SEED; LOGS=$OUT/logs
mkdir -p "$OUT" "$LOGS"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/tmp
VENV=/data/dev/venvs/brain/bin/python; SYS=/usr/bin/python3
[ -f "$TAPE/tape.jsonl" ] || { echo "[run_seed] no tape at $TAPE"; exit 3; }
run_arm() {  # $1 interpreter, $2 arm name
  local py="$1" arm="$2" tag; tag=$(echo "$arm" | tr ':′' '_p')
  echo "[run_seed] $(date +%H:%M:%S) start $arm"
  nice -n 19 "$py" -m brain.harness.run --seed "$SEED" --arms "$arm" --out "$OUT" --tape-dir "$TAPE" --cache-dir "$CACHE" > "$LOGS/$tag.log" 2>&1
  local rc=$?
  echo "[run_seed] $(date +%H:%M:%S) $arm exit $rc · $(grep -a '^\[run\] '"$arm"':' "$LOGS/$tag.log" | tail -n 1 | cut -c1-160)"
  return $rc
}
wait_slots() { while [ "$(jobs -rp | wc -l)" -ge "$MAXP" ]; do sleep 5; done; }
# ---- wave 1: everything with no dependency
for a in KEY SHIFTED-KEY RING-READ A0 FORCED:A0 SHUFFLED-NAME:A0; do wait_slots; run_arm "$SYS" "$a" & done
for a in A1 A2 A3 D A1-MLC A1-NO-SLEEP A1-LOCAL A1-BPTT-AWAKE; do wait_slots; run_arm "$VENV" "$a" & done
wait
# ---- wave 2: the arms that read A1's size or D's snapshots
for a in A1-FIXED A1-ATT A1-MA A4 A5 E′ F; do wait_slots; run_arm "$VENV" "$a" & done
wait
# ---- wave 3: the twins over the hybrids and the network
for a in SHUFFLED-NAME:A1 SHUFFLED-NAME:A5 SHUFFLED-RELATION:A1 SHUFFLED-RELATION:A5 SHUFFLED-RELATION:E′ SHUFFLED-RELATION:F FORCED:A1 FORCED:A5; do wait_slots; run_arm "$VENV" "$a" & done
wait
echo "[run_seed] $(date +%H:%M:%S) all arms done → $OUT ; results: $VENV -m brain.harness.results --run $OUT --tape-dir $TAPE --bars docs/brain/b1/bars.json --ceilings docs/brain/b1/stage-1/ceilings.json"
