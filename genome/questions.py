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

from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from . import world
from .machinery import Organism, retina

Ledger = Dict[int, Set[str]]     # cell id -> the set of things (or words) it was born on


def word_of_vector(v: np.ndarray, blank_zero: bool = False) -> str:
    """The word a words-area vector HOLDS (edit: Claude (Fable 5.1, the seat), 2026-09-29 12:59 +0400 — PREREG-WORD-ROAD §1.9): the ear's code
    (genome/world.py:encode_word) is one-hot per letter slot, so a word cell — which stores its birth input — decodes to
    exactly one word. Refuses BY NAME a vector that is no word's code (the round trip must be exact)."""
    v = np.asarray(v, dtype=np.float64)
    width = 26 if blank_zero else 27
    if v.shape != (world.WORD_SLOTS * width,):
        raise ValueError(f"word_of_vector: a vector of shape {v.shape} is not the ear's code ({world.WORD_SLOTS} x {width})")
    letters = []
    for i in range(world.WORD_SLOTS):
        seg = v[i * width:(i + 1) * width]
        k = int(np.argmax(seg))
        if seg[k] <= 0.0 or k == 26:
            break
        letters.append(world.LETTERS[k])
    word = "".join(letters)
    if not np.allclose(world.encode_word(word, blank_zero), v, rtol=0.0, atol=1e-12):
        raise ValueError(f"word_of_vector: the vector is not the code of {word!r} — a word cell holds something that is no word")
    return word


def build_ledgers(org: Organism, moment_thing: Dict[int, str], words_by_vector: bool = False) -> Dict[str, Ledger]:
    """From the organism's birth log (moment, area, cell, reason) and the runner's own map of
    moment → thing shown, derive which thing each cell was born on. Merges union the sets.

    edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:31 +0400 — A4L-VOICE (docs/briefs/A4L-VOICE.md task 2):
    a THIRD ledger. Before this edit every birth whose area was not "sight" was filed as WORDS — a sound cell would have
    been read as a word cell, silently. A sound birth is filed as SOUND, its own ledger; the returned dict always carries
    "sound" (empty for a genome without the area — every consumer reads "sight"/"words" by key, grepped)."""
    sight: Ledger = {}
    words: Ledger = {}
    sound: Ledger = {}
    # edit: Claude (Fable 5.1, the seat), 2026-09-29 12:59 +0400 — PREREG-WORD-ROAD §1.9: `words_by_vector` (the gene HEAR; False on every call
    # before this edit, byte for byte the old ledger). Under it several word cells are born at ONE moment (a moment meets
    # every word of its utterance), and `moment_thing[m]` names only the LAST word — so a WORD cell is named by the word its
    # own vector holds. The sight ledger and the sound ledger are untouched (`thing last`).
    for m, area, cid, _reason in org.births:
        if words_by_vector and area not in ("sight", "sound"):
            words.setdefault(cid, set()).add(word_of_vector(org.words.cells[cid], org.g.ear_blank_zero))
            continue
        (sight if area == "sight" else (sound if area == "sound" else words)).setdefault(cid, set()).add(moment_thing[m])
    for _m, area, kept, dropped in org.merges:
        L = sight if area == "sight" else (sound if area == "sound" else words)
        L.setdefault(kept, set()).update(L.get(dropped, set()))
    return {"sight": sight, "words": words, "sound": sound}


def word_cells(org: Organism, ledger_words: Ledger, word: str) -> List[int]:
    return [c for c, s in ledger_words.items() if s == {word} and org.words.alive[c]]


def _feat(org: Organism, pic: np.ndarray) -> np.ndarray:
    return retina(pic, org.g.retina)


# edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:47 +0400 — L-6/ANSWER (docs/briefs/LIFE-A-ANSWER-SELF.md
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
                blank_zero: bool = False, majority: Optional[bool] = None) -> Dict[str, object]:
    """`majority` (edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:11 +0400 — A4-LADDER-PREREG
    §2.2 task 3): a read-side override forwarded to every `recall_many` call below — None (the default) reads
    the genome's own declared law, byte-identical to before this parameter existed; True/False forces ANSWER's
    majority-of-glances gate on/off regardless of what the genome declares, so a sitter can ask the SAME
    questions of the SAME organism under both laws with no replay (self_exam.py's `*_old_law` fields)."""
    Ls, Lw = ledgers["sight"], ledgers["words"]
    n = len(things)
    # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — Q3/Q4 draw a DISTRACTOR from the other things (`i % (n - 1)`); one thing has none.
    # The 2 h smokes of g5-seam-1 / L5 (2026-09-22 00:45 +04) hit this as a ZeroDivisionError inside the frozen-10 twin's exam
    # (the twin knew one word on the game tape) and the reader read (iii) as None. Refused by name (both ask roads); the caller falls back.
    if n < 2:
        raise ValueError(f"the exam needs at least two things (Q3/Q4 draw a distractor from the others); got {list(things)!r}")
    out: Dict[str, object] = {}
    # edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:11 +0400 — A4-LADDER-PREREG §2.2 task 2: every
    # abstain-reason dict below gains "minority" (#235: a widened set is a chain; a reader that does not widen
    # KeyErrors at the first minority row, since these are plain dicts, not a defaultdict/Counter).
    q1_ok = 0; q1_n = 0; q1_abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0, "minority": 0}; per = {t: [0, 0] for t in things}; multi = 0
    q1_hedged = 0        # L-6: the "unsure" share among the CORRECT answers -- the hedge rate
    for t in things:
        for xs in held[t]:
            r = org.recall_many("sight", xs, majority=majority); q1_n += 1; per[t][1] += 1
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
    q2_ok = 0; q2_abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0, "minority": 0}; q2_detail = {}
    for t in things:
        r = org.recall_many("words", [world.encode_word(t, blank_zero)], majority=majority)
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
            r = org.recall_many("sight", xs, majority=majority)
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
        abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0, "minority": 0}; answered = {}; graded = _new_graded_counts()
        for xs in rows:
            r = org.recall_many("sight", xs, majority=majority)
            graded[_grade_bucket(r)] += 1
            if r["cell"] is None: abst[r["reason"]] += 1
            else:
                a = "/".join(sorted(Lw.get(r["cell"], set()))); answered[a] = answered.get(a, 0) + 1
        q5[name] = {"abstain_rate": (sum(abst.values()) / len(rows)) if rows else 0.0, "n": len(rows), "abstain": abst, "answered_as": answered, "graded": graded}
    out["Q5"] = q5
    out["composite"] = float(np.mean([out["Q1"]["acc"], out["Q2"]["acc"], out["Q3"]["acc"], out["Q4"]["acc"]]))
    return out


def ask_plant_glances(org: Organism, ledgers: Dict[str, Ledger], word: str, rows: List[List[np.ndarray]],
                      majority: Optional[bool] = None) -> Dict[str, object]:
    """`majority`: the same read-side override as `ask_glances` (A4-LADDER-PREREG §2.2 task 3/5)."""
    Lw = ledgers["words"]; ok = 0; abst = {"novel": 0, "noedge": 0, "ratio": 0, "close": 0, "minority": 0}; answered = {}; graded = _new_graded_counts()
    for xs in rows:
        r = org.recall_many("sight", xs, majority=majority)
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


# ============================================================================ A4L-VOICE: the exam by SOUND
# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:37 +0400 — docs/briefs/A4L-VOICE.md task 4; docs/A4-LADDER-PREREG.md
# §2.3 (V1, V2, V5, V1b). The chords are handed in (genome/voice.py's trait_f32 — the bytes the maker publishes), the held-out renders
# are the exam's own (seed 2), and every answer is scored by a LEDGER outside the organism. Reads only: the organism's hash is
# unchanged by it (the exam asserts it).
def _label(L: Ledger, cell) -> str:
    return "/".join(sorted(L.get(cell, set()))) if cell is not None else ""


