# W3-BUILDER-A-REPORT — W3-0, W3-3, think_counters

*edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 23:45 +0400. Branch `g4-wave3-a`, worktree
`/data/dev/genome-wt-d`. Three commits, in order: `e7a28c5` (W3-0), `429b250` (W3-3), `b4d37e9`
(think_counters, extended mid-task on the coordinator's integration note about Builder B's landed
W3-1). Nothing merged to master; `/data/dev/genome/*` never touched.*

## Pin hash — before and after every task: UNCHANGED

`d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86` (`tests/genome/test_pin_skeleton.py`'s
own `PIN_HASH_DEV`). Not re-derived at the base commit because it cannot have moved by construction: every
task here only changes `creature/mind.py`/`creature/genes.py`, and `G4-skeleton.genome` / `G1.genome`
declare **zero** G4 §3 genes (`genome.declared == {}` for both, confirmed by
`tests/creature/test_refusal.py::TestPositiveControls::test_skeleton_and_g1_genomes_start`), so
`genes.unwired({})` is always `[]` and the new refusal, the new think_counters keys and the new
`sleep_boundary()` call are all on code paths the pin's own genome never reaches. `gate_g4.py`'s G4-2 line
confirms it directly after every commit (see below): `d4b5c6b8d57f35e6… vs pin d4b5c6b8d57f35e6… → PASS`.

## Gates — after the final commit (`b4d37e9`), each read from its own log file

`tests/genome/test_pin_skeleton.py` (`/tmp/wt-d-report-logs/pin.log`):
```
Ran 1 test in 9.210s

OK
```

