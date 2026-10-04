#!/bin/bash
# edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-04 19:19 +0400 — the OFF+ON replay pair of ONE life run SIDE BY SIDE
# (PREREG-W1-MOUTH-VOICES-BRAIN §3 K: «the pair run side by side»; PREREG-BRAIN-DRIVES §8 (11): the ratio prices the box's
# load away). Both replays in this one job's cgroup; the job's exit is the worse of the two. Meant to run THROUGH slot at 4G.
# usage: k_pair.sh <life>
set -u
LIFE=$1
D=/data/dev/genome-wt-toys-1003/docs/organism/whole/records/w1
bash $D/one_run.sh $LIFE off & P_OFF=$!
bash $D/one_run.sh $LIFE on  & P_ON=$!
rc=0
wait $P_OFF || rc=1
wait $P_ON || rc=1
echo "$(date '+%F %T %z') pair $LIFE done: off exit $(cat /data/dev/swarm/2026-10-03/kimi-w1-records/w1/runs/$LIFE/off.exit) on exit $(cat /data/dev/swarm/2026-10-03/kimi-w1-records/w1/runs/$LIFE/on.exit); load $(cut -d' ' -f1-3 /proc/loadavg)"
exit $rc
