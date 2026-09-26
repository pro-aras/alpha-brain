"""d_projection.py — the PRE-REGISTERED projection check on the rule library's searches (B1-PREREG §12, 2026-09-26).

edit: Claude (Opus 5.5), 2026-09-26 17:24 +0400 — D's number (tools/b1/d_budget.py → docs/brain/b1/stage-1/d-budget.json)
is set from prices measured at 50,000 candidates per sleep and a depth factor measured at ONE sleep; no probe measured
deep programs and late-sleep data together. This reads each running search's own cost.jsonl (the arm's milliseconds at
every SLEEP) and compares the cumulative cost with the budget file's `predicted_cum_cpu_s` at the same sleep.

The rule, declared before the runs: at every completed sleep k ≥ 4 of any search, r_k = actual ÷ predicted and the
projected total = r_k × the predicted total. If a projected total exceeds 24 CPU-hours, this EXITS 10 naming the search:
the seat stops that seed's searches (the records are kept, never deleted), re-prices with the measured r_k, and relaunches.
It also EXITS 0 at a checkpoint sleep (default 7, the first expensive one) so the seat reads the ratios once by hand.
It never touches a process. The poll reads files only. `arm_ms` is WALL time inside the arm: before anything stops, a
FIRE is confirmed against the search process's own CPU time (`ps -o cputime`), which is what the allowance counts —
a burst of other work beside the searches inflates wall, not CPU.

`python3 -m tools.b1.d_projection --budget docs/brain/b1/stage-1/d-budget.json --run-dir <runs/seed/D> [--run-dir …] [--checkpoint 7]`
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

LIMIT_S = 24 * 3600


def sleeps_ms(cost: Path):
    """[(k, seq, cumulative arm seconds)] for every SLEEP record so far."""
    out, k = [], 0
    if not cost.exists():
        return out
    for l in cost.read_text(errors="replace").splitlines():
        try:
            r = json.loads(l)
        except ValueError:
            continue           # a line being written
        if r.get("where") == "sleep":
            k += 1
            out.append((k, r["seq"], r["arm_ms"] / 1000.0))
    return out


def check(budget: dict, runs, checkpoint: int, seen: dict):
    pred = {int(k): v for k, v in budget["predicted_cum_cpu_s"].items()}
    total = budget["predicted_total_cpu_h"] * 3600.0
    lines, fire, reached = [], None, []
    for rd in runs:
        for k, seq, act in sleeps_ms(rd / "cost.jsonl"):
            if (rd, k) in seen or k < 4 or k not in pred:
                continue
            seen[(rd, k)] = True
            r = act / pred[k] if pred[k] > 0 else float("inf")
            proj = r * total
            lines.append(f"{time.strftime('%H:%M:%S')} {rd.parent.name}/{rd.name} sleep {k} (seq {seq}): actual {act/3600:.2f} h · "
                         f"predicted {pred[k]/3600:.2f} h · r {r:.3f} · projected total {proj/3600:.2f} CPU-h")
            if proj > LIMIT_S and fire is None:
                fire = f"{rd.parent.name}/{rd.name} at sleep {k}: projected {proj/3600:.2f} CPU-h > 24 — STOP, re-price with r={r:.3f}, relaunch"
            if k >= checkpoint:
                reached.append(f"{rd.parent.name}/{rd.name}")
    return lines, fire, reached


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", required=True)
    ap.add_argument("--run-dir", action="append", required=True)
    ap.add_argument("--checkpoint", type=int, default=7)
    ap.add_argument("--poll", type=int, default=60)
    ns = ap.parse_args(argv)
    budget = json.loads(Path(ns.budget).read_text())
    runs = [Path(p) for p in ns.run_dir]
    seen: dict = {}
    reached_all: set = set()
    while True:
        lines, fire, reached = check(budget, runs, ns.checkpoint, seen)
        for l in lines:
            print(l, flush=True)
        if fire:
            print(f"[d_projection] FIRE: {fire}", flush=True)
            return 10
        reached_all.update(reached)
        if len(reached_all) == len(runs):
            print(f"[d_projection] checkpoint sleep {ns.checkpoint} reached by every search; ratios above — read them by hand", flush=True)
            return 0
        time.sleep(ns.poll)


if __name__ == "__main__":
    sys.exit(main())
