"""tools/toys/w2/diffj.py — PREREG-W2 §3 item 1: the I2 readers — the tape identity and the journal confinement.

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:35 +0400 — new file, written after tests/tools/test_w2_bench.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 item 1. **The journal confinement here is the form this lane
RAISED to the seat (the board ASK-SEAT of 2026-10-05): the law's signed sentence («every other row equal») cannot hold once
the first mentor word teaches, and this module implements the PROPOSED form, PENDING the seat's ruling — the tape identity
stands as written; the journal reads: every non-brain row equal, the FIRST difference a brain row at the first mentor-word
moment, every differing brain row's heard-list delta inside that moment's mentor words, the differing rows counted by kind.**

tape_identity(on_rows, off_rows): ON's non-mentor rows equal OFF's rows field by field with seqs normalized to 1..N in
order on both sides (the insertion shifts seqs; everything else — at, sense, sha, payload, meta — must be equal).

journal_confinement(off_rows, on_rows, mentor_words_by_moment): the journals aligned in order (the replay writes one
journal row per its live row, so order alignment is 1:1 while the confinement holds): every row of a kind OTHER than
"brain" equal field by field except "seq" (the insertion shift); the FIRST difference is a "brain" row; every differing
brain row's heard-list delta (turn's `heard`, learn's `words`) is inside that moment's mentor words; mentor-free moments'
heard lists equal; counts by kind.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

SKIP_SEQ = ("seq",)


def _eq(a: Dict[str, object], b: Dict[str, object], skip: Sequence[str] = SKIP_SEQ) -> Optional[str]:
    keys = (set(a) | set(b)) - set(skip)
    for k in sorted(keys):
        if a.get(k) != b.get(k):
            return k
    return None


def _renumber(rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    return [dict(r, seq=i + 1) for i, r in enumerate(rows)]


def tape_identity(on_rows: Sequence[Dict[str, object]], off_rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    non_mentor = [r for r in on_rows if (r.get("meta") or {}).get("source") != "mentor"]
    a, b = _renumber(non_mentor), _renumber(list(off_rows))
    n = 0
    for x, y in zip(a, b):
        n += 1
        f = _eq(x, y, skip=())
        if f is not None:
            return {"ok": False, "reason": f"field {f!r} differs at position {n}: {x.get(f)!r} != {y.get(f)!r}", "n_compared": n}
    if len(a) != len(b):
        return {"ok": False, "reason": f"row counts differ: ON-minus-mentor {len(a)} vs OFF {len(b)}", "n_compared": n}
    return {"ok": True, "reason": "", "n_compared": n}


def journal_confinement(off_rows: Sequence[Dict[str, object]], on_rows: Sequence[Dict[str, object]],
                        mentor_words_by_moment: Dict[str, List[str]]) -> Dict[str, object]:
    off_rows, on_rows = list(off_rows), list(on_rows)
    first_kind: Optional[str] = None
    n_diff: Dict[str, int] = {}
    n = min(len(off_rows), len(on_rows))
    for i in range(n):
        o, w = off_rows[i], on_rows[i]
        f = _eq(o, w)
        if f is None:
            continue
        kind = str(w.get("kind"))
        if first_kind is None:
            first_kind = kind
        n_diff[kind] = n_diff.get(kind, 0) + 1
        if kind != "brain":
            return {"ok": False, "reason": f"a differing non-brain row ({kind}) at position {i}, field {f!r}",
                    "first_diff_kind": first_kind, "n_diff_by_kind": n_diff}
        moment = str(w.get("moment", o.get("moment", "")))
        mentor = mentor_words_by_moment.get(moment, [])
        for field in ("heard", "words"):
            if field in w or field in o:
                o_l, w_l = list(o.get(field) or []), list(w.get(field) or [])
                extra = list(w_l)
                for v in o_l:
                    if v in extra:
                        extra.remove(v)
                stray = [v for v in extra if v not in mentor]
                if stray:
                    return {"ok": False, "reason": f"a heard delta outside the moment's mentor words at {moment}: {stray}",
                            "first_diff_kind": first_kind, "n_diff_by_kind": n_diff}
    if len(off_rows) != len(on_rows):
        return {"ok": False, "reason": f"journal row counts differ: OFF {len(off_rows)} vs ON {len(on_rows)}",
                "first_diff_kind": first_kind, "n_diff_by_kind": n_diff}
    return {"ok": True, "reason": "", "first_diff_kind": first_kind, "n_diff_by_kind": n_diff}
