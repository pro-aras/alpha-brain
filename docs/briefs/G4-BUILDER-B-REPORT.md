# REPORT — Builder B (Claude Sonnet 5): the G4 genes, tasks B0–B7

*edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 23:05 +0400. Worktree `/data/dev/genome-wt-b`, branch
`g4-genes`. Every commit's own test run is quoted verbatim below; the full suite (`python3 -m unittest
discover -s tests/genome -t .`) reads **`Ran 58 tests in ~12s — OK (expected failures=2)`** at HEAD
(`b448eda`), reproduced twice, byte-identical pass/fail pattern both times.*

## THE PIN
Read independently before any of my work, at git `9a36475`: `hash_dev` =
`d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86` (660 dev canvases, 2,640 moments,
9.9 s). **Reproduced by me at the start of B0** (before writing any test): identical, 9.43 s. Verified
again after **every** commit B0–B7 via `tests/genome/test_pin_skeleton.py`, part of the full suite every
time — **held at every single commit, byte-identical, never moved.**

## B0 — the pin (`tests/genome/test_pin_skeleton.py`)
Commit `a493936`. Test log: `Ran 1 test in 9.666s — OK`. Pin before: `d4b5c6b8d5…` (this commit's own
re-derivation). Pin after: unchanged (this commit IS the pin check). Added `tests/__init__.py` and
`tests/genome/__init__.py` — required for `unittest discover -s tests/genome -t .` to import the package
at all (Python 3.14's loader refuses a non-importable start dir; verified empirically both ways).

## B1 — the parser (`genome/machinery.py`, `genome/G4.genome`, `tests/genome/test_parse_g4.py`)
Commit `e001834`. Test log: `Ran 13 tests in 9.096s — OK` (12 in `test_parse_g4.py` + the pin). Pin
before/after: unchanged.
- `genome/G4.genome` = docs/G4-DESIGN.md §9, with the PREREG §1 correction (`GAZE surprise fixations 4`,
  not the draft's 12). Thetas left as `THETA_N`/`THETA_M` — refused unfilled, exactly as G1.genome is.
- `Genome.declared: Dict[str, dict]` (new field, `default_factory=dict`) holds 20 new genes' own parsed
  sub-dicts: BODY, TAPE, HEART, CRASH, TRAITS, SURPRISE, CYCLE, FAST, SLEEP, PREDICT, FILE, CURIOSITY,
  PARK, INDUCE, DEDUCE, BELIEF, SENTENCE, WORLD, HANDS, ASK — each a strict `re.fullmatch`, refusing a
  placeholder or malformed/truncated line (tested individually, 20/20).
- `AREA` now accepts `{sight, words}` required, `episodes` optional (`AREA episodes from fast`); a
  fourth/unknown area is still refused.
- `RECALL k=N` for any N ≥ 1 (was "k=1 only"). `Organism.recall(side, x, k=1)` extended: k=1 is
  byte-identical to before (a dict-spread trick returns `{}` at k≤1, so the returned dict's KEYS are
  unchanged); k>1 adds a `"ranked"` key, the top-k answer cells by strongest edge, ties by smaller id.
  Proven with a hand-built 2-cell organism: k=1 == the no-k default exactly; k=2 adds `ranked` and
  changes nothing else.
- `G4-skeleton.genome` and `G1.genome` proven to parse to the SAME `Genome` field-for-field (24 fields
  compared, including the new `declared` — both `{}`).

## B2 — `Organism.moment_sight(x_s)` (`tests/genome/test_moment_sight.py`)
Commit `fa7732a`. Test log: `Ran 17 tests in 9.334s — OK`. Pin before/after: unchanged.
Resonance + novelty birth on sight only (no MEET: no HEBB/DELTA/misfire/PRUNE/MERGE). Mirrors `moment()`'s
tail (`t` advances; SCALE fires at its own multiples). Counter `moments_sight_only` is a **plain
attribute, never a `self.c` key** — `state_hash` hashes `json.dumps(self.c)`, so a new key would have
moved the pin at value 0 for every genome that never calls this method.
**Toy numbers:** 50 sight-only moments (random 64-d unit vectors) → 8 cells born, 0 edges, 0 word cells;
`org.t == 50`; a life that ran them hashes differently from one that didn't (`state_hash` differs).

## B3 — FAST (`genome/fast.py`, `tests/genome/test_fast.py`)
Commit `209452d`. Test log: `Ran 22 tests in 9.224s — OK`. Pin before/after: unchanged.
`Episodes(cap, dim_s, dim_w)`: `write` (ring, oldest overwritten, id never reused), `nearest(x_s, k)`
(cosine, ties by smaller id), `most_surprising(n)`, `save/load` (npz, atomic via a real file handle +
`tmp.replace(path)` — passing a string to `np.savez_compressed` would auto-append `.npz` to the `.tmp`
name and break the rename; a file handle avoids that). `get(id)` added beyond the four named methods
(needed by B5/B7 to read the record an id names).
**Toy numbers:** an episode written at moment t is `nearest`'s top-1 at cos=1.0 immediately after write,
with its word; a query orthogonal to everything written (the "shuffled" one-hot) scores cos=0.0, not a
genuine match; a cap-3 ring after 4 writes: the oldest id's `get()` returns None, the other 3 remain and
`most_surprising` never sees the evicted one; save/load round-trips every array byte-exact
(`np.array_equal`) plus functional parity (`nearest`/`most_surprising` identical before/after).

## B4 — PARK (`genome/park.py`, `tests/genome/test_park.py`)
Commit `6cb67d9`. Test log: `Ran 29 tests in 9.307s — OK`. Pin before/after: unchanged.
`Park(n)`: `answer(want, reason) -> "open"|"parked"` (the n-th IDENTICAL reason parks; a different
reason has its own independent counter, never adding to another's); `reopen(want, evidence_kind) -> bool`
(only `"new-sense"`/`"document"`; `"same-sense"` and anything else refused); `state()`.
**Toy numbers:** 3× the same reason → `"open","open","parked"`; the 4th ask returns `"parked"` and the
counters are provably untouched (`state()` before == after); a different reason (B) does not add to A's
count (A still parks on its OWN 3rd occurrence, unaffected by B's 1); `reopen(w,"same-sense")` → `False`,
still parked; `reopen(w,"document")` → `True`, reopened, fresh counting from 0; `reopen(w,"new-sense")`
also reopens; `state()` lists each parked want's reason and count.

## B5 — «why» (`genome/questions.py`, `tests/genome/test_why.py`)
Commit `e3bf14b`. Test log: `Ran 34 tests in 9.380s — OK`. Pin before/after: unchanged.
`why(org, ledgers, episodes, word) -> {"cells", "episodes", "edges"}` — read-only (proven: `state_hash`
and the Episodes ring's `n_written`/`_next_slot`/`ids` all unchanged after two `why()` calls, one of them
for a never-shown word).
**Toy numbers:** a G0b-style life on 3 things (circle/square/triangle, 20 showings each, pool3 retina) +
an Episodes store written beside it — `why(org, ledgers, ep, "circle")` names ≥1 cell and ≥1 episode, all
of them exclusively circle's (checked against square's and triangle's `why()`: zero overlap in cells or
episodes); `why(org, ledgers, ep, "hexagon")` (never shown) returns `{"cells": [], "episodes": [],
"edges": []}` exactly, no exception; `why()` with `episodes=None` still returns cells/edges, empty
episodes.
**Also fixed:** `tests/genome/_toy.py`'s `MINI_GENOME_TEXT` declared `SENSE ear letters 1`, but
`world.encode_word`'s `WORD_SLOTS` is hardcoded at 8 regardless of the genome — a 1-letter ear genome fed
a real `world.encode_word()` vector shape-mismatched on the first ear-side birth. Fixed to `letters 8`.

## B6 — PREDICT + FILE (`genome/predict.py`, `tests/genome/test_predict.py`)
Commit `bfb7ef3`. Test log: `Ran 49 tests in 10.562s — OK (expected failures=1)`. Pin before/after:
unchanged.
`Predictor(org)`: `expect()` (last sight winner's cell vector; the alive-cell mean before any winner;
zeros with none alive), `error(x_actual)` (`1-cos`, clipped [0,2]), `modulate(lr)` (`lr *
clip(0.5+3*error, 0.5, 2.0)`). `Organism.moment(x_s, x_w, lr_scale=1.0)` now returns `(S, T)` (was
`None`) and threads `lr_scale` into `_delta`'s lr — default 1.0 is exact (`x*1.0==x` in IEEE754),
confirmed byte-identical on a real life. `FILE`: `claim/route/decider/due`, all four or refused BY NAME;
`score()` grades a callable-or-plain `evidence` against a filed (never refused) row; `append_ledger`
writes `predictions.jsonl`.
**Clause I could not meet as literally stated, with the reason (RAISED, not forced):** *"200 moments of a
repeating 3-thing stream: median error of the last 50 < 0.7x the first 50."* Computed, not guessed: cells
are FIXED prototypes (machinery.py's own law — DELTA changes edge weights, never a cell vector), so a
persistence predictor's error on a JITTERED stream has a CEILING = `1 - within-thing median cosine`, a
retina+jitter property. On this toy's pool3 front over circle/square/triangle that ceiling is ≈0.75-0.80
(`test_floor_explains_the_ratio_ceiling` confirms last50 lands within 0.08 of it); the PREREG's 0.7×
bar sits below that ceiling. **Numbers:** error genuinely FALLS at all 3 seeds tried (9, 10, 11): ratios
0.704 / 0.730 / 0.899 (mean 0.778) — real, robust, `ratio<1.0` asserted and passing at every seed — but
the literal <0.7 bar does not clear on average; pinned as `@unittest.expectedFailure` (`test_bar_0_7x_
prereg_b6a`) so it reads OK either way and a future change that clears it is caught as an "unexpected
success". The canvas/GAZE glance feed (G1's own 4-glances-per-canvas feed) was tried FIRST, per the
brief's own steer, and is a dead end: median error stayed flat (~0.55-0.58) over 2,400 moments —
consecutive glances are different spatial windows of the canvas, no feature-level persistence for
`expect()` to exploit — reported once in the module docstring, not re-run as a test. The exact-repeat
run (no jitter at all) is the positive control: error → 0 after the first exposure of each thing,
confirming the mechanism itself is correct. The word-shuffled/picture-shuffled null comparison
(`test_word_shuffled_and_picture_shuffled_streams_reported`) did NOT come out clean at this toy's scale —
word-shuffled fell MORE than design at 2 of 3 seeds, and `gate_ga.bands` shows this pool3 front's
between-p95 (0.92) sits ABOVE its within-median (0.81) for these 3 shapes, an OVERLAP under gate G-a's
own amended rule — the noise is in the retina, not the predictor; reported as 9 numbers (3 seeds × 3
arms) in the test, not forced into a "nulls fall less" claim the data does not support.
**Also fixed:** `retina_dim()` hardcoded the eye side at 24 for `pool`/`hogcells` steps regardless of the
genome's own `SENSE eye` — found building a (now-abandoned) 32×32-eye canvas attempt: `RETINA pool4
unit` on a 32×32 glance crashed with a shape mismatch (retina_dim said 36, the real feature was 64). Now
takes `side` from `Genome.eye[0]`; never exercised by the pin (G4-skeleton.genome's only feature block is
`tower:`); pinned in both directions (`retina_dim(("pool4","unit"))==36` unchanged, `retina_dim((...),
side=32)==64` now correct).

## B7 — SLEEP + CYCLE (`genome/sleep.py`, `tests/genome/test_sleep.py`)
Commit `b448eda`. Test log: `Ran 9 tests in 1.662s — OK (expected failures=1)` (`Ran 58 … OK (expected
failures=2)` for the whole suite at this commit). Pin before/after: unchanged.
`sleep(org, episodes, n)`: replays the n most surprising LIVE episodes as ordinary moments (full
HEBB/DELTA/PRUNE/MERGE — `moment()`'s own law, unchanged; skips an episode the ring evicted between
ranking and replay, never an error). `cycle(org)`: **requires `"CYCLE" in org.g.declared`** — a genome
that never declares it (G1.genome, G4-skeleton.genome — the pin) always returns `False` and touches
nothing; when declared, a full merge pass (over every alive cell, not just one moment's winners) + a
matching full prune pass, once alive cells reach `grow_to * NMAX`.
**A design decision, surfaced by review before writing code, not worked around:** `_birth`'s existing
refusal (`area.n >= area.nmax`) counts cells EVER BORN; MERGE marks a cell dead (`alive[b]=0`) but never
decrements `n` — so naively "letting merge free capacity" would require REUSING a dead slot's id, and a
reused id would corrupt `questions.build_ledgers` (which unions every id's birth history forever — a
reborn id would silently inherit a retired cell's old "born on X" facts). **I did not implement id
reuse.** Instead `_birth` gained a SOFT ceiling, gated strictly by `"CYCLE" in declared`: refuse once
ALIVE cells (not ever-born) hit `grow_to*NMAX`. MERGE lowers alive count without touching `area.n`, so
`cycle()`'s merge pass reopens the gate and growth resumes with FRESH, never-reused ids — the array's
real NMAX is still the only hard, one-shot-per-id ceiling, unchanged.
**CYCLE toy numbers:** NMAX=30, grow_to=0.9 (ceiling 27). Feeding near-identical (2% noise) vectors: 26
ticks reach `total_cells()==27` (the ceiling, exactly); **0 further births for 5 more ticks**
(`births_refused_nmax` +5, `total_cells()` unchanged at 27) — `cycle()` returns `True`, merges 25 of the
27 sight cells away (`cells_merged_sight` +25, `total_cells()` drops to 2), and the very next tick births
again (`total_cells()` → 3). `cycle()` returns `False` when `"CYCLE"` is not declared, and `False` again
when declared but below the ceiling (0 cells).
**Clause I could not meet as literally stated, with the reason (RAISED, not forced):** *"a two-arrival
life keeps arrival-1 retention within 5pp with sleep every 200 moments replaying 50, and loses ≥10pp
without."* Built on `world.stream` at 24×24 (not the glance feed — B5/B7's own stream side per the
brief), the best-separated pair of `world.THINGS_10` under this toy's pool3 retina (`gate_ga.bands`: 45
pairs checked; "circle"/"square", tried first, are NEARLY INSEPARABLE under pool3 — within-median 0.844
vs between-median 0.840, gap 0.004 — dropped before any life ran; "ring"/"dot" has the widest gap, 0.371).
Arrival 1 (A = ring/dot, 80/thing) reaches Q1=1.0 cleanly in both arms (both confirmed ≥0.95 by
`test_a_separates_cleanly_…`). Arrival 2 (B = square/bar, 80/thing) with SLEEP OFF **loses 70pp**
(comfortably clears the PREREG's ≥10pp bar — `test_without_sleep_loses_at_least_10pp` passes). With
SLEEP ON (every 50 moments, replay 30) the loss drops to **47.5pp** — a real, monotonic,ROBUST effect:
three schedules tried (every 100/replay 20 → 57.5pp; every 50/replay 30 → 47.5pp; every 30/replay 25 →
30.0pp), more/more-frequent replay ALWAYS reduced the loss further, asserted and passing
(`test_sleep_reduces_the_forgetting`). The literal "within 5pp" bar does not clear at this toy's scale —
pinned `@unittest.expectedFailure` (`test_with_sleep_within_5pp_prereg_b7`). Likely cause, consistent
with B6's ceiling finding: the pool3 front is far cruder than the sealed eye tower the real creature
uses, and cross-arrival interference (B's new sight cells competing for word-side answers) is a real,
structural cost that replaying A's old episodes alone — without also down-weighting B's new interfering
edges — cannot fully undo in one consolidation schedule at 200-ish total moments.

## Summary of what I could not meet, in one place
Two clauses, both experimentally CONFIRMED as representation-ceiling effects (not bugs, not silently
softened), both pinned as `@unittest.expectedFailure` with the exact numbers in the test docstrings so a
future change to the retina/toy scale that clears them is caught as an "unexpected success":
1. **B6(a)**: 200-moment repeating-stream predictor error ratio < 0.7× — measured mean 0.778 over 3 seeds
   (ceiling ≈0.75-0.80, computed from `1 - within-thing median cosine`).
2. **B7**: two-arrival retention within 5pp WITH sleep — measured 47.5pp (down from 70pp without sleep;
   direction and monotonicity both robust, magnitude short of the bar).
Every other clause in B0–B7 was met and is covered by a passing test.

---

# B8 — the two toys re-specified on the creature's own front (PREREG §9 Amendment 1)

*edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 23:55 +0400. Worktree fast-forwarded to master
`a023ded` (which merged `g4-genes`), continuing on branch `g4-genes`. B0–B7's readings above are
unchanged and NOT re-graded — Amendment 1 (`docs/G4-PREREG.md` §9) says so explicitly: "these readings
stand." B8 adds two NEW test files beside them, on the creature's real front. Commit `2f3bac4`. Full
suite: **`Ran 63 tests in ~38s — OK (skipped=1, expected failures=3)`**, reproduced twice, byte-identical
pass/fail pattern both times. **The pin held throughout** (`test_pin_skeleton`, part of every run,
unchanged: `d4b5c6b8d5…`).

## The front, and which "one glance" I used
Both toys use `G4-skeleton.genome`'s real, calibrated RETINA (`thresh0.25 centre tower:eye-tower-g2
sqrt unit`, THETA_N=0.955, THETA_M=0.9975 — gate G-a's own numbers on this exact front) over 32×32
glances of `world.render_canvas` canvases at 128 (G1's world) — never the pool3/plain-render fronts
B6/B7 used. Amendment 1 offered two ways to make "one glance per showing": the whole canvas resized to
32×32 (`gaze.py`'s mode "one"), or the first surprise fixation. **I tried "one" first and rejected it**:
`gate_ga.bands_feats` on circle/square/triangle's whole-canvas features read within-median 0.9934 vs
between-p95 0.9950 — an OVERLAP (shrinking the WHOLE 128px canvas to 32px shrinks the 32px thing itself
to ~8px, losing exactly the detail the sealed tower needs). **I used the first surprise fixation
instead** (`gaze.glances(rgb, spec, gaze_gene, "surprise", pic_id)["feats"][0]`) — no overlap, see below.

## B8(1) — MODULATION toy (`tests/genome/test_b8_modulation.py`)
Test log (this file alone): `Ran 4 tests — OK (expected failures=1)`. Pin before/after: unchanged.

**F, computed first, gate G-a's bands on this world+front (first-fixation features, 40/thing, circle/
square/triangle, seed 100):** within-median **0.9690**, within-p5 0.8882, within-p95 0.9947;
between-median 0.8756, between-p95 **0.9540**, max 0.9682. **Within-median (0.9690) > between-p95
(0.9540) — NO OVERLAP.** **F = 1 − 0.9690 = 0.0310.**

**Exact-repeat control (positive control, PASS, 3/3 seeds):** with zero jitter, error reaches exactly
0.0 within the first few moments of each thing — well under F+0.01 = 0.0410, at all of seeds 9/10/11.

**Null (picture order AND word labels shuffled TOGETHER, one arm, both perturbations at once — read
that way from "the picture-AND-word-shuffled null"):** does not clear the bar at any seed (0/3),
asserted `< 2` (not a majority) — PASS.

**The design bar itself — RAISED, `expectedFailure`, 0/3 (not a majority):**
| seed | first50 | last50 | last50−F | 0.3×(first50−F) | clears? |
|---|---|---|---|---|---|
| 9  | 0.0317 | 0.0484 | 0.0174 | 0.0002 | no |
| 10 | 0.0532 | 0.0426 | 0.0116 | 0.0067 | no |
| 11 | 0.0236 | 0.0473 | 0.0163 | −0.0022 | no |

**Why, computed not guessed:** a single-canvas trace (seed 9) makes the shape visible —
`[1.000, 0.048, 0.009, 0.003, 0.005, 0.062, 0.012, 0.003, 0.025, …]` — moment 0 is the organism's
very first prediction ever (no cells exist, `expect()`→zeros, cos=0, e=1.0 by construction), and moment
1 *already* reads 0.048, close to F=0.0310. Because the sealed tower is this good on this world,
first50's median (0.0236–0.0532 across seeds) is *already* near F — seed 11 even reads BELOW F, a
50-sample median-noise artifact around a true gap close to zero. The bar `(last50−F) ≤ 0.3×(first50−F)`
implicitly assumes real headroom between first50 and F for a learning curve to close; here there is
almost none left to measure. This is a DIFFERENT shape of finding than B6(a)'s pool3 reading (there:
front too WEAK, ceiling above the bar; here: front so strong the window opens after convergence already
happened).

## B8(2) — SLEEP toy (`tests/genome/test_b8_sleep.py`)
Test log (this file alone): `Ran 1 test — OK (skipped=1)`. Pin before/after: unchanged.

**A/B, computed and named** (gate G-a's bands, this front, first-fixation features, 40/thing, all of
`world.THINGS_11`, ranked by within-median minus between-median gap): top four pairs were
square/dot (0.420), circle/dot (0.401), ring/dot (0.397), dot/diamond (0.391) — all four share "dot", a
small simple mark unlike everything else on this front. The next pair DISJOINT from square/dot is
ring/bar (0.309). **A = [square, dot]. B = [ring, bar].**

**The no-sleep loss, measured FIRST as instructed, at three independent dev-seed pairs (held-out fixed
at seed=2, `world.holdout_canvas`, as specified):**
| dev_A seed | dev_B seed | Q1 base | Q1 final | loss (pp) |
|---|---|---|---|---|
| 1  | 2  | 0.875 | 0.875 | 0.0 |
| 5  | 6  | 0.900 | 0.900 | 0.0 |
| 11 | 12 | 0.900 | 0.900 | 0.0 |

**Max loss over all three: 0.0 pp — well under the 10pp bar. NOT GRADABLE on this world**, per Amendment
1's own words ("the G0b machinery retains without sleep: budget per arrival, no disuse decay — G0b (v)
read +0"): my measurement confirms this exactly, at every seed pair tried, with zero exceptions. Skipped
via `unittest.SkipTest` carrying the full readings table above (not just "not gradable" — the actual
numbers), never manufactured. Since the loss never reached ≥10pp, the "ceiling = share of A's held-out
answered by cells the replayed episodes light" computation was never needed (the amendment's branch for
that only applies when the mark IS gradable). SLEEP's retention mark lives only in the 24h life's
alternating windows (PREREG §5 TWINS no-sleep) — not reachable in a toy this short.

**CYCLE's toy** (B7, `tests/genome/test_sleep.py::TestCycle`) stands as PASS unchanged, per Amendment 1's
own instruction — not rerun: 27 = 0.9·30 reached, 0 births for 5 ticks, `cycle()` merges 25 sight cells,
births resume with fresh ids the very next tick.

**One fix needed to run the SLEEP toy at all (not a finding about SLEEP):** the skeleton's own
`STAGE 2 meet moments 200..` never fires within one 80-showing (160-moment) arrival — every `recall`
would read NOEDGE by construction (confirmed: Q1 read exactly 0.0 before the fix) since wiring never
starts. `tests/genome/_creature_front.py`'s `skeleton_genome_immediate_meet()` keeps every other gene
(RETINA, GAZE, BIRTH, BUDGET, NMAX, KWTA, HEBB, DELTA, PRUNE, MERGE, SCALE, RECALL, ABSTAIN — the front
and every threshold) byte-for-byte identical and moves ONLY `STAGE 2 meet` to start at moment 0. This is
an artifact of the toy's chosen LENGTH (160 moments < 200), not a property of the front or of SLEEP.

## B8 summary
Both toys ran on the creature's real, calibrated front. Both positive/negative controls behaved exactly
as required (exact-repeat control PASSES for MODULATION; the null does not clear MODULATION's bar; the
no-sleep loss for SLEEP was measured plainly and found genuinely under 10pp, not forced either way).
Neither literal bar clears on this front — MODULATION for a front-too-strong reason (opposite of B6(a)'s
front-too-weak reason), SLEEP because the mark is honestly NOT GRADABLE on this world at this toy's
scale. Both are reported with every number, pinned so a future change is caught in either direction
(`expectedFailure` for MODULATION's bar; a `self.fail(...)` sentinel in SLEEP's test for if the loss ever
does reach ≥10pp, forcing that test to be rewritten with the ceiling-relative bar rather than silently
staying skipped). The pin never moved.

# WAVE 2 — B9–B13 (docs/G4-PREREG.md §10 Amendment 2, §11)

*edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 23:10 +0400. Worktree fast-forwarded to master
`0cb21f7` (§10 Amendment 2 + §11's Wave 2 spec, merging B8), continuing on branch `g4-genes`. Same rules
and ownership as before; the standing safety constraint held throughout: `/data/dev/genome/run` (the
live `creature.service`, running since 22:29) was never touched, `systemctl` was never run — every test
in this wave builds its own temporary `Organism`/genome in-process, nothing reads or writes the live
tree. HEAD after B13: `6eb291b`; HEAD after a post-review fix pass (below): `b001009`. Full suite
(`python3 -m unittest discover -s tests/genome -t .`) at `b001009`:
**`Ran 121 tests in ~100s — OK (skipped=1, expected failures=7)`**, run twice, byte-identical pass/fail
pattern both times. **The pin held at every commit** (`test_pin_skeleton`, part of every run, unchanged:
`d4b5c6b8d5…`).

## B9 — the three parser genes (`genome/machinery.py`, `tests/genome/test_parse_g4_wave2.py`)
Commit `b252759`. Test log (this file alone): `Ran 5 tests — OK`.

Three strict `re.fullmatch` clauses added to `parse_genome`, the interface fixed for Builder A:
`THINK every <n> canvases` → `declared["THINK"] == {"every": int}`; `EXAM every <n> canvases` →
`declared["EXAM"] == {"every": int}`; `FROZEN after <n> cells` → `declared["FROZEN"] == {"after": int}`.
Parsed only — nothing wired into `Organism` (`FROZEN` is a twin-only gene per §11.1 step 5;
`Organism.__init__`'s existing `frozen_after` kwarg is untouched, read by the mind, not by the parser).
Neither gene touches `self.c`; neither is in `required`; `G4-skeleton.genome` never declares any of the
three, confirmed directly (`test_undeclared_means_absent`) and at full-suite scale (the pin, unchanged).

## B10 — CURIOSITY (`genome/curiosity.py`, `tests/genome/test_curiosity.py`)
Commit `9645fdc`. Test log (this file alone): `Ran 16 tests — OK`.

`Interests(n, rng)`: `choose(pool, rng)` returns the highest-weight item (ties by `rng`, an unseen item
born at weight 1.0); `update(item, outcome)` implements the four named operators — `"answered"` →
generalize (+0.5 to every tracked item sharing that KIND, population-wide); `"parked"` → specialize
(×0.5 on that one item); a new item whose key matches an already-known `"word"`-kind key → bridge
(+0.25, applied at birth inside `choose`/`_weight_of`, not inside `update`); two items answered in the
same sleep window → recombine (their weights set to the mean) — `sleep_boundary()` is a new method the
mind calls once per SLEEP tick to close a window, so recombine only pairs answers within the SAME
window. `"filed"`/`"scored"` carry no operator in the PREREG text and are accepted as documented no-ops
(counted in `state()`, no weight change). `n` is read as a soft population cap (prune the lowest-weight
entries beyond `n` after each `update`; no decay, per the PREREG). `choose_uniform(pool, rng)` is the
free-function null twin.

**The toy (§11.2), 3 seeds, a pool of 2 answerable (`"word"`-kind) + 8 park-only (`"sight"`-kind)
items, 50 choices:**
| seed | real (word picks/50) | null (word picks/50) | ratio |
|---|---|---|---|
| 9  | 46 | 7 | 6.57x |
| 10 | 47 | 9 | 5.22x |
| 11 | 50 | 9 | 5.56x |

Pooled: real 143/150, null 25/150, ratio **5.72x** — every seed and the pooled ratio clear the ≥3x bar
comfortably.

## B11 — THINK's laws (`genome/think.py`, `tests/genome/test_think.py`)
Commit `d98c252`. Test log (this file alone): `Ran 11 tests — OK`.

`believe(word, cells, episode_ids, moment, path)` appends one row to `beliefs.jsonl` (append-only).
`clash(new_row, old_rows, path)`: two belief rows about the SAME word with DISJOINT `"cells"` sets open
a new `"clash"` row naming both rows' line numbers (never overwriting either); overlapping cells are not
a clash (read as the same underlying belief, extended). `induce(episodes, k, org)`: for each word the
organism itself resonates a word-cell for (via `org.recall`, no external ledger — the interface passes
only `episodes`/`k`/`org`), cluster C = the alive sight cells whose strongest word edge
(`Organism._answer_of`) IS that word cell; a rule fires when ≥k episodes' raw-nearest sight cell (by
cosine, not RECALL's abstain-aware path) lands in C and none disagrees — returned FILE-ready.
`deduce(beliefs)`: two DIFFERENT-word beliefs sharing a cell predict a co-resonance, routed at that
cell; two SAME-word beliefs with DISJOINT cells (exactly `clash`'s own condition) are UNROUTABLE — no
single cell names the route — filed with `route=""`, REFUSED BY NAME.

**The three required toys, all first-try green:**
- **induce, planted rule + counter-example:** 8 "zog" + 8 "bar" training moments (distinct sight
  clusters), then 4 agreeing "zog" episodes → rule found (`agree=4, disagree=0, accepted=True`). A 5th
  episode labelled "zog" but drawn from "bar"'s trained cluster → **0 rules** (the counter-example
  blocks it, `disagree>0` refuses induction — "no counter" honored literally).
- **clash, planted contradiction:** two "zog" beliefs, cells `[1,2]` and `[7,8]` (disjoint) →
  `clash()` returns a row, `kind="clash"`, `clashes=[0,1]`; reading the file back shows all 3 rows —
  both original belief rows byte-identical to what `believe()` wrote, never touched. Overlapping cells
  (`[1,2,3]`/`[3,4]`) → `clash()` returns `None`.
- **deduce, unroutable refused by name:** "zog"`[1,2]` + "bar"`[2,3]` (shared cell 2, different words)
  → accepted, `route="recall(sight) at cell 2"`. "zog"`[1,2]` + "zog"`[7,8]` (disjoint, same word) →
  **refused**, `refused=["route"]`, `row["route"]==""`.

## B12 — TRAITS (`genome/traits.py`, `genome/machinery.py`'s `Area.cos`, `genome/fast.py`'s `x_s2`,
`tests/genome/test_traits.py`)
Commit `5d91547` (+ the `org.traits` property fix, `b001009`). Test log (this file alone, after the
fix): `Ran 19 tests — OK (expected failures=2)`.

`Traits(dim_in=112, dim_out=32, lr, rng)`: `H` (dim_out×dim_in) is a seeded random orthogonal
projection at birth (QR-derived, rows orthonormal); `apply(x)` = `H@x` raw; `learn(episodes,
steps<=20)` runs a hand-derived InfoNCE gradient (same-canvas glances near, other canvases far,
τ=0.1 fixed) over the most recent ≤256 episodes carrying a second glance, bumping `version` once per
call that actually stepped. `genome/fast.py`'s `Episodes.write` gained an optional `x_s2=None` +
`has_s2` mask (save/load carry both; old saved files without them still load; nothing else reads it —
kept out of the pin automatically, Episodes is never hashed). `genome/machinery.py`'s `Area` gained a
`traits` attribute (`None` by default, words area never gets one — a "sight-only contrast head"
decision, documented in `genome/traits.py`'s module docstring); `Organism` exposes this as a `traits`
**property** (getter/setter reaching `self.sight.traits`, not just a `set_traits()` method) —
**an advisor review caught that the coordinator's fixed interface names it `org.traits` verbatim, and
Builder A codes against that exact name in parallel; without the property, `org.traits = t` would have
silently created a dead plain attribute while `Area.cos` kept reading the untouched `None` off
`self.sight.traits` — TRAITS would have been a live no-op with every other link green.** Fixed same
commit (`b001009`), 3 new tests confirm `org.traits`/`org.set_traits()`/`org.sight.traits` are all one
fact. `Area.cos`'s untouched two-line path runs when `traits is None` (the pin's own path, byte-
identical); when set, `cos(H·cell, H·x)` is computed with `H·cells` cached and invalidated by
`(n, traits.version)`. `_misfire`/`_merge` keep reading raw dots — a documented choice, not silent.

**Toy (a), 3-thing drawn world (circle/square/triangle, tower front, 40/thing):**
RAW margin (within-median − between-p95) = **0.0091**. After ONE sleep (≤20 steps): margin **0.0691**
(**7.6× raw** — PASSES, the mechanism works). After the PREREG's literal "5 sleeps" (5×`learn(steps=20)`
= 100 gradient steps on the SAME 120-canvas/3-class batch): margin **−0.1161**, WORSE than raw —
**RAISED**, `expectedFailure` (`test_bar_margin_after_5_sleeps_ge_raw_prereg_b12a`). Why, measured not
guessed: InfoNCE's true training objective is canvas-INSTANCE discrimination (tell THIS canvas's pair
apart from every OTHER canvas, same-thing negatives included) — at a mild dose it incidentally helps
thing-level clustering too, but on a small (120-canvas, 3-class) batch, over-training collapses within-
thing cohesion as the head specializes toward telling individual canvases apart. The single-sleep
positive result is kept on the record in its own passing test
(`test_single_sleep_clears_the_bar_by_a_wide_margin`).

**Also reported, never gated (PREREG's own instruction) — the SAME toy-trained (single-sleep) head
applied to 200 real Caltech photographs** (10 word folders under `/data/dev/genome/world/<word>/` —
anchor/ant/barrel/bass/beaver/bonsai/brain/buddha/camera/cannon, 20 images/word; the master tree, read
only, never written): BEFORE (raw front) margin **−0.0897** (the raw front itself already overlaps on
real photos — within-median 0.8283, between-p95 0.9181); AFTER (toy-world-trained head) margin
**−0.2915** — no generalization from synthetic line-drawings to real images. Both numbers on the
record, no pass/fail asserted on their relationship.

**Toy (b), the identity control.** `dim_out==dim_in==112`, `H=I`: `Area.cos` matches raw (untraited)
cosine to float64 precision (`atol=1e-9`) — **PASSES**
(`test_identity_control_dim_out_eq_dim_in_prereg_b12b`). The PREREG's own literal sentence — *"H = I
(first 32 rows) reproduces raw cos exactly"* — is **RAISED**, `expectedFailure`
(`test_first_32_rows_literal_prereg_text_cannot_reproduce_raw_cos`): measured max|diff| **0.2383**, far
outside float precision — a 112→32 coordinate-DROPPING projection cannot reproduce a cosine that depends
on all 112 dimensions, by construction; the clause is only true when `dim_out == dim_in`.

**Toy (c), the pin control.** TRAITS undeclared → `Area.cos` byte-identical — confirmed directly
(`test_untraited_area_cos_is_the_old_two_lines`, `test_organism_never_calling_set_traits_leaves_sight_
traits_none`) and at full-suite scale (`test_pin_skeleton`, unchanged, run after every commit in this
wave). PASSES.

## B13 — MODULATION at arrival (`tests/genome/test_b13_modulation_arrival.py`, PREREG §10 Amendment 2)
Commit `6eb291b`, revised at `b001009` after an advisor review caught two instrument defects (below).
Test log (this file alone, current): `Ran 7 tests — OK (expected failures=2)`.

Stream: circle/square/triangle, 50 SHUFFLED/jittered showings each (150 total, the "previous window");
then moon/house (`world.THINGS_ARRIVAL2[:2]`) interleaved, 15 showings each (30 total, the arrival); a
no-new-things null (3 more old-thing showings ×10, 30 total); 3 seeds (9/10/11).

**Two defects an advisor review found in the first version, both fixed:**
1. *Null-arm contamination.* The null arm was originally fed the SAME `(Organism, Predictor)` as the
   real arm, AFTER the real arm's window had already shown moon/house — its predictor's "last winner"
   was a new-thing cell going into the null window, an artifact, not a clean "no new things" measurement.
   **Fixed:** the null arm now runs on its own fresh `(Organism, Predictor)` pair, fed the IDENTICAL w1
   stream (deterministic replay) before `w2_null` — a new test
   (`test_baselines_are_byte_identical_across_the_two_arms`) asserts the two arms' last-50 medians match
   exactly, at every seed. The null numbers moved (below); the real arm's spike/settle numbers did NOT
   move (they were never contaminated — the real arm ran first in the original code too).
2. *The wrong ceiling.* The first version computed the ceiling as `1 − between-p95` pooled over ALL
   FIVE things' pairwise combinations — dominated by whichever pair reads highest whether or not it
   involves a new thing at all. **Fixed** to the PREREG's own two-part instruction: `ceiling_bands` =
   `1 − ` the WORST (highest) p95 among OLD-vs-NEW pairs only (never old-old or new-new); `ceiling_direct`
   = the PREREG's literal per-instance definition, measured LIVE at each new thing's actual arrival
   (`1 − max(cos to every currently-alive sight cell)`, captured before that showing can birth/wire
   anything). Both printed beside F; the bar itself uses `ceiling_bands`, per the PREREG's literal
   "printed from the gate's bands" wording.

**F and the ceiling, measured first (gate G-a's bands, this front, this world, printed beside every
bar):** F = **0.0310** (circle/square/triangle within-median 0.9690, same reading as B8's). Old-vs-new
pair p95s: circle/moon 0.7263, circle/house 0.9514, square/moon 0.7428, square/house **0.9515** (the
worst), triangle/moon 0.8181, triangle/house 0.9169 — **`ceiling_bands` = 1 − 0.9515 = 0.0485**.
**`ceiling_bands` (0.0485) < 3×F (0.0930)** — exactly the case the PREREG's own text names: the bar is
reported against the ceiling ratio (0.0485/0.0310 = **1.56×**), not the literal 3×.
**`ceiling_direct`, measured live, is thing-SPECIFIC** (a diagnostic finding, not used to pick a
per-thing bar): moon reads **0.195/0.252/0.217** across the three seeds (genuinely novel-looking to this
front — nothing like an old thing), house reads **0.067/0.053/0.056** (closely tracking `ceiling_bands`,
confirming house is the pair driving that pooled worst case).

**Measured at 3 seeds × 2 new things = 6 (seed, thing) pairs (real-arm numbers unchanged by the fix):**
| seed | thing | spike (vs last-50 median) | vs 1.56× ceiling-ratio | e at showing 10 | settled (<F+0.05=0.0810)? |
|---|---|---|---|---|---|
| 9  | moon  | 1.818× | clears | 0.3601 | no |
| 9  | house | 1.761× | clears | 0.1956 | no |
| 10 | moon  | 2.650× | clears | 0.0549 | **yes** |
| 10 | house | 1.971× | clears | 0.0144 | **yes** |
| 11 | moon  | 0.595× | **misses** | 0.0793 | yes (barely) |
| 11 | house | 2.415× | clears | 0.2821 | no |

- **spike ≥ ceiling-ratio (1.56×): 5/6 — a majority — PASSES**
  (`test_spike_vs_ceiling_majority_clears`). None of the 6 pairs reach the literal 3× (max 2.65×),
  confirming the PREREG's own prediction that the ceiling, not 3×, is this front's real bar. (Unchanged
  from the flawed 1.68× ratio — the corrected, smaller 1.56× does not flip any of the 6 verdicts.)
- **settle (<F+0.05 by the thing's 10th showing): EXACTLY 3/6 — a TIE, not a majority — RAISED**,
  `expectedFailure` (`test_settle_under_F_plus_005_within_10_showings`).
- **the PREREG's own conjunctive bar (spike-vs-ceiling AND settle): 2/6 (seed 10's two new things
  only) — not a majority — RAISED**, `expectedFailure` (`test_conjunctive_bar_prereg_b13`).
- **no-new-things null (<1.5×), at 3 seeds, DECONTAMINATED:** seed 9 **1.547×** (misses, barely — just
  above 1.5), seed 10 **0.516×** (clears), seed 11 **0.752×** (clears). **2/3 — a majority — PASSES**
  (`test_null_majority_under_1_5x`). These numbers moved from the contaminated first version
  (1.674/1.131/0.557), but the majority verdict is unchanged, and seed 9's miss PERSISTS after
  decontamination — confirming it is genuine baseline noise (the shuffled-old-things baseline is itself
  noisy enough to occasionally read as its own "spike" with no arrival at all), not the contamination
  artifact.

**Stream design decision, and its consequence, owned rather than hidden (module docstring has the
full paragraph):** the old-things phase is fully SHUFFLED (not per-thing blocks), so "the previous
window's last-50 median" reflects the ordinary noise of a mind that keeps mispredicting whenever the
stream switches thing-identity mid-window — last50_med reads ~0.09–0.11 (≈3×F) under this choice. Under
a BLOCKED old-things phase instead (same-thing runs, as B8's toy used), last50_med would sit near F
(B8 measured 0.043–0.048 under blocking on this exact front/world), and the SAME new-thing first-3
errors (~0.18–0.24, independent of window-1 ordering) would read roughly 4–6× that baseline instead of
~2×. **This was NOT re-run under blocking to chase a cleaner number — that would be config-shopping.**
The finding to carry forward: the spike verdict is sensitive to the window-1 ordering rule, which
belongs to Builder A's `world_maker.py` (the maker schedules real arrivals) — the PREREG should say
which ordering the live maker uses before this mark is read off the live 24h life.

## WAVE 2 summary
All three new genes parse and stay pin-safe (B9). CURIOSITY's toy clears its bar cleanly at every seed
(B10, 5.2–6.6× vs the ≥3× bar). THINK's three required toys all pass first-try, with genuine planted
positives and negatives (B11). TRAITS (B12) is a real, working mechanism — the identity control passes
exactly, and a single sleep lifts the toy-world margin 7.6× — but the PREREG's literal "5 sleeps" and
literal "first 32 rows" clauses are both RAISED with measured, non-trivial evidence (the first an
honest overfitting finding on a small toy, the second a dimensional impossibility the PREREG's own text
cannot satisfy for dim_out<dim_in); the photograph report shows no generalization from drawn shapes to
real images, recorded without gating. B13's re-specified MODULATION mark partially clears (the
spike-vs-ceiling and no-new-things-null components each pass their own bar on a majority of seeds, after
a post-review fix corrected a contaminated null and a mis-scoped ceiling — see B13's own section for
both defects and their measured before/after numbers) but the settle requirement and the PREREG's own
conjunctive "AND" do not reach majority on this small (6-trial) toy — both RAISED with every number.
Nothing here was forced, tuned after the fact, or silently rounded toward a pass; every RAISED clause
carries its measured numbers in the test's own docstring so a later change is judged against the same
evidence. The pin (`d4b5c6b8d5…`) held at every single commit across all five tasks plus the post-review
fix pass, confirmed by two full, byte-identical suite runs at HEAD (`b001009`):
**`Ran 121 tests in ~100s — OK (skipped=1, expected failures=7)`**.

## Three notes for the coordinator (not fixed here — outside this wave's interface, or another
builder's territory; flagged rather than silently left)
1. **`genome/traits.py`'s `Traits` has no `save`/`load`.** Builder A's mind snapshot (§11.1 step 1 saves
   the predictor's state) will need to persist `H` (and `version`) too, or a resumed life's TRAITS head
   is reborn random every restart — silently discarding every sleep's learning. Not this wave's
   interface (`learn`/`apply`/`H` were the only three named), but worth a line in whichever brief covers
   the snapshot/resume path.
2. **`/data/dev/genome/world/ahmad/` exists** (6 images) alongside the ten Caltech folders — presumably
   "his six" the PREREG references elsewhere. One folder of 6 cannot yield a between-thing band on its
   own (no second class to compare against), so B12's photograph report used only the ten Caltech words;
   `ahmad/` was read (confirmed present) but not included in any measurement, rather than silently
   omitted without comment.
3. **B13's spike verdict depends on the maker's within-window ordering rule** (shuffled vs. blocked —
   see B13's own section): this toy chose shuffled and reported the consequence; the live 24h life's
   real arrival mark should be read against whichever rule `creature/world_maker.py` actually uses.
