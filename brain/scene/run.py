"""run.py — S1a's runner (PREREG-R3-TONIGHT §S1a): the caches, stage −1, the toy, THE FIRST GATE, the prices, the full
run's arms and the grader. Everything runs under /usr/bin/python3 (the eye's interpreter; no arm needs torch).

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:20 +0400 — new module.

  python3 -m brain.scene.run cache --split S [--world-seed W]     one cache (written once)
  python3 -m brain.scene.run cache-world --world-seed W           train + test + m2b + m6 and the disjointness record
  python3 -m brain.scene.run questions --world-seed W             the questions (what an arm hears) and the keys (grader)
  python3 -m brain.scene.run stage                                stage −1's organ facts (printed only)
  python3 -m brain.scene.run first-gate                           the toy, ε, the instrument verdict, 6 arms × 300 vs N-SHUF
  python3 -m brain.scene.run arm --arm A --world-seed W           one arm over its stream, answering at every reading point
  python3 -m brain.scene.run grade --world-seed W                 the marks of every arm at every reading point
  python3 -m brain.scene.run report                               the headline table across seeds, the bars, the verdicts
  python3 -m brain.scene.run price                                solo, then the launch's shape (6 arms × 3 seeds at once)

Only this module and marks.py read the truth. The truth enters an ORACLE arm's feed here, as an index (the referent's
thing hypothesis, or the referent thing for ORACLE-TRUTH), and A-RW / N-SHUF never have it read on their behalf.

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:05 +0400 — AMENDMENT 2 (docs/brain/r3/PREREG-R3-TONIGHT-AMEND-2.md in genome-wt-brain3,
d54e6c0, sha checked beside the signed PREREG's): P-ORACLE / ORACLE-TRUTH read with the TYPE-AWARE reader (the word types
passed in from here — the oracle may know them); M1's bars on the 2- and 3-thing items; M6 only where the meeting was seen;
an unheard word NOT GRADABLE; the reading arm A-RW-LR01 (lr 0.01, no bar) beside A-RW. Six arms × three seeds.
edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:17 +0400 — after the full run: a mark with n < 30 at a seed READS UNDERPOWERED
(the signed PREREG); M2a's CEILING-BOUND read per half (the learner's failing half must be one the oracle fails
too — declared, RAISED); the report's «all seeds» counts a seed only where the mark reads PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.world.seeds import substream

from . import AMEND2_SHA256, PREREG_SHA256
from . import cache as C
from . import learners as Lr
from . import marks as M
from . import world as W

ARMS: Tuple[str, ...] = ("A-RW", "A-RW-LR01", "N-SHUF", "P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH")
RW_ARMS = ("A-RW", "A-RW-LR01", "N-SHUF", "P-ORACLE-RW")
LDA_ARMS = ("P-ORACLE", "ORACLE-TRUTH")
ORACLE_ARMS = ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH")        # the only arms whose feed carries a referent index
READING_ARMS = ("A-RW-LR01",)                                     # AMENDMENT 2 §5: printed beside A-RW, no bar
ARM_LR = {"A-RW-LR01": 0.01}                                      # its ONE difference from A-RW
PREREG_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-R3-TONIGHT.md")
AMEND2_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-R3-TONIGHT-AMEND-2.md")
TYPE_WORDS = {"shape": list(W.SHAPES), "colour": list(W.COLOUR_NAMES), "size": list(W.SIZE_NAMES)}
WORD_TYPES = {w: W.word_type(w) for w in W.VOCAB}                 # what the ORACLE may know (AMENDMENT 2 §1)


class RunError(Exception):
    pass


# ------------------------------------------------------------------------------------------------ plumbing
def check_prereg() -> str:
    got = hashlib.sha256(PREREG_PATH.read_bytes()).hexdigest()
    if got != PREREG_SHA256:
        raise RunError(f"PREREG sha256 {got} ≠ the signed {PREREG_SHA256} — STOP and hand back")
    am = hashlib.sha256(AMEND2_PATH.read_bytes()).hexdigest()
    if am != AMEND2_SHA256:
        raise RunError(f"AMENDMENT 2 sha256 {am} ≠ the one this code implements {AMEND2_SHA256} — STOP and hand back")
    return got


def code_identity() -> Dict[str, object]:
    here = Path(__file__).resolve().parent
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(here.glob("*.py"))}
    stamp = here.parents[1] / "CODE_SHA"
    return {"code_sha_file": stamp.read_text().strip() if stamp.exists() else None, "files": files,
            "root": str(here.parents[1]), "python": sys.executable}


class Log:
    def __init__(self, path: Optional[Path] = None):
        self.f = None
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            self.f = open(path, "a", buffering=1, encoding="utf-8")

    def __call__(self, msg: str) -> None:
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
        print(line, flush=True)
        if self.f is not None:
            self.f.write(line + "\n")


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True, default=_jsonable) + "\n")
    tmp.replace(path)


def _jsonable(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def seed_root(root: Path, ws: int) -> Path:
    return Path(root) / str(ws)


# ------------------------------------------------------------------------------------------------ things per scene
class Things:
    """A split's things in view, per scene, as each arm kind reads them: gaze hypotheses ([144 ‖ y/16, x/16] for the RW
    arms, the 144 for P-ORACLE) or the forced windows (ORACLE-TRUTH)."""

    def __init__(self, percepts: C.ScenePercepts):
        self.p = percepts
        self._h: Dict[int, tuple] = {}

    def hyps(self, row: int):
        h = self._h.get(row)
        if h is None:
            hs = self.p.hypotheses(row)
            feats = np.stack([x.feat for x in hs]) if hs else np.zeros((0, 144))
            pos = np.array([x.pos for x in hs], dtype=np.float64).reshape(-1, 2)
            h = ([x.members for x in hs], feats, pos)
            self._h[row] = h
        return h

    def members(self, row: int):
        m, _f, pos = self.hyps(row)
        return m, [tuple(p) for p in pos]

    def for_arm(self, arm: str, row: int) -> np.ndarray:
        if arm == "ORACLE-TRUTH":
            return self.p.forced(row)
        _m, feats, pos = self.hyps(row)
        if arm == "P-ORACLE":
            return feats
        return Lr.feed_rw(feats, pos)


def referent_index(arm: str, things: Things, truth_row: Dict[str, object]) -> Optional[int]:
    """THE ONE PLACE truth meets a learner: an oracle arm's referent, as an index. P-ORACLE-RW / P-ORACLE: the referent's
    thing hypothesis (marks.thing_hypothesis; None if the gaze never landed on it). ORACLE-TRUTH: the referent thing."""
    ref = truth_row.get("referent")
    if ref is None:
        return None
    if arm == "ORACLE-TRUTH":
        return int(ref)
    members, pos = things.members(int(truth_row["row"]))
    return M.thing_hypothesis(int(ref), members, pos, truth_row["fix_thing"], tuple(truth_row["centroids"][int(ref)]))


# ------------------------------------------------------------------------------------------------ questions and keys
def build_questions(root: Path, ws: int) -> Dict[str, object]:
    ts = W.TEST_SEEDS[ws]
    out = {"prereg_sha256": PREREG_SHA256, "world_seed": ws, "test_seed": ts}
    keys = {"prereg_sha256": PREREG_SHA256, "world_seed": ws, "test_seed": ts}
    tt = C.load_truth(C.cache_dir(root, ws, "test"))
    m1 = M.m1_items(tt, ts)
    m2a = M.m2a_items(tt, ts)
    m2b = M.m2b_items(C.load_truth(C.cache_dir(root, ws, "m2b")))
    m6 = M.m6_items(C.load_truth(C.cache_dir(root, ws, "m6")))
    th_test = Things(C.ScenePercepts(C.cache_dir(root, ws, "test")))
    th_m2b = Things(C.ScenePercepts(C.cache_dir(root, ws, "m2b")))
    tr_m2b = C.load_truth(C.cache_dir(root, ws, "m2b"))
    name = []
    for row in tt:
        if len(row["things"]) == 1:
            t = row["things"][0]
            name.append({"item_id": f"NAME:{row['item_id']}", "mark": "NAME", "row": int(row["row"]), "phrase": [],
                         "target": 0, "shape": t["shape"], "colour": t["colour"], "size": t["size"], "n_things": 1})
    q = {"M1": [], "M2a": [], "M2b": [], "M6": [], "NAME": []}
    for it in m1:
        q["M1"].append({**M.question(it), "split": "test"})
    for it in m2a:
        q["M2a"].append({**M.question(it), "split": "test"})
    for it in m6:
        q["M6"].append({**M.question(it), "split": "m6"})
    # «what is this?» is asked ABOUT the thing (a pointer, never its name): the thing's hypothesis for the gaze arms
    for it in m2b:
        r = tr_m2b[it["row"]]
        mem, pos = th_m2b.members(it["row"])
        hyp = M.thing_hypothesis(0, mem, pos, r["fix_thing"], tuple(r["centroids"][0]))
        q["M2b"].append({**M.question(it), "split": "m2b", "hyp": hyp})
    for it in name:
        r = tt[it["row"]]
        mem, pos = th_test.members(it["row"])
        hyp = M.thing_hypothesis(0, mem, pos, r["fix_thing"], tuple(r["centroids"][0]))
        q["NAME"].append({**M.question(it), "split": "test", "hyp": hyp})
    out["questions"] = q
    keys["items"] = {"M1": m1, "M2a": m2a, "M2b": m2b, "M6": m6, "NAME": name}
    d = seed_root(root, ws)
    dump(d / "questions.json", out)
    dump(d / "keys.json", keys)
    return {"M1": len(m1), "M2a": len(m2a), "M2b": len(m2b), "M6": len(m6), "NAME": len(name)}


# ------------------------------------------------------------------------------------------------ answering
def answer_all(arm: str, learner, questions: Dict[str, List[Dict[str, object]]], things: Dict[str, Things],
               test_seed: int) -> Dict[str, Dict[str, object]]:
    ans: Dict[str, Dict[str, object]] = {}
    for mark in ("M1", "M2a", "M6"):
        for q in questions.get(mark, []):
            X = things[q["split"]].for_arm(arm, q["row"])
            a = learner.answer_point(X, q["phrase"], M.tie_rng(test_seed, q["item_id"]))
            ans[q["item_id"]] = a
    for q in questions.get("M2b", []):
        k = 0 if arm == "ORACLE-TRUTH" else q.get("hyp")
        if k is None:
            ans[q["item_id"]] = {"emit": None, "uncovered": True}
            continue
        X = things[q["split"]].for_arm(arm, q["row"])
        ans[q["item_id"]] = {"emit": learner.what_is_this(X[int(k)])}
    for q in questions.get("NAME", []):
        k = 0 if arm == "ORACLE-TRUTH" else q.get("hyp")
        if k is None:
            ans[q["item_id"]] = {"name": None, "uncovered": True}
            continue
        X = things[q["split"]].for_arm(arm, q["row"])
        ans[q["item_id"]] = {"name": {t: learner.name_forced(X[int(k)], ws) for t, ws in TYPE_WORDS.items()},
                             "emit": learner.what_is_this(X[int(k)])}
    return ans


def make_learner(arm: str, lr: float, eps: float):
    """`lr` is A-RW's (the gate's); A-RW-LR01 overrides it with its own (ARM_LR — its one difference). The oracle arms
    read with the TYPE-AWARE reader (AMENDMENT 2 §1), handed the word types from here; no RW arm ever holds them."""
    if arm in RW_ARMS:
        return Lr.RWLearner(lr=ARM_LR.get(arm, lr), oracle=(arm == "P-ORACLE-RW"))
    if arm in LDA_ARMS:
        return Lr.TypedLDAReader(eps, WORD_TYPES)
    raise RunError(f"no such arm: {arm!r}")


def train_arm(arm: str, learner, things: Things, words_of, truth: Optional[Sequence[Dict[str, object]]],
              rows: Sequence[int], seed: int, seen: Optional[list] = None) -> None:
    """Feed `rows` of a training split to one arm. `words_of(row)` = what the parent said with that scene (N-SHUF: the
    permuted utterance). `truth` is passed ONLY for the oracle arms (their referent index)."""
    for i in rows:
        X = things.for_arm(arm, i)
        words = words_of(i)
        ref = referent_index(arm, things, truth[i]) if arm in ORACLE_ARMS else None
        if arm in RW_ARMS:
            learner.train_scene(X, words, referent=ref if arm == "P-ORACLE-RW" else None,
                                rng=substream(seed, f"episodic:{i}"))
            if seen is not None:
                seen.append((X, words, ref if arm == "P-ORACLE-RW" else None))
        else:
            learner.train_scene(Lr.feed_oracle(X, ref), words)


def prepare(arm: str, learner, seen: Optional[list]) -> Dict[str, object]:
    if arm in RW_ARMS:
        return learner.calibrate(seen or [])
    return learner.prepare()


def gate_or_chosen() -> Dict[str, object]:
    """The first gate's choices (lr, ε), read from its record — the full run never re-chooses them."""
    p = C.RUNS / "gate" / "gate.json"
    if not p.exists():
        raise RunError(f"{p} missing — THE FIRST GATE runs before any full stream")
    g = json.loads(p.read_text())
    if g.get("verdict") != "PROCEED":
        raise RunError(f"THE FIRST GATE reads {g.get('verdict')!r} — no full run")
    return g


