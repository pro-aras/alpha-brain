"""genome/think.py — B11 (docs/G4-PREREG.md §11.2): THINK's laws. Beliefs (append-only, clash-opening,
never overwriting), and the two one-step reasoning laws: induce (episodes -> a rule) and deduce (beliefs
-> a predicted co-resonance), both FILE-ready (genome/predict.py's file()/FILE_FIELDS law).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — new module, Wave 2 B11.

Interface fixed for Builder A (§11, the coordinator's Wave 2 message, verbatim):
    believe(word, cells, episode_ids, moment, path) -> row       # append-only beliefs.jsonl
    clash(new_row, old_rows, path) -> row|None                   # a clash OPENS a row, never overwrites
    induce(episodes, k, org) -> list[rule]                       # FILE-ready claims
    deduce(beliefs) -> list[claim]                                # one step; FILE-ready

Design decisions, made and documented here (three ambiguities the PREREG names but does not spell out
to the last detail — decide and write it down, never guess silently: SOLUTIONS #131/#180):

  1. induce()'s "cluster C" for a word W. The organism is asked for W's own word-area cell via
     org.recall("words", world.encode_word(W, ...)) — the same door a live mind would use, no external
     ledger passed in (induce's signature carries only episodes/k/org). C = the set of alive sight
     cells whose strongest word edge (Organism._answer_of) IS that word cell — the cells that "belong
     to W" by the organism's own wiring, not by the ledger's birth history. If the organism itself
     abstains on W (no word cell resonates), no rule is attempted for W — there is nothing induce could
     even name a cluster against.

     "Agree"/"disagree": an episode with word W AGREES when its stored x_s's NEAREST alive sight cell
     (raw cosine over org.sight.cells[:n], not RECALL's resonance-and-KWTA path) is in C; it DISAGREES
     when that nearest cell exists and is outside C. A rule W => C is induced when agree >= k and
     disagree == 0 over that word's episodes.

     route/decider/due for the FILE row: route names the next check ("recall(sight) on the next episode
     with word W"), decider names the mechanical test ("recall(sight) in cluster C"), due is a moment
     string (always non-empty, so a genuinely inducible rule is never accidentally refused by FILE for
     an empty-string technicality).

  2. deduce()'s "unroutable deduction". Two beliefs about DIFFERENT words sharing >=1 cell predict a
     co-resonance and are routed at that shared cell (route names it). Two beliefs about the SAME word
     whose cell sets are DISJOINT — exactly clash()'s own condition — cannot be routed to any ONE cell:
     the belief is fractured across two clusters and there is no cell that stands for "recall answers
     this word" any more. That pair is still handed to file(), with route="" — FILE refuses it BY NAME
     (this is B11's third toy: "an unroutable deduction is REFUSED by name"). Two beliefs about the same
     word with OVERLAPPING cells are not a deduction target at all (one belief, not two to relate).

  3. clash()'s definition, shared with (2): two belief rows about the SAME word whose "cells" sets are
     DISJOINT (no cell in common) are a clash; overlapping cells (even partially) are not — the belief
     is read as the same underlying claim, merely extended. A clash never edits either row; it opens a
     NEW row of kind "clash" naming both old rows' line numbers, appended to the same beliefs.jsonl.
"""
from __future__ import annotations

import json
import pathlib as _pl
from typing import Dict, List, Optional, Union

import numpy as np

from . import world
from .machinery import Organism
from .predict import file as _file


