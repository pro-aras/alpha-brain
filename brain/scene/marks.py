"""marks.py — S1a's marks, the grading hygiene, the bars, and stage −1's organ facts (PREREG-R3-TONIGHT §S1a «Stage −1»,
«The marks», «Bars»). This module READS THE TRUTH (it grades); no learner module imports it.

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:15 +0400 — new module. Declared readings of what the PREREG leaves open (each is
listed in docs/brain/r3/S1A-HANDBACK.md; those that can move a bar are RAISED there):
  · QUESTIONS vs KEYS: an item's question (scene row + phrase) is what an arm hears; its key (target, types) stays here.
  · M1 items: ONE per regular test scene — the parent's own rule (a thing uniformly, a template uniformly) conditioned on
    the phrase being true of EXACTLY one thing in view (≡ uniform over the (thing, template) pairs that are); a scene
    with none gives no item. M1 is graded as FORCED pointing; «none» on an M1 item is printed as the false refusal.
  · M2a items: ONE per regular test scene — an allowed (non-held-out) colour × shape true of nothing in view, uniform,
    said as «⟨colour⟩ ⟨shape⟩».
  · M2b: the 56 m2b scenes (48 graded + 8 diamond, read apart); M6: the 42 m6 scenes. Both EXTRA to the 400.
  · «per word type» for a pointing item = the phrase's NECESSARY types: a word whose removal leaves the phrase true of
    ≥ 2 things in view. For M2a: a word whose removal makes the phrase true of some thing. Items with none → «none»
    (every one-thing M1 item). Per template printed beside.
  · a hypothesis's thing (grading) = the strict plurality of its fixations' things; a tie or no on-thing fixation → no
    thing (pointing to it is wrong for every target). A thing's hypothesis (the oracles' referent) = the hypothesis
    with the most fixations on it (a tie → the nearest mean position to the thing's centroid, in cells).
  · COVERED = the target has ≥ 1 fixation. M1 and M6's bars read COVERED items (the learner); ALL is printed beside.

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:05 +0400 — AMENDMENT 2 (PREREG-R3-TONIGHT-AMEND-2.md, genome-wt-brain3 d54e6c0): §2 M1
is graded on the 2- and 3-thing items (the «graded» block; the one-thing items a sanity reading); §3 meeting_seen(); §4 an
unheard word makes an item NOT GRADABLE (excluded, counted as n_unheard), never 0.0.
edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:17 +0400 — after the full run: a mark with n < 30 at a seed READS UNDERPOWERED
(the signed PREREG); M2a's CEILING-BOUND read per half (the learner's failing half must be one the oracle fails
too — declared, RAISED); the report's «all seeds» counts a seed only where the mark reads PASS.
"""
from __future__ import annotations

import collections
import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from brain.world.seeds import substream

from . import world as W

# ------------------------------------------------------------------------------------------------ the PREREG's numbers
PROBE_ALL144 = {"shape": 0.797, "colour": 0.933, "size": 0.867}               # seat_scene_probe.out, all 144
PROBE_SUBSET = {"shape": ("tower 112", 0.903), "colour": ("colour 32", 0.925), "size": ("tower 112", 0.875)}
VERDICT_FRACTION = 0.90
BARS = {"M1_vs_PORACLE_RW": 0.90, "M1_vs_PORACLE": 0.80, "M2a_refusal": 0.80, "M2a_false_refusal": 0.10,
        "M2b": 0.80, "M6": 0.70, "NSHUF_over_chance": 0.05}
UNDERPOWERED_N = 30
TOY_BAR = 0.90
T1_REFUTE = 0.6
M6_REFUTE = 0.5


def verdict_thresholds() -> Dict[str, float]:
    """The instrument verdict's thresholds, 0.90 × the probe's all-144 readings, computed — never typed."""
    return {k: VERDICT_FRACTION * v for k, v in PROBE_ALL144.items()}


# ------------------------------------------------------------------------------------------------ things and hypotheses
def things_of(truth_row: Dict[str, object]) -> List[W.Thing]:
    return [W.Thing(t["shape"], t["colour"], t["size"], int(t["top"]), int(t["left"])) for t in truth_row["things"]]


def hyp_counts(members: Sequence[Sequence[int]], fix_thing: Sequence[Optional[int]]) -> List[collections.Counter]:
    return [collections.Counter(fix_thing[m] for m in mem if fix_thing[m] is not None) for mem in members]


