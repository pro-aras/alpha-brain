"""scene.py — TOY C's SCENE control: the generator's own probabilities, THE CEILING (G_max), the oracle, the χ² fit (G1) and G6's controls
(docs/research/toys/PREREG-TOY-FRAMES.md §3 THE CEILING, §7 G1 and G6; AMENDMENT-1 §4 (a), (f), (g)).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:43 +0400 — new module, red-first against tests/tools/test_toys_frames_scene.py (stage 3c).

THE GENERATOR (brain/scene/world.py, imported, never edited): a template uniform over T1 «shape», T2 «colour shape», T3 «size shape», T4 «size colour shape»; the referent's
(shape, colour) uniform over the 24 ALLOWED pairs; its size uniform over big / small. So P_gen(«shape») = ¼ · n_s/24, P_gen(«colour shape») = ¼ · [pair allowed]/24,
P_gen(«size shape») = ¼ · ½ · n_s/24, P_gen(«size colour shape») = ¼ · ½ · [pair allowed]/24 (n_s = the allowed pairs a shape has: 4 / 3 / 4 / 4 / 5 / 4). Any other utterance is
outside the support: a CeilingStop (the law: an utterance the four templates cannot produce is a STOP of the same kind as a ceiling violation).

THE CEILING: with the END token the code is self-delimiting, a code of the utterance sequence, so by the likelihood-ratio bound any code Q beats the generator's own code by b bits only
with probability <= 2^-b over the held-out part (independent of the train part F was chosen on): G_max = bits(held | empty) − Σ_i −log2 P_gen(u_i), and G(F) <= G_max + 20 is a false
stop with probability <= 2^-20. The gate is LOOSE (a unigram code's overhead over the generator is whole bits an utterance): it catches gross arithmetic errors only.
"""
from __future__ import annotations

import math
from typing import Dict, FrozenSet, Iterable, List, Sequence, Tuple

import numpy as np
from scipy import stats

from brain.scene import world as W

from . import compress as CO
from . import streams as ST

SEED_ROOT = 20261103
G6_TAG = 8                                    # G6 (a)'s replicate k: default_rng([20261103, 8, k])
SLACK = 20.0
P_FLOOR = 0.001                               # G1's χ² bar: each p > 0.001, else G_max is a reading, not a gate

SHAPES: Tuple[str, ...] = tuple(W.SHAPES)
COLOURS: Tuple[str, ...] = tuple(W.COLOUR_NAMES)
SIZES: Tuple[str, ...] = tuple(W.SIZE_NAMES)
ALLOWED: Tuple[Tuple[str, str], ...] = tuple(W.ALLOWED)                      # (shape, colour)
ALLOWED_SET: FrozenSet[Tuple[str, str]] = frozenset(ALLOWED)
HELDOUT_SET: FrozenSet[Tuple[str, str]] = frozenset(W.HELDOUT)
DAX_WORD: str = W.DAX_WORD
N_ALLOWED = len(ALLOWED)
N_S: Dict[str, int] = {s: sum(1 for (sh, _c) in ALLOWED if sh == s) for s in SHAPES}
N_C: Dict[str, int] = {c: sum(1 for (_s, cc) in ALLOWED if cc == c) for c in COLOURS}


class CeilingStop(Exception):
    """An utterance the generator cannot produce, or a G above G_max + 20: an INSTRUMENT ERROR; the run is void and stops until the cause is named in an amendment."""


# ------------------------------------------------------------------------------------------------------------------ the generator's probabilities
def p_gen(words: Sequence[str]) -> float:
    w = tuple(words)
    n = len(w)
    if n == 1:
        (s,) = w
        if s in N_S:
            return 0.25 * N_S[s] / N_ALLOWED
    elif n == 2:
        a, b = w
        if b in N_S:
            if a in N_C and (b, a) in ALLOWED_SET:
                return 0.25 / N_ALLOWED
            if a in SIZES:
                return 0.25 * 0.5 * N_S[b] / N_ALLOWED
    elif n == 3:
        a, b, c = w
        if a in SIZES and b in N_C and c in N_S and (c, b) in ALLOWED_SET:
            return 0.25 * 0.5 / N_ALLOWED
    raise CeilingStop(f"p_gen: {w!r} is not an utterance of the four templates")


