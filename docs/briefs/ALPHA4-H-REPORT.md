# Builder H report — THE READER and THE LEXICON DOOR
*edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:55 +0400. Branch `alpha4-read`, worktree `/data/dev/genome-wt-y`, off master `74c661d`. Brief: `docs/briefs/ALPHA4-H.md`. Law: `docs/ALPHA4-PREREG.md`.*

## What is NOT done, and why

1. **`tools/verdict_g4.py`'s `M["READ"] = ...` wiring is not landed.** The brief's own deliverable is "the READ mark in `tools/verdict_life.py`" (task 4's header) — that pure function exists, is tested, and is proven against a real closed record (seam-1, below). `verdict_g4.py` is a single ~900-line file every other ALPHA4 builder (G, I, J, K) also edits in the same dispatch; wiring into it now would be the lowest-value addition (advisor's own read, confirmed before I built anything) for the highest merge-conflict risk. `M["SENTENCE"]`/`M["HANDS"]` show the exact three-line pattern (`_hrows = ...; M["HANDS"] = _vl.hands_mark(...)`) the integrator can paste in, using `read_mark(tape, live, "SENSE_READ" in decl, recog, recog_blind)`.
2. **No real 50-held-out-word list exists yet, because no real ALPHA4 life has been born yet.** `tools/read_recognised.py:recognised_share` takes any word list; the natural selection at real-verdict time is "50 words `read_words_born`'s own moment-source map shows were actually bound from the shelf" — noted here as the one small step whoever runs the 24 h verdict still needs, not built speculatively against data that doesn't exist.
3. **The `H×I` seam (one renderer) is satisfied structurally, not tested against builder I's actual code**, which lives on a sibling worktree I never touched. `creature/senses/read_common.py` is written exactly as the brief's READ FIRST line describes it — "a PURE module both doors use" — so builder I's web door importing `render_line`/`png_bytes`/`DEFAULT_FONT_PATH` from it is a one-line `from .read_common import ...`, not a rewrite. The `G×H` seam (reading under unbounded growth, builder G's own worktree) is likewise unreachable from here; both are integration-time work.
4. **THE CEILING FIRST forced a genuine design change** (see below) — the brief's own task-2 literal genome-line design (one moment per sentence-chunk) is now the `--read-single-moment` FALLBACK, not the default. This is not a deviation taken lightly: it is exactly what task 0 itself instructs ("build that shape only if the toy under it reads higher; never loosen the bar"), decided by two real ~16-minute lives, not by argument.
5. **A clause of task 4's own text could not be implemented as written — RAISED, not silently reinterpreted**: "50 shelf words held out by the mark (never among the first N read)" contradicts, in the same sentence, "the mechanism is MEET sight-words on the rendered line." `org.recall_many("sight", …)` can only ever answer with a word some sight glance was bound to; a word the life never heard has no words-cell, so the mark would read exactly 0 on every such word by construction (#228 (b)'s class), never distinguishing "the reader works" from "the reader was never tested on this word." PREREG §5's own sentence never says the WORD is held out — only that the mark runs "on 50 held-out shelf words" with the FONT named as what is held out. I implemented PREREG's coherent reading (words the life DID hear, rendered in a font it never met) and used it for both the toy and the real `read_mark`/`read_recognised.py`. Full reasoning in `tools/read_recognised.py`'s own module docstring, written BEFORE any toy ran (caught by the advisor at the pre-work checkpoint, not after a bad number came back).

## Task 0 — THE CEILING FIRST

Built, in order: `read_common.py` (task 1) → the genome parser branches + `read.py` (task 2) → `tools/read_recognised.py` (the reading-mark slice of task 4, needed to measure anything) — then ran the toy, per the brief's own dependency (task 0 needs 1/2/4 to exist first).

**Toy shelf:** 200 synthetic sentences (3–7 words, deterministic seed 20260923) over a closed 40-word vocabulary, each word the deliberate LAST word of exactly 5 sentences (shuffled placement, so a partial run still samples every word). Built by `scratch/build_ceiling_toy.py`. **Toy genome:** `genome/LIFE.genome` verbatim minus the `WORLD game …` and `HANDS …` lines (the advisor's own read: neither bears on whether MEET can read a line; the maker and the folder door are kept — "the real nursery's competitor for attention") plus `SENSE read shelf <toy> curriculum <toy> every 5 s words 8 canvas 128`. Two real lives, ~16 minutes each (`timeout --kill-after=30 -s TERM 960`, `nice -n 10`), `--folder` pointed at an empty dir for determinism, both ended cleanly (`sense_restarts: 0`, `crash: null`, 4 and 15 snapshots respectively).

| | design | live share (40 words, held-out font) | blind twin |
|---|---|---|---|
| **Toy 1** | task 2's literal genome line: ONE moment per chunk (`self.pending[moment]` is last-wins, so only the chunk's LAST word ever gets a words-cell) | **0.15 (6/40)** | 0.00 (0/40) |
| **Toy 2** | task 0's own candidate: for every chunk, ALSO one extra moment PER WORD (word alone, shown large — world_maker.py's own proven one-word-one-moment road), plus the whole-line "sentence moment" for `SENTENCE`'s frame-finder | **0.60 (24/40)** | 0.00 (0/40) |

