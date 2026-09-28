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

from . import AMEND2_SHA256, PREREG_S1B1_SHA256, PREREG_S1B1R_SHA256, PREREG_SHA256, S1B1R_AMEND1_SHA256
from . import cache as C
from . import learners as Lr
from . import marks as M
from . import world as W

# PREREG-S1B1 §6 (edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:51 +0400): six arms × three seeds; A-RW's law is lr 0.01, S1a's
# law (lr 0.1) is the READING arm A-RW-LR10; N-SHUF and P-ORACLE-RW run at the law's lr.
ARMS: Tuple[str, ...] = ("A-RW", "A-RW-LR10", "N-SHUF", "P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH")
RW_ARMS = ("A-RW", "A-RW-LR10", "N-SHUF", "P-ORACLE-RW")
LDA_ARMS = ("P-ORACLE", "ORACLE-TRUTH")
ORACLE_ARMS = ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH")        # the only arms whose feed carries a referent index
READING_ARMS = ("A-RW-LR10",)                                     # printed beside A-RW on every mark, no bar
ARM_LR = {"A-RW": Lr.LR_S1B1, "A-RW-LR10": Lr.LR, "N-SHUF": Lr.LR_S1B1, "P-ORACLE-RW": Lr.LR_S1B1}
PREREG_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-R3-TONIGHT.md")
AMEND2_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-R3-TONIGHT-AMEND-2.md")
PREREG_S1B1_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-S1B1.md")
# PREREG-S1B1R (edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:00 +0400): the law this slice builds and its AMENDMENT 1
PREREG_S1B1R_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-S1B1R.md")
S1B1R_AMEND1_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-S1B1R-AMEND-1.md")
TEST_SPLITS = C.TEST_SPLITS
TYPE_WORDS = {"shape": list(W.SHAPES), "colour": list(W.COLOUR_NAMES), "size": list(W.SIZE_NAMES)}
# PREREG-S1B1 §4, §5, §9: the new bars' fractions and refutation constants
M3_VS_PORACLE, SPOKEN_VS_PORACLE, TRUTH_VS_PORACLE, ORDER_VS_PORACLE, DECLINE_VS_PORACLE = 0.80, 0.80, 0.90, 0.95, 0.90
DECLINE_ORGAN = 0.80                  # P-ORACLE's DECLINE below it → CEILING-BOUND (purple inside a trained colour's band)
T3_REFUTE = 0.80
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
    s1 = hashlib.sha256(PREREG_S1B1_PATH.read_bytes()).hexdigest()
    if s1 != PREREG_S1B1_SHA256:
        raise RunError(f"PREREG-S1B1 sha256 {s1} ≠ the co-signed {PREREG_S1B1_SHA256} — STOP and hand back")
    # PREREG-S1B1R and its AMENDMENT 1 (edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:00 +0400): checked at every run command
    r = hashlib.sha256(PREREG_S1B1R_PATH.read_bytes()).hexdigest()
    if r != PREREG_S1B1R_SHA256:
        raise RunError(f"PREREG-S1B1R sha256 {r} ≠ the co-signed {PREREG_S1B1R_SHA256} — STOP and hand back")
    a1 = hashlib.sha256(S1B1R_AMEND1_PATH.read_bytes()).hexdigest()
    if a1 != S1B1R_AMEND1_SHA256:
        raise RunError(f"PREREG-S1B1R AMENDMENT 1 sha256 {a1} ≠ the co-signed {S1B1R_AMEND1_SHA256} — STOP and hand back")
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
    # PREREG-S1B1 §4–§5: M3 (a phrase, like M1), SPEAK / DECLINE (a POINTER to the target: its hypothesis for the gaze
    # arms, the thing itself for ORACLE-TRUTH — «this one», never its name); a target without a hypothesis is uncovered
    tr = {s: C.load_truth(C.cache_dir(root, ws, s)) for s in ("m3", "speak", "decline")}
    th = {s: Things(C.ScenePercepts(C.cache_dir(root, ws, s))) for s in ("speak", "decline")}
    m3 = M.m3_items(tr["m3"])
    speak = M.speak_items(tr["speak"])
    decline = M.decline_items(tr["decline"])
    q["M3"] = [{**M.question(it), "split": "m3"} for it in m3]
    for mark, items, split in (("SPEAK", speak, "speak"), ("DECLINE", decline, "decline")):
        q[mark] = []
        for it in items:
            r = tr[split][it["row"]]
            mem, pos = th[split].members(it["row"])
            hyp = M.thing_hypothesis(it["target"], mem, pos, r["fix_thing"], tuple(r["centroids"][it["target"]]))
            it["hyp"] = hyp
            q[mark].append({**M.question(it), "split": split, "hyp": hyp, "thing": it["target"]})
    out["questions"] = q
    out["prereg_s1b1_sha256"] = keys["prereg_s1b1_sha256"] = PREREG_S1B1_SHA256
    keys["items"] = {"M1": m1, "M2a": m2a, "M2b": m2b, "M6": m6, "NAME": name, "M3": m3, "SPEAK": speak, "DECLINE": decline}
    d = seed_root(root, ws)
    dump(d / "questions.json", out)
    dump(d / "keys.json", keys)
    return {"M1": len(m1), "M2a": len(m2a), "M2b": len(m2b), "M6": len(m6), "NAME": len(name), "M3": len(m3),
            "SPEAK": len(speak), "DECLINE": len(decline)}


# ------------------------------------------------------------------------------------------------ answering
def answer_all(arm: str, learner, questions: Dict[str, List[Dict[str, object]]], things: Dict[str, Things],
               test_seed: int) -> Dict[str, Dict[str, object]]:
    ans: Dict[str, Dict[str, object]] = {}
    for mark in ("M1", "M2a", "M6", "M3"):
        for q in questions.get(mark, []):
            X = things[q["split"]].for_arm(arm, q["row"])
            a = learner.answer_point(X, q["phrase"], M.tie_rng(test_seed, q["item_id"]))
            ans[q["item_id"]] = a

    def emits(x) -> Dict[str, List[str]]:
        # the law's «what is this?», and for the RW arms readings (i) and (ii) from the same state (PREREG-S1B1 §3)
        if arm in RW_ARMS:
            r = learner.what_is_this_readings(x)
            return {"emit": r["law"], "emit_i": r["i"], "emit_ii": r["ii"]}
        return {"emit": learner.what_is_this(x)}

    for q in questions.get("M2b", []):
        k = 0 if arm == "ORACLE-TRUTH" else q.get("hyp")
        if k is None:
            ans[q["item_id"]] = {"emit": None, "uncovered": True}
            continue
        X = things[q["split"]].for_arm(arm, q["row"])
        ans[q["item_id"]] = emits(X[int(k)])
    for q in questions.get("NAME", []):
        k = 0 if arm == "ORACLE-TRUTH" else q.get("hyp")
        if k is None:
            ans[q["item_id"]] = {"name": None, "uncovered": True}
            continue
        X = things[q["split"]].for_arm(arm, q["row"])
        ans[q["item_id"]] = {"name": {t: learner.name_forced(X[int(k)], ws) for t, ws in TYPE_WORDS.items()},
                             **emits(X[int(k)])}
    # PREREG-S1B1 §5: the SAME production code for every arm; its read-backs use the item's own tie generator
    for mark in ("SPEAK", "DECLINE"):
        for q in questions.get(mark, []):
            k = q.get("thing") if arm == "ORACLE-TRUTH" else q.get("hyp")
            if k is None:
                ans[q["item_id"]] = {"spoken": None, "reason": "uncovered", "uncovered": True}
                continue
            X = things[q["split"]].for_arm(arm, q["row"])
            a = Lr.produce(learner, X, int(k), lambda q=q: M.tie_rng(test_seed, q["item_id"]))
            if mark == "DECLINE" and arm in LDA_ARMS:
                a["colour_fit"] = learner.colour_fit(X[int(k)])     # the organ fact (§5): d_w / B_w per colour word
            ans[q["item_id"]] = a
    return ans


def make_learner(arm: str, lr: float, eps: float):
    """PREREG-S1B1 §6: every RW arm takes its OWN lr from ARM_LR (A-RW 0.01, the law; A-RW-LR10 0.1, S1a's law as a
    reading; N-SHUF and P-ORACLE-RW 0.01) — `lr` is kept in the signature for the callers and the gate's record. The
    oracle arms read with the TYPE-AWARE reader (AMENDMENT 2 §1), handed the word types from here (no RW arm ever holds
    them), τ_point at conformal 0.95 over training scenes with ≥ 2 hypotheses / things (PREREG-S1B1 §3)."""
    if arm in RW_ARMS:
        return Lr.RWLearner(lr=ARM_LR.get(arm, lr), oracle=(arm == "P-ORACLE-RW"))
    if arm in LDA_ARMS:
        return Lr.TypedLDAReader(eps, WORD_TYPES, point_level=Lr.NONE_LEVEL, point_min_view=Lr.NONE_MIN_VIEW)
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
            # n_view: the scene's hypotheses (P-ORACLE) or things (ORACLE-TRUTH) — τ_point's population (PREREG-S1B1 §3)
            learner.train_scene(Lr.feed_oracle(X, ref), words, n_view=int(np.atleast_2d(X).shape[0]))


def prepare(arm: str, learner, seen: Optional[list]) -> Dict[str, object]:
    if arm in RW_ARMS:
        return learner.calibrate(seen or [])
    return learner.prepare()


def gate_or_chosen(root: Path = C.RUNS) -> Dict[str, object]:
    """The first gate's choices (lr, ε), read from its record under `root` — the full run never re-chooses them."""
    p = Path(root) / "gate" / "gate.json"
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
        g = gate_or_chosen(root)
        lr = g["lr"] if lr is None else lr
        eps = g["eps"] if eps is None else eps
    out = Path(out) if out is not None else seed_root(root, ws) / "arms" / arm
    out.mkdir(parents=True, exist_ok=True)
    Q = json.loads((seed_root(root, ws) / "questions.json").read_text())
    if Q["prereg_sha256"] != PREREG_SHA256:
        raise RunError("questions were written under another PREREG")
    things = {s: Things(C.ScenePercepts(C.cache_dir(root, ws, s))) for s in TEST_SPLITS}
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
              "amend2_sha256": AMEND2_SHA256, "prereg_s1b1_sha256": PREREG_S1B1_SHA256, "code": code_identity(),
              "reading_points": {}}
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
    """Every arm at every reading point, every mark of PREREG-S1B1 §7 (edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:53 +0400):
    S1a's M1 / M2a / M2b / M6 / NAME (the law, and for the RW arms readings (i) and (ii) from the same state), M3, SPEAK,
    DECLINE (with P-ORACLE's purple organ fact)."""
    K = json.loads((seed_root(root, ws) / "keys.json").read_text())
    Q = json.loads((seed_root(root, ws) / "questions.json").read_text())["questions"]
    items = K["items"]
    truth = {s: C.load_truth(C.cache_dir(root, ws, s)) for s in TEST_SPLITS}
    things = {s: Things(C.ScenePercepts(C.cache_dir(root, ws, s))) for s in TEST_SPLITS}
    m2b_cov = {it["row"] for it in items["M2b"] if M.covered(0, truth["m2b"][it["row"]]["fix_thing"])}
    tr = C.load_truth(C.cache_dir(root, ws, "train"))
    seen = M.meeting_seen(tr[W.DAX_INDEX]) if len(tr) > W.DAX_INDEX else None      # AMENDMENT 2 §3
    ptr_gaze = {q["item_id"]: q.get("hyp") for m in ("SPEAK", "DECLINE") for q in Q.get(m, [])}
    ptr_truth = {q["item_id"]: q.get("thing") for m in ("SPEAK", "DECLINE") for q in Q.get(m, [])}
    out = {"prereg_sha256": PREREG_SHA256, "amend2_sha256": AMEND2_SHA256, "prereg_s1b1_sha256": PREREG_S1B1_SHA256,
           "world_seed": ws, "meeting_seen": seen, "arms": {}}
    for arm in arms:
        d = seed_root(root, ws) / "arms" / arm
        rec = json.loads((d / "record.json").read_text())
        kind = "truth" if arm == "ORACLE-TRUTH" else "gaze"
        ptr = ptr_truth if kind == "truth" else ptr_gaze
        out["arms"][arm] = {"lr": rec["lr"], "eps": rec["eps"], "cpu_s": rec["cpu_s"], "wall_s": rec["wall_s"], "rp": {}}
        for rp in sorted(int(k) for k in rec["reading_points"]):
            A = json.loads((d / f"answers_{rp:05d}.json").read_text())["answers"]
            g1 = M.grade_pointing(items["M1"], A, truth["test"], things["test"].members, kind)
            g6 = M.grade_pointing(items["M6"], A, truth["m6"], things["m6"].members, kind)
            g3 = M.grade_pointing(items["M3"], A, truth["m3"], things["m3"].members, kind)
            names = {}
            for t in TYPE_WORDS:
                rows = [(A.get(it["item_id"]) or {}).get("name") for it in items["NAME"]]
                ok = [nm[t] == it[t] for nm, it in zip(rows, items["NAME"]) if nm is not None and nm.get(t) is not None]
                names[t] = {"acc": (sum(ok) / len(ok) if ok else None), "n": len(ok)}
                for key in ("emit", "emit_i", "emit_ii"):
                    em = [it[t] in (A.get(it["item_id"]) or {}).get(key) for it in items["NAME"]
                          if (A.get(it["item_id"]) or {}).get(key) is not None]
                    names[t]["true_" + key] = (sum(em) / len(em) if em else None)
                names[t]["emit_true"] = names[t]["true_emit"]
            dc_rows = M.grade_decline(items["DECLINE"], A, truth["decline"], ptr)
            organ = None
            if arm in LDA_ARMS:
                fits = [(A.get(it["item_id"]) or {}).get("colour_fit") for it, r in zip(items["DECLINE"], dc_rows) if r["covered"]]
                fits = [f for f in fits if f]
                organ = {w: {"mean_d_over_B": float(np.mean([f[w] for f in fits if w in f])),
                             "inside_band": float(np.mean([f[w] <= 1.0 for f in fits if w in f])), "n": len(fits)}
                         for w in W.COLOUR_NAMES if any(w in f for f in fits)}
            out["arms"][arm]["rp"][str(rp)] = {
                "M1": M.summarise_pointing(g1), "M6": M.summarise_pointing(g6), "M3": M.summarise_m3(g3, items["M3"]),
                "M2a": {k: M.grade_m2a(items["M2a"], A, key) for k, key in (("law", "none"), ("i", "none_i"), ("ii", "none_ii"))},
                "M2b": {k: M.grade_m2b(items["M2b"], A, None if kind == "truth" else m2b_cov, key)
                        for k, key in (("law", "emit"), ("i", "emit_i"), ("ii", "emit_ii"))},
                "NAME": names,
                "SPEAK": M.summarise_speak(M.grade_speak(items["SPEAK"], A, truth["speak"], ptr)),
                "DECLINE": M.summarise_decline(dc_rows), "organ_purple": organ,
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


def _frac(k, v):
    return None if v is None else k * v


def s1a_beside(ws: int, rp: str = str(W.N_TRAIN)) -> Optional[Dict[str, object]]:
    """S1a's A-RW (and P-ORACLE) readings on the IDENTICAL items (S1a's own marks.json under its run root; the item ids
    are TESTED equal at the gate) — printed beside every re-read line (PREREG-S1B1 §7)."""
    p = C.S1A_RUNS / str(ws) / "marks.json"
    if not p.exists():
        return None
    mk = json.loads(p.read_text())
    out = {}
    for arm in ("A-RW", "P-ORACLE"):
        R = mk["arms"].get(arm, {}).get("rp", {}).get(rp)
        if R is None:
            continue
        out[arm] = {"M1": R["M1"]["graded"]["covered"], "M2a_refusal": R["M2a"]["all"]["refusal"],
                    "M2a_false_refusal": R["M1"]["graded"]["false_refusal"], "M2b": R["M2b"]["graded"]["correct"],
                    "M6": R["M6"]["all"]["covered"]}
    out["meeting_seen"] = mk.get("meeting_seen")
    return out


def decline_reading(value: Optional[float], p_oracle: Optional[float], spoken_pass: bool) -> Dict[str, object]:
    """DECLINE's verdict pieces, in PREREG-S1B1 §5's own order (edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 14:13 +0400 — after the
    unit, the organ clause is read as written): the guard (DECLINE reads only when SPOKEN meets its bar, else NOT
    GRADABLE); the ORGAN CLAUSE (P-ORACLE's DECLINE < 0.80 → CEILING-BOUND — purple inside a trained colour's band —
    whatever the learner reads); then the fraction bar (≥ 0.90 × P-ORACLE), whose reading is printed beside either way."""
    bar = _frac(DECLINE_VS_PORACLE, p_oracle)
    met = _ge(value, bar)
    if not spoken_pass:
        return {"bar": bar, "fraction_met": met, "pass": False, "ceiling_bound": False,
                "not_gradable": "the mouth is silent (SPOKEN below its bar)"}
    organ = p_oracle is not None and p_oracle < DECLINE_ORGAN
    return {"bar": bar, "fraction_met": met, "pass": met and not organ, "ceiling_bound": organ, "not_gradable": False}


def t4p_reading(m2b_law: Optional[float], m2b_ii: Optional[float], p_oracle: Optional[float]) -> Dict[str, bool]:
    """T4′'s three clauses (PREREG-S1B1 §3, §9), per seed: «spread is the limit» = M2b < 0.80 while P-ORACLE ≥ 0.80 and
    reading (ii) is NO WORSE than the law ((ii) ≥ the law); «(ii) above the law by ≥ 0.05» (read at ≥ 2 seeds in the
    report); «the learner refuses» = M2b ≥ 0.80. (edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 14:13 +0400 — the report had the
    first clause's comparison reversed.)"""
    have = m2b_law is not None and m2b_ii is not None
    return {"spread_is_the_limit": bool(have and m2b_law < M.BARS["M2b"] and (p_oracle or 0) >= M.BARS["M2b"] and m2b_ii >= m2b_law),
            "ii_above_by_005": bool(have and m2b_ii >= m2b_law + 0.05),
            "learner_refuses": bool(m2b_law is not None and m2b_law >= M.BARS["M2b"])}


def bars_for(marks: Dict[str, object], rp: str = str(W.N_TRAIN)) -> Dict[str, object]:
    """PREREG-S1B1 §7's bars for one seed, at `rp`, P-ORACLE's reading beside every mark (a fraction of the oracle on the
    SAME items, #228 (b)); a mark with n < 30 reads UNDERPOWERED; a reading of nothing reads NOT GRADABLE, never 0.0."""
    A = {a: marks["arms"][a]["rp"].get(rp) for a in marks["arms"]}
    m1 = lambda arm, key="graded": A[arm]["M1"][key]
    r: Dict[str, object] = {}
    rows = {}
    for key in ("graded", "size2", "size3"):
        a = m1("A-RW", key)
        prw, po = m1("P-ORACLE-RW", key)["covered"], m1("P-ORACLE", key)["covered"]
        bar_rw, bar_lda = _frac(M.BARS["M1_vs_PORACLE_RW"], prw), _frac(M.BARS["M1_vs_PORACLE"], po)
        rows[key] = {"value": a["covered"], "n": a["n_covered"], "all": a["all"], "n_all": a["n_all"],
                     "coverage": a["coverage"], "chance": a["chance_covered"], "p_oracle": po, "p_oracle_rw": prw,
                     "bar_rw": bar_rw, "bar_lda": bar_lda, "pass": _ge(a["covered"], bar_rw) and _ge(a["covered"], bar_lda),
                     "lr10": m1("A-RW-LR10", key)["covered"] if "A-RW-LR10" in A else None,
                     "oracle_truth": m1("ORACLE-TRUTH", key)["covered"], "n_unheard": a["n_unheard"]}
    r["M1"] = dict(rows["graded"])
    r["M1"]["by_size"] = {"size2": rows["size2"], "size3": rows["size3"]}
    r["M1"]["sanity_size1"] = {"value": m1("A-RW", "size1")["covered"], "n": m1("A-RW", "size1")["n_covered"]}
    # M2a — the law (per half), the readings beside
    law = A["A-RW"]["M2a"]["law"]["all"]
    fr = m1("A-RW")["false_refusal"]
    po2, po_fr = A["P-ORACLE"]["M2a"]["law"]["all"]["refusal"], m1("P-ORACLE")["false_refusal"]
    v2 = M.m2a_verdict(law["refusal"], fr, po2, po_fr)
    r["M2a"] = {"value": law["refusal"], "n": law["n"], "false_refusal": fr, "n_fr": m1("A-RW")["n_fr"], "p_oracle": po2,
                "p_oracle_fr": po_fr, "pass": v2["pass"], "ceiling_bound": v2["ceiling_bound"],
                "failing_halves": v2["failing_halves"], "whole_bar_ceiling": v2["whole_bar_ceiling"],
                "expected_false_refusal": 1.0 - Lr.NONE_LEVEL,
                "reading_i": {"refusal": A["A-RW"]["M2a"]["i"]["all"]["refusal"], "false_refusal": m1("A-RW").get("false_refusal_i")},
                "reading_ii": {"refusal": A["A-RW"]["M2a"]["ii"]["all"]["refusal"], "false_refusal": m1("A-RW").get("false_refusal_ii")},
                "lr10": {"refusal": A["A-RW-LR10"]["M2a"]["law"]["all"]["refusal"], "false_refusal": m1("A-RW-LR10")["false_refusal"]}}
    # M2b — the law; CEILING-BOUND when the oracle reads below the absolute bar
    m2b = A["A-RW"]["M2b"]["law"]["graded"]
    po3 = A["P-ORACLE"]["M2b"]["law"]["graded"]["correct"]
    ok3 = _ge(m2b["correct"], M.BARS["M2b"])
    r["M2b"] = {"value": m2b["correct"], "n": m2b["n"], "p_oracle": po3, "pass": ok3,
                "ceiling_bound": (not ok3) and po3 is not None and po3 < M.BARS["M2b"],
                "diamond": A["A-RW"]["M2b"]["law"]["diamond"]["correct"],
                "diamond_p_oracle": A["P-ORACLE"]["M2b"]["law"]["diamond"]["correct"],
                "reading_i": A["A-RW"]["M2b"]["i"]["graded"]["correct"], "reading_ii": A["A-RW"]["M2b"]["ii"]["graded"]["correct"],
                "lr10": A["A-RW-LR10"]["M2b"]["law"]["graded"]["correct"],
                "shape_words": A["A-RW"]["M2b"]["law"]["graded"]["shape_words_emitted"],
                "idk": A["A-RW"]["M2b"]["law"]["graded"]["idk"]}
    # M6 — only where the meeting was seen
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
                   "ceiling_bound": (not ok6) and (po6 is None or po6 < M.BARS["M6"])}
    # M3 COMPOSE (§4)
    a3 = A["A-RW"]["M3"]["all"]
    p3 = A["P-ORACLE"]["M3"]["all"]["covered"]
    bar3 = _frac(M3_VS_PORACLE, p3)
    r["M3"] = {"value": a3["covered"], "n": a3["n_covered"], "all": a3["all"], "n_all": a3["n_all"], "chance": a3["chance_covered"],
               "p_oracle": p3, "bar": bar3, "pass": _ge(a3["covered"], bar3),
               "p_oracle_rw": A["P-ORACLE-RW"]["M3"]["all"]["covered"],
               "p_oracle_rw_090": _frac(0.90, A["P-ORACLE-RW"]["M3"]["all"]["covered"]),
               "lr10": A["A-RW-LR10"]["M3"]["all"]["covered"],
               "by_kind": {k: A["A-RW"]["M3"][f"kind:{k}"]["covered"] for k in ("colour", "shape", "both")},
               "by_kind_p_oracle": {k: A["P-ORACLE"]["M3"][f"kind:{k}"]["covered"] for k in ("colour", "shape", "both")},
               "by_size": {f"size{n}": A["A-RW"]["M3"][f"size{n}"]["covered"] for n in (2, 3)},
               "by_pair": {f"{sh}-{co}": A["A-RW"]["M3"][f"pair:{sh}-{co}"]["covered"] for sh, co in W.HELDOUT}}
    # SPEAK (§5) — fractions of P-ORACLE on the same items; READ-BACK is the wiring pin
    sp, psp = A["A-RW"]["SPEAK"], A["P-ORACLE"]["SPEAK"]
    b_sp = _frac(SPOKEN_VS_PORACLE, psp["spoken"])
    r["SPOKEN"] = {"value": sp["spoken"], "n": sp["n_covered"], "p_oracle": psp["spoken"], "bar": b_sp,
                   "pass": _ge(sp["spoken"], b_sp), "all": sp["spoken_all"], "reasons": sp["reasons"],
                   "lr10": A["A-RW-LR10"]["SPEAK"]["spoken"], "n_shuf": A["N-SHUF"]["SPEAK"]["spoken"]}
    b_tr = _frac(TRUTH_VS_PORACLE, psp["truth"])
    r["TRUTH"] = {"value": sp["truth"], "n": sp["n_spoken"], "p_oracle": psp["truth"], "n_p_oracle": psp["n_spoken"],
                  "bar": b_tr, "pass": _ge(sp["truth"], b_tr), "truth_seen": sp["truth_seen"],
                  "truth_x_spoken": sp["truth_x_spoken"], "p_oracle_truth_x_spoken": psp["truth_x_spoken"],
                  "lr10": A["A-RW-LR10"]["SPEAK"]["truth"], "n_shuf": A["N-SHUF"]["SPEAK"]["truth"],
                  "n_shuf_chance": A["N-SHUF"]["SPEAK"]["chance_truth"]}
    r["READ-BACK"] = {"value": sp["readback"], "n": sp["n_spoken"], "pass": sp["readback"] == 1.0 if sp["readback"] is not None else False,
                      "p_oracle": psp["readback"], "not_gradable": ("nothing spoken" if sp["readback"] is None else False)}
    b_or = _frac(ORDER_VS_PORACLE, psp["order"])
    r["ORDER"] = {"value": sp["order"], "n": sp["n_multi"], "p_oracle": psp["order"], "bar": b_or,
                  "pass": _ge(sp["order"], b_or), "length_mix": sp["length_mix"], "parent_mix": {"1": 0.25, "2": 0.5, "3": 0.25},
                  "not_gradable": ("no multi-word phrase spoken" if sp["order"] is None else False)}
    # DECLINE (§5): reads only with SPOKEN at its bar; CEILING-BOUND if the oracle reads < 0.80
    dc, pdc = A["A-RW"]["DECLINE"], A["P-ORACLE"]["DECLINE"]
    r["DECLINE"] = {"value": dc["decline"], "n": dc["n_covered"], "p_oracle": pdc["decline"],
                    **decline_reading(dc["decline"], pdc["decline"], bool(r["SPOKEN"]["pass"]))}
    r["DECLINE"].update({"kind_A_spoken": dc["kind_A_spoken"], "kind_A_truth": dc["kind_A_truth"],
                         "kind_B_decline_rate": dc["kind_B_decline_rate"], "reasons": dc["reasons"],
                         "organ_purple": A["P-ORACLE"].get("organ_purple"), "lr10": A["A-RW-LR10"]["DECLINE"]["decline"]})
    # the nulls
    ns = m1("N-SHUF")
    nbar = None if ns["chance_covered"] is None else ns["chance_covered"] + M.BARS["NSHUF_over_chance"]
    r["N-SHUF"] = {"value": ns["covered"], "chance": ns["chance_covered"], "bar": nbar, "pass": _le(ns["covered"], nbar)}
    n3 = A["N-SHUF"]["M3"]["all"]
    r["N-SHUF-M3"] = {"value": n3["covered"], "chance": n3["chance_covered"],
                      "bar": None if n3["chance_covered"] is None else n3["chance_covered"] + M.BARS["NSHUF_over_chance"],
                      "pass": _le(n3["covered"], None if n3["chance_covered"] is None else n3["chance_covered"] + M.BARS["NSHUF_over_chance"])}
    for k in ("M1", "M2a", "M2b", "M6", "M3", "SPOKEN", "TRUTH", "DECLINE"):
        r[k]["underpowered"] = (not r[k].get("not_gradable")) and (r[k]["n"] or 0) < M.UNDERPOWERED_N
    r["ORDER"]["underpowered"] = False
    r["READ-BACK"]["underpowered"] = False
    # the refutations (§9), per seed; the lr law's is read across seeds in the report
    prw = r["M1"]["p_oracle_rw"]
    m1p = r["M1"]["pass"]
    r["refute"] = {
        "T1": bool(r["M1"]["value"] is not None and prw is not None and r["M1"]["value"] < M.T1_REFUTE * prw),
        "lr_below_lr10": bool(r["M1"]["value"] is not None and r["M1"]["lr10"] is not None and r["M1"]["value"] < r["M1"]["lr10"]),
        "T2": bool(m1p and r["M3"]["value"] is not None and p3 is not None and r["M3"]["value"] < M.T1_REFUTE * p3),
        "T3": bool(m1p and r["TRUTH"]["value"] is not None and (r["TRUTH"]["n"] or 0) >= M.UNDERPOWERED_N and r["TRUTH"]["value"] < T3_REFUTE),
        **{f"T4p_{k}" if k != "ii_above_by_005" else "T4p_ii_above_law_by_005": v
           for k, v in t4p_reading(r["M2b"]["value"], r["M2b"]["reading_ii"], po3).items()},
        "one_meeting": bool((not r["M6"].get("not_gradable")) and r["M6"]["value"] is not None and r["M6"]["value"] < M.M6_REFUTE and m1p)}
    return r


