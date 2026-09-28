"""learners.py — S1a's learners and the arms' feeds (PREREG-R3-TONIGHT §S1a «The learner A-RW», «Arms»).

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:10 +0400 — new module. Constants are the PREREG's; the one-line READINGS of what
the PREREG leaves open are marked «declared» here and listed in docs/brain/r3/S1A-HANDBACK.md.

THE FENCE: this module imports numpy, the standard library and brain.scene.slda only. It never imports the world, the
cache's truth reader or the marks (tests/brain/scene/test_truth_fence.py, with a planted offender). An oracle arm's
referent arrives as an INDEX ARGUMENT from the caller (run.py), which is the only place truth meets a learner.

  RWLearner   A-RW (T1): per word a logistic unit on the standardised [144 ‖ y/16, x/16] thing input, noisy-OR over the
              things in view, the delta rule with PROPORTIONAL responsibility, a prototype and a band per word, the
              episodic write for a new word. `oracle=True` is P-ORACLE-RW: A-RW's own code with a said word's
              responsibility 1 on the referent the caller marks (one difference).
  LDAReader   P-ORACLE / ORACLE-TRUTH: the streaming LDA reader (slda.StreamingLDA, one type-blind reader over every word
              as a class) on the 144 features, fed each said word with its referent marked; its answers read the
              per-word Mahalanobis distances under the shared Λ, with bands calibrated conformally at 0.90 on its
              training things.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .slda import StreamingLDA

# ------------------------------------------------------------------------------------------------ the PREREG's constants
LR = 0.1                      # v_w += 0.1 · e_w · r_t · x_t ; b_w += 0.1 · e_w · r_t
LR_GRID = (0.03, 0.1, 0.3)    # the FALLBACK, chosen on the toy's own seed only
SD_FLOOR = 1e-3               # the running sd floored at 1e-3
CLIP = 8.0                    # standardised values clipped at ±8
POS_SCALE = 16.0              # x = [144 numbers ‖ y/16, x/16]
BAND_Q = 0.90                 # a word's band: the 0.90 quantile of its things' distances to its prototype
CONFORMAL = 0.90              # τ_point, τ_word, P-ORACLE's bands: the conformal 0.90 thresholds
P_FROM_MEETING = 3            # fewer than 3 meetings → answers by prototype and band; from the 3rd on, by p_w
EPS_GRID = (1e-4, 1e-3, 1e-2, 3e-2, 1e-1, 3e-1)   # R49's ε grid (probe_shrink), chosen on the toy seed only
RW_DIM = 146


# ------------------------------------------------------------------------------------------------ small pieces
def rw_input(feat: np.ndarray, pos: Tuple[float, float]) -> np.ndarray:
    """x = [144 numbers ‖ y/16, x/16] (unstandardised)."""
    return np.concatenate([np.asarray(feat, dtype=np.float64), [pos[0] / POS_SCALE, pos[1] / POS_SCALE]])


def log_sigmoid(z: np.ndarray) -> np.ndarray:
    """log σ(z), stable: −softplus(−z)."""
    z = np.asarray(z, dtype=np.float64)
    return -np.logaddexp(0.0, -z)


def sigmoid(z: np.ndarray) -> np.ndarray:
    return np.exp(log_sigmoid(z))


def conformal_lower(scores: Sequence[float], level: float = CONFORMAL) -> Optional[float]:
    """Split-conformal threshold for «accept when score ≥ τ» at coverage `level`: τ = the (n − k + 1)-th smallest score,
    k = ⌈(n + 1) · level⌉. None when k > n (too few scores to calibrate: n < 9 at 0.90)."""
    a = np.sort(np.asarray(list(scores), dtype=np.float64))
    n = a.size
    k = int(math.ceil((n + 1) * level - 1e-12))
    if n == 0 or k > n:
        return None
    return float(a[n - k])


def conformal_upper(dists: Sequence[float], level: float = CONFORMAL) -> Optional[float]:
    """Split-conformal threshold for «accept when d ≤ q» at coverage `level`: q = the k-th smallest, k = ⌈(n + 1) · level⌉.
    None when k > n."""
    a = np.sort(np.asarray(list(dists), dtype=np.float64))
    n = a.size
    k = int(math.ceil((n + 1) * level - 1e-12))
    if n == 0 or k > n:
        return None
    return float(a[k - 1])


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> Optional[float]:
    """The smallest value whose cumulative weight reaches q · total (declared: the responsibility-weighted quantile)."""
    values = np.asarray(values, dtype=np.float64)
    weights = np.asarray(weights, dtype=np.float64)
    tot = float(weights.sum())
    if values.size == 0 or tot <= 0.0:
        return None
    o = np.argsort(values, kind="stable")
    cw = np.cumsum(weights[o])
    i = int(np.searchsorted(cw, q * tot - 1e-12 * tot, side="left"))
    return float(values[o][min(i, values.size - 1)])


def pick(scores: np.ndarray, rng: np.random.Generator, best: str = "max") -> int:
    """argmax (or argmin) with ties broken uniformly at random by the item's own generator — never by hypothesis order.
    Declared: the generator is drawn from only when there IS a tie."""
    s = np.asarray(scores, dtype=np.float64)
    b = np.max(s) if best == "max" else np.min(s)
    ties = np.flatnonzero(s == b)
    if ties.size == 1:
        return int(ties[0])
    return int(ties[int(rng.integers(ties.size))])


class RunningStandardiser:
    """Per-unit running mean and sd (Welford; declared: the sample sd √(M2/(n−1)), floored at 1e-3; n < 2 → the floor),
    values clipped at ±8. Declared order: a training scene's things are OBSERVED first, then standardised; a test thing
    is standardised by the statistics as they stand (never observed)."""

    def __init__(self, dim: int):
        self.n = 0
        self.mean = np.zeros(dim)
        self.m2 = np.zeros(dim)

    def observe(self, X: np.ndarray) -> None:
        for x in np.atleast_2d(X):
            self.n += 1
            d = x - self.mean
            self.mean += d / self.n
            self.m2 += d * (x - self.mean)

    def sd(self) -> np.ndarray:
        if self.n < 2:
            return np.full_like(self.mean, SD_FLOOR)
        return np.maximum(np.sqrt(self.m2 / (self.n - 1)), SD_FLOOR)

    def standardise(self, X: np.ndarray) -> np.ndarray:
        return np.clip((np.atleast_2d(X) - self.mean) / self.sd(), -CLIP, CLIP)


# ================================================================================================ A-RW (and P-ORACLE-RW)
class RWLearner:
    def __init__(self, lr: float = LR, oracle: bool = False, dim: int = RW_DIM):
        self.lr = float(lr)
        self.oracle = bool(oracle)
        self.dim = dim
        self.stats = RunningStandardiser(dim)
        self.words: List[str] = []
        self.index: Dict[str, int] = {}
        self.V = np.zeros((0, dim))
        self.b = np.zeros(0)
        self.meetings = np.zeros(0, dtype=np.int64)
        self.proto_sum = np.zeros((0, dim))
        self.proto_w = np.zeros(0)
        self.store_z: List[List[np.ndarray]] = []      # per word: its things' standardised inputs (per meeting)
        self.store_r: List[List[np.ndarray]] = []      # per word: their responsibilities
        self.episodic_band: List[float] = []
        self.scenes = 0
        self.skipped_said = 0                            # P-ORACLE-RW: scenes whose referent had no hypothesis
        self.tau_point: Optional[float] = None
        self.tau_word: Dict[str, Optional[float]] = {}
        self.calib_n: Dict[str, int] = {}

    # -- words ---------------------------------------------------------------------------------
    def _add_word(self, w: str) -> int:
        i = len(self.words)
        self.words.append(w)
        self.index[w] = i
        self.V = np.vstack([self.V, np.zeros((1, self.dim))])
        self.b = np.append(self.b, 0.0)
        self.meetings = np.append(self.meetings, 0)
        self.proto_sum = np.vstack([self.proto_sum, np.zeros((1, self.dim))])
        self.proto_w = np.append(self.proto_w, 0.0)
        self.store_z.append([])
        self.store_r.append([])
        self.episodic_band.append(float("inf"))
        return i

    def prototype(self, i: int) -> np.ndarray:
        return self.proto_sum[i] / self.proto_w[i]

    def band(self, i: int) -> float:
        """While a word has only its episodic meeting, its band is the one the write gave it (the median band of the
        known words then; +inf when no word was known — declared). From its 2nd meeting on: the responsibility-weighted
        0.90 quantile of its things' Euclidean distances to its prototype (declared: weighted by responsibility)."""
        if self.meetings[i] <= 1 or not self.store_z[i]:
            return self.episodic_band[i]
        Z = np.concatenate(self.store_z[i], axis=0)
        R = np.concatenate(self.store_r[i], axis=0)
        d = np.linalg.norm(Z - self.prototype(i)[None, :], axis=1)
        q = weighted_quantile(d, R, BAND_Q)
        return float("inf") if q is None else q

    def bands(self) -> np.ndarray:
        return np.array([self.band(i) for i in range(len(self.words))])

    # -- learning ------------------------------------------------------------------------------
    def _farthest(self, Z: np.ndarray, known: Sequence[int], bands: np.ndarray, rng: np.random.Generator) -> int:
        """The thing hypothesis farthest from every existing word's prototype, measured in bands: argmax over things of
        min over known words of ‖z − proto‖ / band (band +inf → 0 bands away). No known word → all tie. Ties → the
        scene's generator (declared)."""
        if not known:
            return int(rng.integers(Z.shape[0]))
        P = np.stack([self.prototype(i) for i in known])
        B = np.maximum(bands[list(known)], 1e-300)
        D = np.linalg.norm(Z[:, None, :] - P[None, :, :], axis=2) / B[None, :]
        return pick(D.min(axis=1), rng, "max")

    def train_scene(self, raw: np.ndarray, words: Sequence[str], referent: Optional[int] = None,
                    rng: Optional[np.random.Generator] = None) -> None:
        """One scene: its things' raw inputs (H, 146) and the parent's words. `referent` (P-ORACLE-RW only) is the index
        of the thing hypothesis the caller marks; None in A-RW / N-SHUF (never read there)."""
        raw = np.atleast_2d(np.asarray(raw, dtype=np.float64))
        self.scenes += 1
        if raw.shape[0] == 0:
            return
        self.stats.observe(raw)
        Z = self.stats.standardise(raw)
        said = list(dict.fromkeys(words))
        oracle_ref = referent if self.oracle else None
        if self.oracle and referent is None and said:
            self.skipped_said += 1
        # 1. the EPISODIC WRITE, from the pre-scene state; every new word of one utterance shares the one thing (declared)
        new = [w for w in said if w not in self.index]
        if new:
            known = [i for i in range(len(self.words)) if self.proto_w[i] > 0]
            bands = self.bands() if self.words else np.zeros(0)
            if self.oracle and oracle_ref is not None:
                t_star = int(oracle_ref)                     # P-ORACLE-RW: responsibility 1 on the marked referent
            elif self.oracle:
                t_star = None                                # the referent was not seen: nothing to write
            else:
                t_star = self._farthest(Z, known, bands, rng if rng is not None else np.random.default_rng(0))
            band0 = float(np.median(bands[known])) if known else float("inf")
            for w in new:
                i = self._add_word(w)
                if t_star is not None:
                    self.proto_sum[i] = Z[t_star]
                    self.proto_w[i] = 1.0
                    self.store_z[i].append(Z[t_star][None, :].copy())
                    self.store_r[i].append(np.ones(1))
                self.episodic_band[i] = band0
        if not self.words:
            return
        # 2. the delta rule, once per scene, for every word ever heard
        L = Z @ self.V.T + self.b[None, :]                   # (H, W)
        Pm = sigmoid(L)
        p_scene = 1.0 - np.prod(1.0 - Pm, axis=0)
        y = np.array([1.0 if w in said else 0.0 for w in self.words])
        e = y - p_scene
        S = Pm.sum(axis=0)
        R = np.where(S[None, :] > 0, Pm / np.where(S > 0, S, 1.0)[None, :], 1.0 / Z.shape[0])
        skip = np.zeros(len(self.words), dtype=bool)
        if self.oracle:
            for w in said:
                j = self.index[w]
                if oracle_ref is None:
                    skip[j] = True                           # declared: no referent seen → a said word is not updated
                else:
                    R[:, j] = 0.0
                    R[int(oracle_ref), j] = 1.0
        upd = self.lr * e[:, None] * (R.T @ Z)
        upd[skip] = 0.0
        self.V += upd
        db = self.lr * e * R.sum(axis=0)
        db[skip] = 0.0
        self.b += db
        # 3. prototypes: a said word's things, weighted by the responsibilities of this update (a new word's first
        #    meeting contributed its episodic thing instead)
        for w in said:
            j = self.index[w]
            if w not in new and not skip[j]:
                r = R[:, j]
                self.proto_sum[j] += r @ Z
                self.proto_w[j] += float(r.sum())
                self.store_z[j].append(Z.copy())
                self.store_r[j].append(r.copy())
            self.meetings[j] += 1

    # -- answering -----------------------------------------------------------------------------
    def logp_answer(self, Z: np.ndarray, bands: Optional[np.ndarray] = None) -> np.ndarray:
        """log p_w(t) as the learner ANSWERS: a word with fewer than 3 meetings by its prototype and band (p = 1 inside,
        0 outside → 0 / −inf); from its 3rd meeting on, log σ(v_w · z + b_w). (H, W)."""
        out = log_sigmoid(Z @ self.V.T + self.b[None, :])
        for j in np.flatnonzero(self.meetings < P_FROM_MEETING):
            if self.proto_w[j] <= 0:
                out[:, j] = -np.inf
                continue
            bj = bands[j] if bands is not None else self.band(int(j))
            d = np.linalg.norm(Z - self.prototype(int(j))[None, :], axis=1)
            out[:, j] = np.where(d <= bj, 0.0, -np.inf)
        return out

    def phrase_scores(self, Z: np.ndarray, phrase: Sequence[str], logp: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """Σ_{w ∈ phrase} log p_w(t) per thing; None when a word of the phrase was never heard."""
        if any(w not in self.index for w in phrase):
            return None
        if logp is None:
            logp = self.logp_answer(Z)
        return logp[:, [self.index[w] for w in phrase]].sum(axis=1)

    def calibrate(self, scenes: Sequence[Tuple[np.ndarray, Sequence[str], Optional[int]]]) -> Dict[str, object]:
        """At a reading point (declared: under the CURRENT state, over every training scene seen so far):
        τ_point = the conformal 0.90 threshold of the best phrase score of the phrase said in each training scene;
        τ_word(w) = the conformal 0.90 threshold of p_w on the thing with the highest responsibility for w (the
        referent in P-ORACLE-RW) in each training scene where w was said. A threshold with too few scores (n < 9) is
        None and answers conservatively (declared: «what is this?» then emits w only at p = 1)."""
        bands = self.bands()
        pts: List[float] = []
        per_word: Dict[str, List[float]] = {w: [] for w in self.words}
        for raw, words, ref in scenes:
            raw = np.atleast_2d(raw)
            if raw.shape[0] == 0 or not words:
                continue
            Z = self.stats.standardise(raw)
            lp = self.logp_answer(Z, bands)
            s = self.phrase_scores(Z, words, lp)
            if s is not None:
                pts.append(float(np.max(s)))
            Pm = sigmoid(Z @ self.V.T + self.b[None, :])
            for w in dict.fromkeys(words):
                j = self.index.get(w)
                if j is None:
                    continue
                if self.oracle:
                    if ref is None:
                        continue
                    h = int(ref)
                else:
                    col = Pm[:, j]
                    h = int(np.argmax(col))                  # the highest responsibility = the highest p_w (proportional rule)
                per_word[w].append(float(np.exp(lp[h, j])))
        self.tau_point = conformal_lower(pts)
        self.tau_word = {w: conformal_lower(v) for w, v in per_word.items()}
        self.calib_n = {"point": len(pts), **{f"word:{w}": len(v) for w, v in per_word.items()}}
        self._bands_cache = bands
        return {"tau_point": self.tau_point, "tau_word": dict(self.tau_word), "n": dict(self.calib_n)}

    def answer_point(self, raw: np.ndarray, phrase: Sequence[str], rng: np.random.Generator) -> Dict[str, object]:
        """M1 / M2a / M6: the forced pointing (argmax, ties by the item's generator) and the «none» flag
        (best < τ_point)."""
        Z = self.stats.standardise(np.atleast_2d(raw))
        s = self.phrase_scores(Z, phrase, self.logp_answer(Z, getattr(self, "_bands_cache", None)))
        if s is None:
            return {"point": None, "none": None, "best": None, "unheard": [w for w in phrase if w not in self.index]}
        k = pick(s, rng, "max")
        best = float(s[k])
        none = bool(self.tau_point is not None and best < self.tau_point)
        return {"point": k, "none": none, "best": best}

    def what_is_this(self, raw_thing: np.ndarray) -> List[str]:
        """M2b: every word w with p_w(t) ≥ τ_word(w) (τ None → 1.0, declared); [] means «I don't know»."""
        Z = self.stats.standardise(np.atleast_2d(raw_thing))
        lp = self.logp_answer(Z, getattr(self, "_bands_cache", None))[0]
        out = []
        for j, w in enumerate(self.words):
            tau = self.tau_word.get(w)
            tau = 1.0 if tau is None else tau
            if float(np.exp(lp[j])) >= tau:
                out.append(w)
        return out

    def name_forced(self, raw_thing: np.ndarray, type_words: Sequence[str]) -> Optional[str]:
        """A READING (never a bar): the forced argmax of p_w(t) over the words of one type the grader names."""
        cand = [w for w in type_words if w in self.index]
        if not cand:
            return None
        Z = self.stats.standardise(np.atleast_2d(raw_thing))
        lp = self.logp_answer(Z, getattr(self, "_bands_cache", None))[0]
        return cand[int(np.argmax([lp[self.index[w]] for w in cand]))]

    def summary(self) -> Dict[str, object]:
        return {"words": list(self.words), "meetings": [int(m) for m in self.meetings], "scenes": self.scenes,
                "skipped_said": self.skipped_said, "lr": self.lr, "oracle": self.oracle,
                "stats_n": self.stats.n, "tau_point": self.tau_point,
                "tau_word": {w: t for w, t in self.tau_word.items()}, "calib_n": dict(self.calib_n)}


# ================================================================================================ the LDA oracle reader
class LDAReader:
    """P-ORACLE (gaze hypotheses) and ORACLE-TRUTH (forced windows): slda.StreamingLDA over every word as a class (type-
    blind), on the 144 features; fed each said word with its referent's features. Declared readings:
      point      argmin over things of Σ_{w ∈ phrase} d_w(x)² (the Gaussian log-likelihood under the shared Λ);
      «none»     when that best score exceeds the conformal 0.90 threshold of its training referents' said-phrase scores;
      «what is this?»  every word with d_w(x) ≤ band_w, band_w = the conformal 0.90 threshold of d_w over w's training
                 referents (a word with too few, n < 9, takes the median band of the calibrated words — the episodic
                 rule's own fallback);
      per-type naming (the instrument verdict)  the forced argmin of d_w over the words of that type (the grader's
                 types; the reader itself is type-blind)."""

    def __init__(self, eps: float):
        self.eps = float(eps)
        self.lda = StreamingLDA(self.eps)
        self.train_x: List[np.ndarray] = []
        self.train_words: List[Tuple[str, ...]] = []
        self.skipped = 0
        self.band: Dict[str, float] = {}
        self.q_point: Optional[float] = None
        self.calib_n: Dict[str, int] = {}

    def train_scene(self, x_ref: Optional[np.ndarray], words: Sequence[str]) -> None:
        if not words:
            return
        if x_ref is None:
            self.skipped += 1                                # declared: the referent had no hypothesis — nothing seen
            return
        x = np.asarray(x_ref, dtype=np.float64)
        ws = tuple(dict.fromkeys(words))
        for w in ws:
            self.lda.observe(x, w)
        self.train_x.append(x)
        self.train_words.append(ws)

    @property
    def names(self) -> List[str]:
        return list(self.lda.names)

    def distances(self, X: np.ndarray) -> np.ndarray:
        """(H, K) Mahalanobis distances to every word's mean under the reader's metric (Λ after a sleep)."""
        X = np.atleast_2d(np.asarray(X, dtype=np.float64))
        if not self.lda.names:
            return np.zeros((X.shape[0], 0))
        dL, L = self.lda._metric()
        M = np.stack([m[:dL] for m in self.lda.means])
        X = X[:, :dL]
        XL = X @ L
        d2 = np.einsum("ij,ij->i", XL, X)[:, None] - 2.0 * (XL @ M.T) + np.einsum("kj,jl,kl->k", M, L, M)[None, :]
        return np.sqrt(np.maximum(d2, 0.0))

    def prepare(self) -> Dict[str, object]:
        """Sleep (Λ recomputed), then the conformal bands on the training referents under the new metric."""
        self.lda.sleep()
        if not self.train_x:
            self.band, self.q_point = {}, None
            return {"band": {}, "q_point": None, "n": {}}
        X = np.stack(self.train_x)
        Dm = self.distances(X)
        col = {w: k for k, w in enumerate(self.lda.names)}
        per: Dict[str, List[float]] = {w: [] for w in self.lda.names}
        pts: List[float] = []
        for i, ws in enumerate(self.train_words):
            for w in ws:
                per[w].append(float(Dm[i, col[w]]))
            pts.append(float(sum(Dm[i, col[w]] ** 2 for w in ws)))
        raw = {w: conformal_upper(v) for w, v in per.items()}
        good = [b for b in raw.values() if b is not None]
        fallback = float(np.median(good)) if good else float("inf")
        self.band = {w: (b if b is not None else fallback) for w, b in raw.items()}
        self.q_point = conformal_upper(pts)
        self.calib_n = {"point": len(pts), **{f"word:{w}": len(v) for w, v in per.items()}}
        return {"band": dict(self.band), "band_fallback": [w for w, b in raw.items() if b is None],
                "q_point": self.q_point, "n": dict(self.calib_n)}

    def phrase_scores(self, X: np.ndarray, phrase: Sequence[str]) -> Optional[np.ndarray]:
        col = {w: k for k, w in enumerate(self.lda.names)}
        if any(w not in col for w in phrase):
            return None
        D = self.distances(X)
        return (D[:, [col[w] for w in phrase]] ** 2).sum(axis=1)

    def answer_point(self, X: np.ndarray, phrase: Sequence[str], rng: np.random.Generator) -> Dict[str, object]:
        s = self.phrase_scores(X, phrase)
        if s is None:
            return {"point": None, "none": None, "best": None, "unheard": [w for w in phrase if w not in self.lda.names]}
        k = pick(s, rng, "min")
        best = float(s[k])
        none = bool(self.q_point is not None and best > self.q_point)
        return {"point": k, "none": none, "best": best}

    def what_is_this(self, x: np.ndarray) -> List[str]:
        d = self.distances(x)[0]
        return [w for k, w in enumerate(self.lda.names) if d[k] <= self.band.get(w, float("inf"))]

    def name_forced(self, x: np.ndarray, type_words: Sequence[str]) -> Optional[str]:
        col = {w: k for k, w in enumerate(self.lda.names)}
        cand = [w for w in type_words if w in col]
        if not cand:
            return None
        d = self.distances(x)[0]
        return cand[int(np.argmin([d[col[w]] for w in cand]))]

    def summary(self) -> Dict[str, object]:
        return {"eps": self.eps, "names": self.names, "counts": list(self.lda.counts), "train_scenes": len(self.train_x),
                "skipped": self.skipped, "band": dict(self.band), "q_point": self.q_point, "calib_n": dict(self.calib_n)}


# ================================================================================================ the feeds
def nshuf_permutation(rng: np.random.Generator, n: int) -> np.ndarray:
    """N-SHUF's fixed seeded permutation: each utterance paired with the scene of ANOTHER moment (declared: a uniformly
    random derangement, by rejection of permutations with a fixed point)."""
    for _ in range(1000):
        p = rng.permutation(n)
        if not np.any(p == np.arange(n)):
            return p
    raise RuntimeError("no derangement drawn in 1,000 tries")


def feed_rw(hyp_feats: np.ndarray, hyp_pos: np.ndarray) -> np.ndarray:
    """A-RW, N-SHUF and P-ORACLE-RW read the same things: [144 ‖ y/16, x/16] per thing hypothesis."""
    hyp_feats = np.atleast_2d(np.asarray(hyp_feats, dtype=np.float64))
    hyp_pos = np.atleast_2d(np.asarray(hyp_pos, dtype=np.float64))
    return np.concatenate([hyp_feats, hyp_pos / POS_SCALE], axis=1)


def feed_oracle(things144: np.ndarray, referent: Optional[int]) -> Optional[np.ndarray]:
    """P-ORACLE (things = gaze hypotheses) and ORACLE-TRUTH (things = forced windows): the referent's 144 features, or
    None when the caller has no referent thing among them."""
    if referent is None:
        return None
    return np.asarray(things144, dtype=np.float64)[int(referent)]
