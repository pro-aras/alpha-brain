#!/usr/bin/env bash
# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-09 04:36 +0400 — PREREG-ALPHA-6 §2 B5 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…; the seat's authority delegated to this lane for the pre-flights — the law §2 B5's
# own words): the TWO short pre-flight lives of brain-long-5 on the DECLARED TOY SHELF
# (/data/dev/brain-runs/alpha-6/bl5-preflight-toy/video-shelf — the law's own tiny fixtures, NEVER the real
# shelf), both with the front wired (--eye-front) and the mouth clause declared (BRAIN-LONG-5-PREFLIGHT.genome):
#   pre-1: a hard KILL → the resume restores (STATUS brain.restored True) — the gate's own bar;
#   pre-2: the POWER-CUT form (preflight_days.sh's corruption: torn tails + the SEQ emptied in the restart gap)
#          healed (repairs/REPAIRS.jsonl, no seq used twice), then the life CLOSES CLEAN (close_long.sh).
# The standard launch machinery is launch_long.sh (the fence + the units + the timers); the law §6 fences the
# pre-flights SMALL (4G): this driver rewrites the drop-in to MemoryHigh/MemoryMax 4G right after the launch and
# daemon-reloads — the kill's own restart brings the 4G fence live, so pre-1's restored gate is uncontaminated
# (no resume before the kill). The 16G/20G ceiling that launch_long.sh writes stands only for the seconds
# between the launch and this rewrite; the pre-flight's RSS is read against the DECLARED 4G from the start (S2).
# usage: preflight_alpha6.sh <brain-long-5-pre-1|brain-long-5-pre-2> <commit>
set -uo pipefail
NAME="${1:?life name (brain-long-5-pre-1 or -pre-2)}"; COMMIT="${2:?commit}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT=/data/dev/genome-lives/$NAME; UNIT="creature-brain@$NAME.service"
SHELF=/data/dev/brain-runs/alpha-6/bl5-preflight-toy/video-shelf
MODE=kill; [ "$NAME" = "brain-long-5-pre-2" ] && MODE=powercut
fail() { echo "PREFLIGHT FAIL: $*"; exit 1; }

