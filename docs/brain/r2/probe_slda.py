"""Streaming LDA in ONE pass — on A1's state and on the organ's own features — B1 r2 evidence F14 (Claude (Opus 5.5, the seat),
2026-09-27 19:33 +0400), to calibrate the debate's P3/P4 (Fable's «THE READER») before any arm is built.
The reader (Hayes & Kanan 2020, arXiv 1909.01520, §3 as quoted in RESEARCH-FABLE.md): one running mean per name, one shared
covariance updated online over the class-centred showings, the precision Λ = [(1 − ε)Σ + εI]⁻¹ (ε = 1e-4) solved ONCE after
the pass (the live arm solves it at every sleep), the answer argmax_k (Λμ_k)·x − ½ μ_kᵀΛμ_k. It sees the 624 single-letter
TEACH rows once, in tape order. Inputs: A1's NAME-ask state (final snapshot, one fixed start state, as probe_state.py) and
F_pool — the unit-normalised mean of the 5 glances (no network). Scored on the NAME training asks before the first CONST ask and
on T_L's NAME asks. Run with a b1 tree on PYTHONPATH (SOLUTIONS #242):
  PYTHONPATH=/data/dev/genome-wt-b1-tape2 python -u docs/brain/r2/probe_slda.py /data/dev/brain-runs/b1 20261001
"""
import json
import sys

import numpy as np
import torch

from brain.arms.soft.arm import ArmA1
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
first_const = min(r["seq"] for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["CONST"])
pre = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["seq"] < first_const and r["seq"] in fb]
tl = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["phase"] == "T_L"]
yt = [r["payload"]["name"] for r in teach]
yp = [fb[r["seq"]] for r in pre]
yl = [truth.get(r["seq"], {}).get("answer") for r in tl]


def slda(Xt, X_eval, eps=1e-4):
    d = Xt.shape[1]
    names, mu, cnt = [], {}, {}
    S, n = np.zeros((d, d)), 0
    for x, y in zip(Xt, yt):
        if y not in mu:
            names.append(y); mu[y] = x.copy(); cnt[y] = 1       # a new name = its first showing
        else:
            dx = x - mu[y]
            cnt[y] += 1
            mu[y] += dx / cnt[y]
            S += np.outer(dx, x - mu[y]); n += 1               # the shared, class-centred scatter (Welford across classes)
    Sigma = S / max(n, 1)
    L = np.linalg.inv((1 - eps) * Sigma + eps * np.eye(d))
    M = np.stack([mu[k] for k in names])
    W = M @ L
    c = -0.5 * np.einsum("ij,ij->i", W, M)
    return [[names[i] for i in (X @ W.T + c).argmax(1)] for X in X_eval]


def score(p, y):
    ok = sum(a == b for a, b in zip(p, y))
    return f"{ok}/{len(y)} ({100 * ok / len(y):.0f} %)"


def fpool(rid):
    g = np.asarray(cache.glances(int(rid)), dtype=np.float64).mean(0)
    return g / (np.linalg.norm(g) + 1e-12)


Xt = np.stack([fpool(r["payload"]["glance_row"]) for r in teach])
Xp = np.stack([fpool(r["payload"]["operands"][0]["value"]) for r in pre])
Xl = np.stack([fpool(r["payload"]["operands"][0]["value"]) for r in tl])
pp, pl = slda(Xt, [Xp, Xl])
print(f"seed {seed} · one pass over {len(teach)} TEACH rows · chance 3.8 %")
print(f"  IN-SLDA (F_pool, 144 dims, no network): before CONST {score(pp, yp)} · T_L {score(pl, yl)} · distinct {len(set(pl))}")

s = json.load(open(f"{root}/runs/{seed}/A1/summary.json"))
arm = ArmA1(seed=int(seed), config={"variant": "A1", "cache_dir": f"{root}/cache/{seed}", "seed": int(seed)})
arm.load(f"{root}/runs/{seed}/A1/snapshot/final")
enc, h0, act = arm.encoder, arm.h.detach().clone(), arm.engine.active


def state(rid):
    with torch.no_grad():
        h = h0
        for x in enc.ask_steps({"answer_kind": "NAME", "candidate_rows": None, "cues": ["NAME"], "operands": [{"kind": "row", "value": int(rid)}]}):
            h = arm.engine.step(x, h)
        return h[:act].numpy().astype(np.float64)


St = np.stack([state(r["payload"]["glance_row"]) for r in teach])
Sp = np.stack([state(r["payload"]["operands"][0]["value"]) for r in pre])
Sl = np.stack([state(r["payload"]["operands"][0]["value"]) for r in tl])
pp, pl = slda(St, [Sp, Sl])
print(f"  A1-SLDA (A1's state, {act} units):        before CONST {score(pp, yp)} · T_L {score(pl, yl)} · distinct {len(set(pl))}")
