# Builder F (Sonnet 5) report — the BIND diagnostic, the state_hash repair, the retina vectorisation
*edit: Claude (Sonnet 5, builder F), 2026-09-21 17:34 +0400. Brief: `docs/briefs/G5-F-BIND-DIAGNOSTIC-AND-REPAIRS.md`. Branch `g5-repairs`, worktree `/data/dev/genome-wt-k`. Nothing committed; the diff is on disk, uncommitted, for the orchestrator's review.*

---

## 0 · A finding that gates everything below, found while building task 2

**Master HEAD's code does not reproduce life 2's real trajectory.** genome/predict.py's PREDICT error law was rewritten (commit `5a6dcfe`, "D1 (W3-2b): PREDICT's error moves inside the organism", 2026-09-21 11:18 +0400) — landing on master **after life 2 had already been running for 23 hours** (life 2's run root was created 2026-09-20 12:12:33 +0400, right after commit `75b0a9b`, the last commit before it). Because the creature runs as a long-lived `creature.service` that does not hot-reload code, **life 2's actual run used the OLD PREDICT law for its entire life** — the new law only ever ran in later worktrees (wave 3) and in life 3.

Replaying life 2's own tape through current master HEAD's `Mind`/`Organism` (a plain, "correct-looking" replay) diverges from life 2's real live journal starting at the **second canvas** (`err`/`lr` differ immediately; genome/predict.py's target computation changed). The divergence cascades: **17,533/17,807 rows differ on `err`, 17,524 on `lr`, 17,694 on `cells`, 10,741 on `edges`, 760 on `births`** — a replay under master HEAD ends with **739 alive sight cells against life 2's real 668**. A diagnostic built on that replay would answer the BIND question for a creature life 2 never was.

**Verification and fix, not a workaround.** `git diff --stat 75b0a9b master -- creature/ genome/ tools/` shows +950/-124 lines across 14 files since life 2 started (mind.py, think.py, predict.py, body.py, tape.py, curiosity.py, park.py, genes.py, senses/folder.py, world_maker.py, G4.genome, gate_g4.py — the whole of wave 3). **`genome/machinery.py` itself is byte-identical between `75b0a9b` and master** (`git diff` empty) — so the state_hash repair applies unchanged to either tree. I created a **second, separate worktree** `/data/dev/genome-wt-k-hist` (`git worktree add /data/dev/genome-wt-k-hist 75b0a9b`, detached HEAD, never committed to, never touching `/data/dev/genome`), applied the *identical, uncommitted* state_hash edit there, and **verified byte-identical reproduction of life 2's live journal — including `hash` — on a 220-row sample, before any repair** (`creature.replay --against`: `REPLAY identical: 220 mind rows`). This worktree is what task 1's diagnostic and task 2's two replay-identity proofs below actually ran against. Both worktrees are left on disk for the orchestrator's review; `genome-wt-k-hist` can be removed with `git worktree remove /data/dev/genome-wt-k-hist` once inspected — it carries no commits, only the same uncommitted state_hash edit as `genome-wt-k`.

**Raised, not decided:** the orchestrator should know that **any replay-based diagnostic or gate built against life 2 (or life 1, which also predates several of these commits) must run under the commit that was actually live**, not master HEAD, or it silently measures a counterfactual life. `tools/verdict_g4.py`'s own life-2 read may be affected by the same issue in places that depend on `err`/`lr`/cell counts rather than on the tape/journal's own recorded fields — not verified here (out of scope for this brief), flagged for whoever owns that reader.

---

## 1 · THE BIND DIAGNOSTIC — is the 1.9 pp binding or clutter?

