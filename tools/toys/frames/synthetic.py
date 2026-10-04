"""synthetic.py — TOY C's structure-free SYNTHETIC streams and the architect's 17:1x check (does NULL-1's q95 let a noise frame read LOUD by arithmetic alone?).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:49 +0400 — new module, red-first against tests/tools/test_toys_frames_synthetic.py (stage 3f).

S1 `structure_free_scene`: G6's sampler (the generator's own constants) at G4's size, its words shuffled the law's way (train words among train positions, held-out words among held-out positions,
the moments' sizes kept, seed 1) — the SHUFFLE of a stream whose true structure is known.
S2 `structure_free_alpha`: a stream in ALPHA4's REGIME, built only from numbers the law's §0 already prints — the words-a-moment histogram of the 84,275 moments (73,088 / 2,403 / 592 / 8,179 / 1 / 12
of 1, 2, 3, 4, 7, 8 words) and the words each source delivered (maker 35,294 over 17 distinct, game 3,148 over 9, folder 306 over 11, lexicon 117 over 84, shelf 73,624 over 3,290) — with every word
drawn INDEPENDENTLY from that mixture (the shelf's words Zipf-distributed, exponent 1): structure-free by construction, a different draw from anything in the real stream and never a reading of it.

  PYTHONPATH=. python3 -m tools.toys.frames.synthetic check [--out DIR]     # every rule, both nulls and the anatomy on S1 and S2 (run it through slot)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

import numpy as np

from . import evaluate as EV
from . import scene as SC
from . import streams as ST

SEED_ROOT = 20261103
ALPHA_TAG = 9                                                    # default_rng([20261103, 9, seed])
ALPHA_SIZES = {1: 73088, 2: 2403, 3: 592, 4: 8179, 7: 1, 8: 12}  # the law's §0 words-a-moment, summed over the sources (84,275 moments)
ALPHA_MIX = (("mk", 17, 35294), ("gm", 9, 3148), ("fo", 11, 306), ("lx", 84, 117), ("sh", 3290, 73624))   # (prefix, distinct words, words delivered)
ALPHA_ZIPF_PREFIX = "sh"


def structure_free_scene(n: int = 3000, k: int = 1) -> Tuple[List[ST.Moment], List[ST.Moment]]:
    ms = SC.sample_moments(n, np.random.default_rng([SEED_ROOT, SC.G6_TAG, int(k)]))
    i = ST.split_index(len(ms))
    sh = ST.shuffled(ms, i, 1)
    return list(sh[:i]), list(sh[i:])


def structure_free_alpha(n: int = 84275, seed: int = 1) -> Tuple[List[ST.Moment], List[ST.Moment]]:
    rng = np.random.default_rng([SEED_ROOT, ALPHA_TAG, int(seed)])
    words: List[str] = []
    probs: List[float] = []
    total = sum(w for _p, _d, w in ALPHA_MIX)
    for prefix, distinct, delivered in ALPHA_MIX:
        if prefix == ALPHA_ZIPF_PREFIX:
            z = 1.0 / np.arange(1, distinct + 1)
            z = z / z.sum()
        else:
            z = np.full(distinct, 1.0 / distinct)
        for i in range(distinct):
            words.append(f"{prefix}{i:04d}")
            probs.append(float(z[i]) * delivered / total)
    p = np.asarray(probs)
    p = p / p.sum()
    sizes_k = sorted(ALPHA_SIZES)
    sp = np.asarray([ALPHA_SIZES[s] for s in sizes_k], dtype=float)
    sp = sp / sp.sum()
    sizes = [int(sizes_k[j]) for j in rng.choice(len(sizes_k), size=n, p=sp)]
    flat = rng.choice(len(words), size=sum(sizes), p=p)
    ms: List[ST.Moment] = []
    pos = 0
    for i, s in enumerate(sizes):
        w = tuple(words[int(j)] for j in flat[pos:pos + s])
        ms.append(ST.Moment("synthetic", f"a{i:06d}", w, tuple(float(pos + t) for t in range(s))))
        pos += s
    tr, he = ST.split(ms)
    return list(tr), list(he)


def _main(argv: Sequence[str]) -> int:
    if not argv or argv[0] != "check":
        print(__doc__)
        return 64
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    draws = int(argv[argv.index("--draws") + 1]) if "--draws" in argv else 100
    streams = (("S1 scene-shuffled (G6's sampler, 3,000 moments, words shuffled, seed 1)", lambda: structure_free_scene(3000, 1), "S1-scene-shuffled"),
               ("S2 ALPHA4-regime i.i.d. (84,275 moments, Zipf shelf tail)", lambda: structure_free_alpha(84275, 1), "S2-alpha-regime"))
    for title, make, key in streams:
        tr, he = make()
        cond = EV.evaluate_condition(tr, he, name=title, draws=draws, web_seeds=EV.SEEDS)
        text = EV.quiet_text(cond)
        print(text, flush=True)
        if out:
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{key}.json").write_text(json.dumps(cond, sort_keys=True))
            (out / f"{key}.txt").write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