MARK_ORDER = ("M1", "M2a", "M2b", "M6", "M3", "SPOKEN", "TRUTH", "READ-BACK", "ORDER", "DECLINE", "N-SHUF", "N-SHUF-M3")


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


def print_seed_table(marks: Dict[str, object], log=print) -> List[str]:
    ws = marks["world_seed"]
    arms = [a for a in ARMS if a in marks["arms"]]
    lines = [f"== S1b-1 marks · world seed {ws} (test seed {W.TEST_SEEDS[ws]}) · the one meeting seen: {marks.get('meeting_seen')} =="]
    rps = sorted(int(k) for k in marks["arms"]["A-RW"]["rp"])
    lines.append("M1 (covered, the graded 2- and 3-thing items) / M3 (covered) by reading point — A-RW-LR10 is S1a's law, a reading:")
    lines.append("   arm            " + " ".join(f"{rp:>11d}" for rp in rps))
    for arm in arms:
        vals = [(marks["arms"][arm]["rp"][str(rp)]["M1"]["graded"]["covered"], marks["arms"][arm]["rp"][str(rp)]["M3"]["all"]["covered"]) for rp in rps]
        lines.append(f"   {arm:<14} " + " ".join(f"{_f(a)}/{_f(b)}" for a, b in vals))
    top = str(max(rps))
    lines.append(f"At {top} scenes (covered · all), chance and n from A-RW's items:")
    for key in ["graded", "size2", "size3", "size1"]:
        b0 = marks["arms"]["A-RW"]["rp"][top]["M1"][key]
        lines.append(f"   M1 {key:<8} cov {_f(b0.get('coverage'))} chance {_f(b0.get('chance_covered'))} n {b0.get('n_covered')}/{b0.get('n_all')} | "
                     + " | ".join(f"{a} {_f(marks['arms'][a]['rp'][top]['M1'][key]['covered'])}·{_f(marks['arms'][a]['rp'][top]['M1'][key]['all'])}" for a in arms))
    for key in ["all", "kind:colour", "kind:shape", "kind:both", "size2", "size3"] + [f"pair:{sh}-{co}" for sh, co in W.HELDOUT]:
        b0 = marks["arms"]["A-RW"]["rp"][top]["M3"][key]
        lines.append(f"   M3 {key:<22} chance {_f(b0.get('chance_covered'))} n {b0.get('n_covered')}/{b0.get('n_all')} | "
                     + " | ".join(f"{a} {_f(marks['arms'][a]['rp'][top]['M3'][key]['covered'])}" for a in arms))
    for arm in arms:
        R = marks["arms"][arm]["rp"][top]
        g = R["M1"]["graded"]
        m2a = R["M2a"]
        m2b = R["M2b"]
        nm = R["NAME"]
        rw = arm in RW_ARMS
        lines.append(f"   {arm:<14} M2a refusal {_f(m2a['law']['all']['refusal'])} false {_f(g['false_refusal'])}"
                     + (f" [(i) {_f(m2a['i']['all']['refusal'])}/{_f(g.get('false_refusal_i'))} · (ii) {_f(m2a['ii']['all']['refusal'])}/{_f(g.get('false_refusal_ii'))}]" if rw else "")
                     + f" · M2b {_f(m2b['law']['graded']['correct'])} (idk {_f(m2b['law']['graded']['idk'])}; diamond {_f(m2b['law']['diamond']['correct'])})"
                     + (f" [(i) {_f(m2b['i']['graded']['correct'])} · (ii) {_f(m2b['ii']['graded']['correct'])}]" if rw else "")
                     + " · M6 " + (f"{_f(R['M6']['all']['covered'])} (n {R['M6']['all']['n_covered']})" if marks.get("meeting_seen") is True else "NOT GRADABLE")
                     + f" · NAME emits the true word: shape {_f(nm['shape']['true_emit'])} colour {_f(nm['colour']['true_emit'])} size {_f(nm['size']['true_emit'])}"
                     + (f" [(i) {_f(nm['shape']['true_emit_i'])}/{_f(nm['colour']['true_emit_i'])}/{_f(nm['size']['true_emit_i'])}]" if rw else ""))
        sp, dc = R["SPEAK"], R["DECLINE"]
        lines.append(f"   {'':<14} SPEAK spoken {_f(sp['spoken'])} (n {sp['n_covered']}; all {_f(sp['spoken_all'])}) · truth {_f(sp['truth'])} (n {sp['n_spoken']}; seen {_f(sp['truth_seen'])}; ×spoken {_f(sp['truth_x_spoken'])})"
                     f" · read-back {_f(sp['readback'])} · order {_f(sp['order'])} (n {sp['n_multi']}) · lengths {sp['length_mix']} · reasons {sp['reasons']}"
                     f" · DECLINE {_f(dc['decline'])} (n {dc['n_covered']}; A spoken {_f(dc['kind_A_spoken'])} truth {_f(dc['kind_A_truth'])}; B decline {_f(dc['kind_B_decline_rate'])})")
    org = marks["arms"]["P-ORACLE"]["rp"][top].get("organ_purple")
    if org:
        lines.append("   the organ fact (P-ORACLE's colour d_w / B_w of the purple targets): " + " · ".join(
            f"{w} mean {v['mean_d_over_B']:.2f} inside {v['inside_band']:.2f}" for w, v in org.items()))
    for l in lines:
        log(l)
    return lines


