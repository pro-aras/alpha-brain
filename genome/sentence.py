# edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:4x +0400 — L-11 (docs/briefs/LIFE-C-QUESTION-SENTENCE.md
# task 3; NEXT-LIFE-PLAN-2026-09-22.md §4 L-11): SENTENCE's frame-finder. A frame is an ORDERED pair
# (w1, w2) that met in ONE instant (the same episode's `words_in_instant`, genome/fast.py) in >= min_count
# episodes AND whose count exceeds `factor` x the count expected under independence. Pure function over an
# Episodes store (or any object exposing the same len()/get(i) shape) -- never touches the organism, never
# writes anything; genome/think.py's induce()/deduce() are this module's siblings, same law (a pure reader
# over episodes/beliefs, FILE-ready output), kept in a separate file because SENTENCE's own toy (a
# synthetic mission corpus, no Organism at all) never needs `genome.machinery.Organism`.
"""genome/sentence.py — SENTENCE: two-word frames from co-occurring words, judged by the eye, never
next-token (his 09-03/09-12 words; MIND-THINKING-LANGUAGE.md §4.7's own refusal of the OLD "is near"
condition, replaced here by the co-occurrence definition NEXT-LIFE-PLAN-2026-09-22.md §4 L-11 names).

RAISED, not worked around (from the plan's own §4 L-11 reading, confirmed against the live game rung):
under a UNIFORM mission distribution (every (colour, object) pair equally likely -- which is what
BabyAI-GoToLocal's own `--seed` schedule draws from, unweighted), every ordered pair's observed count sits
at ~1x its expected count under independence, so `count > factor * expected` cannot fire by construction
(#228 (b)'s class: a bar the mechanism's own input distribution cannot clear). A frame is only inducible
when the (colour, object) pairing is itself SKEWED -- e.g. a game world that draws "red" beside "ball"
more often than chance. Nobody has measured G5-L's own babyai-gotolocal draw for skew; the toy below
constructs a deliberately skewed corpus (matching the plan's own worked example, "red ball"/"blue key") to
prove the STATISTIC is right, not that the live game world will ever feed it enough skew to fire. The 24 h
mark's own ceiling ("frames filed >= 3 by 24h") is therefore conditional on a fact about the game world
this builder did not measure -- see the report.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple


def find_frames(episodes, min_count: int = 5, factor: float = 2.0) -> List[Dict[str, object]]:
    """PREREG-style pure function (L-11 task 3): reads every live episode's `words_in_instant`, counts
    ordered-pair co-occurrence over the episodes carrying >= 2 DISTINCT words (N below; "over the episodes
    with >= 2 words", the plan's own text) -- for each such episode, every ORDERED pair (w1, w2) with w1
    before w2 in the list (today: colour before object, game.py's own publish order). Returns one row per
    pair clearing BOTH bars: count(w1, w2) >= min_count AND count(w1, w2) > factor * count(w1)*count(w2)/N
    (the independence expectation). Each row carries `episodes`: the ids of every qualifying episode
    (evidence a said frame must cite, G-MOT-6's gate). Deterministic order: by (w1, w2) ascending, so two
    calls over the same store agree byte-for-byte."""
    N = 0
    marginal: Dict[str, int] = {}
    joint: Dict[Tuple[str, str], int] = {}
    joint_eps: Dict[Tuple[str, str], List[int]] = {}
    if episodes is not None:
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — advisor-caught RING-WRAP bug:
        # `.get(eid)` takes an EPISODE ID (mapped through `_id_to_slot`), not a slot index, so once the
        # ring has wrapped (n_written > cap) the ids 0..cap-1 this loop used to ask for are exactly the
        # DEAD ones (evicted, `.get()` returns None) while every LIVE id (n_written-cap .. n_written-1) was
        # never visited -- find_frames() would go silently dead the moment a long life's FAST ring wrapped
        # (LIFE.genome's FAST is 20000; the game rungs ran ~30k rows in 8h), with nothing on STATUS saying
        # so. genome/think.py's induce() avoids this by iterating SLOTS directly (`episodes.word[i]`); here
        # we iterate the correct ID range instead, since find_frames reads via the public `.get()` API.
        # Verified by tests.genome.test_sentence.TestFindFramesRingWrap (cap=3, 6 writes, only the last 3
        # counted -- the old range(len(episodes)) code finds nothing on that fixture).
        n_written = int(getattr(episodes, "n_written", len(episodes)))
        cap = int(getattr(episodes, "cap", len(episodes)) or 0)
        lo = max(0, n_written - cap) if cap else 0
        for eid in range(lo, n_written):
            rec = episodes.get(eid)
            if rec is None:
                continue
            words = rec.get("words_in_instant") or []
            distinct = [w for j, w in enumerate(words) if w and w not in words[:j]]
            if len(distinct) < 2:
                continue
            N += 1
            for w in distinct:
                marginal[w] = marginal.get(w, 0) + 1
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:0x +0400 — "ordered" means TEMPORAL
            # order (the sequence words_in_instant preserves, colour before object -- game.py's own
            # publish order), never every permutation: only pairs (distinct[a], distinct[b]) with a < b
            # are counted. Counting BOTH (w1,w2) and (w2,w1) would make them PERFECTLY correlated (same
            # episode set, identical counts every time for a 2-word instant) and a precision toy could
            # never exceed 0.5 by construction -- caught by this file's own test_ordered_not_symmetric.
            for a in range(len(distinct)):
                for b in range(a + 1, len(distinct)):
                    key = (distinct[a], distinct[b])
                    joint[key] = joint.get(key, 0) + 1
                    joint_eps.setdefault(key, []).append(int(rec["id"]) if "id" in rec else eid)
    rows: List[Dict[str, object]] = []
    if N == 0:
        return rows
    for (w1, w2), count in sorted(joint.items()):
        expected = (marginal.get(w1, 0) * marginal.get(w2, 0)) / N
        if count >= min_count and (expected == 0 or count > factor * expected):
            rows.append({
                "w1": w1, "w2": w2, "count": count, "expected": expected, "N": N,
                "episodes": sorted(set(joint_eps.get((w1, w2), []))),
            })
    return rows


# ============================================================================ the toy corpus (report's precision toy)
def synthetic_missions(rng, n: int = 50, skew_pairs: Optional[Sequence[Tuple[str, str]]] = None,
                        skew_share: float = 0.6, colours=("red", "blue", "green"), objects=("ball", "key", "box")):
    """L-11's own toy corpus: `n` synthetic (colour, object) missions over the plan's own 3x3 vocabulary.
    `skew_share` of the draws are one of `skew_pairs` (uniform among them); the rest are uniform over every
    OTHER (colour, object) pair -- so the corpus is deliberately skewed toward `skew_pairs` (the plan's own
    worked example: "red ball" and "blue key"), never toward the ones NOT named. A `skew_pairs=None`/empty
    corpus is uniform (every pair equally likely) -- the RAISED clause's own demonstration that
    `find_frames` files nothing there."""
    all_pairs = [(c, o) for c in colours for o in objects]
    skew_pairs = list(skew_pairs or [])
    other_pairs = [p for p in all_pairs if p not in skew_pairs]
    out: List[Tuple[str, str]] = []
    for _ in range(n):
        if skew_pairs and rng.random() < skew_share:
            out.append(skew_pairs[rng.integers(0, len(skew_pairs))])
        else:
            pool = other_pairs if other_pairs else all_pairs
            out.append(pool[rng.integers(0, len(pool))])
    return out


class _FakeEpisode:
    """A minimal stand-in for genome.fast.Episodes' `.get(eid)` + `n_written`/`cap` shape -- only what
    find_frames() reads, so the toy needs no real Episodes ring or Organism at all. `cap` (default: no
    eviction, i.e. cap == len(rows)) simulates the ring: an id below `n_written - cap` is EVICTED (`.get()`
    returns None, exactly genome.fast.Episodes' own "no longer live" contract), matching real behaviour
    closely enough for find_frames()'s own ring-wrap regression test."""

    def __init__(self, rows: List[Dict[str, object]], cap: Optional[int] = None):
        self._rows = rows
        self.n_written = len(rows)
        self.cap = cap if cap is not None else len(rows)

    def __len__(self) -> int:
        return min(self.n_written, self.cap) if self.cap else 0

    def get(self, eid: int) -> Optional[Dict[str, object]]:
        if eid < 0 or eid >= self.n_written:
            return None
        if eid < self.n_written - self.cap:   # evicted by the ring
            return None
        return self._rows[eid]


def episodes_from_missions(missions: Sequence[Tuple[str, str]]) -> "_FakeEpisode":
    """Wraps a (colour, object) mission list as the `words_in_instant` shape find_frames() reads, one
    'episode' per mission, ids 0..n-1 (game.py's own publish order: colour before object)."""
    return _FakeEpisode([{"id": i, "words_in_instant": [c, o]} for i, (c, o) in enumerate(missions)])
