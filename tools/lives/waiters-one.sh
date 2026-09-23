#!/usr/bin/env bash
# edit: Claude (Fable 5.1), 2026-09-23 07:38 +0400 — the 2 h smoke skips the 20 random twins (they ran an hour beside alpha4-1 at load 26 for a reading the 24 h verdict makes on the CLOSED tape — #236)
# Claude (Fable 5.1), 2026-09-22 — THE ONE LIFE's three reads (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §6): the 2 h SMOKE (the reader's
# positive control on this cadence, 4 workers, the one replay-based read beside the live life), the 8 h CHECK (NO replay, no worker:
# STATUS's series + the exam files + the journal, by tools/lives/check.py), the 24 h VERDICT (the life closed WHOLE first, then 8 workers on the closed tape — the edit note below).
set -u
NAME="${1:?life name}"; ROOT="/data/dev/genome-lives/$NAME"; CODE="$ROOT/code"
START=$(date -d "$(cat "$ROOT/STARTED-AT")" +%s); GENOME=$(sed -n "s/^GENOME=//p" "$ROOT/unit.env")
SMOKE_AT=$((START + 2*3600 + 120)); CHECK_AT=$((START + 8*3600 + 120)); VERDICT_AT=$((START + 24*3600 + 120))
mkdir -p "$ROOT/readings"
nohup bash -c "until [ \$(date +%s) -ge $SMOKE_AT ]; do sleep 60; done; cd $CODE && nice -n 5 python3 tools/verdict_g4.py --root $ROOT --genome $GENOME --out $ROOT/readings/smoke-2h --skip-random --hours 2 --slice-hours 2 --regime-step 25 --workers 4 --unit creature-g5@$NAME.service; echo exit=\$?; python3 -c \"import json;print('backlog after the smoke:', json.load(open('$ROOT/STATUS.json')).get('mind_backlog_rows'))\"" > "$ROOT/readings/smoke-2h.log" 2>&1 &
echo "smoke waiter pid $! fires $(date -d @$SMOKE_AT '+%H:%M')"
nohup bash -c "until [ \$(date +%s) -ge $CHECK_AT ]; do sleep 60; done; cd $CODE && python3 tools/lives/check.py --root $ROOT --hours 8; echo exit=\$?" > "$ROOT/readings/check-8h.log" 2>&1 &
echo "check waiter pid $! fires $(date -d @$CHECK_AT '+%Y-%m-%d %H:%M')"
# edit: Claude (Fable 5.1), 2026-09-22 22:28 +0400 — the VERDICT reads a CLOSED tape (plan §6/§8 as amended tonight): NRestarts/CPU read from systemd BEFORE the
# stop (a stopped instance forgets them), the watch timer and the unit stopped at 24 h + 2 min (the body's stop() lands the in-flight think and
# writes the `stop` event — the reader waits for it), then the reader with --nrestarts/--cpu-ns (no --unit) and --sizing-prediction from
# $ROOT/SIZING-PREDICTION (written by launch.sh's 5th argument, or by hand before the launch). #236: no reader beside a live life for hours.
SP_FILE="$ROOT/SIZING-PREDICTION"
nohup bash -c "until [ \$(date +%s) -ge $VERDICT_AT ]; do sleep 60; done; NR=\$(systemctl --user show creature-g5@$NAME.service -p NRestarts --value); CPU=\$(systemctl --user show creature-g5@$NAME.service -p CPUUsageNSec --value); echo \"NRestarts \$NR CPUUsageNSec \$CPU read at \$(date '+%H:%M:%S') before the stop\"; systemctl --user stop creature-g5-watch@$NAME.timer; systemctl --user stop creature-g5@$NAME.service; for i in \$(seq 1 60); do grep -qsF '\"event\": \"stop\"' $ROOT/journal/*.jsonl && break; sleep 5; done; grep -hF '\"event\": \"stop\"' $ROOT/journal/*.jsonl | tail -1; SP=\$(cat $SP_FILE 2>/dev/null); cd $CODE && nice -n 5 python3 tools/verdict_g4.py --root $ROOT --genome $GENOME --out $ROOT/readings/verdict-24h --hours 24 --slice-hours 4 --regime-step 25 --workers 8 --nrestarts \${NR:-0} --cpu-ns \${CPU:-0} \${SP:+--sizing-prediction \$SP}; echo exit=\$?" > "$ROOT/readings/verdict-24h.log" 2>&1 &
echo "verdict waiter pid $! fires $(date -d @$VERDICT_AT '+%Y-%m-%d %H:%M')"
