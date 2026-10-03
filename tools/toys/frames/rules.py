"""rules.py — TOY C's three rules, each returning a set F of ordered pairs from the TRAIN part only (docs/research/toys/PREREG-TOY-FRAMES.md §2).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 16:54 +0400 — new module, red-first against tests/tools/test_toys_frames_rules.py (stage 2). `genome.web` and
# `genome.sentence` are IMPORTED, never edited (nothing under brain/ or genome/ changes).

  (a) WEB       genome.web.Web — rule H (once) and rule S with the budget B = 2V (V = the distinct train words), the train words fed in HEARD order (every source, rows in seq
                order); `consolidated()` returns unordered edges, each becomes the ONE ordered pair that is adjacent inside a train moment more often (a tie: alphabetical); an
                edge with NO adjacent train occurrence is dropped and counted («no adjacent occurrence»). The web's defaults are KW-1's (d 3, k 3, alpha 0.001); KW-2's options
                (`spend`, `beta`) are not used.
  (b) SENTENCE  genome.sentence.find_frames over the train moments through a stand-in store (`get(i)` -> {«id», «words_in_instant»}, `n_written`, `cap`), min_count 5,
                factor 2.0, as the cells ran it. NOTE find_frames counts EVERY ordered pair a < b of a moment's distinct words, not only the adjacent ones.
  (c) MDL-GREEDY  candidates = every within-moment adjacent train bigram with count >= 2; greedily add the frame with the largest TRAIN gain
                delta = bits(train | F) − bits(train | F ∪ {f}) − 2 log2 V (the exact count-based change: only the moments where f stands adjacent can change, and each is
                re-parsed under F ∪ {f}), until no candidate has delta > 0; ties (within 1e-9 bits) go to the smaller pair name.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

from genome.sentence import find_frames

from .compress import END, Frame, Scorer, parse_moment, slow_train_bits

RULE_TAG: Dict[str, int] = {"WEB-H": 1, "WEB-S": 2, "SENTENCE": 3, "MDL-GREEDY": 4}      # the law's `rule_tag` (it names the key, not the numbers; printed in the report header)
TIE_BITS = 1e-9


@dataclass(frozen=True)
class RuleResult:
    rule: str
    seed: int
    frames: FrozenSet[Frame]
    info: Dict[str, object]


# ====================================================================================================================== (a) WEB
def orient_edges(edges: Iterable[Tuple[str, str]], scorer: Scorer) -> Tuple[Set[Frame], List[Tuple[str, str]]]:
    """Each unordered edge -> the ordered pair with the larger within-moment adjacent TRAIN count (a tie: the alphabetical order); an edge with no adjacent occurrence in
    either order is returned in `dropped` (as (a, b) with a < b)."""
    frames: Set[Frame] = set()
    dropped: List[Tuple[str, str]] = []
    for e in edges:
        a, b = sorted(e)
        n_ab = scorer.train_adjacent((a, b))
        n_ba = scorer.train_adjacent((b, a))
        if n_ab == 0 and n_ba == 0:
            dropped.append((a, b))
            continue
        frames.add((b, a) if n_ba > n_ab else (a, b))
    return frames, dropped


def web_rule(flat_words: Sequence[str], scorer: Scorer, rule: str, seed: int) -> RuleResult:
    """rule «H»: keeps every pair, unbounded (once); rule «S»: budget 2V, seeds 1-10 in the run. The words are heard one at a time in the order given."""
    if rule not in ("H", "S"):
        raise ValueError(f"web_rule: rule {rule!r} is not 'H' or 'S'")
    from genome import web as Wb
    budget = None if rule == "H" else 2 * scorer.V
    w = Wb.Web(rule, budget=budget, seed=int(seed))
    peak = 0
    for x in flat_words:
        w.hear(x)
        n = len(w.edges)
        if n > peak:
            peak = n
    edges = w.consolidated()
    frames, dropped = orient_edges(edges, scorer)
    info = {"consolidated": len(edges), "dropped_no_adjacent": len(dropped), "budget": budget, "peak_edges": peak, "live_edges": len(w.edges),
            "stats": dict(w.stats), "words_heard": len(flat_words)}
    return RuleResult("WEB-" + rule, int(seed), frozenset(frames), info)


# ====================================================================================================================== (b) SENTENCE
class StandIn:
    """What find_frames reads of the cells' Episodes store: `get(i)`, `n_written`, `cap` (here cap = n_written: no ring eviction, every train moment is visible) and len()."""

    def __init__(self, moments: Sequence[Sequence[str]]):
        self._rows = [list(m) for m in moments]
        self.n_written = len(self._rows)
        self.cap = len(self._rows)

    def __len__(self) -> int:
        return self.n_written

    def get(self, i: int) -> Optional[Dict[str, object]]:
        if i < 0 or i >= self.n_written:
            return None
        return {"id": i, "words_in_instant": list(self._rows[i])}


