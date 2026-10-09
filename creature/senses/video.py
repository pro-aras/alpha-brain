# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 20:56 +0400 — PREREG-ALPHA-6 §1.2/§2 B2 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…): THE VIDEO WORLD SENSE, written test-first (tests/creature/test_sense_video.py,
# tests/tools/test_video_shelf.py, tests/genome/test_parse_world_video.py — RED before this module existed).
"""creature/senses/video.py — SENSE video: the open world's curriculum tapes as a LIFE world (PREREG-ALPHA-6 §1.2).

The genome's `WORLD video shelf <dir> every <n> s; loop; manifest sha256` line arms this sense
(creature/body.py:_declared_video_config). The shelf is FROZEN at launch: a sha256 MANIFEST over every shelf
file, written by the promotion tool (tools/worlds/video_shelf.py — the two share THIS module's manifest form,
so a promoted shelf is exactly what the sense streams).

The rows are the shelf tape's own, published in its own order: each frame an eye row (the tape's own payload
PNG), each caption token an ear row just before its canvas (V0's mapping — the order law holds by the tape's
own construction); the metas are carried WHOLE (provenance video/video-caption, the `video` meta, the tape's
moments/timings — nothing renamed, nothing added, nothing dropped). One canvas per declared `every_s` (the
cadence ≈ the measured life cadence; the clock worlds' own form: the world does not wait for the mind). At the
shelf's end: LOOP from the start (repetition is the motherese form, declared), the loop count journaled through
the `events` callable the body hands (one `video_loop` row per wrap; a crash between the wrap and the cursor
write may journal one row twice in the narrow race every cursor has — the count reads as the max).

THE MANIFEST DISCIPLINE (the law's G-PLANT): before ANY row is published the whole shelf verifies against the
manifest — every named file present and hashing to its entry, every file under the shelf named (a tampered,
missing or sneaked-in file is REFUSED BY NAME) — and every row must name a payload the manifest names whose
sha256 is the manifest's entry. At publish time each payload's bytes are re-hashed against the manifest entry
before they go out: the sense never publishes a row, or a byte, the manifest does not vouch for. A refusal
raises VideoShelfError; the body's crash isolation journals it (the launch's own checks read the silence).

A pure SENSE (creature/senses/scene.py's form): writes only through `publish`, its own cursor
root/video/VIDEO-CURSOR (JSON {loop, row, journaled} written AFTER each row is durable — #230's cursor law, so
a restart resumes mid-shelf and never republishes a durable row) and the `events` journal rows; never reads
the mind, never imports the organism.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# The arming gate (creature/senses/scene.py's SCENE_DOOR_GATED discipline): a genome line arms nothing until
# the code carrying it exists — creature/body.py:_declared_video_config reads it.
VIDEO_DOOR_GATED = True

CURSOR_NAME = "VIDEO-CURSOR"
MANIFEST_NAME = "MANIFEST.sha256"
_WAIT_POLL_S = 0.005


class VideoShelfError(Exception):
    """A shelf whose honesty is in doubt: named (the file, the row, the hash), never silently streamed."""


# ------------------------------------------------------------------------------------------------ hashing
def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------ the manifest (shared with the promotion tool)
def write_manifest(shelf: Path) -> Path:
    """<shelf>/MANIFEST.sha256: `<sha256>  <relpath>` for every file under the shelf (never itself), sorted by
    relpath — sha256sum's own line form, deterministic for the same bytes."""
    shelf = Path(shelf)
    files = sorted((p for p in shelf.rglob("*") if p.is_file() and p.name != MANIFEST_NAME),
                   key=lambda p: p.relative_to(shelf).as_posix())
    lines = "".join(f"{_sha256_path(p)}  {p.relative_to(shelf).as_posix()}\n" for p in files)
    man = shelf / MANIFEST_NAME
    man.write_text(lines)
    return man


