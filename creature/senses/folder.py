# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 02:05 +0400 — A12: the folder door (docs/G4-PREREG.md §11.3).
# edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:08 +0400 — C2 (docs/G4-WAVE3-CLAUSES.md W3-6 step 4;
# PREREG §17, the amendment stamped there): PACING (at most one new picture per scan, deterministic
# (folder, filename) bytewise order -- never mtime, never scan timing) and the SIGHT-ONLY road §11.1 step 2
# needs (a picture under world/ directly, or under a folder whose name is not a word, publishes the EYE row
# only, meta.word absent); FOLDER_DOOR_GATED, the constant `creature/body.py:main` reads before arming the
# door from the genome's own WORLD line (Claude flips it True once G4-6 exists — C3).
"""creature/senses/folder.py — watches `world/` every `period` seconds for at most ONE new picture (by
sha256, never by mtime alone -- a touched-but-unchanged file must not re-publish): a picture under a
folder whose name is a word (a-z <= 8 letters) publishes ear (word = the folder name) then eye; a picture
directly under `world/`, or under a folder whose name is NOT a word (`WORD_RE` fails), publishes the eye
row only -- sight-only, `meta.word` absent (PREREG §11.3's amendment, §11.1 step 2's road). Source
"folder", `meta.moment = "f" + sha[:12]` either way.

A pure SENSE (G4-1's writer sweep): it never touches state/journal/memory, and never imports Organism.
The seen-set (`root/folder/SEEN.json`) is written AFTER the row(s) are durable on the tape -- the cursor
law (#230): a crash between publishing and marking-seen re-publishes the same picture (a safe, idempotent
duplicate the mind just re-lives), never silently loses one.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import re
import time
import zlib
from pathlib import Path
from typing import Callable, List, Tuple

import numpy as np
from PIL import Image

from genome import gaze

WORD_RE = re.compile(r"[a-z]{1,8}")
PICTURE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")

# C2 (PREREG §17): the door arms from the genome's own WORLD `folder <dir>` line only once this constant
# is True -- a genome line arms nothing until the code carrying G4-6 exists. Flipped True here, in the
# commit that lands C3's passing test (the brief's own instruction), which is NOT the same as the live
# creature (git 'master', /data/dev/genome) picking this up: Claude decides when to deploy this branch and
# restart creature.service -- that is "flipping the life", a separate act from flipping this constant.
# `--folder PATH` (creature/body.py:main) stays an override regardless of this constant, for tests.
FOLDER_DOOR_GATED = True


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


def _candidate_pictures(world_dir: Path) -> List[Tuple[str, Path, bool]]:
    """Every candidate picture under `world_dir`, sorted by (folder, filename) BYTEWISE -- the
    deterministic order C2's pacing rule needs (never mtime, never scan timing). `folder` is "" for a
    picture directly under `world_dir` (always sight-only); for one level down, `folder` is the
    directory's own name, and `is_word` says whether WORD_RE matches it -- a folder that does NOT match
    (e.g. `_unnamed`) still yields its pictures, sight-only (PREREG §11.3's amendment). Files that are not
    picture-suffixed (`world/OWN-FOLDERS.txt`, `README.md`, `ASK.log`) are never candidates -- the suffix
    filter alone excludes them, no folder/file special-casing needed."""
    out: List[Tuple[str, Path, bool]] = []
    if not world_dir.exists():
        return out
    for pic in world_dir.iterdir():
        if pic.is_file() and pic.suffix.lower() in PICTURE_SUFFIXES:
            out.append(("", pic, False))
    for d in world_dir.iterdir():
        if not d.is_dir():
            continue
        word = d.name
        is_word = bool(WORD_RE.fullmatch(word))
        for pic in d.iterdir():
            if pic.is_file() and pic.suffix.lower() in PICTURE_SUFFIXES:
                out.append((word, pic, is_word))
    out.sort(key=lambda t: (t[0], t[1].name))
    return out


# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:44 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 4
# (BODY-SENSES.md §4.5): the cheap wide channel, computed from filesystem metadata alone -- suffix, byte
# size, the folder's own name (hashed, never the name itself: BODY-SENSES's own words, "never the name,
# which is the answer" -- a bare crc32 the mind cannot invert to a word), mtime -- BEFORE the picture is
# decoded as an image (`gaze.canvas_of_picture`, the "opening" the brief names). A pure function of already-
# read bytes + `pic.stat()`; no filesystem write, no state.
def _smell_trait(pic: Path, data: bytes, word: str) -> np.ndarray:
    suffix = pic.suffix.lower()
    kind = (PICTURE_SUFFIXES.index(suffix) / len(PICTURE_SUFFIXES)) if suffix in PICTURE_SUFFIXES else 1.0
    size = math.log10(max(len(data), 1))
    folder = (zlib.crc32(word.encode("utf-8")) & 0xFFFFFFFF) / float(0x100000000)   # a HASH, never the name
    try:
        age_s = max(time.time() - pic.stat().st_mtime, 1e-3)
    except OSError:
        age_s = 1e-3
    age = math.log10(age_s)
    return np.array([kind, size, folder, age], dtype=np.float32)


def sense(publish: Callable, stop_event, world_dir: Path, root: Path, canvas: int = 128, period: float = 30.0,
          smell: bool = False) -> None:
    """`smell` (BODY-SENSES §4.5, LIFE.genome's DRAFT `SENSE smell` line): False (the default) is byte-
    identical to before this parameter existed -- no "smell" row is ever published, matching every other
    additive-parameter convention this module already uses. True publishes a `smell` row BEFORE the `ear`/
    `eye` rows of the same picture, sharing that picture's own moment."""
    world_dir = Path(world_dir)
    seen_path = Path(root) / "folder" / "SEEN.json"
    seen_path.parent.mkdir(parents=True, exist_ok=True)
    seen = _load_seen(seen_path)

    while not stop_event.is_set():
        for word, pic, is_word in _candidate_pictures(world_dir):
            try:
                data = pic.read_bytes()
            except OSError:
                continue
            sha = hashlib.sha256(data).hexdigest()
            if sha in seen:
                continue
            moment = "f" + sha[:12]
            try:
                rgb = gaze.canvas_of_picture(pic, canvas)
            except Exception:
                continue   # an unreadable picture is skipped, never fatal to the sense thread (SenseThread's own restart law covers a genuine crash)
            # smell's own trait is computed from metadata alone (never `rgb`, the decoded pixels) -- the
            # decode above only gates WHETHER this picture is published at all this scan (an unreadable
            # picture must not publish a smell row with no matching eye row behind it, or a retry would
            # re-publish the identical smell row every scan until the picture becomes readable/is fixed).
            if smell:
                trait = _smell_trait(pic, data, word)
                publish("smell", trait.tobytes(), {"moment": moment, "source": "smell", "sha_prefix": sha[:12]}, "f32")
            if is_word:
                publish("ear", word.encode("utf-8"), {"moment": moment, "source": "folder", "word": word}, "txt")
            publish("eye", _png_bytes(rgb), {"moment": moment, "source": "folder"}, "png")
            seen.add(sha)
            seen_path.write_text(json.dumps(sorted(seen)))   # AFTER the row(s) are durable -- the cursor law (#230)
            break   # C2's pacing amendment: at most ONE new picture per scan/period
        stop_event.wait(period)