Both blind twins (`read_recognised.blind_twin_root`: a fresh Mind fed the SAME tape with every `source=="shelf"` row dropped) read exactly 0 — the instrument is sound; the 4x gap between designs is real, not noise in the ask road. Recognised under toy 1: `ant big cat mud oar sit`. Recognised under toy 2: 24 of 40, including every one of toy 1's six plus 18 more.

**Why toy 1 reads so low — two compounding causes, not one:** (a) MEET (`creature/mind.py:_consume_eye`) binds every LOCATED glance of a canvas to `self.pending[moment]`, which the `ear` branch overwrites, never appends — so of an (up to) 8-word chunk, only the LAST word's words-cell ever forms an edge to ANY of that canvas's sight glances; the other ≤7 words are heard (they reach `pending_words` for `SENTENCE`) but never bound to sight at all. (b) A second, independent effect the toy also exposed: `tools/read_recognised.py`'s own test render (a single word, alone, large) matches design 2's OWN training distribution exactly, but NOT design 1's — design 1 never once shows the eye an isolated word, only 3–7-word lines. PREREG §5's own mark ("a written word") tests isolated words either way, so design 1 carries a train/test rendering mismatch baked into the mark's own definition, on top of the binding defect. Both reasons point the same direction, which is why the toy's own numbers, not an argument, decided the redesign.

