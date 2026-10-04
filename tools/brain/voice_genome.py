#!/usr/bin/env python3
# edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-04 19:05 +0400 — new tool: PREREG-W1-MOUTH-VOICES-BRAIN §3 (SIGNED x3 at
# toys-1003 1ccc3bf): the bench's ON genome = a DRIVE genome plus the W1 clause, nothing else (tools/brain/drive_genome.py's own form).
"""tools/brain/voice_genome.py --in G --out G2

Writes G2 = G's text, byte for byte, but for ONE line: the MOUTH line in the W1 spelling
«MOUTH    say one frame per think and the brain's phrase per canvas; journaled» (PREREG-W1-MOUTH-VOICES-BRAIN §3):
  - a lean DRIVE genome (its MOUTH line commented «#OFF MOUTH …»): the commented line is REPLACED by the active new line;
  - the full DRIVE genome (an active MOUTH line in the old spelling): that line is REPLACED by the new line.
Refuses when G2 exists, when G carries no MOUTH line in the old spelling (active or #OFF), when G already declares the
clause, or when the two parsed genomes would differ in anything but the MOUTH key (one text line, one parsed key)."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from genome.machinery import parse_genome   # noqa: E402

OLD_ARGS = "say one frame per think; journaled"
NEW_LINE = "MOUTH    say one frame per think and the brain's phrase per canvas; journaled"
NEW_KEY = {"say": "one frame per think", "journaled": True, "brain": "phrase per canvas"}
_ACTIVE = re.compile(r"^MOUTH\s+say one frame per think; journaled\s*$")
_OFF = re.compile(r"^#OFF\s+MOUTH\s+say one frame per think; journaled\s*(#.*)?$")


def mouth_line(lines: list) -> int:
    """The ONE line carrying the old-spelling MOUTH (active or #OFF); -1 none, -2 several."""
    found = [i for i, raw in enumerate(lines)
             if _ACTIVE.match(raw.split("#", 1)[0].strip()) or _OFF.match(raw.strip())]
    if len(found) > 1:
        return -2
    return found[0] if found else -1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    src, out = Path(a.src), Path(a.out)
    if out.exists():
        print(f"refused: {out} exists (a genome of record is never overwritten)", file=sys.stderr)
        return 2
    text = src.read_text()
    g0 = parse_genome(text)
    if "brain" in (g0.declared.get("MOUTH") or {}):
        print(f"refused: {src} already declares the W1 clause (MOUTH {g0.declared['MOUTH']})", file=sys.stderr)
        return 2
    lines = text.splitlines()
    i = mouth_line(lines)
    if i < 0:
        print(f"refused: {src} carries no MOUTH line in the old spelling (active or #OFF; found "
              f"{'several' if i == -2 else 'none'})", file=sys.stderr)
        return 2
    was_off = lines[i].strip().startswith("#OFF")
    lines[i] = NEW_LINE + (f"   # {a.note}" if a.note else "")
    new = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    g1 = parse_genome(new)
    d0, d1 = dict(g0.declared), dict(g1.declared)
    m0, m1 = d0.pop("MOUTH", None), d1.pop("MOUTH", None)
    fields = [k for k in vars(g0) if k != "declared" and k != "text"]
    moved = [k for k in fields if repr(getattr(g0, k)) != repr(getattr(g1, k))]
    if m1 != NEW_KEY or d0 != d1 or moved:
        print(f"refused: the two genomes differ in more than the MOUTH clause (declared-minus-MOUTH equal: {d0 == d1}; "
              f"the new MOUTH: {m1}; fields moved: {moved})", file=sys.stderr)
        return 3
    if was_off and m0 is not None:
        print(f"refused: a #OFF MOUTH line must not declare a key (got {m0})", file=sys.stderr)
        return 3
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(new)
    print(f"wrote {out}: {src.name}'s {'#OFF ' if was_off else ''}MOUTH line -> the W1 spelling; MOUTH = {m1}; "
          f"every other parsed key equal: {d0 == d1}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
