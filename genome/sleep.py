"""sleep.py — SLEEP + CYCLE: complementary systems (fast -> replay -> slow), and the cap that becomes a
cycle (G4 §3 B7; docs/G4-DESIGN.md row 3d, row 7 — E46b/Alpha 2 organs/sleep.py's cursor discipline,
D41/#227, reimplemented minimal).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 22:35 +0400 — B7 (docs/briefs/G4-BUILDER-B-GENES.md).

SLEEP's law: replay the `n` MOST SURPRISING live episodes (FAST's own ranking, genome/fast.py's
Episodes.most_surprising) as ordinary moments — full HEBB/DELTA/PRUNE/MERGE, the SAME law a live moment
runs (Organism.moment, untouched); a replay is not exempt from BUDGET/NMAX and does not advance `org.t`
beyond what moment() itself advances (SCALE can fire from a replay exactly as from a live one).

CYCLE's law: `_birth`'s new soft ceiling (machinery.py, this task) refuses once ALIVE cells reach
`grow_to * NMAX` — for a genome that declares CYCLE only. `cycle(org)` is what LIFTS that ceiling: a
merge pass over every alive cell (not just one moment's winners) plus a matching full prune pass. MERGE
lowers the ALIVE count directly (it never touches `area.n`, the ever-born count), so births resume with
FRESH ids once the alive count drops back under the ceiling — #227's law (never prune/shrink by disuse)
still holds: this consolidates only what is REDUNDANT (MERGE's own cos>THETA_M same-answer law) or WRONG
(PRUNE's own w<floor-after-N-chances law), nothing here ages a cell out for being merely unused.
"""
from __future__ import annotations

from typing import Dict

import numpy as np

from .machinery import Organism


def sleep(org: Organism, episodes, n: int) -> Dict[str, object]:
    """Replays the `n` most surprising LIVE episodes in `episodes` (genome/fast.py's Episodes) as
    ordinary moments. An episode the ring has since overwritten (most_surprising ranked it, then it fell
    off before replay) is skipped, never an error. Returns counts measured against the organism's own
    state before/after — births/merges/prunes are read from Organism.c, so this never double-counts
    anything moment() itself would not have counted."""
    ids = episodes.most_surprising(n)
    births_before = org.sight.n + org.words.n
    merges_before = org.c["cells_merged_sight"] + org.c["cells_merged_words"]
    prunes_before = org.c["edges_pruned"]
    replayed = 0
    for eid in ids:
        rec = episodes.get(eid)
        if rec is None:
            continue
        org.moment(rec["x_s"], rec["x_w"])
        replayed += 1
    return {
        "replayed": replayed,
        "births": (org.sight.n + org.words.n) - births_before,
        "merged": (org.c["cells_merged_sight"] + org.c["cells_merged_words"]) - merges_before,
        "pruned": org.c["edges_pruned"] - prunes_before,
    }


def cycle(org: Organism) -> bool:
    """CYCLE grow to <f> nmax then consolidate. Requires the gene DECLARED (org.g.declared['CYCLE']) —
    a life whose genome never declares CYCLE returns False immediately and touches nothing (the pin:
    G1.genome/G4-skeleton.genome declare no G4 gene at all). Consolidates (a full merge pass, then a
    full prune pass) only when total ALIVE cells have reached grow_to*NMAX; returns True iff it ran."""
    if "CYCLE" not in org.g.declared:
        return False
    grow_to = float(org.g.declared["CYCLE"]["grow_to"])
    ceiling = grow_to * org.g.nmax
    if org.total_cells() < ceiling:
        return False
    for area, axis in ((org.sight, 0), (org.words, 1)):
        org._merge(area, list(area.alive_ids()), axis=axis)
    org._prune(list(org.sight.alive_ids()), list(org.words.alive_ids()))
    return True
