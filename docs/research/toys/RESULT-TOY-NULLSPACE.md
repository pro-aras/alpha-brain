# RESULT — TOY B «THE NULL SPACE»: does protecting the span of earlier rooms' inputs keep old words — and is it the NULL SPACE that does it, or only a smaller step?

*edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 12:26 +0400. Law: `docs/research/toys/PREREG-TOY-NULLSPACE.md`, co-signed 2026-10-03 11:24 +0400, signed-text sha256 `d15a6353d6b62e7ba74c407e2a220054c127250c7b4ee07f55d4564bc40ac2ca` (every record carries it; the code refuses a text that differs). Unit: 870 lives (87 a seed × ten seeds 20261301–20261310), launched at commit `4c5d981` on a clean tree (869 records carry `4c5d9815`; the one at `22f950ef` is the price-written life of seed 20261301 re-run, equal to the first in `rates_rw`, `pairs`, `table`, `first_meet`, `record` and `rho`). Every figure below is in `docs/research/toys/RESULT-TOY-NULLSPACE-REPORT.txt` (regenerated at `b0ae638` by `python3 -B -m tools.toys.nullspace.report`); the lives are `scratch/toys-ns/runs/<arm>/<seed>/<rep>.json` (scratch, gitignored; `tools.toys.nullspace.run launch` rebuilds them in ≈ 10 min wall on two lanes). A TOY on T-MEM-1's sequential bench, never the organism.*

## The answer, in plain words
1. **Yes, protection keeps old words.** After the noise room the plain learner's accuracy on the old rooms' shape words has fallen by 0.79 (BWT −0.792 ± 0.054 over seeds; −0.287 after room 3). The six protectors lose far less: **OWM −0.215 / −0.015 / −0.014 and NSCL −0.124 / −0.027 / −0.026** at τ = 0.1 / 0.01 / 0.001 after the noise room (after room 3: OWM −0.029 / −0.016 / −0.019, NSCL −0.033 / −0.031 / −0.038). Every gap to PLAIN is at least 7 paired standard errors at room 3 and 19 at the noise room (the bar was 2).
2. **It is the direction, not the amount.** Each of the six arms beat **all ten** draws of its own null (a rotated projector of the same spectrum for OWM, a random subspace of the same rank for NSCL) at **ten of ten seeds**, on both barred reads. The same step shrinkage with no direction (SHRINK, the arm's own realised ratio as one scalar) protects almost nothing at room 3 (BWT_3 −0.247 … −0.274 against the protectors' −0.016 … −0.038). One honest exception: at the finest resolution (τ = 0.001) and at the noise room only, the matched shrink comes close (BWT_4 −0.067 / −0.072 against −0.014 / −0.026) — there much of the protection IS amount; room 3 is the bar that tells them apart.
3. **It does not freeze learning.** Every protector learns the new rooms as well as PLAIN (plasticity ≥ 0.985; PLAIN 0.997 / 0.968) — even at τ = 0.001, where only ≈ 3 % of the next room's input energy lies outside the old span. My own prediction that it would freeze there (P-B3) was wrong.
4. **Cost:** a protected life costs ≈ 1.2 × a plain one (G5, solo: OWM 1.35 CPU-s against PLAIN 1.14).

**Verdict class (law §3): NULL-SPACE PROTECTS — all six arms** (OWM and NSCL at the three resolutions).

## What this does NOT show (read before quoting the answer)
- **It is a linear delta-rule learner whose forgetting IS input-space interference**, so a projector off the old inputs' span is the exact remedy by construction. It says nothing about the organism's brain: T-MEM-1's answer for the brain was an order-free STORE (BWT 0.000), and this toy never touched it (law §5.6).
- **It never reached the freezing side of the stability–plasticity trade.** Naming a room's two shapes is easy (PLAIN's own plasticity is ≥ 0.968), so the toy cannot say at what resolution protection starts to cost learning; a harder new room would.
- One learner family, one world family, ten seeds that SHARE the held items (the paired SE is held-item sampling only; the sign counts carry the training-draw variation).
- The law's STD-ONLY(j) «ceiling» is a ceiling only for the forgetting caused AFTER room j; the `removed share` column (1.7 – 1.8 at room 3, 1.1 – 1.3 at the noise room) is therefore not a share of anything — see «Two corrections of my own law» below. No bar depends on it.

