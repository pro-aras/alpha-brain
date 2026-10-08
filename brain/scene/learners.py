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
  LDAReader   SUPERSEDED by AMENDMENT 2 (kept for the first gate's diagnosis scripts only): one type-blind StreamingLDA
              over every word as a class; per-word Mahalanobis distances under one shared Λ.
  TypedLDAReader  P-ORACLE / ORACLE-TRUTH as AMENDMENT 2 §1 rules them: one StreamingLDA per word TYPE (the word → type
              map passed in by the caller), pointing by the within-type posterior, «none» by the pointing score's
              conformal 0.90 threshold, «what is this?» by the conformal 0.90 DISTANCE band under the type's own Λ.

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:05 +0400 — AMENDMENT 2 §1 (PREREG-R3-TONIGHT-AMEND-2.md, genome-wt-brain3 d54e6c0):
TypedLDAReader added; LDAReader kept, superseded.
edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:07 +0400 — AMENDMENT 2 as CO-SIGNED (Fable 5.1, 74be9e0): «none» on the pointing score's
conformal threshold; «what is this?» by the DISTANCE band under the word's own type's Λ.
edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:08 +0400 — PREREG-S1B1R «the repair» (§1 a–e): the ear's type cover and one-word counts,
the READER (RWLearner.calibrate_r / reader_distances, pooled_covariance, shrunk_inverse), production maturity, the ROADS
(RWRoad, OracleRoad) and the believed-names mouth (produce_believed). Additive — S1b-1's roads are byte-for-byte kept.
edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:24 +0400 — BRAIN-IN-BODY (docs/brain/body/INTERFACE-BRAIN-ORGAN.md §3): two ADDITIVE
knobs with the old defaults, so genome/brain.py can read the BRAIN line's `young` and `conformal`: RWLearner.p_from (a class
attribute = P_FROM_MEETING) read where the module constant was, and RWLearner.calibrate(..., level=CONFORMAL).
edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 16:51 +0400 — PREREG-EAR-COVER-CAP (signed; sha256 a00d649c…):
the ear's type cover BOUNDED in the mouth-cap's pattern — at or below COVER_FULL_BELOW the full Bron–Kerbosch runs
VERBATIM (byte-identical to the pre-law module on every fixture/tape/life-scale vocabulary; the pre-law module loaded
from git history is the gate's oracle), above it the DECLARED bounded form (_largest_clique_bounded) — the same greedy
cover, the same tie-break, only the maximum-clique search replaced by a polynomially-bounded one. The bound landed from
the measured enumeration ladder (scratch/ear-cover-cap/ladder.txt), then halved — never tuned. Ear.cover, the two
constants and the one search added; no caller changes; nothing else moves.
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
# PREREG-S1B1 (edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:45 +0400): the law's constants — the classes keep S1a's defaults
# (so S1a's pins still read S1a's law); run.py passes these explicitly
LR_S1B1 = 0.01                # A-RW's law (A-RW-LR10 keeps 0.1 as a reading arm)
SIGMA_FLOOR = 1e-3            # σ_w floored per dimension
NONE_LEVEL = 0.95             # the phrase-level «none» (learner τ_none, oracle τ_point)
NONE_MIN_VIEW = 2             # calibrated on training scenes with ≥ 2 hypotheses (≥ 2 things for ORACLE-TRUTH)


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


# ------------------------------------------------------------------------------------------------ PREREG-EAR-COVER-CAP §2.1
# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 16:51 +0400 — the ear's cover BOUNDED (the mouth-cap's own
# pattern). At or below COVER_FULL_BELOW = (W0, E0) — len(words) ≤ W0 AND exclusion edges ≤ E0 — the full Bron–Kerbosch
# runs VERBATIM (nothing on that path changes a byte); above it the DECLARED bounded form (_largest_clique_bounded)
# runs. The bound LANDED from the measured enumeration ladder (the law's §2.1; scratch/ear-cover-cap/ladder.txt, the
# curve printed in the record): the largest ladder step the full enumeration completed under 60 s CPU and 1 GB was
# synth-g68 — W=68, E=2,089 (20.57 s CPU, 583.4 MB, 2,470,253 maximal cliques; the next steps — synth-g72 and every
# real tape cut from canvas 500 on, the knee included — broke the 1 GB bar) — then HALVED (the declared margin:
# 68 // 2, 2,089 // 2). A module constant beside MOUTH_BUDGET's own form — never a genome line; never tuned after a
# reading. (At W ≤ 34 every graph has ≤ C(34,2) = 561 < 1,044 edges, so the word count is the guard that binds — the
# edge count is the law's declared second counter, printed with each call.)
COVER_FULL_BELOW = (34, 1044)

# the law's §2.4: which path ran ("full" below / "bounded" at and above), journaled with each cover call's counts.
COVER_JOURNAL: List[Dict[str, object]] = []


# ================================================================================================ the EAR (PREREG-S1B1 §5)
class Ear:
    """What every arm learns from what it HEARS (PREREG-S1B1 §5), the same code for every arm: the ORDER KEY (per word, the
    running mean of its relative position i / (L − 1) over the heard utterances of length L ≥ 2 that carry it; a word
    never heard in such an utterance → 0.5), the order words were FIRST heard (the key's tie-break), and the EXCLUSION
    counts c(w, w′) = the heard utterances carrying both words (order-free)."""

    def __init__(self) -> None:
        self.first: Dict[str, int] = {}
        self.pos_sum: Dict[str, float] = {}
        self.pos_n: Dict[str, int] = {}
        self.co: Dict[Tuple[str, str], int] = {}
        self.alone: Dict[str, int] = {}                  # PREREG-S1B1R §1 (e) 4: the one-word utterances per word

    def hear(self, words: Sequence[str]) -> None:
        ws = list(words)
        for w in ws:
            if w not in self.first:
                self.first[w] = len(self.first)
        L = len(ws)
        if L >= 2:
            for i, w in enumerate(ws):
                self.pos_sum[w] = self.pos_sum.get(w, 0.0) + i / (L - 1)
                self.pos_n[w] = self.pos_n.get(w, 0) + 1
        u = sorted(set(ws))
        for a in range(len(u)):
            for b in range(a + 1, len(u)):
                self.co[(u[a], u[b])] = self.co.get((u[a], u[b]), 0) + 1
        if L == 1:                                       # additive (edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:08 +0400)
            self.alone[ws[0]] = self.alone.get(ws[0], 0) + 1

    def key(self, w: str) -> float:
        n = self.pos_n.get(w, 0)
        return self.pos_sum[w] / n if n else 0.5

    def order(self, words: Sequence[str]) -> List[str]:
        """Ascending order key; ties by the order the words were first heard (never-heard words last, by name)."""
        return sorted(words, key=lambda w: (self.key(w), self.first.get(w, len(self.first) + 10 ** 6), w))

    def count(self, a: str, b: str) -> int:
        return self.co.get((a, b) if a < b else (b, a), 0)

    def excluded(self, words: Sequence[str]) -> bool:
        """The learned EXCLUSION: a set holding any pair never heard together (c = 0) is not said."""
        u = list(words)
        return any(self.count(u[i], u[j]) == 0 for i in range(len(u)) for j in range(i + 1, len(u)))

    def summary(self) -> Dict[str, object]:
        return {"keys": {w: self.key(w) for w in sorted(self.first, key=self.first.get)},
                "first": dict(self.first), "pairs_heard": len(self.co)}

    def cover(self, words: Sequence[str], full_below: Tuple[int, int] = COVER_FULL_BELOW) -> List[Tuple[str, ...]]:
        """PREREG-S1B1R §1 (a) (edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:08 +0400): the TYPE COVER of `words` (the learner passes
        its MATURE words) from the EXCLUSION graph — an edge (w, w′) iff c(w, w′) = 0, never heard in one utterance. GREEDY:
        the LARGEST maximal clique of the remaining words becomes a type (ties → the lexicographically smallest sorted
        tuple), its words are removed, and so on; a word left alone is its own type. Types in the order taken.

        edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 16:51 +0400 — PREREG-EAR-COVER-CAP §2.2–2.4: at or below
        `full_below` (the law's COVER_FULL_BELOW by default — the parameter exists so the tests can exercise the bounded
        path on small graphs, MOUTH_BUDGET's own test-only form; every organism call site uses the default) the full
        Bron–Kerbosch runs VERBATIM; above it the DECLARED bounded form (the same greedy cover, the same tie-break, only
        the search replaced — _largest_clique_bounded). Each call appends {"words", "edges", "path"} to COVER_JOURNAL
        (the law's §2.4). The counts come from the ear's own counters (the edge count exactly, pairwise count() lookups)."""
        rest = sorted(set(words))
        edges = sum(1 for i in range(len(rest)) for j in range(i + 1, len(rest)) if self.count(rest[i], rest[j]) == 0)
        full = len(rest) <= full_below[0] and edges <= full_below[1]
        COVER_JOURNAL.append({"words": len(rest), "edges": edges, "path": "full" if full else "bounded"})
        types: List[Tuple[str, ...]] = []
        while rest:
            adj = {w: {u for u in rest if u != w and self.count(w, u) == 0} for w in rest}
            if full:
                best = min(_maximal_cliques(rest, adj), key=lambda c: (-len(c), c))
            else:
                best = _largest_clique_bounded(rest, adj)
            types.append(best)
            rest = [w for w in rest if w not in best]
        return types


def _maximal_cliques(nodes: Sequence[str], adj: Dict[str, set]) -> List[Tuple[str, ...]]:
    """Every maximal clique of the graph on `nodes` (Bron–Kerbosch with a pivot; every choice in sorted order, so nothing
    depends on string hashing). Each clique as a sorted tuple."""
    out: List[Tuple[str, ...]] = []

    def bk(R: List[str], P: List[str], X: List[str]) -> None:
        if not P and not X:
            out.append(tuple(sorted(R)))
            return
        pivot = max(P + X, key=lambda u: (sum(1 for v in P if v in adj[u]), u))
        for v in [v for v in P if v not in adj[pivot]]:
            bk(R + [v], [u for u in P if u in adj[v]], [u for u in X if u in adj[v]])
            P = [u for u in P if u != v]
            X = X + [v]

    bk([], sorted(nodes), [])
    return out


def _largest_clique_bounded(nodes: Sequence[str], adj: Dict[str, set]) -> Tuple[str, ...]:
    """PREREG-EAR-COVER-CAP §2.3 (edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 16:51 +0400) — the DECLARED
    bounded form, the enumeration's largest-maximal-clique pick replaced by a polynomially-bounded search: for each
    start word in sorted order, grow a clique greedily — candidates are the current members' common exclusion-
    neighbors; take them in sorted order; add each iff it is exclusion-adjacent to EVERY current member. The largest
    grown clique over all starts wins; ties → the lexicographically smallest sorted tuple (the enumeration's own
    tie-break). Cost is polynomial by construction (per start ≤ V candidates, each checked against ≤ V current
    members); the deterministic order is total (every iteration is over a sorted list — no hashing anywhere)."""
    best: Tuple[str, ...] = ()
    for s in sorted(nodes):
        members = [s]
        for u in sorted(adj[s]):                        # the current members' common exclusion-neighbors, in sorted order
            if all(u in adj[m] for m in members):       # added iff exclusion-adjacent to EVERY current member
                members.append(u)
        c = tuple(sorted(members))
        if len(c) > len(best) or (len(c) == len(best) and c < best):
            best = c
    return best


# ================================================================================================ A-RW (and P-ORACLE-RW)
class RWLearner:
    # edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:24 +0400 — BRAIN-IN-BODY: the genome's `young` (INTERFACE §3) reaches the
    # learner's maturity through this CLASS attribute (default P_FROM_MEETING = 3, so every existing caller reads 3 as before);
    # genome/brain.py sets it on its own instance. Every site below that read the module constant reads self.p_from / L.p_from.
    p_from: int = P_FROM_MEETING
    # edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:18 +0400 — PREREG-BRAIN-IN-BODY AMENDMENT 1 §2 (sha 45abeca2…): F-M6's switch, a CLASS
    # attribute whose default "band" is the LAW (every existing caller unchanged); genome/brain.py sets the INSTANCE attribute to
    # "nearest" only under `young <n> nearest` (so a law learner's vars() — and every state hash — is unchanged). Read by
    # answer_point alone.
    young_rule: str = "band"

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
        # edit: Claude (Opus 5.5, T-MEM-1 builder), 2026-09-28 17:17 +0400 — PREREG-TMEM1 §2 (the store's own coordinates): the RAW rows beside Z and
        # the storage time (the scene counter at the meeting), per word per meeting. Additive: nothing S1a–S1c-2 reads them.
        self.store_x: List[List[np.ndarray]] = []
        self.store_t: List[List[int]] = []
        self.store_r: List[List[np.ndarray]] = []      # per word: their responsibilities
        self.episodic_band: List[float] = []
        self.scenes = 0
        self.skipped_said = 0                            # P-ORACLE-RW: scenes whose referent had no hypothesis
        self.tau_point: Optional[float] = None
        self.tau_word: Dict[str, Optional[float]] = {}
        self.calib_n: Dict[str, int] = {}
        self.ear = Ear()                                  # PREREG-S1B1 §5: the order key and the exclusion
        self.refusal: Dict[str, Dict[str, Dict[str, object]]] = {"diag": {}, "euclid": {}}
        self.tau_none: Dict[str, Optional[float]] = {"diag": None, "euclid": None}
        self.none_level, self.none_min_view = NONE_LEVEL, NONE_MIN_VIEW

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
        self.store_x.append([])
        self.store_t.append([])
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
                    rng: Optional[np.random.Generator] = None, project=None) -> None:
        """One scene: its things' raw inputs (H, 146) and the parent's words. `referent` (P-ORACLE-RW only) is the index
        of the thing hypothesis the caller marks; None in A-RW / N-SHUF (never read there)."""
        raw = np.atleast_2d(np.asarray(raw, dtype=np.float64))
        self.scenes += 1
        self.ear.hear(words)                             # hearing is independent of seeing (PREREG-S1B1 §5)
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
                    self.store_x[i].append(raw[t_star][None, :].copy())
                    self.store_t[i].append(self.scenes)
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
        db = self.lr * e * R.sum(axis=0)
        db[skip] = 0.0
        if project is not None:                          # T-MEM-1's GATE (edit: Claude (Opus 5.5, T-MEM-1 builder), 2026-09-28 17:17 +0400): the
            upd, db = project(self, upd, db)             # step projected before it is applied; None = S1a–S1c-2's step, value for value
        self.V += upd
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
                self.store_x[j].append(raw.copy())
                self.store_t[j].append(self.scenes)
            self.meetings[j] += 1

    # -- answering -----------------------------------------------------------------------------
    def logp_answer(self, Z: np.ndarray, bands: Optional[np.ndarray] = None) -> np.ndarray:
        """log p_w(t) as the learner ANSWERS: a word with fewer than 3 meetings by its prototype and band (p = 1 inside,
        0 outside → 0 / −inf); from its 3rd meeting on, log σ(v_w · z + b_w). (H, W)."""
        out = log_sigmoid(Z @ self.V.T + self.b[None, :])
        for j in np.flatnonzero(self.meetings < self.p_from):
            if self.proto_w[j] <= 0:
                out[:, j] = -np.inf
                continue
            # a word NEWER than the reading point's band cache (met between reading points — T-MEM-2's claims read the road
            # there) takes its band fresh, the function the cache is built from; every call that worked before is unchanged
            # (edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:42 +0400)
            bj = bands[j] if (bands is not None and j < len(bands)) else self.band(int(j))
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

    # -- refusal by DISTANCE (PREREG-S1B1 §3) -------------------------------------------------------
    def _refusal_states(self, mode: str) -> Dict[str, Dict[str, object]]:
        """Per word, from the learner's OWN store (store_z, store_r — the standardised inputs and responsibilities as they
        were stored at each meeting; declared, RAISED: the store is not re-standardised): μ_w = S1a's prototype; σ_w =
        the responsibility-weighted SD per dimension about μ_w, floored at 1e-3 ("diag") or ≡ 1 ("euclid", reading
        (ii)); d_w(z) = ‖(z − μ_w) / σ_w‖; B_w = the responsibility-weighted 0.90 quantile of d_w over w's own things
        (S1a's BAND_Q and weighted_quantile). A word with fewer than 3 meetings keeps S1a's answer whole: Euclidean
        distance to its prototype, S1a's episodic / 0.90 band. A word with no prototype holds nothing."""
        out: Dict[str, Dict[str, object]] = {}
        for j, w in enumerate(self.words):
            if self.proto_w[j] <= 0:
                out[w] = {"mu": None, "sigma": None, "band": None, "young": True, "floor_count": None}
                continue
            mu = self.prototype(j)
            if self.meetings[j] < self.p_from or not self.store_z[j]:
                out[w] = {"mu": mu, "sigma": np.ones(self.dim), "band": self.band(j), "young": True, "floor_count": None}
                continue
            Z = np.concatenate(self.store_z[j], axis=0)
            R = np.concatenate(self.store_r[j], axis=0)
            tot = float(R.sum())
            sd = np.sqrt((R[:, None] * (Z - mu[None, :]) ** 2).sum(axis=0) / tot) if tot > 0 else np.zeros(self.dim)
            sigma = np.maximum(sd, SIGMA_FLOOR) if mode == "diag" else np.ones(self.dim)
            d = np.linalg.norm((Z - mu[None, :]) / sigma[None, :], axis=1)
            q = weighted_quantile(d, R, BAND_Q)
            out[w] = {"mu": mu, "sigma": sigma, "band": float("inf") if q is None else q, "young": False,
                      "floor_count": int((sd < SIGMA_FLOOR).sum())}
        return out

    def distances(self, Z: np.ndarray, mode: str = "diag") -> np.ndarray:
        """(H, W) d_w(z) under the refusal state of `mode` (inf for a word with no prototype)."""
        Z = np.atleast_2d(Z)
        D = np.full((Z.shape[0], len(self.words)), np.inf)
        st = self.refusal.get(mode, {})
        for j, w in enumerate(self.words):
            r = st.get(w)
            if r is None or r["mu"] is None:
                continue
            D[:, j] = np.linalg.norm((Z - r["mu"][None, :]) / r["sigma"][None, :], axis=1)
        return D

    def held(self, Z: np.ndarray, mode: str = "diag") -> List[str]:
        """HELD(z): every word whose band holds the thing — emitted WHOLE, no pruning (PREREG-S1B1 §3)."""
        D = self.distances(np.atleast_2d(Z)[:1], mode)[0]
        st = self.refusal.get(mode, {})
        return [w for j, w in enumerate(self.words)
                if st.get(w) is not None and st[w]["band"] is not None and D[j] <= st[w]["band"]]

    def phrase_fit(self, Z: np.ndarray, phrase: Sequence[str], mode: str = "diag") -> np.ndarray:
        """f(t) = max over the phrase's words of d_w(z_t) / B_w (inf when a word holds nothing)."""
        D = self.distances(Z, mode)
        st = self.refusal.get(mode, {})
        cols = []
        for w in phrase:
            j = self.index[w]
            r = st.get(w)
            b = None if r is None else r["band"]
            cols.append(np.full(D.shape[0], np.inf) if b is None else D[:, j] / max(float(b), 1e-12))
        return np.max(np.stack(cols, axis=1), axis=1)

    def calibrate(self, scenes: Sequence[Tuple[np.ndarray, Sequence[str], Optional[int]]],
                  level: float = CONFORMAL) -> Dict[str, object]:
        """At a reading point (declared: under the CURRENT state, over every training scene seen so far):
        τ_point = the conformal 0.90 threshold of the best phrase score of the phrase said in each training scene;
        τ_word(w) = the conformal 0.90 threshold of p_w on the thing with the highest responsibility for w (the
        referent in P-ORACLE-RW) in each training scene where w was said. A threshold with too few scores (n < 9) is
        None and answers conservatively (declared: «what is this?» then emits w only at p = 1). — S1a's rules, kept
        whole as READING (i) (PREREG-S1B1 §3).
        PREREG-S1B1 §3 (edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:45 +0400): the refusal states («diag» the law, «euclid»
        reading (ii)) from the store, and τ_none per mode = the conformal 0.95 UPPER threshold of f(t*) = min_t f(t) for
        the phrase said in each training scene that showed ≥ 2 hypotheses (the learner's own count), under the current
        state (the raw inputs re-standardised, as S1a's calibrate)."""
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
        # edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:24 +0400 — `level` (default CONFORMAL = 0.90, every existing caller unchanged) is
        # the genome's `conformal` (INTERFACE §3): τ_point's and τ_word's conformal level.
        self.tau_point = conformal_lower(pts, level)
        self.tau_word = {w: conformal_lower(v, level) for w, v in per_word.items()}
        self._bands_cache = bands
        # the refusal by distance (the law and reading (ii)) and its phrase-level «none»
        self.refusal = {m: self._refusal_states(m) for m in ("diag", "euclid")}
        fits: Dict[str, List[float]] = {"diag": [], "euclid": []}
        for raw, words, _ref in scenes:
            raw = np.atleast_2d(raw)
            if raw.shape[0] < self.none_min_view or not words or any(w not in self.index for w in words):
                continue
            Z = self.stats.standardise(raw)
            for m in fits:
                fits[m].append(float(np.min(self.phrase_fit(Z, list(dict.fromkeys(words)), m))))
        self.tau_none = {m: conformal_upper(v, self.none_level) for m, v in fits.items()}
        self.calib_n = {"point": len(pts), "none": len(fits["diag"]),
                        **{f"word:{w}": len(v) for w, v in per_word.items()}}
        floor = {w: st["floor_count"] for w, st in self.refusal["diag"].items()}
        return {"tau_point": self.tau_point, "tau_word": dict(self.tau_word), "tau_none": dict(self.tau_none),
                "bands": {m: {w: st["band"] for w, st in self.refusal[m].items()} for m in self.refusal},
                "sigma_floor_count": floor, "n": dict(self.calib_n)}

    def answer_point(self, raw: np.ndarray, phrase: Sequence[str], rng: np.random.Generator) -> Dict[str, object]:
        """M1 / M2a / M3 / M6 / the read-back: the forced pointing (argmax of Σ log p_w(t), ties by the item's generator
        — S1a's rule, unchanged: refusing is a separate job from pointing) with the score vector, and three «none»
        flags from the same state: the LAW (PREREG-S1B1 §3: f(t*) > τ_none, the diagonal distance), reading (i)
        S1a's (best < τ_point) and reading (ii) (the Euclidean fit)."""
        Z = self.stats.standardise(np.atleast_2d(raw))
        s = self.phrase_scores(Z, phrase, self.logp_answer(Z, getattr(self, "_bands_cache", None)))
        if s is None:
            return {"point": None, "none": None, "best": None, "unheard": [w for w in phrase if w not in self.index]}
        # edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:18 +0400 — AMENDMENT 1 §2: under young_rule "nearest", a ONE-young-word
        # phrase chooses `point` by _young_nearest (None = a fall-back: the law's pick below, drawing the generator exactly as
        # the law does). `best` = max(s) is the law's number whichever tied index the law would pick; the fix never draws the
        # law's pick, and draws the generator only on an exact DISTANCE tie.
        near = self._young_nearest(Z, phrase, rng)
        if near is None:
            k = pick(s, rng, "max")
            best = float(s[k])
        else:
            k, young_d = near
            best = float(np.max(s))
        words = list(dict.fromkeys(phrase))
        flags = {}
        for m, key in (("diag", "none"), ("euclid", "none_ii")):
            tau = self.tau_none.get(m)
            f = self.phrase_fit(Z, words, m)
            flags[key] = bool(tau is not None and float(np.min(f)) > tau)
            flags[key + "_fit"] = float(np.min(f))
        out = {"point": k, "best": best, "scores": [float(v) for v in s],
               "none_i": bool(self.tau_point is not None and best < self.tau_point), **flags}
        if near is not None:
            out["young_d"] = [float(v) for v in young_d]
            out["point_rule"] = "nearest"
        return out

    def _young_nearest(self, Z: np.ndarray, phrase: Sequence[str], rng: np.random.Generator):
        """F-M6 (PREREG-BRAIN-IN-BODY AMENDMENT 1 §2, edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:18 +0400): (point, distances) when
        the rule ACTS, else None (the law points). It acts only when young_rule is "nearest" AND the phrase is ONE word AND that
        word is heard and young (meetings < p_from). Nearest, exactly: d(h) = √((z_h − μ_w)ᵀ Λ (z_h − μ_w)), μ_w = the word's
        prototype (the responsibility-weighted mean of its stored meetings; one meeting → that meeting), Λ =
        reader["ear"]["lam"][one_alone] (the pooled covariance of the type its ear heard alone most, shrunk at the BRAIN line's
        eps by calibrate_r) — tools/brain/diag/diag_m6_metric.py's distance; an exact tie → pick(d, rng, "min"). The four
        fall-backs to the law: no reader yet (never calibrate_r'd), one_alone None, that type's Λ None, proto_w 0. Read-only."""
        rule = self.young_rule
        if rule not in ("band", "nearest"):
            raise ValueError(f"young_rule {rule!r}: the rules are 'band' (the law) and 'nearest' (F-M6)")
        if rule != "nearest" or len(phrase) != 1:
            return None
        j = self.index.get(phrase[0])
        if j is None or int(self.meetings[j]) >= self.p_from:
            return None
        st = (getattr(self, "reader", None) or {}).get("ear")
        if st is None or st.get("one_alone") is None:
            return None
        lam = st["lam"][st["one_alone"]]
        if lam is None or self.proto_w[j] <= 0:
            return None
        E = Z - self.prototype(int(j))[None, :]
        d = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", E, lam, E), 0.0))
        return pick(d, rng, "min"), d

    def what_is_this_s1a(self, raw_thing: np.ndarray) -> List[str]:
        """READING (i): S1a's «what is this?» — every word w with p_w(t) ≥ τ_word(w) (τ None → 1.0)."""
        Z = self.stats.standardise(np.atleast_2d(raw_thing))
        lp = self.logp_answer(Z, getattr(self, "_bands_cache", None))[0]
        out = []
        for j, w in enumerate(self.words):
            tau = self.tau_word.get(w)
            tau = 1.0 if tau is None else tau
            if float(np.exp(lp[j])) >= tau:
                out.append(w)
        return out

    def what_is_this(self, raw_thing: np.ndarray) -> List[str]:
        """THE LAW (PREREG-S1B1 §3): HELD(z) under the per-word diagonal distance, whole; [] means «I don't know»."""
        return self.held(self.stats.standardise(np.atleast_2d(raw_thing)), "diag")

    def what_is_this_readings(self, raw_thing: np.ndarray) -> Dict[str, List[str]]:
        Z = self.stats.standardise(np.atleast_2d(raw_thing))
        return {"law": self.held(Z, "diag"), "i": self.what_is_this_s1a(raw_thing), "ii": self.held(Z, "euclid")}

    def held_words(self, raw_thing: np.ndarray) -> List[str]:
        """The mouth's HELD (§5 step 1): the law's held words for the target."""
        return self.what_is_this(raw_thing)

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
                "tau_word": {w: t for w, t in self.tau_word.items()}, "calib_n": dict(self.calib_n),
                "tau_none": dict(self.tau_none), "ear": self.ear.summary()}

    # -- PREREG-S1B1R §1 (a)–(c) (edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:08 +0400): additive; S1b-1's roads never read these
    def mature_words(self) -> List[str]:
        """The words of ≥ 3 meetings (P_FROM_MEETING): the only words the learner EMITS (§1 c) and the vertices of its types."""
        return [w for j, w in enumerate(self.words) if self.meetings[j] >= self.p_from]

    def calibrate_r(self, eps: float, world_types: Optional[Dict[str, str]] = None) -> Dict[str, object]:
        """At a reading point, AFTER calibrate() (never changing what it set): the learned TYPES — the ear's greedy cover of
        the MATURE words (§1 a) — and THE READER per type (§1 b), in `self.reader["ear"]`; with `world_types` (a word → type
        map the CALLER passes — the learner never holds one: R-TT) the world's types over the same mature words in
        `self.reader["world"]`. Returns the printable record: the types, the one-alone type and its counts, the bands."""
        mature = self.mature_words()
        self.reader = {"ear": self._reader_state(self.ear.cover(mature), eps)}
        if world_types is not None:
            groups: Dict[str, List[str]] = {}
            for w in mature:
                groups.setdefault(world_types[w], []).append(w)
            self.reader["world"] = self._reader_state(sorted((tuple(sorted(v)) for v in groups.values()),
                                                             key=lambda c: (-len(c), c)), eps)

        def rec(st):
            return {"types": [list(t) for t in st["types"]], "one_alone": st["one_alone"],
                    "alone_counts": list(st["alone_counts"]), "bands": {w: v["band"] for w, v in st["word"].items()}}
        out = {"eps": eps, "mature": mature, **rec(self.reader["ear"])}
        if "world" in self.reader:
            out["world"] = rec(self.reader["world"])
        return out

    def _reader_state(self, types: Sequence[Tuple[str, ...]], eps: float) -> Dict[str, object]:
        """Per type T: Σ_T (pooled_covariance), Λ_T = shrunk_inverse(Σ_T, ε) (slda's own form); per word w ∈ T: μ_w (S1a's
        prototype), B_w = the responsibility-weighted 0.90 quantile (BAND_Q, weighted_quantile) of d_w over w's OWN store;
        the ONE-ALONE type = the type whose words the ear heard alone most often (ties → the earlier type; none heard → None)."""
        st: Dict[str, object] = {"types": [tuple(t) for t in types], "lam": [], "word": {}, "eps": float(eps)}
        for k, T in enumerate(st["types"]):
            S = pooled_covariance(self, T)
            lam = None if S is None else shrunk_inverse(S, eps)
            st["lam"].append(lam)
            for w in T:
                j = self.index[w]
                if lam is None or self.proto_w[j] <= 0 or not self.store_z[j]:
                    st["word"][w] = {"type": k, "mu": None, "band": None}
                    continue
                mu = self.prototype(j)
                D = np.concatenate(self.store_z[j], axis=0) - mu[None, :]
                d = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", D, lam, D), 0.0))
                q = weighted_quantile(d, np.concatenate(self.store_r[j], axis=0), BAND_Q)
                st["word"][w] = {"type": k, "mu": mu, "band": float("inf") if q is None else q}
        counts = [int(sum(self.ear.alone.get(w, 0) for w in T)) for T in st["types"]]
        st["alone_counts"] = counts
        st["one_alone"] = int(np.argmax(counts)) if counts and max(counts) > 0 else None
        return st

    def reader_distances(self, Z: np.ndarray, mode: str = "ear") -> np.ndarray:
        """(H, W) d_w(z) = √((z − μ_w)ᵀ Λ_T (z − μ_w)) under the READER state `mode`; +inf for a word outside it."""
        Z = np.atleast_2d(Z)
        D = np.full((Z.shape[0], len(self.words)), np.inf)
        st = self.reader[mode]
        for w, v in st["word"].items():
            if v["mu"] is None:
                continue
            E = Z - v["mu"][None, :]
            D[:, self.index[w]] = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", E, st["lam"][v["type"]], E), 0.0))
        return D


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


