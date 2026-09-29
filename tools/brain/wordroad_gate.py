#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-29 13:22 +0400 — new tool: THE READER of PREREG-WORD-ROAD's gate (§4), written and pinned
# before the read (tests/tools/test_wordroad_gate.py).
"""tools/brain/wordroad_gate.py --runs DIR [--seeds …] [--null-seed 20261102] [--nulls 10] --out DIR

Reads the gate's replays (PREREG-WORD-ROAD §3) and writes the marks of §4. It replays nothing and runs no mind.

  <runs>/<ws>/off/   journal.jsonl · timings.jsonl · counters.jsonl   (the twin genome as it stands)
  <runs>/<ws>/on/    the same three                                   (the twin genome plus the HEAR line)
  <runs>/<ws>/i1-twin.exit · i1-brain.exit                            (creature.replay --against: 0 = every row equal)
  <runs>/<ws>/grade-off/grade.json · grade-on/grade.json              (tools/brain/grade_life.py --label twin, unchanged)
  <runs>/<null seed>/null-<k>/life/ (a made tape) · null-<k>/on/journal.jsonl · null-<k>/GENOME.genome

THE RULES THIS READER APPLIES (each is the PREREG's, or is said here because the PREREG leaves it to the reader):
  · a pointing is RIGHT when it names a hypothesis whose fixations fall mostly on the target (marks.hyp_label); «none»
    (no hypothesis named) and «unheard» are NOT right — in both arms of every pair. No forced draw is made here.
  · «the shape word alone» = the answer's own `scores_by_word`, summed over the phrase's SHAPE words in phrase order (the
    world's types are the reader's, brain/scene/world.py:word_type); «none» when the top sum is <= 0; an exact tie by the item's
    own generator (marks.tie_rng(test_seed, item)) — the organs' road's own three lines (creature/organs_road.py:answer_point).
  · the NEEDED items: tests 1 and 3, both test sets, the target covered by the gaze, 2 or 3 things, the phrase holds a size
    or colour word, and another thing of the scene has the target's shape.
  · K reads the GRADER's own `correct` of each arm's grade.json (its forced reading of «none», as the record's values were read).
A presence count stands beside every rate and every zero."""
from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain.scene import marks as M           # noqa: E402
from brain.scene import world as W           # noqa: E402
from creature import replay as RP            # noqa: E402
from tools.brain import grade_life as G      # noqa: E402

LIVES = Path("/data/dev/genome-lives")
SEEDS = (20261101, 20261102, 20261103)
TSETS = ("fresh", "s1b1")
MASK = ("words", "words_refused")            # §1.10: the keys the line adds to a canvas row
BARS = {"A": 1.0, "P_gap": 0.10, "P_p": 1e-3, "K": -0.05, "K2": -0.05, "C": 1.5, "words": 14}
COST_SCENES = (9000, 10000)


class GateError(Exception):
    pass


# ================================================================================================ arithmetic
def sign_p(f: int, u: int) -> float:
    """The exact one-sided sign test: P(X >= f) for X ~ Binomial(f + u, 1/2). No discordant pair → 1.0."""
    m = int(f) + int(u)
    if m == 0:
        return 1.0
    return sum(math.comb(m, k) for k in range(int(f), m + 1)) / float(2 ** m)


def pb_tail(ps: Sequence[float], k: int) -> float:
    """P(at least k right) when item i is right with probability ps[i], independently (Poisson-binomial, exact)."""
    d = np.zeros(len(ps) + 1)
    d[0] = 1.0
    for p in ps:
        d[1:] = d[1:] * (1.0 - p) + d[:-1] * p
        d[0] *= (1.0 - p)
    return float(d[int(k):].sum()) if k <= len(ps) else 0.0


