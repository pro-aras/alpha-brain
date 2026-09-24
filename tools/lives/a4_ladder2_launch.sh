#!/usr/bin/env bash
# edit: Claude (Fable 5.1), 2026-09-23 17:10 +0400 — LADDER 2's launch + waiters for one rung (A4-LADDER-2-PREREG §2, §5): a life named a4l2-<rung>
# on the ONE integration commit C2 (§1: one code version for all rungs) with the genome PATH given (genome/ladder2/A4L2-<RUNG>.genome),
# a STATUS sampler every 5 min into readings/status-series.jsonl, check.py at +2 h / +8 h and the STOP WHOLE at 8 h + 2 min — all three
# on ABSOLUTE --on-calendar timers computed here (today's --on-active timers drifted +21 min), and for a rung that declares CHAT the
# seat's chat schedule. NO reader beside a life (#236).   usage: a4_ladder2_launch.sh <rung lower> <commit> <genome path relative to the checkout>
set -u
R="${1:?rung}"; C="${2:?commit}"; G="${3:?genome path}"; NAME="a4l2-$R"; ROOT=/data/dev/genome-lives/$NAME; RD=$ROOT/readings
cd /data/dev/genome
git cat-file -e "$C:$G" 2>/dev/null || { echo "[ladder2] genome $G is not in commit $C — commit it there first (launch.sh checks out $C and reads the genome from it)"; exit 2; }
HAS_CHAT=$(git show "$C:$G" | grep -cE '^CHAT ' || true)
bash tools/lives/launch.sh "$NAME" "$C" "$G" 15000 2>&1 | grep -E 'STATUS after|alive|error|Error' | cut -c1-200
mkdir -p "$RD"
systemd-run --user --on-active=5min --on-unit-active=5min --unit="$NAME-sampler" --description="$NAME STATUS every 5 min → readings/status-series.jsonl" \
  /usr/bin/bash -c "python3 -c \"import json,time; d=json.load(open('$ROOT/STATUS.json')); d['sampled_at']=time.strftime('%Y-%m-%dT%H:%M:%S%z'); print(json.dumps(d))\" >> $RD/status-series.jsonl" 2>&1 | tail -1
for H in 2 8; do AT=$(date -d "+${H} hours" '+%Y-%m-%d %H:%M:%S'); systemd-run --user --on-calendar="$AT" --timer-property=RemainAfterElapse=no --unit="$NAME-check${H}h" --description="$NAME check.py at +$H h = $AT (no replay)" \
  /usr/bin/bash -c "cd $ROOT/code && OPENBLAS_NUM_THREADS=1 nice -n 10 python3 tools/lives/check.py --root $ROOT > $RD/check-${H}h.log 2>&1" 2>&1 | tail -1; done
STOPAT=$(date -d '+482 minutes' '+%Y-%m-%d %H:%M:%S')
systemd-run --user --on-calendar="$STOPAT" --timer-property=RemainAfterElapse=no --unit="$NAME-stop" --description="stop $NAME WHOLE at 8 h + 2 min = $STOPAT" \
  /usr/bin/bash -c "systemctl --user stop creature-g5-watch@$NAME.timer; systemctl --user stop creature-g5@$NAME.service; systemctl --user stop $NAME-sampler.timer; date '+%Y-%m-%d %H:%M %z' > $ROOT/STOPPED-AT" 2>&1 | tail -1
if [ "$HAS_CHAT" -gt 0 ]; then
  systemd-run --user --unit="$NAME-chat" --description="the seat's chat schedule for $NAME (waits until hour 1; one family question every 120 s to hour 8)" \
    /usr/bin/bash -c "cd $ROOT/code && OPENBLAS_NUM_THREADS=1 nice -n 10 python3 tools/chat_seat.py --root $ROOT --schedule --phrasings /data/dev/a4-ladder/fixtures/lang-test-phrasings.json > $RD/chat-schedule.log 2>&1" 2>&1 | tail -1
fi
echo "[ladder2] $NAME alive on $C with $G at $(date '+%H:%M %z'); sampler 5 min; check +2 h/+8 h (absolute); STOP at $STOPAT$([ "$HAS_CHAT" -gt 0 ] && echo '; the chat schedule armed')"
