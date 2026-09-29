"""genome/brain.py — THE BRAIN ORGAN (BRAIN-IN-BODY; docs/brain/body/INTERFACE-BRAIN-ORGAN.md §3).

edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:26 +0400 — new module. Rung 1 is the brain AS IT SCORED: S1b-1R's arm
A-RW-R, the LAW road (brain/scene/learners.py: RWLearner, RWRoad, produce_believed), with T-MEM-2's «none» hook
(brain/scene/health.py: heard_none, attribution) read-only beside it. NO new learning rule.

One organ, declared by the genome's BRAIN line (`declared["BRAIN"]`), living inside the creature's mind as a NEW consumer of
the eye's glances and the ear's words. The mind hands it:
  learn(glance, words, moment=, scene=, world_seed=)   one training canvas: the offline life's ONE step, in its order —
        the «none» hook BEFORE train_scene (generator `tmem2-none:<scene>`, as run_tmem2.py's hook; None before the first
        calibration, as the hook was inactive until the first reading point, and None with nothing in view) · train_scene
        (generator `episodic:<scene>`, as run.train_arm) · the row appended to the calibration list · the learner's own
        attribution kept per word for M4 · a calibration when the count learned reaches a `calibrate at` value.
  ask(payload, glance)   never learns. Forms `begin`, `end`, `point`, `what`, `say`, `why` (INTERFACE §2). Every answer
        carries the digest of §2's table (`kind`, …) and `raw`: the offline function's OWN return, with the offline field
        names, exactly as the scored `answers_10000.json` holds it (the seat's 20:2x addition: one grader serves bench and
        body).
  calibrate()   the reading point: RWLearner.calibrate over every scene learned (level = `conformal`), then calibrate_r(eps)
        — the EAR's types and the READER. Never the world's types (the organ holds none).

THE FENCE: this module never reads the world's truth and never imports the scene world, the graders, the cache or the runner
(tests/genome/test_brain_organ.py, with planted offenders). The tie generator is `substream(test_seed, "tie:<item>")`,
pinned equal to the grader's own. Every generator is a named substream; nothing journaled depends on set order, the clock
or `hash()`.

Where each BRAIN value is read (no VALUE-UNREAD):
  lr           RWLearner(lr) — the delta rule's step.
  eps          calibrate_r(eps) — the READER's shrinkage (the LAW's «what is this?» band).
  none_level   RWLearner.none_level — τ_none, the DISTANCE «none» flag (the reading flag `none` / `none_fit` inside `raw`);
               the LAW's own refusal is τ_point (`none_i`) at `conformal`, as S1b-1R scored it.
  conformal    RWLearner.calibrate(level=) — τ_point (the LAW's «none») and τ_word.
  young        RWLearner.p_from — the learner's maturity (fewer meetings answer by prototype and band; only mature words
               are typed, emitted, believed); and M4: a word under `young` meetings is «unknown».
  young_rule   (optional; edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:20 +0400 — AMENDMENT 1 §2) RWLearner.young_rule — absent
               = the law; "nearest" (`young <n> nearest`) = a pointing ask on ONE young word points at the hypothesis nearest
               the word's prototype under the reader's one-alone metric (RWLearner.answer_point / _young_nearest).
  calibrate_at the scene counts at which learn() calibrates (and `begin` calibrates when scenes were learned since).
  replay       "none" is the only rule rung 1 runs; "uniform" / "strong" refuse by name.
  hears        hears(source): the sources whose canvases the brain learns from.

edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:39 +0400 — PREREG-BRAIN-IN-BODY (signed, 12bdea6, sha256 e39b512e…) moves the contract:
M4 `why` cites ONLY among the word's episodes with ≥ 2 hypotheses in view (a 1-hypothesis episode stores responsibility exactly
1, so the unrestricted rule cited only those); each cited episode carries `hyp` and that moment's `fix` and `hyps`; `learn`
returns the canvas's `fix` and `hyps` (the grader reads whether the one «dax» meeting was seen). The brain keeps, per scene
learned, its moment, scene index, located cells and hypotheses' member lists.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.scene import eye as E
from brain.scene import health as H
from brain.scene import learners as Lr
from brain.world.seeds import substream

CFG_KEYS = ("lr", "eps", "none_level", "conformal", "young", "calibrate_at", "replay", "hears")
# edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:20 +0400 — PREREG-BRAIN-IN-BODY AMENDMENT 1 §2: `young_rule` is an OPTIONAL key (the
# parser declares it only under `young <n> nearest`); absent or "band" = the law and leaves NO trace in the cfg or the learner's
# vars (so a law brain's state hash, save file and summary are what they were); "nearest" = F-M6; any other word refuses by name.
CFG_OPTIONAL = ("young_rule",)
YOUNG_RULES = ("band", "nearest")
REPLAY_BUILT = ("none",)
REPLAY_KNOWN = ("none", "uniform", "strong")
WHY_MAX = 8                    # M4: up to 8 episodes
WHY_MIN_HYPS = 2               # M4: cited only among episodes with ≥ 2 hypotheses in view (PREREG §3, row M4a)
CELL_PX = 8                    # a fixation cell's centre pixel: cell * 8 + 4 (world.fixation_thing's arithmetic)
BOX_MARGIN = 4                 # the box ± 4 px
FEATS = 144
# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:52 +0400 — PREREG-METADATA-1 §2: version 2 carries `segments` (the source and the author of every
# scene learned); a version 1 state still LOADS, read as one run `lived` by an unknown author.
STATE_VERSION = 2
READS_VERSIONS = (1, 2)
SOURCES = ("lived", "prenatal", "implanted-episode", "implanted-knowledge", "inherited")


class BrainError(Exception):
    pass


# ------------------------------------------------------------------------------------------------ small pieces
def tie_rng(test_seed: int, item: str) -> np.random.Generator:
    """The item's own tie generator — the grader's `marks.tie_rng` (pinned equal in the tests), without importing the graders."""
    return substream(int(test_seed), f"tie:{item}")


def things_in_view(glance: Dict[str, object]) -> Tuple[List["E.Hypothesis"], np.ndarray]:
    """The glance (genome.gaze.glances's own return) → the thing hypotheses (brain.scene.eye.hypotheses over the LOCATED
    glances `feats[:len(fix)]`; a coarse `feats[len(fix)]` is kept aside, unused, as the cache kept it) and the learner's
    input `learners.feed_rw(hyp feats, hyp pos)` — run.Things.hyps / for_arm's own construction."""
    fix = [(int(y), int(x)) for y, x in glance["fix"]]
    feats = glance["feats"]
    if len(feats) < len(fix):
        raise BrainError(f"a glance with {len(fix)} fixations carries only {len(feats)} features")
    located = (np.stack([np.asarray(v, dtype=np.float64) for v in feats[:len(fix)]]) if fix
               else np.zeros((0, FEATS), dtype=np.float64))
    hyps = E.hypotheses(fix, located)
    hf = np.stack([h.feat for h in hyps]) if hyps else np.zeros((0, FEATS))
    pos = np.array([h.pos for h in hyps], dtype=np.float64).reshape(-1, 2)
    return hyps, Lr.feed_rw(hf, pos)


