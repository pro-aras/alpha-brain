#!/usr/bin/env bash
# Claude (Fable 5.1), 2026-09-21 — the two readers of a seam life, from the life's OWN checkout: a 2 h smoke (the reader's
# positive control on this cadence) and the 8 h verdict (--hours 8 --slice-hours 2 --regime-step 25).
set -u
NAME="${1:?life name}"; ROOT="/data/dev/genome-lives/$NAME"; CODE="$ROOT/code"
START=$(date -d "$(cat "$ROOT/STARTED-AT")" +%s); GENOME=$(sed -n "s/^GENOME=//p" "$ROOT/unit.env")
SMOKE_AT=$((START + 2*3600 + 120)); VERDICT_AT=$((START + 8*3600 + 120))
mkdir -p "$ROOT/readings"
nohup bash -c "until [ \$(date +%s) -ge $SMOKE_AT ]; do sleep 60; done; cd $CODE && nice -n 5 python3 tools/verdict_g4.py --root $ROOT --genome $GENOME --out $ROOT/readings/smoke-2h --hours 2 --slice-hours 2 --regime-step 25 --workers 6 --unit creature-g5@$NAME.service; echo exit=\$?" > "$ROOT/readings/smoke-2h.log" 2>&1 &
echo "smoke waiter pid $! fires $(date -d @$SMOKE_AT '+%H:%M')"
nohup bash -c "until [ \$(date +%s) -ge $VERDICT_AT ]; do sleep 60; done; cd $CODE && nice -n 5 python3 tools/verdict_g4.py --root $ROOT --genome $GENOME --out $ROOT/readings/verdict-8h --hours 8 --slice-hours 2 --regime-step 25 --workers 8 --unit creature-g5@$NAME.service; echo exit=\$?" > "$ROOT/readings/verdict-8h.log" 2>&1 &
echo "verdict waiter pid $! fires $(date -d @$VERDICT_AT '+%Y-%m-%d %H:%M')"
