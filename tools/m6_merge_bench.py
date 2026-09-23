#!/usr/bin/env python3
# edit: Claude (Opus 5.5, M6 builder), 2026-09-23 17:24 +0400 — A42-M6 (docs/briefs/A42-M6-REPORT.md §3-§4): the sleep's cost and the fast merge's
# identity on a COPY of a real snapshot (never a live root: pass a directory you made with `cp -a`). Loads the organism TWICE (two
# independent objects), optionally replays the sleep's own 200 most-surprising episodes on both (genome/sleep.py:sleep — the same
# deterministic moments), then runs the cycle's body on each: the OLD road (tests/genome/test_merge_fast.py's verbatim `_merge`,
# pinned by sha256 to 51f71ba) on one and the FAST road on the other, each part timed (sight merge, words merge, prune), and
# compares the merge lists, the counters, the alive vectors and the dense state_hash. Also times state_hash() on the loaded state.
# usage: python3 tools/m6_merge_bench.py <snapdir> [--sleep] [--label X]      (snapdir holds organism.json/.npz [+ episodes.npz])
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

TREE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TREE))

from genome.machinery import MERGE_FAST_MARGIN, Organism, parse_genome   # noqa: E402
from genome.sleep import sleep as run_sleep                                  # noqa: E402
from tests.genome.test_merge_fast import _merge_reference                    # noqa: E402  (the verbatim old road)


def _load(snap: Path):
    meta = json.loads((snap / "organism.json").read_text())
    g = parse_genome(meta["genome_text"])
    return Organism.load(snap / "organism", g), g


def _fp(org):
    return {"merges": list(org.merges), "c": dict(org.c), "state_hash": org.state_hash(),
            "alive_s": org.sight.alive[: org.sight.n].tobytes(), "alive_w": org.words.alive[: org.words.n].tobytes()}


def main(argv):
    snap = Path(argv[0]); label = argv[argv.index("--label") + 1] if "--label" in argv else snap.name
    A, g = _load(snap); B, _ = _load(snap)
    print(f"[m6-bench {label}] t {A.t} · sight born {A.sight.n} alive {len(A.sight.alive_ids())} · words born {A.words.n} alive "
          f"{len(A.words.alive_ids())} · W {A.W.shape} · theta_m {g.theta_m} · margin {MERGE_FAST_MARGIN}", flush=True)
    hs = []
    for _ in range(3):
        t0 = time.perf_counter(); A.state_hash(); hs.append((time.perf_counter() - t0) * 1000)
    print(f"[m6-bench {label}] state_hash ms per call (3): {[round(x, 1) for x in hs]}", flush=True)
    if "--sleep" in argv:
        from genome.fast import Episodes
        n = int(g.declared["SLEEP"]["replay"])
        for name, org in (("A", A), ("B", B)):
            eps = Episodes.load(snap / "episodes.npz")
            t0 = time.perf_counter(); res = run_sleep(org, eps, n); dt = time.perf_counter() - t0
            print(f"[m6-bench {label}] sleep() replay of {n} episodes on {name}: {dt * 1000:.0f} ms {res}", flush=True)
        print(f"[m6-bench {label}] after the sleep: sight alive {len(A.sight.alive_ids())} words alive {len(A.words.alive_ids())}; "
              f"A == B before the cycle: {A.state_hash() == B.state_hash()}", flush=True)
    # the candidate filter's own numbers on the sight area (read-only)
    for area_name in ("sight", "words"):
        area = getattr(B, area_name)
        ws = sorted(set(w for w in area.alive_ids() if area.alive[w]))
        t0 = time.perf_counter(); cand = list(B._merge_candidates(area, ws)); dt = time.perf_counter() - t0
        C = area.cells[np.asarray(ws, dtype=np.int64)] if ws else np.zeros((0, area.dim))
        d = area.dim; u = 2.0 ** -53; gamma = d * u / (1 - d * u)
        from genome.machinery import MERGE_FAST_BLOCK
        maxdiff = 0.0; above = 0; ndiff = 0; blocks = {}
        for i, j in cand:                                   # the gemm value exactly as _merge_candidates computed it (same block)
            r0 = (i // MERGE_FAST_BLOCK) * MERGE_FAST_BLOCK
            if r0 not in blocks:
                blocks[r0] = C[r0:min(r0 + MERGE_FAST_BLOCK, len(ws))] @ C[r0:].T
            gv = float(blocks[r0][i - r0, j - r0])
            dd = float(area.cells[ws[i]] @ area.cells[ws[j]])
            maxdiff = max(maxdiff, abs(dd - gv)); ndiff += dd != gv; above += dd > g.theta_m
        print(f"[m6-bench {label}] {area_name}: {len(ws)} alive -> {len(ws) * (len(ws) - 1) // 2} pairs -> {len(cand)} candidates "
              f"({above} above theta by the old gate) in {dt * 1000:.0f} ms · bound 2*gamma_{d}*max|c|^2 = "
              f"{2 * gamma * (float(np.max(np.einsum('ij,ij->i', C, C))) if len(C) else 0):.2e} · ddot != gemm in {ndiff} of {len(cand)} candidates, max |ddot - gemm| {maxdiff:.2e}", flush=True)
    t = {}
    t0 = time.perf_counter(); _merge_reference(A, A.sight, list(A.sight.alive_ids()), axis=0); t["ref_sight"] = time.perf_counter() - t0
    t0 = time.perf_counter(); _merge_reference(A, A.words, list(A.words.alive_ids()), axis=1); t["ref_words"] = time.perf_counter() - t0
    t0 = time.perf_counter(); A._prune(list(A.sight.alive_ids()), list(A.words.alive_ids())); t["ref_prune"] = time.perf_counter() - t0
    t0 = time.perf_counter(); B._merge(B.sight, list(B.sight.alive_ids()), axis=0, fast=True); t["fast_sight"] = time.perf_counter() - t0
    t0 = time.perf_counter(); B._merge(B.words, list(B.words.alive_ids()), axis=1, fast=True); t["fast_words"] = time.perf_counter() - t0
    t0 = time.perf_counter(); B._prune(list(B.sight.alive_ids()), list(B.words.alive_ids())); t["fast_prune"] = time.perf_counter() - t0
    fa, fb = _fp(A), _fp(B)
    new_a = fa["merges"][len(json.loads((snap / "organism.json").read_text())["merges"]):]
    same = {k: fa[k] == fb[k] for k in fa}
    print(f"[m6-bench {label}] cycle body ms — OLD: sight {t['ref_sight'] * 1000:.0f} · words {t['ref_words'] * 1000:.0f} · prune "
          f"{t['ref_prune'] * 1000:.0f} | FAST: sight {t['fast_sight'] * 1000:.0f} · words {t['fast_words'] * 1000:.0f} · prune "
          f"{t['fast_prune'] * 1000:.0f} | merge pass x{(t['ref_sight'] + t['ref_words']) / max(t['fast_sight'] + t['fast_words'], 1e-9):.1f}", flush=True)
    print(f"[m6-bench {label}] merges made by this sleep+cycle (old road): {len(new_a)} (sight {sum(1 for x in new_a if x[1] == 'sight')}, "
          f"words {sum(1 for x in new_a if x[1] == 'words')}) · identical: {same} · ALL IDENTICAL: {all(same.values())}", flush=True)
    return 0 if all(same.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
