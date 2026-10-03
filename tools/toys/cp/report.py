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
from pathlib import Path
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


# ====================================================================================================== THE ANALYSIS (PREREG §5 + AMEND-1)
# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:37 +0400 — `analyse`, `anatomy` (red-first: tests/tools/test_toys_cp_analyse.py).
# `arms[arm][seed]` is a list of per-life summaries {A, SN, SNL, lock, M1, LR{room}, LRfinal{room}, histN[...]} (see `summarise_life` below).
NINE: Tuple[str, ...] = ("L-own-last2", "L-own-ema", "L-hist-last2", "L-hist-ema", "C-own-last2", "C-own-ema", "C-hist-last2", "C-hist-ema", "LP-OUDEYER")
EMA_CELLS: Tuple[str, ...] = ("L-own-ema", "L-hist-ema", "C-own-ema", "C-hist-ema")


def _by_seed(arms, arm: str, key: str, seeds: Sequence[int]) -> Dict[int, np.ndarray]:
    return {s: np.array([l[key] for l in arms[arm][s]], dtype=np.float64) for s in seeds}


def _sd_by_seed(by_seed: Mapping[int, np.ndarray]) -> Dict[int, float]:
    return {s: (float(np.std(v, ddof=1)) if len(v) > 1 else 0.0) for s, v in by_seed.items()}


def _bar(D: float, null: np.ndarray, per_seed: Sequence[float], sign: int, flagged: bool, need8: int, need9: int, lower: bool) -> Dict[str, object]:
    """One bar (BEAT: upper tail, sign +1; LEAVE: lower tail, sign −1). A FLAGGED arm rests on the sign count alone at `need9` (its permutation p is anti-conservative)."""
    p = p_lower(D, null) if lower else p_upper(D, null)
    signs = sign_count(per_seed, sign)
    thr = smallest_passing_lower(null) if lower else smallest_passing(null)
    ok = (signs >= need9) if flagged else (p <= ALPHA and signs >= need8)
    return {"D": float(D), "p": float(p), "signs": int(signs), "n": len(per_seed), "smallest": float(thr), "ok": bool(ok)}


STAGE2_REPS = 10                    # the law's stage 2: 10 replicates × 10 seeds for each arm's NULL


def _stage2(arms, seeds: Sequence[int], stage2_arms: Sequence[str], null_A: np.ndarray, null_A_ho: np.ndarray, null_N: np.ndarray,
            rand_A, rand_N, rand_sd_A, held: Sequence[int]) -> Dict[str, object]:
    """STAGE 2 (PREREG-TOY-CP §6; edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 12:19 +0400, red-first: tests/tools/test_toys_cp_analyse.py::TestStage2).
    For each arm that passes BEAT, its NULL (`arms["NULL-<arm>"]`, S1c's credit derangement; 10 replicates a seed): the arm is VOID iff its NULL also passes BEAT.
    «Passes BEAT» for the NULL is the PLAIN 10-seed bar (p ≤ 0.0056 AND d_s > 0 at ≥ 8 of 10 seeds, ≥ 9 if the NULL's replicate SD is flagged) — the lenient reading, so a
    doubtful NULL can only make the verdict more conservative; the held-out-counted form (ema cells) is printed beside it. A NULL with fewer than 10 replicates at any seed
    is MISSING (the law asks 10). Also kept, as readings: the arm's A minus its NULL's, by seed (the credit's address is what separates them), the NULL's SHARE_N and its LEAVE bar."""
    out: Dict[str, Dict[str, object]] = {}
    missing: List[str] = []
    for arm in stage2_arms:
        key = "NULL-" + arm
        if key not in arms or not all(len(arms[key].get(s, [])) >= STAGE2_REPS for s in seeds):
            missing.append(arm)
            continue
        A_s, N_s = _by_seed(arms, key, "A", seeds), _by_seed(arms, key, "SN", seeds)
        arm_A = _by_seed(arms, arm, "A", seeds)
        sdA = _sd_by_seed(A_s)
        ratio = float(np.mean([sdA[s] / rand_sd_A[s] for s in seeds if rand_sd_A[s] > 0]))
        flagged = ratio > 2.0
        d_s = arm_d_by_seed(A_s, rand_A)
        e_s = arm_d_by_seed(N_s, rand_N)
        D, Dn = arm_D(A_s, rand_A), arm_D(N_s, rand_N)
        beat = _bar(D, null_A, [d_s[s] for s in seeds], +1, flagged, 8, 9, lower=False)
        leave = _bar(Dn, null_N, [e_s[s] for s in seeds], -1, False, 8, 9, lower=True)
        counted = beat["ok"]
        ho = None
        if arm in EMA_CELLS:
            hb = _bar(arm_D(A_s, rand_A, held), null_A_ho, [d_s[s] for s in held], +1, flagged, 6, 7, lower=False)
            ho = {"D": hb["D"], "p": hb["p"], "signs": hb["signs"], "ok": hb["ok"]}
            counted = bool(beat["ok"] and hb["ok"])
        gain = [float(np.mean(arm_A[s]) - np.mean(A_s[s])) for s in seeds]
        locks = [l["lock"] for s in seeds for l in arms[key][s] if l.get("lock") is not None]
        out[arm] = {"null_A": float(np.mean([np.mean(A_s[s]) for s in seeds])), "null_SN": float(np.mean([np.mean(N_s[s]) for s in seeds])),
                    "D": float(D), "p_A": beat["p"], "signs": beat["signs"], "smallest_D": beat["smallest"], "flagged": bool(flagged), "sd_ratio_A": ratio,
                    "beat": bool(beat["ok"]), "beat_counted": bool(counted), "held_out": ho, "void": bool(beat["ok"]),
                    "Dn": float(Dn), "p_N": leave["p"], "signs_N": leave["signs"], "leave": bool(leave["ok"]),
                    "gain_over_null_s": gain, "gain_signs": sign_count(gain, +1), "gain_mean": float(np.mean(gain)),
                    "lock_mean": float(np.mean(locks)) if locks else None, "lock_max": int(max(locks)) if locks else None}
    return {"arms": out, "missing": missing, "void": [a for a, r in out.items() if r["void"]]}


