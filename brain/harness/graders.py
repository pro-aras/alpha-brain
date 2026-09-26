"""graders.py — THE GRADERS: pure functions of (tape, truth, one arm's record) → marks in the Bench grader's
shape (B1-PREREG.md §5, §8; docs/bench/BENCH-PLAN.md §4.7; docs/brain/b1/SEAT-DECISIONS.md R27).

edit: Claude (Fable 5.1), 2026-09-24 18:35 +0400 — the seat, alone.

Every mark is `{mark, graded, pass, reading, bar, ceiling, null, control: {name, caught}, reason_code, fields,
sources: [{file, rows}], class}` — with n, the denominator, k and the per-family breakdowns inside `fields`,
never blended (#170), and the null and the ceiling printed beside the bar (#228 (b)). A mark with no declared
bar is NOT GRADED (`reason_code: NO_BAR`) but still carries its reading — the seat's §12 line declares the
bars AFTER stage −1's ceilings exist (§3.4) and never after any graded answer exists; until then a run is a
smoke and its marks are readings only. The twins' readings (SHUFFLED-NAME, SHUFFLED-RELATION, FORCED-ANSWER,
SHUFFLED-CITATION, RING-READ) enter through `twins=` (their own records graded by these same functions) and
through `shuffled_citation_band` (a grader-side twin: why.jsonl's citations replaced by the same number of
random seqs, its 95 % band by 200 seeded draws — §4's twelfth twin).

The scoring law (§5.1) as code: the FIRST answer is the grade (the record holds exactly one answer per ask);
a relation family's unit is its NAME item — known iff right on a STRICT MAJORITY of its renderings, both
cases pooled (6 renderings under PREREG; 2 under the SMOKE params — the same rule); MIRROR / LOOP per held-out
FORM (majority of its renderings); VOWEL and U1 (a) per (form, font) item; U5 per letter item, refused in
BOTH cases; SILENT is never UNKNOWN.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from brain.protocol import AnswerKind
from brain.world.seeds import substream

REFUSE = "REFUSE"
REFUSAL_KINDS = (AnswerKind.UNKNOWN, AnswerKind.NOTHING)
U3_LETTER_FAMILIES = ("AFTER", "BEFORE", "BETWEEN", "TWO_AFTER", "OTHER_CASE", "CHAIN", "MIRROR", "LOOP", "VOWEL")
REACH_FAMILIES = ("AFTER", "BEFORE", "BETWEEN")
DISCRIMINATING_FAMILIES = ("TWO_AFTER", "OTHER_CASE", "CHAIN")
FAMILY_NULL = {"AFTER": 1 / 25, "BEFORE": 1 / 25, "BETWEEN": 1 / 25, "TWO_AFTER": 1 / 25, "OTHER_CASE": 1 / 26, "CHAIN": 1 / 26,
               "TRANSFER": 1 / 9, "MIRROR": 0.5, "LOOP": 0.5, "VOWEL": 0.5, "U1b_PICK": 0.25, "U2b_LURES": 0.5}
U5_KINDS = ("after_z", "before_a", "two_after_yz", "between_adjacent", "after_never_taught", "other_case_digit")
CANARY_NAMES_HEARD_BY_T_L = 27      # 26 letters + zog (§5.3 U6's own denominator for chance)
NO_RELATION_ROAD = ("A0", "RING-READ")   # §5.5 (0a): they answer no relation cue by design — (0a)/(0a′) NOT APPLICABLE (R38)


class GraderError(Exception):
    pass


# ================================================================================================ small statistics
def binom_tail(n: int, k: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return sum(math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(k, n + 1))


def k_min(n: int, p: float, alpha: float = 0.001) -> int:
    """§5.2's rule: the smallest k with P(X >= k) < alpha under the null."""
    for k in range(0, n + 1):
        if binom_tail(n, k, p) < alpha:
            return k
    return n + 1


def half_width_95(p: float, n: int) -> float:
    return 1.96 * math.sqrt(max(p * (1 - p), 1e-12) / max(n, 1))


# ================================================================================================ the record
def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not Path(path).exists():
        return []
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def load_record(arm_dir: Path) -> Dict[str, Any]:
    """One arm's run directory (R27) → the dict every grader reads. Never a partial read: a missing file is an
    empty list, named in `missing`."""
    arm_dir = Path(arm_dir)
    rec = {"dir": str(arm_dir), "answers": load_jsonl(arm_dir / "answers.jsonl"), "why": load_jsonl(arm_dir / "why.jsonl"),
           "rules": load_jsonl(arm_dir / "rules.jsonl"),
           "sittings": json.loads((arm_dir / "sittings.json").read_text()) if (arm_dir / "sittings.json").exists() else {},
           "summary": json.loads((arm_dir / "summary.json").read_text()) if (arm_dir / "summary.json").exists() else {},
           "missing": [n for n in ("answers.jsonl", "sittings.json", "summary.json") if not (arm_dir / n).exists()]}
    return rec


