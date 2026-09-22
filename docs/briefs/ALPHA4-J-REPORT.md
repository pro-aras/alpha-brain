# Builder J (Sonnet 5) — EVOLVE: report
*Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23. Branch `alpha4-evolve`, off master at `74c661d`.*

**FIRST LINE: adoption is FULLY implemented — this did NOT fall back to `EVOLVE … propose` (proposals
only). A mutant genome is drawn, judged paired against the incumbent, and — on PASS — adopted live at the
next SLEEP boundary: `GENOME.v<n>.genome` is written, `self.genome`/`self.org.g` are re-parsed, the epoch
is journaled as a replay-comparable MIND row, and `Mind.resume` is epoch-aware across a process restart.
Proven with real replay-identity tests (two independent replays from birth are byte-identical, epoch event
included) and against `life 3a`'s own real 2,576-row tape (see "life 3a" below).**

## What is NOT done, and why

1. **The creature's own EXAM/SIT threads read the BIRTH genome after an adoption — a real, live gap I did
   not fix.** `creature/body.py:Body.__init__` reads `self.genome_path` ONCE, from the launch CLI argument,
   and passes that SAME path unchanged to `creature/exam.py:voice_loop` (the self-exam thread, its Q1 feeds
   STAGE 4's readiness judge) and `creature/senses/sit.py:sense` (`genome_path=self.genome_path`, SIT's own
   reflex score) — neither is threaded through `Mind.resume`'s new epoch-aware resolver
   (`_latest_evolved_genome`), because neither is `Mind.resume` at all: both build their OWN throwaway
   `Organism`/genome directly from that fixed path. After an adoption, the creature's own exam and SIT score
   are computed under the RETIRED thresholds (theta_n, kwta, …), not the ones his mind is actually running.
   **The fix is three lines** — resolve `_latest_evolved_genome(root)` in `creature/body.py:main` (or in
   `exam.py`/`sit.py` themselves) and pass that path instead of the birth one — but `creature/exam.py` and
   `creature/senses/sit.py` are outside this brief's named files (owned by earlier waves' builders B and K),
   and I chose not to touch them unbidden mid-parallel-build. Raised here, not worked around.
2. **`Mind.resume`'s `_last_sleep_at` recompute (`(org.t // every) * every`) uses the CURRENT genome's
   SLEEP.every** — exact only when `every` was constant for the whole life. A pre-existing class of gap
   this codebase already carries for Park/Interests/`_filed_predictions` (none of which are persisted
   either); EVOLVE makes this ONE specific instance reachable for the first time (a mutated SLEEP.every
   before a resume). Not fixed — named, matching the standing precedent for this class of gap.
3. **BOUNDS excludes `PARK.after`'s sibling `INDUCE.from_episodes`, and `FROZEN.after`, on a CONSERVATIVE
   reading of an ambiguous brief clause.** The brief's item 1 first lists "every numeric gene value the
   parser reads" (including FROZEN and INDUCE) as candidates, then narrows with "Mutate RATES and
   THRESHOLDS only: theta_n, DELTA lr, KWTA, BUDGET …, PARK after" — a sentence that does NOT mention
   INDUCE at all, and FROZEN's own `creature/genes.py` RUNS row already says it is TWIN-ONLY (read only
   when `"frozen" in blind` — a live genome never reads it, so a live proposal could never grade a mutation
   of it). I read the final "only" sentence as the closed, authoritative list: PARK.after IS included
   (kept), INDUCE.from_episodes is NOT (excluded, named with this exact reasoning in
   `creature/genes.py:BOUNDS["INDUCE.from_episodes"]["reason"]`). This is an interpretation, not a silent
   guess — flagged for the integrator to override if the intent was otherwise.
4. **BUDGET's future "regenerate 1 per 60 moments" clause (builder G's own addition, `genome/ALPHA4.genome`
   line 38) is not in THIS worktree's grammar** — `genome/machinery.py`'s BUDGET branch here still only
   accepts `BUDGET <n> per arrival`. `BOUNDS["BUDGET.per_arrival"]`'s own substitution pattern is written
   to survive that clause once it lands (tested directly: `apply_mutation` on a SYNTHETIC line carrying
   `; regenerate 1 per 60 moments` preserves it byte-for-byte — see `TestRoundTrip.
   test_budget_suffix_survives_mutation_and_a_future_regen_clause`), but this has never been exercised
   against G's REAL landed parser branch (not merged into this isolated worktree). A seam risk for
   integration, not a defect in what is here.