# ================================================================================================ the TYPE-AWARE oracle reader
def _logsumexp_rows(S: np.ndarray) -> np.ndarray:
    m = np.max(S, axis=1, keepdims=True)
    return m + np.log(np.sum(np.exp(S - m), axis=1, keepdims=True))


class TypedLDAReader:
    """P-ORACLE and ORACLE-TRUTH as AMENDMENT 2 §1 rules them (PREREG-R3-TONIGHT-AMEND-2.md, 2026-09-28 12:56 +0400; it
    supersedes LDAReader above, which stays only for the diagnosis scripts of the first gate):
      · ONE StreamingLDA PER WORD TYPE (the 6 shapes compete with each other; the 5 colours; the 2 sizes), each with its
        own within-class covariance, one ε for all three (chosen on the toy seed). The word → type map is PASSED IN by the
        caller — the oracle may know the types, the learners never do, and this module still imports no world.
      · p(w | x) = the posterior WITHIN w's type: the softmax over that type's classes of the reader's own discriminant
        (StreamingLDA's scores; equal class priors, as the reader is built — declared).
      · pointing = argmax over things of Σ_{w ∈ phrase} log p(w | x) (ties by the item's generator);
      · «none» (as CO-SIGNED, Fable 5.1 13:02): the best phrase score Σ log p below τ_point = the conformal 0.90
        threshold of the said-phrase scores on the training referents (the builder's rule, on the new score);
      · «what is this?» (as CO-SIGNED) KEEPS the DISTANCE band, under the word's own type's Λ: emit w when d_w(x) ≤ band_w,
        the conformal 0.90 threshold of d_w over w's training referents (n < 9 → the median band of the calibrated
        words) — a posterior sums to 1 over the taught words and cannot refuse a never-taught shape;
      · per-type naming (the instrument verdict) = the FORCED argmax of the type's posterior over the grader's words
        (= argmin d within the type; no band)."""

    def __init__(self, eps: float, word_types: Dict[str, str], point_level: float = CONFORMAL,
                 point_min_view: Optional[int] = None):
        """point_level / point_min_view: τ_point's conformal level and population — S1a's defaults (0.90, every training
        referent); PREREG-S1B1 §3 passes 0.95 and ≥ 2 hypotheses (≥ 2 things for ORACLE-TRUTH)."""
        self.eps = float(eps)
        self.word_types = dict(word_types)
        self.point_level = float(point_level)
        self.point_min_view = point_min_view
        self.readers: Dict[str, StreamingLDA] = {}
        self.train_x: List[np.ndarray] = []
        self.train_words: List[Tuple[str, ...]] = []
        self.train_nview: List[Optional[int]] = []
        self.ear = Ear()
        self.skipped = 0
        self.band: Dict[str, float] = {}                     # the DISTANCE band per word (what is this?)
        self.band_fallback: List[str] = []
        self.tau_point: Optional[float] = None               # «none»: the pointing score's conformal threshold
        self.calib_n: Dict[str, int] = {}

    def type_of(self, w: str) -> str:
        return self.word_types[w]                            # KeyError: a word of no declared type is refused

    def names_of(self, t: str) -> List[str]:
        r = self.readers.get(t)
        return list(r.names) if r is not None else []

    @property
    def names(self) -> List[str]:
        return [w for t in sorted(self.readers) for w in self.readers[t].names]

    def heard(self, w: str) -> bool:
        return w in self.word_types and w in self.names_of(self.type_of(w))

    def train_scene(self, x_ref: Optional[np.ndarray], words: Sequence[str], n_view: Optional[int] = None) -> None:
        ws = tuple(dict.fromkeys(words))
        if not ws:
            return
        types = [self.type_of(w) for w in ws]                # refuse before any observation
        self.ear.hear(words)                                 # PREREG-S1B1 §5: the oracle hears every utterance, seen or not
        if x_ref is None:
            self.skipped += 1                                # the referent had no hypothesis — nothing seen
            return
        x = np.asarray(x_ref, dtype=np.float64)
        for w, t in zip(ws, types):
            r = self.readers.get(t)
            if r is None:
                r = self.readers[t] = StreamingLDA(self.eps)
            r.observe(x, w)
        self.train_x.append(x)
        self.train_words.append(ws)
        self.train_nview.append(n_view)

    def _log_post(self, t: str, X: np.ndarray) -> np.ndarray:
        """(H, K_t) log posterior over type t's classes, in the reader's class order."""
        r = self.readers[t]
        X = np.atleast_2d(np.asarray(X, dtype=np.float64))
        dL, L = r._metric()
        Mu = np.stack([m[:dL] for m in r.means])
        S = X[:, :dL] @ (Mu @ L).T - 0.5 * np.einsum("kj,jl,kl->k", Mu, L, Mu)[None, :]
        return S - _logsumexp_rows(S)

    def log_posterior(self, X: np.ndarray, w: str) -> np.ndarray:
        t = self.type_of(w)
        return self._log_post(t, X)[:, self.readers[t].names.index(w)]

    def _dist(self, t: str, X: np.ndarray) -> np.ndarray:
        """(H, K_t) Mahalanobis distances to type t's class means under ITS OWN metric (Λ_t after a sleep)."""
        r = self.readers[t]
        X = np.atleast_2d(np.asarray(X, dtype=np.float64))
        dL, L = r._metric()
        Mu = np.stack([m[:dL] for m in r.means])
        Xd = X[:, :dL]
        XL = Xd @ L
        d2 = np.einsum("ij,ij->i", XL, Xd)[:, None] - 2.0 * (XL @ Mu.T) + np.einsum("kj,jl,kl->k", Mu, L, Mu)[None, :]
        return np.sqrt(np.maximum(d2, 0.0))

    def prepare(self) -> Dict[str, object]:
        for t in sorted(self.readers):
            self.readers[t].sleep()
        per: Dict[str, List[float]] = {w: [] for w in self.names}
        pts: List[float] = []
        if self.train_x:
            X = np.stack(self.train_x)
            lp = {t: self._log_post(t, X) for t in self.readers}
            dd = {t: self._dist(t, X) for t in self.readers}
            col = {w: (t, self.readers[t].names.index(w)) for t in self.readers for w in self.readers[t].names}
            for i, ws in enumerate(self.train_words):
                sc = 0.0
                for w in ws:
                    t, k = col[w]
                    per[w].append(float(dd[t][i, k]))
                    sc += float(lp[t][i, k])
                nv = self.train_nview[i] if i < len(self.train_nview) else None
                if self.point_min_view is None or nv is None or nv >= self.point_min_view:
                    pts.append(sc)
        raw = {w: conformal_upper(v) for w, v in per.items()}
        good = [b for b in raw.values() if b is not None]
        fallback = float(np.median(good)) if good else float("inf")
        self.band = {w: (b if b is not None else fallback) for w, b in raw.items()}
        self.band_fallback = [w for w, b in raw.items() if b is None]
        self.tau_point = conformal_lower(pts, self.point_level)
        self.calib_n = {"point": len(pts), **{f"word:{w}": len(v) for w, v in per.items()}}
        return {"band": dict(self.band), "band_fallback": list(self.band_fallback), "tau_point": self.tau_point,
                "point_level": self.point_level, "point_min_view": self.point_min_view, "n": dict(self.calib_n)}

    def answer_point(self, X: np.ndarray, phrase: Sequence[str], rng: np.random.Generator) -> Dict[str, object]:
        unheard = [w for w in phrase if not self.heard(w)]
        if unheard:
            return {"point": None, "none": None, "best": None, "unheard": unheard}
        lps = {w: self.log_posterior(X, w) for w in dict.fromkeys(phrase)}
        s = np.sum([lps[w] for w in phrase], axis=0)
        k = pick(s, rng, "max")
        best = float(s[k])
        none = bool(self.tau_point is not None and best < self.tau_point)
        return {"point": k, "none": none, "best": best, "scores": [float(v) for v in s]}

    def held_words(self, x: np.ndarray) -> List[str]:
        """The mouth's HELD (PREREG-S1B1 §5): the oracle's own «what is this?» — its per-type distance bands."""
        return self.what_is_this(x)

    def colour_fit(self, x: np.ndarray) -> Dict[str, float]:
        """The organ fact of DECLINE (PREREG-S1B1 §5): d_w / B_w of a thing for every colour word, under the colour Λ."""
        t = "colour"
        if t not in self.readers:
            return {}
        d = self._dist(t, x)[0]
        return {w: float(d[k]) / max(self.band.get(w, float("inf")), 1e-12) for k, w in enumerate(self.readers[t].names)}

    def what_is_this(self, x: np.ndarray) -> List[str]:
        out = []
        for t in sorted(self.readers):
            d = self._dist(t, x)[0]
            for k, w in enumerate(self.readers[t].names):
                if float(d[k]) <= self.band.get(w, float("inf")):
                    out.append(w)
        return out

    def name_forced(self, x: np.ndarray, type_words: Sequence[str]) -> Optional[str]:
        cand = [w for w in type_words if self.heard(w)]
        if not cand:
            return None
        t = self.type_of(cand[0])
        if any(self.type_of(w) != t for w in cand):
            raise ValueError(f"forced naming over words of several types: {cand}")
        lp = self._log_post(t, x)[0]
        names = self.readers[t].names
        return cand[int(np.argmax([lp[names.index(w)] for w in cand]))]

    def summary(self) -> Dict[str, object]:
        return {"eps": self.eps, "types": {t: self.names_of(t) for t in sorted(self.readers)},
                "counts": {t: list(self.readers[t].counts) for t in sorted(self.readers)},
                "train_scenes": len(self.train_x), "skipped": self.skipped, "band": dict(self.band),
                "band_fallback": list(self.band_fallback), "tau_point": self.tau_point, "calib_n": dict(self.calib_n),
                "point_level": self.point_level, "point_min_view": self.point_min_view, "ear": self.ear.summary()}


