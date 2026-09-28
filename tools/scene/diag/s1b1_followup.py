# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 14:37 +0400 — PART A of the coordinator's follow-up (after S1b-1's hand-back, before
# S1c): three DIAGNOSES of S1b-1, read by no verdict. learners.py / marks.py / world.py are untouched: every counterfactual
# lives here. Output: /data/dev/brain-runs/scene-s1b1/gate/diag_followup.out.
#   (A1) the residual truth of N-SHUF's stream: how often a deranged utterance is still TRUE of a thing in the scene it
#        was paired with (per phrase, and per word type), beside the independent-draws base rate and the true stream's 1.0;
#   (A2) the null's distribution: K = 10 fresh derangements per seed (substream(seed, "null:<seed>:<k>"), k = 1..10) and
#        the unit's own (k = 0, the control: it must reproduce the unit), N-SHUF run to 10,000 scenes as the unit ran it
#        (training does not depend on the reading points' calibrations; the M1 pointing reads the state at 10,000), M1 on
#        the identical graded covered items; priced first, ≤ 8 at once, each wave waiting on its own pids;
#   (A3) the within-type mouth counterfactual on SPEAK: the forced name of ONE declared type (shape, colour, size), and a
#        fourth reading choosing the type by the within-type posterior margin, on the ONE-hypothesis items (X has one row, so
#        the read-back margin is +∞ — the converse does not hold: see A3′) and on the several-hypothesis items; the law's own
#        TRUTH reproduced first as the control. (label corrected: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 14:43 +0400)
# Run from a pinned copy:  cd /data/dev/brain-runs/scene/code-<sha> && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 \
#   TMPDIR=/data/dev/brain-runs/tmp nice -n 19 /usr/bin/python3 -B tools/scene/diag/s1b1_followup.py all
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from brain.scene import cache as C
from brain.scene import learners as Lr
from brain.scene import marks as M
from brain.scene import run as R
from brain.scene import world as W
from brain.world.seeds import substream

ROOT = C.RUNS                                           # /data/dev/brain-runs/scene-s1b1 (the unit's root)
A2_DIR = ROOT / "diag-followup" / "a2"
UNIT_NSHUF_M1 = {20261101: 0.651, 20261102: 0.597, 20261103: 0.469}   # the unit's report (3 decimals, the control)
UNIT_TRUTH = {20261101: 0.671, 20261102: 0.716, 20261103: 0.600}
K = 10
BASE_PAIRS = 200_000
PRICE_LIMIT_CPU_MIN = 40.0
WAVE = 8


def perm_for(ws: int, k: int, n: int) -> np.ndarray:
    label = "n-shuf-permutation" if k == 0 else f"null:{ws}:{k}"
    return Lr.nshuf_permutation(substream(ws, label), n)


# ------------------------------------------------------------------------------------------------ (A1)
def a1() -> None:
    print("(A1) THE RESIDUAL TRUTH OF N-SHUF'S STREAM — how often a deranged utterance is still true of ≥ 1 thing in the "
          "scene it was paired with (the unit's own derangement), beside the independent-draws base rate "
          f"({BASE_PAIRS:,} random (utterance, scene) pairs of the same stream, substream '<seed>:a1-base') and the true stream")
    for ws in W.WORLD_SEEDS:
        T = C.load_truth(C.cache_dir(ROOT, ws, "train"))
        n = len(T)
        things = [M.things_of(r) for r in T]
        words = [tuple(r["words"]) for r in T]
        perm = perm_for(ws, 0, n)

        def rates(pairs):
            ph, per = 0, {t: [0, 0] for t in W.WORD_TYPES}
            for u, s in pairs:
                ws_ = words[u]
                ph += any(W.phrase_true_of(ws_, t) for t in things[s])
                for w in ws_:
                    typ = W.word_type(w)
                    per[typ][0] += any(W.word_true_of(w, t) for t in things[s])
                    per[typ][1] += 1
            m = len(pairs)
            return ph / m, {t: (a / b if b else None) for t, (a, b) in per.items()}

        der = rates([(int(perm[i]), i) for i in range(n)])
        rng = substream(ws, f"{ws}:a1-base")
        us = rng.integers(0, n, size=BASE_PAIRS)
        ss = rng.integers(0, n, size=BASE_PAIRS)
        base = rates(list(zip(us.tolist(), ss.tolist())))
        tru = rates([(i, i) for i in range(n)])
        print(f"   {ws}: deranged phrase true of ≥ 1 thing {der[0]:.4f} (n {n}) · base rate {base[0]:.4f} · the true stream {tru[0]:.4f}")
        print(f"            per word type — deranged: " + " · ".join(f"{t} {v:.4f}" for t, v in der[1].items())
              + " | base: " + " · ".join(f"{t} {v:.4f}" for t, v in base[1].items())
              + " | true: " + " · ".join(f"{t} {v:.4f}" for t, v in tru[1].items()))


