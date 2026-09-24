"""probe.py — arm D's seconds per candidate program (B1-PREREG §3.5: «D's seconds per candidate program on a
100-candidate sample»), measured on a tape's first sleep that has something to search.

edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 17:06 +0400 — the probe runs D over the tape to the chosen sleep, times every
candidate that sleep's search evaluates (enumeration + evaluation + scoring, the unit the budget counts), and
reports a 100-candidate sample drawn at evenly spaced positions of that record beside the mean over ALL of it,
the sizes, the per-cue split, and the load average at start and end (a number measured under load is labelled
so — #233, #239 (10)). The clock is read here only; the search never sees it.

  python -m brain.arms.library.probe --tape T.jsonl --cache C --out OUT.json [--sleep-index 3] [--budget 5000]
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

from brain.protocol import Answer, HarnessContract, make_arm

from .arm import LibraryArm


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tape", required=True)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sleep-index", type=int, default=0, help="probe the k-th sleep (0 = the first that has examples)")
    ap.add_argument("--budget", type=int, default=5000)
    ap.add_argument("--max-size", type=int, default=20)
    ap.add_argument("--warm-budget", type=int, default=5000, help="the budget of the sleeps BEFORE the probed one")
    a = ap.parse_args(argv)
    out = Path(a.out)
    run_dir = out.parent / (out.stem + "-run")
    cfg = {"cache_dir": a.cache, "run_dir": str(run_dir), "seed": 0, "interpreter": sys.executable,
           "candidates_per_sleep": a.warm_budget, "max_size": a.max_size, "library_snapshots": False}
    arm = make_arm(LibraryArm, 0, cfg)
    load0 = os.getloadavg()
    pending = {}
    in_test = False
    probed = None
    t_start = time.perf_counter()
    for line in Path(a.tape).read_text().splitlines():
        row = json.loads(line)
        k = row["kind"]
        if k == "TEACH":
            HarnessContract.teach(arm, row)
        elif k == "ARRIVAL":
            HarnessContract.arrival(arm, row)
        elif k == "TEST_BEGIN":
            in_test = True
        elif k == "TEST_END":
            in_test = False
        elif k == "ASK":
            if in_test:
                HarnessContract.test_ask(arm, row)
            else:
                ans = HarnessContract.training_ask(arm, row)
                pending[row["seq"]] = (ans, row["payload"]["answer_kind"])
        elif k == "FEEDBACK":
            ans, kind = pending.pop(row["payload"]["ask_seq"], (Answer(kind="SILENT"), "NAME"))
            HarnessContract.feedback(arm, row, ans, kind)
        elif k == "SLEEP":
            has_work = bool(arm.core.examples)
            idx = arm.core.sleep_index + 1
            target = (a.sleep_index == 0 and has_work) or (a.sleep_index == idx)
            if target and probed is None:
                arm.core.budget = a.budget
                arm.core.timing = []
                arm.core.clock = time.perf_counter
                t0 = time.perf_counter()
                HarnessContract.sleep(arm, row)
                wall = time.perf_counter() - t0
                rec = arm.core.timing
                arm.core.timing, arm.core.clock = None, None
                probed = {"sleep": idx, "wall_seconds": wall, "timed": len(rec)}
                if rec:
                    n = len(rec)
                    pick = [rec[int(i * (n - 1) / 99)] for i in range(100)] if n >= 100 else rec
                    secs = [x[2] for x in pick]
                    probed.update({
                        "sample_n": len(pick),
                        "sample_mean_s": statistics.fmean(secs),
                        "sample_median_s": statistics.median(secs),
                        "sample_p95_s": sorted(secs)[int(0.95 * (len(secs) - 1))],
                        "sample_sizes": {str(s): sum(1 for x in pick if x[1] == s) for s in sorted({x[1] for x in pick})},
                        "all_mean_s": statistics.fmean(x[2] for x in rec),
                        "per_key": {key: {"n": sum(1 for x in rec if x[0] == key),
                                          "mean_s": statistics.fmean(x[2] for x in rec if x[0] == key)}
                                    for key in sorted({x[0] for x in rec})},
                    })
                break
            HarnessContract.sleep(arm, row)
    probed = probed or {"note": "no sleep with examples was reached"}
    probed.update({"loadavg_start": load0, "loadavg_end": os.getloadavg(), "interpreter": sys.executable,
                   "budget": a.budget, "tape": a.tape, "total_wall_seconds": time.perf_counter() - t_start,
                   "label": "measured UNDER LOAD unless loadavg_start[0] < 2 (B1-PREREG §3.5 wants a quiet box)"})
    out.write_text(json.dumps(probed, sort_keys=True, indent=1))
    print(json.dumps(probed, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