def run_arm(arm: str, root: Path, ws: int, n_train: int = W.N_TRAIN, reading_points: Sequence[int] = W.READING_POINTS,
            lr: Optional[float] = None, eps: Optional[float] = None, out: Optional[Path] = None, log=print) -> Dict[str, object]:
    t_wall, t_cpu = time.perf_counter(), time.process_time()
    if lr is None or eps is None:
        g = gate_or_chosen()
        lr = g["lr"] if lr is None else lr
        eps = g["eps"] if eps is None else eps
    out = Path(out) if out is not None else seed_root(root, ws) / "arms" / arm
    out.mkdir(parents=True, exist_ok=True)
    Q = json.loads((seed_root(root, ws) / "questions.json").read_text())
    if Q["prereg_sha256"] != PREREG_SHA256:
        raise RunError("questions were written under another PREREG")
    things = {s: Things(C.ScenePercepts(C.cache_dir(root, ws, s))) for s in ("test", "m2b", "m6")}
    train = Things(C.ScenePercepts(C.cache_dir(root, ws, "train")))
    truth = C.load_truth(C.cache_dir(root, ws, "train")) if arm in ORACLE_ARMS else None
    if arm == "N-SHUF":
        perm = Lr.nshuf_permutation(substream(ws, "n-shuf-permutation"), len(train.p))
        words_of = lambda i: train.p.words(int(perm[i]))
    else:
        words_of = lambda i: train.p.words(i)
    learner = make_learner(arm, lr, eps)
    seen: list = []
    done = 0
    record = {"arm": arm, "world_seed": ws, "lr": ARM_LR.get(arm, lr) if arm in RW_ARMS else None, "gate_lr": lr,
              "eps": eps if arm in LDA_ARMS else None, "n_train": n_train, "prereg_sha256": PREREG_SHA256,
              "amend2_sha256": AMEND2_SHA256, "code": code_identity(), "reading_points": {}}
    for rp in sorted(r for r in reading_points if r <= n_train):
        train_arm(arm, learner, train, words_of, truth, range(done, rp), ws, seen)
        done = rp
        cal = prepare(arm, learner, seen)
        ans = answer_all(arm, learner, Q["questions"], things, Q["test_seed"])
        dump(out / f"answers_{rp:05d}.json", {"arm": arm, "world_seed": ws, "rp": rp, "answers": ans})
        record["reading_points"][str(rp)] = {"calibration": cal, "summary": learner.summary(),
                                             "wall_s": time.perf_counter() - t_wall, "cpu_s": time.process_time() - t_cpu}
        log(f"[{arm} {ws}] reading point {rp}: answered {len(ans)} · cpu {time.process_time() - t_cpu:.1f} s")
    record["wall_s"] = time.perf_counter() - t_wall
    record["cpu_s"] = time.process_time() - t_cpu
    dump(out / "record.json", record)
    return record


