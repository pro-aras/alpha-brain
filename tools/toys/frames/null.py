"""null.py — TOY C's two nulls (docs/research/toys/PREREG-TOY-FRAMES.md §3, AMENDMENT-1 §4 (a)-(b)).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:24 +0400 — new module, red-first against tests/tools/test_toys_frames_null.py (stage 3b).
# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 23:16 +0400 — NULL-2's pick is now `_BigramPool` (numpy exclusion masks): BYTE-IDENTICAL to the old `_pick_bigram` (kept below, unchanged, as the REFERENCE) in picks,
# fallback flags AND generator consumption, proved by tests/tools/test_toys_frames_null_pick.py (synthetic bins of every branch, the real ALPHA4 bins and frame sets, the generator state compared after
# every pick, six planted one-line changes caught). Why: the REAL gates stopped at G5 (predicted unit CPU 182.1 min against 40): the old pick ran its 1,000-try rejection loop to its end on 892 of WEB-H's
# 1,430 real picks. No law text changes (the law pins the keys and the matching rule, not the loop).

NULL-1 (the null of the GAIN bar, the DEALT set): for a rule's set F of k frames, a set F' of k pairs: each frame (a, b) is replaced by (a', b') with a' drawn uniformly from the
words whose TRAIN count is in the same log2 bin (width 0.5, bin = floor(2 log2 count)) as a's, b' likewise, (a', b') not in F, not (a, b), and the k replacements DISTINCT (so |F'| = k).
It ablates the PAIRING, not adjacency: a chance word pair almost never stands adjacent inside a moment, so its frame never fires (the law says so itself, which is why NULL-2 exists).

NULL-2 (the ABLATED SELECTION CRITERION, a reading): each frame is replaced by an ADJACENT train bigram (any distinct ordered pair seen adjacent inside a train moment) whose own train
adjacent count is in the same log2 bin as the frame's OWN adjacent count (a frame never adjacent counts as 1: the lowest bin), not in F, not the frame, the k replacements distinct.

A bin without an admissible replacement falls back to the NEAREST bins by index distance (NULL-1: both sides widened by d bins; NULL-2: the two bins at distance d pooled), and every
fallback pick is counted (printed per rule). Draws: default_rng([20261103, rule_tag, seed]) (NULL-1), default_rng([20261103, rule_tag, seed, 2]) (NULL-2); frames are dealt in sorted
order. The statistic of a draw is the compressor's G(F'); q95 = numpy.percentile(values, 95) (linear), sd with ddof = 1.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import numpy as np

from .compress import Frame, Scorer

SEED_ROOT = 20261103
SMALL_ENUM = 64          # a candidate set this small is enumerated; a larger one is rejection-sampled (uniform over the admissible ones either way)
MAX_REJECT = 1000
ENUM_LIMIT = 1_000_000


class NullError(Exception):
    pass


def log2_bin(count: int) -> int:
    """floor(2 log2 count): the bin of width 0.5 in log2 a count belongs to."""
    if count < 1:
        raise ValueError(f"log2_bin: a count must be >= 1, got {count}")
    return int(math.floor(2.0 * math.log2(count)))


def word_bins(scorer: Scorer) -> Dict[int, List[str]]:
    """The train words by the bin of their train count, each bin sorted."""
    counts: Counter = Counter()
    for m in scorer.train:
        counts.update(m)
    bins: Dict[int, List[str]] = {}
    for w in sorted(counts):
        bins.setdefault(log2_bin(counts[w]), []).append(w)
    return bins


def bigram_bins(scorer: Scorer) -> Dict[int, List[Frame]]:
    """The distinct adjacent train bigrams by the bin of their own adjacent count, each bin sorted."""
    tb = scorer.train_bigrams()
    bins: Dict[int, List[Frame]] = {}
    for p in sorted(tb):
        bins.setdefault(log2_bin(tb[p]), []).append(p)
    return bins


@dataclass(frozen=True)
class NullResult:
    kind: str
    draws: int
    k: int
    values: Tuple[float, ...]
    fallbacks: int
    pairs: Optional[Tuple[Tuple[Frame, ...], ...]] = None

    @property
    def mean(self) -> float:
        return float(np.mean(self.values))

    @property
    def sd(self) -> float:
        return float(np.std(self.values, ddof=1)) if len(self.values) > 1 else 0.0

    @property
    def q95(self) -> float:
        return float(np.percentile(np.asarray(self.values), 95))

    def read(self, G: float) -> Dict[str, object]:
        sd = self.sd
        return {"G": G, "mean": self.mean, "sd": sd, "q95": self.q95, "z": ((G - self.mean) / sd if sd > 0 else None), "beats_q95": G > self.q95,
                "fallbacks": self.fallbacks, "draws": self.draws, "k": self.k}


# ------------------------------------------------------------------------------------------------------------------ the pickers
def _span(bins: Dict[int, list], lo: int, hi: int) -> list:
    out: list = []
    for b in range(lo, hi + 1):
        x = bins.get(b)
        if x:
            out.extend(x)
    return out


def _pick_pair(rng, bins: Dict[int, List[str]], ba: int, bb: int, excluded: Set[Frame], lo: int, hi: int) -> Tuple[Frame, bool]:
    for d in range(0, (hi - lo) + 2):
        A = bins.get(ba, []) if d == 0 else _span(bins, ba - d, ba + d)
        B = bins.get(bb, []) if d == 0 else _span(bins, bb - d, bb + d)
        if not A or not B:
            continue
        n = len(A) * len(B)
        if n > SMALL_ENUM:
            for _ in range(MAX_REJECT):
                x = A[int(rng.integers(len(A)))]
                y = B[int(rng.integers(len(B)))]
                if (x, y) not in excluded:
                    return (x, y), d > 0
            if n > ENUM_LIMIT:
                continue
        valid = [(x, y) for x in A for y in B if (x, y) not in excluded]
        if valid:
            return valid[int(rng.integers(len(valid)))], d > 0
    raise NullError(f"NULL-1: no admissible pair in any bin for bins ({ba}, {bb})")


# REFERENCE (the oracle of tests/tools/test_toys_frames_null_pick.py): not called by `null2` since the speed-up of the `_BigramPool` below; this body is unchanged from commit 724865d.
def _pick_bigram(rng, bins: Dict[int, List[Frame]], b0: int, excluded: Set[Frame], lo: int, hi: int) -> Tuple[Frame, bool]:
    for d in range(0, (hi - lo) + 2):
        lists = [bins.get(b0, [])] if d == 0 else [bins.get(b0 - d, []), bins.get(b0 + d, [])]
        total = sum(len(x) for x in lists)
        if total == 0:
            continue
        if total > SMALL_ENUM:
            for _ in range(MAX_REJECT):
                r = int(rng.integers(total))
                for x in lists:
                    if r < len(x):
                        pick = x[r]
                        break
                    r -= len(x)
                if pick not in excluded:
                    return pick, d > 0
        admissible = [p for x in lists for p in x if p not in excluded]
        if admissible:
            return admissible[int(rng.integers(len(admissible)))], d > 0
    raise NullError(f"NULL-2: no admissible adjacent bigram in any bin for bin {b0}")


class _BigramPool:
    """NULL-2's pool as numpy exclusion masks: the SAME picks and the SAME generator consumption as `_pick_bigram`, without its Python loop of doomed rejection tries.

    The reference ran its MAX_REJECT-try rejection loop to its end whenever a bin of more than SMALL_ENUM entries had every entry excluded, or nearly every one (on the real ALPHA4 split 892 of WEB-H's 1,430
    picks, about 3 ms each: G5's price). Level by level, in the reference's own order (d = 0, 1, ...; the lower bin's entries before the upper's), this does the same draws:
      - a level whose bins hold at most SMALL_ENUM entries together is ENUMERATED: the admissible entries, one integers() over their number;
      - a larger level with NO admissible entry would have burned MAX_REJECT tries and found `admissible` empty: it draws those MAX_REJECT integers in ONE vectorised call (the same stream: the tests compare
        the whole generator state after every pick) and goes on;
      - a larger level with some admissible entries draws the MAX_REJECT tries in one call and takes the first accepted one; the generator is then RESTORED to its state before the batch and the tries the
        reference would have made (j + 1) are redrawn, so the consumption is identical; if none is accepted the level is enumerated, as the reference does after its loop.
    The caller drives it as `null2` does: `reset(base)` at the start of a draw, `exclude(pick)` after every pick."""

    def __init__(self, bins: Dict[int, List[Frame]]):
        self.bins = bins
        self.lo, self.hi = min(bins), max(bins)
        self.where: Dict[Frame, Tuple[int, int]] = {p: (b, i) for b, lst in bins.items() for i, p in enumerate(lst)}
        self.mask: Dict[int, np.ndarray] = {b: np.zeros(len(lst), dtype=bool) for b, lst in bins.items()}
        self.n_excl: Dict[int, int] = {b: 0 for b in bins}

    def reset(self, excluded: Iterable[Frame]) -> None:
        """Forget every exclusion, then exclude `excluded` (frames outside the pool matter to nothing)."""
        for b in self.mask:
            self.mask[b][:] = False
            self.n_excl[b] = 0
        for p in excluded:
            self.exclude(p)

    def exclude(self, p: Frame) -> None:
        w = self.where.get(p)
        if w is not None and not self.mask[w[0]][w[1]]:
            self.mask[w[0]][w[1]] = True
            self.n_excl[w[0]] += 1

    def _item(self, ks: List[int], sizes: List[int], r: int) -> Frame:
        for k, size in zip(ks, sizes):
            if r < size:
                return self.bins[k][r]
            r -= size
        raise IndexError(r)

    def pick(self, rng, b0: int) -> Tuple[Frame, bool]:
        bins, mask, n_excl = self.bins, self.mask, self.n_excl
        for d in range(0, (self.hi - self.lo) + 2):
            ks = [b0] if d == 0 else [b0 - d, b0 + d]
            ks = [k for k in ks if k in bins]
            sizes = [len(bins[k]) for k in ks]
            total = sum(sizes)
            if total == 0:
                continue
            m = mask[ks[0]] if len(ks) == 1 else np.concatenate([mask[k] for k in ks])
            if total > SMALL_ENUM:
                if total - sum(n_excl[k] for k in ks) == 0:
                    rng.integers(total, size=MAX_REJECT)
                    continue
                saved = rng.bit_generator.state
                r = rng.integers(total, size=MAX_REJECT)
                ok = ~m[r]
                if ok.any():
                    j = int(np.argmax(ok))
                    rng.bit_generator.state = saved
                    rng.integers(total, size=j + 1)
                    return self._item(ks, sizes, int(r[j])), d > 0
            adm = np.flatnonzero(~m)
            if adm.size:
                return self._item(ks, sizes, int(adm[int(rng.integers(adm.size))])), d > 0
        raise NullError(f"NULL-2: no admissible adjacent bigram in any bin for bin {b0}")


# ------------------------------------------------------------------------------------------------------------------ the draws
def null1(scorer: Scorer, F: Iterable[Frame], rule_tag: int, seed: int, draws: int = 100, keep_pairs: bool = False) -> NullResult:
    frames = sorted(set(F))
    if not frames:
        return NullResult("NULL-1", draws, 0, (0.0,) * draws, 0, tuple(() for _ in range(draws)) if keep_pairs else None)
    wb = word_bins(scorer)
    lo, hi = min(wb), max(wb)
    counts: Counter = Counter()
    for m in scorer.train:
        counts.update(m)
    try:
        own = [(log2_bin(counts[a]), log2_bin(counts[b])) if (a in counts and b in counts) else None for a, b in frames]
    except ValueError as e:
        raise NullError(str(e)) from None
    if any(o is None for o in own):
        raise NullError("NULL-1: a frame holds a word that is not in the train vocabulary")
    rng = np.random.default_rng([SEED_ROOT, int(rule_tag), int(seed)])
    base = set(frames)
    values: List[float] = []
    pairs: List[Tuple[Frame, ...]] = []
    fallbacks = 0
    for _ in range(draws):
        excluded = set(base)
        dealt: List[Frame] = []
        for (ba, bb) in own:
            p, fell = _pick_pair(rng, wb, ba, bb, excluded, lo, hi)
            excluded.add(p)
            dealt.append(p)
            fallbacks += int(fell)
        values.append(scorer.gain(set(dealt)).G)
        if keep_pairs:
            pairs.append(tuple(dealt))
    return NullResult("NULL-1", draws, len(frames), tuple(values), fallbacks, tuple(pairs) if keep_pairs else None)


def null2(scorer: Scorer, F: Iterable[Frame], rule_tag: int, seed: int, draws: int = 100, keep_pairs: bool = False) -> NullResult:
    frames = sorted(set(F))
    if not frames:
        return NullResult("NULL-2", draws, 0, (0.0,) * draws, 0, tuple(() for _ in range(draws)) if keep_pairs else None)
    bb = bigram_bins(scorer)
    if not bb:
        raise NullError("NULL-2: the train has no adjacent bigram at all")
    own = [log2_bin(max(1, scorer.train_adjacent(f))) for f in frames]
    pool = _BigramPool(bb)
    rng = np.random.default_rng([SEED_ROOT, int(rule_tag), int(seed), 2])
    base = set(frames)
    values: List[float] = []
    pairs: List[Tuple[Frame, ...]] = []
    fallbacks = 0
    for _ in range(draws):
        pool.reset(base)
        dealt: List[Frame] = []
        for b0 in own:
            p, fell = pool.pick(rng, b0)
            pool.exclude(p)
            dealt.append(p)
            fallbacks += int(fell)
        values.append(scorer.gain(set(dealt)).G)
        if keep_pairs:
            pairs.append(tuple(dealt))
    return NullResult("NULL-2", draws, len(frames), tuple(values), fallbacks, tuple(pairs) if keep_pairs else None)
