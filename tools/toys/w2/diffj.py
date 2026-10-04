"""tools/toys/w2/diffj.py — PREREG-W2 §3 item 1: the I2 readers — the tape identity and the journal confinement profile.

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:35 +0400 — new file, written after tests/tools/test_w2_bench.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 item 1. **The journal confinement's exact form is RAISED to
the seat (the board ASK-SEAT of 2026-10-05; the measured profile goes with it): the law's signed sentence («every other row
equal») cannot hold once the first mentor word teaches. This module implements the PROPOSED, measured form, PENDING the
seat's ruling.**

The mechanics it encodes (all measured on the pilot's prefix): the replay's rows group by (moment, family) — never by
file index (the coarse/glance acts interleave with the brain's rows differently between two runs, and the insertion shifts
every seq after the first mentor row). Per row family, the fields come in three classes:
- **delivery / eye-side** (`EQUAL_FIELDS`): must be equal field by field, except "seq" (normalized) — a difference there
  is a confinement violation, named;
- **word lists** (`heard`, `words`, `attributed`, `word`, `births`): the ON delta over OFF must sit inside that moment's
  mentor words (a stray word is a violation, named);
- **state / downstream** (hash, held, expected, say, ask, surprise, none, calibrated, edges, err, lr, ep, cells,
  act_chosen, think content, counters): the cells' and the brain's own hearing changes these from the first mentor word
  on — they are PROFILED and counted by family, never equal-required (the world's whole point), and their differences are
  what the seat's ruling reads.
Count differences of a family at a moment are reported, never hidden.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

EQUAL_FIELDS = {
    "brain": {"turn": {"moment", "at", "scene", "n_hyp", "order", "members"},
                "learn": {"moment", "at", "fix", "hyps", "n_hyp"}},
    "act:coarse": {"moment", "glance"},
    "act:glance": {"moment", "fix", "windows", "when"},
}
WORDLIST_FIELDS = ("heard", "words", "attributed")
SKIP = ("seq",)


def _eq(a: Dict[str, object], b: Dict[str, object], skip: Sequence[str] = SKIP) -> Optional[str]:
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


def _family(row: Dict[str, object]) -> str:
    if row.get("kind") is not None:
        return str(row["kind"]) + ":" + str(row.get("act"))
    if row.get("act") is not None and not isinstance(row["act"], dict):
        return "act:" + str(row["act"])
    return "plain"


def _words_of(row: Dict[str, object], field: str) -> List[str]:
    v = row.get(field)
    if field == "attributed" and isinstance(v, dict):
        return list(v.keys())
    if isinstance(v, list) and all(isinstance(x, str) for x in v):
        return list(v)
    if isinstance(v, str):
        return [v]
    return []


def _group(rows: Sequence[Dict[str, object]]) -> Dict[Tuple[str, str], List[Dict[str, object]]]:
    """Rows grouped by (moment, family); moment-free rows under ("", family), in append order."""
    out: Dict[Tuple[str, str], List[Dict[str, object]]] = {}
    for r in rows:
        out.setdefault((str(r.get("moment", "")), _family(r)), []).append(r)
    return out


def _equal_fields(fam: str) -> set:
    if fam.startswith("brain:"):
        return EQUAL_FIELDS["brain"].get(fam.split(":", 1)[1], set())
    return EQUAL_FIELDS.get(fam, set())


def journal_profile(off_rows: Sequence[Dict[str, object]], on_rows: Sequence[Dict[str, object]],
                    mentor_words_by_moment: Dict[str, List[str]]) -> Dict[str, object]:
    """The classified difference profile (the seat's ruling reads this): violations = delivery-field differences and
    stray word-list deltas; downstream = state-field differences and family count differences, counted by family."""
    go, gw = _group(off_rows), _group(on_rows)
    violations: List[str] = []
    downstream: Dict[str, int] = {}
    first: Optional[str] = None
    for key in sorted(set(go) | set(gw)):
        moment, fam = key
        os_, ws = go.get(key, []), gw.get(key, [])
        if len(os_) != len(ws):
            downstream[fam + "#count"] = downstream.get(fam + "#count", 0) + abs(len(os_) - len(ws))
            continue
        eqf = _equal_fields(fam)
        for o, w in zip(os_, ws):
            if _eq(o, w) is None:
                continue
            if first is None:
                first = f"{fam}@{moment or '?'}"
            row_diff = False
            for f in sorted((set(o) | set(w)) - set(SKIP)):
                if o.get(f) == w.get(f):
                    continue
                row_diff = True
                if f in eqf:
                    violations.append(f"{fam}@{moment or '?'}: delivery field {f!r} differs: {o.get(f)!r} != {w.get(f)!r}")
                elif f in WORDLIST_FIELDS:
                    extra = _words_of(w, f)
                    for v in _words_of(o, f):
                        if v in extra:
                            extra.remove(v)
                    mentor = mentor_words_by_moment.get(moment, [])
                    for v in extra:
                        if v not in mentor:
                            violations.append(f"{fam}@{moment or '?'}: word-list delta outside the mentor words: {v!r}")
            if row_diff:
                downstream[fam] = downstream.get(fam, 0) + 1
    return {"violations": violations, "downstream": downstream, "first": first,
            "n_diff": sum(downstream.values()), "families": sorted({fam for _, fam in set(go) | set(gw)})}


def journal_confinement(off_rows: Sequence[Dict[str, object]], on_rows: Sequence[Dict[str, object]],
                        mentor_words_by_moment: Dict[str, List[str]]) -> Dict[str, object]:
    """The confinement gate over the profile: ok iff no delivery-field difference and no stray word-list delta.
    The downstream profile is attached (the seat's ruling reads it)."""
    prof = journal_profile(off_rows, on_rows, mentor_words_by_moment)
    if prof["violations"]:
        return {"ok": False, "reason": prof["violations"][0], "first_diff_kind": prof["first"], "profile": prof}
    return {"ok": True, "reason": "", "first_diff_kind": prof["first"],
            "n_diff_by_kind": dict(prof["downstream"]), "profile": prof}
