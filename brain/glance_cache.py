"""glance_cache.py — THE GLANCE CACHE's storage format, writer and reader (B1-PREREG.md §2.5 / §3.2).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:2x +0400 — shipped in the SAME commit as
brain/protocol.py (the advisor's review before any code landed: an ASK/TEACH row's `operands`/`glance_row`
field is an INT into this cache, so the reader's shape has to exist before Builders 1 and 3 can write a
single line against the protocol — #235's "a widened vector is a chain", read forward this time: the
consumer's shape is fixed before the producers start).

WHAT THIS FILE DOES NOT DO: it does not render a single glyph or call `genome.gaze.glances` itself — that
is `brain/world/build_cache.py` (B1-PREREG.md §2's world builder, step 2 of this builder's own work order),
which runs ONLY under `/usr/bin/python3` (§3.0: the venv's numpy/scipy/PIL differ from the system
interpreter's, so rendering and glancing happen exactly once, in one place, under the interpreter the
PREREG names). This file is the STORAGE FORMAT both sides agree on: `CacheWriter` (append rows, `finalize`
writes the three files atomically and returns the header dict) and `Cache` (read-only, mmap'd, self-
verifying) — the same two classes a synthetic test cache and the real seed-20261001 cache are built and
read through, so a test that exercises `Cache` today already exercises the real reader every arm will use.

The three files, per seed, under `/data/dev/brain-runs/b1/cache/<seed>/` (§2.5):
  glances.npy   float64, shape (row_count, GLANCES_PER_ROW, FEATURES_PER_GLANCE) = (N, 5, 144).
  index.jsonl   one canonical-JSON row per cache row: {row, item_id, script, char, font, variant, seed,
                canvas_png_sha256} — `row` is redundant with the line's own position, kept explicit so a
                reader never has to trust file order alone (#171's class: an index a line's POSITION alone
                encodes is an index that silently breaks the moment a line is dropped or reordered).
  header.json   {seed, genome_sha, organ_pins: {...4 pins...}, interpreter: {...}, library_versions: {...},
                row_count, npy_sha256} — §2.5's own list, verbatim.

Read-only for every arm (§2.5's own law); only `brain/world/build_cache.py` ever constructs a `CacheWriter`.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Union

import numpy as np

GLANCES_PER_ROW = 5          # 4 located fixations + 1 coarse whole-canvas glance (§2.4's GAZE line: coarse 32)
FEATURES_PER_GLANCE = 144    # 112 tower + 32 colour (§2.5: "112 tower + 32 colour")


class CacheError(Exception):
    """Raised by `Cache` on any shape/hash mismatch — never silently truncated or padded."""


def sha256_file(path: Union[str, Path]) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class CacheWriter:
    """Accumulates rows in memory (B1's whole cache is "a few thousand canvases", §7 — small enough to hold
    as a Python list of (5,144) float64 arrays before one `np.stack`), then writes all three files
    atomically (tmp path + `Path.replace`, which is atomic on the same filesystem — never a partial file a
    concurrent reader could open mid-write)."""

    def __init__(self, out_dir: Union[str, Path]):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self._rows: List[np.ndarray] = []
        self._index: List[Dict[str, Any]] = []

    def add(self, *, item_id: str, script: str, char: str, font: str, variant: str, seed: int,
            canvas_png_sha256: str, feats: np.ndarray) -> int:
        """Append one row; returns its row number (assign this to the tape's `glance_row` / `candidate_rows`
        / operand `op_row(...)` values — the SAME int this cache will hand back from `.glances(row)`)."""
        feats = np.asarray(feats, dtype=np.float64)
        if feats.shape != (GLANCES_PER_ROW, FEATURES_PER_GLANCE):
            raise CacheError(f"feats must be shape {(GLANCES_PER_ROW, FEATURES_PER_GLANCE)}, got {feats.shape}")
        row = len(self._rows)
        self._rows.append(feats)
        self._index.append({"row": row, "item_id": str(item_id), "script": str(script), "char": str(char),
                             "font": str(font), "variant": str(variant), "seed": int(seed),
                             "canvas_png_sha256": str(canvas_png_sha256)})
        return row

    def __len__(self) -> int:
        return len(self._rows)

    def finalize(self, *, seed: int, genome_sha: str, organ_pins: Mapping[str, str],
                 interpreter: Mapping[str, Any], library_versions: Mapping[str, str]) -> Dict[str, Any]:
        """Write glances.npy, index.jsonl, header.json (in that order — the header's npy_sha256 must name
        bytes already on disk); returns the header dict written."""
        arr = (np.stack(self._rows, axis=0) if self._rows
               else np.zeros((0, GLANCES_PER_ROW, FEATURES_PER_GLANCE), dtype=np.float64))
        npy_path = self.out_dir / "glances.npy"
        tmp_npy = npy_path.with_name(npy_path.name + ".tmp")
        np.save(tmp_npy, arr)
        # np.save appends .npy if the name doesn't already end with it; tmp_npy already does, so the
        # written file is exactly tmp_npy's own name — asserted once here rather than discovered later.
        written = tmp_npy if tmp_npy.exists() else tmp_npy.with_suffix(tmp_npy.suffix + ".npy")
        written.replace(npy_path)
        npy_sha = sha256_file(npy_path)

        index_path = self.out_dir / "index.jsonl"
        tmp_idx = index_path.with_name(index_path.name + ".tmp")
        with tmp_idx.open("w", encoding="utf-8") as f:
            for row in self._index:
                f.write(_canonical(row) + "\n")
        tmp_idx.replace(index_path)

        header = {"seed": int(seed), "genome_sha": str(genome_sha), "organ_pins": dict(organ_pins),
                  "interpreter": dict(interpreter), "library_versions": dict(library_versions),
                  "row_count": len(self._rows), "npy_sha256": npy_sha}
        (self.out_dir / "header.json").write_text(json.dumps(header, sort_keys=True, indent=2) + "\n")
        return header


class Cache:
    """Read-only. `Cache(cache_dir)` opens `glances.npy` memory-mapped (the cache can run to a few thousand
    rows × 5 × 144 float64 — mmap keeps every arm's own process light regardless) and loads the index and
    header whole (both are small: one line and one dict per row)."""

    def __init__(self, cache_dir: Union[str, Path]):
        self.dir = Path(cache_dir)
        header_path, index_path, npy_path = self.dir / "header.json", self.dir / "index.jsonl", self.dir / "glances.npy"
        for p in (header_path, index_path, npy_path):
            if not p.exists():
                raise CacheError(f"glance cache at {self.dir} is missing {p.name}")
        self.header: Dict[str, Any] = json.loads(header_path.read_text())
        self.index: List[Dict[str, Any]] = [json.loads(line) for line in index_path.read_text().splitlines() if line.strip()]
        self._arr = np.load(npy_path, mmap_mode="r")
        if self._arr.ndim != 3 or self._arr.shape[1:] != (GLANCES_PER_ROW, FEATURES_PER_GLANCE):
            raise CacheError(f"glances.npy has shape {self._arr.shape}, expected (N, {GLANCES_PER_ROW}, {FEATURES_PER_GLANCE})")
        if self._arr.shape[0] != self.header.get("row_count"):
            raise CacheError(f"glances.npy has {self._arr.shape[0]} rows but header.json row_count={self.header.get('row_count')}")
        if len(self.index) != self.header.get("row_count"):
            raise CacheError(f"index.jsonl has {len(self.index)} rows but header.json row_count={self.header.get('row_count')}")
        for i, rec in enumerate(self.index):
            if rec.get("row") != i:
                raise CacheError(f"index.jsonl row {i} carries row={rec.get('row')!r} (position and label disagree)")

    def __len__(self) -> int:
        return int(self._arr.shape[0])

    def glances(self, row: int) -> np.ndarray:
        """The (5, 144) float64 feature array for cache row `row`. A copy (never the mmap view itself) —
        an arm is free to mutate what it gets back without corrupting the cache for the next reader."""
        if not (0 <= row < len(self)):
            raise CacheError(f"cache row {row} out of range [0, {len(self)})")
        return np.array(self._arr[row], dtype=np.float64, copy=True)

    def meta(self, row: int) -> Dict[str, Any]:
        if not (0 <= row < len(self)):
            raise CacheError(f"cache row {row} out of range [0, {len(self)})")
        return self.index[row]

    def verify(self) -> None:
        """Recompute glances.npy's own sha256 and compare to the header (§2.5's test: "a planted row
        changed by one byte must be caught by the header sha"). Reads the whole file — not cheap on a big
        cache, so callers run this once at stage −1 / at cache-build time, not on every arm's start-up."""
        got = sha256_file(self.dir / "glances.npy")
        want = self.header.get("npy_sha256")
        if got != want:
            raise CacheError(f"glances.npy sha256 mismatch: header says {want}, file hashes to {got}")
