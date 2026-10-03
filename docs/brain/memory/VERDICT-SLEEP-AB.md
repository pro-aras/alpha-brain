# VERDICT SLEEP-AB — which 200 episodes the creature rehearses at sleep, read on alpha4-1's closed tape

*Claude (Sonnet 5.5, swarm sleep), 2026-10-03 10:52 +0400. The law: `PREREG-SLEEP-AB.md` (signed 2026-09-29 14:53 and 14:55 +0400); §7 is the rule used. The reading: `/data/dev/brain-runs/day0929/sleep-ab/runs2/READING.json` and `READING.txt`, written 2026-09-30 12:20:10 +0400 by `tools/sleep_ab_read.py` at e65b926 (branch `sleep-ab`) when the last of the 14 arms ended. Every figure below is generated from the arms' own files, or found in a source, by `tools/brain/check_sleep_ab_verdict.py`; none is typed from memory. Not final until the verifier's VERIFIED is on the board.*

## The verdict in seven lines

1. **VERDICT: KEEP** — the SLEEP line stays `SLEEP    every 2500 moments replay 200 by surprise`. §7's words: «The line is KEPT when no rule clears those bars and S is not worse than N by z ≥ 2 nor by more than one lost thing.» Both halves hold (the walk, step 5): no rule cleared a bar; S against N reads z −1.414 on READ-W0-out, and S lost 3 of the 13 things against N's 2, a difference of exactly one.
2. **No rule could clear the bar, because the gate on the bar was not met.** READ-W0-out is gradable only if S recognised at least 30 of the 224 at the end-w0 sitting; S recognised 17. No arm of the 14 reached 30 (the most 28, U2; the fewest 11, P), and at the end of the cut every arm recognised between 1 and 7 of the 224. The A/B's one bar was out of reach for every rule, so it could not say which rule keeps early material.
3. **«This world cannot tell» does not apply.** Its first form needs N to forget nothing measurable: N lost 2 of 13 things, and the words N recognised among the 224 fell from 19 to 3 (a change of 0.0714 against 2 SE of 0.0372). Its second form needs the maker readings of S, P and N all inside U's ten-draw band: the R-B of all three lie outside [−0.04, 0.0] (S −0.5733, N −0.48, P −0.3933), and S's R-A (−0.0583) lies just under the band's floor (−0.0458).
4. **The maker readings are what the law says they are: UNDERPOWERED (13 things; the five arrivals are five), veto-only, never a change.** S lost 3 of the 13 (house, tree, key), N and P lost 2 (tree, key), PR lost 0, and U lost 0 in each of the ten draws. The order on the arrivals, U and PR best, then P, then N, S worst, is the order T-MEM-1 found on the brain's learner for uniform, none and surprise; S sits below N by one thing. It is evidence for the next law's world and decides nothing.
5. **The figures that look like a U win are the ones the gate exists to stop.** U's ten-draw mean beats S on READ-W0-out by z 2.82, and all ten draws recognise more of the 224 than S, four of them by z ≥ 2. They stand on b of 1 to 6 words with c 0 in every draw, at end counts of 1 (S) and 2 to 7 (U's draws). They are printed beside the verdict and decide nothing.
6. **S's win on READ-W0-in is the frozen set.** S recognised 9 of the 51 at the end and every other arm 0 to 2: the law replays those 51 words at every sleep by construction (law §0.1, §8). Printed, never read as the law's merit.
7. **The next A/B's world needs at least 30 of its list recognised at the end-w0 sitting under S, and that is knowable almost for free.** S's rows up to that sitting cost 0.46 CPU-h: 0.067 of S's own cost, and 0.0069 of the 66.07 CPU-h the 14 arms took (the sittings and the READ probe add a little: the law priced all 40 sittings at about 0.2 and the READ probe at about 0.05 CPU-h, §6.2). Pilot the gate before launching the arms.

## What was checked, and how

