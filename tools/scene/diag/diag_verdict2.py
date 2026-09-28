# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:36 +0400 — a DIAGNOSIS of THE FIRST GATE's instrument verdict (read by no verdict).
# Run: cd /data/dev/brain-runs/scene/code-d102d80 && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -B <this file>
"""Diagnosis (NOT a verdict): P-ORACLE fitted on all 300 gate scenes, per-type naming on seed 1's TEST one-thing scenes;
and how many colour observations each colour class had."""
import collections
import numpy as np
from brain.scene import cache as C, learners as Lr, marks as M, run as R
ws = 20261101
trs = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, ws, "train"))); T = C.load_truth(C.cache_dir(C.RUNS, ws, "train"))
te = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, ws, "test"))); TT = C.load_truth(C.cache_dir(C.RUNS, ws, "test"))
for eps in (0.3,):
    Rd = Lr.LDAReader(eps)
    R.train_arm("P-ORACLE", Rd, trs, trs.p.words, T, range(300), ws)
    Rd.prepare()
    print("observations per word class:", {w: c for w, c in zip(Rd.lda.names, Rd.lda.counts)})
    one = [r for r in TT if len(r["things"]) == 1]
    nm = R._per_type_naming(Rd, te, one)
    print("eps", eps, "fit on 300 gate scenes → test one-thing scenes:", {t: (round(v, 3), n) for t, (v, n) in nm.items()})
    gate_one = [T[i] for i in range(300) if len(T[i]["things"]) == 1]
    print("   in-sample on the gate's one-thing scenes:", {t: (round(v, 3), n) for t, (v, n) in R._per_type_naming(Rd, trs, gate_one).items()})
    # confusion of colour on the LOO-failing kind: which colours are confused (in-sample on test)
    conf = collections.Counter()
    for r in one:
        mem, pos = te.members(r["row"]); h = M.thing_hypothesis(0, mem, pos, r["fix_thing"], tuple(r["centroids"][0]))
        if h is None: continue
        got = Rd.name_forced(te.for_arm("P-ORACLE", r["row"])[h], R.TYPE_WORDS["colour"])
        if got != r["things"][0]["colour"]: conf[(r["things"][0]["colour"], got)] += 1
    print("   test colour confusions (true → named):", dict(conf))
