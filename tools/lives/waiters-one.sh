#!/usr/bin/env bash
# Claude (Fable 5.1), 2026-09-22 — THE ONE LIFE's three reads (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §6): the 2 h SMOKE (the reader's
# positive control on this cadence, 4 workers, the one replay-based read beside the live life), the 8 h CHECK (NO replay, no worker:
# STATUS's series + the exam files + the journal, by tools/lives/check.py), the 24 h VERDICT (from the life's own checkout, 8 workers).
set -u
NAME="${1:?life name}"; ROOT="/data/dev/genome-lives/$NAME"; CODE="$ROOT/code"
START=$(date -d "$(cat "$ROOT/STARTED-AT")" +%s); GENOME=$(sed -n "s/^GENOME=//p" "$ROOT/unit.env")
SMOKE_AT=$((START + 2*3600 + 120)); CHECK_AT=$((START + 8*3600 + 120)); VERDICT_AT=$((START + 24*3600 + 120))
mkdir -p "$ROOT/readings"
nohup bash -c "until [ \$(date +%s) -ge $SMOKE_AT ]; do sleep 60; done; cd $CODE && nice -n 5 python3 tools/verdict_g4.py --root $ROOT --genome $GENOME --out $ROOT/readings/smoke-2h --hours 2 --slice-hours 2 --regime-step 25 --workers 4 --unit creature-g5@$NAME.service; echo exit=\$?; python3 -c \"import json;print('backlog after the smoke:', json.load(open('$ROOT/STATUS.json')).get('mind_backlog_rows'))\"" > "$ROOT/readings/smoke-2h.log" 2>&1 &
echo "smoke waiter pid $! fires $(date -d @$SMOKE_AT '+%H:%M')"
nohup bash -c "until [ \$(date +%s) -ge $CHECK_AT ]; do sleep 60; done; cd $CODE && python3 tools/lives/check.py --root $ROOT --hours 8; echo exit=\$?" > "$ROOT/readings/check-8h.log" 2>&1 &
echo "check waiter pid $! fires $(date -d @$CHECK_AT '+%Y-%m-%d %H:%M')"
nohup bash -c "until [ \$(date +%s) -ge $VERDICT_AT ]; do sleep 60; done; cd $CODE && nice -n 5 python3 tools/verdict_g4.py --root $ROOT --genome $GENOME --out $ROOT/readings/verdict-24h --hours 24 --slice-hours 4 --regime-step 25 --workers 8 --unit creature-g5@$NAME.service; echo exit=\$?" > "$ROOT/readings/verdict-24h.log" 2>&1 &
echo "verdict waiter pid $! fires $(date -d @$VERDICT_AT '+%Y-%m-%d %H:%M')"
