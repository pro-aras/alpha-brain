#!/bin/bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 — THE GATE RESUMED after the box's hard stop at 18:59 (no shutdown record; load above 30 for two hours).
# The bench runs and the pair of 20261102 were COMPLETE and are kept untouched. The replays the stop cut (the pairs of 20261101
# and 20261103, the identity plant) are run again whole, the same commands from the same commit: a replay is deterministic.
# The cut folders are MOVED aside, never removed. At most five processes at once.
set -u
CODE=/data/dev/genome-wt-drive; O=/data/dev/brain-runs/day0929/drive; RUNS=$O/runs; BENCH=$O/bench; L=$O/logs; G=$CODE/genome/brain/lives
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TMPDIR=/data/dev/brain-runs/day0929/tmp PYTHONPATH=$CODE
PY="/usr/bin/python3 -B"; PLANT=20261102
cd $CODE || exit 2
C=$O/gate-clock.txt
[ -e $O/read ] && { echo "STOP: $O/read exists — the gate is read once" | tee -a $C; exit 3; }
[ -z "$(git status --porcelain)" ] || { echo "STOP: the drive tree is not clean" | tee -a $C; exit 3; }
[ "$(git rev-parse --short HEAD)" = "c68da99" ] || { echo "STOP: the tree is not at the gate's commit c68da99" | tee -a $C; exit 3; }
n=$(systemctl --user list-units 'creature*' --state=active --no-legend --no-pager | grep -c .)
[ "$n" = "0" ] || { echo "STOP: $n creature unit(s) active" | tee -a $C; exit 3; }
echo "--- THE BOX STOPPED HARD at 18:59 (no shutdown record) and came back at 19:00. Complete before it: every bench run; the pair of 20261102 (off exit 0, on exit 0)." >> $C
date "+%Y-%m-%d %H:%M:%S %z the gate RESUMES at $(git rev-parse --short HEAD); load $(cut -d' ' -f1-3 /proc/loadavg)" >> $C
declare -A P=()
for WS in 20261101 20261103; do
  R=/data/dev/genome-lives/brain-lean-$WS; J=$(ls $R/journal/*.jsonl | head -1)
  for a in off on; do [ -e $RUNS/$WS/$a ] && mv $RUNS/$WS/$a $RUNS/$WS/$a.cut-by-the-stop; done
  ( $PY -m creature.replay --genome $G/BRAIN-LEAN-$WS.genome --tape $R/tape --out $RUNS/$WS/off --closed --timings --against $J > $L/gate-off-$WS.resumed.log 2>&1; echo $? > $RUNS/$WS/off.exit ) & P["off-$WS"]=$!
  ( $PY -m creature.replay --genome $G/BRAIN-LEAN-DRIVE-$WS.genome --tape $R/tape --out $RUNS/$WS/on --closed --timings > $L/gate-on-$WS.resumed.log 2>&1; echo $? > $RUNS/$WS/on.exit ) & P["on-$WS"]=$!
done
R=/data/dev/genome-lives/brain-lean-$PLANT; J=$(ls $R/journal/*.jsonl | head -1)
[ -e $RUNS/$PLANT/plant ] && mv $RUNS/$PLANT/plant $RUNS/$PLANT/plant.cut-by-the-stop
[ "$(diff $G/BRAIN-LEAN-$PLANT.genome $O/genomes/PLANT-$PLANT.genome | grep -c '^[<>]')" = "2" ] || { echo "STOP: the plant genome differs in other than one line" | tee -a $C; exit 3; }
( $PY -m creature.replay --genome $O/genomes/PLANT-$PLANT.genome --tape $R/tape --out $RUNS/$PLANT/plant --closed --against $J > $L/gate-plant-$PLANT.resumed.log 2>&1; echo $? > $RUNS/$PLANT/plant.exit ) & P["plant-$PLANT"]=$!
for k in "${!P[@]}"; do wait "${P[$k]}"; echo "$(date '+%H:%M:%S') $k done; load $(cut -d' ' -f1-3 /proc/loadavg)" >> $C; done
fail=0
for WS in 20261101 20261102 20261103; do echo "off-$WS replay exit $(cat $RUNS/$WS/off.exit) · on-$WS replay exit $(cat $RUNS/$WS/on.exit)" >> $C; [ "$(cat $RUNS/$WS/on.exit)" = "0" ] || fail=1; done
echo "plant-$PLANT replay exit $(cat $RUNS/$PLANT/plant.exit) (it must not be 0)" >> $C
date "+%Y-%m-%d %H:%M:%S %z the runs are done (an ON replay failed: $fail)" >> $C
[ $fail = 0 ] || exit 4
$PY tools/brain/drive_gate.py --runs $RUNS --bench $BENCH --stage1 $O/stage-1 --out $O/read > $L/gate-read.log 2>&1; rc=$?
echo "$(date '+%H:%M:%S') the reader exit $rc" >> $C
exit $rc
