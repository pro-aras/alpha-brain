# edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:30 +0400 — PREREG-INNER-1 §2 «the topic» + AMENDMENT 1 A1/A2/A4 and G3 (the law: research-1003 @
# 9c589b2, file sha256 127b063c…168d; the co-signed TEXT 857e07b2…faa82). Test-first: tests/creature/test_inner_walk.py (red on f123190).
"""creature/inner.py — THE WALK of the inner turn: pure functions over the mind's own web and self, called by creature/mind.py:_inner_turn.

A chain of thoughts begins at the SELF's least reliable mature word (first_topic) and continues by a SEEDED RANDOM walk on the WEB:
the next topic is drawn, with probability ∝ LIFT, among the consolidated neighbours of ANY word the previous say said (their union;
a candidate reached from several said words takes its largest lift — A1), among the brain's mature words, the last `inhibit`
topics excluded (the exclusion is lifted when it empties the set). `walk lift` is the only rule a genome can name (A4); the greedy
rules exist here as TEST parameters for G3's planted lock (every deterministic greedy walk on the real web locks: walk_counts.py).
Nothing here writes the web, the self or the brain."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

RULES = ("lift", "greedy-count", "greedy-lift")
Cand = Tuple[str, int, float]          # (word, the edge's evidence count c, the lift)


def lift(web, a: str, b: str, c: int) -> float:
    """c · T ÷ (n_a · n_b): the edge's evidence over what chance would give two words heard n_a and n_b times in T hearings
    (the web's own counts and clock, PREREG-INNER-1 §0.2)."""
    na, nb = int(web.nodes[a]["n"]), int(web.nodes[b]["n"])
    if na <= 0 or nb <= 0:
        return 0.0
    return float(c) * float(web.t) / (na * nb)


def candidates(web, said: Sequence[str], mature: Iterable[str], last: Sequence[str], inhibit: int) -> Tuple[List[Cand], bool]:
    """The next topic's candidates: the union over the SAID words of their CONSOLIDATED neighbours among the brain's mature words,
    each with its evidence count and its largest lift; the last `inhibit` topics excluded — unless that leaves none, in which case
    the exclusion is lifted (the second value says so). No web, or no said word the web knows → ([], False)."""
    mature_set = {str(w) for w in mature}
    if web is None:
        return [], False
    best: Dict[str, Cand] = {}
    for w in dict.fromkeys(str(x) for x in said):
        if w not in web.nodes:
            continue
        for y, c in web.neighbours(w, n=10 ** 9):
            if y not in mature_set or y == w:
                continue
            l = lift(web, w, y, int(c))
            if y not in best or l > best[y][2] or (l == best[y][2] and int(c) > best[y][1]):
                best[y] = (y, int(c), l)
    if not best:
        return [], False
    excluded = {str(t) for t in (list(last)[-int(inhibit):] if int(inhibit) > 0 else [])}
    kept = [best[y] for y in sorted(best) if y not in excluded]
    if kept:
        return kept, False
    return [best[y] for y in sorted(best)], True


def draw(cands: Sequence[Cand], rng: np.random.Generator, rule: str = "lift") -> Optional[str]:
    """One topic from the candidates: «lift» draws with probability ∝ lift from `rng` (the mind's substream(SEED, "inner-walk:<n>"));
    «greedy-count» / «greedy-lift» take the top (ties by name) — G3's plants, never a genome value."""
    if rule not in RULES:
        raise ValueError(f"inner.draw: rule {rule!r} is not one of {RULES}")
    if not cands:
        return None
    if rule == "greedy-count":
        return sorted(cands, key=lambda c: (-c[1], c[0]))[0][0]
    if rule == "greedy-lift":
        return sorted(cands, key=lambda c: (-c[2], c[0]))[0][0]
    w = np.array([max(float(c[2]), 0.0) for c in cands], dtype=np.float64)
    if w.sum() <= 0:
        w = np.ones(len(cands), dtype=np.float64)
    return str(cands[int(rng.choice(len(cands), p=w / w.sum()))][0])


def first_topic(self_node, mature: Iterable[str]) -> Tuple[Optional[str], str, List[Tuple[str, Optional[float]]]]:
    """The chain's first topic: the mature word with the LOWEST lived reliability in the self (confirmed ÷ expected; ties by name);
    when no mature word has a reliability yet (A2) the earliest by name; with no self (an error switched it off) likewise. Returns
    (topic, its source, the table [(word, reliability or None)] the choice was read from)."""
    words = sorted({str(w) for w in mature})
    if not words:
        return None, "self (no mature word)", []
    if self_node is None:
        return words[0], "self (no self)", [(w, None) for w in words]
    table = [(w, self_node.reliability(w)) for w in words]
    known = [(w, r) for w, r in table if r is not None]
    if not known:
        return words[0], "self (no reliability yet)", table
    return min(known, key=lambda wr: (wr[1], wr[0]))[0], "self", table


def locked(seq: Sequence[str], tail: int = 60, max_period: int = 15) -> Optional[int]:
    """The cycle detector (docs/organism/inner/records/walk_counts.py's own): the period p ≤ max_period that the last `tail` topics
    repeat with, or None. G3's planted greedy walk must read a period ≤ 4."""
    s = list(seq)
    if len(s) < tail + max_period:
        return None
    for p in range(1, max_period):
        if s[-tail:] == s[-tail - p:-p]:
            return p
    return None
