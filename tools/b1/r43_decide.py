"""r43_decide.py — R42's SECOND fire as R43 reads it (SEAT-DECISIONS R43, declared 2026-09-27 04:20 +0400, before any second fire).

edit: Claude (Opus 5.5), 2026-09-27 09:58 +0400 — after a LOWER-BOUND fire (the watch's exit 10 while a twin is inside sleep k), each twin is read on
its own: cpu ÷ pred_k can only grow until the sleep closes, so once it exceeds FLOOR_R (216,000 ÷ 50,000 = 4.32) the re-price
would fall below the floor whatever the close — the twin stops, VOID by cost. A close reads r_k = CPU at the close ÷ pred_k:
r ≤ FLOOR_R re-prices the shared number to ⌊216,000 ÷ r⌋ rounded down to a thousand (≥ 50,000); r > FLOOR_R is VOID. Before
either, WAIT. `watch()` polls a live twin with d_projection's own clock and closed-sleep reader.
`python -m tools.b1.r43_decide --budget docs/brain/b1/stage-1/d-budget.json --run-dir runs/<seed>/SHUFFLED-RELATION_D [...]`
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Dict, Optional

from tools.b1 import d_projection as P

N_NOW = 216_000
FLOOR_N = 50_000
FLOOR_R = N_NOW / FLOOR_N                       # 4.32
TOTAL_H = 5.89                                  # the scaled curve's total as the watch reads it (d-budget.json predicted_total_cpu_h)
FIRE_R = 24.0 / TOTAL_H                         # 4.0747 — the watch's fire line as a ratio


def decide(cpu_h: float, pred_k_h: float, closed_cpu_h: Optional[float]) -> Dict[str, object]:
    if closed_cpu_h is not None:
        r = closed_cpu_h / pred_k_h
        if r > FLOOR_R:
            return {"action": "VOID", "r": r, "why": f"closed at r {r:.4f} > {FLOOR_R}: the re-price falls below the floor"}
        n_new = int(math.floor(N_NOW / r / 1000.0)) * 1000
        return {"action": "REPRICE", "r": r, "n_new": n_new, "why": f"closed at r {r:.4f} ≤ {FLOOR_R}: N' = {n_new:,}"}
    lb = cpu_h / pred_k_h
    if lb > FLOOR_R:
        return {"action": "VOID", "r": lb, "why": f"the lower bound {lb:.4f} > {FLOOR_R} before the close: below the floor whatever the close"}
    return {"action": "WAIT", "r": lb, "why": f"the lower bound {lb:.4f} ≤ {FLOOR_R}; the sleep is still open"}


def watch(budget: dict, run_dirs, poll_s: float = 30.0) -> Dict[str, dict]:
    pred = {int(k): float(v) / 3600.0 for k, v in budget["predicted_cum_cpu_s"].items()}
    out: Dict[str, dict] = {}
    open_k = {}
    for d in run_dirs:
        s = P.Search(Path(d), P.find_pid(Path(d)))
        open_k[s.label] = (s, len(P.closed_sleeps(s.run_dir)) + 1)
    while len(out) < len(open_k):
        now = time.time()
        for label, (s, k) in open_k.items():
            if label in out:
                continue
            pt = P.proc_times(s.pid) if s.pid is not None else None
            if pt is not None:
                s.start = pt[0]
                s.samples.append((now, pt[1]))
            closed = dict(P.closed_sleeps(s.run_dir))
            if k in closed and s.samples:
                cpu_close, how = s.cpu_at(closed[k])
                d = decide(cpu_h=cpu_close / 3600.0, pred_k_h=pred[k], closed_cpu_h=cpu_close / 3600.0)
                d.update({"sleep": k, "clock": how})
            elif pt is None:
                d = {"action": "DEAD", "why": f"the process {s.pid} is gone with sleep {k} open"}
            else:
                d = decide(cpu_h=pt[1] / 3600.0, pred_k_h=pred[k], closed_cpu_h=None)
                d["sleep"] = k
            print(f"[r43] {time.strftime('%H:%M:%S')} {label}: sleep {k} · {d['action']} · {d['why']}", flush=True)
            if d["action"] != "WAIT":
                out[label] = d
        if len(out) < len(open_k):
            time.sleep(poll_s)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", required=True)
    ap.add_argument("--run-dir", action="append", required=True)
    ap.add_argument("--poll", type=float, default=30.0)
    ns = ap.parse_args(argv)
    res = watch(json.loads(Path(ns.budget).read_text()), ns.run_dir, ns.poll)
    print(json.dumps(res, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
