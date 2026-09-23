#!/usr/bin/env bash
# edit: Claude (Fable 5.1), 2026-09-23 12:32 +0400 — THE A4 LADDER'S LANDING REGRESSION on alpha4-1's hour-1 fixture (A4-LADDER-PREREG §1.6):
#   (i) this tree + genome/ladder/A4L-FLOOR.genome replays the fixture IDENTICAL — every field, `hash` included — to the master
#       control replay (/data/dev/a4-ladder/fixtures/ref-floor/journal.jsonl, made by `--make-control` on master; its commit stamped);
#   (ii) this tree + genome/ladder/A4L-<RUNG>.genome vs the tree's own FLOOR replay: the FIRST differing row is printed. A rung whose
#       mechanism the hour-1 fixture cannot exercise (no sound rows, no chat rows) replays identical — that is printed as a NOTE, and the
#       rung's own gate mark (a planted input) must carry the proof instead; it is never silently a pass.
# usage: tools/lives/a4_regression.sh <RUNG>        (from the tree under test)    |    tools/lives/a4_regression.sh --make-control (on master)
set -u
TREE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$TREE"
FIX=/data/dev/a4-ladder/fixtures/alpha4-1-hour1; CTL=/data/dev/a4-ladder/fixtures/ref-floor
export TMPDIR="$TREE/scratch/tmp" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1; mkdir -p "$TMPDIR"
if [ "${1:?RUNG or --make-control}" = --make-control ]; then
  mkdir -p "$CTL"; nice -n 10 python3 -u -m creature.replay --genome genome/ladder/A4L-FLOOR.genome --tape "$FIX/tape/2026-09-23.jsonl" --out "$CTL" > "$CTL/replay.log" 2>&1 || { echo "[a4reg] control replay FAILED (read $CTL/replay.log)"; exit 1; }
  git rev-parse HEAD > "$CTL/CONTROL-COMMIT"; date '+%Y-%m-%d %H:%M %z' > "$CTL/MADE-AT"
  echo "[a4reg] control: $(wc -l < "$CTL/journal.jsonl") rows, made on $(cut -c1-8 "$CTL/CONTROL-COMMIT") at $(cat "$CTL/MADE-AT")"; exit 0
fi
RUNG=$1; G="genome/ladder/A4L-$RUNG.genome"; [ -f "$G" ] || { echo "[a4reg $RUNG] no $G in this tree"; exit 2; }
[ -f "$CTL/journal.jsonl" ] || { echo "[a4reg $RUNG] no control at $CTL — run --make-control on master first"; exit 2; }
OUT="$TREE/scratch/a4reg-$RUNG"; rm -rf "$OUT"; mkdir -p "$OUT/floor" "$OUT/rung"; rc=0
echo "[a4reg $RUNG] tree $(git rev-parse --short HEAD) vs control $(cut -c1-8 "$CTL/CONTROL-COMMIT") — $(date '+%Y-%m-%d %H:%M %z'); load $(cut -d' ' -f1 /proc/loadavg)"
nice -n 10 python3 -u -m creature.replay --genome genome/ladder/A4L-FLOOR.genome --tape "$FIX/tape/2026-09-23.jsonl" --out "$OUT/floor" > "$OUT/floor.log" 2>&1 || { echo "[a4reg $RUNG] FLOOR replay FAILED (read $OUT/floor.log)"; exit 1; }
python3 tools/replay_diff.py "$CTL/journal.jsonl" "$OUT/floor/journal.jsonl" --ignore "" --label-a control-floor --label-b "$RUNG-tree-floor" | tee "$OUT/floor-diff.log"; d=${PIPESTATUS[0]}
if [ $d -eq 0 ]; then echo "[a4reg $RUNG] (i) FLOOR identical to the control, hash included: PASS"; else echo "[a4reg $RUNG] (i) FLOOR NOT identical to the control: FAIL (the branch's undeclared road moved — read $OUT/floor-diff.log)"; rc=1; fi
nice -n 10 python3 -u -m creature.replay --genome "$G" --tape "$FIX/tape/2026-09-23.jsonl" --out "$OUT/rung" > "$OUT/rung.log" 2>&1 || { echo "[a4reg $RUNG] RUNG replay FAILED (read $OUT/rung.log)"; exit 1; }
python3 tools/replay_diff.py "$OUT/floor/journal.jsonl" "$OUT/rung/journal.jsonl" --ignore "" --label-a floor --label-b "$RUNG" | tee "$OUT/rung-diff.log"; d2=${PIPESTATUS[0]}
if [ $d2 -ne 0 ]; then echo "[a4reg $RUNG] (ii) the rung's line MOVES the replay (its first differing row is above)"; else echo "[a4reg $RUNG] (ii) NOTE: the rung's line changes NOTHING on the hour-1 fixture — the rung's own gate mark must prove the road on a planted input, or the line is declared-only (his 23:08 rule)"; fi
exit $rc
