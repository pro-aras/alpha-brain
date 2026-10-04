"""tools/brain/gate_fm6.py — THE BENCH GATE OF F-M6 (docs/brain/body/PREREG-BRAIN-IN-BODY-AMEND-1.md §2, sha 45abeca2…).

edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:27 +0400 — new tool.

  gate_fm6.py --world-seed WS [--glances-root R] [--scored-root S] [--out D] [--plant]
  gate_fm6.py --pool D1 D2          (two seeds' output dirs, <out>/<ws>; the pooled exact sign test, the gate's third clause)

Two organs (genome/brain.py's Brain) are trained from the SAME caches in the SAME order through the mind's own call
(`Brain.learn`, gate_alone.glance_of's glance): THE LAW (`young 3`) and THE FIX (`young 3 nearest`), each configured by the BRAIN
line as machinery.parse_genome reads it. Both then answer, through `Brain.ask`, the questions of three test sets:
  held    the NEW set (2026150x): <glances-root>/<ws>/held/questions.json + keys.json (run.py questions-r --tset held), every mark
  fresh   the scored questions <scored-root>/<ws>/fresh/questions.json, every mark (as gate_alone)
  s1b1    the older set's POINTING <scored-root>/<ws>/questions.json (as gate_alone; answers keyed `older/<item>`)
Printed per seed, AMENDMENT 1 §2's clauses:
  IDENTITY  per set: every ask that is NOT a pointing ask on ONE young word (decided from the LAW organ's own state: a phrase
            of one word, heard, meetings < young — never from the fix's output) — the fix's whole answer EQUALS the law's:
            asks compared · equal · the first difference. Beside it, on the young asks: the answer but `point`, the digest's
            `hyp` / `pos` / `fix` and the new fields (`young_d`, `point_rule`) equals the law's (best, scores, the «none»
            flags and their fits are the law's numbers); and the rule acted ONLY on young asks (acted outside: must be 0).
  M6        on held, for the law and the fix: covered accuracy, n covered, chance (marks.grade_pointing's own rows); the bar
            covered ≥ 0.70 with n ≥ 30; the paired discordant counts (b = fix right & law wrong, c = the reverse) and the
            one-sided exact sign test per seed; meeting_seen (the train cache's truth row of the «dax» scene).
  20261101  NOT GRADABLE (the eye never saw the meeting) — printed, never graded.
Files under <out>/<ws>/: fm6.json (everything, with the per-item M6 rows the pool reads), fm6.txt (the lines),
law-gate-answers.json / fix-gate-answers.json (fresh `<item>` + older `older/<item>`: gate_alone's shape — the FIX file is what
the fixed LIFE's PARITY is read against) and law-held-answers.json / fix-held-answers.json.
--plant   THE CONTROL: the fix ALSO acts on MATURE one-word phrases; IDENTITY must then FAIL.
The tool never writes under a scored root, the glances root or a life's root.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
import types
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain.scene import cache as C          # noqa: E402  (the gate reads the caches and the truth; the organ never does)
from brain.scene import learners as Lr      # noqa: E402
from brain.scene import marks as M          # noqa: E402
from brain.scene import world as W          # noqa: E402
from genome import brain as B               # noqa: E402
from genome.machinery import parse_genome   # noqa: E402

_spec = importlib.util.spec_from_file_location("gate_alone", str(Path(__file__).resolve().parent / "gate_alone.py"))
GA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(GA)

GLANCES_ROOT = C.RUNS                                    # scene-organ-fm6: the caches redrawn under THIS code, «held» included
SCORED_ROOT = C.S1B1R_RUNS
OUT = Path("/data/dev/brain-runs/organ/gate-fm6")
LIFE_ROOTS = (Path("/data/dev/genome-lives"),)
# edit: Kimi K3 (kimi-code, builder lane kimi-w1, integrator hat), 2026-10-05 00:27 +0400 — the seat's ONE shared pinned window
# (PREREG-W1 + PREREG-SLEEP-IDLE): INNER_RUNS (the swarm-1003 root, now read as plain files only) joins the forbidden list beside RUNS.
FORBIDDEN_OUT = (C.S1B1R_RUNS, C.S1B1_RUNS, C.S1A_RUNS, C.SCENE_ORGAN_RUNS, C.FM6_RUNS, C.HEAR_RUNS, C.DRIVE_RUNS, C.INNER_RUNS, C.RUNS) + LIFE_ROOTS
LAW_LINE = GA.BRAIN_LINE
FIX_LINE = GA.BRAIN_LINE.replace("young 3;", "young 3 nearest;")
SETS = ("held", "fresh", "s1b1")
NEW_FIELDS = ("young_d", "point_rule")
POINT_DIGEST = ("hyp", "pos", "fix")
P_BAR, GAP_BAR, MIN_DISCORDANT = 1e-3, 0.10, 10
NOT_GRADABLE_SEEDS = (20261101,)


def cfg_of(line: str) -> Dict[str, object]:
    g = parse_genome((ROOT / "genome" / "ALPHA4.genome").read_text() + "\n" + line + "\n")
    return dict(g.declared["BRAIN"])


def refuse_out(out: Path, extra: Sequence[Path] = ()) -> None:
    o = Path(out).resolve()
    for r in tuple(FORBIDDEN_OUT) + tuple(extra):
        if o == Path(r).resolve() or o.is_relative_to(Path(r).resolve()):
            raise SystemExit(f"gate_fm6: --out {out} is under {r} — the gate never writes under a scored, glances or life root")


def plant(brain: "B.Brain") -> None:
    """THE CONTROL: the fix's nearest rule acts on ANY heard one-word phrase with a prototype (mature words too)."""
    L = brain.L

    def _planted(self, Z, phrase, rng):
        if len(phrase) != 1:
            return None
        j = self.index.get(phrase[0])
        st = (getattr(self, "reader", None) or {}).get("ear")
        if j is None or st is None or st.get("one_alone") is None:
            return None
        lam = st["lam"][st["one_alone"]]
        if lam is None or self.proto_w[j] <= 0:
            return None
        E = Z - self.prototype(int(j))[None, :]
        d = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", E, lam, E), 0.0))
        return Lr.pick(d, rng, "min"), d

    L._young_nearest = types.MethodType(_planted, L)