def analyse(arms: Mapping[str, Mapping[int, Sequence[Dict[str, object]]]], seeds: Sequence[int], draws: int = 10000) -> Dict[str, object]:
    seeds = sorted(seeds)
    held = held_out_seeds(seeds)
    rand_A, rand_N = _by_seed(arms, "RANDOM", "A", seeds), _by_seed(arms, "RANDOM", "SN", seeds)
    ronly_A = _by_seed(arms, "R-ONLY", "A", seeds)
    MA, MN = null_matrix(rand_A, draws), null_matrix(rand_N, draws)             # the SAME permutations (they depend on the stream, not the values)
    col = {s: i for i, s in enumerate(seeds)}
    hcols = [col[s] for s in held]
    null_A, null_N = MA.mean(axis=1), MN.mean(axis=1)
    null_A_ho, null_N_ho = MA[:, hcols].mean(axis=1), MN[:, hcols].mean(axis=1)
    rand_sd_A, rand_sd_N = _sd_by_seed(rand_A), _sd_by_seed(rand_N)
    smallest_D = smallest_passing(null_A)
    # ---- the controls
    G_by_seed = [float(np.mean(ronly_A[s]) - np.mean(rand_A[s])) for s in seeds]
    G = float(np.mean(G_by_seed))
    pc1_signs = sign_count(G_by_seed, +1)
    err_N = [float(np.mean([l["SN"] for l in arms["ERROR"][s]])) for s in seeds]
    nonly = {s: float(np.mean([l["A"] for l in arms["N-ONLY"][s]])) for s in seeds}
    pc3 = [nonly[s] < float(np.quantile(rand_A[s], 0.025)) for s in seeds]
    controls = {"G": G, "G_by_seed": G_by_seed, "smallest_D": smallest_D,
                "PC1": {"ok": bool(G >= 0.05 and pc1_signs >= 8), "G": G, "signs": pc1_signs},
                "PC2": {"ok": bool(sum(1 for v in err_N if v > 0.5) >= 9), "n_over_half": int(sum(1 for v in err_N if v > 0.5)), "by_seed": err_N},
                "PC3": {"ok": bool(all(pc3)), "n_below_band": int(sum(pc3))},
                "ceiling_ok": bool(G >= 3.0 * smallest_D)}
    controls["gradable"] = bool(controls["PC1"]["ok"] and controls["PC2"]["ok"] and controls["PC3"]["ok"] and controls["ceiling_ok"])
    # ---- the arms
    out_arms: Dict[str, Dict[str, object]] = {}
    for arm in NINE:
        A_s, N_s = _by_seed(arms, arm, "A", seeds), _by_seed(arms, arm, "SN", seeds)
        sdA, sdN = _sd_by_seed(A_s), _sd_by_seed(N_s)
        ratio_A = float(np.mean([sdA[s] / rand_sd_A[s] for s in seeds if rand_sd_A[s] > 0]))
        ratio_N = float(np.mean([sdN[s] / rand_sd_N[s] for s in seeds if rand_sd_N[s] > 0]))
        fA, fN = ratio_A > 2.0, ratio_N > 2.0
        d_s = arm_d_by_seed(A_s, rand_A)
        e_s = arm_d_by_seed(N_s, rand_N)
        D, Dn = arm_D(A_s, rand_A), arm_D(N_s, rand_N)
        beat = _bar(D, null_A, [d_s[s] for s in seeds], +1, fA, 8, 9, lower=False)
        leave = _bar(Dn, null_N, [e_s[s] for s in seeds], -1, fN, 8, 9, lower=True)
        A_mean = float(np.mean([np.mean(A_s[s]) for s in seeds]))
        rec = {"A": A_mean, "SN": float(np.mean([np.mean(N_s[s]) for s in seeds])), "D": D, "Dn": Dn, "d_s": [d_s[s] for s in seeds], "e_s": [e_s[s] for s in seeds],
               "p_A": beat["p"], "p_N": leave["p"], "sign_A": beat["signs"], "sign_N": leave["signs"], "smallest_D": beat["smallest"], "smallest_Dn": leave["smallest"],
               "BEAT": beat["ok"], "LEAVE": leave["ok"], "sd_ratio_A": ratio_A, "sd_ratio_N": ratio_N, "sd_flag_A": fA, "sd_flag_N": fN,
               "escaped_share": escaped_share(A_mean, float(np.mean([np.mean(rand_A[s]) for s in seeds])), float(np.mean([np.mean(ronly_A[s]) for s in seeds]))),
               "held_out": None, "CONTAMINATED": False}
        if arm in EMA_CELLS:
            dA = [d_s[s] for s in held]
            eN = [e_s[s] for s in held]
            hb = _bar(arm_D(A_s, rand_A, held), null_A_ho, dA, +1, fA, 6, 7, lower=False)
            hl = _bar(arm_D(N_s, rand_N, held), null_N_ho, eN, -1, fN, 6, 7, lower=True)
            rec["held_out"] = {"n_seeds": len(held), "D": hb["D"], "p_A": hb["p"], "signs_A": hb["signs"], "smallest_D": hb["smallest"], "BEAT": hb["ok"],
                               "Dn": hl["D"], "p_N": hl["p"], "signs_N": hl["signs"], "smallest_Dn": hl["smallest"], "LEAVE": hl["ok"]}
            rec["CONTAMINATED"] = bool((beat["ok"] and not hb["ok"]) or (leave["ok"] and not hl["ok"]))
            rec["BEAT_counted"] = bool(beat["ok"] and hb["ok"])
            rec["LEAVE_counted"] = bool(leave["ok"] and hl["ok"])
        else:
            rec["BEAT_counted"], rec["LEAVE_counted"] = rec["BEAT"], rec["LEAVE"]
        out_arms[arm] = rec
    # ---- the factorial's main effects
    cellsA = {c: {s: float(np.mean([l["A"] for l in arms[c][s]])) for s in seeds} for c in ES_CELLS()}
    cellsN = {c: {s: float(np.mean([l["SN"] for l in arms[c][s]])) for s in seeds} for c in ES_CELLS()}
    # ---- the verdict (§5): classes decided on the COUNTED bars (an ema cell counts only if it also holds on seeds 04-10)
    beat_arms = [a for a in NINE if out_arms[a]["BEAT_counted"]]
    leave_arms = [a for a in NINE if out_arms[a]["LEAVE_counted"]]
    both = [a for a in beat_arms if a in leave_arms]
    if not controls["gradable"]:
        cls = "NOT-GRADABLE"
    elif both:
        cls = "FIXED-PENDING-STAGE-2"
    elif leave_arms and not beat_arms:
        cls = "ESCAPES-BUT-DOES-NOT-BEAT-RANDOM"
    elif not leave_arms and not beat_arms:
        cls = "NOT-FIXED"
    elif not leave_arms:
        cls = "NOT-FIXED"                    # an arm beats RANDOM without leaving N: the law's class (iii) (no arm passes LEAVE); printed as BEATS-WITHOUT-LEAVING
    else:
        cls = "SPLIT"                        # one arm beats RANDOM and another leaves N, none does both: unclassified by the law, printed
    verdict = {"class": cls, "beat_arms": beat_arms, "leave_arms": leave_arms, "both": both, "stage2_arms": list(beat_arms) if controls["gradable"] else [],
               "beats_without_leaving": [a for a in beat_arms if a not in leave_arms]}
    # ---- stage 2 (PREREG §6): the class FIXED-PENDING-STAGE-2 is decided by the NULLs of the arms that passed both counted bars
    stage2 = _stage2(arms, seeds, verdict["stage2_arms"], null_A, null_A_ho, null_N, rand_A, rand_N, rand_sd_A, held)
    fixed_arms = [a for a in both if a in stage2["arms"] and not stage2["arms"][a]["void"]]
    pending = [a for a in both if a not in stage2["arms"]]
    if cls == "FIXED-PENDING-STAGE-2" and not pending:
        cls = "FIXED" if fixed_arms else "NOT-FIXED-ALL-VOID"          # all VOID: every arm that passed both bars has a NULL that passes BEAT (the law names no class for it)
    verdict.update({"class": cls, "fixed_arms": fixed_arms, "void_arms": [a for a in both if a in stage2["arms"] and stage2["arms"][a]["void"]], "stage2_missing": stage2["missing"]})
    return {"seeds": seeds, "held_out_seeds": held, "controls": controls, "arms": out_arms, "main_effects_A": main_effects(cellsA, seeds), "main_effects_SN": main_effects(cellsN, seeds),
            "verdict": verdict, "stage2": stage2,
            "null": {"draws": draws, "sd_A": float(np.std(null_A)), "q99_A": smallest_D, "sd_N": float(np.std(null_N)),
                     "q_lower_N": smallest_passing_lower(null_N), "sd_A_ho": float(np.std(null_A_ho)), "q99_A_ho": smallest_passing(null_A_ho)}}


