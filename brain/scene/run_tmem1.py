"""run_tmem1.py — T-MEM-1 «THE BRAIN READS ITS MEMORY»: the pools (redrawn under the merged code and TESTED equal to
S1c's), the eight training lives × two schedules, the answer roads over one training (A-RW, A-READ in the store's own
coordinates, its label-permuted null, A-READ-EM, TIME-WINDOW), the replay selections (UNIFORM, DRIFT and its null,
SURPRISE, ORACLE-DRIFT), the GATE and its random-anchor null, the marks (BWT per room boundary on held items, KEEP, FWT, A,
M1, the N-pollution prints), THE FIRST GATE's five steps, the price, the report. Runs under /usr/bin/python3.

edit: Claude (Opus 5.5, T-MEM-1 builder), 2026-09-28 17:23 +0400 — new module, written to docs/brain/memory/PREREG-TMEM1.md (genome-wt-brain3
ce41448, sha 0a87fefc…, FINAL: co-signed at ba168c2 and signed by the seat) and CONCLUSION-MEMORY.md (7cb72ca, sha 015da3e6…, co-signed); it extends PREREG-S1C
(a552515a…) + AMENDMENT 1 (92188d04…) + PREREG-S1C2 (5e4585c1…). The coordinator's rulings on the builder's nine declared
readings (2026-09-28 17:1x) are marked «ruled» and listed in docs/brain/memory/TMEM1-HANDBACK.md.

  python3 -m brain.scene.run_tmem1 check                       the shas
  python3 -m brain.scene.run_tmem1 pools --seed S              the five pools of one seed, redrawn and TESTED equal to S1c's
  python3 -m brain.scene.run_tmem1 first-gate                  THE FIRST GATE, steps 1–5
  python3 -m brain.scene.run_tmem1 run --life L --schedule seq|random --seed S
  python3 -m brain.scene.run_tmem1 price
  python3 -m brain.scene.run_tmem1 report

THE LIVES (one training each; the answer road never changes the learner, so A-RW, A-READ, its null, A-READ-EM and
TIME-WINDOW are five roads over ONE training — «same seed, same attributions», PREREG-TMEM1 §2):
  BASE          S1b-1's A-RW at lr 0.01, no replay        roads RW (A-RW) · READ (A-READ) · READ-NULL · READ-EM · TIME-WINDOW
  UNIFORM       + room-balanced replay (S1c-2's law)      road RW
  DRIFT         + replay by META's drift (∝ positive drift, ruled)       road RW
  DRIFT-NULL    + the same with the drift permuted over words            road RW
  SURPRISE      + replay of the top-R scenes by their loss at storage (the creature's most_surprising)   road RW
  ORACLE-DRIFT  + replay by the TRUE fall of held naming (∝ positive fall)   road RW
  GATE          UNIFORM + OWM per update, anchors = the strong words' 8 most recent self-consistent meetings   road RW
  GATE-RANDOM   UNIFORM + OWM per update, anchors = 8 random stored meetings per strong word   road RW
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.world.seeds import substream

from . import cache as C
from . import marks as M
from . import memory as MEM
from . import pickers as PK
from . import rooms as RM
from . import run as R
from . import run_s1c as S
from . import run_s1c2 as S2
from . import world as W

# ------------------------------------------------------------------------------------------------ the PREREG's numbers
PREREG_TMEM1_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/memory/PREREG-TMEM1.md")
PREREG_TMEM1_SHA256 = "0a87fefcef415a8b2964008f986577f90c0e6c2fb5141711b2ef00fb9ad59423"      # final: the seat signs the final text, ce41448
CONCLUSION_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/memory/CONCLUSION-MEMORY.md")
CONCLUSION_SHA256 = "015da3e66da89cb57c9080e5cb3ab9760ecdb7410ffd744dab71f045330c2b12"        # co-signed, 7cb72ca
ROOT = Path("/data/dev/brain-runs/scene-tmem1")
S1C_ROOT = S.ROOT                   # the reference pools (S1c's caches; refused by the merged code, compared as files)
S1C2_ROOT = S2.ROOT                 # the identity records (S1c-2's runs)
S1B1_ROOT = C.S1B1_RUNS             # S1b-1's own caches (the fixed test set as S1c read it; compared as files)
ROOMS: Tuple[str, ...] = tuple(S.WORLDS["law"])
POOL_ROOMS: Tuple[str, ...] = ROOMS
SEEDS: Tuple[int, ...] = RM.S1C_SEEDS
GATE_SEED = S.GATE_SEED
BLOCKS_PER_ROOM = 50
N_BLOCKS = 200
READ_POINTS: Tuple[int, ...] = (50, 100, 150, 200)
SHAPE_TASKS: Tuple[Tuple[str, ...], ...] = tuple(tuple(RM.ROOM_SHAPES[r]) for r in ("R1", "R2", "R3"))
R_REPLAY = 10
SIDAK_Z = 2.4
GATE_SE = 2.0
KEEP_FRACTION = 0.90
WINDOW_SCENES = BLOCKS_PER_ROOM * PK.BLOCK        # TIME-WINDOW: the last 50 blocks' meetings
SMOKE_BLOCKS = 20
PIN_TOL = 1e-9
BAND_STREAM_K = 1                                 # schedule (b): S1c's band pick stream random-band:<seed>:1 (ruled)
VOCAB: Tuple[str, ...] = RM.VOCAB13
TYPE_WORDS = S.TYPE_WORDS
LIVES: Dict[str, Tuple[Optional[str], Optional[str]]] = {
    "BASE": (None, None), "UNIFORM": ("uniform", None), "DRIFT": ("drift", None), "DRIFT-NULL": ("drift-null", None),
    "SURPRISE": ("surprise", None), "ORACLE-DRIFT": ("oracle-drift", None), "GATE": ("uniform", "strong"),
    "GATE-RANDOM": ("uniform", "random")}
SCHEDULES: Tuple[str, ...] = ("seq", "random")
READ_ROADS: Tuple[str, ...] = ("READ", "READ-NULL", "READ-EM", "TIME-WINDOW")


class TmemError(Exception):
    pass


def check_prereg() -> Dict[str, str]:
    got = dict(S2.check_prereg())          # PREREG-S1C2, PREREG-S1C, AMENDMENT 1, PREREG-S1B1
    for key, path, want in (("prereg_tmem1", PREREG_TMEM1_PATH, PREREG_TMEM1_SHA256),
                            ("conclusion_memory", CONCLUSION_PATH, CONCLUSION_SHA256)):
        g = hashlib.sha256(path.read_bytes()).hexdigest()
        if g != want:
            raise TmemError(f"{key} sha256 {g[:12]}… ≠ {want[:12]}… — STOP and hand back")
        got[key] = g
    return got


def prereg_header() -> Dict[str, str]:
    return {**S2.prereg_header(), "prereg_tmem1_sha256": PREREG_TMEM1_SHA256, "conclusion_memory_sha256": CONCLUSION_SHA256}


def chosen_eps() -> float:
    """ε = P-ORACLE's (ruled): the first gate's choice as S1b-1R's record carries it (S1b-1's own choice)."""
    return float(R.gate_or_chosen(C.RUNS)["eps"])


# ================================================================================================ the pools
def build_pools(root: Path, seed: int, log=None) -> Dict[str, object]:
    out = {}
    for room in POOL_ROOMS:
        for kind in RM.KINDS:
            d = RM.room_cache_dir(root, seed, room, kind)
            if not d.exists():
                RM.build_room_cache(root, seed, room, kind, prereg=prereg_header(), log=log)
            out[f"{room}-{kind}"] = C.identity_with(d, RM.room_cache_dir(S1C_ROOT, seed, room, kind))
    return out


def pools_identical(root: Path, seed: int) -> Dict[str, object]:
    """Every redrawn pool against S1c's, as files: the canvas shas, the scene specs and the glances' npy sha."""
    res = {f"{room}-{kind}": C.identity_with(RM.room_cache_dir(root, seed, room, kind), RM.room_cache_dir(S1C_ROOT, seed, room, kind))
           for room in POOL_ROOMS for kind in RM.KINDS}
    return {"pools": res, "same": all(v["same"] for v in res.values())}


def test_set_identical() -> Dict[str, object]:
    """The fixed test set as the merged code reads it (S1b-1R's redraw of S1b-1's caches) against S1b-1's own, as files."""
    res = {ws: C.identity_with(C.cache_dir(C.RUNS, ws, "test"), C.cache_dir(S1B1_ROOT, ws, "test")) for ws in W.WORLD_SEEDS}
    keys = {ws: (json.loads((C.RUNS / str(ws) / "keys.json").read_text())["items"]["NAME"] ==
                 json.loads((S1B1_ROOT / str(ws) / "keys.json").read_text())["items"]["NAME"]) for ws in W.WORLD_SEEDS}
    return {"caches": res, "name_items_equal": keys, "same": all(v["same"] for v in res.values()) and all(keys.values())}


