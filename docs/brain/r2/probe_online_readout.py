"""Can an ONLINE readout learn the letters from A1's own states in ONE pass of the TEACH rows? — B1 r2 evidence F13
(Claude (Opus 5.5, the seat), 2026-09-27 18:56 +0400). The states are A1's (final B1.0 snapshot, one fixed start state, the NAME-ask road
per glance, no learning — exactly as probe_state.py). Four online readers see the single-letter TEACH rows ONCE, in TAPE
ORDER (24 showings per letter: what the tape gives), each row one labelled example; a new name joins at its first showing:
  sgd-raw   A1's own recipe: a linear head, a new name's row starts at ZERO, one cross-entropy SGD step (lr 0.01) per example, RAW h
  sgd-std   the same, on h standardised by the running mean / std of the states seen so far (Welford)
  rls       recursive least squares on the running-centred h, one-hot targets (P0 = I / 0.01, no forgetting)
  proto     running class means of the running-standardised h; answer = the nearest mean (cosine)
Scored on the NAME training asks before the first CONST ask and on T_L's NAME asks (unseen fonts); the offline ceilings are in
probe_state.out. Run with a b1 tree on PYTHONPATH (SOLUTIONS #242), under the brain venv:
  PYTHONPATH=/data/dev/genome-wt-b1-tape2 python -u docs/brain/r2/probe_online_readout.py /data/dev/brain-runs/b1 20261001 A1
"""
import json
import sys

import numpy as np
import torch

from brain.arms.soft.arm import ArmA1
from brain.glance_cache import Cache

root, seed, arm_name = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "A1")
rows = [json.loads(l) for l in open(f"{root}/{seed}/tape.jsonl")]
truth = {}
for l in open(f"{root}/{seed}/truth.jsonl"):
    t = json.loads(l)
    truth[t.get("seq", t.get("ask_seq"))] = t
teach = [r for r in rows if r["kind"] == "TEACH" and len(r["payload"]["name"]) == 1]          # tape order
fb = {r["payload"]["ask_seq"]: r["payload"]["right"] for r in rows if r["kind"] == "FEEDBACK"}
first_const = min(r["seq"] for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["CONST"])
pre = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["seq"] < first_const and r["seq"] in fb]
tl = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["phase"] == "T_L"]

s = json.load(open(f"{root}/runs/{seed}/{arm_name}/summary.json"))
cfg = {k: v for k, v in s["config"].items() if k in ("variant", "teach_trains_answer", "fixed_h")}
cfg.update({"cache_dir": f"{root}/cache/{seed}", "seed": int(seed)})
arm = ArmA1(seed=int(seed), config=cfg)
arm.load(f"{root}/runs/{seed}/{arm_name}/snapshot/final")
enc, h0, act = arm.encoder, arm.h.detach().clone(), arm.engine.active


def state(rid):
    with torch.no_grad():
        h = h0
        for x in enc.ask_steps({"answer_kind": "NAME", "candidate_rows": None, "cues": ["NAME"], "operands": [{"kind": "row", "value": int(rid)}]}):
            h = arm.engine.step(x, h)
        return h[:act].numpy().astype(np.float64)


Xt = np.stack([state(r["payload"]["glance_row"]) for r in teach])
yt = [r["payload"]["name"] for r in teach]
Xp = np.stack([state(r["payload"]["operands"][0]["value"]) for r in pre])
yp = [fb[r["seq"]] for r in pre]
Xl = np.stack([state(r["payload"]["operands"][0]["value"]) for r in tl])
yl = [truth.get(r["seq"], {}).get("answer") for r in tl]
H = Xt.shape[1]


class Stats:                                      # Welford running mean / variance
    def __init__(self):
        self.n, self.m, self.s = 0, np.zeros(H), np.zeros(H)

    def add(self, x):
        self.n += 1
        d = x - self.m
        self.m += d / self.n
        self.s += d * (x - self.m)

    def std(self):
        return np.sqrt(self.s / max(self.n - 1, 1)) + 1e-6


def run(kind):
    names, st = [], Stats()
    W = np.zeros((0, H)); b = np.zeros(0)
    P = np.eye(H) / 0.01; Wr = np.zeros((H, 0))
    sums, counts = {}, {}
    for x, y in zip(Xt, yt):
        st.add(x)
        if y not in names:
            names.append(y)
            W = np.vstack([W, np.zeros(H)]); b = np.append(b, 0.0); Wr = np.hstack([Wr, np.zeros((H, 1))])
        k = names.index(y)
        if kind in ("sgd-raw", "sgd-std"):
            v = x if kind == "sgd-raw" else (x - st.m) / st.std()
            z = W @ v + b
            p = np.exp(z - z.max()); p /= p.sum()
            g = p.copy(); g[k] -= 1.0
            W -= 0.01 * np.outer(g, v); b -= 0.01 * g
        elif kind == "rls":
            v = x - st.m
            Pv = P @ v
            gain = Pv / (1.0 + v @ Pv)
            target = np.zeros(len(names)); target[k] = 1.0
            err = target - v @ Wr
            Wr += np.outer(gain, err)
            P -= np.outer(gain, Pv)
        elif kind == "proto":
            v = (x - st.m) / st.std()
            sums[y] = sums.get(y, 0) + v; counts[y] = counts.get(y, 0) + 1

    def predict(X):
        if kind in ("sgd-raw", "sgd-std"):
            V = X if kind == "sgd-raw" else (X - st.m) / st.std()
            return [names[i] for i in (V @ W.T + b).argmax(1)]
        if kind == "rls":
            return [names[i] for i in ((X - st.m) @ Wr).argmax(1)]
        C = np.stack([sums[n] / counts[n] for n in names]); C /= np.linalg.norm(C, axis=1, keepdims=True)
        V = (X - st.m) / st.std(); V /= np.linalg.norm(V, axis=1, keepdims=True)
        return [names[i] for i in (V @ C.T).argmax(1)]

    pp, pl = predict(Xp), predict(Xl)
    ok_p = sum(a == c for a, c in zip(pp, yp)); ok_l = sum(a == c for a, c in zip(pl, yl))
    return ok_p, ok_l, len(set(pl))


print(f"seed {seed} · {arm_name} states (h {H}) · one pass over {len(teach)} TEACH rows in tape order · chance 3.8 %")
for kind in ("sgd-raw", "sgd-std", "rls", "proto"):
    ok_p, ok_l, nd = run(kind)
    print(f"  {kind:8s}: before CONST {ok_p}/{len(pre)} ({100 * ok_p / len(pre):.0f} %) · T_L {ok_l}/{len(tl)} ({100 * ok_l / len(tl):.0f} %) · distinct T_L answers {nd}")
