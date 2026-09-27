#!/bin/bash
# tools/b1/run_seed.sh — ONE GRADED SEED, every arm and twin, in dependency order with bounded parallelism
# (B1-PREREG.md §8, §4, §6). edit: Claude (Fable 5.1), 2026-09-24 19:02 +0400 — the seat, alone.
# Usage: tools/b1/run_seed.sh <seed> [max_parallel=6]      (from the b1 tree)
#   lane 1 (system python, the cells' interpreter until §3.0 decides otherwise): KEY SHIFTED-KEY RING-READ A0 FORCED:A0 SHUFFLED-NAME:A0
#   lane 2 (venv): A1 → A1-FIXED A1-ATT A1-MA (need A1's size) ; A1-MLC A1-NO-SLEEP A1-LOCAL A1-BPTT-AWAKE ; A2 A3 ; D → E′ F (need D's snapshots) ; SHUFFLED-RELATION:D → SHUFFLED-RELATION:E′ :F ; A4 (needs A1's size)
#   twins on the hybrids: A5 SHUFFLED-NAME:A1 SHUFFLED-NAME:A5 SHUFFLED-RELATION:A1 SHUFFLED-RELATION:A5 SHUFFLED-RELATION:E′ SHUFFLED-RELATION:F FORCED:A1 FORCED:A5
# Each arm is its own process (its own log, its own exit read from the process — never a pipe); nothing here decides a bar.
set -u
SEED="${1:?seed}"; MAXP="${2:-6}"
cd "$(dirname "$0")/../.." || exit 2
# edit: Claude (Opus 5.5), 2026-09-27 15:08 +0400 — R47 (B1.1): the root is B1_ROOT (default the B1.0 root, unchanged).
ROOT=${B1_ROOT:-/data/dev/brain-runs/b1}; OUT=$ROOT/runs/$SEED; TAPE=$ROOT/$SEED; CACHE=$ROOT/cache/$SEED; LOGS=$OUT/logs
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
# edit: Claude (Opus 5.5), 2026-09-27 15:12 +0400 — R47 (B1.1): the two SEARCHES run under a CPU fence (RLIMIT_CPU, relaunch_d_family.sh's
# pattern: 30 CPU-h = 1.25 × the 24 CPU-h allowance; exit 152 = VOID by cost), and the twin search SHUFFLED-RELATION:D runs
# in its OWN background chain: its loaders SHUFFLED-RELATION:E′ and :F follow it only on exit 0. No wave waits on it — on
# B1.0 seed 1 that twin sat hours in one sleep, and a bare `wait` would have held every later arm behind it. Each wave
# waits on its OWN pids only. No rule changes: the dependency stays inside the chain; D's own loaders E′ / F wait on D.
FENCE_S=108000
run_arm_fenced() {  # $1 interpreter, $2 arm name — a search, under the CPU fence
  local py="$1" arm="$2" tag rc; tag=$(echo "$arm" | tr ':′' '_p')
  echo "[run_seed] $(date +%H:%M:%S) start $arm (CPU fence $FENCE_S s)"
  ( ulimit -t "$FENCE_S"; exec nice -n 19 "$py" -m brain.harness.run --seed "$SEED" --arms "$arm" --out "$OUT" --tape-dir "$TAPE" --cache-dir "$CACHE" ) > "$LOGS/$tag.log" 2>&1
  rc=$?
  [ "$rc" -eq 152 ] && echo "[run_seed] $(date +%H:%M:%S) $arm HIT THE CPU FENCE ($FENCE_S CPU-s, SIGXCPU): VOID by cost"
  echo "[run_seed] $(date +%H:%M:%S) $arm exit $rc · $(grep -a '^\[run\] '"$arm"':' "$LOGS/$tag.log" | tail -n 1 | cut -c1-160)"
  return $rc
}
twin_chain() {
  if run_arm_fenced "$VENV" "SHUFFLED-RELATION:D"; then
    run_arm "$VENV" "SHUFFLED-RELATION:E′" & local p1=$!
    run_arm "$VENV" "SHUFFLED-RELATION:F" & local p2=$!
    wait "$p1"; wait "$p2"
  else
    echo "[run_seed] $(date +%H:%M:%S) SHUFFLED-RELATION:D did not complete — SHUFFLED-RELATION:E′ and :F not run (R44: E′'s and F's U3 read NOT GRADABLE)"
  fi
}
twin_chain & TWIN_PID=$!
# ---- wave 1: everything with no dependency
W=()
for a in KEY SHIFTED-KEY RING-READ A0 FORCED:A0 SHUFFLED-NAME:A0; do wait_slots; run_arm "$SYS" "$a" & W+=($!); done
# edit: Claude (Opus 5.5), 2026-09-26 17:12 +0400 — SHUFFLED-RELATION:D searches the SHUFFLED tape so that wave 3's
# SHUFFLED-RELATION:E′ and :F load a library learned on THEIR tape, not the real D's (SEAT-DECISIONS R36).
# edit: Claude (Opus 5.5), 2026-09-27 15:08 +0400 — R46/R47: A1-TEACH runs beside A1 (wave 1) and its three twins in wave 3.
wait_slots; run_arm_fenced "$VENV" D & W+=($!)
for a in A1 A1-TEACH A2 A3 A1-MLC A1-NO-SLEEP A1-LOCAL A1-BPTT-AWAKE; do wait_slots; run_arm "$VENV" "$a" & W+=($!); done
wait "${W[@]}"
# ---- wave 2: the arms that read A1's size or D's snapshots
W=()
for a in A1-FIXED A1-ATT A1-MA A4 A5 E′ F; do wait_slots; run_arm "$VENV" "$a" & W+=($!); done
wait "${W[@]}"
# ---- wave 3: the twins over the hybrids and the network (SHUFFLED-RELATION:E′ / :F run in the twin chain)
W=()
for a in SHUFFLED-NAME:A1 SHUFFLED-NAME:A5 SHUFFLED-RELATION:A1 SHUFFLED-RELATION:A5 FORCED:A1 FORCED:A5 SHUFFLED-NAME:A1-TEACH SHUFFLED-RELATION:A1-TEACH FORCED:A1-TEACH; do wait_slots; run_arm "$VENV" "$a" & W+=($!); done
wait "${W[@]}"
echo "[run_seed] $(date +%H:%M:%S) waves done; waiting on the twin chain (pid $TWIN_PID)"
wait "$TWIN_PID"
echo "[run_seed] $(date +%H:%M:%S) all arms done → $OUT ; results: $VENV -m brain.harness.results --run $OUT --tape-dir $TAPE --bars docs/brain/b1/bars.json --ceilings docs/brain/b1/stage-1/ceilings.json"
