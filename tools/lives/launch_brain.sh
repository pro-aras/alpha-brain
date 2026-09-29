#!/usr/bin/env bash
# edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:46 +0400 — BRAIN-IN-BODY §5 (docs/brain/body/INTERFACE-BRAIN-ORGAN.md):
# LAUNCH ONE brain-in-body life. Run by hand, step by step; every step prints what it did.
# usage: tools/lives/launch_brain.sh <name> <commit> <genome-rel-path>
#   e.g. tools/lives/launch_brain.sh brain-lean-pre 1a2b3c4 genome/brain/BRAIN-LEAN-PREFLIGHT.genome
# FILES ONLY: this script writes files and, at the very end, enables+starts the systemd instance. It is not
# run by the builder — the seat runs it, after the gates (INTERFACE §0/PREREG §7's own law, matched here from
# tools/lives/launch.sh's own precedent for the seam lives).
set -euo pipefail
NAME="${1:?life name}"; COMMIT="${2:?commit}"; GENOME_REL="${3:?genome rel path, e.g. genome/brain/BRAIN-LEAN.genome}"
BODY_ARGS="${4:-}"   # edit: Claude (Fable 5.1, the seat), 2026-09-28 21:10 +0400 — the life's extra body arguments (the full organism: "--folder /data/dev/genome/world --plant-after 15000"); empty for a lean life
# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:15 +0400 — the integration worktree genome-wt-organ is gone; the source is the repo this script lies in (every worktree shares one object store).
SOURCE_REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
LIVES=/data/dev/genome-lives; ROOT="$LIVES/$NAME"; CODE="$ROOT/code"

[ -e "$ROOT" ] && { echo "root exists: $ROOT — refusing (a life's root is never reused)"; exit 2; }
mkdir -p "$LIVES"

# 1. the life's OWN detached checkout at the commit (one code version per life — a closed tape replays under its own commit)
git -C "$SOURCE_REPO" worktree add --detach "$CODE" "$COMMIT"
echo "[launch_brain $NAME] checkout $CODE at $(git -C "$CODE" rev-parse --short HEAD)"
[ -f "$CODE/$GENOME_REL" ] || { echo "no $GENOME_REL at that commit — commit it first"; exit 3; }

# 2. units (templated) installed + daemon-reload; nothing enabled by the installer
bash "$CODE/deploy/install.sh" | tail -2

# 3. the root's record — written before the unit ever starts, so it is dated even if the start fails
mkdir -p "$ROOT"
date "+%Y-%m-%d %H:%M %z" > "$ROOT/STARTED-AT"
echo "$COMMIT" > "$ROOT/CODE-COMMIT"
printf "GENOME=%s\nBODY_ARGS=%s\n" "$CODE/$GENOME_REL" "$BODY_ARGS" > "$ROOT/unit.env"
cp "$CODE/$GENOME_REL" "$ROOT/GENOME.genome"

# 4. enable + start the life
systemctl --user enable --now "creature-brain@$NAME.service"
sleep 20
systemctl --user status "creature-brain@$NAME.service" --no-pager | sed -n 1,4p
echo "[launch_brain $NAME] STATUS after 20 s: $(python3 -c "import json;d=json.load(open('$ROOT/STATUS.json'));print({k:d[k] for k in ('moments','tape_rows','cells','crash','scene')})" 2>/dev/null || echo 'no STATUS yet')"
echo "[launch_brain $NAME] next: read the life's tape/journal against docs/brain/body/PREREG-BRAIN-IN-BODY.md's own gates"
