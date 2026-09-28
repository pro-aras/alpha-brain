#!/usr/bin/env bash
# edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:47 +0400 — BRAIN-IN-BODY §5. CLOSE ONE brain-in-body life.
# usage: tools/lives/close_brain.sh <name>
# Disables (never only stops — SOLUTIONS #240: an update reboot restarted every closed-but-still-enabled life)
# and writes STOPPED-AT so a later restart is refused (creature/body.py:closed_marker). Not run by the
# builder — the seat runs it.
set -euo pipefail
NAME="${1:?life name}"
LIVES=/data/dev/genome-lives; ROOT="$LIVES/$NAME"

systemctl --user disable --now "creature-brain@$NAME.service"
date "+%Y-%m-%d %H:%M %z" > "$ROOT/STOPPED-AT"
echo "[close_brain $NAME] STOPPED-AT $(cat "$ROOT/STOPPED-AT")"

echo "[close_brain $NAME] is-enabled: $(systemctl --user is-enabled "creature-brain@$NAME.service" || true)"
echo "[close_brain $NAME] is-active:  $(systemctl --user is-active "creature-brain@$NAME.service" || true)"
echo "[close_brain $NAME] default.target.wants:"
ls "${HOME}/.config/systemd/user/default.target.wants" 2>&1
