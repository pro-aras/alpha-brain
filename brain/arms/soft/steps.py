# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 18:10 +0400 — the row -> step encoder,
#   written AFTER brain/protocol.py froze at ac7d2ff (merged into this branch from
#   b1-integration). Every shape here is read from the frozen protocol / glance cache, not
#   guessed: GLANCES_PER_ROW=5, FEATURES_PER_GLANCE=144 (brain.glance_cache), CUE_MARKS (14,
#   brain.protocol), TAPE_KINDS (7, brain.protocol). LETTER_DIM=27 and the 24-slot cue table
#   are B1-PREREG.md §4 row A1's own numbers, not the protocol's — declared here (D12-D14,
#   continuing brain/arms/soft/engine.py's D1-D11) because the PREREG names the WIDTHS but not
#   the exact per-row decomposition into a step sequence.
#
# Declared choices:
#   D12. Per-row step order: TEACH = the 5 glance steps (showing the picture) THEN the name's
#        letter steps (hearing its name) — "sees it, then hears its name", the natural teaching
#        order and the only one consistent with "each tape row becomes steps" reading as ONE
#        temporal decomposition rather than two unordered halves.
#        ASK = the cue step(s) (in order; a compound like CHAIN is its two marks in order) THEN
#        each operand's steps in order (a row operand = its 5 glance steps; a name operand =
#        its letter steps) — "ask about X" is heard as "here is the question, here is what it
#        is about", matching how a spoken question places the wh-word/predicate before its
#        argument. PICK additionally appends, AFTER the cue+operand steps, each candidate's 5
#        glance steps IN ORDER — these are what PickScorer's D5 candidate encoding replays from
#        the query state; they do not feed the WORLD head's next-step loss (a candidate sheet is
#        shown, not experienced as a taught fact) — see ArmA1.answer's PICK branch.
#        ARRIVAL, SLEEP, TEST_BEGIN/TEST_END carry no glyph/name/cue content of their own — they
#        drive control flow (ArmA1.fit_event's own branches) and contribute no steps.
#   D13. The letter alphabet is 'a'..'z' (26) + one END-of-name step (27th slot) — a digit's
#        name ("zero".."nine") is spelled through the SAME 26-letter alphabet (its letters are
#        drawn from a-z) with its own END step; a name step's KIND one-hot is always "TEACH" or
#        the ask row's own kind, matching whichever row carries it (never a kind of its own).
#   D14. The 24-slot cue table (14 CUE_MARKS + 4 MLC-recycled + 6 headroom, PREREG §4 row A1)
#        is assigned IN ORDER OF FIRST APPEARANCE on the tape, not fixed alphabetically — a
#        deterministic function of the row stream alone (no seed needed), so two identical
#        replays agree without coordination, and the table is part of the arm's PERSISTED STATE
#        (snapshot/load) since a resumed run must keep assigning new marks after the same slots
#        the interrupted run had already used. >24 distinct marks ever seen -> RAISED (a
#        StepEncodingError, never silently dropped or wrapped around).
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

import numpy as np
import torch

from brain.glance_cache import FEATURES_PER_GLANCE, GLANCES_PER_ROW, Cache
from brain.protocol import TAPE_KINDS, is_name_operand, is_row_operand

LETTERS = "abcdefghijklmnopqrstuvwxyz"
LETTER_DIM = len(LETTERS) + 1  # + END (D13)
CUE_DIM = 24  # PREREG §4 row A1 (D14)
KIND_DIM = len(TAPE_KINDS)
GLANCE_DIM = FEATURES_PER_GLANCE
GLANCE_IDX_DIM = GLANCES_PER_ROW
STEP_DIM = GLANCE_DIM + GLANCE_IDX_DIM + LETTER_DIM + CUE_DIM + KIND_DIM

_KIND_INDEX = {k: i for i, k in enumerate(TAPE_KINDS)}


class StepEncodingError(Exception):
    """Raised (never silently absorbed, PREREG §11: 'RAISED, never worked around') when a
    cue vocabulary would exceed its declared 24 slots, or a name contains a character outside
    a-z (§2.3: names are lower-case a-z only, by construction of the world's own encode_word)."""


def _one_hot(width: int, at: int) -> torch.Tensor:
    v = torch.zeros(width)
    v[at] = 1.0
    return v