## The instrument first (gates and controls)
| check | result |
|---|---|
| c1 PLAIN forgets (BWT_3 ≤ −0.15 and BWT_4 ≤ −0.50, ≥ 8 of 10 seeds) | **10 of 10** (BWT_3 −0.287 ± 0.042 [−0.352, −0.224]; BWT_4 −0.792 ± 0.054 [−0.891, −0.710]) |
| c2 something protectable (Δ ≥ 2 paired SE) | **10 of 10.** Δ_3 = STD-ONLY(2) − PLAIN on BWT_3 = +0.147 (SE 0.025; gap/SE over seeds 2.3 – 9.4, so the weakest seed clears the bar by little); Δ_4 = STD-ONLY(3) − PLAIN on BWT_4 = +0.604 (SE 0.025; 16.7 – 34.7) |
| PB1 the plant ANTI-OWM must lose to PLAIN on BWT_3 | **CAUGHT at 10 of 10** (BWT_3 −0.386, BWT_4 −0.819; against OWM@0.01 the gap is −0.370 (SE 0.029) and −0.804 (SE 0.018), ≥ 2 SE at 10 of 10 seeds) |
| PB4 every arm equals PLAIN through block 50 (room 1 unprojected) | **yes**, all 870 lives |
| PB3 / G2 PLAIN reproduces T-MEM-1's BASE record (seeds 01–03) | `rates_rw`, `pairs`, `table`, `first_meet` and all record rows EQUAL (`GATE-G2-G4-TOY-NULLSPACE.out`) |
| G4 the pre-pass rows equal a learner's own rows | max abs difference 0.0 |
| a consistency check the report prints | STD-ONLY(3) and FREEZE-OLD(3) are the SAME lives as PLAIN on BWT_3 (freezing after room 3 cannot change a read taken after room 3): gap +0.000, SE 0.000 at every seed |
| tests | `tests/tools/test_toys_nullspace.py` Ran 22 OK and `test_toys_nullspace_analyse.py` Ran 13 OK; RED first on the missing modules (`scratch/toys_nullspace-red.log`, `scratch/toys_nullspace_analyse-red.log`, each `FAILED (errors=1)`), GREEN `scratch/toys_nullspace-run1.log`, `scratch/toys_nullspace_analyse-run4.log` |

## The six arms against the four bars (seeds passing, of 10; the bar is ≥ 8)
| arm | B-PROTECT | B-NULLSPACE | B-SHRINK | B-PLASTIC | BWT_3 | BWT_4 | plast 2 / 3 | gap/SE min (BWT_3 / BWT_4) |
|---|---|---|---|---|---|---|---|---|
| OWM τ 0.1 | 10 | 10 | 10 | 10 | −0.029 ± 0.012 | −0.215 ± 0.041 | 0.998 / 1.000 | 9.4 / 19.2 |
| OWM τ 0.01 | 10 | 10 | 10 | 10 | −0.016 ± 0.013 | −0.015 ± 0.012 | 0.999 / 1.000 | 8.4 / 34.1 |
| OWM τ 0.001 | 10 | 10 | 9 | 10 | −0.019 ± 0.015 | −0.014 ± 0.010 | 0.999 / 0.999 | 8.0 / 34.1 |
| NSCL τ 0.1 | 10 | 10 | 10 | 10 | −0.033 ± 0.022 | −0.124 ± 0.047 | 0.998 / 0.997 | 7.3 / 24.0 |
| NSCL τ 0.01 | 10 | 10 | 10 | 10 | −0.031 ± 0.016 | −0.027 ± 0.016 | 0.997 / 0.999 | 7.3 / 32.0 |
| NSCL τ 0.001 | 10 | 10 | **8** | 10 | −0.038 ± 0.013 | −0.026 ± 0.009 | 0.998 / 0.985 | 7.1 / 31.6 |
| PLAIN | — | — | — | — | −0.287 ± 0.042 | −0.792 ± 0.054 | 0.997 / 0.968 | — |

(± is the sd over the ten seeds. NSCL at τ = 0.001 passes B-SHRINK at exactly the bar, 8 of 10. The paired SE: pairs per task 139 / 141 / 192, so 10 discordant pairs = a gap of 0.072 / 0.071 / 0.052; every gap to PLAIN at room 3 is ≥ 0.249.)

