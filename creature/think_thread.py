# edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 20:43 +0400 — L-5 (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4
# L-5; docs/briefs/LIFE-E-THINK-THREAD.md; docs/G4-PREREG.md §19.2): THE THINKING THREAD.
"""creature/think_thread.py — the think thread itself: a bounded, READ-ONLY "frozen copy" of what one
THINK step reads, and a pure `decide()` that computes a RESULT (the item worked, its outcome, and every
write it would make, as DATA) without ever touching the live organism/episodes/park/interests or writing
a file, a journal row, or an organism moment. The ONE-WRITER law (SOLUTIONS #232): this module's functions
write NOTHING; creature/mind.py APPLIES the decision on its own thread at the next boundary.

This file is NOT bound by creature/mind.py's no-clock determinism law (that law binds mind.py alone,
enforced by tests/creature/test_mind_parity.py::test_mind_has_no_clock, an AST sweep over mind.py only) —
`time`/`threading`/`concurrent.futures` are used here to run the work on a real OS thread and time it.
The TIMING NUMBER (think_ms) is computed here and handed back to the mind as a plain float inside the
result dict; creature/mind.py never calls time.* itself, it only does arithmetic (median/last) on numbers
this module already measured — no clock is read from creature/mind.py.

The "frozen copy" (FrozenThinkInputs): a shadow Organism whose W/mask are SLICED to the alive-cell range
actually in use (`org.sight.n x org.words.n`, not the full NMAX x NMAX allocation — NMAX=6000 in
LIFE.genome would make a full W/mask copy ~324MB; the sliced copy is bounded by how many cells and words
are alive, the same "alive sight cells matrix + answer map" scope PREREG names, generalised to the couple
of extra arrays (W, mask, births, merges) `genome.questions.build_ledgers`/`why` and `Organism.recall_many`
need to answer the SAME question `_think_work`'s "word"/"self" branches ask today) — a deep copy of the
FAST episodes ring and (when present) the outcome/reflex ring, a copy of `Mind.moment_word`, and a
boundary-local rng seeded from (SEED, N) (the mind's other rng streams — self._think_rng, CURIOSITY's,
PARK's — are UNTOUCHED by a threaded think; PREREG's own words). The shadow Organism is duck-typed against
`genome.machinery.Organism`/`Area` closely enough that the REAL `Organism.recall_many`/`Organism.recall`
and `genome.questions.build_ledgers`/`why` run UNCHANGED against it (called unbound) — this is deliberate:
reusing the tested, live recall/ledger algorithm verbatim is the only way to guarantee the threaded road's
decision is IDENTICAL in content to what the inline road would have decided at the same boundary (item 3's
shift-equivalence gate), rather than a hand-rolled approximation that could silently disagree with it.

RAISED (not built): a fifth think-writer this brief did not have on its tree at write time — builder F's
"hands" pool kind (creature/mind.py's `_think_work` "hands" branch, life-hands, writes `run/hands/ACT`
directly from inside think, using a mind-local `_hands_rng`) — see this module's `decide()` docstring and
LIFE-E-REPORT.md for the fold-in shape a merge needs to give it: a `{"hands_act": {...}}` plan entry
applied by `Mind._think_apply`, and its rng draw moved onto THIS module's own boundary-local `think_rng`
(never a mind-local rng mutated from a background thread — that would be a second writer of mind state,
and a rng any thread can advance is not reproducible under replay).
"""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from genome.machinery import Area, Organism
from genome.questions import build_ledgers, why as questions_why
from genome.world import encode_word

try:
    from genome import think as think_laws
    _THINK_LAWS_AVAILABLE = True
except ImportError:                    # pragma: no cover — mirrors creature/mind.py's own defensive import
    think_laws = None                  # type: ignore[assignment]
    _THINK_LAWS_AVAILABLE = False


