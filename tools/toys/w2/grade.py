"""grade.py — PREREG-T-L4 §5-§6: the grader's arithmetic. auc() by average ranks, the derangement check, the Hanley-McNeil se, the M1 / M5 rules,
M3's FAMILY statistic (the law's own null made free, one T per interface), M4 (a)'s naming rule as a comparison of maxima, and §6's TOTAL, ORDERED
verdict rule. Arithmetic only: no learner, no stream.

edit: Claude (Fable 5.1, swarm integrator INTEGRATOR-F2), 2026-10-04 02:55 +0400 — new file, written after tests/tools/test_tl4_grade.py was red; law
docs/organism/whole/PREREG-T-L4.md at t-l4-1003 d5111a6 (SIGNED x3), §5.1 G0b, §5.2 M1 / M3 / M4 / M5, §5.3, §6.
edit: Kimi K3 (kimi-code, builder lane), 2026-10-04 22:10 +0400 — AMENDMENT 1 A1.2 (SIGNED x3, ruled wording a): flatness() gains `center`
(M5 reads against the null's OWN measured centre c_cell; 0.5 stays the default); tests tools/test_tl4_grade.py TestM5Amendment1 were red first.
"""
from __future__ import annotations

import math
from typing import Dict, Hashable, List, Mapping, Optional, Sequence

import numpy as np
from scipy import stats

Z_P001 = 3.090232                                       # one-sided z at p = 0.001
INTERFACES = ("S", "W")
STATES = ("doubt", "young", "ask_prev")
VERDICTS = ("VOID", "PASS", "PASS-WIDE", "CROSS-FIRE", "PASS-WITH-HARM", "PARTIAL", "FAIL-SLOW", "FAIL-STRUCTURE")


# ----------------------------------------------------------------------------------------------------- the grader (G0b)
def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """The Mann-Whitney statistic with AVERAGE ranks for ties: P(score+ > score-) + 0.5 P(tie)."""
    s = np.asarray(scores, dtype=np.float64); y = np.asarray(labels).astype(bool)
    n1 = int(y.sum()); n0 = int(y.size - n1)
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = stats.rankdata(s, method="average")
    return float((r[y].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def auc_bruteforce(scores: np.ndarray, labels: np.ndarray) -> float:
    s = np.asarray(scores, dtype=np.float64); y = np.asarray(labels).astype(bool)
    pos, neg = s[y], s[~y]
    d = pos[:, None] - neg[None, :]
    return float((np.sum(d > 0) + 0.5 * np.sum(d == 0)) / (pos.size * neg.size))


def assert_derangement(perm: np.ndarray) -> None:
    p = np.asarray(perm)
    assert np.array_equal(np.sort(p), np.arange(p.size)), "not a permutation"
    fixed = np.flatnonzero(p == np.arange(p.size))
    assert fixed.size == 0, f"a fixed point at {fixed[:5].tolist()}"


def se0(n_pos: int, n_neg: int) -> float:
    """Hanley-McNeil standard error of an AUC under the null 0.5."""
    return math.sqrt((n_pos + n_neg + 1.0) / (12.0 * n_pos * n_neg))


def passing_auc(n_pos: int, n_neg: int, z: float = Z_P001) -> float:
    return 0.5 + z * se0(n_pos, n_neg)


def kth_smallest(values: Sequence[float], k: int) -> float:
    v = np.sort(np.asarray(values, dtype=np.float64))
    return float(v[min(k, v.size) - 1])


def q95_of(dealt: Sequence[float]) -> float:
    """M1's bar: the 95th smallest of 100 dealt AUCs; with fewer draws (the pilot's 10) the maximum stands for q95 (§7.1)."""
    v = np.asarray(dealt, dtype=np.float64)
    return kth_smallest(v, 95) if v.size >= 100 else float(v.max())


# ---------------------------------------------------------------------------------------------------------- M1, M2, M5
def m1_rule(auc: float, c_read: float, dealt: Sequence[float]) -> Dict[str, object]:
    """BIND: SKILL = (AUC - 0.5) / (C_read - 0.5) >= 0.90 AND AUC > q95 of the dealt draws."""
    skill = (auc - 0.5) / (c_read - 0.5) if c_read > 0.5 else float("nan")
    q95 = q95_of(dealt)
    return {"auc": float(auc), "c_read": float(c_read), "skill": float(skill), "q95": q95, "n_dealt": int(len(dealt)),
            "pass": bool(skill >= 0.90 and auc > q95)}


def m2_rule(auc_cont: float, auc_nostate: float, c_read: float) -> Dict[str, object]:
    gain = auc_cont - auc_nostate
    return {"gain": float(gain), "margin": float(c_read - 0.5 - 0.30), "pass": bool(gain >= 0.30)}


def flatness(dealt: Sequence[float], c_read: float, center: float = 0.5) -> Dict[str, object]:
    """M5 NULL-FLAT (= G0d), AMENDMENT 1 A1.2 (SIGNED x3, ruled wording a): |median - center| <= 0.10 and
    q95 <= center + 0.5 (C_read - 0.5), center = the null's OWN measured centre c_cell pre-registered per (interface, word)
    (the 0.5-ideal was the instrument fault the amendment fixes; 0.5 stays the default for unsigned callers). Fed the
    ORACLE's AUC as a one-draw null it must REJECT (the plant holds under (a): C_read >= 0.90 puts the centre clause out on
    every cell)."""
    v = np.asarray(dealt, dtype=np.float64)
    med = float(np.median(v)); q95 = q95_of(v)
    bar = center + 0.5 * (c_read - 0.5)
    return {"median": med, "q95": q95, "q95_bar": float(bar), "center": float(center), "n": int(v.size),
            "pass": bool(abs(med - center) <= 0.10 and q95 <= bar)}


# ------------------------------------------------------------------------------------------------- M3: the family statistic
def family_T(cont: Mapping[Hashable, float], dealt: Mapping[Hashable, Sequence[float]], se0_cells: Mapping[Hashable, float]) -> Dict[str, object]:
    """ONE family statistic per interface over its 18 cells (3 seeds x 6 off-diagonals): T(x) = max over cells of |AUC_x(cell) - 0.5| / s_null(cell),
    s_null = the dealt sd FLOORED at the cell's exchangeable se0; for CONT and for each dealt index k (its own 18 cells, the k-th deal of each seed).
    M3 holds iff T(CONT) < q95{T(k)} (np.quantile, linear). The null carries its own multiplicity: a null-like CONT fails with P ~ 0.05 by
    construction. Printed beside it: each cell's [q02.5, q97.5], the fixed +-0.10 reading, the argmax cell."""
    cells = list(cont.keys())
    K = len(next(iter(dealt.values())))
    s_null: Dict[Hashable, float] = {}
    bands: Dict[Hashable, tuple] = {}
    inside_010: Dict[Hashable, bool] = {}
    inside_band: Dict[Hashable, bool] = {}
    dev_cont: Dict[Hashable, float] = {}
    T_dealt = np.zeros(K)
    for c in cells:
        v = np.asarray(dealt[c], dtype=np.float64)
        assert v.size == K, "every cell needs the same number of dealt learners (paired by deal index k)"
        sd = float(np.std(v, ddof=1)) if v.size > 1 else 0.0
        s_null[c] = max(sd, float(se0_cells[c]))
        lo, hi = (float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975)))
        bands[c] = (lo, hi)
        inside_band[c] = bool(lo <= cont[c] <= hi)
        inside_010[c] = bool(abs(cont[c] - 0.5) <= 0.10)
        dev_cont[c] = abs(cont[c] - 0.5) / s_null[c]
        T_dealt = np.maximum(T_dealt, np.abs(v - 0.5) / s_null[c])
    T_cont = max(dev_cont.values())
    worst_cell = max(cells, key=lambda c: dev_cont[c])              # the (seed, w, w') cell that drives T(CONT), named in the output
    q95 = float(np.quantile(T_dealt, 0.95))
    return {"T_cont": float(T_cont), "T_dealt": T_dealt.tolist(), "q95": q95, "argmax": worst_cell, "pass": bool(T_cont < q95),
            "s_null": s_null, "bands": bands, "inside_band": inside_band, "inside_pm_010": inside_010, "dev_cont": dev_cont,
            "n_cells": len(cells), "K": K, "false_fail_by_construction": 0.05,
            "false_fail_per_cell_reads": float(1.0 - 0.95 ** len(cells))}


