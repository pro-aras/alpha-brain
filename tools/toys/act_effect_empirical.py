#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 12:01 +0400 — PREREG-ACT-EFFECT RESULT instrument (the architect's order after my 11:56 note): the EMPIRICAL ceilings of M2, M3, M4 — the signed screen (window 20, live iff >= 4 changes)
# run on forward's effect process BLOCK-BOOTSTRAPPED from the world's own recorded series (fixed random-3 play: no candidate was run to make them), beside the IID ceilings the signed law used. With both, every
# shortfall the bench reads can be classed: inside the gap between the iid and the empirical ceiling = the instrument's arithmetic (the law's iid assumption); BELOW the empirical ceiling = the mechanism
# (a hard live/dead screen that traps itself: forward dead -> the agent only turns -> the niche that made forward fail persists). Pure Python + numpy; `record` (the venv) writes the series.
"""tools/toys/act_effect_empirical.py

  record    (venv)  fixed random-3 play -> forward's known-effect series per seed; fixed uniform-7 play -> the four no-ops' series
  ceilings          the screen on (a) iid streams at the same marginal rates and (b) block-bootstrapped streams, per block length
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

import numpy as np

from tools.toys.act_chooser_toy import (ACT_NAMES, EFFECT_K, EFFECT_N, EXPLORE, EffectTracker, lock_pass, m4_readings, noop_share)

IID_NOOP_RATES = {3: 0.090, 4: 0.071, 5: 0.027, 6: 0.0}      # probe 2's rates under uniform play (§1.4)


class BootStream:
    """A block bootstrap of recorded 0/1 effect series: contiguous blocks of `block` outcomes, drawn at random, concatenated — the runs inside a block (the niche clusters) survive."""

    def __init__(self, series: Sequence[Sequence[int]], block: int, rng: np.random.Generator):
        self.series = [list(s) for s in series if len(s) >= block]
        if not self.series:
            raise ValueError(f"no recorded series is as long as the block ({block})")
        self.block = int(block)
        self.rng = rng
        self.buf: List[int] = []
        self.i = 0

    def _refill(self) -> None:
        s = self.series[int(self.rng.integers(0, len(self.series)))]
        start = int(self.rng.integers(0, len(s) - self.block + 1))
        self.buf, self.i = s[start:start + self.block], 0

    def next(self) -> int:
        if self.i >= len(self.buf):
            self._refill()
        v = self.buf[self.i]
        self.i += 1
        return v


class IIDStream:
    def __init__(self, p: float, rng: np.random.Generator):
        self.p, self.rng = float(p), rng

    def next(self) -> int:
        return int(self.rng.random() < self.p)


def _stream(src: Union[float, Sequence[Sequence[int]]], block: int, rng: np.random.Generator):
    return IIDStream(src, rng) if isinstance(src, (int, float)) else BootStream(src, block, rng)


def _one_life(rng: np.random.Generator, acts: int, forward, noops, block: int, n: int, k: int):
    streams = {2: _stream(forward, block, rng)}
    for a, r in IID_NOOP_RATES.items():
        streams[a] = _stream(noops[a] if noops and a in noops else r, block, rng)
    tr = EffectTracker(n, k)
    seq = np.zeros(acts, dtype=np.int8)
    hist: List[List[bool]] = []
    for i in range(acts):
        fl = tr.live_flags()
        hist.append(fl)
        if rng.random() < EXPLORE:
            a = int(rng.integers(0, 7))
        else:
            idx = [j for j in range(7) if fl[j]] or list(range(7))
            a = idx[int(rng.integers(0, len(idx)))]
        eff = 1 if a in (0, 1) else streams[a].next()
        tr.record(ACT_NAMES[a], eff)
        seq[i] = a
    return seq, hist


def simulate_lives(forward: Union[float, Sequence[Sequence[int]]], noops: Optional[Dict[int, Sequence[Sequence[int]]]], lives: int, acts: int, block: int, seed: int,
                   n: int = EFFECT_N, k: int = EFFECT_K) -> Dict[str, object]:
    """The signed screen on exogenous effect streams (forward: a float = iid at that rate, or a list of recorded series = block bootstrap; the no-ops likewise, iid at probe 2's rates when None).
    Returns the marks' ceilings: forward's dead-time after act 300, M2's pass share at 960 and at `acts`, M3, M4(a)/(b) (the toy's own readers, imported not re-derived)."""
    rng = np.random.default_rng([int(seed), int(block), int(acts)])
    dead, fshare, nshare, m2a, m2b, m3, m4a, m4b = [], [], [], [], [], [], [], []
    for _ in range(int(lives)):
        seq, hist = _one_life(rng, acts, forward, noops, block, n, k)
        dead.append(1.0 - sum(1 for f in hist[300:] if f[2]) / max(1, len(hist[300:])))
        tail = seq[240:]
        fshare.append(float((tail == 2).mean()))
        nshare.append(float(np.isin(tail, (3, 4, 5, 6)).mean()))
        if acts >= 960:
            m2a.append(bool(lock_pass(seq[:960])))
            m3.append(noop_share(seq) <= 0.25)
            a, b = m4_readings(hist)
            m4a.append(a >= 0.95)
            m4b.append(b)
        m2b.append(bool(lock_pass(seq)))
    out: Dict[str, object] = {"lives": int(lives), "acts": acts, "block": block, "forward_dead_time": float(np.mean(dead)), "forward_dead_time_sd_over_lives": float(np.std(dead)),
                              "forward_share": float(np.mean(fshare)), "noop_share": float(np.mean(nshare))}
    out[f"m2_pass_{acts}"] = float(np.mean(m2b))
    if acts >= 960:
        out["m2_pass_960"] = float(np.mean(m2a))
        out["m3_pass"] = float(np.mean(m3))
        out["m4a_pass"] = float(np.mean(m4a))
        out["m4b_pass"] = float(np.mean([b >= 0.95 for b in m4b]))
        out["m4b_median"] = float(np.median(m4b))
    else:
        out["m2_pass_960"] = out["m3_pass"] = out["m4a_pass"] = out["m4b_pass"] = out["m4b_median"] = None
    return out


def cmd_record(a) -> int:
    """(venv) the world's own series, under FIXED policies (no candidate): forward under random-3, the no-ops under uniform-7."""
    from tools.toys import act_chooser_toy as toy
    seeds = [int(s) for s in a.seeds.split(",")]
    fw: List[List[int]] = []
    noops: Dict[str, List[List[int]]] = {name: [] for name in ("pickup", "drop", "toggle", "done")}
    for s in seeds:
        r = toy.run_game_fx(toy.FixedDist(s, {0: 1.0, 1: 1.0, 2: 1.0}), s, a.episodes, keep_trace=10 ** 7)
        fw.append([t["effect"] for t in r["trace"] if t["act"] == "forward" and t["effect"] is not None])
        r7 = toy.run_game_fx(toy.FixedDist(s, {i: 1.0 for i in range(7)}), s, a.episodes, keep_trace=10 ** 7)
        for name in noops:
            noops[name].append([t["effect"] for t in r7["trace"] if t["act"] == name and t["effect"] is not None])
    out = {"policy": {"forward": "fixed random-3 (uniform over left, right, forward)", "noops": "fixed uniform-7"}, "seeds": seeds, "episodes": a.episodes,
           "forward": fw, "noops": noops, "forward_outcomes": sum(len(x) for x in fw), "forward_rate": sum(sum(x) for x in fw) / sum(len(x) for x in fw)}
    Path(a.out).write_text(json.dumps(out))
    print(f"[record] forward outcomes {out['forward_outcomes']}, rate {out['forward_rate']:.4f} -> {a.out}")
    return 0


