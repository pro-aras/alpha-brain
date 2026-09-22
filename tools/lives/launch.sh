#!/usr/bin/env bash
# Claude (Fable 5.1), 2026-09-21 — LAUNCH ONE 8 h SEAM LIFE (docs/G5-SEAM-LIFE-PLAN.md §0/§2). Run by hand, step by step;
# every step prints what it did. usage: scratch/launch-seam-life.sh <name> <commit>     (e.g. g5-seam-1 <sha>)
set -euo pipefail
NAME="${1:?life name}"; COMMIT="${2:?commit}"; GENOME_REL="${3:-genome/G5.genome}"; PLANT_AFTER="${4:-5000}"   # edit: Claude (Fable 5.1), 2026-09-22 18:24 +0400 — 4th arg: the plant's canvas (15000 for the 24 h ONE life)
LIVES=/data/dev/genome-lives; ROOT="$LIVES/$NAME"; CODE="$ROOT/code"
[ -e "$ROOT" ] && { echo "root exists: $ROOT — refusing (a life's root is never reused)"; exit 2; }
mkdir -p "$LIVES"
# 1. the life's OWN detached checkout at the commit (one code version per life)
git -C /data/dev/genome-wt-q worktree add --detach "$CODE" "$COMMIT"
echo "[launch $NAME] checkout $CODE at $(git -C "$CODE" rev-parse --short HEAD)"
[ -f "$CODE/$GENOME_REL" ] || { echo "no $GENOME_REL at that commit — commit it first"; exit 3; }
# 2. units (templated) installed + daemon-reload; nothing enabled by the installer
bash "$CODE/deploy/install.sh" | tail -2
# 3. the root exists (the body creates it; make it now so the record is dated)
mkdir -p "$ROOT"; date "+%Y-%m-%d %H:%M %z" > "$ROOT/STARTED-AT"; echo "$COMMIT" > "$ROOT/CODE-COMMIT"; printf "GENOME=%s\nPLANT_AFTER=%s\n" "$CODE/$GENOME_REL" "$PLANT_AFTER" > "$ROOT/unit.env"; cp "$CODE/$GENOME_REL" "$ROOT/GENOME.genome"
# 4. enable + start the life and its watch
systemctl --user enable --now "creature-g5@$NAME.service"
systemctl --user enable --now "creature-g5-watch@$NAME.timer"
sleep 20
systemctl --user status "creature-g5@$NAME.service" --no-pager | sed -n 1,4p
echo "[launch $NAME] STATUS after 20 s: $(python3 -c "import json;d=json.load(open('$ROOT/STATUS.json'));print({k:d[k] for k in ('moments','tape_rows','cells','crash')})" 2>/dev/null || echo 'no STATUS yet')"
echo "[launch $NAME] next: the 2 h smoke waiter and the 8 h verdict waiter (scratch/waiters-seam-life.sh $NAME)"
