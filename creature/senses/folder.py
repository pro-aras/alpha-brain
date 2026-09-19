# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 02:05 +0400 — A12: the folder door (docs/G4-PREREG.md §11.3).
"""creature/senses/folder.py — watches `world/<word>/` (a-z <= 8 letters, >= 1 picture) every `period`
seconds for a NEW picture (by sha256, never by mtime alone -- a touched-but-unchanged file must not
re-publish): ear (word = the folder name) then eye, source "folder", `meta.moment = "f" + sha[:12]`.

A pure SENSE (G4-1's writer sweep): it never touches state/journal/memory, and never imports Organism.
The seen-set (`root/folder/SEEN.json`) is written AFTER the rows are durable on the tape -- the cursor
law (#230): a crash between publishing and marking-seen re-publishes the same picture (a safe, idempotent
duplicate the mind just re-lives), never silently loses one.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path
from typing import Callable

from PIL import Image

from genome import gaze

WORD_RE = re.compile(r"[a-z]{1,8}")
PICTURE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")


def _png_bytes(rgb) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _load_seen(seen_path: Path) -> set:
    if not seen_path.exists():
        return set()
    try:
        return set(json.loads(seen_path.read_text()))
    except (json.JSONDecodeError, OSError):
        return set()      # a torn/partial SEEN.json from a crash mid-write is treated as "nothing seen yet" -- never fatal


def sense(publish: Callable, stop_event, world_dir: Path, root: Path, canvas: int = 128, period: float = 30.0) -> None:
    world_dir = Path(world_dir)
    seen_path = Path(root) / "folder" / "SEEN.json"
    seen_path.parent.mkdir(parents=True, exist_ok=True)
    seen = _load_seen(seen_path)

    while not stop_event.is_set():
        if world_dir.exists():
            for d in sorted(p for p in world_dir.iterdir() if p.is_dir()):
                word = d.name
                if not WORD_RE.fullmatch(word):
                    continue
                pics = sorted(p for p in d.iterdir() if p.is_file() and p.suffix.lower() in PICTURE_SUFFIXES)
                if not pics:
                    continue
                new_this_word = False
                for pic in pics:
                    try:
                        data = pic.read_bytes()
                    except OSError:
                        continue
                    sha = hashlib.sha256(data).hexdigest()
                    if sha in seen:
                        continue
                    try:
                        rgb = gaze.canvas_of_picture(pic, canvas)
                    except Exception:
                        continue   # an unreadable picture is skipped, never fatal to the sense thread (SenseThread's own restart law covers a genuine crash)
                    moment = "f" + sha[:12]
                    publish("ear", word.encode("utf-8"), {"moment": moment, "source": "folder", "word": word}, "txt")
                    publish("eye", _png_bytes(rgb), {"moment": moment, "source": "folder"}, "png")
                    seen.add(sha)
                    new_this_word = True
                if new_this_word:
                    seen_path.write_text(json.dumps(sorted(seen)))   # AFTER the rows are durable -- the cursor law (#230)
        stop_event.wait(period)
