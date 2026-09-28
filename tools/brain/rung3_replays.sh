#!/bin/bash
# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:44 +0400 — RUNG 3 after the full organism's life has CLOSED: every replay runs on the tape
# CUT at the lived seq (tools/brain/cut_tape.py; the reviewer's B1), under the life's own code checkout; the live journal is
# handed to --against as ONE file (B2). usage: rung3_replays.sh <life name> <world seed> <lean life name>
set -u
NAME="$1"; WS="$2"; LEAN="$3"
R=/data/dev/genome-lives/$NAME; CODE=$R/code; OUT=/data/dev/brain-runs/organ/rung3/$NAME; L=$OUT/logs; mkdir -p $L
T=/data/dev/genome-wt-organ
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TMPDIR=/data/dev/brain-runs/organ/tmp
[ -f $R/STOPPED-AT ] || { echo "STOP: $R is not closed"; exit 3; }
date "+%Y-%m-%d %H:%M:%S %z start" > $OUT/clock.txt
( cd $T && PYTHONPATH=$T /usr/bin/python3 -B tools/brain/cut_tape.py --root $R --out $OUT/cut > $OUT/cut.json 2> $L/cut.err ); rc=$?
echo "cut exit $rc" >> $OUT/clock.txt; [ $rc = 0 ] || exit 4
( cd $CODE && PYTHONPATH=$CODE nice -n 10 /usr/bin/python3 -B -m creature.replay --genome $R/GENOME.genome --tape $OUT/cut/tape --out $OUT/identity --closed --against $OUT/cut/live-journal.jsonl > $L/identity.log 2>&1 ) &
PI=$!
( cd $CODE && PYTHONPATH=$CODE nice -n 10 /usr/bin/python3 -B -m creature.replay --genome $R/GENOME.genome --tape $OUT/cut/tape --out $OUT/blind --blind brain --closed > $L/blind.log 2>&1 ) &
PB=$!
wait $PI; echo "identity exit $?" >> $OUT/clock.txt
wait $PB; echo "blind exit $?" >> $OUT/clock.txt
date "+%Y-%m-%d %H:%M:%S %z replays done" >> $OUT/clock.txt
cd $T; export PYTHONPATH=$T
/usr/bin/python3 -B tools/brain/journal_diff.py --a $OUT/cut/live-journal.jsonl --b $OUT/blind/journal.jsonl > $OUT/disturbance.txt 2>&1; echo "disturbance exit $?" >> $OUT/clock.txt
/usr/bin/python3 -B tools/brain/journal_diff.py --a $OUT/cut/live-journal.jsonl --b $OUT/blind/journal.jsonl --plant > $OUT/disturbance-planted.txt 2>&1; echo "disturbance-planted exit $? (must be 1)" >> $OUT/clock.txt
/usr/bin/python3 -B tools/brain/grade_life.py --root $R --label full --out $OUT/grade-full > $L/grade-full.log 2>&1; echo "grade-full exit $?" >> $OUT/clock.txt
# THE BRAIN IS THE SAME BRAIN: the full organism's answers against the LEAN life's at the same world seed, item by item
/usr/bin/python3 - $R/journal /data/dev/genome-lives/$LEAN/journal > $OUT/same-brain.txt 2>&1 <<'PYEOF'
import collections, json, sys
from pathlib import Path
def answers(d):
    out = {}
    for f in sorted(Path(d).glob("*.jsonl")):
        for line in f.open(encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                if r.get("kind") == "answer" and r.get("item") is not None and r.get("by") == "brain":
                    out.setdefault(str(r["item"]), r.get("answer"))
    return out
a, b = answers(sys.argv[1]), answers(sys.argv[2])
per = collections.defaultdict(lambda: [0, 0, None])
for k in sorted(set(a) | set(b)):
    m = k.split(":")[0]
    per[m][0] += 1
    same = k in a and k in b and json.dumps(a[k], sort_keys=True) == json.dumps(b[k], sort_keys=True)
    per[m][1] += int(same)
    if not same and per[m][2] is None:
        per[m][2] = k + (" (only in the full life)" if k not in b else " (only in the lean life)" if k not in a else "")
tot = sum(v[0] for v in per.values()); eq = sum(v[1] for v in per.values())
print(f"THE BRAIN IS THE SAME BRAIN · the full organism vs the lean life · items {tot} · equal {eq} · verdict {'EQUAL' if tot and tot == eq else 'DIFFERENT'}")
for m in sorted(per):
    print(f"  {m:<8} items {per[m][0]:>5} · equal {per[m][1]:>5} · first difference {per[m][2] or '—'}")
sys.exit(0 if tot and tot == eq else 1)
PYEOF
echo "same-brain exit $?" >> $OUT/clock.txt
date "+%Y-%m-%d %H:%M:%S %z readers done" >> $OUT/clock.txt
