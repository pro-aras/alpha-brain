# edit: Claude (Fable 5.1, the seat), 2026-09-28 — READ-ONLY diagnosis 2 of M6: is a young word's pointing a band test whose
# ties are broken at random? Predictions written BEFORE the run (see the print at the top).
import json, collections
from pathlib import Path
import numpy as np
from brain.scene import world as W, cache as C, learners as Lr, marks as M, run as R
from brain.world.seeds import substream

print("PREDICTIONS (written before the run): (1) on covered M6 items the score vector for «dax» holds only 0.0 and -inf; "
      "(2) where exactly ONE hypothesis is inside the band the law is right nearly always; (3) where 0 or >= 2 are inside, "
      "the law is at chance; (4) pointing at the hypothesis NEAREST the prototype beats the law at seed 20261103.")
ROOT = Path("/data/dev/brain-runs/organ/scene"); SCORED = C.RUNS
for ws in W.WORLD_SEEDS:
    train = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "train")))
    L = Lr.RWLearner(lr=R.ARM_LR.get("A-RW", 0.01))
    seen = []
    done = 0
    for rp in W.READING_POINTS:
        R.train_arm("A-RW", L, train, train.p.words, None, range(done, rp), ws, seen)
        done = rp
        R.prepare("A-RW", L, seen)
        L.calibrate_r(0.3, None)
    j = L.index[W.DAX_WORD]
    rs = R.r_seed_root(SCORED, ws)
    K = json.loads((rs / "keys.json").read_text())["items"]["M6"]
    A = json.loads((rs / "arms" / "A-RW-R" / "answers_10000.json").read_text())["point"]
    tr6 = C.load_truth(C.cache_dir(ROOT, ws, "m6", R.R_TSET))
    th6 = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "m6", R.R_TSET)))
    proto = L.prototype(j); band = L.band(j)
    vals = collections.Counter(); by_in = collections.defaultdict(lambda: [0, 0]); near = [0, 0]; law = [0, 0]; same = 0
    rank_of_moon = []
    for it in K:
        r6 = tr6[it["row"]]; ft = r6["fix_thing"]
        if not M.covered(it["target"], ft):
            continue
        X = th6.for_arm("A-RW", it["row"])
        mem, _ = th6.members(it["row"])
        labels = [M.hyp_label(c) for c in M.hyp_counts(mem, ft)]
        Z = L.stats.standardise(np.atleast_2d(X))
        d = np.linalg.norm(Z - proto[None, :], axis=1)
        a = A[it["item_id"]]
        for v in a["scores"]:
            vals["-inf" if v == float("-inf") else ("0.0" if v == 0.0 else "other")] += 1
        n_in = int(np.sum(d <= band))
        ok_law = labels[int(a["point"])] == it["target"]
        key = "one inside" if n_in == 1 else ("none inside" if n_in == 0 else "two or more inside")
        by_in[key][0] += int(ok_law); by_in[key][1] += 1
        law[0] += int(ok_law); law[1] += 1
        k = int(np.argmin(d))
        near[0] += int(labels[k] == it["target"]); near[1] += 1
        order = list(np.argsort(d))
        moon_h = [h for h, lab in enumerate(labels) if lab == it["target"]]
        if moon_h:
            rank_of_moon.append(min(order.index(h) for h in moon_h))
    print(f"===== ws {ws}: «dax» meetings {int(L.proto_w[j]) if hasattr(L, 'proto_w') else '?'} · band {band:.3f} · covered M6 items {law[1]}")
    print("  score values over the covered items:", dict(vals))
    print("  THE LAW by how many hypotheses fall inside the band:", {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_in.items())})
    print(f"  THE LAW {law[0]}/{law[1]} = {law[0] / max(1, law[1]):.3f}   ·   NEAREST-PROTOTYPE {near[0]}/{near[1]} = {near[0] / max(1, near[1]):.3f}")
    print("  rank of the moon's hypothesis by distance to the prototype (0 = nearest):", dict(collections.Counter(rank_of_moon)))