def ask_sound(org: Organism, ledgers: Dict[str, Ledger], things: Sequence[str], held: Dict[str, List[List[np.ndarray]]],
              chords: Dict[str, np.ndarray], shifted: Dict[str, Dict[str, np.ndarray]] = None,
              voiced: Dict[str, int] = None, min_voiced: int = 5) -> Dict[str, object]:
    """V1 — each thing's chord → recall sound→sight → the sight cell's birth ledger names the thing.
    V2 — each held-out render's glances → recall_many sight→sound → the sound cell's ledger names the thing.
    V5 — each chord → recall sound→words → the word cell's ledger names the thing (only when MEET sound words exists).
    V1b — the ±4 % pitch-shifted chords, V1's road (printed, no bar). `voiced`: the maker's sound rows per word on the
    tape; `gradable` is False until every asked thing was voiced ≥ `min_voiced` times (the PREREG's «not gradable» rule).
    A genome with no sound area answers `{"graded": False, "reason": ...}` — never an error."""
    if getattr(org, "sound", None) is None:
        return {"gradable": False, "reason": "no sound area (AREA sound undeclared)"}
    Ls, Lw, Lu = ledgers["sight"], ledgers["words"], ledgers.get("sound", {})
    pairs = getattr(org, "sound_meets", {})
    out: Dict[str, object] = {"things": list(things), "sound_born": int(org.sound.n), "sound_alive": int(org.sound.alive.sum())}

    def by_chord(to: str, L: Ledger, table: Dict[str, np.ndarray]) -> Dict[str, object]:
        ok = 0; per: Dict[str, str] = {}; reasons: Dict[str, int] = {}
        for t in things:
            if t not in table:
                per[t] = "no chord"; continue
            r = org.recall("sound", table[t], to=to)
            if r["cell"] is None:
                reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
                per[t] = f"abstain:{r['reason']}"
            else:
                lab = _label(L, r["cell"]); per[t] = lab or "?"
                ok += int(L.get(r["cell"], set()) == {t})
        n = len(things)
        return {"correct": ok, "n": n, "acc": (ok / n) if n else 0.0, "abstain": reasons, "per_thing": per}

    out["V1"] = by_chord("sight", Ls, chords) if "sight-sound" in pairs else None
    out["V5"] = by_chord("words", Lw, chords) if "sound-words" in pairs else None
    # V2 names the answered SOUND cell by the chord it HOLDS (its prototype resonates the thing's TRUE chord at THETA_SOUND)
    # — «the true mapping». On the rung this is its birth ledger (the maker says chord(t) on t's canvas); on the SHUFFLED-
    # sound twin the birth ledger would carry the canvas's label and read the permuted pairing as correct — a null that
    # passes by construction (#228's fifth gate). The birth-ledger reading is printed beside it (`ledger_correct`).
    identity: Dict[int, str] = {}
    th = float(getattr(org, "theta_sound", 0.0) or 0.0)
    for u in range(int(org.sound.n)):
        if not org.sound.alive[u]:
            continue
        best_t, best_c = None, -1.0
        for t, ch in chords.items():
            cv = float(org.sound.cells[u] @ ch)
            if cv > best_c:
                best_t, best_c = t, cv
        if best_t is not None and best_c >= th:
            identity[u] = best_t
    out["sound_identity"] = {int(u): t for u, t in sorted(identity.items())}
    if "sight-sound" in pairs:
        ok = 0; ok_ledger = 0; n = 0; per: Dict[str, List[int]] = {}; reasons: Dict[str, int] = {}
        for t in things:
            per[t] = [0, 0]
            for xs in held.get(t, []):
                r = org.recall_many("sight", xs, to="sound"); n += 1; per[t][1] += 1
                if r["cell"] is None:
                    reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
                    continue
                if identity.get(int(r["cell"])) == t:
                    ok += 1; per[t][0] += 1
                if Lu.get(r["cell"], set()) == {t}:
                    ok_ledger += 1
        out["V2"] = {"correct": ok, "n": n, "acc": (ok / n) if n else 0.0, "abstain": reasons, "ledger_correct": ok_ledger,
                     "per_thing": {t: (v[0] / v[1]) if v[1] else None for t, v in per.items()}}
    else:
        out["V2"] = None
    if shifted and "sight-sound" in pairs:
        out["V1b"] = {s: by_chord("sight", Ls, {t: d[s] for t, d in shifted.items() if s in d}) for s in ("0.96", "1.04")}
    voiced = dict(voiced or {})
    out["voiced"] = {t: int(voiced.get(t, 0)) for t in things}
    short = [t for t in things if voiced.get(t, 0) < min_voiced]
    # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:49 +0400 — the scores over the things the world has VOICED ≥ min_voiced
    # times, printed beside the whole-16 marks: a 20-min pre-flight voices window 0's eleven only (window 2 arrives at hour 4), so its
    # positive control reads HERE while the 16-thing marks read «not gradable» — never a bar, a reading of the road on what was heard.
    heard = [t for t in things if voiced.get(t, 0) >= min_voiced]
    def _on(block, key_ok):
        if not block or not heard:
            return None
        ok = sum(1 for t in heard if key_ok(block, t))
        return {"correct": ok, "n": len(heard), "acc": ok / len(heard)}
    out["voiced_things"] = heard
    out["V1_on_voiced"] = _on(out.get("V1"), lambda b, t: b["per_thing"].get(t) == t)
    out["V5_on_voiced"] = _on(out.get("V5"), lambda b, t: b["per_thing"].get(t) == t)
    if out.get("V2") and heard:
        per = out["V2"]["per_thing"]; vals = [per.get(t) for t in heard if per.get(t) is not None]
        out["V2_on_voiced"] = {"acc": (sum(vals) / len(vals)) if vals else None, "n_things": len(vals)}
    else:
        out["V2_on_voiced"] = None
    out["gradable"] = not short
    out["reason"] = "graded" if not short else f"not gradable: voiced < {min_voiced} times: {short}"
    return out
