# READER v3.5 step 5: the TAPE TWIN read from the dry run's own files — a4l-cost's closed tape replayed under C2's mind code (this branch; its
# creature/ + genome/ are 4d1a100's byte for byte) vs a4l-cost's live journal (633abca), EVERY seq walked (never only the first difference):
# per-field counts of differing rows, row-count mismatches, and compare() with the declared M1 field (`readiness`) and `hash` masked.
import json, sys, collections
from pathlib import Path
sys.path.insert(0, "/data/dev/genome-wt-reader35")
from creature import replay as rp
out = Path(sys.argv[1])
u1 = rp.read_mind_journal(out / "twins" / "unblinded-1" / "mind-journal.jsonl")
live = rp.read_mind_journal(out / "live-journal.jsonl")
print("rows: replay", len(u1), "live", len(live))
print("compare(ignore={hash}):", rp.compare(u1, live, ignore={"hash"}))
print("compare(ignore={hash, readiness}):", rp.compare(u1, live, ignore={"hash", "readiness"}))
g = collections.defaultdict(list); w = collections.defaultdict(list)
for r in u1: g[int(r["seq"])].append(r)
for r in live: w[int(r["seq"])].append(r)
fields = collections.Counter(); count_mismatch = []; missing = []; first = {}
for s in sorted(set(g) | set(w)):
    if s not in g or s not in w:
        missing.append(s); continue
    if len(g[s]) != len(w[s]):
        count_mismatch.append(s); continue
    for a, b in zip(g[s], w[s]):
        for k in (set(a) | set(b)) - {"hash"}:
            if a.get(k) != b.get(k):
                fields[k] += 1; first.setdefault(k, s)
print("differing rows per field (hash masked):", dict(fields), "first seq per field:", first)
print("seqs with a row-count mismatch:", len(count_mismatch), count_mismatch[:10], "· seqs missing on one side:", len(missing), missing[:10])
rd = [(a.get("readiness"), b.get("readiness")) for s in sorted(set(g) & set(w)) for a, b in zip(g[s], w[s]) if a.get("readiness") != b.get("readiness")][:2]
print("readiness, first two differing (replay C2 vs live 633abca):", json.dumps(rd)[:600])