# ------------------------------------------------------------------------------------------------ (A2)
def a2_run(ws: int, k: int, out: Path) -> None:
    """ONE null run: N-SHUF (A-RW's code, lr 0.01, the permuted utterances) trained to 10,000 scenes as the unit trained it;
    M1 read on the identical graded covered items with the items' own tie generators."""
    t0 = time.process_time()
    train = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "train")))
    perm = perm_for(ws, k, len(train.p))
    L = R.make_learner("N-SHUF", Lr.LR_S1B1, 0.3)
    R.train_arm("N-SHUF", L, train, lambda i: train.p.words(int(perm[i])), None, range(W.N_TRAIN), ws, None)
    Q = json.loads((ROOT / str(ws) / "questions.json").read_text())
    K_ = json.loads((ROOT / str(ws) / "keys.json").read_text())
    tt = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "test")))
    ans = R.answer_all("N-SHUF", L, {"M1": Q["questions"]["M1"]}, {"test": tt}, Q["test_seed"])
    g = M.grade_pointing(K_["items"]["M1"], ans, C.load_truth(C.cache_dir(ROOT, ws, "test")), tt.members, "gaze")
    b = M.summarise_pointing(g)["graded"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"seed": ws, "k": k, "m1": b["covered"], "n": b["n_covered"], "chance": b["chance_covered"],
                               "cpu_s": time.process_time() - t0}) + "\n")


def _spawn(jobs):
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", PYTHONUNBUFFERED="1",
               TMPDIR="/data/dev/brain-runs/tmp")
    procs = []
    for ws, k in jobs:
        out = A2_DIR / f"{ws}-{k:02d}.json"
        p = subprocess.Popen(["nice", "-n", "19", sys.executable, "-B", __file__, "a2-run", str(ws), str(k), str(out)],
                             env=env, stdout=subprocess.DEVNULL, stderr=open(A2_DIR / f"{ws}-{k:02d}.err", "w"))
        procs.append((ws, k, p))
    bad = []
    for ws, k, p in procs:                                # this wave waits on ITS OWN pids
        if p.wait() != 0:
            bad.append((ws, k, p.returncode))
    return bad