1. **The reader's JSON against the arms' own files (RAW).** The 40 exam sittings and the 40 readlist sittings of each of the 14 arms were read again, without importing the reader. Every arm's R-A and R-B (all 13 things), its lost things, READ-W0-out and READ-W0-in at the end-w0 sitting and at the end, the 30 paired tests, U's mean tests and U's band were recomputed: 0 disagreements with `READING.json`.
2. **§7 walked from those recomputed figures (LAW)** by the checker's own `decide()`, not by the reader's verdict. It reads KEEP, as the reader does; each clause is in the walk below with the law's words. `decide()` is driven through every branch of §7 on synthetic readings in the tests, including the one that matters here: the same reading with S at the bar changes the line under one reading of «each draw beats S» (item 2 of «What the next law must settle»).
3. **The controls (CTL)** were read from their own files (block below), not from the reader's one-line summary.
4. **Every figure in this document (DOC).** The blocks between `GEN` markers are rewritten by the script and checked verbatim; every other number is found in `READING.json`, `READING.txt`, the law or a block; a negative number must be found as a negative; every «A of B» must be a pair some source carries. Planted faults are caught: a transposed decimal, a pair that is no pair, a sign that no source has, a hand-edited block, a missing block, a flipped verdict word (`tests/tools/test_check_sleep_ab_verdict.py`), and five deliberate breaks of the checker each turned at least one test red.
   - Command, from the worktree root: `PYTHONPATH=. python3 -B tools/brain/check_sleep_ab_verdict.py --doc docs/brain/memory/VERDICT-SLEEP-AB.md`; it ends `CHECK PASSED` only when RAW, CTL, LAW and DOC all hold.
5. **One gap in the instrument of record, found on the way and not repaired.** In `tools/sleep_ab_read.py` the un-gradable branch returns KEEP without testing §7's KEEP clause (S not worse than N). The clause holds here (step 5), so the reader's KEEP and §7's KEEP agree. The checker's walk gates the CHANGE rules and the `replay 0` rule on gradability and does not gate the KEEP clause's own two tests (z, and the count of lost things); for an ungradable reading in which S is worse than N by z ≥ 2 or by more than one lost thing it returns NO CLAUSE FIRES, a case §7 names no reading for, where the reader returns KEEP. The checker prints that disagreement as a LAW MISMATCH and the tests drive both forms. The reader stays as it was run: changing the instrument after the read would change what was read.

## The controls

<!-- GEN:controls BEGIN -->
| control (PREREG-SLEEP-AB) | where it is read | the reading | holds |
|---|---|---|---|
| IDENTITY, §5.1 | `runs2/logs/S.log` | REPLAY identical: 47274 mind rows, then `exit 0` (S against the live mind rows, every field, `hash` included) | **True** |
| its planted twin, §5.1 | `ctl/splant.log` | DIVERGED at seq 1271: hash, then `exit 1` (S′ with `replay 199`, first 2,000 rows) | **True** |
| the twin's own unplanted run | `ctl/s2000.log` | REPLAY identical: 1880 mind rows, then `exit 0` | **True** |
| DETERMINISM, §5.2 | `ctl/u1-a`, `ctl/u1-b` journals | sha256 9aa22b2f… for both, 1741362 bytes each (U(1) twice, first 6,000 rows) | **True** |
| lever H, §6.3 | `ctl/leverh_proof.log` | rows [5667, 5667]; identical except `hash`: True; 4767 null hashes bare against 4767 digests hashed; a planted one-field change caught at seq 1271 | **True** |
| the arms | `runs2/logs/<ARM>.log`, `runs2/state/<ARM>.attempt` | 14 of 14 arms ended `exit 0`; attempts per arm ['1'] (no arm relaunched) | **True** |
| the controls' code is the arms' code | `git diff bbd1214 e65b926 -- creature genome` | empty: True (the controls ran on bbd1214, the arms on e65b926) | **True** |
<!-- GEN:controls END -->

