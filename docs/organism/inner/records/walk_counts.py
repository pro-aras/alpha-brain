#!/usr/bin/env python3
# edit: Claude (Opus 5.5, swarm architect), 2026-10-03 11:15 +0400 — PREREG-INNER-1 §0.1–§0.2: the counts the law rests on, from a COPY of a life's
# saved web (web.json: the webs L / N and the self), read with the code's own reader (genome.web.Web.neighbours). Read-only.
"""docs/organism/inner/records/walk_counts.py --web <copy of state/prev/web.json> [--hops 1000] [--seeds 10]

Prints: the self's lived reliability per mature word; each word's consolidated neighbours among the brain's words; the GREEDY walks
(by count and by lift, with and without inhibition of return) and their cycles; the SEEDED RANDOM walk of PREREG-INNER-1 §2 (lift-weighted,
the last 2 topics excluded, restart from the self's weakest word every 5 hops) and its coverage at each seed.
PLANTED CONTROL (RULES §11): the greedy count walk with no inhibition must LOCK (a cycle of period <= 4 visiting <= 5 words); the
script exits 1 if it does not (the lock detector would then be blind) and 2 if the random walk covers < 10 words at any seed."""
from __future__ import annotations

import argparse
import collections
import json
import sys

import numpy as np

from genome.web import Web

BRAIN = ["big", "blue", "circle", "cross", "green", "red", "ring", "small", "square", "star", "triangle", "white", "yellow"]


def cycle_of(seq, tail=60, max_period=15):
    for p in range(1, max_period):
        if seq[-tail:] == seq[-tail - p:-p]:
            return p, seq[-p:]
    return None, None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="walk_counts")
    ap.add_argument("--web", required=True)
    ap.add_argument("--hops", type=int, default=1000)
    ap.add_argument("--seeds", type=int, default=10)
    a = ap.parse_args(argv)
    W = json.load(open(a.web, encoding="utf-8"))
    Lst = W["webs"]["L"]
    w = Web.loads(json.dumps(Lst))
    n = {b: Lst["nodes"][b]["n"] for b in BRAIN}
    T = Lst["t"]
    lived = W["self"]["lived"]["words"]
    rel = {b: lived[b][1] / lived[b][0] for b in BRAIN}
    weakest = min(BRAIN, key=lambda b: (rel[b], b))
    print("self lived reliability:", {b: round(rel[b], 3) for b in sorted(BRAIN, key=rel.get)}, "· the self picks:", weakest)
    NB = {x: [(y, c) for y, c in w.neighbours(x, n=10 ** 6) if y in BRAIN] for x in BRAIN}
    print("consolidated neighbours among the brain's words:", {x: len(v) for x, v in NB.items()})

    def lift(x, y, c):
        return c * T / (n[x] * n[y])

    def greedy(rule, inhibit):
        seq, recent = ["ring"], ["ring"]
        for _ in range(a.hops):
            cand = [(y, c) for y, c in NB[seq[-1]] if not inhibit or y not in recent[-inhibit:]] or NB[seq[-1]]
            key = (lambda t: (-t[1], t[0])) if rule == "count" else (lambda t: (-lift(seq[-1], t[0], t[1]), -t[1], t[0]))
            y = sorted(cand, key=key)[0][0]
            seq.append(y)
            recent.append(y)
        return seq

    locked_plant = None
    for rule, inh in (("count", 0), ("count", 3), ("lift", 0), ("lift", 3)):
        s = greedy(rule, inh)
        p, cyc = cycle_of(s)
        k = len(set(s))
        print(f"GREEDY {rule:5s} inhibit {inh}: words visited {k:2d} of 13 · cycle period {p} {cyc}")
        if rule == "count" and inh == 0:
            locked_plant = (p is not None and p <= 4 and k <= 5)

    covs = []
    for seed in range(a.seeds):
        rng = np.random.default_rng(seed)
        seq, cur, recent = [], weakest, [weakest]
        for h in range(a.hops):
            if h % 5 == 0:
                cur, recent = weakest, [weakest]
            seq.append(cur)
            cand = [(y, c) for y, c in NB[cur] if y not in recent[-2:]] or NB[cur]
            wts = np.array([lift(cur, y, c) for y, c in cand], float)
            cur = cand[int(rng.choice(len(cand), p=wts / wts.sum()))][0]
            recent.append(cur)
        c = collections.Counter(seq)
        covs.append(len(c))
        print(f"RANDOM walk seed {seed}: covers {len(c)} of 13 · largest share {max(c.values()) / len(seq):.3f} ({c.most_common(1)[0][0]})")
    print(f"PLANT (greedy count walk must lock): {'CAUGHT' if locked_plant else 'MISSED'}")
    if not locked_plant:
        return 1
    return 0 if min(covs) >= 10 else 2


if __name__ == "__main__":
    sys.exit(main())
