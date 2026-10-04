#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:34 +0400 — THE LOCK WALK (PREREG-ACT-EFFECT AMENDMENT 2, before any candidate ran on the game): the candidate's OWN dynamics on the Bernoulli
# world model (no game, no reward, no success), priced against the lock detector. When `forward` is wrongly judged DEAD the screen plays left/right only for ~10^2 choices, a TRANSIENT
# two-act collapse; a «any window ever ≥ 0.9» test would flag such lives, but a lock is a PERSISTENT state. So the detector is the SHARE OF 100-ACT WINDOWS (after act 120) in which
# two acts together hold >= 0.90, and a life passes when that share is <= 2 %. Per forward rate (0.55, 0.592, 0.64) and horizon (960, 4,920 acts): the fraction of lives that pass.
# Run: python3 docs/organism/act/orient/lock_walk.py   (pure Python + numpy; ~2 CPU-min)
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import screen_markov as sm

N_WIN, T_LIVE = 20, 0.2
K_LIVE = int(np.ceil(T_LIVE * N_WIN - 1e-12))


def one_life_acts(rng, acts, rates):
    wins = [deque(maxlen=N_WIN) for _ in range(7)]
    seq = np.zeros(acts, dtype=np.int8)
    for i in range(acts):
        live = sm.live_flags(wins, N_WIN, K_LIVE)
        if rng.random() < sm.FLOOR:
            a = int(rng.integers(0, 7))
        else:
            idx = [j for j in range(7) if live[j]] or list(range(7))
            a = idx[int(rng.integers(0, len(idx)))]
        wins[a].append(1 if rng.random() < rates[a] else 0)
        seq[i] = a
    return seq


def window_stats(seq):
    """Per life: the share of 100-act windows (starting at act >= 120) with top-2 >= 0.9, the same for top-1 >= 0.8, and the maxima."""
    h = len(seq)
    onehot = np.zeros((h + 1, 7), dtype=np.int32)
    onehot[np.arange(1, h + 1), seq] = 1
    cs = np.cumsum(onehot, axis=0)
    win = cs[120 + 100:h + 1] - cs[120:h + 1 - 100]
    srt = np.sort(win, axis=1)
    t1 = srt[:, -1] / 100.0
    t2 = (srt[:, -1] + srt[:, -2]) / 100.0
    return float((t2 >= 0.9).mean()), float((t1 >= 0.8).mean()), float(t1.max()), float(t2.max())


def main():
    out = {}
    print(f"candidate C-SCR (window {N_WIN}, live iff >= {K_LIVE} changes) on the Bernoulli world model; 400 lives per cell; a life PASSES if <= 2 % of its 100-act windows have top-2 >= 0.9")
    for fr in (0.55, 0.592, 0.64):
        rates = [1.0, 1.0, fr, 0.090, 0.071, 0.027, 0.0]
        for horizon in (960, 4920):
            rng = np.random.default_rng([20261007, int(fr * 1000), horizon])
            frac2, frac1, max1, max2 = [], [], [], []
            for _ in range(400):
                f2, f1, m1, m2 = window_stats(one_life_acts(rng, horizon, rates))
                frac2.append(f2); frac1.append(f1); max1.append(m1); max2.append(m2)
            frac2 = np.array(frac2)
            row = {"forward_rate": fr, "horizon": horizon,
                   "pass_share(<=2% windows top2>=0.9)": round(float((frac2 <= 0.02).mean()), 4),
                   "any_window_top2>=0.9 (v2.1-style any-window test)": round(float((np.array(max2) >= 0.9).mean()), 4),
                   "windows_flagged_share_p50_p95_max": [round(float(np.percentile(frac2, q)), 4) for q in (50, 95, 100)],
                   "max_top1_p50_p95_max": [round(float(np.percentile(max1, q)), 3) for q in (50, 95, 100)],
                   "max_top2_p50_p95_max": [round(float(np.percentile(max2, q)), 3) for q in (50, 95, 100)]}
            out[f"{fr}|{horizon}"] = row
            print(json.dumps(row), flush=True)
    json.dump(out, open(HERE / "lock_walk.json", "w"), indent=1)


if __name__ == "__main__":
    main()
