"""gate_ga.py — gate G-a: measure the world's cosine bands through the FIXED fronts, then write
THETA_N and THETA_M into the genome file with the bands beside them (docs/G0-PREREG.md §2, §10 clause 9).

edit: Claude (Fable 5.1), 2026-09-19 16:1x +04.
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
from typing import Dict, List, Sequence

import numpy as np

from . import world
from .machinery import retina


def bands(things: Sequence[str], per_thing: int, rng: np.random.Generator, spec, max_between: int = 30000) -> Dict[str, object]:
    feats = {t: np.stack([retina(world.render(t, rng), spec) for _ in range(per_thing)]) for t in things}
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
    return {
        "within": {"median": q(within_a, 50), "p5": q(within_a, 5), "p95": q(within_a, 95), "n": int(len(within_a))},
        "between": {"median": q(between_a, 50), "p5": q(between_a, 5), "p95": q(between_a, 95), "max": float(between_a.max()), "n": int(len(between_a))},
        "per_thing_within_p5": {t: q((feats[t] @ feats[t].T)[np.triu_indices(per_thing, 1)], 5) for t in things},
    }


def ear_band(words: Sequence[str], blank_zero: bool) -> Dict[str, float]:
    V = np.stack([world.encode_word(w, blank_zero) for w in words])
    C = V @ V.T
    iu = np.triu_indices(len(words), 1)
    return {"max_between": float(C[iu].max()), "median_between": float(np.median(C[iu]))}


def choose(b: Dict[str, object], ear: Dict[str, float]) -> Dict[str, object]:
    """§2's strict rule (THETA_N between between-p95 and within-p5) and §11's amended rule (THETA_N = the
    within-thing MEDIAN, which must exceed the between-thing MAX and the ear's max between-word cosine).
    Both are reported; the amended rule sets the number. Overlap under the amended rule → STOP."""
    strict_lo = max(b["between"]["p95"], ear["max_between"]); strict_hi = b["within"]["p5"]
    out = {"strict": {"lo": strict_lo, "hi": strict_hi, "met": strict_lo < strict_hi}}
    theta_n = round(b["within"]["median"], 3)
    floor = max(b["between"]["max"], ear["max_between"])
    out["amended"] = {"theta_n": theta_n, "floor": floor, "met": theta_n > floor}
    out["overlap"] = not out["amended"]["met"]
    if out["overlap"]:
        return out
    out["theta_n"] = theta_n
    out["theta_m"] = round(min(0.999, b["within"]["p95"] + 0.5 * (1.0 - b["within"]["p95"])), 4)
    return out


def _retina_spec(genome_path: Path):
    for raw in genome_path.read_text().splitlines():
        line = raw.split("#", 1)[0].split()
        if line and line[0] == "RETINA":
            return tuple(line[1:])
    raise SystemExit("gate G-a: no RETINA gene")


def write_thetas(genome_path: Path, theta_n: float, theta_m: float, note: str) -> str:
    text = genome_path.read_text()
    text, n1 = re.subn(r"cos<THETA_N", f"cos<{theta_n}", text)
    text, n2 = re.subn(r"cos>THETA_M", f"cos>{theta_m}", text)
    if n1 != 1 or n2 != 1:
        raise SystemExit(f"gate G-a: placeholders not found exactly once (THETA_N {n1}, THETA_M {n2})")
    text = text.rstrip("\n") + f"\n# gate G-a wrote THETA_N={theta_n} THETA_M={theta_m} — {note}\n"
    genome_path.write_text(text)
    return text


def run(things: Sequence[str], genome_path: Path, out_path: Path, seed: int, per_thing: int = 60, blank_zero: bool = False) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    spec = _retina_spec(genome_path)
    b = bands(things, per_thing, rng, spec)
    ear = ear_band(list(things), blank_zero)
    ch = choose(b, ear)
    report = {"things": list(things), "per_thing": per_thing, "seed": seed, "retina_spec": list(spec), "retina": b, "ear": ear, "choice": ch}
    out_path.write_text(json.dumps(report, indent=1))
    print(f"gate G-a · retina within: median {b['within']['median']:.3f} p5 {b['within']['p5']:.3f} p95 {b['within']['p95']:.3f} (n {b['within']['n']})")
    print(f"gate G-a · retina between: median {b['between']['median']:.3f} p5 {b['between']['p5']:.3f} p95 {b['between']['p95']:.3f} max {b['between']['max']:.3f} (n {b['between']['n']})")
    print(f"gate G-a · ear max between-word cosine {ear['max_between']:.3f} (blank_zero={blank_zero})")
    worst = min(b["per_thing_within_p5"].items(), key=lambda kv: kv[1])
    print(f"gate G-a · weakest thing (within p5): {worst[0]} {worst[1]:.3f}")
    st = ch["strict"]
    print(f"gate G-a · §2 strict rule (THETA_N between between-p95 {st['lo']:.3f} and within-p5 {st['hi']:.3f}): {'MET' if st['met'] else 'NOT MET — several cells per thing will be born; §11'}")
    if ch["overlap"]:
        print(f"gate G-a · §11 amended rule NOT MET: within-median {ch['amended']['theta_n']:.3f} ≤ floor {ch['amended']['floor']:.3f} (between-max / ear-max) — STOP; the front is too weak")
        return report
    note = f"§11 rule: THETA_N = within-median; floor (between-max, ear-max) {ch['amended']['floor']:.4f} · within-p5 {b['within']['p5']:.4f} · within-p95 {b['within']['p95']:.4f} · between-p95 {b['between']['p95']:.4f} · seed {seed} · {per_thing}/thing"
    write_thetas(genome_path, ch["theta_n"], ch["theta_m"], note)
    print(f"gate G-a · THETA_N={ch['theta_n']} (within-median; floor {ch['amended']['floor']:.3f}) THETA_M={ch['theta_m']} — written into {genome_path}")
    return report


if __name__ == "__main__":
    things = sys.argv[1].split(",") if len(sys.argv) > 1 else world.THINGS_10
    run(things, Path("genome/G0.genome"), Path("runs/gate-ga.json"), seed=20260919)
