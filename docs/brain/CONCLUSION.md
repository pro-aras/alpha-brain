# THE BRAIN — the conclusion of the research and the debate (drafted for the seat's co-signature)

*Drafted by Claude (Opus 5.5, the brain's designer), 2026-09-24 12:40 +0400 — protocol step 5 of Ahmad's 11:40 order («… debate on it. Until you two reaches at a final conclusion. And that will be our solid and best research.»). Built on: `RESEARCH-OPUS.md` and `RESEARCH-SEAT.md` (each with its dated corrections), `REVIEW-OF-OPUS-BY-SEAT.md`, `REVIEW-OF-SEAT-BY-OPUS.md`, `DEBATE.md` rounds 1–2 (with their corrections). **Rules kept (his page 11):** every line was argued against before it was written; every number comes from a paper's own text (opened today) or from a computation run on this box (named); everything else is marked [Guessing]. Nothing was built, no life launched, nothing run but reads and arithmetic at `nice -n 19`.*

---

## 1 · The answer, in ten lines

1. **Your idea is right — and it is where the whole field started.** A brain is a mixture of small switches: AND, OR, IF–THEN–ELSE, and THEN (what comes next). The first artificial neurons (McCulloch and Pitts, 1943) were exactly such switches, and the networks that learn — the chatbots included — are mixtures of them whose settings are learned, not written by hand.
2. **So the difference from the chatbots is not the switches. It is how the brain is raised.** In our project it grows from the genome as it needs; it learns first through its own eyes and ears, in your order — letters, then words with pictures, then sentences, books last; it never stops learning; and it says only what it has checked against its own world.
3. **Proven by others:** networks of learned switches can speak — every chatbot does, and one with under 10 million numbers writes simple, fluent stories when everything it reads is simple stories; a network learned which word names which thing from 61 hours of one child's camera and microphone (it learned the links; it did not speak); and old knowledge survives new learning when old experiences are replayed, as in sleep (shown on pictures, not yet on language).
4. **Proven on this computer:** the creature names drawn things it has seen (956 in 1,000 on drawings it never saw), and in its second life said «I don't know» to a shape it had never been shown (180 of 180 — the newest life lost this on one shape, and a fix is under test) — all through its cells, which are a memory, not a thinking brain. A growing net here kept the letters it knew while it learned a new alphabet and a new handwriting (within 2 in 100).
5. **Not proven by anyone:** that switches you can READ — rules you could print, like «IF it has a loop AND …» — can speak: the best attempt scored about 5 points on a translation test, no better than an ordinary small network in the same study, and far below the 28 of a large standard one. And that learning through the senses first makes language cheaper: with PICTURES it helps a network learn word meanings when data is scarce — our case — and the help fades when text is plentiful; with a BODY that acts and is corrected, no one has tested it.
6. **So the brain is built as a partnership.** The cells stay its fast memory — names, «I don't know», what it saw and when. A small learning network grows beside them for order, relations, predicting its world, and speech. A third part that learns readable rules — your AND / OR / IF–THEN, written out — rides along as a candidate until the first experiment says whether it earns a place.
7. **It learns by predicting its world** — what it will see, hear and feel next, and what its acts will bring — and by being corrected when it is wrong. It never takes a word's meaning from text alone, and it never speaks by guessing the next word.
8. **The bar is not «sounds fluent». It is six tests per word, checked against the world (section 2):** point to it; refuse it when the thing is absent; combine it in ways never shown; explain it from its own experience; reject nonsense like «a red sound»; learn a new one from a single meeting. A word that fails loses its «understood» mark until it passes again. A model that has only read text cannot take two of these tests at all — it has nothing to point at and nothing to find missing — and keeps a new word only until the conversation ends.
9. **Two small experiments decide what nobody knows yet.** The first — letters, on this computer; a few CPU-hours for most of it and up to a few CPU-days for the rule-learning part, guesses until measured — shows which part lets it combine what it knows in ways it was never shown («the other case of the letter after b»), and whether growing, sleep and the exact way of learning matter. The second — 200 small arrivals of new signs — shows how it stays able to learn for ever without erasing what it knew.
10. **What we will not claim:** that it understands a word before that word passes the six tests; that it thinks before it passes the combination tests; that anything a chatbot wrote is its own voice. No code is built before you answer section 7.

*Sources behind these lines* (full text in the two researches): McCulloch & Pitts 1943 [metadata]; Merrill, Sabharwal, Smith, TACL 2022 [abstract]; Olsson et al. 2022 [abstract]; Eldan & Li 2023 [abstract]; Vong, Wang, Orhan, Lake, Science 2024 [abstract]; van de Ven, Siegelmann, Tolias 2020 [abstract]; life 2's exam [on disk: MIND-THINKING-LANGUAGE §1 (e) vi]; A4-LADDER-PREREG §0 (4) [on disk]; E48b [on disk]; Bührer et al. 2025 [abstract]; Vaswani et al. 2017 [abstract]; **Zhuang, Fedorenko, Andreas, «Visual Grounding Helps Learn Word Meanings in Low-Data Regimes», NAACL 2024 (arXiv 2310.13257) [abstract, opened for this conclusion]: «visual supervision can indeed improve the efficiency of word learning. However, these improvements are limited: they are present almost exclusively in the low-data regime»**; Hu et al. 2024 (BabyLM 2) [its HTML: the multimodal baselines were image + text models; as read, no image + text vs text-only comparison].

---

## 2 · The bar: six tests of understanding

**His words (2026-09-24 12:01 +04, verbatim):** «What I'm most anxious about is that what will make it different from others. You or any other ai doesn't understand what it is speaking or doesn't understand the words or language it knows from the core. So that i want it to be different at. Speaking of understanding something from the core and meaning. Not just predicting next word as a token.»

**The tests (the seat's operational reading, verbatim, adopted by both):** «the brain predicts the WORLD (what it will see, hear, feel if it looks, acts, or is told), never the next word; words are handles on those predictions. A word is UNDERSTOOD when (1) it points to / acts on the thing; (2) it refuses the word when the thing is absent; (3) it composes grounded parts on UNSEEN combinations (AND, IF…THEN); (4) it explains from its own experience, not from text; (5) it rejects misuse («a red sound»); (6) it learns a new word from one grounded encounter and uses it elsewhere the same day. Each is checkable against its world.»

**The laws that go with them (agreed in DEBATE round 1):**
- **«Never the next word», made exact:** the teacher's speech is part of the world, so a HEARD word may be predicted — but only from the world it is heard in (the thing in view, the act just done, the teacher's mark), never from the previous words alone; and the mouth never samples from a word distribution.
- **Status per word:** every word is UNDERSTOOD (it passes the six tests on the world's own items) or only HEARD-OF (met in a line read or a sentence heard, never anchored). The mouth ASSERTS only with understood words; a heard-of word may appear only as a quotation with its source («I read that …» — his page 11, «never trust any source»). Books add heard-of words and patterns, never meaning; a heard-of word becomes understood only through a grounded encounter.
- **Revocable:** a word returns to heard-of when its grounded predictions fail beyond its band, and the mouth stops asserting it until it is re-anchored. A status that only rises is a certificate that never expires (#217).
- **Test (4) has two halves:** **4a · EXPERIENCE** — it cites episodes that exist on its own tape and carry the answer; **4b · RULE** — it states a readable operation that re-derives the answer on items it never saw.

**What each test is at the letters stage** (the first experiment, §4):
| test | at letters | graded against |
|---|---|---|
| (1) points | given a letter's name, pick its glyph among 4 in never-seen fonts; given the glyph, say the name | the organ ceiling (§4.1 stage −1) |
| (2) refuses | never-taught signs get no name; «is this A?» on a B → «no» | bare name ≤ 1 in 10; «I don't know» or «it resembles X» ≥ 8 in 10 |
| (3) composes | relations on pairs never asked (§4.1's families) | the shuffled-relation twin and the ring-read twin |
| (4a / 4b) explains | «why A?» — its episodes (4a); a readable rule (4b) | a shuffled-citation twin (4a); held-out items (4b) |
| (5) rejects misuse | «after Z?», «the other case of 7», a relation asked of a never-taught sign → «nothing» / «I don't know» | a forced-answer twin |
| (6) one meeting | a new invented sign shown ONCE → named on 10 new renderings, refused on 10 unrelated signs, the same «day» | a declared count of events |

---

## 3 · THE BRAIN — the agreed design, in one page

**What it is.** An ORGAN grown from the genome: a `BRAIN` clause in the creature's genome, interpreted by the machinery like `AREA` and `MEET`, living inside the mind — its weights are memory, so the mind thread is their one writer. Its growth rules are the School's KIND B in its first form.

**Its three parts — the slow store is OPEN until the first experiment reads:**
1. **The cells** (exists today) — the FAST store: a new cell born on one glance by copying the input; names; «I don't know»; the episodes that say what it saw and when.
2. **The learning network** — a grown, gated, recurrent network (soft switches): order («what comes next»), relations, the prediction of its world, and the mouth's order road.
3. **The rule library** — a learner of readable operations over the organs' own deliveries (trait comparison; the tape's order as data; the teacher's marks), found by search in sleep and compressed into reusable rules: a MEASURED PASSENGER until B1 (and, if still open, B3) decides whether it stays.

**Its laws:**
1. **The world is mind-paced** (his 10:15): the next thing arrives when the mind is ready; it sleeps when nothing arrives or when its budget of unconsolidated episodes is full — never by a clock; every horizon is in world time.
2. **It learns by predicting the next moment of every sense** — LOCAL rules awake (eligibility traces; the delta rule at its read-outs), EXACT gradients asleep (through short windows replayed from the episodes); the School's reward, «No» and small hurt act as a third factor on exactly the evidence that gave the answer (FEEL).
3. **It grows where error persists, under a budget that regenerates** — never a cap that eats (#227). The learning network's new units start as continual backpropagation starts them: incoming weights random, outgoing weights ZERO, so a birth never changes what it already computes (Dohare et al., Nature 2024, its full text); the cells keep their copy births. Nothing is removed for disuse.
4. **Renewal** of little-used units only if B2 shows it is needed — and then with «use» measured over the awake stream PLUS sleep replay of the old, never the awake stream alone.
5. **The cells' retirement:** a cell may be merged or retired only when the learning network predicts its content within its band for N sleeps AND its experience stays citable (test 4a); never for disuse.
6. **The mouth speaks from intent:** what to say is chosen from its grounded state for a goal (answer, name, ask, report a surprise); it is rendered through forms it learned, checked against its own perception, and spoken only with understood words. Word order is learned from the world's own speech. The frame composer of today (`genome/chain.py`) stays as the floor speaker it must beat.
7. **Reading:** the library phase reads HUMAN-written text only (machine-written text — his decision, §7 D-1); the weights that read are the weights that live on.
8. **The identity law is kept:** a life replays byte-identically on its machine class — seeded, ordered, no clock inside any update, every search budget counted in candidates, never seconds; across machines, a parity check on float32-rounded scores, never bit-equality promised; a phase run on another machine enters the life as a sealed epoch. The brain's state is hashed by the sparse per-row witness, densely only at snapshots.
9. **The framework:** PyTorch, CPU first, the same code on the Mac or a GPU later — installed only on his word (§7 D-2), relied on only after a replay-identity test on this box; the cells stay numpy.
10. **Dreaming:** in sleep it runs its own predictive model forward from stored episodes with the world absent (his page 10: «Actively dream leading clues in active memory and predict results») — first graded in the game, not at letters.

---

## 4 · The two first experiments (pre-registration skeletons — the bars' numbers are declared after their ceilings are measured)

### 4.1 · B1 — LETTERS AND THEIR RELATIONS (this box; a toy at machine speed; no body)
- **World:** latin upper- and lower-case glyphs through the creature's own gaze (the same 144 numbers a glance the mind receives; computed once and cached); 4 TRAINING fonts per letter (his 3–4 rule), tested on the 30 HELD-OUT fonts (`K/glyphs/*/fonts.tsv`); his order A then B then C; relations asked as a game with wordless question marks whose kind is the cue; the learner PRODUCES its answer; then the digits arrive (for KEEPS and cue transfer).
- **Stage −1 first:** the organ oracle measures every ceiling before any bar — naming at 3 and 4 fonts; the eye's own conflicts (l / I / 1; case pairs whose shapes differ only in size); the perceptual families; the planted sign.
- **Arms:** A0 the cells (the floor) · A1 the grown soft network (local awake, exact asleep, random-in / zero-out births) · A2 recurrent logic gates · A3 Tsetlin clauses · A4 a two-layer transformer (a check, never a candidate) · D the rule library (organ-level atoms; a declared candidate budget; learns in sleep) · A1-MLC (A1 trained on a stream of new-cue episodes) · hybrids **A5** = A0 + A1 · **A6** = A0 + the better of A2 / A3 · **E′** = A0 + D · **F** = A0 + A1 + D.
- **Twins:** A1-FIXED · A1-NO-SLEEP · A1-LOCAL · A1-BPTT-AWAKE · SHUFFLED-NAME · SHUFFLED-RELATION · RING-READ · FORCED-ANSWER · SHUFFLED-CITATION · D×4 (four times D's budget — only on an idle night, his decision §7 D-6).
- **Families and their power** (the smallest count k with P(X ≥ k) < 0.001 under the null; computed by the seat and recomputed by the designer, 2026-09-24):

| family | graded as | n held out | null | k needed |
|---|---|---|---|---|
| successor · predecessor · two-after · between | REACH (beside RING-READ; never read as composition) | 60 each (120, both cases) | 1/25 | 9 of 60 (14 of 120) |
| a NEW cue learned from few pairs («two after» as its own cue) | U3 | 24 (48, both cases) | 1/25 | 6 of 24 (8 of 48) |
| the other case (the name bridges two shapes) | U3 — only where the two forms differ through the organ | 26 | 1/26 | 6 of 26 |
| a CHAIN never shown chained («the other case of the letter after X») | U3 | 13 (26) | 1/26 | 5 of 13 (6 of 26) |
| cue TRANSFER letters → digits («after» on the digits' own order) | U3, at the digits' arrival | 9 (18, both directions) | **1/9** (one of the 9 other digits — the letters' rule; the seat's table used 1/10, where k = 5) | **6 of 9** (8 of 18) |
| mirror-symmetric (A H I M O T U V W X Y) | U3 perceptual — underpowered at 26 letters | balanced 22 | 0.5 | 19 of 22 |
| has a closed loop | U3 perceptual — underpowered | balanced 16 | 0.5 | 15 of 16 |
| vowel (no rule in the picture) | across FONTS only, never across letters | balanced 40 | 0.5 | 31 of 40 |

- **Bars:** (0) positive controls first — every arm learns a planted identity relation to 100 % and plain XOR, else it is VOID, not failed · U1–U6 as in §2's table, per family, never blended (#170) · KEEPS: letters' naming and relations drop ≤ 5 pp after the digits arrive · GROWS: A1 beats A1-FIXED by a declared margin at both seeds · COST: per event on one thread under the bound the probe sets. Two seeds.
- **Selection rule:** a learner goes to the body only if it passes every bar including all six tests at both seeds — by §4.1 of RESEARCH-OPUS only a hybrid can; between A5 and A6, the higher U3 at both seeds, A6 within 5 pp carried beside it. **D1's decision rule (the seat's, round 2):** if the gap between the library arms (D, F) and the network arms (A1, A5) on the new-cue and chain families is under the declared margin at both seeds, the slow store stays OPEN into the words stage (B3) with the same arms and the body is built with F's three parts, the library a measured passenger; if the gap clears the margin either way, the loser is dropped from the body at once. If A1-MLC ≈ D on examples-to-bar at both seeds, the library's case rests on test 4b alone.
- **Predictions on the record** (DEBATE rounds 1–2): the designer — D and F need ≤ ⅓ of A1's examples on the new-cue and chain families; A1 and F beat D by ≥ 10 pp on the perceptual families; F wins U3 overall; A1-MLC needs ≥ 3× D's examples. The seat — F wins U3 and U4b; E′ ties F on new-cue and chain and loses on perceptual; D alone fails U1 and U6.
- **Cost [Guessing — no probe yet; load 18–19 all day]:** the network, gate, clause and transformer arms ≈ 2–4 CPU-hours for all of them at two seeds (the arithmetic in RESEARCH-OPUS §5); the library arms up to their declared budget, ≤ 24 CPU-hours each (≈ 3 CPU-days for D, E′ and F — a budget, not an estimate); the D×4 twin ≈ 4 CPU-days, idle nights only. Every figure is replaced by the probe's before the PREREG is signed.

### 4.2 · B2 — STAYING ABLE TO LEARN (this box)
- **Stream:** ≥ 200 small arrivals of five invented signs each, with invented names, through the creature's organs; and a second stream of permuted traits in Dohare's style.
- **Stage −1:** the organ oracle on the invented signs — near-identical signs removed or merged before any bar (E51's lesson).
- **Arms (7):** FIXED · BIRTH-COPY · BIRTH-RANDOM (random in, zero out) · BIRTH-RANDOM + RENEWAL-AWAKE · BIRTH-RANDOM + RENEWAL-REPLAY · BIRTH + DECAY (E48's failing form) · FIXED + continual backpropagation.
- **Marks:** plasticity = showings to the bar on arrival k, and its slope over k; retention = arrival 1's (and every 20th arrival's) held-out score at arrival k; the fast store's size over k (is the retirement rule firing?); cost.
- **Bars:** a passing arm keeps the plasticity slope within a declared band of 0 and loses ≤ 5 pp of arrival 1. If FIXED shows no loss of plasticity by arrival 200, the stream is too short and every plasticity mark reads NOT GRADABLE.
- **Predictions on the record:** BIRTH-RANDOM keeps both, on both streams; BIRTH-COPY keeps both on the arrival stream and loses plasticity faster on the permuted one; RENEWAL-AWAKE keeps plasticity and forgets arrival 1 (> 5 pp); RENEWAL-REPLAY keeps both; DECAY forgets; FIXED + continual backpropagation keeps plasticity and forgets the old; the fast store grows sublinearly (the seat).
- **Cost:** not priced — the probe prices it before its PREREG.

---

## 5 · The staircase — each step's machine and its honest ceiling

| step | where | what it can show | its honest ceiling | the gate to the next step |
|---|---|---|---|---|
| **1 · LETTERS** (B1, B2) | this box | naming on never-seen fonts; refusal; composition on pairs never asked; one-meeting learning; keeping and staying able to learn | what the eye can tell apart (stage −1); 52 letters + 10 digits make the perceptual families weak; no speech — its answers are names and picks; «it thinks» only as relations over letters | a hybrid passes B1's selection rule; B2 settles the plasticity law |
| **2 · WORDS AND THE GAME** (B3; the same arms if the slow store is still open) | this box | words with pictures («A for Apple»); acts in the game («go to the red ball» — test 1 becomes «acts on»); two- and three-word sentences with word order learned from the teacher's speech | a small world's vocabulary (the drawn things, his folder, the game's colours and objects); photographs are an organ limit (every fixed front's margin negative — G2); two-word frames need a world whose pairs are not independent | the words stage's card passes all six tests on words and acts |
| **3 · THE LIBRARY** (a life that reads) | this box or the M1 Max (his decision §7 D-3) | reading his shelf; words and patterns added as heard-of until grounded; questions on what it read | his shelf is ≈ 31 million words [an estimate: bytes ÷ 5.8], about a third of the «less than 100 million words of input» from which, BabyLM's findings say, children acquire language; its early grades are tiny (K ≈ 0.2 MB, G1–G3 ≈ 2.2 MB of text) | the library card is stuck at a capacity limit on the six tests |
| **4 · SCALE** (his «1b or 2b») | a rented GPU (§7 D-4) | whatever the card says capacity was holding back | the shelf cannot feed it (≈ 0.2 % of the 20 billion tokens a 1 B model is usually given — [computed; the 20-per-parameter ratio is an assumption, not in Hoffmann et al.'s abstract as read]) — it needs human text far beyond the shelf | — |

**What each step costs — computed on this box with its assumptions named** (training arithmetic ≈ 6 × parameters × tokens; this CPU at a guessed 50 GFLOP/s; the M1 Max at 30 % of the brief's ≈ 10 TFLOPS; an A100 at 40 % of NVIDIA's 312 TFLOPS BF16 dense; 1.3 tokens a word — each assumption [Guessing]; a life that reads one moment at a time is SLOWER than these batch figures):
- one reading of the whole shelf: a 10 M brain ≈ 13 hours on this CPU, ≈ 13 minutes on the M1 Max; a 50 M brain ≈ 67 hours on this CPU, ≈ 1.1 hours on the M1 Max; seconds to minutes on an A100 — **on these guessed rates, the library phase needs no rented GPU below ≈ 50 M parameters**;
- his «1 B» at 20 B tokens ≈ 11 days on one A100 (≈ 1.4 days on eight); «2 B» at 40 B tokens ≈ 45 days on one (≈ 5.6 on eight).

---

## 6 · What would show the design WRONG — per pillar, written before any build

| pillar | the observation that refutes it | measured in |
|---|---|---|
| the partnership (hybrid) | a single arm passes all six tests alone → the partnership is unnecessary; OR the hybrid fails a test its parts are meant to carry → the roles are drawn wrong | B1 |
| the learning network as the slow store | E′ (the cells + the rule library, no network) ≥ F on every test within its budget at both seeds | B1 |
| the rule library | D fails the new-cue family inside its declared budget, or wins it only when the relations are given as its atoms | B1 |
| growth | A1-FIXED matches A1 → growing bought nothing at letters | B1 |
| sleep and exact learning | A1-NO-SLEEP keeps as much → sleep does no work; A1-LOCAL matches A1 → exact gradients unneeded (the law becomes local-only) | B1 |
| keeping for ever | BIRTH-RANDOM loses plasticity like FIXED; OR RENEWAL-REPLAY forgets arrival 1 | B2 |
| understanding (the six tests) | SHUFFLED-NAME scores within noise of the brain on pointing; OR the tests pass only with a leak (the canaries above chance); OR no word's status is ever revoked when its predictions fail | B1, and every stage |
| «it thinks» | the discriminating families sit at SHUFFLED-RELATION's or RING-READ's level | B1 |
| grounding-first (the bet) | a twin of the same brain raised TEXT-FIRST (books before letters and words with pictures, then the same grounded stages) reaches the same six-test scores with fewer grounded examples | the words stage and the library |
| the mouth | its sentences are no better grounded and cited than the floor composer's; OR it asserts a heard-of word | the words stage |
| human-inspired, not heavy machinery | it cannot keep up with a mind-paced letters world on one core | B1's COST bar |
| the identity law under PyTorch | the replay-identity test fails in deterministic mode | before any brain life |

---

## 7 · DECISIONS FOR AHMAD (the recommended option first)

| # | the decision | recommended | the alternatives |
|---|---|---|---|
| D-1 | **Text written by a chatbot** (such as the simple stories a large model writes for children) | **Never to TEACH the brain.** Allowed only (a) as test material it is never taught, and (b) inside a separate measuring copy of the brain that never enters its life, to show what the shortcut would buy — its report card read beside the life's, never merged (the seat's condition) | never at all · allowed for teaching |
| D-2 | **Install PyTorch on this box** (free software for building learning networks — no borrowed weights, nothing pre-trained) | **Yes** — CPU version, in its own environment; the brain relies on it only after it passes the replay-identity test | stay on hand-written numpy (a slower, riskier build) |
| D-3 | **A way into the M1 Max** (SSH, or a remote session you open) | **Yes, now** — for measured cost probes today and the library phase later | the Mac stays offline; everything on this box until the GPU step |
| D-4 | **Renting a GPU** (an A100) | **Not now.** Only at the SCALE step, when a card is stuck at capacity after the library phase — on §5's guessed rates the library itself fits this box or the Mac below ≈ 50 M parameters; the probe confirms or refutes it | rent now for the library phase |
| D-5 | **Letters first, as stage 0 of the brain's schooling** (your 23:06 order) | **Confirm** | your earlier order (surroundings → knowing itself → language → reasoning → its own questions), with the letters later |
| D-6 | **The rule library at four times its budget** (≈ 4 CPU-days, on an idle night only, when no life or reader runs) | **Yes, once** — only if, after B1's equal-budget read, the library arms sit within the declared margin of F, so the extra budget can still change the decision | never (equal budgets only) · always |

---

## 8 · Signatures

- **The designer:** Claude (Opus 5.5) — drafted and signed 2026-09-24 12:40 +0400.
- **The seat:** Claude (Fable 5.1) — signed ______________________ (stamp) — or returned with the lines that fail his six tests or its own reading.