def binom_tail(b: int, n: int) -> Optional[float]:
    """One-sided exact sign test: P(X ≥ b), X ~ Bin(n, ½). None when n = 0."""
    if n <= 0:
        return None
    return float(sum(math.comb(n, k) for k in range(b, n + 1)) / 2 ** n)


def strip(a: Dict[str, object]) -> Dict[str, object]:
    """A young ask's answer without the pointing and the new fields: what must still be the law's."""
    out = {k: v for k, v in a.items() if k not in POINT_DIGEST and k != "raw"}
    raw = a.get("raw")
    if isinstance(raw, dict):
        out["raw"] = {k: v for k, v in raw.items() if k not in ("point",) + NEW_FIELDS}
    return out


def payload_of(mark: str, q: Dict[str, object], tr_rows, ts: int, split: str):
    if mark in GA.POINT_MARKS:
        return {"form": "point", "item": q["item_id"], "mark": mark, "phrase": list(q["phrase"]), "box": None, "word": None,
                "test_seed": ts}
    tgt = 0 if mark in GA.WHAT_MARKS else int(q["thing"])
    tr = tr_rows[split][int(q["row"])]
    t = tr["things"][tgt]
    return {"form": "what" if mark in GA.WHAT_MARKS else "say", "item": q["item_id"], "mark": mark, "phrase": [],
            "box": [int(t["top"]), int(t["left"]), int(t["side"])], "centroid": [float(v) for v in tr["centroids"][tgt]],
            "word": None, "test_seed": ts}


def is_young_point(law: "B.Brain", payload: Dict[str, object]) -> bool:
    ph = payload.get("phrase") or []
    if payload.get("form") != "point" or len(ph) != 1:
        return False
    j = law.L.index.get(ph[0])
    return j is not None and int(law.L.meetings[j]) < int(law.cfg["young"])


