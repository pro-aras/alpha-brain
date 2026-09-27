"""B1.2's pre-flight (SEAT-DECISIONS R49): the per-case U1a ceilings and the declared-ε offline readings, on B1.1's own tapes and
B1.1's A1 final state (edit: Claude (Opus 5.5), 2026-09-27 20:28 +0400). Per case (latin-upper / latin-lower), over T_L's U1a asks (every
(letter, test font), one rendering each): (i) the CEILING = a standardised full-batch logistic regression trained on the TEACH rows
(2,000 Adam steps), on F_pool and on A1's NAME-ask state; (ii) the offline one-pass streaming LDA (within-letter covariance, relative
shrinkage) at the ε R49 declares — F_pool 0.1 / 0.3, A1's state 0.01 / 0.03 (seeds 1 / 2; the TEACH-only rule of probe_shrink).
  PYTHONPATH=/data/dev/genome-wt-b1-tape2 python -u docs/brain/b1/b12/probe_ceilings.py /data/dev/brain-runs/b1.1 20261001
"""
import json
import sys

import numpy as np
import torch
import torch.nn.functional as F

from brain.arms.soft.arm import ArmA1
from brain.glance_cache import Cache

torch.manual_seed(0)
root, seed = sys.argv[1], sys.argv[2]
EPS = {"20261001": {"F_pool": 0.1, "state": 0.01}, "20261002": {"F_pool": 0.3, "state": 0.03}}[seed]
cache = Cache(f"{root}/cache/{seed}")
rows = [json.loads(l) for l in open(f"{root}/{seed}/tape.jsonl")]
truth = {}
for l in open(f"{root}/{seed}/truth.jsonl"):
    t = json.loads(l)
    truth[t.get("seq", t.get("ask_seq"))] = t
teach = [r for r in rows if r["kind"] == "TEACH" and len(r["payload"]["name"]) == 1]
u1a = [r for r in rows if r["kind"] == "ASK" and r["phase"] == "T_L" and r["item"].startswith("NAME:") and r["payload"]["cues"] == ["NAME"]]
case_of = {r["seq"]: truth[r["seq"]].get("class") for r in u1a}
yt = [r["payload"]["name"] for r in teach]
yu = [truth[r["seq"]]["answer"] for r in u1a]
names = sorted(set(yt))


def fpool(rid):
    g = np.asarray(cache.glances(int(rid)), dtype=np.float64).mean(0)
    return g / (np.linalg.norm(g) + 1e-12)


arm = ArmA1(seed=int(seed), config={"variant": "A1", "cache_dir": f"{root}/cache/{seed}", "seed": int(seed)})
arm.load(f"{root}/runs/{seed}/A1/snapshot/final")
enc, h0, act = arm.encoder, arm.h.detach().clone(), arm.engine.active


def state(rid):
    with torch.no_grad():
        h = h0
        for x in enc.ask_steps({"answer_kind": "NAME", "candidate_rows": None, "cues": ["NAME"], "operands": [{"kind": "row", "value": int(rid)}]}):
            h = arm.engine.step(x, h)
        return h[:act].numpy().astype(np.float64)


def lr(Xtr, X):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    A = torch.tensor((Xtr - mu) / sd, dtype=torch.float32)
    y = torch.tensor([names.index(v) for v in yt])
    W = torch.zeros(A.shape[1], len(names), requires_grad=True); b = torch.zeros(len(names), requires_grad=True)
    opt = torch.optim.Adam([W, b], lr=0.05)
    for _ in range(2000):
        opt.zero_grad(); (F.cross_entropy(A @ W + b, y) + 1e-3 * W.pow(2).sum()).backward(); opt.step()
    with torch.no_grad():
        return [names[i] for i in (torch.tensor((X - mu) / sd, dtype=torch.float32) @ W + b).argmax(1).numpy()]


def slda(Xt, X, eps):
    d = Xt.shape[1]; mu, cnt, order = {}, {}, []
    S, n = np.zeros((d, d)), 0
    for x, y in zip(Xt, yt):
        if y not in mu:
            mu[y] = x.copy(); cnt[y] = 1; order.append(y); continue
        cnt[y] += 1; dx = x - mu[y]; mu[y] += dx / cnt[y]; S += np.outer(dx, x - mu[y]); n += 1
    Sig = S / max(n - 1, 1)
    L = np.linalg.inv((1 - eps) * Sig + eps * (np.trace(Sig) / d) * np.eye(d))
    M = np.stack([mu[k] for k in order]); W = M @ L; c = -0.5 * np.einsum("ij,ij->i", W, M)
    return [order[i] for i in (X @ W.T + c).argmax(1)]


def per_case(pred):
    out = {}
    for case in ("latin-upper", "latin-lower"):
        idx = [i for i, r in enumerate(u1a) if case_of[r["seq"]] == case]
        ok = sum(pred[i] == yu[i] for i in idx)
        out[case] = f"{ok}/{len(idx)} ({ok / len(idx):.3f})"
    return out


Xi_t = np.stack([fpool(r["payload"]["glance_row"]) for r in teach]); Xi_u = np.stack([fpool(r["payload"]["operands"][0]["value"]) for r in u1a])
Xs_t = np.stack([state(r["payload"]["glance_row"]) for r in teach]); Xs_u = np.stack([state(r["payload"]["operands"][0]["value"]) for r in u1a])
print(f"seed {seed} · U1a asks {len(u1a)} · bars: latin-lower 0.778, latin-upper 0.669 (bars.json)")
print(f"  CEILING F_pool (standardised LR, full batch) : {per_case(lr(Xi_t, Xi_u))}")
print(f"  CEILING A1 state ({act} units)               : {per_case(lr(Xs_t, Xs_u))}")
print(f"  one-pass SLDA F_pool at ε {EPS['F_pool']:g}            : {per_case(slda(Xi_t, Xi_u, EPS['F_pool']))}")
print(f"  one-pass SLDA A1 state at ε {EPS['state']:g}         : {per_case(slda(Xs_t, Xs_u, EPS['state']))}")
