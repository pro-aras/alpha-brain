"""anatomy.py — an exact split of a frame set's gain into its parts: G(F) = M + D + C − L (the architect's 17:1x RAISE; AMENDMENT-1 §1.3).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:45 +0400 — new module, red-first against tests/tools/test_toys_frames_anatomy.py (stage 3d).

bits(held | empty) − bits(held | F) is a sum over the held-out tokens. A held-out FRAME token (a firing) saves cost0(a) + cost0(b) − costF(frame): that is M, the held-out MERGE savings. Every other
held-out token (an unmerged word, an UNK, an END) costs cost0 − costF = log2((cF + 1) / (c0 + 1)) + log2((N0 + K0) / (NF + KF)): the first part is C, the COUNT-SHIFT loss (<= 0: the words a frame
consumed in train have lower train counts under F), the second part, D = (the number of unmerged held tokens) x log2((N0 + K0) / (NF + KF)), is the DENOMINATOR credit (> 0 when the frames
shortened the train's token count by more than they grew the inventory). T = D + C is «the train-merge term». The parts are exact: M + D + C − L equals the compressor's G.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Dict, Iterable

from .compress import END, UNK, Frame, Scorer, parse_moment


def decompose_gain(scorer: Scorer, frames: Iterable[Frame]) -> Dict[str, float]:
    F = frozenset(frames)
    g = scorer.gain(F)
    if not F:
        total = sum(len(m) + 1 for m in scorer.held)
        return {"M": 0.0, "D": 0.0, "C": 0.0, "L": 0.0, "T": 0.0, "G": 0.0, "firings": 0, "unmerged": total, "N0": g.N, "NF": g.N, "delta": 0.0}
    empty: frozenset = frozenset()
    c0: Counter = Counter()
    cF: Counter = Counter()
    for m in scorer.train:
        c0.update(parse_moment(m, empty))
        cF.update(parse_moment(m, F))
    n0, k0 = sum(c0.values()), scorer.V + 2
    nF, kF = g.N, g.K
    vocab = scorer.vocab
    delta = math.log2((n0 + k0) / (nF + kF))

    def cost(counts, t, n, k) -> float:
        return -math.log2((counts.get(t, 0) + 1) / (n + k))

    def mapw(w: str) -> str:
        return w if w in vocab else UNK

    M = C = 0.0
    firings = unmerged = 0
    for m in scorer.held:
        for t in parse_moment(m, F):
            if isinstance(t, tuple):
                a, b = t
                M += cost(c0, mapw(a), n0, k0) + cost(c0, mapw(b), n0, k0) - cost(cF, t, nF, kF)
                firings += 1
            else:
                tt = t if (t == END or t in vocab) else UNK
                unmerged += 1
                C += math.log2((cF.get(tt, 0) + 1) / (c0.get(tt, 0) + 1))
    D = unmerged * delta
    return {"M": M, "D": D, "C": C, "L": g.L, "T": D + C, "G": g.G, "firings": firings, "unmerged": unmerged, "N0": n0, "NF": nF, "delta": delta}