def paired(a: Sequence[bool], b: Sequence[bool]) -> Dict[str, object]:
    """a against b on the same items: n, both rates, the pairs a-only (f) and b-only (u), a − b, its standard error, and
    the exact one-sided sign tests both ways."""
    if len(a) != len(b):
        raise GateError(f"paired: {len(a)} against {len(b)} items")
    n = len(a)
    f = sum(1 for x, y in zip(a, b) if x and not y)
    u = sum(1 for x, y in zip(a, b) if y and not x)
    if n == 0:
        return {"n": 0, "a": None, "b": None, "f": 0, "u": 0, "diff": None, "se": None, "p_a_higher": None, "p_a_lower": None}
    diff = (f - u) / n
    se = math.sqrt(max((f + u) / n - diff * diff, 0.0) / n)
    return {"n": n, "a": sum(map(bool, a)) / n, "b": sum(map(bool, b)) / n, "f": f, "u": u, "diff": diff, "se": se,
            "p_a_higher": sign_p(f, u), "p_a_lower": sign_p(u, f)}


def repoint(by_word: Dict[str, List[float]], phrase: Sequence[str], keep: Sequence[str],
            tie: Callable[[int], int]) -> Optional[int]:
    """The organs' road's own pointing for the part `keep` of `phrase` (creature/organs_road.py:answer_point's three lines):
    each hypothesis's score is the sum over the kept words, in PHRASE order; «none» (None) when the top is <= 0; an exact tie
    by `tie(len(best))`. No kept word → None."""
    words = [w for w in phrase if w in set(keep)]
    if not words:
        return None
    n_h = len(by_word[words[0]])
    if n_h == 0:
        return None
    scores = [float(sum(by_word[w][h] for w in words)) for h in range(n_h)]
    top = max(scores)
    if top <= 0.0:
        return None
    best = [k for k, s in enumerate(scores) if s == top]
    return best[0] if len(best) == 1 else best[int(tie(len(best)))]


def tie_of(test_seed: int, item: str) -> Callable[[int], int]:
    return lambda n: int(M.tie_rng(int(test_seed), str(item)).integers(n))


# ================================================================================================ one arm of one seed
class Arm:
    def __init__(self, root: Path, journal: Path, genome: Path):
        self.life = G.Life(root, journal, genome)
        self.sc = {t: G.SetCtx(self.life, t) for t in TSETS}

    def labels(self, tset: str, split: str, row: int) -> Tuple[List[Optional[int]], Dict[str, object], List[List[int]]]:
        tr = self.sc[tset].truth[split][int(row)]
        members, _pos = self.sc[tset].things[split].members(int(row))
        return [M.hyp_label(c) for c in M.hyp_counts(members, tr["fix_thing"])], tr, members

    def point_items(self, mark: str):
        """Every pointing item of `mark` over both test sets: (tset, item, truth row, labels, members, phrase, answer)."""
        split = G.SetCtx.split_of(mark)
        for tset in TSETS:
            for it in self.sc[tset].items.get(mark, []):
                lab, tr, mem = self.labels(tset, split, int(it["row"]))
                ask = self.life.asks[str(it["item_id"])]
                yield tset, it, tr, lab, mem, list(ask["phrase"]), self.life.answer_of.get(str(it["item_id"])), ask


def is_right(point: Optional[int], labels: Sequence[Optional[int]], target: int) -> bool:
    return point is not None and 0 <= int(point) < len(labels) and labels[int(point)] == int(target)


def needed(it: Dict[str, object], tr: Dict[str, object], phrase: Sequence[str]) -> bool:
    things, tgt = tr["things"], int(it["target"])
    if it["n_things"] not in (2, 3) or not M.covered(tgt, tr["fix_thing"]):
        return False
    if not any(W.word_type(w) in ("size", "colour") for w in phrase):
        return False
    return any(things[j]["shape"] == things[tgt]["shape"] for j in range(len(things)) if j != tgt)


# ================================================================================================ the marks
def mark_a(on: Arm, off: Arm) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for mark in ("M1", "M3"):
        blk = {}
        for name, arm in (("on", on), ("off", off)):
            n = ans = unheard = missing = 0
            words = collections.Counter()
            for _t, it, _tr, _lab, _mem, _ph, a, _ask in arm.point_items(mark):
                n += 1
                if a is None:
                    missing += 1
                    continue
                uw = a["answer"]["raw"].get("unheard") or []
                if uw:
                    unheard += 1
                    words.update(uw)
                else:
                    ans += 1
            blk[name] = {"n": n, "answerable": ans, "unheard": unheard, "no_answer_row": missing,
                         "share": (ans / n) if n else None, "unheard_words": dict(words)}
        blk["pass"] = bool(blk["on"]["n"] > 0 and blk["on"]["share"] == BARS["A"] and blk["on"]["no_answer_row"] == 0)
        out[mark] = blk
    out["pass"] = all(out[m]["pass"] for m in ("M1", "M3"))
    return out


