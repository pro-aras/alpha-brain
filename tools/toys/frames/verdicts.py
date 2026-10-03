"""verdicts.py — TOY C's bars and gates as pure functions over condition records (docs/research/toys/PREREG-TOY-FRAMES.md §4; AMENDMENT-1 §1, §4 (e)).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:03 +0400 — new module, red-first against tests/tools/test_toys_frames_verdicts.py (stage 4c).

  GAIN(rule, ALPHA4)   G(F) > q95 of NULL-1 AND G(F) > 0; WEB-S is judged by the seeds that pass (>= 8 of 10; the exact sign p = P(X >= n_pass | Bin(10, 1/2)) printed).
  SHUFFLE-QUIET        F empty, or G(F) <= q95 of NULL-1, on ALPHA4+SHUFFLE; WEB-S quiet when >= 8 of its ten seeds are (AMENDMENT-1 §4 (e)).
  PLANT gate           AMENDMENT-1 §1 (mode amend1: keeps F* AND (B) AND (C); WEB-S >= 9 of 10 seeds counting a seed only if keeps AND (C)) or the base text's clause (mode law: keeps AND (A)); plants.gate_passes.
  GATE FIRST (per stream)  a rule that fails its PLANT gate or is not SHUFFLE-QUIET on ALPHA4 reads NOT GRADABLE for GAIN there; SCENE's readings are gated by SCENE+PLANT only.
  CRITERION-MATTERS    G(F) > q95 of NULL-2 AND G(F) > 0 (WEB-S: seeds of ten), NOT GRADABLE when PLANT-BEATS-NULL-2 fails on ALPHA4+PLANT.
Readings: the eye's (the cells' 40 said frames against each rule's kept set), the rules' Jaccard overlaps, each rule's recall of F_oracle.
"""
from __future__ import annotations

from math import comb
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

from . import plants as PL

RULES: Tuple[str, ...] = ("WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY")
WEB_S_MIN = 8                                         # «passes» / «quiet» needs 8 of 10 seeds (exact sign p = 0.0547)


def by_rule(cond: Dict[str, object]) -> Dict[str, List[Dict[str, object]]]:
    out: Dict[str, List[Dict[str, object]]] = {}
    for r in cond["records"]:
        out.setdefault(r["rule"], []).append(r)
    return out


