"""Does the network's STATE keep the letters the INPUT carries? — B1 r2 evidence F11/F12 (Claude (Opus 5.5), 2026-09-27 18:40 +0400).
For one seed, and each named soft arm's FINAL snapshot (B1.0 records), every single-letter TEACH row's glance is run through
the arm's own NAME-ask road (`StepEncoder.ask_steps`: the NAME cue, then the 5 glance steps) from ONE fixed start state (the
snapshot's own h), with no learning, giving h_after. Four readers, all trained on the TEACH rows and scored on (a) the NAME
training asks before the first CONST ask and (b) T_L's NAME asks (unseen fonts):
  input-NCM   nearest class mean (cosine) on the mean glance            (F1's reader, the input's own separability)
  input-LR    multinomial logistic regression, full batch, 2,000 steps (what a well-trained linear head COULD read from the input)
  state-NCM   nearest class mean (cosine) on h_after[:active]            (does the state keep the letters?)
  state-LR    logistic regression on h_after[:active], same recipe       (is the letter linearly decodable from the state?)
  arm-head    the arm's OWN NAME head on h_after                         (what the arm answers from this start state)
Run with a b1 tree on PYTHONPATH (SOLUTIONS #242), under the brain venv:
  PYTHONPATH=/data/dev/genome-wt-b1int python docs/brain/r2/probe_state.py /data/dev/brain-runs/b1 20261001 A1 A1-BPTT-AWAKE A1-TEACH
"""
import json
import sys

import numpy as np
import torch
import torch.nn.functional as F

from brain.arms.soft.arm import ArmA1
from brain.glance_cache import Cache

torch.manual_seed(0)
root, seed, arms = sys.argv[1], sys.argv[2], sys.argv[3:] or ["A1"]
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
names = sorted({r["payload"]["name"] for r in teach})
y_teach = np.array([names.index(r["payload"]["name"]) for r in teach])
y_pre = np.array([names.index(fb[r["seq"]]) if fb[r["seq"]] in names else -1 for r in pre])
y_tl = np.array([names.index(truth[r["seq"]]["answer"]) if truth.get(r["seq"], {}).get("answer") in names else -1 for r in tl])


def ncm(Xtr, ytr, X):
    C = np.stack([Xtr[ytr == k].mean(0) for k in range(len(names))])
    C /= np.linalg.norm(C, axis=1, keepdims=True) + 1e-12
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12) @ C.T).argmax(1)


def lr(Xtr, ytr, X, steps=2000):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    A = torch.tensor((Xtr - mu) / sd, dtype=torch.float32)
    W = torch.zeros(A.shape[1], len(names), requires_grad=True)
    b = torch.zeros(len(names), requires_grad=True)
    opt = torch.optim.Adam([W, b], lr=0.05)
    yt = torch.tensor(ytr)
    for _ in range(steps):
        opt.zero_grad()
        (F.cross_entropy(A @ W + b, yt) + 1e-3 * W.pow(2).sum()).backward()
        opt.step()
    with torch.no_grad():
        return (torch.tensor((X - mu) / sd, dtype=torch.float32) @ W + b).argmax(1).numpy()


def score(p, y):
    return f"{int((p == y).sum())}/{len(y)} ({100 * (p == y).mean():.0f} %)"


gl = lambda rid: np.asarray(cache.glances(int(rid)), dtype=np.float64).mean(0)
Xi_t = np.stack([gl(r["payload"]["glance_row"]) for r in teach])
Xi_p = np.stack([gl(r["payload"]["operands"][0]["value"]) for r in pre])
Xi_l = np.stack([gl(r["payload"]["operands"][0]["value"]) for r in tl])
print(f"seed {seed} · TEACH {len(teach)} · before-CONST asks {len(pre)} · T_L NAME asks {len(tl)} · chance {100 / 26:.1f} %")
print(f"  input-NCM : before CONST {score(ncm(Xi_t, y_teach, Xi_p), y_pre)} · T_L {score(ncm(Xi_t, y_teach, Xi_l), y_tl)}")
print(f"  input-LR  : before CONST {score(lr(Xi_t, y_teach, Xi_p), y_pre)} · T_L {score(lr(Xi_t, y_teach, Xi_l), y_tl)}")
for arm_name in arms:
    s = json.load(open(f"{root}/runs/{seed}/{arm_name}/summary.json"))
    cfg = {k: v for k, v in s["config"].items() if k in ("variant", "teach_trains_answer", "fixed_h", "match_params", "match_n_names")}
    cfg.update({"cache_dir": f"{root}/cache/{seed}", "seed": int(seed)})
    arm = ArmA1(seed=int(seed), config=cfg)
    arm.load(f"{root}/runs/{seed}/{arm_name}/snapshot/final")
    if arm.attention_mode:
        print(f"  {arm_name}: attention variant — skipped (its head reads a readout, not h alone)")
        continue
    enc, h0, act = arm.encoder, arm.h.detach().clone(), arm.engine.active

    def state(rid):
        with torch.no_grad():
            h = h0
            for x in enc.ask_steps({"answer_kind": "NAME", "candidate_rows": None, "cues": ["NAME"], "operands": [{"kind": "row", "value": int(rid)}]}):
                h = arm.engine.step(x, h)
            return h[:act].numpy().astype(np.float64), arm.names(h, active_h=act)

    def states(rs, key):
        out, heads = [], []
        for r in rs:
            rid = r["payload"]["glance_row"] if key == "teach" else r["payload"]["operands"][0]["value"]
            hv, lg = state(rid)
            out.append(hv)
            heads.append(arm.names.names[int(lg.argmax())] if lg.numel() else None)
        return np.stack(out), heads

    Xs_t, _ = states(teach, "teach")
    Xs_p, head_p = states(pre, "ask")
    Xs_l, head_l = states(tl, "ask")
    hp = np.array([names.index(v) if v in names else -1 for v in head_p])
    hl = np.array([names.index(v) if v in names else -1 for v in head_l])
    spread = np.linalg.norm(Xs_t - Xs_t.mean(0), axis=1).mean()
    print(f"  {arm_name:14s} (h {act} units; mean distance of a state from the mean state {spread:.3f}; |h| mean {np.abs(Xs_t).mean():.3f})")
    print(f"    state-NCM : before CONST {score(ncm(Xs_t, y_teach, Xs_p), y_pre)} · T_L {score(ncm(Xs_t, y_teach, Xs_l), y_tl)}")
    print(f"    state-LR  : before CONST {score(lr(Xs_t, y_teach, Xs_p), y_pre)} · T_L {score(lr(Xs_t, y_teach, Xs_l), y_tl)}")
    print(f"    arm-head  : before CONST {score(hp, y_pre)} · T_L {score(hl, y_tl)} · distinct answers {len(set(head_l))}")
