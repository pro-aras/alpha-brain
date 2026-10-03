#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-30 10:4x +0400 — the 09-30 DRAFT of this reader (never run; its stamp was typed ahead of the clock, #50).
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 10:51 +0400 — PREREG-HEARS-2 §2: the bench's reader REBUILT test-first (tests/tools/test_hears_read.py, red on the draft): P over the
# grader's own pair population, the six tests' verdicts, X with its plant, I2 as the stronger comparison, every mark that has a control runs it.
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:05 +0400 — AMENDMENT 1 (the architect's review, signed by the architect and the seat): A1.1 the arms' overlap voids C, A1.2 C barred
# on the maker canvases (median AND mean), the whole replay and the scene canvases, A1.3 T's maker-only comparison struck and the shared arm read against a dealt-targets null at k 3
# and k 1, A1.4 G's two clauses replaced (every typed maker word said truly; agreed over ALL of exactly the last 100), A1.5 the discordant items split by phrase class and position.
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:15 +0400 — found by running it on the real live journal: `--tape` alone serves the splits (the cost needs the two timings files beside it).
"""tools/brain/hears_read.py — what the bench of PREREG-HEARS-2 (§2 + AMENDMENT 1) reads, from the two arms' grades, timings, journals and launch records.

    PYTHONPATH=<repo> python3 -B tools/brain/hears_read.py --off <grade dir> --on <grade dir> --out <dir>
        [--on-plant <grade dir of ON regraded on a journal whose ONE cited moment was spoiled>]
        [--tape <the cut tape dir> --off-timings <timings.jsonl> --on-timings <timings.jsonl> --off-arm <OFF's .arm file> --on-arm <ON's .arm file>]
        [--on-journal <ON's journal.jsonl> --off-journal <OFF's journal.jsonl> --i1-journal <the replay under the life's own genome>]

    PYTHONPATH=<repo> python3 -B tools/brain/hears_read.py --plant-x-journal <ON journal.jsonl> --plant-x-out <planted journal.jsonl>

Marks (the law's names):
  P   the scene words, paired item by item on the fresh and the s1b1 sittings and pooled: M1 (the graded population, two or three things), M3, M6 over the items COVERED and
      GRADABLE in BOTH arms (grade_life.pair()'s own rule), with the discordant counts, the smallest gap the n can pass (10 / n, #245 (5)) and the one-sided exact sign tests; the
      rates the grade holds only as rates (M2a, M2b, false refusal) beside their own 10 / n; the six tests' verdicts OFF → ON; the discordant items SPLIT by phrase class (a shape
      word only / a colour or size word / «white») and by position in the sitting (thirds; A1.5). A READING: no bar.
  T   TRANSFER (A1.3): the SHARED words' first k maker meetings (k = 3 and k = 1) read as agreed / ALL turns against a dealt-targets null (the maker's words permuted among the same
      canvases, the says fixed); the maker-only arm is struck as a comparison and read as an over-extension table. A reading with a stated line.
  G   GROWTH (A1.4): the rate agreed / ALL of EXACTLY the last 100 maker turns with its ceiling (turns whose word was typed) and floor (always say the commonest word); every maker
      word typed at the last calibration said truly at least once. A reading with the law's predictions.
  C   COST (A1.1, A1.2): the mind's CPU per canvas, ON over OFF (the SUM of a canvas's ear and eye rows' cpu_ms), BAR ≤ 1.5 on the maker canvases (median AND mean), on the whole
      replay's mean per timed row and on the scene training canvases (median AND mean), every canvas timed in both arms; VOID when the arms' wall windows overlap under 0.90.
  X   EXIST by any hand: ON's EXIST must read 1.000 with the citations by world printed, and the plant — ONE cited moment spoiled, regraded — must read exactly (n − 1) / n.
  I2  the token absent changes nothing: OFF's journal without its turn rows equals the replay under the life's own genome, row for row (every other row, brain rows and answers
      included — the default of journal_diff.py drops those).
Controls run on the real inputs: P (one paired item of ON flipped in memory must move the discordant counts by exactly one), I2 (one character of one kept row must fail it).
A missing field is «not recorded» (None), never 0 (#168). Exit 0 iff no barred mark (C, X, I2) FAILS or is VOID and no control MISSED; ReaderError (exit 2 as a script) on an unreadable input."""
from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import json
import math
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.brain import worlds_read as WR  # noqa: E402

SETS = ("fresh", "s1b1")
MARKS = (("M1", True), ("M3", False), ("M6", False))        # (mark, only the graded population: two or three things — grade_life.pair(graded_only=True))
COST_BAR = 1.5
MIN_OVERLAP = 0.90                                          # A1.1: the arms' wall windows must overlap by this much, or C is VOID
LAST_K = 100
YOUNG = 3                                                   # `young 3` in the BRAIN line: a word needs 3 meetings before it can be believed, held or said
TRANSFER_KS = (3, 1)
NULL_DRAWS = 1000                                           # A1.3: the architect asked ≥ 200
NULL_SEED = 20261003
NOWHERE = "nowhere-on-any-tape"
COLOURS = frozenset({"blue", "green", "red", "white", "yellow"})
SIZES = frozenset({"big", "small"})
CLASSES = ("shape_only", "colour_size", "white", "no_phrase")
THIRDS = ("third_1", "third_2", "third_3")
VERDICT_SOURCES = (("1", ("bars", "M1", "pass")), ("2a", ("bars", "M2a", "pass")), ("2b", ("bars", "M2b", "pass")), ("3", ("bars", "M3", "pass")),
                   ("4a", ("M4a", "verdict")), ("5", ("M5", "verdict")), ("6", ("M6_pooled", "verdict")))


class ReaderError(Exception):
    """An input that cannot be read, named by the path that is missing — never skipped."""


def need(d, *path, src: str = "grade"):
    cur = d
    for i, k in enumerate(path):
        if not isinstance(cur, dict) or k not in cur:
            raise ReaderError(f"{src} lacks {'.'.join(str(x) for x in path[: i + 1])}")
        cur = cur[k]
    return cur


def load_grade(p) -> Dict[str, object]:
    p = Path(p)
    f = p / "grade.json" if p.is_dir() else p
    try:
        return json.loads(f.read_text())
    except (OSError, ValueError) as e:
        raise ReaderError(f"{f}: the grade cannot be read ({e})") from e


def _src(g) -> str:
    return f"grade '{g.get('label')}'"


def sign_test(b: int, c: int) -> float:
    """grade_life.sign_test, exactly: P(X >= b), X ~ Bin(b + c, 1/2); no discordant pair -> 1.0."""
    n = b + c
    if n == 0:
        return 1.0
    return float(sum(math.comb(n, i) for i in range(b, n + 1)) / (2.0 ** n))


# ------------------------------------------------------------------------------------------------ P · the scene words, paired
def _rows(g, tset: str, mark: str) -> Dict[Tuple[str, str], Dict[str, object]]:
    rows = need(g, "items", tset, mark, src=_src(g))
    return {(tset, str(r["item_id"])): r for r in rows}


def _pooled(g, mark: str) -> Dict[Tuple[str, str], Dict[str, object]]:
    out: Dict[Tuple[str, str], Dict[str, object]] = {}
    for tset in SETS:
        out.update(_rows(g, tset, mark))
    return out


def pair_population(a: Dict, b: Dict, graded_only: bool):
    """a, b: key -> row of the OFF and the ON arm. The pair population is grade_life.pair()'s own: the keys in BOTH, of those the rows covered AND gradable in both (and, for M1's
    graded population, with two or three things). Returns the keys in both, the keys gradable in both, the paired keys, and the paired keys ON got right / OFF got right alone."""
    both = sorted(set(a) & set(b))
    base = [k for k in both if a[k].get("gradable") and b[k].get("gradable") and (not graded_only or a[k].get("n_things") in (2, 3))]
    pop = [k for k in base if a[k].get("covered") and b[k].get("covered")]
    on_right = [k for k in pop if b[k].get("correct") and not a[k].get("correct")]
    off_right = [k for k in pop if a[k].get("correct") and not b[k].get("correct")]
    return both, base, pop, on_right, off_right


def pair_items(a: Dict, b: Dict, graded_only: bool) -> Dict[str, object]:
    """The counts of pair_population, with the rates, the gap, the smallest passing gap (10 / n over THE PAIRED n) and the exact sign tests. Every item left out is COUNTED
    (only_off, only_on, excluded_in_both)."""
    both, base, pop, on_right, off_right = pair_population(a, b, graded_only)
    n = len(pop)
    off_rate = (sum(1 for k in pop if a[k].get("correct")) / n) if n else None
    on_rate = (sum(1 for k in pop if b[k].get("correct")) / n) if n else None
    gap = None if n == 0 else on_rate - off_rate
    spg = (10.0 / n) if n else None
    return {"n_items_off": len(a), "n_items_on": len(b), "n_items_both": len(both), "only_off": len(set(a) - set(b)), "only_on": len(set(b) - set(a)),
            "n_pair": n, "excluded_in_both": len(both) - n,
            "covered_off": sum(1 for k in base if a[k].get("covered")), "covered_on": sum(1 for k in base if b[k].get("covered")),
            "covered_only_off": sum(1 for k in base if a[k].get("covered") and not b[k].get("covered")),
            "covered_only_on": sum(1 for k in base if b[k].get("covered") and not a[k].get("covered")),
            "off_rate": off_rate, "on_rate": on_rate, "gap": gap, "smallest_passing_gap": spg,
            "within_noise": (None if n == 0 else abs(gap) < spg),
            "discordant_on_right": len(on_right), "discordant_off_right": len(off_right),
            "p_on_better": sign_test(len(on_right), len(off_right)), "p_on_worse": sign_test(len(off_right), len(on_right))}


def pairs(off, on) -> Dict[str, Dict[str, Dict[str, object]]]:
    out: Dict[str, Dict[str, Dict[str, object]]] = {}
    for tset in SETS:
        out[tset] = {mark: pair_items(_rows(off, tset, mark), _rows(on, tset, mark), go) for mark, go in MARKS}
    out["pooled"] = {mark: pair_items(_pooled(off, mark), _pooled(on, mark), go) for mark, go in MARKS}
    return out


def _agg(a, na, b, nb) -> Dict[str, object]:
    return {"off": a, "on": b, "n_off": na, "n_on": nb, "gap": (None if a is None or b is None else b - a),
            "smallest_passing_gap": (None if not na or not nb else 10.0 / min(na, nb))}


def aggregates(off, on) -> Dict[str, Dict[str, object]]:
    """The rates a grade holds only as RATES (no item rows): M1 and M3 covered, M2a's refusal, false refusal, M2b — each beside its own 10 / n."""
    out: Dict[str, Dict[str, object]] = {}
    for tset in SETS:
        cells: Dict[str, List] = {}
        for side, g in (("off", off), ("on", on)):
            s = _src(g)
            m1 = need(g, "sets", tset, "marks", "M1", "graded", src=s)
            m3m = need(g, "sets", tset, "marks", "M3", src=s)
            m3 = m3m.get("all", m3m)
            law = need(g, "sets", tset, "marks", "roads", "LAW", src=s)
            m2a = need(law, "M2a", "all", src=s + f" sets.{tset}.marks.roads.LAW")
            m2b = need(law, "M2b", "graded", src=s + f" sets.{tset}.marks.roads.LAW")
            cells[side] = [(m1.get("covered"), m1.get("n_covered")), (m3.get("covered"), m3.get("n_covered")), (m2a.get("refusal"), m2a.get("n")),
                           (law.get("false_refusal"), law.get("n_fr")), (m2b.get("correct"), m2b.get("n"))]
        out[tset] = {name: _agg(cells["off"][i][0], cells["off"][i][1], cells["on"][i][0], cells["on"][i][1])
                     for i, name in enumerate(("M1_covered", "M3_covered", "M2a_refusal", "false_refusal", "M2b"))}
    return out


def _fmt_verdict(v) -> str:
    return "PASS" if v is True else "FAIL" if v is False else "n/a" if v is None else str(v)


def verdicts(off, on) -> Dict[str, Dict[str, object]]:
    """The six tests' verdicts side by side (tests 1, 2a/2b, 3, 4a, 5, 6). `changed` compares the verdict's first word only, so a count inside the sentence
    («UNDERPOWERED (n 104)») is never a change; the whole sentence is kept as *_detail when it says more than the first word."""
    out: Dict[str, Dict[str, object]] = {}
    for name, path in VERDICT_SOURCES:
        vals = []
        for g in (off, on):
            cur = g
            for k in path:
                cur = cur.get(k) if isinstance(cur, dict) else None
            vals.append(_fmt_verdict(cur))
        lead = [v.split()[0] if v.split() else v for v in vals]
        d: Dict[str, object] = {"off": lead[0], "on": lead[1], "changed": lead[0] != lead[1]}
        for side, full, ld in (("off", vals[0], lead[0]), ("on", vals[1], lead[1])):
            if full != ld:
                d[side + "_detail"] = full
        out[name] = d
    return out


def p_control(off, on) -> Dict[str, object]:
    """Flip ONE paired item of ON in a copy: the discordant counts must move by exactly one item and n_pair must not move."""
    for tset in SETS:
        for mark, go in MARKS:
            a, b = _rows(off, tset, mark), _rows(on, tset, mark)
            _both, _base, pop, _on, _off = pair_population(a, b, go)
            if not pop:
                continue
            base = pair_items(a, b, go)
            key = pop[0]
            b2 = dict(b)
            b2[key] = {**b[key], "correct": not b[key].get("correct")}
            new = pair_items(a, b2, go)
            d_on = new["discordant_on_right"] - base["discordant_on_right"]
            d_off = new["discordant_off_right"] - base["discordant_off_right"]
            return {"caught": bool(abs(d_on) + abs(d_off) == 1 and new["n_pair"] == base["n_pair"]), "set": tset, "mark": mark, "item": key[1],
                    "before": [base["discordant_on_right"], base["discordant_off_right"]], "after": [new["discordant_on_right"], new["discordant_off_right"]]}
    return {"caught": None, "why": "no paired item in any mark"}


# ------------------------------------------------------------------------------------------------ P · the discordant items split (A1.5)
def phrase_class(phrase) -> str:
    """shape_only: every word is a shape; colour_size: holds a colour or a size word (but not «white»); white: holds «white», apart (the maker draws white things)."""
    ws = [str(w) for w in (phrase or [])]
    if not ws:
        return "no_phrase"
    if "white" in ws:
        return "white"
    if any(w in COLOURS or w in SIZES for w in ws):
        return "colour_size"
    return "shape_only"


def position_third(seq: int, sitting: Optional[Dict[str, object]]) -> Optional[int]:
    """0, 1 or 2: the item's place between the sitting's `begin` and `end` asks by tape seq; None when the sitting is unknown or the item lies outside it."""
    if not sitting or sitting.get("end") is None:
        return None
    b, e = int(sitting["begin"]), int(sitting["end"])
    if e <= b or not (b < seq < e):
        return None
    return min(2, int(3 * (seq - b) / (e - b)))


def tape_index(tape_dir) -> Dict[str, object]:
    """From the cut tape: every scene `point` ask (item → seq, phrase), each sitting's begin / end ask seqs, and the seqs of the maker's eye rows."""
    tape = Path(tape_dir)
    items: Dict[str, Dict[str, object]] = {}
    sittings: Dict[str, Dict[str, object]] = {}
    maker: List[int] = []
    for f in sorted(tape.glob("*.jsonl")):
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                meta = r.get("meta") or {}
                if r.get("sense") == "eye" and meta.get("source") == "maker":
                    maker.append(int(r["seq"]))
                elif r.get("sense") == "ask" and meta.get("source") == "scene" and r.get("payload"):
                    p = json.loads((tape / r["payload"]).read_text(encoding="utf-8"))
                    form = p.get("form")
                    if form == "begin":
                        sittings[str(p.get("set"))] = {"begin": int(r["seq"]), "end": None}
                    elif form == "end" and str(p.get("set")) in sittings:
                        sittings[str(p.get("set"))]["end"] = int(r["seq"])
                    elif form == "point" and p.get("item") is not None:
                        items[str(p["item"])] = {"seq": int(r["seq"]), "phrase": [str(x) for x in (p.get("phrase") or [])], "mark": p.get("mark")}
    return {"items": items, "sittings": sittings, "maker_seqs": sorted(maker)}


def splits(off, on, ti) -> Dict[str, Dict[str, object]]:
    """Per mark, pooled over both sittings: the paired items and the discordant ones by phrase class and by third of the sitting, and each discordant item in full."""
    out: Dict[str, Dict[str, object]] = {}
    for mark, go in MARKS:
        _both, _base, pop, on_right, off_right = pair_population(_pooled(off, mark), _pooled(on, mark), go)
        on_set, off_set = set(on_right), set(off_right)
        by_class = {c: {"n_pair": 0, "on_right": 0, "off_right": 0} for c in CLASSES}
        by_third = {t: {"n_pair": 0, "on_right": 0, "off_right": 0} for t in THIRDS}
        unlocated, unplaced = 0, 0
        disc: List[Dict[str, object]] = []
        for k in pop:
            meta = ti["items"].get(k[1])
            if meta is None:
                unlocated += 1
                continue
            cls = phrase_class(meta["phrase"])
            sit = ti["sittings"].get(k[0])
            third = position_third(int(meta["seq"]), sit)
            by_class[cls]["n_pair"] += 1
            if third is None:
                unplaced += 1
            else:
                by_third[THIRDS[third]]["n_pair"] += 1
            if k in on_set or k in off_set:
                key = "on_right" if k in on_set else "off_right"
                by_class[cls][key] += 1
                if third is not None:
                    by_third[THIRDS[third]][key] += 1
                since = (bisect.bisect_left(ti["maker_seqs"], int(meta["seq"])) - bisect.bisect_right(ti["maker_seqs"], int(sit["begin"]))) if sit else None
                disc.append({"set": k[0], "item": k[1], "direction": key, "phrase": meta["phrase"], "class": cls,
                             "third": (None if third is None else third + 1), "maker_canvases_since_begin": since})
        out[mark] = {"by_class": by_class, "by_third": by_third, "unlocated_items": unlocated, "unplaced_items": unplaced, "discordant": disc}
    return out


# ------------------------------------------------------------------------------------------------ X · EXIST by any hand
def x_mark(off, on, plant) -> Dict[str, object]:
    a_on, a_off = need(on, "M4a", src=_src(on)), need(off, "M4a", src=_src(off))
    exist, n = a_on.get("exist"), a_on.get("n_cited")
    by_world = a_on.get("cited_by_world")        # absent in a grade written before the HEARS-2 grader: «not recorded», never {} (#168)
    maker = None if by_world is None else int(by_world.get("maker", 0))
    out: Dict[str, object] = {"exist": exist, "n_cited": n, "n_with_truth": a_on.get("n_with_truth"), "carry": a_on.get("carry"),
                              "null_p95": a_on.get("null_p95"), "verdict": a_on.get("verdict"), "cited_by_world": by_world, "maker_citations": maker,
                              "exercised_on_a_maker_citation": (None if maker is None else maker > 0),
                              "exist_holds": bool(exist is not None and exist == 1.0 and n),
                              "off": {"exist": a_off.get("exist"), "n_cited": a_off.get("n_cited"), "cited_by_world": a_off.get("cited_by_world"),
                                      "verdict": a_off.get("verdict")}}
    if plant is None:
        out.update({"plant": None, "plant_caught": None, "plant_is_one_spoiled_citation": None, "pass": None})
        return out
    p = need(plant, "M4a", src=_src(plant))
    pe, pn = p.get("exist"), p.get("n_cited")
    one = bool(n and pn == n and pe is not None and abs(pe - (n - 1) / n) < 1e-9)
    caught = bool(pe is not None and pe < 1.0)
    out.update({"plant": {"exist": pe, "n_cited": pn, "cited_by_world": p.get("cited_by_world")}, "plant_caught": caught,
                "plant_is_one_spoiled_citation": one, "pass": bool(out["exist_holds"] and caught and one)})
    return out


def make_x_plant(src, dst) -> Dict[str, object]:
    """Write DST = SRC (a replay's journal.jsonl) with the moment of the FIRST cited episode of the first `why` answer replaced by NOWHERE: one line of one answer changes, every
    other line is copied byte for byte. Regrade DST with the same grade_life command as ON: EXIST must read (n − 1) / n."""
    lines = Path(src).read_text().splitlines(keepends=True)
    for i, line in enumerate(lines):
        if '"because"' not in line or '"episodes"' not in line:
            continue
        r = json.loads(line)
        a = r.get("answer") or {}
        if r.get("kind") == "answer" and r.get("form") == "why" and a.get("kind") == "because" and a.get("episodes"):
            was = a["episodes"][0].get("moment")
            a["episodes"][0]["moment"] = NOWHERE
            lines[i] = json.dumps(r) + "\n"
            break
    else:
        raise ReaderError(f"{src}: no `why` answer that cites an episode — nothing to plant on")
    Path(dst).write_text("".join(lines))
    old = Path(src).read_text().splitlines(keepends=True)
    changed = sum(1 for x, y in zip(old, lines) if x != y)
    if changed != 1 or Path(src).read_bytes() == Path(dst).read_bytes():
        raise ReaderError(f"the plant changed {changed} lines (it must change exactly one, and the bytes)")
    return {"item": r.get("item"), "word": a.get("word"), "was": was, "line": i, "lines_changed": changed,
            "sha256_src": hashlib.sha256(Path(src).read_bytes()).hexdigest(), "sha256_dst": hashlib.sha256(Path(dst).read_bytes()).hexdigest()}


# ------------------------------------------------------------------------------------------------ C · COST
def parse_arm(path) -> Dict[str, object]:
    """An arm's launch record (tools/brain/hears_bench.sh `arm`): `key value` lines — start_epoch, end_epoch, loadavg_*, pressure_cpu_*, exit."""
    d: Dict[str, object] = {}
    try:
        for line in Path(path).read_text().splitlines():
            k, _, v = line.partition(" ")
            if k:
                d[k] = v
    except OSError as e:
        raise ReaderError(f"{path}: the arm's launch record cannot be read ({e})") from e
    for k in ("start_epoch", "end_epoch"):
        if k not in d:
            raise ReaderError(f"{path} lacks {k} (the arm has not finished, or it was not run by hears_bench.sh)")
        d[k] = float(d[k])
    return d


def launch(off_arm, on_arm) -> Dict[str, object]:
    a, b = parse_arm(off_arm), parse_arm(on_arm)
    inter = min(a["end_epoch"], b["end_epoch"]) - max(a["start_epoch"], b["start_epoch"])
    longer = max(a["end_epoch"] - a["start_epoch"], b["end_epoch"] - b["start_epoch"])
    ov = (max(0.0, inter) / longer) if longer > 0 else None
    keep = ("start_iso", "end_iso", "loadavg_start", "loadavg_end", "pressure_cpu_start", "pressure_cpu_end", "exit")
    return {"off": {**{k: a.get(k) for k in keep}, "wall_s": a["end_epoch"] - a["start_epoch"]},
            "on": {**{k: b.get(k) for k in keep}, "wall_s": b["end_epoch"] - b["start_epoch"]},
            "start_skew_s": abs(a["start_epoch"] - b["start_epoch"]), "overlap": ov, "min_overlap": MIN_OVERLAP, "void": bool(ov is None or ov < MIN_OVERLAP)}


def _canvases(tape_dir) -> Dict[str, Dict[str, object]]:
    """moment -> {source, kind, seqs}: the ear and eye rows of every canvas on the tape (every day file, in order). A moment with no eye row has no source."""
    out: Dict[str, Dict[str, object]] = {}
    for f in sorted(Path(tape_dir).glob("*.jsonl")):
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get("sense") not in ("eye", "ear"):
                    continue
                meta = r.get("meta") or {}
                m = meta.get("moment")
                if m is None:
                    continue
                d = out.setdefault(str(m), {"source": None, "kind": None, "seqs": []})
                d["seqs"].append(int(r["seq"]))
                if r["sense"] == "eye":
                    d["source"], d["kind"] = meta.get("source"), meta.get("kind")
    return out


def _timings(p) -> Dict[int, Dict[str, object]]:
    out: Dict[int, Dict[str, object]] = {}
    with Path(p).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out[int(r["seq"])] = r
    return out


def _median(v: Sequence[float]) -> Optional[float]:
    s = sorted(v)
    if not s:
        return None
    return s[len(s) // 2] if len(s) % 2 else (s[len(s) // 2 - 1] + s[len(s) // 2]) / 2


def _canvas_side(tm, seqs_by_moment) -> Dict[str, object]:
    cpu, missing = [], 0
    for m in sorted(seqs_by_moment):
        ss = seqs_by_moment[m]
        if any(s not in tm or "cpu_ms" not in tm[s] for s in ss):
            missing += 1
            continue
        cpu.append(sum(float(tm[s]["cpu_ms"]) for s in ss))
    return {"n": len(cpu), "missing": missing, "mean_cpu_ms": (sum(cpu) / len(cpu)) if cpu else None, "median_cpu_ms": _median(cpu)}


def cost(tape_dir, off_t, on_t, off_arm=None, on_arm=None) -> Dict[str, object]:
    cv = _canvases(tape_dir)
    pops = {"maker": {m: d["seqs"] for m, d in cv.items() if d["source"] == "maker"},
            "scene_train": {m: d["seqs"] for m, d in cv.items() if d["source"] == "scene" and d["kind"] == "train"}}
    t_off, t_on = _timings(off_t), _timings(on_t)
    out: Dict[str, object] = {"bar": COST_BAR, "populations": {}}
    ok = True
    for name, sb in pops.items():
        a, b = _canvas_side(t_off, sb), _canvas_side(t_on, sb)
        rm = (b["mean_cpu_ms"] / a["mean_cpu_ms"]) if a["mean_cpu_ms"] and b["mean_cpu_ms"] else None
        rd = (b["median_cpu_ms"] / a["median_cpu_ms"]) if a["median_cpu_ms"] and b["median_cpu_ms"] else None
        passed = bool(rm is not None and rd is not None and rm <= COST_BAR and rd <= COST_BAR and a["n"] == b["n"] == len(sb) and len(sb) > 0)
        out["populations"][name] = {"canvases": len(sb), "off": a, "on": b, "ratio_mean": rm, "ratio_median": rd, "pass": passed}
        ok = ok and passed
    ca = [float(r["cpu_ms"]) for r in t_off.values() if "cpu_ms" in r]
    cb = [float(r["cpu_ms"]) for r in t_on.values() if "cpu_ms" in r]
    ra = (sum(cb) / len(cb)) / (sum(ca) / len(ca)) if ca and cb and sum(ca) > 0 else None
    p_all = bool(ra is not None and ra <= COST_BAR and len(ca) == len(cb) > 0)
    out["populations"]["all_rows"] = {"off": {"rows": len(ca), "mean_cpu_ms": (sum(ca) / len(ca)) if ca else None},
                                      "on": {"rows": len(cb), "mean_cpu_ms": (sum(cb) / len(cb)) if cb else None}, "ratio_mean": ra, "pass": p_all}
    out["populations_pass"] = bool(ok and p_all)
    out["launch"] = launch(off_arm, on_arm) if (off_arm and on_arm) else None
    out["verdict"] = ("NOT READ" if out["launch"] is None else "VOID" if out["launch"]["void"] else "PASS" if out["populations_pass"] else "FAIL")
    out["pass"] = out["verdict"] == "PASS"
    return out


# ------------------------------------------------------------------------------------------------ I2 · the token absent changes nothing
def is_turn(r) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "turn"


def canon(r) -> str:
    return json.dumps(r, sort_keys=True)


def canon_list(rows) -> str:
    return json.dumps(list(rows), sort_keys=True)


def i2(off_rows: Sequence[Dict], i1_rows: Sequence[Dict]) -> Dict[str, object]:
    """OFF's journal with its turn rows removed against the replay under the life's own genome, row for row (brain `learn`/`calibrate` rows and answers included —
    journal_diff.py's default drops those, so it cannot see a changed one)."""
    rest = [r for r in off_rows if not is_turn(r)]
    first = None
    for k, (a, b) in enumerate(zip(rest, i1_rows)):
        if canon(a) != canon(b):
            first = {"row": k, "seq": a.get("seq"), "off": canon(a)[:200], "i1": canon(b)[:200]}
            break
    return {"rows_off": len(off_rows), "turn_rows_dropped": len(off_rows) - len(rest), "rows_compared": len(rest), "rows_i1": len(i1_rows),
            "first_difference": first, "pass": bool(first is None and len(rest) == len(i1_rows) and len(i1_rows) > 0)}


def plant_one_character(rows: Sequence[Dict]) -> List[Dict]:
    """A copy of ROWS with ONE character of the middle kept (non-turn) row changed to another character of its class — still valid JSON, a different row."""
    kept = [k for k, r in enumerate(rows) if not is_turn(r)]
    if not kept:
        raise ReaderError("no kept row to plant on")
    mid = kept[len(kept) // 2]
    s = canon(rows[mid])
    for pos in range(len(s) - 1, -1, -1):
        ch = s[pos]
        if ch.isdigit():
            new = str((int(ch) + 1) % 10)
        elif ch.isalpha():
            new = "x" if ch != "x" else "y"
        else:
            continue
        try:
            r2 = json.loads(s[:pos] + new + s[pos + 1:])
        except ValueError:
            continue
        if canon(r2) != s:
            out = list(rows)
            out[mid] = r2
            return out
    raise ReaderError("the middle kept row has no character that can be changed")


def i2_control(off_rows, i1_rows, real_pass: bool) -> Dict[str, object]:
    if not real_pass:
        return {"caught": None, "why": "I2 already fails on the real inputs: the control says nothing more"}
    planted = plant_one_character(off_rows)
    changed = canon_list(planted) != canon_list(off_rows)
    return {"caught": bool(changed and not i2(planted, i1_rows)["pass"]), "planted_changed_the_rows": changed}


# ------------------------------------------------------------------------------------------------ T and G · from ON's journal
def _brain(rows):
    return [r for r in rows if r.get("kind", "brain") == "brain"]


def _kind_of_word(w: str, groups: Sequence[Sequence[str]]) -> str:
    """The type of a word at the last calibration, by the group that holds it: the group of «star» is the scene's shapes, of «red» its colours, of «big» its sizes."""
    for g in groups:
        gs = {str(x) for x in g}
        if w in gs:
            return "shape" if "star" in gs else "colour_size" if ("red" in gs or "big" in gs) else "other"
    return "not_typed"


def walk(rows) -> Dict[str, object]:
    """One pass over ON's brain rows in journal order: the maker's turns with the state each one saw (its word's prior maker meetings — the turn precedes the learn —, whether the word
    was typed at the latest calibration BEFORE the turn, whether the word was already learned from the scene hand at its first maker meeting), and the calibrations."""
    scene_known: set = set()
    typed: set = set()
    groups: List[List[str]] = []
    cals: List[Dict[str, object]] = []
    learn_count: Dict[str, int] = collections.Counter()
    side: Dict[str, str] = {}
    turns: List[Dict[str, object]] = []
    for r in _brain(rows):
        act, w = r.get("act"), r.get("world") or "scene"
        if act == "calibrate":
            summ = r.get("summary") or {}
            groups = [[str(x) for x in g] for g in (summ.get("types") or [])]
            typed = {x for g in groups for x in g}
            cals.append({"seq": r.get("seq"), "calibrated_at": summ.get("calibrated_at"), "learned": summ.get("learned"), "mature": summ.get("mature"),
                         "words": summ.get("words"), "types": groups})
        elif act == "learn":
            words = list(dict.fromkeys(str(x) for x in (r.get("words") or [])))
            if w == "scene":
                scene_known.update(words)
            elif w == "maker":
                for x in words:
                    learn_count[x] += 1
        elif act == "turn" and w == "maker":
            heard = [str(x) for x in (r.get("heard") or [])]
            say = [str(x) for x in ((r.get("say") or {}).get("words") or [])] if r.get("say") else []
            word = heard[0] if len(heard) == 1 else None
            prior = learn_count[word] if word is not None else None
            if word is not None and prior == 0:
                side[word] = "shared" if word in scene_known else "maker-only"
            agreed = bool(say) and any(x in heard for x in say)
            if not say:
                sk = "silent"
            elif agreed:
                sk = "true"
            else:
                sk = _kind_of_word(next(x for x in say if x not in heard), groups)
            turns.append({"i": len(turns), "seq": r.get("seq"), "heard": heard, "word": word, "say": say, "agreed": agreed, "say_kind": sk,
                          "meeting": (None if prior is None else prior + 1), "typed": bool(word is not None and word in typed),
                          "before_first_calibration": not cals, "side": (side.get(word) if word is not None else None),
                          "surprise": r.get("surprise")})
    return {"turns": turns, "calibrations": cals, "learn_count": dict(learn_count), "typed_last": sorted(typed), "groups_last": groups}


def _null(arm: List[Dict[str, object]], draws: int, seed: int) -> List[int]:
    """The dealt-targets null: the arm's true words permuted among the same canvases, every say fixed; the agreed count of each draw."""
    rng = random.Random(seed)
    words = [t["word"] for t in arm]
    says = [set(t["say"]) for t in arm]
    out = []
    for _ in range(draws):
        rng.shuffle(words)
        out.append(sum(1 for w, s in zip(words, says) if w in s))
    return out


def t_reading(rows, ks: Sequence[int] = TRANSFER_KS, draws: int = NULL_DRAWS, seed: int = NULL_SEED) -> Dict[str, object]:
    W = walk(rows)
    one_word = [t for t in W["turns"] if t["word"] is not None]
    out: Dict[str, object] = {"ks": list(ks), "draws": draws, "seed": seed, "shared": {}, "maker_only_comparison": "STRUCK (A1.3): 0 by construction (the turn precedes the learn; young 3)"}
    for k in ks:
        arm = [t for t in one_word if t["side"] == "shared" and t["meeting"] <= k]
        n = len(arm)
        agreed = sum(1 for t in arm if t["agreed"])
        null = _null(arm, draws, seed) if n else []
        p95 = sorted(null)[math.ceil(0.95 * draws) - 1] if null else None
        out["shared"][f"k{k}"] = {"k": k, "n": n, "agreed": agreed, "silent": sum(1 for t in arm if t["say_kind"] == "silent"),
                                  "typed": sum(1 for t in arm if t["typed"]), "words": sorted({t["word"] for t in arm}),
                                  "null_p95": p95, "null_max": (max(null) if null else None), "null_mean": ((sum(null) / len(null)) if null else None),
                                  "pass_line": (None if p95 is None else p95 + 1), "shown": (None if p95 is None else bool(agreed > p95)),
                                  "misses": [{"word": t["word"], "meeting": t["meeting"], "said": (t["say"] or None), "typed": t["typed"]} for t in arm if not t["agreed"]]}
    mo = [t for t in one_word if t["side"] == "maker-only" and t["meeting"] <= max(ks)]
    kinds = collections.Counter(t["say_kind"] for t in mo)
    out["over_extension"] = {"n": len(mo), "kinds": dict(kinds), "typed": sum(1 for t in mo if t["typed"]),
                             "before_first_calibration": sum(1 for t in mo if t["before_first_calibration"]),
                             "turns": [{"word": t["word"], "meeting": t["meeting"], "said": (t["say"] or None), "kind": t["say_kind"], "typed": t["typed"],
                                        "before_first_calibration": t["before_first_calibration"]} for t in mo]}
    return out


def g_reading(rows, k: int = LAST_K, young: int = YOUNG) -> Dict[str, object]:
    W = walk(rows)
    turns = W["turns"]
    cut = turns[-k:]
    n = len(cut)
    said = sum(1 for t in cut if t["say"])
    agreed = sum(1 for t in cut if t["agreed"])
    typed = sum(1 for t in cut if t["typed"])
    cnt = collections.Counter(t["word"] for t in cut if t["word"] is not None)
    commonest = cnt.most_common(1)[0] if cnt else (None, 0)
    sur = [float(t["surprise"]) for t in cut if t["surprise"] is not None]
    said_all = sum(1 for t in turns if t["say"])
    agreed_all = sum(1 for t in turns if t["agreed"])
    typed_words = set(W["typed_last"])
    maker_words = {w: {"meetings": m, "typed_at_last_calibration": w in typed_words} for w, m in sorted(W["learn_count"].items())}
    first_say: Dict[str, Optional[int]] = {w: None for w in maker_words if w in typed_words}
    for t in turns:
        if t["word"] in first_say and first_say[t["word"]] is None and t["word"] in t["say"]:
            first_say[t["word"]] = t["i"]
    tm = {w: {"meetings": maker_words[w]["meetings"], "first_agreed_say_turn": i} for w, i in first_say.items()}
    cals = W["calibrations"]
    series = None
    mturns = [r for r in _brain(rows) if r.get("act") == "turn" and r.get("world") == "maker"]
    if mturns:
        series = WR.read(mturns, window=100)["worlds"].get("maker")
    return {"maker_turns": len(turns), "k": k,
            "last_k": {"k": k, "n": n, "fewer_than_k": n < k, "agreed": agreed, "agree_over_all": ((agreed / n) if n else None), "said": said,
                       "say_rate": ((said / n) if n else None), "typed": typed, "ceiling": ((typed / n) if n else None),
                       "floor_commonest_word": ((commonest[1] / n) if n else None), "commonest_word": commonest[0],
                       "surprise": ((sum(sur) / len(sur)) if sur else None), "distinct_said": len({x for t in cut for x in t["say"]})},
            "prediction_last100_true_above_0.8": (None if n < k else bool(agreed / n > 0.8)),
            "maker_agree_rate_all": ((agreed_all / said_all) if said_all else None), "maker_said_all": said_all,
            "typed_maker_words": tm,
            "prediction_every_typed_maker_word_said_truly": (None if not tm else all(v["first_agreed_say_turn"] is not None for v in tm.values())),
            "calibrations": cals, "last_calibration": (cals[-1] if cals else None),
            "maker_words": maker_words, "n_maker_words": len(maker_words), "young": young, "series": series}


# ------------------------------------------------------------------------------------------------ the report
def _f(v, nd: int = 3) -> str:
    return "—" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def _sg(v) -> str:
    return "—" if v is None else f"{v:+.3f}"


def report(o: Dict[str, object]) -> List[str]:
    L = [f"HEARS-2 bench reading (PREREG-HEARS-2 §2 + AMENDMENT 1) · OFF = {o['labels']['off']} · ON = {o['labels']['on']}"]
    L.append("  P · the scene words, paired item by item (a READING, no bar). The paired population is the items COVERED and GRADABLE in BOTH arms "
             "(M1: two or three things), the grader's own pair rule; the smallest passing gap is 10 / n over THAT n:")
    for tset in (*SETS, "pooled"):
        for mark, _go in MARKS:
            d = o["pairs"][tset][mark]
            L.append(f"    {tset:6s} {mark:3s} n {d['n_pair']:4d} · OFF {_f(d['off_rate'])} · ON {_f(d['on_rate'])} · gap {_sg(d['gap'])} · smallest passing gap "
                     f"{_f(d['smallest_passing_gap'])} · discordant ON-right {d['discordant_on_right']} / OFF-right {d['discordant_off_right']} · "
                     f"p(ON worse) {_f(d['p_on_worse'])} · items off {d['n_items_off']} on {d['n_items_on']} both {d['n_items_both']} "
                     f"(only off {d['only_off']} / only on {d['only_on']}) · left out of the pair {d['excluded_in_both']} · coverage only-off "
                     f"{d['covered_only_off']} / only-on {d['covered_only_on']}"
                     f"{' · WITHIN NOISE' if d['within_noise'] else ''}")
    L.append("  P · the rates the grade holds only as rates (no item rows), each beside its own 10 / n:")
    for tset in SETS:
        for name, d in o["aggregates"][tset].items():
            L.append(f"    {tset:6s} {name:13s} OFF {_f(d['off'])} (n {_f(d['n_off'])}) · ON {_f(d['on'])} (n {_f(d['n_on'])}) · gap {_sg(d['gap'])} · "
                     f"smallest passing gap {_f(d['smallest_passing_gap'])}")
    L.append("  P · the six tests' verdicts, OFF → ON: " + " · ".join(f"{k} {v['off']}→{v['on']}{' (CHANGED)' if v['changed'] else ''}" for k, v in o["verdicts"].items()))
    sp = o.get("splits")
    if sp:
        L.append("  P · the discordant items split (A1.5; pooled over both sittings; each cell: paired n, ON-right / OFF-right):")
        for mark, d in sp.items():
            cl = " · ".join(f"{c} n {v['n_pair']} ({v['on_right']}/{v['off_right']})" for c, v in d["by_class"].items() if v["n_pair"])
            th = " · ".join(f"{t} n {v['n_pair']} ({v['on_right']}/{v['off_right']})" for t, v in d["by_third"].items())
            L.append(f"    {mark}: by phrase class: {cl} · by third of the sitting: {th} · items with no ask on the tape {d['unlocated_items']} · outside a sitting {d['unplaced_items']}")
            for x in d["discordant"]:
                L.append(f"      {mark} {x['set']} {x['item']} {x['direction']} · {x['phrase']} [{x['class']}] · third {x['third']} · maker canvases since the sitting began {x['maker_canvases_since_begin']}")
    t = o.get("T")
    if t:
        L.append(f"  T · TRANSFER (a reading, A1.3; the maker-only comparison is struck: {t['maker_only_comparison']}). The SHARED words' first k maker meetings, agreed / ALL turns, "
                 f"against {t['draws']} dealt-targets draws (the maker's words permuted among the same canvases, says fixed; seed {t['seed']}); SHOWN iff agreed > the null's p95:")
        for key, s in t["shared"].items():
            L.append(f"    k = {s['k']}: shared words {s['words']} · agreed {s['agreed']} of {s['n']} (silent {s['silent']}, word typed at the turn {s['typed']}) · null p95 {_f(s['null_p95'])} "
                     f"(max {_f(s['null_max'])}, mean {_f(s['null_mean'])}) · pass line {_f(s['pass_line'])} → shown {s['shown']}")
            for m in s["misses"]:
                L.append(f"      miss: {m['word']} meeting {m['meeting']} said {m['said']} typed {m['typed']}")
        oe = t["over_extension"]
        L.append(f"    over-extension reading, the maker-only words' first meetings (n {oe['n']}): what was said {oe['kinds']} · word typed at the turn {oe['typed']} · "
                 f"before the first calibration {oe['before_first_calibration']}")
    g = o.get("G")
    if g:
        lk = g["last_k"]
        L.append(f"  G · GROWTH (a reading, A1.4): maker turns {g['maker_turns']} · the LAST {lk['k']} (n {lk['n']}{', FEWER than k' if lk['fewer_than_k'] else ''}): "
                 f"agreed {lk['agreed']} of {lk['n']} = {_f(lk['agree_over_all'])} (agreed / ALL; says {lk['said']}) · ceiling {_f(lk['ceiling'])} (turns whose word was typed: "
                 f"{lk['typed']}) · floor, always the commonest word «{lk['commonest_word']}»: {_f(lk['floor_commonest_word'])} · surprise {_f(lk['surprise'])} · distinct said "
                 f"{lk['distinct_said']} · prediction «above 0.8»: {g['prediction_last100_true_above_0.8']}")
        L.append(f"    every maker word typed at the last calibration said truly at least once: {g['prediction_every_typed_maker_word_said_truly']} · "
                 + ", ".join(f"{w} (meetings {v['meetings']}, first true say at maker turn {v['first_agreed_say_turn']})" for w, v in g["typed_maker_words"].items()))
        lc = g["last_calibration"]
        L.append(f"    calibrations (at, mature) {[(c['calibrated_at'], c['mature']) for c in g['calibrations']]} · the last: learned {_f(lc and lc['learned'])} mature "
                 f"{_f(lc and lc['mature'])} · maker words {g['n_maker_words']}: "
                 + ", ".join(f"{w} {v['meetings']}{'✓' if v['typed_at_last_calibration'] else '✗'}" for w, v in g["maker_words"].items()))
        sr = g.get("series")
        if sr:
            for w_ in sr["windows"]:
                L.append(f"    maker window from {w_['from']:5d} n {w_['n']:4d} say {_f(w_['say_rate'])} agreed/said {_f(w_['agree_rate'])} ask {_f(w_['ask_rate'])} "
                         f"surprise {_f(w_['surprise'])} distinct {w_['distinct_said']}")
    x = o["X"]
    L.append(f"  X · EXIST by any hand: ON exist {_f(x['exist'])} over {_f(x['n_cited'])} citations (with a truth {_f(x['n_with_truth'])}) · cited by world "
             f"{x['cited_by_world'] if x['cited_by_world'] is not None else 'NOT RECORDED by this grade'} · maker citations {_f(x['maker_citations'])} "
             f"(the by-any-hand road exercised: {x['exercised_on_a_maker_citation']}) · carry {_f(x['carry'])} null p95 {_f(x['null_p95'])} · OFF exist "
             f"{_f(x['off']['exist'])} over {_f(x['off']['n_cited'])}")
    if x["plant"] is None:
        L.append("    the planted control (ONE cited moment spoiled, regraded): NOT GIVEN — X is not graded without it")
    else:
        L.append(f"    the planted control: exist {_f(x['plant']['exist'])} over {_f(x['plant']['n_cited'])} · caught (< 1): {x['plant_caught']} · exactly one "
                 f"citation spoiled ((n−1)/n): {x['plant_is_one_spoiled_citation']} → X {_fmt_verdict(x['pass'])}")
    c = o.get("C")
    if c:
        lc_ = c["launch"]
        if lc_ is None:
            L.append("  C · COST: NO launch record given (--off-arm / --on-arm): the arms' overlap is unknown, so C cannot pass (A1.1)")
        else:
            L.append(f"  C · launch (A1.1): start skew {lc_['start_skew_s']:.1f} s · wall OFF {lc_['off']['wall_s']:.0f} s ON {lc_['on']['wall_s']:.0f} s · overlap {_f(lc_['overlap'])} "
                     f"(min {lc_['min_overlap']}) → {'VOID — re-run the pair' if lc_['void'] else 'ok'} · loadavg OFF {lc_['off']['loadavg_start']} → {lc_['off']['loadavg_end']} · "
                     f"ON {lc_['on']['loadavg_start']} → {lc_['on']['loadavg_end']} · PSI cpu OFF {lc_['off']['pressure_cpu_start']} → {lc_['off']['pressure_cpu_end']} · "
                     f"ON {lc_['on']['pressure_cpu_start']} → {lc_['on']['pressure_cpu_end']}")
        L.append(f"  C · COST, the mind's CPU per canvas ON over OFF (the drive law's canvas = its ear + eye rows; bar ≤ {c['bar']} on EACH population, A1.2) → {c['verdict']}:")
        for name, p in c["populations"].items():
            if name == "all_rows":
                L.append(f"    {name:12s} rows off {p['off']['rows']} on {p['on']['rows']} · mean cpu_ms off {_f(p['off']['mean_cpu_ms'])} on {_f(p['on']['mean_cpu_ms'])} · "
                         f"ratio {_f(p['ratio_mean'])} → {'PASS' if p['pass'] else 'FAIL'}")
            else:
                L.append(f"    {name:12s} canvases {p['canvases']} · timed off {p['off']['n']} (missing {p['off']['missing']}) on {p['on']['n']} (missing {p['on']['missing']}) · "
                         f"cpu_ms mean off {_f(p['off']['mean_cpu_ms'])} on {_f(p['on']['mean_cpu_ms'])} · median off {_f(p['off']['median_cpu_ms'])} on {_f(p['on']['median_cpu_ms'])} · "
                         f"ratio mean {_f(p['ratio_mean'])} median {_f(p['ratio_median'])} → {'PASS' if p['pass'] else 'FAIL'}")
    i = o.get("I2")
    if i:
        L.append(f"  I2 · OFF without its turn rows vs the replay under the life's own genome: OFF rows {i['rows_off']} (turn rows dropped {i['turn_rows_dropped']}) → compared "
                 f"{i['rows_compared']} vs I1 {i['rows_i1']} · first difference {i['first_difference']} → {'PASS' if i['pass'] else 'FAIL'}")
    cp = o["controls"]
    L.append(f"  controls (run on THESE inputs): P {json.dumps(cp['P'])} · I2 {json.dumps(cp['I2']) if cp['I2'] is not None else 'not run'}")
    L.append("  BARS: " + " · ".join(f"{k} {v}" for k, v in o["bars"].items()))
    return L


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="hears_read")
    for name in ("off", "on", "on-plant", "tape", "off-timings", "on-timings", "off-arm", "on-arm", "on-journal", "off-journal", "i1-journal", "out", "plant-x-journal", "plant-x-out"):
        ap.add_argument("--" + name)
    a = ap.parse_args(argv)
    if a.plant_x_journal:
        if not a.plant_x_out:
            ap.error("--plant-x-journal needs --plant-x-out")
        print(json.dumps(make_x_plant(a.plant_x_journal, a.plant_x_out), indent=1, sort_keys=True))
        return 0
    if not (a.off and a.on and a.out):
        ap.error("--off, --on and --out are required")
    if bool(a.off_timings) != bool(a.on_timings):
        raise ReaderError("C needs --off-timings and --on-timings together")
    if a.off_timings and not a.tape:
        raise ReaderError("C needs --tape (the canvases' ear and eye rows) beside the timings")
    do_cost = bool(a.tape and a.off_timings and a.on_timings)           # --tape alone is enough for the splits
    if bool(a.off_arm) != bool(a.on_arm):
        raise ReaderError("the launch record needs --off-arm and --on-arm together")
    i2_args = [a.off_journal, a.i1_journal]
    if any(i2_args) and not all(i2_args):
        raise ReaderError("I2 needs --off-journal and --i1-journal together")
    off, on = load_grade(a.off), load_grade(a.on)
    plant = load_grade(a.on_plant) if a.on_plant else None
    o: Dict[str, object] = {"labels": {"off": off.get("label"), "on": on.get("label")}, "pairs": pairs(off, on), "aggregates": aggregates(off, on),
                            "verdicts": verdicts(off, on), "X": x_mark(off, on, plant)}
    o["controls"] = {"P": p_control(off, on), "I2": None}
    if a.tape:
        o["splits"] = splits(off, on, tape_index(a.tape))
    if a.on_journal:
        rows = WR.read_journal(Path(a.on_journal))
        o["T"], o["G"] = t_reading(rows), g_reading(rows)
    if do_cost:
        o["C"] = cost(a.tape, a.off_timings, a.on_timings, a.off_arm, a.on_arm)
    if all(i2_args):
        off_rows = [json.loads(line) for line in Path(a.off_journal).read_text().splitlines() if line.strip()]
        i1_rows = [json.loads(line) for line in Path(a.i1_journal).read_text().splitlines() if line.strip()]
        o["I2"] = i2(off_rows, i1_rows)
        o["controls"]["I2"] = i2_control(off_rows, i1_rows, o["I2"]["pass"])
    ctl = [v["caught"] for v in o["controls"].values() if v is not None and v.get("caught") is not None]
    o["bars"] = {"C": ("NOT READ" if "C" not in o else o["C"]["verdict"]),
                 "X": ("NOT READ" if o["X"]["pass"] is None else "PASS" if o["X"]["pass"] else "FAIL"),
                 "I2": ("NOT READ" if "I2" not in o else "PASS" if o["I2"]["pass"] else "FAIL"),
                 "controls": ("NOT RUN" if not ctl else "CAUGHT" if all(ctl) else "MISSED")}
    o["inputs"] = {name: {"path": str(p), "sha256": _sha(p if Path(p).is_file() else Path(p) / "grade.json")}
                   for name, p in (("off", a.off), ("on", a.on), ("on_plant", a.on_plant), ("off_timings", a.off_timings), ("on_timings", a.on_timings),
                                   ("off_arm", a.off_arm), ("on_arm", a.on_arm), ("on_journal", a.on_journal), ("off_journal", a.off_journal),
                                   ("i1_journal", a.i1_journal)) if p}
    lines = report(o)
    print("\n".join(lines))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "hears.json").write_text(json.dumps(o, indent=1, sort_keys=True))
    (out / "hears.txt").write_text("\n".join(lines) + "\n")
    bad = o["bars"]["C"] in ("FAIL", "VOID") or o["bars"]["X"] == "FAIL" or o["bars"]["I2"] == "FAIL" or o["bars"]["controls"] == "MISSED"
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ReaderError as e:
        print(f"hears_read: {e}", file=sys.stderr)
        sys.exit(2)