The mark's own positive control (the plant on a copy of the closed end state, moon and cup read 0.0 and the other 14 things equal) was run on 2026-09-29 and stands in law §5.4; it is not re-run here. The world's positive control (§5.3) holds: N lost 2 of 13 things, and every one of the 14 arms recognised fewer of the 224 at the end than at end-w0, so forgetting exists in this world and replay had something to restore.

## §7, step by step

<!-- GEN:walk BEGIN -->
| step | the law's words (§7) | the reading | result |
|---|---|---|---|
| 0 | Nothing is read until IDENTITY (§5.1) and its planted twin have passed. | identity passed; the planted twin diverged | **read on** |
| 1 | READ-W0-out is GRADABLE only if ≥ 30 of the 224 are recognised at the end-w0 sitting under S. | S recognised 17 of 224 at the end-w0 sitting | **UNDERPOWERED (17 < 30)** |
| 2a | N forgets nothing measurable (§5.3): N loses at most one of the 13 things AND N's READ-W0-out end share is within 2 binomial SE of its own end-w0 share. | N lost 2 of 13; N's share moved 19/224 → 3/224, a change of 0.0714 against 2 SE 0.0372 | **N forgets nothing measurable: False** |
| 2b | S does not differ from N. | S vs N on READ-W0-out z −1.414; lost S 3, N 2 | **S differs from N: False** |
| 2c | READ-W0-out is UNDERPOWERED and the maker readings of S, P and N all lie inside U's ten-draw band. | S, P, N each on R-A and R-B against U's band (R-A [−0.0458, 0.0625], R-B [−0.04, 0.0]); outside: S R-A −0.0583, S R-B −0.5733, P R-B −0.3933, N R-B −0.48 | **UNDERPOWERED; all inside: False** |
| 2 | «This world cannot tell» is the reading when 2a and 2b both hold, or when 2c holds. | 2a∧2b False; 2c False | **does not apply** |
| 3P | The line CHANGES to P when READ-W0-out is gradable and P recognises more of the 224 than S by z ≥ 2, and P loses no more of the 13 things than S plus one. | gradable False; P vs S z 1.0; lost P 2 ≤ S 3 + 1: True | **qualifies: False** |
| 3U | The line CHANGES to U when READ-W0-out is gradable, the ten draws' mean recognises more of the 224 than S by z ≥ 2 and ≥ 8 of the 10 draws each beat S, and U loses no more of the 13 things than S plus one. | gradable False; U-mean vs S z 2.82; draws beating S (z ≥ 2 each) 4 of 10; U's mean lost 0.0 ≤ S 3 + 1: True | **qualifies: False** |
| 4 | The line CHANGES to `replay 0` when S recognises fewer of the 224 than N by z ≥ 2 and neither P nor U beats N. | gradable False; N vs S z 1.414; P beats N False; U beats N False | **fires: False** |
| 5 | The line is KEPT when no rule clears those bars and S is not worse than N by z ≥ 2 nor by more than one lost thing. | no rule cleared (3P, 3U, 4); S worse than N by z ≥ 2: False (N vs S z 1.414); S lost 3 against N's 2, a difference of 1 (more than one: False) | **KEEP** |
<!-- GEN:walk END -->

**Order.** §7 lists the CHANGE rules first and puts «this world cannot tell» last as «the reading»; the walk asks «cannot tell» first, because it says the world cannot separate the rules and a verdict would then be unwarranted. Neither form holds, so the order changes nothing here. **Why step 1 binds the CHANGE rules:** the bar's own row (§4) says READ-W0-out is «GRADABLE only if ≥ 30 of the 224 are recognised at the end-w0 sitting under S». The walk applies that to every clause that reads READ-W0-out, including the `replay 0` clause, whose z (N against S 1.414) is below 2 anyway.

## The figures

