# REPORT — Builder B, Wave 3, W3-1 (D-G12: one belief per word; extension; the clash half wired)

edit: Claude (Sonnet 5, W3 builder B), 2026-09-20 23:03 +0400 — report, committed after the gates below
were re-run on the final bytes (a defect was found and fixed mid-task; see "One defect found and fixed").

Branch `g4-wave3-b`, worktree `/data/dev/genome-wt-e`. Files touched: `genome/think.py`,
`tests/genome/test_think.py` (two same-word fixtures switched off `believe()` — see below),
`tests/genome/test_believe_scope.py` (new). Nothing outside `genome/think.py` and `tests/genome/` was
touched; `/data/dev/genome`, `/data/dev/genome/run*` and no systemd unit were ever opened for writing
(life 1's beliefs.jsonl was `shutil.copy2`'d to a temp dir before being read).

Commits: `3ad7727` (the W3-1 implementation + toys), `7502eee` (the fix below, re-verified on the final
bytes — this is the commit the gates below were run against).

## Gates — every "Ran N … OK" line verbatim, from the final commit (7502eee)

- `tests/genome/test_pin_skeleton.py`: `Ran 1 test in 9.716s` / `OK`
- The whole `tests/genome` suite (`python3 -m unittest discover -s tests/genome -t .`):
  `Ran 136 tests in 122.970s` / `OK (skipped=1, expected failures=9)`
- `tests/creature/test_wave2_belief_path.py` + `tests/creature/test_wave2_think.py`:
  `Ran 11 tests in 21.474s` / `OK`

## The interface, delivered exactly

`believe(word, cells, episode_ids, moment, path, ledgers=None, clash_enabled=True) -> dict`, `"kind"` in
`{"belief","revisit","extension","clash"}` (+`"clash_refused"` when `clash_enabled=False`), `"line"` =
the row's own line number except a revisit, which returns the STANDING row's line. `read_beliefs(path,
fold=True)` folds revisits/extensions into one standing row per word with `revisits`/`extensions`
counts and the union of every episode id on the word's current chain (plus a `clashes` count, an extra
field beyond the brief's own minimum). The four rules are checked in this order: (1) no standing →
belief; (2) a ledger reassignment OR any standing cell removed → clash; (3) same cell set → revisit;
(4) cells added, none removed → extension. Six design decisions (the ledger check's exact meaning,
clash()'s reuse across an extension-standing / same-cells / partial-overlap standing, and fold's
handling of a clash-forked word) are documented in full in `genome/think.py`'s module docstring —
following the pattern the original B11 docstring set for its own three ambiguities.

## Toy numbers (`tests/genome/test_believe_scope.py`, 9 tests, all pass)

- (a) stable stream, 6 calls on one word: kinds = `[belief, revisit, revisit, revisit, revisit, revisit]`
  → 1 belief + 5 revisits + 0 extensions. `read_beliefs(fold=True)` returns one row: cells `[1,2]`,
  `revisits=5`, `extensions=0`, `clashes=0`, episodes = the union of all 6 calls' episode ids.
- (b) 2 calls stable + 2 calls with a cell added: kinds = `[belief, revisit, extension, revisit]` →
  exactly 1 extension, `of=0`, `added=[3]`, `cells=[1,2,3]`. Folded: `extensions=1`, `revisits=2`.
- (c) ledger relabel, same cells, 2 belief/revisit calls then 2 calls under a ledger claiming the
  standing cells now answer `"not_zog"`: both of the relabelled calls return `kind="clash"` (≥1
  required by the brief; both fired since the standing itself becomes a fresh, still-relabelled belief
  each time — a persistent contradiction re-clashes on every call, there is no "settled" state).
  Every clash row names two real, distinct, on-disk lines.
- (c, second form) cells removed with no ledger at all (`[1,2]` → `[9,10]`, fully disjoint): 1 call →
  `kind="clash"`, `clashes=[0,1]`, both belief rows still readable unchanged.
- (c, third form — added after the fix below) cells removed with an OVERLAPPING remainder
  (`[1,2,3]` → `[3,4]`): 1 call → `kind="clash"`, `clashes=[0,1]` — clash()'s own disjoint law finds no
  conflict here (not disjoint), so believe() opens the clash directly (see "One defect found and fixed").
- (d) the negative control: the same ledger-relabel stream with `clash_enabled=False` → every call
  returns `kind="clash_refused"`, the file's line count and its full byte-hash are IDENTICAL before and
  after (asserted explicitly); the positive twin (same scenario, `clash_enabled` defaulting `True`)
  immediately after DOES write and DOES grow the file.
- (e) append-only: a 5-call mixed stream (belief → revisit → extension → clash → clash_refused) with the
  first 1 and first 3 lines' sha256 hashed after every call — identical across every checkpoint.

## Life 1's replay (the scale control, read from a `shutil.copy2` of the read-only source)