# ------------------------------------------------------------------------------------------------ grading
def grade_seed(root: Path, ws: int, arms: Sequence[str] = ARMS, log=print) -> Dict[str, object]:
    K = json.loads((seed_root(root, ws) / "keys.json").read_text())
    items = K["items"]
    truth = {s: C.load_truth(C.cache_dir(root, ws, s)) for s in ("test", "m2b", "m6")}
    things = {s: Things(C.ScenePercepts(C.cache_dir(root, ws, s))) for s in ("test", "m2b", "m6")}
    m2b_cov = {it["row"] for it in items["M2b"] if M.covered(0, truth["m2b"][it["row"]]["fix_thing"])}
    tr = C.load_truth(C.cache_dir(root, ws, "train"))
    seen = M.meeting_seen(tr[W.DAX_INDEX]) if len(tr) > W.DAX_INDEX else None      # AMENDMENT 2 §3
    out = {"prereg_sha256": PREREG_SHA256, "amend2_sha256": AMEND2_SHA256, "world_seed": ws, "meeting_seen": seen,
           "arms": {}}
    for arm in arms:
        d = seed_root(root, ws) / "arms" / arm
        rec = json.loads((d / "record.json").read_text())
        kind = "truth" if arm == "ORACLE-TRUTH" else "gaze"
        out["arms"][arm] = {"lr": rec["lr"], "eps": rec["eps"], "cpu_s": rec["cpu_s"], "wall_s": rec["wall_s"], "rp": {}}
        for rp in sorted(int(k) for k in rec["reading_points"]):
            A = json.loads((d / f"answers_{rp:05d}.json").read_text())["answers"]
            g1 = M.grade_pointing(items["M1"], A, truth["test"], things["test"].members, kind)
            g6 = M.grade_pointing(items["M6"], A, truth["m6"], things["m6"].members, kind)
            names = {}
            for t in TYPE_WORDS:
                rows = [(A.get(it["item_id"]) or {}).get("name") for it in items["NAME"]]
                ok = [nm[t] == it[t] for nm, it in zip(rows, items["NAME"]) if nm is not None and nm.get(t) is not None]
                # the conformal promise, checked (declared reading): how often «what is this?» emits the thing's TRUE word
                # of this type on the one-thing test scenes — a 0.90 band should emit it ≈ 0.90 of the time
                em = [it[t] in (A.get(it["item_id"]) or {}).get("emit") for it in items["NAME"]
                      if (A.get(it["item_id"]) or {}).get("emit") is not None]
                names[t] = {"acc": (sum(ok) / len(ok) if ok else None), "n": len(ok),
                            "emit_true": (sum(em) / len(em) if em else None), "n_emit": len(em)}
            out["arms"][arm]["rp"][str(rp)] = {
                "M1": M.summarise_pointing(g1), "M2a": M.grade_m2a(items["M2a"], A),
                "M2b": M.grade_m2b(items["M2b"], A, None if kind == "truth" else m2b_cov),
                "M6": M.summarise_pointing(g6), "NAME": names,
                "calibration": rec["reading_points"][str(rp)]["calibration"]}
    dump(seed_root(root, ws) / "marks.json", out)
    log(f"[grade {ws}] written {seed_root(root, ws) / 'marks.json'}")
    return out


def _f(v, nd=3) -> str:
    return "  —  " if v is None else f"{v:.{nd}f}"


def _ge(v, bar) -> bool:
    return v is not None and bar is not None and v >= bar


def _le(v, bar) -> bool:
    return v is not None and bar is not None and v <= bar


