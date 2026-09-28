#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:44 +0400 — BRAIN-IN-BODY rung 3, the reviewer's B1 + B2 (REVIEW-BEFORE-RUNG3.md).
"""tools/brain/cut_tape.py --root <a CLOSED life's root> --out <dir>

In the full organism the other worlds keep publishing after the scene world has ended, and the body's stop leaves the rows
still in its queue unconsumed: the tape holds a TAIL the live mind never lived. A replay of the whole tape would live it,
and every identity check would fail for a reason that has nothing to do with the brain. SOLUTIONS #239: «the reader cuts at
the lived seq».

Writes, never touching the life's root:
  <out>/tape/<day>.jsonl   the tape's rows with seq <= the ledger's last_seq, day file by day file, in order
  <out>/tape/payload       a symlink to the life's own payload directory
  <out>/live-journal.jsonl the life's MIND rows of every journal day file, in order (creature.replay.is_mind_row) — ONE file
                           for `python3 -m creature.replay --against`, which reads one file (a life that crosses 00:00 UTC
                           has two day files)
Prints the tape's rows, the lived rows, the tail and the tail's senses. Refuses a root that is not closed (no STOPPED-AT)."""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
from pathlib import Path

from creature.replay import is_mind_row
from creature.tape import _resolve_tape_dir
from genome.machinery import parse_genome


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root, out = Path(a.root), Path(a.out)
    if not (root / "STOPPED-AT").exists():
        print(f"refused: {root} is not closed (no STOPPED-AT)", file=sys.stderr)
        return 2
    if out.exists() and any(out.iterdir()):
        print(f"refused: {out} exists and is not empty", file=sys.stderr)
        return 2
    g = parse_genome((root / "GENOME.genome").read_text())
    tape = _resolve_tape_dir(root, g.declared.get("TAPE", {}).get("path"))
    ledger = json.loads((root / "state" / "ledger.json").read_text())
    last = int(ledger["last_seq"])
    (out / "tape").mkdir(parents=True, exist_ok=True)
    total = lived = 0
    tail = collections.Counter()
    prev = 0
    for day in sorted(tape.glob("*.jsonl")):
        kept = []
        with day.open(encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                r = json.loads(line)          # a torn line raises here, named by the traceback's file and line: never skipped
                seq = int(r["seq"])
                if seq <= prev:
                    print(f"refused: {day}:{n} seq {seq} is not above the row before it ({prev})", file=sys.stderr)
                    return 3
                prev = seq
                total += 1
                if seq <= last:
                    lived += 1
                    kept.append(line if line.endswith("\n") else line + "\n")
                else:
                    tail[str(r.get("sense"))] += 1
        if kept:
            (out / "tape" / day.name).write_text("".join(kept), encoding="utf-8")
    os.symlink((tape / "payload").resolve(), out / "tape" / "payload")
    n_mind = 0
    with (out / "live-journal.jsonl").open("w", encoding="utf-8") as w:
        for day in sorted((root / "journal").glob("*.jsonl")):
            with day.open(encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        r = json.loads(line)
                        if is_mind_row(r):
                            w.write(json.dumps(r) + "\n")
                            n_mind += 1
    print(json.dumps({"root": str(root), "ledger_last_seq": last, "tape_rows": total, "lived_rows": lived,
                      "tail_rows": total - lived, "tail_by_sense": dict(sorted(tail.items())),
                      "tape_day_files": len(list(tape.glob("*.jsonl"))), "journal_day_files": len(list((root / "journal").glob("*.jsonl"))),
                      "live_mind_rows": n_mind}, indent=1))
    if lived != last:
        print(f"NOTE: {lived} lived rows against last_seq {last} — the tape has a hole or does not start at 1", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
