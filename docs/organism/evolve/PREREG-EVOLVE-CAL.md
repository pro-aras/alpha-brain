# PREREG-EVOLVE-CAL — calibrating the evolve gate: a noise model, a planted-good control, the dead dimensions, and a confirmation slice

*Written by Claude (Opus 5.5, swarm architect), 2026-10-03 11:21 +0400 (from `date`), on the seat's word of 2026-10-03 (EVOLVE-CAL «must decide together: the E3 fix, which dimensions a 2 h slice can grade at all, a tolerance per dimension from a measured noise model, and a planted-good mutant that must PASS on a real slice beside the planted-bad that must refuse»), before any code or run. The builder is the CLAIMS lane (Claude Sonnet 5.5, a3fcebae1c279bf9b), holder of the census this law rests on (`docs/organism/claims/CLAIMS-CHECK-2026-10-03.md` §1(c), §2 E1–E3, branch claims-1003 at 375cfa5). It co-signs after its adversarial read; the seat signs.*

## 0 · What the gate is today, and what is wrong with it (the census, re-read)

The EVOLVE organ (`tools/evolve.py`, ALPHA4-PREREG §6; genome line `EVOLVE every 6 h; mutate 1 gene within bounds; judge on the last 2 h; adopt at sleep under the regression bar`) replays the INCUMBENT and ONE MUTANT from the same shadow checkpoint over the last 2 h of tape, grades both, and applies `regression_bar` (`tools/evolve.py:165–194`): any numeric reading that goes DOWN refuses (no tolerance); a PASS needs one reading up by its margin (`MARGINS`: q1_seen +0.01, confirmed_share +0.02, reward_mean +0.02, frames_filed +1) and a wall-clock cost ratio ≤ 1.2. On `brain-long-2` (14 proposals, read from `evolve/PROPOSAL-*.json`):

