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
import re
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


STAGE_B_RULE = "M"      # RULED by the seat on 2026-10-03 23:36 (AMENDMENT 3b's raised rule): Stage B runs whenever a twin of the chosen level MOVES — it restores the law's own N1 design at epsilon* (21 values)


def stage_b_decision(inc: dict, five_twins: Sequence[dict]) -> dict:
    """Stage B under the rule the seat ruled (STAGE_B_RULE = M). `stage_b_condition` still takes its rule explicitly (S is kept for the record and for the comparison the signers saw)."""
    return stage_b_condition(inc, five_twins, rule=STAGE_B_RULE)


_VARIANT_EPS = re.compile(r"eps:([0-9.eE+-]+):([0-9]+)\Z")
MIN_TERCILE_TWINS = 9          # three twins in each tercile at the least; fewer and no terciles are computed (said, never silent)
SELECTION_NOTE_MOVED = ("epsilon* is the smallest level at which a twin moved a reading (A3b.2): this null is conditioned on a move and is wider than the true noise "
                        "(the verifier's limit 3, printed beside every band as the seat ruled 23:36)")
SELECTION_NOTE_FLAT = "no twin moved q1_seen or confirmed_share: no level was selected on a move and the null is flat"
LR_RECORD_NOTE = "the record's DELTA lr mutations were 0.05 -> 0.07 and 0.09 (+40 % and +80 %)"


def _eps_k(twin: dict):
    m = _VARIANT_EPS.match(str(twin.get("variant", "")))
    return (float(m.group(1)), int(m.group(2))) if m else None


def _unit(d: str) -> str:
    return {"q1_seen": "items of 110", "confirmed_share": "share", "frames_filed": "frames"}.get(d, "")


def null_provenance(inc: dict, eps_twins: Sequence[dict]) -> dict:
    """What the epsilon null IS, printed beside every band (the seat's 23:36 ruling on the verifier's limits 2 and 3): the twins' perturbation (1 + k × epsilon) on DELTA lr, the RMS deviation
    from the incumbent by TERCILE of that perturbation with the label «top tercile grows» (strictly more than FLAT_FACTOR × the bottom tercile's), and the SELECTION note (a null in which a
    twin moved is conditioned on a move). A twin without a parseable `eps:<level>:<k>` variant is counted and said, never hidden."""
    n = len(eps_twins)
    good = [(lk, t) for lk, t in ((_eps_k(t), t) for t in eps_twins) if lk is not None]
    unparsed = n - len(good)
    levels = sorted({lk[0] for lk, _ in good})
    eps = levels[0] if len(levels) == 1 else None
    pert = None
    if good:
        ps = [1.0 + k * lv for (lv, k), _ in good]
        pert = [min(ps), max(ps)]
    moved_any = any(moved_dims(inc, t) for t in eps_twins)
    if pert is None:
        perturbation_note = f"variant unknown for {unparsed} of {n} twins: the perturbation (1 + k × epsilon) cannot be printed"
    else:
        where = f"epsilon {levels[0]!r}" if eps is not None else "epsilon levels " + ", ".join(repr(x) for x in levels)
        ks = [k for (_, k), _ in good]
        perturbation_note = (f"the twins' perturbation (1 + k × epsilon) on DELTA lr runs {pert[0]:.4g} … {pert[1]:.4g} ({where}, k = {min(ks)}..{max(ks)}, "
                             f"{len(good)} of {n} twins; {LR_RECORD_NOTE})" + (f"; variant unknown for {unparsed} of {n} twins" if unparsed else ""))
    terciles = None
    top_grows = {d: False for d in GATED}
    if len(good) >= MIN_TERCILE_TWINS:
        srt = sorted(good, key=lambda x: (1.0 + x[0][1] * x[0][0], x[0][1]))
        base, extra = divmod(len(srt), 3)
        sizes = [base + (1 if i < extra else 0) for i in range(3)]
        terciles, start = [], 0
        for s in sizes:
            g = srt[start:start + s]
            start += s
            ps = [1.0 + k * lv for (lv, k), _ in g]
            as_twins = [{"label": f"k{k}", "reading": t} for (_, k), t in g]
            terciles.append({"n": len(g), "k": [min(k for (_, k), _ in g), max(k for (_, k), _ in g)], "perturbation": [min(ps), max(ps)],
                             "rms_dev": {d: _rms_dev(inc, as_twins, d) for d in GATED}})
        for d in GATED:
            lo, hi = terciles[0]["rms_dev"][d], terciles[2]["rms_dev"][d]
            top_grows[d] = bool(hi > FLAT_FACTOR * lo * (1.0 + _FLAT_TOL) and hi > 0)
        tercile_note = "RMS deviation by k-tercile is printed per dimension"
    else:
        tercile_note = f"fewer than {MIN_TERCILE_TWINS} twins ({len(good)} with a variant): no k-terciles are computed"
    return {"epsilon": eps, "levels": levels, "n_twins": n, "unparsed": unparsed, "perturbation": pert, "perturbation_note": perturbation_note, "terciles": terciles,
            "tercile_note": tercile_note, "top_tercile_grows": top_grows, "selected_on_a_move": bool(moved_any),
            "selection_note": SELECTION_NOTE_MOVED if moved_any else SELECTION_NOTE_FLAT}


