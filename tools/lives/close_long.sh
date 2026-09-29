#!/usr/bin/env bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:14 +0400 — THE LONG LIFE: close it — the life AND its two timers are DISABLED (#240), never only stopped.
# usage: tools/lives/close_long.sh <name>
set -euo pipefail
NAME="${1:?life name}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
systemctl --user disable --now "creature-g5-watch@$NAME.timer" "creature-brain-series@$NAME.timer"
bash "$HERE/close_brain.sh" "$NAME"