def report(root: Path, log=print, dest: Optional[Path] = None) -> Dict[str, object]:
    out = {"prereg_sha256": PREREG_SHA256, "amend2_sha256": AMEND2_SHA256, "prereg_s1b1_sha256": PREREG_S1B1_SHA256, "seeds": {}}
    lines: List[str] = [f"S1b-1 report · PREREG-S1B1 sha {PREREG_S1B1_SHA256} · PREREG-R3-TONIGHT {PREREG_SHA256[:16]}… · AMEND-2 {AMEND2_SHA256[:16]}…", ""]
    for ws in W.WORLD_SEEDS:
        mk = json.loads((seed_root(root, ws) / "marks.json").read_text())
        lines += print_seed_table(mk, log=lambda s: None)
        b = bars_for(mk)
        b["s1a"] = s1a_beside(ws)
        out["seeds"][str(ws)] = b
        lines.append("")
    lines.append("== S1b-1 BARS at 10,000 scenes (A-RW, the law lr 0.01; P-ORACLE beside every mark; S1a's A-RW on the identical items beside) ==")
    for ws in W.WORLD_SEEDS:
        b = out["seeds"][str(ws)]
        s1a = (b.get("s1a") or {}).get("A-RW", {})
        m1 = b["M1"]
        lines.append(f"{ws} M1 {_f(m1['value'])} (all {_f(m1['all'])}; n {m1['n']}/{m1['n_all']}; chance {_f(m1['chance'])}) bars ≥ {_f(m1['bar_rw'])} (0.90 × P-ORACLE-RW {_f(m1['p_oracle_rw'])}) "
                     f"and ≥ {_f(m1['bar_lda'])} (0.80 × P-ORACLE {_f(m1['p_oracle'])}) → {_verdict(m1)} · A-RW-LR10 {_f(m1['lr10'])} · S1a {_f(s1a.get('M1'))}")
        for k, v in m1["by_size"].items():
            lines.append(f"          M1 {k}: {_f(v['value'])} (n {v['n']}, chance {_f(v['chance'])}) → {_verdict(v)} · A-RW-LR10 {_f(v['lr10'])}")
        m2a = b["M2a"]
        lines.append(f"          M2a refusal {_f(m2a['value'])} (n {m2a['n']}) · false refusal {_f(m2a['false_refusal'])} (n {m2a['n_fr']}; expected {m2a['expected_false_refusal']:.2f}) "
                     f"· P-ORACLE {_f(m2a['p_oracle'])} / {_f(m2a['p_oracle_fr'])} → {_verdict(m2a)}"
                     + (f" (the learner fails: {', '.join(m2a['failing_halves'])}; whole-bar: {'CEILING-BOUND' if m2a['whole_bar_ceiling'] else 'FAIL'})" if not m2a["pass"] else "")
                     + f" · (i) {_f(m2a['reading_i']['refusal'])}/{_f(m2a['reading_i']['false_refusal'])} · (ii) {_f(m2a['reading_ii']['refusal'])}/{_f(m2a['reading_ii']['false_refusal'])}"
                     + f" · A-RW-LR10 {_f(m2a['lr10']['refusal'])}/{_f(m2a['lr10']['false_refusal'])} · S1a {_f(s1a.get('M2a_refusal'))}/{_f(s1a.get('M2a_false_refusal'))}")
        m2b = b["M2b"]
        lines.append(f"          M2b {_f(m2b['value'])} (n {m2b['n']}; «I don't know» {_f(m2b['idk'])}) · P-ORACLE {_f(m2b['p_oracle'])} → {_verdict(m2b)} · (i) {_f(m2b['reading_i'])} · (ii) {_f(m2b['reading_ii'])} "
                     f"· A-RW-LR10 {_f(m2b['lr10'])} · S1a {_f(s1a.get('M2b'))} · diamond (apart) {_f(m2b['diamond'])} · P-ORACLE {_f(m2b['diamond_p_oracle'])} · shape words said {m2b['shape_words']}")
        m6 = b["M6"]
        lines.append("          M6 " + (f"NOT GRADABLE — {m6['not_gradable']}" if m6.get("not_gradable") else
                                          f"{_f(m6['value'])} (all {_f(m6['all'])}; n {m6['n']}/{m6['n_all']}; chance {_f(m6['chance'])}) · P-ORACLE {_f(m6['p_oracle'])} → {_verdict(m6)}")
                     + f" · S1a {_f(s1a.get('M6'))}")
        m3 = b["M3"]
        lines.append(f"          M3 {_f(m3['value'])} (all {_f(m3['all'])}; n {m3['n']}/{m3['n_all']}; chance {_f(m3['chance'])}) bar ≥ {_f(m3['bar'])} (0.80 × P-ORACLE {_f(m3['p_oracle'])}) → {_verdict(m3)} "
                     f"· kinds colour {_f(m3['by_kind']['colour'])} shape {_f(m3['by_kind']['shape'])} both {_f(m3['by_kind']['both'])} · P-ORACLE-RW {_f(m3['p_oracle_rw'])} (0.90× {_f(m3['p_oracle_rw_090'])}, a reading) · A-RW-LR10 {_f(m3['lr10'])}")
        s, t, rb, o, dcl = b["SPOKEN"], b["TRUTH"], b["READ-BACK"], b["ORDER"], b["DECLINE"]
        lines.append(f"          SPOKEN {_f(s['value'])} (n {s['n']}) ≥ {_f(s['bar'])} (0.80 × P-ORACLE {_f(s['p_oracle'])}) → {_verdict(s)} · reasons {s['reasons']} · A-RW-LR10 {_f(s['lr10'])} · N-SHUF {_f(s['n_shuf'])}")
        lines.append(f"          TRUTH {_f(t['value'])} (n {t['n']}) ≥ {_f(t['bar'])} (0.90 × P-ORACLE {_f(t['p_oracle'])}, n {t['n_p_oracle']}) → {_verdict(t)} · seen {_f(t['truth_seen'])} · ×spoken {_f(t['truth_x_spoken'])} "
                     f"(P-ORACLE {_f(t['p_oracle_truth_x_spoken'])}) · A-RW-LR10 {_f(t['lr10'])} · N-SHUF {_f(t['n_shuf'])} vs a random true phrase {_f(t['n_shuf_chance'])}")
        lines.append(f"          READ-BACK {_f(rb['value'])} (n {rb['n']}; the wiring pin = 1.000) → {_verdict(rb) if rb['value'] is None or rb['value'] == 1.0 else 'BROKEN ROAD'} · "
                     f"ORDER {_f(o['value'])} (n {o['n']}) ≥ {_f(o['bar'])} (0.95 × P-ORACLE {_f(o['p_oracle'])}) → {_verdict(o)} · lengths {o['length_mix']} vs the parent's {o['parent_mix']}")
        lines.append(f"          DECLINE {_f(dcl['value'])} (n {dcl['n']}) ≥ {_f(dcl['bar'])} (0.90 × P-ORACLE {_f(dcl['p_oracle'])}; the fraction {'met' if dcl.get('fraction_met') else 'not met'}) → {_verdict(dcl)}"
                     + (" (the organ clause: P-ORACLE < 0.80 — purple inside a trained colour's band)" if dcl.get("ceiling_bound") else "")
                     + f" · kind A spoken {_f(dcl['kind_A_spoken'])} truth {_f(dcl['kind_A_truth'])} "
                     f"· kind B decline {_f(dcl['kind_B_decline_rate'])} · A-RW-LR10 {_f(dcl['lr10'])}")
        ns, n3 = b["N-SHUF"], b["N-SHUF-M3"]
        lines.append(f"          N-SHUF M1 {_f(ns['value'])} ≤ {_f(ns['bar'])} → {'PASS' if ns['pass'] else 'FAIL'} · M3 {_f(n3['value'])} ≤ {_f(n3['bar'])} → {'PASS' if n3['pass'] else 'FAIL'}")
    reads = {k: {ws: (_verdict(out["seeds"][str(ws)][k]) if k not in ("N-SHUF", "N-SHUF-M3") else ("PASS" if out["seeds"][str(ws)][k]["pass"] else "FAIL"))
                 for ws in W.WORLD_SEEDS} for k in MARK_ORDER}
    for ws in W.WORLD_SEEDS:
        rb = out["seeds"][str(ws)]["READ-BACK"]
        if rb["value"] is not None and rb["value"] != 1.0:
            reads["READ-BACK"][ws] = "BROKEN ROAD"
    grad6 = [ws for ws in W.WORLD_SEEDS if not out["seeds"][str(ws)]["M6"].get("not_gradable")]
    allpass = {k: all(reads[k][ws] == "PASS" for ws in W.WORLD_SEEDS) for k in MARK_ORDER if k != "M6"}
    allpass["M6"] = bool(grad6) and all(reads["M6"][ws] == "PASS" for ws in grad6)
    lines.append("per seed: " + " · ".join(f"{k} " + "/".join(reads[k][ws] for ws in W.WORLD_SEEDS) for k in MARK_ORDER))
    lines.append("every bar at all 3 seeds (M6 where the meeting was seen: " + ", ".join(map(str, grad6)) + "): "
                 + " · ".join(f"{k} {'PASS' if allpass[k] else 'no'}" for k in MARK_ORDER)
                 + f" → S1b-1 {'PASSES' if all(allpass.values()) else 'does not pass'}")
    ref = {ws: out["seeds"][str(ws)]["refute"] for ws in W.WORLD_SEEDS}
    lr_revert = sum(ref[ws]["lr_below_lr10"] for ws in W.WORLD_SEEDS) >= 2
    ii_above = sum(ref[ws]["T4p_ii_above_law_by_005"] for ws in W.WORLD_SEEDS) >= 2
    lines.append("refutations (§9): T1 " + " ".join(f"{ws}:{'REFUTED' if ref[ws]['T1'] else 'no'}" for ws in W.WORLD_SEEDS)
                 + f" · the lr law (A-RW below A-RW-LR10 on M1 at ≥ 2 seeds) {'REVERTS' if lr_revert else 'stands'} "
                 + "(" + " ".join(f"{ws}:{'below' if ref[ws]['lr_below_lr10'] else 'not below'}" for ws in W.WORLD_SEEDS) + ")"
                 + " · T2 " + " ".join(f"{ws}:{'REFUTED' if ref[ws]['T2'] else 'no'}" for ws in W.WORLD_SEEDS)
                 + " · T3 " + " ".join(f"{ws}:{'REFUTED' if ref[ws]['T3'] else 'no'}" for ws in W.WORLD_SEEDS)
                 + " · T4′ spread-is-the-limit " + " ".join(f"{ws}:{'yes' if ref[ws]['T4p_spread_is_the_limit'] else 'no'}" for ws in W.WORLD_SEEDS)
                 + f" · (ii) above the law by ≥ 0.05 at ≥ 2 seeds: {'yes — the plain band is the next law' if ii_above else 'no'}"
                 + " · the learner refuses (M2b ≥ 0.80) " + " ".join(f"{ws}:{'yes' if ref[ws]['T4p_learner_refuses'] else 'no'}" for ws in W.WORLD_SEEDS)
                 + " · one-meeting " + " ".join(f"{ws}:{'REFUTED' if ref[ws]['one_meeting'] else ('n/g' if out['seeds'][str(ws)]['M6'].get('not_gradable') else 'no')}" for ws in W.WORLD_SEEDS))
    out["all_pass"] = allpass
    out["reads"] = {k: {str(ws): v for ws, v in d.items()} for k, d in reads.items()}
    out["m6_gradable_seeds"] = grad6
    out["lr_law_reverts"] = lr_revert
    for l in lines:
        log(l)
    d = Path(root) if dest is None else Path(dest)          # S1b-1R's gate step 2 writes its re-run's report apart (additive)
    d.mkdir(parents=True, exist_ok=True)
    dump(d / "report.json", out)
    (d / "report.txt").write_text("\n".join(lines) + "\n")
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


def gate_eye_fixture() -> Dict[str, object]:
    """Step 1: the seat's eye fixture under /usr/bin/python3 with THIS tree first on sys.path (S1a's first test)."""
    repo = str(Path(__file__).resolve().parents[2])
    fx = "/data/dev/genome-wt-brain3/docs/brain/r3/seat_eye_fixture.py"
    code = (f"import sys, runpy\nsys.path.insert(0, {repo!r})\nrunpy.run_path({fx!r}, run_name='__main__')\n"
            "import brain\nprint('MODULE', brain.__file__)\n")
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    p = subprocess.run(["/usr/bin/python3", "-B", "-c", code], capture_output=True, text=True, env=env, cwd=repo, timeout=300)
    rows = [l for l in p.stdout.splitlines() if l.startswith("row ")]
    ok = [l.endswith("png-sha match True · glances byte-equal True") for l in rows]
    mod = [l.split(" ", 1)[1] for l in p.stdout.splitlines() if l.startswith("MODULE ")]
    return {"rows": len(rows), "equal": sum(ok), "pass": p.returncode == 0 and len(rows) == 3 and all(ok)
            and bool(mod) and mod[0].startswith(repo), "module": mod[0] if mod else None}


def gate_identity(root: Path) -> Dict[str, object]:
    """Step 2 (PREREG-S1B1 §1): (a) every redrawn S1a cache (train / test / m2b / m6 of each world seed, and the toy and
    stage −1) carries S1a's scene specs, canvas shas and glances; (b) the M1 / M2a / M2b / M6 / NAME item ids — with
    their phrase and target — equal S1a's keys.json; stage −1's printed text equals S1a's byte for byte."""
    res = {"caches": {}, "items": {}, "stage_text_equal": None}
    for ws in W.WORLD_SEEDS:
        for split in ("train", "test", "m2b", "m6"):
            res["caches"][f"{ws}/{split}"] = C.identity_with(C.cache_dir(root, ws, split), C.cache_dir(C.S1A_RUNS, ws, split))
        kn = json.loads((seed_root(root, ws) / "keys.json").read_text())["items"]
        ko = json.loads((seed_root(C.S1A_RUNS, ws) / "keys.json").read_text())["items"]
        for mark in ("M1", "M2a", "M2b", "M6", "NAME"):
            a = [(it["item_id"], it.get("phrase"), it.get("target")) for it in kn[mark]]
            b = [(it["item_id"], it.get("phrase"), it.get("target")) for it in ko[mark]]
            res["items"][f"{ws}/{mark}"] = {"n": len(a), "same": a == b}
    for split in ("toy-train", "toy-test", "stage"):
        res["caches"][split] = C.identity_with(C.cache_dir(root, None, split), C.cache_dir(C.S1A_RUNS, None, split))
    new_t = (Path(root) / "stage" / "stage_minus1.txt")
    old_t = (C.S1A_RUNS / "stage" / "stage_minus1.txt")
    res["stage_text_equal"] = new_t.exists() and old_t.exists() and new_t.read_bytes() == old_t.read_bytes()
    res["pass"] = (all(v["same"] for v in res["caches"].values()) and all(v["same"] for v in res["items"].values())
                   and bool(res["stage_text_equal"]))
    return res


def gate_lockin() -> Dict[str, object]:
    """Step 4 (§2): the machinery toy of tests/brain/scene/test_learners_s1b1.py — planted directions, ambiguous 2-thing
    scenes, seeds 11 / 12, 1,500 scenes — lr 0.01 must read > 0.90 and lr 0.1 on the SAME scenes ≥ 0.10 below it."""
    rng = np.random.default_rng(11)
    dirs = {w: rng.normal(size=Lr.RW_DIM) for w in ("a", "b", "c", "d")}
    scenes = []
    for _ in range(1500):
        ws = rng.choice(list(dirs), size=2, replace=False)
        raw = np.stack([dirs[w] + 0.3 * rng.normal(size=Lr.RW_DIM) for w in ws])
        scenes.append((raw, [str(ws[rng.integers(2)])]))

    def acc(lr):
        L = Lr.RWLearner(lr=lr)
        for k, (raw, ws) in enumerate(scenes):
            L.train_scene(raw, ws, rng=np.random.default_rng(k))
        r2 = np.random.default_rng(12)
        ok = 0
        for k in range(200):
            ws = r2.choice(list(dirs), size=2, replace=False)
            raw = np.stack([dirs[w] + 0.3 * r2.normal(size=Lr.RW_DIM) for w in ws])
            ok += L.answer_point(raw, [str(ws[0])], np.random.default_rng(k))["point"] == 0
        return ok / 200

    a001, a01 = acc(Lr.LR_S1B1), acc(Lr.LR)
    return {"lr_001": a001, "lr_01": a01, "pass": a001 > 0.90 and a001 - a01 >= 0.10}


def gate_order_key() -> Dict[str, object]:
    """Step 5 (§5): the ORDER KEY learned from seed 20261101's first 300 utterances reads size < colour < shape for
    every word; a shuffled-position control (each utterance permuted by a seeded generator) fails the pin."""
    ws0 = W.WORLD_SEEDS[0]
    utts = [W.train_scene(ws0, i).words for i in range(W.GATE_N)]
    heard = sorted({w for u in utts for w in u})

    def pin(ear):
        k = {t: [ear.key(w) for w in heard if W.word_type(w) == t] for t in ("size", "colour", "shape")}
        return bool(all(k.values()) and max(k["size"]) < min(k["colour"]) and max(k["colour"]) < min(k["shape"])), k

    ear = Lr.Ear()
    for u in utts:
        ear.hear(u)
    ok, keys = pin(ear)
    rng = np.random.default_rng(ws0)
    ctrl = Lr.Ear()
    for u in utts:
        ctrl.hear(tuple(u[k] for k in rng.permutation(len(u))))
    cok, _ck = pin(ctrl)
    return {"pin": ok, "control_fails": not cok, "keys": {t: [round(v, 3) for v in vs] for t, vs in keys.items()},
            "pass": ok and not cok}


def first_gate(root: Path, log=print, toy_only: bool = False) -> Dict[str, object]:
    """THE FIRST GATE of PREREG-S1B1 §8 (edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:55 +0400) — nine steps; each of steps
    1–8 stops the run on a miss; step 9 is printed. Needs every cache and every seed's questions under `root`."""
    check_prereg()
    t0 = time.perf_counter()
    out: Dict[str, object] = {"prereg_sha256": PREREG_SHA256, "amend2_sha256": AMEND2_SHA256,
                              "prereg_s1b1_sha256": PREREG_S1B1_SHA256, "code": code_identity()}
    lines = ["== THE FIRST GATE (PREREG-S1B1 §8; each step stops the run on a miss) =="]
    stop: List[str] = []
    # 1. the eye
    eye = gate_eye_fixture()
    out["eye"] = eye
    lines.append(f"1. the eye fixture under /usr/bin/python3 from this tree: {eye['equal']}/{eye['rows']} byte-equal (module {eye['module']}) → {'PASS' if eye['pass'] else 'MISS'}")
    if not eye["pass"]:
        stop.append("the eye fixture")
    # 2. identity with S1a
    idn = gate_identity(root)
    out["identity"] = idn
    bad_c = [k for k, v in idn["caches"].items() if not v["same"]]
    bad_i = [k for k, v in idn["items"].items() if not v["same"]]
    lines.append(f"2. identity with S1a: {len(idn['caches']) - len(bad_c)}/{len(idn['caches'])} caches carry S1a's specs, canvas shas and glances "
                 f"(rows {sum(v['rows_new'] for v in idn['caches'].values())}); {len(idn['items']) - len(bad_i)}/{len(idn['items'])} item sets equal S1a's keys; "
                 f"stage −1's text byte-equal: {idn['stage_text_equal']} → {'PASS' if idn['pass'] else 'MISS ' + str(bad_c + bad_i)}")
    if not idn["pass"]:
        stop.append("the identity with S1a")
    # 3. the toy at lr 0.01, no fallback
    tr = Things(C.ScenePercepts(C.cache_dir(root, None, "toy-train")))
    te = Things(C.ScenePercepts(C.cache_dir(root, None, "toy-test")))
    te_truth = C.load_truth(C.cache_dir(root, None, "toy-test"))
    tr_truth = C.load_truth(C.cache_dir(root, None, "toy-train"))
    items = M.m1_items(te_truth, W.TOY_SEED, mark="TOY")
    rows = list(range(len(tr.p)))
    L = Lr.RWLearner(lr=Lr.LR_S1B1)
    seen: list = []
    train_arm("A-RW", L, tr, tr.p.words, None, rows, W.TOY_SEED, seen)
    L.calibrate(seen)
    toy = _toy_m1(L, "A-RW", items, te, te_truth)
    toy_pass = _ge(toy["covered"], M.TOY_BAR)
    out["toy"] = {"lr": Lr.LR_S1B1, "m1": toy, "pass": toy_pass}
    lines.append(f"3. THE TOY at lr {Lr.LR_S1B1} (no fallback): M1 covered {_f(toy['covered'])} (n {toy['n_covered']}; all {_f(toy['all'])}; chance {_f(toy['chance_covered'])}) "
                 f"≥ {M.TOY_BAR} → {'PASS' if toy_pass else 'MISS'}")
    if not toy_pass:
        stop.append("the toy at lr 0.01")
    eps_rows = {}
    for eps in Lr.EPS_GRID:
        R = make_learner("P-ORACLE", Lr.LR_S1B1, eps)
        train_arm("P-ORACLE", R, tr, tr.p.words, tr_truth, rows, W.TOY_SEED)
        R.prepare()
        nm = _per_type_naming(R, te, te_truth)
        eps_rows[str(eps)] = {"naming": nm, "mean": float(np.mean([v[0] for v in nm.values()])),
                              "m1": _toy_m1(R, "P-ORACLE", items, te, te_truth)["covered"]}
    best = max(eps_rows.items(), key=lambda kv: (kv[1]["mean"], float(kv[0])))
    eps = float(best[0])
    out["eps_choice"] = {"grid": eps_rows, "eps": eps}
    lines.append("   P-ORACLE's ε on the toy seed (S1a's rule): " + " · ".join(f"{k}: {v['mean']:.3f} · {v['m1']:.3f}" for k, v in eps_rows.items()) + f" → ε {eps}")
    # 4. the lock-in pin
    lk = gate_lockin()
    out["lockin"] = lk
    lines.append(f"4. the lock-in pin (machinery toy, seeds 11 / 12, 1,500 scenes): lr 0.01 {lk['lr_001']:.3f} · lr 0.1 {lk['lr_01']:.3f} "
                 f"(> 0.90 and ≥ 0.10 below) → {'PASS' if lk['pass'] else 'MISS'}")
    if not lk["pass"]:
        stop.append("the lock-in pin")
    # 5. the ORDER-KEY pin
    ok = gate_order_key()
    out["order_key"] = ok
    lines.append(f"5. the ORDER-KEY pin on seed {W.WORLD_SEEDS[0]}'s first {W.GATE_N} utterances: keys size {ok['keys']['size']} < colour {ok['keys']['colour']} "
                 f"< shape {ok['keys']['shape']}: {ok['pin']}; the shuffled control fails: {ok['control_fails']} → {'PASS' if ok['pass'] else 'MISS'}")
    if not ok["pass"]:
        stop.append("the order-key pin")
    # 6. S1a's instrument verdict, re-read on the fresh gate caches
    ws = W.WORLD_SEEDS[0]
    trs = Things(C.ScenePercepts(C.cache_dir(root, ws, "train")))
    trs_truth = C.load_truth(C.cache_dir(root, ws, "train"))
    gate_rows = list(range(W.GATE_N))
    one = [i for i in gate_rows if len(trs_truth[i]["things"]) == 1]
    loo = {t: [] for t in TYPE_WORDS}
    for i in one:
        R = make_learner("P-ORACLE", Lr.LR_S1B1, eps)
        train_arm("P-ORACLE", R, trs, trs.p.words, trs_truth, [j for j in gate_rows if j != i], ws)
        R.prepare()
        nm = _per_type_naming(R, trs, [trs_truth[i]])
        for t, (v, n) in nm.items():
            if n:
                loo[t].append(v)
    th = M.verdict_thresholds()
    s1a_gate = C.S1A_RUNS / "gate" / "gate.json"
    s1a_v = json.loads(s1a_gate.read_text()).get("instrument", {}) if s1a_gate.exists() else {}
    verdict = {}
    for t in TYPE_WORDS:
        v = float(np.mean(loo[t])) if loo[t] else None
        verdict[t] = {"p_oracle": v, "n": len(loo[t]), "threshold": th[t], "fires": v is None or v < th[t],
                      "s1a": (s1a_v.get(t) or {}).get("p_oracle")}
    out["instrument"] = verdict
    fired = [t for t, v in verdict.items() if v["fires"]]
    same = all(v["s1a"] is not None and abs(v["p_oracle"] - v["s1a"]) < 1e-12 for v in verdict.values())
    lines.append(f"6. S1a's instrument verdict re-read on the fresh caches (LOO on the {len(one)} one-thing gate scenes): " + " · ".join(
        f"{t} {_f(v['p_oracle'])} vs {v['threshold']:.4f} (S1a {_f(v['s1a'])})" for t, v in verdict.items())
        + f" → {'PROCEED' if not fired else 'FIRES ' + str(fired)}; equal to S1a's: {same}")
    if fired:
        stop.append(f"the instrument verdict fires for {fired}")
    if not same:
        stop.append("the instrument verdict differs from S1a's on identical caches — an instrument fault")
    # 7. the arms × 300 scenes vs N-SHUF on the graded M1
    Q = json.loads((seed_root(root, ws) / "questions.json").read_text())
    K = json.loads((seed_root(root, ws) / "keys.json").read_text())
    tt = {s: Things(C.ScenePercepts(C.cache_dir(root, ws, s))) for s in TEST_SPLITS}
    t_truth = C.load_truth(C.cache_dir(root, ws, "test"))
    perm = Lr.nshuf_permutation(substream(ws, "n-shuf-permutation"), len(trs.p))
    arms, learners = {}, {}
    for arm in ARMS:
        Lx = make_learner(arm, Lr.LR_S1B1, eps)
        seen = []
        words_of = (lambda i: trs.p.words(int(perm[i]))) if arm == "N-SHUF" else trs.p.words
        train_arm(arm, Lx, trs, words_of, trs_truth if arm in ORACLE_ARMS else None, gate_rows, ws, seen)
        cal = prepare(arm, Lx, seen)
        ans = answer_all(arm, Lx, {"M1": Q["questions"]["M1"]}, tt, Q["test_seed"])
        g = M.grade_pointing(K["items"]["M1"], ans, t_truth, tt["test"].members, "truth" if arm == "ORACLE-TRUTH" else "gaze")
        arms[arm] = M.summarise_pointing(g)
        learners[arm] = (Lx, cal)
    ns_cov = arms["N-SHUF"]["graded"]["covered"]
    must = ("A-RW", "P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH")
    beat = {a: (arms[a]["graded"]["covered"] is not None and ns_cov is not None and arms[a]["graded"]["covered"] > ns_cov) for a in must}
    out["arms300"] = {a: {k: arms[a][k] for k in ("graded", "size2", "size3", "size1", "all")} for a in ARMS}
    out["beat_nshuf"] = beat
    g0 = arms["A-RW"]["graded"]
    lines.append(f"7. {len(ARMS)} arms × {W.GATE_N} scenes of seed {ws}, M1 on the graded 2- and 3-thing items (n {g0['n_all']}, covered {g0['n_covered']}; chance {_f(g0['chance_covered'])}):")
    for a in ARMS:
        b = arms[a]
        lines.append(f"   {a:<14} {_f(b['graded']['covered'])} (size2 {_f(b['size2']['covered'])} · size3 {_f(b['size3']['covered'])} · pooled all sizes {_f(b['all']['covered'])})"
                     + ("" if a == "N-SHUF" else (" · a reading arm" if a in READING_ARMS else f" · beats N-SHUF: {'yes' if beat.get(a) else 'NO'}")))
    miss7 = [a for a, v in beat.items() if not v]
    if miss7:
        stop.append(f"{miss7} do not beat N-SHUF at 300 scenes")
    # 8. the SPEAK road's smoke on the 300-scene A-RW (the wiring pin)
    L_rw, _cal = learners["A-RW"]
    sq = {m: Q["questions"][m] for m in ("SPEAK", "DECLINE")}
    ans = answer_all("A-RW", L_rw, sq, tt, Q["test_seed"])
    ptr = {q["item_id"]: q.get("hyp") for m in sq for q in sq[m]}
    sp = M.summarise_speak(M.grade_speak(K["items"]["SPEAK"], ans, C.load_truth(C.cache_dir(root, ws, "speak")), ptr))
    dc = M.summarise_decline(M.grade_decline(K["items"]["DECLINE"], ans, C.load_truth(C.cache_dir(root, ws, "decline")), ptr))
    rb_ok = sp["readback"] == 1.0 and sp["n_spoken"] > 0
    out["speak_smoke"] = {"speak": sp, "decline": dc, "pass": rb_ok}
    lines.append(f"8. the SPEAK road's smoke (A-RW at {W.GATE_N} scenes): spoken {_f(sp['spoken'])} (n {sp['n_covered']}) · READ-BACK {_f(sp['readback'])} on {sp['n_spoken']} spoken "
                 f"(the wiring pin = 1.000) · truth {_f(sp['truth'])} (no bar at {W.GATE_N}) · reasons {sp['reasons']} · DECLINE reasons {dc['reasons']} → {'PASS' if rb_ok else 'MISS'}")
    if not rb_ok:
        stop.append("the wiring pin (READ-BACK) on the SPEAK smoke")
    # 9. the σ-floor count per word (printed)
    floor = _cal.get("sigma_floor_count", {})
    out["sigma_floor_count"] = floor
    lines.append("9. per word, the dimensions of σ_w at the 1e-3 floor (A-RW at 300; printed): " + " · ".join(f"{w} {c}" for w, c in floor.items()))
    out["verdict"] = "STOP" if stop else "PROCEED"
    out["stop_reasons"] = stop
    out["lr"], out["eps"] = Lr.LR_S1B1, eps
    out["wall_s"] = time.perf_counter() - t0
    lines.append(f"GATE: {out['verdict']}" + (f" — {'; '.join(stop)}" if stop else ""))
    for l in lines:
        log(l)
    out["lines"] = lines
    dump(Path(root) / "gate" / "gate.json", out)
    (Path(root) / "gate" / "gate.txt").write_text("\n".join(lines) + "\n")
    return out