def grade_m6(K, law_ans, fix_ans, groot: Path, ws: int, tset: str, pre: str) -> Dict[str, object]:
    """M6 for the law and the fix on one test set: marks.grade_pointing's own rows over the set's m6 cache (the answers' `raw`,
    keyed `<pre><item>`); covered accuracy · n · chance · unheard per organ; the paired items (covered, gradable in both) and
    their discordants b (fix right, law wrong) and c (law right, fix wrong) with the one-sided exact sign p."""
    T6 = C.load_truth(C.cache_dir(groot, ws, "m6", tset))
    P6 = C.ScenePercepts(C.cache_dir(groot, ws, "m6", tset))

    def members_of(row: int):
        hs = P6.hypotheses(row)
        return [h.members for h in hs], [tuple(h.pos) for h in hs]

    rows = {}
    for who, ans in (("law", law_ans), ("fix", fix_ans)):
        A = {it["item_id"]: (ans.get(pre + it["item_id"]) or {}).get("raw") for it in K}
        rows[who] = M.grade_pointing(K, {k: v for k, v in A.items() if v is not None}, T6, members_of, "gaze")
    out: Dict[str, object] = {"n_items": len(K), "test_set": tset}
    for who in ("law", "fix"):
        cov = [r for r in rows[who] if r["gradable"] and r["covered"]]
        acc = (sum(r["correct"] for r in cov) / len(cov)) if cov else None
        out[who] = {"covered": acc, "n_covered": len(cov), "right": sum(r["correct"] for r in cov),
                    "chance_covered": (float(np.mean([r["chance"] for r in cov])) if cov else None),
                    "n_unheard": sum(1 for r in rows[who] if not r["gradable"])}
        out[who]["reads"] = ("UNDERPOWERED" if len(cov) < M.UNDERPOWERED_N else ("PASS" if acc >= M.BARS["M6"] else "FAIL"))
    pairs = [(rl, rf) for rl, rf in zip(rows["law"], rows["fix"]) if rl["item_id"] == rf["item_id"]
             and rl["gradable"] and rf["gradable"] and rl["covered"]]
    b = sum(1 for rl, rf in pairs if rf["correct"] and not rl["correct"])
    c = sum(1 for rl, rf in pairs if rl["correct"] and not rf["correct"])
    out.update({"paired_n": len(pairs), "b_fix_only": b, "c_law_only": c, "sign_p": binom_tail(b, b + c),
                "items": [{"item_id": rl["item_id"], "covered": rl["covered"], "gradable": rl["gradable"] and rf["gradable"],
                           "law": rl["correct"], "fix": rf["correct"], "chance": rl["chance"]}
                          for rl, rf in zip(rows["law"], rows["fix"])]})
    return out


