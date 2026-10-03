#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:11 +0400 — the derived numbers PREREG-ACT-EFFECT quotes, computed here and read back from this file's own
# output (never typed from memory, #242). Pure arithmetic over the orientation probes' counts (orient/probe_world_facts*.json) and the
# declared parameters (window n = 10, live threshold t = 0.3, floor 0.1). Run: python3 docs/organism/act/orient/prereg_numbers.py
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
p1 = json.loads((HERE / "probe_world_facts.json").read_text())["random7"]
p2 = json.loads((HERE / "probe_world_facts2.json").read_text())
ACTS = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]
N_WIN, T_LIVE, FLOOR = 10, 0.3, 0.1


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


print("== reward per step under uniform play (probe 1: %d steps, %d episodes, success %.4f)" % (p1["steps"], p1["episodes"], p1["success"]))
rew_total = sum(p1["per_act"][a]["rewarded"] for a in ACTS)
for a in ACTS:
    d = p1["per_act"][a]
    print(f"  {a:8s} rewarded {d['rewarded']:3d} / n {d['n']:5d} = {d['rewarded'] / d['n']:.5f}   10-outcome window holds a reward {1 - (1 - d['rewarded'] / d['n']) ** 10:.3f} of the time")
print(f"  total rewarded {rew_total} over {p1['steps']} steps = {rew_total / p1['steps']:.5f}/step -> {960 * rew_total / p1['steps']:.1f} rewards in 960 acts, {4920 * rew_total / p1['steps']:.1f} in 4,920")
pf, pl, pr = (p1["per_act"][a]["rewarded"] / p1["per_act"][a]["n"] for a in ("forward", "left", "right"))
for name, q in (("left", pl), ("right", pr)):
    n_needed = 9 * (pf + q) / (pf - q) ** 2
    print(f"  steps of EACH act to rank forward over {name} at z = 3: {n_needed:,.0f}")

print("== the effect signal (probe 2, same-episode pairs, uniform play)")
for a in ACTS:
    d = p2["per_act"][a]
    print(f"  {a:8s} n {d['n']:5d}  p_changed {d['p_changed']:.3f}  p_novel {d['p_novel']:.3f}")
print(f"  boundary outcomes excluded {p2['unknown_boundary_outcomes']} of {p2['steps']} = {p2['unknown_boundary_outcomes'] / p2['steps']:.4f}")
lo = min(p2["per_act"][a]["p_changed"] for a in ("left", "right", "forward"))
hi = max(p2["per_act"][a]["p_changed"] for a in ("pickup", "drop", "toggle", "done"))
print(f"  lowest live-act rate {lo:.3f} / highest dead-act rate {hi:.3f} = factor {lo / hi:.1f}")

print(f"== misclassification of the SCREEN (window {N_WIN}, live iff rate >= {T_LIVE}, i.e. >= {math.ceil(T_LIVE * N_WIN)} changes of {N_WIN})")
k_live = math.ceil(T_LIVE * N_WIN)
for a in ACTS:
    p = p2["per_act"][a]["p_changed"]
    p_dead = binom_cdf(k_live - 1, N_WIN, p)       # judged dead although its true rate is p
    print(f"  {a:8s} true rate {p:.3f}: P(judged DEAD at one evaluation) = {p_dead:.4f}   P(judged LIVE) = {1 - p_dead:.4f}")

print("== the candidate's stationary mixture (the landed 10 % uniform draw + uniform over the live set {left, right, forward})")
live_share = (1 - FLOOR) / 3 + FLOOR / 7
dead_share = FLOOR / 7
print(f"  P(left) = P(right) = P(forward) = {live_share:.4f}; P(each no-op) = {dead_share:.4f}; no-op total {4 * dead_share:.4f}")

print("== startup: acts until EVERY act has >= 10 outcomes under uniform choice (7 acts, 20,000 trials)")
rng = np.random.default_rng(20261003)
t_all = []
for _ in range(20000):
    c = np.zeros(7, dtype=int)
    t = 0
    while c.min() < N_WIN:
        c[rng.integers(0, 7)] += 1
        t += 1
    t_all.append(t)
t_all = np.array(t_all)
print(f"  mean {t_all.mean():.1f}, median {np.median(t_all):.0f}, p5 {np.percentile(t_all, 5):.0f}, p95 {np.percentile(t_all, 95):.0f}")

print("== sample size for the smallest detectable seed-level gap (paired t, 12 seeds, p < 0.001 one-sided)")
t_crit = 4.437  # t(0.999, 11 df)
for sd in (0.0156, 0.0197, 0.0211):
    print(f"  SD of paired seed-wise differences {sd:.4f}: smallest detectable gap {t_crit * sd / math.sqrt(12):.4f}")
print("  sign test over 12 seeds: P(>= 11 positive) = %.5f, P(12 positive) = %.5f" % (
    sum(math.comb(12, k) for k in (11, 12)) / 2 ** 12, 1 / 2 ** 12))
