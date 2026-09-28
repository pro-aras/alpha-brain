"""cache.py — the per-seed glance cache of S1a: written ONCE (under /usr/bin/python3), shared by every arm.

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:06 +0400 — new module (PREREG-R3-TONIGHT §S1a; brief step 2: «A per-seed glance
cache is written once and shared by every arm»).

Storage reuses brain.glance_cache (never re-typed): `CacheWriter` / `Cache` hold the (N, 5, 144) glances, index.jsonl
(item_id, canvas_png_sha256 — script "scene-s1a", variant = the split) and header.json (genome sha, the four organ pins,
the interpreter). Beside them, in the same directory:
  percept.npz        fix (N, 4, 2) int16 (−1 padded) and n_fix (N,) — the located fixation cells (the learner may read)
  forced.npz         ORACLE-TRUTH's one window per thing: feats (M, 144), scene_row (M,), thing (M,), centroid (M, 2)
  hear.jsonl         the parent's words per scene (what the learner hears; () at test)
  truth.jsonl        GRADING AND ORACLE FEEDS ONLY: the scene spec (things, boxes, referent, template), the centroids,
                     and each fixation's thing (world.fixation_thing). No learner module reads it (test_truth_fence.py).
  scene_header.json  the PREREG sha, the split, the seeds, the held-outs, every file's sha256, the self-check.
A directory is built under `<dir>.building` and renamed into place only when complete, so a reader never opens a half cache.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np
import PIL
import scipy

from genome import gaze as G

from brain.glance_cache import Cache, CacheWriter, sha256_file
from brain.world import organs
from brain.world.seeds import substream

from . import PREREG_SHA256, eye
from . import world as W

RUNS = Path("/data/dev/brain-runs/scene")
N_LOCATED = 4


class SceneCacheError(Exception):
    pass


def cache_dir(root: Path, world_seed: Optional[int], split: str) -> Path:
    """<root>/<world seed>/cache/<split> for a world seed's train/test/m2b/m6; <root>/toy/cache/<split>; <root>/stage/cache/stage."""
    if split in ("toy-train", "toy-test"):
        return Path(root) / "toy" / "cache" / split
    if split == "stage":
        return Path(root) / "stage" / "cache" / split
    if world_seed is None:
        raise SceneCacheError(f"split {split!r} needs a world seed")
    return Path(root) / str(world_seed) / "cache" / split


def split_seed(split: str, world_seed: Optional[int]) -> int:
    if split == "train":
        return int(world_seed)
    if split in ("test", "m2b", "m6"):
        return W.TEST_SEEDS[int(world_seed)]
    if split in ("toy-train", "toy-test"):
        return W.TOY_SEED
    if split == "stage":
        return W.STAGE_SEED
    raise SceneCacheError(f"no such split: {split!r}")


def _versions() -> Dict[str, str]:
    return {"executable": sys.executable, "python": sys.version.split()[0], "numpy": np.__version__,
            "scipy": scipy.__version__, "PIL": PIL.__version__}


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _scene_percepts(scene: W.Scene, spec, gcfg, colour):
    rgb, cents = W.render_scene(scene)
    sha, feats, fix = eye.look(rgb, spec, gcfg, colour)
    an = G._analyse_frame(rgb)
    grey = G.luminance(rgb)
    forced = [eye.forced_glance(rgb, c, spec, gcfg, colour, an=an, grey=grey) for c in cents]
    return rgb, cents, sha, feats, fix, forced


