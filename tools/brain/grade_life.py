#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-28 20:30 +0400 — BRAIN-IN-BODY: the grader of a life (PREREG-BRAIN-IN-BODY §3, INTERFACE §6).
# edit: Claude (Fable 5.1, the seat), 2026-09-28 20:40 +0400 — brought under the SIGNED PREREG (12bdea6, §3 and §8's three differences): M4's
# null keeps the cited episodes and draws among THEIR hyps; a citation maps to a thing by M1's rule over fix / hyps; the sign
# test is ONE-sided; every pointing is read FORCED (a `point: None` → a uniform draw over the row's hyps by the item's tie
# generator; a «misuse» answer on a pointing mark → its `raw_forced`); the twin must be ABLE (its forced M1 above the null's
# p95) or the pair reads VOID; the twin's M3 pair pools both sets; the life's M1 and M3 are read against the null's p95.
"""tools/brain/grade_life.py — the six marks of ONE life, read from its own tape, its journal and its truth files.

    PYTHONPATH=<repo> /usr/bin/python3 -B tools/brain/grade_life.py --root <life root> [--journal <journal.jsonl | dir>]
        [--scored /data/dev/brain-runs/scene-s1b1r] [--out <dir>] [--label brain|twin|null]

What it reads
  the TAPE      every row (creature.tape.read_tape, every day file): the `ask` rows' payloads, the scene `eye` rows
  the JOURNAL   the mind's rows `kind: "answer"` (one per ask; `raw` = the offline graders' own fields, `fix`, `hyps`) and
                `kind: "brain"` (its learning acts)
  the TRUTH     root/truth/scene/<eye seq>.json — read HERE and nowhere in the mind or the brain

What it does NOT do: it never imports creature.mind or genome.brain, never reads the offline glance caches, and never
recomputes an answer. The grading functions are the scored run's own (brain/scene/marks.py, brain/scene/run.py:
grade_answers_r, bars_r); the oracle arms' readings beside each bar and the null's 20 draws are the scored record's at the
same world seed (PREREG §3: «the oracle readings beside each bar are S1b-1R's record at the same seed»).
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import math
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from brain.scene import marks as M
from brain.scene import run as R
from brain.scene import world as W
from creature.tape import _resolve_tape_dir, read_tape
from genome.machinery import parse_genome

LAW = "LAW"
POINT_MARKS = ("M1", "M2a", "M3", "M6", "M5")
ROAD_MARKS = ("M2b", "NAME", "SPEAK", "SPEAK2", "DECLINE")
GRADED_SET = "fresh"                 # PREREG §1: every mark is graded on the FRESH set alone …
M6_POOLED_SETS = ("fresh", "s1b1")   # … except test 6, pooled over both sets
CELL_PX = 8
M4_MAX_CITED = 8
M4_TWIN_DRAWS = 20


class GradeError(Exception):
    pass


# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:04 +0400 — the seam test (brain-organ a417b69): the journal keeps `Brain.ask`'s return WHOLE
# under `answer`, so `raw` / `raw_forced` sit inside it; `begin` / `end` rows carry no item; NAME's forced names are keyed by
# the brain's LEARNED type (its words joined with «|») and are mapped to the world's type names HERE, on the truth side.
def raw_of(a: Optional[Dict[str, object]]) -> Dict[str, object]:
    if not a:
        return {}
    ans = a.get("answer") or {}
    r = ans.get("raw") if isinstance(ans, dict) else None
    return dict(r) if isinstance(r, dict) else dict(a.get("raw") or {})


def forced_of(a: Optional[Dict[str, object]]) -> Dict[str, object]:
    if not a:
        return {}
    ans = a.get("answer") or {}
    r = ans.get("raw_forced") if isinstance(ans, dict) else None
    return dict(r) if isinstance(r, dict) else dict(a.get("raw_forced") or {})


def world_type_of_key(key: str) -> str:
    """A learned type's key («circle|cross|…») → the world's name for it: the type most of its words have. A key that is
    already a world type name passes through."""
    if key in W.WORD_TYPES:
        return key
    kinds = collections.Counter(W.word_type(w) for w in key.split("|"))
    return kinds.most_common(1)[0][0]


def name_by_world_type(raw: Dict[str, object]) -> Dict[str, object]:
    nm = raw.get("name")
    if not isinstance(nm, dict):
        return raw
    out = dict(raw)
    mapped: Dict[str, object] = {}
    for k, v in nm.items():
        t = world_type_of_key(str(k))
        if t in mapped:
            raise GradeError(f"two learned types map to the world's {t!r}: {sorted(nm)}")
        mapped[t] = v
    out["name"] = mapped
    return out


# ------------------------------------------------------------------------------------------------ reading a life
def _jsonl(path: Path) -> List[Dict[str, object]]:
    out = []
    with Path(path).open(encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError as e:
                    raise GradeError(f"{path}:{n}: a line that does not parse ({e})") from e
    return out


def read_journal(journal: Path) -> List[Dict[str, object]]:
    """A journal is a directory of day files (a live life) or ONE journal.jsonl (a replay's out dir)."""
    journal = Path(journal)
    if journal.is_dir():
        rows: List[Dict[str, object]] = []
        for f in sorted(journal.glob("*.jsonl")):
            rows.extend(_jsonl(f))
        return rows
    return _jsonl(journal)


class Life:
    """One life as the grader reads it. Nothing here is computed by the mind's code."""

    def __init__(self, root: Path, journal: Optional[Path] = None, genome_path: Optional[Path] = None):
        self.root = Path(root)
        gp = Path(genome_path) if genome_path else self.root / "GENOME.genome"
        self.genome = parse_genome(gp.read_text())
        self.cfg = self.genome.declared.get("WORLD_SCENE")
        if self.cfg is None:
            raise GradeError(f"{gp}: no WORLD scene line — not a scene-world life")
        self.ws = int(self.cfg["seed"])
        tape_decl = self.genome.declared.get("TAPE", {}).get("path")
        self.tape_dir = _resolve_tape_dir(self.root, tape_decl)
        self.rows = list(read_tape(self.root, tape_decl))
        self.by_seq = {int(r["seq"]): r for r in self.rows}
        self.truth_dir = self.root / "truth" / "scene"
        self.journal = read_journal(journal if journal is not None else self.root / "journal")
        self.answers = [j for j in self.journal if j.get("kind") == "answer"]
        self.brain_rows = [j for j in self.journal if j.get("kind") == "brain"]
        # the tape, indexed
        self.asks: Dict[str, Dict[str, object]] = {}          # item → the ask's payload (+ its tape row)
        self.why_repeats_asked = 0
        self.why_repeats_answered = 0
        self.moment_eye: Dict[str, Dict[str, object]] = {}    # moment → the eye row
        self.moment_words: Dict[str, List[str]] = collections.defaultdict(list)
        self.train_moment: Dict[int, str] = {}                # scene index → moment
        for r in self.rows:
            meta = r.get("meta") or {}
            if meta.get("source") != "scene":
                continue
            if r["sense"] == "ask":
                p = json.loads((self.tape_dir / r["payload"]).read_text(encoding="utf-8"))
                if p.get("item") is not None:
                    # edit: Claude (Fable 5.1, the seat), 2026-09-28 21:23 +0400 — a `why` is asked in EVERY sitting under one item name
                    # («M4:<word>»); PREREG §3 grades the FRESH sitting's, which comes first on the tape: the first ask stands
                    if str(p["item"]) in self.asks and p.get("form") == "why":
                        self.why_repeats_asked += 1
                        continue
                    self.asks[str(p["item"])] = {**p, "_moment": meta.get("moment"), "_seq": int(r["seq"])}
            elif r["sense"] == "ear":
                self.moment_words[str(meta.get("moment"))].append(str(meta.get("word")))
            elif r["sense"] == "eye":
                self.moment_eye[str(meta.get("moment"))] = r
                if meta.get("kind") == "train":
                    self.train_moment[int(meta["scene"])] = str(meta.get("moment"))
        self.answer_of: Dict[str, Dict[str, object]] = {}
        dup = []
        for j in self.answers:
            if j.get("item") is None:          # `begin` / `end`: acknowledgements, no item
                continue
            k = str(j.get("item"))
            if k in self.answer_of:
                if j.get("form") == "why":               # a later sitting's repeat of a `why`: counted, never graded
                    self.why_repeats_answered += 1
                    continue
                dup.append(k)
            self.answer_of[k] = j
        if dup:
            raise GradeError(f"{len(dup)} items were answered more than once, e.g. {dup[:3]} — a journal that holds two lives?")

    def truth_of_eye(self, eye_row: Dict[str, object]) -> Dict[str, object]:
        p = self.truth_dir / f"{int(eye_row['seq']):09d}.json"
        if not p.exists():
            raise GradeError(f"no truth file for eye row seq {eye_row['seq']} ({p})")
        return json.loads(p.read_text(encoding="utf-8"))

    def counts(self) -> Dict[str, object]:
        c = collections.Counter(r["sense"] for r in self.rows if (r.get("meta") or {}).get("source") == "scene")
        by = collections.Counter(str(j.get("by")) for j in self.answers)
        forms = collections.Counter(str(j.get("form")) for j in self.answers)
        return {"tape_rows": len(self.rows), "scene_rows_by_sense": dict(c), "train_scenes": len(self.train_moment),
                "asks_on_tape": len(self.asks), "answers_in_journal": len(self.answers), "answers_by": dict(by),
                "answers_by_form": dict(forms), "brain_rows": len(self.brain_rows),
                "why_repeats_asked_in_later_sittings": self.why_repeats_asked,
                "why_repeats_answered": self.why_repeats_answered,
                "asks_without_answer": sorted(k for k in self.asks if k not in self.answer_of and
                                              self.asks[k].get("form") not in ("begin", "end"))[:10],
                "n_asks_without_answer": sum(1 for k in self.asks if k not in self.answer_of and
                                             self.asks[k].get("form") not in ("begin", "end"))}


# ------------------------------------------------------------------------------------------------ the offline graders' inputs
def things_of_dict(scene_dict: Dict[str, object]) -> List[W.Thing]:
    return [W.Thing(t["shape"], t["colour"], t["size"], int(t["top"]), int(t["left"])) for t in scene_dict["things"]]


def fix_things(fix: Sequence[Sequence[int]], things: Sequence[W.Thing]) -> List[Optional[int]]:
    return [W.fixation_thing((int(c[0]), int(c[1])), things) for c in fix]


def hyp_positions(fix: Sequence[Sequence[int]], hyps: Sequence[Sequence[int]]) -> List[Tuple[float, float]]:
    return [(float(np.mean([fix[m][0] for m in mem])), float(np.mean([fix[m][1] for m in mem]))) for mem in hyps]


class SplitThings:
    """What `grade_pointing` asks of a split: members(row) → (the hypotheses' member lists, their mean positions)."""

    def __init__(self) -> None:
        self.rows: Dict[int, Tuple[List[List[int]], List[Tuple[float, float]]]] = {}

    def members(self, row: int):
        if row not in self.rows:
            raise GradeError(f"row {row} has no answer row carrying fix / hyps")
        return self.rows[row]


class SetCtx:
    """One test set of one life, shaped like brain.scene.run._RCtx (the grader's context), built from the life alone."""

    def __init__(self, life: Life, tset: str):
        self.life, self.tset = life, tset
        self.items: Dict[str, List[Dict[str, object]]] = collections.defaultdict(list)
        self.truth: Dict[str, Dict[int, Dict[str, object]]] = collections.defaultdict(dict)
        self.things: Dict[str, SplitThings] = collections.defaultdict(SplitThings)
        seen_items = set()
        disagree: List[str] = []
        for moment, eye in life.moment_eye.items():
            meta = eye.get("meta") or {}
            if meta.get("kind") != "sitting" or meta.get("set") != tset:
                continue
            t = life.truth_of_eye(eye)
            split, row = str(t["split"]), int(t["row"])
            sd = t["scene_dict"]
            things = things_of_dict(sd)
            fix = hyps = None
            for it in t.get("items", []):
                a = life.answer_of.get(str(it["item_id"]))
                if a is None:
                    continue
                f, h = a.get("fix"), a.get("hyps")
                if fix is None:
                    fix, hyps = f, h
                elif f != fix or h != hyps:
                    disagree.append(str(it["item_id"]))
            for it in t.get("items", []):
                if it["item_id"] in seen_items:
                    raise GradeError(f"item {it['item_id']} is keyed by two canvases")
                seen_items.add(it["item_id"])
                self.items[str(it["mark"])].append(dict(it))
            if fix is None:
                fix, hyps = [], []
            self.truth[split][row] = {"row": row, "item_id": sd.get("item_id"), "things": sd["things"],
                                      "referent": sd.get("referent"), "fix": [list(map(int, c)) for c in fix],
                                      "fix_thing": fix_things(fix, things), "centroids": sd["centroids"],
                                      "words": sd.get("words", [])}
            self.things[split].rows[row] = ([list(map(int, m)) for m in hyps], hyp_positions(fix, hyps))
        if disagree:
            raise GradeError(f"{len(disagree)} answers on one canvas disagree on fix / hyps, e.g. {disagree[:3]}")
        for m in self.items:
            self.items[m].sort(key=lambda it: str(it["item_id"]))
        # the pointer each pointed ask SHOULD have resolved to — the grader's own reading, with the truth
        self.ptr: Dict[str, Optional[int]] = {}
        for mark in ("M2b", "NAME", "SPEAK", "SPEAK2", "DECLINE"):
            for it in self.items.get(mark, []):
                split = self.split_of(mark)
                tr = self.truth[split][int(it["row"])]
                mem, pos = self.things[split].members(int(it["row"]))
                k = int(it["target"])
                self.ptr[str(it["item_id"])] = M.thing_hypothesis(k, mem, pos, tr["fix_thing"], tuple(tr["centroids"][k]))
        self.m2b_cov = {int(it["row"]) for it in self.items.get("M2b", [])
                        if M.covered(0, self.truth["m2b"][int(it["row"])]["fix_thing"])}

    @staticmethod
    def split_of(mark: str) -> str:
        return {"M1": "test", "M2a": "test", "NAME": "test", "M5": "test", "M2b": "m2b", "M6": "m6", "M3": "m3",
                "SPEAK": "speak", "SPEAK2": "speak2", "DECLINE": "decline"}[mark]

    def truth_list(self, split: str) -> "_Rows":
        return _Rows(self.truth[split])


class _Rows:
    """truth[row] by row index, as the offline graders index a list."""

    def __init__(self, d: Dict[int, Dict[str, object]]):
        self.d = d

    def __getitem__(self, row: int) -> Dict[str, object]:
        return self.d[int(row)]

    def __len__(self) -> int:
        return (max(self.d) + 1) if self.d else 0


def offline_answers(life: Life, ctx: SetCtx) -> Dict[str, object]:
    """The life's answers in the scored file's own shape: {"point": {item: raw}, "roads": {"LAW": {item: raw}}}.
    PREREG §3 «read FORCED»: on M1 / M2a / M3 / M6 a «misuse» answer is read by its `raw_forced` (what the pointing would
    have been — the false misuse itself is counted by M5's control), and a `point: None` that is not «unheard» is read as a
    uniform draw over the row's hypotheses by the item's own tie generator (marks.tie_rng). Both are counted."""
    point: Dict[str, Dict[str, object]] = {}
    road: Dict[str, Dict[str, object]] = {}
    forced = collections.Counter()
    for mark, items in ctx.items.items():
        for it in items:
            a = life.answer_of.get(str(it["item_id"]))
            if a is None:
                continue
            raw = raw_of(a)
            if not raw:
                raise GradeError(f"answer {it['item_id']} carries no `raw` (INTERFACE addendum 1)")
            if mark == "NAME":
                raw = name_by_world_type(raw)
            if mark in ("M1", "M2a", "M3", "M6"):
                if raw.get("misuse") is not None:
                    forced[f"{mark}:misuse→raw_forced"] += 1
                    raw = forced_of(a) or {"point": None}
                if raw.get("point") is None and not raw.get("unheard"):
                    hyps = a.get("hyps") or []
                    ts = (life.asks.get(str(it["item_id"])) or {}).get("test_seed")
                    if hyps and ts is not None:
                        raw = dict(raw)
                        raw["point"] = int(M.tie_rng(int(ts), str(it["item_id"])).integers(len(hyps)))
                        raw["forced_by_grader"] = True
                        raw.setdefault("none", True)
                        raw.setdefault("none_i", True)
                        forced[f"{mark}:None→uniform"] += 1
            (point if mark in POINT_MARKS else road)[str(it["item_id"])] = raw
    return {"point": point, "roads": {LAW: road}, "m2a_keys": {LAW: "none_i"}, "mouths": {LAW: "believed"},
            "forced": dict(forced)}


class _Ctx:
    """The duck of run._RCtx that grade_answers_r reads."""

    def __init__(self, sc: SetCtx, meeting_seen: Optional[bool]):
        self.items = {m: sc.items.get(m, []) for m in ("M1", "M2a", "M2b", "M6", "NAME", "M3", "SPEAK", "SPEAK2", "DECLINE")}
        self.truth = {s: sc.truth_list(s) for s in ("test", "m2b", "m6", "m3", "speak", "speak2", "decline")}
        self.things = {s: sc.things[s] for s in ("test", "m2b", "m6", "m3", "speak", "speak2", "decline")}
        self.m2b_cov = sc.m2b_cov
        self.meeting_seen = meeting_seen
        self.ptr = {"gaze": dict(sc.ptr), "truth": {}}


# ------------------------------------------------------------------------------------------------ the dax meeting
def meeting_seen(life: Life) -> Dict[str, object]:
    """Was the ONE «dax» meeting SEEN (≥ 1 fixation on the moon)? Read from the training tape, before any ask. The
    fixations are the ones the mind's own eye made on that canvas (the brain's learn row carries them when it journals
    `fix`; otherwise the grader looks once with the genome's own eye — the same function, the same canvas)."""
    m = life.train_moment.get(W.DAX_INDEX)
    if m is None:
        return {"seen": None, "why": f"the life has no training scene {W.DAX_INDEX} (train {life.cfg['train']})"}
    eye = life.moment_eye[m]
    t = life.truth_of_eye(eye)
    things = things_of_dict(t["scene_dict"])
    moon = [k for k, th in enumerate(things) if th.shape == W.DAX_SHAPE]
    fix = None
    for j in life.brain_rows:
        if j.get("moment") == m and j.get("fix") is not None:
            fix = j["fix"]
    how = "the brain's learn row"
    if fix is None:
        from PIL import Image
        from genome import gaze as G
        rgb = np.asarray(Image.open(life.tape_dir / eye["payload"]).convert("RGB"), dtype=np.uint8)
        g = G.glances(rgb, life.genome.retina, life.genome.gaze, "surprise", eye["sha"], colour=life.genome.colour,
                      predicted=None)
        fix = [[int(y), int(x)] for y, x in g["fix"]]
        how = "the grader's own look (genome.gaze.glances, the life's genome, predicted=None)"
    ft = fix_things(fix, things)
    return {"seen": bool(moon) and any(k in moon for k in ft if k is not None), "moment": m, "said": t.get("said"),
            "moon": moon, "fix": fix, "fix_thing": ft, "read_by": how,
            "things": [(th.shape, th.colour, th.size) for th in things]}


# ------------------------------------------------------------------------------------------------ M6 pooled, M5, M4
def pointing_rows(sc: SetCtx, A: Dict[str, object], mark: str) -> List[Dict[str, object]]:
    split = SetCtx.split_of(mark)
    return M.grade_pointing(sc.items.get(mark, []), A["point"], sc.truth_list(split), sc.things[split].members, "gaze")


def grade_m6_pooled(per_set_rows: Dict[str, List[Dict[str, object]]], seen: Optional[bool]) -> Dict[str, object]:
    rows = [r for s in M6_POOLED_SETS for r in per_set_rows.get(s, [])]
    grad = [r for r in rows if r["gradable"]]
    cov = [r for r in grad if r["covered"]]
    out = {"sets": {s: len(per_set_rows.get(s, [])) for s in M6_POOLED_SETS}, "n_items": len(rows), "n_covered": len(cov),
           "n_unheard": len(rows) - len(grad),
           "covered": (float(np.mean([r["correct"] for r in cov])) if cov else None),
           "all": (float(np.mean([r["correct"] for r in grad])) if grad else None),
           "chance_covered": (float(np.mean([r["chance"] for r in cov])) if cov else None),
           "bar": M.BARS["M6"], "n_bar": M.UNDERPOWERED_N, "meeting_seen": seen}
    if seen is None:
        out["verdict"] = "NOT GRADABLE — this life holds no «dax» meeting (its training stream ends before it)"
    elif seen is not True:
        out["verdict"] = "NOT GRADABLE — the one meeting was not seen by the gaze (an organ limit)"
    elif not cov or out["n_unheard"] == len(rows):
        out["verdict"] = "NOT GRADABLE — no covered gradable item"
    elif len(cov) < M.UNDERPOWERED_N:
        out["verdict"] = f"UNDERPOWERED (n {len(cov)} < {M.UNDERPOWERED_N})"
    else:
        out["verdict"] = "PASS" if out["covered"] >= M.BARS["M6"] else "FAIL"
    return out


def grade_m5(life: Life, sc: SetCtx, A: Dict[str, object]) -> Dict[str, object]:
    """PREREG §3 test 5. Misuse items: refused = the answer is `misuse` or «none» (the law's none_i); named = `misuse`.
    Valid phrases (every M1 and M3 item): called misuse. The never-heard pairs of M3: called misuse (must be 0)."""
    items = sc.items.get("M5", [])
    rows = []
    for it in items:
        a = life.answer_of.get(str(it["item_id"]))
        if a is None:
            continue
        raw = raw_of(a)
        named = raw.get("misuse") is not None
        none = bool(raw.get("none_i")) if raw.get("point") is not None else bool(raw.get("none"))
        unheard = bool(raw.get("unheard"))
        forced = forced_of(a)
        rows.append({"item_id": it["item_id"], "kind_of_pair": it.get("kind_of_pair"), "phrase": it.get("phrase"),
                     "named": named, "none": none, "unheard": unheard, "refused": named or none,
                     "forced_point": forced.get("point"), "n_things": it.get("n_things")})
    grad = [r for r in rows if not r["unheard"]]

    def rate(sel, key):
        return (float(np.mean([r[key] for r in sel])) if sel else None, len(sel))

    valid = []
    for mark in ("M1", "M3"):
        for it in sc.items.get(mark, []):
            a = life.answer_of.get(str(it["item_id"]))
            if a is not None:
                valid.append({"item_id": it["item_id"], "mark": mark, "misuse": raw_of(a).get("misuse") is not None})
    m3v = [v for v in valid if v["mark"] == "M3"]
    out = {"n_items": len(items), "n_answered": len(rows), "n_unheard": len(rows) - len(grad),
           "refused": rate(grad, "refused")[0], "named": rate(grad, "named")[0], "n": len(grad),
           "by_kind": {k: {"refused": rate([r for r in grad if r["kind_of_pair"] == k], "refused")[0],
                           "named": rate([r for r in grad if r["kind_of_pair"] == k], "named")[0],
                           "n": len([r for r in grad if r["kind_of_pair"] == k])}
                       for k in sorted({str(r["kind_of_pair"]) for r in grad})},
           "valid_called_misuse": rate(valid, "misuse")[0], "n_valid": len(valid),
           "m3_pairs_called_misuse": int(sum(v["misuse"] for v in m3v)), "n_m3": len(m3v),
           "forced_twin_answers_a_thing": rate([r for r in grad if r["named"]], "forced_point")[1],
           "bars": {"refused": 0.90, "named": 0.80, "valid_called_misuse_max": 0.05, "m3_pairs_called_misuse": 0}}
    ok = (out["n"] >= M.UNDERPOWERED_N and out["refused"] is not None and out["refused"] >= 0.90 and out["named"] >= 0.80
          and out["valid_called_misuse"] is not None and out["valid_called_misuse"] <= 0.05
          and out["m3_pairs_called_misuse"] == 0)
    out["verdict"] = ("NOT GRADABLE — no M5 answers" if not rows else
                      f"UNDERPOWERED (n {out['n']})" if out["n"] < M.UNDERPOWERED_N else "PASS" if ok else "FAIL")
    out["rows"] = rows
    return out


def _cited_thing(ep: Dict[str, object], things: Sequence[W.Thing], hyp: Optional[int] = None) -> Optional[int]:
    """M1's own rule for ONE cited episode: the thing the cited hypothesis is on — marks.hyp_label over the things its
    member fixations land on (world.fixation_thing). None: no thing, or a tie between two things."""
    fix, hyps = ep.get("fix") or [], ep.get("hyps") or []
    h = ep.get("hyp") if hyp is None else hyp
    if h is None or not (0 <= int(h) < len(hyps)):
        return None
    ft = fix_things(fix, things)
    return M.hyp_label(M.hyp_counts([hyps[int(h)]], ft)[0])


def grade_m4a(life: Life) -> Dict[str, object]:
    """PREREG §3 test 4a, graded on the FRESH sitting's `why` answers.
    EXIST (a wiring pin, never evidence): every cited moment is a training moment of THIS tape whose ear rows carry the word.
    ELIGIBLE: every cited episode had ≥ 2 hypotheses in view (the PREREG's population; a citation outside it is counted and
    fails the mark's reading rule).
    CARRY: the cited hypothesis' thing truly has the word's property (`world.word_true_of`); no thing = not CARRY.
    THE NULL: draw k = 1..20 — each cited episode's hypothesis replaced by one drawn uniformly among that episode's `hyps`,
    generator substream(ws, "m4-null:<k>"), in citation order. CARRY must be ≥ 0.90 and above the draws' 95th percentile."""
    from brain.world.seeds import substream
    per_word: Dict[str, Dict[str, object]] = {}
    cited: List[Tuple[str, Dict[str, object], List[W.Thing]]] = []      # in citation order: (word, episode, its things)
    n_cited = n_exist = n_elig = n_carry = 0
    unknown = []
    for item, ask in sorted(life.asks.items(), key=lambda kv: kv[1]["_seq"]):
        if ask.get("form") != "why":
            continue
        word = str(ask.get("word"))
        a = life.answer_of.get(item)
        if a is None or word in per_word:
            continue
        ans = a.get("answer") or raw_of(a)
        if ans.get("kind") != "because":
            unknown.append(word)
            per_word[word] = {"kind": ans.get("kind")}
            continue
        eps = list(ans.get("episodes") or [])
        if len(eps) > M4_MAX_CITED:
            raise GradeError(f"«why {word}» cites {len(eps)} episodes (> {M4_MAX_CITED})")
        ex = el = ca = 0
        for e in eps:
            m = str(e.get("moment"))
            eye = life.moment_eye.get(m)
            real = eye is not None and (eye.get("meta") or {}).get("kind") == "train" and word in life.moment_words.get(m, [])
            ex += int(real)
            things = things_of_dict(life.truth_of_eye(eye)["scene_dict"]) if real else []
            elig = len(e.get("hyps") or []) >= 2
            el += int(elig)
            k = _cited_thing(e, things) if real else None
            ca += int(k is not None and W.word_true_of(word, things[k]))
            cited.append((word, e, things))
        per_word[word] = {"kind": "because", "cited": len(eps), "exist": ex, "eligible": el, "carry": ca}
        n_cited, n_exist, n_elig, n_carry = n_cited + len(eps), n_exist + ex, n_elig + el, n_carry + ca
    twin = []
    for d in range(1, M4_TWIN_DRAWS + 1):
        rng = substream(int(life.ws), f"m4-null:{d}")
        hit = 0
        for word, e, things in cited:
            hyps = e.get("hyps") or []
            if not hyps:
                continue
            k = _cited_thing(e, things, hyp=int(rng.integers(len(hyps)))) if things else None
            hit += int(k is not None and W.word_true_of(word, things[k]))
        twin.append(hit / len(cited) if cited else None)
    tv = [v for v in twin if v is not None]
    p95 = float(np.percentile(np.asarray(tv), 95)) if tv else None
    exist = (n_exist / n_cited) if n_cited else None
    carry = (n_carry / n_cited) if n_cited else None
    out = {"words_asked": len(per_word), "words_explained": sum(1 for v in per_word.values() if v.get("kind") == "because"),
           "words_unknown": sorted(unknown), "n_cited": n_cited, "exist": exist, "eligible": n_elig, "carry": carry,
           "null_carry": twin, "null_p95": p95, "null_median": (float(np.median(np.asarray(tv))) if tv else None),
           "bars": {"exist": 1.0, "carry": 0.90, "carry_above": "the null's 95th percentile (20 draws)"}, "per_word": per_word}
    if not n_cited:
        out["verdict"] = "NOT GRADABLE — no citation"
    elif n_elig != n_cited:
        out["verdict"] = f"FAIL — {n_cited - n_elig} citations are of episodes with < 2 hypotheses (outside the PREREG's population)"
    elif n_cited < M.UNDERPOWERED_N:
        out["verdict"] = f"UNDERPOWERED (n {n_cited})"
    else:
        out["verdict"] = "PASS" if (exist == 1.0 and carry >= 0.90 and p95 is not None and carry > p95) else "FAIL"
    return out


# ------------------------------------------------------------------------------------------------ the pairing (the twin)
def sign_test(b: int, c: int) -> float:
    """Exact ONE-sided sign test on the discordant pairs (PREREG §3: «the brain better»): P(X ≥ b), X ~ Bin(b + c, 1/2),
    b = the first right and the second wrong, c = the reverse. No discordant pair → 1.0."""
    n = b + c
    if n == 0:
        return 1.0
    return float(sum(math.comb(n, i) for i in range(b, n + 1)) / (2.0 ** n))


def pair(rows_a: Sequence[Dict[str, object]], rows_b: Sequence[Dict[str, object]], graded_only: bool) -> Dict[str, object]:
    """Paired on the SAME items, covered and gradable in BOTH (the coverage is the eye's, so it is the same canvas fact).
    `rows_*` may hold several sets' rows (M3 pools both sets, PREREG §3)."""
    B = {r["item_id"]: r for r in rows_b}
    both = [(r, B[r["item_id"]]) for r in rows_a if r["item_id"] in B]
    if graded_only:
        both = [(x, y) for x, y in both if x["n_things"] in (2, 3)]
    both = [(x, y) for x, y in both if x["covered"] and y["covered"] and x["gradable"] and y["gradable"]]
    b = sum(1 for x, y in both if x["correct"] and not y["correct"])
    c = sum(1 for x, y in both if y["correct"] and not x["correct"])
    a = float(np.mean([x["correct"] for x, _ in both])) if both else None
    t = float(np.mean([y["correct"] for _, y in both])) if both else None
    own = (float(np.mean([not y.get("forced", False) for _, y in both])) if both else None)
    return {"n": len(both), "first": a, "second": t, "diff": (a - t if both else None), "first_only": b, "second_only": c,
            "p": sign_test(b, c), "second_answered": (float(np.mean([y["answered"] for _, y in both])) if both else None),
            "second_own_pointing": own, "smallest_passable_gap": (10.0 / len(both) if both else None)}


# ------------------------------------------------------------------------------------------------ one life's grade
def grade(root: Path, journal: Optional[Path], scored: Path, label: str, genome: Optional[Path] = None) -> Dict[str, object]:
    life = Life(root, journal, genome)
    ws = life.ws
    out: Dict[str, object] = {"label": label, "root": str(root), "world_seed": ws, "counts": life.counts(),
                              "journal": str(journal if journal is not None else Path(root) / "journal")}
    ms = meeting_seen(life)
    out["meeting"] = ms
    sets = list(life.cfg.get("sitting") or [])
    per_set: Dict[str, object] = {}
    m6_rows: Dict[str, List[Dict[str, object]]] = {}
    item_rows: Dict[str, Dict[str, List[Dict[str, object]]]] = {}
    for tset in sets:
        sc = SetCtx(life, tset)
        A = offline_answers(life, sc)
        g = R.grade_answers_r(_Ctx(sc, ms["seen"]), "A-RW-R", A)
        per_set[tset] = {"n_items": {m: len(v) for m, v in sc.items.items()}, "marks": g, "forced": A.get("forced", {})}
        m6_rows[tset] = pointing_rows(sc, A, "M6")
        item_rows[tset] = {m: pointing_rows(sc, A, m) for m in ("M1", "M3", "M6")}
        # AMENDMENT 1 §3 rule 1 (edit: Claude (Fable 5.1, the seat), 2026-09-28 22:08 +0400): which pointings were the grader's own uniform
        # draws (a `point: None` read forced) — printed with every pair, so a PASS cannot hide a twin that never pointed
        for rows_ in item_rows[tset].values():
            for r_ in rows_:
                r_["forced"] = bool((A["point"].get(r_["item_id"]) or {}).get("forced_by_grader"))
        if tset == GRADED_SET:
            out["M5"] = grade_m5(life, sc, A)
            # the pointer: the brain's recorded target against the grader's own reading with the truth
            bad = []
            checked = 0
            for it_id, want in sc.ptr.items():
                a = life.answer_of.get(it_id)
                if a is None:
                    continue
                raw = raw_of(a)
                ans = a.get("answer") or {}
                got = ans.get("hyp") if "hyp" in ans else raw.get("target")
                if raw.get("uncovered") or ans.get("kind") == "unseen":
                    got = None
                checked += 1
                if got != want:
                    bad.append((it_id, got, want))
            out["pointer"] = {"checked": checked, "mismatches": len(bad), "first": bad[:3]}
    out["sets"] = per_set
    out["items"] = item_rows
    out["M6_pooled"] = grade_m6_pooled(m6_rows, ms["seen"])
    out["M4a"] = grade_m4a(life)
    # the bars: the scored record's marks at this seed, with the law's arm replaced by THIS life's fresh-set grading
    sm_path = Path(scored) / str(ws) / "fresh" / "marks.json"
    if GRADED_SET in per_set and sm_path.exists():
        marks = json.loads(sm_path.read_text())
        rp = str(max(int(k) for k in marks["arms"]["A-RW-R"]["rp"]))
        mine = copy.deepcopy(per_set[GRADED_SET]["marks"])
        mine["reader"] = marks["arms"]["A-RW-R"]["rp"][rp].get("reader")
        marks["arms"]["A-RW-R"]["rp"] = {rp: mine}
        marks["meeting_seen"] = ms["seen"]
        for arm in list(marks["arms"]):
            if arm != "A-RW-R":
                marks["arms"][arm]["rp"] = {rp: marks["arms"][arm]["rp"][rp]}
        out["bars"] = R.bars_r(marks, rp=rp)
        out["bars_rp"] = rp
        out["scored_marks"] = str(sm_path)
        # THE NULL (PREREG §3): the life's M1 (graded, covered) and M3 (covered) against the 20 derangements' 95th percentile
        nl = marks.get("nulls") or {}
        m1v = mine["M1"]["graded"].get("covered")
        m3b = mine["M3"].get("all", mine["M3"])
        m3v = m3b.get("covered") if isinstance(m3b, dict) else None
        p1, p3 = (nl.get("summary_m1") or {}).get("p95"), (nl.get("summary_m3") or {}).get("p95")
        out["null"] = {"K": nl.get("K"), "m1": m1v, "m1_p95": p1, "m1_above": (m1v is not None and p1 is not None and m1v > p1),
                       "m3": m3v, "m3_p95": p3, "m3_above": (m3v is not None and p3 is not None and m3v > p3)}
    else:
        out["bars"] = None
        out["bars_why"] = f"no {GRADED_SET} sitting in this life, or no scored record at {sm_path}"
    return out


def _f(v, nd=3) -> str:
    return "n/a" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def report_lines(g: Dict[str, object]) -> List[str]:
    L: List[str] = []
    c = g["counts"]
    L.append(f"LIFE {g['label']} · world seed {g['world_seed']} · root {g['root']}")
    L.append(f"  tape rows {c['tape_rows']} · scene rows {c['scene_rows_by_sense']} · training scenes {c['train_scenes']}")
    L.append(f"  asks on the tape {c['asks_on_tape']} · answers in the journal {c['answers_in_journal']} {c['answers_by']} · "
             f"asks without an answer {c['n_asks_without_answer']} {c['asks_without_answer']}")
    m = g["meeting"]
    L.append(f"  the one «dax» meeting: seen = {m.get('seen')} ({m.get('why') or m.get('read_by')}); things {m.get('things')}; "
             f"fixations → thing {m.get('fix_thing')}")
    if g.get("pointer"):
        L.append(f"  the pointer: checked {g['pointer']['checked']} · mismatches {g['pointer']['mismatches']} {g['pointer']['first']}")
    if g.get("bars"):
        L.append(f"  THE BARS (S1b-1R's own rules; oracle readings = the scored record at this seed; reading point {g['bars_rp']}):")
        for k, b in g["bars"].items():
            if isinstance(b, dict):
                keep = {x: b[x] for x in ("value", "n", "all", "bar", "p_oracle", "pass", "not_gradable", "underpowered",
                                           "ceiling_bound", "refusal", "false_refusal") if x in b}
                L.append(f"    {k:<12} {json.dumps(keep, default=str)}")
    for tset, ps in g["sets"].items():
        mk = ps["marks"]
        m1, m3 = mk["M1"]["graded"], mk["M3"].get("all", mk["M3"])
        rd = mk["roads"][LAW]
        L.append(f"  SET {tset}{' (READINGS ONLY)' if tset != GRADED_SET else ''}: items {ps['n_items']} · read forced {ps.get('forced')}")
        L.append(f"    M1 covered {_f(m1.get('covered'))} (n {m1.get('n_covered')}) · over ALL items {_f(m1.get('all'))} "
                 f"(n {m1.get('n_all')}) · coverage {_f(m1.get('coverage'))} · chance {_f(m1.get('chance_covered'))}")
        L.append(f"    M3 covered {_f(m3.get('covered'))} (n {m3.get('n_covered')}) · over ALL {_f(m3.get('all'))}")
        L.append(f"    M2a refusal {_f(rd['M2a']['all']['refusal'])} (n {rd['M2a']['all']['n']}) · false refusal {_f(rd.get('false_refusal'))}")
        L.append(f"    M2b {_f(rd['M2b']['graded']['correct'])} (n {rd['M2b']['graded']['n']}) · over ALL {_f(rd['M2b']['graded']['correct_all'])}")
    p = g["M6_pooled"]
    L.append(f"  TEST 6 · M6 POOLED over {p['sets']}: covered {_f(p['covered'])} (n {p['n_covered']} of {p['n_items']}; "
             f"chance {_f(p['chance_covered'])}; bar {p['bar']}, n ≥ {p['n_bar']}) → {p['verdict']}")
    if g.get("null"):
        z = g["null"]
        L.append(f"  THE NULL ({z['K']} shuffled-utterance draws, the scored record's): M1 {_f(z['m1'])} vs p95 {_f(z['m1_p95'])} → "
                 f"{'ABOVE' if z['m1_above'] else 'NOT ABOVE'} · M3 {_f(z['m3'])} vs p95 {_f(z['m3_p95'])} → "
                 f"{'ABOVE' if z['m3_above'] else 'NOT ABOVE'}")
    a = g["M4a"]
    L.append(f"  TEST 4a · EXPLAIN: words asked {a['words_asked']} · explained {a['words_explained']} · «unknown» {a['words_unknown']} · "
             f"citations {a['n_cited']} (of episodes with ≥ 2 hypotheses: {a['eligible']}) · EXIST {_f(a['exist'])} (a wiring pin, bar 1.000) · "
             f"CARRY {_f(a['carry'])} (bar 0.90) · the null's median {_f(a['null_median'])}, p95 {_f(a['null_p95'])} → {a['verdict']}")
    L.append("  TEST 4b · RULE: NOT BUILT tonight (PREREG §3)")
    if g.get("M5"):
        f = g["M5"]
        L.append(f"  TEST 5 · MISUSE: refused {_f(f['refused'])} (bar 0.90) · named misuse {_f(f['named'])} (bar 0.80) · n {f['n']} "
                 f"(unheard {f['n_unheard']}) · valid phrases called misuse {_f(f['valid_called_misuse'])} of {f['n_valid']} "
                 f"(bar ≤ 0.05) · never-heard pairs called misuse {f['m3_pairs_called_misuse']} of {f['n_m3']} (bar 0) → {f['verdict']}")
        L.append(f"    by kind: {json.dumps(f['by_kind'])}")
    return L


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="grade_life")
    ap.add_argument("--root", required=True)
    ap.add_argument("--journal")
    ap.add_argument("--genome")
    ap.add_argument("--scored", default="/data/dev/brain-runs/scene-s1b1r")
    ap.add_argument("--label", default="brain")
    ap.add_argument("--out")
    ap.add_argument("--pair-with", help="another grade.json (the twin's): the paired sign test on M1 and M3, first = this life")
    a = ap.parse_args(argv)
    g = grade(Path(a.root), Path(a.journal) if a.journal else None, Path(a.scored), a.label,
              Path(a.genome) if a.genome else None)
    out = Path(a.out) if a.out else Path(a.root) / "grade" / a.label
    out.mkdir(parents=True, exist_ok=True)
    lines = report_lines(g)
    if a.pair_with:
        other = json.loads(Path(a.pair_with).read_text())
        prs = {}
        # ABLE (#228; PREREG §3): the second's FORCED M1 on the fresh set must be above the null's p95, or «first > second»
        # only says the first can point — the pair then reads VOID, never PASS
        o_g = other["sets"][GRADED_SET]["marks"]["M1"]["graded"]
        o_m1, o_n = o_g.get("covered"), o_g.get("n_covered")
        p95 = (g.get("null") or {}).get("m1_p95")
        able = o_m1 is not None and p95 is not None and o_m1 > p95
        lines.append(f"  THE SECOND IS ABLE? its forced M1 {_f(o_m1)} on n {o_n} (the items whose every word it heard) vs the null's p95 "
                     f"{_f(p95)} → {'ABLE' if able else 'NOT ABLE — every pair reads VOID'} · its answers read forced: "
                     f"{other['sets'][GRADED_SET].get('forced')}")
        # AMENDMENT 1 §3 rule 1: BOTH pairs pool the fresh and the older set (population moved, bar unchanged)
        for mark, graded_only, sets in (("M1", True, M6_POOLED_SETS), ("M3", False, M6_POOLED_SETS)):
            ra = [r for s_ in sets for r in g["items"].get(s_, {}).get(mark, [])]
            rb = [r for s_ in sets for r in other["items"].get(s_, {}).get(mark, [])]
            prs[mark] = pair(ra, rb, graded_only)
            p = prs[mark]
            p["sets"] = list(sets)
            ok = p["n"] >= M.UNDERPOWERED_N and p["diff"] is not None and p["diff"] >= 0.10 and p["p"] < 0.001
            # a pair with no item gradable in BOTH is NOT COMPARED (PREREG §3: a mark the second cannot answer by construction
            # is never a first's win); under n 30 it is UNDERPOWERED — printed with its numbers, never PASS or FAIL
            p["verdict"] = ("VOID" if not able else
                            "NOT COMPARED — no item is gradable in both" if p["n"] == 0 else
                            f"UNDERPOWERED (n {p['n']} < {M.UNDERPOWERED_N})" if p["n"] < M.UNDERPOWERED_N else
                            "PASS" if ok else "FAIL")
            p["second_unheard"] = sum(1 for r in rb if not r["gradable"])
            p["second_items"] = len(rb)
            lines.append(f"  PAIRED {mark} over {list(sets)}: {g['label']} {_f(p['first'])} vs {other['label']} {_f(p['second'])} on n {p['n']} · "
                         f"diff {_f(p['diff'])} · discordant {p['first_only']} / {p['second_only']} · exact one-sided sign test p {p['p']:.2e} "
                         f"→ {p['verdict']} (bar: diff ≥ 0.10 and p < 0.001; at this n the smallest passable gap is "
                         f"{_f(p['smallest_passable_gap'])}) · the second heard every word of "
                         f"{p['second_items'] - p['second_unheard']} of {p['second_items']} phrases · it pointed ON ITS OWN on "
                         f"{_f(p['second_own_pointing'])} of the paired items"
                         + ("" if p["second_own_pointing"] is None or p["second_own_pointing"] >= 0.5 or not str(p["verdict"]).startswith("PASS")
                            else " — READ AS «the brain points where the organs' road does not», never «adds over the cells»"))
        lines.append("  NOT COMPARED with the second, by construction: test 4 (its `why` answers «unknown») and test 5 (it has no misuse act)")
        g["paired"] = {"with": a.pair_with, "able": able, **prs}
    (out / "grade.json").write_text(json.dumps(g, indent=1, sort_keys=True, default=R._jsonable if hasattr(R, "_jsonable") else str))
    (out / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"[grade_life] written {out / 'grade.json'} and {out / 'report.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