762 source rows, 15 distinct words (the clauses doc's own reading says "16 words" — the file itself has
15; noted, not corrected, since it isn't mine to edit). Replayed through the new `believe()` in order,
no `ledgers` (life 1's file carries no ledger snapshots), onto a fresh file:

```
belief: 15, revisit: 667, extension: 79, clash: 1, clash_refused: 0   (sums to 762)
folded standing beliefs: 15 (≤ 16, as required)
```

Per-word reconciliation (`1 + revisits + extensions == source_rows`), now asserted in the test: holds
EXACTLY for all 14 words with `clashes=0`. The one exception is `"diamond"` (69 source rows): its
own history genuinely contains a same-word cell-set change that the new scope law reads as a
contradiction (the OLD unconditional `believe()` that wrote life 1's file could never express this —
every one of its 69 rows was an unconditional overwrite-by-append) — the replay opens exactly 1 clash
for it, after which the folded view shows only the post-clash chain (11 = 1+6+4), by decision 6
(a clash forks; fold tracks the latest fork; the pre-clash rows are still on disk, just not merged into
the single "standing belief" summary). This is not a defect; it is the append-only, no-double-book-belief
law doing exactly what D-G12 asked for on real, previously-uncritiqued data.

## One defect found and fixed before this report (self-caught on review, not shipped)

The first implementation (commit `3ad7727`) had a silent fallback: when `removed` was non-empty but
clash()'s own disjoint-cells law found the two sides still overlapping (e.g. standing `[1,2,3]` → new
`[3,4]`), believe() returned the freshly-written plain "belief" row instead of a clash — a FIFTH,
undeclared kind outside `{belief,revisit,extension,clash,clash_refused}`, and one that silently forked
`read_beliefs(fold=True)`'s per-word chain. Life 1's own replay caught it in the numbers themselves:
"diamond" folded 69 source rows down to 11 with `clashes=0` — no clash to explain the missing 58. Fixed
in `7502eee`: rule 4 is unconditional (cells removed or a ledger reassignment always ends in a clash
row); when clash()'s narrower disjoint-only law does not fire, believe() opens the clash directly
(`_open_clash_direct`, already built for the ledger case) instead of falling back to a plain belief.
Re-verified: diamond now reads exactly 1 clash, and every other word's chain reconciles exactly against
its source row count (added as an explicit per-word assertion in the replay test, plus a new toy
`test_c_partial_removal_with_overlap_is_also_a_clash`). All three gates above were re-run on these
final bytes.

## Clauses met in full — nothing raised as unimplementable. Two integration notes for whoever wires the mind, not a clause failure on my side:

1. **The ledger half of rule 4 has no live caller yet.** `creature/mind.py`'s `_think_work` already
   computes `ledgers = build_ledgers(self.org, self.moment_word)` two lines above its
   `think_laws.believe(...)` call but does not pass it — `believe()` is called with 5 positional args
   only, so `ledgers` defaults to `None` and the ledger-reassignment half of rule 4 (decision 4 in
   `think.py`) can never fire from the live mind, only from a caller that opts in. This is Builder A's
   file, not touched here; wiring it is one keyword argument (`ledgers=ledgers`) at the existing call
   site once the orchestrator decides the mind should reason about it.
2. **On-disk row count vs. returned-kind counters.** A genuine clash writes TWO rows (the fresh belief,
   then the clash) but `believe()` returns ONE dict (`kind="clash"`) — by the fixed interface's own
   words, "return its row with kind clash". So once any clash fires, `len(beliefs.jsonl)` will exceed
   `beliefs + revisits + extensions + clashes` (Builder A's W3-1 counters, one per returned kind) by
   the clash count. `tests/creature/test_wave2_belief_path.py`'s own invariant
   (`len(rows) == mind.think_counters["beliefs"]`) still passes today only because (a) no clash fires on
   that test's 3-shape stream and (b) `mind.py` still increments `beliefs` unconditionally per call
   (pre-W3-3-counters code, unchanged in this worktree). Once Builder A's per-kind counters land, that
   test's invariant will need `len(rows) == beliefs + revisits + extensions + 2*clashes` (or simply drop
   the byte-count assertion) — flagging it now so it isn't a surprise at merge.

## A minor factual note, not a clause

`docs/G4-WAVE3-CLAUSES.md` W3-1 states life 1 has "762 belief rows for 16 words"; the file itself has
762 rows and 15 distinct words. Not corrected (not mine to edit); the replay above uses the real count.

## Cost shape, noted not fixed (out of scope for this clause)

`believe()` re-reads the whole beliefs file (`read_beliefs`) plus at least one more `_line_count` open
(two on a clash) on every call — fine at life 1's scale (≤ 3,000 lines over 11.5h) but O(n²) over a
24h+ life as the file grows; worth an index or an in-memory cache if a future clause needs `believe()`
to run at machine speed rather than think-cadence.
