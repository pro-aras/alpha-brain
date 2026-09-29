#!/usr/bin/env bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:14 +0400 — THE LONG LIFE: close it — the life AND its two timers are DISABLED (#240), never only stopped.
# usage: tools/lives/close_long.sh <name>
set -euo pipefail
NAME="${1:?life name}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:42 +0400 — + the health watch (a timer that outlived its life would restart nothing, but #240: nothing stays enabled)
systemctl --user disable --now "creature-g5-watch@$NAME.timer" "creature-brain-series@$NAME.timer" "creature-brain-health@$NAME.timer" 2>&1 | grep -v "not loaded" || true
bash "$HERE/close_brain.sh" "$NAME"