# ============================================================================ the frozen copy
def _freeze_area(area: Area, n: int) -> Area:
    """A shadow Area, sliced to `n` (the LIVE cell count at freeze time) on every per-cell array — never
    the full NMAX allocation. `nmax` on the shadow is set to `n` too: nothing this module calls reads
    `.nmax` on the recall path (only `.n`-sliced arrays and `.n` itself), so shrinking it is safe and
    keeps `alive_ids()`/`cos()` (which both slice by `.n`) trivially consistent with the copied arrays'
    own shape."""
    shadow = object.__new__(Area)
    shadow.name, shadow.dim, shadow.nmax = area.name, area.dim, n
    shadow.cells = area.cells[:n].copy()
    shadow.alive = area.alive[:n].copy()
    shadow.misfires = area.misfires[:n].copy()
    shadow.n = n
    shadow.traits = None                # TRAITS is #OFF on LIFE.genome; a shadow never carries a live head reference
    shadow._traits_cache_version = None
    shadow._traits_cache_n = None
    shadow._traits_cache_Hc = None
    shadow.own_band = area.own_band[:n].copy() if area.own_band is not None else None
    shadow.own_band_n = area.own_band_n[:n].copy() if area.own_band_n is not None else None
    return shadow


def freeze_recall_view(org: Organism) -> Organism:
    """A shadow Organism carrying ONLY what `Organism.recall`/`recall_many` and `genome.questions.
    build_ledgers`/`why` read: W and mask SLICED to (sight.n, words.n) — bounded by how many cells are
    alive, not by NMAX — the two Areas (also sliced), the genome `g` (SHARED, never mutated after parse,
    safe to share across threads), and `births`/`merges` (plain lists, copied whole — bounded by total
    births so far, not by NMAX^2). Never changes the live organism; called on the MIND's own thread, once
    per THINK boundary, before the frozen copy is handed to the think thread."""
    n_s, n_w = org.sight.n, org.words.n
    shadow = object.__new__(Organism)
    shadow.g = org.g
    shadow.W = org.W[:n_s, :n_w].copy()
    shadow.mask = org.mask[:n_s, :n_w].copy()
    shadow.sight = _freeze_area(org.sight, n_s)
    shadow.words = _freeze_area(org.words, n_w)
    shadow.births = list(org.births)
    shadow.merges = list(org.merges)
    return shadow


@dataclass
class FrozenThinkInputs:
    """Everything a think reads, frozen at boundary N (PREREG §19.2/plan §4 L-5's own list): the alive
    sight cells matrix + the answer map are IMPLICIT in `shadow_org` (its W/mask/sight/words already ARE
    that scope — see `freeze_recall_view`'s docstring), the FAST ring's used slice is `episodes` (a deep
    copy), the outcome/reflex ring's slice is `outcome_episodes`, the parked ledger is `park_state`
    (captured for interface completeness / a future decide() that needs it — this brief's decide() never
    reads it: PARK's own filtering already ran live during pool-building, and the parking VERDICT itself
    is an ordered write, decided at apply time, never here — see `decide()`'s module docstring), the pool
    computed at N is `item` (the ALREADY-CHOSEN item only — `_think_choose` runs live, synchronously, on
    the mind's own thread, since it is cheap and mutates `self.interests`, a live write; only the CHOSEN
    item's own, potentially-expensive WORK is handed to this thread), and the think rng of its own is
    `rng`, seeded from (SEED, N) — never `self._think_rng` (the mind's other, cross-boundary stream)."""
    item: Dict[str, object]
    shadow_org: Optional[Organism]
    episodes: Any                       # a deep copy of Mind.episodes (genome.fast.Episodes), or None
    outcome_episodes: Any               # a deep copy of Mind.outcome_episodes, or None
    moment_word: Dict[int, str]
    park_state: Dict[str, object]       # {"parked": {...}, "counts": {...}} — see FrozenThinkInputs docstring
    declared: Dict[str, dict]           # genome.declared — SHARED (read-only after parse, never mutated)
    ear_blank_zero: bool
    frozen_t: int                       # org.t at boundary N (NOT the live, advanced t at apply time)
    rng: np.random.Generator
    boundary: int                       # the canvas index N this copy was frozen at