# ------------------------------------------------------------------------------------------------ one seed
def run_seed(ws: int, groot: Path, sroot: Path, out: Path, do_plant: bool = False, cfg_over: Optional[Dict] = None,
             log=print) -> Dict[str, object]:
    t0, c0 = time.perf_counter(), time.process_time()
    law_cfg, fix_cfg = cfg_of(LAW_LINE), cfg_of(FIX_LINE)
    if cfg_over:                                       # the unit test's tiny life only (calibrate at a few scenes)
        law_cfg, fix_cfg = {**law_cfg, **cfg_over}, {**fix_cfg, **cfg_over}
    assert fix_cfg == {**law_cfg, "young_rule": "nearest"}, (law_cfg, fix_cfg)
    law, fix = B.Brain(law_cfg), B.Brain(fix_cfg)
    if do_plant:
        plant(fix)
    train = C.ScenePercepts(C.cache_dir(groot, ws, "train"))
    learn_diff = 0
    for i in range(len(train)):
        g, words = GA.glance_of(train, i), train.words(i)
        kw = dict(moment=f"sc{ws}t{i:06d}", scene=i, world_seed=ws)
        ra, rb = GA.canon(law.learn(g, words, **kw)), GA.canon(fix.learn(g, words, **kw))
        learn_diff += int(ra != rb)
    res: Dict[str, object] = {"world_seed": ws, "plant": bool(do_plant), "n_train": len(train), "learn_rows_differing": learn_diff,
                              "law_cfg": law_cfg, "fix_cfg": fix_cfg, "glances_root": str(groot), "scored_root": str(sroot),
                              "learn_cpu_s": time.process_time() - c0}
    trd = C.load_truth(C.cache_dir(groot, ws, "train"))
    if W.DAX_INDEX < len(trd):
        r = trd[W.DAX_INDEX]
        moon = [k for k, t in enumerate(r["things"]) if t["shape"] == W.DAX_SHAPE]
        res["meeting_seen"] = bool(moon) and any(f in moon for f in r["fix_thing"] if f is not None)
    else:
        res["meeting_seen"] = None
    sources = {"held": (groot / str(ws) / "held" / "questions.json", "held", False),
               "fresh": (sroot / str(ws) / "fresh" / "questions.json", "fresh", False),
               "s1b1": (sroot / str(ws) / "questions.json", "s1b1", True)}
    answers = {"law": {"gate": {}, "held": {}}, "fix": {"gate": {}, "held": {}}}
    ident: Dict[str, Dict[str, object]] = {}
    for sname in ("fresh", "s1b1", "held"):
        qpath, tset, older = sources[sname]
        Q = json.loads(qpath.read_text())
        ts = int(Q["test_seed"])
        for b in (law, fix):
            b.ask({"form": "begin", "set": tset, "test_seed": ts}, None)
        marks = GA.POINT_MARKS if older else GA.POINT_MARKS + GA.WHAT_MARKS + GA.SAY_MARKS
        P: Dict[str, "C.ScenePercepts"] = {}
        T: Dict[str, list] = {}
        blk = {"compared": 0, "equal": 0, "first": None, "young": 0, "young_equal": 0, "young_first": None,
               "acted": 0, "acted_outside_young": 0, "point_moved": 0, "per_mark": {}}
        for mark in marks:
            pm = blk["per_mark"].setdefault(mark, {"compared": 0, "equal": 0, "young": 0})
            for q in Q["questions"].get(mark, []):
                split, row = q["split"], int(q["row"])
                if split not in P:
                    P[split] = C.ScenePercepts(C.cache_dir(groot, ws, split, tset))
                    T[split] = C.load_truth(C.cache_dir(groot, ws, split, tset))
                g = GA.glance_of(P[split], row)
                p = payload_of(mark, q, T, ts, split)
                a, f = GA.canon(law.ask(p, g)), GA.canon(fix.ask(p, g))
                key = ("older/" if older else "") + q["item_id"]
                dest = "held" if sname == "held" else "gate"
                answers["law"][dest][key], answers["fix"][dest][key] = a, f
                acted = isinstance(f.get("raw"), dict) and "point_rule" in f["raw"]
                if is_young_point(law, p):
                    blk["young"] += 1
                    pm["young"] += 1
                    blk["acted"] += int(acted)
                    blk["point_moved"] += int((f.get("raw") or {}).get("point") != (a.get("raw") or {}).get("point"))
                    d = GA.first_diff(strip(a), strip(f), key)
                    blk["young_equal"] += int(d is None)
                    if d and blk["young_first"] is None:
                        blk["young_first"] = d
                    continue
                blk["acted_outside_young"] += int(acted)
                blk["compared"] += 1
                pm["compared"] += 1
                d = GA.first_diff(a, f, key)
                blk["equal"] += int(d is None)
                pm["equal"] += int(d is None)
                if d and blk["first"] is None:
                    blk["first"] = d
        blk["pass"] = (blk["compared"] > 0 and blk["compared"] == blk["equal"] and blk["young"] == blk["young_equal"]
                       and blk["acted_outside_young"] == 0)
        ident[sname] = blk
    res["identity"] = ident
    res["identity_pass"] = all(b["pass"] for b in ident.values())
    # -- M6 on held (the clauses) and on fresh / s1b1 (READINGS: DIAG-M6's positive control) --------------------
    Kh = json.loads((groot / str(ws) / "held" / "keys.json").read_text())["items"]["M6"]
    m6 = grade_m6(Kh, answers["law"]["held"], answers["fix"]["held"], groot, ws, "held", "")
    # edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:35 +0400 — the READINGS on the used sets, never a clause: DIAG-M6 read, on the
    # FRESH set, the law 21/27 (20261102) and 14/29 (20261103) and «nearest under the one-alone metric» 26/27 and 22/29; the
    # built rule must reproduce those numbers there, or it is not DIAG's rule (and a held PASS would be a reading of another fix)
    readings = {}
    for tset, kpath, pre in (("fresh", sroot / str(ws) / "fresh" / "keys.json", ""), ("s1b1", sroot / str(ws) / "keys.json", "older/")):
        K = json.loads(kpath.read_text())["items"]["M6"]
        r = grade_m6(K, answers["law"]["gate"], answers["fix"]["gate"], groot, ws, tset, pre)
        r.pop("items")
        readings[tset] = r
    res["M6_readings_used_sets"] = readings
    m6["bar"], m6["n_bar"] = M.BARS["M6"], M.UNDERPOWERED_N
    if ws in NOT_GRADABLE_SEEDS:
        m6["verdict"] = "NOT GRADABLE (as signed: at 20261101 the eye never saw the meeting)"
    elif res["meeting_seen"] is None:
        m6["verdict"] = "NOT GRADABLE (no «dax» meeting in this training stream)"
    elif res["meeting_seen"] is not True:
        m6["verdict"] = "NOT GRADABLE (the eye never saw the meeting)"
    else:
        m6["verdict"] = m6["fix"]["reads"]
    res["M6_held"] = m6
    res["cpu_s"], res["wall_s"] = time.process_time() - c0, time.perf_counter() - t0
    sub = Path(out) / str(ws)
    sub.mkdir(parents=True, exist_ok=True)
    tag = "planted" if do_plant else "fm6"
    (sub / f"{tag}.json").write_text(json.dumps(GA.canon(res), sort_keys=True, indent=1) + "\n")
    pre = "planted-" if do_plant else ""
    for who in ("law", "fix"):
        (sub / f"{pre}{who}-gate-answers.json").write_text(json.dumps(answers[who]["gate"], sort_keys=True) + "\n")
        (sub / f"{pre}{who}-held-answers.json").write_text(json.dumps(answers[who]["held"], sort_keys=True) + "\n")
    lines = seed_lines(res)
    (sub / f"{tag}.txt").write_text("\n".join(lines) + "\n")
    for l in lines:
        log(l)
    return res


