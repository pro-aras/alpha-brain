"""phase0_oracle_states.py — READ-ONLY offline check of the curiosity signals at S1c's ORACLE decision points (TOY A, phase 0).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 10:55 +0400 — new module. Reads S1c's saved law-world ORACLE records only
# (/data/dev/brain-runs/scene-s1c/<seed>/runs/law/ORACLE.json); runs no life, writes nothing but stdout. It EXISTS because the
# ORACLE's record carries, at every policy decision, the TRUE next-block gain of EVERY room (a clone trained on that room's
# next block: words-learned gain, M1 gain), so any choice rule's ONE-STEP value can be read exactly at those states with no
# run. It is the world's own count for the PREREG (docs/research/toys/PREREG-TOY-CP.md): does the world offer a choice at
# all, how much of it is «leave the noise room», and which signal points the right way.

CAVEAT (stated in the PREREG): the states are the ORACLE's (a learner that has learned most words), the values are ONE step
and OFF-policy; a signal's value here is a reading about the signal, never a prediction of a life's A.

THE NULL AND THE PLANTS (the instrument's own controls, printed every run):
  * dealt-gains null: at every decision the four rooms' gains are DEALT to other rooms (a random permutation), 2,000 draws; a
    signal's argmax value is read against that distribution (a signal that predicts nothing sits at the random-pick value).
  * PLANT-PERFECT: the true gain as a signal must read the best-room value EXACTLY, and sit far outside the null.
  * PLANT-ANTI: minus the true gain must read the worst-room value EXACTLY.
  * the presence count: the field `gains` must be present on every policy row read (#168).

  PYTHONPATH=. python3 -m tools.toys.cp.phase0_oracle_states [--root DIR] [--seeds 20261301,20261302,20261303]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path("/data/dev/brain-runs/scene-s1c")
SEEDS: Tuple[int, ...] = (20261301, 20261302, 20261303)
ROOMS: Tuple[str, ...] = ("R1", "R2", "R3", "N")
BLOCK = 10                      # scenes per block (S1c's B)
EMA_A = (0.1, 0.3)              # the time-scale readings (0.1 is the PREREG's declared a)
NULL_DRAWS = 2000
RNG_SEED = 20261003


class Phase0Error(Exception):
    pass


def load_oracle(root: Path, seed: int) -> Dict[str, object]:
    p = Path(root) / str(seed) / "runs" / "law" / "ORACLE.json"
    d = json.loads(p.read_text())
    if d.get("picker") != "ORACLE" or list(d["rooms"]) != list(ROOMS):
        raise Phase0Error(f"{p}: not the law world's ORACLE record")
    return d


def ema(values: Sequence[float], a: float) -> Optional[float]:
    """The PREREG's EMA: the first reward initialises, then est <- (1 - a) est + a r at every later visit."""
    if not values:
        return None
    s = float(values[0])
    for y in values[1:]:
        s = (1.0 - a) * s + a * float(y)
    return s


def last2(values: Sequence[float]) -> Optional[float]:
    return float(np.mean(values[-2:])) if values else None


def signals_at(rec: Sequence[Dict[str, object]], table: Sequence[Dict[str, float]], b: int) -> Dict[str, Dict[str, Optional[float]]]:
    """Every signal's per-room estimate at the decision BEFORE block b (blocks < b are the history).

    own reward of block c in room r:  L_r(c-1) - L_r(c)                                    (S1c's drop)
    hist reward of block c in room r: sum_j n_j(c) (L_j(c-1) - L_j(c)) / sum_j n_j(c), n_j(c) = scenes experienced in room j
                                      through block c (BLOCK per visit, the round-robin included) — the HISTORY SO FAR as the
                                      compressor's test data (Schmidhuber A.5: «both the old and the new compressor have to be
                                      tested on the same data, namely, the history so far»), weights normalised to sum 1."""
    own: Dict[str, List[float]] = {r: [] for r in ROOMS}
    hist: Dict[str, List[float]] = {r: [] for r in ROOMS}
    visits = {r: 0 for r in ROOMS}
    for x in rec:
        c = int(x["block"])
        if c >= b:
            break
        r = str(x["room"])
        visits[r] += 1
        n = {j: BLOCK * visits[j] for j in ROOMS}
        tot = float(sum(n.values()))
        own[r].append(table[c - 1][r] - table[c][r])
        hist[r].append(sum(n[j] * (table[c - 1][j] - table[c][j]) for j in ROOMS) / tot)
    out: Dict[str, Dict[str, Optional[float]]] = {"ERROR": {r: float(table[b - 1][r]) for r in ROOMS},
                                                  "L-own-last2": {r: last2(own[r]) for r in ROOMS},
                                                  "L-hist-last2": {r: last2(hist[r]) for r in ROOMS}}
    for a in EMA_A:
        out[f"L-own-ema{a}"] = {r: ema(own[r], a) for r in ROOMS}
        out[f"L-hist-ema{a}"] = {r: ema(hist[r], a) for r in ROOMS}
    return out


