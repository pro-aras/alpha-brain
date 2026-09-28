# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:40 +0400 — a DIAGNOSIS (read by no verdict): why P-ORACLE's declared pointing rule
# (argmin over things of Σ_w d_w(x)², the per-word Mahalanobis distance under the shared Λ) reads BELOW A-RW on the toy.
# Rule (b) compares things by the LDA's own posterior over words (Σ_w log softmax_k δ_k(x)), which cancels each thing's
# own xᵀΛx; rule (c) is (a) with the thing's Λ-norm removed explicitly (Σ_w [d_w(x)² − xᵀΛx] = Σ_w −2 δ_w(x)).
# Run: cd /data/dev/brain-runs/scene/code-d102d80 && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -B <this file>
import numpy as np
from brain.scene import cache as C, learners as Lr, marks as M, run as R, world as W
tr = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, None, "toy-train"))); te = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, None, "toy-test")))
trT = C.load_truth(C.cache_dir(C.RUNS, None, "toy-train")); teT = C.load_truth(C.cache_dir(C.RUNS, None, "toy-test"))
items = M.m1_items(teT, W.TOY_SEED, mark="TOY")
for eps in (0.3,):
    Rd = Lr.LDAReader(eps)
    R.train_arm("P-ORACLE", Rd, tr, tr.p.words, trT, range(len(tr.p)), W.TOY_SEED)
    Rd.prepare()
    dL, L = Rd.lda._metric()
    Mu = np.stack([m[:dL] for m in Rd.lda.means]); col = {w: k for k, w in enumerate(Rd.lda.names)}
    rules = {"(a) argmin Σ d² [declared]": {}, "(b) argmax Σ log posterior": {}, "(c) argmax Σ δ (Λ-norm removed)": {}}
    for it in items:
        X = te.for_arm("P-ORACLE", it["row"])
        D = Rd.distances(X)
        delta = X @ L @ Mu.T - 0.5 * np.einsum("kj,jl,kl->k", Mu, L, Mu)[None, :]
        logpost = delta - np.logaddexp.reduce(delta, axis=1, keepdims=True)
        idx = [col[w] for w in it["phrase"]]
        rng = lambda: M.tie_rng(W.TOY_SEED, it["item_id"])
        rules["(a) argmin Σ d² [declared]"][it["item_id"]] = {"point": Lr.pick((D[:, idx] ** 2).sum(1), rng(), "min")}
        rules["(b) argmax Σ log posterior"][it["item_id"]] = {"point": Lr.pick(logpost[:, idx].sum(1), rng(), "max")}
        rules["(c) argmax Σ δ (Λ-norm removed)"][it["item_id"]] = {"point": Lr.pick(delta[:, idx].sum(1), rng(), "max")}
    for name, ans in rules.items():
        s = M.summarise_pointing(M.grade_pointing(items, ans, teT, te.members, "gaze"))["all"]
        print(f"eps {eps} toy M1 {name}: covered {s['covered']:.3f} (n {s['n_covered']}) · all {s['all']:.3f}")
    Xn = np.concatenate([te.for_arm("P-ORACLE", it["row"]) for it in items])
    q = np.einsum("ij,jk,ik->i", Xn, L, Xn)
    print(f"   the things' own Λ-norm xᵀΛx on the toy test: min {q.min():.1f} median {np.median(q):.1f} max {q.max():.1f}")

# --- the gate's step 3 for the two LDA arms under rules (a) and (b): trained on the first 300 scenes of seed 1, read on
#     its test M1 items (the gate's own items and tie generators)
ws = 20261101
trs = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, ws, "train"))); T = C.load_truth(C.cache_dir(C.RUNS, ws, "train"))
tt = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, ws, "test"))); TT = C.load_truth(C.cache_dir(C.RUNS, ws, "test"))
import json
K = json.loads((C.RUNS / str(ws) / "keys.json").read_text())["items"]["M1"]
for arm in ("P-ORACLE", "ORACLE-TRUTH"):
    Rd = Lr.LDAReader(0.3)
    R.train_arm(arm, Rd, trs, trs.p.words, T, range(300), ws)
    Rd.prepare()
    dL, L = Rd.lda._metric()
    Mu = np.stack([m[:dL] for m in Rd.lda.means]); col = {w: k for k, w in enumerate(Rd.lda.names)}
    out = {"a": {}, "b": {}}
    for it in K:
        X = tt.for_arm(arm, it["row"])
        D = Rd.distances(X)
        delta = X @ L @ Mu.T - 0.5 * np.einsum("kj,jl,kl->k", Mu, L, Mu)[None, :]
        logpost = delta - np.logaddexp.reduce(delta, axis=1, keepdims=True)
        idx = [col[w] for w in it["phrase"]]
        out["a"][it["item_id"]] = {"point": Lr.pick((D[:, idx] ** 2).sum(1), M.tie_rng(20261201, it["item_id"]), "min")}
        out["b"][it["item_id"]] = {"point": Lr.pick(logpost[:, idx].sum(1), M.tie_rng(20261201, it["item_id"]), "max")}
    for r, ans in out.items():
        s = M.summarise_pointing(M.grade_pointing(K, ans, TT, tt.members, "truth" if arm == "ORACLE-TRUTH" else "gaze"))["all"]
        print(f"gate 300 · {arm:<12} rule ({r}): M1 covered {s['covered']:.3f} (n {s['n_covered']}) · all {s['all']:.3f}")
