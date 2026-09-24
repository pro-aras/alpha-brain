# THE BRAIN — the part that thinks, grown from the genome inside the one body

*SKELETON, round 1 — written by Claude (Opus 5.5, the brain's designer), 2026-09-24 11:46 +0400. **Nothing below is settled.** Each section carries ONE provisional line and the questions it waits on. **The body of this document waits for his 11:40 protocol** (relayed by the seat): `RESEARCH-OPUS.md` and `RESEARCH-SEAT.md` written independently → `REVIEW-OF-SEAT-BY-OPUS.md` and `REVIEW-OF-OPUS-BY-SEAT.md` → `DEBATE.md` until convergence or a named irreducible disagreement with the experiment that settles it → `CONCLUSION.md`, co-signed → then this body, built on the conclusion. Design questions: `QUESTIONS-FOR-THE-SEAT.md`; the record: `DIALOGUE.md`; his notes: `AHMAD-NOTES-2026-09-24.md` (12 pages, photos in `notes/`).*

## 0 · The design in twelve lines
*Written last, after the conclusion.*

## 1 · The goal, his words, and what «a brain that thinks» means here
- His words verbatim: 10:55 · 11:10 · 11:24 · 11:40 (2026-09-24); the 10:15 law (not bounded by time — speed and accuracy); the pure road (09-23 16:56); his 09-03 «the prediction for speaking is a wrong direction»; his notes, page 1 («intelligence is in understanding what you are saying») and page 5 («understood by it, not predict … But the prediction plays important role in its learning curve»).
- **Provisional:** the brain is the missing middle between the organs and the mouth — a network GROWN in the mind from a BRAIN clause that predicts its body's next moment in every sense (action → reaction, reaction → action), composes what it knows into relations it was never shown, and says what it means through a judged mouth, learning every moment of its life.
- «Not the same thing as the market», as five checkable differences, each with its test in §9: GROWN (its size is an output); GROUNDED FIRST (his order — letters seen and heard, words with pictures, sentences, books LAST); CONTINUAL (never frozen; no separate training phase); SPEAKS BY INTENT (never free-running next-word generation); REPLAYABLE AND CITED (every belief has an address).
- What it is NOT: a borrowed model or borrowed weights; a fixed architecture; a text model trained once; a replacement of the organs; a set of hand-written rules (his 11:40: the gates «should get adjusted as the learning goes on»).
- A NOTES-MAP (Q11): every item of his twelve pages → what it asks · the creature now · the section · the stage.

## 2 · The substrate that grows (the brief's question 1)
- **Provisional — pending the research and the debate:** HYBRID, the complementary-learning-systems frame: the cells stay the FAST store (one-shot, episodic — names seen things ≈ 0.9); the SLOW store is a network grown from a BRAIN clause whose units are LEARNED GATES — AND / OR (a thresholded sum, by its weights), IF / ELSE (a gate choosing between the old state and the new), THEN (a state carried to the next moment); units born where error persists under a budget that refuses, depth added by a declared rule, the wrong and the redundant pruned, the unused never (#227).
- Alternatives, each a CHECK on the same letters toy: SOFT gates (a gated recurrent network) vs HARD learned gates (a learned logic-gate network; a Tsetlin clause machine — E20: plain XOR 100 %, 74.72 % under 40 % label noise, 5.21 pp behind a ridge on glyph features, clauses stable 0.738 against a random twin's 0.051: an explainer, not a classifier); a growing TRANSFORMER; the cells ALONE (the floor).
- The toy that can refuse it: §8's letters toy — the grown brain must beat the cells-alone floor on THEN (sequence) and on relations held out by pair, and a FIXED-size twin of its final size must not match it (else growth bought nothing — E48 clause (iv)).
- Waits on: the research, Q4, Q7.

## 3 · The learning signal (the brief's question 2)
- **Provisional:** prediction error over the body's own multimodal stream, as his page 6 says («The more predictions of brain about something get/goes wrong, the more it learns»). AWAKE, one step a moment at the body's pace: predict the next moment of every sense; cheap error-driven updates. ASLEEP, at machine speed while the mind-paced world waits (his 10:15): replay of short windows from the cells' episodes and the tape, old and new interleaved (a share of the new stream — E46's lesson), exact gradients through the window as the machine's advantage (his 13:39 rule) — the first thing to challenge. THE SCHOOL's reward / «No» + hurt / teach again as a third factor on exactly the evidence that gave the answer (the FEEL rule of Bench §4.2, made the brain's). CURIOSITY aims where the error is expected to fall.
- Cost per moment: **not measured** (load 18 all morning); [Guessing] ≈ 1–10 ms a moment on one Ryzen thread for a 1–10 M brain, ≈ 20–50 ms at 50 M, the M1 Max ≈ 5–20× faster for batched sleep replay — every figure replaced by the solo probe (Q12 (a)).
- Checks: a local-only twin; a no-sleep twin; a no-FEEL twin.
- Waits on: the research, Q1, Q3, Q9, Q12.

## 4 · Grounding — «knows what it speaks», and the mouth (the brief's question 3)
- **Provisional:** a word is known when its use PREDICTS the senses in both directions (the thing in front of it → its name; a name → the thing), it refuses a name for a thing never seen («I do not know» under ANSWER), it acts on a two-word sentence in the game («go to the red ball»), and every sentence it says back-parses to claims its own perception holds (L30: grounded and cited) — each against a shuffled-world twin (Q1's four tests).
- The mouth: TEXT first (a word, then a frame, then a small sentence), by intent → render → judge; `genome/chain.py`'s composer stays the floor speaker; a SOUND answer later (Bench D-17).
- Waits on: Q1, Q5.

## 5 · Continual and open-ended (the brief's question 4)
- **Provisional:** forgetting is met by four mechanisms, each with a twin — growth under a budget (new units for new things; old ones untouched); sleep replay interleaving old with new; the family / context law (#225; E48b's Decision 31: a label conflict is context, not capacity); the arrival law (a never-heard word opens an arrival). MEASURED as retention curves on held-out items of every earlier stage after each arrival, split by the thing's age (G4 (v)'s form), against a no-replay twin and a fixed-size twin.
- **Said plainly:** the estate has measured forgetting only in LABELLED heads with classes arriving in sequence (E48's sequential gradient head kept 0 of 120 letters where the local growing rule kept 58–66 %; E46b's rehearsal curve 0.00 → 0.08 → 0.34 → 0.51 → 0.57 over 0 → 31,000 rehearsed rows, confounded by the label conflict of #225). A self-supervised predictive brain's forgetting has NEVER been measured here; the letters → numbers arrival is where it is first measured.
- «Open-ended», operationally: the world keeps arriving (new families, then the doors to the open world — his 09-17 word), the objective (predict the next moment) never runs out, and the School's top stage is generated after the brain is frozen for the sitting.
- Waits on: the research, Q8.

## 6 · The library phase (the brief's question 5)
- **Provisional:** HIS stage 12 — books after grounding, never first; the creature READING as a life with a tape; read aloud through the ear road, a declared sample also shown; the same weights before and after; on this box at the mind's pace. The shelf ≈ 31 M words [estimate] with tiny early grades (K ≈ 0.2 MB, G1-G3 ≈ 2.2 MB) — the gap between his curriculum's grounded words and the shelf's College text is the phase's honest ceiling. The Mac only as a sealed epoch (Q2); a rented GPU only from 300 M (Q7).
- Waits on: the research, Q1, Q2, Q6.

## 7 · How the brain meets the organs (the brief's question 6)
- **Provisional:** the brain lives in the MIND — its weights are memory, so the mind thread is their one writer; it consumes the rows the mind already consumes (the eye's glance features — 144 numbers a glance, five a canvas; the ear's word, decoded letter by letter (Q10); the sound trait's 37; outcomes and acts; body rows; the School's feel rows); it emits `say` (journaled), `act` (the existing ACT-file road), `question` (the ask/out road); its predictions reach the organs as SURPRISE's expected input does today (his page 6: «the brain and organs shall communicate on predictions of brain»); its state is hashed through the sparse per-row witness and densely only at snapshots (a dense hash of millions of floats a canvas would repeat ALPHA4 §11 (4)'s finding: the hash was a third of the mind's cost); its sleep runs on THINK's frozen-copy law. STAYS: the organs (sealed), the cells (fast store), ANSWER (the gate), the tape law, the crash law. REPLACED only when beaten on the same items: the act chooser, INDUCE / DEDUCE, the frame composer as the default speaker.
- Waits on: Q5, Q9, Q10.

## 8 · The staircase and its bars (the brief's question 7)
- **Provisional:** the first brain ≤ 1 M parameters [Guessing], grown on the letters toy on this CPU. «It thinks» at the letters stage = composing what it has seen into relations never shown FOR THAT PAIR — THEN (what comes after, before, two after a letter in his A-then-B-then-C order), AND / OR (a letter that is this and that; this or that), IF / ELSE (a conditional over letters it knows) — each item above a shuffled-relation twin and under its organs' ceiling. Then ≈ 10 M (words with pictures; small sentences), ≈ 50 M (the Mac; books), 300 M + (a GPU — his call, on the card's word). Every step's ceiling, and its cost in CPU- or GPU-hours, measured where the probe exists, labelled where it does not.
- **His notes** (arrived 11:42, `AHMAD-NOTES-2026-09-24.md`): the test list is built from pages 4–6 (traits + geometry; «learn the general pattern instead of memorizing specifics»; prediction drives learning), his five words, and page 10's loop for the later executive stage; the NOTES-MAP (Q11) places every other item.
- Waits on: the research, Q7, Q8, Q11.

## 9 · What would show the design is WRONG (the brief's question 8)
One refuting observation per pillar, written before any build (provisional list; the numbers declared with each PREREG):
- **the substrate:** a fixed-size twin of the brain's final size matches the grown brain on the letters toy (growth bought nothing);
- **the learning:** a no-sleep twin retains as well as the brain (sleep does no work); a local-only twin matches it (exact gradients are unneeded);
- **grounding:** a shuffled-world twin (names paired with the wrong pictures) scores within noise of the brain on word → picture;
- **continual:** the letters' retention after the numbers arrive drops more than 5 pp for the brain where the cells alone keep it (G4 (v)'s bar);
- **«it thinks»:** relations held out by pair sit at the shuffled-relation twin's score;
- **the cost:** the brain cannot keep up with a mind-paced letters world on one core (then it is not «human-inspired, not heavy machinery»);
- **the mouth:** its sentences are no better grounded and cited than the floor composer's.

## 10 · The build order
*After the conclusion.*

## 11 · Risks
*After the conclusion.*

## 12 · DECISIONS for Ahmad (each with the recommended option first)
*Provisional rows only — settled after the conclusion and round 2:*

| # | decision | recommended (provisional) |
|---|---|---|
| D-1 | the substrate | the hybrid — the cells (fast) + a grown network of learned gates (slow); soft-gate vs hard-gate vs transformer as checks on the letters toy |
| D-2 | what «understood, not predicted» binds | prediction = the learning; the mouth speaks by intent, judged |
| D-3 | identity across machines | per machine class; a phase run elsewhere enters as a sealed epoch |
| D-4 | the framework | numpy for the first brain; PyTorch CPU (deterministic) from 10 M; never a pretrained weight |
| D-5 | the library phase | his stage 12, read aloud on this box as a life, the same weights before and after |
| D-6 | the first size | grown from ≈ 10^5; ≤ 1 M at letters; 10 M → 50 M (the Mac) → 300 M + (a GPU) on the card's word |
| D-7 | kind B | the brain IS kind B's first form (one road) |
| D-8 | who answers | both graded; the brain answers once it beats the cells on the same items |