def hyp_label(c: collections.Counter) -> Optional[int]:
    if not c:
        return None
    top = c.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return None
    return int(top[0][0])


def covered(thing: int, fix_thing: Sequence[Optional[int]]) -> bool:
    return any(t == thing for t in fix_thing)


def thing_hypothesis(thing: int, members: Sequence[Sequence[int]], pos: Sequence[Tuple[float, float]],
                     fix_thing: Sequence[Optional[int]], centroid_px: Tuple[float, float]) -> Optional[int]:
    """The hypothesis «for» a thing: the most fixations on it; a tie → the nearest mean position to the thing's centroid
    (cells); None when the thing has no fixation."""
    counts = [sum(1 for m in mem if fix_thing[m] == thing) for mem in members]
    if not counts or max(counts) == 0:
        return None
    best = [i for i, c in enumerate(counts) if c == max(counts)]
    if len(best) == 1:
        return best[0]
    cy, cx = centroid_px[0] / 8.0 - 0.5, centroid_px[1] / 8.0 - 0.5
    return min(best, key=lambda i: ((pos[i][0] - cy) ** 2 + (pos[i][1] - cx) ** 2, i))


# ------------------------------------------------------------------------------------------------ items
def necessary_types(phrase: Sequence[str], things: Sequence[W.Thing]) -> Tuple[str, ...]:
    out = []
    for w in phrase:
        rest = [x for x in phrase if x != w]
        if sum(W.phrase_true_of(rest, t) for t in things) >= 2:
            out.append(W.word_type(w))
    return tuple(sorted(set(out)))


def absent_types(phrase: Sequence[str], things: Sequence[W.Thing]) -> Tuple[str, ...]:
    out = []
    for w in phrase:
        rest = [x for x in phrase if x != w]
        if any(W.phrase_true_of(rest, t) for t in things):
            out.append(W.word_type(w))
    return tuple(sorted(set(out)))


def m1_items(truth: Sequence[Dict[str, object]], seed: int, mark: str = "M1") -> List[Dict[str, object]]:
    items = []
    for row in truth:
        things = things_of(row)
        cands = [(k, tpl) for k, t in enumerate(things) for tpl in W.TEMPLATES
                 if sum(W.phrase_true_of(W.template_words(tpl, t), u) for u in things) == 1]
        if not cands:
            continue
        rng = substream(seed, f"{mark.lower()}-item:{row['item_id']}")
        k, tpl = cands[int(rng.integers(len(cands)))]
        phrase = W.template_words(tpl, things[k])
        items.append({"item_id": f"{mark}:{row['item_id']}", "mark": mark, "row": int(row["row"]), "phrase": list(phrase),
                      "target": k, "template": tpl, "types": list(necessary_types(phrase, things)),
                      "n_things": len(things)})
    return items


def m2a_items(truth: Sequence[Dict[str, object]], seed: int) -> List[Dict[str, object]]:
    items = []
    for row in truth:
        things = things_of(row)
        cands = [(s, c) for s, c in W.ALLOWED if not any(t.shape == s and t.colour == c for t in things)]
        rng = substream(seed, f"m2a-item:{row['item_id']}")
        s, c = cands[int(rng.integers(len(cands)))]
        phrase = (c, s)
        assert not any(W.phrase_true_of(phrase, t) for t in things)
        items.append({"item_id": f"M2a:{row['item_id']}", "mark": "M2a", "row": int(row["row"]), "phrase": list(phrase),
                      "target": None, "types": list(absent_types(phrase, things)), "n_things": len(things)})
    return items