def cmd_ceilings(a) -> int:
    data = json.loads(Path(a.series).read_text())
    fw = data["forward"]
    noops = {3: data["noops"]["pickup"], 4: data["noops"]["drop"], 5: data["noops"]["toggle"], 6: data["noops"]["done"]}
    rate = data["forward_rate"]
    rows: List[Dict[str, object]] = []
    iid = simulate_lives(rate, None, a.lives, a.acts, 1, a.seed)
    iid["kind"] = f"iid at forward {rate:.3f}"
    rows.append(iid)
    for b in [int(x) for x in a.blocks.split(",")]:
        r = simulate_lives(fw, noops, a.lives, a.acts, b, a.seed)
        r["kind"] = f"block bootstrap, block {b} (forward + no-ops from the recorded series)"
        rows.append(r)
    keys = ("forward_dead_time", "m2_pass_960", f"m2_pass_{a.acts}", "m3_pass", "m4a_pass", "m4b_pass", "m4b_median", "forward_share", "noop_share")
    print(f"{'kind':74s} " + " ".join(f"{k:>16s}" for k in keys))
    for r in rows:
        print(f"{r['kind']:74s} " + " ".join(f"{r[k]:16.4f}" for k in keys))
    Path(a.out).write_text(json.dumps({"series": a.series, "lives": a.lives, "acts": a.acts, "rows": rows}, indent=1))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("--seeds", default="20260923,21260923,22260923")
    r.add_argument("--episodes", type=int, default=300)
    r.add_argument("--out", required=True)
    c = sub.add_parser("ceilings")
    c.add_argument("--series", required=True)
    c.add_argument("--blocks", default="50,100,200")
    c.add_argument("--lives", type=int, default=600)
    c.add_argument("--acts", type=int, default=4920)
    c.add_argument("--seed", type=int, default=20261008)
    c.add_argument("--out", required=True)
    a = ap.parse_args(list(argv) if argv is not None else None)
    return {"record": cmd_record, "ceilings": cmd_ceilings}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