def build(split: str, world_seed: Optional[int], out_dir: Path, limit: Optional[int] = None,
          recheck_n: int = 10, log=None) -> Dict[str, object]:
    """Render + glance every scene of (split, seed) once, write the cache, self-check `recheck_n` rows (fresh render +
    fresh glances must equal the cached bytes). Returns scene_header.json's dict."""
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise SceneCacheError(f"{out_dir} exists — a cache is written once (remove it by hand to rebuild)")
    seed = split_seed(split, world_seed)
    scenes = W.scenes_for(split, seed)
    if limit is not None:
        scenes = scenes[:limit]
    tmp = out_dir.with_name(out_dir.name + ".building")
    if tmp.exists():
        shutil.rmtree(tmp)
    spec, gcfg, colour = eye.eye_config()
    pins = organs.organ_pins()
    writer = CacheWriter(tmp)
    n = len(scenes)
    fix_arr = np.full((n, N_LOCATED, 2), -1, dtype=np.int16)
    n_fix = np.zeros(n, dtype=np.int8)
    f_feats: List[np.ndarray] = []
    f_row: List[int] = []
    f_thing: List[int] = []
    f_cent: List[List[float]] = []
    hear, truth = [], []
    for i, s in enumerate(scenes):
        rgb, cents, sha, feats, fix, forced = _scene_percepts(s, spec, gcfg, colour)
        row = writer.add(item_id=s.item_id, script="scene-s1a", char="", font="", variant=split, seed=seed,
                         canvas_png_sha256=sha, feats=eye.glance_row(feats, len(fix)))
        assert row == i
        fix_arr[row, :len(fix)] = np.asarray(fix, dtype=np.int16).reshape(-1, 2)
        n_fix[row] = len(fix)
        for k, (c, v) in enumerate(zip(cents, forced)):
            f_feats.append(v); f_row.append(row); f_thing.append(k); f_cent.append([c[0], c[1]])
        hear.append({"row": row, "item_id": s.item_id, "words": list(s.words)})
        t = s.to_dict()
        t.update({"row": row, "centroids": [[c[0], c[1]] for c in cents],
                  "fix": [[y, x] for y, x in fix], "fix_thing": [W.fixation_thing(c, s.things) for c in fix]})
        truth.append(t)
        if log is not None and (i + 1) % 1000 == 0:
            log(f"[cache {split} {seed}] {i + 1}/{n}")
    versions = _versions()
    header = writer.finalize(seed=seed, genome_sha=organs.genome_sha(), organ_pins=pins, interpreter=versions,
                             library_versions=versions)
    np.savez(tmp / "percept.npz", fix=fix_arr, n_fix=n_fix)
    np.savez(tmp / "forced.npz", feats=np.asarray(f_feats, dtype=np.float64).reshape(-1, eye.FEATS),
             scene_row=np.asarray(f_row, dtype=np.int32), thing=np.asarray(f_thing, dtype=np.int8),
             centroid=np.asarray(f_cent, dtype=np.float64).reshape(-1, 2))
    with (tmp / "hear.jsonl").open("w", encoding="utf-8") as f:
        for r in hear:
            f.write(_canonical(r) + "\n")
    with (tmp / "truth.jsonl").open("w", encoding="utf-8") as f:
        for r in truth:
            f.write(_canonical(r) + "\n")
    checked = _self_check(scenes, tmp, seed, split, recheck_n, spec, gcfg, colour)
    sh = {"prereg_sha256": PREREG_SHA256, "split": split, "seed": seed, "world_seed": world_seed, "rows": n,
          "limit": limit, "heldout": [list(p) for p in W.HELDOUT], "interpreter": versions,
          "glance_header": header, "self_check_rows": checked,
          "files": {p.name: sha256_file(p) for p in sorted(tmp.iterdir()) if p.is_file()}}
    (tmp / "scene_header.json").write_text(json.dumps(sh, sort_keys=True, indent=2) + "\n")
    tmp.rename(out_dir)
    return sh


def _self_check(scenes: Sequence[W.Scene], d: Path, seed: int, split: str, n: int, spec, gcfg, colour) -> List[int]:
    """Brain/world/build.py's own rule, extended to the sidecars: rows chosen by the seed are re-rendered and re-glanced
    FRESH and must equal the cached glances, fixations and forced windows byte for byte."""
    rng = substream(seed, f"scene_cache_self_check:{split}")
    n = min(n, len(scenes))
    rows = sorted(int(r) for r in rng.choice(len(scenes), size=n, replace=False))
    c = Cache(d)
    pc = np.load(d / "percept.npz")
    fc = np.load(d / "forced.npz")
    for r in rows:
        _rgb, _cents, sha, feats, fix, forced = _scene_percepts(scenes[r], spec, gcfg, colour)
        if sha != c.meta(r)["canvas_png_sha256"]:
            raise SceneCacheError(f"self-check: row {r} canvas sha differs")
        if not np.array_equal(eye.glance_row(feats, len(fix)), c.glances(r)):
            raise SceneCacheError(f"self-check: row {r} glances differ")
        if int(pc["n_fix"][r]) != len(fix) or [tuple(int(v) for v in x) for x in pc["fix"][r][:len(fix)]] != fix:
            raise SceneCacheError(f"self-check: row {r} fixations differ")
        got = fc["feats"][fc["scene_row"] == r]
        if got.shape[0] != len(forced) or not np.array_equal(got, np.asarray(forced)):
            raise SceneCacheError(f"self-check: row {r} forced windows differ")
    return rows


