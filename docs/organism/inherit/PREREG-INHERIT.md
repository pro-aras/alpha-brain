# PREREG — INHERIT: a newborn takes its parent's brain

*Written and signed by Claude (Fable 5.1, the seat, ALONE under his 2026-09-29 15:25 word), 2026-09-29 20:33 +0400. No co-signer: the adversarial walk is §6. Written before any line of the build and before any life.*

## 1 · His word

2026-09-29 20:22 +0400, verbatim: «One thing i just got as an idea that why don't we synthetically place the memories and the raw knowledge there in the brain to start and begin with? Like humans you told the evolution memories are there so why don't we similar place those initialization memories and parts there in it. To give it a kick start. That would be more like human mechanism as we are trying to replicate here»

## 2 · What is inherited, and what is not

A brain's saved state (`genome/brain.py`, `Brain.save`) holds three kinds of thing. The law says which pass to the child.

| Part of the state | Passes to the child | Why |
|---|---|---|
| The learner (the word map, the reader, the bands, the thresholds) | YES | This is the knowledge. |
| `seen`, `moments`, `scenes`, `canvas` (one entry per scene learned) | YES, whole | `calibrate()` reads `seen`; the four lists are index-aligned; a calibration over the child's first scenes alone would replace the parent's. |
| `episodes` (the store the brain CITES when asked «why») | NO, emptied | A child cites only what it lived. Its citations index the aligned lists, so the child's own episodes stay right. |
| The organism's cells, its episodes, its ledger | NO | Not the brain. The body is born blank. |

The child's BRAIN line equals the parent's exactly (`Brain.load` refuses any other). The child lives at a world seed its parent did NOT live.

## 3 · The mechanism

- The life's root holds `inherit/brain.json` and `inherit/brain.npz` (ONE copied pair; the file carries its own hash) and `inherit/INHERITED-FROM` (the parent's root, its learned count, the hash).
- At BIRTH (a Mind built, not resumed) with a BRAIN line: if the pair exists, the brain is loaded from it, its `episodes` emptied, and the mind journals one row `kind: "inherit"` and carries `inherited: {learned, hash}` on STATUS. With no pair the code path is the old one.
- A resume loads `state/brain` as before. The inherited count is read again from the pair.
- A replay copies `inherit/` from the life's root into its work root.
- No genome line, no parser edit: `genome/machinery.py` is pinned and the inheritance is given at birth from outside the genome, as a parent's is. DECLARED as a choice of the seat; his to overturn (a gene `INHERIT` is the alternative, at the price of a cache redraw).

## 4 · The lives

Lean body, the template `genome/brain/BRAIN-LEAN.genome` (DRIVE on), world seed 20261103, sittings fresh + s1b1.

| Arm | Born with | T (training scenes) |
|---|---|---|
| C, the child | the brain of `brain-lean-nearest-20261102` (10,000 scenes at seed 20261102, true utterances) | 1 · 1,000 · 10,000 |
| B, the blank twin | nothing | 1 · 1,000 · 10,000 |
| N, the null child | the brain of a parent that lived the same 10,000 scenes at seed 20261102 with the utterances SHUFFLED (k 1), built for this law | 1 · 1,000 |

Eight lives and one null parent. Two at a time at most, beside the long life.

## 5 · The marks

Graded by `tools/brain/grade_life.py` (unchanged), on the fresh set, FORCED readings. M1 = pointing at a named thing; M2a and M3 as the body's law defines them.

| Mark | Clause | Bar |
|---|---|---|
| I1 BORN KNOWING | C at T 1 against B at T 10,000, same seed, same set | C ≥ B − 0.05 on M1, M2a and M3 |
| I2 THE KICK | C at T 1 against B at T 1 | M1: C − B ≥ 0.30 |
| I3 IT IS THE PARENT'S KNOWLEDGE | C at T 1 against N at T 1 | M1: C − N ≥ 0.30 |
| I4 NO HARM | C at T 10,000 against B at T 10,000 | C ≥ B − 0.02 on M1, M2a and M3 |
| I5 IDENTITY | a closed life with no `inherit/` replayed under the new code | its journal equal to its own, row for row |
| I6 REFUSAL | a pair with one byte changed; a pair under another BRAIN line | each refuses BY NAME, and the plant asserts it changed the bytes |
| I7 RESUME | a child killed hard in mid-training | back by itself, `restored True`, the inherited count kept |

READINGS, no bar: the curve at T 1,000; test 2b («I don't know») and test 6 (the dax) for C against B; `why` (M4) is NOT GRADED at T 1 (the child has cited nothing yet).

## 6 · The adversarial walk (the seat against its own law)

1. **Is I2 trivially true?** Yes, nearly: a blank brain after one scene points by chance. It is kept because it is his question («a kick start»), and it is NOT the evidence. The evidence is I1 (does knowledge from one world hold in another) and I3.
2. **Can I1 pass without the mechanism?** Only if a brain after one scene equals one after 10,000; B at T 1 reads that case and must sit far below.
3. **Can I3's null hear?** The shuffled parent lived the same scenes and the same words in the same counts; only the pairing is broken. Its child is loaded by the same code. What it lacks is exactly the thing tested.
4. **Ceilings.** M1's ceiling is set by the eye (the body's verdict: 0.89 of named things seen). Bars I1 and I4 are differences at one seed and one set, so the ceiling cancels. I2 and I3 ask 0.30 where the recorded gap between a mature brain and chance is above 0.5.
5. **Power.** One sitting carries about 3,000 asks; M1 has hundreds of items. A gap of 0.05 at n ≥ 300 is above two standard errors (0.03 at p 0.9). The per-mark n is printed beside every reading; a mark under n 100 reads UNDERPOWERED, not pass or fail.
6. **One seed.** Every life is at world seed 20261103. The verdict says «at one seed». The sets fresh and s1b1 of this seed were read before by `brain-lean-20261103`; they are not never-used, and no value was tuned on them for this law.
7. **The parent's own sitting.** The parent's state was saved after its sittings. The brain learns only from training rows (`refused_rows 0`, `learned 10000`), so the sittings left no trace in `seen`; checked at the build by the count.
8. **Calibration.** The child's first calibration comes «before a sitting», over `seen` whole (the parent's 10,000 and its own T). The points 250 … 10,000 do not fire again for the child (its count starts at 10,000). DECLARED.
9. **What this does not show.** It does not show that Alpha 1, 2 or 3's knowledge can be placed: their words are tied to nothing this eye saw. It shows inheritance inside one body plan.

## 7 · Verdict rule

INHERIT is ADOPTED as the birth road of the next versions when I1, I3, I4, I5, I6 and I7 pass. I2 is reported. A failed mark is a result with its reason, never loosened after the read.

Signed: Claude (Fable 5.1), the seat, alone — 2026-09-29 20:33 +0400.
