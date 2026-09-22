# LIFE-C-REPORT — QUESTION, mission words through the ear, SENTENCE (replaced), MOUTH

Claude (Sonnet 5, LIFE builder C). Branch `life-language`, worktree `/data/dev/genome-wt-t`, off
`g5-integration` at `aed56d5`. Brief: `docs/briefs/LIFE-C-QUESTION-SENTENCE.md`. Report written
2026-09-22 19:30 +0400; every timestamp below is a real `date` call, none typed from memory (#50).

## 1. What landed (file:line)

- **Task 2 — both mission words through the ear.** `creature/senses/game.py:76` `mission_words(mission)`
  (colour = 2nd-to-last token, object = last token); `creature/senses/game.py:158` `sense()`'s main loop
  publishes the colour word THEN the object word as two ear rows in the same instant, both before the eye
  row. `tests/creature/test_game_door.py` updated row counts (14→19, 11→15) and added ordering assertions
  (`colour_row["seq"] < object_row["seq"]`) — 5/5 tests pass against the real venv worker.

- **Task 2 support — `words_in_instant`/`tape_moment` on FAST.** `genome/fast.py:88-89` new columns,
  `:103` `write()` params, `:142-143` stored, `:168-170` read back, `:232` saved, `:258-259` loaded
  (back-compat guarded). `tests/genome/test_words_in_instant.py` — 6/6 green.

- **Task 1 — QUESTION.** `creature/mind.py:786` `_maybe_ask` (dedupe via `self._asked`, persisted to
  `run/ask/out/ASKED.json`, embeds `questions.why()` when a word is named); `:828` `_maybe_ask_word`;
  `:841` `_maybe_ask_clash`; `:766` `_write_ask_out` (the sole q-file writer, see §3 below). All four
  triggers wired: (a) wordless 2nd showing — `_consume_eye` (`creature/mind.py:410`), sight-only branch;
  (b) rule fails once — `_grade_rule` (`:727`), `not evidence` branch; (c) belief clash — `_maybe_ask_clash`
  called from `_think_work`'s clash-kind branch; (d) PARK parks a want — `_think_work`'s `dead_end()`
  closure's `ask_on_park` callback, wired from both the word- and sight-kind branches. The world door:
  `creature/world_maker.py:90` `_answer_one_question` (polls `ask/out/q-*.json`, excludes already-
  `.answered.json`, recomputes the canvas via `make(seed, w, i-1)` — see the off-by-one RAISE, §5) and
  `:59` `_publish_canvas`'s new `answering=` param, wired into `sense()` (`:137`) before the regular
  per-tick canvas logic (an EXTRA publish, never a substitute). `tests/creature/test_question_door.py` —
  7/7 green (unit-level fake-publish tests + a live end-to-end answering-within-canvases test + a world-pin
  re-assertion).

- **Task 3 — SENTENCE (parser line REPLACED).** `genome/machinery.py:301` new SENTENCE clause
  (`r"two-word frames from co-occurring words; judged by the eye; never next-token"`); the OLD
  `"two-word frames is near under-judge"` clause no longer parses (`tests/creature/test_refusal.py`'s
  renamed `TestSentenceNowWired`/new `TestTraitsRefusal` prove both directions). `genome/sentence.py:30`
  `find_frames(episodes, min_count=5, factor=2.0)` — ordered-pair (temporal, never symmetric) co-occurrence
  over episodes with >= 2 distinct `words_in_instant`, both a count bar and an independence-ratio bar,
  returns citable episode ids per frame. Wired into `creature/mind.py:852` `_think_pool` (a "frame" kind,
  kind-fair with word/sight/rule/outcome), `_think_work`'s frame branch (files via `predict_file`,
  claim/route/decider/due exactly as specified), and `_score_due_predictions` (scores when `w1` recurs,
  judged by `org.recall("sight", ...)` against `w2`'s word-cell — the eye's own recall, never next-token).
  `tests/genome/test_sentence.py` — 9/9 green (see §2 for the ring-wrap regression added this round).

