# edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:28 +0400 — BRAIN-IN-BODY §5 (docs/brain/body/INTERFACE-BRAIN-ORGAN.md);
# the seat's additive amendment (message during the build, 2026-09-28 ~20:27 +0400): every ask carrying a `box` also carries
# a `centroid`; every truth file's `scene_dict` carries `centroids` (ALL things) and `row`.
"""creature/senses/scene.py — SENSE scene: the scene-talk world's tape rows (INTERFACE-BRAIN-ORGAN.md §2).

`plan(cfg)` is a PURE function of `declared["WORLD_SCENE"]` (INTERFACE §1): the whole ordered list of moments
(training scenes, then one sitting per declared set, in declared order), each a dict `{moment, rows, truth,
phase}` — `rows` a list of `{sense, meta, ext, payload}` with `payload` a ZERO-ARG CALLABLE, and `truth` a
ZERO-ARG CALLABLE (or None) returning the truth-file dict. Both are lazy so building the plan for 10,000+
moments costs seconds, not the PNG-rendering time of the whole life — the executor and `tools/brain/
make_tape.py` share this ONE function, so a threaded life and a synchronous tape-maker agree row for row.
`phase` is bookkeeping ONLY (never published) — `("train",)` or `("sitting", set_name, "begin" | "split" |
"why" | "end")`.

**The render is shared, once per canvas.** `W.render_scene(scene)` returns both the PNG pixels (the eye
row's payload) and every thing's ink centroid (the seat's amendment: an ask's `centroid`, and the truth
file's `scene_dict["centroids"]`) — the single expensive call of this module. `_memo_render(scene)` returns
ONE zero-arg getter, closed over by the eye payload, every `what`/`say` ask's payload on that canvas, and
the truth callable, so a canvas is rendered exactly once no matter how many of those three read it — never
twice, and never at PLAN time (`plan()` never renders; every render happens inside a `payload`/`truth`
callable, invoked by the executor or `make_tape.py` alone).

The questions are the offline generators' own (`brain.scene.marks`: `m1_items`, `m2a_items`, `m2b_items`,
`m6_items`, `m3_items`, `speak_items`, `decline_items`, `speak2_items`; NAME built inline exactly as
`brain.scene.run.build_questions`/`build_questions_r` build it — the same 8-line loop, read from the source,
not guessed) — called on truth rows built as `{**scene.to_dict(), "row": i}` (the marks.py generators never
read `fix_thing`/`centroids`/eye-derived fields; those belong to the offline glance cache, never to this
sense — DECLARED, RAISED in HANDBACK-B: `box`+`centroid` replace `hyp` here precisely because no glance
exists yet). A sitting truth file's `items` are those generator dicts THEMSELVES, unmodified (no `hyp`
added, none removed) — the grader feeds them to the offline graders unchanged.

DECLARED READINGS (raised in HANDBACK-B, none fixed by INTERFACE-BRAIN-ORGAN.md or the seat's amendment):
  - Split order within one sitting: `("test", "m2b", "m6", "m3", "speak", "decline")`, `+ ("speak2",)` for the
    "fresh" set only — `brain.scene.cache.TEST_SPLITS`/`FRESH_SPLITS`'s own order (not imported: cache.py
    pulls in the glance stack this sense must never touch; the order is copied here as a plain tuple).
  - Ask order on one `test`-split canvas: M1 (if the scene has one), M2a (always — every test canvas
    therefore publishes at least one ask), NAME (1-thing scenes only), M5 (fresh set only, every canvas).
  - `box` is null on every `point` form (M1, M2a, M3, M6, M5); the target thing's own `[top, left, side]` on
    every `what` (M2b, NAME) / `say` (SPEAK, SPEAK2, DECLINE) form. `word` is null except on `why` (M4).
  - `centroid` (the seat's amendment) rides beside `box` on every ask row: null when `box` is null (point
    forms — the schema stays uniform, 7 keys on every ask), else `[cy, cx]` (floats) of `render_scene`'s
    second return at the target's index.
  - `scene_dict` = `{**scene.to_dict(), "row": r, "centroids": [[cy, cx], ...]}` (the seat's amendment) for
    EVERY truth file (train and sitting alike); for a train truth, `r` = the training scene's own index `i`
    (there is no other "row" concept during training).
  - `end`'s payload mirrors `begin`'s shape: `{"form": "end", "set": set_name}` (INTERFACE names `begin`'s
    payload explicitly; `end`'s is unspecified there).
  - `why`'s `moment` id: `sc<ws>q-<set>-why-<word>` (INTERFACE names the payload/meta shape but not the id;
    every published word is <= 8 letters a-z, `genome.world.encode_word`'s own alphabet, so it is always a
    safe moment-string component).
  - M5 (no PREREG file for it exists on this worktree — RAISED; built exactly to the builder brief's own
    spec): kind cycles `("colour", "shape", "size")` by `row_index % 3`; the pair is drawn without
    replacement from that kind's names (`substream(ts, f"m5-item:{item_id}")`); "every third item" is read
    as `row_index % 3 == 2` — which, by the cycle above, is always the "size" kind (the two conditions
    coincide; noted, not hidden) — its extra word is drawn from one of the OTHER two types (uniform), one
    word of that type; the whole phrase is emitted in the fixed order (size, colour, shape). Since
    `W.SIZE_NAMES` has exactly two members, every size-kind pair is `{"big", "small"}` in drawn order.

A pure SENSE (G4-1's writer sweep): writes only the tape (through `publish`), `root/truth/scene/*.json` and
its own cursor `root/scene/SCENE-CURSOR` (written AFTER a moment's rows are durable — #230's cursor law, the
same shape `creature/senses/game.py`/`chat.py` use) — never state/journal/memory, never imports Organism.
"""
from __future__ import annotations

