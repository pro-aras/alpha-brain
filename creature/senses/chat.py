# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:33 +0400 — A4L-LANG task 2 (docs/briefs/A4L-LANG.md;
# docs/A4-LADDER-PREREG.md §3.2 item 1): THE CHAT DOOR — a conversation door that cannot teach him.
"""creature/senses/chat.py — SENSE chat: watches `$ROOT/chat/in/*.json` `{id, text, picture?}` (written by the SEAT —
tools/chat_seat.py — or by anyone the orchestrator lets type; never by any part of this creature) and publishes ONE tape
row of the sense `chat` per chat, one chat per scan, in bytewise filename order. Its payload is the CANVAS: the chat's
picture when it names one (a held-out render the seat wrote under `chat/pics/`, never text printed on it — the gaze
fixates ink, so a question printed on the picture would be answered about the print), else the sentence rendered as a
line exactly as the shelf reader renders one (`read_common.render_line`, the default font, the reader's own cleaned
words joined). Its meta: `{moment, source, id, words, shown}` — the words cut exactly as the reader cuts them
(`read_common.words_of`, the ear's 8-letter law) and NEVER the family, the thing, the lure or any truth: the creature
does not parse a question, and the door does not tell it what kind of question it is.

**Never an `ear` or `eye` row** — so no existing instrument (canvases, moments, births by source, the SURPRISE shares,
the READ mark's shelf episodes) ever counts a chat as a world canvas, and no chat word can reach the MEET road. The mind
routes every `chat` row to ONE read-only branch (creature/mind.py:_consume_chat).

It also watches `$ROOT/chat/graded/*.json` `{id, right, novel}` (the seat's grades of the answers — the grade sense's
own shape) and publishes each as a `grade` row with meta `kind: "chat"`: the mind counts those on STATUS apart from the
ask door's grades (the READINESS judge's (d) never reads a chat grade).

A pure SENSE (G4-1's writer sweep): it reads `chat/in`, `chat/pics`, `chat/graded` and writes only its own two cursors
(`chat/SEEN.json`, `chat/GRADED-SEEN.json`), each AFTER the row it records is durable on the tape (#230's cursor law) — a
crash between publish and mark-seen re-publishes the same chat, which the mind answers again (a duplicate out file
overwritten with the same answer). It never imports Organism/machinery and never touches state/journal/memory.
`render_answer` is the DOOR's rendering of an answer for a reader: an abstention reads «(I do not know)» with its reason
and its resemblance — words the creature never says.
"""
from __future__ import annotations

import io
import json
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np
from PIL import Image

from . import read_common

# The arming gate (creature/senses/read.py's own C2/C3 discipline): a genome line arms nothing until the code carrying
# it exists — creature/body.py:_declared_chat_config reads it.
CHAT_DOOR_GATED = True
DEFAULT_PERIOD_S = 1.0     # the CHAT line carries no rate (the seat asks every 120 s); a code-side poll, raised in the report
MAX_WORDS = 64             # a chat's words are all heard (no reader chunking); bounded so a pasted page cannot flood a row
_SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def _load_seen(path: Path) -> set:
    if not path.exists():
        return set()
    try:
        v = json.loads(path.read_text())
        return set(str(x) for x in v) if isinstance(v, list) else set()
    except (json.JSONDecodeError, OSError):
        return set()     # a torn cursor from a crash mid-write reads as "nothing seen yet", never fatal (grade.py's own law)


def _write_cursor(path: Path, seen: set) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(sorted(seen)))
    tmp.replace(path)


def _chat_id(data: dict, stem: str) -> Optional[str]:
    cid = str(data.get("id", stem))
    if _SAFE_ID.fullmatch(cid):
        return cid
    return stem if _SAFE_ID.fullmatch(stem) else None


def _canvas_of(data: dict, words: List[str], pics_dir: Path, canvas: int, font_path: str) -> Optional[np.ndarray]:
    """The chat's canvas, or None when its picture is not readable yet (missing, torn, or not canvas x canvas — the
    door refuses a picture the eye was never built to see, never resizes it)."""
    pic = data.get("picture")
    if pic:
        p = pics_dir / Path(str(pic)).name          # a name under chat/pics/ only — never a path the chat chose
        try:
            rgb = np.asarray(Image.open(p).convert("RGB"), dtype=np.uint8)
        except (OSError, ValueError):
            return None
        if rgb.shape != (canvas, canvas, 3):
            return None
        return rgb
    return read_common.render_line(" ".join(words), canvas, font_path)


