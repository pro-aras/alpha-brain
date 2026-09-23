# READER-LAG-0923 (b): the RACY CLOSE (creature/body.py:stop joins the mind thread 5 s, then mind.close() runs BESIDE an in-flight consume),
# built DETERMINISTICALLY as the two end states the race can leave on disk — never a body fix, a fixture the reader is read against:
#   mode frozen : the mind COMPLETED rows 1..N-1; row N (an eye row) was in flight when close() ran and never finished (the process exited
#                 while it ran): close() landed the pending think at row N's own at/seq (Mind._cur_at/_cur_seq are set at the top of
#                 _consume_eye) and snapshotted (ledger last_seq = N-1); STATUS last_seq N-1, queue depth = head - N (row N dequeued);
#                 the stop event; NO rows of N's own in the journal.
#   mode late   : as frozen, but row N's consume COMPLETED after the stop event (its moment/coarse/sleep/think rows land after the stop row;
#                 the sequential stand-in for the interleaving «close first, the rest of N after»; a submit after the executor's shutdown
#                 raises here exactly as it would in the body — recorded, not hidden).
# Source rows: dry-life-1's tape (rows 1..850 on the tape, like build_lag_root.py). N = the last EYE row <= 750 (749).
import json, os, shutil, sys, threading, types
from pathlib import Path
W = Path("/data/dev/genome-wt-reader-lag"); sys.path.insert(0, str(W))
from creature.mind import Mind
from creature import body as body_mod
SRC = Path("/data/dev/genome-wt-reader-fix/scratch/dry-life-1"); ROOT = Path(sys.argv[1]); MODE = sys.argv[2]; assert MODE in ("frozen", "late", "crash")
TAPE_ROWS = 850
assert not ROOT.exists(), "fresh root only (#212)"
(ROOT / "tape").mkdir(parents=True)
os.symlink((SRC / "tape" / "payload").resolve(), ROOT / "tape" / "payload")
rows = [json.loads(l) for l in open(SRC / "tape" / "2026-09-22.jsonl")][:TAPE_ROWS]
N = int(sys.argv[3]) if len(sys.argv) > 3 else max(r["seq"] for r in rows if r["sense"] == "eye" and r["seq"] <= 750)   # the in-flight EYE row (749 by default; 729 = an eye row while the word think launched at canvas 270 is still pending — applied live at 731)
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
for r in rows:
    if r["seq"] >= N: break
    mind.consume(r)
    if mind.snapshot_count > snaps:
        snaps = mind.snapshot_count; ev({"seq": None, "at": r["at"], "event": "snapshot", "snapshots": snaps, "at_moment": mind.org.t})
assert mind.last_seq == N - 1
for e in exam_ev: ev(e)
rowN = rows[N - 1]; assert rowN["seq"] == N and rowN["sense"] == "eye"
pending_before_close = mind._think_pending is not None
mind._cur_at, mind._cur_seq = rowN["at"], rowN["seq"]          # what _consume_eye sets FIRST when row N's consume begins (creature/mind.py:1163-1164)
prev = mind.snapshot_count
mind.close()                                                   # body.py:stop, the join timed out: the in-flight think lands at row N's seq; the snapshot beside the in-flight consume
if mind.snapshot_count > prev:
    ev({"seq": None, "at": stop["at"], "event": "snapshot", "snapshots": mind.snapshot_count, "at_moment": mind.org.t})
fake = types.SimpleNamespace(_status_lock=threading.Lock(), _mind_times=[], sense_restarts=0, crash=None, mind=mind,
                             started_at=start["at"], q=types.SimpleNamespace(qsize=lambda: TAPE_ROWS - N))   # row N dequeued, rows N+1..head in the queue
st = body_mod.Body._build_status(fake); st["heartbeat_at"] = json.load(open(SRC / "STATUS.json"))["heartbeat_at"]
(ROOT / "STATUS.json").write_text(json.dumps(st))
late_error = None
if MODE == "crash":
    # mode crash: row N's in-flight consume reaches a think boundary whose chosen item is threaded (word/self) AFTER close() shut the executor:
    # `submit` raises RuntimeError → creature/body.py:_handle_mind_crash writes STATUS with `crash` and os._exit(3) — here modelled as the
    # crash WINNING the race with stop()'s own stop row (no stop event on the record; STATUS = the crash handler's, the last writer).
    try:
        mind.consume(rowN)
    except Exception as e:
        late_error = repr(e)
        fake.crash = {"at": rowN["at"], "error": repr(e), "seq": N}
        st = body_mod.Body._build_status(fake); st["heartbeat_at"] = json.load(open(SRC / "STATUS.json"))["heartbeat_at"]
        (ROOT / "STATUS.json").write_text(json.dumps(st))
    else:
        late_error = "NO EXCEPTION: row N's consume reached no threaded think boundary — this row does not reproduce the crash path"
        ev(stop)
else:
    ev(stop)
    if MODE == "late":
        try:
            mind.consume(rowN)                                 # the rest of row N, after the stop row (the executor is shut down: a word/self think boundary raises here as in the body)
        except Exception as e:
            late_error = repr(e)
led = json.loads((ROOT / "state" / "ledger.json").read_text())
jrows = [json.loads(l) for l in open(J)]
mind_rows = [r for r in jrows if r.get("event") not in ("start", "snapshot", "stop", "exam")]
print(json.dumps({"mode": MODE, "N": N, "pending_think_at_close": pending_before_close, "tape_head": rows[-1]["seq"], "mind_last_seq_attr": mind.last_seq,
                  "status_last_seq": st["last_seq"], "status_backlog": st["mind_backlog_rows"], "ledger_last_seq": led["last_seq"],
                  "journal_last_mind_seq": max(int(r["seq"]) for r in mind_rows), "rows_at_N": [sorted(k for k in r if k != "seq") for r in mind_rows if int(r["seq"]) == N],
                  "file_order_tail": [(r.get("event") or ("think" if "think" in r else "moment/other"), r.get("seq")) for r in jrows[-6:]], "late_error": late_error}, default=str))