def p_rows(on: Arm) -> Dict[str, List[Dict[str, object]]]:
    """Per test, the NEEDED items of ON with both pointings and the readings' per-item figures."""
    rows: Dict[str, List[Dict[str, object]]] = {"M1": [], "M3": []}
    for mark in ("M1", "M3"):
        for tset, it, tr, lab, mem, phrase, a, ask in on.point_items(mark):
            if not needed(it, tr, phrase):
                continue
            tgt = int(it["target"])
            item = str(it["item_id"])
            if a is None:
                raise GateError(f"{item}: ON has no answer row")
            raw, det = a["answer"]["raw"], (a.get("detail") or {})
            by = det.get("scores_by_word")
            shape_words = [w for w in phrase if W.word_type(w) == "shape"]
            if raw.get("unheard"):
                full, alone = None, None                    # mark A fails then; here the pair is wrong / wrong
            else:
                if by is None or set(by) != set(phrase):
                    raise GateError(f"{item}: ON's answer carries no scores_by_word for its phrase {phrase} (got {by and sorted(by)})")
                full = raw.get("point")
                again = repoint(by, phrase, phrase, tie_of(int(ask["test_seed"]), item))
                if again != full:
                    raise GateError(f"{item}: the reader's pointing by the WHOLE phrase ({again}) is not the answer's ({full})")
                alone = repoint(by, phrase, shape_words, tie_of(int(ask["test_seed"]), item))
            things = tr["things"]
            same = [i for i, l in enumerate(lab) if l is not None and things[l]["shape"] == things[tgt]["shape"]] or list(range(len(lab)))
            sizes = [len(m) for m in mem]
            most = [i for i, s in enumerate(sizes) if s == max(sizes)]
            kinds = {W.word_type(w) for w in phrase} - {"shape"}
            rows[mark].append({"item": item, "tset": tset, "n_hyp": len(lab), "full": is_right(full, lab, tgt),
                               "alone": is_right(alone, lab, tgt), "full_none": full is None, "alone_none": alone is None,
                               "chance": 1.0 / len(lab) if lab else 0.0,
                               "shape_only_road": float(np.mean([lab[i] == tgt for i in same])),
                               "most_fixations": float(np.mean([lab[i] == tgt for i in most])),
                               "kind": "both" if kinds == {"size", "colour"} else next(iter(kinds))})
    return rows


