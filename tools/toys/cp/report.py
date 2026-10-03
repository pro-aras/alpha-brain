"""report.py — TOY A's analysis: the statistics (pure functions, unit-tested on synthetic data) and, below them, the report over the lives' records.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:31 +0400 — the statistics section, written to docs/research/toys/PREREG-TOY-CP.md §5 and
# PREREG-TOY-CP-AMEND-1.md §4–§5; red-first (tests/tools/test_toys_cp.py::TestReport). The report section follows in a later edit of this file.

THE STATISTIC (PREREG §5). For arm E and seed s: d_s(E) = mean over E's replicates of A − mean over RANDOM's 20 lives of A; D(E) = mean_s d_s; likewise e_s,
Dn for SHARE_N. THE NULL is a distribution of 10,000 draws: at every seed RANDOM's 20 lives are split at random into a «fake arm» of 10 and a reference of
the other 10; D_null = the mean over seeds of (mean fake − mean reference) — conservative (its reference has 10 lives, the real comparison 20). The draws
are made in one fixed order (seed by seed, a permutation of the 20 lives, the first 10 the fake arm) from `default_rng(20261003)`; the held-out null reuses
the SAME per-seed draws restricted to seeds 20261304–10. p(E) = (1 + #{D_null ≥ D(E)}) / (draws + 1) (SHARE_N: the lower tail).
"""
from __future__ import annotations

import math
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

NULL_SEED = 20261003
BOOT_SEED = 20261004
ALPHA = 0.05 / 9                    # Bonferroni over the eight cells and LP-OUDEYER
HELD_OUT_FROM = 20261304            # seeds 20261304–10: the held-out reading of the ema cells (a = 0.1 was read on 20261301–03)
FACTORS: Dict[str, Tuple[str, str, int]] = {"loss": ("L", "C", 0), "scope": ("own", "hist", 1), "time": ("last2", "ema", 2)}


def null_matrix(rand_by_seed: Mapping[int, Sequence[float]], draws: int = 10000, fake: int = 10, seed: int = NULL_SEED) -> np.ndarray:
    """(draws, n_seeds): per draw and seed, mean(fake arm) − mean(reference), in sorted-seed order."""
    rng = np.random.default_rng(seed)
    seeds = sorted(rand_by_seed)
    M = np.empty((draws, len(seeds)))
    for d in range(draws):
        for j, s in enumerate(seeds):
            v = np.asarray(rand_by_seed[s], dtype=np.float64)
            perm = rng.permutation(len(v))
            M[d, j] = v[perm[:fake]].mean() - v[perm[fake:2 * fake]].mean()
    return M


def null_distribution(rand_by_seed: Mapping[int, Sequence[float]], draws: int = 10000, fake: int = 10, seed: int = NULL_SEED,
                      seeds: Optional[Sequence[int]] = None) -> np.ndarray:
    """D_null over all the seeds (or over `seeds`, the held-out subset, from the same draws)."""
    M = null_matrix(rand_by_seed, draws, fake, seed)
    keep = sorted(rand_by_seed) if seeds is None else sorted(seeds)
    cols = [sorted(rand_by_seed).index(s) for s in keep]
    return M[:, cols].mean(axis=1)


def arm_d_by_seed(arm_by_seed: Mapping[int, Sequence[float]], rand_by_seed: Mapping[int, Sequence[float]]) -> Dict[int, float]:
    return {s: float(np.mean(arm_by_seed[s]) - np.mean(rand_by_seed[s])) for s in sorted(arm_by_seed)}


def arm_D(arm_by_seed: Mapping[int, Sequence[float]], rand_by_seed: Mapping[int, Sequence[float]], seeds: Optional[Sequence[int]] = None) -> float:
    d = arm_d_by_seed(arm_by_seed, rand_by_seed)
    keep = sorted(d) if seeds is None else sorted(seeds)
    return float(np.mean([d[s] for s in keep]))


def p_upper(D: float, null: np.ndarray) -> float:
    return (1.0 + float(np.sum(null >= D))) / (len(null) + 1.0)


def p_lower(D: float, null: np.ndarray) -> float:
    return (1.0 + float(np.sum(null <= D))) / (len(null) + 1.0)


def smallest_passing(null: np.ndarray, alpha: float = ALPHA) -> float:
    """The smallest D that clears the upper-tail bar: the (1 − alpha) quantile of the null."""
    return float(np.quantile(null, 1.0 - alpha))


def smallest_passing_lower(null: np.ndarray, alpha: float = ALPHA) -> float:
    """The largest Dn that clears the lower-tail bar (SHARE_N): the alpha quantile of the null."""
    return float(np.quantile(null, alpha))


def sign_count(values: Sequence[float], sign: int) -> int:
    return int(sum(1 for v in values if sign * v > 0))


def sign_p(k: int, n: int) -> float:
    """Exact one-sided sign test: P(X >= k) for X ~ Binomial(n, 1/2)."""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / float(2 ** n)


def held_out_seeds(seeds: Sequence[int]) -> List[int]:
    return [s for s in sorted(seeds) if s >= HELD_OUT_FROM]


def sd_flag(arm_sd_by_seed: Mapping[int, float], rand_sd_by_seed: Mapping[int, float], ratio: float = 2.0) -> bool:
    """FLAGGED iff the mean over seeds of (the arm's replicate SD ÷ RANDOM's SD) exceeds `ratio`: its permutation p is then anti-conservative."""
    r = [arm_sd_by_seed[s] / rand_sd_by_seed[s] for s in sorted(arm_sd_by_seed) if rand_sd_by_seed[s] > 0]
    return bool(np.mean(r) > ratio)


def escaped_share(A_E: float, A_rand: float, A_ronly: float) -> float:
    """(A(E) − A(RANDOM)) / (A(R-ONLY) − A(RANDOM)) — NEVER clipped: it can exceed 1 or be negative (AMEND-1 §4)."""
    return (A_E - A_rand) / (A_ronly - A_rand)


def cell_name(loss: str, scope: str, scale: str) -> str:
    return f"{loss}-{scope}-{scale}"


def main_effects(cells: Mapping[str, Mapping[int, float]], seeds: Sequence[int], boot: int = 10000) -> Dict[str, Dict[str, object]]:
    """The factorial's main effects: per seed, the mean over the other factors' four cells of (high − low); the across-seed mean, its standard
    error, the sign count and a 95 % bootstrap interval over seeds."""
    seeds = sorted(seeds)
    out: Dict[str, Dict[str, object]] = {}
    rng = np.random.default_rng(BOOT_SEED)
    for factor, (lo, hi, pos) in FACTORS.items():
        per = []
        for s in seeds:
            effs = []
            for name in cells:                                  # the four cells with the factor LOW, each paired with its HIGH partner
                parts = name.split("-")
                if parts[pos] == lo:
                    hi_parts = list(parts)
                    hi_parts[pos] = hi
                    effs.append(cells["-".join(hi_parts)][s] - cells[name][s])
            per.append(float(np.mean(effs)))
        arr = np.array(per)
        se = float(arr.std(ddof=1) / math.sqrt(len(arr))) if len(arr) > 1 else float("nan")
        bs = np.array([arr[rng.integers(len(arr), size=len(arr))].mean() for _ in range(boot)])
        out[factor] = {"per_seed": per, "mean": float(arr.mean()), "se": se, "signs": sign_count(per, +1),
                       "ci95": (float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975)))}
    return out