def sentence_rule(moments: Sequence[Sequence[str]], min_count: int = 5, factor: float = 2.0) -> RuleResult:
    rows = find_frames(StandIn(moments), min_count=min_count, factor=factor)
    n_multi = sum(1 for m in moments if len({w for w in m if w}) >= 2)
    if rows and rows[0]["N"] != n_multi:
        raise RuntimeError(f"sentence_rule: find_frames' N {rows[0]['N']} differs from the moments with >= 2 distinct words {n_multi}")
    frames = frozenset((r["w1"], r["w2"]) for r in rows)
    detail = [(r["w1"], r["w2"], int(r["count"]), float(r["expected"])) for r in rows]
    return RuleResult("SENTENCE", 0, frames, {"rows": len(rows), "N": n_multi, "min_count": min_count, "factor": factor, "detail": detail})


# ====================================================================================================================== (c) MDL-GREEDY
def mdl_candidates(scorer: Scorer) -> List[Frame]:
    """Every distinct ordered pair adjacent inside a train moment at least twice, in name order."""
    return sorted(p for p, c in scorer.train_bigrams().items() if c >= 2)


class _Plus:
    """The frame set F ∪ {f} without copying F (membership only)."""
    __slots__ = ("F", "f")

    def __init__(self, F: Set[Frame], f: Frame):
        self.F, self.f = F, f

    def __contains__(self, p) -> bool:
        return p == self.f or p in self.F