def bars_for(marks: Dict[str, object], rp: str = str(W.N_TRAIN)) -> Dict[str, object]:
    """The bars at `rp` for one seed, P-ORACLE's reading beside every mark — the signed PREREG's bars as AMENDMENT 2
    reads them: M1 on the 2- and 3-thing items (pooled = the verdict line; per scene size printed with its own mark,
    declared), M6 only where the meeting was seen, a reading of None (nothing gradable) never a 0.0."""
    A = {a: marks["arms"][a]["rp"].get(rp) for a in marks["arms"]}
    m1 = lambda arm, key="graded": A[arm]["M1"][key]
    r: Dict[str, object] = {}
    rows = {}
    for key in ("graded", "size2", "size3"):
        a = m1("A-RW", key)
        prw, po = m1("P-ORACLE-RW", key)["covered"], m1("P-ORACLE", key)["covered"]
        bar_rw = None if prw is None else M.BARS["M1_vs_PORACLE_RW"] * prw
        bar_lda = None if po is None else M.BARS["M1_vs_PORACLE"] * po
        rows[key] = {"value": a["covered"], "n": a["n_covered"], "all": a["all"], "n_all": a["n_all"],
                     "coverage": a["coverage"], "chance": a["chance_covered"], "p_oracle": po, "p_oracle_rw": prw,
                     "bar_rw": bar_rw, "bar_lda": bar_lda, "pass": _ge(a["covered"], bar_rw) and _ge(a["covered"], bar_lda),
                     "lr01": m1("A-RW-LR01", key)["covered"] if "A-RW-LR01" in A else None,
                     "oracle_truth": m1("ORACLE-TRUTH", key)["covered"], "n_unheard": a["n_unheard"]}
    r["M1"] = dict(rows["graded"])
    r["M1"]["by_size"] = {"size2": rows["size2"], "size3": rows["size3"]}
    r["M1"]["sanity_size1"] = {"value": m1("A-RW", "size1")["covered"], "n": m1("A-RW", "size1")["n_covered"]}
    m2a = A["A-RW"]["M2a"]["all"]
    fr = m1("A-RW")["false_refusal"]
    po2, po_fr = A["P-ORACLE"]["M2a"]["all"]["refusal"], m1("P-ORACLE")["false_refusal"]
    v2 = M.m2a_verdict(m2a["refusal"], fr, po2, po_fr)          # CEILING-BOUND read per half (declared, RAISED)
    r["M2a"] = {"value": m2a["refusal"], "n": m2a["n"], "false_refusal": fr, "n_fr": m1("A-RW")["n_fr"], "p_oracle": po2,
                "p_oracle_fr": po_fr, "pass": v2["pass"], "ceiling_bound": v2["ceiling_bound"],
                "failing_halves": v2["failing_halves"], "whole_bar_ceiling": v2["whole_bar_ceiling"]}
    m2b = A["A-RW"]["M2b"]["graded"]
    po3 = A["P-ORACLE"]["M2b"]["graded"]["correct"]
    ok3 = _ge(m2b["correct"], M.BARS["M2b"])
    r["M2b"] = {"value": m2b["correct"], "n": m2b["n"], "p_oracle": po3, "pass": ok3,
                "ceiling_bound": (not ok3) and po3 is not None and po3 < M.BARS["M2b"],
                "diamond": A["A-RW"]["M2b"]["diamond"]["correct"], "diamond_p_oracle": A["P-ORACLE"]["M2b"]["diamond"]["correct"]}
    seen = marks.get("meeting_seen")
    m6 = A["A-RW"]["M6"]["all"]
    po6 = A["P-ORACLE"]["M6"]["all"]["covered"]
    if seen is not True:
        why = "the meeting was never seen (0 fixations on the dax at its scene)" if seen is False else "no meeting in this stream"
        r["M6"] = {"value": None, "n": 0, "not_gradable": why, "pass": False, "ceiling_bound": False, "p_oracle": None,
                   "chance": None, "all": None, "n_all": 0}
    elif m6["covered"] is None:
        r["M6"] = {"value": None, "n": 0, "not_gradable": f"the learner never heard «dax» (n_unheard {m6['n_unheard']})",
                   "pass": False, "ceiling_bound": False, "p_oracle": po6, "chance": None, "all": None, "n_all": 0}
    else:
        ok6 = _ge(m6["covered"], M.BARS["M6"])
        r["M6"] = {"value": m6["covered"], "n": m6["n_covered"], "all": m6["all"], "n_all": m6["n_all"], "p_oracle": po6,
                   "chance": m6["chance_covered"], "pass": ok6, "not_gradable": False,
                   "ceiling_bound": (not ok6) and (po6 is None or po6 < M.BARS["M6"]),
                   "by_size": {f"size{n}": A["A-RW"]["M6"][f"size{n}"]["covered"] for n in (2, 3)}}
    ns = m1("N-SHUF")
    r["N-SHUF"] = {"value": ns["covered"], "chance": ns["chance_covered"],
                   "bar": None if ns["chance_covered"] is None else ns["chance_covered"] + M.BARS["NSHUF_over_chance"],
                   "pass": _le(ns["covered"], None if ns["chance_covered"] is None else ns["chance_covered"] + M.BARS["NSHUF_over_chance"]),
                   "by_size": {k: {"value": m1("N-SHUF", k)["covered"], "chance": m1("N-SHUF", k)["chance_covered"]}
                               for k in ("size2", "size3")}}
    for k in ("M1", "M2a", "M2b", "M6"):
        r[k]["underpowered"] = (not r[k].get("not_gradable")) and (r[k]["n"] or 0) < M.UNDERPOWERED_N
    prw = r["M1"]["p_oracle_rw"]
    r["T1_refuted"] = bool(r["M1"]["value"] is not None and prw is not None and r["M1"]["value"] < M.T1_REFUTE * prw)
    r["one_meeting_refuted"] = bool((not r["M6"].get("not_gradable")) and r["M6"]["value"] is not None
                                    and r["M6"]["value"] < M.M6_REFUTE and r["M1"]["pass"])
    return r


def print_seed_table(marks: Dict[str, object], log=print) -> List[str]:
    ws = marks["world_seed"]
    arms = [a for a in ARMS if a in marks["arms"]]
    lines = [f"== S1a marks · world seed {ws} (test seed {W.TEST_SEEDS[ws]}) · the one meeting seen: {marks.get('meeting_seen')} =="]
    rps = sorted(int(k) for k in marks["arms"]["A-RW"]["rp"])
    lines.append("M1 (covered, the GRADED 2- and 3-thing items) by reading point — A-RW-LR01 is a reading arm (no bar):")
    lines.append("   arm            " + " ".join(f"{rp:>7d}" for rp in rps))
    for arm in arms:
        vals = [marks["arms"][arm]["rp"][str(rp)]["M1"]["graded"]["covered"] for rp in rps]
        lines.append(f"   {arm:<14} " + " ".join(f"{_f(v):>7}" for v in vals))
    top = str(max(rps))
    lines.append(f"At {top} scenes — M1 (covered · all) per block; chance and n from A-RW's items; size1 is the sanity reading:")
    for key in ["graded", "size2", "size3", "size1", "type:colour", "type:shape", "type:size", "type:none",
                "tpl:T1", "tpl:T2", "tpl:T3", "tpl:T4"]:
        cells = []
        for arm in arms:
            b = marks["arms"][arm]["rp"][top]["M1"].get(key)
            cells.append(f"{arm} —" if b is None else f"{arm} {_f(b['covered'])}·{_f(b['all'])}")
        b0 = marks["arms"]["A-RW"]["rp"][top]["M1"].get(key) or {}
        lines.append(f"   {key:<12} cov {_f(b0.get('coverage'))} chance {_f(b0.get('chance_covered'))} n {b0.get('n_covered')}/{b0.get('n_all')} | "
                     + " | ".join(cells))
    for arm in arms:
        R = marks["arms"][arm]["rp"][top]
        m2a, m2b, m6 = R["M2a"]["all"], R["M2b"], R["M6"]["all"]
        nm = R["NAME"]
        m6s = (f"M6 covered {_f(m6['covered'])} all {_f(m6['all'])} (n {m6['n_covered']}/{m6['n_all']}, chance {_f(m6['chance_covered'])}, unheard {m6['n_unheard']})"
               if marks.get("meeting_seen") is True else "M6 NOT GRADABLE (the meeting was never seen)")
        lines.append(f"   {arm:<14} M2a refusal {_f(m2a['refusal'])} (n {m2a['n']}) · false refusal (graded M1 covered) "
                     f"{_f(R['M1']['graded']['false_refusal'])} · M2b {_f(m2b['graded']['correct'])} (n {m2b['graded']['n']}; "
                     f"«I don't know» {_f(m2b['graded']['idk'])}; diamond {_f(m2b['diamond']['correct'])}) · {m6s} "
                     f"· NAME shape {_f(nm['shape']['acc'])} colour {_f(nm['colour']['acc'])} size {_f(nm['size']['acc'])} "
                     f"· «what is this?» emits the true word (the 0.90 promise) shape {_f(nm['shape'].get('emit_true'))} "
                     f"colour {_f(nm['colour'].get('emit_true'))} size {_f(nm['size'].get('emit_true'))}")
    for s in W.M2B_SHAPES:
        lines.append(f"   M2b {s:<6} " + " ".join(f"{arm} {_f(marks['arms'][arm]['rp'][top]['M2b'][f'shape:{s}']['correct'])}" for arm in arms)
                     + f" · A-RW emitted {marks['arms']['A-RW']['rp'][top]['M2b'][f'shape:{s}']['shape_words_emitted']}")
    if marks.get("meeting_seen") is True:
        for n in (2, 3):
            lines.append(f"   M6 size{n}: " + " ".join(f"{arm} {_f(marks['arms'][arm]['rp'][top]['M6'][f'size{n}']['covered'])}" for arm in arms)
                         + f" · chance {_f(marks['arms']['A-RW']['rp'][top]['M6'][f'size{n}']['chance_covered'])}")
    gap = []
    for key in ("graded", "size2", "size3"):
        a = marks["arms"]["ORACLE-TRUTH"]["rp"][top]["M1"][key]["covered"]
        b = marks["arms"]["P-ORACLE"]["rp"][top]["M1"][key]["covered"]
        gap.append(f"{key} {_f(None if a is None or b is None else a - b)}")
    lines.append("   the gaze's cost ORACLE-TRUTH − P-ORACLE on M1 (covered): " + " · ".join(gap))
    for l in lines:
        log(l)
    return lines


