# edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 22:45 +0400 — W3-0 (docs/G4-WAVE3-CLAUSES.md, docs/G4-PREREG.md §14):
# THE GENERIC REFUSAL, made structural. RUNS is built by READING the code (grepping `declared[`, `in
# self.genome.declared`, `org.g.declared`) — every entry names the real file:function that consumes the
# gene, found by exhaustive grep across creature/ and genome/ (see the builder report's table for the
# grep output this was built from). A gene earns a site ONLY if some line actually reads its presence or
# its value; a site that merely PARSES the gene (genome/machinery.py's parser, which every declared gene
# has by construction) does not count — that would make every declared gene trivially "wired".
#
# Two genes are wired WITHOUT being gated on their own presence (`"FILE" in declared` / `"BELIEF" in
# declared` do not appear anywhere): `genome.predict.file()` and `genome.think.believe()` are called
# UNCONDITIONALLY by creature/mind.py's THINK step whenever a pool item of the matching kind is worked,
# regardless of whether FILE/BELIEF is declared at all. That is a real call site (declaring FILE/BELIEF
# does not silently do nothing — the mechanism they name runs on every life that has THINK), so they are
# wired; the finding for the report is that their declared VALUE is never read (FILE's four field names,
# BELIEF's "clash opens never overwrites" wording carry no parameter today) and BELIEF's own "clash" half
# is additionally unwired per PREREG §14 (wave 3's own job — D-G12/W3-1).
#
# Several genes ARE wired without a `"X" in declared` presence-branch because the behaviour they name is
# unconditional in the body/machinery layer (the same call happens whether or not the gene appears in the
# genome text): BODY, TAPE, HEART, CRASH, WORLD, ASK. Declaring them is documentation of a fact the code
# already guarantees, not a switch — so their declared VALUE is never read either (a HEART line edited to
# "every 60 s" changes nothing; STATUS_PERIOD_S is a body.py constant). Named here rather than treated as
# unwired because the PREREG's own W3-0 contract puts them in "the body's own" table by name (a call site
# genuinely exists), but flagged in the report as "value read: no" — the same class of finding as TRAITS,
# one notch less dangerous only because nothing claims to interpret a NUMBER that in fact does nothing.
"""creature/genes.py — W3-0: the registry of genes the machinery RUNS, and the refusal law built on it.

`RUNS[layer][GENE] = "<file>:<site> — <one-line note>"` for a gene with a real call site, or `None` for a
gene that is declared/parsed but has NO interpreter anywhere (today: only TRAITS — PREREG §12/§14's own
finding, kept as an explicit row rather than a bare absence so the next reader sees WHY, not just a gap).

`unwired(declared)` is the law `Mind.__init__` runs first: any key in a parsed genome's `declared` dict
that names no wired gene (RUNS entry with a non-None site) is named in the refusal.
"""
from __future__ import annotations

from typing import Dict, List, Optional


RUNS: Dict[str, Dict[str, Optional[str]]] = {
    # ---------------------------------------------------------------------------------- the machinery
    "machinery": {
        "CYCLE": "genome/machinery.py:Organism._birth (soft ceiling grow_to*nmax) + genome/sleep.py:cycle (consolidation pass)",
    },
    # ---------------------------------------------------------------------------------------- the body
    # BODY/TAPE/HEART/CRASH/WORLD/ASK: the behaviour each names is unconditional in body.py/tape.py/ask.py
    # (present whether or not the gene is declared) — the site is real, but the declared VALUE is never
    # read (see the module docstring and the builder report's "value read?" column).
    "body": {
        "EXAM": "creature/body.py:Body.start (declared['EXAM']['every'] read; starts the voice/exam thread)",
        "BODY": "creature/body.py:Body/SenseThread (thread wiring is fixed by code; declared['BODY']['threads'] NOT read)",
        "TAPE": "creature/tape.py:Tape.__init__ (root/'tape' hardcoded; declared['TAPE']['path'] NOT read)",
        "HEART": "creature/body.py:STATUS_PERIOD_S=10.0 constant (declared['HEART']['every_s'] NOT read)",
        "CRASH": "creature/body.py:SenseThread.run (journal on restart) + Body._handle_mind_crash (page) — unconditional, declared['CRASH'] value NOT read",
        "WORLD": "creature/body.py:main --maker-period default 5.0 / world_maker.sense period — declared['WORLD'] values NOT read",
        "ASK": "creature/ask.py:answer (the six verbs are hardcoded `if q == ...`; declared['ASK']['verbs'] NOT read)",
    },
    # ---------------------------------------------------------------------------------------- the mind
    "mind": {
        "FAST": "creature/mind.py:Mind.__init__ (Episodes built when declared) + Mind.resume (episodes.npz reloaded)",
        "PREDICT": "creature/mind.py:Mind.__init__ (Predictor built when declared) + Mind.resume (predictor rebuilt against the loaded org)",
        "PARK": "creature/mind.py:Mind.__init__ (Park built when declared)",
        "CURIOSITY": "creature/mind.py:Mind.__init__ (Interests built when declared and genome.curiosity importable)",
        "ARRIVAL": "creature/mind.py:Mind._consume_eye (Organism.new_arrival() called on a never-heard word)",
        "SLEEP": "creature/mind.py:Mind._maybe_sleep (every/replay read) + Mind.resume (_last_sleep_at rebuilt)",
        "THINK": "creature/mind.py:Mind._maybe_think (gated: 'THINK' not in declared -> return; every read otherwise)",
        "FROZEN": "creature/mind.py:Mind.__init__ (declared['FROZEN']['after'] read when 'frozen' in blind — a TWIN-ONLY gene, PREREG §11.1 step 5)",
        "FILE": "creature/mind.py:_think_work (predict_file() called for 'sight' pool items) — called UNGATED by FILE's own presence; declared['FILE'] value NOT read",
        "BELIEF": "creature/mind.py:_think_work (think_laws.believe() called for 'word' pool items, UNGATED by BELIEF's own presence for the call itself; clash_enabled=('BELIEF' in declared) IS gated on it and passed through once believe() accepts the kwarg — W3-1, Builder B, g4-wave3-b)",
        "TRAITS": None,  # PREREG §12/§14: declared but the mind has no TRAITS interpreter yet (wave 3, W3-4: same-cell positives) — the organism does not start.
    },
}


def unwired(declared: Dict[str, dict]) -> List[str]:
    """Every key of a parsed genome's `declared` dict that names no WIRED gene (an entry in RUNS whose
    site is not None) — sorted. A gene RUNS does not mention at all (INDUCE, DEDUCE, SENTENCE, HANDS,
    SURPRISE today; any typo or planted key) is unwired for the same reason TRAITS is: nothing in RUNS
    claims a site for it, so `wired` below never contains it."""
    wired = {gene for layer in RUNS.values() for gene, site in layer.items() if site is not None}
    return sorted(gene for gene in declared if gene not in wired)
