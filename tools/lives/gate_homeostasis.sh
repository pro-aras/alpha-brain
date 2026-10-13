#!/usr/bin/env bash
# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-13 — PREREG-HOMEOSTASIS §3 G + AMENDMENT 2
# F5/F8 (the law SIGNED 2026-10-12; AMENDMENTS 1-2 signed): THE GATE LIFE G-ON — the §0(b) bench form
# WHOLE (the declared toy shelf, scene seed 20261211) + the fresh never-used life SEED 20261213 (the
# never-used grep printed in the gate record) + the ONE line HOMEOSTASIS arousal boredom fatigue,
# fenced 4G. THE F5 STOPPING RULE (declared BEFORE the run): ≥ 10,000 canvases AND then extend toward
# H-SEEK-LEARN's population — until (one seek fired AND 1,000 post-seek canvases are banked) or the
# ceiling (30,000 canvases / 8 h wall), whichever first. Then close clean; the arm replays ride its tape.
# usage: gate_homeostasis.sh <commit>   (as a transient unit; posts START/DONE/FAIL to the board)
set -uo pipefail
COMMIT="${1:?commit}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME=brain-long-6-h0gate
ROOT=/data/dev/genome-lives/$NAME
UNIT="creature-brain@$NAME.service"
SHELF=/data/dev/brain-runs/alpha-6/bl5-preflight-toy/video-shelf
LANE=kimi
WALL=$((8 * 3600))
fail() { /data/dev/swarm/bin/post "$LANE" FAIL <<X
H0 GATE LIFE FAIL: $* (life $NAME)
X
echo "GATE-LIFE FAIL: $*"; exit 1; }

[ -e "$ROOT" ] && fail "root exists: $ROOT (a bench life's root is never reused)"
/data/dev/swarm/bin/post "$LANE" START <<X
H0 GATE LIFE START: $NAME on $COMMIT — PREREG-HOMEOSTASIS §3 G + AMENDMENT 2 F5/F8: the gate life with the drives LIVE (SEED 20261213, fresh; scene 20261211; the toy shelf), fenced 4G; the F5 stopping rule (≥10k canvases, extend to a seek + 1,000 post-seek canvases, ceiling 30k canvases / 8 h). Its tape feeds the arm replays.
X

# 0 · the toy shelf verifies (the bench fixture, the §0 form)
( cd "$HERE/../.." && PYTHONPATH=. python3 -B -m tools.worlds.video_shelf verify --shelf "$SHELF" ) || fail "the toy shelf's manifest does not verify"

# 1 · the launch, the standard machinery's own form
bash "$HERE/launch_long.sh" "$NAME" "$COMMIT" genome/brain/lives/BRAIN-LONG-6-H0-GATE.genome \
     "--folder /data/dev/genome/world --plant-after 15000 --eye-front" || fail "the launch"

# 2 · the small fence (the §0 bench's 4G form)
DROP="${HOME}/.config/systemd/user/creature-brain@${NAME}.service.d"
cat > "$DROP/fence.conf" <<'FEOF'
# the H0 GATE life's fence (AMENDMENT 2 F8: fenced small like the §0 bench — 4G).
[Service]
MemoryHigh=4G
MemoryMax=4G
FEOF
systemctl --user daemon-reload
echo "[fence] 4G/4G written + daemon-reloaded"

# 3 · the F5 stopping rule (declared before the run): ≥10k canvases, then the seek extension
canvases_of () { /usr/bin/python3 -c "import json;print(json.load(open('$ROOT/state/ledger.json')).get('canvas_index') or 0)" 2>/dev/null || echo 0; }
seek_canvas_of () { grep -a '"seek"' "$ROOT"/journal/*.jsonl 2>/dev/null | tail -1 | /usr/bin/python3 -c "import json,sys; s=sys.stdin.read().strip(); print(json.loads(s)['seek']['canvas'] if s else -1)" 2>/dev/null || echo -1; }
T0=$(date +%s)
while :; do
  C=$(canvases_of)
  CRASH=$(/usr/bin/python3 -c "import json;print(json.load(open('$ROOT/STATUS.json')).get('crash'))" 2>/dev/null || echo readfail)
  [ "$CRASH" != "None" ] && [ "$CRASH" != "readfail" ] && fail "a crash on STATUS: $CRASH"
  SC=$(seek_canvas_of)
  ELAPSED=$(( $(date +%s) - T0 ))
  if [ "${C:-0}" -ge 10000 ]; then
    if [ "$SC" -ge 0 ] && [ $(( C - SC )) -ge 1000 ]; then echo "[stop] the seek population is banked (seek at $SC, now $C)"; break; fi
    if [ "${C:-0}" -ge 30000 ]; then echo "[stop] the canvas ceiling (30,000) — the seek clause reads VACUOUS if none fired (seeks: $SC)"; break; fi
    if [ "$ELAPSED" -gt "$WALL" ]; then echo "[stop] the wall ceiling (8 h) at $C canvases (seeks: $SC)"; break; fi
  fi
  [ "$ELAPSED" -gt "$WALL" ] && [ "${C:-0}" -lt 10000 ] && fail "8 h without 10,000 canvases (at $C) — the box was busy or the life stalled"
  sleep 60
done
echo "[run] canvases=$C seek_canvas=$SC at $(date '+%F %T %z')"
bash "$HERE/close_long.sh" "$NAME" || fail "the clean close"

/data/dev/swarm/bin/post "$LANE" DONE <<X
H0 GATE LIFE CLOSED: $NAME at $C canvases (the seek's last canvas: $SC) on $COMMIT — the tape is closed; the arm replays + the identity legs + the self-exam ride it next. The seat reads + commits the records.
X
echo "GATE-LIFE DONE: $NAME — $C canvases, seek at $SC"
