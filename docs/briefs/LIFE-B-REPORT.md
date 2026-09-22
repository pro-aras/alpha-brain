# Builder B report — THE EYE: SURPRISE (L-4) + the coarse whole-canvas glance (L-7)
*Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:3x +0400. Brief: `docs/briefs/LIFE-B-SURPRISE-COARSE.md`. Worktree `/data/dev/genome-wt-s`, branch `life-eye` (created off g5-integration `aed56d5`).*

## 0 · What landed, with file:line

- **`genome/machinery.py`**
  - GAZE's fullmatch gains an optional trailing `` coarse (<int>)`` clause (:213-221 in the edited file; stored as `g["gaze"]["coarse"]`, absent otherwise — byte-identical when undeclared).
  - SURPRISE's fullmatch gains an optional trailing `` predicted (mind-cell)`` literal (`"mind-cell"` is the ONLY accepted value; stored as `g["declared"]["SURPRISE"]["predicted"]`, absent otherwise — byte-identical to the old `{"floor": f}` shape when undeclared).
  - `Organism.expected_sight(xw) -> Optional[np.ndarray]` (new method, beside `_answer_of`): the word's best-lit cell's largest-edge sight cell, masked by `self.sight.alive` explicitly. Read-only, never births.
  - `Organism._resonate(area, x, confirm=False)`: `confirm=True` refuses the would-be novelty birth, counting it on the plain attribute `self.births_skipped_confirmed` (kept OUT of `self.c`/`state_hash()`, the same reasoning as the existing `moments_sight_only` attribute — a new `self.c` key would move every genome's hash even at value 0).
  - `Organism.moment(x_s, x_w, lr_scale=1.0, confirm=False)`: `confirm=True` runs HEBB/DELTA only — MISFIRE/PRUNE/MERGE are skipped whole (the brief's own words: "a cheap moment: HEBB/DELTA only, no birth"). Default `False` on every existing call site — byte-identical.
- **`genome/gaze.py`**: `_one_glance_vector(rgb, spec, size, ink_rule, colour)` (new, shared helper — the exact `mode="one"` derivation, used by BOTH the `mode="one"` branch and the coarse feature, so they are byte-identical by construction, never two derivations of the formula). `_residual(v, predicted)` = `1 - dot(v, predicted)` (both unit vectors), `None` when `predicted is None`. `glances()` gains `predicted=None` (returns a `"residual"` list parallel to `"feats"`) and, when `gaze.get("coarse")` is set, appends a fifth feature (the coarse vector) to `"feats"`/`"residual"` — **never** to `"fix"`/`"windows"` (which stay the four located glances). `predicted` is **never** forwarded into `gaze_sequence`'s own `predicted=` argument (that would move fixation SELECTION — G-EYE-5's "other form", explicitly declared out of scope by the brief).
- **`creature/genes.py`**: `RUNS["mind"]["SURPRISE"]` now names a real call site (was `unwired` — LIFE.genome would have refused to start on `SURPRISE floor 0.05 predicted mind-cell` otherwise, per W3-0's generic refusal).
- **`creature/mind.py`** (`Mind.__init__`, `_consume_eye`, `_coarse_row`, `_think_pool`):
  - `word`/`xw` computation moved above the `gaze.glances()` call (PREREG §2.2's order law makes this safe — the ear row always precedes the eye row of the same moment).
  - `predicted = self.org.expected_sight(xw) if surprise_gene is not None else None`, passed into `gaze.glances(..., predicted=predicted)`.
  - `--blind coarse` strips the coarse feature from `g["feats"]`/`g["residual"]` BEFORE `org_feats`/`residuals` are built (so the mind's own learning road sees exactly 4 feats — the fifth row is genuinely dropped, not just unjournaled).
  - `floor = -1.0 if "surprise" in self.blind else float(surprise_gene["floor"])`; `confirmed_flags[i] = floor is not None and residuals[i] is not None and residuals[i] < floor`.
  - `org.moment(x, xw, lr_scale=lr_scale, confirm=confirmed_flags[i])` inside the word-bearing loop.
  - `glances_confirmed`/`glances_surprised` (new Mind ints, incremented per glance) — `graded = residual is not None`; `surprised = graded and not confirmed`.
  - The main journal row gains `"residual"`/`"confirmed"` (sliced to the 4 located glances, gated on `surprise_gene is not None`) on BOTH the word-bearing and sight-only branches.
  - `_coarse_row()` (new method): a SECOND journal row sharing the triggering canvas's own `seq` (SLEEP's own pattern) — `{"act": "coarse", "glance": <last index>, "fix": None, "windows": None, "hash": ..., **residual/confirmed if SURPRISE declared}`. `None` (nothing written) when coarse is undeclared or blind to it.
  - `_confirmed_episodes: set` — an episode id is added when glance 0 (the one FAST's episode is built from) was CONFIRMED; `_think_pool()`'s two FAST-episode loops (`kind: "word"` and `kind: "sight"`) skip any episode id in this set — "no think-pool item" for a CONFIRMED glance.
  - `Mind.__init__` refuses `BIND` declared together with `SURPRISE` or GAZE's `coarse` clause, by name (W3-0's own law: a combination the machinery does not run refuses).
- **`creature/body.py`** (`_build_status`): `glances_confirmed`, `glances_surprised`, `births_skipped_confirmed` on every STATUS write.
- **`tools/verdict_g4.py`**: `BLINDS` gains `"coarse"` and `"surprise"`.
- **`genome/run_g1.py`** (`live()`'s `feed()`, :92-103) — **the one real chain bug found and fixed**, see §2.
- Fixture/test-scaffolding fixes forced by the new `predicted=` keyword: `tests/creature/test_g5i_seam_deliver_moment.py`'s `leaky_glances` wrapper now takes `**kw` (was a fixed 5-arg signature — TypeError under the merged tree, SOLUTIONS #235's own class, exactly as it happened once before for `colour=`); `tests/creature/test_refusal.py`'s `SAMPLE_LINE` gains a `SURPRISE` row (its own gate, `test_sample_line_set_is_exactly_the_registry`, caught the omission on the first full-suite run).

## 1 · The chain (#235) — every `gaze.glances(`/`glance_rows(`/`glance_held(` caller, and what was done

| caller | file:line | effect of the 5th (coarse) feature | action |
|---|---|---|---|
| `Mind._consume_eye` | `creature/mind.py:375` | the seam itself | wired (L-4/L-7) |
| `glance_rows` | `genome/run_g1.py:61` | `feats` len 5, `fix` len 4, stored as separate tuple fields | safe (never zips them) |
| `glance_held` | `genome/run_g1.py:67` | same | safe |
| `first_glance_feats` | `genome/run_g1.py:214` | takes `feats[0]` only | safe, unaffected |
| **`live()`'s `feed()`** | `genome/run_g1.py:92-96` (pre-fix) | `for k, x in enumerate(feats): ... fix[k]` — `k=4` (coarse) had no `fix[4]` | **CRASHED: `IndexError: list index out of range`, reproduced RED, then FIXED** (guarded `k < len(fix)`; the coarse glance is excluded from `moment_on`'s on/off-thing bookkeeping, never guessed) |
| `landing()` | `genome/run_g1.py:137-145` | only reads `fix[:first]`, never `feats` | safe |
| `glance_picture` | `genome/ask.py:54` | returns the whole `feats` list, consumed by `recall_many`/`edge_many` | safe |
| `ask_glances`/`ask_plant_glances`/`build_ledgers` | `genome/questions.py` | consume `feats` lists via `recall_many`, never index against `fix` | safe |
| a training tool | `genome/train_eye.py:320` | `feats[0]` only, and forwards neither `colour=` nor `predicted=` (a pre-existing gap — the same one G5 builder J's colour report named and left; this tool is off the mind's road) | safe, noted, not fixed (out of scope) |
| `tools/self_exam.py`, `tools/verdict_g4.py:287-291` (`own_asks`), `tools/diag_g1.py` | via `glance_held`/`feats_only` | `feats_only()` strips to `List[List[np.ndarray]]`, no `fix` pairing at all | safe |
| `tools/pin_g1.py:49-50` | `fix[0]` only | safe |
| test files (`_creature_front.py`, `test_bind_colour.py`, `test_verdict_twins_g5.py`, `test_traits.py`, `test_g5i_seam_deliver_moment.py`, `test_verdict_twins_g5.py`'s negative-control lambda) | — | one required a `**kw` fix (above); the rest call `gaze.glances()` directly and never build a stale-signature wrapper | one fixed, rest safe |

**The one real bug: `genome/run_g1.py`'s `feed()`.** Reproduced RED first (`python3 -c "..."` — see transcript; `IndexError: list index out of range` on the very first coarse-declaring genome fed through `run_g1.live()`), then fixed and reproduced GREEN (`tests/creature/test_surprise_coarse.py::TestRunG1ChainCoarse`, both tests green — see §4). This gate (`run_g1.live` vs the mind) is the estate's own G4-2 parity check; it would have crashed the moment anyone ran it against a coarse-declaring genome (LIFE.genome declares coarse).

## 2 · Tests, RED→GREEN — honest account

Test-first was followed where the mechanism's shape was already settled by the brief (the parser clauses, the `--blind` gating, the BIND refusal, the run_g1.py chain bug). For SURPRISE's own toy, the brief's literal expectation ("the second showing's glances all confirmed") does **not** survive contact with the single-x̂-per-canvas definition it also specifies (§3) — this was caught by `advisor()` BEFORE the toy was written, not discovered by a failing assertion; building the toy to the brief's own optimistic prose would have produced a test asserting something false. The toys below were then written to measure and print the REAL numbers, run, and iterated (mostly on tape LENGTH — `STAGE 2 meet moments 200..` means HEBB never fires under 200 org.t moments, so several early toy tapes silently measured "before wiring" and had to be lengthened) rather than on a wrong mechanism.

Genuine RED reproduced and quoted:
```
$ python3 -c "... run_g1.live(g, dev, [], [], ['circle','square'], [], {}, 'never')"
Traceback (most recent call last):
  File ".../genome/run_g1.py", line 96, in feed
    moment_on[org.t] = on_thing(fix[k], truth["cell"])
                                 ~~~^^^
IndexError: list index out of range
```
→ fixed → GREEN: `TestRunG1ChainCoarse` (2/2 pass).

A second genuine RED, caught by `advisor()` on review rather than found independently (§6 clause 8): once `RUNS["mind"]["SURPRISE"]` names a real call site, the BARE `SURPRISE floor <f>` form (no `predicted mind-cell`) stops refusing at `Mind.__init__` and silently runs this brief's mechanism instead — reversing W3-0's own pre-existing refusal for that exact line. The fix (`creature/mind.py`, beside the BIND checks) was written first; the new test was then verified RED by temporarily disabling the fix and re-running it alone:
```
$ python3 -m unittest tests.creature.test_surprise_coarse.TestSurpriseParses.test_old_form_refuses_at_mind_start -v
FAIL: test_old_form_refuses_at_mind_start
AssertionError: GenomeError not raised
```
→ fix restored (diffed byte-identical to the pre-check version) → GREEN.

All 26 tests in `tests/creature/test_surprise_coarse.py`: **green** (final full-file run: `Ran 26 tests ... OK`, life3a test included; individually every class was also run in isolation to green during development). Full suites on the FINAL bytes:
- `tests/genome` (unaffected by my creature/-side edits, run to confirm `genome/run_g1.py`'s fix didn't move any existing pin): `Ran 221 tests in 63.067s` / `OK (skipped=1, expected failures=6)`.
- `tests/creature` (includes my new file + the two scaffolding fixes): **quoted in §7 below** — launched with `-t .`, final log at `scratch/creature_suite_final2.log` (286 tests, after the bare-SURPRISE-form fix and its new test).

## 3 · The toy's numbers

**Repeated canvas (task 2's first clause), 50 identical showings of "circle":** at steady state (the 50th showing), located-glance residual `[0.0, 0.0056, 0.1556, 0.0857]`, confirmed `[True, True, False, False]` — **2 of 4 confirm**, not "all 4" (the brief's prose). Mechanism, measured not guessed: x̂ is ONE vector per canvas (the word's single best-edge sight cell); the four located glances land on up to 4 distinct sight cells (F's own diagnostic, SOLUTIONS #228's family); at most the glances whose window matches x̂'s own location can have residual under the 0.05 floor. On the STATUS-counter toy (`TestStatusCounters`, a separate repeated tape — "key" × 50, seed 31, read through `Body._build_status()`): `glances_confirmed=17`, `glances_surprised=53`, `births_skipped_confirmed=0` — both surfaced on STATUS and asserted equal to the mind's own attributes, `glances_confirmed` asserted `>0`.

**Corrupted block (a 16×16 block inverted on the thing, at the truth file's own top/left — `test_replay.py`'s own corruption pattern), "square" shown 40 times then once corrupted:** ALL 4 located glances of this run landed on/near the block. Before: residual `[0.0, 0.0007, ~0, 0.0641]`, confirmed `[True, True, True, False]`. After the corruption: residual `[0.0837, 0.0937, 0.1079, 0.0955]`, confirmed `[False, False, False, False]` — every fixation that was confirmed flips to surprised. Clean, unambiguous demonstration.

**Shuffled-expectation twin (x̂ = a random alive sight cell instead of the real best-edge one), "triangle" × 50 showings:** real confirmed rate **0.800**, shuffled-expectation rate **0.469** — a real, sizeable gap (not exact-chance because "confirms" here also includes genuinely-similar-by-accident cells on a front where THETA_N=0.955 already means most cell pairs are far apart; the separation is the point, not a specific number).

**L1's real closed tape (8h+ ladder rung, `/data/dev/genome-lives/g5-ladder-L1`, read-only, symlinked payload, 16,653 tape rows / 8,327 canvases), replayed under a SURPRISE-added copy of L1's own genome — the pre-flight's number, 297.0s to replay:**
- `glances_confirmed=17552`, `glances_surprised=15448`, **overall confirmed share = 0.532**.
- `births_skipped_confirmed=9` (small — the mind is rarely AT a would-be-novelty-birth moment exactly when it is also confirmed; the two conditions are largely disjoint by construction, which is the expected, not-worrying, shape).
- Confirmed share per 500-canvas window ranges **0.470 (window 2, early) → 0.593 (window 5) → 0.566 (the tail)** — rising as the organism accumulates word→sight-cell edges, never collapsing to 0 or 1. Full series in `scratch/preflight/l1_surprise_windows.json` (not committed — a scratch artifact; the numbers above are the ones that matter).
- This is the CONFIRM mechanism's ceiling reading on a real, unmodified closed life — no bar was declared for it in this brief (the mark itself, per L-4's plan text, is "the confirmed share rises across each window and drops at every arrival" — the windowing above is coarser than per-arrival; a per-arrival re-read is a natural next step, raised, not built, since L-4's own mark text asks for the SPIKE/SETTLE shape at arrivals specifically, which needs `org.arrivals` boundaries, not a fixed canvas step — see §5).

## 4 · The exam's Q1, with and without coarse (task 1's pre-flight)

Two live 6-minute `creature.body` runs from the SAME wall-clock start, same maker/folder settings, on `genome/G5.genome` + `` coarse 32`` vs plain `genome/G5.genome` (never `genome/LIFE.genome`, whose other DRAFT lines are not yet landed and would refuse to start — the advisor's own catch):
```
python3 -m creature.body --root <tmp> --genome <copy> --plant-after 5000 --folder /data/dev/genome/world
```
Both ran the full 6 minutes, stopped cleanly (`crash: null`, 2 snapshots each), fed the identical `tape_rows=311`. **Moments confirm the mechanism end-to-end on a live run**: coarse 625 moments vs plain 500 — exactly 625/5 = 500/4 = 125 canvases, the 25% rise L-7 predicts, to the count. The coarse root's journal carries exactly 125 `act: "coarse"` rows (one per canvas), each `glance: 4, fix: null, windows: null`, none carrying `residual`/`confirmed` (SURPRISE undeclared on this genome — gated correctly).

`tools/self_exam.py --held 10 --check-tape 400` on a hard-link copy (`cp -al`) of each root:

| | coarse | plain (no coarse) | Δ |
|---|---|---|---|
| Q1 (seen words, n=110) | 0.709 | 0.845 | **−0.136** |
| Q1 (all 16 words, n=160) | 0.4875 | 0.5813 | −0.094 |
| sight/word cells | 138 / 14 | 106 / 14 | +32 sight cells |
| `disjoint_control_caught` / `organism_hash_unchanged_by_exam` | true / true | true / true | both exams ran cleanly |

**Honest reading, not spun:** on this 6-minute smoke coarse reads WORSE, opposite to G-EYE-6's own prediction (Q1 ≥ 0.975, beside the "one-glance twin already reads 0.819" ceiling). This is NOT evidence the mechanism is wrong — it is evidence a 125-canvas, 110-question smoke is far too short/small to read the mark at all: coarse produces 32 MORE sight cells in the same wall-clock window (a 5th moment a canvas is a 5th chance to birth), and more, younger cells with fewer showings each is exactly the shape that lowers held-out recall on ANY front, coarse or not, before the edges have had time to settle (life 1's own early-window numbers above, 0.47 rising to 0.53-0.59, show the same settling-in shape over thousands of canvases — 125 is a rounding error against that). **The mark this brief owes is a 24h-scale reading, not this smoke's; this smoke only proves the plumbing is correct** (moment counts, journal shape, no crash) — reported as such, not overclaimed either direction.

## 5 · Task 3 — the cadence re-base

Traced from the code, not assumed (the advisor's initial guess about FAST was wrong and is corrected here):
- **`SNAPSHOT_EVERY = 500`** (`creature/mind.py:88`) IS moment-denominated (`self.org.t - self._last_snapshot_moments >= SNAPSHOT_EVERY`) — under coarse, moments advance 5/canvas instead of 4, so a snapshot now fires every 500/5=100 canvases instead of 500/4=125 — **20% MORE FREQUENT** snapshots (a wall-clock/IO cost, never a correctness issue — atomic npz+json writes, just more of them). **This constant needs the same re-base LIFE.genome's own SLEEP/SCALE lines already got** (2000→2500, 1000→1250, both exactly ×5/4) — it has no genome knob today; either add one or accept the extra snapshot frequency. Raised, not built (not this brief's file to add a gene for).
- **`FAST episodes 20000`** — genome-declared, NOT a code constant, and NOT moment-denominated in its actual fill rate: `Episodes.write(...)` is called exactly **once per CANVAS** (using `f0`, glance 0's feature) regardless of how many glances/moments that canvas has — traced at `creature/mind.py`'s `ep_id = self.episodes.write(...)` call sites (both branches). Coarse adds a 5th MOMENT but not a 5th FAST write. **Does not need re-basing.**
- **`EXAM every <n> canvases`** — declared in canvases already, unaffected by moments/canvas. **Does not need re-basing.**

## 6 · Clauses raised, never worked around

1. **SURPRISE's toy prose ("all confirmed") vs the single-x̂ definition it also specifies** — built exactly as specified (one expectation vector per canvas), measured honestly (2/4 confirm at steady state, not 4/4), NOT switched to a per-glance-x̂ alternative (that is a PREREG change, not this builder's call). The alternative — x̂ per glance, the nearest of the word's edge-bearing cells — is named as the fix if "all confirmed" is truly wanted; not built.
2. **"No think-pool item"** — built as the additive, narrow form (`_confirmed_episodes` excludes an episode id from `_think_pool()`'s two loops). The wider form (skip the FAST *write* itself for a confirmed glance 0) was considered and NOT built: it would also change SLEEP's `most_surprising()` ranking, the `episodic` PREDICT arm's episode-nearest comparison, and the `"ep"` field on the journal row — three mechanisms this brief does not own.
3. **Resume/crash-restart persistence** of `glances_confirmed`/`glances_surprised`/`_confirmed_episodes`/`births_skipped_confirmed` — NOT persisted in `snapshot()`/`ledger.json`. Matches the EXISTING, already-accepted gap shared by `_induce_pending`/`_deduce_pending`/`_filed_predictions`/`Park`/`Interests` (their own `__init__` comments say so). Replay (this estate's main verification road) builds a fresh `Mind` every time, so this gap does not affect any replay-identity claim in this report; it WOULD reset these four counters/sets across a live crash-restart. Raised, not built.
4. **Coarse's size is constrained to the RETINA tower's fixed input side (32 for `tower:eye-tower-g2`)** — `retina()`'s tower step asserts its input is exactly `t.side × t.side` (`genome/machinery.py:496`), so `coarse 16` on this front refuses with an `AssertionError`, not a `GenomeError` (a real, if narrow, gap: a malformed `coarse` value should refuse with a genome-level message naming the size mismatch BEFORE the first canvas, not an assertion mid-run on the first glance). Every G-EYE-6 genome line on disk declares `coarse 32` beside `glance 32` for exactly this reason. Raised (a pre-flight check for `coarse == glance` when the front is a fixed-size tower would be a clean, small addition); not built (out of this brief's stated scope, and the live genome never exercises the mismatch).
5. **`genome/train_eye.py:320`** forwards neither `colour=` nor `predicted=` to `gaze.glances()` — a training tool off the mind's road, reads `feats[0]` only, so it is UNAFFECTED by coarse (never crashes) but would silently never see a coarse-informed residual if it were ever extended to care about SURPRISE. Noted, not touched (pre-existing gap, not introduced by this brief).
6. **Life 3a's own recorded journal no longer replays byte-identical on this box** (`/data/dev/genome/run-g4-life3a-20260921-1314`, 4,675 tape rows / 2,576 mind rows both sides) — verified this is **PRE-EXISTING and unrelated to this brief**: `git stash` + a fresh replay of the SAME tape under the PRISTINE (pre-this-brief) code reproduces the IDENTICAL divergence; a second check — this branch's code vs the pristine code, same tape, same genome text (life 3a's own saved `state/organism.json:genome_text`) — replays BYTE-IDENTICAL to each other (`diff=None`). Named precisely, per a full field-by-field diff (not just the first divergence `compare()` reports), grouped by seq: exactly **two** fields ever differ, nothing else —
   - `hash` — diverges at 2,343 of 2,576 seqs, first seq **2**, last seq 4,675. This is the DECLARED volatile field (PREREG §19/L-1): a per-write content hash of organism state that a genuine cross-version/cross-run drift (weights, thetas, numpy version — none investigated) would move on nearly every row, which is exactly the 91%-of-rows shape measured. Expected, not a divergence in the load-bearing sense.
   - `think` — diverges too, and NOT trivially: of the 233 seqs where BOTH sides carry a `"think"` row (present/absent always agrees — 0 seq has it on one side only), **213 have a different sub-value**. First differing seq **140**. Sub-key breakdown across those 213: `item` differs 213/213 (always — a different word/rule was chosen to think about), `kind` differs 175/213, `outcome` differs 174/213, `parked` differs 2/213. Example at seq 140: this branch's replay picks `{"item": "arrow", "kind": "word", "outcome": "belief", "parked": false}`, life 3a's own record has `{"item": "bar", "kind": "word", "outcome": "belief", "parked": false}` — a different item entirely, not a rounding difference. This is a REAL behavioural divergence, not a declared-volatile field, and it is NOT this brief's introduction (proven by the same stash A/B: pristine code reproduces it identically, since pristine and modified code are byte-identical to each other on this tape). Most likely downstream of whatever causes `hash` to drift — a different eye-tower/theta/numpy state changes which cells get born and wired at each step, which changes which items are even IN the think pool at a given seq — but this is inference, not verified; the actual root cause is still one of the three candidates named below, unconfirmed.
   
   So: this box's drift from life 3a's own historical record is a SEPARATE, pre-existing finding (SOLUTIONS #229's family — the eye tower weights, gate-G-a's written thetas, or a numpy/Python version, none investigated), raised for whoever owns pin discipline, not fixed here (out of scope, and fixing it would mean editing something this brief does not own without knowing which of the three candidate causes is real) — but it is now precisely characterized rather than summarized as "diverges at seq 2:hash", since the `think` divergence is the more consequential of the two and starts substantially later (seq 140, not seq 2).
7. **`genome/run_g1.py`'s `feed()` IndexError** — this one WAS fixed (§1/§2), since it falls squarely inside "grep every `gaze.glances(`/`glance_rows(` caller … and list them" and the fix is a one-line guard with no other consequence (verified: the no-coarse road is byte-identical, `TestRunG1ChainCoarse::test_no_coarse_byte_identical_to_before`).
8. **The bare `SURPRISE floor <f>` form silently changed behaviour once `RUNS["mind"]["SURPRISE"]` named a real call site** (advisor-caught, not self-found): `genes_module.unwired()` only flags a declared gene with NO row in `RUNS` — it no longer distinguished "the mechanism form" from "the bare form G5.genome's own comment reserves for a different, never-built rule" (a per-sense publish gate, "a sense publishes when `|actual − predicted| > floor`"). Before this brief, the bare form correctly refused (W3-0, declared-but-unwired). Fixed: `Mind.__init__` now refuses the bare form by name explicitly (`creature/mind.py`, beside the BIND checks) — `SURPRISE` only runs when `predicted == "mind-cell"`; the bare form's refusal-by-name behaviour is restored, new test `TestSurpriseParses::test_old_form_refuses_at_mind_start`.
9. **The exam road honours no `--blind` flag today, coarse included** (verified by precedent, not newly discovered here — `tools/verdict_g4.py`'s own worker always re-parses the genome fresh for the exam subprocess regardless of the mind's `blind` set, PREREG-noted in this file's earlier draft): a life run under `--blind coarse` LEARNS on 4 features per canvas but is ASKED on the exam's own fresh, unblinded parse of the same genome — which, if that genome declares `coarse 32`, means the exam's own `self_exam`/`ask` road would compute a 5-feature glance set for a mind that only ever wired 4. Traced precisely: `worker()` (`tools/verdict_g4.py:166-219`) builds `Mind(genome_path, root, blind=frozenset(spec.get("blind", [])))` — the mind's own road correctly honours `blind`. But its ASKING road either shells out (`subprocess.run([..., "self_exam.py", "--root", ..., "--genome", ...])`, line ~217 — `self_exam.py` has no `--blind` argument at all, confirmed by reading its `argparse` block) or, only when `spec.get("one_glance")`, runs `self_exam.py`'s `main()` IN-PROCESS after monkeypatching `gaze.glances` (`_force_one_glance()`, line 149-153) — the one existing precedent for making the asking road see what the learning road saw. `own_asks()` (line 285) has the identical gap: it calls `run_g1.glance_held(held, g, "surprise")` directly on the genome's own declared GAZE dict, with no blind-awareness at all.
   **The fix I would make, left unmade (the reader is the orchestrator's, not this brief's file):** add a `_force_no_coarse()` twin of `_force_one_glance()` — a `gaze.glances` monkeypatch that drops the 5th feature/residual from its return dict, exactly mirroring what `Mind._consume_eye` already does for the learning road — and in `worker()`, widen the in-process branch's condition from `if spec.get("one_glance"):` to `if spec.get("one_glance") or "coarse" in spec.get("blind", []):` (calling `_force_no_coarse()` in the coarse-only case), since the monkeypatch only reaches code running in the SAME interpreter — the current `subprocess.run(...)` branch spawns a fresh process the parent's monkeypatch cannot touch, so routing the coarse-blind case through the existing in-process call (as `one_glance` already does) is required, not optional. `own_asks()` would need the same monkeypatch active around its own `run_g1.glance_held()` call. Not built: this is consistent with the estate's existing shape (every other `--blind` gene has the same asymmetry today, not something this brief's two genes introduced), and it is the reader's file to change, not this one. Until it is, a `--blind coarse` verdict must be read as "learned-without, asked-with," never as "coarse never existed" for that life.

## 7 · Suites on the final bytes

```
$ cd /data/dev/genome-wt-s && export TMPDIR=$PWD/scratch/tmp
$ python3 -m unittest discover -s tests/genome -t .
Ran 221 tests in 63.067s
OK (skipped=1, expected failures=6)

$ python3 -m unittest discover -s tests/creature -t .
Ran 286 tests in 403.235s
OK (skipped=1)
```
(genome suite log: `scratch/genome_suite_final.log`; creature suite log: `scratch/creature_suite_final2.log`, both under this worktree's own scratch/, not committed. Both are re-runs launched AFTER the advisor-caught `SURPRISE` bare-form refusal fix — §6 clause 8 — and its new test landed, so `Ran 286` is the true final creature count (25 → 26 tests in `test_surprise_coarse.py`, +1 for the new pin, everything else in the suite unmoved) and `Ran 221` on the genome side is unmoved from the earlier run, confirming that fix touched no `tests/genome`-visible behaviour. An earlier, now-superseded creature run reading `Ran 285 tests in 407.447s` remains on disk at `scratch/creature_suite_final.log` as a record but is not quoted as final.)

## 8 · date stamps

Advisor caught a SOLUTIONS #50 drift: `genome/machinery.py` and `genome/gaze.py` (the first two files touched, right after this session's own `date` calls read `18:34`/`18:36` +0400) carried `19:0x` stamps in their edit comments — typed ahead of the clock, not read from `date` at write time. Fixed: `sed -i 's/2026-09-22 19:0x/2026-09-22 18:3x/g'` on both files. A second drift of the same shape was caught mid-fix (the advisor-caught SURPRISE bare-form refusal, §6 clause 8, was itself stamped `20:0x` when `date` read `19:33` at write time) and fixed the same way, `20:0x` → `19:3x`.

Verified against the bytes on disk, not from memory — `grep -h "LIFE builder B" <the 12 edited/new files> | grep -oE "2026-09-22 [0-9]+:[0-9x]+[-0-9x:]* \+0400" | sort | uniq -c`:
```
      7 2026-09-22 18:3x +0400
     13 2026-09-22 19:0x +0400
      1 2026-09-22 19:0x-19:3x +0400
      2 2026-09-22 19:3x +0400
```
Every one of these is ≤ a real `date` call made during this session (18:34, 18:36, …, 19:26, 19:33) — none ahead of the clock.

## 9 · Commit

Final commit sha: **filled in after `git commit`, see the handback message**.