def _verdict(b: Dict[str, object]) -> str:
    """NOT GRADABLE, then UNDERPOWERED (the signed PREREG: «a mark with n < 30 items per seed reads UNDERPOWERED» —
    whatever its value), then PASS / CEILING-BOUND / FAIL."""
    if b.get("not_gradable"):
        return "NOT GRADABLE"
    if b.get("underpowered"):
        return "UNDERPOWERED"
    if b["pass"]:
        return "PASS"
    return "CEILING-BOUND" if b.get("ceiling_bound") else "FAIL"


def report(root: Path, log=print) -> Dict[str, object]:
    out = {"prereg_sha256": PREREG_SHA256, "amend2_sha256": AMEND2_SHA256, "seeds": {}}
    lines: List[str] = []
    for ws in W.WORLD_SEEDS:
        mk = json.loads((seed_root(root, ws) / "marks.json").read_text())
        lines += print_seed_table(mk, log=lambda s: None)
        out["seeds"][str(ws)] = bars_for(mk)
        lines.append("")
    lines.append("== S1a BARS at 10,000 scenes (A-RW; P-ORACLE's reading beside every mark; M1 on the 2- and 3-thing items) ==")
    for ws in W.WORLD_SEEDS:
        b = out["seeds"][str(ws)]
        m1 = b["M1"]
        lines.append(f"{ws} M1 covered {_f(m1['value'])} (all {_f(m1['all'])}; n {m1['n']}/{m1['n_all']}; chance {_f(m1['chance'])}) "
                     f"bars ≥ {_f(m1['bar_rw'])} (0.90 × P-ORACLE-RW {_f(m1['p_oracle_rw'])}) and ≥ {_f(m1['bar_lda'])} "
                     f"(0.80 × P-ORACLE {_f(m1['p_oracle'])}) → {_verdict(m1)} · ORACLE-TRUTH {_f(m1['oracle_truth'])} · "
                     f"A-RW-LR01 {_f(m1['lr01'])} (reading)")
        for k, v in m1["by_size"].items():
            lines.append(f"          {k}: {_f(v['value'])} (n {v['n']}, chance {_f(v['chance'])}) bars {_f(v['bar_rw'])} · {_f(v['bar_lda'])} "
                         f"(P-ORACLE-RW {_f(v['p_oracle_rw'])}, P-ORACLE {_f(v['p_oracle'])}) → {_verdict(v)} · A-RW-LR01 {_f(v['lr01'])}")
        lines.append(f"          size1 (sanity): {_f(m1['sanity_size1']['value'])} (n {m1['sanity_size1']['n']})")
        m2a, m2b, m6, ns = b["M2a"], b["M2b"], b["M6"], b["N-SHUF"]
        lines.append(f"          M2a refusal {_f(m2a['value'])} (n {m2a['n']}) · false refusal {_f(m2a['false_refusal'])} (n {m2a['n_fr']}) "
                     f"· P-ORACLE {_f(m2a['p_oracle'])} / {_f(m2a['p_oracle_fr'])} → {_verdict(m2a)}"
                     + (f" (the learner fails: {', '.join(m2a['failing_halves'])}; the whole-bar reading: "
                        f"{'CEILING-BOUND' if m2a['whole_bar_ceiling'] else 'FAIL'})" if not m2a["pass"] else ""))
        lines.append(f"          M2b {_f(m2b['value'])} (n {m2b['n']}) · P-ORACLE {_f(m2b['p_oracle'])} → {_verdict(m2b)} · diamond (apart) "
                     f"{_f(m2b['diamond'])} · P-ORACLE {_f(m2b['diamond_p_oracle'])}")
        if m6.get("not_gradable"):
            lines.append(f"          M6 NOT GRADABLE — {m6['not_gradable']}")
        else:
            lines.append(f"          M6 covered {_f(m6['value'])} (all {_f(m6['all'])}; n {m6['n']}/{m6['n_all']}; chance {_f(m6['chance'])}) "
                         f"· P-ORACLE {_f(m6['p_oracle'])} → {_verdict(m6)}")
        lines.append(f"          N-SHUF M1 {_f(ns['value'])} ≤ chance {_f(ns['chance'])} + 0.05 = {_f(ns['bar'])} → {'PASS' if ns['pass'] else 'FAIL'} "
                     f"(size2 {_f(ns['by_size']['size2']['value'])} vs {_f(ns['by_size']['size2']['chance'])}; "
                     f"size3 {_f(ns['by_size']['size3']['value'])} vs {_f(ns['by_size']['size3']['chance'])})")
        und = [k for k in ("M1", "M2a", "M2b", "M6") if b[k].get("underpowered")]
        if und:
            lines.append(f"          UNDERPOWERED (n < 30): {', '.join(und)}")
    grad6 = [ws for ws in W.WORLD_SEEDS if not out["seeds"][str(ws)]["M6"].get("not_gradable")]
    # a seed counts for a mark only when that mark READS PASS there (UNDERPOWERED, CEILING-BOUND and FAIL do not)
    reads = {k: {ws: (_verdict(out["seeds"][str(ws)][k]) if k != "N-SHUF" else ("PASS" if out["seeds"][str(ws)][k]["pass"] else "FAIL"))
                 for ws in W.WORLD_SEEDS} for k in ("M1", "M2a", "M2b", "M6", "N-SHUF")}
    allpass = {k: all(reads[k][ws] == "PASS" for ws in W.WORLD_SEEDS) for k in ("M1", "M2a", "M2b", "N-SHUF")}
    allpass["M6"] = bool(grad6) and all(reads["M6"][ws] == "PASS" for ws in grad6)
    lines.append("per seed: " + " · ".join(f"{k} " + "/".join(reads[k][ws] for ws in W.WORLD_SEEDS) for k in reads))
    lines.append("every bar at all 3 seeds (M6 at the seeds where the meeting was seen: " + ", ".join(map(str, grad6)) + "): "
                 + " · ".join(f"{k} {'PASS' if v else 'no'}" for k, v in allpass.items())
                 + f" → S1a {'PASSES' if all(allpass.values()) else 'does not pass'}")
    out["reads"] = {k: {str(ws): v for ws, v in d.items()} for k, d in reads.items()}
    lines.append("refutations: T1 (A-RW M1 < 0.6 × P-ORACLE-RW) " + " ".join(
        f"{ws}:{'REFUTED' if out['seeds'][str(ws)]['T1_refuted'] else 'no'}" for ws in W.WORLD_SEEDS)
        + " · one-meeting (M6 < 0.5 while M1 passes) " + " ".join(
        f"{ws}:{'REFUTED' if out['seeds'][str(ws)]['one_meeting_refuted'] else ('n/g' if out['seeds'][str(ws)]['M6'].get('not_gradable') else 'no')}"
        for ws in W.WORLD_SEEDS))
    out["all_pass"] = allpass
    out["m6_gradable_seeds"] = grad6
    for l in lines:
        log(l)
    dump(Path(root) / "report.json", out)
    (Path(root) / "report.txt").write_text("\n".join(lines) + "\n")
    return out