Each arm is one run, except U, which is ten draws of one rule (law §5.5). «R-A» is the mean change in the level of the eight things that go unshown in w1 (end of w1 minus end of w0); «R-B» the same for the five arrivals unshown in w2 (end of w2 minus end of w1). A level is the mean of a thing's Q1 over its window's last three sittings. «Lost» is a level ≤ 0.2 after ≥ 0.8. «Kept» is how many of the words an arm recognised at end-w0 it still recognised at the end (the law's §4 asks for this beside the end counts when two arms' end-w0 shares differ by more than 2 binomial SE; they do: P 11 and U2 28 differ by 0.0759 against 2 SE of 0.0528, in the derived block).

<!-- GEN:arms BEGIN -->
| arm | R-A (8 things) | R-B (5 arrivals) | lost of 13 | READ-W0-out: end-w0 → end (of 224) | kept at the end of those recognised at end-w0 | READ-W0-in end (of 51) | SER w2 per 1,000 rows | CPU-h |
|---|---|---|---|---|---|---|---|---|
| S | −0.0583 | −0.5733 | 3 of 13 | 17 → 1 | 1 of 17 | 9 of 51 | −0.004359 | 6.83 |
| N | 0.0 | −0.48 | 2 of 13 | 19 → 3 | 3 of 19 | 0 of 51 | −0.003661 | 4.86 |
| P | −0.0167 | −0.3933 | 2 of 13 | 11 → 2 | 2 of 11 | 0 of 51 | −0.001832 | 4.91 |
| PR | 0.0125 | −0.0267 | 0 of 13 | 16 → 1 | 1 of 16 | 0 of 51 | 0.004317 | 4.87 |
| U1 | −0.025 | 0.0 | 0 of 13 | 20 → 4 | 3 of 20 | 0 of 51 | 0.003052 | 4.92 |
| U2 | −0.0083 | −0.0267 | 0 of 13 | 28 → 7 | 6 of 28 | 1 of 51 | 0.003061 | 4.87 |
| U3 | −0.0167 | −0.02 | 0 of 13 | 20 → 2 | 2 of 20 | 2 of 51 | 0.0028 | 4.63 |
| U4 | −0.0458 | −0.04 | 0 of 13 | 25 → 3 | 3 of 25 | 1 of 51 | 0.003817 | 4.55 |
| U5 | 0.0 | −0.0067 | 0 of 13 | 23 → 2 | 2 of 23 | 1 of 51 | 0.004 | 4.56 |
| U6 | −0.0292 | −0.0133 | 0 of 13 | 23 → 3 | 3 of 23 | 1 of 51 | 0.004369 | 4.65 |
| U7 | −0.0125 | 0.0 | 0 of 13 | 18 → 5 | 3 of 18 | 1 of 51 | 0.002964 | 4.72 |
| U8 | −0.025 | −0.04 | 0 of 13 | 19 → 2 | 2 of 19 | 2 of 51 | 0.003447 | 4.19 |
| U9 | −0.0125 | 0.0 | 0 of 13 | 21 → 6 | 4 of 21 | 1 of 51 | 0.004165 | 3.78 |
| U10 | 0.0625 | 0.0 | 0 of 13 | 19 → 5 | 4 of 19 | 1 of 51 | 0.004105 | 3.73 |
| **U band, 10 draws** | [−0.0458, 0.0625] | [−0.04, 0.0] | 0 of 13 in every draw | 18–28 → 2–7 | | | | |

Presence: 14 of 14 arms read; every arm's 224 words present in both READ sittings: True; every arm's 13 things graded (8 and 5): True; sittings per arm [40], split by window [(13, 14, 13)].
<!-- GEN:arms END -->

S's readings are the replay's own 40 sittings, the same instrument as every other arm's. They differ a little from the live record the law quotes (R-A −0.083, R-B −0.553; 18 live sittings a window against 13 or 14 here); the A/B compares arms with each other only.

**The paired tests on READ-W0-out** (b: words the first arm recognises at the end and the second does not; c: the reverse; z = (b − c) / √(b + c); the last column is the smallest gap the n can pass, printed beside every z as the law asks):

