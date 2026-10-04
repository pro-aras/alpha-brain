#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:58 +0400 — WORLD-FACT DIAGNOSTIC (no candidate): the RECORDED effect series under fixed random-3 / uniform-7 play against the iid binomial; the smooth-weight alternative priced on the real series.
# scratch diagnostic (no candidate): window-rate distributions of the RECORDED effect series — forward under fixed random-3 play, every act under fixed uniform-7 play —
# and what a smooth weight clip((rate - lo) / (hi - lo), 0, 1) would give, against the iid binomial.
import math
import sys

import numpy as np

from tools.toys import act_chooser_toy as toy


def series(policy_factory, seeds, episodes):
    out = {a: [] for a in toy.ACT_NAMES}
    for s in seeds:
        r = toy.run_game_fx(policy_factory(s), s, episodes, keep_trace=10 ** 7)
        per = {a: [] for a in toy.ACT_NAMES}
        for t in r["trace"]:
            if t["effect"] is not None:
                per[t["act"]].append(t["effect"])
        for a in toy.ACT_NAMES:
            out[a].append(per[a])
    return out


def binom_pmf(k, n, p):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def window_stats(seqs, n, lo, hi):
    rates = []
    for s in seqs:
        for i in range(len(s) - n + 1):
            rates.append(sum(s[i:i + n]) / n)
    r = np.array(rates)
    w = np.clip((r - lo) / (hi - lo), 0.0, 1.0)
    return r, w


seeds = [20260923, 21260923, 22260923]
EP = int(sys.argv[1]) if len(sys.argv) > 1 else 300
r3 = series(lambda s: toy.FixedDist(s, {0: 1.0, 1: 1.0, 2: 1.0}), seeds, EP)
u7 = series(lambda s: toy.FixedDist(s, {i: 1.0 for i in range(7)}), seeds, EP)
for n, lo, hi in ((20, 0.10, 0.30), (20, 0.05, 0.25), (30, 0.10, 0.30)):
    print(f"== window {n}, smooth weight clip((rate-{lo})/({hi}-{lo}))")
    for name, src, acts in (("forward under random-3", r3, ["forward"]), ("every act under uniform-7", u7, toy.ACT_NAMES)):
        for a in acts:
            r, w = window_stats(src[a], n, lo, hi)
            p = float(np.mean(np.concatenate([np.array(x) for x in src[a]])))
            iid_below_lo = sum(binom_pmf(k, n, p) for k in range(n + 1) if k / n < lo)
            iid_w = sum(binom_pmf(k, n, p) * min(1.0, max(0.0, (k / n - lo) / (hi - lo))) for k in range(n + 1))
            print(f"  {name:28s} {a:8s} p {p:.3f} windows {len(r):6d}: rate<lo {np.mean(r < lo):.4f} (iid {iid_below_lo:.4f}) · lo<=rate<hi {np.mean((r >= lo) & (r < hi)):.4f} · rate>=hi {np.mean(r >= hi):.4f} · E[weight] {w.mean():.4f} (iid {iid_w:.4f}) · P(weight=0) {np.mean(w == 0):.4f}")
# autocorrelation function of forward's effect under random-3
allf = r3["forward"]
p = float(np.mean(np.concatenate([np.array(x) for x in allf])))
acf = []
for lag in (1, 2, 3, 5, 8, 12, 20, 30):
    num = den = 0.0
    for s in allf:
        a = np.array(s, dtype=float) - p
        if len(a) > lag:
            num += float((a[lag:] * a[:-lag]).sum()); den += float((a * a).sum())
    acf.append((lag, round(num / den, 3)))
print("forward effect ACF (per forward outcome) under random-3:", acf)
