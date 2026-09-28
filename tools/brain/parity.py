#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:07 +0400 — PREREG-BRAIN-IN-BODY §3 PARITY: the life's answers against rung 1's, item by item.
"""tools/brain/parity.py --journal <journal dir | journal.jsonl> --gate-answers <gate-answers.json> [--out F]

Every item rung 1's gate answered (the fresh set, every mark; the older set's pointing, keyed `older/<item>`) must have ONE
answer in the life's journal, and that answer — `Brain.ask`'s return as the mind journaled it — must EQUAL the gate's after
one JSON round trip (NaN equals NaN; ±Infinity equal themselves). Prints, per mark: asked by the gate · found in the life ·
equal · the first difference. Exit 0 only when every item is found and equal.
Control: --plant flips ONE number in ONE of the life's answers in memory; the tool must then exit non-zero."""
from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional


def _rows(journal: Path) -> List[dict]:
    files = sorted(journal.glob("*.jsonl")) if journal.is_dir() else [journal]
    out = []
    for f in files:
        with f.open(encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    return out


def first_diff(a, b, path: str = "") -> Optional[str]:
    if isinstance(a, float) and isinstance(b, float):
        if (math.isnan(a) and math.isnan(b)) or a == b:
            return None
        return f"{path} ({a!r} vs {b!r})"
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None:
        return None if (a is b or a == b and type(a) is type(b)) else f"{path} ({a!r} vs {b!r})"
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return None if float(a) == float(b) else f"{path} ({a!r} vs {b!r})"
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return f"{path}.{k} (only in {'the gate' if k in b else 'the life'})"
            d = first_diff(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path} (length {len(a)} vs {len(b)})"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    return None if a == b else f"{path} ({a!r} vs {b!r})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", required=True)
    ap.add_argument("--gate-answers", required=True)
    ap.add_argument("--by", default="brain")
    ap.add_argument("--plant", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    gate: Dict[str, dict] = json.loads(Path(a.gate_answers).read_text())
    life: Dict[str, dict] = {}
    dup = 0
    why_repeats = 0
    for r in _rows(Path(a.journal)):
        if r.get("kind") == "answer" and r.get("item") is not None and r.get("by") == a.by:
            if str(r["item"]) in life:
                # edit: Claude (Fable 5.1, the seat), 2026-09-28 21:23 +0400 — a `why` is asked again in a later sitting under one item
                # name; the first stands (PREREG §3). Any OTHER item answered twice is a fault and is counted.
                if r.get("form") == "why":
                    why_repeats += 1
                    continue
                dup += 1
            life[str(r["item"])] = json.loads(json.dumps(r.get("answer")))
    if a.plant:
        k = sorted(x for x in life if x.startswith("M1:") and isinstance((life[x].get("raw") or {}).get("best"), float))[0]
        life[k]["raw"]["best"] += 1e-9
        print(f"[parity] PLANTED: {k}.raw.best moved by 1e-9")
    per = collections.defaultdict(lambda: {"gate": 0, "found": 0, "equal": 0, "first": None})
    for key in sorted(gate):
        older = key.startswith("older/")
        item = key[len("older/"):] if older else key
        mark = ("older/" if older else "") + item.split(":")[0]
        p = per[mark]
        p["gate"] += 1
        if item not in life:
            p["first"] = p["first"] or f"{item}: not answered in the life"
            continue
        p["found"] += 1
        d = first_diff(life[item], json.loads(json.dumps(gate[key])), item)
        if d is None:
            p["equal"] += 1
        else:
            p["first"] = p["first"] or d
    tot = {k: sum(p[k] for p in per.values()) for k in ("gate", "found", "equal")}
    ok = tot["gate"] > 0 and tot["gate"] == tot["found"] == tot["equal"] and dup == 0
    lines = [f"PARITY · the life ({a.journal}) against rung 1 ({a.gate_answers}) · verdict {'EQUAL' if ok else 'DIFFERENT'}",
             f"  the gate answered {tot['gate']} · found in the life {tot['found']} · equal {tot['equal']} · items answered twice in the life {dup} (a later sitting's `why` repeats, not counted: {why_repeats}) · answers in the life by «{a.by}» {len(life)}",
             "  mark            gate   found   equal  first difference"]
    for mark in sorted(per):
        p = per[mark]
        lines.append(f"  {mark:<14} {p['gate']:>5} {p['found']:>7} {p['equal']:>7}  {p['first'] or '—'}")
    txt = "\n".join(lines)
    print(txt)
    if a.out:
        Path(a.out).write_text(txt + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
