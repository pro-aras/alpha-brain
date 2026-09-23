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

# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE): BOUNDS,
# below RUNS/unwired. One table naming EVERY numeric gene value `genome/machinery.py`'s parser reads,
# `[lo, hi]` + the step (int, or float with the decimal count the parser prints back). Genes that change a
# MOMENT's shape or an ARRAY's shape are EXCLUDED, named with the reason (the advisor's amendment, brief
# ALPHA4-J.md item 1, 2026-09-23 00:34 +0400): mutating one of these would change what a persisted episode
# ring/journal row/W-matrix MEANS mid-life, which no replay-identity law here defends against — only RATES
# and THRESHOLDS are mutated. Two more are excluded on a narrower, documented reading of the same brief
# clause: PARK's "after" and INDUCE's "from" were named in the brief's own first (pre-exclusion) list of
# "every numeric gene value the parser reads", but its FINAL sentence ("Mutate RATES and THRESHOLDS only:
# theta_n, DELTA lr, KWTA, BUDGET per arrival and its regen, SLEEP every/replay, THINK every, PRUNE
# w/chances, MERGE cos, ABSTAIN ratio, CURIOSITY interests, SCALE every, BIRTH misfires, PARK after") does
# not mention INDUCE at all, and FROZEN's own RUNS row below already marks it TWIN-ONLY (never read from a
# live genome — mutating it would change nothing a live proposal could ever grade). Read conservatively:
# PARK after IS in the final list (kept, mutable); INDUCE from is NOT (excluded here, named, not silently
# dropped) — raised in the builder report as an interpretation, not a silent guess.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

import numpy as np


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
        # edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:58 +0400 — A4L-COST (docs/briefs/A4L-COST.md; docs/A4-LADDER-PREREG.md
        # §2.1): HASH's own row — real call sites, all gated on `"HASH" in declared` at Organism.__init__ (an undeclared HASH builds no
        # witness, and row_hash() is state_hash(), byte-identical — the negative control).
        "HASH": "genome/machinery.py:Organism.row_hash (the per-row witness: genome/witness.py's SPARSE digest when declared) + "
                "Organism._hebb/_prune/_merge (mark the rows whose MASK they change) + creature/mind.py's five hashed journal rows; "
                "Organism.save keeps the DENSE state_hash in the snapshot meta (load's verification chain unchanged)",
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
        # edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:0x +0400 — ALPHA4-H (docs/briefs/ALPHA4-H.md
        # tasks 2/3; ALPHA4-PREREG.md §3): the shelf reader and the lexicon door, wired the SAME C1.7/C2 shape
        # WORLD_GAME/HANDS above use (gated on the gene's own declared presence; a genome line arms nothing
        # until the code carrying it exists, behind each module's own *_DOOR_GATED constant).
        "SENSE_READ": "creature/body.py:main (declared['SENSE_READ'] read; arms creature/senses/read.py behind READ_DOOR_GATED) + creature/mind.py:consume ('ear'/'eye' branches, unchanged -- a shelf row is source='shelf', read exactly like every other ear/eye row; MEET/ARRIVAL/FAST all apply with no new branch)",
        "DOOR_LEXICON": "creature/body.py:main (declared['DOOR_LEXICON'] read; arms creature/senses/lexicon.py behind LEXICON_DOOR_GATED) + creature/mind.py:_maybe_ask (gated on 'DOOR_LEXICON' in declared: a what-is want that resolves a word also writes world/questions/q-<n>.json {q, word} for the door to answer -- ask/out/q-<n>.json alone carries no word, only a tape moment, ALPHA4-H-REPORT.md's own RAISED clause)",
        # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 00:56 +0400 — ALPHA4-PREREG.md §3: two real
        # call sites each, the same two-site shape HANDS/WORLD_GAME already use (body arms the sense
        # thread; the mind consumes what it publishes). DOOR_WEB: creature/body.py:main reads
        # declared['DOOR_WEB'] and arms creature/senses/web.py behind WEB_DOOR_GATED (the same
        # "a genome line arms nothing until the code exists" discipline C2/C3 used for the folder/game
        # doors); creature/mind.py:Mind._consume_web counts fetches/refusals from the `web` tape rows the
        # sense publishes (STATUS's web_fetches/web_refused_rate) and tracks the hold flag `_hold_active`
        # from `hold` tape rows (STATUS's web_hold; also read by the READINESS judge's (e)).
        # SENSE_GRADE: creature/body.py:Body.start reads declared['SENSE_GRADE'] and starts
        # creature/senses/grade.py:sense (the same C1.7 pattern SIT/SENSE_BODY use); creature/mind.py:
        # Mind._consume_grade/_consume_hold track the seat's grades and the hold flag the READINESS
        # judge's (d)/(e) read.
        "DOOR_WEB": "creature/body.py:main (declared['DOOR_WEB'] read; arms creature/senses/web.py behind WEB_DOOR_GATED) + creature/mind.py:Mind._consume_web (fetch/refusal counters + the hold flag)",
        "SENSE_GRADE": "creature/body.py:Body.start (declared['SENSE_GRADE'] read; starts creature/senses/grade.py:sense) + creature/mind.py:Mind._consume_grade/_consume_hold (the seat's grades + the hold flag, both read by the READINESS judge)",
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
        # edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6: EVOLVE. Real call
        # sites: Mind._consume_proposal (a 'proposal' tape row, gated on EVOLVE's own declared presence, records the
        # latest not-yet-adopted PASS proposal) + Mind._maybe_sleep's adoption branch (writes GENOME.v<n>.genome,
        # re-parses self.genome/self.org.g, journals the epoch row) + Mind.resume (epoch-aware: resolves the latest
        # GENOME.v<n>.genome under root instead of the launch genome_path). creature/body.py:main arms the worker
        # (tools/evolve.py, a subprocess) and creature/senses/evolve.py's sense thread (publishes PROPOSAL-<n>.json
        # files as 'proposal' tape rows) behind EVOLVE's own declared presence, the same C2/C3 gate discipline
        # WORLD_GAME/HANDS use.
        "EVOLVE": "creature/mind.py:Mind._consume_proposal + Mind._maybe_sleep (adoption) + Mind.resume (epoch-aware) "
                  "+ creature/body.py:main (arms tools/evolve.py + creature/senses/evolve.py) + tools/evolve.py (the shadow/twin replay + grading)",
        # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 00:56 +0400 — ALPHA4-PREREG.md §3/§4: the
        # ONE real call site of the "by READY" STAGE form — creature/mind.py:Mind._consume_sit evaluates
        # §4 (a)-(e) from tape facts at every EXAM boundary and commits STAGE 4 (self.stage, a journal
        # "stage" event) once all five hold on two consecutive windows. The plain "moments" STAGE form
        # (STAGE 1/2/3 here) stays an undeclared, ungated Genome field exactly as before — this row exists
        # only for the NEW `declared["STAGE_READY"]` key the "by READY" grammar writes.
        "STAGE_READY": "creature/mind.py:Mind._consume_sit (THE READINESS JUDGE, ALPHA4-PREREG §4 (a)-(e); commits self.stage=4 via a journal event, never undone)",
    },
}