# ------------------------------------------------------------------------------------------------ stage −1
def stage_minus1(root: Path, log=print) -> Dict[str, object]:
    d = C.cache_dir(root, None, "stage")
    if not d.exists():
        C.build("stage", None, d, log=log)
    P = C.ScenePercepts(d)
    f = M.organ_facts(C.load_truth(d), P)
    lines = [f"== STAGE −1 (organ facts, printed only) · {len(P)} scenes of seed {W.STAGE_SEED} =="]
    for n in (1, 2, 3):
        rc, nr = f["recall"][n]
        ac, na = f["all_covered"][n]
        mg, nh = f["merge"][n]
        jk, _ = f["on_no_thing"][n]
        sp, ns = f["split"][n]
        lines.append(f"{n}-thing scenes ({na}): gaze per-thing recall {_f(rc)} (n {nr}) · all things covered {_f(ac)} · "
                     f"merge (hypotheses on 2 things) {_f(mg)} of {nh} · hypotheses on no thing {_f(jk)} · "
                     f"split (a thing → ≥ 2 hypotheses) {_f(sp)} of {ns}")
    lines.append(f"input separability, LOO nearest-class-mean, {f['n_one_thing']} one-thing scenes "
                 f"(the probe read all 144: shape 0.797 · colour 0.933 · size 0.867; tower 112 shape 0.903 · colour 32 colour 0.925 · tower 112 size 0.875):")
    for road, t in f["separability"].items():
        lines.append(f"   {road:<10} " + " · ".join(
            f"{typ}: all {_f(v['all 144'])} tower {_f(v['tower 112'])} colour {_f(v['colour 32'])}" for typ, v in t.items()))
    for l in lines:
        log(l)
    f["lines"] = lines
    dump(Path(root) / "stage" / "stage_minus1.json", f)
    (Path(root) / "stage" / "stage_minus1.txt").write_text("\n".join(lines) + "\n")
    return f


# ------------------------------------------------------------------------------------------------ THE FIRST GATE
def _toy_m1(learner, arm: str, items, toy_test: Things, toy_truth) -> Dict[str, object]:
    ans = {}
    for it in items:
        X = toy_test.for_arm(arm, it["row"])
        ans[it["item_id"]] = learner.answer_point(X, it["phrase"], M.tie_rng(W.TOY_SEED, it["item_id"]))
    g = M.grade_pointing(items, ans, toy_truth, toy_test.members, "gaze")
    return M.summarise_pointing(g)["all"]


def _per_type_naming(reader, things: Things, truth_rows, arm: str = "P-ORACLE") -> Dict[str, Tuple[Optional[float], int]]:
    """Forced per-type naming of every COVERED thing of `truth_rows` (its hypothesis), graded apart per type."""
    ok = {t: [] for t in TYPE_WORDS}
    for row in truth_rows:
        mem, pos = things.members(int(row["row"]))
        X = things.for_arm(arm, int(row["row"]))
        for k, t in enumerate(row["things"]):
            h = M.thing_hypothesis(k, mem, pos, row["fix_thing"], tuple(row["centroids"][k]))
            if h is None:
                continue
            for typ, ws in TYPE_WORDS.items():
                ok[typ].append(reader.name_forced(X[h], ws) == t[typ])
    return {t: (sum(v) / len(v) if v else None, len(v)) for t, v in ok.items()}