def freeze_inputs(mind: "object", item: Dict[str, object], boundary: int) -> FrozenThinkInputs:
    """Built on the MIND's own thread (never the think thread) — every field is a COPY or an immutable
    shared reference (`declared`, `g` inside the shadow org), so the think thread that receives this can
    touch none of the live mind's mutable state (the `is not` test this brief's writer-sweep control
    pins). `mind` is duck-typed (creature.mind.Mind) rather than imported by type to avoid a cycle."""
    shadow_org = freeze_recall_view(mind.org) if item.get("kind") in ("word", "self") else None
    episodes_copy = copy.deepcopy(mind.episodes) if mind.episodes is not None else None
    outcome_copy = copy.deepcopy(mind.outcome_episodes) if item.get("kind") == "outcome" and mind.outcome_episodes is not None else None
    park_state = {"parked": dict(mind.park._parked), "counts": dict(mind.park._counts)} if mind.park is not None else {"parked": {}, "counts": {}}
    return FrozenThinkInputs(
        item=item, shadow_org=shadow_org, episodes=episodes_copy, outcome_episodes=outcome_copy,
        moment_word=dict(mind.moment_word), park_state=park_state, declared=mind.genome.declared,
        ear_blank_zero=mind.genome.ear_blank_zero, frozen_t=mind.org.t,
        rng=np.random.default_rng([int(mind.genome.seed), 0x7448494e4b, int(boundary)]),   # "tHINK"-ish + boundary, distinct per boundary
        boundary=boundary,
    )


# ============================================================================ SELF's pure trigger (mirrors creature/mind.py:Mind._self_trigger)
_SELF_STALL_KEYS = ("moments", "births", "arrivals")


def self_trigger(r1: Dict[str, object], r2: Dict[str, object]) -> Optional[str]:
    """A verbatim copy of `Mind._self_trigger` (LIFE-A-ANSWER-SELF.md #3) — duplicated rather than called
    unbound because it is eight lines, pure, reads only its two arguments and a class-level tuple, and
    keeping it here means `decide()`'s "self" branch needs no live Mind reference at all, not even for
    this one class attribute. If `Mind._self_trigger`'s law ever changes, this copy must change with it —
    named in the report as a duplication to watch, not hidden.

    edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:41 +0400 — ALPHA4-G.md task 5: kept in sync
    with `Mind._self_trigger`'s own edit, same day — the "self:no_budget" branch (`refused`, checked
    after no_room, same reasoning: exactly one word even when both rise together)."""
    stalled = [k for k in _SELF_STALL_KEYS if r1.get(k) is not None and r2.get(k) is not None and r1[k] == r2[k]]
    moved = [k for k in _SELF_STALL_KEYS if r1.get(k) is not None and r2.get(k) is not None and r1[k] != r2[k]]
    if stalled and moved:
        return f"self:{stalled[0]}_stopped"
    n1, n2 = r1.get("refused_nmax"), r2.get("refused_nmax")
    if n1 is not None and n2 is not None and n2 > n1:
        return "self:no_room"
    b1, b2 = r1.get("refused"), r2.get("refused")
    if b1 is not None and b2 is not None and b2 > b1:
        return "self:no_budget"
    return None