`python3 tools/gate_g4.py --tree /data/dev/genome-wt-d` (`/tmp/wt-d-report-logs/gate_g4.log`), full output:
```
G4-1 writer sweep over 5 files: 0 offenders
G4-1 control: planted offender CAUGHT
G4-2 mind parity: d4b5c6b8d57f35e6… vs pin d4b5c6b8d57f35e6… → PASS
G4-2 control (two canvases swapped): 6f851d20ce2b28f8… → CAUGHT
G4-3 replay identity: exit 0 → PASS  REPLAY identical: 120 mind rows
G4-3 control (payload byte flipped at seq 62): exit 1 → CAUGHT  DIVERGED at seq 62: births
G4 gates: {'1': 'PASS', '2': 'PASS', '3': 'PASS'}
```
(the three lines the brief asks for are G4-1/G4-2/G4-3's own `→ PASS`/`CAUGHT` lines, quoted above verbatim;
the dict line is the script's own summary.)

`tests/creature/test_arrival.py` (`/tmp/wt-d-report-logs/arrival.log`):
```
Ran 3 tests in 6.691s

OK
```

Full suites, run sequentially (a first parallel attempt hit a `tests/genome` `__pycache__` race —
`ImportError: Start directory is not importable: 'tests/genome'` — cleared and re-run clean; not a code
regression, noted here per the verification discipline rather than silently discarded):
- `python3 -m unittest discover -s tests/creature -t .` → **`Ran 86 tests in 526.073s` / `OK`**
  (`/tmp/wt-d-final-creature.log`; 73 pre-existing + 3 `test_sleep_boundary` + 10 `test_think_counters`).
- `python3 -m unittest discover -s tests/genome -t .` → **`Ran 128 tests in 118.516s` / `OK (skipped=1, expected failures=9)`**
  (`/tmp/wt-d-genome-retry.log`; genome/ is Builder B's tree and untouched by this branch — unchanged count
  and skip/xfail totals from before this work).

## Task 1 — W3-0: THE GENERIC REFUSAL

**Commit:** `e7a28c5`. **Log** (`/tmp/wt-d-report-logs/w3-0.log`, `tests/creature/test_refusal.py`, 9 tests):
```
Ran 9 tests in 0.012s

OK
```

**The RUNS table** (`creature/genes.py`), built by exhaustive grep of `declared[`, `in ...declared`,
`org.g.declared` across `creature/` and `genome/` — a gene earns a site only if some line actually reads
its presence or its value; the parser recognising a gene (every declared gene has that, trivially) does
not count:

| Gene | Layer | Site | Declared value read? |
|---|---|---|---|
| CYCLE | machinery | `genome/machinery.py:Organism._birth` (soft ceiling) + `genome/sleep.py:cycle` (consolidation) | yes (`grow_to`) |
| FAST | mind | `Mind.__init__` (Episodes built) + `Mind.resume` (episodes.npz reloaded) | yes (`episodes`) |
| PREDICT | mind | `Mind.__init__` (Predictor built) + `Mind.resume` (rebuilt against loaded org) | value unused (no params today) |
| PARK | mind | `Mind.__init__` (Park built) | yes (`after`) |
| CURIOSITY | mind | `Mind.__init__` (Interests built, gated on `genome.curiosity` importable) | yes (`interests`) |
| ARRIVAL | mind | `Mind._consume_eye` (`Organism.new_arrival()` on a never-heard word) | value unused (no params) |
| SLEEP | mind | `Mind._maybe_sleep` (every/replay read) + `Mind.resume` (`_last_sleep_at` rebuilt) | yes (`every`, `replay`) |
| THINK | mind | `Mind._maybe_think` (gated: absent → return; `every` read otherwise) | yes (`every`) |
| FROZEN | mind | `Mind.__init__` (`declared['FROZEN']['after']` read **only** when `'frozen' in blind` — a twin-only gene, PREREG §11.1 step 5) | yes, conditionally |
| FILE | mind | `_think_work` (`predict_file()` for `"sight"` pool items) — **called ungated by FILE's own presence** | **no** (four field names never read) |
| BELIEF | mind | `_think_work` (`think_laws.believe()` for `"word"` pool items) — call itself **ungated** by BELIEF's presence; `clash_enabled=("BELIEF" in declared)` **is** gated on it, passed once `believe()` accepts the kwarg | **no** (the `"clash opens never overwrites"` text is never parsed as a parameter — only the gene's *presence* now does anything, via `clash_enabled`) |
| EXAM | body | `Body.start` (`declared['EXAM']['every']` read; starts the voice/exam thread) | yes (`every`) |
| BODY | body | `Body`/`SenseThread` — thread wiring is fixed by code | **no** (`threads` list never read) |
| TAPE | body | `creature/tape.py:Tape.__init__` — `root/'tape'` hardcoded | **no** (`path` never read) |
| HEART | body | `creature/body.py:STATUS_PERIOD_S=10.0` constant | **no** (`every_s` never read) |
| CRASH | body | `SenseThread.run` (journal on restart) + `Body._handle_mind_crash` (page) — unconditional | **no** (value never read) |
| WORLD | body | `Body.main --maker-period` default 5.0 / `world_maker.sense` period | **no** (`drawn_every_s`/`folder`/`web_per_hour` never read) |
| ASK | body | `creature/ask.py:answer` — the six verbs are hardcoded `if q == ...` | **no** (`verbs` never read) |
| TRAITS | mind | **`None`** — no interpreter anywhere (PREREG §12/§14) | n/a — always refused |

**The finding, stated plainly:** of G4.genome's 18 actively-declared genes, **8 have a real call site but
their declared VALUE is never read anywhere** (FILE, BELIEF, BODY, TAPE, HEART, CRASH, WORLD, ASK) — a
`HEART every 60 s` line would change nothing; `BODY`'s thread list is documentation of a fact the code
already guarantees, not a switch. This is the same class of defect TRAITS was (a declared gene the
machinery does not run), one notch less dangerous only because nothing currently claims to interpret a
*number* that in fact does nothing. Per the PREREG's own W3-0 contract text ("the mind carries a table of
the genes it INTERPRETS, **the body its own (BODY, TAPE, HEART, CRASH, WORLD, ASK, EXAM)**") these six are
named as belonging to the body's table by design, so they are entered as wired with a real site rather than
refused — but the "value read? no" column is the honest, load-bearing part of this deliverable and is
carried into every comment in `creature/genes.py` itself, not just this table. **Raised, not worked
around:** whether FILE/BELIEF/BODY/TAPE/HEART/CRASH/WORLD/ASK should eventually read their declared values
(and refuse a mismatched one, e.g. a `HEART` value that disagreed with `STATUS_PERIOD_S`) is a design
question for whoever owns those constants next, not something I changed here.

