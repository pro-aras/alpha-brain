"""run_tmem5.py — T-MEM-5 (= S1c-3) «WHERE SEPARATES»: the CONTEXT learner's lives (its own act, the room, as context), the
arms and their nulls, the SPLIT graders (MEMORY: the noise room settles; CURIOSITY: progress chooses), the readings
(BIAS-ONLY, A-READ+WHERE, A read at ḡ_R), THE FIRST GATE's five steps (the identity, the fixed-point toy, the chain-rule pin,
the instrument, the smoke), the price and the report. Runs under /usr/bin/python3.

edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 18:27 +0400 — new module, written to docs/brain/memory/PREREG-TMEM5.md (genome-wt-brain3
ce41448, sha 30121082…, final) and its AMENDMENT 1 (brain-design-3 95b6e48, sha ab9a5fca…, final: the builder's 13 declared
readings ruled — «ruled» below; the context null's VOID clause re-set on the bar's own window; NULL-CTX + REPLAY added; the
null's four gains printed). It extends PREREG-S1C (a552515a…) + AMENDMENT 1 (92188d04…) + PREREG-S1C2 (5e4585c1…): everything
not named is theirs (run_s1c.py, run_s1c2.py, pickers.py). The pools are scene-tmem1's (redrawn under the merged code and
TESTED equal to S1c's); the learner is context.py's CtxLearner at lr 0.01, lr_g 0.001.

  python3 -m brain.scene.run_tmem5 check                           the shas
  python3 -m brain.scene.run_tmem5 first-gate                      THE FIRST GATE (seed 20261301), steps 1–5
  python3 -m brain.scene.run_tmem5 run --arm A --seed S            one life; <root>/<seed>/runs/<A>.json
  python3 -m brain.scene.run_tmem5 band --learner L --seed S --k A-B   RANDOM-CTX's band lives on L = ctx | ctx-replay
  python3 -m brain.scene.run_tmem5 price                           solo, printed before the unit
  python3 -m brain.scene.run_tmem5 report                          the identity, the two graders, the readings

THE CONTEXT (PREREG-TMEM5 §1): during a block the learner's context is the room it CHOSE (its act); a replayed scene trains
under ITS OWN stored act (ruled (1)); SHUFFLED-CTX trains block b under σ_b(room), σ_b a derangement from
`ctx-shuffle:<seed>:<block>` (null_derangement's rule, ruled (2)); the window L_k is ALWAYS read with label k; the fixed test
set (WORDS-LEARNED, M1) reads the SHARED map alone (g = 1, c = 0), and A is also read at ḡ_R (ruled (13)).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.world.seeds import substream

from . import context as CX
from . import learners as Lr
from . import memory as MEM
from . import pickers as PK
from . import rooms as RM
from . import run as R
from . import run_s1c as S
from . import run_s1c2 as S2
from . import run_tmem1 as T1
from . import world as W

# ------------------------------------------------------------------------------------------------ the PREREG's numbers
PREREG_TMEM5_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/memory/PREREG-TMEM5.md")
PREREG_TMEM5_SHA256 = "301210825f6809a9d40b706aa03b19b31b44c44c21667d2cd0420e2765e6d1ab"      # final: the seat signs, ce41448
AMEND1_TMEM5_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/memory/PREREG-TMEM5-AMEND-1.md")
AMEND1_TMEM5_SHA256 = "ab9a5fca939c258f940b2191529404f12fb80f06d8b9fdbf37fd5b468ea36d00"      # final: both sign, 95b6e48
ROOT = Path("/data/dev/brain-runs/scene-tmem5")
POOLS_ROOT = T1.ROOT                 # scene-tmem1's pools: redrawn under the merged code, TESTED equal to S1c's
S1C_ROOT = S.ROOT                    # the identity records (S1c's own runs)
ROOMS: Tuple[str, ...] = tuple(S.WORLDS["law"])
LEARNABLE: Tuple[str, ...] = ("R1", "R2", "R3")
SEEDS: Tuple[int, ...] = RM.S1C_SEEDS
GATE_SEED = S.GATE_SEED
BAND_K: Tuple[int, ...] = S.BAND_K
R_REPLAY = 10
MEMORY_AFTER = 20                    # the MEMORY fraction reads blocks 21–200
G_LAST = 10                          # g_N (and each learnable room's gain) over its own last 10 blocks
BAR_N_FRACTION = 0.3
BAR_G_RATIO = 0.1
REFUTE_G = 0.3                       # §5: g_N > 0.3 at block 200 with biases present, at ≥ 2 seeds
LEAVE_BAR, SHARE_ALLOWANCE, POSITIVE_CONTROL, A_VS_ORACLE = S.BAR_LEAVE_N, S.BAR_SHARE_ALLOWANCE, S.BAR_POSITIVE_CONTROL, S.BAR_A_VS_ORACLE
# THE TOY (§3 step 2 with Fable's edit: B receives the scenes N receives in a RANDOM-CTX life); its construction is DECLARED
# (ruled (8)): 146 inputs = the three attribute values' prototype directions (norm TOY_SIGNAL) + unit noise ‖ [y/16, x/16];
# the 13 words of the world in its three types; S1's 1 / 2 / 3-thing mix; A's parent TRUE (a thing uniformly, a template
# T1–T4 uniformly); B's utterance N's rule (a template uniformly, each slot's word uniform over its type), independent of
# the things; exactly 50 of the 200 blocks in B (500 scenes) at positions drawn from the toy's seed.
TOY_SEEDS: Tuple[int, ...] = (0, 1, 2)
TOY_ROOMS: Tuple[str, ...] = ("A", "B")
TOY_BLOCKS = 200
TOY_B_BLOCKS = 50
TOY_SIGNAL = 3.0
TOY_GB_BAR = 0.1
TOY_GA_BAR = 0.8
TOY_EVAL_N = 300
TOY_TAG = 20260928
FD_H = 1e-6
FD_TOL = 1e-6
GATE4_BLOCKS = 60
SMOKE_BLOCKS = 20
VOCAB: Tuple[str, ...] = RM.VOCAB13
TYPE_WORDS = S.TYPE_WORDS
LEARNER_KINDS: Dict[str, Tuple[bool, bool]] = {"ctx": (True, True), "bias": (False, True), "gain": (True, False),
                                               "frozen": (False, False)}              # kind → (learn_gain, learn_bias)
# arm → (the picker, the replay grain, the learner kind, the context shuffled per block)
ARM_SPEC: Dict[str, Tuple[str, Optional[str], str, bool]] = {
    "PROGRESS-CTX": ("PROGRESS", None, "ctx", False), "PROGRESS-CTX+REPLAY": ("PROGRESS", "room", "ctx", False),
    "RANDOM-CTX": ("RANDOM", None, "ctx", False), "RANDOM-CTX+REPLAY": ("RANDOM", "room", "ctx", False),
    "ORACLE-CTX": ("ORACLE", None, "ctx", False), "ORACLE-CTX+REPLAY": ("ORACLE", "room", "ctx", False),
    "NULL-CTX": ("NULL", None, "ctx", False), "NULL-CTX+REPLAY": ("NULL", "room", "ctx", False),
    "SHUFFLED-CTX": ("PROGRESS", None, "ctx", True), "SHUFFLED-CTX-RANDOM": ("RANDOM", None, "ctx", True),
    "BIAS-ONLY-RANDOM": ("RANDOM", None, "bias", False), "BIAS-ONLY-PROGRESS": ("PROGRESS", None, "bias", False),
    "FROZEN-PROGRESS": ("PROGRESS", None, "frozen", False), "FROZEN-RANDOM": ("RANDOM", None, "frozen", False)}
ARMS: Tuple[str, ...] = tuple(ARM_SPEC)
BAND_LEARNERS: Dict[str, str] = {"ctx": "RANDOM-CTX", "ctx-replay": "RANDOM-CTX+REPLAY"}
# CURIOSITY's barred arms: X → (its band's learner, O_X, RANDOM_X, NULL_X) — each with its OWN null (AMENDMENT 1 §3)
CURIOSITY: Dict[str, Tuple[str, str, str, str]] = {
    "PROGRESS-CTX": ("ctx", "ORACLE-CTX", "RANDOM-CTX", "NULL-CTX"),
    "PROGRESS-CTX+REPLAY": ("ctx-replay", "ORACLE-CTX+REPLAY", "RANDOM-CTX+REPLAY", "NULL-CTX+REPLAY")}
MEMORY_ARM, MEMORY_NULL = "RANDOM-CTX", "SHUFFLED-CTX-RANDOM"
IDENTITY: Dict[str, str] = {"FROZEN-PROGRESS": "PROGRESS", "FROZEN-RANDOM": "RANDOM"}     # ruled (11): at every seed
WHERE_ARMS: Tuple[str, ...] = ("RANDOM-CTX", "PROGRESS-CTX")                                # ruled (10)
EPS_ARMS: Tuple[str, ...] = tuple(a for a, v in ARM_SPEC.items() if v[0] in ("PROGRESS", "NULL"))


class Tmem5Error(Exception):
    pass


def check_prereg() -> Dict[str, str]:
    """PREREG-TMEM5 and its AMENDMENT 1 (final) beside the laws they extend (PREREG-TMEM1 and CONCLUSION-MEMORY for the
    READER, PREREG-S1C2, PREREG-S1C, AMENDMENT 1 of S1c, PREREG-S1B1 — run_tmem1.check_prereg)."""
    got = dict(T1.check_prereg())
    for key, path, want in (("prereg_tmem5", PREREG_TMEM5_PATH, PREREG_TMEM5_SHA256),
                            ("amend1_tmem5", AMEND1_TMEM5_PATH, AMEND1_TMEM5_SHA256)):
        g = hashlib.sha256(path.read_bytes()).hexdigest()
        if g != want:
            raise Tmem5Error(f"{key} sha256 {g[:12]}… ≠ {want[:12]}… — STOP and hand back")
        got[key] = g
    return got


def prereg_header() -> Dict[str, str]:
    return {**T1.prereg_header(), "prereg_tmem5_sha256": PREREG_TMEM5_SHA256, "amend1_tmem5_sha256": AMEND1_TMEM5_SHA256}


# ================================================================================================ the learner and the context
def new_ctx_learner(kind: str, rooms: Sequence[str] = ROOMS) -> CX.CtxLearner:
    """The context learner at the law's lr 0.01 and lr_g 0.001: `ctx` learns g and c; `bias` only c (BIAS-ONLY, g ≡ 1);
    `gain` only g (the toy's print); `frozen` neither (S1c's A-RW bit for bit — the identity)."""
    gain, bias = LEARNER_KINDS[kind]
    return CX.CtxLearner(rooms, lr=Lr.LR_S1B1, lr_g=CX.LR_G, learn_gain=gain, learn_bias=bias)


def shuffle_sigma(seed: int, block: int, rooms: Sequence[str]) -> Dict[str, str]:
    """SHUFFLED-CTX's label map of block b: a derangement of the rooms from substream `ctx-shuffle:<seed>:<block>`, uniform
    permutations drawn until one has no fixed point (null_derangement's rule, ruled (2))."""
    rng = substream(seed, f"ctx-shuffle:{int(seed)}:{int(block)}")
    for _ in range(10_000):
        perm = rng.permutation(len(rooms))
        sg = {rooms[i]: rooms[int(perm[i])] for i in range(len(rooms))}
        if PK.is_derangement(sg):
            return sg
    raise Tmem5Error("no derangement in 10,000 draws")


def same_state5(a: CX.CtxLearner, b: CX.CtxLearner) -> bool:
    """S1c's clone check, and the context's own parameters (ruled (12))."""
    return (S._same_state(a, b) and a.g == b.g and set(a.c) == set(b.c)
            and all(np.array_equal(a.c[r], b.c[r]) for r in a.c) and a.ctx == b.ctx)


def scaled(L: Lr.RWLearner, g: float) -> Lr.RWLearner:
    """A read-only view of the learner whose map is scaled by g (logit = g · (v · z) + b, c = 0): A read at ḡ_R. The learner
    itself is untouched (a shallow copy with its own V)."""
    Lg = copy.copy(L)
    Lg.V = L.V * float(g)
    return Lg


def gbar(L: CX.CtxLearner) -> float:
    return float(np.mean([L.g[r] for r in LEARNABLE]))


def window_losses(L, data, rooms: Sequence[str]) -> Dict[str, float]:
    """L_k for every room, the window of room k read with label k (§1)."""
    return {r: CX.ctx_window_loss(L, data.window[r], r) for r in rooms}


def replay5(L: CX.CtxLearner, data, draws: Sequence[Tuple[str, int]], seed: int) -> None:
    """S1c-2's replay, each drawn scene under ITS OWN stored act — the room it was met in (ruled (1))."""
    for q, i in draws:
        X, words = data.visit_scene(q, i)
        L.set_context(q)
        L.train_scene(X, words, referent=None, rng=substream(seed, f"episodic:room:{q}:visit:{i}"))


# ================================================================================================ the LIFE
def life5(data, test, arm: str, rooms: Sequence[str] = ROOMS, n_blocks: int = PK.N_BLOCKS, prefix: str = "",
          identity_credit: bool = False, R_: int = R_REPLAY, where: bool = False, eps: Optional[float] = None,
          keep_learner: bool = False, log=None) -> Dict[str, object]:
    """One life of one arm: S1c-2's life2 (POST → REPLAY → PRE at every boundary) on the context learner. For the FROZEN
    arms every computation is run_s1c.life's, in its order — the identity control proves it on S1c's own records. The
    context's own record rides beside S1c's rows (`ctx_record`), so S1c's rows keep S1c's keys."""
    picker_name, grain, kind, shuffle = ARM_SPEC[arm]
    replay_on = grain is not None and R_ > 0
    if shuffle and replay_on:
        raise Tmem5Error("no arm shuffles the context AND replays")
    cpu0, wall0 = time.process_time(), time.time()
    seed, rooms = data.seed, list(rooms)
    L = new_ctx_learner(kind, rooms)
    cursor = {r: 0 for r in rooms}
    last = {r: 0 for r in rooms}
    buffer: List[Tuple[str, int]] = []
    by_room: Dict[str, List[int]] = {r: [] for r in rooms}
    Lk = window_losses(L, data, rooms)
    table = [dict(Lk)]
    table_pre = [dict(Lk)]
    wl_now, _ = test.words_learned(L)
    wl_curve = [wl_now]
    ctx0 = {"g": dict(L.g), "gR": gbar(L), "wl_gR": test.words_learned(scaled(L, gbar(L)))[0]}
    clones: Dict[str, CX.CtxLearner] = {}
    oracle_log: Dict[str, object] = {}
    replayed = {r: 0 for r in rooms}

    def gain_fn(rs: Sequence[str]) -> Dict[str, Tuple[float, float]]:
        clones.clear()
        m1_now = test.m1_fast(L)
        oracle_log["m1_now"] = m1_now
        out = {}
        for r in rs:
            cl = copy.deepcopy(L)
            cl.set_context(r)                                    # ruled (12): the clone learns under the room's act
            S.train_block(cl, data, r, cursor[r], seed)          # the clone trains the next block WITHOUT replay
            wl_c, _ = test.words_learned(cl)
            m1_c = test.m1_fast(cl)
            out[r] = (float(wl_c - wl_now), None if (m1_c is None or m1_now is None) else float(m1_c - m1_now))
            clones[r] = cl
        return out

    picker = PK.make_picker(picker_name, rooms, seed, gain_fn=gain_fn, prefix=prefix, identity_credit=identity_credit)
    rec: List[Dict[str, object]] = []
    ctx_rec: List[Dict[str, object]] = []
    for block in range(1, n_blocks + 1):
        est = picker.estimates()
        if block <= len(rooms):
            room, flag = rooms[block - 1], "round-robin"
        else:
            room, flag = picker.pick(block, PK.Context(last_visit=dict(last), L_now=dict(Lk)))
        sigma = shuffle_sigma(seed, block, rooms) if shuffle else None
        label = sigma[room] if shuffle else room
        L.set_context(label)
        start = cursor[room]
        thetas = S.train_block(L, data, room, start, seed, snapshots=True)
        cursor[room] += PK.BLOCK
        for i in range(start, start + PK.BLOCK):
            buffer.append((room, i))
            by_room[room].append(i)
        drift = PK.drift_reading(thetas)
        same = None
        if picker_name == "ORACLE" and flag == "policy":
            same = same_state5(clones[room], L)                   # before any replay: the clone saw the block only
            if not same:
                raise Tmem5Error(f"{arm} block {block}: the ORACLE's clone of {room} is not the learner after the same block")
        Lk_new = window_losses(L, data, rooms)                    # (i) POST_b
        drop = Lk[room] - Lk_new[room]
        draws: List[Tuple[str, int]] = []
        if replay_on:
            draws = S2.replay_draws(seed, block, by_room, buffer, rooms, R_, grain)     # (ii) the REPLAY
            replay5(L, data, draws, seed)
            Lk_pre = window_losses(L, data, rooms)                                      # (iii) PRE_(b+1)
        else:
            Lk_pre = Lk_new                                                             # (iii) ≡ (i)
        credited = picker.observe(block, room, drop=drop, drift=drift)
        wl_now, _ = test.words_learned(L)
        gR = gbar(L)
        wl_g, _ = test.words_learned(scaled(L, gR))
        row = {"block": block, "room": room, "flag": flag, "start": start, "est": est, "L": Lk_new, "drop": drop,
               "drift": drift, "credited": credited, "wl": wl_now}
        if picker_name == "ORACLE" and flag == "policy":
            row.update({"gains": {r: list(v) for r, v in picker.last_gains.items()}, "m1_now": oracle_log.get("m1_now"),
                        "clone_identical": same})
        if replay_on:
            mix = {r: sum(1 for q, _i in draws if q == r) for r in rooms}
            for r in rooms:
                replayed[r] += mix[r]
            row.update({"PRE": Lk_pre, "replay": [[q, int(i)] for q, i in draws], "replay_mix": mix,
                        "replay_effect": {r: Lk_new[r] - Lk_pre[r] for r in rooms}})
        rec.append(row)
        ctx_rec.append({"block": block, "label": label, "sigma": sigma, "g": dict(L.g),
                        "c_norm": {r: float(np.linalg.norm(L.c[r])) for r in rooms}, "gR": gR, "wl_gR": wl_g})
        Lk = Lk_pre
        table.append(dict(Lk_new))
        table_pre.append(dict(Lk_pre))
        last[room] = block
        wl_curve.append(wl_now)
        if log is not None and block % 50 == 0:
            log(f"[{arm}{' ' + prefix if prefix else ''} {seed}] block {block}: wl {wl_now} · {room} {flag} · g "
                + " ".join(f"{r} {L.g[r]:.3f}" for r in rooms))
    ans = test.points(L)
    full = test.m1_full(L, ans)
    fast = test.m1_fast(L, ans)
    if full["graded"]["covered"] != fast:
        raise Tmem5Error(f"M1 fast {fast} ≠ the grader's {full['graded']['covered']}")
    pin = test.pin(L, ans)
    if pin["names_mismatch"] or pin["points_mismatch"]:
        raise Tmem5Error(f"the batched readers differ from name_forced / answer_point at the life's end: {pin}")
    _wl_end, rates = test.words_learned(L)
    out = {"seed": seed, "picker": picker_name, "rooms": rooms, "prefix": prefix, "identity_credit": identity_credit,
           "n_blocks": n_blocks, "record": rec, "table": table, "wl_curve": wl_curve, "rates_end": rates,
           "word_n": test.word_n, "m1_end": full["graded"], "m1_end_value": fast, "cursor": cursor,
           "pi": getattr(picker, "pi", None), "cpu_s": None, "wall_s": None,
           "n_empty_windows": {r: data.window[r].n_empty for r in rooms}, "prereg": prereg_header(), "pin_end": pin,
           "code": R.code_identity(), "note": S.ORACLE_TRUTH_NOTE if picker_name == "ORACLE" else None,
           "arm": arm, "kind": kind, "shuffle": shuffle, "grain": grain if replay_on else None, "R": R_ if replay_on else 0,
           "table_pre": table_pre, "buffer_len": len(buffer), "replayed": replayed, "ctx0": ctx0, "ctx_record": ctx_rec,
           "g_end": dict(L.g), "c_end": {r: [float(v) for v in L.c[r]] for r in rooms}, "words_end": list(L.words),
           "lr_g": L.lr_g}
    out["marks"] = S.run_marks(out)
    out["marks2"] = S2.marks2(out)
    out["marks5"] = marks5(out)
    if where:
        t0 = time.process_time()
        out["where"] = where_reading(L, test, T1.chosen_eps() if eps is None else float(eps))
        out["where"]["cpu_s"] = time.process_time() - t0
    out["cpu_s"], out["wall_s"] = time.process_time() - cpu0, time.time() - wall0
    if keep_learner:
        out["_learner"] = L
    return out


# ================================================================================================ the marks of the slice
def n_fraction(rec: Sequence[Dict[str, object]], after: int = MEMORY_AFTER) -> Dict[str, object]:
    """N's mean drop over its blocks after `after` ÷ the learnable rooms' mean drop over theirs (S1c's drop: the visited
    room's window, read with its own label, before − after the block); both numbers and their n (ruled (3)); a denominator
    ≤ 0 → None (NOT GRADABLE)."""
    n = [float(x["drop"]) for x in rec if x["room"] == "N" and int(x["block"]) > after]
    r = [float(x["drop"]) for x in rec if x["room"] in LEARNABLE and int(x["block"]) > after]
    num = float(np.mean(n)) if n else None
    den = float(np.mean(r)) if r else None
    frac = (num / den) if (num is not None and den is not None and den > 0) else None
    return {"num": num, "den": den, "n_N": len(n), "n_R": len(r), "fraction": frac, "after": after}


def gain_reading(run: Dict[str, object]) -> Dict[str, object]:
    """Each label's gain after every block that trained it (the trajectory); g_N = the mean over the last 10 N-blocks with
    its sd (ddof 1, the noise floor); ḡ_R = each learnable room's mean over ITS OWN last 10 blocks, averaged over R1–R3,
    with the block-200 value beside it (ruled (4)); the four gains at the end (AMENDMENT 1 §2's print for the null)."""
    ctx, rooms = run["ctx_record"], list(run["rooms"])
    traj = {k: [(int(c["block"]), float(c["g"][k])) for c in ctx if c["label"] == k] for k in rooms}

    def last(k):
        return [v for _b, v in traj[k][-G_LAST:]]

    gN = last("N")
    per = {k: (float(np.mean(last(k))) if last(k) else None) for k in LEARNABLE}
    return {"g_N": float(np.mean(gN)) if gN else None, "g_N_sd": float(np.std(gN, ddof=1)) if len(gN) > 1 else None,
            "g_N_n": len(gN), "g_R": float(np.mean(list(per.values()))) if all(v is not None for v in per.values()) else None,
            "g_R_rooms": per, "g_R_at_end": float(np.mean([ctx[-1]["g"][k] for k in LEARNABLE])) if ctx else None,
            "g_end": dict(ctx[-1]["g"]) if ctx else None, "g_N_at_end": float(ctx[-1]["g"]["N"]) if ctx else None,
            "trajectory": traj}


def marks5(run: Dict[str, object]) -> Dict[str, object]:
    ctx = run["ctx_record"]
    out = {"n_fraction": n_fraction(run["record"]), "n_fraction_all": n_fraction(run["record"], after=0)}
    out.update(gain_reading(run))
    out["A"] = run["marks"]["A"]
    out["A_gR"] = (float(np.mean([c["wl_gR"] for c in ctx])) / len(VOCAB)) if ctx else None
    out["c_N_norm_end"] = float(ctx[-1]["c_norm"]["N"]) if ctx else None
    return out


# ================================================================================================ A-READ+WHERE
def where_cells(L: CX.CtxLearner, types: Sequence[Sequence[str]], eps: float) -> Dict[str, object]:
    """The store keyed by (word, room) (ruled (10)): per room, T-MEM-1's READER over that room's rows alone (its own
    coordinates) and its STRONG rule; (w, room) is KEPT iff w is STRONG there. Also each word's attributed-row count and
    leave-one-out agreement per room (printed whether or not it is STRONG)."""
    rows = MEM.StoreRows.from_learner(L)
    rc = CX.row_contexts(L)
    if len(rc) != len(rows):
        raise Tmem5Error("the stored acts do not align with the store's rows")
    per_room: Dict[str, Dict[str, object]] = {}
    kept, kept_rows = set(), []
    for r in L.rooms:
        idx = [i for i in range(len(rows)) if rc[i] == r]
        if not idx:
            per_room[r] = {"rows": 0, "strong": {}, "words": {}}
            continue
        try:
            rd = MEM.StoreReader(rows.take(idx), types, eps)
        except MEM.MemoryError_ as e:
            per_room[r] = {"rows": len(idx), "strong": {}, "words": {}, "error": str(e)}
            continue
        st = rd.strong()
        words = {}
        for w in rd.words:
            att = rd.attributed(w)
            ok = rd.loo_agree(w, att) if att else np.zeros(0, dtype=bool)
            words[w] = {"n_att": len(att), "agree": float(ok.mean()) if len(ok) else None,
                        "rows": sum(1 for i in idx if rows.word[i] == w)}
        per_room[r] = {"rows": len(idx), "strong": {w: {"n": v["n"], "agree": v["agree"]} for w, v in st.items()},
                       "words": words}
        for w in st:
            kept.add((w, r))
        kept_rows += [i for i in idx if rows.word[i] in st]
    ex_n = {}
    for w in sorted(set(rows.word)):
        ex_n[w] = sum(1 for i in range(len(rows)) if rc[i] == "N" and rows.word[i] == w and (w, "N") not in kept)
    return {"rows": rows, "row_room": rc, "kept": kept, "kept_rows": sorted(kept_rows), "per_room": per_room,
            "excluded_N": ex_n}


def where_reading(L: CX.CtxLearner, test, eps: float) -> Dict[str, object]:
    """A-READ+WHERE at the life's end: the kept cells, N's rows excluded per word, and the naming of the held items by
    the WHERE reader beside the unkeyed A-READ (every row) and the map (A-RW) — WORDS-LEARNED by each."""
    types = L.ear.cover(L.mature_words())
    if not types:
        return {"types": [], "note": "no learned type"}
    cells = where_cells(L, types, eps)
    rows = cells["rows"]
    rates_all = T1.TestSetM.rates_reader(test, MEM.StoreReader(rows, types, eps))
    kr = rows.take(cells["kept_rows"])
    rates_where = T1.TestSetM.rates_reader(test, MEM.StoreReader(kr, types, eps)) if len(kr) else {w: None for w in VOCAB}
    _wl, rates_rw = test.words_learned(L)

    def wl(rates):
        return sum(1 for w in VOCAB if rates.get(w) is not None and rates[w] >= S.LEARNED_AT)

    by_room = {r: {"rows": sum(1 for q in cells["row_room"] if q == r),
                   "kept": sum(1 for i in cells["kept_rows"] if cells["row_room"][i] == r)} for r in L.rooms}
    return {"types": [list(t) for t in types], "per_room": cells["per_room"], "kept": sorted([list(k) for k in cells["kept"]]),
            "excluded_N": cells["excluded_N"], "rows_total": len(rows), "rows_kept": len(kr), "by_room": by_room,
            "rates_all": rates_all, "rates_where": rates_where, "rates_rw": rates_rw,
            "wl_all": wl(rates_all), "wl_where": wl(rates_where), "wl_rw": wl(rates_rw), "eps": eps}


# ================================================================================================ the graders
def _q(v: Sequence[float], q: float) -> float:
    return float(np.percentile(np.asarray(v, dtype=np.float64), q))


def memory_verdict(per_seed: Dict[int, Dict[str, object]]) -> Dict[str, object]:
    """MEMORY «WHERE separates» (§4 as AMENDMENT 1 §2 re-set it): per_seed[s] = {"X": RANDOM-CTX's marks5, "NULL":
    SHUFFLED-CTX under RANDOM's marks5, "blind": the context-blind RANDOM's fraction on the same window (S1c's records)}.
    Every seed: N's fraction < 0.3 AND g_N ≤ 0.1 · ḡ_R. The order (ruled (5)): NOT GRADABLE BY NAME → VOID (the null MEETS
    the fraction clause itself at ≥ 2 seeds) → NOT GRADABLE BY NOISE (g_N's sd over its last 10 blocks > 0.1 · ḡ_R) →
    NOT GRADABLE BY DENOMINATOR (the learnable rooms' mean drop ≤ 0) → FAIL → PASS."""
    seeds = sorted(per_seed)
    missing = [f"{k}@{s}" for s in seeds for k in ("X", "NULL") if per_seed[s].get(k) is None]
    out: Dict[str, object] = {"seeds": {}, "missing": missing}
    if missing:
        out["verdict"] = "NOT GRADABLE BY NAME"
        return out
    null_n, noisy, denom, fails = 0, [], [], []
    for s in seeds:
        X, N_, blind = per_seed[s]["X"], per_seed[s]["NULL"], per_seed[s].get("blind")
        f, gN, sd, gR = X["n_fraction"]["fraction"], X["g_N"], X["g_N_sd"], X["g_R"]
        bar_g = BAR_G_RATIO * gR if gR is not None else None
        f_state = None if f is None else ("PASS" if f < BAR_N_FRACTION else "FAIL")
        g_state = None if (gN is None or bar_g is None) else ("PASS" if gN <= bar_g else "FAIL")
        noise = sd is not None and bar_g is not None and sd > bar_g
        nf = N_["n_fraction"]["fraction"]
        meets = nf is not None and nf < BAR_N_FRACTION
        null_n += int(meets)
        if noise:
            noisy.append(s)
        if f is None or bar_g is None:
            denom.append(s)
        fails += ([f"fraction@{s}"] if f_state == "FAIL" else []) + ([f"g_N@{s}"] if g_state == "FAIL" else [])
        out["seeds"][s] = {"fraction": X["n_fraction"], "f_state": f_state, "g_N": gN, "g_N_sd": sd, "g_N_n": X["g_N_n"],
                           "g_R": gR, "g_R_at_end": X["g_R_at_end"], "bar_g": bar_g, "g_state": g_state, "noisy": noise,
                           "trajectory_N": X["trajectory"]["N"], "g_N_at_end": X.get("g_N_at_end"),
                           "null_fraction": N_["n_fraction"], "null_meets": meets, "null_g_end": N_["g_end"],
                           "blind_fraction": blind,
                           "null_minus_blind": (nf - blind) if (nf is not None and blind is not None) else None}
    out.update({"null_seeds": null_n, "noisy": noisy, "denominator": denom, "fails": fails})
    if null_n >= 2:
        out["verdict"] = "VOID"
    elif noisy:
        out["verdict"] = "NOT GRADABLE BY NOISE"
    elif denom:
        out["verdict"] = "NOT GRADABLE BY DENOMINATOR"
    elif fails:
        out["verdict"] = "FAIL"
    else:
        out["verdict"] = "PASS"
    return out


def curiosity_verdict(per_seed: Dict[int, Dict[str, object]]) -> Dict[str, object]:
    """CURIOSITY «progress chooses» for one barred arm X on its own learner (§4's rows, ruled (6)): per_seed[s] = {"X", "O",
    "RND", "NUL": run_marks, "band_A": RANDOM_X's band A values, "band_n"}. Rows: A above the band's 97.5 % edge
    (CEILING-BOUND where O_X is not above it); SHARE_N ≤ SHARE_N(O_X) + 0.05; LEAVE_N ≤ 50. The positive control
    A(O_X) − A(RANDOM_X) ≥ 0.05 (the law life); the null clause (AMENDMENT 1 §3): VOID when NULL_X meets the A-band bar AND
    the SHARE_N bar at ≥ 2 seeds. S1c-2's «A ≥ 0.80 × A(O_X)» is a READING, never a bar. The order: NOT GRADABLE BY NAME
    (an arm, its null or a band life missing) → NOT GRADABLE FOR CHOICE → VOID → FAIL → CEILING-BOUND → PASS."""
    seeds = sorted(per_seed)
    missing = [f"{k}@{s}" for s in seeds for k in ("X", "O", "RND", "NUL") if per_seed[s].get(k) is None]
    missing += [f"band@{s} (n {per_seed[s].get('band_n', 0)} of {len(BAND_K)})" for s in seeds
                if per_seed[s].get("band_n", 0) < len(BAND_K)]
    out: Dict[str, object] = {"seeds": {}, "missing": missing}
    if missing:
        out["verdict"] = "NOT GRADABLE BY NAME"
        return out
    pcs, null_n, fails, ceils = [], 0, [], []
    for s in seeds:
        d = per_seed[s]
        X, O, RND, NUL = d["X"], d["O"], d["RND"], d["NUL"]
        lo, hi = _q(d["band_A"], 2.5), _q(d["band_A"], 97.5)
        rows = {}
        if O["A"] <= hi:
            rows["A_band"] = {"value": X["A"], "bar": hi, "state": "CEILING-BOUND", "oracle": O["A"]}
        else:
            rows["A_band"] = {"value": X["A"], "bar": hi, "state": "PASS" if X["A"] > hi else "FAIL", "oracle": O["A"]}
        sb = O["share"]["N"] + SHARE_ALLOWANCE
        rows["SHARE_N"] = {"value": X["share"]["N"], "bar": sb, "state": "PASS" if X["share"]["N"] <= sb else "FAIL"}
        rows["LEAVE_N"] = {"value": X["leave"]["N"], "bar": LEAVE_BAR, "state": "PASS" if X["leave"]["N"] <= LEAVE_BAR else "FAIL"}
        pc = O["A"] - RND["A"]
        pcs.append(pc >= POSITIVE_CONTROL)
        meets = NUL["A"] > hi and NUL["share"]["N"] <= sb
        null_n += int(meets)
        fails += [f"{k}@{s}" for k, v in rows.items() if v["state"] == "FAIL"]
        ceils += [f"{k}@{s}" for k, v in rows.items() if v["state"] == "CEILING-BOUND"]
        out["seeds"][s] = {"bars": rows, "band": [lo, hi], "band_n": d["band_n"], "positive_control": pc,
                           "null_meets": meets, "null": {"A": NUL["A"], "SHARE_N": NUL["share"]["N"]},
                           "reading_080": {"value": X["A"], "bar": A_VS_ORACLE * O["A"], "meets": X["A"] >= A_VS_ORACLE * O["A"]}}
    out.update({"null_seeds": null_n, "fails": fails, "ceiling_bound": ceils, "positive_control_all": all(pcs)})
    if not all(pcs):
        out["verdict"] = "NOT GRADABLE FOR CHOICE"
    elif null_n >= 2:
        out["verdict"] = "VOID"
    elif fails:
        out["verdict"] = "FAIL"
    elif ceils:
        out["verdict"] = "CEILING-BOUND"
    else:
        out["verdict"] = "PASS"
    return out


# ================================================================================================ THE TOY (§3 step 2)
_TOY_TYPES: Dict[str, Tuple[str, ...]] = {"shape": W.SHAPES, "colour": W.COLOUR_NAMES, "size": W.SIZE_NAMES}


class ToyWorld:
    """The fixed-point toy's two rooms (the construction is declared above, ruled (8)): room A's words name a thing in view;
    room B's words are drawn AFTER its things and never read them."""

    def __init__(self, seed: int):
        g = np.random.default_rng([TOY_TAG, int(seed), 0])
        d = Lr.RW_DIM - 2
        self.seed = int(seed)
        self.proto = {w: g.normal(size=d) * (TOY_SIGNAL / np.sqrt(d)) for w in VOCAB}

    def thing(self, rng: np.random.Generator) -> Tuple[str, str, str]:
        return (W.SHAPES[int(rng.integers(len(W.SHAPES)))], W.COLOUR_NAMES[int(rng.integers(len(W.COLOUR_NAMES)))],
                W.SIZE_NAMES[int(rng.integers(len(W.SIZE_NAMES)))])

    def x(self, t: Tuple[str, str, str], rng: np.random.Generator) -> np.ndarray:
        f = self.proto[t[0]] + self.proto[t[1]] + self.proto[t[2]] + rng.normal(size=Lr.RW_DIM - 2)
        return np.concatenate([f, rng.uniform(0.0, 128.0, size=2) / Lr.POS_SCALE])

    def scene(self, room: str, rng: np.random.Generator) -> Tuple[np.ndarray, Tuple[str, ...], List[Tuple[str, str, str]]]:
        k = W._n_things(rng)
        attrs = [self.thing(rng) for _ in range(k)]
        X = np.stack([self.x(t, rng) for t in attrs])
        tpl = W.TEMPLATES[int(rng.integers(len(W.TEMPLATES)))]
        slots = RM.SLOT_TYPES[tpl]
        if room == "A":
            t = attrs[int(rng.integers(k))]
            val = {"shape": t[0], "colour": t[1], "size": t[2]}
            words = tuple(val[s] for s in slots)
        elif room == "B":
            words = tuple(_TOY_TYPES[s][int(rng.integers(len(_TOY_TYPES[s])))] for s in slots)
        else:
            raise Tmem5Error(f"no toy room {room!r}")
        return X, words, attrs


def toy_order(seed: int) -> List[str]:
    """The toy's 200 blocks: exactly 50 in B (500 scenes, N's visits in a RANDOM-CTX life), at positions from the seed."""
    g = np.random.default_rng([TOY_TAG, int(seed), 1])
    b_at = {int(i) for i in g.choice(TOY_BLOCKS, size=TOY_B_BLOCKS, replace=False)}
    return ["B" if i in b_at else "A" for i in range(TOY_BLOCKS)]


def toy_life(seed: int, learn_bias: bool = True) -> Dict[str, object]:
    """One toy life of the context learner (lr 0.01, lr_g 0.001; with biases = the law's learner, without = gain only):
    g_A and g_B after every block, the first block (and B-scene count) at which g_B ≤ 0.1, and the toy's difficulty (A's
    forced naming by the shared map on fresh one-thing things)."""
    cpu0 = time.process_time()
    world = ToyWorld(seed)
    order = toy_order(seed)
    L = CX.CtxLearner(TOY_ROOMS, lr=Lr.LR_S1B1, lr_g=CX.LR_G, learn_gain=True, learn_bias=learn_bias)
    rng = np.random.default_rng([TOY_TAG, int(seed), 2])
    gA, gB, nB, first = [], [], 0, None
    for b, room in enumerate(order, start=1):
        L.set_context(room)
        for i in range(PK.BLOCK):
            X, words, _a = world.scene(room, rng)
            L.train_scene(X, words, rng=np.random.default_rng([TOY_TAG, int(seed), 3, b, i]))
            nB += int(room == "B")
        gA.append(float(L.g["A"]))
        gB.append(float(L.g["B"]))
        if first is None and L.g["B"] <= TOY_GB_BAR:
            first = [b, nB]
    ev = np.random.default_rng([TOY_TAG, int(seed), 4])
    acc: Dict[str, List[bool]] = {t: [] for t in _TOY_TYPES}
    for _ in range(TOY_EVAL_N):
        t = world.thing(ev)
        x = world.x(t, ev)
        for k, (typ, ws) in enumerate(_TOY_TYPES.items()):
            acc[typ].append(L.name_forced(x, ws) == t[k])
    b_blocks = [i for i, r in enumerate(order, start=1) if r == "B"]
    return {"seed": int(seed), "learn_bias": bool(learn_bias), "g_A": gA, "g_B": gB, "g_B_end": gB[-1],
            "g_B_min": min(gB), "g_A_min": min(gA), "g_A_end": gA[-1], "n_B_scenes": nB, "first_g_B_le_bar": first,
            "g_B_at_B_blocks": [gB[b - 1] for b in b_blocks], "naming_A": {t: float(np.mean(v)) for t, v in acc.items()},
            "c_B_norm": float(np.linalg.norm(L.c["B"])), "cpu_s": time.process_time() - cpu0}


def toy_gate() -> Dict[str, object]:
    runs = {s: {"bias": toy_life(s, True), "gain_only": toy_life(s, False)} for s in TOY_SEEDS}
    per = {s: {"g_B_end": r["bias"]["g_B_end"], "g_A_min": r["bias"]["g_A_min"],
               "pass": r["bias"]["g_B_end"] <= TOY_GB_BAR and r["bias"]["g_A_min"] >= TOY_GA_BAR} for s, r in runs.items()}
    return {"runs": runs, "per_seed": per, "pass": all(v["pass"] for v in per.values())}


# ================================================================================================ the chain-rule pin (§3 step 3)
def fd_pin(L: CX.CtxLearner, raw: np.ndarray, words: Sequence[str], room: str, h: float = FD_H) -> Dict[str, object]:
    """The step on ONE one-thing scene (where the delta rule IS the cross-entropy's gradient) against −rate · ∂L/∂θ by
    central differences at the post-observation standardisation, for every coordinate of V, g_room, c_room and b; an error
    passes at ≤ FD_TOL · max(1, |step|). The planted offender: V's step scaled by g_room a SECOND time."""
    raw = np.atleast_2d(np.asarray(raw, dtype=np.float64))
    if raw.shape[0] != 1:
        raise Tmem5Error("the chain-rule pin reads ONE thing: only there is the delta rule the loss's own gradient")
    if any(w not in L.index for w in words):
        raise Tmem5Error("the pin's scene must carry heard words only (no episodic write)")
    L2 = copy.deepcopy(L)
    L2.set_context(room)
    L2.train_scene(raw, words, rng=np.random.default_rng(0))
    dV, db, dg, dc = L2.V - L.V, L2.b - L.b, L2.g[room] - L.g[room], L2.c[room] - L.c[room]
    P = copy.deepcopy(L)
    P.stats.observe(raw)
    P.set_context(room)

    def num(get, put, rate):
        x0 = get()
        put(x0 + h)
        up = P.scene_loss(raw, words, room)
        put(x0 - h)
        dn = P.scene_loss(raw, words, room)
        put(x0)
        return -rate * (up - dn) / (2.0 * h)

    err = {"V": 0.0, "g": 0.0, "c": 0.0, "b": 0.0}
    numV = np.zeros_like(dV)
    for j in range(dV.shape[0]):
        for k in range(dV.shape[1]):
            def put(v, j=j, k=k):
                P.V[j, k] = v
            numV[j, k] = num(lambda j=j, k=k: float(P.V[j, k]), put, P.lr)
            err["V"] = max(err["V"], abs(dV[j, k] - numV[j, k]) / max(1.0, abs(dV[j, k])))

    def put_g(v):
        P.g[room] = v
    n_g = num(lambda: float(P.g[room]), put_g, P.lr_g)
    err["g"] = abs(dg - n_g) / max(1.0, abs(dg))
    for j in range(len(dc)):
        def put_c(v, j=j):
            P.c[room][j] = v

        def put_b(v, j=j):
            P.b[j] = v
        n_c = num(lambda j=j: float(P.c[room][j]), put_c, P.lr)
        n_b = num(lambda j=j: float(P.b[j]), put_b, P.lr)
        err["c"] = max(err["c"], abs(dc[j] - n_c) / max(1.0, abs(dc[j])))
        err["b"] = max(err["b"], abs(db[j] - n_b) / max(1.0, abs(db[j])))
    j, k = np.unravel_index(int(np.argmax(np.abs(dV))), dV.shape)
    doubled = abs(dV[j, k] * L.g[room] - numV[j, k]) / max(1.0, abs(dV[j, k]))
    return {"room": room, "g": float(L.g[room]), "max_err": err, "pass": max(err.values()) <= FD_TOL,
            "planted_doubled_err": float(doubled), "planted_doubled_caught": bool(doubled > FD_TOL),
            "step": {"dV_max": float(np.abs(dV).max()), "dg": float(dg), "dc_max": float(np.abs(dc).max())}}


def fd_scene(data, room: str, known: Sequence[str], start: int = 1000) -> Tuple[int, np.ndarray, List[str]]:
    """The first ONE-thing visit scene of `room` from index `start` on whose words are all heard (never a scene a gate life
    of ≤ 60 blocks can have met: 60 blocks read at most 600 of a room's 2,000)."""
    for i in range(start, RM.pool_size(room, "visit")):
        X, words = data.visit_scene(room, i)
        if np.atleast_2d(X).shape[0] == 1 and words and all(w in known for w in words):
            return i, np.atleast_2d(X), list(words)
    raise Tmem5Error(f"room {room}: no one-thing scene of heard words from {start}")


# ================================================================================================ the records
def run_path(root: Path, seed: int, arm: str) -> Path:
    return Path(root) / str(seed) / "runs" / f"{arm}.json"


def band_path(root: Path, seed: int, learner: str, k: int) -> Path:
    return Path(root) / str(seed) / "band" / learner / f"random-{k:02d}.json"


def _load(p: Path) -> Optional[Dict[str, object]]:
    return json.loads(p.read_text()) if p.exists() else None


def dump(path: Path, run: Dict[str, object]) -> None:
    R.dump(path, {k: v for k, v in run.items() if not k.startswith("_")})


def blind_fraction(seed: int) -> Optional[float]:
    """The context-blind RANDOM's N fraction on the bar's window, from S1c's own record (AMENDMENT 1 §2's print)."""
    old = _load(S2.s1c_run_path(seed, "RANDOM"))
    return None if old is None else n_fraction(old["record"])["fraction"]


# ================================================================================================ THE FIRST GATE
def record_lines5(run: Dict[str, object]) -> List[str]:
    """S1c-2's record lines, then the context's own per block: the label (σ_b under the shuffle) and the four gains."""
    out = S2.record_lines2({**run, "arm": run["arm"]})
    for i, c in enumerate(run["ctx_record"], start=1):
        extra = f"label {c['label']}" + (f" (σ {c['sigma']})" if c.get("sigma") else "")
        extra += " · g " + " ".join(f"{r}:{v:.4f}" for r, v in c["g"].items()) + f" · wl@ḡ_R {c['wl_gR']}"
        out[i] = out[i] + " · " + extra
    return out


def first_gate5(root: Path = ROOT, log=print) -> Dict[str, object]:
    """PREREG-TMEM5 §3 on seed 20261301, printed whole; every step a STOP on a miss but step 4 (a print)."""
    out: Dict[str, object] = {"verdict": "STOP", "seed": GATE_SEED, "rooms": list(ROOMS)}
    lines: List[str] = []

    def say(s: str) -> None:
        lines.append(s)
        log(s)

    def stop(step: str) -> Dict[str, object]:
        say(f"   STOP at {step}")
        out["lines"] = lines
        return out

    shas = check_prereg()
    out["shas"] = shas
    say(f"THE FIRST GATE (T-MEM-5, seed {GATE_SEED}, THE LAW'S WORLD {list(ROOMS)}) — PREREG-TMEM5 {shas['prereg_tmem5'][:12]}… · "
        f"AMENDMENT 1 {shas['amend1_tmem5'][:12]}… · PREREG-S1C2 {shas['prereg_s1c2'][:12]}… · PREREG-S1C {shas['prereg_s1c'][:12]}… · "
        f"code {R.code_identity()['code_sha_file']}")
    gdir = Path(root) / "gate"
    # 1. identity
    pools = T1.pools_identical(POOLS_ROOT, GATE_SEED)
    tset = T1.test_set_identical()
    fence = S.fence_sweep()
    data = S.RoomData(POOLS_ROOT, GATE_SEED, ROOMS)
    test = T1.TestSetM()
    idr, diffs, side = {}, {}, {}
    for a, p in IDENTITY.items():
        idr[a] = life5(data, test, a, log=log)
        dump(gdir / "step1" / f"{a}.json", idr[a])
        old = _load(S2.s1c_run_path(GATE_SEED, p))
        diffs[a] = ["record missing"] if old is None else S2.identity_diff(idr[a], old)
        side[a] = None if old is None else {k: (str(v[0])[:60], str(v[1])[:60]) for k, v in S2.masked_side_by_side(idr[a], old).items()}
    out["step1"] = {"pools_same": pools["same"], "test_set_same": tset["same"], "fence": fence, "diffs": diffs, "masked": side}
    say(f"1. identity — the pools (scene-tmem1's redraw) against S1c's, as files: {'SAME' if pools['same'] else 'DIFFERENT'} · the "
        f"fixed test set against S1b-1's: {'SAME' if tset['same'] else 'DIFFERENT'} · the truth fence's sweep (rooms.py, pickers.py, "
        f"memory.py, context.py): Ran {fence['ran']}, {'OK' if fence['ok'] else 'FAILED'} · the context learner FROZEN (g ≡ 1, "
        f"c ≡ 0, neither learned) against S1c's records ({S2.s1c_run_path(GATE_SEED, 'PROGRESS').parent}), every field but the five "
        f"masked BY NAME {list(S2.VOLATILE)}: " + " · ".join(
            f"{a} ({IDENTITY[a]}) {'EQUAL' if not d else 'DIFFERS in ' + str(d)}" for a, d in diffs.items()))
    for a in IDENTITY:
        if side[a]:
            say(f"   the masked fields of {a} (S1c | this tree): " + " · ".join(f"{k}: {v[0]} | {v[1]}" for k, v in side[a].items()))
    if not (pools["same"] and tset["same"] and fence["ok"]) or any(diffs.values()):
        return stop("step 1")
    # 2. the fixed-point toy
    toy = toy_gate()
    R.dump(gdir / "step2" / "toy.json", toy)
    out["step2"] = {"per_seed": toy["per_seed"], "pass": toy["pass"],
                    "gain_only": {s: {"g_B_end": r["gain_only"]["g_B_end"], "g_B_min": r["gain_only"]["g_B_min"],
                                      "g_A_min": r["gain_only"]["g_A_min"]} for s, r in toy["runs"].items()}}
    say(f"2. the fixed-point toy (declared construction: signal {TOY_SIGNAL}, 13 words, S1's 1–3-thing mix; room B's words "
        f"independent of its things; {TOY_BLOCKS} blocks, {TOY_B_BLOCKS} in B = {TOY_B_BLOCKS * PK.BLOCK} B-scenes; lr_g {CX.LR_G}): "
        f"with biases, g_B ≤ {TOY_GB_BAR} after its {TOY_B_BLOCKS * PK.BLOCK} B-scenes AND g_A ≥ {TOY_GA_BAR} at every block, at seeds "
        f"{list(TOY_SEEDS)}:")
    for s, r in toy["runs"].items():
        b, g = r["bias"], r["gain_only"]
        tr = ", ".join(f"{v:.3f}" for v in b["g_B_at_B_blocks"][4::5])
        say(f"   seed {s}: g_B {b['g_B_end']:.4f} (first ≤ {TOY_GB_BAR} at block {b['first_g_B_le_bar'][0] if b['first_g_B_le_bar'] else '—'}"
            f"{', after ' + str(b['first_g_B_le_bar'][1]) + ' B-scenes' if b['first_g_B_le_bar'] else ''}) · g_A min {b['g_A_min']:.4f}, "
            f"end {b['g_A_end']:.4f} · |c_B| {b['c_B_norm']:.3f} → {'PASS' if toy['per_seed'][s]['pass'] else 'MISS'} · the toy's "
            f"difficulty (A's forced naming, one thing): " + " ".join(f"{t} {v:.3f}" for t, v in b["naming_A"].items())
            + f" · g_B after every 5th B-block: {tr} · WITHOUT biases (gain only, a print): g_B end {g['g_B_end']:.4f}, min "
            f"{g['g_B_min']:.4f}, g_A min {g['g_A_min']:.4f} · CPU {b['cpu_s'] + g['cpu_s']:.1f} s")
    if not toy["pass"]:
        return stop("step 2 (lr_g is the knob, never the bar: a STOP and an amendment)")
    # 3. the chain-rule pin
    L = new_ctx_learner("ctx")
    for blk in range(12):
        room = ROOMS[blk % len(ROOMS)]
        L.set_context(room)
        S.train_block(L, data, room, (blk // len(ROOMS)) * PK.BLOCK, GATE_SEED)
    pins = {}
    for room in ("R2", "N"):
        i, raw, words = fd_scene(data, room, list(L.index))
        for gv in (None, 0.5):
            LL = copy.deepcopy(L)
            if gv is not None:
                LL.g[room] = gv
            pins[f"{room}@{'own g' if gv is None else 'g 0.5'}"] = {**fd_pin(LL, raw, words, room), "scene": i, "words": words}
    ok3 = all(p["pass"] for p in pins.values()) and all(p["planted_doubled_caught"] for k, p in pins.items() if k.endswith("g 0.5"))
    out["step3"] = {"pins": pins, "pass": ok3}
    say(f"3. the chain-rule pin — the step on one one-thing scene against −rate · ∂L/∂θ by central differences (h {FD_H:g}), every "
        f"coordinate of V, g, c, b, to {FD_TOL:g} (a learner of 12 round-robin blocks):")
    for k, p in pins.items():
        say(f"   {k} (visit {p['scene']}, «{' '.join(p['words'])}», g {p['g']:.4f}): max error V {p['max_err']['V']:.2e} · g "
            f"{p['max_err']['g']:.2e} · c {p['max_err']['c']:.2e} · b {p['max_err']['b']:.2e} → {'PASS' if p['pass'] else 'MISS'} · the "
            f"planted doubled factor: error {p['planted_doubled_err']:.2e} ({'CAUGHT' if p['planted_doubled_caught'] else 'not caught'})")
    if not ok3:
        return stop("step 3")
    # 4. the instrument under RANDOM-CTX (a print)
    r60 = life5(data, test, "RANDOM-CTX", n_blocks=GATE4_BLOCKS, log=log)
    dump(gdir / "step4" / "RANDOM-CTX-60.json", r60)
    nf = n_fraction(r60["record"])
    old60 = _load(S1C_ROOT / "gate" / "step2-law-RANDOM60.json")
    bf = n_fraction(old60["record"]) if old60 is not None else None
    gtr = r60["marks5"]["trajectory"]
    out["step4"] = {"fraction": nf, "blind": bf, "g_N": gtr["N"], "g_end": r60["marks5"]["g_end"]}
    say(f"4. the instrument under RANDOM-CTX over {GATE4_BLOCKS} blocks (a PRINT): N's own mean drop over its blocks 21–{GATE4_BLOCKS} "
        f"{S._fmt(nf['num'], 4)} (n {nf['n_N']}) · the learnable rooms' {S._fmt(nf['den'], 4)} (n {nf['n_R']}) · the fraction "
        f"{S._fmt(nf['fraction'])}" + (f" · the context-blind RANDOM of S1c's gate, same picks and window: {S._fmt(bf['num'], 4)} / "
                                         f"{S._fmt(bf['den'], 4)} = {S._fmt(bf['fraction'])}" if bf else " · (S1c's 60-block record missing)"))
    say("   g_N after each N-block: " + ", ".join(f"b{b} {v:.4f}" for b, v in gtr["N"]) + " · the gains at block "
        f"{GATE4_BLOCKS}: " + " ".join(f"{r} {v:.4f}" for r, v in r60["marks5"]["g_end"].items()))
    # 5. the smoke of every arm, read whole, and the instrument's pins
    smoke = {a: life5(data, test, a, n_blocks=SMOKE_BLOCKS) for a in ARMS}
    for a, r in smoke.items():
        dump(gdir / "smoke" / f"{a}.json", r)
    ident = {"NULL-CTX": life5(data, test, "NULL-CTX", n_blocks=SMOKE_BLOCKS, identity_credit=True),
             "NULL-CTX+REPLAY": life5(data, test, "NULL-CTX+REPLAY", n_blocks=SMOKE_BLOCKS, identity_credit=True)}
    pi = PK.null_derangement(GATE_SEED, ROOMS)
    home = {a: [x["block"] for x in smoke[a]["record"] if x["credited"] == x["room"]] for a in ("NULL-CTX", "NULL-CTX+REPLAY")}
    sig_ok = {a: all(PK.is_derangement(c["sigma"]) and c["sigma"] == shuffle_sigma(GATE_SEED, c["block"], ROOMS)
                     and c["label"] == c["sigma"][x["room"]] != x["room"] for x, c in zip(smoke[a]["record"], smoke[a]["ctx_record"]))
              for a in ("SHUFFLED-CTX", "SHUFFLED-CTX-RANDOM")}
    planted_sigma = not PK.is_derangement({r: r for r in ROOMS})
    expl = {a: PK.exploration_mismatches(smoke[a]["record"], GATE_SEED, ROOMS) for a in EPS_ARMS}
    flip = [dict(x) for x in smoke["PROGRESS-CTX"]["record"]]
    kp = next((i for i, x in enumerate(flip) if x["flag"] == "policy"), None)
    caught = False
    if kp is not None:
        flip[kp]["flag"] = "explore"
        caught = PK.exploration_mismatches(flip, GATE_SEED, ROOMS) == [flip[kp]["block"]]
    s5 = {"pi": pi, "null_pi_is_pi": all(smoke[a]["pi"] == pi for a in home), "is_derangement": PK.is_derangement(pi),
          "identity_is_progress": S2.rows_equal(ident["NULL-CTX"], smoke["PROGRESS-CTX"]),
          "identity_is_progress_replay": S2.rows_equal(ident["NULL-CTX+REPLAY"], smoke["PROGRESS-CTX+REPLAY"]),
          "credit_lands_home": home, "sigma_ok": sig_ok, "planted_identity_sigma_caught": planted_sigma,
          "exploration_mismatches": expl, "planted_flip_caught": caught}
    s5["pass"] = bool(s5["null_pi_is_pi"] and s5["is_derangement"] and s5["identity_is_progress"] and s5["identity_is_progress_replay"]
                      and not any(home.values()) and all(sig_ok.values()) and planted_sigma and not any(expl.values()) and caught)
    out["step5"] = {**s5, "rooms": {a: [x["room"] for x in smoke[a]["record"]] for a in ARMS}}
    say(f"5. the {SMOKE_BLOCKS}-block smoke of every arm — the instrument's pins: π = {pi} (a derangement: {s5['is_derangement']}; "
        f"both nulls carry it: {s5['null_pi_is_pi']}) · a null's credit lands on its producer at {({a: v or 'none' for a, v in home.items()})} · "
        f"the identity credit IS its estimate's picker — NULL-CTX ≡ PROGRESS-CTX: {s5['identity_is_progress']} · NULL-CTX+REPLAY ≡ "
        f"PROGRESS-CTX+REPLAY: {s5['identity_is_progress_replay']} · every σ_b a derangement from ctx-shuffle:<seed>:<block>, the "
        f"block trained under σ_b(room) ≠ room: {sig_ok} (a planted identity σ caught: {planted_sigma}) · the ε flags agree with "
        f"the stream in every ε arm: {not any(expl.values())} (a planted flipped flag caught: {caught}) → {'PASS' if s5['pass'] else 'MISS'}")
    say("   each record whole:")
    for a in ARMS:
        for ln in record_lines5(smoke[a]):
            say(ln)
    if not s5["pass"]:
        return stop("step 5")
    out["verdict"] = "PROCEED"
    say("THE FIRST GATE: PROCEED")
    out["lines"] = lines
    return out


def gate_ok(root: Path = ROOT) -> Dict[str, object]:
    p = Path(root) / "gate" / "first_gate.json"
    if not p.exists():
        raise Tmem5Error(f"{p} is missing — THE FIRST GATE has not run")
    g = json.loads(p.read_text())
    if g.get("verdict") != "PROCEED":
        raise Tmem5Error(f"THE FIRST GATE reads {g.get('verdict')} — no life")
    return g


# ================================================================================================ the price
def price(root: Path = ROOT, log=print) -> Dict[str, object]:
    """Solo at seed 20261301: one life of each cost class; the projection for the unit: 14 arms × 3 seeds + 120 band lives
    (the pools are scene-tmem1's, reused)."""
    check_prereg()
    gate_ok(root)
    data = S.RoomData(POOLS_ROOT, GATE_SEED, ROOMS)
    test = T1.TestSetM()
    cpu = {}
    for a in ("RANDOM-CTX", "RANDOM-CTX+REPLAY", "ORACLE-CTX", "ORACLE-CTX+REPLAY"):
        r = life5(data, test, a)
        cpu[a] = r["cpu_s"]
        log(f"[price] {a}: {r['cpu_s']:.1f} CPU-s ({r['wall_s']:.1f} s wall)")
    w = life5(data, test, "PROGRESS-CTX", where=True)
    cpu["WHERE"] = w["where"]["cpu_s"]
    cpu["PROGRESS-CTX"] = w["cpu_s"] - w["where"]["cpu_s"]
    log(f"[price] PROGRESS-CTX: {cpu['PROGRESS-CTX']:.1f} CPU-s + A-READ+WHERE at its end {cpu['WHERE']:.1f} CPU-s")
    plain, rep = cpu["RANDOM-CTX"], cpu["RANDOM-CTX+REPLAY"]
    per_seed_lives = 9 * plain + 3 * rep + cpu["ORACLE-CTX"] + cpu["ORACLE-CTX+REPLAY"] + 2 * cpu["WHERE"]
    per_seed_bands = len(BAND_K) * (plain + rep)
    total = 3 * (per_seed_lives + per_seed_bands)
    out = {"cpu_s": cpu, "lives_cpu_s": 3 * per_seed_lives, "bands_cpu_s": 3 * per_seed_bands, "unit_cpu_min": total / 60.0}
    log(f"[price] THE UNIT: 42 lives {3 * per_seed_lives / 60:.1f} CPU-min + 120 band lives {3 * per_seed_bands / 60:.1f} = "
        f"{total / 60:.1f} CPU-min (PREREG-TMEM5 §6 estimate ≈ 10–12)")
    R.dump(Path(root) / "price" / "price.json", out)
    return out


# ================================================================================================ the report
def load_all(root: Path = ROOT):
    runs = {s: {a: _load(run_path(root, s, a)) for a in ARMS} for s in SEEDS}
    bands = {s: {ln: [x for x in (_load(band_path(root, s, ln, k)) for k in BAND_K) if x is not None] for ln in BAND_LEARNERS}
             for s in SEEDS}
    return runs, bands


def identity_at_the_run(runs) -> Dict[str, object]:
    out, side = {}, {}
    for s in SEEDS:
        for a, p in IDENTITY.items():
            old, new = _load(S2.s1c_run_path(s, p)), runs[s][a]
            out[f"{a}@{s}"] = ["missing"] if (old is None or new is None) else S2.identity_diff(new, old)
            if old is not None and new is not None and s == SEEDS[0]:
                side[a] = {k: (str(v[0])[:50], str(v[1])[:50]) for k, v in S2.masked_side_by_side(new, old).items()}
    return {"diffs": {k: v for k, v in out.items() if v}, "n_compared": len(out), "masked": side}


def refutations5(runs) -> Dict[str, object]:
    """§5 (decided at block 200): (a) g_N > 0.3 at block 200 with biases present (RANDOM-CTX), at ≥ 2 seeds; (b) the
    context null's N fraction < 0.3 (SHUFFLED-CTX under RANDOM — AMENDMENT 1 §2: the same clause as its VOID) at ≥ 2
    seeds, with its four gains at block 200 printed beside it."""
    a, b = {}, {}
    for s in SEEDS:
        x, n = runs[s][MEMORY_ARM], runs[s][MEMORY_NULL]
        a[s] = None if x is None else x["marks5"]["g_N_at_end"] > REFUTE_G
        f = None if n is None else n["marks5"]["n_fraction"]["fraction"]
        b[s] = None if f is None else f < BAR_N_FRACTION
    return {"a": a, "a_refuted": sum(1 for v in a.values() if v) >= 2, "b": b, "b_refuted": sum(1 for v in b.values() if v) >= 2}


def report(root: Path = ROOT, log=print) -> Dict[str, object]:
    shas = check_prereg()
    gate_ok(root)
    runs, bands = load_all(root)
    seeds = list(SEEDS)
    L: List[str] = []
    idc = identity_at_the_run(runs)
    identity_ok = not idc["diffs"]
    L.append(f"T-MEM-5 «WHERE SEPARATES» — the report · PREREG-TMEM5 {shas['prereg_tmem5'][:12]}… · AMENDMENT 1 {shas['amend1_tmem5'][:12]}… "
             f"(with PREREG-S1C2 {shas['prereg_s1c2'][:12]}…, PREREG-S1C {shas['prereg_s1c'][:12]}…, AMENDMENT 1 of S1c "
             f"{shas['amend1_s1c'][:12]}…) · THE LAW'S WORLD {list(ROOMS)} · 200 blocks × 10 scenes · lr 0.01, lr_g {CX.LR_G} · R = {R_REPLAY}")
    L.append("")
    L.append(f"THE IDENTITY CONTROL (the context learner FROZEN, PROGRESS and RANDOM at every seed, against S1c's records; every field "
             f"but {list(S2.VOLATILE)}): {idc['n_compared'] - len(idc['diffs'])} of {idc['n_compared']} EQUAL"
             + (f" · DIFFERENT: {idc['diffs']}" if idc["diffs"] else ""))
    for a, v in idc["masked"].items():
        L.append(f"   the masked fields of {a}@{seeds[0]} (S1c | this tree): " + " · ".join(f"{k}: {x[0]} | {x[1]}" for k, x in v.items()))
    L.append("")
    # MEMORY
    mps = {s: {"X": runs[s][MEMORY_ARM]["marks5"] if runs[s][MEMORY_ARM] else None,
               "NULL": runs[s][MEMORY_NULL]["marks5"] if runs[s][MEMORY_NULL] else None,
               "blind": blind_fraction(s)} for s in seeds}
    mv = memory_verdict(mps)
    if not identity_ok:
        mv["verdict_before_identity"], mv["verdict"] = mv["verdict"], "NOT GRADABLE (IDENTITY)"
    L.append(f"MEMORY «WHERE separates» (RANDOM-CTX, every seed: N's fraction over blocks 21–200 < {BAR_N_FRACTION} AND g_N ≤ "
             f"{BAR_G_RATIO} · ḡ_R; the context null VOIDs it iff SHUFFLED-CTX under RANDOM meets the fraction clause at ≥ 2 seeds — "
             f"AMENDMENT 1 §2): VERDICT {mv['verdict']}" + (f" · missing {mv['missing']}" if mv.get("missing") else ""))
    for s, d in mv.get("seeds", {}).items():
        fr, nf = d["fraction"], d["null_fraction"]
        L.append(f"   {s}: N's fraction {S._fmt(fr['num'], 4)} / {S._fmt(fr['den'], 4)} = {S._fmt(fr['fraction'])} (n {fr['n_N']} / "
                 f"{fr['n_R']}) {d['f_state']} · g_N {S._fmt(d['g_N'], 4)} (mean of the last {d['g_N_n']} N-blocks; sd {S._fmt(d['g_N_sd'], 4)}"
                 f"{' > the bar: NOISE' if d['noisy'] else ''}) vs {BAR_G_RATIO} · ḡ_R {S._fmt(d['g_R'], 4)} = {S._fmt(d['bar_g'], 4)} "
                 f"{d['g_state']} (ḡ_R at block 200: {S._fmt(d['g_R_at_end'], 4)}) · g_N at block 200 {S._fmt(d['g_N_at_end'], 4)}")
        L.append(f"      the null (SHUFFLED-CTX under RANDOM, the same picks, the same window): {S._fmt(nf['num'], 4)} / {S._fmt(nf['den'], 4)} "
                 f"= {S._fmt(nf['fraction'])} — {'MEETS the clause' if d['null_meets'] else 'does not meet it'} · the context-blind RANDOM "
                 f"(S1c's record) {S._fmt(d['blind_fraction'])} · null − blind {S._fmt(d['null_minus_blind'])} · the null's four gains at "
                 f"block 200: " + " ".join(f"{r} {v:.4f}" for r, v in d["null_g_end"].items()))
        L.append("      g_N after each N-block: " + ", ".join(f"b{b} {v:.3f}" for b, v in d["trajectory_N"]))
    L.append("")
    # CURIOSITY
    cv = {}
    for X, (learner, O, RND, NUL) in CURIOSITY.items():
        ps = {}
        for s in seeds:
            bl = bands[s][learner]

            def mk(a, s=s):
                return runs[s][a]["marks"] if runs[s][a] else None
            ps[s] = {"X": mk(X), "O": mk(O), "RND": mk(RND), "NUL": mk(NUL), "band_A": [b["marks"]["A"] for b in bl], "band_n": len(bl)}
        v = curiosity_verdict(ps)
        if not identity_ok:
            v["verdict_before_identity"], v["verdict"] = v["verdict"], "NOT GRADABLE (IDENTITY)"
        cv[X] = v
        L.append(f"CURIOSITY «progress chooses» — {X} (O = {O}, RANDOM = {RND} with its 20-life band, NULL = {NUL}): VERDICT "
                 f"{v['verdict']}" + (f" · missing {v['missing']}" if v.get("missing") else ""))
        for s, d in v.get("seeds", {}).items():
            b = d["bars"]
            L.append(f"   {s}: A {b['A_band']['value']:.3f} above the band [{d['band'][0]:.3f}, {d['band'][1]:.3f}] (n {d['band_n']}; O "
                     f"{b['A_band']['oracle']:.3f}) {b['A_band']['state']} · SHARE_N {b['SHARE_N']['value']:.3f} vs {b['SHARE_N']['bar']:.3f} "
                     f"{b['SHARE_N']['state']} · LEAVE_N {b['LEAVE_N']['value']} vs {LEAVE_BAR} {b['LEAVE_N']['state']} · the positive "
                     f"control {d['positive_control']:+.3f} {'PASS' if d['positive_control'] >= POSITIVE_CONTROL else 'MISS'} · the null "
                     f"(A {d['null']['A']:.3f}, SHARE_N {d['null']['SHARE_N']:.3f}) meets X's bars: {d['null_meets']} · (a reading: A ≥ 0.80 × O "
                     f"= {d['reading_080']['bar']:.3f}: {d['reading_080']['meets']})")
    L.append("")
    L.append("A MEMORY pass with a CURIOSITY fail is a RESULT (the noise room settled, and progress still cannot choose).")
    L.append("")
    L.append("per seed, every arm (A · A read at ḡ_R · S12 · SHARE [R1 R2 R3 N] · explore apart · LEAVE_N · lock-in · M1 · wl@200 · N's "
             "fraction 21–200 (all blocks) · g_N (last 10) · the gains at block 200 · CPU):")
    for s in seeds:
        L.append(f" seed {s}:")
        for a in ARMS:
            r = runs[s][a]
            if r is None:
                L.append(f"   {a:<20} NOT GRADABLE BY NAME (the life is missing)")
                continue
            m, m5 = r["marks"], r["marks5"]
            L.append(f"   {a:<20} A {m['A']:.3f} · A@ḡ_R {S._fmt(m5['A_gR'])} · S12 {m['S12'] if m['S12'] is not None else '∞'} · SHARE ["
                     + " ".join(f"{m['share'][q]:.3f}" for q in ROOMS) + "] · explore [" + " ".join(f"{m['explore'][q]:.3f}" for q in ROOMS)
                     + f"] · LEAVE_N {m['leave']['N']} · lock-in {m['longest_run']} ({m['longest_run_room']}) · M1 {S._fmt(m['M1'])} · wl@200 "
                     f"{m['wl_end']} · N fraction {S._fmt(m5['n_fraction']['fraction'])} ({S._fmt(m5['n_fraction_all']['fraction'])}) · g_N "
                     f"{S._fmt(m5['g_N'], 4)} · g@200 " + " ".join(f"{q} {v:.3f}" for q, v in m5["g_end"].items()) + f" · CPU {r['cpu_s']:.1f} s")
    L.append("")
    # the readings
    L.append("the readings (no bar):")
    for s in seeds:
        bo, rc = runs[s]["BIAS-ONLY-RANDOM"], runs[s][MEMORY_ARM]
        bp, pc_ = runs[s]["BIAS-ONLY-PROGRESS"], runs[s]["PROGRESS-CTX"]
        if bo and rc:
            L.append(f"   {s}: BIAS-ONLY (c learned, g ≡ 1) under RANDOM — N's fraction {S._fmt(bo['marks5']['n_fraction']['fraction'])} "
                     f"against RANDOM-CTX's {S._fmt(rc['marks5']['n_fraction']['fraction'])} (which half does the work) · under PROGRESS: "
                     + (f"A {bp['marks']['A']:.3f}, SHARE_N {bp['marks']['share']['N']:.3f}, LEAVE_N {bp['marks']['leave']['N']} against "
                        f"PROGRESS-CTX's A {pc_['marks']['A']:.3f}, SHARE_N {pc_['marks']['share']['N']:.3f}, LEAVE_N {pc_['marks']['leave']['N']}"
                        if (bp and pc_) else "missing"))
        sc = runs[s]["SHUFFLED-CTX"]
        if sc:
            L.append(f"      SHUFFLED-CTX under PROGRESS: N's fraction {S._fmt(sc['marks5']['n_fraction']['fraction'])} (n {sc['marks5']['n_fraction']['n_N']}) "
                     f"· SHARE_N {sc['marks']['share']['N']:.3f} · LEAVE_N {sc['marks']['leave']['N']} · its gains at block 200 "
                     + " ".join(f"{q} {v:.3f}" for q, v in sc["marks5"]["g_end"].items()))
        for a in WHERE_ARMS:
            r = runs[s][a]
            if r is None or "where" not in r:
                continue
            w = r["where"]
            if not w.get("types"):
                L.append(f"      A-READ+WHERE on {a}: {w.get('note')}")
                continue
            L.append(f"      A-READ+WHERE on {a} (block 200; ε {w['eps']}): rows kept {w['rows_kept']} of {w['rows_total']} · by room "
                     + " ".join(f"{q} {v['kept']}/{v['rows']}" for q, v in w["by_room"].items()) + f" · WORDS-LEARNED: WHERE {w['wl_where']} · "
                     f"the unkeyed A-READ {w['wl_all']} · the map (A-RW) {w['wl_rw']}")
            L.append("         N's rows excluded per word: " + " ".join(f"{q} {n}" for q, n in w["excluded_N"].items())
                     + " · STRONG per room: " + " · ".join(f"{q} {sorted(v['strong'])}" for q, v in w["per_room"].items()))
            L.append("         naming on the held items (WHERE | unkeyed | map): " + " ".join(
                f"{q} {S._fmt(w['rates_where'].get(q), 2)}|{S._fmt(w['rates_all'].get(q), 2)}|{S._fmt(w['rates_rw'].get(q), 2)}" for q in VOCAB))
            nw = w["per_room"].get("N", {}).get("words", {})
            if nw:
                L.append("         N's words in N's own reader (attributed rows, leave-one-out agreement): " + " ".join(
                    f"{q} {v['n_att']}/{S._fmt(v['agree'], 2)}" for q, v in nw.items()))
    L.append("")
    rf = refutations5(runs)
    L.append("the refutations (§5, decided at block 200):")
    L.append(f"   (a) g_N > {REFUTE_G} at block 200 with biases present (RANDOM-CTX): " + " · ".join(
        f"{s} {'holds' if v else 'does not hold' if v is not None else 'NOT GRADABLE'}" for s, v in rf["a"].items())
             + f" → {'REFUTED: the contradiction is not the mechanism; S1c-2 WHERE reading was a correlate' if rf['a_refuted'] else 'not refuted'}")
    L.append(f"   (b) the context null's N fraction < {BAR_N_FRACTION} (SHUFFLED-CTX under RANDOM): " + " · ".join(
        f"{s} {'holds' if v else 'does not hold' if v is not None else 'NOT GRADABLE'}" for s, v in rf["b"].items())
             + f" → {'REFUTED: the gain separates without the room' if rf['b_refuted'] else 'not refuted'} (its four gains at block 200 "
               f"are printed with the MEMORY bar above)")
    L.append("the predictions (§5, from the mechanism; tags as written):")
    for s in seeds:
        x, p = runs[s][MEMORY_ARM], runs[s]["PROGRESS-CTX"]
        if x is None or p is None:
            continue
        cvs = cv["PROGRESS-CTX"].get("seeds", {}).get(s)
        L.append(f"   {s}: g_N → ≈ 0 [Likely]: g_N at block 200 {x['marks5']['g_N_at_end']:.4f} · N's fraction < 0.3 [Likely]: "
                 f"{S._fmt(x['marks5']['n_fraction']['fraction'])} · PROGRESS-CTX leaves N (LEAVE_N ≤ 50) [Likely]: {p['marks']['leave']['N']} · "
                 f"PROGRESS-CTX's A above RANDOM-CTX's band [Guessing]: " + (f"{p['marks']['A']:.3f} vs {cvs['band'][1]:.3f}" if cvs else "—"))
    L.append("")
    L.append("per-word n on the fixed test set: " + " ".join(f"{w} {n}" for w, n in (runs[seeds[0]]["PROGRESS-CTX"] or {}).get("word_n", {}).items()))
    txt = "\n".join(L)
    (Path(root) / "report.txt").write_text(txt + "\n")
    R.dump(Path(root) / "report.json", {"identity": idc, "memory": mv, "curiosity": cv, "refutations": rf, "shas": shas,
                                        "marks": {s: {a: (runs[s][a]["marks"] if runs[s][a] else None) for a in ARMS} for s in seeds},
                                        "marks5": {s: {a: (runs[s][a]["marks5"] if runs[s][a] else None) for a in ARMS} for s in seeds},
                                        "where": {s: {a: (runs[s][a].get("where") if runs[s][a] else None) for a in WHERE_ARMS} for s in seeds}})
    for ln in L:
        log(ln)
    return {"identity": idc, "memory": mv, "curiosity": cv, "refutations": rf}


# ================================================================================================ the CLI
def _ks(spec: str) -> List[int]:
    a, _, b = spec.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="brain.scene.run_tmem5")
    ap.add_argument("cmd", choices=["check", "first-gate", "run", "band", "price", "report"])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--seed", type=int)
    ap.add_argument("--arm", choices=list(ARMS))
    ap.add_argument("--learner", choices=sorted(BAND_LEARNERS), default="ctx")
    ap.add_argument("--k", default="1-20")
    a = ap.parse_args(argv)
    root = Path(a.root)
    log = R.Log(root / "logs" / f"{a.cmd}.log")
    if a.cmd == "check":
        log(json.dumps(check_prereg()))
        return 0
    check_prereg()
    if a.cmd == "first-gate":
        g = first_gate5(root, log=log)
        R.dump(root / "gate" / "first_gate.json", g)
        (root / "gate" / "first_gate.out").write_text("\n".join(g.get("lines", [])) + "\n")
        return 0 if g["verdict"] == "PROCEED" else 10
    if a.cmd in ("run", "band"):
        gate_ok(root)
        data = S.RoomData(POOLS_ROOT, a.seed, ROOMS)
        test = T1.TestSetM()
        if a.cmd == "run":
            r = life5(data, test, a.arm, where=a.arm in WHERE_ARMS, log=log)
            dump(run_path(root, a.seed, a.arm), r)
            m5 = r["marks5"]
            log(f"[run {a.arm} {a.seed}] A {r['marks']['A']:.3f} · SHARE_N {r['marks']['share']['N']:.3f} · LEAVE_N "
                f"{r['marks']['leave']['N']} · N fraction {S._fmt(m5['n_fraction']['fraction'])} · g_N {S._fmt(m5['g_N'], 4)} · "
                f"{r['cpu_s']:.1f} CPU-s")
            return 0
        arm = BAND_LEARNERS[a.learner]
        for k in _ks(a.k):
            r = life5(data, test, arm, prefix=PK.band_prefix(a.seed, k))
            dump(band_path(root, a.seed, a.learner, k), r)
            log(f"[band {a.learner} {a.seed} k {k}] A {r['marks']['A']:.3f} · SHARE_N {r['marks']['share']['N']:.3f} · {r['cpu_s']:.1f} CPU-s")
        return 0
    if a.cmd == "price":
        price(root, log=log)
        return 0
    if a.cmd == "report":
        report(root, log=log)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
