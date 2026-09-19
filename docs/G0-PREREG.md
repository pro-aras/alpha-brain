# G0 — THE GENOME, rung 0 · DRAFT FOR AHMAD'S APPROVAL (no code until his yes)
**A readable genome + fixed machinery grows an organism, on its own, from words and pictures shown together — and the organism answers questions from what grew.**

edit: Claude (Fable 5.1), 2026-09-19 15:0x +04 — written on his 14:43 word: «We start with a small genome experiment in python … raise something with set of instructions like human dna or genetic code, and it grows on it's own … then we test it with few words and pictures and ask questions related to it. If it works then we continue.» The chart beside this file (`docs/chart/`) is the same design drawn.

## 0 · Why this, and what the record already says
- **His words:** Alpha 3 was fed words and does not understand; C++ before a working system was costing us; Python can be tested for something that works.
- **What Alpha 3 lacked, measured 09-19:** words never met pictures (the eye read letters, the reader read text; one thread, one duty per pass); no cell ever tied a picture to a word; two days on one unanswerable question.
- **E48b (FAIL on its conjunction — the digits, a context defect D31 cured; its arm A1 ported byte-exact and alive three days):** a LOCAL, ONLINE growth rule works — prototypes born on novelty and on error under a BUDGET (never a cap that eats the least-used), a delta rule on grown edges, synaptic scaling, pruning under a floor, NO disuse decay (#227). That rule becomes the first genes.
- **E29 (FAIL):** a genome that grows the SHAPE of a gradient-trained net lost to a hand-designed shape, and 48 random genomes beat the evolved one. **This genome never encodes a network's shape for backprop; it encodes the local rules an organism lives by.** The random-genome control stays (§4) so the same trap is visible if it recurs.

## 1 · The genome — one readable file, one gene per line
The genome is TEXT he can read and edit. Fixed **machinery** (`genome/machinery.py`, the ribosome) reads it and runs it; the genome never changes during a life. Six gene families:

```
SEED   20260919
# BODY — what senses exist and what areas the organism has
SENSE  eye    24x24 grey             # a picture is 576 numbers
RETINA centre pool3 unit             # FIXED front, not learned (his §2): centre on the ink's centroid, 3x3 mean pool -> 8x8 = 64, unit length
SENSE  ear    letters 8              # a word is up to 8 letters, one-hot per position (8 x 27 = 216), unit length
AREA   sight  from retina
AREA   words  from ear
MEET   sight  words                  # rung 0: the meeting is EDGES ONLY — a weight matrix sight-cells x word-cells; no convergence cells yet
# GROW — when a cell is born (E48b's arm-A1 rule, the one ported and lived)
BIRTH  novelty  cos<THETA_N          # no cell in the area resonates -> a new cell holds the input. THETA_N is NOT 0.90 by habit:
                                     # it is set by gate G-a below from the world's own within-thing / between-thing cosine bands
BIRTH  error    misfires 3           # a cell keeps answering wrongly -> a new cell is born beside it
BUDGET 400 per arrival               # per ARRIVAL (a new set of things), never per stage; set so it does NOT bind in rung 0;
                                     # births_refused is printed beside every birth count. Never replace a cell (#227)
NMAX   2000
# WIRE — how cells connect
KWTA   5                             # five winners per area per moment
HEBB   window 1                      # cells active in the SAME moment across areas get an edge
DELTA  lr 0.05                       # the edge grows when the pairing is right, shrinks when wrong
# SHRINK — what is removed (the wrong and the redundant; never the merely unused)
PRUNE  w<0.02 after 3 chances        # 0.02 of the delta rule's unit scale (weights are bounded to [-1, 1] by the rule)
MERGE  cos>THETA_M same-answer       # THETA_M set by gate G-a too (above the within-thing 95th percentile)
SCALE  every 1000 moments            # synaptic scaling (homeostasis)
# STAGE — development in order (critical periods)
STAGE  1 senses   moments 0..200     # sight and words grow; no cross-area wiring yet
STAGE  2 meet     moments 200..      # cross-area wiring (HEBB) is permitted from here
# ANSWER — how a question is answered from what grew
RECALL k=1                           # activate one side; read the strongest edge to the other
ABSTAIN second/best > 0.85           # too close to call -> "I do not know this" (a RATIO of edge strengths, unit-free; frozen after the toy)
```

Everything above is a parameter of a mechanism the machinery already knows how to run; a gene the machinery does not know is refused at birth (the organism does not start), never silently ignored.

## 2 · The world (rung 0: synthetic, so the truth is known)
- **10 things:** circle, square, triangle, cross, ring, bar, dot, star, arrow, wave. Each has a **word** (its name) and **pictures**: 24×24 grey renderings with jitter — position ±3 px, scale 0.8–1.2, rotation ±15° where the shape has an orientation, noise σ 0.05. A held-out rendering is a NEW jitter draw never seen in development.
- **A moment** = a picture and its word shown TOGETHER (the present). The development stream: 10 things × 60 moments = 600, in a shuffled arrival order. Held-out: 10 × 20 new renderings.
- **Arrival 2 (retention):** 5 NEW things (moon, house, tree, cup, key) after the first 600 — the organism must keep the first 10 (E48b's Latin → Cyrillic shape).
- **Gate G-a, before any threshold is declared (#228b, #222a):** render the world, pass every picture through the RETINA gene, and print the cosine bands — within-thing (same thing, two renderings) and between-thing — as median / 5th / 95th percentiles. THETA_N is set BETWEEN the between-thing 95th percentile and the within-thing 5th percentile; if those bands overlap, the retina is too weak and that is reported before anything else runs (the fix is a stronger fixed front — a 3-orientation filter bank — never a learned one). THETA_M is set above the within-thing 95th percentile. Both numbers are written into the genome file with the bands beside them.
- **The toy before the world (#222):** a 2-thing world (circle, bar) must reach Q1 = 1.0 before the 10-thing world is touched. If the toy fails, the machinery is wrong, not the genome.

## 3 · The questions (asked after development; answered from the grown structure only)
| Q | asked as | answer comes from | chance |
|---|---|---|---|
| Q1 what is this? | a held-out picture | strongest edge from the active sight cells into words | 0.10 |
| Q2 show me a «word» | a word | strongest edge from the word cells into sight; scored by the retrieved cell's thing | 0.10 |
| Q3 is this a «word»? | picture + word, half true | the edge's margin against the abstain floor | 0.50 |
| Q4 which of these two is a «word»? | two pictures + a word | the larger edge | 0.50 |
| Q5 what is this? | a thing NEVER shown (a spiral) | must ABSTAIN — «I do not know this» | — |

**The truth stays outside him.** The machinery keeps a scoring ledger (which thing each sight cell was born on, which word each word cell holds) OUTSIDE the organism; no gene, no cell and no answer road ever reads it. Q2 is scored by that ledger; the organism only ever returns a cell. (The belief-scope law of the estate.)

Q5 is metacognition's first cell: an organism that cannot say «I do not know» becomes Alpha 3's two days on one question.

## 4 · Twins and controls — each blind to exactly ONE thing (#228)
| twin | what it lacks | must read |
|---|---|---|
| T-shuffle | words paired at random with pictures PER MOMENT during development (a fresh random word each moment, not one fixed wrong permutation) | Q1, Q2 at chance (the association is learned from co-occurrence, not from geometry) |
| T-frozen | GROW genes off after the embryo's first 10 cells | far below the mark |
| T-nowire | HEBB off (areas grow, never meet) | Q1, Q2 at chance |
| T-random-genome ×20 | every numeric gene drawn uniformly within these bounds, declared now: THETA_N in [0.50, 0.99], misfires in [1, 8], BUDGET in [50, 800], KWTA in [1, 12], lr in [0.005, 0.3], PRUNE floor in [0.001, 0.2], THETA_M in [0.90, 0.999], SCALE in [100, 5000], STAGE-1 length in [0, 400], ABSTAIN ratio in [0.5, 0.99]; seed per draw = 1..20 | the DISTRIBUTION of the marks; the design genome's rank is reported (E29's control) |
| PLANT | one made-up pair («zog» + a unique picture) shown 5 times with its OWN budget (#228a) | Q1 answers «zog» |
| NULL PLANT | a pair shown 0 times | abstains |

Ceilings before the run: Q3/Q4 chance 0.50; Q1/Q2 chance 0.10; T-shuffle's own noise band is measured on the twin's structure before the bar in (ii) is read.

## 5 · The marks (conjunctive; bars declared here, before the toy's numbers are seen)
1. **(i) it answers:** Q1 ≥ 0.80 and Q2 ≥ 0.80 on held-out renderings; Q3 ≥ 0.85; Q4 ≥ 0.90.
2. **(ii) the meeting is real:** T-shuffle Q1 ≤ 0.20 and T-nowire Q1 ≤ 0.20.
3. **(iii) growth matters:** T-frozen at least 30 pp under (i).
4. **(iv) it grows on its own:** cells born ≥ 50 from 0 by the stream alone (the seat writes none) with births_refused = 0 (the budget did not bind, so the count is the world's, not the budget's); a 5-thing world births FEWER cells than the 10-thing world; pruned ≥ 5 % of edges born; 0 cells removed for disuse.
5. **(v) it keeps what it learned:** after arrival 2, Q1 on the first 10 things within 5 pp of before.
6. **(vi) it knows what it does not know:** the plant answered, the null plant abstained; Q5 abstains ≥ 0.80 on unseen things with false abstention ≤ 0.20 on seen ones.
7. **(vii) same genome, same stream, same organism:** two lives byte-identical (sha256 of the state) — the replay gate.
8. **(viii) cost:** one life ≤ 5 min on this box, one process, measured at the run's own shape.
9. **(ix) not luck:** the design genome ranks in the top quartile of the 20 random genomes on (i). If a random genome beats it, that is the finding, reported as such.

## 6 · What rung 0 does NOT claim
No sentences, no reasoning modes, no reward signal, no sleep or replay, no evolution (the genome is hand-written), synthetic pictures. Each of those is a later gene family on the SAME substrate — the chart's coverage table says which rung.

## 7 · Predictions, written before any run
(i) likely PASS — E48b's rule reads 0.79–0.96 on harder frames. (ii) PASS. (iii) PASS. (iv) births 100–300; **pruning may FAIL the 5 % bar** (E48b pruned 1 %) — if so, the bar is read as a finding about the rule, not moved. (v) PASS under the budget rule. (vi) the uncertain one: the margin rule is new; a false-abstention rate above 0.20 is the likely failure. (vii) PASS by construction (numpy, fixed seed, no threads). (ix) unknown — E29 says do not assume.

## 8 · After rung 0
- **Rung 1 — his test:** a folder door `/data/dev/genome/world/<word>/` (one tree: code, docs, world) where he drops a few pictures per word (5 or more each, any size; resized to 32×32 grey); the organism develops on them; he asks through a small door: `ask what-is picture.png` · `ask show cat` · `ask is picture.png cat` · `ask which a.png b.png cat`. The log is his record. Same marks, his pictures, held-out by picture.
- **Rung 2 — a lineage:** mutate the genome's numbers, select by the rung-0 marks on HELD-OUT families, E29's random-genome control kept; only if rung 1 passes.
- **Later gene families (the chart, right column):** a REWARD gene (an answer graded by an outcome the organism perceives); a SLEEP gene (replay of the day's moments into the slow store); a PREDICT gene (the organism says what comes next and files the error); a SENTENCE gene (order over words); a SENSE for sound (E52's cochlear front, on master) — each its own PREREG.

## 9 · Order and cost
1. His approval of this design (the chart is the same thing drawn).
2. The machinery + the world renderer + the toy gate (2 things → 1.0) — Python 3.14, numpy, PIL, one process; ~2 h.
3. The 10-thing life, the twins, the plant, the marks → VERDICT with every number and every twin, PASS or FAIL as read.
4. Rung 1's folder door for his words and pictures.

**Decisions his (with my recommendation):** D-G1 development only in rung 0, evolution in rung 2 (recommended: yes — one thing at a time, and E29 says evolution without a working substrate rewards luck). D-G2 the rung-0 world synthetic with known truth, his pictures in rung 1 (recommended: yes — the toy must be solvable before the world is real).

## 10 · Run clauses — declared before any organism runs (edit: Claude (Fable 5.1), 2026-09-19 15:59 +04, on his 15:53 «Ok go for it»)
Each of these was left open by §1–§9; each is decided HERE, before a number is seen, so none can become a moved bar (#228).
1. **RECALL needs resonance.** "Activate one side" means the lit side's best cell has cos ≥ THETA_N. If no cell resonates there is nothing to read and the organism abstains for the reason NOVEL. Two abstain counts are printed everywhere: by-novelty and by-ratio, so mark (vi) says which rule did the work.
2. **DELTA's right/wrong and BIRTH-error's misfire come from the moment alone.** Target = this moment's winners on the other side; a misfire = the cell's strongest existing edge is not among them. The ledger is never consulted (proved by the ledger-corruption plant, clause 12).
3. **Edge mechanics.** HEBB creates an edge at w = lr (a new edge is not under the prune floor on its first check). The delta rule is per cell: a winning cell's row moves toward 1 on the co-active winners and toward 0 on its other existing edges, lr 0.05, weights clipped to [−1, 1]; applied from both sides on the one shared matrix. PRUNE strikes (|w| < 0.02 → strike; ≥ 0.02 → strikes reset; 3 strikes → removed) and MERGE are checked on the moment's winners only. KWTA takes every cell when fewer than 5 exist. A newborn cell is a winner in its birth moment. Cells are prototypes and never move; MERGE keeps the lower id, averages the two rows, unions the masks.
4. **Q3 / Q4.** Q3 answers YES iff the given word's cell carries the top edge from the best sight cell and the reading is not an abstain; else NO. Its ceiling under this rule = 1 − ½ × (false-abstention rate on seen things), printed beside the 0.85 bar. Q4 reads the edge from each picture's best cell to the word's cell and picks the larger; a non-resonating picture reads 0; a tie is wrong.
5. **Plant and null plant.** After arrival 2, «zog» gets its own 5-moment arrival with a fresh budget; PASS = a majority of 20 held-out zog renderings answer «zog». «vex» (0 showings) PASS = a majority of 20 renderings abstain. A merged cell's ledger entry is the SET of things it was born on; the count of multi-thing cells is printed.
6. **Mark (iv)'s 5-thing life runs 600 moments (120 per thing)**, the same stream length as the 10-thing life, so "fewer births" measures variety, not length.
7. **SCALE every 1000 fires 0 times in a 900-moment life.** It runs, its count prints as 0, and the VERDICT marks it UNTESTED (#228 addendum 2), never passed.
8. **Two askings.** The five questions are asked at moment 600 and at moment 900 (questions never change him). Mark (i) is read at 900 — the final organism; mark (v) = Q1(first 10 things, 900) − Q1(first 10, 600) ≥ −5 pp. Both readings are printed.
9. **Gate G-a covers the ear too.** The ear's 27th symbol (blank) is shared, so 3-letter words agree on 5 of 8 slots (cosine 0.625). G-a prints the ear's maximum between-word cosine and THETA_N must exceed it; if the retina's bands force THETA_N below it, the ear encoding changes to blank = zero (8 × 26 = 208) and that change is stamped in the genome file BEFORE the run.
10. **One process, sequential lives,** OPENBLAS_NUM_THREADS = OMP_NUM_THREADS = 1. Six separate RNG streams: development renderings, held-out renderings, arrival-2 renderings, plant renderings, T-shuffle's word draws, the organism's own seed — every twin sees the identical picture stream.
11. **Noise bands before bars.** T-shuffle runs at 3 seeds and its Q1 band is printed before bar (ii) is read; T-nowire's abstain rate is printed beside its accuracy so (ii) reads as "no edges, no answers", not as geometry at chance. T-shuffle's births_refused is expected high (error births burn its budget); the design genome's must be 0 for (iv).
12. **Ledger-corruption plant.** The runner shuffles its own ledger labels after a life; the organism's state hash must be unchanged (it never read them). Planted control: a copy of a development rendering placed in the held-out set must be caught by the disjointness check.
13. **The replay gate** = two full lives (900 moments + the plant arrival) from the same genome and streams, sha256 over the fixed-dtype state arrays and counters identical.
14. **Centroid shift is zero-fill, never a roll.** Shapes with orientation (rotation jitter applies): triangle, cross, bar, arrow, wave, house, tree, cup, key, spiral, zog, vex; without: circle, square, ring, dot, star, moon.
