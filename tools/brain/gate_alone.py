"""tools/brain/gate_alone.py — THE GATE «BRAIN ALONE» (docs/brain/body/INTERFACE-BRAIN-ORGAN.md §3; PREREG-BRAIN-IN-BODY §2).

edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:52 +0400 — new tool.
edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:49 +0400 — CORRECTION (#50): the «20:52» above was TYPED, not read from `date`;
the tool was written between the 20:26 and the 20:36 clock reads (its first run, the price, at ~20:36; first commit 6fa0b41 at
20:38). The «20:44» note below was likewise typed before the 20:44 read (that edit was made between 20:39 and 20:44).
Docstring-only correction.

The organ (genome/brain.py's Brain, configured by the genome's own BRAIN line as machinery.parse_genome reads it) is fed the
scored run's training canvases IN ORDER through the SAME call the mind makes — `Brain.learn(glance, words, moment=, scene=,
world_seed=)`, the glance rebuilt from a cache row as genome.gaze.glances returns it (`feats` = the located glances then the
coarse one, `fix` = the located cells) — then answers the scored run's FRESH questions through `Brain.ask(payload, glance)`
with the payload a sitting's ask row carries (INTERFACE §2: `point` a phrase; `what` / `say` a pointing `box` + `centroid`
taken from the canvas's truth row — the parent's gesture). Each answer's `raw` must EQUAL the scored
`answers_10000.json` item by item: the `point` block (M1, M2a, M6, M3) and the LAW road (M2b, NAME, SPEAK, SPEAK2, DECLINE).
Per seed and per mark: items compared · items equal · the first difference. A difference is a JOIN DEFECT.

Roots (the seat's 20:3x word): glances from --glances-root (default /data/dev/brain-runs/organ/scene, the caches REDRAWN under
this tree's code and proven byte-identical to the scored ones); questions, keys and the scored answers from --scored-root
(default /data/dev/brain-runs/scene-s1b1r — read as plain JSON, never written). Outputs under --out (default
/data/dev/brain-runs/organ/gate-alone/).

  --plant            THE CONTROL: one word of one training utterance changed (scene PLANT_SCENE: its first word → another
                     word of the heard vocabulary) — the gate must FAIL.
  --limit N          price: learn N scenes only, no sitting; prints the projected cost of a whole seed.
  --save             after the sitting: save the 10,000-scene state, print its size and write time, reload, hash-compare.

edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:44 +0400 — PREREG-BRAIN-IN-BODY (signed, 12bdea6): the gate also compares the
OLDER set's POINTING answers (M1, M2a, M3, M6 of test seeds 2026120x, caches <glances-root>/<ws>/cache/<split>) against
<scored-root>/<ws>/arms/A-RW/answers_10000.json's `answers`; M4's reading follows §3 row M4a (citations among ≥ 2-hypothesis
episodes; CARRY by marks.hyp_label over fix_thing; the null `m4-null:<k>`).

Beside the verdict (READINGS, the truth read here only, never in the organ): M5 on the final learner — (a) every ordered pair
of two different mature words of one world type flagged; (b) M1 + M3 phrases falsely flagged; (c) the six held-out
colour × shape pairs — and M4a's ceiling as PREREG §3 grades it (m4_reading).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain.scene import cache as C          # noqa: E402  (the gate reads the caches and the truth; the organ never does)
from brain.scene import marks as M          # noqa: E402
from brain.scene import world as W          # noqa: E402
from brain.world.seeds import substream     # noqa: E402
from genome import brain as B               # noqa: E402
from genome.machinery import parse_genome   # noqa: E402

GLANCES_ROOT = Path("/data/dev/brain-runs/scene-organ")   # edit: Claude (Fable 5.1, the seat), 2026-09-28 20:49 +0400 — the tree's fresh root (cache.RUNS); the first redraw at organ/scene was drawn before cache.py's RUNS moved
SCORED_ROOT = Path("/data/dev/brain-runs/scene-s1b1r")
OUT = Path("/data/dev/brain-runs/organ/gate-alone")
TSET = "fresh"
RP = 10_000
BRAIN_LINE = ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3; "
              "calibrate at 250 500 1000 2000 5000 10000 and before a sitting; replay none; hears scene")
POINT_MARKS = ("M1", "M2a", "M6", "M3")
WHAT_MARKS = ("M2b", "NAME")
SAY_MARKS = ("SPEAK", "SPEAK2", "DECLINE")
PLANT_SCENE = 100
M4_TWIN_DRAWS = 20


def brain_cfg() -> Dict[str, object]:
    """The BRAIN line read by the genome's own parser (the line the genomes carry, INTERFACE §1)."""
    g = parse_genome((ROOT / "genome" / "ALPHA4.genome").read_text() + "\n" + BRAIN_LINE + "\n")
    return dict(g.declared["BRAIN"])


