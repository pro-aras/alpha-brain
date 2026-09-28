"""run_s1c2.py — S1c-2 «netted progress and rehearsal»: the life with the boundary order POST → REPLAY → PRE, the replay
buffer and its draws, the fourteen arms, the identity control against S1c's records, THE FIRST GATE's seven steps, the
price and the report. Runs under /usr/bin/python3.

edit: Claude (Opus 5.5, S1c-2 builder), 2026-09-28 16:19 +0400 — new module, written to docs/brain/r3/PREREG-S1C2.md (genome-wt-brain3 141a8cd,
sha 5e4585c1…, final), which extends PREREG-S1C (a552515a…) with AMENDMENT 1 §1–§5 (92188d04…): everything not restated is
S1c's (run_s1c.py, pickers.py, rooms.py — the pools are S1c's caches, read from S1c's root; rooms.py and the drawing code are
unchanged, so cache.check_code and the room code's sha accept them). The coordinator's rulings on the builder's declared
readings (2026-09-28 16:1x) are marked «ruled» below and listed in docs/brain/r3/S1C2-HANDBACK.md.

  python3 -m brain.scene.run_s1c2 check                         the four shas
  python3 -m brain.scene.run_s1c2 first-gate                    THE FIRST GATE (seed 20261301), steps 1–7
  python3 -m brain.scene.run_s1c2 run --arm A --seed S          one life; <root>/<seed>/runs/<A>.json
  python3 -m brain.scene.run_s1c2 band --learner L --seed S --k A-B   RANDOM's band lives on L = bare | replay
  python3 -m brain.scene.run_s1c2 price                         solo, printed before the unit
  python3 -m brain.scene.run_s1c2 report                        the identity control, the bars, the readings

THE BOUNDARY ORDER (PREREG-S1C2 §2), for every arm at every boundary b: (i) POST_b — L_k for all rooms, the visited room's
drop = PRE_b − POST_b (S1c's drop); (ii) the REPLAY (replay arms only); (iii) PRE_{b+1} — L_k for all rooms again (≡ (i) for a
non-replay arm). WORDS-LEARNED (so A) and M1 at 200 are read at the END of the boundary, after the replay (ruled: the state
that enters the next block; the replay learner's ORACLE and RANDOM are read the same way).
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

from . import pickers as PK
from . import run as R
from . import run_s1c as S

# ------------------------------------------------------------------------------------------------ the PREREG's numbers
PREREG_S1C2_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-S1C2.md")
PREREG_S1C2_SHA256 = "5e4585c11c94d68d5294c35149aefd5636481d6eddcbed2e9b3952a42def2c46"   # final: Fable's confirmation, 141a8cd
ROOT = Path("/data/dev/brain-runs/scene-s1c2")
S1C_ROOT = S.ROOT                    # S1c's run root: its pools (the caches) and its records (the identity control's reference)
ROOMS: Tuple[str, ...] = tuple(S.WORLDS["law"])
R_REPLAY = 10
GATE_SEED = S.GATE_SEED
SMOKE_BLOCKS = 20
BAND_K: Tuple[int, ...] = S.BAND_K
LEAVE_BAR, SHARE_ALLOWANCE, A_VS_ORACLE, POSITIVE_CONTROL = S.BAR_LEAVE_N, S.BAR_SHARE_ALLOWANCE, S.BAR_A_VS_ORACLE, S.BAR_POSITIVE_CONTROL
NET_PIN_TOL = 1e-9
# arm → (the estimate's picker, the replay grain: None = the bare learner, "room" = the law, "visit" = the reading arm)
ARM_SPEC: Dict[str, Tuple[str, Optional[str]]] = {
    "PROGRESS": ("PROGRESS", None), "RANDOM": ("RANDOM", None), "ERROR": ("ERROR", None), "ORACLE": ("ORACLE", None),
    "NULL": ("NULL", None), "PROGRESS-NET": ("PROGRESS-NET", None), "NULL-NET": ("NULL-NET", None),
    "PROGRESS-UCB": ("PROGRESS-UCB", None),
    "PROGRESS+REPLAY": ("PROGRESS", "room"), "ERROR+REPLAY": ("ERROR", "room"), "RANDOM+REPLAY": ("RANDOM", "room"),
    "ORACLE+REPLAY": ("ORACLE", "room"), "NULL+REPLAY": ("NULL", "room"), "PROGRESS+REPLAY-V": ("PROGRESS", "visit")}
ARMS: Tuple[str, ...] = tuple(ARM_SPEC)
IDENTITY_ARMS: Tuple[str, ...] = ("PROGRESS", "RANDOM", "ERROR", "ORACLE", "NULL")
LEARNER_BAND = {"bare": "RANDOM", "replay": "RANDOM+REPLAY"}
# the arms under the bars (PREREG-S1C2 §5): X → (its learner, O_X, RANDOM_X, NULL_X)
BARRED = {"PROGRESS-NET": ("bare", "ORACLE", "RANDOM", "NULL-NET"),
          "PROGRESS+REPLAY": ("replay", "ORACLE+REPLAY", "RANDOM+REPLAY", "NULL+REPLAY")}
# the identity control compares every field of S1c's record but these five (ruled: masked BY NAME, printed side by side)
VOLATILE: Tuple[str, ...] = ("cpu_s", "wall_s", "code", "prereg", "world")
S1C_RUN_KEYS: Tuple[str, ...] = ("seed", "picker", "rooms", "prefix", "identity_credit", "n_blocks", "record", "table",
                                 "wl_curve", "rates_end", "word_n", "m1_end", "m1_end_value", "cursor", "pi",
                                 "n_empty_windows", "pin_end", "note", "marks")


class S2Error(Exception):
    pass


def check_prereg() -> Dict[str, str]:
    """PREREG-S1C2 (final) beside the laws it extends — PREREG-S1C, AMENDMENT 1, PREREG-S1B1 (run_s1c.check_prereg)."""
    got = dict(S.check_prereg())
    s2 = hashlib.sha256(PREREG_S1C2_PATH.read_bytes()).hexdigest()
    if s2 != PREREG_S1C2_SHA256:
        raise S2Error(f"PREREG-S1C2 sha256 {s2[:12]}… ≠ {PREREG_S1C2_SHA256[:12]}… — STOP and hand back")
    got["prereg_s1c2"] = s2
    return got


def prereg_header() -> Dict[str, str]:
    return {**S.prereg_header(), "prereg_s1c2_sha256": PREREG_S1C2_SHA256}


# ================================================================================================ the pickers and the replay
def make_picker2(arm: str, rooms: Sequence[str], seed: int, gain_fn=None, prefix: str = "", identity_credit: bool = False):
    name, _grain = ARM_SPEC[arm]
    if name == "PROGRESS-NET":
        return PK.NetPicker(rooms, seed)
    if name == "NULL-NET":
        if identity_credit:
            return PK.NullNetPicker(rooms, seed, credit={r: r for r in rooms}, allow_identity=True)
        return PK.NullNetPicker(rooms, seed)
    if name == "PROGRESS-UCB":
        return PK.UCBPicker(rooms, seed, n_round_robin=len(rooms))
    return PK.make_picker(name, rooms, seed, gain_fn=gain_fn, prefix=prefix, identity_credit=identity_credit)


def replay_draws(seed: int, block: int, by_room: Dict[str, List[int]], buffer: Sequence[Tuple[str, int]],
                 rooms: Sequence[str], R_: int, grain: str) -> List[Tuple[str, int]]:
    """R draws WITH replacement from the replay buffer (every visit scene the life has consumed so far), from substream
    `replay:<seed>:<block>`. The room grain (the law): uniform over the rooms visited so far (in the world's room order),
    then uniform over that room's consumed visit scenes — declared: the room drawn first, then the scene, per draw. The
    visit grain (the reading arm): uniform over every consumed scene (in consumption order)."""
    rng = substream(seed, f"replay:{int(seed)}:{int(block)}")
    out: List[Tuple[str, int]] = []
    if grain == "room":
        visited = [r for r in rooms if by_room[r]]
        for _ in range(R_):
            r = visited[int(rng.integers(len(visited)))]
            out.append((r, int(by_room[r][int(rng.integers(len(by_room[r])))])))
    elif grain == "visit":
        for _ in range(R_):
            r, i = buffer[int(rng.integers(len(buffer)))]
            out.append((r, int(i)))
    else:
        raise S2Error(f"no such replay grain: {grain!r}")
    return out


def replay(L, data, draws: Sequence[Tuple[str, int]], seed: int) -> None:
    """Each drawn scene re-trained by the SAME train_scene road, WHOLE (the standardiser observes it again, the delta rule,
    the prototypes, the stores, the meetings); its episodic generator is the scene's own (declared; a replayed scene carries
    no word the learner has not heard, so the episodic write never draws from it)."""
    for r, i in draws:
        X, words = data.visit_scene(r, i)
        L.train_scene(X, words, referent=None, rng=substream(seed, f"episodic:room:{r}:visit:{i}"))


# ================================================================================================ the LIFE
def life2(data, test, arm: str, rooms: Sequence[str] = ROOMS, n_blocks: int = PK.N_BLOCKS, prefix: str = "",
          identity_credit: bool = False, R_: int = R_REPLAY, planted_replay_before_post: bool = False,
          bracket_check: bool = False, log=None) -> Dict[str, object]:
    """One life of one arm. For S1c's five arms (and the bare learner) every computation is run_s1c.life's, in its order —
    the identity control proves it on S1c's own records. `planted_replay_before_post` (THE FIRST GATE 2's planted offender
    only) replays BEFORE step (i); `bracket_check` re-trains a clone of the pre-block learner on the block alone and asks
    that it reproduce POST_b and the drop (the blocks where it does not are returned)."""
    picker_name, grain = ARM_SPEC[arm]
    replay_on = grain is not None and R_ > 0
    cpu0, wall0 = time.process_time(), time.time()
    seed, rooms = data.seed, list(rooms)
    L = S.new_learner()
    cursor = {r: 0 for r in rooms}
    last = {r: 0 for r in rooms}
    buffer: List[Tuple[str, int]] = []
    by_room: Dict[str, List[int]] = {r: [] for r in rooms}
    Lk = {r: PK.window_loss(L, data.window[r]) for r in rooms}
    table = [dict(Lk)]
    table_pre = [dict(Lk)]
    wl_now, _ = test.words_learned(L)
    wl_curve = [wl_now]
    clones: Dict[str, object] = {}
    oracle_log: Dict[str, object] = {}
    bracket_bad: List[int] = []
    replayed = {r: 0 for r in rooms}

    def gain_fn(rs: Sequence[str]) -> Dict[str, Tuple[float, float]]:
        clones.clear()
        m1_now = test.m1_fast(L)
        oracle_log["m1_now"] = m1_now
        out = {}
        for r in rs:
            cl = copy.deepcopy(L)
            S.train_block(cl, data, r, cursor[r], seed)          # the clone trains the next block WITHOUT replay
            wl_c, _ = test.words_learned(cl)
            m1_c = test.m1_fast(cl)
            out[r] = (float(wl_c - wl_now), None if (m1_c is None or m1_now is None) else float(m1_c - m1_now))
            clones[r] = cl
        return out

    picker = make_picker2(arm, rooms, seed, gain_fn=gain_fn, prefix=prefix, identity_credit=identity_credit)
    rec: List[Dict[str, object]] = []
    for block in range(1, n_blocks + 1):
        est = picker.estimates()
        if block <= len(rooms):
            room, flag = rooms[block - 1], "round-robin"
        else:
            room, flag = picker.pick(block, PK.Context(last_visit=dict(last), L_now=dict(Lk)))
        start = cursor[room]
        pre_clone = copy.deepcopy(L) if bracket_check else None
        thetas = S.train_block(L, data, room, start, seed, snapshots=True)
        cursor[room] += PK.BLOCK
        for i in range(start, start + PK.BLOCK):
            buffer.append((room, i))
            by_room[room].append(i)
        drift = PK.drift_reading(thetas)
        same = None
        if picker_name == "ORACLE" and flag == "policy":
            same = S._same_state(clones[room], L)                 # before any replay: the clone saw the block only
            if not same:
                raise S2Error(f"{arm} block {block}: the ORACLE's clone of {room} is not the learner after the same block")
        draws: List[Tuple[str, int]] = []
        if replay_on and planted_replay_before_post:            # THE PLANTED OFFENDER (gate 2 only): replay, then «POST»
            draws = replay_draws(seed, block, by_room, buffer, rooms, R_, grain)
            replay(L, data, draws, seed)
        Lk_new = {r: PK.window_loss(L, data.window[r]) for r in rooms}          # (i) POST_b
        drop = Lk[room] - Lk_new[room]
        if bracket_check:
            S.train_block(pre_clone, data, room, start, seed)
            post2 = {r: PK.window_loss(pre_clone, data.window[r]) for r in rooms}
            if post2 != Lk_new or (Lk[room] - post2[room]) != drop:
                bracket_bad.append(block)
        if replay_on and not planted_replay_before_post:
            draws = replay_draws(seed, block, by_room, buffer, rooms, R_, grain)       # (ii) the REPLAY
            replay(L, data, draws, seed)
            Lk_pre = {r: PK.window_loss(L, data.window[r]) for r in rooms}          # (iii) PRE_{b+1}
        elif replay_on:
            Lk_pre = dict(Lk_new)
        else:
            Lk_pre = Lk_new                                                         # (iii) ≡ (i)
        readings = ({"pre_before": dict(Lk), "pre_after": dict(Lk_pre)} if getattr(picker, "wants_readings", False) else {})
        credited = picker.observe(block, room, drop=drop, drift=drift, **readings)
        wl_now, _ = test.words_learned(L)
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
        if picker_name in ("PROGRESS-NET", "NULL-NET"):
            net = picker.net()
            row.update({"net": net, "neg_rooms": sum(1 for v in net.values() if v is not None and v < 0)})
        if picker_name == "PROGRESS-UCB" and flag == "policy":
            row["ucb"] = {k: v for k, v in picker.last_pick.items()}
        rec.append(row)
        Lk = Lk_pre
        table.append(dict(Lk_new))
        table_pre.append(dict(Lk_pre))
        last[room] = block
        wl_curve.append(wl_now)
        if log is not None and block % 50 == 0:
            log(f"[{arm}{' ' + prefix if prefix else ''} {seed}] block {block}: wl {wl_now} · {room} {flag}")
    ans = test.points(L)
    full = test.m1_full(L, ans)
    fast = test.m1_fast(L, ans)
    if full["graded"]["covered"] != fast:
        raise S2Error(f"M1 fast {fast} ≠ the grader's {full['graded']['covered']}")
    pin = test.pin(L, ans)
    if pin["names_mismatch"] or pin["points_mismatch"]:
        raise S2Error(f"the batched readers differ from name_forced / answer_point at the life's end: {pin}")
    wl_end, rates = test.words_learned(L)
    out = {"seed": seed, "picker": picker_name, "rooms": rooms, "prefix": prefix, "identity_credit": identity_credit,
           "n_blocks": n_blocks, "record": rec, "table": table, "wl_curve": wl_curve, "rates_end": rates,
           "word_n": test.word_n, "m1_end": full["graded"], "m1_end_value": fast, "cursor": cursor,
           "pi": getattr(picker, "pi", None), "cpu_s": time.process_time() - cpu0, "wall_s": time.time() - wall0,
           "n_empty_windows": {r: data.window[r].n_empty for r in rooms}, "prereg": prereg_header(), "pin_end": pin,
           "code": R.code_identity(), "note": S.ORACLE_TRUTH_NOTE if picker_name == "ORACLE" else None,
           "arm": arm, "grain": grain if replay_on else None, "R": R_ if replay_on else 0, "table_pre": table_pre,
           "buffer_len": len(buffer), "replayed": replayed,
           "bracket_check": bracket_bad if bracket_check else None,
           "planted_replay_before_post": bool(planted_replay_before_post)}
    out["marks"] = S.run_marks(out)
    out["marks2"] = marks2(out)
    return out


# ================================================================================================ the marks of the slice
def _table(run: Dict[str, object], after: str) -> Dict[str, Dict[str, Optional[float]]]:
    """By the block's room k, the mean change of every room's L_j: `after` = "block" → POST_b − PRE_b (the block's own
    change), "full" → PRE_{b+1} − PRE_b (the block plus the replay's repair — what PROGRESS sees between visits). For the
    bare learner both equal run_s1c's interference exactly (the same arithmetic, in the same order)."""
    rec, rooms, table, pre = run["record"], list(run["rooms"]), run["table"], run["table_pre"]
    top = table if after == "block" else pre
    out = {}
    for k in rooms:
        bl = [x["block"] for x in rec if x["room"] == k]
        out[k] = {j: (float(np.mean([top[b][j] - pre[b - 1][j] for b in bl])) if bl else None) for j in rooms}
    return out


def _offdiag(t: Dict[str, Dict[str, Optional[float]]]) -> Optional[float]:
    v = [t[k][j] for k in t for j in t[k] if j != k and t[k][j] is not None]
    return float(np.mean(v)) if v else None


def _longest_negative(series: Sequence[Optional[float]]) -> int:
    best = cur = 0
    for v in series:
        cur = cur + 1 if (v is not None and v < 0) else 0
        best = max(best, cur)
    return best


def marks2(run: Dict[str, object]) -> Dict[str, object]:
    """The slice's readings (PREREG-S1C2 §3, with the ruling on the two tables)."""
    rec, rooms = run["record"], list(run["rooms"])
    bt, ft = _table(run, "block"), _table(run, "full")
    r_drops = [x["drop"] for x in rec if x["room"] in ("R1", "R2", "R3")]
    n_drops = [x["drop"] for x in rec if x["room"] == "N"]
    out = {"block_table": bt, "full_table": ft, "offdiag_block": _offdiag(bt), "offdiag_full": _offdiag(ft),
           "n_fraction": (float(np.mean(n_drops)) / float(np.mean(r_drops))) if n_drops and r_drops else None}
    if run.get("grain"):
        tot = sum(run["replayed"].values())
        out["buffer_n_share"] = (run["replayed"]["N"] / tot) if tot else None
        out["replay_effect_mean"] = {r: float(np.mean([x["replay_effect"][r] for x in rec])) for r in rooms}
        out["replayed"] = dict(run["replayed"])
    if run["picker"] in ("PROGRESS-NET", "NULL-NET"):
        negs = [x["neg_rooms"] for x in rec]
        out["neg_rooms_mean"] = float(np.mean(negs))
        out["neg_rooms_max"] = int(max(negs))
        out["longest_negative_run"] = {r: _longest_negative([x["net"][r] for x in rec]) for r in rooms}
    if run["picker"] == "PROGRESS-UCB":
        sh = [x["ucb"]["bonus"][x["room"]] / (abs(x["ucb"]["est"][x["room"]]) + x["ucb"]["bonus"][x["room"]])
              for x in rec if "ucb" in x and (abs(x["ucb"]["est"][x["room"]]) + x["ucb"]["bonus"][x["room"]]) > 0]
        out["bonus_share_mean"] = float(np.mean(sh)) if sh else None      # declared: bonus / (|est| + bonus) at the pick
    return out


# ================================================================================================ the pins
def _norm(x):
    return json.loads(json.dumps(x, sort_keys=True, default=R._jsonable))


def _canon(x) -> str:
    return json.dumps(_norm(x), sort_keys=True)


def identity_diff(new: Dict[str, object], old: Dict[str, object]) -> List[str]:
    """The identity control: every field of S1c's record except the five masked BY NAME must be equal as canonical JSON,
    byte for byte (floats print their shortest round-trip repr, so one ulp differs). Returns the differing field names."""
    diffs = []
    for k in S1C_RUN_KEYS:
        if k in VOLATILE:
            continue
        if (k in new) != (k in old) or (k in new and _canon(new[k]) != _canon(old[k])):
            diffs.append(k)
    return diffs


def masked_side_by_side(new: Dict[str, object], old: Dict[str, object]) -> Dict[str, Tuple[object, object]]:
    """The five masked fields' values side by side (ruled: so a masked field can never hide a real difference)."""
    return {k: (old.get(k), new.get(k)) for k in VOLATILE}


def rows_equal(a: Dict[str, object], b: Dict[str, object]) -> bool:
    return _canon(a["record"]) == _canon(b["record"]) and _canon(a["table"]) == _canon(b["table"])


def net_pin(run: Dict[str, object]) -> List[Tuple[int, str]]:
    """THE FIRST GATE 3 on a NET life (the bare learner): at every boundary b, for every visited room k with last visit v,
    the recorded net_k equals drop_v(k) − Σ_{j=v+1}^{b} (PRE_{j+1}(k) − PRE_j(k)) to 1e-9 — for v = b the bracketed drop
    itself. Returns the (block, room) pairs that miss."""
    rec, pre = run["record"], run["table_pre"]
    lastv: Dict[str, int] = {}
    dropv: Dict[str, float] = {}
    bad = []
    for x in rec:
        b = x["block"]
        lastv[x["room"]], dropv[x["room"]] = b, x["drop"]
        for k, v in lastv.items():
            want = dropv[k] - sum(pre[j][k] - pre[j - 1][k] for j in range(v + 1, b + 1))
            got = x["net"][k]
            if got is None or abs(got - want) > NET_PIN_TOL:
                bad.append((b, k))
    return bad


def ucb_pin(run: Dict[str, object]) -> Dict[str, bool]:
    """THE FIRST GATE 6: after the round-robin every n_k ≥ 1 (the bonus is defined), t ≥ 1 at every policy pick, and c —
    the running mean |drop| — reads > 0 from block 5."""
    rec, n_rr = run["record"], len(run["rooms"])
    seen = {x["room"] for x in rec[:n_rr]}
    ucb = [x for x in rec if "ucb" in x]
    c_ok = all(float(np.mean([abs(y["drop"]) for y in rec[:x["block"] - 1]])) > 0 for x in rec if x["block"] > n_rr)
    return {"visits_ge_1": seen == set(run["rooms"]), "c_positive_from_5": bool(c_ok and all(x["ucb"]["c"] > 0 for x in ucb)),
            "t_ge_1": all(x["ucb"]["t"] >= 1 for x in ucb)}


# ================================================================================================ the verdict of one arm
def _q(v: Sequence[float], q: float) -> float:
    return float(np.percentile(np.asarray(v, dtype=np.float64), q))


def arm_verdict(per_seed: Dict[int, Dict[str, object]]) -> Dict[str, object]:
    """PREREG-S1C2 §5 for one arm X, read on its own learner: per_seed[s] = {"X", "O", "RND", "NUL": marks,
    "band_A": the RANDOM_X band's A values, "band_n"}. The order (ruled): NOT GRADABLE BY NAME (an arm, a life or a band
    life missing) → NOT GRADABLE FOR CHOICE (the positive control misses at any seed) → VOID (NULL_X meets X's A and SHARE_N
    bars at ≥ 2 seeds) → FAIL (any meetable bar misses) → CEILING-BOUND (every miss is a bar above its ceiling: A above the
    band where O_X itself is not above the band's 97.5 % edge) → PASS."""
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
        a_bar = A_VS_ORACLE * O["A"]
        rows = {"A": {"value": X["A"], "bar": a_bar, "state": "PASS" if X["A"] >= a_bar else "FAIL"}}
        if O["A"] <= hi:
            rows["A_band"] = {"value": X["A"], "bar": hi, "state": "CEILING-BOUND", "oracle": O["A"]}
        else:
            rows["A_band"] = {"value": X["A"], "bar": hi, "state": "PASS" if X["A"] > hi else "FAIL", "oracle": O["A"]}
        sb = O["share"]["N"] + SHARE_ALLOWANCE
        rows["SHARE_N"] = {"value": X["share"]["N"], "bar": sb, "state": "PASS" if X["share"]["N"] <= sb else "FAIL"}
        rows["LEAVE_N"] = {"value": X["leave"]["N"], "bar": LEAVE_BAR, "state": "PASS" if X["leave"]["N"] <= LEAVE_BAR else "FAIL"}
        pc = O["A"] - RND["A"]
        pcs.append(pc >= POSITIVE_CONTROL)
        meets = NUL["A"] >= a_bar and NUL["share"]["N"] <= sb
        null_n += int(meets)
        fails += [f"{k}@{s}" for k, v in rows.items() if v["state"] == "FAIL"]
        ceils += [f"{k}@{s}" for k, v in rows.items() if v["state"] == "CEILING-BOUND"]
        out["seeds"][s] = {"bars": rows, "band": [lo, hi], "band_n": d["band_n"], "positive_control": pc,
                           "null_meets": meets}
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


# ================================================================================================ records
def run_path(root: Path, seed: int, arm: str) -> Path:
    return Path(root) / str(seed) / "runs" / f"{arm}.json"


def band_path(root: Path, seed: int, learner: str, k: int) -> Path:
    return Path(root) / str(seed) / "band" / learner / f"random-{k:02d}.json"


def s1c_run_path(seed: int, arm: str) -> Path:
    return S.run_path(S1C_ROOT, seed, "law", arm)


def s1c_band_path(seed: int, k: int) -> Path:
    return S.band_path(S1C_ROOT, seed, "law", k)


def _load(p: Path) -> Optional[Dict[str, object]]:
    return json.loads(p.read_text()) if p.exists() else None


# ================================================================================================ THE FIRST GATE
def record_lines2(run: Dict[str, object]) -> List[str]:
    """S1c's record lines, then the slice's per-block extras (PRE, the replay's draws and effect, NET, UCB)."""
    out = S.record_lines(run)
    out[0] = out[0].replace(f"   {run['picker']}", f"   {run['arm']} ({run['picker']}, grain {run.get('grain')}, R {run.get('R')})", 1)
    for i, x in enumerate(run["record"], start=1):
        extra = []
        if "replay" in x:
            extra.append("replay " + ",".join(f"{q}:{j}" for q, j in x["replay"]) + " · mix " +
                         " ".join(f"{r}:{v}" for r, v in x["replay_mix"].items()) + " · POST−PRE " +
                         " ".join(f"{r}:{v:+.3f}" for r, v in x["replay_effect"].items()))
        if "net" in x:
            extra.append("net " + " ".join(f"{r}:{S._fmt(v)}" for r, v in x["net"].items()) + f" · negative {x['neg_rooms']}")
        if "ucb" in x:
            u = x["ucb"]
            extra.append(f"ucb t {u['t']} c {u['c']:.3f} · bonus " + " ".join(f"{r}:{v:.3f}" for r, v in u["bonus"].items()))
        if extra:
            out[i] = out[i] + " · " + " · ".join(extra)
    return out


def first_gate2(root: Path = ROOT, log=print) -> Dict[str, object]:
    """PREREG-S1C2 §4 on seed 20261301, printed whole. Steps 1–4, 6 stop on a miss; step 5 MARKS the replay world NOT
    GRADABLE FOR CHOICE and the gate goes on (ruled, as its text says); step 7 is the smoke, read whole."""
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
    say(f"THE FIRST GATE (S1c-2, seed {GATE_SEED}, THE LAW'S WORLD {list(ROOMS)}) — PREREG-S1C2 {shas['prereg_s1c2'][:12]}… · "
        f"PREREG-S1C {shas['prereg_s1c'][:12]}… · AMENDMENT 1 {shas['amend1_s1c'][:12]}… · PREREG-S1B1 {shas['prereg_s1b1'][:12]}… · "
        f"code {R.code_identity()['code_sha_file']}")
    data = S.RoomData(S1C_ROOT, GATE_SEED, ROOMS)
    test = S.FixedTestSet()
    gdir = Path(root) / "gate"
    # 1. identity
    idr = {a: life2(data, test, a, log=log) for a in IDENTITY_ARMS}
    diffs, side = {}, {}
    for a, r in idr.items():
        R.dump(gdir / "step1" / f"{a}.json", r)
        old = _load(s1c_run_path(GATE_SEED, a))
        diffs[a] = ["record missing"] if old is None else identity_diff(r, old)
        side[a] = None if old is None else {k: (str(v[0])[:60], str(v[1])[:60]) for k, v in masked_side_by_side(r, old).items()}
    out["step1"] = {"diffs": diffs, "masked": side}
    say(f"1. identity — S1c's five arms re-run on this tree against S1c's records ({s1c_run_path(GATE_SEED, 'PROGRESS').parent}), "
        f"every field but the five masked BY NAME {list(VOLATILE)}: " + " · ".join(
            f"{a} {'EQUAL' if not d else 'DIFFERS in ' + str(d)}" for a, d in diffs.items())
        + f" · the caches: S1c's pools, accepted by cache.check_code and the room code's sha "
          f"({sum(len(data.visit[r].p) + data.window[r].n for r in ROOMS)} canvases)")
    for a in IDENTITY_ARMS:
        if side[a]:
            say(f"   the masked fields of {a} (S1c | this tree): " + " · ".join(f"{k}: {v[0]} | {v[1]}" for k, v in side[a].items()))
    if any(diffs.values()):
        return stop("step 1 (another tree, not another result)")
    # 2. the bracket is the room's
    r0 = life2(data, test, "PROGRESS+REPLAY", R_=0)
    r10 = life2(data, test, "PROGRESS+REPLAY", bracket_check=True, log=log)
    planted = life2(data, test, "PROGRESS+REPLAY", n_blocks=SMOKE_BLOCKS, bracket_check=True, planted_replay_before_post=True)
    R.dump(gdir / "step2" / "PROGRESS+REPLAY-R0.json", r0)
    R.dump(gdir / "step2" / "PROGRESS+REPLAY-R10.json", r10)
    R.dump(gdir / "step2" / "PROGRESS+REPLAY-planted.json", planted)
    d0 = identity_diff(r0, idr["PROGRESS"])
    s2 = {"r0_vs_progress": d0, "r10_bracket_misses": r10["bracket_check"], "planted_caught_at": planted["bracket_check"],
          "replay_effect_mean": r10["marks2"]["replay_effect_mean"]}
    s2["pass"] = (not d0) and r10["bracket_check"] == [] and len(planted["bracket_check"]) > 0
    out["step2"] = s2
    say(f"2. the bracket is the room's — PROGRESS+REPLAY at R = 0 vs PROGRESS: {'EQUAL' if not d0 else 'DIFFERS in ' + str(d0)} · "
        f"at R = 10, a clone of the pre-block learner trained on the block alone reproduces POST_b and the drop at every one of "
        f"{len(r10['record'])} blocks: misses {r10['bracket_check'] or 'none'} · the planted replay BEFORE POST caught at blocks "
        f"{planted['bracket_check']} · the replay's own change, POST_b − PRE_(b+1) (mean per room): "
        + " ".join(f"{r} {v:+.4f}" for r, v in r10["marks2"]["replay_effect_mean"].items())
        + f" → {'PASS' if s2['pass'] else 'MISS'}")
    if not s2["pass"]:
        return stop("step 2")
    # 3. NET is what it says
    net = life2(data, test, "PROGRESS-NET", log=log)
    R.dump(gdir / "step3" / "PROGRESS-NET.json", net)
    bad = net_pin(net)
    consec = sum(1 for i in range(1, len(net["record"])) if net["record"][i]["room"] == net["record"][i - 1]["room"])
    out["step3"] = {"misses": bad[:20], "n_misses": len(bad), "consecutive_visits": consec, "pass": not bad}
    say(f"3. NET is what it says — at every boundary of a 200-block PROGRESS-NET life, for every visited room: net = the "
        f"bracketed drop minus the room's intervening PRE changes (the bracketed drop itself on a consecutive visit; "
        f"{consec} consecutive visits in the life), to {NET_PIN_TOL:g}: misses {len(bad)}{' ' + str(bad[:5]) if bad else ''} → "
        f"{'PASS' if not bad else 'MISS'}")
    if bad:
        return stop("step 3")
    # 4. the null is a null
    pi = PK.null_derangement(GATE_SEED, ROOMS)
    src = next(k for k, v in pi.items() if v == ROOMS[0])
    planted_one = dict(pi)
    planted_one[ROOMS[0]], planted_one[src] = ROOMS[0], pi[ROOMS[0]]
    i_net = life2(data, test, "NULL-NET", identity_credit=True)
    pr = life2(data, test, "PROGRESS+REPLAY")
    i_rep = life2(data, test, "NULL+REPLAY", identity_credit=True)
    smoke = {a: life2(data, test, a, n_blocks=SMOKE_BLOCKS) for a in ARMS}
    for a, r in smoke.items():
        R.dump(gdir / "smoke" / f"{a}.json", r)
    home = {a: [x["block"] for x in smoke[a]["record"] if x["credited"] == x["room"]] for a in ("NULL", "NULL-NET", "NULL+REPLAY")}
    expl = {a: PK.exploration_mismatches(smoke[a]["record"], GATE_SEED, ROOMS) for a in ARMS
            if ARM_SPEC[a][0] in ("ERROR", "PROGRESS", "NULL", "PROGRESS-NET", "NULL-NET", "PROGRESS-UCB")}
    flip = [dict(x) for x in smoke["PROGRESS-NET"]["record"]]
    kp = next((i for i, x in enumerate(flip) if x["flag"] == "policy"), None)
    caught = False
    if kp is not None:
        flip[kp]["flag"] = "explore"
        caught = PK.exploration_mismatches(flip, GATE_SEED, ROOMS) == [flip[kp]["block"]]
    s4 = {"pi": pi, "is_derangement": PK.is_derangement(pi), "identity_caught": not PK.is_derangement({r: r for r in ROOMS}),
          "fixed_point_caught": not PK.is_derangement(planted_one), "null_pi_is_pi": all(smoke[a]["pi"] == pi for a in home),
          "net_identity_is_net": rows_equal(i_net, net), "replay_identity_is_replay": rows_equal(i_rep, pr),
          "credit_lands_home": home, "exploration_mismatches": expl, "planted_flip_caught": caught}
    s4["pass"] = bool(s4["is_derangement"] and s4["identity_caught"] and s4["fixed_point_caught"] and s4["null_pi_is_pi"]
                      and s4["net_identity_is_net"] and s4["replay_identity_is_replay"] and not any(home.values())
                      and not any(expl.values()) and caught)
    out["step4"] = s4
    say(f"4. the null is a null — π = {pi} (a derangement from null:seed: {s4['is_derangement']}; the planted identity caught: "
        f"{s4['identity_caught']}; a planted fixed point caught: {s4['fixed_point_caught']}; the three nulls carry it: "
        f"{s4['null_pi_is_pi']}) · the identity credit IS its estimate's picker over 200 blocks — NULL-NET ≡ PROGRESS-NET: "
        f"{s4['net_identity_is_net']} · NULL+REPLAY ≡ PROGRESS+REPLAY: {s4['replay_identity_is_replay']} · a null's credit lands "
        f"on its producer at {({a: v or 'none' for a, v in home.items()})} · the ε flags agree with the stream in every ε arm's "
        f"smoke: {not any(expl.values())} (a planted flipped flag caught: {caught}) → {'PASS' if s4['pass'] else 'MISS'}")
    if not s4["pass"]:
        return stop("step 4")
    # 5. the replay learner offers a choice (MARKS, never stops)
    orp = life2(data, test, "ORACLE+REPLAY", log=log)
    rrp = life2(data, test, "RANDOM+REPLAY", log=log)
    R.dump(gdir / "step5" / "ORACLE+REPLAY.json", orp)
    R.dump(gdir / "step5" / "RANDOM+REPLAY.json", rrp)
    diff = orp["marks"]["A"] - rrp["marks"]["A"]
    out["step5"] = {"A_oracle_replay": orp["marks"]["A"], "A_random_replay": rrp["marks"]["A"], "diff": diff,
                    "pass": diff >= POSITIVE_CONTROL, "clone_identical": all(x.get("clone_identical", True) for x in orp["record"])}
    out["replay_world_gradable_for_choice"] = diff >= POSITIVE_CONTROL
    say(f"5. the replay learner offers a choice — A(ORACLE+REPLAY) {orp['marks']['A']:.3f} − A(RANDOM+REPLAY) "
        f"{rrp['marks']['A']:.3f} = {diff:+.3f} ≥ 0.05 → {'PASS' if diff >= POSITIVE_CONTROL else 'MISS: the replay world reads NOT GRADABLE FOR CHOICE (the gate goes on)'} "
        f"(the ORACLE+REPLAY's clone equalled the learner after every policy block, before its replay: "
        f"{out['step5']['clone_identical']}; CPU {orp['cpu_s']:.1f} s / {rrp['cpu_s']:.1f} s)")
    # 6. UCB's pin
    ucb = life2(data, test, "PROGRESS-UCB", log=log)
    R.dump(gdir / "step6" / "PROGRESS-UCB.json", ucb)
    up = ucb_pin(ucb)
    out["step6"] = {**up, "pass": all(up.values())}
    say(f"6. UCB's pin — after the round-robin every n_k ≥ 1: {up['visits_ge_1']} · t ≥ 1 at every policy pick: {up['t_ge_1']} · "
        f"c (the running mean |drop|) > 0 from block 5: {up['c_positive_from_5']} → {'PASS' if all(up.values()) else 'MISS'}")
    if not all(up.values()):
        return stop("step 6")
    # 7. the smoke, every record read whole
    say(f"7. the {SMOKE_BLOCKS}-block smoke of every arm, each record whole:")
    for a in ARMS:
        for ln in record_lines2(smoke[a]):
            say(ln)
    out["step7"] = {a: {"rooms": [x["room"] for x in smoke[a]["record"]], "flags": [x["flag"] for x in smoke[a]["record"]]}
                    for a in ARMS}
    out["verdict"] = "PROCEED"
    say(f"THE FIRST GATE: PROCEED{'' if out['replay_world_gradable_for_choice'] else ' (the replay world NOT GRADABLE FOR CHOICE — marked, per step 5)'}")
    out["lines"] = lines
    return out


def gate_ok(root: Path = ROOT) -> Dict[str, object]:
    p = Path(root) / "gate" / "first_gate.json"
    if not p.exists():
        raise S2Error(f"{p} is missing — THE FIRST GATE has not run")
    g = json.loads(p.read_text())
    if g.get("verdict") != "PROCEED":
        raise S2Error(f"THE FIRST GATE reads {g.get('verdict')} — no life")
    return g


# ================================================================================================ the price
def price(root: Path = ROOT, log=print) -> Dict[str, object]:
    """Solo at seed 20261301, one life of each cost class; the projection for the unit: 14 arms × 3 seeds + 120 band lives
    (the pools are S1c's, reused)."""
    check_prereg()
    gate_ok(root)
    data = S.RoomData(S1C_ROOT, GATE_SEED, ROOMS)
    test = S.FixedTestSet()
    cpu = {}
    for a in ("RANDOM", "PROGRESS-NET", "PROGRESS-UCB", "ORACLE", "PROGRESS+REPLAY", "RANDOM+REPLAY", "ORACLE+REPLAY"):
        r = life2(data, test, a)
        cpu[a] = r["cpu_s"]
        log(f"[price] {a}: {r['cpu_s']:.1f} CPU-s ({r['wall_s']:.1f} s wall)")
    plain_bare = cpu["RANDOM"]
    lives = 3 * (4 * plain_bare + cpu["PROGRESS-NET"] * 2 + cpu["PROGRESS-UCB"] + cpu["ORACLE"]
                 + 4 * cpu["PROGRESS+REPLAY"] + cpu["RANDOM+REPLAY"] + cpu["ORACLE+REPLAY"])
    bands = 3 * len(BAND_K) * (cpu["RANDOM"] + cpu["RANDOM+REPLAY"])
    total = lives + bands
    out = {"cpu_s": cpu, "lives_cpu_s": lives, "bands_cpu_s": bands, "unit_cpu_min": total / 60.0}
    log(f"[price] THE UNIT: 42 lives {lives / 60:.1f} CPU-min + 120 band lives {bands / 60:.1f} (the pools are S1c's) = "
        f"{total / 60:.1f} CPU-min (PREREG-S1C2 §8 expected ≈ 11 for the lives)")
    R.dump(Path(root) / "price" / "price.json", out)
    return out


# ================================================================================================ the report
def load_all(root: Path = ROOT):
    runs = {s: {a: _load(run_path(root, s, a)) for a in ARMS} for s in S.RM.S1C_SEEDS}
    bands = {s: {ln: [x for x in (_load(band_path(root, s, ln, k)) for k in BAND_K) if x is not None]
                 for ln in LEARNER_BAND} for s in S.RM.S1C_SEEDS}
    return runs, bands


def identity_at_the_run(runs, bands) -> Dict[str, object]:
    """S1c's five arms and its 20 band lives, re-run at every seed, against S1c's own records."""
    out, side = {}, {}
    for s in S.RM.S1C_SEEDS:
        for a in IDENTITY_ARMS:
            old, new = _load(s1c_run_path(s, a)), runs[s][a]
            key = f"{a}@{s}"
            out[key] = ["missing"] if (old is None or new is None) else identity_diff(new, old)
            if old is not None and new is not None and s == S.RM.S1C_SEEDS[0]:
                side[a] = {k: (str(v[0])[:50], str(v[1])[:50]) for k, v in masked_side_by_side(new, old).items()}
        got = {int(x["prefix"].split(":")[2]): x for x in bands[s]["bare"]}
        for k in BAND_K:
            old = _load(s1c_band_path(s, k))
            key = f"band{k:02d}@{s}"
            out[key] = ["missing"] if (old is None or k not in got) else identity_diff(got[k], old)
    return {"diffs": {k: v for k, v in out.items() if v}, "n_compared": len(out), "masked": side}


def report(root: Path = ROOT, log=print) -> Dict[str, object]:
    shas = check_prereg()
    g = gate_ok(root)
    runs, bands = load_all(root)
    seeds = list(S.RM.S1C_SEEDS)
    L: List[str] = []
    idc = identity_at_the_run(runs, bands)
    L.append(f"S1c-2 «netted progress and rehearsal» — the report · PREREG-S1C2 {shas['prereg_s1c2'][:12]}… (with PREREG-S1C "
             f"{shas['prereg_s1c'][:12]}… and AMENDMENT 1 {shas['amend1_s1c'][:12]}…) · THE LAW'S WORLD {list(ROOMS)} · 200 blocks "
             f"× 10 scenes · 196 policy blocks · R = {R_REPLAY}")
    L.append("")
    L.append(f"THE IDENTITY CONTROL (S1c's five arms and its 20 band lives re-run at every seed against S1c's records; every field "
             f"but {list(VOLATILE)}): {idc['n_compared'] - len(idc['diffs'])} of {idc['n_compared']} EQUAL"
             + (f" · DIFFERENT: {idc['diffs']}" if idc["diffs"] else ""))
    for a, v in idc["masked"].items():
        L.append(f"   the masked fields of {a}@{seeds[0]} (S1c | this tree): " + " · ".join(f"{k}: {x[0]} | {x[1]}" for k, x in v.items()))
    identity_ok = not idc["diffs"]
    L.append("")

    def marks_of(s, a):
        r = runs[s][a]
        return None if r is None else r["marks"]

    per_arm = {}
    for X, (learner, O, RND, NUL) in BARRED.items():
        ps = {}
        for s in seeds:
            bl = bands[s][learner]
            ps[s] = {"X": marks_of(s, X), "O": marks_of(s, O), "RND": marks_of(s, RND), "NUL": marks_of(s, NUL),
                     "band_A": [x["marks"]["A"] for x in bl], "band_n": len(bl)}
        v = arm_verdict(ps)
        if not identity_ok:
            v["verdict_before_identity"] = v["verdict"]
            v["verdict"] = "NOT GRADABLE (IDENTITY)"
        if learner == "replay" and not g.get("replay_world_gradable_for_choice", True) and v["verdict"] == "PASS":
            v["note"] = "the gate's step 5 marked the replay world NOT GRADABLE FOR CHOICE at seed 20261301"
        per_arm[X] = v
        L.append(f"{X} on the {learner} learner (O = {O}, RANDOM = {RND} with its 20-life band, NULL = {NUL}): VERDICT {v['verdict']}"
                 + (f" · missing {v['missing']}" if v.get("missing") else ""))
        for s, d in v.get("seeds", {}).items():
            b = d["bars"]
            L.append(f"   {s}: A {b['A']['value']:.3f} vs 0.80 × O {b['A']['bar']:.3f} {b['A']['state']} · A above the band "
                     f"[{d['band'][0]:.3f}, {d['band'][1]:.3f}] (n {d['band_n']}; O {b['A_band']['oracle']:.3f}) {b['A_band']['state']} · "
                     f"SHARE_N {b['SHARE_N']['value']:.3f} vs {b['SHARE_N']['bar']:.3f} {b['SHARE_N']['state']} · LEAVE_N "
                     f"{b['LEAVE_N']['value']} vs {LEAVE_BAR} {b['LEAVE_N']['state']} · the positive control {d['positive_control']:+.3f} "
                     f"{'PASS' if d['positive_control'] >= POSITIVE_CONTROL else 'MISS'} · NULL meets X's bars: {d['null_meets']}")
    L.append("")
    L.append("per seed, every arm (A · S12 · SHARE [R1 R2 R3 N] · explore apart · LEAVE_N · lock-in · M1 · wl@200 · N's drop / the "
             "learnable rooms' · the FULL-STEP and BLOCK off-diagonal · the buffer's N-share):")
    for s in seeds:
        L.append(f" seed {s}:")
        for a in ARMS:
            r = runs[s][a]
            if r is None:
                L.append(f"   {a:<18} NOT GRADABLE BY NAME (the life is missing)")
                continue
            m, m2 = r["marks"], r["marks2"]
            L.append(f"   {a:<18} A {m['A']:.3f} · S12 {m['S12'] if m['S12'] is not None else '∞'} · SHARE ["
                     + " ".join(f"{m['share'][q]:.3f}" for q in ROOMS) + "] · explore [" + " ".join(f"{m['explore'][q]:.3f}" for q in ROOMS)
                     + f"] · LEAVE_N {m['leave']['N']} · lock-in {m['longest_run']} ({m['longest_run_room']}) · M1 {S._fmt(m['M1'])} · "
                     f"wl@200 {m['wl_end']} · N/R drop {S._fmt(m2['n_fraction'])} · off-diag FULL {S._fmt(m2['offdiag_full'], 4)} "
                     f"BLOCK {S._fmt(m2['offdiag_block'], 4)}" + (f" · buffer N {m2['buffer_n_share']:.3f}" if 'buffer_n_share' in m2 else "")
                     + f" · CPU {r['cpu_s']:.1f} s")
    L.append("")
    L.append("the readings (no bar):")
    for s in seeds:
        def band_line(learner, key, x):
            v = [b["marks"][key] if key == "A" else b["marks"]["share"]["N"] for b in bands[s][learner]]
            if len(v) < len(BAND_K):
                return f"NOT GRADABLE BY NAME (band n {len(v)})"
            lo, hi = _q(v, 2.5), _q(v, 97.5)
            return f"{x:.3f} vs [{lo:.3f}, {hi:.3f}] (n {len(v)}) {'BELOW' if x < lo else 'ABOVE' if x > hi else 'inside'}"
        er, rr, pr_, prog = runs[s]["ERROR+REPLAY"], runs[s]["RANDOM+REPLAY"], runs[s]["PROGRESS+REPLAY"], runs[s]["PROGRESS"]
        L.append(f"   {s}: ERROR+REPLAY's SHARE_N " + (band_line("replay", "SHARE_N", er["marks"]["share"]["N"]) if er else "missing")
                 + " · the replay's own gain, A(RANDOM+REPLAY) vs the bare RANDOM band " + (band_line("bare", "A", rr["marks"]["A"]) if rr else "missing"))
        if pr_ and prog:
            L.append(f"      the FORGETTING reading (ruled: the FULL-STEP table's 12 off-diagonal entries, PRE_(b+1) − PRE_b): "
                     f"PROGRESS+REPLAY {pr_['marks2']['offdiag_full']:+.4f} vs PROGRESS-S1C {prog['marks2']['offdiag_full']:+.4f} · the "
                     f"BLOCK table's (the interference before the repair): {pr_['marks2']['offdiag_block']:+.4f} vs "
                     f"{prog['marks2']['offdiag_block']:+.4f} · the replay's own change per room (POST_b − PRE_(b+1), mean): "
                     + " ".join(f"{q} {v:+.4f}" for q, v in pr_["marks2"]["replay_effect_mean"].items()))
        for a in ("PROGRESS+REPLAY", "PROGRESS+REPLAY-V", "ERROR+REPLAY", "RANDOM+REPLAY", "ORACLE+REPLAY", "NULL+REPLAY"):
            r = runs[s][a]
            if r is not None:
                L.append(f"      {a}: the buffer's N-share {r['marks2']['buffer_n_share']:.3f} · replayed per room {r['marks2']['replayed']}")
        for a in ("PROGRESS-NET", "NULL-NET"):
            r = runs[s][a]
            if r is not None:
                m2 = r["marks2"]
                L.append(f"      {a}: negative-net rooms per boundary mean {m2['neg_rooms_mean']:.2f}, max {m2['neg_rooms_max']} · the "
                         f"longest negative run per room {m2['longest_negative_run']}")
        u = runs[s]["PROGRESS-UCB"]
        if u is not None:
            L.append(f"      PROGRESS-UCB: A {u['marks']['A']:.3f} · SHARE_N {u['marks']['share']['N']:.3f} · LEAVE_N {u['marks']['leave']['N']} · "
                     f"lock-in {u['marks']['longest_run']} · the bonus's share of the score at the pick (declared: bonus / (|est| + bonus)) "
                     f"{S._fmt(u['marks2']['bonus_share_mean'])}")
        for a in ARMS:
            r = runs[s][a]
            if r is not None and ARM_SPEC[a][1] is None and r["marks2"]["block_table"] != r["marks2"]["full_table"]:
                L.append(f"      PIN MISS: {a}'s BLOCK and FULL-STEP tables differ on the bare learner")
    L.append("")
    L.append("the 4 × 4 tables (the mean change of each room's L_j during a block in k), per seed — PROGRESS-S1C (bare; BLOCK = "
             "FULL-STEP) and PROGRESS+REPLAY (BLOCK | FULL-STEP):")
    for s in seeds:
        p, q = runs[s]["PROGRESS"], runs[s]["PROGRESS+REPLAY"]
        if p is None or q is None:
            continue
        for k in ROOMS:
            L.append(f"   {s} block in {k:<2}: PROGRESS " + " ".join(f"{j} {S._fmt(p['marks2']['full_table'][k][j], 4)}" for j in ROOMS)
                     + " | +REPLAY BLOCK " + " ".join(f"{j} {S._fmt(q['marks2']['block_table'][k][j], 4)}" for j in ROOMS)
                     + " | FULL " + " ".join(f"{j} {S._fmt(q['marks2']['full_table'][k][j], 4)}" for j in ROOMS))
    L.append("")
    # the refutations
    ref = refutations2(runs, bands)
    L.append("the refutations (§6; decided at block 200 — one «holds» where it holds at all 3 seeds, declared as in S1c):")
    names = {"a": "(a) SHARE_N(NET) inside or above RANDOM's band", "b": "(b) SHARE_N(NET) passes its bar but A(NET) below RANDOM's band",
             "c": "(c) PROGRESS+REPLAY's FULL-STEP off-diagonal not below PROGRESS-S1C's",
             "d": "(d) A(PROGRESS+REPLAY) inside RANDOM+REPLAY's band while the positive control holds",
             "e": "(e) ERROR+REPLAY's SHARE_N below RANDOM+REPLAY's band"}
    for k, nm in names.items():
        v = ref[k]
        L.append(f"   {nm}: " + " · ".join(f"{s} {'holds' if v[s] else 'does not hold' if v[s] is not None else 'NOT GRADABLE'}" for s in seeds)
                 + f" → {'REFUTED' if all(v[s] for s in seeds) else 'not refuted'}")
    L.append("the predictions (§6, from the mechanism; tags as written):")
    for s in seeds:
        n, pr_, er = runs[s]["PROGRESS-NET"], runs[s]["PROGRESS+REPLAY"], runs[s]["ERROR+REPLAY"]
        prog = runs[s]["PROGRESS"]
        if None in (n, pr_, er, prog):
            continue
        L.append(f"   {s}: (N) SHARE_N(NET) {n['marks']['share']['N']:.3f}, LEAVE_N(NET) {n['marks']['leave']['N']} [Guessing] · (R) the "
                 f"FULL-STEP off-diagonal {pr_['marks2']['offdiag_full']:+.4f} < PROGRESS-S1C's {prog['marks2']['offdiag_full']:+.4f} "
                 f"[Likely]: {pr_['marks2']['offdiag_full'] < prog['marks2']['offdiag_full']} · LEAVE_N(+REPLAY) {pr_['marks']['leave']['N']} "
                 f"≤ 50 [Likely] · ERROR+REPLAY's SHARE_N {er['marks']['share']['N']:.3f} (stays trapped [Likely])")
    L.append("")
    L.append("per-word n on the fixed test set: " + " ".join(f"{w} {n}" for w, n in (runs[seeds[0]]["PROGRESS"] or {}).get("word_n", {}).items()))
    txt = "\n".join(L)
    (Path(root) / "report.txt").write_text(txt + "\n")
    R.dump(Path(root) / "report.json", {"identity": idc, "verdicts": per_arm, "refutations": ref, "shas": shas,
                                        "marks": {s: {a: (runs[s][a]["marks"] if runs[s][a] else None) for a in ARMS} for s in seeds},
                                        "marks2": {s: {a: (runs[s][a]["marks2"] if runs[s][a] else None) for a in ARMS} for s in seeds}})
    for ln in L:
        log(ln)
    return {"identity": idc, "verdicts": per_arm, "refutations": ref}


def refutations2(runs, bands) -> Dict[str, Dict[int, Optional[bool]]]:
    out = {k: {} for k in "abcde"}
    for s in S.RM.S1C_SEEDS:
        def band(learner, key):
            v = [b["marks"]["A"] if key == "A" else b["marks"]["share"]["N"] for b in bands[s][learner]]
            return (_q(v, 2.5), _q(v, 97.5)) if len(v) == len(BAND_K) else None
        n, o, pr_, prog, er = (runs[s][a] for a in ("PROGRESS-NET", "ORACLE", "PROGRESS+REPLAY", "PROGRESS", "ERROR+REPLAY"))
        orp, rrp = runs[s]["ORACLE+REPLAY"], runs[s]["RANDOM+REPLAY"]
        bs, ba, rs_, ra = band("bare", "SHARE_N"), band("bare", "A"), band("replay", "SHARE_N"), band("replay", "A")
        out["a"][s] = None if (n is None or bs is None) else n["marks"]["share"]["N"] >= bs[0]
        out["b"][s] = None if (n is None or o is None or ba is None) else (
            n["marks"]["share"]["N"] <= o["marks"]["share"]["N"] + SHARE_ALLOWANCE and n["marks"]["A"] < ba[0])
        out["c"][s] = None if (pr_ is None or prog is None) else pr_["marks2"]["offdiag_full"] >= prog["marks2"]["offdiag_full"]
        out["d"][s] = None if (pr_ is None or ra is None or orp is None or rrp is None) else (
            ra[0] <= pr_["marks"]["A"] <= ra[1] and orp["marks"]["A"] - rrp["marks"]["A"] >= POSITIVE_CONTROL)
        out["e"][s] = None if (er is None or rs_ is None) else er["marks"]["share"]["N"] < rs_[0]
    return out


# ================================================================================================ the CLI
def _ks(spec: str) -> List[int]:
    a, _, b = spec.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="brain.scene.run_s1c2")
    ap.add_argument("cmd", choices=["check", "first-gate", "run", "band", "price", "report"])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--seed", type=int)
    ap.add_argument("--arm", choices=list(ARMS))
    ap.add_argument("--learner", choices=sorted(LEARNER_BAND), default="bare")
    ap.add_argument("--k", default="1-20")
    a = ap.parse_args(argv)
    root = Path(a.root)
    log = R.Log(root / "logs" / f"{a.cmd}.log")
    if a.cmd == "check":
        log(json.dumps(check_prereg()))
        return 0
    check_prereg()
    if a.cmd == "first-gate":
        g = first_gate2(root, log=log)
        R.dump(root / "gate" / "first_gate.json", g)
        (root / "gate" / "first_gate.out").write_text("\n".join(g.get("lines", [])) + "\n")
        return 0 if g["verdict"] == "PROCEED" else 10
    if a.cmd in ("run", "band"):
        gate_ok(root)
        data = S.RoomData(S1C_ROOT, a.seed, ROOMS)
        test = S.FixedTestSet()
        if a.cmd == "run":
            r = life2(data, test, a.arm, log=log)
            R.dump(run_path(root, a.seed, a.arm), r)
            log(f"[run {a.arm} {a.seed}] A {r['marks']['A']:.3f} · SHARE_N {r['marks']['share']['N']:.3f} · LEAVE_N "
                f"{r['marks']['leave']['N']} · M1 {S._fmt(r['marks']['M1'])} · {r['cpu_s']:.1f} CPU-s")
            return 0
        arm = LEARNER_BAND[a.learner]
        for k in _ks(a.k):
            r = life2(data, test, arm, prefix=PK.band_prefix(a.seed, k))
            R.dump(band_path(root, a.seed, a.learner, k), r)
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
