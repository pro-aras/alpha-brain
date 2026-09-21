"""genome/curiosity.py — B10 (docs/G4-PREREG.md §11.2): CURIOSITY. Interests tracks a weight per
(kind, key) pair and picks the highest-weight item from a pool the mind hands it each THINK step.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — new module, Wave 2 B10.

edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:xx +0400 — W3-2 (docs/G4-WAVE3-CLAUSES.md): a new
outcome, "failed" — "a scored rule that FAILS lowers CURIOSITY's weight on its item", the brief's own
words. Specialize's own arithmetic (x0.5), under its own name: a rule can FAIL (its due-canvas decider
did not hold) without ever being PARKED (parked needs 3 identical fails on the SAME want, PARK's own
law) — the two are different signals sharing one multiplier, so they are counted separately
(state()["outcomes"]["failed"] vs the PARK ledger) even though the weight math is identical to "parked".

Interface fixed for Builder A (docs/G4-PREREG.md §11, the coordinator's Wave 2 message, verbatim):
    class Interests(n: int, rng)
        choose(pool, rng) -> item        # pool = [{"kind": "word"|"sight"|"due"|"rule", "key": str,
                                          #          "episode": int|None, "pred": dict|None}, ...]
                                          # highest weight, ties by rng; an unseen item is born at 1.0
        update(item, outcome)            # outcome in {"answered","parked","filed","scored","failed"}
        state()                          # for STATUS
        save(path) / load(path)          # JSON
    the null twin = choose with weights ignored (uniform by rng) — provided here as choose_uniform().

Two spec points the PREREG names but does not fully pin down, decided and documented here (consistent
with the rest of the estate's "an ambiguity is decided and written down, not silently guessed"
discipline — SOLUTIONS #131/#180):

  1. THE KEY. Weights are tracked per (kind, key), never per bare key — a word "circle" and a sight
     whose key happens to be "circle" are different interests and must not share a weight.

  2. BRIDGE's trigger. "a new item whose key is a known word → bridge +0.25" fires at BIRTH (the first
     time choose() ever sees this exact (kind, key) pair), never inside update(). A set of every key
     that has appeared under kind=="word" is kept; a brand-new item of a DIFFERENT kind whose key is in
     that set is born at 1.25 instead of 1.0. A brand-new "word" item can never trigger its own bridge
     (its own key was not yet known before it existed), and a repeat sighting of an existing (kind,key)
     is not a birth, so bridge never re-fires on it.

  3. RECOMBINE's trigger. "two items answered in the same sleep window → recombine to their mean" needs
     a notion of "window" this class does not otherwise have. sleep_boundary() is a method the mind
     calls once per SLEEP tick (§11.1 step 4) to close the current window. Inside a window, every
     "answered" outcome is remembered in order; the SECOND (and each subsequent) answered item in the
     same window is recombined with the immediately-preceding answered item: both weights are set to
     their mean. generalize (the +0.5 to every item of that kind) always fires first, on the pre-
     recombine weights, so an "answered" outcome does both operators in the order the PREREG lists them
     (generalize, then recombine) rather than one replacing the other.

  4. outcomes "filed" and "scored" carry no operator in the PREREG text (only "answered" -> generalize
     and "parked" -> specialize are named). They are accepted, counted in state(), and change no weight
     — a documented no-op, not an omission.

  5. `n` (Interests.__init__'s first argument) is read as a soft population cap: after any update(), if
     more than n (kind,key) pairs are tracked, the lowest-weight ones beyond n are dropped (ties broken
     by insertion order, oldest first). No decay is applied (the PREREG says "no decay" explicitly) —
     this is pruning of the population, not decay of a weight.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

Item = Dict[str, object]
Key = Tuple[str, str]  # (kind, key)

VALID_OUTCOMES = {"answered", "parked", "filed", "scored", "failed"}


def _k(item: Item) -> Key:
    return (str(item["kind"]), str(item["key"]))


class Interests:
    def __init__(self, n: int, rng) -> None:
        self.n = int(n)
        self.rng = rng
        self.weights: Dict[Key, float] = {}
        self._known_words: set = set()
        self._insertion_order: List[Key] = []
        self._window_answered: List[Key] = []  # answered (kind,key)s since the last sleep_boundary()
        self._outcomes_seen: Dict[str, int] = {o: 0 for o in VALID_OUTCOMES}

    # ---------------------------------------------------------------- birth
    def _weight_of(self, item: Item) -> float:
        k = _k(item)
        if k not in self.weights:
            w = 1.0
            if k[0] != "word" and k[1] in self._known_words:
                w += 0.25  # bridge: a new item whose key is a known word
            self.weights[k] = w
            self._insertion_order.append(k)
        if k[0] == "word":
            self._known_words.add(k[1])
        return self.weights[k]

    # --------------------------------------------------------------- choose
    def choose(self, pool: List[Item], rng=None) -> Item:
        if not pool:
            raise ValueError("Interests.choose: empty pool")
        r = self.rng if rng is None else rng
        weights = [self._weight_of(item) for item in pool]
        best = max(weights)
        tied = [i for i, w in enumerate(weights) if w == best]
        idx = tied[0] if len(tied) == 1 else int(r.choice(tied))
        return pool[idx]

    # --------------------------------------------------------------- update
    def update(self, item: Item, outcome: str) -> None:
        if outcome not in VALID_OUTCOMES:
            raise ValueError(f"Interests.update: unknown outcome {outcome!r}")
        k = _k(item)
        if k not in self.weights:
            self._weight_of(item)  # a never-seen item can still be updated: born first, then updated
        self._outcomes_seen[outcome] += 1
        if outcome == "answered":
            # generalize: +0.5 to every tracked item of this kind (population-wide, not just k)
            for other in list(self.weights):
                if other[0] == k[0]:
                    self.weights[other] += 0.5
            # recombine: the SECOND (or later) answered item in the same sleep window averages with
            # the one immediately before it in this window
            if self._window_answered:
                prev = self._window_answered[-1]
                if prev != k and prev in self.weights and k in self.weights:
                    mean = (self.weights[prev] + self.weights[k]) / 2.0
                    self.weights[prev] = mean
                    self.weights[k] = mean
            self._window_answered.append(k)
        elif outcome == "parked":
            # specialize: x0.5 on that item only
            self.weights[k] = self.weights[k] * 0.5
        elif outcome == "failed":
            # W3-2: a scored rule FAIL — specialize's same x0.5, under its own name (module docstring).
            self.weights[k] = self.weights[k] * 0.5
        # "filed" / "scored": no operator named in the PREREG — counted, no weight change.
        self._prune()

    def sleep_boundary(self) -> None:
        """Called once per SLEEP tick (§11.1 step 4): closes the current window so the next
        "answered" outcome starts a fresh recombine chain rather than pairing with one from a
        window that already ended."""
        self._window_answered = []

    def _prune(self) -> None:
        if len(self.weights) <= self.n:
            return
        # drop the lowest-weight entries beyond n; ties broken oldest-inserted-first
        order = sorted(self._insertion_order, key=lambda k: (self.weights.get(k, 0.0), self._insertion_order.index(k)))
        excess = len(self.weights) - self.n
        for k in order[:excess]:
            self.weights.pop(k, None)
            if k in self._insertion_order:
                self._insertion_order.remove(k)
            self._window_answered = [w for w in self._window_answered if w != k]

    # ---------------------------------------------------------------- state
    def state(self) -> Dict[str, object]:
        return {
            "n": self.n,
            "count": len(self.weights),
            "weights": {f"{k[0]}:{k[1]}": w for k, w in self.weights.items()},
            "outcomes": dict(self._outcomes_seen),
            "window_open_answered": len(self._window_answered),
        }

    # ----------------------------------------------------------- save/load
    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        tmp = path.with_suffix(path.suffix + ".tmp")
        payload = {
            "n": self.n,
            "weights": [[k[0], k[1], w] for k, w in self.weights.items()],
            "known_words": sorted(self._known_words),
            "insertion_order": [[k[0], k[1]] for k in self._insertion_order],
            "window_answered": [[k[0], k[1]] for k in self._window_answered],
            "outcomes_seen": self._outcomes_seen,
        }
        with open(tmp, "w") as f:
            json.dump(payload, f)
        tmp.replace(path)

    def load(self, path: Union[str, Path]) -> None:
        path = Path(path)
        with open(path) as f:
            payload = json.load(f)
        self.n = int(payload["n"])
        self.weights = {(kind, key): float(w) for kind, key, w in payload["weights"]}
        self._known_words = set(payload["known_words"])
        self._insertion_order = [(kind, key) for kind, key in payload["insertion_order"]]
        self._window_answered = [(kind, key) for kind, key in payload["window_answered"]]
        self._outcomes_seen = {o: int(payload["outcomes_seen"].get(o, 0)) for o in VALID_OUTCOMES}


# ------------------------------------------------------------------- the null twin
def choose_uniform(pool: List[Item], rng) -> Item:
    """The null twin named in the PREREG: choose() with weights ignored — uniform by rng. A free
    function (not a method) so a toy/mind can compare Interests.choose against it without also
    carrying an Interests instance's state."""
    if not pool:
        raise ValueError("choose_uniform: empty pool")
    return pool[int(rng.integers(len(pool)))]
