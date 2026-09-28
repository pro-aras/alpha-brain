#!/usr/bin/env bash
# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:10 +0400 — BRAIN-IN-BODY: ONE life under the real unit, from launch to close.
# usage: tools/lives/run_brain_life.sh <name> <commit> <genome-rel-path> [<max seconds> [<body args>]]
# Launches (tools/lives/launch_brain.sh), then reads the life's own STATUS every 10 s as a SERIES (never an endpoint: #236),
# and closes it (tools/lives/close_brain.sh: disable --now + STOPPED-AT, #240) when the world has ENDED and the mind has
# consumed every row of its tape — or when the unit is no longer active, or at the time limit. The verdict of the run
# (ENDED-CLEAN / UNIT-DIED / TIME-LIMIT) is written to <root>/RUN-VERDICT with the unit's own NRestarts and result.
set -uo pipefail
NAME="${1:?life name}"; COMMIT="${2:?commit}"; GENOME_REL="${3:?genome rel path}"; MAX="${4:-7200}"; BODY_ARGS="${5:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="/data/dev/genome-lives/$NAME"; UNIT="creature-brain@$NAME.service"
bash "$HERE/launch_brain.sh" "$NAME" "$COMMIT" "$GENOME_REL" "$BODY_ARGS" || { echo "[run $NAME] the launch failed"; exit 2; }
SERIES="$ROOT/SERIES.tsv"
printf "at\tuptime_load\tactive\ttape_seq\tmind_last_seq\tbacklog\tmoments\tcells\tscene_published\ttrain_done\tended\tbrain_learned\tasks_answered\tms_per_canvas_1min\trss_mb\tsense_restarts\tcrash\n" > "$SERIES"
T0=$(date +%s); VERDICT="TIME-LIMIT"; STABLE=0
while [ $(( $(date +%s) - T0 )) -lt "$MAX" ]; do
  ACTIVE=$(systemctl --user is-active "$UNIT" || true)
  LINE=$(/usr/bin/python3 - "$ROOT" <<'PYEOF'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
try:
    s = json.loads((root / "STATUS.json").read_text())
except Exception as e:
    print("\t".join(["?"] * 13) + f"\tno STATUS: {e!r}"); sys.exit(0)
seq = "?"
for p in (root / "tape" / "SEQ", root / "run" / "tape" / "SEQ"):
    if p.exists():
        seq = p.read_text().strip()
sc = s.get("scene") or {}
br = s.get("brain") or {}
print("\t".join(str(x) for x in (seq, s.get("last_seq"), s.get("mind_backlog_rows"), s.get("moments"), s.get("cells"),
                                 sc.get("published_moments"), sc.get("train_done"), sc.get("ended"),
                                 br.get("learned", br.get("learn_rows")), br.get("asks_answered"),
                                 s.get("mind_ms_per_canvas_1min"), s.get("rss_mb"), s.get("sense_restarts"), s.get("crash"))))
PYEOF
)
  printf "%s\t%s\t%s\t%s\n" "$(date '+%H:%M:%S')" "$(cut -d' ' -f1 /proc/loadavg)" "$ACTIVE" "$LINE" >> "$SERIES"
  if [ "$ACTIVE" != "active" ]; then VERDICT="UNIT-DIED ($ACTIVE)"; break; fi
  SEQ=$(echo "$LINE" | cut -f1); LAST=$(echo "$LINE" | cut -f2); BACK=$(echo "$LINE" | cut -f3); ENDED=$(echo "$LINE" | cut -f8)
  if [ "$ENDED" = "True" ] && [ "$BACK" = "0" ] && [ "$SEQ" = "$LAST" ]; then
    STABLE=$(( STABLE + 1 ))
    if [ "$STABLE" -ge 2 ]; then VERDICT="ENDED-CLEAN"; break; fi     # two readings in a row: the mind holds the tape's last row
  else
    STABLE=0
  fi
  sleep 10
done
systemctl --user show "$UNIT" -p NRestarts -p Result -p ExecMainStatus -p ActiveEnterTimestamp > "$ROOT/UNIT-SHOW-BEFORE-CLOSE.txt" 2>&1
bash "$HERE/close_brain.sh" "$NAME" > "$ROOT/CLOSE.log" 2>&1; CRC=$?
systemctl --user show "$UNIT" -p NRestarts -p Result -p ExecMainStatus -p ActiveExitTimestamp > "$ROOT/UNIT-SHOW-AFTER-CLOSE.txt" 2>&1
{ echo "$VERDICT"; echo "close exit $CRC"; echo "wall seconds $(( $(date +%s) - T0 ))"; cat "$ROOT/UNIT-SHOW-BEFORE-CLOSE.txt"; echo "--- after close"; cat "$ROOT/UNIT-SHOW-AFTER-CLOSE.txt"; } > "$ROOT/RUN-VERDICT"
echo "[run $NAME] $VERDICT"; cat "$ROOT/RUN-VERDICT"; echo "--- the series (first 3, last 5 of $(wc -l < "$SERIES") lines)"; head -4 "$SERIES"; tail -5 "$SERIES"; echo "--- close"; cat "$ROOT/CLOSE.log"
[ "$VERDICT" = "ENDED-CLEAN" ]
