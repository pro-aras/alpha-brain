#!/usr/bin/env bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:5x +0400 — PREREG-INHERIT I7: a child killed hard in mid-training comes back by itself.
set -u
NAME=inh-c-kill; ROOT=/data/dev/genome-lives/$NAME; UNIT="creature-brain@$NAME.service"; D=/data/dev/brain-runs/day0929/inherit
[ -e "$ROOT" ] && { echo "root exists"; exit 2; }
mkdir -p "$ROOT"; git -C /data/dev/genome-wt-inherit worktree add --detach "$ROOT/code" bb44d3a >/dev/null 2>&1 || exit 3
cp $D/genomes/INH-T10000-20261103.genome "$ROOT/GENOME.genome"; date "+%Y-%m-%d %H:%M %z" > "$ROOT/STARTED-AT"
printf "GENOME=%s\nBODY_ARGS=\n" "$ROOT/GENOME.genome" > "$ROOT/unit.env"
mkdir "$ROOT/inherit"; cp /data/dev/genome-lives/brain-lean-nearest-20261102/state/brain.json /data/dev/genome-lives/brain-lean-nearest-20261102/state/brain.npz "$ROOT/inherit/"
systemctl --user start "$UNIT" || exit 5
/usr/bin/python3 - "$ROOT" "$UNIT" <<'PYEOF'
import json, os, signal, subprocess, sys, time
R, U = sys.argv[1], sys.argv[2]
def st():
    for _ in range(10):
        try: return json.load(open(R + "/STATUS.json"))
        except Exception: time.sleep(0.5)
    return None
def line(tag, s):
    b = s["brain"]; print(tag, s["heartbeat_at"], "learned", b["learned"], "learn_rows", b["learn_rows"], "restored", b.get("restored"), "inherited", b.get("inherited"), "crash", s["crash"], flush=True)
t0 = time.time(); s = None
while time.time() - t0 < 900:
    s = st()
    if s and (s.get("brain") or {}).get("learn_rows", 0) >= 1500: break
    time.sleep(3)
line("before-kill", s)
pid = int(subprocess.run(["systemctl", "--user", "show", U, "-p", "MainPID", "--value"], capture_output=True, text=True).stdout)
print(subprocess.run(["ps", "-o", "pid,stat,args", "-p", str(pid)], capture_output=True, text=True).stdout[:240])
os.kill(pid, signal.SIGKILL)
time.sleep(45)
print(subprocess.run(["systemctl", "--user", "show", U, "-p", "NRestarts", "-p", "ActiveState"], capture_output=True, text=True).stdout)
before = s["brain"]["learn_rows"]
for _ in range(3):
    a = st(); line("after", a); time.sleep(15)
b = a["brain"]
ok = b.get("restored") is True and (b.get("inherited") or {}).get("learned") == 10000 and b["learn_rows"] > before and a["crash"] is None
print("I7", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
PYEOF
RC=$?
systemctl --user stop "$UNIT"; date "+%Y-%m-%d %H:%M %z" > "$ROOT/STOPPED-AT"
exit $RC
