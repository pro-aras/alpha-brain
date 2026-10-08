# PREREG-EAR-COVER-CAP — the calibration cliff dies: the ear's type cover, bounded, byte-identical below the bound

*Law before code (RULES law 1). Author: Kimi K3 (kimi-code, acting seat, alone — Ahmad's standing words of
2026-10-05). Ordered by the record: VERDICT-OPEN-WORLD-4 (FAIL-COST) found the organism's own calibration
cliff — `Ear.cover` → `_maximal_cliques` (brain/scene/learners.py:198–214, Bron–Kerbosch enumerating EVERY
maximal clique) explodes over a real open-world vocabulary at the brain's first calibration cadence (159
words / 97 mature / 565 pairs at the knee, canvas 967 of the V3 tape; OOM at 4G, reproduced four times,
once by the seat's own negative control). It is the mouth's 2^N cliff's own cousin; the mouth-cap's
pattern is this law's form. It gates PREREG-ALPHA-6's launch (its AMENDMENT 1, prerequisite (a)).*

## 0 · The question, what a pass settles, what it cannot

**The question.** Can the brain calibrate over open-world vocabularies — the type cover's MECHANISM kept
(the exclusion graph; the greedy largest-clique cover; the deterministic tie-break), the enumeration's
cliff dead on every path, byte-identity below a declared bound, and the bounded form's difference above it
measured and printed, never hidden?

**A pass settles:** (i) below the declared bound the full Bron–Kerbosch runs VERBATIM — byte-identical
types on every existing fixture, tape, and life vocabulary; (ii) at and above the bound the DECLARED
bounded form runs — the same greedy cover with a polynomially-bounded search — completing the knee's real
graph inside §6's bar; (iii) the downstream contract holds everywhere: a partition of the mature words,
each type a mutual-exclusion clique, deterministic order; (iv) the instrument CAN fail (a planted unique
maximum found; a doctored form caught); (v) the organism's suites stay green. **A pass opens:** the V3
bench's deferred marks (its AMENDMENT 1 re-prices with this law's sha) and PREREG-ALPHA-6's prerequisite
(a) — the launch may proceed.

