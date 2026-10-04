#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:53 +0400 — SMOKE DIAGNOSTIC (not a graded run): one life of C-SCR replayed with its trace after a 2-life smoke showed forward dead 14.7 % of acts 241–960.
# scratch diagnostic (not committed): one life of the candidate, its per-act empirical change rate over KNOWN outcomes and forward's window over time.
import collections
import json
import sys

from tools.toys import act_chooser_toy as toy

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 30261923
acts_n = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
pol = toy.ScreenChooser(seed)
r = toy.run_game_fx(pol, seed, 10 ** 6, keep_trace=acts_n, max_steps_total=acts_n)
tr = r["trace"]
n = collections.Counter(); ch = collections.Counter(); unk = collections.Counter()
for t in tr:
    if t["effect"] is None:
        unk[t["act"]] += 1
    else:
        n[t["act"]] += 1; ch[t["act"]] += t["effect"]
print("seed", seed, "acts", len(tr), "episodes", r["episodes"], "successes", r["successes"])
for a in toy.ACT_NAMES:
    print(f"  {a:8s} known {n[a]:4d} excluded {unk[a]:3d}  change rate {ch[a] / max(1, n[a]):.3f}")
hist = pol.live_history
dead = [i for i, f in enumerate(hist) if not f[2]]
print("forward judged dead at choices:", len(dead), "of", len(hist))
# runs of dead
runs = []
start = None
for i, f in enumerate(hist):
    if not f[2] and start is None:
        start = i
    if f[2] and start is not None:
        runs.append((start, i - 1)); start = None
if start is not None:
    runs.append((start, len(hist) - 1))
print("dead stretches (start, end, length):", [(a, b, b - a + 1) for a, b in runs][:12])
# forward's window just before each death: the last 20 known effects of forward
fw = [t["effect"] for t in tr if t["act"] == "forward" and t["effect"] is not None]
print("forward known effects (first 60):", fw[:60])
# the per-100-act forward change rate
blk = []
for i in range(0, len(tr) - 99, 100):
    seg = [t for t in tr[i:i + 100] if t["act"] == "forward" and t["effect"] is not None]
    blk.append((len(seg), round(sum(t["effect"] for t in seg) / max(1, len(seg)), 2)))
print("forward (count, rate) per 100 acts:", blk)
