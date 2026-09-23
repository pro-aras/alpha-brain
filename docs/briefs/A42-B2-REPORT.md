# A42-B2 — REPORT (WORK IN PROGRESS: the session closed at the coordinator's word) · builder B2, Claude Opus 5.5 · branch `a42-b2` off `a4-integration` `a50b0f3` · worktree `/data/dev/genome-wt-b2` · written 2026-09-23 16:36 +0400

## WIP — what is NOT done (read first)
- **NOTHING IS BUILT.** No code changed, no test written: no RED and no GREEN log exists. This commit holds this note only.
- **PART 1 (G9), step 1, the CEILING: NOT MEASURED.** Neither the hour-1 fixture nor the 10:54 snapshot copy has been read for the ceiling yet. No number below is a ceiling. The clause is neither built nor refused.
- **PART 2 (the birth-source ledger): NOT STARTED.** A design question is open (below, item P2-1). It must be decided before any code.
- Not run: both suites, gate_g4 1/2/3/6, `tools/gate_g5_landing.sh a42-b2`, the undeclared-identity replay.
- Nothing under `/data/dev/genome-lives/` was read or written. The fixtures were read in place and not changed. No copy has been made yet.

## The next step, in order (for the session that picks this up)
1. Copy the fixtures to `scratch/` (hour-1 tape + payload, the 10:54 snapshot). Run the BASELINE: this tree + `genome/ALPHA4.genome` replays the hour-1 fixture. Compare it to the control `/data/dev/genome-wt-induce/scratch/replays/h1-alpha4-master/journal.jsonl`, masked on `readiness` (`tools/replay_diff.py … --ignore readiness`). Use `nice -n 19` and BLAS threads 1. Wait while the 1-min load is above 12.
2. **The CEILING** (a scratch instrument that sits OUTSIDE the mind's road):
   - (a) On the hour-1 replay, at every shelf SENTENCE moment (a multi-word instant, after its MEET, where the scorer runs), do this for every shelf frame the mind has filed, and also for every find_frames shelf pair, whose w1 AND w2 are both on the line: does ANY of the line's glances `recall("sight", x)` return a words cell whose ledger is exactly {w2}?
   - (b) Do the same on a COPY of the 10:54 snapshot. Re-render the ring's shelf sentence instants (`read_common.render_line(" ".join(words_in_instant), 128, DEFAULT_FONT)` — the reader's own renderer, words already cut to 8). Glance them with `gaze.glances` and read-only recall.
   - Print the ceiling beside the old scorer's 0/63. Split it: (i) w2 is the chunk's LAST word vs not; (ii) located glances only vs with the coarse glance. If the ceiling is below 0.1, REFUSE and build nothing.
3. Only if the ceiling is 0.1 or more: write the tests RED first (the toy with planted line moments; the declared scorer), then the clause (the parser plus the scorer), then UNDECLARED byte-identity and a DECLARED replay that prints the shelf true/false counts.
4. PART 2 after item P2-1 is decided.

## What the orientation established [Certain: read off the code and the fixture]
- **The scorer:** `creature/mind.py:1998` `_score_due_predictions`. A frame entry is due when `entry["target_word"] in words_in_instant` (w1 anywhere in the instant). The evidence is `_frame_evidence(w2, first_glance)` (`:2070`): `recall` on the canvas's FIRST glance only, and the answer cell's ledger must be exactly {w2}. It is called from `_consume_eye` (`:1756`) on the worded road, after the canvas's MEET loop, with `g["feats"][0]`.
- **Why shelf frames score 0:** the reader's default shape is two moments (`creature/body.py:617` `_read_shape_from_argv`: `one_word_moments=True` unless `--read-single-moment` is given). `creature/senses/read.py:164` `_publish_chunk` publishes one moment PER WORD first (ear w + eye w rendered large). Only then does it publish the sentence moment (every word as an ear row + the rendered line). So a shelf frame is first due on w1's ONE-WORD moment, and it is scored against a canvas that shows only w1.
- **On the sentence moment, `pending` is last-wins.** MEET binds the line's glances to the chunk's LAST word only (the reader's own docstring says so). The ceiling must therefore be split by whether w2 is the chunk's last word. [Likely: the ceiling where w2 is not the last word is low. Not yet measured.]
- **What the hour-1 fixture holds** (`/data/dev/a4-ladder/fixtures/alpha4-1-hour1/tape/2026-09-23.jsonl`, 4,581 rows):
  - shelf eye rows: 825 = 645 per-word + 180 sentence moments. By words per sentence moment: 4 words ×148, 3 ×6, 2 ×9, 1 ×17.
  - game: 121 eye rows, 2 words each.
  - maker: 722, 1 word each.
  - folder: 119, 1 word each (plus one row with no name).
  - **lexicon: 4 eye rows with 8 words each.** These are also multi-word instants, so the new due rule would fire on a lexicon gloss that carries w1. The clause must name this, or restrict itself to the shelf.
  - hands: 26 rows, 0 words.
- **The undeclared-identity control:** `/data/dev/genome-wt-induce/scratch/replays/h1-alpha4-master/journal.jsonl` (4,322 rows; master `2357347` + ALPHA4.genome) is byte-identical to `/data/dev/a4-ladder/fixtures/ref-floor/journal.jsonl` (checked with `cmp`). `genome/ALPHA4.genome` is identical to the fixture's `GENOME.genome` (checked with `diff`).
- **The 10:54 snapshot's `ledger.json` keys:** last_seq, moment_word (55,200), moments, ear_pending, ear_pending_words, sight (6,896 cells → the words heard at their births), words (753), predictor_last_winner, act/hands rng states, hands_*, stage, grades, sit_readings, web_*. **It has no birth-source key.** The ring holds 10,160 episodes and has not wrapped.

## P2-1 — an open design question for the orchestrator (RAISED before any code)
`genome/chain.py:thing_words` reads FAST's ring twice:
- `birth_sources` maps each birth to a live episode's `source`. A birth older than the oldest live episode reads «?».
- `heard_on_pictures` collects the words of live episodes whose source is a picture source.

Both reads shrink when the ring wraps. The brief defines «born» in one line: words whose word cell has a MEET edge to a sight cell born on a picture source, the source read from the ledger. That is the **LITERAL** rule over a ledger source. By the LANG report, it held **119** words on the 10:54 copy («a · is · it · the» among them). «heard» holds **29–30**. So «born», as written, cannot agree with «heard» today.

Agreement needs the heard-on-pictures half to come from a ledger too. One way is a second, monotone ledger key (e.g. `picture_words`, written when a picture-source instant is consumed); the rule would then be the literal-from-ledger set ∩ that key. Planned: build that, keep the literal-from-ledger set printed as the twin, and say so here. The orchestrator can refuse it.

**The proof on the 10:54 copy has a second problem.** An old snapshot has no source key, so its «born» set can only be back-filled from its ring. That makes it equal to «heard» by construction, which proves nothing. The honest proof is the hour-1 replay: the ledger written at birth vs the ring-derived set. The synthetic 200-episode wrap is the RED.
