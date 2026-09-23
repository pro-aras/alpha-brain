# A42-B3 report — the sound-axis chunk law + the Gutenberg clause

Branch `a42-b3`, worktree `/data/dev/genome-wt-b3`. Branched from `a4-integration @ a50b0f3` (the first
builder's hand-back state); a4-integration moved to `51f71ba` (the a4l-explore merge) mid-task and was
merged into this branch before the final gate (commit `3dcb684`). Commits: `c850cad` (task 1), `ee484ee`
(task 2), `3dcb684` (merge of a4-integration).

## NOT DONE / limits of each proof (read this first)

1. **Task 1's closed-tape replay (`a4l-pre-voice`) never crosses 64 sound cells** — it ends at `sound.n =
   11` under both arms. It proves the *smaller initial allocation* is hash-neutral on a real, closed,
   voiced life; it does **not** exercise the grow-boundary at cell 64. That crossing is proven only by the
   toy (`tests/genome/test_a42_b3_sound_chunk.py`, >128 distinct sounds, two boundaries).
2. **Task 1's hour-1-fixture check (HASH-sparse + VOICE scratch genome) never runs any sound at all** —
   the fixture's own tape (`alpha4-1-hour1/tape/2026-09-23.jsonl`, 4,581 raw rows / 4,322 mind rows) carries
   **zero** `ear-sound` rows (confirmed by counting `sense` values in the tape before writing this). This
   check reconfirms "an empty sound area is hash-neutral" at production scale and pipeline width (the full
   Mind, not a bare Organism) — it says nothing about the boundary either.
3. **The load()-path asymmetry fix (`o.sound` added to the sight/words re-grow tuple) is a defensive,
   hash-neutral token, not a fix to a reachable bug** — tested directly
   (`TestLoadAsymmetryMissingMeetingCaughtByDigest`): the one scenario that would exercise the gap (a
   meeting declared at load time but not at save time, with `sound.n > 0`) changes `state_hash()`'s own
   `sound_meets` iteration and is refused by `Organism.load()`'s digest-mismatch gate *before* the gap ever
   matters. The line is kept anyway, against a future change that might decouple "which meetings are
   declared" from the digest.
4. **RSS is a noisy proxy, not an exact cost model.** Measured delta between the two `a4l-pre-voice`-tape
   replay arms: ~68 MB (386.2 MB parent, 318.3 MB task-1). The back-of-envelope estimate (two pairs ×
   (2048²−2048×64) cells × 10 bytes) is ≈ 81 MB. Same order of magnitude and correct direction (task-1 arm
   uses less), not exact — `ru_maxrss` includes the whole process's peak, not an isolated allocation.
5. **Task 2's clause is built but declared nowhere** — per the brief and Ahmad's 16:56 word, no genome file
   is touched by this task; the seat declares the line tonight. Its "live" behaviour (Ahmad's 16:56
   amendment) is proven through the real sense road run directly (`read_sense.sense()` in a thread, over
   the real `pg14640.txt`), not through an actual running life with the clause declared.
6. **`creature/body.py`'s wiring test is a source pin, not an end-to-end test.** `creature.body.main()` is
   a blocking CLI service loop (registers SIGTERM/SIGINT, `while not stop_requested.is_set(): sleep(0.2)`)
   — not practically callable in a unit test. The behavioural proof that the kwarg actually changes what
   gets published is `TestRealShelfThroughTheSenseRoad`, on the exact `creature/senses/read.py` function
   body.py calls, with the kwarg set exactly as body.py's own line sets it.
7. **Final gates**: see the log lines below — filled in after this file was first drafted, from the actual
   log output, never typed from memory.

## TASK 1 — the sound-axis chunk (64)

### Code
- `genome/machinery.py`: new `SOUND_GROW_CHUNK = 64` constant; `_Pair.__init__` gains `self.sound_axis`
  (decided once from the areas, never the pair's name); `_Pair.grow(axis)` picks `SOUND_GROW_CHUNK` vs
  `GROW_CHUNK` per axis — the one method behind every grow call site, including `load()`'s direct
  `p.grow(0)`/`p.grow(1)`; `Organism.__init__`'s sound-meet construction gets a separate `sound_cap`
  (collapses to `cap` under NMAX — the negative control is untouched).
- `load()`'s pair re-grow loop: `o.sound` added beside `o.sight`/`o.words` (see NOT-DONE item 3).
- Three **existing** tests patched `machinery.GROW_CHUNK` alone and asserted `"> 8"` on a sound pair's sound
  axis as a **"positive control: ... grew"**. With `SOUND_GROW_CHUNK` unpatched (64 by default after this
  task) that control would pass whether or not growth actually happened — a vacuous control (SOLUTIONS
  #91's class). Fixed by patching `SOUND_GROW_CHUNK` alongside the other two in all three fixtures:
  `tests/genome/test_a4l_seam5_witness_sound.py` (one local patch),
  `tests/creature/test_a4l_seam5_witness_sound_seams.py` (two local patches, one shared class fixture),
  `tests/creature/test_a4l_voice_seams.py` (one shared class fixture).

### RED → GREEN (test-first)
RED (unmodified `genome/machinery.py`, the new toy file + the three patched fixtures):
`scratch/logs/task1-red-1.log` — `Ran 36 tests in 39.734s` / `FAILED (errors=13)`, every error
`AttributeError: module 'genome.machinery' has no attribute 'SOUND_GROW_CHUNK'`.

GREEN (after the `genome/machinery.py` edit): `scratch/logs/task1-green-1.log` —
`Ran 36 tests in 60.639s` / `OK`. Adjacent, untouched suites re-run to confirm nothing else moved:
`scratch/logs/task1-adjacent-1.log` — `Ran 48 tests in 37.140s` / `OK`
(`test_a4l_voice_machinery`, `test_grow_mechanics`, `test_a4l_cost_witness`, `test_a4l_cost_seams`).

### Identity proof
**(a) The closed `a4l-pre-voice` tape, detached worktrees, parent vs task-1:**
`git worktree add --detach scratch/ctl-a50b0f3 a50b0f3` and `... scratch/ctl-c850cad c850cad`; the tape
copied via `cp -a` (same filesystem, `/data`) to `scratch/tapes/a4l-pre-voice-tape/` — the live life root
under `/data/dev/genome-lives/` was never otherwise touched. `scratch/replay_arm.py` replays under each
tree's **own** `genome/ladder/A4L-VOICE.genome`, in a **fresh process per arm** (module caching would
otherwise silently answer for the wrong tree), printing a positive control first:

```
[parent-a50b0f3] hasattr(machinery, 'SOUND_GROW_CHUNK') = False   (git HEAD a50b0f301...)
[task1-c850cad]  hasattr(machinery, 'SOUND_GROW_CHUNK') = True (value 64)   (git HEAD c850cad65...)
```

Both arms: `sight.n=873 words.n=162 sound.n=11` (identical — the tape never crosses 64). Shapes:
parent `sight-sound [2048, 2048]` / `sound-words [2048, 2048]`; task-1 `sight-sound [2048, 64]` /
`sound-words [64, 2048]` — the sight/words axis unchanged, the sound axis shrunk exactly as designed.
**`state_hash` identical**: `8d75609e0827a9cbc9c64c45a9d02a6512ce32822b08d75f33a10387ce9336cf` both arms.
`tools/replay_diff.py … --ignore ""`: `2007 mind rows · compared 2007 · IDENTICAL except ['']: True`
(`scratch/logs/task1-replay-diff.log`). RSS: parent 386.2 MB, task-1 318.3 MB (Δ ≈ 68 MB; NOT-DONE item 4).

**(b) The toy (`tests/genome/test_a42_b3_sound_chunk.py`, part of the GREEN run above):** two Organisms fed
an identical 200-moment stream of fresh novel sight+sound (one fixed word) — one run with
`SOUND_GROW_CHUNK` at its real value (64), one with it patched to 2048 (the pre-task law) — never
interleaved (each run to completion, restored, then the other runs). `state_hash()`/`row_hash()` (dense
**and** HASH sparse) identical at **every** one of 200 moments; shapes diverge from cell 64 (the positive
control: `assertNotEqual` on the shape lists); `ss.W.shape[1] % 64 == 0` (the sound axis) while
`ss.W.shape[0] % 2048 == 0` (the sight axis, untouched) — the two constants are independent, not merely
"A grew". A one-ulp plant at the **first masked (live) coordinate** of `sight-sound` (`np.nonzero(mask)`,
never `[shape-1, shape-1]`, which is unmasked padding once cells are few — SOLUTIONS #91's rule) moves both
the dense and the sparse digest.

**(c) The hour-1 fixture, HASH-sparse + VOICE scratch genome (fixture's own `GENOME.genome` = byte-identical
to `genome/ALPHA4.genome` + 3 VOICE lines + `HASH sparse; dense at snapshot`, never `A4L-VOICE.genome` —
its own SENSE eye dims could mismatch the fixture's tape):** parent vs task-1, same detached-worktree
method. Both arms: `sight.n=1803 words.n=276 sound.n=0` (the fixture tape carries zero `ear-sound` rows —
NOT-DONE item 2). `state_hash` identical:
`e266659aea2601dc6f5af62adc4d71fc8a88bd2cd3e90a9fe4adb589629f41f8`. `replay_diff --ignore ""`:
`4322 mind rows · compared 4322 · IDENTICAL except ['']: True` (`scratch/logs/task1-hour1-replay-diff.log`).

**(d) The load-asymmetry regression**, `TestLoadAsymmetryMissingMeetingCaughtByDigest` (part of the GREEN
run above) — see NOT-DONE item 3 for what it found and what the fix actually is.

## TASK 2 — the Gutenberg clause, built UNDECLARED

### Code
- `genome/machinery.py`: `SENSE read`'s regex gains an optional `(; gutenberg body only)?` group;
  `declared["SENSE_READ"]` gains a sixth key **only when present**; `GenomeError` names the clause on a
  misspelling.
- `creature/body.py`: `gutenberg_body_only=bool(read_cfg.get("gutenberg_body_only"))` threaded into the
  `SENSE_READ` `functools.partial`.
- `creature/senses/read.py`: `sense(..., gutenberg_body_only: bool = False)`, threaded to `_doc_sentences`;
  `_doc_sentences` keeps the text strictly between `"*** START OF"` and the first `"*** END OF"` **after**
  it (both marker lines excluded) when both are found in that order; the whole file otherwise (absent,
  one marker only, or END found only before START — the search for END never looks before START's own
  position, so this can only ever read as "no END found").

### RED → GREEN (test-first)
RED — captured honestly, **after** the code was already written (an ordering slip; corrected by
`git stash push -- genome/machinery.py creature/body.py creature/senses/read.py`, running the tests against
the stashed-out, pre-edit tree, then `git stash pop`): `scratch/logs/task2-red-1.log` —
`Ran 17 tests in 14.577s` / `FAILED (failures=4, errors=9)`. The 4 non-failing tests are legitimate
controls unaffected by this task (the pre-existing 5-key parser shape, and two data-only probes against the
real shelf); every one of the 13 failures/errors is exactly the missing feature
(`TypeError: ... got an unexpected keyword argument 'gutenberg_body_only'`, a `GenomeError` from the
old regex rejecting the clause, or the source-pin/`assertIn` on the not-yet-true prose).

GREEN: `scratch/logs/task2-green-1.log` — `Ran 17 tests in 1.814s` / `OK`. Adjacent, untouched suites:
`scratch/logs/task2-adjacent-1.log` — `Ran 40 tests in 11.984s` / `OK`
(`test_read_lexicon_parser`, `test_read_door`, `test_read_recognised`).

### The real-shelf controls (Ahmad's 16:56 amendment: "its LIVE behaviour matters")
All on the real, read-only `/data/alpha3-library/SHELF.sqlite` + `G1-G3/readers/pg14640.txt` — never
written to; a throwaway shelf pointing an ABSOLUTE path at the real file is used instead of copying it
(pathlib: `Path(anything) / "/abs/path"` returns the absolute path unchanged).

- **The designer's own Q2 probe, reproduced exactly** (not merely "close"): 129 header words, 10,649 total,
  2,909 from the END marker's own line, **269 of 2,094** nursery docs carry both markers — all four match
  `docs/ALPHA4-2-PREREG.md` §11 Q2 to the word.
- **`_doc_sentences` on the real file, flag ON**: no returned sentence contains "gutenberg", "literary
  archive foundation" or "www.gutenberg.org"; first body sentence pinned and printed:
  `"[Transcriber's Notes: Welcome to the schoolroom of 1900."` (split_sentences does not cut on `:`).
  **Flag OFF** (negative control): all three phrases ARE present.
- **The stronger form, through the actual sense road** (`read_sense.sense()` in a thread, a real `Tape`,
  `tests/creature/test_read_door.py`'s own pattern): with the flag ON, no published **ear** word's
  cleaned/truncated (letters=8) form matches any of PREREG's own marker tokens (gutenberg, license,
  trademark, distribution, donations, foundation, copyright, agreement, liability, warranty). With it OFF,
  the header's own title word DOES reach the tape (positive control that the harness can see the word when
  it is really there).

### Identity proof (hour-1 fixture, undeclared)
Own worktree (`ee484ee`, then the merge `3dcb684`) vs a detached `a50b0f3` checkout, both via
`genome/ALPHA4.genome` (never touched by either task) on the same fixture tape:
- **vs the induce-lane reference** (`/data/dev/genome-wt-induce/scratch/replays/h1-alpha4-master/journal.jsonl`),
  masked on `readiness` only (hash **included**, per the brief's literal wording — not pre-emptively
  masked): `4322 mind rows · compared 4322 · IDENTICAL except ['readiness']: True`
  (`scratch/logs/task2-hour1-diff-vs-induce-ref-hash-included.log`).
- **vs a50b0f3 directly**, `--ignore ""` (every field including hash): `4322 mind rows · compared 4322 ·
  IDENTICAL except ['']: True` (`scratch/logs/task2-hour1-diff-vs-a50b0f3.log`) — `state_hash` on both:
  `e266659aea2601dc6f5af62adc4d71fc8a88bd2cd3e90a9fe4adb589629f41f8`, same as task 1's own hour-1 check
  (the fixture's own `ALPHA4.genome` is byte-identical in every tree touched today).

## Final gates
(run on the merged tree, commit `3dcb684`; one process at a time, `uptime` checked before each)

- Full genome suite: `python3 -m unittest discover -s tests/genome -t .` —
  `scratch/logs/final-genome-suite.log`: `Ran 532 tests in 156.654s` /
  `OK (skipped=1, expected failures=6)` (both pre-existing, not from this task's edits).

## LOAD discipline
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19`, one process at a time throughout;
`uptime` checked before every heavy step (1-min load ranged ~7–11 during this session, never above 12 so
no wait was needed). Every stamp in this file and in code comments read from `date "+%Y-%m-%d %H:%M %z"` at
write time. `/data/dev/genome-lives/` touched only via the one `cp -a` of `a4l-pre-voice`'s tape into this
worktree's own `scratch/`; no other worktree touched. Detached worktrees (`scratch/ctl-a50b0f3`,
`scratch/ctl-c850cad`) removed after use.