def load_manifest(shelf: Path) -> Dict[str, str]:
    """relpath -> sha256, exactly as written. No manifest: the shelf is not a shelf, refused by name."""
    man = Path(shelf) / MANIFEST_NAME
    if not man.is_file():
        raise VideoShelfError(f"the shelf {shelf} carries no {MANIFEST_NAME} — the shelf is FROZEN by its manifest "
                              f"(PREREG-ALPHA-6 §1.2); the promotion tool writes it")
    out: Dict[str, str] = {}
    for line in man.read_text().splitlines():
        if not line.strip():
            continue
        sha, _sep, rel = line.partition(" ")
        rel = rel.strip()
        if not rel or not sha:
            raise VideoShelfError(f"the manifest line {line!r} is not `<sha256>  <relpath>`")
        if rel in out:
            raise VideoShelfError(f"the manifest names {rel} twice")
        out[rel] = sha.strip()
    return out


def verify_shelf(shelf: Path) -> Dict[str, str]:
    """The frozen shelf against its manifest, whole: every named file present and hashing to its entry; every
    file under the shelf (but the manifest itself) named. Returns relpath -> sha256. Any doubt raises by name."""
    shelf = Path(shelf)
    entries = load_manifest(shelf)
    for rel, want in entries.items():
        p = shelf / rel
        if not p.is_file():
            raise VideoShelfError(f"the shelf lost a file its manifest names: {rel}")
        got = _sha256_path(p)
        if got != want:
            raise VideoShelfError(f"the shelf file {rel} does not hash to its manifest's sha256 "
                                  f"({got[:16]}… != {want[:16]}…) — the shelf is frozen at launch")
    for p in sorted(shelf.rglob("*")):
        if p.is_file() and p.name != MANIFEST_NAME:
            rel = p.relative_to(shelf).as_posix()
            if rel not in entries:
                raise VideoShelfError(f"the shelf carries a file its manifest does not name: {rel} — "
                                      f"additions between lives, never mid-life")
    return entries


# ------------------------------------------------------------------------------------------------ the rows
def _ext(rel: str) -> str:
    if rel.endswith(".png"):
        return "png"
    if rel.endswith(".txt"):
        return "txt"
    raise VideoShelfError(f"the video world's tape carries a payload of an unknown kind: {rel} (its rows are png/txt)")


def _load_rows(shelf: Path, entries: Dict[str, str]) -> List[Dict[str, object]]:
    """The shelf tape's rows in tape order (day files sorted, lines in order — creature/tape.py's own glob form),
    each checked against the manifest: only eye/ear rows (the two provenances), each naming a payload the
    manifest names, each row's sha the manifest's own entry for that payload."""
    rows: List[Dict[str, object]] = []
    for day in sorted(Path(shelf).glob("*.jsonl")):
        for line in day.read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise VideoShelfError(f"the shelf {shelf} carries no tape rows")
    for r in rows:
        sense = r.get("sense")
        if sense not in ("eye", "ear"):
            raise VideoShelfError(f"the video world's tape carries a {sense!r} row (seq {r.get('seq')}) — "
                                  f"its two provenances are eye and ear, never another")
        rel = str(r.get("payload"))
        if rel not in entries:
            raise VideoShelfError(f"row seq {r.get('seq')} names a payload its manifest does not: {rel} — "
                                  f"the sense never publishes a row the manifest doesn't name")
        if str(r.get("sha")) != entries[rel]:
            raise VideoShelfError(f"row seq {r.get('seq')}'s sha does not equal the manifest's sha256 for {rel}")
    return rows


def plan(cfg: Dict[str, object]) -> Tuple[List[Dict[str, object]], Dict[str, str]]:
    """declared["WORLD_VIDEO"] -> (the shelf's rows, the manifest entries), the shelf verified WHOLE first.
    Reads the frozen shelf (I/O at arm time, never inside the publish loop beyond the per-row re-hash)."""
    shelf = Path(str(cfg["shelf"]))
    entries = verify_shelf(shelf)
    return _load_rows(shelf, entries), entries


def _payload_bytes(shelf: Path, rel: str, entries: Dict[str, str]) -> bytes:
    """The row's payload bytes, re-hashed against the manifest at the moment they go out: never a byte the
    manifest does not vouch for."""
    data = (shelf / rel).read_bytes()
    if _sha256_bytes(data) != entries[rel]:
        raise VideoShelfError(f"the payload {rel} does not hash to the manifest's sha256 at publish time — "
                              f"the shelf was touched mid-life")
    return data


