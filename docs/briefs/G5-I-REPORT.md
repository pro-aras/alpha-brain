# G5-I REPORT — THE SEAM: where, when and the act delivered beside every trait (DELIVER + MOMENT)

*Builder I (Sonnet 5), stamped `date "+%Y-%m-%d %H:%M %z"` = 2026-09-21 21:22 +0400. Branch `g5-seam` in
worktree `/data/dev/genome-wt-m`, from master `ec28b4c`. `/data/dev/genome` (the live creature, `run/`,
`world/`, systemd) was never touched — read-only throughout; life 3a's closed root
(`run-g4-life3a-20260921-1314/`) was read directly (its tape's payload files, its `state/organism.json`
for the genome text it ran under) — never written to, and its `run/` symlink target was never followed
(`creature.replay.run_replay` builds a fresh temp root and symlinks only the source tape's own `payload/`
dir, exactly as the tool already does for every other replay on this estate).*

---

## 0 · What was built, in one line

Two new, additive genes — `DELIVER where fixation when instant act glance` (the eye's promise) and
`MOMENT keys sight words surprise where when act source` (the mind's promise) — carry the window origin,
the tape's own instant, the act ("glance", the only verb declared today) and the source (`maker`/`folder`,
copied from the eye row's own `meta["source"]`) beside every glance's feature, into `genome/fast.py`'s
`Episodes` row and the journal row, **never into `x_s`/`x_w`** — the vectors `org.moment()`/
`moment_sight()` compare by cosine are byte-for-byte what they always were. Proven by: PARITY (state_hash
and every pre-existing mark unmoved, on both a toy tape and life 3a's real 2 h closed tape) with a planted
cosine-leak negative control CAUGHT; the E51 A1.2 position plant (two classes whose 32×32 glance windows
are byte-identical — chance is a measured fact, not a hope — and the mind answers **above** chance only
by reading `where`, never `x_s`); and one real episode, on a real tape, carrying `where`/`when`/`act`/
`source` (#180's law: prove the last link with one real value).

## 1 · Files touched, and why each line is there

- **`genome/machinery.py`** — two new `elif gene ==` branches (`DELIVER`, `MOMENT`), each a strict
  `re.fullmatch` of the design's own literal line (same discipline as every gene here: ASK's six-verb
  literal, BODY's `service <name> threads …`). Nothing renamed, no existing branch edited. `DELIVER`'s
  parsed value is `{"where": "fixation", "when": "instant", "act": "glance"}`; `MOMENT`'s is
  `{"keys": ["sight", "words", "surprise", "where", "when", "act", "source"]}`. `FAST`'s own literal
  (`"keys sight words surprise"`) is untouched — MOMENT is a wholly separate gene, not a widened FAST
  (pinned by `test_fast_gene_is_untouched_by_moment`).
- **`genome/fast.py`** — `Episodes` gains five new columns (`where_y`/`where_x`/`has_where`, `when`, `act`,
  `source`, `glance`), a `nearest_where(where, k)` reader, and `save`/`load` persistence with
  backward-compatible loading of a pre-seam store (life 3a's own `episodes.npz` carries none of these
  keys — loading it now defaults every seam field to absent, never raises). Convention mirrors B12's
  `x_s2`/`has_s2` exactly: a presence mask for `where` (a real `(-1,-1)` origin is possible the moment a
  canvas is ≥ 2×2, so a bare sentinel is not enough), the empty string as "absent" for the three string
  fields (`word`'s own convention), `-1` for `glance` (`moment`/`ids`'s own convention). `Episodes` is
  never hashed (`state_hash()` reads `Organism` only), so none of this can move gate G4-2's pin by
  construction — and the parity tests prove it directly rather than trusting the argument.
- **`creature/mind.py`** (`_consume_eye`) — computes `seam0` once per canvas (glance 0's window origin
  from `g["windows"][0]`, the tape row's own `at`, the literal `"glance"`, `meta.get("source")`, and
  `glance=0`), gated on `"DELIVER" in self.genome.declared`; hands it to `Episodes.write` as extra keyword
  arguments gated on `"MOMENT" in self.genome.declared`, and to the journal row as extra dict keys gated
  on `DELIVER` alone. `"where" in self.blind` drops just the `where` field (the same blind-twin convention
  as `"gaze"`/`"predict"`/`"sleep"`/`"curiosity"` already in this file) — `--blind where`.
- **`creature/genes.py`** — two rows added to `RUNS["mind"]` (W3-0's law: a declared gene with no real
  call site refuses the organism at `Mind.__init__`; mine ARE real call sites, so they must be named or
  every genome that declares them refuses to start — caught by my own first test run, §3 below).
- **`tests/genome/test_deliver_moment.py`** (new) — parser accept/reject for both genes.
- **`tests/genome/test_fast_seam.py`** (new) — `Episodes` unit tests: write/get round-trip, absence
  defaults, `glance=0` not confused with absent, **the load-bearing claim that `where` never alters cosine
  recall** (two episodes, identical `x_s`, different `where`, must still tie exactly under `nearest`),
  `nearest_where`'s five behaviours, save/load round-trip, and loading a genuinely pre-seam `.npz` (built
  by hand with the OLD key set, exactly what `genome/fast.py` wrote before this gene existed).
- **`tests/creature/test_g5i_seam_deliver_moment.py`** (new) — the mind-level tests: §3 below.
- **`tests/creature/test_refusal.py`** — `SAMPLE_LINE` gained the two rows W3-0's own registry-pin test
  demanded the moment `DELIVER`/`MOMENT` were added to `RUNS` (§3.4).

## 2 · Interpretation choices — raised, not silent

1. **`where` = the glance's WINDOW ORIGIN in pixel space (`g["windows"][0]`, a `(top, left)` pair from
   `genome/gaze.py:glance_window`), not the 16×16 FIXATION CELL (`g["fix"][0]`).** DELIVER's literal line
   reads "where fixation", and the fixation CELLS still travel on the journal's own `fix` field, unchanged
   from before this gene. I chose the window origin for the field the SEAM actually carries because (a) it
   is what the retina's 112-vector was computed FROM, (b) it is what E51's A1.2 plant varies (two classes'
   windows differ only in pixel origin, not in which 16×16 cell was visited under a different grid), and
   (c) cell↔origin is a bijection away from clamped canvas edges (`glance_window`'s own `min(max(...))`
   clamp), so nothing is lost by carrying the finer-grained value. If the orchestrator wants the CELL
   instead (or both), that is a one-line change to `seam0`'s construction in `_consume_eye` — raised here
   rather than guessed silently.
2. **"onto the tape row's meta" (the brief's own words) landed on the JOURNAL row, not the tape row
   itself.** The tape row is written by the EYE SENSE thread, before the mind ever glances the picture —
   the window origin/glance index do not exist at tape-publish time, only at mind-consume time (the
   sealed gaze organ runs inside `Mind._consume_eye`, never in `creature/world_maker.py` or
   `creature/senses/folder.py`). The journal (`run_root/journal/*.jsonl`) is the mind's own per-tick
   record and plays the same "what happened on this tick" role the brief's phrase describes; I read "the
   tape row's meta" as shorthand for it. Nothing on the real tape (`run_root/tape/*.jsonl`) changed.
3. **`when` = the EYE row's own `at`** (the ISO instant `creature/tape.py:now_iso` stamped when the
   picture was published), not the matching EAR row's `at` (the word can arrive on an earlier tick; the
   mind glances the EYE row). This is the one wall-clock value `_consume_eye` already had in hand
   (`row["at"]`, the parameter — the determinism-law AST sweep in `test_mind_parity.py` still passes
   unmodified, since nothing here reads `time`/`datetime`/`random`).
4. **`glance` is always `0` today.** FAST only ever writes glance 0's feature vector to an episode (the
   pre-existing `f0 = g["feats"][0]`); the seam's `glance` field records THAT fact rather than inventing
   per-glance episodes. G-EYE-2/G-MIND-2 (BIND, out of this brief's scope) is what would make more than
   one glance reach FAST — `glance` is already the right field name for it to fill in later.
5. **`creature/genes.py` was touched though the brief's file list did not name it.** W3-0's registry
   (`RUNS`) refuses `Mind.__init__` for any declared gene with no named call site — since DELIVER/MOMENT
   ARE real call sites, leaving them out of `RUNS` would make every genome that declares them refuse to
   start (caught immediately by my own first test run against the real `Mind`, §3.4). Registering them was
   not optional once the interpreter existed; the registry's own test (`test_refusal.py`) then required
   its `SAMPLE_LINE` fixture updated too (§3.4) — the same two-step addendum-2's INDUCE/DEDUCE pin-move
   already established as the pattern on this branch.
6. **`--blind where` blinds `Episodes` only, not the journal.** `seam0`'s `where` key is `None` under the
   blind, so `Episodes.write` never receives it — but the journal row is built separately, straight from
   `g["windows"]`, so a blinded life's journal STILL carries `"windows"` for a human reading it. Deliberate:
   the blind exists to test the MECHANISM (can a rule that reads `where` answer above chance), not to hide
   the fact from a person auditing the run — but say so here, because a reader of a `--blind where` journal
   who expects `"windows"` to vanish too would otherwise read the blind as not having taken.

## 3 · Tests, every reading with its control and twin

All suites/tests run from the worktree root; genome text for the mind-level tests is
`tests/creature/G4-wave2-test.genome` (already declares `GAZE`+`PREDICT`+`FAST`) plus the two seam lines
appended (`SEAM_GENOME_TEXT` in the test file) — never `genome/G4.genome` itself, which stays undeclared
for either gene (§3.5).

### 3.1 · Parser (`tests/genome/test_deliver_moment.py`, 12 tests)
Each gene's own valid line parses; a missing word, an extra word, wrong case, or a substituted word
(`"where cell …"` instead of `"where fixation …"`) is refused **by name**; undeclared means absent from
`Genome.declared`; `FAST`'s own literal is untouched by MOMENT's existence; `genome/G4.genome` (the live
genome text) does not declare either gene (§3.5's own control).

### 3.2 · Episodes unit tests (`tests/genome/test_fast_seam.py`, 11 tests)
Write/get round-trip for all five new fields; the pre-existing call shape (no seam kwargs) reads back as
`None` everywhere, not a fabricated value; `glance=0` (a real value) is never confused with "absent" (the
`-1` sentinel); **`test_where_does_not_alter_x_s_or_cosine_recall`** — two episodes with IDENTICAL `x_s`
but different `where` still tie EXACTLY (`r[0][1] == r[1][1]`) under `nearest()`; `nearest_where`'s five
behaviours (exact match first, blind to `x_s` by construction, episodes with no `where` never candidates,
empty/all-blind store returns `[]`, the ring's overwrite drops `where` with the rest of the row); save/load
round-trip; loading a genuinely pre-seam `.npz` (hand-built with the OLD key set) defaults every seam field
to absent rather than raising.

### 3.3 · The seam reaching one real episode, on a real tape (`TestSeamReachesARealEpisode`, 1 test)
A small mixed tape (8 worded + 3 sight-only canvases) through the REAL `Mind.consume()` loop — never a
hand-built `Episodes` row. Every live episode (worded AND sight-only) carries a real `where` (2-tuple),
`when` (ends in `"Z"`, the tape's own instant), `act == "glance"`, `source == "test"` (the tape fixture's
own `meta["source"]`), `glance == 0`; the journal's canvas rows carry the same, additively (`"windows"` a
non-empty list, `"when"`, `"act"`, `"source"`, `"glance"` all present).

### 3.4 · PARITY — the refusing test (`TestSeamParity`, 2 tests + the registry fix)
- **`test_parity_state_hash_and_every_pre_existing_mark`**: the SAME tape (identical seed → byte-identical
  canvases) replayed under `WAVE2_GENOME_TEXT` (no DELIVER/MOMENT) and under `SEAM_GENOME_TEXT` (both
  declared) — `org.state_hash()` equal, `org.summary()` equal (every births/cells/edges/merges/scale-event
  count), and every journal row equal FIELD FOR FIELD once the seam's own five new keys are stripped from
  the seam run's rows (25 worded + 6 sight-only canvases, 31 canvas rows compared).
- **`test_negative_control_a_leak_into_the_cosine_is_caught`**: `genome.gaze.glances` monkeypatched so
  glance 0's feature vector is perturbed by `(top + left) * 1e-3` — exactly the failure G-EYE-1 forbids, a
  position folded into the cosine-compared vector — and the parity check above is proven SENSITIVE, not
  vacuously equal: re-run standalone with the hashes printed,
  **`base_hash = 7557b77ebe27c14e…`, `leaked_hash = 0ca2ccdd21f3aa17…` — DIFFERENT, CAUGHT.**
- **The registry fix, found by my own first run, not designed in advance:** `Mind.__init__` refused to
  start ANY genome declaring `DELIVER`/`MOMENT` until `creature/genes.py`'s `RUNS` named their call sites
  (§2.5) — three of my own new tests failed with `GenomeError: DELIVER, MOMENT declared but nothing runs
  it (W3-0)` on the very first run. Registering them then moved `tests/creature/test_refusal.py`'s own
  registry-pin fixture (`SAMPLE_LINE`), which failed for the same reason addendum 2 moved the INDUCE/DEDUCE
  one: the pin enumerates every `RUNS` gene and needs a parseable sample line for each. Fixed by adding the
  two rows; `python3 -m unittest tests.creature.test_refusal` reads `Ran 12 tests … OK` on the final bytes.

### 3.5 · Life 3a's real 2 h closed tape (a one-off, not part of `unittest discover`)
Life 3a's tape (`/data/dev/genome/run-g4-life3a-20260921-1314/tape/2026-09-21.jsonl`, 4,675 rows) replayed
via `creature.replay.run_replay` under (a) `genome/G4.genome` unmodified and (b) the same text + the two
seam lines appended — **both under the CURRENT worktree code** (rule 4: master's `creature/`/`genome/` are
byte-identical to commit 068e510, the code life 3a's and 3b's minds actually ran). Kept OUT of
`unittest discover` (≈300 s total; too slow for the routine suite — the same reason `tools/gate_g4.py` is
a separate script, not a discovered test) as `scratch/life3a_parity_check.py` (git-ignored; not committed).

```
base replay:  150.9s   (uptime load average 2.25–3.33 during this window: three other builders' full
seam replay:  151.9s    test-suite runs were active on this box at the same time — not a solo cost)
base rows: 2576   seam rows: 2576
base final hash: 52a804ebb7474271…
seam final hash: 52a804ebb7474271…
STATE_HASH PARITY: PASS
seam rows carrying the new (windows/when/act/source/glance) keys: 2338 of 2576
EVERY PRE-EXISTING FIELD PARITY: PASS
```
One real row from life 3a's own tape, through the real seam:
```
{"seq": 2, "moment": "w0000i000001t000000000", "word": "bar",
 "windows": [[4, 20], [4, 12], [4, 28], [0, 20]], "when": "2026-09-21T09:14:39.659Z",
 "act": "glance", "source": "maker", "glance": 0}
```
**A number worth explaining, not just reporting:** the base replay's final hash (`52a804eb…`) is
IDENTICAL to life 3a's own recorded `state_hash` in `state/organism.json`. §18 addendum 2 records what
looks like the opposite finding — that a replay of life 3a's tape under the FIXED mind DIVERGES from life
3a's own LIVE JOURNAL at seq 120/140 (the first THINK step whose kind the fixed pool-composition rule
chooses differently, because life 3a's LIVE journal was written under the PRE-FIX `think.py`, before
`genome/think.py:411`'s `r["cell"]` → `r["lit"]` change — my worktree's code is the FIXED code, so this is
a real code difference between the two runs, not a coincidence). The hash matching ANYWAY is the point,
not a contradiction to explain away: `Organism.state_hash()` is a pure function of the tape-driven
`org.moment()`/`org.moment_sight()` call sequence — the GAZE/RETINA/BIRTH/HEBB/DELTA/PRUNE/MERGE machinery
— which is entirely determined by the (fixed, real) tape and the (fixed, sha-pinned) gaze organ; nothing
the THINK step chooses to work on (a rule item vs a word item, which words get induced) ever calls
`org.moment()` or births/wires/prunes a cell. So a THINK-step divergence between the OLD code (life 3a's
own live run) and the FIXED code (this replay) moved JOURNAL ROWS — exactly what addendum 2 measured and
reported — **while moving nothing `state_hash()` reads.** That is direct, independent evidence for this
brief's own parity claim: a mechanism that writes into a store/record `state_hash()` never touches
(Episodes, the journal's THINK rows) cannot move the digest, whatever else about the code changed. My
base-vs-seam comparison (both on the FIXED code, §3.5's actual claim) is a narrower version of the exact
same fact.

### 3.6 · The E51 A1.2 position plant (`TestPositionPlantE51A12`, 3 tests)
`fixations` (Alpha 2's sha-pinned saliency organ — EYE.md's own scope, not this seam's) is replaced by a
controlled, deterministic routing rule for this test alone (a pure function of the picture's own content,
reading the one pixel that tells the two canvases apart) so the plant is not at the mercy of a black-box
saliency call landing on an exact 8-pixel grid cell — the same discipline #228(c) used when E51's own
position family had to be redeclared as "a window on a canvas."

- **(a) Ceiling first — chance is a fact, not a hope.** Cell A → window origin `(20, 20)`; cell B → `(68,
  68)`. `glance_window` on canvas A at cell A and on canvas B at cell B return **byte-identical** 32×32
  arrays (`np.array_equal` — asserted, not assumed) and `genome.machinery.retina()` on each (through
  `ink_border`, the genome's own INK rule) produces **identical** 112-vectors.
- **(b) The mind answers above chance, reading `where`.** 6 training episodes per class (12 total, real
  words `"classa"`/`"classb"`, real ear+eye tape rows, real `Mind.consume()`), then 5 query canvases per
  class (10 total, sight-only, the SAME byte-identical images). Read through `Episodes.get()` on the
  actual written episodes:
  - **x_s-blind road** (`nearest(x_s, k)`, filtered to training ids): **5/10 = 0.500 — EXACTLY chance**,
    and provably so, not merely near it: every candidate ties at cosine 1.0 (`x_s` is identical across
    both classes by construction), so the deterministic "smaller id first" tie-break always returns
    training id 0 (`"classa"`) regardless of the query's true class — right on every class-A query, wrong
    on every class-B one, 50% on a balanced 5+5 set BY THE TIE-BREAK'S OWN ARITHMETIC.
  - **`where`-reading road** (`nearest_where(where, k)`, filtered to training ids): **10/10 = 1.000** —
    perfect, because `where` IS the class signal by the plant's own construction (each class's queries
    reuse its own training window origin exactly, distance 0).
- **(c) The `--blind where` twin sits at exactly chance.** Same training+query shape, `Mind(..., blind=
  frozenset({"where"}))`: every episode (training and query alike) has `where is None`;
  `nearest_where` returns `[]` for anything; the only road left is x_s-blind — **5/10 = 0.500**, the SAME
  number as (b)'s ceiling, for the SAME reason (the tie-break). (The blind takes on `Episodes` only, not
  the journal — §2.6.)

## 4 · The 8 h / 2 h window clause (his 20:27 speed-up)

Nothing in `DELIVER`/`MOMENT`/`seam0`/`Episodes`'s new columns reads `WORLD`'s `arrival_every_h` (or any
other WORLD field) — the seam is per-glance/per-canvas, wired entirely inside `_consume_eye`'s own
per-row work, with no dependency on the arrival-window schedule at all. An 8 h life with `WORLD … arrivals
every 2 h` exercises the exact same code path, at the same per-canvas granularity, as a 24 h life with `…
arrivals every 6 h`. No clause here assumes 6 h.

## 5 · Raised for the orchestrator (not worked around)

1. **§2.1** — `where` = window origin, not the 16×16 fixation cell; the cell still travels on `fix`,
   unchanged. Flag if the design wants the cell as well/instead.
2. **A merge-time seam with Builder J (g5-bind-colour):** if J's BIND pools four glances into one
   `org.moment` call and/or reshapes `g["feats"]`/`g["windows"]` (112 → 144 with colour), the meaning of
   `g["windows"][0]` this seam reads (today: glance 0's own window) may change — my code reads whatever
   `gaze.glances` hands back positionally (`g["windows"][0]`), so it will not silently break, but the
   SEMANTICS of "glance 0" under a pooled-episode design is J's call, not mine; worth a joint look before
   both branches merge.
3. **`tests/genome/test_deliver_moment.py::test_g4_genome_does_not_declare_it_yet`** is a deliberate "not
   yet" pin (G5's own rule: "nothing here is switched on… no code before his yes," `docs/organs/
   BRIEF.md`/`G5-DESIGN.md §0`). The day `genome/G4.genome` actually declares `DELIVER`/`MOMENT`, this test
   must be updated in the SAME commit (addendum 2's own precedent for INDUCE/DEDUCE) or it will fail
   honestly, as designed.
4. **Nothing else raised.** Every clause of the brief (DELIVER, MOMENT, the three tests, the 8 h/2 h note)
   was implementable as specified; no bar was loosened; the one gate that failed (the W3-0 registry
   refusal, §3.4) was fixed, not worked around, and its own control (`test_every_runs_gene_parses`) is what
   proves the fix is real rather than papered over.

## 6 · Suites on the final bytes (commit `54f6bf8`)

```
$ python3 -u -m unittest discover -s tests/genome -t .   > scratch/FINAL_genome.log 2>&1
Ran 159 tests in 74.224s
OK (skipped=1, expected failures=6)

$ python3 -u -m unittest discover -s tests/creature -t . > scratch/FINAL_creature.log 2>&1
Ran 147 tests in 713.842s
OK
```
Launched after commit `54f6bf8` (working tree exactly HEAD — a stray unused-import edit made mid-run was
reverted with `git checkout` before this run, so these are genuinely the final committed bytes); load
average 7.79/6.30/4.34 at launch, 3.46/5.12/5.06 at finish (three to four other builders' worktrees ran
their own full suites concurrently on this box the whole time — not a solo cost; SOLUTIONS rule 2).
Test-count check: 139 (the baseline creature run, captured before any of this task's edits landed —
`scratch/baseline_creature.log`, `Ran 139 tests … OK`, confirmed pre-edit by timing: the process started
before the first `machinery.py` edit) + 8 new in `test_g5i_seam_deliver_moment.py` = 147 — matches.
`test_refusal.py`'s own count is unchanged (12 test METHODS before and after; the two new `SAMPLE_LINE`
rows are read inside an existing `subTest` loop, which does not add to `unittest`'s "Ran N tests" count).

(genome suite count check: 136 baseline (measured before any edit landed, `scratch/baseline_genome.log`,
`Ran 136 tests … OK`) + 12 new in `test_deliver_moment.py` + 11 new in `test_fast_seam.py` = 159 — matches.)

## 7 · Commits on `g5-seam`

- `a251185` — `.gitignore`: `scratch/` (orchestrator's correction, before any scratch file was written).
- `1100e22` — DELIVER + MOMENT: the parser, `Episodes`, `_consume_eye`'s wiring, the registry entries, the
  three new test files.
- `54f6bf8` — `tests/creature/test_refusal.py`'s `SAMPLE_LINE` pin, moved for the two new registry rows.

## 8 · What this report does not claim

It does not claim DELIVER/MOMENT should go live in `genome/G4.genome` — that is Ahmad's yes to give (§5.3,
`docs/organs/BRIEF.md`'s own rule). It does not claim anything about G-EYE-2/BIND, G-EYE-3..7, or any other
line of `docs/organs/G5-DESIGN.md §3`/§4 — those are other builders' briefs. It does not claim the
`fixations` mock in §3.6 says anything about Alpha 2's real saliency organ's accuracy — that mock exists
precisely to keep this seam's own test independent of that organ's behaviour, which is EYE.md's scope.