class SlotTable:
    """The 24-slot cue vocabulary (D14, REVISED after a real bug this file's own test caught —
    see below). The 14 real CUE_MARKS get a STATIC slot = their index in `brain.protocol.
    CUE_MARKS` (a frozen, protocol-level constant, no tape-dependence, no mutable state at
    all). Slots 14-23 (10 of them — PREREG's '4 recycled MLC slots' plus headroom) are for
    A1-MLC's per-episode synthetic cues, which `brain.protocol` does not yet shape (no
    mlc.jsonl format is frozen) — kept as a genuinely DYNAMIC, order-of-first-appearance table
    for that upper range only, RAISED in docs/briefs/B1-BUILDER3-REPORT.md as unbuilt/untested
    pending that format.

    THE BUG THIS REPLACED: the original design assigned ALL 18 named slots dynamically, in
    order of first appearance on the tape — including calls made from INSIDE `ArmA1.answer()`,
    which B1-PREREG.md's own control 0e requires to leave `state_sha()` UNCHANGED under
    `learn=False`. Since `answer()` must encode an ASK row's cue to build its query state
    regardless of whether the caller is training or a frozen TEST sitting, a genuinely novel
    mark seen FIRST during a test ask would mutate the (persisted, hashed) slot table as a
    side effect of a call the protocol declares side-effect-free — caught by
    tests/brain/arms_soft/test_arm_a1_conformance.py's own `check_arm` run (`slots` was the
    ONLY one of eight state components that moved, isolated by comparing each component of
    state_sha's input separately rather than trusting the digest alone — #171's law, applied
    to my own instrument). Making the 14 real marks a static, protocol-derived lookup removes
    the mutation entirely for every mark B1 actually uses; only the still-unbuilt MLC range
    keeps the dynamic (and therefore state-mutating-on-first-sight) behaviour, scoped away
    from anything `check_arm` or the six tests will ever exercise before that side-tape format
    exists.
    """

    STATIC_MARKS: tuple = ()  # populated in __init__ from brain.protocol.CUE_MARKS (D14)

    def __init__(self, capacity: int = CUE_DIM):
        from brain.protocol import CUE_MARKS  # local import: keeps this module importable stand-alone

        self.capacity = capacity
        self._static = {m: i for i, m in enumerate(CUE_MARKS)}
        self._dynamic: Dict[str, int] = {}  # MLC's upper range only (RAISED, see docstring)

    def slot_of(self, mark: str) -> int:
        if mark in self._static:
            return self._static[mark]
        if mark not in self._dynamic:
            next_slot = len(self._static) + len(self._dynamic)
            if next_slot >= self.capacity:
                raise StepEncodingError(
                    f"cue vocabulary exceeded its declared {self.capacity} slots at mark {mark!r} "
                    f"(static: {sorted(self._static)}; dynamic: {sorted(self._dynamic)}) — "
                    f"B1-PREREG.md §4 row A1: '> 24 -> RAISED'"
                )
            self._dynamic[mark] = next_slot
        return self._dynamic[mark]

    def to_dict(self) -> Dict[str, int]:
        return dict(self._dynamic)  # the static half needs no persistence: it is CUE_MARKS itself

    @classmethod
    def from_dict(cls, d: Mapping[str, int]) -> "SlotTable":
        t = cls()
        t._dynamic = dict(d)
        return t

    def state_bytes(self) -> bytes:
        # the static half is a constant (never varies across arms or runs) and is excluded on
        # purpose — including it would make every arm's state_sha depend on brain.protocol's
        # CUE_MARKS ordering for no reason; only the DYNAMIC (MLC) half is genuine per-run state.
        return repr(sorted(self._dynamic.items())).encode()