def mdl_greedy(scorer: Scorer, max_steps: Optional[int] = None) -> RuleResult:
    train = scorer.train
    V = scorer.V
    cost_f = 2.0 * math.log2(V)
    cands = mdl_candidates(scorer)
    cset = set(cands)
    occ: Dict[Frame, List[int]] = {c: [] for c in cands}
    for i, m in enumerate(train):
        seen: Set[Frame] = set()
        for j in range(len(m) - 1):
            p = (m[j], m[j + 1])
            if p in cset and p not in seen:
                seen.add(p)
                occ[p].append(i)
    empty: Set[Frame] = set()
    cur = [parse_moment(m, empty) for m in train]
    cnt: Counter = Counter()
    for toks in cur:
        cnt.update(toks)
    n_tok = sum(cnt.values())
    clt = [0.0] + [c * math.log2(c + 1) for c in range(1, n_tok + 2)]          # c log2(c + 1), c = 0 .. N + 1 (a count never exceeds N)
    K = V + 2
    F: Set[Frame] = set()

    def self_code(n: int, k: int, counts) -> float:
        return n * math.log2(n + k) - sum(clt[c] for c in counts.values() if c > 0)

    bits = self_code(n_tok, K, cnt)
    bits_start = bits
    trace: List[Dict[str, object]] = []
    while max_steps is None or len(trace) < max_steps:
        S = sum(clt[c] for c in cnt.values() if c > 0)
        evals: List[Tuple[float, Frame]] = []
        for f in cands:
            if f in F:
                continue
            plus = _Plus(F, f)
            d: Dict[object, int] = {}
            for i in occ[f]:
                for t in cur[i]:
                    d[t] = d.get(t, 0) - 1
                for t in parse_moment(train[i], plus):
                    d[t] = d.get(t, 0) + 1
            dn = 0
            ds = 0.0
            for t, dt in d.items():
                if dt:
                    c0 = cnt.get(t, 0)
                    dn += dt
                    ds += clt[c0 + dt] - clt[c0]
            n2, k2 = n_tok + dn, K + 1
            bits2 = n2 * math.log2(n2 + k2) - (S + ds)
            evals.append((bits - bits2 - cost_f, f))
        if not evals:
            break
        best = max(e[0] for e in evals)
        if not best > 0.0:
            break
        chosen = min(f for dlt, f in evals if dlt >= best - TIE_BITS)
        delta = next(dlt for dlt, f in evals if f == chosen)
        # apply: re-parse the moments where the frame stands adjacent, update the counts, add its model cost
        F.add(chosen)
        fires = 0
        for i in occ[chosen]:
            new = parse_moment(train[i], F)
            cnt.subtract(cur[i])
            cnt.update(new)
            fires += sum(1 for t in new if t == chosen)
            cur[i] = new
        for t in [t for t, c in cnt.items() if c == 0]:
            del cnt[t]
        n_tok = sum(cnt.values())
        K += 1
        bits = self_code(n_tok, K, cnt)
        trace.append({"frame": chosen, "delta": delta, "bits_after": bits, "fires": fires, "n_tokens": n_tok})
    info = {"steps": len(trace), "trace": trace, "candidates": len(cands), "train_bits_empty": bits_start, "train_bits_final": bits, "max_steps": max_steps}
    return RuleResult("MDL-GREEDY", 0, frozenset(F), info)


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:09 +0400 — the MDL trace checker, moved here VERBATIM from tests/tools/test_toys_frames_rules.py (stage 5b: the gate G3 runs it on random streams too).
def trace_problems(train, trace) -> List[str]:
    """Check a greedy trace against the SLOW recount: every step's delta, its pick (the argmax over ALL candidates, ties within 1e-9 by the pair's name), its running bits,
    and that no candidate is left with a positive delta at the end. Returns the problems found (empty = the trace is exact)."""
    V = len({w for m in train for w in m})
    cands = sorted(p for p, c in Scorer(train, [["x"]]).train_bigrams().items() if c >= 2)
    F: set = set()
    bits_prev = slow_train_bits(train, F)[0]
    out: List[str] = []

    def slow_deltas() -> Dict[tuple, float]:
        return {f: bits_prev - slow_train_bits(train, F | {f})[0] - 2 * math.log2(V) for f in cands if f not in F}

    for i, s in enumerate(trace):
        sd = slow_deltas()
        best = max(sd.values())
        tied = sorted(f for f, d in sd.items() if d >= best - 1e-9)
        if tuple(s["frame"]) != tied[0]:
            out.append(f"step {i}: chose {s['frame']} but the slow recount's pick is {tied[0]} (best {best:.9f})")
        if abs(s["delta"] - sd.get(tuple(s["frame"]), float("nan"))) > 1e-9:
            out.append(f"step {i}: delta {s['delta']:.12f} vs the recount {sd.get(tuple(s['frame']))}")
        if not s["delta"] > 0:
            out.append(f"step {i}: a taken step with delta {s['delta']} <= 0")
        F.add(tuple(s["frame"]))
        bits_prev = slow_train_bits(train, F)[0]
        if abs(s["bits_after"] - bits_prev) > 1e-6:
            out.append(f"step {i}: bits_after {s['bits_after']} vs the recount {bits_prev}")
    left = [d for d in slow_deltas().values() if d > 1e-9]
    if left:
        out.append(f"{len(left)} candidates still have a positive delta after the last step (max {max(left):.9f})")
    return out
