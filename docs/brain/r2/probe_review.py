"""probe_review.py — the cheap measurements the review of RESEARCH-SEAT-R2.md turns on (edit: Fable 5.1 (brain r2), 2026-09-27 19:36 +0400).
On B1.1's records, both seeds, A1's FINAL snapshot, the NAME-ask road from one fixed start state (F11/F13's road):
 (1) the common-vs-letter energy: ||mean state||^2 against the mean ||h - mean||^2 — the seat's «(0.06/0.735)^2 ≈ 1/150» mixes a
     whole-vector deviation with a PER-UNIT magnitude; the ratio that governs an SGD head is over whole vectors;
 (2) the SAME online readers, one pass over the 624 TEACH rows in tape order, on the STATE and on the INPUT (F_pool: the unit-normalised
     mean glance, the creature's BIND pooling) — does the trunk cost naming for an online reader?  sgd-std · rls · slda (running class
     means + a shared covariance, shrinkage 1e-4, the precision solved at the end of the pass) · imprint (sgd-std whose new row is born
     from its first standardised example: unscaled, and scaled by 1/d);
 (3) A1's OWN confidence at T_L (raw.conf in answers.jsonl), B1.1 and B1.0 — the seat wrote «0/156 answered at 97 % confidence»;
 (4) the hybrids' SAME control: on B1.1's F and A5 records, each SAME ask paired with its SAME_NAME_REF NAME ask on the identical
     rendering (the tape's operand row), the two answers and the parts that gave them (raw.routed_to) — a routing defect, or two namers
     that disagree?
Run:  OPENBLAS_NUM_THREADS=1 PYTHONPATH=/data/dev/genome-wt-b1-tape2 nice -n 19 /data/dev/venvs/brain/bin/python -u probe_review.py
"""
import json
import os
from collections import Counter

import numpy as np
import torch

from brain.arms.soft.arm import ArmA1
from brain.glance_cache import Cache

torch.set_num_threads(1)
ROOT = "/data/dev/brain-runs/b1.1"


def load_rows(path):
    return [json.loads(l) for l in open(path) if l.strip()]


class Welford:
    def __init__(self, d):
        self.n = 0; self.mu = np.zeros(d); self.M2 = np.zeros(d)

    def add(self, x):
        self.n += 1; d = x - self.mu; self.mu += d / self.n; self.M2 += d * (x - self.mu)

    def std(self):
        return np.sqrt(self.M2 / max(self.n - 1, 1)) + 1e-6


def run_readers(Xt, yt_names, Xp, Xl, names_all):
    """one pass over (Xt, yt) in order; returns {reader: (pred_pre, pred_tl)} as name strings"""
    d = Xt.shape[1]
    out = {}
    for reader in ("sgd-std", "rls", "slda", "imprint-raw", "imprint-scaled"):
        w = Welford(d); names = []
        W = np.zeros((0, d)); b = np.zeros(0)                       # sgd heads (rows per name)
        P = np.eye(d + 1) / 0.01; Wr = np.zeros((d + 1, 0))          # rls
        mus = {}; cnt = {}; S = np.zeros((d, d)); nS = 0             # slda
        for x, y in zip(Xt, yt_names):
            w.add(x); z = (x - w.mu) / w.std()
            if y not in names:
                names.append(y)
                if reader in ("sgd-std", "imprint-raw", "imprint-scaled"):
                    row = np.zeros(d)
                    if reader == "imprint-raw": row = z.copy()
                    if reader == "imprint-scaled": row = z / d
                    W = np.vstack([W, row]); b = np.append(b, 0.0)
                Wr = np.hstack([Wr, np.zeros((d + 1, 1))])
                mus[y] = np.zeros(d); cnt[y] = 0
            k = names.index(y)
            if reader in ("sgd-std", "imprint-raw", "imprint-scaled"):
                logits = W @ z + b; p = np.exp(logits - logits.max()); p /= p.sum(); p[k] -= 1.0
                W -= 0.01 * np.outer(p, z); b -= 0.01 * p
            elif reader == "rls":
                xa = np.append(z, 1.0); t = np.zeros(len(names)); t[k] = 1.0
                Px = P @ xa; g = Px / (1.0 + xa @ Px); e = t - Wr.T @ xa
                Wr += np.outer(g, e); P -= np.outer(g, Px)
            elif reader == "slda":
                cnt[y] += 1; mus[y] += (z - mus[y]) / cnt[y]
                zc = z - w.mu * 0  # the standardised state is already centred by the running mean
                S += np.outer(z, z); nS += 1
        def finish_pred(X):
            Z = (X - w.mu) / w.std()
            if reader in ("sgd-std", "imprint-raw", "imprint-scaled"):
                return [names[i] for i in (Z @ W.T + b).argmax(1)]
            if reader == "rls":
                Za = np.hstack([Z, np.ones((len(Z), 1))]); return [names[i] for i in (Za @ Wr).argmax(1)]
            Sig = S / max(nS - 1, 1); Lam = np.linalg.inv((1 - 1e-4) * Sig + 1e-4 * np.eye(d))
            M = np.stack([mus[n] for n in names]); Wl = M @ Lam; bl = -0.5 * np.einsum("kd,kd->k", M, Wl)
            return [names[i] for i in (Z @ Wl.T + bl).argmax(1)]
        out[reader] = (finish_pred(Xp), finish_pred(Xl))
    return out


def score(pred, y):
    n = len(y); ok = sum(1 for p, t in zip(pred, y) if p == t)
    return f"{ok}/{n} ({100 * ok / n:.0f} %) · distinct {len(set(pred))}"


