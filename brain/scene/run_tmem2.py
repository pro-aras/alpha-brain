"""run_tmem2.py — T-MEM-2 «METACOGNITION DECIDES» (PREREG-TMEM2, final 4d03f79, sha b785b54f…; CONCLUSION-MEMORY §4): the
HEALTH lives, their identity with S1b-1R's own record, the four HEALTH roads, the graders, the bars, THE FIRST GATE, the
price and the report. Everything runs under /usr/bin/python3 (the eye's interpreter, as S1a / S1b-1 / S1b-1R).

edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:36 +0400 — new module.
edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:18 +0400 — PREREG-TMEM2 AMENDMENT 1 (final a7dceea, sha 6da8ff67…): both rows
graded through the rule (health.grades; the truth-fed row at the referent's hypothesis — one difference, the hypothesis); the
two readings beside it, offline (the metacognition-of-perception reading and the false-unseen rate); step 3 read after the
rule; step 5's price a STOP when OVER; the amendment's sha checked with the law's.

  python3 -m brain.scene.run_tmem2 first-gate              THE FIRST GATE (§7): 3 lives solo, the toy, agreement, the smoke, the price
  python3 -m brain.scene.run_tmem2 life --world-seed W     one HEALTH life; its identity checked at the end (exit 3 on a miss)
  python3 -m brain.scene.run_tmem2 grade --world-seed W    one seed's marks
  python3 -m brain.scene.run_tmem2 report                  the bars across the seeds, the report

S1b-1R's run root is READ (its caches, its fresh questions and keys, its A-RW-R record — the CONTROL and the identity's
reference), never written; this slice writes only under /data/dev/brain-runs/scene-tmem2/. Only this module and marks.py
read the world's truth: the train truth for the row's offline ceiling (the scene's referent), the fresh keys for the
graders, the oracle's per-word accuracies and the NAME things' verdicts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.harness.bars import binomial_half_width_95
from brain.world.seeds import substream

from . import cache as C
from . import health as H
from . import learners as Lr
from . import marks as M
from . import run as R
from . import world as W

TMEM2_ROOT = Path("/data/dev/brain-runs/scene-tmem2")
S1B1R_ROOT = C.RUNS                                  # /data/dev/brain-runs/scene-s1b1r — READ, never written
PREREG_TMEM2_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/memory/PREREG-TMEM2.md")
PREREG_TMEM2_SHA256 = "b785b54f97c6c2bc300ce07cdc26aaa716bf9c7fcb3e7cc183294480b5fd2914"
PREREG_TMEM2_AMEND1_PATH = Path("/data/dev/genome-wt-brain3/docs/brain/memory/PREREG-TMEM2-AMEND-1.md")
PREREG_TMEM2_AMEND1_SHA256 = "6da8ff679a317166c7a4e82bf9efd183785b5ecb90ad1bcb6fbae90d241386e6"   # final, a7dceea
S1B1R_REPORT_SHA256 = "b695ae5c94d13a85a3d05a1b58f553306f776726e2e66fd042b7302741a219a3"
HEALTH_ROADS: Tuple[str, ...] = ("HEALTH-MOUTH", "HEALTH-ORACLE", "HEALTH-TRUTHFED", "NULL")
GRADED_ROADS: Tuple[str, ...] = ("CONTROL",) + HEALTH_ROADS
TRAINED: Tuple[str, ...] = tuple(sorted(W.SHAPES + W.COLOUR_NAMES + W.SIZE_NAMES))   # the 13 trained words
B1_TRUTH, B1_SPOKEN = 0.90, 0.80
B2_ER, B2_TR, B2_CEIL = 0.70, 0.90, 0.30
B3_ECE, B4_AUROC = 0.10, 0.70
POWER_N = 30
STEP3_TOL = 0.10                                     # the ruling on step 3: a reversal of MORE than 0.10 is the fault
PRICE_CPU_S = 300.0                                  # ≤ 5 CPU-min declared; AMENDMENT 1 §4: OVER is a STOP
RESIDUAL_NEAR = 0.05                                 # AMENDMENT 1 §3: the residual predicted within 0.05 on most words (a reading)


class TMem2Error(Exception):
    pass


def check_prereg_tmem2() -> str:
    """S1b-1R's own check (S1a / S1b-1 / S1b-1R texts), this law's sha and its AMENDMENT 1's — at every run command."""
    R.check_prereg()
    got = hashlib.sha256(Path(PREREG_TMEM2_PATH).read_bytes()).hexdigest()
    if got != PREREG_TMEM2_SHA256:
        raise TMem2Error(f"PREREG-TMEM2 sha256 {got} ≠ the final {PREREG_TMEM2_SHA256} — STOP and hand back")
    am = hashlib.sha256(Path(PREREG_TMEM2_AMEND1_PATH).read_bytes()).hexdigest()
    if am != PREREG_TMEM2_AMEND1_SHA256:
        raise TMem2Error(f"PREREG-TMEM2-AMEND-1 sha256 {am} ≠ the final {PREREG_TMEM2_AMEND1_SHA256} — STOP and hand back")
    return got


def price_verdict(unit_cpu_s: float) -> Dict[str, bool]:
    """THE FIRST GATE step 5 (AMENDMENT 1 §4): the unit's price solo against the declared ≤ 5 CPU-min — OVER is a STOP."""
    within = float(unit_cpu_s) <= PRICE_CPU_S
    return {"within": within, "stop": not within}


def toy_passes(t: Dict[str, object]) -> bool:
    """THE FIRST GATE step 2: A kept, B refused, the null flips them, an ungraded claim moves nothing — and (AMENDMENT 1) a
    claim set aside «unseen» moves nothing but its count."""
    return (t["keeps"] == {"A": True, "B": False} and t["null"] == {"A": False, "B": True}
            and bool(t["ungraded_moves_nothing"]) and bool(t.get("unseen_moves_nothing", False)))


def perception_rates(p: Dict[str, Dict[str, int]]) -> Dict[str, Optional[float]]:
    """AMENDMENT 1 §3, offline: THE METACOGNITION-OF-PERCEPTION READING (of the gradable claims whose referent the gaze never
    saw, the fraction set aside «unseen») and, beside it, Fable's FALSE-UNSEEN RATE (of those whose referent it DID see, the
    fraction set aside) — per claim, and per scene (every gradable claim of the scene set aside) beside."""
    def r(a: int, b: int) -> Optional[float]:
        return (a / b) if b else None
    u, s = p["unseen"], p["seen"]
    return {"metacognition": r(u["set_aside"], u["gradable"]), "false_unseen": r(s["set_aside"], s["gradable"]),
            "metacognition_scenes": r(u["scenes_set_aside"], u["scenes"]),
            "false_unseen_scenes": r(s["scenes_set_aside"], s["scenes"])}


def perception_line(ws, p: Dict[str, Dict[str, int]]) -> str:
    q = perception_rates(p)
    u, s = p["unseen"], p["seen"]
    return (f"{ws}: the metacognition-of-perception reading (the referent never seen): claims set aside {u['set_aside']} / "
            f"{u['gradable']} = {_f(q['metacognition'])} (scenes {u['scenes_set_aside']} / {u['scenes']} = {_f(q['metacognition_scenes'])})"
            f" · the false-unseen rate (the referent seen): {s['set_aside']} / {s['gradable']} = {_f(q['false_unseen'])} "
            f"(scenes {s['scenes_set_aside']} / {s['scenes']} = {_f(q['false_unseen_scenes'])}; predicted 0.05–0.08)")


