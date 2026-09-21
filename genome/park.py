"""park.py — PARK: metacognition, day-1 gene (G4 §3 B4; docs/G4-DESIGN.md row 4c: D39 — Alpha 3's two
days repeating one want, "skullcap~device", 86% of 09-18, because nothing told it to stop asking).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B4 (docs/briefs/G4-BUILDER-B-GENES.md).

Law of this file: N identical dead-end ANSWERS (by REASON, not by attempt count alone — a different
reason has its own counter and never adds to another reason's) park a want; a parked want's further asks
are refused WITH NO WORK (the caller must check `answer()`'s return before doing anything); reopened only
by a NEW SENSE or a DOCUMENT naming the want (PREREG's genome line: `PARK after N identical dead-ends
reopen on new-sense`; the B4 contract widens it to "a new sense or document" — both are evidence the
world changed, never merely asking again).
"""
from __future__ import annotations

from typing import Dict, Tuple

REOPEN_KINDS = frozenset({"new-sense", "document"})


class Park:
    """PARK — PREREG §3 B4: `answer(want, reason) -> "open"|"parked"`; `reopen(want, evidence_kind) ->
    bool`; `state()` for STATUS."""

    def __init__(self, n: int):
        if n < 1:
            raise ValueError(f"Park: n must be >= 1, got {n}")
        self.n = n
        self._counts: Dict[Tuple[str, str], int] = {}     # (want, reason) -> how many times, independent per reason
        self._parked: Dict[str, str] = {}                  # want -> the reason it was parked with

    def answer(self, want: str, reason: str) -> str:
        """Call once per dead-end answer for `want`. A want already parked returns "parked" and does
        NO further work (the counters are not touched). Otherwise the (want, reason) pair's own count is
        incremented; a DIFFERENT reason for the same want has its own independent counter and never adds
        to this one's — only the n-th IDENTICAL reason parks the want."""
        if want in self._parked:
            return "parked"
        key = (want, reason)
        self._counts[key] = self._counts.get(key, 0) + 1
        if self._counts[key] >= self.n:
            self._parked[want] = reason
            return "parked"
        return "open"

    def is_parked(self, want: str) -> bool:
        """edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-2 (docs/G4-WAVE3-CLAUSES.md):
        a plain query, additive (no existing behaviour touched) — callers that build candidate work
        BEFORE calling answer() (creature/mind.py's rule pool, W3-2) need to skip an already-parked want
        without doing that work over again just to get "parked" back from answer()."""
        return want in self._parked

    def reopen(self, want: str, evidence_kind: str) -> bool:
        """Reopens a parked want when `evidence_kind` is "new-sense" or "document" — never for asking
        again with the same kind of evidence ("same-sense" and anything else return False, no change).
        A reopened want's dead-end counters are cleared (fresh evidence deserves a fresh count)."""
        if want not in self._parked:
            return False
        if evidence_kind not in REOPEN_KINDS:
            return False
        del self._parked[want]
        for key in [k for k in self._counts if k[0] == want]:
            del self._counts[key]
        return True

    def state(self) -> Dict[str, object]:
        """For STATUS: every parked want with the reason it parked on and the count it parked at (== n,
        by construction), plus the still-open (want, reason) counters and the total parked."""
        return {
            "parked": {want: {"reason": reason, "count": self.n} for want, reason in self._parked.items()},
            "open_counts": {f"{want}\x1f{reason}": c for (want, reason), c in self._counts.items()},
            "n": self.n,
            "total_parked": len(self._parked),
        }
