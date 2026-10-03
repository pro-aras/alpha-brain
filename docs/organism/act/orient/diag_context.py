#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 12:07 +0400 — WORLD-FACT DIAGNOSTIC (no candidate): next-frame novelty / change / reward by (previous act, previous effect) context under fixed random-3 play — the material of a LEARNED class-B chooser's law.
# scratch diagnostic (no candidate): under FIXED random-3 play, the NOVELTY / change / reward of the NEXT frame by (previous act, previous effect) context and next act.
# The question for a LEARNED class-B chooser: does a dense novelty value, per context, point at the persistent walker's rule (blocked -> turn, after a turn -> forward, after a moving forward -> forward)?
import collections
import sys

from tools.toys import act_chooser_toy as toy

seeds = [20260923, 21260923, 22260923]
EP = int(sys.argv[1]) if len(sys.argv) > 1 else 300
n = collections.Counter(); nov = collections.Counter(); chg = collections.Counter(); rew = collections.Counter()
for s in seeds:
    r = toy.run_game_fx(toy.FixedDist(s, {0: 1.0, 1: 1.0, 2: 1.0}), s, EP, keep_trace=10 ** 7)
    tr = r["trace"]
    for prev, cur in zip(tr, tr[1:]):
        if prev["episode"] != cur["episode"]:
            continue
        if prev["effect"] is None or cur["effect"] is None:
            continue
        ctx = (prev["act"] if prev["act"] == "forward" else "turn", prev["effect"])
        key = (ctx, cur["act"] if cur["act"] == "forward" else "turn")
        n[key] += 1; nov[key] += cur["novel"]; chg[key] += cur["effect"]; rew[key] += int(cur["terminated"] and cur["got"] > 0)
print(f"{'previous (act, effect)':26s} {'next':8s} {'n':>6s} {'P(novel)':>9s} {'P(change)':>10s} {'P(reward step)':>15s}")
for ctx in (("turn", 1), ("forward", 1), ("forward", 0)):
    for nxt in ("turn", "forward"):
        k = (ctx, nxt)
        print(f"{str(ctx):26s} {nxt:8s} {n[k]:6d} {nov[k] / max(1, n[k]):9.3f} {chg[k] / max(1, n[k]):10.3f} {rew[k] / max(1, n[k]):15.4f}")