def unwired(declared: Dict[str, dict]) -> List[str]:
    """Every key of a parsed genome's `declared` dict that names no WIRED gene (an entry in RUNS whose
    site is not None) — sorted. A gene RUNS does not mention at all (INDUCE, DEDUCE, SENTENCE, HANDS,
    SURPRISE today; any typo or planted key) is unwired for the same reason TRAITS is: nothing in RUNS
    claims a site for it, so `wired` below never contains it."""
    wired = {gene for layer in RUNS.values() for gene, site in layer.items() if site is not None}
    return sorted(gene for gene in declared if gene not in wired)


# ============================================================================ ALPHA4-PREREG.md §6: BOUNDS
# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400.
#
# Each MUTABLE entry: {"lo", "hi", "kind" ("int"|"float"), "decimals" (float only — the decimal count the
# genome text already carries, so a mutant line reads exactly like a hand-written one), "pattern" (a
# MULTILINE regex over the RAW genome TEXT — comments included — with group(1) the fixed text up to and
# including the number's own left edge, and group(2) everything AFTER the number to end of line, `.*`
# greedy so a trailing clause this builder has never seen — G's future "; regenerate …" on BUDGET, per the
# advisor's own example — survives untouched: only the number between the two groups is replaced).
#
# Each EXCLUDED entry carries "excluded": True and "reason" — named, never silently dropped, per the
# brief's own instruction.
_NUM_RE = r"-?\d+(?:\.\d+)?"