# -------------------------------------------------------------------------------------------------------- M4 (a)
def naming_correct(p_names: np.ndarray, class_name_mask: np.ndarray) -> bool:
    """«The best-scored trained name is one the class was given in TRAIN», read as a comparison of maxima (the class's names CONTAIN the maximum),
    never as a selection over the lexicon (M6): a tie at the maximum counts as inside the set."""
    p = np.asarray(p_names, dtype=np.float64); m = np.asarray(class_name_mask, dtype=bool)
    return bool(m.any() and p[m].max() >= p.max())


# -------------------------------------------------------------------------------------------------------- section 6
def verdict(m1: Mapping[str, Mapping[str, Optional[bool]]], m3: Mapping[str, bool], m4: Mapping[str, bool],
            lr10: Mapping[str, bool]) -> Dict[str, object]:
    """§6, TOTAL and ORDERED: m1[I][s] is True (M1 holds for state s on interface I on all seeds), False, or None (the cell is VOID: a gate or M5
    failed on a seed). An interface BINDS when every cell is True; it is CLEAN when m3[I]; HARMLESS when m4[I]; a state binds somewhere when some
    interface's cell for it is True. The first row whose condition holds is the verdict."""
    ifs = tuple(m1.keys())
    gradable = {I: all(m1[I][s] is not None for s in STATES) for I in ifs}
    binds = {I: gradable[I] and all(bool(m1[I][s]) for s in STATES) for I in ifs}
    clean = {I: bool(m3[I]) for I in ifs}
    harmless = {I: bool(m4[I]) for I in ifs}
    bound = {s: any(m1[I][s] is True for I in ifs) for s in STATES}
    rows: List[int] = []
    if not any(gradable.values()):
        rows.append(1); name = "VOID"
    elif binds["S"] and clean["S"] and harmless["S"]:
        rows.append(2); name = "PASS"
    elif binds["W"] and clean["W"] and harmless["W"]:
        rows.append(3); name = "PASS-WIDE"
    elif any(binds.values()) and not any(binds[I] and clean[I] for I in ifs):
        rows.append(4); name = "CROSS-FIRE"
    elif any(binds[I] and clean[I] for I in ifs):
        rows.append(5); name = "PASS-WITH-HARM"
    elif any(bound.values()):
        rows.append(6); name = "PARTIAL"
    elif any(bool(lr10[s]) for s in STATES):
        rows.append(7); name = "FAIL-SLOW"
    else:
        rows.append(8); name = "FAIL-STRUCTURE"
    return {"verdict": name, "rows_matched": rows, "binds": binds, "clean": clean, "harmless": harmless, "bound_states": bound,
            "gradable": gradable, "void_cells": [(I, s) for I in ifs for s in STATES if m1[I][s] is None],
            "lr10_pass": [s for s in STATES if bool(lr10[s])]}