def support() -> Dict[Tuple[str, ...], float]:
    out: Dict[Tuple[str, ...], float] = {}
    for s in SHAPES:
        out[(s,)] = p_gen((s,))
    for (s, c) in ALLOWED:
        out[(c, s)] = p_gen((c, s))
    for z in SIZES:
        for s in SHAPES:
            out[(z, s)] = p_gen((z, s))
    for z in SIZES:
        for (s, c) in ALLOWED:
            out[(z, c, s)] = p_gen((z, c, s))
    return out


def entropy() -> float:
    return -sum(p * math.log2(p) for p in support().values())


def h_length() -> float:
    by: Dict[int, float] = {}
    for u, p in support().items():
        by[len(u)] = by.get(len(u), 0.0) + p
    return -sum(p * math.log2(p) for p in by.values())


def h_given_length() -> float:
    return entropy() - h_length()


def g_max(held_words: Iterable[Sequence[str]], bits0: float) -> float:
    """G_max = bits(held | empty) − Σ_i −log2 P_gen(u_i) over the held-out utterances (CeilingStop on one the generator cannot produce)."""
    return bits0 - sum(-math.log2(p_gen(u)) for u in held_words)


def ceiling_violation(G: float, gmax: float, slack: float = SLACK) -> bool:
    return G > gmax + slack


def oracle_frames() -> FrozenSet[Tuple[str, str]]:
    """The 24 allowed (colour, shape) pairs in the order T2 and T4 say them (the structure the six exclusions leave)."""
    return frozenset((c, s) for (s, c) in ALLOWED)


# ------------------------------------------------------------------------------------------------------------------ a synthetic stream from the constants
def sample_moments(n: int, rng) -> List[ST.Moment]:
    out: List[ST.Moment] = []
    for i in range(n):
        tpl = int(rng.integers(4))
        s, c = ALLOWED[int(rng.integers(N_ALLOWED))]
        z = SIZES[int(rng.integers(len(SIZES)))]
        words = ((s,), (c, s), (z, s), (z, c, s))[tpl]
        out.append(ST.Moment("scene", f"syn{i:06d}", words, tuple(float(i * 10 + j) for j in range(len(words)))))
    return out