`unwired(declared)`: `wired = {gene for layer in RUNS.values() for gene, site in layer.items() if site is
not None}`; returns `sorted(gene for gene in declared if gene not in wired)`. `Mind.__init__` calls it
immediately after `parse_genome`, before any object is built from the genome, and raises
`GenomeError(f"{', '.join(bad)} declared but nothing runs it (W3-0): the organism does not start")` naming
every offender. The old standalone TRAITS-only `raise` is retired — replaced by its `RUNS["mind"]["TRAITS"]
= None` row.

**Toys, all four, all PASS:**
- (a) positive: `genome/G4.genome` starts a `Mind` in a temp root (plus `G4-skeleton.genome`/`G1.genome`,
  which declare nothing new and must be completely untouched — confirmed `declared == {}` for both).
- (b) `G4.genome` + an active `INDUCE rule from 5 episodes no counter` line → `GenomeError` naming
  **only** `INDUCE` (every gene G4.genome already declares is asserted absent from the message).
- (c) the planted control: a `parse_genome` wrapped to inject `declared["PLANTED"] = {...}` into a
  real, otherwise-clean `Genome` → refuses naming `PLANTED` (exercised through the full `Mind.__init__`
  path, and again directly against the bare `unwired()` function).
- (d) every RUNS gene (all 19, including the `None` TRAITS row) is one line the parser itself recognises —
  fed alone, the only possible `GenomeError` is the unrelated "genome lacks [...] required" one, never
  "unknown gene".

**Clauses met in full.** No clause of W3-0 was raised as unimplementable.

## Task 2 — W3-3: `Interests.sleep_boundary()` wired

**Commit:** `429b250`. **Log** (`/tmp/wt-d-report-logs/w3-3.log`, `tests/creature/test_sleep_boundary.py`, 3 tests):
```
Ran 3 tests in 8.246s

OK
```

One line in `Mind._maybe_sleep`'s `while` loop, after the `_write_journal` call (one boundary crossed → one
call): `if self.interests is not None: self.interests.sleep_boundary()`.

**A real gap found and worked around correctly, not silently:** `Interests.update()` — the method that
actually appends to `_window_answered` and is the only thing `sleep_boundary()`'s reset can matter to — is
**not called anywhere** by `creature/mind.py` today (`_think_work`'s outcome vocabulary — `"belief"`,
`"filed"`, dead-end reason strings — is not yet the same vocabulary as `Interests.update`'s `{"answered",
"parked","filed","scored"}`; wiring that mapping is a separate, later job, not named by W3-3). So the toy
plants "answered" items **directly on `mind.interests`** — exactly the words the clause uses ("plant one
answered item before a sleep and one after") — around a **real** SLEEP boundary crossed by a real tape
through `Mind.consume` (never a synthetic, hand-called `_maybe_sleep`).

**Positive:** window is `[]` immediately after the first real boundary crossed; the pre-boundary and
post-boundary plants end with **different** final weights (2.0 vs 1.5 in the concrete run) — generalize
still applies to both (population-wide, kind-scoped, unaffected by the window), but recombine — which
*is* window-scoped — never fires across the boundary.

**Negative control (the clause's own ask):** `mind.interests.sleep_boundary = lambda: None` (the exact
line this commit adds, removed) on the identical tape and plants → the window survives the boundary
uncut, and the two plants **do** recombine to the same mean weight (1.75 == 1.75). Verified NOT vacuous by
hand: temporarily neutering the real wiring (`if False and self.interests is not None: ...`) makes the
*positive* test fail with the expected assertion (`[('word','planted_before')] != []`), confirmed, then
reverted.

**Clauses met in full.** No clause of W3-3 was raised as unimplementable.

## Task 3 — think_counters (the brief's "Also" item), extended for Builder B's landed W3-1

**Commit:** `b4d37e9`. **Log** (`/tmp/wt-d-report-logs/think-counters.log`,
`tests/creature/test_think_counters.py` + `tests/creature/test_wave2_belief_path.py`, 11 tests):
```
Ran 11 tests in 77.468s

