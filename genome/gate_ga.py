"""gate_ga.py — gate G-a: measure the world's cosine bands through the FIXED fronts, then write
THETA_N and THETA_M into the genome file with the bands beside them (docs/G0-PREREG.md §2, §10 clause 9).

edit: Claude (Fable 5.1), 2026-09-19 19:33 +0400 — G3 §2: the FLOOR rule (THETA_N = between-p5, MARGIN = 5 % of the band width) for genomes carrying RESONATE; overlap never stops such a run.
edit: Claude (Fable 5.1), 2026-09-19 16:1x +04.
edit: Claude (Fable 5.1), 2026-09-19 16:37 +04 — G0b: the eye's side from the genome; the closest pair; the plant's showings from the within-thing share above THETA_N.
Rule: THETA_N sits between the between-thing 95th percentile and the within-thing 5th percentile
(and above the ear's max between-word cosine); THETA_M above the within-thing 95th percentile.
If the retina bands overlap, STOP and report — the fix is a stronger fixed front, never jitter
turned down, never a learned one.
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List, Sequence

import numpy as np

from . import world
from .machinery import retina


def bands(things: Sequence[str], per_thing: int, rng: np.random.Generator, spec, max_between: int = 30000, side: int = 24) -> Dict[str, object]:
    feats = {t: np.stack([retina(world.render(t, rng, side), spec) for _ in range(per_thing)]) for t in things}
    within: List[float] = []
    for t in things:
        F = feats[t]
        C = F @ F.T
        iu = np.triu_indices(len(F), 1)
        within.extend(C[iu].tolist())
    between: List[float] = []
    for a, b in itertools.combinations(things, 2):
        between.extend((feats[a] @ feats[b].T).ravel().tolist())
    within_a, between_a = np.array(within), np.array(between)
    if len(between_a) > max_between:
        between_a = between_a[rng.permutation(len(between_a))[:max_between]]
    q = lambda x, p: float(np.percentile(x, p))
    pairs = {}
    for a, b in itertools.combinations(things, 2):
        pairs[f"{a}/{b}"] = q((feats[a] @ feats[b].T).ravel(), 95)
    closest = max(pairs.items(), key=lambda kv: kv[1])
    return {
        "within": {"median": q(within_a, 50), "p5": q(within_a, 5), "p95": q(within_a, 95), "n": int(len(within_a)), "all": within_a},
        "between": {"median": q(between_a, 50), "p5": q(between_a, 5), "p95": q(between_a, 95), "max": float(between_a.max()), "n": int(len(between_a))},
        "per_thing_within_p5": {t: q((feats[t] @ feats[t].T)[np.triu_indices(per_thing, 1)], 5) for t in things},
        "pair_p95": pairs, "closest_pair": {"pair": closest[0], "p95": closest[1]},
    }


def ear_band(words: Sequence[str], blank_zero: bool) -> Dict[str, float]:
    V = np.stack([world.encode_word(w, blank_zero) for w in words])
    C = V @ V.T
    iu = np.triu_indices(len(words), 1)
    return {"max_between": float(C[iu].max()), "median_between": float(np.median(C[iu]))}


def choose(b: Dict[str, object], ear: Dict[str, float], rule: str = "max") -> Dict[str, object]:
    """§2's strict rule (THETA_N between between-p95 and within-p5) and §11's amended rule (THETA_N = the
    within-thing MEDIAN, which must exceed the between-thing MAX and the ear's max between-word cosine).
    Both are reported; the amended rule sets the number. Overlap under the amended rule → STOP."""
    strict_lo = max(b["between"]["p95"], ear["max_between"]); strict_hi = b["within"]["p5"]
    out = {"strict": {"lo": strict_lo, "hi": strict_hi, "met": strict_lo < strict_hi}}
    theta_n = round(b["within"]["median"], 3)
    # G0b §2b: the floor is the between-thing p95 (fewer than 5 % of cross-thing rendering pairs resonate);
    # the pairs whose own p95 reaches THETA_N are NAMED — separating them is the error-birth road's job
    floor = max(b["between"]["p95" if rule == "p95" else "max"], ear["max_between"])
    out["amended"] = {"theta_n": theta_n, "floor": floor, "rule": rule, "met": theta_n > floor,
                      "conflated_pairs": sorted([(k, v) for k, v in b["pair_p95"].items() if v >= theta_n], key=lambda kv: -kv[1])}
    out["overlap"] = not out["amended"]["met"]
    if out["overlap"]:
        return out
    out["theta_n"] = theta_n
    out["theta_m"] = round(min(0.999, b["within"]["p95"] + 0.5 * (1.0 - b["within"]["p95"])), 4)
    return out


def choose_floor(b: Dict[str, object], ear: Dict[str, float]) -> Dict[str, object]:
    """G3 §2: under RESONATE nearest, THETA_N is the FLOOR = between-thing p5; MARGIN = 5 % of the band width
    (within-median − between-p5); THETA_M as before. Overlap never stops a run; the strict and p95 rules are reported."""
    out = choose(b, ear, rule="p95"); out.pop("overlap", None)
    floor = round(b["between"]["p5"], 3); width = b["within"]["median"] - b["between"]["p5"]
    out.update({"rule": "floor", "theta_n": floor, "theta_m": round(min(0.999, b["within"]["p95"] + 0.5 * (1.0 - b["within"]["p95"])), 4),
                "margin": round(max(0.0, 0.05 * width), 4), "band_width": width, "overlap": False})
    return out


def _retina_spec(genome_path: Path):
    for raw in genome_path.read_text().splitlines():
        line = raw.split("#", 1)[0].split()
        if line and line[0] == "RETINA":
            return tuple(line[1:])
    raise SystemExit("gate G-a: no RETINA gene")


def _eye_side(genome_path: Path) -> int:
    for raw in genome_path.read_text().splitlines():
        line = raw.split("#", 1)[0].split()
        if line[:2] == ["SENSE", "eye"]:
            return int(line[2].split("x")[0])
    raise SystemExit("gate G-a: no SENSE eye gene")


def write_thetas(genome_path: Path, theta_n: float, theta_m: float, note: str, margin: Optional[float] = None) -> str:
    text = genome_path.read_text()
    text, n1 = re.subn(r"cos<THETA_N", f"cos<{theta_n}", text)
    text, n2 = re.subn(r"cos>THETA_M", f"cos>{theta_m}", text)
    if n1 != 1 or n2 != 1:
        raise SystemExit(f"gate G-a: placeholders not found exactly once (THETA_N {n1}, THETA_M {n2})")
    if margin is not None:
        text, n3 = re.subn(r"margin cos<MARGIN", f"margin cos<{margin}", text)
        if n3 != 1: raise SystemExit(f"gate G-a: MARGIN placeholder not found exactly once ({n3})")
    text = text.rstrip("\n") + f"\n# gate G-a wrote THETA_N={theta_n} THETA_M={theta_m}" + (f" MARGIN={margin}" if margin is not None else "") + f" — {note}\n"
    genome_path.write_text(text)
    return text


def run(things: Sequence[str], genome_path: Path, out_path: Path, seed: int, per_thing: int = 60, blank_zero: bool = False) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    spec = _retina_spec(genome_path); side = _eye_side(genome_path)
    b = bands(things, per_thing, rng, spec, side=side)
    within_all = b["within"].pop("all")
    ear = ear_band(list(things), blank_zero)
    nearest = "RESONATE" in genome_path.read_text()
    ch = choose_floor(b, ear) if nearest else choose(b, ear, rule="p95" if "g0b" in genome_path.name.lower() else "max")
    report = {"things": list(things), "per_thing": per_thing, "seed": seed, "retina_spec": list(spec), "retina": b, "ear": ear, "choice": ch}
    if not ch.get("overlap"):
        # G0b §3: the plant's showings are set from the gate — p_res = share of within-thing pairs at or above THETA_N;
        # showings k = the least k with 1 − (1 − p_res)^k ≥ 0.9, never fewer than 5
        p_res = float((within_all >= ch["theta_n"]).mean())
        k = 5
        while (1.0 - (1.0 - p_res) ** k) < 0.9 and k < 60:
            k += 1
        report["plant"] = {"p_res_at_theta_n": p_res, "showings": int(k)}
        print(f"gate G-a · within-thing share ≥ THETA_N = {p_res:.3f} → plant showings {k} (least k with 1−(1−p)^k ≥ 0.9, min 5)")
    print(f"gate G-a · closest pair {b['closest_pair']['pair']} between-p95 {b['closest_pair']['p95']:.3f}")
    out_path.write_text(json.dumps(report, indent=1))
    print(f"gate G-a · retina within: median {b['within']['median']:.3f} p5 {b['within']['p5']:.3f} p95 {b['within']['p95']:.3f} (n {b['within']['n']})")
    print(f"gate G-a · retina between: median {b['between']['median']:.3f} p5 {b['between']['p5']:.3f} p95 {b['between']['p95']:.3f} max {b['between']['max']:.3f} (n {b['between']['n']})")
    print(f"gate G-a · ear max between-word cosine {ear['max_between']:.3f} (blank_zero={blank_zero})")
    worst = min(b["per_thing_within_p5"].items(), key=lambda kv: kv[1])
    print(f"gate G-a · weakest thing (within p5): {worst[0]} {worst[1]:.3f}")
    st = ch["strict"]
    print(f"gate G-a · §2 strict rule (THETA_N between between-p95 {st['lo']:.3f} and within-p5 {st['hi']:.3f}): {'MET' if st['met'] else 'NOT MET — several cells per thing will be born; §11'}")
    if ch["overlap"]:
        print(f"gate G-a · amended rule ({ch['amended']['rule']}) NOT MET: within-median {ch['amended']['theta_n']:.3f} ≤ floor {ch['amended']['floor']:.3f} — STOP; the front is too weak")
        return report
    print(f"gate G-a · conflated pairs at THETA_N (their p95 ≥ {ch['amended']['theta_n']}): {ch['amended']['conflated_pairs'] or 'none'} — the error-birth road's job")
    note = f"§11 rule: THETA_N = within-median; floor (between-max, ear-max) {ch['amended']['floor']:.4f} · within-p5 {b['within']['p5']:.4f} · within-p95 {b['within']['p95']:.4f} · between-p95 {b['between']['p95']:.4f} · seed {seed} · {per_thing}/thing"
    if nearest:
        note = f"G3 floor rule: THETA_N = between-p5 {ch['theta_n']}; MARGIN = 5 % of the band width {ch['band_width']:.4f}; within-median {b['within']['median']:.4f} between-p95 {b['between']['p95']:.4f}"
        write_thetas(genome_path, ch["theta_n"], ch["theta_m"], note, margin=ch["margin"])
        print(f"gate G-a · G3 FLOOR rule: THETA_N={ch['theta_n']} (between-p5) THETA_M={ch['theta_m']} MARGIN={ch['margin']} — written into {genome_path}")
        return report
    write_thetas(genome_path, ch["theta_n"], ch["theta_m"], note)
    print(f"gate G-a · THETA_N={ch['theta_n']} (within-median; floor {ch['amended']['floor']:.3f}) THETA_M={ch['theta_m']} — written into {genome_path}")
    return report


if __name__ == "__main__":
    # python3 -m genome.gate_ga [genome file] [things comma list]   (G0b: genome/G0b.genome, THINGS_11)
    gpath = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("genome/G0.genome")
    things = sys.argv[2].split(",") if len(sys.argv) > 2 else (world.THINGS_11 if "G0b" in gpath.name else world.THINGS_10)
    run(things, gpath, Path(f"runs/gate-ga-{gpath.stem}.json"), seed=20260919)


# ============================================================================ G1: the gate over GLANCES
# edit: Claude (Fable 5.1), 2026-09-19 17:24 +0400 — G1 §5 step 5/7: the bands are measured on precomputed glance features
# (the FIRST fixation of each picture); the p95 rule chooses; thetas + the plant's showings written as for G0b.
def bands_feats(feats: Dict[str, np.ndarray], rng: np.random.Generator, max_between: int = 30000) -> Dict[str, object]:
    things = list(feats.keys())
    within: List[float] = []
    for t in things:
        F = feats[t]; C = F @ F.T; iu = np.triu_indices(len(F), 1); within.extend(C[iu].tolist())
    between: List[float] = []
    for a, b in itertools.combinations(things, 2):
        between.extend((feats[a] @ feats[b].T).ravel().tolist())
    within_a, between_a = np.array(within), np.array(between)
    if len(between_a) > max_between:
        between_a = between_a[rng.permutation(len(between_a))[:max_between]]
    q = lambda x, p: float(np.percentile(x, p))
    pairs = {f"{a}/{b}": q((feats[a] @ feats[b].T).ravel(), 95) for a, b in itertools.combinations(things, 2)}
    closest = max(pairs.items(), key=lambda kv: kv[1])
    return {
        "within": {"median": q(within_a, 50), "p5": q(within_a, 5), "p95": q(within_a, 95), "n": int(len(within_a)), "all": within_a},
        "between": {"median": q(between_a, 50), "p5": q(between_a, 5), "p95": q(between_a, 95), "max": float(between_a.max()), "n": int(len(between_a))},
        "per_thing_within_p5": {t: q((feats[t] @ feats[t].T)[np.triu_indices(len(feats[t]), 1)], 5) if len(feats[t]) > 1 else 1.0 for t in things},
        "pair_p95": pairs, "closest_pair": {"pair": closest[0], "p95": closest[1]},
    }


def run_feats(feats: Dict[str, np.ndarray], words: Sequence[str], genome_path: Path, out_path: Path, seed: int, blank_zero: bool = False, label: str = "") -> Dict[str, object]:
    """Gate G-a on precomputed glance features (G1). Writes THETA_N/THETA_M into the genome when the p95 rule is met;
    returns the report either way (the run reads it and says so when the bands overlap — G1 §1)."""
    rng = np.random.default_rng(seed)
    b = bands_feats(feats, rng)
    within_all = b["within"].pop("all")
    ear = ear_band(list(words), blank_zero)
    nearest = "RESONATE" in genome_path.read_text()
    ch = choose_floor(b, ear) if nearest else choose(b, ear, rule="p95")
    report = {"things": list(feats.keys()), "per_thing": {t: int(len(v)) for t, v in feats.items()}, "seed": seed, "label": label, "retina": b, "ear": ear, "choice": ch, "rule": "floor" if nearest else "p95"}
    print(f"gate G-a [{label}] · within: median {b['within']['median']:.3f} p5 {b['within']['p5']:.3f} p95 {b['within']['p95']:.3f} (n {b['within']['n']}) · between: median {b['between']['median']:.3f} p95 {b['between']['p95']:.3f} max {b['between']['max']:.3f} · ear max {ear['max_between']:.3f}")
    print(f"gate G-a [{label}] · closest pair {b['closest_pair']['pair']} p95 {b['closest_pair']['p95']:.3f} · weakest thing (within p5) {min(b['per_thing_within_p5'].items(), key=lambda kv: kv[1])}")
    st = ch["strict"]
    print(f"gate G-a [{label}] · §2 strict rule (between-p95 {st['lo']:.3f} < THETA_N < within-p5 {st['hi']:.3f}): {'MET' if st['met'] else 'NOT MET'}")
    if nearest:
        p_res = float((within_all >= ch["theta_n"]).mean()); k = 5
        while (1.0 - (1.0 - p_res) ** k) < 0.9 and k < 60: k += 1
        report["plant"] = {"p_res_at_theta_n": p_res, "showings": int(k)}
        note = f"G3 floor rule [{label}]: THETA_N = between-p5; MARGIN = 5 % of the band width {ch['band_width']:.4f}; within-median {b['within']['median']:.4f} between-p95 {b['between']['p95']:.4f}; seed {seed}"
        write_thetas(genome_path, ch["theta_n"], ch["theta_m"], note, margin=ch["margin"])
        print(f"gate G-a [{label}] · G3 FLOOR rule: THETA_N={ch['theta_n']} (between-p5) THETA_M={ch['theta_m']} MARGIN={ch['margin']} (band width {ch['band_width']:.3f}; p95 rule {'met' if ch['amended']['met'] else 'not met'}, reported) — written into {genome_path}")
        out_path.write_text(json.dumps(report, indent=1)); return report
    if ch["overlap"]:
        print(f"gate G-a [{label}] · p95 rule NOT MET: within-median {ch['amended']['theta_n']:.3f} ≤ floor {ch['amended']['floor']:.3f} — the bands OVERLAP under the INK rule; thetas NOT written")
        report["overlap"] = True
        out_path.write_text(json.dumps(report, indent=1)); return report
    p_res = float((within_all >= ch["theta_n"]).mean()); k = 5
    while (1.0 - (1.0 - p_res) ** k) < 0.9 and k < 60: k += 1
    report["plant"] = {"p_res_at_theta_n": p_res, "showings": int(k)}
    print(f"gate G-a [{label}] · conflated pairs at THETA_N: {ch['amended']['conflated_pairs'] or 'none'} · within share ≥ THETA_N {p_res:.3f} → plant showings {k}")
    note = f"G1 gate on glances [{label}]: THETA_N = within-median; floor (between-p95, ear-max) {ch['amended']['floor']:.4f} · within-p5 {b['within']['p5']:.4f} · within-p95 {b['within']['p95']:.4f} · seed {seed}"
    write_thetas(genome_path, ch["theta_n"], ch["theta_m"], note)
    print(f"gate G-a [{label}] · THETA_N={ch['theta_n']} THETA_M={ch['theta_m']} — written into {genome_path}")
    out_path.write_text(json.dumps(report, indent=1)); return report