def scan_once(publish: Callable, root: Path, in_dir: Optional[Path] = None, graded_dir: Optional[Path] = None,
              pics_dir: Optional[Path] = None, canvas: int = 128, letters: int = 8,
              font_path: str = read_common.DEFAULT_FONT_PATH, max_words: int = MAX_WORDS) -> int:
    """One scan: at most ONE chat row (the first readable unseen chat, bytewise), then every unseen grade. Returns the
    number of rows published."""
    root = Path(root)
    in_dir = Path(in_dir) if in_dir is not None else root / "chat" / "in"
    base = in_dir.parent   # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 12:00 +0400 — the door's own directory: the CHAT line's `in` path's parent (root/chat tonight)
    graded_dir = Path(graded_dir) if graded_dir is not None else base / "graded"
    pics_dir = Path(pics_dir) if pics_dir is not None else base / "pics"
    cursor_dir = base
    cursor_dir.mkdir(parents=True, exist_ok=True)
    seen_path = cursor_dir / "SEEN.json"
    graded_seen_path = cursor_dir / "GRADED-SEEN.json"
    published = 0

    seen = _load_seen(seen_path)
    if in_dir.exists():
        for p in sorted(in_dir.glob("*.json"), key=lambda q: q.name.encode("utf-8")):
            if p.stem in seen:
                continue
            try:
                data = json.loads(p.read_text())
            except (json.JSONDecodeError, OSError):
                continue          # a torn write on the seat's side: retried next scan, never fatal
            if not isinstance(data, dict):
                continue
            cid = _chat_id(data, p.stem)
            if cid is None:
                continue
            words = read_common.words_of(str(data.get("text", "")), max_words=max_words, letters=letters)
            rgb = _canvas_of(data, words, pics_dir, canvas, font_path)
            if rgb is None:
                continue          # its picture is not there yet: this chat waits, the next one is not blocked
            meta: Dict[str, object] = {"moment": f"chat-{cid}", "source": "chat", "id": cid, "words": words,
                                       "shown": "picture" if data.get("picture") else "line"}
            publish("chat", read_common.png_bytes(rgb), meta, "png")
            seen.add(p.stem)
            _write_cursor(seen_path, seen)   # AFTER the row is durable (#230)
            published += 1
            break                            # one chat per scan

    gseen = _load_seen(graded_seen_path)
    if graded_dir.exists():
        for p in sorted(graded_dir.glob("*.json"), key=lambda q: q.name.encode("utf-8")):
            if p.stem in gseen:
                continue
            try:
                data = json.loads(p.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(data, dict):
                continue
            gid = _chat_id(data, p.stem) or p.stem
            right, novel = bool(data.get("right")), bool(data.get("novel"))
            payload = json.dumps({"id": gid, "right": right, "novel": novel, "kind": "chat"}).encode("utf-8")
            publish("grade", payload, {"moment": f"chatgrade-{p.stem}", "source": "chat", "kind": "chat",
                                       "id": gid, "right": right, "novel": novel}, "json")
            gseen.add(p.stem)
            _write_cursor(graded_seen_path, gseen)
            published += 1
    return published


def sense(publish: Callable, stop_event, root: Path, in_dir: Optional[Path] = None, graded_dir: Optional[Path] = None,
          pics_dir: Optional[Path] = None, canvas: int = 128, letters: int = 8,
          font_path: str = read_common.DEFAULT_FONT_PATH, period: float = DEFAULT_PERIOD_S, max_words: int = MAX_WORDS) -> None:
    """The door's thread body (a creature.body.SenseThread runs it): one scan every `period` seconds until stopped."""
    while not stop_event.is_set():
        scan_once(publish, root, in_dir=in_dir, graded_dir=graded_dir, pics_dir=pics_dir, canvas=canvas,
                  letters=letters, font_path=font_path, max_words=max_words)
        stop_event.wait(period)


def render_answer(out: Dict[str, object]) -> str:
    """The DOOR's rendering of one `chat/out/<id>.json` for a reader: the answer's words, or «(I do not know)» with its
    reason and its resemblance when the creature said nothing (it never says those words itself)."""
    ans = out.get("answer")
    if ans:
        return " ".join(str(w) for w in ans)
    reason = out.get("abstain_reason") or out.get("refused")
    res = out.get("resembles")
    return "(I do not know)" + (f" — {reason}" if reason else "") + (f"; it resembles «{res}»" if res else "")
