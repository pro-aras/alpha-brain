# A42-M6 — the sleep merge's O(n²) pass, made fast without moving one decision (builder report)
Written by Claude (Opus 5.5, M6 builder), 2026-09-23 17:14 +0400 — edit stamps are `date` at write time. Branch `a42-m6` off `a4-integration` at
**51f71ba** (51f71bada80ba50b72d370e178184a47fb9a01b9, the coordinator's 17:0x tip — the worktree was first cut at a50b0f3 and
reset to 51f71ba before any edit; `genome/machinery.py:_merge` and `genome/sleep.py` are byte-identical between the two).
Worktree `/data/dev/genome-wt-m6`. Nothing was run under a live root; every snapshot and tape read here is a `cp -a` copy in `scratch/`.

## 0 · NOT DONE (first, per the brief)
(filled at hand-back)

## 1 · The old road, written down BEFORE the fast road (the pre-registration clause — #197/#227)
Source: `genome/machinery.py` at 51f71ba, `Organism._merge` (lines 1810–1848, 39 lines, sha256 of the text
`4f6503dd91a983ed70447994174a8bc16c31cd8db1b9483dee97d79ee639a1b1`), called by `genome/sleep.py:cycle` as
`org._merge(area, list(area.alive_ids()), axis=axis)` for `(sight, 0)` then `(words, 1)`, then one `_prune` over every alive
row and column. `moment()` calls the same `_merge` with the moment's winners (≤ KWTA + a misfire birth).

1. **The set.** `ws = sorted(set(w for w in winners if area.alive[w]))` — alive AT ENTRY, deduplicated, ascending id. From
   `cycle()` the winners are `area.alive_ids()` (numpy int64, already ascending), so `ws` is that list, element type
   `numpy.int64`; from `moment()` they are Python ints. `a, b = ws[i], ws[j]` — the objects handed to every later step.
2. **The visit order.** `for i in range(len(ws)): for j in range(i + 1, len(ws))` — every unordered pair once, LEXICOGRAPHIC
   in (a, b) with a < b: the outer cell ascending, then its partners ascending.
3. **Per pair, four gates in this order, each a pure READ:**
   (a) `area.alive[a] and area.alive[b]` — read AT VISIT TIME (a merge earlier in the same pass sets `alive[b] = 0`);
   (b) the similarity `float(area.cells[a] @ area.cells[b])` — numpy `@` of two 1-D float64 rows of the C-contiguous
       `(capacity, dim)` array `area.cells` (sight dim 144, words dim 216), i.e. a BLAS `ddot` over `dim` terms in the
       library's own summation order (OpenBLAS, `OPENBLAS_NUM_THREADS=1` in the unit); NOT `Area.cos` (no traits head, no
       dead-cell −1); converted exactly to a Python float; skipped iff `<= self.g.theta_m` (a Python float, 0.9969 in
       ALPHA4.genome) — so a pair proceeds iff the value is strictly `>` theta_m, and a NaN would proceed (NaN `<=` x is False);
   (c) `aa, ab = self._answer_of(area, a), self._answer_of(area, b)` — read AT VISIT TIME from W/mask: for sight the row
       `W[c]` masked by `mask[c]`, for words the column `W[:, c]` masked by `mask[:, c]`; `None` when the mask is empty, else
       `int(np.argmax(np.where(m == 1, row, -inf)))` (ties → the lowest index);
   (d) proceed iff `aa is not None and ab is not None and aa == ab`.