| # | gene → value | verdict | q1_seen (of 110) inc → mut | frames inc → mut | twin wall s |
|---|---|---|---|---|---|
| 2 | DELTA.lr 0.07 | REFUSED | 83 → 79 | 382 → 388 | 7,944 / 6,768 |
| 3 | BIRTH.misfires 3 (the incumbent's own value, E2) | REFUSED (null) | 100 → 100 | 151 → 151 | 3,958 / 3,954 |
| 4 | DELTA.lr 0.09 | REFUSED | 106 → 99 | 44 → 46 | 1,807 / 1,581 |
| **5** | **KWTA.k 4** | **PASS, ADOPTED 10-01 01:59** | **90 → 92** | 39 → 39 | 1,695 / 1,691 |
| 6 | BUDGET.per_arrival 305 | REFUSED (null) | 108 → 108 | 36 → 36 | 2,004 / 1,998 |
| 7 | SLEEP.every 1414 | REFUSED | 107 → 105 | 31 → 31 | 2,051 / 2,097 |
| 8 | SLEEP.replay 92 | REFUSED | 110 → 108 | 32 → 29 | 1,970 / 1,953 |
| 9 | SLEEP.every 2612 | REFUSED (null) | 102 → 103 | 32 → 32 | 1,942 / 2,053 |
| 10 | MERGE.theta_m 0.9834 | REFUSED | 100 → 92 | 32 → 32 | 2,035 / 1,973 |
| 11 | SLEEP.replay 255 | REFUSED (null) | 103 → 103 | 29 → 29 | 2,028 / 2,133 |
| 12 | MERGE.theta_m 0.9947 | REFUSED | 106 → 108 | 30 → 28 | 2,165 / 2,319 |
| 13 | KWTA.k 10 | REFUSED | 104 → 102 | 26 → 26 | 2,169 / 2,142 |
| 14 | DELTA.lr 0.07 | REFUSED | 103 → 103 | 28 → 27 | 2,046 / 2,081 |

(#1: not gradable, no checkpoint yet.) Over the 13 judged rounds q1_seen moved −8 … +2 items; the one adoption was +2 items of 110 on one slice.

**The defects (the census, each re-checked against the code read today):**
- **D1 — no noise model.** The twins are deterministic replays, so a refusal is not a random draw — but a mutant's trajectory diverges chaotically from the incumbent's, and nobody has measured how far two MERIT-NEUTRAL twins drift apart in q1_seen or frames_filed over 2 h. «Any drop refuses» and «+1 item is null, +2 passes» sit inside a spread nobody knows.
- **D2 — no planted-GOOD control on a real slice.** The accept branch is tested only on hand-built dicts; the two real-slice controls (a planted bad `BIRTH.theta_n 0.5`, a null `DELTA.lr 0.051`, one draw each) are both refusals, which a gate that refuses everything also passes.
- **D3 — `confirmed_share` dead by a call-site shift (E3).** `tools/evolve.py:151` calls `surprise_mark(tape_slice, journal_rows, status, …)` against the signature `surprise_mark(journal, status, surprise_declared, …)`; every argument lands one place off and the mark reads «not gradable» in 13/13, falsely (the twin journal carries `confirmed` on 3,678 / 3,678 moment rows; called right: 0.4494).
- **D4 — two dimensions blind by construction.** `reward_mean` and `act_pass` are read from the TAPE slice both twins replay; in a replay the world's answers are the tape's, so they are identical on the twins (equal 13/13) and can neither gate nor veto. A replay cannot judge a policy change at all (the ACT lane's premise).
- **D5 — one dimension above its ceiling.** `sentence_pass` needs ≥ 100 missions; a 2 h slice holds 3–10 (one per game episode). NOT GRADABLE in 13/13.
- **D6 — the cost ratio reads the box.** It is a WALL-clock ratio of two twins run one after the other (never in parallel), so a load change between them moves it (#243 (5), #242 addendum).
- **D7 — multiplicity.** A proposal every 6 h; one PASS in 13 judged rounds with no noise model may be best-of-13 on noise (#158).
- **D8 — the proposer can draw the incumbent's own value (E2)**: #3 cost ≈ 2 × 3,950 s to refuse a mutant identical to its incumbent.

**Why this law now.** The working gate is q1_seen + frames_filed + a load-dependent cost. The BRAIN GENOME idea of his session notes (10-02: «growth rules, learning rules, drives, self-census, mutation operators … two time scales … the outer loop needs a fitness function») rests ENTIRELY on an outer loop that can tell a better genome from a worse one. Until this gate is calibrated, no genome — of the body or of a brain — can be evolved honestly here.

## 1 · What changes (code; the builder's)

| Where | What |
|---|---|
| `tools/evolve.py:151` (D3) | `surprise_mark(journal_rows, status, "SURPRISE" in declared)` — the right argument order, pinned by a test that grades a twin journal carrying `confirmed` (red on today's line) and a planted journal with `confirmed` stripped (must read None, so a dead input is told from a mis-routed one). |
| `regression_bar` (D4, D5) | `reward_mean`, `act_pass`, `sentence_pass` leave the bar: each is printed in every proposal as NOT GRADABLE with its reason (D4: «read from the tape both twins replay — identical by construction»; D5: «needs ≥ 100 missions, the slice holds n»), with its presence count. The bar reads q1_seen, frames_filed, confirmed_share and the cost. |
| the cost (D6) | the twin's PROCESS CPU-seconds (`time.process_time()` around each twin), not wall; the wall ratio printed beside. |
| the verdicts (D1, D7) | THREE verdicts, not two: **REGRESSED** (a reading falls below its band), **IMPROVED** (no reading below its band, at least one above it, CPU ratio ≤ 1.2), **NO EVIDENCE** (neither) — the incumbent stays on both REGRESSED and NO EVIDENCE. An IMPROVED mutant is ADOPTED only after it is IMPROVED again on the NEXT disjoint 2 h slice (a CONFIRMATION round, its own twins, the same bands). |
| the bands (D1) | per dimension d, from the NOISE MODEL (§2): REGRESSED on d iff Δ_d < μ_d − z·σ_d; above its band iff Δ_d > μ_d + z·σ_d; μ_d, σ_d the mean and SD of the merit-neutral twin differences, z = 2.39 (one-sided 0.0083 per side per dimension under normality: 0.025 family-wise over three dimensions). Integer readings (q1_seen in items of 110, frames_filed in frames) compare on their own grid: the band edges are printed in items / frames. The normality of each null distribution is CHECKED (Shapiro–Wilk on its draws, printed); a dimension whose null is not normal at p < 0.01 uses its rank band instead (outside all draws: below the minimum / above the maximum) and says so. |
| the proposer (D8) | `draw_mutation` redraws (the same stream, the next draw) when the value equals the incumbent's; pinned by a test on `(20261101, 1, 3)` (today: `BIRTH.misfires 3`). |

None of this touches a running life: `brain-long-2`'s EVOLVE worker runs from its own code checkout. The changes enter a later life by the ladder.

## 2 · The calibration (on COPIES of `brain-long-2`'s own evolve record; the live root never written)

`brain-long-2/evolve/checkpoints/` holds 38 shadow checkpoints (every 2 h of tape) and the tape holds every slice; past slices are immutable. Every run below copies one checkpoint and its slice into scratch (`tools/evolve.py`'s own `build_twin` / `tape_slice` / `grade_twin`, called from a calibration script, never re-implemented).

- **N1 · THE NOISE MODEL (merit-neutral twins).** On ONE slice S1 (the slice of round 13, a mid-life state): the incumbent twin, and **20** twins of the SAME genome with `SEED` replaced by `SEED + k`, k = 1 … 20. A changed seed changes no gene and so no merit; it changes the mind's internal draws, so the twins diverge as a mutant's would by chaos alone. The 20 differences (twin_k − incumbent) per dimension are the null: μ_d, σ_d, the normality check, the bands. **Why the seed and not a near-null gene:** a «small» gene step (DELTA.lr 0.05 → 0.051) is itself a merit change of unknown size; a seed is merit-neutral by construction. Check that the seed reaches the mind: the 20 twins' journals must NOT all be equal to the incumbent's (if they are, the seed does not reach the mind's draws, the null is degenerate, and the builder RAISES — #228 (a)).
- **N2 · does the band transfer across the life?** The same with **10** seed twins on a second slice S2 from early life (round 5's slice). The bands of S1 and S2 are printed side by side; if σ differs by more than ×2 between them, the band is a function of the life's age and the gate must compute it per round (the next law), and this law's bands are stated for mid-life only.
- **P-BAD · planted bad mutants must be REGRESSED** (on S1): `BIRTH.theta_n 0.5` (the recorded plant), and the two most harmful real mutants of the record re-judged under the bands (#10 MERGE.theta_m 0.9834, −8 items; #4 DELTA.lr 0.09, −7 items).
- **P-GOOD · a RESTORATION plant must be IMPROVED, on two slices** (S1 and the slice after it): the incumbent DEGRADED by one gene is the plant's «incumbent»; the mutant RESTORES that gene to the life's value. The degradation is chosen BEFORE any band is read, as the FIRST of this declared list whose own Δq1 (degraded − true incumbent, one pair on S1) exceeds **2 × the band half-width** — so the plant sits where the gate can see it (#228 (a)): (1) `MERGE.theta_m 0.9834` (the record's −8 items), (2) `DELTA.lr 0.09` (−7), (3) `KWTA.k 1` (the bound's edge). If none clears, the gate cannot see a degradation of that size on a 2 h slice — a RESULT: the gate is NOT GRADABLE for improvements of that size, adoption stays OFF, and the law says so.
- **R5 · the one adoption re-judged.** #5 (KWTA.k 5 → 4, +2 items) under the bands, on its OWN slice and on the next disjoint slice. If it is NO EVIDENCE on either, the record says the adoption was within the gate's noise (best-of-13, #158). Nothing is changed in `brain-long-2` retroactively.
- **E3 re-graded.** `confirmed_share` read right on all 13 judged rounds' twins (their journals are on disk under `evolve/round-<n>/`): its Δ per round printed; whether any of the 13 verdicts would have changed under the bands is printed (a reading).

**Order and stops:** the unit tests of §1 first (red, then green); N1 (STOP if the seed does not reach the mind); N2; P-BAD and P-GOOD (STOP and report if P-BAD is not REGRESSED or P-GOOD not IMPROVED: the calibrated gate is then blind on its own plants, and adoption stays OFF); R5; E3's regrade.

## 3 · Marks and bars of THIS law (what makes the calibration itself trustworthy)

| # | Mark | Bar |
|---|---|---|
| C1 | the seed reaches the mind: the N1 twins' journals differ from the incumbent's | ≥ 18 of 20 differ |
| C2 | P-BAD: each of the three planted bad mutants is REGRESSED under the bands | 3 of 3 |
| C3 | P-GOOD: the restoration plant is IMPROVED on S1 AND on the next slice | 2 of 2 |
| C4 | E3: `confirmed_share` graded (not None) on every judged round's twin pair whose journal carries `confirmed`; the stripped plant reads None | all; plant caught |
| C5 | D8: the proposer never emits the incumbent's value over (SEED 20261101, epochs 1–3, proposal_no 1–50) | 0 of 150 |

**Readings:** the bands (μ, σ, z, edges in items / frames) per dimension and per slice; the normality checks; the 13 historic verdicts re-read under the bands (how many REFUSED become NO EVIDENCE, whether #5 holds); the CPU vs wall cost ratios of every pair; the price.

## 4 · Price (measured per twin: rounds 5–14 ran 1,581–2,319 s a twin; ≈ 2,000 s taken)

N1: 21 twins ≈ 11.7 CPU-h · N2: 11 ≈ 6.1 · P-BAD: 3 mutant twins on S1 (the incumbent shared) ≈ 1.7 · P-GOOD: up to 3 degradation probes + 2 slices × 2 twins ≈ 3.9 · R5: 2 slices × 2 ≈ 2.2 · **total ≈ 26 CPU-h** (≈ 9 h wall on 3 slots; a whole organism per twin, ≈ 1–3 GB each — the slot gate's memory floor applies). The seat schedules it (a night run fits); a twin solo on an idle box is measured first (G-price) and replaces the 2,000 s estimate.

## 5 · Adversarial walk

1. **Is the seed null merit-neutral?** It changes no gene; it can change WHICH cells are born and which ties break, i.e. the organism's luck. That luck is exactly what a one-gene mutant also draws, and it is the noise the gate must not mistake for merit. A near-null gene would mix luck with an unknown merit step.
2. **Is z = 2.39 above a ceiling?** The bands are relative to the measured σ; their absolute width is read, not set. If σ_q1 is about 1.5 items (the record's spread of real mutants is −8 … +2 items, which bounds it from above), the band edge is ≈ 3.6 items: an IMPROVED mutant needs ≥ +4 items of 110. The record's one adoption (+2) would read NO EVIDENCE — a prediction on the record, not a bar.
3. **Can the plant fire?** P-GOOD is chosen by its own measured effect against the band (§2), so it cannot be placed where the gate is blind without the law saying so.
4. **Every «every / ≥ N» counted:** 20 + 10 seed twins; 3 bad plants; 2 slices for P-GOOD and R5; 13 historic rounds; 150 proposer draws.
5. **What a pass does NOT show:** that evolution will find better genomes (that needs mutants whose merit exceeds the noise, which the bands now measure); that a 2 h slice is long enough for any real improvement (if every IMPROVED needs ≥ +4 items, the life may evolve nothing — a finding about the slice, answerable by the next law: a longer judging window or more exam items).
6. **The brain genome.** An outer loop over growth and learning rules is weeks of compute (RESEARCH-2026-10-03 §BRAIN GENOME). It needs this gate's bands, its planted-good control and its confirmation slice first, applied to its own fitness.

Signed: Claude (Opus 5.5, swarm architect), 2026-10-03 11:21 +0400 — the author.

---

## AMENDMENT 1 — the builder's adversarial read (2026-10-03 11:34 +0400, before any code or run)

*The claims lane read the text at 73f0e96 (sha256 9dcbf9cc…) against the code and refused to co-sign on a STOP-level premise defect. The author verified A1 by grep (the modules that exist — `genome/machinery.py`, `sleep.py`, `gaze.py`, `questions.py`, `predict.py` — hold 0 RNG draws and never read the seed; `.seed` is read only in `creature/mind.py`, `creature/think_thread.py`, `genome/web.py`) and accepts all eight. Where this amendment and §1–§5 disagree, this amendment rules.*

- **A1 · THE SEED DOES NOT REACH THE CELLS — §2 N1's premise was false.** The organism's machinery draws no random number. In a twin restored from a checkpoint, `_act_rng` and `_hands_rng` are re-built from the seed and then OVERWRITTEN by the snapshot's saved states (`creature/mind.py` resume); only `_think_rng` and the think thread's boundary generator are re-derived from `SEED + k`, and what think picks reaches is bookkeeping (beliefs, predictions, `frames_filed`, questions, the mouth). `q1_seen` is read from the twin's saved organism and ledgers, and `confirmed_share` from the organism's glances. **Predicted: across seed twins `q1_seen` and `confirmed_share` are BIT-IDENTICAL (σ = 0); only `frames_filed` and the think/act journal rows vary.** §5.1's «the seed changes WHICH cells are born» is struck as false for this code. Consequences:
  - **(i) C1 becomes per GATED DIMENSION:** for every dimension a band is claimed for, its null must hold ≥ 3 distinct values and σ > 0; a dimension that fails has NO band, and the law says so.
  - **(ii) The null for `q1_seen` and `confirmed_share` is the ε-TWIN:** the same genome with `DELTA lr 0.05 · (1 + k·ε)`, k = 1 … 20, a perturbation that REACHES the organism and is merit-negligible. Its dose-response is checked at ε ∈ {1e-6, 1e-5, 1e-4} (5 twins at each of the two non-chosen levels): the spread of the readings must be flat in ε on the plateau used. If it grows with ε, that ε is a merit step, not noise, and a smaller ε is taken. The chosen ε is the smallest level whose 5 twins do not all equal the incumbent bit for bit. **The seed twins stay, but only as the null of `frames_filed`** (10 twins, not 20).
  - **(iii) THE STOP TEST, first and cheap.** On a SHORT slice, ONE pair `SEED` vs `SEED + 1`, and ONE pair ε = 1e-5 vs the incumbent. Compare `org.row_hash()`, `q1_seen` and the journals. Predicted: the seed pair's organism EQUAL and its think rows different; the ε pair's organism DIFFERENT. If the ε pair's organism is equal too, nothing small reaches the cells, the noise model is degenerate, and the builder RAISES before any CPU-hour is spent.
- **A2 · The null has the test's PAIRING.** Production compares a same-seed pair (incumbent and mutant both `SEED`, one gene apart). ε-twins are same-seed pairs, so they are the PRIMARY null. Seed twins (different seed, same genome) bound only the think-driven reading.
- **A3 · The cost's null from the same twins (D6, corrected).** Process CPU does not remove load dependence: contention inflates a CPU-second as it inflates wall time (#242 addendum: the identical 100 epochs cost 119 ms alone, 207 among three, 689 among nine). The cost ratio is therefore BANDED like the other dimensions, from the CPU-second ratios of the N1 twins (identical or ε-identical genomes run one after another: their ratio spread IS the cost's noise), and `/proc/loadavg` and `/proc/pressure/cpu` are recorded at each twin's start and end. The fixed 1.2 stays as a POLICY cap printed beside the band; a mutant is cost-REGRESSED only if its ratio is outside the band AND above 1.2.
- **A4 · The band's arithmetic.**
  - (i) σ is ESTIMATED: the 21 values of a dimension on S1 (the incumbent + 20 ε-twins, 20 df) give σ̂.
  - (ii) The production Δ is a difference of TWO draws, so under no merit difference it is centred at 0 with σ_Δ = √2·σ̂. The band edge is **t(20, 1 − 0.0083) · σ_Δ = 2.614 · σ_Δ ≈ 3.70 σ̂** (one-sided 0.0083 per side per dimension; computed with scipy, printed with its inputs). The edge is NOT centred on the mean of the k differences against ONE incumbent: that mean is the incumbent's own luck on that slice (μ_X − X_0) and transfers to no other round.
  - (iii) The rank-band fallback (for a non-normal null) at n = 21 has error 1/22 ≈ 4.5 % per side per dimension: the «0.025 family-wise» holds only for the normal band, and a dimension on the rank band says so beside its verdict.
- **A5 · P-GOOD's choice of degradation** is made AFTER N1, by the deterministic first-fit rule of §2's list (the first whose own Δq1 on S1 exceeds 2 × the band half-width). «Chosen BEFORE any band is read» is struck. The plant's Δ on S1 is printed beside the record's Δ on its own slice.
- **A6 · P-BAD on their OWN slices.** #10 (MERGE.theta_m 0.9834, −8 items) and #4 (DELTA.lr 0.09, −7 items) were measured on rounds 10's and 4's slices; their twins are deterministic, so their recorded Δs are re-read under the bands with NO new twin, as READINGS, if N2 shows the band transfers across the life. Only the recorded plant `BIRTH.theta_n 0.5` is run on S1. **C2 becomes: that plant REGRESSED on S1 (1 of 1)**, with #10 and #4 printed.
- **A7 · R5 and N2.** #5's own-slice Δ is on the record (+2 items on round 5's slice = S2), so its re-judge there costs no twin, only S2's band (N2). The confirmation on the NEXT disjoint slice keeps its 2 twins. N2's transfer test is an F-test on the two variances (S1: 20 df; S2: 11 values, 10 df), two-sided 0.05. Refused transfer = the band is age-dependent, stated, and the next law computes it per round.
- **A8 · The proposer's redraw.** `draw_mutation(seed, epoch, proposal_no)` cannot see the incumbent, so the redraw lives in `mutate_genome_text` / the worker: when the drawn value equals the incumbent's, the SAME generator's next integer draw (gene index) and value draw are taken, and so on until they differ. The stream rule is pinned by a test. C5's check uses the per-epoch incumbent text (v1 after #5's adoption, KWTA 4).

**The price, re-counted:**
- the STOP test (two short-slice pairs) ≈ 0.5 CPU-h;
- S1: the incumbent + 20 ε-twins + 10 dose-response twins + 10 seed twins = 41 twins ≈ 22.8 CPU-h;
- N2: 10 ε-twins ≈ 5.6;
- P-BAD: 1 ≈ 0.6;
- P-GOOD: up to 3 probes + 2 slices × 2 ≈ 3.9;
- R5's confirmation: 2 ≈ 1.1.

**Total ≈ 34 CPU-h** (≈ 12 h wall on 3 slots), the STOP test first. Order: the claims lane builds the re-sit reader first (the seat's order); the STOP test can be run by whoever is free first.

Signed (AMENDMENT 1): Claude (Opus 5.5, swarm architect), 2026-10-03 11:34 +0400 (from `date`) — the author.
Co-signed: the builder (Claude Sonnet 5.5, claims) — pending, on the sha of this text.
Signed: the seat — pending.
