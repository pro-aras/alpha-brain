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

# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:50 +0400 — PREREG-S1B1 §1: world.py's bytes change, so check_code refuses
# S1a's caches; S1b-1's run root is FRESH and every cache is redrawn there; S1a's root is read (as plain files) only by the
# identity test and for S1a's numbers beside.
# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 15:59 +0400 — PREREG-S1B1R / AMENDMENT 1 §4 (c): world.py's bytes change again, so
# check_code refuses S1b-1's caches; this slice's run root is FRESH (RUNS) and every cache is redrawn there; S1b-1's root
# (S1B1_RUNS) is READ as plain files only (the identity test, S1b-1's report). Two TEST SETS per world seed share ONE
# training cache: S1b-1's own ("s1b1": 2026120x at S1b-1's relative paths) and the fresh one ("fresh": 2026140x under
# <root>/<ws>/fresh/, with SPEAK2).
# edit: Claude (Fable 5.1, the seat), 2026-09-28 20:49 +0400 — BRAIN-IN-BODY: the BRAIN / WORLD scene parser branches changed genome/machinery.py's
# bytes, so check_code refuses S1b-1R's caches (its own rule, as at every slice before). This tree's run root is FRESH
# (RUNS = scene-organ): every cache is redrawn there by THIS code and proven array-identical to the scored ones
# (tools/brain/diag/cache_identity.py); the scored record's plain files (keys, questions, arms, marks, the gate, the nulls) are
# COPIED into it. S1b-1R's own root (S1B1R_RUNS) is the RECORD: read as plain files only, never written.
# edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:24 +0400 — PREREG-BRAIN-IN-BODY AMENDMENT 1 §2 «the hidden cost»: F-M6 changes
# genome/machinery.py, brain/scene/world.py and this file (all WORLD_CODE), so check_code refuses every cache under scene-organ; this
# tree's run root is FRESH again (RUNS = scene-organ-fm6): every cache is redrawn there (cache-r, now with the «held» set) and the
# fresh and older sets' caches are proven array-identical to the scored ones (tools/brain/diag/cache_identity.py <this root>).
# edit: Claude (Fable 5.1, the seat), 2026-09-29 13:17 +0400 — PREREG-WORD-ROAD §5: the gene HEAR changes genome/machinery.py (the parser branch,
# Organism.moment's list form) and this file, both WORLD_CODE, so check_code refuses every cache under scene-organ-fm6; this
# tree's run root is FRESH again (RUNS = scene-organ-hear): every cache is redrawn there (cache-r) and proven array-identical
# to the scored ones and, for the «held» set, to F-M6's (tools/brain/diag/cache_identity.py <this root> <F-M6's root>). No eye
# or world line changed: the redraw is the pin's price, not a new world.
# edit: Claude (Fable 5.1, the seat), 2026-09-29 16:40 +0400 — PREREG-BRAIN-DRIVES §8 (14): the gene DRIVE changes genome/machinery.py (one parser branch)
# and this file, both WORLD_CODE, so check_code refuses every cache under scene-organ-hear; this tree's run root is FRESH again
# (RUNS = scene-organ-drive): every cache is redrawn there (cache-r) and proven array-identical to the HEAR root's
# (tools/brain/diag/cache_identity.py <this root> <the HEAR root>). No eye or world line changed: the pin's price, not a new
# world. World seed 20261104's training split is drawn there for the first time (the gate's never-used world).
RUNS = Path("/data/dev/brain-runs/scene-organ-drive")
HEAR_RUNS = Path("/data/dev/brain-runs/scene-organ-hear")     # the HEAR redraw (the pre-DRIVE code), read as plain files only
FM6_RUNS = Path("/data/dev/brain-runs/scene-organ-fm6")       # F-M6's redraw (the pre-HEAR code), read as plain files only
SCENE_ORGAN_RUNS = Path("/data/dev/brain-runs/scene-organ")   # rung 1's redraw (the pre-F-M6 code), read as plain files only
S1B1R_RUNS = Path("/data/dev/brain-runs/scene-s1b1r")
S1B1_RUNS = Path("/data/dev/brain-runs/scene-s1b1")
S1A_RUNS = Path("/data/dev/brain-runs/scene")
N_LOCATED = 4
TEST_SPLITS = ("test", "m2b", "m6", "m3", "speak", "decline")
FRESH_SPLITS = TEST_SPLITS + ("speak2",)
# edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:23 +0400 — PREREG-BRAIN-IN-BODY AMENDMENT 1 §2: the NEW test set «held» (test seeds
# 2026150x) draws every split as the fresh set does, SPEAK2 included, under <root>/<ws>/held/cache/<split>; its M6 holds 84.
_SET_SPLITS = {"s1b1": TEST_SPLITS, "fresh": FRESH_SPLITS, "held": FRESH_SPLITS}