**It cannot settle (each said now):** that the bounded form's types ARE the enumeration's above the bound
— the maximum-clique search is NP-hard and the bounded form is a declared, deterministic, bounded search;
where both can run their agreement is MEASURED and printed (M-AGREE), and where they differ the bounded
form is the law's declared form, never a silent approximation; anything about the READER's downstream
behavior at scale (the types feed it unchanged — its own later readings); any new capability (this law
changes one search's cost form, nothing the organism MEANS).

## 1 · The mechanism today (the code map, never re-designed here)

- `Ear.cover(words)` (learners.py:198–210): the exclusion graph (edge iff the pair was never heard in one
  utterance, `count(w,w′) == 0`); GREEDY: the LARGEST maximal clique of the remaining words becomes a type
  (ties → the lexicographically smallest sorted tuple), its words removed, repeat; a lone word is its own
  type. The types feed `calibrate_r` → `_reader_state` (learners.py:653, 669–): per type the pooled
  covariance reader, per word its band.
- `_maximal_cliques` (learners.py:213–229): Bron–Kerbosch with a pivot, listing EVERY maximal clique so
  the greedy can pick the max — the cliff (the list is the memory bomb; the search is the time bomb).
- Callers: `calibrate_r` (the production path), the bench runners (run.py, run_tmem1/tmem5), the toy, the
  tests. The fix lives INSIDE `cover`, so every caller inherits it; no caller changes.

## 2 · The build (brain/scene/learners.py ONLY, tests first — NOT a pinned file, no window)

1. **The declared bound `COVER_FULL_BELOW = (W0, E0)`** — words and exclusion edges. The bound LANDS FROM
   THE MEASURED CURVE, never guessed: the build's own probe runs the full enumeration over a declared
   ladder of real and synthetic graphs; W0/E0 = the largest ladder step where the enumeration completes
   under 60 s CPU and 1 GB, then HALVED (the declared margin). The probe's curve is printed in the record;
   the bound is a module constant beside MOUTH_BUDGET's own form; **never tuned after any reading.**
2. **Below the bound** (`len(words) ≤ W0` AND `edges ≤ E0`, both O(1) from the ear's own counters): the
   full Bron–Kerbosch runs VERBATIM — the clause `if` guards it; nothing else on that path changes a byte.
3. **At and above the bound — the DECLARED bounded form** (the same greedy cover, the same tie-break,
   only the search replaced): for each start word in sorted order, grow a clique greedily — candidates
   are the current members' common exclusion-neighbors; take them in sorted order; add each iff it is
   exclusion-adjacent to EVERY current member. Take the largest grown clique over all starts; ties → the
   lexicographically smallest sorted tuple (the enumeration's own tie-break). Then the cover loop
   continues exactly as today. Cost is polynomial by construction (per start ≤ V steps of set
   intersections; the implementation's own bitset or sorted-set form is the build's detail inside THIS
   declared algorithm); the deterministic order is total (no hashing anywhere).
4. **The record's prints:** which path ran (below/above) journaled with each cover call's counts; the
   knee's real graph run printed (the types' sizes, the price); the scaling curve over declared synthetic
   sizes (1×, 2×, 4× the knee's) printed beside.

## 3 · The gates (instrument)

| gate | asserts | read on |
|---|---|---|
| **G-BYTE** | below the bound: types byte-identical to the pre-law code on every existing test fixture, on the OW-1/2 bench tapes' ear vocabularies, and on a scene life's 25-word ear; the pre-law module loaded from git history as the oracle | the bench |
| **G-KNEE** | the knee's REAL exclusion graph (the V3 tape's own, rebuilt by the bench's own probe form): the bounded form COMPLETES ≤ 60 s CPU and ≤ 500 MB at SLOT_MEM 4G; the cover is VALID (a partition; every type a clique of the exclusion graph — verified against it; two runs byte-identical) | the bench |
| **G-PLANT** | a synthetic exclusion graph with a planted UNIQUE maximum clique: the bounded form finds exactly it; a doctored form (one start skipped) misses it and is CAUGHT; **M-AGREE:** over every graph the enumeration can still reach (the fixtures + a declared synthetic ladder), the bounded form's types vs the enumeration's — the AGREEMENT measured and printed (a disagreement is a reading of the declared semantics difference, never a gate) | the bench |

## 4 · The marks

| # | mark | what is read | bar |
|---|---|---|---|
| **M-BYTE** | G-BYTE's whole surface | byte-identical everywhere below the bound |
| **M-KNEE** | G-KNEE's price and validity | inside §6's bar; the cover valid; deterministic ×2 |
| **M-AGREE** | the measured agreement over the reachable band | printed (the rate, the disagreements named) — a READING |
| **M-SCALE** | the declared synthetic scaling curve (1×/2×/4× the knee) | printed; the 4× point COMPLETES inside a declared wall (≤ 20 min CPU at 4G — the life's own horizon) |
| **M-SUITES** | the brain/scene suites + the tools suite on the final bytes | green (the brain/scene learner suites whole; tools through slot) |

## 5 · The verdict rule (TOTAL and ORDERED)

| # | the marks read (in this order) | verdict |
|---|---|---|
| 1 | a gate fails (G-BYTE, G-KNEE, G-PLANT) | **VOID** — an AMENDMENT names the cause |
| 2 | M-KNEE fails | **FAIL-COST** — the bounded form does not hold the knee; re-thought in a NEW law |
| 3 | M-SCALE's 4× point fails | **FAIL-HORIZON** — the form holds today and not the life's horizon; named, the next scale law scoped |
| 4 | M-SUITES fails | **FAIL** — named |
| 5 | the gates hold, every mark inside its bar | **PASS** — the calibration cliff is dead; V3's deferred bench and Alpha 6's prerequisite (a) open |

## 6 · The price and the stop rules

- Every job through `slot` (SLOT_MEM=4G; the form `SLOT_MEM=4G bash /data/dev/swarm/bin/slot kimi <label>
  -- <cmd>`); ONE bench job at a time beside the ON replay (12G — the box's only heavy job). The knee and
  the scaling points are seconds-to-minutes; the suites ≈ 7–15 min each.
- **STOP:** S1 any job's CPU > 1 CPU-h → STOP; S2 any job's peak > 3,800 MB at 4G → STOP (the bound and
  the bar re-thought — never loosened); S3 a gate → VOID, an AMENDMENT names it.

## 7 · Never

No enumeration of all maximal cliques anywhere at/above the bound (the cliff stays dead); no tuned bound
or tie-break after a reading; no semantics hidden (the bounded form's difference is measured and printed —
M-AGREE); no caller edits (the fix lives inside `cover`); no genome/parser/machinery.py touch (brain-side,
unpinned); no new capability smuggled (this law changes one search's cost form — nothing the organism
MEANS); a FAIL told honestly is a result.

Signed: **Kimi K3 (kimi-code, author and acting seat, alone — Ahmad's standing words of 2026-10-05;
ordered by the record: VERDICT-OPEN-WORLD-4's FAIL-COST)**, 2026-10-08 (the stamp read from `date` at
signing), on this file's sha256 carried by the SEAT-LINE file beside it in `docs/organism/records/ear-cover-cap/`.
