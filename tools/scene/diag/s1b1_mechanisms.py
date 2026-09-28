# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 14:14 +0400 — DIAGNOSES of three S1b-1 results (read by no verdict).
# (a) M2a: the learner's τ_none is calibrated on EVERY ≥ 2-hypothesis training scene, including those whose referent the
#     gaze never fixated (the learner cannot know) — the fit of the said phrase there is poor and may set the 0.95
#     quantile. A-RW (lr 0.01) re-run on world seed 1 to 10,000 scenes; f(t*) split by the referent's coverage (truth).
# (b) TRUTH: the mouth speaks ONE word; how often that word is also true of another thing in view, and the read-back
#     margins of the true and the false spoken phrases (from the unit's own answers at 10,000).
# (c) N-SHUF above chance: a SALIENCE pointer (the hypothesis with the most fixations; ties random) on M1's graded items.
# Run: cd /data/dev/brain-runs/scene/code-<sha> && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -B <this file>
import json
import numpy as np
from brain.scene import cache as C, learners as Lr, marks as M, run as R, world as W
from brain.world.seeds import substream
ROOT = C.RUNS
ws = 20261101
tr = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "train"))); T = C.load_truth(C.cache_dir(ROOT, ws, "train"))
L = R.make_learner("A-RW", Lr.LR_S1B1, 0.3)
seen = []
R.train_arm("A-RW", L, tr, tr.p.words, None, range(W.N_TRAIN), ws, seen)
L.calibrate(seen)
cov, unc = [], []
for i, (raw, words, _r) in enumerate(seen):
    if np.atleast_2d(raw).shape[0] < 2 or any(w not in L.index for w in words):
        continue
    f = float(np.min(L.phrase_fit(L.stats.standardise(raw), list(dict.fromkeys(words)), "diag")))
    (cov if M.covered(int(T[i]["referent"]), T[i]["fix_thing"]) else unc).append(f)
allf = cov + unc
print(f"(a) τ_none(diag) = {L.tau_none['diag']:.3f} over n {len(allf)} training scenes with ≥ 2 hypotheses; the referent UNCOVERED in "
      f"{len(unc)} ({len(unc) / len(allf):.3f}) — median f {np.median(unc):.2f} vs {np.median(cov):.2f} covered; "
      f"f > τ_none: uncovered {np.mean(np.array(unc) > L.tau_none['diag']):.3f} · covered {np.mean(np.array(cov) > L.tau_none['diag']):.3f}")
tau_cov = Lr.conformal_upper(cov, 0.95)
print(f"    a counterfactual τ over the COVERED-referent scenes only (a reading, not the law): {tau_cov:.3f}")
Q = json.loads((ROOT / str(ws) / "questions.json").read_text())["questions"]
K = json.loads((ROOT / str(ws) / "keys.json").read_text())["items"]
tt = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "test")))
TT = C.load_truth(C.cache_dir(ROOT, ws, "test"))
key = {it["item_id"]: it for it in K["M1"] + K["M2a"]}
for name, tau in (("the law's τ_none", L.tau_none["diag"]), ("the covered-only τ", tau_cov)):
    ref, fr = [], []
    for q in Q["M2a"]:
        f = float(np.min(L.phrase_fit(L.stats.standardise(tt.for_arm("A-RW", q["row"])), q["phrase"], "diag")))
        ref.append(f > tau)
    for q in Q["M1"]:
        it = key[q["item_id"]]
        if it["n_things"] < 2 or not M.covered(it["target"], TT[it["row"]]["fix_thing"]):
            continue
        f = float(np.min(L.phrase_fit(L.stats.standardise(tt.for_arm("A-RW", q["row"])), q["phrase"], "diag")))
        fr.append(f > tau)
    print(f"    M2a under {name} {tau:.3f}: refusal {np.mean(ref):.3f} (n {len(ref)}) · false refusal on the graded covered M1 {np.mean(fr):.3f} (n {len(fr)})")
# (b) the one-word mouth
A = json.loads((ROOT / str(ws) / "arms" / "A-RW" / "answers_10000.json").read_text())["answers"]
sp_truth = C.load_truth(C.cache_dir(ROOT, ws, "speak"))
tm, fm, other_true = [], [], 0
n = 0
for it in K["SPEAK"]:
    a = A[it["item_id"]]
    if a.get("spoken") is None:
        continue
    row = sp_truth[it["row"]]
    things = M.things_of(row)
    true = M.unique_true(a["spoken"], things, it["target"], range(len(things)))
    also = any(W.phrase_true_of(a["spoken"], things[k]) for k in range(len(things)) if k != it["target"])
    n += 1
    other_true += also
    (tm if true else fm).append(a["margin"])
