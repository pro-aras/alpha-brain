#!/bin/bash
# edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-04 19:19 +0400 — ONE replay of the W1 bench (PREREG-W1-MOUTH-VOICES-BRAIN §4),
# the form of /data/dev/swarm/2026-10-03/int/one_replay.sh: the tape and journal are the builder's sha-checked COPIES under
# /data/dev/swarm/2026-10-03/kimi-w1-records/w1/lives/ (never a life's root, RULES §7); the replay's TMPDIR is its own
# (runs/<life>/tmp-<arm>-<life>/ so the saved state — state/brain.json for I2, state/predictions.jsonl for F — is read from
# the work root after; creature.replay never deletes it). Its log, exit code and clock beside it. Meant to run THROUGH slot.
# usage: one_run.sh <life: lean-2026110X|full-20261102> <arm: plain|off|on|plant>
set -u
WT=/data/dev/genome-wt-toys-1003
B=/data/dev/swarm/2026-10-03/kimi-w1-records/w1
LIFE=$1; ARM=$2
G=$WT/genome/brain/lives; R=$B/lives/$LIFE; O=$B/runs/$LIFE
case "$LIFE" in
  lean-2026110*) ws=${LIFE#lean-}
    PLAIN=$G/BRAIN-LEAN-$ws.genome; OFF=$G/BRAIN-LEAN-DRIVE-$ws.genome
    ON=$WT/docs/organism/whole/records/w1/genomes/BRAIN-LEAN-DRIVE-$ws-W1.genome
    AGAINST=$R/journal/2026-09-28.jsonl;;
  full-20261102) ws=20261102
    PLAIN=$G/BRAIN-FULL-20261102.genome; OFF=$G/BRAIN-FULL-DRIVE-20261102.genome
    ON=$WT/docs/organism/whole/records/w1/genomes/BRAIN-FULL-DRIVE-20261102-W1.genome
    AGAINST=$R/journal.jsonl;;
  *) echo "no such life: $LIFE"; exit 97;;
esac
case "$ARM" in
  plain) GENOME=$PLAIN; A=$AGAINST; T=;;
  off)   GENOME=$OFF;   A=-;        T=--timings;;
  on)    GENOME=$ON;    A=-;        T=--timings;;
  plant) GENOME=$B/genomes/PLANT-$ws.genome; A=$AGAINST; T=;;
  *) echo "no such arm: $ARM"; exit 97;;
esac
cd "$WT" || exit 97
export TMPDIR=$O/tmp-$ARM-$LIFE PYTHONPATH=$WT PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p "$TMPDIR" "$O"
args=(--genome "$GENOME" --tape "$R/tape" --out "$O/$ARM" --closed)
[ -n "$T" ] && args+=($T)
[ "$A" != "-" ] && args+=(--against "$A")
{ echo "$(date '+%F %T %z') start code $(git rev-parse HEAD) genome $(sha256sum "$GENOME" | cut -c1-16) arm $ARM life $LIFE"; } > "$O/$ARM.clock"
/usr/bin/python3 -B -m creature.replay "${args[@]}" > "$B/logs/replay-$LIFE-$ARM.log" 2>&1
rc=$?
echo "$rc" > "$O/$ARM.exit"
echo "$(date '+%F %T %z') end rc=$rc last line: $(tail -n 1 "$B/logs/replay-$LIFE-$ARM.log")" >> "$O/$ARM.clock"
exit "$rc"
