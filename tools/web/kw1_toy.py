#!/usr/bin/env python3
# edit: Claude (Opus 5.5, the seat), 2026-09-29 22:55 +0400 — PREREG-KW-1 §3.1 / §4.0 / §4.1 + AMENDMENT 1: THE TOY.
"""tools/web/kw1_toy.py --out <dir> — six rules × three worlds × ten seeds on the law's toy; writes <dir>/toy.json (every run's
numbers) and prints the gates G1–G3 on the toy and the marks K1–K5 with every seed.

The world (§3.1): V = 60 words w00…w59, Zipf(1) base frequencies; every word draws 2 associates (uniform among the others, no
repeat); the planted set P is their union, undirected; T = 20,000 words; the next word is one of the current word's associates
(uniform) with probability q, else a Zipf draw. POSITIVE q 0.3; NULL q 0; CHANGE q 0.3 with the associates redrawn at word
10,000 (P_old, P_new). World draws: numpy default_rng([world_seed, 7001]); a rule's seed = world_seed + 1,000."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from genome import web as Wb  # noqa: E402

V, T, Q = 60, 20000, 0.3
SEEDS = list(range(1, 11))
RULES = list(Wb.RULES)


def world(seed: int, q: float, change: bool):
    rng = np.random.default_rng([seed, 7001])
    zipf = 1.0 / np.arange(1, V + 1)
    zipf /= zipf.sum()

    def draw():
        a = {}
        for i in range(V):
            others = np.array([j for j in range(V) if j != i])
            a[i] = [int(x) for x in rng.choice(others, size=2, replace=False)]
        return a

    def pairs(a):
        return {tuple(sorted((f"w{i:02d}", f"w{j:02d}"))) for i, js in a.items() for j in js}

    A = draw()
    P_old, P_new = pairs(A), None
    cur = int(rng.choice(V, p=zipf))
    out = [cur]
    for t in range(1, T):
        if change and t == T // 2:
            A = draw()
            P_new = pairs(A)
        if q > 0 and rng.random() < q:
            cur = A[cur][int(rng.integers(2))]
        else:
            cur = int(rng.choice(V, p=zipf))
        out.append(cur)
    return [f"w{i:02d}" for i in out], P_old, P_new


def grow(rule: str, words, budget: int, seed: int):
    w = Wb.Web(rule, budget=None if rule == "H" else budget, seed=seed)
    peak = 0
    for x in words:
        w.hear(x)
        peak = max(peak, len(w.edges))
    return w, peak


def score(C, P):
    tp = len(C & P)
    return {"consolidated": len(C), "hit": tp, "recall": tp / len(P) if P else None,
            "precision": (tp / len(C)) if C else None}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def sign_test(pairs_):
    """exact two-sided sign test on paired differences (ties dropped)."""
    up = sum(1 for a, b in pairs_ if a > b)
    dn = sum(1 for a, b in pairs_ if a < b)
    n = up + dn
    if n == 0:
        return {"up": 0, "down": 0, "p": None}
    k = min(up, dn)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n)
    return {"up": up, "down": dn, "p": p}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    runs = []
    gates = {"G1": [], "G2": {}, "G3": []}
    for ws in SEEDS:
        for wname, q, change in (("POSITIVE", Q, False), ("NULL", 0.0, False), ("CHANGE", Q, True)):
            words, P_old, P_new = world(ws, q, change)
            Vd = len(set(words))
            B = 2 * Vd
            shuffled = None
            for rule in RULES:
                web, peak = grow(rule, words, B, ws + 1000)
                C = set(web.consolidated())
                row = {"world": wname, "seed": ws, "rule": rule, "V": Vd, "B": B, "peak_edges": peak,
                       "live_edges": len(web.edges), "stats": dict(web.stats)}
                if wname == "CHANGE":
                    row["old"] = score(C, P_old)
                    row["new"] = score(C, P_new)
                else:
                    row["planted"] = score(C, P_old)
                runs.append(row)
                if rule != "H":
                    gates["G3"].append(peak <= B)
                if wname == "POSITIVE" and ws == 1:
                    errs = Wb.recount_errors(web, words)
                    gates["G1"].append({"rule": rule, "errors": len(errs), "first": errs[:2]})
                    if rule == "S":
                        twin, _ = grow("S", words, B, ws + 1000)
                        other, _ = grow("S", words, B, ws + 1001)
                        gates["G2"] = {"same_seed_identical": twin.dumps() == web.dumps(),
                                       "other_seed_differs": other.dumps() != web.dumps()}
                        # the plant of G1: one count changed must be caught
                        k0 = next(iter(web.edges))
                        web.edges[k0]["c"] += 1
                        gates["G1_plant_caught"] = bool(Wb.recount_errors(web, words))
                        web.edges[k0]["c"] -= 1
                if wname == "POSITIVE" and rule == "S0":
                    if shuffled is None:
                        shuffled = list(np.random.default_rng([ws, 7003]).permutation(words))
                    web_sh, _ = grow("S0", shuffled, B, ws + 1000)
                    row["S0_on_shuffled"] = score(set(web_sh.consolidated()), P_old)
            print(f"[toy] seed {ws} {wname} done", flush=True)
    (out / "toy.json").write_text(json.dumps({"runs": runs, "gates": gates}, sort_keys=True, indent=1))

    def pick(world_, rule, field="planted", key="recall"):
        return [r[field][key] for r in runs if r["world"] == world_ and r["rule"] == rule]

    L = []
    L.append("# KW-1 · the toy (written by tools/web/kw1_toy.py)")
    L.append(f"G1 recount (POSITIVE, seed 1): {gates['G1']} · plant caught: {gates.get('G1_plant_caught')}")
    L.append(f"G2 determinism: {gates['G2']}")
    L.append(f"G3 budget held in every budgeted run: {all(gates['G3'])} ({len(gates['G3'])} runs)")
    L.append("")
    L.append("| rule | POSITIVE recall (mean) | POSITIVE precision (mean) | consolidated (mean) | NULL consolidated (mean) | CHANGE recall new | CHANGE recall old |")
    L.append("|---|---|---|---|---|---|---|")
    for rule in RULES:
        L.append(f"| {rule} | {mean(pick('POSITIVE', rule)):.3f} | {mean(pick('POSITIVE', rule, key='precision')) or 0:.3f} | "
                 f"{mean(pick('POSITIVE', rule, key='consolidated')):.1f} | {mean(pick('NULL', rule, key='consolidated')):.1f} | "
                 f"{mean(pick('CHANGE', rule, 'new')):.3f} | {mean(pick('CHANGE', rule, 'old')):.3f} |")
    L.append("")
    L.append("Per seed, POSITIVE recall: " + "; ".join(f"{r}: " + " ".join(f"{x:.2f}" for x in pick('POSITIVE', r)) for r in RULES))
    L.append("Per seed, NULL consolidated: " + "; ".join(f"{r}: " + " ".join(str(x) for x in pick('NULL', r, key='consolidated')) for r in RULES))
    h_rec, s_rec = mean(pick("POSITIVE", "H")), mean(pick("POSITIVE", "S"))
    h_pre, s_pre = mean(pick("POSITIVE", "H", key="precision")), mean(pick("POSITIVE", "S", key="precision"))
    k1 = (h_rec is not None and s_rec is not None and s_rec >= 0.8 * h_rec and s_pre is not None and h_pre is not None
          and s_pre >= h_pre - 0.05)
    L.append("")
    note = " (H's recall under 0.5: «the consolidation test cannot store this world», §6.1)" if h_rec is not None and h_rec < 0.5 else ""
    L.append(f"**K1 RANDOM GROWTH STORES:** S recall {s_rec:.3f} vs 0.8 × H {0.8 * h_rec:.3f}; S precision {s_pre:.3f} vs H − 0.05 "
             f"{h_pre - 0.05:.3f} → {'PASS' if k1 else 'FAIL'}{note}")
    h_null, s_null = mean(pick("NULL", "H", key="consolidated")), mean(pick("NULL", "S", key="consolidated"))
    L.append(f"**K2 NO INVENTION:** NULL world, S consolidated {s_null:.1f} vs H + 2 = {h_null + 2:.1f} → {'PASS' if s_null <= h_null + 2 else 'FAIL'}")
    s0 = mean(pick("POSITIVE", "S0"))
    bar3 = 3 * (2 * V) / (V * (V - 1) / 2)
    s0_sh = mean([r["S0_on_shuffled"]["recall"] for r in runs if r["world"] == "POSITIVE" and r["rule"] == "S0"])
    L.append(f"**K3 THE NULL IS BLIND:** S0 recall {s0:.3f} vs bar {bar3:.3f} → {'PASS' if s0 <= bar3 else 'FAIL'} · beside it, S0 on the "
             f"SHUFFLED toy stream: {s0_sh:.3f} (AMENDMENT 1's named leak)")
    for x, y in (("S", "L"), ("R", "S"), ("L", "F")):
        rec = sign_test(list(zip(pick("POSITIVE", x), pick("POSITIVE", y))))
        pre = sign_test(list(zip(pick("POSITIVE", x, key="precision"), pick("POSITIVE", y, key="precision"))))
        L.append(f"K4 reading, {x} vs {y}: recall {mean(pick('POSITIVE', x)):.3f} vs {mean(pick('POSITIVE', y)):.3f} (sign test {rec}); "
                 f"precision {mean(pick('POSITIVE', x, key='precision')) or 0:.3f} vs {mean(pick('POSITIVE', y, key='precision')) or 0:.3f} ({pre})")
    text = "\n".join(L) + "\n"
    (out / "TOY-READINGS.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
