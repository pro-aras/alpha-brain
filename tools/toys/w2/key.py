"""tools/toys/w2/key.py — PREREG-W2 §3 item 4: the fenced EXAMINER'S KEY.

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:08 +0400 — new file, written after tests/tools/test_w2_key.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 item 4 (a table-driven parser of the WORLD's grammar returning
{subject, verb, polarity, np, tpl} or UNPARSEABLE; its table is the frozen v1 set and NOTHING else; it never reads the
organism's store).

The grammar (v1, frozen):
  «unsure» | «fresh» | «asked»                         with tpl M-M1 / M-M2 / M-M3 (the token must match its id)
  «alpha sees NP»                                      with tpl M-C1-T<n> (the NP's family must equal n), M-C3, M-A1..M-A3
  «alpha does not see NP»                              with tpl M-C2-T<n> (the NP's family must equal n)
  NP = T1 «⟨shape⟩» | T2 «⟨colour⟩ ⟨shape⟩» | T3 «⟨size⟩ ⟨shape⟩» | T4 «⟨size⟩ ⟨colour⟩ ⟨shape⟩»
over the trained vocabulary (brain/scene/world.py's SHAPES / COLOUR_NAMES / SIZE_NAMES, read-only). Anything else is
UNPARSEABLE (None): an unknown tpl, a word outside the ear's alphabet, an unknown verb, a family mismatch, a broken
negation, a token/id mismatch.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from brain.scene import world as W
from creature.senses import mentor as M

SHAPES = set(W.SHAPES)
COLOURS = set(W.COLOUR_NAMES)
SIZES = set(W.SIZE_NAMES)

SEES_TPLS = {"M-C3", "M-A1", "M-A2", "M-A3"}
MIRROR_TPL = {"unsure": "M-M1", "fresh": "M-M2", "asked": "M-M3"}


def _np_family(words: Sequence[str]) -> Optional[str]:
    """The NP's template family by its shape, or None when the words are no NP of T1-T4 over the vocabulary."""
    if len(words) == 1 and words[0] in SHAPES:
        return "T1"
    if len(words) == 2 and words[0] in COLOURS and words[1] in SHAPES:
        return "T2"
    if len(words) == 2 and words[0] in SIZES and words[1] in SHAPES:
        return "T3"
    if len(words) == 3 and words[0] in SIZES and words[1] in COLOURS and words[2] in SHAPES:
        return "T4"
    return None


def parse(words: Sequence[str], tpl: str) -> Optional[Dict[str, object]]:
    """One mentor production's words + its tpl id -> {subject, verb, polarity, np, tpl}, or None (UNPARSEABLE)."""
    if tpl not in M.TEMPLATES_V1:
        return None
    ws = [str(w) for w in words]
    if not ws or not all(w.isalpha() and w.islower() and len(w) <= 8 for w in ws):
        return None
    if len(ws) == 1 and ws[0] in MIRROR_TPL:
        return {"subject": None, "verb": "mirror", "polarity": None, "np": None, "tpl": tpl} if tpl == MIRROR_TPL[ws[0]] else None
    if ws[0] != "alpha":
        return None
    if len(ws) >= 3 and ws[1] == "sees":
        fam = _np_family(ws[2:])
        if fam is None:
            return None
        if tpl in SEES_TPLS or tpl == f"M-C1-{fam}":
            return {"subject": "alpha", "verb": "sees", "polarity": "+", "np": tuple(ws[2:]), "tpl": tpl}
        return None
    if len(ws) >= 5 and ws[1] == "does" and ws[2] == "not" and ws[3] == "see":
        fam = _np_family(ws[4:])
        if fam is None:
            return None
        if tpl == f"M-C2-{fam}":
            return {"subject": "alpha", "verb": "see", "polarity": "-", "np": tuple(ws[4:]), "tpl": tpl}
        return None
    return None
