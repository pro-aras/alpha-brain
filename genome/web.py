# edit: Claude (Opus 5.5, the seat), 2026-09-29 22:52 +0400 — PREREG-KW-1 §2 and §4.3 (docs/brain/memory/kweb/, signed 865adcf): THE KNOWLEDGE WEB.
# edit: Claude (Opus 5.5, the seat), 2026-09-29 22:49 +0400 — PREREG-KW-1 AMENDMENT 1: consolidation = c >= k AND k spaced occasions AND a Poisson tail
# P(X >= c | E) < alpha (the signed lift test passed chance bursts); `m` leaves, `gap` and `alpha` enter; edges carry `occ`.
"""genome/web.py — a web of heard words, every fact about it kept (never inferred), grown by one of six rules.

NODES are heard words: `n` (times heard), `first`, `last` (the order of life, 1-based, in words heard), `source`, `author`.
EVENTS: each heard word pairs with each of the previous `d` DISTINCT words (itself excluded): the temporal-context link.
EDGES (unordered pairs) carry `c` (evidence: pair events while the edge lives), `t0` (made at), `last` (last evidence, None if
never), `touch` (last evidence or making), `miss` (hearings of each word apart since `touch`), `state` (silent | consolidated),
`consolidated_at`, `occ` (occasions), `source`, `author`.
CONSOLIDATION (one test for every rule, AMENDMENT 1): c >= k AND occ >= k AND P(X >= c | E) < alpha for X ~ Poisson(E),
E = 2 · d · f_a · f_b · max(1, t − t0 + 1), f = a word's share of all words heard so far. An evidence event more than `gap` words
after the edge's previous evidence starts a new OCCASION (the evidence that makes an edge is its first). Checked at an evidence
event.

THE RULES (PREREG-KW-1 §2.1): H keeps every pair, unbounded; F makes edges until the budget B is full, then refuses; L makes an
edge for every heard pair and, when full, replaces the SILENT edge with the least c (ties: the oldest `touch`, then the key);
S is L with a realisation of probability p; R makes edges ONLY by one blind sprout a heard word (to a uniform random known word)
and counts heard pairs as evidence on existing edges; S0 is S with every event redirected to a uniformly random pair of known
words. L, S, R and S0 remove a SILENT edge when each of its two words has been heard `z` times apart since its `touch`; H and F
never remove; no rule removes a consolidated edge. Every draw: numpy default_rng([seed, RULE_TAG[rule]]). No clock.

THE SELF (PREREG-KW-1 §4.3): a `Claim` is a quantified statement about the organism, checked event by event: `always` is
demoted when its contradictions pass its tolerance share, `usually` when its confirmations fall under its level, each only
after `min_events`; a demoted claim keeps its counts.
"""
from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

RULES = ("H", "F", "L", "S", "R", "S0")
RULE_TAG = {"H": 0, "F": 1, "L": 2, "S": 3, "R": 4, "S0": 5}
REMOVING = ("L", "S", "R", "S0")
VERSION = 1


class WebError(Exception):
    pass


