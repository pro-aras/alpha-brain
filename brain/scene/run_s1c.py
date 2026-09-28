"""run_s1c.py — S1c «THE NOISY ROOM»'s runner: the room caches, the fixed test set, the LIFE (200 blocks of 10 scenes,
a room chosen per block), the record, the marks, THE FIRST GATE, the price, the report. Runs under /usr/bin/python3.

edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:12 +0400 — new module, written to docs/brain/r3/PREREG-S1C.md (genome-wt-brain3 9ef2583,
sha a552515a…) and its AMENDMENT 1 (PREREG-S1C-AMEND-1.md, 1eba85d, sha 825f4ad8…); the learner is S1b-1's A-RW, unchanged
(PREREG-S1B1.md, sha caace482…), at lr 0.01. Every constant is the PREREG's; the one-line READINGS it leaves open are
marked «declared» and listed in docs/brain/r3/S1C-HANDBACK.md.

  python3 -m brain.scene.run_s1c check                         the three shas
  python3 -m brain.scene.run_s1c cache-rooms --seed S          every pool of one S1c seed (each written once)
  python3 -m brain.scene.run_s1c first-gate                    THE FIRST GATE (seed 20261301), steps 1–5
  python3 -m brain.scene.run_s1c run --picker P --seed S       one life; the record under <root>/<seed>/runs/<P>.json
  python3 -m brain.scene.run_s1c band --seed S --k A-B         RANDOM's band runs k = A..B (AMENDMENT 1 §3 (b))
  python3 -m brain.scene.run_s1c price                         solo: one life of each picker kind at seed 20261301
  python3 -m brain.scene.run_s1c report                        the marks, the bars, the verdict, the readings

THE TRUTH: only this module and marks.py read it. The fixed test set's truth (S1b-1's caches of S1's three test seeds)
is read HERE for WORDS-LEARNED and M1 — the grader's road — and the ORACLE's clones are graded on that road and handed
to the picker as a CALLBACK of gains; no picker module reads a test set, a room's spec or a truth row.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import sys
import time
import unittest
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.world.seeds import substream

from . import PREREG_S1B1_SHA256
from . import cache as C
from . import learners as Lr
from . import marks as M
from . import pickers as PK
from . import rooms as RM
from . import run as R
from . import world as W

# ------------------------------------------------------------------------------------------------ the PREREG's numbers
PREREG_S1C_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-S1C.md")
AMEND1_S1C_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-S1C-AMEND-1.md")
PREREG_S1C_SHA256 = "a552515af334424b474cca7c96b72d87076d8c0d1a539208e6a5538ce4e7e25c"
AMEND1_S1C_SHA256 = "825f4ad8086f45ac16fef3651370cd46a00c15e921a2518a4bb834bb741eb0dd"
ROOT = Path("/data/dev/brain-runs/scene-s1c")
TEST_ROOT = C.RUNS                                    # S1b-1's root: the fixed test set's caches, questions and keys
GATE_SEED = 20261301
BAND_K: Tuple[int, ...] = tuple(range(1, 21))          # AMENDMENT 1 §3 (b): 20 extra RANDOM runs per seed
LEARNED_AT = 0.80                                     # WORDS-LEARNED: forced naming ≥ 0.80
UNDERPOWERED_WORD_N = 20
BAR_A_VS_ORACLE = 0.80
BAR_SHARE_ALLOWANCE = 0.05
BAR_LEAVE_N = 50
BAR_POSITIVE_CONTROL = 0.05
GATE2_BLOCKS, GATE2_AFTER, GATE2_LAST = 60, 20, 20
GATE2_FLAT, GATE2_R_OVER_N, GATE2_U_OVER_R = 0.05, 3.0, 2.0
SMOKE_BLOCKS = 20
VOCAB: Tuple[str, ...] = RM.VOCAB13
TYPE_WORDS: Dict[str, List[str]] = {"shape": list(W.SHAPES), "colour": list(W.COLOUR_NAMES), "size": list(W.SIZE_NAMES)}
ORACLE_TRUTH_NOTE = ("the ORACLE's clones read the fixed test set's truth through the grader's road only (run_s1c.FixedTestSet "
                     "→ marks.py); the picker receives the gains as a callback and reads no test set")


class S1cError(Exception):
    pass


def check_prereg() -> Dict[str, str]:
    """The law and its amendment (and the learner's law, S1b-1's) — checked before the gate and inside the unit."""
    got = {"prereg_s1c": hashlib.sha256(PREREG_S1C_PATH.read_bytes()).hexdigest(),
           "amend1_s1c": hashlib.sha256(AMEND1_S1C_PATH.read_bytes()).hexdigest(),
           "prereg_s1b1": hashlib.sha256(R.PREREG_S1B1_PATH.read_bytes()).hexdigest()}
    want = {"prereg_s1c": PREREG_S1C_SHA256, "amend1_s1c": AMEND1_S1C_SHA256, "prereg_s1b1": PREREG_S1B1_SHA256}
    bad = [k for k in want if got[k] != want[k]]
    if bad:
        raise S1cError(f"sha mismatch {bad}: {[(got[k][:12], want[k][:12]) for k in bad]} — STOP and hand back")
    return got


def prereg_header() -> Dict[str, str]:
    return {"prereg_s1c_sha256": PREREG_S1C_SHA256, "amend1_s1c_sha256": AMEND1_S1C_SHA256,
            "prereg_s1b1_sha256": PREREG_S1B1_SHA256}


def new_learner() -> Lr.RWLearner:
    """S1b-1's A-RW, unchanged, at its law's lr 0.01 (run.make_learner's own road)."""
    L = R.make_learner("A-RW", Lr.LR_S1B1, 0.3)
    if not isinstance(L, Lr.RWLearner) or L.lr != Lr.LR_S1B1 or L.oracle:
        raise S1cError("the learner is not S1b-1's A-RW at lr 0.01")
    return L


# ================================================================================================ the rooms of one seed
class RoomData:
    """One S1c seed's pools as the learner reads them: per room its visit scenes ([144 ‖ y/16, x/16] per hypothesis and
    what the parent said) and its window (stacked once for the loss). Never the truth."""

    def __init__(self, root: Path, seed: int, rooms: Sequence[str]):
        self.seed, self.rooms = int(seed), list(rooms)
        self.visit: Dict[str, R.Things] = {}
        self.window: Dict[str, PK.WindowSet] = {}
        self.shas: List[str] = []
        for r in self.rooms:
            pv = RM.RoomPercepts(RM.room_cache_dir(root, seed, r, "visit"))
            pw = RM.RoomPercepts(RM.room_cache_dir(root, seed, r, "window"))
            if len(pv) != RM.pool_size(r, "visit") or len(pw) != RM.pool_size(r, "window"):
                raise S1cError(f"room {r} seed {seed}: pools of {len(pv)} / {len(pw)}, the law says "
                               f"{RM.pool_size(r, 'visit')} / {RM.pool_size(r, 'window')}")
            self.visit[r] = R.Things(pv)
            tw = R.Things(pw)
            self.window[r] = PK.WindowSet([tw.for_arm("A-RW", i) for i in range(len(pw))],
                                          [pw.words(i) for i in range(len(pw))], VOCAB)
            self.shas += pv.shas() + pw.shas()

    def visit_scene(self, room: str, i: int) -> Tuple[np.ndarray, List[str]]:
        th = self.visit[room]
        if not 0 <= i < len(th.p):
            raise S1cError(f"room {room}: visit {i} is outside its pool of {len(th.p)}")
        return th.for_arm("A-RW", i), th.p.words(i)


# ================================================================================================ the fixed test set
class _LazyTieRng:
    """The item's own tie generator (marks.tie_rng), built only if `pick` draws — i.e. only on a tie, as answer_point."""

    def __init__(self, seed: int, item_id: str):
        self.seed, self.item_id, self.g = seed, item_id, None

    def integers(self, *a, **k):
        if self.g is None:
            self.g = M.tie_rng(self.seed, self.item_id)
        return self.g.integers(*a, **k)


class FixedTestSet:
    """S1's three test seeds POOLED (S1b-1's caches, questions and keys): the one-thing NAME items (WORDS-LEARNED) and the
    M1 items (S1a's grader, the covered 2- and 3-thing items). The GRADER'S road — the only place S1c reads a truth."""

    def __init__(self, root: Path = TEST_ROOT):
        self.root = Path(root)
        name_rows, self.name_truth, self.m1 = [], [], []
        self.per_seed: Dict[int, Dict[str, object]] = {}
        for ws in W.WORLD_SEEDS:
            ts = W.TEST_SEEDS[ws]
            Q = json.loads((self.root / str(ws) / "questions.json").read_text())["questions"]
            K = json.loads((self.root / str(ws) / "keys.json").read_text())["items"]
            th = R.Things(C.ScenePercepts(C.cache_dir(self.root, ws, "test")))
            tr = C.load_truth(C.cache_dir(self.root, ws, "test"))
            qn = {q["item_id"]: q for q in Q["NAME"]}
            for it in K["NAME"]:
                q = qn[it["item_id"]]
                if q.get("hyp") is None:
                    continue                                  # uncovered (none are, in S1b-1's items: 472 / 472)
                name_rows.append(th.for_arm("A-RW", q["row"])[int(q["hyp"])])
                self.name_truth.append({"item_id": it["item_id"], "shape": it["shape"], "colour": it["colour"],
                                        "size": it["size"]})
            qm = {q["item_id"]: q for q in Q["M1"]}
            items = []
            for it in K["M1"]:
                q = qm[it["item_id"]]
                row = tr[it["row"]]
                members, _pos = th.members(it["row"])
                self.m1.append({"ws": ws, "ts": ts, "item_id": it["item_id"], "X": th.for_arm("A-RW", q["row"]),
                                "phrase": list(q["phrase"]), "target": int(it["target"]), "n_things": int(it["n_things"]),
                                "covered": M.covered(int(it["target"]), row["fix_thing"]),
                                "labels": [M.hyp_label(c) for c in M.hyp_counts(members, row["fix_thing"])]})
                items.append(it)
            self.per_seed[ws] = {"items": items, "truth": tr, "things": th, "ts": ts}
        self.name_X = np.stack(name_rows)
        self.carry = {w: [i for i, t in enumerate(self.name_truth) if t[W.word_type(w)] == w] for w in VOCAB}
        self.word_n = {w: len(v) for w, v in self.carry.items()}
        self.m1_X = np.concatenate([it["X"] for it in self.m1 if it["X"].shape[0]], axis=0)
        h = np.array([it["X"].shape[0] for it in self.m1])
        self.m1_starts = np.concatenate([[0], np.cumsum(h)])
        self.shas = []
        for ws in W.WORLD_SEEDS:
            self.shas += self.per_seed[ws]["things"].p.shas()

    # -- WORDS-LEARNED ---------------------------------------------------------------------------
    def names(self, L: Lr.RWLearner) -> Dict[str, List[Optional[str]]]:
        """name_forced, batched: per type, the argmax of log p_w(t) over the type's HEARD words (the first on a tie, as
        name_forced's np.argmax), None when no word of the type was heard. Pinned against name_forced item by item
        (tests/brain/scene/test_run_s1c.py)."""
        Z = L.stats.standardise(self.name_X)
        lp = L.logp_answer(Z, getattr(L, "_bands_cache", None))
        out: Dict[str, List[Optional[str]]] = {}
        for t, words in TYPE_WORDS.items():
            cand = [w for w in words if w in L.index]
            if not cand:
                out[t] = [None] * Z.shape[0]
                continue
            cols = [L.index[w] for w in cand]
            k = np.argmax(lp[:, cols], axis=1)
            out[t] = [cand[int(i)] for i in k]
        return out

    def words_learned(self, L: Lr.RWLearner) -> Tuple[int, Dict[str, float]]:
        """The number of the 13 words whose forced naming on the one-thing scenes carrying the word reads ≥ 0.80; an
        unnamed word (None) is a miss (AMENDMENT 1 §4)."""
        nm = self.names(L)
        rates = {}
        for w in VOCAB:
            idx = self.carry[w]
            col = nm[W.word_type(w)]
            rates[w] = float(np.mean([col[i] == w for i in idx])) if idx else None
        return sum(1 for w in VOCAB if rates[w] is not None and rates[w] >= LEARNED_AT), rates

    # -- M1 -------------------------------------------------------------------------------------
    def points(self, L: Lr.RWLearner) -> Dict[str, Dict[str, object]]:
        """answer_point's forced pointing, batched: argmax of Σ log p_w(t) with ties by the item's own generator; an
        item whose phrase holds an unheard word is marked unheard (not gradable). Pinned against answer_point."""
        Z = L.stats.standardise(self.m1_X)
        lp = L.logp_answer(Z, getattr(L, "_bands_cache", None))
        out: Dict[str, Dict[str, object]] = {}
        for i, it in enumerate(self.m1):
            unheard = [w for w in it["phrase"] if w not in L.index]
            if unheard:
                out[it["item_id"]] = {"point": None, "none": None, "best": None, "unheard": unheard}
                continue
            a, b = int(self.m1_starts[i]), int(self.m1_starts[i + 1])
            s = lp[a:b][:, [L.index[w] for w in it["phrase"]]].sum(axis=1)
            k = Lr.pick(s, _LazyTieRng(it["ts"], it["item_id"]), "max")
            out[it["item_id"]] = {"point": k}
        return out

    def m1_fast(self, L: Lr.RWLearner, answers: Optional[Dict[str, Dict[str, object]]] = None) -> Optional[float]:
        ans = self.points(L) if answers is None else answers
        ok = []
        for it in self.m1:
            a = ans[it["item_id"]]
            if it["n_things"] < 2 or a.get("unheard") or not it["covered"]:
                continue
            k = a.get("point")
            ok.append(k is not None and it["labels"][int(k)] is not None and it["labels"][int(k)] == it["target"])
        return float(np.mean(ok)) if ok else None

    def pin(self, L: Lr.RWLearner, answers: Optional[Dict[str, Dict[str, object]]] = None) -> Dict[str, int]:
        """The batched readers against the learner's own per-item calls (name_forced; answer_point with the item's tie
        generator) on EVERY item at this state — run at the end of every life."""
        nm = self.names(L)
        bad_n = sum(1 for i in range(len(self.name_truth)) for t, ws in TYPE_WORDS.items()
                    if L.name_forced(self.name_X[i], ws) != nm[t][i])
        ans = self.points(L) if answers is None else answers
        bad_p = sum(1 for it in self.m1
                    if L.answer_point(it["X"], it["phrase"], M.tie_rng(it["ts"], it["item_id"])).get("point")
                    != ans[it["item_id"]].get("point"))
        return {"names_checked": len(self.name_truth) * len(TYPE_WORDS), "names_mismatch": bad_n,
                "points_checked": len(self.m1), "points_mismatch": bad_p}

    def m1_full(self, L: Lr.RWLearner, answers: Optional[Dict[str, Dict[str, object]]] = None) -> Dict[str, object]:
        """S1a's grader, whole: marks.grade_pointing per seed, the rows pooled, marks.summarise_pointing."""
        ans = self.points(L) if answers is None else answers
        rows = []
        for ws, d in self.per_seed.items():
            rows += M.grade_pointing(d["items"], ans, d["truth"], d["things"].members, "gaze")
        return M.summarise_pointing(rows)


# ================================================================================================ the LIFE
def train_block(L: Lr.RWLearner, data: RoomData, room: str, start: int, seed: int,
                snapshots: bool = False) -> List[np.ndarray]:
    """The learner trains on the room's next B = 10 unseen pool scenes exactly as in S1b-1 (train_scene: the episodic
    write, the delta rule); each scene's episodic generator is substream `episodic:room:<r>:visit:<i>` (declared)."""
    th = [PK.theta(L, VOCAB)] if snapshots else []
    for i in range(start, start + PK.BLOCK):
        X, words = data.visit_scene(room, i)
        L.train_scene(X, words, referent=None, rng=substream(seed, f"episodic:room:{room}:visit:{i}"))
        if snapshots:
            th.append(PK.theta(L, VOCAB))
    return th


def _same_state(a: Lr.RWLearner, b: Lr.RWLearner) -> bool:
    return (a.words == b.words and np.array_equal(a.V, b.V) and np.array_equal(a.b, b.b)
            and np.array_equal(a.meetings, b.meetings) and a.stats.n == b.stats.n
            and np.array_equal(a.stats.mean, b.stats.mean) and np.array_equal(a.stats.m2, b.stats.m2))


def life(data: RoomData, test: FixedTestSet, picker_name: str, rooms: Sequence[str], n_blocks: int = PK.N_BLOCKS,
         prefix: str = "", identity_credit: bool = False, log=None, m1_every_block: bool = False) -> Dict[str, object]:
    """One life of one picker on one seed: blocks 1..len(rooms) a fixed ROUND-ROBIN, then the picker's; the six L_k at
    every boundary (0..n_blocks); the record per block; WORDS-LEARNED at every boundary; M1 at the end."""
    cpu0, wall0 = time.process_time(), time.time()
    seed, rooms = data.seed, list(rooms)
    L = new_learner()
    cursor = {r: 0 for r in rooms}
    last = {r: 0 for r in rooms}
    Lk = {r: PK.window_loss(L, data.window[r]) for r in rooms}
    table = [dict(Lk)]
    wl_now, _ = test.words_learned(L)
    wl_curve = [wl_now]
    clones: Dict[str, Lr.RWLearner] = {}
    oracle_log: Dict[str, object] = {}

    def gain_fn(rs: Sequence[str]) -> Dict[str, Tuple[float, float]]:
        clones.clear()
        m1_now = test.m1_fast(L)
        oracle_log["m1_now"] = m1_now
        out = {}
        for r in rs:
            cl = copy.deepcopy(L)
            train_block(cl, data, r, cursor[r], seed)
            wl_c, _ = test.words_learned(cl)
            m1_c = test.m1_fast(cl)
            out[r] = (float(wl_c - wl_now), None if (m1_c is None or m1_now is None) else float(m1_c - m1_now))
            clones[r] = cl
        return out

    picker = PK.make_picker(picker_name, rooms, seed, gain_fn=gain_fn, prefix=prefix, identity_credit=identity_credit)
    rec: List[Dict[str, object]] = []
    for block in range(1, n_blocks + 1):
        est = picker.estimates()
        if block <= len(rooms):
            room, flag = rooms[block - 1], "round-robin"
        else:
            room, flag = picker.pick(block, PK.Context(last_visit=dict(last), L_now=dict(Lk)))
        start = cursor[room]
        thetas = train_block(L, data, room, start, seed, snapshots=True)
        cursor[room] += PK.BLOCK
        drift = PK.drift_reading(thetas)
        Lk_new = {r: PK.window_loss(L, data.window[r]) for r in rooms}
        drop = Lk[room] - Lk_new[room]
        credited = picker.observe(block, room, drop=drop, drift=drift)
        wl_now, _ = test.words_learned(L)
        row = {"block": block, "room": room, "flag": flag, "start": start, "est": est, "L": Lk_new, "drop": drop,
               "drift": drift, "credited": credited, "wl": wl_now}
        if picker_name == "ORACLE" and flag == "policy":
            same = _same_state(clones[room], L)
            if not same:
                raise S1cError(f"block {block}: the ORACLE's clone of {room} is not the learner after the same block")
            row.update({"gains": {r: list(v) for r, v in picker.last_gains.items()}, "m1_now": oracle_log.get("m1_now"),
                        "clone_identical": same})
        if m1_every_block:
            row["m1"] = test.m1_fast(L)
        rec.append(row)
        Lk = Lk_new
        table.append(dict(Lk))
        last[room] = block
        wl_curve.append(wl_now)
        if log is not None and block % 50 == 0:
            log(f"[{picker_name}{' ' + prefix if prefix else ''} {seed}] block {block}: wl {wl_now} · {room} {flag}")
    ans = test.points(L)
    full = test.m1_full(L, ans)
    fast = test.m1_fast(L, ans)
    if full["graded"]["covered"] != fast:
        raise S1cError(f"M1 fast {fast} ≠ the grader's {full['graded']['covered']}")
    pin = test.pin(L, ans)
    if pin["names_mismatch"] or pin["points_mismatch"]:
        raise S1cError(f"the batched readers differ from name_forced / answer_point at the life's end: {pin}")
    wl_end, rates = test.words_learned(L)
    out = {"seed": seed, "picker": picker_name, "rooms": rooms, "prefix": prefix, "identity_credit": identity_credit,
           "n_blocks": n_blocks, "record": rec, "table": table, "wl_curve": wl_curve, "rates_end": rates,
           "word_n": test.word_n, "m1_end": full["graded"], "m1_end_value": fast, "cursor": cursor,
           "pi": getattr(picker, "pi", None), "cpu_s": time.process_time() - cpu0, "wall_s": time.time() - wall0,
           "n_empty_windows": {r: data.window[r].n_empty for r in rooms}, "prereg": prereg_header(), "pin_end": pin,
           "code": R.code_identity(), "note": ORACLE_TRUTH_NOTE if picker_name == "ORACLE" else None}
    out["marks"] = run_marks(out)
    return out


# ================================================================================================ the marks
def longest_run(rooms_seq: Sequence[str]) -> Tuple[int, Optional[str]]:
    best, who, cur, prev = 0, None, 0, None
    for r in rooms_seq:
        cur = cur + 1 if r == prev else 1
        prev = r
        if cur > best:
            best, who = cur, r
    return best, who


def run_marks(run: Dict[str, object]) -> Dict[str, object]:
    """A, S12, SHARE, the exploration shares apart, LEAVE, the lock-in, the mean block-drop per room, the interference
    table, M1 at the end."""
    rec, rooms, table = run["record"], list(run["rooms"]), run["table"]
    n_rr = len(rooms)
    n_blocks = int(run["n_blocks"])
    pol = [x for x in rec if x["block"] > n_rr]
    n_pol = max(1, n_blocks - n_rr)
    wl = [x["wl"] for x in rec]
    A = float(np.mean(wl)) / len(VOCAB) if wl else None
    s12 = next((PK.BLOCK * x["block"] for x in rec if x["wl"] >= 12), None)
    share = {r: sum(1 for x in pol if x["room"] == r and x["flag"] == "policy") / n_pol for r in rooms}
    expl = {r: sum(1 for x in pol if x["room"] == r and x["flag"] == "explore") / n_pol for r in rooms}
    leave = {r: max([n_rr] + [x["block"] for x in pol if x["room"] == r and x["flag"] == "policy"]) for r in rooms}
    run_len, run_room = longest_run([x["room"] for x in pol])
    drops = {r: [x["drop"] for x in rec if x["room"] == r] for r in rooms}
    mean_drop = {r: (float(np.mean(v)) if v else None) for r, v in drops.items()}
    inter = {}
    for k in rooms:
        bl = [x["block"] for x in rec if x["room"] == k]
        inter[k] = {j: (float(np.mean([table[b][j] - table[b - 1][j] for b in bl])) if bl else None) for j in rooms}
    return {"A": A, "S12": s12, "share": share, "explore": expl, "leave": leave, "longest_run": run_len,
            "longest_run_room": run_room, "mean_drop": mean_drop, "interference": inter,
            "M1": run.get("m1_end_value"), "wl_end": wl[-1] if wl else None, "n_policy_blocks": n_pol}


# ================================================================================================ THE FIRST GATE
def room_claims(run: Dict[str, object]) -> Dict[str, object]:
    """Step 2 on a RANDOM life of 60 blocks: the TV flat in magnitude, the learnable rooms falling ≥ 3 × that, K known
    ((i) flat, (ii) as learned as any learnable room at block 60), U above 2 × the learnable rooms' last-20 mean. Declared:
    a room's «mean block-drop after block 20» reads over ITS OWN visited blocks 21–60 (the seat's line for K, applied to
    every room); «L's level» is the mean of L over the boundaries after blocks 21–60; «≥ 3 × that» is printed under both
    readings — 3 × |N's mean drop| (the gate's) and 3 × (0.05 × L_N's level)."""
    rec, table = run["record"], run["table"]
    after = [x for x in rec if x["block"] > GATE2_AFTER]
    blocks = [x["block"] for x in after]

    def mean_drop(rs):
        v = [x["drop"] for x in after if x["room"] in rs]
        return (float(np.mean(v)) if v else None), len(v)

    def level(r, lo, hi):
        return float(np.mean([table[b][r] for b in range(lo, hi + 1)]))

    last = max(blocks) if blocks else GATE2_BLOCKS
    n_drop, n_n = mean_drop(["N"])
    k_drop, n_k = mean_drop(["K"])
    r_drop, n_r = mean_drop(["R1", "R2", "R3"])
    lvl_n, lvl_k = level("N", GATE2_AFTER + 1, last), level("K", GATE2_AFTER + 1, last)
    lo = last - GATE2_LAST + 1
    u_last = level("U", lo, last) if "U" in run["rooms"] else None
    r_last = float(np.mean([level(r, lo, last) for r in ("R1", "R2", "R3")]))
    at = table[last]
    out = {"blocks": [GATE2_AFTER + 1, last], "n_visits": {"N": n_n, "K": n_k, "R": n_r},
           "N": {"mean_drop": n_drop, "level": lvl_n, "bound": GATE2_FLAT * lvl_n,
                 "pass": n_drop is not None and abs(n_drop) <= GATE2_FLAT * lvl_n},
           "R": {"mean_drop": r_drop,
                 "bound_gate": None if n_drop is None else GATE2_R_OVER_N * abs(n_drop),
                 "bound_alt": GATE2_R_OVER_N * GATE2_FLAT * lvl_n},
           "K": {"mean_drop": k_drop, "level": lvl_k, "bound": GATE2_FLAT * lvl_k, "L_K_end": at["K"],
                 "min_L_R_end": min(at["R1"], at["R2"], at["R3"]),
                 "pass_i": k_drop is not None and k_drop <= GATE2_FLAT * lvl_k,
                 "pass_ii": at["K"] <= min(at["R1"], at["R2"], at["R3"])}}
    out["R"]["pass"] = r_drop is not None and n_drop is not None and r_drop >= GATE2_R_OVER_N * abs(n_drop)
    out["R"]["pass_alt"] = r_drop is not None and r_drop >= out["R"]["bound_alt"]
    out["K"]["pass"] = out["K"]["pass_i"] and out["K"]["pass_ii"]
    out["U"] = {"last20": u_last, "R_last20": r_last, "bound": GATE2_U_OVER_R * r_last,
                "kept": u_last is not None and u_last >= GATE2_U_OVER_R * r_last}
    out["pass"] = bool(out["N"]["pass"] and out["R"]["pass"] and out["K"]["pass"])
    return out


def _fmt(v, nd=3) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def record_lines(run: Dict[str, object]) -> List[str]:
    """The record, whole, one line per block (THE FIRST GATE 5: the record is the instrument)."""
    rooms = run["rooms"]
    out = [f"   {run['picker']}{' (identity credit)' if run.get('identity_credit') else ''} — seed {run['seed']} · rooms "
           f"{rooms} · π {run.get('pi')}"]
    for x in run["record"]:
        est = " ".join(f"{r}:{_fmt(x['est'].get(r))}" for r in rooms)
        L = " ".join(f"{r}:{x['L'][r]:.3f}" for r in rooms)
        extra = ""
        if "gains" in x:
            extra = " · gains " + " ".join(f"{r}:{g[0]:+.0f}/{_fmt(g[1])}" for r, g in x["gains"].items())
        out.append(f"   b{x['block']:>3} {x['room']:<2} {x['flag']:<11} start {x['start']:>4} · est [{est}] · L [{L}] · "
                   f"drop {x['drop']:+.4f} · drift {x['drift']:.3f} · credited {x['credited']} · wl {x['wl']}{extra}")
    return out


def fence_sweep() -> Dict[str, object]:
    """Step 1's AST sweep: the truth fence's own test module, run in-process (it covers rooms.py and pickers.py)."""
    buf = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName("tests.brain.scene.test_truth_fence")
    res = unittest.TextTestRunner(stream=buf, verbosity=0).run(suite)
    return {"ran": res.testsRun, "ok": res.wasSuccessful(), "text": buf.getvalue().strip().splitlines()[-1:]}


def first_gate(root: Path = ROOT, log=print) -> Dict[str, object]:
    out: Dict[str, object] = {"verdict": "STOP", "seed": GATE_SEED}
    lines: List[str] = []

    def say(s: str) -> None:
        lines.append(s)
        log(s)

    shas = check_prereg()
    out["shas"] = shas
    say(f"THE FIRST GATE (S1c, seed {GATE_SEED}) — PREREG-S1C {shas['prereg_s1c'][:12]}… · AMENDMENT 1 {shas['amend1_s1c'][:12]}… · "
        f"PREREG-S1B1 {shas['prereg_s1b1'][:12]}… · code {R.code_identity()['code_sha_file']}")
    # 1. the caches and the fence
    data = RoomData(root, GATE_SEED, RM.ROOMS)
    test = FixedTestSet()
    disj = C.assert_disjoint(data.shas, test.shas)
    fence = fence_sweep()
    say(f"1. the room pools read: " + " · ".join(f"{r} {len(data.visit[r].p)}+{data.window[r].n}" for r in RM.ROOMS)
        + f" (H = 0 windows: {sum(w.n_empty for w in data.window.values())}) · the fixed test set: NAME {len(test.name_truth)}, "
        f"M1 {len(test.m1)} (graded 2–3 {sum(1 for it in test.m1 if it['n_things'] >= 2)}) · per-word n "
        f"{min(test.word_n.values())}–{max(test.word_n.values())} · no room canvas is a test canvas ({disj} checked) · "
        f"the truth fence's sweep (rooms.py + pickers.py): Ran {fence['ran']}, {'OK' if fence['ok'] else 'FAILED'}")
    out["step1"] = {"pools": {r: [len(data.visit[r].p), data.window[r].n] for r in RM.ROOMS}, "name": len(test.name_truth),
                    "m1": len(test.m1), "word_n": test.word_n, "disjoint_checked": disj, "fence": fence}
    if not fence["ok"] or min(test.word_n.values()) < UNDERPOWERED_WORD_N:
        say("   STOP at step 1")
        out["lines"] = lines
        return out
    # 2. the rooms are what they claim, under a RANDOM learner over 60 blocks
    r60 = life(data, test, "RANDOM", RM.ROOMS, n_blocks=GATE2_BLOCKS)
    cl = room_claims(r60)
    out["step2"] = cl
    say(f"2. RANDOM over {GATE2_BLOCKS} blocks, blocks {cl['blocks'][0]}–{cl['blocks'][1]} (visits N {cl['n_visits']['N']}, "
        f"K {cl['n_visits']['K']}, R1–R3 {cl['n_visits']['R']}):")
    say(f"   N: |mean drop| {_fmt(abs(cl['N']['mean_drop']) if cl['N']['mean_drop'] is not None else None, 4)} ≤ 0.05 × level "
        f"{_fmt(cl['N']['level'])} = {_fmt(cl['N']['bound'], 4)} → {'PASS' if cl['N']['pass'] else 'MISS'}")
    say(f"   R1–R3: mean drop {_fmt(cl['R']['mean_drop'], 4)} ≥ 3 × |N's| = {_fmt(cl['R']['bound_gate'], 4)} → "
        f"{'PASS' if cl['R']['pass'] else 'MISS'} (the other reading, ≥ 3 × 0.05 × L_N's level = {_fmt(cl['R']['bound_alt'], 4)}: "
        f"{'PASS' if cl['R']['pass_alt'] else 'MISS'})")
    say(f"   K: (i) mean drop {_fmt(cl['K']['mean_drop'], 4)} ≤ 0.05 × level {_fmt(cl['K']['level'])} = "
        f"{_fmt(cl['K']['bound'], 4)} → {'PASS' if cl['K']['pass_i'] else 'MISS'} · (ii) L_K(60) {_fmt(cl['K']['L_K_end'])} ≤ "
        f"min L_R(60) {_fmt(cl['K']['min_L_R_end'])} → {'PASS' if cl['K']['pass_ii'] else 'MISS'}")
    say(f"   U: last-20 mean {_fmt(cl['U']['last20'])} ≥ 2 × R1–R3's {_fmt(cl['U']['R_last20'])} = {_fmt(cl['U']['bound'])} → "
        f"{'U KEPT' if cl['U']['kept'] else 'U DROPPED (its bars with it)'}")
    say("   the room-by-block table of L_k (every 10th boundary): " + " | ".join(
        f"b{b}: " + " ".join(f"{r} {r60['table'][b][r]:.2f}" for r in RM.ROOMS) for b in range(0, GATE2_BLOCKS + 1, 10)))
    if not cl["pass"]:
        say("   STOP at step 2")
        out["lines"] = lines
        return out
    rooms = list(RM.ROOMS) if cl["U"]["kept"] else [r for r in RM.ROOMS if r != "U"]
    out["rooms"] = rooms
    out["u_dropped"] = not cl["U"]["kept"]
    # 3. the positive control
    ro = life(data, test, "ORACLE", rooms, log=log)
    rr = life(data, test, "RANDOM", rooms, log=log)
    R.dump(Path(root) / "gate" / "step3-ORACLE.json", ro)
    R.dump(Path(root) / "gate" / "step3-RANDOM.json", rr)
    R.dump(Path(root) / "gate" / "step2-RANDOM60.json", r60)
    diff = ro["marks"]["A"] - rr["marks"]["A"]
    out["step3"] = {"A_oracle": ro["marks"]["A"], "A_random": rr["marks"]["A"], "diff": diff,
                    "pass": diff >= BAR_POSITIVE_CONTROL, "cpu_s": {"ORACLE": ro["cpu_s"], "RANDOM": rr["cpu_s"]}}
    say(f"3. the positive control: A(ORACLE) {ro['marks']['A']:.3f} − A(RANDOM) {rr['marks']['A']:.3f} = {diff:+.3f} ≥ 0.05 → "
        f"{'PASS' if diff >= BAR_POSITIVE_CONTROL else 'MISS'} (CPU {ro['cpu_s']:.1f} s / {rr['cpu_s']:.1f} s; the ORACLE's clone "
        f"equalled the learner after every policy block: {all(x.get('clone_identical', True) for x in ro['record'])})")
    if diff < BAR_POSITIVE_CONTROL:
        say("   STOP at step 3 (S1c reads NOT GRADABLE: the world offers no choice)")
        out["lines"] = lines
        return out
    # 4 + 5. the null is a null; the smoke of every picker, its record read whole
    smoke = {p: life(data, test, p, rooms, n_blocks=SMOKE_BLOCKS) for p in PK.PICKERS}
    ident = life(data, test, "NULL", rooms, n_blocks=SMOKE_BLOCKS, identity_credit=True)
    for p, r in list(smoke.items()) + [("NULL-identity-credit", ident)]:
        R.dump(Path(root) / "gate" / "smoke" / f"{p}.json", r)
    pi = PK.null_derangement(GATE_SEED, rooms)
    planted_identity = {r: r for r in rooms}
    src = next(k for k, v in pi.items() if v == rooms[0])
    planted_one = dict(pi)
    planted_one[rooms[0]], planted_one[src] = rooms[0], pi[rooms[0]]
    keys = ("block", "room", "flag", "start", "est", "L", "drop", "drift", "credited", "wl")
    same_as_progress = [{k: x[k] for k in keys} for x in ident["record"]] == [{k: x[k] for k in keys} for x in smoke["PROGRESS"]["record"]]
    null_lands_home = [x["block"] for x in smoke["NULL"]["record"] if x["credited"] == x["room"]]
    expl_bad = {p: PK.exploration_mismatches(smoke[p]["record"], GATE_SEED, rooms) for p in PK.EPS_PICKERS}
    rec_flip = [dict(x) for x in smoke["PROGRESS"]["record"]]
    k_pol = next((i for i, x in enumerate(rec_flip) if x["flag"] == "policy"), None)
    caught_flip = False
    if k_pol is not None:
        rec_flip[k_pol]["flag"] = "explore"
        caught_flip = PK.exploration_mismatches(rec_flip, GATE_SEED, rooms) == [rec_flip[k_pol]["block"]]
    s4 = {"pi": pi, "is_derangement": PK.is_derangement(pi), "planted_identity_caught": not PK.is_derangement(planted_identity),
          "planted_fixed_point_caught": not PK.is_derangement(planted_one), "identity_credit_is_progress": same_as_progress,
          "null_credit_lands_home": null_lands_home, "exploration_mismatches": expl_bad, "planted_flip_caught": caught_flip}
    s4["pass"] = bool(s4["is_derangement"] and s4["planted_identity_caught"] and s4["planted_fixed_point_caught"]
                      and same_as_progress and not null_lands_home and not any(expl_bad.values()) and caught_flip)
    out["step4"] = s4
    say(f"4. the null is a null: π = {pi} (a derangement: {s4['is_derangement']}; the planted identity caught: "
        f"{s4['planted_identity_caught']}; a planted fixed point caught: {s4['planted_fixed_point_caught']}) · the planted "
        f"identity-credit null reads exactly PROGRESS's {SMOKE_BLOCKS}-block record: {same_as_progress} · the null's credit "
        f"lands on its producer at blocks {null_lands_home or 'none'} · exploration flags vs the ε stream: "
        f"{ {p: v or 'all agree' for p, v in expl_bad.items()} } (a planted flipped flag caught: {caught_flip}) → "
        f"{'PASS' if s4['pass'] else 'MISS'}")
    say(f"5. the {SMOKE_BLOCKS}-block smoke of every picker, each record whole:")
    for p in PK.PICKERS:
        for ln in record_lines(smoke[p]):
            say(ln)
    for ln in record_lines(ident):
        say(ln)
    out["step5"] = {p: {"rooms": [x["room"] for x in smoke[p]["record"]], "flags": [x["flag"] for x in smoke[p]["record"]],
                        "cpu_s": smoke[p]["cpu_s"]} for p in PK.PICKERS}
    if not s4["pass"]:
        say("   STOP at step 4")
        out["lines"] = lines
        return out
    out["verdict"] = "PROCEED"
    say(f"THE FIRST GATE: PROCEED — rooms {rooms}{' (U dropped)' if out['u_dropped'] else ''}")
    out["lines"] = lines
    return out


def gate_rooms(root: Path = ROOT) -> List[str]:
    """The rooms in play, from THE FIRST GATE's own record; no run starts without a PROCEED."""
    p = Path(root) / "gate" / "first_gate.json"
    if not p.exists():
        raise S1cError(f"{p} is missing — THE FIRST GATE has not run")
    g = json.loads(p.read_text())
    if g.get("verdict") != "PROCEED":
        raise S1cError(f"THE FIRST GATE reads {g.get('verdict')} — no run")
    return list(g["rooms"])


# ================================================================================================ the report
def _q(v: Sequence[float], q: float) -> float:
    return float(np.percentile(np.asarray(v, dtype=np.float64), q))


def verdict_of(per_seed: Dict[int, Dict[str, Dict[str, object]]], u_kept: bool) -> Dict[str, object]:
    """The bars (PREREG-S1C §4 as AMENDMENT 1 §3 re-set them). per_seed[seed][picker] = run_marks(...). Declared order:
    NOT GRADABLE (the positive control fails at any seed) → VOID (the NULL meets PROGRESS's A and SHARE_N bars at ≥ 2
    seeds) → PASS (every PROGRESS bar at every seed) / FAIL."""
    seeds = sorted(per_seed)
    pc, bars, null_meets = {}, {}, {}
    for s in seeds:
        m = per_seed[s]
        o, rnd, p, nl = m["ORACLE"], m["RANDOM"], m["PROGRESS"], m["NULL"]
        pc[s] = {"diff": o["A"] - rnd["A"], "pass": (o["A"] - rnd["A"]) >= BAR_POSITIVE_CONTROL}
        a_bar = BAR_A_VS_ORACLE * o["A"]
        b = {"A": {"value": p["A"], "bar": a_bar, "pass": p["A"] >= a_bar},
             "SHARE_N": {"value": p["share"]["N"], "bar": o["share"]["N"] + BAR_SHARE_ALLOWANCE,
                         "pass": p["share"]["N"] <= o["share"]["N"] + BAR_SHARE_ALLOWANCE},
             "LEAVE_N": {"value": p["leave"]["N"], "bar": BAR_LEAVE_N, "pass": p["leave"]["N"] <= BAR_LEAVE_N}}
        if u_kept:
            b["SHARE_U"] = {"value": p["share"]["U"], "bar": o["share"]["U"] + BAR_SHARE_ALLOWANCE,
                            "pass": p["share"]["U"] <= o["share"]["U"] + BAR_SHARE_ALLOWANCE}
        bars[s] = b
        null_meets[s] = {"A": nl["A"] >= a_bar, "SHARE_N": nl["share"]["N"] <= o["share"]["N"] + BAR_SHARE_ALLOWANCE}
        null_meets[s]["both"] = null_meets[s]["A"] and null_meets[s]["SHARE_N"]
    n_null = sum(1 for s in seeds if null_meets[s]["both"])
    all_pass = all(v["pass"] for s in seeds for v in bars[s].values())
    if not all(pc[s]["pass"] for s in seeds):
        verdict = "NOT GRADABLE"
    elif n_null >= 2:
        verdict = "VOID"
    else:
        verdict = "PASS" if all_pass else "FAIL"
    return {"verdict": verdict, "positive_control": pc, "bars": bars, "null_meets": null_meets, "null_seeds": n_null,
            "all_bars_pass": all_pass}


def refutations(per_seed: Dict[int, Dict[str, Dict[str, object]]], u_kept: bool) -> Dict[str, object]:
    seeds = sorted(per_seed)
    a_rand = [per_seed[s]["RANDOM"]["A"] for s in seeds]
    spread = max(a_rand) - min(a_rand)
    out = {"a": {s: per_seed[s]["PROGRESS"]["share"]["N"] >= per_seed[s]["ERROR"]["share"]["N"] for s in seeds},
           "b": {s: per_seed[s]["PROGRESS"]["A"] <= per_seed[s]["RANDOM"]["A"] + spread for s in seeds},
           "d": {s: per_seed[s]["PROGRESS-DRIFT"]["share"]["N"] >= per_seed[s]["ERROR"]["share"]["N"] for s in seeds},
           "random_spread": spread}
    if u_kept:
        out["c"] = {s: per_seed[s]["PROGRESS"]["share"]["U"] >= per_seed[s]["ERROR"]["share"]["U"] for s in seeds}
    return out


def load_runs(root: Path = ROOT) -> Tuple[Dict[int, Dict[str, Dict[str, object]]], Dict[int, List[Dict[str, object]]]]:
    main, band = {}, {}
    for s in RM.S1C_SEEDS:
        d = Path(root) / str(s)
        main[s] = {p: json.loads((d / "runs" / f"{p}.json").read_text()) for p in PK.PICKERS
                   if (d / "runs" / f"{p}.json").exists()}
        band[s] = [json.loads(f.read_text()) for f in sorted((d / "band").glob("random-*.json"))] if (d / "band").exists() else []
    return main, band


def report(root: Path = ROOT, log=print) -> Dict[str, object]:
    shas = check_prereg()
    rooms = gate_rooms(root)
    u_kept = "U" in rooms
    runs, band = load_runs(root)
    missing = [(s, p) for s in RM.S1C_SEEDS for p in PK.PICKERS if p not in runs[s]]
    if missing:
        raise S1cError(f"runs missing: {missing}")
    per_seed = {s: {p: runs[s][p]["marks"] for p in PK.PICKERS} for s in RM.S1C_SEEDS}
    v = verdict_of(per_seed, u_kept)
    rf = refutations(per_seed, u_kept)
    L: List[str] = []
    L.append(f"S1c «THE NOISY ROOM» — the report · PREREG-S1C {shas['prereg_s1c'][:12]}… · AMENDMENT 1 {shas['amend1_s1c'][:12]}… · "
             f"rooms {rooms}{'' if u_kept else ' (U dropped by THE FIRST GATE)'} · 200 blocks × 10 scenes · 13 words")
    L.append("")
    L.append("per seed (A = words-learned per scene, ceiling 1.0; S12 = the scene at which ≥ 12 of 13 first hold; SHARE / "
             "exploration apart over the policy blocks; LEAVE = the last policy pick, earliest possible "
             f"{len(rooms)}; lock-in = the longest run of one room in the policy blocks; M1 = the covered graded items at 200):")
    for s in RM.S1C_SEEDS:
        L.append(f" seed {s}:")
        for p in PK.PICKERS:
            m = per_seed[s][p]
            sh = " ".join(f"{r} {m['share'][r]:.3f}" for r in rooms)
            ex = " ".join(f"{r} {m['explore'][r]:.3f}" for r in rooms)
            L.append(f"   {p:<15} A {m['A']:.3f} · S12 {m['S12'] if m['S12'] is not None else '∞'} · SHARE [{sh}] · explore [{ex}] · "
                     f"LEAVE_N {m['leave']['N']}{' · LEAVE_U ' + str(m['leave']['U']) if u_kept else ''} · lock-in "
                     f"{m['longest_run']} ({m['longest_run_room']}) · M1 {_fmt(m['M1'])} · wl@200 {m['wl_end']} · "
                     f"CPU {runs[s][p]['cpu_s']:.1f} s")
    L.append("")
    L.append("THE POSITIVE CONTROL (A(ORACLE) − A(RANDOM) ≥ 0.05 at every seed): " + " · ".join(
        f"{s} {v['positive_control'][s]['diff']:+.3f} {'PASS' if v['positive_control'][s]['pass'] else 'MISS'}" for s in RM.S1C_SEEDS))
    L.append("THE NULL (AMENDMENT 1 §3 (a): PROGRESS's bars VOID iff the NULL meets PROGRESS's A AND SHARE_N bars at ≥ 2 seeds): "
             + " · ".join(f"{s} A {'meets' if v['null_meets'][s]['A'] else 'misses'}, SHARE_N "
                          f"{'meets' if v['null_meets'][s]['SHARE_N'] else 'misses'}" for s in RM.S1C_SEEDS)
             + f" → at {v['null_seeds']} seed(s)")
    L.append("PROGRESS's bars (every bar at all 3 seeds):")
    for s in RM.S1C_SEEDS:
        L.append(f"   {s}: " + " · ".join(f"{k} {_fmt(b['value'])} vs {_fmt(b['bar'])} {'PASS' if b['pass'] else 'FAIL'}"
                                         for k, b in v["bars"][s].items()))
    L.append(f"THE VERDICT: {v['verdict']}")
    L.append("")
    L.append("the refutations (§5; per seed — a refutation reads as stated where it holds at all 3):")
    names = {"a": "(a) SHARE_N(PROGRESS) ≥ SHARE_N(ERROR)", "b": f"(b) A(PROGRESS) ≤ A(RANDOM) + RANDOM's seed spread {rf['random_spread']:.3f}",
             "c": "(c) SHARE_U(PROGRESS) ≥ SHARE_U(ERROR)", "d": "(d) (a reading) SHARE_N(PROGRESS-DRIFT) ≥ SHARE_N(ERROR)"}
    for k in ("a", "b", "c", "d"):
        if k in rf:
            L.append(f"   {names[k]}: " + " · ".join(f"{s} {'holds' if rf[k][s] else 'does not hold'}" for s in RM.S1C_SEEDS)
                     + f" → {'REFUTED' if all(rf[k].values()) else 'not refuted'}")
    L.append("the predictions (§5; Guessing, the directions Likely):")
    for s in RM.S1C_SEEDS:
        m = per_seed[s]
        esu = m["ERROR"]["share"]["N"] + (m["ERROR"]["share"]["U"] if u_kept else 0.0)
        rnku = sum(m["RANDOM"]["share"][r] + m["RANDOM"]["explore"][r] for r in rooms if r in ("N", "K", "U"))
        L.append(f"   {s}: ERROR's SHARE_N + SHARE_U {esu:.3f} (> 0.5 predicted) · PROGRESS's LEAVE_N {m['PROGRESS']['leave']['N']} "
                 f"(≤ 20 predicted) · A(PROGRESS) / A(ORACLE) {m['PROGRESS']['A'] / m['ORACLE']['A']:.3f} (≥ 0.80 predicted) · "
                 f"RANDOM in N, K, U {rnku:.3f} (≈ 0.5) · A(RANDOM) / A(ORACLE) {m['RANDOM']['A'] / m['ORACLE']['A']:.3f} (≈ 0.6)")
    L.append("")
    L.append("THE NULL against RANDOM's band (AMENDMENT 1 §3 (b), a READING: 20 extra RANDOM runs per seed, the 2.5–97.5 % band):")
    for s in RM.S1C_SEEDS:
        b = band[s]
        nl = per_seed[s]["NULL"]
        if len(b) < len(BAND_K):
            L.append(f"   {s}: the band has {len(b)} of {len(BAND_K)} runs — not read")
            continue
        a = [x["marks"]["A"] for x in b]
        sn = [x["marks"]["share"]["N"] for x in b]
        lr = [x["marks"]["longest_run"] for x in b]
        L.append(f"   {s}: A(NULL) {nl['A']:.3f} vs the band [{_q(a, 2.5):.3f}, {_q(a, 97.5):.3f}] "
                 f"({'inside' if _q(a, 2.5) <= nl['A'] <= _q(a, 97.5) else 'OUTSIDE'}) · SHARE_N(NULL) {nl['share']['N']:.3f} vs "
                 f"[{_q(sn, 2.5):.3f}, {_q(sn, 97.5):.3f}] ({'inside' if _q(sn, 2.5) <= nl['share']['N'] <= _q(sn, 97.5) else 'OUTSIDE'}) · "
                 f"the null's lock-in {nl['longest_run']} ({nl['longest_run_room']}) vs RANDOM's longest runs {min(lr)}–{max(lr)} · π "
                 f"{runs[s]['NULL']['pi']}")
    L.append("")
    L.append("the instrument (per seed, under RANDOM): the mean block-drop per room over its own blocks; the interference "
             "(the mean change of each room's L_j during a block in k; the diagonal is the room's own −drop):")
    for s in RM.S1C_SEEDS:
        m = per_seed[s]["RANDOM"]
        L.append(f"   {s}: mean drop " + " ".join(f"{r} {_fmt(m['mean_drop'][r], 4)}" for r in rooms))
        for k in rooms:
            L.append(f"      block in {k:<2}: " + " ".join(f"{j} {_fmt(m['interference'][k][j], 4)}" for j in rooms))
    L.append("")
    L.append("per-word n on the fixed test set (one-thing scenes): " + " ".join(
        f"{w} {runs[RM.S1C_SEEDS[0]]['PROGRESS']['word_n'][w]}" for w in VOCAB))
    txt = "\n".join(L)
    (Path(root) / "report.txt").write_text(txt + "\n")
    R.dump(Path(root) / "report.json", {"verdict": v, "refutations": rf, "per_seed": per_seed, "rooms": rooms, "shas": shas,
                                        "band": {s: [x["marks"] for x in band[s]] for s in RM.S1C_SEEDS}})
    for ln in L:
        log(ln)
    return {"verdict": v, "refutations": rf}


# ================================================================================================ the price
def price(root: Path = ROOT, log=print) -> Dict[str, object]:
    """Solo, at seed 20261301: one life of RANDOM, PROGRESS, PROGRESS-DRIFT and ORACLE (ERROR and NULL cost what PROGRESS
    costs); the projection for the unit: the pools of two seeds, 18 lives, 60 band lives."""
    check_prereg()
    rooms = gate_rooms(root)
    data = RoomData(root, GATE_SEED, rooms)
    test = FixedTestSet()
    cpu = {}
    for p in ("RANDOM", "PROGRESS", "PROGRESS-DRIFT", "ORACLE"):
        r = life(data, test, p, rooms)
        cpu[p] = r["cpu_s"]
        log(f"[price] {p}: {r['cpu_s']:.1f} CPU-s ({r['wall_s']:.1f} s wall)")
    spec, gcfg, colour = RM.eye.eye_config()
    sample = [RM.room_scene(GATE_SEED, r, "visit", i) for r in RM.ROOMS for i in range(50)]
    t0 = time.process_time()
    for sc in sample:
        RM._percepts(sc, spec, gcfg, colour)
    per_canvas = (time.process_time() - t0) / len(sample)
    n_canvas = len(RM.ROOMS) * RM.N_VISIT + (len(RM.ROOMS) - 1) * RM.N_WINDOW + RM.K_WINDOW
    pool_cpu = per_canvas * n_canvas
    log(f"[price] the eye: {1000 * per_canvas:.2f} CPU-ms per canvas × {n_canvas} canvases = {pool_cpu:.1f} CPU-s per seed")
    per_seed = cpu["RANDOM"] + cpu["PROGRESS"] * 3 + cpu["PROGRESS-DRIFT"] + cpu["ORACLE"]
    total = 3 * per_seed + 3 * len(BAND_K) * cpu["RANDOM"] + (2 * pool_cpu if pool_cpu else 0.0)
    out = {"cpu_s": cpu, "pool_cpu_s_per_seed": pool_cpu, "per_seed_lives_cpu_s": per_seed, "unit_cpu_min": total / 60.0}
    log(f"[price] the unit: 18 lives {3 * per_seed / 60:.1f} CPU-min + 60 band lives {3 * len(BAND_K) * cpu['RANDOM'] / 60:.1f} "
        f"+ two seeds' pools {(2 * pool_cpu / 60) if pool_cpu else float('nan'):.1f} = {total / 60:.1f} CPU-min "
        f"(the declared ≤ 15 CPU-min is replaced by this figure — AMENDMENT 1 §1)")
    R.dump(Path(root) / "price" / "price.json", out)
    return out


# ================================================================================================ the CLI
def _ks(spec: str) -> List[int]:
    a, _, b = spec.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="brain.scene.run_s1c")
    ap.add_argument("cmd", choices=["check", "cache-rooms", "first-gate", "run", "band", "price", "report"])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--seed", type=int)
    ap.add_argument("--picker")
    ap.add_argument("--k", default="1-20")
    a = ap.parse_args(argv)
    root = Path(a.root)
    log = R.Log(root / "logs" / f"{a.cmd}.log")
    if a.cmd == "check":
        log(json.dumps(check_prereg()))
        return 0
    check_prereg()
    if a.cmd == "cache-rooms":
        t0, w0 = time.process_time(), time.time()
        RM.build_seed(root, a.seed, prereg=prereg_header(), log=log)
        log(f"[rooms {a.seed}] {time.process_time() - t0:.1f} CPU-s, {time.time() - w0:.1f} s wall")
        return 0
    if a.cmd == "first-gate":
        g = first_gate(root, log=log)
        R.dump(root / "gate" / "first_gate.json", g)
        (root / "gate" / "first_gate.out").write_text("\n".join(g.get("lines", [])) + "\n")
        return 0 if g["verdict"] == "PROCEED" else 10
    if a.cmd in ("run", "band"):
        rooms = gate_rooms(root)
        data = RoomData(root, a.seed, rooms)
        test = FixedTestSet()
        if a.cmd == "run":
            r = life(data, test, a.picker, rooms, log=log)
            R.dump(root / str(a.seed) / "runs" / f"{a.picker}.json", r)
            log(f"[run {a.picker} {a.seed}] A {r['marks']['A']:.3f} · SHARE_N {r['marks']['share']['N']:.3f} · "
                f"LEAVE_N {r['marks']['leave']['N']} · M1 {_fmt(r['marks']['M1'])} · {r['cpu_s']:.1f} CPU-s")
            return 0
        for k in _ks(a.k):
            r = life(data, test, "RANDOM", rooms, prefix=PK.band_prefix(a.seed, k))
            R.dump(root / str(a.seed) / "band" / f"random-{k:02d}.json", r)
            log(f"[band {a.seed} k {k}] A {r['marks']['A']:.3f} · SHARE_N {r['marks']['share']['N']:.3f} · {r['cpu_s']:.1f} CPU-s")
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