class SceneCacheError(Exception):
    pass


def test_splits(tset: str = "s1b1") -> tuple:
    """The test splits of a test set: S1b-1's six; the fresh set's seven (SPEAK2 added)."""
    if tset not in _SET_SPLITS:
        raise SceneCacheError(f"no such test set: {tset!r}")
    return _SET_SPLITS[tset]


_REPO = Path(__file__).resolve().parents[2]
# the code that DRAWS a cache: a cache is read only by the same bytes of these files (check_code)
WORLD_CODE = ("brain/scene/world.py", "brain/scene/eye.py", "brain/scene/cache.py", "brain/world/seeds.py",
              "brain/world/build.py", "brain/world/organs.py", "brain/glance_cache.py", "genome/world.py", "genome/gaze.py",
              "genome/machinery.py", "genome/eye.py", "genome/retina_fast.py", "genome/ALPHA4.genome")


def code_shas() -> Dict[str, str]:
    return {rel: sha256_file(_REPO / rel) for rel in WORLD_CODE}


def check_code(d: Path) -> None:
    """Refuse a cache drawn by other bytes of the world / eye / cache code than the ones running now."""
    sh = json.loads((Path(d) / "scene_header.json").read_text())
    now = code_shas()
    bad = [k for k, v in sh.get("code", {}).items() if now.get(k) != v] + [k for k in now if k not in sh.get("code", {})]
    if bad:
        raise SceneCacheError(f"{d} was drawn by other code: {bad} — rebuild it (a cache is read only by its own code)")


def cache_dir(root: Path, world_seed: Optional[int], split: str, tset: str = "s1b1") -> Path:
    """<root>/<world seed>/cache/<split> for a world seed's train and S1b-1's test set; <root>/<world seed>/fresh/cache/<split>
    for the fresh test set (PREREG-S1B1R; the train cache is ONE per world seed, shared); <root>/toy/cache/<split>;
    <root>/stage/cache/stage."""
    if split in ("toy-train", "toy-test"):
        return Path(root) / "toy" / "cache" / split
    if split == "stage":
        return Path(root) / "stage" / "cache" / split
    if world_seed is None:
        raise SceneCacheError(f"split {split!r} needs a world seed")
    if split == "train" or tset == "s1b1":
        return Path(root) / str(world_seed) / "cache" / split
    test_splits(tset)
    return Path(root) / str(world_seed) / tset / "cache" / split


def split_seed(split: str, world_seed: Optional[int], tset: str = "s1b1") -> int:
    if split == "train":
        return int(world_seed)
    if split in test_splits(tset):
        return W.TEST_SETS[tset][int(world_seed)]
    if split in ("toy-train", "toy-test"):
        return W.TOY_SEED
    if split == "stage":
        return W.STAGE_SEED
    raise SceneCacheError(f"no such split in the {tset!r} test set: {split!r}")


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
          recheck_n: int = 10, log=None, tset: str = "s1b1") -> Dict[str, object]:
    """Render + glance every scene of (split, seed) once, write the cache, self-check `recheck_n` rows (fresh render +
    fresh glances must equal the cached bytes). Returns scene_header.json's dict. `tset` picks the test set's seed for a
    test split (PREREG-S1B1R: "s1b1" S1b-1's own, "fresh" the fresh one); it is recorded in the header."""
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise SceneCacheError(f"{out_dir} exists — a cache is written once (remove it by hand to rebuild)")
    seed = split_seed(split, world_seed, tset)
    scenes = W.scenes_for(split, seed, limit, tset=tset if split in test_splits(tset) else None)   # F-M6: the set's own size
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
          "limit": limit, "test_set": tset, "heldout": [list(p) for p in W.HELDOUT], "interpreter": versions, "code": code_shas(),
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
        check_code(self.dir)
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


