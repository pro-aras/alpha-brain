"""probe_world_head.py — three cheap measurements on A1's FINAL B1.1 snapshot (edit: Fable 5.1 (brain r2), 2026-09-27 19:08 +0400).
(a) The WORLD head's LETTER sub-head as a namer: on every TEACH row `_advance_steps` trains it toward the name's first letter
    (next-step prediction after the 5th glance, 745 rows, the same raw-h SGD recipe as the NAME head). Read after the 5 TEACH
    glances from one fixed start state (F11's road), scored on the TEACH rows, the NAME training asks and T_L's NAME asks.
    If it collapses like the NAME head, the conditioning reading holds independently of the FEEDBACK road.
(b) The NAME head on the ask road for the same snapshot (F11 was B1.0), plus a standardised offline linear reader of the state.
(c) The recurrent weights: engine.py `_init_rows(0, h0, gen, from_active=0)` never randomises the first h0 units' W_hh rows
    (the `if from_active > 0` guard), so W_hh starts at ZERO — read ||W_hh|| against ||W_ih|| per gate in the final snapshot,
    split into the initial block (rows < 64) and the born units (rows >= 64).
(d) The cost of a prototype / LDA reader per event at d = 144 (the input) and d = the state width, timed here, one thread.
Run:  OPENBLAS_NUM_THREADS=1 PYTHONPATH=/data/dev/genome-wt-b1-tape2 nice -n 19 /data/dev/venvs/brain/bin/python -u \
        probe_world_head.py /data/dev/brain-runs/b1.1 20261001 A1
"""
import json
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

from brain.arms.soft.arm import ArmA1
from brain.arms.soft.steps import LETTERS
from brain.glance_cache import Cache

torch.manual_seed(0)
torch.set_num_threads(1)
root, seed, arm_name = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "A1")
rows = [json.loads(l) for l in open(f"{root}/{seed}/tape.jsonl")]
truth = {}
for l in open(f"{root}/{seed}/truth.jsonl"):
    t = json.loads(l)
    if t.get("type") == "ask":
        truth[t["seq"]] = t
teach = [r for r in rows if r["kind"] == "TEACH" and len(r["payload"]["name"]) == 1]
fb = {r["payload"]["ask_seq"]: r["payload"]["right"] for r in rows if r["kind"] == "FEEDBACK"}
train = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["phase"] == "L4" and r["seq"] in fb]
tl = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["phase"] == "T_L"]
names = sorted({r["payload"]["name"] for r in teach})

s = json.load(open(f"{root}/runs/{seed}/{arm_name}/summary.json"))
cfg = {k: v for k, v in s["config"].items() if k in ("variant", "teach_trains_answer", "fixed_h")}
cfg.update({"cache_dir": f"{root}/cache/{seed}", "seed": int(seed)})
arm = ArmA1(seed=int(seed), config=cfg)
arm.load(f"{root}/runs/{seed}/{arm_name}/snapshot/final")
enc, h0, act = arm.encoder, arm.h.detach().clone(), arm.engine.active
print(f"seed {seed} · {arm_name} final snapshot · h {act} units · names heard {len(arm.names.names)} · TEACH {len(teach)} · NAME train asks {len(train)} · T_L NAME {len(tl)}")


def world_letter(rid):
    """the WORLD head's letter prediction after the 5 TEACH glances (what `_advance_steps` trains toward the name)"""
    with torch.no_grad():
        h = h0
        for x in enc.glance_steps(int(rid), "TEACH"):
            h = arm.engine.step(x, h)
        lg = arm.world(h, active_h=act)["letter"]
        i = int(lg.argmax())
        return (LETTERS[i] if i < len(LETTERS) else "<END>"), h[:act].numpy().astype(np.float64)


def name_head(rid):
    with torch.no_grad():
        h = h0
        for x in enc.ask_steps({"answer_kind": "NAME", "candidate_rows": None, "cues": ["NAME"], "operands": [{"kind": "row", "value": int(rid)}]}):
            h = arm.engine.step(x, h)
        lg = arm.names(h, active_h=act)
        return arm.names.names[int(lg.argmax())], h[:act].numpy().astype(np.float64)


def score(pairs):
    n = len(pairs)
    ok = sum(1 for p, y in pairs if p == y)
    distinct = len({p for p, _ in pairs})
    return f"{ok}/{n} ({100 * ok / n:.0f} %) · distinct answers {distinct}"