4. **The merge (the only writes), in this order:** axis 0 — `ma, mb` = mask rows as float64; `W[a] = (W[a]·ma + W[b]·mb) /
   max(ma + mb, 1)`; `mask[a] = (ma + mb) > 0`; `strikes[a] = min(strikes[a], strikes[b])`; row b of W/mask/strikes zeroed;
   witness `mark_rows([a, b])`. Axis 1 — the same on columns a and b; witness `mark_rows(flatnonzero(mb))`. Then
   `alive[b] = 0`; `misfires[b] = 0`; `c["cells_merged_<area>"] += 1`; `merges.append((t, area.name, int(a), int(b)))`;
   and, when sound meetings exist, `_merge_pair_edges(area, a, b)` (each meeting's rows/columns a, b by the same rule).
   **The lower id is always the survivor** (a < b by the visit order).
5. **What the pass reads and writes — the fact the fast road rests on.** `area.cells` is READ ONLY in the whole pass: no line
   of `_merge`, `_answer_of`, `_merge_rows` or `_merge_pair_edges` writes it (the COST writer sweep pins `.cells` writers to
   birth/grow/load/allocation/the shadow). So gate (b) is a CONSTANT of the pass for every pair. The pass writes `alive`,
   `misfires`, W/mask/strikes (rows or columns a and b only), the counter, the merges log, the witness's dirty set and the
   sound meetings; gates (a) and (c) read `alive` and W/mask — so they are ORDER-DEPENDENT: (i) once b is merged into a,
   every later pair holding b is skipped at gate (a); (ii) once a has absorbed b, a's row/column is the union average and
   `_answer_of(a)` can CHANGE for every later pair (a, c) — a cascade no «decide every pair from the start state» road can
   reproduce; (iii) a merge on the sight axis writes rows a, b only, so `_answer_of(c)` of any other sight cell c is
   unmoved (the words pass reads the columns the sight pass rewrote — it runs after it, as `cycle()` orders them).
6. **A pair that fails gate (b) has no side effect** — gates (a)–(c) are reads; only step 4 writes. So a pair whose gate (b)
   fails can be REMOVED from the visit sequence without changing any read or write of any other pair, whenever it would
   have been visited. That is the whole licence of the fast road, and it covers nothing else: every pair whose gate (b) can
   pass must still be visited, in the old order, through the old gates (a), (c), (d) read at visit time.

## 2 · The fast road — the clause written before the code
- `_merge(area, winners, axis, fast=False)`: `fast=False` (every `moment()` call) walks EVERY pair in the old order — the
  old road. `fast=True` (only `cycle()`) walks the list `_merge_candidates(area, ws)` returns. The loop BODY is the old body
  unchanged, including gate (b)'s own expression on the same array objects — so every visited pair is decided by the old
  arithmetic, not by the filter's.
- `_merge_candidates(area, ws)` is READ-ONLY (writes nothing — the writer sweep does not see it): it gathers the alive
  cells `C = area.cells[ws]` (a bit-exact copy), computes `C[r0:r1] @ C[r0:].T` in row blocks (float64 BLAS gemm, the strict
  upper triangle only), and keeps every (i, j), i < j, with `NOT (S <= theta_m − margin)`, `margin = 1e-9`. Row-major
  `nonzero` inside ascending blocks gives the pairs in the old lexicographic order (asserted by a test).
- **Why no pair whose gate (b) can pass is dropped (the error bound, printed beside the margin):** for any evaluation order
  of a `dim`-term float64 dot product (sequential, blocked, SIMD multi-accumulator, FMA), `|fl(x·y) − x·y| ≤ γ_dim Σ|x_k y_k|`,
  `γ_n = n·u/(1 − n·u)`, `u = 2⁻⁵³` (Higham, Accuracy and Stability, §3.1). So `|ddot − gemm| ≤ 2·γ_dim·‖x‖·‖y‖`:
  3.2e-14 at dim 144 and 4.8e-14 at dim 216 for unit cells — 1/20,000 of the margin. A dropped pair has `gemm ≤ θ − 1e-9`,
  hence `ddot < θ` and the old gate (b) skips it. Measured on this box (numpy 2.3.5, OpenBLAS): `ddot ≠ gemm` in 87.6 % of
  sampled pairs at dim 144 (84 % of near-duplicates), max |diff| 5.0e-16 — so a road that DECIDED on gemm values would
  diverge from the old one at the threshold; the fast road only FILTERS on them.
- **Refusals (the road falls back to the old enumeration, never approximates):** any non-finite value in the gathered cells,
  or `2·γ_dim·max‖c‖²·4 ≥ margin` (norms far from 1), or fewer than 2 cells.
- **What it cannot change:** gates (a), (c), (d) and the merge run in the old order over a superset of the pairs whose gate
  (b) passes; every pair in the superset but not in the true set fails gate (b) exactly as in the old road (same expression,
  same arrays), so it writes nothing. `cycle()`'s order (sight, words, prune) and `_prune` are untouched.

## 3 · RED → GREEN (read from the log files, never from a claim)
- **RED** — `scratch/logs/red-test_merge_fast.log`: the new `tests/genome/test_merge_fast.py` on tree 764dd66, whose
  `genome/machinery.py` sha256 prefix 505165c12d3f8af6 is 51f71ba's (the log's first line prints both):
  `Ran 11 tests in 40.093s` · `FAILED (failures=1, errors=8)` — 3 × AttributeError (no `_merge_candidates`), 4 × TypeError
  (`_merge()` got an unexpected keyword argument 'fast'), 1 × the large toy's cost bar (`[M6 cost] … cycle() reference 17237 ms,
  fast 19797 ms (x0.9)` — both walks were the old road), and TestWiring's error was the TOY's own (a 300-cell toy ran out of
  ids — fixed by scaling the clusters with the toy's size before GREEN; RED-2 below re-runs the FINAL test bytes on untouched
  51f71ba so that test is seen failing for its own reason). Passing on the old code, as designed: the verbatim-reference pin
  and PC2 (both read only the reference).
- **GREEN** — `scratch/logs/green1-test_merge_fast.log`: `Ran 11 tests in 28.780s` · `OK`;
  `[M6 cost] toy 4104 alive sight x 390 words: cycle() reference 21078 ms, fast 434 ms (x48.5); merges sight 229 words 10`
  (the words figure is the alive count after the cycle's 10 word merges; 400 before).
- **The loop body is the old body:** a script extracted the 32 lines from `a, b = ws[i], ws[j]` to `_merge_pair_edges` in
  51f71ba and in the new `_merge`: identical after one dedent (the only text change is the loop header).
- **The targeted modules around the merge** (`scratch/logs/targeted.log`: the COST writer sweep, cycle-redundant, sleep, VOICE
  machinery, seam-5 witness × sound, COST witness, the creature cost seams incl. CycleTimesHash, the creature seam-5 sound
  seams): `Ran 92 tests in 93.865s` · `OK (expected failures=2)`. The writer sweep needs no new row: `_merge_candidates`
  writes nothing, and `_merge`'s writes are the old ones.

## 4 · The cost (ms per pass, both roads, the same process and load; nice 19, one BLAS thread, load 10–12)
| state (a COPY) | alive sight × words | OLD sight · words | FAST sight · words | merge pass | prune (same code) | candidates of pairs |
|---|---|---|---|---|---|---|
| toy (unit test, 4,320 born, 5 % dead) | 4,104 × 400 | cycle() incl. prune **21,078** | cycle() incl. prune **434** | ×48.5 (whole cycle) | in both | — |
| alpha4-1 hour-4 checkpoint (`evolve/checkpoints/3`), after a real 200-episode sleep | 3,727 × 604 | **14,185 · 303** | **98 · 5** | **×139.8** | 805 · 693 | 105 of 6,943,401 |
| alpha4-1 at 17:06 (`state/`), after a real 200-episode sleep | 6,217 × 1,201 | **47,786 · 1,893** | **311 · 19** | **×150.8** | 3,345 · 3,102 | 142 of 19,322,436 |

Logs: `scratch/logs/bench-ckpt3.log`, `scratch/logs/bench-latest.log` (tool: `tools/m6_merge_bench.py`, committed). On real
tapes (§5.3), the rows that carry a sleep (200 replayed moments + the cycle) read, untouched 51f71ba → a42-m6:
3,559 → 1,427 · 2,307 → 1,537 · 3,688 → 1,571 · 6,080 → 2,109 · 6,625 → 2,354 · 9,288 → 2,367 · 8,355 → 2,617 ·
11,369 → 3,741 ms (the eight sleeps of alpha4-pre-3's tape; `--timings`, the same flags; what remains is the replay's
moments and the prune). **The fast road is still O(n²) in arithmetic** (one gemm over the upper triangle — 0.31 s at
6,217 cells, [Guessing] ≈ 3 s at 20,000 and ≈ 20 s at 50,000); it removed the Python loop, not the square.

## 5 · The identity proofs — what each proves and what it does not
1. **The toy (the unit tests).** fast ≡ reference on the merge list (pairs, order, survivor), the counters, both alive
   vectors, the dense `state_hash` and the per-row `row_hash` under BOTH hash forms (dense; HASH sparse — plus the witness ==
   its from-scratch recompute), at 700 alive cells with every planted case and at 4,104 alive cells through the whole
   `cycle()` (229 sight + 10 word merges). The planted cases pin the order-dependence: A (a merges b then c; (b, c) never), B
   (a's answer moves away after absorbing b: (a, c) refused), C (a's answer moves TO c's: (a, c) merged), D (argmax tie → the
   lowest id), E (None never merges), F1 (EXACTLY theta, one-hot construction exact in every summation order: no merge), F2
   (one ulp above: merge); dead cells interleaved so no cell id equals its index in the alive list (#234).
   **The positive controls, each SEEN:** PC1 — F2's similarity moved one ulp down onto theta: the merge lists differ in
   exactly that pair, and the same perturbation under the reference is identical again; PC1b — theta set to the smallest
   merged similarity (the advisor's form): differs, and the reference under it is identical to the fast road under it; PC2 —
   answers read once before the pass (the «decide every pair from the start state» shape): differs, B's (a, c) merged on the
   stale answer and C's (a, c) lost; PC3 — gate (b) decided on a gemm entry instead of the old 1-D `@`, with theta placed
   BETWEEN one isolated pair's two values: the reference and the mutant differ at that pair while the fast road equals the
   reference. **Does not prove:** anything about sound meetings (the toy declares none — covered by the seam-5 suites, green
   under the fast cycle, §3), nor real distributions (below).
2. **Real states (the bench on copies).** After a real 200-episode sleep on the hour-4 checkpoint and on the 17:06 state, the
   OLD cycle body on one copy and the FAST on the other: merges, counters, alive vectors and `state_hash` identical (ALL
   IDENTICAL: True, both). Measured beside it: `ddot ≠ gemm` in 76 of 105 and 101 of 142 candidates, max |ddot − gemm|
   5.6e-16 and 6.7e-16 against the bound 3.2e-14 and the margin 1e-9. **Thin:** the cycles themselves merged 1 and 3 pairs
   (the rest of the 15 and 29 merges were the sleep's replayed moments, the moment road in both), because cycles fire every
   sleep and little is pending. The first timing run (`scratch/time_old_cycle_alpha4-1.log`: the OLD road alone on the 17:01 state, no sleep
   before it — sight 37.7 s, words 1.3 s, prune 1.2 s at 6,174 × 1,190, load ≈ 7) merged 0: a comparison there would have been
   vacuous, which is why the bench replays the sleep first.
3. **alpha4-pre-3's closed tape** (10,864 rows, 8 sleeps, 8 cycles true; its own GENOME.genome; `--closed --timings`),
   replayed under untouched 51f71ba (a `git archive` copy, `scratch/ctl-51f71ba`) and under a42-m6 (fc6d36d, clean):
   `tools/replay_diff.py … --ignore ""`: `8968 mind rows · compared 8968 · rows with a non-ignored diff: 0 · IDENTICAL
   except ['']: True`; the two journals are BYTE-identical (sha256 cedc2c7e60d25868…). Every mind row carries the DENSE
   state hash (the genome declares no HASH; 2.002 hashed rows per canvas + one per sleep), which folds cells, alive, misfires,
   W/mask/strikes, the counters and the whole merges log — so the state after each of the 8 real cycles is identical, not only
   the decisions journaled. **Does not prove:** sizes beyond pre-3's (≈ 2,000–2,500 alive cells; the bench covers 3,700 and
   6,200); the per-cycle merge counts (not journaled — the observer run below reports them if it ran).
4. **The alpha4-1 hour-1 fixture** (4,322 mind rows, 3 sleeps, all cycling), `genome/ALPHA4.genome` (sha256 a68870a8…, the
   same in 2357347, 51f71ba and a42-m6), `--timings`, no `--closed` (a mid-life cut, as the 14:00 control):
   (a) **a42-m6 vs untouched 51f71ba, hash included: IDENTICAL, 0 rows differ** (byte-identical journals, sha256 345ac27a…);
   (b) a42-m6 vs the 14:00 master control (`genome-wt-induce/…/h1-alpha4-master`, 2357347), `--ignore readiness`:
   IDENTICAL, 4 rows differ only in `readiness`; (c) untouched 51f71ba vs the same control, `--ignore readiness`: the same 4
   rows — (c) is the integration branch's own fact (the judge-units change), not M6's.
5. **The landing gate** (`tools/gate_g5_landing.sh a42-m6`, §6).

## 6 · Measured, not fixed (the brief's two questions)
1. **A sleep at alpha4-1's current size** (a COPY of its 17:06 state: t 110,700, 6,204 alive sight → 6,217 after the sleep,
   1,201 words; nice 19, one BLAS thread, load ≈ 10–11 — the live mind runs at nice 0, so its absolute figures are smaller
   [Likely], the ratios the same): `sleep()` (the 200 most-surprising episodes replayed as moments) 1,341 / 1,371 ms on the two
   copies; the OLD cycle 47,786 (sight merge) + 1,893 (words merge) + 3,345 (prune) ≈ **53.0 s**; the FAST cycle 311 + 19 +
   3,102 ≈ **3.4 s**, of which the untouched prune is 91 %. The whole sleep ≈ 54.4 s → ≈ 4.8 s. [Certain for the copy]
2. **The merge's share of a canvas vs the hash's.** `state_hash()` (ALPHA4.genome declares no HASH, so `row_hash` IS
   `state_hash`) costs 368 / 398 / 393 ms a call on the 17:06 copy, and a canvas writes 2 hashed rows (2.002 per eye row on
   pre-3's replay journal: the moment row and the coarse row; + 1 per sleep) ⇒ ≈ 0.76 s a canvas. alpha4-1's per-canvas cost
   (STATUS `mind_ms_per_canvas_1min`, the a4-ladder 5-min series, 15 samples 16:25–17:40 +04 at 7,146–7,733 cells): median
   2,465 ms (1,103–6,681; the high ones sit on sleeps) ⇒ **the hash ≈ 31 % of a canvas** [Likely: a copy's timing against a
   live median] — §11 (4)'s «a third» holds at this size. **The merge:** ≈ 49.7 s a sleep; a sleep every ≈ 16.4 min (11 in
   180.1 min, 14:39 → 17:40 +04) ≈ 460 canvases (2,500 moments less the 200 replayed, 5 moments a canvas) ⇒ ≈ 108 ms a canvas
   amortised ≈ **4.4 %** — but paid as ONE stall of ≈ 20 canvases' worth of backlog at 2.465 s a canvas, the stall the review
   saw as 1.5–1.8 s canvases and 7.12 s sense gaps. After M6 ≈ 0.33 s a sleep (≈ 0.7 ms a canvas amortised); the prune's
   ≈ 3.1 s stays, and so does the hash's ≈ 31 %.
