#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:05 +0400 — ORIENTATION READER (scratch, not committed): the LIVE record's per-act
# «effect» (did the frame's tape `sha` change between the previous game eye row and this outcome's own eye row?) on COPIES of brain-long-2's
# closed tape days. Prints the PRESENCE counts first (#168): game eye rows, rows carrying `sha`, outcome rows, outcome rows carrying act/got.
import collections
import json
import sys
from pathlib import Path

ACT_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]
files = sorted(Path("scratch/ro/tape").glob("*.jsonl"))
rows = []
for f in files:
    for line in f.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        m = r.get("meta") or {}
        if m.get("source") == "game" and r.get("sense") in ("eye", "outcome"):
            rows.append({"seq": int(r["seq"]), "sense": r["sense"], "sha": r.get("sha"), "meta": m})
rows.sort(key=lambda r: r["seq"])
eyes = [r for r in rows if r["sense"] == "eye"]
outs = [r for r in rows if r["sense"] == "outcome"]
print(f"files {len(files)} · game eye rows {len(eyes)} (carrying sha {sum(1 for r in eyes if r['sha'])}) · game outcome rows {len(outs)} "
      f"(carrying act {sum(1 for r in outs if 'act' in r['meta'])}, got {sum(1 for r in outs if r['meta'].get('got') is not None)})")

prev_sha = None
prev_key = None
last_eye_sha = None
prev_ep = None
last_ep = None
boundary = 0
n = collections.Counter()
chg = collections.Counter()
unknown = 0
dups = 0
chosen_by = collections.Counter()
for r in rows:
    m = r["meta"]
    if r["sense"] == "eye":
        key = (m.get("episode"), m.get("step"))
        if key == prev_key:
            dups += 1          # a re-published step (the cursor law): same frame twice — never compare a frame with itself
            continue
        prev_sha, last_eye_sha = last_eye_sha, r["sha"]
        prev_ep, last_ep = last_ep, m.get("episode")
        prev_key = key
    else:
        act = m.get("act")
        chosen_by[m.get("chosen_by")] += 1
        if prev_sha is None or last_eye_sha is None:
            unknown += 1
            continue
        if prev_ep != last_ep:
            boundary += 1      # the worker resets SILENTLY: this act landed on a NEW episode's frame -> effect UNKNOWN (never 0, never 1)
            continue
        n[act] += 1
        chg[act] += int(last_eye_sha != prev_sha)

print(f"duplicate eye rows skipped {dups} · outcome rows with no previous frame (unknown) {unknown} · episode-BOUNDARY outcomes excluded {boundary} · chosen_by {dict(chosen_by)}")
print("per act (the LIVE life's own play: 10 % uniform + 90 % the locked act):")
for a in ACT_NAMES:
    print(f"  {a:8s} n {n[a]:5d}  changed {chg[a]:5d}  effect rate {chg[a] / max(1, n[a]):.3f}")
print("total outcomes compared", sum(n.values()))
