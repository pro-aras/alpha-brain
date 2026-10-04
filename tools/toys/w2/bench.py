"""tools/toys/w2/bench.py — PREREG-W2 §3-§5: the bench runner (the arms re-read and the marks' raw figures).

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 03:1x +0400 — new file; law
docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 (the bench), §4 (the gates), §5 (the marks). The law's §11 pilot shape:
one CONT-shaped arms pass over the slice (the pilot's measured-first job); the graded shape: 5 arms + k_null dealt + the
readings per bench seed.

generation(bl2, seed): the full assembly + the global reference census + the mentor rows per canvas (the ON tape's
content and the arms' stream are the SAME generation, asserted by the rows' hash). arms_bench(bl2, seed, lo, hi,
train_end, k_null): the slice's stream (SM.build), the feeds, the arms (CONT, SHUF x k_null, NOSTATE, BLIND, ORACLE,
CONST), and the marks' raw figures (M-BIND's AUCs and C_read with the NOT-GRADABLE rule, the dealt diag AUCs for
M-CONTINGENT (ii)'s per-seed self-centred flatness and the S6 guard's three-seed table, M-NOHARM (a)/(b),
M-TRUE/M-ATTRIB/M-JOINT/M-SELFVOICE/M-CONTINGENT (i)'s counts — every figure with its n and presence counts).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

from brain.scene import learners as Lr
from brain.world.seeds import substream
from creature.senses import mentor as M
from tools.toys.w2 import arms as A
from tools.toys.w2 import census as C
from tools.toys.w2 import feed as F
from tools.toys.w2 import grade as G
from tools.toys.w2 import key as K
from tools.toys.w2 import record as R
from tools.toys.w2 import state as ST
from tools.toys.w2 import stream as SM

LABELS = ("doubt", "young", "ask_prev")
WORDS = ("unsure", "fresh", "asked")
WORD_OF = dict(zip(LABELS, WORDS))


def generation(bl2: Path, seed: int, hi: Optional[int] = None):
    """The full assembly + census + mentor rows for every canvas [0, hi) (the shared generation; the mirror tokens
    carried by the two-call determinism of stream.build)."""
    cs = R.assemble(bl2, 0, hi)
    census = C.meeting_counts([c.words for c in cs])
    by_moment: Dict[str, list] = {}
    for pos, c in enumerate(cs):
        say = (c.turn.get("say") or {}).get("words") if c.turn.get("say") else None
        ask_target = SM._ask_target(c)
        mc = M.Canvas(moment=c.moment, things=c.things, fix=c.fix,
                      state={"doubt": 0, "young": 0, "ask_prev": 0},
                      say=say, ask_target=ask_target, order=c.order)
        ref = M._referent_pick(mc, substream(seed, f"w2:mentor:{c.order}"))
        base = M.mentor_rows(mc, substream(seed, f"w2:mentor:{c.order}"))
        s = ST.state_of(cs, census, pos, ref)
        rows = M.mentor_rows(M.Canvas(moment=c.moment, things=c.things, fix=c.fix,
                                      state={"doubt": int(s[0]), "young": int(s[1]), "ask_prev": int(s[2])},
                                      say=say, ask_target=ask_target, order=c.order),
                             substream(seed, f"w2:mentor:{c.order}"))
        if rows:
            by_moment[c.moment] = rows
    return cs, census, by_moment


def _score(L, mats_test):
    """The full scene-score matrix (n_test, n_words); callers index a word by its global index in L.index."""
    return A.score_window(L, mats_test)


def _labels(stream_states, lo_pos, hi_pos):
    return {l: np.array([int(s[i]) for s in stream_states[lo_pos:hi_pos]], dtype=int) for i, l in enumerate(LABELS)}


def arms_bench(bl2: Path, seed: int, lo: int = 250, hi: int = 20250, train_end: int = 18250, k_null: int = 100,
               out: Optional[Path] = None) -> Dict[str, object]:
    """One bench seed's arms re-read over the slice [lo, hi): TRAIN [lo, train_end), TEST [train_end, hi)."""
    cs, census, by_moment = generation(bl2, seed, hi=hi)
    stream = SM.build(cs, census, seed, lo, hi)
    n_tr = train_end - lo
    n_te = hi - train_end
    utts = [SM.words_of(u) for u in stream.utterances]
    tr_words, te_words = utts[:n_tr], utts[n_tr:]
    Xs_tr = [cs[lo + t].X for t in range(n_tr)]
    states = stream.states
    mats_tr, stats_tr = F.build(Xs_tr, states[:n_tr], "S")
    matsN_tr, _ = F.build(Xs_tr, states[:n_tr], "N")
    Xs_te = [cs[train_end + t].X for t in range(n_te)]
    labs = _labels(states, n_tr, n_tr + n_te)
    labels = {l: labs[l] for l in LABELS}
    # ---- CONT ----
    Lc = A.train_arm(mats_tr, tr_words, seed)
    mats_te_c, _ = F.build(Xs_te, states[n_tr:], "S", window="test", frozen_mean=Lc.stats.mean)
    sc_cont = _score(Lc, mats_te_c)
    # ---- NOSTATE ----
    Ln = A.train_arm(matsN_tr, tr_words, seed)
    mats_te_n, _ = F.build(Xs_te, states[n_tr:], "N", window="test", frozen_mean=Ln.stats.mean)
    sc_n = _score(Ln, mats_te_n)
    # ---- ORACLE (the ceiling, under CONT's final standardiser) ----
    cols = [Lc.index[w] for w in WORDS if w in Lc.index]
    oracle = {}
    if cols:
        Z_all = np.concatenate([Lc.stats.standardise(M) for M in mats_tr], axis=0)
        for j, w in enumerate(WORDS):
            if w not in Lc.index:
                continue
            l = LABELS[WORDS.index(w)]
            li = LABELS.index(l)
            y = np.concatenate([np.concatenate([np.zeros(int(cs[lo + t].X.shape[0])), [float(states[t][li])]]) for t in range(n_tr)])
            fit = A.oracle_fit(Z_all, y, ridge=1e-3, max_iter=30)
            sco = A.oracle_scores(Lc.stats, fit["v"], fit["b"], mats_te_c)
            oracle[w] = {"c_read": G.auc(sco, labels[l]), "n_iter": fit["n_iter"], "converged": fit["converged"],
                         "rows_fed": fit["rows_fed"], "rows_total": int(Z_all.shape[0]),
                         "scores": sco}
    # ---- SHUF (the dealt mirror) and CONST ----
    dealt_diag: Dict[str, List[float]] = {w: [] for w in WORDS}
    naming_dealt: List[float] = []
    cont_aucs = {w: (G.auc(sc_cont[:, list(Lc.index).index(w)], labels[LABELS[WORDS.index(w)]]) if w in Lc.index else None) for w in WORDS}
    word_cols_c = {w: list(Lc.index).index(w) for w in WORDS if w in Lc.index}
    for k in range(1, k_null + 1):
        perm = Lr.nshuf_permutation(substream(seed, f"w2:deal:{k}"), n_tr)
        du = SM.deal_mirror(stream.utterances[:n_tr], perm)
        Lk = A.train_arm(mats_tr, [SM.words_of(u) for u in du], seed)
        mats_te_k, _ = F.build(Xs_te, states[n_tr:], "S", window="test", frozen_mean=Lc.stats.mean)
        sc_k = _score(Lk, mats_te_k)
        cols_k = A.state_word_columns(Lk)
        for w in WORDS:
            if w in Lk.index:
                dealt_diag[w].append(G.auc(sc_k[:, list(Lk.index).index(w)], labels[LABELS[WORDS.index(w)]]))
            else:
                dealt_diag[w].append(float("nan"))
        if k <= 3:
            naming_dealt.append(_naming_acc(Lk, cs, stream, train_end, n_te, mats_te_k))
    # ---- BLIND ----
    bperm = Lr.nshuf_permutation(substream(seed, "w2:blind"), n_tr)
    srows = [states[t] for t in bperm]
    matsB_tr, _ = F.build(Xs_tr, [np.asarray(s) for s in srows], "S")
    Lb = A.train_arm(matsB_tr, tr_words, seed)
    mats_te_b, _ = F.build(Xs_te, states[n_tr:], "S", window="test", frozen_mean=Lc.stats.mean)
    sc_b = _score(Lb, mats_te_b)
    blind = {w: (G.auc(sc_b[:, list(Lb.index).index(w)], labels[LABELS[WORDS.index(w)]]) if w in Lb.index else None) for w in WORDS}
    const = {w: G.auc(A.const_scores(float(np.mean([w in u["mirror"] for u in stream.utterances[:n_tr]])), n_te),
                      labels[LABELS[WORDS.index(w)]]) for w in WORDS}
    m1 = {}
    for w in WORDS:
        if w not in Lc.index:
            continue
        l = LABELS[WORDS.index(w)]
        m1[w] = G.m1_rule(cont_aucs[w], oracle.get(w, {}).get("c_read", float("nan")), [x for x in dealt_diag[w] if x == x])
    naming = _naming_pair(Lc, Ln, cs, stream, train_end, n_te, mats_te_c, mats_te_n)
    proto = _proto_home(Lc, mats_tr, n_tr)
    rec = {"seed": seed, "slice": [lo, hi], "train_end": train_end, "n_train": n_tr, "n_test": n_te,
           "test_n": {l: {"pos": int(labels[l].sum()), "neg": int(n_te - labels[l].sum())} for l in LABELS},
           "stream": {"n_utterances": len(stream.utterances), "n_referent_readbacks": stream.n_referent_readbacks,
                      "mirror_counts": {w: sum(w in u["mirror"] for u in stream.utterances) for w in WORDS}},
           "cont": {"auc": cont_aucs, "naming": naming},
           "nostate": {"auc": {w: (G.auc(sc_n[:, list(Ln.index).index(w)], labels[LABELS[WORDS.index(w)]]) if w in Ln.index else None) for w in WORDS},
                        "naming": naming.get("nostate")},
           "oracle": {w: {k: v for k, v in o.items() if k != "scores"} for w, o in oracle.items()},
           "dealt_diag": dealt_diag, "naming_dealt": naming_dealt, "blind": blind, "const": const, "m1": m1,
           "proto_home": proto,
           "gradability": _gradability(labels, stream, n_tr, n_te, Lc, oracle,
                                       {w: sum(w in u["mirror"] for u in stream.utterances[:n_tr]) for w in WORDS})}
    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "reading.json").write_text(json.dumps(_jsonable(rec), indent=1, sort_keys=True), encoding="utf-8")
    return rec


