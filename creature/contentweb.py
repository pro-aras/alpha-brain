# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB (F1) §1
# (docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27, cweb-1010 @ 35ea7e8): the
# content tokens of the amodal knowledge web. Test-first: tests/creature/test_content_web.py (RED on
# 35ea7e8 — this module and the flag did not exist).
# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 18:1x +0400 — AMENDMENT 1 (signed, same
# folder, 2026-10-10 15:3x): the s: token RE-PRICED. The old form (blake2b-32 over the 0.05
# per-component quantization of the unit feature row) measured dead at the verdict of record —
# 0/240 recurrence across the toy's re-renders, 0 collisions; the knife-edge's FINE side; the record
# stands in docs/brain/content-web/VERDICT-*.md, never deleted. The cause per RULES §2: that token
# keyed the RENDER; the new one keys the RECOGNITION — s:c<id> = the nearest alive sight cell to the
# hypothesis's feature row by raw cosine over org.sight.cells, exactly genome/think.py's
# _nearest_sight_cell (induce()'s own read — reused by import, never re-implemented; never recall()'s
# abstain path). The empty alive store yields ZERO tokens (the eye's early-life silence is the
# declared honest floor). The w:/g: forms stand unchanged.
# edit: Kimi Code (K3, kimi-code, the seat), 2026-10-10 18:5x +0400 — M-COST's fix (the seat builds
# the amendment alone, Ahmad's 10-10 16:4x rule): eye_tokens hoists the alive ids/matrix ONCE per row
# (genome/think.py's _nearest_in — the hoisted twin pinned bit-identical by tests/genome/
# test_induce_hoist.py). The answers are byte-unchanged; the cost is one copy per row, not per
# hypothesis (the +11.8 % measured overhead was the per-call copies — an efficiency fault, the bar
# never moved).
"""creature/contentweb.py — the per-sense CONTENT TOKENS fed to the knowledge webs behind
Mind(..., content_web: bool = False). Pure functions, import-light (creature/inner.py and
creature/muse.py's own law: no CREATURE imports, so nothing here can become circular; genome/think is
a genome-internal module, already imported by creature/mind); the web's arithmetic (genome/web.py) is
UNTOUCHED — it hears strings, it never learns the difference.

THE TOKENS (the law §1 + AMENDMENT 1, machine form; every constant declared here BEFORE any reading):
  w:<word>   every word-carrying row — the ear (the folder's read words and the video captions arrive
             as ear rows), and the chat/ask doors' consumed sentences (the SAME vocabulary as the ear:
             read text and heard speech land in one lexicon — the human form). Under the flag the ear's
             node keys gain this prefix by construction; OFF they stay bare (byte-identity).
  s:c<id>    the SIGHT channel (eye canvases — scene/maker/video): ONE token per hypothesis of the
             glance, in the glance's own order. id = the index of the NEAREST ALIVE SIGHT CELL to the
             hypothesis's feature row by RAW COSINE over org.sight.cells — genome/think.py's
             _nearest_sight_cell's exact form (the read induce() already uses; deliberately NOT
             recall()'s resonance/KWTA abstain path — a read of the organism's geometry, never the
             answer machinery). The token is AMODAL BY CONSTRUCTION and now keys the organism's OWN
             RECOGNITION of the content: the same thing re-seen is whatever re-resonates the same
             cell. THE DECLARED FLOOR: a canvas read with ZERO alive sight cells emits ZERO s: tokens
             (the eye's early-life silence — never an invented key). The read happens where the feed
             sits in _consume_eye — the store as it stands ON ARRIVAL, before this canvas's own
             learning road: a novel canvas keys to the nearest OLD cell (the organism's prior
             geometry), never to the cell its own road may then birth.
  g:<act>:<sign>   the game channel (outcome rows): the event kind (the row's own meta act) + its
             reward sign («+» / «-» / «0» / «none» when the row carries no got), declared from the
             row's own keys.
Senses not listed (touch/smell/ear-sound/sit/hold/grade/proposal/web/body): NO tokens in v1 — named
here, never silently skipped; a later law prices each.

The knife-edge of the law's §6 now reads on the organism's resolution: nearest-cell churn across
re-renders when cells crowd (the jitter crossing cell boundaries) — the pilot prints the recurrence,
the all-pairs collision count, and the per-component render-jitter σ (the diagnostic that killed the
old form) BEFORE any mark binds. A bad form is a RESULT, never tuned post hoc.
"""
from __future__ import annotations

from typing import List, Optional, Sequence

import numpy as np

# AMENDMENT 1: the organism's own recognition read — genome/think.py's _nearest_sight_cell (the raw
# cosine nearest ALIVE sight cell; induce()'s form), imported, never re-implemented. genome/think
# imports genome-internal modules only (world/machinery/predict): no circularity into creature/.
from genome.think import _nearest_in, _nearest_sight_cell

WORD_PREFIX = "w:"
SIGHT_PREFIX = "s:"
GAME_PREFIX = "g:"
# the armed senses of v1 (the law §1): every OTHER consumed sense contributes NO tokens
TOKEN_SENSES = ("ear", "eye", "chat", "ask", "outcome")


def word_token(word: object) -> str:
    """w:<word> — one lexicon for heard speech and read text (the law §1)."""
    return WORD_PREFIX + str(word)


def cell_of(org, feat) -> Optional[int]:
    """AMENDMENT 1's extractor seam (G-PLANT(iii)'s doctoring point): the nearest ALIVE sight cell to
    `feat` by raw cosine over the organism's store — genome/think.py's _nearest_sight_cell itself.
    None when the alive store is empty (the declared floor's own None)."""
    return _nearest_sight_cell(org, np.asarray(feat, dtype=np.float64))


def sight_token(org, feat) -> Optional[str]:
    """s:c<id> — the recognition token of ONE hypothesis's feature row: the nearest alive sight cell
    (cell_of), or None when the store is empty (the eye's early-life silence — zero tokens, never an
    invented key). Deterministic by construction (the store and the glance are)."""
    cid = cell_of(org, feat)
    return None if cid is None else SIGHT_PREFIX + "c" + str(int(cid))


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


def eye_tokens(org, feats: Sequence) -> List[str]:
    """An eye row's tokens: one s:c<id> token per hypothesis, in the glance's own order (the caller
    reads the hypotheses off genome/brain.py:99's things_in_view — reused, never re-implemented).
    The empty alive store yields ZERO tokens (the declared floor, per-hypothesis Nones dropped).
    The alive ids/matrix are hoisted ONCE per row (genome/think.py's _nearest_in — pinned
    bit-identical to the per-call form by tests/genome/test_induce_hoist.py): the answers are
    unchanged, the cost is one copy per row, not one per hypothesis."""
    ids = org.sight.alive_ids()
    if len(ids) == 0:
        return []
    M = org.sight.cells[ids]
    out: List[str] = []
    for f in feats:
        cid = _nearest_in(ids, M, np.asarray(f, dtype=np.float64))
        if cid is not None:
            out.append(SIGHT_PREFIX + "c" + str(int(cid)))
    return out


def words_tokens(words: Sequence) -> List[str]:
    """A chat/ask row's tokens: the consumed sentence's words, in sentence order."""
    return [word_token(w) for w in words]


def outcome_tokens(act: object, got: Optional[float]) -> List[str]:
    """An outcome row's token."""
    return [game_token(act, got)]
