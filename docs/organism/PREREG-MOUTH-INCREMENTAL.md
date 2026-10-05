# PREREG-MOUTH-INCREMENTAL — the mouth the human way: build the phrase word by word, stop when the listener can pick the thing out

*Law before code (RULES law 1). Author: Kimi K3 (kimi-code, acting seat). Signed: alone — Ahmad's word of 2026-10-05 («Only you have to work. No extra helper or anything»). Ordered by his word of the same day ~15:20 (memory `feedback_2026-10-05_human_mechanism_never_cheat.md`): reverse-engineer the ACTUAL human mechanism and implement THAT at machine level — and never cheat.*

## 0 · Read first

1. **The research** `docs/brain/mouth/RESEARCH-HUMAN-MOUTH-MECHANISM.md` (this branch) WHOLE — the human mechanism as the evidence has it (Dale & Reiter 1995 read whole through §3; Hawkins et al. on useful redundancy; Yassa & Stark on the memory loop; every source's read-status flagged there), and the part-by-part map to our organs: the ear's order is the salience order; the read-back is the hearer model; the believed map is the discriminatory-power filter; the budget is the bail-out.
2. **The incident and the cap** — PREREG-MOUTH-CAP + AMENDMENTS 1–3 (this branch, signed): the enumeration cliff (321,719 read-backs on one canvas, the replay killed), the two-branch bound (MOUTH_BUDGET 4,096, MOUTH_FULL_BELOW 12), the identity gates (M-TAPE-FULL PASS; M-TAPE-BL2 armed at drafting). **This law supersedes nothing of it:** the cap is the bail-out underneath the mechanism; `produce_believed` stays byte-exact what the cap's gates prove.
3. The turn's call (`genome/brain.py:_turn_core`): `produce_believed(road, X, h, rng_factory)`; the journaled say dict's six keys; the tie generator `substream(world_seed, "turn-say:<scene>:<h>")` built FRESH per candidate — **every read-back of one canvas sees the same stream from position 0**, so a read-back's outcome depends on the phrase and never on how many read-backs ran before it (the cap law's item 4, re-verified by reading 2026-10-05).

## 1 · The question, what a pass settles, what it cannot

**The question.** Can the mouth build its phrase the human way — walk the ear-ordered sayable words ONCE, skip a word that rules out nothing, add a word, and ask the hearer model after each addition «can you pick it out now?», stopping at the first YES — so that the 2^N enumeration exists NOWHERE, the worst canvas costs len(say) read-backs, and the bail-out stays honest?

**A pass settles:** (i) the incremental form implements the documented human mechanism line for line (the fixtures from the literature computed by hand); (ii) the old mouth is untouched (additive function, the record's bytes unmoved by construction, the cap's gates un-reopened); (iii) the cost claim — ≤ len(say) read-backs ALWAYS, pinned on every corpus fixture; (iv) the first honest measurement of how differently the two mouths speak on a real tape (R-DIFF over brain-long-2's 50,000 canvases, no bar — the rung decision's planning basis).

