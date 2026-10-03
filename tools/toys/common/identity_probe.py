"""identity_probe.py — HARNESS VALIDATION for the TOYS lane: does THIS tree, on the pools it redrew, reproduce the records the earlier
rounds saved? No hypothesis, no mechanism code: the earlier rounds' own functions run on this tree's pools and are diffed with the
earlier rounds' own records.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:18 +0400 — new module (promoted from two scratch probes run at 11:1x; the
# outputs are kept in docs/research/toys/PROBE-IDENTITY.out). It was run BEFORE any toy code because both laws rest on their G2
# (a life of the toy equals the earlier record) and #246 (8) records that a state hash on this box moved with the BLAS thread count.

  PYTHONPATH=. python3 -m tools.toys.common.identity_probe s1c   [--seed 20261301] [--k 1] [--pool-root DIR]
        S1c's own run_s1c.life (RANDOM, the band prefix k) vs S1c's recorded band life — every field but the masked five.
  PYTHONPATH=. python3 -m tools.toys.common.identity_probe tmem1 [--seed 20261301] [--pool-root DIR]
        T-MEM-1's own run_tmem1.life_m1 (BASE, schedule seq, the eps its record carries) vs its recorded BASE.json —
        rates_rw, pairs, table, first_meet and every record row.
Exit 0 iff everything is EQUAL.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Sequence

from brain.scene import pickers as PK
from brain.scene import run_s1c as S
from brain.scene import run_s1c2 as S2
from brain.scene import run_tmem1 as T1

REPO = Path(__file__).resolve().parents[3]
POOLS = REPO / "scratch" / "toys-pools"
S1C_ROOT = Path("/data/dev/brain-runs/scene-s1c")
TMEM1_ROOT = Path("/data/dev/brain-runs/scene-tmem1")


def _first_diff(a: str, b: str, width: int = 70) -> str:
    i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
    return f"at char {i}: new …{a[max(0, i - width):i + width]}… | old …{b[max(0, i - width):i + width]}…"


def probe_s1c(seed: int, k: int, pool_root: Path = POOLS, log=print) -> bool:
    data = S.RoomData(pool_root, seed, S.WORLDS["law"])
    test = S.FixedTestSet()
    rooms = list(S.WORLDS["law"])
    new = S.life(data, test, "RANDOM", rooms, prefix=PK.band_prefix(seed, k))
    old = json.loads((S1C_ROOT / str(seed) / "band" / "law" / f"random-{k:02d}.json").read_text())
    diff = S2.identity_diff(new, old)
    log(f"S1c RANDOM band life k={k} seed {seed}: CPU {new['cpu_s']:.2f} s · identity_diff = "
        f"{diff if diff else 'EQUAL (every field but the masked five: cpu_s, wall_s, code, prereg, world)'} · "
        f"A new {new['marks']['A']:.6f} old {old['marks']['A']:.6f} · words learned at 200: new {new['marks']['wl_end']} old {old['marks']['wl_end']}")
    for f in diff[:5]:
        log(f"  {f}: {_first_diff(S2._canon(new[f]), S2._canon(old[f]))}")
    log("  masked fields side by side (old | new): " + "; ".join(f"{m}: {str(v[0])[:40]} | {str(v[1])[:40]}" for m, v in S2.masked_side_by_side(new, old).items()))
    return not diff


def probe_tmem1(seed: int, pool_root: Path = POOLS, log=print) -> bool:
    old = json.loads((TMEM1_ROOT / str(seed) / "runs" / "seq" / "BASE.json").read_text())
    data = S.RoomData(pool_root, seed, T1.ROOMS)
    test = T1.TestSetM()
    truth = T1.room_truth_map(data, pool_root, seed)
    new = T1.life_m1(data, test, "BASE", "seq", eps=float(old["eps"]), truth=truth)
    log(f"T-MEM-1 BASE / seq seed {seed}: CPU {new['cpu_s']:.1f} s (record {old['cpu_s']:.1f} s) · eps {old['eps']}")
    ok = True
    for key in ("rates_rw", "pairs", "table", "first_meet"):
        a, b = S2._canon(new[key]), S2._canon(old[key])
        log(f"  {key:10s} {'EQUAL' if a == b else 'DIFFERENT ' + _first_diff(a, b)}")
        ok &= a == b
    cols = ("block", "room", "flag", "start", "L", "drop", "wl")
    rows = (len(new["record"]) == len(old["record"]) and
            all(S2._canon({c: x[c] for c in cols}) == S2._canon({c: y[c] for c in cols}) for x, y in zip(new["record"], old["record"])))
    log(f"  record rows {'EQUAL' if rows else 'DIFFERENT'} ({len(new['record'])} / {len(old['record'])})")
    return bool(ok and rows)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("s1c")
    a1.add_argument("--seed", type=int, default=20261301)
    a1.add_argument("--k", type=int, default=1)
    a2 = sub.add_parser("tmem1")
    a2.add_argument("--seed", type=int, default=20261301)
    for a in (a1, a2):
        a.add_argument("--pool-root", type=Path, default=POOLS)
    ns = ap.parse_args(argv)
    ok = probe_s1c(ns.seed, ns.k, ns.pool_root) if ns.cmd == "s1c" else probe_tmem1(ns.seed, ns.pool_root)
    print("PROBE", "EQUAL" if ok else "DIFFERENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
