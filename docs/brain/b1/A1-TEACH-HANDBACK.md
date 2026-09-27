# A1-TEACH — hand-back (R46)

edit: Claude (Sonnet 5, A1-TEACH builder), 2026-09-27 14:17 +0400 — built per `docs/dev/briefs/a1-teach.md` in worktree
`/data/dev/genome-wt-b1-teach` (branch `b1-a1teach`, from `b1-integration` 691f41a). Law: `docs/brain/b1/SEAT-DECISIONS.md`
R46 (2026-09-27 13:33 +0400) and `docs/brain/B1-PREREG.md` §4 row A1 / §12's 2026-09-27 13:33 line. Final commit of this
work: **5202613**.

## What changed

**`brain/arms/soft/arm.py`**
- `__init__` (line 124-129): `self.teach_trains_answer = bool(self.config.get("teach_trains_answer", False))`; if True
  together with `variant in ("A1-ATT", "A1-MA")`, raises `ValueError` at construction (item 5 — the switch is only for
  the non-attention variants, a declared limit named in the error).
- `_fit_teach` (line 338, 350-351): `h_before = self.h.detach().clone() if self.teach_trains_answer else None` captured
  at the very start, before anything advances (guarded — with the switch False this line does not run); A1's own TEACH
  handling (hear x; `_advance_steps`; ring append) is completely unchanged; then, guarded, `self._teach_answer_step(row["payload"], h_before)`.
- `_teach_answer_step` (new method, line 353 onward): builds the NAME ask's own payload
  `{"answer_kind": "NAME", "candidate_rows": None, "cues": ["NAME"], "operands": [op_row(g)]}`, runs its `ask_steps`
  with `self.engine.step` from `h_before` (NOT under `torch.no_grad()` — the loss needs a live graph), reads
  `active_h = self.engine.active` AFTER step 2 (so a mid-row birth is reflected), computes
  `logits = self.names(h, active_h=active_h)`, `loss = F.cross_entropy(logits.unsqueeze(0), torch.tensor([target_idx]))`,
  and dispatches to `self.local_trainer.step(loss, valence=1.0)` (awake_mode "local") or `self.bptt_trainer.step(loss)`
  (else) — exactly `_fit_feedback`'s own dispatch. Touches no abstention history, `_pending`, or `_ring`.
- Import line: added `op_row` from `brain.protocol`.
- Module docstring: new `D21` design-decision paragraph (line 46-51) documenting that the switch reuses `_fit_feedback`'s
  trainer dispatch rather than a new primitive, and that the shared eligibility-trace buffer therefore also touches
  engine/world/yesno/pick parameters, not only the NAME head's — declared, not hidden.
