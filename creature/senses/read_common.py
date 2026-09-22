# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 00:58 +0400 — STUB, not the implementation.
"""creature/senses/read_common.py — STUB.

Builder H (worktree /data/dev/genome-wt-y, branch alpha4-read, docs/briefs/ALPHA4-H.md) owns this file for
real: the show-and-hear renderer both the shelf reader (H's own SENSE read) and the web door (this
builder's DOOR web) use to turn a piece of text into ear rows (its words, heard) + ONE eye row (the line,
rendered and shown). "H lands first" — until that lands on this tree (by a merge at `alpha4-integration`,
never by this builder copying wt-y's file), every function here raises `NotImplementedError` with a clear
message naming the real owner, so any caller that reaches one fails LOUDLY and immediately rather than
silently substituting a fabricated render.

`creature/senses/web.py` (this builder's own module) checks `IS_STUB` once and, additionally, wraps every
call to these functions in a `try/except NotImplementedError` — belt and suspenders: a partial landing
(some functions real, some still raising) is handled exactly like a total stub, never a crash that would
send a `SenseThread` into its restart loop and burn the door's own rate budget re-fetching the same
question over and over (SOLUTIONS #230's class: a strict consumer of bytes it did not fully control,
looping on the same failure).

The four names and signatures below are copied verbatim from ALPHA4-H.md item 1 — this builder does not
invent a shape for them, only a placeholder body, so `web.py`'s own call sites need no change the day the
real module lands.
"""
from __future__ import annotations

from typing import List

import numpy as np

IS_STUB = True

_OWNER = ("builder H's real implementation has not landed on this tree yet "
          "(docs/briefs/ALPHA4-H.md item 1, worktree /data/dev/genome-wt-y) — this is a placeholder stub")


def split_sentences(text: str) -> List[str]:
    """STUB. Real shape (ALPHA4-H.md item 1): splits `text` into sentences."""
    raise NotImplementedError(f"read_common.split_sentences: {_OWNER}")


def words_of(sentence: str, max_words: int, letters: int) -> List[str]:
    """STUB. Real shape: lower-case, letters-only words of `sentence`, longest-first `letters` letters as
    the ear's `encode_word` expects, empty words dropped, at most `max_words`."""
    raise NotImplementedError(f"read_common.words_of: {_OWNER}")


def render_line(sentence: str, canvas_px: int, font_path: str) -> np.ndarray:
    """STUB. Real shape: PIL, black text on white, wrapped to `canvas_px`, deterministic (the same bytes
    twice) — returns an RGB array."""
    raise NotImplementedError(f"read_common.render_line: {_OWNER}")


def png_bytes(rgb: np.ndarray) -> bytes:
    """STUB. Real shape: PNG-encodes an RGB array (the same encoding every other sense's own `_png_bytes`
    helper uses — folder.py, game.py)."""
    raise NotImplementedError(f"read_common.png_bytes: {_OWNER}")
