"""life.py — TOY A's life: S1c's 200-block life with a picker OBJECT, the second loss, the prequential errors, the ear-cover check, the drop's
anatomy. The record carries S1c's own keys byte for byte (so the loop can be pinned against S1c's records) and everything this toy adds under `extra`.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:30 +0400 — new module, written to docs/research/toys/PREREG-TOY-CP.md §2–§4 and AMEND-1; red-first
# (tests/tools/test_toys_cp.py). It is a COPY of brain/scene/run_s1c.py `life` (lines 297–376 of the tree at 15445a3) with three differences:
# the picker is an object with `observe_block(info)` instead of a name, the loss tables carry `C` beside `L`, and the extras are added. Nothing
# under brain/ is edited. The identity of the copy is not assumed: tests/tools/test_toys_cp.py::TestLifeIdentity and the unit's gate G2 compare
# its records with S1c's field for field (pickers.window_loss, learners and the pools are S1c's own).

A block = 10 scenes in the picked room; a life = `n_blocks` blocks, the first len(rooms) a fixed round-robin; the learner S1b-1's A-RW at lr 0.01; the
record per block {block, room, flag, start, est, L (all rooms after the block), drop, drift, credited, wl}.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.scene import pickers as PK
from brain.scene import run as R
from brain.scene import run_s1c as S
from brain.world.seeds import substream

from . import estimators as ES
from . import losses as LS

VOCAB = LS.VOCAB


def ear_state(L) -> Tuple[bool, int]:
    """Does the ear's own type cover over the HEARD words equal the vocabulary's map restricted to them? (and how many words are heard)"""
    heard = sorted(L.words)
    hs = set(heard)
    expect = sorted(tuple(sorted(w for w in ws if w in hs)) for ws in LS.TYPE_WORDS.values() if any(w in hs for w in ws))
    got = sorted(tuple(c) for c in L.ear.cover(heard))
    return got == expect, len(heard)


def train_block_pre(L, data, room: str, start: int, seed: int, want_pre: bool) -> Tuple[List[np.ndarray], List[float]]:
    """run_s1c.train_block with theta snapshots, plus each scene's PREQUENTIAL loss (taken before the update on it) when asked."""
    th = [PK.theta(L, VOCAB)]
    pre: List[float] = []
    for i in range(start, start + PK.BLOCK):
        X, words = data.visit_scene(room, i)
        if want_pre:
            pre.append(LS.scene_loss_pre(L, X, words))
        L.train_scene(X, words, referent=None, rng=substream(seed, f"episodic:room:{room}:visit:{i}"))
        th.append(PK.theta(L, VOCAB))
    return th, pre


