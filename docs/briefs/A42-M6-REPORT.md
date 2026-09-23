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
