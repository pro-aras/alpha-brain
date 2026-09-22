# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 00:51 +0400 — ALPHA4-H task 1 (docs/briefs/ALPHA4-H.md;
# ALPHA4-PREREG.md §3 SENSE read / §5 READ mark): a PURE module both the read sense (creature/senses/read.py)
# and the lexicon door (creature/senses/lexicon.py) use, and both the sense and the READ mark's held-out-font
# render import HELDOUT_FONT_PATH from HERE so the two can never drift apart (the brief's own words).
"""creature/senses/read_common.py — the shared, pure text/render primitives for the shelf reader and the
lexicon door: splitting prose into sentences, cleaning a sentence into ear-shaped words (<= 8 a-z letters,
matching `genome/world.py:encode_word`'s WORD_SLOTS), and rendering a line of text the SAME way a picture is
rendered elsewhere in this codebase (`creature/senses/folder.py:_png_bytes`, `creature/world_maker.py:_png_bytes`).

No I/O, no randomness, no imports of Organism/machinery -- a pure module, importable by the writer sweep's
"true sense" walk (tools/gate_g4.py:gate1, tests/creature/test_writer_sweep.py) without tripping either check.
"""
from __future__ import annotations

import io
import re
from typing import List

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# The letter ear's own vocabulary (genome/world.py:LETTERS is 'abcdefghijklmnopqrstuvwxyz' -- a-z only,
# WORD_SLOTS=8). Mirrored here as a plain regex rather than imported, so this module never depends on
# genome.world (which is itself independent of machinery/Organism -- but read_common.py's own law, stated
# above, is "no I/O, no randomness", and staying import-light keeps the writer sweep's static walk simple).
_NON_LETTER = re.compile(r"[^a-z]+")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WS = re.compile(r"\s+")

# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 00:51 +0400 — ALPHA4-H task 1: "The default font is
# DejaVu Sans; DejaVu Serif is the HELD-OUT font: never rendered in a life, only by the reading mark (a
# constant the mark and the sense both import, so they cannot drift)." Verified present on this box:
# `find /usr/share/fonts -iname '*DejaVu*'` (2026-09-23 00:4x +0400).
DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
HELDOUT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"


def split_sentences(text: str) -> List[str]:
    """A prose blob -> its sentences, in order. Whitespace (including newlines -- shelf docs are plain
    text wrapped at ~70 columns) is normalised to single spaces FIRST, so a sentence that was wrapped
    across lines becomes one string; then split after a '.', '!' or '?' followed by whitespace. Empty/
    whitespace-only fragments (a stray run of punctuation, a trailing empty tail) are dropped. Pure: the
    same text always yields the same list."""
    normalised = _WS.sub(" ", text).strip()
    if not normalised:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT.split(normalised) if s.strip()]


def words_of(sentence: str, max_words: int, letters: int) -> List[str]:
    """A sentence -> at most `max_words` ear-ready words: whitespace-tokenised, lower-cased, every
    character outside a-z stripped (apostrophes, digits, punctuation -- "don't" -> "dont", "1900." ->
    ""), each truncated to its own first `letters` characters (genome/world.py:encode_word's own limit --
    WORD_SLOTS=8 today; a word this sense hands the ear longer than that raises ValueError and would crash
    the mind thread, PREREG §2.6's crash law making that the worst possible failure for a sense to cause).
    A token that cleans to "" (pure punctuation/digits) is dropped, never published as an empty word."""
    out: List[str] = []
    for tok in sentence.split():
        cleaned = _NON_LETTER.sub("", tok.lower())[:letters]
        if cleaned:
            out.append(cleaned)
        if len(out) >= max_words:
            break
    return out


def render_line(sentence: str, canvas_px: int, font_path: str) -> np.ndarray:
    """A line of text -> an RGB canvas (canvas_px x canvas_px x 3, uint8): black text on white, PIL,
    word-wrapped to the canvas width, vertically centred. Deterministic -- no randomness, no wall clock --
    the same three arguments always render the same bytes (test_read_common.py's own pin). The DEFAULT
    font (module constant above) is what a life ever shows; the HELD-OUT font is passed only by the
    reading mark, never by `creature/senses/read.py`."""
    img = Image.new("RGB", (canvas_px, canvas_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_size = max(8, canvas_px // 8)
    font = ImageFont.truetype(str(font_path), font_size)
    margin = max(2, canvas_px // 32)
    max_w = canvas_px - 2 * margin

    lines: List[str] = []
    cur = ""
    for w in sentence.split():
        trial = (cur + " " + w).strip()
        box = draw.textbbox((0, 0), trial, font=font)
        if not cur or (box[2] - box[0]) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    line_h = font_size + max(2, font_size // 4)
    total_h = line_h * len(lines)
    y = max(margin, (canvas_px - total_h) // 2)
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font)
        lw = box[2] - box[0]
        x = max(margin, (canvas_px - lw) // 2)
        draw.text((x, y), line, fill=(0, 0, 0), font=font)
        y += line_h

    return np.asarray(img, dtype=np.uint8)


def png_bytes(rgb: np.ndarray) -> bytes:
    """The SAME encoding `creature/senses/folder.py:_png_bytes` / `creature/world_maker.py:_png_bytes`
    already use -- kept as its own tiny function here (rather than imported from either, neither of which
    this module should depend on) so read.py/lexicon.py share ONE copy between themselves."""
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()
