#!/usr/bin/env bash
# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:30 +0400 — BRAIN-IN-BODY rung 3: ONE FULL-ORGANISM life under the real unit, launch to close.
# A separate file from run_brain_life.sh on purpose: that script was being run by a live chain when this was written, and a
# script is never edited under the shell that holds it (#241).
# usage: tools/lives/run_brain_life_full.sh <name> <commit> <genome-rel-path> <max seconds> "<body args>"
# The full organism's other worlds never stop publishing, so «the mind holds the tape's last row» is not its end. Its end:
# the scene world has ENDED and the mind has ANSWERED every ask row the tape carries (counted on the tape itself), read so
# twice in a row. STATUS is read every 10 s as a SERIES, with every organ's own counter beside the backlog.
set -uo pipefail
NAME="${1:?life name}"; COMMIT="${2:?commit}"; GENOME_REL="${3:?genome rel path}"; MAX="${4:?max seconds}"; BODY_ARGS="${5:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="/data/dev/genome-lives/$NAME"; UNIT="creature-brain@$NAME.service"
bash "$HERE/launch_brain.sh" "$NAME" "$COMMIT" "$GENOME_REL" "$BODY_ARGS" || { echo "[run $NAME] the launch failed"; exit 2; }
SERIES="$ROOT/SERIES.tsv"
printf "at\tload\tactive\tasks_on_tape\tasks_answered\tbacklog\tmoments\tcells\tscene_published\ttrain_done\tended\tbrain_learned\tms_per_canvas_1min\trss_mb\tsense_restarts\tcrash\tthinks\tsleeps\tepisodes\tsnapshots\tbirths\trows_by_sense\n" > "$SERIES"
T0=$(date +%s); VERDICT="TIME-LIMIT"; STABLE=0
while [ $(( $(date +%s) - T0 )) -lt "$MAX" ]; do
  ACTIVE=$(systemctl --user is-active "$UNIT" || true)
  LINE=$(/usr/bin/python3 - "$ROOT" <<'PYEOF'
import collections, json, sys
from pathlib import Path
root = Path(sys.argv[1])
try:
    s = json.loads((root / "STATUS.json").read_text())
except Exception as e:
    print("\t".join(["?"] * 18) + f"\tno STATUS: {e!r}"); sys.exit(0)
asks = 0
by = collections.Counter()
for d in (root / "tape", root / "run" / "tape"):
    for f in sorted(d.glob("*.jsonl")) if d.exists() else []:
        with f.open() as fh:
            for line in fh:
                i = line.find('"sense": "')
                if i >= 0:
                    sense = line[i + 10: line.find('"', i + 10)]
                    by[sense] += 1
                    asks += int(sense == "ask")
sc = s.get("scene") or {}
br = s.get("brain") or {}
print("\t".join(str(x) for x in (asks, br.get("asks_answered"), s.get("mind_backlog_rows"), s.get("moments"), s.get("cells"),
                                 sc.get("published_moments"), sc.get("train_done"), sc.get("ended"),
                                 br.get("learned", br.get("learn_rows")), s.get("mind_ms_per_canvas_1min"), s.get("rss_mb"),
                                 s.get("sense_restarts"), s.get("crash"), s.get("thinks"), s.get("sleeps"), s.get("episodes"),
                                 s.get("snapshots"), s.get("births"), json.dumps(dict(sorted(by.items()))))))
PYEOF
)
  printf "%s\t%s\t%s\t%s\n" "$(date '+%H:%M:%S')" "$(cut -d' ' -f1 /proc/loadavg)" "$ACTIVE" "$LINE" >> "$SERIES"
  if [ "$ACTIVE" != "active" ]; then VERDICT="UNIT-DIED ($ACTIVE)"; break; fi
  ASKS=$(echo "$LINE" | cut -f1); ANS=$(echo "$LINE" | cut -f2); ENDED=$(echo "$LINE" | cut -f8)
  if [ "$ENDED" = "True" ] && [ "$ASKS" != "0" ] && [ "$ASKS" = "$ANS" ]; then
    STABLE=$(( STABLE + 1 ))
    if [ "$STABLE" -ge 2 ]; then VERDICT="ENDED-CLEAN"; break; fi
  else
    STABLE=0
  fi
  sleep 10
done
systemctl --user show "$UNIT" -p NRestarts -p Result -p ExecMainStatus -p ActiveEnterTimestamp > "$ROOT/UNIT-SHOW-BEFORE-CLOSE.txt" 2>&1
bash "$HERE/close_brain.sh" "$NAME" > "$ROOT/CLOSE.log" 2>&1; CRC=$?
systemctl --user show "$UNIT" -p NRestarts -p Result -p ExecMainStatus > "$ROOT/UNIT-SHOW-AFTER-CLOSE.txt" 2>&1
{ echo "$VERDICT"; echo "close exit $CRC"; echo "wall seconds $(( $(date +%s) - T0 ))"; cat "$ROOT/UNIT-SHOW-BEFORE-CLOSE.txt"; echo "--- after close"; cat "$ROOT/UNIT-SHOW-AFTER-CLOSE.txt"; } > "$ROOT/RUN-VERDICT"
echo "[run $NAME] $VERDICT"; cat "$ROOT/RUN-VERDICT"; echo "--- the series (head, tail of $(wc -l < "$SERIES") lines)"; head -3 "$SERIES"; tail -4 "$SERIES"; echo "--- close"; cat "$ROOT/CLOSE.log"
[ "$VERDICT" = "ENDED-CLEAN" ]