def ES_CELLS() -> Tuple[str, ...]:
    return ("L-own-last2", "L-own-ema", "L-hist-last2", "L-hist-ema", "C-own-last2", "C-own-ema", "C-hist-last2", "C-hist-ema")


def anatomy(rows: Sequence[Mapping[str, object]], min_block: int = 5) -> Dict[str, object]:
    """The drop's anatomy (PREREG §4): over RANDOM's blocks, in N's blocks against R1-R3's, the means of the total drop and of its bias-only, weight-only and
    statistics-only parts (single-factor drops from the state before the block toward the state after it), the interaction (total − the three), and
    share_bias = mean(bias-only) / mean(total). The mechanism of §0 item 4 holds iff share_bias > 0.5 in N's blocks (own-window). `min_block` = 5: the 196 policy
    blocks (the PREREG did not name the range; the all-blocks and blocks >= 21 readings are printed beside)."""
    out: Dict[str, object] = {}
    for cls, is_cls in (("N", lambda r: r == "N"), ("R", lambda r: r != "N")):
        sel = [x for x in rows if int(x["block"]) >= min_block and is_cls(x["room"])]
        d: Dict[str, object] = {}
        for scope in ("own", "hist"):
            if not sel:
                d[scope] = None
                continue
            m = {k: float(np.mean([x[scope][k] for x in sel])) for k in ("total", "bias", "weight", "stats")}
            d[scope] = {"n": len(sel), "mean_total": m["total"], "mean_bias": m["bias"], "mean_weight": m["weight"], "mean_stats": m["stats"],
                        "mean_interaction": m["total"] - m["bias"] - m["weight"] - m["stats"],
                        "share_bias": (m["bias"] / m["total"]) if m["total"] != 0 else float("nan")}
        out[cls] = d
    own_n = out["N"].get("own")
    out["mechanism_holds"] = bool(own_n is not None and own_n["share_bias"] > 0.5)
    return out