for seed in ("20261001", "20261002"):
    print(f"=== seed {seed} ===")
    rows = load_rows(f"{ROOT}/{seed}/tape.jsonl")
    truth = {t["seq"]: t for t in load_rows(f"{ROOT}/{seed}/truth.jsonl") if t.get("type") == "ask"}
    teach = [r for r in rows if r["kind"] == "TEACH" and len(r["payload"]["name"]) == 1]
    fb = {r["payload"]["ask_seq"]: r["payload"]["right"] for r in rows if r["kind"] == "FEEDBACK"}
    pre = [r for r in rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["NAME"] and r["phase"] == "L4" and r["seq"] in fb]
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
    rid_p = [r["payload"]["operands"][0]["value"] for r in pre]; yp = [fb[r["seq"]] for r in pre]
    rid_l = [r["payload"]["operands"][0]["value"] for r in tl]; yl = [truth[r["seq"]]["answer"] for r in tl]
    Xs = {k: np.stack([state(r) for r in rids]) for k, rids in (("t", rid_t), ("p", rid_p), ("l", rid_l))}
    Xi = {k: np.stack([fpool(r) for r in rids]) for k, rids in (("t", rid_t), ("p", rid_p), ("l", rid_l))}
    # (1) the energies
    hbar = Xs["t"].mean(0); common = float(hbar @ hbar); dev = float(np.mean(np.sum((Xs["t"] - hbar) ** 2, axis=1)))
    ibar = Xi["t"].mean(0); icommon = float(ibar @ ibar); idev = float(np.mean(np.sum((Xi["t"] - ibar) ** 2, axis=1)))
    print(f"(1) STATE (h {act}): ||mean||^2 {common:.2f} · mean ||h-mean||^2 {dev:.4f} · ratio letter/common 1/{common / dev:,.0f} · "
          f"the seat's (0.06/0.735)^2 = 1/{(0.735 / 0.06) ** 2:.0f}")
    print(f"    INPUT F_pool (144): ||mean||^2 {icommon:.3f} · mean ||x-mean||^2 {idev:.4f} · ratio 1/{icommon / idev:.1f}")
    # (2) the readers on the state and on the input
    for label, X in (("STATE", Xs), ("INPUT", Xi)):
        res = run_readers(X["t"], yt, X["p"], X["l"], None)
        for reader, (pp, pl) in res.items():
            print(f"(2) {label:5s} {reader:15s}: NAME train asks {score(pp, yp)} · T_L {score(pl, yl)}")
    # (3) A1's own confidence at T_L
    for root_, tag in ((ROOT, "B1.1"), ("/data/dev/brain-runs/b1", "B1.0")):
        p = f"{root_}/runs/{seed}/A1/answers.jsonl"
        if not os.path.exists(p):
            print(f"(3) {tag}: no A1 record"); continue
        ans = load_rows(p)
        confs = [a["answer"]["raw"]["conf"] for a in ans if a.get("sitting") == "T_L" and a["cues"] == ["NAME"] and isinstance(a["answer"].get("raw"), dict) and "conf" in a["answer"]["raw"]]
        given = Counter(a["answer"].get("value") for a in ans if a.get("sitting") == "T_L" and a["cues"] == ["NAME"])
        if confs:
            print(f"(3) {tag} A1 T_L NAME conf: n {len(confs)} · mean {np.mean(confs):.3f} · min {np.min(confs):.3f} · max {np.max(confs):.3f} · answers {dict(given.most_common(2))}")
    # (4) the hybrids' SAME control — the GRADED one at T_L: CONTROL_SAME (cue SAME) paired with SAME_NAME_REF (cue NAME) on the
    # IDENTICAL rendering (the same operand row; R13), the two answers and the parts that gave them (raw.routed_to)
    asks = {r["seq"]: r for r in rows if r["kind"] == "ASK"}
    fam = {seq: t.get("family") for seq, t in truth.items()}
    for arm_name in ("F", "A5", "E′", "D", "A0"):
        p = f"{ROOT}/runs/{seed}/{arm_name}/answers.jsonl"
        if not os.path.exists(p):
            print(f"(4) {arm_name}: no record"); continue
        ans = {a["seq"]: a for a in load_rows(p)}
        same = [a for a in ans.values() if fam.get(a["seq"]) == "CONTROL_SAME"]
        ref = {asks[a["seq"]]["payload"]["operands"][0]["value"]: a for a in ans.values() if fam.get(a["seq"]) == "SAME_NAME_REF"}
        agree = disagree = 0; parts = Counter(); kinds = Counter(); dis_examples = []
        for a in same:
            rid = asks[a["seq"]]["payload"]["operands"][0]["value"]
            r = ref.get(rid)
            if r is None:
                continue
            sa, na = a["answer"].get("value"), r["answer"].get("value")
            parts[(a["answer"].get("raw", {}).get("routed_to"), r["answer"].get("raw", {}).get("routed_to"))] += 1
            kinds[(a["answer"]["kind"], r["answer"]["kind"])] += 1
            if a["answer"]["kind"] == "NAME" and sa == na: agree += 1
            else:
                disagree += 1
                if len(dis_examples) < 3: dis_examples.append((a["item"], a["answer"]["kind"], sa, r["answer"]["kind"], na, a["truth"]))
        print(f"(4) {arm_name}: CONTROL_SAME asks {len(same)} · paired {agree + disagree} · SAME == NAME on the same rendering {agree} · differ {disagree} · "
              f"(SAME part, NAME part) {dict(parts)} · (SAME kind, NAME kind) {dict(kinds)} · e.g. {dis_examples}")
