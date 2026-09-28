"""d_reprice.py — B1-PREREG §12's projection rule, its consequence: «that seed's searches stop, the records are kept, the number is
re-priced with the measured ratio, and they relaunch».

edit: Claude (Opus 5.5), 2026-09-26 19:31 +0400 — the rule fired at 19:29 on 2026-09-26 for SHUFFLED-RELATION:D (the twin search, which runs
at D's number by R36/R37): its sleep 5 alone projected past 24 CPU-h. The re-price is the rule's own arithmetic, nothing new:
N' = ⌊N ÷ r⌋ rounded down to a thousand (d_budget's rounding), where r is the LARGEST measured ratio among the searches that
fired. The predicted curve scales by N'/N (the price model is per candidate), so the 0.8 margin d_budget built in is kept: the
search that fired is predicted at ≈ the old total again. The old budget and the reading that fired are kept inside the new file.
A re-price only LOWERS the number (r > 1); anything else is refused.

`python3 -m tools.b1.d_reprice --budget docs/brain/b1/stage-1/d-budget.json --ratio 1.35 --fired "20261001/SHUFFLED-RELATION_D"
    --sleep 5 --cpu-h 1.80 --at "2026-09-26 19:4x +0400" --out docs/brain/b1/stage-1/d-budget.json`
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def reprice(budget: Dict[str, Any], ratio: float, reading: Dict[str, Any]) -> Dict[str, Any]:
    if not ratio > 1.0:
        raise ValueError(f"a re-price only lowers the number: ratio {ratio} ≤ 1")
    n = int(budget["candidates_per_sleep"])
    n_new = int(n / ratio) // 1000 * 1000
    scale = n_new / n
    out = dict(budget)
    out["candidates_per_sleep"] = n_new
    out["predicted_cum_cpu_s"] = {k: round(float(v) * scale, 1) for k, v in budget["predicted_cum_cpu_s"].items()}
    out["predicted_total_cpu_h"] = round(float(budget["predicted_total_cpu_h"]) * scale, 2)
    prev = {k: budget[k] for k in ("candidates_per_sleep", "predicted_total_cpu_h", "predicted_cum_cpu_s")}
    out["repriced"] = list(budget.get("repriced", [])) + [{"from": prev, "ratio": ratio, "reading": dict(reading),
                                                           "rule": "B1-PREREG §12 (2026-09-26 17:48): N' = floor(N / r), "
                                                                   "rounded down to 1,000; the curve scales by N'/N"}]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", required=True)
    ap.add_argument("--ratio", type=float, required=True)
    ap.add_argument("--fired", required=True)
    ap.add_argument("--sleep", type=int, required=True)
    ap.add_argument("--cpu-h", type=float, required=True)
    ap.add_argument("--at", required=True)
    ap.add_argument("--out", required=True)
    ns = ap.parse_args(argv)
    b = json.loads(Path(ns.budget).read_text())
    new = reprice(b, ns.ratio, {"search": ns.fired, "sleep": ns.sleep, "cpu_h": ns.cpu_h, "at": ns.at})
    Path(ns.out).write_text(json.dumps(new, indent=1, sort_keys=True) + "\n")
    print(f"[d_reprice] {b['candidates_per_sleep']:,} → {new['candidates_per_sleep']:,} candidates per sleep (r = {ns.ratio}); "
          f"predicted {b['predicted_total_cpu_h']} → {new['predicted_total_cpu_h']} CPU-h at D's own price")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
