#!/usr/bin/env bash
# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-13 — PREREG-HOMEOSTASIS AMENDMENT 3 §A3-3
# (SIGNED 2026-10-13, SEAT-LINE-H0-A3.txt): the marks' POPULATION clause — G2, the SAME gate world's
# longer run (BRAIN-LONG-6-H0-GATE.genome unchanged: SEED 20261213, the declared fresh seed; the first
# 12,677 canvases replay G-ON's record deterministically inside it). THE STOPPING RULE, DECLARED BEFORE
# THE RUN (F5's own ceiling form): run to 30,000 canvases OR the 8-h wall, whichever first; then close
# clean. The boredom regime (b > 0.7, ~10,700 canvases in on the first run's trajectory) then holds a
# real share of the record for the boredom marks' signed ratios.
# usage: gate_homeostasis_g2.sh <commit>   (as a transient unit; posts START/DONE/FAIL to the board)
set -uo pipefail
COMMIT="${1:?commit}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME=brain-long-6-h0gate2
ROOT=/data/dev/genome-lives/$NAME
UNIT="creature-brain@$NAME.service"
SHELF=/data/dev/brain-runs/alpha-6/bl5-preflight-toy/video-shelf
LANE=kimi
WALL=$((8 * 3600))
fail() { /data/dev/swarm/bin/post "$LANE" FAIL <<X
H0 G2 FAIL: $* (life $NAME)
X
echo "G2 FAIL: $*"; exit 1; }

[ -e "$ROOT" ] && fail "root exists: $ROOT (a bench life's root is never reused)"
/data/dev/swarm/bin/post "$LANE" START <<X
H0 G2 START: $NAME on $COMMIT — AMENDMENT 3 §A3-3 (the marks' population clause): the SAME gate world to the declared ceiling (30,000 canvases / 8 h wall), fenced 4G. The first 12,677 canvases replay G-ON's record; the boredom regime then holds a real share of the tape.
X

( cd "$HERE/../.." && PYTHONPATH=. python3 -B -m tools.worlds.video_shelf verify --shelf "$SHELF" ) || fail "the toy shelf's manifest does not verify"
bash "$HERE/launch_long.sh" "$NAME" "$COMMIT" genome/brain/lives/BRAIN-LONG-6-H0-GATE.genome \
     "--folder /data/dev/genome/world --plant-after 15000 --eye-front" || fail "the launch"

DROP="${HOME}/.config/systemd/user/creature-brain@${NAME}.service.d"
cat > "$DROP/fence.conf" <<'FEOF'
# the H0 G2 life's fence (AMENDMENT 3 §A3-3: fenced small like G-ON — 4G).
[Service]
MemoryHigh=4G
MemoryMax=4G
FEOF
systemctl --user daemon-reload
echo "[fence] 4G/4G written + daemon-reloaded"

canvases_of () { /usr/bin/python3 -c "import json;print(json.load(open('$ROOT/state/ledger.json')).get('canvas_index') or 0)" 2>/dev/null || echo 0; }
T0=$(date +%s)
while :; do
  C=$(canvases_of)
  CRASH=$(/usr/bin/python3 -c "import json;print(json.load(open('$ROOT/STATUS.json')).get('crash'))" 2>/dev/null || echo readfail)
  [ "$CRASH" != "None" ] && [ "$CRASH" != "readfail" ] && fail "a crash on STATUS: $CRASH"
  ELAPSED=$(( $(date +%s) - T0 ))
  [ "${C:-0}" -ge 30000 ] && { echo "[stop] the 30,000-canvas ceiling (AMENDMENT 3 §A3-3)"; break; }
  [ "$ELAPSED" -gt "$WALL" ] && { echo "[stop] the 8-h wall at $C canvases (AMENDMENT 3 §A3-3's own second form)"; break; }
  sleep 60
done
echo "[run] canvases=$C at $(date '+%F %T %z') (elapsed ${ELAPSED}s)"
bash "$HERE/close_long.sh" "$NAME" || fail "the clean close"
/data/dev/swarm/bin/post "$LANE" DONE <<X
H0 G2 CLOSED: $NAME at $C canvases (elapsed ${ELAPSED}s) on $COMMIT — the tape feeds the arms' re-grade under AMENDMENT 3 (the re-formed marks + the per-canvas buckets). The seat reads + commits the records.
X
echo "G2 DONE: $NAME — $C canvases"
