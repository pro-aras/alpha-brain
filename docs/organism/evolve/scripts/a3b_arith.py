#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:55 +0400 — PREREG-EVOLVE-CAL AMENDMENT 3b: every figure of A3b.3 (the two stops), A3b.4 (N2's df) and A3b.5 (the cost band at the
# number of values actually in the null) in one place, run through slot, its output committed beside the amendment. Stdlib + scipy; no organism file is read.
"""a3b_arith.py — the arithmetic of AMENDMENT 3b.

THE MODEL (the law's own, A3.6): every twin independently MOVES a reading with probability p; a band needs at least two moves among the twins at the chosen level (A1 (i):
>= 3 distinct values of incumbent + twins — an UPPER BOUND on the chance of a band, because two moves may land on one value). Stop 1 reads the six A0/A0+ twins; stop 2 reads
the five twins at the chosen level. Under ONE p the two stops are nested (stop 1's condition is implied by stop 2's); with a p that grows with epsilon they are not, and the
true miss lies between the larger and the sum — both are printed.

CONTROLS: the verifier's published numbers (COSIGN-LINES.txt, its v2_arith.out / v2b_extra.out) are re-derived below and the script ABORTS if one is off by more than 0.0006.
"""
import math
from math import comb

from scipy import stats


def pmf(n, k, p):
    return comb(n, k) * p ** k * (1 - p) ** (n - k)


def p_ge(n, k, p):
    """P(X >= k), X ~ Bin(n, p)."""
    return 1.0 - sum(pmf(n, i, p) for i in range(k))


def grant20(p):                      # the 20-twin design grants a band iff >= 2 moves among 20 (modelled)
    return p_ge(20, 2, p)


def stop1_miss(p):                   # six A0/A0+ twins, none moves; the 20-twin design would have granted (>= 2 among the other 14)
    return (1 - p) ** 6 * p_ge(14, 2, p)


def stop2_miss_S(p):                 # Stage B only if >= 2 moves among the chosen level's 5 (rule S, modelled); the 20-twin design would have granted
    return pmf(5, 0, p) * p_ge(15, 2, p) + pmf(5, 1, p) * p_ge(15, 1, p)


def stop2_miss_one(p):               # the verifier's one-move condition: Stage B only if >= 1 move among the 5 (no selection modelled)
    return pmf(5, 0, p) * p_ge(15, 2, p)


def p_stage_b_S(p):
    return p_ge(5, 2, p)


def p_stage_b_one(p):
    return p_ge(5, 1, p)


STAGE_B_CPU_H = 11.4                 # A3.6: 15 twins at 2,739 s


def check(name, got, want, tol=0.0006):
    if abs(got - want) > tol:
        raise SystemExit(f"CONTROL FAILED: {name}: got {got:.6f}, the verifier's figure is {want}")


