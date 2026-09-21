#!/usr/bin/env bash
# edit: Claude (Fable 5.1), 2026-09-21 21:04 +0400 — THE LANDING CHECKER for the G5 builders (I, J, K, L): run on the integration tree
# AFTER a branch is merged there, BEFORE the merge is accepted. Never the builders' green reports (#180, #214). Steps:
#   1. gate_g4 1/2/3/6 (parity vs the pin + every planted control)            2. both suites with -t . on the final bytes
#   3. life 3a's whole tape replayed under this tree, diffed (minus hash) against the MASTER control replay
#      (scratch/replay-life3a-master/journal.jsonl) — a branch that declares nothing new in G4.genome must be identical.
# usage: tools/gate_g5_landing.sh <label>     (logs under scratch/landing-<label>/; exit 0 iff every step passed)
set -u
TREE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="${1:?label}"
OUT="$TREE/scratch/landing-$LABEL"; mkdir -p "$OUT"
cd "$TREE"
rc=0
echo "[landing $LABEL] tree $TREE at $(git rev-parse --short HEAD) — $(date '+%Y-%m-%d %H:%M %z'); load $(cut -d' ' -f1-3 /proc/loadavg)"
nice -n 10 python3 -u tools/gate_g4.py --tree "$TREE" --only 1,2,3,6 > "$OUT/gate_g4.log" 2>&1; g=$?
grep -E "G4 gates:" "$OUT/gate_g4.log" || true
[ $g -eq 0 ] && grep -q "'1': 'PASS', '2': 'PASS', '3': 'PASS', '6': 'PASS'" "$OUT/gate_g4.log" || { echo "[landing $LABEL] GATE FAILED (exit $g)"; rc=1; }
nice -n 10 python3 -u -m unittest discover -s tests/genome -t . > "$OUT/suite-genome.log" 2>&1; sg=$?
nice -n 10 python3 -u -m unittest discover -s tests/creature -t . > "$OUT/suite-creature.log" 2>&1; sc=$?
echo "[landing $LABEL] genome: $(grep -E '^Ran ' "$OUT/suite-genome.log") $(grep -E '^(OK|FAILED)' "$OUT/suite-genome.log") (exit $sg)"
echo "[landing $LABEL] creature: $(grep -E '^Ran ' "$OUT/suite-creature.log") $(grep -E '^(OK|FAILED)' "$OUT/suite-creature.log") (exit $sc)"
[ $sg -eq 0 ] && [ $sc -eq 0 ] || rc=1
mkdir -p "$OUT/replay-life3a"
nice -n 10 python3 -u -m creature.replay --genome genome/G4.genome --tape /data/dev/genome/run-g4-life3a-20260921-1314/tape/2026-09-21.jsonl --out "$OUT/replay-life3a" > "$OUT/replay-life3a.log" 2>&1; r=$?
if [ $r -ne 0 ]; then echo "[landing $LABEL] REPLAY of life 3a's tape FAILED (exit $r)"; rc=1; fi
python3 tools/replay_diff.py "$TREE/scratch/replay-life3a-master/journal.jsonl" "$OUT/replay-life3a/journal.jsonl" --label-a master --label-b "$LABEL" | tee "$OUT/replay-diff.log"; d=${PIPESTATUS[0]}
[ $d -eq 0 ] || { echo "[landing $LABEL] REPLAY DIFF vs master: NOT identical (read $OUT/replay-diff.log — a new key is a format change to record; a changed value is a finding)"; rc=1; }
echo "[landing $LABEL] RESULT: $([ $rc -eq 0 ] && echo PASS || echo FAIL) — logs in $OUT"
exit $rc