# ================================================================================================ the MOUTH (PREREG-S1B1 §5)
def _subsets(words: Sequence[str]) -> List[List[str]]:
    ws = list(words)
    out = []
    for mask in range(1, 1 << len(ws)):
        out.append([ws[i] for i in range(len(ws)) if mask >> i & 1])
    return out


def produce(arm, X: np.ndarray, target: int, rng_factory) -> Dict[str, object]:
    """The SAME production code for every arm (PREREG-S1B1 §5), parameterised by the arm's `held_words(x)`,
    `answer_point(X, phrase, rng)` and `ear`; the builder types no phrase.
      1. HELD = the words whose band holds the target, whole;
      2. candidates = every non-empty subset of HELD not EXCLUDED by the ear (a pair never heard together), each in the
         ear's ORDER;
      3. the READ-BACK: each candidate through the arm's own pointing (a fresh item tie generator per candidate —
         declared); ACCEPTED iff the scores' maximum is UNIQUE and on the target and «none» did not fire;
      4. spoken = the shortest accepted; then the largest read-back margin (the target's score − the best other); then,
         declared, the candidate's (order keys, first-heard) sequence;
      5. none accepted → «I cannot say it yet», one reason (declared priority): «no held word» when HELD is empty; else
         «none fired» when some candidate read back uniquely on the target but «none» fired; else «no unique read-back».
    The read-back's point and the target given are both RECORDED, so the grader re-checks the wiring on every spoken
    phrase (READ-BACK = 1.000 by construction; a reading below it is a broken road)."""
    X = np.atleast_2d(X)
    held = list(arm.held_words(X[int(target)]))
    if not held:
        return {"spoken": None, "reason": "no held word", "held": [], "n_candidates": 0, "n_accepted": 0,
                "target": int(target)}
    ear = arm.ear
    cands = [ear.order(c) for c in _subsets(held) if not ear.excluded(c)]
    accepted = []
    fired = 0
    for c in cands:
        a = arm.answer_point(X, c, rng_factory())
        if a.get("point") is None:
            continue
        sc = np.asarray(a["scores"], dtype=np.float64)
        top = np.flatnonzero(sc == np.max(sc))
        if not (top.size == 1 and int(top[0]) == int(target)):
            continue
        if a.get("none"):
            fired += 1
            continue
        others = np.delete(sc, int(target))
        margin = float(sc[int(target)] - np.max(others)) if others.size else float("inf")
        rank = (len(c), -margin, tuple(ear.key(w) for w in c), tuple(ear.first.get(w, 10 ** 6) for w in c))
        accepted.append((rank, c, int(a["point"]), margin))
    if not accepted:
        return {"spoken": None, "reason": "none fired" if fired else "no unique read-back", "held": held,
                "n_candidates": len(cands), "n_accepted": 0, "target": int(target)}
    accepted.sort(key=lambda t: t[0])
    _rank, phrase, point, margin = accepted[0]
    return {"spoken": list(phrase), "reason": None, "held": held, "readback_point": point, "target": int(target),
            "margin": margin, "n_candidates": len(cands), "n_accepted": len(accepted)}


