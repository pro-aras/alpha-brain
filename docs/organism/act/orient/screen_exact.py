#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:28 +0400 — THE EXACT INSTRUMENT for PREREG-ACT-EFFECT §3.1 (AMENDMENT 1, before signature). The selecting walk of 11:25
# (screen_select.py, Monte Carlo) selected (15, 0.15) and then FAILED its own confirmation clause (|single-act chain 1.34 % - full chain 0.69 %| = 0.65 pp at forward 0.592 > 0.5 pp):
# the clause was tighter than the estimator's noise (a dead-time fraction with dwell times of ~10^2 choices has a standard error of several tenths of a point). The rule's
# THRESHOLDS are unchanged (R1 <= 2 %, R2 <= 5 %, R3 <= 240, order n asc then |t - 0.2| asc); only the INSTRUMENT changes, from simulated to EXACT:
#   At the instants an act is sampled its window holds its last n outcomes, which are iid Bernoulli(p) whatever the sampling times, so the state seen at a sample is distributed
#   as the product measure: P(dead) = P_d = P(Bin(n, p) < k) per SAMPLE. After a sample the act waits a geometric number of choices (mean 1/lambda) for the next one,
#   lambda_a if it is live, lambda_d if dead (the landed floor alone, 0.1/7). Renewal-reward: the fraction of CHOICES spent dead = (P_d / lambda_d) / (P_d / lambda_d + (1 - P_d) / lambda_a).
# Cross-checks: (1) the closed form against replicated single-act simulations (agreement within 3 standard errors of the replicates); (2) THE PLANT: v1's reasoning
# (the per-evaluation share P_d read as a time fraction) must be CAUGHT as wrong against the simulation at (n = 10, t = 0.3, p = 0.64).
# Run: python3 docs/organism/act/orient/screen_exact.py   (pure Python + numpy; < 1 CPU-min)
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import screen_markov as sm

FLOOR = 0.1
LAM_A3 = (1 - FLOOR) / 3 + FLOOR / 7        # a live act among three live acts
LAM_A4 = (1 - FLOOR) / 4 + FLOOR / 7        # a live act among four live acts (a no-op wrongly live)
LAM_D = FLOOR / 7                           # a dead act: the floor alone
GRID_N = (10, 15, 20, 30)
GRID_T = (0.15, 0.20, 0.25, 0.30)
FWD_RATES = (0.55, 0.592, 0.64)
NOOP_RATE = 0.12
R1_MAX_DEAD, R2_MAX_LIVE, R3_MAX_P99 = 0.02, 0.05, 240


def cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def k_of(n, t):
    return int(math.ceil(t * n - 1e-12))


def forward_dead_time(n, k, p):
    pd = cdf(k - 1, n, p)
    return (pd / LAM_D) / (pd / LAM_D + (1 - pd) / LAM_A3)


def noop_live_time(n, k, q):
    pl = 1 - cdf(k - 1, n, q)
    return (pl / LAM_A4) / (pl / LAM_A4 + (1 - pl) / LAM_D)