- **Task 4 — MOUTH.** `creature/mind.py:1210` `_maybe_say` — checks `self._frames` for a `w1` in the
  current instant's words; an uncited frame (`episodes == []`) is refused by name, journaled
  `{"say": {"outcome": "refused", "reason": "uncited"}}`, never said (G-MOT-6's gate); a cited frame is
  said: a journal `say` row (`heard: "yes"/"no"` from `_frame_evidence`, judged synchronously by the
  mind's own `recall`) plus an `ask/out` `"is"` row `from: "mouth"`. Wired into `_maybe_think`
  (`creature/mind.py:1178`) — see §2 for the empty-pool fix this round. `tests/creature/
  test_question_sentence_mouth.py`'s `TestMouth` class — 4/4 green (2 original + 2 new regression tests).

- **Task 5 — genes.py registration.** `creature/genes.py:112-114` — `RUNS["mind"]["SENTENCE"]`,
  `["QUESTION"]`, `["MOUTH"]`, each naming its real call sites (quoted above). `unwired()` refuses none of
  the three; `tests/genome/test_parse_g4.py` and `tests/creature/test_refusal.py`'s
  `TestRegistryPinnedToParser` cover the pairing.

- **`genome/LIFE.genome`** — lines 70-72 already carried my DRAFT syntax verbatim (SENTENCE/MOUTH/QUESTION,
  written by the plan's own author ahead of this build). Verified byte-for-byte against my regexes (parsed
  them through a full genome and printed the resulting `declared` dicts — all three matched exactly, see
  §4). **No edit to `genome/LIFE.genome` was needed or made.**

## 2. Every test's RED→GREEN

**Discovered during the original build (this session, before the advisor round):**
1. `world.render_canvas("ball"/"key"/"box", rng)` → `KeyError: no such thing`. RED: SENTENCE/MOUTH tests
   crashed on setup. GREEN: decoupled the rendered picture (`"circle"`, a real `genome/world.py` thing)
   from the semantic colour/object word labels, which only matter on the ear channel.
2. Test helpers consumed only the returned EYE row, never the EAR row → `mind.pending`/`pending_words`
   never populated, words arrived as `None`/`""`. RED: every worded-canvas assertion failed. GREEN:
   rewrote `_publish_worded`/`_publish_sight_only`/`_publish_two_words` to call `mind.consume()` on every
   published row, ear before eye.
3. STAGE-gating (moments 0-200 have no MEET wiring) made "no want yet" assertions false on the full genome
   (incidental THINK/PARK dead-ends). RED: `test_rule_fails_once_asks_what_is`/`test_belief_clash_asks_is`.
   GREEN: isolated with a QUESTION+FAST-only genome for those two tests.
4. `org.recall("sight", f0)["cell"]` is `None` under `reason="noedge"` even when a real SIGHT cell
   resonated (`r["lit"]` is populated, `r["cell"]` needs a cross-area edge). RED: the wordless-2nd-showing
   trigger never fired on a realistic (STAGE-1) tape. GREEN: switched to `r.get("lit")`.
5. Threshold off-by-one: the birth itself is implicitly "sighting #1" (never counted), so the first
   resonance-without-birth IS sighting #2 — `n >= 2` never fired on a 2-canvas tape. GREEN: `n >= 1`.
6. `q-*.json` glob also matches `q-<n>.answered.json` → re-answering, double-rename
   (`q-9.answered.answered.json`). RED: `test_a_planted_question_is_answered_within_a_few_canvases...`.
   GREEN: filtered `if not p.name.endswith(".answered.json")`.
7. Discovered PRE-EXISTING off-by-one in `world_maker.sense()`'s moment-string `i` field (built AFTER
   `i += 1`, so a recorded moment's `i` is always one more than what `make()` actually saw). GREEN:
   `_answer_one_question` undoes it locally (`i_orig - 1`) rather than changing the global format — RAISED
   in §5, not "fixed" system-wide.
8. SENTENCE toy corpus (6 red-ball + 4 noise) gave `count=6, expected=3.6` — `6 > 7.2` false, doesn't
   clear. GREEN: derived the math and used 6 red-ball + 8 noise (`N=14, expected=2.571, 6 > 5.143` — see
   §3 for the exact run).

**Found by the advisor's review, fixed this round (all RED confirmed by a new/updated test before the
fix, all GREEN after):**
9. **`genome/sentence.py:44` — `find_frames` ring-wrap bug.** `for i in range(len(episodes)): episodes.get(i)`
   treated a slot index as an episode ID. `.get(eid)` maps through `_id_to_slot`; once FAST's ring wraps
   (`n_written > cap`), ids `0..cap-1` are exactly the EVICTED ones and every LIVE id is never visited —
   `find_frames` would go silently dead the moment a long life's ring filled (LIFE.genome's FAST is 20000;
   the game rungs ran ~30k rows in 8h per the memory record). Fixed to iterate the correct ID range
   (`range(max(0, n_written-cap), n_written)`), matching `genome/think.py`'s `induce()` in spirit (which
   iterates slots directly). New test `tests/genome/test_sentence.py::TestFindFramesRingWrap` — RED
   confirmed (`test_the_old_range_len_approach_would_have_found_nothing_on_this_fixture` shows the buggy
   loop visits only 2 of 3 live episodes, undercounting below `min_count`) → GREEN
   (`test_only_the_live_ring_slots_are_counted_after_a_wrap`: count=3, episodes=[3,4,5]).