def cache_all(root: Path, log=print) -> Dict[str, object]:
    """Every cache under `root`, one at a time (the eye's price, solo): stage −1, the toy, each world seed (train and
    its six test splits); then each seed's questions and keys."""
    rec = {}
    t = time.process_time()
    stage_minus1(root, log=lambda s: None)
    rec["stage"] = time.process_time() - t
    for split in ("toy-train", "toy-test"):
        d = C.cache_dir(root, None, split)
        t = time.process_time()
        if not d.exists():
            C.build(split, None, d, log=log)
        rec[split] = time.process_time() - t
    for ws in W.WORLD_SEEDS:
        t = time.process_time()
        C.build_world_seed(root, ws, log=log)
        rec[str(ws)] = time.process_time() - t
        build_questions(root, ws)
    log(f"[cache-all] CPU-s per step: {rec}")
    return rec


def cache_r(root: Path, log=print) -> Dict[str, object]:
    """PREREG-S1B1R / AMENDMENT 1 §4 (c) (edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:00 +0400): every cache this slice reads,
    drawn ONCE under its fresh root by THIS code, one at a time: the toy (P-ORACLE's ε, S1a's rule), then per world seed the
    ONE training cache, S1b-1's own test set (2026120x — the gate's step 2 re-runs S1b-1's arms on it) and the FRESH test set
    (2026140x, with SPEAK2 — the graded marks). No questions here (run.py writes them; they are pure functions of the
    caches). CPU and wall seconds per step are recorded."""
    check_prereg()
    rec: Dict[str, object] = {}
    for split in ("toy-train", "toy-test"):
        d = C.cache_dir(root, None, split)
        t, w = time.process_time(), time.perf_counter()
        if not d.exists():
            C.build(split, None, d, log=log)
        rec[split] = {"cpu_s": time.process_time() - t, "wall_s": time.perf_counter() - w}
    for ws in W.WORLD_SEEDS:
        for tset in ("s1b1", "fresh"):
            t, w = time.process_time(), time.perf_counter()
            dj = C.build_world_seed(root, ws, log=log, tset=tset)
            rec[f"{ws}/{tset}"] = {"cpu_s": time.process_time() - t, "wall_s": time.perf_counter() - w,
                                   "test_seed": dj["test_seed"], "checked": dj["checked"], "overlap": dj["overlap"]}
            log(f"[cache-r] {ws}/{tset}: cpu {rec[f'{ws}/{tset}']['cpu_s']:.1f} s · disjoint {dj['checked']}")
    rec["cpu_s_total"] = sum(v["cpu_s"] for v in rec.values() if isinstance(v, dict))
    log(f"[cache-r] CPU-s in all: {rec['cpu_s_total']:.1f}")
    dump(Path(root) / "logs" / "cache-r.json", rec)
    return rec


# ------------------------------------------------------------------------------------------------ the price
def price(root: Path, n: int = 2000, log=print) -> Dict[str, object]:
    """Solo (A-RW, seed 1), then the launch's shape (6 arms × 3 seeds at once, nice 19), each over the first `n` scenes
    with the reading points ≤ n; CPU seconds read from each process's own record, extrapolated ×(10,000 / n)."""
    g = gate_or_chosen(root)
    tmp = Path(root) / "price"
    rps = [r for r in W.READING_POINTS if r <= n]
    base = [sys.executable, "-B", "-m", "brain.scene.run", "arm", "--root", str(root), "--n", str(n), "--rps", ",".join(map(str, rps))]
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


# ================================================================================================ S1b-1R «the repair»
# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:23 +0400 — PREREG-S1B1R (sha 879a22fb…) with AMENDMENT 1 (a198f0b4…): the four arms
# and A-RW-R's one-difference readings on the FRESH test set, the K-draw null, the grader, the bars, the report, THE FIRST
# GATE's six steps and the price. Additive: S1b-1's arms, grader, bars and report above are untouched — the gate's step 2
# re-runs them with S1b-1's roads on S1b-1's own test seeds and must reproduce S1b-1's regraded report.
R_ARMS: Tuple[str, ...] = ("A-RW-R", "P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH")
R_TRAIN_AS = {"A-RW-R": "A-RW", "P-ORACLE-RW": "P-ORACLE-RW", "P-ORACLE": "P-ORACLE", "ORACLE-TRUTH": "ORACLE-TRUTH"}
R_READINGS: Tuple[str, ...] = ("R-TT", "R-DIAG", "R-OLDMOUTH", "R-NONE-DIST", "S1B1-ROADS")
R_TSET = "fresh"
NULL_K = 20                     # §1 (f): K = 20 derangements per seed (keys null:<seed>:k, k = 1..20); k = 0 is S1b-1's draw
NULL_PCT = 95                   # the bar: A-RW-R above the null's 95th percentile (numpy's default linear rule)
TRUTH_NEED_VS_PORACLE, MINIMAL_VS_PORACLE = 0.90, 0.90
READER_TOY_SEEDS = (0, 1, 2)
TOY_DIAG_MAX, TOY_READER_MIN = 0.50, 0.90
READER_TOY = {"k": 16, "sig_big": 4.0, "sig_small": 0.1, "cls_sd": 3.0, "noise": 0.5, "delta2": 10.0, "n_train": 1200,
              "n_test": 200}
R_MARK_ORDER = ("M1", "NULL-M1", "NULL-M3", "M2a", "M2b", "M3", "M6", "SPOKEN", "TRUTH", "TRUTH-NEED", "MINIMAL", "ORDER",
                "READ-BACK", "DECLINE")
R_BARS = tuple(k for k in R_MARK_ORDER if k != "DECLINE")        # DECLINE is a READING (§5)
S1B1_REPORT_REGRADED = Path("/data/dev/genome-wt-brain3/docs/brain/r3/S1B1-REPORT-REGRADED.txt")
S1B1_REPORT_REGRADED_SHA256 = "7abd2ee6cd04e6df1df6259192baeb2b194d8ff8be9deafc09875cc5615a9478"
STEP2_MARKS = ("M1", "M3", "M6", "M2a", "M2b", "SPOKEN", "TRUTH", "READ-BACK")
PARENT_MIX = {"1": 0.25, "2": 0.5, "3": 0.25}


def r_seed_root(root: Path, ws: int) -> Path:
    """The FRESH test set's records of one world seed: <root>/<ws>/fresh/ (questions, keys, arms, nulls, marks)."""
    return Path(root) / str(ws) / R_TSET


def types_check(cover: Sequence[Sequence[str]], words: Sequence[str]) -> Dict[str, object]:
    """THE FIRST GATE step 3 (§4): the learned cover equals the WORLD's three types over the same words (a type = a set)."""
    world: Dict[str, List[str]] = {}
    for w in words:
        world.setdefault(W.word_type(w), []).append(w)
    want = sorted(tuple(sorted(v)) for v in world.values())
    got = sorted(tuple(sorted(t)) for t in cover)
    return {"pass": got == want, "cover": [list(t) for t in cover], "world": [list(t) for t in want]}


def reader_toy(seed: int, eps: float, **over) -> Dict[str, object]:
    """THE FIRST GATE step 4 (§4) — a POSITIVE CONTROL of the READER on the learner's own store: a planted two-type toy (A-RW's
    own code at lr 0.01; words a0..a2 × b0..b1, one thing a scene, both words said, so the ear learns the two types) with
    CORRELATED features: a nuisance block P whose within-class spread is rank one along u (every coordinate varies, all
    together), class blocks A / B carrying the classes. The NEVER-TAUGHT class is a0's things moved along v ⊥ u in P by
    δ² = 10 per-coordinate variances: inside a0's DIAGONAL box (each coordinate within its spread), outside the POOLED
    ellipse (v carries almost no within-type variance). Refusal = no word of type A emitted. Beside: the READER's hold on
    fresh TRAINED things (a READER refusing everything would pass vacuously), and the pin that the weighted pooled
    covariance equals the plain one when every r = 1 (one-thing scenes). Parameters frozen before the gate (READER_TOY)."""
    P_ = dict(READER_TOY, **over)
    rng = np.random.default_rng(seed)
    d, k = Lr.RW_DIM, int(P_["k"])
    half = (d - k) // 2
    iP, iA, iB = np.arange(k), np.arange(k, k + half), np.arange(k + half, d)
    u = np.ones(k) / np.sqrt(k)
    v = np.array([1.0 if i % 2 == 0 else -1.0 for i in range(k)]) / np.sqrt(k)
    mA = {f"a{i}": np.zeros(d) for i in range(3)}
    mB = {f"b{j}": np.zeros(d) for j in range(2)}
    for w in mA:
        mA[w][iA] = rng.normal(size=iA.size) * P_["cls_sd"]
    for w in mB:
        mB[w][iB] = rng.normal(size=iB.size) * P_["cls_sd"]

    def thing(a: str, b: str) -> np.ndarray:
        x = mA[a] + mB[b]
        x[iP] += P_["sig_big"] * rng.normal() * u + P_["sig_small"] * rng.normal(size=k)
        x[iA] += P_["noise"] * rng.normal(size=iA.size)
        x[iB] += P_["noise"] * rng.normal(size=iB.size)
        return x

    L = Lr.RWLearner(lr=Lr.LR_S1B1)
    seen = []
    for n in range(int(P_["n_train"])):
        a, b = f"a{rng.integers(3)}", f"b{rng.integers(2)}"
        raw = thing(a, b)[None, :]
        L.train_scene(raw, [a, b], rng=np.random.default_rng(n))
        seen.append((raw, [a, b], None))
    L.calibrate(seen)
    info = L.calibrate_r(eps)
    delta = float(np.sqrt(P_["delta2"] * (P_["sig_big"] ** 2 / k + P_["sig_small"] ** 2)))
    diag, rdr = Lr.RWRoad(L, band="diag"), Lr.RWRoad(L)
    type_a = {"a0", "a1", "a2"}
    ref: Dict[str, List[bool]] = {"diag": [], "reader": []}
    hold: Dict[str, List[bool]] = {"diag": [], "reader": []}
    for _n in range(int(P_["n_test"])):
        b = f"b{rng.integers(2)}"
        novel = thing("a0", b)
        novel[iP] += delta * v
        trained = thing(f"a{rng.integers(3)}", b)
        for name, road in (("diag", diag), ("reader", rdr)):
            ref[name].append(not (set(road.held_words(novel)) & type_a))
            hold[name].append(bool(set(road.held_words(trained)) & type_a))
    worst = 0.0
    for T in L.reader["ear"]["types"]:
        S = Lr.pooled_covariance(L, T)
        Zs = [np.concatenate(L.store_z[L.index[w]], axis=0) for w in T]
        if not all(np.all(np.concatenate(L.store_r[L.index[w]]) == 1.0) for w in T):
            worst = float("inf")
            continue
        plain = sum((Z - Z.mean(axis=0)).T @ (Z - Z.mean(axis=0)) for Z in Zs) / sum(Z.shape[0] for Z in Zs)
        worst = max(worst, float(np.max(np.abs(S - plain)) / max(float(np.max(np.abs(plain))), 1e-300)))
    return {"seed": seed, "eps": eps, "types": info["types"], "diag_refusal": float(np.mean(ref["diag"])),
            "reader_refusal": float(np.mean(ref["reader"])), "reader_holds_trained": float(np.mean(hold["reader"])),
            "diag_holds_trained": float(np.mean(hold["diag"])), "n_test": int(P_["n_test"]), "pin_weighted_vs_plain": worst}


