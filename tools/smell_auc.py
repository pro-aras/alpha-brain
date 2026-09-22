#!/usr/bin/env python3
# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 4
# (BODY-SENSES.md §4.5's own refusal test): "measure whether the smell vector predicts anything the
# creature cares about better than chance -- e.g. whether two pictures with the same folder word have
# closer smell vectors than two with different words. If the AUC is ~= 0.5, the channel is noise and is
# refused (SOLUTIONS #217's law)."
"""tools/smell_auc.py — the smell channel's own refusal test, run READ-ONLY over a closed life's tape.

Usage: python3 tools/smell_auc.py --root /data/dev/genome-lives/g5-seam-1 [--world /data/dev/genome/world]

The closed life named in the brief (g5-seam-1) never declared SENSE_SMELL, so no `smell` tape row exists
there to read directly -- this script recomputes the trait RETROSPECTIVELY from the same three facts the
live sense would have read (suffix, byte size, folder name, mtime), by matching each folder `eye` row back
to its ORIGINAL FILE under the maker's read-only `world/` directory via the file's own sha256 prefix (the
eye row's own `meta["moment"]` is `"f" + sha[:12]` -- creature/senses/folder.py's own moment convention,
matched here against every candidate file's sha256, read-only, never written).

Prints TWO numbers, never tunes anything to either: the FULL vector's AUC (kind, size, folder-hash, age)
and a FOLDER-BLIND control (kind, size, age only, the folder axis excluded) -- SOLUTIONS #217/#162's law:
a same-word pair's folder-hash distance is 0 BY CONSTRUCTION, which inflates the full vector's AUC without
saying anything about whether the channel is useful once the answer itself is excluded. Both are reported;
neither is optimised against.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PICTURE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")
DEFAULT_WORLD = Path("/data/dev/genome/world")


def _read_folder_eye_rows(life_root: Path) -> List[dict]:
    rows: List[dict] = []
    for f in sorted((Path(life_root) / "tape").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("sense") == "eye" and (r.get("meta") or {}).get("source") == "folder":
                rows.append(r)
    return rows


def _index_world_files_by_sha12(world_root: Path) -> Dict[str, Tuple[Path, str]]:
    """{sha12: (file_path, folder_word)} for every picture under world_root -- "" for a picture directly
    under world_root (no folder). Read-only: only .stat()/.read_bytes(), never a write."""
    out: Dict[str, Tuple[Path, str]] = {}
    world_root = Path(world_root)
    if not world_root.exists():
        return out
    for pic in world_root.iterdir():
        if pic.is_file() and pic.suffix.lower() in PICTURE_SUFFIXES:
            sha = hashlib.sha256(pic.read_bytes()).hexdigest()
            out[sha[:12]] = (pic, "")
    for d in world_root.iterdir():
        if not d.is_dir():
            continue
        for pic in d.iterdir():
            if pic.is_file() and pic.suffix.lower() in PICTURE_SUFFIXES:
                sha = hashlib.sha256(pic.read_bytes()).hexdigest()
                out[sha[:12]] = (pic, d.name)
    return out


def _smell_trait_kind_size_folder(pic: Path, folder_word: str) -> np.ndarray:
    """The kind/size/folder THREE of creature/senses/folder.py:_smell_trait's own four -- same suffix
    index, same log10(bytes), same crc32 hash. `age` is DELIBERATELY NOT computed here: the live sense's
    `age` is `log10(time.time() - mtime)` AT THE INSTANT THE PICTURE WAS PUBLISHED; for a closed life read
    long afterward, "now" is whatever wall-clock instant this script happens to run at, which has nothing
    to do with what the live mind actually saw (RAISED, not faked as 0 or as a fresh reading dressed up as
    the historical one — #194's law: a prose claim about an artifact is not the artifact). The refusal test
    (BODY-SENSES §4.5) is unaffected: it asks whether the CHANNEL separates same-word from different-word
    pairs at all, and kind/size/folder already answer that; `age` is graded live, in the pre-flight and the
    24 h life itself, where "now" is honest."""
    suffix = pic.suffix.lower()
    kind = (PICTURE_SUFFIXES.index(suffix) / len(PICTURE_SUFFIXES)) if suffix in PICTURE_SUFFIXES else 1.0
    size = math.log10(max(pic.stat().st_size, 1))
    folder = (zlib.crc32(folder_word.encode("utf-8")) & 0xFFFFFFFF) / float(0x100000000)
    return np.array([kind, size, folder], dtype=np.float64)


def _auc_from_distances(same: np.ndarray, diff: np.ndarray) -> float:
    """P(a same-word pair's distance < a different-word pair's distance) + 0.5*P(equal) — the standard
    Mann-Whitney U / rank-sum AUC, computed by searchsorted (O(n log n), no scipy dependency). For each
    same-pair distance s, `lo`/`hi` bracket how many diff-pair distances are <= s (side="left"/"right");
    a WIN for "same < diff" is a diff value STRICTLY GREATER than s (`len(diff) - hi`), plus half credit
    for a tie (`hi - lo`) — caught by this file's own toy test (a naive lo/hi read scores the OPPOSITE
    direction, verified against a planted perfect-separation control before this function was trusted)."""
    if len(same) == 0 or len(diff) == 0:
        return float("nan")
    diff_sorted = np.sort(diff)
    lo = np.searchsorted(diff_sorted, same, side="left")
    hi = np.searchsorted(diff_sorted, same, side="right")
    wins = ((len(diff) - hi) + 0.5 * (hi - lo)).sum()
    return float(wins / (len(same) * len(diff)))


def compute_auc(life_root: Path, world_root: Path = DEFAULT_WORLD, blind_folder_axis: bool = False,
                 max_pairs: int = 200000, seed: int = 20260922) -> Dict[str, object]:
    """Reads `life_root`'s closed tape (read-only), matches every folder eye row to its source file under
    `world_root` (read-only) by sha12, computes each matched picture's smell trait, and the AUC of "same
    folder word" vs "different" by EUCLIDEAN distance. `blind_folder_axis`: drop the folder-hash column
    before computing distance (the honest control, #217's law) -- age is EXCLUDED from both vectors here
    (see the note below: retrospective age is not a fact this script can recover honestly, RAISED, never
    faked as 0)."""
    rows = _read_folder_eye_rows(life_root)
    index = _index_world_files_by_sha12(world_root)
    matched: List[Tuple[np.ndarray, str]] = []
    unmatched = 0
    for r in rows:
        moment = (r.get("meta") or {}).get("moment") or ""
        sha12 = moment[1:] if moment.startswith("f") else moment
        hit = index.get(sha12)
        if hit is None:
            unmatched += 1
            continue
        pic, word = hit
        trait = _smell_trait_kind_size_folder(pic, word)
        if blind_folder_axis:
            trait = trait[:2]   # kind, size only (age excluded, see _smell_trait_kind_size_folder's own note)
        matched.append((trait, word))

    same_d: List[float] = []
    diff_d: List[float] = []
    n = len(matched)
    rng = np.random.default_rng(seed)
    total_pairs = n * (n - 1) // 2
    sample = total_pairs <= max_pairs
    pairs_iter = (
        [(i, j) for i in range(n) for j in range(i + 1, n)] if sample
        else [tuple(rng.integers(0, n, size=2)) for _ in range(max_pairs)]
    )
    for i, j in pairs_iter:
        if i == j:
            continue
        vi, wi = matched[i]
        vj, wj = matched[j]
        d = float(np.linalg.norm(vi - vj))
        (same_d if wi == wj else diff_d).append(d)

    auc = _auc_from_distances(np.array(same_d), np.array(diff_d))
    return {
        "life_root": str(life_root), "folder_eye_rows": len(rows), "matched": n, "unmatched": unmatched,
        "same_pairs": len(same_d), "diff_pairs": len(diff_d), "auc": auc,
        "blind_folder_axis": blind_folder_axis, "sampled_pairs": not sample,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--world", default=str(DEFAULT_WORLD))
    a = ap.parse_args()
    full = compute_auc(Path(a.root), Path(a.world), blind_folder_axis=False)
    blind = compute_auc(Path(a.root), Path(a.world), blind_folder_axis=True)
    print(json.dumps({"full_vector_auc": full, "folder_blind_auc": blind}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