def _need(rule: str, n: int) -> int:
    return -(-WEB_S_MIN * n // 10) if rule == "WEB-S" else n


def _sign_p(n: int, k: int) -> float:
    return sum(comb(n, j) for j in range(k, n + 1)) / 2 ** n


def _null_ok(rec: Dict[str, object], key: str) -> bool:
    n = rec.get(key)
    return bool(n) and "error" not in n


def gain_pass(rec: Dict[str, object]) -> bool:
    return _null_ok(rec, "null1") and rec["n_frames"] > 0 and rec["gain"]["G"] > rec["null1"]["q95"] and rec["gain"]["G"] > 0


def gain_verdicts(cond: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {}
    for rule, recs in by_rule(cond).items():
        n = len(recs)
        k = sum(1 for r in recs if gain_pass(r))
        need = _need(rule, n)
        out[rule] = {"n": n, "n_pass": k, "need": need, "passes": k >= need, "exact_sign_p": _sign_p(n, k), "no_null": sum(1 for r in recs if not _null_ok(r, "null1")),
                     "per_seed": [bool(gain_pass(r)) for r in recs]}
    return out


def quiet_pass(rec: Dict[str, object]) -> bool:
    return rec["n_frames"] == 0 or (_null_ok(rec, "null1") and rec["gain"]["G"] <= rec["null1"]["q95"])


def shuffle_quiet(cond: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {}
    for rule, recs in by_rule(cond).items():
        n = len(recs)
        k = sum(1 for r in recs if quiet_pass(r))
        need = _need(rule, n)
        out[rule] = {"n": n, "n_quiet": k, "need": need, "quiet": k >= need, "empty": sum(1 for r in recs if r["n_frames"] == 0)}
    return out


def plant_gates(cond: Dict[str, object], mode: str) -> Dict[str, Dict[str, object]]:
    B = cond["plant_stream"]["B"]
    out: Dict[str, Dict[str, object]] = {}
    for rule, recs in by_rule(cond).items():
        rows = [dict(r["plant"], seed=r["seed"]) for r in recs]
        out[rule] = PL.gate_passes(rule, rows, B, mode)
    return out


def criterion_pass(rec: Dict[str, object]) -> bool:
    return _null_ok(rec, "null2") and rec["n_frames"] > 0 and rec["gain"]["G"] > rec["null2"]["q95"] and rec["gain"]["G"] > 0


def criterion_matters(cond: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {}
    for rule, recs in by_rule(cond).items():
        n = len(recs)
        k = sum(1 for r in recs if criterion_pass(r))
        need = _need(rule, n)
        out[rule] = {"n": n, "n_pass": k, "need": need, "matters": k >= need}
    return out


def grade(conds: Dict[str, Dict[str, object]], mode: str) -> Dict[str, object]:
    """The five conditions ALPHA4, ALPHA4+PLANT, ALPHA4+SHUFFLE, SCENE, SCENE+PLANT -> every rule's gates and verdicts (GATE FIRST per stream)."""
    if mode not in ("amend1", "law"):
        raise ValueError(f"grade: mode {mode!r} is not amend1 | law")
    a4, a4p, a4s = conds["ALPHA4"], conds["ALPHA4+PLANT"], conds["ALPHA4+SHUFFLE"]
    scp = conds["SCENE+PLANT"]
    pg_a4, sq, gv, cm = plant_gates(a4p, mode), shuffle_quiet(a4s), gain_verdicts(a4), criterion_matters(a4)
    pg_sc = plant_gates(scp, mode)
    beats2 = {"ALPHA4+PLANT": bool(a4p["plant_stream"]["plant_beats_null2"]), "SCENE+PLANT": bool(scp["plant_stream"]["plant_beats_null2"])}
    out: Dict[str, object] = {"mode": mode, "plant_beats_null2": beats2, "alpha4": {}, "scene": {}}
    for rule in RULES:
        if rule not in gv:
            continue
        gate_ok = bool(pg_a4[rule]["pass"] and sq[rule]["quiet"])
        verdict = "NOT GRADABLE" if not gate_ok else ("PASS" if gv[rule]["passes"] else "FAIL")
        if not beats2["ALPHA4+PLANT"]:
            crit = "NOT GRADABLE"
        else:
            crit = "YES" if cm[rule]["matters"] else "NO"
        out["alpha4"][rule] = {"plant_gate": pg_a4[rule], "shuffle_quiet": sq[rule], "gate_first_ok": gate_ok, "gain": gv[rule], "gain_verdict": verdict,
                               "criterion": dict(cm[rule], verdict=crit)}
        out["scene"][rule] = {"plant_gate": pg_sc[rule], "gradable": bool(pg_sc[rule]["pass"])}
    return out


# ------------------------------------------------------------------------------------------------------------------ readings
def eye_reading(cond: Dict[str, object], says: Sequence[Tuple[str, str, object]]) -> Dict[str, object]:
    """The cells' said frames (frame text, the eye's `heard`, seq) against each record's kept set: how many of the distinct said frames it keeps, the pooled yes-rate of the says of the frames it
    keeps against those it does not (n printed), and the frames it keeps that the cells never said. A said frame of any other length than two words can never be a kept pair."""
    said: Dict[str, Dict[str, object]] = {}
    for text, heard, _seq in says:
        w = tuple(text.split())
        e = said.setdefault(text, {"pair": (w if len(w) == 2 else None), "says": 0, "yes": 0})
        e["says"] += 1
        e["yes"] += int(heard == "yes")
    total_says = sum(e["says"] for e in said.values())
    total_yes = sum(e["yes"] for e in said.values())
    said_pairs = {e["pair"] for e in said.values() if e["pair"] is not None}
    recs = []
    for r in cond["records"]:
        kept = {tuple(f) for f in r["frames"]}
        in_k = [e for e in said.values() if e["pair"] in kept]
        says_k = sum(e["says"] for e in in_k)
        yes_k = sum(e["yes"] for e in in_k)
        says_n, yes_n = total_says - says_k, total_yes - yes_k
        recs.append({"rule": r["rule"], "seed": r["seed"], "n_frames": len(kept), "said_kept": len(in_k), "says_kept": says_k, "yes_kept": yes_k,
                     "rate_kept": (yes_k / says_k if says_k else None), "says_not_kept": says_n, "yes_not_kept": yes_n, "rate_not_kept": (yes_n / says_n if says_n else None),
                     "kept_never_said": len(kept - said_pairs)})
    # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 21:40 +0400 — the law's §4 «each [distinct said frame] with its says and its yes-count»: the per-frame table (red-first: tests/tools/test_toys_frames_verdicts.py,
    # KeyError 'frames'), most says first, ties by the frame's text; `pair` is the two words as a list, None for a said text that is not two words.
    frames = [{"frame": text, "pair": (list(e["pair"]) if e["pair"] is not None else None), "says": e["says"], "yes": e["yes"]}
              for text, e in sorted(said.items(), key=lambda kv: (-kv[1]["says"], kv[0]))]
    return {"distinct_said": len(said), "says": total_says, "yes": total_yes, "base_rate": (total_yes / total_says if total_says else None), "frames": frames, "records": recs}


def jaccard(a: Iterable, b: Iterable) -> Optional[float]:
    A, B = set(a), set(b)
    if not A and not B:
        return None
    return len(A & B) / len(A | B)


def _sets(cond: Dict[str, object]) -> Dict[str, List[FrozenSet[Tuple[str, str]]]]:
    return {rule: [frozenset(tuple(f) for f in r["frames"]) for r in recs] for rule, recs in by_rule(cond).items()}


def overlaps(cond: Dict[str, object]) -> Dict[str, Optional[float]]:
    """Jaccard between the rules' kept sets; WEB-S's value is the mean over its seeds (seeds whose Jaccard is undefined are left out)."""
    s = _sets(cond)
    out: Dict[str, Optional[float]] = {}
    for a, b in (("WEB-H", "SENTENCE"), ("WEB-H", "MDL-GREEDY"), ("SENTENCE", "MDL-GREEDY")):
        if a in s and b in s:
            out[f"{a}|{b}"] = jaccard(s[a][0], s[b][0])
    for b in ("WEB-H", "SENTENCE", "MDL-GREEDY"):
        if "WEB-S" in s and b in s:
            js = [j for j in (jaccard(x, s[b][0]) for x in s["WEB-S"]) if j is not None]
            out[f"WEB-S|{b}"] = (sum(js) / len(js)) if js else None
    return out


def oracle_recall(cond: Dict[str, object], oracle: Iterable[Tuple[str, str]]) -> Dict[str, float]:
    O = frozenset(oracle)
    out: Dict[str, float] = {}
    for rule, sets in _sets(cond).items():
        rs = [len(x & O) / len(O) for x in sets]
        out[rule] = sum(rs) / len(rs)
    return out
