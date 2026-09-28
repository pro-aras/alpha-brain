"""d_budget.py — the rule library's candidates per sleep, by B1-PREREG §4 row D's formula, from prices MEASURED on the tape.

edit: Claude (Opus 5.5), 2026-09-26 17:24 +0400 — the §12 line of 12:08 omitted D's number (the graded run of 13:03 ran the
arm's toy default, 2,000). The signed probe's 0.0028 s per candidate was a 100-candidate sample: startup, not the price.
Measured on the real tape the price moves by sleep and by depth (0.27 ms at sleep 3 → 6.6 ms at sleep 7 at 50,000 per
sleep; ×2.38 at sleep 3 going 50,000 → 841,038). So the formula is applied per sleep:

    candidates per sleep = ⌊ MARGIN × 24 CPU-h ÷ ( f × Σ_s p_s ) ⌋        (Σ over the sleeps that search)

which is the PREREG's ⌊24 CPU-h ÷ price ÷ sleeps⌋ with price = the mean per-sleep price (a mean over sleeps × the number
of sleeps = the sum). A sleep that spent < 90 % of the probe's budget (nothing new for most cues) is a FIXED cost, its
measured seconds, whatever N — and is taken off the allowance before the division.
edit: Claude (Opus 5.5), 2026-09-26 17:30 +0400 — partial-spend sleeps as a fixed cost (sleep 10 spent 10 at 50,000). p_s = the 50,000-per-sleep probe's measured seconds per candidate where measured; beyond the last
measured sleep m, p_s = p_m × toy_s / toy_m, the SHAPE of the graded toy run's own per-sleep price (its arm-ms per sleep ÷
its candidates; a sleep the toy barely searched, spent < 100, is priced like the next sleep it searched — conservative). f = the depth factor measured
at sleep 3 (the larger of the two 50,000 readings' ratios — conservative). MARGIN 0.8 because the late prices are
projected, not measured; the pre-registered projection check (tools/b1/d_projection.py) holds the total under 24 CPU-h.

`python3 -m tools.b1.d_budget --shallow-log <price_d log> --depth docs/brain/b1/stage-1/d-price-s3-1M.json
   --shallow3 docs/brain/b1/stage-1/d-price.json --toy-run <toy D dir> --out docs/brain/b1/stage-1/d-budget.json`
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BUDGET_S = 24 * 3600
MARGIN = 0.8
LINE = re.compile(r"^\[price_d\] sleep (\d+) at seq (\d+): ([0-9.]+) s, spent (\d+)$")


def shallow_prices(log: Path) -> dict:
    out = {}
    for l in log.read_text(errors="replace").splitlines():
        m = LINE.match(l.strip())
        if m and float(m.group(3)) > 0:
            sp = int(m.group(4))
            out[int(m.group(1))] = {"seq": int(m.group(2)), "wall_s": float(m.group(3)), "spent": sp,
                                    "p": float(m.group(3)) / max(sp, 1)}
    return out


def toy_prices(toy_dir: Path) -> dict:
    cost = [json.loads(l) for l in (toy_dir / "cost.jsonl").read_text().splitlines() if l.strip()]
    lib = [json.loads(l) for l in (toy_dir / "arm" / "library_log.jsonl").read_text().splitlines() if l.strip()]
    spent = {r["sleep"]: sum(int(c.get("spent") or 0) for c in r["cues"]) for r in lib}
    out, prev_ms, k = {}, 0.0, 0
    for r in cost:
        if r["where"] == "sleep":
            k += 1
            d_ms = r["arm_ms"] - prev_ms
            sp = spent.get(k, 0)
            if sp > 0 or d_ms > 100:
                out[k] = {"seq": r["seq"], "ms": round(d_ms, 1), "spent": sp, "p": d_ms / 1000.0 / max(sp, 1)}
        prev_ms = r["arm_ms"]
    # a sleep the toy barely searched (spent < 100: every cue perfect or unchanged) is priced like the NEXT sleep the toy
    # searched in full — the graded run may search there (conservative: it can only raise the sum)
    keys = sorted(out)
    for i, k in enumerate(keys):
        if out[k]["spent"] < 100:
            nxt = [j for j in keys[i + 1:] if out[j]["spent"] >= 100] or [j for j in reversed(keys[:i]) if out[j]["spent"] >= 100]
            out[k]["p"] = out[nxt[0]]["p"]
            out[k]["priced_as"] = nxt[0]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shallow-log", required=True)
    ap.add_argument("--depth", required=True)
    ap.add_argument("--shallow3", required=True)
    ap.add_argument("--toy-run", required=True)
    ap.add_argument("--sleeps", type=int, default=17)
    ap.add_argument("--probe-budget", type=int, default=50000)
    ap.add_argument("--out", required=True)
    ns = ap.parse_args(argv)
    sh = shallow_prices(Path(ns.shallow_log))
    toy = toy_prices(Path(ns.toy_run))
    deep = json.loads(Path(ns.depth).read_text())
    s3 = json.loads(Path(ns.shallow3).read_text())
    d3 = next(s for s in deep["sleeps"] if s["spent"])
    p3_deep = d3["wall_s"] / d3["spent"]
    p3_shallow = [x["wall_s"] / x["spent"] for x in s3["sleeps"] if x["spent"]][0]
    if 3 in sh:
        p3_shallow = min(p3_shallow, sh[3]["p"])        # the smaller shallow reading → the larger factor
    f = p3_deep / p3_shallow
    m = max(sh)
    full_m = max(k for k, v in sh.items() if v["spent"] >= 0.9 * ns.probe_budget)
    per_sleep = {}
    for s in range(1, ns.sleeps + 1):
        if s in sh and sh[s]["spent"] >= 0.9 * ns.probe_budget:
            per_sleep[s] = {"p": sh[s]["p"], "source": "measured at 50,000 (full spend)"}
        elif s in sh:
            # nothing new for most cues: the sleep spent little at 50,000 and costs its fixed overhead (rescoring,
            # compression) whatever the budget — «nothing new since its last search» does not depend on N
            per_sleep[s] = {"fixed_s": sh[s]["wall_s"], "source": f"measured at 50,000: spent {sh[s]['spent']} — a fixed cost"}
        elif s > m and s in toy and full_m in toy:
            per_sleep[s] = {"p": sh[full_m]["p"] * toy[s]["p"] / toy[full_m]["p"],
                            "source": f"projected: p_{full_m} × toy_{s}/toy_{full_m}"}
    total_p = sum(v.get("p", 0.0) for v in per_sleep.values())
    fixed = sum(v.get("fixed_s", 0.0) for v in per_sleep.values())
    n = int((MARGIN * BUDGET_S - fixed) / (f * total_p)) // 1000 * 1000
    cum, pred = 0.0, {}
    for s in sorted(per_sleep):
        cum += f * n * per_sleep[s].get("p", 0.0) + per_sleep[s].get("fixed_s", 0.0)
        pred[s] = round(cum, 1)
    out = {"candidates_per_sleep": n, "margin": MARGIN, "budget_cpu_s": BUDGET_S, "depth_factor": round(f, 4),
           "depth_probe": {"p_deep": p3_deep, "spent": d3["spent"], "p_shallow": p3_shallow},
           "per_sleep": {str(k): {kk: (round(vv, 7) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in sorted(per_sleep.items())},
           "sum_p": round(total_p, 6), "fixed_s": round(fixed, 2), "predicted_cum_cpu_s": {str(k): v for k, v in pred.items()},
           "predicted_total_cpu_h": round(cum / 3600, 2), "last_measured_sleep": m,
           "letter_of_the_signed_probe": {"p": 0.0028, "candidates_per_sleep": int(BUDGET_S / 0.0028 / ns.sleeps)},
           "toy": {str(k): v for k, v in toy.items()}, "shallow": {str(k): v for k, v in sh.items()}}
    Path(ns.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"[d_budget] f={f:.3f} sum_p={total_p:.5f} s → candidates per sleep {n:,} (margin {MARGIN}); predicted total "
          f"{cum/3600:.2f} CPU-h; the signed probe's letter would be {out['letter_of_the_signed_probe']['candidates_per_sleep']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
