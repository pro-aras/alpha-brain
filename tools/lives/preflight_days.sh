#!/usr/bin/env bash
# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:47 +0400 — his 23:20 word: the days life's PRE-FLIGHT. A short life of the days genome under the
# real units, and the three failures a few days alone can bring: (1) a hard kill mid-training; (2) a POWER CUT (the process killed with no
# snapshot, zero-filled tails appended to the tape, the journal and beliefs, the SEQ emptied) — it must come back by itself, repair and go
# on with no seq used twice; (3) killed until systemd gives up (the unit FAILED) — the health watch must bring it back. Every step prints
# what it saw; the verdict is the last line (PREFLIGHT PASS or PREFLIGHT FAIL: <why>).
# usage: tools/lives/preflight_days.sh <name> <commit> <genome rel path>
set -uo pipefail
NAME="${1:?}"; COMMIT="${2:?}"; GENOME_REL="${3:?}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT=/data/dev/genome-lives/$NAME; UNIT="creature-brain@$NAME.service"
fail() { echo "PREFLIGHT FAIL: $*"; exit 1; }
st() { /usr/bin/python3 -c "
import json,sys
try: s=json.load(open('$ROOT/STATUS.json'))
except Exception as e: print('none'); sys.exit()
b=s.get('brain') or {}
print(json.dumps({'hb':s.get('heartbeat_at'),'last_seq':s.get('last_seq'),'moments':s.get('moments'),'learned':b.get('learned'),'restored':b.get('restored'),
 'web':{k:v.get('nodes') for k,v in (b.get('web') or {}).items()},'web_error':b.get('web_error'),'web_restored':b.get('web_restored'),
 'self':b.get('self',{}).get('claims') if b.get('self') else None,'hash':s.get('hash_form'),'crash':s.get('crash')}))"; }
wait_learned() { local want=$1 t0=$(date +%s); while [ $(( $(date +%s) - t0 )) -lt 600 ]; do
  L=$(/usr/bin/python3 -c "import json;print((json.load(open('$ROOT/STATUS.json')).get('brain') or {}).get('learned') or 0)" 2>/dev/null || echo 0)
  [ "${L:-0}" -ge "$want" ] && return 0; /usr/bin/python3 -c "import time; time.sleep(5)"; done; return 1; }
pid() { systemctl --user show "$UNIT" -p MainPID --value; }

bash "$HERE/launch_long.sh" "$NAME" "$COMMIT" "$GENOME_REL" "--folder /data/dev/genome/world --plant-after 15000" || fail "the launch"
wait_learned 120 || fail "no 120 scenes learned in 10 minutes"
echo "[1] alive: $(st)"
S1=$(st); echo "$S1" | grep -q '"web": {"L"' || fail "no web on STATUS: $S1"
echo "$S1" | grep -q '"hash": "sparse' || echo "$S1" | grep -q 'sparse' || fail "the row hash is not sparse: $S1"

# (1) a hard kill mid-training
P=$(pid); kill -9 "$P"; /usr/bin/python3 -c "import time; time.sleep(40)"
[ "$(systemctl --user is-active "$UNIT")" = active ] || fail "not back after a hard kill"
echo "[2] after a hard kill: $(st)"
st | grep -q '"web_restored": true' || fail "the web was not restored after the kill"

# (2) a POWER CUT: no snapshot, torn tails, an emptied SEQ, all within the 5 s before systemd restarts it
TOP=$(/usr/bin/python3 -c "
import json,glob
m=0
for f in sorted(glob.glob('$ROOT/tape/*.jsonl')):
    for l in open(f,'rb'):
        try: m=max(m,json.loads(l)['seq'])
        except Exception: pass
print(m)")
P=$(pid); kill -9 "$P"
DAY=$(ls "$ROOT"/tape/*.jsonl | tail -1); JD=$(ls "$ROOT"/journal/*.jsonl | tail -1)
/usr/bin/python3 - "$DAY" "$JD" "$ROOT/state/beliefs.jsonl" "$ROOT/tape/SEQ" <<'PYEOF'
import sys, os
day, jd, bel, seq = sys.argv[1:5]
for p, junk in ((day, b"\x00" * 4096), (jd, b'{"kind": "brain", "act": "le'), (bel, b"\x00" * 100)):
    if os.path.exists(p):
        with open(p, "ab") as f:
            f.write(junk)
open(seq, "wb").close()
print("the cut: tails torn, SEQ emptied")
PYEOF
/usr/bin/python3 -c "import time; time.sleep(45)"
[ "$(systemctl --user is-active "$UNIT")" = active ] || fail "not back after the power cut: $(systemctl --user show "$UNIT" -p Result -p NRestarts)"
echo "[3] after the power cut: $(st)"
[ -s "$ROOT/repairs/REPAIRS.jsonl" ] || fail "no repair recorded"
echo "[3] repairs: $(wc -l < "$ROOT/repairs/REPAIRS.jsonl") rows: $(cut -c1-160 "$ROOT/repairs/REPAIRS.jsonl" | tr '\n' ' ')"
/usr/bin/python3 -c "import time; time.sleep(20)"
/usr/bin/python3 - "$ROOT" "$TOP" <<'PYEOF' || fail "the tape after the cut"
import json, glob, sys
root, top = sys.argv[1], int(sys.argv[2])
seqs = []
for f in sorted(glob.glob(root + "/tape/*.jsonl")):
    for l in open(f, "rb"):
        seqs.append(json.loads(l)["seq"])
assert len(seqs) == len(set(seqs)), "a seq used twice"
assert max(seqs) > top, f"no new row after the cut ({max(seqs)} <= {top})"
print(f"[3] the tape: {len(seqs)} rows, no seq twice, max {max(seqs)} > {top} before the cut")
PYEOF

# (3) killed until systemd gives up; the health watch must bring it back
for i in 1 2 3 4 5 6 7; do P=$(pid); [ -n "$P" ] && [ "$P" != 0 ] && kill -9 "$P" 2>/dev/null; /usr/bin/python3 -c "import time; time.sleep(8)"; done
echo "[4] after 7 kills: $(systemctl --user show "$UNIT" -p ActiveState -p Result -p NRestarts | tr '\n' ' ')"
[ "$(systemctl --user is-active "$UNIT")" = failed ] || echo "[4] note: the unit did not reach FAILED (it is $(systemctl --user is-active "$UNIT"))"
systemctl --user start "creature-brain-health@$NAME.service"
/usr/bin/python3 -c "import time; time.sleep(30)"
[ "$(systemctl --user is-active "$UNIT")" = active ] || fail "the health watch did not bring it back: $(tail -2 "$ROOT/RECOVERY.log" 2>/dev/null)"
echo "[4] the watch acted: $(tail -1 "$ROOT/RECOVERY.log" 2>/dev/null | cut -c1-240)"
echo "[4] HEALTH.md: $(head -6 "$ROOT/HEALTH.md" | tr '\n' ' ' | cut -c1-400)"
wait_learned 400 || fail "the training did not finish after the tests"
echo "[5] end: $(st)"
echo "PREFLIGHT PASS"
