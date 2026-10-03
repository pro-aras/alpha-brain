#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:16 +0400 — PREREG-EVOLVE-CAL AMENDMENT 3 (A3.4, A3.6, A3.7): the N1 analysis. Tests first: tests/tools/test_evolve_cal_analyse.py.
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:51 +0400 — AMENDMENT 3b (the verifier's E1, E2, E3 and limits (1), (5)): ONE test, MOVE, releases Stage A and chooses the level;
# EQUALS counts an unmatched moment row (`moment_flips`); frames_filed is printed and never releases; Stage B takes its rule explicitly; both-sided ceilings for all three dimensions.
"""tools/evolve_cal_analyse.py — from the twins' readings to the null arrays, the staged decisions and the BANDS file.

Pure functions over reading dicts (a twin's `reading.json`); `tools/evolve_cal.py` builds the bands (scipy), this module decides WHICH twins go into which null and what the
staged design does next (AMENDMENT 3, A3.6, as amended by A3b):

  MOVE       an epsilon twin MOVES iff its q1_seen or its confirmed_share differs from the incumbent's (exactly; a missing reading is REFUSED); a level moves iff a twin at it does.
             frames_filed moves with the think stream the seed twins bound: it is printed beside every decision and releases nothing (the verifier's limit 1);
  Stage A0   the incumbent + one epsilon twin at 1e-3 and one at 1e-2 on the full slice: NON-DEGENERATE iff at least one epsilon twin MOVES;
  Stage A0+  (only if A0 found nothing) four more: DEGENERATE iff none of the six MOVES; the 95 % upper bound on the per-twin chance of a move is 1 − 0.05^(1/6) ≈ 0.39;
  A3.4/A3b.2 the chosen level is the smallest at which a twin MOVES; a larger level whose twins' RMS deviation exceeds FLAT_FACTOR × the chosen level's, in q1_seen or
             confirmed_share, is labelled `spread_grows` (A1 (ii)'s merit step) — a LABEL: the band is always the null at the chosen level;
  A3b.1      a twin EQUALS the incumbent iff no moment row is unmatched or discretely different (`moment_flips == 0`) AND its three readings are equal; the other kinds' discrete
             payloads are outside that rule and are printed;
  Stage B    the other 15 twins at the chosen level: rule S (as signed in A3.6: the six values hold >= 3 distinct values in some gated dimension) or rule M (the builder's
             alternative: some twin of the level MOVES); the rule is an explicit argument — the signers have not chosen;
  A3.7       a degenerate dimension has NO band (reading A) or the band of its null's own range floored at one resolvable step (reading B); every band is printed beside
             its dimension's ceiling on both sides (A3b.5).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence

import tools.evolve_cal as cal
from tools import evolve_bands as eb

GATED = eb.GATED                       # ("q1_seen", "frames_filed", "confirmed_share")
MOVE_DIMS = ("q1_seen", "confirmed_share")   # the readings the seed never reaches (A1): the only ones a MOVE, the release of Stage A and the choice of a level read
Q1_ITEMS = 110
FLAT_FACTOR = 2.0                      # the RMS deviation of a larger level over the chosen level's, above which the larger level is labelled `spread_grows` (strictly more)
GROWTH_FACTOR = FLAT_FACTOR            # the name A3's code gave it
_FLAT_TOL = 1e-9                       # relative: «exactly twice» is not a growth whatever the float noise of an items-to-fraction round trip
FLATNESS_NOTE = ("the readings respond to epsilon above the chosen level; the band is the noise at the smallest perturbation that moves a reading, "
                 "not the response of a mutation-sized change")


def readings_equal(a: dict, b: dict) -> bool:
    """The three gated readings equal, exactly; a None on either side is not equal (a missing reading is never a match)."""
    for d in GATED:
        x, y = a.get(d), b.get(d)
        if x is None or y is None or x != y:
            return False
    return True


def _need(r: dict, d: str, who: str):
    v = r.get(d)
    if v is None:
        raise ValueError(f"{who}: no {d!r} reading (refused: a missing reading is never read as a move or as a hold)")
    return v


def moved_dims(inc: dict, reading: dict) -> List[str]:
    """The MOVE_DIMS in which a twin's reading differs from the incumbent's (A3b.2). frames_filed is not among them; a missing reading on either side is REFUSED."""
    return [d for d in MOVE_DIMS if _need(inc, d, "the incumbent") != _need(reading, d, "a twin")]


def _moved(inc: dict, twins: Dict[str, dict]) -> Dict[str, List[str]]:
    """{dimension: [twin labels]} over ALL THREE gated readings (frames_filed is printed here, and filtered out of the decisions); a missing reading is refused."""
    out: Dict[str, List[str]] = {}
    for label, r in twins.items():
        for d in GATED:
            if _need(inc, d, "the incumbent") != _need(r, d, f"twin {label}"):
                out.setdefault(d, []).append(label)
    return out


def twin_record(label: str, reading: dict, comparison: dict) -> dict:
    """A twin as the analysis reads it: its readings, its moment FLIPS (A3b.1: discretely different + unmatched rows) and the other kinds' discrete payloads, from a
    `compare_twins_keyed` result. A comparison without `moment.flips` (the shape before A3b) is refused: it cannot say whether the twin EQUALS the incumbent."""
    m = comparison.get("moment") or {}
    for k in ("flips", "only_a", "only_b", "discrete_differing"):
        if k not in m:
            raise ValueError(f"twin_record({label}): the comparison carries no moment.{k} (refused: an old-shape comparison cannot say whether the twin EQUALS the incumbent)")
    return {"label": label, "reading": reading, "moment_flips": int(m["flips"]), "moment_unmatched": int(m["only_a"]) + int(m["only_b"]),
            "moment_discrete_differing": int(m["discrete_differing"]), "other_discrete": dict(comparison.get("other_discrete") or {})}


def _flips(t: dict) -> int:
    if t.get("moment_flips") is None:
        raise ValueError(f"twin {t.get('label')!r}: no moment_flips (refused: without the flip count the twin cannot be said to EQUAL the incumbent)")
    return int(t["moment_flips"])


def twin_equals(inc: dict, twin: dict) -> bool:
    """A3b.1: EQUALS iff no moment row is unmatched or discretely different AND the three readings equal the incumbent's."""
    return _flips(twin) == 0 and readings_equal(inc, twin["reading"])


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
    """Stage A0 (A3b.2): NON-DEGENERATE iff a twin MOVES (q1_seen or confirmed_share); a frames_filed-only difference is printed in `moved` and releases nothing."""
    moved = _moved(inc, eps_twins)
    release = [d for d in MOVE_DIMS if d in moved]
    return {"non_degenerate": bool(release), "moved": moved, "release_dims": release, "frames_only": bool(moved) and not release, "n_twins": len(eps_twins)}


def a0plus_decision(inc: dict, six_twins: Dict[str, dict]) -> dict:
    n = len(six_twins)
    if n < 6:
        raise ValueError(f"a0plus_decision: {n} epsilon twins (the rule needs all six: the two of A0 and the four of A0+)")
    moved = _moved(inc, six_twins)
    release = [d for d in MOVE_DIMS if d in moved]
    return {"degenerate": not release, "moved": moved, "release_dims": release, "n_twins": n, "upper_bound_p": 1.0 - 0.05 ** (1.0 / n)}


def stage_b_condition(inc: dict, five_twins: Sequence[dict], rule: str) -> dict:
    """Stage B (the other 15 twins at the chosen level), under a rule the CALLER names — the signers have not chosen (A3b.3, RAISED):
    S (as signed in A3.6): some gated dimension of [incumbent + the chosen level's five twins] holds >= 3 distinct values, where a band A1 (i) would grant could exist;
    M (the builder's alternative): some twin of the level MOVES (q1_seen or confirmed_share); at the chosen level that is true by construction of the choice."""
    if rule not in ("S", "M"):
        raise ValueError(f"stage_b_condition: rule must be 'S' or 'M', got {rule!r}")
    if rule == "S":
        dims = [d for d in GATED if len({x[d] for x in [inc, *five_twins] if x.get(d) is not None}) >= 3]
    else:
        dims = [d for d in MOVE_DIMS if any(_need(inc, d, "the incumbent") != _need(t, d, "a twin") for t in five_twins)]
    return {"rule": rule, "run": bool(dims), "dims": dims, "n_values": 1 + len(five_twins)}


def _rms_dev(inc: dict, twins: Sequence[dict], d: str) -> float:
    xs: List[float] = []
    for t in twins:
        x, y = _need(inc, d, "the incumbent"), _need(t["reading"], d, f"twin {t.get('label')}")
        xs.append(float(round((y - x) * Q1_ITEMS)) if d == "q1_seen" else float(y - x))   # q1_seen in whole items, the others in their own units
    return math.sqrt(sum(v * v for v in xs) / len(xs)) if xs else 0.0


def choose_level(inc: dict, levels: Dict[float, Sequence[dict]]) -> dict:
    """`levels`: epsilon -> its twins, each a `twin_record` {label, reading, moment_flips, other_discrete}. A3b.2: the chosen level is the SMALLEST at which some twin MOVES
    (q1_seen or confirmed_share differs from the incumbent's). A discrete flip with no reading moved is printed (`flip_without_move`) and chooses nothing; the flatness read looks
    ABOVE the chosen level: a larger level whose RMS deviation exceeds FLAT_FACTOR × the chosen one's in some MOVE dimension is `spread_grows`, a label, never the null."""
    per: Dict[float, dict] = {}
    for eps in sorted(levels):
        tw = list(levels[eps])
        moved: Dict[str, List[str]] = {}
        frames_moved: List[str] = []
        n_moved = flips = equal = 0
        move_without_flip = other_flip = False
        for t in tw:
            label = t.get("label")
            md = moved_dims(inc, t["reading"])
            f = _flips(t)
            flips += f
            if md:
                n_moved += 1
                for d in md:
                    moved.setdefault(d, []).append(label)
                if f == 0:
                    move_without_flip = True
            if _need(inc, "frames_filed", "the incumbent") != _need(t["reading"], "frames_filed", f"twin {label}"):
                frames_moved.append(label)
            if twin_equals(inc, t):
                equal += 1
            if t.get("other_discrete") and f == 0:
                other_flip = True
        per[eps] = {"n": len(tw), "twins_moved": n_moved, "moved": moved, "frames_moved": frames_moved, "flips": flips, "twins_equal_to_incumbent": equal,
                    "flip_without_move": flips > 0 and n_moved == 0, "reading_move_without_flip": move_without_flip, "other_kind_flip_moment_rows_equal": other_flip,
                    "rms_dev": {d: _rms_dev(inc, tw, d) for d in GATED}, "spread_grows": False}
    moving = [e for e in sorted(per) if per[e]["twins_moved"] > 0]
    chosen: Optional[float] = moving[0] if moving else None
    grows = False
    if chosen is not None:
        base = per[chosen]["rms_dev"]
        for e in sorted(per):
            if e <= chosen:
                continue
            per[e]["spread_grows"] = any(per[e]["rms_dev"][d] > FLAT_FACTOR * base[d] * (1.0 + _FLAT_TOL) and per[e]["rms_dev"][d] > 0 for d in MOVE_DIMS)
            grows = grows or per[e]["spread_grows"]
    return {"chosen": chosen, "per_level": per, "flat_factor": FLAT_FACTOR, "flatness_note": FLATNESS_NOTE if grows else None}


def _ceiling(d: str, inc: dict, band: dict) -> dict:
    """A3b.5: the dimension's ceiling printed on BOTH sides beside its band. REGRESSED is unreachable when the half-width is not below the incumbent's own reading (a fall cannot
    exceed it), IMPROVED when it is not below the headroom. A bandless dimension is read against the LEGACY tolerance (A′, the seat's ruling): any fall regresses, a rise needs
    its margin (tools/evolve.py MARGINS)."""
    reading = inc.get(d)
    if reading is None:
        return {"reading": None, "unit": None, "up_room": None, "down_room": None, "improved_reachable": None, "regressed_reachable": None,
                "basis": "no incumbent reading", "note": "the incumbent carries no reading for this dimension"}
    half = eb._half(band)
    margin = cal.ev.MARGINS[d]
    if d == "q1_seen":
        items = round(float(reading) * Q1_ITEMS)
        shown, up, down, unit = items, Q1_ITEMS - items, items, "items of 110"
        half_u = None if half is None else half * Q1_ITEMS
        margin_u = margin * Q1_ITEMS
    elif d == "confirmed_share":
        shown, up, down, unit = float(reading), 1.0 - float(reading), float(reading), "share (0..1)"
        half_u, margin_u = half, margin
    else:
        shown, up, down, unit = float(reading), None, float(reading), "frames (no ceiling known)"
        half_u, margin_u = half, margin
    if half_u is not None:
        basis = "band"
        improved = True if up is None else bool(half_u < up)
        regressed = bool(half_u < down)
        edge_txt = f"half-width {half_u:.6g} {unit}"
    else:
        basis = "no band: the legacy tolerance (A′): any fall regresses, a rise needs its margin"
        improved = True if up is None else bool(up + 1e-12 >= margin_u)
        regressed = bool(down > 0)
        edge_txt = f"legacy margin {margin_u:.6g} {unit}"
    parts = [f"reading {shown:.6g} ({unit}); {edge_txt}; room up {'unbounded' if up is None else f'{up:.6g}'}, room down {down:.6g}"]
    if not improved:
        parts.append("IMPROVED UNREACHABLE: the bar is not below the headroom (a bar above its own ceiling)")
    if not regressed:
        parts.append("REGRESSED UNREACHABLE: the bar is not below the incumbent's own reading")
    if improved and regressed:
        parts.append("both sides reachable")
    return {"reading": shown, "unit": unit, "up_room": up, "down_room": down, "improved_reachable": improved, "regressed_reachable": regressed, "basis": basis, "note": "; ".join(parts)}


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
    for d in GATED:
        b["dims"][d]["ceiling"] = _ceiling(d, inc, b["dims"][d])
    eb.validate_bands(b)
    return b
