# the seat's arithmetic for mark P's paired bar (PREREG-WORD-ROAD §4): exact power by the trinomial
# a pair is favourable (full phrase right, shape word alone wrong) with prob pf, unfavourable with prob pu, tied otherwise
# PASS = (f - u) / n >= 0.10  AND  the exact one-sided sign test P(X >= f | f + u, 1/2) < 0.001
import math, sys
from functools import lru_cache
def sign_p(f, u):
    m = f + u
    return sum(math.comb(m, k) for k in range(f, m + 1)) / 2 ** m if m else 1.0
def power(n, d, g):
    pf, pu = (d + g) / 2, (d - g) / 2
    pt = 1 - pf - pu
    tot = 0.0
    lg = [math.lgamma(i + 1) for i in range(n + 2)]
    for f in range(n + 1):
        for u in range(n - f + 1):
            if (f - u) / n < 0.10 - 1e-12 or sign_p(f, u) >= 0.001:
                continue
            t = n - f - u
            lp = lg[n] - lg[f] - lg[u] - lg[t] + (f * math.log(pf) if pf > 0 else (0 if f == 0 else -1e9)) \
                + (u * math.log(pu) if pu > 0 else (0 if u == 0 else -1e9)) + (t * math.log(pt) if pt > 0 else (0 if t == 0 else -1e9))
            tot += math.exp(lp)
    return tot
def smallest(n):
    for f in range(n + 1):
        if f / n >= 0.10 - 1e-12 and sign_p(f, 0) < 0.001:
            return f, f / n
print("the smallest passing result (every discordant pair favourable): n -> pairs, gap")
for n in (73, 75, 79, 226, 228):
    print("  ", n, smallest(n))
print("P(pass) by the true gap g and the discordance d (share of pairs on which the two pointings differ in rightness)")
print("   n     d     g=0.00   g=0.05   g=0.10   g=0.15   g=0.20   g=0.25")
for n in (75, 228):
    for d in (0.2, 0.3, 0.4):
        print(f"   {n:<5d} {d:<5.1f} " + "  ".join(f"{power(n, d, g):7.4f}" if g <= d else "      —" for g in (0.0, 0.05, 0.10, 0.15, 0.20, 0.25)))
