#!/usr/bin/env bash
# edit: Claude (Fable 5.1), 2026-09-23 20:06 +0400 — LADDER 2's 20-MIN PRE-FLIGHT for one rung (A4-LADDER-2-PREREG §1.7, ladder 1's law): a4l2-pre-<rung> on C2 with
# the rung's genome PATH; the stop at +20 min and the post-close read at +22 min on ABSOLUTE --on-calendar timers.
# usage: a4_ladder2_preflight.sh <rung lower> <commit> <genome path relative to the checkout>
set -u
R="${1:?rung}"; C="${2:?commit}"; G="${3:?genome path}"; NAME="a4l2-pre-$R"; ROOT=/data/dev/genome-lives/$NAME
cd /data/dev/genome
git cat-file -e "$C:$G" 2>/dev/null || { echo "[preflight] genome $G is not in commit $C"; exit 2; }
bash tools/lives/launch.sh "$NAME" "$C" "$G" 15000 2>&1 | tail -3 | cut -c1-200
STOPAT=$(date -d '+20 minutes' '+%Y-%m-%d %H:%M:%S'); READAT=$(date -d '+22 minutes' '+%Y-%m-%d %H:%M:%S')
systemd-run --user --on-calendar="$STOPAT" --timer-property=RemainAfterElapse=no --unit="$NAME-stop" --description="stop the pre-flight life $NAME at $STOPAT" \
  /usr/bin/bash -c "systemctl --user stop creature-g5-watch@$NAME.timer; systemctl --user stop creature-g5@$NAME.service; date '+%Y-%m-%d %H:%M %z' > $ROOT/STOPPED-AT" 2>&1 | tail -1
systemd-run --user --on-calendar="$READAT" --timer-property=RemainAfterElapse=no --unit="$NAME-postclose" --description="post-close read of $NAME at $READAT" \
  /usr/bin/bash /data/dev/genome-lives/a4l2-preflight-postclose.sh "$R" "$G" 2>&1 | tail -1
echo "[preflight] $NAME alive on $C with $G at $(date '+%H:%M %z'); stop at $STOPAT; post-close read at $READAT"