def _gradability(labels, stream, n_tr, n_te, Lc, oracle, mirror_counts):
    out = {}
    for w in WORDS:
        l = LABELS[WORDS.index(w)]
        pos = int(labels[l].sum())
        said = int(mirror_counts.get(w, 0))
        out[w] = {"pos_test": pos, "c_read": oracle.get(w, {}).get("c_read"), "said_train": said,
                  "gradable": None}
    return out


def _naming_acc(L, cs, stream, train_end, n_te, mats_te, lo: int = 250) -> float:
    """The share of TEST canvases where the best-scored trained name of the LEADING row is one TRUE of the leading thing
    (T-L4 M4(a)'s comparison of maxima, G.naming_correct — never an argmax over the lexicon)."""
    vocab = [w for w in L.words if w in K.SHAPES or w in K.COLOURS or w in K.SIZES]
    if not vocab:
        return float("nan")
    cols = [L.index[w] for w in vocab]
    ok = 0
    n = 0
    for t in range(n_te):
        c = cs[train_end + t]
        ref = stream.referents[(train_end - lo) + t] if (train_end - lo) + t < len(stream.referents) else None
        lead_hyp, lead_word = ST.lead(c, ref)
        if lead_hyp is None or lead_hyp >= mats_te[t].shape[0]:
            continue
        thing = None
        if ref is not None:
            thing = c.things[ref]
        else:
            # the turn's leading hyp's thing: the truth thing under the hyp's fixation cells
            cells = {tuple(c.fix[m]) for m in c.hyps[lead_hyp]} if lead_hyp < len(c.hyps) else set()
            best, best_n = None, 0
            for i, th in enumerate(c.things):
                nn = M.fixation_hits(th, [list(x) for x in cells])
                if nn > best_n:
                    best, best_n = i, nn
            thing = c.things[best] if best is not None else None
        if thing is None:
            continue
        P = A.TA.row_probs(L, mats_te[t])
        mask = np.array([M.word_true_of(v, thing) for v in vocab], dtype=bool)
        n += 1
        ok += int(G.naming_correct(P[lead_hyp, cols], mask))
    return float(ok / n) if n else float("nan")