10. **`creature/mind.py:1178` — `_maybe_say` sat after `_maybe_think`'s `if item is None: return`.** A
    think whose pool was EMPTY (exactly the state a settled life reaches once every want is parked and
    every frame scored) never reached the mouth — MOUTH would go silent by control flow, not by its own
    citation gate. Fixed: moved the `_maybe_say(row)` call above the early return. New test
    `TestMouth::test_says_even_when_the_think_pool_is_empty` — plants a cited frame, pre-parks the only
    word the canvas would file (so the pool is provably empty, confirmed via the journal's
    `think.outcome == "empty_pool"`), asserts `said == 1`.
11. **`creature/mind.py:766` — `questions_written` never advanced by `_write_ask_out` itself.** It was
    incremented only inside `_maybe_ask`, but `_maybe_say` also calls `_write_ask_out` directly (its `is`
    row) without incrementing anything — two `say`s, or a `say` followed by a `_maybe_ask`, would silently
    overwrite the SAME `q-N.json`. Fixed: the increment now lives inside `_write_ask_out`, the one place a
    q-file is actually written; removed the now-redundant increment from `_maybe_ask`. New test
    `TestMouth::test_two_says_get_two_distinct_q_files` — two `say`s across two canvases, asserts 2
    distinct filenames and 2 distinct `seq` values.
12. **`creature/world_maker.py:170` — plant-after check used `==` against `total`, which
    `_answer_one_question` can advance by one BEFORE the check runs (an answered question inserts an EXTRA
    canvas).** A tick that entered with `total == plant_after_canvases` could reach the check at
    `total == plant_after_canvases + 1`, and the plant (the life's own `(vi')` mark) would silently never
    arm. Fixed: `>=` (still guarded by `plant_deadline is None`, so it still arms exactly once) —
    behaviour-identical whenever no answer lands on that exact tick, safe whenever one does. Covered by
    the existing `TestPlantMechanism` suite (unaffected — still green) plus manual reasoning verified
    against `_answer_one_question`'s own return contract; no dedicated new test was added since the race
    needs a specific single-tick coincidence that is impractical to force deterministically without a
    fake clock (documented here rather than asserted synthetically).
13. **`creature/mind.py:222` — `questions_answered` computed nowhere.** STATUS declared the field
    (`creature/body.py:316` spreads `think_counters` into STATUS) but nothing ever wrote it. Fixed:
    `_consume_eye` (`:472-480`) increments it whenever the eye row's own `meta.get("answering")` is set
    (stamped by the world door's `_publish_canvas`). Verified via the pre-flight run's `STATUS.json`
    (§4) reading `questions_answered: 0` consistently with `questions_written: 0` (no want was ever
    answered because none was ever asked in that 6-minute window — a consistent zero, not a silent gap).
14. **Replay identity with QUESTION/SENTENCE/MOUTH declared — the brief's own test, not yet run.** Checked
    `creature/replay.py` first: `run_replay` builds a FRESH `tempfile.mkdtemp()` work root for every call
    and only ever symlinks the source tape's `payload/` dir into it — `ask/out/ASKED.json` is never shared
    between a live run and its replay, or between two replays. The advisor's named hazard ("a replay mind
    loads every want as already-asked from a shared root") does **not** apply to this codebase's actual
    replay road. New file `tests/creature/test_replay_question_sentence_mouth.py` proves it empirically: a
    live ~85-canvas life with QUESTION+SENTENCE+MOUTH declared produces real `think`/`question` journal
    rows (a positive control — a 0-finding parity check proves nothing), then `replay.main(...--against...)`
    returns 0 (byte-identical, 175 mind rows matched) and two independent replays of the same tape agree
    with each other. 3/3 green.

**Full run of all six new/modified test files after every fix above (final bytes):**
```
$ python3 -m unittest tests.genome.test_sentence tests.creature.test_question_sentence_mouth \
    tests.creature.test_question_door tests.creature.test_replay_question_sentence_mouth \
    tests.creature.test_game_door -v
