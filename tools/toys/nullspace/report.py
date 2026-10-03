"""report.py — TOY B's analysis: summaries of the lives' records, gradability, the bars (B-PROTECT, B-NULLSPACE, B-SHRINK, B-PLASTIC), the verdict classes, the frontier, the renderer.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:50 +0400 — new module, written to docs/research/toys/PREREG-TOY-NULLSPACE.md §3 (text co-signed 2026-10-03 11:24 +0400,
# sha256 d15a6353…); red-first (tests/tools/test_toys_nullspace_analyse.py). The BWT marks and the paired standard error are T-MEM-1's own functions (brain/scene/run_tmem1.py
# `bwt_series`, `paired_gate`), imported, not copied.

THE BARS (decided at the ten seeds; E is OWM@tau or NSCL@tau; the barred BWTs are j = 3 (after R3) and j = 4 (after N); j = 2 is printed):
  GRADABILITY first — (c1) PLAIN forgets: BWT_3(PLAIN) <= −0.15 and BWT_4(PLAIN) <= −0.50 at >= 8 of 10 seeds; (c2) something is protectable: Δ_3 = BWT_3(STD-ONLY(2)) − BWT_3(PLAIN) and
                Δ_4 = BWT_4(STD-ONLY(3)) − BWT_4(PLAIN) each exceed twice the paired SE of that difference, at >= 8 gradable seeds; else NOT GRADABLE.
  B-PROTECT   BWT_j(E) − BWT_j(PLAIN) >= 2 paired SE for j = 3 AND 4, at >= 8 gradable seeds.
  B-NULLSPACE E's BWT_3 and BWT_4 each exceed at least 9 of the 10 draws of its null (ROT for OWM, RANDRANK for NSCL): rank <= 2 of 11; >= 8 seeds.
  B-SHRINK    BWT_j(E) − BWT_j(SHRINK(E)) >= 2 paired SE for j = 3 and 4, at >= 8 seeds.
  B-PLASTIC   PLASTICITY_2(E)/PLASTICITY_2(PLAIN) >= 0.90 and PLASTICITY_3(E)/PLASTICITY_3(PLAIN) >= 0.90, at >= 8 seeds.
CLASSES per arm: NULL-SPACE-PROTECTS (all four) · PROTECTS-BUT-FREEZES (protect + null + shrink, not plastic) · PROTECTS-BY-SHRINKING (protect + plastic, fails a null) · SHRINK-AND-FREEZE
(protect, fails plasticity AND a null: unclassified by the law, printed) · NOTHING (no B-PROTECT) · NOT-GRADABLE. The HEADLINE is the best class any of the six arms reaches.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from brain.scene import run_tmem1 as T1

TAUS = ("0.1", "0.01", "0.001")
READ = T1.READ_POINTS
NEED = 8                                 # seeds of ten
Z = 2.0                                  # paired standard errors
RANK_MAX = 2                             # rank <= 2 of 11
PLAST_RATIO = 0.90
CLASS_ORDER = ("NULL-SPACE-PROTECTS", "PROTECTS-BUT-FREEZES", "PROTECTS-BY-SHRINKING", "SHRINK-AND-FREEZE", "NOTHING")
VOCAB13 = ("big", "small", "red", "blue", "green", "yellow", "white", "circle", "square", "triangle", "cross", "ring", "star")


def rank_among(value: float, nulls: Sequence[float]) -> int:
    """1 + the number of null draws at least as high as `value`: 1 = above every draw (of 10: rank 1 of 11)."""
    return 1 + int(sum(1 for x in nulls if x >= value))


def paired(a: Mapping[str, object], b: Mapping[str, object], j: int) -> Tuple[float, float]:
    """The paired difference of backward transfer after room j (a − b) over the SAME held (item, word) pairs and its standard error (T-MEM-1's paired_gate rule)."""
    r = T1.paired_gate({"pairs": a["pairs"]}, {"pairs": b["pairs"]}, None, j)
    return float(r["diff"]), float(r["se"])


# ====================================================================================================== summaries and loading
def summarise_life(rec: Mapping[str, object], plain50: Optional[str] = None) -> Dict[str, object]:
    n = rec["word_n"]
    rw = {b: rec["rates_rw"][b] for b in READ}
    bs = T1.bwt_series(rw, T1.SHAPE_TASKS, n)
    R = bs["R"]
    pairs = {int(b): {int(t): np.asarray(v, dtype=int) for t, v in tasks.items()} for b, tasks in rec["pairs"].items()}
    shape_words = {w for t in T1.SHAPE_TASKS for w in t}
    cont = [w for w in VOCAB13 if w not in shape_words]
    ex = rec.get("extra", {})
    eq50 = None
    if plain50 is not None:
        eq50 = json.dumps(rec["rates_rw"][:51], sort_keys=True) == plain50
    rho = ex.get("rho") or {}
    return {"bwt": {j: float(bs["BWT"][j]) for j in (2, 3, 4)}, "R": {j: dict(R[j]) for j in R}, "plast": {i: float(R[i][i]) for i in (1, 2, 3)}, "pairs": pairs,
            "cpu": float(rec["cpu_s"]), "A": float(np.mean([sum(1 for w in VOCAB13 if (r.get(w) or 0) >= 0.80) for r in rec["rates_rw"][1:]])) / len(VOCAB13),
            "transfer": {b: T1._pooled(rw[b], cont, n)[0] for b in READ}, "eq50": eq50, "alpha": ex.get("alpha"), "capacity": ex.get("capacity"),
            "nscl_dims": ex.get("nscl_dims"), "rho_mean": float(np.mean(list(rho.values()))) if rho else None, "n_words_end": ex.get("n_words_end")}


def load_all(root: Path, seeds: Sequence[int]) -> Tuple[Dict[str, Dict[int, List[Dict[str, object]]]], Dict[str, int]]:
    """arms -> seed -> [life summaries in replicate order]; the record counts. `eq50` compares each life's first 51 rate tables with the same seed's PLAIN."""
    summ: Dict[str, Dict[int, List[Dict[str, object]]]] = {}
    counts: Dict[str, int] = {}
    plain50: Dict[int, str] = {}
    for s in seeds:
        p = Path(root) / "PLAIN" / str(s) / "00.json"
        if p.exists():
            plain50[s] = json.dumps(json.loads(p.read_text())["rates_rw"][:51], sort_keys=True)
    for arm_dir in sorted(Path(root).iterdir()):
        if not arm_dir.is_dir():
            continue
        for s in seeds:
            d = arm_dir / str(s)
            if not d.is_dir():
                continue
            for f in sorted(d.glob("*.json")):
                rec = json.loads(f.read_text())
                summ.setdefault(arm_dir.name, {}).setdefault(s, []).append(summarise_life(rec, plain50.get(s)))
                counts[arm_dir.name] = counts.get(arm_dir.name, 0) + 1
    return summ, counts


# ====================================================================================================== the analysis
def _life(summ, arm: str, seed: int, k: int = 0):
    return summ[arm][seed][k]


def analyse(summ: Mapping[str, Mapping[int, Sequence[Dict[str, object]]]], seeds: Sequence[int]) -> Dict[str, object]:
    seeds = sorted(seeds)
    # ---- gradability
    c1_s, c2_s, grad_s = {}, {}, {}
    for s in seeds:
        P = _life(summ, "PLAIN", s)
        c1_s[s] = bool(P["bwt"][3] <= -0.15 and P["bwt"][4] <= -0.50)
        d3, se3 = paired(_life(summ, "STD-ONLY@2", s), P, 3)
        d4, se4 = paired(_life(summ, "STD-ONLY@3", s), P, 4)
        c2_s[s] = bool(d3 >= Z * se3 and d4 >= Z * se4)
        grad_s[s] = c1_s[s] and c2_s[s]
    n1, n2, ng = sum(c1_s.values()), sum(c2_s.values()), sum(grad_s.values())
    gradable = {"c1": {"ok": n1 >= NEED, "n": n1, "by_seed": c1_s}, "c2": {"ok": n2 >= NEED, "n": n2, "by_seed": c2_s}, "n_gradable": ng, "ok": bool(n1 >= NEED and n2 >= NEED and ng >= NEED)}
    # ---- the arms
    def mean_bwt(arm: str, j: int) -> float:
        return float(np.mean([np.mean([l["bwt"][j] for l in summ[arm][s]]) for s in seeds]))

    arms: Dict[str, Dict[str, object]] = {}
    for fam, null_fam, shrink_fam in (("OWM", "ROT", "SHRINK-OWM"), ("NSCL", "RANDRANK", "SHRINK-NSCL")):
        for t in TAUS:
            name = f"{fam}@{t}"
            if name not in summ:
                continue
            prot, nul, shr, pla = {}, {}, {}, {}
            for s in seeds:
                E, P = _life(summ, name, s), _life(summ, "PLAIN", s)
                prot[s] = bool(grad_s[s] and all(paired(E, P, j)[0] >= Z * paired(E, P, j)[1] for j in (3, 4)))
                nulls = summ[f"{null_fam}@{t}"][s]
                nul[s] = bool(all(rank_among(E["bwt"][j], [l["bwt"][j] for l in nulls]) <= RANK_MAX for j in (3, 4)))
                S_ = _life(summ, f"{shrink_fam}@{t}", s)
                shr[s] = bool(all(paired(E, S_, j)[0] >= Z * paired(E, S_, j)[1] for j in (3, 4)))
                pla[s] = bool(E["plast"][2] / P["plast"][2] >= PLAST_RATIO and E["plast"][3] / P["plast"][3] >= PLAST_RATIO)
            bars = {k: {"ok": sum(v.values()) >= NEED, "n": sum(v.values()), "by_seed": v} for k, v in (("B_PROTECT", prot), ("B_NULLSPACE", nul), ("B_SHRINK", shr), ("B_PLASTIC", pla))}
            if not gradable["ok"]:
                cls = "NOT-GRADABLE"
            elif not bars["B_PROTECT"]["ok"]:
                cls = "NOTHING"
            elif bars["B_NULLSPACE"]["ok"] and bars["B_SHRINK"]["ok"] and bars["B_PLASTIC"]["ok"]:
                cls = "NULL-SPACE-PROTECTS"
            elif bars["B_NULLSPACE"]["ok"] and bars["B_SHRINK"]["ok"]:
                cls = "PROTECTS-BUT-FREEZES"
            elif bars["B_PLASTIC"]["ok"]:
                cls = "PROTECTS-BY-SHRINKING"
            else:
                cls = "SHRINK-AND-FREEZE"
            share = {}
            for j in (2, 3, 4):
                std = f"STD-ONLY@{j - 1}"
                if std in summ:
                    num, den = mean_bwt(name, j) - mean_bwt("PLAIN", j), mean_bwt(std, j) - mean_bwt("PLAIN", j)
                    share[j] = float(num / den) if den != 0 else float("nan")
            arms[name] = {**bars, "class": cls, "removed_share": share, "bwt": {j: mean_bwt(name, j) for j in (2, 3, 4)},
                          "plast": {i: float(np.mean([_life(summ, name, s)["plast"][i] for s in seeds])) for i in (1, 2, 3)}}
    best = None
    if not gradable["ok"]:
        headline = "NOT-GRADABLE"
    else:
        reached = [a["class"] for a in arms.values()]
        headline = next((c for c in CLASS_ORDER if c in reached), "NOTHING")
    # ---- the plant and the pins
    anti_ok = None
    if "ANTI-OWM@0.01" in summ:
        n_lose = sum(1 for s in seeds if _life(summ, "ANTI-OWM@0.01", s)["bwt"][3] < _life(summ, "PLAIN", s)["bwt"][3])
        anti_ok = {"ok": n_lose >= NEED, "n": n_lose}
    viol = sorted({(a, s) for a, d in summ.items() if a != "PLAIN" and not a.startswith("LRSHRINK") for s, ls in d.items() for l in ls if l.get("eq50") is False})
    pb4 = {"violations": viol, "ok": not viol}
    # ---- the frontier (a reading) and the cost
    frontier = {}
    for a, d in summ.items():
        lives = [l for s in seeds for l in d.get(s, [])]
        if lives:
            frontier[a] = {"plast2": float(np.mean([l["plast"][2] for l in lives])), "plast3": float(np.mean([l["plast"][3] for l in lives])),
                           "bwt3": float(np.mean([l["bwt"][3] for l in lives])), "bwt4": float(np.mean([l["bwt"][4] for l in lives])),
                           "cpu": float(np.mean([l["cpu"] for l in lives])), "n": len(lives)}
    return {"seeds": seeds, "gradable": gradable, "arms": arms, "headline": headline, "PB1": anti_ok, "PB4": pb4, "frontier": frontier}


def render(an: Mapping[str, object], summ, seeds: Sequence[int], counts: Optional[Mapping[str, int]] = None) -> List[str]:
    L: List[str] = []
    g = an["gradable"]
    L.append(f"TOY B — THE NULL SPACE · seeds {seeds[0]}–{seeds[-1]} ({len(seeds)})")
    if counts:
        L.append("lives on disk: " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    L.append(f"GRADABILITY (decided first): (c1) PLAIN forgets (BWT_3 ≤ −0.15 and BWT_4 ≤ −0.50) at {g['c1']['n']} of {len(seeds)} seeds → {'PASS' if g['c1']['ok'] else 'FAIL'}; "
             f"(c2) the ceiling is above the noise (Δ_3, Δ_4 each ≥ 2 paired SE) at {g['c2']['n']} of {len(seeds)} → {'PASS' if g['c2']['ok'] else 'FAIL'}; gradable seeds {g['n_gradable']} → "
             f"{'GRADABLE' if g['ok'] else 'NOT GRADABLE'}")
    L.append("")
    L.append(f"{'arm':14s} {'B-PROTECT':>10s} {'B-NULLSP':>9s} {'B-SHRINK':>9s} {'B-PLASTIC':>10s}   class                     removed share (BWT_2/3/4)   BWT_3 BWT_4   plast2 plast3")
    for name, a in an["arms"].items():
        sh = a["removed_share"]
        ns_ = len(seeds)
        L.append(f"{name:14s} {a['B_PROTECT']['n']:>5d}/{ns_} {'Y' if a['B_PROTECT']['ok'] else '·'} {a['B_NULLSPACE']['n']:>4d}/{ns_} {'Y' if a['B_NULLSPACE']['ok'] else '·'} "
                 f"{a['B_SHRINK']['n']:>4d}/{ns_} {'Y' if a['B_SHRINK']['ok'] else '·'} {a['B_PLASTIC']['n']:>5d}/{ns_} {'Y' if a['B_PLASTIC']['ok'] else '·'}   {a['class']:24s} "
                 f"{sh.get(2, float('nan')):+.2f} / {sh.get(3, float('nan')):+.2f} / {sh.get(4, float('nan')):+.2f}   {a['bwt'][3]:+.3f} {a['bwt'][4]:+.3f}   {a['plast'][2]:.3f} {a['plast'][3]:.3f}")
    L.append("")
    L.append("PLANTED CONTROLS: " + (f"PB1 ANTI-OWM must LOSE to PLAIN on BWT_3: at {an['PB1']['n']} of {len(seeds)} seeds → {'CAUGHT' if an['PB1']['ok'] else 'NOT CAUGHT (the mark is blind to the projector)'}" if an["PB1"] else "PB1 absent")
             + f" · PB4 every arm equals PLAIN through block 50: {'yes' if an['PB4']['ok'] else 'VIOLATED ' + str(an['PB4']['violations'])}")
    L.append("")
    L.append("THE FRONTIER (mean over seeds [and draws]): PLASTICITY_2, PLASTICITY_3, BWT_3, BWT_4, CPU of a life, lives")
    for a in sorted(an["frontier"]):
        f = an["frontier"][a]
        L.append(f"   {a:18s} {f['plast2']:.3f} {f['plast3']:.3f}   {f['bwt3']:+.3f} {f['bwt4']:+.3f}   {f['cpu']:6.2f} s  n {f['n']}")
    L.append("")
    L.append(f"HEADLINE: {an['headline']}")
    return L


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(description="TOY B's report over the lives' records")
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3] / "scratch" / "toys-ns" / "runs")
    ap.add_argument("--out", type=Path, default=None)
    ns = ap.parse_args(argv)
    seeds = list(range(20261301, 20261311))
    summ, counts = load_all(ns.root, seeds)
    need = ["PLAIN", "STD-ONLY@2", "STD-ONLY@3"] + [f"{f}@{t}" for f in ("OWM", "NSCL", "ROT", "RANDRANK", "SHRINK-OWM", "SHRINK-NSCL") for t in TAUS]
    missing = [a for a in need if a not in summ or any(s not in summ[a] for s in seeds)]
    if missing:
        print(f"records missing for {missing}; run the unit first", file=sys.stderr)
        return 2
    an = analyse(summ, seeds)
    text = "\n".join(render(an, summ, seeds, counts)) + "\n"
    print(text)
    if ns.out:
        ns.out.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
