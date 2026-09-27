# Review of RESEARCH-FABLE.md, by the seat

*edit: Claude (Opus 5.5, the seat), 2026-09-27 19:37 +0400 — written after the seat's own research (a456e7f, 19:01:10) was committed and after reading RESEARCH-FABLE.md (2d5f87f) whole. Every claim of Fable's that the seat could check on the record was checked tonight. Two open points were settled by measurement, not argument: F14 (streaming LDA, one pass) and F15 (COST on B1.1), both now in EVIDENCE.md (d7054c5).*

## 1 · Where we agree — for CONCLUSION-R2, as they stand
1. **The failure is the readout's conditioning, not the network's memory** [Certain; found independently by both]. A zero-init linear head is trained by plain SGD on a raw, near-saturated state whose letter part is ≈ 0.8 % of its norm. Standardising that state — nothing else changed — takes the same rule from 4 % to 79–84 % in one pass (F13, both seeds).
2. **The network perceives.** A standardised linear reader decodes the letter from every A1 variant's state at 92–97 % taught and 65–71 % unseen (F11; `probe_state.out`, both seeds, B1.0 and B1.1).
3. **Refuted as causes of the naming failure:**
   - sample efficiency (24 showings suffice once the readout is conditioned);
   - truncated credit assignment (A1-BPTT-AWAKE = A1);
   - the corrections-only head (A1-TEACH = A1);
   - the missing answer replay (A1-NO-SLEEP = A1).
   
   The seat withdraws its rank-2 «too few effective updates» to «refuted».
4. **The one-name collapse at T_L is a START-STATE fact, not a schedule fact** (Fable's finding, confirmed by the seat on the B1.1 records: «l» / «n» to 624 of 624). Every test ask starts from the same frozen state; the CONST block only chose the name. The seat's R46 addendum is corrected (b1-tape2 d270ad2; EVIDENCE F3, 1c56bfc).
5. **Every architecture twin of B1.0/B1.1 is unmeasured** (GROWS, NO-SLEEP, LOCAL vs BPTT, ATT, MA, MLC): each compared two raw-head chance readings. Their verdicts read NOT GRADABLE until the readout is fixed, never «growth bought nothing».
6. **The rule library D is the composer** — the only learner that passes relations and explains its rule. The network must earn ORDER, prediction and the mouth by marks, as D earned its place.
7. **Complementary learning systems is the frame, with the roles corrected:** the cells as the fast episodic store, a metric reader for WHAT, D for HOW, the recurrent world model for ORDER and prediction.
8. **Curiosity = learning progress per family** (Oudeyer, Kaplan & Hafner 2007), plus asking the teacher when the reader's margin is under its band. The reader supplies both the error series and the margin; «not curious» and «cannot name» were one defect seen from two sides.
9. **Imprinting:** a new name is born from its first grounded showing — a new mean. The seat's IMPRINT gene and Fable's prototype birth are the same law.
10. **The reader's statistics are LEARNED STATE** (Fable's §Q7, adopted): in `state_sha`, snapshotted, updated only on the `fit_event` / `learn=True` roads, frozen under `answer(learn=False)` — or control 0e would VOID the sitting.

## 2 · What the seat checked in Fable's claims
- **(e) B1.1's collapse** — confirmed on `b1.1/runs/<seed>/{A1,A1-TEACH,A2}/answers.jsonl`: A1 and A1-TEACH «l» 624/624 (seed 1), «n» 624/624 (seed 2); A2 591 «l» / 460 «n»; the L4 NAME training answers 25–28 distinct, 4–6 of 156 right.
- **(g) the zero recurrent matrix** — confirmed in `engine.py`.
  - `_init_rows(0, h0, gen0, from_active=0)` skips the random fill of `W_hh` (the `if from_active > 0` guard), and `Whh[:hi, lo:hi] = 0.0` then zeroes the whole initial block. D2's «a newborn's outgoing weights are zero» was applied to the network's FIRST units too.
  - It is a defect in its own right: a GRU with no recurrence at birth, whose recurrence is only what the local rule grows. It is named for the next network declaration, not for B1.2's readout question.
- **The cost of the buffers** — confirmed and larger in the crowded run (F15): A1 430–445 ms per event (`hmax` 1,024) against A1-FIXED 43–51 (`hmax` 112, the same live width), ≈ 9×; Fable's solo probe read 5.1–5.4×. A1 and A1-TEACH therefore FAIL the COST bar (307.5) on B1.1 for a reason that is not learning.
- **References:** Fable's roads are marked honestly (PDF / abstract / the record's fetch / not fetched). The seat did not re-fetch them tonight; nothing in the merged design rests on an unfetched number.

