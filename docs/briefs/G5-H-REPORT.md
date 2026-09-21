# G5-H REPORT — MODULATION's settle and null bars re-derived for the W3-2b regime

*Builder H (Sonnet 5), stamped `date "+%Y-%m-%d %H:%M %z"` = 2026-09-21 18:44 +0400. Branch
`g5-modulation-bars` in worktree `/data/dev/genome-wt-l`, from master `ee0e45e`. `/data/dev/genome`
(the live creature, `run/`, `world/`, systemd) was never touched — read-only throughout; every
measurement ran in a fresh `--out` under this worktree's own `runs/`, or against a **hard-link
copy** of an existing record (`cp -al`), never a record's own `--out`.*

---

## 0 · What changed, in one line

`tools/verdict_g4.py`'s `modulation()` now computes **two independent readings** on every read —
the §16 fixed-bar reading (3× spike / 1.25× settle / 1.5× null, the pre-W3-2b record) and a
**regime-derived** reading whose null band and settle bar are **derived from the life's own
pre-window (window-0) data at read time** (#158's argument for adaptivity — never a typed ratio).
Both are in `results.json` under `marks.MODULATION`; the top-level verdict grades on the
regime-derived one (`marks.MODULATION.pass`); the §16 reading is kept as
`marks.MODULATION.pass_fixed_bars_record`. Nothing else in the reader changed except the two
places that RENDER MODULATION's own text (the `bar` string in `main()`, the VERDICT.md row in
`write_verdict()`) — required to print both readings, scoped to MODULATION only.

## 1 · The derivation (`_regime_calibration`, new function, `tools/verdict_g4.py`)

Both quantities are computed **only from window-0 rows** (the pre-window canvases — the only
stretch on the tape with no real arrival to confound the calibration):

- **Null band:** at every 100th canvas inside window 0, treat it as a FAKE boundary and compute —
  for every thing with ≥ 3 showings after it — the SAME statistic the real spike rule computes:
  `median(its first 3 errs after) / median(the 50 errs immediately before)`. Doing this at every
  such boundary, for every continuing thing (not just the one midpoint the original null used),
  yields a sample of "what ratio does pure noise produce on THIS life's own tape"; its 95th
  percentile is the null band. **A real spike must clear this band AND the fixed 3× bar** (brief's
  "must exceed BOTH").