# ================================================================================================ S1b-1R «the repair»
# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:08 +0400 — PREREG-S1B1R §1 (sha 879a22fb…) with AMENDMENT 1 (a198f0b4…): the READER's
# pieces, the ROADS (one per reading, over one learned state) and the mouth that says what it BELIEVES. Additive: S1b-1's
# classes, `produce` and every S1b-1 road above are byte-for-byte as they were.
def pooled_covariance(L: "RWLearner", words: Sequence[str]) -> Optional[np.ndarray]:
    """§1 (b): Σ_T = Σ_{w∈T} Σ_i r_i (z_i − μ_w)(z_i − μ_w)ᵀ / Σ_{w∈T} Σ_i r_i over the words' OWN stores (store_z, store_r
    as stored — the inputs the diagonal band reads), μ_w = the word's prototype. None when the words hold no weight."""
    num = np.zeros((L.dim, L.dim))
    den = 0.0
    for w in words:
        j = L.index[w]
        if L.proto_w[j] <= 0 or not L.store_z[j]:
            continue
        R = np.concatenate(L.store_r[j], axis=0)
        D = np.concatenate(L.store_z[j], axis=0) - L.prototype(j)[None, :]
        num += (D * R[:, None]).T @ D
        den += float(R.sum())
    return num / den if den > 0 else None


