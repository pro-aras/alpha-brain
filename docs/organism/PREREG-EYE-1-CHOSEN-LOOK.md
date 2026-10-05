# PREREG-EYE-1 — THE CHOSEN LOOK: the loop's return arrow (the brain's doubt steers the eye)

*Law before code (RULES law 1). Author: Kimi K3 (kimi-code, acting seat). Signed: alone — Ahmad's word of 2026-10-05 («Only you have to work. No extra helper or anything»). Ordered by his evening order of the same day: the eyes, deep research, then build — «work as per human working mechanism», and never cheat.*

## 0 · Read first

1. **The research** `docs/brain/eye/RESEARCH-HUMAN-EYE-MECHANISM.md` (genome master) WHOLE — the human visual loop (retina sends errors; V1's filters are LEARNED; feedback = predictions, feedforward = errors; **attention is the error-guided act: predict → look where the error is expected → update → repeat** (Rao & Ballard 1999, Rao 1998, read whole in the review); saliency WTA+IOR (Itti & Koch 1998)); the gap map: **the loop's return arrow is MISSING — the residual is computed and filed, and steers nothing** («NEVER forwarded into gaze_sequence», `genome/gaze.py:6-8`; no look-again anywhere in creature code, grep 2026-10-05), and the forced road (`brain/scene/eye.py:forced_glance`, `:120-135`) is built, pinned at fixation cells by `tests/brain/scene/test_eye.py`, and unused by any loop.
2. **The 09-29 bench (the record, not a toy):** DIAG-LOOK-AGAIN — at four fixations the eye sees the parent's named thing on **0.89–0.90** of canvases (the 0.234–0.249 unseen base rate, the same construction); ONE more look at the right place takes it to **0.98–0.99** on that bench. The anchors are quoted, never re-derived here.
3. **The turn's own doubt** (`genome/brain.py:_turn_core`): `order` (the hypotheses, most-fixated first), `held` per hypothesis; a hypothesis with `held == []` is what the organism's ASK condition already reads — the brain's B7 doubt, computed every canvas, read-only.
4. **The loop in the live creature:** `_consume_eye` computes the glance dict `g` once per canvas (cells and brain share it); `_brain_canvas` runs the turn BEFORE the learn (`creature/mind.py:1644-1690`, the DRIVE order). The turn is READ-ONLY (no call writes the learner — pinned by the state hash, `tests/genome/test_brain_turn.py`).
5. **The pinned files:** `genome/gaze.py` and `genome/machinery.py` are in `cache.WORLD_CODE` (the 12-file list, read 2026-10-05) — **this law touches neither** (no window owed); every mechanism lands in `creature/mind.py`, `brain/scene/eye.py` (both unpinned), `tests/`, `tools/`, `docs/` (the pin gate: `git diff --stat` empty elsewhere).

## 1 · The question, what a pass settles, what it cannot

**The question.** Can the organism do the human loop's return arrow — when its leading hypothesis holds no word (its own doubt), LOOK AGAIN at exactly that thing before it learns — so that the named-thing-seen rate on the real tape rises toward the bench's 0.98–0.99, at a priced cost of at most ONE extra glance a canvas, with every unfired canvas byte-identical to today?

**A pass settles:** (i) the mechanism is the human form (doubt → a directed look at the doubted thing → re-read → then learn/ask); (ii) the unit pins: it fires only on the doubt, at the doubt's locus, at most once a canvas, and re-feeds the brain's eye row before the turn's re-read; (iii) R-LOOK over brain-long-2's 50,000 canvases (a dual replay — the instrument only observes the master journal beside it): the fire rate, the named-thing-seen rate against the 0.89 anchor, the says that change, the canvas cost, and the confinement (every journal difference traceable to a fired canvas or its downstream); (iv) nothing else moves (G-SUITES, the pin gate).

**It cannot settle (each said now):** that a LIFE should live this way (the rung's own law — R-LOOK is its planning input, never its gate); that 0.98–0.99 transfers from the 09-29 bench (R-LOOK measures the real transfer, with the anchor printed — a shortfall is a READING and §5's walk item 1, never a re-tune); a learned eye front (E2's own law); the cells' own seeing (the chosen look re-feeds the BRAIN's eye row; the cell organism's seeing of the canvas is untouched — named, never silently shared).

## 2 · The build (the human loop, one arrow)

1. **The doubt:** after the turn, the leading hypothesis `order[0]` with `held == []` (the turn's own ask condition — no new condition invented).
2. **The look:** ONE `forced_glance` at that hypothesis's locus (its `pos` — the members' mean cell, `brain/scene/eye.py:67-68`, through `cell_centre_px`'s own form), with the same spec/gaze/colour of the canvas's own eye call.
3. **The re-feed:** the leading hypothesis's feature is recomputed from its members' glances WITH the forced glance appended to its members' pool (the same unit-mean rule, `brain/scene/eye.py:hypotheses`) — the eye row the brain re-reads.
4. **The re-read:** the turn is re-run on the re-fed view (the same read-only turn — its determinism holds: same code, new input); the journaled turn row gains the look's own sub-record `{looked: true, at: [y, x], held_before: [], held_after: [...]}` (additive keys; the row's old keys unmoved) — **and only then does the learn run, on the re-read state** (the human order: look closer FIRST, ask/learn after).
5. **The cap:** at most ONE chosen look per canvas (priced; a second doubt the same canvas is the ASK's business, not the eye's). The coarse glance and the cells' road are untouched.
6. **The instrument** `tools/brain/look_diff.py`: replays a closed tape under the E1 code with a journal tee — the master journal computed BESIDE it (the mouth_diff form, G-DUAL's proof reused) — and writes one side row per fired look {seq, scene, at, held_before, held_after, said_old, said_new} beside the run's own journal.

## 3 · The gates (instrument)

| gate | asserts | read on |
|---|---|---|
| **G-LOOK-UNIT** | the unit fixtures: fires exactly on `held == []` at the locus, never when a word is held; the feature re-feed changes the turn's held when the bench says it should; the turn's state-hash pin holds around BOTH turns (read-only) | the build |
| **G-DUAL-LOOK** | the tee journal of a 2,000-canvas prefix is byte-identical to the plain E1 replay's journal (the instrument observes, never interferes); a planted side-row flip is CAUGHT | the build |
| **G-SUITES** | the five suites on the build sha (the mouth law's form: brain with exactly the 16 named torch errors; creature in three parts, partition exact) | the build sha |
| **G-PURE** | the pin gate: no WORLD_CODE file in the diff; no new imports outside the allow-list of `tests/brain/scene/test_truth_fence.py` | the build sha |

## 4 · The marks

| # | mark | what is read | plant | bar |
|---|---|---|---|---|
| **M-FIRE** | the fire rule over the unit corpus: fires iff leading held == []; at most once a canvas; at the doubt's locus (the forced window's centre within one cell of the hypothesis's `pos`) | a fixture with the doubt on the SECOND hypothesis: the look must land THERE, not on the leader | **every fixture exact** |
| **M-SEEN** (the bench's own measure, moved to the real tape) | over R-LOOK's said canvases carrying a parent-named thing: the share whose named thing the brain HOLDS, E1 vs the master journal's same measure, per seed-window, with presence counts | the named-thing population printed (n of n — never a silent zero) | **E1 ≥ master on every window of ≥ 200 such canvases, AND the master reads within 0.03 of the 0.89 anchor (the instrument's own sanity — #162's form: a measure far from its anchor is an instrument fault, named)** |
| **M-COST** | the added canvas cost of R-LOOK (the forced glance's measured ms × the fire rate, CPU per canvas, against the turn's own measured cost) | the fire rate printed | **≤ 1.5 × the turn's own cost, and never a second look** |
| **M-CONFINE** | every journal difference of the R-LOOK replay vs master is at a fired canvas or downstream of one (the W2 I2 profile's form: a diff reader asserts the first OTHER difference is None) | a planted off-doubt journal flip: CAUGHT by the diff reader | **first other difference None** |
| **R-LOOK** (readings, no bar) | the fire rate; the says that change after a look (the two mouths' forms printed); the holds gained (held_before/after per fired canvas); the 0.98–0.99 bench figure printed beside the real transfer | — | printed with presence counts |

## 5 · The verdict rule (TOTAL and ORDERED)

| # | the marks read (in this order) | verdict |
|---|---|---|
| 1 | an instrument gate fails (G-LOOK-UNIT, G-DUAL-LOOK, G-SUITES, G-PURE) or M-CONFINE fails | **VOID** — the build's or the instrument's result; an AMENDMENT names the cause |
| 2 | M-SEEN fails (the chosen look does not raise the seen rate on the real tape, or the master's anchor check fails) | **FAIL-TRANSFER** — the 09-29 bench's number was a bench's, not the life's: the research map's walk item 1 lands; the loop stays open by evidence, E1 is refused, and the failure is reported as the result |
| 3 | M-COST fails | **FAIL-COST** — the form is re-priced in a NEW law, never shipped silent |
| 4 | M-FIRE, M-SEEN, M-COST, M-CONFINE all hold, R-LOOK printed | **PASS** — the loop's return arrow exists and is measured; the RUNG's law (a `look` genome clause, a pinned window, a life) may be written with R-LOOK as its planning input |

## 6 · The price and the stop rules

- The unit corpus: < 5 CPU-min. The prefix dual replay (2,000 canvases): ≈ 10 CPU-min at 2G. **The R-LOOK replay: ≈ 8–10 CPU-h at SLOT_MEM 8G**, sequenced onto the measured box (at most two 8G jobs beside bl4 — the AMENDMENT-2-of-the-mouth-law's measured form; the queue behind M-TAPE-BL2 and R-DIFF, posted on the board).
- The suites: the mouth law's §6 figures.
- **Stop rules:** S1 price (2 × the clause → STOP); S2 memory (a replay peak > 6,000 MB → STOP); S3 instrument (any gate/mark failure → STOP; a buggy build fixed and re-run, never routed around); S4 clause (unimplementable → RAISE); S5 load (a graded job above 1.5 × the quiet load re-timed alone).

## 7 · The adversarial walk (each answered before signature)

1. *The bench's 0.98–0.99 was a bench's.* Said in §1 and given its own verdict row (row 2): the real transfer is M-SEEN's measurement with the anchor check beside it; a shortfall is a result, never a re-tune.
2. *The re-feed changes what the learner learns — a downstream avalanche.* That is the mechanism (the look is FOR learning). M-CONFINE bounds it to fired canvases + downstream; R-LOOK prints the says that change.
3. *A doubt that never resolves* (the forced glance changes nothing): the cap is ONE look a canvas; the ASK road then does its own work; pinned by a fixture.
4. *The cells' seeing silently shared:* the chosen look re-feeds the BRAIN's eye row only; the cells' episodes of the canvas are written before it and untouched (the DRIVE order, §0 item 4) — G-LOOK-UNIT's fixture asserts the cell road's rows unmoved.
5. *The turn is no longer deterministic per canvas:* it is deterministic per (canvas, look) — the look is a pure function of the tape and the turn's own output (no clock, no set order — the substream rule); the replay identity of UNFIRED canvases holds byte-for-byte (M-CONFINE's zero-difference half).
6. *The look could fire on a canvas the brain does not hear* (an ask held, a maker row): the doubt is read after the turn, which only runs on heard canvases — scoped by construction.
7. *`forced_glance` at a locus near the rim:* its own clamp handles it (the byte-pinned form); a rim fixture.

**NOT done by this law:** no life, no genome line, no WORLD_CODE file, no window owed; the mentor templates frozen v1; nothing under `/data/dev/genome-lives/` touched (replays read copies); the cells' seeing untouched; E2/E3/E4 deferred to their own laws.

Signed: **Kimi K3 (kimi-code, author and acting seat, alone — Ahmad's words of 2026-10-05)**, 2026-10-05 23:16 +0400 (from `date` at signing), on this file's sha256 carried by `docs/organism/records/mouth-cap/SEAT-LINE-EYE1.txt` beside it.