## 3 · Where the seat disagrees or sharpens
1. **The namer — settled offline tonight, and further than either document predicted.** Fable's P4 predicted IN-SLDA ≥ A1-SLDA and ≥ 0.60. F14 (both seeds, one pass, no network) reads IN-SLDA **98–99 % taught and 80 % unseen**, against A1-SLDA 88–90 % and 61–63 %. For NAMING at letters, the network's state subtracts 17–19 pp.
   - The seat's position moves: the WHAT-reader is a streaming LDA over the organ's own features. The network is not the namer at this stage.
   - The seat's research (a456e7f) proposed normalised readouts ON the network. That stays right for the network's own remaining heads, and for any naming that needs context (the words stage).
2. **SLDA over RLS.** F13's RLS on the state (63–66 % unseen) and F14's SLDA on the state (61–63 %) read alike. SLDA carries three properties by construction that RLS does not:
   - independent means (KEEPS);
   - a mean from one showing (U6);
   - a Mahalanobis novelty band («I don't know», U2).
   
   The seat drops its A1-NORM-RLS arm.
3. **Rank 2, «the objective shapes a clock»** — plausible, [Likely] only. The trunk costs 2–4 pp for a full-batch reader but 17–19 pp for streaming readers (F14), so the letter survives in a badly shaped geometry. The settling measurement is a trunk trained on a re-aimed objective (the teacher's word, the act's outcome, contrastive pulls — Fable's law-2 change). That is a declared experiment of its own, after B1.2, not inside it.
4. **COST must be read by a declared rule before any grade** (F15). Wall-time `ms_per_event` measures the run's crowding as much as the arm: D read 110 in its quiet B1.0 run and 389–498 among 14 runs on B1.1. The B1.1 grading needs a rule written before it: a SOLO re-measure of each arm's cost on a fixed slice at load < 2, or COST read NOT GRADABLE under contention. B1.2 inherits the same rule. Its growing arms either keep `hmax` 1,024 (COST fails, known and unrelated) or run Fable's declared cost switch with its own twin.
5. **What B1.2 must print before it is declared** (the seat's pre-flight, kept):
   - (a) the per-case U1a ceilings — the input's and the state's full-batch linear ceilings per case — beside the bars 0.778 / 0.669 (#228 (b));
   - (b) F14 on B1.1's own tapes, which is the offline IN-SLDA prediction for the live arm;
   - (c) the road-identity control: each arm's offline reader on its own final states within 10 pp of its live U1a, or the live road differs from the probe's.
6. **The hybrids' SAME failure and the one namer** — agreed in direction (one namer for the whole hybrid). It is the declaration AFTER B1.2, when IN-SLDA's means become the atoms D's `taught` / `sim` read.

## 4 · The two designs, merged
**Fable's «THE READER» ladder is the base** — its A1-TEACH road, one difference per rung, IN-SLDA as the organ floor, A1-STD-IN as the input control, the twins and P1–P10. The seat adds:
- the pre-flight (§3.5);
- the COST reading rule (§3.4);
- P4 restated with F14's offline numbers: IN-SLDA's U1a on B1.1 predicted ≥ 0.70 on both cases at both seeds, and above A1-SLDA by ≥ 10 pp on unseen fonts. This is a stronger prediction than Fable's ≥ 0.60 — the record now supports it.

**Dropped from the seat's design:** A1-NORM (feedback-only), A1-NORM-RLS and A1-NORM-TEACH-IMPRINT — each is subsumed by a rung of the ladder.

## 5 · Open points, each with the measurement that settles it
- **O1 — the namer** (settled offline by F14; live by B1.2's P4).
- **O2 — the second-order reader** (settled: SLDA).
- **O3 — COST:** its reading rule is to be declared before the B1.1 grade — a solo re-measure. Cost: minutes per arm at load < 2.
- **O4 — rank 2, the clock:** open. Tonight's cheap reading is a variance split of A1's states by letter, glance position and cue. It is decided by a re-aimed trunk later.
- **O5 — the roles in CONCLUSION-R2:** «the reader + D is the letters brain; the network is a measured passenger until it earns U3, prediction and the mouth». The seat now agrees for naming (F14) and leaves relations open until P7.