OK
```

`Mind.think_counters` gains `"revisits": 0, "extensions": 0, "clashes": 0` (body.py already spreads
`think_counters` into STATUS on every write — no change needed there). `_think_work`'s `"word"` branch now
reads the returned row's `"kind"` (`{"belief","revisit","extension","clash"}` → the matching counter;
absent or unknown → `"beliefs"`, never a `KeyError`).

**Mid-task instruction from the coordinator** (Builder B's W3-1 landed on `g4-wave3-b`, worktree
`genome-wt-e`, commit `04a302a`, read there **read-only** — this branch never imports or includes his
files): `believe(word, cells, episode_ids, moment, path, ledgers=None, clash_enabled=True)`. Two
integration facts handled, both in `creature/mind.py` only:
1. `ledgers` (already computed above the call site) and `clash_enabled=("BELIEF" in self.genome.declared)`
   are now passed — but **only when this tree's own `genome/think.py.believe()` actually accepts them**,
   detected once via `inspect.signature(think_laws.believe).parameters` (`_BELIEVE_KWARGS`, module level).
   Today's tree still has the plain 5-parameter `believe()` (Builder B's file is not on this branch), so
   `_BELIEVE_KWARGS` is empty and the call is **byte-identical** to before this commit; the moment
   `genome/think.py` gains those parameters (at merge), the same call site starts passing both
   automatically, with no second edit here.
2. `tests/creature/test_wave2_belief_path.py`'s `len(rows) == counters["beliefs"]` invariant is
   generalised to `len(rows) == beliefs + revisits + extensions + 2*clashes` — all four read from
   **Mind's own `think_counters`** (never re-derived by re-classifying `beliefs.jsonl`'s individual rows,
   which cannot tell "this row is the clash" from "this row is what it opened against"). Reduces to
   exactly the old check in this tree today (`kind` is always `"belief"`; clashes/revisits/extensions all
   read 0) and stays correct once the dedupe lands and any of the three others starts firing.

**Tests, all real, none vacuous:**
- `TestBackwardCompatibleWithTodaysBelieve`: today's real, unstubbed, end-to-end belief formation still
  counts into `"beliefs"` and nothing else moves.
- `TestKindToCounterMapping` (6 tests): a stub matching Builder B's new signature returning each of
  `"belief"`/`"revisit"`/`"extension"`/`"clash"` counts into exactly the matching counter and nothing
  else; a missing `"kind"` key and a genuinely unknown kind string both count as `"beliefs"` and neither
  raises.
- `TestLedgersAndClashEnabledPassthrough` (3 tests): a stub matching the new signature captures a
  non-`None` `ledgers` dict carrying `"sight"`/`"words"` keys and `clash_enabled=True` (G4.genome declares
  BELIEF); with `BELIEF` deleted from the in-memory `declared` dict, `clash_enabled` reads `False`; a stub
  matching **today's exact old signature** (no `ledgers`/`clash_enabled` parameters at all) receives
  **no** extra keywords and does not `TypeError` — the backward-compatibility guard, proven rather than
  assumed.
- `test_wave2_belief_path.py`'s own end-to-end test (150 canvases, real tape) still passes under the
  generalised identity.

The one non-trivial piece of test engineering: `_think_pool()` computed fresh **after** all 150 canvases
are consumed contains no genuinely-abstaining word (by the end of the run most words already resonate on a
single glance, so they never enter the pool) — so a naive "pool at the end, replay an item" approach found
nothing. Fixed by spying on `_think_work` **during** the real `consume()` loop to capture the actual
item(s) `_maybe_think` worked that resolved to `"belief"` mid-stream, then re-verifying the most mature
(latest) captured item once more before handing it to the stub tests.

**Clauses met in full.** No clause was raised as unimplementable; the coordinator's two integration facts
are both handled without editing `genome/*`.

## Summary of clauses raised (unimplementable, not worked around)

None of W3-0, W3-3, or the think_counters "Also" item had a clause I could not implement. The one thing
worth Claude's attention before merge is the **8-gene "value read? no" finding** in the W3-0 table above —
not a blocker (G4.genome starts fine, all gates green), but a real gap the PREREG's own instrument now
names structurally for the first time.