def speak2_pin_rows(rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """THE FIRST GATE step 5 (AMENDMENT 1 §2): on every drawn SPEAK2 scene (the cache's own rows) no single word of the target
    is unique, the kind's 2-word phrase is, the kind's other two 2-word phrases are not."""
    n = ok = 0
    per: Dict[str, List[int]] = {}
    for r in rows:
        kind = W.speak2_kind(int(r["index"]))
        p = W.speak2_pin(M.things_of(r), int(r["referent"]), kind)
        n += 1
        ok += bool(p["pass"])
        per.setdefault(kind, [0, 0])
        per[kind][0] += bool(p["pass"])
        per[kind][1] += 1
    return {"n": n, "pass": ok, "kinds": {k: f"{a}/{b}" for k, (a, b) in sorted(per.items())}}


# ------------------------------------------------------------------------------------------------ the fresh questions
def build_questions_r(root: Path, ws: int) -> Dict[str, int]:
    """The FRESH test set's questions and keys (§2): S1b-1's own generators and counts on test seed 2026140x, and SPEAK2 (a
    POINTER to the target — its hypothesis for the gaze arms, the thing for ORACLE-TRUTH; the kind stays in the keys).
    S1b-1's build_questions is untouched (the gate's step 2 uses it on S1b-1's own set)."""
    ts = W.FRESH_TEST_SEEDS[ws]
    cd = lambda s: C.cache_dir(root, ws, s, R_TSET)
    shas = {"prereg_sha256": PREREG_SHA256, "prereg_s1b1_sha256": PREREG_S1B1_SHA256,
            "prereg_s1b1r_sha256": PREREG_S1B1R_SHA256, "amend1_sha256": S1B1R_AMEND1_SHA256}
    out = {**shas, "world_seed": ws, "test_seed": ts, "test_set": R_TSET}
    keys = {**shas, "world_seed": ws, "test_seed": ts, "test_set": R_TSET}
    tt = C.load_truth(cd("test"))
    tr = {s: C.load_truth(cd(s)) for s in ("m2b", "m6", "m3", "speak", "decline", "speak2")}
    th = {s: Things(C.ScenePercepts(cd(s))) for s in ("test", "m2b", "speak", "decline", "speak2")}
    m1, m2a = M.m1_items(tt, ts), M.m2a_items(tt, ts)
    m2b, m6, m3 = M.m2b_items(tr["m2b"]), M.m6_items(tr["m6"]), M.m3_items(tr["m3"])
    speak, decline, speak2 = M.speak_items(tr["speak"]), M.decline_items(tr["decline"]), M.speak2_items(tr["speak2"])
    name = []
    for row in tt:
        if len(row["things"]) == 1:
            t = row["things"][0]
            name.append({"item_id": f"NAME:{row['item_id']}", "mark": "NAME", "row": int(row["row"]), "phrase": [],
                         "target": 0, "shape": t["shape"], "colour": t["colour"], "size": t["size"], "n_things": 1})
    q: Dict[str, List[Dict[str, object]]] = {
        "M1": [{**M.question(it), "split": "test"} for it in m1], "M2a": [{**M.question(it), "split": "test"} for it in m2a],
        "M6": [{**M.question(it), "split": "m6"} for it in m6], "M3": [{**M.question(it), "split": "m3"} for it in m3]}
    for mark, items, split in (("M2b", m2b, "m2b"), ("NAME", name, "test")):
        q[mark] = []
        rows = tr["m2b"] if split == "m2b" else tt
        for it in items:
            r = rows[it["row"]]
            mem, pos = th[split].members(it["row"])
            hyp = M.thing_hypothesis(0, mem, pos, r["fix_thing"], tuple(r["centroids"][0]))
            q[mark].append({**M.question(it), "split": split, "hyp": hyp})
    for mark, items, split in (("SPEAK", speak, "speak"), ("DECLINE", decline, "decline"), ("SPEAK2", speak2, "speak2")):
        q[mark] = []
        for it in items:
            r = tr[split][it["row"]]
            mem, pos = th[split].members(it["row"])
            hyp = M.thing_hypothesis(it["target"], mem, pos, r["fix_thing"], tuple(r["centroids"][it["target"]]))
            it["hyp"] = hyp
            q[mark].append({**M.question(it), "split": split, "hyp": hyp, "thing": it["target"]})
    out["questions"] = q
    keys["items"] = {"M1": m1, "M2a": m2a, "M2b": m2b, "M6": m6, "NAME": name, "M3": m3, "SPEAK": speak, "DECLINE": decline,
                     "SPEAK2": speak2}
    d = r_seed_root(root, ws)
    dump(d / "questions.json", out)
    dump(d / "keys.json", keys)
    return {k: len(v) for k, v in keys["items"].items()}


# ------------------------------------------------------------------------------------------------ the roads and the answers
def r_roads(arm: str, learner, final: bool) -> Dict[str, Tuple[object, str, str]]:
    """The roads an arm answers through (§1, §3): name → (road, mouth "believed" | "old", the M2a «none» key). A-RW-R: the
    LAW at every reading point, its five one-difference readings at the last (AMENDMENT 1 §4 e); P-ORACLE-RW: A-RW-R's
    roads; P-ORACLE / ORACLE-TRUTH: their own road through the SAME new mouth (§3)."""
    if arm in LDA_ARMS:
        return {"LAW": (Lr.OracleRoad(learner), "believed", "none")}
    roads: Dict[str, Tuple[object, str, str]] = {"LAW": (Lr.RWRoad(learner), "believed", "none_i")}
    if arm == "A-RW-R" and final:
        roads.update({"R-TT": (Lr.RWRoad(learner, types="world"), "believed", "none_i"),
                      "R-DIAG": (Lr.RWRoad(learner, band="diag"), "believed", "none_i"),
                      "R-OLDMOUTH": (Lr.RWRoad(learner), "old", "none_i"),
                      "R-NONE-DIST": (Lr.RWRoad(learner, none="dist"), "believed", "none"),
                      "S1B1-ROADS": (Lr.RWRoad(learner, types=None, band="diag", mature=False, none="dist"), "old", "none")})
    return roads


def answer_all_r(arm: str, learner, questions: Dict[str, List[Dict[str, object]]], things: Dict[str, Things],
                 test_seed: int, roads: Dict[str, Tuple[object, str, str]]) -> Dict[str, object]:
    """The pointing marks once (M1 / M2a / M6 / M3 — pointing is road-free; every «none» flag rides on the answer), then per
    road: M2b and NAME («what is this?» under the road), SPEAK / SPEAK2 / DECLINE (the road's mouth; a fresh item tie
    generator per read-back candidate; DECLINE carries the oracle's colour fit, the organ fact)."""
    feed = R_TRAIN_AS.get(arm, arm)
    point: Dict[str, Dict[str, object]] = {}
    for mark in ("M1", "M2a", "M6", "M3"):
        for q in questions.get(mark, []):
            X = things[q["split"]].for_arm(feed, q["row"])
            point[q["item_id"]] = learner.answer_point(X, q["phrase"], M.tie_rng(test_seed, q["item_id"]))
    out: Dict[str, object] = {"point": point, "roads": {}}
    for name, (road, mouth, _key) in roads.items():
        ans: Dict[str, Dict[str, object]] = {}
        for q in questions.get("M2b", []):
            k = 0 if arm == "ORACLE-TRUTH" else q.get("hyp")
            if k is None:
                ans[q["item_id"]] = {"emit": None, "uncovered": True}
                continue
            ans[q["item_id"]] = {"emit": road.held_words(things[q["split"]].for_arm(feed, q["row"])[int(k)])}
        for q in questions.get("NAME", []):
            k = 0 if arm == "ORACLE-TRUTH" else q.get("hyp")
            if k is None:
                ans[q["item_id"]] = {"name": None, "emit": None, "uncovered": True}
                continue
            x = things[q["split"]].for_arm(feed, q["row"])[int(k)]
            ans[q["item_id"]] = {"name": {t: learner.name_forced(x, ws_) for t, ws_ in TYPE_WORDS.items()},
                                 "emit": road.held_words(x)}
        for mark in ("SPEAK", "SPEAK2", "DECLINE"):
            for q in questions.get(mark, []):
                k = q.get("thing") if arm == "ORACLE-TRUTH" else q.get("hyp")
                if k is None:
                    ans[q["item_id"]] = {"spoken": None, "reason": "uncovered", "uncovered": True}
                    continue
                X = things[q["split"]].for_arm(feed, q["row"])
                f = lambda q=q: M.tie_rng(test_seed, q["item_id"])
                a = Lr.produce_believed(road, X, int(k), f) if mouth == "believed" else Lr.produce(road, X, int(k), f)
                if mark == "DECLINE" and arm in LDA_ARMS:
                    a["colour_fit"] = learner.colour_fit(X[int(k)])
                ans[q["item_id"]] = a
        out["roads"][name] = ans
    return out


def oracle_reader_record(R) -> Dict[str, object]:
    """The oracle's side of the per-reading-point record: its types (the world's, its mature classes) and its one-alone type."""
    road = Lr.OracleRoad(R)
    types = road.types()
    counts = [int(sum(R.ear.alone.get(w, 0) for w in T)) for T in types]
    return {"types": [list(t) for t in types], "one_alone": road.one_alone(), "alone_counts": counts}


def run_arm_r(arm: str, root: Path, ws: int, n_train: int = W.N_TRAIN, reading_points: Sequence[int] = W.READING_POINTS,
              eps: Optional[float] = None, out: Optional[Path] = None, log=print) -> Dict[str, object]:
    """One S1b-1R arm over its stream (S1b-1's training, byte for byte: A-RW-R trains as S1b-1's A-RW), answering the FRESH
    questions at every reading point through its roads (the LAW; A-RW-R's readings at the last)."""
    t_wall, t_cpu = time.perf_counter(), time.process_time()
    if arm not in R_ARMS:
        raise RunError(f"no such S1b-1R arm: {arm!r}")
    if eps is None:
        eps = gate_or_chosen_r(root)["eps"]
    out = Path(out) if out is not None else r_seed_root(root, ws) / "arms" / arm
    out.mkdir(parents=True, exist_ok=True)
    Q = json.loads((r_seed_root(root, ws) / "questions.json").read_text())
    if Q.get("prereg_s1b1r_sha256") != PREREG_S1B1R_SHA256 or Q.get("amend1_sha256") != S1B1R_AMEND1_SHA256:
        raise RunError("the fresh questions were written under another law")
    things = {s: Things(C.ScenePercepts(C.cache_dir(root, ws, s, R_TSET))) for s in C.test_splits(R_TSET)}
    train = Things(C.ScenePercepts(C.cache_dir(root, ws, "train")))
    as_ = R_TRAIN_AS[arm]
    truth = C.load_truth(C.cache_dir(root, ws, "train")) if as_ in ORACLE_ARMS else None
    learner = make_learner(as_, Lr.LR_S1B1, eps)
    seen: list = []
    done = 0
    rps = sorted(r for r in reading_points if r <= n_train)
    record = {"arm": arm, "trains_as": as_, "world_seed": ws, "test_seed": Q["test_seed"], "test_set": R_TSET,
              "lr": Lr.LR_S1B1 if as_ in RW_ARMS else None, "eps": eps, "n_train": n_train,
              "prereg_s1b1r_sha256": PREREG_S1B1R_SHA256, "amend1_sha256": S1B1R_AMEND1_SHA256,
              "prereg_s1b1_sha256": PREREG_S1B1_SHA256, "code": code_identity(), "reading_points": {}}
    for rp in rps:
        train_arm(as_, learner, train, train.p.words, truth, range(done, rp), ws, seen)
        done = rp
        final = rp == rps[-1]
        cal = prepare(as_, learner, seen)
        if as_ in RW_ARMS:
            cal_r = learner.calibrate_r(eps, WORD_TYPES if (arm == "A-RW-R" and final) else None)
            cal_r["types_check"] = types_check(cal_r["types"], cal_r["mature"])
        else:
            cal_r = oracle_reader_record(learner)
        roads = r_roads(arm, learner, final)
        ans = answer_all_r(arm, learner, Q["questions"], things, Q["test_seed"], roads)
        dump(out / f"answers_{rp:05d}.json", {"arm": arm, "world_seed": ws, "rp": rp,
                                             "m2a_keys": {n: key for n, (_r, _m, key) in roads.items()},
                                             "mouths": {n: m for n, (_r, m, _k) in roads.items()}, **ans})
        record["reading_points"][str(rp)] = {"calibration": cal, "reader": cal_r, "roads": list(roads),
                                             "summary": learner.summary(), "wall_s": time.perf_counter() - t_wall,
                                             "cpu_s": time.process_time() - t_cpu}
        log(f"[{arm} {ws}] reading point {rp}: roads {list(roads)} · cpu {time.process_time() - t_cpu:.1f} s")
    record["wall_s"] = time.perf_counter() - t_wall
    record["cpu_s"] = time.process_time() - t_cpu
    dump(out / "record.json", record)
    return record


# ------------------------------------------------------------------------------------------------ the null (§1 f)
def null_perm(ws: int, k: int, n: int) -> np.ndarray:
    """The k-th derangement: key `null:<seed>:k` (k = 1..20); k = 0 is S1b-1's own draw (`n-shuf-permutation`)."""
    return Lr.nshuf_permutation(substream(ws, "n-shuf-permutation" if k == 0 else f"null:{ws}:{k}"), n)


def run_null(root: Path, ws: int, k: int, n_train: int = W.N_TRAIN, out: Optional[Path] = None) -> Dict[str, object]:
    """ONE null draw (AMENDMENT 1 §4 d): N-SHUF — A-RW's own code at lr 0.01 on the k-th deranged utterances — trained to
    `n_train`, answering the FRESH M1 and M3 items at the end (pointing is A-RW-R's, unchanged), graded here: M1 on the
    graded covered 2- and 3-thing items, M3 on the covered items, with their chance."""
    t0, w0 = time.process_time(), time.perf_counter()
    train = Things(C.ScenePercepts(C.cache_dir(root, ws, "train")))
    perm = null_perm(ws, k, len(train.p))
    L = make_learner("N-SHUF", Lr.LR_S1B1, 0.3)
    train_arm("N-SHUF", L, train, lambda i: train.p.words(int(perm[i])), None, range(n_train), ws, None)
    rs = r_seed_root(root, ws)
    Q = json.loads((rs / "questions.json").read_text())
    K = json.loads((rs / "keys.json").read_text())["items"]
    th = {s: Things(C.ScenePercepts(C.cache_dir(root, ws, s, R_TSET))) for s in ("test", "m3")}
    ans = {}
    for mark in ("M1", "M3"):
        for q in Q["questions"][mark]:
            ans[q["item_id"]] = L.answer_point(th[q["split"]].for_arm("N-SHUF", q["row"]), q["phrase"],
                                               M.tie_rng(Q["test_seed"], q["item_id"]))
    g1 = M.summarise_pointing(M.grade_pointing(K["M1"], ans, C.load_truth(C.cache_dir(root, ws, "test", R_TSET)),
                                               th["test"].members, "gaze"))["graded"]
    g3 = M.summarise_m3(M.grade_pointing(K["M3"], ans, C.load_truth(C.cache_dir(root, ws, "m3", R_TSET)),
                                         th["m3"].members, "gaze"), K["M3"])["all"]
    rec = {"world_seed": ws, "k": k, "key": "n-shuf-permutation" if k == 0 else f"null:{ws}:{k}", "n_train": n_train,
           "m1": g1["covered"], "n_m1": g1["n_covered"], "chance_m1": g1["chance_covered"],
           "m3": g3["covered"], "n_m3": g3["n_covered"], "chance_m3": g3["chance_covered"],
           "cpu_s": time.process_time() - t0, "wall_s": time.perf_counter() - w0}
    dump(Path(out) if out is not None else rs / "nulls" / f"{k:02d}.json", rec)
    return rec


# ------------------------------------------------------------------------------------------------ the grader (S1b-1R)
class _RCtx:
    """One world seed's FRESH test set as the grader reads it (the truth enters here and in marks.py only)."""

    def __init__(self, root: Path, ws: int):
        rs = r_seed_root(root, ws)
        self.K = json.loads((rs / "keys.json").read_text())
        self.Q = json.loads((rs / "questions.json").read_text())["questions"]
        self.items = self.K["items"]
        self.truth = {s: C.load_truth(C.cache_dir(root, ws, s, R_TSET)) for s in C.test_splits(R_TSET)}
        self.things = {s: Things(C.ScenePercepts(C.cache_dir(root, ws, s, R_TSET))) for s in C.test_splits(R_TSET)}
        self.m2b_cov = {it["row"] for it in self.items["M2b"] if M.covered(0, self.truth["m2b"][it["row"]]["fix_thing"])}
        tr = C.load_truth(C.cache_dir(root, ws, "train"))
        self.meeting_seen = M.meeting_seen(tr[W.DAX_INDEX]) if len(tr) > W.DAX_INDEX else None
        marks_ = ("SPEAK", "SPEAK2", "DECLINE")
        self.ptr = {"gaze": {q["item_id"]: q.get("hyp") for m in marks_ for q in self.Q.get(m, [])},
                    "truth": {q["item_id"]: q.get("thing") for m in marks_ for q in self.Q.get(m, [])}}


def grade_answers_r(ctx: _RCtx, arm: str, A: Dict[str, object]) -> Dict[str, object]:
    """Every mark of §5 for one arm's answers at one reading point: the pointing marks (M1, M6, M3) once; per road M2a (the
    road's «none» key: τ_point = `none_i` for the RW law and its readings, S1b-1's distance `none` for R-NONE-DIST and
    S1B1-ROADS, the oracle's τ_point `none`), M1's false refusal under the same key, M2b, NAME, the mouth (SPEAK, SPEAK2,
    MINIMAL, ORDER, per kind), DECLINE and the oracle's organ fact."""
    kind = "truth" if arm == "ORACLE-TRUTH" else "gaze"
    it, tr, th = ctx.items, ctx.truth, ctx.things
    P = A["point"]
    g1 = M.grade_pointing(it["M1"], P, tr["test"], th["test"].members, kind)
    g6 = M.grade_pointing(it["M6"], P, tr["m6"], th["m6"].members, kind)
    g3 = M.grade_pointing(it["M3"], P, tr["m3"], th["m3"].members, kind)
    out: Dict[str, object] = {"M1": M.summarise_pointing(g1), "M6": M.summarise_pointing(g6),
                              "M3": M.summarise_m3(g3, it["M3"]), "roads": {}}
    ptr = ctx.ptr[kind]
    for road, ans in A["roads"].items():
        key = A["m2a_keys"][road]
        names = {}
        for t in TYPE_WORDS:
            got = [(ans.get(x["item_id"]) or {}) for x in it["NAME"]]
            ok = [g["name"][t] == x[t] for g, x in zip(got, it["NAME"]) if g.get("name") and g["name"].get(t) is not None]
            em = [x[t] in g["emit"] for g, x in zip(got, it["NAME"]) if g.get("emit") is not None]
            names[t] = {"forced": (sum(ok) / len(ok) if ok else None), "n": len(ok), "emits_true": (sum(em) / len(em) if em else None)}
        sp_rows = M.grade_mouth_r(it["SPEAK"], ans, tr["speak"], ptr)
        s2_rows = M.grade_mouth_r(it["SPEAK2"], ans, tr["speak2"], ptr)
        dc_rows = M.grade_decline(it["DECLINE"], ans, tr["decline"], ptr)
        organ = None
        if arm in LDA_ARMS:
            fits = [f for f in ((ans.get(x["item_id"]) or {}).get("colour_fit") for x, r in zip(it["DECLINE"], dc_rows)
                                if r["covered"]) if f]
            organ = {w: {"mean_d_over_B": float(np.mean([f[w] for f in fits if w in f])),
                         "inside_band": float(np.mean([f[w] <= 1.0 for f in fits if w in f])), "n": len(fits)}
                     for w in W.COLOUR_NAMES if any(w in f for f in fits)}
        gb = out["M1"]["graded"]
        out["roads"][road] = {"m2a_key": key, "mouth": A["mouths"][road], "M2a": M.grade_m2a(it["M2a"], P, key),
                              "false_refusal": gb.get("false_refusal" if key == "none" else "false_refusal_i"),
                              "n_fr": gb["n_fr"],
                              "M2b": M.grade_m2b(it["M2b"], ans, None if kind == "truth" else ctx.m2b_cov, "emit"),
                              "NAME": names, "MOUTH": M.summarise_mouth_r(sp_rows, s2_rows),
                              "DECLINE": M.summarise_decline(dc_rows), "organ_purple": organ,
                              "readback_decline": M._rate(r["readback_ok"] for r in dc_rows if r["covered"] and r["spoken"])[0]}
    return out


def null_record(rs: Path) -> Dict[str, object]:
    """The seed's null draws (k = 1..K the distribution; k = 0, S1b-1's own draw, printed apart)."""
    nd = rs / "nulls"
    rows = [json.loads(p.read_text()) for p in sorted(nd.glob("*.json"))] if nd.exists() else []
    draws = sorted((r for r in rows if r["k"] >= 1), key=lambda r: r["k"])
    k0 = next((r for r in rows if r["k"] == 0), None)
    ref = draws[0] if draws else (k0 or {})
    return {"K": len(draws), "ks": [r["k"] for r in draws], "m1": [r["m1"] for r in draws], "m3": [r["m3"] for r in draws],
            "summary_m1": M.null_summary([r["m1"] for r in draws]), "summary_m3": M.null_summary([r["m3"] for r in draws]),
            "chance_m1": ref.get("chance_m1"), "chance_m3": ref.get("chance_m3"), "n_m1": ref.get("n_m1"),
            "n_m3": ref.get("n_m3"), "k0": k0, "cpu_s": float(sum(r["cpu_s"] for r in rows))}


def grade_seed_r(root: Path, ws: int, arms: Sequence[str] = R_ARMS, log=print) -> Dict[str, object]:
    ctx = _RCtx(root, ws)
    rs = r_seed_root(root, ws)
    out = {"prereg_s1b1r_sha256": PREREG_S1B1R_SHA256, "amend1_sha256": S1B1R_AMEND1_SHA256,
           "prereg_s1b1_sha256": PREREG_S1B1_SHA256, "world_seed": ws, "test_seed": W.FRESH_TEST_SEEDS[ws],
           "meeting_seen": ctx.meeting_seen, "arms": {},
           "target_mix": M.target_mix(ctx.items["SPEAK2"], ctx.truth["speak2"])}
    for arm in arms:
        d = rs / "arms" / arm
        rec = json.loads((d / "record.json").read_text())
        out["arms"][arm] = {"eps": rec["eps"], "lr": rec["lr"], "cpu_s": rec["cpu_s"], "wall_s": rec["wall_s"], "rp": {}}
        for rp in sorted(int(k) for k in rec["reading_points"]):
            g = grade_answers_r(ctx, arm, json.loads((d / f"answers_{rp:05d}.json").read_text()))
            g["reader"] = rec["reading_points"][str(rp)]["reader"]
            out["arms"][arm]["rp"][str(rp)] = g
    out["nulls"] = null_record(rs)
    dump(rs / "marks.json", out)
    log(f"[grade-r {ws}] written {rs / 'marks.json'}")
    return out


# ------------------------------------------------------------------------------------------------ the bars (§5) and §6
def bars_r(marks: Dict[str, object], rp: str = str(W.N_TRAIN)) -> Dict[str, object]:
    """PREREG-S1B1R §5's bars for one seed at `rp` — A-RW-R's LAW, P-ORACLE (its own road through the same mouth) beside
    every mark as the fraction's base; n < 30 → UNDERPOWERED; a reading of nothing, or a P-ORACLE reading of nothing under a
    fraction bar, reads NOT GRADABLE (never 0.0); DECLINE is a READING; the one-difference readings printed beside."""
    A = {a: marks["arms"][a]["rp"][rp] for a in marks["arms"]}
    law = lambda a: A[a]["roads"]["LAW"]
    rd = lambda name: A["A-RW-R"]["roads"].get(name)
    r: Dict[str, Dict[str, object]] = {}
    rows = {}
    for key in ("graded", "size2", "size3"):
        a = A["A-RW-R"]["M1"][key]
        prw, po = A["P-ORACLE-RW"]["M1"][key]["covered"], A["P-ORACLE"]["M1"][key]["covered"]
        brw, blda = _frac(M.BARS["M1_vs_PORACLE_RW"], prw), _frac(M.BARS["M1_vs_PORACLE"], po)
        rows[key] = {"value": a["covered"], "n": a["n_covered"], "all": a["all"], "n_all": a["n_all"], "chance": a["chance_covered"],
                     "p_oracle": po, "p_oracle_rw": prw, "bar_rw": brw, "bar_lda": blda,
                     "pass": _ge(a["covered"], brw) and _ge(a["covered"], blda),
                     "oracle_truth": A["ORACLE-TRUTH"]["M1"][key]["covered"], "n_unheard": a["n_unheard"]}
    r["M1"] = dict(rows["graded"])
    r["M1"]["by_size"] = {"size2": rows["size2"], "size3": rows["size3"]}
    nl = marks["nulls"]
    for mk, val, summ, ch, k0key in (("NULL-M1", r["M1"]["value"], nl["summary_m1"], nl["chance_m1"], "m1"),
                                     ("NULL-M3", A["A-RW-R"]["M3"]["all"]["covered"], nl["summary_m3"], nl["chance_m3"], "m3")):
        p95 = summ["p95"]
        r[mk] = {"value": val, "bar": p95, "dist": summ, "chance": ch, "K": nl["K"],
                 "median_minus_chance": (None if summ["median"] is None or ch is None else summ["median"] - ch),
                 "k0": (nl["k0"] or {}).get(k0key), "n": summ["n"], "pass": bool(val is not None and p95 is not None and val > p95),
                 "not_gradable": ("no null draw" if p95 is None else False)}
    L = law("A-RW-R")
    lm = L["M2a"]["all"]
    po2, po_fr = law("P-ORACLE")["M2a"]["all"]["refusal"], law("P-ORACLE")["false_refusal"]
    v2 = M.m2a_verdict(lm["refusal"], L["false_refusal"], po2, po_fr)
    side = lambda name, f: (f(rd(name)) if rd(name) is not None else None)
    r["M2a"] = {"value": lm["refusal"], "n": lm["n"], "false_refusal": L["false_refusal"], "n_fr": L["n_fr"],
                "p_oracle": po2, "p_oracle_fr": po_fr, "pass": v2["pass"], "ceiling_bound": v2["ceiling_bound"],
                "failing_halves": v2["failing_halves"], "whole_bar_ceiling": v2["whole_bar_ceiling"],
                "r_none_dist": side("R-NONE-DIST", lambda g: {"refusal": g["M2a"]["all"]["refusal"], "false_refusal": g["false_refusal"]}),
                "s1b1_roads": side("S1B1-ROADS", lambda g: {"refusal": g["M2a"]["all"]["refusal"], "false_refusal": g["false_refusal"]})}
    m2b = L["M2b"]["graded"]
    po3 = law("P-ORACLE")["M2b"]["graded"]["correct"]
    ok3 = _ge(m2b["correct"], M.BARS["M2b"])
    r["M2b"] = {"value": m2b["correct"], "n": m2b["n"], "idk": m2b["idk"], "p_oracle": po3, "pass": ok3,
                "ceiling_bound": (not ok3) and po3 is not None and po3 < M.BARS["M2b"],
                "r_tt": side("R-TT", lambda g: g["M2b"]["graded"]["correct"]),
                "r_diag": side("R-DIAG", lambda g: g["M2b"]["graded"]["correct"]),
                "s1b1_roads": side("S1B1-ROADS", lambda g: g["M2b"]["graded"]["correct"]),
                "p_oracle_rw": law("P-ORACLE-RW")["M2b"]["graded"]["correct"],
                "shape_words": m2b["shape_words_emitted"], "dax_emitted": int(m2b["shape_words_emitted"].get("dax", 0)),
                "per_shape": {s: L["M2b"][f"shape:{s}"]["correct"] for s in W.M2B_SHAPES},
                "per_shape_p_oracle": {s: law("P-ORACLE")["M2b"][f"shape:{s}"]["correct"] for s in W.M2B_SHAPES},
                "diamond": L["M2b"]["diamond"]["correct"], "diamond_p_oracle": law("P-ORACLE")["M2b"]["diamond"]["correct"]}
    a3 = A["A-RW-R"]["M3"]["all"]
    p3 = A["P-ORACLE"]["M3"]["all"]["covered"]
    bar3 = _frac(M3_VS_PORACLE, p3)
    r["M3"] = {"value": a3["covered"], "n": a3["n_covered"], "all": a3["all"], "n_all": a3["n_all"], "chance": a3["chance_covered"],
               "p_oracle": p3, "bar": bar3, "pass": _ge(a3["covered"], bar3),
               "not_gradable": ("P-ORACLE reads nothing" if bar3 is None else False),
               "by_kind": {k: A["A-RW-R"]["M3"][f"kind:{k}"]["covered"] for k in ("colour", "shape", "both")},
               "by_kind_p_oracle": {k: A["P-ORACLE"]["M3"][f"kind:{k}"]["covered"] for k in ("colour", "shape", "both")}}
    seen = marks.get("meeting_seen")
    m6 = A["A-RW-R"]["M6"]["all"]
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
                   "ceiling_bound": (not ok6) and (po6 is None or po6 < M.BARS["M6"])}
    mo, pmo = L["MOUTH"], law("P-ORACLE")["MOUTH"]

    def frac_mark(value, n, pval, k, extra):
        bar = _frac(k, pval)
        ng = "nothing to read" if value is None else ("P-ORACLE reads nothing" if bar is None else False)
        return {"value": value, "n": n, "p_oracle": pval, "bar": bar, "pass": _ge(value, bar), "not_gradable": ng, **extra}

    kinds = lambda key: {k: v[key] for k, v in mo["kinds"].items()}
    r["SPOKEN"] = frac_mark(mo["spoken"], mo["n_spoken_cov"], pmo["spoken"], SPOKEN_VS_PORACLE,
                            {"reasons": (mo["speak"] or {}).get("reasons"), "spoken2": mo["spoken2"], "reasons2": mo["reasons2"],
                             "p_oracle_spoken2": pmo["spoken2"]})
    r["TRUTH"] = frac_mark(mo["truth"], mo["n_truth"], pmo["truth"], TRUTH_VS_PORACLE,
                           {"n_p_oracle": pmo["n_truth"], "truth_seen": (mo["speak"] or {}).get("truth_seen"),
                            "truth_x_spoken": (mo["speak"] or {}).get("truth_x_spoken"),
                            "p_oracle_truth_x_spoken": (pmo["speak"] or {}).get("truth_x_spoken"),
                            "r_oldmouth": side("R-OLDMOUTH", lambda g: g["MOUTH"]["truth"]),
                            "s1b1_roads": side("S1B1-ROADS", lambda g: g["MOUTH"]["truth"])})
    r["TRUTH-NEED"] = frac_mark(mo["truth_need"], mo["n_truth_need"], pmo["truth_need"], TRUTH_NEED_VS_PORACLE,
                                {"n_p_oracle": pmo["n_truth_need"], "lengths": mo["length_mix_speak2"],
                                 "kinds": kinds("truth_need"), "kinds_n": kinds("n_spoken"),
                                 "p_oracle_kinds": {k: v["truth_need"] for k, v in pmo["kinds"].items()}})
    r["MINIMAL"] = frac_mark(mo["minimal"], mo["n_minimal"], pmo["minimal"], MINIMAL_VS_PORACLE,
                             {"n_p_oracle": pmo["n_minimal"], "lengths": mo["length_mix"], "parent_mix": PARENT_MIX,
                              "kinds": kinds("minimal"), "kinds_n": kinds("n_minimal")})
    r["ORDER"] = frac_mark(mo["order"], mo["n_order"], pmo["order"], ORDER_VS_PORACLE,
                           {"n_p_oracle": pmo["n_order"], "kinds": kinds("order"), "kinds_n": kinds("n_order")})
    if mo["n_order"] == 0:
        r["ORDER"]["not_gradable"] = "no multi-word phrase spoken"
    rb = mo["readback_all"]
    r["READ-BACK"] = {"value": rb, "n": mo["n_readback_all"], "pass": (rb == 1.0) if rb is not None else False,
                      "not_gradable": ("nothing spoken" if rb is None else False), "speak": mo["readback_speak"],
                      "speak2": mo["readback2"], "p_oracle": pmo["readback_all"]}
    dc, pdc = L["DECLINE"], law("P-ORACLE")["DECLINE"]
    r["DECLINE"] = {"value": dc["decline"], "n": dc["n_covered"], "p_oracle": pdc["decline"], "reading": True, "pass": None,
                    "not_gradable": False, "kind_A_spoken": dc["kind_A_spoken"], "kind_A_truth": dc["kind_A_truth"],
                    "kind_B_decline_rate": dc["kind_B_decline_rate"], "reasons": dc["reasons"],
                    "organ_purple": law("P-ORACLE").get("organ_purple")}
    for k in ("M1", "M2a", "M2b", "M3", "M6", "SPOKEN", "TRUTH", "TRUTH-NEED", "MINIMAL", "ORDER"):
        r[k]["underpowered"] = (not r[k].get("not_gradable")) and (r[k].get("n") or 0) < M.UNDERPOWERED_N
    for k in ("NULL-M1", "NULL-M3", "READ-BACK", "DECLINE"):
        r[k]["underpowered"] = False
    m2b_v, t5 = r["M2b"]["value"], False
    t5 = bool(m2b_v is not None and m2b_v < M.BARS["M2b"] and po3 is not None and po3 >= M.BARS["M2b"])
    limit = None
    if t5:
        rtt, prw = r["M2b"]["r_tt"], r["M2b"]["p_oracle_rw"]
        limit = ("the ear's types" if (rtt is not None and rtt >= M.BARS["M2b"]) else
                 "the store's attributions" if (prw is not None and prw >= M.BARS["M2b"]) else
                 "the per-type pooled form on a learner's store")
    tv, tn = r["TRUTH"]["value"], r["TRUTH"]["n"] or 0
    ov, on, ob = r["ORDER"]["value"], r["ORDER"]["n"] or 0, r["ORDER"]["bar"]
    r["refute"] = {"T5_seed": t5, "T5_limit": limit,
                   "T3p": bool(r["M1"]["pass"] and tv is not None and tn >= M.UNDERPOWERED_N and tv < T3_REFUTE),
                   "ORDER": bool(on >= M.UNDERPOWERED_N and ov is not None and ob is not None and ov < ob),
                   "M2a_below": bool(r["M2a"]["value"] is not None and r["M2a"]["value"] < M.BARS["M2a_refusal"]),
                   "null": bool(r["NULL-M1"]["value"] is not None and r["NULL-M1"]["bar"] is not None
                                and r["NULL-M1"]["value"] <= r["NULL-M1"]["bar"])}
    return r


