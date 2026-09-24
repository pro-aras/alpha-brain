"""solo_probe.py — STAGE −1 CLAUSE 5: THE SOLO COST PROBE (B1-PREREG.md §3.5; the seat's).

edit: Claude (Fable 5.1), 2026-09-24 18:55 +0400 — the seat, alone.

"On a quiet box (`uptime` load < 2), one thread, nice 0: A0's per-event cost on 1,000 tape events; A1's per
event at H = 64 and H = 512; D's seconds per candidate program on a 100-candidate sample. These numbers
replace every [Guessing] in §7 before the seat's §12 line."

`python -m brain.harness.solo_probe --tape-dir <dir> --cache-dir <dir> --out docs/brain/b1/stage-1/solo-probe.json
[--events 1000] [--force]` — refuses above load 2 unless forced (a "solo" cost measured beside eight workers is
not solo — #233's own note). A0 runs under whichever interpreter §3.0 decided (this script is launched under it);
A1 needs the venv's torch. Each figure carries the load it was measured under, the interpreter and the number of
events, so a reader never has to guess the conditions (#194).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from brain.harness.run import load_tape  # noqa: E402
from brain.protocol import HarnessContract, make_arm  # noqa: E402


def _replay(arm, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """The HarnessContract dispatch over `rows` (no sittings: the first N events of the tape are all training)."""
    t0 = time.perf_counter()
    pending: Dict[int, Any] = {}
    kinds = {r["seq"]: r["payload"]["answer_kind"] for r in rows if r["kind"] == "ASK"}
    n = 0
    for r in rows:
        k = r["kind"]
        if k == "TEACH":
            HarnessContract.teach(arm, r)
        elif k == "ARRIVAL":
            HarnessContract.arrival(arm, r)
        elif k == "SLEEP":
            HarnessContract.sleep(arm, r)
        elif k == "ASK":
            pending[r["seq"]] = HarnessContract.training_ask(arm, r)
        elif k == "FEEDBACK":
            a = pending.pop(r["payload"]["ask_seq"], None)
            if a is not None:
                HarnessContract.feedback(arm, r, a, kinds[r["payload"]["ask_seq"]])
        else:
            continue
        n += 1
    wall = time.perf_counter() - t0
    c = arm.cost()
    return {"events": n, "wall_s": round(wall, 3), "ms_per_event_wall": round(1000 * wall / max(n, 1), 3),
            "arm_events": c["events"], "arm_ms": round(c["ms"], 1), "ms_per_event_arm": round(c["ms"] / max(c["events"], 1), 3)}


def probe_a0(rows, cache_dir: Path, seed: int, run_dir: Path) -> Dict[str, Any]:
    from brain.arms.cells.a0 import A0Arm
    arm = make_arm(A0Arm, seed, {"cache_dir": str(cache_dir), "run_dir": str(run_dir / "a0"), "seed": seed, "interpreter": sys.executable})
    return _replay(arm, rows)


def probe_a1(rows, cache_dir: Path, seed: int, run_dir: Path, h: int) -> Dict[str, Any]:
    import torch
    torch.set_num_threads(1)
    from brain.arms.soft.arm import ArmA1
    arm = make_arm(ArmA1, seed, {"cache_dir": str(cache_dir), "run_dir": str(run_dir / f"a1-h{h}"), "seed": seed, "interpreter": sys.executable,
                                 "variant": "A1-FIXED", "fixed_h": h})
    out = _replay(arm, rows)
    out["size"] = arm.size()
    return out


def probe_d(rows, cache_dir: Path, seed: int, run_dir: Path, candidates: int) -> Dict[str, Any]:
    """D's seconds per candidate program: one sleep with `candidates_per_sleep` = the sample, timed."""
    from brain.arms.library.arm import LibraryArm
    arm = make_arm(LibraryArm, seed, {"cache_dir": str(cache_dir), "run_dir": str(run_dir / "d"), "seed": seed, "interpreter": sys.executable,
                                      "candidates_per_sleep": int(candidates), "library_snapshots": False, "library_log": True})
    pending: Dict[int, Any] = {}
    kinds = {r["seq"]: r["payload"]["answer_kind"] for r in rows if r["kind"] == "ASK"}
    for r in rows:
        if r["kind"] == "TEACH":
            HarnessContract.teach(arm, r)
        elif r["kind"] == "ASK":
            pending[r["seq"]] = HarnessContract.training_ask(arm, r)
        elif r["kind"] == "FEEDBACK":
            a = pending.pop(r["payload"]["ask_seq"], None)
            if a is not None:
                HarnessContract.feedback(arm, r, a, kinds[r["payload"]["ask_seq"]])
    t0 = time.perf_counter()
    arm.sleep(64)
    wall = time.perf_counter() - t0
    return {"candidates": int(candidates), "sleep_wall_s": round(wall, 3), "seconds_per_candidate": round(wall / max(candidates, 1), 4),
            "events_before_sleep": len(rows)}


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--tape-dir", required=True)
    p.add_argument("--cache-dir", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--events", type=int, default=1000)
    p.add_argument("--d-candidates", type=int, default=100)
    p.add_argument("--only", default="a0,a1-64,a1-512,d")
    p.add_argument("--force", action="store_true")
    p.add_argument("--seed", type=int, default=20261001)
    ns = p.parse_args(argv)
    load1 = os.getloadavg()[0]
    if load1 >= 2.0 and not ns.force:
        raise SystemExit(f"load {load1:.2f} >= 2: a solo probe waits for a quiet box (§3.5); --force to override (the figure is then not solo)")
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(k, "1")
    tape_dir, cache_dir = Path(ns.tape_dir), Path(ns.cache_dir)
    rows, sha = load_tape(tape_dir)
    rows = rows[: ns.events]
    run_dir = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp")) / f"solo-probe-{int(time.time())}"
    run_dir.mkdir(parents=True, exist_ok=True)
    out: Dict[str, Any] = {"tape_sha256": sha, "events": len(rows), "load1_at_start": load1, "interpreter": sys.executable, "nice": os.nice(0),
                           "threads": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}, "probes": {}}
    only = set(ns.only.split(","))
    if "a0" in only:
        out["probes"]["A0"] = probe_a0(rows, cache_dir, ns.seed, run_dir)
        print("[solo] A0:", json.dumps(out["probes"]["A0"]))
    for h in (64, 512):
        if f"a1-{h}" in only:
            try:
                out["probes"][f"A1-H{h}"] = probe_a1(rows, cache_dir, ns.seed, run_dir, h)
                print(f"[solo] A1 H={h}:", json.dumps(out["probes"][f"A1-H{h}"]))
            except ImportError as e:
                out["probes"][f"A1-H{h}"] = {"error": f"torch not importable under {sys.executable}: {e}"}
    if "d" in only:
        out["probes"]["D"] = probe_d(rows, cache_dir, ns.seed, run_dir, ns.d_candidates)
        print("[solo] D:", json.dumps(out["probes"]["D"]))
    out["load1_at_end"] = os.getloadavg()[0]
    Path(ns.out).parent.mkdir(parents=True, exist_ok=True)
    Path(ns.out).write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(f"[solo] wrote {ns.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
