#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:16 +0400 — PREREG-EVOLVE-CAL AMENDMENT 3 (A3.4, A3.6, A3.7): the N1 analysis. Tests first: tests/tools/test_evolve_cal_analyse.py.
"""tools/evolve_cal_analyse.py — from the twins' readings to the null arrays, the staged decisions and the BANDS file.

Pure functions over reading dicts (a twin's `reading.json`); `tools/evolve_cal.py` builds the bands (scipy), this module decides WHICH twins go into which null and what the
staged design does next (AMENDMENT 3, A3.6):

  Stage A0   the incumbent + one epsilon twin at 1e-3 and one at 1e-2 on the full slice: NON-DEGENERATE iff at least one epsilon twin's three readings differ from the incumbent's;
  Stage A0+  (only if A0 found nothing) four more: DEGENERATE iff all six equal the incumbent in every reading; the 95 % upper bound on the per-twin chance of a reading
             flip is 1 − 0.05^(1/6) ≈ 0.39;
  Stage B    the other 15 twins at the chosen level run only if the chosen level's six values (the incumbent + 5) hold >= 3 distinct values in some gated dimension;
  A3.4       a twin EQUALS the incumbent iff its journal has no DISCRETE keyed difference AND its three readings are equal; the chosen level is the smallest one whose twins
             do not all equal the incumbent; a larger level whose readings' RMS deviation from the incumbent is more than twice the chosen level's «grows» (a merit step);
  A3.7       a degenerate dimension has NO band (reading A) or the band of its null's own range floored at one resolvable step (reading B).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence

import tools.evolve_cal as cal
from tools import evolve_bands as eb

GATED = eb.GATED                       # ("q1_seen", "frames_filed", "confirmed_share")
Q1_ITEMS = 110
GROWTH_FACTOR = 2.0                    # the RMS deviation of a larger level over the chosen level's, above which the larger level is read as a merit step


def readings_equal(a: dict, b: dict) -> bool:
    """The three gated readings equal, exactly; a None on either side is not equal (a missing reading is never a match)."""
    for d in GATED:
        x, y = a.get(d), b.get(d)
        if x is None or y is None or x != y:
            return False
    return True


def _moved(inc: dict, twins: Dict[str, dict]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for label, r in twins.items():
        for d in GATED:
            x, y = inc.get(d), r.get(d)
            if x is None or y is None or x != y:
                out.setdefault(d, []).append(label)
    return out


def null_arrays(inc: dict, twins: Sequence[dict]) -> Dict[str, List[float]]:
    """The incumbent first, then the twins: q1_seen, frames_filed, confirmed_share and ln(CPU-seconds). A None reading is refused, never dropped."""
    out: Dict[str, List[float]] = {d: [] for d in GATED}
    out["ln_cpu"] = []
    for r in [inc, *twins]:
        for d in GATED:
            if r.get(d) is None:
                raise ValueError(f"null_arrays: a twin carries no {d!r} reading (refused, not dropped)")
            out[d].append(float(r[d]))
        if r.get("cpu_s") is None or not (r["cpu_s"] > 0):
            raise ValueError("null_arrays: a twin carries no CPU-seconds reading (refused, not dropped)")
        out["ln_cpu"].append(math.log(float(r["cpu_s"])))
    return out


def a0_decision(inc: dict, eps_twins: Dict[str, dict]) -> dict:
    moved = _moved(inc, eps_twins)
    return {"non_degenerate": bool(moved), "moved": moved, "n_twins": len(eps_twins)}


def a0plus_decision(inc: dict, six_twins: Dict[str, dict]) -> dict:
    n = len(six_twins)
    if n < 6:
        raise ValueError(f"a0plus_decision: {n} epsilon twins (the rule needs all six: the two of A0 and the four of A0+)")
    moved = _moved(inc, six_twins)
    return {"degenerate": not moved, "moved": moved, "n_twins": n, "upper_bound_p": 1.0 - 0.05 ** (1.0 / n)}


def stage_b_condition(inc: dict, five_twins: Sequence[dict]) -> dict:
    """Stage B runs only where more draws can sharpen a band A1 (i) would grant: some gated dimension of [incumbent + the chosen level's twins] holds >= 3 distinct values."""
    dims = [d for d in GATED if len({x[d] for x in [inc, *five_twins] if x.get(d) is not None}) >= 3]
    return {"run": bool(dims), "dims": dims, "n_values": 1 + len(five_twins)}


def _rms_dev(inc: dict, twins: Sequence[dict], d: str) -> float:
    grid = Q1_ITEMS if d == "q1_seen" else 1.0                 # q1_seen in items, the others in their own units
    xs = [(t["reading"][d] - inc[d]) * grid for t in twins if t["reading"].get(d) is not None and inc.get(d) is not None]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else 0.0


def choose_level(inc: dict, levels: Dict[float, Sequence[dict]]) -> dict:
    """`levels`: epsilon -> its twins, each {label, reading, discrete_differing} (the keyed comparison of its journal with the incumbent's). The chosen level is the smallest whose
    twins do not ALL equal the incumbent (A3.4: no discrete difference AND equal readings); a larger flipping level whose RMS deviation grows beyond GROWTH_FACTOR times the
    chosen one's, in some gated dimension, is flagged `spread_grows` (a merit step, never the null)."""
    per: Dict[float, dict] = {}
    for eps in sorted(levels):
        tw = levels[eps]
        equal = sum(1 for t in tw if t.get("discrete_differing", 0) == 0 and readings_equal(inc, t["reading"]))
        per[eps] = {"n": len(tw), "twins_equal_to_incumbent": equal, "differs": equal < len(tw), "rms_dev": {d: _rms_dev(inc, tw, d) for d in GATED}, "spread_grows": False}
    flipping = [e for e in sorted(per) if per[e]["differs"]]
    chosen: Optional[float] = flipping[0] if flipping else None
    if chosen is not None:
        for e in flipping[1:]:
            base = per[chosen]["rms_dev"]
            per[e]["spread_grows"] = any(per[e]["rms_dev"][d] > GROWTH_FACTOR * base[d] and per[e]["rms_dev"][d] > 0 for d in GATED)
    return {"chosen": chosen, "per_level": per}


def bands_from_twins(inc: dict, eps_twins: Sequence[dict], seed_twins: Optional[Sequence[dict]], slice_name: str, scope: str, degenerate: str = "none") -> dict:
    """The BANDS file from the incumbent + the chosen level's epsilon twins (the null of every dimension) and the seed twins (frames_filed's A2.2 null, the incumbent among them).
    degenerate = «none» (reading A: a degenerate dimension has NO band) or «range» (reading B: the band of its null's own range, floored at one resolvable step)."""
    if degenerate not in ("none", "range"):
        raise ValueError(f"bands_from_twins: degenerate must be 'none' or 'range', got {degenerate!r}")
    null = null_arrays(inc, eps_twins)
    seed_frames = None
    if seed_twins:
        seed_frames = [float(x["frames_filed"]) for x in [inc, *seed_twins]]
    b = cal.make_bands(null, slice_name, scope, seed_frames=seed_frames)
    canvases = ((inc.get("detail") or {}).get("surprise") or {}).get("canvases")
    floors = {"q1_seen": 0.0, "frames_filed": 0.0, "confirmed_share": (1.0 / (4.0 * canvases)) if canvases else 0.0}
    if degenerate == "range":
        for d in GATED:
            band = b["dims"][d]
            if band["kind"] == "none":
                rng = max(float(band["range"]), floors[d])
                b["dims"][d] = {**band, "kind": "rank", "edge": None, "range": rng,
                                "note": f"reading B: a degenerate null (the dimension never moved, or held fewer than 3 distinct values) is banded by its own range {band['range']:.6g}, "
                                        f"floored at one resolvable step {floors[d]:.6g}: any Δ larger than every null Δ is outside"}
                if band.get("grid"):
                    b["dims"][d]["edge_grid"] = rng / band["grid"]
                    b["dims"][d]["min_clear_grid"] = math.floor(round(rng / band["grid"], 9)) + 1
        b["degenerate_reading"] = "B: the null's own range, floored at one resolvable step"
    else:
        b["degenerate_reading"] = "A: a degenerate dimension has NO band and does not gate"
    q1 = inc.get("q1_seen")
    if q1 is not None:
        ceiling = Q1_ITEMS - round(q1 * Q1_ITEMS)
        b["dims"]["q1_seen"]["ceiling_items"] = ceiling
        half = b["dims"]["q1_seen"].get("edge_grid")
        b["dims"]["q1_seen"]["ceiling_note"] = (f"the incumbent reads {round(q1 * Q1_ITEMS)} of {Q1_ITEMS}: at most {ceiling} items of improvement; an IMPROVED on q1_seen is "
                                                f"reachable iff the band's edge ({half if half is not None else 'no band'} items) is below {ceiling}")
    eb.validate_bands(b)
    return b
