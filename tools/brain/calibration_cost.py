#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:18 +0400 — PREREG-HEARS-2 AMENDMENT 1 §A1.8 (2): the price of ONE calibration at 100,000 scenes, MEASURED (not scaled from the 20,000 figure).
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:24 +0400 — committed beside its record (docs/organism/hears/CALIBRATION-COST-2026-10-03.md) so the measurement can be repeated; it writes calib_cost.json next to the brain's files.
"""usage: PYTHONPATH=. python3 -B tools/brain/calibration_cost.py <genome with the BRAIN line> <brain base path (the prefix of brain.json / brain.npz)> [--max 100000]

Loads a real brain (the scene hand's 10,000 learned scenes, 6 calibrations), times Brain.calibrate() at its own size, then GROWS it by cycling its own real scenes through the learner's own
train_scene (so the per-word stores grow as they do in a life) and times calibrate() again at 20,000, 50,000 and 100,000 scenes (and more if --max allows). Two structures:
  all_scene   every real scene as it is (two or three things, two or three words) — an UPPER bound for the maker's feed;
  maker_like  only the real one-thing scenes, each with ONE shape word — the maker's structure (one drawn thing, one true word).
Reports wall and CPU seconds of the calibration, the peak RSS, and the growth's own cost per scene. Calibrations after the first are measured twice (the second is the one to read)."""
from __future__ import annotations

import json
import resource
import sys
import time
from pathlib import Path

import numpy as np

from genome import brain as B
from genome.machinery import parse_genome


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def timed_calibrate(b):
    t0, c0 = time.perf_counter(), time.process_time()
    b.calibrate()
    return time.perf_counter() - t0, time.process_time() - c0


def run(genome: Path, base: Path, structure: str, max_n: int):
    cfg = dict(parse_genome(genome.read_text()).declared["BRAIN"])
    b = B.Brain.load(base, cfg)
    n0 = b.n_learned
    templates = list(b.seen)
    if structure == "maker_like":
        shapes = next(set(g) for g in b.types() if "star" in g)
        tm = []
        for X, words, _ in templates:
            if X.shape[0] == 1:
                w = [x for x in words if x in shapes][:1]
                if w:
                    tm.append((X, w, None))
        templates = tm
    print(f"[{structure}] loaded {n0} scenes, {len(b.L.words)} words; templates {len(templates)}; RSS {rss_mb():.0f} MB", flush=True)
    out = []
    targets = [n0] + [t for t in (20000, 50000, 100000, 150000, 200000) if n0 < t <= max_n]
    i = 0
    for target in targets:
        g0, g1 = time.perf_counter(), time.process_time()
        grown = 0
        while b.n_learned < target:
            X, words, _ = templates[i % len(templates)]
            i += 1
            b.L.train_scene(X, words, referent=None, rng=np.random.default_rng(i))
            b.seen.append((X, words, None))
            grown += 1
        grow_cpu = time.process_time() - g1
        w1, c1 = timed_calibrate(b)
        w2, c2 = timed_calibrate(b)
        row = {"structure": structure, "scenes": b.n_learned, "grown_by": grown, "grow_cpu_s": round(grow_cpu, 2), "grow_cpu_ms_per_scene": (round(1000 * grow_cpu / grown, 3) if grown else None),
               "calibrate_wall_s_first": round(w1, 3), "calibrate_cpu_s_first": round(c1, 3), "calibrate_wall_s_second": round(w2, 3), "calibrate_cpu_s_second": round(c2, 3),
               "peak_rss_mb": round(rss_mb())}
        out.append(row)
        print(json.dumps(row), flush=True)
    return out


def main() -> int:
    genome, base = Path(sys.argv[1]), Path(sys.argv[2])
    max_n = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 100000
    res = []
    for structure in ("all_scene", "maker_like"):
        res += run(genome, base, structure, max_n)
    Path(base).with_name("calib_cost.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