def a2() -> None:
    A2_DIR.mkdir(parents=True, exist_ok=True)
    jobs = [(ws, k) for ws in W.WORLD_SEEDS for k in range(0, K + 1)]
    # the price, first: one run solo
    first = jobs[1]
    t0 = time.perf_counter()
    bad = _spawn([first])
    one = json.loads((A2_DIR / f"{first[0]}-{first[1]:02d}.json").read_text())
    proj = one["cpu_s"] * len(jobs) / 60.0
    print(f"(A2) THE NULL'S DISTRIBUTION — the price: one N-SHUF run (seed {first[0]}, k {first[1]}) solo {one['cpu_s']:.1f} CPU-s "
          f"({time.perf_counter() - t0:.1f} s wall) → {len(jobs)} runs ≈ {proj:.1f} CPU-min (the limit {PRICE_LIMIT_CPU_MIN:.0f})")
    if bad or proj > PRICE_LIMIT_CPU_MIN:
        print(f"   STOP: {'the price is above the limit' if proj > PRICE_LIMIT_CPU_MIN else 'the priced run failed ' + str(bad)}")
        raise SystemExit(3)
    rest = [j for j in jobs if j != first]
    for w0 in range(0, len(rest), WAVE):
        wave = rest[w0:w0 + WAVE]
        bad = _spawn(wave)
        if bad:
            print(f"   STOP: runs failed {bad}")
            raise SystemExit(4)
    cpu = 0.0
    for ws in W.WORLD_SEEDS:
        rows = [json.loads((A2_DIR / f"{ws}-{k:02d}.json").read_text()) for k in range(0, K + 1)]
        cpu += sum(r["cpu_s"] for r in rows)
        unit = rows[0]
        fresh = np.array([r["m1"] for r in rows[1:]])
        rank = int((fresh < unit["m1"]).sum())
        print(f"   {ws}: k=0 (the unit's own) {unit['m1']:.3f} — the unit's report {UNIT_NSHUF_M1[ws]:.3f} "
              f"({'reproduced' if abs(unit['m1'] - UNIT_NSHUF_M1[ws]) < 0.0005 else 'NOT reproduced'}); chance {unit['chance']:.3f} + 0.05 = "
              f"{unit['chance'] + 0.05:.3f}; n {unit['n']}")
        print(f"            k=1..{K}: " + " ".join(f"{v:.3f}" for v in fresh)
              + f" → min {fresh.min():.3f} · median {np.median(fresh):.3f} · max {fresh.max():.3f} · 95th pct {np.percentile(fresh, 95):.3f} "
              f"· above chance + 0.05 in {(fresh > unit['chance'] + 0.05).sum()}/{K} · the unit's draw is above {rank}/{K} fresh draws")
    print(f"   all {len(jobs)} runs: {cpu / 60:.1f} CPU-min")


# ------------------------------------------------------------------------------------------------ (A3)
def within_type_margin(L, raw_thing, words):
    """The learner's within-type posterior q_w = p_w / Σ_type p_w over the type's heard words (declared); returns (top word,
    q_top − q_runner-up)."""
    cand = [w for w in words if w in L.index]
    Z = L.stats.standardise(np.atleast_2d(raw_thing))
    lp = L.logp_answer(Z, getattr(L, "_bands_cache", None))[0]
    p = np.exp(np.array([lp[L.index[w]] for w in cand]))
    q = p / p.sum() if p.sum() > 0 else np.full(len(cand), 1.0 / len(cand))
    o = np.argsort(-q, kind="stable")
    return cand[int(o[0])], float(q[o[0]] - (q[o[1]] if len(cand) > 1 else 0.0))


