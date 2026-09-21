# Builder J (Sonnet 5) report — BIND, colour, the retina adopted
*edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:31 +0400, corrected 2026-09-21 21:56 +0400 (advisor-caught: the reversed-ordering finding was measured but unstated; a fabricated §7 baseline number; two wrong citations — see the diffs below and §6.6). Brief: `docs/briefs/G5-J-BIND-COLOUR-RETINA.md`. Branch `g5-bind-colour`, worktree `/data/dev/genome-wt-n`.*

## 0 · In five lines
1. **BIND** (`BIND glances per canvas`): the four glances of one canvas are MEAN-pooled into one unit-renormalised vector before `org.moment()`/`org.moment_sight()` — one moment per canvas instead of four. Measured on a real 600-canvas slice of life 2's tape: births fall 181 → 60 (≈3×) and the mind's own per-canvas cost *drops* 44.58 → 36.68 ms (fewer resonate/hebb/delta/misfire/prune/merge cycles). **Q1 (all 16 words): BIND 0.9625 vs the first-fixation twin's 0.98125 — FAILS the bar as pre-registered.** A diagnostic (§2) found the pre-registered exam itself feeds a shape (4 raw glances into `recall_many`) the BIND-trained organism never produced at wake; re-read the SAME held-out canvases through the pooling BIND actually trained on and Q1 rises to **0.9750 — one held-out answer (156 vs 157 of 160) under the bar.** Reported as FAIL either way, never loosened — §2 has both numbers and the full reasoning.
2. **SENSE colour** (`SENSE colour rg by 4x4 under the glance fixed-gain`): reproduces Researcher G's exact measured numbers through THIS branch's own production wiring (`genome.gaze.glances(colour=...)`), not a copy of her formula — **grey −0.107 → colour +0.046** on BabyAI POV, bit-for-bit the numbers in `REPORT-G5-G.md` §3.6. Grey/maker-world exactness: `max|rg| = max|by| = 0.0` EXACTLY, and the tower's own 112 numbers are byte-identical with colour on or off (the outer unit-step is a true no-op on a zero colour block).
3. **RETINA adopted, silently** (no new genome syntax): `genome/retina_fast.py` (F's module, copied verbatim from `g5-repairs`) is wired into `genome/gaze.py`'s `organs()`/`_analyse_frame()` behind a third sha-pin. Byte-identical on **every eye canvas of life 3a's real tape (2338/2338)**.
4. **BIND changes what a "moment" is.** `org.t` advances once per canvas instead of once per `GAZE.fixations` (4) — every moment-denominated gene's cadence in canvas/wall-clock terms changes by the same factor. Full table in §3; **`SLEEP` MUST be re-expressed (2000→500) or the ALIVE gate fails by construction** (2.8 h between sleeps vs the 1 h bar).
5. Colour and retina both PASS their bars cleanly; BIND's own measured effect (≈3× fewer spurious births, a real cost reduction) is exactly what F's diagnosis predicted, but its pre-registered Q1 bar is a FAIL, reported as measured. **A finding beyond the pre-registered bar (§2, §6.6): on the SAME correct-commit exam, `unbound` (4 raw glances/canvas) reads 0.9875 — ABOVE first-fixation's 0.98125, not below it.** EYE.md/G5-DESIGN.md cite "first-fixation 0.975 > 4-fixation 0.956" (a 1.9 pp cost for extra glances) as BIND's own premise; under the commit life 2 actually ran on, that ordering reverses. The two arms are not a clean glance-count test (`unbound` also runs 4× the moments and 39 sleeps vs 9), so this does not by itself refute G-EYE-2 — but the cited 1.9 pp cost does not reproduce, and that bears on the ship/hold decision. Six things are raised in §6 for the orchestrator's decision — the headline one is whether to ship BIND on its other merits pending an exam-road fix, none of them a defect in this branch's own code.

---

## 1 · The BIND rule, why, and its cost

**The rule (EYE.md §4 G-EYE-2 + F's diagnostic, `/data/dev/genome-wt-k/docs/briefs/G5-F-REPORT.md` §1):** for each canvas, take the `F` per-glance 112- (or 144-, with colour) dimensional feature vectors `gaze.glances()` already computes, **mean them, then re-normalise to unit length** (`creature/mind.py:_bind_pool`), and feed the organism that ONE vector via a single `Organism.moment()`/`moment_sight()` call instead of `F` separate calls.

**Why mean, not max or "glance 0 only":** F's diagnostic is explicit that the signal is **glance INDEX, not glance CONTENT** — 87.3% of the extra glance-1–3 births are themselves ON the thing (not clutter), and glance 0 is not privileged (22.3% of all sight births are already on glance 0, many of which never misfire). The gap F found (27.9% vs 17.3% ever-misfire; 32.9% vs 17.9% cross-thing edges, split by glance index) says "several looks at the SAME correctly-fixated object keep birthing new, less-reliable cells instead of reinforcing one shared percept" — i.e. EYE.md §1.3's *"one object, several fixations, ONE percept"* (transsaccadic integration). A mean treats every glance as an equally real, already-computed look at the same thing; discarding three of the four (max/first-only) would throw away real information the diagnostic never said was bad.

**Why re-normalise:** `Organism.cos()` (`genome/machinery.py:451`, the `self.traits is None` branch) is a **raw dot product** against unit-norm stored cells (`c = self.cells[:self.n] @ x`) — not a normalised cosine. Every `Area.cells` row is unit length by construction (born directly from a `RETINA …unit`-terminated vector, or from this pooled one). A non-unit pooled query would (a) silently rescale every `THETA_N`/`ABSTAIN` comparison for that moment and (b) permanently corrupt the newborn cell's OWN stored vector norm — the same shape of defect as SOLUTIONS #231(1) (an un-normalised quantity treated as if it already were), just on a pooled vector instead of an ink rule.

**What it changes for BIRTH, measured directly** (this branch's own code, a real 600-canvas / 1200-row slice of life 2's tape — `scratch/time_bind.py`, results in §5):

| | UNBOUND (today) | BIND |
|---|---|---|
| org.moment/moment_sight calls over 600 canvases | 2,400 | 600 |
| org.t after 600 canvases (+ 1 sleep firing crossing the 2000 boundary under UNBOUND, 0 under BIND) | 2,600 | 600 |
| total births | 181 | **60 (≈3× fewer)** |
| cells [sight, words] | [157, 11] | [46, 11] |
| mind cost | 44.578 ms/canvas | **36.679 ms/canvas (−17.7%)** |

Fewer births is the direct, expected effect of collapsing four resonance/birth opportunities into one per canvas — the same mechanism F's diagnostic named as the source of the 1.9 pp Q1 gap (77.5% of all sight births come from glances 1–3). The cost DROP (not a rise) is because the dominant per-canvas cost in this branch's `_consume_eye` is `Organism.state_hash()` (called once per canvas either way, unaffected by BIND — F's `g5-repairs` state_hash repair is NOT part of this branch/brief and was not adopted here, so this cost sits on the OLD, un-repaired algorithm, ≈35 ms/canvas by F's own measurement) plus the retina/gaze cost (also unaffected by BIND — the SAME 4 glances are computed either way); BIND removes only the `_resonate`/`_hebb`/`_delta`/`_misfire`/`_prune`/`_merge` work, which is real but a minority of the per-canvas total. **Raised for the orchestrator:** adopting F's state_hash repair (branch `g5-repairs`, not this brief's job) would very likely dominate any further per-canvas cost conversation more than BIND does.

**The same cost picture, confirmed on the full life-2 tape** (§2's three-arm replay, `uptime` load average ≈ 5.8–6.7 during the replay window — four builders sharing this box, not a solo reading; load ran 2.3–3.6 outside that window):

| arm | ms/canvas @2,000 canvases | @8,000 | @16,000 | final (17,768) | final cells alive [sight,words] |
|---|---|---|---|---|---|
| unbound | 52.34 | 57.13 | 62.35 | **63.37** | [668, 17] — keeps climbing |
| first-fixation | 40.74 | 42.38 | 44.59 | **44.94** | [269, 17] |
| BIND | 42.08 | 43.99 | 45.98 | **46.29** | [216, 17] |

`unbound`'s ms/canvas keeps climbing (52 → 57 → 60+) because it keeps accumulating cells fastest (§1's births finding, at full scale: more alive cells means a longer `Area.cos()` dot product every resonate call) — the same mechanism, at 17,768 canvases instead of 600. `first-fixation` and `BIND` are close to each other and comparatively flat because they are BOTH capped at 1 `org.moment()` call per canvas (§2, cadence-matched) and accumulate cells at similar, much slower rates.

## 2 · BIND's test — Q1 on life 2's tape under 75b0a9b's mind

**Road, per hard rule 4:** life 2's real trajectory ran under commit `75b0a9b` (F's finding, `G5-F-REPORT.md` §0 — master's PREDICT law changed 2026-09-21 11:18, after life 2 started at 2026-09-20 12:12). A detached checkout `git worktree add --detach scratch/wt-75b0a9b 75b0a9b` (never committed, never touching `/data/dev/genome`) carries the MINIMAL BIND diff (the same `BIND` parser clause in `genome/machinery.py`, the same `_bind_pool` + `org_feats` wiring in `creature/mind.py`, byte-for-byte the g5-bind-colour branch's own change — `creature/genes.py`'s `unwired()` refusal law does not exist yet at 75b0a9b, so no RUNS entry was needed there). Life 2's FULL real tape (35,536 rows, hard-link-copied via `cp -al` into `scratch/life2full/`, never touching the live run) was replayed from an EMPTY organism under THREE arms, each its own fresh run root under `scratch/wt-75b0a9b/scratch/`:

- **unbound** — life 2's own `G4.genome`, unmodified (the twin: what life 2's real code produces from scratch).
- **first-fixation** — the SAME genome with `GAZE … fixations 1` (the bar EYE.md/G5-DESIGN.md cite as "0.975").
- **bind** — the same genome + `BIND glances per canvas`.

