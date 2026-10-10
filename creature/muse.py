# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:00 +0400 — PREREG-CONTEMPLATE-1 §1
# (docs/brain/muse/PREREG-CONTEMPLATE-1.md, signed 2026-10-09 23:01): THE MUSE — the pure machinery of
# the contemplation chain, called by creature/mind.py:_maybe_muse behind Mind(..., muse: bool = False)
# (default OFF: not one of these lines runs — the byte-identity pin, the N1 form). Test-first:
# tests/creature/test_muse.py (RED on 823c02d).
"""creature/muse.py — the trigger and the addresses of the contemplation chain: pure functions over the
mind's own web and self, nothing here writes the web, the self, the brain or the store (creature/inner.py's
own law, the same shape).

THE TRIGGER (the law §1.1, machine form): a heard sentence (the words the chat/ask doors consume) fires
when one of its words is
  (a) SELF-TOUCHING — the word is carried by the SELF node (a word of one of its claims' texts, the
      hearsay the self holds) or is a CONSOLIDATED web neighbour of such a word ("a word within one web
      edge of the SELF node": the self's own words are distance zero, their consolidated neighbours
      distance one — the declared reading); or
  (b) a NAMED NOVELTY — heard >= MUSE_NOVEL_MIN times this life (the web's own node count) with NO
      consolidated edge ("the web has never consolidated" it: heard but not known).

THE BUDGET (§1.1): at most ONE chain per MUSE_BUDGET heard sentences — the arithmetic is the mind's
(_maybe_muse); the constant is declared here beside the chain's bounds.

THE CHAIN (§1.2): the content address (seed_of) is the sha of the heard words' own bytes IN ORDER — a
shuffled bag addresses nothing (the law's NULL: content-addressed, never bag-addressed). The walk itself
is creature/inner.py's machinery (candidates/draw/lift) driven by the mind; first_topic is deliberately
NOT used: the muse's chain is seeded by the HEARD CLAIM, never by the self's least reliable word — a
named difference from INNER's restart, documented at the law's own reuse clause.
"""
from __future__ import annotations

import hashlib
import re
from typing import Dict, List, Sequence, Set

MUSE_BUDGET = 25          # §1.1: at most ONE chain per 25 heard sentences (declared, never fitted)
MUSE_STEPS = 8            # §1.2: the chain's bound (declared)
MUSE_INHIBIT = 2          # the walk's inhibition window over the last topics (the INNER line's own value)
MUSE_NOVEL_MIN = 2        # §1.1(b): heard >= 2 times this life, never consolidated (a named novelty)

_NON_LETTER = re.compile(r"[^a-z]")
WORD_LETTERS = 8          # the ear's own 8-letter law (genome/world.py:WORD_SLOTS; read_common.words_of)


def words_of(text: str) -> List[str]:
    """A claim text -> the ear's words: whitespace tokens, lower-cased, non a-z stripped, each truncated
    to its first WORD_LETTERS letters (read_common.words_of's own law — the creature/senses module is not
    imported here so creature/muse stays import-light beside genome/; pinned to cut identically by
    tests/creature/test_muse.py's matrix)."""
    out: List[str] = []
    for tok in str(text).split():
        cleaned = _NON_LETTER.sub("", tok.lower())[:WORD_LETTERS]
        if cleaned:
            out.append(cleaned)
    return out


def self_words(self_node) -> Set[str]:
    """The words the SELF node carries: the union over its claims' texts, cut by the ear's law. The
    claims are the self's hearsay (PREREG-KW-1 §4.3's implanted knowledge); their lived reliability
    counts are NOT self words (every heard word has one — the trigger would fire on everything)."""
    if self_node is None:
        return set()
    out: Set[str] = set()
    for claim in self_node.claims.values():
        out.update(words_of(claim.text))
    return out


def seed_of(words: Sequence[str]) -> str:
    """The chain's content address: the sha of the heard words' own bytes, IN ORDER (the law §6's
    replay-determinism: the walk is seeded from the heard rows' own bytes — the INNER precedent's
    substream keys on this address). Order destroyed -> another address -> no chain, no fruit."""
    return hashlib.sha256("\x00".join(str(w) for w in words).encode("utf-8")).hexdigest()[:16]


def trigger(words: Sequence[str], web, self_ws: Set[str]) -> Dict[str, object]:
    """The declared classes and only they fire (law §1.1 + §2 G-UNIT(b)). Returns {"fire", "anchors",
    "classes"}: anchors = the firing words in heard order (deduped), classes the sorted union of
    "self"/"novel" they fired under. A word the web never heard is in NO class (it cannot be within one
    edge of anything, and one hearing is not a novelty)."""
    anchors: List[str] = []
    classes: Set[str] = set()
    for w in dict.fromkeys(str(x) for x in words):
        if web is None or w not in web.nodes:
            continue
        nb = {n for n, _c in web.neighbours(w)}            # consolidated only (web.neighbours' own law)
        if w in self_ws or nb & self_ws:
            anchors.append(w)
            classes.add("self")
            continue                                       # a self word is never ALSO counted a novelty
        node = web.nodes[w]
        if int(node.get("n", 0)) >= MUSE_NOVEL_MIN and not nb:
            anchors.append(w)
            classes.add("novel")
    return {"fire": bool(anchors), "anchors": anchors, "classes": sorted(classes)}
