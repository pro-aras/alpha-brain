# VERDICT KW-1 — a knowledge web with true metadata, random growth under a budget, and memories of the self, tested small

*Claude (Opus 5.5, the seat, alone), 2026-09-29 22:59 +0400. The law: `PREREG-KW-1.md` (signed 865adcf, AMENDMENT 1 before any run). Every figure below is copied from the readings the tools wrote (`records/TOY-READINGS.md`, `records/SHELF-READINGS.md`, `records/SELF-READINGS.md`, and their JSON beside them); none is typed from memory. The code: `genome/web.py` and `tools/web/kw1_*.py` on the branch `knowledge-web`.*

## The verdict in six lines

1. **The metadata can be kept TRUE.** Every count the web and the self hold equals a recount from the record, for all six rules on the toy and on the organism's shelf, and a planted change of one count is caught every time (G1, K10).
2. **Memories about itself, placed by us before its life, are tested by that life.** The three true ones were kept; the two false ones were DEMOTED, one at scene 29 and one at scene 279 (K9 PASS).
3. **The organism's own web of heard words is a SMALL WORLD, as a human's is:** clustering 0.397 against 0.018 for a random web of the same size, average path 3.32 steps against 3.69 (a reading).
4. **Random growth under a tight budget does not store what an unbounded web stores.** At 2 edges a word the random rule S kept 0.238 of the planted associations against 0.914 (K1 FAIL).
5. **The kind of randomness matters.** Randomness in WHEN an edge is made adds nothing (S 0.238 against the rule without it, L 0.239). Blind random sprouting kept only by use, the brain's own rule, is the best budgeted rule on the toy: recall 0.294 and precision 0.736 against S's 0.238 and 0.542, better at 9 of 10 seeds and 10 of 10. It fails at the shelf's vocabulary of 826 words (a reading).
6. **The web predicts speech the organism has not heard yet, but less than the bar asked:** its associations recur there 1.75 times as often as chance pairs, against a bar of 2 (K6 FAIL). A shuffled stream reads 0.96 (K7 PASS), so the 1.75 is real.

## The gates

| Gate | Reading | Result |
|---|---|---|
| G1 FAITHFUL | toy (POSITIVE, seed 1): 0 recount errors for H, F, L, S, R, S0; shelf (the growth part, seed 1): 0 for all six; a planted one-count change caught on both | PASS (for S0, nodes only: its evidence is random by definition, `genome/web.py:recount_errors`) |
| G2 DETERMINISTIC | S twice at one seed: byte-identical; S at another seed: different | PASS |
| G3 BUDGET | 150 budgeted toy runs and 42 shelf runs: no run held more than B edges | PASS |

## The toy (V 60 words, planted sets of 117 to 120 pairs, B = 120, 10 seeds)

| Rule | Recall of the planted pairs | Precision | Consolidated | NULL world: consolidated (all false) | CHANGE world: new set | CHANGE world: old set |
|---|---|---|---|---|---|---|
| H, keeps everything | 0.914 | 0.693 | 156.6 | 68.6 | 0.635 | 0.813 |
| F, first come | 0.143 | 0.907 | 18.7 | 2.1 | 0.050 | 0.131 |
| L, least evidence out | 0.239 | 0.564 | 50.4 | 25.7 | 0.086 | 0.214 |
| S, random when made | 0.238 | 0.542 | 51.8 | 25.9 | 0.083 | 0.213 |
| R, blind random sprouts | 0.294 | 0.736 | 47.6 | 17.1 | 0.133 | 0.233 |
| S0, the null of S | 0.070 | 0.071 | 116.7 | 115.4 | 0.069 | 0.066 |

| Mark | Reading | Result |
|---|---|---|
| **K1 RANDOM GROWTH STORES** | S recall 0.238 against 0.8 × H = 0.731; S precision 0.542 against H − 0.05 = 0.643 | **FAIL** |
| **K2 NO INVENTION** | NULL world: S 25.9 consolidated against H + 2 = 70.6 | PASS |
| **K3 THE NULL IS BLIND** | S0 recall 0.070 against a bar of 0.203; S0 on the shuffled toy stream 0.061 | PASS |
| K4, S against L | recall 0.238 against 0.239 (better at 4 seeds, worse at 5); precision 0.542 against 0.564 (3 against 7, p 0.34) | a reading: randomness in when an edge is made changes nothing |
| K4, R against S | recall 0.294 against 0.238 (9 against 1, p 0.021); precision 0.736 against 0.542 (10 against 0, p 0.002) | a reading: blind sprouts kept by use are better |
| K4, L against F | recall 0.239 against 0.143 (10 against 0); precision 0.564 against 0.907 (0 against 10) | a reading: turnover buys recall and costs precision |
| K5 CHANGE | only H learns the new set well (0.635); every budgeted rule keeps little of either set | a reading |

**Why K1 failed, read from the numbers.** The budget B = 2V = 120 turned out to EQUAL the planted set (117 to 120 pairs), because every word draws 2 associates. The budgeted rules keep about 50 edges consolidated and spend the rest of the budget on silent edges that are still being tested, so they could never hold the whole set. The law set B from the vocabulary without comparing it with the planted set; that is the law's defect, found at the read and not repaired after it. KW-2 sets the budget against the world's size of truth.

**Why R wins on the toy** [Likely]. An edge made BY a co-occurrence counts that co-occurrence as its first evidence, so chance pairs start one step from consolidation. A blind sprout starts at zero and is judged only by what happens AFTER it exists: a hypothesis stated before its data. It also turns over once a word instead of up to three times.