def first_gate(root: Path, log=print, toy_only: bool = False) -> Dict[str, object]:
    check_prereg()
    t0 = time.perf_counter()
    out: Dict[str, object] = {"prereg_sha256": PREREG_SHA256, "amend2_sha256": AMEND2_SHA256, "code": code_identity()}
    lines = ["== THE FIRST GATE (PREREG-R3-TONIGHT §S1a, as AMENDMENT 2 reads it) =="]
    # --- 1. the toy
    for split in ("toy-train", "toy-test"):
        d = C.cache_dir(root, None, split)
        if not d.exists():
            C.build(split, None, d, log=log)
    tr = Things(C.ScenePercepts(C.cache_dir(root, None, "toy-train")))
    te = Things(C.ScenePercepts(C.cache_dir(root, None, "toy-test")))
    te_truth = C.load_truth(C.cache_dir(root, None, "toy-test"))
    tr_truth = C.load_truth(C.cache_dir(root, None, "toy-train"))
    items = M.m1_items(te_truth, W.TOY_SEED, mark="TOY")
    rows = list(range(len(tr.p)))

    def toy_run(lr):
        L = Lr.RWLearner(lr=lr)
        seen: list = []
        train_arm("A-RW", L, tr, tr.p.words, None, rows, W.TOY_SEED, seen)
        L.calibrate(seen)
        return _toy_m1(L, "A-RW", items, te, te_truth)

    toy = {"items": len(items), "runs": {}}
    r = toy_run(Lr.LR)
    toy["runs"][str(Lr.LR)] = r
    lr = Lr.LR
    if r["covered"] < M.TOY_BAR:
        for g in Lr.LR_GRID:
            if str(g) not in toy["runs"]:
                toy["runs"][str(g)] = toy_run(g)
        best = max(toy["runs"].items(), key=lambda kv: (kv[1]["covered"], float(kv[0]) == Lr.LR, -float(kv[0])))
        lr = float(best[0])
        toy["fallback"] = True
    else:
        toy["fallback"] = False
    toy["lr"] = lr
    toy["m1_covered"] = toy["runs"][str(lr)]["covered"]
    toy["pass"] = toy["m1_covered"] >= M.TOY_BAR
    lines.append(f"1. THE TOY: A-RW trained on {len(rows)} one-thing scenes (seed {W.TOY_SEED}), M1 on {len(items)} two-thing "
                 f"items: " + " · ".join(f"lr {k}: covered {_f(v['covered'])} (n {v['n_covered']}) all {_f(v['all'])} chance {_f(v['chance_covered'])}"
                                         for k, v in toy["runs"].items())
                 + f" → lr {lr} {'PASS' if toy['pass'] else 'FAIL'} (bar ≥ {M.TOY_BAR}; fallback grid {'used' if toy['fallback'] else 'not needed'})")
    # --- ε for P-ORACLE, on the toy seed only
    eps_rows = {}
    for eps in Lr.EPS_GRID:
        R = make_learner("P-ORACLE", Lr.LR, eps)            # AMENDMENT 2 §1: the TYPE-AWARE reader, ε on the toy as before
        train_arm("P-ORACLE", R, tr, tr.p.words, tr_truth, rows, W.TOY_SEED)
        R.prepare()
        nm = _per_type_naming(R, te, te_truth)
        eps_rows[str(eps)] = {"naming": nm, "mean": float(np.mean([v[0] for v in nm.values()])),
                              "m1": _toy_m1(R, "P-ORACLE", items, te, te_truth)["covered"]}
    best = max(eps_rows.items(), key=lambda kv: (kv[1]["mean"], float(kv[0])))
    eps = float(best[0])
    out["eps_choice"] = {"grid": eps_rows, "eps": eps, "rule": "max mean per-type forced naming on the toy's two-thing "
                         "scenes' covered things; ties → the larger ε"}
    lines.append("   P-ORACLE's ε on the toy seed only (mean per-type forced naming · toy M1): " + " · ".join(
        f"{k}: {v['mean']:.3f} · {v['m1']:.3f}" for k, v in eps_rows.items()) + f" → ε {eps}")
    out["toy"] = toy
    out["lr"], out["eps"] = lr, eps
    if toy_only:
        for l in lines:
            log(l)
        return out
    # --- 2. the instrument verdict: P-ORACLE's per-type naming, leave-one-scene-out, on the gate's one-thing scenes
    ws = W.WORLD_SEEDS[0]
    trs = Things(C.ScenePercepts(C.cache_dir(root, ws, "train")))
    trs_truth = C.load_truth(C.cache_dir(root, ws, "train"))
    gate_rows = list(range(W.GATE_N))
    one = [i for i in gate_rows if len(trs_truth[i]["things"]) == 1]
    loo = {t: [] for t in TYPE_WORDS}
    for i in one:
        R = make_learner("P-ORACLE", lr, eps)               # AMENDMENT 2 §1: the verdict RE-READ with the type-aware reader
        train_arm("P-ORACLE", R, trs, trs.p.words, trs_truth, [j for j in gate_rows if j != i], ws)
        R.prepare()
        nm = _per_type_naming(R, trs, [trs_truth[i]])
        for t, (v, n) in nm.items():
            if n:
                loo[t].append(v)
    th = M.verdict_thresholds()
    verdict = {}
    for t in TYPE_WORDS:
        v = float(np.mean(loo[t])) if loo[t] else None
        verdict[t] = {"p_oracle": v, "n": len(loo[t]), "probe_all144": M.PROBE_ALL144[t], "threshold": th[t],
                      "fires": v is None or v < th[t], "best_subset": M.PROBE_SUBSET[t]}
    out["instrument"] = verdict
    lines.append(f"2. THE INSTRUMENT VERDICT: P-ORACLE (ε {eps}) per-type naming, leave-one-scene-out on the {len(one)} "
                 f"one-thing scenes among the first {W.GATE_N} of seed {ws}:")
    for t, v in verdict.items():
        lines.append(f"   {t:<6} {_f(v['p_oracle'])} (n {v['n']}) vs 0.90 × probe {v['probe_all144']} = {v['threshold']:.4f} → "
                     f"{'FIRES' if v['fires'] else 'does not fire'} · best-subset probe {v['best_subset'][0]} {v['best_subset'][1]} (read by no verdict)")
    # --- 3. the arms × 300 scenes vs N-SHUF on M1 (seed 1's test items; AMENDMENT 2: the graded 2- and 3-thing items)
    Qf = seed_root(root, ws) / "questions.json"
    if not Qf.exists():
        build_questions(root, ws)
    Q = json.loads(Qf.read_text())
    K = json.loads((seed_root(root, ws) / "keys.json").read_text())
    tt = Things(C.ScenePercepts(C.cache_dir(root, ws, "test")))
    t_truth = C.load_truth(C.cache_dir(root, ws, "test"))
    perm = Lr.nshuf_permutation(substream(ws, "n-shuf-permutation"), len(trs.p))
    arms = {}
    for arm in ARMS:
        L = make_learner(arm, lr, eps)
        seen: list = []
        words_of = (lambda i: trs.p.words(int(perm[i]))) if arm == "N-SHUF" else trs.p.words
        train_arm(arm, L, trs, words_of, trs_truth if arm in ORACLE_ARMS else None, gate_rows, ws, seen)
        prepare(arm, L, seen)
        ans = answer_all(arm, L, {"M1": Q["questions"]["M1"]}, {"test": tt}, Q["test_seed"])
        g = M.grade_pointing(K["items"]["M1"], ans, t_truth, tt.members, "truth" if arm == "ORACLE-TRUTH" else "gaze")
        arms[arm] = M.summarise_pointing(g)
    # AMENDMENT 2 §2: «beats N-SHUF» is read on the GRADED 2- and 3-thing items; the reading arm carries no bar
    ns_cov = arms["N-SHUF"]["graded"]["covered"]
    beat = {a: (arms[a]["graded"]["covered"] is not None and ns_cov is not None and arms[a]["graded"]["covered"] > ns_cov)
            for a in ARMS if a != "N-SHUF" and a not in READING_ARMS}
    out["arms300"] = {a: arms[a]["graded"] for a in ARMS}
    out["arms300_blocks"] = {a: {k: arms[a][k] for k in ("graded", "size1", "size2", "size3", "all")} for a in ARMS}
    out["beat_nshuf"] = beat
    g0 = arms["A-RW"]["graded"]
    lines.append(f"3. {len(ARMS)} ARMS × {W.GATE_N} scenes of seed {ws}, M1 on its GRADED 2- and 3-thing test items "
                 f"(n {g0['n_all']}, covered {g0['n_covered']}; chance covered {_f(g0['chance_covered'])}) — per size and the "
                 f"one-thing sanity reading beside:")
    for a in ARMS:
        b = arms[a]
        lines.append(f"   {a:<14} M1 covered {_f(b['graded']['covered'])} · all {_f(b['graded']['all'])} · size2 "
                     f"{_f(b['size2']['covered'])} (chance {_f(b['size2']['chance_covered'])}) · size3 {_f(b['size3']['covered'])} "
                     f"(chance {_f(b['size3']['chance_covered'])}) · size1 sanity {_f(b['size1']['covered'])} · pooled (all sizes) "
                     f"{_f(b['all']['covered'])}"
                     + ("" if a == "N-SHUF" else (" · a reading arm, no bar" if a in READING_ARMS else
                                                  f" · beats N-SHUF: {'yes' if beat[a] else 'NO'}")))
    lines.append(f"   (the brief's step 6: ORACLE-TRUTH < 0.95 → STOP; the signed PREREG's and AMENDMENT 2's STOP is the "
                 f"instrument verdict. ORACLE-TRUTH reads {_f(arms['ORACLE-TRUTH']['graded']['covered'])} on the graded items, "
                 f"{_f(arms['ORACLE-TRUTH']['all']['covered'])} on all.)")
    fired = [t for t, v in verdict.items() if v["fires"]]
    stop = []
    if fired:
        stop.append(f"the instrument verdict fires for {fired}")
    if not toy["pass"]:
        stop.append("A-RW fails its own toy after the fallback grid")
    out["verdict"] = "STOP" if stop else "PROCEED"
    out["stop_reasons"] = stop
    out["results_not_stops"] = [f"{a} does not beat N-SHUF" for a, b in beat.items() if not b]
    out["wall_s"] = time.perf_counter() - t0
    lines.append(f"GATE: {out['verdict']}" + (f" — {'; '.join(stop)}" if stop else "")
                 + (f" · RESULTS (not stops): {'; '.join(out['results_not_stops'])}" if out["results_not_stops"] else ""))
    for l in lines:
        log(l)
    out["lines"] = lines
    dump(Path(root) / "gate" / "gate.json", out)
    (Path(root) / "gate" / "gate.txt").write_text("\n".join(lines) + "\n")
    return out


