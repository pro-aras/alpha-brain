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
# BODY, TAPE, HEART, CRASH, WORLD, ASK are wired without a `"X" in declared` presence-branch guarding the
# CALL SITE itself (the same call happens whether or not the gene appears in the genome text) — but as of
# C1 (docs/G4-WAVE3-CLAUSES.md W3-0b) each one's declared VALUE IS now read when the gene is present, and
# the prior default (the hardcoded constant/behaviour) is kept exactly when it is absent: `_check_body_
# threads`/`_resolve_tape_dir`/`_status_period_s`/`_crash_policy` in creature/body.py + creature/tape.py,
# and the WORLD-driven maker period/window/folder-dir also in creature/body.py:main; `_ask_refusal` in
# creature/ask.py. TAPE and CRASH's own grammar in genome/machinery.py is still a single fixed-string
# match each (TAPE takes any path but CRASH accepts only the literal "sense restart journal; mind page",
# and ASK only the literal six-verb line) — the READING side is wired and tested against hand-built
# `declared` values beyond what today's parser can produce; raised in the builder report, not worked
# around (not this builder's file).
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
    # edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:08 +0400 — C1.7 (docs/G4-WAVE3-CLAUSES.md
    # W3-0b): BODY/TAPE/HEART/CRASH/WORLD/ASK now READ their declared values (each gated on the gene's
    # own presence -- undeclared keeps the exact prior default, a toy in each of
    # tests/creature/test_gene_values.py, test_world_pin.py, test_world_maker.py proves the change).
    "body": {
        "EXAM": "creature/body.py:Body.start (declared['EXAM']['every'] read; starts the voice/exam thread)",
        "BODY": "creature/body.py:_check_body_threads, read at Body.__init__ (declared['BODY']['threads'] validated against the known five; refuses naming an unknown thread or a missing 'mind')",
        "TAPE": "creature/tape.py:_resolve_tape_dir, read at Body.__init__ / creature/body.py:Body.start's read_tape (declared['TAPE']['path'] resolves the tape directory)",
        "HEART": "creature/body.py:Body.__init__ -> Body._status_loop (declared['HEART']['every_s'] read into self._status_period_s, the STATUS write period)",
        "CRASH": "creature/body.py:_crash_policy, read at Body.__init__ -> SenseThread.run (restart) + Body._handle_mind_crash (page) — declared['CRASH']'s two sub-facts gate each behaviour",
        "WORLD": "creature/body.py:main (declared['WORLD']['drawn_every_s']/['arrival_every_h'] read into world_maker.sense's period/window_seconds; ['folder'] arms creature/senses/folder.py behind FOLDER_DOOR_GATED)",
        "ASK": "creature/ask.py:_ask_refusal, read at answer() (declared['ASK']['verbs'] read; a verb outside it is refused by name instead of reaching the hardcoded `if q == ...` branches)",
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
        # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-2 (docs/G4-WAVE3-CLAUSES.md):
        # two rows added, ONLY these two, nothing else in this file touched (Builder C owns the body rows
        # concurrently). Both are real call sites: _think_pool builds 'rule' pool items by calling
        # think_laws.induce()/deduce() directly (gated on their OWN declared presence — an undeclared
        # INDUCE/DEDUCE never even computes a candidate rule), and _think_work's new 'rule' branch files
        # them through FILE (gated on FILE's own declared presence too, W3-0b — induce()/deduce() call
        # predict.file() internally, so without FILE the mind dead-ends BEFORE calling them).
        "INDUCE": "creature/mind.py:_think_pool/_think_work (think_laws.induce() called for words with >= k episodes; filed as 'rule' items, scored at their due canvas)",
        "DEDUCE": "creature/mind.py:_think_pool/_think_work (think_laws.deduce() called over standing beliefs; filed as 'rule' items, scored at their due canvas)",
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