def main() -> None:
    # ---- controls: the verifier's figures
    for p, w in ((0.05, 0.112), (0.10, 0.221), (0.20, 0.210), (0.30, 0.112), (0.50, 0.016)):
        check(f"stop1 p={p}", stop1_miss(p), w)
    # NB: the verifier's v2_arith table is at p = 0.05, 0.10, 0.15, 0.20, 0.30 for its five columns; the five values it prints are checked by the pairs below
    for p, w in ((0.05, 0.264), (0.10, 0.608), (0.15, 0.824), (0.20, 0.931)):
        check(f"P(>=2 of 20) p={p}", grant20(p), w, 0.0006)
    for p, w in ((0.05, 0.242), (0.10, 0.527), (0.15, 0.660), (0.20, 0.668), (0.30, 0.521)):
        check(f"stop2 S p={p}", stop2_miss_S(p), w)
    for p, w in ((0.05, 0.132), (0.10, 0.266), (0.15, 0.302), (0.20, 0.273), (0.30, 0.162)):
        check(f"stop2 one-move p={p}", stop2_miss_one(p), w)
    print("CONTROLS PASSED: the verifier's figures (stop 1 at p = .05/.10/.20/.30/.50 = 0.112/0.221/0.210/0.112/0.016; P(>=2 of 20) = 0.264/0.608/0.824/0.931; stop 2 under S = "
          "0.242/0.527/0.660/0.668/0.521; the one-move condition = 0.132/0.266/0.302/0.273/0.162) are re-derived to within 0.0006")
    print()

    # ---- the maximum of stop 1's miss, and where a band becomes more likely than not
    best = max((stop1_miss(i / 1000), i / 1000) for i in range(1, 1000))
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if grant20(mid) < 0.5 else (lo, mid)
    print(f"STOP 1 (A0/A0+: six twins, none moves) misses at most {best[0]:.4f} at p = {best[1]:.3f}; the 20-twin design grants a band more often than not above p = {hi:.4f}")
    print()

    # ---- the table
    print("TABLE (every cell a probability, the model above; miss = the 20-twin design would have granted a band and the staged design does not):")
    print(f"{'p':>6} | {'20-twin grants':>14} | {'stop 1 miss':>11} | {'stop 2 miss, rule S':>19} | {'S: P(Stage B runs)':>18} | {'S: E[Stage B CPU-h]':>19} | {'M: Stage B CPU-h':>16}")
    for p in (0.05, 0.10, 0.139, 0.15, 0.20, 0.30, 0.50):
        print(f"{p:6.3f} | {grant20(p):14.3f} | {stop1_miss(p):11.3f} | {stop2_miss_S(p):19.3f} | {p_stage_b_S(p):18.3f} | {STAGE_B_CPU_H * p_stage_b_S(p):19.2f} | {STAGE_B_CPU_H:16.1f}")
    print()
    print("ONE-MOVE CONDITION (the verifier's alternative, no selection modelled): Stage B only if >= 1 move among the five; miss / P(Stage B runs) / E[CPU-h]:")
    for p in (0.05, 0.10, 0.15, 0.20, 0.30, 0.50):
        print(f"  p={p:.2f}: miss {stop2_miss_one(p):.3f}  P(runs) {p_stage_b_one(p):.3f}  E[CPU-h] {STAGE_B_CPU_H * p_stage_b_one(p):.2f}")
    print()

    # ---- E4: N2's F tests
    print("N2 F-TESTS (two-sided 0.05: F(0.975; dfn, dfd); the smallest detectable sigma ratio is sqrt(F)); df = values - 1:")
    for label, dfn, dfd in (("frames_filed: S1 11 values (10 seeds + incumbent) vs S2 7 values (6 seeds + incumbent)", 10, 6),
                            ("the text of A3.6 (4) as signed (6 values on S2)", 10, 5),
                            ("the law's A7 (S1 21 values vs S2 11 values)", 20, 10),
                            ("epsilon dims, S1 Stage A only (6 values) vs S2 7 values", 5, 6),
                            ("epsilon dims, S1 with Stage B (21 values) vs S2 7 values", 20, 6)):
        f = float(stats.f.ppf(0.975, dfn, dfd))
        print(f"  ({dfn:>2}, {dfd:>2}): F = {f:.3f}, detectable sigma ratio {math.sqrt(f):.2f}x   [{label}]")
    print()

    # ---- limit (2): the cost band at the number of values actually in the null
    sigma_ln = 0.0490
    print(f"COST BAND (A4 (ii): edge = t(n-1, 1-0.0083) * sqrt(2) * sigma_hat; sigma_hat = {sigma_ln} = the ln-SD of the seven STOP twins' CPU-seconds; the policy cap is 1.2):")
    for n, what in ((7, "the STOP stage's seven twins"), (17, "the degenerate branch: incumbent + 6 epsilon twins + 10 seed twins"), (21, "the law's incumbent + 20 twins")):
        t = float(stats.t.ppf(1 - 0.0083, n - 1))
        factor = t * math.sqrt(2)
        edge = factor * sigma_ln
        print(f"  n = {n:>2} ({what}): t = {t:.4f}, factor {factor:.3f}, edge ln {edge:.4f}, ratio {math.exp(edge):.4f} {'(above' if math.exp(edge) > 1.2 else '(at or below'} the 1.2 cap)")
    print()

    # ---- A3b.3: the band edge's factor at the number of values actually in a dimension's epsilon null (Stage A only: the incumbent + 5 twins = 6 values; with Stage B: 21)
    f6 = float(stats.t.ppf(1 - 0.0083, 5)) * math.sqrt(2)
    f21 = float(stats.t.ppf(1 - 0.0083, 20)) * math.sqrt(2)
    print(f"BAND EDGE FACTOR (t(n-1, 1-0.0083) * sqrt(2) * sigma_hat): n = 6 values {f6:.3f}, n = 21 values {f21:.3f}: a band from six values is {f6 / f21:.3f}x as wide as the 20-twin band")
    print()

    # ---- the price, A3.6's inputs (S1 twin 2,739 s; S2 twin 3,560 s) and A3b.4's N2
    s1, s2 = 2739 / 3600, 3560 / 3600
    a0, a0p, seeds, stage_a, stage_b = 3 * s1, 4 * s1, 10 * s1, 23 * s1, 15 * s1
    pbad, pgood, r5 = 1 * s1, 2.1, 1.4
    n2_seed = 7 * s2
    n2_both = 13 * s2
    deg = a0 + a0p + seeds + n2_seed + pbad + pgood + r5
    nondeg_b = a0 + stage_a + stage_b + n2_both + pbad + pgood + r5
    nondeg_nob = a0 + stage_a + n2_both + pbad + pgood + r5
    print("PRICE (CPU-hours; an S1 twin 0.761, an S2 twin 0.989 — A3.5's measured figures):")
    print(f"  A0 {a0:.2f} · A0+ {a0p:.2f} · 10 seeds {seeds:.2f} · Stage A (13 epsilon + 10 seed twins) {stage_a:.2f} · Stage B {stage_b:.2f}")
    print(f"  N2: seed twins only (7 twins) {n2_seed:.2f}; with epsilon twins at the chosen level too (6 seeds + 6 epsilon + the incumbent = 13 twins) {n2_both:.2f}")
    print(f"  TOTAL degenerate branch (A0 + A0+ + seeds + N2 seeds + P-BAD + P-GOOD + R5) = {deg:.1f}")
    print(f"  TOTAL non-degenerate branch with Stage B (N2 with epsilon twins) = {nondeg_b:.1f}; without Stage B (rule S stops) = {nondeg_nob:.1f}")
    print("  (A3.6 printed 24.1 and 42.4 with N2 = 6.9 in both; the verifier recomputed them; A3b.4 adds the six epsilon twins to the non-degenerate branch's N2)")


if __name__ == "__main__":
    main()