def check_control(root_in: Path) -> Dict[str, object]:
    """The CONTROL's record is S1b-1R's: its report.txt must carry the recorded sha (§1)."""
    p = Path(root_in) / "report.txt"
    got = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    return {"report": str(p), "sha": got, "ok": got == S1B1R_REPORT_SHA256}


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------------------------------------ the identity (§1)
def canon(obj) -> str:
    """Canonical JSON (Test B2's `compare_prefix` discipline): the object through JSON once (numpy → Python by run.py's own
    rule), re-serialised with sorted keys and compact separators."""
    return json.dumps(json.loads(json.dumps(obj, default=R._jsonable)), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def compare(ref: str, run: str) -> Dict[str, object]:
    """Byte for byte; the first differing offset (None when equal)."""
    if ref == run:
        return {"same": True, "first_diff": None, "n_bytes": len(ref.encode("utf-8"))}
    n = min(len(ref), len(run))
    step, i = 4096, 0
    while i < n and ref[i:i + step] == run[i:i + step]:
        i += step
    first = next((k for k in range(i, min(i + step, n)) if ref[k] != run[k]), n)
    return {"same": False, "first_diff": first, "n_bytes": len(ref.encode("utf-8"))}


def plant(text: str) -> str:
    """A copy with ONE character changed in the middle (Test B2's `plant_nudge`: the first alphanumeric at or after the
    middle, «0» → «1», anything else → «0») — the planted offender the check must refuse."""
    i = len(text) // 2
    j = next((k for k in range(i, len(text)) if text[k].isalnum()), next((k for k in range(len(text)) if text[k].isalnum()), 0))
    new = "0" if text[j] != "0" else "1"
    return text[:j] + new + text[j + 1:]


def identity(answers: Dict[str, object], summary: Dict[str, object], root_in: Path, ws: int, rp: int) -> Dict[str, object]:
    """§1: at the last reading point the life's `answers.point`, `answers.roads.LAW` and `learner.summary()` equal S1b-1R's
    record byte for byte under canonical JSON; for each part the planted control runs FIRST and must be CAUGHT."""
    d = R.r_seed_root(root_in, ws) / "arms" / "A-RW-R"
    ref_ans = json.loads((d / f"answers_{rp:05d}.json").read_text())
    ref_rec = json.loads((d / "record.json").read_text())
    parts = {"point": (ref_ans["point"], answers["point"]), "LAW": (ref_ans["roads"]["LAW"], answers["roads"]["LAW"]),
             "summary": (ref_rec["reading_points"][str(rp)]["summary"], summary)}
    out: Dict[str, object] = {"ref": str(d), "rp": rp, "parts": {}}
    for k, (ref, run) in parts.items():
        a, b = canon(ref), canon(run)
        caught = not compare(plant(a), b)["same"]
        r = compare(a, b)
        out["parts"][k] = {"same": r["same"], "first_diff": r["first_diff"], "n_bytes": r["n_bytes"], "planted_caught": caught,
                           "sha_ref": _sha(a), "sha_run": _sha(b)}
    out["pass"] = all(v["same"] and v["planted_caught"] for v in out["parts"].values())
    return out


# ------------------------------------------------------------------------------------------------ the life (§1, §2)
class _Hook:
    """The ONE read-only hook (§1): before each training scene the LAW road's claims (health.claims); after it the grades —
    through the learner's OWN attribution (the truth-free row) and, offline, at the scene's REFERENT (the truth-fed row,
    the ceiling of the row; the referent's hypothesis by marks.thing_hypothesis, the oracle arms' own mapping). Inactive
    until the first reading point at which the READER has types (§2)."""

    def __init__(self, L: "Lr.RWLearner", train: "R.Things", truth: Sequence[Dict[str, object]]):
        self.L, self.train, self.truth = L, train, truth
        self.free, self.fed = H.HealthBook(), H.HealthBook()
        self.active = False
        self.n_scenes = 0
        # AMENDMENT 1 §3, offline (the tape's truth; never read by a road): the truth-free row's gradable claims — graded or set
        # aside by the rule — by whether the gaze saw the scene's referent
        self.perception = {k: {"gradable": 0, "set_aside": 0, "scenes": 0, "scenes_set_aside": 0} for k in ("seen", "unseen")}

    def before(self, i: int, X: np.ndarray):
        if not self.active or np.atleast_2d(X).shape[0] == 0:
            return None
        rec = H.claims(Lr.RWRoad(self.L), X)
        self.free.add_claims(rec)
        self.fed.add_claims(rec)
        self.n_scenes += 1
        return rec

    def after(self, i: int, X: np.ndarray, words: Sequence[str], new: Sequence[str], rec) -> None:
        if rec is None:
            return
        g = H.grades(rec, H.attribution(self.L, X, words, new))           # through AMENDMENT 1's rule, at h*
        self.free.add_grades(g)
        ref = R.referent_index("A-RW", self.train, self.truth[i])
        self.fed.add_grades(H.grades(rec, {w: ref for w in dict.fromkeys(words)}))   # the SAME rule, at the referent's hypothesis
        if g and self.truth[i].get("referent") is not None:              # every training scene has one (declared)
            p = self.perception["unseen" if ref is None else "seen"]
            n_aside = sum(1 for _b, ok, _w in g if ok is None)
            p["gradable"] += len(g)
            p["set_aside"] += n_aside
            p["scenes"] += 1
            p["scenes_set_aside"] += int(n_aside == len(g))


def train_hooked(L: "Lr.RWLearner", train: "R.Things", rows, ws: int, seen: list, hook: _Hook) -> None:
    """A COPY of run.train_arm's A-RW road — the same calls in the same order (the thing inputs, train_scene with the scene's
    episodic generator, the calibration list) — with the read-only hook around train_scene."""
    for i in rows:
        X = train.for_arm("A-RW", i)
        words = train.p.words(i)
        rec = hook.before(i, X)
        known = set(L.index)
        L.train_scene(X, words, referent=None, rng=substream(ws, f"episodic:{i}"))
        seen.append((X, words, None))
        hook.after(i, X, words, [w for w in dict.fromkeys(words) if w not in known], rec)


def name_predictions(L: "Lr.RWLearner", Q: Dict[str, object], K: Dict[str, object], things: Dict[str, "R.Things"]) -> List[Dict]:
    """The fresh NAME things' believed names (§4 with the co-signed edit: the ROAD's b_T under the EAR's types — the mouth's own
    word, never name_forced): one per covered thing × learned type, with the world's verdict («correct»)."""
    road = Lr.RWRoad(L)
    ntypes = len(road.types())
    key = {it["item_id"]: it for it in K["items"]["NAME"]}
    out: List[Dict] = []
    for q in Q["questions"]["NAME"]:
        h = q.get("hyp")
        if h is None:
            continue
        B = road.believed(things[q["split"]].for_arm("A-RW", q["row"]))
        it = key[q["item_id"]]
        for k in range(ntypes):
            b = B[k][int(h)]
            if b is None:
                continue
            typ = W.word_type(b)
            out.append({"item_id": q["item_id"], "type": typ, "word": b, "correct": bool(it[typ] == b)})
    return out


def oracle_accuracy(preds: Sequence[Dict]) -> Dict[str, Optional[float]]:
    """HEALTH-ORACLE's rule (§3): per word, the true accuracy of the believed name over the NAME things believed to be it."""
    n: Dict[str, int] = {}
    ok: Dict[str, int] = {}
    for p in preds:
        n[p["word"]] = n.get(p["word"], 0) + 1
        ok[p["word"]] = ok.get(p["word"], 0) + int(p["correct"])
    return {w: (ok[w] / n[w] if n.get(w) else None) for w in sorted(set(TRAINED) | set(n))}


def answer_road(road: "H.HealthRoad", L: "Lr.RWLearner", questions: Dict[str, List[Dict]], things: Dict[str, "R.Things"],
                test_seed: int) -> Dict[str, Dict[str, object]]:
    """run.answer_all_r's per-road loop (M2b, NAME, SPEAK, SPEAK2, DECLINE — the same order, pointers and item tie generators)
    through a HEALTH road, with the words the row refused RECORDED per mouth item (`row_refused`); a decline the mouth calls
    «no sayable word» where the row refused a word the band held reads the ROW's reason («not held lately» when a row
    under 0.80 refused one, else «no row»), the mouth's own kept beside as `mouth_reason` (§3)."""
    feed = "A-RW"
    ans: Dict[str, Dict[str, object]] = {}
    for q in questions.get("M2b", []):
        k = q.get("hyp")
        ans[q["item_id"]] = ({"emit": None, "uncovered": True} if k is None else
                             {"emit": road.held_words(things[q["split"]].for_arm(feed, q["row"])[int(k)])})
    for q in questions.get("NAME", []):
        k = q.get("hyp")
        if k is None:
            ans[q["item_id"]] = {"name": None, "emit": None, "uncovered": True}
            continue
        x = things[q["split"]].for_arm(feed, q["row"])[int(k)]
        ans[q["item_id"]] = {"name": {t: L.name_forced(x, ws_) for t, ws_ in R.TYPE_WORDS.items()}, "emit": road.held_words(x)}
    for mark in ("SPEAK", "SPEAK2", "DECLINE"):
        for q in questions.get(mark, []):
            k = q.get("hyp")
            if k is None:
                ans[q["item_id"]] = {"spoken": None, "reason": "uncovered", "uncovered": True}
                continue
            X = things[q["split"]].for_arm(feed, q["row"])
            road.begin_item()
            a = Lr.produce_believed(road, X, int(k), lambda q=q: M.tie_rng(test_seed, q["item_id"]))
            refused = road.end_item()
            a["row_refused"] = refused
            if a.get("spoken") is None and a.get("reason") == "no sayable word" and refused:
                a["mouth_reason"] = a["reason"]
                a["reason"] = H.REASON_NOT_HELD if any(r["why"] == H.REASON_NOT_HELD for r in refused) else H.REASON_NO_ROW
            ans[q["item_id"]] = a
    return ans


def _compact(book: "H.HealthBook") -> Dict[str, Dict[str, object]]:
    return {w: {"n_claims": r.n_claims, "n_graded": r.n_graded, "cal20": r.cal20()} for w, r in sorted(book.rows.items())}


def run_life(ws: int, root_in: Path = S1B1R_ROOT, root_out: Path = TMEM2_ROOT, eps: Optional[float] = None,
             rps: Sequence[int] = W.READING_POINTS, n_train: int = W.N_TRAIN, log=print) -> Dict[str, object]:
    """ONE HEALTH life (§1): A-RW-R's training re-run (the same code, seed, lr 0.01, reading points; the READER calibrated at
    every reading point, as S1b-1R did — the claims read the latest one) with the read-only hook; at the last reading point
    the LAW road through S1b-1R's own `answer_all_r` (the identity's object) and the four HEALTH roads, each ONE difference in
    `sayable` on the one learned state; the identity checked against S1b-1R's record."""
    t_cpu, t_wall = time.process_time(), time.perf_counter()
    rs_in = R.r_seed_root(root_in, ws)
    ref_rec = json.loads((rs_in / "arms" / "A-RW-R" / "record.json").read_text())
    eps = ref_rec["eps"] if eps is None else eps
    Q = json.loads((rs_in / "questions.json").read_text())
    K = json.loads((rs_in / "keys.json").read_text())
    things = {s: R.Things(C.ScenePercepts(C.cache_dir(root_in, ws, s, R.R_TSET))) for s in C.test_splits(R.R_TSET)}
    train = R.Things(C.ScenePercepts(C.cache_dir(root_in, ws, "train")))
    truth = C.load_truth(C.cache_dir(root_in, ws, "train"))
    L = R.make_learner("A-RW", Lr.LR_S1B1, eps)
    hook = _Hook(L, train, truth)
    seen: list = []
    done = 0
    rps = sorted(r for r in rps if r <= n_train)
    out = Path(root_out) / str(ws) / "life"
    out.mkdir(parents=True, exist_ok=True)
    rec: Dict[str, object] = {"world_seed": ws, "test_seed": Q["test_seed"], "eps": eps, "rps": rps, "n_train": n_train,
                              "root_in": str(root_in), "prereg_tmem2_sha256": PREREG_TMEM2_SHA256,
                              "prereg_tmem2_amend1_sha256": PREREG_TMEM2_AMEND1_SHA256,
                              "prereg_s1b1r_sha256": R.PREREG_S1B1R_SHA256, "code": R.code_identity(), "rows_by_rp": {}}
    for rp in rps:
        train_hooked(L, train, range(done, rp), ws, seen, hook)
        done = rp
        final = rp == rps[-1]
        R.prepare("A-RW", L, seen)
        L.calibrate_r(eps, R.WORD_TYPES if final else None)
        rec["rows_by_rp"][str(rp)] = {"free": _compact(hook.free), "fed": _compact(hook.fed)}
        hook.active = True
        log(f"[life {ws}] reading point {rp}: claims on {hook.n_scenes} scenes · cpu {time.process_time() - t_cpu:.1f} s")
    preds = name_predictions(L, Q, K, things)
    acc = oracle_accuracy(preds)
    perm = H.derange(TRAINED, substream(ws, f"tmem2-null:{ws}"))
    answers = R.answer_all_r("A-RW-R", L, Q["questions"], things, Q["test_seed"], {"LAW": (Lr.RWRoad(L), "believed", "none_i")})
    gates = {"HEALTH-MOUTH": H.book_gate(hook.free), "HEALTH-ORACLE": H.accuracy_gate(acc),
             "HEALTH-TRUTHFED": H.book_gate(hook.fed), "NULL": H.book_gate(hook.free, perm)}
    for name in HEALTH_ROADS:
        answers["roads"][name] = answer_road(H.HealthRoad(L, gates[name]), L, Q["questions"], things, Q["test_seed"])
    idn = identity(answers, L.summary(), root_in, ws, rps[-1])
    R.dump(out / f"answers_{rps[-1]:05d}.json", {"world_seed": ws, "rp": rps[-1], **answers})
    rec.update({"rows": {"free": hook.free.summary(), "fed": hook.fed.summary()}, "claim_scenes": hook.n_scenes,
                "perception": hook.perception,
                "name_preds": preds, "oracle_accuracy": acc, "perm": perm, "identity": idn,
                "types": [list(t) for t in Lr.RWRoad(L).types()],
                "cpu_s": time.process_time() - t_cpu, "wall_s": time.perf_counter() - t_wall})
    R.dump(out / "record.json", rec)
    log(f"[life {ws}] identity {'PASS' if idn['pass'] else 'MISS'} · cpu {rec['cpu_s']:.1f} s · wall {rec['wall_s']:.1f} s")
    return rec


# ------------------------------------------------------------------------------------------------ the graders (§4)
def grade_road(ctx: "R._RCtx", ans: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """S1b-1R's graders unchanged, on COVERED targets (the gaze arms' pointers)."""
    ptr = ctx.ptr["gaze"]
    sp_rows = M.grade_mouth_r(ctx.items["SPEAK"], ans, ctx.truth["speak"], ptr)
    s2_rows = M.grade_mouth_r(ctx.items["SPEAK2"], ans, ctx.truth["speak2"], ptr)
    dc_rows = M.grade_decline(ctx.items["DECLINE"], ans, ctx.truth["decline"], ptr)
    return {"MOUTH": M.summarise_mouth_r(sp_rows, s2_rows), "DECLINE": M.summarise_decline(dc_rows),
            "M2b": M.grade_m2b(ctx.items["M2b"], ans, ctx.m2b_cov, "emit"),
            "rows": {r["item_id"]: r for r in list(sp_rows) + list(s2_rows)},
            "refused_words": _refused_counts(ans, ctx)}


def _refused_counts(ans: Dict[str, Dict[str, object]], ctx: "R._RCtx") -> Dict[str, int]:
    out: Dict[str, int] = {}
    for it in list(ctx.items["SPEAK"]) + list(ctx.items["SPEAK2"]):
        for r in (ans.get(it["item_id"]) or {}).get("row_refused") or []:
            key = f"{r['word']}:{r['why']}"
            out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


def decision(ctrl_rows: Dict[str, Dict[str, object]], arm_rows: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """§4 the decision marks over the CONTROL's spoken phrases on covered targets (SPEAK + SPEAK2): ERROR-RECALL = of its
    spoken-and-FALSE phrases, the fraction the arm DECLINES or replaces by a TRUE phrase; TRUE-RETENTION = of its
    spoken-and-TRUE phrases, the fraction the arm still speaks TRULY."""
    err = [i for i, r in ctrl_rows.items() if r["covered"] and r["spoken"] and not r["true"]]
    tru = [i for i, r in ctrl_rows.items() if r["covered"] and r["spoken"] and r["true"]]
    er_hits = sum(1 for i in err if (not arm_rows[i]["spoken"]) or arm_rows[i]["true"])
    tr_hits = sum(1 for i in tru if arm_rows[i]["spoken"] and arm_rows[i]["true"])
    return {"n_err": len(err), "n_true": len(tru), "n_spoken": len(err) + len(tru), "er_hits": er_hits, "tr_hits": tr_hits,
            "er": (er_hits / len(err)) if err else None, "tr": (tr_hits / len(tru)) if tru else None,
            "declined": sum(1 for i in err if not arm_rows[i]["spoken"]),
            "replaced_true": sum(1 for i in err if arm_rows[i]["spoken"] and arm_rows[i]["true"])}


def calibration(rec: Dict[str, object], kind: str) -> Dict[str, object]:
    """§4 ECE and type-2 AUROC of a row's cal_20 against the NAME things' verdicts: «free» the truth-free row (the law's),
    «fed» the truth-fed row (the row's ceiling), «null» the deranged rows (the floor of «uncalibrated»). A word with no graded
    claim has no cal_20: excluded, counted."""
    rows = rec["rows"]["fed" if kind == "fed" else "free"]
    perm = rec["perm"]
    conf, corr, excluded = [], [], 0
    for p in rec["name_preds"]:
        w = perm.get(p["word"], p["word"]) if kind == "null" else p["word"]
        c = (rows.get(w) or {}).get("cal20")
        if c is None:
            excluded += 1
            continue
        conf.append(float(c))
        corr.append(1 if p["correct"] else 0)
    e = H.ece(conf, corr)
    return {"ece": e["ece"], "curve": e["curve"], "n_pred": len(conf), "n_err": e["n_err"], "n_excluded": excluded,
            "auroc": H.auroc(conf, corr), "conf": conf, "correct": corr}


def word_table(rec: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    """§2 printed per word at the last reading point: n_claims, n_graded, cal_20 truth-free and truth-fed, |difference|,
    median |Δ|, the drift READING's firings (both forms), the said word's MISSED count, and the gate's state."""
    free, fed = rec["rows"]["free"], rec["rows"]["fed"]
    out = {}
    for w in TRAINED:
        f, g = free.get(w, {}), fed.get(w, {})
        cf, cg = f.get("cal20"), g.get("cal20")
        gate = "open" if (f.get("n_graded", 0) >= H.GATE_N and cf is not None and cf >= H.GATE_CAL) else (
            H.REASON_NO_ROW if f.get("n_graded", 0) < H.GATE_N else H.REASON_NOT_HELD)
        out[w] = {"n_claims": f.get("n_claims", 0), "n_graded": f.get("n_graded", 0), "cal20_free": cf, "cal20_fed": cg,
                  "n_graded_fed": g.get("n_graded", 0),
                  "abs_diff": (abs(cf - cg) if cf is not None and cg is not None else None),
                  "median_abs_delta": f.get("median_abs_delta"), "drift_firings": f.get("drift_firings", 0),
                  "drift_firings_floor": f.get("drift_firings_floor", 0), "missed": f.get("missed", 0), "gate": gate,
                  "oracle_accuracy": rec["oracle_accuracy"].get(w),
                  "unseen": f.get("unseen", 0), "unseen_fed": g.get("unseen", 0),                     # AMENDMENT 1 §3
                  "residual": (cf - cg if cf is not None and cg is not None else None)}
    return out


def grade_seed_tmem2(root_in: Path = S1B1R_ROOT, root_out: Path = TMEM2_ROOT, ws: int = 20261101,
                     rp: int = W.N_TRAIN, life_dir: Optional[Path] = None, log=print) -> Dict[str, object]:
    """One seed's marks (§4): every road's mouth marks and reasons (the CONTROL graded from S1b-1R's own record), the decision
    marks against the control, ECE / AUROC of the three rows, the per-word table, the identity and the life's cost."""
    ctx = R._RCtx(root_in, ws)
    life_dir = Path(life_dir) if life_dir is not None else Path(root_out) / str(ws) / "life"
    ctrl = json.loads((R.r_seed_root(root_in, ws) / "arms" / "A-RW-R" / f"answers_{rp:05d}.json").read_text())["roads"]["LAW"]
    life = json.loads((life_dir / f"answers_{rp:05d}.json").read_text())
    rec = json.loads((life_dir / "record.json").read_text())
    graded = {"CONTROL": grade_road(ctx, ctrl), "LAW": grade_road(ctx, life["roads"]["LAW"])}
    for name in HEALTH_ROADS:
        graded[name] = grade_road(ctx, life["roads"][name])
    dec = {name: decision(graded["CONTROL"]["rows"], g["rows"]) for name, g in graded.items()}
    rep = Path(root_in) / "report.json"
    ctrl_vs_report = None
    if rep.exists():
        b = json.loads(rep.read_text())["seeds"].get(str(ws))
        if b is not None:
            mo = graded["CONTROL"]["MOUTH"]
            ctrl_vs_report = {"TRUTH": [mo["truth"], b["TRUTH"]["value"]], "SPOKEN": [mo["spoken"], b["SPOKEN"]["value"]],
                              "TRUTH-NEED": [mo["truth_need"], b["TRUTH-NEED"]["value"]]}
            ctrl_vs_report["equal"] = all(a == c for a, c in ctrl_vs_report.values())
    out = {"prereg_tmem2_sha256": PREREG_TMEM2_SHA256, "prereg_tmem2_amend1_sha256": PREREG_TMEM2_AMEND1_SHA256,
           "perception": rec["perception"], "world_seed": ws, "test_seed": W.FRESH_TEST_SEEDS[ws], "rp": rp,
           "roads": {n: {k: v for k, v in g.items() if k != "rows"} for n, g in graded.items()}, "decision": dec,
           "calibration": {k: calibration(rec, k) for k in ("free", "fed", "null")}, "words": word_table(rec),
           "identity": rec["identity"], "life_cpu_s": rec["cpu_s"], "claim_scenes": rec["claim_scenes"],
           "types": rec["types"], "perm": rec["perm"], "control_vs_report": ctrl_vs_report}
    R.dump(life_dir.parent / "marks.json", out)                  # <root>/<ws>/marks.json beside the life it grades
    log(f"[grade-tmem2 {ws}] written")
    return out


# ------------------------------------------------------------------------------------------------ the bars (§5)
def b1(truth_hm: Optional[float], n_hm: int, truth_ho: Optional[float], spoken_hm: Optional[float],
       spoken_ctrl: Optional[float], truth_ctrl: Optional[float]) -> Dict[str, object]:
    """B1 TRUTH at the same rate, one seed: TRUTH(HM) ≥ 0.90 × TRUTH(HO) AND SPOKEN(HM) ≥ 0.80 × SPOKEN(CONTROL) — no pass by
    silence (a SPOKEN miss FAILS whatever TRUTH reads); TRUTH on < 30 spoken → UNDERPOWERED; «met by the control» where the
    CONTROL already meets 0.90 × the oracle (then B1 is not evidence for the gate)."""
    bar_t = None if truth_ho is None else B1_TRUTH * truth_ho
    bar_s = None if spoken_ctrl is None else B1_SPOKEN * spoken_ctrl
    spoken_ok = spoken_hm is not None and bar_s is not None and spoken_hm >= bar_s
    met = bool(truth_ctrl is not None and bar_t is not None and truth_ctrl >= bar_t)
    if truth_hm is None or bar_t is None or bar_s is None:
        v = "NOT GRADABLE"
    elif not spoken_ok:
        v = "FAIL"
    elif (n_hm or 0) < POWER_N:
        v = "UNDERPOWERED"
    else:
        v = "PASS" if truth_hm >= bar_t else "FAIL"
    return {"verdict": v, "truth_hm": truth_hm, "n_hm": n_hm, "truth_ho": truth_ho, "bar_truth": bar_t, "spoken_hm": spoken_hm,
            "spoken_ctrl": spoken_ctrl, "bar_spoken": bar_s, "spoken_ok": spoken_ok, "truth_ctrl": truth_ctrl, "met_by_control": met}


def b2(er_hm: Optional[float], er_ho: Optional[float], tr_hm: Optional[float], er_null: Optional[float], n_err: int) -> Dict[str, object]:
    """B2 the decision, POOLED: ER(HM) ≥ 0.70 × ER(HO) AND TRUE-RETENTION(HM) ≥ 0.90 AND the NULL below HM by at least its
    95 % binomial half-width (the ruled form: 1.96·√(p(1−p)/n), p = the NULL's ER, n = the control's pooled errors; > 0 when the
    half-width is 0); CEILING-BOUND when the oracle's own ER < 0.30; UNDERPOWERED under 30 errors."""
    hw = binomial_half_width_95(er_null, n_err) if (er_null is not None and n_err > 0) else None
    gap = None if (er_hm is None or er_null is None) else er_hm - er_null
    c1 = er_hm is not None and er_ho is not None and er_hm >= B2_ER * er_ho
    c2 = tr_hm is not None and tr_hm >= B2_TR
    c3 = gap is not None and hw is not None and gap >= hw and (gap > 0 if hw == 0 else True)
    if n_err < POWER_N:
        v = "UNDERPOWERED"
    elif er_ho is None or er_hm is None:
        v = "NOT GRADABLE"
    elif er_ho < B2_CEIL:
        v = "CEILING-BOUND"
    else:
        v = "PASS" if (c1 and c2 and c3) else "FAIL"
    return {"verdict": v, "er_hm": er_hm, "er_ho": er_ho, "bar_er": (None if er_ho is None else B2_ER * er_ho), "tr_hm": tr_hm,
            "er_null": er_null, "null_hw": hw, "null_gap": gap, "n_err": n_err, "clauses": {"recall": c1, "retention": c2, "null": c3}}


def b3(ece_free: Optional[float], n_pred: int) -> Dict[str, object]:
    """B3 calibration, one seed: ECE(the truth-free row) ≤ 0.10, read on its n predictions (the ruling)."""
    v = "NOT GRADABLE" if ece_free is None else ("UNDERPOWERED" if n_pred < POWER_N else ("PASS" if ece_free <= B3_ECE else "FAIL"))
    return {"verdict": v, "ece": ece_free, "n_pred": n_pred}


def b4(auroc_pooled: Optional[float], n_err_pooled: int) -> Dict[str, object]:
    """B4 sensitivity: type-2 AUROC ≥ 0.70 POOLED over the three seeds; UNDERPOWERED under 30 errors pooled."""
    v = "NOT GRADABLE" if auroc_pooled is None else ("UNDERPOWERED" if n_err_pooled < POWER_N else ("PASS" if auroc_pooled >= B4_AUROC else "FAIL"))
    return {"verdict": v, "auroc": auroc_pooled, "n_err": n_err_pooled}


def step3(free: Dict[str, Dict[str, object]], fed: Dict[str, Dict[str, object]], words: Sequence[str]) -> Dict[str, object]:
    """THE FIRST GATE step 3 as ruled: a word under 20 graded claims reads «no row» (printed, not a stop); a trained word whose
    truth-free cal_20 reads below its truth-fed cal_20 is a printed reading, and a STOP only when by MORE than 0.10 (the
    declared instrument fault of §6)."""
    no_row = [w for w in words if (free.get(w) or {}).get("n_graded", 0) < H.GATE_N]
    rev, fault = [], []
    for w in words:
        if w in no_row:
            continue
        cf, cg = (free.get(w) or {}).get("cal20"), (fed.get(w) or {}).get("cal20")
        if cf is None or cg is None or cf >= cg:
            continue
        rev.append(w)
        if cg - cf > STEP3_TOL + 1e-9:
            fault.append(w)
    return {"no_row": no_row, "reversed": rev, "fault": fault, "stop": bool(fault)}


def bars_tmem2(marks: Dict[int, Dict[str, object]]) -> Dict[str, object]:
    """§5 and §6 over the three seeds' marks."""
    seeds = sorted(marks)
    out: Dict[str, object] = {"B1": {}, "B3": {}, "per_seed": {}, "refute": {}}
    pooled = {n: {"er_hits": 0, "n_err": 0, "tr_hits": 0, "n_true": 0} for n in GRADED_ROADS}
    conf, corr = [], []
    for ws in seeds:
        mk = marks[ws]
        mo = {n: mk["roads"][n]["MOUTH"] for n in GRADED_ROADS}
        out["B1"][ws] = b1(mo["HEALTH-MOUTH"]["truth"], mo["HEALTH-MOUTH"]["n_truth"] or 0, mo["HEALTH-ORACLE"]["truth"],
                           mo["HEALTH-MOUTH"]["spoken"], mo["CONTROL"]["spoken"], mo["CONTROL"]["truth"])
        cal = mk["calibration"]
        out["B3"][ws] = b3(cal["free"]["ece"], cal["free"]["n_pred"])
        conf += cal["free"]["conf"]
        corr += cal["free"]["correct"]
        for n in GRADED_ROADS:
            d = mk["decision"][n]
            for k in pooled[n]:
                pooled[n][k] += d[k]
        dec = mk["decision"]
        n_rev = [w for w, v in mk["words"].items() if v["abs_diff"] is not None and v["abs_diff"] > 0.10]
        out["refute"][ws] = {
            "a_silence": bool(mo["HEALTH-MOUTH"]["spoken"] is not None and mo["CONTROL"]["spoken"] is not None
                              and mo["HEALTH-MOUTH"]["spoken"] < B1_SPOKEN * mo["CONTROL"]["spoken"]
                              and (mo["HEALTH-MOUTH"]["truth"] or 0) > (mo["CONTROL"]["truth"] or 0)),
            "d_disagree_words": n_rev, "d_fires": len(n_rev) >= 3,
            "sign_reversed": [w for w, v in mk["words"].items() if v["cal20_free"] is not None and v["cal20_fed"] is not None
                              and v["cal20_free"] < v["cal20_fed"]],
            "sign_fault": [w for w, v in mk["words"].items() if v["cal20_free"] is not None and v["cal20_fed"] is not None
                           and v["cal20_fed"] - v["cal20_free"] > STEP3_TOL + 1e-9]}
        out["per_seed"][ws] = {n: {"er": dec[n]["er"], "tr": dec[n]["tr"], "n_err": dec[n]["n_err"], "n_true": dec[n]["n_true"]}
                               for n in GRADED_ROADS}
    pooled_rates = {n: {"er": (p["er_hits"] / p["n_err"]) if p["n_err"] else None, "tr": (p["tr_hits"] / p["n_true"]) if p["n_true"] else None,
                        **p} for n, p in pooled.items()}
    out["pooled"] = pooled_rates
    n_err = pooled["CONTROL"]["n_err"]
    out["B2"] = b2(pooled_rates["HEALTH-MOUTH"]["er"], pooled_rates["HEALTH-ORACLE"]["er"], pooled_rates["HEALTH-MOUTH"]["tr"],
                   pooled_rates["NULL"]["er"], n_err)
    au = H.auroc(conf, corr)
    out["B4"] = b4(au, int(len(corr) - sum(corr)))
    out["B4"]["per_seed"] = {ws: {"auroc": marks[ws]["calibration"]["free"]["auroc"], "n_err": marks[ws]["calibration"]["free"]["n_err"]}
                             for ws in seeds}
    b1_all = all(out["B1"][ws]["verdict"] == "PASS" for ws in seeds)
    b3_all = all(out["B3"][ws]["verdict"] == "PASS" for ws in seeds)
    b2v, b4v = out["B2"]["verdict"], out["B4"]["verdict"]
    out["passes"] = bool(b1_all and b3_all and b4v == "PASS" and b2v in ("PASS", "CEILING-BOUND"))
    out["refute"]["b_null_like_mouth"] = not out["B2"]["clauses"]["null"]
    out["refute"]["c_ceiling"] = out["B2"]["verdict"] == "CEILING-BOUND"
    return out


# ------------------------------------------------------------------------------------------------ the report
def _f(v, nd=3) -> str:
    return "  —  " if v is None else f"{v:.{nd}f}"


def seed_lines(mk: Dict[str, object]) -> List[str]:
    ws = mk["world_seed"]
    idn = mk["identity"]
    L = [f"== T-MEM-2 · world seed {ws} (fresh test seed {mk['test_seed']}) ==",
         "the identity with S1b-1R's A-RW-R record at 10,000 (canonical JSON; the planted byte first): " + " · ".join(
             f"{k} {'=' if v['same'] else '≠'} ({v['n_bytes']} bytes; planted {'CAUGHT' if v['planted_caught'] else 'NOT CAUGHT'})"
             for k, v in idn["parts"].items()) + f" → {'PASS' if idn['pass'] else 'MISS'}",
         f"the learned types: " + " ".join("(" + " ".join(t) + ")" for t in mk["types"]) + f" · claims recorded on {mk['claim_scenes']} training scenes",
         "the rows at 10,000 (per word: confident claims · graded · set aside «unseen» (AMENDMENT 1) · cal_20 truth-free / truth-fed · |diff| · median |Δ| · drift firings unfloored / floored 1/20 · the said word's MISSED · the gate · the oracle's accuracy):"]
    for w, v in mk["words"].items():
        L.append(f"   {w:<9} claims {v['n_claims']:>5} · graded {v['n_graded']:>5} (fed {v['n_graded_fed']:>5}) · unseen {v.get('unseen', 0):>4} (fed {v.get('unseen_fed', 0):>4})"
                 f" · cal_20 {_f(v['cal20_free'])} / {_f(v['cal20_fed'])}"
                 f" · |diff| {_f(v['abs_diff'])} · median |Δ| {_f(v['median_abs_delta'])} · drift {v['drift_firings']} / {v['drift_firings_floor']}"
                 f" · missed {v['missed']:>4} · gate {v['gate']} · oracle {_f(v['oracle_accuracy'])}")
    if mk.get("perception"):
        L.append("AMENDMENT 1's readings (offline, the tape's truth; readings, never bars): " + perception_line(ws, mk["perception"]))
    L.append("the roads (S1b-1R's graders, covered targets): SPOKEN · TRUTH (n) · ×spoken · READ-BACK · SPEAK2 spoken · TRUTH-NEED (n) · MINIMAL (n) · ORDER (n) · DECLINE (reading) · M2b (the band, unchanged)")
    for n in ("CONTROL", "LAW") + HEALTH_ROADS:
        g = mk["roads"][n]
        mo, dc = g["MOUTH"], g["DECLINE"]
        sp = mo["speak"] or {}
        L.append(f"   {n:<16} {_f(mo['spoken'])} · {_f(mo['truth'])} (n {mo['n_truth']}) · {_f(sp.get('truth_x_spoken'))} · {_f(mo['readback_all'])} · "
                 f"{_f(mo['spoken2'])} · {_f(mo['truth_need'])} (n {mo['n_truth_need']}) · {_f(mo['minimal'])} (n {mo['n_minimal']}) · "
                 f"{_f(mo['order'])} (n {mo['n_order']}) · DECLINE {_f(dc['decline'])} · M2b {_f(g['M2b']['graded']['correct'])}")
        L.append(f"   {'':<16} reasons SPEAK {sp.get('reasons')} · SPEAK2 {mo['reasons2']} · DECLINE {dc['reasons']}"
                 + (f" · the row refused {g['refused_words']}" if g.get("refused_words") else ""))
    L.append("the decision (over the CONTROL's spoken phrases on SPEAK + SPEAK2, covered): ERROR-RECALL (declined + replaced true / errors) · TRUE-RETENTION (true / true):")
    for n in GRADED_ROADS:
        d = mk["decision"][n]
        L.append(f"   {n:<16} ER {_f(d['er'])} ({d['declined']} + {d['replaced_true']} / {d['n_err']}) · TR {_f(d['tr'])} ({d['tr_hits']} / {d['n_true']})")
    for k, lab in (("free", "the truth-free row (the law's)"), ("fed", "the truth-fed row (its ceiling)"), ("null", "the deranged rows (the floor)")):
        c = mk["calibration"][k]
        L.append(f"   calibration of {lab}: ECE {_f(c['ece'])} · type-2 AUROC {_f(c['auroc'])} · n {c['n_pred']} (errors {c['n_err']}; no row {c['n_excluded']})"
                 " · curve " + " ".join(f"[{b['bin'] / 10:.1f}: n {b['n']} conf {b['conf']:.2f} acc {b['acc']:.2f}]" for b in c["curve"]))
    cv = mk.get("control_vs_report")
    if cv:
        L.append(f"   the CONTROL re-graded vs S1b-1R's report.json: TRUTH {cv['TRUTH']} · SPOKEN {cv['SPOKEN']} · TRUTH-NEED {cv['TRUTH-NEED']} → {'EQUAL' if cv['equal'] else 'DIFFER'}")
    return L


def report_tmem2(root_in: Path = S1B1R_ROOT, root_out: Path = TMEM2_ROOT, log=print) -> Dict[str, object]:
    """THE GRADER READING THE LAW AS WRITTEN (and as ruled): every seed's tables, §5's bars, §6's refutations and readings."""
    marks = {ws: json.loads((Path(root_out) / str(ws) / "marks.json").read_text()) for ws in W.WORLD_SEEDS}
    lines = [f"T-MEM-2 report · PREREG-TMEM2 sha {PREREG_TMEM2_SHA256} · AMENDMENT 1 sha {PREREG_TMEM2_AMEND1_SHA256} · PREREG-S1B1R {R.PREREG_S1B1R_SHA256[:16]}… · the control's report.txt {S1B1R_REPORT_SHA256[:16]}…", ""]
    for ws in W.WORLD_SEEDS:
        lines += seed_lines(marks[ws])
        lines.append("")
    b = bars_tmem2(marks)
    pooled = {k: {f: sum(marks[ws]["perception"][k][f] for ws in W.WORLD_SEEDS) for f in ("gradable", "set_aside", "scenes", "scenes_set_aside")}
              for k in ("seen", "unseen")}
    lines.append("== AMENDMENT 1's READINGS (offline, the tape's truth; readings, never bars) ==")
    lines += [perception_line(ws, marks[ws]["perception"]) for ws in W.WORLD_SEEDS] + [perception_line("pooled", pooled), ""]
    lines.append("== T-MEM-2 BARS (fresh seeds; the ceiling beside every bar; the ruled forms of B2's null clause and B3's power) ==")
    for ws in W.WORLD_SEEDS:
        x = b["B1"][ws]
        lines.append(f"{ws} B1 TRUTH(HEALTH-MOUTH) {_f(x['truth_hm'])} (n {x['n_hm']}) ≥ {_f(x['bar_truth'])} (0.90 × HEALTH-ORACLE {_f(x['truth_ho'])}) AND SPOKEN "
                     f"{_f(x['spoken_hm'])} ≥ {_f(x['bar_spoken'])} (0.80 × CONTROL {_f(x['spoken_ctrl'])}) → {x['verdict']} · the CONTROL's TRUTH {_f(x['truth_ctrl'])}"
                     + (" — «met by the control»: NOT evidence for the gate (B2 carries the claim)" if x["met_by_control"] else ""))
        y = b["B3"][ws]
        c = marks[ws]["calibration"]
        lines.append(f"         B3 ECE(the truth-free row) {_f(y['ece'])} ≤ 0.10 (n {y['n_pred']} predictions; errors {c['free']['n_err']}) → {y['verdict']}"
                     f" · the NULL {_f(c['null']['ece'])} (the floor) · the truth-fed row {_f(c['fed']['ece'])} (the row's ceiling)")
        ps = b["per_seed"][ws]
        lines.append("         the decision per seed: " + " · ".join(f"{n} ER {_f(v['er'])} (n {v['n_err']}) TR {_f(v['tr'])} (n {v['n_true']})" for n, v in ps.items()))
        lines.append(f"         B4 per seed (a reading; the bar is pooled): AUROC {_f(b['B4']['per_seed'][ws]['auroc'])} (errors {b['B4']['per_seed'][ws]['n_err']})")
    x = b["B2"]
    pr = b["pooled"]
    lines.append(f"POOLED B2 ERROR-RECALL(HEALTH-MOUTH) {_f(x['er_hm'])} ≥ {_f(x['bar_er'])} (0.70 × HEALTH-ORACLE {_f(x['er_ho'])}) AND TRUE-RETENTION {_f(x['tr_hm'])} ≥ 0.90"
                 f" AND the NULL {_f(x['er_null'])} below by ≥ its half-width {_f(x['null_hw'])} (gap {_f(x['null_gap'])}) · n errors {x['n_err']} → {x['verdict']}"
                 + (" — the control's errors are the gaze's, not the words' (CEILING-BOUND: the oracle's own recall < 0.30)" if x["verdict"] == "CEILING-BOUND" else "")
                 + f" · clauses {x['clauses']}")
    lines.append("       pooled decision: " + " · ".join(f"{n} ER {_f(v['er'])} ({v['er_hits']}/{v['n_err']}) TR {_f(v['tr'])} ({v['tr_hits']}/{v['n_true']})" for n, v in pr.items()))
    y = b["B4"]
    lines.append(f"POOLED B4 type-2 AUROC(the truth-free row) {_f(y['auroc'])} ≥ 0.70 (errors {y['n_err']}; chance 0.50) → {y['verdict']}")
    rf = b["refute"]
    lines.append("refutations (§6): (a) the row buys silence " + " ".join(f"{ws}:{'YES' if rf[ws]['a_silence'] else 'no'}" for ws in W.WORLD_SEEDS)
                 + f" · (b) the NULL ≈ HEALTH-MOUTH (the null clause not met) {'YES — the gate refuses, it does not know' if rf['b_null_like_mouth'] else 'no'}"
                 + f" · (c) CEILING-BOUND {'YES' if rf['c_ceiling'] else 'no'}"
                 + " · (d) the rows disagree by > 0.10 on ≥ 3 words " + " ".join(f"{ws}:{'YES ' + str(rf[ws]['d_disagree_words']) if rf[ws]['d_fires'] else 'no (' + str(len(rf[ws]['d_disagree_words'])) + ')'}" for ws in W.WORLD_SEEDS))
    lines.append("the declared sign (§6: truth-free cal_20 ≥ truth-fed on every word): " + " ".join(
        f"{ws}: reversed {rf[ws]['sign_reversed'] or 'none'}" + (f" — FAULT (> 0.10) {rf[ws]['sign_fault']}" if rf[ws]["sign_fault"] else "") for ws in W.WORLD_SEEDS))
    b1s = "/".join(b["B1"][ws]["verdict"] for ws in W.WORLD_SEEDS)
    b3s = "/".join(b["B3"][ws]["verdict"] for ws in W.WORLD_SEEDS)
    lines.append(f"per seed: B1 {b1s} · B3 {b3s} · pooled: B2 {b['B2']['verdict']} · B4 {b['B4']['verdict']}")
    lines.append(f"A PASS is B1–B4, or B2 CEILING-BOUND with B1, B3, B4 met → T-MEM-2 {'PASSES' if b['passes'] else 'does not pass'}")
    for l in lines:
        log(l)
    out = {"prereg_tmem2_sha256": PREREG_TMEM2_SHA256, "prereg_tmem2_amend1_sha256": PREREG_TMEM2_AMEND1_SHA256, "bars": b,
           "perception": {"per_seed": {ws: marks[ws]["perception"] for ws in W.WORLD_SEEDS}, "pooled": pooled}, "lines": lines}
    R.dump(Path(root_out) / "report.json", out)
    (Path(root_out) / "report.txt").write_text("\n".join(lines) + "\n")
    return out


# ------------------------------------------------------------------------------------------------ THE FIRST GATE (§7)
def gate_or_chosen_tmem2(root_out: Path = TMEM2_ROOT) -> Dict[str, object]:
    p = Path(root_out) / "gate" / "gate.json"
    if not p.exists():
        raise TMem2Error(f"{p} missing — THE FIRST GATE runs before the unit")
    g = json.loads(p.read_text())
    if (g.get("verdict") != "PROCEED" or g.get("prereg_tmem2_sha256") != PREREG_TMEM2_SHA256
            or g.get("prereg_tmem2_amend1_sha256") != PREREG_TMEM2_AMEND1_SHA256):
        raise TMem2Error(f"THE FIRST GATE reads {g.get('verdict')!r} under sha {g.get('prereg_tmem2_sha256')} / AMENDMENT 1 "
                         f"{g.get('prereg_tmem2_amend1_sha256')} — no unit")
    return g


def first_gate_tmem2(root_in: Path = S1B1R_ROOT, root_out: Path = TMEM2_ROOT, log=print) -> Dict[str, object]:
    """THE FIRST GATE (§7), each step a STOP on a miss, printed whole: (1) the identity, three lives run ONE AT A TIME (so each
    life's CPU is its solo price); (2) the row's toy, seeds 0–2; (3) agreement and coverage on seed 20261101's stream (the
    ruled STOP: a reversal of more than 0.10); (4) the smoke — seed 20261101's fresh items under all four roads, the reasons
    and the decision tables whole; (5) the price, solo, against ≤ 5 CPU-min. AMENDMENT 1: step 3 is read AFTER the rule, with
    the per-word graded / set-aside counts, the residual and the two perception readings (all three seeds) printed beside;
    step 5 is a STOP when OVER."""
    check_prereg_tmem2()
    t0, c0 = time.perf_counter(), time.process_time()
    gdir = Path(root_out) / "gate"
    lives_root = gdir / "lives"
    ctl = check_control(root_in)
    out: Dict[str, object] = {"prereg_tmem2_sha256": PREREG_TMEM2_SHA256, "prereg_tmem2_amend1_sha256": PREREG_TMEM2_AMEND1_SHA256,
                              "code": R.code_identity(), "control": ctl}
    lines = ["== THE FIRST GATE (PREREG-TMEM2 §7 + AMENDMENT 1 §4; each step a STOP on a miss; printed whole) ==",
             f"   the law: PREREG-TMEM2 {PREREG_TMEM2_SHA256[:16]}… · AMENDMENT 1 {PREREG_TMEM2_AMEND1_SHA256[:16]}… · code {out['code']['code_sha_file']}",
             f"0. the CONTROL's record: {ctl['report']} sha {'as recorded' if ctl['ok'] else 'CHANGED'} ({(ctl['sha'] or '')[:16]}…)"]
    stop: List[str] = [] if ctl["ok"] else ["the control's record changed"]
    lives = {}
    for ws in W.WORLD_SEEDS:
        lives[ws] = run_life(ws, root_in, lives_root, log=lambda s: None)
    out["identity"] = {ws: lives[ws]["identity"] for ws in lives}
    lines.append("1. THE IDENTITY (S1b-1R's A-RW-R record at 10,000; canonical JSON; the planted one-byte change first):")
    for ws, rec in lives.items():
        idn = rec["identity"]
        lines.append(f"   {ws}: " + " · ".join(f"{k} {'=' if v['same'] else '≠ at ' + str(v['first_diff'])} ({v['n_bytes']} bytes; planted {'CAUGHT' if v['planted_caught'] else 'NOT CAUGHT'})"
                                           for k, v in idn["parts"].items()) + f" · cpu {rec['cpu_s']:.1f} s → {'PASS' if idn['pass'] else 'MISS'}")
    if not all(rec["identity"]["pass"] for rec in lives.values()):
        stop.append("the identity (step 1)")
    toys = [H.row_toy(s) for s in (0, 1, 2)]
    out["toy"] = toys
    tok = all(toy_passes(t) for t in toys)
    lines.append("2. the row's toy (A 95 %, B 50 %, 200 graded claims each): " + " · ".join(
        f"seed {t['seed']}: cal_20 A {t['cal20']['A']:.2f} B {t['cal20']['B']:.2f} · kept {t['keeps']} · the null {t['null']} · an ungraded claim moves nothing {t['ungraded_moves_nothing']}"
        f" · a claim set aside «unseen» moves nothing {t['unseen_moves_nothing']}"
        for t in toys) + f" → {'PASS' if tok else 'MISS'}")
    if not tok:
        stop.append("the row's toy (step 2)")
    ws0 = W.WORLD_SEEDS[0]
    rec0 = lives[ws0]
    s3 = step3(rec0["rows"]["free"], rec0["rows"]["fed"], TRAINED)
    out["step3"] = s3
    lines.append(f"3. agreement and coverage on seed {ws0}'s stream (claims on {rec0['claim_scenes']} scenes), AFTER AMENDMENT 1's rule — per word:"
                 " graded truth-free / truth-fed · set aside «unseen» truth-free / truth-fed · cal_20 truth-free / truth-fed · the residual (free − fed):")
    near = []
    for w in TRAINED:
        f, g = rec0["rows"]["free"].get(w, {}), rec0["rows"]["fed"].get(w, {})
        cf, cg = f.get("cal20"), g.get("cal20")
        res = (cf - cg) if cf is not None and cg is not None else None
        if res is not None and abs(res) <= RESIDUAL_NEAR + 1e-9:
            near.append(w)
        lines.append(f"   {w:<9} {f.get('n_graded', 0):>5} / {g.get('n_graded', 0):>5} · {f.get('unseen', 0):>4} / {g.get('unseen', 0):>4} · {_f(cf)} / {_f(cg)} · "
                     + (f"{res:+.3f}" if res is not None else "  —  ")
                     + ("  «no row»" if w in s3["no_row"] else "") + ("  reversed (a reading)" if w in s3["reversed"] and w not in s3["fault"] else "")
                     + ("  REVERSED BY > 0.10 — the declared instrument fault" if w in s3["fault"] else ""))
    out["residual_near"] = near
    lines.append(f"   the residual within {RESIDUAL_NEAR:.2f} on {len(near)} of {len(TRAINED)} words (predicted: most [Likely]; a reading)")
    lines.append(f"   «no row»: {s3['no_row'] or 'none'} · reversed: {s3['reversed'] or 'none'} · the fault (> 0.10): {s3['fault'] or 'none'} → {'MISS' if s3['stop'] else 'PASS'}")
    out["perception"] = {ws: lives[ws]["perception"] for ws in W.WORLD_SEEDS}
    lines.append("   AMENDMENT 1's readings (offline, the tape's truth; readings, never bars), every gate life:")
    lines += ["      " + perception_line(ws, lives[ws]["perception"]) for ws in W.WORLD_SEEDS]
    if s3["stop"]:
        stop.append("the declared sign reversed by > 0.10 (step 3)")
    c = time.process_time()
    mk0 = grade_seed_tmem2(root_in, root_out, ws0, life_dir=lives_root / str(ws0) / "life", log=lambda s: None)
    grade_cpu = time.process_time() - c
    out["smoke"] = {"decision": mk0["decision"], "reasons": {n: {"speak": (mk0["roads"][n]["MOUTH"]["speak"] or {}).get("reasons"),
                                                               "speak2": mk0["roads"][n]["MOUTH"]["reasons2"],
                                                               "decline": mk0["roads"][n]["DECLINE"]["reasons"]} for n in mk0["roads"]}}
    lines.append(f"4. the smoke — seed {ws0}'s fresh items under all four roads (the tables whole):")
    lines += ["   " + l for l in seed_lines(mk0)[4:]]
    rb_bad = [n for n in HEALTH_ROADS if mk0["roads"][n]["MOUTH"]["readback_all"] not in (1.0, None)]
    lines.append(f"   the wiring pin (READ-BACK 1.000 wherever something was spoken): {'PASS' if not rb_bad else 'BROKEN ROAD ' + str(rb_bad)}")
    if rb_bad:
        stop.append("the smoke's wiring pin (step 4)")
    life_cpu = [lives[ws]["cpu_s"] for ws in W.WORLD_SEEDS]
    unit = sum(life_cpu) + 3 * grade_cpu
    out["price"] = {"life_cpu_s": life_cpu, "grade_cpu_s": grade_cpu, "unit_cpu_s": unit}
    pv = price_verdict(unit)
    out["price"]["verdict"] = pv
    lines.append(f"5. the price, solo (the three lives above ran one at a time): lives {' / '.join(f'{v:.1f}' for v in life_cpu)} CPU-s · one seed's grading {grade_cpu:.1f} CPU-s"
                 f" → the unit ≈ {unit:.0f} CPU-s ≈ {unit / 60:.1f} CPU-min against ≤ 5 declared → {'within → PASS' if pv['within'] else 'OVER → MISS'}")
    if pv["stop"]:
        stop.append("the price is OVER the declared ≤ 5 CPU-min (step 5)")
    out["verdict"] = "STOP" if stop else "PROCEED"
    out["stop_reasons"] = stop
    out["wall_s"] = time.perf_counter() - t0
    out["cpu_s"] = time.process_time() - c0
    lines.append(f"GATE: {out['verdict']}" + (f" — {'; '.join(stop)}" if stop else "") + f" · {out['wall_s']:.0f} s wall · {out['cpu_s']:.0f} CPU-s")
    for l in lines:
        log(l)
    out["lines"] = lines
    R.dump(gdir / "gate.json", out)
    (gdir / "gate.txt").write_text("\n".join(lines) + "\n")
    return out


# ------------------------------------------------------------------------------------------------ CLI
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="brain.scene.run_tmem2")
    ap.add_argument("cmd", choices=["first-gate", "life", "grade", "report"])
    ap.add_argument("--world-seed", type=int)
    ap.add_argument("--root-in", default=str(S1B1R_ROOT))
    ap.add_argument("--root-out", default=str(TMEM2_ROOT))
    a = ap.parse_args(argv)
    root_in, root_out = Path(a.root_in), Path(a.root_out)
    log = R.Log(root_out / "logs" / (f"{a.cmd}-{a.world_seed}.log" if a.world_seed else f"{a.cmd}.log"))   # three lives never share a log
    check_prereg_tmem2()
    if a.cmd == "first-gate":
        g = first_gate_tmem2(root_in, root_out, log=log)
        return 0 if g["verdict"] == "PROCEED" else 3
    if a.cmd == "life":
        rec = run_life(a.world_seed, root_in, root_out, log=log)
        return 0 if rec["identity"]["pass"] else 3
    if a.cmd == "grade":
        grade_seed_tmem2(root_in, root_out, a.world_seed, log=log)
    elif a.cmd == "report":
        report_tmem2(root_in, root_out, log=log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