5. **"Retention" (PREREG §5/§6's own named 2 h-gradable reading) is not an independently gradable number on
   a shared-start slice.** Both twins in a judging round start from the SAME checkpoint, so Q1-at-start is
   identical for both by construction — a "Q1(start) − Q1(end)" formula would just restate Q1(end). I did
   NOT invent a second, independent formula to fill this slot (that would be exactly the "never re-
   implement a mark" rule broken in spirit even without reusing an existing name). `q1_seen_start` is
   printed once per round (on the checkpoint, before either twin runs) and `evolve_mark`/the proposal record
   both carry a `retention_note` saying so explicitly. Raised as a PREREG-level finding: retention, as the
   brief names it, is not a fact a 2 h EVOLVE slice can independently measure; if a design HAS wanted a
   genuinely-informative retention reading it would need staggered/non-shared-start checkpoints, out of my
   scope to redesign.
6. **The negative control against a REAL closed life (g5-seam-1) is slow.** The shadow must replay the
   life's own tape from birth up to the −2 h boundary before it can checkpoint at all — on seam-1's
   37,100-row pre-window (real 32×32 eye rows through the sealed CNN tower, ACT/OUTCOME reflexes, SIT,
   threaded THINK) this took **the measured ≈28.5 CPU-minutes given in the "COST" paragraph of the
   negative-control section below** (derived there from the worker process's own ≈55 total CPU-minutes
   minus the four twins' own ≈26.5 CPU-minutes, which the proposal records state exactly) — confirmed NOT
   a bug: a direct 1000/3000-row timing probe on the same genome (169/138 rows/sec) badly under-estimated
   the full run because per-row cost (auto-snapshot compression of a 32 MB W matrix every
   `SNAPSHOT_EVERY=500` moments; `build_ledgers`-class O(cells)-ish work in THINK) GROWS with the
   organism's own size, and a fresh Mind's first few thousand rows are the CHEAP, small-organism part of
   that curve. This IS the brief's own COST deliverable (item 5: "measure the shadow's
   CPU share and the twins' wall time on the seam-1 slice; report both") — the numbers are below, not a
   thing left undone, but they are the reason this report took real wall-clock time to finish.
7. **Two structural limits of a judging round's own readings, found in review (advisor-caught) and NOT
   fixed — recorded on every proposal and printed by `evolve_mark`, never silently hidden.** (a)
   `reward_mean` (`act_mark`'s own field) is read from the SLICE's own recorded outcome rows, which BOTH
   twins consume unchanged regardless of their own genome — it is therefore mathematically IDENTICAL for
   incumbent and mutant on every round (the exact same collapse as retention, item 5 above), can never
   clear its declared MARGINS entry, and can never register as a regression either; it is only a live
   signal once a genome actually drives the game (`ACT` declaring both `turn` and `step`, as ALPHA4's own
   genome does — seam-1's does not, `mind_drives_acts` reads False there, so this specific limit never
   fired in the negative control below). (b) On a genome that DOES drive acts, a mutant twin whose chosen
   action diverges from the tape's own historical choice (made under the INCUMBENT, never the mutant) is
   graded `act_mismatch > 0` by `act_mark`'s own bar, which fails `act_pass`, which `regression_bar` reads
   as a REGRESSION — structurally more likely for ANY mutation that changes a decision-relevant gene,
   independent of whether the change is actually better. Neither limit changes what THIS brief delivers
   (the mechanism, the bar, the tests); both are PREREG-level findings about what the bar can and cannot
   see, exactly the kind of thing item 5's "not gradable"/"printed, not graded" convention already exists
   to carry — `evolve_mark`'s own docstring and bar text now say so explicitly.
8. **`shadow_lag_rows`** (the gap between the live tape's own head seq and what the shadow has actually
   consumed at judging time) is now recorded on every proposal and surfaced as `evolve_mark`'s
   `max_shadow_lag_rows` — PRINTED, never gating (#236's own failure mode: a box loaded with other
   builders' work can let the shadow fall behind, silently shrinking a round's slice below `judge_h` while
   the record still claims the full window). Added after the advisor's own review of this brief's first
   commit; not present in the numbers already gathered against g5-seam-1 below (that run pre-dates the
   field — its own `advance_shadow` calls there always fully catch the shadow up before judging, so its
   TRUE lag was 0 throughout; the field exists for when a live 24 h life runs the worker continuously
   beside five other builders' own lives, which this negative control does not simulate).

## A real bug, found and fixed during my own review

`creature/senses/evolve.py:sense()` originally did `for p in sorted(evolve_dir.glob("PROPOSAL-*.json")):`
— `sorted()` on `Path` objects sorts the raw filename STRING, and `"PROPOSAL-10.json"` sorts
LEXICOGRAPHICALLY *before* `"PROPOSAL-2.json"` (bytewise, `'1' < '2'`). Empirically confirmed:
`sorted([Path(f"PROPOSAL-{n}.json") for n in range(1,13)])` reads `1, 10, 11, 12, 2, 3, 4, …, 9`. Publishing
in that raw order would advance the DISK cursor past 10 on the first scan that ever sees a double-digit
proposal number, then permanently SKIP 2 through 9 (`n <= last_done` filters them out on every future
scan) — exactly the class of bug `creature/senses/game.py`'s own manifest names are zero-padded to avoid
(its own docstring: "the filename's own zero-padded index sorts bytewise == numeric order"). A life
running past its 10th proposal (PREREG's own mark wants ≥ 3 per 24 h, so any life past ~3.5 days) would
have silently lost 8 real proposals from the record. Fixed: sort by the EXTRACTED INTEGER, never the path
string. Regression test added (`test_ten_or_more_proposals_publish_in_numeric_order_none_skipped`,
1..12 proposals, asserts the exact published order) — found by re-reading my own file against the
game-worker precedent it was explicitly modelled on, not by a failing test (there wasn't one until I wrote
this one).

## Tests: RED → GREEN

Before this brief, `EVOLVE` did not exist as a gene, `creature/genes.py` had no `BOUNDS`, `tools/evolve.py`
did not exist, and `creature/mind.py` had no `_consume_proposal`/adoption path — every test below is new
and would have failed on import alone (`GenomeError: unknown gene 'EVOLVE'`, `ImportError`, or
`AttributeError`) against the pre-brief tree. All are green on the final bytes:

```
$ python3 -m unittest tests.genome.test_parse_evolve tests.creature.test_evolve_bounds \
    tests.creature.test_evolve_adoption tests.creature.test_evolve_sense \
    tests.creature.test_evolve_body_integration tests.creature.test_verdict_life_marks \
    tests.creature.test_refusal tests.tools.test_evolve_worker
Ran 117 tests in 66.203s
OK
```
(`scratch/my-tests-final2.log`, `python3 -m unittest discover` invoked under `nice -n 10`, `TMPDIR` set per
the rules.) Breakdown: 24 in `test_parse_evolve`+`test_evolve_bounds` (the EVOLVE grammar, refusing tests,
the 15-entry BOUNDS table, round-trip mutation at lo/hi/mid for every mutable gene, rng determinism), 13 in
`test_evolve_adoption` (PASS adopts at the next SLEEP boundary, REFUSED never adopts, the epoch row is a
MIND row surviving `read_mind_journal`'s own filter, PARK/CURIOSITY live-patch, a second epoch mutates from
the FIRST epoch's own text, two independent replays byte-identical including the epoch event, `Mind.resume`
epoch-aware, a malformed mutant text is refused not crashed), 10 in `test_evolve_sense` (cursor persistence
so a sense-thread restart never double-publishes and double-adopts, a torn JSON file retried not skipped,
the writer-sweep planted-offender controls the brief's own rules ask for, the 10+-proposals sort-order
regression below), 5 in
`test_evolve_body_integration` (a REAL `Body` with EVOLVE armed the way `creature/body.py:main` wires it —
worker subprocess + sense thread — produces a real shadow checkpoint on disk within seconds; STATUS exports
`evolve_epoch`/`evolve_proposals_seen` on every write, #164, 0 on a genome that never declares EVOLVE), 7 in
`test_verdict_life_marks::EvolveMark` (proposals/pairing/adoptions/negative-control clauses of the mark
itself), 15 in `test_refusal` (the pre-existing generic-refusal suite, extended with EVOLVE's own
`SAMPLE_LINE` row — see below), 17 in `test_evolve_worker` (the regression bar's every clause,
checkpoint/twin/slice machinery, a real paired judging round on a synthetic tape, the negative control's
own machinery on a synthetic stand-in), plus 24 already counted above.

### Both full suites, on the final bytes

```
$ python3 -m unittest discover -s tests/genome -t .
Ran 284 tests in 65.649s
OK (skipped=1, expected failures=6)
```
(`scratch/suite-genome-final.log`)

```
$ python3 -m unittest discover -s tests/creature -t .
Ran 548 tests in 565.116s
OK (skipped=1)
```
(`scratch/suite-creature-68f0e9f.log` — the suite's THIRD full run, this one on the exact bytes of the
SECOND (follow-up) commit `68f0e9f`, the true final state of this branch: 546 on `da0464c` + 2 new
`shadow_lag_rows` tests in `test_verdict_life_marks.py` = 548, OK. History, for the record: the FIRST run
(536) started before the STATUS export / EvolveMark tests / sort-bug fix landed — stale, per the advisor's
own catch; the SECOND run (546, `scratch/suite-creature-COMMITTED.log`) confirmed `da0464c` itself; this
THIRD run confirms the branch's actual HEAD.) The very first run of all caught a real, pre-existing-fixture
omission of mine along the way: `tests/creature/test_refusal.py:TestRegistryPinnedToParser` pins every
`creature/genes.py` RUNS entry against a hand-written sample genome LINE (the same fixture G5 builders
I/J/K and LIFE builders A/B/C/F all had to extend when they added their own RUNS rows) — I had added
`RUNS["mind"]["EVOLVE"]` without adding `SAMPLE_LINE["EVOLVE"]`, and the suite caught it by name
(`test_every_runs_gene_parses`, `test_sample_line_set_is_exactly_the_registry`) exactly as it is designed
to. Fixed (one row added, matching the file's own convention); every subsequent run green.

## Gates

```
$ python3 tools/gate_g4.py --tree /data/dev/genome-wt-aa --genome genome/G4-skeleton.genome
G4-1 writer sweep over 12 files: 0 offenders
G4-1 control: planted offender CAUGHT
G4-2 mind parity: b05315037ff98529… vs pin b05315037ff98529… → PASS
G4-2 control (two canvases swapped): 55bcde154c429f6f… → CAUGHT
G4-3 replay identity: exit 0 → PASS  REPLAY identical: 120 mind rows
G4-3 control (payload byte flipped at seq 62): exit 1 → CAUGHT  DIVERGED at seq 62: births
G4-6 two senses on one tape: exit 0, evidence present, folder rows 13 → PASS  ...
G4 gates: {'1': 'PASS', '2': 'PASS', '3': 'PASS', '6': 'PASS'}
```
Gate 1 (the writer sweep) globs `creature/senses/*.py`, which now includes `creature/senses/evolve.py` —
0 offenders confirms it never imports Organism/machinery and never writes under state/journal/memory. The
brief's own extra ask ("+ a planted offender: an evolve worker that writes state/") is
`tests/creature/test_evolve_sense.py::TestWriterSweepCatchesAnEvolveOffender` — two planted "evolve"-shaped
offender files (one importing Organism, one writing under `state/`) run directly through
`tools.gate_g4.sweep`, both CAUGHT, plus a positive control that the REAL module sweeps to zero offenders.

`tools/inventory.py` on a fixture genome declaring EVOLVE (see "genome/ALPHA4.genome" below for why the
real file could not be used):
```
[inventory] EVOLVE      MADE           genes.RUNS   unread: -
[inventory] tests/creature/G4-evolve-test.genome: 21 rows - DECLARED-ONLY 0 - VALUE-UNREAD 3 - OFF 6 -> clear
```
The 3 VALUE-UNREAD rows (HEBB, MEET, RECALL) are pre-existing, unrelated to EVOLVE (RECALL's own genome
comment already documents this gap: "kept because the machinery refuses a genome without it").

### `genome/ALPHA4.genome` does not parse standalone in this isolated worktree

It already carries builder G's `BUDGET … ; regenerate …`/`GROW`/`CYCLE` lines, builder H's `SENSE read`/
`DOOR lexicon` lines, and builder I's `DOOR web`/`STAGE 3`/`STAGE 4` lines — none of which this worktree's
`genome/machinery.py` recognises yet (each builder works in a SEPARATE worktree; PREREG §8 step 3 merges
them at `alpha4-integration`). Every EVOLVE-specific test here instead uses a fixture derived from
`genome/LIFE.genome` (which parses cleanly, byte-tested unaffected by this branch) plus my own EVOLVE line
— `tests/creature/G4-evolve-test.genome`, built the SAME way `test_sleep_boundary.py`'s own
`_write_sleep_curiosity_genome()` derives its fixture (base text + appended lines, never an edit to the
base file). The EVOLVE parser branch, RUNS entry, and BOUNDS table will need to be re-verified against the
REAL merged `genome/ALPHA4.genome` at integration time — nothing here depends on that file's OTHER lines,
so I expect this to be a formality, but it is untested against the actual merged bytes.

### `life 3a`'s tape, replayed under this tree

```
EVOLVE declared on life3a genome: False
replayed rows: 2576
life3a recorded mind rows: 2576
diff (no masking): (2, 'hash')
diff (hash masked): (140, 'think')
```
Both divergences are PRE-EXISTING and ALREADY DOCUMENTED, independent of this brief: seq 2's hash is the
environment/pin drift `tests/creature/test_surprise_coarse.py::TestLife3aReplayIdentity`'s own docstring
names ("a pre-existing environment/pin drift … that predates and is outside this brief"); seq 140's `think`
field is the SAME rng-choice divergence `docs/G4-PREREG.md`'s own record names verbatim ("diverged from the
live journal at seq 140 (the first think whose kind the rng chose differently; the 139 rows before it
byte-identical)"). EVOLVE is not declared on life 3a's own genome, so none of this brief's new code paths
(`_consume_proposal`, `_maybe_adopt_evolve_proposal`, the epoch-aware `resume`) are reachable on this tape
at all — the replay is identical to the documented pre-existing baseline, meaning this branch introduces
ZERO new divergence on an unrelated genome (the additive-change guarantee W3-0-style branches are supposed
to have).

## The negative control (brief item 4, run before any life)

Run via `python3 tools/evolve.py --negative-control --root <copy of g5-seam-1> --genome <its genome> --out
<scratch>`, `nice -n 10`, on a `cp -r` copy under `scratch/negctl-seam1/` (never the closed record under
`/data/dev/genome-lives/g5-seam-1/` itself — verified byte-identical to the source via `md5sum` on every
tape `.jsonl` file both before AND after the run).

**Operational note for the pre-flight (PREREG §8 step 5):** `tools/verdict_g4.py`'s own EVOLVE wiring
looks for the negative control's two output files at `root/evolve/NEGATIVE-CONTROL-planted_bad.json` and
`root/evolve/NEGATIVE-CONTROL-null.json` (`root` being whatever life it is reading). For the READER to
pick these up on `alpha4-1`, whoever runs the pre-flight negative control must pass `--out` pointing INTO
`alpha4-1`'s own root (`<alpha4-1 root>/evolve`), not an arbitrary scratch directory as this validation
run used — the run below used `scratch/negctl-seam1/_out` on purpose (seam-1's copy is not, and must never
become, `alpha4-1`'s own root).

```
shadow consumed 37100 rows up to seq 37100 (T-2.0h checkpoint)
shadow consumed 7225 more rows to the tape's end (seq 44325)
planted_bad (BIRTH.theta_n=0.5): verdict=REFUSED reason=q1_seen: incumbent 0.9727272727272728, mutant 0.6727272727272727 (regressed)
planted_bad incumbent q1_seen=0.9727272727272728 mutant q1_seen=0.6727272727272727 q1_seen_start=0.9727272727272728
null (DELTA.lr=0.051): verdict=REFUSED reason=no reading cleared its declared margin (no regressions either — a null mutant)
null incumbent q1_seen=0.9727272727272728 mutant q1_seen=0.9727272727272728 q1_seen_start=0.9727272727272728
planted_bad REFUSED: True; null REFUSED: True
EXIT CODE: 0
```
**A reconciliation, not a coincidence:** seam-1's own `CLOSED-AT` file records the life's mind at seq
37,086 against a tape at seq 44,325 (lag 7,239) at the moment it was closed. This worker's checkpoint —
computed independently, by finding the tape row whose OWN "at" timestamp is closest to (last "at" − 2 h),
with no reference to that recorded lag — landed at seq 37,100, 14 rows later than where the live mind had
actually reached at close. The two numbers agree to within 0.2 % via two unrelated derivations (one from
the mind's own real-time consumption before it fell behind under the six verdict-readers' load that
night; one from this worker's post-hoc timestamp arithmetic on the same tape) — the kind of agreement
that makes a number a fact about the record rather than an artifact of whichever tool produced it (#168's
own rule: "agreement to a nameable difference is what makes it a fact about the subject").

(`scratch/negctl-seam1-run.log`, full output.) **COST (brief item 5), exact numbers from the proposal
records themselves (`NEGATIVE-CONTROL-*.json`'s own `wall_s` fields, never estimated):** the FOUR twin
replays (incumbent+mutant × 2 rounds, each over the identical real 7,225-row 2 h slice) took **381.8 s /
445.9 s** (planted_bad: incumbent/mutant, cost_ratio 1.168×) and **371.4 s / 390.2 s** (null:
incumbent/mutant, cost_ratio 1.051×) — **1,589.2 s (≈ 26.5 CPU-minutes) total for all four**, both ratios
comfortably under the 1.2× cost bar on their own (the planted-bad mutant was refused on its measured Q1
regression, not on cost). The worker process's own accumulated CPU time at exit (`ps`'s `TIME` column) was
**≈ 55 minutes on one core**, measured under real contention from four other builders' parallel test
suites/lives on the same box (`nice -n 10` throughout, per the rules) — so the SHADOW's own build-up
(birth → the T−2 h checkpoint, 37,100 rows of real 32×32 eye rows through the sealed CNN tower,
ACT/OUTCOME reflexes, SIT, THINK) accounted for the remaining **≈ 28.5 minutes**, the dominant cost, as
item 6 above already named: the O(organism-size) scaling this codebase already carries elsewhere
(auto-snapshot compression every `SNAPSHOT_EVERY=500` moments on a genuinely large, ~2000-cell organism;
THINK-side O(cells)-ish work) means a shadow that must replay a WHOLE life from birth gets more expensive
as that life gets older — a fresh 1,000-3,000-row timing probe on the SAME genome (169/138 rows/sec) badly
under-estimated the full run for exactly this reason (item 6's own finding). `shadow_lag_rows` reads `None`
on these two JSON files specifically — they were produced by a process already running (started ≈00:52)
before that field's own code landed (≈01:56); it is unit-tested (`tests/tools/test_evolve_worker.py`) and
present on every proposal a freshly-started worker produces from here on, but not on this one historical
artifact, said here rather than silently reformatted to look like it was there all along. **Peak RSS**
(`ps`'s own `RSS` column, sampled repeatedly through the run, not a peak-memory profiler): the worker
process — shadow + one twin at a time, per brief item 2's own "never in parallel" — reached **≈ 681 MB**
at its highest observed sample (during round 902's mutant twin, the largest organism this run ever built).
Against PREREG §5 GROW's own box-total projection ("mind + EVOLVE's shadow + one twin ≤ 20 GB"), that
reading is for the SHADOW alone at seam-1's own (non-EVOLVE, un-grown) scale; the live MIND process and a
genuinely GROW-unbounded organism at 24 h scale are each a separate, larger budget line the pre-flight
projection in PREREG §8 step 5 will need to size on its own — this number is one data point toward it, not
a substitute for that projection.

**The result is unambiguous.** `q1_seen_start` (measured once, on the checkpoint, before either twin runs)
was **0.9727** for both rounds — confirming the retention finding above (identical by construction). The
INCUMBENT held that same 0.9727 after replaying the real slice in BOTH rounds (a faithful continuation).
The PLANTED-BAD mutant (`theta_n` moved from 0.952 to 0.5, deliberately outside BOUNDS' own [0.85, 0.99]
band) collapsed Q1 to **0.6727** — a 30-point drop, cleanly REFUSED on a measured regression, not merely
"no improvement" (unlike the smaller synthetic tapes in the unit suite, where the same plant sometimes only
manages "no improvement" within a short synthetic slice — this seam-1-scale run is the one that matters for
the record, and it shows the bar catching a REAL, large, unambiguous act of harm). The NULL mutant (`lr`
moved one step, 0.05 → 0.051) changed nothing measurable — REFUSED for lack of any improvement, exactly the
"a value moved by one step inside the noise" case the brief names. Both readings are printed regardless of
verdict (brief's own instruction, and advisor's point 7: a PASS here would be a finding about the bar,
never a reason to loosen it — reported honestly, not routed around); here both are REFUSED, cleanly, for
exactly the reasons the mechanism exists to catch.

## The mechanism, in one paragraph

`creature/genes.py:BOUNDS` (15 mutable gene values, each with `[lo,hi]`+decimals and a text-substitution
regex anchored on a stable prefix so an unrelated trailing clause — THINK's threading tail, a future BUDGET
regen clause — survives untouched) + `draw_mutation`/`apply_mutation`/`mutate_genome_text` (deterministic
on `(SEED, epoch, proposal_no)`). `tools/evolve.py` (the worker, a SUBPROCESS like the game worker) keeps a
SHADOW `Mind` that just consumes the live tape continuously — including its own "proposal" rows — so it
self-adopts the SAME sequence of epochs the live mind does, with NO separate bookkeeping; `shadow.
genome_text`/`shadow.evolve_epoch` at any moment are therefore always the correct incumbent to mutate FROM
(the advisor's blind spot #2: a second round must never mutate from the birth genome again). Every 2 h of
TAPE time it checkpoints (a copy of state, never the live root); every `EVOLVE.every_h` it finds the
checkpoint nearest `now − judge_h`, replays INCUMBENT and ONE MUTANT over the real tape slice in fresh
scratch roots, grades both with `tools/verdict_life.py`'s own `surprise_mark`/`sentence_mark`/`act_mark`
plus `tools/self_exam.py`'s own Q1 machinery (never re-implemented), and applies the regression bar (no
mark regresses, ≥ 1 clears its declared margin, cost ≤ 1.2×). `creature/senses/evolve.py`'s sense thread
republishes `PROPOSAL-<n>.json` onto the tape (a DISK-persisted cursor — unlike `sit.py`'s in-memory one, a
duplicate publish here would let the SAME mutation adopt twice as two epochs). `creature/mind.py`'s
`_consume_proposal`/`_maybe_adopt_evolve_proposal` adopt a PASS proposal at the next SLEEP boundary: the
mutant text is written to `GENOME.v<n>.genome`, `self.genome`/`self.org.g` are re-parsed (safe by
construction — BOUNDS excludes every shape-changing gene), `genome/park.py`'s `Park.n` and
`genome/curiosity.py`'s `Interests.n` are live-patched (the two mutable genes cached at construction rather
than read live — checked against their source, not assumed), and the epoch is journaled as a nested-key
MIND row (never a top-level `"event"` key, so it stays visible to `creature.replay`'s own byte-identity
machinery). `Mind.resume` is epoch-aware (`_latest_evolved_genome`) so a process restart rebuilds from the
LATEST adopted genome, never silently reverting to birth values. `creature/body.py:Body._build_status`
exports `evolve_epoch`/`evolve_proposals_seen` on every STATUS write (#164), 0 on a genome that never
declares EVOLVE.

## Commit

`da0464cf090a8ed386bb626d88e8c5f4ffdb5243` — the mechanism, all code, all tests, the negative control
machinery, the initial numbers.
`68f0e9fa772b023df035c7d0f7f2b9bb288c615b` — the advisor-review follow-up (`shadow_lag_rows`, the two
structural bar-limit findings, the corrected/re-verified full-suite count).
Both on branch `alpha4-evolve`, off master `74c661d`.
