#!/usr/bin/env bash
# edit: Claude (Fable 5.1), 2026-09-23 13:22 +0400 — THE A4 LADDER'S LAUNCH + WAITERS for one rung (A4-LADDER-PREREG §1.5, §4): the life on the RUNG'S OWN
# BRANCH COMMIT (§1.3), a STATUS sampler every 5 min into readings/status-series.jsonl, check.py (the life's own checkout, no replay) at +2 h and
# +8 h, the stop WHOLE at 8 h + 2 min, and for LANG the seat's chat schedule (tools/chat_seat.py --schedule; it waits until hour 1 by itself).
# NO reader beside a life (#236): the rung's reads run after the closes, from its own checkout.   usage: a4_ladder_launch.sh <rung lower> <commit>
# edit: Claude (Fable 5.1), 2026-09-23 17:03 +0400 — the +2 h / +8 h checks and the 8 h + 2 min STOP on ABSOLUTE wall-clock timers (--on-calendar, computed at launch):
#   today's --on-active monotonic timers drifted +21 min against the wall clock and the seat re-armed five stops by hand (the ladder of 09-23).
set -u
R="${1:?rung}"; C="${2:?commit}"; RU=$(echo "$R" | tr a-z A-Z); NAME="a4l-$R"; ROOT=/data/dev/genome-lives/$NAME; RD=$ROOT/readings
cd /data/dev/genome
bash tools/lives/launch.sh "$NAME" "$C" "genome/ladder/A4L-$RU.genome" 15000 2>&1 | grep -E 'STATUS after|alive|error|Error' | cut -c1-200
mkdir -p "$RD"
systemd-run --user --on-active=5min --on-unit-active=5min --unit="$NAME-sampler" --description="$NAME STATUS every 5 min → readings/status-series.jsonl" \
  /usr/bin/bash -c "python3 -c \"import json,time; d=json.load(open('$ROOT/STATUS.json')); d['sampled_at']=time.strftime('%Y-%m-%dT%H:%M:%S%z'); print(json.dumps(d))\" >> $RD/status-series.jsonl" 2>&1 | tail -1
for H in 2 8; do systemd-run --user --on-calendar="$(date -d "+${H} hours" '+%Y-%m-%d %H:%M:%S')" --timer-property=RemainAfterElapse=no --unit="$NAME-check${H}h" --description="$NAME check.py at +$H h (no replay)" \
  /usr/bin/bash -c "cd $ROOT/code && OPENBLAS_NUM_THREADS=1 nice -n 10 python3 tools/lives/check.py --root $ROOT > $RD/check-${H}h.log 2>&1" 2>&1 | tail -1; done
systemd-run --user --on-calendar="$(date -d '+482 minutes' '+%Y-%m-%d %H:%M:%S')" --timer-property=RemainAfterElapse=no --unit="$NAME-stop" --description="stop $NAME WHOLE at 8 h + 2 min" \
  /usr/bin/bash -c "systemctl --user stop creature-g5-watch@$NAME.timer; systemctl --user stop creature-g5@$NAME.service; systemctl --user stop $NAME-sampler.timer; date '+%Y-%m-%d %H:%M %z' > $ROOT/STOPPED-AT" 2>&1 | tail -1
if [ "$R" = lang ]; then
  systemd-run --user --unit="$NAME-chat" --description="the seat's chat schedule for $NAME (waits until hour 1; one family question every 120 s to hour 8)" \
    /usr/bin/bash -c "cd $ROOT/code && OPENBLAS_NUM_THREADS=1 nice -n 10 python3 tools/chat_seat.py --root $ROOT --schedule --phrasings /data/dev/a4-ladder/fixtures/lang-test-phrasings.json > $RD/chat-schedule.log 2>&1" 2>&1 | tail -1
fi
echo "[ladder] $NAME alive on $C at $(date '+%H:%M %z'); sampler 5 min; check +2 h/+8 h; stop at +8 h 2 min$([ "$R" = lang ] && echo '; the chat schedule armed')"
