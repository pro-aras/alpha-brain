#!/bin/bash
# READER-LAG-0923 item 4: gate_g4 1/2/3/6 on THIS worktree, then both suites (-t ., TMPDIR on disk under scratch), then the genome suite's
# one module that failed at a17cb0e in the reader-fix lane, run on the 2357347 EXPORT (is it pre-existing on the base?). Logs to files; the
# verdict lines are grepped FROM THE FILES (#197: unittest's verdict goes to unbuffered stderr).
set -u
W=/data/dev/genome-wt-reader-lag; G=$W/scratch/gates; export TMPDIR=$W/scratch/tmp; mkdir -p "$TMPDIR"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$W" || exit 2
uptime; date "+%Y-%m-%d %H:%M:%S %z"
nice -n 19 python3 tools/gate_g4.py --tree "$W" --only 1,2,3,6 > "$G/gate_g4.log" 2>&1; echo "gate exit=$?" >> "$G/gate_g4.log"
uptime; date "+%Y-%m-%d %H:%M:%S %z"
nice -n 19 python3 -u -m unittest discover -s tests/genome -t . > "$G/suite-genome.log" 2>&1; echo "suite exit=$?" >> "$G/suite-genome.log"
uptime; date "+%Y-%m-%d %H:%M:%S %z"
nice -n 19 python3 -u -m unittest discover -s tests/creature -t . > "$G/suite-creature.log" 2>&1; echo "suite exit=$?" >> "$G/suite-creature.log"
date "+%Y-%m-%d %H:%M:%S %z"
cd "$W/scratch/master-2357347" && nice -n 19 python3 -u -m unittest tests.genome.test_read_lexicon_parser > "$G/base-2357347-read-lexicon-parser.log" 2>&1; echo "exit=$?" >> "$G/base-2357347-read-lexicon-parser.log"
cd "$W" && nice -n 19 python3 -u -m unittest tests.genome.test_read_lexicon_parser > "$G/tip-read-lexicon-parser.log" 2>&1; echo "exit=$?" >> "$G/tip-read-lexicon-parser.log"
echo "=== verdicts (from the files) ==="
grep -h "G4 gates\|gate exit" "$G/gate_g4.log"
for f in suite-genome suite-creature base-2357347-read-lexicon-parser tip-read-lexicon-parser; do echo "-- $f"; grep -h "^Ran \|^OK\|^FAILED\|exit=" "$G/$f.log"; done
echo "=== leaked temp roots under scratch/tmp (named, not removed) ==="; ls "$TMPDIR" | wc -l; du -sh "$TMPDIR" | cut -f1
date "+%Y-%m-%d %H:%M:%S %z"