def _verdict_r(b: Dict[str, object]) -> str:
    if b.get("reading"):
        return "READING"
    return _verdict(b)


def _d(dct: Optional[Dict[str, object]], nd: int = 3) -> str:
    """A dict of rates / counts printed compactly (None → —)."""
    if dct is None:
        return "  —  "
    return "{" + ", ".join(f"{k}: {(_f(v, nd) if isinstance(v, float) or v is None else v)}" for k, v in dct.items()) + "}"


def print_seed_table_r(marks: Dict[str, object], rp: Optional[str] = None, log=print) -> List[str]:
    """One seed's tables, read whole: the learned types at every reading point beside the world's (with the one-alone type
    and its count), M1 / M3 by reading point, the blocks at the last point, the null's distribution, every arm × road's
    answer kinds (M2a, M2b and the shape words emitted, NAME, the mouth's marks, lengths and reasons, SPEAK2 per kind,
    DECLINE), the organ fact and the achieved SPEAK2 target mix."""
    ws = marks["world_seed"]
    arms = [a for a in R_ARMS if a in marks["arms"]]
    rps = sorted(int(k) for k in marks["arms"]["A-RW-R"]["rp"])
    top = rp if rp is not None else str(max(rps))
    L = [f"== S1b-1R marks · world seed {ws} (fresh test seed {marks['test_seed']}) · the one meeting seen: {marks.get('meeting_seen')} =="]
    L.append("the learned types (A-RW-R's ear cover over its mature words, §1 a) by reading point, beside the world's three types:")
    for r_ in rps:
        rec = marks["arms"]["A-RW-R"]["rp"][str(r_)]["reader"]
        tc = rec.get("types_check") or {}
        one = rec.get("one_alone")
        L.append(f"   {r_:>6}: " + " ".join("(" + " ".join(t) + ")" for t in rec["types"])
                 + f" — the world's: {'EQUAL' if tc.get('pass') else 'DIFFER ' + str(tc.get('world'))}"
                 + " · the one-alone type: " + (("(" + " ".join(rec["types"][one]) + ")") if one is not None else "none")
                 + f" · one-word utterances per type {rec['alone_counts']}")
    for arm in ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH"):
        if arm in marks["arms"]:
            rec = marks["arms"][arm]["rp"][top]["reader"]
            one = rec.get("one_alone")
            L.append(f"   {arm} at {top}: " + " ".join("(" + " ".join(t) + ")" for t in rec["types"])
                     + " · the one-alone type: " + (("(" + " ".join(rec["types"][one]) + ")") if one is not None else "none")
                     + f" · counts {rec['alone_counts']}")
    L.append("M1 (covered, the graded 2- and 3-thing items) / M3 (covered) by reading point:")
    L.append("   arm            " + " ".join(f"{r_:>11d}" for r_ in rps))
    for arm in arms:
        vals = [(marks["arms"][arm]["rp"][str(r_)]["M1"]["graded"]["covered"], marks["arms"][arm]["rp"][str(r_)]["M3"]["all"]["covered"])
                if str(r_) in marks["arms"][arm]["rp"] else (None, None) for r_ in rps]
        L.append(f"   {arm:<14} " + " ".join(f"{_f(a)}/{_f(b)}" for a, b in vals))
    L.append(f"At {top} scenes (covered · all), chance and n from A-RW-R's items:")
    for key in ("graded", "size2", "size3", "size1"):
        b0 = marks["arms"]["A-RW-R"]["rp"][top]["M1"][key]
        L.append(f"   M1 {key:<8} cov {_f(b0.get('coverage'))} chance {_f(b0.get('chance_covered'))} n {b0.get('n_covered')}/{b0.get('n_all')} | "
                 + " | ".join(f"{a} {_f(marks['arms'][a]['rp'][top]['M1'][key]['covered'])}·{_f(marks['arms'][a]['rp'][top]['M1'][key]['all'])}" for a in arms))
    for key in ["all", "kind:colour", "kind:shape", "kind:both", "size2", "size3"] + [f"pair:{sh}-{co}" for sh, co in W.HELDOUT]:
        b0 = marks["arms"]["A-RW-R"]["rp"][top]["M3"][key]
        L.append(f"   M3 {key:<22} chance {_f(b0.get('chance_covered'))} n {b0.get('n_covered')}/{b0.get('n_all')} | "
                 + " | ".join(f"{a} {_f(marks['arms'][a]['rp'][top]['M3'][key]['covered'])}" for a in arms))
    nl = marks["nulls"]
    for key, mk in (("summary_m1", "M1"), ("summary_m3", "M3")):
        s = nl[key]
        L.append(f"   THE NULL {mk}: K {nl['K']} draws (keys null:{ws}:1..{nl['K']}) {[_f(v) for v in nl[mk.lower()]]} → min {_f(s['min'])} · median {_f(s['median'])}"
                 f" · max {_f(s['max'])} · 95th pct {_f(s['p95'])} · chance {_f(nl['chance_' + mk.lower()])} · k = 0 (S1b-1's draw) {_f((nl['k0'] or {}).get(mk.lower()))}")
    for arm in arms:
        Rr = marks["arms"][arm]["rp"][top]
        for road in [n for n in ("LAW",) + R_READINGS if n in Rr["roads"]]:
            g = Rr["roads"][road]
            m2b, mo, nm, dc = g["M2b"]["graded"], g["MOUTH"], g["NAME"], g["DECLINE"]
            L.append(f"   {arm:<12} {road:<11} [{g['mouth']} mouth; «none» {g['m2a_key']}] M2a refusal {_f(g['M2a']['all']['refusal'])} false {_f(g['false_refusal'])}"
                     f" · M2b {_f(m2b['correct'])} (n {m2b['n']}; idk {_f(m2b['idk'])}; diamond {_f(g['M2b']['diamond']['correct'])}) shape words said {m2b['shape_words_emitted']}"
                     f" · NAME forced shape {_f(nm['shape']['forced'])} colour {_f(nm['colour']['forced'])} size {_f(nm['size']['forced'])}"
                     f" · «what is this?» emits the true word shape {_f(nm['shape']['emits_true'])} colour {_f(nm['colour']['emits_true'])} size {_f(nm['size']['emits_true'])}")
            L.append(f"   {'':<24} SPEAK spoken {_f(mo['spoken'])} (n {mo['n_spoken_cov']}) · TRUTH {_f(mo['truth'])} (n {mo['n_truth']}; seen {_f((mo['speak'] or {}).get('truth_seen'))};"
                     f" ×spoken {_f((mo['speak'] or {}).get('truth_x_spoken'))}) · SPEAK2 spoken {_f(mo['spoken2'])} (n {mo['n_cov2']}) · TRUTH-NEED {_f(mo['truth_need'])} (n {mo['n_truth_need']})"
                     f" · MINIMAL {_f(mo['minimal'])} (n {mo['n_minimal']}) · ORDER {_f(mo['order'])} (n {mo['n_order']}) · READ-BACK {_f(mo['readback_all'])} (n {mo['n_readback_all']})")
            L.append(f"   {'':<24} lengths SPEAK+SPEAK2 {_d(mo['length_mix'])} · SPEAK {_d(mo['length_mix_speak'])} · SPEAK2 {_d(mo['length_mix_speak2'])}"
                     f" · reasons SPEAK {(mo['speak'] or {}).get('reasons')} · SPEAK2 {mo['reasons2']}"
                     f" · DECLINE {_f(dc['decline'])} (n {dc['n_covered']}; A spoken {_f(dc['kind_A_spoken'])} truth {_f(dc['kind_A_truth'])}; B decline {_f(dc['kind_B_decline_rate'])};"
                     f" reasons {dc['reasons']}; read-back {_f(g.get('readback_decline'))})")
            L.append(f"   {'':<24} SPEAK2 per kind: " + " · ".join(
                f"{k} TRUTH-NEED {_f(v['truth_need'])} (n {v['n_spoken']}) MINIMAL {_f(v['minimal'])} (n {v['n_minimal']}) ORDER {_f(v['order'])} (n {v['n_order']})"
                f" lengths {_d(v['length_mix'])} reasons {v['reasons']}" for k, v in mo["kinds"].items()))
    org = marks["arms"].get("P-ORACLE", {}).get("rp", {}).get(top, {}).get("roads", {}).get("LAW", {}).get("organ_purple")
    if org:
        L.append("   the organ fact (P-ORACLE's colour d_w / B_w of the purple targets): " + " · ".join(
            f"{w} mean {v['mean_d_over_B']:.2f} inside {v['inside_band']:.2f}" for w, v in org.items()))
    L.append("   the achieved SPEAK2 target mix per kind (AMENDMENT 1 §2): " + " · ".join(
        f"{k} shape {v['shape']} colour {v['colour']} size {v['size']}" for k, v in sorted(marks["target_mix"].items())))
    for l in L:
        log(l)
    return L


