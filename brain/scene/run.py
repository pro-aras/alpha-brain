"""run.py — S1a's runner (PREREG-R3-TONIGHT §S1a): the caches, stage −1, the toy, THE FIRST GATE, the prices, the full
run's arms and the grader. Everything runs under /usr/bin/python3 (the eye's interpreter; no arm needs torch).

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:20 +0400 — new module.

  python3 -m brain.scene.run cache --split S [--world-seed W]     one cache (written once)
  python3 -m brain.scene.run cache-world --world-seed W           train + test + m2b + m6 and the disjointness record
  python3 -m brain.scene.run questions --world-seed W             the questions (what an arm hears) and the keys (grader)
  python3 -m brain.scene.run stage                                stage −1's organ facts (printed only)
  python3 -m brain.scene.run first-gate                           the toy, ε, the instrument verdict, 5 arms × 300 vs N-SHUF
  python3 -m brain.scene.run arm --arm A --world-seed W           one arm over its stream, answering at every reading point
  python3 -m brain.scene.run grade --world-seed W                 the marks of every arm at every reading point
  python3 -m brain.scene.run report                               the headline table across seeds, the bars, the verdicts
  python3 -m brain.scene.run price                                solo, then the launch's shape (5 arms × 3 seeds at once)

Only this module and marks.py read the truth. The truth enters an ORACLE arm's feed here, as an index (the referent's
thing hypothesis, or the referent thing for ORACLE-TRUTH), and A-RW / N-SHUF never have it read on their behalf.
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

from . import PREREG_SHA256
from . import cache as C
from . import learners as Lr
from . import marks as M
from . import world as W

ARMS: Tuple[str, ...] = ("A-RW", "N-SHUF", "P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH")
RW_ARMS = ("A-RW", "N-SHUF", "P-ORACLE-RW")
LDA_ARMS = ("P-ORACLE", "ORACLE-TRUTH")
PREREG_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/r3/PREREG-R3-TONIGHT.md")
TYPE_WORDS = {"shape": list(W.SHAPES), "colour": list(W.COLOUR_NAMES), "size": list(W.SIZE_NAMES)}


class RunError(Exception):
    pass


# ------------------------------------------------------------------------------------------------ plumbing
def check_prereg() -> str:
    got = hashlib.sha256(PREREG_PATH.read_bytes()).hexdigest()
    if got != PREREG_SHA256:
        raise RunError(f"PREREG sha256 {got} ≠ the signed {PREREG_SHA256} — STOP and hand back")
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
    if arm in RW_ARMS:
        return Lr.RWLearner(lr=lr, oracle=(arm == "P-ORACLE-RW"))
    if arm in LDA_ARMS:
        return Lr.LDAReader(eps)
    raise RunError(f"no such arm: {arm!r}")


def train_arm(arm: str, learner, things: Things, words_of, truth: Optional[Sequence[Dict[str, object]]],
              rows: Sequence[int], seed: int, seen: Optional[list] = None) -> None:
    """Feed `rows` of a training split to one arm. `words_of(row)` = what the parent said with that scene (N-SHUF: the
    permuted utterance). `truth` is passed ONLY for the oracle arms (their referent index)."""
    for i in rows:
        X = things.for_arm(arm, i)
        words = words_of(i)
        ref = referent_index(arm, things, truth[i]) if arm in ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH") else None
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
    truth = C.load_truth(C.cache_dir(root, ws, "train")) if arm in ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH") else None
    if arm == "N-SHUF":
        perm = Lr.nshuf_permutation(substream(ws, "n-shuf-permutation"), len(train.p))
        words_of = lambda i: train.p.words(int(perm[i]))
    else:
        words_of = lambda i: train.p.words(i)
    learner = make_learner(arm, lr, eps)
    seen: list = []
    done = 0
    record = {"arm": arm, "world_seed": ws, "lr": lr, "eps": eps, "n_train": n_train, "prereg_sha256": PREREG_SHA256,
              "code": code_identity(), "reading_points": {}}
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
    out = {"prereg_sha256": PREREG_SHA256, "world_seed": ws, "arms": {}}
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
                ok = [nm[t] == it[t] for nm, it in zip(rows, items["NAME"]) if nm is not None]
                names[t] = {"acc": (sum(ok) / len(ok) if ok else None), "n": len(ok)}
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


def bars_for(marks: Dict[str, object], rp: str = str(W.N_TRAIN)) -> Dict[str, object]:
    """The PREREG's bars at 10,000 scenes for one seed, P-ORACLE's reading beside every mark."""
    A = {a: marks["arms"][a]["rp"].get(rp) for a in marks["arms"]}
    r = {}
    m1 = A["A-RW"]["M1"]["all"]
    po_rw = A["P-ORACLE-RW"]["M1"]["all"]["covered"]
    po = A["P-ORACLE"]["M1"]["all"]["covered"]
    ns = A["N-SHUF"]["M1"]["all"]
    r["M1"] = {"value": m1["covered"], "n": m1["n_covered"], "all": m1["all"], "n_all": m1["n_all"],
               "coverage": m1["coverage"], "p_oracle": po, "p_oracle_rw": po_rw,
               "bar_rw": M.BARS["M1_vs_PORACLE_RW"] * po_rw, "bar_lda": M.BARS["M1_vs_PORACLE"] * po,
               "pass": (m1["covered"] >= M.BARS["M1_vs_PORACLE_RW"] * po_rw and m1["covered"] >= M.BARS["M1_vs_PORACLE"] * po)}
    m2a = A["A-RW"]["M2a"]["all"]
    fr = A["A-RW"]["M1"]["all"]["false_refusal"]
    po2 = A["P-ORACLE"]["M2a"]["all"]["refusal"]
    po_fr = A["P-ORACLE"]["M1"]["all"]["false_refusal"]
    ok2 = m2a["refusal"] >= M.BARS["M2a_refusal"] and fr <= M.BARS["M2a_false_refusal"]
    ceil2 = po2 < M.BARS["M2a_refusal"] or po_fr > M.BARS["M2a_false_refusal"]
    r["M2a"] = {"value": m2a["refusal"], "n": m2a["n"], "false_refusal": fr, "p_oracle": po2, "p_oracle_fr": po_fr,
                "pass": ok2, "ceiling_bound": (not ok2) and ceil2}
    m2b = A["A-RW"]["M2b"]["graded"]
    po3 = A["P-ORACLE"]["M2b"]["graded"]["correct"]
    ok3 = m2b["correct"] >= M.BARS["M2b"]
    r["M2b"] = {"value": m2b["correct"], "n": m2b["n"], "p_oracle": po3, "pass": ok3,
                "ceiling_bound": (not ok3) and po3 < M.BARS["M2b"],
                "diamond": A["A-RW"]["M2b"]["diamond"]["correct"], "diamond_p_oracle": A["P-ORACLE"]["M2b"]["diamond"]["correct"]}
    m6 = A["A-RW"]["M6"]["all"]
    po6 = A["P-ORACLE"]["M6"]["all"]["covered"]
    ok6 = m6["covered"] >= M.BARS["M6"]
    r["M6"] = {"value": m6["covered"], "n": m6["n_covered"], "all": m6["all"], "n_all": m6["n_all"], "p_oracle": po6,
               "chance": m6["chance_covered"], "pass": ok6, "ceiling_bound": (not ok6) and po6 < M.BARS["M6"]}
    r["N-SHUF"] = {"value": ns["covered"], "chance": ns["chance_covered"],
                   "bar": ns["chance_covered"] + M.BARS["NSHUF_over_chance"],
                   "pass": ns["covered"] <= ns["chance_covered"] + M.BARS["NSHUF_over_chance"]}
    for k in ("M1", "M2a", "M2b", "M6"):
        n = r[k]["n"]
        r[k]["underpowered"] = n < M.UNDERPOWERED_N
    r["T1_refuted"] = m1["covered"] < M.T1_REFUTE * po_rw
    r["one_meeting_refuted"] = (m6["covered"] < M.M6_REFUTE) and r["M1"]["pass"]
    return r


def print_seed_table(marks: Dict[str, object], log=print) -> List[str]:
    ws = marks["world_seed"]
    lines = [f"== S1a marks · world seed {ws} (test seed {W.TEST_SEEDS[ws]}) =="]
    rps = sorted(int(k) for k in marks["arms"]["A-RW"]["rp"])
    lines.append("M1 (covered) by reading point:")
    lines.append("   arm            " + " ".join(f"{rp:>7d}" for rp in rps))
    for arm in ARMS:
        vals = [marks["arms"][arm]["rp"][str(rp)]["M1"]["all"]["covered"] for rp in rps]
        lines.append(f"   {arm:<14} " + " ".join(f"{_f(v):>7}" for v in vals))
    top = str(max(rps))
    lines.append(f"At {top} scenes — M1 by scene size / word type (covered · all · coverage · chance · n covered):")
    for key in ["all", "size1", "size2", "size3", "type:colour", "type:shape", "type:size", "type:none",
                "tpl:T1", "tpl:T2", "tpl:T3", "tpl:T4"]:
        cells = []
        for arm in ARMS:
            b = marks["arms"][arm]["rp"][top]["M1"].get(key)
            if b is None:
                cells.append(f"{arm}: —")
                continue
            cells.append(f"{arm} {_f(b['covered'])}·{_f(b['all'])}")
        b0 = marks["arms"]["A-RW"]["rp"][top]["M1"].get(key) or {}
        lines.append(f"   {key:<12} cov {_f(b0.get('coverage'))} chance {_f(b0.get('chance_covered'))} n {b0.get('n_covered')}/{b0.get('n_all')} | " + " | ".join(cells))
    for arm in ARMS:
        R = marks["arms"][arm]["rp"][top]
        m2a, m2b, m6 = R["M2a"]["all"], R["M2b"], R["M6"]["all"]
        nm = R["NAME"]
        lines.append(f"   {arm:<14} M2a refusal {_f(m2a['refusal'])} (n {m2a['n']}) · false refusal on M1 covered "
                     f"{_f(R['M1']['all']['false_refusal'])} · M2b {_f(m2b['graded']['correct'])} (n {m2b['graded']['n']}; "
                     f"«I don't know» {_f(m2b['graded']['idk'])}; diamond {_f(m2b['diamond']['correct'])}) · M6 covered "
                     f"{_f(m6['covered'])} all {_f(m6['all'])} (n {m6['n_covered']}/{m6['n_all']}, chance {_f(m6['chance_covered'])}) "
                     f"· NAME shape {_f(nm['shape']['acc'])} colour {_f(nm['colour']['acc'])} size {_f(nm['size']['acc'])}")
    for s in W.M2B_SHAPES:
        lines.append(f"   M2b {s:<6} " + " ".join(f"{arm} {_f(marks['arms'][arm]['rp'][top]['M2b'][f'shape:{s}']['correct'])}" for arm in ARMS)
                     + f" · A-RW emitted {marks['arms']['A-RW']['rp'][top]['M2b'][f'shape:{s}']['shape_words_emitted']}")
    for n in (2, 3):
        lines.append(f"   M6 size{n}: " + " ".join(f"{arm} {_f(marks['arms'][arm]['rp'][top]['M6'][f'size{n}']['covered'])}" for arm in ARMS)
                     + f" · chance {_f(marks['arms']['A-RW']['rp'][top]['M6'][f'size{n}']['chance_covered'])}")
    gap = []
    for key in ("all", "size1", "size2", "size3"):
        a = marks["arms"]["ORACLE-TRUTH"]["rp"][top]["M1"][key]["covered"]
        b = marks["arms"]["P-ORACLE"]["rp"][top]["M1"][key]["covered"]
        gap.append(f"{key} {_f(None if a is None or b is None else a - b)}")
    lines.append("   the gaze's cost ORACLE-TRUTH − P-ORACLE on M1 (covered): " + " · ".join(gap))
    for l in lines:
        log(l)
    return lines


def report(root: Path, log=print) -> Dict[str, object]:
    out = {"prereg_sha256": PREREG_SHA256, "seeds": {}}
    lines: List[str] = []
    for ws in W.WORLD_SEEDS:
        mk = json.loads((seed_root(root, ws) / "marks.json").read_text())
        lines += print_seed_table(mk, log=lambda s: None)
        out["seeds"][str(ws)] = bars_for(mk)
    lines.append("== S1a BARS at 10,000 scenes (A-RW; P-ORACLE's reading beside every mark) ==")
    lines.append("seed      M1 covered (all)   [bar vs P-ORACLE-RW · vs P-ORACLE]     M2a refusal / false   M2b            M6 covered (all)      N-SHUF (≤ chance+0.05)")
    for ws in W.WORLD_SEEDS:
        b = out["seeds"][str(ws)]
        lines.append(
            f"{ws}  {_f(b['M1']['value'])} ({_f(b['M1']['all'])}) [{_f(b['M1']['bar_rw'])} · {_f(b['M1']['bar_lda'])}] "
            f"P-OR {_f(b['M1']['p_oracle'])} P-OR-RW {_f(b['M1']['p_oracle_rw'])} {'PASS' if b['M1']['pass'] else 'FAIL'}   "
            f"{_f(b['M2a']['value'])} / {_f(b['M2a']['false_refusal'])} P-OR {_f(b['M2a']['p_oracle'])} "
            f"{'PASS' if b['M2a']['pass'] else ('CEILING-BOUND' if b['M2a']['ceiling_bound'] else 'FAIL')}   "
            f"{_f(b['M2b']['value'])} P-OR {_f(b['M2b']['p_oracle'])} {'PASS' if b['M2b']['pass'] else ('CEILING-BOUND' if b['M2b']['ceiling_bound'] else 'FAIL')}   "
            f"{_f(b['M6']['value'])} ({_f(b['M6']['all'])}) P-OR {_f(b['M6']['p_oracle'])} "
            f"{'PASS' if b['M6']['pass'] else ('CEILING-BOUND' if b['M6']['ceiling_bound'] else 'FAIL')}   "
            f"{_f(b['N-SHUF']['value'])} ≤ {_f(b['N-SHUF']['bar'])} {'PASS' if b['N-SHUF']['pass'] else 'FAIL'}")
        und = [k for k in ("M1", "M2a", "M2b", "M6") if b[k]["underpowered"]]
        if und:
            lines.append(f"          UNDERPOWERED (n < 30): {', '.join(und)}")
    allpass = {k: all(out['seeds'][str(ws)][k]['pass'] for ws in W.WORLD_SEEDS) for k in ("M1", "M2a", "M2b", "M6", "N-SHUF")}
    lines.append("every bar at all 3 seeds: " + " · ".join(f"{k} {'PASS' if v else 'no'}" for k, v in allpass.items())
                 + f" → S1a {'PASSES' if all(allpass.values()) else 'does not pass'}")
    lines.append("refutations: T1 (A-RW M1 < 0.6 × P-ORACLE-RW) " + " ".join(
        f"{ws}:{'REFUTED' if out['seeds'][str(ws)]['T1_refuted'] else 'no'}" for ws in W.WORLD_SEEDS)
        + " · one-meeting (M6 < 0.5 while M1 passes) " + " ".join(
        f"{ws}:{'REFUTED' if out['seeds'][str(ws)]['one_meeting_refuted'] else 'no'}" for ws in W.WORLD_SEEDS))
    out["all_pass"] = allpass
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
    out: Dict[str, object] = {"prereg_sha256": PREREG_SHA256, "code": code_identity()}
    lines = ["== THE FIRST GATE (PREREG-R3-TONIGHT §S1a) =="]
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
        R = Lr.LDAReader(eps)
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
        R = Lr.LDAReader(eps)
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
    # --- 3. five arms × 300 scenes vs N-SHUF on M1 (seed 1's test items)
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
        train_arm(arm, L, trs, words_of, trs_truth if arm in ("P-ORACLE-RW", "P-ORACLE", "ORACLE-TRUTH") else None,
                  gate_rows, ws, seen)
        prepare(arm, L, seen)
        ans = answer_all(arm, L, {"M1": Q["questions"]["M1"]}, {"test": tt}, Q["test_seed"])
        g = M.grade_pointing(K["items"]["M1"], ans, t_truth, tt.members, "truth" if arm == "ORACLE-TRUTH" else "gaze")
        arms[arm] = M.summarise_pointing(g)["all"]
    beat = {a: arms[a]["covered"] > arms["N-SHUF"]["covered"] for a in ARMS if a != "N-SHUF"}
    out["arms300"] = arms
    out["beat_nshuf"] = beat
    lines.append(f"3. FIVE ARMS × {W.GATE_N} scenes of seed {ws}, M1 on its {arms['A-RW']['n_all']} test items "
                 f"(covered {arms['A-RW']['n_covered']}; chance covered {_f(arms['A-RW']['chance_covered'])}):")
    for a in ARMS:
        lines.append(f"   {a:<14} M1 covered {_f(arms[a]['covered'])} · all {_f(arms[a]['all'])}"
                     + ("" if a == "N-SHUF" else f" · beats N-SHUF: {'yes' if beat[a] else 'NO'}"))
    lines.append(f"   (the brief's step 6 asked for ORACLE-TRUTH < 0.95 → STOP; the signed PREREG's STOP is the instrument "
                 f"verdict. ORACLE-TRUTH reads {_f(arms['ORACLE-TRUTH']['covered'])} here.)")
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
    """Solo (A-RW, seed 1), then the launch's shape (5 arms × 3 seeds at once, nice 19), each over the first `n` scenes
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
             f"launch shape 5 arms × 3 seeds at once: cpu {cpu_shape:.1f} s total (per process "
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
