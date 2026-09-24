"""transforms.py — SHUFFLED-NAME and SHUFFLED-RELATION: the two twins that are TAPE transforms
(B1-PREREG.md §4 "Twins"; SEAT-DECISIONS R22, R23). Pure functions over the concrete tape rows; every changed
row gets its sha recomputed through `make_row`, so a transformed tape is itself a legitimate tape whose own
sha is recorded in the run's facts. Test-sitting rows (TEST_BEGIN…TEST_END) are NEVER transformed.

edit: Claude (Fable 5.1), 2026-09-24 18:31 +0400 — the seat, alone.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence, Tuple

from brain.protocol import RELATION_CUES, make_row
from brain.world.families import LETTER_NAMES
from brain.world.names import DIGIT_NAMES
from brain.world.seeds import substream

ALL_NAMES: Tuple[str, ...] = tuple(LETTER_NAMES) + tuple(DIGIT_NAMES)


def _bijection(seed: int, purpose: str, items: Sequence) -> Dict[Any, Any]:
    rng = substream(seed, purpose)
    perm = [int(i) for i in rng.permutation(len(items))]
    return {items[i]: items[perm[i]] for i in range(len(items))}


def _training_mask(rows: Sequence[Mapping[str, Any]]) -> List[bool]:
    out, in_sit = [], False
    for r in rows:
        if r["kind"] == "TEST_BEGIN":
            in_sit = True
        out.append(not in_sit)
        if r["kind"] == "TEST_END":
            in_sit = False
    return out


def _rebuild(row: Mapping[str, Any], payload: Mapping[str, Any]) -> Dict[str, Any]:
    return make_row(row["seq"], row["kind"], row["phase"], row["item"], payload)


def shuffled_name(rows: Sequence[Mapping[str, Any]], seed: int) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """R22: one seeded bijection over the 26 letter names + 10 digit names, applied to every name in the
    TRAINING rows: TEACH names, heard-name operands, and every FEEDBACK `right` that is a name."""
    m = _bijection(seed, "twin:shuffled-name", ALL_NAMES)
    mask = _training_mask(rows)
    kind_by_seq = {r["seq"]: r["payload"]["answer_kind"] for r in rows if r["kind"] == "ASK"}
    out = []
    for r, train in zip(rows, mask):
        if not train:
            out.append(dict(r))
            continue
        p = dict(r["payload"])
        changed = False
        if r["kind"] == "TEACH" and p["name"] in m:
            p["name"] = m[p["name"]]
            changed = True
        elif r["kind"] == "ASK":
            ops = []
            for op in p["operands"]:
                if op["kind"] == "name" and op["value"] in m:
                    ops.append({"kind": "name", "value": m[op["value"]]})
                    changed = True
                else:
                    ops.append(dict(op))
            p["operands"] = ops
        elif r["kind"] == "FEEDBACK":
            if kind_by_seq.get(p["ask_seq"]) == "NAME" and p["right"] in m:
                p["right"] = m[p["right"]]
                changed = True
        out.append(_rebuild(r, p) if changed else dict(r))
    return out, m


def shuffled_relation(rows: Sequence[Mapping[str, Any]], seed: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """R23: per relation cue, a seeded bijection over the names (NAME answers) or the 26 sheet indices (PICK
    answers) replaces the training FEEDBACK `right`; YESNO cues get a per-item seeded coin."""
    mask = _training_mask(rows)
    asks = {r["seq"]: r for r in rows if r["kind"] == "ASK"}
    maps: Dict[str, Any] = {}
    out = []
    for r, train in zip(rows, mask):
        if not train or r["kind"] != "FEEDBACK":
            out.append(dict(r))
            continue
        ask = asks[r["payload"]["ask_seq"]]
        cues = ask["payload"]["cues"]
        if not any(c in RELATION_CUES for c in cues):
            out.append(dict(r))
            continue
        cue_key = "+".join(cues)
        kind = ask["payload"]["answer_kind"]
        p = dict(r["payload"])
        if kind == "NAME":
            mp = maps.setdefault(cue_key, _bijection(seed, f"twin:shuffled-relation:{cue_key}", ALL_NAMES))
            p["right"] = mp.get(p["right"], p["right"])
        elif kind == "PICK":
            n = len(ask["payload"]["candidate_rows"] or [])
            mp = maps.setdefault(f"{cue_key}:pick:{n}", _bijection(seed, f"twin:shuffled-relation:{cue_key}:pick:{n}", list(range(n))))
            p["right"] = int(mp[int(p["right"])]) if int(p["right"]) in mp else p["right"]
        elif kind == "YESNO":
            coin = int(substream(seed, f"twin:shuffled-relation:{cue_key}:{r['seq']}").integers(0, 2))
            p["right"] = "YES" if coin else "NO"
            maps.setdefault(f"{cue_key}:yesno", "per-item seeded coin (R23)")
        out.append(_rebuild(r, p))
    return out, {k: (v if isinstance(v, str) else {str(a): b for a, b in v.items()}) for k, v in maps.items()}