def shrunk_inverse(S: np.ndarray, eps: float) -> np.ndarray:
    """Λ = [(1 − ε)Σ + ε (tr Σ / d) I]⁻¹ — slda.StreamingLDA.sleep's own shrinkage form (a zero or non-finite trace → I,
    its D27)."""
    d = S.shape[0]
    tr = float(np.trace(S))
    if not np.isfinite(tr) or tr <= 0.0:
        return np.eye(d)
    return np.linalg.inv((1.0 - eps) * S + eps * (tr / d) * np.eye(d))


class RWRoad:
    """ONE ROAD of PREREG-S1B1R §1 / §3 over an RWLearner's state — a road never changes the learner, so every reading is
    one difference on one learned state. The law A-RW-R is RWRoad(L): types from the ear, the READER band, production
    maturity, «none» = S1a's τ_point (S1b-1's none_i). The readings swap one argument back: types="world" (R-TT), band="diag"
    (R-DIAG), none="dist" (R-NONE-DIST); R-OLDMOUTH is the law's road under S1b-1's `produce`. S1B1-ROADS (the item-change
    control, AMENDMENT 1 §4 b) = RWRoad(L, types=None, band="diag", mature=False, none="dist") under `produce`: S1b-1's A-RW."""

    def __init__(self, L: "RWLearner", types: Optional[str] = "ear", band: str = "reader", mature: bool = True,
                 none: str = "tau_point"):
        if band not in ("reader", "diag") or none not in ("tau_point", "dist") or types not in (None, "ear", "world"):
            raise ValueError(f"no such road: types={types!r} band={band!r} none={none!r}")
        self.L, self.mode, self.band, self.mature, self.none = L, types, band, bool(mature), none
        self.ear = L.ear

    def held_words(self, x: np.ndarray) -> List[str]:
        """The road's «what is this?» (§1 b, c): every word whose band — the READER's per learned type, or S1b-1's diagonal
        — holds the thing; with production maturity, only the MATURE words (a young word is never emitted)."""
        L = self.L
        Z = L.stats.standardise(np.atleast_2d(x))[:1]
        if self.band == "diag":
            out = L.held(Z, "diag")
        else:
            st = L.reader[self.mode]
            D = L.reader_distances(Z, self.mode)[0]
            out = [w for w in L.words if w in st["word"] and st["word"][w]["band"] is not None
                   and D[L.index[w]] <= st["word"][w]["band"]]
        if self.mature:
            out = [w for w in out if L.meetings[L.index[w]] >= L.p_from]
        return out

    def answer_point(self, X: np.ndarray, phrase: Sequence[str], rng: np.random.Generator) -> Dict[str, object]:
        """The learner's own pointing, unchanged (young words point as S1a's); «none» is the road's: τ_point (none_i, §1 d)
        or S1b-1's distance flag."""
        a = self.L.answer_point(X, phrase, rng)
        if self.none == "tau_point" and a.get("point") is not None:
            a = dict(a)
            a["none"] = a["none_i"]
        return a

    def types(self) -> List[Tuple[str, ...]]:
        return list(self.L.reader[self.mode]["types"])

    def believed(self, X: np.ndarray) -> List[List[Optional[str]]]:
        """Per learned type T, per hypothesis h: b_T(h) = the argmax over T's MATURE words of the learner's own log p_w(h)
        (the delta-rule score name_forced reads); an exact tie → the first word of T's sorted tuple."""
        L = self.L
        Z = L.stats.standardise(np.atleast_2d(X))
        lp = L.logp_answer(Z, getattr(L, "_bands_cache", None))
        out: List[List[Optional[str]]] = []
        for T in self.types():
            cand = [w for w in T if w in L.index and L.meetings[L.index[w]] >= L.p_from]
            if not cand:
                out.append([None] * Z.shape[0])
                continue
            cols = lp[:, [L.index[w] for w in cand]]
            out.append([cand[int(k)] for k in np.argmax(cols, axis=1)])
        return out

    def sayable(self, x: np.ndarray, w: str) -> bool:
        return w in self.held_words(x)

    def one_alone(self) -> Optional[int]:
        return self.L.reader[self.mode]["one_alone"]