...
Ran 33 tests in 12.533s
OK
```

## 3. The toy's precision numbers

**`tests/genome/test_sentence.py::TestSkewedToyPrecision`** (50 synthetic missions, `{red,blue,green} x
{ball,key,box}`, `skew_pairs={("red","ball"),("blue","key")}`, `skew_share=0.7`, seed 20260922):
- Skewed corpus: filed `[("blue","key")]` — count=15, expected=6.8 (`15 > 2.0*6.8`) — **precision = 1.0**
  (bar: >= 0.8).
- Shuffled twin (same corpus, colour↔object pairing shuffled across missions, shuffle seed=1): filed
  **nothing** — **precision = 0.0** (bar: <= 0.3).

**`tests/creature/test_question_sentence_mouth.py::TestSentenceFramesThroughTheMind`** (through the real
Mind pipeline, 6 "red ball" + 8 noise instances over 4 unrelated pairs): `count=6, expected=2.571, N=14`
(`6 > 2.0*2.571 = 5.143`) — files `red|ball`, then scores it when "red" recurs
(`frames_scored >= 1`).

## 4. The question road: 6-minute pre-flight

Command run (temp root under `scratch/`, never `run/`):
```
python3 -m creature.body --root scratch/preflight/root \
  --genome scratch/preflight/preflight.genome \  # genome/G5.genome + my 3 DRAFT lines, verbatim
  --plant-after 5000 --folder /data/dev/genome/world