def pointer_hypothesis(box: Sequence[float], centroid: Optional[Sequence[float]], fix: Sequence[Sequence[int]],
                       hyps: Sequence["E.Hypothesis"]) -> Optional[int]:
    """THE POINTER (INTERFACE §3 with the seat's 20:3x addition): the parent's pointing gesture `box` = [top, left, side] px at
    ONE thing → the hypothesis with the most of its fixations inside the box ± 4 px (a fixation cell's centre pixel
    cell · 8 + 4; half-open as world.fixation_thing has it); a tie → the nearest mean position (cells) to the pointed
    thing's ink `centroid` [cy, cx] px mapped as (cy / 8 − 0.5, cx / 8 − 0.5) — marks.thing_hypothesis's own arithmetic —
    then the lower index; no centroid → the box's centre (declared); no fixation inside → None («unseen»)."""
    top, left, side = (float(v) for v in box)
    counts = []
    for h in hyps:
        c = 0
        for m in h.members:
            py, px = int(fix[m][0]) * CELL_PX + CELL_PX // 2, int(fix[m][1]) * CELL_PX + CELL_PX // 2
            if top - BOX_MARGIN <= py < top + side + BOX_MARGIN and left - BOX_MARGIN <= px < left + side + BOX_MARGIN:
                c += 1
        counts.append(c)
    if not counts or max(counts) == 0:
        return None
    best = [i for i, c in enumerate(counts) if c == max(counts)]
    if len(best) == 1:
        return best[0]
    cy_px, cx_px = (float(centroid[0]), float(centroid[1])) if centroid is not None else (top + side / 2.0, left + side / 2.0)
    cy, cx = cy_px / 8.0 - 0.5, cx_px / 8.0 - 0.5
    return min(best, key=lambda i: ((hyps[i].pos[0] - cy) ** 2 + (hyps[i].pos[1] - cx) ** 2, i))


