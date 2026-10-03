# records/origin-planted — the planted run the verifier asked to SEE: an origin row that says «R9 UNTESTED … NOT A PASS», beside a fully tested control

*edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:08 +0400 (from `date`) — on the VERIFIER's ask of 20:39 on c887b50: «show me on a planted run that the origin ROW (not only the r9 dict) says «R9 UNTESTED» and is not summarised as a pass, with the series row saying so». Law: `PREREG-RESIT-READER.md` v4 + erratum E1 (the verifier co-signed it 21:02). The runs are the test suite's own stub lives (`tests/tools/test_resit_origin.py` OriginBase) driven through the real `resit.py run --mode origin` BY PATH with `-B -I`; the generator is `make_planted_run.py` in this folder (run from the worktree root with `TMPDIR=<scratch> PYTHONPATH=. python3 -B …/make_planted_run.py <OUTDIR>`), its output is `runs/` (with `runs/READINGS.txt`).*

## What the two runs are

| run | the plant | what it does to R9 |
|---|---|---|
| `runs/planted-untested-set/` | a `learn` row at seq 1004, right after the fresh set's begin (seq 1003), appended to the stub life's journal (the generator asserts the plant changed the bytes) | in the fresh sitting every held item, the why and the end answer after the brain moved: LATE; only `begin` stays EARLY, which tests nothing. The s1b1 sitting is untouched. |
| `runs/control-fully-tested/` | none | both sittings fully EARLY: the same stub life, unplanted |

## The reading (`runs/READINGS.txt`; each line is copied from the file named)

**Planted.**
- `ORIGIN.json`: `r9_untested_sets` = `["fresh"]`; `r9_reading` = «R9 UNTESTED for set(s) fresh (no tested EARLY item) — NOT A PASS for them: their begin state is verified only by R10c · R9 EXACT on 3 of 3 TESTED EARLY items (tested EARLY items per set: fresh 0, s1b1 3); the structural begin/end rows equal on 3 of 3 (not counted as tests); LATE items 4, discordant 0».
- `RESIT.jsonl`: the SAME `r9_reading` and `r9_untested_sets` (the series row is the origin row; runs/READINGS.txt prints the equality check, True).
- `RESIT.md`: the note cell of the origin line carries the same text.
- `ORIGIN.json` `r9.by_set`: fresh `n_early` 1, `n_early_tested` 0, `n_late` 4, `untested` true, with the note; s1b1 `n_early` 5, `n_early_tested` 3, `untested` false.

**Control.**
- `r9_untested_sets` = `[]`; `r9_reading` = «R9 EXACT on 6 of 6 TESTED EARLY items (tested EARLY items per set: fresh 3, s1b1 3); the structural begin/end rows equal on 4 of 4 (not counted as tests); LATE items 0, discordant 0»; `RESIT.md` repeats it; the word UNTESTED appears nowhere in the control's three files.

## What it shows, and what it does not

It shows that the line a reader of the row (or of RESIT.md) meets first for a set with no tested EARLY item is UNTESTED, that it says «NOT A PASS», and that the exactness it still claims is over the TESTED rows alone, with the structural begin/end rows counted beside them and «not counted as tests». The planted run found TWO wording faults in turn, each fixed at the commit that carries this folder: the first line said «R9 EXACT on the other sets: 6 of 6 EARLY items» (the 6 held the untested set's own begin row), and the second said «EXACT where tested: 6 of 6 EARLY items (begin and end included)», which put structural rows into the denominator of a word that erratum E1 reserves for non-structural ones (the VERIFIER's ruling, 21:3x). It does not show a real life's UNTESTED set: the real-data smoke (`../origin-bl2-fallback-smoke/`) has none (0 untested, 1,722 and 1,285 tested EARLY items; its row was written by the reader a82ea77, whose fallback wording differed from the final one).
