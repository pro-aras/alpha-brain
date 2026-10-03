"""compress.py — TOY C's compressor: a two-part code of the utterance sequence, the SAME code for every rule (docs/research/toys/PREREG-TOY-FRAMES.md §1).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 16:49 +0400 — new module, red-first against tests/tools/test_toys_frames.py (stage 1); every number the tests pin was worked by
# hand in the test's own comments, never by calling this code.

THE CODE (law §1). Data: moments (utterances) as word sequences; the first 60 % TRAIN, the rest HELD-OUT. A frame is an ORDERED pair (a, b). The PARSE: inside a moment, left
to right, a position whose next two words are a frame in F becomes ONE frame token and consumes both, else one word token; the parse never crosses a moment, and every
moment's tokens are followed by ONE END token (the code is self-delimiting: a decoder is handed no boundaries). The token's probability is its TRAIN-parse count, add-one
smoothed over the inventory words ∪ frames ∪ UNK ∪ END:

    p(t) = (c_t + 1) / (N + K)       N = the train tokens INCLUDING the END tokens;  K = V + |F| + 2  (V = the distinct train words);

a held-out word never seen in train is UNK. A frame that never fires and a word that vanishes as a token under F both stay in the inventory (K counts them). The model
cost of F is L(F) = |F| · 2 · log2 V bits, and the gain on text it never saw is G(F) = bits(held-out | ∅) − bits(held-out | F) − L(F); G(∅) = 0 exactly.

The TRAIN self-code (what MDL-GREEDY minimises) has the closed form  bits(train | F) = N log2(N + K) − Σ_t c_t log2(c_t + 1)  (train_bits below).

`slow_gain` is a literal re-computation written in another shape (explicit inventory, exact rationals for every p): TestFastEqualsSlow pins the two together to 1e-9, and
`Scorer` is never trusted without it (law G3).
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Iterable, List, Mapping, Sequence, Set, Tuple

Frame = Tuple[str, str]
END = "\x00END"        # tokens no word can equal (words are printable text)
UNK = "\x00UNK"


def parse_moment(words: Sequence[str], frames) -> list:
    """The leftmost-greedy, non-overlapping parse of one moment under the frame set, followed by END."""
    out: list = []
    i, n = 0, len(words)
    while i < n:
        if i + 1 < n and (words[i], words[i + 1]) in frames:
            out.append((words[i], words[i + 1]))
            i += 2
        else:
            out.append(words[i])
            i += 1
    out.append(END)
    return out


def train_bits(counts: Mapping[object, int], n_tokens: int, k: int) -> float:
    """bits(train | F) = N log2(N + K) − Σ c log2(c + 1): the train's own code length under its own add-one model (tokens with c = 0 contribute nothing)."""
    s = 0.0
    for c in counts.values():
        if c > 0:
            s += c * math.log2(c + 1)
    return n_tokens * math.log2(n_tokens + k) - s


@dataclass(frozen=True)
class Gain:
    G: float
    L: float
    bits0: float
    bitsF: float
    N: int
    K: int
    V: int
    n_held_words: int

    @property
    def per_word(self) -> float:
        return self.G / self.n_held_words if self.n_held_words else 0.0