print(f"(b) A-RW's spoken phrases at 10,000 (seed {ws}): {n}, of lengths {sorted(set(len(A[it['item_id']]['spoken']) for it in K['SPEAK'] if A[it['item_id']].get('spoken')))}; "
      f"also true of ANOTHER thing in view: {other_true} ({other_true / n:.3f}); read-back margin median true {np.median(tm):.2f} (n {len(tm)}) · false {np.median(fm):.2f} (n {len(fm)})")
# (c) a salience pointer on M1
ok, tot = 0, 0
ns = json.loads((ROOT / str(ws) / "arms" / "N-SHUF" / "answers_10000.json").read_text())["answers"]
agree = 0
for q in Q["M1"]:
    it = key[q["item_id"]]
    row = TT[it["row"]]
    if it["n_things"] < 2 or not M.covered(it["target"], row["fix_thing"]):
        continue
    members, pos = tt.members(q["row"])
    counts = np.array([len(m) for m in members], dtype=float)
    k = Lr.pick(counts, M.tie_rng(W.TEST_SEEDS[ws], q["item_id"]), "max")
    lab = M.hyp_label(M.hyp_counts(members, row["fix_thing"])[k])
    ok += lab == it["target"]
    tot += 1
    agree += (ns[q["item_id"]]["point"] == k)
print(f"(c) the salience pointer (the most-fixated hypothesis) on M1's graded covered items: {ok / tot:.3f} (n {tot}); N-SHUF agrees with it on {agree / tot:.3f}")
# (b′) why each false spoken phrase is false: a word false of the TARGET itself, or true of the target and of another
#      thing the gaze SAW, or true of the target and of another thing the gaze MISSED; by the spoken word's type
import collections
why = collections.Counter()
for it in K["SPEAK"]:
    a = A[it["item_id"]]
    sp = a.get("spoken")
    if sp is None:
        continue
    row = sp_truth[it["row"]]
    things = M.things_of(row)
    t = it["target"]
    if M.unique_true(sp, things, t, range(len(things))):
        continue
    seen_k = {k for k in row["fix_thing"] if k is not None}
    wt = W.word_type(sp[0])
    if not W.phrase_true_of(sp, things[t]):
        why[("false of the target", wt, "one hypothesis" if a["margin"] == float("inf") else "several")] += 1
    elif any(W.phrase_true_of(sp, things[k]) for k in seen_k if k != t):
        why[("also true of a SEEN thing", wt)] += 1
    else:
        why[("also true of an UNSEEN thing", wt)] += 1
print("(b′) the false spoken phrases, by cause and the word's type:", dict(why))
# (b″) a COUNTERFACTUAL reading (not the law): the SAME accepted candidates, but ties at an infinite margin (one hypothesis
#      in view) broken by the target's own Σ log p (the most confident candidate) instead of the declared order key /
#      first-heard; and how often the TRUE word of the target was held at all.
st = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "speak")))
sp_q = {q["item_id"]: q for q in Q["SPEAK"]}
res = {"law": [], "cf": []}
held_true = 0
n_items = 0
for it in K["SPEAK"]:
    q = sp_q[it["item_id"]]
    if q.get("hyp") is None:
        continue
    X = st.for_arm("A-RW", q["row"])
    k = int(q["hyp"])
    held = L.held_words(X[k])
    row = sp_truth[it["row"]]
    things = M.things_of(row)
    t = it["target"]
    n_items += 1
    held_true += any(W.phrase_true_of([w], things[t]) and M.unique_true([w], things, t, range(len(things))) for w in held)
    acc = []
    for c in [L.ear.order(c) for c in Lr._subsets(held) if not L.ear.excluded(c)]:
        a = L.answer_point(X, c, M.tie_rng(W.TEST_SEEDS[ws], it["item_id"]))
        sc = np.asarray(a["scores"])
        top = np.flatnonzero(sc == sc.max())
        if not (top.size == 1 and int(top[0]) == k) or a["none"]:
            continue
        others = np.delete(sc, k)
        margin = float(sc[k] - others.max()) if others.size else float("inf")
        acc.append((c, margin, float(sc[k])))
    if not acc:
        continue
    law = sorted(acc, key=lambda z: (len(z[0]), -z[1], tuple(L.ear.key(w) for w in z[0]), tuple(L.ear.first.get(w, 10 ** 6) for w in z[0])))[0][0]
    cf = sorted(acc, key=lambda z: (len(z[0]), -z[1], -z[2]))[0][0]
    for key_, ph in (("law", law), ("cf", cf)):
        res[key_].append(M.unique_true(ph, things, t, range(len(things))))
print(f"(b″) seed {ws}, A-RW at 10,000: TRUTH with the declared tie-break {np.mean(res['law']):.3f} (n {len(res['law'])}) · with ties at "
      f"+∞ broken by the target's own Σ log p {np.mean(res['cf']):.3f} (a counterfactual reading) · items whose HELD words include a "
      f"word uniquely true of the target: {held_true}/{n_items}")
