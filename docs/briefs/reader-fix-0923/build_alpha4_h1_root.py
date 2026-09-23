# READER-FIX-0923 end-to-end control: a CLOSED ALPHA4 record built from alpha4-1's hour-1 fixture (scratch copy) — the tape as recorded,
# the journal/state/STATUS written by THIS tree's Mind replaying it (mind code identical to 7bbc995: only creature/replay.py differs),
# STATUS by creature/body.py's own _build_status on the replay's measured per-row times, HEARD.json as the shelf sense writes it.
# Synthetic body events: start at the life's birth (00:58:17Z, the review), stop after the last row. No truth/, no exam/, no evolve/.
import json, os, sys, threading, time, types
from pathlib import Path
W = Path("/data/dev/genome-wt-reader-fix"); sys.path.insert(0, str(W))
from creature.mind import Mind
from creature import body as body_mod
FX = W / "scratch" / "fixtures" / "alpha4-1-hour1"; ROOT = W / "scratch" / "alpha4-h1-root"
assert not ROOT.exists(), "fresh root only"
(ROOT / "tape").mkdir(parents=True)
os.symlink((FX / "tape" / "payload").resolve(), ROOT / "tape" / "payload")
rows = [json.loads(l) for l in open(FX / "tape" / "2026-09-23.jsonl")]
(ROOT / "tape" / "2026-09-23.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
(ROOT / "CODE-COMMIT").write_text("7bbc995\n"); (ROOT / "GENOME.genome").write_text((FX / "GENOME.genome").read_text())
(ROOT / "journal").mkdir()
with open(ROOT / "journal" / "2026-09-23.jsonl", "a") as f:
    f.write(json.dumps({"seq": None, "at": "2026-09-23T00:58:17.000Z", "event": "start", "resumed_from_seq": 0, "backlog_replayed": 0}) + "\n")
mind = Mind(ROOT / "GENOME.genome", ROOT)
times = []; t0 = time.perf_counter()
for r in rows:
    a = time.perf_counter(); mind.consume(r); b = time.perf_counter(); times.append((b, 1000 * (b - a), r["sense"]))
mind.close()
wall = time.perf_counter() - t0
with open(ROOT / "journal" / "2026-09-23.jsonl", "a") as f:
    f.write(json.dumps({"seq": None, "at": "2026-09-23T01:58:17.500Z", "event": "stop"}) + "\n")
fake = types.SimpleNamespace(_status_lock=threading.Lock(), _mind_times=times, sense_restarts=0, crash=None, mind=mind,
                             started_at="2026-09-23T00:58:17.000Z", q=types.SimpleNamespace(qsize=lambda: 0))
st = body_mod.Body._build_status(fake)
st["heartbeat_at"] = rows[-1]["at"]
(ROOT / "STATUS.json").write_text(json.dumps(st, indent=1, default=str))
heard, seen = [], set()
for r in rows:
    m = r.get("meta") or {}
    if r["sense"] == "ear" and m.get("source") == "shelf" and m.get("word") and m["word"] not in seen:
        seen.add(m["word"]); heard.append(m["word"])
(ROOT / "read").mkdir(); (ROOT / "read" / "HEARD.json").write_text(json.dumps(heard))
print(json.dumps({"rows": len(rows), "wall_s": round(wall, 1), "journal_rows": sum(1 for _ in open(ROOT / "journal" / "2026-09-23.jsonl")),
                  "status": {k: st.get(k) for k in ("cells", "mind_ms_per_canvas_1min", "sight_born", "acts_chosen", "act_mismatches", "thinks", "sleeps", "questions_written", "questions_answered", "frames_filed")},
                  "heard": len(heard)}, default=str))
