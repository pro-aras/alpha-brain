# Builder K report — ACT/OUTCOME/SIT/body sense
*edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:20 +0400. Branch `g5-acts`, worktree `/data/dev/genome-wt-o`, from master `ec28b4c`.*

## What was built

Four new genome lines, each a strict `re.fullmatch` in `genome/machinery.py`'s parser, each registered with a real call site in `creature/genes.py`'s `RUNS` (or `Mind.__init__`'s generic W3-0 refusal names it and the organism does not start):

```
ACT      glance open ask                                          # the vocabulary; declared["ACT"]["verbs"]
OUTCOME  act to episode; error grades it; ranks replay             # declared["OUTCOME"]
SIT      exam every 2000 canvases; the score returns as a sense    # extends EXAM; declared["SIT"]["every"]
SENSE    body every 60 s fields moments births arrivals budget_left refused restarts mind_ms rss   # declared["SENSE_BODY"]
```

`genome/G4.genome` itself was **never edited** — every test builds a temp genome from its text plus the
new lines (`test_gene_values.py`'s own `_append` technique), pinned by `test_g4_genome_itself_never_declares_any_of_the_four`.

### The mechanism: a dedicated "reflex" episode ring, never `self.episodes`

`creature/mind.py:Mind.__init__` builds `self.outcome_episodes` (a second `genome.fast.Episodes` instance,
cap 2000 — a code constant, no numeric parameter exists in either OUTCOME's or SIT's fixed gene text) when
EITHER `OUTCOME` or `SIT` is declared. Both an "outcome" tape row and a "sit" tape row (SIT's score, tagged
`act="sit"`) are written into it through one shared helper, `Mind._record_reflex`.

**Why not `self.episodes` (the brief's own words: "the existing modulator is pointed at a new source ...
SLEEP already replays surprising acts into SLOW")** — RAISED, not built. Two independent ways it corrupts
the organism, both found before writing any code that would have hit them live:
1. `genome/sleep.py:sleep()` replays the `n` most-surprising live episodes as **ordinary moments**:
   `org.moment(rec["x_s"], rec["x_w"])`. An act has no sight glance. A zero `x_s` makes
   `Area.cos()` (`machinery.py:423`, a plain dot product with **no norm division**) read exactly `0.0`
   against every cell — below `THETA_N` — so `_resonate` (`machinery.py:550`) **births a garbage sight
   cell every single replay**.
2. A *real* glance vector paired with `encode_word(act)` avoids (1) but is not safe either: stage 2's
   `_hebb`/`_delta` (`machinery.py:566`) would wire that visual context to a non-"thing" word
   ("open"/"ask"/"sit"), competing with the real word on Q1 recall — the exam itself would be corrupted,
   and it would get replayed 200×/sleep by construction (SLEEP's own `n`).

There is no safe `(x_s, x_w)` pair for a reflex observation under the **current** SLEEP law. The ring gives
`most_surprising()`/`nearest()` for free (literally reusing `genome/fast.py`'s existing class, no new
learning machinery written) so "ranks replay" is a real, working, tested capability *on this ring* — but
`genome.sleep.sleep()` is never pointed at it. `x_s[0]` doubles as the ring's own scalar payload slot (the
reflex's `got` value) — never read by `cos()`/`_resonate` since this ring never reaches `Organism.moment()`.
This is also why `--blind outcome`/`--blind sit` are Mind-level (senses never receive `blind` anywhere in
this codebase; matches the existing `"gaze"`/`"predict"`/`"curiosity"` precedent).

**The residual is a real prediction, not a magnitude reading (#175).** `expected` = the row's own value if
supplied (trusting the publisher — e.g. a future HANDS/game mechanism, or Builder L's game reward); else the
mind's own **per-act running mean of past `got` values** (`self._act_expected`/`self._act_n`, updated
*after* grading the current observation so the next one is graded against it, not this one). `residual` =
the row's own value if supplied; else `|got - expected|`; else `None` ("not gradable", #228 (a) — never a
fabricated 0). The running mean is **not persisted** — `Mind.resume()` rebuilds it by replaying the ring's
own live entries in id (== temporal) order, reading `x_s[0]` back as each entry's own `got`.

### THINK's "outcome" kind

`_think_pool()` gains a fourth-ish kind: one item per distinct act among the last 50 live reflex episodes.
`_think_work()`'s new branch reads the episode and returns `{"outcome": "reflected", "residual": ...}` — a
read-only reflection (no FILE claim: nothing downstream consumes an "is this act predictable" claim yet, a
further growth line, not built here). Kind fairness (`_think_choose`) needed **no changes** — it is already
generic over any kind string. Pinned by a walk that actually drives THINK across enough passes for the pool
to carry an "outcome" item and for `_think_choose` to pick it at least once (#232's addendum: a branch no
test reaches crashes on its first real walk).

## §seam — the outcome tape row's shape (for Builder L and anyone else publishing sense="outcome")

Envelope (the tape's own, unchanged): `seq`, `at`, `sense="outcome"`, `sha`, `payload`. `meta` carries
**exactly**:
```json
{"moment": "<any string>", "act": "<str>", "expected": <float | null>, "got": <float | null>,
 "residual": <float | null>, "source": "<str>"}
```
- `act`: any string; tagged `in_vocab` against `declared["ACT"]["verbs"]` if `ACT` is declared (never
  refused if out of vocabulary — journaled, not crashed).
- `expected`/`residual` may be `null`; the mind fills what it can (see above). If your publisher already
  knows the residual (e.g. a game's reward vs. a target), supply it directly — it is trusted as-is.
- `got` should be a float; a missing `got` is treated as ungradable, never a crash.

SIT's own rows (`sense="sit"`) are a **separate, simpler** shape: `meta = {"moment", "source", "score", "exam_file"}`,
internally re-expressed as a reflex with `act="sit"` — so a SIT reading shows up in the SAME
`outcome_episodes` ring and the SAME `"outcome"` THINK kind, for free.

Body sense rows (`sense="body"`): `meta = {"moment", "source": "body", "reading": {<the declared fields>: <STATUS value or null>}}`.
Not put through the reflex ring at all (see "What was not built" below).

## Readings, each with its control/twin

**G-MOT-2 plant** (`tests/creature/test_g5k_outcome.py::TestOutcomePlantAndTwin`, seed 2026, 60 rows
interleaving a predictable act "open" (`got` constant 0.9) and an unpredictable one "ask" (`got` ~
Uniform(0,1))):
- **REAL** residual: "open" floors at exactly `0.0` from its second occurrence on (its running mean
  converges instantly to a constant — a clean, unambiguous demonstration, not a gradual curve, since the
  plant is deterministic). "ask" stays noisy (first-5 mean 0.127, last-5 mean 0.164 in the pinned run — does
  **not** collapse toward 0).
- **TWIN** (E21's own shape: `|got_t - got_{t-1}|` over the **whole interleaved stream**, act-blind):
  both arms read ~0.49–0.52 throughout — it **cannot tell the acts apart at all**, dominated by the A/B
  alternation rather than either act's own predictability. Real gap (open vs ask, last-5) ≫ twin gap
  (asserted `twin_gap < real_gap / 2` — the actual pinned run: real_gap ≈ 0.16, twin_gap ≈ 0.02).
- `--blind outcome`: 5/5 acts journaled (`{"outcome": {...}}` rows present), `ep: null` on every one, ring
  stays at `n_written == 0`.

**G-MOT-3 SIT, the pre-registration check MOTOR-HANDS.md's own words require** ("refuse the line if the
score is constant across life 2's ten files ... print it") — run against the **closed** life-2 root
(`/data/dev/genome/run-g4-life2-20260920-1212/exam/`, read via a hard-link copy under this worktree's
`scratch/`, hard rule 3), using `sit.py`'s **own** `_score_of`/`_latest_exam_file` functions (dogfooding the
real code, not a re-derivation):
```
9 files (not 10 — LAST.json is the tenth *.json glob match, excluded by design):
[0.9909, 0.9909, 0.9727, 0.9636, 0.9909, 0.9727, 0.9818, 0.9455, 0.9273]
```
Not constant (range 0.064) — **the line is not refused**. (The brief's own quoted numbers, ".995 → .952",
do not match the file on disk; the disk is authoritative here, not chased further per the advisor's
instruction.) `_latest_exam_file` correctly picks the newest **digit-prefixed** file, never `LAST.json`
(`exam.py`'s own #168-class scar, checked structurally).

**BODY-SENSES §4.1 body sense**: "the numbers on the tape equal STATUS's at the instant (± one write)" —
tested two ways: (a) a pure field-mapping unit test against a hand-built STATUS.json (exact equality); (b) a
live `Body` with `SENSE_BODY` + `HEART every 1 s` declared, reading a real published "body" row and a
STATUS.json read strictly after it — the row's monotone counters (`moments`, `births`) are asserted `<=`
the later STATUS read (never larger — never stale-in-the-wrong-direction). Replay exactness: the same row
consumed into a **second, fresh** Mind produces a byte-identical journal row (no clock, no randomness in
`_consume_body`).

**Snapshot/resume**: the reflex ring and the per-act running expectation both survive a `snapshot()` +
`Mind.resume()` round trip (`_rebuild_act_expectation`, replayed from the ring's own entries). `org.state_hash()`
is asserted unchanged by outcome/sit/body rows in every test that touches it — none of the three mechanisms
ever reaches `Organism`.

## What was RAISED, not built

1. **"SLEEP already replays surprising acts into SLOW" / "PREDICT's modulator already scales learning by
   them" (G-MOT-2's own words)** — see the corruption analysis above. `genome.sleep.sleep()` is never
   pointed at `self.outcome_episodes`; `genome.predict.Predictor` is untouched (its `error()`/`modulate()`
   are bound to sight-cell cosine comparisons and would need new state to accept an outcome residual — not
   built, to avoid inventing new learning machinery the brief explicitly says is not required).
2. **BODY-SENSES §4.1's own refusal test, read strictly** ("count the moments in which any journaled
   decision differs [with the sense armed vs not]") — as built, arming `SENSE_BODY` changes **only the
   journal** (an extra "body" row every period); nothing downstream (THINK's pool, CURIOSITY, FILE) yet
   consumes a body reading, so a strict reading of "any journaled decision differs" is not yet met. No
   consumer exists to wire it to within this brief's scope (the DRIVE/threshold explicitly stays out per
   the document's own words — "this gene must not carry a threshold").
3. **`KNOWN_BODY_THREADS` (`creature/body.py`) does not know "sit"/"body"** as thread-roster category
   names. If a future `BODY service creature threads eye ear door mind voice sit body` line is ever written,
   `_check_body_threads` refuses it today. Not fixed here — that set is Wave-3-C's coarse taxonomy
   (`"door" covers ask/folder/web`; there is no obvious existing bucket for "sit"/"body"), a decision for
   whoever owns that gene's next revision, not this builder's file.
4. **SIT vs EXAM's cadences are independent by design, not mutually refused.** SIT's own "every" value is a
   real, read parameter (mirrors `exam.py:voice_loop`'s own ledger-based canvas cadence exactly) that
   governs how often SIT **checks** for a newer exam file — a completely separate concern from EXAM's own
   cadence for **producing** one. They can differ with no conflict (SIT just checks less/more often than
   EXAM writes); considered and rejected a mutual-refusal rule since there is no actual contradiction to
   refuse.
5. **The act census (G-MOT-1: "one count per verb, never a total")** — `self._act_n` already tracks a
   per-act count as a side effect of the running-mean mechanism, but is not exported to STATUS (no shape was
   specified for it beyond what the three explicit test requirements ask for). Available via
   `mind._act_n` for a future mark; not wired to a surface.
6. **CURIOSITY never learns from an "outcome" reflection** — `_think_work`'s "outcome" branch never calls
   `self.interests.update(...)` (unlike "word"/"rule" kinds via `_grade_rule`), so the kind's popularity
   weight never moves from its initial value. Matches the existing "due" kind's same omission (not a
   regression, an existing pattern); a "was this outcome useful to have reflected on" signal does not exist
   yet to grade it by.

## Suite results

*(final counts to be filled in once the concurrently-running full suites across other worktrees on this
box free up enough CPU for a clean, uncontended run — `nice -n 10`, ≤ 3 workers per hard rule 2; every
number below is quoted from a log, never typed from memory)*

- `tests/creature/test_g5k_outcome.py` alone, twice, clean: **23 tests, OK** both times.
- `tests/creature/test_writer_sweep.py`: OK (the two new sense modules walk clean — no state/journal/memory
  write, no Organism import; `sit.py`'s `from genome.machinery import parse_genome` is not flagged, since
  the sweep only flags `Organism`/bare `machinery` imports, not `parse_genome`).
- `tests/creature/test_mind_parity.py`: OK, including `test_mind_has_no_clock` (the AST sweep) — this
  builder's edits import nothing of time/datetime/random/os.urandom.
- Full `tests/genome` (`-t .`): **Ran 136 tests ... OK (skipped=1, expected failures=6)** — byte-identical
  to the pre-change baseline count.
- Full `tests/creature` (`-t .`): baseline (before this builder's changes) **Ran 139 tests ... OK**.

## Commits (branch `g5-acts`)

- `7d186f8` — `.gitignore`: add `scratch/` (orchestrator correction, before any scratch work).
- *(this report's own commit, plus the implementation commit(s), listed at hand-back)*
