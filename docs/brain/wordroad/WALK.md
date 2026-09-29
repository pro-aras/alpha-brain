*Walk by Claude (Opus 5.5, read-only investigator), 2026-09-29 12:22 +0400.*

# THE WORD ROAD — the consumer walk (read-only)

Tree: `/data/dev/genome-wt-day0929`, branch day-0929, commit 9d218b2. Nothing in the tree was changed except this file.
Closed lives were only read. Scratch scripts and their output: `/data/dev/brain-runs/day0929/walk/`
(`measure_utterances.py`, `planted_control.py`, `lastwords.py`, `measure-out.json`).

**The draft law under test.** One `Organism.moment` per glance (so `org.t` and every moment cadence stay as they are).
The words side of that moment is the UNION of the winners of each word's own vector, in spoken order. Each word keeps its
own vector for its own novelty/error birth. The ledger's and journal's `word` stays the LAST word.

Tags: **[Certain]** = read in the file (line quoted or cited) or measured. **[Likely]** = inferred from code I read, not run.

**A correction to the brief.** `sorted(self.pending.items())` is hashed in `_chat_guard` (`creature/mind.py:1220`), not in
`_row_digest`. `_row_digest` (`creature/mind.py:2148-2154`) is `self.org.row_hash()` alone. [Certain]

---

## (A) Producers — who publishes `ear` rows, and how many per moment

The mind consumes rows in tape (seq) order: `Body._publish` writes the tape row and puts it on the one queue under the
same lock (`creature/body.py:214-217`); `_mind_loop` takes the queue FIFO (`creature/body.py:322-329`). [Certain]

| Producer | Lines | Ear rows per moment | Order; which word is LAST |
|---|---|---|---|
| `creature/senses/scene.py` (WORLD scene) | 260-261: `rows = [{"sense": "ear", ... "word": w ...} for w in said]`, then the eye row | 1, 2 or 3 (template T1-T4) | `brain/scene/world.py:141-154`: T1 «shape», T2 «colour shape», T3 «size shape», T4 «size colour shape». **The shape is always last.** Scene 2,699 says «dax» alone. [Certain] |
| `creature/senses/game.py` (WORLD game) | 221-225: `if colour is not None: publish("ear", colour ...)` then `publish("ear", word ...)` | 2 (1 if the mission has one token) | colour first, object last (`mission_words`, 85-97: `colour = toks[-2]`). Measured: 2 on every game moment. [Certain] |
| `creature/senses/read.py` (SENSE read, the shelf) | 184-198 `_publish_chunk` | default shape (`_read_shape_from_argv`, `creature/body.py:701-706`: True unless `--read-single-moment`): each word ALONE on its own moment (1 row), then the line's moment with every word (up to `words 4`) | chunk order; the line's last word is last. Every shelf word is also last on its own one-word moment. [Certain] |
| `creature/senses/lexicon.py` (DOOR lexicon) | 86-88: `for w in gloss_words: publish("ear", ...)` | up to 8 (`words` default 8) | gloss order; function words often last. [Certain] |
| `creature/senses/web.py` (DOOR web) | 285-294 (292: `for w in words:`, 294: `publish("ear", ...)`) per sentence moment | up to `max_words` | sentence order. Not on any measured tape (the web door opens at STAGE 4). [Certain for code; no rows measured] |
| `creature/senses/folder.py` | 141-142: one `publish("ear", word ...)` when `is_word` | 0 or 1 | — [Certain] |
| `creature/world_maker.py` (the maker) | 80: `publish("ear", thing ...)`; 81-84 an optional `ear-sound` row carrying `meta.word` | 1 | — ; the `ear-sound` row is not an `ear` row (`mind.consume` routes it to `_consume_ear_sound`). [Certain] |
| `creature/senses/ear.py` (sound door) | 101: publishes `ear-sound` only | 0 `ear` rows | — [Certain] |
| `creature/senses/chat.py` | 124: publishes `chat` (a read-only branch, never the MEET road) | 0 `ear` rows | chat words ride in `meta.words`, read by `_consume_chat` only. [Certain] |
| `hands.py`, `body_sense.py`, `grade.py`, `sit.py`, `evolve.py` | publish eye/outcome/touch/body/grade/hold/sit/proposal | 0 `ear` rows | [Certain] |
| test/tool tapes: `tools/gate_g4.py:217`, `tests/creature/*` | one per moment, except `_publish_two_words` (test_question_sentence_mouth.py), `_scene_tape.py`, `_chat_tape.py`, `readiness_rows.py` | 1 or 2+ | — [Certain] |

