# PREREG-CONTENT-WEB (F1) — the amodal knowledge web: every sense feeds knowledge, content nodes beside word nodes

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-10 13:27 +0400 — authored under Ahmad's 10-10
words: «Ok go ahead» on the fix road + «go on and test everything one by one when you build so we can
have a verified pure road», on the research of record docs/brain/RESEARCH-ANY-INPUT-KNOWLEDGE-AND-THOUGHT.md
(master 87770db): the human knowledge layer is AMODAL — content, not channel (the rewired ferret; the
blind occipital cortex reading language; Makin's bound carried). Alpha's knowledge layer today is
EAR-BOUND by construction, measured 2026-10-10 06:4x on the live life's own code: the webs hear ONLY
`sense == "ear"` rows (creature/mind.py:1013–1024); a chat-taught word can never enter the web (the
00:32 round's finding, the board's NOTE of 06:4x).

## §0 · The gap, named against the code

`Mind.consume` dispatches 14 senses; exactly ONE feeds the knowledge webs (`_web_hear`, ear words only).
The tape already carries every channel (eye/scene/maker/video/game/folder/chat/ask/touch/smell/…). The
web's arithmetic (genome/web.py) is already content-agnostic: nodes are strings, pair events,
consolidation by c/occ/Poisson-over-expectation, decay, sprouts. THE GAP IS THE FEED, not the math.
This law widens the feed and ONLY the feed — behind a flag — and measures the crossing.

What this law is NOT (scope, said plainly): not a re-foundation of representation (that is N7's road);
not a change to the word road's ledger/episodes (they stand); not a change to web.py's arithmetic
(untouched); not a genome line (a Mind construction flag, the N1/CONTEMPLATE-1 form); never a live-life
edit — a bench law first, as every law here.

## §1 · The mechanism (machine form; every constant declared BEFORE any reading)

New, behind `Mind(..., content_web: bool = False)` (default OFF = byte-identical: the webs hear ear
rows only, exactly as today — the N1 wiring form; no genome/parser/machinery.py edit; nothing
persisted beyond the web's own existing state).

**The content tokens.** Under the flag, every consumed row contributes ITS OWN tokens to
`_web_hear` (one call per token, the ear's own cadence — the web's arithmetic never learns the
difference):

- `ear` (and every word-carrying row — the folder's read words, the video captions, which already
  arrive as ear rows): unchanged, `w:<word>` — under ON the node keys gain the `w:` prefix by
  construction; OFF they stay bare (byte-identity).
- `eye` (scene/maker/video canvases — the SIGHT channel): for each hypothesis `h` in the glance, one
  content token `s:<sig>` where `sig` = the blake2b-32 hash of the organism's OWN feature row `X[h]`
  quantized per component at a DECLARED width of 0.05 — `X[h]` is the hypothesis's `feat`, a
  UNIT-normalized 144-vector (brain/scene/eye.py:106 `v = _unit(...)`; machinery.py's `_unit` divides
  by the L2 norm), so components live in [−1, 1] and concentrate in ≈ [−0.3, 0.3]: the 0.05 width is
  the machine-form constant, fixed here from the code's own normalization, NEVER fitted. THE TOKEN IS
  AMODAL BY CONSTRUCTION: it names the organism's read of the content, never a word; the same content
  re-seen maps to the same token (deterministic), and no word is needed for a thing to be known.
- `chat` / `ask` (the doors — this morning's closed door, opened): the consumed sentence's words as
  `w:<word>` — the SAME vocabulary as the ear (the human form: read text and heard speech land in one
  lexicon). The composer/answer path is untouched; only the web hears them now.
- `outcome` (the game channel): `g:<kind>:<got>` — the event kind + its reward sign, declared from the
  row's own keys.
- Senses not listed (touch/smell/sound/sit/hold/grade/proposal/web/body): NO tokens in v1 — named,
  never silently skipped; a later law prices each.

**The co-occurrence is the mechanism.** The web's own arithmetic then does what it already does for
words: a seen thing's `s:` token and its heard name `w:circle` co-occur within the d-window → an edge;
evidence on spaced occasions → consolidation (the same Poisson tail, unchanged). Cross-channel
grounding becomes a measurable web fact, never a new mechanism. **The feed order (declared):** tokens
feed in TAPE ORDER — the rows as consumed; within an eye row, the hypotheses in the glance's own
order; an ear row feeds its word exactly where it feeds today. The pairing geometry is walked, not
hoped: the web's window is d = 3 DISTINCT tokens back, so a one-word naming after ≤ 2 hypotheses pairs
the name with BOTH ([s₁, s₂, w]: w pairs with the previous 3 distinct) — the planted arc names things
with ONE word, and the pilot PRINTS the planted pair's co-occurrence count before the verdict (the
chances ceiling, §6).

**Composition (declared):** with `muse=True` also on, the muse's trigger reads the web exactly as
before (its classes read `w:`-vocabulary words; the content tokens do not alter the self/novel
classes' readings — the trigger's `web.nodes` lookups for a heard word hit `w:` nodes only because
the heard words are tokenized `w:` under the flag — pinned by a G-UNIT row).

## §2 · Gates (instruments first)

- **G-UNIT** — (a) flag OFF byte-identical consume of a scripted mixed-sense stream (journal + web
  state byte-equal); (b) the token forms: a scripted canvas yields exactly its declared `s:` tokens
  (per-hypothesis, deterministic ×2), a chat row yields `w:` words, an outcome row its `g:` token;
  (c) the same content re-seen yields the SAME `s:` token, a different thing a DIFFERENT one (the
  identity/collision check with presence counts); (d) OFF vs ON web-state divergence is EXACTLY the
  new tokens (the ear-only prefix stream is a subsequence — byte-checkable); (e) the muse-composition
  row; (f) determinism ×2 of every web metric.
- **G-IDENTITY** — flag OFF: the N1 gate's own two inputs (the toy tape; the bl2 500-row segment)
  replayed byte-identical master vs branch (the same files, copied into this worktree's scratch).
- **G-PLANT** — (i) a doctored extractor that emits tokens for the EAR channel twice must be CAUGHT by
  the OFF/ON divergence check's accounting (the token census per sense is printed — every «0 of N»
  carries its presence count, #168); (ii) a doctored quantizer that maps everything to ONE bin must be
  caught by G-UNIT(c)'s distinctness check.

## §3 · The bench and the marks (bars written first)

The toy: the muse bench's own world (8 things × 30 rounds on maker canvases + the hearsay ear stream +
the chat door's planted arc), driven ON vs OFF. Plus the PLANTED cross-channel arc of record: a thing
SEEN repeatedly (its `s:` token recurring) whose name is heard ONLY through the chat door (never the
ear — the door-isolation form: the channel crossing is forced to be cross-channel).

- **M-CROSS**: ON reads ≥ 1 consolidated `s:`↔`w:` edge per planted kind (seen+named pairs), printed
  with presence counts (n `s:` tokens, n consolidated edges by kind-pair); OFF reads EXACTLY 0 `s:`
  and `g:` nodes (byte-difference proven, not inferred).
- **M-GROUND** (the human form, the law's core): after the planted arc, the heard-only name's node and
  the seen-only content's node are CONSOLIDATED neighbours (the organism grounded a word it never
  heard from a teacher's naming channel onto content it only saw — the channels crossed); the
  consolidation row's own evidence (c, occ, the Poisson tail value) printed.
- **M-CHAT** (the morning's finding as a regression pin): ON: after the planted chat arc, «alpha» IS
  a node in the web with its edge evidence printed; OFF: absent (the finding reproduced as the
  control).
- **M-STABILITY** (the pilot's reading printed BEFORE the mark binds — #228): the same thing re-seen
  across the bench's own calibration boundary maps to the same `s:` token ≥ a declared share of times
  (bar 16/16 — the quantization is deterministic; the calibration does not touch the eye's features —
  but MEASURED, not assumed; if the eye's own feature row drifts across calibrations, the reading says
  so and the mark reads FAIL-FORM, the instrument's fault, never hidden).
- **M-NULL**: 10 derangement twins (each sense's token stream deranged within itself, moments kept —
  co-occurrence destroyed, marginal rates kept): the planted `s:`↔`w:` edge consolidates in NONE of
  them; the real run's consolidated cross-edge count exceeds the null MAX.
- **M-COST**: per-row process_time overhead ON vs OFF ≤ 5 %, both directions timed (the web hears more
  tokens per row — priced).

## §4 · Verdict forms

**PASS** — all gates + M-CROSS + M-GROUND + M-CHAT + M-STABILITY + M-NULL + M-COST, both plants
caught. **FAIL-FORM** — the content keys churn (M-STABILITY) or the toy cannot ground (instrument
fault, named, an amendment re-prices). **FAIL-MECHANISM** — the web's co-occurrence arithmetic does
not produce the crossing even fed (a result: the consolidation law needs re-thinking for sparse
content channels — named, never loosened). **VOID** — an instrument gate fails.

## §5 · Price

The toy build + ON/OFF arms + the planted arc + the 10-draw null ≤ 45 CPU-min; the identity replays ≤
10 CPU-min; peak ≤ 2 GB (SLOT_MEM=2G — the web grows with content nodes; measured-first, RULES §6d).
Total ≤ 1.5 CPU-h.

## §6 · Adversarial walk

- The token's granularity is the design's one knife-edge: too coarse and distinct things collide
  (G-UNIT(c)'s distinctness check + the planted 8-thing toy's all-pairs collision count printed); too
  fine and nothing recurs (M-STABILITY reads the recurrence). The 0.05 component width is DECLARED
  (the unit-vector form, measured against the code's `_unit`, verifier V1); the collision and
  recurrence readings are printed either way — a bad choice is a RESULT, never tuned post hoc.
- The web's capacity under content tokens: rule N's budget beta scales with known words; the bench
  prints the web's stats (realised/refused/replaced/removed_missed) beside the marks — a silent
  refusal storm would read as «no edges» and is caught by the presence counts, not the edge claim.
- The consolidation's Poisson expectation E uses the node's share of ALL tokens; a rare content token
  beside a frequent word is the asymmetric case the arithmetic already handles (E scales with both
  frequencies) — the planted arc's pair is counted BEFORE the verdict (the ceiling: the expected
  number of chances in the window printed beside the bar, #228 (b)).
- Determinism: the quantizer + hash are byte-deterministic; the web's rng is untouched; replay twice,
  byte-identical (G-UNIT(f) + the bench ×2).
- The muse composition is pinned (§1); the chat door's composer never sees the web change (the fruit
  path reads the store, not the web).
- What this law does NOT claim: that the organism UNDERSTANDS across channels; that `s:` tokens are
  concepts (they are content addresses); that the live life's genome gains anything (a bench law; a
  life-rung law follows only on a PASS and his word). It claims one measurable arc: every armed
  channel feeds the knowledge web, content nodes consolidate beside word nodes, and a name heard only
  through one door grounds onto content only ever seen.

## §7 · Signatures

Author: Kimi Code (K3, kimi-code, the seat alone) — 2026-10-10 13:27 +0400. Verifier loop: the seat's
own adversarial read recorded in `verify/CONTENT-WEB-VERIFIER-READ.md` beside this law before
signing. The seat: SIGNED under Ahmad's 10-10 words; the SEAT-LINE in `SEAT-LINE-CONTENT-WEB.txt`.