def _null_notes(prov: dict, d: str) -> List[str]:
    """The lines printed beside the band of dimension `d`: the selection note, the perturbation, and (for a gated dimension) the RMS by tercile with its label."""
    notes = [prov["selection_note"], prov["perturbation_note"]]
    if d in GATED:
        if prov["terciles"] is None:
            notes.append(prov["tercile_note"])
        else:
            t = prov["terciles"]
            parts = " / ".join(f"{x['rms_dev'][d]:.3g}" for x in t)
            ks = " / ".join(f"k {x['k'][0]}–{x['k'][1]}" for x in t)
            label = (f"top tercile GROWS (> {FLAT_FACTOR} × the bottom tercile's): the top of the range is mutation-sized and the band may include merit, not only noise"
                     if prov["top_tercile_grows"][d] else f"the top tercile does not grow (not more than {FLAT_FACTOR} × the bottom tercile's)")
            notes.append(f"RMS deviation of {d} by k-tercile ({_unit(d)}): {parts} ({ks}) — {label}")
    else:
        notes.append("the cost null is the epsilon twins' ln CPU-seconds: " + prov["tercile_note"])
    return notes


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


def bands_from_twins(inc: dict, eps_twins: Sequence[dict], seed_twins: Optional[Sequence[dict]], slice_name: str, scope: str, degenerate: str = "legacy") -> dict:
    """The BANDS file from the incumbent + the chosen level's epsilon twins (the null of every dimension) and the seed twins (frames_filed's A2.2 null, the incumbent among them).
    degenerate = «legacy» (the DEFAULT — reading A′, the seat's ruling of 2026-10-03 22:32 on A3.7, extended by the seat's line on A3b at 23:36 to EVERY dimension left without a measured
    band in EVERY branch: it keeps the LEGACY tolerance — any fall regresses, a rise needs its margin, tools/evolve.py MARGINS), «none» (reading A: a dimension without a band does not gate —
    never the default, «a calibration never loosens», kept only to replay the readings the signers refused) or «range» (reading B: the band of its null's own range, floored at one
    resolvable step; not ruled). Every band carries beside it `null_notes` (the twins' perturbation (1 + k × epsilon), the RMS deviation by k-tercile with its label, the selection note)
    and the file carries `null`, the same facts as data (the verifier's limits 2 and 3, printed as the seat ruled)."""
    if degenerate not in ("none", "range", "legacy"):
        raise ValueError(f"bands_from_twins: degenerate must be 'none', 'range' or 'legacy', got {degenerate!r}")
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
    elif degenerate == "legacy":
        for d in GATED:
            band = b["dims"][d]
            if band["kind"] == "none":
                band["legacy"] = {"fall": "any", "rise_margin": cal.ev.MARGINS[d],
                                  "basis": "A′ (the seat's ruling of 2026-10-03 22:32 on A3.7): the calibration measured no noise for this dimension at the perturbations that reach the "
                                           "organism, so its tolerance is the pre-law one (tools/evolve.py MARGINS), not a measured one"}
        b["degenerate_reading"] = "A′: a bandless dimension keeps the legacy tolerance (any fall regresses, a rise needs its margin) — a pre-law tolerance, not a measured one"
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
    prov = null_provenance(inc, eps_twins)
    b["null"] = prov
    for d, band in b["dims"].items():
        band["null_notes"] = _null_notes(prov, d)
    eb.validate_bands(b)
    return b
