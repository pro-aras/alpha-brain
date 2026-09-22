*Appendix A of docs/organs/NEXT-LIFE-PLAN-2026-09-22.md — produced read-only by an Opus 5 agent on 2026-09-22 17:47–18:07 +0400 from the verdict records under /data/dev/genome/runs/ and /data/dev/genome-lives/*/readings/; filed VERBATIM by Claude (Fable 5.1), 2026-09-22 18:2x +0400, after re-verifying in the tree: world.py:85-96/111-118 (house, cup, zog, vex as described), verdict_g4.py:598 (the null gate is a strict > .5, so 5/10 is a tie), verdict_g4.py:457 (the reader string still reads v3 at 0b51288), and life 1's tape carries 0 rows of zog (grep -c).*

# Every mark that ever FAILED, and why — the creature's ten graded records

Read-only sweep, 2026-09-22. Every number is copied from a `results.json` / `VERDICT.md` on disk;
every mechanism claim carries a `file:line` I opened. Where a record has no such field the cell says
**not on disk** / **not recorded** — nothing is inferred from the register alone.

## The records read (and which reading is the verdict of record)

| life | genome | window | verdict of record | reader | record path |
|---|---|---|---|---|---|
| life 1 | `G4-life1.genome` 6e22b59f | 11.4 h | dry-run **b**, 2026-09-20 09:22 UTC | v1 (no version string) | `/data/dev/genome/runs/g4-verdict-dryrun-life1-b/` |
| life 1 (superseded) | same | 11.4 h | dry-run **a**, 08:37 UTC | v1 | `/data/dev/genome/runs/g4-verdict-dryrun-life1/` |
| life 2 | `G4.genome` e15d482b | 24.0 h | 2026-09-21 14:40 UTC | v2 | `/data/dev/genome/runs/g4-verdict-life2-20260921-1215/` (+ `…-v2control/`, byte-equal marks) |
| life 3a | `G4.genome` e15d482b | closed at h 3 | **no 24 h verdict on disk** — only its 2 h smoke | v2 | `/data/dev/genome/runs/g4-smoke-life3-2h/` (+ `-ctl`, identical) |
| life 3b | `G4.genome` e15d482b | 24.0 h | 2026-09-22 12:07 UTC (16:49 +04) | **v3.1** @ 0b51288 | `/data/dev/genome/runs/g4-verdict-life3b-20260921-1606/` |
| g5-seam-1 | `G5.genome` 5d1d67a2 | 8.0 h | v3.1 re-grade 08:36 UTC | **v3.1** | `/data/dev/genome-lives/g5-seam-1/readings/verdict-8h-v31/` |
| L1 | `L1.genome` 09c841da | 8.0 h | v3.1 08:35 | v3.1 | `/data/dev/genome-lives/g5-ladder-L1/readings/verdict-8h-v31/` |
| L2 | `L2.genome` 78396bae | 8.0 h | v3.1 08:35 | v3.1 | `…/g5-ladder-L2/readings/verdict-8h-v31/` |
| L3 | `L3.genome` 219033d6 | 8.0 h | v3.1 08:35 | v3.1 | `…/g5-ladder-L3/readings/verdict-8h-v31/` |
| L4 | `L4.genome` bf31799a | 8.0 h | v3.1 08:36 | v3.1 | `…/g5-ladder-L4/readings/verdict-8h-v31/` |
| L5 | `L5.genome` d6d5dc15 | 8.0 h | v3.1 08:36 | v3.1 | `…/g5-ladder-L5/readings/verdict-8h-v31/` |

**A record defect found while doing this** — every `verdict-8h-v31/results.json` writes
`"reader": "tools/verdict_g4.py v3 (…)"`, byte-identical to the v3 dirs: v3.1 never bumped the string
(`tools/verdict_g4.py:457` at 0b51288 == `:460` at 90ba695). The record cannot say which reader read
it; only the directory name can. **OWED: bump the version string.**

---

# (A) EVERY (life, mark) THAT FAILED — the verdicts of record

`bar` is shortened; the reading is verbatim from the record.
**Status vocabulary:** FIXED (names the commit or register row) · OWED (a fix is named, not yet made) ·
OPEN (a creature fact nobody has a fix for) · **N/A (no defect)** — a BY-CONSTRUCTION row, where the
mark graded something the life's tape or genome could not contain; nothing to fix in the creature,
though several of these are a reason to stop grading that mark on that window.

| # | life | mark | bar (short) | the reading | cause | mechanism (verified at) | status |
|---|---|---|---|---|---|---|---|
| 1 | life 1 | **(iv) grows alone** | ≥50 born · 0 refused · ≥5 % pruned · 0 disuse | born 400 · refused_budget **454** · arrivals **0** · budget_left **0** · pruned 94.85 % | **CREATURE (wiring)** | `BUDGET 400 per arrival` (`genome/G4.genome:37`) but nothing in the mind opened an arrival, so `_birth` fell to the `budget_left <= 0` refusal for the rest of the life (`genome/machinery.py:645-647`) | **FIXED** — the ARRIVAL gene (`genome/G4.genome:38`, PREREG §15); life 2 reads refused 0 / arrivals 17. PENDING 2026-09-20 12:43 |
| 2 | life 1 | **(vi) knows unknown** | plant majority answered · null majority abstains · Q5 ≥.80 · false ≤.20 | plant zog answered **0.00** (abstain novel 9, `triangle` 1) · null vex abstains 0.90 ✔ · Q5 1.00 ✔ · false 0.000 ✔ | **BY-CONSTRUCTION** | **the plant never reached life 1's tape**: `grep -c zog run-g4-life1-20260920-0042/tape/*.jsonl` = **0, 0**; the tape ends at `last_seq 16,420` while life 2 first delivers zog at **seq 30,001**. An 11.4 h window closes before the plant, so the mind abstains `novel` for the same reason every 2 h smoke does. (The register's "its word cell *would have* been refused" is a counterfactual about a delivery that never happened.) `zog` = an hourglass, two triangles meeting (`genome/world.py:111-113`) — hence the one wrong answer `triangle`. Note `vii_replay.plant_seq 602` is the **reader's own planted eye row**, a different plant | **N/A (no defect)** — life 2, first life whose window contains the plant, reads **10/10** |
| 3 | life 1 | **MODULATION** | at every window with NEW things a majority spike ≥3× last-50 median and settle by the 10th showing | F 0.048 · window 1 (cup, house, key, moon, tree): spike **0/5** (ratios .46/1.20/1.34/1.35/.63) · settled 2/5 · last50_med 0.2336 | **CREATURE (design of the old error)** | the pre-wave-3 PREDICT error never spiked at arrival: every new thing's first-3 median sat at 0.46–1.35× the running median. The record carries no regime road at all (`spike_regime`/`n_showings` = **null** under reader v1) | **FIXED** — wave 3's error (life 3b, same world, reads spike ratios **58.5×** and MODULATION PASS) |
| 4 | life 1 (a-read only, superseded 45 min later) | **(iii) growth matters** | frozen twin ≥30 pp under | T_frozen_Q1 **0.827** vs Q1 0.936 | **INSTRUMENT** | the twin was the **50-cell** frozen twin, not G0b's 10-cell one; 0.827 vs 0.936 is 11 pp | **FIXED** in dry-run b: `T_frozen_10_Q1` **0.094** vs Q1 0.950 → PASS |
| 5 | life 1 (a-read only) | **(xi) gaze earns place** | ≥.10 over the one-glance twin | Q1_gaze 0.936 vs Q1_one_glance **0.982** (twin WINS) | **INSTRUMENT** | the one-glance twin was built by setting `GAZE fixations 1` — which still gives it a full-resolution glance. G1's twin is gaze **mode 'one'** (the whole canvas at glance×glance) | **FIXED** in dry-run b: gaze 0.950 vs one-glance **0.688**, first-fixation-only 0.988 printed → PASS |
| 6 | life 2 | **(v) retention** | ≤5 pp on the last-of-window pair | w1 .991→.973→.964 (**2.7 pp**, ok) · w3 .982→.945→**.927 (5.5 pp)** | **CREATURE (fact)** | a real 5.5 pp loss across arrival window 3; the mark's own pair rule (§15). Life 3b reads **0.0 pp on both** odd windows; the six 8 h lives read +0.9 to +1.8 pp — it did not repeat | **OPEN** — not reproduced in 3b or any 8 h life; no fix was made, and none is owed unless it returns |
| 7 | life 2 | **MODULATION** | as #3, plus §18 add. 3 regime band | spike_regime **0/5** (band 1.6644, n=462) · settled_regime 5/5 · ratios .46–1.35 | **CREATURE (design of the old error)** | identical numbers to life 1 window 1 — the same pre-wave-3 error | **FIXED** — wave 3's error |
| 8 | life 2 | **W3-2 rules** | filed>0 · scored>0 · acc ≥.80 · clusters ≥.5 own cells · reach ≥5 of ≥5 words | filed **0** · scored 0 · induce **0** · reach **0 of 17** eligible | **BY-CONSTRUCTION** | life 2's genome declared INDUCE/DEDUCE **OFF** (`genome/G4.genome` edit note of 2026-09-20 00:38, "PREREG §14: INDUCE and DEDUCE declared OFF"); its journal carries **no `rule` think kind at all** — kinds `{word: 1479, null: 297}` over 1,776 thinks. §18 graded a mark the life's genome had switched off | **N/A (no defect)** — INDUCE went ON for life 3 (`G4.genome` edit note 2026-09-21 13:14) |
| 9 | life 2 | **W3-1 beliefs** | ≤1 raw `belief` row per word · revisits>0 · clashes reported | rows **1,424**, kinds `{belief: 1424}` · max **356** belief rows for one word · standing 16 of 17 heard | **CREATURE (wiring)** + an **INSTRUMENT** half | (a) the wiring: life 2 ran with "BELIEF's clash half is **unwired**" (`G4.genome` edit note 2026-09-20 00:38), so every observation opened a fresh belief row instead of a revisit/extension/clash. (b) the bar itself contradicted the clash law — a clash legitimately writes the new observation as a fresh belief row first (`genome/think.py:66-70`) | **FIXED both** — (a) the belief dedupe **D-G12**, commit **3ad7727** "genome/think.py — W3-1 (D-G12): believe() scoped, one belief per word" (+ b4d37e9 the kind counters, ada2003 the seam test), merged to master as **068e510** = life 3b's code: 261 rows / 28 belief / max 5 / extra 5 = clash 5 → PASS. (b) reader v3's `w3_1_beliefs()` accounts the clash row's belief side (PENDING 2026-09-22 11:2x, fix 2) |
| 10 | life 2 | **DOOR** | ≥300 pictures on the tape · ≥11 folder words | folder_rows **0** · pictures **0** · folder_words **[]** | **BY-CONSTRUCTION** | the folder door is armed only by an explicit `--folder PATH` (`creature/body.py:273-291` @75b0a9b, "default OFF") and life 2's unit passed none; its tape carries only `eye` 17,768 + `ear` 17,768 rows, no `folder/` dir exists in the run root | **N/A (no defect)** — the WORLD line armed the door from life 3 (`genome/G4.genome:66`, edit note 2026-09-21 13:14) |
| 11 | life 2 | **PARK** | ≥1 parked · share ≤5 % | parked **0** of 1,720 thinks · parked_rules 0 · sight-only rows on the tape **0** | **BY-CONSTRUCTION** | both declared dead-end sources were absent: no rule items (#8) and no wordless sight (#10). `dead_end()` is only reachable from a worked pool item (`creature/mind.py:718-727`) | **N/A (no defect)** — see row 20 for the real PARK reading |
| 12 | life 3a | **(vi)** (2 h smoke; no 24 h verdict exists) | as above | plant zog answered **0.00**, abstain novel 10/10 · null vex abstains 0.50 (`ring` 5) | **BY-CONSTRUCTION** (plant half) | the plant is delivered at canvas 5,000 ≈ hour 7; a 2 h tape cannot contain it. The null half is the real reading — see table B row 1 | **N/A (no defect)** for the plant half |
| 13 | life 3a | **(v)** (2 h smoke) | ≤5 pp | pairs **[]**, note "no odd window with exams on both sides → not readable" | **BY-CONSTRUCTION** | arrivals every 6 h; a 2 h tape has no odd window | **N/A (no defect)** |
| 14 | life 3a | **MODULATION** (2 h smoke) | as above | `graded_windows []`, reason field **null** in this record | **BY-CONSTRUCTION** | no window change inside 2 h | **N/A (no defect)** (reader v3 prints the reason; the 3b smoke record already carries it) |
| 15 | life 3a | **DOOR** (2 h smoke) | ≥300 pictures · ≥11 words | folder_rows 479 · pictures **240** · folder_words **9** | **BY-CONSTRUCTION** | one picture per 30-s scan; 240 in 2 h, 307 in 8 h | **N/A (no defect)** |
| 16 | life 3a | **W3-2 rules** (2 h smoke) | reach ≥5 of ≥5 eligible | eligible 21 · reach **1** (`bar`) · filed 6 · scored 6 · accuracy **1.00** · induce 12 | **CREATURE (wiring)** — and the row that nearly read as a PASS | INDUCE clustered on `r["cell"]` (the **sight** cell a word recalls) compared against `_answer_of(sight,c)`, a **words** index — `genome/think.py:427` carries the fix comment verbatim. 20 of 21 words could never induce; the one that did was an id coincidence. The mark's inner clauses (filed 6 / scored 6 / acc 1.00) all read PASS-shaped; only §18 add. 2's **reach floor** turned the mark FAIL | **FIXED** — commit **2641b75** (`r["cell"]` → `r["lit"]`), merged as **068e510**; life 3b reads filed 496 / reach 15 of 28. Life 3a was closed at its third hour on this defect |
| 17 | life 3b | **(iv) grows alone** | ≥50 born · **0 refused at ANY cap** · ≥5 % pruned · 0 disuse | born 1,705 · refused `{budget: 25, nmax: 0, frozen: 0}` · redundant 6,440 · arrivals 28 · budget_left 330 · pruned 93.3 % | **CREATURE (fact)** | 25 births met `budget_left <= 0` (`genome/machinery.py:645-647`) in the moments before an arrival refreshed the 400-birth budget. The drawn world alone stays under NMAX (born 1,705 of 2,000) | **OPEN** — no fix. Either the bar accepts a small budget-refusal count, or BUDGET/arrival pacing changes. His call |
| 18 | life 3b | **(vii) REPLAY** | two replays byte-identical; the plant caught | vs_live **(2, 'hash')** · two_replays **identical** · 19,270 rows · plant at seq 703 **caught** | **INSTRUMENT** | the life ran master **068e510**'s `state_hash()`; the reader's mind carries the repaired one, so the only differing field over 19,270 rows is `hash` (17,522 rows; `tools/replay_diff.py` reads IDENTICAL except `['hash']`). The gate is a conjunction over both comparisons at `tools/verdict_g4.py:548` | **OWED** — when the reader's commit ≠ the life's, declare `hash` volatile (#195) and grade REPLAY on every other field. Named in PENDING 2026-09-22 16:49 |
| 19 | life 3b | **W3-2 rules** | every rule's cluster ≥.5 of the word's OWN cells | filed 496 · scored 493 · **accuracy .986** · reach 15 of 28 · T-shuffle filed 0 · **38 rules under .5 own share, all `triangle`, .308–.444** (triangle owns 47 cells) | **CREATURE (fact)** | composite things share their parts' cells: `house` is drawn as a rectangle plus a triangular roof (`genome/world.py:85-88`), so a triangle rule's cluster is 56–69 % cells that are not triangle's own. *The record lists each rule's `word`/`cluster`/`own_share` but **cluster composition is not recorded** — which word's cells fill the remainder is the register's attribution, not the record's* | **OPEN** — a world/law question: either the exam's cell ownership admits shared parts, or the bar is stated per-composite. No fix exists |
| 20 | life 3b | **PARK** | ≥1 parked · share ≤5 % | parked **0** of 1,748 thinks (the reader's 24.0 h window) · parked_rules 0 · sight-only rows 1 | **CREATURE (fact)** | PARK parks only on the **n-th IDENTICAL (want, reason)** pair (`genome/park.py:31-44`; `PARK after 3 identical dead-ends`, `genome/G4.genome:55`). Counted over the life's **whole journal** (1,801 thinks, 24 h 45 min — 53 more than the reader's cut): the **think road** reached a dead end **4 times in total** — `no_cell_answers` for `circle` ×2, `ahmad` ×1, `camera` ×1 — so no want ever reached 3; the separate **rule-scoring road** (`park.answer(want, "rule_failed_3")`, `creature/mind.py:608`) fired **0 times** (`grep -c rule_failed_3` = 0, 0 over both journal days). Every other think outcome was productive: sight/filed 521, rule/filed 511, due/not_yet_due 503, word/belief 262 | **OPEN** — the bar asks for an event the pool almost never produces. Either lower n, count dead ends per want across reasons, or declare PARK not gradable on a world this legible |
| 21 | **g5-seam-1** | **(iv) grows alone** | 0 refused at ANY cap | born 2,031 · refused `{budget: 0, **nmax: 1,988**, frozen: 0}` · redundant 4,369 · arrivals 30 · budget_left 399 · pruned 89.9 % | **CREATURE (fact) — the capacity law** | `NMAX 2000` (`genome/G5.genome:41`) is a **lifetime budget of ids**, not a population cap: `_birth` refuses at `area.n >= area.nmax` where `area.n` is EVER-BORN and never decreases (`genome/machinery.py:626-628`), and the CYCLE merge pass lowers only the ALIVE count (`machinery.py:631-643`, the comment states ids are never reused so `build_ledgers` stays honest). The game's 7×7 frames + 307 folder pictures + the maker spent 2,000 sight ids by ~hour 6 | **OPEN → his call taken**: NMAX 4,000 for the next life's genome (PENDING 2026-09-22 16:49, his 16:14 word "we need to lift the cap"); the **id-reuse law** goes to a PREREG for his yes. Surfacing FIXED: STATUS's birth ledger + (iv) counting every cap (v3.1, commit 0b51288) |
| 22 | **g5-seam-1** | **(vi) knows unknown** | plant majority answered | plant zog answered **0.00** (abstain novel 9, `triangle` 1) · null vex abstains 0.60 (`ring` 4) · Q5 1.00 · false 0.009 | **CREATURE (fact)** — consequence of #21 | the plant's five showings birthed **no** sight cell because every birth hit the NMAX refusal; the same tape on L1–L4 (no game, nmax refusals 0) reads **10/10** | **OPEN** — resolved only by the NMAX decision above |
| 23 | **L5** | **(iv)** | 0 refused at ANY cap | born 2,031 · refused `{budget 0, **nmax 1,984**, frozen 0}` · redundant 4,358 · pruned 90.0 % | **CREATURE (fact)** | identical to #21 — L5 is the seam life minus one ear line the mind ignores | **OPEN** (same) |
| 24 | **L5** | **(vi)** | plant majority answered | plant **0.00** (`triangle` 1) · null abstains 0.60 (`ring` 4) · false 0.018 | **CREATURE (fact)** | identical to #22 | **OPEN** (same) |
| 25 | **L1** | **(vi)** | **null majority abstains** | plant zog answered **1.00** (`zog` 10/10 ✔) · null vex abstains **0.50** (`ring` 5) · Q5 1.00 · false 0.009 | **CREATURE (fact)** | the plant half passes; the null half fails on a **tie**: the gate is `n["abstain_rate"] > .5` (`tools/verdict_g4.py:598`), and 5/10 is not a majority. `vex` = a hexagon **outline** with a bar inside (`genome/world.py:114-118`) against `ring` = a circle outline (`world.py:57-60`) — the nearest alive cell resonates and `ABSTAIN second/best > 0.85` (`genome/G4.genome:70`) does not fire | **OPEN** — see table B row 1 |
| 26 | **L2** | **(vi)** | as above | plant 1.00 (`zog` 10) · null abstains **0.50** (`ring` 5) · false 0.009 | **CREATURE (fact)** | identical to #25 | **OPEN** |
| 27 | **L3** | **(vi)** | as above | plant 1.00 (`zog` 10) · null abstains **0.50** (`ring` 5) · false 0.027 | **CREATURE (fact)** | identical to #25 | **OPEN** |
| 28 | **L4** | **(vi)** | as above | plant 1.00 (`zog` 10) · null abstains **0.50** (`ring` 5) · false 0.027 | **CREATURE (fact)** | identical to #25 | **OPEN** |
| 29 | **L1** | **W3-2 rules** | every rule's cluster ≥.5 own cells | filed 165 · scored 162 · **acc .975** · reach 15 of 28 · T-shuffle 0 · **4 rules under .5: `circle` .469, .469, .471, .471** (circle owns 32 cells) | **CREATURE (fact, borderline)** | the same circle/ring confusion the null `vex` shows — two clusters land 1.5–3 pp under the .5 bar. Reader v3 labelled this " VOID by the wiring", which is the **reach**-floor message, not this clause | **Label FIXED** (v3.1 `w3_2_reason`, `tools/verdict_g4.py:845-857`, now names the own-cells clause). The reading itself is **OPEN** — a genuine borderline |
| 30 | **L2** | **W3-2 rules** | as above | filed 172 · scored 169 · **acc .982** · reach 14 of 28 · **4 rules: `circle` .484, .484, .471, .471** | **CREATURE (fact, borderline)** | identical to #29 | same as #29 |

### Counts for table A (the 30 verdict-of-record rows)

| class | rows | which |
|---|---|---|
| **INSTRUMENT** | 3 | 4, 5 (life 1's two wrong twins, superseded within the hour) · 18 (REPLAY's cross-version `hash`) |
| **CREATURE (wiring — a mind defect with a named fix)** | 3 | 1 (the un-refreshed budget) · 9a (the unwired clash half) · 16 (INDUCE's key) |
| **CREATURE (fact — no fix exists)** | 12 | 6, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28 · plus 29, 30 as borderline readings (**14 with those**) |
| **CREATURE (design of the old PREDICT error, fixed by wave 3)** | 2 | 3, 7 |
| **BY-CONSTRUCTION** | 8 | 2, 8, 10, 11, 12, 13, 14, 15 |
| **plus A2** | 4 instrument defects on the same records (MODULATION's plant window, the null's `all()`, (iv)'s single counter, W3-2's label) — all FIXED in v3.1 |
| **plus A4** | 2 false PASSES ((viii) COST in 9 records; (iv) in 2 under v3) |

## (A2) Where reader v3 differed from v3.1 on the SAME tapes (not rows above — the same records, an older instrument)

| mark | lives | v3 read | v3.1 read | cause of the v3 reading | fix |
|---|---|---|---|---|---|
| **MODULATION** | all six 8 h lives | **FAIL** — window 1 pass, **window 3 FAIL** (new 1, spike 1, settled 0) | **PASS** — window 1 by majority (settled 4/5 seam-1, 3/5 L1); window 3 moved to `not_gradable_windows` | **INSTRUMENT, a bar above its own ceiling (#228 b)**: window 3's only new thing is the PLANT, shown **5 times by design** (`genome/world.py:29`), and the clause is "settle by the **10th** showing" — `n_showings 5`, `err_10th null` | **FIXED** — `grade_modulation_windows(min_showings=10)` skips such a window, never FAILs it (`tools/verdict_g4.py:803-822`), PREREG §18 add. 4 |
| **MODULATION null** | same | `no_spike` False | `no_spike_regime` True (share under band 0.909) | **INSTRUMENT**: the fake-boundary null used `all()` over eleven things against a band that IS their own 95th percentile — false ~43 % of the time by construction (L1: ten of eleven under 2.27, `wave` 3.73) | **FIXED** — `null_clears()` grades by **majority** (`tools/verdict_g4.py:825-835`) |
| **(iv)** | seam-1, L5 | **PASS** | **FAIL** (rows 21, 23) | **INSTRUMENT — a false PASS**: the bar read `births_refused_budget` **alone** and saw 0 while 1,988 / 1,984 births were refused at NMAX | **FIXED** — `iv_refusals()` sums budget+nmax+frozen (`tools/verdict_g4.py:838-842`, used at `:573`) |
| **W3-2 reason** | L1, L2 | " VOID by the wiring: rules reached 15 of 28" (false — 15 ≥ the floor of 5) | " FAIL on the own-cells clause: circle 0.469 …" | **INSTRUMENT**: one message for two clauses | **FIXED** — `w3_2_reason()` (`tools/verdict_g4.py:845-857`) |

## (A3) The seven 2 h smokes — mostly the tape's own length

All seven read VERDICT FAIL. Per-mark, from `readings/smoke-2h/results.json` and `runs/g4-smoke-life3*-2h/`:

| mark | which smokes | reading | cause |
|---|---|---|---|
| (v) retention | all 7 | `pairs []`, "no odd window with exams on both sides → not readable" | **BY-CONSTRUCTION** |
| (vi) | all 7 | plant answered 0.00, abstain novel 10/10 | **BY-CONSTRUCTION** (plant at canvas 5,000 ≈ h 7) |
| MODULATION | all 7 | `graded_windows []` | **BY-CONSTRUCTION** (no window change in 2 h) |
| DOOR | all 7 | pictures **240** of 300, folder_words 9 of 11 | **BY-CONSTRUCTION** (1 picture / 30 s) |
| (iii) growth matters | **seam-1, L5 only** | `T_frozen_10_Q1` **null**, Q1 0.681 | **INSTRUMENT** — the frozen-10 twin knew ONE word on the game tape and `ask_glances` divided by `n − 1` → ZeroDivisionError inside the twin's exam. **FIXED**: refused by name at `genome/questions.py:144-152`; `self_exam.py` falls back to all things and stamps `seen_words_fallback_to_all` |
| W3-1 beliefs | **seam-1, L4, L5** | from the v2 smoke records: seam-1 63 rows (`belief` 19, `clash` 5, standing_words 14, **max 4** per word) · L4 37 rows (`belief` 13, `clash` 1, standing 12, max 2) · L5 66 rows (`belief` 19, `clash` 6, standing 13, max 4). *The v2 records carry **no** `extra_belief_rows` / `unaccounted` fields — those are reader v3's; the "extra 5 = clash 5" re-grade is the register's (PENDING 2026-09-22 11:2x), not this record's* | **INSTRUMENT** — the "≤1 raw belief row per word" bar contradicts the clash law (`genome/think.py:66-70`). **FIXED** in v3 |
| (viii) COST | all 7 | e.g. seam-1 **0.168 ms** "≤ 2 × 13.29 ms" → **PASS** | **INSTRUMENT, a false PASS** (see below) |
| W3-2 rules | 3a smoke | reach 1 of 21 | see row 16 |
| PARK | 3b smoke (0/167), seam-1 smoke (0/311), L5 smoke (0/311) | parked 0 | **CREATURE** — the game rungs park nothing at 2 h where L1–L4 park 1 of 167 |

## (A4) The two FALSE PASSES — marks that read PASS and were measuring the instrument

| mark | lives it falsely passed | the reading | why it is false | status |
|---|---|---|---|---|
| **(viii) COST** | life 1, life 2, **all seven 2 h smokes** | life 1: 21.37 "ms" ≤ 2 × 45.99 · life 2: 26.53 ≤ 2 × 47.36 · seam-1 smoke: 0.168 ≤ 2 × 13.29 | **#162, two different units**: `STATUS.mind_ms_median_1min` is the median of `mind.consume(row)` over EVERY tape row (ear, body, outcome rows included) while the probe is all rows' time ÷ **canvases** | **FIXED** — `viii_cost()` (`tools/verdict_g4.py:858`) grades only when STATUS carries `mind_ms_per_canvas_1min`; life 3b and all six 8 h reads say **not graded** with the reason. *Every (viii) PASS before 2026-09-22 was a reading of the instrument* |
| **(iv)** | seam-1, L5 under reader v3 | PASS with 1,988 / 1,984 NMAX refusals | see A2 | **FIXED** in v3.1 |

---

# (B) THE CREATURE FAILURES THAT REPEAT ACROSS LIVES

| # | what repeats | lives + numbers | what the code does (verified) | candidate fixes and what each would change |
|---|---|---|---|---|
| B1 | **the null plant `vex` is answered as `ring`** | life 1 abstain .90 (ring 1) · life 2 .90 (ring 1) · **3a smoke .50 (ring 5)** · 3b smoke .50 (ring 5) · **life 3b .70 (ring 3)** · seam-1 .60 (ring 4) · L5 .60 (ring 4) · **L1–L4 .50 (ring 5)** · all six 2 h smokes .50 (ring 5) | `vex` = a hexagon **outline** with a bar inside (`genome/world.py:114-118`); `ring` = a circle **outline** (`world.py:57-60`). At 32×32 through the sealed tower the two are near-identical, so the best cell resonates and `ABSTAIN second/best > 0.85` (`genome/G4.genome:70`) never fires. The gate is a **strict** majority, `> .5` (`tools/verdict_g4.py:598`) — 5/10 is a tie, not a pass. The comparator-error rungs (L1–L5, seam-1) sit at .50–.60 where the novelty-arm lives sit at .70–.90 | **(a)** tighten ABSTAIN (`second/best > 0.85` → e.g. 0.92): would raise abstention on vex and on every borderline real thing — measure `false_abstention` (now .009–.027) as the cost. **(b)** add a *novelty-distance* clause to ABSTAIN (abstain when max cos < THETA_N even if the ratio is close): targets exactly this case, because vex's glances are novel by `THETA_N 0.952` while their ratio is not. **(c)** leave the creature and state the bar as ≥ .5 — but then the mark stops separating anything |
| B2 | **`cup` never settles** | 3b err_10th **1.0** over 540 showings · seam-1 **1.0** / 180 · L1 **1.0** / 180 · L2 **1.0** / 180 · L3 **1.0** / 180 · L4 **1.0** / 180 · L5 **1.0** / 180. (life 1 / life 2, old error: err_10th **0.272**, settled) | `cup` is drawn as a filled box with an **inner box cut out** (`genome/world.py:92-96`) — an outlined rectangle whose ink is a thin frame. Under wave 3's error the per-thing prediction error **reads 1.0** at the 10th showing (and still 1.0 at the 180th/540th) while key/moon/tree fall to .0039–.022 in the same window. *The error's own range/ceiling was not measured for this note* | **(a)** treat it as a PREDICT-arm fact and add `cup` to a named "not predicted" list the mark reports rather than fails on. **(b)** widen the retina/glance for thin-frame ink (GAZE `ink` weighting) — would move `ring`, `vex`, `cup` together, so re-run B1's numbers after. **(c)** nothing: MODULATION already passes by majority (4/5 or 3/5) — this is a *named residue*, not a mark failure |
| B3 | **composite things borrow their parts' cells** | life 1 exam `per_thing_Q1`: **square .70**, diamond .70 (window 1 brought `house`) · life 2: circle .60, diamond .70 · **life 3b W3-2: 38 rules under .5 own share, ALL `triangle`, .308–.444** · L1/L2 W3-2: 4 rules, `circle` .469–.484 · `house` err_10th 1.0 on L1–L4 and 3b but **0.0089 (settled)** on seam-1 and L5 | `house` = rectangle + triangular roof (`genome/world.py:85-88`); `tree` = triangle + trunk (`world.py:89-91`). A composite's glances resonate on the part's cells, so the part's rule cluster is no longer its own. *The rule records carry `word`/`cluster`/`own_share` only — **cluster composition is not recorded**, so which word's cells fill the remainder is not readable from the record* | **(a)** record the cluster's composition (one field: the owning word of each cell) so the claim is measurable, then decide the bar — cheapest, unblocks the question. **(b)** let the own-cells bar admit cells owned by a word whose picture *contains* this one (a world fact the world module can declare) — turns 38 FAILs into a reported overlap. **(c)** change the world (draw house/tree without reusing part shapes) — but that removes the phenomenon rather than handling it |
| B4 | **PARK never fires on the G4 pool** | life 1 **0 / 817** · life 2 **0 / 1,720** · life 3b **0 / 1,748** · 3b 2 h smoke 0/167 · seam-1 **3 / 1,181** · L5 **2 / 1,180** · L1–L4 **1 / 605** · seam-1 & L5 2 h smokes 0/311 | PARK parks only on the **3rd IDENTICAL** (want, reason) pair (`genome/park.py:31-44`; the genome says `PARK after 3 identical dead-ends`, `genome/G4.genome:55`). Life 3b produced exactly **4 dead ends in 24 h** — `no_cell_answers` for `circle` ×2, `ahmad` ×1, `camera` ×1 — against 1,797 productive outcomes (sight/filed 521, rule/filed 511, due/not_yet_due 503, word/belief 262) | **(a)** count dead ends per **want** across reasons instead of per (want, reason): `circle` would still be at 2, so this alone does not fire. **(b)** lower n to 2 — makes 3b read parked ≥ 1 on `circle` and keeps the ≤5 % share trivially. **(c)** declare PARK **not gradable** on a world where the mind almost never dead-ends, and grade it on a world that produces dead ends (a harder door). Honest, and the mark stops being a coin-flip |
| B5 | **births refused at a cap** | life 1 **454 at BUDGET** (arrivals 0 — a wiring bug, FIXED) · life 3b **25 at BUDGET** over 24 h (arrivals 28, budget_left 330) · seam-1 **1,988 at NMAX** · L5 **1,984 at NMAX** · L1–L4 **0** | two different caps in one function: `budget_left <= 0` (`genome/machinery.py:645-647`) and `area.n >= area.nmax` where `area.n` is ever-born (`machinery.py:626-628`), plus CYCLE's soft ceiling reusing the nmax counter (`machinery.py:631-643`) | **NMAX**: (a) raise to 4,000 — **already decided** (PENDING 16:49, his 16:14 word); the edge matrix grows to 128 MB. (b) id reuse keyed by (id, birth epoch) — a **law change**, needs a PREREG + toy + a regression bar on the old worlds. **BUDGET**: (c) accept a small refusal count in (iv)'s bar with the count printed, or (d) refresh the budget on a schedule as well as on arrival — changes what "an arrival" means |
| B6 | **the plant cannot be learned when a cap is spent** | **seam-1 0/10** (NMAX 1,988 spent) · **L5 0/10** (NMAX 1,984) · against **life 2 10/10**, **life 3b 10/10**, **L1–L4 10/10** (all with 0 NMAX refusals). *Life 1's 0/10 is NOT an instance — its tape never carried zog (row 2); it is excluded here* | the plant's five showings must birth cells; `_birth` returns `None` at `area.n >= area.nmax` before any cell exists (`genome/machinery.py:626-628`). Verified consequence of B5, not a separate defect | resolved by B5. **The diagnostic worth keeping: (vi)'s plant clause is the only mark that detected a spent capacity budget** — (iv) under reader v3 read PASS on the same records |

---

# (C) WHAT PASSED IN EVERY LIFE IT WAS GRADED — the settled marks

Across the nine verdicts of record (life 1 dry-run b, life 2, life 3b, seam-1, L1–L5). Best / worst per mark.

| mark | bar | passed in | best reading | worst reading |
|---|---|---|---|---|
| **(i) knows** | Q1,Q2 ≥.80 · Q3 ≥.85 · Q4 ≥.90 | 9 of 9 | seam-1 / L5: Q1 **.982** Q2 1.0 Q3 1.0 Q4 1.0 (chance .032) | life 1 & life 2: Q1 **.936** (life 2 Q3 .955) — still 15× chance |
| **(ii) meeting is real** | the shuffled- and no-wire twins at chance | 9 of 9 | life 1 & L4: T-shuffle **0.000**, T-nowire 0.000 | seam-1: T-shuffle **.056** (nowire 0.000 everywhere) |
| **(iii) growth matters** | frozen-10 twin ≥30 pp under | 9 of 9 (the 08:37 life-1 read used the wrong twin; the seam/L5 **smokes** errored — A3) | seam-1 / L5: frozen-10 **.031** vs Q1 .981 (95 pp) | life 1 & life 2: **.094** vs .950 / .956 (86 pp) |
| **(vii) REPLAY** | two replays byte-identical; the plant caught | 8 of 9 (3b = row 18) | seam-1 19,274 rows, both comparisons identical, plant caught at seq 503 | L2 6,673 rows — identical, plant at 703 |
| **(ix) not luck** | own genome in the top quartile of 21 | 9 of 9 — for life 1 it is graded in the **08:37** read (rank **1 of 21**, composite .9977, best random `random-19` .9864) and **dropped from the 09:22 re-read** (the 20 random genomes were not re-run; the key is absent from that record) | life 2 / 3b / L3 / L4 / L5 / seam-1: **rank 1 of 21**, composite .9977 | L1 / L2: rank 1 of 21, composite .9932 |
| **(x) gaze finds the thing** | ≥.90 in the first 2 fixations · ≥1.5× random | 9 of 9 | identical in all nine: gaze **1.000**, random .0818, ratio **12.22** | same |
| **(xi) gaze earns its place** | ≥.10 over the one-glance twin | 9 of 9 (the 08:37 read used the wrong twin) | life 3b: .988 vs one-glance .713 (**+.275**); random gaze .175 | seam-1 / L5: .981 vs .788 (**+.194**) |
| **W3-1 beliefs** | ≤1 raw belief row per word beyond a named clash side · revisits >0 | 7 of 8 graded (life 2 = row 9; life 1 has no such mark — **not on disk**) | L3: 102 rows, 23 belief, max **1** per word, extra 0, clash 0 | L5: 230 rows, max **7** per word, extra **14** = clash 14, `unaccounted []` |
| **DOOR** | ≥300 pictures · ≥11 folder words | 7 of 8 graded (life 2 = row 10; life 1 has no such mark) | identical in all seven 8 h/24 h reads: folder_rows **613**, pictures **307**, folder_words **11** | same (sight-only rows 1) |
| **ALIVE** | every counter moves every hour; gaps bounded; NRestarts 0 | 9 of 9 | seam-1 / L1–L5: 8.0 h, max sense gap **5.1 s**, restarts 0, crashes 0, NRestarts 0 | life 3b: 24.0 h, max sense gap **6.6 s** (the morning's 48 replay workers stretched it from 5.1). Life 1: 11.4 h, gap 5.1. Life 2: 23.999 h, gap 5.2, **`nrestarts: null` — not read** for that record |
| **MODULATION** | window majority spike + settle; null clears | 7 of 9 under the verdict of record (life 1, life 2 = rows 3, 7) | life 3b: spike ratio **58.5×**, 4/5 spike, 3/5 settled | L1 / L2: 5/5 spike (82.99×), **3/5** settled |
| **(v) retention** | ≤5 pp | 8 of 9 (life 2 = row 6) | life 3b: **0.0 pp** on both odd windows | life 1: **4.5 pp** on window 1 |
| **PARK** | ≥1 parked · share ≤5 % | 6 of 9 (life 2, 3b = rows 11, 20) | seam-1 **3** of 1,181 (0.25 %) | L1–L4 **1** of 605 (0.17 %) |
| **W3-2 rules** | filed>0 · acc ≥.80 · reach ≥5 · clusters ≥.5 own | 4 of 8 graded (life 2, 3a, 3b, L1, L2 = rows 8, 16, 19, 29, 30) | L5: filed 272, scored 267, **acc .993**, reach 15 of 29, 0 wrong-cell rules | L4: filed 132, scored 126, acc .984, reach 15 of 28 |
| **PLANTS / TWINS / BANDS** | — | **never graded** in any record (`pass: null` in all ten) — they are report containers, not gates | life 3b TWINS: gaze twin Q1 .175 vs live .982; frozen twin .456; random-gaze loses (xi) by margin **.812** | — |

---

# (D) WHO FOUND THE FAILURE — the life, or a control run before it

**Count: 4 found by a pre-run control · 13 found by the life (or by an instrument built after it).**
Every INSTRUMENT defect but one was found *after* the record it corrupted existed.

### Found by a PRE-RUN control (before any life spent time on it) — 4

1. **The eye vector widened 112 → 144 and every other consumer still computed 112.** `tools/self_exam.py`
   run on a hard-link copy of the 6-min pre-flight root, before the seam life started:
   `ValueError: matmul … size 112 is different from 144` at `genome/machinery.py:539`
   (`runs/g5-integration-checks-20260921/self_exam.log`). The live exam duty would have died at the
   first canvas of the 8 h life; the passing re-run is `dry-A.self_exam.log` (Q1 .927, 2,296 moments).
2. **The reader's own planted divergence raised IndexError on a G5 tape** (index 300 among maker eye
   rows when the game and folder doors share the first 1,000 seqs). Fixed in commit **34f97f4** and
   proved by the 0.1 h dry-run before the life: `runs/…/dry-run-reader-0.1h/` REPLAY pass **true**,
   plant caught at seq 201.
3. **BIND refused by its own pre-registered bar** (Q1 0.9625 < 0.98125) and shipped **OFF** with its
   reason — commits b5f1f53 / 83ee412, before the seam genome was written.
4. **Two verdict-reader twin defects at landing J** (commit **0fd52fc**): the `T-one-glance` wrapper's
   frozen signature dropped the mind's new `colour=` keyword (TypeError in that worker on every G5
   verdict), and the no-wire twin rebuilt `Predictor` without the genome's declared error arm.

### Found by the LIFE — an instrument built or re-run after the record existed — 13

| # | what | found by |
|---|---|---|
| 1 | life 1's un-refreshed birth budget (row 1) | the **births-per-hour series** on the closed tape, not by any surface (PENDING 2026-09-20 12:43) |
| 2 | life 1's wrong (iii) and (xi) twins (rows 4, 5) | re-reading the same record 45 min later with corrected twins |
| 3 | W3-1's bar vs the clash law (row 9b) | the six 2 h smokes, 2026-09-22 10:1x |
| 4 | (viii) COST's units (A4) | the six 2 h smokes |
| 5 | the one-word exam's ZeroDivisionError (A3) | the seam-1 and L5 2 h smokes |
| 6 | INDUCE's sight-id-vs-words-index key (row 16) | an organ-research **code read** + a probe on a copy of life 3a's snapshot (commit ed37eb0) — *the 2 h smoke's own W3-2 clauses read PASS-shaped on one word; only §18 add. 2's reach floor turned it FAIL* |
| 7 | the pool-composition defect (79 % of life 3a's thinks were `due` items that can do no work) | life 3a's journal, after the life |
| 8 | **NMAX as a lifetime budget of ids** (rows 21–24) and (iv) reading one refusal counter (A2) | g5-seam-1's 8 h verdict failing **(vi)**, then a probe on the 8 h state |
| 9 | MODULATION's plant window — a bar above its ceiling (A2) | the six 8 h v3 reads |
| 10 | the null's `all()` over eleven things (A2) | L4's 8 h v3 read (ten of eleven under 2.27, `wave` 3.73) |
| 11 | W3-2's "VOID by the wiring" label on a real borderline (A2) | L1's 8 h v3 read |
| 12 | REPLAY's cross-version `hash` (row 18) | life 3b's 24 h read |
| 13 | the readers **starving** the lives (the game rungs ran 2 h behind their world); the SIT test's race; INDUCE's per-episode 2 MB copies | a **lag series** across snapshots, the full suite under contention, and profiling on a hard-link copy of the closed seam life |

**The pattern:** all four pre-run catches came from running a *consumer's own road* on a real (copied)
root before the life; all thirteen post-hoc catches came from a **series or a second reading**, never
from a surface. No mark ever failed for the reason its author expected without a second instrument
confirming it.

---

## What is owed, in one place

| owed | where | class |
|---|---|---|
| Bump the reader's version string (v3.1 records say "v3") | `tools/verdict_g4.py:457` | INSTRUMENT |
| REPLAY: declare `hash` volatile when the reader's commit ≠ the life's | row 18 | INSTRUMENT |
| NMAX 4,000 in the next genome (decided); the id-reuse law to a PREREG for his yes | rows 21–24, B5 | CREATURE law |
| Record each rule cluster's **composition** so B3 becomes measurable | row 19, B3 | CREATURE / instrument |
| Decide PARK: lower n, count per want, or declare not gradable on this world | row 20, B4 | CREATURE |
| Decide the null-plant clause: tighten ABSTAIN, add a novelty-distance clause, or restate the bar | rows 25–28, B1 | CREATURE |
| Decide (iv)'s budget clause: accept a printed refusal count or change arrival pacing | row 17, B5 | CREATURE |

*Written by Claude (Opus 5, 1M), 2026-09-22 18:03 +04 — read-only sweep; nothing under `/data/dev/genome`,
`/data/dev/genome-lives` or `/data/shariah-shadow` was modified, no service touched, no suite run.*
