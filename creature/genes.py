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
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:55 +0400 — ALPHA4-G.md task 4
        # (docs/ALPHA4-PREREG.md §2/§3): the description text updated for CYCLE's SECOND form (redundant-
        # share, `declared["CYCLE"] == {"share": f}` — distinguished from the old {"grow_to": f} by which
        # key is present, genome/machinery.py's own parser comment) — the site itself (both branches) is
        # unchanged, so this row's "wired" status (non-None) was already correct; only the words move.
        "CYCLE": "genome/machinery.py:Organism._birth (soft ceiling grow_to*nmax, the OLD form only) + genome/sleep.py:cycle "
                 "(consolidation pass; the redundant-share form's own trigger, births_refused_redundant since the last cycle / alive)",
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:55 +0400 — ALPHA4-G.md task 1
        # (docs/ALPHA4-PREREG.md §2/§3, his 00:17 word «no cap»): GROW unbounded's own row — two real call
        # sites, both gated on `"GROW" in declared` (an undeclared GROW never touches area capacity beyond
        # genome.nmax, never grows W/mask/strikes beyond it either — the NMAX road is byte-for-byte
        # untouched, the negative control test_grow_mechanics.py:TestInitialCapacity pins).
        "GROW": "genome/machinery.py:Organism.__init__ (Area/W initial capacity) + Organism._birth (Area.grow()'s doubling, "
                "Organism._grow_W()'s fixed +2048 chunks — never a births_refused_nmax refusal)",
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:32 +0400 — L-6 (docs/briefs/LIFE-A-ANSWER-SELF.md
        # #1/#2): THRESH's own consumer is Organism.moment's push + Organism.own_floor (both gated on
        # `self.sight.own_band is not None`, itself gated on THRESH's own declared presence at __init__); ANSWER's
        # is Organism.recall/recall_many's grade/own_floor/resembles_cell computation (gated on "ANSWER" in
        # declared, side=="sight" only -- own_band tracks sight cells, and `genome/think.py:_nearest_in`'s
        # algorithm -- the nearest ALIVE sight cell by raw cosine -- is mirrored inline in machinery.py rather
        # than imported, since genome/think.py imports machinery.Organism and an import the other way would be
        # circular; raised in the report, not silently substituted).
        "THRESH": "genome/machinery.py:Organism.moment (the own-band push) + Organism.own_floor (its p5)",
        "ANSWER": "genome/machinery.py:Organism.recall/recall_many (grade/own_floor/resembles_cell on the sight side)",
    },
    # ---------------------------------------------------------------------------------------- the body
    # edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:08 +0400 — C1.7 (docs/G4-WAVE3-CLAUSES.md
    # W3-0b): BODY/TAPE/HEART/CRASH/WORLD/ASK now READ their declared values (each gated on the gene's
    # own presence -- undeclared keeps the exact prior default, a toy in each of
    # tests/creature/test_gene_values.py, test_world_pin.py, test_world_maker.py proves the change).
    "body": {
        "EXAM": "creature/body.py:Body.start (declared['EXAM']['every'] read; starts the voice/exam thread)",
        "BODY": "creature/body.py:_check_body_threads, read at Body.__init__ (declared['BODY']['threads'] validated against the known six — 'think' added by LIFE builder E, L-5; refuses naming an unknown thread or a missing 'mind')",
        "TAPE": "creature/tape.py:_resolve_tape_dir, read at Body.__init__ / creature/body.py:Body.start's read_tape (declared['TAPE']['path'] resolves the tape directory)",
        "HEART": "creature/body.py:Body.__init__ -> Body._status_loop (declared['HEART']['every_s'] read into self._status_period_s, the STATUS write period)",
        "CRASH": "creature/body.py:_crash_policy, read at Body.__init__ -> SenseThread.run (restart) + Body._handle_mind_crash (page) — declared['CRASH']'s two sub-facts gate each behaviour",
        "WORLD": "creature/body.py:main (declared['WORLD']['drawn_every_s']/['arrival_every_h'] read into world_maker.sense's period/window_seconds; ['folder'] arms creature/senses/folder.py behind FOLDER_DOOR_GATED)",
        "ASK": "creature/ask.py:_ask_refusal, read at answer() (declared['ASK']['verbs'] read; a verb outside it is refused by name instead of reaching the hardcoded `if q == ...` branches)",
        # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K (docs/briefs/G5-K-ACTS-OUTCOME-SIT-BODY.md):
        # SIT and SENSE_BODY are the two body-side rows (sense threads, gated on their own declared presence at
        # Body.start — the same C1.7 pattern EXAM/WORLD/ASK already use).
        "SIT": "creature/body.py:Body.start (declared['SIT']['every'] read; starts the sit-publishing sense thread) + creature/senses/sit.py:sense (the canvas-cadence check against state/ledger.json, folder.py's own pattern; publishes the latest exam file's score)",
        "SENSE_BODY": "creature/body.py:Body.start (declared['SENSE_BODY']['period_s']/['fields'] read; starts the body-sense thread) + creature/senses/body_sense.py:sense (STATUS.json's own numbers republished onto the tape every period_s)",
        # edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:0x +0400 — G5-L brief: WORLD's second shape
        # (`WORLD game ...`, stored under its own declared key so it never clobbers declared['WORLD']'s
        # "drawn" dict). Read at creature/body.py:main, exactly like WORLD's own row above, gated behind
        # creature/senses/game.py's GAME_DOOR_GATED constant (the same "a genome line arms nothing until
        # the code exists" discipline C2/C3 used for the folder door).
        "WORLD_GAME": "creature/body.py:main (declared['WORLD_GAME'] read; arms creature/senses/game.py behind GAME_DOOR_GATED)",
    },
    # ---------------------------------------------------------------------------------------- the mind
    "mind": {
        "FAST": "creature/mind.py:Mind.__init__ (Episodes built when declared) + Mind.resume (episodes.npz reloaded)",
        "PREDICT": "creature/mind.py:Mind.__init__ (Predictor built when declared) + Mind.resume (predictor rebuilt against the loaded org)",
        "PARK": "creature/mind.py:Mind.__init__ (Park built when declared)",
        "CURIOSITY": "creature/mind.py:Mind.__init__ (Interests built when declared and genome.curiosity importable)",
        "ARRIVAL": "creature/mind.py:Mind._consume_eye (Organism.new_arrival() called on a never-heard word)",
        "SLEEP": "creature/mind.py:Mind._maybe_sleep (every/replay read) + Mind.resume (_last_sleep_at rebuilt)",
        "THINK": "creature/mind.py:Mind._maybe_think (gated: 'THINK' not in declared -> return; every read otherwise). declared['THINK']['threaded'] (L-5, the '; on its own thread; lands next boundary' tail) additionally gates Mind._maybe_think_threaded/_think_apply_pending/_think_apply_plan + creature/think_thread.py's frozen-copy/decide() -- absent, byte-identical to before this gene's tail existed",
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
        # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K: ACT/OUTCOME are the mind-side rows.
        # Two real call sites each (Mind.__init__ builds state; Mind._consume_outcome/_consume_sit/_think_pool/
        # _think_work read the declared value or act on the row) — the same two-site shape PREDICT/FAST already use.
        "ACT": "creature/mind.py:Mind._record_reflex (declared['ACT']['verbs'] read; an outcome/sit row's act tagged in/out of the declared vocabulary)",
        "OUTCOME": "creature/mind.py:Mind.__init__ (self.outcome_episodes built) + Mind._consume_outcome/_record_reflex (residual computed via a per-act running expectation; written as a reflex episode, ranked by Episodes.most_surprising) + Mind._think_pool/_think_work ('outcome' pool kind)",
        # edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400 — G-EYE-1/G-MIND-1 (docs/briefs/G5-I-SEAM-DELIVER-MOMENT.md):
        # two rows, both real call sites, gated on their OWN declared presence (an undeclared DELIVER never computes seam0; an
        # undeclared MOMENT never passes it to Episodes.write). Neither writes into x_s/x_w (the parity test proves it).
        "DELIVER": "creature/mind.py:Mind._consume_eye ('deliver_on' gates computing seam0 — where/when/act/source/glance — from the eye's own glance windows + the tape row, and gates the journal row's extra keys)",
        "MOMENT": "creature/mind.py:Mind._consume_eye ('moment_on' gates whether seam0 is passed to Episodes.write) + genome/fast.py:Episodes (the where/when/act/source/glance columns, get(), nearest_where(), save()/load())",
        # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:35 +0400 — G-EYE-2/BIND (docs/briefs/G5-J-BIND-COLOUR-RETINA.md):
        # the real call site is _bind_pool() (module-level, top of creature/mind.py) + its use in Mind._consume_eye,
        # gated on "BIND" in declared, both branches (word-bearing and sight-only).
        "BIND": "creature/mind.py:_bind_pool + Mind._consume_eye (org_feats = _bind_pool(g['feats']) when declared; org.moment/moment_sight called once per canvas instead of once per glance)",
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10/L-11 (docs/briefs/LIFE-C-QUESTION-SENTENCE.md):
        # three rows, real call sites each. SENTENCE was previously declared-and-parsed with NO consumer (the
        # unreachable "is near" clause, MIND-THINKING-LANGUAGE.md §4.7); it is now wired against the new co-occurrence
        # definition, and its OLD line no longer parses (genome/machinery.py's own regex replaced, not extended).
        "SENTENCE": "creature/mind.py:_think_pool/_think_work ('frame' pool items via genome.sentence.find_frames() over episodes with >=2 words_in_instant; filed through FILE; _score_due_predictions grades a frame when w1 recurs, judged by the mind's own recall(sight) against w2's word-cell)",
        "QUESTION": "creature/mind.py:_maybe_ask (a want -- a parked wordless sight, a rule/frame that failed once, a belief clash, or PARK actually parking one -- writes ONE run/ask/out/q-<n>.json row; ASKED.json ledger dedupes) + creature/world_maker.py:sense (the door polls ask/out, answers a what-is on a canvas it drew by showing the thing again with its word)",
        "MOUTH": "creature/mind.py:_maybe_say (a filed, CITED frame whose w1 is in the current instant's words_in_instant is said: a journal 'say' row + an ask/out 'is' row, judged synchronously by the mind's own recall — an uncited frame is refused by name, never said)",
        "TRAITS": None,  # PREREG §12/§14: declared but the mind has no TRAITS interpreter yet (wave 3, W3-4: same-cell positives) — the organism does not start.
        # edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400 — L-4 (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md
        # §4): a real call site, gated on SURPRISE's own presence — creature/mind.py:Mind._consume_eye computes
        # `Organism.expected_sight(xw)` and passes it into `gaze.glances(..., predicted=...)`, reads the returned
        # `"residual"` back onto the journal row, and passes `confirm=` into `Organism.moment()` (genome/machinery.py)
        # for a glance whose residual is under the declared floor. Undeclared SURPRISE: predicted stays None, every
        # residual is None, confirm is never True — byte-identical to before this gene existed.
        "SURPRISE": "creature/mind.py:Mind._consume_eye (Organism.expected_sight() + gaze.glances(predicted=) + Organism.moment(confirm=))",
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:32 +0400 — L-9 (docs/briefs/LIFE-A-ANSWER-SELF.md
        # #3): SELF's real call sites -- _consume_body records the (reading, seq) pair a "self" pool item
        # compares; _think_pool appends the "self" kind item (kind-fair with word/sight/due/rule/outcome);
        # _think_work's "self" branch does the comparison and files the stall/no_room beliefs; _maybe_think
        # reads the LAST recorded body reading (never the live queue -- replay agrees) to skip+count THINK
        # while backlog stays over SELF's own threshold.
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:32 +0400 — the coordinator's fix (docs/briefs/
        # LIFE-A-REPORT.md §3 clause 6): the "behind" belief is NOT a comparison (one read the same field/
        # threshold as the skip and was always preempted by it) -- _maybe_think now tracks a run of skips and
        # _file_behind_belief() files it at the first think that RUNS after the run.
        "SELF": "creature/mind.py:Mind._consume_body (records readings) + _think_pool/_think_work ('self' kind, stall/no_room beliefs) + _maybe_think (the backlog skip + the 'behind' belief on resume, via _file_behind_belief)",
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:41 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
        # (docs/briefs/LIFE-F-HANDS-TOUCH-SMELL.md; MOTOR-HANDS.md G-MOT-4; BODY-SENSES.md §4.5/§4.6):
        # HANDS/SENSE_TOUCH/SENSE_SMELL, the mind-side rows. HANDS: two real call sites (Mind.__init__
        # resolves the jail/shelf paths; Mind._think_pool/_think_work builds and works the 'hands' pool
        # kind, Mind._maybe_think writes run/hands/ACT). SENSE_TOUCH/SENSE_SMELL: the same two-site shape
        # FAST's "sound" key uses (Mind.__init__ builds the dedicated ring; Mind._consume_touch/
        # _consume_smell read the declared presence and act on the row).
        "HANDS": "creature/mind.py:Mind.__init__ (self._hands_jail_path/_hands_shelf_dir resolved) + Mind._think_pool/_think_work ('hands' pool kind chooses a program) + Mind._maybe_think (writes run/hands/ACT) + creature/body.py:Body.start (declared['HANDS'] read via _declared_hands_config; starts creature/senses/hands.py:sense behind HANDS_DOOR_GATED)",
        "SENSE_TOUCH": "creature/mind.py:Mind.__init__ (self.touch_episodes built) + Mind._consume_touch (trait decoded, written to the dedicated ring, journaled)",
        "SENSE_SMELL": "creature/mind.py:Mind.__init__ (self.smell_episodes built) + Mind._consume_smell (trait decoded, written to the dedicated ring, journaled)",
    },
}


def unwired(declared: Dict[str, dict]) -> List[str]:
    """Every key of a parsed genome's `declared` dict that names no WIRED gene (an entry in RUNS whose
    site is not None) — sorted. A gene RUNS does not mention at all (INDUCE, DEDUCE, SENTENCE, HANDS,
    SURPRISE today; any typo or planted key) is unwired for the same reason TRAITS is: nothing in RUNS
    claims a site for it, so `wired` below never contains it."""
    wired = {gene for layer in RUNS.values() for gene, site in layer.items() if site is not None}
    return sorted(gene for gene in declared if gene not in wired)