**It cannot settle (each said now):** that a LIFE should speak incrementally (the rung's own law, with a genome clause and a pinned window — the R-DIFF reading is its planning input, never its gate); that the incremental mouth is «better» (it is the human mechanism; «better» is not a claim this bench makes — the phrases CAN differ, the way *the white bird* differs from *the bird*, and that difference is the mechanism, not noise); any improvement toward Full Brevity (NP-hard and non-human — FORBIDDEN by design, §7).

## 2 · The build (additive — nothing existing moves)

`brain/scene/learners.py` gains `produce_incremental(road, X, target, rng_factory, budget=MOUTH_BUDGET)` — the human mechanism, line by line (the pin gate: `git diff --stat` over everything except {`brain/scene/learners.py`, `tests/brain/scene/test_learners_mouth_incremental.py`, `tools/brain/mouth_diff.py`, `tests/tools/test_mouth_diff.py`, `docs/`} is EMPTY):

1. **The walk:** `say` computed EXACTLY as `produce_believed` computes it (the same believed map, the same sayable rule — the preference order is the road's type order, the ear inside it).
2. **The Relevance skip (free, no read-back):** a word every other hypothesis believes the same name for (in its type) rules out nothing — skipped, counted in `skipped`.
3. **The increment:** add the word; ONE read-back of the phrase so far (the hearer model, the tie generator per candidate as the turn builds it); if the read-back points at the target first and «none» does not fire → **STOP: speak** (the phrase in the ear's order, as everywhere).
4. **Indelibility (the white-bird law):** a word once added is never removed, whatever later words could do alone — pinned by M-INDELIBLE.
5. **The bail-out:** the list exhausted without sufficiency → `spoken None`, `reason "the read-back"` (the old reason string's own family — «I cannot say it yet»); the budget of the cap law bounds the read-backs a second time (`≤ len(say)` is the mechanism's own bound; the budget is the belt under the braces), its breach → `reason "the mouth's budget"` (the cap's declared string, verbatim).
6. **The row** carries the old keys (`target`, `believed`, `sayable`, `spoken`, `reason`, `readback_point`, `margin`) plus the mechanism's own: `n_say`, `n_readbacks` (ALWAYS ≤ len(say) — M-COST's pin), `skipped` (the powerless words), `added` (the walked words). The margin is computed at the stopping read-back as everywhere (a READING, the field keeps its meaning).
7. **The instrument** `tools/brain/mouth_diff.py`: replays a closed tape with `produce_believed` monkeypatched by a dispatcher that computes BOTH mouths on the turn's own (road, X, h, rng_factory) — the turn still speaks the OLD mouth (the journal is byte-identical to the plain replay, G-DUAL's proof) — and writes one side row per said canvas: {seq, scene, old phrase, new phrase, equal, lengths, n_readbacks each}.

## 3 · The gates (instrument)

| gate | asserts | read on |
|---|---|---|
| **G-EQUIV2** | the reference implementation in the test file is lifted from §2's text (the twin-implementation form); the literature fixtures' expected phrases are computed BY HAND and quoted beside the test | once |
| **G-DUAL** | the dispatcher's replay journal is byte-identical to the plain replay's on a 2,000-canvas prefix of brain-long-2 (the instrument observes, never interferes); a planted one-word flip in the side file is CAUGHT by its reader | once |
| **G-SUITES** | the five suites on the build sha (the cap law's G-SUITES form, verbatim: brain with exactly the 16 named torch errors; creature in three parts, partition exact) | the build sha |

## 4 · The marks

| # | mark | what is read | plant (must be CAUGHT) | bar |
|---|---|---|---|---|
| **M-INCREMENT** | the corpus (≥ 200 fixtures incl. the literature's own: D&R §2.2's dog/cat contrast set, mapped to our kinds; the seven-cups set of D&R §3.1.2) vs the twin implementation | a fixture whose expected phrase is mis-computed by hand ON PURPOSE (the test must catch the hand, not the code — #246 (1)'s form: the instrument is graded too) | **every fixture's phrase/reason/readback_point equal** |
| **M-INDELIBLE** | the white-bird pin: the ear's first word discriminates but does not suffice; a later word alone would | an «optimized» variant that drops the early word — must FAIL this mark | **the output KEEPS the early word (length 2), so no future edit can sneak Full Brevity back** |
| **M-SKIP** | the Relevance skip: a word all hypotheses believe alike is never said, costs no read-back | a fixture counting its read-backs — the skipped word must not consume one | **the skipped word absent from `added`, present in `skipped`, `n_readbacks` excluding it** |
| **M-BAIL** | the list exhausted with the read-back never sufficient | — | **`spoken None`, `reason "the read-back"`; the budget breach → `reason "the mouth's budget"` (say = budget + 1, every word relevant)** |
| **M-COST** | `n_readbacks ≤ len(say)` on EVERY corpus fixture and every R-DIFF canvas | — | **holds everywhere, no exception counted** |
| **R-DIFF** (a reading, NO BAR) | over brain-long-2's 50,000 canvases: the share of said canvases where the two mouths differ; the length distributions; the differing rows' examples printed; the n_readbacks profile of both | the G-DUAL plant | the figures printed with their presence counts (said canvases n of n, the old mouth's say rows as the denominator — #168's form) |

## 5 · The verdict rule (TOTAL and ORDERED)

| # | the marks read (in this order) | verdict |
|---|---|---|
| 1 | an instrument gate fails (G-EQUIV2, G-DUAL, G-SUITES) or M-INCREMENT fails | **VOID** — the build's or the instrument's result; an AMENDMENT names the cause |
| 2 | M-INDELIBLE, M-SKIP, M-BAIL or M-COST fails | **FAIL-MECHANISM** — the build is not the mechanism the research documents; diagnosed to its cause and re-built under an AMENDMENT, never loosened |
| 3 | every gate and mark holds, R-DIFF printed | **PASS** — the human-form mouth exists beside the old, measured on the real tape; the RUNG's law (a `mouth` genome clause, a pinned window, a life) may be written with R-DIFF as its planning input |

## 6 · The price (each from a named measurement) and the stop rules

- The corpus: < 5 CPU-min. The G-DUAL prefix replay: 2,000 canvases ≈ 10 CPU-min (the OFF replay's measured rate), SLOT_MEM 2G. **The R-DIFF replay: ≈ 8 CPU-h at SLOT_MEM 8G** (the OFF reference's own shape), run AFTER the cap law's M-TAPE-BL2 completes (sequence, never contention — the box holds bl4 ~10 GB + one 8G replay + suites).
- The suites: the cap law's §6 figures (creature ×3 at 10G ≈ 90 min wall).
- **Stop rules:** S1 price (2 × the clause → STOP, re-price); S2 memory (a replay peak > 6,000 MB → STOP); S3 instrument (any gate/mark failure → STOP; a buggy build fixed and re-run, never routed around); S4 clause (unimplementable → RAISE); S5 load (a graded job started above 1.5 × the quiet load re-timed alone).

## 7 · The adversarial walk (each answered before signature)

1. *«Just make it faster»* — NO: the mechanism is the point (his word). The incremental form is the documented human mechanism; a tuned-down enumeration would be the cheat he forbade.
2. *The phrases can differ from the old mouth's* — declared as the mechanism (the white bird), never hidden: the old mouth stays the record's mouth until a RUNG carries the advancement, and R-DIFF measures the difference first, with presence counts, no bar.
3. *The rng streams*: every read-back of a canvas sees the same fresh same-seed stream (§0 item 3) — the incremental mouth's fewer read-backs cannot shift a read-back's outcome. Pinned by a corpus fixture where the two mouths' read-back counts differ (they do) and the shared prefix's outcomes are equal.
4. *A word that flips the read-back AWAY from the target*: keep walking (the human keeps talking; indelibility), bail at exhaustion. Pinned by a corpus fixture.
5. *`margin` under no competition*: computed at the stopping read-back (the field's old meaning, a reading).
6. *The budget «second bound»*: len(say) CAN exceed MOUTH_BUDGET (mentor scale 26 < 4,096 — the mechanism's own bound binds first, always; the budget breach needs say > 4,096 — named as unreachable on any measured stream, kept for the form).
7. *The dispatcher's purity*: it computes, never substitutes (the turn speaks the OLD mouth in the R-DIFF replay — G-DUAL proves byte-identity); the side file is the only output.
8. *The twin implementation could share my blind spot*: the literature fixtures are computed by hand FROM THE PAPERS (D&R §2.2, §3.1.2's worked examples, mapped word-for-kind), and M-INCREMENT's plant grades the hand.

**NOT done by this law:** no life, no genome line, no pinned-file edit (no window owed); `produce_believed` untouched (the cap's gates stand un-reopened); the mentor templates frozen v1; nothing under `/data/dev/genome-lives/` touched (replays read copies).

Signed: **Kimi K3 (kimi-code, author and acting seat, alone — Ahmad's words of 2026-10-05)**, 2026-10-05 17:39 +0400 (from `date` at signing), on this file's sha256 carried by `docs/organism/records/mouth-cap/SEAT-LINE-INC.txt` beside it.
