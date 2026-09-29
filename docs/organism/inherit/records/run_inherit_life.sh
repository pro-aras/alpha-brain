#!/usr/bin/env bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:4x +0400 — PREREG-INHERIT §4: ONE lean life, launch to grade, no seat needed.
# usage: run_inherit_life.sh <name> <genome file> <max seconds> [<parent root>]
# The unit is STARTED, never enabled: a short graded life is not resurrected by a reboot (#240).
set -uo pipefail
NAME="${1:?}"; GENOME_SRC="${2:?}"; MAX="${3:?}"; PARENT="${4:-}"
COMMIT=bb44d3a; SRC=/data/dev/genome-wt-inherit
ROOT=/data/dev/genome-lives/$NAME; UNIT="creature-brain@$NAME.service"
[ -e "$ROOT" ] && { echo "root exists: $ROOT"; exit 2; }
mkdir -p "$ROOT"
git -C "$SRC" worktree add --detach "$ROOT/code" "$COMMIT" >/dev/null 2>&1 || { echo "checkout failed"; exit 3; }
cp "$GENOME_SRC" "$ROOT/GENOME.genome"
date "+%Y-%m-%d %H:%M %z" > "$ROOT/STARTED-AT"; echo "$COMMIT" > "$ROOT/CODE-COMMIT"
printf "GENOME=%s\nBODY_ARGS=\n" "$ROOT/GENOME.genome" > "$ROOT/unit.env"
if [ -n "$PARENT" ]; then
  mkdir "$ROOT/inherit"
  cp "$PARENT/state/brain.json" "$PARENT/state/brain.npz" "$ROOT/inherit/" || { echo "the parent's pair is not whole"; exit 4; }
  /usr/bin/python3 -c "
import json,sys
m=json.load(open('$ROOT/inherit/brain.json'))
print(json.dumps({'parent_root':'$PARENT','learned':len(m['brain']['moments']),'hash':m['state_hash'],'cfg':m['cfg']},sort_keys=True))" > "$ROOT/inherit/INHERITED-FROM"
fi
systemctl --user start "$UNIT" || { echo "start failed"; exit 5; }
T0=$(date +%s); VERDICT="TIME-LIMIT"; STABLE=0
while [ $(( $(date +%s) - T0 )) -lt "$MAX" ]; do
  /usr/bin/python3 -c "import time; time.sleep(10)"
  A=$(systemctl --user is-active "$UNIT" || true)
  if [ "$A" != "active" ]; then VERDICT="UNIT-DIED ($A)"; break; fi
  S=$(/usr/bin/python3 -c "
import json
try:
    s=json.load(open('$ROOT/STATUS.json')); b=s.get('brain') or {}; sc=s.get('scene') or {}
    print('DONE' if (sc.get('ended') and b.get('asks_pending')==0 and (b.get('asks_answered') or 0)>0 and (s.get('mind_backlog_rows') or 0)==0) else 'RUN')
except Exception: print('RUN')")
  if [ "$S" = "DONE" ]; then STABLE=$((STABLE+1)); [ "$STABLE" -ge 2 ] && { VERDICT="ENDED-CLEAN"; break; }; else STABLE=0; fi
done
cp "$ROOT/STATUS.json" "$ROOT/STATUS-BEFORE-STOP.json" 2>/dev/null
systemctl --user show "$UNIT" -p NRestarts -p Result > "$ROOT/UNIT-SHOW-BEFORE-CLOSE.txt" 2>&1
systemctl --user stop "$UNIT"; SRC_RC=$?
date "+%Y-%m-%d %H:%M %z" > "$ROOT/STOPPED-AT"
{ echo "$VERDICT"; echo "stop exit $SRC_RC"; echo "wall seconds $(( $(date +%s) - T0 ))"; cat "$ROOT/UNIT-SHOW-BEFORE-CLOSE.txt"; } > "$ROOT/RUN-VERDICT"
mkdir -p "$ROOT/grade"
( cd "$ROOT/code" && OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$ROOT/code" /usr/bin/python3 -B tools/brain/grade_life.py --root "$ROOT" --out "$ROOT/grade" --label brain > "$ROOT/grade/grade.log" 2>&1 ); echo "grade exit $?" >> "$ROOT/RUN-VERDICT"
cat "$ROOT/RUN-VERDICT"
[ "$VERDICT" = "ENDED-CLEAN" ]