def decision_points(root: Path, seeds: Sequence[int]) -> Tuple[List[Dict[str, object]], Dict[str, int]]:
    rows: List[Dict[str, object]] = []
    seen = {"policy_rows": 0, "with_gains": 0, "round_robin_rows": 0}
    for s in seeds:
        d = load_oracle(root, s)
        rec, table = d["record"], d["table"]
        for x in rec:
            if x["flag"] == "round-robin":
                seen["round_robin_rows"] += 1
                continue
            if x["flag"] != "policy":
                continue
            seen["policy_rows"] += 1
            g = x.get("gains")
            if g is None:
                continue
            seen["with_gains"] += 1
            rows.append({"seed": s, "block": int(x["block"]),
                         "g_wl": {r: float(g[r][0]) for r in ROOMS},
                         "g_m1": {r: (float(g[r][1]) if g[r][1] is not None else 0.0) for r in ROOMS},
                         "sig": signals_at(rec, table, int(x["block"])), "oracle_room": x["room"]})
    return rows, seen


def argmax_room(sig: Dict[str, Optional[float]], sign: float = 1.0) -> Optional[str]:
    if any(v is None for v in sig.values()):
        return None
    return max(ROOMS, key=lambda r: (sign * sig[r], r))      # ties -> the later name (the PREREG's rule is least-recently-visited; a tie is measure zero here)


def value_of(rows: Sequence[Dict[str, object]], key: str, pick) -> Tuple[float, int]:
    vals = []
    for r in rows:
        k = pick(r)
        if k is not None:
            vals.append(r[key][k])
    return (float(np.mean(vals)) if vals else float("nan")), len(vals)


def dealt_null(rows: Sequence[Dict[str, object]], key: str, name: str, rng: np.random.Generator, draws: int = NULL_DRAWS) -> np.ndarray:
    """The signal's argmax picks stay; the four gains of every decision are DEALT to random rooms (#247 (1))."""
    picks = [argmax_room(r["sig"][name]) for r in rows]
    idx = [i for i, k in enumerate(picks) if k is not None]
    pos = np.array([ROOMS.index(picks[i]) for i in idx])
    G = np.array([[rows[i][key][r] for r in ROOMS] for i in idx])        # (n, 4)
    out = np.empty(draws)
    for d in range(draws):
        perm = np.argsort(rng.random(G.shape), axis=1)                    # an independent permutation per decision
        out[d] = float(np.mean(G[np.arange(len(idx)), perm[np.arange(len(idx)), pos]]))
    return out