# ------------------------------------------------------------------------------------------------ progress (scene.py's form)
class Progress:
    """Thread-safe counters, shared between the sense thread and `creature/body.py:Body._build_status` (an
    EXTRA keyword like scene.py's own; default None, a direct call is unaffected)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._rows = 0
        self._canvases = 0
        self._loop = 0
        self._ended = False

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            return {"published_rows": self._rows, "published_canvases": self._canvases,
                    "loop": self._loop, "ended": self._ended}

    def set(self, rows: int, canvases: int, loop: int) -> None:
        with self._lock:
            self._rows, self._canvases, self._loop = rows, canvases, loop

    def mark(self, rows: int, canvases: int, loop: int, ended: bool) -> None:
        with self._lock:
            self._rows, self._canvases, self._loop, self._ended = rows, canvases, loop, ended


# ------------------------------------------------------------------------------------------------ the cursor (#230)
def _cursor_path(root: Path) -> Path:
    return Path(root) / "video" / CURSOR_NAME


def _load_cursor(root: Path) -> Tuple[int, int, int]:
    """(loop, row-in-pass, journaled-loop); a missing or unreadable cursor starts the shelf from its start."""
    p = _cursor_path(root)
    if not p.exists():
        return (0, 0, 0)
    try:
        d = json.loads(p.read_text())
        return (max(0, int(d.get("loop", 0))), max(0, int(d.get("row", 0))), max(0, int(d.get("journaled", 0))))
    except (OSError, ValueError, TypeError, AttributeError):
        return (0, 0, 0)


def _write_cursor(root: Path, loop: int, row: int, journaled: int) -> None:
    p = _cursor_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps({"loop": loop, "row": row, "journaled": journaled}))
    tmp.replace(p)


# ------------------------------------------------------------------------------------------------ the executor
def sense(publish: Callable, stop_event, root: Path, cfg: Dict[str, object],
          progress: Optional[Progress] = None, events: Optional[Callable[[Dict[str, object]], None]] = None) -> None:
    """The sense thread body (a `creature.body.SenseThread` runs it): verify the shelf, then publish its rows
    in order, one canvas per declared `every_s`, resuming from root/video/VIDEO-CURSOR, LOOPING at the shelf's
    end with the count journaled, until the stop event."""
    shelf = Path(str(cfg["shelf"]))
    every = float(cfg["every_s"])
    loop_on = bool(cfg.get("loop", True))
    rows, entries = plan(cfg)                                # the manifest discipline, before anything publishes
    n = len(rows)
    n_canvases = sum(1 for r in rows if r["sense"] == "eye")
    loop, i, journaled = _load_cursor(root)
    if i >= n:                                               # a cursor past the shelf's end: the pass had wrapped
        loop, i = loop + 1, 0
    published_canvases = loop * n_canvases + sum(1 for r in rows[:i] if r["sense"] == "eye")
    published_rows = loop * n + i
    if progress is not None:
        progress.set(published_rows, published_canvases, loop)
    last_eye: Optional[float] = None
    while not stop_event.is_set():
        r = rows[i]
        if r["sense"] == "eye":
            if last_eye is not None:
                wait = every - (time.monotonic() - last_eye)
                if wait > 0 and stop_event.wait(wait):
                    return
            last_eye = time.monotonic()
        rel = str(r["payload"])
        publish(r["sense"], _payload_bytes(shelf, rel, entries), dict(r["meta"]), _ext(rel))
        i += 1
        published_rows += 1
        if r["sense"] == "eye":
            published_canvases += 1
        _write_cursor(root, loop, i, journaled)              # AFTER the row is durable (#230)
        if progress is not None:
            progress.mark(published_rows, published_canvases, loop, False)
        if i >= n:
            if not loop_on:                                  # never from the parser (the ONE form loops); a test's own
                if progress is not None:
                    progress.mark(published_rows, published_canvases, loop, True)
                while not stop_event.is_set():
                    stop_event.wait(1.0)
                return
            loop += 1
            i = 0
            if events is not None and loop > journaled:
                journaled = loop
                events({"event": "video_loop", "loop": loop, "canvases": n_canvases, "rows": n})
            _write_cursor(root, loop, i, journaled)