## The nulls, and what a smaller step buys
- **Rotated / random-rank draws** (means over seeds × 10 draws; BWT_3 / BWT_4): ROT 0.1 −0.284 / −0.771 · ROT 0.01 −0.278 / −0.689 · ROT 0.001 −0.266 / −0.246 · RANDRANK 0.1 −0.286 / −0.786 · RANDRANK 0.01 −0.287 / −0.752 · RANDRANK 0.001 −0.296 / −0.378. At room 3 none beats PLAIN (−0.287) beyond its own spread (sd 0.041 – 0.062); at the noise room a near-full-rank random projector (τ = 0.001 removes ≈ 127 of 147 directions) protects by shrinking.
- **Matched shrink, same ratio as the projector, no direction** (BWT_3 / BWT_4): SHRINK-OWM 0.1 −0.268 / −0.634 · 0.01 −0.259 / −0.278 · 0.001 −0.247 / −0.067; SHRINK-NSCL 0.1 −0.274 / −0.706 · 0.01 −0.262 / −0.521 · 0.001 −0.254 / −0.072.
- **The plain step made smaller (LRSHRINK, lr × s throughout)**: s = ½ −0.252 / −0.730 · ¼ −0.232 / −0.499 · ⅛ −0.222 / −0.150 (plasticity ≥ 0.995). A small enough step softens the NOISE room (the culprit) and does nothing for the interference among the learnable rooms.
- **Capacity** (mean over seeds, of 147 directions; OWM's `trace(I − P_j)` beside NSCL's removed rank `147 − d_j`; after rooms 1..j for j = 1 / 2 / 3): τ 0.1 (α 3,473.5): OWM 13.1 / 24.0 / 30.8 · NSCL 6.9 / 9.9 / 11.5; τ 0.01 (α 347.4): OWM 43.0 / 67.1 / 79.0 · NSCL 38.2 / 44.8 / 49.4; τ 0.001 (α 34.7): OWM 89.5 / 118.2 / 127.1 · NSCL 90.5 / 114.8 / 124.1. Protecting only 7 – 12 directions (NSCL τ 0.1) already keeps room 3 (−0.033); the noise room needs more (−0.124).

