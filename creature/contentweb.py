# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 13:5x +0400 — PREREG-CONTENT-WEB (F1) §1
# (docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27, cweb-1010 @ 35ea7e8): the
# content tokens of the amodal knowledge web. Test-first: tests/creature/test_content_web.py (RED on
# 35ea7e8 — this module and the flag did not exist).
"""creature/contentweb.py — the per-sense CONTENT TOKENS fed to the knowledge webs behind
Mind(..., content_web: bool = False). Pure functions, import-light (creature/inner.py and
creature/muse.py's own law: no organism imports, so nothing here can become circular); the web's
arithmetic (genome/web.py) is UNTOUCHED — it hears strings, it never learns the difference.

THE TOKENS (the law §1, machine form; every constant declared here BEFORE any reading):
  w:<word>   every word-carrying row — the ear (the folder's read words and the video captions arrive
             as ear rows), and the chat/ask doors' consumed sentences (the SAME vocabulary as the ear:
             read text and heard speech land in one lexicon — the human form). Under the flag the ear's
             node keys gain this prefix by construction; OFF they stay bare (byte-identity).
  s:<sig>    the SIGHT channel (eye canvases — scene/maker/video): ONE token per hypothesis of the
             glance, in the glance's own order. sig = blake2b with a 32-bit digest (blake2b-32) over
             the organism's OWN feature row — the hypothesis's `feat` (brain/scene/eye.py:106's
             v = _unit(...) — a UNIT-normalized 144-vector, machinery.py:1029's L2 form, so components
             live in [-1, 1] and concentrate in ~[-0.3, 0.3]) — quantized per component at the DECLARED
             width QUANT_WIDTH = 0.05 (~12 effective levels where the components live; the units
             resolution of verifier V1, fixed from the code's own normalization, NEVER fitted). The
             token is AMODAL BY CONSTRUCTION: it names the organism's read of the content, never a
             word; the same canvas bytes map to the same token (the glance is a pure function of the
             bytes — the prediction never touches fixation selection, genome/gaze.py:209-217).
  g:<act>:<sign>   the game channel (outcome rows): the event kind (the row's own meta act) + its
             reward sign («+» / «-» / «0» / «none» when the row carries no got), declared from the
             row's own keys.
Senses not listed (touch/smell/ear-sound/sit/hold/grade/proposal/web/body): NO tokens in v1 — named
here, never silently skipped; a later law prices each.

The quantization's knife-edge is the law's §6: too coarse and distinct things collide, too fine and
nothing recurs. The collision and recurrence readings are printed by the bench either way — a bad
choice is a RESULT, never tuned post hoc.
"""
from __future__ import annotations

import hashlib
from typing import List, Optional, Sequence

import numpy as np

QUANT_WIDTH = 0.05     # the law §1's DECLARED per-component quantization width of the unit feature row
HASH_BYTES = 4         # blake2b-32: a 32-bit (4-byte) digest
WORD_PREFIX = "w:"
SIGHT_PREFIX = "s:"
GAME_PREFIX = "g:"
# the armed senses of v1 (the law §1): every OTHER consumed sense contributes NO tokens
TOKEN_SENSES = ("ear", "eye", "chat", "ask", "outcome")


def word_token(word: object) -> str:
    """w:<word> — one lexicon for heard speech and read text (the law §1)."""
    return WORD_PREFIX + str(word)


def sight_token(feat) -> str:
    """s:<sig> — the declared token of ONE hypothesis's unit feature row: per-component quantization
    at QUANT_WIDTH (round-to-nearest bin), the integer vector rendered as text (endianness-free) and
    hashed blake2b-32. Byte-deterministic by construction."""
    q = np.rint(np.asarray(feat, dtype=np.float64) / QUANT_WIDTH).astype(np.int64)
    sig = hashlib.blake2b(",".join(str(int(x)) for x in q).encode("utf-8"), digest_size=HASH_BYTES).hexdigest()
    return SIGHT_PREFIX + sig


def game_token(act: object, got: Optional[float]) -> str:
    """g:<kind>:<got> — the event kind + its reward sign, from the outcome row's own keys."""
    if got is None:
        sign = "none"
    else:
        g = float(got)
        sign = "+" if g > 0 else ("-" if g < 0 else "0")
    return GAME_PREFIX + str(act) + ":" + sign


# ------------------------------------------------------------------ the per-row extractors (one seam
# per sense — G-PLANT(i)'s doctored extractor lives at exactly this seam)
def ear_tokens(word: object) -> List[str]:
    """An ear row's tokens: its one word (the unchanged cadence; the prefix is the flag's)."""
    return [word_token(word)]


def eye_tokens(feats: Sequence) -> List[str]:
    """An eye row's tokens: one s: token per hypothesis, in the glance's own order (the caller reads
    the hypotheses off genome/brain.py:99's things_in_view — reused, never re-implemented)."""
    return [sight_token(f) for f in feats]


def words_tokens(words: Sequence) -> List[str]:
    """A chat/ask row's tokens: the consumed sentence's words, in sentence order."""
    return [word_token(w) for w in words]


def outcome_tokens(act: object, got: Optional[float]) -> List[str]:
    """An outcome row's token."""
    return [game_token(act, got)]
