# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:55 +0400 — PREREG-EVOLVE-CAL §1 (D1, D4, D5, D6, D7) + A3/A4: the calibrated gate's pure parts.
"""tools/evolve_bands.py — the CALIBRATED evolve gate: bands, three verdicts, the dead dimensions, the confirmation rule.

Standard library only: the worker imports this and must not need scipy (the BANDS FILE is built offline by `tools/evolve_cal.py`
from the merit-neutral twins' noise model, docs/organism/evolve/PREREG-EVOLVE-CAL.md §2 + A1/A2).

A BAND is the half-width of the NO-EVIDENCE region around Δ = mutant − incumbent = 0 (A4 (ii): the production Δ is a difference of two
draws, so under no merit difference it is centred at 0, and the edge is t(20, 1 − 0.0083) · √2 · σ̂, not centred on the mean of k
differences against one incumbent). Three kinds: `normal` (edge = that half-width), `rank` (the null's range max − min, used when the
null is not normal at p < 0.01 — «outside all draws»), `none` (the null could not give a band: fewer than 3 distinct values or σ = 0,
A1 (i); the dimension does not gate and the law says so). An integer reading compares on its own GRID (q1_seen in items of 1/110,
frames_filed in frames): Δ is rounded to whole grid steps and compared strictly with the edge in steps, so float noise in a difference of
two k/110 values never moves a reading across an edge.

The bar reads q1_seen, frames_filed, confirmed_share and the cost. reward_mean, act_pass and sentence_pass are blind by construction (D4:
read from the tape both twins replay) or above their ceiling (D5: ≥ 100 missions, a 2 h slice holds a handful): they are printed as NOT
GRADABLE with the reason and a presence count and never enter the bar.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, Optional

GATED = ("q1_seen", "frames_filed", "confirmed_share")
COST_DIM = "ln_cpu"
KINDS = ("normal", "rank", "none")
COST_POLICY_CAP = 1.2


def _half(band: dict) -> Optional[float]:
    kind = band.get("kind")
    if kind == "normal":
        return float(band["edge"])
    if kind == "rank":
        return float(band["range"])
    return None


def position(delta: Optional[float], band: dict) -> str:
    """below / within / above the band, `no-band` for a dimension without one, `missing` for a reading that is None."""
    if delta is None:
        return "missing"
    half = _half(band)
    if half is None:
        return "no-band"
    grid = band.get("grid")
    d, h = (round(delta / grid), half / grid) if grid else (delta, half)
    if d < -h:
        return "below"
    if d > h:
        return "above"
    return "within"


def _dim_entry(iv, mv, band: dict) -> dict:
    half = _half(band)
    grid = band.get("grid")
    delta = None if (iv is None or mv is None) else (mv - iv)
    edge_grid = (half / grid) if (half is not None and grid) else None
    return {"incumbent": iv, "mutant": mv, "delta": delta, "position": position(delta, band), "kind": band.get("kind"),
            "edge": half, "grid": grid,
            "delta_grid": (delta / grid) if (delta is not None and grid) else None,
            "edge_grid": edge_grid,
            "min_clear_grid": (math.floor(round(edge_grid, 9)) + 1) if edge_grid is not None else None}


def _cost_entry(incumbent: dict, mutant: dict, bands: dict) -> dict:
    """The cost: the twins' PROCESS CPU-seconds (not wall). REGRESSED only if the ratio is outside its band (high side) AND above the
    policy cap (A3); with no band for the cost the cap alone decides; a cheaper mutant is never a regression."""
    cap = float(bands.get("cost_policy_cap", COST_POLICY_CAP))
    ci, cm = incumbent.get("cpu_s"), mutant.get("cpu_s")
    if ci is None or cm is None or not (ci > 0) or not (cm > 0):
        return {"ratio": None, "ln_ratio": None, "position": "missing", "regressed": False, "cap": cap}
    ratio = cm / ci
    ln_ratio = math.log(ratio)
    cband = bands["dims"].get(COST_DIM)
    pos = position(ln_ratio, cband) if cband is not None else "no-band"
    outside_high = True if pos == "no-band" else (pos == "above")
    return {"ratio": ratio, "ln_ratio": ln_ratio, "position": pos, "regressed": bool(ratio > cap and outside_high), "cap": cap,
            "edge": (_half(cband) if cband else None),
            "wall_ratio": ((mutant.get("wall_s") / incumbent.get("wall_s")) if (incumbent.get("wall_s") and mutant.get("wall_s")) else None)}


def calibrated_verdict(incumbent: dict, mutant: dict, bands: dict) -> dict:
    """REGRESSED (a reading below its band, or the cost regressed), IMPROVED (none below, at least one above, cost not regressed),
    NO EVIDENCE (neither). The incumbent stays on REGRESSED and on NO EVIDENCE; an IMPROVED needs the confirmation round (confirm_decision)."""
    dims = {d: _dim_entry(incumbent.get(d), mutant.get(d), bands["dims"][d]) for d in GATED}
    cost = _cost_entry(incumbent, mutant, bands)
    below = [d for d, e in dims.items() if e["position"] == "below"]
    above = [d for d, e in dims.items() if e["position"] == "above"]
    if below or cost["regressed"]:
        verdict = "REGRESSED"
    elif above:
        verdict = "IMPROVED"
    else:
        verdict = "NO EVIDENCE"

    def part(d: str) -> str:
        e = dims[d]
        if e["delta"] is None:
            return f"{d} missing"
        g = f" (Δ {e['delta_grid']:+.0f} vs edge {e['edge_grid']:.2f}; needs ≥ {e['min_clear_grid']})" if e["edge_grid"] is not None else (
            f" (Δ {e['delta']:+.4f} vs edge {e['edge']:.4f})" if e["edge"] is not None else " (no band)")
        return f"{d} {e['incumbent']}->{e['mutant']} {e['position']}{g}"
    bits = [part(d) for d in GATED]
    if cost["ratio"] is not None:
        bits.append(f"cpu ratio {cost['ratio']:.3f} ({cost['position']}, cap {cost['cap']}{', REGRESSED' if cost['regressed'] else ''})")
    return {"verdict": verdict, "dims": dims, "cost": cost, "reason": f"{verdict}: " + "; ".join(bits)}


def not_gradable_block(incumbent: dict, mutant: dict) -> Dict[str, dict]:
    """reward_mean, act_pass, sentence_pass: NOT GRADABLE with their reason and presence count (the number of sides that carry the field)."""
    missions = ((incumbent.get("detail") or {}).get("sentence") or {}).get("missions")
    by_construction = "NOT GRADABLE: read from the tape both twins replay — identical by construction (D4)"
    reasons = {"reward_mean": by_construction, "act_pass": by_construction,
               "sentence_pass": f"NOT GRADABLE: needs ≥ 100 missions, the slice holds {missions} (D5)"}
    out: Dict[str, dict] = {}
    for key, reason in reasons.items():
        iv, mv = incumbent.get(key), mutant.get(key)
        out[key] = {"reason": reason, "incumbent": iv, "mutant": mv, "present": sum(x is not None for x in (iv, mv)), "equal": iv == mv}
    out["sentence_pass"]["missions"] = missions
    return out


def confirm_decision(first: dict, second: dict) -> dict:
    """An IMPROVED mutant is ADOPTED only after it is IMPROVED again on the NEXT DISJOINT slice (its own twins, the same bands).
    `first` and `second` are proposal dicts carrying `gate.verdict`, `gene`, `value`, `slice_from_seq`, `slice_to_seq`."""
    g1 = (first.get("gate") or {}).get("verdict")
    g2 = (second.get("gate") or {}).get("verdict")
    if g1 != "IMPROVED":
        return {"adopt": False, "keep_pending": False, "reason": f"nothing to confirm: the first round read {g1}"}
    if (first.get("gene"), first.get("value")) != (second.get("gene"), second.get("value")):
        return {"adopt": False, "keep_pending": False,
                "reason": f"not the same mutation: first {first.get('gene')}={first.get('value')}, second {second.get('gene')}={second.get('value')}"}
    if int(second["slice_from_seq"]) < int(first["slice_to_seq"]):
        return {"adopt": False, "keep_pending": True,
                "reason": f"the confirmation slice starts at seq {second['slice_from_seq']}, before the first slice's end {first['slice_to_seq']}: the slices overlap, so this is not a confirmation round"}
    if g2 != "IMPROVED":
        return {"adopt": False, "keep_pending": False, "reason": f"the confirmation round read {g2}: the first IMPROVED is not confirmed"}
    return {"adopt": True, "keep_pending": False, "reason": "IMPROVED twice on disjoint slices"}


def validate_bands(bands: dict) -> None:
    """Refuse a malformed BANDS file BY NAME rather than gate on a half-read one."""
    if not isinstance(bands, dict) or not isinstance(bands.get("dims"), dict):
        raise ValueError("bands: no `dims` object")
    cap = bands.get("cost_policy_cap")
    if not isinstance(cap, (int, float)) or isinstance(cap, bool) or not (cap > 0):
        raise ValueError(f"bands: `cost_policy_cap` must be a positive number, got {cap!r}")
    for d in GATED:
        if d not in bands["dims"]:
            raise ValueError(f"bands: the gated dimension {d!r} is missing")
    for d, b in bands["dims"].items():
        if not isinstance(b, dict) or b.get("kind") not in KINDS:
            raise ValueError(f"bands: dimension {d!r} has kind {None if not isinstance(b, dict) else b.get('kind')!r} (need one of {KINDS})")
        if b["kind"] == "normal":
            e = b.get("edge")
            if not isinstance(e, (int, float)) or isinstance(e, bool) or not (e >= 0):
                raise ValueError(f"bands: dimension {d!r} is `normal` and needs an edge >= 0, got {e!r}")
        if b["kind"] == "rank":
            r = b.get("range")
            if not isinstance(r, (int, float)) or isinstance(r, bool) or not (r >= 0):
                raise ValueError(f"bands: dimension {d!r} is `rank` and needs a range >= 0, got {r!r}")
        g = b.get("grid")
        if g is not None and not (isinstance(g, (int, float)) and g > 0):
            raise ValueError(f"bands: dimension {d!r} has a bad grid {g!r}")


def load_bands(path) -> dict:
    bands = json.loads(Path(path).read_text())
    validate_bands(bands)
    return bands
