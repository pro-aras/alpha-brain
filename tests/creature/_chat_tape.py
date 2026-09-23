# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:36 +0400 — A4L-LANG: a small synthetic tape for the chat
# tests — maker canvases (world_maker.make's own renders, the eye's own road) + shelf-style multi-word lines (the reader's
# own render) so the organism learns a few things and the episodes carry frames, links and a pivot; chat rows published
# through the door's own scan_once. Fresh roots only (#212). A helper module (leading underscore: no tests of its own).
from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

from creature.senses import chat as chat_sense
from creature.senses import read_common
from creature.tape import Tape
from genome import world

ROOT = Path(__file__).resolve().parents[2]
LANG_GENOME = ROOT / "genome" / "ladder" / "A4L-LANG.genome"
FLOOR_GENOME = ROOT / "genome" / "ladder" / "A4L-FLOOR.genome"
THINGS = ("ring", "star", "cross")
AT = "2026-09-23T01:00:00.000Z"


def _png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(b, format="PNG"); return b.getvalue()


def lines_it_is(n: int = 30, fillers: int = 60) -> List[List[str]]:
    """«it is X» over twelve distinct X: «it is» a frame heard adjacent n times (a LINK), «is» a PIVOT — beside `fillers`
    two-word lines naming no question word, so find_frames' independence bar can clear (with no filler every multi-word
    instant carries both words: expected = n*n/n = n, and n > 2n never holds — found RED by this file's first run)."""
    xs = ["big", "red", "on", "up", "here", "fun", "hot", "wet", "old", "new", "sad", "odd"]
    fill = [["green", "box"], ["blue", "ball"]]
    return [["it", "is", xs[k % len(xs)]] for k in range(n)] + [fill[k % 2] for k in range(fillers)]


def lines_varied(n: int = 120, seed: int = 11) -> List[List[str]]:
    """Shelf-like lines of three words drawn from a sixty-word vocabulary: rendered text is the life's main birth source
    (alpha4-1's shelf), so a record that must cross GROW's first doubling carries them."""
    vocab = [w for w in ("the cat sat on a mat and dog ran to big red hen in pond sun man duck tub nest pot lid cup "
                         "boy girl fox owl bee ant cow pig hat bag box jam egg fig map pen car bus van log net "
                         "kid rug web yak zip hut ink").split()]
    rng = np.random.default_rng(seed)
    return [[vocab[int(i)] for i in rng.integers(0, len(vocab), size=3)] for _ in range(n)]


def build(root: Path, things: Sequence[str] = THINGS, per_thing: int = 45, lines: Optional[List[List[str]]] = None,
          seed: int = 20260923, k0: int = 0) -> Tape:
    """Publishes `lines` (shelf-style moments) FIRST, then `per_thing` maker canvases of each thing, interleaved
    round-robin, every canvas by world.render_canvas on its own rng [seed, k] — never seed 3 (the chat's held-out renders)."""
    tape = Tape(root)
    k = k0
    for j, words in enumerate(lines or []):
        m = f"read{k0 + j:06d}"
        for w in words:
            tape.publish("ear", w.encode(), {"moment": m, "source": "shelf", "word": w}, "txt", at=AT)
        rgb = read_common.render_line(" ".join(words), 128, read_common.DEFAULT_FONT_PATH)
        tape.publish("eye", _png(rgb), {"moment": m, "source": "shelf", "text": " ".join(words)}, "png", at=AT)
    for i in range(per_thing):
        for t in things:
            rgb, _truth = world.render_canvas(t, np.random.default_rng([seed, k]))
            m = f"w0000i{k:06d}t{k:09d}"
            tape.publish("ear", t.encode(), {"moment": m, "source": "maker", "word": t}, "txt", at=AT)
            tape.publish("eye", _png(rgb), {"moment": m, "source": "maker"}, "png", at=AT)
            k += 1
    return tape


def held_render(thing: str, k: int = 0) -> np.ndarray:
    """A held-out render (seed 3, the chat's own), disjoint from build()'s [seed, k] streams."""
    rgb, _t = world.render_canvas(thing, np.random.default_rng([3, k]))
    return rgb


def drop_chat(root: Path, tape: Tape, cid: str, text: str, picture: Optional[np.ndarray] = None) -> Dict[str, object]:
    """Write one chat (and its picture) under root/chat/ and publish it through the door's own scan; returns the row."""
    (root / "chat" / "in").mkdir(parents=True, exist_ok=True)
    obj: Dict[str, object] = {"id": cid, "text": text}
    if picture is not None:
        (root / "chat" / "pics").mkdir(parents=True, exist_ok=True)
        (root / "chat" / "pics" / f"{cid}.png").write_bytes(_png(picture))
        obj["picture"] = f"{cid}.png"
    (root / "chat" / "in" / f"{cid}.json").write_text(json.dumps(obj))
    rows: List[Dict[str, object]] = []

    def pub(sense, payload, meta, ext):
        r = tape.publish(sense, payload, meta, ext, at=AT); rows.append(r); return r
    chat_sense.scan_once(pub, root, canvas=128, letters=8)
    assert rows and rows[0]["sense"] == "chat", rows
    return rows[0]


def drop_grade(root: Path, tape: Tape, cid: str, right: bool, novel: bool) -> Dict[str, object]:
    (root / "chat" / "graded").mkdir(parents=True, exist_ok=True)
    (root / "chat" / "graded" / f"{cid}.json").write_text(json.dumps({"id": cid, "right": right, "novel": novel}))
    rows: List[Dict[str, object]] = []

    def pub(sense, payload, meta, ext):
        r = tape.publish(sense, payload, meta, ext, at=AT); rows.append(r); return r
    chat_sense.scan_once(pub, root, canvas=128, letters=8)
    return [r for r in rows if r["sense"] == "grade"][0]


def journal_rows(root: Path) -> List[dict]:
    out: List[dict] = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        out += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    return out
