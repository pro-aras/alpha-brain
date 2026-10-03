#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:03 +0400 — PREREG-HEARS-2 §2 + AMENDMENT 1 (A1.1): the bench's driver, so the verifier re-runs EXACTLY what was run.
# usage:
#   hears_bench.sh arms <out dir>             build OFF and ON from the life's genome (diffs asserted), start BOTH replays in the SAME minute through two
#                                              slots, record loadavg + PSI + epoch seconds at each arm's start and end, wait for both
#   hears_bench.sh read <out dir>             grade both arms, read the maker side, plant X and regrade it, run journal_diff beside I2, run hears_read
#   hears_bench.sh arm <label> <genome> <out> (internal: one arm; called under `slot`)
# Inputs (environment; the defaults are the HEARS lane's scratch copies — the life's own root is never read through, #212):
#   LIFE_GENOME  the closed life's GENOME.genome (copy)                  default <repo>/scratch/GENOME-full.genome
#   TAPE         the life's tape CUT at the lived seq, payload copied    default <repo>/scratch/cut-full/tape
#   TRUTH_SRC    the life's truth/ directory (copied into the grading root)  default /data/dev/genome-lives/brain-full-20261102/truth
#   I1_JOURNAL   the identity replay's journal (the replay under the life's own genome, no DRIVE)  REQUIRED by `read`, no default (the reader refuses an empty one)
# OFF = the life's genome + `DRIVE brain turn before hearing; says 1; asks 1` (the life predates DRIVE); ON = OFF with `hears scene maker`: ONE token apart.
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:15 +0400 — the free-slot check reads the slot LOCKS, not the slot-N.who records (a killed job leaves its record behind); the read stage's
# grading root, X plant + regrade and hears_read were dry-run on the real live journal (the identity journal) before this commit; the arms stage is first exercised at the launch.
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:48 +0400 — `read` REQUIRES I1_JOURNAL (the first default named a run that never finished; the advisor and the verifier both saw it fail there) and refuses an empty
# one; the `arms` stage's free-slot precheck follows the swarm gate's 5 slots (SLOT_N default 5). The bench pair was launched by the 33f68f9 version of this file; the replays' own command (the `arm` stage) and the genome construction are unchanged by this edit.
set -u
SELF=$(readlink -f "$0")
REPO=$(cd "$(dirname "$SELF")/../.." && pwd)
LIFE_GENOME=${LIFE_GENOME:-$REPO/scratch/GENOME-full.genome}
TAPE=${TAPE:-$REPO/scratch/cut-full/tape}
TRUTH_SRC=${TRUTH_SRC:-/data/dev/genome-lives/brain-full-20261102/truth}
I1_JOURNAL=${I1_JOURNAL:-}          # REQUIRED by `read`: the replay under the life's own genome (no DRIVE) — no default (the first default pointed at a run that never finished)
SLOT=${SLOT:-/data/dev/swarm/bin/slot}
LANE=${LANE:-hears}
export REPO TAPE TMPDIR=$REPO/scratch/tmp PYTHONPATH=$REPO PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cmd=${1:-}

if [ "$cmd" = "arm" ]; then
  label=$2; genome=$3; out=$4
  cd "$REPO" || exit 97
  mkdir -p "$out"
  {
    echo "label $label"
    echo "start_epoch $(date +%s.%N)"
    echo "start_iso $(date '+%F %T %z')"
    echo "loadavg_start $(cat /proc/loadavg)"
    echo "pressure_cpu_start $(tr '\n' '|' < /proc/pressure/cpu)"
  } > "$out.arm"
  python3 -B -m creature.replay --genome "$genome" --tape "$TAPE" --out "$out" --closed --timings > "$out.log" 2>&1
  rc=$?
  echo "$rc" > "$out.exit"
  {
    echo "end_epoch $(date +%s.%N)"
    echo "end_iso $(date '+%F %T %z')"
    echo "loadavg_end $(cat /proc/loadavg)"
    echo "pressure_cpu_end $(tr '\n' '|' < /proc/pressure/cpu)"
    echo "exit $rc"
  } >> "$out.arm"
  exit $rc
fi

OUT=${2:?out dir}
mkdir -p "$OUT/logs"
cd "$REPO" || exit 97