**Why R fails on the shelf** [Certain, arithmetic]. With 826 known words a blind sprout hits a given associate about once in 825 tries; R consolidated 35.8 edges there against S's 346.4.

**The consolidation test still invents.** Over 20,000 words of a world with NO associations, H consolidated 68.6 edges (3.9 % of the 1,770 pairs). The Poisson tail at 0.001 is applied at every evidence event of a pair, about 34 looks each, so the per-pair false rate is about 34 × 0.001. A sequential test that spends its error across looks is owed (KW-2).

## The organism's shelf (the words alpha4-1 heard in its first 12 hours)

15,222 words heard; the first 9,133 grow the web (826 distinct words, B = 1,652); the last 6,089 are the held-out truth; the held-out part holds 1,522 strong pairs among the words the web knows.

| Rule | Consolidated | Enrichment in unheard speech | Recall of the held-out's strong pairs |
|---|---|---|---|
| H | 560.0 | 1.80 | 0.063 |
| F | 123.0 | 1.73 | 0.011 |
| L | 303.0 | 1.70 | 0.032 |
| S (10 seeds) | 346.4 | 1.75 (1.66 to 1.86) | 0.040 |
| R (10 seeds) | 35.8 | 1.73 (1.30 to 2.56) | 0.005 |
| S0 (10 seeds) | 64.9 | 1.17 (0.00 to 5.13) | 0.000 |
| H, the growth part SHUFFLED | 106.0 | 0.95 | — |
| S, the growth part SHUFFLED (10 seeds) | 83.1 | 0.96 (0.88 to 1.12) | — |

| Mark | Reading | Result |
|---|---|---|
| **K6 IT PREDICTS SPEECH NOT YET HEARD** | S 1.75 against the bar of 2 (and against 0.8 × H = 1.44, which it clears) | **FAIL** |
| **K7 THE INSTRUMENT FINDS NOTHING IN A SHUFFLE** | H 0.95, S 0.96 | PASS |
| K8 the web's shape | H: 251 words, 560 edges, clustering 0.397 (a random web of that size: 0.018), average path 3.32 (random: 3.69), hubs «the» 81, «a» 44, «and» 40; S: 188 words, 326 edges, clustering 0.386 (random 0.019), path 3.54 (random 4.21) | a reading: a small world |
| K8 what it holds | S's strongest: in–the, of–the, on–the, has–the, a–the, pond–the, is–it, a–is, will–you, man–the, girl–illustra(tion), do–you, dog–the, letters–the | a reading: the primer's own phrases |

## The self (the closed lean life `inh-b-t10000`, 10,000 training canvases)

| Claim, placed by the seat before the record was read | Quantifier | Confirmed | Contradicted | End | First demoted at scene |
|---|---|---|---|---|---|
| T1 «I look at no more than four places on a canvas.» | always (0.05) | 10,000 | 0 | trusted | — |
| T2 «The parent says at most one word of each kind at a time.» | always (0.05) | 9,750 | 0 | trusted | — |
| T3 «Usually, what I expect is what the parent says.» | usually (0.70) | 7,630 | 2,120 (share 0.783) | trusted | 522 (then recovered) |
| F1 «I see every thing the parent names.» | always (0.05) | 8,710 | 1,039 (10.7 %) | **demoted** | 279 |
| F2 «The parent always says three words.» | always (0.05) | 2,508 | 7,492 | **demoted** | 29 |

| Mark | Reading | Result |
|---|---|---|
| **K9 LIFE KEEPS THE TRUE AND DEMOTES THE FALSE** | as the table | PASS (T1 was a positive control known before the run, PREREG §0) |
| **K10 THE LIVED SELF IS TRUE** | its lived rates equal a recount; a planted change caught | PASS |
| K11 knowing what it knows | 398 pointing items (353 right, 45 wrong): the type-2 area of its lived reliability is 0.702; the null's 95th percentile is 0.720 | a reading, UNDERPOWERED (45 wrong items), not above the null |

**What its lived self says about itself** (per word: how often the word named something it expected that word for): circle 1,599 of 1,634 (0.98), square 0.96, star 0.96, triangle 0.94, cross 0.91, big 0.90, small 0.87, green 0.85, yellow 0.84, blue 0.78, red 0.78, white 0.77, **ring 1,480 of 2,124 (0.70)**, dax 0 of 1. So it knows where it is weak: it most often fails to expect «ring» when the parent says it.

**F1's rate beside the eye's own measure.** F1 was contradicted on 10.7 % of the canvases. The bench measured the eye missing a named thing on about 11 % of scenes (DIAG-LOOK-AGAIN). The proxy also counts misnaming (ring against circle), so the closeness is a reading, not a proof [Likely].

## What changes

1. `genome/web.py` (the web, its metadata, six growth rules, the self node, quantified claims) goes to master: it changes no behaviour of any life; no genome line uses it yet.
2. **KW-2, owed:** a budget set against the world's size of truth (4× and 10× the true set, not 2V); a sequential consolidation test that spends its error across looks; sprouting steered to recently co-active words (R's prospective test with S's reach); the self's reliability used to decide when to ask (the stage-2 design's part A).
3. The shelf's web and the self node enter a LIVING body only by a later law behind a genome line.

## What this does not show

- Nothing ran inside a living body: every web grew from a closed record.
- One toy family, one shelf stream (the first 12 hours of one life), one lean life for the self.
- K11's question (does its self-knowledge predict its errors) is not answered: too few errors.