def report(root: Path = ROOT, seeds: Sequence[int] = SEEDS, log=print) -> Dict[str, object]:
    rows, seen = decision_points(root, seeds)
    if not rows:
        raise Phase0Error("no decision points read")
    rng = np.random.default_rng(RNG_SEED)
    log(f"PHASE 0 — S1c's ORACLE decision points, law world, seeds {list(seeds)} (root {root})")
    log(f"presence: policy rows {seen['policy_rows']} · carrying `gains` {seen['with_gains']} · round-robin rows (no gains, not decisions) {seen['round_robin_rows']}")
    if seen["with_gains"] != seen["policy_rows"]:
        raise Phase0Error(f"the field `gains` is present on {seen['with_gains']} of {seen['policy_rows']} policy rows")
    out: Dict[str, object] = {"n": len(rows), "seen": seen}
    for key, label in (("g_wl", "WORDS-LEARNED gain of the room's next block (words)"), ("g_m1", "M1 gain of the room's next block")):
        log(f"\n== {label}: the true one-step gain by room, all {len(rows)} decisions")
        by_room = {}
        for r in ROOMS:
            v = np.array([x[key][r] for x in rows])
            by_room[r] = float(v.mean())
            log(f"   {r}: mean {v.mean():+.4f}  sd {v.std():.4f}  share>0 {np.mean(v > 0):.2f}  share<0 {np.mean(v < 0):.2f}")
        rnd = float(np.mean([np.mean([x[key][r] for r in ROOMS]) for x in rows]))
        ronly = float(np.mean([np.mean([x[key][r] for r in ROOMS if r != "N"]) for x in rows]))
        best = float(np.mean([max(x[key].values()) for x in rows]))
        worst = float(np.mean([min(x[key].values()) for x in rows]))
        orc = float(np.mean([x[key][x["oracle_room"]] for x in rows]))
        log(f"   value of a RANDOM pick {rnd:+.4f} · of a uniform pick over R1-R3 only (never N) {ronly:+.4f} · of the BEST-room pick {best:+.4f} · of the WORST-room pick {worst:+.4f} · of the ORACLE's own pick {orc:+.4f}")
        log(f"   the share of the whole spread (best - random) that «never N» captures: {(ronly - rnd) / (best - rnd):.3f}")
        res = {"by_room": by_room, "random": rnd, "r_only": ronly, "best": best, "worst": worst, "oracle_pick": orc, "signals": {}}
        # the planted signals: the true gain (and its negative) as a «signal» must read the best (worst) room's value EXACTLY,
        # whatever the tie-break, because the room it picks carries the maximum (minimum) of that very key
        for pname, sgn, want in (("PLANT-PERFECT", 1.0, best), ("PLANT-ANTI", -1.0, worst)):
            v = float(np.mean([x[key][max(ROOMS, key=lambda r: (sgn * x[key][r], r))] for x in rows]))
            ok = abs(v - want) < 1e-12
            log(f"   {pname:14s} value {v:+.4f} (must equal the {'best' if sgn > 0 else 'worst'}-room value {want:+.4f}) -> {'CAUGHT/OK' if ok else 'PLANT FAILED'}")
            if not ok:
                raise Phase0Error(f"{pname} read {v} not {want}")
        names = list(rows[0]["sig"])
        log(f"   {'signal':16s} {'argmax value':>13s} {'null mean±sd':>16s} {'z':>7s} {'argmin value':>13s} {'picks N':>8s} {'best room':>10s} {'n':>5s}")
        for nme in names:
            v_arg, n = value_of(rows, key, lambda r, nme=nme: argmax_room(r["sig"][nme]))
            v_min, _ = value_of(rows, key, lambda r, nme=nme: argmax_room(r["sig"][nme], -1.0))
            nul = dealt_null(rows, key, nme, rng)
            z = (v_arg - nul.mean()) / nul.std() if nul.std() > 0 else float("nan")
            picks = [argmax_room(r["sig"][nme]) for r in rows]
            share_n = float(np.mean([p == "N" for p in picks if p is not None]))
            share_best = float(np.mean([r[key][p] == max(r[key].values()) for r, p in zip(rows, picks) if p is not None]))
            log(f"   {nme:16s} {v_arg:+13.4f} {nul.mean():+9.4f}±{nul.std():.4f} {z:+7.2f} {v_min:+13.4f} {share_n:8.2f} {share_best:10.2f} {n:5d}")
            res["signals"][nme] = {"argmax": v_arg, "argmin": v_min, "null_mean": float(nul.mean()), "null_sd": float(nul.std()), "z": z,
                                   "picks_N": share_n, "picks_best": share_best, "n": n}
        out[key] = res
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--seeds", default=",".join(str(s) for s in SEEDS))
    a = ap.parse_args(argv)
    report(a.root, [int(s) for s in a.seeds.split(",")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