class OracleRoad:
    """P-ORACLE / ORACLE-TRUTH through the new mouth (PREREG-S1B1R §3): its believed names are its per-type FORCED names
    (the argmax of its within-type posterior over its MATURE classes — ≥ 3 showings; an exact tie → the reader's class
    order); SAYABLE = its own per-type distance band holds the thing; its pointing and «none» (its τ_point at 0.95) are its
    own; it knows the types (the caller's order). The one-alone type from its ear, as the learner's."""

    def __init__(self, R: "TypedLDAReader", order: Sequence[str] = ("shape", "colour", "size")):
        self.R, self.ear = R, R.ear
        self.order = [t for t in order if t in R.readers]

    def _mature(self, t: str) -> List[int]:
        r = self.R.readers[t]
        return [k for k, c in enumerate(r.counts) if c >= P_FROM_MEETING]

    def types(self) -> List[Tuple[str, ...]]:
        return [tuple(sorted(self.R.readers[t].names[k] for k in self._mature(t))) for t in self.order]

    def believed(self, X: np.ndarray) -> List[List[Optional[str]]]:
        X = np.atleast_2d(X)
        out: List[List[Optional[str]]] = []
        for t in self.order:
            ks = self._mature(t)
            if not ks:
                out.append([None] * X.shape[0])
                continue
            lp = self.R._log_post(t, X)[:, ks]
            out.append([self.R.readers[t].names[ks[int(k)]] for k in np.argmax(lp, axis=1)])
        return out

    def sayable(self, x: np.ndarray, w: str) -> bool:
        return w in self.R.what_is_this(x)

    def held_words(self, x: np.ndarray) -> List[str]:
        return self.R.what_is_this(x)

    def answer_point(self, X: np.ndarray, phrase: Sequence[str], rng: np.random.Generator) -> Dict[str, object]:
        return self.R.answer_point(X, phrase, rng)

    def one_alone(self) -> Optional[int]:
        counts = [sum(self.ear.alone.get(w, 0) for w in T) for T in self.types()]
        return int(np.argmax(counts)) if counts and max(counts) > 0 else None


# edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05 13:21 +0400 — PREREG-MOUTH-CAP §2 (signed, this branch's first commit):
# the mouth's declared candidate budget — read-backs per produce_believed call (AMENDMENT 1: the expensive unit, the
# pilot's measured 4.7 ms each — 4,096 ≈ 19.3 s worst; ≈ 585 × the closed record's measured maximum of 7, the law's item 2).
# A constant, never a genome line (#221's form: a knob would re-hash every life).
MOUTH_BUDGET = 4096

# PREREG-MOUTH-CAP AMENDMENT 2 (same edit): at len(say) ≤ MOUTH_FULL_BELOW the OLD enumeration runs verbatim (2¹²−1 =
# 4,095 ≤ MOUTH_BUDGET — the full enumeration can never exceed the budget, and the record's say ≤ 3 sits deep inside);
# the capped path exists only where no closed record can reach.
MOUTH_FULL_BELOW = 12


def _combos(seq: list, k: int):
    """Index combinations in lexicographic order — itertools.combinations' own form with no import (the learner
    modules' import fence, tests/brain/scene/test_truth_fence.py)."""
    n = len(seq)
    if k < 0 or k > n:
        return
    idx = list(range(k))
    while True:
        yield tuple(seq[i] for i in idx)
        for i in range(k - 1, -1, -1):
            if idx[i] != i + n - k:
                break
        else:
            return
        idx[i] += 1
        for j in range(i + 1, k):
            idx[j] = idx[j - 1] + 1


