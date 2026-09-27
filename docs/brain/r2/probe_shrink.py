"""probe_shrink.py — the shrinkage chosen by a DECLARED rule on the TEACH rows only, then T_L read once (edit: Fable 5.1 (brain r2), 2026-09-27 20:02 +0400).
F16 fixed S2 at ε = 1e-4 RELATIVE and read the state 4 pp above F_pool; F14's ABSOLUTE 1e-4 (≈ a relative 0.2 on F_pool) read F_pool
at 80 %. So the shrinkage level moves the state-vs-input verdict, and a fixed ε chosen after seeing T_L is #158's trap. Here, for each
input (F_pool; A1's NAME-ask state, raw prep) and each seed: the streaming LDA of F16 (WITHIN-letter covariance by Welford's cross
term, one pass in tape order) at ε ∈ {1e-4, 1e-3, 1e-2, 3e-2, 1e-1, 3e-1} relative (ε · trace Σ / d); ε is CHOSEN by
leave-one-TEACH-font-out accuracy over the 4 TEACH fonts (fit on 3 fonts' TEACH rows, score the 4th's) — TEACH rows only, never a
sitting — and T_L is then read ONCE at the chosen ε. Every ε's T_L is printed too, as a descriptive grid, never for the choice.
Run:  OPENBLAS_NUM_THREADS=1 PYTHONPATH=/data/dev/genome-wt-b1-tape2 nice -n 19 /data/dev/venvs/brain/bin/python -u probe_shrink.py
"""
import json
from collections import defaultdict

import numpy as np
import torch

from brain.arms.soft.arm import ArmA1

torch.set_num_threads(1)
ROOT = "/data/dev/brain-runs/b1.1"
EPS = (1e-4, 1e-3, 1e-2, 3e-2, 1e-1, 3e-1)


def slda_fit(X, y, eps):
    d = X.shape[1]; names = []; mu = {}; cnt = {}; S = np.zeros((d, d)); nS = 0
    for x, k in zip(X, y):
        if k not in names:
            names.append(k); mu[k] = x.copy(); cnt[k] = 1; continue
        cnt[k] += 1; dz = x - mu[k]; mu[k] += dz / cnt[k]; S += np.outer(dz, x - mu[k]); nS += 1
    Sig = S / max(nS, 1)
    L = np.linalg.inv((1 - eps) * Sig + eps * (np.trace(Sig) / d) * np.eye(d))
    M = np.stack([mu[k] for k in names]); W = M @ L; c = -0.5 * np.einsum("ij,ij->i", W, M)
    return lambda Z: [names[i] for i in (Z @ W.T + c).argmax(1)]


def acc(pred, y):
    return sum(1 for p, t in zip(pred, y) if p == t) / len(y)


for seed in ("20261001", "20261002"):
    rows = [json.loads(l) for l in open(f"{ROOT}/{seed}/tape.jsonl") if l.strip()]
    truth_ask, font_of = {}, {}
    for l in open(f"{ROOT}/{seed}/truth.jsonl"):
        t = json.loads(l)
        if t.get("type") == "ask": truth_ask[t["seq"]] = t
        elif t.get("type") == "rendering": font_of[int(t["cache_row"])] = t["font"]
    teach = [r for r in rows if r["kind"] == "TEACH" and len(r["payload"]["name"]) == 1]
    tl = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["phase"] == "T_L"]
    s = json.load(open(f"{ROOT}/runs/{seed}/A1/summary.json"))
    cfg = {k: v for k, v in s["config"].items() if k in ("variant", "teach_trains_answer", "fixed_h")}
    cfg.update({"cache_dir": f"{ROOT}/cache/{seed}", "seed": int(seed)})
    arm = ArmA1(seed=int(seed), config=cfg); arm.load(f"{ROOT}/runs/{seed}/A1/snapshot/final")
    enc, h0, act, cache = arm.encoder, arm.h.detach().clone(), arm.engine.active, arm.cache

    def state(rid):
        with torch.no_grad():
            h = h0
            for x in enc.ask_steps({"answer_kind": "NAME", "candidate_rows": None, "cues": ["NAME"], "operands": [{"kind": "row", "value": int(rid)}]}):
                h = arm.engine.step(x, h)
            return h[:act].numpy().astype(np.float64)

    def fpool(rid):
        v = np.asarray(cache.glances(int(rid)), dtype=np.float64).mean(0); return v / (np.linalg.norm(v) + 1e-12)

    rid_t = [r["payload"]["glance_row"] for r in teach]; yt = [r["payload"]["name"] for r in teach]
    fonts = [font_of[int(r)] for r in rid_t]; font_set = sorted(set(fonts))
    rid_l = [r["payload"]["operands"][0]["value"] for r in tl]; yl = [truth_ask[r["seq"]]["answer"] for r in tl]
    print(f"=== seed {seed} · TEACH {len(teach)} rows in {len(font_set)} fonts {font_set} · T_L NAME {len(tl)} · A1 state {act} units ===")
    for label, f in (("F_pool", fpool), ("A1-state", state)):
        Xt = np.stack([f(r) for r in rid_t]); Xl = np.stack([f(r) for r in rid_l])
        cv = {}; tl_at = {}
        for eps in EPS:
            folds = []
            for held in font_set:
                tr = [i for i, ft in enumerate(fonts) if ft != held]; te = [i for i, ft in enumerate(fonts) if ft == held]
                pred = slda_fit(Xt[tr], [yt[i] for i in tr], eps)
                folds.append(acc(pred(Xt[te]), [yt[i] for i in te]))
            cv[eps] = float(np.mean(folds))
            tl_at[eps] = acc(slda_fit(Xt, yt, eps)(Xl), yl)
        best = max(EPS, key=lambda e: cv[e])
        grid = " · ".join(f"ε {e:g}: cv {100 * cv[e]:.0f} % / T_L {100 * tl_at[e]:.0f} %" for e in EPS)
        print(f"  {label:9s}: {grid}")
        print(f"  {label:9s}: CHOSEN by leave-one-TEACH-font-out ε = {best:g} (cv {100 * cv[best]:.0f} %) → T_L read once: {100 * tl_at[best]:.0f} % ({int(round(tl_at[best] * len(yl)))}/{len(yl)})")