def report_r(root: Path, rp: str = str(W.N_TRAIN), log=print) -> Dict[str, object]:
    """THE GRADER READING THE LAW AS WRITTEN: every seed's tables, §5's bars per seed with P-ORACLE beside, the per-seed
    verdict line, «every bar at all three seeds» (M6 where the meeting was seen; DECLINE a reading), §6's refutations."""
    out: Dict[str, object] = {"prereg_s1b1r_sha256": PREREG_S1B1R_SHA256, "amend1_sha256": S1B1R_AMEND1_SHA256,
                              "prereg_s1b1_sha256": PREREG_S1B1_SHA256, "seeds": {}}
    lines = [f"S1b-1R report · PREREG-S1B1R sha {PREREG_S1B1R_SHA256} · AMENDMENT 1 sha {S1B1R_AMEND1_SHA256} · PREREG-S1B1 {PREREG_S1B1_SHA256[:16]}…", ""]
    for ws in W.WORLD_SEEDS:
        mk = json.loads((r_seed_root(root, ws) / "marks.json").read_text())
        lines += print_seed_table_r(mk, rp, log=lambda s: None)
        out["seeds"][str(ws)] = bars_r(mk, rp)
        lines.append("")
    lines.append("== S1b-1R BARS at 10,000 scenes (A-RW-R, the law, on the FRESH test seeds; P-ORACLE beside every mark as the fraction's base; "
                 "n < 30 → UNDERPOWERED; the one-difference readings beside, never bars) ==")
    for ws in W.WORLD_SEEDS:
        b = out["seeds"][str(ws)]
        m1 = b["M1"]
        lines.append(f"{ws} M1 {_f(m1['value'])} (all {_f(m1['all'])}; n {m1['n']}/{m1['n_all']}; chance {_f(m1['chance'])}) bars ≥ {_f(m1['bar_rw'])} "
                     f"(0.90 × P-ORACLE-RW {_f(m1['p_oracle_rw'])}) and ≥ {_f(m1['bar_lda'])} (0.80 × P-ORACLE {_f(m1['p_oracle'])}) → {_verdict_r(m1)} · ORACLE-TRUTH {_f(m1['oracle_truth'])}")
        for k, v in m1["by_size"].items():
            lines.append(f"          M1 {k}: {_f(v['value'])} (n {v['n']}, chance {_f(v['chance'])}) → {_verdict(v)}")
        for mk in ("NULL-M1", "NULL-M3"):
            nb = b[mk]
            ds = nb["dist"]
            lines.append(f"          THE NULL ({mk[5:]}): A-RW-R {_f(nb['value'])} > the null's 95th percentile {_f(nb['bar'])} → {_verdict_r(nb)} · K {nb['K']}: min {_f(ds['min'])} "
                         f"median {_f(ds['median'])} max {_f(ds['max'])} · chance {_f(nb['chance'])} (median − chance {_f(nb['median_minus_chance'])}) · k = 0 (S1b-1's draw) {_f(nb['k0'])}")
        m2a = b["M2a"]
        lines.append(f"          M2a refusal {_f(m2a['value'])} (n {m2a['n']}) · false refusal {_f(m2a['false_refusal'])} (n {m2a['n_fr']}) · P-ORACLE {_f(m2a['p_oracle'])} / {_f(m2a['p_oracle_fr'])} → {_verdict_r(m2a)}"
                     + (f" (the learner fails: {', '.join(m2a['failing_halves'])}; whole-bar: {'CEILING-BOUND' if m2a['whole_bar_ceiling'] else 'FAIL'})" if not m2a["pass"] else "")
                     + f" · R-NONE-DIST {_d(m2a['r_none_dist'])} · S1B1-ROADS {_d(m2a['s1b1_roads'])}")
        m2b = b["M2b"]
        lines.append(f"          M2b {_f(m2b['value'])} (n {m2b['n']}; «I don't know» {_f(m2b['idk'])}) · P-ORACLE {_f(m2b['p_oracle'])} → {_verdict_r(m2b)} · R-TT {_f(m2b['r_tt'])} · R-DIAG {_f(m2b['r_diag'])}"
                     f" · P-ORACLE-RW {_f(m2b['p_oracle_rw'])} · S1B1-ROADS {_f(m2b['s1b1_roads'])} · per shape {_d(m2b['per_shape'])} (P-ORACLE {_d(m2b['per_shape_p_oracle'])})"
                     f" · diamond (apart) {_f(m2b['diamond'])} · P-ORACLE {_f(m2b['diamond_p_oracle'])} · shape words said {m2b['shape_words']} («dax» {m2b['dax_emitted']})")
        m3 = b["M3"]
        lines.append(f"          M3 {_f(m3['value'])} (all {_f(m3['all'])}; n {m3['n']}/{m3['n_all']}; chance {_f(m3['chance'])}) ≥ {_f(m3['bar'])} (0.80 × P-ORACLE {_f(m3['p_oracle'])}) → {_verdict_r(m3)}"
                     f" · per kind {_d(m3['by_kind'])} (P-ORACLE {_d(m3['by_kind_p_oracle'])})")
        m6 = b["M6"]
        lines.append("          M6 " + (f"NOT GRADABLE — {m6['not_gradable']}" if m6.get("not_gradable") else
                                          f"{_f(m6['value'])} (all {_f(m6['all'])}; n {m6['n']}/{m6['n_all']}; chance {_f(m6['chance'])}) ≥ 0.70 · P-ORACLE {_f(m6['p_oracle'])} → {_verdict_r(m6)}"))
        s, t, tn, mn, o, rb, dcl = (b[k] for k in ("SPOKEN", "TRUTH", "TRUTH-NEED", "MINIMAL", "ORDER", "READ-BACK", "DECLINE"))
        lines.append(f"          SPOKEN {_f(s['value'])} (n {s['n']}) ≥ {_f(s['bar'])} (0.80 × P-ORACLE {_f(s['p_oracle'])}) → {_verdict_r(s)} · reasons {s['reasons']}"
                     f" · SPEAK2 spoken {_f(s['spoken2'])} (P-ORACLE {_f(s['p_oracle_spoken2'])}) reasons {s['reasons2']}")
        lines.append(f"          TRUTH {_f(t['value'])} (n {t['n']}) ≥ {_f(t['bar'])} (0.90 × P-ORACLE {_f(t['p_oracle'])}, n {t['n_p_oracle']}) → {_verdict_r(t)} · seen {_f(t['truth_seen'])}"
                     f" · ×spoken {_f(t['truth_x_spoken'])} (P-ORACLE {_f(t['p_oracle_truth_x_spoken'])}) · R-OLDMOUTH {_f(t['r_oldmouth'])} · S1B1-ROADS {_f(t['s1b1_roads'])}")
        lines.append(f"          TRUTH-NEED {_f(tn['value'])} (n {tn['n']}) ≥ {_f(tn['bar'])} (0.90 × P-ORACLE {_f(tn['p_oracle'])}, n {tn['n_p_oracle']}) → {_verdict_r(tn)}"
                     f" · per kind {_d(tn['kinds'])} (n {tn['kinds_n']}; P-ORACLE {_d(tn['p_oracle_kinds'])}) · lengths {_d(tn['lengths'])}")
        lines.append(f"          MINIMAL {_f(mn['value'])} (n {mn['n']} true-and-unique) ≥ {_f(mn['bar'])} (0.90 × P-ORACLE {_f(mn['p_oracle'])}, n {mn['n_p_oracle']}) → {_verdict_r(mn)}"
                     f" · per kind {_d(mn['kinds'])} (n {mn['kinds_n']}) · lengths SPEAK + SPEAK2 {_d(mn['lengths'])} vs the parent's {PARENT_MIX} (a reading: the parent speaks by template)")
        lines.append(f"          ORDER {_f(o['value'])} (n {o['n']}) ≥ {_f(o['bar'])} (0.95 × P-ORACLE {_f(o['p_oracle'])}, n {o['n_p_oracle']}; graded when n ≥ 30) → {_verdict_r(o)}"
                     f" · per kind {_d(o['kinds'])} (n {o['kinds_n']})")
        lines.append(f"          READ-BACK {_f(rb['value'])} (n {rb['n']}; SPEAK {_f(rb['speak'])} · SPEAK2 {_f(rb['speak2'])}; the wiring pin = 1.000) → "
                     + (_verdict_r(rb) if rb["value"] is None or rb["value"] == 1.0 else "BROKEN ROAD"))
        lines.append(f"          DECLINE {_f(dcl['value'])} (n {dcl['n']}) · P-ORACLE {_f(dcl['p_oracle'])} → a READING (the organ puts purple inside a trained colour's band)"
                     f" · kind A spoken {_f(dcl['kind_A_spoken'])} truth {_f(dcl['kind_A_truth'])} · kind B decline {_f(dcl['kind_B_decline_rate'])} · reasons {dcl['reasons']}")
    reads = {k: {ws: _verdict_r(out["seeds"][str(ws)][k]) for ws in W.WORLD_SEEDS} for k in R_MARK_ORDER}
    for ws in W.WORLD_SEEDS:
        rb = out["seeds"][str(ws)]["READ-BACK"]
        if rb["value"] is not None and rb["value"] != 1.0:
            reads["READ-BACK"][ws] = "BROKEN ROAD"
    grad6 = [ws for ws in W.WORLD_SEEDS if not out["seeds"][str(ws)]["M6"].get("not_gradable")]
    allpass = {k: all(reads[k][ws] == "PASS" for ws in W.WORLD_SEEDS) for k in R_BARS if k != "M6"}
    allpass["M6"] = bool(grad6) and all(reads["M6"][ws] == "PASS" for ws in grad6)
    lines.append("per seed: " + " · ".join(f"{k} " + "/".join(reads[k][ws] for ws in W.WORLD_SEEDS) for k in R_MARK_ORDER))
    lines.append("every bar at all 3 seeds (M6 where the meeting was seen: " + ", ".join(map(str, grad6)) + "; DECLINE a reading): "
                 + " · ".join(f"{k} {'PASS' if allpass[k] else 'no'}" for k in R_BARS)
                 + f" → S1b-1R {'PASSES' if all(allpass.values()) else 'does not pass'}")
    ref = {ws: out["seeds"][str(ws)]["refute"] for ws in W.WORLD_SEEDS}
    t5 = sum(ref[ws]["T5_seed"] for ws in W.WORLD_SEEDS) >= 2
    m2a_law = sum(ref[ws]["M2a_below"] for ws in W.WORLD_SEEDS) >= 2
    lines.append("refutations (§6): T5 (the READER from its own store: M2b < 0.80 at ≥ 2 seeds while P-ORACLE ≥ 0.80) "
                 + ("REFUTED" if t5 else "not refuted") + " ("
                 + " ".join(f"{ws}:{'yes — the limit: ' + ref[ws]['T5_limit'] if ref[ws]['T5_seed'] else 'no'}" for ws in W.WORLD_SEEDS) + ")"
                 + " · T3′ (TRUTH < 0.80, n ≥ 30, where M1 passes) " + " ".join(f"{ws}:{'REFUTED' if ref[ws]['T3p'] else 'no'}" for ws in W.WORLD_SEEDS)
                 + " · ORDER (< 0.95 × P-ORACLE with n ≥ 30) " + " ".join(f"{ws}:{'REFUTED' if ref[ws]['ORDER'] else 'no'}" for ws in W.WORLD_SEEDS)
                 + f" · M2a's law (refusal < 0.80 at ≥ 2 seeds) {'REFUTED — reading (i) belonged to its items' if m2a_law else 'stands'} ("
                 + " ".join(f"{ws}:{'below' if ref[ws]['M2a_below'] else 'not below'}" for ws in W.WORLD_SEEDS) + ")"
                 + " · the null (A-RW-R's M1 ≤ the null's 95th percentile at any seed) "
                 + ("REFUTED — the pairings did not teach it" if any(ref[ws]["null"] for ws in W.WORLD_SEEDS) else "not refuted")
                 + " (" + " ".join(f"{ws}:{'at or below' if ref[ws]['null'] else 'above'}" for ws in W.WORLD_SEEDS) + ")")
    out["all_pass"] = allpass
    out["passes"] = all(allpass.values())
    out["reads"] = {k: {str(ws): v for ws, v in d.items()} for k, d in reads.items()}
    out["m6_gradable_seeds"] = grad6
    for l in lines:
        log(l)
    out["lines"] = lines
    dump(Path(root) / "report.json", out)
    (Path(root) / "report.txt").write_text("\n".join(lines) + "\n")
    return out


# ------------------------------------------------------------------------------------------------ THE FIRST GATE (S1b-1R §4)
def gate_or_chosen_r(root: Path = C.RUNS) -> Dict[str, object]:
    """THE FIRST GATE's record under `root` (ε, the lr): the unit never re-chooses them, and runs only on PROCEED under THIS law."""
    p = Path(root) / "gate" / "gate.json"
    if not p.exists():
        raise RunError(f"{p} missing — THE FIRST GATE runs before any full stream")
    g = json.loads(p.read_text())
    if g.get("verdict") != "PROCEED":
        raise RunError(f"THE FIRST GATE reads {g.get('verdict')!r} — no full run")
    if g.get("prereg_s1b1r_sha256") != PREREG_S1B1R_SHA256 or g.get("amend1_sha256") != S1B1R_AMEND1_SHA256:
        raise RunError("THE FIRST GATE was read under another law — no full run")
    return g


def _spawn_wait(cmds: Sequence[Tuple[str, List[str], Path]], cwd: str) -> List[Dict[str, object]]:
    """Start every command at once (nice 19, S1's environment) and wait on EACH OWN pid; the exit codes are returned."""
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", PYTHONUNBUFFERED="1",
               TMPDIR="/data/dev/brain-runs/tmp", PYTHONDONTWRITEBYTECODE="1")
    procs = []
    for tag, cmd, logf in cmds:
        logf.parent.mkdir(parents=True, exist_ok=True)
        procs.append((tag, subprocess.Popen(["nice", "-n", "19"] + cmd, cwd=cwd, env=env, stdout=open(logf, "w"),
                                            stderr=subprocess.STDOUT)))
    return [{"tag": tag, "rc": p.wait()} for tag, p in procs]


def gate_step2(root: Path, eps: float, log=print) -> Dict[str, object]:
    """§4 step 2 — THE LIFE UNCHANGED (the #180 last-link check): (a) every redrawn cache of S1b-1's world (train and S1b-1's
    six test splits × 3 seeds, the toy) carries S1b-1's specs, canvas shas and glances (S1b-1's files read as plain JSON);
    (b) S1b-1's question items and pointers, rebuilt by S1b-1's own build_questions, equal S1b-1's; (c) S1b-1's SIX arms,
    re-run from THIS code with S1b-1's roads (lr 0.01 / 0.1, the k = 0 derangement, this gate's ε) at 10,000 scenes on
    S1b-1's OWN test seeds and graded by S1b-1's own grader, reproduce S1b-1's bars EXACTLY — full precision against
    S1b-1's marks.json — on M1, M3, M6, M2a, M2b, SPOKEN, TRUTH, READ-BACK per seed, and S1B1-REPORT-REGRADED.txt's printed
    bar section line for line. (Training never reads a calibration, so the 10,000-scene state is the unit's.)"""
    res: Dict[str, object] = {"caches": {}, "items": {}, "bars": {}}
    t0 = time.process_time()
    for ws in W.WORLD_SEEDS:
        for split in ("train",) + C.TEST_SPLITS:
            res["caches"][f"{ws}/{split}"] = C.identity_with(C.cache_dir(root, ws, split), C.cache_dir(C.S1B1_RUNS, ws, split))
    for split in ("toy-train", "toy-test"):
        res["caches"][split] = C.identity_with(C.cache_dir(root, None, split), C.cache_dir(C.S1B1_RUNS, None, split))
    for ws in W.WORLD_SEEDS:
        build_questions(root, ws)
        kn = json.loads((seed_root(root, ws) / "keys.json").read_text())["items"]
        ko = json.loads((seed_root(C.S1B1_RUNS, ws) / "keys.json").read_text())["items"]
        for mark in ("M1", "M2a", "M2b", "M6", "NAME", "M3", "SPEAK", "DECLINE"):
            a = [(it["item_id"], it.get("phrase"), it.get("target")) for it in kn[mark]]
            b = [(it["item_id"], it.get("phrase"), it.get("target")) for it in ko[mark]]
            res["items"][f"{ws}/{mark}"] = {"n": len(a), "same": a == b}
        qn = json.loads((seed_root(root, ws) / "questions.json").read_text())["questions"]
        qo = json.loads((seed_root(C.S1B1_RUNS, ws) / "questions.json").read_text())["questions"]
        res["items"][f"{ws}/questions"] = {"n": sum(len(v) for v in qn.values()), "same": qn == qo}
    cwd = str(Path(__file__).resolve().parents[2])
    base = [sys.executable, "-B", "-m", "brain.scene.run", "arm", "--root", str(root), "--rps", str(W.N_TRAIN),
            "--lr", str(Lr.LR_S1B1), "--eps", repr(float(eps))]
    cmds = [(f"{ws}/{arm}", base + ["--arm", arm, "--world-seed", str(ws)], Path(root) / "gate" / "step2" / "logs" / f"{ws}-{arm}.log")
            for ws in W.WORLD_SEEDS for arm in ARMS]
    w0 = time.perf_counter()
    runs = _spawn_wait(cmds, cwd)
    res["arms"] = runs
    res["arms_wall_s"] = time.perf_counter() - w0
    res["arms_cpu_s"] = 0.0
    for ws in W.WORLD_SEEDS:
        for arm in ARMS:
            p = seed_root(root, ws) / "arms" / arm / "record.json"
            if p.exists():
                res["arms_cpu_s"] += float(json.loads(p.read_text())["cpu_s"])
    if any(r["rc"] != 0 for r in runs):
        res["pass"] = False
        res["why"] = f"arms failed: {[r for r in runs if r['rc'] != 0]}"
        return res
    for ws in W.WORLD_SEEDS:
        bn = bars_for(grade_seed(root, ws, log=lambda s: None))
        bo = bars_for(json.loads((seed_root(C.S1B1_RUNS, ws) / "marks.json").read_text()))
        res["bars"][str(ws)] = {k: bool(bn[k] == bo[k]) for k in STEP2_MARKS}
        res["bars"][str(ws)]["_values"] = {k: [bn[k].get("value"), bo[k].get("value")] for k in STEP2_MARKS}
    dest = Path(root) / "gate" / "step2"
    report(root, log=lambda s: None, dest=dest)
    old = S1B1_REPORT_REGRADED.read_bytes()
    res["regraded_sha_ok"] = hashlib.sha256(old).hexdigest() == S1B1_REPORT_REGRADED_SHA256
    cut = lambda ls: ls[next(i for i, l in enumerate(ls) if l.startswith("== S1b-1 BARS")):]
    nb, ob = cut((dest / "report.txt").read_text().splitlines()), cut(old.decode("utf-8").splitlines())
    diff = [i for i in range(max(len(nb), len(ob))) if i >= len(nb) or i >= len(ob) or nb[i] != ob[i]]
    res["report_bar_section"] = {"n_lines": len(nb), "n_differ": len(diff),
                                 "differ": [{"new": nb[i] if i < len(nb) else None, "s1b1": ob[i] if i < len(ob) else None} for i in diff[:6]]}
    res["cpu_s_in_process"] = time.process_time() - t0
    res["pass"] = bool(all(v["same"] for v in res["caches"].values()) and all(v["same"] for v in res["items"].values())
                       and all(all(v[k] for k in STEP2_MARKS) for v in res["bars"].values()) and not diff
                       and res["regraded_sha_ok"])
    return res


