#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-21 21:04 +0400 — the G5 landings: compare two replay journals (or a replay against a live journal)
# field by field over MIND rows, with a declared ignore set (default: `hash` — Builder F's live-block state_hash changed
# that field's value on every row by design, so byte-identity of the journal is now "identical except hash"). Prints the
# counts and the FIRST differing (seq, field, a, b) and any key present on one side only (a new journal field is a
# format change to record, never silently a match — the advisor's rule, 2026-09-21). Exit 0 iff no non-ignored diff.
#
# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:5x +0400 — this file carried its OWN duplicate of
# creature/replay.py's "mind row" filter (a blanket `"event" not in r`), which had the SAME gap that file's
# own fix addresses (docs/ALPHA4-PREREG.md §4/§6: the mind itself now journals semantic "event" rows —
# "stage", "epoch" — that a blanket filter silently drops from THIS tool's own comparison too, the one
# `tools/gate_g5_landing.sh` actually runs for every builder's landing). Fixed by importing
# creature.replay's OWN `is_mind_row` instead of re-implementing it a second time — a definition kept in
# one place cannot drift out of sync with the other's fix the way these two already had.
"""usage: python3 tools/replay_diff.py A.jsonl B.jsonl [--ignore hash,other] [--label-a X --label-b Y]"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from creature.replay import is_mind_row as _is_mind_row


def mind_rows(path: str):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if _is_mind_row(r):
                out.append(r)
    return out


def main(argv):
    a_path, b_path = argv[0], argv[1]
    ignore = set((argv[argv.index("--ignore") + 1] if "--ignore" in argv else "hash").split(","))
    la = argv[argv.index("--label-a") + 1] if "--label-a" in argv else "A"
    lb = argv[argv.index("--label-b") + 1] if "--label-b" in argv else "B"
    A, B = mind_rows(a_path), mind_rows(b_path)
    n = min(len(A), len(B))
    ignored_only = other = 0
    first = None
    one_sided = set()
    for x, y in zip(A[:n], B[:n]):
        row_diff = False
        for k in sorted(set(x) | set(y)):
            if x.get(k) != y.get(k):
                if k in ignore:
                    ignored_only += 1
                    continue
                row_diff = True
                if k not in x or k not in y:
                    one_sided.add(k)
                if first is None:
                    first = (x.get("seq"), k, str(x.get(k))[:100], str(y.get(k))[:100])
        other += row_diff
    print(f"[replay_diff] {la}: {len(A)} mind rows · {lb}: {len(B)} mind rows · compared {n}")
    print(f"[replay_diff] rows differing ONLY in ignored fields {sorted(ignore)}: {ignored_only} · rows with a non-ignored diff: {other}")
    print(f"[replay_diff] first non-ignored diff (seq, field, {la}, {lb}): {first}")
    print(f"[replay_diff] keys present on one side only: {sorted(one_sided)}")
    ok = other == 0 and len(A) == len(B)
    print(f"[replay_diff] IDENTICAL except {sorted(ignore)}: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