def m2b_items(truth: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    items = []
    for row in truth:
        t = row["things"][0]
        items.append({"item_id": f"M2b:{row['item_id']}", "mark": "M2b", "row": int(row["row"]), "phrase": [],
                      "target": 0, "shape": t["shape"], "colour": t["colour"], "size": t["size"],
                      "graded": t["shape"] in W.M2B_SHAPES, "n_things": 1})
    return items


def m6_items(truth: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    return [{"item_id": f"M6:{row['item_id']}", "mark": "M6", "row": int(row["row"]), "phrase": [W.DAX_WORD],
             "target": int(row["referent"]), "n_things": len(row["things"])} for row in truth]


def question(item: Dict[str, object]) -> Dict[str, object]:
    """What an arm is asked: never the target or the types."""
    return {"item_id": item["item_id"], "mark": item["mark"], "row": item["row"], "phrase": list(item["phrase"])}


def tie_rng(seed: int, item_id: str) -> np.random.Generator:
    """The item's own tie-break generator (declared: a named substream of the split's seed) — the same in every arm."""
    return substream(seed, f"tie:{item_id}")


# ------------------------------------------------------------------------------------------------ grading
def _rate(xs: Iterable[bool]) -> Tuple[Optional[float], int]:
    xs = list(xs)
    return (sum(xs) / len(xs) if xs else None), len(xs)


def grade_pointing(items: Sequence[Dict[str, object]], answers: Dict[str, Dict[str, object]],
                   truth: Sequence[Dict[str, object]], members_of, arm_kind: str) -> List[Dict[str, object]]:
    """Per item: covered, correct (forced pointing), none, chance. `members_of(row)` → (members, pos) of the scene's
    hypotheses (gaze arms). arm_kind 'gaze' (hypotheses) or 'truth' (ORACLE-TRUTH: one thing per true thing)."""
    out = []
    for it in items:
        row = truth[it["row"]]
        ft = row["fix_thing"]
        a = answers.get(it["item_id"])
        cov = covered(it["target"], ft)
        if arm_kind == "truth":
            n_opts = len(row["things"])
            corr = a is not None and a.get("point") is not None and int(a["point"]) == it["target"]
        else:
            members, _pos = members_of(it["row"])
            n_opts = len(members)
            lab = None
            if a is not None and a.get("point") is not None:
                lab = hyp_label(hyp_counts(members, ft)[int(a["point"])])
            corr = lab is not None and lab == it["target"]
        # AMENDMENT 2 §4: an item whose phrase holds a word the arm never heard is NOT GRADABLE — excluded from every
        # rate and counted apart as n_unheard, never scored 0.0
        gradable = not bool((a or {}).get("unheard"))
        row_out = {"item_id": it["item_id"], "covered": cov, "correct": bool(corr), "gradable": gradable,
                   "none": (None if a is None else a.get("none")), "answered": a is not None and a.get("point") is not None,
                   "chance": 1.0 / max(1, n_opts), "n_things": it["n_things"], "types": it.get("types", []),
                   "template": it.get("template")}
        for key in ("none_i", "none_ii"):          # PREREG-S1B1 §3: the readings, carried when the arm answered them
            if a is not None and key in a:
                row_out[key] = a.get(key)
        out.append(row_out)
    return out


def _pointing_block(rows):
    """One block of a pointing grade (S1a's rates, lifted to module level for M3 — edit: Claude (Opus 5.5, S1b-1 builder),
    2026-09-28 13:48 +0400 — byte-for-byte the same arithmetic)."""
    un = sum(1 for r in rows if not r["gradable"])
    rows = [r for r in rows if r["gradable"]]
    cov = [r for r in rows if r["covered"]]
    acc_c, n_c = _rate(r["correct"] for r in cov)
    acc_a, n_a = _rate(r["correct"] for r in rows)
    ch_c = float(np.mean([r["chance"] for r in cov])) if cov else None
    ch_a = float(np.mean([r["chance"] for r in rows])) if rows else None
    fr, n_fr = _rate(bool(r["none"]) for r in cov if r["none"] is not None)
    out = {"covered": acc_c, "n_covered": n_c, "all": acc_a, "n_all": n_a, "coverage": (n_c / n_a if n_a else None),
           "chance_covered": ch_c, "chance_all": ch_a, "false_refusal": fr, "n_fr": n_fr, "n_unheard": un}
    for key in ("none_i", "none_ii"):                # PREREG-S1B1 §3: the readings' false refusal, from the same answers
        if any(key in r for r in cov):
            v, n = _rate(bool(r[key]) for r in cov if r.get(key) is not None)
            out[f"false_refusal_{key[5:]}"] = v
    return out


def summarise_pointing(g: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """Blocks of the pointing grade. AMENDMENT 2 §2: «graded» = the 2- and 3-thing items (the bars read it); «size1» is
    the one-thing sanity reading; the per-type and per-template rows are over the graded items (declared). Every rate
    counts GRADABLE items only (§4); a block with none reads None, with n_unheard beside it."""
    block = _pointing_block
    graded = [r for r in g if r["n_things"] >= 2]
    res = {"all": block(g), "graded": block(graded)}
    for n in (1, 2, 3):
        res[f"size{n}"] = block([r for r in g if r["n_things"] == n])
    for t in W.WORD_TYPES:
        res[f"type:{t}"] = block([r for r in graded if t in r["types"]])
    res["type:none"] = block([r for r in graded if not r["types"]])
    for tpl in W.TEMPLATES:
        rows = [r for r in graded if r["template"] == tpl]
        if rows:
            res[f"tpl:{tpl}"] = block(rows)
    return res


def m2a_verdict(refusal: Optional[float], false_refusal: Optional[float], po_refusal: Optional[float],
                po_false_refusal: Optional[float]) -> Dict[str, object]:
    """M2a's bar is CONJUNCTIVE (refusal ≥ 0.80 AND false refusal ≤ 0.10). Declared reading (RAISED), after the full run:
    CEILING-BOUND is read PER HALF — the bar reads CEILING-BOUND only when every half the learner fails is a half P-ORACLE
    fails too; a half the oracle reaches is the learner's own FAIL (#170: a blend hides which half failed). The whole-bar
    reading (P-ORACLE fails the conjunction) is returned beside, as `whole_bar_ceiling`."""
    ok = lambda v, lo=None, hi=None: v is not None and (lo is None or v >= lo) and (hi is None or v <= hi)
    halves = {"refusal": (ok(refusal, lo=BARS["M2a_refusal"]), ok(po_refusal, lo=BARS["M2a_refusal"])),
              "false_refusal": (ok(false_refusal, hi=BARS["M2a_false_refusal"]), ok(po_false_refusal, hi=BARS["M2a_false_refusal"]))}
    failing = [h for h, (mine, _po) in halves.items() if not mine]
    return {"pass": not failing, "failing_halves": failing,
            "ceiling_bound": bool(failing) and all(not halves[h][1] for h in failing),
            "whole_bar_ceiling": not (halves["refusal"][1] and halves["false_refusal"][1]),
            "halves": {h: {"learner": a, "p_oracle": b} for h, (a, b) in halves.items()}}


def meeting_seen(dax_row: Dict[str, object]) -> bool:
    """AMENDMENT 2 §3: the one meeting reached the learner iff the dax (the dax scene's referent) got ≥ 1 fixation."""
    return covered(int(dax_row["referent"]), dax_row["fix_thing"])


def grade_m2a(items, answers, key: str = "none") -> Dict[str, object]:
    """M2a's refusal. `key` picks the «none» flag read (PREREG-S1B1 §3: "none" the law; "none_i" / "none_ii" the
    readings from the same state)."""
    rows = [{"none": bool((answers.get(it["item_id"]) or {}).get(key)),
             "answered": answers.get(it["item_id"]) is not None and answers[it["item_id"]].get(key) is not None,
             "types": it["types"], "n_things": it["n_things"]} for it in items]
    res = {}
    for key, sel in [("all", rows)] + [(f"size{n}", [r for r in rows if r["n_things"] == n]) for n in (1, 2, 3)] + \
            [(f"type:{t}", [r for r in rows if t in r["types"]]) for t in ("colour", "shape")] + \
            [("type:none", [r for r in rows if not r["types"]])]:
        v, n = _rate(r["none"] for r in sel if r["answered"])
        res[key] = {"refusal": v, "n": n, "presence": sum(1 for r in sel if r["answered"])}
    return res


def grade_m2b(items, answers, covered_rows=None, key: str = "emit") -> Dict[str, object]:
    """CORRECT = no SHAPE word emitted (a colour or size word alone, or «I don't know», is correct). Declared: «dax» is a
    shape word. `covered_rows` (gaze arms): the rows whose thing got ≥ 1 fixation — the bar reads those (all printed).
    `key` picks the emission read (PREREG-S1B1 §3: "emit" the law; "emit_i" / "emit_ii" the readings)."""
    rows = []
    for it in items:
        a = answers.get(it["item_id"]) or {}
        em = a.get(key)
        if em is None:
            continue
        shape_words = [w for w in em if w in W.SHAPE_WORDS]
        rows.append({"shape": it["shape"], "graded": it["graded"], "correct": not shape_words, "emit": list(em),
                     "idk": not em, "colour_ok": it["colour"] in em, "size_ok": it["size"] in em,
                     "covered": True if covered_rows is None else it["row"] in covered_rows})
    def block(sel):
        c = [r for r in sel if r["covered"]]
        v, n = _rate(r["correct"] for r in c)
        va, na = _rate(r["correct"] for r in sel)
        return {"correct": v, "n": n, "correct_all": va, "n_all": na,
                "idk": _rate(r["idk"] for r in c)[0], "colour_word_right": _rate(r["colour_ok"] for r in c)[0],
                "size_word_right": _rate(r["size_ok"] for r in c)[0],
                "shape_words_emitted": dict(collections.Counter(w for r in c for w in r["emit"] if w in W.SHAPE_WORDS))}
    res = {"graded": block([r for r in rows if r["graded"]]), "diamond": block([r for r in rows if not r["graded"]])}
    for s in W.M2B_SHAPES:
        res[f"shape:{s}"] = block([r for r in rows if r["shape"] == s])
    return res


# ------------------------------------------------------------------------------------------------ S1b-1: M3, SPEAK, DECLINE
# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:48 +0400 — PREREG-S1B1 §4–§5 (sha caace482…).
TYPE_RANK = {"size": 0, "colour": 1, "shape": 2}          # the parent's order (the templates: size, colour, shape)


def m3_items(truth: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    """M3 COMPOSE: the m3 split's scenes carry their phrase and target (the question and its truth)."""
    items = []
    for row in truth:
        things = things_of(row)
        phrase = list(row["words"])
        tgt = things[int(row["referent"])]
        items.append({"item_id": f"M3:{row['item_id']}", "mark": "M3", "row": int(row["row"]), "phrase": phrase,
                      "target": int(row["referent"]), "kind": W.m3_kind(int(row["index"])), "pair": [tgt.shape, tgt.colour],
                      "types": list(necessary_types(phrase, things)), "template": "T2", "n_things": len(things)})
    return items


def summarise_m3(g: Sequence[Dict[str, object]], items: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """M3's blocks: all (every M3 item is a 2- or 3-thing scene), per scene size, per distractor kind (a miss on one kind
    alone names the word that does not compose), per held-out pair (n 10, readings)."""
    kind = {it["item_id"]: it["kind"] for it in items}
    pair = {it["item_id"]: f"{it['pair'][0]}-{it['pair'][1]}" for it in items}
    res = {"all": _pointing_block(g)}
    for n in (2, 3):
        res[f"size{n}"] = _pointing_block([r for r in g if r["n_things"] == n])
    for k in ("colour", "shape", "both"):
        res[f"kind:{k}"] = _pointing_block([r for r in g if kind[r["item_id"]] == k])
    for sh, co in W.HELDOUT:
        res[f"pair:{sh}-{co}"] = _pointing_block([r for r in g if pair[r["item_id"]] == f"{sh}-{co}"])
    return res


def speak_items(truth: Sequence[Dict[str, object]], mark: str = "SPEAK") -> List[Dict[str, object]]:
    return [{"item_id": f"{mark}:{row['item_id']}", "mark": mark, "row": int(row["row"]), "phrase": [],
             "target": int(row["referent"]), "n_things": len(row["things"])} for row in truth]


def decline_items(truth: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    items = speak_items(truth, "DECLINE")
    for it, row in zip(items, truth):
        t = row["things"][it["target"]]
        it.update({"kind": W.decline_kind(int(row["index"])), "shape": t["shape"], "size": t["size"]})
    return items


def unique_true(phrase: Sequence[str], things: Sequence[W.Thing], target: int, among: Iterable[int]) -> bool:
    """The phrase is true of the target and of no other thing in `among` (order-free: phrase_true_of)."""
    if not W.phrase_true_of(phrase, things[target]):
        return False
    return not any(W.phrase_true_of(phrase, things[k]) for k in among if k != target)


def in_parent_order(phrase: Sequence[str]) -> bool:
    ranks = [TYPE_RANK[W.word_type(w)] for w in phrase]
    return all(a < b for a, b in zip(ranks, ranks[1:]))


def random_true_phrase_chance(things: Sequence[W.Thing], target: int) -> float:
    """N-SHUF's reference (declared): the fraction of the parent's grammar — (size | ∅) × (colour | ∅) × shape, 108
    phrases — that is true of the target and of no other thing in view."""
    n = hit = 0
    for size in (None,) + W.SIZE_NAMES:
        for colour in (None,) + W.COLOUR_NAMES:
            for shape in W.SHAPES:
                phrase = [w for w in (size, colour, shape) if w is not None]
                n += 1
                hit += unique_true(phrase, things, target, range(len(things)))
    return hit / n


def _mouth_row(it, a, row, pointer) -> Dict[str, object]:
    things = things_of(row)
    ft = row["fix_thing"]
    t = int(it["target"])
    sp = a.get("spoken")
    seen = {k for k in ft if k is not None}
    return {"item_id": it["item_id"], "covered": covered(t, ft), "spoken": sp is not None,
            "phrase": list(sp) if sp is not None else None,
            "true": sp is not None and unique_true(sp, things, t, range(len(things))),
            "true_seen": sp is not None and unique_true(sp, things, t, seen),
            "readback_ok": (sp is not None and a.get("readback_point") is not None
                            and a.get("readback_point") == a.get("target") and a.get("target") == pointer),
            "in_order": (in_parent_order(sp) if sp is not None and len(sp) >= 2 else None),
            "length": len(sp) if sp is not None else 0, "reason": a.get("reason"),
            "has_colour": sp is not None and any(w in W.COLOURS for w in sp), "n_things": it["n_things"],
            "chance": random_true_phrase_chance(things, t), "kind": it.get("kind")}


def grade_speak(items, answers, truth, pointers: Optional[Dict[str, Optional[int]]] = None) -> List[Dict[str, object]]:
    """Per item: covered (the target has ≥ 1 fixation — the bars read those), spoken, TRUE (of the target and of no other
    thing in view, the world's truth, order-free), TRUE-SEEN (no other SEEN thing), READ-BACK re-checked from the arm's
    recorded point and the target it was given (and that the given target is the question's pointer), ORDER, length.
    `pointers`: item_id → the pointer the question carried (the target hypothesis, or the thing for ORACLE-TRUTH);
    default = the recorded target itself."""
    rows = []
    for it in items:
        a = answers.get(it["item_id"]) or {}
        ptr = a.get("target") if pointers is None else pointers.get(it["item_id"])
        rows.append(_mouth_row(it, a, truth[it["row"]], ptr))
    return rows


def summarise_speak(rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    cov = [r for r in rows if r["covered"]]
    sp = [r for r in cov if r["spoken"]]
    multi = [r for r in sp if r["length"] >= 2]
    out = {"spoken": _rate(r["spoken"] for r in cov)[0], "n_covered": len(cov),
           "spoken_all": _rate(r["spoken"] for r in rows)[0], "n_all": len(rows),
           "truth": _rate(r["true"] for r in sp)[0], "n_spoken": len(sp),
           "truth_seen": _rate(r["true_seen"] for r in sp)[0],
           "truth_x_spoken": _rate(r["spoken"] and r["true"] for r in cov)[0],
           "readback": _rate(r["readback_ok"] for r in sp)[0],
           "order": _rate(r["in_order"] for r in multi)[0], "n_multi": len(multi),
           "length_mix": {str(k): (sum(1 for r in sp if r["length"] == k) / len(sp) if sp else None) for k in (1, 2, 3)},
           "reasons": dict(collections.Counter(r["reason"] for r in cov if not r["spoken"])),
           "chance_truth": (float(np.mean([r["chance"] for r in cov])) if cov else None)}
    return out


def grade_decline(items, answers, truth, pointers: Optional[Dict[str, Optional[int]]] = None) -> List[Dict[str, object]]:
    rows = grade_speak(items, answers, truth, pointers)
    for r in rows:
        r["correct"] = not r["has_colour"]                     # a decline counts as correct; a colourless phrase too
    return rows


def summarise_decline(rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    cov = [r for r in rows if r["covered"]]
    a = [r for r in cov if r["kind"] == "A"]
    b = [r for r in cov if r["kind"] == "B"]
    a_sp = [r for r in a if r["spoken"]]
    return {"decline": _rate(r["correct"] for r in cov)[0], "n_covered": len(cov), "n_all": len(rows),
            "decline_all": _rate(r["correct"] for r in rows)[0],
            "kind_A_spoken": _rate(r["spoken"] for r in a)[0], "n_A": len(a),
            "kind_A_truth": _rate(r["true"] for r in a_sp)[0], "n_A_spoken": len(a_sp),
            "kind_B_decline_rate": _rate(not r["spoken"] for r in b)[0], "n_B": len(b),
            "reasons": dict(collections.Counter(r["reason"] for r in cov if not r["spoken"]))}


# ------------------------------------------------------------------------------------------------ stage −1 (organ facts)
def loo_ncm(X: np.ndarray, y: Sequence[str]) -> Optional[float]:
    """Leave-one-out nearest-class-mean (the seat's probe's own rule: a class seen only in the left-out item is absent)."""
    y = np.asarray(y)
    n = len(y)
    if n < 2:
        return None
    cls = sorted(set(y.tolist()))
    sums = {c: X[y == c].sum(axis=0) for c in cls}
    cnt = {c: int((y == c).sum()) for c in cls}
    ok = 0
    for i in range(n):
        names, means = [], []
        for c in cls:
            if c == y[i]:
                if cnt[c] <= 1:
                    continue
                means.append((sums[c] - X[i]) / (cnt[c] - 1))
            else:
                means.append(sums[c] / cnt[c])
            names.append(c)
        M = np.stack(means)
        ok += names[int(np.argmin(((M - X[i]) ** 2).sum(axis=1)))] == y[i]
    return ok / n


def organ_facts(truth: Sequence[Dict[str, object]], percepts) -> Dict[str, object]:
    """Stage −1: gaze per-thing recall by scene size; the merge rate (hypotheses covering 2 things); the split rate (one
    thing → ≥ 2 hypotheses); the eye's input separability on one-thing scenes (LOO nearest-class-mean for shape, colour,
    size on all 144 / tower 112 / colour 32) on three roads: the thing's HYPOTHESIS (what P-ORACLE reads), the probe's
    TRUTH road (the unit mean of the fixations that land on the thing), and the FORCED window (ORACLE-TRUTH's)."""
    rec = {n: [] for n in (1, 2, 3)}
    all_cov = {n: [] for n in (1, 2, 3)}
    merge = {n: [0, 0] for n in (1, 2, 3)}
    junk = {n: [0, 0] for n in (1, 2, 3)}
    split = {n: [0, 0] for n in (1, 2, 3)}
    roads = {"hypothesis": [], "truth": [], "forced": []}
    labels = []
    for row in truth:
        n = len(row["things"])
        ft = row["fix_thing"]
        hyps = percepts.hypotheses(int(row["row"]))
        members = [h.members for h in hyps]
        cnts = hyp_counts(members, ft)
        cov = [covered(k, ft) for k in range(n)]
        rec[n].extend(cov)
        all_cov[n].append(all(cov))
        for c, mem in zip(cnts, members):
            merge[n][1] += 1
            junk[n][1] += 1
            if len(c) >= 2:
                merge[n][0] += 1
            if not c:
                junk[n][0] += 1
        for k in range(n):
            if not cov[k]:
                continue
            split[n][1] += 1
            if sum(1 for c in cnts if c.get(k, 0) > 0) >= 2:
                split[n][0] += 1
        if n == 1 and cov[0]:
            hi = thing_hypothesis(0, members, [h.pos for h in hyps], ft, tuple(row["centroids"][0]))
            roads["hypothesis"].append(hyps[hi].feat)
            _fix, loc = percepts.located(int(row["row"]))
            on = [loc[m] for m in range(len(ft)) if ft[m] == 0]
            v = np.mean(on, axis=0)
            roads["truth"].append(v / (np.linalg.norm(v) + 1e-12))
            roads["forced"].append(percepts.forced(int(row["row"]))[0])
            t = row["things"][0]
            labels.append((t["shape"], t["colour"], t["size"]))
    out = {"recall": {n: _rate(rec[n]) for n in rec}, "all_covered": {n: _rate(all_cov[n]) for n in all_cov},
           "merge": {n: (merge[n][0] / merge[n][1] if merge[n][1] else None, merge[n][1]) for n in merge},
           "on_no_thing": {n: (junk[n][0] / junk[n][1] if junk[n][1] else None, junk[n][1]) for n in junk},
           "split": {n: (split[n][0] / split[n][1] if split[n][1] else None, split[n][1]) for n in split},
           "separability": {}, "n_one_thing": len(labels)}
    if labels:
        ys = {"shape": [l[0] for l in labels], "colour": [l[1] for l in labels], "size": [l[2] for l in labels]}
        for road, vecs in roads.items():
            X = np.stack(vecs)
            out["separability"][road] = {
                typ: {"all 144": loo_ncm(X, y), "tower 112": loo_ncm(X[:, :112], y), "colour 32": loo_ncm(X[:, 112:], y)}
                for typ, y in ys.items()}
    return out
