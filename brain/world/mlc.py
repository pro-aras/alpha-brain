"""mlc.py — THE MLC SIDE TAPE's row shape, validator and LEAK CHECK (B1-PREREG.md §4 A1-MLC, §5.5 (0g);
docs/brain/b1/SEAT-DECISIONS.md R19).

edit: Claude (Fable 5.1), 2026-09-24 18:14 +0400 — the seat, alone.

`brain/protocol.py` is FROZEN (its `CUE_MARKS` are the 14 real marks and `validate_tape_row` rejects any
other), so the MLC episodes' synthetic cues live in THEIR OWN row shape, validated here: the tape's five
fields + `sha` (computed by `brain.protocol.row_sha`, the same function), plus `after_seq` (the main-tape
FEEDBACK seq the row is interleaved after) and `episode`. Kinds: ASK and FEEDBACK only. Cues: exactly one of
`MLC0`..`MLC3` — episode e uses slot e mod 4, so a slot's meaning turns over every four episodes and a network
must read it from the study pairs, never from the slot. MLC seqs are offset by `MLC_SEQ_BASE` so they can
never collide with a main-tape seq in an arm's `why()` citations.

THE LEAK CHECK (0g) reads NOTHING from the truth file: each ASK's operand row is resolved to its glyph through
the cache INDEX (char per row — `brain.glance_cache.Cache.meta`), and the answer from the FEEDBACK's `right`;
the pair (x, y) is then tested against the order families' construction: |idx(y) − idx(x)| must not be 0, 1
or 2 (identity = OTHER_CASE's shape, ±1 = AFTER/BEFORE/BETWEEN's, ±2 = TWO_AFTER's — every held-out name
pair of every order family, in either direction, is one of these), and no MLC row may carry a real cue mark.
A planted +2 episode is the check's own negative control (`tests/brain/harness/test_mlc.py`).
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Sequence, Tuple

from brain.protocol import CUE_MARKS, ProtocolError, is_row_operand, row_sha

from .families import LETTER_NAMES
from .names import letter_name

MLC_SLOTS = 4
MLC_MARKS: Tuple[str, ...] = tuple(f"MLC{i}" for i in range(MLC_SLOTS))
MLC_SEQ_BASE = 1_000_000
MLC_FORBIDDEN_DIFFS = (0, 1, 2)


class MlcError(Exception):
    pass


def make_mlc_row(mlc_seq: int, after_seq: int, episode: int, kind: str, phase: str, item: str,
                 payload: Mapping[str, Any]) -> Dict[str, Any]:
    """One materialised MLC row (`seq` already OFFSET by MLC_SEQ_BASE; a FEEDBACK's `ask_seq` must be offset
    by the caller the same way — `validate_mlc_row` checks it is)."""
    payload = dict(payload)
    row = {"seq": MLC_SEQ_BASE + int(mlc_seq), "kind": kind, "phase": str(phase), "item": str(item),
           "payload": payload, "sha": row_sha(payload), "after_seq": int(after_seq), "episode": int(episode)}
    validate_mlc_row(row)
    return row


def validate_mlc_row(row: Mapping[str, Any]) -> None:
    for f in ("seq", "kind", "phase", "item", "payload", "sha", "after_seq", "episode"):
        if f not in row:
            raise MlcError(f"mlc row missing field {f!r}: {row!r}")
    if not isinstance(row["seq"], int) or row["seq"] < MLC_SEQ_BASE:
        raise MlcError(f"mlc row seq must be an int >= {MLC_SEQ_BASE}: {row['seq']!r}")
    if row["kind"] not in ("ASK", "FEEDBACK"):
        raise MlcError(f"mlc row kind must be ASK or FEEDBACK, got {row['kind']!r}")
    p = row["payload"]
    if row["kind"] == "ASK":
        for k in ("cues", "operands", "candidate_rows", "answer_kind"):
            if k not in p:
                raise MlcError(f"mlc ASK payload missing {k!r}")
        cues = p["cues"]
        if not isinstance(cues, list) or len(cues) != 1 or cues[0] not in MLC_MARKS:
            raise MlcError(f"mlc ASK cues must be exactly one of {MLC_MARKS}: {cues!r}")
        ops = p["operands"]
        if len(ops) != 1 or not is_row_operand(ops[0]) or not isinstance(ops[0]["value"], int):
            raise MlcError(f"mlc ASK needs exactly one glyph-row operand with an int value: {ops!r}")
        if p["candidate_rows"] is not None or p["answer_kind"] != "NAME":
            raise MlcError("mlc ASK is a NAME ask with no candidates")
    else:
        if not isinstance(p.get("ask_seq"), int) or p["ask_seq"] < MLC_SEQ_BASE:
            raise MlcError(f"mlc FEEDBACK ask_seq must be an offset mlc seq: {p.get('ask_seq')!r}")
        if not isinstance(p.get("right"), str) or p["right"] not in LETTER_NAMES:
            raise MlcError(f"mlc FEEDBACK right must be a letter name: {p.get('right')!r}")
    if row_sha(p) != row["sha"]:
        raise MlcError(f"mlc row {row['seq']} sha does not match its payload")


def leak_check(mlc_rows: Sequence[Mapping[str, Any]], char_of_row: Callable[[int], Tuple[str, str]]) -> Dict[str, Any]:
    """§5.5 (0g): `mlc.jsonl` checked WHOLE. `char_of_row(cache_row) -> (script, char)` is the cache index's
    own reading. Returns {pass, n_rows, n_pairs, violations: [...], checks: {...}} — every violation named,
    never a bare bool (#234)."""
    violations: List[Dict[str, Any]] = []
    asks: Dict[int, Mapping[str, Any]] = {}
    n_pairs = 0
    real_marks = set(CUE_MARKS)
    for row in mlc_rows:
        try:
            validate_mlc_row(row)
        except MlcError as e:
            violations.append({"kind": "malformed", "seq": row.get("seq"), "why": str(e)})
            continue
        if row["kind"] == "ASK":
            if any(c in real_marks for c in row["payload"]["cues"]):
                violations.append({"kind": "real_cue_mark", "seq": row["seq"], "cues": row["payload"]["cues"]})
            asks[row["seq"]] = row
    for row in mlc_rows:
        if row.get("kind") != "FEEDBACK":
            continue
        ask = asks.get(row["payload"]["ask_seq"])
        if ask is None:
            violations.append({"kind": "orphan_feedback", "seq": row["seq"]})
            continue
        script, ch = char_of_row(int(ask["payload"]["operands"][0]["value"]))
        if script not in ("latin-upper", "latin-lower"):
            violations.append({"kind": "operand_not_a_letter", "seq": ask["seq"], "script": script})
            continue
        x = letter_name(ch)
        y = row["payload"]["right"]
        n_pairs += 1
        d = abs(LETTER_NAMES.index(y) - LETTER_NAMES.index(x))
        if d in MLC_FORBIDDEN_DIFFS:
            violations.append({"kind": "order_family_pair", "seq": ask["seq"], "pair": [x, y], "diff": d,
                               "why": {0: "identity (OTHER_CASE's shape)", 1: "AFTER/BEFORE/BETWEEN's pair", 2: "TWO_AFTER's pair (+2)"}[d]})
    return {"pass": not violations, "n_rows": len(mlc_rows), "n_pairs": n_pairs, "violations": violations,
            "checks": {"no_real_cue_mark": not any(v["kind"] == "real_cue_mark" for v in violations),
                       "no_order_family_pair": not any(v["kind"] == "order_family_pair" for v in violations),
                       "well_formed": not any(v["kind"] in ("malformed", "orphan_feedback", "operand_not_a_letter") for v in violations)}}