Each arm's final organism (+ ledgers) was read by `tools/self_exam.py`'s own road (unmodified, this checkout's own copy) — `world.holdout_canvas(THINGS_11+THINGS_ARRIVAL2+…, held=10, seed=2)`, `ask_glances`. **Correction caught before quoting anything:** `self_exam.py` writes TWO Q1 readings — `ask_seen_words` (capped at `THINGS_11`, 11 words, n=110) and `ask_all_words` (`THINGS_11+THINGS_ARRIVAL2`, the full 16, n up to 160, matching EYE.md's own "160-item exam" ceiling note). My driver's first printout quoted the 11-word one by mistake; both are in every arm's saved exam JSON regardless, and every number below is the 16-word `ask_all_words` reading, exactly as the brief and the orchestrator's own message both said ("all 16 words"). This reproduces the SAME instrument that produced the 0.975/0.956 figures cited in EYE.md/G5-DESIGN.md, but run HERE, under the CORRECT commit, on MY OWN three arms, so the numbers below are directly comparable to each other (same code lineage, same exam machinery, same held-out seed) — not merely quoted from the possibly-counterfactual (per F's own §0 finding) prior verdict run.

**Cadence per arm, measured (journal rows carrying a `"sleep"` key), not estimated:**

| arm | org.t advance per canvas (from `_consume_eye`) | STAGE 2 (`t≥200`) reached at canvas | sleeps over the full tape |
|---|---|---|---|
| unbound | 4 (`GAZE fixations 4`, no BIND) | 50 | 39 (matches life 2's own real STATUS.json exactly) |
| first-fixation | 1 (`GAZE fixations 1` — only one glance EXISTS) | 200 | **9** |
| BIND | 1 (4 glances pooled into 1 `org.moment()` call) | 200 | **9** |

**first-fixation and BIND are cadence-MATCHED — both 1 moment/canvas, both reach STAGE 2 at canvas 200, both sleep 9 times over the tape — for two different reasons (one glance vs. four pooled into one).** This is what makes them the fair pair to compare (the brief's own framing: "the first-fixation twin's reading is the bar"); `unbound` differs on every one of these axes and is reported as a reference, not the bar. **Check (arithmetic, not measurement):** first-fixation/BIND's `org.t final = 19,568` = `17,768 canvases + 9 sleeps × 200 replay` exactly; `unbound`'s `org.t final = 78,872` = `4 × 17,768 + 39 × 200` exactly — both match §3's cadence-splitting formula and the table's own sleep counts, confirming the sleep counts and the `org.t` finals are mutually consistent, not independently-rounded readings.

**Q1, all 16 words (`ask_all_words`), held=10 canvases/word, seed 2:**

| arm | Q1.acc | n | correct | final ms/canvas | org.t final | cells ALIVE [sight,words] | births |
|---|---|---|---|---|---|---|---|
| unbound (life 2's own code, from scratch) | **0.9875** | 160 | 158 | 63.37 | 78,872 | [668, 17] | 717 |
| first-fixation (GAZE fixations 1) | **0.98125** | 160 | 157 | 44.94 | 19,568 | [269, 17] | 296 |
| **BIND** (pre-registered exam) | **0.9625** | 160 | 154 | 46.29 | 19,568 | [216, 17] | 244 |

**Bar (as pre-registered):** BIND's Q1 ≥ the first-fixation twin's reading. **0.9625 < 0.98125 — FAILS**, as measured, reported without loosening it.

**A finding beyond the pre-registered bar, stated plainly:** the table above also gives `unbound`'s (life 2's own real 4-glances-per-canvas code) Q1 reading — **0.9875, ABOVE first-fixation's 0.98125**, not below it. EYE.md/G5-DESIGN.md's cited premise for BIND (G-EYE-2, "first-fixation-only 0.975 > 4-fixation 0.956 — the extra glances cost 1.9 pp") does NOT reproduce under the commit life 2 actually ran on: on this exam, under 75b0a9b, the ordering is reversed (4-fixation 0.9875 > first-fixation 0.98125), and both cited figures under-read what this checkout measures (0.975→0.98125, +0.6 pp; 0.956→0.9875, +3.2 pp). **This is not a clean test of glance count by itself** — `unbound` also runs 4× the `org.moment()` calls and 39 sleeps against first-fixation's 9 (§2's cadence table above), so its higher Q1 could as easily be "more sleep/consolidation" as "more glances." But the number the design docs cite as BIND's own justification does not hold up when measured on the correct commit, which is relevant to whether the extra-glances-cost-accuracy premise behind G-EYE-2 still applies (see §6.6).

**The sanity check the whole comparison rests on — the `unbound` arm's own final state matches life 2's REAL recorded final state EXACTLY:** this checkout's `unbound` run ends `org.t=78,872`, `births=717`, `cells alive [668, 17]` (668+17=685) and **39 sleeps** — identical, digit for digit, to life 2's own `STATUS.json` (`moments:78872, births:717, cells:685, sleeps:39`) and to F's independent reproduction (`G5-F-REPORT.md` §2(b): `cells=[668,17]` — his own true-code replay — matching this checkout's alive count exactly; `t=78872` matching too). **This confirms the ported checkout (BIND diff on commit 75b0a9b) is faithful: replaying life 2's own code from scratch reproduces life 2's own real trajectory exactly, so the first-fixation and BIND readings on the SAME checkout are trustworthy comparisons, not artefacts of a bad port.**

