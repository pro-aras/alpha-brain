#!/bin/bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 — THE GATE's runs (PREREG-BRAIN-DRIVES §3, signed by the seat alone, sha256 a5fdea1e…).
# Every body run is a REPLAY of a closed lean life's tape from the drive tree. Nothing is written under a life's root.
# The bench (runs G, J and JB's bench side) and the body (B-OFF, B-ON as PAIRS side by side, and the identity plant) run at once.
set -u
CODE=/data/dev/genome-wt-drive; O=/data/dev/brain-runs/day0929/drive; RUNS=$O/runs; BENCH=$O/bench; L=$O/logs; G=$CODE/genome/brain/lives
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TMPDIR=/data/dev/brain-runs/day0929/tmp PYTHONPATH=$CODE
PY="/usr/bin/python3 -B"
SEEDS="20261101 20261102 20261103"; NEW=20261104; PLANT=20261102
cd $CODE || exit 2
C=$O/gate-clock.txt
[ -e $RUNS ] && { echo "STOP: $RUNS exists — the gate is read once" | tee -a $C; exit 3; }
[ -e $BENCH ] && { echo "STOP: $BENCH exists — the gate is read once" | tee -a $C; exit 3; }
n=$(systemctl --user list-units 'creature*' --state=active --no-legend --no-pager | grep -c .)
[ "$n" = "0" ] || { echo "STOP: $n creature unit(s) active" | tee -a $C; exit 3; }
[ -z "$(git status --porcelain)" ] || { echo "STOP: the drive tree is not clean" | tee -a $C; exit 3; }
mkdir -p $RUNS $BENCH/g $BENCH/j $BENCH/jb $L $O/genomes
date "+%Y-%m-%d %H:%M:%S %z the gate starts at $(git rev-parse --short HEAD); PREREG sha256 $(sha256sum docs/organism/drive/PREREG-BRAIN-DRIVES.md | cut -c1-16); load $(cut -d' ' -f1-3 /proc/loadavg)" > $C
declare -A P=()
( nice -n 5 $PY tools/brain/diag/probe_drive.py --ws $NEW --n 10000 --nulls 10 --out $BENCH/g > $L/gate-bench-g.log 2>&1 ) & P["bench-g-$NEW"]=$!
for WS in $SEEDS; do
  ( nice -n 5 $PY tools/brain/diag/probe_drive.py --ws $WS --n 10000 --nulls 10 --out $BENCH/j > $L/gate-bench-j-$WS.log 2>&1 ) & P["bench-j-$WS"]=$!
  ( nice -n 5 $PY tools/brain/diag/probe_drive.py --ws $WS --n 10000 --nulls 10 --genome $G/BRAIN-LEAN-DRIVE-$WS.genome --out $BENCH/jb > $L/gate-bench-jb-$WS.log 2>&1 ) & P["bench-jb-$WS"]=$!
done
for WS in $SEEDS; do
  R=/data/dev/genome-lives/brain-lean-$WS
  [ -f $R/STOPPED-AT ] || { echo "STOP: $R is not closed" | tee -a $C; exit 3; }
  [ "$(ls $R/journal/*.jsonl | wc -l)" = "1" ] || { echo "STOP: $R has more than one journal day file" | tee -a $C; exit 3; }
  J=$(ls $R/journal/*.jsonl | head -1)
  mkdir -p $RUNS/$WS
  ( nice -n 0 $PY -m creature.replay --genome $G/BRAIN-LEAN-$WS.genome --tape $R/tape --out $RUNS/$WS/off --closed --timings --against $J > $L/gate-off-$WS.log 2>&1; echo $? > $RUNS/$WS/off.exit ) & P["off-$WS"]=$!
  ( nice -n 0 $PY -m creature.replay --genome $G/BRAIN-LEAN-DRIVE-$WS.genome --tape $R/tape --out $RUNS/$WS/on --closed --timings > $L/gate-on-$WS.log 2>&1; echo $? > $RUNS/$WS/on.exit ) & P["on-$WS"]=$!
done
# THE IDENTITY PLANT (PREREG §5.5): one value changed; the replay must DIVERGE from the closed journal
R=/data/dev/genome-lives/brain-lean-$PLANT; J=$(ls $R/journal/*.jsonl | head -1)
sed 's/^DELTA    lr 0.05/DELTA    lr 0.06/' $G/BRAIN-LEAN-$PLANT.genome > $O/genomes/PLANT-$PLANT.genome
[ "$(diff $G/BRAIN-LEAN-$PLANT.genome $O/genomes/PLANT-$PLANT.genome | grep -c '^[<>]')" = "2" ] || { echo "STOP: the plant genome differs in other than one line" | tee -a $C; exit 3; }
( nice -n 5 $PY -m creature.replay --genome $O/genomes/PLANT-$PLANT.genome --tape $R/tape --out $RUNS/$PLANT/plant --closed --against $J > $L/gate-plant-$PLANT.log 2>&1; echo $? > $RUNS/$PLANT/plant.exit ) & P["plant-$PLANT"]=$!
fail=0
for k in "${!P[@]}"; do wait "${P[$k]}"; rc=$?; echo "$(date '+%H:%M:%S') $k exit $rc; load $(cut -d' ' -f1-3 /proc/loadavg)" >> $C; done
for WS in $SEEDS; do echo "off-$WS replay exit $(cat $RUNS/$WS/off.exit) · on-$WS replay exit $(cat $RUNS/$WS/on.exit)" >> $C; [ "$(cat $RUNS/$WS/on.exit)" = "0" ] || fail=1; done
echo "plant-$PLANT replay exit $(cat $RUNS/$PLANT/plant.exit) (it must not be 0)" >> $C
date "+%Y-%m-%d %H:%M:%S %z the runs are done (an ON replay failed: $fail)" >> $C
[ $fail = 0 ] || exit 4
$PY tools/brain/drive_gate.py --runs $RUNS --bench $BENCH --stage1 $O/stage-1 --out $O/read > $L/gate-read.log 2>&1; rc=$?
echo "$(date '+%H:%M:%S') the reader exit $rc" >> $C
exit $rc
