# edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:29 +0400 — BRAIN-IN-BODY (docs/brain/body/INTERFACE-BRAIN-ORGAN.md §4 «THE ORGANS'
# ROAD»; the seat's 20:2x addition: every answer carries `raw` in the offline graders' field names, and every answer row `fix` + `hyps`).
"""creature/organs_road.py — THE ORGANS' ROAD: the scene world's asks answered from the ORGANISM's own memory (its cells, its
sight→words edges, its words ledger, its FAST ring), when the mind has no brain (no BRAIN line, or `--blind brain`). It is the
twin's road (#228: a control must still be able to DO the thing), so it is a real attempt, never a stub — and it is READ-ONLY:
creature/mind.py asserts the organism's hash and the mind's road unchanged around every call (the chat's own law).

Every answer has the SAME digest shape as the brain's (INTERFACE §2's table: `kind`, …) and a `raw` in the offline graders'
field names, so one grader reads both roads:
  point → raw {"point": hyp | None, "none": bool, "none_i": bool}; a phrase word with no cell → {"point": None, "none": None,
          "unheard": [words]}.
  what  → raw {"emit": [words]} ([] = «I don't know»); an unseen pointer → {"emit": None, "uncovered": True}.
  say   → raw {"spoken": [words] | None, "reason": str | None, "target": hyp, "readback_point": None}; an unseen pointer →
          {"spoken": None, "reason": "uncovered", "uncovered": True}.
  why   → raw = the answer itself.

The eye's hypotheses are `brain.scene.eye.hypotheses` (imported lazily: that module pulls brain.world at import, which no genome
without asks should pay for). `pointer` is §3's rule for ONE box; tests/creature/test_brain_mind.py pins it equal to builder A's
once genome/brain.py carries it (`pointer_hypothesis(box, centroid, fix, hyps)`, the seat's addendum 2).
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from genome.questions import why as questions_why, word_cells

CELL_PX = 8          # a fixation cell's side in pixels: GAZE canvas 128 / grid 16 (W.fixation_thing's own arithmetic)
MARGIN = 4           # the box ± 4 px (W.fixation_thing's own margin)
WHY_MAX = 8          # INTERFACE §3 M4: up to 8 episodes
_SCENE_MOMENT = re.compile(r"^sc\d+t(\d{6})$")


def eye_view(g: Dict[str, object]) -> Tuple[List[Tuple[int, int]], np.ndarray, list]:
    """(fix, located (len(fix), F), hypotheses) of one glance dict — the located glances are feats[:len(fix)] (the coarse one,
    when GAZE declares it, is feats[len(fix)] and is not a located glance)."""
    from brain.scene import eye as _eye
    fix = [(int(y), int(x)) for (y, x) in (g.get("fix") or [])]
    if not fix:
        return fix, np.zeros((0, 0)), []
    located = np.stack([np.asarray(v, dtype=np.float64) for v in list(g["feats"])[:len(fix)]], axis=0)
    return fix, located, _eye.hypotheses(fix, located)


def pointer_hypothesis(box: Sequence[int], centroid: Optional[Sequence[float]], fix: Sequence[Tuple[int, int]], hyps,
                       cell_px: int = CELL_PX, margin: int = MARGIN) -> Optional[int]:
    """INTERFACE §3 «The pointer» (with the seat's addendum 2: the ask carries the pointed thing's ink `centroid` [cy, cx]):
    the hypothesis with the most of its fixations inside the box ± 4 px (a fixation cell's centre pixel is cell · 8 + 4;
    half-open, W.fixation_thing's own test); a tie → the hypothesis whose mean position is nearest (cy / 8 − 0.5, cx / 8 − 0.5)
    (marks.thing_hypothesis's rule), then the lower index; none inside → None («unseen»). `centroid` None (an ask without
    one) → the box's centre stands in for it."""
    top, left, side = (int(v) for v in box)
    counts = []
    for h in hyps:
        n = 0
        for i in h.members:
            py, px = fix[i][0] * cell_px + cell_px // 2, fix[i][1] * cell_px + cell_px // 2
            if top - margin <= py < top + side + margin and left - margin <= px < left + side + margin:
                n += 1
        counts.append(n)
    if not counts or max(counts) == 0:
        return None
    best = [i for i, c in enumerate(counts) if c == max(counts)]
    if len(best) == 1:
        return best[0]
    cy_px, cx_px = (float(centroid[0]), float(centroid[1])) if centroid is not None else (top + side / 2.0, left + side / 2.0)
    cy, cx = cy_px / cell_px - 0.5, cx_px / cell_px - 0.5
    return min(best, key=lambda i: ((hyps[i].pos[0] - cy) ** 2 + (hyps[i].pos[1] - cx) ** 2, i))


def _pointer():
    """The ONE pointer rule: genome/brain.py's (builder A's organ) when it is on the tree — INTERFACE §4 «import it from
    genome/brain.py» — else this module's copy; tests/creature/test_brain_mind.py pins the two equal on 400 random cases."""
    try:
        from genome.brain import pointer_hypothesis as p
        return p
    except ImportError:
        return pointer_hypothesis


def _one_name(r: Dict[str, object], Lw: Dict[int, set]) -> Optional[str]:
    """The answer cell's own name: exactly one non-empty word in the words ledger, else None."""
    if r.get("cell") is None:
        return None
    ws = Lw.get(int(r["cell"]), set())
    if len(ws) == 1:
        w = next(iter(ws))
        return w or None
    return None


def _none() -> Dict[str, object]:
    return {"kind": "none", "raw": {"point": None, "none": True, "none_i": True}}


def answer_point(org, Lw: Dict[int, set], payload: Dict[str, object], fix, located, hyps) -> Tuple[Dict[str, object], Dict[str, object]]:
    """§4: each hypothesis scored by the summed edge between its member glances and each phrase word's cell (Organism.edge_many,
    the best of the word's own cells); the best hypothesis, «none» when every edge is 0; a phrase word the organism has no cell
    for → «unheard» (the seat's 20:2x rule). A tie → marks.tie_rng(test_seed, item), the brain's own tie generator."""
    phrase = [str(w) for w in (payload.get("phrase") or [])]
    cells = {w: word_cells(org, Lw, w) for w in phrase}
    detail: Dict[str, object] = {"cells": {w: len(cells[w]) for w in phrase}}
    unheard = [w for w in phrase if not cells[w]]
    if unheard:
        return {"kind": "unheard", "words": unheard, "raw": {"point": None, "none": None, "unheard": unheard}}, detail
    if not phrase or not hyps:
        detail["scores"] = []
        return _none(), detail
    # edit: Claude (Fable 5.1, the seat), 2026-09-29 13:13 +0400 — PREREG-WORD-ROAD §4 mark P (the co-signer's OPEN POINT 1): under the gene HEAR
    # the answer's DETAIL carries each phrase word's OWN score per hypothesis, unrounded, so the gate's reader can point AGAIN
    # by any part of the phrase (the shape word alone) in the SAME cells — a paired control inside one organism. Read-only, in
    # the detail alone: the answer, its `raw` and the organism are what they were; without the line the detail is what it was.
    scores = []
    by_word: Optional[Dict[str, List[float]]] = {w: [] for w in phrase} if "HEAR" in org.g.declared else None
    for h in hyps:
        xs = [located[i] for i in h.members]
        vals = [max(org.edge_many("sight", xs, c) for c in cells[w]) for w in phrase]
        scores.append(float(sum(vals)))
        if by_word is not None:
            for w, v in zip(phrase, vals):
                by_word[w].append(float(v))
    detail["scores"] = [round(s, 6) for s in scores]
    if by_word is not None:
        detail["scores_by_word"] = by_word
    top = max(scores)
    if top <= 0.0:
        return _none(), detail
    best = [k for k, s in enumerate(scores) if s == top]
    if len(best) == 1:
        k = best[0]
    else:
        from brain.scene import marks as _marks
        k = best[int(_marks.tie_rng(int(payload["test_seed"]), str(payload["item"])).integers(len(best)))]
        detail["tie"] = best
    h = hyps[k]
    return ({"kind": "thing", "hyp": int(k), "pos": [float(h.pos[0]), float(h.pos[1])],
             "fix": [[int(fix[i][0]), int(fix[i][1])] for i in h.members],
             "raw": {"point": int(k), "none": False, "none_i": False}}, detail)


def _pointed(payload, fix, located, hyps):
    box = payload.get("box")
    if box is None or not hyps:
        return None, None
    k = _pointer()(box, payload.get("centroid"), fix, hyps)
    return k, (None if k is None else [located[i] for i in hyps[k].members])


def answer_what(org, Lw, payload, fix, located, hyps) -> Tuple[Dict[str, object], Dict[str, object]]:
    """§4: Organism.recall_many over the pointer's member glances (the ANSWER / ABSTAIN genes inside it), the words ledger's
    one name → «words»; any abstain or a cell that is not one word → «unknown»; no fixation in the box → «unseen»."""
    k, xs = _pointed(payload, fix, located, hyps)
    if k is None:
        return {"kind": "unseen", "raw": {"emit": None, "uncovered": True}}, {"target": None}
    r = org.recall_many("sight", xs)
    name = _one_name(r, Lw)
    detail = {"target": int(k), "reason": r.get("reason"), "grade": r.get("grade")}
    if name is None:
        return {"kind": "unknown", "raw": {"emit": []}}, detail
    return {"kind": "words", "words": [name], "raw": {"emit": [name]}}, detail


def answer_say(org, Lw, payload, fix, located, hyps) -> Tuple[Dict[str, object], Dict[str, object]]:
    """§4: as `what`, said: one name → «phrase»; else «declined» with the recall's own reason («not_one_word» when the answer
    cell names no single word); no fixation in the box → «unseen»."""
    k, xs = _pointed(payload, fix, located, hyps)
    if k is None:
        return {"kind": "unseen", "raw": {"spoken": None, "reason": "uncovered", "uncovered": True}}, {"target": None}
    r = org.recall_many("sight", xs)
    name = _one_name(r, Lw)
    detail = {"target": int(k), "reason": r.get("reason"), "grade": r.get("grade")}
    if name is None:
        reason = str(r.get("reason")) if r.get("cell") is None else "not_one_word"
        return ({"kind": "declined", "reason": reason,
                 "raw": {"spoken": None, "reason": reason, "target": int(k), "readback_point": None}}, detail)
    return ({"kind": "phrase", "words": [name],
             "raw": {"spoken": [name], "reason": None, "target": int(k), "readback_point": None}}, detail)


def _scene_of(tape_moment: Optional[str]) -> Optional[int]:
    m = _SCENE_MOMENT.match(tape_moment or "")
    return int(m.group(1)) if m else None


def answer_why(org, ledgers, episodes, payload) -> Tuple[Dict[str, object], Dict[str, object]]:
    """§4: «unknown» unless ASK's own `why` road (genome.questions.why) holds the word — a cell born on it alone or a FAST
    episode whose word it is. Else «because»: up to 8 of those episodes, earliest first (the organs keep no responsibility),
    each its tape moment, the scene parsed from it, and `pos` None (the ring keeps glance 0's window, `where`, not a
    hypothesis position — carried beside as `where`); rule.over = the cited moments, rule.band None (no band in the organs)."""
    word = str(payload.get("word") or "")
    w = questions_why(org, ledgers, episodes, word)
    detail = {"cells": len(w["cells"]), "episodes": len(w["episodes"]), "edges": len(w["edges"])}
    if not w["cells"] and not w["episodes"]:
        ans: Dict[str, object] = {"kind": "unknown"}
    else:
        eps = []
        for eid in w["episodes"][:WHY_MAX]:
            e = episodes.get(int(eid)) if episodes is not None else None
            if e is None:
                continue
            eps.append({"moment": e["tape_moment"], "scene": _scene_of(e["tape_moment"]), "pos": None,
                        "where": (None if e["where"] is None else [int(e["where"][0]), int(e["where"][1])])})
        ans = {"kind": "because", "word": word, "episodes": eps, "rule": {"over": [e["moment"] for e in eps], "band": None}}
    ans["raw"] = {k: v for k, v in ans.items()}
    return ans, detail