def _mark(name: str, *, reading: Any, graded: bool, passed: Optional[bool], bar: Any = None, ceiling: Any = None, null: Any = None,
          control: Optional[Dict[str, Any]] = None, reason_code: str = "", fields: Optional[Dict[str, Any]] = None,
          sources: Optional[List[Dict[str, Any]]] = None, klass: str = "") -> Dict[str, Any]:
    return {"mark": name, "graded": bool(graded), "pass": (bool(passed) if passed is not None else None), "reading": reading,
            "bar": bar, "ceiling": ceiling, "null": null, "control": control or {"name": None, "caught": None},
            "reason_code": reason_code, "fields": fields or {}, "sources": sources or [], "class": klass}


def _no_bar(name: str, reading: Any, **kw) -> Dict[str, Any]:
    return _mark(name, reading=reading, graded=False, passed=None, reason_code="NO_BAR", **kw)


def _by_sitting(answers: Sequence[Mapping[str, Any]], sitting: str, family: Optional[str] = None) -> List[Mapping[str, Any]]:
    return [a for a in answers if a.get("sitting") == sitting and (family is None or a.get("family") == family)]


# ================================================================================================ U1
def grade_u1a(answers, sitting: str = "T_L", bar: Optional[Mapping[str, float]] = None, ceiling: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """U1 (a): NAME on held-out fonts, per (letter, font) item, PER CASE (§5.3). `bar`/`ceiling` per case."""
    rows = _by_sitting(answers, sitting, "U1a_NAME")
    per_case: Dict[str, Dict[str, Any]] = {}
    for case in ("latin-upper", "latin-lower"):
        items = [a for a in rows if a["class"] == case]
        n = len(items)
        k = sum(1 for a in items if a["correct"])
        kinds = Counter(a["answer"]["kind"] for a in items)
        per_case[case] = {"n": n, "k": k, "share": (k / n if n else None), "answer_kinds": dict(kinds)}
    fields = {"per_case": per_case, "sitting": sitting}
    reading = {c: v["share"] for c, v in per_case.items()}
    if not bar:
        return _no_bar(f"U1a_NAME@{sitting}", reading, ceiling=ceiling, null=0.0, fields=fields, klass="U1")
    ok = all(per_case[c]["n"] > 0 and per_case[c]["share"] >= bar[c] for c in per_case if c in bar)
    return _mark(f"U1a_NAME@{sitting}", reading=reading, graded=True, passed=ok, bar=dict(bar), ceiling=ceiling, null=0.0, fields=fields, klass="U1")


def grade_u1b(answers, sitting: str = "T_L", bar: Optional[int] = None) -> Dict[str, Any]:
    rows = _by_sitting(answers, sitting, "U1b_PICK")
    n, k = len(rows), sum(1 for a in rows if a["correct"])
    kmin = k_min(n, FAMILY_NULL["U1b_PICK"]) if n else None
    fields = {"n": n, "k": k, "k_min": kmin, "answer_kinds": dict(Counter(a["answer"]["kind"] for a in rows))}
    if bar is None:
        return _no_bar(f"U1b_PICK@{sitting}", (k / n if n else None), null=FAMILY_NULL["U1b_PICK"], fields=fields, klass="U1")
    return _mark(f"U1b_PICK@{sitting}", reading=(k / n if n else None), graded=n > 0, passed=(k >= bar), bar=bar, null=FAMILY_NULL["U1b_PICK"],
                 fields=fields, klass="U1")


# ================================================================================================ U2
def grade_u2a(answers, sitting: str = "T_L", max_sure_names: int = 4, min_refusals: int = 32) -> Dict[str, Any]:
    """U2 (a): 40 never-taught signs — a bare sure NAME on <= 4 AND UNKNOWN/RESEMBLES on >= 32 (§5.3; the bar
    is the PREREG's own, scaled from the A1 NULL rung). FORCED-ANSWER must fail it (the twin's own mark)."""
    rows = _by_sitting(answers, sitting, "U2a_NEVER_TAUGHT")
    n = len(rows)
    kinds = Counter(a["answer"]["kind"] for a in rows)
    sure = kinds.get(AnswerKind.NAME, 0)
    refused = kinds.get(AnswerKind.UNKNOWN, 0) + kinds.get(AnswerKind.RESEMBLES, 0)
    scale = n / 40 if n else 1.0
    max_sure, min_ref = math.floor(max_sure_names * scale + 1e-9), math.ceil(min_refusals * scale - 1e-9)
    ok = n > 0 and sure <= max_sure and refused >= min_ref
    fields = {"n": n, "sure_names": sure, "refusals_unknown_or_resembles": refused, "nothing": kinds.get(AnswerKind.NOTHING, 0),
              "silent": kinds.get(AnswerKind.SILENT, 0), "bar": {"max_sure_names": max_sure, "min_refusals": min_ref}, "answer_kinds": dict(kinds)}
    return _mark(f"U2a_REFUSES@{sitting}", reading={"sure_names": sure, "refusals": refused}, graded=n > 0, passed=ok,
                 bar={"max_sure_names": max_sure, "min_refusals": min_ref}, null=None, fields=fields, klass="U2")


def grade_u2b(answers, sitting: str = "T_L", bar: Optional[int] = None) -> Dict[str, Any]:
    rows = _by_sitting(answers, sitting, "U2b_LURES")
    n, k = len(rows), sum(1 for a in rows if a["correct"])
    yes = sum(1 for a in rows if a["answer"]["kind"] == AnswerKind.YES)
    pos = [a for a in rows if a["class"].endswith("positive")]
    lure = [a for a in rows if a["class"].endswith("lure")]
    fields = {"n": n, "k": k, "echo_rate_yes": (yes / n if n else None), "positives": {"n": len(pos), "k": sum(1 for a in pos if a["correct"])},
              "lures": {"n": len(lure), "k": sum(1 for a in lure if a["correct"])}, "k_min": (k_min(n, 0.5) if n else None)}
    b = bar if bar is not None else (math.ceil(69 / 104 * n) if n else None)   # §5.3: 69 of 104, scaled
    return _mark(f"U2b_LURES@{sitting}", reading=(k / n if n else None), graded=n > 0, passed=(n > 0 and k >= b), bar=b, null=0.5, fields=fields, klass="U2")


# ================================================================================================ U3
def _item_key(a: Mapping[str, Any]) -> str:
    return a["item"]


def family_items(answers, family: str, sitting: str) -> Dict[str, Dict[str, Any]]:
    """The family's units at a sitting: item → {renderings, right, known, per_class}. VOWEL's unit is the
    (form, font) item — its `item` field already carries the font (schedule.py), so the same grouping holds."""
    rows = _by_sitting(answers, sitting, family)
    items: Dict[str, Dict[str, Any]] = {}
    for a in rows:
        it = items.setdefault(_item_key(a), {"renderings": 0, "right": 0, "per_class": defaultdict(lambda: [0, 0]), "kinds": Counter(), "extra": {}})
        it["renderings"] += 1
        it["right"] += 1 if a["correct"] else 0
        it["per_class"][a["class"]][0] += 1 if a["correct"] else 0
        it["per_class"][a["class"]][1] += 1
        it["kinds"][a["answer"]["kind"]] += 1
        for k in ("after_was",):
            if k in a:
                it["extra"][k] = a[k]
    for it in items.values():
        it["known"] = it["right"] * 2 > it["renderings"]        # a STRICT majority of its renderings (§5.1)
        it["per_class"] = {c: {"k": v[0], "n": v[1]} for c, v in it["per_class"].items()}
        it["kinds"] = dict(it["kinds"])
    return items


def grade_u3_family(answers, family: str, sitting: str = "T_L", bar: Optional[int] = None, ceiling: Optional[Mapping[str, Any]] = None,
                    twin_band: Optional[float] = None, truth_asks: Optional[Mapping[int, Any]] = None) -> Dict[str, Any]:
    """One U3 family: k known of n NAME items; pass iff k >= bar AND (if given) share > the SHUFFLED-RELATION
    twin's 95 % band. Breakdowns: per case / direction (never a second bar), CHAIN by after_was."""
    items = family_items(answers, family, sitting)
    n = len(items)
    k = sum(1 for it in items.values() if it["known"])
    null = FAMILY_NULL.get(family, 1 / 25)
    per_class: Dict[str, List[int]] = defaultdict(lambda: [0, 0])
    for it in items.values():
        for c, v in it["per_class"].items():
            per_class[c][0] += v["k"]
            per_class[c][1] += v["n"]
    breakdown = {c: {"right": v[0], "renderings": v[1]} for c, v in per_class.items()}
    extra: Dict[str, Any] = {}
    if family == "CHAIN":
        split = defaultdict(lambda: [0, 0])
        for it in items.values():
            w = it["extra"].get("after_was")
            if w is None and truth_asks is not None:
                w = "?"
            split[w or "?"][0] += 1 if it["known"] else 0
            split[w or "?"][1] += 1
        extra["by_after_was"] = {w: {"known": v[0], "n": v[1]} for w, v in split.items()}
    renderings = sum(it["renderings"] for it in items.values())
    fields = {"n": n, "k": k, "share": (k / n if n else None), "renderings": renderings, "k_min": (k_min(n, null) if n else None),
              "majority_rule": "strict majority of the item's renderings", "breakdown_by_class": breakdown, "twin_band_95": twin_band,
              "abstentions": sum(it["kinds"].get(AnswerKind.UNKNOWN, 0) + it["kinds"].get(AnswerKind.NOTHING, 0) for it in items.values()), **extra}
    name = f"U3_{family}@{sitting}"
    klass = "REACH" if family in REACH_FAMILIES else "U3"
    if n == 0:
        return _mark(name, reading=None, graded=False, passed=None, bar=bar, ceiling=ceiling, null=null, reason_code="NO_ITEMS", fields=fields, klass=klass)
    if bar is None:
        return _no_bar(name, k / n, ceiling=ceiling, null=null, fields=fields, klass=klass)
    ok = k >= bar and (twin_band is None or (k / n) > twin_band)
    return _mark(name, reading=k / n, graded=True, passed=ok, bar=bar, ceiling=ceiling, null=null,
                 control={"name": "SHUFFLED-RELATION band", "caught": (None if twin_band is None else (k / n) > twin_band)}, fields=fields, klass=klass)


def examples_to_bar(answers, bar: Optional[int], probes: Sequence[str] = ("P1", "P2", "P3", "P4"),
                    episodes_at: Sequence[int] = (6, 12, 18, 36)) -> Dict[str, Any]:
    """§5.2 TWO_AFTER's probe ladder: the first probe whose known count reaches the bar → its episode count;
    never → «> 36». The T_L reading is printed beside it."""
    ladder = []
    reached = None
    for p, e in zip(probes, episodes_at):
        items = family_items(answers, "TWO_AFTER", p)
        k = sum(1 for it in items.values() if it["known"])
        ladder.append({"probe": p, "episodes": e, "n": len(items), "known": k})
        if reached is None and bar is not None and len(items) and k >= bar:
            reached = e
    reading = reached if reached is not None else (f"> {episodes_at[-1]}" if bar is not None else None)
    return _mark("EXAMPLES_TO_BAR_TWO_AFTER", reading=reading, graded=False, passed=None, bar=bar, reason_code=("NO_BAR" if bar is None else "DIAGNOSTIC"),
                 fields={"ladder": ladder}, klass="U3")


# ================================================================================================ U4
def grade_u4a(record: Mapping[str, Any], tape_rows: Sequence[Mapping[str, Any]], bar: Optional[float] = None, seed: int = 0,
              n_draws: int = 200) -> Dict[str, Any]:
    """U4a: per letter asked, cited-and-true iff >= 1 cited seq is a TEACH row EARLIER than the ask whose name is
    the answer. n < 13 → NOT GRADABLE. SHUFFLED-CITATION's band: the same number of seqs drawn at random
    (seeded) from the seqs before the ask, 200 draws, the 95th percentile of the share."""
    why = record.get("why") or []
    if any(w.get("no_road") for w in why) or not why:
        return _mark("U4a_EXPLAINS_EXPERIENCE", reading=None, graded=False, passed=None, bar=bar, reason_code=("NO_ROAD" if why else "NO_WHY_FILE"), klass="U4")
    teach_name_by_seq = {r["seq"]: r["payload"]["name"] for r in tape_rows if r["kind"] == "TEACH"}
    n = len(why)
    hits = 0
    per = []
    for w in why:
        ok = any((s in teach_name_by_seq) and (s < w["seq"]) and (teach_name_by_seq[s] == w["letter"]) for s in w.get("cited", []))
        hits += 1 if ok else 0
        per.append({"letter": w["letter"], "seq": w["seq"], "n_cited": w.get("n_cited", len(w.get("cited", []))), "cited_and_true": ok, "error": w.get("error")})
    share = hits / n
    rng = substream(seed, "twin:shuffled-citation")
    shares = []
    for _ in range(n_draws):
        h = 0
        for w in why:
            m = int(w.get("n_cited", len(w.get("cited", []))))
            if m <= 0 or w["seq"] <= 1:
                continue
            draw = rng.integers(1, w["seq"], size=m)
            if any((int(s) in teach_name_by_seq) and teach_name_by_seq[int(s)] == w["letter"] for s in draw):
                h += 1
        shares.append(h / n)
    shares.sort()
    band = shares[min(len(shares) - 1, int(0.95 * len(shares)))] if shares else None
    fields = {"n": n, "cited_and_true": hits, "share": share, "per_letter": per, "shuffled_citation_band_95": band, "draws": n_draws}
    if n < 13:
        return _mark("U4a_EXPLAINS_EXPERIENCE", reading=share, graded=False, passed=None, bar=bar, reason_code="NOT_GRADABLE_N_LT_13", fields=fields, klass="U4")
    if bar is None:
        return _no_bar("U4a_EXPLAINS_EXPERIENCE", share, fields=fields, klass="U4")
    ok = share >= bar and (band is None or share > band)
    return _mark("U4a_EXPLAINS_EXPERIENCE", reading=share, graded=True, passed=ok, bar=bar, control={"name": "SHUFFLED-CITATION band", "caught": (share > band if band is not None else None)},
                 fields=fields, klass="U4")


def grade_u4b(record: Mapping[str, Any], truth_asks: Mapping[int, Mapping[str, Any]], bars: Optional[Mapping[str, int]] = None,
              within_pp: float = 5.0) -> Dict[str, Any]:
    """U4b: per U3 family, the rule's accuracy on the family's T_L items >= the family's bar (as a share of items
    known, the same unit) AND within 5 pp of the arm's own U3 answers on the same items."""
    rules = record.get("rules") or []
    if not rules or any(r.get("no_road") for r in rules):
        return _mark("U4b_EXPLAINS_RULE", reading=None, graded=False, passed=None, reason_code=("NO_ROAD" if rules else "NO_RULES_FILE"), klass="U4")
    answers = record["answers"]
    per_family = {}
    all_ok, any_graded = True, False
    for r in rules:
        fam = r["family"]
        if r.get("no_rule") or r.get("error"):
            per_family[fam] = {"no_rule": True, "text": r.get("text"), "error": r.get("error")}
            all_ok = False
            continue
        own = family_items(answers, fam, "T_L")
        # the rule's answers, graded item by item exactly as the arm's own
        rule_rows = []
        for a in r["answers"]:
            t = truth_asks.get(int(a["seq"]))
            if t is None:
                continue
            kind = t["answer_kind"]
            if a["kind"] in REFUSAL_KINDS or a["kind"] == AnswerKind.SILENT:
                correct = (t["answer"] == REFUSE)
            elif kind == "NAME":
                correct = a["kind"] == AnswerKind.NAME and a["value"] == t["answer"]
            elif kind == "PICK":
                correct = a["kind"] == AnswerKind.PICK and a["value"] == t["answer"]
            else:
                correct = a["kind"] == t["answer"]
            rule_rows.append({"item": t["item"], "class": t["class"], "correct": correct, "answer": {"kind": a["kind"]}, "sitting": "T_L", "family": fam})
        rule_items = family_items(rule_rows, fam, "T_L")
        n = len(rule_items)
        k_rule = sum(1 for it in rule_items.values() if it["known"])
        k_own = sum(1 for it in own.values() if it["known"])
        agree = sum(1 for key, it in rule_items.items() if key in own and own[key]["known"] == it["known"])
        bar = (bars or {}).get(fam)
        ok = None
        if n and bar is not None:
            any_graded = True
            ok = (k_rule >= bar) and (abs(k_rule - k_own) / n * 100.0 <= within_pp)
            all_ok = all_ok and ok
        per_family[fam] = {"n": n, "rule_known": k_rule, "own_known": k_own, "items_agree": agree, "bar": bar, "pass": ok, "text": r.get("text")}
    if not any_graded:
        return _mark("U4b_EXPLAINS_RULE", reading={f: v.get("rule_known") for f, v in per_family.items()}, graded=False, passed=None,
                     reason_code="NO_BAR", fields={"per_family": per_family, "within_pp": within_pp}, klass="U4")
    return _mark("U4b_EXPLAINS_RULE", reading={f: v.get("rule_known") for f, v in per_family.items()}, graded=True, passed=all_ok,
                 bar=dict(bars or {}), fields={"per_family": per_family, "within_pp": within_pp}, klass="U4")


# ================================================================================================ U5 / U6
def grade_u5(answers, bar: Optional[float] = None) -> Dict[str, Any]:
    """U5: per letter item, refused in BOTH cases; pooled share >= bar AND no kind at 0 of its items; each kind
    printed. Items with one ask (never-taught signs, digits) are one-ask items."""
    rows = [a for a in answers if a.get("family") == "U5" and a.get("sitting") in ("T_L", "T_D")]
    items: Dict[Tuple[str, str], List[bool]] = defaultdict(list)
    for a in rows:
        items[(a["class"], a["item"])].append(a["answer"]["kind"] in REFUSAL_KINDS)
    per_kind = {}
    total, refused = 0, 0
    for kind in U5_KINDS:
        ks = {k: v for k, v in items.items() if k[0] == kind}
        n = len(ks)
        r = sum(1 for v in ks.values() if all(v))
        per_kind[kind] = {"n": n, "refused": r}
        total += n
        refused += r
    share = refused / total if total else None
    zero_kind = [k for k, v in per_kind.items() if v["n"] and v["refused"] == 0]
    fields = {"n": total, "refused": refused, "share": share, "per_kind": per_kind, "kinds_at_zero": zero_kind}
    if bar is None:
        return _no_bar("U5_REJECTS_MISUSE", share, fields=fields, klass="U5")
    ok = total > 0 and share >= bar and not zero_kind
    return _mark("U5_REJECTS_MISUSE", reading=share, graded=total > 0, passed=ok, bar=bar, fields=fields, klass="U5")


def grade_u6(answers, bar_k: Optional[int] = None, ceiling: Optional[float] = None) -> Dict[str, Any]:
    plant = _by_sitting(answers, "T_L", "U6_PLANT")
    ref = _by_sitting(answers, "T_L", "U6_REFUSAL")
    n = len(plant)
    named = sum(1 for a in plant if a["answer"]["kind"] == AnswerKind.NAME and a["answer"]["value"] == "zog")
    false_zog = sum(1 for a in ref if a["answer"]["kind"] == AnswerKind.NAME and a["answer"]["value"] == "zog")
    kmin = k_min(n, 1 / CANARY_NAMES_HEARD_BY_T_L) if n else None
    fields = {"n": n, "named_zog": named, "k_min": kmin, "refusal_signs": len(ref), "false_zog_on_refusal_signs": false_zog,
              "plant_answer_kinds": dict(Counter(a["answer"]["kind"] for a in plant))}
    b = bar_k if bar_k is not None else kmin
    if n == 0:
        return _mark("U6_ONE_MEETING", reading=None, graded=False, passed=None, reason_code="NO_ITEMS", fields=fields, klass="U6")
    if bar_k is None:
        return _no_bar("U6_ONE_MEETING", named / n, ceiling=ceiling, null=1 / CANARY_NAMES_HEARD_BY_T_L, fields=fields, klass="U6")
    ok = named >= b and false_zog <= 1
    return _mark("U6_ONE_MEETING", reading=named / n, graded=True, passed=ok, bar=b, ceiling=ceiling, null=1 / CANARY_NAMES_HEARD_BY_T_L, fields=fields, klass="U6")


# ================================================================================================ KEEPS · COST · TRANSFER
def grade_keeps(answers, max_drop_pp: float = 5.0) -> Dict[str, Any]:
    """§5.4 KEEPS: U1 (a) and every letter U3 family re-asked at T_D — each drop <= 5 pp."""
    per = {}
    ok_all = True
    for case in ("latin-upper", "latin-lower"):
        tl = [a for a in _by_sitting(answers, "T_L", "U1a_NAME") if a["class"] == case]
        td = [a for a in _by_sitting(answers, "T_D", "U1a_NAME") if a["class"] == case]
        if tl and td:
            s1, s2 = sum(a["correct"] for a in tl) / len(tl), sum(a["correct"] for a in td) / len(td)
            drop = (s1 - s2) * 100.0
            per[f"U1a_NAME:{case}"] = {"T_L": s1, "T_D": s2, "drop_pp": drop, "ok": drop <= max_drop_pp}
            ok_all = ok_all and drop <= max_drop_pp
    for fam in U3_LETTER_FAMILIES:
        i1, i2 = family_items(answers, fam, "T_L"), family_items(answers, fam, "T_D")
        if i1 and i2:
            s1 = sum(1 for it in i1.values() if it["known"]) / len(i1)
            s2 = sum(1 for it in i2.values() if it["known"]) / len(i2)
            drop = (s1 - s2) * 100.0
            per[fam] = {"T_L": s1, "T_D": s2, "drop_pp": drop, "ok": drop <= max_drop_pp}
            ok_all = ok_all and drop <= max_drop_pp
    return _mark("KEEPS", reading={k: v["drop_pp"] for k, v in per.items()}, graded=bool(per), passed=(ok_all if per else None), bar=max_drop_pp,
                 reason_code=("" if per else "NO_T_D"), fields={"per_family": per, "max_drop_pp": max_drop_pp}, klass="KEEPS")


def grade_cost(record: Mapping[str, Any], bound_ms_per_event: Optional[float] = None) -> Dict[str, Any]:
    c = (record.get("summary") or {}).get("cost") or {}
    ms = c.get("ms_per_event")
    size = (record.get("summary") or {}).get("size")
    fields = {"ms_per_event": ms, "arm_events": c.get("arm_events"), "arm_ms": c.get("arm_ms"), "size": size}
    if ms is None:
        return _mark("COST", reading=None, graded=False, passed=None, reason_code="NO_COST", fields=fields, klass="COST")
    if bound_ms_per_event is None:
        return _no_bar("COST", ms, fields=fields, klass="COST")
    return _mark("COST", reading=ms, graded=True, passed=ms <= bound_ms_per_event, bar=bound_ms_per_event, fields=fields, klass="COST")


# ================================================================================================ the controls
def grade_controls(record: Mapping[str, Any], tape_counts: Optional[Mapping[str, Any]] = None, seed: int = 0) -> Dict[str, Dict[str, Any]]:
    answers = record["answers"]
    out: Dict[str, Dict[str, Any]] = {}
    # (0a) CONST — 100 %
    const = _by_sitting(answers, "T_L", "CONTROL_CONST")
    n, k = len(const), sum(1 for a in const if a["correct"])
    out["C0a_CONST"] = _mark("C0a_CONST", reading=(k / n if n else None), graded=n > 0, passed=(n > 0 and k == n), bar=1.0,
                             fields={"n": n, "k": k, "answer_kinds": dict(Counter(a["answer"]["kind"] for a in const))}, klass="CONTROL")
    # (0a′) SAME — equal to the arm's own NAME answer on the same rendering on >= 19 of 20 (scaled)
    same = {a["item"].split(":", 1)[1]: a for a in _by_sitting(answers, "T_L", "CONTROL_SAME")}
    ref = {a["item"].split(":", 1)[1].replace(":same-ref", ""): a for a in _by_sitting(answers, "T_L", "SAME_NAME_REF")}
    pairs = [(same[k], ref[k]) for k in same if k in ref]
    n = len(pairs)
    eq = sum(1 for s, r in pairs if s["answer"]["kind"] == r["answer"]["kind"] and s["answer"]["value"] == r["answer"]["value"])
    need = math.ceil(19 / 20 * n) if n else None
    out["C0a_SAME"] = _mark("C0a_SAME", reading=(eq / n if n else None), graded=n > 0, passed=(n > 0 and eq >= need), bar=(need / n if n else None),
                            fields={"n": n, "equal_to_own_name": eq, "need": need,
                                    "same_answer_kinds": dict(Counter(s["answer"]["kind"] for s, _ in pairs))}, klass="CONTROL")
    # edit: Claude (Opus 5.5), 2026-09-26 17:33 +0400 — PREREG §5.5 (0a): «A0 and RING-READ answer no relation cue by design
    # — for them (0a)/(0a′) read NOT APPLICABLE, named.» Both were graded for every arm, so A0, its twins and RING-READ read
    # FAILED controls on both seeds (SEAT-DECISIONS R38). The reading stays on the record; the mark is not graded.
    base = str((record.get("summary") or {}).get("arm") or "").split(":", 1)[-1]
    if base in NO_RELATION_ROAD:
        for key in ("C0a_CONST", "C0a_SAME"):
            m = out[key]
            out[key] = _mark(key, reading=m["reading"], graded=False, passed=None, bar=m["bar"], reason_code="NOT_APPLICABLE",
                             fields=dict(m["fields"], why=f"{base} answers no relation cue by design (PREREG §5.5 (0a))"), klass="CONTROL")
    # (0d) CANARY — at chance: pass iff correct <= the smallest k with P(X >= k) < 0.001 under 1/27 (above → a LEAK)
    can = _by_sitting(answers, "T_L", "CONTROL_CANARY")
    n, k = len(can), sum(1 for a in can if a["correct"])
    kmax = k_min(n, 1 / CANARY_NAMES_HEARD_BY_T_L) - 1 if n else None
    out["C0d_CANARY"] = _mark("C0d_CANARY", reading=(k / n if n else None), graded=n > 0, passed=(n > 0 and k <= kmax), bar=(f"<= {kmax} of {n}" if n else None),
                              null=1 / CANARY_NAMES_HEARD_BY_T_L, fields={"n": n, "k": k, "k_leak": (kmax + 1 if kmax is not None else None)}, klass="CONTROL")
    # (0e) FROZEN — from sittings.json
    sit = record.get("sittings") or {}
    void = {s: v for s, v in sit.items() if v.get("void")}
    out["C0e_FROZEN"] = _mark("C0e_FROZEN", reading=(len(void) == 0), graded=bool(sit), passed=(bool(sit) and not void), bar="state_sha before = after every sitting",
                              fields={"sittings": list(sit), "void": {s: v.get("reasons") for s, v in void.items()}}, klass="CONTROL")
    # (0f)/(0g) — the tape's own build-time controls, passed through when counts.json is given
    if tape_counts:
        ctl = tape_counts.get("controls", {})
        d, l = ctl.get("disjoint", {}), ctl.get("mlc_leak", {})
        out["C0f_DISJOINT"] = _mark("C0f_DISJOINT", reading=d.get("pass"), graded="pass" in d, passed=d.get("pass"), fields=d, klass="CONTROL")
        out["C0g_MLC_LEAK"] = _mark("C0g_MLC_LEAK", reading=l.get("pass"), graded="pass" in l, passed=l.get("pass"), fields=l, klass="CONTROL")
    return out


# ================================================================================================ one arm, all marks
def grade_arm(record: Mapping[str, Any], truth_asks: Mapping[int, Mapping[str, Any]], tape_rows: Sequence[Mapping[str, Any]],
              bars: Optional[Mapping[str, Any]] = None, ceilings: Optional[Mapping[str, Any]] = None, twin_bands: Optional[Mapping[str, float]] = None,
              tape_counts: Optional[Mapping[str, Any]] = None, seed: int = 0) -> Dict[str, Any]:
    """Every mark of §5 for ONE arm's record. `bars` (the seat's §12 line, parsed) keys: U1a {case: share},
    U1b (k), U2b (k), U3 {family: k}, TRANSFER (k), U4a (share), U5 (share), U6 (k), COST (ms/event), KEEPS (pp).
    `twin_bands` {family: the SHUFFLED-RELATION twin's 95 % band} when its record exists."""
    bars = bars or {}
    answers = record["answers"]
    cf = (ceilings or {}).get("families", {}) if ceilings else {}

    def ceil_of(name: str):
        e = cf.get(name)
        return (e or {}).get("organ_ceiling", {}).get("max") if e else None

    marks: Dict[str, Any] = {}
    marks.update(grade_controls(record, tape_counts, seed))
    marks["U1a_NAME@T_L"] = grade_u1a(answers, "T_L", bars.get("U1a"), {c: ceil_of(f"NAMING_{c}_4fonts") for c in ("latin-upper", "latin-lower")})
    marks["U1b_PICK@T_L"] = grade_u1b(answers, "T_L", bars.get("U1b"))
    marks["U2a_REFUSES@T_L"] = grade_u2a(answers, "T_L")
    marks["U2b_LURES@T_L"] = grade_u2b(answers, "T_L", bars.get("U2b"))
    u3bars = bars.get("U3", {}) or {}
    for fam in U3_LETTER_FAMILIES:
        marks[f"U3_{fam}@T_L"] = grade_u3_family(answers, fam, "T_L", u3bars.get(fam), ceil_of(fam), (twin_bands or {}).get(fam), truth_asks)
    marks["U3_TRANSFER@T_D"] = grade_u3_family(answers, "TRANSFER", "T_D", bars.get("TRANSFER"), None, (twin_bands or {}).get("TRANSFER"), truth_asks)
    marks["EXAMPLES_TO_BAR_TWO_AFTER"] = examples_to_bar(answers, u3bars.get("TWO_AFTER"))
    marks["U4a_EXPLAINS_EXPERIENCE"] = grade_u4a(record, tape_rows, bars.get("U4a"), seed)
    marks["U4b_EXPLAINS_RULE"] = grade_u4b(record, truth_asks, u3bars or None)
    marks["U5_REJECTS_MISUSE"] = grade_u5(answers, bars.get("U5"))
    marks["U6_ONE_MEETING"] = grade_u6(answers, bars.get("U6"), ceil_of("PLANT"))
    marks["KEEPS"] = grade_keeps(answers, float(bars.get("KEEPS", 5.0)))
    marks["COST"] = grade_cost(record, bars.get("COST"))
    return marks


def partition(marks: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    """`tools/verdict_g4.py:partition_marks`'s rule, on this shape: failed · not gradable (never counted as
    failed) · missing-graded (judged by its pass)."""
    failed, not_gradable, missing = [], [], []
    for name, m in marks.items():
        if "graded" not in m:
            missing.append(name)
            if not m.get("pass"):
                failed.append(name)
        elif m["graded"]:
            if not m.get("pass"):
                failed.append(name)
        else:
            not_gradable.append([name, str(m.get("reason_code") or "")])
    return {"failed": failed, "not_gradable": not_gradable, "missing_graded": missing}
