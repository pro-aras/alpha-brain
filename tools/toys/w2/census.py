"""tools/toys/w2/census.py — PREREG-W2 §3 item 3: the REFERENCE CENSUS and its gate (G-CENSUS).

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:08 +0400 — new file, written after tests/tools/test_w2_census.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 item 3 (per-canvas meeting counts from the tape's word lists,
asserted equal to the saved census at every calibration point, n of n with presence counts; a planted census byte must move
the comparison).

meeting_counts(word_lists): one entry per canvas of every word's meetings BEFORE that canvas, plus one final entry of the
totals after the last canvas (T-L4's body's m_before form). compare_saved: the gate against one saved census file — every
word's `meetings` equal on BOTH sides (a word missing on either side with a positive count on the other is a difference),
presence counts printed beside the result, the first difference named.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple


def meeting_counts(word_lists: Sequence[Sequence[str]]) -> List[Dict[str, int]]:
    """Entry i: the meetings of every word BEFORE canvas i; the final entry: the totals after the last canvas."""
    counts: Dict[str, int] = {}
    out: List[Dict[str, int]] = []
    for words in word_lists:
        out.append(dict(counts))
        for w in words:
            counts[w] = counts.get(w, 0) + 1
    out.append(dict(counts))
    return out


def at(counts: Sequence[Dict[str, int]], i: int) -> Dict[str, int]:
    """The cumulative meetings through the first i canvases (the saved census's quantity at calibration point i)."""
    if i < 0 or i > len(counts) - 1:
        raise IndexError(f"calibration point {i} outside the lists (0..{len(counts) - 1})")
    return dict(counts[i])


def compare_saved(word_lists: Sequence[Sequence[str]], saved: Dict[str, object], at: int) -> Dict[str, object]:
    """G-CENSUS at one calibration point: the recomputed meetings through `at` canvases equal the saved census's
    `words[w]['meetings']` for every word on BOTH sides. Presence counts: n_words (the union), n_checked (compared).
    first_diff: (word, recomputed, saved) of the first mismatch, or None."""
    mine: Dict[str, int] = {}
    for words in list(word_lists)[:at]:
        for w in words:
            mine[w] = mine.get(w, 0) + 1
    theirs = {str(w): int(v.get("meetings", 0)) for w, v in dict(saved.get("words", {})).items()}
    union = sorted(set(mine) | set(theirs))
    first: Optional[Tuple[str, int, int]] = None
    for w in union:
        a, b = mine.get(w, 0), theirs.get(w, 0)
        if a != b and first is None:
            first = (w, a, b)
    return {"ok": first is None, "n_words": len(union), "n_checked": len(union), "first_diff": first, "at": at}