def glance_of(p: "C.ScenePercepts", row: int) -> Dict[str, object]:
    """A cache row → genome.gaze.glances's own shape: `feats` = the located glances then the coarse one (row 4 of the cache),
    `fix` = the located cells."""
    fix, loc = p.located(row)
    g = p.glances.glances(row)
    return {"feats": [np.asarray(v, dtype=np.float64) for v in loc] + [np.asarray(g[4], dtype=np.float64)],
            "fix": [tuple(c) for c in fix], "windows": [], "residual": [None] * (len(fix) + 1)}


def canon(o):
    """One JSON round-trip (object keys become strings, tuples lists, Infinity stays a float)."""
    return json.loads(json.dumps(o, sort_keys=True, default=_np))


def _np(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def first_diff(a, b, path: str = "") -> Optional[str]:
    """The first path where a and b differ (a NaN equals a NaN; inf equals the same inf), else None."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return f"{path}.{k} (only in {'scored' if k in a else 'brain'})"
            d = first_diff(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path} (length {len(a)} vs {len(b)})"
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return None
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))
                                       and not isinstance(a, bool) and not isinstance(b, bool)):
        return f"{path} ({a!r} vs {b!r})"
    return None if a == b else f"{path} ({a!r} vs {b!r})"


def world_type_of_key(key: str) -> str:
    """NAME's `name` block: the organ keys a forced name by its LEARNED type's words («big|small»); the world's type is read
    here (the gate may; the organ may not)."""
    ts = {W.word_type(w) for w in key.split("|")}
    return ts.pop() if len(ts) == 1 else "mixed:" + key


# ------------------------------------------------------------------------------------------------ one seed
def run_seed(ws: int, groot: Path, sroot: Path, out: Path, plant: bool = False, limit: Optional[int] = None,
             save: bool = False, log=print) -> Dict[str, object]:
    t0, c0 = time.perf_counter(), time.process_time()
    cfg = brain_cfg()
    rec_scored = json.loads((sroot / str(ws) / TSET / "arms" / "A-RW-R" / "record.json").read_text())
    if float(rec_scored["eps"]) != float(cfg["eps"]) or float(rec_scored["lr"]) != float(cfg["lr"]):
        raise SystemExit(f"the BRAIN line (lr {cfg['lr']}, eps {cfg['eps']}) is not the scored arm's "
                         f"(lr {rec_scored['lr']}, eps {rec_scored['eps']})")
    if list(cfg["calibrate_at"]) != list(W.READING_POINTS):
        raise SystemExit(f"calibrate at {cfg['calibrate_at']} is not the scored reading points {W.READING_POINTS}")
    train = C.ScenePercepts(C.cache_dir(groot, ws, "train"))
    n_train = len(train) if limit is None else int(limit)
    brain = B.Brain(cfg)
    planted = None
    none_counts = {"True": 0, "False": 0, "None": 0}
    calibrated_at = []
    for i in range(n_train):
        words = train.words(i)
        if plant and i == PLANT_SCENE:
            vocab = sorted(set(w for k in range(PLANT_SCENE) for w in train.words(k)))
            other = [w for w in vocab if w != words[0]][0]
            planted = {"scene": i, "was": list(words), "now": [other] + list(words[1:])}
            words = planted["now"]
        r = brain.learn(glance_of(train, i), words, moment=f"sc{ws}t{i:06d}", scene=i, world_seed=ws)
        none_counts[str(r["none"])] += 1
        if r["calibrated"]:
            calibrated_at.append(i + 1)
            log(f"[gate {ws}] calibrated at {i + 1} · cpu {time.process_time() - c0:.1f} s")
    learn_cpu, learn_wall = time.process_time() - c0, time.perf_counter() - t0
    res: Dict[str, object] = {"world_seed": ws, "plant": planted, "n_train": n_train, "calibrated_at": calibrated_at,
                              "learn_none": none_counts, "learn_cpu_s": learn_cpu, "learn_wall_s": learn_wall,
                              "glances_root": str(groot), "scored_root": str(sroot), "cfg": cfg}
    if limit is not None:
        res["projected_learn_cpu_s"] = learn_cpu / max(n_train, 1) * len(train)
        log(f"[gate {ws}] PRICE: {n_train} scenes learned in {learn_cpu:.1f} s cpu ({learn_wall:.1f} s wall) → "
            f"a whole seed ({len(train)} scenes) ≈ {res['projected_learn_cpu_s']:.0f} s cpu")
        return res
    # -- the sitting ----------------------------------------------------------------------------------
    Q = json.loads((sroot / str(ws) / TSET / "questions.json").read_text())
    S = json.loads((sroot / str(ws) / TSET / "arms" / "A-RW-R" / f"answers_{RP:05d}.json").read_text())
    ts = int(Q["test_seed"])
    begin = brain.ask({"form": "begin", "set": TSET, "test_seed": ts}, None)
    splits = C.test_splits(TSET)
    P = {s: C.ScenePercepts(C.cache_dir(groot, ws, s, TSET)) for s in splits}
    T = {s: C.load_truth(C.cache_dir(groot, ws, s, TSET)) for s in splits}
    table: Dict[str, Dict[str, object]] = {}
    pin = {"compared": 0, "equal": 0, "mismatches": []}
    answers: Dict[str, object] = {}
    misuse_flags: List[str] = []
    name_block = {"compared": 0, "equal": 0, "first": None}
    for mark in POINT_MARKS + WHAT_MARKS + SAY_MARKS:
        blk = {"compared": 0, "equal": 0, "first": None, "scored_n": 0}
        ref = S["point"] if mark in POINT_MARKS else S["roads"]["LAW"]
        blk["scored_n"] = sum(1 for k in ref if k.startswith(mark + ":"))
        for q in Q["questions"].get(mark, []):
            item, row, split = q["item_id"], int(q["row"]), q["split"]
            p = P[split]
            g = glance_of(p, row)
            if mark in POINT_MARKS:
                payload = {"form": "point", "item": item, "mark": mark, "phrase": list(q["phrase"]), "box": None, "word": None,
                           "test_seed": ts}
            else:
                tgt = 0 if mark in WHAT_MARKS else int(q["thing"])
                tr = T[split][row]
                t = tr["things"][tgt]
                box = [int(t["top"]), int(t["left"]), int(t["side"])]
                cent = [float(v) for v in tr["centroids"][tgt]]
                payload = {"form": "what" if mark in WHAT_MARKS else "say", "item": item, "mark": mark, "phrase": [],
                           "box": box, "centroid": cent, "word": None, "test_seed": ts}
                hyps = B.things_in_view(g)[0]
                h = B.pointer_hypothesis(box, cent, g["fix"], hyps)
                pin["compared"] += 1
                if h == q.get("hyp"):
                    pin["equal"] += 1
                else:
                    pin["mismatches"].append({"item": item, "brain": h, "scored": q.get("hyp")})
            a = canon(brain.ask(payload, g))
            answers[item] = a
            if a.get("kind") == "misuse":
                misuse_flags.append(item)
            mine = a.get("raw")
            theirs = canon(ref.get(item))
            if mark == "NAME" and isinstance(mine, dict) and isinstance(mine.get("name"), dict):
                # the organ's learned types → the world's (read here): then `name` compares like with like
                mapped = {world_type_of_key(k): v for k, v in mine["name"].items()}
                name_block["compared"] += 1
                nd = first_diff(theirs.get("name"), mapped, f"{item}.name")
                name_block["equal"] += int(nd is None)
                if nd and name_block["first"] is None:
                    name_block["first"] = nd
                mine = {**mine, "name": mapped}
            blk["compared"] += 1
            d = first_diff(theirs, mine, item)
            if d is None:
                blk["equal"] += 1
            elif blk["first"] is None:
                blk["first"] = d
        table[mark] = blk
    # -- the OLDER set's POINTING (PREREG §2, signed 12bdea6): M1, M2a, M3, M6 of test seeds 2026120x against
    #    arms/A-RW/answers_10000.json's `answers` (pointing is road-free; A-RW-R trains as A-RW); its what / say are no reference
    Qo = json.loads((sroot / str(ws) / "questions.json").read_text())
    So = json.loads((sroot / str(ws) / "arms" / "A-RW" / f"answers_{RP:05d}.json").read_text())["answers"]
    tso = int(Qo["test_seed"])
    brain.ask({"form": "begin", "set": "s1b1", "test_seed": tso}, None)
    Po: Dict[str, "C.ScenePercepts"] = {}
    older: Dict[str, Dict[str, object]] = {}
    for mark in POINT_MARKS:
        blk = {"compared": 0, "equal": 0, "first": None, "scored_n": sum(1 for k in So if k.startswith(mark + ":"))}
        for q in Qo["questions"].get(mark, []):
            item, row, split = q["item_id"], int(q["row"]), q["split"]
            if split not in Po:
                Po[split] = C.ScenePercepts(C.cache_dir(groot, ws, split, "s1b1"))
            g = glance_of(Po[split], row)
            a = canon(brain.ask({"form": "point", "item": item, "mark": mark, "phrase": list(q["phrase"]), "box": None,
                                 "word": None, "test_seed": tso}, g))
            answers["older/" + item] = a
            if a.get("kind") == "misuse":
                misuse_flags.append("older/" + item)
            blk["compared"] += 1
            d = first_diff(canon(So.get(item)), a.get("raw"), "older/" + item)
            if d is None:
                blk["equal"] += 1
            elif blk["first"] is None:
                blk["first"] = d
        older[mark] = blk
    end = brain.ask({"form": "end"}, None)
    # -- the verdict ----------------------------------------------------------------------------------
    blocks = list(table.values()) + list(older.values())
    total_c = sum(b["compared"] for b in blocks)
    total_e = sum(b["equal"] for b in blocks)
    counts_ok = all(b["compared"] == b["scored_n"] and b["compared"] > 0 for b in blocks)
    summ = {"brain": canon(brain.L.summary()), "scored": canon(rec_scored["reading_points"][str(RP)]["summary"])}
    summ_diff = first_diff(summ["scored"], summ["brain"], "summary")
    ok = counts_ok and total_c > 0 and total_c == total_e and not pin["mismatches"] and summ_diff is None
    res.update({"begin": begin, "end": end, "table": table, "older": older, "pin": {**pin, "mismatches": pin["mismatches"][:20],
                                                                        "n_mismatches": len(pin["mismatches"])},
                "name_forced_mapped": name_block, "misuse_flags": misuse_flags, "summary_diff": summ_diff,
                "compared": total_c, "equal": total_e, "counts_ok": counts_ok,
                "verdict": "PASS" if ok else "FAIL", "types": [list(t) for t in brain.types()]})
    # -- the readings: M5 and M4 (truth read here only) -----------------------------------------------
    res["M5"] = m5_reading(brain, Q)
    res["M4"] = m4_reading(brain, ws, train, C.load_truth(C.cache_dir(groot, ws, "train")))
    if save:
        res["save"] = save_reading(brain, out / str(ws) / ("brain-planted" if plant else "brain"))
    res["cpu_s"], res["wall_s"] = time.process_time() - c0, time.perf_counter() - t0
    sub = out / str(ws)
    sub.mkdir(parents=True, exist_ok=True)
    tag = "planted" if plant else "gate"
    (sub / f"{tag}.json").write_text(json.dumps(canon(res), sort_keys=True, indent=1) + "\n")
    (sub / f"{tag}-answers.json").write_text(json.dumps(answers, sort_keys=True) + "\n")
    lines = table_lines(res)
    (sub / f"{tag}.txt").write_text("\n".join(lines) + "\n")
    for l in lines:
        log(l)
    return res


def table_lines(res: Dict[str, object]) -> List[str]:
    ws = res["world_seed"]
    L = [f"GATE «BRAIN ALONE» · world seed {ws}" + (f" · PLANTED CONTROL {res['plant']}" if res.get("plant") else "")
         + f" · verdict {res['verdict']}",
         f"  compared {res['compared']} · equal {res['equal']} · counts equal to the scored file's: {res['counts_ok']} · "
         f"learner.summary() vs the scored record: {'equal' if res['summary_diff'] is None else res['summary_diff']}",
         f"  pointer pin (M2b/NAME/SPEAK/SPEAK2/DECLINE vs questions.json hyp): compared {res['pin']['compared']} · "
         f"equal {res['pin']['equal']} · mismatches {res['pin']['n_mismatches']}",
         f"  {'mark':8s} {'compared':>9s} {'equal':>7s} {'scored n':>9s}  first difference"]
    for mark, b in res["table"].items():
        L.append(f"  {mark:8s} {b['compared']:9d} {b['equal']:7d} {b['scored_n']:9d}  {b['first'] or '—'}")
    L.append("  the OLDER set's pointing (test seeds 2026120x) vs scene-s1b1r/<ws>/arms/A-RW/answers_10000.json:")
    for mark, b in res["older"].items():
        L.append(f"  {mark:8s} {b['compared']:9d} {b['equal']:7d} {b['scored_n']:9d}  {b['first'] or '—'}")
    nb = res["name_forced_mapped"]
    L.append(f"  NAME.name (the organ's learned-type keys mapped to the world's types, here): compared {nb['compared']} · "
             f"equal {nb['equal']} · first {nb['first'] or '—'}")
    L.append(f"  answers flagged misuse (M5) among these items: {len(res['misuse_flags'])} · learn «none» {res['learn_none']} · "
             f"calibrated at {res['calibrated_at']} · begin {res['begin']['calibrated']}")
    m5 = res["M5"]
    L.append(f"  M5 (a) same-world-type ordered pairs flagged {m5['a']['flagged']}/{m5['a']['n']} = {m5['a']['share']} · "
             f"(b) M1+M3 phrases falsely flagged {m5['b']['flagged']}/{m5['b']['n']} = {m5['b']['share']} · "
             f"(c) held-out pairs flagged {m5['c']['flagged']}/{m5['c']['n']} (M3 phrases of them {m5['c']['m3_flagged']}/"
             f"{m5['c']['m3_n']}) · ear types {m5['types']}")
    m4 = res["M4"]
    L.append(f"  M4a (PREREG §3, ≥ 2 hypotheses): cited {m4['n_cited']} · EXIST {m4['exist']} · CARRY {m4['carry']} · null (20 draws, "
             f"m4-null:<k>) median {m4['null_median']} p95 {m4['null_p95']} · reads {m4['reads']} (bar CARRY ≥ 0.90 and > p95) · "
             f"the rule's base rate over all ≥ 2-hypothesis attributed episodes {m4['base_carry']} · cited fix ≠ cache "
             f"{m4['fix_join_mismatches']}")
    for w, pw in m4["per_word"].items():
        L.append(f"    {w:9s} {pw['kind']:8s} episodes {pw['episodes']:5d} · citable (≥ 2 hyps) {pw['citable']:5d} · cited "
                 f"{pw['cited']} · exist {pw['exist']} · carry {pw['carry']} · base {pw['base_carry']}")
    if res.get("save"):
        s = res["save"]
        L.append(f"  STATE at {res['n_train']} scenes: {s['bytes_npz']} B npz + {s['bytes_json']} B json = {s['bytes']} B · "
                 f"write {s['write_s']:.2f} s · load {s['load_s']:.2f} s · hash round-trip {s['hash_equal']}")
    L.append(f"  cpu {res['cpu_s']:.1f} s · wall {res['wall_s']:.1f} s")
    return L


# ------------------------------------------------------------------------------------------------ readings
def m5_reading(brain: "B.Brain", Q: Dict[str, object]) -> Dict[str, object]:
    mature = brain.L.mature_words()
    pairs = [(a, b) for a in mature for b in mature if a != b and a in W.VOCAB and b in W.VOCAB
             and W.word_type(a) == W.word_type(b)]
    fa = sum(1 for a, b in pairs if brain.misuse([a, b]) is not None)
    phr = [q for m in ("M1", "M3") for q in Q["questions"].get(m, [])]
    fb = [q["item_id"] for q in phr if brain.misuse(q["phrase"]) is not None]
    held = [(c, s) for s, c in W.HELDOUT] + [(s, c) for s, c in W.HELDOUT]
    fc = sum(1 for a, b in held if brain.misuse([a, b]) is not None)
    hs = {frozenset(p) for p in W.HELDOUT}
    m3h = [q for q in Q["questions"].get("M3", []) if any(frozenset((x, y)) in hs for x in q["phrase"] for y in q["phrase"] if x != y)]
    fm3 = sum(1 for q in m3h if brain.misuse(q["phrase"]) is not None)
    return {"types": [list(t) for t in brain.types()], "mature": mature,
            "a": {"n": len(pairs), "flagged": fa, "share": (fa / len(pairs)) if pairs else None},
            "b": {"n": len(phr), "flagged": len(fb), "share": (len(fb) / len(phr)) if phr else None, "items": fb[:20]},
            "c": {"n": len(held), "flagged": fc, "pairs": [list(p) for p in W.HELDOUT], "m3_n": len(m3h), "m3_flagged": fm3}}


def m4_reading(brain: "B.Brain", ws: int, train: "C.ScenePercepts", truth: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """M4's ceiling as PREREG §3 row M4a grades it (signed 12bdea6), on the rung-1 learner: every word the parent said, asked
    «why»; EXIST = each cited moment is a training moment whose utterance carries the word (a wiring pin); CARRY = the cited
    hypothesis' thing — marks.hyp_label over the truth row's fix_thing of the cited hypothesis' member cells (M1's own rule;
    no thing = not CARRY) — truly has the word's property (world.word_true_of); pooled over the words. THE NULL: 20 draws,
    draw k: each cited episode's hypothesis replaced by one drawn uniformly among that episode's `hyps`, generator
    substream(ws, "m4-null:<k>"), in citation order (the words in sorted order, each word's citations in the answer's order);
    the bar reads CARRY ≥ 0.90 and above the draws' 95th percentile (grade_life.py's percentile rule). Beside: the share of
    ALL of a word's attributed ≥ 2-hypothesis episodes that carry (the rule's own base rate), and, per word, the citable
    counts. The cited `fix` must equal the cache's cells for that scene (the join)."""
    import collections
    words = sorted(set(w for i in range(brain.n_learned) for w in train.words(i)))

    def carries(w: str, scene: int, members: Sequence[int]) -> bool:
        tr = truth[scene]
        lab = M.hyp_label(collections.Counter(tr["fix_thing"][m] for m in members if tr["fix_thing"][m] is not None))
        return lab is not None and w in W.VOCAB and W.word_true_of(w, M.things_of(tr)[lab])

    per: Dict[str, Dict[str, object]] = {}
    cited_all = []                           # (word, scene, hyps) in citation order, for the null
    n_cited = n_exist = n_carry = 0
    fix_join_bad = 0
    base_n = base_hit = 0
    for w in words:
        a = brain.why(w)
        pool = [e for e in brain.episodes.get(w, []) if len(brain.canvas[int(e[0])][1]) >= 2]
        ph = sum(int(carries(w, brain.scenes[int(e[0])], brain.canvas[int(e[0])][1][int(e[1])])) for e in pool)
        base_n += len(pool)
        base_hit += ph
        row = {"kind": a["kind"], "citable": len(pool), "episodes": len(brain.episodes.get(w, [])),
               "base_carry": (ph / len(pool)) if pool else None, "cited": 0, "exist": 0, "carry": None}
        if a["kind"] == "because":
            ex = ca = 0
            for e in a["episodes"]:
                sc = int(e["scene"])
                ex += int(w in train.words(sc) and e["moment"] == f"sc{ws}t{sc:06d}")
                fix_c, _loc = train.located(sc)
                fix_join_bad += int([list(c) for c in fix_c] != e["fix"])
                ca += int(carries(w, sc, e["hyps"][int(e["hyp"])]))
                cited_all.append((w, sc, e["hyps"]))
            row.update({"cited": len(a["episodes"]), "exist": ex, "carry": ca / len(a["episodes"])})
            n_cited, n_exist, n_carry = n_cited + len(a["episodes"]), n_exist + ex, n_carry + ca
        per[w] = row
    null = []
    for k in range(1, 21):
        rng = substream(ws, f"m4-null:{k}")
        hit = 0
        for w, sc, hyps in cited_all:
            h = int(rng.integers(len(hyps)))
            hit += int(carries(w, sc, hyps[h]))
        null.append(hit / len(cited_all) if cited_all else None)
    nv = sorted(v for v in null if v is not None)
    p95 = nv[min(len(nv) - 1, int(math.ceil(0.95 * len(nv))) - 1)] if nv else None
    carry = (n_carry / n_cited) if n_cited else None
    return {"n_cited": n_cited, "exist": (n_exist / n_cited) if n_cited else None, "carry": carry, "null": null,
            "null_p95": p95, "null_median": nv[len(nv) // 2] if nv else None,
            "base_carry": (base_hit / base_n) if base_n else None, "fix_join_mismatches": fix_join_bad,
            "reads": ("PASS" if carry is not None and carry >= 0.90 and p95 is not None and carry > p95 else "FAIL")
            if n_cited else "NOT GRADABLE", "per_word": per}


def save_reading(brain: "B.Brain", base: Path) -> Dict[str, object]:
    base.parent.mkdir(parents=True, exist_ok=True)
    h0 = brain.state_hash()
    t = time.perf_counter()
    brain.save(base)
    write_s = time.perf_counter() - t
    t = time.perf_counter()
    b2 = B.Brain.load(base, brain.cfg)
    load_s = time.perf_counter() - t
    npz, js = Path(str(base) + ".npz"), Path(str(base) + ".json")
    return {"bytes_npz": npz.stat().st_size, "bytes_json": js.stat().st_size, "bytes": npz.stat().st_size + js.stat().st_size,
            "write_s": write_s, "load_s": load_s, "hash_equal": b2.state_hash() == h0, "hash": h0}


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--world-seed", type=int, required=True)
    ap.add_argument("--glances-root", type=Path, default=GLANCES_ROOT)
    ap.add_argument("--scored-root", type=Path, default=SCORED_ROOT)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--plant", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--save", action="store_true")
    a = ap.parse_args(argv)
    if a.world_seed not in W.WORLD_SEEDS:
        raise SystemExit(f"no such world seed {a.world_seed} (the scored ones: {W.WORLD_SEEDS})")
    if Path(a.out).resolve().is_relative_to(Path(a.scored_root).resolve()):
        raise SystemExit("the gate never writes under the scored root")
    res = run_seed(a.world_seed, a.glances_root, a.scored_root, a.out, plant=a.plant, limit=a.limit, save=a.save)
    if a.limit is not None:
        return 0
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
