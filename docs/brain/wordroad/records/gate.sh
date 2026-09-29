#!/bin/bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 — THE GATE's runs (PREREG-WORD-ROAD §3, signed by both, sha256 7ed1d132…).
# Every run is a REPLAY of a closed lean life's tape from the word-road tree. Nothing is written under a life's root.
# PHASE 1: per seed, the ON and OFF replays as a PAIR, alone on the box (mark C's cost), one pair after the other.
# PHASE 2: the BRAIN genome's identity replays, the ten null tapes and their replays, the grades — in parallel.
set -u
CODE=/data/dev/genome-wt-wordroad; O=/data/dev/brain-runs/day0929/wordroad; RUNS=$O/runs; L=$O/logs; G=$CODE/genome/brain/lives
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TMPDIR=/data/dev/brain-runs/day0929/tmp PYTHONPATH=$CODE
PY="/usr/bin/python3 -B"
SEEDS="20261101 20261102 20261103"; NULLSEED=20261102
cd $CODE || exit 2
C=$O/gate-clock.txt
[ -e $RUNS ] && { echo "STOP: $RUNS exists — the gate is read once" | tee -a $C; exit 3; }
n=$(systemctl --user list-units 'creature*' --state=active --no-legend --no-pager | grep -c .)
[ "$n" = "0" ] || { echo "STOP: $n creature unit(s) active" | tee -a $C; exit 3; }
[ -z "$(git status --porcelain)" ] || { echo "STOP: the word-road tree is not clean" | tee -a $C; exit 3; }
mkdir -p $RUNS $L
date "+%Y-%m-%d %H:%M:%S %z the gate starts at $(git rev-parse --short HEAD); PREREG sha256 $(sha256sum docs/brain/wordroad/PREREG-WORD-ROAD.md | cut -c1-16)" > $C
for WS in $SEEDS; do
  R=/data/dev/genome-lives/brain-lean-$WS
  [ -f $R/STOPPED-AT ] || { echo "STOP: $R is not closed" | tee -a $C; exit 3; }
  [ "$(ls $R/journal/*.jsonl | wc -l)" = "1" ] || { echo "STOP: $R has more than one journal day file" | tee -a $C; exit 3; }
  mkdir -p $RUNS/$WS
  echo "$(date '+%H:%M:%S') pair $WS starts; load $(cut -d' ' -f1-3 /proc/loadavg); other python processes $(pgrep -c -f '[p]ython3' )" >> $C
  ( nice -n 0 $PY -m creature.replay --genome $G/BRAIN-LEAN-TWIN-$WS.genome --tape $R/tape --out $RUNS/$WS/off --closed --timings --counters-every 1000 --against /data/dev/brain-runs/organ/rung2/$WS/twin/journal.jsonl > $L/gate-off-$WS.log 2>&1 ) & P1=$!
  ( nice -n 0 $PY -m creature.replay --genome $G/BRAIN-LEAN-TWIN-HEAR-$WS.genome --tape $R/tape --out $RUNS/$WS/on --closed --timings --counters-every 1000 > $L/gate-on-$WS.log 2>&1 ) & P2=$!
  wait $P1; rc1=$?; echo $rc1 > $RUNS/$WS/i1-twin.exit
  wait $P2; rc2=$?; echo $rc2 > $RUNS/$WS/on.exit
  echo "$(date '+%H:%M:%S') pair $WS done: off (against the recorded twin) exit $rc1 · on exit $rc2; load $(cut -d' ' -f1-3 /proc/loadavg)" >> $C
  [ $rc2 = 0 ] || { echo "STOP: the ON replay failed at $WS" >> $C; exit 4; }
done
date "+%Y-%m-%d %H:%M:%S %z phase 1 done" >> $C
declare -A P=()
for WS in $SEEDS; do
  R=/data/dev/genome-lives/brain-lean-$WS; J=$(ls $R/journal/*.jsonl | head -1)
  ( nice -n 10 $PY -m creature.replay --genome $G/BRAIN-LEAN-$WS.genome --tape $R/tape --out $RUNS/$WS/brain --closed --against $J > $L/gate-brain-$WS.log 2>&1; echo $? > $RUNS/$WS/i1-brain.exit ) & P["brain-$WS"]=$!
  ( nice -n 10 $PY tools/brain/grade_life.py --root $R --journal $RUNS/$WS/off/journal.jsonl --genome $G/BRAIN-LEAN-TWIN-$WS.genome --label twin --out $RUNS/$WS/grade-off > $L/gate-grade-off-$WS.log 2>&1 ) & P["grade-off-$WS"]=$!
  ( nice -n 10 $PY tools/brain/grade_life.py --root $R --journal $RUNS/$WS/on/journal.jsonl --genome $G/BRAIN-LEAN-TWIN-HEAR-$WS.genome --label twin --out $RUNS/$WS/grade-on > $L/gate-grade-on-$WS.log 2>&1 ) & P["grade-on-$WS"]=$!
done
for K in 1 2 3 4 5 6 7 8 9 10; do
  D=$RUNS/$NULLSEED/null-$K; NG=$G/BRAIN-LEAN-TWIN-HEAR-NULL-$NULLSEED-k$K.genome; mkdir -p $D
  ( nice -n 10 $PY tools/brain/make_tape.py --genome $NG --root $D/life > $L/gate-null-tape-$K.log 2>&1 && cp $NG $D/GENOME.genome && cp $NG $D/life/GENOME.genome && nice -n 10 $PY -m creature.replay --genome $NG --tape $D/life/tape --out $D/on --closed > $L/gate-null-$K.log 2>&1 ) & P["null-$K"]=$!
done
fail=0
for k in "${!P[@]}"; do wait "${P[$k]}"; rc=$?; echo "$(date '+%H:%M:%S') $k exit $rc" >> $C; [ $rc = 0 ] || fail=1; done
for WS in $SEEDS; do echo "i1-brain-$WS exit $(cat $RUNS/$WS/i1-brain.exit)" >> $C; done
date "+%Y-%m-%d %H:%M:%S %z phase 2 done (a step failed: $fail)" >> $C
exit $fail
