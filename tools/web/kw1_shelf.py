#!/usr/bin/env python3
# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:00 +0400 — PREREG-KW-1 §3.2 / §4.0 / §4.2 + AMENDMENT 1: THE ORGANISM'S SHELF.
"""tools/web/kw1_shelf.py --out <dir> — the web grown from the words alpha4-1 HEARD from its shelf in its first 12 hours
(tape ear rows, source «shelf», seq <= 50,094, seq order): the first 60 % grows the web, the rest is the held-out truth.
Writes <dir>/shelf.json and <dir>/SHELF-READINGS.md; prints G1 and G3 on the shelf and K6–K8.

Enrichment of a web (K6) = Σ h_ab / Σ E'_ab over its consolidated edges whose two words both occur in the held-out part, with
h_ab its pair events there (the same window: the previous 3 DISTINCT words) and E'_ab = 2 · d · n'_a · n'_b / N'. K7 grows H and S
on the growth part SHUFFLED (numpy default_rng([1, 7002]).permutation) and reads them against the same held-out part."""
from __future__ import annotations

import argparse
import collections
import glob
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from genome import web as Wb  # noqa: E402

TAPE = "/data/dev/genome-lives/alpha4-1/tape"
CUT = 50094
D = 3
SEEDS = list(range(1, 11))


def heard_words(tape_dir: str = TAPE, cut: int = CUT) -> Tuple[List[str], int]:
    rows, bad = [], 0
    for f in sorted(glob.glob(f"{tape_dir}/*.jsonl")):
        with open(f, "rb") as fh:
            for raw in fh:
                if b'"sense": "ear"' not in raw:
                    continue
                try:
                    r = json.loads(raw.replace(b"\x00", b"").decode("utf-8"))
                except Exception:
                    bad += 1
                    continue
                m = r.get("meta") or {}
                if m.get("source") == "shelf" and int(r["seq"]) <= cut:
                    rows.append((int(r["seq"]), str(m["word"])))
    rows.sort()
    return [w for _s, w in rows], bad


def pair_counts(words: List[str], d: int = D) -> Dict[Tuple[str, str], int]:
    counts: Dict[Tuple[str, str], int] = collections.Counter()
    recent: List[str] = []
    for w in words:
        for u in recent:
            if u != w:
                counts[(u, w) if u < w else (w, u)] += 1
        recent = ([w] + [x for x in recent if x != w])[:d]
    return counts


def enrichment(C, h, n2, N2):
    num = den = 0.0
    used = 0
    for a, b in C:
        if a in n2 and b in n2:
            used += 1
            num += h.get((a, b), 0)
            den += 2 * D * n2[a] * n2[b] / N2
    return {"edges_used": used, "observed": num, "expected": den, "enrichment": (num / den if den > 0 else None)}


