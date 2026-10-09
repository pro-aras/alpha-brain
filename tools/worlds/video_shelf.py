# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-09 04:36 +0400 — PREREG-ALPHA-6 §2 B2 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…; test-first: tests/tools/test_video_shelf.py RED before this module existed).
"""tools/worlds/video_shelf.py — THE SHELF PROMOTION TOOL (PREREG-ALPHA-6 §2 B2).

The V3 bench tapes (docs/organism/whole/records/open-world-4/bench/tape-curriculum — read in place, never moved)
→ a life's video shelf dir: every file copied BYTE-EXACT, then the sha256 MANIFEST written over the copies
(creature/senses/video.py's own manifest form — the sense and this tool share ONE form, so a promoted shelf is
exactly what the sense streams), then the shelf verified whole before it is handed over. The shelf is FROZEN at
launch (additions between lives, never mid-life — replay honesty): the tool therefore REFUSES a non-empty
target by name, and its `verify` catches one flipped byte by name (the law's G-PLANT).

CLI:
  python3 -m tools.worlds.video_shelf promote --src BENCH_TAPE_DIR --shelf SHELF_DIR
  python3 -m tools.worlds.video_shelf verify --shelf SHELF_DIR
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List

from creature.senses import video as V


class ShelfPromotionError(Exception):
    """A promotion that would lie (a missing source, an occupied target) — refused by name."""


def _count_rows(shelf: Path) -> int:
    n = 0
    for day in sorted(Path(shelf).glob("*.jsonl")):
        n += sum(1 for line in day.read_text().splitlines() if line.strip())
    return n


def promote(src: Path, shelf: Path) -> Dict[str, object]:
    """src → shelf: byte-exact copies + the manifest + a whole-shelf verify. Returns the record dict."""
    src, shelf = Path(src), Path(shelf)
    if not src.is_dir():
        raise ShelfPromotionError(f"no such bench tape dir: {src}")
    if not list(src.glob("*.jsonl")):
        raise ShelfPromotionError(f"the source {src} carries no tape day file (*.jsonl)")
    if shelf.exists() and any(shelf.iterdir()):
        raise ShelfPromotionError(f"the shelf dir {shelf} is not empty — a frozen shelf is never overwritten "
                                  f"(PREREG-ALPHA-6 §1.2: additions between lives, never mid-life)")
    shelf.mkdir(parents=True, exist_ok=True)
    files: List[str] = []
    for p in sorted(src.rglob("*")):
        if p.is_file():
            rel = p.relative_to(src).as_posix()
            dest = shelf / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            files.append(rel)
    man = V.write_manifest(shelf)
    V.verify_shelf(shelf)                       # the tool's own check before it hands the shelf over (raises by name)
    rec = {"src": str(src), "shelf": str(shelf), "files": files, "n_files": len(files),
           "rows": _count_rows(shelf), "manifest": V.MANIFEST_NAME,
           "manifest_sha256": hashlib.sha256(man.read_bytes()).hexdigest(),
           "law": "PREREG-ALPHA-6 §1.2/§2 B2", "verify": "ok"}
    print(f"promoted {rec['n_files']} files ({rec['rows']} rows) {src} -> {shelf}")
    print(f"manifest {V.MANIFEST_NAME} sha256 {rec['manifest_sha256']} — verify ok")
    return rec


def verify(shelf: Path) -> int:
    try:
        entries = V.verify_shelf(Path(shelf))
    except V.VideoShelfError as e:
        print(f"VERIFY FAIL: {e}")
        return 1
    print(f"VERIFY OK: {len(entries)} files named, every sha256 matches ({shelf})")
    return 0


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="tools.worlds.video_shelf", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("promote", help="the bench tapes → a life's frozen shelf dir (+ the manifest)")
    p.add_argument("--src", required=True, type=Path)
    p.add_argument("--shelf", required=True, type=Path)
    v = sub.add_parser("verify", help="the shelf against its manifest, whole")
    v.add_argument("--shelf", required=True, type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "promote":
        promote(a.src, a.shelf)
        return 0
    return verify(a.shelf)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
