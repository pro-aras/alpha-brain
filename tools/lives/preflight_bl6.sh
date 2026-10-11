#!/usr/bin/env bash
# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 20:5x +0400 — PREREG-BRAIN-LONG-6 §2 B5 (the law
# SIGNED; SEAT-LINE sha256 2c6bb22b…; AMENDMENT 1 e21d62d0…): the TWO short pre-flight lives of brain-long-6
# on the DECLARED TOY SHELF (/data/dev/brain-runs/alpha-6/bl5-preflight-toy/video-shelf — the A6 build's own
# fixture, NEVER the real shelf; reused lawfully per the law §2 B5), both with the front wired (--eye-front)
# and the REGISTERS clause declared (BRAIN-LONG-6-PREFLIGHT.genome carries it — the launch genome's own form):
#   pre-1: a hard KILL → the resume restores (STATUS brain.restored True) — the gate's own bar;
#   pre-2: the POWER-CUT form (preflight_alpha6.sh's own corruption: torn tails + the SEQ emptied in the
#          restart gap) healed (repairs/REPAIRS.jsonl, no seq used twice), then the life CLOSES CLEAN.
# THE BL6 ADDITIONS over A6's driver (the law §3 G-REGISTERS-LIVE's live rehearsal): the pre-flight ALSO
# reads the registers' presence: (a) the web carries s:-prefixed nodes (the content web ON — presence count
# printed); (b) the muse budget form: one planted chat pair through the door's own road, the muse's journal
# rows printed (a chain may lawfully not fire inside the price — the budget accounting is the presence);
# (c) precision: the journal's `lr` stream printed with its first divergence from the 0.5/2.0 clip pair
# (the register's fingerprint) — NAMED if none lands inside the ≤1 h price.
# The launch machinery is the standard one (launch_long.sh → launch_brain.sh → close_long.sh); the law §6
# fences the pre-flights SMALL (4G): this driver rewrites the drop-in to MemoryHigh/MemoryMax 4G right after
# the launch and daemon-reloads — the kill's own restart brings the 4G fence live, so pre-1's restored gate
# is uncontaminated (no resume before the kill). The 16G/20G ceiling that launch_long.sh writes stands only
# for the seconds between the launch and this rewrite; the pre-flight's RSS is read against the DECLARED 4G
# from the start (S2). The scene world rides the toy seed's own (the preflight genome's scene line: seed
# 20261211, train 400 — the repaired scene world's FIRST live publication is read here, restarts == 0).
# usage: preflight_bl6.sh <brain-long-6-pre-1|brain-long-6-pre-2> <commit>
set -uo pipefail
NAME="${1:?life name (brain-long-6-pre-1 or -pre-2)}"; COMMIT="${2:?commit}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT=/data/dev/genome-lives/$NAME; UNIT="creature-brain@$NAME.service"
SHELF=/data/dev/brain-runs/alpha-6/bl5-preflight-toy/video-shelf
MODE=kill; [ "$NAME" = "brain-long-6-pre-2" ] && MODE=powercut
fail() { echo "PREFLIGHT FAIL: $*"; exit 1; }

