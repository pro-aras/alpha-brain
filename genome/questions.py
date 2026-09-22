"""questions.py — asks the five questions and scores them OUTSIDE the organism.

edit: Claude (Fable 5.1), 2026-09-19 19:33 +0400 — G3: a fourth abstain reason «close» (ABSTAIN margin) counted everywhere.
edit: Claude (Fable 5.1), 2026-09-19 16:2x +04 — G0 rung 0 (docs/G0-PREREG.md §3, §10 clauses 1, 4, 5).
edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B5 (docs/G4-PREREG.md §3): `why(org,
ledgers, episodes, word)` — the record behind an answer. Reads only; changes nothing (a question never
changes the organism, G0's law, extended to the episode store).

The organism only ever returns a CELL (or abstains). The ledger — which thing each sight
cell was born on, which word each word cell holds — is built by the runner from the
stream and lives here, never in the organism. Questions never change the organism.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Set, Tuple

import numpy as np

from . import world
from .machinery import Organism, retina

Ledger = Dict[int, Set[str]]     # cell id -> the set of things (or words) it was born on


def build_ledgers(org: Organism, moment_thing: Dict[int, str]) -> Dict[str, Ledger]:
    """From the organism's birth log (moment, area, cell, reason) and the runner's own map of
    moment → thing shown, derive which thing each cell was born on. Merges union the sets."""
    sight: Ledger = {}
    words: Ledger = {}
    for m, area, cid, _reason in org.births:
        (sight if area == "sight" else words).setdefault(cid, set()).add(moment_thing[m])
    for _m, area, kept, dropped in org.merges:
        L = sight if area == "sight" else words
        L.setdefault(kept, set()).update(L.get(dropped, set()))
    return {"sight": sight, "words": words}


def word_cells(org: Organism, ledger_words: Ledger, word: str) -> List[int]:
    return [c for c, s in ledger_words.items() if s == {word} and org.words.alive[c]]


def _feat(org: Organism, pic: np.ndarray) -> np.ndarray:
    return retina(pic, org.g.retina)


# edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 20:2x +0400 — L-6/ANSWER (docs/briefs/LIFE-A-ANSWER-SELF.md
# #2): one shared bucket for a `recall`/`recall_many` result's grade, used by Q1's hedge rate and every
# Q5/plant/null "graded" count below. `grade is None` (ANSWER undeclared) degenerates to the pre-ANSWER
# reading: a real answer is "sure_bare", an abstain is "abstain" — so every count below is well-defined
# (all zero in the categories ANSWER would have populated) whether or not the gene is declared.
def _grade_bucket(r: Dict[str, object]) -> str:
    grade = r.get("grade")
    if r["cell"] is not None:
        return "unsure" if grade == "unsure" else "sure_bare"
    return "abstain_with_resemblance" if grade in ("sure", "unsure") else "abstain"


def _new_graded_counts() -> Dict[str, int]:
    return {"sure_bare": 0, "unsure": 0, "abstain_with_resemblance": 0, "abstain": 0}


def ask(org: Organism, ledgers: Dict[str, Ledger], things: Sequence[str], held: Dict[str, List[np.ndarray]],
        never: Dict[str, List[np.ndarray]], blank_zero: bool = False) -> Dict[str, object]:
    """Q1–Q5 on held-out renderings of `things`; Q5 on `never` (things never shown). Returns every
    count, the abstain reasons separately, and per-thing accuracy."""
    Ls, Lw = ledgers["sight"], ledgers["words"]
    n = len(things)
    # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — Q3/Q4 draw a DISTRACTOR from the other things (`i % (n - 1)`); one thing has none.
    # The 2 h smokes of g5-seam-1 / L5 (2026-09-22 00:45 +04) hit this as a ZeroDivisionError inside the frozen-10 twin's exam
    # (the twin knew one word on the game tape) and the reader read (iii) as None. Refused by name (both ask roads); the caller falls back.
    if n < 2:
        raise ValueError(f"the exam needs at least two things (Q3/Q4 draw a distractor from the others); got {list(things)!r}")
    out: Dict[str, object] = {}

    # Q1 — what is this?  a held-out picture → the strongest edge from the lit sight cell into words
    q1_ok = 0; q1_n = 0; q1_abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0}; per = {t: [0, 0] for t in things}
    multi = 0; q1_hedged = 0        # L-6: the "unsure" share among the CORRECT answers -- the hedge rate
    for t in things:
        for pic in held[t]:
            r = org.recall("sight", _feat(org, pic)); q1_n += 1; per[t][1] += 1
            if r["cell"] is None:
                q1_abst[r["reason"]] += 1
            else:
                ans = Lw.get(r["cell"], set())
                if len(ans) > 1: multi += 1
                if ans == {t}:
                    q1_ok += 1; per[t][0] += 1
                    if _grade_bucket(r) == "unsure": q1_hedged += 1
    out["Q1"] = {"acc": q1_ok / q1_n, "n": q1_n, "correct": q1_ok, "abstain": q1_abst,
                 "false_abstention": sum(q1_abst.values()) / q1_n, "per_thing": {t: v[0] / v[1] for t, v in per.items()},
                 "answers_from_multi_word_cells": multi, "hedge_rate": (q1_hedged / q1_ok) if q1_ok else None}

    # Q2 — show me a «word»  a word → the strongest edge from its cell into sight; scored by the cell's thing
    q2_ok = 0; q2_abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0}; q2_detail = {}
    for t in things:
        r = org.recall("words", world.encode_word(t, blank_zero))
        if r["cell"] is None:
            q2_abst[r["reason"]] += 1; q2_detail[t] = f"abstain:{r['reason']}"
        else:
            born = Ls.get(r["cell"], set()); q2_detail[t] = "/".join(sorted(born))
            if born == {t}: q2_ok += 1
    out["Q2"] = {"acc": q2_ok / n, "n": n, "correct": q2_ok, "abstain": q2_abst, "detail": q2_detail}

    # Q3 — is this a «word»?  picture + word, half true: YES iff the word's cell carries the top edge and no abstain
    q3_ok = 0; q3_n = 0; q3_true_abstain = 0
    for ti, t in enumerate(things):
        for i, pic in enumerate(held[t]):
            truth = (i % 2 == 0)
            word = t if truth else things[(ti + 1 + (i % (n - 1))) % n]      # never t itself
            r = org.recall("sight", _feat(org, pic))
            yes = r["cell"] is not None and Lw.get(r["cell"], set()) == {word}
            if truth and r["cell"] is None: q3_true_abstain += 1
            q3_ok += int(yes == truth); q3_n += 1
    out["Q3"] = {"acc": q3_ok / q3_n, "n": q3_n, "correct": q3_ok, "true_pairs_abstained": q3_true_abstain,
                 "ceiling": 1.0 - 0.5 * out["Q1"]["false_abstention"]}

    # Q4 — which of these two is a «word»?  the larger edge from each picture's lit cell to the word's cell(s)
    q4_ok = 0; q4_n = 0; q4_ties = 0
    for ti, t in enumerate(things):
        wc = word_cells(org, Lw, t)
        for i, pic in enumerate(held[t]):
            u = things[(ti + 1 + (i % (n - 1))) % n]; other = held[u][i % len(held[u])]   # never t itself
            e_t = max([org.edge("sight", _feat(org, pic), c) for c in wc], default=0.0)
            e_u = max([org.edge("sight", _feat(org, other), c) for c in wc], default=0.0)
            if e_t == e_u: q4_ties += 1
            q4_ok += int(e_t > e_u); q4_n += 1
    out["Q4"] = {"acc": q4_ok / q4_n, "n": q4_n, "correct": q4_ok, "ties": q4_ties}

    # Q5 — a thing never shown: must abstain
    q5 = {}
    for name, pics in never.items():
        abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0}; answered = {}; graded = _new_graded_counts()
        for pic in pics:
            r = org.recall("sight", _feat(org, pic))
            graded[_grade_bucket(r)] += 1
            if r["cell"] is None: abst[r["reason"]] += 1
            else:
                a = "/".join(sorted(Lw.get(r["cell"], set()))); answered[a] = answered.get(a, 0) + 1
        q5[name] = {"abstain_rate": sum(abst.values()) / len(pics), "n": len(pics), "abstain": abst, "answered_as": answered, "graded": graded}
    out["Q5"] = q5
    out["composite"] = float(np.mean([out["Q1"]["acc"], out["Q2"]["acc"], out["Q3"]["acc"], out["Q4"]["acc"]]))
    return out


def ask_plant(org: Organism, ledgers: Dict[str, Ledger], word: str, pics: List[np.ndarray]) -> Dict[str, object]:
    """The plant («zog», shown 5 times) must be ANSWERED; the null plant («vex», shown 0 times) must abstain."""
    Lw = ledgers["words"]; ok = 0; abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0}; answered = {}; graded = _new_graded_counts()
    for pic in pics:
        r = org.recall("sight", _feat(org, pic))
        graded[_grade_bucket(r)] += 1
        if r["cell"] is None: abst[r["reason"]] += 1
        else:
            a = "/".join(sorted(Lw.get(r["cell"], set()))); answered[a] = answered.get(a, 0) + 1
            if Lw.get(r["cell"], set()) == {word}: ok += 1
    return {"answered_rate": ok / len(pics), "abstain_rate": sum(abst.values()) / len(pics), "n": len(pics), "abstain": abst, "answered_as": answered, "graded": graded}


# ============================================================================ G1: questions over GLANCES
# edit: Claude (Fable 5.1), 2026-09-19 17:24 +0400 — G1 §1: a picture is a LIST of glance features; recall_many/edge_many sum the
# evidence over glances. With one glance per picture these are `ask`/`ask_plant` (pinned in tools/pin_g1.py).
Held = Dict[str, List[List[np.ndarray]]]     # thing -> pictures -> glance features


def ask_glances(org: Organism, ledgers: Dict[str, Ledger], things: Sequence[str], held: Held, never: Held,
                blank_zero: bool = False) -> Dict[str, object]:
    Ls, Lw = ledgers["sight"], ledgers["words"]
    n = len(things)
    # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — Q3/Q4 draw a DISTRACTOR from the other things (`i % (n - 1)`); one thing has none.
    # The 2 h smokes of g5-seam-1 / L5 (2026-09-22 00:45 +04) hit this as a ZeroDivisionError inside the frozen-10 twin's exam
    # (the twin knew one word on the game tape) and the reader read (iii) as None. Refused by name (both ask roads); the caller falls back.
    if n < 2:
        raise ValueError(f"the exam needs at least two things (Q3/Q4 draw a distractor from the others); got {list(things)!r}")
    out: Dict[str, object] = {}
    q1_ok = 0; q1_n = 0; q1_abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0}; per = {t: [0, 0] for t in things}; multi = 0
    q1_hedged = 0        # L-6: the "unsure" share among the CORRECT answers -- the hedge rate
    for t in things:
        for xs in held[t]:
            r = org.recall_many("sight", xs); q1_n += 1; per[t][1] += 1
            if r["cell"] is None:
                q1_abst[r["reason"]] += 1
            else:
                ans = Lw.get(r["cell"], set())
                if len(ans) > 1: multi += 1
                if ans == {t}:
                    q1_ok += 1; per[t][0] += 1
                    if _grade_bucket(r) == "unsure": q1_hedged += 1
    out["Q1"] = {"acc": q1_ok / q1_n if q1_n else 0.0, "n": q1_n, "correct": q1_ok, "abstain": q1_abst,
                 "false_abstention": (sum(q1_abst.values()) / q1_n) if q1_n else 0.0, "per_thing": {t: (v[0] / v[1]) if v[1] else 0.0 for t, v in per.items()},
                 "answers_from_multi_word_cells": multi, "hedge_rate": (q1_hedged / q1_ok) if q1_ok else None}
    q2_ok = 0; q2_abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0}; q2_detail = {}
    for t in things:
        r = org.recall_many("words", [world.encode_word(t, blank_zero)])
        if r["cell"] is None:
            q2_abst[r["reason"]] += 1; q2_detail[t] = f"abstain:{r['reason']}"
        else:
            born = Ls.get(r["cell"], set()); q2_detail[t] = "/".join(sorted(born))
            if born == {t}: q2_ok += 1
    out["Q2"] = {"acc": q2_ok / n if n else 0.0, "n": n, "correct": q2_ok, "abstain": q2_abst, "detail": q2_detail}
    q3_ok = 0; q3_n = 0; q3_true_abstain = 0
    for ti, t in enumerate(things):
        for i, xs in enumerate(held[t]):
            truth = (i % 2 == 0)
            word = t if truth else things[(ti + 1 + (i % (n - 1))) % n]
            r = org.recall_many("sight", xs)
            yes = r["cell"] is not None and Lw.get(r["cell"], set()) == {word}
            if truth and r["cell"] is None: q3_true_abstain += 1
            q3_ok += int(yes == truth); q3_n += 1
    out["Q3"] = {"acc": q3_ok / q3_n if q3_n else 0.0, "n": q3_n, "correct": q3_ok, "true_pairs_abstained": q3_true_abstain,
                 "ceiling": 1.0 - 0.5 * out["Q1"]["false_abstention"]}
    q4_ok = 0; q4_n = 0; q4_ties = 0
    for ti, t in enumerate(things):
        wc = word_cells(org, Lw, t)
        for i, xs in enumerate(held[t]):
            u = things[(ti + 1 + (i % (n - 1))) % n]; other = held[u][i % len(held[u])]
            e_t = max([org.edge_many("sight", xs, c) for c in wc], default=0.0)
            e_u = max([org.edge_many("sight", other, c) for c in wc], default=0.0)
            if e_t == e_u: q4_ties += 1
            q4_ok += int(e_t > e_u); q4_n += 1
    out["Q4"] = {"acc": q4_ok / q4_n if q4_n else 0.0, "n": q4_n, "correct": q4_ok, "ties": q4_ties}
    q5 = {}
    for name, rows in never.items():
        abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0}; answered = {}; graded = _new_graded_counts()
        for xs in rows:
            r = org.recall_many("sight", xs)
            graded[_grade_bucket(r)] += 1
            if r["cell"] is None: abst[r["reason"]] += 1
            else:
                a = "/".join(sorted(Lw.get(r["cell"], set()))); answered[a] = answered.get(a, 0) + 1
        q5[name] = {"abstain_rate": (sum(abst.values()) / len(rows)) if rows else 0.0, "n": len(rows), "abstain": abst, "answered_as": answered, "graded": graded}
    out["Q5"] = q5
    out["composite"] = float(np.mean([out["Q1"]["acc"], out["Q2"]["acc"], out["Q3"]["acc"], out["Q4"]["acc"]]))
    return out


def ask_plant_glances(org: Organism, ledgers: Dict[str, Ledger], word: str, rows: List[List[np.ndarray]]) -> Dict[str, object]:
    Lw = ledgers["words"]; ok = 0; abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0}; answered = {}; graded = _new_graded_counts()
    for xs in rows:
        r = org.recall_many("sight", xs)
        graded[_grade_bucket(r)] += 1
        if r["cell"] is None: abst[r["reason"]] += 1
        else:
            a = "/".join(sorted(Lw.get(r["cell"], set()))); answered[a] = answered.get(a, 0) + 1
            if Lw.get(r["cell"], set()) == {word}: ok += 1
    return {"answered_rate": ok / len(rows) if rows else 0.0, "abstain_rate": (sum(abst.values()) / len(rows)) if rows else 0.0, "n": len(rows), "abstain": abst, "answered_as": answered, "graded": graded}


# ============================================================================ B5: «why» — the record behind an answer
def why(org: Organism, ledgers: Dict[str, Ledger], episodes, word: str) -> Dict[str, object]:
    """G4 §3 B5: the record behind an answer about `word` — not a new question to the organism, a
    report ON the organism's own state. "cells": every alive cell (in either area) born on `word` alone,
    as ("sight"|"words", cell_id) pairs; "episodes": every live FAST episode (genome/fast.py's Episodes)
    whose own word is exactly `word`, ids ascending; "edges": every currently-alive edge between one of
    those sight cells and one of those word cells, as (sight_cell, word_cell, weight) — the strongest
    evidence a caller can show for "why does it say that". `episodes` may be None (no FAST store yet).
    Never changes the organism or the episode store; a word never shown (no cell, no episode) returns
    every list empty, never an error — "I do not know" has a why too: nothing."""
    sight_cells = sorted(c for c, s in ledgers.get("sight", {}).items() if s == {word} and org.sight.alive[c])
    words_cells = sorted(c for c, s in ledgers.get("words", {}).items() if s == {word} and org.words.alive[c])
    cells: List[Tuple[str, int]] = [("sight", c) for c in sight_cells] + [("words", c) for c in words_cells]
    ep_ids: List[int] = []
    if episodes is not None:
        for slot in range(len(episodes)):
            if str(episodes.word[slot]) == word:
                ep_ids.append(int(episodes.ids[slot]))
        ep_ids.sort()
    edges: List[Tuple[int, int, float]] = []
    for s in sight_cells:
        for t in words_cells:
            if org.mask[s, t]:
                edges.append((s, t, float(org.W[s, t])))
    return {"cells": cells, "episodes": ep_ids, "edges": edges}
