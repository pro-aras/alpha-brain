#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-29 12:09 +0400 — new tool: F-M2B's PROBE, on TRAINING rows alone.
"""tools/brain/diag/probe_fm2b.py --ws WS [--fit 8000] [--out DIR]

F-M2B (PREREG-BRAIN-IN-BODY §7): «a READER built from the learner's CONFIDENT meetings only». No record says where
«confident» sits. This probe measures it on TRAINING rows alone (#244 (1)): the brain learns the first --fit training scenes
of one world seed; the remaining training scenes are the VALIDATION rows (never learned, never a test scene).

  PART A — is a meeting's responsibility a usable confidence? Per stored meeting of a mature word: H (things in view),
           max r, and (a READING: the truth is read here, never in the organ) whether argmax r is the hypothesis of the
           true referent. Per threshold tau: the share of meetings kept and the attribution accuracy among the kept.
  PART B — the reader rebuilt from the kept meetings, per tau and per form («soft»: the kept meetings' rows weighted by r;
           «hard»: the kept meetings' argmax row alone, weight 1). On the validation rows' ONE-THING scenes:
             pseudo-novel  leave-one-shape-out: shape s is removed from the reader (its mean, its band, its rows in its
                           type's covariance); a thing of shape s is CORRECT when no shape word holds it (M2b's own rule);
             true-hold     with s in the reader: the share of s-things that s holds;
             false-name    with s in the reader: the share of s-things another shape word holds;
             size / colour the share of things whose own size / colour word holds them.
A presence count stands beside every rate. Nothing here writes the organ or any life root.

edit: Claude (Fable 5.1, the seat), 2026-09-29 12:13 +0400 — the first run's finding: a ONE-hypothesis view has r = 1 and is wrong 0.13 of the time
(the eye missed the named thing), so max r alone cannot clean the store. The second confidence signal is the brain's OWN
«none» at the meeting (T-MEM-2's hook, `Brain.learn`'s `none`: «this phrase fits nothing I see», read BEFORE the scene is
learned). edit: Claude (Fable 5.1, the seat), 2026-09-29 12:17 +0400 — THE PROXY'S CEILING: one more cell, "oracle:hard@0.0" — the reader built from the
TRUE referent's hypothesis of every meeting where the gaze saw it (the truth read by the BENCH; a READING, never a candidate).
edit: Claude (Fable 5.1, the seat), 2026-09-29 12:21 +0400 — the second run's finding: at 0.96 right attributions the proxy reads 0.42–0.46 and the
exact-attribution reader 0.77–0.84, so the last wrong rows matter most (they are OTHER SHAPES: they put between-shape scatter
into the type's covariance). Two more signals, both the brain's own: "jn" = the UTTERANCE's joint attribution (the parent names
ONE thing: J(h) ∝ Π_w r_w(h) over the said words' stored responsibilities; the row is argmax J, kept when max J >= tau and
«none» was not True); "an" = "rn" and every said word's own argmax is the same hypothesis. And TRIM k: after a build, each
word's rows farther than its own band are dropped and the reader rebuilt, k times (rows are removed, never re-attributed).
edit: Claude (Fable 5.1, the seat), 2026-09-29 12:33 +0400 — the third run's finding: TRIM moves along the hold / refuse trade (each round drops
the 0.10 beyond the 0.90 band, so the hold rate falls 0.09 a round, the exact-attribution reader's too); it is not a fix. No
confident rule without it passes 0.49 on the proxy (the exact-attribution reader: 0.77–0.84). ROBUST k: the MEAN and the
COVARIANCE are fitted on each word's INLIERS (its rows inside its own band), k rounds, while the BAND stays the weighted 0.90
quantile over ALL the kept rows under the final metric — the band's quantile is the law's, only the metric is cleaned.
edit: Claude (Fable 5.1, the seat), 2026-09-29 12:49 +0400 — the fourth run's finding: ROBUST does not help (0.37–0.41 against 0.40–0.46
without it). `--grid dose` is the DOSE-RESPONSE: the exact-attribution reader with a share c of its multi-hypothesis rows
replaced by a WRONG hypothesis of the same view (drawn by substream(ws, "dose:<c>")), c in DOSES — how right must the store
be for the reader to refuse a shape it was never taught? (A reading: the truth is the bench's.)
edit: Claude (Fable 5.1, the seat), 2026-09-29 12:51 +0400 — the dose-response's finding: the reader needs a store about 0.98–0.99 right; the
responsibilities, frozen at each meeting by a learner that was then YOUNG, reach 0.96. `--grid point` is the record's second
option read through the LEARNER, not the reader: every learned scene is pointed at AGAIN by the learner as it stands at the
reading point (its own law: `RWRoad.answer_point` over the scene's raw view and the parent's phrase, «none» = τ_point); a
meeting is kept when «none» does not fire and the best thing leads the second by >= tau (log units); its row is the pointed
thing, weight 1. "pt" reads the organ's own calibration list (`Brain.seen`: every scene's raw view and words).
edit: Claude (Fable 5.1, the seat), 2026-09-29 12:52 +0400 — `--grid m2b --fit 10000`: THE PROXY AGAINST THE REAL MARK, on test sets ALREADY READ
(the fresh set 2026140x and the older 2026120x; never the gate's): the brain learns all 10,000 scenes as the scored run did,
and each reader answers the m2b split's «what is this?» items by M2b's own rule (CORRECT = no shape word holds the thing).
THE CONTROL: the law reader here must read the record's own M2b (0.646 / 0.708 / 0.729 on the fresh set).
FILTERS: "r" = max r >= tau; "rn" = "r" and the meeting's «none» was not True (a meeting before the first reading
point has none = None and is KEPT); "rN" = "r" and the meeting's «none» was False (those early meetings DROPPED)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain.scene import cache as C          # noqa: E402
from brain.scene import learners as Lr      # noqa: E402
from brain.scene import marks as M          # noqa: E402
from brain.scene import world as W          # noqa: E402
from genome import brain as B               # noqa: E402
from genome.machinery import parse_genome   # noqa: E402
from tools.brain import gate_alone as GA    # noqa: E402

TAUS = (0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0)
FORMS = ("soft", "hard")
FILTERS = ("r", "rn", "rN")
SCENE_FILTERS = ("jn", "an")
TRIMS = (0, 1, 2)
DOSES = (0.0, 0.01, 0.02, 0.04, 0.06, 0.08, 0.12, 0.16)
MARGINS = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)


def keeps(flt: str, tau: float, r: np.ndarray, none) -> bool:
    if float(np.max(r)) < tau:
        return False
    if flt == "rn":
        return none is not True
    if flt == "rN":
        return none is False
    return True


def brain_cfg() -> Dict[str, object]:
    """The BRAIN line of the template a next life is seeded from (genome/brain/BRAIN-LEAN.genome), by the genome's parser."""
    return dict(parse_genome((ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()).declared["BRAIN"])


def hyp_of(g) -> Tuple[list, np.ndarray, List[List[int]]]:
    hyps, X = B.things_in_view(g)
    return hyps, X, [[int(m) for m in h.members] for h in hyps]


def labels_of(members: Sequence[Sequence[int]], fix_thing) -> List[Optional[int]]:
    return [M.hyp_label(c) for c in M.hyp_counts(members, fix_thing)]


# ------------------------------------------------------------------------------------------------ PART A
def part_a(brain: "B.Brain", truth, n_fit: int, nones: Sequence[Optional[bool]]) -> Dict[str, object]:
    L = brain.L
    rows = []            # one per stored NON-episodic meeting of a mature word
    skipped = {"episodic": 0, "shape_mismatch": 0}
    for w in L.mature_words():
        j = L.index[w]
        for m, (r, t) in enumerate(zip(L.store_r[j], L.store_t[j])):
            i = int(t) - 1                                   # the scene index (L.scenes counted the call before storing)
            if not (0 <= i < n_fit):
                raise SystemExit(f"store_t {t} of {w!r} is outside the fitted scenes")
            members = brain.canvas[i][1]
            if len(r) != len(members):
                skipped["episodic" if len(r) == 1 and m == 0 else "shape_mismatch"] += 1
                continue
            lab = labels_of(members, truth[i]["fix_thing"])
            ref = int(truth[i]["referent"])
            h_true = [h for h, x in enumerate(lab) if x == ref]
            h_hat = int(np.argmax(r))
            rows.append({"word": w, "type": W.word_type(w), "H": len(r), "max_r": float(np.max(r)), "r": r, "none": nones[i],
                         "seen": bool(h_true), "right": bool(h_true) and h_hat in h_true,
                         "mass_true": float(sum(r[h] for h in h_true)) / float(np.sum(r)) if float(np.sum(r)) > 0 else 0.0})
    out: Dict[str, object] = {"n_meetings": len(rows), "skipped": skipped, "by_type": {}}
    for ty in ("size", "colour", "shape", "all"):
        sel = [x for x in rows if ty == "all" or x["type"] == ty]
        blk = {"n": len(sel), "H1_share": _rate(x["H"] == 1 for x in sel), "referent_seen_share": _rate(x["seen"] for x in sel),
               "max_r_quantiles": ({q: float(np.quantile([x["max_r"] for x in sel], q)) for q in (0.05, 0.25, 0.5, 0.75, 0.95)}
                                   if sel else None),
               "taus": {}}
        multi = [x for x in sel if x["H"] > 1]
        blk["none_counts"] = {str(v): sum(1 for x in sel if x["none"] is v) for v in (True, False, None)}
        blk["none_true_when_wrong"] = _rate(x["none"] is True for x in sel if not x["right"])
        blk["none_true_when_right"] = _rate(x["none"] is True for x in sel if x["right"])
        for flt in FILTERS:
            for tau in TAUS:
                k = [x for x in sel if keeps(flt, tau, x["r"], x["none"])]
                km = [x for x in k if x["H"] > 1]
                mass = float(sum(float(np.sum(x["r"])) for x in k))
                blk["taus"][f"{flt}@{tau}"] = {
                    "kept": len(k), "kept_share": len(k) / len(sel) if sel else None,
                    "right_among_kept": _rate(x["right"] for x in k),
                    "wrong_mass_soft": (1.0 - sum(x["mass_true"] * float(np.sum(x["r"])) for x in k) / mass) if mass > 0 else None,
                    "kept_multi": len(km), "right_among_kept_multi": _rate(x["right"] for x in km)}
        out["by_type"][ty] = blk
    info = scene_info(L)
    sc: Dict[str, object] = {}
    seen_scenes = sorted(info)
    for flt in SCENE_FILTERS:
        for tau in TAUS:
            k = []
            for i in seen_scenes:
                si = info[i]
                if nones[i] is True:
                    continue
                if flt == "jn" and si["conf"] < tau:
                    continue
                if flt == "an" and not (si["agree"] and si["min_max_r"] >= tau):
                    continue
                lab = labels_of(brain.canvas[i][1], truth[i]["fix_thing"])
                k.append(lab[si["h"]] == int(truth[i]["referent"]))
            sc[f"{flt}@{tau}"] = {"scenes_kept": len(k), "kept_share": len(k) / len(seen_scenes) if seen_scenes else None,
                                  "right_among_kept": _rate(k)}
    out["scene_filters"] = {"scenes_with_a_stored_meeting": len(seen_scenes), "cells": sc}
    for x in rows:
        del x["r"]
    return out


def _rate(it) -> Optional[float]:
    v = [bool(x) for x in it]
    return (sum(v) / len(v)) if v else None


# ------------------------------------------------------------------------------------------------ PART B
def scene_info(L: "Lr.RWLearner") -> Dict[int, Dict[str, object]]:
    """Per learned scene, from the STORE alone: the said words' stored responsibilities (non-episodic meetings), their joint
    attribution J(h) ∝ Π_w r_w(h), whether every word's own argmax agrees, the smallest of the words' max r."""
    by: Dict[int, List[np.ndarray]] = {}
    for j in range(len(L.words)):
        for r, t in zip(L.store_r[j], L.store_t[j]):
            by.setdefault(int(t) - 1, []).append(np.asarray(r, dtype=np.float64))
    out: Dict[int, Dict[str, object]] = {}
    for i, rs in by.items():
        n = max(len(r) for r in rs)
        rs = [r for r in rs if len(r) == n]                  # an episodic write's one row is not a view's list
        if not rs:
            continue
        lj = np.sum([np.log(np.maximum(r, 1e-300)) for r in rs], axis=0)
        lj = lj - np.max(lj)
        J = np.exp(lj) / float(np.sum(np.exp(lj)))
        arg = [int(np.argmax(r)) for r in rs]
        out[i] = {"n": n, "h": int(np.argmax(J)), "conf": float(np.max(J)), "agree": len(set(arg)) == 1,
                  "min_max_r": float(min(float(np.max(r)) for r in rs)), "n_words": len(rs)}
    return out


def repoint(brain: "B.Brain", ws: int) -> Dict[int, Dict[str, object]]:
    """Per learned scene: the learner's pointing NOW (the law road) for the parent's phrase over the scene's own raw view."""
    from brain.world.seeds import substream as _sub
    road = brain.road()
    out: Dict[int, Dict[str, object]] = {}
    for i, (X, words, _n) in enumerate(brain.seen):
        X = np.atleast_2d(X)
        if X.shape[0] == 0:
            continue
        a = road.answer_point(X, list(dict.fromkeys(words)), _sub(int(ws), f"repoint:{i}"))
        if a.get("point") is None:
            continue
        s = sorted((float(v) for v in a["scores"]), reverse=True)
        margin = (s[0] - s[1]) if len(s) > 1 else float("inf")
        if not np.isfinite(s[0]):
            continue
        out[i] = {"n": int(X.shape[0]), "h": int(a["point"]), "none": bool(a["none"]), "margin": float(margin)}
    return out


class Reader:
    """The READER's state (learners.RWLearner._reader_state's own arithmetic) over a FILTERED store. tau 0.0 + «soft» is the
    law's state, value for value (checked in main against the brain's own reader)."""

    def __init__(self, L: "Lr.RWLearner", types, eps: float, tau: float, form: str, drop: Optional[str] = None,
                 flt: str = "r", nones: Optional[Sequence[Optional[bool]]] = None, true_h=None, info=None, trim: int = 0, robust: int = 0, dose_seed: int = 0):
        self.L, self.types, self.eps = L, [tuple(t) for t in types], float(eps)
        self.rows: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
        self.kept: Dict[str, Tuple[int, int]] = {}
        from brain.world.seeds import substream as _sub
        dose_rng = _sub(int(dose_seed), f"dose:{tau}") if flt == "dose" else None
        for T in self.types:
            for w in T:
                if w == drop:
                    continue
                j = L.index[w]
                Zs, Rs, n_all, n_kept = [], [], 0, 0
                for z, r, t in zip(L.store_z[j], L.store_r[j], L.store_t[j]):
                    n_all += 1
                    if flt in ("oracle", "dose"):
                        h = true_h(int(t) - 1, len(r))
                        if h is None:
                            continue
                        if flt == "dose" and len(r) > 1 and float(dose_rng.random()) < tau:
                            h = [k for k in range(len(r)) if k != h][int(dose_rng.integers(len(r) - 1))]
                        n_kept += 1
                        Zs.append(z[h][None, :]); Rs.append(np.ones(1))
                        continue
                    if flt == "pt":
                        si = info.get(int(t) - 1)
                        if si is None or si["n"] != len(r) or si["none"] or si["margin"] < tau:
                            continue
                        n_kept += 1
                        Zs.append(z[si["h"]][None, :]); Rs.append(np.ones(1))
                        continue
                    if flt in SCENE_FILTERS:
                        si = info.get(int(t) - 1)
                        nn = None if nones is None else nones[int(t) - 1]
                        if si is None or si["n"] != len(r) or nn is True:
                            continue
                        if flt == "jn" and si["conf"] < tau:
                            continue
                        if flt == "an" and not (si["agree"] and si["min_max_r"] >= tau):
                            continue
                        n_kept += 1
                        Zs.append(z[si["h"]][None, :]); Rs.append(np.ones(1))
                        continue
                    if not keeps(flt, tau, r, None if nones is None else nones[int(t) - 1]):
                        continue
                    n_kept += 1
                    if form == "hard":
                        h = int(np.argmax(r))
                        Zs.append(z[h][None, :]); Rs.append(np.ones(1))
                    else:
                        Zs.append(z); Rs.append(r)
                self.kept[w] = (n_kept, n_all)
                if Zs:
                    self.rows[w] = (np.concatenate(Zs, axis=0), np.concatenate(Rs, axis=0))
        self.inl: Dict[str, np.ndarray] = {}
        self._fit()
        self.outliers: Dict[str, int] = {}
        for _ in range(int(robust)):
            new = {}
            for w in list(self.rows):
                if w not in self.band or not np.isfinite(self.band[w]):
                    continue
                Z, R = self.rows[w]
                E = Z - self.mu[w][None, :]
                d = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", E, self.lam[self.type_of[w]], E), 0.0))
                keep = d <= self.band[w]
                if keep.any():
                    new[w] = keep
                    self.outliers[w] = int((~keep).sum())
            self.inl = new
            self._fit()
        self.trimmed: Dict[str, int] = {}
        for _ in range(int(trim)):
            for w in list(self.rows):
                if w not in self.band or not np.isfinite(self.band[w]):
                    continue
                Z, R = self.rows[w]
                E = Z - self.mu[w][None, :]
                d = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", E, self.lam[self.type_of[w]], E), 0.0))
                keep = d <= self.band[w]
                self.trimmed[w] = self.trimmed.get(w, 0) + int((~keep).sum())
                if keep.any():
                    self.rows[w] = (Z[keep], R[keep])
            self._fit()

    def _fit(self) -> None:
        L = self.L
        self.mu: Dict[str, np.ndarray] = {}
        for w, (Z, R) in self.rows.items():
            k = self.inl.get(w)
            Zi, Ri = (Z, R) if k is None else (Z[k], R[k])
            if float(Ri.sum()) > 0:
                self.mu[w] = (Ri @ Zi) / float(Ri.sum())
        self.lam: List[Optional[np.ndarray]] = []
        self.band: Dict[str, float] = {}
        self.type_of: Dict[str, int] = {}
        for k, T in enumerate(self.types):
            num, den = np.zeros((L.dim, L.dim)), 0.0
            for w in T:
                if w not in self.mu:
                    continue
                Z, R = self.rows[w]
                k_ = self.inl.get(w)
                if k_ is not None:
                    Z, R = Z[k_], R[k_]
                D = Z - self.mu[w][None, :]
                num += (D * R[:, None]).T @ D
                den += float(R.sum())
            lam = Lr.shrunk_inverse(num / den, self.eps) if den > 0 else None
            self.lam.append(lam)
            for w in T:
                if w not in self.mu or lam is None:
                    continue
                Z, R = self.rows[w]
                E = Z - self.mu[w][None, :]
                d = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", E, lam, E), 0.0))
                q = Lr.weighted_quantile(d, R, Lr.BAND_Q)
                self.band[w] = float("inf") if q is None else float(q)
                self.type_of[w] = k

    def held(self, z: np.ndarray) -> List[str]:
        out = []
        for w, b in self.band.items():
            if self.L.meetings[self.L.index[w]] < self.L.p_from:
                continue
            e = z - self.mu[w]
            d = float(np.sqrt(max(float(e @ self.lam[self.type_of[w]] @ e), 0.0)))
            if d <= b:
                out.append(w)
        return out


def validation_things(train, truth, lo: int, hi: int, L) -> List[Dict[str, object]]:
    """The validation rows' ONE-THING scenes whose one thing the gaze covered: its hypothesis's standardised input."""
    out = []
    counts = {"scenes": 0, "one_thing": 0, "covered": 0}
    for i in range(lo, hi):
        counts["scenes"] += 1
        tr = truth[i]
        if len(tr["things"]) != 1:
            continue
        counts["one_thing"] += 1
        g = GA.glance_of(train, i)
        hyps, X, members = hyp_of(g)
        lab = labels_of(members, tr["fix_thing"])
        hs = [h for h, x in enumerate(lab) if x == 0]
        if not hs:
            continue
        counts["covered"] += 1
        h = max(hs, key=lambda k: len(members[k]))
        t = tr["things"][0]
        out.append({"scene": i, "z": L.stats.standardise(X[h][None, :])[0], "shape": t["shape"], "colour": t["colour"],
                    "size": t["size"]})
    return out, counts


def part_b(brain: "B.Brain", things, eps: float, nones: Sequence[Optional[bool]], truth=None, grid_name: str = "full",
           ws: int = 0) -> Dict[str, object]:
    L = brain.L
    types = brain.L.reader["ear"]["types"]
    shapes = [w for w in W.SHAPES if w in L.index and L.meetings[L.index[w]] >= L.p_from]
    out: Dict[str, object] = {"types": [list(t) for t in types], "shapes": shapes, "cells": {}}
    def true_h(i: int, n_rows: int) -> Optional[int]:
        members = brain.canvas[i][1]
        if n_rows != len(members):
            return None                                      # an episodic write: its one row is not a view's hypothesis list
        lab = labels_of(members, truth[i]["fix_thing"])
        hs = [h for h, x in enumerate(lab) if x == int(truth[i]["referent"])]
        return max(hs, key=lambda k: len(members[k])) if hs else None

    info = scene_info(L)
    grid = [(f, fo, ta, 0, rb) for (f, fo, ta) in (("r", "soft", 0.0), ("r", "hard", 0.0), ("rn", "hard", 0.0), ("rn", "hard", 0.8),
                                                   ("rn", "hard", 0.9), ("rn", "hard", 0.95), ("jn", "hard", 0.0), ("jn", "hard", 0.8),
                                                   ("jn", "hard", 0.9), ("jn", "hard", 0.95), ("an", "hard", 0.9), ("rN", "hard", 0.9),
                                                   ("oracle", "hard", 0.0))
            for rb in (0, 1, 2, 3, 5)]
    if grid_name == "look":          # edit: Claude (Fable 5.1, the seat), 2026-09-29 15:15 +0400 — tools/brain/diag/probe_lookagain.py's cells
        grid = [("r", "soft", 0.0, 0, 0), ("r", "hard", 0.0, 0, 0), ("rn", "soft", 0.0, 0, 0), ("rn", "hard", 0.0, 0, 0),
                ("rn", "hard", 0.9, 0, 0), ("rn", "hard", 0.95, 0, 0), ("oracle", "hard", 0.0, 0, 0)]
    if grid_name == "dose":
        grid = [("dose", "hard", c, 0, 0) for c in DOSES]
    if grid_name == "m2b":
        info_pt = repoint(brain, ws)
        out["m2b"] = {}
        cells = [("r", "soft", 0.0), ("rn", "hard", 0.0), ("rn", "hard", 0.9), ("rn", "hard", 0.95), ("rN", "hard", 0.95),
                 ("jn", "hard", 0.95), ("an", "hard", 0.9), ("pt", "hard", 2.0), ("pt", "hard", 4.0), ("oracle", "hard", 0.0)]
        readers = {f"{f}:{fo}@{ta}": Reader(L, types, eps, ta, fo, flt=f, nones=nones, true_h=true_h,
                                            info=(info_pt if f == "pt" else info), dose_seed=ws) for f, fo, ta in cells}
        for tset in ("fresh", "s1b1"):
            d = C.cache_dir(C.RUNS, ws, "m2b", tset)
            C.check_code(d)
            P_, T_ = C.ScenePercepts(d), C.load_truth(d)
            items = []
            for row in range(len(P_)):
                tr = T_[row]
                th = tr["things"][0]
                g = GA.glance_of(P_, row)
                hyps, X, _members = hyp_of(g)
                box = [int(th["top"]), int(th["left"]), int(th["side"])]
                h = B.pointer_hypothesis(box, [float(v) for v in tr["centroids"][0]], g["fix"], hyps)
                covered = M.covered(0, tr["fix_thing"])
                items.append({"shape": th["shape"], "graded": th["shape"] in W.M2B_SHAPES, "covered": bool(covered),
                              "z": None if h is None else L.stats.standardise(X[h][None, :])[0]})
            blk = {"n_items": len(items), "graded": sum(1 for x in items if x["graded"]),
                   "graded_covered": sum(1 for x in items if x["graded"] and x["covered"]), "readers": {}}
            for name, rd in readers.items():
                sel = [x for x in items if x["graded"] and x["covered"] and x["z"] is not None]
                ok = [not any(w in W.SHAPE_WORDS for w in rd.held(x["z"])) for x in sel]
                per = {}
                for s in W.M2B_SHAPES:
                    ss = [o for o, x in zip(ok, sel) if x["shape"] == s]
                    per[s] = (sum(ss) / len(ss)) if ss else None
                blk["readers"][name] = {"n": len(sel), "correct": (sum(ok) / len(ok)) if ok else None, "per_shape": per}
            out["m2b"][tset] = blk
        grid = []
    if grid_name == "point":
        info = repoint(brain, ws)
        grid = [("pt", "hard", m, 0, 0) for m in MARGINS] + [("r", "soft", 0.0, 0, 0), ("oracle", "hard", 0.0, 0, 0)]
        rp = []
        for i, si in info.items():
            lab = labels_of(brain.canvas[i][1], truth[i]["fix_thing"])
            rp.append((si["none"], si["margin"], lab[si["h"]] == int(truth[i]["referent"]), int(truth[i]["referent"]) in lab))
        out["repoint"] = {"scenes": len(info), "none_fired": sum(1 for x in rp if x[0]),
                          "none_fired_when_referent_unseen": _rate(x[0] for x in rp if not x[3]),
                          "none_fired_when_referent_seen": _rate(x[0] for x in rp if x[3]),
                          "by_margin": {str(m): {"kept": sum(1 for x in rp if not x[0] and x[1] >= m),
                                                 "kept_share": sum(1 for x in rp if not x[0] and x[1] >= m) / len(rp),
                                                 "right_among_kept": _rate(x[2] for x in rp if not x[0] and x[1] >= m)}
                                        for m in MARGINS}}
    for flt, form, tau, trim, robust in grid:
        if True:
            full = Reader(L, types, eps, tau, form, flt=flt, nones=nones, true_h=true_h, info=info, trim=trim, robust=robust,
                          dose_seed=ws)
            cell = {"kept": {w: list(v) for w, v in full.kept.items()}, "bands": dict(full.band)}
            th, fn, sz, co, n = 0, 0, 0, 0, 0
            for x in things:
                held = full.held(x["z"])
                n += 1
                th += x["shape"] in held
                fn += any(w in W.SHAPE_WORDS and w != x["shape"] for w in held)
                sz += x["size"] in held
                co += x["colour"] in held
            cell.update({"n": n, "true_hold": th / n if n else None, "false_name": fn / n if n else None,
                         "size_held": sz / n if n else None, "colour_held": co / n if n else None})
            per = {}
            tot_c, tot_n = 0, 0
            for s in shapes:
                loo = Reader(L, types, eps, tau, form, drop=s, flt=flt, nones=nones, true_h=true_h, info=info, trim=trim,
                             robust=robust, dose_seed=ws)
                sel = [x for x in things if x["shape"] == s]
                c = sum(1 for x in sel if not any(w in W.SHAPE_WORDS for w in loo.held(x["z"])))
                per[s] = {"n": len(sel), "correct": c / len(sel) if sel else None}
                tot_c += c; tot_n += len(sel)
            cell["pseudo_novel"] = {"n": tot_n, "correct": tot_c / tot_n if tot_n else None, "per_shape": per}
            cell["trimmed"] = dict(full.trimmed)
            cell["outliers"] = dict(full.outliers)
            out["cells"][f"{flt}:{form}@{tau}" + (f"+t{trim}" if trim else "") + (f"+rb{robust}" if robust else "")] = cell
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", type=int, required=True)
    ap.add_argument("--fit", type=int, default=8000)
    ap.add_argument("--out", default="/data/dev/brain-runs/day0929/fm2b")
    ap.add_argument("--grid", default="full", choices=("full", "dose", "point", "m2b"))
    a = ap.parse_args()
    t0 = time.process_time()
    cfg = brain_cfg()
    d = C.cache_dir(C.RUNS, a.ws, "train")
    C.check_code(d)
    train = C.ScenePercepts(d)
    truth = C.load_truth(d)
    if not (0 < a.fit < len(train)) and not (a.grid == "m2b" and a.fit == len(train)):
        raise SystemExit(f"--fit {a.fit} must leave validation rows (the training stream holds {len(train)})")
    brain = B.Brain(cfg)
    nones: List[Optional[bool]] = []
    for i in range(a.fit):
        lr_ = brain.learn(GA.glance_of(train, i), train.words(i), moment=f"sc{a.ws}t{i:06d}", scene=i, world_seed=a.ws)
        nones.append(lr_["none"])
    brain.ask({"form": "begin", "set": "probe", "test_seed": 0}, None)      # the reading point before a sitting
    L = brain.L
    # the control: tau 0 + soft must BE the brain's own reader, value for value
    law = Reader(L, L.reader["ear"]["types"], cfg["eps"], 0.0, "soft")
    own = L.reader["ear"]["word"]
    diffs = [(w, law.band.get(w), own[w]["band"]) for w in own if own[w]["band"] is not None
             and abs(law.band.get(w, float("nan")) - own[w]["band"]) > 1e-9 * max(1.0, abs(own[w]["band"]))]
    mu_diff = max((float(np.max(np.abs(law.mu[w] - own[w]["mu"]))) for w in own if own[w]["mu"] is not None and w in law.mu),
                  default=None)
    control = {"words_compared": sum(1 for w in own if own[w]["band"] is not None), "band_diffs": diffs, "max_mu_diff": mu_diff}
    things, counts = validation_things(train, truth, a.fit, len(train), L)
    res = {"world_seed": a.ws, "fit": a.fit, "validation": [a.fit, len(train)], "cfg": {k: cfg[k] for k in ("lr", "eps", "young")},
           "young_rule": cfg.get("young_rule"), "mature": L.mature_words(), "control_law_reader": control,
           "validation_counts": counts, "none_at_learning": {str(v): sum(1 for x in nones if x is v) for v in (True, False, None)},
           "A": part_a(brain, truth, a.fit, nones), "B": part_b(brain, things, float(cfg["eps"]), nones, truth, a.grid, a.ws),
           "cpu_s": None}
    res["cpu_s"] = time.process_time() - t0
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / (f"probe-{a.ws}-fit{a.fit}.json" if a.grid == "full" else f"probe-{a.ws}-fit{a.fit}-{a.grid}.json")
    p.write_text(json.dumps(res, indent=1, sort_keys=True, default=GA._np))
    print(f"[probe {a.ws}] wrote {p} · cpu {res['cpu_s']:.1f} s · control: {control['words_compared']} words, "
          f"{len(diffs)} band differences, max |mu diff| {mu_diff}")
    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(main())