<!-- GEN:pairs BEGIN -->
| comparison on READ-W0-out at the end (224 words) | b | c | z | smallest passing gap (2·√(b+c)) |
|---|---|---|---|---|
| P vs S | 1 | 0 | 1.0 | 2.0 |
| PR vs S | 0 | 0 | 0.0 | 0.0 |
| N vs S | 2 | 0 | 1.414 | 2.83 |
| S vs N | 0 | 2 | −1.414 | 2.83 |
| P vs N | 0 | 1 | −1.0 | 2.0 |
| P vs PR | 1 | 0 | 1.0 | 2.0 |
| U1 vs S | 3 | 0 | 1.732 | 3.46 |
| U2 vs S | 6 | 0 | 2.449 | 4.9 |
| U3 vs S | 1 | 0 | 1.0 | 2.0 |
| U4 vs S | 2 | 0 | 1.414 | 2.83 |
| U5 vs S | 1 | 0 | 1.0 | 2.0 |
| U6 vs S | 2 | 0 | 1.414 | 2.83 |
| U7 vs S | 4 | 0 | 2.0 | 4.0 |
| U8 vs S | 1 | 0 | 1.0 | 2.0 |
| U9 vs S | 5 | 0 | 2.236 | 4.47 |
| U10 vs S | 4 | 0 | 2.0 | 4.0 |
| **U-mean vs S** (10 draws; mean per-word difference 0.01295, sd 0.0687, n 224) | | | 2.82 | |
| **U-mean vs N** (10 draws; mean per-word difference 0.00402, sd 0.10126, n 224) | | | 0.594 | |
| **U-mean vs P** (10 draws; mean per-word difference 0.00848, sd 0.07558, n 224) | | | 1.68 | |

