# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 10:46 +0400 — PREREG-HEARS-2 §2: tools/brain/hears_read.py's tests, written BEFORE the reader was rebuilt (the seat's 09-30 draft was never run).
# Each mark reads what the law says, and a planted defect must be CAUGHT by the mark it targets; every plant asserts that it changed the bytes (#247 (5)). The pair population is pinned against
# the grader's own reported n on the real grade of the closed life (188 / 201 / 58 / 57 / 56).
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:08 +0400 — AMENDMENT 1 (signed by the architect and the seat): C by populations with the launch overlap (A1.1, A1.2: the maker canvases by median
# AND mean, the whole replay, the scene canvases), T against the dealt-targets null at k 3 and k 1 (A1.3), G over EXACTLY the last 100 (A1.4), the discordant items split by phrase class and
# position (A1.5); every temp dir is removed (the first version leaked them into the data-disk TMPDIR).
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:15 +0400 — a test for the tape-only call, found by running the reader on the real live journal; the whole file was then put through a
# mutation sweep (17 mutants of the reader, each caught by a named test; the harness first proved it loaded the mutant — its first version imported the real module and «caught» nothing).
"""tests/tools/test_hears_read.py — tools/brain/hears_read.py."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.brain import drive_gate as DG
from tools.brain import grade_life as GL
from tools.brain import hears_read as H

SETS = ("fresh", "s1b1")
REAL_GRADE = Path("/data/dev/brain-runs/organ/rung3/brain-full-20261102/grade-full/grade.json")


class Tmp(unittest.TestCase):
    def mk(self, prefix: str = "hears-read-") -> Path:
        d = Path(tempfile.mkdtemp(prefix=prefix))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d


# ------------------------------------------------------------------------------------------------ fixtures: a grade.json of two sittings
def _row(item_id, correct, covered=True, gradable=True, n_things=2):
    return {"item_id": item_id, "correct": correct, "covered": covered, "gradable": gradable, "n_things": n_things, "answered": True,
            "forced": False, "chance": 0.5, "none": False, "none_i": False, "none_ii": False, "template": "T1", "types": []}


# (kind, how many, how many of the first of them are right in the OFF arm): P covered+gradable with 2 things (the paired population of every mark), S covered+gradable with ONE thing (inside M3 and
# M6's population, OUTSIDE M1's graded one), U not covered, N not gradable
BASE = {
    ("fresh", "M1"): [("P", 14, 10), ("S", 2, 2), ("U", 2, 0), ("N", 2, 0)],
    ("s1b1", "M1"): [("P", 10, 6), ("S", 1, 1), ("U", 1, 0), ("N", 1, 0)],
    ("fresh", "M3"): [("P", 10, 7), ("U", 2, 0)],
    ("s1b1", "M3"): [("P", 8, 5), ("U", 1, 0)],
    ("fresh", "M6"): [("P", 6, 3), ("U", 2, 0)],
    ("s1b1", "M6"): [("P", 6, 4), ("N", 1, 0)],
}


def _rows_of(tset, mark):
    out, k = [], 0
    for kind, n, right in BASE[(tset, mark)]:
        for j in range(n):
            out.append(_row(f"{mark}:{tset}:{k:03d}", j < right, covered=(kind in ("P", "S")), gradable=(kind != "N"), n_things=(1 if kind == "S" else 2)))
            k += 1
    return out


def _rate(rows):
    return (sum(1 for r in rows if r["correct"]) / len(rows)) if rows else None


def make_grade(label, flips=(), drop=(), m2a=(0.81, 400), bar_pass=None, m4a=None, m5="PASS", m6="PASS"):
    """A grade.json with the keys the reader reads and nothing it does not (the real one has hundreds more)."""
    flips, drop = set(flips), set(drop)
    items, sets_ = {}, {}
    for tset in SETS:
        items[tset] = {}
        for mark in ("M1", "M3", "M6"):
            rows = []
            for r in _rows_of(tset, mark):
                if (tset, mark, r["item_id"]) in drop:
                    continue
                if (tset, mark, r["item_id"]) in flips:
                    r["correct"] = not r["correct"]
                rows.append(r)
            items[tset][mark] = rows
        m1 = [r for r in items[tset]["M1"] if r["covered"] and r["gradable"] and r["n_things"] in (2, 3)]
        m3 = [r for r in items[tset]["M3"] if r["covered"] and r["gradable"]]
        sets_[tset] = {"marks": {"M1": {"graded": {"covered": _rate(m1), "n_covered": len(m1)}},
                                 "M3": {"all": {"covered": _rate(m3), "n_covered": len(m3)}},
                                 "roads": {"LAW": {"M2a": {"all": {"refusal": m2a[0], "n": m2a[1], "presence": m2a[1]}},
                                                   "M2b": {"graded": {"correct": 0.7, "n": 48}}, "false_refusal": 0.05}}}}
    ok = {"M1": True, "M2a": True, "M2b": False, "M3": True, "M6": True}
    ok.update(bar_pass or {})
    bars = {k: {"value": 0.9, "n": 100, "pass": v, "underpowered": False} for k, v in ok.items()}
    return {"label": label, "world_seed": 20261102, "items": items, "sets": sets_, "bars": bars,
            "M4a": m4a if m4a is not None else {"exist": 1.0, "n_cited": 10, "n_with_truth": 7, "cited_by_world": {"maker": 3, "scene": 7},
                                                 "carry": 0.95, "null_p95": 0.58, "verdict": "PASS"},
            "M5": {"verdict": m5, "refused": 1.0, "named": 1.0, "n": 400},
            "M6_pooled": {"verdict": m6, "covered": 0.7, "n_covered": 12, "n_items": 14}}


def write_grade(d, g):
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    p = d / "grade.json"
    p.write_text(json.dumps(g, indent=1, sort_keys=True))
    return p


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------ fixtures: a tape, its timings, the arms' launch records, a journal
# scene training canvases sA, sB (an ear row and an eye row each), a scene SITTING canvas sC (never in the cost population), maker canvases mA, mB, and a shelf canvas
TAPE = [
    (1, "ear", "scene", "sA", None), (2, "eye", "scene", "sA", "train"),
    (3, "ear", "scene", "sB", None), (4, "eye", "scene", "sB", "train"),
    (5, "eye", "scene", "sC", "sitting"),
    (6, "ear", "maker", "mA", None), (7, "eye", "maker", "mA", None),
    (8, "ear", "maker", "mB", None), (9, "eye", "maker", "mB", None),
    (10, "eye", "shelf", "hA", None),
]
OFF_CPU = {1: 1.0, 2: 3.0, 3: 1.0, 4: 3.0, 5: 9.0, 6: 2.0, 7: 2.0, 8: 2.0, 9: 2.0, 10: 5.0}        # sA = sB = 4, mA = mB = 4
ON_CPU = {1: 1.5, 2: 3.5, 3: 1.5, 4: 3.5, 5: 9.0, 6: 6.0, 7: 6.0, 8: 6.0, 9: 6.0, 10: 5.0}         # sA = sB = 5 (x1.25), mA = mB = 12 (x3)
CHEAP_MAKER = {**ON_CPU, 6: 2.0, 7: 2.0, 8: 2.0, 9: 2.0}                                             # the maker canvases at 1x: every population under the bar


def write_tape(d, rows=TAPE):
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    with (d / "2026-10-03.jsonl").open("w") as f:
        for seq, sense, src, moment, kind in rows:
            meta = {"source": src, "moment": moment}
            if kind:
                meta["kind"] = kind
            f.write(json.dumps({"seq": seq, "sense": sense, "meta": meta}) + "\n")
    return d


def write_timings(p, cpu, rows=TAPE, skip=()):
    with Path(p).open("w") as f:
        for seq, sense, src, _m, _k in rows:
            if seq in skip:
                continue
            f.write(json.dumps({"seq": seq, "sense": sense, "source": src, "ms": cpu[seq] * 2.0, "cpu_ms": cpu[seq]}) + "\n")
    return Path(p)


def write_arm(p, start, end, load="1.00 1.00 1.00 1/100 1", psi="some avg10=0.00 avg60=0.00 avg300=0.00 total=0|"):
    Path(p).write_text("\n".join(["label x", f"start_epoch {start}", "start_iso t0", f"loadavg_start {load}", f"pressure_cpu_start {psi}", f"end_epoch {end}", "end_iso t1",
                                  f"loadavg_end {load}", f"pressure_cpu_end {psi}", "exit 0"]) + "\n")
    return Path(p)


def _learn(seq, world, words):
    r = {"kind": "brain", "act": "learn", "seq": seq, "moment": f"m{seq}", "at": "t", "words": words}
    if world != "scene":
        r["world"] = world
    return r


def _turn(seq, world, heard, say, surprise=0.1, n_hyp=1):
    r = {"kind": "brain", "act": "turn", "seq": seq, "moment": f"m{seq}", "at": "t", "heard": heard, "say": ({"words": say} if say else None),
         "surprise": surprise, "n_hyp": n_hyp, "ask": None, "expected": [[None]]}
    if world != "scene":
        r["world"] = world
    return r


def _calibrate(seq, types, learned):
    return {"kind": "brain", "act": "calibrate", "seq": seq, "moment": "m", "at": "t",
            "summary": {"calibrated_at": learned, "calibrations": 1, "episodes": 2 * learned, "learned": learned, "mature": sum(len(g) for g in types),
                        "tau_point": -1.0, "words": sum(len(g) for g in types), "types": types}}


WORDS4 = ["star", "bar", "dot", "cup"]
ALL_TYPES = [["star", "bar", "dot", "cup"], ["red"], ["big"]]


def maker_journal(n=120, early_types=ALL_TYPES, last_types=ALL_TYPES, never_true=(), mode="normal"):
    """Six scene canvases teach «star», an early calibration, then n maker turns i = 0..n-1 of the word WORDS4[i % 4]. normal: the say is WRONG for i < 20, for every tenth after that and for
    the words in never_true, right otherwise — over the LAST 100 turns (n 120) agreed is 90 and over all 120 it is 90 of 120 said. silent: no say. rare: a true say on one turn in ten."""
    rows, seq = [], 100
    for _ in range(6):
        rows += [_turn(seq, "scene", ["star", "red"], ["star"]), _learn(seq, "scene", ["star", "red"])]
        seq += 1
    rows.append(_calibrate(seq, early_types, 6))
    seq += 1
    for i in range(n):
        w = WORDS4[i % 4]
        if mode == "silent":
            say = None
        elif mode == "rare":
            say = [w] if i % 10 == 5 else None
        else:
            say = ["zzz"] if (i < 20 or i % 10 == 0 or w in never_true) else [w]
        rows += [_turn(seq, "maker", [w], say), _learn(seq, "maker", [w])]
        seq += 1
    rows.append(_calibrate(seq, last_types, 6 + n))
    return rows


SHARED6 = ["star", "ring", "cross", "square", "triangle", "circle"]


def t_journal(say_of, cal_after=0):
    """Four scene canvases teach each of the six shared words (and «red»); then the maker names each shared word and two maker-only words (bar, dot) three times, in rounds. The
    calibration (types: the six shapes, «red», «big») sits before maker turn number cal_after. say_of(word, meeting) is the say of that turn (a list of words, or None)."""
    rows, seq = [], 1
    for w in SHARED6:
        for _ in range(4):
            rows += [_turn(seq, "scene", [w, "red"], [w]), _learn(seq, "scene", [w, "red"])]
            seq += 1
    plan = [(w, m) for m in (1, 2, 3) for w in SHARED6 + ["bar", "dot"]]
    cal = _calibrate(0, [SHARED6, ["red"], ["big"]], 24)
    for idx, (w, m) in enumerate(plan):
        if idx == cal_after:
            rows.append({**cal, "seq": seq})
            seq += 1
        rows += [_turn(seq, "maker", [w], say_of(w, m)), _learn(seq, "maker", [w])]
        seq += 1
    return rows


def write_jsonl(p, rows):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return p


# a tape with the two sittings' asks (begin, every item of M1 / M3 / M6 in index order, end) and a maker eye row after every third ask
PHRASES = [["star"], ["red", "star"], ["white", "star"]]            # item index % 3: a shape only / a colour word / «white»


def write_ask_tape(d):
    d = Path(d)
    (d / "payload").mkdir(parents=True, exist_ok=True)
    rows, state = [], {"seq": 0, "asks": 0}
    where: dict = {}
    maker: list = []

    def ask(payload):
        state["seq"] += 1
        state["asks"] += 1
        name = f"payload/{state['seq']:09d}.json"
        (d / name).write_text(json.dumps(payload))
        rows.append({"seq": state["seq"], "sense": "ask", "meta": {"source": "scene", "moment": f"ask{state['seq']}"}, "payload": name})
        s = state["seq"]
        if state["asks"] % 3 == 0:
            state["seq"] += 1
            maker.append(state["seq"])
            rows.append({"seq": state["seq"], "sense": "eye", "meta": {"source": "maker", "moment": f"mk{state['seq']}"}})
        return s

    for tset in SETS:
        where[tset] = {"begin": ask({"form": "begin", "set": tset})}
        names = sorted((r["item_id"] for mark in ("M1", "M3", "M6") for r in _rows_of(tset, mark)), key=lambda s: (int(s.split(":")[2]), s))
        for name in names:
            where[name] = ask({"form": "point", "item": name, "mark": name.split(":")[0], "phrase": PHRASES[int(name.split(":")[2]) % 3]})
        where[tset]["end"] = ask({"form": "end", "set": tset})
    with (d / "2026-10-03.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return d, where, maker


# ------------------------------------------------------------------------------------------------ the statistics, against their sources
class Statistics(unittest.TestCase):
    def test_the_sign_test_is_the_graders_own(self) -> None:
        for b, c in ((0, 0), (1, 0), (0, 1), (5, 2), (9, 9), (30, 4)):
            self.assertEqual(H.sign_test(b, c), GL.sign_test(b, c), (b, c))


# ------------------------------------------------------------------------------------------------ P: the scene words, paired item by item
class PairedScene(Tmp):
    def test_identical_arms_read_zero_and_the_population_is_the_graders_pair_population(self) -> None:
        off = make_grade("off")
        p = H.pairs(off, copy.deepcopy(off))
        m1 = p["fresh"]["M1"]
        self.assertEqual((m1["n_items_off"], m1["n_items_on"], m1["n_items_both"]), (20, 20, 20))
        self.assertEqual((m1["only_off"], m1["only_on"]), (0, 0))
        self.assertEqual(m1["n_pair"], 14)                       # covered AND gradable AND two or three things, in BOTH — the grader's pair()
        self.assertEqual(m1["excluded_in_both"], 6)              # the 2 one-thing, 2 uncovered, 2 not gradable: counted, never dropped silently
        self.assertAlmostEqual(m1["off_rate"], 10 / 14)
        self.assertAlmostEqual(m1["on_rate"], 10 / 14)
        self.assertEqual(m1["gap"], 0.0)
        self.assertAlmostEqual(m1["smallest_passing_gap"], 10 / 14)      # 10 / n over the PAIRED n, not over every graded item (that would read 10 / 18)
        self.assertEqual((m1["discordant_on_right"], m1["discordant_off_right"]), (0, 0))
        self.assertTrue(m1["within_noise"])
        self.assertEqual(p["fresh"]["M3"]["n_pair"], 10)         # M3 and M6 take the one-thing rows too: only M1's graded population needs 2-3 things
        self.assertEqual(p["fresh"]["M6"]["n_pair"], 6)
        self.assertEqual(p["pooled"]["M1"]["n_pair"], 24)        # fresh + s1b1, as the grader's own pairing pools them
        self.assertAlmostEqual(p["pooled"]["M1"]["off_rate"], 16 / 24)
        self.assertEqual(p["pooled"]["M3"]["n_pair"], 18)
        self.assertEqual(p["pooled"]["M6"]["n_pair"], 12)

    def test_the_planted_flip_shows_in_the_discordant_counts_and_only_there(self) -> None:
        off = make_grade("off")
        on_same = make_grade("on")
        flip = ("fresh", "M1", "M1:fresh:003")                  # a paired item OFF got right
        on_plant = make_grade("on", flips=[flip])
        d = self.mk()
        a, b = write_grade(d / "a", on_same), write_grade(d / "b", on_plant)
        self.assertNotEqual(sha(a), sha(b), "the plant must change the bytes")
        diffs = [(s, m, x["item_id"]) for s in SETS for m in ("M1", "M3", "M6")
                 for x, y in zip(on_same["items"][s][m], on_plant["items"][s][m]) if x["correct"] != y["correct"]]
        self.assertEqual(diffs, [flip], "the plant must change exactly one item")
        base, p = H.pairs(off, on_same), H.pairs(off, on_plant)
        self.assertEqual((base["fresh"]["M1"]["discordant_off_right"], base["fresh"]["M1"]["discordant_on_right"]), (0, 0))
        m1 = p["fresh"]["M1"]
        self.assertEqual((m1["discordant_off_right"], m1["discordant_on_right"]), (1, 0))
        self.assertAlmostEqual(m1["on_rate"], 9 / 14)
        self.assertAlmostEqual(m1["gap"], -1 / 14)
        self.assertEqual(m1["p_on_worse"], 0.5)                  # P(X >= 1), X ~ Bin(1, 1/2)
        self.assertEqual(m1["p_on_better"], 1.0)
        self.assertTrue(m1["within_noise"])                      # one item cannot be told from noise at n 14: the smallest passing gap is 0.714
        self.assertEqual(p["pooled"]["M1"]["discordant_off_right"], 1)
        for other in (("fresh", "M3"), ("fresh", "M6"), ("s1b1", "M1"), ("s1b1", "M3"), ("s1b1", "M6")):
            q = p[other[0]][other[1]]
            self.assertEqual((q["discordant_off_right"], q["discordant_on_right"]), (0, 0), other)

    def test_a_flip_outside_the_paired_population_does_not_show(self) -> None:
        off = make_grade("off")
        for flip in (("fresh", "M1", "M1:fresh:014"),           # covered and gradable but ONE thing: outside M1's graded population
                     ("fresh", "M1", "M1:fresh:016"),           # not covered
                     ("fresh", "M1", "M1:fresh:018")):          # not gradable
            on = make_grade("on", flips=[flip])
            self.assertNotEqual(json.dumps(on, sort_keys=True), json.dumps(off, sort_keys=True), "the plant must change the bytes")
            m1 = H.pairs(off, on)["fresh"]["M1"]
            self.assertEqual((m1["discordant_off_right"], m1["discordant_on_right"], m1["n_pair"]), (0, 0, 14), flip)

    def test_an_item_in_one_arm_only_is_counted_and_never_silently_dropped(self) -> None:
        off = make_grade("off")
        on = make_grade("on", drop=[("fresh", "M1", "M1:fresh:000"), ("fresh", "M1", "M1:fresh:001")])
        m1 = H.pairs(off, on)["fresh"]["M1"]
        self.assertEqual((m1["n_items_off"], m1["n_items_on"], m1["n_items_both"]), (20, 18, 18))
        self.assertEqual((m1["only_off"], m1["only_on"]), (2, 0))
        self.assertEqual(m1["n_pair"], 12)

    def test_the_coverage_each_arm_has_inside_the_paired_items_is_printed(self) -> None:
        off = make_grade("off")
        on = copy.deepcopy(off)
        for r in on["items"]["fresh"]["M1"]:
            if r["item_id"] == "M1:fresh:002":
                r["covered"] = False                              # ON's eye lost one covered item: a coverage change is a finding of its own
        m1 = H.pairs(off, on)["fresh"]["M1"]
        self.assertEqual(m1["n_pair"], 13)
        self.assertEqual((m1["covered_only_off"], m1["covered_only_on"]), (1, 0))


class Splits(Tmp):
    """A1.5: the discordant items by phrase class and by third of the sitting, from the ask rows of the cut tape."""

    def test_the_phrase_classes(self) -> None:
        self.assertEqual(H.phrase_class(["star"]), "shape_only")
        self.assertEqual(H.phrase_class(["star", "ring"]), "shape_only")
        self.assertEqual(H.phrase_class(["red", "star"]), "colour_size")
        self.assertEqual(H.phrase_class(["big", "star"]), "colour_size")
        self.assertEqual(H.phrase_class(["white", "star"]), "white")           # «white» apart, even beside a size word
        self.assertEqual(H.phrase_class(["big", "white"]), "white")
        self.assertEqual(H.phrase_class([]), "no_phrase")
        self.assertEqual(H.phrase_class(None), "no_phrase")

    def test_the_thirds_of_a_sitting(self) -> None:
        s = {"begin": 1000, "end": 1300}
        self.assertEqual([H.position_third(x, s) for x in (1001, 1050, 1099, 1100, 1150, 1199, 1200, 1250, 1299)], [0, 0, 0, 1, 1, 1, 2, 2, 2])
        self.assertIsNone(H.position_third(1000, s))                          # the begin ask itself is not inside
        self.assertIsNone(H.position_third(1300, s))
        self.assertIsNone(H.position_third(1100, {"begin": 1000, "end": None}))
        self.assertIsNone(H.position_third(1100, None))

    def test_the_tape_index_reads_the_asks_the_sittings_and_the_makers_eye_rows(self) -> None:
        d, where, maker = write_ask_tape(self.mk())
        ti = H.tape_index(d)
        self.assertEqual(ti["sittings"]["fresh"], {"begin": where["fresh"]["begin"], "end": where["fresh"]["end"]})
        self.assertEqual(ti["maker_seqs"], maker)
        self.assertEqual(ti["items"]["M1:fresh:003"]["seq"], where["M1:fresh:003"])
        self.assertEqual(ti["items"]["M1:fresh:002"]["phrase"], ["white", "star"])
        self.assertEqual(len(ti["items"]), sum(len(_rows_of(s, m)) for s in SETS for m in ("M1", "M3", "M6")))

    def _split(self, flips):
        d, where, maker = write_ask_tape(self.mk())
        ti = H.tape_index(d)
        off, on = make_grade("off"), make_grade("on", flips=flips)
        return H.splits(off, on, ti), where, maker

    def test_the_planted_flip_lands_in_its_phrase_class_and_its_third(self) -> None:
        # index 3 → PHRASES[0] = a shape word only; index 2 → «white»; index 4 → a colour word. M1:fresh:002 and 003 and 004 are paired items OFF got right (the first 10 of 14).
        for name, cls in (("M1:fresh:003", "shape_only"), ("M1:fresh:002", "white"), ("M1:fresh:004", "colour_size")):
            sp, where, maker = self._split([("fresh", "M1", name)])
            m1 = sp["M1"]
            self.assertEqual(sum(v["off_right"] for v in m1["by_class"].values()), 1, name)
            self.assertEqual(m1["by_class"][cls]["off_right"], 1, name)
            self.assertEqual(sum(v["on_right"] for v in m1["by_class"].values()), 0, name)
            (x,) = m1["discordant"]
            self.assertEqual((x["item"], x["direction"], x["class"]), (name, "off_right", cls))
            b, e, s = where["fresh"]["begin"], where["fresh"]["end"], where[name]
            third = min(2, int(3 * (s - b) / (e - b)))
            self.assertEqual(x["third"], third + 1)
            self.assertEqual(m1["by_third"][H.THIRDS[third]]["off_right"], 1)
            self.assertEqual(x["maker_canvases_since_begin"], sum(1 for q in maker if b < q < s))
            for other in ("M3", "M6"):
                self.assertEqual(sp[other]["discordant"], [], other)

    def test_the_paired_items_are_counted_in_every_class_and_third_and_the_missing_are_counted(self) -> None:
        sp, _where, _maker = self._split([])
        m1 = sp["M1"]
        self.assertEqual(sum(v["n_pair"] for v in m1["by_class"].values()), 24)           # the pooled paired population of M1: 14 + 10
        self.assertEqual(sum(v["n_pair"] for v in m1["by_third"].values()), 24)
        self.assertEqual((m1["unlocated_items"], m1["unplaced_items"]), (0, 0))
        d = self.mk()
        write_tape(d / "bare")                                                             # a tape with no asks at all: every paired item is «unlocated», counted
        sp2 = H.splits(make_grade("off"), make_grade("on"), H.tape_index(d / "bare"))
        self.assertEqual(sp2["M1"]["unlocated_items"], 24)
        self.assertEqual(sum(v["n_pair"] for v in sp2["M1"]["by_class"].values()), 0)


class AggregatesAndVerdicts(unittest.TestCase):
    def test_the_rates_the_grade_holds_only_as_rates_are_read_with_their_own_smallest_gap(self) -> None:
        off, on = make_grade("off"), make_grade("on", m2a=(0.78, 400))
        a = H.aggregates(off, on)["fresh"]["M2a_refusal"]
        self.assertEqual((a["off"], a["on"], a["n_off"], a["n_on"]), (0.81, 0.78, 400, 400))
        self.assertAlmostEqual(a["gap"], -0.03)
        self.assertAlmostEqual(a["smallest_passing_gap"], 10 / 400)
        self.assertIn("M1_covered", H.aggregates(off, on)["s1b1"])
        self.assertEqual(H.aggregates(off, on)["fresh"]["M1_covered"]["n_off"], 14)

    def test_the_six_tests_verdicts_side_by_side_and_a_change_is_flagged(self) -> None:
        off = make_grade("off")
        on = make_grade("on", bar_pass={"M1": False}, m5="FAIL")
        v = H.verdicts(off, on)
        self.assertEqual(v["1"], {"off": "PASS", "on": "FAIL", "changed": True})
        self.assertEqual(v["3"], {"off": "PASS", "on": "PASS", "changed": False})
        self.assertEqual(v["5"], {"off": "PASS", "on": "FAIL", "changed": True})
        self.assertEqual(v["2b"]["off"], "FAIL")
        self.assertEqual(sorted(v), ["1", "2a", "2b", "3", "4a", "5", "6"])


# ------------------------------------------------------------------------------------------------ X: EXIST by any hand, and the plant
class ExistByAnyHand(Tmp):
    def _m4a(self, exist=1.0, n=10, by_world=None):
        return {"exist": exist, "n_cited": n, "n_with_truth": 7, "cited_by_world": by_world or {"maker": 3, "scene": 7}, "carry": 0.95,
                "null_p95": 0.58, "verdict": "PASS"}

    def test_exist_one_with_the_plant_caught_passes_and_prints_the_citations_by_world(self) -> None:
        on, off = make_grade("on"), make_grade("off")
        plant = make_grade("plant", m4a=self._m4a(exist=0.9, by_world={"?": 1, "maker": 3, "scene": 6}))       # exactly one of ten citations spoiled
        x = H.x_mark(off, on, plant)
        self.assertTrue(x["exist_holds"])
        self.assertTrue(x["plant_caught"])
        self.assertTrue(x["pass"])
        self.assertEqual(x["cited_by_world"], {"maker": 3, "scene": 7})
        self.assertEqual(x["maker_citations"], 3)
        self.assertTrue(x["exercised_on_a_maker_citation"])

    def test_a_plant_that_did_not_bite_means_the_instrument_is_blind_and_x_fails(self) -> None:
        x = H.x_mark(make_grade("off"), make_grade("on"), make_grade("plant", m4a=self._m4a(exist=1.0)))
        self.assertFalse(x["plant_caught"])
        self.assertFalse(x["pass"])

    def test_a_plant_that_changed_more_than_one_citation_or_the_population_is_refused(self) -> None:
        on = make_grade("on")
        for bad in (self._m4a(exist=0.5), self._m4a(exist=0.9, n=9)):
            x = H.x_mark(make_grade("off"), on, make_grade("plant", m4a=bad))
            self.assertFalse(x["pass"], bad)
            self.assertFalse(x["plant_is_one_spoiled_citation"], bad)

    def test_exist_under_one_on_the_real_arm_fails_even_with_the_plant_caught(self) -> None:
        on = make_grade("on", m4a=self._m4a(exist=0.9))
        x = H.x_mark(make_grade("off"), on, make_grade("plant", m4a=self._m4a(exist=0.8)))
        self.assertFalse(x["exist_holds"])
        self.assertFalse(x["pass"])

    def test_no_plant_given_x_is_not_graded_never_passed(self) -> None:
        x = H.x_mark(make_grade("off"), make_grade("on"), None)
        self.assertIsNone(x["pass"])
        self.assertTrue(x["exist_holds"])

    def test_no_maker_citation_is_said_so_the_by_any_hand_road_is_not_claimed_as_exercised(self) -> None:
        on = make_grade("on", m4a=self._m4a(by_world={"scene": 10}))
        x = H.x_mark(make_grade("off"), on, make_grade("plant", m4a=self._m4a(exist=0.9, by_world={"?": 1, "scene": 9})))
        self.assertTrue(x["pass"])
        self.assertFalse(x["exercised_on_a_maker_citation"])

    def test_the_x_plant_journal_changes_one_cited_moment_and_nothing_else(self) -> None:
        rows = [{"kind": "brain", "act": "learn", "seq": 1, "words": ["star"]},
                {"kind": "answer", "item": "M1:a", "form": "point", "answer": {"kind": "point"}},
                {"kind": "answer", "item": "M4:star", "form": "why",
                 "answer": {"kind": "because", "word": "star", "episodes": [{"moment": "m1"}, {"moment": "m2"}]}},
                {"kind": "answer", "item": "M4:bar", "form": "why",
                 "answer": {"kind": "because", "word": "bar", "episodes": [{"moment": "m3"}]}}]
        d = self.mk()
        src, dst = write_jsonl(d / "in.jsonl", rows), d / "out.jsonl"
        info = H.make_x_plant(src, dst)
        self.assertNotEqual(sha(src), sha(dst), "the plant must change the bytes")
        out = [json.loads(line) for line in dst.read_text().splitlines()]
        self.assertEqual(len(out), len(rows))
        changed = [(i, a, b) for i, (a, b) in enumerate(zip(rows, out)) if a != b]
        self.assertEqual(len(changed), 1)
        self.assertEqual(out[2]["answer"]["episodes"][0]["moment"], H.NOWHERE)
        self.assertEqual(out[2]["answer"]["episodes"][1], {"moment": "m2"})
        self.assertEqual((info["item"], info["word"], info["was"]), ("M4:star", "star", "m1"))

    def test_the_x_plant_refuses_a_journal_with_nothing_cited(self) -> None:
        d = self.mk()
        src = write_jsonl(d / "in.jsonl", [{"kind": "brain", "act": "learn", "seq": 1}])
        with self.assertRaises(H.ReaderError):
            H.make_x_plant(src, d / "out.jsonl")


# ------------------------------------------------------------------------------------------------ C: the mind's CPU per canvas, and the launch
class Cost(Tmp):
    def setUp(self) -> None:
        self.d = self.mk("hears-read-cost-")
        self.tape = write_tape(self.d / "tape")

    def test_the_cpu_of_a_canvas_is_the_sum_of_its_rows_and_the_scene_population_is_the_training_canvases(self) -> None:
        off_t, on_t = write_timings(self.d / "off.jsonl", OFF_CPU), write_timings(self.d / "on.jsonl", ON_CPU)
        c = H.cost(self.tape, off_t, on_t)
        sc, mk, al = c["populations"]["scene_train"], c["populations"]["maker"], c["populations"]["all_rows"]
        self.assertEqual((sc["canvases"], sc["off"]["n"], sc["on"]["n"], sc["off"]["missing"], sc["on"]["missing"]), (2, 2, 2, 0, 0))
        self.assertAlmostEqual(sc["off"]["mean_cpu_ms"], 4.0)
        self.assertAlmostEqual(sc["on"]["mean_cpu_ms"], 5.0)
        self.assertAlmostEqual(sc["ratio_mean"], 1.25)            # the sitting canvas (9 ms on both) is NOT in the population
        self.assertAlmostEqual(sc["ratio_median"], 1.25)
        self.assertTrue(sc["pass"])
        self.assertAlmostEqual(mk["ratio_mean"], 3.0)
        self.assertEqual(mk["canvases"], 2)
        self.assertFalse(mk["pass"])                               # the maker's canvases cost 3x with the brain listening: held to the same bar (A1.2)
        self.assertEqual(al["off"]["rows"], 10)
        self.assertAlmostEqual(al["ratio_mean"], 48 / 30)
        self.assertFalse(al["pass"])
        self.assertFalse(c["populations_pass"])                    # every population is held to the bar: one failing is a failing C
        self.assertEqual(c["bar"], 1.5)
        self.assertEqual(c["verdict"], "NOT READ")                 # no launch record: the arms' overlap is unknown, C cannot pass (A1.1)
        self.assertFalse(c["pass"])

    def test_the_median_and_the_mean_are_both_held_to_the_bar(self) -> None:
        # five maker canvases, one ear and one eye row each. A: the mean passes (1.167) and the median fails (2.0). B: the median passes (1.0) and the mean fails (2.8).
        rows = []
        for i in range(5):
            rows += [(2 * i + 1, "ear", "maker", f"m{i}", None), (2 * i + 2, "eye", "maker", f"m{i}", None)]
        tape = write_tape(self.d / "tape5", rows)
        for name, off_c, on_c, mean_ok, median_ok in (("A", [10, 10, 10, 10, 200], [20, 20, 20, 20, 200], True, False), ("B", [10] * 5, [10, 10, 10, 10, 100], False, True)):
            off = {s: off_c[(s - 1) // 2] / 2 for s in range(1, 11)}
            on = {s: on_c[(s - 1) // 2] / 2 for s in range(1, 11)}
            mk = H.cost(tape, write_timings(self.d / f"off{name}.jsonl", off, rows), write_timings(self.d / f"on{name}.jsonl", on, rows))["populations"]["maker"]
            self.assertEqual(mk["ratio_mean"] <= 1.5, mean_ok, name)
            self.assertEqual(mk["ratio_median"] <= 1.5, median_ok, name)
            self.assertFalse(mk["pass"], name)

    def test_planted_the_scene_canvases_doubled_fails_the_scene_population(self) -> None:
        bad = dict(ON_CPU)
        for s in (1, 2, 3, 4):
            bad[s] = ON_CPU[s] * 2.0
        off_t, on_t = write_timings(self.d / "off.jsonl", OFF_CPU), write_timings(self.d / "on.jsonl", bad)
        self.assertNotEqual(sha(self.d / "on.jsonl"), sha(write_timings(self.d / "on-same.jsonl", ON_CPU)), "the plant must change the bytes")
        sc = H.cost(self.tape, off_t, on_t)["populations"]["scene_train"]
        self.assertAlmostEqual(sc["ratio_mean"], 2.5)
        self.assertFalse(sc["pass"])

    def test_a_canvas_with_a_row_missing_from_the_timings_is_counted_and_the_mark_cannot_pass(self) -> None:
        off_t = write_timings(self.d / "off.jsonl", OFF_CPU)
        on_t = write_timings(self.d / "on.jsonl", CHEAP_MAKER, skip=(1,))                    # sA's ear row never timed on ON
        sc = H.cost(self.tape, off_t, on_t)["populations"]["scene_train"]
        self.assertEqual((sc["canvases"], sc["on"]["n"], sc["on"]["missing"], sc["off"]["n"]), (2, 1, 1, 2))
        self.assertFalse(sc["pass"], "an arm that timed fewer canvases than the tape holds cannot pass on the ones it kept")

    def test_a_scene_population_of_none_is_not_a_pass(self) -> None:
        d = self.mk("hears-read-cost-empty-")
        (d / "tape").mkdir()
        (d / "tape" / "x.jsonl").write_text(json.dumps({"seq": 1, "sense": "eye", "meta": {"source": "shelf", "moment": "h"}}) + "\n")
        t = d / "t.jsonl"
        t.write_text(json.dumps({"seq": 1, "sense": "eye", "source": "shelf", "ms": 1.0, "cpu_ms": 1.0}) + "\n")
        c = H.cost(d / "tape", t, t)
        self.assertEqual(c["populations"]["scene_train"]["canvases"], 0)
        self.assertFalse(c["populations"]["scene_train"]["pass"])

    def test_the_launch_record_overlap_decides_void_or_not_and_the_verdict_follows(self) -> None:
        off_t, on_t = write_timings(self.d / "off.jsonl", OFF_CPU), write_timings(self.d / "on.jsonl", CHEAP_MAKER)
        ok_off, ok_on = write_arm(self.d / "off.arm", 1000.0, 3000.0), write_arm(self.d / "on.arm", 1005.0, 3000.0)
        c = H.cost(self.tape, off_t, on_t, ok_off, ok_on)
        self.assertTrue(c["populations_pass"])
        self.assertAlmostEqual(c["launch"]["overlap"], 1995 / 2000)
        self.assertFalse(c["launch"]["void"])
        self.assertAlmostEqual(c["launch"]["start_skew_s"], 5.0)
        self.assertEqual((c["verdict"], c["pass"]), ("PASS", True))
        late_on = write_arm(self.d / "on-late.arm", 1500.0, 3600.0)                       # the ON arm started 500 s late: overlap 1500 / 2100 = 0.714
        v = H.cost(self.tape, off_t, on_t, ok_off, late_on)
        self.assertAlmostEqual(v["launch"]["overlap"], 1500 / 2100)
        self.assertTrue(v["launch"]["void"])
        self.assertEqual((v["verdict"], v["pass"]), ("VOID", False))
        self.assertTrue(v["populations_pass"], "the numbers may look fine: a void pair is never read")
        edge = H.cost(self.tape, off_t, on_t, ok_off, write_arm(self.d / "on-edge.arm", 1200.0, 3000.0))      # overlap exactly 1800 / 2000 = 0.90: not void
        self.assertFalse(edge["launch"]["void"])

    def test_a_failing_population_with_a_good_launch_is_fail_and_a_launch_record_without_an_end_is_refused(self) -> None:
        off_t, on_t = write_timings(self.d / "off.jsonl", OFF_CPU), write_timings(self.d / "on.jsonl", ON_CPU)
        a, b = write_arm(self.d / "off.arm", 1000.0, 3000.0), write_arm(self.d / "on.arm", 1000.0, 3000.0)
        self.assertEqual(H.cost(self.tape, off_t, on_t, a, b)["verdict"], "FAIL")
        broken = self.d / "broken.arm"
        broken.write_text("label x\nstart_epoch 1000.0\n")
        with self.assertRaises(H.ReaderError) as cm:
            H.cost(self.tape, off_t, on_t, a, broken)
        self.assertIn("end_epoch", str(cm.exception))


# ------------------------------------------------------------------------------------------------ I2: the token absent changes nothing
class I2(unittest.TestCase):
    def _rows(self):
        i1 = [{"seq": s, "word": "w", "hash": f"h{s}"} for s in range(1, 9)] + [_learn(9, "scene", ["star"])]
        off = []
        for r in i1:
            off.append(r)
            if r.get("kind") != "brain":
                off.append(_turn(r["seq"], "scene", ["star"], ["star"]))
        return off, i1

    def test_off_without_its_turn_rows_equals_the_replay_without_drive(self) -> None:
        off, i1 = self._rows()
        r = H.i2(off, i1)
        self.assertTrue(r["pass"])
        self.assertEqual((r["turn_rows_dropped"], r["rows_compared"], r["rows_i1"]), (8, 9, 9))
        self.assertIsNone(r["first_difference"])
        self.assertEqual(r["pass"], DG.mark_i2(off, i1)["pass"])        # the drive law's own comparison, same inputs

    def test_a_learn_row_that_differs_is_a_difference_the_default_journal_diff_would_not_see(self) -> None:
        off, i1 = self._rows()
        bad = copy.deepcopy(off)
        bad[-1]["words"] = ["moon"]                                      # a brain `learn` row: journal_diff.py drops every brain row, I2 must not
        r = H.i2(bad, i1)
        self.assertFalse(r["pass"])
        self.assertEqual(r["first_difference"]["seq"], 9)

    def test_planted_one_character_of_one_kept_row_fails_the_comparison(self) -> None:
        off, i1 = self._rows()
        planted = H.plant_one_character(off)
        self.assertNotEqual(json.dumps(planted, sort_keys=True), json.dumps(off, sort_keys=True), "the plant must change the bytes")
        self.assertFalse(H.i2(planted, i1)["pass"])

    def test_a_missing_row_fails_and_an_empty_pair_is_not_a_pass(self) -> None:
        off, i1 = self._rows()
        self.assertFalse(H.i2(off, i1[:-1])["pass"])
        self.assertFalse(H.i2([], [])["pass"])


# ------------------------------------------------------------------------------------------------ T: the shared words against the dealt-targets null
class Transfer(unittest.TestCase):
    def test_perfect_says_on_the_six_shared_words_show_transfer_at_k3_and_k1(self) -> None:
        t = H.t_reading(t_journal(lambda w, m: [w]))
        k3, k1 = t["shared"]["k3"], t["shared"]["k1"]
        self.assertEqual((k3["n"], k3["agreed"], k3["typed"], k3["silent"]), (18, 18, 18, 0))
        self.assertEqual((k1["n"], k1["agreed"], k1["typed"]), (6, 6, 6))
        self.assertEqual(k3["words"], sorted(SHARED6))
        # the architect's arithmetic: with perfect says the null's p95 is 6 of 18 (shown from 7) and 3 of 6 at k = 1 (shown from 4)
        self.assertEqual((k3["null_p95"], k3["pass_line"]), (6, 7))
        self.assertEqual((k1["null_p95"], k1["pass_line"]), (3, 4))
        self.assertTrue(k3["shown"])
        self.assertTrue(k1["shown"])
        self.assertEqual(k3["misses"], [])
        self.assertEqual((t["draws"], t["ks"]), (1000, [3, 1]))
        self.assertIn("STRUCK", t["maker_only_comparison"])

    def test_a_silent_brain_does_not_show_transfer_and_its_silence_is_counted(self) -> None:
        t = H.t_reading(t_journal(lambda w, m: None))
        k3 = t["shared"]["k3"]
        self.assertEqual((k3["n"], k3["agreed"], k3["silent"]), (18, 0, 18))
        self.assertEqual(k3["null_p95"], 0)
        self.assertFalse(k3["shown"])                                    # agreed over ALL turns: a silent brain cannot pass
        self.assertEqual(len(k3["misses"]), 18)
        self.assertIsNone(k3["misses"][0]["said"])

    def test_always_saying_the_commonest_word_matches_the_null_exactly_and_shows_nothing(self) -> None:
        t = H.t_reading(t_journal(lambda w, m: ["star"]))
        k3 = t["shared"]["k3"]
        self.assertEqual(k3["agreed"], 3)                                # «star» is right on its own three turns
        self.assertEqual((k3["null_p95"], k3["null_max"]), (3, 3))       # every dealt draw has three «star» targets: the null is a point
        self.assertFalse(k3["shown"])
        self.assertEqual({m["said"][0] for m in k3["misses"]}, {"star"})
        self.assertEqual(len(k3["misses"]), 15)

    def test_the_null_is_seeded_and_repeatable(self) -> None:
        a, b = H.t_reading(t_journal(lambda w, m: [w])), H.t_reading(t_journal(lambda w, m: [w]))
        self.assertEqual(a["shared"]["k3"]["null_p95"], b["shared"]["k3"]["null_p95"])
        self.assertEqual(a["shared"]["k3"]["null_mean"], b["shared"]["k3"]["null_mean"])
        c = H.t_reading(t_journal(lambda w, m: [w]), seed=7)
        self.assertEqual(c["seed"], 7)

    def test_a_word_not_typed_at_the_turn_is_counted_so_the_ceiling_is_visible(self) -> None:
        # the calibration comes after the first seven maker turns (the six shared words' first meetings and «bar»'s): those six shared turns were not typed
        t = H.t_reading(t_journal(lambda w, m: [w], cal_after=7))
        self.assertEqual(t["shared"]["k3"]["typed"], 18 - 6)
        self.assertEqual(t["shared"]["k1"]["typed"], 0)

    def test_the_maker_only_words_are_an_over_extension_table_not_a_comparison(self) -> None:
        table = {("bar", 1): None, ("bar", 2): ["circle"], ("bar", 3): ["red"], ("dot", 1): None, ("dot", 2): None, ("dot", 3): ["zzz"]}
        say_of = lambda w, m: [w] if w in SHARED6 else table[(w, m)]
        oe = H.t_reading(t_journal(say_of))["over_extension"]
        self.assertEqual(oe["n"], 6)
        self.assertEqual(oe["kinds"], {"silent": 3, "shape": 1, "colour_size": 1, "not_typed": 1})
        self.assertEqual((oe["typed"], oe["before_first_calibration"]), (0, 0))
        self.assertEqual([x["kind"] for x in oe["turns"] if x["word"] == "bar"], ["silent", "shape", "colour_size"])
        late = H.t_reading(t_journal(say_of, cal_after=7))["over_extension"]            # «bar»'s first meeting is before the first calibration, «dot»'s is after
        self.assertEqual(late["before_first_calibration"], 1)

    def test_a_journal_with_no_maker_turn_gives_empty_arms_never_a_rate(self) -> None:
        t = H.t_reading([r for r in t_journal(lambda w, m: [w]) if r.get("world") != "maker"])
        self.assertEqual(t["shared"]["k3"]["n"], 0)
        self.assertIsNone(t["shared"]["k3"]["shown"])
        self.assertIsNone(t["shared"]["k3"]["null_p95"])


# ------------------------------------------------------------------------------------------------ G: the last hundred maker turns
class Growth(unittest.TestCase):
    def test_the_last_hundred_agreed_over_all_with_its_ceiling_and_floor_known_by_construction(self) -> None:
        g = H.g_reading(maker_journal())
        self.assertEqual(g["maker_turns"], 120)
        lk = g["last_k"]
        self.assertEqual((lk["k"], lk["n"], lk["said"], lk["agreed"], lk["typed"]), (100, 100, 100, 90, 100))
        self.assertAlmostEqual(lk["agree_over_all"], 0.9)
        self.assertAlmostEqual(lk["ceiling"], 1.0)
        self.assertAlmostEqual(lk["floor_commonest_word"], 0.25)          # four words, 25 turns each in the last 100
        self.assertEqual(g["maker_said_all"], 120)
        self.assertAlmostEqual(g["maker_agree_rate_all"], 0.75)          # the whole life reads another number: the cut at the last 100 is real
        self.assertTrue(g["prediction_last100_true_above_0.8"])
        self.assertFalse(lk["fewer_than_k"])
        self.assertEqual({w: v["meetings"] for w, v in g["maker_words"].items()}, {w: 30 for w in WORDS4})

    def test_a_silent_brain_does_not_pass_and_a_rarely_speaking_true_one_does_not_either(self) -> None:
        silent = H.g_reading(maker_journal(mode="silent"))["last_k"]
        self.assertEqual((silent["agreed"], silent["said"]), (0, 0))
        self.assertAlmostEqual(silent["agree_over_all"], 0.0)
        self.assertIsNone(H.g_reading(maker_journal(mode="silent"))["maker_agree_rate_all"])
        g = H.g_reading(maker_journal(mode="rare"))
        lk = g["last_k"]
        self.assertEqual((lk["said"], lk["agreed"]), (10, 10))           # agreed / said would read 1.0 and pass; agreed / ALL reads 0.1
        self.assertAlmostEqual(lk["agree_over_all"], 0.1)
        self.assertFalse(g["prediction_last100_true_above_0.8"])

    def test_fewer_than_a_hundred_maker_turns_is_not_read_and_says_so(self) -> None:
        g = H.g_reading(maker_journal(n=50))
        self.assertEqual((g["last_k"]["n"], g["last_k"]["fewer_than_k"]), (50, True))
        self.assertIsNone(g["prediction_last100_true_above_0.8"])

    def test_every_typed_maker_word_said_truly_once_clause_one_replaced(self) -> None:
        g = H.g_reading(maker_journal())
        self.assertEqual({w: v["first_agreed_say_turn"] for w, v in g["typed_maker_words"].items()}, {"star": 24, "bar": 21, "dot": 22, "cup": 23})
        self.assertTrue(g["prediction_every_typed_maker_word_said_truly"])
        bad = H.g_reading(maker_journal(never_true=("cup",)))                 # «cup» is typed at the last calibration and never said truly
        self.assertIsNone(bad["typed_maker_words"]["cup"]["first_agreed_say_turn"])
        self.assertFalse(bad["prediction_every_typed_maker_word_said_truly"])
        part = H.g_reading(maker_journal(never_true=("cup",), last_types=[["star", "bar", "dot"], ["red"], ["big"]]))   # «cup» NOT typed at the last calibration: not in the clause
        self.assertEqual(sorted(part["typed_maker_words"]), ["bar", "dot", "star"])
        self.assertTrue(part["prediction_every_typed_maker_word_said_truly"])
        self.assertFalse(part["maker_words"]["cup"]["typed_at_last_calibration"])

    def test_the_ceiling_counts_turns_whose_word_was_typed_before_the_turn(self) -> None:
        early = [["star"], ["red"], ["big"]]                                  # only «star» is typed when the maker turns happen
        lk = H.g_reading(maker_journal(early_types=early))["last_k"]
        self.assertEqual(lk["typed"], 25)
        self.assertAlmostEqual(lk["ceiling"], 0.25)

    def test_growth_with_no_maker_turn_says_so_never_a_rate(self) -> None:
        g = H.g_reading([r for r in maker_journal() if r.get("world") != "maker"])
        self.assertEqual(g["maker_turns"], 0)
        self.assertIsNone(g["last_k"]["agree_over_all"])
        self.assertIsNone(g["prediction_last100_true_above_0.8"])
        self.assertIsNone(g["prediction_every_typed_maker_word_said_truly"])


# ------------------------------------------------------------------------------------------------ the whole reader, end to end
class EndToEnd(Tmp):
    def _bench(self, on_cpu=ON_CPU, plant_exist=0.9, arm_on=(1005.0, 3000.0)):
        d = self.mk("hears-read-e2e-")
        i1 = [{"seq": s, "word": "w", "hash": f"h{s}"} for s in range(1, 5)]
        off_j = []
        for r in i1:
            off_j += [r, _turn(r["seq"], "scene", ["star"], ["star"])]
        a = {
            "off": write_grade(d / "off", make_grade("off")),
            "on": write_grade(d / "on", make_grade("on")),
            "plant": write_grade(d / "plant", make_grade("plant", m4a={"exist": plant_exist, "n_cited": 10, "n_with_truth": 7,
                                                                          "cited_by_world": {"?": 1, "maker": 3, "scene": 6}, "carry": 0.9,
                                                                          "null_p95": 0.58, "verdict": "PASS"})),
            "tape": write_tape(d / "tape"),
            "off_t": write_timings(d / "off-t.jsonl", OFF_CPU),
            "on_t": write_timings(d / "on-t.jsonl", on_cpu),
            "off_arm": write_arm(d / "off.arm", 1000.0, 3000.0),
            "on_arm": write_arm(d / "on.arm", *arm_on),
            "on_j": write_jsonl(d / "on-j.jsonl", maker_journal()),
            "off_j": write_jsonl(d / "off-j.jsonl", off_j),
            "i1_j": write_jsonl(d / "i1-j.jsonl", i1),
        }
        argv = ["--off", str(a["off"].parent), "--on", str(a["on"].parent), "--on-plant", str(a["plant"].parent), "--tape", str(a["tape"]),
                "--off-timings", str(a["off_t"]), "--on-timings", str(a["on_t"]), "--off-arm", str(a["off_arm"]), "--on-arm", str(a["on_arm"]),
                "--on-journal", str(a["on_j"]), "--off-journal", str(a["off_j"]), "--i1-journal", str(a["i1_j"]), "--out", str(d / "out")]
        return d, argv

    def test_every_input_reads_and_the_files_are_written(self) -> None:
        # the maker canvases cost 3x in the fixture, so C fails: the exit code must say so, and nothing else may fail
        d, argv = self._bench()
        rc = H.main(argv)
        o = json.loads((d / "out" / "hears.json").read_text())
        self.assertEqual(rc, 1)
        self.assertEqual(o["bars"], {"C": "FAIL", "X": "PASS", "I2": "PASS", "controls": "CAUGHT"})
        self.assertEqual(o["pairs"]["fresh"]["M1"]["n_pair"], 14)
        self.assertEqual(o["controls"]["P"]["caught"], True)
        self.assertEqual(o["controls"]["I2"]["caught"], True)
        self.assertEqual(o["splits"]["M1"]["unlocated_items"], 24)           # the cost fixture's tape holds no asks: counted, not hidden
        self.assertEqual(o["G"]["last_k"]["n"], 100)
        self.assertEqual(o["T"]["shared"]["k3"]["n"], 3)                     # «star» is the one shared word of the fixture journal
        self.assertIn("off", o["inputs"])
        self.assertEqual(len(o["inputs"]["off"]["sha256"]), 64)
        txt = (d / "out" / "hears.txt").read_text()
        for needle in ("P ·", "T ·", "G ·", "C ·", "X ·", "I2 ·", "smallest passing gap", "cited by world", "overlap", "BARS:"):
            self.assertIn(needle, txt)

    def test_when_every_barred_mark_passes_the_exit_is_zero(self) -> None:
        d, argv = self._bench(on_cpu=CHEAP_MAKER)
        self.assertEqual(H.main(argv), 0)
        self.assertEqual(json.loads((d / "out" / "hears.json").read_text())["bars"]["C"], "PASS")

    def test_arms_that_barely_overlap_void_c_and_fail_the_exit_however_good_the_numbers(self) -> None:
        d, argv = self._bench(on_cpu=CHEAP_MAKER, arm_on=(1500.0, 3600.0))
        self.assertEqual(H.main(argv), 1)
        self.assertEqual(json.loads((d / "out" / "hears.json").read_text())["bars"]["C"], "VOID")

    def test_a_plant_that_did_not_bite_fails_the_exit(self) -> None:
        d, argv = self._bench(on_cpu=CHEAP_MAKER, plant_exist=1.0)
        self.assertEqual(H.main(argv), 1)
        self.assertEqual(json.loads((d / "out" / "hears.json").read_text())["bars"]["X"], "FAIL")

    def test_an_input_that_lacks_a_key_is_an_error_that_names_the_key(self) -> None:
        d, argv = self._bench()
        broken = json.loads((d / "on" / "grade.json").read_text())
        del broken["sets"]["fresh"]["marks"]["M3"]
        (d / "on" / "grade.json").write_text(json.dumps(broken))
        with self.assertRaises(H.ReaderError) as cm:
            H.main(argv)
        self.assertIn("M3", str(cm.exception))

    def test_a_half_given_launch_record_or_cost_input_is_refused(self) -> None:
        d, argv = self._bench()
        i = argv.index("--on-arm")
        with self.assertRaises(H.ReaderError):
            H.main(argv[:i] + argv[i + 2:])
        j = argv.index("--off-timings")
        with self.assertRaises(H.ReaderError):
            H.main(argv[:j] + argv[j + 2:])

    def test_the_tape_alone_gives_the_splits_and_leaves_c_not_read(self) -> None:
        # found by running the reader on real inputs: --tape serves the splits AND the cost; only the timings make it a cost reading
        d = self.mk("hears-read-tapeonly-")
        off, on = write_grade(d / "off", make_grade("off")), write_grade(d / "on", make_grade("on"))
        self.assertEqual(H.main(["--off", str(off.parent), "--on", str(on.parent), "--tape", str(write_tape(d / "tape")), "--out", str(d / "out")]), 0)
        o = json.loads((d / "out" / "hears.json").read_text())
        self.assertIn("splits", o)
        self.assertEqual(o["bars"]["C"], "NOT READ")
        t = write_timings(d / "t.jsonl", OFF_CPU)
        with self.assertRaises(H.ReaderError):                               # timings without the tape they are read against
            H.main(["--off", str(off.parent), "--on", str(on.parent), "--off-timings", str(t), "--on-timings", str(t), "--out", str(d / "out2")])

    def test_only_the_inputs_given_are_read_and_the_rest_say_not_read(self) -> None:
        d = self.mk("hears-read-min-")
        off, on = write_grade(d / "off", make_grade("off")), write_grade(d / "on", make_grade("on"))
        self.assertEqual(H.main(["--off", str(off.parent), "--on", str(on.parent), "--out", str(d / "out")]), 0)
        o = json.loads((d / "out" / "hears.json").read_text())
        self.assertEqual(o["bars"]["C"], "NOT READ")
        self.assertEqual(o["bars"]["X"], "NOT READ")
        self.assertEqual(o["bars"]["I2"], "NOT READ")
        self.assertEqual(o["controls"]["P"]["caught"], True)

    def test_the_plant_x_mode_writes_the_planted_journal_and_prints_what_it_changed(self) -> None:
        d = self.mk("hears-read-xmode-")
        rows = [{"kind": "answer", "item": "M4:star", "form": "why", "answer": {"kind": "because", "word": "star", "episodes": [{"moment": "m1"}]}}]
        src = write_jsonl(d / "in.jsonl", rows)
        self.assertEqual(H.main(["--plant-x-journal", str(src), "--plant-x-out", str(d / "out.jsonl")]), 0)
        self.assertNotEqual(sha(src), sha(d / "out.jsonl"))


# ------------------------------------------------------------------------------------------------ the real producer: the closed life's own grade
@unittest.skipUnless(REAL_GRADE.exists(), "the closed life's grade is not on this box")
class OnTheRealGrade(unittest.TestCase):
    """OFF = ON = the real grade of brain-full-20261102: every pair identical, and the paired n's are the numbers the grader's own report prints
    (M1 covered n 188 / 201, M3 58 / 57, M6 pooled 56) — the population is the grader's, read from the file the grader wrote."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.g = json.loads(REAL_GRADE.read_text())

    def test_the_paired_populations_are_the_graders_own_n(self) -> None:
        p = H.pairs(self.g, copy.deepcopy(self.g))
        self.assertEqual(p["fresh"]["M1"]["n_pair"], self.g["sets"]["fresh"]["marks"]["M1"]["graded"]["n_covered"])
        self.assertEqual(p["s1b1"]["M1"]["n_pair"], self.g["sets"]["s1b1"]["marks"]["M1"]["graded"]["n_covered"])
        self.assertEqual((p["fresh"]["M1"]["n_pair"], p["s1b1"]["M1"]["n_pair"]), (188, 201))
        self.assertEqual((p["fresh"]["M3"]["n_pair"], p["s1b1"]["M3"]["n_pair"]), (58, 57))
        self.assertEqual(p["pooled"]["M6"]["n_pair"], self.g["M6_pooled"]["n_covered"])
        self.assertEqual(p["pooled"]["M6"]["n_pair"], 56)
        for tset in ("fresh", "s1b1", "pooled"):
            for mark in ("M1", "M3", "M6"):
                self.assertEqual((p[tset][mark]["discordant_on_right"], p[tset][mark]["discordant_off_right"]), (0, 0), (tset, mark))
        self.assertAlmostEqual(p["fresh"]["M1"]["smallest_passing_gap"], 10 / 188)

    def test_the_verdicts_and_the_aggregates_read_from_the_real_keys(self) -> None:
        v = H.verdicts(self.g, copy.deepcopy(self.g))
        self.assertEqual(sorted(v), ["1", "2a", "2b", "3", "4a", "5", "6"])
        self.assertTrue(all(not x["changed"] for x in v.values()))
        a = H.aggregates(self.g, copy.deepcopy(self.g))
        self.assertEqual(a["fresh"]["M2a_refusal"]["n_off"], 400)
        self.assertEqual(a["fresh"]["M1_covered"]["n_off"], 188)

    def test_the_old_graders_grade_has_no_citations_by_world_and_the_reader_says_so_never_a_zero(self) -> None:
        # the grade of 09-28 predates the HEARS-2 grader: it has no `cited_by_world` / `n_with_truth`. A missing field is «not recorded», never {} or 0 (#168)
        x = H.x_mark(self.g, copy.deepcopy(self.g), None)
        self.assertEqual(x["n_cited"], 104)
        self.assertEqual(x["exist"], 1.0)
        self.assertIsNone(x["cited_by_world"])
        self.assertIsNone(x["maker_citations"])
        self.assertIsNone(x["exercised_on_a_maker_citation"])


if __name__ == "__main__":
    unittest.main()
