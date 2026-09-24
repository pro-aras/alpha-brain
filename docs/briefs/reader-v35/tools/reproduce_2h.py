# READER v3.5 step 5: reproduce the seat's 2 h stream counts (A4-LADDER-2-PREREG ADDENDUM §7(2) item 1) on the CLOSED copies — find the wall-clock
# instant at which the seat's numbers were read, then run the reader's own IDENTITY mark with both roots cut at that instant.
import json, sys, bisect
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "/data/dev/genome-wt-reader35")
import tools.verdict_g4 as vg
from tools import verdict_life as vl
SRC = ("maker", "game", "shelf", "folder")
def eye_times(root):
    rows = []
    for f in sorted((Path(root) / "tape").glob("*.jsonl")):
        rows += vg.read_jsonl(f)
    return {s: sorted(vg._iso(r["at"]).timestamp() for r in rows if r.get("sense") == "eye" and (r.get("meta") or {}).get("source") == s) for s in SRC}
def counts_at(times, T):
    return tuple(bisect.bisect_right(times[s], T) for s in SRC)
def find(roots, target):
    """Every instant (an eye row's own time, ± 1 ms) where min over the roots of the per-source counts == target."""
    ts = [eye_times(r) for r in roots]
    cands = sorted({t for tt in ts for s in SRC for t in tt[s]})
    hits = [T for T in cands if tuple(min(c) for c in zip(*[counts_at(tt, T) for tt in ts])) == tuple(target)]
    return hits, ts
if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "cost":
        roots = ["a4l2-cost-copy"]; target = (1651, 277, 1851, 275); other = "a4l-cost-copy"
    else:
        roots = ["a4l2-floor-copy", "a4l2-cost-copy"]; target = (1737, 291, 1945, 290); other = None
    hits, ts = find([Path("/data/dev/scratch-reader35") / r for r in roots], target)
    print(f"{mode}: target {dict(zip(SRC, target))} — instants reproducing it: {len(hits)}"
          + (f", from {datetime.fromtimestamp(hits[0], timezone.utc).isoformat()} to {datetime.fromtimestamp(hits[-1], timezone.utc).isoformat()}" if hits else ""))
    if hits:
        T = hits[0]
        A_root = Path("/data/dev/scratch-reader35") / roots[0]
        A0 = vg.side_record(A_root)
        hA = (T - A0["t0"].timestamp()) / 3600 + 1e-7
        A = vg.side_record(A_root, hA)
        if other:
            B = vg.side_record(Path("/data/dev/scratch-reader35") / other)
        else:
            B_root = Path("/data/dev/scratch-reader35") / roots[1]
            B0 = vg.side_record(B_root); B = vg.side_record(B_root, (T - B0["t0"].timestamp()) / 3600 + 1e-7)
        m = vl.identity_mark(A["tape"], A["mind"], B["tape"], B["mind"], label_a=roots[0], label_b=(other or roots[1]))
        print(f"  cut at {datetime.fromtimestamp(T, timezone.utc).isoformat()} (A at {hA:.4f} h of its life): IDENTITY {'PASS' if m['pass'] else 'FAIL'} — {m['reason']}")
        for s in SRC:
            v = m["streams"][s]; print(f"    {s:7s} {v['identical']:,}/{v['compared']:,} (a {v['a']:,}, b {v['b']:,}) first divergence {v['first_divergence']}")
        print(f"    meeting points {m['meeting_points']:,} (disagree {m['meeting_points_disagree']}) · reach {m['reach']}")
