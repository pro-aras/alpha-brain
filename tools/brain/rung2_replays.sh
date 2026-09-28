#!/bin/bash
# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:29 +0400 — RUNG 2 after the lives have CLOSED (PREREG §6): per life the identity replay and
# the twin (the life's own tape under the genome without the BRAIN line); once, at 20261102, the blind-brain road and the
# null (a made tape, utterances shuffled, k = 1). Every replay runs under the LIFE's own code checkout. Each is waited on by
# its own pid and its exit is written; then the readers run one by one and every exit is kept.
set -u
OUT=/data/dev/brain-runs/organ/rung2; L=$OUT/logs; mkdir -p $L
GATE=/data/dev/brain-runs/organ/gate-alone-merged-f17a596
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TMPDIR=/data/dev/brain-runs/organ/tmp
SEEDS="20261101 20261102 20261103"
date "+%Y-%m-%d %H:%M:%S %z replays start" > $OUT/clock.txt
declare -A P=()
for WS in $SEEDS; do
  R=/data/dev/genome-lives/brain-lean-$WS; CODE=$R/code
  [ -f $R/STOPPED-AT ] || { echo "STOP: $R is not closed" | tee -a $OUT/clock.txt; exit 3; }
  # edit: Claude (Fable 5.1, the seat), 2026-09-29 00:24 +0400 — the reviewer's B2, left LOUD: this reads the FIRST journal day file only. Every
  # rung-2 life stayed inside one UTC day (one day file each — checked), so it held. A life that crosses 00:00 UTC must go
  # the rung-3 road instead: tools/brain/cut_tape.py writes the live journal as ONE file (rung3_replays.sh).
  [ "$(ls $R/journal/*.jsonl | wc -l)" = "1" ] || { echo "STOP: $R has more than one journal day file — use the cut-tape road" | tee -a $OUT/clock.txt; exit 3; }
  J=$(ls $R/journal/*.jsonl | head -1)
  ( cd $CODE && PYTHONPATH=$CODE nice -n 10 /usr/bin/python3 -B -m creature.replay --genome $R/GENOME.genome --tape $R/tape --out $OUT/$WS/identity --closed --against $J > $L/identity-$WS.log 2>&1 ) &
  P["identity-$WS"]=$!
  ( cd $CODE && PYTHONPATH=$CODE nice -n 10 /usr/bin/python3 -B -m creature.replay --genome $CODE/genome/brain/lives/BRAIN-LEAN-TWIN-$WS.genome --tape $R/tape --out $OUT/$WS/twin --closed > $L/twin-$WS.log 2>&1 ) &
  P["twin-$WS"]=$!
done
WS=20261102; R=/data/dev/genome-lives/brain-lean-$WS; CODE=$R/code
( cd $CODE && PYTHONPATH=$CODE nice -n 10 /usr/bin/python3 -B -m creature.replay --genome $R/GENOME.genome --tape $R/tape --out $OUT/$WS/blind --blind brain --closed > $L/blind-$WS.log 2>&1 ) &
P["blind-$WS"]=$!
( cd $CODE && NG=$CODE/genome/brain/lives/BRAIN-LEAN-NULL-$WS-k1.genome && PYTHONPATH=$CODE nice -n 10 /usr/bin/python3 -B tools/brain/make_tape.py --genome $NG --root $OUT/$WS/null-life > $L/null-tape-$WS.log 2>&1 && cp $NG $OUT/$WS/null-life/GENOME.genome && PYTHONPATH=$CODE nice -n 10 /usr/bin/python3 -B -m creature.replay --genome $NG --tape $OUT/$WS/null-life/tape --out $OUT/$WS/null --closed > $L/null-$WS.log 2>&1 ) &
P["null-$WS"]=$!
fail=0
for k in "${!P[@]}"; do wait "${P[$k]}"; rc=$?; echo "$k exit $rc" >> $OUT/clock.txt; [ $rc = 0 ] || fail=1; done
date "+%Y-%m-%d %H:%M:%S %z replays done (fail=$fail)" >> $OUT/clock.txt
# the readers — under the INTEGRATION tree's tools (the graders are not the life's code)
T=/data/dev/genome-wt-organ; export PYTHONPATH=$T; cd $T
for WS in $SEEDS; do
  R=/data/dev/genome-lives/brain-lean-$WS; D=$OUT/$WS
  /usr/bin/python3 -B tools/brain/parity.py --journal $R/journal --gate-answers $GATE/$WS/$WS/gate-answers.json --out $D/parity.txt > $L/parity-$WS.log 2>&1; echo "parity-$WS exit $?" >> $OUT/clock.txt
  /usr/bin/python3 -B tools/brain/parity.py --journal $R/journal --gate-answers $GATE/$WS/$WS/gate-answers.json --plant > $L/parity-planted-$WS.log 2>&1; echo "parity-planted-$WS exit $? (must be 1)" >> $OUT/clock.txt
  /usr/bin/python3 -B tools/brain/journal_diff.py --a $R/journal --b $D/twin/journal.jsonl > $D/disturbance.txt 2>&1; echo "disturbance-$WS exit $?" >> $OUT/clock.txt
  /usr/bin/python3 -B tools/brain/grade_life.py --root $R --journal $D/twin/journal.jsonl --genome $R/code/genome/brain/lives/BRAIN-LEAN-TWIN-$WS.genome --label twin --out $D/grade-twin > $L/grade-twin-$WS.log 2>&1; echo "grade-twin-$WS exit $?" >> $OUT/clock.txt
  /usr/bin/python3 -B tools/brain/grade_life.py --root $R --label brain --out $D/grade-brain --pair-with $D/grade-twin/grade.json > $L/grade-brain-$WS.log 2>&1; echo "grade-brain-$WS exit $?" >> $OUT/clock.txt
done
WS=20261102; D=$OUT/$WS
/usr/bin/python3 -B tools/brain/journal_diff.py --a $D/twin/journal.jsonl --b $D/blind/journal.jsonl --keep-answers > $D/twin-vs-blind.txt 2>&1; echo "twin-vs-blind-$WS exit $?" >> $OUT/clock.txt
/usr/bin/python3 -B tools/brain/null_identity.py --journal $D/null/journal.jsonl --offline /data/dev/brain-runs/organ/null-k1/answers-$WS-k01.json > $D/null-identity.txt 2>&1; echo "null-identity-$WS exit $?" >> $OUT/clock.txt
/usr/bin/python3 -B tools/brain/grade_life.py --root $D/null-life --journal $D/null/journal.jsonl --label null --out $D/grade-null > $L/grade-null-$WS.log 2>&1; echo "grade-null-$WS exit $?" >> $OUT/clock.txt
date "+%Y-%m-%d %H:%M:%S %z readers done" >> $OUT/clock.txt
