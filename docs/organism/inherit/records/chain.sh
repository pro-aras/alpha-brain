#!/usr/bin/env bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:5x +0400 — PREREG-INHERIT §4: the eight lives, two at a time, then I7, then the reader. Needs no seat.
set -u
D=/data/dev/brain-runs/day0929/inherit; G=$D/genomes; R=$D/run_inherit_life.sh
P=/data/dev/genome-lives/brain-lean-nearest-20261102; NP=/data/dev/genome-lives/inh-nullparent-20261102
LOG=$D/chain.log
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %z') $*" >> "$LOG"; }
waitfor() { while [ "$(systemctl --user is-active "$1" 2>/dev/null)" = "active" ] || [ "$(systemctl --user is-active "$1" 2>/dev/null)" = "activating" ]; do /usr/bin/python3 -c "import time; time.sleep(15)"; done; }
say "chain start; waiting for the suites and the null parent"
waitfor inherit-suites-2.service
waitfor inh-nullparent.service
say "null parent: $(head -1 $NP/RUN-VERDICT 2>/dev/null) · its brain pair: $(ls $NP/state/brain.json $NP/state/brain.npz 2>&1 | tr '\n' ' ')"
pair() { # two lives at once, each waited on by its own pid
  bash $R $1 $2 $3 "${4:-}" > $D/life-$1.log 2>&1 & A=$!
  bash $R $5 $6 $7 "${8:-}" > $D/life-$5.log 2>&1 & B=$!
  wait $A; say "$1 exit $? · $(head -1 /data/dev/genome-lives/$1/RUN-VERDICT 2>/dev/null)"
  wait $B; say "$5 exit $? · $(head -1 /data/dev/genome-lives/$5/RUN-VERDICT 2>/dev/null)"
}
pair inh-c-t1 $G/INH-T1-20261103.genome 1800 $P            inh-b-t1 $G/INH-T1-20261103.genome 1800 ""
pair inh-n-t1 $G/INH-T1-20261103.genome 1800 $NP           inh-c-t1000 $G/INH-T1000-20261103.genome 2400 $P
pair inh-b-t1000 $G/INH-T1000-20261103.genome 2400 ""      inh-n-t1000 $G/INH-T1000-20261103.genome 2400 $NP
pair inh-c-t10000 $G/INH-T10000-20261103.genome 5400 $P    inh-b-t10000 $G/INH-T10000-20261103.genome 5400 ""
/usr/bin/python3 -B $D/read_inherit.py $D/INHERIT-READINGS.md > $D/read.log 2>&1; say "reader exit $?"
bash $D/i7_kill.sh > $D/i7.log 2>&1; say "I7 exit $?"
say "chain end"
