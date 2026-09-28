#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-28 20:30 +0400 — BRAIN-IN-BODY: the grader of a life (PREREG-BRAIN-IN-BODY §3, INTERFACE §6).
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
            k = str(j.get("item"))
            if k in self.answer_of:
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
    """The life's answers in the scored file's own shape: {"point": {item: raw}, "roads": {"LAW": {item: raw}}}."""
    point: Dict[str, Dict[str, object]] = {}
    road: Dict[str, Dict[str, object]] = {}
    for mark, items in ctx.items.items():
        for it in items:
            a = life.answer_of.get(str(it["item_id"]))
            if a is None:
                continue
            raw = a.get("raw")
            if raw is None:
                raise GradeError(f"answer {it['item_id']} carries no `raw` (INTERFACE addendum 1)")
            (point if mark in POINT_MARKS else road)[str(it["item_id"])] = raw
    return {"point": point, "roads": {LAW: road}, "m2a_keys": {LAW: "none_i"}, "mouths": {LAW: "believed"}}


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
    if seen is not True:
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
        raw = a.get("raw") or {}
        named = raw.get("misuse") is not None
        none = bool(raw.get("none_i")) if raw.get("point") is not None else False
        unheard = bool(raw.get("unheard"))
        forced = a.get("raw_forced") or {}
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
                valid.append({"item_id": it["item_id"], "mark": mark, "misuse": (a.get("raw") or {}).get("misuse") is not None})
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


def _thing_at(pos: Sequence[float], things: Sequence[W.Thing], margin: int = 4) -> Optional[int]:
    """The thing under a position given in grid cells (a hypothesis' mean position): its pixel centre inside a box ± 4 px."""
    py, px = (float(pos[0]) + 0.5) * CELL_PX, (float(pos[1]) + 0.5) * CELL_PX
    hit = [i for i, t in enumerate(things)
           if t.top - margin <= py < t.top + t.side + margin and t.left - margin <= px < t.left + t.side + margin]
    return hit[0] if len(hit) == 1 else None


