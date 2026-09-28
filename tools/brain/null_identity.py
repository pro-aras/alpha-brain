#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:28 +0400 — PREREG-BRAIN-IN-BODY §3 THE NULL: the replayed shuffled tape against the offline null.
"""tools/brain/null_identity.py --journal <the null replay's journal> --offline <answers-<ws>-k<k>.json>

The offline null (tools/brain/null_k1_answers.py, equal to the scored record's scores) answers M1 and M3 only. Item by item:
  POINTING  `point`, `best`, `scores` — what the null learner points at, and how strongly
  WHOLE     the whole offline dict against the life's `raw`
Printed apart, because the offline null was never calibrated (run.run_null trains and answers, no reading point), so its
«none» flags are computed without τ; the body's brain calibrates before a sitting. A difference in WHOLE that is not in
POINTING is that, and is named by its keys. Exit 0 when POINTING is equal on every item."""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", required=True)
    ap.add_argument("--offline", required=True)
    a = ap.parse_args()
    off = json.loads(Path(a.offline).read_text())["point"]
    p = Path(a.journal)
    life = {}
    for f in (sorted(p.glob("*.jsonl")) if p.is_dir() else [p]):
        for line in f.open(encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                if r.get("kind") == "answer" and r.get("item") is not None:
                    ans = r.get("answer") or {}
                    raw = ans.get("raw_forced") if (ans.get("raw") or {}).get("misuse") is not None else ans.get("raw")
                    life.setdefault(str(r["item"]), json.loads(json.dumps(raw)))
    n = found = pointing = whole = 0
    keys = collections.Counter()
    first = None
    for item, o in sorted(off.items()):
        n += 1
        o = json.loads(json.dumps(o))
        l = life.get(item)
        if l is None:
            first = first or f"{item}: not answered"
            continue
        found += 1
        ok = all(l.get(k) == o.get(k) for k in ("point", "best", "scores"))
        pointing += int(ok)
        if not ok:
            first = first or f"{item}: point {l.get('point')} vs {o.get('point')} · best {l.get('best')} vs {o.get('best')}"
        if l == o:
            whole += 1
        else:
            for k in sorted(set(l) | set(o)):
                if l.get(k) != o.get(k):
                    keys[k] += 1
    print(f"NULL IDENTITY · offline items {n} · found in the replay {found} · POINTING equal {pointing} · WHOLE equal {whole}")
    print(f"  keys that differ, by count: {dict(keys)}")
    print(f"  first pointing difference: {first or '—'}")
    return 0 if n > 0 and pointing == n else 1


if __name__ == "__main__":
    sys.exit(main())
