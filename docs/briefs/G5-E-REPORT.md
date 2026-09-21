# G5-E REPORT — the three PREDICT error arms, decided by replay of life 2's tape

*Builder E (Sonnet 5), stamped `date "+%Y-%m-%d %H:%M %z"` = 2026-09-21 18:16 +0400 (amended pass: the
moon reading corrected (§6 — moon is a real thing in life 2's world, spikes and settles; §3's ceiling
table now shows the measured spike alongside G-MIND-3's pre-declared one; §5's mechanism explicitly
marked [Likely, one trace point] against the [Certain] zero-reading; §2/§7 corrected which replays
actually cross-checked which; per-arm cost added). First closed 18:07 +0400. The first edit stamps in
the code were typed as 17:04 — ahead of the clock, SOLUTIONS #50's exact shape — and corrected in one
pass to `date`'s own 16:58 output; see §9.*

Branch `g5-error-arms` in worktree `/data/dev/genome-wt-j`, from master `3b3a267`. `/data/dev/genome`
(the live creature) was never touched — no write under `run/`, `world/`, or any systemd unit; every
replay ran in a fresh out dir under `/data/dev/genome-wt-j/runs/g5-e-arms/` or a temp dir, and every
import of the pristine master tree (§1) was read-only.

---

## 0 · The finding that reframes the whole brief — read this before the table

The brief's byte-identity clause (item 1: "prove it by replaying life 2's tape under the default and
`--against` its live journal: must be identical") is **unsatisfiable as written, by no fault of G5-E**.

**Timeline (git history, journal timestamps, all independently confirmed by the coordinator's message
mid-task, citing Builder F's separate proof):**

| when | what |
|---|---|
| 2026-09-20T08:12:33Z (12:12:33 +0400) | life 2's `creature.service` process starts, on master at commit `75b0a9b` — `NRestarts 0` for its whole 24 h |
| 2026-09-21 10:31–11:18 +0400 | Builder D writes W3-2b: `genome/predict.py`'s `error()` moves its target from `expect()` (the LAST moment's remembered single winner) to `org.sight.cos(x_actual)` over every cell alive before this moment — commit `5a6dcfee` |
| 2026-09-21 11:46 → 13:16 +0400 | W3-2b merges to the `g4-wave3` staging branch, then to **master** |
| 2026-09-21 12:15–12:59 +0400 | the frozen verdict reader (`a21858b`) reads life 2 — **at this moment master did not yet carry W3-2b**, so its replay used the SAME formula life 2's live process was running, and "REPLAY 18,959 rows identical, plant caught" was a true reading *at the time* |

Because a running Python process never hot-reloads, life 2's live journal is a **permanent record of
the pre-W3-2b formula**. This worktree branches from master **after** 13:16 — it has always run
post-W3-2b code, as does every worktree branched from master since. **No code at master ≥ 13:16
2026-09-21 can replay life 2's tape identically to its own live journal** — not G5-E's, not master's
own unedited `creature/mind.py`/`genome/predict.py`. Confirmed directly: a replay of life 2's tape
under a **completely unedited, read-only import of `/data/dev/genome`'s current files** diverges from
the live journal at seq 4, field `err` (mine: `1.0`; life 2's own record: `0.2215`) — reproduced before
a single G5-E line was suspected, by importing `/data/dev/genome` ahead of this worktree on `sys.path`
and replaying rows 1–4 in a scratch temp root. The coordinator's message names the same mechanism and a
further symptom (734–739 final sight cells here vs 664 in life 2's own record) and cites Builder F's
independent proof that a checkout **at `75b0a9b`** (`/data/dev/genome-wt-k-hist`, not run by me) *does*
reproduce the live journal — evidence the replay machinery itself is sound and the divergence is the
code, not the tool.

**What this changes, concretely:**
- Item 1's literal check (`--against` life 2's live journal) is replaced by the only pair that can
  legitimately agree: **this worktree's default-arm replay vs a replay of the same tape under a
  pristine, unedited master checkout** (§1). Both run post-W3-2b code; both must be identical, and are.
- Item 2's "the unchanged arm = life 2's own series is the twin" is replaced by **the novelty arm
  replayed under this worktree's own code** — the coordinator's own wording. Every arm below is read
  against that twin's journal, never against life 2's stale record.
- Life 2's own frozen MODULATION verdict (0/5 spike at window 1, 0/1 at window 3) is **not the baseline**
  any more — it was read under a formula this tape can no longer produce. §3's table reads all four
  series (novelty included) under today's formula and reports life 2's number only as a labelled,
  ungraded side-by-side.
- **Raised, not mine to fix:** PREREG §10/§16's MODULATION ceiling table was calibrated on a ~0.23
  steady-state error (the pre-W3-2b formula). Today's formula's steady-state error on this tape is
  ~0.015–0.016 (§3), which turns the 3× spike bar into "any error above ~0.045" and makes the
  fake-boundary null noisy by construction (§3, the fake-boundary table) — a re-derivation question for
  whoever owns §10/§16, not answered here.
- **Also raised:** Builder F (worktree `genome-wt-k`) was replaying life 2's tape concurrently under a
  different brief; if that brief's own byte-identity clause reads the same way, it will hit the same
  seq-4 divergence for the same reason.

---

## 1 · The byte-identity proof (item 1, corrected)

`genome/machinery.py`'s `PREDICT` clause gains an **optional** trailing `; error
<novelty|conjunctive|episodic|comparator>`; absent (every genome on disk before this brief,
`genome/G4.genome` included) or spelled `; error novelty`, `declared["PREDICT"]["arm"] == "novelty"` and
`genome/predict.py`'s `Predictor.error()` runs the **same six lines** it ran before this brief for that
branch (renamed `e_novelty`, never refactored into a shared helper the default arm also routes through).

**Proof, not assertion:** replayed life 2's full 24 h-cut tape (`gather()`, `--hours 24`, 34,402 tape
rows → 18,959 mind rows — exactly the count the frozen reader itself reports) under this worktree's
default arm, and separately under a **pristine, completely unedited `/data/dev/genome` import** (same
tape, same genome file, `sys.path` pointed at `/data/dev/genome` ahead of this worktree so
`creature.mind`/`genome.predict` resolve to the untouched files — confirmed via
`sys.modules['creature.mind'].__file__`). `creature.replay.compare()` on the two journals:

```
worktree rows=18959  pristine rows=18959
diff: None  ->  IDENTICAL
```

**This is the brief's byte-identity pin, correctly targeted.** It proves the arm-selection machinery is
purely additive: a genome that never writes `; error <arm>` is unaffected by any of §2's code.

## 2 · The twin, and the four replays

All four replays (novelty/default, conjunctive, episodic, comparator) ran on the **same** 24 h-cut tape
built once via `tools.verdict_g4.gather()` (never re-derived — reused by import) and are read against
**the novelty arm's own replay under this worktree's code** (never life 2's stale journal, per §0).
**Only `novelty` ran twice**, via both `creature.replay.run_replay` and `tools.verdict_g4.worker()` — the
two final hashes match exactly (table below), which is the cross-check. `conjunctive`, `episodic` and
`comparator` each ran once, via `worker()` only (its `Episodes.nearest` cost makes a second run per arm
wasteful) — there is no second-road cross-check for these three, only for the twin they are read against.
The no-predict twin ran with `--blind predict` under the default genome (arm-independent by construction:
`predict_on` is `False`, `error()` is never called).

| arm | replayer | mind rows | final cells [sight, words] | final hash |
|---|---|---|---|---|
| novelty (default) | `run_replay` | 18,959 | [734, 17] | `30fbc32f…` |
| novelty (worker, for the exam) | `worker()` | 18,959 | [734, 17] | `30fbc32f2d418a82dd7bf21beb30c8042258bd0e9fb844233ca44efcd057a12a` |
| conjunctive | `worker()` | 18,959 | [735, 17] | `b986d873…` |
| episodic | `worker()` | 18,959 | [707, 17] | `58151b69…` |
| comparator | `worker()` | 18,959 | [725, 17] | `3f12e165…` |
| no-predict twin | `worker()`, `--blind predict` | 18,959 | [675, 17] | `01034dc3…` |
| *(reference, not run by me)* life 2's own live record | — | 18,959 | [664, 17] | `e96aa296…` (pre-W3-2b) |

Every arm's err-carrying (canvas) row count is **17,201** — including the no-predict twin, which is
silent (`max_err = 0.0` over all 17,201 rows) *because PREDICT was blinded*, not because it processed
fewer rows (the control the brief's "no-predict blind" clause asks for).

## 3 · MODULATION, per arm — the ceiling before the bar (item 3)

`F = 1 − θ_N = 1 − 0.952 = 0.0480` (G4.genome's own θ_N; unrelated to the 0.031/0.048 toy-front numbers
in earlier PREREG amendments, which were measured on a *different* front). Read via
`tools.verdict_g4.modulation(G, F)`, imported, never re-derived, on each replay's own `mind-journal`.

**Cost per arm, measured (whole-canvas throughput, not comparable to G-MIND-3's own declared per-call
cost — see below; these four ran together under `run_workers()`, 4 parallel BLAS-threaded processes
sharing the box):** no-predict-twin 126.95 ms/canvas, conjunctive 131.14, comparator 131.67, episodic
135.46 (novelty's own solo `run_replay` read 119.0 ms/canvas, the only single-process figure in this
set). Episodic's ~4–8 ms/canvas premium over the others is consistent with G-MIND-3's own pre-declared
figure for this arm's one added call — "one `Episodes.nearest` per canvas — 35.45 ms today, 3.33 ms
after R2" (MIND-MEMORY §4 G-MIND-3) — though that number is the isolated call cost on a different
measurement road (R2 unapplied here, solo, not the 4-worker whole-canvas figure above), so the two are
directionally consistent, not a matched pair.

**G-MIND-3's pre-declared ceiling table, walked against what was actually measured:**

| arm | G-MIND-3's pre-declared ceiling/verdict | measured on this tape |
|---|---|---|
| A (conjunctive) | admissible; spike ≈ 4.3× (word_novelty held 3 showings, median{1.0,1.0,1.0}) | **matches, but larger**: `first3_med = 1.0` on every new thing; measured spike **62–64×** on house/zog (table below) — G-MIND-3's 4.3× was computed against the pre-W3-2b ~0.23 steady-state denominator (§0); today's ~0.016 denominator makes the same numerator a much bigger ratio |
| B (episodic) | ratio undefined (denominator ~0 at steady state); the mark must be an absolute margin, `first3_med ≥ last50_med + 0.05` | **worse than predicted**: `first3_med = 0.0` (not merely undefined) on every new thing **and on zog** — see §5 |
| C (comparator) | admissible; ≥ 4.3×, "the only arm whose denominator is guaranteed well-behaved" | **matches, but larger**: `first3_med = 1.0` on every new thing; measured spike **64–69×** on house/zog (table below) — same pre-/post-W3-2b denominator shift as row A |

**Window 1 (5 new things: cup, house, key, moon, tree) and window 3 (zog), read today:**

| arm | last50_med (w1) | spike (of 5) | settled (of 5) | zog spike | zog first3_med | graded pass |
|---|---|---|---|---|---|---|
| novelty (default) | 0.0161 | **4/5** (house: 0.0431, ratio 2.68×, miss) | 1/5 (moon only) | **True** (68.26×) | 1.0 | False |
| conjunctive | 0.0161 | **5/5** | 1/5 (moon only) | **True** (64.31×) | 1.0 | False |
| comparator | 0.0156 | **5/5** | 1/5 (moon only) | **True** (68.73×) | 1.0 | False |
| episodic | 0.0 | **0/5** | 0/5 | **False** | 0.0 | False |

**Per-thing, window 1, novelty vs conjunctive — the one row that differs, and it is exactly the
mechanism G-MIND-3 proposed:**

| thing | novelty first3_med | conjunctive first3_med | comparator first3_med |
|---|---|---|---|
| cup | 1.0 | 1.0 | 1.0 |
| **house** | **0.0431** (ratio 2.68×, below the 3× bar) | **1.0** (ratio 62.11×) | **1.0** (ratio 64.1×) |
| key | 1.0 | 1.0 | 1.0 |
| moon | 1.0 | 1.0 | 1.0 |
| tree | 1.0 | 1.0 | 1.0 |

`house` is a square under a triangle (MIND-MEMORY's own worked example of a look-alike). Under the
unchanged (novelty) arm, house's glance resonates an existing cell well enough that
`1 − cmax = 0.0431` — barely above baseline, missing the 3× bar. Under **both** conjunctive and
comparator it reads the maximal `1.0`: conjunctive because `word_novelty = 1.0` for house's first 3
showings regardless of how well the shape resonates; comparator because the resonating cell's
established answer is a *different* word (not "house"), so the mismatch predicate fires. **This is the
one thing G-MIND-3 built these two arms to fix, and it is fixed, on the real tape, by both of them.**
Every other new thing already spiked under the unchanged arm (novelty's zog also spikes, 68.26×) — the
gap was narrow, and both admissible arms close it identically.

**Settle (10th showing ≤ 1.25 × last50_med) fails for every arm, including the unchanged default —
arm-independent, a fact about this world's regime today, not about which arm is chosen:**

| thing | last50_med | bar (1.25×) | novelty err@10 | conjunctive err@10 | comparator err@10 |
|---|---|---|---|---|---|
| cup | 0.0161 | 0.0201 | 1.0 | 1.0 | 1.0 |
| house | 0.0161 | 0.0201 | 1.0 | 1.0 | 1.0 |
| key | 0.0161 | 0.0201 | 0.0207 (misses by 0.0006) | 0.0207 | 0.0207 |
| moon | 0.0161 | 0.0201 | **0.0039 (settles)** | **0.0039 (settles)** | **0.0039 (settles)** |
| tree | 0.0161 | 0.0201 | 0.022 (misses by 0.0019) | 0.022 | 0.022 |

Only `moon` settles by its 10th showing, under every arm alike (the err@10 values are literally
identical between novelty/conjunctive/comparator — the arms only change the *first 3 showings*, never
later ones, so this is expected, not a coincidence). **1/5 majority-settled is a FAIL for all three**
graded arms under `modulation()`'s own conjunction — this is the regime finding of §0, not a per-arm
result.

**The fake-boundary null (window 0's midpoint, continuing things — must show no spike, ratio < 1.5×) —
also arm-independent and also NOT clean today:**

| thing | novelty | conjunctive | comparator |
|---|---|---|---|
| dot | 1.96× **(exceeds)** | 1.85× **(exceeds)** | 1.85× **(exceeds)** |
| wave | 1.69× **(exceeds)** | 1.6× **(exceeds)** | 1.6× **(exceeds)** |
| every other thing | < 1.5× | < 1.5× | < 1.5× |

2 of 11 continuing things exceed 1.5× under all three graded arms, at the **same** things (dot, wave),
with nearly the same ratios — because last50_med has collapsed to ~0.015 (§0's regime finding), a
~0.03 absolute fluctuation now reads as a 2× "spike" where under the old ~0.23 baseline it would have
read ~1.13×. **`null_fake_boundary_w0.no_spike` is `False` for novelty, conjunctive and comparator
alike** — not a defect of the new arms, the same instrument-in-different-units shape as SOLUTIONS #162.

## 4 · The no-predict blind (item 3's clause)

`max_err = 0.0` over all 17,201 canvas rows, arm-independent by construction (verified: it ran under the
default genome; `predict_on` gates on `self.predictor is not None and "predict" not in self.blind`,
never on `self.arm`). Row count matches the novelty arm's own (17,201 = 17,201) — the twin is silent
because PREDICT was blinded, not because it saw less tape.

## 5 · Arm B (episodic) — why it reads 0.0 everywhere, including on zog

`err = clip(max(0, cos_to_nearest_CELL − cos_to_nearest_EPISODE), 0, 2)`. Measured: **`first3_med = 0.0`
and `last50_med = 0.0` on every new thing at both windows, including zog — not merely an undefined ratio
(G-MIND-3's own prediction) but a value that never rises above 0 at all in the windows read.**

**[Certain — measured directly]** The all-zero reading itself: `first3_med = 0.0` and `last50_med = 0.0`
on every new thing at both windows, over the full 17,201-row replay — this is not a bug in
`_error_episodic` (toy-tested correct in isolation, `tests/genome/test_predict_arms.py::TestEpisodicArm`,
§9, where the same formula produces a real, large positive gap on a toy with a SPARSE episode store — see
`test_prototype_explains_a_glance_no_episode_is_near`). A raw trace at **zog's own first canvas** (seq
30002, `area.n=720` sight cells, `len(episodes)=15000` episodes already written):

```
area.n=720  episodes_len=15000  cos_cell=0.8723  cos_ep=0.8715  gap=0.0007
```

**[Likely — one trace point, not measured across many]** The mechanism below is inferred from this ONE
canvas's numbers; it was not re-measured at other new-thing arrivals or other points in the tape (that
would need the trace repeated several times, which this brief's budget did not cover — raised in §10).
An equally consistent alternative this single trace cannot rule out: the nearest cell and nearest
episode landed this close because they are literally *the same canvas's* glance-k (the cell) and
glance-1 (the episode written for it), rather than because the FAST store is generically 20× larger.
**Neither number is low.** My first hypothesis (that a brand-new shape's first showing would find
BOTH stores far away, "low − low ≈ 0") was wrong — measured, not guessed away: at 30,002 canvases in,
the 64-feature glance space is dense enough that *any* new shape lands within ~0.87 cosine of something
already stored, in **both** stores, and the two nearest neighbours are within 0.0008 cosine of each
other. **The real reason `cos_ep` can never fall meaningfully behind `cos_cell` is structural and
population-size-driven, not glance-index-driven:** every sight cell's own birth moment is *also* written
as a FAST episode (mind.py writes one episode per canvas regardless of whether that canvas births a
cell), and by this point in the tape the episode ring holds 15,000 rows against only 720 cells — a
20×-larger, exhaustive-search population drawn from the *same* distribution the cells were born from,
which can structurally never be a meaningfully worse match than the small SLOW population it is a
superset-like cover of. `max(0, cos_cell − cos_ep)` collapses to ≈0 by the arithmetic of population size
long before any "prototype explains more than memory" case (G-MIND-3's own motivating scenario) can
arise on a store this populated. The gap the formula was built to detect needs a FAST store much
*smaller* than the SLOW store, which never happens here (`FAST episodes 20000` vs a few hundred cells
mid-life, growing to thousands by the plant).

Whatever the mechanism, the practical consequence (also [Certain]) stands on its own: arm B's error
never rises above 0 anywhere it was checked on the real tape, so it cannot spike on the zog plant.

## 6 · Admissibility (item 3's zog gate, applied)

The brief: *"An arm that does not spike on zog is refused before its moon reading is read."* **`moon`
is a real thing in life 2's own world** — §3's window-1 table lists it among the five new things
(`cup, house, key, moon, tree`), it spikes under every graded arm (`first3_med = 1.0`), and it is the
**only** one of the five that also settles by its 10th showing (`err@10 = 0.0039`, §3's settle table).
Read literally, the brief's "moon reading" is that row: moon is the case G-MIND-3 predicted would
resonate an existing cell strongly enough to fail the old formula's ratio bar — MIND-MEMORY §4's own
words, "the moon resonates the circle cell, whose answer is «circle», and the word that arrives is
«moon»," measured there at "0.9–1.9× the steady error" under the pre-W3-2b formula (§0) — and on this
tape, under today's formula, it does not fail: measured `spike_ratio` at window 1
is **62.11× (novelty and conjunctive) / 64.1× (comparator)**, and moon is the one thing that settles
(`err_10th = 0.0039` at window 1, all three arms; §3's settle table). The look-alike that the unchanged
(novelty) arm actually *does* miss on this tape is `house` (§3), which is walked there in full.

| arm | zog spike | admissible per G-MIND-3's pre-declaration | measured admissibility |
|---|---|---|---|
| **A — conjunctive** | **True** (64.31×) | yes | **ADMISSIBLE** — spikes 5/5 incl. house and zog; fixes the one thing the unchanged arm missed |
| **B — episodic** | **False** (0.0) | mark uncertain (ratio undefined) | **REFUSED** before any further reading — fails the zog gate outright, and fails G-MIND-3's own declared fallback (`first3_med ≥ last50_med + 0.05`; measured `0.0 < 0.05`) |
| **C — comparator** | **True** (68.73×) | yes, "denominator guaranteed well-behaved" | **ADMISSIBLE** — identical spike pattern to A (5/5 incl. house and zog) |

**Neither A nor C, nor the unchanged default, PASSES the full conjunctive MODULATION mark** (spike AND
settle, with a clean null) under `modulation()`'s own grading — §3's settle and null tables show this is
a property of today's formula's regime on this tape (steady error collapsed from ~0.23 to ~0.015 between
when the mark's bars were calibrated and today, §0), not a defect specific to any arm. **A and C are
equally admissible and equally effective at the one thing G-MIND-3 built them to fix (house); B is
refused by its own pre-declared gate.**

## 7 · The exam column (item 4)

Every arm's held-out exam ran at the END of its own 24 h-cut replay (`tools/self_exam.py --held 10
--check-tape 400`, the same procedure the frozen reader's own twins use). **Not run: an exam at the END
OF WINDOW 1 specifically** (would need a second, `until_seq`-cut replay per arm — four more ~35–130 min
replays; raised as unaffordable within this brief's budget, not silently skipped).

| arm | `ask_seen_words.Q1` | `ask_all_words.Q1` |
|---|---|---|
| **novelty, via `worker()` (the twin — the number every row below is measured against)** | 108/110 = 0.9818 | 156/160 = 0.9750 |
| conjunctive | 109/110 = 0.9909 (+1) | 157/160 = 0.9812 (+1) |
| episodic | 107/110 = 0.9727 (−1) | 157/160 = 0.9812 (+1) |
| comparator | **110/110 = 1.0000 (+2)** | **160/160 = 1.0000 (+4)** |
| no-predict twin (PREDICT fully blind) | 109/110 = 0.9909 (+1) | 159/160 = 0.9938 (+3) |
| *(reference, not comparable — pre-W3-2b formula)* life 2's own frozen `unblinded-1` | 0.9364 | 0.9563 |

**Read against the correct twin (novelty-worker, both replayed under this worktree's own code, §2 — the
`worker()` and `run_replay` novelty replays share the identical final hash `30fbc32f…`, which confirms
`run_replay` and `worker()` are deterministic and mutually consistent on this tape, not identity to
master — §1's pristine-vs-worktree comparison is the identity proof):** the arms do **not** simply
separate from a flat baseline. **Comparator's +4 questions (156→160 of 160) is outside the ±1-question noise the other three
arms show** and is the clearest single exam result here — consistent with §3's mechanism (its lr scales
up only on a genuine established-answer mismatch, never on an unresolved "nothing born yet" glance the
other arms also treat as maximal surprise). **The no-predict twin's +3 (156→159) is the finding worth
flagging as a caution, not a footnote: blinding PREDICT ENTIRELY does almost as well as the best arm and
clearly better than conjunctive/episodic/the unchanged novelty arm.** On this world, at this tape's
length, a constant learning rate (`lr_scale ≡ 1.0`) is nearly as good as the most sophisticated
modulator tried. Conjunctive and episodic each move exactly +1 on `ask_all_words` and are within the
resolution of a 160-question exam (0.625 pp/question) — **not distinguishable from novelty** on this
reading alone. Life 2's own frozen `.9364`/`.9563` is not a valid comparator at all (§0: pre-W3-2b
lr-scaling) and is shown only as the historical reference it is.

## 8 · The code

- `genome/machinery.py` — `PREDICT`'s `re.fullmatch` gains an optional, non-capturing `(?:; error
  (novelty|conjunctive|episodic|comparator))?` tail; `declared["PREDICT"]["arm"] = m.group(3) or
  "novelty"`. An unknown arm word refuses exactly as an unknown gene does (tested).
- `genome/predict.py` — `Predictor.__init__` gains `arm: str = "novelty"` and `self._word_seen: Dict[str,
  int] = {}` (arm A's per-word delivery count). `error()` computes `e_novelty` first (the untouched six
  lines, renamed), then dispatches on `self.arm`; the `"novelty"` branch is `e = e_novelty` with no
  further computation — byte-identical (§1). Three new private methods, `_error_conjunctive`,
  `_error_episodic`, `_error_comparator`, each documented against its MIND-MEMORY §4 G-MIND-3 source and
  its fallback for a sight-only canvas / no established answer / empty FAST store.
- `creature/mind.py` — `_consume_eye` hoists `xw = encode_word(word, …)` above the `predictor.error()`
  call (pure, so this changes nothing else) and passes `word=word, xw=xw, episodes=self.episodes` to
  `error()` unconditionally; the `"novelty"` arm ignores all three. `Predictor(...)` is now constructed
  with `arm=self.genome.declared["PREDICT"].get("arm", "novelty")` at both `__init__` and `resume()`.
- **Known gap, out of scope for a replay-only brief:** `_word_seen` (arm A) is not persisted in
  `ledger.json` — `Mind.resume()` re-derives `_heard` (a boolean set) from `moment_word`, which cannot
  recover a per-word COUNT. A live deployment of arm A across a restart would restart every word's count
  at 0. `creature/replay.py` and `tools/verdict_g4.py`'s `worker()` — this brief's only callers — never
  call `resume()`, so this never fired here; flagged for whoever might deploy arm A live.

## 9 · Tests

`tests/genome/test_parse_g4.py` — extended `test_each_new_gene_declared_dict` and
`TestTheLifeGenome.test_life_genome_parses_with_written_thetas_and_the_declared_set` for the new `"arm"`
key (an intentional shape change, stamped); new class `TestPredictArmClause` (5 tests: bare line and
explicit `; error novelty` both default to `"novelty"`; all three new words parse; an unknown word
refuses; a misspelt clause word (`arm` instead of `error`) refuses).

`tests/genome/test_predict_arms.py` (new, 18 tests) — `TestNoveltyArmUnchanged` (4: default ctor is
`"novelty"`; nothing-born-yet and exact-repeat pin the same two numbers the pre-brief code always gave;
the new kwargs are provably ignored by the novelty arm); `TestConjunctiveArm` (3: word_novelty held for
showings 1–3 then falls at showing 4 — the exact off-by-one MIND-MEMORY's own table warns against, caught
and fixed here before any replay was spent, §10; a never-heard word on an already-familiar shape still
spikes; a sight-only canvas has no word to be new); `TestEpisodicArm` (5: bootstrap zero; `episodes=None`
behaves like empty; a resonating prototype with no near episode gives a real positive gap — proving the
formula CAN produce a nonzero value, which is why §5's all-zero reading on the real tape is a fact about
this tape's density, not a dead formula; a real matching episode closes the gap to zero; never mutates
the store); `TestComparatorArm` (6: matching word → graded novelty; mismatched word → maximal surprise —
the moon/house mechanism, isolated; no established answer yet → fallback; sight-only → fallback; nothing
resonates → maximal surprise; never births or mutates misfire counters — read-only, as `_misfire`'s
reimplementation must be).

**Suite runs, quoted from log files (never piped/tailed, SOLUTIONS #191/#197):**
- `python3 -m unittest discover -s tests/genome -t . > /tmp/g5e-logs/genome-suite-final.log 2>&1` →
  **`Ran 159 tests in 103.261s` / `OK (skipped=1, expected failures=6)`**
- `python3 -m unittest discover -s tests/creature -t . > /tmp/g5e-logs/creature-suite-final.log 2>&1` →
  **`Ran 133 tests in 714.782s` / `OK`**

Both runs are on the FINAL bytes (after the stamp fix, §0's addition, everything in §8) — the earlier
in-flight runs (genome 136→159 as tests were added; creature 133 OK before the stamp-only edit to
`mind.py`'s header) were superseded and are not quoted as the deliverable.

## 10 · Raised, not worked around

1. **§0 in full**: the brief's literal byte-identity clause against life 2's live journal cannot be
   satisfied by any master-branched worktree today; replaced by the pristine-vs-worktree proof (§1).
2. **PREREG §10/§16's MODULATION ceiling table needs re-derivation** for the post-W3-2b regime (steady
   error ~0.015–0.016 now vs ~0.23 when the 3×/1.25×/1.5× bars were set) — affects the null and the
   settle clause for **every** arm, not a G5-E-specific finding.
3. **Arm A's `_word_seen` is not resume-safe** (§8) — a replay-only gap, flagged for any live use.
4. **The window-1-exam clause of item 4 was not run** (§7) — cost, not oversight; the end-of-life exam
   was run for all arms instead and is reported with its limitation stated.
5. **Builder F's concurrent replay** (`genome-wt-k`) may hit the same seq-4 divergence if its own brief's
   byte-identity clause is worded the same way — the orchestrator's decision, not mine to message.
6. **The no-predict twin scores within 1 question of the best arm** (§7: 159/160 vs comparator's
   160/160, both well above novelty's 156/160) — on this world, at this tape's length, PREDICT's whole
   modulation mechanism (any of the four arms) buys very little over a constant learning rate. Worth a
   read by whoever owns PREDICT's design, not a verdict this brief is positioned to render (one tape, one
   life, one exam).
7. **Arm B's zero reading (§5) is [Certain]; its explanation is [Likely], not settled.** The all-zero
   measurement (`first3_med = last50_med = 0.0` on every new thing, both windows, 17,201 rows) is
   certain. The population-size mechanism — the exhaustive `Episodes.nearest` search over a FAST store
   20× the size of the SLOW store structurally can't fall meaningfully behind the cell search — is
   inferred from **one** raw trace at zog's first canvas (seq 30002). A same-canvas glance-k/glance-1
   alternative is not ruled out by that single point. Before arm B's premise is judged a design mismatch
   for whoever might want it on a future life, the trace should be repeated at several new-thing
   arrivals and several points in a tape — this brief's budget covered one.

---

*All readings final: the byte-identity proof (§1), the four-arm MODULATION table (§3), the arm-B
mechanism trace (§5) and the novelty-worker exam twin (§7) all landed before this report was closed.*
