#!/bin/bash
# READER-LAG-0923 item 3: old (2357347 export) vs new (this branch) gather() on hard-link COPIES of the five closed G4 roots, each at a
# FULL cut (24 h, the whole record) and a SHORT cut (a fraction of the life: the time-cut road, M > time_cut_seq, closed_whole False).
# Separate processes per tree; the diff in a third. One process at a time, nice 19.
set -u
W=/data/dev/genome-wt-reader-lag; C=$W/scratch/control; OLD=$W/scratch/master-2357347; export TMPDIR=$W/scratch/tmp
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
declare -A SHORT=( [run-g4-attempt1-20260920-0029]=0.1 [run-g4-life1-20260920-0042]=6 [run-g4-life2-20260921-1212]=6 [run-g4-life2-20260920-1212]=6 [run-g4-life3a-20260921-1314]=1 [run-g4-life3b-20260921-1606]=6 )
uptime; date "+%Y-%m-%d %H:%M:%S %z"
pass=0; fail=0
for R in $C/roots/run-g4-*; do
  n=$(basename $R)
  for H in 24 ${SHORT[$n]:-6}; do
    for T in old new; do
      TREE=$OLD; [ $T = new ] && TREE=$W
      nice -n 19 python3 $C/gather_dump.py $TREE $R $H $C/out/$n-$H-$T.json $C/out/$n-$H-$T-dir > $C/out/$n-$H-$T.log 2>&1 || { echo "gather $T $n $H FAILED"; cat $C/out/$n-$H-$T.log | tail -3; }
    done
    echo "== $n --hours $H"; cat $C/out/$n-$H-old.log | cut -c1-260
    nice -n 19 python3 $C/control_diff.py $C/out/$n-$H-old.json $C/out/$n-$H-new.json | tee $C/out/$n-$H-diff.log | cut -c1-400 && pass=$((pass+1)) || fail=$((fail+1))
  done
done
echo "CONTROLS: pass $pass fail $fail"; date "+%Y-%m-%d %H:%M:%S %z"