**The instrument diagnostic (ceiling-first, per SOLUTIONS #228(b) and the brief's own instruction to check the CEILING before grading the bar) — BIND's pre-registered exam UNDER-reads because it feeds a shape the mechanism never produced:** `Organism.recall_many` (`genome/machinery.py:834`) processes the 4 held-out glances of a canvas ONE AT A TIME — each one independently thresholded by `_lit()` (`cos ≥ THETA_N`) — and only SUMS the surviving evidence afterward. A BIND-trained organism's sight cells are born from POOLED (mean, unit-renormalised) vectors; a single RAW held-out glance can sit below THETA_N against a pooled cell even when the pooled vector (what BIND's wake actually trained on) would clear it easily — the exam probes a representation the organism was never trained to recognise piecewise. Re-running the IDENTICAL `ask_glances` scoring function (`genome/questions.py`, unmodified — nothing about the scoring changed, only what is handed to it) with each held-out canvas's 4 glances pooled by `creature.mind._bind_pool` FIRST — "the position the mechanism saw", SOLUTIONS #200's law — `scratch_bind_consistent_exam.py`:

| reading | Q1.acc | n | correct | abstain |
|---|---|---|---|---|
| pre-registered (4 raw glances → `recall_many`) | 0.9625 | 160 | 154 | novel 1, noedge 1, ratio 3, close 0 |
| **BIND-consistent (pooled → `recall_many` on 1 vector)** | **0.9750** | 160 | **156** | novel 1, noedge 0, ratio 1, close 0 |

The BIND-consistent reading (0.9750) is **still below** first-fixation's 0.98125 — **one single held-out answer** (156 vs. the 157 that would tie it) — but it is a materially different finding than the pre-registered reading's 1.875 pp gap (154/160): most of the apparent shortfall (3 of 4 percentage points) was the exam asking the organism a question shaped like the OLD design, not like BIND. **Reported honestly: BIND FAILS the pre-registered bar on both readings** (never loosened, never substituted for the grade); the second reading is offered beside it, labelled, as the more mechanism-faithful number, and as the thing that would need fixing (the exam's own glance-feeding road, not BIND itself) before this bar could be graded fairly at all.

## 3 · Moment-denominated genes under BIND — the cadence table

**The mechanism (measured, not estimated):** life 2's own STATUS.json — `started_at 2026-09-20T08:12:33.049Z`, `heartbeat_at 2026-09-21T09:00:09.448Z`, `episodes 17768` — gives a real canvas rate of **716.64 canvases/hour** (24.793 h ÷ 17,768 canvases). `org.t` (STATUS `moments: 78872`) splits EXACTLY into `4 × 17,768 = 71,072` from `_consume_eye` (one `org.moment`/`moment_sight` call per glance, `GAZE.fixations = 4`) plus `39 sleeps × 200 replay = 7,800` from `SLEEP`'s own replay bursts (`78,872 = 71,072 + 7,800`, exact). **Under BIND, `_consume_eye`'s own contribution drops to `1 × canvases`** — SLEEP's replay bursts are UNCHANGED in absolute size (episodes are already written one-per-canvas via `f0`, untouched by BIND — see §4's scoping note) but become a larger fraction of the total. So: **"every N moments" ≈ N/4 canvases today, ≈ N canvases under BIND** — a 4× lengthening in canvas/wall-clock terms for any gene whose N is left unchanged.

| gene | today (canvases / wall-clock, @716.64/h) | BIND, N unchanged | recommendation |
|---|---|---|---|
| `SLEEP every 2000 moments replay 200 by surprise` | 500 canvases ≈ **41.9 min** | 2000 canvases ≈ **2.79 h** | **RE-EXPRESS → `every 500 moments`** (500 canvases ≈ 41.9 min, unchanged). REQUIRED, not optional: the verdict reader's ALIVE mark needs sleeps > 0 in every hour; 2.79 h between sleeps fails it by construction. |
| `SCALE every 1000 moments` | 250 canvases ≈ 20.9 min | 1000 canvases ≈ 83.7 min | **LEAVE UNCHANGED.** `_scale()`'s trigger (`self.t % scale_every == 0`) and the mechanism it regulates (`_delta`'s per-moment weight nudges, the only thing that can push `‖W[s]‖` over 1) both advance in lockstep with `org.t` — "every 1000 moments" means "every 1000 weight-update opportunities" regardless of BIND. That is the invariant SCALE actually needs; wall-clock time is not it. |
| `CYCLE grow to 0.9 nmax then consolidate` | not moment-denominated — a CELL-COUNT ceiling (`total_cells() >= grow_to*nmax`, checked inside `_birth()`) | unaffected in meaning | **LEAVE UNCHANGED.** Only the wall-clock RATE of approaching the ceiling shifts (slower under BIND — §1's measurement: ≈3× fewer births over the same canvases), which is BIND doing its job, not something to compensate for. |
| `HEBB window 1` | `hebb_window` is parsed and REQUIRED but not read anywhere inside `_hebb()`'s body (grep-verified: no functional effect today, regardless of BIND) | unaffected — still inert | **N/A today.** If a future windowed-Hebbian rule reads this field, its "window" (a co-occurrence span, presumably in moments) would need reconsidering under BIND at that time; nothing to re-express now because nothing reads it now. |
| `STAGE 1 senses moments 0..200` / `STAGE 2 meet moments 200..` | `t=200` at canvas 50 ≈ **4.19 min** (gates `self.wire` — HEBB/DELTA/misfire/PRUNE/MERGE all start here) | `t=200` at canvas 200 ≈ **16.75 min** | **RE-EXPRESS → `moments 0..50` / `moments 50..`** to preserve the original ~4.2 min sense-only warm-up before word↔sight wiring begins. Left at 200, canvases 51–200 stay in sense-only mode that used to already be wiring — a real, likely-unintended behaviour change, not just a rename. |
| `BUDGET 400 per arrival` | a births-CAP per arrival (checked in `_birth()` via `budget_left <= 0`), not a rate | unaffected in meaning | **LEAVE UNCHANGED.** The cap is genuinely "at most 400 new cells," never "N per unit time." BIND changes the RATE births accrue underneath the cap (§1: ≈3× fewer over the same canvases) — that is the effect to observe, not pre-compensate for. |
| `NMAX 2000` | an absolute lifetime cell ceiling | unaffected | **LEAVE UNCHANGED** — not moment- or canvas-denominated at all. |
| `FAST episodes 20000 keys sight words surprise` | a ring-buffer capacity in EPISODES; `self.episodes.write(...)` is already called exactly ONCE per canvas (keyed on `f0`, the first raw glance — §4's scoping note: untouched by BIND) | unaffected | **LEAVE UNCHANGED** — already canvas-denominated, not moment-denominated; BIND changes nothing here. |
| `SNAPSHOT_EVERY = 500` (a CODE CONSTANT, `creature/mind.py:88`, compared against `org.t` at `mind.py`'s `consume()` — **not a gene**, per the orchestrator's own note) | 125 canvases ≈ **10.46 min** | 500 canvases ≈ **41.86 min** | Same shape as SLEEP, smaller stakes: 41.9 min still clears the "≥1 snapshot per hour" ALIVE bar, so it does not fail by construction the way SLEEP would. **Not changed here** (explicit instruction). If wall-clock cadence should be preserved, the constant would need to become 125 — a CODE change, not a genome-text one, out of scope for G5.genome assembly; flagged for whoever owns `creature/mind.py`'s constants next. |

**Also, out of scope but worth naming:** `PREDICT`'s own `err`/`lr_scale` and the `FAST` episode writer are measured on `g["feats"][0]` (the raw first glance, never the BIND-pooled vector) — a deliberate scoping choice, not an oversight; see §4.

## 4 · Scoping: what BIND does NOT touch

`_bind_pool()` only changes the vector(s) fed to `Organism.moment()`/`moment_sight()` (the SLOW area's resonance/birth/wiring). It leaves untouched, on purpose (the brief names BIND as "one canvas = one moment" for the ORGANISM's binding, not a rewrite of PREDICT or FAST):
- **PREDICT** (`self.predictor.error(g["feats"][0])`, `lr_scale = self.predictor.modulate(1.0)`) — still reads the raw FIRST glance, exactly as before BIND existed.
- **FAST's episode write** (`self.episodes.write(moment=t_at_f0, x_s=f0, …)`) — `f0 = g["feats"][0]`, the raw first glance; already ONE episode per canvas regardless of BIND (§3's `FAST` row).
- **The journal's `fix` field** — still lists all 4 `(y, x)` fixation coordinates (the WHERE of all 4 looks stays on the tape row) even though only 1 moment now happens; only the ORGANISM's own moment count changes.

## 5 · The COLOUR bar and the RETINA identity bar

**COLOUR — the grey/maker-world exactness (the gate before the gate, EYE.md §4 G-EYE-3):** over every canvas of `THINGS_11` (11 renderings, `genome/world.render_canvas`), `max|rg| = max|by| = 0.0` **exactly** — the maker's world is one grey plane × 3, so both opponency channels are true zero everywhere. Directly asserted: with `colour` declared, the first 112 numbers of every glance's feature vector are `np.array_equal` to the SAME glance's vector with `colour=None` (the outer unit-step in `glances()` is provably a no-op when the appended block is exactly zero — `unit(concat(v, 0)) == v` when `‖v‖ = 1`). `sight_dim()` reports 144 with `colour` declared, 112 without — parity preserved, every existing pin untouched.

**COLOUR — the BabyAI bar, reproduced through THIS branch's own wiring, not a copy of the formula** (`scratch/colour_babyai.py`, not committed — reuses `game-worlds/code/bands.py`'s `bands()`/`THINGS` PURE functions read-only, and G's own harvested `results/minigrid.npz`, but computes every feature vector through `genome.gaze.glances(colour=...)`, this branch's real production door, writing its own scratch PNGs only into `scratch/babyai_frames/`, never into `/data/dev/game-worlds/frames/`):

| | grey (112) | +colour fixed-gain (144) |
|---|---|---|
| G's reported (`REPORT-G5-G.md` §3.6, BabyAI POV, his own gaze, things-only) | −0.107 | **+0.046** |
| this branch's own `genome.gaze.glances(colour=...)`, same 240 harvested frames | **−0.107** | **+0.046** |

Bit-for-bit the same margin, to 3 decimals, through the real gene's wiring instead of a standalone script — the design F/G measured is what actually got built. Bar (§4 of the brief: "≥ +0.04"): **PASS** (+0.046 ≥ +0.04).

**RETINA — byte-identity on life 3a's real tape** (`tests/genome/test_retina_fast_life3a.py`, committed, runs with the suite): every one of life 3a's **2,338 eye canvases** — saliency AND all 8 channels (`lum, rg, by, contrast, orient_h, orient_v, orient_d1, orient_d2`) — `np.array_equal` between the pinned oracle's `analyse()` and `retina_fast.analyse_fast()`. `max|delta| = 0.0`. A negative control (a `+1e-9` planted corruption) proves the check is not vacuous. F proved life 2's tape (17,768 canvases); this proves life 3a's, per the brief's own bar.

**The new pin, named:** `genome/gaze.py`'s `organs()` now verifies a THIRD file's bytes before adopting `retina_fast.py` — `genome/retina_fast.py` → sha256 **`90305a986e6b489cacdbe652392ed8557317a8d38de9b68ad4c1aa0a26e9008d`**. This differs from F's reported `452602160658d8253c477953476d1d91c7cfbadebc0241ba75abfdd74e343b1d` because this copy carries this branch's own edit-attribution header line (SOLUTIONS.md's hard-rule header, Ahmad 2026-07-17: "anyone/any agent who edits ANY file must record NAME + DATE + TIME") — the file's FUNCTIONAL content (everything after the header comments) is byte-for-byte F's, verified by re-running his own `test_retina_fast.py` suite unmodified (below) and by the life-3a identity test above; only the pin VALUE moved to match this copy's real bytes, recomputed with `sha256sum`, never typed from memory.

## 6 · Raised (not worked around)

1. **BIND fails its pre-registered bar (§2).** Recorded as FAIL, not loosened. The mechanism-consistent re-reading (0.9750 vs the bar's 0.98125 — one held-out answer) says most of the apparent shortfall was the EXAM's own glance-feeding road, not BIND's binding rule — but "most" is not "all", and one answer is still under the bar. **Orchestrator's decision, not made here:** (a) ship BIND anyway on the strength of its OTHER measured effects (§1: ≈3× fewer spurious births, matching F's own diagnosis of the defect BIND was built to fix; a real, measured cost reduction) and treat Q1 as inconclusive pending an exam repair; (b) fix `ask_glances`'/`recall_many`'s glance-feeding road to pool held-out glances under a BIND-declaring genome (a real code change, not this brief's scope) and re-grade; (c) hold BIND pending (b). This report does not recommend one of the three — that is a design call, not a measurement.
2. **`Organism.state_hash()`'s OLD (un-repaired) cost dominates the per-canvas mind cost** measured in both §1 (the 600-canvas slice) and §2 (the full 17,768-canvas replay: first-fixation/BIND settle near 45 ms/canvas, unbound climbs past 62 ms/canvas as its cell count grows). F's `g5-repairs` branch fixes this (35.86 → 7.29 ms median) but it is NOT part of this brief and was not adopted here (only `retina_fast.py` was, per the brief's explicit instruction). Whoever merges BIND onto a life that also wants the cheaper state_hash should merge both.
3. **SLEEP replays raw first glances (`f0`) into a BIND-pooled-trained SLOW area.** `genome/sleep.py:44` calls `org.moment(rec["x_s"], rec["x_w"])` where `rec["x_s"]` is FAST's stored `f0` — the raw, un-pooled first glance (§4's deliberate scoping: BIND was left out of PREDICT/FAST on purpose). So under BIND, WAKE trains sight cells on pooled (mean, 4-glance) vectors while SLEEP's replay trains the SAME cells on raw single-glance vectors — two different representations of "what a canvas looks like" feeding the same cell population. `first-fixation` has no such split (its only glance IS its `f0`). Confirmed structurally (`genome/sleep.py:44`, read directly) and consistent with §2's diagnostic (the organism performs measurably better when FED pooled vectors than raw ones at exam time — the same mismatch, at a different door). **Design question for the orchestrator, not a defect in what shipped here:** should `f0`/FAST's episode write become the BIND-pooled vector when BIND is declared, so wake and sleep train on the same shape?
4. **`gaze.glances(mode="one", colour=not None)` raises `GenomeError`** — T-one-glance (`tools/verdict_g4.py`'s twin, monkeypatching `gaze.glances` to force `mode="one"`) has no per-glance window to read the 4×4 colour cells from; the brief names no intended behaviour for this combination, so it refuses loudly rather than guessing (SOLUTIONS discipline: a gap named beats a gap silently filled). Currently inert (no genome anywhere declares `colour` yet), but flagged for whoever runs `verdict_g4.py`'s twins against a colour-bearing genome.
5. **The BIND bar's provenance vs. this report's own measurement — and they disagree, in BOTH numbers, and the ORDERING reverses.** EYE.md/G5-DESIGN.md cite "first-fixation-only 0.975 > 4-fixation 0.956 — the extra glances cost 1.9 pp" as "life 2's own twins," the very premise G-EYE-2 (and this brief's BIND mandate) rests on, without naming which commit computed them; F's report (§0) shows the verdict reader that most plausibly produced them (`runs/g4-verdict-life2-20260921-1215/`) ran AFTER master's PREDICT law changed (2026-09-21 11:18) — i.e. those cited numbers may themselves be the counterfactual F warns about. **On this report's own three-arm replay, under the correct (75b0a9b) commit, same exam machinery, same seed: first-fixation reads 0.98125 (0.6 pp above the cited 0.975) and `unbound` (the true 4-fixation arm) reads 0.9875 (3.2 pp above the cited 0.956) — and 0.9875 > 0.98125, so the ORDER the cited numbers report (first-fixation beats 4-fixation) is reversed here (4-fixation beats first-fixation).** This is stated plainly, not softened: as measured on the correct commit, the extra-glances-cost-accuracy premise cited for G-EYE-2 does not hold up. It is not a clean refutation — `unbound` also runs 4× the moments and 39 sleeps vs first-fixation's 9 (§2's cadence table), a real confound between "more glances" and "more consolidation" that this replay was not designed to separate — but the cited 1.9 pp cost does not reproduce under the commit life 2 actually ran on, which bears directly on the ship/fix/hold decision in item 1: if extra glances are not a net Q1 loss under the real code, BIND's own justifying premise needs re-examination alongside its Q1 result. Worth a look by whoever owns the verdict reader next, and by whoever next revisits G-EYE-2's clause.
6. **`retina_fast.py`'s pin value moved** (§5) — a consequence of this branch's own edit-attribution header, not a functional change; named so nobody is surprised the two branches' pins differ.

## 7 · Suites, on final bytes

Per the orchestrator's correction: `python3 -u -m unittest discover -s tests/genome -t .` and `-s tests/creature -t .` (the `-t .` top-level flag; without it several modules' relative imports fail to load). Both run from the worktree root, on the FINAL committed bytes (after every code change in this report), `nice -n 10`.

```
$ python3 -u -m unittest discover -s tests/genome -t .
----------------------------------------------------------------------
Ran 142 tests in 56.098s

OK (skipped=1, expected failures=6)
```

```
$ python3 -u -m unittest discover -s tests/creature -t .
----------------------------------------------------------------------
Ran 152 tests in 625.190s

OK
```

142 = **136** (this checkout's own pre-change baseline, `python3 -u -m unittest discover -s tests/genome -t .` run BEFORE any edit in this branch, `scratch/baseline_genome.log`: "Ran 136 tests") **+ F's `test_retina_fast.py`'s 4** (copied verbatim) **+ this branch's own `tests/genome/test_retina_fast_life3a.py`'s 2**. 152 = the pre-existing 139 (after the `test_refusal.py` sample-line fix, §6 is unaffected by that — a pure test-fixture addition, no production code touched by it) + this branch's own `tests/creature/test_bind_colour.py` (13 tests). Neither suite required a tolerance loosened, a test skipped, or a bar moved to pass; the 1 skip and 6 expected-failures in `tests/genome` are pre-existing and unrelated to this brief (PREREG-bar toys, noted by earlier builders' own edit history in those files).

**294 tests total across both suites, all passing** (142+152); of those, 15 are new in this branch (2 retina life-3a identity tests + 13 BIND/colour mechanics tests) and the other 279 are pre-existing, unregressed.

## 8 · Commits

On branch `g5-bind-colour`, worktree `/data/dev/genome-wt-n`, all ahead of master `ec28b4c`:

```
92e23a6 G5-J: pin BIND + colour mechanics (parser grammar, sight_dim, grey no-op, moment-count/unit-norm through a real Mind)
203f656 G5-J: BIND (one canvas = one moment), SENSE colour (fixed-gain rg/by 4x4), retina_fast adopted
f0bc5ea gitignore: scratch/ (orchestrator correction)
```

Nothing committed to `/data/dev/genome`, no other worktree's tracked files touched, no systemd unit touched. The detached checkout at `scratch/wt-75b0a9b` (commit `75b0a9b`, carrying the same BIND diff manually ported for §2's replay) has uncommitted changes on disk, left for review exactly as F left `genome-wt-k-hist`; it can be removed with `git worktree remove scratch/wt-75b0a9b --force` once inspected (it carries no commits of its own). `scratch/` (both this worktree's own and the nested checkout's) is fully git-ignored and holds only reproducibility material: `time_bind.py` (§1's 600-canvas cost slice), `colour_babyai.py` (§5's BabyAI band reproduction), `wt-75b0a9b/scratch_run_bind_q1.py` + `scratch_bind_consistent_exam.py` (§2's three-arm replay and the instrument diagnostic) and their logs/run roots — none of it required to reproduce the committed code's own behaviour (the committed test suites are self-contained), all of it kept so the numbers in this report can be checked against their source.