def _naming_pair(Lc, Ln, cs, stream, train_end, n_te, mats_te_c, mats_te_n, lo: int = 250) -> Dict[str, object]:
    acc_c = _naming_acc(Lc, cs, stream, train_end, n_te, mats_te_c, lo)
    acc_n = _naming_acc(Ln, cs, stream, train_end, n_te, mats_te_n, lo)
    return {"cont": acc_c, "nostate": acc_n, "n": n_te,
            "gradable": bool(acc_n == acc_n and acc_n >= 0.90),
            "pass": bool(acc_c == acc_c and acc_n == acc_n and acc_c >= acc_n - 0.02)}


def _proto_home(L, mats_tr, n_tr) -> Dict[str, object]:
    """The mentor world's own words' first meetings: the row each was stored on (the state row's index = n X rows)."""
    out = {}
    for w in ("alpha", "sees", "does", "not", "see", "unsure", "fresh", "asked"):
        j = L.index.get(w)
        if j is None or not L.store_x[j]:
            out[w] = {"present": False}
            continue
        stored = L.store_x[j][0][0]
        t = int(L.store_t[j][0]) - 1
        n_x = mats_tr[t].shape[0] - 1
        on_state = bool(np.array_equal(stored, mats_tr[t][n_x]))
        out[w] = {"present": True, "on_state_row": on_state, "t": t}
    n_on = sum(1 for v in out.values() if v.get("on_state_row"))
    n_present = sum(1 for v in out.values() if v.get("present"))
    return {"words": out, "n_on_state": n_on, "n_present": n_present, "n": 8, "smallest_gap": 10.0 / 8}


def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o