# ================================================================================================ the test set (+ M2a)
class TestSetM(S.FixedTestSet):
    """S1c's fixed test set (NAME, M1), plus the M2a items (absent phrases) for the pollution prints' refusal pair, and the
    per-word naming of any ROAD."""

    def __init__(self, root: Path = C.RUNS):
        super().__init__(root)
        self.m2a = []
        for ws in W.WORLD_SEEDS:
            Q = json.loads((Path(root) / str(ws) / "questions.json").read_text())["questions"]
            K = json.loads((Path(root) / str(ws) / "keys.json").read_text())["items"]
            qm = {q["item_id"]: q for q in Q["M2a"]}
            th = self.per_seed[ws]["things"]
            for it in K["M2a"]:
                q = qm[it["item_id"]]
                self.m2a.append({**it, "ts": W.TEST_SEEDS[ws], "X": th.for_arm("A-RW", q["row"]), "phrase": list(q["phrase"])})

    def rates_reader(self, reader: MEM.StoreReader) -> Dict[str, Optional[float]]:
        """Per word: the reader's forced naming accuracy over the one-thing items carrying the word (an unnamed word is
        a miss — S1c's rule)."""
        names = {t: reader.names(self.name_X, ws)[0] for t, ws in TYPE_WORDS.items()}
        return {w: (float(np.mean([names[W.word_type(w)][i] == w for i in idx])) if idx else None)
                for w, idx in self.carry.items()}

    def pairs_of(self, names: Dict[str, List[Optional[str]]], tasks: Sequence[Sequence[str]]) -> Dict[int, List[int]]:
        """Per task i (1-based): the correctness of every held (item, word) pair of its words, in a FIXED order (the task's
        words in order, each word's items in the test set's order) — the GATE's paired difference reads these."""
        return {i + 1: [int(names[W.word_type(w)][k] == w) for w in T for k in self.carry[w]] for i, T in enumerate(tasks)}

    def pairs_rw(self, L, tasks: Sequence[Sequence[str]]) -> Dict[int, List[int]]:
        return self.pairs_of(self.names(L), tasks)

    def m2a_pair(self, reader: MEM.StoreReader) -> Dict[str, Optional[float]]:
        """The reader's «none» on M2a's absent phrases (refusal; 1 − it = false accepts) and on M1's covered graded
        present phrases (false refusal)."""
        ref = [bool(reader.answer_point(it["X"], it["phrase"], M.tie_rng(it["ts"], it["item_id"])).get("none"))
               for it in self.m2a if all(w in reader.type_of for w in it["phrase"])]
        fr = [bool(reader.answer_point(it["X"], it["phrase"], M.tie_rng(it["ts"], it["item_id"])).get("none"))
              for it in self.m1 if it["n_things"] >= 2 and it["covered"] and all(w in reader.type_of for w in it["phrase"])]
        return {"refusal": float(np.mean(ref)) if ref else None, "n_m2a": len(ref),
                "false_accept": (1.0 - float(np.mean(ref))) if ref else None,
                "false_refusal": float(np.mean(fr)) if fr else None, "n_m1": len(fr)}


# ================================================================================================ the LIFE
def scene_loss(L, X: np.ndarray, words: Sequence[str]) -> float:
    """A scene's own loss over the fixed 13 words BEFORE its update (the SURPRISE rank; pickers.window_loss's arithmetic)."""
    p = PK.hyp_probs(L, np.atleast_2d(X), VOCAB)
    P = 1.0 - np.prod(1.0 - p, axis=0) if p.shape[0] else np.zeros(len(VOCAB))
    P = np.clip(P, PK.P_CLIP, 1.0 - PK.P_CLIP)
    y = np.array([1.0 if w in words else 0.0 for w in VOCAB])
    return -float(np.sum(y * np.log(P) + (1.0 - y) * np.log(1.0 - P)))