# ============================================================================ BELIEF
def believe(word: str, cells: List[int], episode_ids: List[int], moment: int, path: Union[str, _pl.Path]) -> Dict[str, object]:
    """Appends one belief row to `path` (beliefs.jsonl, append-only — PREREG row 4b: BELIEF clash opens
    never overwrites). Returns the written row, carrying "line" = its own 0-based line index in the
    file — the index a later clash() references when it opens against this row."""
    p = _pl.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    line_no = 0
    if p.exists():
        with open(p) as f:
            line_no = sum(1 for _ in f)
    row: Dict[str, object] = {
        "line": line_no,
        "kind": "belief",
        "word": word,
        "cells": sorted(set(int(c) for c in cells)),
        "episodes": sorted(set(int(e) for e in episode_ids)),
        "moment": int(moment),
    }
    with open(p, "a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def read_beliefs(path: Union[str, _pl.Path]) -> List[Dict[str, object]]:
    """Reads every row of beliefs.jsonl back, in file order — a small, honest extension beyond the
    three named functions (believe/clash/induce/deduce all need a way to read what believe() wrote;
    the file itself is the interface, this is just the obvious reader for it)."""
    p = _pl.Path(path)
    if not p.exists():
        return []
    rows = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


# ============================================================================ CLASH
def clash(new_row: Dict[str, object], old_rows: List[Dict[str, object]], path: Union[str, _pl.Path]) -> Optional[Dict[str, object]]:
    """A clash is two beliefs about the SAME word whose "cells" sets are DISJOINT (decision 3 above).
    On a clash, OPENS a new row (kind "clash") naming both rows' line numbers — appended to `path`,
    never overwriting either belief. Returns that row, or None if no row in `old_rows` clashes with
    `new_row` (including: new_row's own word never appears in old_rows, or every same-word row shares
    at least one cell with it)."""
    conflicting = [
        r for r in old_rows
        if r.get("kind", "belief") == "belief"
        and r.get("word") == new_row.get("word")
        and r.get("line") != new_row.get("line")
        and not (set(r.get("cells", [])) & set(new_row.get("cells", [])))
    ]
    if not conflicting:
        return None
    old = conflicting[0]
    p = _pl.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    line_no = 0
    if p.exists():
        with open(p) as f:
            line_no = sum(1 for _ in f)
    row: Dict[str, object] = {
        "line": line_no,
        "kind": "clash",
        "word": new_row.get("word"),
        "clashes": [old.get("line"), new_row.get("line")],
        "moment": new_row.get("moment"),
    }
    with open(p, "a") as f:
        f.write(json.dumps(row) + "\n")
    return row


# ============================================================================ helpers shared by induce/deduce
def _nearest_sight_cell(org: Organism, x: np.ndarray) -> Optional[int]:
    """The raw-cosine nearest ALIVE sight cell to x — deliberately NOT recall()'s resonance/KWTA path
    (decision 1 above): induce asks "what does the organism's geometry say", not "what would RECALL,
    with its abstain machinery, have answered"."""
    ids = org.sight.alive_ids()
    if len(ids) == 0:
        return None
    cos = org.sight.cells[ids] @ x
    return int(ids[int(np.argmax(cos))])


# ============================================================================ INDUCE
def induce(episodes, k: int, org: Organism) -> List[Dict[str, object]]:
    """PREREG row 4d: INDUCE rule from <n> episodes no counter — a rule W => cluster C when >= k
    episodes agree and none disagrees (decision 1 above). Returns FILE-ready rows (predict.file()'s
    shape: {"accepted", "refused", "row", "outcome"} plus "word"/"cluster"/"agree"/"disagree"). An
    induced rule (agree>=k, disagree==0) is always ROUTABLE — C is non-empty by construction (an empty
    cluster cannot ever accumulate an agreeing episode) — so every row this function emits is accepted;
    the "REFUSED by name" case belongs to deduce() (decision 2)."""
    rules: List[Dict[str, object]] = []
    if episodes is None or len(episodes) == 0:
        return rules
    words_seen = sorted(set(str(episodes.word[i]) for i in range(len(episodes)) if str(episodes.word[i])))
    for word in words_seen:
        r = org.recall("words", world.encode_word(word, org.g.ear_blank_zero))
        word_cell = r["cell"]
        if word_cell is None:
            continue  # the organism itself abstains on this word — nothing to cluster against
        C = sorted(int(c) for c in org.sight.alive_ids() if org._answer_of(org.sight, int(c)) == word_cell)
        agree = disagree = 0
        ep_ids: List[int] = []
        for i in range(len(episodes)):
            if str(episodes.word[i]) != word:
                continue
            nearest = _nearest_sight_cell(org, episodes.x_s[i])
            if nearest is None:
                continue
            if nearest in C:
                agree += 1
                ep_ids.append(int(episodes.ids[i]))
            else:
                disagree += 1
        if agree >= k and disagree == 0 and C:
            row = _file(
                claim=f'"{word}" resonates cluster {C}',
                route=f"recall(sight) on the next episode with word {word!r}",
                decider=f"recall(sight) in cluster {C}",
                due=f"moment {org.t}",
            )
            row["word"] = word
            row["cluster"] = C
            row["agree"] = agree
            row["disagree"] = disagree
            row["episodes"] = ep_ids
            rules.append(row)
    return rules


# ============================================================================ DEDUCE
def deduce(beliefs: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """PREREG row 4d: DEDUCE one step — every pair of belief rows (kind=="belief") is examined once.
    Two beliefs about DIFFERENT words sharing >=1 cell predict a co-resonance, routed at the shared
    cell. Two beliefs about the SAME word with DISJOINT cells (decision 2/3 above) are unroutable — no
    single cell names the route — and are filed with route="", REFUSED BY NAME. Two beliefs about the
    same word with overlapping cells are skipped (one belief, not a deduction target)."""
    belief_rows = [b for b in beliefs if b.get("kind", "belief") == "belief"]
    claims: List[Dict[str, object]] = []
    for i in range(len(belief_rows)):
        for j in range(i + 1, len(belief_rows)):
            a, b = belief_rows[i], belief_rows[j]
            shared = sorted(set(a.get("cells", [])) & set(b.get("cells", [])))
            if a.get("word") != b.get("word"):
                if not shared:
                    continue
                row = _file(
                    claim=f'"{a["word"]}" and "{b["word"]}" co-resonate at cell(s) {shared}',
                    route=f"recall(sight) at cell {shared[0]}",
                    decider=f'both "{a["word"]}" and "{b["word"]}" answer',
                    due=f"belief lines {a.get('line')}/{b.get('line')}",
                )
            else:
                if shared:
                    continue
                row = _file(
                    claim=f'"{a["word"]}" resonates two disjoint clusters ({a.get("cells")} / {b.get("cells")})',
                    route="",  # unroutable: no single cell names "recall answers this word"
                    decider=f'recall(sight) answers "{a["word"]}" from either cluster',
                    due=f"belief lines {a.get('line')}/{b.get('line')}",
                )
            row["words"] = [a.get("word"), b.get("word")]
            claims.append(row)
    return claims