# ============================================================================ decide()
def decide(frozen: FrozenThinkInputs) -> Dict[str, object]:
    """The pure decision: works `frozen.item`, returns a PLAN — never writes a file, a journal row, an
    organism moment, or mutates anything `frozen` did not already own a private copy of. The plan's shape
    is a small tagged dict `Mind._think_apply` (creature/mind.py) knows how to perform for real:
      {"dead_end": {"want", "reason", "ask": {"form": "what-is"|"is", "args": [...], "why_word": str|None}|None}}
      {"believe": {"word", "cells": [...], "episode_ids": [...], "moment": int}}
      {"file_predict": {"claim", "route", "decider", "due", "target_word", "due_canvas"}}
      {"file_rule": {"row", "want", "op"}}
      {"file_frame": {"w1", "w2", "key", "episodes_cited": [...]}}
      {"reflected": {"act", "residual"}}
      {"not_yet_due": True}
      {"no_change": True}
    Every kind's OWN dead-end reason strings are the exact ones `Mind._think_work` uses today (episode_gone,
    no_cell_answers, no_belief_gene, no_route, no_file_gene, think_laws_unavailable, unknown_kind) so a
    reader of the journal cannot tell threaded from inline by the vocabulary alone — only by `launched_at`.

    A "hands" item (builder F's, not on this tree at write time — see the module docstring) is not a kind
    this function recognises; it falls into `unknown_kind` until the merge adds a branch here returning
    `{"hands_act": {...}}`, with the program choice drawn from `frozen.rng` (never a mind-local rng)."""
    item = frozen.item
    kind = str(item.get("kind"))
    declared = frozen.declared

    if kind == "word":
        word = str(item["key"])
        if not _THINK_LAWS_AVAILABLE:
            return {"dead_end": {"want": word, "reason": "think_laws_unavailable", "ask": {"form": "what-is", "args_word": word}}}
        rec = frozen.episodes.get(item["episode"]) if frozen.episodes is not None else None
        if rec is None:
            return {"dead_end": {"want": word, "reason": "episode_gone", "ask": {"form": "what-is", "args_word": word}}}
        ledgers = build_ledgers(frozen.shadow_org, frozen.moment_word)
        record = questions_why(frozen.shadow_org, ledgers, frozen.episodes, word)
        xs = _recent_word_glances(frozen.episodes, word, 5, fallback=rec["x_s"])
        r = frozen.shadow_org.recall_many("sight", xs)
        if r.get("cell") is None:
            return {"dead_end": {"want": word, "reason": "no_cell_answers", "ask": {"form": "what-is", "args_word": word}}}
        if "BELIEF" not in declared:
            return {"dead_end": {"want": word, "reason": "no_belief_gene", "ask": {"form": "what-is", "args_word": word}}}
        sight_cells = [int(c) for area, c in record["cells"] if area == "sight"]
        return {"believe": {"word": word, "cells": sight_cells, "episode_ids": list(record["episodes"]), "moment": frozen.frozen_t}}

    if kind == "sight":
        rec = frozen.episodes.get(item["episode"]) if frozen.episodes is not None else None
        if rec is None:
            return {"dead_end": {"want": str(item["key"]), "reason": "episode_gone", "ask": None}}
        tape_moment = rec.get("tape_moment")
        candidates = frozen.episodes.nearest(rec["x_s"], 10)
        nearest_word = None
        for eid, _cos in candidates:
            other = frozen.episodes.get(eid)
            if other is not None and other["word"]:
                nearest_word = other["word"]
                break
        if nearest_word is None:
            return {"dead_end": {"want": str(item["key"]), "reason": "no_route",
                                  "ask": ({"form": "what-is", "args_tape_moment": tape_moment} if tape_moment else None)}}
        if "FILE" not in declared:
            return {"dead_end": {"want": str(item["key"]), "reason": "no_file_gene", "ask": None}}
        return {"file_predict": {
            "claim": f"the next showing of this sight resonates {nearest_word}'s cells",
            "route": "the journal's err/recall on the next canvas with that word",
            "decider": "recall == word", "due": "the next showing",
            "target_word": nearest_word, "due_canvas": frozen.boundary + 1,
        }}

    if kind == "due":
        return {"not_yet_due": True}

    if kind == "rule":
        op, key = str(item.get("op")), str(item.get("key"))
        want = f"{op}:{key}"
        if "FILE" not in declared:
            return {"dead_end": {"want": want, "reason": "no_file_gene", "ask": None}}
        row = item.get("pred")
        if row is None:
            return {"dead_end": {"want": want, "reason": "no_route", "ask": None}}
        return {"file_rule": {"row": row, "want": want, "op": op}}

    if kind == "frame":
        frame_row = item.get("pred") or {}
        w1, w2 = str(frame_row.get("w1")), str(frame_row.get("w2"))
        key = str(item.get("key"))
        want = f"frame:{key}"
        if "FILE" not in declared:
            return {"dead_end": {"want": want, "reason": "no_file_gene", "ask": None}}
        episodes_cited = [int(e) for e in (frame_row.get("episodes") or [])]
        return {"file_frame": {"w1": w1, "w2": w2, "key": key, "episodes_cited": episodes_cited}}

    if kind == "outcome":
        rec = frozen.outcome_episodes.get(item["episode"]) if frozen.outcome_episodes is not None else None
        if rec is None:
            return {"dead_end": {"want": str(item["key"]), "reason": "episode_gone", "ask": None}}
        return {"reflected": {"act": rec["word"], "residual": float(rec["surprise"])}}

    if kind == "self":
        body_pair = item.get("body_pair")           # [(seq1, r1), (seq2, r2)] — carried on the item by Mind's synchronous prepare step
        (seq1, r1), (seq2, r2) = body_pair[-2], body_pair[-1]
        word = self_trigger(r1, r2)
        if word is None:
            return {"no_change": True}
        if not _THINK_LAWS_AVAILABLE:
            return {"dead_end": {"want": word, "reason": "think_laws_unavailable", "ask": None}}
        if "BELIEF" not in declared:
            return {"dead_end": {"want": word, "reason": "no_belief_gene", "ask": None}}
        return {"believe": {"word": word, "cells": [], "episode_ids": [seq1, seq2], "moment": frozen.frozen_t}}

    return {"dead_end": {"want": str(item.get("key")), "reason": "unknown_kind", "ask": None}}