- **The growth edge case (item 4):** no widening code was needed. Verified by reading `engine.py`:
  `GrowingGRUEngine.step` (engine.py:299-312) always returns an hmax-wide tensor (the tail beyond `active` is the
  unborn units' zero padding), and `self.h`/`h_before` are built from `engine.zero_state()` (also hmax-wide) from
  construction — so `h_before` is already the right width for whatever `active` becomes mid-row. Pinned by
  `TestA1TeachGrowth.test_birth_during_a_teach_row_does_not_crash_and_still_trains`.

**`brain/harness/run.py`** (line 82-86): registry entry
`"A1-TEACH": ArmSpec("A1-TEACH", "brain.arms.soft.arm", "ArmA1", {"variant": "A1", "teach_trains_answer": True})`.
Its three twins (`SHUFFLED-NAME:A1-TEACH`, `SHUFFLED-RELATION:A1-TEACH`, `FORCED:A1-TEACH`) resolve through the
existing `spec_for` prefix-splitting logic with no special-casing (confirmed by test).

**`brain/harness/results.py`**
- `RELATION_TWINNED` (line 136): `("A1", "A1-TEACH", "A5", "E′", "F")` — A1-TEACH is a plain network like A1 (not a
  hybrid), so it carries no entry in `RELATION_TWIN_SOURCE` (it runs its own search), exactly like A1.
- `A1_TEACH_DIAGNOSTIC_ARMS = ("A1-TEACH", "A1", "SHUFFLED-NAME:A1-TEACH")` (line 286).
- `_u1a_reading(arms, arm)` (line 289-296): reads `marks["U1a_NAME@T_L"]["reading"]` directly and returns it only if
  it is a dict — U1a's reading is `{case: share}` (`graders.grade_u1a`), never a float, so the pre-existing `_reading()`
  (float-or-None) would read `None` for it on every arm (pinned as a negative-control test).
- `_a1_teach_diagnostic(arms, void)` (line 298-311): `{"computable": bool, "u1a": {arm: reading}, "missing": [...],
  "void": {...}}` over the three arms above — `computable` False names whichever arm is missing or VOID. Called from
  `_decisions` (line 318) and returned under `"a1_teach"` in `_decisions`'s dict.
- `render_verdict` (line 461-471): prints the `a1_teach` line under "The decisions", both the computable and the
  not-computable branch (tested for both; confirmed it does not crash on a real committed results.json that carries
  no A1-TEACH arm at all).
- `RESULTS_VERSION` → `"b1-results-v4"`; a dated edit note added to the module docstring.

## Tests — red on the old code, then green

All seven of the brief's tests, plus companion positive/negative controls. Files:
`tests/brain/arms_soft/test_arm_a1_teach.py` (items 1-5), `tests/brain/harness/test_a1_teach_registry.py` (item 6),
`tests/brain/harness/test_a1_teach_results.py` (item 7).

| # | test | red (old code, commit 691f41a) | green (commit 5202613) |
|---|---|---|---|
| 1 | `TestA1TeachPositiveControl.test_switch_on_rises_clearly_above_the_uniform` | `AssertionError: 0.3333333432674408 not greater than 0.3833333333333333 : a: p=0.3333333432674408 did not rise clearly above 1/3 after 10 TEACH repeats` | ok |
| 1 (companion) | `test_switch_off_stays_at_the_init_uniform` | ok (trivially true pre-change — the switch does not exist, so passing it changes nothing; kept as the positive control's other half) | ok |
| 2 | `TestA1TeachIdentityAndNegativeControl.test_switch_false_is_byte_for_byte_a1_and_switch_true_differs` (identity **and** its own negative control in one test) | `AssertionError: 'ff4e89dd…' == 'ff4e89dd…' : the negative control: switch True over the SAME prefix must diverge from A1` (the identity half passed trivially pre-change; the negative control is what makes this test meaningful, and it is what failed) | ok |
| 3 | `TestA1TeachNothingCommitted.test_h_equal_names_differ` | `AssertionError: True is not false : the NAME head's parameters must differ between switch OFF and switch ON after the SAME new TEACH row` | ok |
| 4 | `TestA1TeachGrowth.test_birth_during_a_teach_row_does_not_crash_and_still_trains` | `AssertionError: False is not true : the virtual ask on row 3 must have actually trained c's row despite the birth mid-row` | ok |
| 5 | `TestA1TeachAttentionRefusal.test_a1_att_with_switch_raises` | `AssertionError: ValueError not raised` | ok |
| 5 | `TestA1TeachAttentionRefusal.test_a1_ma_with_switch_raises` | `AssertionError: ValueError not raised` | ok |
| 5 (companion) | `test_a1_att_without_the_switch_still_constructs` (negative control: the refusal is keyed to the switch, not the variant alone) | ok | ok |
| 6 | `TestA1TeachRegistry.test_a1_teach_carries_variant_and_the_switch` | `RunError: unknown arm 'A1-TEACH'; the runner knows: [...]` | ok |
| 6 | `TestA1TeachRegistry.test_the_three_twins_resolve_with_no_special_casing` | same `RunError` | ok |
| 6 | `TestA1TeachRegistry.test_a1_teach_is_named_in_the_known_arms_listing` | `AssertionError: 'A1-TEACH' not found in ['A0', 'A1', ...]` | ok |
| 6 | `TestA1TeachRegistry.test_spec_for_does_not_mutate_the_registry` | same `RunError` | ok |
| 7 | `TestA1TeachRelationTwinned.test_a1_teach_is_in_relation_twinned` | `AssertionError: 'A1-TEACH' not found in ('A1', 'A5', 'E′', 'F')` | ok |
| 7 | `TestA1TeachRelationTwinned.test_a1_teach_missing_twin_reads_twin_missing` | `KeyError: 'A1-TEACH'` (an empty gaps dict) | ok |
| 7 | `TestU1aReadingHelper.test_u1a_reading_returns_the_planted_dict` (+2 more in the class) | `AttributeError: module 'brain.harness.results' has no attribute '_u1a_reading'` | ok |
| 7 | `TestU1aReadingHelper.test_reading_would_have_read_none_the_bug_this_avoids` (the negative control the brief names: "test it on a planted U1a dict") | ok (this IS the bug — `_reading()` already reads None for a dict on the old code, which is exactly what the test pins) | ok |
| 7 | `TestA1TeachDiagnosticDecision.*` (4 tests) | `KeyError: 'a1_teach'` | ok |
| 7 | `TestA1TeachVerdictRendering.test_not_computable_line_renders_without_crashing` | `AssertionError: 'NOT COMPUTABLE' not found in "..."` | ok |
| 7 (companion) | `TestA1TeachRelationTwinned.test_a1_teachs_own_twin_present_is_no_gap`, `TestA1TeachVerdictRendering.test_computable_line_renders` | ok (positive controls; both trivially true pre-change since neither depends on new state, kept for post-hoc regression coverage) | ok |

Full logs: `/data/dev/brain-runs/scratch-a1teach/red-arm.log`, `red-registry-results.log`, `green-arm.log`,
`green-registry-results.log`. The red run for test 3 was re-verified after its own redesign (see below) via
`git stash` on the three source files (test files untouched) — same failure line, then `git stash pop` restored the
implementation.

**One test needed a mid-build correction, worth recording:** the first version of test 3 fed the SAME arm's very
FIRST-ever TEACH row to both copies. With only one name ever heard, `F.cross_entropy` over a single class is
mathematically constant (softmax of one logit is always 1.0), so its gradient is exactly zero regardless of the
switch — the test passed "red" for the wrong reason (a degenerate zero-gradient case, not the switch doing nothing).
Fixed by building a shared two-name prehistory first (via `snapshot`/`load`, so both copies start byte-identical),
and testing the SAME **third** TEACH row — non-degenerate (n=3 at the point of divergence). Re-verified red on the
old code after the fix (see the table).

## The whole brain suite

```
cd /data/dev/genome-wt-b1-teach && OPENBLAS_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/tmp nice -n 19 \
  /data/dev/venvs/brain/bin/python -m unittest discover -s tests/brain -t . > .../suite.log 2>&1
```
Read from the file (never through a pipe):
```
Ran 393 tests in 231.762s
OK (skipped=3)
exit 0
```
Run on commit **5202613** (the six-file commit above). Zero `ERROR:`/`FAIL:` blocks in the log (checked separately).
The 3 skips are pre-existing and unrelated to this change (env-gated tests, e.g. `B1_TAPE_TWICE`).

## The smoke run (not graded)

Built the SMOKE world (`brain.world.tape.smoke_world` / `build_tape`, the same code `tests/brain/harness/test_tape.py`'s
`setUpModule` uses) into `/data/dev/brain-runs/scratch-a1teach/smoke/` (2,287 rows, seed 20261001) — this same tape is
also the fixture `TestA1TeachIdentityAndNegativeControl` replays a prefix of (built once by that test's own
`setUpModule`, reused here rather than rebuilt). Ran `brain.harness.run` for `A1` and `A1-TEACH` into
`/data/dev/brain-runs/scratch-a1teach/smoke/run/`:

```
[run] A1:       2287 rows · asks 1704 (test 1204, correct 132) · wall 264s
[run] A1-TEACH: 2287 rows · asks 1704 (test 1204, correct 131) · wall 263s
```

Answer-kind table, `U1a_NAME@T_L` (156 asks each: 78 latin-upper + 78 latin-lower), read before any score:

| arm | n asks | answer-kind counts | distinct names given | correct |
|---|---|---|---|---|
| A1 | 156 | `{'NAME': 156}` | 1 → `{'a': 156}` | 6 / 156 (3 upper, 3 lower) |
| A1-TEACH | 156 | `{'NAME': 156}` | 1 → `{'a': 156}` | 6 / 156 (3 upper, 3 lower) |

**Both arms answer "a" to every single NAME ask, identically.** This is consistent with — not contradicted by — the
mechanism: with all NAME logits still at their zero init (the argmax of an all-equal vector is its first index, "a",
exactly as `TestA1TeachPositiveControl` models it), and the SMOKE schedule's `naming_reps=1`/`teach_rounds=1` giving
each name only a handful of TEACH exposures total, R46's one-training-step-per-TEACH-row has far too few repetitions
at SMOKE scale to move any logit's rank — my unit test needed ~10 repeats of each name to see a clear rise (item 1),
and the smoke tape's L1/L2 TEACH phase does not give any single name that many. The 132-vs-131 overall test-ask parity
is the same story at the aggregate level. This is a scale limitation of the SMOKE fixture, not a defect in the switch
(the switch's mechanism is directly demonstrated at the unit level, tests 1 and 3); a graded seed's L1/L2 TEACH volume
(§2.7: `teach_rounds=12`, `naming_reps=3`) is what R46 is actually sized for, and the seat's own gate runs that.

## Raised

Nothing. Every clause of R46 was implementable exactly as written; no bar was touched, no clause was worked around.

## Not done (by design, per the brief)

No graded run was launched. No merge into `b1-integration`. No push. No branch switch in any other worktree.
`/data/dev/genome-wt-b1int`, `/data/dev/brain-runs/b1/runs/`, and `/data/dev/brain-runs/b1/<seed>/` were never touched.