**Decision (task 0's own rule, applied): the two-moment shape is now the PRODUCTION default** (`creature/body.py:_read_shape_from_argv`, `--read-single-moment` the one override, pinned by `tests/creature/test_read_door.py::TestReadShapeFromArgv`). The bar was never loosened: toy 1's 0.15 is reported as measured, not rounded up or excused.

## What landed, with file:line

1. **`creature/senses/read_common.py`** (112 lines, new) — `split_sentences`, `words_of` (lower-case, a–z only, each word truncated to its first `letters` chars — `genome/world.py:WORD_SLOTS`'s own limit, so a shelf word can never crash the mind via `encode_word`'s `ValueError`), `render_line` (PIL, word-wrapped, deterministic — pinned by same-bytes-twice tests), `png_bytes`. `DEFAULT_FONT_PATH`/`HELDOUT_FONT_PATH` (DejaVu Sans/Serif, both verified present on this box before being hardcoded) are the ONE constant both `read.py` and `tools/read_recognised.py` import, so the sense and the mark cannot drift apart.
2. **`genome/machinery.py:parse_genome`** (+26 lines) — two new `elif` branches before the final `unknown gene` refusal: `SENSE read shelf <sqlite> curriculum <md> every <n> s words <k> canvas <px>` → `declared["SENSE_READ"]`; `DOOR lexicon <sqlite> answers what-is by showing` → `declared["DOOR_LEXICON"]` (`DOOR` is a brand-new top-level keyword, dispatched on `args[0]` exactly like `SENSE`/`WORLD` — builder I's `DOOR web …` is a sibling `elif`, landing beside this one at integration). Both refuse a misspelt form by name (`tests/genome/test_read_lexicon_parser.py`, 12 tests, including a pin against the LITERAL bytes of `genome/ALPHA4.genome`'s own two lines).
3. **`creature/genes.py:RUNS["body"]`** (+6 lines) — `SENSE_READ`/`DOOR_LEXICON` entries naming their real call sites, so `unwired()` never refuses them and `tools/inventory.py` reads MADE, not DECLARED-ONLY (below).
4. **`creature/senses/read.py`** (211 lines, new) — the sense thread. Cursor `root/read/CURSOR.json = {doc_id, sentence_ix, chunk_ix}` (extended by one coordinate beyond the brief's literal "doc_id + sentence index," documented in-file, because a sentence longer than `words` needs a THIRD coordinate to resume mid-sentence), written only after rows are durable (#230's law). `_nursery_docs`: `format='text'` rows only, every path containing `holdout` or ending `.jsonl` excluded — verified directly against the real `/data/alpha3-library/SHELF.sqlite` (2,103 rows → 2,094 after exclusion; the 9 excluded are exactly the K/mathematics `*.{train,holdout}.jsonl` family + one `G1-G3/…/facts.jsonl`), ordered K → G1-G3 → G4-G8 → G9-G12 → College → University (CURRICULUM.md read in full, confirmed to name no per-doc order — `_explicit_order` is a real, tested code path for if that ever changes, not dead scaffolding). Both moment shapes (§ above) live in one file, `one_word_moments` a parameter, not a fork.
5. **`creature/body.py`** (+62 lines) — `_declared_read_config`/`_declared_lexicon_config` (C2/C3's gating discipline, `READ_DOOR_GATED`/`LEXICON_DOOR_GATED` both `True`), `_read_shape_from_argv` (the task-0 decision, pinned), both doors wired in `main()` beside the folder sense; `letters` is always `genome_for_cli.ear_letters`, never a second invented number.
6. **`creature/senses/lexicon.py`** (106 lines, new) — watches `root/world/questions/q-*.json` (see item 8), looks up `senses(word, lang='en')` ordered `(sense_no, id)` — verified against the REAL lexicon that `sense_no` repeats across `pos` (`cat`: Verb/Noun/Adjective all carry `sense_no=1`), so `id` (the primary key, insertion order) is the only real tie-break, not an assumption — skips a gloss that cleans to nothing (`words_of` returns `[]`) and tries the next sense_no. Publishes ear-then-eye on moment `lexXXXXXXXX` (deterministic from word **and** the question's own id, so two distinct wants for the same word each get a fresh moment — world_maker.py's own "fresh total on a repeat showing" discipline, not a stale reused id). Marks `<qid>.answered.json` / `<qid>.unanswered.json` — **the seam contract for builder I's web door**, documented in the module's own docstring: it watches the SAME directory for `*.unanswered.json`.
7. **The reading-mark instrument, `tools/read_recognised.py`** (121 lines, new) — `recognised_share` (mirrors `tools/hands_recognised.py`'s own shape: `load_snapshot` + `gaze.glances` + `org.recall_many`, asserted never to mutate the organism); `blind_twin_root` (a fresh Mind fed a filtered tape, symlinked payload dir — `creature/replay.py:run_replay`'s own discipline, never copies or writes the source root).
8. **`creature/mind.py`** (+36 lines) — the RAISED clause from item 5 above, made concrete: `_write_ask_out` now returns the `n` it used (additive; every existing caller already discards return values, e.g. `Organism.moment`'s own S/T precedent); `_maybe_ask` — when a want is `form=="what-is"` AND carries a resolved `why_word` (never the sight-only "show me this picture again" want, which has no `why_word`) AND `"DOOR_LEXICON" in self.genome.declared` — also calls the new `_write_lexicon_want(n, why_word)`, writing `root/world/questions/q-<n>.json {"q":"what-is","word":…}`. Pure, deterministic, no new randomness or wall-clock read; gated on the gene so an undeclared `DOOR_LEXICON` (every life before this one) writes nothing new — verified both by code-path inspection and empirically (below).
9. **`tools/verdict_life.py`** (+140 lines) — `read_words_born` (maps a journal birth's own moment to its tape source, counts `words`-area births on `source=="shelf"` moments only); `shelf_episodes_from_tape` (tape-only `words_in_instant` rows, mirroring `world_pair_skew`'s own tape-only discipline — gradable with no `episodes.npz` at all); `shuffled_shelf_episodes` (the shuffled-twin null: every shelf word pooled and reshuffled into moments of their original lengths, preserving marginals, destroying pairing); `read_frames` (calls `genome.sentence.find_frames` — "SENTENCE's own twin machinery," task 4's literal words — over both the real and shuffled corpora; precision = the share of real-filed pairs the shuffle could NOT also produce); `read_mark` (the four clauses: words born ≥ 500, frames ≥ 20 at precision ≥ 0.8, the reading share ≥ 0.6, the blind twin at exactly 0 — `graded`/`pass`/`reason`/`bar`, `hands_mark`'s own shape).

## Tests: every one RED before, GREEN after

Test-first throughout (each new function/branch was asserted on before it existed, confirmed to fail with the expected error, then made to pass — the day's own record of that is in each file's own comment trail, e.g. `test_read_door.py`'s `TestReadMeetsBody` initially read 0 edges because G4-skeleton's `STAGE 2 meet` starts at moment 200, a toy-width artefact, not a read.py defect — diagnosed and fixed with a local fixture genome, not by loosening the assertion).

```
$ TMPDIR=$PWD/scratch/tmp python3 -m unittest tests.creature.test_read_common tests.creature.test_read_door \
  tests.creature.test_lexicon_door tests.creature.test_mind_lexicon_want tests.genome.test_read_lexicon_parser \
  tests.tools.test_read_recognised tests.creature.test_verdict_life_marks tests.creature.test_refusal \
  tests.creature.test_writer_sweep
Ran 148 tests in 15.379s

OK
```

148 new/touched tests (this brief's own files), all passing on the final bytes. `test_refusal.py` needed one real fix mid-way: its `SAMPLE_LINE` registry-pin fixture (a pre-existing, unrelated-to-me test whose whole job is catching an unfixtured `RUNS` entry) correctly FAILED the first time the full suite ran after `creature/genes.py`'s two new rows landed — fixed by adding the two sample lines, not by weakening the test (`tests/creature/test_refusal.py::TestRegistryPinnedToParser`, both clauses green after).

## Gates and the full suites, final bytes

**`tools/gate_g4.py --tree /data/dev/genome-wt-y --only 1,2,3,6`:**
```
G4-1 writer sweep over 14 files: 0 offenders
G4-1 control: planted offender CAUGHT
G4-2 mind parity: b05315037ff98529… vs pin b05315037ff98529… → PASS
G4-2 control (two canvases swapped): 55bcde154c429f6f… → CAUGHT
G4-3 replay identity: exit 0 → PASS  REPLAY identical: 120 mind rows
G4-3 control (payload byte flipped at seq 62): exit 1 → CAUGHT  DIVERGED at seq 62: births
G4-6 two senses on one tape: exit 0, evidence present, folder rows 13 → PASS
G4 gates: {'1': 'PASS', '2': 'PASS', '3': 'PASS', '6': 'PASS'}
```
**My own planted offender** (the brief's own gate line), a `read.py`-shaped `sense()` whose cursor write targets `root/state/` instead of `root/read/`: caught by `tests/creature/test_writer_sweep.py`'s walker (which resolves a path built through an intermediate variable — `read.py`'s own real style) both inline and via-variable. **A RAISED finding from building this control**: `tools/gate_g4.py`'s OWN `sweep()` (simpler, no variable resolution) catches the inline form but MISSES the variable-built one — `read.py`'s, `folder.py`'s, `game.py`'s and `hands.py`'s own real style for every cursor write in this tree. Not fixed here (not this builder's file, and every REAL file in this tree is still swept by `test_writer_sweep.py`'s walker, which IS exhaustive over `creature/senses/*.py`) — `tests/creature/test_read_door.py::TestPlantedReadOffender` pins both readings, positive and negative.

**Both suites:**
```
$ TMPDIR=$PWD/scratch/tmp python3 -m unittest discover -s tests/genome -t .
Ran 289 tests in 65.616s
OK (skipped=1, expected failures=6)

$ TMPDIR=$PWD/scratch/tmp python3 -m unittest discover -s tests/creature -t .
Ran 579 tests in 519.758s
OK (skipped=1)
```
Every skip/xfail is pre-existing and outside this brief's files (`grep` confirms none of `test_read_common.py`/`test_read_door.py`/`test_lexicon_door.py`/`test_mind_lexicon_want.py`/`test_read_lexicon_parser.py`/`test_read_recognised.py` declares a skip that fires; the one live skip in the 579 belongs to one of the pre-existing conditional skips in `test_game_act_file.py`/`test_hands_sense.py`/etc., unrelated files this brief never touches).

**`tools/inventory.py`** on `genome/LIFE.genome` + my two new lines (`scratch/life-with-my-genes.genome`, since `genome/ALPHA4.genome` still carries other builders' unlanded DRAFT lines and refuses to parse on this branch alone — expected, not a defect):
```
[inventory] SENSE_READ        MADE           genes.RUNS
[inventory] DOOR_LEXICON      MADE           genes.RUNS
[inventory] SENSE read        MADE           a channel, not a tape row (no publish() names it) ...
scratch/life-with-my-genes.genome: 60 rows - DECLARED-ONLY 0 - VALUE-UNREAD 3 - OFF 8 -> clear
```
Both genes MADE by every path `inventory.py` checks; 0 DECLARED-ONLY overall. The 3 VALUE-UNREAD and 8 `#OFF` rows are pre-existing (`HEBB`/`MEET`/`RECALL`, and eight `#OFF …` genome comments), none of them mine.

## The closed-tape regression (life 3a) — the CORRECT baseline, found by reading `tools/gate_g5_landing.sh`

My first attempt compared my worktree's replay against life 3a's own ORIGINAL 09-21 13:14 journal and found a real divergence at seq 140 (`think.item`: `arrow` vs `bar`) — **isolated by `git stash` to be 100% pre-existing** (identical divergence with every one of my changes removed) and **explained by `docs/organs/G5-DESIGN.md` row 16b**: a "kind chosen first, fairly" fix to THINK's pool-selection order, landed AFTER life 3a ran, specifically BECAUSE life 3a's original behaviour (CURIOSITY working "rule" items almost exclusively) was recognised as a defect — replaying life 3a's OLD tape under the FIXED code is *supposed* to choose different think items than the life originally did. That comparison was against the wrong baseline.

The actual convention (`tools/gate_g5_landing.sh`, the shared landing checker every G5/ALPHA4 builder's worktree already carries a cached copy of): compare against a **master control replay of the SAME tape**, both sides on `genome/G4.genome` (byte-identical between master and this branch — checked directly). Redone correctly:
```
$ (cd /data/dev/genome && python3 -m creature.replay --genome genome/G4.genome \
   --tape <local copy of life 3a's tape> --out <scratch>/replay-life3a-master)
$ python3 -m creature.replay --genome genome/G4.genome --tape <same tape> --out <scratch>/replay-life3a-mine
$ python3 tools/replay_diff.py <master journal> <mine journal> --label-a master --label-b mine
[replay_diff] master: 2576 mind rows · mine: 2576 mind rows · compared 2576
[replay_diff] rows differing ONLY in ignored fields ['hash']: 0 · rows with a non-ignored diff: 0
[replay_diff] IDENTICAL except ['hash']: True
```
**Identical except `hash`, 0/2576 rows differing.** Life 3a's tape never declares `SENSE_READ`/`DOOR_LEXICON` — nothing of mine moves, confirmed both structurally (every new branch is gated on a gene this genome never carries) and empirically. The tape itself was `cp -r`'d once from `/data/dev/genome/run-g4-life3a-20260921-1314` into this worktree's `scratch/`; every replay ran against that local copy, never against the live master path.

**`tools/verdict_life.py:read_mark` on seam-1's closed record (a copy, `scratch/seam1-copy/`, tape+journal only — 21 MB, the 281 MB payload dir was not copied, not needed by a tape/journal-only function):**
```
eye row sources present on seam-1's tape: {'game', 'maker', 'folder'}
read_words_born: 0
read_frames: {'shelf_moments': 0, ..., 'precision': None, 'pairs': []}
read_mark → graded=False, pass=None, reason='not gradable: SENSE_READ not declared on this life'
```
Not gradable, by name, exactly as the brief requires.

## Cost + rate (task 5)

Toy 1 (single-moment) and toy 2 (two-moment) both ran maker + reader concurrently for ~16 min, `words 8`, `every 5 s`:

| | `mind_ms_per_canvas_1min` (final) | shelf eye rows (moments read) | words_born (shelf's 40 + maker's ~11) |
|---|---|---|---|
| Toy 1 | 29.14 ms | 192 (of 200 — the corpus nearly exhausted) | 51 |
| Toy 2 | 60.40 ms | fewer sentence-level moments, but ≈9x more total tape rows per multi-word chunk (one moment per word + one sentence moment) | 51 (saturated at the SAME total — both toys share one 40-word vocabulary) |

The two-moment design roughly **doubles** the mind's per-canvas cost (not 6–9x, despite publishing far more rows per chunk) — most of a canvas's cost is the fixed retina/tower pass per glance, and a one-word moment still needs the same four located glances a line does; the EXTRA cost is from processing more canvases per unit time, not a heavier canvas. **RAISED, not measured**: PREREG §5's own COST bar ("`mind_ms_per_canvas_1min` ≤ the pre-flight's figure × 1.5") needs the REAL pre-flight's baseline (PREREG §8 item 5, not yet run — no ALPHA4 life exists yet); I report the toy's own before/after-shape comparison instead, honestly labelled as not the same thing. **On PREREG §9's "words born ≥ 3,000 by 24 h"**: the toy's own 40-word vocabulary saturated almost immediately (51 of a possible ~51 total, all of it by minute 12–16) — this is NOT a valid rate to extrapolate to 24 h, because the toy's vocabulary is closed and small while Ahmad's real shelf (2,094 nursery docs, tens of thousands of distinct words) keeps offering NEW words the entire 24 h; the toy can only speak to "does a word get bound and become recognisable at all," which it answered (yes, at 0.60 under the adopted design), not to the prediction's own rate.

## Commit

`0762f5306a345522cddd6ce02d69811539451ed5` on branch `alpha4-read` (worktree `/data/dev/genome-wt-y`), off master `74c661d`. 18 files changed (7 modified, 11 new), 2,361 insertions.
