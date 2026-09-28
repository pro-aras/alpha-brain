# B1.0 — VERDICT (both seeds)

*edit: Claude (Opus 5.5), 2026-09-28 02:38 +0400 — written from the two graded records (b1-results-v4.1; `results-b1.0/20261001/results.sha256` a2d5565b…, `20261002/` 6ae789b9…), by the rules declared before the runs: §5.5 / R40 (a failed control VOIDS an arm), R39 (CONST is NOT GRADABLE where no sleep precedes the sitting), R44 + R51 (a missing null reads NOT GRADABLE), R45 (the D family at the floor, 50,000 per sleep; a fire stops the twin VOID by cost). Tapes: `/data/dev/brain-runs/b1/<seed>/` (ce0d65d9… / bcc7a4f5…). Runs: genome-wt-b1int 7fb1c85 (the D family, R45) and b1-a1teach (A1-TEACH, R46). Grader: genome-wt-b1-tape2 5bfe93b (its suite: Ran 402 … OK (skipped=3)).*

## In plain words
1. **No learner goes to the body (§6).** The three hybrids (A5, E′, F) are VOID by the identity control (C0a_SAME) at both seeds. The selection and D1 cannot be computed.
2. **The rule library D names letters in fonts it never saw, above both bars, on both seeds** (0.857 / 0.778 and 0.853 / 0.769), and explains its rules (U4b).
3. **D's relations pass against their null on seed 2:** AFTER 11/12, BEFORE 9/12, BETWEEN 10/12, TWO_AFTER 20/21, CHAIN 21/25, with the shuffled twin's band at 0.
   - On seed 1 the twin search stopped VOID by cost at 02:09:57 (R45), so D's relations read NOT GRADABLE there (R51).
   - Seed 1's readings, printed as readings, not passes: 12/12, 12/12, 10/12, 18/21, 14/25.
4. **D fails, at both seeds:**
   - refusing never-taught signs (U2a: 0 of 40 refused);
   - explaining from experience (U4a 0.0);
   - rejecting misuse (U5 0.04 / 0.14);
   - keeping what it learned (KEEPS).
   
   At one seed each: TRANSFER to the digits fails on seed 2 (11/18 against 13), and one meeting (U6) fails on seed 1 (2/10) but passes on seed 2 (6/10).
5. **The networks name at chance on both seeds.** A1 and its twins, A2, A3, A4 and A1-TEACH read U1a 0.035–0.038, about 1 in 26: one answer. A3 and A4 are VOID by CONST on seed 2. The cause is their answer readout (brain r2 CONCLUSION-R2, co-signed; B1.2 addresses it).
6. **The hybrids name through their non-library part.** E′'s U1a equals A0's exactly, and F's equals A5's (0.10–0.18). The part that names at 85 % (D) is not the one that answers NAME in them.
7. **CONST cannot be read on this tape for a sleep-only learner:** it is taught after the last sleep (R39). B1.1's tape moved it (R47), and there every learner fails it (VERDICT-B1.1).

## The instrument (0c) — sound at both seeds
KEY fails nothing. SHIFTED-KEY fails U1b and U2b (and the controls): a shifted answer stream cannot pass the graders.

## Every learner arm, by the letter
| arm | seed 20261001 | seed 20261002 |
|---|---|---|
| D (rule library) | read: fails U2a, U4a, U5, U6, KEEPS; U3 NOT GRADABLE (TWIN_VOID by cost, R51) | read: fails U2a, U3 TRANSFER, U4a, U5, KEEPS |
| A1, A1-TEACH, A1 twins, A2 (networks) | read: fail U1a (0.038), U1b, U2a, U2b, U3 … | the same |
| A3, A4 | read: fail U1a, U1b, U2a, U2b, U3 … | VOID by C0a_CONST |
| A5, E′, F (hybrids) | VOID by C0a_SAME (E′ and F: their relation nulls also VOID by cost) | VOID by C0a_SAME |
| A0 (cells) | read: fails U1a (0.126 / 0.098), U2a, U2b, U3 | read: fails U1a (0.164 / 0.130), U2a, U2b, U3 |

**The nulls:**
- Seed 2: every SHUFFLED-RELATION twin is complete (D's search closed 17/17 sleeps, 13:25:58; E′'s and F's loaders ran).
- Seed 1: SHUFFLED-RELATION:D was VOID by cost (marker `runs/20261001/SHUFFLED-RELATION_D/VOID-BY-COST.json`: sleep 10, 13.32 CPU-h, r 17.65 × 1.36 = 24.01 > 24). So D's, E′'s and F's U3 read NOT GRADABLE, TWIN_VOID (R44, R51).

## §6's decisions
- **The selection:** none. A5, E′ and F are VOID at both seeds.
- **D1 (i) F − A5 and D1 (ii) E′ vs F:** not computable (VOID).
- **D1 (iii) D − A1** (a diagnostic of readings):
  - seed 1: AFTER +100, BEFORE +91.7, BETWEEN +83.3, TWO_AFTER +85.7, OTHER_CASE +80, CHAIN +56, MIRROR +6.2, LOOP 0, VOWEL +10;
  - seed 2: +91.7, +66.7, +83.3, +95.2, +100, +84, +6.2, +7.1, +7.5 pp.
- **GROWS A1 − A1-FIXED:** 0 on every family at both seeds. Growth bought nothing at letters.
- **Memory Attention:** 0. The effect belongs to attention, not to the memory.
- **Examples to the bar (TWO_AFTER):** D 6; A1 and A1-MLC more than 36.
- **A1-TEACH (R46):** U1a 0.038, the same as A1 at both seeds. Teaching alone changes nothing.

## The predictions on the record (§6)
**The designer:**
- «A1-MLC needs ≥ 3× D's examples» — holds (more than 36 against 6).
- «A1 and F beat D by ≥ 10 pp on the perceptual families» — false at both seeds: A1 is never ahead on MIRROR, LOOP or VOWEL (families declared underpowered), and F is VOID.
- «F wins U3 overall» — not computable (F VOID).

**The seat:**
- «F wins U3 and U4b» and «E′ ties F…» — not computable.
- «D alone fails U1 and U6» — wrong on U1 (D passes U1a at both seeds); U6 fails on seed 1 only.

## What B1.0 settles, and what follows
**Settled:**
- The rule library names unseen fonts at both seeds, and relates letters against a clean null on seed 2. B1.1 repeated the naming at both of its seeds, and the relations against a complete null on its seed 1.
- The networks' one-answer collapse holds on both tapes.
- No hybrid passes its identity control, because its NAME and SAME answers come from different parts.

**Named, not yet declared (as in VERDICT-B1.1):**
- D's missing name constant;
- the networks' readout (B1.2, held by R50 until its design fixes are declared);
- a hybrid whose NAME answer comes from the part that can name.