def _f(v) -> str:
    return "—" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))


def seed_lines(res: Dict[str, object]) -> List[str]:
    ws = res["world_seed"]
    L = [f"GATE F-M6 (AMENDMENT 1 §2) · world seed {ws}" + (" · PLANTED CONTROL (the fix acts on mature one-word phrases)" if res["plant"] else "")
         + f" · IDENTITY {'PASS' if res['identity_pass'] else 'FAIL'}",
         f"  trained {res['n_train']} scenes, law and fix in lockstep · learn rows differing {res['learn_rows_differing']} · "
         f"meeting_seen {res['meeting_seen']}",
         "  IDENTITY (asks that are not a pointing on ONE young word, decided from the LAW's state: the whole answer equal)"]
    for s, b in res["identity"].items():
        L.append(f"    {s:6s} compared {b['compared']:5d} · equal {b['equal']:5d} · first {b['first'] or '—'}")
        L.append(f"           young one-word pointings {b['young']} (rule acted {b['acted']}, point moved {b['point_moved']}) · equal but "
                 f"the pointing and the new fields {b['young_equal']} · first {b['young_first'] or '—'} · rule acted outside them "
                 f"{b['acted_outside_young']} · {'PASS' if b['pass'] else 'FAIL'}")
    m = res["M6_held"]
    for who in ("law", "fix"):
        x = m[who]
        L.append(f"  M6 on held · {who:3s}: covered {_f(x['covered'])} (n {x['n_covered']} of {m['n_items']}; chance {_f(x['chance_covered'])}; "
                 f"unheard {x['n_unheard']}) · reads {x['reads']} (bar {m['bar']}, n ≥ {m['n_bar']})")
    L.append(f"  paired (covered, gradable in both) n {m['paired_n']} · b (fix right, law wrong) {m['b_fix_only']} · c (law right, fix wrong) "
             f"{m['c_law_only']} · one-sided exact sign p {_f(m['sign_p'])} (this seed alone; the gate's clause is POOLED: --pool)")
    L.append(f"  M6 clause at this seed: {m['verdict']}")
    for tset, r in (res.get("M6_readings_used_sets") or {}).items():
        L.append(f"  READING (not a clause) M6 on the used set {tset}: law {r['law']['right']}/{r['law']['n_covered']} = "
                 f"{_f(r['law']['covered'])} · fix {r['fix']['right']}/{r['fix']['n_covered']} = {_f(r['fix']['covered'])} · "
                 f"b {r['b_fix_only']} c {r['c_law_only']}")
    L.append(f"  cpu {res['cpu_s']:.1f} s · wall {res['wall_s']:.1f} s")
    return L


