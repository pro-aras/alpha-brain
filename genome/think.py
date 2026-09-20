"""genome/think.py — B11 (docs/G4-PREREG.md §11.2): THINK's laws. Beliefs (append-only, clash-opening,
never overwriting), and the two one-step reasoning laws: induce (episodes -> a rule) and deduce (beliefs
-> a predicted co-resonance), both FILE-ready (genome/predict.py's file()/FILE_FIELDS law).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — new module, Wave 2 B11.

Interface fixed for Builder A (§11, the coordinator's Wave 2 message, verbatim):
    believe(word, cells, episode_ids, moment, path) -> row       # append-only beliefs.jsonl
    clash(new_row, old_rows, path) -> row|None                   # a clash OPENS a row, never overwrites
    induce(episodes, k, org) -> list[rule]                       # FILE-ready claims
    deduce(beliefs) -> list[claim]                                # one step; FILE-ready

edit: Claude (Sonnet 5, W3 builder B), 2026-09-20 22:44 +0400 — Wave 3, W3-1 (docs/G4-WAVE3-CLAUSES.md,
D-G12 BELIEF DEDUPE): believe()'s interface widened, fixed for Builder A (docs/briefs/W3-BUILDER-B.md,
verbatim):
    believe(word, cells, episode_ids, moment, path, ledgers=None, clash_enabled=True) -> row
        # "kind" in {"belief","revisit","extension","clash"} (+"clash_refused" when clash_enabled=False);
        # "line" = the row's own line number in the file, EXCEPT a revisit, which returns the STANDING
        # row's line (the row it revisits) — a revisit's line on DISK is never written (the minimal
        # {"kind","of","episodes_added","moment"} shape the clause names); the "line" key the function
        # RETURNS is added on top, equal to "of".
    read_beliefs(path, fold=False) -> rows                        # fold=True: one row per word, folded

Four rules (docs/G4-WAVE3-CLAUSES.md W3-1, verbatim law), checked in this order:
    1. No standing belief for the word -> a "belief" row (unchanged from Wave 2).
    2. a ledger reassignment (decision 4 below) or any STANDING cell REMOVED -> a "clash" (rule 4) —
       checked BEFORE the plain set-equality below, so a stream whose cells stay physically the same but
       whose ledger now says they answer another word is never misread as a quiet revisit.
    3. set(cells) == set(standing.cells) -> a "revisit" (rule 2).
    4. cells ADDED, none removed -> an "extension" (rule 3); the extension's full cell set becomes the
       new standing for later calls (a chain: belief -> extension -> extension -> ..., each "of" pointing
       at the PREVIOUS link; "standing" always means the LAST link written for that word).

Four more design decisions this clause adds (the pattern set by decisions 1-3 below: resolve an
ambiguity the clause names but does not spell out to the letter, and write it down — SOLUTIONS
#131/#180):

  4. The ledger check (rule 4's "(when ledgers is given) any of the word's cells now answering ANOTHER
     word — the words-ledger set for the cell != {word}"). `ledgers` is the SAME two-key dict
     `build_ledgers()` already produces (genome/questions.py: {"sight": Ledger, "words": Ledger},
     Ledger = cell -> set of things/words it was born on). believe()'s `cells` are always SIGHT cells
     (mind.py: "a belief carries the word's SIGHT cells"), so "the ledger set for the cell" reads
     `ledgers["sight"][cell]` — exactly the set `questions.why()` already tests against `{word}` when it
     decides which cells belong to a word in the first place. The check runs over the STANDING belief's
     cells (not the freshly-observed ones): a cell that already belonged to the word when the belief was
     formed can still drift to another word later (a merge, a re-birth) while `recall()` keeps resonating
     the SAME physical cell every time — a same-cells stream under a drifted ledger must not read as a
     quiet revisit, which is why this check runs before the plain set-equality check.

  5. clash()'s own law (decision 3, below, unchanged) only ever finds a conflict between two rows whose
     cell sets are DISJOINT, and only ever looks at rows of `kind=="belief"`. Rule 4 itself ("cells
     REMOVED, or a ledger reassignment, -> clash") is UNCONDITIONAL — every entry into that branch ends
     in a clash row — so three cases fall outside clash()'s narrower law and are covered on top of it:
     (a) the STANDING row is an EXTENSION, not a "belief" — clash()'s own `kind=="belief"` filter would
     silently skip it; fixed by never handing clash() the raw standing row, but a one-element "view"
     `{"kind":"belief","word":...,"line":standing_line,"cells":standing_cells}` — same line, same cells,
     kind normalised — so clash()'s law applies whichever kind is CURRENTLY standing. (b) the ledger
     fired with the cells UNCHANGED (decision 4) — two identical cell sets are never disjoint. (c) cells
     were REMOVED but an overlapping remainder survives (standing [1,2,3] -> new [3,4]: 1,2 removed, 3
     kept) — again not disjoint. For (b) and (c), clash() correctly finds no conflict by its own law and
     returns None; believe() does not call clash() a second time or loosen its law, it opens the clash
     row itself, in exactly clash()'s own shape (`_open_clash_direct`), since these are contradiction
     shapes clash()'s cells-disjoint test was never meant to see (its own toy, unchanged, is exactly the
     overlapping-cells case — but as a REASON NOT TO CLASH between two rows compared directly, which is
     still true; rule 4 just does not give believe() the option of walking away from this branch without
     a clash row once it has decided cells were removed or the ledger disagrees). Either way, a genuine
     clash first WRITES the new observation as its own fresh "belief" row (so both sides of "clashes":
     [old_line, new_line] are real, addressable rows on disk — matching Alpha 2's own law: "a
     contradiction opens a clash [naming two rows] and never overwrites"), then opens the clash row
     naming [standing_line, new_belief_line]; believe() returns the CLASH row only (not the belief row
     also written beneath it) — the fixed interface's own words, "return its row with kind clash". One
     consequence, left as observed rather than suppressed: while a ledger keeps reporting the SAME
     drifted label, EVERY subsequent call re-clashes (there is no "settled" state to fall back into) —
     the toy only requires >= 1 clash, and a persistent contradiction genuinely looks like one clash per
     call, not a single event.

  6. `read_beliefs(path, fold=True)`'s handling of a word that clashed: the clash branch's fresh belief
     row starts a brand-new chain (a fork). fold() tracks the LATEST chain only — a plain "belief" row
     for a word already in the fold table RESETS that word's folded entry (dropping the pre-clash
     episode count from the single-row summary). This is a decision, not an oversight: "one standing
     belief per word" (singular) can only ever describe the CURRENT, un-contradicted claim; the
     superseded chain's episodes are not lost — they are still on disk in the raw (fold=False) rows, and
     the clash row itself names both lines — they are simply not merged into the one-row-per-word
     summary.

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


# ============================================================================ BELIEF (W3-1: scoped)
def _line_count(p: _pl.Path) -> int:
    if not p.exists():
        return 0
    with open(p) as f:
        return sum(1 for _ in f)


def _append(p: _pl.Path, row: Dict[str, object]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(row) + "\n")


def _write_belief(p: _pl.Path, word: str, cells: List[int], episode_ids: List[int], moment: int) -> Dict[str, object]:
    row: Dict[str, object] = {
        "line": _line_count(p),
        "kind": "belief",
        "word": word,
        "cells": sorted(set(int(c) for c in cells)),
        "episodes": sorted(set(int(e) for e in episode_ids)),
        "moment": int(moment),
        "clashes": [],  # PREREG §11.2: a belief row carries "clashes" too, so a reader never KeyErrors
                         # on it before any clash has ever opened against this row.
    }
    _append(p, row)
    return row


def _write_revisit(p: _pl.Path, word: str, of_line: int, episode_ids: List[int], moment: int) -> Dict[str, object]:
    """W3-1 rule 2: the standing row is never rewritten; a small row records that it was seen again.
    The file row carries no "line" of its own (the clause's literal minimal shape) — the RETURNED dict
    adds one, equal to `of_line` (interface: "a revisit returns the STANDING row's line")."""
    row: Dict[str, object] = {
        "kind": "revisit",
        "of": int(of_line),
        "word": word,
        "episodes_added": sorted(set(int(e) for e in episode_ids)),
        "moment": int(moment),
    }
    _append(p, row)
    returned = dict(row)
    returned["line"] = int(of_line)
    return returned


def _write_extension(p: _pl.Path, word: str, of_line: int, added: List[int], full_cells: List[int],
                      episode_ids: List[int], moment: int) -> Dict[str, object]:
    """W3-1 rule 3: cells added, none removed. The full new cell set becomes this word's standing for
    later calls (the chain: belief -> extension -> extension -> ...)."""
    row: Dict[str, object] = {
        "line": _line_count(p),
        "kind": "extension",
        "of": int(of_line),
        "word": word,
        "added": sorted(int(c) for c in added),
        "cells": sorted(int(c) for c in full_cells),
        "episodes": sorted(set(int(e) for e in episode_ids)),
        "moment": int(moment),
    }
    _append(p, row)
    return row


def _open_clash_direct(p: _pl.Path, word: str, old_line: int, new_line: int, moment: int) -> Dict[str, object]:
    """The same row SHAPE clash() writes (decision 5 above) for the two contradictions clash()'s own
    cells-disjoint law cannot see on its own: a ledger reassignment with the cell set unchanged, or a
    partial removal that leaves an overlapping remainder. Rule 4 ("cells REMOVED, or a ledger
    reassignment, -> clash") is unconditional — every entry into that branch ends in a clash row, one
    way or the other; this is the "or the other"."""
    row: Dict[str, object] = {
        "line": _line_count(p),
        "kind": "clash",
        "word": word,
        "clashes": sorted([int(old_line), int(new_line)]),
        "moment": int(moment),
    }
    _append(p, row)
    return row


def _standing_row(rows: List[Dict[str, object]], word: str) -> Optional[Dict[str, object]]:
    """The LAST {belief, extension} row for `word` in file order — None if the word has never been
    believed. A "clash" row never becomes standing (decision 6 above: a clash forks the chain; the fresh
    belief written alongside it is what becomes standing next)."""
    standing = None
    for r in rows:
        if r.get("kind", "belief") in ("belief", "extension") and r.get("word") == word:
            standing = r
    return standing


def believe(word: str, cells: List[int], episode_ids: List[int], moment: int, path: Union[str, _pl.Path],
            ledgers: Optional[Dict[str, Dict[int, "set"]]] = None, clash_enabled: bool = True) -> Dict[str, object]:
    """W3-1 (docs/G4-WAVE3-CLAUSES.md, D-G12): one belief per word. Reads the word's standing belief
    first (append-only — PREREG row 4b: BELIEF clash opens, never overwrites) and applies the four rules
    documented at the top of this module. Returns the written row (or, for "clash_refused", a row
    describing what was refused and written nothing)."""
    p = _pl.Path(path)
    prior_rows = read_beliefs(p)
    standing = _standing_row(prior_rows, word)

    new_cells = sorted(set(int(c) for c in cells))
    new_set = set(new_cells)
    new_eps = sorted(set(int(e) for e in episode_ids))

    if standing is None:
        return _write_belief(p, word, new_cells, new_eps, moment)

    standing_cells = set(int(c) for c in standing.get("cells", []))
    standing_line = int(standing["line"])

    ledger_clash = False
    if ledgers is not None:
        sight_ledger = ledgers.get("sight", {})
        ledger_clash = any(sight_ledger.get(c, {word}) != {word} for c in standing_cells)

    removed = standing_cells - new_set

    if ledger_clash or removed:
        if not clash_enabled:
            return {
                "kind": "clash_refused",
                "word": word,
                "cells": new_cells,
                "moment": int(moment),
                "of": standing_line,
                "line": None,
                "reason": "BELIEF gene's clash half is undeclared (clash_enabled=False)",
            }
        new_belief = _write_belief(p, word, new_cells, new_eps, moment)
        standing_view = {"kind": "belief", "word": word, "line": standing_line, "cells": sorted(standing_cells)}
        row = clash(new_belief, [standing_view], p)
        if row is not None:
            return row
        # clash()'s own law is cells-disjoint only (decision 3/5 above): a same-cells ledger
        # reassignment can never be disjoint from itself, and neither can a PARTIAL removal that leaves
        # an overlapping remainder (e.g. standing [1,2,3] -> new [3,4]: 1,2 removed, 3 kept). Rule 4 is
        # unconditional ("cells REMOVED, or a ledger reassignment, -> clash") — every entry into this
        # branch ends in a clash row; believe() opens it directly when clash()'s own narrower law does
        # not fire, in exactly its own shape. (An earlier version of this function returned the plain
        # new belief here instead — a fifth, undeclared "kind" outside the fixed interface, and one that
        # silently forked read_beliefs(fold=True)'s per-word chain for any word with a partial-overlap
        # removal; life 1's replay caught it on "diamond", 69 source rows collapsing to 11 folded.)
        return _open_clash_direct(p, word, standing_line, int(new_belief["line"]), moment)

    if new_set == standing_cells:
        return _write_revisit(p, word, standing_line, new_eps, moment)

    added = new_set - standing_cells  # removed is empty here, so this is exactly rule 3's case
    return _write_extension(p, word, standing_line, sorted(added), new_cells, new_eps, moment)


def read_beliefs(path: Union[str, _pl.Path], fold: bool = False) -> List[Dict[str, object]]:
    """Reads every row of beliefs.jsonl back, in file order — a small, honest extension beyond the
    three named functions (believe/clash/induce/deduce all need a way to read what believe() wrote;
    the file itself is the interface, this is just the obvious reader for it). `fold=True` (W3-1) folds
    revisits and extensions into one standing row per word, with a "revisits"/"extensions"/"clashes"
    count and the union of every episode id ever attached to the word's CURRENT chain (decision 6
    above: a clash forks the chain; fold tracks the latest fork only)."""
    p = _pl.Path(path)
    if not p.exists():
        return []
    rows = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not fold:
        return rows
    return _fold_beliefs(rows)


def _fold_beliefs(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    folded: Dict[str, Dict[str, object]] = {}
    order: List[str] = []
    clash_count: Dict[str, int] = {}
    for r in rows:
        kind = r.get("kind", "belief")
        word = r.get("word")
        if kind == "belief":
            if word not in folded:
                order.append(word)
            folded[word] = {
                "kind": "belief",
                "word": word,
                "line": r["line"],
                "cells": list(r.get("cells", [])),
                "episodes": set(r.get("episodes", [])),
                "revisits": 0,
                "extensions": 0,
                "moment": r.get("moment"),
            }
        elif kind == "extension" and word in folded:
            entry = folded[word]
            entry["cells"] = list(r.get("cells", []))
            entry["episodes"] |= set(r.get("episodes", []))
            entry["extensions"] += 1
            entry["line"] = r["line"]
            entry["moment"] = r.get("moment")
        elif kind == "revisit" and word in folded:
            entry = folded[word]
            entry["episodes"] |= set(r.get("episodes_added", []))
            entry["revisits"] += 1
            entry["moment"] = r.get("moment")
        elif kind == "clash" and word is not None:
            clash_count[word] = clash_count.get(word, 0) + 1
    out = []
    for word in order:
        e = folded[word]
        e["episodes"] = sorted(e["episodes"])
        e["clashes"] = clash_count.get(word, 0)
        out.append(e)
    return out


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
