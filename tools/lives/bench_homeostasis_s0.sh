#!/usr/bin/env bash
# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 — PREREG-HOMEOSTASIS §0(b) (DRAFT law,
# docs/organism/homeostasis/PREREG-HOMEOSTASIS.md): the CONTROLLED bench life for the §0 baseline table.
# A short life on PRODUCTION code, the pre-flight genome UNCHANGED (SEED 20261211, the declared toy shelf,
# REGISTERS armed — comparable with the pre-flight records), fenced 4G, run to ≥ 52,000 moments
# (≥ 10,000 canvases), closed clean, then read by tools/brain/homeostasis_s0.py into the law's records.
# NO kill/power-cut gates (the pre-flights proved those); §0 is a READING — it feeds the constants' choice.
# The gate's own runs get a fresh never-used seed at signature (the prereg §3 G) — §0's seed is declared
# and reused so no constant is fitted to the gate's world.
# usage: bench_homeostasis_s0.sh <commit>   (run as a transient unit; it posts START/DONE/FAIL to the board)
set -uo pipefail
COMMIT="${1:?commit}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME=brain-long-6-h0s0
ROOT=/data/dev/genome-lives/$NAME
UNIT="creature-brain@$NAME.service"
SHELF=/data/dev/brain-runs/alpha-6/bl5-preflight-toy/video-shelf
RECS=/data/dev/genome/docs/organism/homeostasis/records
LANE=kimi
fail() { /data/dev/swarm/bin/post "$LANE" FAIL <<X
H0-§0 BENCH FAIL: $* (life $NAME)
X
echo "BENCH FAIL: $*"; exit 1; }

[ -e "$ROOT" ] && fail "root exists: $ROOT (a bench life's root is never reused)"
/data/dev/swarm/bin/post "$LANE" START <<X
H0-§0 BENCH START: $NAME on $COMMIT — PREREG-HOMEOSTASIS §0(b): the controlled baseline reading (≥ 52,000 moments, fenced 4G, the toy shelf), then tools/brain/homeostasis_s0.py's table into the law's records. ETA ~2 h.
X

# 0 · the toy shelf verifies (the pre-flights' own fixture)
( cd "$HERE/../.." && PYTHONPATH=. python3 -B -m tools.worlds.video_shelf verify --shelf "$SHELF" ) || fail "the toy shelf's manifest does not verify"

# 1 · the launch, the standard machinery's own form
bash "$HERE/launch_long.sh" "$NAME" "$COMMIT" genome/brain/lives/BRAIN-LONG-6-PREFLIGHT.genome \
     "--folder /data/dev/genome/world --plant-after 15000 --eye-front" || fail "the launch"

# 2 · the small fence (the pre-flights' 4G form; daemon-reload applies it to the unit's cgroup)
DROP="${HOME}/.config/systemd/user/creature-brain@${NAME}.service.d"
cat > "$DROP/fence.conf" <<'FEOF'
# the §0 BENCH life's fence (PREREG-HOMEOSTASIS §0(b): fenced small like the pre-flights — 4G).
[Service]
MemoryHigh=4G
MemoryMax=4G
FEOF
systemctl --user daemon-reload
echo "[fence] 4G/4G written + daemon-reloaded"

# 3 · run to the §0 length, then close clean
T0=$(date +%s)
while :; do
  M=$(/usr/bin/python3 -c "import json;print(json.load(open('$ROOT/STATUS.json')).get('moments') or 0)" 2>/dev/null || echo 0)
  C=$(/usr/bin/python3 -c "import json;print(json.load(open('$ROOT/STATUS.json')).get('crash'))" 2>/dev/null || echo readfail)
  [ "$C" != "None" ] && [ "$C" != "readfail" ] && fail "a crash on STATUS: $C"
  [ "${M:-0}" -ge 52000 ] && break
  [ $(( $(date +%s) - T0 )) -gt 12600 ] && fail "3.5 h without 52,000 moments (moments=$M) — the box was busy or the life stalled"
  sleep 30
done
echo "[run] moments=$M reached at $(date '+%F %T %z')"
bash "$HERE/close_long.sh" "$NAME" || fail "the clean close"

# 4 · the §0 table into the law's records
mkdir -p "$RECS"
( cd "$HERE/../.." && PYTHONPATH=. python3 -B tools/brain/homeostasis_s0.py "$ROOT/journal" ) > "$RECS/s0-bench-$NAME.txt" 2>&1
RC=$?
[ $RC -eq 0 ] || fail "the reader's exit $RC (the table at $RECS/s0-bench-$NAME.txt)"
/data/dev/swarm/bin/post "$LANE" DONE <<X
H0-§0 BENCH DONE: $NAME closed clean at $M moments on $COMMIT; the §0(b) table committed next at docs/organism/homeostasis/records/s0-bench-$NAME.txt (the seat reads + commits it). The §0(a) live baselines are already in the prereg's §0.
X
echo "BENCH DONE: $NAME — the table at $RECS/s0-bench-$NAME.txt"
