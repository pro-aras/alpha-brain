#!/usr/bin/env bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:14 +0400 — THE LONG LIFE: launch ONE brain life that must need no seat for days.
# usage: tools/lives/launch_long.sh <name> <commit> <genome-rel-path> "<body args>"
# = the memory fence (a drop-in for this instance, written BEFORE the start) + tools/lives/launch_brain.sh (files, enable --now)
#   + the watch timer (pages when the counters stop moving) + the series timer (one SERIES.tsv line every 5 min).
# It never closes the life: tools/lives/close_long.sh does (disable --now on the life AND its two timers, #240).
set -euo pipefail
NAME="${1:?life name}"; COMMIT="${2:?commit}"; GENOME_REL="${3:?genome rel path}"; BODY_ARGS="${4:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DROP="${HOME}/.config/systemd/user/creature-brain@${NAME}.service.d"
mkdir -p "$DROP"
cat > "$DROP/fence.conf" <<'FEOF'
# the long life's memory fence: the box has 30 GB; GROW is unbounded. At MemoryHigh the kernel reclaims and slows the life;
# at MemoryMax it is killed and the unit restarts it from its last snapshot (Restart=on-failure).
[Service]
MemoryHigh=16G
MemoryMax=20G
FEOF
echo "[launch_long $NAME] fence: $(grep -c Memory "$DROP/fence.conf") lines in $DROP/fence.conf"
bash "$HERE/launch_brain.sh" "$NAME" "$COMMIT" "$GENOME_REL" "$BODY_ARGS"
systemctl --user enable --now "creature-g5-watch@$NAME.timer" "creature-brain-series@$NAME.timer"
systemctl --user show "creature-brain@$NAME.service" -p MemoryHigh -p MemoryMax -p ActiveState
systemctl --user list-timers --no-pager | grep -F "$NAME" || true