# (a) the world's letter head
wt = [(world_letter(r["payload"]["glance_row"])[0], r["payload"]["name"]) for r in teach]
wp = [(world_letter(r["payload"]["operands"][0]["value"])[0], fb[r["seq"]]) for r in train]
wl = [(world_letter(r["payload"]["operands"][0]["value"])[0], truth[r["seq"]]["answer"]) for r in tl]
print(f"(a) WORLD letter head after 5 TEACH glances: TEACH rows {score(wt)} · NAME train asks {score(wp)} · T_L {score(wl)}")
# (b) the NAME head on the ask road, and offline linear readers of the state
np_ = [(name_head(r["payload"]["operands"][0]["value"])[0], fb[r["seq"]]) for r in train]
nl = [(name_head(r["payload"]["operands"][0]["value"])[0], truth[r["seq"]]["answer"]) for r in tl]
print(f"(b) NAME head on the ask road: NAME train asks {score(np_)} · T_L {score(nl)}")
Xt = np.stack([name_head(r["payload"]["glance_row"])[1] for r in teach]); yt = np.array([names.index(r["payload"]["name"]) for r in teach])
Xp = np.stack([name_head(r["payload"]["operands"][0]["value"])[1] for r in train]); yp = np.array([names.index(fb[r["seq"]]) for r in train])
Xl = np.stack([name_head(r["payload"]["operands"][0]["value"])[1] for r in tl]); yl = np.array([names.index(truth[r["seq"]]["answer"]) if truth[r["seq"]]["answer"] in names else -1 for r in tl])
spread = np.linalg.norm(Xt - Xt.mean(0), axis=1).mean()
print(f"    states on the ask road: mean distance from the mean state {spread:.3f} · |h| mean {np.abs(Xt).mean():.3f} · mean-state norm {np.linalg.norm(Xt.mean(0)):.3f}")


def lr(Xtr, ytr, X, steps=2000):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    A = torch.tensor((Xtr - mu) / sd, dtype=torch.float32)
    W = torch.zeros(A.shape[1], len(names), requires_grad=True); b = torch.zeros(len(names), requires_grad=True)
    opt = torch.optim.Adam([W, b], lr=0.05); ytt = torch.tensor(ytr)
    for _ in range(steps):
        opt.zero_grad(); (F.cross_entropy(A @ W + b, ytt) + 1e-3 * W.pow(2).sum()).backward(); opt.step()
    with torch.no_grad():
        return (torch.tensor((X - mu) / sd, dtype=torch.float32) @ W + b).argmax(1).numpy()


def ncm(Xtr, ytr, X):
    C = np.stack([Xtr[ytr == k].mean(0) for k in range(len(names))]); C /= np.linalg.norm(C, axis=1, keepdims=True) + 1e-12
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12) @ C.T).argmax(1)


pl, ll = lr(Xt, yt, Xp), lr(Xt, yt, Xl)
pn, ln = ncm(Xt, yt, Xp), ncm(Xt, yt, Xl)
print(f"    state-LR (standardised, full batch): NAME train asks {int((pl == yp).sum())}/{len(yp)} · T_L {int((ll == yl).sum())}/{len(yl)}"
      f" · state-NCM: {int((pn == yp).sum())}/{len(yp)} · {int((ln == yl).sum())}/{len(yl)}")

# (c) the recurrent weights
e = arm.engine
for g in ("r", "z", "n"):
    Wih, Whh = getattr(e, f"W_ih_{g}")[:act].detach(), getattr(e, f"W_hh_{g}")[:act, :act].detach()
    print(f"(c) gate {g}: ||W_ih||_F {float(Wih.norm()):.3f} (mean |w| {float(Wih.abs().mean()):.4f}, glance cols {float(Wih[:, :144].abs().mean()):.4f}, one-hot cols {float(Wih[:, 144:].abs().mean()):.4f})"
          f" · ||W_hh||_F {float(Whh.norm()):.3f} (mean |w| {float(Whh.abs().mean()):.4f}; initial block rows<64 {float(Whh[:64, :64].abs().mean()):.4f}; born rows>=64 {float(Whh[64:, :].abs().mean()):.4f})"
          f" · |bias| mean {float(getattr(e, f'b_{g}')[:act].abs().mean()):.4f}")

# (d) the cost of a prototype / LDA reader per event, one thread
rng = np.random.default_rng(0)
for d in (144, act):
    mu = np.zeros(d); M2 = np.zeros(d); S = np.zeros((d, d)); protos = np.zeros((26, d)); counts = np.zeros(26); n = 0
    xs = rng.random((1000, d)) * 0.4; ys = rng.integers(0, 26, 1000)
    t0 = time.perf_counter()
    for x, y in zip(xs, ys):
        n += 1; delta = x - mu; mu += delta / n; M2 += delta * (x - mu)          # Welford
        counts[y] += 1; protos[y] += (x - protos[y]) / counts[y]                # the class prototype
        xc = x - mu; S += np.outer(xc, xc)                                      # the shared covariance (rank-1)
    t_upd = (time.perf_counter() - t0) / 1000
    t0 = time.perf_counter()
    Sinv = np.linalg.inv(S / max(n - 1, 1) + 1e-3 * np.eye(d)); W = protos @ Sinv                  # once per sleep
    t_solve = time.perf_counter() - t0
    t0 = time.perf_counter()
    for x in xs:
        _ = (W @ (x - mu)).argmax()                                             # the read
    t_read = (time.perf_counter() - t0) / 1000
    print(f"(d) d = {d}: update {t_upd * 1e6:.0f} µs/event · read {t_read * 1e6:.1f} µs/event · the LDA solve (once per sleep) {t_solve * 1e3:.1f} ms")