Run: `/data/dev/genome-wt-k-hist`'s Mind (life 2's true code + the state_hash repair), life 2's full tape (35,536 rows, 17,768 canvases) replayed once into a fresh temp root, with two OBSERVE-ONLY instrumentation points (never touching any file): `Mind._consume_eye` wrapped to snapshot `org.t`/`len(org.births)` before and after each canvas and to independently recompute `gaze.glances()` on the same payload for `fix` (a pure function, no side effects); `Organism._misfire` REPLACED with a byte-for-byte copy of its own body plus one line recording every time the `else:` (misfire) branch fires — diffing `misfires[]` before/after would UNDER-count, because a streak that reaches the birth-error threshold resets to 0 in the same call. Final state: `org.t=78872 sight.n=700 words.n=17`, `state_hash=8472af1850b77e2a709a3edfbc677277e0c7968c1cacb129f9eb92082cb3b694` — **`cells=[700,17]` matches life 2's real end state exactly** (STATUS.json's `cells: 685` is the ALIVE count after merges; `sight.n=700` is the ever-born count, matching `organism.json`'s own `sight_n: 700`).

For each SIGHT birth: `glance_index = birth_t − canvas_t_before` (t advances by exactly 1 per glance); on/off-thing from that glance's fixation cell against `truth/{seq:09d}.json`'s `cell` (Chebyshev ≤ 1, `genome/run_g1.py:60-61`); cross-thing edges from `org.edges_log`, with the thing at each edge's moment read from `mind.moment_word[moment]`.

**(A) sight births by glance index** (700 total; 2 births at glance 26/37 are SLEEP-episode-replay artifacts — `org.t` values from a replayed OLD episode, not a normal glance 0–3 — 0.3% combined, excluded from the discussion below):

| glance | births | share |
|---|---|---|
| 0 (first fixation) | 156 | 22.3% |
| 1 | 91 | 13.0% |
| 2 | 207 | 29.6% |
| 3 | 244 | 34.9% |

**77.5% of all sight births happen on glances 1–3, not glance 0** — three extra looks account for more than three-quarters of the organism's entire sight vocabulary.

**(B) fixation on/off-thing rate by glance, over all 17,768 canvases** (Chebyshev ≤ 1 to the truth cell):

| glance | on-thing | rate |
|---|---|---|
| 0 | 17,656 / 17,768 | 99.37% |
| 1 | 17,561 / 17,768 | 98.83% |
| 2 | 17,111 / 17,768 | 96.30% |
| 3 | 16,455 / 17,768 | 92.61% |

Later glances drift toward clutter (inhibition-of-return pushes the gaze off the just-visited region), but the drift is modest — even at glance 3, 92.6% of fixations are still on the thing.

**(C) sight births by (glance bucket × on/off-thing):**

| | on-thing | off-thing | unknown |
|---|---|---|---|
| born glance 0 | 155 | 1 | 0 |
| born glance 1–3 | 473 | 69 | 2 |

Glance-0 births are almost never off-thing (0.6%). Glance-1–3 births are off-thing **21× more often** (12.7%) — but **87.3% of the extra births (473 of 542) are still ON the thing.** Clutter is real but explains only a minority of the extra births.

**(D) misfire events, attributed to a cell's OWN birth bucket:**

| bucket | cells born | ever misfired | events total | events/cell |
|---|---|---|---|---|
| born glance 0 | 156 | 27 (17.3%) | 812 | 5.205 |
| born glance 1–3 | 544 | 152 (27.9%) | 3,697 | 6.796 |
| born ON-thing | 628 | 160 (25.5%) | 4,128 | 6.573 |
| born OFF-thing | 70 | 19 (27.1%) | 381 | 5.443 |

