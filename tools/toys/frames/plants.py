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

from collections import Counter

from . import anatomy as AN
from . import compress as CO
from . import null as NL
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


# ------------------------------------------------------------------------------------------------------------------ AMENDMENT-1 §1: the PLANT gate
# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:58 +0400 — stage 4a, red-first against tests/tools/test_toys_frames_plants.py: per rule (i) keeps F*, (A) the whole-set G, (C) F*'s marginal credit inside the rule's own set;
# per stream (B) G({F*}) with the architect's first-order expected value, its decomposition and PLANT-BEATS-NULL-2; the gate's modes (`amend1`: keeps AND (B) AND (C); `law`: keeps AND (A)); the parse-breaking control.
PLANT_NULL_TAG = 5                                            # AMENDMENT-1 §4 (a): the PLANT gate's NULL-2 of the one-frame set


def plant_reading(sc: CO.Scorer, frames) -> Dict[str, object]:
    """(i) whether the rule's set keeps the planted frame, (A) its whole-set G, (C) G(F) − G(F minus the planted frame) (None when the frame is not kept)."""
    F = frozenset(frames)
    A = sc.gain(F).G
    kept = ST.PLANT in F
    C = (A - sc.gain(F - {ST.PLANT}).G) if kept else None
    return {"kept": kept, "A": A, "C": C}


def plant_stream_block(sc: CO.Scorer, plants_train: int, plants_held: int, null_draws: int = 100) -> Dict[str, object]:
    """Per PLANT stream: (B) G({F*}), the architect's first-order expected value with its inputs, the exact decomposition of B, and PLANT-BEATS-NULL-2 (B >= q95 of NULL-2 of {F*})."""
    one = {ST.PLANT}
    B = sc.gain(one).G
    n2 = NL.null2(sc, one, PLANT_NULL_TAG, 0, null_draws)
    d = n2.read(B)
    d["values"] = list(n2.values)
    return {"B": B, "plants_train": plants_train, "plants_held": plants_held, "V": sc.V, "N0": sc.n0,
            "expected_first_order": first_order_saving(plants_held, sc.n0, plants_train, sc.V), "decomposition": AN.decompose_gain(sc, one),
            "null2_of_plant": d, "plant_beats_null2": bool(B >= n2.q95)}


def gate_passes(rule: str, rows: Sequence[Dict[str, object]], B: float, mode: str) -> Dict[str, object]:
    """The PLANT gate of one rule on one PLANT stream. `rows` = its plant readings, one a seed (WEB-S: ten; the others: one).
    amend1: every counted seed keeps F* with C > 0, and B > 0 (WEB-S at >= 9 of 10 seeds, a seed counted only if (i) and (C) both hold). law: keeps F* with A > 0 (WEB-S at >= 9 of 10 seeds)."""
    if mode not in ("amend1", "law"):
        raise ValueError(f"gate mode {mode!r} is not amend1 | law")
    n = len(rows)
    if mode == "amend1":
        counted = [r for r in rows if r["kept"] and r["C"] is not None and r["C"] > 0]
    else:
        counted = [r for r in rows if r["kept"] and r["A"] > 0]
    need = -(-9 * n // 10) if rule == "WEB-S" else n
    ok = len(counted) >= need
    if mode == "amend1":
        ok = ok and B > 0
    return {"pass": bool(ok), "n_seeds": n, "n_counted": len(counted), "need": need, "mode": mode, "B": B}


def _never_fires(words, frames) -> list:
    return list(words) + [CO.END]


def plant_gate_control(planted_moments: Sequence[ST.Moment]) -> Dict[str, object]:
    """AMENDMENT-1 §1.4: a compressor whose parse never fires a frame (a bug that breaks the parse) must make (B) and (C) read <= 0 and the gate read FAIL, on a small planted stream.
    `planted_moments` is a stream that already carries its plants. The set tried is {F*} plus the most frequent real bigram (a junk frame)."""
    tr, he = ST.split(planted_moments)
    train, held = words_of(tr), words_of(he)
    honest = CO.Scorer(train, held)
    broken = CO.Scorer(train, held, parse=_never_fires)
    bigrams = honest.train_bigrams()
    junk = sorted(((c, p) for p, c in bigrams.items() if p != ST.PLANT), key=lambda cp: (-cp[0], cp[1]))[0][1]
    F = {ST.PLANT, junk}

    def readings(sc: CO.Scorer) -> Tuple[float, float]:
        return sc.gain({ST.PLANT}).G, sc.gain(F).G - sc.gain({junk}).G

    Bh, Ch = readings(honest)
    Bb, Cb = readings(broken)
    tok_h = Counter(t for m in train for t in CO.parse_moment(m, frozenset(F)))
    tok_b = Counter(t for m in train for t in _never_fires(m, frozenset(F)))
    gate_h, gate_b = bool(Bh > 0 and Ch > 0), bool(Bb > 0 and Cb > 0)
    return {"B_honest": Bh, "C_honest": Ch, "B_broken": Bb, "C_broken": Cb, "gate_honest": gate_h, "gate_broken": gate_b,
            "caught": bool(Bb <= 0 and Cb <= 0 and not gate_b), "bytes_changed": tok_h != tok_b, "junk_frame": list(junk)}


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