# ====================================================================================================== THE LOADER AND THE RENDERER
# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:38 +0400 — `summarise_life`, `load_all`, `render`, `main`.
ROOM_WORDS = {"R1": ("circle", "square"), "R2": ("triangle", "cross"), "R3": ("ring", "star")}
VOCAB13 = ("big", "small", "red", "blue", "green", "yellow", "white", "circle", "square", "triangle", "cross", "ring", "star")


def _pooled(row: Sequence[Optional[float]], words: Sequence[str], n: Mapping[str, int]) -> float:
    num = den = 0.0
    for w in words:
        v = row[VOCAB13.index(w)]
        if v is not None and n.get(w):
            num += v * n[w]
            den += n[w]
    return num / den if den else float("nan")


def summarise_life(rec: Mapping[str, object]) -> Dict[str, object]:
    """The numbers one life contributes (the record is large; the report keeps these)."""
    m = rec["marks"]
    rows = rec["record"]
    n_rr = len(rec["rooms"])
    pol = [x for x in rows if x["block"] > n_rr]
    late = [x for x in pol if x["block"] >= 101]
    out: Dict[str, object] = {"A": float(m["A"]), "SN": float(m["share"]["N"]), "M1": m.get("M1"), "lock": m.get("longest_run"),
                              "SNL": sum(1 for x in late if x["room"] == "N" and x["flag"] == "policy") / max(1, len(late)),
                              "LR": None, "LRfinal": None, "ear_full_first": None, "ear_last_wrong": None, "ear_end_ok": None, "histN": None}
    ex = rec.get("extra") or {}
    n = rec.get("word_n", {})
    rc = ex.get("rates_curve")
    if rc:
        out["LR"] = {r: float(np.mean([_pooled(row, ws, n) for row in rc])) for r, ws in ROOM_WORDS.items()}
        out["LRfinal"] = {r: _pooled(rc[-1], ws, n) for r, ws in ROOM_WORDS.items()}
    elif rec.get("rates_end"):
        out["LRfinal"] = {r: _pooled([rec["rates_end"].get(w) for w in VOCAB13], ws, n) for r, ws in ROOM_WORDS.items()}
    ok, nh = ex.get("ear_ok"), ex.get("n_heard")
    if ok and nh:
        out["ear_full_first"] = next((b for b, (o, h) in enumerate(zip(ok, nh), start=1) if o and h == 13), None)
        wrong = [b for b, o in enumerate(ok, start=1) if not o]
        out["ear_last_wrong"] = wrong[-1] if wrong else 0
        out["ear_end_ok"] = bool(ok[-1])
    hw = ex.get("hist_w_N")
    if hw:
        out["histN"] = [float(hw[min(len(hw) - 1, b - 1)]) for b in range(20, 201, 20)]
    return out


