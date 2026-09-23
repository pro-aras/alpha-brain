# READER-LAG-0923 LAG e2e root: dry-life-1's record with the TAPE cut at 850 rows and the MIND having consumed only rows 1..750
# (a mind 100 rows behind its world at the stop), written in the body's own order by THIS tree's Mind (creature/mind.py is byte-identical
# to the pin bbaf4dd's; the life ran on 74c661d — the reader masks `hash` across commits, as it does for dry-life-1 itself).
#   journal: dry-life-1's start row verbatim → the Mind's own rows (rows 1..750; a `snapshot` event whenever its snapshot_count grows,
#            stamped with the triggering row's tape time) → dry-life-1's exam event verbatim → mind.close() (+ its snapshot event) →
#            dry-life-1's stop row verbatim (creature/body.py:stop's order: senses joined, the queue left unread, close(), STATUS, stop)
#   STATUS: creature/body.py:Body._build_status on the closed mind with the body's queue depth = 100 (the unconsumed rows 751..850),
#           heartbeat_at/started_at = dry-life-1's own
#   tape:   rows 1..850 of dry-life-1's tape file, payload symlinked; truth/ for seq ≤ 850; exam/ copied; GENOME.genome, CODE-COMMIT copied
import json, os, shutil, sys, threading, types
from pathlib import Path
W = Path("/data/dev/genome-wt-reader-lag"); sys.path.insert(0, str(W))
from creature.mind import Mind
from creature import body as body_mod
SRC = Path("/data/dev/genome-wt-reader-fix/scratch/dry-life-1"); ROOT = Path(sys.argv[1])
TAPE_ROWS, MIND_ROWS, QSIZE = 850, 750, 100
assert not ROOT.exists(), "fresh root only (#212)"
(ROOT / "tape").mkdir(parents=True)
os.symlink((SRC / "tape" / "payload").resolve(), ROOT / "tape" / "payload")
rows_all = [json.loads(l) for l in open(SRC / "tape" / "2026-09-22.jsonl")]
rows = rows_all[:TAPE_ROWS]; assert rows[-1]["seq"] == TAPE_ROWS
(ROOT / "tape" / "2026-09-22.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows)); (ROOT / "tape" / "SEQ").write_text(f"{TAPE_ROWS}\n")
for f in ("GENOME.genome", "CODE-COMMIT", "STARTED-AT", "PAGE.json", "unit.env"):
    shutil.copy2(SRC / f, ROOT / f)
(ROOT / "truth").mkdir()
for f in sorted((SRC / "truth").glob("*.json")):
    if int(f.stem) <= TAPE_ROWS: shutil.copy2(f, ROOT / "truth" / f.name)
shutil.copytree(SRC / "exam", ROOT / "exam")
src_events = [json.loads(l) for l in open(SRC / "journal" / "2026-09-22.jsonl") if '"event"' in l]
start = next(e for e in src_events if e["event"] == "start"); stop = next(e for e in src_events if e["event"] == "stop"); exam_ev = [e for e in src_events if e["event"] == "exam"]
(ROOT / "journal").mkdir(); J = ROOT / "journal" / "2026-09-22.jsonl"
def ev(row): J.open("a").write(json.dumps(row) + "\n")
ev(start)
mind = Mind(ROOT / "GENOME.genome", ROOT)
snaps = mind.snapshot_count
for r in rows[:MIND_ROWS]:
    mind.consume(r)
    if mind.snapshot_count > snaps:
        snaps = mind.snapshot_count; ev({"seq": None, "at": r["at"], "event": "snapshot", "snapshots": snaps, "at_moment": mind.org.t})
assert mind.last_seq == MIND_ROWS, mind.last_seq
for e in exam_ev: ev(e)
prev = mind.snapshot_count
mind.close()                                   # body.py:stop — the queue (rows 751..850) is left unread; close() lands the in-flight think at the last EYE row consumed
if mind.snapshot_count > prev:
    ev({"seq": None, "at": stop["at"], "event": "snapshot", "snapshots": mind.snapshot_count, "at_moment": mind.org.t})
fake = types.SimpleNamespace(_status_lock=threading.Lock(), _mind_times=[], sense_restarts=0, crash=None, mind=mind,
                             started_at=start["at"], q=types.SimpleNamespace(qsize=lambda: QSIZE))
st = body_mod.Body._build_status(fake); st["heartbeat_at"] = json.load(open(SRC / "STATUS.json"))["heartbeat_at"]
(ROOT / "STATUS.json").write_text(json.dumps(st))
ev(stop)
led = json.loads((ROOT / "state" / "ledger.json").read_text())
jrows = [json.loads(l) for l in open(J)]
mind_rows = [r for r in jrows if r.get("event") not in ("start", "snapshot", "stop", "exam")]
print(json.dumps({"tape_rows": len(rows), "tape_head": rows[-1]["seq"], "mind_last_seq": mind.last_seq, "status_last_seq": st["last_seq"], "status_backlog": st["mind_backlog_rows"],
                  "ledger_last_seq": led["last_seq"], "journal_rows": len(jrows), "mind_rows": len(mind_rows), "journal_last_mind_seq": max(int(r["seq"]) for r in mind_rows),
                  "rows_at_749": [sorted(k for k in r if k != "seq") for r in mind_rows if int(r["seq"]) == 749], "rows_at_750": [r for r in mind_rows if int(r["seq"]) == 750],
                  "cells": st["cells"], "snapshots": mind.snapshot_count, "events": [e["event"] for e in jrows if "event" in e]}, default=str))
