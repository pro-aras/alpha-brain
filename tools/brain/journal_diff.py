#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:28 +0400 — PREREG-BRAIN-IN-BODY §3 «the brain does not disturb the organs».
"""tools/brain/journal_diff.py --a <journal> --b <journal> [--keep-answers]

Compares two journals of ONE tape row by row after dropping the brain's own rows (`kind: "brain"`) and, unless
--keep-answers, the answer rows (`kind: "answer"`: the brain's and the organs' answers differ by design). Every other row
must be byte-identical (json.dumps, keys sorted) and in the same order; the organism's hash rides on its canvas rows, so an
equal last hash is an equal organism. Prints the counts, the first difference, and the last `hash` of each side.
Control: --plant changes one character of one kept row of side b in memory; the tool must then exit non-zero."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def rows(p: Path):
    files = sorted(p.glob("*.jsonl")) if p.is_dir() else [p]
    out = []
    for f in files:
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    out.append(json.loads(line))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--keep-answers", action="store_true")
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    drop = {"brain"} if a.keep_answers else {"brain", "answer"}
    # a journal written by the body also carries the body's own event rows (seq None: start / snapshot / stop); a replay's
    # journal.jsonl holds mind rows only — the mind's rows are the ones with an integer seq
    A = [r for r in rows(Path(a.a)) if r.get("kind") not in drop and isinstance(r.get("seq"), int)]
    B = [r for r in rows(Path(a.b)) if r.get("kind") not in drop and isinstance(r.get("seq"), int)]
    sa = [json.dumps(r, sort_keys=True) for r in A]
    sb = [json.dumps(r, sort_keys=True) for r in B]
    if a.plant and sb:
        k = len(sb) // 2
        sb[k] = sb[k][:-2] + ("0" if sb[k][-2] != "0" else "1") + sb[k][-1]
        print(f"[journal_diff] PLANTED: one character of kept row {k} of side b")
    first = None
    for i, (x, y) in enumerate(zip(sa, sb)):
        if x != y:
            first = (i, A[i].get("seq"), x[:160], y[:160])
            break
    same = first is None and len(sa) == len(sb)
    ha = next((r["hash"] for r in reversed(A) if r.get("hash") is not None), None)
    hb = next((r["hash"] for r in reversed(B) if r.get("hash") is not None), None)
    print(f"JOURNAL DIFF · dropped kinds {sorted(drop)} · kept rows a {len(sa)} · b {len(sb)} · verdict {'IDENTICAL' if same else 'DIFFERENT'}")
    print(f"  the last organism hash: a {ha} · b {hb} · {'equal' if ha == hb and ha is not None else 'NOT equal'}")
    if first:
        print(f"  first difference at kept row {first[0]} (seq {first[1]}):\n    a {first[2]}\n    b {first[3]}")
    return 0 if same and ha == hb else 1


if __name__ == "__main__":
    sys.exit(main())