def _recent_word_glances(episodes, word: str, n: int, fallback) -> list:
    """A verbatim copy of `Mind._recent_word_glances`, against a COPIED (not live) Episodes ring."""
    if episodes is None:
        return [fallback]
    live = np.flatnonzero((episodes.ids >= 0) & (episodes.word == word))
    if live.size == 0:
        return [fallback]
    order = live[np.argsort(episodes.moment[live], kind="stable")][-n:]
    return [episodes.x_s[i].copy() for i in order]


def wait_for(future) -> Dict[str, object]:
    """Blocks on `future.result()`, timing the block — called from `Mind._think_apply_pending` (creature/
    mind.py), which decides WHETHER a wait happened at all via `future.done()` (a plain state check, not a
    clock read) before calling this; this function always measures a `wait_ms` (near-zero when the future
    was already done), so the caller's own `if not was_done:` gate is what actually counts a "wait" for
    PREREG §19.2's `think_waits` mark — this function never decides that itself, it only measures."""
    t0 = time.perf_counter()
    result = future.result()
    wait_ms = (time.perf_counter() - t0) * 1000.0
    return {"result": result, "wait_ms": wait_ms}


def worker_run(frozen: FrozenThinkInputs) -> Dict[str, object]:
    """Runs ON THE THINK THREAD: times `decide()`, catches any exception (item 2: "a think that raises is
    journaled as think.outcome: 'error' with the repr and never kills the mind") and returns a plain,
    JSON-safe-ish result dict `Mind._think_apply` reads. `think_ms` is measured HERE (this module may
    import time; creature/mind.py never does) and handed back as a float — the mind only ever does
    arithmetic on it."""
    t0 = time.perf_counter()
    try:
        plan = decide(frozen)
        error = None
    except Exception as e:                    # noqa: BLE001 — a think's own exception must never propagate to the executor/mind thread
        plan = {"error": repr(e)}
        error = repr(e)
    think_ms = (time.perf_counter() - t0) * 1000.0
    return {"boundary": frozen.boundary, "item": frozen.item, "plan": plan, "error": error, "think_ms": think_ms}