def a3() -> None:
    print("(A3) THE WITHIN-TYPE MOUTH COUNTERFACTUAL on SPEAK — A-RW (lr 0.01) retrained to 10,000 per seed; TRUTH = the word "
          "is true of the target and of no other thing in view (the world's truth). Readings: the forced name of ONE declared "
          "type (name_forced over shape / colour / size), and the type chosen by the within-type posterior margin (q = p_w / "
          "Σ_type p_w; top − runner-up; declared). The law's own TRUTH on the same items beside.")
    print("   CAVEAT: NAME's 0.93–0.95 («what is this?» emits the true word) is read on ONE-THING test scenes; the SPEAK items "
          "are 2- and 3-thing scenes (a different population), and a word true of the target may also be true of another thing.")
    for ws in W.WORLD_SEEDS:
        train = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "train")))
        L = R.make_learner("A-RW", Lr.LR_S1B1, 0.3)
        seen: list = []
        R.train_arm("A-RW", L, train, train.p.words, None, range(W.N_TRAIN), ws, seen)
        L.calibrate(seen)
        Q = json.loads((ROOT / str(ws) / "questions.json").read_text())["questions"]
        K_ = json.loads((ROOT / str(ws) / "keys.json").read_text())["items"]
        st = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "speak")))
        tr = C.load_truth(C.cache_dir(ROOT, ws, "speak"))
        q_by = {q["item_id"]: q for q in Q["SPEAK"]}
        ans = R.answer_all("A-RW", L, {"SPEAK": Q["SPEAK"]}, {"speak": st}, W.TEST_SEEDS[ws])
        ctrl = M.summarise_speak(M.grade_speak(K_["SPEAK"], ans, tr, {q["item_id"]: q.get("hyp") for q in Q["SPEAK"]}))
        print(f"   {ws}: the control — the law's TRUTH re-read {ctrl['truth']:.3f} (n {ctrl['n_spoken']}) vs the unit's {UNIT_TRUTH[ws]:.3f} "
              f"({'reproduced' if abs(ctrl['truth'] - UNIT_TRUTH[ws]) < 0.0005 else 'NOT reproduced'})")
        tables = {"one": {}, "several": {}}
        for it in K_["SPEAK"]:
            q = q_by[it["item_id"]]
            if q.get("hyp") is None:
                continue
            X = st.for_arm("A-RW", q["row"])
            h = int(q["hyp"])
            row = tr[it["row"]]
            things = M.things_of(row)
            t = int(it["target"])
            key = "one" if X.shape[0] == 1 else "several"
            tab = tables[key]
            for typ, ws_words in R.TYPE_WORDS.items():
                w = L.name_forced(X[h], ws_words)
                tab.setdefault(typ, []).append(w is not None and M.unique_true([w], things, t, range(len(things))))
            best = max(((within_type_margin(L, X[h], R.TYPE_WORDS[typ]), typ) for typ in R.TYPE_WORDS), key=lambda z: z[0][1])
            (w, _m), typ = best
            tab.setdefault("by margin", []).append(M.unique_true([w], things, t, range(len(things))))
            tab.setdefault("chosen type", []).append(typ)
            a = ans[it["item_id"]]
            if a.get("spoken") is not None:
                tab.setdefault("the law (spoken)", []).append(M.unique_true(a["spoken"], things, t, range(len(things))))
        for key, label in (("one", "ONE hypothesis in view (X has one row; the read-back margin is then +∞, but +∞ does not imply one row — A3′)"), ("several", "SEVERAL hypotheses in view")):
            tab = tables[key]
            if not tab:
                print(f"      {label}: no items")
                continue
            chosen = {typ: tab["chosen type"].count(typ) for typ in R.TYPE_WORDS}
            print(f"      {label}: " + " · ".join(f"{r} {np.mean(tab[r]):.3f} (n {len(tab[r])})"
                                                 for r in ("shape", "colour", "size", "by margin", "the law (spoken)") if r in tab)
                  + f" · the margin chose {chosen}")


class _NoYoungWords:
    """A COUNTERFACTUAL arm for the mouth only (edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 14:39 +0400): the learner with every word
    of fewer than 3 meetings (P_FROM_MEETING) dropped from HELD — everything else is the learner's own."""

    def __init__(self, L):
        self.L, self.ear = L, L.ear

    def held_words(self, x):
        return [w for w in self.L.held_words(x) if self.L.meetings[self.L.index[w]] >= Lr.P_FROM_MEETING]

    def answer_point(self, X, phrase, rng):
        return self.L.answer_point(X, phrase, rng)