- **Settle bar:** window 0's own per-showing errors, for each thing's showings **after its own
  first 3** (excluding each thing's bootstrap transient — the only place on the tape a window-0
  thing is itself new) — a continuing thing's own steady per-canvas noise. Its 95th percentile is
  the settle bar: an **absolute error ceiling**, not a ratio on a baseline that can collapse to
  near-zero (1.25× of a ~0.016 median is ~0.02 — a bar a single glance's own rounding can trip).
- Both readings are `None` (never a divide-by-zero, never a silent 0) when window 0 doesn't carry
  enough data (e.g. every boundary's `last50` reads 0, as the no-predict blind's does throughout —
  §4 below) or a life is too young; every caller checks before grading.
- Per new thing, `modulation()` now also prints **`first_settle_showing_regime`** — the first
  showing (1-indexed) at which that thing's own error first cleared the regime settle bar, found
  even where the 10th showing itself didn't stay under it (a finding about the mechanism, printed
  rather than hidden — see §3's `cup`/`house` rows, where a thing dips under the bar mid-stream and
  then reverts by its 10th showing: worth a look by whoever reads tomorrow's verdict, not something
  this brief's bars can resolve).

## 2 · Life 3b's own band (control (a) — the smoke on a hard-link copy)

`cp -al runs/g4-smoke-life3b-2h runs/g4-smoke-life3b-2h-ctl2` (the original, `/data/dev/genome`'s
own record, untouched); `python3 tools/verdict_g4.py --root /data/dev/genome/run --genome
genome/G4.genome --out runs/g4-smoke-life3b-2h-ctl2 --hours 2 --skip-random --reuse` — 55.4 s, every
twin reused (no replay), `VERDICT FAIL` (unchanged failure set: `v_retention, vi_knows_unknown,
MODULATION, DOOR, PARK`).

**Reading:** `marks.MODULATION.windows == {}` (the 2 h smoke never reaches a window boundary — the
maker's windows are 6 h), `reason` = *"no window change on this tape yet … not gradable; the regime
band is still derived and printed under 'regime'"*, and the band **is** printed:
`null_band_95 = 2.2212` (n=150 fake-boundary samples, share within band 0.9467), `settle_bar_err_95
= 0.0397`. `null_fake_boundary_w0` (the one-midpoint check, still computed on 2 h of data) reads
`no_spike(regime) = False` — `wave` spikes to 3.73× at that specific probe, above even the derived
band, a real reading of this life's own noisy things (`dot`/`wave` recur as the noisy pair across
every replay in §3 too) — printed honestly, not smoothed away. **Control (a) satisfied**: not
gradable, band printed.

## 3 · E's four arm replays of life 2 under master (control (b))

Read directly (`modulation({"mind": read_jsonl(...)}, F=0.048)`, `F = 1 − θ_N`, `θ_N = 0.952` from
`genome/G4.genome`) against
`/data/dev/genome-wt-j/runs/g5-e-arms/replay-{novelty-worker,conjunctive,comparator,episodic}/mind-journal.jsonl`
— Builder E's own replays, read-only, nothing re-run.

| arm | regime band (n) | house spike(fixed) | house spike(regime) | dot ratio | wave ratio | null(fixed) | null(regime) |
|---|---|---|---|---|---|---|---|
| novelty (default — what life 3b runs) | 2.0142 (462) | **False** (2.68×) | **False** | 1.96 | 1.69 | False | **True** |
| conjunctive | 2.0148 (462) | **True** (62.11×) | **True** | 1.85 | 1.60 | False | **True** |
| comparator | 2.0669 (462) | **True** (64.10×) | **True** | 1.85 | 1.60 | False | **True** |
| episodic | None (0 — `last50` reads 0 throughout) | False | False | — | — | False | None |

**Both required readings confirmed:** house still MISSES the spike under the unchanged (novelty)
arm and PASSES under comparator, exactly as Builder E's report §3/§6 found — this reader change
doesn't alter which arm is "admissible," it only fixes the INSTRUMENT so the mark can be read at
all. `dot` (1.96×/1.85×) and `wave` (1.69×/1.60×) now sit **inside** their life's own derived band
under every graded arm — the exact two things the fixed 1.5× null was failing on purely from the
regime collapse (E's report §3, "not a defect of the new arms, the same instrument-in-different-
units shape as #162"). Settle readings (`first_settle_showing_regime`, per thing): under novelty,
`moon`/`key`/`tree` settle by showing 3–5 and stay settled; `cup` dips under the bar at showing 4
but reverts to 1.0 by its 10th (printed, not hidden — the same finding as §1's note); `house` never
settles within its window under novelty (consistent with its missed spike — it never leaves the
established cell) but settles at showing 4–5 under conjunctive/comparator, where the spike itself
fires. Episodic's own window-0 has `last50 == 0` throughout (its error is 0 almost everywhere — E's
report §5), so its null band and settle bar both read `None`/0.0 rather than crashing or silently
inventing a number — an honest "ungradable on this arm's own noise floor," not a false reading.
**Control (b) satisfied.**

## 4 · Life 2's original record under the regime-derived bars (control (c))

Two independent checks, both against the record `/data/dev/genome/runs/g4-verdict-life2-20260921-1215/`
(the pre-W3-2b, ~0.23-steady-state regime), neither touching the original:

1. **Direct:** `modulation({"mind": read_jsonl(".../live-journal.jsonl")}, F)` on the exact rows the
   frozen reader (`a21858b`) graded MODULATION from.
2. **End-to-end:** `cp -al runs/g4-verdict-life2-20260921-1215 runs/g4-verdict-life2-regime-ctl`,
   full reader re-run with `--reuse` (54.2 s, all 34 twins reused) — `VERDICT FAIL`, failed set
   includes `v_retention, MODULATION` (plus `W3_2_rules, W3_1_beliefs, DOOR, PARK`, which this
   reader version grades and the frozen `a21858b` did not — those are §18's later extensions, not
   this brief's subject, and are unrelated to MODULATION).

**Reading (both roads agree exactly):** `null_band_95 = 1.6644` (n=462, on the OLD ~0.23-regime
noise), `settle_bar_err_95 = 0.4182`. `graded_windows_regime`: window 1 — **0 of 5 spike**, 5 of 5
settle (settle became MORE lenient, as expected — 0.4182 is far above 1.25×0.23≈0.29 — but spike
stays the binding, majority-failing clause); window 3 (`zog`) — **0 of 1 spike**.
`marks.MODULATION.pass = False` — **exactly the FAIL the frozen reader read** (§18: "FAIL on
exactly (v) and MODULATION"; §18 addendum 2's per-window numbers: window 1 "0 spikes… 2 settled",
window 3 "0 of 1" — the spike counts match bit for bit, 0/5 and 0/1, under both the fixed and the
regime bar). **The regime-derived band on this life's own OLD noise (1.6644) does NOT pass life
2's MODULATION — control (c) satisfied**, and the band is not too wide by the brief's own test.

## 5 · The no-predict blind (control (d))

`modulation()` on `/data/dev/genome-wt-j/runs/g5-e-arms/replay-no-predict/mind-journal.jsonl` (arm-
independent, `err = 0.0` over all 17,201 canvas rows — Builder E's report §4). `null_band_95 =
None` (0 ratio samples: every boundary's `last50` reads 0, so every candidate sample is skipped by
construction — never a `0/0` masquerading as a real ratio). Every `spike`/`spike_regime` reads
`False` (0 of 5 at window 1, 0 of 1 at window 3, under both readings — `spike_ratio` itself is
`None`, printed rather than a fabricated number). `marks.MODULATION.pass = False`,
`pass_fixed_bars_record = False`. **Never PASSES, and the ungradable null is visible in the
output (`null_band_95: None`) rather than silently defaulting to a pass — control (d) satisfied.**

## 6 · Reader diff summary

`tools/verdict_g4.py`:
- New `_regime_calibration(mind, step=100, prev_window=50, first_n=3, settle_skip=3) -> dict` —
  the derivation of §1, pure function of the `mind` rows already filtered to drawn-world moments
  with a word (the same filter `modulation()` already applied). No other module reads or writes
  window-0 rows differently; the existing window/median/per-thing loop is **reused, not
  re-derived** (the per-window loop, the `by_seq` map, the existing `null_fake_boundary_w0` block's
  structure, the existing `read_jsonl`/`gather` machinery — all untouched).
- `modulation()`: calls `_regime_calibration` once at the top; each per-thing record gains
  `spike_regime`, `settled_regime`, `first_settle_showing_regime`, `n_showings` beside the untouched
  `spike`/`settled`/`spike_ratio`/`err_10th`/`settled_toy_bar_F_plus_05`; `null_fake_boundary_w0`
  gains `no_spike_regime` beside the untouched `no_spike`; a new `graded_windows_regime` list beside
  the untouched `graded_windows`; `out["regime"]` carries the full calibration dict; `out["pass"]`
  now reads the regime-graded verdict, `out["pass_fixed_bars_record"]` the old one; `out["reason"]`
  is set (only) when `windows` is empty, naming the smoke/short-tape case explicitly.
- `main()`: `M["MODULATION"]["bar"]` text updated to name both readings (was the §16-only sentence).
- `write_verdict()`: the MODULATION row in VERDICT.md now prints both `graded_windows`, both
  `no_spike`, the regime band/share/settle-bar numbers, and `pass_fixed_bars_record` beside the
  graded `pass` — the only other place this brief's change is visible.
- **Everything else — every other mark, `gather()`, the twin machinery, REPLAY, the plant, every
  other reader rule — is byte-for-byte what master already had.** `git diff --stat`:
  `tools/verdict_g4.py | 115 ++++++++++++++++++++++++++++++++++++++---------`, one file.

**A design choice, flagged rather than silently made:** the brief says grading should use the
regime-derived reading "from life 3b on." I did not gate this on the life's identity (no
version/date check) — `_regime_calibration` runs identically on every read, deriving its own band
from whatever window-0 data that particular life's tape carries, so it is naturally adaptive rather
than switched. §4's control is the reason this is safe: re-reading life 2's OLD record through this
same, always-regime-grading code still fails MODULATION (the band self-calibrates to the OLD
regime's own noise and stays well under the real spike ratios' floor), so nothing about life 1's or
life 2's *already-published* verdicts would change if they were re-read with this reader version.
If a stricter "only from life 3b's own genome/timestamp onward" gate was intended instead, that is a
one-line addition at the `out["pass"]` assignment in `modulation()` — raised here rather than
guessed at, since the brief's own control (c) doesn't distinguish the two designs (both satisfy it).

## 7 · Tests

`tests/creature/test_verdict_modulation_regime.py` (new, 6 tests, synthetic `mind` rows only — no
replay, no root, deterministic via `random.Random(seq)`-seeded jitter so every number is
reproducible and no exact-tie percentile artifact sneaks in, §7a note below):

- `TestRegimeCalibration.test_settle_bar_is_the_95th_percentile_of_window0s_own_noise_excluding_bootstrap`
  — an independent reference computation (same exclusion rule, written separately in the test) must
  match `_regime_calibration`'s own settle bar to 6 decimal places; the bootstrap transient (err=1.0)
  must never leak into it.
- `TestRegimeCalibration.test_null_band_sees_a_planted_ratio_and_a_flat_stream_does_not_clear_it` —
  a planted, genuine elevation (ratio 3.125×) must sit ABOVE the derived band (so it stays
  distinguishable from noise); flat noise (ratio ≈1.0) must sit inside it.
- `TestModulationRegimeGrading.test_planted_spike_is_caught_a_flat_stream_is_not_and_a_bandonly_ratio_needs_both_bars`
  — the brief's own three-way test: a planted 10× spike passes under both readings; a planted 1.1×
  flat stream passes neither; a planted ratio strictly between the band and the fixed 3× bar
  (clears the band alone) **still fails** — proving "must exceed BOTH" is enforced, not either/or.
- `TestModulationRegimeGrading.test_regime_settle_bar_admits_natural_noise_the_fixed_ratio_bar_refuses`
  — the brief's central defect, reproduced on purpose: a 10th-showing error strictly between the
  fixed bar (1.25×) and the regime bar (95th-pct of real noise) MISSES `settled` and PASSES
  `settled_regime`.
- `TestModulationRegimeGrading.test_no_window_change_yet_is_not_gradable_but_the_band_is_still_printed`
  — mirrors control (a) in miniature: empty `windows`, `pass=False` both readings, `reason` names
  "not gradable", the band is still populated.
- `TestModulationRegimeGrading.test_pass_and_pass_fixed_bars_record_are_independent_fields` — a
  clean life (big spikes, settles to near-zero) passes BOTH readings, proving they are not aliases
  of one boolean.

**§7a, a self-catch worth keeping on the record:** the first draft of `_baseline_window0` used a
FIXED, exactly-periodic 10-value noise pattern (not real jitter). Two of the six tests then failed
— not from a bug in `_regime_calibration`, but because a perfectly periodic synthetic input, sampled
at a boundary step that doesn't evenly divide the pattern's period, produces EXACT ties at the 95th-
percentile value (several ratio samples landing on the identical float), and a strict `<` around an
exact tie is a coin flip a real (continuous, never-repeating) error series would essentially never
hit. Fixed by generating the noise as a genuine (deterministically-seeded) mixture — 90% quiet,
10% real bumps — rather than a repeating sequence; every test is green since. Kept in §6's diff note
and here because it is exactly the class of self-inflicted instrument trap the estate's own
SOLUTIONS corpus warns about (a synthetic fixture whose own structure, not the code under test,
produces the failure) — worth a look before any future synthetic-tape test in this tree reuses a
fixed periodic pattern for "noise."

`python3 -m unittest tests.creature.test_verdict_modulation_regime -v` → **`Ran 6 tests in 0.12s` /
`OK`**.

Suites on the final bytes (stamps corrected to `date`'s own output, §8):
- `python3 -m unittest discover -s tests/genome -t . > /tmp/g5h-logs/genome-suite-final.log 2>&1` →
  **`Ran 136 tests in 65.434s` / `OK (skipped=1, expected failures=6)`**
- `python3 -m unittest discover -s tests/creature -t . > /tmp/g5h-logs/creature-suite.log 2>&1` →
  **`Ran 139 tests in 670.541s` / `OK`** (133 pre-existing + the 6 new from this brief; every
  pre-existing test still green — the reader change is additive-only, no creature/body code touched).

## 8 · Edit stamps

Every `# edit:` comment in `tools/verdict_g4.py` and the new test file reads `2026-09-21 18:44
+0400` — the FIRST draft carried `20:02` (typed from an earlier session clock, SOLUTIONS #50's exact
shape) and was corrected in one pass after running `date` directly (18:44) and finding the
mismatch; `sed`-replaced across both files, re-verified with `grep`.

## 9 · Raised, not worked around

Nothing in the brief's four steps was unimplementable. The one open design question is §6's grading-
scope note (regime-derived-always vs. gated-from-life-3b) — both satisfy every stated control;
flagged for the orchestrator's word rather than silently picked.

---

*All controls' numbers in this report were read directly off `results.json`/`VERDICT.md` under
`runs/g4-smoke-life3b-2h-ctl2/` and `runs/g4-verdict-life2-regime-ctl/` (both hard-link copies,
neither the original record's own `--out`), or from a direct `modulation()` call against Builder
E's and the frozen reader's own journal files, read-only.*