st() { /usr/bin/python3 -c "
import json,sys
try: s=json.load(open('$ROOT/STATUS.json'))
except Exception: print('none'); sys.exit()
b=s.get('brain') or {}
print(json.dumps({'moments':s.get('moments'),'last_seq':s.get('last_seq'),'learned':b.get('learned'),
 'restored':b.get('restored'),'calibrations':b.get('calibrations'),'video':s.get('video'),'crash':s.get('crash'),
 'scene':s.get('scene'),'sense_restarts':s.get('sense_restarts'),'turns':b.get('turns')}))"; }
wait_learned() { local want=$1 t0=$(date +%s); while [ $(( $(date +%s) - t0 )) -lt 1500 ]; do
  L=$(/usr/bin/python3 -c "import json;print((json.load(open('$ROOT/STATUS.json')).get('brain') or {}).get('learned') or 0)" 2>/dev/null || echo 0)
  [ "${L:-0}" -ge "$want" ] && return 0; sleep 5; done; return 1; }
pid() { systemctl --user show "$UNIT" -p MainPID --value; }
rss_mb() { /usr/bin/python3 -c "import json;print(json.load(open('$ROOT/STATUS.json')).get('rss_mb') or 0)" 2>/dev/null || echo 0; }

# 0 · the declared toy shelf must exist, frozen and verified, before any life is born
[ -f "$SHELF/MANIFEST.sha256" ] || fail "no toy shelf at $SHELF (the A6 build's fixture)"
( cd "$HERE/../.." && PYTHONPATH=. python3 -B -m tools.worlds.video_shelf verify --shelf "$SHELF" ) || fail "the toy shelf's manifest does not verify"

# 1 · the launch, the standard machinery's own form (+ the front wired — the law's pass-through)
bash "$HERE/launch_long.sh" "$NAME" "$COMMIT" genome/brain/lives/BRAIN-LONG-6-PREFLIGHT.genome \
     "--folder /data/dev/genome/world --plant-after 15000 --eye-front" || fail "the launch"

# 2 · the pre-flight fence (the law §6: fenced small, 4G) — in place before the kill's restart
DROP="${HOME}/.config/systemd/user/creature-brain@${NAME}.service.d"
cat > "$DROP/fence.conf" <<'FEOF'
# the PRE-FLIGHT's fence (PREREG-BRAIN-LONG-6 §6: fenced small, 4G — not the long life's 16G/20G): S2 stops the flight
# if the life's RSS crosses it. Written by preflight_bl6.sh over launch_long.sh's own drop-in.
[Service]
MemoryHigh=4G
MemoryMax=4G
FEOF
systemctl --user daemon-reload
echo "[fence] $(grep -c Memory "$DROP/fence.conf") lines, 4G/4G, daemon-reloaded (live at the unit's next start)"

# 3 · the healthy birth: the first calibration, the video rows flowing, the front on, the voice rows on,
#     THE SCENE WORLD PUBLISHING (the law's repair, read live), the registers' presence
wait_learned 250 || fail "no 250 learned in 25 minutes: $(st)"
echo "[1] alive past the first calibration: $(st)"
st | grep -q '"crash": null' || fail "a crash on STATUS: $(st)"
st | grep -q '"restored": null' || fail "restored is not None at birth: $(st)"
st | grep -q '"calibrations": 0' && fail "no calibration on STATUS: $(st)"
# the law's scene repair, live: the scene world at 20261211 publishes, and the refusal crash-loop is dead
st | grep -q '"published_moments": 0' && fail "the scene world published nothing: $(st)"
/usr/bin/python3 - "$ROOT" <<'PYEOF' || fail "the registers' live presence"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
# (a) the content web ON: s:-prefixed content nodes in the web state
web = json.load(open(root / "state" / "web.json"))
s_nodes = sum(1 for rule in ("L", "N") for k in (web.get(rule) or {}).get("nodes", {}) if str(k).startswith("s:"))
w_nodes = sum(1 for rule in ("L", "N") for k in (web.get(rule) or {}).get("nodes", {}) if str(k).startswith("w:"))
assert s_nodes > 0, f"no s: content nodes in the web (content_web declared): prefixes read: {s_nodes} s:, {w_nodes} w:"
print(f"[1] content-web live: {s_nodes} s: nodes, {w_nodes} w: nodes in the live web")
PYEOF
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
# the BL6 additions: (b) the muse's journal surface, (c) precision's lr fingerprint
muse_rows = [r for r in J if r.get("muse") or (r.get("kind") == "muse")]
lrs = [r["lr"] for r in canvas if isinstance(r.get("lr"), (int, float))]
clip_pair = sum(1 for v in lrs if v in (0.5, 2.0))
print(f"[1] video rows eye {len(veye)} ear {len(vear)} · the first {min(len(life_v), 40)} video rows == the shelf's own · "
      f"front {len(fronted)}/{len(canvas)} canvas rows · voice rows {len(voice)} · say answers with n_readbacks {len(inc)}/{len(says)}")
print(f"[1] muse journal rows: {len(muse_rows)} (the planted chat pair lands with the pre-flight's own chat write if any — the budget form)")
print(f"[1] precision: {len(lrs)} lr rows, {clip_pair} at the clip pair (the register's fingerprint grows the interior share as it settles)")
if not says:
    print("[1] NAMED: no say answer inside the flight's ≤1 h price — the row-level live form reads on the launch's first day (M-MOUTH's own wall)")
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
print("the cut: tails torn, SEQ emptied (preflight_alpha6.sh's own form)")
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
/usr/bin/python3 - "$ROOT" <<'PYEOF' || fail "the video world stalled across the gate"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
rows = []
for f in sorted((root / "tape").glob("*.jsonl")):
    rows.extend(json.loads(l) for l in open(f) if l.strip())
veye = [r for r in rows if r["sense"] == "eye" and r["meta"].get("source") == "video"]
assert len(veye) >= 2, f"the video eye stalled: {len(veye)} rows"
print(f"[3] the video world kept flowing: eye rows {len(veye)}")
PYEOF
bash "$HERE/close_long.sh" "$NAME" || fail "the clean close"
echo "PREFLIGHT PASS: $NAME ($MODE) on $COMMIT"
