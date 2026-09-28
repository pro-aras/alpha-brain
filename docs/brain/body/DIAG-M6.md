# DIAG-M6 — why «learn a new word from one meeting» reads chance, and what would repair it

*Claude (Fable 5.1, the seat), 2026-09-28 20:35 +0400. Read-only diagnosis on the scored run's caches (redrawn, byte-identical: `diag/cache_identity.out`, 42 caches, 0 differing, the planted bit caught). Every number below is a READING on the fresh test set, which has now been read four times. It names a cause. It grades no fix (PREREG §7: a fix is graded on a set never used).*

## In plain words
1. **The one meeting is not the problem at two seeds.** At 20261102 and 20261103 the brain wrote «dax» to the right thing, the moon. At 20261101 the eye never looked at the moon; «dax» was written to the green square beside it. That seed cannot be graded.
2. **The law answers a young word with an inside / outside test, not with a distance.** A word met fewer than 3 times scores each thing 0 (inside its band) or −∞ (outside). Every score on the covered items is one of those two values. When no thing or several things are inside, the item's tie generator picks. That is a coin toss.
3. **The plain distance is not enough either.** One meeting stores the thing's colour, size and place with its shape. Ranked by plain distance, seed 20261103 reads 0.552.
4. **The reader's own learned metric repairs most of it.** Ranked by distance under the covariance the brain pooled from its OWN stored meetings, pointing reads 0.963 and 0.759.

| world seed | the law | the law by things inside the band (right / asked) | nearest, plain distance | nearest, the reader's metric (its one-alone type) |
|---|---|---|---|---|
| 20261101 | 0.655 (19/29) — NOT GRADABLE | none 19/27 · one 0/2 | 0.172 | 0.103 |
| 20261102 | 0.778 (21/27) | none 3/7 · one 17/18 · two or more 1/2 | 0.889 | **0.963** (26/27) |
| 20261103 | 0.483 (14/29) | none 3/6 · one 4/10 · two or more 7/13 | 0.552 | **0.759** (22/29) |

Seed 20261101's 0.655 is luck: 27 of its 29 items have nothing inside the band, so the tie generator chose. It shows why that seed must stay NOT GRADABLE.

## Predictions, written before each run, and what happened
| # | prediction | result |
|---|---|---|
| band 1 | the scores hold only 0.0 and −∞ | **held** |
| band 2 | with exactly ONE thing inside the band the law is right nearly always | held at 20261102 (17/18); **FAILED at 20261103 (4/10)** |
| band 3 | with none or several inside, the law is at chance | held |
| band 4 | nearest-by-distance beats the law at 20261103 | held, weakly (0.552 against 0.483) |
| metric 1 | the ear's one-alone type is the shape type at every seed | **held** (heard alone 2,502–2,555 times; the other types 0) |
| metric 2 | nearest under that type's metric reads ≥ 0.85 at both gradable seeds | held at 20261102 (0.963); **FAILED at 20261103 (0.759)** |
| metric 3 | the colour and size types' metrics read LOWER than the shape type's | held at 20261102 (0.889, 0.852); **FAILED at 20261103 (all three 0.759)** |
| metric 4 | at 20261101 every metric stays low | held (0.10–0.17) |

**What the failures say.** The gain does not come from a «shape bias». At 20261103 any of the brain's three learned metrics gives the same 22 of 29. The gain comes from measuring with a LEARNED metric at all: one that gives less weight to what varies freely inside every word (place, the other attributes). Whether the type matters is not settled by these readings.

## The fix this points to (F-M6, not built)
A young word points at the thing NEAREST its one stored meeting under the reader's own metric. «None» stays the band's job. One difference: the score of a word under 3 meetings. Every mature word answers as today.
- Reading on the used set, pooled over the two gradable seeds: 48 of 56 = 0.857, against the law's 35 of 56 = 0.625.
- It must be graded on test seeds never used (PREREG §7), with M1, M2a and M3 not lower than the law's.
- It does nothing for a meeting the eye never saw. That needs the look-again act.

## Files
`tools/brain/diag/diag_m6.py`, `diag_m6_band.py`, `diag_m6_metric.py`; their outputs in `docs/brain/body/diag/`.