import io
import json
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

from brain.scene import marks as M
from brain.scene import world as W
from brain.world.seeds import substream
from genome.world import encode_word

# The arming gate (creature/senses/game.py's own C2/C3 discipline): a genome line arms nothing until the
# code carrying it exists — creature/body.py:_declared_scene_config reads it.
SCENE_DOOR_GATED = True

CURSOR_NAME = "SCENE-CURSOR"
_WAIT_POLL_S = 0.005

POINT_MARKS = frozenset({"M1", "M2a", "M3", "M6", "M5"})
WHAT_MARKS = frozenset({"M2b", "NAME"})
SAY_MARKS = frozenset({"SPEAK", "SPEAK2", "DECLINE"})

# DECLARED (module docstring): the split order within one sitting; brain.scene.cache.TEST_SPLITS/FRESH_SPLITS's own order.
_TEST_SPLITS: Tuple[str, ...] = ("test", "m2b", "m6", "m3", "speak", "decline")
_FRESH_EXTRA: Tuple[str, ...] = ("speak2",)

_M5_KINDS: Tuple[str, ...] = ("colour", "shape", "size")
_M5_ORDER: Tuple[str, ...] = ("size", "colour", "shape")


def _m5_words(kind: str) -> Tuple[str, ...]:
    return {"colour": W.COLOUR_NAMES, "shape": W.SHAPES, "size": W.SIZE_NAMES}[kind]


# ------------------------------------------------------------------------------------------------ bytes / rendering
def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _json_bytes(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True).encode("utf-8")


def _assert_word(word: str) -> None:
    encode_word(word)   # raises ValueError naming the word when it is not <= 8 letters a-z (its own law)


def _memo_render(scene: W.Scene) -> Callable[[], Tuple[np.ndarray, List[Tuple[float, float]]]]:
    """ONE zero-arg getter for `W.render_scene(scene)`, memoized on first call — shared by the eye payload,
    every `what`/`say` ask's `centroid`, and the truth callable of the SAME canvas, so a canvas is rendered
    exactly once regardless of how many of those three ever call it (and never at plan() time)."""
    cache: List[Tuple[np.ndarray, List[Tuple[float, float]]]] = []

    def get() -> Tuple[np.ndarray, List[Tuple[float, float]]]:
        if not cache:
            cache.append(W.render_scene(scene))
        return cache[0]
    return get


