# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:46 +0400 — a DIAGNOSIS (read by no verdict): THE FIRST GATE's step 3 recomputed
# with the gate's own code, items and generators, printed PER SCENE SIZE (the gate stored only the pooled block). Its
# pooled rows must equal gate.json's exactly, or nothing below it is read.
# Run: cd /data/dev/brain-runs/scene/code-d102d80 && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -B <this file>
import json
from brain.scene import cache as C, learners as Lr, marks as M, run as R
from brain.world.seeds import substream
ws = 20261101
g = json.loads((C.RUNS / "gate" / "gate.json").read_text())
trs = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, ws, "train"))); T = C.load_truth(C.cache_dir(C.RUNS, ws, "train"))
tt = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, ws, "test"))); TT = C.load_truth(C.cache_dir(C.RUNS, ws, "test"))
Q = json.loads((C.RUNS / str(ws) / "questions.json").read_text()); K = json.loads((C.RUNS / str(ws) / "keys.json").read_text())
perm = Lr.nshuf_permutation(substream(ws, "n-shuf-permutation"), len(trs.p))
for arm in R.ARMS:
    L = R.make_learner(arm, g["lr"], g["eps"]); seen = []
    words_of = (lambda i: trs.p.words(int(perm[i]))) if arm == "N-SHUF" else trs.p.words
    R.train_arm(arm, L, trs, words_of, T if arm in ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH") else None, range(300), ws, seen)
    R.prepare(arm, L, seen)
    ans = R.answer_all(arm, L, {"M1": Q["questions"]["M1"]}, {"test": tt}, Q["test_seed"])
    s = M.summarise_pointing(M.grade_pointing(K["items"]["M1"], ans, TT, tt.members, "truth" if arm == "ORACLE-TRUTH" else "gaze"))
    same = abs(s["all"]["covered"] - g["arms300"][arm]["covered"]) < 1e-12 and abs(s["all"]["all"] - g["arms300"][arm]["all"]) < 1e-12
    print(f"{arm:<14} pooled covered {s['all']['covered']:.3f} (gate.json {g['arms300'][arm]['covered']:.3f}, {'SAME' if same else 'DIFFERS'}) · "
          + " · ".join(f"size{n}: {s[f'size{n}']['covered']:.3f} vs chance {s[f'size{n}']['chance_covered']:.3f} (n {s[f'size{n}']['n_covered']})"
                       for n in (1, 2, 3)))
