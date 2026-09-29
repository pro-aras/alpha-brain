#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-29 16:38 +0400 — PREREG-BRAIN-DRIVES §3: the gate's ON genome = a genome plus the DRIVE line, nothing else
# (tools/brain/drive_genome.py's own form).
"""tools/brain/drive_genome.py --in G --out G2 [--says 0|1] [--asks 0|1]

Writes G2 = G's text, byte for byte, plus ONE line: the gene DRIVE (PREREG-BRAIN-DRIVES §2.1). Refuses when G already declares
DRIVE, when G2 exists, or when the two parsed genomes differ in anything but the key DRIVE (one text line, one parsed key)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from genome.machinery import parse_genome   # noqa: E402

DRIVE_LINE = "DRIVE    brain turn before hearing; says {says}; asks {asks}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--note", default="")
    ap.add_argument("--says", type=int, default=1, choices=(0, 1))
    ap.add_argument("--asks", type=int, default=1, choices=(0, 1))
    a = ap.parse_args()
    src, out = Path(a.src), Path(a.out)
    if out.exists():
        print(f"refused: {out} exists (a genome of record is never overwritten)", file=sys.stderr)
        return 2
    text = src.read_text()
    g0 = parse_genome(text)
    if "DRIVE" in g0.declared:
        print(f"refused: {src} already declares DRIVE", file=sys.stderr)
        return 2
    line = DRIVE_LINE.format(says=a.says, asks=a.asks) + (f"   # {a.note}" if a.note else "")
    new = text + ("" if text.endswith("\n") else "\n") + line + "\n"
    g1 = parse_genome(new)
    d0, d1 = dict(g0.declared), dict(g1.declared)
    hear = d1.pop("DRIVE", None)
    fields = [k for k in vars(g0) if k != "declared" and k != "text"]
    moved = [k for k in fields if repr(getattr(g0, k)) != repr(getattr(g1, k))]
    if hear is None or d0 != d1 or moved:
        print(f"refused: the two genomes differ in more than DRIVE (declared equal: {d0 == d1}; fields moved: {moved})", file=sys.stderr)
        return 3
    if not new.startswith(text):
        print("refused: the old text is not a prefix of the new", file=sys.stderr)
        return 3
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(new)
    print(f"wrote {out}: {src.name} + 1 line; DRIVE = {hear}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