class Scorer:
    """Scores frame sets against ONE train/held-out split. Holds no state a call changes: gain(F) is a pure function of F."""

    def __init__(self, train: Sequence[Sequence[str]], held: Sequence[Sequence[str]], parse=None):
        # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:57 +0400 — the optional `parse` hook (default: parse_moment, behaviour unchanged): AMENDMENT-1 §1.4's gate control needs a compressor whose
        # parse never fires a frame, and a hook is cleaner than patching a module at run time.
        self._parse = parse if parse is not None else parse_moment
        self.train: List[Tuple[str, ...]] = [tuple(m) for m in train]
        self.held: List[Tuple[str, ...]] = [tuple(m) for m in held]
        if not self.train:
            raise ValueError("Scorer: an empty train part")
        self.vocab: Set[str] = {w for m in self.train for w in m}
        self.V = len(self.vocab)
        self.n_held_words = sum(len(m) for m in self.held)
        self._tb: Counter | None = None
        self._hb: Counter | None = None
        c0: Counter = Counter()
        for m in self.train:
            c0.update(m)
        c0[END] = len(self.train)
        self._c0 = c0
        self._n0 = sum(c0.values())                                   # N under ∅ = train words + one END a moment
        self._bits0 = self._held_bits(c0, self._n0, self.V + 2, frozenset())

    @property
    def n0(self) -> int:
        """N under the empty frame set: the train words plus one END a moment (the architect's 17:0x expected-value reading of the PLANT gate prints it)."""
        return self._n0

    # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:03 +0400 — the public `n0` above (plants.py's expected-value reading needs N_train); nothing else in this file changes.
    # -- the held-out code length under a train model (counts, N, K) and a frame set ------------------------------------------------
    def _held_bits(self, counts: Mapping[object, int], n: int, k: int, frames) -> float:
        d = math.log2(n + k)
        held_tokens: Counter = Counter()
        vocab = self.vocab
        for m in self.held:
            for t in self._parse(m, frames):
                if isinstance(t, str) and t != END and t not in vocab:
                    t = UNK
                held_tokens[t] += 1
        bits = 0.0
        for t, c in held_tokens.items():
            bits += c * (d - math.log2(counts.get(t, 0) + 1))
        return bits

    # -- the gain --------------------------------------------------------------------------------------------------------------------
    def gain(self, frames) -> Gain:
        F = frozenset(frames)
        if not F:
            return Gain(0.0, 0.0, self._bits0, self._bits0, self._n0, self.V + 2, self.V, self.n_held_words)
        cF: Counter = Counter()
        for m in self.train:
            cF.update(self._parse(m, F))
        n = sum(cF.values())
        k = self.V + len(F) + 2
        bits_f = self._held_bits(cF, n, k, F)
        L = len(F) * 2 * math.log2(self.V)
        return Gain(self._bits0 - bits_f - L, L, self._bits0, bits_f, n, k, self.V, self.n_held_words)

    # -- adjacency (inside a moment only) ---------------------------------------------------------------------------------------------
    @staticmethod
    def _bigrams(moments: Sequence[Sequence[str]]) -> Counter:
        c: Counter = Counter()
        for m in moments:
            for i in range(len(m) - 1):
                c[(m[i], m[i + 1])] += 1
        return c

    def train_bigrams(self) -> Counter:
        if self._tb is None:
            self._tb = self._bigrams(self.train)
        return self._tb

    def held_bigrams(self) -> Counter:
        if self._hb is None:
            self._hb = self._bigrams(self.held)
        return self._hb

    def train_adjacent(self, pair: Frame) -> int:
        return int(self.train_bigrams().get(tuple(pair), 0))

    def held_adjacent(self, pair: Frame) -> int:
        return int(self.held_bigrams().get(tuple(pair), 0))


# ================================================================================================================== the slow reference
def _slow_tokens(moment: Sequence[str], frames) -> list:
    toks: list = []
    skip = False
    for i, w in enumerate(moment):
        if skip:
            skip = False
            continue
        nxt = moment[i + 1] if i + 1 < len(moment) else None
        if nxt is not None and (w, nxt) in frames:
            toks.append((w, nxt))
            skip = True
        else:
            toks.append(w)
    toks.append(END)
    return toks


def _slow_code(train, held, frames) -> Tuple[float, int, int, int, int]:
    """(held-out bits, N, K, V, held-out words) under `frames`, by an explicit inventory and exact rational probabilities."""
    vocabulary = set()
    for m in train:
        for w in m:
            vocabulary.add(w)
    inventory = set(vocabulary) | set(frames) | {UNK, END}
    counts = {t: 0 for t in inventory}
    n_tokens = 0
    for m in train:
        for t in _slow_tokens(m, frames):
            counts[t] += 1                                     # a token outside the inventory is a KeyError: the reference cannot silently invent one
            n_tokens += 1
    k = len(inventory)
    bits = 0.0
    n_words = 0
    for m in held:
        n_words += len(m)
        for t in _slow_tokens(m, frames):
            if isinstance(t, str) and t != END and t not in vocabulary:
                t = UNK
            bits += -math.log2(Fraction(counts[t] + 1, n_tokens + k))
    return bits, n_tokens, k, len(vocabulary), n_words


def slow_gain(train, held, frames) -> Dict[str, float]:
    F = set(frames)
    bits0, _n0, _k0, v, n_words = _slow_code(train, held, set())
    bits_f, n, k, v2, _w = _slow_code(train, held, F)
    L = len(F) * 2 * math.log2(v) if F else 0.0
    return {"G": bits0 - bits_f - L, "bits0": bits0, "bitsF": bits_f, "L": L, "N": n, "K": k, "V": v2, "n_held_words": n_words}


def slow_train_bits(train, frames) -> Tuple[float, int, int]:
    """bits(train | F) by the literal sum Σ −log2 p(t) over the train's own tokens (exact rationals): the reference for train_bits and for MDL-GREEDY's incremental gain."""
    F = set(frames)
    vocabulary = {w for m in train for w in m}
    inventory = set(vocabulary) | F | {UNK, END}
    counts = {t: 0 for t in inventory}
    toks: list = []
    for m in train:
        for t in _slow_tokens(m, F):
            counts[t] += 1
            toks.append(t)
    n, k = len(toks), len(inventory)
    bits = 0.0
    for t in toks:
        bits += -math.log2(Fraction(counts[t] + 1, n + k))
    return bits, n, k