def build_world_seed(root: Path, world_seed: int, log=None, tset: str = "s1b1") -> Dict[str, object]:
    """train (world seed) + the test set's splits (its test seed), each written once, then the disjointness record (beside
    the test set's caches: <root>/<ws>/cache/disjoint.json for S1b-1's set, <root>/<ws>/fresh/cache/disjoint.json for the
    fresh one — PREREG-S1B1R)."""
    out = {}
    splits = test_splits(tset)
    for split in ("train",) + splits:
        d = cache_dir(root, world_seed, split, tset)
        if d.exists():
            out[split] = json.loads((d / "scene_header.json").read_text())
            continue
        out[split] = build(split, world_seed, d, log=log, tset=tset)
        if log is not None:
            log(f"[cache {split} {world_seed} {tset}] written: {out[split]['rows']} rows")
    tr = ScenePercepts(cache_dir(root, world_seed, "train")).shas()
    rec = {"prereg_sha256": PREREG_SHA256, "world_seed": world_seed, "test_set": tset,
           "test_seed": W.TEST_SETS[tset][int(world_seed)], "train_canvases": len(tr), "checked": {}}
    for split in splits:
        rec["checked"][split] = assert_disjoint(tr, ScenePercepts(cache_dir(root, world_seed, split, tset)).shas())
    # edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:23 +0400 — AMENDMENT 1 §2: the «held» set's canvases are also checked against the
    # OLDER sets' canvases of the same root (every split of «s1b1» and «fresh» whose cache is present; the ones read are recorded)
    if tset == "held":
        old = []
        rec["checked_vs_old"] = {}
        for ot in ("s1b1", "fresh"):
            for split in test_splits(ot):
                d = cache_dir(root, world_seed, split, ot)
                if (d / "scene_header.json").exists():
                    old.extend(json.loads(l)["canvas_png_sha256"] for l in (d / "index.jsonl").read_text().splitlines() if l.strip())
                    rec["checked_vs_old"][f"{ot}/{split}"] = True
        for split in splits:
            assert_disjoint(old, ScenePercepts(cache_dir(root, world_seed, split, tset)).shas())
        rec["old_canvases"] = len(old)
    rec["overlap"] = 0
    (cache_dir(root, world_seed, splits[0], tset).parent / "disjoint.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    return rec


# ------------------------------------------------------------------------------------------------ identity with S1a
SPEC_KEYS = ("item_id", "split", "index", "seed", "things", "words", "referent", "template", "centroids", "fix", "fix_thing")


def _jsonl(p: Path) -> List[Dict[str, object]]:
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def identity_with(d_new: Path, d_old: Path) -> Dict[str, object]:
    """PREREG-S1B1 §1 (a): a redrawn cache carries the SAME scene specs and the SAME canvas shas as S1a's — read from
    S1a's OWN files (index.jsonl, truth.jsonl, header.json) as plain JSON, never through ScenePercepts (whose
    check_code refuses S1a's world bytes by design) and never assumed. The glances' npy sha is compared too (identical
    canvases through an identical eye must give identical glances)."""
    old_i, new_i = _jsonl(Path(d_old) / "index.jsonl"), _jsonl(Path(d_new) / "index.jsonl")
    old_t, new_t = _jsonl(Path(d_old) / "truth.jsonl"), _jsonl(Path(d_new) / "truth.jsonl")
    ho = json.loads((Path(d_old) / "header.json").read_text())
    hn = json.loads((Path(d_new) / "header.json").read_text())
    sha_diff = [k for k, (a, b) in enumerate(zip(old_i, new_i)) if a["canvas_png_sha256"] != b["canvas_png_sha256"]
                or a["item_id"] != b["item_id"]]
    spec_diff = [k for k, (a, b) in enumerate(zip(old_t, new_t)) if any(a.get(key) != b.get(key) for key in SPEC_KEYS)]
    return {"rows_old": len(old_i), "rows_new": len(new_i), "canvas_sha_diff": len(sha_diff), "spec_diff": len(spec_diff),
            "npy_equal": ho.get("npy_sha256") == hn.get("npy_sha256"),
            "same": (len(old_i) == len(new_i) and len(old_t) == len(new_t) and not sha_diff and not spec_diff
                     and ho.get("npy_sha256") == hn.get("npy_sha256"))}