def main():
    out = {"instrument": "closed form (renewal-reward); thresholds unchanged from PREREG §3.1", "grid": [], "selected": None, "crosscheck": [], "plant": None}
    ok_all = True
    print("EXACT R1/R2 over the grid; R3 = the startup p99 of the full chain (Monte Carlo, far from the 240 limit on both sides)")
    p99s = {}
    for n in GRID_N:
        for t in GRID_T:
            k = k_of(n, t)
            if (n, k) not in p99s:
                p99s[(n, k)] = None
    for n in GRID_N:
        for t in GRID_T:
            k = k_of(n, t)
            dead = {p: forward_dead_time(n, k, p) for p in FWD_RATES}
            nl = noop_live_time(n, k, NOOP_RATE)
            if p99s[(n, k)] is None:
                import screen_select as ss
                p99s[(n, k)] = ss.startup_p99(n, t, lives=3000, seed=20261005)
            p99, mean = p99s[(n, k)]
            r1 = all(v <= R1_MAX_DEAD for v in dead.values()); r2 = nl <= R2_MAX_LIVE; r3 = p99 <= R3_MAX_P99
            row = {"n": n, "t": t, "k": k, "forward_dead_time": {str(p): round(v, 5) for p, v in dead.items()}, "noop_0.12_live_time": round(nl, 5),
                   "startup_p99": p99, "startup_mean": round(mean, 1), "R1": r1, "R2": r2, "R3": r3, "all": r1 and r2 and r3}
            out["grid"].append(row)
            print(json.dumps(row), flush=True)
    order = sorted(out["grid"], key=lambda r: (r["n"], abs(r["t"] - 0.2)))
    chosen = next((r for r in order if r["all"]), None)
    if chosen is None:
        print("SELECTED: NONE — the law is refused by its own arithmetic"); ok_all = False
    else:
        n, t, k = chosen["n"], chosen["t"], chosen["k"]
        out["selected"] = {"n": n, "t": t, "k": k}
        print(f"SELECTED (exact): n = {n}, t = {t} (live iff >= {k} changes of the last {n} known outcomes)")
        # M4's ceilings for the selected configuration (exact), per observed no-op rate
        noops = {"pickup": 0.090, "drop": 0.071, "toggle": 0.027, "done": 0.0}
        nl = {a: noop_live_time(n, k, q) for a, q in noops.items()}
        out["selected"]["M4a_ceiling_mean_noops_dead"] = round(1 - sum(nl.values()) / 4, 5)
        out["selected"]["noop_live_time"] = {a: round(v, 5) for a, v in nl.items()}
        out["selected"]["M4b_ceiling_forward_live_time"] = {str(p): round(1 - forward_dead_time(n, k, p), 5) for p in (0.50, 0.55, 0.592, 0.64)}
        print("  M4(a) ceiling (mean fraction of the four no-ops judged dead):", out["selected"]["M4a_ceiling_mean_noops_dead"], "per-act live time", out["selected"]["noop_live_time"])
        print("  M4(b) ceiling (forward judged live), by true rate:", out["selected"]["M4b_ceiling_forward_live_time"])
    # cross-check 1: the closed form against replicated single-act simulations
    for (n, t, p) in ((20, 0.2, 0.50), (20, 0.2, 0.55), (15, 0.15, 0.55), (10, 0.3, 0.64)):
        k = k_of(n, t)
        reps = [1.0 - sm.single_act_fraction(n, t, p, choices=300_000, seed=700 + r) for r in range(8)]
        m, se = float(np.mean(reps)), float(np.std(reps, ddof=1) / math.sqrt(len(reps)))
        ex = forward_dead_time(n, k, p)
        agree = abs(m - ex) <= 3 * se + 0.002
        ok_all = ok_all and agree
        row = {"n": n, "t": t, "p": p, "exact": round(ex, 5), "simulated_mean": round(m, 5), "se_of_replicates": round(se, 5), "agree_within_3se": agree}
        out["crosscheck"].append(row)
        print("CROSSCHECK", json.dumps(row), flush=True)
    # cross-check 2 — THE PLANT: v1's per-evaluation share read as a time fraction must be CAUGHT
    n, t, p = 10, 0.3, 0.64
    k = k_of(n, t)
    wrong = cdf(k - 1, n, p)                         # v1's «0.6 %»: per evaluation, not per choice
    reps = [1.0 - sm.single_act_fraction(n, t, p, choices=300_000, seed=900 + r) for r in range(8)]
    sim = float(np.mean(reps))
    caught = abs(wrong - sim) > 0.03
    out["plant"] = {"v1_per_evaluation_share": round(wrong, 5), "simulated_time_fraction": round(sim, 5), "exact": round(forward_dead_time(n, k, p), 5), "caught": caught,
                    "asserts_changed": wrong != forward_dead_time(n, k, p)}
    ok_all = ok_all and caught and out["plant"]["asserts_changed"]
    print("PLANT (v1's per-evaluation share as a time fraction):", json.dumps(out["plant"]), "->", "CAUGHT" if caught else "MISSED")
    json.dump(out, open(HERE / "screen_exact.json", "w"), indent=1)
    print("RESULT:", "OK" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