def a3_dax() -> None:
    """(A3′) the spoken phrases broken down (a CORRECTION to S1B1-HANDBACK §6 (b), which read a +∞ read-back margin as «one
    hypothesis in view»): a word with < 3 meetings («dax») answers by its band, p ∈ {0, 1}, so when its band holds the target
    and not the others its read-back margin is +∞ and it wins the margin tie-break among one-word candidates."""
    print("(A3′) A-RW's SPOKEN phrases at 10,000, by (the word is «dax» or not) × (hypotheses in view) × (margin) × TRUE — and a "
          "COUNTERFACTUAL mouth with the words of < 3 meetings dropped from HELD (a reading, not a proposal)")
    for ws in W.WORLD_SEEDS:
        train = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "train")))
        L = R.make_learner("A-RW", Lr.LR_S1B1, 0.3)
        seen: list = []
        R.train_arm("A-RW", L, train, train.p.words, None, range(W.N_TRAIN), ws, seen)
        L.calibrate(seen)
        Q = json.loads((ROOT / str(ws) / "questions.json").read_text())["questions"]
        K_ = json.loads((ROOT / str(ws) / "keys.json").read_text())["items"]
        st = R.Things(C.ScenePercepts(C.cache_dir(ROOT, ws, "speak")))
        tr = C.load_truth(C.cache_dir(ROOT, ws, "speak"))
        q_by = {q["item_id"]: q for q in Q["SPEAK"]}
        A = json.loads((ROOT / str(ws) / "arms" / "A-RW" / "answers_10000.json").read_text())["answers"]
        import collections
        c = collections.Counter()
        cf = []
        same = 0   # the control: the law's own mouth, re-run here with the same rng factory, must reproduce the unit's spoken phrase
        for it in K_["SPEAK"]:
            q = q_by[it["item_id"]]
            if q.get("hyp") is None:
                continue
            X = st.for_arm("A-RW", q["row"])
            row = tr[it["row"]]
            things = M.things_of(row)
            t = int(it["target"])
            a = A[it["item_id"]]
            sp = a.get("spoken")
            if sp is not None:
                true = M.unique_true(sp, things, t, range(len(things)))
                cause = ("true" if true else "false of the target" if not W.phrase_true_of(sp, things[t])
                         else "also true of another")
                c[("«dax»" if sp == ["dax"] else "other", "1 hyp" if X.shape[0] == 1 else "≥2 hyp",
                   "+∞" if a["margin"] == float("inf") else "finite", cause)] += 1
            law = Lr.produce(L, X, int(q["hyp"]), lambda it=it: M.tie_rng(W.TEST_SEEDS[ws], it["item_id"]))
            same += law.get("spoken") == sp
            b = Lr.produce(_NoYoungWords(L), X, int(q["hyp"]), lambda it=it: M.tie_rng(W.TEST_SEEDS[ws], it["item_id"]))
            if b.get("spoken") is not None:
                cf.append(M.unique_true(b["spoken"], things, t, range(len(things))))
        n_sp = sum(c.values())
        n_dax = sum(v for k, v in c.items() if k[0] == "«dax»")
        print(f"   {ws}: the control — the law's mouth re-run here reproduces the unit's spoken phrase on {same} of "
              f"{sum(1 for it in K_['SPEAK'] if q_by[it['item_id']].get('hyp') is not None)} items")
        print(f"   {ws}: spoken {n_sp}, of which «dax» {n_dax} (all false: {all(k[3] != 'true' for k in c if k[0] == '«dax»')}); "
              + " · ".join(f"{'/'.join(k)} {v}" for k, v in sorted(c.items())))
        print(f"            the counterfactual mouth without the young words: TRUTH {np.mean(cf):.3f} (n {len(cf)}) — the unit's {UNIT_TRUTH[ws]:.3f}")


def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else "all"
    if cmd == "a2-run":
        a2_run(int(argv[2]), int(argv[3]), Path(argv[4]))
        return 0
    R.check_prereg()
    if cmd in ("a1", "all"):
        a1()
    if cmd in ("a2", "all"):
        a2()
    if cmd in ("a3", "all"):
        a3()
    if cmd in ("a3dax", "a3", "all"):
        a3_dax()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