## The readings (no bar; paired against OWM τ 0.01 unless said; gap = the arm's BWT minus OWM's, SE = paired, «≥ 2 SE» counted over the ten seeds)
- **OWM-NB** (the bias outside the protected space): −0.032 at room 3 (SE 0.010; ≥ 2 SE at 9 of 10 seeds), −0.011 at the noise room (3 of 10) — a free bias costs a little. P-B7 holds.
- **OWM-RESTD** (P rebuilt in the CURRENT standardiser's coordinates): −0.020 (6 of 10) and −0.011 (6 of 10) — slightly WORSE, not better: the as-seen coordinates are not where the leak is. P-B6 refuted.
- **OWM-BM** (OWM's Methods recursion over batch-mean inputs, a looser projector of rank ≤ 50 a room): −0.002 (1 of 10) and −0.007 (3 of 10) — as protective as the all-rows form here.
- **OWM-OLDONLY** (words born in a room learn plain): −0.089 (9 of 10) and −0.067 (10 of 10) — letting new words learn unprojected costs old rooms; my §5 (h) worry (projected-from-birth words cannot learn their base rate) did not show: plasticity is ≈ 1.0 for every arm.
- **NSCL τ 0.01 against OWM τ 0.01**: −0.015 (2 of 10) and −0.012 (6 of 10) — the hard and the soft projector are close.
- **FREEZE-OLD(j)** (only the units that existed at room j's end stop updating): BWT_4 −0.477 / −0.222 / −0.188 for j = 1 / 2 / 3, against OWM's −0.015 (and plasticity 0.80 / 0.62 for j = 1). Freezing the old units alone does not match the projector; against OWM-OLDONLY's −0.082 the measured contrast suggests words born later, learning plain, take over the old inputs (a hypothesis, not tested here).
- **STD-ONLY(1)** (no weight moves after room 1): BWT_3 −0.061, BWT_4 −0.041, with plasticity 0.257 / 0.000 for rooms 2 / 3 — it forgets little because it never learned the later rooms.

## Predictions (written before any life) against the outcome
| | prediction | outcome |
|---|---|---|
| P-B1 [Likely] | PLAIN forgets at all seeds as in T-MEM-1, exactly at 01–03 | **holds** (c1 10 of 10; G2 EQUAL at 01–03) |
| P-B2 [Guessing] | OWM(0.01) removes more than half of the forgetting weights can give; plasticity ratio ≥ 0.9 | **holds by the letter** (printed share 1.84 / 1.29; plasticity ratio 1.002 / 1.033), but the «ceiling» it names is not one (below) |
| P-B3 [Guessing] | OWM(0.001) and NSCL(0.001) freeze: B-PLASTIC fails | **REFUTED** (both pass at 10 of 10; plasticity 0.999 / 0.985 at room 3) |
| P-B4 [Likely] | ROT(τ) protects less than OWM(τ) at every τ but more than PLAIN | **holds on the means** (ROT less at every τ; more than PLAIN by 0.003 / 0.009 / 0.021 at room 3, inside the draws' spread, and by 0.021 / 0.103 / 0.546 at the noise room) |
| P-B5 [Guessing] | Δ_3 > 0.10 (refuted if ≤ 0.10) | **holds** (Δ_3 = +0.147) |
| P-B6 [Guessing] | OWM-RESTD protects at least as well as OWM | **REFUTED** (slightly worse) |
| P-B7 [Guessing] | OWM-NB protects less than OWM | **holds** (−0.032 / −0.011) |

**The law's refutation clauses:** «protection comes from the null space» is refuted if every arm that passes B-PROTECT fails B-NULLSPACE or B-SHRINK — **not refuted** (all six pass all four bars). «The old inputs' span is the right thing to protect» is refuted if ANTI-OWM is within 2 SE of OWM at ≥ 8 seeds — **not refuted** (it is ≥ 2 SE below at 10 of 10). P-B5 is not refuted.

## Two corrections of my own law, found in reading the unit (no bar moves; both printed in the report)
1. **STD-ONLY(j) is not a ceiling for protection.** It freezes every weight AFTER room j; rooms 2..j still learn and forget as PLAIN does, so its BWT is a ceiling only for the forgetting caused after room j. A protector active from room 2 beats it, and OWM does (`removed share` > 1). c2's use (is there something protectable in room j + 1?) stands and passes; the share column is a printed reading with the wrong denominator and should be ignored.
2. **P-B3's freeze did not happen** (above): the naming task needs few directions, so the stability–plasticity frontier's far side is unmeasured here.

## Cost
G5 (`GATE-G5-TOY-NULLSPACE.out`, solo lives at seed 20261301, box load 6.96): PLAIN 1.14 CPU-s · OWM 1.35 (× 1.18) · NSCL 1.36 · ROT 1.29 · RANDRANK 1.35 · SHRINK-OWM 1.20 · OWM-RESTD 1.93 (× 1.69, it rebuilds P each block) · pre-pass 0.10 s a seed; the unit was priced at 19.0 CPU-min (the law's estimate was 33) and ran 87 lives in 111 – 125 s a seed on two lanes (`scratch/toys-ns/logs/work-{0,1}.log`). The per-life means in the report (PLAIN 1.36, OWM 1.27) were taken under load and are readings, not ratios (#243 (5)).

## Reproduce
```
PYTHONPATH=. python3 -B -m tools.toys.nullspace.run status
PYTHONPATH=. python3 -B -m tools.toys.nullspace.report --out docs/research/toys/RESULT-TOY-NULLSPACE-REPORT.txt
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python3 -B -u -m unittest discover -s tests/tools -t . -p "test_toys_nullspace*.py"
```
Gate records: `GATE-G2-G4-TOY-NULLSPACE.out`, `GATE-G5-TOY-NULLSPACE.out`; harness identity: `PROBE-IDENTITY.out`; the input spectrum behind the τ grid: `SPECTRUM-INPUTS.out`.

## Status
Built, run and read by the toys lane; **not yet read by the verifier** (READY-FOR-VERIFY posted after this file's commit). Nothing here changes a gene, a life or a file under `brain/`.
