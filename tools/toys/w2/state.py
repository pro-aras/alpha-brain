"""tools/toys/w2/state.py — PREREG-W2 §3 item 2: the offline STATE labels and the SHARED state row (the CODE-F six).

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:44 +0400 — new file, written after tests/tools/test_w2_record.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 item 2 and the builder's declared conventions (the board
NOTE of this lane): the labels are the record's OWN, never assumed.

The six coordinates (the toy's CODE-F on the real record):
- **doubt** = the journal's own per-hyp `held` list at the LEADING hyp is empty (held[lead] == []; 1.0 while the turn has
  not acted — the record's own warm-up, the toy's 90 warm-up moments' analog).
- **young** = the lead word's reference-census count BEFORE the canvas is < 3 (the learner's own `meetings < p_from`).
- **ask_prev** = the previous scene canvas's act was ASK (turn.ask non-null; the ACT, not the label).
- **say_prev** = the previous scene canvas's act was SAY (turn.say non-null — independent of ask_prev: a real turn can do
  both, PREREG-T-L4 §2.3's own note).
- **cnt** = ln(1 + the lead word's count before the canvas).
- **fit** = the canvas's say.readback as recorded, else 0.0 (the builder's declared convention for the record's own
  continuous shadow; the flags carry the labels).

The LEAD: the mentor's referent when the mentor names one (mapped to the journal's hyp by the pointer rule's own
arithmetic, genome/brain.py:pointer_hypothesis), else the turn's leading hypothesis (the say's hyp, else order[0]). The
lead WORD is the lead thing's head noun — the referent's shape, else the parent's last word (every NP ends in the shape).

held_two_ways: G-STATE's two-way read at sampled canvases — read 1 the journal's `held` (any hyp empty), read 2 the act
(ask non-null), equal by the organism's own ask rule (it asks about the FIRST thing whose held is empty) at every canvas
the turn acted, n of n.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from tools.toys.w2 import census as C
from tools.toys.w2.record import SceneCanvas

CELL_PX = 8


def _pointer(box: Sequence[float], fix: Sequence[Sequence[int]], members: Sequence[Sequence[int]]) -> Optional[int]:
    """The pointer rule's own arithmetic over (fix cells, hyp members): the hyp with the most of its fixations inside the
    box ± 4 px (a fixation cell's centre pixel), half-open; a tie → the lower index; none → None."""
    top, left, side = (float(v) for v in box)
    counts = []
    for m in members:
        c = 0
        for f in m:
            y, x = int(fix[int(f)][0]), int(fix[int(f)][1])
            cy, cx = y * CELL_PX + 4, x * CELL_PX + 4
            if top - 4 <= cy < top + side + 4 and left - 4 <= cx < left + side + 4:
                c += 1
        counts.append(c)
    best = max(counts, default=0)
    return counts.index(best) if best > 0 else None


def lead(canvas: SceneCanvas, referent_thing: Optional[int]) -> Tuple[Optional[int], str]:
    """(lead hyp index, lead word). The mentor's referent when given; else the turn's leading hyp and the parent's head noun."""
    if referent_thing is not None:
        t = canvas.things[referent_thing]
        hyp = _pointer((t.top, t.left, t.side), canvas.fix, canvas.hyps)
        return hyp, t.shape
    turn = canvas.turn
    say = turn.get("say")
    if say is not None:
        return int(say["hyp"]), canvas.words[-1]
    order = turn.get("order") or [0]
    return int(order[0]), canvas.words[-1]


def doubt_of(canvas: SceneCanvas, lead_hyp: Optional[int]) -> float:
    held = canvas.turn.get("held")
    if not held:
        return 1.0                                    # the turn never acted or held nothing: the record's own warm-up
    if lead_hyp is None or lead_hyp >= len(held):
        return 1.0
    return 1.0 if held[lead_hyp] == [] else 0.0


def state_of(canvases: Sequence[SceneCanvas], census: Sequence[Dict[str, int]], i: int,
             referent_thing: Optional[int] = None) -> np.ndarray:
    """The CODE-F six for canvas i: (doubt, young, ask_prev, say_prev, cnt, fit)."""
    c = canvases[i]
    lead_hyp, lead_word = lead(c, referent_thing)
    doubt = doubt_of(c, lead_hyp)
    m = census[i].get(lead_word, 0)
    young = 1.0 if m < 3 else 0.0
    ask_prev = 1.0 if (i > 0 and canvases[i - 1].turn.get("ask") is not None) else 0.0
    say_prev = 1.0 if (i > 0 and canvases[i - 1].turn.get("say") is not None) else 0.0
    say = c.turn.get("say")
    fit = float(say.get("readback", 0.0)) if say is not None else 0.0
    return np.array([doubt, young, ask_prev, say_prev, math.log1p(m), fit], dtype=np.float64)


def labels_of(canvases: Sequence[SceneCanvas], census: Sequence[Dict[str, int]], i: int,
              referent_thing: Optional[int] = None) -> Dict[str, int]:
    s = state_of(canvases, census, i, referent_thing)
    return {"doubt": int(s[0]), "young": int(s[1]), "ask_prev": int(s[2])}


def held_two_ways(canvases: Sequence[SceneCanvas], census, every: int = 25) -> Tuple[List[int], List[int]]:
    """G-STATE's two-way read at every `every`-th canvas whose turn acted (reason null): read 1 the journal's held (any
    hyp empty), read 2 the act (ask non-null). The two aligned lists must be equal (the organism's own ask rule)."""
    read_held: List[int] = []
    read_act: List[int] = []
    for c in canvases:
        if c.order % every:
            continue
        turn = c.turn
        if turn.get("reason") is not None:
            continue
        held = turn.get("held") or []
        read_held.append(1 if any(h == [] for h in held) else 0)
        read_act.append(1 if turn.get("ask") is not None else 0)
    return read_held, read_act
