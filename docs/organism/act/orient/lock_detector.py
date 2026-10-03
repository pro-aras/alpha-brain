#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:33 +0400 — THE LOCK DETECTOR'S CEILINGS (PREREG-ACT-EFFECT AMENDMENT 2, before any candidate ran): pure SAMPLING arithmetic over FIXED
# act mixtures — no environment, no chooser, no success measured. It prices the detectors M2 may use, from the mixtures the bench's arms are known to play:
#   top-1: the largest share ONE act holds in any 100-act window after act 120 (v2.1's detector, threshold 0.8);
#   top-2: the largest share the best TWO acts hold together in any such window (AMENDMENT 2's detector, threshold 0.9).
# WHY: argmax on raw change (K-ARGMAX) breaks the left/right tie (both change the frame every time) AT RANDOM, so it alternates between the two turns and no single act passes
# ~0.5: v2.1's single-act detector would have MISSED the very plant it exists to catch. A turn-spin holds two acts, not one.
# AMENDMENT 2 also prices the PERSISTENT form: a life passes when <= 2 % of its 100-act windows have top-2 >= 0.9 (lock_walk.py prices the candidate's own transients).
# Run: python3 docs/organism/act/orient/lock_detector.py   (numpy only; < 1 CPU-min)
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FLOOR = 0.1
U = FLOOR / 7
MIX = {
    "R-NULL (uniform 7)": [1 / 7] * 7,
    "R-3 (uniform over l,r,f)": [1 / 3, 1 / 3, 1 / 3, 0, 0, 0, 0],
    "R-SCR (the candidate's stationary mixture)": [0.9 / 3 + U] * 3 + [U] * 4,
    "R-CEIL (forward .5, left=right=.25)": [0.25, 0.25, 0.5, 0, 0, 0, 0],
    "iv-0.7 (forward .7)": [0.15, 0.15, 0.7, 0, 0, 0, 0],
    "K-ARGMAX-like (left, right tied; floor 0.1)": [0.9 / 2 + U, 0.9 / 2 + U] + [U] * 5,
    "P-OLD-like (one act locked; floor 0.1)": [0.9 + U] + [U] * 6,
}
THRESH_TOP1, THRESH_TOP2 = 0.8, 0.9


def lives(probs, horizon, n_lives, seed):
    rng = np.random.default_rng(seed)
    p = np.array(probs, dtype=float)
    p = p / p.sum()
    top1 = np.zeros(n_lives)
    top2 = np.zeros(n_lives)
    frac2 = np.zeros(n_lives)
    for start in range(0, n_lives, 100):
        m = min(100, n_lives - start)
        draws = rng.choice(7, size=(m, horizon), p=p)
        onehot = np.zeros((m, horizon + 1, 7), dtype=np.int32)
        onehot[np.arange(m)[:, None], np.arange(1, horizon + 1)[None, :], draws] = 1
        cs = np.cumsum(onehot, axis=1)
        lo = 120
        win = cs[:, lo + 100: horizon + 1, :] - cs[:, lo: horizon + 1 - 100, :]       # all 100-act windows starting at act >= 120
        srt = np.sort(win, axis=2)
        top1[start:start + m] = srt[:, :, -1].max(axis=1) / 100.0
        top2[start:start + m] = (srt[:, :, -1] + srt[:, :, -2]).max(axis=1) / 100.0
        frac2[start:start + m] = ((srt[:, :, -1] + srt[:, :, -2]) >= 90).mean(axis=1)     # the share of windows with top-2 >= 0.9
    return top1, top2, frac2


def main():
    out = {}
    print(f"thresholds: top-1 >= {THRESH_TOP1} (v2.1), top-2 >= {THRESH_TOP2} (AMENDMENT 2); 100-act windows from act 120; 600 lives per cell")
    for horizon in (960, 4920):
        print(f"== horizon {horizon} acts")
        for name, probs in MIX.items():
            t1, t2, f2 = lives(probs, horizon, 600, seed=20261006 + horizon)
            row = {"top1_p5_p50_p95_max": [round(float(np.percentile(t1, q)), 3) for q in (5, 50, 95, 100)],
                   "top2_p5_p50_p95_max": [round(float(np.percentile(t2, q)), 3) for q in (5, 50, 95, 100)],
                   "flagged_by_top1_ge_0.8": round(float((t1 >= THRESH_TOP1).mean()), 3),
                   "flagged_by_top2_ge_0.9": round(float((t2 >= THRESH_TOP2).mean()), 3),
                   "pass_share(<=2% of windows top2>=0.9)": round(float((f2 <= 0.02).mean()), 3)}
            out[f"{horizon}|{name}"] = row
            print(f"  {name:48s} top1 {row['top1_p5_p50_p95_max']}  top2 {row['top2_p5_p50_p95_max']}  flagged top1>=.8: {row['flagged_by_top1_ge_0.8']:.3f}  top2>=.9: {row['flagged_by_top2_ge_0.9']:.3f}  PASS(<=2% windows): {row['pass_share(<=2% of windows top2>=0.9)']:.3f}", flush=True)
    json.dump(out, open(HERE / "lock_detector.json", "w"), indent=1)


if __name__ == "__main__":
    main()
