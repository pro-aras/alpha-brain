# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:31 +0400 — A4L-LANG tasks 4/5 (docs/A4-LADDER-PREREG.md
# §3.2 items 3-5; docs/briefs/A4L-LANG.md): the composer, its judge's back-parse, and the THING-WORD set. Pure readers:
# imported by the mind (creature/mind.py:_consume_chat) and by the reader (tools/verdict_life.py:chat_marks); NO rng,
# NO probability, NO argmax over a vocabulary — never next-token. Ported from the builder's own task-0 instrument
# (scratch/task0/probe_lang.py), which reproduced the designer's M3 readings on the 10:54 snapshot copy.
"""genome/chain.py — sentences as CHAINS of the creature's own frames with ONE pivot slot (A4-LADDER-PREREG §3.2).

A LINK is a landed frame (`genome.sentence.find_frames`: >= 5 co-occurrences in one instant AND > 2x independence)
whose pair was ALSO heard ADJACENT — w2 immediately after w1 in the RAW heard order of `words_in_instant` — in >= `adj`
instants. A PIVOT is a word heard in >= `instants` multi-word instants (>= 2 distinct words, find_frames' own N) and
immediately followed by >= `distinct` distinct words (its right slot is open: Braine's pivot, Tomasello's item-based
frame). CANDIDATES are the simple paths of links ending in a pivot, at most `max_words - 1` words (the slot takes the
last), containing >= 1 word of the question — a single pivot word is a path of zero links. CHOICE, in this order: the
most question words · the pivot with the most distinct followers · the longest · the most adjacency evidence summed
over its links · lexicographic (the path as a tuple of words). The answer is the chosen path + the content in the slot,
or the content alone when no candidate exists. THE FORM IS CHOSEN BEFORE THE CONTENT IS PLACED: `content` is read by
nothing but the last line of `compose`.

THE JUDGE (§3.2 item 5, the songbird's template-then-match) re-derives every claim of a form from the store by its own
scan (`judge_form`), never from the composer's tables: each link a landed frame heard adjacent >= `adj` times (the
instants CITED), the pivot's followers and instants re-counted.

THE THING-WORDS (§3.2 item 3). `thing_words(..., rule="literal")` is the clause as written: a word whose own word cell
has a MEET edge to a sight cell first born on a PICTURE source (maker, folder, game, hands). Measured on alpha4-1's
10:54 snapshot copy (task 0 (c)) it holds 119 words, among them «a is it the or in on do you an» — a shelf glance lights
maker-born cells and MEET wires them to the shelf's words — and every phrasing naming two such words would route its
content through the question's own words (task 0: what-is 60/256, yes-no 128/256 by construction on the builder's own
stress phrasings). `rule="heard"` (THING_WORD_RULE, the default — RAISED in the report as a law refinement, the literal
rule kept as the measured twin) is the literal set INTERSECTED with the words the world said while SHOWING a picture (a
live episode whose `source` is a picture source carries the word in its `words_in_instant`): 30 words, no function
word, all 16 drawn names kept (task 0: 240/256 · 240/256 · echo 0/128 · which 192/192).
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import numpy as np

from genome.sentence import find_frames

PICTURE_SOURCES = ("maker", "folder", "game", "hands")
THING_WORD_RULES = ("literal", "heard")
THING_WORD_RULE = "heard"          # RAISED (A4L-LANG-REPORT.md): the literal §3.2-item-3 clause is the measured twin
COMPOSE_CAP = 10000                # paths visited per compose — a runaway walk on a long life's link graph is #236's shape


# ============================================================================ the store, read once
def instants(episodes) -> List[Tuple[int, List[str]]]:
    """Every LIVE episode's (id, words_in_instant) in id order — find_frames' own ring-wrap-safe walk (ids from
    n_written - cap to n_written; an evicted id reads None and is skipped). Empty words dropped (Episodes.get's own
    convention)."""
    out: List[Tuple[int, List[str]]] = []
    if episodes is None:
        return out
    n_written = int(getattr(episodes, "n_written", len(episodes)))
    cap = int(getattr(episodes, "cap", len(episodes)) or 0)
    lo = max(0, n_written - cap) if cap else 0
    for eid in range(lo, n_written):
        rec = episodes.get(eid)
        if rec is None:
            continue
        words = [w for w in (rec.get("words_in_instant") or []) if w]
        out.append((int(rec["id"]) if "id" in rec else eid, words))
    return out


def store_stats(episodes, rows: Optional[List[Tuple[int, List[str]]]] = None) -> Dict[str, object]:
    """One pass: `adjacency` (w1, w2) -> the ids of the instants in which w2 IMMEDIATELY follows w1 in the raw heard
    order (each instant once); `follow` word -> the set of words that immediately follow it anywhere; `multi` word ->
    the multi-word instants (>= 2 distinct words) it was heard in."""
    rows = rows if rows is not None else instants(episodes)
    adjacency: Dict[Tuple[str, str], List[int]] = {}
    follow: Dict[str, Set[str]] = {}
    multi: Dict[str, int] = {}
    for eid, words in rows:
        distinct = [w for j, w in enumerate(words) if w not in words[:j]]
        if len(distinct) >= 2:
            for w in distinct:
                multi[w] = multi.get(w, 0) + 1
        seen = set()
        for a, b in zip(words, words[1:]):
            follow.setdefault(a, set()).add(b)
            if (a, b) not in seen:
                seen.add((a, b))
                adjacency.setdefault((a, b), []).append(eid)
    return {"rows": rows, "adjacency": adjacency, "follow": follow, "multi": multi}


def links(episodes, adj: int = 5, stats: Optional[Dict[str, object]] = None,
          frames: Optional[List[Dict[str, object]]] = None) -> List[Dict[str, object]]:
    """The LINKS: find_frames' own rows (the SAME call the think step makes) whose pair was heard adjacent in >= `adj`
    instants. Each row: w1, w2, adj_count, adj_episodes (the instants cited), n_episodes (the frame's co-occurrence
    count), episodes (the frame's own episode ids). find_frames' order ((w1, w2) ascending)."""
    stats = stats if stats is not None else store_stats(episodes)
    frames = frames if frames is not None else find_frames(episodes)
    out: List[Dict[str, object]] = []
    for f in frames:
        eps = stats["adjacency"].get((f["w1"], f["w2"]), [])
        if len(eps) >= adj:
            out.append({"w1": f["w1"], "w2": f["w2"], "adj_count": len(eps), "adj_episodes": list(eps),
                        "n_episodes": int(f["count"]), "episodes": list(f["episodes"])})
    return out


def pivots(episodes, distinct: int = 10, instants: int = 20, stats: Optional[Dict[str, object]] = None) -> Dict[str, int]:
    """word -> its distinct-follower count, for every word heard in >= `instants` multi-word instants and immediately
    followed by >= `distinct` distinct words."""
    stats = stats if stats is not None else store_stats(episodes)
    follow, multi = stats["follow"], stats["multi"]
    return {w: len(f) for w, f in sorted(follow.items()) if multi.get(w, 0) >= instants and len(f) >= distinct}


# ============================================================================ the composer
def _pair(l) -> Tuple[str, str]:
    return (str(l["w1"]), str(l["w2"])) if isinstance(l, dict) else (str(l[0]), str(l[1]))


def _count(v) -> int:
    return int(v) if isinstance(v, (int, np.integer)) else len(v)


def compose(question_words: Sequence[str], content: Optional[str], links: Iterable, pivots, follow, adjacency,
            max_words: int = 6, cap: int = COMPOSE_CAP) -> Dict[str, object]:
    """§3.2 item 4, exactly. `links`: link rows (or (w1, w2) pairs); `pivots`: the pivot words (a dict or a set);
    `follow`: word -> its followers (the pivot ranking reads len()); `adjacency`: (w1, w2) -> an instant count or the
    cited instants (the evidence sum reads the count). Returns {answer, form, pivot, candidates_n, paths_n, truncated}:
    `answer` None when `content` is None (the form is still chosen and recorded — content-independent by construction).
    The walk is an iterative DFS in sorted order, capped at `cap` visited paths (`truncated` says so)."""
    q = set(w for w in question_words if w)
    graph: Dict[str, List[str]] = {}
    for l in links:
        a, b = _pair(l)
        graph.setdefault(a, []).append(b)
    for a in graph:
        graph[a] = sorted(set(graph[a]))
    piv = set(pivots)
    nodes = sorted(set(graph) | {b for bs in graph.values() for b in bs} | piv)
    max_path = max(1, int(max_words) - 1)
    stack: List[List[str]] = [[n] for n in reversed(nodes)]
    cands: List[Tuple[str, ...]] = []
    paths_n = 0; truncated = False
    while stack:
        if paths_n >= cap:
            truncated = True
            break
        p = stack.pop(); paths_n += 1
        if p[-1] in piv and (q & set(p)):
            cands.append(tuple(p))
        if len(p) < max_path:
            for nb in reversed(graph.get(p[-1], [])):
                if nb not in p:
                    stack.append(p + [nb])
    base = {"candidates_n": len(cands), "paths_n": paths_n, "truncated": truncated}
    if not cands:
        return {"answer": ([content] if content is not None else None), "form": [], "pivot": None, **base}

    def key(p: Tuple[str, ...]):
        return (-len(q & set(p)), -len(follow.get(p[-1], ())), -len(p),
                -sum(_count(adjacency.get((a, b), 0)) for a, b in zip(p, p[1:])), p)

    best = min(cands, key=key)
    return {"answer": (list(best) + [content] if content is not None else None), "form": list(best), "pivot": best[-1], **base}


# ============================================================================ the judge's back-parse
def judge_form(form: Sequence[str], episodes, adj: int = 5, distinct: int = 10, instants: int = 20,
               rows: Optional[List[Tuple[int, List[str]]]] = None, frames: Optional[List[Dict[str, object]]] = None) -> Dict[str, object]:
    """§3.2 item 5: re-derive every claim of `form` from the store by its OWN scan (never the composer's tables): each
    consecutive pair a landed frame heard adjacent in >= `adj` instants (their ids CITED), the last word a pivot (its
    followers and multi-word instants re-counted). The empty form (the content alone) passes. Returns {ok, reason,
    links: [[w1, w2, adj_count, n_episodes]], cited: [[instant ids] per link], pivot_followers, pivot_instants}."""
    out: Dict[str, object] = {"ok": True, "reason": None, "links": [], "cited": [], "pivot_followers": None, "pivot_instants": None}
    if not form:
        return out
    rows = rows if rows is not None else globals()["instants"](episodes)
    frames = frames if frames is not None else find_frames(episodes)
    fset = {(f["w1"], f["w2"]): f for f in frames}
    for a, b in zip(form, form[1:]):
        eps = [eid for eid, w in rows if any(w[i] == a and w[i + 1] == b for i in range(len(w) - 1))]
        f = fset.get((a, b))
        if f is None:
            return {**out, "ok": False, "reason": f"link «{a} {b}»: not a landed frame"}
        if len(eps) < adj:
            return {**out, "ok": False, "reason": f"link «{a} {b}»: heard adjacent in {len(eps)} instants < {adj}"}
        out["links"].append([a, b, len(eps), int(f["count"])]); out["cited"].append(eps)
    pivot = form[-1]
    followers = {w[i + 1] for _eid, w in rows for i in range(len(w) - 1) if w[i] == pivot}
    inst = sum(1 for _eid, w in rows if pivot in w and len(set(w)) >= 2)
    out["pivot_followers"], out["pivot_instants"] = len(followers), inst
    if len(followers) < distinct or inst < instants:
        return {**out, "ok": False, "reason": f"pivot «{pivot}»: {len(followers)} followers / {inst} instants < {distinct} / {instants}"}
    return out


# ============================================================================ the THING-WORDS (§3.2 item 3)
def birth_sources(births: Sequence[Tuple[int, str, int, str]], episodes, per_canvas: int) -> Dict[int, str]:
    """sight cell -> the source of the canvas it was FIRST born on: the live episode whose own glance moments
    [moment, moment + per_canvas) — bounded by the next episode's moment — contain the birth moment; a birth at a moment
    no canvas owns (a SLEEP replay) reads "sleep", one before the ring's oldest live episode "?". Verified on the hour-1
    fixture against the journal's own `source`: 1,745 of 1,745 sight cells agree (task 0)."""
    if episodes is None:
        return {}
    n = len(episodes)
    if n == 0:
        return {}
    ids = np.asarray(episodes.ids[:n]); live = ids >= 0
    starts = np.asarray(episodes.moment[:n], dtype=np.int64)[live]
    srcs = np.asarray([str(s) for s in episodes.source[:n]], dtype=object)[live]
    order = np.argsort(starts, kind="stable"); starts, srcs = starts[order], srcs[order]
    out: Dict[int, str] = {}
    for m, area, cid, _reason in births:
        if area != "sight" or int(cid) in out:
            continue
        i = int(np.searchsorted(starts, int(m), side="right")) - 1
        if i < 0:
            out[int(cid)] = "?"
            continue
        end = starts[i] + int(per_canvas)
        if i + 1 < len(starts):
            end = min(end, int(starts[i + 1]))
        out[int(cid)] = str(srcs[i]) if int(m) < end else "sleep"
    return out


def heard_on_pictures(episodes) -> Set[str]:
    """Every word a live episode with a PICTURE source carries in its `words_in_instant` — what the world said while
    SHOWING a picture."""
    out: Set[str] = set()
    if episodes is None:
        return out
    n = len(episodes)
    for i in range(n):
        if int(episodes.ids[i]) < 0 or str(episodes.source[i]) not in PICTURE_SOURCES:
            continue
        for w in str(episodes.words_in_instant[i]).split("|"):
            if w:
                out.add(w)
    return out


def thing_words(org, ledger_words: Dict[int, Set[str]], episodes, per_canvas: int, rule: str = THING_WORD_RULE) -> Set[str]:
    """§3.2 item 3's THING-WORDS under `rule`: "literal" — a word whose own word cell (ledger {word}, alive) has a MEET
    edge (mask 1) to a sight cell first born on a picture source; "heard" (the default, RAISED) — the literal set
    intersected with `heard_on_pictures`. Read-only on the organism and the store."""
    if rule not in THING_WORD_RULES:
        raise ValueError(f"thing_words: unknown rule {rule!r} (one of {THING_WORD_RULES})")
    ns, nw = int(org.sight.n), int(org.words.n)
    if ns == 0 or nw == 0:
        return set()
    bsrc = birth_sources(org.births, episodes, per_canvas)
    pic = np.array([bsrc.get(s) in PICTURE_SOURCES for s in range(ns)], dtype=bool)
    if not pic.any():
        return set()
    wired = (org.mask[:ns, :nw][pic] == 1).any(axis=0)
    alive_w = org.words.alive[:nw] == 1
    out: Set[str] = set()
    for t in np.flatnonzero(wired & alive_w):
        ws = ledger_words.get(int(t), set())
        if len(ws) == 1:
            w = next(iter(ws))
            if w:
                out.add(w)
    if rule == "heard":
        out &= heard_on_pictures(episodes)
    return out