# ------------------------------------------------------------------------------------------------ items (marks.py's own)
def _name_items(truth_rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    """NAME: exactly `brain.scene.run.build_questions`/`build_questions_r`'s own 8-line loop, read from the
    source (not guessed) — one item per ONE-thing `test`-split row."""
    items = []
    for row in truth_rows:
        if len(row["things"]) == 1:
            t = row["things"][0]
            items.append({"item_id": f"NAME:{row['item_id']}", "mark": "NAME", "row": int(row["row"]), "phrase": [],
                          "target": 0, "shape": t["shape"], "colour": t["colour"], "size": t["size"], "n_things": 1})
    return items


def _m5_items(truth_rows: Sequence[Dict[str, object]], ts: int) -> List[Dict[str, object]]:
    items = []
    for row in truth_rows:
        r = int(row["row"])
        item_id = f"M5:{row['item_id']}"
        kind = _M5_KINDS[r % 3]
        rng = substream(ts, f"m5-item:{item_id}")
        words = _m5_words(kind)
        idx = rng.choice(len(words), size=2, replace=False)
        pair = [words[int(i)] for i in idx]
        by_type: Dict[str, List[str]] = {"size": [], "colour": [], "shape": []}
        by_type[kind] = list(pair)
        if r % 3 == 2:      # DECLARED: "every third item" == the size-kind item, by the cycle above
            other = [k for k in _M5_KINDS if k != kind]
            extra_kind = other[int(rng.integers(len(other)))]
            extra_words = _m5_words(extra_kind)
            extra = extra_words[int(rng.integers(len(extra_words)))]
            by_type[extra_kind].append(extra)
        phrase = [w for t in _M5_ORDER for w in by_type[t]]
        items.append({"item_id": item_id, "mark": "M5", "row": r, "phrase": phrase, "kind_of_pair": kind,
                      "pair": pair, "n_things": len(row["things"])})
    return items


_SPLIT_ITEM_FN = {
    "m2b": lambda truth: M.m2b_items(truth),
    "m6": lambda truth: M.m6_items(truth),
    "m3": lambda truth: M.m3_items(truth),
    "speak": lambda truth: M.speak_items(truth),
    "decline": lambda truth: M.decline_items(truth),
    "speak2": lambda truth: M.speak2_items(truth),
}

_MARK_ORDER_ON_TEST = {"M1": 0, "M2a": 1, "NAME": 2, "M5": 3}


def _test_split_by_row(truth_rows: Sequence[Dict[str, object]], ts: int, want_m5: bool) -> Dict[int, List[Dict[str, object]]]:
    by_row: Dict[int, List[Dict[str, object]]] = {}
    for it in M.m1_items(truth_rows, ts):
        by_row.setdefault(it["row"], []).append(it)
    for it in M.m2a_items(truth_rows, ts):
        by_row.setdefault(it["row"], []).append(it)
    for it in _name_items(truth_rows):
        by_row.setdefault(it["row"], []).append(it)
    if want_m5:
        for it in _m5_items(truth_rows, ts):
            by_row.setdefault(it["row"], []).append(it)
    for r in by_row:
        by_row[r].sort(key=lambda it: _MARK_ORDER_ON_TEST[it["mark"]])
    return by_row


def _other_split_by_row(split: str, truth_rows: Sequence[Dict[str, object]]) -> Dict[int, List[Dict[str, object]]]:
    by_row: Dict[int, List[Dict[str, object]]] = {}
    for it in _SPLIT_ITEM_FN[split](truth_rows):
        by_row.setdefault(it["row"], []).append(it)
    return by_row


def _ask_row(item: Dict[str, object], ts: int, truth_row: Dict[str, object], moment_id: str,
             render: Callable[[], Tuple[np.ndarray, List[Tuple[float, float]]]]) -> Dict[str, object]:
    """One `ask` tape row (payload + meta) for `item` on `moment_id`'s canvas. `render` is that canvas's
    shared getter (§ module docstring) — called only for `what`/`say` marks, and only when the payload is
    actually built (inside the lazy callable below, never eagerly)."""
    mark = item["mark"]
    if mark in POINT_MARKS:
        form, phrase, target = "point", list(item["phrase"]), None
    elif mark in WHAT_MARKS or mark in SAY_MARKS:
        form = "what" if mark in WHAT_MARKS else "say"
        phrase, target = [], int(item["target"])
    else:
        raise ValueError(f"creature.senses.scene: no ask form for mark {mark!r}")

    def build() -> bytes:
        if target is None:
            box, centroid = None, None
        else:
            t = truth_row["things"][target]
            box = [int(t["top"]), int(t["left"]), int(t["side"])]
            cy, cx = render()[1][target]
            centroid = [float(cy), float(cx)]
        payload = {"item": item["item_id"], "mark": mark, "form": form, "phrase": phrase, "box": box,
                   "centroid": centroid, "word": None, "test_seed": int(ts)}
        return _json_bytes(payload)

    meta = {"moment": moment_id, "source": "scene", "item": item["item_id"], "form": form}
    return {"sense": "ask", "meta": meta, "ext": "json", "payload": build}


def _scene_dict_with_centroids(scene: W.Scene, row: int, render: Callable[[], Tuple[np.ndarray, List[Tuple[float, float]]]]) -> Dict[str, object]:
    cents = render()[1]
    return {**scene.to_dict(), "row": row, "centroids": [[float(c[0]), float(c[1])] for c in cents]}


# ------------------------------------------------------------------------------------------------ the plan
def plan(cfg: Dict[str, object]) -> List[Dict[str, object]]:
    """`declared["WORLD_SCENE"]` (INTERFACE §1) -> the whole ordered list of moments. Pure: two calls with an
    equal `cfg` produce byte-identical payloads (once every `payload`/`truth` callable is invoked), metas and
    order — no `default_rng()`, no clock, no `hash()`, no set/dict order (INTERFACE §0.3). Never renders."""
    ws = int(cfg["seed"])
    if ws not in W.WORLD_SEEDS:
        raise ValueError(f"WORLD scene: seed {ws} is not a world seed (one of {W.WORLD_SEEDS}) — refused by name")
    n_train = int(cfg["train"])
    sets: List[str] = list(cfg["sitting"])
    utter = cfg["utterance"]

    perm = None
    if isinstance(utter, dict) and "shuffled" in utter:
        from brain.scene.run import null_perm   # imported lazily: this sense must not hard-depend on the arms/cache stack
        perm = null_perm(ws, int(utter["shuffled"]), n_train)

    moments: List[Dict[str, object]] = []
    train_scenes = [W.train_scene(ws, i) for i in range(n_train)]
    said_words: List[str] = []
    seen_words = set()
    for i, sc in enumerate(train_scenes):
        said = list(train_scenes[int(perm[i])].words) if perm is not None else list(sc.words)
        for w in said:
            _assert_word(w)
            if w not in seen_words:
                seen_words.add(w)
                said_words.append(w)
        moment_id = f"sc{ws}t{i:06d}"
        render = _memo_render(sc)
        rows = [{"sense": "ear", "meta": {"moment": moment_id, "source": "scene", "word": w, "scene": i}, "ext": "txt",
                 "payload": (lambda w=w: w.encode("utf-8"))} for w in said]
        rows.append({"sense": "eye", "meta": {"moment": moment_id, "source": "scene", "kind": "train", "scene": i,
                                              "world_seed": ws}, "ext": "png",
                     "payload": (lambda r=render: _png_bytes(r()[0]))})

        def _truth(sc=sc, i=i, said=said, r=render, ws=ws) -> Dict[str, object]:
            return {"kind": "train", "scene": i, "world_seed": ws,
                    "scene_dict": _scene_dict_with_centroids(sc, i, r), "said": said}
        moments.append({"moment": moment_id, "rows": rows, "truth": _truth, "phase": ("train",)})

    for set_name in sets:
        ts = int(W.TEST_SETS[set_name][ws])
        splits = _TEST_SPLITS + (_FRESH_EXTRA if set_name == "fresh" else ())

        begin_id = f"sc{ws}q-{set_name}-begin"
        moments.append({"moment": begin_id, "truth": None, "phase": ("sitting", set_name, "begin"), "rows": [
            {"sense": "ask", "meta": {"moment": begin_id, "source": "scene", "form": "begin"}, "ext": "json",
             "payload": (lambda sn=set_name, ts=ts: _json_bytes({"form": "begin", "set": sn, "test_seed": ts}))}]})

        for split in splits:
            scenes = W.scenes_for(split, ts)
            truth_rows = [{**sc2.to_dict(), "row": r} for r, sc2 in enumerate(scenes)]
            by_row = _test_split_by_row(truth_rows, ts, want_m5=(set_name == "fresh")) if split == "test" \
                else _other_split_by_row(split, truth_rows)
            for r, sc2 in enumerate(scenes):
                its = by_row.get(r, [])
                moment_id = f"sc{ws}q-{set_name}-{split}-{r:04d}"
                tr = truth_rows[r]
                render = _memo_render(sc2)
                rows = [_ask_row(it, ts, tr, moment_id, render) for it in its]
                rows.append({"sense": "eye", "meta": {"moment": moment_id, "source": "scene", "kind": "sitting",
                                                       "set": set_name, "split": split, "row": r}, "ext": "png",
                             "payload": (lambda rd=render: _png_bytes(rd()[0]))})

                def _truth(sc2=sc2, r=r, its=its, rd=render, set_name=set_name, split=split) -> Dict[str, object]:
                    return {"kind": "sitting", "set": set_name, "split": split, "row": r,
                            "scene_dict": _scene_dict_with_centroids(sc2, r, rd), "items": its}
                moments.append({"moment": moment_id, "rows": rows, "truth": _truth,
                                "phase": ("sitting", set_name, "split")})

        for w in sorted(said_words):
            why_id = f"sc{ws}q-{set_name}-why-{w}"
            moments.append({"moment": why_id, "truth": None, "phase": ("sitting", set_name, "why"), "rows": [
                {"sense": "ask", "meta": {"moment": why_id, "source": "scene", "item": f"M4:{w}", "form": "why"}, "ext": "json",
                 "payload": (lambda w=w: _json_bytes({"form": "why", "item": f"M4:{w}", "mark": "M4", "word": w}))}]})

        end_id = f"sc{ws}q-{set_name}-end"
        moments.append({"moment": end_id, "truth": None, "phase": ("sitting", set_name, "end"), "rows": [
            {"sense": "ask", "meta": {"moment": end_id, "source": "scene", "form": "end"}, "ext": "json",
             "payload": (lambda sn=set_name: _json_bytes({"form": "end", "set": sn}))}]})

    return moments


# ------------------------------------------------------------------------------------------------ progress (shared, in-process)
class Progress:
    """Thread-safe counters, shared between the sense thread and `creature/body.py:Body._build_status` via an
    EXTRA keyword `sense()` accepts beyond INTERFACE §5's declared signature (default None, so a direct call
    or test that omits it is unaffected). `creature/body.py` holds the same instance both places."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._published = 0
        self._train_done = False
        self._sitting_done: Dict[str, bool] = {}
        self._ended = False

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            return {"published_moments": self._published, "train_done": self._train_done,
                    "sitting_done": dict(self._sitting_done), "ended": self._ended}

    def mark(self, published: int, phase: Tuple, is_last: bool, n_train: int) -> None:
        with self._lock:
            self._published = published
            if phase == ("train",) and published >= n_train:
                self._train_done = True
            if phase[0] == "sitting" and phase[2] == "end":
                self._sitting_done[phase[1]] = True
            if is_last:
                self._ended = True


# ------------------------------------------------------------------------------------------------ the cursor (#230)
def _cursor_path(root: Path) -> Path:
    return Path(root) / "scene" / CURSOR_NAME


def _load_cursor(root: Path) -> int:
    p = _cursor_path(root)
    if not p.exists():
        return 0
    try:
        t = p.read_text().strip()
        return int(t) if t else 0
    except (OSError, ValueError):
        return 0


def _write_cursor(root: Path, n: int) -> None:
    p = _cursor_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(str(n))
    tmp.replace(p)


# ------------------------------------------------------------------------------------------------ the executor
def _publish_moment(publish: Callable, root: Path, m: Dict[str, object]) -> None:
    eye_row = None
    for row in m["rows"]:
        payload = row["payload"]()
        r = publish(row["sense"], payload, row["meta"], row["ext"])
        if row["sense"] == "eye":
            eye_row = r
    truth_fn = m["truth"]
    if truth_fn is not None:
        if eye_row is None:
            raise RuntimeError(f"creature.senses.scene: moment {m['moment']!r} carries truth but published no eye row")
        truth_obj = truth_fn()
        truth_dir = Path(root) / "truth" / "scene"
        truth_dir.mkdir(parents=True, exist_ok=True)
        (truth_dir / f"{int(eye_row['seq']):09d}.json").write_text(json.dumps(truth_obj, sort_keys=True))


def sense(publish: Callable, stop_event, root: Path, cfg: Dict[str, object], backlog: Callable[[], int],
          progress: Optional[Progress] = None) -> None:
    """The sense thread body (a `creature.body.SenseThread` runs it): publish `plan(cfg)` in order, honouring
    `feed`'s cadence (§5), resuming from `root/scene/SCENE-CURSOR` (#230) so a restart never republishes a
    moment already durable on the tape. After the last moment it publishes nothing more and waits for the
    stop event (INTERFACE §2's own words, for the `end` ask)."""
    moments = plan(cfg)
    n_train = int(cfg["train"])
    cursor = _load_cursor(root)
    if progress is not None and cursor:
        # a restart: recompute the counters from the moments already durable (phase scan only, no payload calls)
        for i in range(min(cursor, len(moments))):
            progress.mark(i + 1, moments[i]["phase"], i == len(moments) - 1, n_train)
    feed = cfg["feed"]
    mode = feed["mode"]
    for idx in range(cursor, len(moments)):
        if stop_event.is_set():
            return
        if mode == "max":
            k = int(feed["backlog"])
            while backlog() >= k:
                if stop_event.is_set():
                    return
                stop_event.wait(_WAIT_POLL_S)
                if stop_event.is_set():
                    return
        _publish_moment(publish, root, moments[idx])
        _write_cursor(root, idx + 1)
        if progress is not None:
            progress.mark(idx + 1, moments[idx]["phase"], idx == len(moments) - 1, n_train)
        if mode == "every":
            stop_event.wait(float(feed["ms"]) / 1000.0)
    while not stop_event.is_set():
        stop_event.wait(1.0)
