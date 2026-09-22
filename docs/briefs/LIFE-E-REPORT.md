# LIFE builder E report — THE THINKING THREAD (L-5)
*by Claude (Sonnet 5, LIFE builder E), 2026-09-22 21:5x +0400. Brief: `docs/briefs/LIFE-E-THINK-THREAD.md`. Branch `life-think` off `g5-integration` at `0a640f0`.*

## 0 · One-line summary
THINK now runs on its own thread when the genome's own line asks for it (absent — every genome on disk
today — the inline road is untouched); "word"/"self" kind thinks (the ones that need `Organism.recall_many`/
`genome.questions.build_ledgers`/`why`) are launched at boundary N on a frozen, bounded copy and applied
at N+every; every other kind (sight/due/rule/frame/outcome) still runs and applies synchronously — a scope
cut found EMPIRICALLY (§4) and load-bearing for shift-equivalence. Life 3a's whole tape replays with 0
content-order mismatches across all 232 comparable think rows.

## 1 · What landed, file:line

- `genome/machinery.py:397-408` — THINK's `re.fullmatch` gains the optional tail `; on its own thread;
  lands next boundary`. Absent → `declared["THINK"] == {"every": int}` **exactly** as before (no "threaded"
  key at all, not even `False`) — every pre-existing test/genome pinning that bare shape is untouched.
  Present → `declared["THINK"]["threaded"] = True`.
- `creature/body.py:39-46` — `KNOWN_BODY_THREADS` gains a sixth name, `"think"`. Pure validation (the
  class's own pre-existing law): a genome may list it without the THINK gene ever threading, and vice
  versa — the two facts are read independently (BODY's roster by `_check_body_threads`, the mechanism by
  `Mind.__init__`'s `declared["THINK"].get("threaded")`).
- `creature/think_thread.py` (NEW, 280 lines) — the think thread's own module: `_freeze_area`/
  `freeze_recall_view` (a shadow `Organism` whose `W`/`mask` are sliced to `(sight.n, words.n)`, not the
  full NMAX×NMAX allocation — bounded by how many cells are alive, not by NMAX=6000's 288 MB), `self_trigger`
  (a verbatim copy of `Mind._self_trigger`), `decide()` (the pure per-kind decision — see §4 for which kinds
  actually route through it today), `worker_run`/`wait_for` (timing — this module owns every wall-clock
  read the threaded road needs; `creature/mind.py` never calls `time.*` itself).
- `creature/mind.py`:
  - `__init__` (~L258-283): `_think_threaded`, `_think_executor` (a `concurrent.futures.ThreadPoolExecutor
    (max_workers=1)`, built only when threaded), `_think_pending`, `think_waits`, `think_wait_ms`,
    `think_ms_last`, `_think_ms_history` (capped 500).
  - `_maybe_think` (~L1660-1721): unchanged inline road; dispatches to `_maybe_think_threaded` when
    `self._think_threaded`.
  - `_maybe_think_threaded` (~L1740-1793), `_think_apply_pending` (~L1795-1834), `_think_apply_plan`
    (~L1836-1943): the launch/apply pipeline. `think_ms_median()` (~L1946-1953).
  - `_file_rule` (~L1629-1666): gains an optional `due_canvas` parameter (default `self._canvas_index`,
    byte-identical to every existing call site) so the threaded road can pin a rule's own due-canvas to its
    LAUNCH boundary, never the later apply boundary.
  - `close()` (~L2038-2049): applies a still-pending think before the final snapshot, shuts the executor
    down.
- `tools/gate_g4.py:15-22,63-76` — `SENSE_FILES` gains `creature/think_thread.py` (item 4: the writer sweep
  did not reach it; now it does — `G4-1 writer sweep over 10 files: 0 offenders`, control CAUGHT).
- `creature/genes.py:65,91` — doc text updated (BODY's "known five" → "known six"; THINK's entry names the
  threaded road).
- `tests/creature/test_life_e_think_thread.py` (NEW, 16 tests) — the parser tail, BODY's sixth name, the
  executor built only when threaded, the frozen copy holds no live reference (`is not` on every array +
  `recall_many` on the shadow agrees with the live organism), the writer sweep reaches the module (+ a
  planted-offender negative control), shift-equivalence + replay-determinism on a synthetic tape, a raising
  `decide()` journals `outcome: "error"` and never kills the mind, STATUS exports the four new fields.
- `tests/creature/test_life_seams.py` — filled the two stubs gated on my own landing (`_wired("SURPRISE",
  "SELF") and "lands next boundary" in machinery.py`, `_worker_obeys() and "lands next boundary" in
  machinery.py`): `test_BxE_…` (a CONFIRMED episode never reaches the think pool, hence never the frozen
  copy) and `test_DxE_…` (D's act choice is a mind-thread call, `creature/think_thread.py` names neither
  `_maybe_choose_act` nor `game/ACT`, and a static+live check both confirm it).
- `tests/creature/test_gene_values.py:311-320` — `test_the_lifes_own_line_starts` no longer asserts G4.genome's
  five threads equal the FULL known set (now six, since "think" is opt-in) — #232 addendum (c)'s own class
  of merge-time flip, fixed by asserting the two facts that still hold (subset, and the sixth name exists).

## 2 · Tests: RED → GREEN
Development on this brief was **iterative direct verification** before the formal suite existed (the brief
is a from-scratch mechanism with no prior code to extend test-first against) — two REAL bugs were found and
fixed this way, then formalized as the permanent 16-test file, green on its first run:

1. **RED**: `AttributeError: module 'creature.think_thread' has no attribute 'wait_for'` — the first live
   run of the threaded mind on a synthetic 200-canvas tape crashed at the first apply. **GREEN**: added
   `wait_for()` (creature/think_thread.py) — re-ran the same script, mind completed (20 thinks, 3 beliefs, 7
   filed).
2. **RED**: a shift-equivalence check (inline vs threaded, same 400-canvas tape, same seed) diverged
   starting at the 9th think — identical FILED/SCORED totals but a DIFFERENT item chosen from there on.
   Root cause traced (§4): deferring `_induce_pending`/`_deduce_pending`/`_frame_pending`/`_filed_predictions`
   bookkeeping to apply time let the SAME rule/prediction stay pool-visible on boundaries where inline had
   already excluded it, desyncing `_think_choose`'s rng draws. **GREEN** (first attempt, marking the
   pending-sets synchronously): still diverged at the same point — a second read showed `_filed_predictions`
   (used by "due" kind candidate generation) had the SAME class of gap. **GREEN** (final): scoped the
   threaded pipeline to "word"/"self" kind ONLY (the two kinds that actually need `Organism.recall_many`);
   every other kind calls the ORIGINAL `_think_work` synchronously — re-ran the same 400-canvas check:
   `IDENTICAL under the shift: 40 think rows, 0 diffs`.
3. **GREEN on write**: `tests/creature/test_life_e_think_thread.py`'s 16 tests, `Ran 16 tests in 34.801s —
   OK` on the first formal run (no red iteration needed — the mechanism they pin was already the one
   verified live above).
4. **RED→GREEN, the two seam stubs**: `test_BxE_…`/`test_DxE_…` were `self.fail("fill at the landing: …")`
   stubs (the coordinator's own convention) — RED the instant my landing made their `skipUnless` true (both
   failed with the stub's own message). Filled with real assertions (§1); GREEN on write.
5. **RED→GREEN, a pre-existing test whose premise my own change flipped**: `test_the_lifes_own_line_starts`
   (`tests/creature/test_gene_values.py`) asserted `set(G4.genome's threads) == KNOWN_BODY_THREADS` — true
   at 5==5 before this brief, false at 5⊂6 after (`KNOWN_BODY_THREADS` gained "think"). RED on the first
   full-suite run after landing the parser/BODY changes; fixed to assert the two facts that still hold
   (§1's own note, #232 addendum (c)'s class — a test pinning a merge-time absence another lane's own
   change flips).

**Suites on the final bytes** (logs under `scratch/logs/`, this worktree, `export TMPDIR=$PWD/scratch/tmp`):
- `python3 -m unittest discover -s tests/creature -t .` → `Ran 416 tests in 467.474s` — **OK (skipped=1)**
  (`scratch/logs/suite-creature-final.log`).
- `python3 -m unittest discover -s tests/genome -t .` → `Ran 268 tests in 62.693s` — **OK (skipped=1,
  expected failures=6)** (`scratch/logs/suite-genome-final.log`).
- `python3 tools/gate_g4.py --genome genome/G4-skeleton.genome --only 1` → `G4-1 writer sweep over 10 files:
  0 offenders` / `control: planted offender CAUGHT` / `G4 gates: {'1': 'PASS'}`.
- `python3 tools/gate_g4.py --genome genome/G4-skeleton.genome --only 2,3` → `G4-2 mind parity:
  b05315037ff98529… vs pin b05315037ff98529… → PASS` (the pin is **unmoved** — the skeleton genome never
  declares THINK's threaded tail, so this brief changes nothing it touches), `G4-3 replay identity: PASS`,
  both controls CAUGHT.

## 3 · The shifted comparison — life 3a's whole tape (the landing control, item 3)
`genome/G4.genome` (inline) vs the same file + the two lines (`BODY … threads … mind think voice`,
`THINK every 10 canvases; on its own thread; lands next boundary`), both replayed via
`creature.replay.run_replay` over `/data/dev/genome/run-g4-life3a-20260921-1314/tape/2026-09-21.jsonl`
(4,675 tape rows) into fresh scratch roots (never the life's own):

```
inline replay:   2576 mind rows in 47.1s
threaded replay: 2575 mind rows in 50.9s (via run_replay — see the tail note below)
think rows: inline 233, threaded 232 (kind counts: word 64, rule 66, sight 62, due 40)
content-order (item, kind, outcome, parked), first 232 rows compared: 0 mismatches
non-think mind rows: inline 2343, threaded 2343, 0 mismatches
```

**The shift rule, found empirically (§4's scope cut) and confirmed here**: "word"/"self" kind rows carry
`launched_at = N` and land `THINK.every` CANVASES later (their own journal `seq` matches whatever the tape's
own eye-row seq is at canvas N+every — life 3a's tape has sight-only stretches, so this is NOT a fixed
seq delta of `every*2`; confirmed directly against the raw tape: canvas boundary 180's eye row is seq 360 in
both roads, canvas boundary 190's is seq 379 — not 380 — in BOTH the inline comparison point and the
threaded apply, because roughly one sight-only canvas fell in that ten-canvas window). Every other kind
(sight/due/rule/frame/outcome) is unshifted — its `seq` and content are identical to the inline road's,
canvas for canvas.

**The one-row tail difference (233 vs 232), fully explained and resolved**: `creature.replay.run_replay()`
never calls `Mind.close()` (a pre-existing convention this brief did not change) — it only calls
`mind.consume()` over every tape row, then reads the journal directory. The very LAST think the threaded
road launches (at the tape's final THINK boundary) therefore never gets a chance to apply within
`run_replay`'s own flow, because there is no NEXT boundary to trigger it, and `run_replay` never asks the
mind to close. Confirmed directly (not via `run_replay`): consuming the SAME tape through a plain `Mind` +
an explicit `mind.close()` call gives `thinks == 233`, matching inline exactly, and the recovered tail item
is `('dot', 'word', 'belief', False)` — the SAME item inline's own last think row names. **RAISED, not
fixed**: `run_replay()` is shared infrastructure (every builder's replay-based gate reads it); teaching it
to call `close()` is a real behaviour change for every OTHER caller and is out of this brief's file list —
a live `Body` (via `Body.stop()`) and any DIRECT caller of `Mind.close()` already flush correctly; only a
`run_replay()`-based A/B comparison specifically under-counts the threaded road's very last tape by one
think.

## 4 · The scope cut — RAISED, with its reasoning (item 3's "no other difference" gate)
Item 2's letter asks that EVERY write a think makes be deferred to apply time — rules to file, beliefs,
wants parked, question rows, frames, say rows. Building this literally for ALL seven pool kinds broke
shift-equivalence (§2, bug 2): "sight"/"rule"/"frame"'s own IN-MEMORY bookkeeping (`_filed_predictions`,
`_induce_pending`/`_deduce_pending`/`_frame_pending` — the SETS `_think_pool()` reads, live, to decide
whether a candidate is still offered) were also deferred, and `_score_due_predictions`/`_think_pool()` read
them on EVERY canvas, not just at THINK boundaries — a candidate that inline had already excluded after
boundary N stayed offered on every threaded boundary up to N+every, changing the POOL COMPOSITION, hence
the number of `_think_choose` rng draws, hence every choice after it. Marking the sets synchronously (at
choose-time, mirroring how `_self_worked_seq` already had to be) closed most but not all of the gap
(`_filed_predictions` itself, feeding "due" kind, has the same class of hole).

**Decision**: only "word" and "self" — the two kinds that actually need `Organism.recall_many`/
`genome.questions.build_ledgers`/`why` (an O(alive cells) read, the one that can genuinely grow as the
organism does, and the one SOLUTIONS #236's own finding was about before its `induce()` hoist) — go through
the launch/apply pipeline. Every other kind is cheap (bounded by a ring's own size or already fully computed
during pool-building) and continues to run and apply IMMEDIATELY, synchronously, at the SAME boundary as
the inline road — calling the ORIGINAL, unmodified `_think_work` (zero risk of behavioural drift, since it
is literally the same code path). `creature/think_thread.py:decide()`'s sight/due/rule/frame/outcome
branches and `Mind._think_apply_plan`'s matching branches are BUILT and were unit-tested for
content-equivalence against `_think_work` during development, but are presently DEAD CODE on the wired
pipeline — left in place (harmless, documented) as the starting point for whoever next fixes the
pool-gating-timing gap and re-routes them through the thread.

**Other raised points, each named at its own site in the code:**
- **MOUTH (`_maybe_say`) is never deferred.** Its own law (LIFE-C-QUESTION-SENTENCE.md task 4) judges THIS
  canvas's own instant synchronously ("the songbird's loop… no external judge"); deferring it to N+every
  would judge a DIFFERENT canvas, changing what it means, not merely when it runs. Item 2's "say rows" among
  a think's writes is read as the general class, not a directive to move MOUTH.
- **`believe()`'s `ledgers` kwarg reads LIVE state at apply time, deliberately** (`_think_apply_plan`,
  the "believe" branch) — it is believe()'s OWN drift check (has a cell since been reassigned?), and a
  frozen-at-decide ledger could never disagree with cells decided from that same frozen state, which would
  make the check a no-op. This is the one place the two roads can genuinely diverge in CONTENT
  (revisit/extension/clash classification, never whether a row is written at all) if births/merges land
  between launch and apply. Not observed on any test tape run this session (§3: all 23 belief rows on the
  life 3a comparison matched field-for-field, kind counters included) — named as a theoretical possibility,
  not a measured one.
- **F's "hands" think kind** (the coordinator's mid-task note, §5): not on this tree at write time.
  `creature/think_thread.py`'s module docstring and `decide()`'s own docstring name the fold-in shape: a
  `{"hands_act": {...}}` plan entry, applied by `Mind._think_apply_plan`, with the program draw moved onto
  `frozen.rng` (never a mind-local `_hands_rng` mutated from the background thread — that would be a second
  writer of mind state AND non-reproducible under replay). "hands" is a cheap-kind candidate under §4's own
  rule (a jail-program pick, not an organism read) unless its own cost profile says otherwise.
- **`think_ms` does not capture `freeze_inputs()`'s own copy cost.** The L1 replay (§5) shows `think_waits`
  at 0/832 and `think_ms` staying under 10 ms even at hour 11 — but the max single-row consume gap (1.64 s)
  is far larger than that, and is NOT visible in either number, because `freeze_inputs()` (the shadow-org
  slice + episodes deepcopy) runs SYNCHRONOUSLY on the mind's own thread, before submission — its cost is
  absorbed into the ordinary per-row consume time the body already measures (`mind_ms_median_1min`), not
  into `think_ms`. RAISED for a future session: a `prepare_ms` counter alongside `think_ms` would make this
  visible on its own line.

## 5 · The L1 replay — think ms series and waits (item 5)
`/data/dev/genome-lives/g5-ladder-L1/tape/{2026-09-21,2026-09-22}.jsonl` (16,653 rows total) replayed under
`genome/ladder/L1.genome` + the two lines, in a fresh scratch root (`scratch/L1-threaded-run/`, tape/payload
SYMLINKED, never the life's own root) via a plain `Mind` + `read_tape` loop (never `creature.replay`, so
`close()` — hence the tail think — is included):

```
rows consumed: 16653   wall time: 351.5 s
max single-row consume gap: 1641.9 ms at row 16298   (PREREG §19.2 bar: ≤ 5.1 s — MET, 3.1x headroom)
thinks: 832   think_waits: 0   think_wait_ms total: 0.0   (bar: waits/thinks < 5% — MET, 0%)
think_ms_last: 6.35   think_ms_median (whole run): 3.89

think ms series per hour (median, n, max):
  hour  0: n=77  median=1.72 ms  max=2.59 ms
  hour  1: n=84  median=2.29 ms  max=3.87 ms
  hour  2: n=79  median=3.40 ms  max=4.78 ms
  hour  3: n=72  median=3.61 ms  max=5.35 ms
  hour  4: n=72  median=4.01 ms  max=5.05 ms
  hour  5: n=72  median=4.01 ms  max=6.49 ms
  hour  6: n=71  median=4.95 ms  max=5.67 ms
  hour  7: n=72  median=6.09 ms  max=6.09 ms
  hour  8: n=72  median=5.11 ms  max=6.29 ms
  hour  9: n=71  median=5.82 ms  max=8.59 ms
  hour 10: n=71  median=5.42 ms  max=7.61 ms
  hour 11: n=13  median=6.35 ms  max=7.82 ms
```
Reported, not tuned to: `think_ms` grows roughly 3.6x from hour 0 to hour 11 (1.7→6.3 ms) as the organism's
alive-cell count and the FAST episodes ring grow — consistent with the shadow copy's own bound (§1: sliced
to alive cells, not NMAX) growing with the life, not staying flat. `think_waits` stayed at 0 for the WHOLE
run: every "word"/"self" decide() completed well inside its own `every`=10-canvas window every single time
on this tape — the launch/apply pipeline never once blocked the mind thread on this life's own cadence.

## 6 · Register (item 6)
`creature/genes.py` — updated (§1). `genome/LIFE.genome`'s two DRAFT lines needed **no syntax change** —
confirmed by parsing them directly (`BODY … threads eye ear door mind think voice` and `THINK every 10
canvases; on its own thread; lands next boundary` both parse to exactly the shape this brief's parser
change produces). The file as a WHOLE still refuses to parse (an unrelated, not-yet-landed `SENSE smell`
line from builder F) — not this brief's concern, and LIFE.genome is coordinator-owned/pre-flight-checked,
not edited here. Their comment text ("refuses until the machinery names it") is now stale (it no longer
refuses) but is left for the coordinator's own pre-flight pass to update alongside every other builder's
DRAFT line.

## 7 · Commit
Branch `life-think`, commits on top of `0a640f0`:
1. `genome/machinery.py`, `creature/body.py`, `creature/think_thread.py` (new), `creature/mind.py`,
   `tools/gate_g4.py`, `creature/genes.py`, `tests/creature/test_life_e_think_thread.py` (new),
   `tests/creature/test_life_seams.py`, `tests/creature/test_gene_values.py` — the mechanism, its gate
   coverage, and the seam fills.
2. This report.

Final commit sha: **filled in after the commit below** (see the tool output).
