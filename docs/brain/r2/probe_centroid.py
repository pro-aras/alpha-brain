"""The eye's features, read by a reader that does not learn — B1 r2 evidence (Claude (Opus 5.5), 2026-09-27 18:36 +0400).
Nearest class mean (cosine) of the 5×144 glance features of every single-letter TEACH row, the SAME features every B1
network arm receives through `brain.arms.soft.steps.StepEncoder` (cache.glances(row)[i]). Scored on (a) the NAME-cue
training asks before the first CONST ask (their FEEDBACK `right`) and (b) T_L's NAME-cue asks (the truth's `answer`).
Run with a b1 tree on PYTHONPATH (a script run BY PATH puts its own folder on sys.path, SOLUTIONS #242), under the brain venv:
  PYTHONPATH=/data/dev/genome-wt-b1int python docs/brain/r2/probe_centroid.py /data/dev/brain-runs/b1 20261001
"""
import json
import sys

import numpy as np

from brain.glance_cache import Cache

root, seed = sys.argv[1], sys.argv[2]
cache = Cache(f"{root}/cache/{seed}")
rows = [json.loads(l) for l in open(f"{root}/{seed}/tape.jsonl")]
truth = {}
for l in open(f"{root}/{seed}/truth.jsonl"):
    t = json.loads(l)
    truth[t.get("seq", t.get("ask_seq"))] = t
teach = [r for r in rows if r["kind"] == "TEACH" and len(r["payload"]["name"]) == 1]
fb = {r["payload"]["ask_seq"]: r["payload"]["right"] for r in rows if r["kind"] == "FEEDBACK"}
const = [r["seq"] for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["CONST"]]
first_const = min(const) if const else 10 ** 9
pre = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["seq"] < first_const and r["seq"] in fb]
tl = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["phase"] == "T_L"]


def vec(row_id, how):
    g = np.asarray(cache.glances(int(row_id)), dtype=np.float64)
    return {"mean": g.mean(0), "concat": g.reshape(-1), "last": g[-1]}[how]


allg = np.stack([np.asarray(cache.glances(int(r["payload"]["glance_row"]))) for r in teach])
print(f"seed {seed}: {len(teach)} single-letter TEACH rows; glances per row {allg.shape[1:]}; feature mean {allg.mean():.3f} "
      f"std {allg.std():.3f} min {allg.min():.3f} max {allg.max():.3f}; per-glance norm {np.linalg.norm(allg, axis=2).mean():.2f}")
for how in ("mean", "concat", "last"):
    X = np.stack([vec(r["payload"]["glance_row"], how) for r in teach])
    y = [r["payload"]["name"] for r in teach]
    names = sorted(set(y))
    C = np.stack([X[[i for i, v in enumerate(y) if v == n]].mean(0) for n in names])
    C /= np.linalg.norm(C, axis=1, keepdims=True)

    def pred(v):
        return names[int(np.argmax(C @ (v / (np.linalg.norm(v) + 1e-12))))]

    ok_pre = sum(pred(vec(r["payload"]["operands"][0]["value"], how)) == fb[r["seq"]] for r in pre)
    ok_tl = sum(pred(vec(r["payload"]["operands"][0]["value"], how)) == truth.get(r["seq"], {}).get("answer") for r in tl)
    print(f"  nearest class mean [{how:6s}]: before CONST {ok_pre}/{len(pre)} ({100 * ok_pre / len(pre):.0f} %) · "
          f"T_L NAME {ok_tl}/{len(tl)} ({100 * ok_tl / len(tl):.0f} %)")