**(E) cross-thing edges** (a sight cell's edges, over its whole life, naming more than one distinct thing):

| bucket | cells | touch >1 thing | mean distinct things/cell |
|---|---|---|---|
| born glance 0 | 156 | 28 (17.9%) | 1.244 |
| born glance 1–3 | 544 | 179 (32.9%) | 1.634 |
| born ON-thing | 628 | 185 (29.5%) | 1.540 |
| born OFF-thing | 70 | 22 (31.4%) | 1.629 |

**The two-line answer.** Split by **glance index** (0 vs 1–3), the gap is large and consistent across both instruments: nearly **10 points more likely to ever misfire** (27.9% vs 17.3%) and **15 points more likely to be wired to more than one thing** (32.9% vs 17.9%). Split by **on/off-thing** alone, the gap is much smaller and inconsistent across the two instruments (25.5% vs 27.1% misfire; 29.5% vs 31.4% cross-thing — off-thing is not clearly worse). **Binding, not clutter, is the dominant mechanism**: the glance-index signal dominates the on/off-thing signal, and 87.3% of the extra glance-1–3 births are themselves on-thing — meaning most of the damage is not "the third glance landed on a clutter stroke", it is "the second and third looks at the SAME, correctly-fixated object keep birthing new, less-reliable cells instead of reinforcing one shared percept", exactly the gap G-EYE-2 names (*"one object, several fixations, ONE percept"*). A real, smaller clutter contribution sits alongside it: the 69 off-thing births (12.7% of glance-1–3 births, 21× glance 0's rate) are a second, independent source of unreliable cells. **`BIND glances per canvas` is the fix indicated by this data; `GAZE surprise fixations 1` would also remove the clutter births but would throw away the 87.3% of extra births that are legitimate (if redundant) looks at the thing.**

---

## 2 · STATE_HASH — hash only the live block

**The precondition, verified, not assumed.** A cell id is only ever written by `_birth()` with `cid < area.n` at write time, and `area.n` never decreases (CYCLE retires/merges cells but keeps their ids below `n`) — so every nonzero entry of `W`/`mask`/`strikes` already lies inside `[:sight.n, :words.n]`. Checked on the three real closed life snapshots on this box:

| life | nmax | n_s | n_w | W: total=block? | mask | strikes | bytes hashed today → live block |
|---|---|---|---|---|---|---|---|
| life 1 | 2000 | 384 | 16 | 226 = 226 | 226 = 226 | 2 = 2 | 40.00 MB → 0.0614 MB (0.15%) |
| life 2 | 2000 | 700 | 17 | 430 = 430 | 430 = 430 | 5 = 5 | 40.00 MB → 0.1190 MB (0.30%) |
| life 3a | 2000 | 1113 | 23 | 509 = 509 | 509 = 509 | 4 = 4 | 40.00 MB → 0.2560 MB (0.64%) |

Invariant holds exactly on all three; pinned in `tests/genome/test_state_hash_live_block.py` (also on a fresh toy organism, so it isn't a fact about only these three snapshots).

**(a) Timing, solo, median of 20, life 2's end snapshot** (loaded once with the pristine pre-repair algorithm — needed to pass `Organism.load`'s own check — then both the old and new hash functions timed as standalone functions against the same in-memory object, so neither timing pays for reload/import):

- OLD (full 2000×2000 arrays): **median 35.86 ms** (min 35.76, max 37.59)
- NEW (live block only): **median 7.29 ms** (min 7.12, max 7.47)
- **speedup 4.92×**

Note for the record, not a defect: the remaining 7.29 ms is now dominated by `json.dumps(edges_log)` + `json.dumps(prunes_log)` (≈2.94 ms + ≈2.89 ms on life 2's 15,293/14,830-entry logs) — "the counters as now" per the brief, correctly left untouched; this is where the NEXT optimisation would have to look (these lists grow with the life, not with `nmax`, so the win here is already the dominant one — `sha256(W.tobytes())` alone was ≈22.8 ms of the old 35.86).

**(b) Two fresh replays under the new hash, life 2's true tape, in fresh temp roots** (`/data/dev/genome-wt-k-hist`, life 2's true code + the repair): both end at `state_hash = 8472af1850b77e2a709a3edfbc677277e0c7968c1cacb129f9eb92082cb3b694`, `cells=[668,17]` — life 2's real final alive count. `creature.replay.compare(replay_A, replay_B)` → **`None`** (every field, including `hash`, identical).

**(c) Replay against life 2's LIVE journal** (`run-g4-life2-20260920-1212/journal/*.jsonl`, 19,583 rows): a comparator that skips only the `"hash"` key found **0 non-hash differences across all 19,583 rows** (`distinct non-hash keys that differ: []`). A separate check confirms the repair is real, not a no-op: of the 17,807 rows carrying a `hash` field, **all 17,807 differ** (0 accidentally equal). This is the strongest possible form of the brief's ask: identical in every field except `hash`, proved by exhaustive comparison, not sampling.

**(d) The new digest for the pin.** Two different digests are in play and both are reported, never edited on master:
- **G4-2's own pin** (`tools/gate_g4.py`'s `gate2()`, G4-skeleton.genome's 660-canvas toy dev stream): OLD `d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86` → **NEW `b05315037ff98529836472e6ddd9ebb5a45742b0511f5facf6b73cd754fa1e3f`**. Independently re-derived twice (once via a scratch call into `gate_g4.build_tape`/`consume_all`, once as the value the pinned tests below compute) — both agree.
- **Life 2's own true end-state digest** under the repair: `8472af1850b77e2a709a3edfbc677277e0c7968c1cacb129f9eb92082cb3b694` (matches (b) and the standalone timing script (a) independently).

**`Organism.load`'s saved-hash assertion does NOT survive on old snapshots — by design, and verified, not assumed:**
```
GenomeError: loaded organism's state_hash 8472af1850b77e2a is not the saved 07498bf839b9d090
```
raised on life 2's real `state/organism.npz`+`.json` under the repaired code. This is the correct behaviour of a changed digest — a loud, named refusal, never a silent accept — but it means **a resume of any live creature after this repair merges would refuse to start** until its snapshot is regenerated or a migration path is added. **Raised, not decided:** the orchestrator's call is between (i) a hash-version tag in `meta` with a fallback comparator for old-format digests, (ii) a one-time snapshot migration (re-save under the new algorithm) run before/at merge, or (iii) accept the break and require every live creature to start from a fresh root at merge time. A positive control sits beside the refusal: saving and reloading under the SAME (new) code round-trips cleanly (`tests/genome/test_state_hash_live_block.py::test_a_snapshot_saved_under_the_new_code_round_trips`).

---

## 3 · THE RETINA VECTORISED

New module `genome/retina_fast.py` (sha256 `452602160658d8253c477953476d1d91c7cfbadebc0241ba75abfdd74e343b1d`) — `cell_means_fast` replaces the pure-Python per-pixel loop (88% / 4.77 ms of the retina's 5.42 ms, EYE.md §0.3 row 2) with numpy `bincount`-based integer accumulation over the SAME non-uniform grid mapping (`cy = min(grid-1, y*grid//h)`, general, not special-cased to 128×128). `channels()`/`saliency()`/`classes_at()` are **reused unmodified** from the pinned oracle (`organs/retina.py`, sha `aa95693d…` — the same pin `genome/gaze.py` already carries) via its own independent sha-check, so any divergence could only come from `cell_means_fast`. `organs/retina.py` itself is **never edited** (its own header: "the ORACLE for the later C++ port"); `genome/gaze.py` is **untouched** and still calls the original oracle in production — this is an additive module, not a rewire.

**Identity, every canvas on life 2's tape (17,768 of them), oracle vs `retina_fast`:**
```
TOTAL canvases checked: 17768
saliency byte-identical on all 17768: True
first differing seq: None
max |delta| over all canvases: 0.0
fixation mismatches: 0 / 17768
```
Byte-exact on every one, never loosened to a tolerance. Fixations (via `organs/gaze.py`'s unmodified `gaze_sequence`, called directly on the fast analysis) match exactly wherever saliency does — checked directly, not merely inferred. The tower's 112-vectors are cut from `luminance(rgb)`, never from the retina's channels, so byte-identical saliency/fixations already implies byte-identical 112-vectors; asserted anyway in `tests/genome/test_retina_fast.py`.

**Timing:**
- Solo per-call median, first 200 canvases: OLD 5.20 ms, FAST 1.21 ms — **4.29×**
- Aggregate over all 17,768 canvases (includes PNG decode + fixation recompute in the harness): OLD 6.44 ms/canvas, FAST 1.57 ms/canvas — **4.12×**

Lower than EYE.md's hoped-for 11.7× (that number priced the whole 8-channel analysis against a different baseline); the honest number, measured, is **≈4.1–4.3×**, still cutting the eye's ≈7.4 ms/canvas share meaningfully (`cell_means` alone: old 4.77 ms → new well under 1 ms).

**The sha-pin road, named.** `genome/gaze.py:PINS` currently pins only `organs/retina.py` and `organs/gaze.py`. Adopting `retina_fast.py` (rewiring `gaze.py`'s `organs()` to call `retina_fast.analyse_fast` instead of the oracle's `analyse`) would add a THIRD pin, `genome/retina_fast.py` → `452602160658d8253c477953476d1d91c7cfbadebc0241ba75abfdd74e343b1d`, alongside the EXISTING `organs/retina.py` pin (kept — `retina_fast.py` still calls the oracle's `channels()`/`saliency()` and checks its own sha independently at import). Not wired in here — this is the orchestrator's decision, matching the brief's "adopting this module is the orchestrator's decision, not made here."

**Negative control** (proves the identity check can fail, not vacuous): a planted 1e-9 corruption on one saliency cell is caught by `np.array_equal` — `tests/genome/test_retina_fast.py::test_negative_control_catches_a_real_divergence`.

---

## 4 · The diff, the tests, and their logs

**Diff (uncommitted, on `g5-repairs`):**
```
 genome/machinery.py | 17 +++++++++++++++--
 1 file changed, 15 insertions(+), 2 deletions(-)
?? genome/retina_fast.py                       (new, 89 lines)
?? tests/genome/test_state_hash_live_block.py  (new, 6 tests)
?? tests/genome/test_retina_fast.py            (new, 4 tests)
```
`genome-wt-k-hist/genome/machinery.py` carries the identical (uncommitted) state_hash edit, applied only for the historical-code replays in §0/§1/§2 — never committed there either.

**The two new suites, on final bytes** (`tests.genome.test_state_hash_live_block tests.genome.test_retina_fast`):
```
Ran 10 tests in 7.675s

OK
```
(6 state_hash tests: the invariant on a toy organism and on life 2's real snapshot, the digest differs from the old one and is deterministic, `Organism.load` refuses a pre-repair snapshot by name, a same-version save/load round-trips. 4 retina_fast tests: random frames, all 11 rendered things with fixation match, a non-uniform w×h grid, the negative control.)

**The full existing suite, on final bytes** (43 modules, `tests/creature` + `tests/genome`, run the way `tools/gate_g4.py` itself invokes tests — `python3 -m unittest <dotted modules>`, not `unittest discover`, which mis-resolves this repo's package layout and is not how this repo's own tooling runs tests):
```
Ran 279 tests in 435.110s

FAILED (failures=4, skipped=1, expected failures=6)
```
The 1 skip and 6 expected-failures are pre-existing (PREREG-bar toys unrelated to this brief). **The 4 failures are exactly, and only, the four tests that pin the OLD state_hash digest** — every one fails with the SAME two digests, `b05315037ff98529836472e6ddd9ebb5a45742b0511f5facf6b73cd754fa1e3f` (got, matching §2(d)'s independently-derived new G4-2 digest) vs `d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86` (the old pin):
- `tests.creature.test_mind_parity.TestGate42MindParity.test_g4_2_parity`
- `tests.creature.test_mind_parity.TestGate42MindParity.test_g4_2_control_swapped_canvas`
- `tests.creature.test_wave2_predict_fast.TestSkeletonHashUnchanged.test_skeleton_pin_unchanged`
- `tests.genome.test_pin_skeleton.TestPinSkeleton.test_hash_dev_unchanged`

No other test regressed. This is the expected, correct shape of a digest-changing repair: every consumer of the OLD pin fails loudly and names the mismatch; nothing was edited to hide it; the pins on master are untouched.

---

## 5 · Raised (not worked around)

1. **Replay-based diagnostics/gates against a closed life must run under the commit that was actually live**, never master HEAD, or they measure a counterfactual (§0). Flagged for whoever next builds a replay-based tool against life 1 or life 2.
2. ~~`Organism.load` refuses every pre-repair snapshot~~ — **resolved, §6**: `load()` now accepts either digest.
3. **Adopting `genome/retina_fast.py` into production** (rewiring `genome/gaze.py`) is a decision, not made here — proven byte-identical and ~4.1–4.3× faster, never wired in.
4. **`edges_log`/`prunes_log` JSON serialisation is now `state_hash`'s dominant cost** (§2(a)) — noted for whoever looks at this function next; out of scope here ("the counters as now").

---

## 6 (added 2026-09-21 17:46 +0400) · `Organism.load` accepts EITHER digest — the orchestrator's follow-up task (commit 412d721)

**The ask:** the closed lives' readers (`tools/verdict_g4.py`'s W3-2 reach control, the exam) must still LOAD old-format snapshots (saved under the pre-repair, full-array `state_hash`) — §2's refusal, while correct behaviour for a changed digest, blocked every reader that opens a real closed life predating this repair.

**The fix.** `Organism.state_hash()` (the live-block hash, §2) is untouched — every NEW `save()` still writes it, every live/replay path still reads it. A new method `Organism._state_hash_legacy()` is a byte-for-byte copy of the PRE-REPAIR `state_hash` body (the full `nmax × nmax` arrays), kept verbatim, called from nowhere except `load()`'s fallback. `Organism.load()` now: computes the new hash first; on mismatch, computes the legacy hash and accepts if THAT matches; raises `GenomeError` (naming both computed digests and the saved one) only when neither matches.

**Verified, read-only, on the real snapshots the ask named:**
```
life2:  load() OK, sight.n=700 words.n=17 t=78872
        new hash=8472af1850b77e2a  legacy hash=07498bf839b9d090  saved=07498bf839b9d090
life3a: load() OK, sight.n=1113 words.n=23 t=10352
        new hash=bc57f150c6948e67  legacy hash=52a804ebb7474271  saved=52a804ebb7474271
```
Both load via the legacy fallback (the saved digest matches `_state_hash_legacy()`, not `state_hash()` — exactly the pre-repair snapshots they are); no write was needed to read them.

**The test** (`tests/genome/test_state_hash_live_block.py::TestLoadAcceptsEitherDigest`, on `_build_toy_organism()`, a small real organism, plus the two real snapshots above): five cases, the three the orchestrator asked for plus two real-snapshot controls —
1. `test_new_format_snapshot_loads` — a snapshot saved by the current code loads (fast path, no fallback).
2. `test_legacy_format_snapshot_loads` — a snapshot whose saved digest is the LEGACY one (built by overwriting the `.json`'s `state_hash` field with `_state_hash_legacy()`'s value — the exact shape every real pre-repair snapshot has) loads via the fallback.
3. `test_corrupted_snapshot_refuses_under_both` — one entry of `sight_cells` flipped after save (the toy's 40 canvases never reach `stage2_start`, so `W`/`mask`/`strikes` are genuinely all-zero and corrupting them would prove nothing here; `sight_cells` is hashed identically by both digests, so corrupting it breaks both just as surely) — `load()` still raises `GenomeError`, naming the digest it could not match either way.
4. `test_real_life2_snapshot_now_loads` / 5. `test_real_life3a_snapshot_now_loads` — the real thing, read-only, both asserting the loaded organism's `_state_hash_legacy()` equals the saved digest (the control proving these are genuinely legacy-format snapshots, not a vacuous pass).

The file's original `test_real_life2_snapshot_refuses` (§2's now-superseded behaviour) is replaced, not left contradicting the new code — noted in the class docstring, with the date and reason.

**`tests/genome` on final bytes** (20 modules, same `python3 -m unittest <dotted modules>` convention `tools/gate_g4.py` itself uses):
```
Ran 149 tests in 98.836s

FAILED (failures=1, skipped=1, expected failures=6)
```
The 1 skip and 6 expected-failures are the same pre-existing, unrelated ones §4's 279-test full-suite run already carried. **The one failure is `tests.genome.test_pin_skeleton.TestPinSkeleton.test_hash_dev_unchanged`** — the same OLD-pin mismatch as before (`b0531503…` vs `d4b5c6b8…`), unaffected by this task, still correctly failing. The other three OLD-pin tests (`test_mind_parity` ×2, `test_wave2_predict_fast`) live under `tests/creature`, outside this run's scope; unaffected by this change, still failing the same way — not re-run here (this task's ask was `tests/genome`), but nothing in this diff touches them. No test regressed that wasn't already failing before this task.

**Committed** on branch `g5-repairs` (this worktree): `genome/machinery.py` (`_state_hash_legacy` + `load()`'s two-digest fallback) and `tests/genome/test_state_hash_live_block.py` (the superseded test replaced, the five-case class added). Nothing touched on master, `/data/dev/genome`, or any pin.
