"""Open point 2 settled by a grid — does the trunk cost naming for a streaming-LDA reader? (Claude (Opus 5.5, the seat), 2026-09-27 19:55 +0400)
F14 (the seat's probe_slda.py) read IN-SLDA 80 % / A1-SLDA 61–63 % on unseen fonts; Fable's probe_review.py read the INPUT 64–66 % /
the STATE 67–68 %. Both are one pass over the 624 TEACH rows in tape order; they differ in the reader:
  the seat's:  the WITHIN-class covariance (Welford over x − μ_y), on the RAW vectors, shrinkage ε = 1e-4 absolute;
  Fable's:     the TOTAL scatter Σ z zᵀ (z centred by the GLOBAL running mean, not the class mean), on vectors standardised by the
               running statistics AT THEIR OWN TIME (the class means hold early z's under immature statistics), ε = 1e-4.
Hayes & Kanan 2020 (arXiv 1909.01520, §3) define the shared covariance over deviations from the CLASS mean. This grid runs, on B1.1's
own tapes and B1.1's A1 final state (the B1.2 tape), both seeds, T_L's NAME asks (unseen fonts) and the 156 L4 NAME training asks:
  cov ∈ {within, total}  ×  prep ∈ {raw, std-final (standardised once by the pass's FINAL statistics), std-running (Fable's)}  ×
  input ∈ {F_pool, A1-state};  ε RELATIVE: ε · trace(Σ)/d (so the shrinkage means the same at every scale), ε = 1e-4.
The row «total · std-running» must reproduce Fable's numbers (the control that the grid reads the same record).
  PYTHONPATH=/data/dev/genome-wt-b1-tape2 python -u docs/brain/r2/probe_slda_grid.py /data/dev/brain-runs/b1.1 20261001
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
train = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["phase"] == "L4" and r["seq"] in fb]
tl = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["phase"] == "T_L"]
yt = [r["payload"]["name"] for r in teach]
ya = [fb[r["seq"]] for r in train]
yl = [truth.get(r["seq"], {}).get("answer") for r in tl]


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


def slda(Xt, evals, cov, prep, eps=1e-4):
    d = Xt.shape[1]
    n, m, s2 = 0, np.zeros(d), np.zeros(d)                     # running global statistics (Welford)
    fin_m, fin_sd = Xt.mean(0), Xt.std(0) + 1e-6               # the pass's FINAL statistics (std-final)
    names, mu, cnt = [], {}, {}
    S, nS = np.zeros((d, d)), 0
    for x, y in zip(Xt, yt):
        n += 1; dx = x - m; m += dx / n; s2 += dx * (x - m)
        sd = np.sqrt(s2 / max(n - 1, 1)) + 1e-6
        z = x if prep == "raw" else ((x - fin_m) / fin_sd if prep == "std-final" else (x - m) / sd)
        if y not in mu:
            names.append(y); mu[y] = z.copy(); cnt[y] = 1
            if cov == "total":
                S += np.outer(z, z); nS += 1
            continue
        cnt[y] += 1
        if cov == "within":
            dz = z - mu[y]; mu[y] += dz / cnt[y]; S += np.outer(dz, z - mu[y]); nS += 1
        else:
            mu[y] += (z - mu[y]) / cnt[y]; S += np.outer(z, z); nS += 1
    Sig = S / max(nS - 1, 1)
    L = np.linalg.inv((1 - eps) * Sig + eps * (np.trace(Sig) / d) * np.eye(d))
    M = np.stack([mu[k] for k in names]); W = M @ L; c = -0.5 * np.einsum("ij,ij->i", W, M)
    out = []
    for X in evals:
        Z = X if prep == "raw" else ((X - fin_m) / fin_sd if prep == "std-final" else (X - m) / (np.sqrt(s2 / max(n - 1, 1)) + 1e-6))
        out.append([names[i] for i in (Z @ W.T + c).argmax(1)])
    return out


def pct(p, y):
    ok = sum(a == b for a, b in zip(p, y)); return f"{ok}/{len(y)} ({100 * ok / len(y):.0f} %)"


inputs = {"F_pool": (np.stack([fpool(r["payload"]["glance_row"]) for r in teach]), np.stack([fpool(r["payload"]["operands"][0]["value"]) for r in train]), np.stack([fpool(r["payload"]["operands"][0]["value"]) for r in tl])),
          f"A1-state({act})": (np.stack([state(r["payload"]["glance_row"]) for r in teach]), np.stack([state(r["payload"]["operands"][0]["value"]) for r in train]), np.stack([state(r["payload"]["operands"][0]["value"]) for r in tl]))}
print(f"=== seed {seed} (B1.1 tape, B1.1 A1) · one pass over {len(teach)} TEACH rows · L4 NAME asks {len(train)} · T_L NAME asks {len(tl)}")
for name, (Xt, Xa, Xl) in inputs.items():
    for cov in ("within", "total"):
        for prep in ("raw", "std-final", "std-running"):
            pa, pl = slda(Xt, [Xa, Xl], cov, prep)
            print(f"  {name:15s} cov={cov:6s} prep={prep:11s}: L4 NAME {pct(pa, ya)} · T_L {pct(pl, yl)}")