def graph_stats(C) -> Dict[str, object]:
    adj: Dict[str, set] = collections.defaultdict(set)
    for a, b in C:
        adj[a].add(b)
        adj[b].add(a)
    n, m = len(adj), len(C)
    if n < 3:
        return {"nodes": n, "edges": m}
    cl = []
    for v, nb in adj.items():
        k = len(nb)
        if k < 2:
            continue
        links = sum(1 for x in nb for y in nb if x < y and y in adj[x])
        cl.append(2 * links / (k * (k - 1)))
    # the largest component and its mean shortest path (BFS from every node)
    seen, comps = set(), []
    for v in adj:
        if v in seen:
            continue
        comp, stack = [], [v]
        seen.add(v)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(comp)
    big = max(comps, key=len)
    tot = cnt = 0
    for s in big:
        dist = {s: 0}
        q = collections.deque([s])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1
                    q.append(y)
        tot += sum(dist.values())
        cnt += len(dist) - 1
    degs = sorted((len(nb) for nb in adj.values()), reverse=True)
    kmean = 2 * m / n
    return {"nodes": n, "edges": m, "mean_degree": kmean, "max_degree": degs[0], "clustering": sum(cl) / len(cl) if cl else 0.0,
            "random_clustering": kmean / (n - 1), "largest_component": len(big), "mean_path": (tot / cnt if cnt else None),
            "random_path": (float(np.log(n) / np.log(kmean)) if kmean > 1 else None),
            "hubs": sorted(((len(nb), v) for v, nb in adj.items()), reverse=True)[:8]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    words, bad = heard_words()
    n_grow = int(0.6 * len(words))
    grow_w, held = words[:n_grow], words[n_grow:]
    Vg = len(set(grow_w))
    B = 2 * Vg
    h = pair_counts(held)
    n2 = collections.Counter(held)
    N2 = len(held)
    strong = {k for k, c in h.items() if k[0] in set(grow_w) and k[1] in set(grow_w)
              and c >= 3 and c >= 3 * (2 * D * n2[k[0]] * n2[k[1]] / N2)}
    head = {"words": len(words), "bad_lines": bad, "grow": len(grow_w), "held_out": len(held), "V_grow": Vg, "B": B,
            "held_out_strong_pairs": len(strong)}
    print(f"[shelf] {head}", flush=True)
    runs, g1, g3 = [], [], []
    shuffled = [str(x) for x in np.random.default_rng([1, 7002]).permutation(grow_w)]
    jobs = [("H", 1, grow_w, "real"), ("F", 1, grow_w, "real"), ("L", 1, grow_w, "real")]
    jobs += [(r, s, grow_w, "real") for r in ("S", "R", "S0") for s in SEEDS]
    jobs += [("H", 1, shuffled, "shuffled")] + [("S", s, shuffled, "shuffled") for s in SEEDS]
    keep: Dict[str, object] = {}
    for rule, seed, stream, kind in jobs:
        w = Wb.Web(rule, budget=None if rule == "H" else B, seed=seed)
        peak = 0
        for x in stream:
            w.hear(x)
            peak = max(peak, len(w.edges))
        C = w.consolidated()
        row = {"rule": rule, "seed": seed, "stream": kind, "consolidated": len(C), "live": len(w.edges), "peak": peak,
               "stats": dict(w.stats), **enrichment(C, h, n2, N2),
               "recall_strong": (len(set(C) & strong) / len(strong) if strong else None)}
        if rule != "H":
            g3.append(peak <= B)
        if kind == "real" and seed == 1:
            errs = Wb.recount_errors(w, stream)
            g1.append({"rule": rule, "errors": len(errs), "first": errs[:2]})
            if rule in ("H", "S"):
                row["graph"] = graph_stats(C)
                top = sorted(((w.edges[k]["c"], k) for k in C), reverse=True)[:25]
                row["top"] = [[c, list(k)] for c, k in top]
                keep[rule] = w
        runs.append(row)
        print(f"[shelf] {rule} seed {seed} {kind}: consolidated {len(C)} enrichment {row['enrichment']}", flush=True)
    if "S" in keep:
        wS = keep["S"]
        k0 = next(iter(wS.edges))
        wS.edges[k0]["c"] += 1
        plant = bool(Wb.recount_errors(wS, grow_w))
        wS.edges[k0]["c"] -= 1
    else:
        plant = None
    (out / "shelf.json").write_text(json.dumps({"head": head, "runs": runs, "G1": g1, "G1_plant_caught": plant,
                                                "G3": all(g3)}, sort_keys=True, indent=1))

    def sel(rule, kind="real"):
        return [r for r in runs if r["rule"] == rule and r["stream"] == kind]

    def mean(xs):
        xs = [x for x in xs if x is not None]
        return sum(xs) / len(xs) if xs else None

    L = ["# KW-1 · the organism's shelf (written by tools/web/kw1_shelf.py)", "", f"{head}", "",
         f"G1 recount (seed 1, the growth part): {g1} · plant caught: {plant}", f"G3 budget held: {all(g3)} ({len(g3)} runs)", "",
         "| rule | runs | consolidated (mean) | enrichment (mean) | per seed | recall of the held-out's strong pairs (mean) |", "|---|---|---|---|---|---|"]
    for rule in ("H", "F", "L", "S", "R", "S0"):
        rs = sel(rule)
        L.append(f"| {rule} | {len(rs)} | {mean([r['consolidated'] for r in rs]):.1f} | "
                 f"{(mean([r['enrichment'] for r in rs]) or 0):.2f} | {' '.join('%.2f' % r['enrichment'] if r['enrichment'] is not None else 'none' for r in rs)} | "
                 f"{(mean([r['recall_strong'] for r in rs]) or 0):.3f} |")
    for rule in ("H", "S"):
        rs = sel(rule, "shuffled")
        L.append(f"| {rule} on the SHUFFLED growth part | {len(rs)} | {mean([r['consolidated'] for r in rs]):.1f} | "
                 f"{(mean([r['enrichment'] for r in rs]) or 0):.2f} | {' '.join('%.2f' % r['enrichment'] if r['enrichment'] is not None else 'none' for r in rs)} | — |")
    eh, es = sel("H")[0]["enrichment"], mean([r["enrichment"] for r in sel("S")])
    k6 = es is not None and eh is not None and es >= 2 and es >= 0.8 * eh
    L += ["", f"**K6 IT PREDICTS SPEECH NOT YET HEARD:** S enrichment {es:.2f} (bar ≥ 2 and ≥ 0.8 × H's {eh:.2f} = {0.8 * eh:.2f}) → {'PASS' if k6 else 'FAIL'}"]
    k7 = []
    for rule in ("H", "S"):
        rs = sel(rule, "shuffled")
        e = mean([r["enrichment"] for r in rs])
        n = mean([r["consolidated"] for r in rs])
        k7.append((rule, e, n, (e is None) or e <= 1.5))
    L.append("**K7 THE INSTRUMENT FINDS NOTHING IN A SHUFFLE:** " + "; ".join(
        f"{r}: consolidated {n:.1f}, enrichment {('none' if e is None else '%.2f' % e)} → {'PASS' if ok else 'FAIL'}" for r, e, n, ok in k7))
    for rule in ("H", "S"):
        g = sel(rule)[0].get("graph")
        L.append(f"K8 reading, {rule} (seed 1) as a web: {g}")
        L.append(f"K8 reading, {rule} (seed 1), its 25 strongest associations: " + ", ".join(f"{a}–{b} ({c})" for c, (a, b) in sel(rule)[0].get("top", [])))
    text = "\n".join(L) + "\n"
    (out / "SHELF-READINGS.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