def first_gate_r(root: Path, log=print) -> Dict[str, object]:
    """THE FIRST GATE of PREREG-S1B1R §4 with AMENDMENT 1: six steps, each a STOP on a miss, printed whole; ε (P-ORACLE's,
    chosen on the toy seed by S1a's rule — the READER's ε, §1 b) printed first. Needs every cache under `root`."""
    check_prereg()
    t0, c0 = time.perf_counter(), time.process_time()
    out: Dict[str, object] = {"prereg_s1b1r_sha256": PREREG_S1B1R_SHA256, "amend1_sha256": S1B1R_AMEND1_SHA256,
                              "prereg_s1b1_sha256": PREREG_S1B1_SHA256, "code": code_identity(), "cpu_s": {}}
    lines = ["== THE FIRST GATE (PREREG-S1B1R §4 with AMENDMENT 1; each step stops the run on a miss; printed whole) =="]
    stop: List[str] = []
    # 0. ε, S1a's rule on the toy seed (the same code as S1b-1's gate)
    c = time.process_time()
    tr = Things(C.ScenePercepts(C.cache_dir(root, None, "toy-train")))
    te = Things(C.ScenePercepts(C.cache_dir(root, None, "toy-test")))
    tr_truth, te_truth = C.load_truth(C.cache_dir(root, None, "toy-train")), C.load_truth(C.cache_dir(root, None, "toy-test"))
    items = M.m1_items(te_truth, W.TOY_SEED, mark="TOY")
    eps_rows = {}
    for e in Lr.EPS_GRID:
        Rd = make_learner("P-ORACLE", Lr.LR_S1B1, e)
        train_arm("P-ORACLE", Rd, tr, tr.p.words, tr_truth, list(range(len(tr.p))), W.TOY_SEED)
        Rd.prepare()
        nm = _per_type_naming(Rd, te, te_truth)
        eps_rows[str(e)] = {"naming": nm, "mean": float(np.mean([v[0] for v in nm.values()])),
                            "m1": _toy_m1(Rd, "P-ORACLE", items, te, te_truth)["covered"]}
    eps = float(max(eps_rows.items(), key=lambda kv: (kv[1]["mean"], float(kv[0])))[0])
    out["eps_choice"] = {"grid": eps_rows, "eps": eps}
    out["cpu_s"]["eps"] = time.process_time() - c
    lines.append("0. P-ORACLE's ε on the toy seed (S1a's rule; the READER's ε, §1 b): "
                 + " · ".join(f"{k}: {v['mean']:.3f} · {v['m1']:.3f}" for k, v in eps_rows.items()) + f" → ε {eps} (S1b-1's gate: 0.3)")
    # 1. the eye
    c = time.process_time()
    eye = gate_eye_fixture()
    out["eye"] = eye
    lines.append(f"1. the eye fixture under /usr/bin/python3 from this tree: {eye['equal']}/{eye['rows']} byte-equal (module {eye['module']}) → {'PASS' if eye['pass'] else 'MISS'}")
    if not eye["pass"]:
        stop.append("the eye fixture")
    out["cpu_s"]["eye"] = time.process_time() - c
    # 2. the life unchanged
    c = time.process_time()
    s2 = gate_step2(root, eps, log)
    out["life"] = s2
    out["cpu_s"]["life"] = time.process_time() - c + float(s2.get("arms_cpu_s", 0.0))
    bad_c = [k for k, v in s2["caches"].items() if not v["same"]]
    bad_i = [k for k, v in s2["items"].items() if not v["same"]]
    lines.append(f"2. THE LIFE UNCHANGED: (a) {len(s2['caches']) - len(bad_c)}/{len(s2['caches'])} caches carry S1b-1's specs, canvas shas and glances "
                 f"(rows {sum(v['rows_new'] for v in s2['caches'].values())}); (b) {len(s2['items']) - len(bad_i)}/{len(s2['items'])} item and question sets equal S1b-1's"
                 + (f" — MISS {bad_c + bad_i}" if bad_c or bad_i else ""))
    if "why" in s2:
        lines.append(f"   (c) STOP: {s2['why']}")
    else:
        for ws, v in s2["bars"].items():
            lines.append(f"   (c) {ws}: S1b-1's six arms re-run here (S1b-1's roads, 10,000 scenes) vs S1b-1's marks.json at full precision: "
                         + " · ".join(f"{k} {'=' if v[k] else '≠'} ({_f(v['_values'][k][0])})" for k in STEP2_MARKS))
        rs = s2["report_bar_section"]
        lines.append(f"   (c) S1B1-REPORT-REGRADED.txt (sha {'as recorded' if s2['regraded_sha_ok'] else 'CHANGED'}): its bar section, {rs['n_lines']} lines, "
                     f"reproduced line for line: {rs['n_differ'] == 0}" + (f" — first differences {rs['differ']}" if rs["n_differ"] else "")
                     + f" · the 18 arms: {s2['arms_cpu_s']:.1f} CPU-s, {s2['arms_wall_s']:.1f} s wall")
    lines.append(f"   → {'PASS' if s2['pass'] else 'MISS'}")
    if not s2["pass"]:
        stop.append("the life unchanged (step 2)")
    # 3. the ear's types at 10,000 on seed 20261101
    c = time.process_time()
    ws0 = W.WORLD_SEEDS[0]
    trs = Things(C.ScenePercepts(C.cache_dir(root, ws0, "train")))
    Lx = make_learner("A-RW", Lr.LR_S1B1, eps)
    train_arm("A-RW", Lx, trs, trs.p.words, None, range(W.N_TRAIN), ws0, None)
    mature = Lx.mature_words()
    cover = Lx.ear.cover(mature)
    tc = types_check(cover, mature)
    counts = [int(sum(Lx.ear.alone.get(w, 0) for w in T)) for T in cover]
    out["types"] = {**tc, "alone_counts": counts, "young": [w for w in Lx.words if w not in mature]}
    out["cpu_s"]["types"] = time.process_time() - c
    lines.append(f"3. the ear's types at {W.N_TRAIN} on seed {ws0} (the greedy cover of the {len(mature)} mature words; young {out['types']['young']}): "
                 + " ".join("(" + " ".join(t) + ")" for t in cover) + f" · the world's three: {'EQUAL' if tc['pass'] else 'DIFFER'}"
                 + f" · one-word utterances per type {counts} → {'PASS' if tc['pass'] else 'MISS (an instrument fact: the types would decide it)'}")
    if not tc["pass"]:
        stop.append("the ear's types (step 3)")
    # 4. the READER toy, a positive control, and the pin
    c = time.process_time()
    toys = [reader_toy(s, eps) for s in READER_TOY_SEEDS]
    out["toy"] = toys
    tok = all(t["diag_refusal"] <= TOY_DIAG_MAX and t["reader_refusal"] >= TOY_READER_MIN for t in toys)
    pin = max(t["pin_weighted_vs_plain"] for t in toys)
    out["cpu_s"]["toy"] = time.process_time() - c
    lines.append(f"4. THE READER toy (ε {eps}; seeds {list(READER_TOY_SEEDS)}; {READER_TOY['n_test']} never-taught things a seed): "
                 + " · ".join(f"seed {t['seed']}: diagonal refusal {t['diag_refusal']:.3f} (≤ {TOY_DIAG_MAX}) · READER refusal {t['reader_refusal']:.3f} (≥ {TOY_READER_MIN})"
                              f" · the READER holds trained things {t['reader_holds_trained']:.3f} (printed)" for t in toys)
                 + f" · the pin (weighted = unweighted when every r = 1): max relative difference {pin:.1e} → {'PASS' if tok and pin < 1e-9 else 'MISS'}")
    if not (tok and pin < 1e-9):
        stop.append("the READER toy (step 4)")
    # 5. SPEAK2's pin on every NEED item
    c = time.process_time()
    pins = {str(ws): speak2_pin_rows(C.load_truth(C.cache_dir(root, ws, "speak2", R_TSET))) for ws in W.WORLD_SEEDS}
    out["speak2_pin"] = pins
    pok = all(v["n"] == W.split_size("speak2") and v["pass"] == v["n"] for v in pins.values())
    out["cpu_s"]["speak2_pin"] = time.process_time() - c
    lines.append("5. SPEAK2's pin (no single word unique; the kind's 2-word phrase unique; its other two not): "
                 + " · ".join(f"{ws} {v['pass']}/{v['n']} {v['kinds']}" for ws, v in pins.items()) + f" → {'PASS' if pok else 'MISS'}")
    if not pok:
        stop.append("SPEAK2's pin (step 5)")
    # 6. the 300-scene smoke of every arm on seed 20261101, its answer-kind tables read whole
    c = time.process_time()
    sm = gate_smoke_r(root, eps)
    out["smoke"] = sm
    out["cpu_s"]["smoke"] = time.process_time() - c
    lines.append(f"6. the {W.GATE_N}-scene smoke of every arm on seed {ws0} (the fresh items of test seed {W.FRESH_TEST_SEEDS[ws0]}), the answer-kind tables whole:")
    lines += ["   " + l for l in sm["lines"]]
    lines.append(f"   → {'PASS' if sm['pass'] else 'MISS'}" + ("" if sm["pass"] else f" ({sm['why']})"))
    if not sm["pass"]:
        stop.append("the smoke's wiring pin (step 6)")
    out["verdict"] = "STOP" if stop else "PROCEED"
    out["stop_reasons"] = stop
    out["lr"], out["eps"] = Lr.LR_S1B1, eps
    out["wall_s"] = time.perf_counter() - t0
    out["cpu_s"]["in_process"] = time.process_time() - c0
    out["cpu_s"]["total"] = out["cpu_s"]["in_process"] + float(s2.get("arms_cpu_s", 0.0))
    lines.append(f"GATE: {out['verdict']}" + (f" — {'; '.join(stop)}" if stop else "")
                 + f" · {out['wall_s']:.0f} s wall · {out['cpu_s']['total']:.0f} CPU-s (the 18 re-run arms included)")
    for l in lines:
        log(l)
    out["lines"] = lines
    dump(Path(root) / "gate" / "gate.json", out)
    (Path(root) / "gate" / "gate.txt").write_text("\n".join(lines) + "\n")
    return out


def gate_smoke_r(root: Path, eps: float) -> Dict[str, object]:
    """§4 step 6: every arm trained on the first 300 scenes of seed 20261101 and answering the FRESH items; per arm × road
    the answer-kind tables — M2b's emitted shape words, the mouth's phrase lengths and decline reasons (SPEAK, SPEAK2,
    DECLINE), READ-BACK over every spoken phrase (the wiring pin: 1.000 wherever something was spoken, and the law must
    speak), the types and the one-alone type with its count; the null's first draw at 300 (M1 / M3)."""
    ws0 = W.WORLD_SEEDS[0]
    build_questions_r(root, ws0)
    sm_dir = Path(root) / "gate" / "smoke"
    ctx = _RCtx(root, ws0)
    lines: List[str] = []
    ok, why = True, []
    table: Dict[str, object] = {}
    for arm in R_ARMS:
        rec = run_arm_r(arm, root, ws0, n_train=W.GATE_N, reading_points=(W.GATE_N,), eps=eps, out=sm_dir / arm, log=lambda s: None)
        A = json.loads((sm_dir / arm / f"answers_{W.GATE_N:05d}.json").read_text())
        g = grade_answers_r(ctx, arm, A)
        rr = rec["reading_points"][str(W.GATE_N)]["reader"]
        one = rr.get("one_alone")
        lines.append(f"{arm}: types " + " ".join("(" + " ".join(t) + ")" for t in rr["types"]) + " · the one-alone type "
                     + (("(" + " ".join(rr["types"][one]) + ")") if one is not None else "none") + f" (counts {rr['alone_counts']})"
                     + f" · M1 {_f(g['M1']['graded']['covered'])} · M3 {_f(g['M3']['all']['covered'])} · cpu {rec['cpu_s']:.1f} s")
        table[arm] = {}
        for road in [n for n in ("LAW",) + R_READINGS if n in g["roads"]]:
            gr = g["roads"][road]
            mo, m2b = gr["MOUTH"], gr["M2b"]["graded"]
            rb, n_rb = mo["readback_all"], mo["n_readback_all"]
            rbd = gr.get("readback_decline")
            lines.append(f"   {road:<11} M2b shape words emitted {m2b['shape_words_emitted']} (correct {_f(m2b['correct'])}; idk {_f(m2b['idk'])})"
                         f" · lengths SPEAK {_d(mo['length_mix_speak'])} SPEAK2 {_d(mo['length_mix_speak2'])}"
                         f" · reasons SPEAK {(mo['speak'] or {}).get('reasons')} SPEAK2 {mo['reasons2']} DECLINE {gr['DECLINE']['reasons']}"
                         f" · READ-BACK {_f(rb)} on {n_rb} spoken (DECLINE {_f(rbd)})")
            table[arm][road] = {"readback": rb, "n": n_rb, "readback_decline": rbd, "shape_words": m2b["shape_words_emitted"],
                                "lengths": mo["length_mix"], "reasons": [(mo["speak"] or {}).get("reasons"), mo["reasons2"], gr["DECLINE"]["reasons"]]}
            if (rb is not None and rb != 1.0) or (rbd is not None and rbd != 1.0):
                ok = False
                why.append(f"{arm}/{road} READ-BACK {rb} / {rbd}")
        if arm == "A-RW-R" and not table[arm]["LAW"]["n"]:
            ok = False
            why.append("A-RW-R's law spoke nothing: the pin would be vacuous")
    nr = run_null(root, ws0, 1, n_train=W.GATE_N, out=sm_dir / "null-01.json")
    lines.append(f"N-SHUF (k = 1, key null:{ws0}:1) at {W.GATE_N}: M1 {_f(nr['m1'])} (chance {_f(nr['chance_m1'])}) · M3 {_f(nr['m3'])} (chance {_f(nr['chance_m3'])}) · cpu {nr['cpu_s']:.1f} s")
    return {"lines": lines, "pass": ok, "why": "; ".join(why), "table": table, "null": nr}


# ------------------------------------------------------------------------------------------------ the price (S1b-1R)
def price_r(root: Path, log=print) -> Dict[str, object]:
    """SOLO, one process at a time, on seed 20261101: each of the four arms over its whole 10,000-scene stream with every
    reading point (A-RW-R with its five readings at the last), then one null draw (k = 1) — nothing extrapolated in length.
    Projected to the unit: four arms × three seeds + (K + 1) draws × three seeds. The caches' and the gate's measured CPU
    beside, and §7's declaration (≤ 25 CPU-min: the arms, the READER, the nulls, the fresh caches)."""
    g = gate_or_chosen_r(root)
    eps = g["eps"]
    ws0 = W.WORLD_SEEDS[0]
    tmp = Path(root) / "price" / "solo"
    cwd = str(Path(__file__).resolve().parents[2])
    base = [sys.executable, "-B", "-m", "brain.scene.run"]
    solo: Dict[str, Dict[str, object]] = {}
    for arm in R_ARMS:
        o = tmp / arm
        w = time.perf_counter()
        r = _spawn_wait([(arm, base + ["arm-r", "--root", str(root), "--arm", arm, "--world-seed", str(ws0), "--out", str(o),
                                       "--eps", repr(float(eps))], tmp / "logs" / f"{arm}.log")], cwd)[0]
        rec = json.loads((o / "record.json").read_text()) if r["rc"] == 0 else {}
        solo[arm] = {"rc": r["rc"], "cpu_s": rec.get("cpu_s"), "wall_s": time.perf_counter() - w}
    w = time.perf_counter()
    r = _spawn_wait([("null", base + ["null-r", "--root", str(root), "--world-seed", str(ws0), "--ks", "1", "--out",
                                      str(tmp / "null-01.json")], tmp / "logs" / "null.log")], cwd)[0]
    nrec = json.loads((tmp / "null-01.json").read_text()) if r["rc"] == 0 else {}
    solo["null"] = {"rc": r["rc"], "cpu_s": nrec.get("cpu_s"), "wall_s": time.perf_counter() - w}
    if any(v["rc"] != 0 for v in solo.values()):
        raise RunError(f"a priced run failed: {solo}")
    arms_cpu = 3 * sum(solo[a]["cpu_s"] for a in R_ARMS)
    nulls_cpu = 3 * (NULL_K + 1) * solo["null"]["cpu_s"]
    unit = arms_cpu + nulls_cpu
    cache_rec = json.loads((Path(root) / "logs" / "cache-r.json").read_text()) if (Path(root) / "logs" / "cache-r.json").exists() else {}
    caches = float(cache_rec.get("cpu_s_total", 0.0))
    fresh_caches = float(sum(v["cpu_s"] for k, v in cache_rec.items() if isinstance(v, dict) and k.endswith("/fresh")))
    gate_cpu = float(g.get("cpu_s", {}).get("total", 0.0))
    price_cpu = float(sum(v["cpu_s"] for v in solo.values()))
    declared = unit + caches
    lines = [f"== PRICE (solo, one process at a time, seed {ws0}, the whole {W.N_TRAIN}-scene stream; nothing extrapolated in length) ==",
             " · ".join(f"{a} cpu {solo[a]['cpu_s']:.1f} s wall {solo[a]['wall_s']:.1f} s" for a in R_ARMS)
             + f" · one null draw (k = 1: train to {W.N_TRAIN}, M1 + M3) cpu {solo['null']['cpu_s']:.1f} s",
             f"the unit: 4 arms × 3 seeds ≈ {arms_cpu:.0f} CPU-s + {NULL_K + 1} null draws × 3 seeds ≈ {nulls_cpu:.0f} CPU-s → ≈ {unit / 60:.1f} CPU-min",
             f"§7's declaration (the arms, the READER, the nulls, the fresh caches) ≤ 25 CPU-min: the unit ≈ {unit / 60:.1f} + the caches as drawn "
             f"{caches / 60:.1f} (train × 3, S1b-1's test sets, the fresh sets {fresh_caches:.0f} CPU-s, the toy) ≈ {declared / 60:.1f} CPU-min → "
             + ("within" if declared <= 25 * 60 else "OVER"),
             f"beside the declaration: THE FIRST GATE {gate_cpu / 60:.1f} CPU-min (S1b-1's 18 arms re-run included) · this price {price_cpu / 60:.1f} CPU-min"
             f" → the slice in all ≈ {(declared + gate_cpu + price_cpu) / 60:.1f} CPU-min"]
    out = {"solo": solo, "unit_cpu_s": unit, "arms_cpu_s": arms_cpu, "nulls_cpu_s": nulls_cpu, "caches_cpu_s": caches,
           "gate_cpu_s": gate_cpu, "price_cpu_s": price_cpu, "declared_cpu_s": declared, "lines": lines, "eps": eps}
    for l in lines:
        log(l)
    dump(Path(root) / "price" / "price.json", out)
    (Path(root) / "price" / "price.txt").write_text("\n".join(lines) + "\n")
    return out


def run_nulls(root: Path, ws: int, ks: Sequence[int], n_train: int = W.N_TRAIN, out: Optional[Path] = None, log=print) -> None:
    for k in ks:
        rec = run_null(root, ws, k, n_train=n_train, out=out if (out is not None and len(ks) == 1) else None)
        log(f"[null {ws} k={k}] M1 {_f(rec['m1'])} · M3 {_f(rec['m3'])} · cpu {rec['cpu_s']:.1f} s")


def _ks(spec: str) -> List[int]:
    out: List[int] = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


# ------------------------------------------------------------------------------------------------ CLI
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="brain.scene.run")
    ap.add_argument("cmd", choices=["cache", "cache-world", "cache-all", "questions", "stage", "first-gate", "arm", "grade",
                                    "report", "price", "cache-r", "questions-r", "arm-r", "null-r", "grade-r", "report-r",
                                    "first-gate-r", "price-r"])
    ap.add_argument("--split")
    ap.add_argument("--world-seed", type=int)
    ap.add_argument("--arm")
    ap.add_argument("--n", type=int, default=W.N_TRAIN)
    ap.add_argument("--rps", default=",".join(map(str, W.READING_POINTS)))
    ap.add_argument("--out")
    ap.add_argument("--root", default=str(C.RUNS))
    ap.add_argument("--lr", type=float)                  # S1b-1R gate step 2: S1b-1's arms before any gate record exists
    ap.add_argument("--eps", type=float)
    ap.add_argument("--ks", default="0-%d" % NULL_K)     # S1b-1R: the null draws (k = 0 is S1b-1's own)
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
    elif a.cmd == "cache-all":
        cache_all(root, log=log)
    elif a.cmd == "first-gate":
        g = first_gate(root, log=log)
        return 0 if g["verdict"] == "PROCEED" else 3
    elif a.cmd == "arm":
        rps = [int(x) for x in a.rps.split(",") if x]
        run_arm(a.arm, root, a.world_seed, n_train=a.n, reading_points=rps, lr=a.lr, eps=a.eps,
                out=Path(a.out) if a.out else None, log=log)
    elif a.cmd == "grade":
        mk = grade_seed(root, a.world_seed, log=log)
        print_seed_table(mk, log=log)
    elif a.cmd == "report":
        report(root, log=log)
    elif a.cmd == "price":
        price(root, n=a.n if a.n != W.N_TRAIN else 2000, log=log)
    elif a.cmd == "cache-r":
        cache_r(root, log=log)
    elif a.cmd == "questions-r":
        log(f"[questions-r {a.world_seed}] {build_questions_r(root, a.world_seed)}")
    elif a.cmd == "arm-r":
        rps = [int(x) for x in a.rps.split(",") if x]
        run_arm_r(a.arm, root, a.world_seed, n_train=a.n, reading_points=rps, eps=a.eps,
                  out=Path(a.out) if a.out else None, log=log)
    elif a.cmd == "null-r":
        run_nulls(root, a.world_seed, _ks(a.ks), n_train=a.n, out=Path(a.out) if a.out else None, log=log)
    elif a.cmd == "grade-r":
        mk = grade_seed_r(root, a.world_seed, log=log)
        print_seed_table_r(mk, log=log)
    elif a.cmd == "report-r":
        report_r(root, log=log)
    elif a.cmd == "first-gate-r":
        g = first_gate_r(root, log=log)
        return 0 if g["verdict"] == "PROCEED" else 3
    elif a.cmd == "price-r":
        price_r(root, log=log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