class StepEncoder:
    """Builds the fixed-width (STEP_DIM,) step vectors GrowingGRUEngine.step consumes, from a
    validated tape row and the seed's glance Cache. No learning here — pure, stateless encoding
    except for the SlotTable's persisted cue-slot assignment."""

    def __init__(self, cache: Cache, slots: SlotTable):
        self.cache = cache
        self.slots = slots

    # -- primitive blocks --------------------------------------------------------------------
    def _kind_block(self, kind: str) -> torch.Tensor:
        return _one_hot(KIND_DIM, _KIND_INDEX[kind])

    def _glance_step(self, cache_row: int, glance_index: int, kind: str) -> torch.Tensor:
        feats = self.cache.glances(cache_row)[glance_index]  # (144,) float64
        glance_block = torch.from_numpy(np.asarray(feats, dtype=np.float32))
        idx_block = _one_hot(GLANCE_IDX_DIM, glance_index)
        letter_block = torch.zeros(LETTER_DIM)
        cue_block = torch.zeros(CUE_DIM)
        return torch.cat([glance_block, idx_block, letter_block, cue_block, self._kind_block(kind)])

    def glance_steps(self, cache_row: int, kind: str) -> List[torch.Tensor]:
        return [self._glance_step(cache_row, i, kind) for i in range(GLANCES_PER_ROW)]

    def _letter_step(self, letter_index: int, kind: str) -> torch.Tensor:
        glance_block = torch.zeros(GLANCE_DIM)
        idx_block = torch.zeros(GLANCE_IDX_DIM)
        letter_block = _one_hot(LETTER_DIM, letter_index)
        cue_block = torch.zeros(CUE_DIM)
        return torch.cat([glance_block, idx_block, letter_block, cue_block, self._kind_block(kind)])

    def name_steps(self, name: str, kind: str) -> List[torch.Tensor]:
        steps = []
        for ch in name:
            if ch not in LETTERS:
                raise StepEncodingError(f"name {name!r} carries a non a-z character {ch!r} (§2.3)")
            steps.append(self._letter_step(LETTERS.index(ch), kind))
        steps.append(self._letter_step(len(LETTERS), kind))  # END
        return steps

    def _cue_step(self, mark: str, kind: str) -> torch.Tensor:
        glance_block = torch.zeros(GLANCE_DIM)
        idx_block = torch.zeros(GLANCE_IDX_DIM)
        letter_block = torch.zeros(LETTER_DIM)
        cue_block = _one_hot(CUE_DIM, self.slots.slot_of(mark))
        return torch.cat([glance_block, idx_block, letter_block, cue_block, self._kind_block(kind)])

    def cue_steps(self, cues: Sequence[str], kind: str) -> List[torch.Tensor]:
        return [self._cue_step(m, kind) for m in cues]

    def operand_steps(self, operand: Mapping[str, Any], kind: str) -> List[torch.Tensor]:
        if is_row_operand(operand):
            return self.glance_steps(int(operand["value"]), kind)
        if is_name_operand(operand):
            return self.name_steps(str(operand["value"]), kind)
        raise StepEncodingError(f"unknown operand shape: {operand!r}")

    # -- whole-row decompositions (D12) ------------------------------------------------------
    def teach_steps(self, payload: Mapping[str, Any]) -> List[torch.Tensor]:
        return self.glance_steps(int(payload["glance_row"]), "TEACH") + self.name_steps(str(payload["name"]), "TEACH")

    def ask_steps(self, payload: Mapping[str, Any]) -> List[torch.Tensor]:
        steps = list(self.cue_steps(payload["cues"], "ASK"))
        for op in payload["operands"]:
            steps.extend(self.operand_steps(op, "ASK"))
        return steps

    def candidate_steps(self, candidate_row: int) -> List[torch.Tensor]:
        return self.glance_steps(int(candidate_row), "ASK")


# ───────────────────────── token ids for A1-MA (§4.1) ──────────────────────────────────────────
# "The token ids: the 27 letter-steps, the 24 cue-mark slots, the event kinds, and — for a
# glance step, its glance POSITION 1-5" (B1-PREREG.md §4.1). A declared, stable layout over the
# n_tokens = 27+24+7+5 = 63 ids MemoryAttentionReadout's table E is sized to:
#   [0..26]   = LETTER_DIM (26 letters + END)
#   [27..50]  = CUE_DIM's first 24 slots (both the static CUE_MARKS half and SlotTable's
#               dynamic MLC half share this same 24-wide range — a token id names a SLOT, and
#               the slot table is exactly what makes a slot's meaning stable within one arm)
#   [51..57]  = KIND_DIM (the 7 TAPE_KINDS, in their declared order)
#   [58..62]  = GLANCE_IDX_DIM (5 glance positions)
TOKEN_LETTER_BASE = 0
TOKEN_CUE_BASE = LETTER_DIM
TOKEN_KIND_BASE = TOKEN_CUE_BASE + CUE_DIM
TOKEN_GLANCE_BASE = TOKEN_KIND_BASE + KIND_DIM
N_TOKENS = TOKEN_GLANCE_BASE + GLANCE_IDX_DIM


def token_id_of_step(step: torch.Tensor) -> int:
    """Decode a (STEP_DIM,) step vector back to its token id (A1-MA's lookup key) by reading
    WHICH block the encoder populated — the inverse of StepEncoder's own construction, so a
    step built by any of glance_steps/name_steps/cue_steps decodes to a unique, stable id."""
    glance_idx_block = step[GLANCE_DIM : GLANCE_DIM + GLANCE_IDX_DIM]
    letter_block = step[GLANCE_DIM + GLANCE_IDX_DIM : GLANCE_DIM + GLANCE_IDX_DIM + LETTER_DIM]
    cue_block = step[GLANCE_DIM + GLANCE_IDX_DIM + LETTER_DIM : GLANCE_DIM + GLANCE_IDX_DIM + LETTER_DIM + CUE_DIM]
    if float(glance_idx_block.sum()) > 0:
        return TOKEN_GLANCE_BASE + int(torch.argmax(glance_idx_block))
    if float(letter_block.sum()) > 0:
        return TOKEN_LETTER_BASE + int(torch.argmax(letter_block))
    if float(cue_block.sum()) > 0:
        return TOKEN_CUE_BASE + int(torch.argmax(cue_block))
    kind_block = step[-KIND_DIM:]
    return TOKEN_KIND_BASE + int(torch.argmax(kind_block))  # defensive fallback; no encoder path produces this today
