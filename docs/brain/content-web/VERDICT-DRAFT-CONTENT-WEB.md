# VERDICT-DRAFT-CONTENT-WEB (F1) — the builder's reading, gate by gate, mark by mark

edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 15:1x +0400 — written against the law
(docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27, cweb-1010 @ 35ea7e8) on the
final bytes (the records commit 9d42d0e; code unchanged since bc53679). The verdict itself is the
seat's walk; this draft reads every gate and mark against its bar with the numbers, and names every
honest caveat. Every cited output is committed under docs/brain/content-web/records/ (RULES §14).

## The one-paragraph reading

**FAIL-FORM (§4, row 2) — the content keys churn.** The feed is built exactly as the law declares and
every instrument gate is green (G-UNIT 10/10, G-PLANT both plants caught, G-IDENTITY byte-identical to
the journals of record). On the bench, the web's co-occurrence arithmetic demonstrably crosses channels
wherever tokens RECUR (the chat door's word «alpha» consolidates with the ear's «star» c=12/occ=12 and
with the game channel's g:step:+ c=8 — both cross-channel consolidations, both real). But the declared
s: token (blake2b-32 over the 0.05 per-component quantization of the unit 144-vector hypothesis feat)
NEVER recurs across the toy's fresh renders of the same thing: 0/240 cross-render recurrence, 0/16
across the calibration boundaries — and 0/240 collisions (the §6 knife-edge read on both sides: the
width is too FINE, never too coarse). So no s:↔w: edge can gather evidence (the planted pairs' realized
max c = 1 against a chances ceiling of 12) and M-CROSS/M-GROUND/M-STABILITY/M-NULL read FAIL with the
mechanism's own numbers printed. This is the law's anticipated FAIL-FORM row: «the content keys churn
(M-STABILITY) … (instrument fault, named, an amendment re-prices)». The instrument is trusted (both
plants bite and are caught); the failure is the token form's granularity on fresh-rendered canvases,
measured — never tuned, never hidden.

## The gates (§2)

- **G-UNIT — PASS, 10/10 OK** (tests/creature/test_content_web.py; RED on the law commit 35ea7e8: «Ran
  10 tests in 0.901s FAILED (errors=10)», exit 1, scratch/cweb-gunit-red.log — no module, no flag;
  GREEN on the wiring: «Ran 10 tests in 16.462s OK», exit 0, scratch/cweb-gunit-green3.log).
  - (a) flag OFF byte-identical to the no-argument construction over a scripted 58-row mixed-sense
    stream (ear 24, eye 27, outcome 3, ask 1, web 1, grade 1, chat 1): journal bytes equal,
    state/web.json bytes equal (43 473 B), chat/out files byte-equal, the content census untouched.
  - (b) the token forms per sense, exact: 27 canvases yield exactly the law's recomputed s: tokens
    (gaze.glances → things_in_view → 0.05 quantization → blake2b-32, in the glance's own order), the
    ear's 24 words w:-prefixed in tape order, the chat «you are alpha» → w:you/w:are/w:alpha, the ask
    → w:circle, the outcomes → g:step:+ / g:step:- / g:run:none; deterministic ×2 (58 tokens
    identical). The named-absent senses (web/grade) contribute 0 tokens.
  - (c) the same canvas bytes re-seen → the SAME token (s:36061758 both times); a different thing → a
    DIFFERENT one; 0 all-pairs collisions over the fixture's 27 canvases (presence counts printed).
  - (d) OFF-vs-ON divergence EXACTLY the new tokens: the ON ear stream == the OFF stream with the w:
    prefix (byte-checked); the census accounts 58/58 (ear 24, eye 27, chat 3, ask 1, outcome 3); ON
    nodes = 40 = exactly the 8 OFF nodes' w: forms ∪ 4 door-w: ∪ 26 s: ∪ 3 g:; the OFF web carries 0
    s:/g: nodes.
  - (e) the muse-composition row: the trigger's self/novel classes identical on the bare web, the w:
    web, and the w: web carrying content nodes plus a SILENT cross edge («you are alpha» → self,
    «the zog is here» → novel, «the circle is big» → no fire); end-to-end, an ON+muse mind fires the
    chain with BARE anchors [you, are, alpha] and class [self] — the w: mapping lives only at the
    trigger's call site; the question doors never see a prefix.
  - (f) determinism ×2: two ON runs, journal + web.json byte-identical, census identical.
- **G-PLANT — PASS, both plants caught.** (i) The doctored ear extractor (tokens emitted twice) drives
  the ear census to 48 against the OFF stream's 24 and the accounting of (d) raises — caught. (ii) The
  one-bin quantizer collapses distinct things to one token (s:c1349dd5 == s:c1349dd5) and (c)'s
  distinctness check raises — caught. Each plant asserts it changed the bytes first.
- **G-IDENTITY — PASS, byte-identical master vs branch AND to the journals of record.** The N1 gate's
  own script and inputs copied into this worktree's scratch/ (every referenced payload verified
  byte-identical first: 500/500 bl2, 400/400 toy). Toy leg: a728072329aa82bb… master == branch; bl2
  500-row leg: 26dc80c60d4ec173… master == branch — both are exactly the shas of record (N1's and
  CONTEMPLATE-1's records). cmp exit 0 both pairs; slot cweb id-*, SLOT_MEM=2G, peaks 92/92/274/275 MB
  (the ledger's own numbers). records/identity-shas.txt.

## The bench (§3) — tools/brain/content_web_bench.py, the run of record scratch/cweb/bench-run2
(slot cweb bench2, SLOT_MEM=2G, peak 307 MB, 14 s wall — the law §5's caps: 2 GB, 45 CPU-min). The toy:
534 rows, 8 things × 30 rounds, the planted arc 2 × 12 one-word chat rows in the sticky tail window,
30 outcome rows; sleeps 0 (D-sleep); ON web t=535, OFF web t=240. The marks, pilot, twins and the ON
token stream are byte-identical across two runs (modulo the cost timings) — §6's determinism line held.
The pilot was printed BEFORE the marks bind: recurrence 30/30 sightings → 30 distinct tokens per thing
(modal share 1/30), multi-hypothesis sightings 1, distinct s: tokens 240, all-pairs collisions 0,
cross-boundary stability 0/16; the planted pairs' ceiling: 12 namings × 30 sightings, realized max c 1
(35/36 pair edges, all silent).

- **M-CROSS — FAIL.** ON: 0 consolidated s:↔w: edges per planted kind (bar ≥ 1; presence counts: 30
  distinct s: tokens per thing, 12 namings). OFF: EXACTLY 0 s:/g: nodes — PASS half, byte-proven (OFF
  web.json contains 0 `"s:` / `"g:` keys; ON contains 2929 / 138).
- **M-GROUND — FAIL.** The heard-only name never grounds onto the seen-only content: the best alpha
  pair (s:990ab2cf, w:alpha) reads c=1, occ=1, E=0.0531, Poisson tail 0.0517 (≫ α), state silent; zeta
  likewise (c=1, E=0.0548, tail 0.0534). The chances ceiling was printed first: 12 possible pair
  events, 1 realized — the token's churn, not the arithmetic, starves the edge.
- **M-CHAT — PASS.** ON: w:alpha IS a node, with its edge evidence printed — including TWO consolidated
  cross-channel edges: w:alpha↔w:star (c=12, occ=12 — the chat word grounded onto the thing's EAR name)
  and g:step:+↔w:alpha (c=8 — the chat word crossing the GAME channel). OFF: alpha absent (the 00:32
  finding reproduced as the control). This mark is the law's regression pin and it holds.
- **M-STABILITY — FAIL: 0/16.** The pilot's recurrence reading (printed first): no thing's fresh render
  ever reproduces its token (0/240 cross-render recurrence; the calibration boundaries are innocent —
  the eye's features are a pure function of the canvas bytes, predicted never touches fixation
  selection; the churn is the toy's per-occurrence render jitter against a 144-component quantization
  at 0.05). The bar's own parenthetical («the quantization is deterministic; the calibration does not
  touch the eye's features») is confirmed; the premise that the same thing re-seen maps to the same
  token is REFUTED on this toy world.
- **M-NULL — FAIL (as a consequence of the churn).** The twins' half HELD: the planted edge
  consolidates in NONE of the 10 derangement twins (10 × False), and every twin reads 0 consolidated
  cross edges. The real run's consolidated cross-edge count is 0, so «real exceeds the null MAX» reads
  0 > 0 — False. A FAIL of the bar's second clause only, and it fails because the real run has nothing
  the null could be beaten by.
- **M-COST — PASS.** ON 6.19 s vs OFF 5.96 s process time over 534 rows = +3.9 % (run 1); +2.3 % (run
  2). Bar ≤ 5 %. The web hears 535 tokens ON vs 240 OFF — priced.

## Honest readings and named caveats (nothing hidden)

1. **What actually failed and what did not.** The web's arithmetic crossed channels wherever tokens
   recur: w:↔w: (alpha↔star, c=12) and g:↔w: (g:step:+↔alpha, c=8) consolidated — cross-channel
   consolidation is real and reachable under the unchanged arithmetic. The failure is exactly and only
   the s: token's granularity: at 0.05 per component of the unit 144-vector, the maker world's
   per-occurrence jitter (position ±3 px, scale 0.8–1.2, rotation ±15°, noise σ 0.05,
   genome/world.py:123-136) never reproduces a quantized signature. Collisions are 0/240 — the width
   sits on the knife-edge's FINE side. An amendment road (the SEAT's call, never built here): re-price
   the token form (a coarser declared width, or a posture-tolerant feature) OR re-price the toy (the
   same canvases cycled — which would make M-STABILITY a pure calibration-invariance check, its
   parenthetical's own reading). Per the law, a bad choice is a RESULT; it was measured, not tuned.
2. **The muse composition is pinned at the trigger, and ONLY there** (the law §1's own scope). Under
   ON, the chain's WALK (creature/inner.py's candidates over the w:-vocabulary web) is handed the bare
   `said`/`mature` sets by the pre-existing machinery — it finds no candidates and the chain rests
   after its anchors (seen in G-UNIT(e2e): 3 anchor steps, then rest). Unpinned by the law; named here.
   The beliefs store, the question doors and the composer never see a prefix (asserted).
3. **D-isolation is a declared bench deviation from the muse bench's world:** the alpha ear-hearsay is
   absent (the law §3's «never the ear» forces it; otherwise M-CHAT's OFF-absent half is unmeasurable).
   Pinned at the tape level in tests/tools/test_content_web_bench.py.
4. **The census is in-memory instrument data** (the law §1: nothing persisted beyond the web's own
   existing state). It zeroes at birth/resume and never snapshots.
5. **The bench's toy carries no ask rows** (the ask w: form is G-UNIT(b)'s pin; the bench measures the
   crossing, which needs eye+chat+outcome only). Named.
6. **One multi-hypothesis sighting** of 240 (the pilot prints it; D-hyp reads the FIRST hypothesis's
   token per sighting — the glance's own order).

## Price (§5)

G-UNIT 17 s; bench 14 s wall ×2 runs (peak 307 MB, the slot ledger's number); identity legs ~2 s + ~4 s
(peaks 92/275 MB); suites below. All inside ≤ 45 CPU-min (bench) / ≤ 10 CPU-min (identity) / ≤ 2 GB and
the ≤ 1.5 CPU-h total.

## Suites on the final bytes (the §5 form; lines read FROM the log files, shas in
records/suite-shas.txt; branch cweb-1010, final bytes 9d42d0e — the records commit; code unchanged
since bc53679)

- genome suite: «Ran 771 tests in 160.972s OK (skipped=1, expected failures=6)» · exit 0 · slot cweb
  suite-genome cap 2G peak 860MB
- tools suite: «Ran 1313 tests in 440.476s OK (skipped=33)» · exit 0 (the 6 new bench tests inside;
  was 1307 at CONTEMPLATE-1) · slot cweb suite-tools cap 2G peak 1631MB
- creature touched-paths subset (the seat's full creature split runs at merge; the builder runs every
  sense path this law's wiring touches — the new G-UNIT file + muse/chat/ask/outcome/replay/hear(s)/
  inner/web/parity/question/mouth): «Ran 206 tests in 401.881s OK (skipped=1)» · exit 0 · slot cweb
  suite-creature-touched cap 2G peak 2048MB (AT the cap — 833MB swap used, green regardless; named,
  measured-first)

## The builder's verdict line

Every gate green; the bench reads M-CHAT PASS, M-COST PASS, M-CROSS/M-GROUND/M-STABILITY/M-NULL FAIL
with the mechanism's numbers printed and both null halves behaving exactly as designed. **The §4 form
is FAIL-FORM — the content keys churn (M-STABILITY 0/16; the toy cannot ground a token that never
recurs).** The instrument is proven (plants caught, identity byte-exact, determinism ×2); the failure
is the declared token form's granularity against the toy's fresh-render canvases — measured on both
sides of the §6 knife-edge (recurrence 0/240, collisions 0/240), reported, never tuned. An amendment
that re-prices the token form or the toy is the seat's road.
