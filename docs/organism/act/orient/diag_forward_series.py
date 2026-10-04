#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:54 +0400 — WORLD-FACT DIAGNOSTIC under FIXED random-3 play (no candidate): forward's temporal clustering against the iid binomial the exact walk assumed.
# scratch diagnostic (not committed until used in the report): the TEMPORAL STRUCTURE of forward's effect under FIXED random-3 play (no candidate): the screen's window rule applied to the
# recorded series, against the iid binomial the exact walk assumed.
import collections
import json
import math
import sys

import numpy as np

from tools.toys import act_chooser_toy as toy


def cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


seeds = [int(s) for s in sys.argv[1].split(",")] if len(sys.argv) > 1 else [20260923, 21260923, 22260923]
episodes = int(sys.argv[2]) if len(sys.argv) > 2 else 300
series_all = []
for s in seeds:
    pol = toy.FixedDist(s, {0: 1.0, 1: 1.0, 2: 1.0})
    r = toy.run_game_fx(pol, s, episodes, keep_trace=10 ** 7)
    tr = r["trace"]
    fw = [t["effect"] for t in tr if t["act"] == "forward" and t["effect"] is not None]
    series_all.append(fw)
allfw = [x for s in series_all for x in s]
p = sum(allfw) / len(allfw)
print(f"forward known outcomes {len(allfw)}, change rate {p:.3f}")
# lag-1 autocorrelation within each series
num = den = 0.0
for s in series_all:
    a = np.array(s, dtype=float) - p
    num += float((a[1:] * a[:-1]).sum()); den += float((a * a).sum())
print(f"lag-1 autocorrelation of forward's effect: {num / den:.3f} (iid: 0)")
# windows of 20 consecutive forward outcomes
for n, k in ((20, 4), (10, 3)):
    dead = tot = 0
    for s in series_all:
        for i in range(len(s) - n + 1):
            tot += 1
            dead += int(sum(s[i:i + n]) < k)
    iid = cdf(k - 1, n, p)
    print(f"window {n}, live iff >= {k}: windows judged DEAD in the real series {dead / tot:.4f} (n = {tot}) vs iid binomial at p = {p:.3f}: {iid:.5f} -> x{(dead / tot) / max(iid, 1e-9):.1f}")
# run lengths of zeros
runs = []
for s in series_all:
    c = 0
    for x in s:
        if x == 0:
            c += 1
        else:
            if c:
                runs.append(c)
            c = 0
    if c:
        runs.append(c)
runs = np.array(runs)
print(f"runs of consecutive blocked forwards: n {len(runs)}, mean {runs.mean():.2f}, max {runs.max()}, share >= 6: {(runs >= 6).mean():.3f}, share >= 10: {(runs >= 10).mean():.3f}; iid geometric P(run >= 6) = {(1 - p) ** 5:.4f}, P(>= 10) = {(1 - p) ** 9:.5f}")
