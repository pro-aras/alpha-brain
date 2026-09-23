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

edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:15 +0400 — ALPHA4-G.md task 4 (docs/ALPHA4-PREREG.md
§2/§3): a SECOND form, `CYCLE consolidate when redundant > <share> of alive` (declared["CYCLE"] == {"share":
f}, distinct from the OLD form's {"grow_to": f} — genome/machinery.py's own parser distinguishes them by
which key is present, never a "kind" tag, so the old form's declared dict stays byte-for-byte what
test_parse_g4.py:104 already pins). The trigger is `births_refused_redundant SINCE THE LAST CYCLE / alive
cells > share` — under GROW there is no cap to grow toward, so the cycle fires on WASTE (a cell that would
have been born error-redundant and was refused, §11 amendment 4's own counter) rather than on fullness.
`org._cycle_baseline_redundant` (machinery.py's Organism.__init__, a plain attribute, never self.c/hashed —
see its own comment) is the count of births_refused_redundant AS OF the last time THIS cycle actually ran;
reset to the current count only when a cycle fires, mirroring how the old form's own ceiling naturally
"resets" (ALIVE drops back under grow_to*NMAX once a merge pass runs). Persisted across save/load in `meta`
(never self.c) so a resumed life's trigger doesn't fire on the WHOLE history the moment it resumes (#233's
class: an unrefreshed baseline).
"""
from __future__ import annotations

from typing import Dict

import numpy as np

from .machinery import Organism


def sleep(org: Organism, episodes, n: int, words: bool = True) -> Dict[str, object]:
    """Replays the `n` most surprising LIVE episodes in `episodes` (genome/fast.py's Episodes) as
    ordinary moments. An episode the ring has since overwritten (most_surprising ranked it, then it fell
    off before replay) is skipped, never an error. Returns counts measured against the organism's own
    state before/after — births/merges/prunes are read from Organism.c, so this never double-counts
    anything moment() itself would not have counted.

    edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:34 +0400 — A4L-VOICE task 3: `words=False` (the mind's
    `--blind ear` twin only) replays each episode's glance with NO word (`Organism.moment(x_s, None)`): «the words area never
    lights» holds in sleep too (an episode's blank-word encoding would otherwise light a blank word cell and wire sight to
    it). Default True: byte-for-byte the old replay."""
    ids = episodes.most_surprising(n)
    births_before = org.sight.n + org.words.n
    merges_before = org.c["cells_merged_sight"] + org.c["cells_merged_words"]
    prunes_before = org.c["edges_pruned"]
    replayed = 0
    for eid in ids:
        rec = episodes.get(eid)
        if rec is None:
            continue
        org.moment(rec["x_s"], rec["x_w"] if words else None)
        replayed += 1
    return {
        "replayed": replayed,
        "births": (org.sight.n + org.words.n) - births_before,
        "merged": (org.c["cells_merged_sight"] + org.c["cells_merged_words"]) - merges_before,
        "pruned": org.c["edges_pruned"] - prunes_before,
    }


def cycle(org: Organism) -> bool:
    """CYCLE grow to <f> nmax then consolidate | CYCLE consolidate when redundant > <share> of alive.
    Requires the gene DECLARED (org.g.declared['CYCLE']) — a life whose genome never declares CYCLE
    returns False immediately and touches nothing (the pin: G1.genome/G4-skeleton.genome declare no G4
    gene at all). Consolidates (a full merge pass, then a full prune pass) only when the declared form's
    own trigger fires; returns True iff it ran."""
    if "CYCLE" not in org.g.declared:
        return False
    cyc = org.g.declared["CYCLE"]
    if "grow_to" in cyc:
        ceiling = float(cyc["grow_to"]) * org.g.nmax
        if org.total_cells() < ceiling:
            return False
    else:
        # ALPHA4-G task 4: the redundant-share form — births_refused_redundant SINCE THE LAST CYCLE, over
        # the current alive-cell count. `alive == 0` (a life with nothing born yet) never divides by zero
        # and never triggers (there is nothing to consolidate).
        share = float(cyc["share"])
        alive = org.total_cells()
        since_last = org.c["births_refused_redundant"] - org._cycle_baseline_redundant
        if alive == 0 or since_last / alive <= share:
            return False
    for area, axis in ((org.sight, 0), (org.words, 1)):
        org._merge(area, list(area.alive_ids()), axis=axis)
    org._prune(list(org.sight.alive_ids()), list(org.words.alive_ids()))
    # ALPHA4-G task 4: reset the redundant-share baseline only on an ACTUAL run (either form) — a cycle
    # that never fires leaves the "since the last cycle" window open, exactly like the old form's own
    # ceiling naturally staying crossed until a merge pass actually lowers ALIVE back under it.
    org._cycle_baseline_redundant = org.c["births_refused_redundant"]
    return True
