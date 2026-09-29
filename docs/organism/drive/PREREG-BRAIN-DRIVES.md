# PREREG BRAIN-DRIVES, stage 1 — the brain takes its turn: at every canvas it expects, it speaks and it asks, by itself

*Written and signed by Claude (Fable 5.1, the seat), alone, 2026-09-29 16:26 +0400. His 2026-09-29 15:25 word set the seat to work alone after the last builder, so no second hand co-signs this law. In its place stands §8, the adversarial walk, written before any code. This text is law once the signature stands under its final form. The map it serves: `docs/organism/HUMAN-MECHANISM-MAP-2026-09-29.md` (branch day-0929, e406cd7), §5 step 1. The rungs it grades: L13 and L16 of `CHILD-LADDER-2026-09-29.md`.*

**His words (2026-09-29 15:51 +0400, verbatim):** «The brain is not being used. It doesn't read, speak or understand yet? … It needs some one to do something with it. … Start from the brain and use the existing codes we have».

---

## 0 · What was known before this text (stage −1, on the bench)

The probe `tools/brain/diag/probe_drive.py` ran the brain organ as it stands (genome master 262cc20, the template's BRAIN line) over the 10,000 training scenes of the three world seeds, in order. At each canvas, BEFORE the brain learned from it, the probe took the turn of §2 and read it against the bench's truth. No production code was changed. The table is `/data/dev/brain-runs/day0929/drive/stage-1/TABLE.txt` (sha256 88c6ef7b005c108b…).

| Reading (20261101 / 20261102 / 20261103) | Value |
|---|---|
| Canvases after the first calibration (canvas 250) | 9,750 / 9,750 / 9,750 |
| It would SPEAK on | 0.950 / 0.947 / 0.951 of them (9,264 / 9,230 / 9,275 says) |
| What it says is TRUE of the thing it looked at | 0.978 / 0.974 / 0.979 |
| … and picks that thing out among the things in view (UNIQUE-TRUE) | 0.945 / 0.938 / 0.946 |
| The same phrases dealt to other canvases (10 draws a seed) | 0.194 – 0.211 |
| Says of two or more words | 43 / 31 / 30 |
| It would ASK on | 0.100 / 0.104 / 0.096 of the canvases (977 / 1,010 / 937 asks) |
| Its forced names are right, where it holds a word for the thing | 0.922 / 0.919 / 0.919 (n 41,640 / 41,502 / 42,003 names) |
| … and where it holds none (it doubts) | 0.800 / 0.805 / 0.802 (n 3,018 / 3,162 / 2,913 names) |
| SURPRISE at the parent's words, against its forced names | 0.134 / 0.139 / 0.134 |
| The same, utterances dealt to other canvases (10 draws a seed) | 0.682 – 0.693 |
| SURPRISE against its HELD words | 0.055 / 0.057 / 0.055, its null 0.086 – 0.095 |
| Surprise, first window (canvases 250–999) and last (9,000–9,999) | 0.171 / 0.172 / 0.173 and 0.138 / 0.127 / 0.131 |
| CPU for one seed, turns and learning | 151 / 146 / 150 s |

**Three things this table settles.**
1. **The expectation is the forced names, not the held words.** The held words are loose: a band holds many words of a kind for any thing, so a shuffled utterance is «expected» almost as often as the true one (0.055 against 0.09). The forced names separate: 0.13 against 0.69.
2. **The brain speaks one word.** 99.6 % of its says are one word, because its mouth says the SHORTEST phrase that picks the thing out. That is the scored mouth's own law (test 3), unchanged here.
3. **There is no unknown thing in training.** After canvas 250 every training thing is made of words the brain has met often. So «it asks about what it does not know» cannot be read against the truth here. What can be read is whether its doubt INFORMS: its forced names are worse where it doubts (0.80 against 0.92).

---

## 1 · The question

Does the brain, put in the body's loop at every canvas, act by itself — expect, speak, ask — so that what it says is true, its doubt informs, and its surprise is real; with its learning and its exam answers untouched, and at a price the body can pay?

---

## 2 · The law

### 2.1 The gene
```
DRIVE    brain turn before hearing; says 1; asks 1
```
- ONE form. `says` and `asks` each take 0 or 1. Any other word refuses by name.
- `DRIVE` beside no `BRAIN` line refuses by name. Under `--blind brain` there is no brain and no turn.
- Absent: every row of every life is what it was.

### 2.2 The turn (`genome/brain.py`: `Brain.turn(glance, *, scene, world_seed)`), read-only
At a canvas the brain hears, before it learns from it, with the brain as it then is:
1. **things** — the eye's hypotheses (`things_in_view`), each with its fixation cells.
2. **order** — the hypotheses by their number of fixations, most first; ties by the lower index.
3. Before the first calibration, or with nothing in view, the turn ends here with its reason.
4. **held** — per hypothesis, the LAW road's held words (`RWRoad.held_words`).
5. **expected** — per hypothesis, its forced name in each learned type (`RWRoad.believed`), in the types' order; a type with no mature word gives none.
6. **say** (when `says 1`) — the first hypothesis in `order` for which the scored mouth speaks (`learners.produce_believed` over the LAW road, its read-back included). The tie generator of hypothesis h is `substream(world_seed, "turn-say:<scene>:<h>")`. At most one say a canvas. The say carries: the hypothesis, its cells, its position, the words, the read-back's point, the margin (none when it is infinite).
7. **ask** (when `asks 1`) — the first hypothesis in `order` with NO held word. At most one ask a canvas. The ask carries: the hypothesis, its cells, its position.

### 2.3 The surprise (`Brain.surprise(turn, words)`)
With U the distinct words of the parent's utterance: surprise = 1 − (the largest number of U's words that ONE hypothesis's expected names hold) / |U|. None when there is no expectation or no word.

### 2.4 The mind (`creature/mind.py`)
At an eye row the brain hears, that is no ask canvas, under `DRIVE`: the mind takes the brain's turn, computes the surprise against the instant's words, and writes ONE journal row `{"kind": "brain", "act": "turn", …}` BEFORE the canvas's `learn` row. Then the brain learns, as it always did.

### 2.5 What does not change
- The brain's learning, calibration and exam answers: not one number.
- Every other organ: not one row.
- In stage 1 a say and an ask are the brain's own acts on the record. They move no other organ, and the world does not answer the ask. That is stage 2, under its own law.

---

## 3 · The runs

| Run | What | Code | Where |
|---|---|---|---|
| G | **The never-used world.** World seed **20261104**, never drawn before this text. The probe, calling the PRODUCTION turn, over its 10,000 training scenes. | the gate's commit | the bench |
| J | **The join.** The probe with the production turn at the three old seeds must give stage −1's table again. | the gate's commit | the bench |
| B-OFF | The three closed lean lives replayed under their own genomes (`genome/brain/lives/BRAIN-LEAN-2026110{1,2,3}.genome`), `--against` their journals. | the gate's commit | `/data/dev/brain-runs/day0929/drive/runs/` |
| B-ON | The same tapes under the same genomes plus the DRIVE line (made by `tools/brain/drive_genome.py`, which refuses any other difference). | the gate's commit | the same |

No life is launched. The tapes of the closed lives are read only.

---

## 4 · The marks

Every rate is read after the first calibration. n is the count the rate stands on.

| Mark | What is read | On | Bar | Measured at stage −1 | Reachable · failable |
|---|---|---|---|---|---|
| **I1** | The line absent: each B-OFF replay equals its closed journal | 3 replays | every row equal | — (shown today for another gene) | yes · a planted change must break it |
| **I2** | The line present: B-ON's journal with its `turn` rows removed equals B-OFF's, row for row | 3 replays | every row equal | — | yes · yes |
| **JB** | Each B-ON `turn` row equals the bench's turn for the same scene: things, order, expected names, say, ask, surprise | 3 × 10,000 canvases | every canvas equal | — | yes · yes |
| **S** | TRUE: every word of a say is a true word of the thing under it | run G | ≥ 0.95, and above every one of 10 null draws | 0.974 – 0.979; null ≤ 0.211 | yes · yes |
| **U** | UNIQUE-TRUE: the say is true of its thing and of no other thing in view | run G | ≥ 0.90 | 0.938 – 0.946 | yes · yes |
| **R** | The say rate in every window of 1,000 canvases | run G | ≥ 0.85 in every window | lowest window 0.916 | yes · yes |
| **D** | DOUBT INFORMS: forced names right where it holds a word, minus where it holds none | run G | ≥ 0.05, exact one-sided p < 0.001 | 0.114 – 0.122 | yes · yes |
| **E** | SURPRISE against the forced names | run G | mean ≤ 0.20, and below every one of 10 null draws | 0.134 – 0.139; null ≥ 0.682 | yes · yes |
| **J** | The join of the bench: run J's table equals stage −1's, figure for figure | 3 seeds | equal | — | yes · yes |
| **C** | The mind's CPU per training canvas, B-ON over B-OFF, the pair run side by side | 3 pairs | ≤ 1.5 | — (the bench: 15 ms a canvas, turns and learning) | yes · yes |

**Readings, never graded:** the ask rate; the share of says about the parent's own thing; says by the number of things in the scene; says of two or more words; the first true say's canvas; the count of distinct words said truly, by window (its spoken vocabulary as it grows); the surprise series and its fitted slope with its standard error.

---

## 5 · The controls

1. **The planted say.** In run G a copy of the rows with every say's words replaced by a word of the same kind that is false of the thing must read S under 0.05. It shows the grader can fail a mouth.
2. **The silent mouth.** A turn under `says 0` says nothing: S reads NOT GRADABLE by name, never a pass, and R reads 0.
3. **The turn never learns.** The brain's state hash is equal before and after every turn of the unit tests, and I2 shows it on three lives.
4. **The null is a distribution.** Ten draws a mark, by a generator named in the probe. The bar stands above or below every draw.
5. **The identity plant.** One B-OFF replay is repeated with one genome value changed (`DELTA lr 0.05` → `0.06`): it must diverge.

---

## 6 · The decision rule

- **Every mark passes:** `DRIVE` becomes a line of the brain templates (`BRAIN-LEAN`, `BRAIN-FULL`). The rungs L13 and L16 read REACHED IN ITS FIRST FORM, with the two limits of §7 written beside them.
- **I1, I2, JB or J fails:** a wiring defect. It is repaired test-first and the replays are run again. The marks S to E are not read until they hold.
- **S, U, R, D or E fails at the never-used seed:** the brain's turn is not adopted. The failing mark and its figure go to the map's §6.
- **C fails:** the turn is adopted only with a cadence (every k-th canvas), priced first.

---

## 7 · What this does not claim

- **Not that the brain learns by itself.** Its learning is untouched. It still learns only when the parent speaks.
- **Not that the two minds talk.** No other organ reads a say or an ask in stage 1.
- **Not that its asking is answered,** nor that asking teaches it faster. That is stage 2's experiment, and the science is split on it (Begus 2014 for, Bazhydai 2026 against).
- **Not that it speaks sentences.** It says the one word that picks the thing out, and two words when one is not enough.
- **Not a new world.** It is the scene world of 14 words.

---

## 8 · The adversarial walk (in place of a co-signer)

Each line is an attack on this law, and what the law does about it.

| # | The attack | The answer |
|---|---|---|
| 1 | The bars were chosen after seeing the three seeds. The exam is sat by its own writer (#158). | The marks are graded on world seed 20261104, never drawn. Each turn is taken before the brain learns that scene, so every canvas is unseen at its turn. |
| 2 | «True» is cheap: «small» is true of half the things. | U asks that the say picks its thing out among the things in view. The null deals the same phrases to other canvases. |
| 3 | A mouth that says nothing passes S. | R bars the rate in every window. Control 2 names the silent mouth. |
| 4 | The say echoes the parent. | The turn comes before the hearing. The scene was never seen. |
| 5 | A margin of +∞ once passed as certainty (#244 (3)). | The margin chooses nothing here. The thing is chosen by fixations. Inside the scored mouth the margin is what it was in test 3. |
| 6 | The ask mark stands where nothing can fire (#228 a): training holds no unknown thing. | So the ask is not graded against the truth. D reads whether doubt informs. The ask rate is a reading. |
| 7 | On a never-taught shape the ask would fire exactly where test 2b's «I don't know» fires: the same reader. | Said here: that figure is test 2b's, 0.65 – 0.73, and no new evidence. It is not a mark. |
| 8 | Surprise falls because words mature, not because the brain predicts THIS scene. | The null deals the utterances to other canvases: a brain that predicts only «some words» reads like its null. |
| 9 | The turn might write the learner. | The state hash around every turn in the tests. I2 on three lives. |
| 10 | The body's glance might differ from the bench's. | JB joins every canvas. |
| 11 | The price is read on a crowded box (#236, #242). | C is a ratio of a pair run side by side, in CPU. The load is printed beside it. |
| 12 | The grader labels a hypothesis by the thing under most of its fixations; a merged hypothesis has two things. | The count with no thing or two things under the target is printed beside S. At stage −1 it was 0 of 27,769. |
| 13 | The gene's values could be read nowhere (#180). | `says` and `asks` each gate a branch; the tests run 0 and 1 of each; the inventory must read MADE. |
| 14 | A parser edit voids every glance cache (#245 (1)). | A fresh cache root, every cache redrawn under the new bytes, an array-by-array identity check with a planted bit, `cache.RUNS` moved. |
| 15 | One more journal row a canvas could slow the life or fill the disk. | C prices it. The row's size is printed. |
| 16 | The never-used seed is the same generator: it cannot surprise. | True, and said. It guards against a bar fitted to three draws, not against a new world. The wider worlds are owed at stage 3. |

---

## 9 · Signature

- **The seat:** Claude (Fable 5.1) — signed 2026-09-29 16:26 +0400, on this final text, alone.
