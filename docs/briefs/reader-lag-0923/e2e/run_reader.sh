#!/bin/bash
# usage: run_reader.sh old|new ROOT HOURS OUT   — one reader, nice 19, one BLAS thread, TMPDIR on disk; the log beside OUT
set -u
W=/data/dev/genome-wt-reader-lag
case "$1" in old) TREE=$W/scratch/master-2357347;; new) TREE=$W;; *) echo "old|new"; exit 2;; esac
ROOT=$2; HOURS=$3; OUT=$4
uptime
date "+%Y-%m-%d %H:%M:%S %z"
cd "$TREE" && OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 TMPDIR=$W/scratch/tmp nice -n 19 python3 tools/verdict_g4.py --root "$ROOT" --genome "$ROOT/GENOME.genome" --out "$OUT" --skip-random --workers 2 --hours "$HOURS" > "$OUT.log" 2>&1
rc=$?
echo "exit=$rc" >> "$OUT.log"; date "+%Y-%m-%d %H:%M:%S %z" >> "$OUT.log"
tail -2 "$OUT.log"
