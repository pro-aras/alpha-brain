#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:25 +0400 — THE SELECTING WALK of PREREG-ACT-EFFECT §3.1: it applies the rule (R1, R2, R3 and the selection order) MECHANICALLY to the
# grid of (window n, live threshold t) on a Bernoulli world model, with FRESH seeds (base 20261004), and CONFIRMS the selected configuration on the full 7-act chain.
# No game, no reward, no success is measured. Written and committed BEFORE it runs; the rule is the PREREG's text, quoted in `RULE` below.
#   R1  a live act is not starved: for a live act of true change rate 0.55, 0.592 and 0.64, the fraction of CHOICES judged DEAD <= 2 %   (single-act chain; the full chain must agree within 0.5 pp)
#   R2  a no-op is not kept alive: a no-op of true rate 0.12 is judged LIVE <= 5 % of choices
#   R3  the reading window is clean: the startup's p99 (full chain; every act has >= n known outcomes) <= 240 acts
#   selection: the first configuration ordered by n ascending, then |t - 0.2| ascending, that meets R1-R3; none -> the law is REFUSED by its own arithmetic.
# Run: python3 docs/organism/act/orient/screen_select.py   (pure Python + numpy; ~3 CPU-min)
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import screen_markov as sm      # the same chain, the same sampling rates (0.3143 live, 0.0143 dead)

SEED = 20261004
GRID_N = (10, 15, 20, 30)
GRID_T = (0.15, 0.20, 0.25, 0.30)
FWD_RATES = (0.55, 0.592, 0.64)
NOOP_RATE = 0.12
R1_MAX_DEAD = 0.02
R2_MAX_LIVE = 0.05
R3_MAX_P99 = 240
CONFIRM_TOL = 0.005
RULE = "R1 forward-like dead-time <= 2 % at 0.55/0.592/0.64 | R2 a rate-0.12 no-op live <= 5 % | R3 startup p99 <= 240 | order: n asc, |t-0.2| asc"


def startup_p99(n, t, lives=2000, seed=SEED):
    """Full-chain startup: the act index by which every act has >= n known outcomes (the screen eliminates acts as they reach n, so it is shorter than uniform choice)."""
    from collections import deque
    k_live = int(np.ceil(t * n - 1e-12))
    rates = [1.0, 1.0, 0.592, 0.090, 0.071, 0.027, 0.0]
    rng = np.random.default_rng([seed, n, int(t * 1000), 3])
    out = []
    for _ in range(lives):
        wins = [deque(maxlen=n) for _ in range(7)]
        for i in range(5000):
            if all(len(w) >= n for w in wins):
                out.append(i)
                break
            live = sm.live_flags(wins, n, k_live)
            if rng.random() < sm.FLOOR:
                a = int(rng.integers(0, 7))
            else:
                idx = [j for j in range(7) if live[j]] or list(range(7))
                a = idx[int(rng.integers(0, len(idx)))]
            wins[a].append(1 if rng.random() < rates[a] else 0)
        else:
            out.append(5000)
    return float(np.percentile(out, 99)), float(np.mean(out))


def main():
    print("RULE:", RULE)
    rows = []
    for n in GRID_N:
        for t in GRID_T:
            dead = {p: 1.0 - sm.single_act_fraction(n, t, p, seed=SEED) for p in FWD_RATES}
            noop_live = sm.single_act_fraction(n, t, NOOP_RATE, lam_live=0.9 / 4 + sm.FLOOR / 7, seed=SEED)
            p99, mean = startup_p99(n, t)
            r1 = all(d <= R1_MAX_DEAD for d in dead.values())
            r2 = noop_live <= R2_MAX_LIVE
            r3 = p99 <= R3_MAX_P99
            row = {"n": n, "t": t, "forward_dead_fraction": {str(p): round(d, 4) for p, d in dead.items()}, "noop_0.12_live_fraction": round(noop_live, 4),
                   "startup_p99": p99, "startup_mean": round(mean, 1), "R1": r1, "R2": r2, "R3": r3, "all": r1 and r2 and r3}
            rows.append(row)
            print(json.dumps(row), flush=True)
    order = sorted(rows, key=lambda r: (r["n"], abs(r["t"] - 0.2)))
    chosen = next((r for r in order if r["all"]), None)
    out = {"rule": RULE, "seed": SEED, "grid": rows, "selected": None}
    if chosen is None:
        print("SELECTED: NONE — THE LAW IS REFUSED BY ITS OWN ARITHMETIC (v3 follows)")
    else:
        print(f"SELECTED: n = {chosen['n']}, t = {chosen['t']}")
        conf = []
        ok = True
        for fr in FWD_RATES:
            r = sm.part2(chosen["n"], chosen["t"], [1.0, 1.0, fr, 0.090, 0.071, 0.027, 0.0], lives=1000, seed=SEED, note="confirmation")
            single = chosen["forward_dead_fraction"][str(fr)]
            agree = abs(r["forward_dead_time_fraction"] - single) <= CONFIRM_TOL
            ok = ok and agree and r["forward_dead_time_fraction"] <= R1_MAX_DEAD
            r["single_act_chain_dead"] = single
            r["agrees_within_0.5pp"] = agree
            conf.append(r)
            print("CONFIRM", json.dumps(r), flush=True)
        out["selected"] = {"n": chosen["n"], "t": chosen["t"], "confirmed_on_full_chain": ok, "confirmation": conf}
        print("CONFIRMED on the full chain:" , ok)
    json.dump(out, open(HERE / "screen_select.json", "w"), indent=1)
    return 0 if (chosen is not None and out["selected"]["confirmed_on_full_chain"]) else 1


if __name__ == "__main__":
    sys.exit(main())
