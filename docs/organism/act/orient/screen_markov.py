#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:18 +0400 — AN ARITHMETIC WALK, not a bench run (PREREG-ACT-EFFECT §8 and its AMENDMENT BEFORE SIGNATURE): the
# screen's STATIONARY behaviour on a Bernoulli WORLD MODEL built from the orientation probe's per-act change rates (no game, no reward, no success measured).
# It exists because the first draft (window 10, live iff rate >= 0.3) gave misclassification per EVALUATION and hid the time spent misclassified: a DEAD act
# is drawn only by the floor (0.1/7 = 1.43 % a choice), 22x rarer than a live one, so a wrongly-dead `forward` stays dead for ~10^2 choices (12.7 % of ALL
# choices at n = 10; ~10 % even at n = 20 when forward's rate is 0.55, as the live tape read 0.592). The window n and the threshold t are chosen by the RULE
# declared in the PREREG (§3), never from success.
#   PART 1  one act in isolation (its window as a Markov chain driven by its own sampling rate): the fraction of CHOICES spent judged DEAD (for a live act)
#           or judged LIVE (for a no-op), over a grid of (n, t) and of the act's true rate;
#   PART 2  the full 7-act chain for the shortlisted configurations: startup, shares, M4's quantities.
# Run: python3 docs/organism/act/orient/screen_markov.py   (pure Python + numpy; ~2 CPU-min)
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P2 = json.loads((HERE / "probe_world_facts2.json").read_text())["per_act"]
ACTS = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]
RATES = [P2[a]["p_changed"] for a in ACTS]
FLOOR = 0.1
NOOPS = (3, 4, 5, 6)
LAM_LIVE = (1 - FLOOR) / 3 + FLOOR / 7     # a live act among 3 live acts: 0.3143 per choice
LAM_DEAD = FLOOR / 7                       # a dead act: the floor alone, 0.0143 per choice


def single_act_fraction(n, t, p, choices=400_000, seed=1, lam_live=LAM_LIVE, lam_dead=LAM_DEAD, start_live=True):
    """Fraction of CHOICES during which an act with true change rate p is judged LIVE (window n known outcomes, live iff mean >= t; < n outcomes -> live)."""
    rng = np.random.default_rng([seed, n, int(t * 1000), int(p * 1000)])
    k_live = int(np.ceil(t * n - 1e-12))       # live iff changes >= k_live
    win = deque(maxlen=n)
    live_choices = 0
    u = rng.random(choices)
    o = rng.random(choices)
    for i in range(choices):
        live = True if len(win) < n else (sum(win) >= k_live)
        live_choices += live
        if u[i] < (lam_live if live else lam_dead):
            win.append(1 if o[i] < p else 0)
    return live_choices / choices


def part1():
    rows = []
    print("PART 1 — fraction of CHOICES judged LIVE, one act in isolation (live act: want ~1; no-op: want ~0)")
    print(f"{'n':>3} {'t':>5} {'k':>3} | " + " ".join(f"fwd={p:.2f}" for p in (0.45, 0.50, 0.55, 0.60, 0.64, 0.70)) + " |  " + " ".join(f"noop={q:.2f}" for q in (0.05, 0.09, 0.12)))
    for n in (10, 15, 20, 30):
        for t in (0.15, 0.2, 0.25, 0.3):
            k = int(np.ceil(t * n - 1e-12))
            f = [single_act_fraction(n, t, p) for p in (0.45, 0.50, 0.55, 0.60, 0.64, 0.70)]
            q = [single_act_fraction(n, t, qq, lam_live=0.9 / 4 + FLOOR / 7) for qq in (0.05, 0.09, 0.12)]
            rows.append({"n": n, "t": t, "k": k, "forward_live_fraction": dict(zip(("0.45", "0.50", "0.55", "0.60", "0.64", "0.70"), f)),
                         "noop_live_fraction": dict(zip(("0.05", "0.09", "0.12"), q))})
            print(f"{n:3d} {t:5.2f} {k:3d} | " + " ".join(f"{x:8.4f}" for x in f) + " |  " + " ".join(f"{x:9.4f}" for x in q), flush=True)
    return rows


def live_flags(wins, n, k_live):
    return [True if len(w) < n else (sum(w) >= k_live) for w in wins]


def one_life(rng, n, t, acts, rates):
    k_live = int(np.ceil(t * n - 1e-12))
    wins = [deque(maxlen=n) for _ in range(7)]
    shares = np.zeros(7)
    dead_f = 0
    noop_dead = 0.0
    exact = 0
    startup = None
    for i in range(acts):
        live = live_flags(wins, n, k_live)
        if startup is None and all(len(w) >= n for w in wins):
            startup = i
        if rng.random() < FLOOR:
            a = int(rng.integers(0, 7))
        else:
            idx = [j for j in range(7) if live[j]] or list(range(7))
            a = idx[int(rng.integers(0, len(idx)))]
        wins[a].append(1 if rng.random() < rates[a] else 0)
        if i >= 300:
            shares[a] += 1
            dead_f += 0 if live[2] else 1
            noop_dead += sum(1 for j in NOOPS if not live[j]) / 4.0
            exact += 1 if (live[0] and live[1] and live[2] and not any(live[j] for j in NOOPS)) else 0
    return shares, dead_f, noop_dead, exact, startup


def part2(n, t, rates, lives=800, acts=1000, seed=20261003, note=""):
    rng = np.random.default_rng([seed, n, int(t * 1000)])
    shares = np.zeros(7)
    dead_f = noop_dead = exact = 0.0
    starts = []
    for _ in range(lives):
        s, d, nd, ex, st = one_life(rng, n, t, acts, rates)
        shares += s; dead_f += d; noop_dead += nd; exact += ex
        starts.append(st if st is not None else acts)
    denom = lives * (acts - 300)
    sh = shares / shares.sum()
    return {"n": n, "t": t, "note": note, "forward_rate": rates[2], "startup_mean": round(float(np.mean(starts)), 1),
            "startup_p99": float(np.percentile(starts, 99)),
            "share": {ACTS[i]: round(float(sh[i]), 4) for i in range(7)},
            "useful_share": round(float(sh[:3].sum()), 4), "noop_share": round(float(sh[3:].sum()), 4),
            "forward_dead_time_fraction": round(dead_f / denom, 4), "M4a_mean_noops_dead": round(noop_dead / denom, 4),
            "set_exact_fraction": round(exact / denom, 4)}


if __name__ == "__main__":
    print("world model: change rates", dict(zip(ACTS, RATES)), "floor", FLOOR)
    print(f"IDEAL stationary mixture (R-SCR): left=right=forward={(1 - FLOOR) / 3 + FLOOR / 7:.4f}, no-op total {4 * FLOOR / 7:.4f}")
    out = {"part1": part1(), "part2": []}
    print("PART 2 — the full chain (acts 300..999 read; 800 lives)")
    for (n, t, fr, note) in ((10, 0.3, 0.637, "first draft"), (20, 0.3, 0.55, "first draft's n=20 at forward 0.55"),
                              (20, 0.2, 0.637, ""), (20, 0.2, 0.55, ""), (20, 0.2, 0.50, ""), (15, 0.2, 0.55, ""), (30, 0.2, 0.55, "")):
        r = part2(n, t, [1.0, 1.0, fr, 0.090, 0.071, 0.027, 0.0], note=note)
        out["part2"].append(r)
        print(json.dumps(r), flush=True)
    json.dump(out, open(HERE / "screen_markov.json", "w"), indent=1)
