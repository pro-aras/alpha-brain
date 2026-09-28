"""memory.py — T-MEM-1 «THE BRAIN READS ITS MEMORY»: the learner's own STORE, read in the store's own coordinates (the READER
of S1b-1R over the stored raw rows), the ORDER-FREE PIN, the STRONG rule, the GATE's anchors and its OWM projection, the EM
re-attribution, META's per-word drift. LEARNER side: it reads only what the learner itself holds.

edit: Claude (Opus 5.5, T-MEM-1 builder), 2026-09-28 17:17 +0400 — new module, written to docs/brain/memory/PREREG-TMEM1.md (genome-wt-brain3
ce41448, sha 0a87fefc…, final) with CONCLUSION-MEMORY (7cb72ca, co-signed) §2 and the coordinator's rulings on the
builder's declared readings (2026-09-28 17:1x), listed in docs/brain/memory/TMEM1-HANDBACK.md:
  · the store's own coordinates: z = clip((x − m) / s, ±8), m and s the mean and the sample sd (floored at 1e-3) over EVERY
    stored raw row, unweighted, summed in a CANONICAL row order (by the row's word, its raw bytes, its responsibility) — so
    the reader is a function of the multiset of rows and the ORDER-FREE PIN holds exactly;
  · the READER per learned type T (the ear's cover of the mature words): μ_w the responsibility-weighted mean of w's rows,
    Σ_T S1b-1R's pooled covariance about the μ_w, Λ_T = shrunk_inverse(Σ_T, ε) with ε P-ORACLE's; forced naming = argmin of
    d_w (Mahalanobis under w's own type's Λ); pointing = argmax over things of Σ log p(w | z) within type (TypedLDAReader's
    form, equal priors); «none» (for the pollution prints' M2a pair) = the pointed thing lies outside some phrase word's
    band B_w (the weighted 0.90 quantile of d_w over w's own rows);
  · the STRONG rule (no truth): ≥ 20 attributed rows (the argmax-responsibility row of each meeting) whose leave-one-out
    naming agreement (w's mean down-dated by the row, Λ held) is ≥ 0.80; a meeting is SELF-CONSISTENT when its attributed
    row agrees; the anchors = the 8 most recent self-consistent meetings' attributed rows;
  · the GATE = OWM over [z, 1]: each strong word's row update is projected orthogonal to its 8 anchor rows, standardised by
    the learner's CURRENT statistics, so every anchor's logit — and so its loss — is unchanged by the step.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .learners import BAND_Q, CLIP, SD_FLOOR, pick, shrunk_inverse, weighted_quantile
from .pickers import P_CLIP, hyp_probs

STRONG_MIN_ROWS = 20
STRONG_AGREE = 0.80
K_ANCHORS = 8
RISE_TOL = 1e-10            # the rise count's tolerance on an anchor's loss (a float's own noise, declared)


class MemoryError_(Exception):
    pass


# ================================================================================================ the rows
class StoreRows:
    """The learner's store, one ROW per (word, meeting, hypothesis): the word, the raw input (146), the responsibility, the
    storage time (the learner's scene counter at the meeting), the meeting's id (per word, in storage order) and the row's
    hypothesis index within the meeting."""

    def __init__(self, word: Sequence[str], X: np.ndarray, r: np.ndarray, t: np.ndarray, meeting: np.ndarray,
                 hyp: np.ndarray):
        self.word = list(word)
        self.X = np.asarray(X, dtype=np.float64).reshape(len(self.word), -1)
        self.r = np.asarray(r, dtype=np.float64).reshape(-1)
        self.t = np.asarray(t, dtype=np.int64).reshape(-1)
        self.meeting = np.asarray(meeting, dtype=np.int64).reshape(-1)
        self.hyp = np.asarray(hyp, dtype=np.int64).reshape(-1)

    def __len__(self) -> int:
        return len(self.word)

    @classmethod
    def from_learner(cls, L, resp: Optional[Dict[Tuple[str, int], np.ndarray]] = None) -> "StoreRows":
        """Every stored meeting of every word, as rows. `resp` (A-READ-EM's road) replaces a meeting's responsibilities."""
        word, X, r, t, mt, hy = [], [], [], [], [], []
        for j, w in enumerate(L.words):
            for m, (xs, rs, ts) in enumerate(zip(L.store_x[j], L.store_r[j], L.store_t[j])):
                rr = resp.get((w, m), rs) if resp is not None else rs
                for h in range(xs.shape[0]):
                    word.append(w)
                    X.append(xs[h])
                    r.append(float(rr[h]))
                    t.append(int(ts))
                    mt.append(m)
                    hy.append(h)
        d = L.dim
        return cls(word, np.asarray(X).reshape(-1, d) if X else np.zeros((0, d)), np.asarray(r), np.asarray(t, dtype=np.int64),
                   np.asarray(mt, dtype=np.int64), np.asarray(hy, dtype=np.int64))

    def take(self, idx: Sequence[int]) -> "StoreRows":
        idx = np.asarray(idx, dtype=np.int64)
        return StoreRows([self.word[i] for i in idx], self.X[idx], self.r[idx], self.t[idx], self.meeting[idx], self.hyp[idx])

    def canonical(self) -> "StoreRows":
        """The rows in the canonical order: by word, then the raw row's bytes, then the responsibility — a function of the
        multiset alone, so a shuffled store rebuilds bit for bit."""
        keys = sorted(range(len(self)), key=lambda i: (self.word[i], self.X[i].tobytes(), float(self.r[i])))
        return self.take(keys)

    def window(self, t_min: int) -> "StoreRows":
        """TIME-WINDOW's store: the rows stored at a scene counter > t_min."""
        return self.take([i for i in range(len(self)) if self.t[i] > t_min])

    def permuted_labels(self, rng: np.random.Generator) -> "StoreRows":
        """The null: the word labels shuffled across rows (each row keeps its raw input and responsibility)."""
        perm = rng.permutation(len(self))
        return StoreRows([self.word[i] for i in perm], self.X, self.r, self.t, self.meeting, self.hyp)

    def shuffled(self, rng: np.random.Generator) -> "StoreRows":
        """THE ORDER-FREE PIN's shuffle: the rows reordered, each keeping its word, responsibility and raw input."""
        return self.take(rng.permutation(len(self)))


# ================================================================================================ the READER
class StoreReader:
    """S1b-1R's READER built over the store's rows in the store's OWN coordinates (module doc)."""

    def __init__(self, rows: StoreRows, types: Sequence[Sequence[str]], eps: float):
        rows = rows.canonical()
        self.rows, self.eps = rows, float(eps)
        n = len(rows)
        if n == 0:
            raise MemoryError_("an empty store has no reader")
        self.m = rows.X.sum(axis=0) / n
        dev = rows.X - self.m[None, :]
        self.s = np.maximum(np.sqrt((dev * dev).sum(axis=0) / max(n - 1, 1)), SD_FLOOR) if n > 1 else np.full(rows.X.shape[1], SD_FLOOR)
        self.Z = self.std(rows.X)
        present = set(rows.word)
        self.types = [tuple(w for w in T if w in present) for T in types]
        self.types = [T for T in self.types if T]
        self.type_of: Dict[str, int] = {w: k for k, T in enumerate(self.types) for w in T}
        self.mu: Dict[str, np.ndarray] = {}
        self.sum_rz: Dict[str, np.ndarray] = {}
        self.sum_r: Dict[str, float] = {}
        self.idx: Dict[str, np.ndarray] = {}
        self.lam: List[np.ndarray] = []
        for k, T in enumerate(self.types):
            num = np.zeros((self.Z.shape[1], self.Z.shape[1]))
            den = 0.0
            for w in T:
                ii = np.asarray([i for i in range(n) if rows.word[i] == w], dtype=np.int64)
                self.idx[w] = ii
                rr = rows.r[ii]
                Zw = self.Z[ii]
                self.sum_rz[w] = (rr[:, None] * Zw).sum(axis=0)
                self.sum_r[w] = float(rr.sum())
                if self.sum_r[w] <= 0:
                    raise MemoryError_(f"word {w!r} holds no responsibility")
                self.mu[w] = self.sum_rz[w] / self.sum_r[w]
                D = Zw - self.mu[w][None, :]
                num += (D * rr[:, None]).T @ D
                den += self.sum_r[w]
            self.lam.append(shrunk_inverse(num / den, self.eps))
        self.words = [w for T in self.types for w in T]
        self.band: Dict[str, float] = {}
        for w in self.words:
            d = self._d_rows(self.Z[self.idx[w]], w)
            q = weighted_quantile(d, self.rows.r[self.idx[w]], BAND_Q)
            self.band[w] = float("inf") if q is None else float(q)

    # -- coordinates and distances --------------------------------------------------------------
    def std(self, X: np.ndarray) -> np.ndarray:
        return np.clip((np.atleast_2d(np.asarray(X, dtype=np.float64)) - self.m[None, :]) / self.s[None, :], -CLIP, CLIP)

    def _d_rows(self, Z: np.ndarray, w: str, mu: Optional[np.ndarray] = None) -> np.ndarray:
        lam = self.lam[self.type_of[w]]
        E = np.atleast_2d(Z) - (self.mu[w] if mu is None else mu)[None, :]
        return np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", E, lam, E), 0.0))

    def dist(self, Xraw: np.ndarray, words: Sequence[str]) -> np.ndarray:
        """(H, len(words)) d_w of each raw row; +inf for a word the reader does not hold."""
        Z = self.std(Xraw)
        out = np.full((Z.shape[0], len(words)), np.inf)
        for c, w in enumerate(words):
            if w in self.type_of:
                out[:, c] = self._d_rows(Z, w)
        return out

    def log_post(self, Xraw: np.ndarray, w: str) -> np.ndarray:
        """log p(w | z) within w's learned type (the discriminant zᵀΛμ − ½ μᵀΛμ, equal priors — TypedLDAReader's form)."""
        k = self.type_of[w]
        lam, T = self.lam[k], self.types[k]
        Z = self.std(Xraw)
        Mu = np.stack([self.mu[v] for v in T])
        S = Z @ (Mu @ lam).T - 0.5 * np.einsum("kj,jl,kl->k", Mu, lam, Mu)[None, :]
        mx = S.max(axis=1, keepdims=True)
        lse = mx + np.log(np.exp(S - mx).sum(axis=1, keepdims=True))
        return (S - lse)[:, T.index(w)]

    # -- answering ------------------------------------------------------------------------------
    def name_forced(self, xraw: np.ndarray, type_words: Sequence[str]) -> Optional[str]:
        cand = [w for w in type_words if w in self.type_of]
        if not cand:
            return None
        d = self.dist(np.atleast_2d(xraw)[:1], cand)[0]
        return cand[int(np.argmin(d))]

    def names(self, Xraw: np.ndarray, type_words: Sequence[str]) -> Tuple[List[Optional[str]], np.ndarray]:
        """Batched forced naming over one grader type: the names and the margins (the second-smallest d − the smallest;
        +inf with one candidate) — THE ORDER-FREE PIN compares both."""
        cand = [w for w in type_words if w in self.type_of]
        n = np.atleast_2d(Xraw).shape[0]
        if not cand:
            return [None] * n, np.full(n, np.nan)
        D = self.dist(Xraw, cand)
        k = np.argmin(D, axis=1)
        if D.shape[1] > 1:
            srt = np.sort(D, axis=1)
            margin = srt[:, 1] - srt[:, 0]
        else:
            margin = np.full(n, np.inf)
        return [cand[int(i)] for i in k], margin

    def answer_point(self, Xraw: np.ndarray, phrase: Sequence[str], rng: np.random.Generator) -> Dict[str, object]:
        unheard = [w for w in phrase if w not in self.type_of]
        if unheard:
            return {"point": None, "none": None, "best": None, "unheard": unheard}
        s = np.sum([self.log_post(Xraw, w) for w in phrase], axis=0)
        k = pick(s, rng, "max")
        Z = self.std(np.atleast_2d(Xraw)[k:k + 1])
        none = any(float(self._d_rows(Z, w)[0]) > self.band[w] for w in dict.fromkeys(phrase))
        return {"point": int(k), "none": bool(none), "best": float(s[k]), "scores": [float(v) for v in s]}

    # -- the STRONG rule, the anchors -----------------------------------------------------------------
    def attributed(self, w: str) -> List[int]:
        """Row indices (into self.rows) of w's ATTRIBUTED rows: per meeting, its argmax-responsibility row (the earlier
        hypothesis on a tie)."""
        ii = self.idx.get(w)
        if ii is None:
            return []
        best: Dict[int, Tuple[float, int, int]] = {}
        for i in ii:
            m = int(self.rows.meeting[i])
            key = (-float(self.rows.r[i]), int(self.rows.hyp[i]), int(i))
            if m not in best or key < best[m]:
                best[m] = key
        return [v[2] for _m, v in sorted(best.items())]

    def loo_agree(self, w: str, rows: Sequence[int]) -> np.ndarray:
        """Per attributed row: does the reader with w's mean DOWN-DATED by the row (Λ held) name the row as w among w's
        type's words?"""
        T = self.types[self.type_of[w]]
        out = np.zeros(len(rows), dtype=bool)
        others = [v for v in T if v != w]
        for c, i in enumerate(rows):
            z = self.Z[i:i + 1]
            rr = float(self.rows.r[i])
            den = self.sum_r[w] - rr
            if den <= 0:
                continue
            mu_loo = (self.sum_rz[w] - rr * self.Z[i]) / den
            dw = float(self._d_rows(z, w, mu_loo)[0])
            do = [float(self._d_rows(z, v)[0]) for v in others]
            out[c] = all(dw < x for x in do)
        return out

    def strong(self) -> Dict[str, Dict[str, object]]:
        """The STRONG words (no truth): ≥ 20 attributed rows AND their LOO agreement ≥ 0.80; with each word's
        self-consistent meetings (in storage order)."""
        out = {}
        for w in self.words:
            att = self.attributed(w)
            if len(att) < STRONG_MIN_ROWS:
                continue
            ok = self.loo_agree(w, att)
            rate = float(ok.mean()) if len(ok) else 0.0
            if rate >= STRONG_AGREE:
                out[w] = {"n": len(att), "agree": rate, "consistent": [att[c] for c in range(len(att)) if ok[c]]}
        return out

    def anchors(self, strong: Dict[str, Dict[str, object]], k: int = K_ANCHORS) -> Dict[str, np.ndarray]:
        """Per strong word: the RAW rows of its k most RECENT self-consistent meetings' attributed rows."""
        out = {}
        for w, s in strong.items():
            rows = sorted(s["consistent"], key=lambda i: (int(self.rows.t[i]), int(self.rows.meeting[i])))[-k:]
            out[w] = self.rows.X[np.asarray(rows, dtype=np.int64)]
        return out

    def random_anchors(self, strong: Dict[str, Dict[str, object]], rng: np.random.Generator, k: int = K_ANCHORS) -> Dict[str, np.ndarray]:
        """The null: k meetings drawn uniformly (without replacement) from the strong word's OWN attributed rows."""
        out = {}
        for w in strong:
            att = self.attributed(w)
            pick_ = rng.choice(len(att), size=min(k, len(att)), replace=False)
            out[w] = self.rows.X[np.asarray([att[int(c)] for c in sorted(pick_)], dtype=np.int64)]
        return out

    # -- the EM re-attribution (A-READ-EM) ----------------------------------------------------------
    def em_responsibilities(self) -> Dict[Tuple[str, int], np.ndarray]:
        """One E-step: every stored meeting of a reader word re-attributed, r_h ∝ exp(−½ d_w(z_h)²) over its rows."""
        out: Dict[Tuple[str, int], List[Tuple[int, float]]] = {}
        for w in self.words:
            ii = self.idx[w]
            d = self._d_rows(self.Z[ii], w)
            for i, dv in zip(ii, d):
                out.setdefault((w, int(self.rows.meeting[i])), []).append((int(self.rows.hyp[i]), -0.5 * float(dv) ** 2))
        res = {}
        for key, v in out.items():
            v = sorted(v)
            lg = np.array([x for _h, x in v])
            e = np.exp(lg - lg.max())
            full = np.zeros(max(h for h, _x in v) + 1)
            for (h, _x), p in zip(v, e / e.sum()):
                full[h] = p
            res[key] = full
        return res


# ================================================================================================ the GATE (OWM)
def owm_project(u: np.ndarray, A: np.ndarray) -> np.ndarray:
    """u projected onto the orthogonal complement of the row space of A (k × d): u − Aᵀ (A Aᵀ)⁺ A u."""
    if A.shape[0] == 0:
        return u
    coef = np.linalg.pinv(A @ A.T) @ (A @ u)
    return u - A.T @ coef


class Gate:
    """The per-update projection (T-MEM-1's GATE): installed as RWLearner.train_scene's `project` hook. For every STRONG
    word s with anchors (raw rows), its update [ΔV_s ‖ Δb_s] is projected orthogonal to [z_a ‖ 1] for its anchors, z_a
    standardised by the learner's CURRENT statistics (after the scene's own observation — the statistics the step uses).
    Every step's anchor logits are read before and after under that same standardisation: a step on which any anchor's
    loss rose (by > RISE_TOL) is counted (the null is 0)."""

    def __init__(self, anchors: Dict[str, np.ndarray]):
        self.anchors = {w: np.atleast_2d(a) for w, a in anchors.items()}
        self.steps = 0
        self.rises = 0
        self.max_rise = 0.0

    def ranks(self, L) -> Dict[str, object]:
        per = {}
        stack = []
        for w, a in self.anchors.items():
            A = np.hstack([L.stats.standardise(a), np.ones((a.shape[0], 1))])
            per[w] = int(np.linalg.matrix_rank(A))
            stack.append(A)
        return {"per_word": per, "stacked": int(np.linalg.matrix_rank(np.vstack(stack))) if stack else 0}

    def __call__(self, L, upd: np.ndarray, db: np.ndarray):
        self.steps += 1
        rose = False
        for w, a in self.anchors.items():
            j = L.index.get(w)
            if j is None:
                continue
            A = np.hstack([L.stats.standardise(a), np.ones((a.shape[0], 1))])
            u = np.concatenate([upd[j], [db[j]]])
            u2 = owm_project(u, A)
            upd[j], db[j] = u2[:-1], u2[-1]
            before = A @ np.concatenate([L.V[j], [L.b[j]]])
            after = A @ np.concatenate([L.V[j] + upd[j], [L.b[j] + db[j]]])
            rise = float(np.max(np.logaddexp(0.0, -after) - np.logaddexp(0.0, -before)))   # −log σ(logit) per anchor, y = 1
            if rise > RISE_TOL:
                rose = True
                self.max_rise = max(self.max_rise, rise)
        self.rises += int(rose)
        return upd, db


# ================================================================================================ META's drift
def word_terms(learner, windows: Sequence[object], vocab: Sequence[str]) -> Dict[str, float]:
    """Each word's OWN term of the held-window loss: −Σ [y log P + (1 − y) log(1 − P)] over every window scene of every
    room (pickers.window_loss's arithmetic, per word, summed over the rooms' windows)."""
    tot = np.zeros(len(vocab))
    for ws in windows:
        p = hyp_probs(learner, ws.X, ws.vocab)
        for i in range(ws.n):
            a, b = int(ws.starts[i]), int(ws.starts[i + 1])
            P = 1.0 - np.prod(1.0 - p[a:b], axis=0) if b > a else np.zeros(len(ws.vocab))
            P = np.clip(P, P_CLIP, 1.0 - P_CLIP)
            y = ws.Y[i]
            tot -= y * np.log(P) + (1.0 - y) * np.log(1.0 - P)
    return {w: float(tot[c]) for c, w in enumerate(vocab)}


def draw_by_weight(weights: Dict[str, float], rng: np.random.Generator, R: int, eligible: Sequence[str]) -> List[str]:
    """R words drawn ∝ the POSITIVE weight among the eligible words (with replacement); none positive → uniform over the
    eligible words (declared, ruled)."""
    el = [w for w in eligible]
    if not el:
        return []
    w = np.array([max(float(weights.get(x, 0.0)), 0.0) for x in el])
    if w.sum() <= 0:
        return [el[int(rng.integers(len(el)))] for _ in range(R)]
    p = w / w.sum()
    return [el[int(rng.choice(len(el), p=p))] for _ in range(R)]