if [ "$cmd" = "arms" ]; then
  cp "$LIFE_GENOME" "$OUT/GENOME-life.genome" || exit 3
  awk '{print} /^BRAIN    /{print "DRIVE    brain turn before hearing; says 1; asks 1"}' "$OUT/GENOME-life.genome" > "$OUT/GENOME-off.genome"
  sed 's/replay none; hears scene$/replay none; hears scene maker/' "$OUT/GENOME-off.genome" > "$OUT/GENOME-on.genome"
  # the arms differ by ONE token, and OFF from the life by ONE added line — asserted, never assumed
  [ "$(diff "$OUT/GENOME-life.genome" "$OUT/GENOME-off.genome" | grep -c '^[<>]')" = 1 ] || { echo "STOP: OFF differs from the life by more than the one DRIVE line"; exit 3; }
  [ "$(diff "$OUT/GENOME-off.genome" "$OUT/GENOME-on.genome" | grep -c '^[<>]')" = 2 ] || { echo "STOP: ON differs from OFF by more than one line"; exit 3; }
  grep -q '; hears scene maker$' "$OUT/GENOME-on.genome" || { echo "STOP: ON does not hear the maker"; exit 3; }
  # free slots are counted from the LOCKS (a killed job leaves its slot-N.who record behind; the lock is what the slot gate honours)
  total=${SLOT_N:-5}                   # the swarm's slot gate (/data/dev/swarm/bin/slot) has run 5 slots since 11:4x; the first version assumed 6
  busy=0
  for i in $(seq 1 "$total"); do
    exec {sfd}>"/data/dev/swarm/slots/slot-$i.lock"
    if flock -n "$sfd"; then flock -u "$sfd"; else busy=$((busy + 1)); fi
    exec {sfd}>&-
  done
  if [ $((total - busy)) -lt 2 ]; then echo "STOP: fewer than two free slots ($busy of $total busy): the arms must start in the same minute (A1.1)"; exit 5; fi
  { echo "arms launched $(date '+%F %T %z') · slots busy before: $busy of $total"; echo "loadavg $(cat /proc/loadavg)"; echo "pressure_cpu $(tr '\n' '|' < /proc/pressure/cpu)"; } > "$OUT/launch.txt"
  ( "$SLOT" "$LANE" bench-off -- bash "$SELF" arm off "$OUT/GENOME-off.genome" "$OUT/off" ) &
  PO=$!
  ( "$SLOT" "$LANE" bench-on -- bash "$SELF" arm on "$OUT/GENOME-on.genome" "$OUT/on" ) &
  PN=$!
  wait $PO; RO=$?
  wait $PN; RN=$?
  echo "off exit $RO · on exit $RN" > "$OUT/arms.exit"
  [ "$RO" = 0 ] && [ "$RN" = 0 ]
  exit $?
fi

if [ "$cmd" = "read" ]; then
  [ -s "$I1_JOURNAL" ] || { echo "STOP: set I1_JOURNAL to the identity replay's journal.jsonl (the replay under the life's own genome, no DRIVE); got '${I1_JOURNAL}'"; exit 3; }
  C=$OUT/clock.txt
  step() { echo "$1 exit $2" >> "$C"; }
  # the grading root: the cut tape (a symlink to the HEARS copy), the truth (a copy), the life's genome — never the life's own root
  G=$OUT/groot
  mkdir -p "$G"
  [ -e "$G/tape" ] || ln -s "$TAPE" "$G/tape"
  [ -d "$G/truth" ] || cp -r "$TRUTH_SRC" "$G/truth"
  cp "$OUT/GENOME-life.genome" "$G/GENOME.genome"
  date "+%Y-%m-%d %H:%M:%S %z read start" >> "$C"
  for arm in off on; do
    python3 -B tools/brain/grade_life.py --root "$G" --journal "$OUT/$arm/journal.jsonl" --genome "$OUT/GENOME-$arm.genome" --label "$arm" --out "$OUT/grade-$arm" > "$OUT/logs/grade-$arm.log" 2>&1
    step "grade-$arm" $?
  done
  python3 -B tools/brain/worlds_read.py --journal "$OUT/on/journal.jsonl" --out "$OUT/worlds-on" > "$OUT/logs/worlds-on.log" 2>&1
  step worlds-on $?
  # X's plant: ONE cited moment of ON's journal spoiled, regraded under the same command as ON
  mkdir -p "$OUT/xplant"
  python3 -B tools/brain/hears_read.py --plant-x-journal "$OUT/on/journal.jsonl" --plant-x-out "$OUT/xplant/journal.jsonl" > "$OUT/xplant.json" 2> "$OUT/logs/xplant.err"
  step xplant-make $?
  python3 -B tools/brain/grade_life.py --root "$G" --journal "$OUT/xplant/journal.jsonl" --genome "$OUT/GENOME-on.genome" --label xplant --out "$OUT/grade-xplant" > "$OUT/logs/grade-xplant.log" 2>&1
  step grade-xplant $?
  # I2 as the law names it (journal_diff.py drops every brain row and every answer row) and its planted control (must exit 1)
  python3 -B tools/brain/journal_diff.py --a "$OUT/off/journal.jsonl" --b "$I1_JOURNAL" > "$OUT/i2-journal_diff.txt" 2>&1
  step i2-journal_diff $?
  python3 -B tools/brain/journal_diff.py --a "$OUT/off/journal.jsonl" --b "$I1_JOURNAL" --plant > "$OUT/i2-journal_diff-planted.txt" 2>&1
  echo "i2-journal_diff-planted exit $? (must be 1)" >> "$C"
  # the bench's reader: P, T, G, C, X, and I2 as the stronger comparison (only the turn rows dropped)
  python3 -B tools/brain/hears_read.py --off "$OUT/grade-off" --on "$OUT/grade-on" --on-plant "$OUT/grade-xplant" --tape "$TAPE" \
    --off-timings "$OUT/off/timings.jsonl" --on-timings "$OUT/on/timings.jsonl" --off-arm "$OUT/off.arm" --on-arm "$OUT/on.arm" \
    --on-journal "$OUT/on/journal.jsonl" --off-journal "$OUT/off/journal.jsonl" --i1-journal "$I1_JOURNAL" --out "$OUT/read" > "$OUT/logs/read.log" 2>&1
  step hears_read $?
  date "+%Y-%m-%d %H:%M:%S %z read done" >> "$C"
  exit 0
fi

echo "usage: hears_bench.sh arms|read <out dir>" >&2
exit 64