BOUNDS: Dict[str, dict] = {
    # ---- mutable: RATES and THRESHOLDS only (brief ALPHA4-J.md item 1's final sentence) ----
    "BIRTH.theta_n": {
        "lo": 0.85, "hi": 0.99, "kind": "float", "decimals": 3,
        "pattern": re.compile(r"^(BIRTH\s+novelty\s+cos<)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "BIRTH novelty cos<THETA_N — the brief's own planted-bad value (0.5) is deliberately OUTSIDE this band",
    },
    "BIRTH.misfires": {
        "lo": 1, "hi": 8, "kind": "int",
        "pattern": re.compile(r"^(BIRTH\s+error\s+misfires\s+)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "BIRTH error misfires N",
    },
    "DELTA.lr": {
        "lo": 0.01, "hi": 0.2, "kind": "float", "decimals": 2,
        "pattern": re.compile(r"^(DELTA\s+lr\s+)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "DELTA lr F",
    },
    "KWTA.k": {
        "lo": 2, "hi": 10, "kind": "int",
        "pattern": re.compile(r"^(KWTA\s+)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "KWTA N",
    },
    "BUDGET.per_arrival": {
        "lo": 100, "hi": 800, "kind": "int",
        "pattern": re.compile(r"^(BUDGET\s+)" + _NUM_RE + r"(\s+per\s+arrival.*)$", re.MULTILINE),
        "note": "BUDGET N per arrival — the regen clause (builder G, ALPHA4-PREREG §3) is not in this "
                "worktree's grammar; the suffix group's trailing `.*` preserves it untouched once it lands",
    },
    "SLEEP.every": {
        "lo": 500, "hi": 5000, "kind": "int",
        "pattern": re.compile(r"^(SLEEP\s+every\s+)" + _NUM_RE + r"(\s+moments\s+replay.*)$", re.MULTILINE),
        "note": "SLEEP every N moments replay M by surprise",
    },
    "SLEEP.replay": {
        "lo": 50, "hi": 500, "kind": "int",
        "pattern": re.compile(r"^(SLEEP\s+every\s+" + _NUM_RE + r"\s+moments\s+replay\s+)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "SLEEP every N moments replay M by surprise",
    },
    "THINK.every": {
        "lo": 2, "hi": 50, "kind": "int",
        "pattern": re.compile(r"^(THINK\s+every\s+)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "THINK every N canvases[; on its own thread; lands next boundary] — the optional tail survives via the suffix group",
    },
    "PRUNE.floor": {
        "lo": 0.005, "hi": 0.1, "kind": "float", "decimals": 2,
        "pattern": re.compile(r"^(PRUNE\s+w<)" + _NUM_RE + r"(\s+after\s+.*)$", re.MULTILINE),
        "note": "PRUNE w<F after N chances",
    },
    "PRUNE.chances": {
        "lo": 1, "hi": 10, "kind": "int",
        "pattern": re.compile(r"^(PRUNE\s+w<" + _NUM_RE + r"\s+after\s+)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "PRUNE w<F after N chances",
    },
    "MERGE.theta_m": {
        "lo": 0.98, "hi": 0.999, "kind": "float", "decimals": 4,
        "pattern": re.compile(r"^(MERGE\s+cos>)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "MERGE cos>THETA_M same-answer",
    },
    "ABSTAIN.ratio": {
        "lo": 0.5, "hi": 0.98, "kind": "float", "decimals": 2,
        "pattern": re.compile(r"^(ABSTAIN\s+second/best\s*>\s*)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "ABSTAIN second/best > F — the ratio form only (the margin form, ABSTAIN margin cos<M, is a "
                "different sub-gene; LIFE.genome/ALPHA4.genome both use the ratio form)",
    },
    "CURIOSITY.interests": {
        "lo": 10, "hi": 200, "kind": "int",
        "pattern": re.compile(r"^(CURIOSITY\s+interests\s+)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "CURIOSITY interests N operators … — genome/curiosity.py's Interests.n is a SOFT POPULATION "
                "CAP on a plain dict, never an array size (checked against the source, not assumed)",
    },
    "SCALE.every": {
        "lo": 200, "hi": 5000, "kind": "int",
        "pattern": re.compile(r"^(SCALE\s+every\s+)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "SCALE every N moments",
    },
    "PARK.after": {
        "lo": 1, "hi": 10, "kind": "int",
        "pattern": re.compile(r"^(PARK\s+after\s+)" + _NUM_RE + r"(.*)$", re.MULTILINE),
        "note": "PARK after N identical dead-ends … — genome/park.py's Park.n gates a plain dict counter, never an array size",
    },
    # ---- excluded: shape genes (the advisor's amendment) ----
    "GAZE.fixations": {"excluded": True, "reason": "moments per canvas — exam.py:66 divides by it; every 'every N canvases' cadence depends on it; the episode ring's keys change meaning"},
    "GAZE.grid": {"excluded": True, "reason": "the fixation grid — an array-shape gene of the same GAZE line"},
    "GAZE.canvas": {"excluded": True, "reason": "the canvas side — an array-shape gene of the same GAZE line"},
    "GAZE.glance": {"excluded": True, "reason": "the glance window side — an array-shape gene of the same GAZE line"},
    "SENSE.ear_letters": {"excluded": True, "reason": "words_dim() = ear_letters * 26|27 — a sight/words AREA dimension"},
    "RETINA": {"excluded": True, "reason": "the fixed front's own step list — sight_dim() depends on it structurally"},
    "FAST.episodes": {"excluded": True, "reason": "the episode ring's own size — a persisted array shape"},
    "HEBB.window": {"excluded": True, "reason": "the window IS one moment by construction (machinery.py's own comment); any other value refuses"},
    "SENSE.colour": {"excluded": True, "reason": "sight_dim() += 32 when declared — an AREA dimension"},
    "EXAM.every": {"excluded": True, "reason": "the judge's own window — PREREG §2: judges are sealed, never mutated in-life"},
    "SIT.every": {"excluded": True, "reason": "the judge's own window — PREREG §2: judges are sealed, never mutated in-life"},
    "STAGE": {"excluded": True, "reason": "developmental stage boundaries — a moment's own meaning (senses/meet/nursery/world) changes at these, not a rate"},
    # ---- excluded: read conservatively from the brief's own final ("mutate only") list (see module docstring) ----
    "PARK.reopen_kinds": {"excluded": True, "reason": "not a number — 'reopen on new-sense' is a fixed literal the parser accepts, nothing to mutate"},
    "FROZEN.after": {"excluded": True, "reason": "creature/genes.py RUNS['mind']['FROZEN'] is TWIN-ONLY (read only when 'frozen' in blind) — a live genome never reads it, so a live proposal could never grade a mutation of it"},
    "INDUCE.from_episodes": {"excluded": True, "reason": "named in the brief's own first (pre-exclusion) list but absent from its final 'Mutate RATES and THRESHOLDS only' sentence — read conservatively as not included (raised in the report, not silently guessed)"},
}

MUTABLE_KEYS: Tuple[str, ...] = tuple(sorted(k for k, v in BOUNDS.items() if not v.get("excluded")))


def draw_mutation(seed: int, epoch: int, proposal_no: int) -> Tuple[str, object]:
    """ALPHA4-PREREG.md §6: "one numeric gene moved within genes.py BOUNDS by the mind's own rng seeded on
    (SEED, epoch)" — the brief's own item 1 adds `proposal_no` as a third stream key so two proposals filed
    within the same epoch (a refused one, then a retry) never draw the same mutation. `np.random.default_
    rng` with an integer sequence seed is deterministic across processes/machines — the SAME triple always
    draws the SAME (gene, value), which is what makes a replay of a 'proposal' tape row reproduce the exact
    mutant text without the mutant text itself needing to be re-derived (it is carried verbatim on the row
    regardless — this function is what PRODUCES that text the first time, at the worker)."""
    rng = np.random.default_rng([int(seed), int(epoch), int(proposal_no)])
    key = MUTABLE_KEYS[int(rng.integers(0, len(MUTABLE_KEYS)))]
    spec = BOUNDS[key]
    if spec["kind"] == "int":
        value: object = int(rng.integers(int(spec["lo"]), int(spec["hi"]) + 1))
    else:
        value = round(float(rng.uniform(spec["lo"], spec["hi"])), int(spec["decimals"]))
    return key, value


def apply_mutation(text: str, key: str, value: object) -> str:
    """One gene, one value, substituted into the genome TEXT (never a dict — brief item 1: "the mutant TEXT
    is what is stored"). `pattern.subn` with `count=1` — a pattern that matches zero or more than once
    raises, naming the count, rather than silently mutating the wrong line or every line."""
    spec = BOUNDS.get(key)
    if spec is None or spec.get("excluded"):
        raise ValueError(f"EVOLVE: {key!r} is not a mutable BOUNDS entry ({(spec or {}).get('reason', 'unknown key')})")
    kind = spec["kind"]
    val_str = str(int(round(value))) if kind == "int" else f"{float(value):.{int(spec['decimals'])}f}"
    pattern = spec["pattern"]
    new_text, n = pattern.subn(lambda m: m.group(1) + val_str + m.group(2), text, count=1)
    if n != 1:
        raise ValueError(f"EVOLVE: BOUNDS[{key!r}]'s pattern matched {n} times in the genome text (need exactly 1)")
    return new_text


def mutate_genome_text(text: str, seed: int, epoch: int, proposal_no: int) -> Tuple[str, str, object]:
    """Draw one (gene, value) deterministically (SEED, epoch, proposal_no) and apply it to `text`. Returns
    (mutant_text, gene_key, value) — the worker publishes all three on the proposal row (brief item 2's
    payload shape) so a reader never has to re-derive the value from the rng to know what changed."""
    key, value = draw_mutation(seed, epoch, proposal_no)
    return apply_mutation(text, key, value), key, value