# ------------------------------------------------------------------------------------------------ the price
def price(root: Path, n: int = 2000, log=print) -> Dict[str, object]:
    """Solo (A-RW, seed 1), then the launch's shape (6 arms × 3 seeds at once, nice 19), each over the first `n` scenes
    with the reading points ≤ n; CPU seconds read from each process's own record, extrapolated ×(10,000 / n)."""
    g = gate_or_chosen()
    tmp = Path(root) / "price"
    rps = [r for r in W.READING_POINTS if r <= n]
    base = [sys.executable, "-B", "-m", "brain.scene.run", "arm", "--n", str(n), "--rps", ",".join(map(str, rps))]
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", PYTHONUNBUFFERED="1")
    cwd = str(Path(__file__).resolve().parents[2])

    def launch(jobs):
        procs = []
        t0 = time.perf_counter()
        for arm, ws in jobs:
            o = tmp / f"{len(jobs)}x" / f"{ws}-{arm}"
            o.mkdir(parents=True, exist_ok=True)
            p = subprocess.Popen(["nice", "-n", "19"] + base + ["--arm", arm, "--world-seed", str(ws), "--out", str(o)],
                                 cwd=cwd, env=env, stdout=open(o / "log.txt", "w"), stderr=subprocess.STDOUT)
            procs.append((arm, ws, o, p))
        res = []
        for arm, ws, o, p in procs:
            rc = p.wait()
            rec = json.loads((o / "record.json").read_text()) if rc == 0 else None
            res.append({"arm": arm, "seed": ws, "rc": rc, "cpu_s": rec["cpu_s"] if rec else None,
                        "wall_s": rec["wall_s"] if rec else None})
        return res, time.perf_counter() - t0

    solo, solo_wall = launch([("A-RW", W.WORLD_SEEDS[0])])
    shape, shape_wall = launch([(a, s) for s in W.WORLD_SEEDS for a in ARMS])
    k = W.N_TRAIN / n
    out = {"n": n, "extrapolate": k, "solo": solo, "solo_wall": solo_wall, "shape": shape, "shape_wall": shape_wall,
           "lr": g["lr"], "eps": g["eps"]}
    cpu_shape = sum(r["cpu_s"] or 0 for r in shape)
    lines = [f"== PRICE (first {n} scenes, reading points {rps}; × {k:.0f} to 10,000) ==",
             f"solo A-RW seed {W.WORLD_SEEDS[0]}: cpu {solo[0]['cpu_s']:.1f} s, wall {solo_wall:.1f} s → ≈ {solo[0]['cpu_s'] * k / 60:.1f} CPU-min per arm-seed",
             f"launch shape {len(ARMS)} arms × 3 seeds at once: cpu {cpu_shape:.1f} s total (per process "
             + ", ".join(f"{r['arm']}/{r['seed']} {r['cpu_s']:.1f}" for r in shape) + f"), wall {shape_wall:.1f} s "
             f"→ ≈ {cpu_shape * k / 3600:.2f} CPU-h and ≈ {shape_wall * k / 60:.1f} min wall for the arms at 10,000"]
    for l in lines:
        log(l)
    out["lines"] = lines
    dump(Path(root) / "price" / "price.json", out)
    (Path(root) / "price" / "price.txt").write_text("\n".join(lines) + "\n")
    return out


# ------------------------------------------------------------------------------------------------ CLI
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="brain.scene.run")
    ap.add_argument("cmd", choices=["cache", "cache-world", "questions", "stage", "first-gate", "toy", "arm", "grade",
                                    "report", "price"])
    ap.add_argument("--split")
    ap.add_argument("--world-seed", type=int)
    ap.add_argument("--arm")
    ap.add_argument("--n", type=int, default=W.N_TRAIN)
    ap.add_argument("--rps", default=",".join(map(str, W.READING_POINTS)))
    ap.add_argument("--out")
    ap.add_argument("--root", default=str(C.RUNS))
    a = ap.parse_args(argv)
    root = Path(a.root)
    log = Log(root / "logs" / f"{a.cmd}.log")
    check_prereg()
    if a.cmd == "cache":
        C.build(a.split, a.world_seed, C.cache_dir(root, a.world_seed, a.split), log=log)
    elif a.cmd == "cache-world":
        rec = C.build_world_seed(root, a.world_seed, log=log)
        log(f"[cache-world {a.world_seed}] disjoint: {rec['checked']} test canvases vs {rec['train_canvases']} training, overlap 0")
    elif a.cmd == "questions":
        log(f"[questions {a.world_seed}] {build_questions(root, a.world_seed)}")
    elif a.cmd == "stage":
        stage_minus1(root, log=log)
    elif a.cmd == "toy":
        first_gate(root, log=log, toy_only=True)
    elif a.cmd == "first-gate":
        g = first_gate(root, log=log)
        return 0 if g["verdict"] == "PROCEED" else 3
    elif a.cmd == "arm":
        rps = [int(x) for x in a.rps.split(",") if x]
        run_arm(a.arm, root, a.world_seed, n_train=a.n, reading_points=rps, out=Path(a.out) if a.out else None, log=log)
    elif a.cmd == "grade":
        mk = grade_seed(root, a.world_seed, log=log)
        print_seed_table(mk, log=log)
    elif a.cmd == "report":
        report(root, log=log)
    elif a.cmd == "price":
        price(root, n=a.n if a.n != W.N_TRAIN else 2000, log=log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