# ------------------------------------------------------------------------------------------------------------------ G1: the generator's marginals fit the stream
def chi2_checks(moments: Sequence[ST.Moment]) -> Dict[str, object]:
    """χ² goodness of fit of the template by length, the shape, colour and size marginals and the uniformity of the 24 pairs (each p > 0.001, else G_max is printed and not gated);
    the «dax» moment is excluded and counted; held-out pairs seen are counted (any one stops the gate)."""
    n = dax = 0
    len_c = [0, 0, 0]
    shape_c = {s: 0 for s in SHAPES}
    colour_c = {c: 0 for c in COLOURS}
    size_c = {z: 0 for z in SIZES}
    pair_c = {p: 0 for p in ALLOWED}
    heldout = 0
    for m in moments:
        w = tuple(m.words)
        if w == (DAX_WORD,):
            dax += 1
            continue
        p_gen_ok = len(w) in (1, 2, 3) and w[-1] in shape_c
        if not p_gen_ok:
            raise CeilingStop(f"chi2_checks: {w!r} is not an utterance of the four templates")
        n += 1
        len_c[len(w) - 1] += 1
        shape = w[-1]
        shape_c[shape] += 1
        colour = size = None
        if len(w) == 2:
            if w[0] in colour_c:
                colour = w[0]
            elif w[0] in size_c:
                size = w[0]
        elif len(w) == 3:
            size, colour = w[0], w[1]
        if colour is not None:
            colour_c[colour] += 1
            if (shape, colour) in ALLOWED_SET:
                pair_c[(shape, colour)] += 1
            else:
                heldout += 1
        if size is not None:
            size_c[size] += 1

    def fit(obs: Sequence[int], probs: Sequence[float]) -> Dict[str, object]:
        tot = sum(obs)
        if tot == 0:
            return {"stat": None, "p": 0.0, "obs": list(obs), "n": 0}
        exp = [tot * p for p in probs]
        st, p = stats.chisquare(list(obs), exp)
        return {"stat": float(st), "p": float(p), "obs": list(obs), "n": int(tot)}

    out: Dict[str, object] = {"n": n, "dax_excluded": dax}
    out["length"] = fit(len_c, [0.25, 0.5, 0.25])
    out["shape"] = fit([shape_c[s] for s in SHAPES], [N_S[s] / N_ALLOWED for s in SHAPES])
    out["colour"] = fit([colour_c[c] for c in COLOURS], [N_C[c] / N_ALLOWED for c in COLOURS])
    out["size"] = fit([size_c[z] for z in SIZES], [1.0 / len(SIZES)] * len(SIZES))
    out["pairs"] = fit([pair_c[p] for p in ALLOWED], [1.0 / N_ALLOWED] * N_ALLOWED)
    out["heldout_pairs_seen"] = heldout
    out["gated"] = bool(n > 0 and heldout == 0 and all(out[k]["p"] > P_FLOOR for k in ("length", "shape", "colour", "size", "pairs")))
    return out


# ------------------------------------------------------------------------------------------------------------------ G6: the ceiling gate's own controls
def _replicate_setup(k: int, n_moments: int):
    ms = sample_moments(n_moments, np.random.default_rng([SEED_ROOT, G6_TAG, int(k)]))
    tr, he = ST.split(ms)
    sc = CO.Scorer([m.words for m in tr], [m.words for m in he])
    F = frozenset(f for f in oracle_frames() if sc.train_adjacent(f) > 0)
    return sc, F, [m.words for m in he]


def g6_replicate(k: int, n_moments: int = 10_000) -> Dict[str, object]:
    """G6 (a): on replicate k drawn from the generator's own constants, G(F_oracle) <= G_max + 20, the margin G_max − G(F_oracle) printed."""
    sc, F, held = _replicate_setup(k, n_moments)
    g = sc.gain(F)
    gm = g_max(held, g.bits0)
    return {"k": int(k), "n_moments": n_moments, "n_oracle": len(F), "G_oracle": g.G, "G_max": gm, "margin": gm - g.G, "violation": ceiling_violation(g.G, gm)}


def g6_cheat(k: int = 1, n_moments: int = 4000) -> Dict[str, object]:
    """G6 (b): a planted cheat — bits(held | F) replaced by 0.9 x the generator's own code length — must exceed G_max + 20 and be CAUGHT; the plant asserts it changed the bytes."""
    sc, F, held = _replicate_setup(k, n_moments)
    g = sc.gain(F)
    gm = g_max(held, g.bits0)
    s = sum(-math.log2(p_gen(u)) for u in held)
    cheat_bits = 0.9 * s
    G_cheat = g.bits0 - cheat_bits - g.L
    return {"k": int(k), "bitsF_honest": g.bitsF, "bitsF_cheat": cheat_bits, "G_honest": g.G, "G_cheat": G_cheat, "G_max": gm, "caught": ceiling_violation(G_cheat, gm)}


def g6_exact_checks() -> Dict[str, object]:
    """G6 (c): Σ P_gen over the generator's whole support = 1 (to 1e-12), its entropy 6.0774, H(length) 1.5, H(utterance | length) 4.5774."""
    sup = support()
    return {"sum_p": sum(sup.values()), "entropy": entropy(), "h_length": h_length(), "h_given_length": h_given_length(), "support_size": len(sup)}
