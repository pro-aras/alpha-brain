"""price_d.py — the rule library's search PRICE at a real budget (B1-PREREG §4 row D: candidates per sleep = ⌊24 CPU-h ÷
seconds per candidate ÷ sleeps⌋; the NUMBER after the probe).

edit: Claude (Opus 5.5), 2026-09-26 17:04 +0400 — the §12 line of 12:08 omitted D's number, so B1's graded run used the arm's
toy default (2,000 candidates per sleep, split over the cues: 210–333 per relation cue, programs of size ≤ 7, never the
size-8 «name after x»). The solo probe's 0.0028 s per candidate was measured on SMALL programs (100 candidates after 1,000
events); a candidate's cost grows with its size and with the data it is evaluated on, so the budget is re-priced here on
the real tape at a real per-sleep budget instead of extrapolated from the small-program rate (#162).

`/data/dev/venvs/brain/bin/python -m tools.b1.price_d --seed 20261001 --candidates 50000 --sleeps 3 --out <json>`
Drives D through the tape up to its N-th SLEEP; records per sleep: wall seconds, candidates spent, seconds per candidate,
and each cue's max_size_reached / spent from D's own library_log. One thread; the load at start and end is recorded.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from brain.harness.run import load_tape  # noqa: E402
from brain.protocol import HarnessContract, make_arm  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=20261001)
    p.add_argument("--candidates", type=int, default=50000)
    p.add_argument("--sleeps", type=int, default=3)
    p.add_argument("--out", required=True)
    ns = p.parse_args(argv)
    import torch
    torch.set_num_threads(1)
    from brain.arms.library.arm import LibraryArm
    tape_dir = Path(f"/data/dev/brain-runs/b1/{ns.seed}")
    cache_dir = Path(f"/data/dev/brain-runs/b1/cache/{ns.seed}")
    rows, sha = load_tape(tape_dir)
    run_dir = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp")) / f"price-d-{ns.seed}-{int(time.time())}"
    run_dir.mkdir(parents=True, exist_ok=True)
    arm = make_arm(LibraryArm, ns.seed, {"cache_dir": str(cache_dir), "run_dir": str(run_dir), "seed": ns.seed, "interpreter": sys.executable,
                                         "candidates_per_sleep": ns.candidates, "library_snapshots": False, "library_log": True})
    out = {"seed": ns.seed, "tape_sha256": sha, "candidates_per_sleep": ns.candidates, "load1_start": os.getloadavg()[0],
           "interpreter": sys.executable, "sleeps": []}
    pending, kinds = {}, {r["seq"]: r["payload"]["answer_kind"] for r in rows if r["kind"] == "ASK"}
    n_sleeps = 0
    for r in rows:
        k = r["kind"]
        if k == "TEACH":
            HarnessContract.teach(arm, r)
        elif k == "ARRIVAL":
            HarnessContract.arrival(arm, r)
        elif k == "ASK":
            if r["phase"].startswith("T"):
                continue
            pending[r["seq"]] = HarnessContract.training_ask(arm, r)
        elif k == "FEEDBACK":
            a = pending.pop(r["payload"]["ask_seq"], None)
            if a is not None:
                HarnessContract.feedback(arm, r, a, kinds[r["payload"]["ask_seq"]])
        elif k == "SLEEP":
            t0 = time.perf_counter()
            HarnessContract.sleep(arm, r)
            wall = time.perf_counter() - t0
            n_sleeps += 1
            log = [json.loads(l) for l in open(run_dir / "library_log.jsonl")]
            last = log[-1]
            spent = sum(int(c.get("spent") or 0) for c in last["cues"])
            out["sleeps"].append({"sleep": n_sleeps, "seq": r["seq"], "wall_s": round(wall, 2), "spent": spent,
                                  "s_per_candidate": (round(wall / spent, 6) if spent else None),
                                  "cues": [{k2: c.get(k2) for k2 in ("key", "n", "score", "spent", "max_size_reached", "program", "perfect")}
                                           for c in last["cues"] if c.get("searched")]})
            print(f"[price_d] sleep {n_sleeps} at seq {r['seq']}: {wall:.1f} s, spent {spent}", flush=True)
            if n_sleeps >= ns.sleeps:
                break
    out["load1_end"] = os.getloadavg()[0]
    Path(ns.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"[price_d] wrote {ns.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