# ------------------------------------------------------------------------------------------------ the pool
def pool(dirs: Sequence[Path], log=print) -> Dict[str, object]:
    recs = [json.loads((Path(d) / "fm6.json").read_text()) for d in dirs]
    seeds = [r["world_seed"] for r in recs]
    if len(set(seeds)) != len(seeds):
        raise SystemExit(f"--pool reads two DIFFERENT seeds, got {seeds}")
    use = [r for r in recs if r["world_seed"] not in NOT_GRADABLE_SEEDS and r["meeting_seen"] is True]
    items = [(r["world_seed"], it) for r in use for it in r["M6_held"]["items"] if it["covered"] and it["gradable"]]
    n = len(items)
    law = sum(it["law"] for _s, it in items)
    fx = sum(it["fix"] for _s, it in items)
    b = sum(1 for _s, it in items if it["fix"] and not it["law"])
    c = sum(1 for _s, it in items if it["law"] and not it["fix"])
    p = binom_tail(b, b + c)
    gap = ((fx - law) / n) if n else None
    ok = gap is not None and gap >= GAP_BAR and p is not None and p < P_BAR
    out = {"seeds": seeds, "pooled_seeds": [r["world_seed"] for r in use], "n": n, "law_covered": (law / n) if n else None,
           "fix_covered": (fx / n) if n else None, "gap": gap, "b": b, "c": c, "p": p,
           "identity": {str(r["world_seed"]): r["identity_pass"] for r in recs},
           "m6_per_seed": {str(r["world_seed"]): r["M6_held"]["verdict"] for r in recs},
           "verdict": "PASS" if ok else "FAIL"}
    lines = [f"GATE F-M6 · POOLED over {out['pooled_seeds']} (of {seeds}; 20261101 and unseen meetings are not pooled)",
             f"  covered items {n} · law {_f(out['law_covered'])} · fix {_f(out['fix_covered'])} · gap {_f(gap)} (bar ≥ {GAP_BAR}) · "
             f"discordant b {b} / c {c} (p < {P_BAR} needs ≥ {MIN_DISCORDANT}, all for the fix) · one-sided exact sign p "
             f"{'—' if p is None else f'{p:.3g}'} → {out['verdict']}",
             f"  the other clauses, per seed: IDENTITY {out['identity']} · M6 {out['m6_per_seed']}"]
    for l in lines:
        log(l)
    out["lines"] = lines
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--world-seed", type=int)
    ap.add_argument("--glances-root", type=Path, default=GLANCES_ROOT)
    ap.add_argument("--scored-root", type=Path, default=SCORED_ROOT)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--plant", action="store_true")
    ap.add_argument("--pool", nargs=2, type=Path)
    a = ap.parse_args(argv)
    if a.pool:
        res = pool(a.pool)
        return 0 if res["verdict"] == "PASS" else 1
    if a.world_seed not in W.WORLD_SEEDS:
        raise SystemExit(f"no such world seed {a.world_seed} (the scored ones: {W.WORLD_SEEDS})")
    refuse_out(a.out, (a.scored_root, a.glances_root))
    res = run_seed(a.world_seed, a.glances_root, a.scored_root, a.out, do_plant=a.plant)
    if a.plant:
        return 0 if not res["identity_pass"] else 1          # the control must FAIL IDENTITY
    return 0 if res["identity_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