def grade_m4a(life: Life) -> Dict[str, object]:
    """PREREG §3 test 4a. EXIST: every cited moment is a training moment of THIS tape whose ear rows carry the word.
    CARRY: the thing under the cited position truly has the word's property (the world's own `word_true_of`).
    The shuffled-citation twin: the same number of citations drawn at random from the moments where the word was heard,
    each with a position drawn at random among that canvas's THINGS' centres — 20 draws; the brain's pooled CARRY must sit
    above the twin's 95th percentile. (The twin points at true things' centres, never at empty space: it is blind to which
    thing the word was about, and to nothing else.)"""
    heard_at: Dict[str, List[str]] = collections.defaultdict(list)
    for i, m in sorted(life.train_moment.items()):
        for w in dict.fromkeys(life.moment_words.get(m, [])):
            heard_at[w].append(m)
    per_word = {}
    n_cited = n_exist = n_carry = 0
    unknown = []
    for item, ask in sorted(life.asks.items()):
        if ask.get("form") != "why":
            continue
        word = str(ask.get("word"))
        a = life.answer_of.get(item)
        if a is None:
            continue
        ans = a.get("answer") or {}
        if ans.get("kind") != "because":
            unknown.append(word)
            per_word[word] = {"kind": ans.get("kind"), "heard": len(heard_at.get(word, []))}
            continue
        eps = list(ans.get("episodes") or [])
        if len(eps) > M4_MAX_CITED:
            raise GradeError(f"«why {word}» cites {len(eps)} episodes (> {M4_MAX_CITED})")
        ex = ca = 0
        for e in eps:
            m = str(e.get("moment"))
            eye = life.moment_eye.get(m)
            real = eye is not None and (eye.get("meta") or {}).get("kind") == "train" and word in life.moment_words.get(m, [])
            ex += int(real)
            if real:
                things = things_of_dict(life.truth_of_eye(eye)["scene_dict"])
                k = _thing_at(e.get("pos") or (-9, -9), things)
                ca += int(k is not None and W.word_true_of(word, things[k]))
        per_word[word] = {"kind": "because", "cited": len(eps), "exist": ex, "carry": ca, "heard": len(heard_at.get(word, []))}
        n_cited, n_exist, n_carry = n_cited + len(eps), n_exist + ex, n_carry + ca
    # the shuffled-citation twin
    twin = []
    for d in range(M4_TWIN_DRAWS):
        rng = np.random.default_rng([int(life.ws) & 0xFFFFFFFF, 0x4D34, d])
        tot = hit = 0
        for word, pw in sorted(per_word.items()):
            if pw.get("kind") != "because" or not heard_at.get(word):
                continue
            ms = heard_at[word]
            for _ in range(int(pw["cited"])):
                m = ms[int(rng.integers(len(ms)))]
                things = things_of_dict(life.truth_of_eye(life.moment_eye[m])["scene_dict"])
                k = int(rng.integers(len(things)))
                tot += 1
                hit += int(W.word_true_of(word, things[k]))
        twin.append(hit / tot if tot else None)
    tv = sorted(v for v in twin if v is not None)
    p95 = (tv[min(len(tv) - 1, int(math.ceil(0.95 * len(tv))) - 1)] if tv else None)
    exist = (n_exist / n_cited) if n_cited else None
    carry = (n_carry / n_cited) if n_cited else None
    out = {"words_asked": len(per_word), "words_explained": sum(1 for v in per_word.values() if v.get("kind") == "because"),
           "words_unknown": sorted(unknown), "n_cited": n_cited, "exist": exist, "carry": carry,
           "twin_carry": twin, "twin_p95": p95, "twin_median": (tv[len(tv) // 2] if tv else None),
           "bars": {"exist": 1.0, "carry": 0.90, "carry_above": "the twin's 95th percentile"}, "per_word": per_word}
    if not n_cited:
        out["verdict"] = "NOT GRADABLE — no citation"
    elif n_cited < M.UNDERPOWERED_N:
        out["verdict"] = f"UNDERPOWERED (n {n_cited})"
    else:
        out["verdict"] = "PASS" if (exist == 1.0 and carry >= 0.90 and p95 is not None and carry > p95) else "FAIL"
    return out


# ------------------------------------------------------------------------------------------------ the pairing (the twin)
def sign_test(b: int, c: int) -> float:
    """Exact two-sided sign test on the discordant pairs (b: first right, second wrong; c: the reverse)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2.0 ** n)
    return float(min(1.0, 2.0 * tail))


def pair(rows_a: Sequence[Dict[str, object]], rows_b: Sequence[Dict[str, object]], graded_only: bool) -> Dict[str, object]:
    """Paired on the SAME items, covered and gradable in BOTH (the coverage is the eye's, so it is the same canvas fact)."""
    B = {r["item_id"]: r for r in rows_b}
    both = [(r, B[r["item_id"]]) for r in rows_a if r["item_id"] in B]
    if graded_only:
        both = [(x, y) for x, y in both if x["n_things"] in (2, 3)]
    both = [(x, y) for x, y in both if x["covered"] and y["covered"] and x["gradable"] and y["gradable"]]
    b = sum(1 for x, y in both if x["correct"] and not y["correct"])
    c = sum(1 for x, y in both if y["correct"] and not x["correct"])
    a = float(np.mean([x["correct"] for x, _ in both])) if both else None
    t = float(np.mean([y["correct"] for _, y in both])) if both else None
    return {"n": len(both), "first": a, "second": t, "diff": (a - t if both else None), "first_only": b, "second_only": c,
            "p": sign_test(b, c), "second_answered": (float(np.mean([y["answered"] for _, y in both])) if both else None)}


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
        per_set[tset] = {"n_items": {m: len(v) for m, v in sc.items.items()}, "marks": g}
        m6_rows[tset] = pointing_rows(sc, A, "M6")
        item_rows[tset] = {m: pointing_rows(sc, A, m) for m in ("M1", "M3", "M6")}
        if tset == GRADED_SET:
            out["M5"] = grade_m5(life, sc, A)
            # the pointer: the brain's recorded target against the grader's own reading with the truth
            bad = []
            for it_id, want in sc.ptr.items():
                a = life.answer_of.get(it_id)
                if a is None:
                    continue
                raw = a.get("raw") or {}
                got = raw.get("target") if "target" in raw else (None if raw.get("uncovered") else a.get("pointer"))
                if "target" in raw and got != want:
                    bad.append((it_id, got, want))
            out["pointer"] = {"checked": sum(1 for k in sc.ptr if (life.answer_of.get(k) or {}).get("raw", {}).get("target") is not None
                                             or (life.answer_of.get(k) or {}).get("raw", {}).get("uncovered")),
                              "mismatches": len(bad), "first": bad[:3]}
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
        L.append(f"  SET {tset}{' (READINGS ONLY)' if tset != GRADED_SET else ''}: items {ps['n_items']}")
        L.append(f"    M1 covered {_f(m1.get('covered'))} (n {m1.get('n_covered')}) · over ALL items {_f(m1.get('all'))} "
                 f"(n {m1.get('n_all')}) · coverage {_f(m1.get('coverage'))} · chance {_f(m1.get('chance_covered'))}")
        L.append(f"    M3 covered {_f(m3.get('covered'))} (n {m3.get('n_covered')}) · over ALL {_f(m3.get('all'))}")
        L.append(f"    M2a refusal {_f(rd['M2a']['all']['refusal'])} (n {rd['M2a']['all']['n']}) · false refusal {_f(rd.get('false_refusal'))}")
        L.append(f"    M2b {_f(rd['M2b']['graded']['correct'])} (n {rd['M2b']['graded']['n']}) · over ALL {_f(rd['M2b']['graded']['correct_all'])}")
    p = g["M6_pooled"]
    L.append(f"  TEST 6 · M6 POOLED over {p['sets']}: covered {_f(p['covered'])} (n {p['n_covered']} of {p['n_items']}; "
             f"chance {_f(p['chance_covered'])}; bar {p['bar']}, n ≥ {p['n_bar']}) → {p['verdict']}")
    a = g["M4a"]
    L.append(f"  TEST 4a · EXPLAIN: words asked {a['words_asked']} · explained {a['words_explained']} · «unknown» {a['words_unknown']} · "
             f"citations {a['n_cited']} · EXIST {_f(a['exist'])} (bar 1.000) · CARRY {_f(a['carry'])} (bar 0.90) · "
             f"shuffled-citation twin median {_f(a['twin_median'])}, p95 {_f(a['twin_p95'])} → {a['verdict']}")
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
        for mark, graded_only in (("M1", True), ("M3", False)):
            prs[mark] = pair(g["items"][GRADED_SET][mark], other["items"][GRADED_SET][mark], graded_only)
            p = prs[mark]
            ok = p["n"] >= M.UNDERPOWERED_N and p["diff"] is not None and p["diff"] >= 0.10 and p["p"] < 0.001
            p["verdict"] = ("VOID — the second answers nothing" if p["second_answered"] in (None, 0.0) else
                            "PASS" if ok else "FAIL")
            lines.append(f"  PAIRED {mark}: {g['label']} {_f(p['first'])} vs {other['label']} {_f(p['second'])} on n {p['n']} · "
                         f"diff {_f(p['diff'])} · discordant {p['first_only']} / {p['second_only']} · exact sign test p {p['p']:.2e} · "
                         f"the second answered {_f(p['second_answered'])} → {p['verdict']} (bar: diff ≥ 0.10 and p < 0.001)")
        g["paired"] = {"with": a.pair_with, **prs}
    (out / "grade.json").write_text(json.dumps(g, indent=1, sort_keys=True, default=R._jsonable if hasattr(R, "_jsonable") else str))
    (out / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"[grade_life] written {out / 'grade.json'} and {out / 'report.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
