# edit: Claude (Fable 5.1, the seat), 2026-09-28 — READ-ONLY diagnosis of M6 («dax», one meeting) on the scored run's caches.
"""Which hypothesis did the ONE meeting write «dax» to, against where the moon was; and what do the M6 answers point at."""
import json, sys, collections
from pathlib import Path
import numpy as np
from brain.scene import world as W, cache as C, learners as Lr, marks as M, run as R, health as H
from brain.world.seeds import substream

ROOT = __import__("pathlib").Path("/data/dev/brain-runs/organ/scene")   # the redrawn caches (byte-identical to the scored ones)
SCORED = C.RUNS
for ws in W.WORLD_SEEDS:
    train = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "train")))
    truth = C.load_truth(C.cache_dir(ROOT, ws, "train"))
    L = Lr.RWLearner(lr=R.ARM_LR.get("A-RW", 0.01))
    i = W.DAX_INDEX
    for r in range(0, i):
        L.train_scene(train.for_arm("A-RW", r), train.p.words(r), referent=None, rng=substream(ws, f"episodic:{r}"))
    X = train.for_arm("A-RW", i)
    words = train.p.words(i)
    row = truth[i]
    things = M.things_of(row)
    members, pos = train.members(i)
    ft = row["fix_thing"]
    labels = [M.hyp_label(c) for c in M.hyp_counts(members, ft)]
    known_before = set(L.index)
    L.train_scene(X, words, referent=None, rng=substream(ws, f"episodic:{i}"))
    att = H.attribution(L, X, words, [w for w in words if w not in known_before])
    print(f"===== ws {ws}  dax scene index {i}")
    print("  said:", list(words), " referent thing:", row.get("referent"))
    print("  things:", [(t.shape, t.colour, t.size) for t in things])
    print("  fixations → thing:", ft)
    print("  hypotheses: members", [list(m) for m in members], " labels (thing each hypothesis is on):", labels)
    print("  attribution after the meeting:", att)
    moon = [k for k, t in enumerate(things) if t.shape == W.DAX_SHAPE]
    hyp_on_moon = [h for h, lab in enumerate(labels) if lab in moon]
    print("  moon is thing", moon, "; hypotheses on the moon:", hyp_on_moon,
          "; WRITTEN TO:", att.get(W.DAX_WORD), "→ thing", (labels[att[W.DAX_WORD]] if att.get(W.DAX_WORD) is not None else None))
    # M6 answers on the scored record (fresh set)
    rs = R.r_seed_root(SCORED, ws)
    K = json.loads((rs / "keys.json").read_text())["items"]["M6"]
    A = json.loads((rs / "arms" / "A-RW-R" / "answers_10000.json").read_text())["point"]
    tr6 = C.load_truth(C.cache_dir(ROOT, ws, "m6", R.R_TSET))
    th6 = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "m6", R.R_TSET)))
    tally = collections.Counter(); wrong_shapes = collections.Counter(); wrong_cols = collections.Counter()
    for it in K:
        r6 = tr6[it["row"]]; t6 = M.things_of(r6); ft6 = r6["fix_thing"]
        cov = M.covered(it["target"], ft6)
        a = A.get(it["item_id"]) or {}
        if not cov:
            tally["uncovered"] += 1; continue
        mem, _ = th6.members(it["row"])
        lab = M.hyp_label(M.hyp_counts(mem, ft6)[int(a["point"])]) if a.get("point") is not None else None
        if lab == it["target"]:
            tally["correct"] += 1
        else:
            tally["wrong"] += 1
            if lab is not None:
                wrong_shapes[t6[lab].shape] += 1; wrong_cols[t6[lab].colour] += 1
            else:
                wrong_shapes["(mixed/none)"] += 1
    print("  M6 fresh:", dict(tally), " wrong answers land on shapes:", dict(wrong_shapes), " colours:", dict(wrong_cols))
    dax_t = things[moon[0]] if moon else None
    print("  the moon at the meeting was:", (dax_t.shape, dax_t.colour, dax_t.size) if dax_t else None)
    cols6 = collections.Counter(M.things_of(tr6[it["row"]])[it["target"]].colour for it in K)
    print("  M6 test moons' colours:", dict(cols6))
