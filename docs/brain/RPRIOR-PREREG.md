# R-PRIOR · THE CHILDHOOD — can the brain get general structure from programs it makes itself? (PRE-REGISTRATION DRAFT)

*Drafted by the seat, Claude (Opus 5.5), 2026-09-26 12:43 +0400, on Ahmad's 12:18 word (verbatim: «yes go for the recommended reasoner first and try out the childhood as well»). DRAFT until the seat's dated §9 line, which comes after the price probe (§6). Nothing here is built yet. The reasoner (R-THINK, `RTHINK-PREREG.md`) runs first.*

## 0 · In ten lines
1. **The paper:** «Self-Play Pretraining with Zero Data», arXiv 2609.30063 (read on its own page, 2026-09-26). A generator proposes programs for a universal Turing machine, and a learner predicts their output bytes. The generator is rewarded when a program's gradient lines up with the learner's recent movement, which is its frontier. The paper reports three results: zero-shot loss on natural images, text and melody falls as a power law in self-play compute; in-context learning appears; and «facts about a particular world must ultimately enter through interaction with that world».
2. **Why it fits us:** it is structure without borrowed text (D-1, the pure road), with facts from the body. That is the childhood before the body's world.
3. **Why it matters now:** B1's first raw counts show the grown network (A1) at the plain cells' level on the letter-relation questions (A1 322, A0 334 of 3,484 test asks on seed 20261001), while the rule library answers 1,385. The relations are SEQUENCE skills (after, before, between, chains). Sequence skills are exactly what the paper claims a self-play childhood gives.
4. **Q1, does the micro version work here?** At this box's scale, does a self-play learner's zero-shot loss on natural bytes fall faster with compute than a learner fed a FIXED random-program prior and a learner with no childhood? Do reverse, stack and associative recall appear in context?
5. **Q2, does it help OUR brain?** Does A1, started from the childhood's recurrent core, learn B1's relation families better than A1 from random weights, on the same tape, graded by B1's own graders?
6. **Arms:** P0 no childhood · P1 a fixed prior (random programs, no generator learning) · P2 self-play (the paper's reward) · P2-SHUF, P2 with the reward's sign shuffled per batch (the reward's null).
7. **Honest scale:** our compute is about 10¹³ effective FLOPs, below the paper's smallest point (10¹⁴). A null here is WEAK evidence against the idea, and §8 says so before any run.
8. **The learner is A1's own kind,** a GRU core of the width B1's A1 ends at, so Q2 transfers the core itself. A transformer learner would answer a different question.
9. **Adoption:** the childhood enters the birth sequence as a CHILDHOOD phase of the genome only if Q1 and Q2 both hold at two seeds.
10. **The rest is on the record:** the price probe, the bars and their ceilings, and the seat's line (§9).

## 1 · The world — the machine and its programs
- **The machine:** a Brainf\*ck-like universal Turing machine, per the paper («a Brainf\*ck-like Turing-complete language: primitive instructions manipulate a byte-valued tape, implement loops, and read or emit bytes»).
  - Here it has the 8 classic instructions `> < + - . , [ ]` and an END token.
  - The tape is 256 byte cells, wrapping.
  - There is a step cap of 4,096 and an output cap of 128 bytes; a program that hits the step cap keeps its output so far.
  - There is no input stream; `,` reads 0.
  - Programs are up to 64 tokens. An unbalanced bracket is rejected at generation, never «fixed».
- **Its test:** 20 hand-written programs with known outputs, including a copy loop, a counter and a nested loop, must match byte for byte. A planted off-by-one interpreter must fail that test.
- **The data:** each program's output bytes are one training sequence for the learner. No natural data ever enters training (§3 checks it by hash).

## 2 · The arms (identical learner; only the stream differs)
- **The learner:** a byte-level GRU, 256-symbol embedding → GRU(H) → 256 logits. H = the median final `h_alive` of B1's A1 across seeds 20261001/20261002, read from their `summary.json` when both exist, so Q2 transfers a core of A1's own size.
  - It trains by next-byte cross-entropy with Adam(1e-3) and clip 1.0.
  - It uses one thread and nice 19.
- **P0 · none:** no childhood. The random init itself is the arm.
- **P1 · fixed prior:** programs sampled from the generator's INITIAL (untrained) distribution for the whole budget, like the paper's «fixed uniform Solomonoff prior».
- **P2 · self-play:** the generator is a small autoregressive policy over program tokens (a 1-layer GRU, width declared after the probe), trained by REINFORCE with a moving-average baseline.
  - The reward is the paper's: r_i = |⟨∇θ L(y_i, θ_e), P_e ⊙ (θ_⌊e/2⌋ − θ_e)⟩|, where P_e is Adam's diagonal step operator lr/√(v̂_e + ε) and the lookback is e/2.
- **P2-SHUF · the reward's null:** the same loop with the rewards permuted across the batch before the update. It shares P2's stream statistics, but its generator learns nothing from the learner.
- **Q2's arms are B1's A1 on B1's tape 20261001 and 20261002:**
  - A1-CHILD: the recurrent core (W_ih's byte half aside, W_hh and the biases) is taken from P2's learner; the input projection is re-initialised because A1's input is B1's step vector, not bytes.
  - A1-FIXEDPRIOR: the same, from P1.
  - A1: B1's own run is the random-init arm.
  - B1's graders and bars are used unchanged, and the §12 line of B1-PREREG is law for them.

## 3 · Controls — run first; a failing control VOIDS the arm, never «fails» it
- **(c1) The machine's own test** (§1).
- **(c2) The reward's three planted cases:**
  - A program the learner has MASTERED (trained to near-zero loss) must score near zero.
  - A program emitting uniform random bytes must score low.
  - A program one step beyond a mastered one must score highest of the three.
  - The rule is declared in §6 with numbers after the probe.
- **(c3) No natural data in training:** every training sequence's hash is checked against every evaluation sequence's hash, and a planted copy must be caught.
- **(c4) Replay identity:** the same seed gives the same learner state hash at every checkpoint, run twice, with a planted one-step divergence caught.
- **(c5) The in-context tasks have a known chance:** a learner with random weights reads at chance on each, measured, not assumed.

## 4 · The marks
- **M1 · transfer of the prior:** bits per byte on held-out NATURAL bytes, checkpointed along compute. The bytes come from three sources, all test material only (D-1 allows measuring, never teaching):
  - (a) the glyph renderings of B1's world as raw bytes;
  - (b) a public-domain book from the shelf, read and never trained on;
  - (c) the creature's own tape payload bytes.
  - The printed result is the fitted slope of loss against log compute for P0, P1, P2 and P2-SHUF, each with its standard error. A slope is fitted from the whole checkpoint series, never from two readings (SOLUTIONS #240 (4)).
- **M2 · in context:** reverse string, stack and associative recall, each at m ∈ {0, 1, 4, 16} examples, exact-match accuracy with n and its interval beside the measured chance (c5).
- **M3 · our brain:** B1's U3 relation marks (AFTER, BEFORE, BETWEEN, TWO_AFTER, CHAIN) and U1 (a) for A1-CHILD, A1-FIXEDPRIOR and A1, at both seeds. M3 is read only if M1 or M2 shows P2 ahead of P1. A prior that learned nothing cannot be the reason for a transfer.

## 5 · The decision rule (declared now; the numbers in §9)
- **ADOPT the childhood** (a CHILDHOOD phase before birth in the genome's birth sequence) only if all three hold at BOTH seeds:
  - P2's M1 slope is steeper than P1's AND P2-SHUF's by the declared margin;
  - M2 is above chance by the declared margin on at least two of the three tasks at m = 16;
  - A1-CHILD − A1 ≥ 5 pp on U3 overall, with no U3 family worse by more than 5 pp.
- **A PRIOR BUT NO TRANSFER:** M1 and M2 hold, but M3 fails. The byte-level childhood does not reach the brain's step format; the next road is a childhood trained in the step format itself, which gets its own pre-registration.
- **NOT AT OUR SCALE:** M1 and M2 do not separate P2 from P1. The null is recorded as weak (§8), and the idea waits for more compute. It is not discarded.

## 6 · The price probe (before §9; the box must be quiet or the figure says what it ran beside)
- The learner's tokens per second at H ∈ {64, the B1 H} on one thread.
- The generator's samples per second.
- The reward's cost per program: one extra backward pass plus the dot product.
- The machine's steps per second.
- From these, the seat declares: the budget per arm (≤ 8 CPU-hours), the checkpoint grid, the batch sizes, and the bars' margins, each with its ceiling (#228 (b)).

## 7 · The seat's traps for this build (one line each)
- The Adam preconditioner P_e is read from the optimiser's own state, never recomputed by hand.
- The lookback θ_⌊e/2⌋ is a stored snapshot, never a recomputation (#162: one quantity, one road).
- Every loss is in bits per BYTE, never nats per token.
- The generator's reward is logged per program with its three components.
- Nothing runs beside a live learner's graded read (#236).
- One thread, nice 19, a cost figure with the load it was measured under.

## 8 · What R-PRIOR cannot settle
- **Scale:** whether the paper's scaling holds at 10¹⁴–10¹⁹ FLOPs. We run about two orders of magnitude below its smallest point.
- **Other learners:** whether a transformer learner would transfer. The question here is A1's core.
- **Language:** whether a childhood helps SPEECH. That is the words stage, not letters.
- **Weight of a null:** a null here says «not at 10¹³ FLOPs on this box», never «the idea is wrong».

## 9 · The seat's lines (appended, dated; never edited)
*(empty — the price probe's figures; the budget; the bars with their ceilings; then the signature that makes this PREREG law)*