# ------------------------------------------------------------------------------------------------ readers
class ScenePercepts:
    """What a learner may read: the glances, the fixation cells, the forced windows (ORACLE-TRUTH's arm only) and what
    the parent said. Never the truth."""

    def __init__(self, d: Path):
        self.dir = Path(d)
        self.glances = Cache(self.dir)
        pc = np.load(self.dir / "percept.npz")
        self.fix = np.asarray(pc["fix"])
        self.n_fix = np.asarray(pc["n_fix"])
        fc = np.load(self.dir / "forced.npz")
        self.forced_feats = np.asarray(fc["feats"])
        self.forced_row = np.asarray(fc["scene_row"])
        self.forced_thing = np.asarray(fc["thing"])
        self.forced_centroid = np.asarray(fc["centroid"])
        self.hear = [json.loads(l) for l in (self.dir / "hear.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        self.header = json.loads((self.dir / "scene_header.json").read_text())
        if len(self.hear) != len(self.glances) or self.fix.shape[0] != len(self.glances):
            raise SceneCacheError(f"{self.dir}: sidecars disagree with the glance cache on the row count")
        starts = np.searchsorted(self.forced_row, np.arange(len(self.glances) + 1))
        self._forced_slices = [(int(starts[i]), int(starts[i + 1])) for i in range(len(self.glances))]

    def __len__(self) -> int:
        return len(self.glances)

    def located(self, row: int):
        """(fixation cells [(y, x)] × k, located glances (k, 144))."""
        k = int(self.n_fix[row])
        g = self.glances.glances(row)
        return [(int(y), int(x)) for y, x in self.fix[row][:k]], g[:k]

    def hypotheses(self, row: int) -> List[eye.Hypothesis]:
        fix, loc = self.located(row)
        return eye.hypotheses(fix, loc)

    def forced(self, row: int) -> np.ndarray:
        a, b = self._forced_slices[row]
        return self.forced_feats[a:b]

    def forced_positions(self, row: int) -> np.ndarray:
        """The forced windows' centroids in grid-cell units (y, x) = centroid px / 8 − 0.5 (a cell's centre maps to its
        own index, as a fixation's cell does)."""
        a, b = self._forced_slices[row]
        return self.forced_centroid[a:b] / 8.0 - 0.5

    def words(self, row: int) -> List[str]:
        return list(self.hear[row]["words"])

    def shas(self) -> List[str]:
        return [self.glances.meta(i)["canvas_png_sha256"] for i in range(len(self.glances))]


def load_truth(d: Path) -> List[Dict[str, object]]:
    """GRADING AND ORACLE FEEDS ONLY (marks.py, run.py)."""
    return [json.loads(l) for l in (Path(d) / "truth.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def assert_disjoint(train_shas: Iterable[str], test_shas: Iterable[str]) -> int:
    """No test canvas's sha appears in training. Returns the number of test canvases checked; raises on any overlap."""
    seen = set(train_shas)
    k = 0
    bad = []
    for s in test_shas:
        k += 1
        if s in seen:
            bad.append(s)
    if bad:
        raise SceneCacheError(f"{len(bad)} test canvas(es) byte-identical to a training canvas, e.g. {bad[0][:16]}…")
    return k


def build_world_seed(root: Path, world_seed: int, log=None) -> Dict[str, object]:
    """train (world seed) + test, m2b, m6 (its test seed), each written once, then the disjointness record."""
    out = {}
    for split in ("train", "test", "m2b", "m6"):
        d = cache_dir(root, world_seed, split)
        if d.exists():
            out[split] = json.loads((d / "scene_header.json").read_text())
            continue
        out[split] = build(split, world_seed, d, log=log)
        if log is not None:
            log(f"[cache {split} {world_seed}] written: {out[split]['rows']} rows")
    tr = ScenePercepts(cache_dir(root, world_seed, "train")).shas()
    rec = {"prereg_sha256": PREREG_SHA256, "world_seed": world_seed, "train_canvases": len(tr), "checked": {}}
    for split in ("test", "m2b", "m6"):
        rec["checked"][split] = assert_disjoint(tr, ScenePercepts(cache_dir(root, world_seed, split)).shas())
    rec["overlap"] = 0
    (Path(root) / str(world_seed) / "cache" / "disjoint.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    return rec
