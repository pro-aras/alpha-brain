#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-28 20:41 +0400 — PREREG-BRAIN-IN-BODY §3 THE NULL: the offline k-th null re-run with its ANSWERS kept.
"""The scored record keeps only the null's scores (fresh/nulls/<k>.json). This re-runs `run.run_null`'s own training and
answering for ONE draw, keeps the answers, and REFUSES to write them unless m1, m3, n_m1 and n_m3 equal the record exactly.
Written into a NEW folder, never the record.  usage: null_k1_answers.py --world-seed WS --k K --out DIR"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from brain.scene import cache as C, learners as Lr, marks as M, run as R, world as W

CACHES = C.RUNS                                       # the tree's fresh root: redrawn under this code, array-identical to the scored caches
SCORED = Path("/data/dev/brain-runs/scene-s1b1r")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world-seed", type=int, required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ws, k = a.world_seed, a.k
    train = R.Things(C.ScenePercepts(C.cache_dir(CACHES, ws, "train")))
    perm = R.null_perm(ws, k, len(train.p))
    L = R.make_learner("N-SHUF", Lr.LR_S1B1, 0.3)
    R.train_arm("N-SHUF", L, train, lambda i: train.p.words(int(perm[i])), None, range(W.N_TRAIN), ws, None)
    rs = R.r_seed_root(SCORED, ws)
    Q = json.loads((rs / "questions.json").read_text())
    K = json.loads((rs / "keys.json").read_text())["items"]
    th = {s: R.Things(C.ScenePercepts(C.cache_dir(CACHES, ws, s, R.R_TSET))) for s in ("test", "m3")}
    ans = {}
    for mark in ("M1", "M3"):
        for q in Q["questions"][mark]:
            ans[q["item_id"]] = L.answer_point(th[q["split"]].for_arm("N-SHUF", q["row"]), q["phrase"],
                                               M.tie_rng(Q["test_seed"], q["item_id"]))
    g1 = M.summarise_pointing(M.grade_pointing(K["M1"], ans, C.load_truth(C.cache_dir(CACHES, ws, "test", R.R_TSET)),
                                               th["test"].members, "gaze"))["graded"]
    g3 = M.summarise_m3(M.grade_pointing(K["M3"], ans, C.load_truth(C.cache_dir(CACHES, ws, "m3", R.R_TSET)),
                                         th["m3"].members, "gaze"), K["M3"])["all"]
    got = {"m1": g1["covered"], "n_m1": g1["n_covered"], "m3": g3["covered"], "n_m3": g3["n_covered"]}
    rec = json.loads((rs / "nulls" / f"{k:02d}.json").read_text())
    want = {x: rec[x] for x in got}
    print(f"[null {ws} k={k}] re-run {got}")
    print(f"[null {ws} k={k}] record {want}")
    if got != want:
        print("[null] THE RE-RUN DOES NOT EQUAL THE RECORD — nothing written")
        return 3
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    R.dump(out / f"answers-{ws}-k{k:02d}.json", {"world_seed": ws, "k": k, "key": rec["key"], "test_seed": Q["test_seed"],
                                                "equals_record": True, "scores": got, "point": ans})
    print(f"[null] equal to the record; {len(ans)} answers written to {out / f'answers-{ws}-k{k:02d}.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