Every producer that can hand the ear a word longer than 8 letters filters first (`read_common.words_of`, 50-64: lower-case,
strip non a-z, truncate to `letters`). Measured: **0 heard words the ear would refuse** on all six tapes (E). This matters:
under the draft every non-last word is encoded for the first time, and `encode_word` RAISES on a bad word (#230's class).

---

## (B) The chain — one row per consumer

Class column: UNCHANGED / MUST WIDEN / BREAKS / AMBIGUOUS, under the draft law exactly as stated above.

Tags for the tables: every Where / Reads / Assumes cell is [Certain] (read in the file at the cited line). Every «Under
the draft» cell is [Likely] by nature — a prediction about a law not yet built — except where it cites a measurement (C.3,
E), which is [Certain].

### B.1 The mind (`creature/mind.py`)

| # | Where | Reads / writes | Assumes | Under the draft | Class | Pinned by |
|---|---|---|---|---|---|---|
| 1 | 780-789 `consume` ear branch | writes `pending[m] = meta.get("word")` (last wins) and `pending_words[m].append(w)` if truthy | nothing: already keeps both | the list the law needs already exists | UNCHANGED | test_mind_chat.py:32-33 (state dict); test_question_sentence_mouth.py:54 (order law) |
| 2 | 1830, 1834 `_consume_eye` pops | `word = pending.pop(m)`, `words_in_instant = pending_words.pop(m, [])` | both popped at the eye row | already popped | UNCHANGED | same |
| 3 | 1843-1846 blind-ear twin | `label = word` (last); `word, words_in_instant = None, []` | one label per canvas | the twin keeps the LAST word for its ledger and ARRIVAL clock; if the live law widens ARRIVAL (#10), the twin's clock must widen too, or the twin is blind to more than one thing (#228 addendum) | MUST WIDEN | test_b2_picture_words.py:212; test_a4l_voice_seams.py |
| 4 | 1844, 1884 → 1424-1449 `_brain_canvas` | `tape_words = list(words_in_instant)` → `brain.learn(g, list(words))` | a list, tape order | the brain already hears every word | UNCHANGED | test_brain_mind.py:172 |
| 5 | 1853 → 3410 `_maybe_say` | `_last_words_in_instant` (the list) | a list | already every word | UNCHANGED | test_life_seams.py:122 |
| 6 | 1858 | `xw = encode_word(word, ...)` — ONE vector | one word | needs one vector per word (the draft's core input) | MUST WIDEN | — |
| 7 | 1860-1862 SURPRISE | `predicted = self.org.expected_sight(xw)` — ONE expected sight vector for the canvas | one word | which word's expectation? The last (shape) keeps today's; a multi-word canvas has no single expectation. Live in BRAIN-FULL (SURPRISE declared) | AMBIGUOUS | test_surprise_coarse.py |
| 8 | 1922 → `genome/predict.py:209-234` comparator arm | `winners_w` = top-KWTA cells of ONE `xw` | one word | under the union a sight cell's answer may be a colour cell; comparator then reads 1.0 (lr ×2, ranked first for SLEEP) though the canvas carried that word. `error comparator` is declared in BRAIN-FULL and ALPHA4 | MUST WIDEN | test_predict_arms.py |
| 9 | 1922 → `predict.py:177-192` conjunctive arm | `_word_seen[word]` counts the last word only | one word | colour words never counted. Declared only in `runs/g5-e-arms/genomes/G4-arm-conjunctive.genome` | AMBIGUOUS | test_predict_arms.py |
| 10 | 1981-1987 ARRIVAL | `arr_word = word` (last); `_heard.add`; `org.new_arrival()` | one word per canvas | does a never-heard NON-last word open an arrival (a fresh BUDGET)? In the scene world 7 words are never last (E) | AMBIGUOUS | test_b13_modulation_arrival.py |
| 11 | 3615 `resume` | `mind._heard = {v for v in mind.moment_word.values() if v}` — re-derived from LAST words | `_heard` ⊆ last words | if #10 widens, a resumed mind forgets every non-last word it heard and opens its arrival again: resume ≠ live | BREAKS (if #10 widens) | test_brain_mind.py:393-400, 489-492 (resume at a cut) |
| 12 | 1988-1991 | `moment_word[org.t] = ledger_word` (last) per glance → `build_ledgers` | every birth at moment t belongs to one word | word cells of non-last words are born at the same `t` and get the last word's label (see #30) | BREAKS | test_b2_picture_words.py:86; test_exam_one_word.py:50; test_mind_voice.py:123 |
| 13 | 2010 | `S, T = self.org.moment(x, xw, lr_scale=..., confirm=..., x_snd=...)` | one word vector | must pass every word's vector | MUST WIDEN | — |
| 14 | 2011-2014 | sound winners | — | untouched | UNCHANGED | test_mind_voice.py |
| 15 | 2019-2023 `episodes.write` | `x_w = xw` (one vector), `word = word`, `words_in_instant` | one x_w per episode | x_w stays the last word's; SLEEP (#20) then replays the last word only | AMBIGUOUS | test_words_in_instant.py |
| 16 | 2033-2035 → 2297-2389 `_score_due_predictions` | trigger `entry["target_word"] == word` (2340); decider `Lw.get(r["cell"]) == {word}` (2355) | the canvas has one word; recall's one answer should be it | a sight cell's single answer (argmax edge) may now be a colour cell → evidence FALSE on a canvas that carried the word → more FALSE outcomes → more QUESTION wants (2371-2386) | AMBIGUOUS | test_g9_line_scorer.py; test_question_sentence_mouth.py |
| 17 | 2041-2044 journal row | `"word": word` (last) | one word | the draft keeps it last. Its readers are on one-word maker moments (#63, #64) | UNCHANGED | test_mind_parity.py |
| 18 | 2068-2106 QUESTION (wordless sight) | `ledgers["sight"].get(cell) == {""}` | — | sight-only road, no word | UNCHANGED | test_question_sentence_mouth.py |
| 19 | 2081-2087 sight-only road | `moment_word = label or ""` | — | label None unless blind-ear | UNCHANGED | — |
| 20 | 2266-2275 `_maybe_sleep` → `genome/sleep.py:63` | `moment_word[t0+i] = rec["word"]`; `org.moment(rec["x_s"], rec["x_w"])` — one stored vector | one word per episode | the replay teaches the last word only while the live law meets every word | AMBIGUOUS | test_wave2_predict_fast.py |
| 21 | 2332-2338 frame trigger | `due = entry["target_word"] in words_in_instant` | a list | already a list | UNCHANGED | test_sentence.py; test_g9_line_scorer.py |
| 22 | 2391-2427 `_frame_evidence`, `_frame_evidence_line` | decider `Lw.get(cell) == {w2}`; docstring: «The line's MEET binds the canvas's glances to the chunk's LAST word only (`pending` is last-wins) … 0.430 when w2 is the last word, 0.183 when it is not» | last-wins | code reads the ledger (inherits #30); the G9 ceiling was measured under last-wins and no longer describes the road | AMBIGUOUS | test_g9_line_scorer.py |
| 23 | 2474-2483 `_recent_word_glances`; 2572-2583 `_latest_tape_moment_for_word` | `ep.word == word` over FAST | a word = the episode's last word | a non-last word has no episodes → no belief, no moment to ask about | AMBIGUOUS | test_question_sentence_mouth.py |
| 24 | 2609-2629 `_think_pool` word items | `rec["word"]` | last word | colour/size words never become word items | AMBIGUOUS | test_question_sentence_mouth.py:303-321 («the ONLY word this canvas writes to FAST ("ball")») |
| 25 | 2652-2660 INDUCE items → `genome/think.py:431-435` | `slots_of` keyed on `episodes.word[i]` | last word | non-last words never induced | AMBIGUOUS | test_induce_cost.py (twin of the INDUCE text) |
| 26 | 2676-2683 SENTENCE items → `genome/sentence.py:62` | `words_in_instant` | a list | already a list | UNCHANGED | test_sentence.py |
| 27 | 1211-1228 `_chat_guard` | `tuple(sorted(self.pending.items()))`, `pending_words` | compared by value | shapes unchanged | UNCHANGED | test_mind_chat.py:32 |
| 28 | 3478, 3482 `snapshot`; 3602-3603 `resume` | `ear_pending` (dict str→str), `ear_pending_words` (dict str→list) | both persisted since L-11 | nothing new to persist for the in-flight words | UNCHANGED | test_brain_mind.py:393 |
| 29 | 1230-1305 `_chat_content`, `_consume_chat` | `word_cells(org, Lw, w)`, `chain.thing_words` | the words ledger is true | code unchanged; reads the ledger (#30) | UNCHANGED | test_mind_chat.py:213 |

### B.2 The ledger and its readers (`genome/questions.py`, `creature/organs_road.py`, `genome/chain.py`, `creature/think_thread.py`)

| # | Where | Reads / writes | Assumes | Under the draft | Class | Pinned by |
|---|---|---|---|---|---|---|
| 30 | `genome/questions.py:25-41` `build_ledgers` | `for m, area, cid, _reason in org.births: (...).add(moment_thing[m])` | one word per moment | a word cell born at `t` for «red» is filed under the LAST word («circle»). Every reader of `Lw` inherits it (#31-#38, #62, #67, #73) | BREAKS | test_b2_picture_words.py:86; test_mind_voice.py:123,145; test_a4l_voice_seams.py:182; test_mind_parity.py:173 |
| 31 | `questions.py:264-287` `why` (episodes: 279) | cells by ledger `s == {word}`; episodes by `str(episodes.word[slot]) == word` | last word | cells inherit #30; a non-last word has no episodes | AMBIGUOUS | test_why.py |
| 32 | `questions.py:44-45` `word_cells`; `ask` (69-) / `ask_glances` Q1-Q4 | `Lw.get(cell) == {t}` | ledger true | code unchanged; inherits #30 | UNCHANGED | test_exam_one_word.py |
| 33 | `creature/organs_road.py:98-130` `answer_point` | `cells = {w: word_cells(org, Lw, w) for w in phrase}`; «unheard» when a phrase word has no cell | ledger true | today every colour/size phrase word reads «unheard» (0 cells). Code unchanged, but with #30 unfixed the colour cells sit under the shape's label and add to the shape's edge sum | UNCHANGED | test_brain_mind.py:242-257 |
| 34 | `organs_road.py:140-173` `answer_what`, `answer_say` | `_one_name(recall_many(...), Lw)` — one word | one word per sight answer | may now say a colour/size word; the graders accept it (M2b: «CORRECT = no SHAPE word emitted», `brain/scene/marks.py:283-286`; NAME read by world type) | UNCHANGED | test_brain_mind.py |
| 35 | `organs_road.py:176-196` `answer_why` → #31 | cites FAST episodes of `word` | last word | a colour word gets cells (if #30 is fixed) and no episodes → «because» with 0 episodes | AMBIGUOUS | test_brain_mind.py |
| 36 | `genome/chain.py:250-297` `_literal`, `thing_words` | `ledger_words` with `len(ws) == 1` | ledger true | inherits #30 | UNCHANGED | test_b2_picture_words.py; test_mind_chat.py |
| 37 | `chain.py:207` `birth_sources(..., per_canvas)` | glances per canvas | one moment per glance | the draft keeps it | UNCHANGED | test_b2_picture_words.py |
| 38 | `creature/think_thread.py:125-141` `freeze_inputs`; 84-98 `freeze_recall_view` | copies `moment_word` and `births`, then `build_ledgers` on the shadow (203) | the ledger is `moment_word` alone | any new birth→word map must be copied into the frozen copy, or the threaded think reads the old ledger | MUST WIDEN | test_life_e_think_thread.py:149 |

### B.3 The organism (`genome/machinery.py`, `genome/sleep.py`)

| # | Where | Reads / writes | Assumes | Under the draft | Class | Pinned by |
|---|---|---|---|---|---|---|
| 39 | 1449-1521 `Organism.moment(x_s, x_w, ...)` | `T = self._resonate(self.words, x_w)` once | one word | needs every word's vector. Other callers pass one vector and must stay byte-identical: `genome/sleep.py:63`, `genome/run_g1.py:104`, `tools/pin_g1.py:24`, `brain/arms/cells/a0.py:104` | MUST WIDEN | test_pin_skeleton.py (PIN_HASH_DEV 44f6fa81…) |
| 40 | 1426-1447 `_resonate` | births a novelty cell if nothing resonates; KWTA winners | — | called once per word; unchanged | UNCHANGED | — |
| 41 | 1486-1489 THRESH push | `if self._answer_of(self.sight, s0) == T[0]` — «T[0] the top word winner — the word cell of the moment's word» | T[0] is the moment's one word | with T in SPOKEN order, T[0] is the FIRST word's top cell («small», not «circle»); the push then tracks a different word than the ledger's last word | BREAKS | test_thresh_own_band.py |
| 42 | 1769-1780 `_hebb` | edges for S × T | sets | union T works as is | UNCHANGED | test_pin_skeleton.py |
| 43 | 1782-1806 `_delta` | `tgt_w[T] = 1` for every s in S; `tgt_s[S] = 1` for every t in T | sets | every sight winner is pulled toward every word of the utterance (the law's intent) | UNCHANGED | test_pin_skeleton.py |
| 44 | 1871-1893 `_misfire`, sight half | `ans = _answer_of(sight, cid)`; misfire unless `ans in T` | set-based | code works with the union; behaviour moves: a sight cell's answer is ONE word cell (argmax); a cell whose answer is «red» misfires when a «blue circle» is said → error births (BUDGET) | AMBIGUOUS | test_pin_skeleton.py |
| 45 | 1871-1893 `_misfire`, words half | redundancy `area.cells[cid] @ x > theta_m`, then `_birth(area, x, "error")` with `x = x_w` | one x_w | needs the vector of the word that lit `cid`. Well-defined: distinct words never co-resonate (C.3) | MUST WIDEN | — |
| 46 | 1895-1920 `_prune` | rows S, cols T | sets | unchanged | UNCHANGED | — |
| 47 | 1922-1968 `_merge(words, T)`, `_merge(sight, S)` | pairs with `cos > THETA_M` and the same answer | — | a cross-word merge cannot happen: word cells are exact encodings (novelty and error births both store the input) and distinct words have cos ≤ 0.875 < THETA_M 0.9969 | UNCHANGED | test_merge_fast.py |
| 48 | 1523-1554 `_sound_meets` → 1597-1623 `_pair_misfire(sw, U, T, x_snd, x_w, …)` | words-side error birth holds `x_w` | one x_w | same as #45. Dormant in the brain lives (no `AREA sound` declared) | MUST WIDEN | test_a4l_voice_machinery.py |
| 49 | 1837-1869 `expected_sight(xw)` | one word's best-lit cell → its strongest sight cell | one word | see #7 | AMBIGUOUS | test_surprise_coarse.py |
| 50 | 2017-2035, 2051-2130, 2143-2257, 2403-2420 `_lit`, `recall`, `recall_many`, `edge_many` | one query vector | query time | unchanged | UNCHANGED | test_why.py |
| 51 | 1269-1306 `new_arrival`, `_maybe_regen_budget`; 1373-1377 budget refusal | `budget_left` | — | unchanged code; the spend rate rises (more word births per canvas); depends on #10 | UNCHANGED | test_state_hash_grow.py |
| 52 | 1886-1889 `births_refused_redundant` → `genome/sleep.py:85-103` CYCLE share trigger | counter / alive | — | definition unchanged; its rate moves, so CYCLE (declared in BRAIN-FULL) fires on another cadence | UNCHANGED | test_merge_fast.py |
| 53 | `genome/sleep.py:36-70` `sleep` | `org.moment(rec["x_s"], rec["x_w"])` | one x_w per episode | see #20 | AMBIGUOUS | test_wave2_predict_fast.py |
| 54 | 2598-2735 `row_hash`, `state_hash` | hashes `self.c`, `self.births`, `self.merges`, W/mask | — | unchanged, IF no new field enters `self.c` or `org.births` (each would move every pin: the `moments_sight_only` precedent, 1175-1179) | UNCHANGED | test_pin_skeleton.py; test_state_hash_live_block.py |
| 55 | 150-859 `parse_genome` | unknown gene → `GenomeError(f"unknown gene {gene!r} …")` (858-859) | — | the law needs a parser branch (an edit to `genome/machinery.py`, pinned — C.1), a `RUNS` row in `creature/genes.py` (else `unwired()` refuses at `Mind.__init__`), and shows in `tools/inventory.py` | MUST WIDEN | test_refusal.py; test_parse_g4.py |

### B.4 Episodes and their readers

| # | Where | Reads / writes | Assumes | Under the draft | Class | Pinned by |
|---|---|---|---|---|---|---|
| 56 | `genome/fast.py:61-62, 88, 98-148` `Episodes` | `x_w` one vector; `word` `<U32`; `words_in_instant` `<U256` (the words joined by a vertical bar) | one word vector | x_w keeps the last word only (#15, #20). Measured max joined length 47 (no truncation) | AMBIGUOUS | test_words_in_instant.py |
| 57 | `genome/predict.py:194-207` episodic arm | `episodes.nearest(x_s)` | — | reads x_s only | UNCHANGED | test_predict.py |
| 58 | `genome/curiosity.py`, `genome/park.py` | want keys | — | no word/episode field read (grep) | UNCHANGED | test_curiosity.py |
| 59 | `genome/think.py:225` `believe`, `:487` `deduce` | beliefs keyed on word items (#24) | last word | inherits #24 | UNCHANGED | test_think.py |

### B.5 Tools and graders

| # | Where | Reads | Assumes | Under the draft | Class | Pinned by |
|---|---|---|---|---|---|---|
| 60 | `tools/verdict_g4.py:491-499` `rows_for_spec` shuffle_words (T-shuffle) | permutes `meta.word` across ALL ear rows | one word per moment | under last-wins this null already put colour words in last place, so the null met words the real life never met; under the draft both meet every word — the null's contrast changes meaning | AMBIGUOUS | test_verdict_reader_fix_0923.py:449-454 (rows_for_spec's filters; the shuffle itself: none found) |
| 61 | `verdict_g4.py:539-541` `_cross` | edges whose `L["sight"][sc] != L["words"][wc]` | a sight cell and its word cell share one label | with #30 fixed, every sight→colour edge counts as «cross» (sight label «circle», word label «red»); unfixed, colour cells are mislabelled | BREAKS | — |
| 62 | `verdict_g4.py:714-770` MODULATION; 1157-1192 folder/heard | journal `word` on maker `w…` moments; tape `meta.word` | one word | maker/folder moments carry one word | UNCHANGED | — |
| 63 | `tools/verdict_life.py:146, 346, 730` | journal `word` (plant showings, SURPRISE per thing, sizing) | the journal word | the draft keeps it last; the graded rows are maker rows (one word) | UNCHANGED | test_verdict_reader_fix_0923.py |
| 64 | `verdict_life.py:486, 789-826, 864-866, 1219` | tape `meta.word` lists per moment | a list from the tape | already per moment, tape order | UNCHANGED | test_verdict_life_marks.py:503-529 |
| 65 | `tools/self_exam.py:22-30, 123`; `creature/exam.py` | `ledger.json` `words` | ledger true | inherits #30 | UNCHANGED | test_exam.py |
| 66 | `tools/inventory.py` | RUNS rows + parser attrs | — | generic; the new gene needs a RUNS row to read MADE | UNCHANGED | — |
| 67 | `creature/replay.py:181-210`, `tools/replay_diff.py` | field-by-field compare | — | generic; closed lives replay identical only if the law is GATED on a gene their genomes lack | UNCHANGED | test_mind_parity.py |
| 68 | `tools/brain/grade_life.py:149-165, 493-509` | tape words per moment (all, in order); M4 «real» = `word in life.moment_words[m]` | a list | already a list; the organs twin's M4 answers change through #35 | UNCHANGED | none found (no test under tests/ names grade_life) |
| 69 | `tools/brain/parity.py`, `tools/brain/journal_diff.py`, `tools/lives/check.py` | no word field (grep) | — | — | UNCHANGED | — |
| 70 | `genome/ask.py:42-58`, `creature/ask.py:48-121`, `tools/answer_readtwin.py`, `tools/chat_ceiling.py`, `tools/hands_recognised.py`, `tools/read_recognised.py`, `tools/diag_g1.py` | `ledger.json` `words` | ledger true | inherit #30 | UNCHANGED | — |
| 71 | `tools/evolve.py:116-160` (the EVOLVE judge; EVOLVE is declared in BRAIN-FULL) | ledger.json `words` via self_exam (135); `surprise_mark` over the twin's journal rows (151) | ledger true; journal `word` | inherits #30 and #63 | UNCHANGED | — |
| 72 | `tools/lives/view.py:106` | `Counter(r.get("word") for r in moments)` — a display | journal `word` | shows the last word | UNCHANGED | — |
| 73 | `creature/body.py:370` STATUS | `arrivals`, `budget_left`, `births_refused_budget` | — | code unchanged; the numbers move with #10 and #51 | UNCHANGED | test_self_gene.py; test_verdict_reader_lag_0923.py |

Sweep for any other reader (`grep` for `["word"]`, `get("word")`, `moment_word`, `words_in_instant`, `.pending`, `_heard`,
`pending_words` over `tools/*.py`, `tools/lives`, `tools/b1`, `tools/scene`, `tools/toys`, `creature/*.py`, `judge/`, `world/`,
`deploy/`): the hits not in a row above are the outcome ring's act names (`creature/mind.py:1664`,
`tools/toys/act_chooser_toy.py:570` — `word` there is an ACT name, not the word road), the brain reader's own state
(`tools/scene/diag_tmem2_amend1.py:73`), the ask door's request fields (`creature/ask.py:140-146`) and RUNS descriptions
(`creature/genes.py:207-209`). `judge/`, `world/` and `deploy/` hold no reader. [Certain]

**Count by class (73 rows):** UNCHANGED 42 · MUST WIDEN 9 · BREAKS 5 · AMBIGUOUS 17. (Counted by script from the class
column above. BREAKS = #11, #12, #30, #41, #61. MUST WIDEN = #3, #6, #8, #13, #38, #39, #45, #48, #55. Two rows hang on
the ARRIVAL decision (#10): #11 breaks, and #3 must widen, only if a never-heard non-last word opens an arrival.)

---

## (C) Pins

### C.1 Pin lists over source bytes

| Pin | Where | What it pins | Hit by the law? |
|---|---|---|---|
| `WORLD_CODE` | `brain/scene/cache.py:81-83` | sha256 of `brain/scene/world.py`, `brain/scene/eye.py`, `brain/scene/cache.py`, `brain/world/seeds.py`, `brain/world/build.py`, `brain/world/organs.py`, `brain/glance_cache.py`, `genome/world.py`, `genome/gaze.py`, **`genome/machinery.py`**, `genome/eye.py`, `genome/retina_fast.py`, **`genome/ALPHA4.genome`**; `check_code` (90-96) refuses every scene cache drawn by other bytes; users: `Percepts.__init__` (249) and the diag/gate tools under `tools/brain`, `tools/scene` | **Yes.** Any parser branch or `moment` edit in `genome/machinery.py`, or a gene line in `genome/ALPHA4.genome`, refuses every cache under `RUNS = /data/dev/brain-runs/scene-organ-fm6`: a fresh root, a redraw, and `tools/brain/diag/cache_identity.py` with a planted bit (#245 (1)). [Certain] |
| `room_code` | `brain/scene/rooms.py:27-28, 184` | rooms.py's own sha | No. [Certain] |
| `PINS` + `_RETINA_FAST_PIN` | `genome/gaze.py:34-37, 46, 57-68` | alpha2 `organs/retina.py`, `organs/gaze.py`; `genome/retina_fast.py` | No. [Certain] |
| `PINS` | `genome/cochlea.py:37-40, 52-56` | E52 `gammatone.py`, `front.py` | No. [Certain] |
| `SOURCE_SHA256` | `brain/scene/slda.py:24-25` | a record of `genome-wt-b12/brain/arms/soft/readers.py` | No. [Certain] |
| PREREG sha checks | `brain/scene/run.py:78-99`, `run_s1c.py:88-90`, `run_s1c2.py:81`, `run_tmem1.py:99`, `run_tmem2.py:76-82`, `run_tmem5.py:160`, `brain/harness/bars.py:78` | signed documents / ceilings | No. [Certain] |

### C.2 Pins in tests

| Pin | Where | Tape | Hit? |
|---|---|---|---|
| `PIN_HASH_DEV = "44f6fa81…"` | test_pin_skeleton.py:23, test_mind_parity.py:29, test_wave2_predict_fast.py:25 | G4-skeleton on maker tapes, ONE ear row per moment (test_mind_parity.py:42) | No, if the law is gated and G4-skeleton does not declare it. [Certain for the tape shape] |
| `GOLDEN = "4598b746…"` | test_exam_one_word.py:96 | one word per moment (34) | No. [Certain] |
| `WORLD_PIN_SHA256 = "bd5db2cc…"` | test_world_pin.py:24 | world_maker output | No (no producer changes). [Certain] |
| `MASTER_2357347_INDUCE_SHA256` | test_induce_cost.py:117 | pins the TEXT of an INDUCE twin; the test asserts live `induce` = twin | **Yes, if INDUCE widens** (#25) — the equivalence fails by design. [Certain] |
| `fixtures_brain_law_pre_fm6.json` | test_brain_fm6.py:19 | the brain organ's own state (`genome/brain.py`) | No (the brain already hears every word). [Certain] |
| `LeanVsTwin` | test_brain_genomes.py:50-61 | BRAIN-LEAN vs BRAIN-LEAN-TWIN differ by the BRAIN line only | **Yes, if the gene enters BRAIN-LEAN and not BRAIN-LEAN-TWIN.** [Certain] |
| `FullEqualsAlpha4PlusTwo` | test_brain_genomes.py:64-75 | `declared(BRAIN-FULL) − declared(ALPHA4) == {BRAIN, WORLD_SCENE}` | **Yes, if the gene enters BRAIN-FULL and not ALPHA4.genome** — and adding it to ALPHA4.genome moves WORLD_CODE (C.1). [Certain] |
| `test_the_closed_lives_genomes_are_untouched` | test_brain_genomes.py:152-157 | the closed lives' genomes under `genome/brain/lives/` | only if those files are edited (they must not be). [Certain] |
| `unwired()` law | `creature/genes.py:280`; test_refusal.py | every declared key needs a RUNS row | **Yes** — a new declared key refuses at `Mind.__init__` until its row exists. [Certain] |

### C.3 A structural fact that closes two questions (measured)

Every words-area threshold on disk is ≥ 0.9. Of the 78 `.genome` files in the tree, 77 carry a numeric `BIRTH novelty
cos<`; the one that does not is `tests/genome/G4-draft.genome`, whose line is the placeholder `cos<THETA_N` (the parser
refuses a placeholder, so it cannot run a life). Of the 77, seventy carry 0.95-0.968 (the words area uses THETA_N when no
RESONATE line); the seven G3 genomes carry a low sight THETA_N (0.36-0.576) and `RESONATE sight nearest words cos>=0.9`,
which sets the words floor at 0.9. All 42 closed-life genomes (`/data/dev/genome-lives/*/GENOME.genome`) carry
`BIRTH novelty cos<0.952` and `MERGE cos>0.9969`. No genome uses `blank=zero`. Under `SENSE ear letters 8` two distinct
words share at most 7 of 8 slots, so their cosine is at most 0.875. Measured over every word heard on the six tapes: max
cosine between two distinct words = **0.875** (3,340 words, alpha4-1 whole tape) and 0.625 (14 words, the lean lives).
So a words cell is lit by exactly one word, and two words' cells can never merge (0.875 < THETA_M 0.9969). [Certain]
This makes #45 and #48 well-defined; it does not make them automatic.

---

## (D) Tests that pin the one-word shape

| Test | Line | What it pins | Moves when |
|---|---|---|---|
| test_mind_chat.py | 32-33 | the chat guard's state dict: `pending`, `pending_words`, `len(moment_word)` | only if `pending` changes type |
| test_question_sentence_mouth.py | 54 | «ear THEN eye … or `self.pending` never carries the word» | never (order law holds) |
| test_question_sentence_mouth.py | 303-321 | «the ONLY word this canvas writes to FAST ("ball" -- self.pending keeps the LAST ear row)» | if FAST's `word`/`x_w` widens |
| test_b2_picture_words.py | 86, 160, 212 | `build_ledgers(mind.org, mind.moment_word)["words"]`; the blind-ear twin's empty `words_in_instant` | if #30 or #3 change |
| test_exam_one_word.py | 50, 96 | the exam's ledger + GOLDEN | if #30 changes on a multi-word tape (its tape is one word) |
| test_mind_voice.py | 123, 145 | `build_ledgers` on the voice tape | if #30 changes |
| test_a4l_voice_seams.py | 182 | `build_ledgers(shadow, m.moment_word)` | if #30 / #38 change |
| test_mind_parity.py | 173 | ledger keys `last_seq, moment_word, moments, sight, words` | if a new ledger key is REQUIRED |
| test_life_e_think_thread.py | 149 | the frozen `moment_word` is a copy | if #38 adds a map |
| test_life_seams.py | 122 | `_last_words_in_instant = ["red", "ball"]` | no |
| test_g9_line_scorer.py | 93-170 | the G9 line scorer's triggers per source | if the law is declared in its genome |
| test_induce_cost.py | 117 | the INDUCE twin (keyed on `episodes.word`) | if INDUCE widens |
| test_thresh_own_band.py | — | the THRESH push on `T[0]` | under #41 |
| test_words_in_instant.py | 20-77 | the Episodes columns | if `x_w` widens |
| test_sentence.py | 19-70 | `find_frames` over `words_in_instant` | no |
| test_brain_genomes.py | 50-157 | the templates (C.2) | if the gene enters one template and not its pair |
| test_brain_mind.py | 172, 393-400, 489-492 | the brain hears the tape's words in order; resume at a cut | the resume test must run under the new gene with ARRIVAL (row #11) |

---

## (E) What the closed tapes carry — measured

Method: `measure_utterances.py` walks each tape in seq order and runs the mind's own rule (`consume` ear branch; the pop in
`_consume_eye`), measured at the eye row. **Positive control:** the simulated last word equals the journal's canvas-row
`word` on 10,000 / 10,000 (each lean life), 12,867 / 12,867 (brain-full) and 38,420 / 38,420 (alpha4-1 lived) rows.
**Planted control:** a FIRST-wins simulation mismatches the journal on 7,485 of 10,000 (lean-1101, exactly its 2- and
3-word moments) and 7,699 of 12,867 (brain-full). Torn lines 0, NUL lines 0 on every tape. Presence: every ear row on
every tape carries `meta`, `meta.moment`, a truthy `meta.word` and `meta.source` (e.g. lean-1101 19,968 of 19,968;
alpha4-1 lived 50,743 of 50,743). Ear rows after their own eye row: 0 in every lived window (30 in alpha4-1's resurrected
tail). Ear moments left pending at the end: 0 everywhere. [Certain]

Windows: each life is read up to its last lived seq (the max journal seq before the first `stop` event). For the four
lean lives and brain-full that is the whole tape (ledger `last_seq` agrees). **alpha4-1**: lived seq ≤ 93,188 (its stop
at 2026-09-24T01:00:44Z); its tape holds 110,111 more rows: the journal's resurrection row says `resumed_from_seq 93188, backlog_replayed 464`
(464 rows the mind had not yet consumed when it stopped [Likely]), then the reboot's resurrected tail (#240). The tail is not
the life and is reported apart. brain-lean-nearest-20261102 has a different tape
(sha256 f7507975… vs 9eb89791…, same byte length) from brain-lean-20261102, and the same plan: every count below is equal.

| Life (window) | rows | ear | eye | met moments | 1 word | 2 | 3 | 4 | 5+ | distinct words | ever last | NEVER last (tokens) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| brain-lean-20261101 | 34,443 | 19,968 | 11,464 | 10,000 | 2,515 | 5,002 | 2,483 | 0 | 0 | 14 | 7 | 7 (9,968) |
| brain-lean-20261102 | 34,477 | 20,006 | 11,464 | 10,000 | 2,503 | 4,988 | 2,509 | 0 | 0 | 14 | 7 | 7 (10,006) |
| brain-lean-20261103 | 34,418 | 19,952 | 11,464 | 10,000 | 2,556 | 4,936 | 2,508 | 0 | 0 | 14 | 7 | 7 (9,952) |
| brain-lean-nearest-20261102 | 34,477 | 20,006 | 11,464 | 10,000 | 2,503 | 4,988 | 2,509 | 0 | 0 | 14 | 7 | 7 (10,006) |
| brain-full-20261102 | 38,173 | 21,678 | 12,867 | 11,204 | 3,504 | 5,074 | 2,514 | 103 | 9 | 270 | 240 | 30 (10,121) |
| alpha4-1 (lived, seq ≤ 93,188) | 93,188 | 50,743 | 38,420 | 38,127 | 32,562 | 1,946 | 238 | 3,368 | 13 | 1,860 | 1,822 | 38 (1,325) |
| alpha4-1 (whole tape, not the life) | 203,299 | 112,489 | 84,598 | 84,305 met at an eye row (84,275 distinct) | 73,148 | 2,373 | 592 | 8,179 | 13 | 3,340 | 3,315 | 25 (280) |

By source (met moments, words per moment):

| Life | scene | game | shelf | lexicon | maker | folder |
|---|---|---|---|---|---|---|
| the four lean lives | 1: 2,503-2,556 · 2: 4,936-5,002 · 3: 2,483-2,509 | — | — | — | — | — |
| brain-full-20261102 | 1: 2,503 · 2: 4,988 · 3: 2,509 | 2: 81 | 1: 450 · 2: 5 · 3: 4 · 4: 103 | 3: 1 · 5+: 9 | 1: 472 | 1: 79 |
| alpha4-1 (lived) | — | 2: 1,573 | 1: 15,542 · 2: 373 · 3: 238 · 4: 3,365 | 1: 2 · 4: 3 · 5+: 13 | 1: 16,712 | 1: 306 |

Words never last (the words no organism cell ever met):
- **Every lean life:** big, small, blue, green, red, white, yellow — every size and colour word. Ever last: circle, cross,
  dax, ring, square, star, triangle. Non-last tokens are 49.9-50.0 % of all ear tokens (e.g. 9,968 of 19,968).
- **brain-full:** 30 — the same 7 scene words, the game's colours (red 65, purple 16 first; box / ball last), and 23 gloss
  words (lexicon 23, scene 7, game 2; a word can have two sources).
- **alpha4-1 lived:** 38 — lexicon 33, game 5 (the game said red 267, purple 128, grey 256, yellow 256, blue 282, green 384
  times, always first; box / ball / key last; «blue» is absent from the list because some other moment had it last). **The shelf leaves no word unmet**: its default shape shows each word alone
  on its own moment before the line (A).

Utterances with a repeated word: 0 (lean) · 7 (brain-full) · 113 (alpha4-1 lived). Longest utterance: 3 (lean) · 8
(brain-full, alpha4-1). Longest `"|".join(words)`: 20 · 45 · 47 characters (the Episodes column holds 256).

Five examples per life (evenly spaced among the multi-word moments; the last word in brackets):
- brain-lean-20261101: small yellow [circle] · yellow [square] · red [cross] · big [square] · small [star]
- brain-lean-20261102 (and -nearest-, same plan): small [star] · blue [cross] · blue [star] · red [ring] · blue [star]
- brain-lean-20261103: small [circle] · big [ring] · small blue [ring] · big [ring] · white [triangle]
- brain-full-20261102: red [box] (game) · big [square] · blue [star] · small green [cross] · yellow [circle]
- alpha4-1 lived: the project gutenber [ebook] (shelf) · green [box] (game) · grey [box] (game) · and do not [waste] (shelf) · o b g [illustra] (shelf)
- a gloss (brain-full, lexicon): a polygon with three sides and three [angles]

---

## (F) RISKS — where the draft is AMBIGUOUS or BREAKS, and the question the PREREG must answer

1. **The words ledger (#30, BREAKS).** `build_ledgers` files every birth under `moment_thing[m]`, one word per moment.
   Under the draft, «red»'s cell is born at the same `t` as «circle»'s and is filed as «circle». Every reader of `Lw`
   inherits it: Q1-Q4, `word_cells`, the organs' road, self_exam, `chain.thing_words`, INDUCE clusters, `_frame_evidence`,
   `verdict_g4._cross`, the ask doors. *Question:* where does the birth→word map live? It must stay out of `org.births`
   and `self.c` (both hashed, #54); be persisted in ledger.json; be copied by `think_thread.freeze_inputs` (#38); be
   rebuilt the same way on sleep births (#20). Pin it with a test that fails on today's code: a two-word tape where
   `Lw[cell_of("red")] == {"red"}`.
2. **ARRIVAL and resume (#10, #11).** Does a never-heard non-last word open an arrival (a fresh BUDGET)? If yes,
   `resume` must stop re-deriving `_heard` from `moment_word` (3615) — persist it, or derive it from the new map — and the
   blind-ear twin's clock (#3) must widen with it. *Test:* resume at a cut after a colour word is heard, then replay: equal
   journals.
3. **THRESH's anchor (#41, BREAKS).** `T[0]` becomes the FIRST spoken word's top cell. *Question:* is the push «the sight
   cell's answer is ANY word of the moment», «the last word's», or «the first word's»? Name it; do not inherit it from
   list order.
4. **Error births in the words area (#45, #48).** `_misfire` and `_pair_misfire` birth with the one `x_w`. *Question:* the
   rule «the cell's own lighting word's vector» — state it (C.3 shows the map is unique on every genome on disk; the PREREG
   should say what happens if a future genome drops the words floor below 0.875).
5. **SLEEP and the episode ring (#15, #20, #53, #56).** The ring stores one `x_w`. Under the draft SLEEP replays the last
   word only, while the live law meets every word. *Question:* does a replayed episode meet every word of its instant
   (re-encoded from `words_in_instant`, a pure function), or only the last? If every word, the sleep-born word cells need
   the #1 map too.
6. **SURPRISE's expectation (#7, #49).** One `predicted` vector per canvas. *Question:* whose — the last word's (today),
   or none on a multi-word canvas? Live in BRAIN-FULL.
7. **PREDICT comparator (#8, MUST WIDEN).** `winners_w` from one `xw`. Unwidened, a sight cell that answers a colour word
   reads error 1.0 (lr ×2, first in SLEEP's queue) though the canvas carried that word. *Question:* confirm «winners_w =
   the union».
8. **The sight misfire (#44).** A sight cell has ONE answer (argmax edge). In the scene world every shape comes with
   several colours and sizes; a cell whose answer becomes «red» misfires on every «blue circle», and each misfire can
   birth an error cell and spend BUDGET. *Question:* is «answer ∈ T» the law (a set-based test, as today), knowing it may
   split sight cells by colour? Price the birth rate on a toy before the life; put `births_refused_budget` and
   `births_refused_redundant` series beside it (#238).
9. **The think road stays last-word (#16, #23, #24, #25, #31, #35).** Predictions, beliefs, INDUCE rules, QUESTION
   moments and `why` episodes all key on FAST's `word`. Under the draft colour/size words have cells but no episodes: `why
   red` answers «because» with 0 episodes; no belief or rule is ever formed about «red». *Question:* keep the think road
   last-word (and say so as a declared limit), or key it on `words_in_instant`? Widening INDUCE moves the
   test_induce_cost.py twin by design.
10. **The prediction decider (#16).** `Lw.get(recall(first_glance).cell) == {word}` asks for the last word. With a union,
    the one answer can be a colour cell → FALSE on a canvas that carried the target word → more QUESTION wants.
    *Question:* the pass rule on a multi-word canvas.
11. **SENTENCE G9's ceiling (#22).** The 0.430 / 0.183 ceilings were measured under last-wins. Re-measure before any G9
    reading under the new law. Do not re-derive the bar.
12. **The cross-edge mark (#61, BREAKS).** `verdict_g4._cross` counts edges whose sight and word labels differ. With a true
    words ledger every sight→colour edge is «cross». *Question:* redefine the mark (a sight cell's label set vs the word),
    or declare it NOT GRADABLE under the new law.
13. **The T-shuffle null (#60).** It permutes words across all ear rows. Under last-wins it made the null meet colour words
    the real life never met; under the new law both meet them. *Question:* is the null's removal still «words detached from
    sight» only?
14. **The pins (C).** Any edit to `genome/machinery.py` or `genome/ALPHA4.genome` refuses every scene cache (WORLD_CODE).
    Adding the gene to one template of a pair breaks LeanVsTwin or FullEqualsAlpha4PlusTwo. Gate the law on a gene the
    closed lives' genomes lack, or their replays diverge.
15. **Duplicates (E).** 113 alpha4-1 moments say a word twice (e.g. «to instruct to teach»). *Question:* the union is a set
    in first-occurrence order; ARRIVAL and the ledger count a word once per moment. State it.
16. **A new encode path.** Under the draft every non-last word reaches `encode_word` for the first time; it RAISES on a
    word over 8 letters or outside a-z. Measured 0 such words on every tape, and every producer filters (A). Keep a test
    that a bad non-last word refuses by name and does not crash the mind (#230).

---

## (G) What the draft law gets wrong (or leaves unsaid)

1. **«The ledger's word stays the LAST word» is two ledgers, not one.** For SIGHT cells (the thing shown) the last word is
   a choice the PREREG can make. For WORD cells it is wrong: `build_ledgers` would file every non-last word's cells under
   the last word (#30). The draft must split them: the sight ledger may stay `moment_word`; the words ledger needs its own
   birth→word map.
2. **«In spoken order» silently moves THRESH.** Today `T[0]` is the only word's top cell. With spoken order it is the first
   word («small»), while the ledger names the last («circle») (#41). The draft names an order but not which word anchors
   the own band.
3. **«Each word keeps its own vector for its own birth» covers novelty, not the error-birth inputs.** `_misfire` and
   `_pair_misfire` read one `x_w` (#45, #48). The draft should name the cell → word map these read (unique, C.3).
4. **One moment per glance keeps the clock, but not the BUDGET's meaning.** More births per moment spend the one budget
   faster, and ARRIVAL is keyed on one word per canvas (#10, #51). The draft says nothing on ARRIVAL; the lean lives'
   world has 7 words that are never last, so the choice is not rare.
5. **SLEEP is not the live law.** The draft keeps FAST's `x_w` as the last word, so every replayed moment is one-word
   (#20). A law «the organism meets every word» that sleep does not obey is two laws.
6. **The think road stays one-word without saying so (#9 in F).** Name it as a declared limit, or widen it.
7. **The twin.** The draft keeps «the one-word road as the twin». The twin is today's code; but #3 (blind-ear bookkeeping),
   #8 (comparator) and #20 (sleep) must be read so the twin differs from the new road by the word road ALONE, not by
   ARRIVAL or SLEEP as well (#228's addendum: a control blind to exactly one thing).
