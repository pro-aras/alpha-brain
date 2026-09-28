# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:36 +0400 — a DIAGNOSIS of THE FIRST GATE's instrument verdict (read by no verdict).
# Run: cd /data/dev/brain-runs/scene/code-d102d80 && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -B <this file>
"""Negative control for the instrument verdict's LOO (NOT a verdict): the same protocol, P-ORACLE (ε 0.3), but each of
the 299 training scenes carries the utterance of ANOTHER gate scene (a seeded derangement over the 300) — blind to the
word→feature pairing only. Must read ≈ chance (shape 1/6, colour 1/5, size 1/2); anything else is a leak."""
import numpy as np
from brain.scene import cache as C, learners as Lr, marks as M, run as R
from brain.world.seeds import substream
ws = 20261101
trs = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, ws, "train"))); T = C.load_truth(C.cache_dir(C.RUNS, ws, "train"))
rows = list(range(300)); one = [i for i in rows if len(T[i]["things"]) == 1]
for rep in range(3):
    perm = Lr.nshuf_permutation(substream(ws, f"verdict-null:{rep}"), 300)
    acc = {t: [] for t in R.TYPE_WORDS}
    for i in one:
        Rd = Lr.LDAReader(0.3)
        for j in rows:
            if j == i: continue
            ref = R.referent_index("P-ORACLE", trs, T[j])
            Rd.train_scene(Lr.feed_oracle(trs.for_arm("P-ORACLE", j), ref), trs.p.words(int(perm[j])))
        Rd.prepare()
        mem, pos = trs.members(i); h = M.thing_hypothesis(0, mem, pos, T[i]["fix_thing"], tuple(T[i]["centroids"][0]))
        x = trs.for_arm("P-ORACLE", i)[h]
        for t, wl in R.TYPE_WORDS.items():
            acc[t].append(Rd.name_forced(x, wl) == T[i]["things"][0][t])
    print(f"shuffled-utterance LOO, permutation {rep}:", {t: f"{sum(v)}/{len(v)} = {np.mean(v):.3f}" for t, v in acc.items()},
          "chance: shape 0.167 colour 0.200 size 0.500")