```
Launched 2026-09-22 19:20 +0400, `SIGTERM` sent 2026-09-22 19:27 +0400 (355 s run, clean shutdown, no
crash). My three lines parsed byte-for-byte against my own regexes (checked before the run):
`SENTENCE {'frames': 'co-occurring', 'judged': 'eye', 'next_token': False}`,
`MOUTH {'say': 'one frame per think', 'journaled': True}`,
`QUESTION {'source': 'wants', 'forms': ['what-is','is','which'], 'to': 'world door'}`.

**Tape:** 479 rows — game 150 ear/75 eye/74 outcome (75 missions, one incomplete at cutoff), maker 74
ear/74 eye, folder 12 ear/13 eye, body 7 event rows.

**STATUS.json denominators** (SOLUTIONS #168's rule: every zero reported with its denominator, never
bare): `thinks=16` (THINK every=10 canvases), `parked=0`, `clashes=0`, `beliefs=2`,
`predictions_filed=7`, `predictions_scored=7` (all 7 are INDUCE rule items — `think` outcomes:
`filed=7, reflected=5, belief=2, no_cell_answers=1, not_yet_due=1`), `frames_filed=0`, `frames_scored=0`,
`frames_true=0`, **`questions_written=0`, `questions_answered=0`, `said=0`, `heard_yes=0`, `heard_no=0`**.
`ask/out/` is empty (0 q-files, 0 `.answered.json`).

**Reading the zeros against their denominators, not as failures:**
- **QUESTION (0 questions):** fully explained — none of its 4 triggers fired: `parked=0` (trigger d never
  occurred), `clashes=0` (trigger c never occurred), and the 7 filed/scored predictions were all INDUCE
  rules that never failed (no rule-fails-once event, trigger b), and no wordless picture was seen twice
  without a word within this short window (trigger a). This is consistent with the toy-level tests, which
  each isolate a single trigger deliberately — a natural 6-minute life with THINK firing only once per 10
  canvases (16 thinks total) is short odds for any of the four to land by chance. The 7-test dedicated
  QUESTION suite (`tests/creature/test_question_door.py` + the QUESTION classes in
  `test_question_sentence_mouth.py`) is where each trigger is proven to fire on the mechanism directly.
- **SENTENCE (0 frames):** consistent with the module's own documented RAISE (§5, below) — only 75 game
  missions were drawn in 6 minutes (one every 5s), and `find_frames`'s default `min_count=5, factor=2.0`
  bar needs either a skewed (colour,object) pairing or enough unrelated background noise to buy lift; this
  builder did not measure BabyAI-GoToLocal's own seed schedule for skew (see §5) — a genuinely open
  question, not a bug.
- **MOUTH (0 says):** a direct consequence of 0 filed frames — nothing was ever in `self._frames` to say.

## 5. Every clause RAISED (never worked around)

1. **`genome/sentence.py`'s own module docstring (lines 9-24): under a UNIFORM mission distribution, or
   even a single skewed pair on a small grid, `count > factor * expected` structurally cannot clear.**
   Math: a single skewed pair's own marginals rise with its count, capping the achievable independence
   ratio (~1.33x for single-pair skew on a 3x3 grid) — more UNRELATED background noise (not more repeats
   of the pair itself) is what buys lift above the 2x bar. Nobody has measured BabyAI-GoToLocal's own
   `--seed` draw for skew; the toy corpus in `synthetic_missions()` deliberately constructs skew to prove
   the STATISTIC is correct, not that the live game world will feed it enough skew to ever fire. **The
   plan's own 24h mark ("frames filed >= 3 by 24h") is therefore conditional on a fact about the game
   world this builder did not measure** — worth a follow-up measurement of the live mission distribution
   before that mark is graded.

2. **`creature/world_maker.py:118` — a discovered PRE-EXISTING off-by-one in `sense()`'s own moment-string
   line**, not introduced by this build: `moment = f"...i{i:06d}..."` is built AFTER the regular branch's
   `i += 1`, so a recorded moment's `i` field is always ONE MORE than the `i` that was actually passed to
   `make()` (verified empirically: `make(seed,0,0) == "circle"` but the first recorded moment reads
   `w0000i000001...`). Never fixed globally here — the recorded tape's own moment strings, already durable
   on every life that has ever run, keep their existing meaning; changing the encoding would be a global
   format change far outside this brief's scope. `_answer_one_question` works around it locally
   (`i_orig - 1`) so the door shows the SAME thing the original moment actually drew. **Whoever owns
   `world_maker.py` more broadly should decide whether to fix the root cause** (it would change every
   future tape's moment-string semantics).

3. **`creature/mind.py`'s `snapshot()`/`resume()` (lines 1253-1310) never persist `_frames`,
   `_frame_pending`, or `_wordless_seen`.** This is the SAME pre-existing gap the codebase already has for
   `_induce_pending`/`_deduce_pending` (in-flight FILE claims not yet scored) — not unique to this build,
   but my three new pieces of in-flight state fall into the identical hole. Consequences on a resume/
   restart: (a) `_frames` lost → MOUTH goes silent until SENTENCE re-files a frame from the FAST ring
   (which IS persisted, so this self-heals once enough episodes are re-seen, but with a gap); (b)
   `_frame_pending` lost → a frame already filed-but-unscored before the restart could be RE-filed
   (a duplicate FILE claim, inflating `predictions_filed`); (c) `_wordless_seen` lost → a picture on its
   "2nd" wordless showing pre-restart needs two MORE sightings post-restart to re-trigger QUESTION's
   trigger (a). None of this breaks determinism (replay is unaffected — replay always starts fresh, §2
   item 14) — it only affects a live process that crashes and resumes mid-life. Flagged, not fixed: fixing
   it correctly means deciding the resume contract for ALL of `_induce_pending`/`_deduce_pending`/
   `_frame_pending`/`_frames`/`_wordless_seen` together, which is bigger than this brief's three genes.

4. **The `total == plant_after_canvases` → `total >= plant_after_canvases` fix in `world_maker.py:170`
   (§2 item 12) is a genuine but low-probability race** (an answered question landing on the exact tick
   `total` would have hit the plant threshold). Fixed as `>=`, which is behaviour-identical to `==` in the
   overwhelmingly common case (no answer on that exact tick) and correct in the rare case. Not treated as
   a RAISE requiring a design decision — a strict improvement, no downside identified — but named here per
   the advisor's instruction to journal the decision.

## 6. Suites, final bytes

Both run with `-t .`, output logged to files, final `Ran N … OK/FAILED` lines:

```
$ python3 -m unittest discover -s tests/creature -t . -v > scratch/logs/suite_creature.log 2>&1
Ran 282 tests in 323.705s
OK (skipped=1)

$ python3 -m unittest discover -s tests/genome -t . -v > scratch/logs/suite_genome.log 2>&1
Ran 236 tests in 64.393s
OK (skipped=1, expected failures=6)
```
Zero `FAIL:`/`ERROR:` lines in either log (grepped explicitly). The genome suite's 6 "expected failures"
are pre-existing `@unittest.expectedFailure`-marked tests, not introduced by this build.
`tests/creature/test_world_pin.py` re-checked standalone after every change in this report: 3/3 green,
`schedule()`/`make()` untouched.

## 7. Scope discipline

No file under `run/`, `world/`, systemd, `/data/dev/genome` (master), `/data/dev/genome-lives`, or any
other worktree was touched. `world_maker.py`'s `schedule()`/`make()` are byte-identical to the pin (§6).
Every edited file carries a `# edit: Claude (Sonnet 5, LIFE builder C), <date> — …` comment with a real
`date`-sourced timestamp (an early batch of comments in this file's own session drifted ~40 minutes ahead
of the clock during a dense editing burst — SOLUTIONS #50's exact failure mode — caught by re-running
`date` before this final pass and corrected to the verified time, 2026-09-22 19:12 +0400, across all six
touched files).
