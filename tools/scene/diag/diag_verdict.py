# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:36 +0400 — a DIAGNOSIS of THE FIRST GATE's instrument verdict (read by no verdict).
# Run: cd /data/dev/brain-runs/scene/code-d102d80 && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -B <this file>
"""Diagnosis of the instrument verdict (NOT a verdict): the same 113 one-thing gate scenes, several readers."""
import numpy as np
from brain.scene import cache as C, learners as Lr, marks as M, run as R, world as W
ws = 20261101
trs = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, ws, "train")))
T = C.load_truth(C.cache_dir(C.RUNS, ws, "train"))
rows = list(range(300))
one = [i for i in rows if len(T[i]["things"]) == 1]
def hyp(i, k):
    mem, pos = trs.members(i)
    return M.thing_hypothesis(k, mem, pos, T[i]["fix_thing"], tuple(T[i]["centroids"][k]))
X1 = np.stack([trs.for_arm("P-ORACLE", i)[hyp(i, 0)] for i in one])
lab = {t: [T[i]["things"][0][t] for i in one] for t in ("shape", "colour", "size")}
print("n one-thing", len(one))
print("NCM LOO on these hypotheses (the probe's rule):", {t: round(M.loo_ncm(X1, y), 3) for t, y in lab.items()})
# LDA LOO at several eps, type-blind (the declared reading)
def lda_loo(eps, only_type=None, words_filter=None):
    acc = {t: [] for t in R.TYPE_WORDS}
    for i in one:
        Rd = Lr.LDAReader(eps)
        for j in rows:
            if j == i: continue
            ref = R.referent_index("P-ORACLE", trs, T[j])
            if ref is None: continue
            ws_ = trs.p.words(j)
            if words_filter: ws_ = [w for w in ws_ if words_filter(w)]
            Rd.train_scene(Lr.feed_oracle(trs.for_arm("P-ORACLE", j), ref), ws_)
        Rd.prepare()
        x = trs.for_arm("P-ORACLE", i)[hyp(i, 0)]
        for t, wl in R.TYPE_WORDS.items():
            if only_type and t != only_type: continue
            acc[t].append(Rd.name_forced(x, wl) == T[i]["things"][0][t])
    return {t: (round(float(np.mean(v)), 3) if v else None) for t, v in acc.items()}
for eps in (1e-4, 1e-2, 0.1, 0.3, 0.6, 0.9, 1.0):
    print("type-blind LDA LOO eps", eps, lda_loo(eps))
# per-type Σ: the reader fed only one type's words (a TYPE-AWARE reader — a diagnostic, read by no verdict)
for t, wl in R.TYPE_WORDS.items():
    print("per-type-Σ LDA LOO eps 0.3,", t, lda_loo(0.3, only_type=t, words_filter=lambda w, wl=wl: w in wl))