def schedule_room(schedule: str, block: int, rooms: Sequence[str], picker, last: Dict[str, int], Lk: Dict[str, float]) -> Tuple[str, str]:
    if schedule == "seq":
        return rooms[(block - 1) // BLOCKS_PER_ROOM], "seq"
    if block <= len(rooms):
        return rooms[block - 1], "round-robin"
    return picker.pick(block, PK.Context(last_visit=dict(last), L_now=dict(Lk)))


def _read_roads(L, test: TestSetM, eps: float, em_resp, block: int, seed: int, which: Sequence[str]) -> Dict[str, object]:
    types = L.ear.cover(L.mature_words())
    rows = MEM.StoreRows.from_learner(L)
    out: Dict[str, object] = {}
    if not len(rows) or not types:
        return {r: None for r in which}
    if "READ" in which:
        out["READ"] = test.rates_reader(MEM.StoreReader(rows, types, eps))
    if "READ-NULL" in which:
        out["READ-NULL"] = test.rates_reader(MEM.StoreReader(rows.permuted_labels(substream(seed, f"labels:{seed}:{block}")), types, eps))
    if "TIME-WINDOW" in which:
        tw = rows.window(L.scenes - WINDOW_SCENES)
        out["TIME-WINDOW"] = test.rates_reader(MEM.StoreReader(tw, types, eps)) if len(tw) else None
    if "READ-EM" in which:
        out["READ-EM"] = test.rates_reader(MEM.StoreReader(MEM.StoreRows.from_learner(L, resp=em_resp), types, eps))
    return out


def life_m1(data, test: TestSetM, name: str, schedule: str, rooms: Sequence[str] = ROOMS, n_blocks: int = N_BLOCKS,
            eps: Optional[float] = None, log=None, truth=None) -> Dict[str, object]:
    """One training life of T-MEM-1 (module doc); `truth` (the grader's road: a (room, i) → the referent hypothesis map)
    is read ONLY by A-READ-EM's attribution diagnostic, offline, never by the learner."""
    sel, gate_kind = LIVES[name]
    eps = chosen_eps() if eps is None else float(eps)
    cpu0, wall0 = time.process_time(), time.time()
    seed, rooms = data.seed, list(rooms)
    windows = [data.window[r] for r in rooms]
    L = S.new_learner()
    picker = PK.RandomPicker(rooms, seed, prefix=PK.band_prefix(seed, BAND_STREAM_K)) if schedule == "random" else None
    cursor = {r: 0 for r in rooms}
    last = {r: 0 for r in rooms}
    buffer: List[Tuple[str, int]] = []
    by_room: Dict[str, List[int]] = {r: [] for r in rooms}
    by_word: Dict[str, List[Tuple[str, int]]] = {}
    scene_of: Dict[int, Tuple[str, int]] = {}
    err_at: Dict[Tuple[str, int], Tuple[float, int]] = {}
    term_at: Dict[str, float] = {}
    rate_at: Dict[str, float] = {}
    first_meet: Dict[str, int] = {}
    Lk = {r: PK.window_loss(L, data.window[r]) for r in rooms}
    table = [dict(Lk)]
    _wl, rates0 = test.words_learned(L)
    rates_rw = [rates0]
    roads: Dict[str, Dict[int, object]] = {r: {} for r in READ_ROADS}
    em_resp: Dict[Tuple[str, int], np.ndarray] = {}
    pairs: Dict[int, Dict[int, List[int]]] = {}
    em_diag: Dict[int, object] = {}
    pollution: Dict[int, object] = {}
    gate_obj = None
    gate_log: List[Dict[str, object]] = []
    rec: List[Dict[str, object]] = []
    for block in range(1, n_blocks + 1):
        room, flag = schedule_room(schedule, block, rooms, picker, last, Lk)
        start = cursor[room]
        said: Dict[str, None] = {}
        rises0 = gate_obj.rises if gate_obj is not None else 0
        for i in range(start, start + PK.BLOCK):
            X, words = data.visit_scene(room, i)
            if sel == "surprise":
                err_at[(room, i)] = (scene_loss(L, X, words), len(err_at))
            L.train_scene(X, words, referent=None, rng=substream(seed, f"episodic:room:{room}:visit:{i}"), project=gate_obj)
            scene_of[L.scenes] = (room, i)
            buffer.append((room, i))
            by_room[room].append(i)
            for w in dict.fromkeys(words):
                by_word.setdefault(w, []).append((room, i))
                said[w] = None
                first_meet.setdefault(w, block)
        cursor[room] += PK.BLOCK
        Lpost = {r: PK.window_loss(L, data.window[r]) for r in rooms}                     # (i) POST_b
        drop = Lk[room] - Lpost[room]
        weights: Dict[str, float] = {}
        if sel in ("drift", "drift-null"):
            terms = MEM.word_terms(L, windows, VOCAB)
            for w in said:
                term_at[w] = terms[w]
            weights = {w: terms[w] - term_at[w] for w in by_word}
            if sel == "drift-null":
                ws_ = sorted(weights)
                perm = substream(seed, f"drift-null:{seed}:{block}").permutation(len(ws_))
                weights = {ws_[k]: weights[ws_[int(perm[k])]] for k in range(len(ws_))}
        elif sel == "oracle-drift":
            _w, rp = test.words_learned(L)
            for w in said:
                rate_at[w] = rp[w]
            weights = {w: (rate_at[w] - rp[w]) if (rate_at.get(w) is not None and rp[w] is not None) else 0.0 for w in by_word}
        draws: List[Tuple[str, int]] = []
        if sel is not None:                                                                   # (ii) the REPLAY
            if sel == "uniform":
                draws = S2.replay_draws(seed, block, by_room, buffer, rooms, R_REPLAY, "room")
            elif sel == "surprise":
                top = sorted(err_at.items(), key=lambda kv: (-kv[1][0], kv[1][1]))[:R_REPLAY]
                draws = [k for k, _v in top]
            else:
                rng = substream(seed, f"replay:{seed}:{block}")
                el = sorted(by_word)
                wv = np.array([max(float(weights.get(w, 0.0)), 0.0) for w in el])
                for _ in range(R_REPLAY):
                    if wv.sum() > 0:
                        w = el[int(rng.choice(len(el), p=wv / wv.sum()))]
                    else:
                        w = el[int(rng.integers(len(el)))]
                    sc = by_word[w]
                    draws.append(sc[int(rng.integers(len(sc)))])
            replayed: Dict[str, None] = {}
            for q, i2 in draws:
                X, words = data.visit_scene(q, i2)
                L.train_scene(X, words, referent=None, rng=substream(seed, f"episodic:room:{q}:visit:{i2}"), project=gate_obj)
                scene_of[L.scenes] = (q, i2)
                for w in dict.fromkeys(words):
                    replayed[w] = None
            Lpre = {r: PK.window_loss(L, data.window[r]) for r in rooms}                    # (iii) PRE_(b+1)
            if sel in ("drift", "drift-null") and replayed:
                terms2 = MEM.word_terms(L, windows, VOCAB)
                for w in replayed:
                    term_at[w] = terms2[w]
            if sel == "oracle-drift" and replayed:
                _w2, rp2 = test.words_learned(L)
                for w in replayed:
                    rate_at[w] = rp2[w]
        else:
            Lpre = Lpost
        wl, rates = test.words_learned(L)                                                     # read after the replay (ruled)
        rates_rw.append(rates)
        if block in READ_POINTS:
            pairs[block] = test.pairs_rw(L, SHAPE_TASKS)
        row = {"block": block, "room": room, "flag": flag, "start": start, "L": Lpost, "drop": drop, "wl": wl}
        if sel is not None:
            row.update({"PRE": Lpre, "replay": [[q, int(i2)] for q, i2 in draws],
                        "replay_mix": {r: sum(1 for q, _i in draws if q == r) for r in rooms}})
            if weights:
                row["weights"] = {w: round(float(v), 6) for w, v in sorted(weights.items())}
        if gate_kind is not None:
            row["gate"] = {"strong": len(gate_obj.anchors) if gate_obj is not None else 0,
                           "rises": (gate_obj.rises - rises0) if gate_obj is not None else 0}
        # the answer roads (BASE only): READ at every boundary, the others at the room boundaries
        if name == "BASE":
            which = ["READ"] + (["READ-NULL", "TIME-WINDOW", "READ-EM"] if block in READ_POINTS else [])
            if block in READ_POINTS:
                rows_before = MEM.StoreRows.from_learner(L, resp=em_resp)
                types = L.ear.cover(L.mature_words())
                if len(rows_before) and types:
                    rd = MEM.StoreReader(rows_before, types, eps)
                    new_resp = rd.em_responsibilities()
                    em_diag[block] = em_diagnostic(L, rd, em_resp, new_resp, scene_of, truth)
                    em_resp = {**em_resp, **new_resp}
            got = _read_roads(L, test, eps, em_resp, block, seed, which)
            for k, v in got.items():
                roads[k][block] = v
            if block in (N_BLOCKS - BLOCKS_PER_ROOM, N_BLOCKS) and schedule == "seq":
                pollution[block] = pollution_prints(L, test, eps, scene_of)
        # the gate for the next block (strong words and anchors from this store, fixed for the block)
        if gate_kind is not None:
            types = L.ear.cover(L.mature_words())
            rows = MEM.StoreRows.from_learner(L)
            if len(rows) and types:
                rd = MEM.StoreReader(rows, types, eps)
                strong = rd.strong()
                anc = rd.anchors(strong) if gate_kind == "strong" else rd.random_anchors(strong, substream(seed, f"anchors:{seed}:{block}"))
                gate_obj = MEM.Gate(anc)
                rk = gate_obj.ranks(L)
                gate_log.append({"block": block, "strong": sorted(strong), "rank_stacked": rk["stacked"],
                                 "rank_per_word": rk["per_word"]})
        rec.append(row)
        table.append(dict(Lpost))
        Lk = Lpre
        last[room] = block
        if log is not None and block % 50 == 0:
            log(f"[{name} {schedule} {seed}] block {block}: wl {wl}")
    ans = test.points(L)
    full = test.m1_full(L, ans)
    pin = order_free_pin(L, test, eps) if name == "BASE" else None
    out = {"order_free_pin": pin, "seed": seed, "life": name, "schedule": schedule, "rooms": rooms, "n_blocks": n_blocks, "record": rec,
           "table": table, "rates_rw": rates_rw, "roads": roads, "em_diag": em_diag, "pollution": pollution,
           "gate_log": gate_log, "gate_steps": gate_obj.steps if gate_obj is not None else 0, "pairs": pairs,
           "gate_rises_total": sum(x["gate"]["rises"] for x in rec if "gate" in x),
           "first_meet": first_meet, "word_n": test.word_n, "m1_end": full["graded"], "eps": eps,
           "cpu_s": time.process_time() - cpu0, "wall_s": time.time() - wall0, "prereg": prereg_header(),
           "code": R.code_identity(), "store_rows_end": sum(x.shape[0] for xs in L.store_x for x in xs)}
    out["marks"] = marks_m1(out)
    return out


# ================================================================================================ the offline diagnostics
def _true_hyp(data_truth, room: str, i: int) -> Optional[int]:
    return data_truth.get((room, i)) if data_truth is not None else None


def em_diagnostic(L, reader: MEM.StoreReader, old: Dict, new: Dict, scene_of: Dict[int, Tuple[str, int]], truth) -> Dict[str, object]:
    """A-READ-EM's diagnostic per word (ruled): the fraction of meetings whose attributed row the pass CHANGED, and the
    attribution accuracy against the tape's truth before and after (offline; N's meetings, which have no referent, are
    excluded and counted)."""
    per: Dict[str, Dict[str, object]] = {}
    n_excluded = 0
    for j, w in enumerate(L.words):
        ch, acc_b, acc_a, n = 0, 0, 0, 0
        for m, (rs, ts, xs) in enumerate(zip(L.store_r[j], L.store_t[j], L.store_x[j])):
            before = old.get((w, m), rs)
            after = new.get((w, m), before)
            if len(before) > 1 and int(np.argmax(before)) != int(np.argmax(after)):
                ch += 1
            if truth is None:
                continue
            q, i = scene_of.get(int(ts), (None, None))
            th = truth.get((q, i)) if q is not None else None
            if th is None or q == "N":
                n_excluded += int(q == "N")
                continue
            if xs.shape[0] == 1:
                continue                                  # the episodic first meeting: one stored row, nothing to attribute
            n += 1
            acc_b += int(int(np.argmax(before)) == th)
            acc_a += int(int(np.argmax(after)) == th)
        k = len(L.store_r[j])
        per[w] = {"meetings": k, "changed": (ch / k) if k else None, "n_truth": n,
                  "acc_before": (acc_b / n) if n else None, "acc_after": (acc_a / n) if n else None}
    return {"per_word": per, "n_meetings_excluded_N": n_excluded}


def pollution_prints(L, test: TestSetM, eps: float, scene_of) -> Dict[str, object]:
    """CONCLUSION-MEMORY §3's prints at R3|N and the end: per word the raw class mean's distance from the grand mean (in a
    FIXED metric: the post-R3 store sd, applied by the caller), the band widths, the M2a pair, and N's per-word row counts."""
    rows = MEM.StoreRows.from_learner(L)
    types = L.ear.cover(L.mature_words())
    rd = MEM.StoreReader(rows, types, eps)
    grand = rows.X.mean(axis=0)
    mu_raw = {}
    for w in sorted(set(rows.word)):
        ii = np.asarray([k for k in range(len(rows)) if rows.word[k] == w], dtype=np.int64)
        rr = rows.r[ii]
        mu_raw[w] = ((rr[:, None] * rows.X[ii]).sum(axis=0) / rr.sum()).tolist()
    n_rows = {w: 0 for w in sorted(set(rows.word))}
    for k in range(len(rows)):
        q = scene_of.get(int(rows.t[k]), (None, None))[0]
        if q == "N":
            n_rows[rows.word[k]] += 1
    return {"grand": grand.tolist(), "mu_raw": mu_raw, "store_sd": rd.s.tolist(), "bands": dict(rd.band),
            "m2a": test.m2a_pair(rd), "n_rows_from_N": n_rows, "n_rows": {w: int(sum(1 for x in rows.word if x == w)) for w in n_rows}}


def shrinkage(p150: Dict[str, object], p200: Dict[str, object]) -> Dict[str, object]:
    """‖μ_w − μ̄‖ post-N / post-R3, both in the post-R3 store's sd (a fixed metric)."""
    s = np.asarray(p150["store_sd"])
    out = {}
    for w, mu in p150["mu_raw"].items():
        if w not in p200["mu_raw"]:
            continue
        a = np.linalg.norm((np.asarray(mu) - np.asarray(p150["grand"])) / s)
        b = np.linalg.norm((np.asarray(p200["mu_raw"][w]) - np.asarray(p200["grand"])) / s)
        out[w] = (b / a) if a > 0 else None
    vals = [v for v in out.values() if v is not None]
    return {"per_word": out, "mean": float(np.mean(vals)) if vals else None}


# ================================================================================================ the marks
def _pooled(rates: Dict[str, Optional[float]], words: Sequence[str], n: Dict[str, int]) -> Tuple[Optional[float], int]:
    c, t = 0.0, 0
    for w in words:
        if rates.get(w) is None or not n.get(w):
            continue
        c += rates[w] * n[w]
        t += n[w]
    return ((c / t) if t else None), t


def bwt_series(rates_by_block: Dict[int, Dict[str, Optional[float]]], tasks: Sequence[Sequence[str]], n: Dict[str, int]) -> Dict[str, object]:
    """R_{j,i} at the read points (j = 1..4 ↔ blocks 50/100/150/200) over task i's pooled held (item, word) pairs;
    BWT_j = mean over i < j of (R_{j,i} − R_{i,i}); SE_j = √(p(1 − p)/n) of the pooled accuracy after room j over the pairs
    of W_{<j} (ruled)."""
    Rm = {j: {i: _pooled(rates_by_block[READ_POINTS[j - 1]], tasks[i - 1], n)[0] for i in range(1, len(tasks) + 1)}
          for j in range(1, len(READ_POINTS) + 1) if READ_POINTS[j - 1] in rates_by_block and rates_by_block[READ_POINTS[j - 1]] is not None}
    out = {"R": Rm, "BWT": {}, "SE": {}}
    for j in range(2, len(READ_POINTS) + 1):
        if j not in Rm:
            continue
        diffs = [Rm[j][i] - Rm[i][i] for i in range(1, min(j, len(tasks) + 1)) if i in Rm and Rm[j][i] is not None and Rm[i][i] is not None]
        words = [w for i in range(1, min(j, len(tasks) + 1)) for w in tasks[i - 1]]
        p, nn = _pooled(rates_by_block[READ_POINTS[j - 1]], words, n)
        out["BWT"][j] = float(np.mean(diffs)) if diffs else None
        out["SE"][j] = math.sqrt(p * (1 - p) / nn) if (p is not None and nn) else None
    return out


def paired_gate(g: Dict[str, object], rnd: Dict[str, object], test_word_n: Dict[str, int], j: int = 3) -> Dict[str, object]:
    """The GATE's bar: BWT(strong) − BWT(random), post-R3, and the SE of the PAIRED difference over the same held
    (item, word) pairs: per pair x = (c_g,j − c_g,i) − (c_r,j − c_r,i); SE = √(Σ_i sd_i² / n_i) / (#tasks) — the SE of
    the mean of task means (declared). Needs the per-pair correctness series, carried as `pairs`."""
    xs_by_task = []
    for i in range(1, j):
        xs = np.asarray(g["pairs"][READ_POINTS[j - 1]][i]) - np.asarray(g["pairs"][READ_POINTS[i - 1]][i]) \
            - (np.asarray(rnd["pairs"][READ_POINTS[j - 1]][i]) - np.asarray(rnd["pairs"][READ_POINTS[i - 1]][i]))
        xs_by_task.append(xs)
    means = [float(x.mean()) for x in xs_by_task if len(x)]
    se = math.sqrt(sum((float(x.std(ddof=1)) ** 2) / len(x) for x in xs_by_task if len(x) > 1)) / max(1, len(xs_by_task))
    return {"diff": float(np.mean(means)) if means else None, "se": se, "n": [len(x) for x in xs_by_task]}


def marks_m1(run: Dict[str, object]) -> Dict[str, object]:
    n = run["word_n"]
    rw = {b: run["rates_rw"][b] for b in READ_POINTS if b < len(run["rates_rw"])}
    fm = run["first_meet"]
    full_tasks = [tuple(w for w in VOCAB if fm.get(w) is not None and (fm[w] - 1) // BLOCKS_PER_ROOM == i) for i in range(3)]
    out = {"RW": {"shape": bwt_series(rw, SHAPE_TASKS, n), "full": bwt_series(rw, full_tasks, n)},
           "full_tasks": [list(t) for t in full_tasks],
           "A": float(np.mean([sum(1 for w in VOCAB if (r.get(w) or 0) >= S.LEARNED_AT) for r in run["rates_rw"][1:]])) / len(VOCAB),
           "M1": run["m1_end"].get("covered")}
    w12 = [w for t in full_tasks[:2] for w in t]
    out["KEEP"] = _pooled(rw[150], w12, n)[0] if 150 in rw else None
    out["KEEP_shape"] = _pooled(rw[150], [w for t in SHAPE_TASKS[:2] for w in t], n)[0] if 150 in rw else None
    cont = [w for w in VOCAB if w not in {x for t in SHAPE_TASKS for x in t}]
    out["transfer_colour_size"] = {b: _pooled(rw[b], cont, n)[0] for b in rw}
    out["FWT"] = {j: _pooled(rw[READ_POINTS[j - 2]], SHAPE_TASKS[j - 1], n)[0] for j in (2, 3) if READ_POINTS[j - 2] in rw}
    for road, series in run["roads"].items():
        if series:
            rs = {b: v for b, v in series.items() if b in READ_POINTS and v is not None}
            if rs:
                out[road] = {"shape": bwt_series(rs, SHAPE_TASKS, n), "full": bwt_series(rs, full_tasks, n)}
    if run["roads"].get("READ"):
        rr = run["roads"]["READ"]
        out["A_READ"] = float(np.mean([sum(1 for w in VOCAB if (rr[b] or {}).get(w, 0) is not None and ((rr[b] or {}).get(w) or 0) >= S.LEARNED_AT)
                                       for b in sorted(rr)])) / len(VOCAB)
    return out


# ================================================================================================ the grader's road: truth
def room_truth_map(data, root: Path, seed: int, rooms: Sequence[str] = ("R1", "R2", "R3")) -> Dict[Tuple[str, int], Optional[int]]:
    """GRADING ONLY (A-READ-EM's offline diagnostic): per consumed visit scene of a learnable room, the index of the
    hypothesis that covers the utterance's referent (marks.thing_hypothesis; None when the gaze missed it). N's scenes
    have no referent and are absent (counted apart by the diagnostic)."""
    out: Dict[Tuple[str, int], Optional[int]] = {}
    for r in rooms:
        tr = RM.load_room_truth(RM.room_cache_dir(root, seed, r, "visit"))
        th = data.visit[r]
        for row in tr:
            i = int(row["row"])
            mem, pos = th.members(i)
            ref = row.get("referent")
            out[(r, i)] = None if ref is None else M.thing_hypothesis(int(ref), mem, pos, row["fix_thing"], tuple(row["centroids"][int(ref)]))
    return out


# ================================================================================================ loading
def _intkeys(d):
    if isinstance(d, dict):
        return {(int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): _intkeys(v) for k, v in d.items()}
    if isinstance(d, list):
        return [_intkeys(x) for x in d]
    return d


def load_run(p: Path) -> Optional[Dict[str, object]]:
    if not p.exists():
        return None
    r = json.loads(p.read_text())
    for k in ("pairs", "roads", "em_diag", "pollution"):
        if k in r:
            r[k] = _intkeys(r[k])
    r["marks"] = marks_m1(r)
    return r


def run_path(root: Path, seed: int, schedule: str, life: str) -> Path:
    return Path(root) / str(seed) / "runs" / schedule / f"{life}.json"


# ================================================================================================ THE FIRST GATE
def gate_toy() -> Dict[str, object]:
    """Step 3's first pin: a two-word toy (dimension 6). A strong word with 3 anchors; one delta step, gated and ungated;
    the anchors' losses under one standardisation: gated → unchanged (to 1e-12), ungated → moved."""
    from . import learners as Lr
    rng = np.random.default_rng(0)
    L = Lr.RWLearner(lr=0.5, dim=6)
    for i in range(30):
        X = rng.normal(size=(1, 6)) + (np.array([[3, 0, 0, 0, 0, 0]]) if i % 2 == 0 else np.array([[0, 3, 0, 0, 0, 0]]))
        L.train_scene(X, ["a"] if i % 2 == 0 else ["b"], rng=np.random.default_rng(i))
    anchors_raw = np.array([[3.0, 0, 0, 0, 0, 0], [3.2, 0.1, 0, 0, 0, 0], [2.9, -0.1, 0.1, 0, 0, 0]])
    A = np.hstack([L.stats.standardise(anchors_raw), np.ones((3, 1))])
    j = L.index["a"]

    def anchor_loss(LL):
        lg = A @ np.concatenate([LL.V[j], [LL.b[j]]])
        return float(np.sum(np.logaddexp(0.0, -lg)))

    X = np.array([[0.5, 2.5, 0.3, 0, 0, 0]])                   # a scene that says «a» off its anchors
    out = {}
    for kind in ("ungated", "gated"):
        LL = copy.deepcopy(L)
        stats_before = copy.deepcopy(LL.stats)
        g = MEM.Gate({"a": anchors_raw}) if kind == "gated" else None
        before = anchor_loss(LL)
        # the step under the learner's own road; the anchors re-read under the SAME standardisation the step used
        LL.train_scene(X, ["a"], rng=np.random.default_rng(99), project=g)
        A2 = np.hstack([LL.stats.standardise(anchors_raw), np.ones((3, 1))])
        lg_b = A2 @ np.concatenate([L.V[j], [L.b[j]]])
        lg_a = A2 @ np.concatenate([LL.V[j], [LL.b[j]]])
        out[kind] = {"change": float(np.sum(np.logaddexp(0.0, -lg_a)) - np.sum(np.logaddexp(0.0, -lg_b))),
                     "rises": (g.rises if g is not None else None), "steps": (g.steps if g is not None else None)}
        _ = (before, stats_before)
    out["pass"] = abs(out["gated"]["change"]) < 1e-12 and abs(out["ungated"]["change"]) > 1e-6 and out["gated"]["rises"] == 0
    return out


def first_gate(root: Path = ROOT, log=print) -> Dict[str, object]:
    """PREREG-TMEM1 §3, each step a STOP on a miss (printed whole)."""
    out: Dict[str, object] = {"verdict": "STOP"}
    lines: List[str] = []

    def say(s: str) -> None:
        lines.append(s)
        log(s)

    def stop(step: str) -> Dict[str, object]:
        say(f"   STOP at {step}")
        out["lines"] = lines
        return out

    shas = check_prereg()
    eps = chosen_eps()
    out.update({"shas": shas, "eps": eps})
    say(f"THE FIRST GATE (T-MEM-1) — PREREG-TMEM1 {shas['prereg_tmem1'][:12]}… · CONCLUSION-MEMORY {shas['conclusion_memory'][:12]}… · "
        f"PREREG-S1C2 {shas['prereg_s1c2'][:12]}… · PREREG-S1C {shas['prereg_s1c'][:12]}… · AMENDMENT 1 {shas['amend1_s1c'][:12]}… · "
        f"code {R.code_identity()['code_sha_file']} · ε = {eps} (P-ORACLE's)")
    # 1. identity: the pools and the test set as files, then S1c-2's three arms re-run on this tree
    pools = {s: pools_identical(root, s) for s in SEEDS}
    ts = test_set_identical()
    data = S.RoomData(root, GATE_SEED, ROOMS)
    test2 = S.FixedTestSet()
    diffs, side = {}, {}
    for arm in ("PROGRESS", "RANDOM", "RANDOM+REPLAY"):
        new = S2.life2(data, test2, arm)
        old = json.loads(S2.run_path(S1C2_ROOT, GATE_SEED, arm).read_text())
        diffs[arm] = S2.identity_diff(new, old)
        side[arm] = {k: (str(v[0])[:50], str(v[1])[:50]) for k, v in S2.masked_side_by_side(new, old).items()}
    out["step1"] = {"pools": {s: pools[s]["same"] for s in SEEDS}, "test_set": ts["same"], "diffs": diffs}
    say(f"1. identity — the redrawn pools against S1c's (canvas shas, specs, glances), every pool of every seed: "
        + " · ".join(f"{s} {'EQUAL' if pools[s]['same'] else 'DIFFERENT'}" for s in SEEDS)
        + f" · the fixed test set as the merged code reads it (S1b-1R's redraw) against S1b-1's own: {'EQUAL' if ts['same'] else 'DIFFERENT'} "
        + f"· S1c-2's arms re-run on this tree at {GATE_SEED}: " + " · ".join(f"{a} {'EQUAL' if not d else 'DIFFERS in ' + str(d)}" for a, d in diffs.items()))
    for a, v in side.items():
        say(f"   the masked fields of {a} (S1c-2 | this tree): " + " · ".join(f"{k}: {x[0]} | {x[1]}" for k, x in v.items()))
    if not all(p["same"] for p in pools.values()) or not ts["same"] or any(diffs.values()):
        return stop("step 1 (another tree, not another result)")
    # 2. THE ORDER-FREE PIN, per seed, on A-READ's final store (the BASE life under the sequential schedule)
    test = TestSetM()
    pins = {}
    bases = {}
    for s in SEEDS:
        d = S.RoomData(root, s, ROOMS)
        truth = room_truth_map(d, root, s)
        b = life_m1(d, test, "BASE", "seq", eps=eps, truth=truth, log=log)
        bases[s] = b
        R.dump(Path(root) / "gate" / "step2" / f"BASE-seq-{s}.json", b)
        pins[s] = b["order_free_pin"]
    out["step2"] = pins
    say("2. THE ORDER-FREE PIN — A-READ's final store per seed: the rows shuffled (each keeping its word, responsibility and raw "
        "input), the reader rebuilt; every held item's forced name and margin: " + " · ".join(
            f"{s} names equal {p['names_equal']}, max |Δ margin| {p['max_margin_diff']:.1e} ({p['n_rows']} rows)" for s, p in pins.items()))
    if not all(p["pass"] for p in pins.values()):
        return stop("step 2")
    # 3. the gate's own pins
    toy = gate_toy()
    out["step3"] = toy
    say(f"3. the gate's pins — a two-word toy, one delta step on a scene off the anchors: the anchors' loss change gated "
        f"{toy['gated']['change']:.2e} (rises {toy['gated']['rises']}) · ungated {toy['ungated']['change']:+.4f} → "
        f"{'PASS' if toy['pass'] else 'MISS'} (the rise count is logged per block in every GATE life)")
    if not toy["pass"]:
        return stop("step 3")
    # 4. TIME-WINDOW's positive control at seed 20261301
    tw = bases[GATE_SEED]["marks"].get("TIME-WINDOW", {}).get("shape", {})
    bwt3, se3 = tw.get("BWT", {}).get(3), tw.get("SE", {}).get(3)
    ok4 = bwt3 is not None and se3 is not None and bwt3 < -SIDAK_Z * se3
    out["step4"] = {"bwt": bwt3, "se": se3, "pass": ok4}
    say(f"4. TIME-WINDOW's positive control at {GATE_SEED}: post-R3 BWT (the rooms' own shape words) {S._fmt(bwt3, 4)} against the "
        f"floor −2.4 × SE {S._fmt(-SIDAK_Z * se3 if se3 is not None else None, 4)} → {'BELOW (the mark can fail): PASS' if ok4 else 'MISS: the test is VOID'}")
    if not ok4:
        return stop("step 4 (the test is VOID)")
    # 5. the 20-block smoke of every life, both schedules
    d1 = S.RoomData(root, GATE_SEED, ROOMS)
    say(f"5. the {SMOKE_BLOCKS}-block smoke of every life under both schedules, each record whole:")
    for sch in SCHEDULES:
        for name in LIVES:
            r = life_m1(d1, test, name, sch, n_blocks=SMOKE_BLOCKS, eps=eps)
            R.dump(Path(root) / "gate" / "smoke" / f"{name}-{sch}.json", r)
            for ln in smoke_lines(r):
                say(ln)
    out["verdict"] = "PROCEED"
    say("THE FIRST GATE: PROCEED")
    out["lines"] = lines
    return out


def order_free_pin(L, test: TestSetM, eps: float) -> Dict[str, object]:
    """THE ORDER-FREE PIN on a learner's final store: the rows shuffled (each keeping its word, responsibility and raw
    input), the reader rebuilt; every held item's forced name must be identical and every margin equal within 1e-9."""
    types = L.ear.cover(L.mature_words())
    rows = MEM.StoreRows.from_learner(L)
    a = MEM.StoreReader(rows, types, eps)
    b = MEM.StoreReader(rows.shuffled(np.random.default_rng(20261310)), types, eps)
    eq, md = True, 0.0
    for t, ws in TYPE_WORDS.items():
        na, ma = a.names(test.name_X, ws)
        nb, mb = b.names(test.name_X, ws)
        eq = eq and na == nb
        fin = np.isfinite(ma) & np.isfinite(mb)
        if fin.any():
            md = max(md, float(np.max(np.abs(ma[fin] - mb[fin]))))
        eq = eq and bool(np.all(np.isfinite(ma) == np.isfinite(mb)))
    return {"names_equal": eq, "max_margin_diff": md, "n_rows": len(rows), "pass": bool(eq and md <= PIN_TOL)}


def smoke_lines(run: Dict[str, object]) -> List[str]:
    out = [f"   {run['life']} ({run['schedule']}) — seed {run['seed']}"]
    for x in run["record"]:
        extra = ""
        if "replay" in x:
            extra += " · replay " + ",".join(f"{q}:{i}" for q, i in x["replay"])
        if "weights" in x:
            extra += " · weights " + " ".join(f"{w}:{v:+.3f}" for w, v in x["weights"].items())
        if "gate" in x:
            extra += f" · gate strong {x['gate']['strong']} rises {x['gate']['rises']}"
        out.append(f"   b{x['block']:>3} {x['room']:<2} {x['flag']:<11} start {x['start']:>4} · L " + " ".join(
            f"{r}:{v:.3f}" for r, v in x["L"].items()) + f" · drop {x['drop']:+.4f} · wl {x['wl']}{extra}")
    return out


def gate_ok(root: Path = ROOT) -> Dict[str, object]:
    p = Path(root) / "gate" / "first_gate.json"
    if not p.exists():
        raise TmemError(f"{p} is missing — THE FIRST GATE has not run")
    g = json.loads(p.read_text())
    if g.get("verdict") != "PROCEED":
        raise TmemError(f"THE FIRST GATE reads {g.get('verdict')} — no life")
    return g


# ================================================================================================ the price
def price(root: Path = ROOT, log=print) -> Dict[str, object]:
    """Solo, at seed 20261301 under the sequential schedule: one life of each kind; the projection for the unit: 8 lives
    × 2 schedules × 3 seeds (the pools are drawn before the gate)."""
    check_prereg()
    gate_ok(root)
    eps = chosen_eps()
    data = S.RoomData(root, GATE_SEED, ROOMS)
    test = TestSetM()
    truth = room_truth_map(data, root, GATE_SEED)
    cpu = {}
    for name in LIVES:
        r = life_m1(data, test, name, "seq", eps=eps, truth=truth if name == "BASE" else None)
        cpu[name] = r["cpu_s"]
        log(f"[price] {name}: {r['cpu_s']:.1f} CPU-s ({r['wall_s']:.1f} s wall)")
    total = 2 * 3 * sum(cpu.values())
    out = {"cpu_s": cpu, "unit_cpu_min": total / 60.0}
    log(f"[price] THE UNIT: 8 lives × 2 schedules × 3 seeds = 48 lives ≈ {total / 60:.1f} CPU-min (the pools already drawn; "
        f"PREREG-TMEM1 §5 estimated 12–15)")
    R.dump(Path(root) / "price" / "price.json", out)
    return out


# ================================================================================================ the report
def _floor(se: Optional[float]) -> Optional[float]:
    return None if se is None else -SIDAK_Z * se


def report(root: Path = ROOT, log=print) -> Dict[str, object]:
    shas = check_prereg()
    gate_ok(root)
    runs = {sch: {s: {n: load_run(run_path(root, s, sch, n)) for n in LIVES} for s in SEEDS} for sch in SCHEDULES}
    missing = [f"{n}@{sch}:{s}" for sch in SCHEDULES for s in SEEDS for n in LIVES if runs[sch][s][n] is None]
    L: List[str] = []
    L.append(f"T-MEM-1 «THE BRAIN READS ITS MEMORY» — the report · PREREG-TMEM1 {shas['prereg_tmem1'][:12]}… · CONCLUSION-MEMORY "
             f"{shas['conclusion_memory'][:12]}… · THE LAW'S WORLD {list(ROOMS)} · (a) SEQUENTIAL R1→R2→R3→N × 50 blocks · (b) RANDOM "
             f"(random-band:<seed>:{BAND_STREAM_K}) · R = {R_REPLAY}")
    if missing:
        L.append(f"NOT GRADABLE BY NAME — lives missing: {missing}")
    seq = runs["seq"]
    L.append("")
    L.append("THE BARS (schedule (a); every seed; the BARRED BWT on each room's own SHAPE words, PREREG-TMEM1 §1 as co-signed):")
    # A-READ, with A-RW as the world's positive control
    rw_below, aread = {}, {}
    for s in SEEDS:
        b = seq[s]["BASE"]
        if b is None:
            continue
        m = b["marks"]
        rw, rd = m["RW"]["shape"], m.get("READ", {}).get("shape", {})
        f3 = _floor(rw["SE"].get(3))
        rw_below[s] = rw["BWT"].get(3) is not None and f3 is not None and rw["BWT"][3] < f3
        ok = {}
        for j in (2, 3):
            fj = _floor(rd.get("SE", {}).get(j))
            v = rd.get("BWT", {}).get(j)
            ok[j] = v is not None and fj is not None and v >= fj
        aread[s] = ok
        L.append(f"   {s}: A-READ post-R2 BWT {S._fmt(rd.get('BWT', {}).get(2), 4)} vs {S._fmt(_floor(rd.get('SE', {}).get(2)), 4)} "
                 f"{'PASS' if ok[2] else 'FAIL'} · post-R3 {S._fmt(rd.get('BWT', {}).get(3), 4)} vs {S._fmt(_floor(rd.get('SE', {}).get(3)), 4)} "
                 f"{'PASS' if ok[3] else 'FAIL'} · A-RW (the world's positive control) post-R3 {S._fmt(rw['BWT'].get(3), 4)} vs "
                 f"{S._fmt(f3, 4)} {'BELOW (forgetting exists)' if rw_below[s] else 'NOT below'}")
    n_below = sum(1 for v in rw_below.values() if v)
    aread_pass = aread and all(all(v.values()) for v in aread.values())
    verdict_read = ("NOT GRADABLE BY NAME" if any(seq[s]["BASE"] is None for s in SEEDS) else
                    "VOID (A-RW did not forget below the floor at ≥ 2 seeds)" if n_below < 2 else ("PASS" if aread_pass else "FAIL"))
    L.append(f"   A-READ: {verdict_read} (A-RW below the floor at {n_below} of 3 seeds)")
    # DRIFT
    dd = {}
    for s in SEEDS:
        k = {n: (seq[s][n]["marks"]["KEEP"] if seq[s][n] else None) for n in ("DRIFT", "ORACLE-DRIFT", "DRIFT-NULL", "UNIFORM")}
        ok = None if None in (k["DRIFT"], k["ORACLE-DRIFT"]) else k["DRIFT"] >= KEEP_FRACTION * k["ORACLE-DRIFT"]
        nm = None if None in (k["DRIFT-NULL"], k["ORACLE-DRIFT"]) else k["DRIFT-NULL"] >= KEEP_FRACTION * k["ORACLE-DRIFT"]
        dd[s] = (ok, nm)
        L.append(f"   {s}: A-RW + DRIFT KEEP {S._fmt(k['DRIFT'], 4)} vs 0.90 × ORACLE-DRIFT's {S._fmt(k['ORACLE-DRIFT'], 4)} → "
                 f"{'PASS' if ok else 'FAIL' if ok is not None else 'NOT GRADABLE'} · the drift-permuted null {S._fmt(k['DRIFT-NULL'], 4)} "
                 f"{'MEETS it' if nm else 'does not meet it'} · UNIFORM {S._fmt(k['UNIFORM'], 4)}")
    n_null = sum(1 for _o, nm in dd.values() if nm)
    verdict_drift = ("NOT GRADABLE BY NAME" if any(o is None for o, _n in dd.values()) else "VOID (the null meets it at ≥ 2 seeds)"
                     if n_null >= 2 else ("PASS" if all(o for o, _n in dd.values()) else "FAIL"))
    L.append(f"   A-RW + DRIFT: {verdict_drift}")
    # the GATE
    gp = {}
    for s in SEEDS:
        g, rnd = seq[s]["GATE"], seq[s]["GATE-RANDOM"]
        if g is None or rnd is None:
            gp[s] = None
            continue
        pg = paired_gate(g, rnd, g["word_n"])
        ok = pg["diff"] is not None and pg["diff"] >= GATE_SE * pg["se"]
        gp[s] = ok
        L.append(f"   {s}: GATE − GATE-RANDOM post-R3 BWT (shape words) {S._fmt(pg['diff'], 4)} vs 2 × the paired SE "
                 f"{S._fmt(GATE_SE * pg['se'], 4)} (n {pg['n']}) → {'PASS' if ok else 'FAIL'} · the anchors' stacked rank "
                 f"{max((x['rank_stacked'] for x in g['gate_log']), default=0)} (against 144) · steps with an anchor's loss risen "
                 f"{g['gate_rises_total']} (null 0)")
    n_gate = sum(1 for v in gp.values() if v)
    verdict_gate = "NOT GRADABLE BY NAME" if any(v is None for v in gp.values()) else ("PASS" if n_gate >= 2 else "FAIL")
    L.append(f"   the GATE: {verdict_gate} (at {n_gate} of 3 seeds; the bar asks ≥ 2)")
    L.append("")
    L.append("the BWT series (read points after R1 / R2 / R3 / N; the barred shape-word series and the full W_i beside) per road, both schedules:")
    for sch in SCHEDULES:
        for s in SEEDS:
            for n in LIVES:
                r = runs[sch][s][n]
                if r is None:
                    L.append(f"   {sch} {s} {n}: NOT GRADABLE BY NAME")
                    continue
                m = r["marks"]
                roads = ["RW"] + ([x for x in ("READ", "READ-NULL", "READ-EM", "TIME-WINDOW") if x in m] if n == "BASE" else [])
                for road in roads:
                    sh, fu = m[road]["shape"], m[road]["full"]
                    L.append(f"   {sch} {s} {n:<12} {road:<11} BWT shape " + " ".join(
                        f"{j}:{S._fmt(sh['BWT'].get(j), 3)}±{S._fmt(sh['SE'].get(j), 3)}" for j in (2, 3, 4))
                        + " · full " + " ".join(f"{j}:{S._fmt(fu['BWT'].get(j), 3)}" for j in (2, 3, 4))
                        + (f" · A {m['A']:.3f} · M1 {S._fmt(m['M1'])} · KEEP {S._fmt(m['KEEP'])} (shape {S._fmt(m['KEEP_shape'])}) · FWT "
                           + " ".join(f"{j}:{S._fmt(v)}" for j, v in m["FWT"].items()) if road == "RW" else ""))
    L.append("")
    L.append("the readings (no bar):")
    for s in SEEDS:
        b = seq[s]["BASE"]
        if b is None:
            continue
        tr = b["marks"]["transfer_colour_size"]
        L.append(f"   {s}: the continuing colour/size words' held naming after R1 / R2 / R3 / N (a transfer reading): "
                 + " ".join(f"{k}:{S._fmt(v)}" for k, v in sorted(tr.items())) + " · held items per word n: "
                 + " ".join(f"{w} {b['word_n'][w]}" for w in VOCAB))
        if b["pollution"].get(150) and b["pollution"].get(200):
            sk = shrinkage(b["pollution"][150], b["pollution"][200])
            p1, p2 = b["pollution"][150], b["pollution"][200]
            L.append(f"      N-POLLUTION (CONCLUSION §3): the class-mean shrinkage ratio post-N / post-R3 mean {S._fmt(sk['mean'])} (predicted ≈ 0.75) "
                     "· per word " + " ".join(f"{w} {S._fmt(v)}" for w, v in sorted(sk["per_word"].items())))
            L.append(f"      the band widths post-R3 → post-N: " + " ".join(
                f"{w} {S._fmt(p1['bands'].get(w))}→{S._fmt(p2['bands'].get(w))}" for w in sorted(p2["bands"])))
            L.append(f"      M2a (the READER's «none»): refusal {S._fmt(p1['m2a']['refusal'])} → {S._fmt(p2['m2a']['refusal'])} (false accepts "
                     f"{S._fmt(p1['m2a']['false_accept'])} → {S._fmt(p2['m2a']['false_accept'])}) · false refusal on M1 {S._fmt(p1['m2a']['false_refusal'])} → "
                     f"{S._fmt(p2['m2a']['false_refusal'])} · N's rows per word at the end: " + " ".join(
                         f"{w} {v}" for w, v in sorted(p2["n_rows_from_N"].items())))
        for blk, dg in sorted(b["em_diag"].items()):
            pw = dg["per_word"]
            L.append(f"      A-READ-EM at block {blk}: changed " + " ".join(f"{w} {S._fmt(v['changed'])}" for w, v in pw.items() if v["meetings"])
                     + " · attribution accuracy before→after " + " ".join(
                         f"{w} {S._fmt(v['acc_before'])}→{S._fmt(v['acc_after'])}" for w, v in pw.items() if v["n_truth"])
                     + f" · N's meetings excluded {dg['n_meetings_excluded_N']}")
        L.append(f"      the ORDER-FREE PIN on the unit's own BASE life: {b['order_free_pin']}")
    L.append("")
    L.append("the refutations (§4):")
    n_read_fail = sum(1 for s in SEEDS if seq[s]["BASE"] and not aread.get(s, {}).get(3, True))
    L.append(f"   A-READ's post-R3 BWT below the floor at ≥ 2 seeds: at {n_read_fail} → {'REFUTED' if n_read_fail >= 2 else 'not refuted'}")
    le = [s for s in SEEDS if seq[s]["DRIFT"] and seq[s]["UNIFORM"] and seq[s]["DRIFT"]["marks"]["KEEP"] <= seq[s]["UNIFORM"]["marks"]["KEEP"]]
    L.append(f"   DRIFT ≤ UNIFORM on KEEP at seeds {le or 'none'}; the null meets DRIFT's bar at {n_null} seed(s)")
    rk = [max((x['rank_stacked'] for x in seq[s]['GATE']['gate_log']), default=0) for s in SEEDS if seq[s]['GATE']]
    L.append(f"   the gate's stacked anchor rank > 100: max {max(rk) if rk else '—'} → {'REFUTED' if rk and max(rk) > 100 else 'not refuted'}")
    txt = "\n".join(L)
    (Path(root) / "report.txt").write_text(txt + "\n")
    R.dump(Path(root) / "report.json", {"verdicts": {"A-READ": verdict_read, "DRIFT": verdict_drift, "GATE": verdict_gate},
                                        "missing": missing, "shas": shas})
    for ln in L:
        log(ln)
    return {"A-READ": verdict_read, "DRIFT": verdict_drift, "GATE": verdict_gate}


# ================================================================================================ the CLI
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="brain.scene.run_tmem1")
    ap.add_argument("cmd", choices=["check", "pools", "first-gate", "run", "price", "report"])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--seed", type=int)
    ap.add_argument("--life", choices=list(LIVES))
    ap.add_argument("--schedule", choices=list(SCHEDULES), default="seq")
    a = ap.parse_args(argv)
    root = Path(a.root)
    log = R.Log(root / "logs" / f"{a.cmd}.log")
    if a.cmd == "check":
        log(json.dumps(check_prereg()))
        return 0
    check_prereg()
    if a.cmd == "pools":
        t0 = time.process_time()
        res = build_pools(root, a.seed, log=log)
        same = all(v["same"] for v in res.values())
        log(f"[pools {a.seed}] {len(res)} pools, every one EQUAL to S1c's: {same} · {time.process_time() - t0:.1f} CPU-s")
        return 0 if same else 11
    if a.cmd == "first-gate":
        g = first_gate(root, log=log)
        R.dump(root / "gate" / "first_gate.json", g)
        (root / "gate" / "first_gate.out").write_text("\n".join(g.get("lines", [])) + "\n")
        return 0 if g["verdict"] == "PROCEED" else 10
    if a.cmd == "run":
        gate_ok(root)
        data = S.RoomData(root, a.seed, ROOMS)
        test = TestSetM()
        truth = room_truth_map(data, root, a.seed) if a.life == "BASE" else None
        r = life_m1(data, test, a.life, a.schedule, truth=truth, log=log)
        R.dump(run_path(root, a.seed, a.schedule, a.life), r)
        log(f"[run {a.life} {a.schedule} {a.seed}] A {r['marks']['A']:.3f} · KEEP {S._fmt(r['marks']['KEEP'])} · {r['cpu_s']:.1f} CPU-s")
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
