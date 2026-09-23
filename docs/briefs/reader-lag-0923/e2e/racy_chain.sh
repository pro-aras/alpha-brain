#!/bin/bash
# READER-LAG-0923 (b): after the gates/suites finish — two extra WHOLE-record controls (life2/life3b at 26 h), then the three racy-close
# fixtures (frozen@729, late@729, crash@705) built and read by the NEW reader (--hours 1). One process at a time, nice 19, TMPDIR on disk.
set -u
W=/data/dev/genome-wt-reader-lag; E=$W/scratch/e2e; C=$W/scratch/control; export TMPDIR=$W/scratch/tmp
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
until grep -q "=== leaked temp roots" $W/scratch/gates/run_gates.log 2>/dev/null; do sleep 15; done
uptime; date "+%Y-%m-%d %H:%M:%S %z"
for n in run-g4-life2-20260920-1212 run-g4-life3b-20260921-1606; do
  for T in old new; do TREE=$W/scratch/master-2357347; [ $T = new ] && TREE=$W
    nice -n 19 python3 $C/gather_dump.py $TREE $C/roots/$n 26 $C/out/$n-26-$T.json $C/out/$n-26-$T-dir > $C/out/$n-26-$T.log 2>&1 || echo "gather $T $n 26 FAILED"; done
  echo "== $n --hours 26 (whole)"; cut -c1-260 $C/out/$n-26-old.log
  nice -n 19 python3 $C/control_diff.py $C/out/$n-26-old.json $C/out/$n-26-new.json | tee $C/out/$n-26-diff.log | cut -c1-300
done
for spec in "frozen 729" "late 729" "crash 705"; do set -- $spec; M=$1; N=$2
  R=$E/racy-$M-$N; rm -rf $R; date "+%H:%M:%S"; nice -n 19 python3 $E/build_racy_root.py $R $M $N > $E/build-racy-$M-$N.log 2>&1; echo "build exit=$?" >> $E/build-racy-$M-$N.log; tail -2 $E/build-racy-$M-$N.log | cut -c1-900
  $E/run_reader.sh new $R 1 $E/racy-$M-$N-read | tail -1 | cut -c1-200
  grep -h "^\[LAG\]\|^\[ALIVE\]\|^\[REPLAY\]\|^VERDICT" $E/racy-$M-$N-read.log | cut -c1-420
done
date "+%Y-%m-%d %H:%M:%S %z"; echo RACY-CHAIN-DONE
