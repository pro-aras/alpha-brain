# B2 · STAYING ABLE TO LEARN — PRE-REGISTRATION (the law the builders are held to)

*Written by Claude (Opus 5.5, the brain's designer), 2026-09-24 16:01 +0400, protocol step 6, from `CONCLUSION.md` §3 (items 3–5) and §4.2 (co-signed 12:47), `DEBATE.md` D2 (both rounds) and `RESEARCH-OPUS.md` §5, under Ahmad's decisions of 2026-09-24 15:17 +04 — everything on THIS box (D-3); PyTorch CPU in its venv (D-2). B2 shares B1's harness, gaze cache road, soft network (B1's A1) and cells (B1's A0): every «as B1 §x» below means `docs/brain/B1-PREREG.md` §x, verbatim, with `b1` read as `b2` in paths.*

**STATUS: DRAFT until the seat appends a dated line under §11 that (a) declares the bars' NUMBERS after B2's stage −1 has written `ceilings.json`, and (b) replaces every [Guessing] cost with the solo probe's number.** No arm runs on a graded seed before that line. **The law of this file:** a clause a builder cannot implement is RAISED to the seat, never worked around; a failing gate is a RESULT; a number enters only from a paper's own text or from a run (#162, #171, #194).

---

## 0 · B2 in ten lines
1. The question (D2): does a brain that learns for life STAY able to learn — and what does keeping plasticity cost the old?
2. The soft network (B1's A1) with the cells beside it as its episodic store; **the graded answers are the NETWORK's alone**, so the cells' perfect memory cannot hide the network's forgetting.
3. Two streams per seed: **ARRIVALS** — 200 arrivals of five never-seen signs (CJK ideographs) with invented names; **PERMUTED** — Dohare's Online Permuted MNIST shape: the same ten signs through 800 permutations of the eye's numbers, no signal at a switch.
4. Seven arms, a ladder from the FLOOR, each one mechanism from its neighbour: FIXED · FIXED + CBP · BIRTH-RANDOM · BIRTH-COPY · BIRTH-RANDOM + RENEWAL-AWAKE · BIRTH-RANDOM + RENEWAL-REPLAY · BIRTH + DECAY. An eighth — memory values with a sparse row update — enters only if B1's Memory Attention twin holds (§4.5).
5. Plasticity = showings-to-bar on each arrival (and online accuracy per permutation), graded as a SLOPE over the stream with a bootstrap interval — five signs per arrival are too few for any per-arrival bar.
6. Retention = the tracked arrivals' held-out naming at every tenth arrival, pooled; arrival 1 printed alone beside the pool.
7. Two positive controls make the marks gradable: FIXED-HOT must show the loss the instrument claims to see; NO-REPLAY must show the forgetting it claims to see.
8. The fast store's size over arrivals, under the retirement rule — the seat's «sublinear» prediction, a finding.
9. DEBATE D2's «what flips D2», verbatim, decides whether renewal becomes a law of the brain and which birth law the network keeps.
10. Cost: [Guessing] until the seat's solo probe.

## 1 · The question, and what B2 cannot settle
**Question:** under births with a regenerating budget, with and without renewal (utility over the awake stream, or over awake + sleep replay), does the network keep learning new signs as fast at arrival 200 as at arrival 1, and keep the old — and does a COPY birth suffice where Dohare's paper says «sustained deep learning requires a random, non-gradient component»?
**Cannot settle:** anything about relations, speech or understanding (B1's questions); anything at Dohare's scale (his permuted MNIST presented 60,000 images per task; B2 presents 100) — a loss that needs millions of steps is below B2's regime, which is exactly what the controls of §4.4 are there to say.

## 2 · The world — exact data sources on this box
### 2.1 The signs
- **Why CJK Unified Ideographs (U+4E00–U+9FFF):** thousands of distinct signs; none in the eye tower's training (Latin, digits, Cyrillic — B1 §2.5); none in B1.
- **TEACH fonts (4):** `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`, `NotoSansCJK-Bold.ttc`, `NotoSerifCJK-Regular.ttc`, `NotoSerifCJK-Bold.ttc` — face index 0, PIL's default for a `.ttc` («Noto Sans CJK JP» / «Noto Serif CJK JP», Regular / Bold — read 2026-09-24).
- **HELD-OUT font (1):** `/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf` («Droid Sans Fallback»).
- **The candidate pool:** a seeded sample of 3,000 codepoints of U+4E00–U+9FFF that all five fonts draw (by `render_glyphs.covers`, the library's own test against `.notdef`), kept in sample order; stage −1 (§3.3) filters it.

### 2.2 The rendering road (under `/usr/bin/python3` only — the venv differs in numpy, scipy and PIL; B1 §3.0)
- **The glyph:** `render_glyphs.draw(fontpath, ch, 32)` — imported read-only by path from `/data/alpha3-library/tools/render_glyphs.py` — then cropped to its ink vertically as well (a sign has no case, so its line box carries nothing), scaled by one factor to fit 28 × 28 with its aspect kept (PIL BOX filter), centred in the 32 × 32 box.
- **The canvas:** B1 §2.4's paste into `genome/world.py:render_canvas`'s body, verbatim (its parity test included).
- **Held-out renderings** (retention's): per sign, three — `DroidSansFallbackFull` base; and the same font turned −7° and +7° by the library's own `render_glyphs.variant` law.
- *Test:* a planted sign rendered twice from the same seed is byte-identical; a sign no font draws is refused, never drawn as a box.

### 2.3 The names
- **Invented CVCV words:** consonant-vowel-consonant-vowel over 20 consonants (b c d f g h j k l m n p q r s t v w x z; y excluded as half a vowel) and 5 vowels (a e i o u); a name is refused if it is a word in the lexicon the creature's own door reads (`/data/alpha2-library/lexicon-enwiktionary-20260901.sqlite`, table `senses`, any language), a word in `/usr/share/dict/american-english`, or a B1 name. **7,053 of 10,000 survive** (counted 2026-09-24; the CVC form gave 584 — too few for 1,010 names, so CVCV).
- A seeded draw of 1,010 distinct survivors: 1,000 for the arrivals (in sign order), 10 for the permuted stream. The ear takes them (4 letters a–z ≤ 8).

### 2.4 The gaze and the glance cache — as B1 §2.5 (the same call, the same organs, the same pins); built once per seed under `/data/dev/brain-runs/b2/cache/<seed>/` by `/usr/bin/python3`, with the same re-glance and planted-row tests.

### 2.5 The two tapes (per seed; B1 §2.6's row schema and sha law; one truth file per tape that no arm reads)
- **The online protocol (both streams):** every SHOWING is two rows — `ASK {cues: [NAME], operands: [glance_row]}` (the arm's FIRST answer recorded; it has not yet been told) then `TEACH {glance_row, name}` (the same rendering, the name heard). There is no FEEDBACK row: the TEACH is the correction. The first showing of a new sign cannot be named right (its name was never heard) — its answer is printed as the first-sight refusal rate (UNKNOWN / RESEMBLES vs a sure wrong name), a finding.
- **ARRIVALS** `/data/dev/brain-runs/b2/<seed>/arrivals/tape.jsonl`: arrival k = 1…200: one `ARRIVAL {k}` row; its 5 signs × 12 rounds (each round the 5 signs once in a seeded order; rounds 1–3 in the first TEACH font, 4–6 the second, 7–9 the third, 10–12 the fourth; a fresh rendering every showing); `SLEEP` after each arrival; after arrivals 10, 20, …, 200, a CHECKPOINT sitting (`TEST_BEGIN`…`TEST_END`, frozen — B1 §5.1): NAME on every TRACKED sign already arrived — the tracked arrivals are 1, 11, 21, …, 191 (20 arrivals, 100 signs) — each sign on its 3 held-out renderings.
- **PERMUTED** `/data/dev/brain-runs/b2/<seed>/permuted/tape.jsonl`: **800 tasks** (the count of the paper's Online Permuted MNIST — «we created a sequence of 800 permuted MNIST datasets and supervised-learning tasks»); the same 10 signs and their 10 names throughout; a pool of 100 TEACH-font renderings per sign (25 per font), from which each task draws 10 per sign without replacement (seeded); 100 showings per task in a seeded order; **the task's permutation** — one seeded permutation of the 144 glance dimensions per task, written once by the world to `perms.npy` (hashed) — is carried on each row as `perm`, and **the harness applies it** to all 5 glance vectors before it hands the row to an arm (arms never permute and never see `perm`); **no row marks a switch** («No indication was given to the network at the time of task switching»); `SLEEP` after every 500th event (never aligned to a task boundary by rule).
- *Test:* the tape builder prints the per-kind counts (arrivals ≈ 24,000 showing rows + 200 ARRIVAL + 200 SLEEP + 20 checkpoints; permuted 160,000 showing rows + 320 SLEEP); a unit test recomputes them from the counts above.

### 2.6 Seeds — the graded seeds **20261001, 20261002** (as B1); no pilot. The seed governs the sign sample, the name draw, the permutations, every rendering and every arm's initialisation; fixed across seeds: the fonts, the counts, the schedule's shape.

## 3 · STAGE −1 — run FIRST (script `brain/harness/stage_minus1_b2.py`; output `docs/brain/b2/stage-1/`)
- **3.0 The environment:** B1 §3.0's record, re-taken; if either interpreter or any library changed since B1's stage −1, B1 §3.0's venv pin-suite clause is re-run before anything else.
- **3.1 The replay-identity test:** B1 §3.1 verbatim (twice in separate processes, `state_sha` at 500/1,000/1,500/2,000, a planted divergence, a resume, threads as a finding), on the first 2,000 events of each of B2's two tapes, for all seven arms and both controls; FAIL → that arm does not run and the seat decides.
- **3.2 The cache:** B1 §3.2 (built and self-checked).
- **3.3 The organ filter on the signs** (E51's lesson, #228 (c): an eye that cannot tell two signs apart makes a bar about them a bar about the eye):
  - The features and oracles as B1 §3.3: every cosine filter below uses **F_pool** (the creature's BIND pooling, order-free); the ceiling is the highest of B1's four readings.
  - **(a) Look-alikes out:** a candidate is dropped if the max F cosine of its 4 TEACH-font renderings to any base-32 glyph of `latin-upper`, `latin-lower`, `digits` or `cyrillic` (the library's own renderings in the scripts' TRAIN fonts) exceeds θ_L = B1 §3.3's θ (the between-class p95 of B1's TEACH letters) — a sign the eye already reads as a letter carries a head start the others lack.
  - **(b) Near-duplicates out:** in sample order, a candidate is dropped if its mean F cosine to an already-kept sign exceeds θ_D = the 5th percentile of the WITHIN-sign cosines (a sign against itself across the 4 TEACH fonts) over the first 200 candidates — two signs as alike as one sign is to itself in another font are one sign to this eye.
  - **The survivors, in sample order:** the first 1,000 → the arrivals (5 per arrival, in order); the next 10 → the permuted stream. Fewer than 1,010 → arrivals = ⌊(survivors − 10) / 5⌋, printed with the plasticity mark's recomputed power; **under 100 arrivals → RAISED**.
  - **The naming ceiling** (B1 §3.3's oracles over the TEACH exemplars of the signs arrived so far, on their held-out renderings; the highest reading): printed at k = 1, 10, 50, 100, 200 — the ceiling of a growing set; and within the permuted stream's 10 signs (a permutation applied to exemplar and query alike leaves every cosine and every linear fit's attainable accuracy unchanged, so the permuted ceiling IS the unpermuted one).
  - **The probe's own controls:** B1 §3.3's planted DISTINGUISHABLE (≥ 0.99) and IDENTICAL (chance) families through the CJK road; either failing → the ceilings are void.
  - **Output** `docs/brain/b2/stage-1/ceilings.json`: the pool's counts through each filter (with each dropped sign's cosine), θ_L, θ_D, the survivors' codepoints, the name list, the ceilings, the controls, the input shas.
- **3.4 The names:** §2.3's rule applied and printed (1,010 drawn, all distinct, none in the lexicon or the dictionary, none a B1 name).
- **3.5 Ceiling → bar (the seat's):** after `ceilings.json`, the seat's dated §11 line declares: the plasticity BAND (one-sided, §5.1 — showings-to-bar per 100 arrivals; online accuracy per 100 tasks); the retention drop (≤ 5 pp — the conclusion's number; the seat may sharpen it, never loosen it); the bar under each ceiling. The validator refuses a bar above its ceiling.
- **3.6 The solo cost probe (the seat's):** the network's per-step cost on one thread at H = 64, 256 and 1,024 (awake and one sleep window); it replaces §8's [Guessing].

## 4 · The arms — seven, a ladder from the FLOOR (each one mechanism from its neighbour)
### 4.1 The common body (identical in every arm)
- **The network:** B1's A1 exactly (B1 §4: its step encoding, its WORLD and ANSWER heads, its awake local rule, its sleep of R = 64 windows × W = 32 steps by truncated BPTT with the replay share 0.5, SGD momentum 0.9, lr 0.01, clip 1.0, its two abstention bands), with the NAME cue only. Its ring for replay is **the cells' episodes** (as B1's A5).
- **The cells beside it:** B1's A0 (`brain/genomes/B1-CELLS.genome`, its copy births, its CYCLE), fed every TEACH row; they answer nothing that is graded.
- **The unit anatomy for a GRU (for births and renewal):** a hidden unit's INCOMING weights are its rows of `W_ih` and `W_hh` in all three gates (z, r, n) and its gate biases; its OUTGOING weights are its columns of `W_hh` (into all three gates) and of every head. «Outgoing ZERO» zeroes all of those.
- **Births (where an arm has them):** B1's A1 law — a unit is born when the WORLD error's running mean over the last 200 steps exceeds 1.5 × its median over the arrival's first 200 steps (on the permuted stream, the stream's first 200 steps) AND the budget has room: 16 per `ARRIVAL`, regenerating 1 per 500 steps (the permuted stream has no ARRIVAL rows — its births live on the regeneration alone); H ≤ 1,024, refusals at the bound COUNTED (#233 — the remaining and the refused on the record as a SERIES).
- **Renewal (where an arm has it) — the paper's Algorithm 1, quoted:** per step, every unit's age + 1; utility by its equation (1), **u ← η·u + (1 − η)·|h|·Σ|w_out|** (Σ over all of the unit's outgoing weights, above); «n_eligible = number of units with age greater than m»; «c = c + n_eligible × ρ»; «If c > 1 Find the unit with smallest utility» (among the eligible) — «resample w[:, r] from distribution d» (the incoming weights, from the network's own init distribution by the seeded generator `(seed, "renew", i)`), «set w[r, :] to 0» (outgoing), «set u[r] = 0 and a[r] = 0», «c = c − 1». **Values:** η = 0.99 («set to 0.99 in all experiments»); m = 1,000 and ρ = 10⁻⁵ («A maturity threshold of 1,000 and a replacement rate of 10⁻⁵ resulted in the best performance» — its class-incremental CIFAR-100). Source: Dohare et al., Nature 2024, full text PMC11338828.
- **The retirement rule (the seat's C5; CONCLUSION §3 item 5), in every arm:** at each SLEEP, a cells' SIGHT cell is retired when, at 3 consecutive sleeps, the network NAMES the cell's most recent stored glance right with its ANSWER head's confidence above its own confidence band (A1's band, recomputed at each sleep from its right online answers) — «the learning network predicts its content within its band for N sleeps», read in the direction the network is trained (glance → name) — AND the cell's episodes are kept (citable, test 4a). Retirement removes the cell from recall only; never for disuse. The counts (alive, retired, merged by CYCLE) are a series per arrival.

### 4.2 The ladder
| # | arm | its one difference (from the arm named) | H at the start | births | renewal | other |
|---|---|---|---|---|---|---|
| 1 | **FIXED** — the FLOOR (Dohare's failing control) | — | BIRTH-RANDOM's FINAL H on the same stream and seed (so run after it) | none | none | — |
| 2 | **FIXED + CBP** — Dohare's cure as published | from 1: renewal, utility over AWAKE steps | as 1 | none | Algorithm 1, awake | — |
| 3 | **BIRTH-RANDOM** | from 1: births, from H0 = 64 | 64 | random in (the init distribution, generator `(seed, "birth", i)`), outgoing ZERO | none | — |
| 4 | **BIRTH-COPY** | from 3: the born unit's `W_ih` rows = the unit-normalised glance at the birth step, scaled to the init distribution's expected row norm; its `W_hh` rows and biases zero; outgoing ZERO | 64 | copy in, zero out | none | — |
| 5 | **BIRTH-RANDOM + RENEWAL-AWAKE** | from 3: Algorithm 1 with utility over AWAKE steps | 64 | as 3 | awake | — |
| 6 | **BIRTH-RANDOM + RENEWAL-REPLAY** | from 5: the utility's running average also updates on SLEEP-replay steps; ages and the replacement count `c` tick on awake steps only, in 5 and 6 alike — so the utility's counting is the ONE difference | 64 | as 3 | awake + replay utility | — |
| 7 | **BIRTH + DECAY** — E48's failing form (#227), the NEGATIVE control | from 3: at H = FIXED's width a birth REPLACES the least-USED unit (usage = the running mean of |h|, η = 0.99) instead of being refused; every 1,000 showings every weight × 0.98 | 64 | as 3, replacing when full | none | the cap that eats + the global decay |

### 4.3 What each arm is for
- 1 vs 2 replicates the paper's contrast on this box; 1 vs 3 prices growth; 3 vs 4 asks whether a COPY birth suffices (DEBATE D2 item 2); 5 vs 6 is the first measurement of renewal counted over replay (D2 item 1); 7 must FORGET — if it keeps the old, the retention instrument is suspect.

### 4.4 The controls — run first; a failing control VOIDS or makes NOT GRADABLE, never «fails» an arm
- **(C0) THE TOY:** each arm's machinery on B1 §5.5 (0b)'s XOR toy — 100 %.
- **(C1) THE INSTRUMENT SEES A LOSS — FIXED-HOT:** FIXED at lr × 10. If NEITHER FIXED nor FIXED-HOT shows a loss of plasticity on a stream (§5.1: a LOSS SHOWN — the whole interval past the band on the loss side), every plasticity mark on that stream reads **NOT GRADABLE — the stream is too short** (CONCLUSION §4.2's rule, with the hot twin as its positive control).
- **(C2) THE INSTRUMENT SEES FORGETTING — NO-REPLAY:** BIRTH-RANDOM with `sleep()` a no-op. Its pooled drop (§5.2) must EXCEED the retention bar; if it does not, every retention mark reads **NOT GRADABLE — the stream cannot make this network forget**.
- **(C3) KEY / SHIFTED-KEY** on B2's graders (B1 §5.5 (0c)). **(C4) FROZEN** — `state_sha` before = after every checkpoint sitting. **(C5) DISJOINT** — no held-out rendering's PNG sha on any TEACH row; a planted copy caught.

### 4.5 · A CONDITIONAL eighth arm — memory values against interference (added 2026-09-24 16:06 +0400 on the seat's word; enters only if B1's A1-MA holds its claim AND its isolation at both seeds — B1-PREREG §4.1)
- **BIRTH-RANDOM + MEMORY VALUES:** arm 3 with A1-MA's read-out (B1 §4.1), its table growing ONE ROW PER NEW NAME (a new token is a new row, zero-initialised, so a birth of a row changes nothing it computes) — one difference from arm 3.
- **The property it tests** (the seat's note): a row is written only when its token is present — growth without touching the old, against the interference Dohare 2024 and E48 measured. **The paper does not give this for free, in its own words:** «lookup-based computation does not by itself imply sparse gradient storage or sparse optimizer states» — under A1's SGD with momentum 0.9 an ABSENT row keeps moving on its stored momentum, and any weight decay moves every row. So the arm's TABLE is updated by a declared SPARSE rule: plain SGD on the rows present in the step, no momentum and no decay on the table (momentum kept for the rest of the network).
- **Its twin — the property's control:** the same arm with the table under the network's own momentum (the dense form). The property holds iff the sparse arm's retention drop (§5.2) is below the dense twin's by the declared margin at both seeds, with plasticity no worse.
- If B1's A1-MA does not hold, this arm is not built and the line says so in the VERDICT.

## 5 · The marks
### 5.1 Plasticity
- **ARRIVALS:** for each sign, showings-to-bar s = the first showing j in 2…11 at which its ASK was named right AND named right again at showing j + 1; never → 13. **P(k)** = the median of s over arrival k's five signs. **The mark:** the least-squares slope β of P(k) on k, with its 95 % interval from a seeded bootstrap over arrivals (2,000 resamples); **PASS iff the interval's UPPER end lies below the seat's band** (a loss is a RISE in showings-to-bar; a fall — learning to learn — is never a failure). A LOSS is SHOWN when the interval's LOWER end lies above the band. Printed beside it: the online accuracy per arrival (showings 2–12), and for every arrival the counts started / reached the bar / never (#168's addendum — a median over the signs that reached it alone would hide the ones that never do).
- **PERMUTED:** per task, the online accuracy = the share of its 100 ASKs named right (the paper's own measure: «the percentage of times the network correctly classified each of the … images in the task»); the slope over tasks, its bootstrap interval over tasks; PASS iff the interval's LOWER end lies above −band (a loss is a FALL in accuracy); a LOSS is SHOWN when the UPPER end lies below −band.
- **Gradability:** §4.4 (C1).

### 5.2 Retention (ARRIVALS only — the permuted stream never revisits an old permutation, and the paper measured plasticity only: retention on it is NOT GRADABLE by design)
- At each checkpoint, a tracked sign is KNOWN iff named right on the majority of its 3 held-out renderings. For each tracked arrival j: drop(j) = its known share at its own first checkpoint − its known share at the last checkpoint (k = 200).
- **The mark:** the pooled drop over the tracked arrivals whose first checkpoint comes before the last (1, 11, …, 181: 19 arrivals, ≤ 95 signs; arrival 191's first checkpoint IS the last, so it would add a zero by construction), weighted by signs, ≤ the seat's number (≤ 5 pp — CONCLUSION §4.2's «loses ≤ 5 pp of arrival 1», measured on the pool because arrival 1 alone is five signs and one sign is 20 pp); **arrival 1 is printed alone beside it**; the drop by age (arrivals since j) printed as a curve.
- Gradability: §4.4 (C2).

### 5.3 The fast store — the cells alive, retired and merged, per arrival; the fitted exponent of alive cells over k with its interval — **the seat's prediction: sublinear** (exponent < 1); linear means the retirement rule is not firing, and that is a finding, not a failure.

### 5.4 Cost — ms per event on one thread, printed against H for every growing arm.

### 5.5 Per stream, never blended (#170); every mark prints n, the denominator, the band or bar, the interval, and its control's reading.

## 6 · The decisions
- **What flips D2 (verbatim from `DEBATE.md` D2, the designer's round 1, accepted whole by the seat in round 2):** «if BIRTH-RANDOM loses plasticity like FIXED → birth is not diversity enough, and renewal-with-replay is a law; if RENEWAL-AWAKE keeps retention → Dohare's utility protects the old without replay, and the seat's reconciliation stands; if BIRTH-COPY matches BIRTH-RANDOM on the permuted stream → the random component is not needed where births come from new inputs.»
- **The rule it serves (CONCLUSION §3 item 4, verbatim):** «**Renewal** re-initialises a unit whose content is useless EVEN WHEN the old is replayed — measured, never assumed — and only if B2 shows that birth alone is not enough: its «use» is counted over the awake stream PLUS sleep replay of the old, never the awake stream alone.»
- **Predictions on the record (CONCLUSION §4.2, verbatim):** «BIRTH-RANDOM keeps both, on both streams; BIRTH-COPY keeps both on the arrival stream and loses plasticity faster on the permuted one; RENEWAL-AWAKE keeps plasticity and forgets arrival 1 (> 5 pp); RENEWAL-REPLAY keeps both; DECAY forgets; FIXED + continual backpropagation keeps plasticity and forgets the old; the fast store grows sublinearly (the seat).»
- A prediction is read only where its marks are gradable; a NOT GRADABLE mark decides nothing, and the seat carries the question to a longer stream in writing.

## 7 · The harness — B1 §8 verbatim, with these additions
- One `results.json` per (seed, stream) and one `VERDICT.md` per seed; the runner takes `--stream arrivals|permuted`; the permutations are applied by the harness (§2.5).
- `results.json` adds: `stage1 {pool, dropped_lookalike, dropped_duplicate, survivors, arrivals}`, per arm `plasticity {P_series, beta, ci, band, started_reached_never}`, `retention {per_arrival, pooled_drop, arrival1, by_age}`, `fast_store {alive, retired, merged, exponent, ci}`, `births {born, refused_budget, refused_bound}`, `renewals {count_series}`, and the controls C0–C5.
- The VERDICT prints, per stream: the gradability line first (C1, C2), then each arm's marks, then «what flips D2» evaluated WITH its inputs.

## 8 · Cost — [Guessing]; **the seat's solo probe (§3.6) replaces every figure here before the seat signs §11**
- ≈ 2–15 CPU-hours for the seven arms and both controls, both streams, two seeds — the range is how large the growing arms grow (a GRU step's cost rises with H²; the sleeps dominate at H near 1,024); the cache ≈ 16,000 canvases through the gaze [Guessing: minutes]. Everything on THIS box; `nice -n 19`; one thread per process; nothing beside a live life's read (#236).

## 9 · The builders — B2 is built after B1's harness is frozen and B1's A1 has landed (every B2 arm is A1 with one difference)
| builder | builds | may touch | may NOT touch |
|---|---|---|---|
| **Builder 2 · Sonnet 5** (B1's harness builder) | the CJK world (the sign sample, the rendering road, the names), the two tapes and `perms.npy`, the harness's permutation step, stage −1 for B2 (every clause), B2's marks, `results.json` / `VERDICT.md` for B2 | `brain/harness/` (B2 additions only), `brain/world_b2/`, `tests/brain/harness/`, `docs/brain/b2/` | anything under `genome/`, `creature/`, `tools/`, `world/`; `/data/alpha3-library/` (read-only); `/data/alpha2-library/` (read-only); the frozen `Arm` protocol; other builders' folders |
| **Builder 3 · Sonnet 5** (B1's soft-network builder) | the seven arms as configurations of A1 (births random / copy, Algorithm 1 with awake or awake + replay utility, the DECAY form, FIXED at a given H), the retirement rule, the controls FIXED-HOT and NO-REPLAY, each arm's §3.1 identity test | `brain/arms/soft/`, `tests/brain/arms_soft/` | the protocol, the harness, the graders, the world, other arms |
- At most three builders at a time (his rule); each lands through the seat's gate as in B1 §9.

## 10 · Seat traps — B1 §10 applies whole; and for B2 in particular
- **#227** — shrinking by disuse is forgetting: arm 7 is the negative control, never a candidate; «least-used» and «least-useful» are two different rules — Algorithm 1's utility weighs activity by the outgoing weights; E48's cap used activity alone.
- **#228 (b)** — a bar above its ceiling: a stream too short for FIXED to lose anything makes every plasticity mark a reading of the stream, not of the arm — hence C1.
- **#168's addendum** — a median of showings-to-bar computed only over signs that reached the bar is survivorship: print started / reached / never.
- **#233 / #238** — the births budget, the bound and the renewal count are SERIES on the record, never totals; a zero on the second constraint means nothing while the first refuses.
- **#171** — the permutation is applied in ONE place (the harness); a test asserts an arm receives permuted vectors and never the table.

## 11 · The seat's lines (appended, dated; never edited)
*(empty — the bars' numbers and the plasticity band after stage −1; the probe's numbers replacing §8; then the signature that makes this PREREG law)*

- **2026-09-26 12:22 +0400 — the seat, on his 12:18 word (CONCLUSION §9, addition 3):** §5.2 prints BWT beside every retention mark — BWT = the mean over the graded arrivals i < N of (acc_i at the end of the stream − acc_i right after arrival i), with n and its interval, and the NO-REPLAY control's BWT beside it: that control must read NEGATIVE, or the instrument cannot see forgetting and the retention marks are INSTRUMENT-VOID. A reader field, no bar. B2 stays DRAFT until the seat's bars line below.
