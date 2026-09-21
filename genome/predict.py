"""predict.py — PREDICT + FILE: the one modulator, and the falsifiability law (G4 §3 B6; docs/G4-DESIGN.md
row 3b — his research's predictive-coding/active-inference mechanism, docs/THINKING-RUNG1-PREREG.md §1 —
new, minimal; FILE reimplements Alpha 2's organs/prediction_ledger.py's law in tens of lines).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 22:07 +0400 — B6 (docs/briefs/G4-BUILDER-B-GENES.md).

edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 10:46 +0400 — W3-2b (docs/G4-WAVE3-CLAUSES.md, W3-2's
NOTE; docs/G4-PREREG.md §16 addendum 1): `error()`'s target moves INSIDE the organism. The reading that
forced this: PREDICT's error was measured against `expect()` = the LAST moment's strongest sight winner
— a state carried from a DIFFERENT thing (the previous canvas), so every canvas boundary read the same
size (steady ~.23) and an ARRIVAL was invisible to it (life 1: 0 of 5 spikes). The law now: the expected
glance is the nearest RESONATING cell's stored vector for THIS glance — `c = org.sight.cos(x_actual)`
over the cells alive BEFORE this moment (this method is called, in `creature/mind.py`, before
`Organism.moment()` runs for the canvas — no newborn from this very glance can be among them); if the
nearest cell RESONATES (`c.max() >= org._theta(org.sight)`, machinery's own threshold, read not called —
`Organism._resonate` BIRTHS, which a mere error reading must never do) the error is `1 - c.max()`; with
nothing resonating (including no sight cell born yet) the error is the maximal 1.0 — a genuine surprise,
not a graded wrongness. `expect()`/`note_winners()` are KEPT for the record (mind.py still calls
`note_winners` after every moment) but nothing grades on them any more; see this module's own toy
(tests/genome/test_predict.py) and tests/genome/test_b13_modulation_arrival.py for the re-read this
forced on both the B6 and B13 toys — reported honestly, not moved.

PREDICT's OLD law (superseded above, kept here so the "why" is not lost): `expect()` named the feature
the NEXT glance was predicted to look like — the current sight winner's own cell vector (the strongest
resonating sight cell of the last moment lived, read from `Organism.moment()`'s new (S, T) return — B2's
edit to machinery.py); before any winner had ever been seen, the mean of the alive sight cells; with none
alive at all, zeros. `error(x_actual)` was 1 minus the cosine to that expectation (clipped into [0, 2],
cosine's own range) — the modulator: it grades the act (the caller reads `.last_error` to know how
surprising this moment was), scales DELTA's learning rate (`modulate`), and ranks what SLEEP replays (B7
reads `surprise=error` off this same number — still true under the new law, same signal, new source).

FILE's law: a prediction is FILED with all four fields named (claim, route, decider, due) or REFUSED BY
NAME — never silently dropped, never accepted half-written. `score` grades a filed (never a refused) row
against `evidence`: a callable `evidence(row) -> bool` is the general form (the "decider" is WHO applies
it; `evidence` supplies the mechanical check no free-text field can); a plain value is graded by its own
truthiness. `append_ledger` writes one JSON line to `predictions.jsonl` per PREREG §3 B6 — plain append
(a ledger is append-only; unlike FAST's full-file save, a torn last line is a known, tolerable read-time
risk, not a save-time one).
"""
from __future__ import annotations

import json
import pathlib as _pl
from typing import Callable, Dict, List, Optional, Union

import numpy as np

from .machinery import Organism

FILE_FIELDS = ("claim", "route", "decider", "due")