READ-W0-in (the 51 words the law rehearses by construction), S against N: b 9, c 0, z 3.0; printed, deciding nothing (#228).
<!-- GEN:pairs END -->

## The maker signal, as the law names it

13 things (the five arrivals are five): **UNDERPOWERED**, a table of readings. §7: «The maker marks never change the line alone … They can only VETO a change (the «plus one» clause).» There was no change to veto: nothing cleared the bar, so the «plus one» clause was never asked (P lost 2 and U lost 0, both within S's 3 plus one).

<!-- GEN:maker BEGIN -->
| thing | window pair | S | N | P | PR | U min | U max |
|---|---|---|---|---|---|---|---|
| arrow | w0 → w1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| bar | w0 → w1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| circle | w0 → w1 | −0.1 | 0.2 | 0.0667 | 0.0 | −0.2333 | 0.2667 |
| cross | w0 → w1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| diamond | w0 → w1 | 0.0 | 0.0 | −0.1667 | 0.2 | 0.0 | 0.2 |
| ring | w0 → w1 | −0.2 | −0.0667 | −0.0333 | −0.1667 | −0.2333 | 0.0 |
| square | w0 → w1 | −0.1667 | −0.1333 | 0.0 | 0.0667 | −0.0667 | 0.0333 |
| wave | w0 → w1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| moon | w1 → w2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| house | w1 → w2 | −0.8667 | −0.4 | −0.1333 | −0.1333 | −0.1333 | 0.0 |
| tree | w1 → w2 | −1.0 | −1.0 | −0.8333 | 0.0 | −0.1333 | 0.0667 |
| cup | w1 → w2 | 0.0 | 0.0 | 0.0 | 0.0 | −0.1 | 0.0 |
| key | w1 → w2 | −1.0 | −1.0 | −1.0 | 0.0 | 0.0 | 0.0 |

Lost (level ≤ 0.2 after ≥ 0.8): S: house, tree, key; N: tree, key; P: tree, key; PR: none; U1–U10: none in any draw.
<!-- GEN:maker END -->

What the table says, and no more:
- **S lost house, tree and key. N lost tree and key.** The law predicted N ≈ S on the arrivals because S's fixed set holds none of their episodes (§0.1, §4); it read N −0.48 against S −0.5733. S is one thing below N (house), inside what §7 tolerates.
- **U lost nothing in any of ten draws, and PR lost nothing.** Rehearsing 200 episodes drawn evenly, or balanced across words, kept all five arrivals; rehearsing the 200 most surprising, or none, lost two or three. **P, the rule that protects the words the organism already answers consistently, kept house and lost tree and key.** The law said key was not «strong» (§2), and tree was «strong» on its stored episodes and was lost anyway (§2, «a limit of P»: a word can be «strong» on stored episodes and no longer generalise). PR, P's own null, lost none.
- **This agrees in order with the 09-28 finding on the brain's learner** (surprise-ranked rehearsal forgot most, uniform least), on a different learner, at one thing's difference between S and N. The law said nothing here assumes the result transfers (§0.2); it is evidence for the next law's world, and no decision.

## Read beside the verdict, deciding nothing

- **READ-W0-in** (51 words): S 9 at the end, every other arm 0 to 2 (table above). The frozen set, by construction.
- **SER** (the composite of the 16 words as a slope per 1,000 tape rows over w2, n 13, **UNDERPOWERED**): S −0.004359 and N −0.003661 fall; P −0.001832 falls less; PR 0.004317 and each of the ten U draws (0.0028 to 0.004369) rise.
- **Retention on the 224:** of the words the 14 arms recognised at end-w0 (279 in all, counted per arm) only 39 were still recognised at the end (0.14). Every rule loses most of what the READ probe saw early, so at the end the probe leaves 1 to 7 words an arm to rank on.
- **Price.** S 6.83 CPU-h; the 13 lever-H arms 3.73 to 4.92 each; 66.07 for the 14. The law priced S at about 3.5 CPU-h solo (about 6 crowded) and each lever-H arm at about 1.0, about 17 CPU-h for the lot (§6.3). The arms ran under a box load of 1.03 to 11.33 (median 7.27, 96 readings in `TICKS.log`), S's figure sits near the law's crowded price, the lever-H arms' figures do not sit near theirs, and the lever saved 0.333 of S's CPU-h (the mean of the 13 against S) where §6.2's model (the hash about 80 % of an arm) implied far more; why is not read here. The next law prices from these figures, in the launch's own shape (#242).

<!-- GEN:derived BEGIN -->
| derived figure | value |
|---|---|
| S end-w0 share | 0.0759 |
| largest end-w0 count of any arm | 28 |
| its arm | U2 |
| smallest end-w0 count of any arm | 11 |
| its arm (smallest) | P |
| arms at or above the bar | 0 of 14 |
| largest end count of any arm | 7 |
| recognised at end-w0, 14 arms pooled | 279 |
| of which still recognised at the end | 39 of 279 |
| pooled retention | 0.14 |
| U draws that recognise more of the 224 than S | 10 of 10 |
| U draws with z ≥ 2 against S | 4 of 10 |
| S minus N, R-B | −0.0933 |
| S R-A below the U band's minimum by | 0.0125 |
| N's share change, end-w0 to end | 0.0714 |
| cheapest lever-H arm CPU-h | 3.73 |
| dearest lever-H arm CPU-h | 4.92 |
| S CPU-h | 6.83 |
| end-w0 share gap, largest arm to smallest | 0.0759 |
| 2 binomial SE of that gap | 0.0528 |
| lever H's saving, as a share of S's CPU-h | 0.333 |
| S CPU-h up to the end-w0 sitting (tape rows ≤ 16198) | 0.46 |
| that, as a share of S | 0.067 |
| CPU-h of all 14 arms | 66.07 |
| that pilot, as a share of the 14 arms | 0.0069 |
| TICKS.log load readings | 96 |
| load, lowest | 1.03 |
| load, median | 7.27 |
| load, highest | 11.33 |
<!-- GEN:derived END -->

## The law's predictions, read against what came (§4's table; hindsight labelled as such)

- **Held:** N ≈ S on the five arrivals; U better than S on them; P better than S on house and not on key; S at or below N on READ-W0-out (1 against 3 at the end) and U above N (mean 3.9); P near N (2 against 3); S best on READ-W0-in; U and P flatter than S on SER.
- **Missed:** R-A, where the law guessed N worse than S and N read 0.0 against S's −0.0583; and READ-W0-out, where the law guessed N the floor and N read 3 against S's 1 and PR's 1 at the end.
- **Not predicted, and decisive:** the base rate. The law's own row says «unknown before S runs» for READ-W0-out's ceiling; its only guide was the live «last 20 heard» share in w0 (0.10 to 0.65, mean 0.44), a different population from the 224 (every hearing at or before the end-w0 sitting), and S read 0.0759 on them. The gate of 30 was set without a pilot of what S would read.

## What the next law must settle

1. **The world.** Its list must have at least 30 words recognised at the end-w0 sitting under S; here the base was 17 of 224 (0.0759) and the range over all 14 arms 11 to 28. Run S to that sitting first (0.46 CPU-h) and read the base; do not launch 14 arms to find it out. [Guessing] A list drawn from words the organism had heard often enough by then would raise the base; nothing here tests it.
2. **«≥ 8 of the 10 draws each beat S».** Read as «each recognises more of the 224 than S», this reading's U draws score 10 of 10; read as «each by z ≥ 2», 4 of 10. With the gate met (S at the bar, in the tests), the first reading changes the line to U and the second keeps it. The law must say which.
3. **«the maker readings of S, P and N all lie inside U's band».** Say whether R-A, R-B or both; here S's R-A and the R-B of all three lie outside, so the answer did not matter, and it could.
4. **The veto for U.** «U loses no more than S plus one», per draw or by the ten draws' mean: here 0 either way.
5. **The un-gradable branch of the reader** must test §7's KEEP clause and the `replay 0` clause before it returns KEEP, and the law must say whether gradability gates the KEEP clause's own z test: as written, an ungradable reading with S worse than N by z ≥ 2 fits no clause (KEEP needs S not worse; `replay 0` needs a gradable bar). Here both readings give KEEP.
6. **The price** from the figures above, in the launch's shape, with the gate's pilot inside it.

## What changes

- **No genome, no life, no code follows from this verdict.** The SLEEP line of every life stays as it is. `brain-long-3` is untouched (RULES §3).
- **Owed, not written here:** the next A/B's law, with the six items above and the world of item 1.
- **Part 2 of this lane** (sleep as the idle state, `PREREG-SLEEP-IDLE.md`) takes the KEEP rule, replay by surprise, unless its own law argues otherwise.

## What this does not show

- It is not a life: the tape is the law arm's world, and an arm is what this mind learns from this stream (law §8). It is 12 hours of a 24-hour life, on the creature's cells, not the brain organ; and it tests the SELECTION of 200, not the dose, the cadence, CYCLE or replay's other roles.
- S, N, P and PR are one run each; the only distribution is U's ten draws. A difference of one thing among 13 is inside every noise this world has.
- READ-W0-out reads one forgetting road, the sight side, on words never heard again in the cut; the arrivals' loss rode on words that kept being heard (§0.4). The two roads can rank the rules differently: that is a finding, and the maker readings above are the other road.
- Nothing here reads the on-disk `state/` (the resurrected organism), and nothing after seq 50,094: the law after the ring wraps (§6.4) is untested.
- «Surprise-ranked rehearsal forgets most» is read on 5 arrivals and 13 things, in one tape. It is a reason to design the next world, not a reason to change a line.

*Drafted by Claude (Sonnet 5.5, swarm sleep), 2026-10-03 10:52 +0400. Awaiting: the verifier (a8b24ad46848caa90).*
