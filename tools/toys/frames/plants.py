"""plants.py — TOY C's conditions (plain / PLANT / SHUFFLE) and the PLANT gate's readings (docs/research/toys/PREREG-TOY-FRAMES.md §3, §4, §7 G4).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:03 +0400 — new module, red-first against tests/tools/test_toys_frames_plants.py (stage 3a: the PERFECT-MECHANISM reading).

A CONDITION is a stream turned into (train moments, held-out moments): `plain` = the 60/40 split; `plant` = a NEW moment [zzq, xxv] inserted after every `every`-th moment (100 on
ALPHA4, 10 on SCENE) and THEN the split (so about 60 % of the plants land in train); `shuffle` = the train words permuted among the train positions and the held-out words among the
held-out positions (the moments' sizes kept), seed 1, then the same split.

THE PERFECT-MECHANISM READING (the seat's 17:0x question, before AMENDMENT-1): what the ORIGINAL whole-set clause «each such set's G > 0» reads for a mechanism that finds the planted
frame EXACTLY and keeps nothing else, i.e. G({(zzq, xxv)}) on the planted split, beside its control — the same one-frame set on the PLAIN split, where it never fires.

  PYTHONPATH=. python3 -m tools.toys.frames.plants perfect [--out FILE]     # both real streams, from the copies (run it through slot)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from . import compress as CO
from . import streams as ST

PLANT_EVERY: Dict[str, int] = {"ALPHA4": 100, "SCENE": 10}


def words_of(moments: Sequence[ST.Moment]) -> List[Tuple[str, ...]]:
    return [m.words for m in moments]


def condition_parts(moments: Sequence[ST.Moment], kind: str, every: Optional[int] = None, shuffle_seed: int = 1) -> Tuple[List[ST.Moment], List[ST.Moment]]:
    """(train moments, held-out moments) of a condition."""
    if kind == "plain":
        return ST.split(moments)
    if kind == "plant":
        if not every:
            raise ValueError("a plant condition needs `every`")
        return ST.split(ST.with_plant(moments, every))
    if kind == "shuffle":
        n_train = ST.split_index(len(moments))
        sh = ST.shuffled(moments, n_train, shuffle_seed)
        return list(sh[:n_train]), list(sh[n_train:])
    raise ValueError(f"condition kind {kind!r} is not plain | plant | shuffle")


def n_plants(part: Sequence[ST.Moment]) -> int:
    return sum(1 for m in part if m.source == "plant")


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:09 +0400 — G1's plant-token premise: how often each plant token occurs as a word of a REAL (non-plant) moment (law §3 calls both «in no vocabulary»; AMENDMENT-1).
def plant_token_occurrences(moments: Sequence[ST.Moment]) -> Dict[str, int]:
    out = {t: 0 for t in ST.PLANT}
    for m in moments:
        if m.source == "plant":
            continue
        for w in m.words:
            if w in out:
                out[w] += 1
    return out


def first_order_saving(plants_held: int, n_train_tokens: int, plants_train: int, V: int) -> Optional[float]:
    """The architect's expected value of the planted frame's gain (17:0x ruling): n_held_plants x log2(N_train / n_train_plants) − 2 log2 V (None without a train plant)."""
    if plants_train < 1:
        return None
    return plants_held * math.log2(n_train_tokens / plants_train) - 2.0 * math.log2(V)


def perfect_reading(moments: Sequence[ST.Moment], every: int) -> Dict[str, object]:
    """G of the one-frame set {PLANT} on the planted split (a mechanism that found the planted frame exactly), and the same set on the PLAIN split (its control)."""
    tr, he = condition_parts(moments, "plant", every)
    sc = CO.Scorer(words_of(tr), words_of(he))
    g = sc.gain({ST.PLANT})
    ptr, phe = n_plants(tr), n_plants(he)
    ptr_moments, phe_moments = condition_parts(moments, "plain")
    sp = CO.Scorer(words_of(ptr_moments), words_of(phe_moments))
    gp = sp.gain({ST.PLANT})
    return {"every": every, "n_moments": len(tr) + len(he), "n_train": len(tr), "n_held": len(he), "plants_train": ptr, "plants_held": phe,
            "V": g.V, "N": g.N, "K": g.K, "n_train_tokens_empty": sc.n0, "bits0": g.bits0, "bitsF": g.bitsF, "L": g.L, "G": g.G,
            "expected_first_order": first_order_saving(phe, sc.n0, ptr, g.V),
            "control_plain_G": gp.G, "control_plain_L": gp.L, "control_plain_bitsF_minus_bits0": gp.bitsF - gp.bits0}


# ------------------------------------------------------------------------------------------------------------------ the command line
def _real_streams() -> Dict[str, List[ST.Moment]]:
    a4 = ST.load_moments(sorted((ST.COPIES / "alpha4-1" / "tape").glob("*.jsonl")))
    bf = ST.scene_moments(ST.load_moments(sorted((ST.COPIES / "brain-full-20261102" / "tape").glob("*.jsonl"))))
    return {"ALPHA4": a4, "SCENE": bf}


def _main(argv: Sequence[str]) -> int:
    if not argv or argv[0] != "perfect":
        print(__doc__)
        return 64
    out = None
    if "--out" in argv:
        out = Path(argv[argv.index("--out") + 1])
    streams = _real_streams()
    res: Dict[str, object] = {}
    for name, ms in streams.items():
        r = perfect_reading(ms, PLANT_EVERY[name])
        res[name] = r
        print(f"{name}+PLANT (every {r['every']}): {r['n_moments']} moments (train {r['n_train']}, held {r['n_held']}); plants train {r['plants_train']} held {r['plants_held']}; "
              f"V {r['V']} N {r['N']} K {r['K']}; bits0 {r['bits0']:.1f} bitsF {r['bitsF']:.1f} L {r['L']:.2f} -> G({{plant}}) = {r['G']:+.2f} bits "
              f"(first-order expected {r['expected_first_order']:.1f}); control (the same frame on the PLAIN split) G {r['control_plain_G']:+.2f}, L {r['control_plain_L']:.2f}")
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res, indent=1, sort_keys=True))
        print(f"written {out}")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