class Predictor:
    """PREDICT — PREREG §3 B6: `expect()`, `error(x_actual)`, `modulate(lr)`. Bound to one Organism;
    call `note_winners(S)` with the sight winners `Organism.moment()` returned, once per moment lived,
    so the NEXT `expect()` reflects what was just seen.

    W3-2b (2026-09-21): `error()` no longer calls `expect()` — it reads `self.org.sight` directly (the
    nearest RESONATING cell to the actual glance, module docstring). `expect()`/`note_winners()` are kept
    for the record (still called every moment) but nothing grades on them any more."""

    def __init__(self, org: Organism, lo: float = 0.5, hi: float = 2.0):
        self.org = org
        self.lo, self.hi = lo, hi
        self._last_winner: Optional[np.ndarray] = None
        self.last_error: Optional[float] = None

    def note_winners(self, S: List[int]) -> None:
        """S: the sight winners of the moment just lived (best first, §11 am. 3's resonate order). The
        strongest one becomes what the NEXT expect() names. An empty S (nothing resonated) leaves the
        last winner as it was — a moment with no sight winner teaches expect() nothing new."""
        if S:
            self._last_winner = self.org.sight.cells[S[0]].copy()

    def expect(self) -> np.ndarray:
        """The next glance's expected feature: the last noted winner; before any winner, the mean of
        the alive sight cells; with none alive, zeros (genome.sight_dim()-long)."""
        if self._last_winner is not None:
            return self._last_winner
        alive = self.org.sight.alive_ids()
        if len(alive) == 0:
            return np.zeros(self.org.g.sight_dim())
        return self.org.sight.cells[alive].mean(axis=0)

    def error(self, x_actual: np.ndarray) -> float:
        """W3-2b (docs/G4-WAVE3-CLAUSES.md, W3-2's NOTE; PREREG §16 addendum 1): the expected glance is
        the nearest RESONATING sight cell's stored vector for THIS glance — `c = org.sight.cos(x_actual)`
        over the cells alive BEFORE this moment (the caller, creature/mind.py, calls this BEFORE
        `Organism.moment()` runs for the canvas, so no newborn from this very glance can be among them —
        a newborn scoring 0 error at its own birth would hide every arrival). If the nearest cell
        RESONATES (`c.max() >= org._theta(org.sight)` — machinery's own comparison, READ not CALLED:
        `Organism._resonate` births, which a mere error reading must never do) the error is
        `1 - c.max()` (clipped into [0, 2], cosine's own range); with nothing resonating — including no
        sight cell born yet (`org.sight.n == 0`) — the error is the maximal 1.0: a genuine surprise,
        not a graded wrongness (there is nothing yet to be wrong ABOUT)."""
        area = self.org.sight
        if area.n == 0:
            e = 1.0
        else:
            c = area.cos(x_actual)
            cmax = float(c.max())
            theta = self.org._theta(area)
            e = float(np.clip(1.0 - cmax, 0.0, 2.0)) if cmax >= theta else 1.0
        self.last_error = e
        return e

    def modulate(self, lr: float) -> float:
        """lr x clip(0.5 + 3*error, 0.5, 2.0) — PREREG's genome line: `PREDICT … error scales delta
        0.5..2.0`. Reads the last `error()` call's result; with none yet, error=0 (scale floors at 0.5)."""
        e = self.last_error if self.last_error is not None else 0.0
        scale = float(np.clip(0.5 + 3.0 * e, self.lo, self.hi))
        return lr * scale


# ============================================================================================= FILE
def file(claim: str, route: str, decider: str, due: str) -> Dict[str, object]:
    """FILE claim route decider due: all four named (non-empty) or refused BY NAME. Returns
    {"accepted": True, "row": {...}} or {"accepted": False, "refused": [missing field names], "row": {...}}
    — the refusal is itself a row, never a silent drop or a raised exception."""
    row = {"claim": claim, "route": route, "decider": decider, "due": due}
    missing = [f for f in FILE_FIELDS if not row.get(f)]
    if missing:
        return {"accepted": False, "refused": missing, "row": dict(row)}
    return {"accepted": True, "refused": [], "row": dict(row), "outcome": None}


def score(row: Dict[str, object], evidence: Union[Callable[[Dict[str, object]], bool], object]) -> Dict[str, object]:
    """Grades a FILED (never a refused) row's claim against `evidence`. `evidence` callable -> called as
    evidence(row["row"]); otherwise graded by bool(evidence). Returns a NEW dict (the input row is never
    mutated) with "outcome" set True/False. Raises ValueError on a refused row — there is nothing to
    grade (score()ing a refusal is a caller bug, not a data condition FILE should paper over)."""
    if not row.get("accepted"):
        raise ValueError(f"score: a refused claim was never filed — nothing to grade (refused: {row.get('refused')})")
    outcome = bool(evidence(row["row"])) if callable(evidence) else bool(evidence)
    out = dict(row); out["row"] = dict(row["row"]); out["outcome"] = outcome
    return out


def append_ledger(path, row: Dict[str, object]) -> None:
    """Appends one FILE/score row as a JSON line to `path` (predictions.jsonl, PREREG §3 B6)."""
    p = _pl.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(row, default=str) + "\n")