def load_all(root: Path, seeds: Sequence[int]) -> Tuple[Dict[str, Dict[int, List[Dict[str, object]]]], List[Mapping[str, object]], Dict[str, int]]:
    """arms -> seed -> [life summaries in replicate order]; the anatomy rows of RANDOM's lives; the record counts."""
    import json
    arms: Dict[str, Dict[int, List[Dict[str, object]]]] = {}
    decomp: List[Mapping[str, object]] = []
    counts: Dict[str, int] = {}
    for arm_dir in sorted(Path(root).iterdir()):
        if not arm_dir.is_dir():
            continue
        for s in seeds:
            d = arm_dir / str(s)
            if not d.is_dir():
                continue
            for f in sorted(d.glob("*.json")):
                rec = json.loads(f.read_text())
                arms.setdefault(arm_dir.name, {}).setdefault(s, []).append(summarise_life(rec))
                counts[arm_dir.name] = counts.get(arm_dir.name, 0) + 1
                if arm_dir.name == "RANDOM":
                    decomp.extend(rec.get("extra", {}).get("decomp", []))
    return arms, decomp, counts


def _f(x, nd=3) -> str:
    return "—" if x is None or (isinstance(x, float) and x != x) else f"{x:.{nd}f}"


def render(an: Mapping[str, object], arms, decomp, counts, seeds: Sequence[int]) -> List[str]:
    L: List[str] = []
    ctl, A, V = an["controls"], an["arms"], an["verdict"]
    L.append(f"TOY A — COMPRESSION PROGRESS · seeds {seeds[0]}–{seeds[-1]} ({len(seeds)}) · held-out seeds {an['held_out_seeds'][0]}–{an['held_out_seeds'][-1]} ({len(an['held_out_seeds'])})")
    L.append("lives on disk: " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    L.append(f"THE NULL (RANDOM's 20 lives a seed split 10/10, {an['null']['draws']} draws): sd of D_null {an['null']['sd_A']:.5f} (A), {an['null']['sd_N']:.5f} (SHARE_N); smallest passing D "
             f"{an['null']['q99_A']:.5f} (A, upper 1 − 0.0056), largest passing Dn {an['null']['q_lower_N']:.5f} (SHARE_N, lower 0.0056); on the 7 held-out seeds {an['null']['q99_A_ho']:.5f}")
    L.append("")
    L.append("THE CONTROLS (the world can show it):")
    L.append(f"   PC1 R-ONLY beats RANDOM: G = {ctl['G']:+.4f}, positive at {ctl['PC1']['signs']} of {len(seeds)} seeds → {'PASS' if ctl['PC1']['ok'] else 'FAIL'}  (per seed " +
             " ".join(f"{g:+.3f}" for g in ctl['G_by_seed']) + ")")
    L.append(f"   PC2 ERROR is trapped: SHARE_N > 0.5 at {ctl['PC2']['n_over_half']} of {len(seeds)} seeds → {'PASS' if ctl['PC2']['ok'] else 'FAIL'}")
    L.append(f"   PC3 N-ONLY loses: A below RANDOM's 2.5 % band edge at {ctl['PC3']['n_below_band']} of {len(seeds)} seeds → {'PASS' if ctl['PC3']['ok'] else 'FAIL'}")
    L.append(f"   CEILING: G {ctl['G']:.4f} ≥ 3 × the smallest passing D {3 * ctl['smallest_D']:.4f} → {'PASS' if ctl['ceiling_ok'] else 'FAIL'};  GRADABLE: {ctl['gradable']}")
    L.append("")
    L.append(f"{'arm':14s} {'A':>6s} {'SHARE_N':>8s} {'late N':>7s} {'D':>8s} {'p_A':>7s} {'sgn':>4s} {'BEAT':>5s} {'Dn':>8s} {'p_N':>7s} {'sgn':>4s} {'LEAVE':>6s} {'esc.share':>10s} {'sdA×':>5s} {'sdN×':>5s}  flags")
    for arm in NINE:
        a = A[arm]
        late = float(np.mean([l["SNL"] for s in seeds for l in arms[arm][s]]))
        flags = []
        if a["sd_flag_A"] or a["sd_flag_N"]:
            flags.append("SD-FLAGGED (sign count only, ≥ 9 of 10)")
        if a["CONTAMINATED"]:
            flags.append("CONTAMINATED")
        L.append(f"{arm:14s} {a['A']:6.3f} {a['SN']:8.3f} {late:7.3f} {a['D']:+8.4f} {a['p_A']:7.4f} {a['sign_A']:2d}/{len(seeds)} {str(a['BEAT']):>5s} {a['Dn']:+8.4f} {a['p_N']:7.4f} {a['sign_N']:2d}/{len(seeds)} "
                 f"{str(a['LEAVE']):>6s} {a['escaped_share']:+10.3f} {a['sd_ratio_A']:5.2f} {a['sd_ratio_N']:5.2f}  {' · '.join(flags)}")
    for ref in ("RANDOM", "R-ONLY", "ERROR", "N-ONLY", "ORACLE"):
        if ref in arms:
            A_ = float(np.mean([l["A"] for s in seeds for l in arms[ref][s]]))
            N_ = float(np.mean([l["SN"] for s in seeds for l in arms[ref][s]]))
            L.append(f"{ref:14s} {A_:6.3f} {N_:8.3f}   (reference)")
    L.append("")
    L.append(f"THE HELD-OUT READING of the ema cells (seeds {an['held_out_seeds'][0]}–{an['held_out_seeds'][-1]} alone; ≥ 6 of 7 (7 of 7 if SD-flagged) and p' ≤ 0.0056 on the 7-seed null; smallest passing D' {an['null']['q99_A_ho']:.5f}):")
    for arm in EMA_CELLS:
        h = A[arm]["held_out"]
        L.append(f"   {arm:12s} D' {h['D']:+.4f} p' {h['p_A']:.4f} signs {h['signs_A']}/7 BEAT {h['BEAT']} · Dn' {h['Dn']:+.4f} p' {h['p_N']:.4f} signs {h['signs_N']}/7 LEAVE {h['LEAVE']} → "
                 f"counted BEAT {A[arm]['BEAT_counted']} LEAVE {A[arm]['LEAVE_counted']}{' · CONTAMINATED' if A[arm]['CONTAMINATED'] else ''}")
    L.append("")
    for key, label in (("main_effects_A", "A"), ("main_effects_SN", "SHARE_N")):
        L.append(f"THE FACTORIAL'S MAIN EFFECTS on {label} (mean over the other factors' cells of high − low; loss C−L, scope hist−own, time ema−last2):")
        for f in ("loss", "scope", "time"):
            e = an[key][f]
            neg = sum(1 for v in e["per_seed"] if v < 0)
            L.append(f"   {f:6s} mean {e['mean']:+.4f}  se {e['se']:.4f}  positive at {e['signs']} / negative at {neg} of {len(seeds)} seeds  95% CI [{e['ci95'][0]:+.4f}, {e['ci95'][1]:+.4f}]")
    L.append("")
    # ---- predictions and refutations
    ho = len(an["held_out_seeds"])
    L.append("PREDICTIONS (written before any life) and REFUTATIONS:")
    rand_band_N = {s: float(np.quantile([l["SN"] for l in arms["RANDOM"][s]], 0.025)) for s in seeds}
    rand_band_A = {s: (float(np.quantile([l["A"] for l in arms["RANDOM"][s]], 0.025)), float(np.quantile([l["A"] for l in arms["RANDOM"][s]], 0.975))) for s in seeds}
    for arm in ("L-hist-last2", "L-hist-ema"):
        sn = {s: float(np.mean([l["SN"] for l in arms[arm][s]])) for s in seeds}
        over = sum(1 for s in seeds if sn[s] >= 0.5)
        over_ho = sum(1 for s in an["held_out_seeds"] if sn[s] >= 0.5)
        below = sum(1 for s in seeds if sn[s] < rand_band_N[s])
        below_ho = sum(1 for s in an["held_out_seeds"] if sn[s] < rand_band_N[s])
        L.append(f"   P1 {arm}: SHARE_N ≥ 0.5 at {over}/{len(seeds)} seeds (held-out {over_ho}/{ho}); below RANDOM's band at {below}/{len(seeds)} (held-out {below_ho}/{ho}) → "
                 f"P1 {'HOLDS' if over >= 8 and over_ho >= 6 else 'does not hold'}; refuted-by-escape {'YES' if below >= 8 and below_ho >= 6 else 'no'}")
    for loss in ("L", "C"):
        e, l2 = f"{loss}-own-ema", f"{loss}-own-last2"
        inside = sum(1 for s in seeds if rand_band_A[s][0] <= float(np.mean([l["A"] for l in arms[e][s]])) <= rand_band_A[s][1])
        L.append(f"   P2 {e} vs {l2}: SHARE_N {A[e]['SN']:.3f} vs {A[l2]['SN']:.3f} ({'lower' if A[e]['SN'] < A[l2]['SN'] else 'not lower'}); A inside RANDOM's band at {inside}/{len(seeds)} seeds")
    L.append(f"   P3 the cells passing BOTH counted bars: {V['both'] or 'none'} (predicted: the C-hist cells only)")
    reach = {a: sum(1 for s in seeds if np.mean([l['A'] for l in arms[a][s]]) >= np.mean([l['A'] for l in arms['R-ONLY'][s]])) for a in NINE}
    L.append("   P4 seeds at which an arm's A reaches R-ONLY's: " + " · ".join(f"{a} {n}" for a, n in reach.items()) + f" (predicted: none) → {'HOLDS' if not any(reach.values()) else 'does not hold'}")
    L.append(f"   P5 LP-OUDEYER D {A['LP-OUDEYER']['D']:+.4f} vs L-own-last2 D {A['L-own-last2']['D']:+.4f} (difference {abs(A['LP-OUDEYER']['D'] - A['L-own-last2']['D']):.4f} against the smallest passing D {an['null']['q99_A']:.4f}) → "
             f"{'≈' if abs(A['LP-OUDEYER']['D'] - A['L-own-last2']['D']) < an['null']['q99_A'] else 'differs'}")
    for f in ("loss", "scope"):
        e = an["main_effects_SN"][f]
        neg = sum(1 for v in e["per_seed"] if v < 0)
        L.append(f"   H-quantity ({f}): main effect on SHARE_N {e['mean']:+.4f}, negative at {neg}/{len(seeds)} seeds, CI [{e['ci95'][0]:+.4f}, {e['ci95'][1]:+.4f}] → "
                 f"{'supported' if neg >= 8 and e['ci95'][1] < 0 else 'not supported'}")
    et, ea = an["main_effects_SN"]["time"], an["main_effects_A"]["time"]
    inside_t = abs(et["mean"]) <= abs(an["null"]["q_lower_N"]) and abs(ea["mean"]) <= an["null"]["q99_A"]
    L.append(f"   H-time: main effect on SHARE_N {et['mean']:+.4f} and on A {ea['mean']:+.4f} against the null's {an['null']['q_lower_N']:+.4f} / {an['null']['q99_A']:+.4f} → "
             f"{'REFUTED (both inside the null band)' if inside_t else 'not refuted'}")
    L.append("")
    # ---- the drop's anatomy (§0 item 4)
    L.append("THE DROP'S ANATOMY over RANDOM's lives (single-factor drops from the state before a block toward the state after it; own window and history-wide):")
    for label, mb in (("the 196 policy blocks (5-200) — the READING THAT DECIDES", 5), ("all blocks (1-200)", 1), ("blocks ≥ 21", 21)):
        an_ = anatomy(decomp, min_block=mb)
        L.append(f"   {label}:")
        for cls in ("N", "R"):
            for scope in ("own", "hist"):
                d = an_[cls][scope]
                if d:
                    L.append(f"      {'N' if cls == 'N' else 'R1–R3'} blocks, {scope:4s} (n {d['n']}): total {d['mean_total']:+.4f} = bias {d['mean_bias']:+.4f} + weight {d['mean_weight']:+.4f} + stats "
                             f"{d['mean_stats']:+.4f} + interaction {d['mean_interaction']:+.4f}   share_bias {d['share_bias']:+.3f}")
        if mb == 5:
            L.append(f"   §0 item 4's mechanism (the bias part is the MAJORITY of the drop in N's blocks): {'HOLDS' if an_['mechanism_holds'] else 'REFUTED — the bias part is not the majority in N blocks'}")
    L.append("")
    # ---- the ear, N's history weight, learned per room
    L.append("THE EAR'S OWN TYPE COVER (first block at which all 13 words are heard AND Ear.cover over the heard words equals the vocabulary map; 'never' if never):")
    for s in seeds:
        v = [l["ear_full_first"] for arm in arms for l in arms[arm].get(s, []) if l["ear_end_ok"] is not None]
        got = [x for x in v if x is not None]
        wrong_end = sum(1 for arm in arms for l in arms[arm].get(s, []) if l["ear_end_ok"] is False)
        L.append(f"   {s}: lives {len(v)} · first-correct block min {min(got) if got else 'never'} / median {int(np.median(got)) if got else 'never'} / max {max(got) if got else 'never'}"
                 f" · never-correct lives {len(v) - len(got)} · wrong at block 200 in {wrong_end}")
    L.append("N'S HISTORY WEIGHT n_N / Σ n_j at blocks 20, 40, … 200 (mean over lives):")
    for arm in list(NINE) + ["RANDOM", "ERROR"]:
        h = [l["histN"] for s in seeds for l in arms[arm][s] if l["histN"]]
        if h:
            L.append(f"   {arm:14s} " + " ".join(f"{v:.3f}" for v in np.mean(h, axis=0)))
    L.append("LEARNED PER ROOM (mean over the 200 boundaries of the pooled forced-naming accuracy of the room's own shape words; the minimum over rooms; final accuracy):")
    for arm in list(NINE) + ["RANDOM", "R-ONLY", "ERROR", "N-ONLY"]:
        lr = [l["LR"] for s in seeds for l in arms[arm][s] if l["LR"]]
        fin = [l["LRfinal"] for s in seeds for l in arms[arm][s] if l["LRfinal"]]
        if lr:
            L.append(f"   {arm:14s} R1 {np.mean([x['R1'] for x in lr]):.3f} R2 {np.mean([x['R2'] for x in lr]):.3f} R3 {np.mean([x['R3'] for x in lr]):.3f} · min {np.mean([min(x.values()) for x in lr]):.3f}"
                     f" · final R1 {np.mean([x['R1'] for x in fin]):.3f} R2 {np.mean([x['R2'] for x in fin]):.3f} R3 {np.mean([x['R3'] for x in fin]):.3f}")
    L.append("")
    S2 = an["stage2"]
    L.append(f"STAGE 2 (the credit-derangement NULL — the arm blind to WHERE only — 10 replicates × 10 seeds, for each arm that passes BEAT; the arm is VOID iff its NULL passes the plain 10-seed BEAT): "
             f"arms {V['stage2_arms'] or 'none required'}; missing {S2['missing'] or 'none'}")
    if S2["arms"]:
        L.append(f"   {'arm':14s} {'NULL A':>7s} {'NULL SHARE_N':>12s} {'D(NULL)':>9s} {'p_A':>7s} {'sgn':>5s} {'sdA×':>5s} {'BEAT':>5s} {'counted':>8s} {'VOID':>5s} {'arm−NULL A':>11s} {'sgn':>5s} {'NULL lock-in mean/max':>22s}  NULL LEAVE")
        for arm, r in S2["arms"].items():
            lock = f"{r['lock_mean']:.1f}/{r['lock_max']}" if r["lock_mean"] is not None else "—"
            L.append(f"   {arm:14s} {r['null_A']:7.3f} {r['null_SN']:12.3f} {r['D']:+9.4f} {r['p_A']:7.4f} {r['signs']:2d}/{len(seeds)} {r['sd_ratio_A']:5.2f} {str(r['beat']):>5s} {str(r['beat_counted']):>8s} "
                     f"{str(r['void']):>5s} {r['gain_mean']:+11.4f} {r['gain_signs']:2d}/{len(seeds)} {lock:>22s}  {r['Dn']:+.4f} p {r['p_N']:.4f} {r['signs_N']}/{len(seeds)} {str(r['leave'])}")
        L.append(f"   (the smallest passing D for BEAT is {an['null']['q99_A']:.4f}; a NULL whose replicate SD is more than twice RANDOM's is judged by the sign count at ≥ 9 of 10 alone)")
    L.append(f"VERDICT CLASS: {V['class']}  (arms passing the counted BEAT: {V['beat_arms'] or 'none'} · the counted LEAVE: {V['leave_arms'] or 'none'} · both: {V['both'] or 'none'} · "
             f"beat without leaving: {V['beats_without_leaving'] or 'none'} · FIXED (both bars and a NULL that does not pass BEAT): {V['fixed_arms'] or 'none'} · VOID: {V['void_arms'] or 'none'})")
    return L


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="TOY A's report over the lives' records")
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3] / "scratch" / "toys-cp" / "runs")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--draws", type=int, default=10000)
    ns = ap.parse_args(argv)
    seeds = list(range(20261301, 20261311))
    arms, decomp, counts = load_all(ns.root, seeds)
    need = list(NINE) + ["RANDOM", "R-ONLY", "ERROR", "N-ONLY"]
    missing = [a for a in need if a not in arms or any(s not in arms[a] for s in seeds)]
    if missing:
        print(f"records missing for {missing}; run the unit first", file=__import__("sys").stderr)
        return 2
    an = analyse(arms, seeds, draws=ns.draws)
    lines = render(an, arms, decomp, counts, seeds)
    text = "\n".join(lines) + "\n"
    print(text)
    if ns.out:
        ns.out.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