def _key(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a < b else (b, a)


def poisson_sf(c: int, E: float) -> float:
    """P(X >= c) for X ~ Poisson(E)."""
    if c <= 0:
        return 1.0
    if E <= 0:
        return 0.0
    term = math.exp(-E)
    cdf = term
    for i in range(1, c):
        term *= E / i
        cdf += term
    return max(0.0, 1.0 - cdf)


class Web:
    def __init__(self, rule: str, budget: Optional[int] = None, seed: int = 0, *, d: int = 3, k: int = 3, gap: Optional[int] = None,
                 alpha: float = 1e-3, p: float = 0.5, z: int = 10, source: str = "lived", author: Optional[str] = None):
        if rule not in RULES:
            raise WebError(f"rule {rule!r} is not one of {RULES}")
        if rule != "H" and (budget is None or int(budget) < 1):
            raise WebError(f"rule {rule} needs a budget >= 1, got {budget!r}")
        self.rule, self.budget, self.seed = rule, (None if rule == "H" else int(budget)), int(seed)
        self.d, self.k, self.p, self.z = int(d), int(k), float(p), int(z)
        self.gap = 2 * self.d if gap is None else int(gap)
        self.alpha = float(alpha)
        self.source, self.author = str(source), author
        self.t = 0
        self.nodes: Dict[str, Dict[str, object]] = {}
        self.order: List[str] = []                       # known words, first-heard order (R's and S0's draws index it)
        self.recent: List[str] = []                      # the previous d distinct words, most recent first
        self.edges: Dict[Tuple[str, str], Dict[str, object]] = {}
        self._adj: Dict[str, set] = {}
        self.rng = np.random.default_rng([self.seed, RULE_TAG[rule]])
        self.stats = {"events": 0, "offered": 0, "realised": 0, "refused": 0, "replaced": 0, "removed_missed": 0,
                      "sprouted": 0, "sprout_existing": 0, "consolidated": 0, "evidence": 0}

    # -- the edges --------------------------------------------------------------------------------
    def _new_edge(self, key: Tuple[str, str], c: int) -> bool:
        if self.budget is not None and len(self.edges) >= self.budget:
            if self.rule == "F":
                self.stats["refused"] += 1
                return False
            victim = None
            best = None
            for kk, e in self.edges.items():
                if e["state"] != "silent":
                    continue
                cand = (e["c"], e["touch"], kk)
                if best is None or cand < best:
                    best, victim = cand, kk
            if victim is None:
                self.stats["refused"] += 1
                return False
            self._drop(victim)
            self.stats["replaced"] += 1
        t = self.t
        self.edges[key] = {"c": int(c), "occ": (1 if c else 0), "t0": t, "last": (t if c else None), "touch": t, "miss": [0, 0],
                           "state": "silent", "consolidated_at": None, "source": self.source, "author": self.author}
        for w in key:
            self._adj.setdefault(w, set()).add(key)
        if c:
            self._check(key)
        return True

    def _drop(self, key: Tuple[str, str]) -> None:
        del self.edges[key]
        for w in key:
            s = self._adj.get(w)
            if s is not None:
                s.discard(key)

    def _check(self, key: Tuple[str, str]) -> None:
        e = self.edges[key]
        if e["state"] != "silent" or e["c"] < self.k or e["occ"] < self.k:
            return
        t = self.t
        fa, fb = self.nodes[key[0]]["n"] / t, self.nodes[key[1]]["n"] / t
        E = 2 * self.d * fa * fb * max(1, t - e["t0"] + 1)
        if poisson_sf(int(e["c"]), E) < self.alpha:
            e["state"], e["consolidated_at"] = "consolidated", t
            self.stats["consolidated"] += 1

    def _evidence(self, key: Tuple[str, str]) -> None:
        e = self.edges[key]
        if e["last"] is None or self.t - e["last"] > self.gap:
            e["occ"] += 1
        e["c"] += 1
        e["last"] = e["touch"] = self.t
        e["miss"] = [0, 0]
        self.stats["evidence"] += 1
        self._check(key)

    def _event(self, a: str, b: str, touched: set) -> None:
        """One pair event (a != b), under the rule. R never makes an edge here; S0 redirects before calling."""
        key = _key(a, b)
        self.stats["events"] += 1
        if key in self.edges:
            self._evidence(key)
            touched.add(key)
            return
        if self.rule == "R":
            return
        self.stats["offered"] += 1
        if self.rule in ("S", "S0") and self.rng.random() >= self.p:
            return
        if self._new_edge(key, 1):
            self.stats["realised"] += 1
            touched.add(key)

    # -- hearing ----------------------------------------------------------------------------------
    def hear(self, word: str) -> None:
        w = str(word)
        self.t += 1
        t = self.t
        nd = self.nodes.get(w)
        if nd is None:
            nd = self.nodes[w] = {"n": 0, "first": t, "last": t, "source": self.source, "author": self.author}
            self.order.append(w)
        nd["n"] += 1
        nd["last"] = t
        touched: set = set()
        for u in self.recent:
            if u == w:
                continue
            if self.rule == "S0":
                if len(self.order) < 2:
                    continue
                i, j = self.rng.choice(len(self.order), size=2, replace=False)
                self._event(self.order[int(i)], self.order[int(j)], touched)
            else:
                self._event(u, w, touched)
        if self.rule == "R" and len(self.order) >= 2:
            while True:
                x = self.order[int(self.rng.integers(len(self.order)))]
                if x != w:
                    break
            key = _key(w, x)
            self.stats["sprouted"] += 1
            if key in self.edges:
                self.stats["sprout_existing"] += 1
            elif self._new_edge(key, 0):
                touched.add(key)
        if self.rule in REMOVING:
            for key in list(self._adj.get(w, ())):
                if key in touched:
                    continue
                e = self.edges.get(key)
                if e is None or e["state"] != "silent" or e["touch"] == t:
                    continue
                e["miss"][0 if key[0] == w else 1] += 1
                if e["miss"][0] >= self.z and e["miss"][1] >= self.z:
                    self._drop(key)
                    self.stats["removed_missed"] += 1
        self.recent = ([w] + [x for x in self.recent if x != w])[: self.d]

    # -- reading --------------------------------------------------------------------------------
    def consolidated(self) -> List[Tuple[str, str]]:
        return sorted(k for k, e in self.edges.items() if e["state"] == "consolidated")

    def neighbours(self, word: str, n: int = 10) -> List[Tuple[str, int]]:
        """«What goes with X?»: X's consolidated edges, most evidence first."""
        out = []
        for key in self._adj.get(word, ()):
            e = self.edges[key]
            if e["state"] == "consolidated":
                out.append((key[1] if key[0] == word else key[0], int(e["c"])))
        return sorted(out, key=lambda kv: (-kv[1], kv[0]))[:n]

    # -- the state ------------------------------------------------------------------------------
    def to_dict(self) -> Dict[str, object]:
        return {"version": VERSION, "rule": self.rule, "budget": self.budget, "seed": self.seed, "d": self.d, "k": self.k,
                "gap": self.gap, "alpha": self.alpha, "p": self.p, "z": self.z, "source": self.source, "author": self.author, "t": self.t,
                "nodes": self.nodes, "order": self.order, "recent": self.recent,
                "edges": [[a, b, e] for (a, b), e in sorted(self.edges.items())],
                "rng": self.rng.bit_generator.state, "stats": self.stats}

    def dumps(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def loads(cls, s: str) -> "Web":
        st = json.loads(s)
        if st.get("version") != VERSION:
            raise WebError(f"loads: version {st.get('version')!r}, this module reads {VERSION}")
        w = cls(st["rule"], st["budget"], st["seed"], d=st["d"], k=st["k"], gap=st["gap"], alpha=st["alpha"], p=st["p"], z=st["z"],
                source=st["source"], author=st["author"])
        w.t, w.nodes, w.order, w.recent, w.stats = st["t"], st["nodes"], st["order"], st["recent"], st["stats"]
        for a, b, e in st["edges"]:
            w.edges[(a, b)] = e
            w._adj.setdefault(a, set()).add((a, b))
            w._adj.setdefault(b, set()).add((a, b))
        w.rng.bit_generator.state = st["rng"]
        return w


def recount_errors(web: Web, words: Sequence[str]) -> List[str]:
    """PREREG-KW-1 G1: every node's n / first / last and every live edge's c, occ and last against a recount FROM THE WORDS. An
    edge's c = its making credit (1 when a heard pair made it, 0 for R's sprout) + its pair's events after t0; its occasions the
    same events under the gap rule. S0's edges are given random evidence by definition: for S0 only the nodes are recounted."""
    errs: List[str] = []
    nodes: Dict[str, List[int]] = {}
    events: Dict[Tuple[str, str], List[int]] = {}
    recent: List[str] = []
    for t, w in enumerate(words, 1):
        nd = nodes.setdefault(w, [0, t, t])
        nd[0] += 1
        nd[2] = t
        for u in recent:
            if u != w:
                events.setdefault(_key(u, w), []).append(t)
        recent = ([w] + [x for x in recent if x != w])[: web.d]
    for w, (n, first, last) in nodes.items():
        got = web.nodes.get(w)
        if got is None or (got["n"], got["first"], got["last"]) != (n, first, last):
            errs.append(f"node {w}: web {None if got is None else (got['n'], got['first'], got['last'])} recount {(n, first, last)}")
    if set(web.nodes) != set(nodes):
        errs.append(f"node sets differ by {sorted(set(web.nodes) ^ set(nodes))[:5]}")
    if web.rule == "S0":
        return errs
    for key, e in web.edges.items():
        ts = events.get(key, [])
        made_by_pair = e["t0"] in ts and web.rule != "R"
        after = [t for t in ts if t > e["t0"]]
        c = (1 if made_by_pair else 0) + len(after)
        last = (after[-1] if after else (e["t0"] if made_by_pair else None))
        occ, prev = (1 if made_by_pair else 0), (e["t0"] if made_by_pair else None)
        for t in after:
            if prev is None or t - prev > web.gap:
                occ += 1
            prev = t
        if e["c"] != c or e["last"] != last or e["occ"] != occ:
            errs.append(f"edge {key}: web c {e['c']} occ {e['occ']} last {e['last']} recount c {c} occ {occ} last {last}")
    return errs


class Claim:
    """A quantified statement about the organism (PREREG-KW-1 §4.3), kept or demoted by life, never deleted."""

    def __init__(self, cid: str, text: str, quantifier: str, level: float, *, source: str = "implanted-knowledge",
                 author: Optional[str] = None, min_events: int = 30):
        if quantifier not in ("always", "usually"):
            raise WebError(f"claim {cid}: quantifier {quantifier!r} is not always | usually")
        self.id, self.text, self.quantifier, self.level = cid, text, quantifier, float(level)
        self.source, self.author, self.min_events = source, author, int(min_events)
        self.confirmed = self.contradicted = 0
        self.state = "trusted"
        self.first_demoted_at: Optional[int] = None
        self.first_event_at: Optional[int] = None

    def observe(self, ok: bool, at: int) -> None:
        if self.first_event_at is None:
            self.first_event_at = int(at)
        if ok:
            self.confirmed += 1
        else:
            self.contradicted += 1
        n = self.confirmed + self.contradicted
        if n < self.min_events:
            return
        if self.quantifier == "always":
            demote = self.contradicted / n > self.level
        else:
            demote = self.confirmed / n < self.level
        self.state = "demoted" if demote else "trusted"
        if demote and self.first_demoted_at is None:
            self.first_demoted_at = int(at)

    def to_dict(self) -> Dict[str, object]:
        n = self.confirmed + self.contradicted
        return {"id": self.id, "text": self.text, "quantifier": self.quantifier, "level": self.level, "source": self.source,
                "author": self.author, "confirmed": self.confirmed, "contradicted": self.contradicted,
                "share_confirmed": (self.confirmed / n if n else None), "state": self.state,
                "first_demoted_at": self.first_demoted_at, "first_event_at": self.first_event_at, "min_events": self.min_events}
