#!/bin/bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 — the five suites on ONE commit of a tree, each waited on by its own pid, each exit read.
set -u
CODE="$1"; L=/data/dev/brain-runs/day0929/wordroad/logs
cd "$CODE" || exit 2
[ -z "$(git status --porcelain)" ] || { echo "STOP: $CODE is not clean"; exit 3; }
H=$(git rev-parse --short HEAD)
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TMPDIR=/data/dev/brain-runs/day0929/tmp PYTHONPATH=$CODE
date "+%Y-%m-%d %H:%M:%S %z" > $L/final-$H.started
nice -n 10 /usr/bin/python3 -B -u -m unittest discover -s tests/brain/scene -t . > $L/final-scene-$H.log 2>&1 &  P1=$!
nice -n 10 /data/dev/venvs/brain/bin/python -B -u -m unittest discover -s tests/brain -t . > $L/final-brainvenv-$H.log 2>&1 &  P2=$!
nice -n 10 /usr/bin/python3 -B -u -m unittest discover -s tests/genome -t . > $L/final-genome-$H.log 2>&1 &  P3=$!
nice -n 10 /usr/bin/python3 -B -u -m unittest discover -s tests/creature -t . > $L/final-creature-$H.log 2>&1 &  P4=$!
nice -n 10 /usr/bin/python3 -B -u -m unittest discover -s tests/tools -t . > $L/final-tools-$H.log 2>&1 &  P5=$!
wait $P1; echo $? > $L/final-scene-$H.exit
wait $P2; echo $? > $L/final-brainvenv-$H.exit
wait $P3; echo $? > $L/final-genome-$H.exit
wait $P4; echo $? > $L/final-creature-$H.exit
wait $P5; echo $? > $L/final-tools-$H.exit
date "+%Y-%m-%d %H:%M:%S %z" > $L/final-$H.finished
{ echo "the five suites on $H ($(cat $L/final-$H.started) → $(cat $L/final-$H.finished)), BLAS threads 1"
  for s in scene brainvenv genome creature tools; do echo "== $s exit=$(cat $L/final-$s-$H.exit)"; grep -a -E '^(Ran [0-9]+ tests|OK|FAILED)' $L/final-$s-$H.log; grep -a -E '^(ERROR|FAIL):' $L/final-$s-$H.log | head -12; done; } > $L/final-suites-$H.txt
cat $L/final-suites-$H.txt