st() { /usr/bin/python3 -c "
import json,sys
try: s=json.load(open('$ROOT/STATUS.json'))
except Exception: print('none'); sys.exit()
b=s.get('brain') or {}
print(json.dumps({'moments':s.get('moments'),'last_seq':s.get('last_seq'),'learned':b.get('learned'),
 'restored':b.get('restored'),'calibrations':b.get('calibrations'),'video':s.get('video'),'crash':s.get('crash'),
 'turns':b.get('turns')}))"; }
wait_learned() { local want=$1 t0=$(date +%s); while [ $(( $(date +%s) - t0 )) -lt 1500 ]; do
  L=$(/usr/bin/python3 -c "import json;print((json.load(open('$ROOT/STATUS.json')).get('brain') or {}).get('learned') or 0)" 2>/dev/null || echo 0)
  [ "${L:-0}" -ge "$want" ] && return 0; sleep 5; done; return 1; }
pid() { systemctl --user show "$UNIT" -p MainPID --value; }
rss_mb() { /usr/bin/python3 -c "import json;print(json.load(open('$ROOT/STATUS.json')).get('rss_mb') or 0)" 2>/dev/null || echo 0; }

# 0 · the declared toy shelf must exist, frozen and verified, before any life is born
[ -f "$SHELF/MANIFEST.sha256" ] || fail "no toy shelf at $SHELF (scratch/a6/make_toy_shelf.py builds it)"
( cd "$HERE/../.." && PYTHONPATH=. python3 -B -m tools.worlds.video_shelf verify --shelf "$SHELF" ) || fail "the toy shelf's manifest does not verify"

# 1 · the launch, the standard machinery's own form (+ the front wired — the law §1.5's pass-through)
bash "$HERE/launch_long.sh" "$NAME" "$COMMIT" genome/brain/lives/BRAIN-LONG-5-PREFLIGHT.genome \
     "--folder /data/dev/genome/world --plant-after 15000 --eye-front" || fail "the launch"

# 2 · the pre-flight fence (the law §6: fenced small, 4G) — in place before the kill's restart
DROP="${HOME}/.config/systemd/user/creature-brain@${NAME}.service.d"
cat > "$DROP/fence.conf" <<'FEOF'
# the PRE-FLIGHT's fence (PREREG-ALPHA-6 §6: fenced small, 4G — not the long life's 16G/20G): S2 stops the flight
# if the life's RSS crosses it. Written by preflight_alpha6.sh over launch_long.sh's own drop-in.
[Service]
MemoryHigh=4G
MemoryMax=4G
FEOF
systemctl --user daemon-reload
echo "[fence] $(grep -c Memory "$DROP/fence.conf") lines, 4G/4G, daemon-reloaded (live at the unit's next start)"

# 3 · the healthy birth: the first calibration, the video rows flowing, the front on, the voice rows on
wait_learned 250 || fail "no 250 learned in 25 minutes: $(st)"
echo "[1] alive past the first calibration: $(st)"
st | grep -q '"crash": null' || fail "a crash on STATUS: $(st)"
st | grep -q '"restored": null' || fail "restored is not None at birth: $(st)"
st | grep -q '"calibrations": 0' && fail "no calibration on STATUS: $(st)"
# the say-answer reading, bounded (the sitting's speak split lands ~minutes after the first calibration on this
# full organism; the flight's price is the law's ≤1 h): 10 minutes for the first one, then EVERY existing say
# answer must carry the mechanism's own keys. None yet: named honestly — the row-level live form reads on the
# launch's first day (M-MOUTH's own wall, 6 h); the clause's presence is already proven below by the voice rows.
SNOW=$(date +%s); while [ $(( $(date +%s) - SNOW )) -lt 600 ]; do
  N=$(/usr/bin/python3 -c "
import json,glob
n=0
for f in sorted(glob.glob('$ROOT/journal/*.jsonl')):
    for l in open(f):
        try: r=json.loads(l)
        except Exception: continue
        if r.get('kind')=='answer' and r.get('form')=='say': n+=1
print(n)" 2>/dev/null || echo 0)
  [ "${N:-0}" -ge 1 ] && break; sleep 10; done
/usr/bin/python3 - "$ROOT" "$SHELF" <<'PYEOF' || fail "the video world / the front / the mouth, live"
import json, sys
from pathlib import Path
root, shelf = Path(sys.argv[1]), Path(sys.argv[2])
rows = []
for f in sorted((root / "tape").glob("*.jsonl")):
    rows.extend(json.loads(l) for l in open(f) if l.strip())
veye = [r for r in rows if r["sense"] == "eye" and r["meta"].get("source") == "video"]
vear = [r for r in rows if r["sense"] == "ear" and r["meta"].get("source") == "video-caption"]
assert len(veye) >= 2 and len(vear) >= 1, f"the video world is not flowing: eye {len(veye)} ear {len(vear)}"
# provenance + payload UNTOUCHED: the life's first video rows are the shelf's own rows, field for field, byte
# for byte (the video/single-video converter tape carries no concat `video` key — untouched means EQUAL to the
# shelf's own meta, whatever it carries).
shelf_rows = []
for f in sorted(shelf.glob("*.jsonl")):
    shelf_rows.extend(json.loads(l) for l in open(f) if l.strip())
life_v = [r for r in rows if r["meta"].get("source") in ("video", "video-caption")]
for i in range(min(len(life_v), 40)):
    s, l = shelf_rows[i], life_v[i]
    assert l["sense"] == s["sense"] and l["meta"] == s["meta"], f"row {i}: the meta moved: {l['meta']} != {s['meta']}"
    assert (root / "tape" / l["payload"]).read_bytes() == (shelf / s["payload"]).read_bytes(), f"row {i}: the payload moved"
J = []
for f in sorted((root / "journal").glob("*.jsonl")):
    J.extend(json.loads(l) for l in open(f) if l.strip())
canvas = [r for r in J if "cells" in r and "err" in r]
fronted = [r for r in canvas if "front" in r]
assert len(canvas) > 50 and len(fronted) == len(canvas), f"the front key: {len(fronted)}/{len(canvas)} canvas rows"
voice = [r for r in J if r.get("kind") == "brain" and r.get("act") == "voice"]
assert len(voice) >= 1, "no voice row — the W1 mouth is silent past the calibration (the clause's life)"
says = [r for r in J if r.get("kind") == "answer" and r.get("form") == "say" and isinstance(r.get("answer"), dict)]
inc = [r for r in says if "n_readbacks" in (r["answer"].get("raw") or {})]
assert len(inc) == len(says), f"a say answer without the mechanism's own keys: {len(inc)}/{len(says)}"
print(f"[1] video rows eye {len(veye)} ear {len(vear)} · the first {min(len(life_v), 40)} video rows == the shelf's own, metas and payload bytes · "
      f"front {len(fronted)}/{len(canvas)} canvas rows · voice rows {len(voice)} · say answers with n_readbacks {len(inc)}/{len(says)}")
if not says:
    print("[1] NAMED: no say answer inside the flight's ≤1 h price — the row-level live form reads on the "
          "launch's first day (M-MOUTH's own wall); the clause is proven here by the voice rows and the bench")
PYEOF
R=$(rss_mb); echo "[1] RSS ${R} MB against the DECLARED 4G fence (S2)"
[ "$(/usr/bin/python3 -c "print(1 if float('$R') < 4096 else 0)")" = 1 ] || fail "S2: RSS $R MB past the fence"

# 4 · the gate itself
if [ "$MODE" = kill ]; then
  P=$(pid); [ -n "$P" ] && kill -9 "$P"; sleep 40
  [ "$(systemctl --user is-active "$UNIT")" = active ] || fail "not back after the hard kill"
  sleep 20
  S=$(st); echo "[2] after the hard kill: $S"
  echo "$S" | grep -q '"restored": true' || fail "the resume did not restore: $S"
  echo "$S" | grep -q '"crash": null' || fail "a crash after the resume: $S"
else
  TOP=$(/usr/bin/python3 -c "
import json,glob
m=0
for f in sorted(glob.glob('$ROOT/tape/*.jsonl')):
    for l in open(f,'rb'):
        try: m=max(m,json.loads(l)['seq'])
        except Exception: pass
print(m)")
  P=$(pid); [ -n "$P" ] && kill -9 "$P"
  DAY=$(ls "$ROOT"/tape/*.jsonl | tail -1); JD=$(ls "$ROOT"/journal/*.jsonl | tail -1)
  /usr/bin/python3 - "$DAY" "$JD" "$ROOT/state/beliefs.jsonl" "$ROOT/tape/SEQ" <<'PYEOF'
import sys, os
day, jd, bel, seq = sys.argv[1:5]
for p, junk in ((day, b"\x00" * 4096), (jd, b'{"kind": "brain", "act": "le'), (bel, b"\x00" * 100)):
    if os.path.exists(p):
        with open(p, "ab") as f:
            f.write(junk)
open(seq, "wb").close()
print("the cut: tails torn, SEQ emptied (preflight_days.sh's own form)")
PYEOF
  sleep 50
  [ "$(systemctl --user is-active "$UNIT")" = active ] || fail "not back after the power cut: $(systemctl --user show "$UNIT" -p Result -p NRestarts | tr '\n' ' ')"
  S=$(st); echo "[2] after the power cut: $S"
  echo "$S" | grep -q '"restored": true' || fail "not restored after the power cut: $S"
  [ -s "$ROOT/repairs/REPAIRS.jsonl" ] || fail "no repair recorded"
  echo "[2] repairs: $(wc -l < "$ROOT/repairs/REPAIRS.jsonl") rows"
  sleep 20
  /usr/bin/python3 - "$ROOT" "$TOP" <<'PYEOF' || fail "the tape after the cut"
import json, glob, sys
root, top = sys.argv[1], int(sys.argv[2])
seqs = []
for f in sorted(glob.glob(root + "/tape/*.jsonl")):
    for l in open(f, "rb"):
        seqs.append(json.loads(l)["seq"])
assert len(seqs) == len(set(seqs)), "a seq used twice"
assert max(seqs) > top, f"no new row after the cut ({max(seqs)} <= {top})"
print(f"[2] the tape: {len(seqs)} rows, no seq twice, max {max(seqs)} > {top} before the cut")
PYEOF
fi

# 5 · the video sense kept flowing through it all (the cursor's resume), then the life CLOSES CLEAN
V=$(st); echo "[3] before the close: $V"
bash "$HERE/close_long.sh" "$NAME" || fail "the close"
[ -f "$ROOT/STOPPED-AT" ] || fail "no STOPPED-AT — the life did not close clean"
[ "$(systemctl --user is-active "$UNIT")" = active ] && fail "the unit is still active after the close"
echo "[3] closed: STOPPED-AT $(cat "$ROOT/STOPPED-AT")"
echo "PREFLIGHT PASS ($NAME, mode $MODE, commit $COMMIT)"