def produce_believed(road, X: np.ndarray, target: int, rng_factory, budget: int = MOUTH_BUDGET) -> Dict[str, object]:
    """THE MOUTH SAYS WHAT IT BELIEVES (PREREG-S1B1R §1 e as Fable's edit reads it) — the SAME code for every arm, over
    its ROAD (`types()`, `believed(X)`, `sayable(x, w)`, `answer_point(X, phrase, rng)` with the road's «none», `ear`,
    `one_alone()`):
      1. per learned type T the BELIEVED name b_T(h) of every hypothesis; b_T(target) is SAYABLE iff the road's band holds
         the target — otherwise T is silent for it;
      2. a candidate = a non-empty subset of the sayable believed names; believed-UNIQUE iff no OTHER hypothesis has, for
         every word of it, the same believed name in that word's type (categorical: no δ, no continuous margin; the
         others' names are their argmax names, no band — AMENDMENT 1 §4 g);
      3. ACCEPTED iff believed-unique AND the read-back — the arm's own pointing, a fresh item tie generator per candidate,
         an exact tie broken by it as everywhere — puts the target first AND «none» does not fire;
      4. spoken = the SHORTEST accepted; ties → the largest read-back margin (+∞ with one hypothesis in view) → a candidate
         holding a word of the type the ear hears ALONE most often → the ear's order keys → first-heard; the phrase is in
         the ear's order;
      5. none accepted → «I cannot say it yet», one reason (declared priority): «no sayable word»; «no believed-unique
         phrase»; «none» when a believed-unique candidate read back to the target with «none» firing; else «the read-back».
    The read-back's point and the target are RECORDED, so the grader re-checks the wiring (READ-BACK 1.000).

    PREREG-MOUTH-CAP §2 + AMENDMENTS 1–2 (edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05): TWO branches at
    `MOUTH_FULL_BELOW`. At len(say) ≤ 12 the OLD enumeration runs VERBATIM (2¹²−1 = 4,095 ≤ `MOUTH_BUDGET` — the full
    enumeration can never exceed the budget; the closed record's say ≤ 3 sits deep inside: every returned key and counter
    is byte-identical to the old code's, on the ASK road's journaled raw too). At len(say) > 12 — where no closed record
    can reach — the enumeration is LENGTH-ORDERED under the declared budget: candidates per length class k = 1 … len(say)
    (`_combos` — never a materialized 2^N list); the uniqueness filter runs for EVERY candidate (exact `n_unique` wherever
    the budget does not bind — the old code paid the same 2^N pass with a list on top); the read-backs of a class run
    whole and the enumeration stops after the FIRST class holding ≥ 1 accepted — the same winner as the full enumeration
    BY the rank's own first key (length), with the within-class evaluation complete for the margin tie-break. `budget`
    counts READ-BACKS (the expensive unit, the pilot's measured 4.7 ms); spent mid-class it DISCARDS the partial class
    whole (AMENDMENT 3: its evaluated accepted could be beaten by the unevaluated part's margin) and the result is the
    DECLARED OVERFLOW FORM: `spoken None`, `reason "the mouth's budget"` — the mouth says NOTHING, never a different
    phrase. The parameter exists so tests
    exercise the budget path small; every organism call site uses the default (G-CALLERS). On the capped path
    `n_candidates` stays exact (2^len(say) − 1, arithmetic) and `n_accepted` on the early-stopped path reports the first
    accepted class (the prefix), under `"exhaustive": false`."""
    X = np.atleast_2d(X)
    t = int(target)
    n_hyp = X.shape[0]
    types = [tuple(T) for T in road.types()]
    B = road.believed(X)
    base: Dict[str, object] = {"target": t, "believed": {str(k): B[k][t] for k in range(len(types)) if B[k][t] is not None},
                               "sayable": [], "n_candidates": 0, "n_unique": 0, "n_accepted": 0}
    say = [(k, B[k][t]) for k in range(len(types)) if B[k][t] is not None and road.sayable(X[t], B[k][t])]
    base["sayable"] = [w for _k, w in say]
    if not say:
        return {"spoken": None, "reason": "no sayable word", **base}
    one = road.one_alone()
    ear = road.ear
    if len(say) <= MOUTH_FULL_BELOW:
        # PREREG-MOUTH-CAP AMENDMENT 2: the OLD enumeration VERBATIM — every class, every read-back, the old dict's own
        # keys; 2¹²−1 ≤ MOUTH_BUDGET, so the budget can never bind here, and the closed record (say ≤ 3) sits deep inside.
        cands = [[say[i] for i in range(len(say)) if mask >> i & 1] for mask in range(1, 1 << len(say))]
        uniq = [c for c in cands if not any(all(B[k][h] == w for k, w in c) for h in range(n_hyp) if h != t)]
        base["n_candidates"], base["n_unique"] = len(cands), len(uniq)
        if not uniq:
            return {"spoken": None, "reason": "no believed-unique phrase", **base}
        accepted = []
        fired = 0
        for c in uniq:
            phrase = ear.order([w for _k, w in c])
            a = road.answer_point(X, phrase, rng_factory())
            if a.get("point") is None or int(a["point"]) != t:
                continue
            if a.get("none"):
                fired += 1
                continue
            sc = np.asarray(a["scores"], dtype=np.float64)
            others = np.delete(sc, t)
            margin = float(sc[t] - np.max(others)) if others.size else float("inf")
            alone = 0 if (one is not None and any(k == one for k, _w in c)) else 1
            rank = (len(phrase), -margin, alone, tuple(ear.key(w) for w in phrase),
                    tuple(ear.first.get(w, 10 ** 6) for w in phrase))
            accepted.append((rank, phrase, int(a["point"]), margin))
        base["n_accepted"] = len(accepted)
        if not accepted:
            return {"spoken": None, "reason": "none" if fired else "the read-back", **base}
        accepted.sort(key=lambda z: z[0])
        _rank, phrase, point, margin = accepted[0]
        return {"spoken": list(phrase), "reason": None, "readback_point": point, "margin": margin, **base}
    # len(say) > MOUTH_FULL_BELOW — the capped path (AMENDMENT 1): no closed record can reach here.
    base["n_candidates"] = (1 << len(say)) - 1
    fired = 0
    readbacks = 0
    n_unique = 0
    n_accepted = 0
    exhaustive = True
    winner = None
    for _k in range(1, len(say) + 1):
        accepted = []
        completed = True
        for c in _combos(say, _k):
            if any(all(B[tk][h] == w for tk, w in c) for h in range(n_hyp) if h != t):
                continue
            n_unique += 1
            if winner is not None:
                continue
            if readbacks >= budget:
                exhaustive = False
                completed = False
                break
            readbacks += 1
            phrase = ear.order([w for _tk, w in c])
            a = road.answer_point(X, phrase, rng_factory())
            if a.get("point") is None or int(a["point"]) != t:
                continue
            if a.get("none"):
                fired += 1
                continue
            sc = np.asarray(a["scores"], dtype=np.float64)
            others = np.delete(sc, t)
            margin = float(sc[t] - np.max(others)) if others.size else float("inf")
            alone = 0 if (one is not None and any(tk == one for tk, _w in c)) else 1
            rank = (len(phrase), -margin, alone, tuple(ear.key(w) for w in phrase),
                    tuple(ear.first.get(w, 10 ** 6) for w in phrase))
            accepted.append((rank, phrase, int(a["point"]), margin))
        if not completed:
            break        # AMENDMENT 3: a budget break discards the partial class WHOLE — the overflow form, never a partial-class winner
        n_accepted += len(accepted)
        if accepted:
            accepted.sort(key=lambda z: z[0])
            winner = accepted[0]
    base["n_unique"], base["n_accepted"] = n_unique, n_accepted
    base["exhaustive"] = exhaustive
    base["n_readbacks"] = readbacks
    if winner is not None:
        _rank, phrase, point, margin = winner
        return {"spoken": list(phrase), "reason": None, "readback_point": point, "margin": margin, **base}
    if not exhaustive:
        return {"spoken": None, "reason": "the mouth's budget", "n_say": len(say), "budget": int(budget), **base}
    if n_unique == 0:
        return {"spoken": None, "reason": "no believed-unique phrase", **base}
    return {"spoken": None, "reason": "none" if fired else "the read-back", **base}


# edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05 17:4x +0400 — PREREG-MOUTH-INCREMENTAL §2 (signed): THE MOUTH
# THE HUMAN WAY — additive; produce_believed above is byte-untouched. The mechanism (RESEARCH-HUMAN-MOUTH-MECHANISM.md):
# walk the sayable words in the road's preference order ONCE; skip a word that rules out nothing (Relevance, free);
# add a word, ask the hearer model (the read-back) after EACH addition; stop at the first sufficiency; never unsay
# (indelibility); the list exhausted → the honest bail-out. ≤ len(say) read-backs ALWAYS — the 2^N enumeration is
# nowhere. `budget` is the cap law's belt under the mechanism's braces (its breach needs say > MOUTH_BUDGET — named
# unreachable on any measured stream, kept for the form).
def produce_incremental(road, X: np.ndarray, target: int, rng_factory, budget: int = MOUTH_BUDGET) -> Dict[str, object]:
    """THE INCREMENTAL MOUTH (PREREG-MOUTH-INCREMENTAL §2): the human production mechanism at machine level —
      1. the SAME sayable believed names as produce_believed (the same road, the same believed map, the same sayable
         rule — the preference order is the road's type order);
      2. RELEVANCE: a word every OTHER hypothesis believes the same name for (in its type) rules out nothing —
         SKIPPED, no read-back spent, counted in `skipped`;
      3. INCREMENT: add the word; ONE read-back of the phrase so far; ACCEPTED (speak) iff it points at the target
         first and «none» does not fire — the hearer model's own sufficiency test;
      4. INDELIBLE: a word once added is never removed, whatever a later word could do alone;
      5. the list exhausted without sufficiency → `spoken None`, `reason "the read-back"`; the budget breached →
         `reason "the mouth's budget"` (the cap law's declared string, verbatim).
    The row: the old keys (`target`, `believed`, `sayable`, `spoken`, `reason`, `readback_point`, `margin`) plus the
    mechanism's own (`n_say`, `n_readbacks` — ALWAYS ≤ len(say), `skipped`, `added`). The margin is computed at the
    stopping read-back, as everywhere (a reading)."""
    X = np.atleast_2d(X)
    t = int(target)
    n_hyp = X.shape[0]
    types = [tuple(T) for T in road.types()]
    B = road.believed(X)
    base: Dict[str, object] = {"target": t, "believed": {str(k): B[k][t] for k in range(len(types)) if B[k][t] is not None},
                               "sayable": []}
    say = [(k, B[k][t]) for k in range(len(types)) if B[k][t] is not None and road.sayable(X[t], B[k][t])]
    base["sayable"] = [w for _k, w in say]
    base.update({"n_say": len(say), "n_readbacks": 0, "skipped": [], "added": []})
    if not say:
        return {"spoken": None, "reason": "no sayable word", **base}
    ear = road.ear
    phrase: List[str] = []
    for k, w in say:
        if n_hyp > 1 and all(B[k][h] == w for h in range(n_hyp) if h != t):
            base["skipped"].append(w)          # Relevance: rules out nothing (EVERY other hypothesis believes it) — never said, never read back
            # (AMENDMENT 1: only WITH distractors — an empty contrast set needs no discriminatory power; the human says the type name)
            continue
        phrase = ear.order(phrase + [w])       # indelible: once added, never removed
        base["added"].append(w)
        if base["n_readbacks"] >= budget:
            return {"spoken": None, "reason": "the mouth's budget", "budget": int(budget), **base}
        base["n_readbacks"] += 1
        a = road.answer_point(X, phrase, rng_factory())
        if a.get("point") is None or int(a["point"]) != t or a.get("none"):
            continue                           # not sufficient yet — keep walking (the human keeps talking)
        sc = np.asarray(a["scores"], dtype=np.float64)
        others = np.delete(sc, t)
        margin = float(sc[t] - np.max(others)) if others.size else float("inf")
        return {"spoken": list(phrase), "reason": None, "readback_point": int(a["point"]), "margin": margin, **base}
    return {"spoken": None, "reason": "the read-back", **base}


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
