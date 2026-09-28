# edit: Claude (Fable 5.1, the seat), 2026-09-28 — READ-ONLY diagnosis 3 of M6: a young word read with the metric of the type
# its own ear heard ALONE most (the learner's own «one-alone» type). A READING on the fresh set (already used three times):
# it names a cause; it grades no fix.
import json, collections
from pathlib import Path
import numpy as np
from brain.scene import world as W, cache as C, learners as Lr, marks as M, run as R

print("PREDICTIONS (written before the run): (1) the one-alone type is the SHAPE type at every seed; (2) nearest under the "
      "one-alone type's metric reads >= 0.85 at 20261102 and 20261103; (3) the colour type's and the size type's metrics read "
      "LOWER than the shape type's at both; (4) at 20261101 (the meeting was written to the square) every metric stays low.")
ROOT = Path("/data/dev/brain-runs/organ/scene"); SCORED = C.RUNS
for ws in W.WORLD_SEEDS:
    train = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "train")))
    L = Lr.RWLearner(lr=R.ARM_LR.get("A-RW", 0.01))
    seen = []; done = 0
    for rp in W.READING_POINTS:
        R.train_arm("A-RW", L, train, train.p.words, None, range(done, rp), ws, seen)
        done = rp
        R.prepare("A-RW", L, seen)
        L.calibrate_r(0.3, None)
    st = L.reader["ear"]
    j = L.index[W.DAX_WORD]
    proto = L.prototype(j)
    types = [tuple(t) for t in st["types"]]
    names = []
    for T in types:
        kinds = collections.Counter(W.word_type(w) for w in T)
        names.append(kinds.most_common(1)[0][0] + ("" if len(kinds) == 1 else f" (mixed {dict(kinds)})"))
    print(f"===== ws {ws}: the ear's types {[list(t) for t in types]}")
    print(f"  named by the world (for the reader of this printout only): {names} · heard alone {st['alone_counts']} · one-alone = type {st['one_alone']} ({names[st['one_alone']] if st['one_alone'] is not None else None})")
    rs = R.r_seed_root(SCORED, ws)
    K = json.loads((rs / "keys.json").read_text())["items"]["M6"]
    tr6 = C.load_truth(C.cache_dir(ROOT, ws, "m6", R.R_TSET))
    th6 = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "m6", R.R_TSET)))
    score = collections.defaultdict(lambda: [0, 0])
    for it in K:
        r6 = tr6[it["row"]]; ft = r6["fix_thing"]
        if not M.covered(it["target"], ft):
            continue
        X = th6.for_arm("A-RW", it["row"])
        mem, _ = th6.members(it["row"])
        labels = [M.hyp_label(c) for c in M.hyp_counts(mem, ft)]
        Z = L.stats.standardise(np.atleast_2d(X))
        E = Z - proto[None, :]
        cands = {"euclid": np.linalg.norm(E, axis=1)}
        for k, lam in enumerate(st["lam"]):
            if lam is not None:
                cands[f"type {k} = {names[k]}"] = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", E, lam, E), 0.0))
        for name, d in cands.items():
            score[name][0] += int(labels[int(np.argmin(d))] == it["target"]); score[name][1] += 1
    for name, (a, n) in score.items():
        print(f"  NEAREST under {name:<34} {a}/{n} = {a / max(1, n):.3f}")
