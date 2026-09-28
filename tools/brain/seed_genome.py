#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:06 +0400 — BRAIN-IN-BODY: one genome at another world seed, and the null's genome.
"""tools/brain/seed_genome.py --in G --seed WS [--utterance-shuffled K] --out G2

Writes G2 = G with EXACTLY these tokens changed: the SEED line's number, the `WORLD scene seed <n>` number, and — when asked
— `utterance true` → `utterance shuffled K`. Refuses unless both seed tokens are found once and equal in G (a life's SEED
is its world's seed), and unless the parsed genomes differ in nothing but those values. Comments are kept byte for byte."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from genome.machinery import parse_genome


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--utterance-shuffled", type=int)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    text = Path(a.src).read_text()
    m1 = re.findall(r"^(SEED\s+)(\d+)", text, flags=re.M)
    m2 = re.findall(r"^(WORLD\s+scene seed )(\d+);", text, flags=re.M)
    if len(m1) != 1 or len(m2) != 1 or m1[0][1] != m2[0][1]:
        print(f"refused: SEED {m1} and WORLD scene seed {m2} must each appear once and be equal", file=sys.stderr)
        return 2
    out = re.sub(r"^(SEED\s+)\d+", lambda m: m.group(1) + str(a.seed), text, count=1, flags=re.M)
    out = re.sub(r"^(WORLD\s+scene seed )\d+;", lambda m: m.group(1) + str(a.seed) + ";", out, count=1, flags=re.M)
    if a.utterance_shuffled is not None:
        n = len(re.findall(r"^WORLD\s+scene .*; utterance true", out, flags=re.M))
        if n != 1:
            print("refused: no `utterance true` on the WORLD scene line", file=sys.stderr)
            return 2
        out = re.sub(r"^(WORLD\s+scene .*; utterance )true", lambda m: m.group(1) + f"shuffled {a.utterance_shuffled}", out,
                     count=1, flags=re.M)
    g0, g1 = parse_genome(text), parse_genome(out)
    d0, d1 = dict(g0.declared), dict(g1.declared)
    w0, w1 = dict(d0.pop("WORLD_SCENE")), dict(d1.pop("WORLD_SCENE"))
    w0.pop("seed"); w1.pop("seed")
    u0, u1 = w0.pop("utterance"), w1.pop("utterance")
    want_u = "true" if a.utterance_shuffled is None else {"shuffled": a.utterance_shuffled}
    if d0 != d1 or w0 != w1 or u1 != want_u or g1.declared["WORLD_SCENE"]["seed"] != a.seed or g1.seed != a.seed:
        print("refused: the two genomes differ in more than the seed (and the utterance)", file=sys.stderr)
        return 3
    if (g0.retina, g0.gaze, g0.colour) != (g1.retina, g1.gaze, g1.colour):
        print("refused: the eye changed", file=sys.stderr)
        return 3
    changed = [(x, y) for x, y in zip(text.splitlines(), out.splitlines()) if x != y]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(out)
    print(f"wrote {a.out}: {len(changed)} lines changed; seed {a.seed}; utterance {u1}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