def _num(v):
    """A JSON-able plain number (numpy scalars → Python)."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


def _plain(o):
    """Deep copy into JSON-able Python (numpy → lists / scalars; tuples → lists; dict keys kept as strings)."""
    if isinstance(o, dict):
        return {str(k): _plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_plain(v) for v in o]
    if isinstance(o, np.ndarray):
        return _plain(o.tolist())
    return _num(o)


def check_cfg(cfg: Dict[str, object]) -> Dict[str, object]:
    """`declared["BRAIN"]` whole: every key present, no other, each of its kind; replay other than "none" refuses by name."""
    if not isinstance(cfg, dict):
        raise BrainError(f"BRAIN: the config is not a dict: {cfg!r}")
    missing = [k for k in CFG_KEYS if k not in cfg]
    extra = sorted(k for k in cfg if k not in CFG_KEYS + CFG_OPTIONAL)
    if missing or extra:
        raise BrainError(f"BRAIN: missing {missing}, unknown {extra} (the keys are {list(CFG_KEYS)})")
    out = {"lr": float(cfg["lr"]), "eps": float(cfg["eps"]), "none_level": float(cfg["none_level"]),
           "conformal": float(cfg["conformal"]), "young": int(cfg["young"]),
           "calibrate_at": [int(x) for x in cfg["calibrate_at"]], "replay": str(cfg["replay"]),
           "hears": [str(x) for x in cfg["hears"]]}
    rule = cfg.get("young_rule", "band")
    if rule not in YOUNG_RULES:
        raise BrainError(f"BRAIN: young_rule {rule!r} is no rule (known: {list(YOUNG_RULES)}; AMENDMENT 1 §2)")
    if rule == "nearest":
        out["young_rule"] = "nearest"
    if out["replay"] not in REPLAY_KNOWN:
        raise BrainError(f"BRAIN: replay {out['replay']!r} is no rule (known: {list(REPLAY_KNOWN)})")
    if out["replay"] not in REPLAY_BUILT:
        raise BrainError(f"BRAIN: replay {out['replay']!r}: not built at rung 1 (rung 1 runs replay none)")
    if not (0.0 < out["lr"] <= 1.0) or out["eps"] <= 0.0 or out["young"] < 1:
        raise BrainError(f"BRAIN: lr in (0, 1], eps > 0, young >= 1 — got {out}")
    if not (0.0 < out["none_level"] < 1.0) or not (0.0 < out["conformal"] < 1.0):
        raise BrainError(f"BRAIN: none and conformal are levels in (0, 1) — got {out}")
    at = out["calibrate_at"]
    if not at or at[0] < 1 or any(b <= a for a, b in zip(at, at[1:])):
        raise BrainError(f"BRAIN: calibrate at takes strictly rising scene counts >= 1, got {at}")
    return out


# ================================================================================================ the organ
class Brain:
    """ONE organ: an RWLearner (A-RW-R's learning, lr from the genome), its calibration list, the LAW road over it, and the
    per-word EPISODES the learner attributed (M4's store). See the module docstring for where each BRAIN value is read."""

    def __init__(self, cfg: Dict[str, object]):
        self.cfg = check_cfg(cfg)
        self.L = Lr.RWLearner(lr=self.cfg["lr"])
        self.L.p_from = self.cfg["young"]                 # an INSTANCE attribute: the class default stays P_FROM_MEETING
        self.L.none_level = self.cfg["none_level"]
        if self.cfg.get("young_rule") == "nearest":     # F-M6 (AMENDMENT 1 §2): an INSTANCE attribute, set only off the law
            self.L.young_rule = "nearest"
        self.seen: List[Tuple[np.ndarray, List[str], None]] = []   # the calibration list (run.train_arm's `seen`)
        self.moments: List[str] = []                      # per scene learned: its tape moment
        self.canvas: List[List[object]] = []              # per scene learned: [its located cells, its hypotheses' member lists]
        self.scenes: List[int] = []                       # per scene learned: its scene index
        # M4's store: per word, its episodes [learn order, hypothesis, pos y, pos x, responsibility]
        self.episodes: Dict[str, List[List[float]]] = {}
        self.n_calibrations = 0
        self.calibrated_at: Optional[int] = None          # the count learned at the last calibration
        # edit: Claude (Fable 5.1, the seat), 2026-09-29 20:52 +0400 — PREREG-METADATA-1 §2: the runs over the order of life, each
        # {start, end, source, author, first_moment, last_moment}; `author` is the life's own name (the mind sets it); `_run` is
        # the source and author of the scenes learned NEXT (lived by this life unless a surgery opened another run).
        self.segments: List[Dict[str, object]] = []
        self.author: Optional[str] = None
        self._run: Optional[Tuple[str, Optional[str]]] = None

    # -- the source of every memory, and the census (PREREG-METADATA-1) ------------------------
    def begin_run(self, source: str, author: Optional[str]) -> None:
        """The scenes learned from now on carry this source and author, until `end_run()`."""
        if source not in SOURCES:
            raise BrainError(f"begin_run: source {source!r} is not one of {SOURCES}")
        self._run = (str(source), None if author is None else str(author))

    def end_run(self) -> None:
        self._run = None

    def note_learned(self, moment: str) -> None:
        """One scene was appended to the order of life: the last run is extended, or a new one opened."""
        source, author = self._run if self._run is not None else ("lived", self.author)
        order = self.n_learned - 1
        last = self.segments[-1] if self.segments else None
        if last is not None and last["end"] == order and last["source"] == source and last["author"] == author:
            last["end"] = order + 1
            last["last_moment"] = str(moment)
        else:
            self.segments.append({"start": order, "end": order + 1, "source": source, "author": author,
                                  "first_moment": str(moment), "last_moment": str(moment)})

    def source_of(self, order: int) -> Dict[str, object]:
        for s in self.segments:
            if s["start"] <= order < s["end"]:
                return s
        raise BrainError(f"source_of: no run holds order {order} (runs {[(s['start'], s['end']) for s in self.segments]})")

    def census(self) -> Dict[str, object]:
        """What the brain holds, counted by source. Pure: it reads the learner's stores and the runs, it writes nothing."""
        L = self.L
        kinds = {w: i for i, t in enumerate(self.types()) for w in t} if self.n_calibrations else {}
        mature = set(L.mature_words())
        words: Dict[str, object] = {}
        given_only: List[str] = []
        for w in L.words:
            j = L.index[w]
            by: Dict[str, int] = {}
            for t in L.store_t[j]:
                src = str(self.source_of(int(t) - 1)["source"])
                by[src] = by.get(src, 0) + 1
            words[w] = {"meetings": int(L.meetings[j]), "episodes_by_source": dict(sorted(by.items())),
                        "mature": w in mature, "kind": kinds.get(w)}
            if by and not by.get("lived"):
                given_only.append(w)
        scenes_by: Dict[str, int] = {}
        for s in self.segments:
            scenes_by[str(s["source"])] = scenes_by.get(str(s["source"]), 0) + int(s["end"]) - int(s["start"])
        return _plain({"scenes": self.n_learned, "scenes_by_source": scenes_by, "n_words": len(L.words), "words": words,
                       "given_only_words": given_only, "calibrations": self.n_calibrations,
                       "runs": [dict(s) for s in self.segments]})

    # -- the mind's questions ------------------------------------------------------------------
    def hears(self, source: Optional[str]) -> bool:
        return source is not None and str(source) in self.cfg["hears"]

    @property
    def n_learned(self) -> int:
        return len(self.seen)

    def road(self) -> "Lr.RWRoad":
        """The LAW (A-RW-R): the ear's types, the READER band, production maturity, «none» = τ_point."""
        return Lr.RWRoad(self.L)

    # -- learning ------------------------------------------------------------------------------
    def learn(self, glance: Dict[str, object], words: Sequence[str], *, moment: str, scene: int,
              world_seed: int) -> Dict[str, object]:
        hyps, X = things_in_view(glance)
        words = [str(w) for w in words]
        none: Optional[bool] = None
        if self.n_calibrations > 0 and X.shape[0] > 0:     # T-MEM-2's hook: active from the first reading point on
            hn = H.heard_none(self.road(), X, words, substream(int(world_seed), f"tmem2-none:{int(scene)}"))
            none = hn["none"]
        known = set(self.L.index)
        self.L.train_scene(X, words, referent=None, rng=substream(int(world_seed), f"episodic:{int(scene)}"))
        self.seen.append((X, words, None))
        order = len(self.moments)
        self.moments.append(str(moment))
        self.scenes.append(int(scene))
        fix_l = [[int(y), int(x)] for y, x in glance["fix"]]
        hyps_l = [[int(m) for m in h.members] for h in hyps]
        self.canvas.append([fix_l, hyps_l])
        new = [w for w in dict.fromkeys(words) if w not in known]
        att = H.attribution(self.L, X, words, new)
        for w, h in att.items():
            if h is None:
                continue
            j = self.L.index[w]
            r = 1.0 if w in new else float(self.L.store_r[j][-1][h])
            self.episodes.setdefault(w, []).append([order, int(h), float(hyps[h].pos[0]), float(hyps[h].pos[1]), r])
        self.note_learned(str(moment))          # PREREG-METADATA-1 §2: the scene's source and author
        calibrated = False
        if self.n_learned in self.cfg["calibrate_at"]:
            self.calibrate()
            calibrated = True
        return {"n_hyp": int(X.shape[0]), "words": words, "attributed": {w: (None if h is None else int(h)) for w, h in att.items()},
                "none": none, "calibrated": calibrated, "fix": fix_l, "hyps": hyps_l}

    def calibrate(self) -> Dict[str, object]:
        """The reading point: τ_point / τ_word at `conformal`, the refusal states and τ_none at `none_level`, over EVERY scene
        learned (run.prepare), then the ear's types and the READER at `eps` (calibrate_r; no world types — the organ holds
        none). Returns a small record for the journal."""
        cal = self.L.calibrate(self.seen, level=self.cfg["conformal"])
        cr = self.L.calibrate_r(self.cfg["eps"])
        self.n_calibrations += 1
        self.calibrated_at = self.n_learned
        return _plain({"at": self.n_learned, "tau_point": cal["tau_point"], "tau_none": cal["tau_none"],
                       "types": cr["types"], "mature": cr["mature"], "one_alone": cr["one_alone"], "bands": cr["bands"],
                       "n": {"point": cal["n"].get("point"), "none": cal["n"].get("none")}})

    # -- asking --------------------------------------------------------------------------------
    def ask(self, payload: Dict[str, object], glance: Optional[Dict[str, object]]) -> Dict[str, object]:
        """One ask (INTERFACE §2). NEVER learns: no call below writes the learner (the LAW's reads, the mouth's read-backs)."""
        form = payload.get("form")
        if form == "begin":
            did = False
            if self.n_learned > 0 and self.calibrated_at != self.n_learned:
                self.calibrate()
                did = True
            a = {"kind": "begin", "calibrated": did, "at": self.n_learned}
            return {**a, "raw": dict(a)}
        if form == "end":
            return {"kind": "end", "raw": {"kind": "end"}}
        if form == "why":
            a = self.why(str(payload.get("word")))
            return {**a, "raw": json.loads(json.dumps(a))}
        if form not in ("point", "what", "say"):
            raise BrainError(f"ask: no such form {form!r}")
        if glance is None:
            raise BrainError(f"ask: form {form!r} needs its canvas's glance")
        # edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:49 +0400 — a pointing / naming / saying ask without its `item` or `test_seed`
        # REFUSES by name: a default would build a wrong tie generator silently (visible only on an exact tie).
        missing = [k for k in ("item", "test_seed") if payload.get(k) is None]
        if missing:
            raise BrainError(f"ask: form {form!r} needs {missing} (the item's tie generator is substream(test_seed, 'tie:<item>'))")
        hyps, X = things_in_view(glance)
        fix = [(int(y), int(x)) for y, x in glance["fix"]]
        item = str(payload["item"])
        ts = int(payload["test_seed"])
        if form == "point":
            return self._point(list(payload.get("phrase") or []), hyps, X, fix, item, ts)
        box = payload.get("box")
        h = None if box is None else pointer_hypothesis(box, payload.get("centroid"), fix, hyps)
        if form == "what":
            name_item = payload.get("mark") == "NAME"
            if h is None:
                raw = {"emit": None, "uncovered": True}
                if name_item:
                    raw["name"] = None
                return {"kind": "unseen", "raw": raw}
            x = X[h]
            emit = list(self.road().held_words(x)) if self.n_calibrations else []
            raw = {"emit": emit}
            if name_item:
                raw["name"] = self._names(x)
            if emit:
                return {"kind": "words", "words": list(emit), "hyp": int(h), "raw": raw}
            return {"kind": "unknown", "hyp": int(h), "raw": raw}
        # say
        if h is None:
            return {"kind": "unseen", "raw": {"spoken": None, "reason": "uncovered", "uncovered": True}}
        if not self.n_calibrations:
            return {"kind": "declined", "reason": "not calibrated", "hyp": int(h), "raw": {"spoken": None, "reason": "not calibrated"}}
        a = Lr.produce_believed(self.road(), X, int(h), lambda: tie_rng(ts, item))
        raw = _plain(a)
        if a.get("spoken"):
            return {"kind": "phrase", "words": list(a["spoken"]), "hyp": int(h), "raw": raw}
        return {"kind": "declined", "reason": a.get("reason"), "hyp": int(h), "raw": raw}

    def _point(self, phrase: List[str], hyps, X: np.ndarray, fix, item: str, ts: int) -> Dict[str, object]:
        """M5's misuse check first (the EAR's types), then the LAW's pointing (RWLearner.answer_point with the item's tie
        generator; «none» = `none_i`, τ_point)."""
        mis = self.misuse(phrase)
        forced = None
        if all(w in self.L.index for w in phrase) and X.shape[0] == 0:
            raw = {"point": None, "none": None, "best": None, "n_hyp": 0}
            if mis:
                return {"kind": "misuse", "words": mis, "raw": {"point": None, "misuse": mis}, "raw_forced": raw}
            return {"kind": "none", "reason": "nothing in view", "raw": raw}
        forced = _plain(self.L.answer_point(X, phrase, tie_rng(ts, item)))
        if mis:
            return {"kind": "misuse", "words": mis, "raw": {"point": None, "misuse": mis}, "raw_forced": forced}
        if forced.get("point") is None:
            return {"kind": "unheard", "words": list(forced.get("unheard") or []), "raw": forced}
        if forced.get("none_i"):
            return {"kind": "none", "raw": forced}
        h = int(forced["point"])
        return {"kind": "thing", "hyp": h, "pos": [float(hyps[h].pos[0]), float(hyps[h].pos[1])],
                "fix": [[int(fix[m][0]), int(fix[m][1])] for m in hyps[h].members], "raw": forced}

    def types(self) -> List[Tuple[str, ...]]:
        """The EAR's types at the last calibration (the LAW road's own `types()`); none before the first."""
        if not self.n_calibrations:
            return []
        return [tuple(t) for t in self.road().types()]

    def misuse(self, phrase: Sequence[str]) -> Optional[List[str]]:
        """M5: the first pair (in the phrase's order) of two DIFFERENT words the EAR puts in ONE type — words that never met in
        one utterance and share a clique of the exclusion graph (Ear.cover over the mature words, at the last calibration):
        a phrase naming nothing that can exist. Words of different types are never misuse, heard together or not."""
        where: Dict[str, int] = {}
        for k, T in enumerate(self.types()):
            for w in T:
                where[w] = k
        ws = [str(w) for w in phrase]
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                a, b = ws[i], ws[j]
                if a != b and a in where and where.get(b) == where[a]:
                    return [a, b]
        return None

    def _names(self, x: np.ndarray) -> Dict[str, Optional[str]]:
        """NAME's forced name per LEARNED type (learners.name_forced over the type's words), keyed by the type's words joined
        with «|» — the organ holds no world type names (RAISED: the scored file keys it by the world's «shape/colour/size»)."""
        return {"|".join(T): self.L.name_forced(x, list(T)) for T in self.types()}

    def why(self, word: str) -> Dict[str, object]:
        """M4 · explain (PREREG §3 row M4a over INTERFACE §3): «unknown» when the word was never heard or is young (< `young`
        meetings) or has no attributed episode with ≥ 2 hypotheses in view; else up to 8 episodes FROM ITS OWN STORE where it
        heard the word and attributed it (health.attribution's reading), chosen among the episodes with ≥ 2 hypotheses in
        view, strongest responsibility first, ties by the earlier moment: each {moment, scene, hyp, pos, fix, hyps};
        rule.over = the cited moments, rule.band = the word's READER band (the LAW's «what is this?»)."""
        j = self.L.index.get(word)
        if j is None or int(self.L.meetings[j]) < self.cfg["young"]:
            return {"kind": "unknown", "word": word}
        pool = [e for e in self.episodes.get(word, []) if len(self.canvas[int(e[0])][1]) >= WHY_MIN_HYPS]
        if not pool:
            # PREREG-METADATA-1 §2: a word with no citable episode of its own, met in a GIVEN run, is named as given. A brain
            # whose every run is lived never enters here with a hit, so its answer is the old one.
            given = [self.source_of(int(t) - 1) for t in self.L.store_t[j]]
            given = [s for s in given if s["source"] != "lived"]
            if given:
                return {"kind": "given", "word": word, "source": str(given[0]["source"]), "author": given[0]["author"]}
            return {"kind": "unknown", "word": word}
        eps_ = sorted(pool, key=lambda e: (-e[4], e[0]))[:WHY_MAX]
        cited = [{"moment": self.moments[int(e[0])], "scene": self.scenes[int(e[0])], "hyp": int(e[1]), "pos": [e[2], e[3]],
                  "fix": [list(c) for c in self.canvas[int(e[0])][0]], "hyps": [list(m) for m in self.canvas[int(e[0])][1]]}
                 for e in eps_]
        band = None
        if self.n_calibrations:
            wst = self.L.reader["ear"]["word"].get(word)
            band = None if wst is None else wst["band"]
        return {"kind": "because", "word": word, "episodes": cited, "rule": {"over": [c["moment"] for c in cited], "band": band}}

    # -- the brain's own turn -------------------------------------------------------------------
    # edit: Claude (Fable 5.1, the seat), 2026-09-29 16:27 +0400 — PREREG-BRAIN-DRIVES §2.2 / §2.3 (signed 3aa380b, sha256 a5fdea1e…): THE TURN.
    # What the brain does BY ITSELF at a canvas, before it hears: it expects, it says, it asks. READ-ONLY: no call below
    # writes the learner (the LAW road's reads and the scored mouth's read-backs), pinned by the state hash around every turn
    # (tests/genome/test_brain_turn.py). Nothing here reads the world's truth.
    def turn(self, glance: Dict[str, object], *, scene: int, world_seed: int, says: int = 1, asks: int = 1) -> Dict[str, object]:
        """One turn (PREREG-BRAIN-DRIVES §2.2):
          things / members / cells   the eye's hypotheses, each with the indices of its fixations and their cells;
          order      the hypotheses by their number of fixations, most first, ties by the lower index;
          held       per hypothesis, the LAW road's held words;
          expected   per hypothesis, its forced name in each learned type (RWRoad.believed), a type with no mature word → None;
          say        (says 1) the first hypothesis in `order` for which the scored mouth speaks (learners.produce_believed, the
                     read-back included; the tie generator of hypothesis h is substream(world_seed, "turn-say:<scene>:<h>"));
          ask        (asks 1) the first hypothesis in `order` with NO held word.
        Before the first calibration, or with nothing in view, the turn ends with its `reason` and says and asks nothing."""
        if says not in (0, 1) or asks not in (0, 1):
            raise BrainError(f"turn: says and asks each take 0 or 1, got says {says!r} asks {asks!r}")
        hyps, X = things_in_view(glance)
        n = int(X.shape[0])
        fix = [[int(y), int(x)] for y, x in glance["fix"]]
        members = [[int(m) for m in h.members] for h in hyps]
        cells = [[list(fix[m]) for m in ms] for ms in members]
        order = sorted(range(n), key=lambda h: (-len(members[h]), h))
        out: Dict[str, object] = {"scene": int(scene), "n_hyp": n, "order": order, "members": members, "held": [], "expected": [],
                                  "say": None, "ask": None, "reason": None}
        if n == 0:
            out["reason"] = "nothing in view"
            return out
        if not self.n_calibrations:
            out["reason"] = "not calibrated"
            return out
        road = self.road()
        out["held"] = [list(road.held_words(X[h])) for h in range(n)]
        Bv = road.believed(X)
        out["expected"] = [[Bv[k][h] for k in range(len(Bv))] for h in range(n)]
        if says:
            for h in order:
                a = Lr.produce_believed(road, X, h, lambda h=h: substream(int(world_seed), f"turn-say:{int(scene)}:{h}"))
                if a.get("spoken"):
                    m = a.get("margin")
                    out["say"] = {"hyp": int(h), "fix": cells[h], "pos": [float(hyps[h].pos[0]), float(hyps[h].pos[1])],
                                  "words": [str(w) for w in a["spoken"]], "readback": int(a["readback_point"]),
                                  "margin": (float(m) if m is not None and math.isfinite(float(m)) else None)}
                    break
        if asks:
            for h in order:
                if not out["held"][h]:
                    out["ask"] = {"hyp": int(h), "fix": cells[h], "pos": [float(hyps[h].pos[0]), float(hyps[h].pos[1])]}
                    break
        return out

    @staticmethod
    def surprise(turn: Dict[str, object], words: Sequence[str]) -> Optional[float]:
        """PREREG-BRAIN-DRIVES §2.3: with U the distinct words of the utterance, 1 − (the largest number of U's words that ONE
        hypothesis's expected names hold) / |U|. None when the turn holds no expectation or the utterance no word."""
        U = list(dict.fromkeys(str(w) for w in words))
        if not U or not turn.get("expected"):
            return None
        got = max(len(set(U) & {w for w in e if w is not None}) for e in turn["expected"])
        return 1.0 - got / len(U)

    # -- the status and the state --------------------------------------------------------------
    def summary(self) -> Dict[str, object]:
        L = self.L
        out = {"learned": self.n_learned, "calibrations": self.n_calibrations, "calibrated_at": self.calibrated_at,
               "words": len(L.words), "mature": len(L.mature_words()), "types": [list(t) for t in self.types()],
               "tau_point": L.tau_point, "episodes": sum(len(v) for v in self.episodes.values())}
        # edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:20 +0400 — the rule is NAMED when it is not the law (a law life's journaled
        # summary rows stay byte-identical: creature/mind.py journals this dict at every calibration)
        if self.cfg.get("young_rule") == "nearest":
            out["young_rule"] = "nearest"
        return _plain(out)

    def _state(self, version: int = STATE_VERSION) -> Tuple[Dict[str, object], Dict[str, np.ndarray]]:
        enc = _Encoder()
        learner = {k: enc.enc(v) for k, v in sorted(vars(self.L).items())}
        meta = {"version": int(version), "cfg": self.cfg, "learner": learner,
                "brain": {"seen": enc.enc(self.seen), "moments": list(self.moments), "scenes": list(self.scenes),
                          "canvas": self.canvas,
                          "episodes": enc.enc(self.episodes), "n_calibrations": self.n_calibrations,
                          "calibrated_at": self.calibrated_at}}
        if version >= 2:
            meta["brain"]["segments"] = [dict(s) for s in self.segments]
        return meta, enc.arrays()

    def state_hash(self) -> str:
        """The hash of what the brain LEARNED: the version 1 form of the state, as every pin before METADATA 1 took it.
        edit: Claude (Fable 5.1, the seat), 2026-09-29 20:54 +0400 — PREREG-METADATA-1 AMENDMENT 1: the runs (who gave a memory) are not
        learning; they are covered by the saved FILE's own hash (`save`), which is taken over the whole version 2 state."""
        meta, arrays = self._state(version=1)
        return _hash(meta, arrays)

    def save(self, base: Path) -> None:
        """<base>.npz (the arrays, grouped by dtype) + <base>.json (everything else, dicts as ordered pairs, the state hash).
        The caller renames atomically."""
        base = Path(base)
        meta, arrays = self._state()
        meta["state_hash"] = _hash(meta, arrays)
        with open(str(base) + ".npz", "wb") as f:
            np.savez(f, **arrays)
        Path(str(base) + ".json").write_text(json.dumps(meta, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    # edit: Claude (Fable 5.1, the seat), 2026-09-29 20:35 +0400 — PREREG-INHERIT §2 / §3: a newborn takes its parent's brain.
    @classmethod
    def inherit(cls, base: Path, cfg: Dict[str, object]) -> Tuple["Brain", Dict[str, object]]:
        """PREREG-INHERIT §2: the parent's saved pair <base>.json|npz -> (the child's brain, {learned, hash}). What passes: the
        learner and the four index-aligned lists (`seen`, `moments`, `scenes`, `canvas`). What does not: `episodes`, the store the
        brain CITES — a child cites only what it lived. Every refusal names the inheritance."""
        base = Path(base)
        j, z = Path(str(base) + ".json"), Path(str(base) + ".npz")
        if not (j.exists() and z.exists()):
            raise BrainError(f"inherit: the pair is not whole ({j.name} {'present' if j.exists() else 'absent'}, "
                             f"{z.name} {'present' if z.exists() else 'absent'}) — the organism does not start")
        try:
            saved_hash = json.loads(j.read_text(encoding="utf-8")).get("state_hash")
            if not saved_hash:
                raise BrainError("the pair carries no state hash")
            b = cls.load(base, cfg)
        except BrainError as e:
            raise BrainError(f"inherit: {e}")
        except Exception as e:
            raise BrainError(f"inherit: the pair cannot be read ({e!r})")
        info = {"learned": int(b.n_learned), "hash": str(saved_hash)}
        b.episodes = {}
        for s in b.segments:                    # PREREG-METADATA-1 §2: what the parent LIVED the child INHERITED; a gift stays a gift
            if s["source"] == "lived":
                s["source"] = "inherited"
        return b, info

    @classmethod
    def load(cls, base: Path, cfg: Dict[str, object]) -> "Brain":
        base = Path(base)
        meta = json.loads(Path(str(base) + ".json").read_text(encoding="utf-8"))
        want = check_cfg(cfg)
        if meta.get("version") not in READS_VERSIONS:
            raise BrainError(f"load: state version {meta.get('version')!r}, this organ reads {READS_VERSIONS}")
        # edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:20 +0400 — a brain saved under one young rule never loads under the other
        saved_rule, want_rule = meta["cfg"].get("young_rule", "band"), want.get("young_rule", "band")
        if saved_rule != want_rule:
            raise BrainError(f"load: the saved brain lived under young_rule {saved_rule!r}, not {want_rule!r} — a resume never "
                             f"changes the genome (AMENDMENT 1 §2)")
        if meta["cfg"] != want:
            raise BrainError(f"load: the saved brain lived under {meta['cfg']}, not {want} — a resume never changes the genome")
        with np.load(str(base) + ".npz") as z:
            arrays = {k: z[k] for k in z.files}
        saved_hash = meta.pop("state_hash", None)
        if saved_hash is not None and _hash(meta, arrays) != saved_hash:
            raise BrainError("load: the state's files do not hash to the hash they carry")
        dec = _Decoder(arrays)
        b = cls(cfg)
        for k, v in meta["learner"].items():
            setattr(b.L, k, dec.dec(v))
        bb = meta["brain"]
        b.seen = [tuple(t) for t in dec.dec(bb["seen"])]
        b.moments = list(bb["moments"])
        b.scenes = [int(s) for s in bb["scenes"]]
        b.canvas = [[[list(c) for c in f], [list(m) for m in hs]] for f, hs in bb["canvas"]]
        b.episodes = dec.dec(bb["episodes"])
        b.n_calibrations = int(bb["n_calibrations"])
        b.calibrated_at = bb["calibrated_at"]
        if "segments" in bb:
            b.segments = [dict(s) for s in bb["segments"]]
        elif b.n_learned:                       # a version 1 state: one run, lived, its author unknown (PREREG-METADATA-1 §2)
            b.segments = [{"start": 0, "end": b.n_learned, "source": "lived", "author": None,
                           "first_moment": b.moments[0], "last_moment": b.moments[-1]}]
        covered = sum(int(s["end"]) - int(s["start"]) for s in b.segments)
        if covered != b.n_learned:
            raise BrainError(f"load: the runs cover {covered} scenes, the brain learned {b.n_learned}")
        return b


# ================================================================================================ the state's encoding
def _hash(meta: Dict[str, object], arrays: Dict[str, np.ndarray]) -> str:
    h = hashlib.sha256()
    h.update(json.dumps(meta, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    for k in sorted(arrays):
        a = np.ascontiguousarray(arrays[k])
        h.update(f"|{k}|{a.dtype.str}|{a.shape}|".encode("utf-8"))
        h.update(a.tobytes())
    return h.hexdigest()


class _Encoder:
    """Every value of a learner's / the brain's state as JSON with arrays by reference: each array is flattened into ONE pool
    per dtype (so ~60,000 small arrays become a handful of npz entries), referenced by (pool, offset, shape); identical
    arrays share their bytes (a loaded brain gets independent copies — the live learner aliases none of them). Dicts are
    ordered PAIRS (insertion order survives the round-trip), tuples stay tuples, floats keep inf / nan exactly."""

    def __init__(self):
        self.pools: Dict[str, List[np.ndarray]] = {}
        self.size: Dict[str, int] = {}
        self.seen: Dict[Tuple[str, bytes], int] = {}

    def _array(self, a: np.ndarray) -> Dict[str, object]:
        a = np.ascontiguousarray(a)
        dt = a.dtype.str
        flat = a.reshape(-1)
        key = (dt, hashlib.sha256(flat.tobytes()).digest() + len(flat).to_bytes(8, "little"))
        off = self.seen.get(key)
        if off is None:
            off = self.size.get(dt, 0)
            self.pools.setdefault(dt, []).append(flat)
            self.size[dt] = off + flat.size
            self.seen[key] = off
        return {"t": "nd", "p": dt, "o": off, "s": list(a.shape)}

    def enc(self, v):
        if isinstance(v, np.ndarray):
            return self._array(v)
        if isinstance(v, bool) or v is None or isinstance(v, str):
            return v
        if isinstance(v, (np.bool_,)):
            return {"t": "npb", "v": bool(v)}
        if isinstance(v, int):
            return v
        if isinstance(v, np.integer):
            return {"t": "npi", "d": v.dtype.str, "v": int(v)}
        # edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:49 +0400 — np.floating BEFORE float: np.float64 subclasses float, and
        # repr(np.float64(x)) is «np.float64(x)» under numpy 2, which float() cannot read back.
        if isinstance(v, np.floating):
            return {"t": "npf", "d": v.dtype.str, "v": repr(float(v))}
        if isinstance(v, float):
            return {"t": "f", "v": repr(v)}
        if isinstance(v, tuple):
            return {"t": "tuple", "v": [self.enc(x) for x in v]}
        if isinstance(v, list):
            return [self.enc(x) for x in v]
        if isinstance(v, dict):
            return {"t": "dict", "v": [[self.enc(k), self.enc(x)] for k, x in v.items()]}
        if isinstance(v, Lr.RunningStandardiser):
            return {"t": "stats", "v": {"n": v.n, "mean": self._array(v.mean), "m2": self._array(v.m2)}}
        if isinstance(v, Lr.Ear):
            return {"t": "ear", "v": [[k, self.enc(x)] for k, x in sorted(vars(v).items())]}
        raise BrainError(f"state: cannot encode a {type(v).__name__}")

    def arrays(self) -> Dict[str, np.ndarray]:
        return {f"pool{dt}": (np.concatenate(ps) if ps else np.zeros(0)) for dt, ps in self.pools.items()}


class _Decoder:
    def __init__(self, arrays: Dict[str, np.ndarray]):
        self.arrays = arrays

    def dec(self, v):
        if isinstance(v, list):
            return [self.dec(x) for x in v]
        if not isinstance(v, dict):
            return v
        t = v.get("t")
        if t == "nd":
            pool = self.arrays[f"pool{v['p']}"]
            n = int(np.prod(v["s"])) if v["s"] else 1
            return np.array(pool[v["o"]:v["o"] + n], dtype=np.dtype(v["p"]), copy=True).reshape(v["s"])
        if t == "npb":
            return np.bool_(v["v"])
        if t == "npi":
            return np.dtype(v["d"]).type(v["v"])
        if t == "f":
            return float(v["v"])
        if t == "npf":
            return np.dtype(v["d"]).type(float(v["v"]))
        if t == "tuple":
            return tuple(self.dec(x) for x in v["v"])
        if t == "dict":
            return {self.dec(k): self.dec(x) for k, x in v["v"]}
        if t == "stats":
            s = Lr.RunningStandardiser(1)
            s.n = int(v["v"]["n"])
            s.mean = self.dec(v["v"]["mean"])
            s.m2 = self.dec(v["v"]["m2"])
            return s
        if t == "ear":
            e = Lr.Ear()
            for k, x in v["v"]:
                setattr(e, k, self.dec(x))
            return e
        raise BrainError(f"state: cannot decode {t!r}")
