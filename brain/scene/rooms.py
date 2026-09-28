"""rooms.py — S1c «THE NOISY ROOM»: the six ROOMS carved from S1's world, their pools and windows, and their glance caches.
WORLD side (it imports world.py and the cache's writer; no learner module imports it — tests/brain/scene/test_truth_fence.py).

edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:01 +0400 — new module, written to docs/brain/r3/PREREG-S1C.md (genome-wt-brain3 9ef2583,
sha a552515a…) §1 and its AMENDMENT 1 §1–§2 (PREREG-S1C-AMEND-1.md, 1eba85d, sha 825f4ad8…). Every number is the PREREG's;
the one-line READINGS it leaves open are marked «declared» and listed in docs/brain/r3/S1C-HANDBACK.md.

  R1 {circle, square} · R2 {triangle, cross} · R3 {ring, star} — S1's training generator restricted to the room's two shapes
     (the pair uniform over the room's ALLOWED pairs, the size uniform — S1's _trained_attrs, restricted), 1 / 2 / 3 things
     in S1's mix, the parent TRUE (S1's _parent: a thing uniformly, a template uniformly).
  N  the noisy TV: S1's full generator for the SCENE; the utterance a template uniform over T1–T4 with every slot's word
     uniform over that type's trained words, drawn from the scene's own substream AFTER the things (declared), independent
     of them; no referent.
  K  the KNOWN room: ONE spec — a big red star, box top 48 / left 48, «red star» (T2) — re-rendered per visit under the
     visit's own item_id (AMENDMENT 1 §2); its window is ONE render. (A fact the amendment records: (star, red) is one of
     S1's held-out pairs.)
  U  structured but UNLEARNABLE by a linear word unit: S1's full generator; the parent says ONE true word of a referent
     chosen uniformly (declared: S1's _parent's first draw) — its colour word iff [shape ∈ {circle, triangle, ring}] XOR
     [size = big], else its shape word.
Pools per S1c seed: every room 2,000 VISIT scenes (AMENDMENT 1 §1; `room:<r>:visit:<i>`), 40 WINDOW scenes for R1–R3, N, U
(`room:<r>:window:<i>`), ONE for K. A scene is a function of (seed, room, kind, i) alone; an index outside its pool RAISES
— a pool is never wrapped.

The caches: one per (seed, room, kind), under <root>/<seed>/rooms/<room>-<kind>, through S1a's own road (cache.py's
render + look + CacheWriter), with two declared differences: no forced windows are drawn (no S1c arm reads ORACLE-TRUTH's
feed — forced.npz is written EMPTY so cache.ScenePercepts reads the directory unchanged), and the scene header carries this
module's sha under its own key `room_code` (cache.check_code compares the header's `code` key for key with cache.py's
WORLD_CODE, so rooms.py's sha cannot sit there); RoomPercepts refuses a cache drawn by other bytes of rooms.py.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.glance_cache import Cache, CacheWriter, sha256_file
from brain.world import organs
from brain.world.seeds import substream

from . import cache as C
from . import eye
from . import world as W

# ------------------------------------------------------------------------------------------------ the PREREG's numbers
ROOMS: Tuple[str, ...] = ("R1", "R2", "R3", "N", "K", "U")        # also the round-robin's order (blocks 1–6)
ROOM_SHAPES: Dict[str, Tuple[str, str]] = {"R1": ("circle", "square"), "R2": ("triangle", "cross"), "R3": ("ring", "star")}
U_COLOUR_SHAPES: Tuple[str, ...] = ("circle", "triangle", "ring")
K_THING = W.Thing("star", "red", "big", 48, 48)
K_WORDS: Tuple[str, ...] = ("red", "star")                          # T2 of K_THING
N_VISIT = 2_000                                                     # AMENDMENT 1 §1 (the draft's 1,000 could run out)
N_WINDOW = 40
K_WINDOW = 1
S1C_SEEDS: Tuple[int, ...] = (20261301, 20261302, 20261303)
VOCAB13: Tuple[str, ...] = W.SIZE_NAMES + W.COLOUR_NAMES + W.SHAPES   # the FIXED 13-word vocabulary (§2's loss)
SLOT_TYPES: Dict[str, Tuple[str, ...]] = {"T1": ("shape",), "T2": ("colour", "shape"), "T3": ("size", "shape"),
                                          "T4": ("size", "colour", "shape")}
_TYPE_WORDS: Dict[str, Tuple[str, ...]] = {"shape": W.SHAPES, "colour": W.COLOUR_NAMES, "size": W.SIZE_NAMES}
KINDS: Tuple[str, ...] = ("visit", "window")


class RoomError(Exception):
    pass


def pool_size(room: str, kind: str) -> int:
    if room not in ROOMS:
        raise RoomError(f"no such room: {room!r}")
    if kind == "visit":
        return N_VISIT
    if kind == "window":
        return K_WINDOW if room == "K" else N_WINDOW
    raise RoomError(f"no such pool kind: {kind!r}")


def _room_attrs(room: str, rng: np.random.Generator) -> Tuple[str, str, str]:
    """S1's _trained_attrs restricted to the room's two shapes: the pair uniform over the room's ALLOWED pairs, then the
    size uniform over big / small (the same two draws in the same order)."""
    pairs = [p for p in W.ALLOWED if p[0] in ROOM_SHAPES[room]]
    s, c = pairs[int(rng.integers(len(pairs)))]
    return s, c, W.SIZE_NAMES[int(rng.integers(len(W.SIZE_NAMES)))]


def room_scene(seed: int, room: str, kind: str, index: int) -> W.Scene:
    """The index-th VISIT or WINDOW scene of `room` under S1c seed `seed` (0-based), from substream
    `room:<room>:<kind>:<index>` of the seed. Raises outside the pool."""
    n = pool_size(room, kind)
    if not 0 <= int(index) < n:
        raise RoomError(f"room {room} {kind} index {index} is outside its pool of {n} — a pool is never wrapped")
    index = int(index)
    split = f"room:{room}:{kind}"
    if room == "K":
        return W.Scene(split, index, seed, (K_THING,), K_WORDS, 0, "T2")
    rng = substream(seed, f"room:{room}:{kind}:{index}")
    k = W._n_things(rng)
    if room in ROOM_SHAPES:
        things = W._place([_room_attrs(room, rng) for _ in range(k)], rng)
        words, ref, tpl = W._parent(things, rng)
        return W.Scene(split, index, seed, things, words, ref, tpl)
    things = W._place([W._trained_attrs(rng) for _ in range(k)], rng)
    if room == "N":
        tpl = W.TEMPLATES[int(rng.integers(len(W.TEMPLATES)))]
        words = tuple(_TYPE_WORDS[t][int(rng.integers(len(_TYPE_WORDS[t])))] for t in SLOT_TYPES[tpl])
        return W.Scene(split, index, seed, things, words, None, tpl)
    # U
    ref = int(rng.integers(len(things)))
    t = things[ref]
    colour = (t.shape in U_COLOUR_SHAPES) != (t.size == "big")
    return W.Scene(split, index, seed, things, (t.colour if colour else t.shape,), ref, "U")


def room_scenes(seed: int, room: str, kind: str, limit: Optional[int] = None) -> List[W.Scene]:
    n = pool_size(room, kind) if limit is None else min(int(limit), pool_size(room, kind))
    return [room_scene(seed, room, kind, i) for i in range(n)]


# ------------------------------------------------------------------------------------------------ the caches
def rooms_code_sha() -> str:
    return sha256_file(Path(__file__).resolve())


def room_cache_dir(root: Path, seed: int, room: str, kind: str) -> Path:
    return Path(root) / str(seed) / "rooms" / f"{room}-{kind}"


def _percepts(scene: W.Scene, spec, gcfg, colour):
    """cache._scene_percepts without the forced windows (declared: no S1c arm reads them)."""
    rgb, cents = W.render_scene(scene)
    sha, feats, fix = eye.look(rgb, spec, gcfg, colour)
    return rgb, cents, sha, feats, fix


def build_room_cache(root: Path, seed: int, room: str, kind: str, limit: Optional[int] = None, recheck_n: int = 10,
                     prereg: Optional[Dict[str, str]] = None, log=None) -> Dict[str, object]:
    """Render + glance every scene of one pool ONCE (cache.build's road, scenes from room_scene), self-check `recheck_n`
    rows fresh, write under `<dir>.building` and rename into place when complete. Returns the scene header."""
    out_dir = room_cache_dir(root, seed, room, kind)
    if out_dir.exists():
        raise RoomError(f"{out_dir} exists — a cache is written once (remove it by hand to rebuild)")
    scenes = room_scenes(seed, room, kind, limit)
    tmp = out_dir.with_name(out_dir.name + ".building")
    if tmp.exists():
        shutil.rmtree(tmp)
    spec, gcfg, colour = eye.eye_config()
    pins = organs.organ_pins()
    writer = CacheWriter(tmp)
    n = len(scenes)
    fix_arr = np.full((n, C.N_LOCATED, 2), -1, dtype=np.int16)
    n_fix = np.zeros(n, dtype=np.int8)
    hear, truth = [], []
    split = f"room:{room}:{kind}"
    for i, s in enumerate(scenes):
        _rgb, cents, sha, feats, fix = _percepts(s, spec, gcfg, colour)
        row = writer.add(item_id=s.item_id, script="scene-s1c", char="", font="", variant=split, seed=seed,
                         canvas_png_sha256=sha, feats=eye.glance_row(feats, len(fix)))
        assert row == i
        fix_arr[row, :len(fix)] = np.asarray(fix, dtype=np.int16).reshape(-1, 2)
        n_fix[row] = len(fix)
        hear.append({"row": row, "item_id": s.item_id, "words": list(s.words)})
        t = s.to_dict()
        t.update({"row": row, "centroids": [[c[0], c[1]] for c in cents], "fix": [[y, x] for y, x in fix],
                  "fix_thing": [W.fixation_thing(c, s.things) for c in fix]})
        truth.append(t)
        if log is not None and (i + 1) % 500 == 0:
            log(f"[rooms {seed} {room}-{kind}] {i + 1}/{n}")
    versions = C._versions()
    header = writer.finalize(seed=seed, genome_sha=organs.genome_sha(), organ_pins=pins, interpreter=versions,
                             library_versions=versions)
    np.savez(tmp / "percept.npz", fix=fix_arr, n_fix=n_fix)
    np.savez(tmp / "forced.npz", feats=np.zeros((0, eye.FEATS)), scene_row=np.zeros(0, dtype=np.int32),
             thing=np.zeros(0, dtype=np.int8), centroid=np.zeros((0, 2)))
    with (tmp / "hear.jsonl").open("w", encoding="utf-8") as f:
        for r in hear:
            f.write(C._canonical(r) + "\n")
    with (tmp / "truth.jsonl").open("w", encoding="utf-8") as f:
        for r in truth:
            f.write(C._canonical(r) + "\n")
    checked = _self_check(scenes, tmp, seed, split, recheck_n, spec, gcfg, colour)
    sh = {"prereg": dict(prereg or {}), "split": split, "room": room, "kind": kind, "seed": seed, "rows": n,
          "limit": limit, "heldout": [list(p) for p in W.HELDOUT], "interpreter": versions, "code": C.code_shas(),
          "room_code": rooms_code_sha(), "glance_header": header, "self_check_rows": checked, "forced_windows": False,
          "files": {p.name: sha256_file(p) for p in sorted(tmp.iterdir()) if p.is_file()}}
    (tmp / "scene_header.json").write_text(json.dumps(sh, sort_keys=True, indent=2) + "\n")
    tmp.rename(out_dir)
    return sh


def _self_check(scenes: Sequence[W.Scene], d: Path, seed: int, split: str, n: int, spec, gcfg, colour) -> List[int]:
    """cache._self_check's rule without the forced windows: rows chosen by the seed are re-rendered and re-glanced FRESH
    and must equal the cached canvas sha, glances and fixations byte for byte."""
    rng = substream(seed, f"scene_cache_self_check:{split}")
    n = min(n, len(scenes))
    rows = sorted(int(r) for r in rng.choice(len(scenes), size=n, replace=False))
    c = Cache(d)
    pc = np.load(d / "percept.npz")
    for r in rows:
        _rgb, _cents, sha, feats, fix = _percepts(scenes[r], spec, gcfg, colour)
        if sha != c.meta(r)["canvas_png_sha256"]:
            raise RoomError(f"self-check: row {r} canvas sha differs")
        if not np.array_equal(eye.glance_row(feats, len(fix)), c.glances(r)):
            raise RoomError(f"self-check: row {r} glances differ")
        if int(pc["n_fix"][r]) != len(fix) or [tuple(int(v) for v in x) for x in pc["fix"][r][:len(fix)]] != fix:
            raise RoomError(f"self-check: row {r} fixations differ")
    return rows


def build_seed(root: Path, seed: int, prereg: Optional[Dict[str, str]] = None, log=None) -> Dict[str, object]:
    """Every pool of one seed (each written once; an existing cache is kept and its header returned)."""
    out: Dict[str, object] = {}
    for room in ROOMS:
        for kind in KINDS:
            d = room_cache_dir(root, seed, room, kind)
            if d.exists():
                out[f"{room}-{kind}"] = json.loads((d / "scene_header.json").read_text())
                continue
            out[f"{room}-{kind}"] = build_room_cache(root, seed, room, kind, prereg=prereg, log=log)
            if log is not None:
                log(f"[rooms {seed} {room}-{kind}] written: {out[f'{room}-{kind}']['rows']} rows")
    return out


class RoomPercepts(C.ScenePercepts):
    """cache.ScenePercepts (the glances, the fixations, what the parent said — never the truth) + the room code's check."""

    def __init__(self, d: Path):
        super().__init__(d)
        got = self.header.get("room_code")
        if got != rooms_code_sha():
            raise RoomError(f"{d} was drawn by other bytes of rooms.py ({str(got)[:12]}…) — rebuild it")


def load_room_truth(d: Path) -> List[Dict[str, object]]:
    """GRADING AND RECORD ONLY (run_s1c.py): the room scene specs."""
    return C.load_truth(d)