def life_cp(data, test, picker, label: str, rooms: Sequence[str], n_blocks: int = PK.N_BLOCKS, prefix: str = "",
            decompose: bool = False, rep: Optional[int] = None, prereg: Optional[Dict[str, str]] = None) -> Dict[str, object]:
    cpu0, wall0 = time.process_time(), time.time()
    seed, rooms = data.seed, list(rooms)
    L = S.new_learner()
    cursor = {r: 0 for r in rooms}
    last = {r: 0 for r in rooms}
    n_scenes = {r: 0 for r in rooms}
    Lk = {r: PK.window_loss(L, data.window[r]) for r in rooms}
    Ck = {r: LS.window_C(L, data.window[r]) for r in rooms}
    table = [dict(Lk)]
    ctab = [dict(Ck)]
    wl_now, _ = test.words_learned(L)
    wl_curve = [wl_now]
    want_pre = isinstance(picker, ES.LPPicker)
    rec: List[Dict[str, object]] = []
    ear_ok: List[bool] = []
    n_heard: List[int] = []
    hist_w_n: List[float] = []
    rates_curve: List[List[Optional[float]]] = []
    decomp: List[Dict[str, object]] = []
    for block in range(1, n_blocks + 1):
        est = picker.estimates()
        if block <= len(rooms):
            room, flag = rooms[block - 1], "round-robin"
        else:
            room, flag = picker.pick(block, PK.Context(last_visit=dict(last), L_now=dict(Lk)))
        start = cursor[room]
        snap_b = LS.Snap.of(L) if decompose else None
        thetas, preq = train_block_pre(L, data, room, start, seed, want_pre)
        cursor[room] += PK.BLOCK
        n_scenes[room] += PK.BLOCK
        drift = PK.drift_reading(thetas)
        Lk_new = {r: PK.window_loss(L, data.window[r]) for r in rooms}
        Ck_new = {r: LS.window_C(L, data.window[r]) for r in rooms}
        drop = Lk[room] - Lk_new[room]
        info = ES.Info(block=block, room=room, L_before=dict(Lk), L_after=dict(Lk_new), C_before=dict(Ck), C_after=dict(Ck_new),
                       n_after=dict(n_scenes), drop=drop, drift=drift, preq=preq)
        credited = picker.observe_block(info)
        wl_now, rates = test.words_learned(L)
        row = {"block": block, "room": room, "flag": flag, "start": start, "est": est, "L": Lk_new, "drop": drop,
               "drift": drift, "credited": credited, "wl": wl_now}
        if decompose:
            snap_a = LS.Snap.of(L)
            mixes = {"bias": LS.Snap.mix(snap_b, snap_a, bias=True), "weight": LS.Snap.mix(snap_b, snap_a, weights=True),
                     "stats": LS.Snap.mix(snap_b, snap_a, stats=True)}
            Lv = {k: {r: PK.window_loss(sn, data.window[r]) for r in rooms} for k, sn in mixes.items()}
            tot_n = float(sum(n_scenes.values()))
            own = {"total": Lk[room] - Lk_new[room]}
            hist = {"total": float(sum(n_scenes[j] * (Lk[j] - Lk_new[j]) for j in rooms) / tot_n)}
            for k in mixes:
                own[k] = Lk[room] - Lv[k][room]
                hist[k] = float(sum(n_scenes[j] * (Lk[j] - Lv[k][j]) for j in rooms) / tot_n)
            decomp.append({"block": block, "room": room, "own": own, "hist": hist})
        rec.append(row)
        ok, nh = ear_state(L)
        ear_ok.append(ok)
        n_heard.append(nh)
        hist_w_n.append(n_scenes["N"] / float(sum(n_scenes.values())) if "N" in n_scenes else 0.0)
        rates_curve.append([rates[w] for w in VOCAB])
        Lk = Lk_new
        Ck = Ck_new
        table.append(dict(Lk))
        ctab.append(dict(Ck))
        last[room] = block
        wl_curve.append(wl_now)
    ans = test.points(L)
    full = test.m1_full(L, ans)
    fast = test.m1_fast(L, ans)
    if full["graded"]["covered"] != fast:
        raise S.S1cError(f"M1 fast {fast} ≠ the grader's {full['graded']['covered']}")
    pin = test.pin(L, ans)
    if pin["names_mismatch"] or pin["points_mismatch"]:
        raise S.S1cError(f"the batched readers differ from name_forced / answer_point at the life's end: {pin}")
    wl_end, rates = test.words_learned(L)
    out = {"seed": seed, "picker": label, "rooms": rooms, "prefix": prefix, "identity_credit": False,
           "n_blocks": n_blocks, "record": rec, "table": table, "wl_curve": wl_curve, "rates_end": rates,
           "word_n": test.word_n, "m1_end": full["graded"], "m1_end_value": fast, "cursor": cursor,
           "pi": getattr(picker, "pi", None), "cpu_s": time.process_time() - cpu0, "wall_s": time.time() - wall0,
           "n_empty_windows": {r: data.window[r].n_empty for r in rooms}, "prereg": dict(prereg or {}), "pin_end": pin,
           "code": R.code_identity(), "note": None}
    out["marks"] = S.run_marks(out)
    extra: Dict[str, object] = {"arm": label, "rep": rep, "C": ctab, "hist_w_N": hist_w_n, "ear_ok": ear_ok, "n_heard": n_heard,
                                "rates_curve": rates_curve, "n_scenes": dict(n_scenes)}
    if decompose:
        extra["decomp"] = decomp
    out["extra"] = extra
    return out