def p_block(rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    pr = paired([r["full"] for r in rows], [r["alone"] for r in rows])
    n = len(rows)
    k = sum(1 for r in rows if r["full"])
    return {**pr, "full": pr["a"], "alone": pr["b"], "gap": pr["diff"], "p": pr["p_a_higher"],
            "full_none": sum(1 for r in rows if r["full_none"]), "alone_none": sum(1 for r in rows if r["alone_none"]),
            "reading_chance": {"chance": float(np.mean([r["chance"] for r in rows])) if n else None, "right": k,
                               "p_exact": pb_tail([r["chance"] for r in rows], k) if n else None},
            "reading_shape_only_road": float(np.mean([r["shape_only_road"] for r in rows])) if n else None,
            "reading_most_fixations": float(np.mean([r["most_fixations"] for r in rows])) if n else None,
            "kinds": dict(collections.Counter(r["kind"] for r in rows))}


def mark_k(on_grade: Dict[str, object], off_grade: Dict[str, object]) -> Dict[str, object]:
    a, b, ids = [], [], []
    for tset in TSETS:
        off = {r["item_id"]: r for r in off_grade["items"][tset]["M1"]}
        on = {r["item_id"]: r for r in on_grade["items"][tset]["M1"]}
        if set(on) != set(off):
            raise GateError(f"K: the two grades hold different M1 items on {tset}")
        for k in sorted(off):
            o = off[k]
            if o["answered"] and o["gradable"] and o["covered"] and o["n_things"] in (2, 3):
                ids.append(k)
                b.append(bool(o["correct"]))
                a.append(bool(on[k]["correct"]))
    return {**paired(a, b), "items": ids, "flags_a": a, "flags_b": b}


def _emit(arm: Arm, item: str) -> Optional[List[str]]:
    a = arm.life.answer_of.get(item)
    return None if a is None else a["answer"]["raw"].get("emit")


def mark_k2(on: Arm, off: Arm) -> Dict[str, object]:
    a, b = [], []
    said = {"on": collections.Counter(), "off": collections.Counter()}
    idk = {"on": 0, "off": 0}
    skipped = 0
    for tset in TSETS:
        for it in off.sc[tset].items.get("M2b", []):
            if not it.get("graded"):
                continue
            item = str(it["item_id"])
            eo, en = _emit(off, item), _emit(on, item)
            if eo is None or en is None:
                skipped += 1                                  # the pointed thing was not seen: no emission in either arm
                if (eo is None) != (en is None):
                    raise GateError(f"{item}: seen in one arm and not in the other")
                continue
            for name, e in (("on", en), ("off", eo)):
                idk[name] += not e
                said[name].update(W.word_type(w) if w in W.VOCAB else "other" for w in e)
            a.append(not any(w in W.SHAPE_WORDS for w in en))
            b.append(not any(w in W.SHAPE_WORDS for w in eo))
    n = len(a)
    return {**paired(a, b), "flags_a": a, "flags_b": b, "unseen_in_both": skipped, "idk_share": {k: (v / n if n else None) for k, v in idk.items()},
            "words_emitted_by_kind": {k: dict(v) for k, v in said.items()}}


def first_hearings(arm: Arm, journal_rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """Mark G's bar: on every training canvas, the number of word cells born there equals the number of words first heard
    there. Read from the tape (what was said) and the journal's canvas rows (`births`)."""
    life = arm.life
    born_at: Dict[str, int] = {}
    for r in journal_rows:
        if "word" in r and r.get("moment") is not None:
            born_at[str(r["moment"])] = sum(1 for b in r.get("births", []) if b[0] == "words")
    heard: set = set()
    firsts: Dict[str, int] = {}
    wrong = []
    canvases = 0
    for scene in sorted(life.train_moment):
        m = life.train_moment[scene]
        new = [w for w in dict.fromkeys(life.moment_words.get(m, [])) if w not in heard]
        for w in new:
            heard.add(w)
            firsts[w] = scene
        if m not in born_at:
            if life.moment_words.get(m):
                wrong.append({"scene": scene, "first_heard": new, "word_cells_born": None})
            continue
        canvases += 1
        if born_at[m] != len(new):
            wrong.append({"scene": scene, "first_heard": new, "word_cells_born": born_at[m]})
    return {"canvases_read": canvases, "words_heard": len(firsts), "first_heard_at_scene": firsts, "canvases_wrong": wrong,
            "last_first_hearing_but_dax": max((s for w, s in firsts.items() if w != W.DAX_WORD), default=None)}


def series(path: Path) -> List[Dict[str, object]]:
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def mark_g(on: Arm, off: Arm, run: Path) -> Dict[str, object]:
    jon = G.read_journal(run / "on" / "journal.jsonl")
    joff = G.read_journal(run / "off" / "journal.jsonl")
    fh_on, fh_off = first_hearings(on, jon), first_hearings(off, joff)
    con, coff = series(run / "on" / "counters.jsonl"), series(run / "off" / "counters.jsonl")
    fin_on, fin_off = con[-1], coff[-1]
    if not fin_on.get("final") or not fin_off.get("final"):
        raise GateError("counters.jsonl has no final row")
    names = fin_on["word_cells"]
    ok = (not fh_on["canvases_wrong"] and fh_on["words_heard"] == BARS["words"] and len(names) == BARS["words"]
          and set(names) == set(fh_on["first_heard_at_scene"]))
    keys = ("canvases", "cells_sight", "cells_words", "cells_born_sight", "cells_born_words", "edges_alive", "births_refused_budget",
            "births_refused_nmax", "births_refused_redundant", "births_skipped_confirmed", "budget_left", "arrivals")
    return {"pass": bool(ok), "on": fh_on, "off_reading": {k: fh_off[k] for k in ("canvases_read", "words_heard")},
            "off_canvases_wrong_n": len(fh_off["canvases_wrong"]), "word_cells_on": names, "word_cells_off": fin_off["word_cells"],
            "hear_shared_cell": fin_on.get("hear_shared_cell"), "hear_words_refused": fin_on.get("hear_words_refused"),
            "series": {"on": [{k: r.get(k) for k in keys} for r in con], "off": [{k: r.get(k) for k in keys} for r in coff]},
            "readings": {"sight_cells_on_over_off": fin_on["cells_sight"] / fin_off["cells_sight"] if fin_off["cells_sight"] else None,
                         "refused_budget_on_over_off": (fin_on["births_refused_budget"] / fin_off["births_refused_budget"]
                                                        if fin_off["births_refused_budget"] else None),
                         "refused_redundant_on_over_off": (fin_on["births_refused_redundant"] / fin_off["births_refused_redundant"]
                                                           if fin_off["births_refused_redundant"] else None),
                         "births_refused_nmax": {"on": fin_on["births_refused_nmax"], "off": fin_off["births_refused_nmax"]}}}


def canvas_ms(arm: Arm, timings: Path, lo: int, hi: int) -> Dict[str, object]:
    """The mind's ms per TRAINING canvas: the consume ms of the canvas's ear rows and its eye row, scenes lo … hi − 1."""
    ms_of = {int(r["seq"]): float(r["ms"]) for r in series(timings)}
    life = arm.life
    seqs: Dict[str, List[int]] = collections.defaultdict(list)
    for r in life.rows:
        meta = r.get("meta") or {}
        if meta.get("source") == "scene" and r["sense"] in ("ear", "eye") and meta.get("moment") is not None:
            seqs[str(meta["moment"])].append(int(r["seq"]))
    per = []
    missing = 0
    for scene in range(lo, hi):
        m = life.train_moment.get(scene)
        if m is None:
            missing += 1
            continue
        ss = seqs[m]
        if any(s not in ms_of for s in ss):
            missing += 1
            continue
        per.append(sum(ms_of[s] for s in ss))
    return {"n": len(per), "missing": missing, "mean_ms": float(np.mean(per)) if per else None,
            "median_ms": float(np.median(per)) if per else None}


def mark_c(on: Arm, off: Arm, run: Path) -> Dict[str, object]:
    a = canvas_ms(on, run / "on" / "timings.jsonl", *COST_SCENES)
    b = canvas_ms(off, run / "off" / "timings.jsonl", *COST_SCENES)
    ratio = (a["mean_ms"] / b["mean_ms"]) if (a["mean_ms"] and b["mean_ms"]) else None
    full = COST_SCENES[1] - COST_SCENES[0]
    return {"on": a, "off": b, "ratio": ratio, "bar": BARS["C"],
            "pass": bool(ratio is not None and ratio <= BARS["C"] and a["n"] == full and b["n"] == full)}


def mark_i(run: Path, on: Arm, off: Arm) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for name in ("i1-twin", "i1-brain"):
        p = run / f"{name}.exit"
        out[name] = {"exit": int(p.read_text().strip()) if p.exists() else None,
                     "rows": (sum(1 for _ in (run / ("off" if name == "i1-twin" else "brain") / "journal.jsonl").open())
                              if (run / ("off" if name == "i1-twin" else "brain") / "journal.jsonl").exists() else None)}
    out["I1_pass"] = bool(out["i1-twin"]["exit"] == 0 and out["i1-brain"]["exit"] == 0)
    jon = RP.read_mind_journal(run / "on" / "journal.jsonl")
    joff = RP.read_mind_journal(run / "off" / "journal.jsonl")
    d = RP.compare(jon, joff, ignore=MASK)
    life = off.life
    first = None
    for scene in sorted(life.train_moment):
        m = life.train_moment[scene]
        if len(dict.fromkeys(life.moment_words.get(m, []))) > 1:
            first = {"scene": scene, "moment": m, "words": life.moment_words[m], "eye_seq": int(life.moment_eye[m]["seq"])}
            break
    out["I2"] = {"first_difference": list(d) if d is not None else None, "first_multi_word_canvas": first,
                 "pass": bool(d is not None and first is not None and int(d[0]) == first["eye_seq"])}
    return out


# ================================================================================================ the gate
def read_seed(runs: Path, ws: int, log=print) -> Dict[str, object]:
    run = runs / str(ws)
    root = LIVES / f"brain-lean-{ws}"
    code = ROOT / "genome" / "brain" / "lives"
    off = Arm(root, run / "off" / "journal.jsonl", code / f"BRAIN-LEAN-TWIN-{ws}.genome")
    on = Arm(root, run / "on" / "journal.jsonl", code / f"BRAIN-LEAN-TWIN-HEAR-{ws}.genome")
    g_on = json.loads((run / "grade-on" / "grade.json").read_text())
    g_off = json.loads((run / "grade-off" / "grade.json").read_text())
    rows = p_rows(on)
    res = {"world_seed": ws, "I": mark_i(run, on, off), "A": mark_a(on, off),
           "P": {m: p_block(rows[m]) for m in ("M1", "M3")}, "P_rows": rows,
           "K": mark_k(g_on, g_off), "K2": mark_k2(on, off), "G": mark_g(on, off, run), "C": mark_c(on, off, run)}
    log(f"[gate {ws}] read: P items {len(rows['M1'])} / {len(rows['M3'])} · K n {res['K']['n']} · K2 n {res['K2']['n']}")
    return res


def read_nulls(runs: Path, ws: int, k_max: int, items: Dict[str, List[str]]) -> Dict[str, object]:
    """NULL-10: each draw's full-phrase accuracy on the SAME items (the made tape's sitting is the life's)."""
    out = {"draws": [], "M1": [], "M3": []}
    for k in range(1, k_max + 1):
        d = runs / str(ws) / f"null-{k}"
        arm = Arm(d / "life", d / "on" / "journal.jsonl", d / "GENOME.genome")
        rows = p_rows(arm)
        rec = {"k": k}
        for m in ("M1", "M3"):
            got = [r["item"] for r in rows[m]]
            if got != items[m]:
                raise GateError(f"null {k}: its NEEDED items of {m} are not the life's ({len(got)} against {len(items[m])})")
            rec[m] = sum(1 for r in rows[m] if r["full"]) / len(rows[m]) if rows[m] else None
            out[m].append(rec[m])
        out["draws"].append(rec)
    return out


def verdict(seeds: Sequence[Dict[str, object]], nulls: Optional[Dict[str, object]], null_seed: int) -> Dict[str, object]:
    v: Dict[str, object] = {}
    v["I1"] = all(s["I"]["I1_pass"] for s in seeds)
    v["I2"] = all(s["I"]["I2"]["pass"] for s in seeds)
    v["A"] = all(s["A"]["pass"] for s in seeds)
    P: Dict[str, object] = {}
    for m in ("M1", "M3"):
        rows = [r for s in seeds for r in s["P_rows"][m]]
        pooled = p_block(rows)
        every = all((s["P"][m]["gap"] is not None and s["P"][m]["gap"] > 0.0) for s in seeds)
        nul = None
        if nulls is not None:
            mine = next(s for s in seeds if s["world_seed"] == null_seed)["P"][m]["full"]
            nul = {"on": mine, "draws": nulls[m], "max": max(nulls[m]), "above_every_draw": bool(all(mine > x for x in nulls[m]))}
        ok = bool(pooled["n"] > 0 and pooled["gap"] >= BARS["P_gap"] - 1e-12 and pooled["p"] < BARS["P_p"] and every
                  and nul is not None and nul["above_every_draw"])
        P[m] = {"pooled": pooled, "gap_above_0_at_every_seed": every, "null": nul, "pass": ok}
    v["P"] = P
    v["P_pass"] = all(P[m]["pass"] for m in P)
    for key in ("K", "K2"):
        a = [x for s in seeds for x in s[key]["flags_a"]]
        b = [x for s in seeds for x in s[key]["flags_b"]]
        pr = paired(a, b)
        v[key] = {**pr, "bar": BARS[key], "pass": bool(pr["n"] > 0 and pr["diff"] >= BARS[key] - 1e-12)}
    v["G"] = all(s["G"]["pass"] for s in seeds)
    v["C"] = all(s["C"]["pass"] for s in seeds)
    v["ADOPT"] = bool(v["I1"] and v["I2"] and v["A"] and v["P_pass"] and v["K"]["pass"] and v["K2"]["pass"] and v["G"] and v["C"])
    return v


def report(res: Dict[str, object]) -> str:
    def f(x, d=3):
        return "n/a" if x is None else f"{x:.{d}f}"
    L = ["THE WORD ROAD — the gate's marks (PREREG-WORD-ROAD §4)", ""]
    v = res["verdict"]
    for s in res["seeds"]:
        ws = s["world_seed"]
        i = s["I"]
        L.append(f"SEED {ws}")
        L.append(f"  I1 the line absent: twin replay exit {i['i1-twin']['exit']} (rows {i['i1-twin']['rows']}) · BRAIN replay exit "
                 f"{i['i1-brain']['exit']} (rows {i['i1-brain']['rows']}) → {'PASS' if i['I1_pass'] else 'FAIL'}")
        L.append(f"  I2 the plant: first difference {i['I2']['first_difference']} · the first multi-word canvas "
                 f"{i['I2']['first_multi_word_canvas']} → {'PASS' if i['I2']['pass'] else 'FAIL'}")
        for m in ("M1", "M3"):
            a = s["A"][m]
            L.append(f"  A {m}: ON answerable {a['on']['answerable']} of {a['on']['n']} ({f(a['on']['share'])}; unheard words "
                     f"{a['on']['unheard_words']}) · OFF {a['off']['answerable']} of {a['off']['n']} ({f(a['off']['share'])}) → "
                     f"{'PASS' if a['pass'] else 'FAIL'}")
        for m in ("M1", "M3"):
            p = s["P"][m]
            rc = p["reading_chance"]
            L.append(f"  P {m} (NEEDED n {p['n']}; kinds {p['kinds']}): the whole phrase {f(p['full'])} · the shape word alone "
                     f"{f(p['alone'])} · gap {f(p['gap'])} (pairs {p['f']} for, {p['u']} against; p {p['p']:.2e}) · «none» "
                     f"{p['full_none']} / {p['alone_none']}")
            L.append(f"      readings, never graded: chance {f(rc['chance'])} (right {rc['right']}, exact p {rc['p_exact']:.2e}) · "
                     f"a shape-only road {f(p['reading_shape_only_road'])} · the most-fixations pointer {f(p['reading_most_fixations'])}")
        k = s["K"]
        L.append(f"  K (n {k['n']}): ON {f(k['a'])} · OFF {f(k['b'])} · ON − OFF {f(k['diff'])} ± {f(k['se'])} (pairs {k['f']} / {k['u']}; "
                 f"sign test «ON lower» p {f(k['p_a_lower'], 4)})")
        k = s["K2"]
        L.append(f"  K2 (n {k['n']}; unseen in both {k['unseen_in_both']}): ON {f(k['a'])} · OFF {f(k['b'])} · ON − OFF {f(k['diff'])} ± "
                 f"{f(k['se'])} · «I don't know» share ON {f(k['idk_share']['on'])} OFF {f(k['idk_share']['off'])} · words emitted "
                 f"by kind ON {k['words_emitted_by_kind']['on']} OFF {k['words_emitted_by_kind']['off']}")
        g = s["G"]
        L.append(f"  G: words heard {g['on']['words_heard']} · canvases read {g['on']['canvases_read']} · canvases where the word "
                 f"cells born are not the words first heard {len(g['on']['canvases_wrong'])} {g['on']['canvases_wrong'][:3]} · "
                 f"word cells ON {len(g['word_cells_on'])} OFF {len(g['word_cells_off'])} · shared cells {g['hear_shared_cell']} · "
                 f"words the ear refused {g['hear_words_refused']} → {'PASS' if g['pass'] else 'FAIL'}")
        r = g["readings"]
        L.append(f"      readings: sight cells ON / OFF {f(r['sight_cells_on_over_off'])} · refused by budget ON / OFF "
                 f"{f(r['refused_budget_on_over_off'])} · refused redundant ON / OFF {f(r['refused_redundant_on_over_off'])} · "
                 f"refused by the cap {r['births_refused_nmax']}")
        L.append("      series (every 1,000 worded canvases): canvases · sight cells ON/OFF · refused by budget ON/OFF · redundant ON/OFF")
        for a, b in zip(g["series"]["on"], g["series"]["off"]):
            L.append(f"        {a['canvases']:>6} · {a['cells_sight']} / {b['cells_sight']} · {a['births_refused_budget']} / "
                     f"{b['births_refused_budget']} · {a['births_refused_redundant']} / {b['births_refused_redundant']}")
        c = s["C"]
        L.append(f"  C: ms per training canvas, scenes {COST_SCENES[0]}–{COST_SCENES[1] - 1}: ON {f(c['on']['mean_ms'], 2)} (n {c['on']['n']}) · "
                 f"OFF {f(c['off']['mean_ms'], 2)} (n {c['off']['n']}) · ratio {f(c['ratio'])} (bar ≤ {c['bar']}) → "
                 f"{'PASS' if c['pass'] else 'FAIL'}")
        L.append("")
    L.append("POOLED")
    for m in ("M1", "M3"):
        p = v["P"][m]
        q = p["pooled"]
        nul = p["null"]
        L.append(f"  P {m}: n {q['n']} · the whole phrase {f(q['full'])} · the shape word alone {f(q['alone'])} · gap {f(q['gap'])} "
                 f"(bar ≥ {BARS['P_gap']}) · pairs {q['f']} for, {q['u']} against · p {q['p']:.2e} (bar < {BARS['P_p']}) · above 0 "
                 f"at every seed: {p['gap_above_0_at_every_seed']} · NULL-10 "
                 + ("not read" if nul is None else f"ON {f(nul['on'])} against the draws' max {f(nul['max'])} "
                    f"({[round(x, 3) for x in nul['draws']]}): above every draw {nul['above_every_draw']}")
                 + f" → {'PASS' if p['pass'] else 'FAIL'}")
    for key in ("K", "K2"):
        k = v[key]
        L.append(f"  {key}: n {k['n']} · ON {f(k['a'])} · OFF {f(k['b'])} · ON − OFF {f(k['diff'])} ± {f(k['se'])} (bar ≥ {k['bar']}; "
                 f"pairs {k['f']} / {k['u']}; sign test «ON lower» p {f(k['p_a_lower'], 4)}) → {'PASS' if k['pass'] else 'FAIL'}")
    L.append("")
    L.append("THE MARKS: " + " · ".join(f"{k} {'PASS' if x else 'FAIL'}" for k, x in (
        ("I1", v["I1"]), ("I2", v["I2"]), ("A", v["A"]), ("P", v["P_pass"]), ("K", v["K"]["pass"]), ("K2", v["K2"]["pass"]),
        ("G", v["G"]), ("C", v["C"]))))
    L.append("THE DECISION RULE (§4): HEAR " + ("becomes the law of the next brain lives" if v["ADOPT"] else "is NOT adopted"))
    return "\n".join(L) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS))
    ap.add_argument("--null-seed", type=int, default=20261102)
    ap.add_argument("--nulls", type=int, default=10)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    runs, out = Path(a.runs), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    seeds = [read_seed(runs, ws) for ws in a.seeds]
    nulls = None
    if a.nulls > 0:
        mine = next(s for s in seeds if s["world_seed"] == a.null_seed)
        nulls = read_nulls(runs, a.null_seed, a.nulls, {m: [r["item"] for r in mine["P_rows"][m]] for m in ("M1", "M3")})
    res = {"seeds": seeds, "nulls": nulls, "verdict": verdict(seeds, nulls, a.null_seed), "bars": BARS}
    (out / "gate.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=_np))
    txt = report(res)
    (out / "report.txt").write_text(txt)
    print(txt)
    return 0 if res["verdict"]["ADOPT"] else 1


def _np(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(type(o))


if __name__ == "__main__":
    sys.exit(main())
