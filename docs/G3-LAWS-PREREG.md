# G3 — two genome laws changed and one gene added: recognition by the nearest cell, birth by error, abstain by margin
*(edit: Claude (Fable 5.1), 2026-09-19 19:33 +0400 — on Ahmad's 19:19 «Let's tweak some genome laws» and 19:30 «Ok go» to the design shown him. Written before any number. PREREG is law: a bar is never moved; the old genome stays on the record as the twin.)*

## 0 · Why
G2's eye learned photographs as NEIGHBOURHOODS (nearest-neighbour recognition .327 on the eleven unseen words against the glyph eye's .201, chance .14) but not as BANDS (within-median .499 under between-p95 .610). The genome's novelty gene births a cell whenever nothing passes an absolute cosine threshold — on photographs, every glance. So the organism could never use what the eye learned. The laws below let it recognise by the nearest cell and grow by its errors (E48b's regime, whose proof is the neural organ alive since 09-16), with «I do not know» by a margin.

## 1 · The laws (genes; the machinery refuses anything else)
- `RESONATE sight nearest words cos>=0.9` — the SIGHT winners are the nearest KWTA cells by cosine at or above a FLOOR (the novelty gene's THETA_N, now written by the gate as the world's **between-thing 5th percentile**: below it a picture is unlike anything ever seen, and only then is a cell born by novelty). The WORDS area keeps a strict threshold (0.9): a word on the ear lights its own cell only (the ear's max between-word cosine is 0.5–0.625), so Hebb never wires a sight cell to a neighbouring word by accident. Without this gene the machinery runs the old law exactly (pinned: G0b's development hash unchanged).
- `BIRTH error misfires 3` — unchanged mechanics, now the main road: the nearest cell answering the wrong word three times births a cell beside it holding the current input (refused if within THETA_M of it). `BIRTH novelty cos<THETA_N` stays as the under-floor road.
- `ABSTAIN margin cos<MARGIN` (added; the ratio rule stays beside it) — a question is answered by the strongest edge from the lit sight cells as before; it is REFUSED («close») when the best-answering lit cell's cosine does not beat the best lit cell of a DIFFERENT answer by MARGIN, and («novel») when nothing reaches the floor. MARGIN is written by the gate as **5 % of the band width (within-median − between-p5)**, so it scales with the eye's spread. Q2 (a word → a picture) takes no margin (one word cell lights).
- Everything else as G0b/G1/G2: budget, prune, merge, scale, stages, KWTA 5, HEBB window 1, DELTA lr 0.05, RECALL k=1, the gaze, the eyes.

## 2 · The gate under the new law
Gate G-a measures the same bands and writes THETA_N := between-p5 (rounded to 3 dp), THETA_M as before (within-p95 + half the gap to 1), MARGIN as above; overlap no longer stops a run (the bands are reported, the strict and p95 rules printed for the record). The plant's showings from p_res as before.

## 3 · The tests, in order (each with its own genome file; each run's page names it)
- **T1 — G0b's world under the new laws** (`genome/G3-G0b.genome` = G0b + the two genes, `run_g0`): the nine marks with G0b's bars. **Regression bar:** it must pass the eight marks G0b passed ((iv) reported as before); a lost mark refuses the law change for drawn worlds.
- **T2 — G1b's toy under the new laws** (`genome/G3-toy.genome` = G1 + the two genes, `run_g1 --toy`): the ten marks with G1 §3's bars; must pass the nine G1b passed.
- **T3 — photographs** (`genome/G3-his.genome` = G2-his + the two genes: the photograph eye, your eleven words, `run_g1 --his`): bars as G1 §3 in counts, (iv) gating. **Twin: the OLD laws on the SAME eye** (`genome/G2-his.genome`, run as G2-his — its gate overlaps, the toy's thetas carried, as G1 §1 says). **Mark (xii):** Q1(G3) − Q1(G2 twin) ≥ .10 on the 92 held-out pictures.
- Every run: replay, T-shuffle, T-frozen, T-nowire, the random genomes with the new genes fixed, the smaller life.

## 4 · Predictions, written now
- T1: the eight marks hold; births by error rise, novelty births fall to a handful; pruning rises (more wrong edges are born and shrunk).
- T2: the nine marks hold; the null plant «vex» may now ABSTAIN by margin (a hexagon between ring cells) — (vi) uncertain, could turn to PASS.
- T3: Q1 near the nearest-neighbour level, .25–.40 (23–37 of 92) — FAIL on (i); budget refusals near 0 (was 197); error births in the hundreds; (xii) PASS (the twin reads 10 of 92 at best); «ahmad» 0–1 of 2. False abstention high (margin and novel both fire on photographs).
- The risk named: on drawn worlds the margin abstain may refuse answers between look-alike things (circle/diamond) and cost (i) — that is a finding against the margin's size, not a reason to move it after the fact.

## 5 · Order
1. This file. 2. Machinery: the genes; pins (G0b hash unchanged, run_g0 parity+toy). 3. Gates on the three genomes. 4. T1, T2, the twin, T3. 5. Registers; his word.

## 6 · Amendment 1 — the margin gene WITHDRAWN after the machinery toy (edit: Claude (Fable 5.1), 2026-09-19 19:35 +0400; before any world run)
**The reading that forced it.** T1's run stopped at the two-thing toy (circle, bar — the machinery check that runs before every world): Q1 0.175 with 33 of 40 answers refused «close» (`runs/g3-g0b-run.log`). The mechanism, read from the rule: under the floor (0.552) the five lit cells include cells of BOTH things; a cell born by ERROR beside a misfiring cell still carries, for a while, its strongest edge to the WRONG word — its cosine to the picture is as high as the right cells', so the "best lit cell of a different answer" is a sibling under correction, and the gap is near zero. The margin gene, as I defined it, refuses exactly the pictures the error road is learning. It is a defect in the gene's definition, not its size, and the toy caught it before any world. **Withdrawn:** `ABSTAIN margin` is removed from the three G3 genomes; the ratio rule (on evidence) and the novel-under-floor abstain stay. G3 is now the two law changes only (RESONATE nearest with the floor; birth by error as the main road). The gate's MARGIN numbers stay in the genome files as comments, for the record. T1 is rerun; T2's first run (with the margin, already in flight) is kept as a record of the margin's effect on canvases and T2 is rerun without it.
