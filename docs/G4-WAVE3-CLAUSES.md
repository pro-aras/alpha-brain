# G4 · WAVE 3 — the clauses, written before any code (edit: Claude (Fable 5.1), 2026-09-20 12:41 +0400)

Law: docs/G4-PREREG.md stands (§1–§16). Nothing below is built before life 2's VERDICT is read (2026-09-21 ~12:15 +04) and its
register line written. Each clause is a gene contract + a toy + a mark with its ceiling and null + the control that would catch a
broken instrument; each lands ONE AT A TIME inside the living creature behind the pin (G4-8) and a G4-9-style replay gate on a
real tape; a failed toy is a finding, never a moved bar. The order at the end is the order of building. His to overturn.

## W3-0 · THE GENERIC REFUSAL (the first line of code; PREREG §14's own rule made structural)
- **Contract:** the mind carries a table of the genes it INTERPRETS (`INTERPRETED_BY_MIND`), the body its own (BODY, TAPE, HEART,
  CRASH, WORLD, ASK, EXAM), the machinery its own (the parser's `required` set + CYCLE + FROZEN + ARRIVAL). At `Mind.__init__`
  every declared gene must be in the union or the organism does not start: `GenomeError("<GENE> is declared but nothing runs
  it")`. The TRAITS refusal of 2026-09-19 23:17 becomes one row of the table.
- **Toy:** a genome declaring INDUCE (today: no interpreter) refuses at start with INDUCE named; the same genome with INDUCE
  `#OFF` starts (positive control); `G4.genome` starts (the life's own genome is the second positive control).
- **Mark:** none — a law. **Control:** a planted gene name added to the parser and not to any table must refuse.

## W3-1 · D-G12 — BELIEF DEDUPE (Alpha 2's scope law: one belief per word; a change is an EXTENSION; a contradiction a CLASH)
- **Reading of life 1:** 762 belief rows for 16 words in 11.5 h — every think pass that answered re-wrote the word's belief
  whole (`believe()` appends unconditionally). Alpha 2's law: a belief is one row per claim; new evidence is appended to it;
  a change of its cell set is an extension row that names the belief; a contradiction opens a clash and never overwrites.
- **Contract:** `believe(word, cells, episodes, moment, path)` reads the word's standing belief first. Same cell set → the
  episodes are appended to the standing row (a REVISIT; the row's `episodes` grows, its line number does not; a `revisits`
  counter). New cells added, none removed → an `extension` row `{kind: "extension", of: <line>, added: [...]}`. Cells REMOVED
  or the word's cells now answering ANOTHER word (the ledger's `words` set for those cells ≠ {word}) → `clash()` as written
  (B11: opens, never overwrites) — the clash half is WIRED by this clause. STATUS gains `beliefs` (standing), `extensions`,
  `clashes`, `revisits` on every write.
- **Toy:** a stream where a word's answer cells are stable → exactly 1 belief + N revisits + 0 extensions; a stream whose
  second half births a new cell for the word → 1 extension; a stream whose second half re-labels the word's cells to another
  word (a planted shuffle of the last 30 ear rows) → ≥ 1 clash. **Control:** the same planted stream under `BELIEF` undeclared
  must write no clash row (the clash half is a gene, not a side effect).
- **Mark (for life 3):** standing beliefs ≤ words met; clashes printed with their cells; every extension traceable by `why`.

## W3-2 · INDUCE / DEDUCE WIRED — a rule is a PREDICTION, filed through FILE's four fields, scored at its due canvas
- **Why this is the road that makes FILE fire:** §14 named the FILE road as unable to fire on the maker's stream because
  `_think_pool` files only for a wordless sight. A RULE is a worded prediction: «the next showing of *w* lights cells C» — it
  has a claim, a route (the next ear-then-eye canvas of *w*), a decider (the resonance of C on that canvas) and a due
  (that canvas's seq). Filed by name or refused by name (B6's law); scored by `_score_due_predictions` at the due canvas.
- **Contract:** the think step's pool gains `rule` items: INDUCE (B11's `induce(episodes, k=5, org)`) runs on a word with ≥ 5
  episodes whose recalled cells agree and no counter-example; its rule is filed as above (`predictions_filed` moves at
  last). DEDUCE (B11's `deduce(beliefs)`) runs on two standing beliefs sharing ≥ 1 cell: «pictures of *w1* will also light
  *w2*'s shared cells» → filed the same way. A scored rule that FAILS lowers CURIOSITY's weight on its item (the outcome
  grades the act); a rule that fails 3 times is PARKED (D39's rule, wave 2's PARK gene, reopened on a new sense).
- **Toy:** the maker's world for 600 canvases → ≥ 5 rules filed, ≥ 3 scored, accuracy printed per rule; **null:** the same
  stream with the ear's words shuffled (`default_rng(5)`, the verdict reader's own twin) → the rules' accuracy at chance
  (≤ 1/11 + noise) — a rule engine that scores well on shuffled words is reading the sight, not the meeting.
- **Mark (life 3):** `predictions_filed` > 0 · `predictions_scored` > 0 · rule accuracy ≥ .80 on the seen eleven ·
  the shuffled-tape twin at chance · PARK ≥ 1 on a rule that cannot be scored (a word shown once — the plant «zog»
  after its five showings is the natural dead end).

## W3-3 · `Interests.sleep_boundary()` WIRED — one line
- `_maybe_sleep` calls `self.interests.sleep_boundary()` after every SLEEP row (B10's contract, §11.1 step 4). Test: a
  recombine chain never pairs an answer from before a sleep with one after it (a planted pair across a sleep must not combine).

## W3-4 · D-G11 — TRAITS, the learning eye, re-designed: same-WORD positives + VISReg (arXiv 2606.02572) — a toy OFF the life first
- **What B12 found (§12):** InfoNCE with two glances of the SAME canvas as the positive learned canvas-INSTANCE identity after
  5 sleeps (margin −0.116 vs raw 0.009) and one learn step dropped a resonating cell under THETA_N (0.964 → 0.701): a head
  changes the space the thetas were measured in.
- **Contract:** `Traits(dim_in=112, dim_out=32)` keeps its interface (`H`, `apply`, `learn`, `version`) and its birth (a seeded
  orthogonal projection). `learn(episodes)` at sleep takes the last ≤ 256 episodes WITH A WORD (the creature's own ear row —
  never the world's truth); positives = episodes of the SAME WORD (the invariance term pulls each episode's z to its word's
  batch mean); the anti-collapse terms are VISReg's, written as the paper writes them: scale `(1/D)Σ(1−σ_j)²` on the centred
  batch, shape = sliced Wasserstein to N(0,1) over K random unit directions (`sort(Z̃w_k)` vs the standard-normal quantiles,
  Z̃ = Ẑ/(sg(σ)+ε)), centre `‖μ‖²`; loss = (1−λ)·invariance + λ·(scale + shape + centre), **λ = 0.6** (the paper's small-data
  default), K = 64 (a 32-d head needs no 4096), lr 0.01, ≤ 20 steps a sleep, batch 256. The SIGReg twin = the same with the
  shape term replaced by the Epps–Pulley sketch (LeJEPA), everything else equal.
- **The thetas move with the head:** after every `learn` that ran a step, gate G-a is RE-RUN IN HEAD SPACE on the maker's
  world's first-fixation glances (within-median → THETA_N_head, floor (between-p95, ear-max), THETA_M_head) and the sight
  area's cos reads the head-space thetas; the head (`H`, `version`, the head thetas) is saved with the snapshot and loaded at
  resume (today it is neither — a resumed mind would run a fresh random head over cells born under a learned one).
- **Toy (OFF the life, on life 1's and life 2's recorded `episodes.npz` — the data already exists):** after 10 learns,
  (a) drawn held-out (seed 2): within-median − between-p95 in head space ≥ the raw front's (must not LOSE bands where the
  raw eye has them); (b) his photographs (`world/`) and the Caltech ten: the margin > 0 (G2's mark, which the supervised
  tower failed at −0.085 raw / −0.111 trained); (c) the instance control from B12 printed: two glances of one canvas vs
  two canvases of one word — same-word similarity must not sit BELOW same-canvas similarity by more than it does in raw
  space (the B12 failure's signature). **Twins:** SIGReg head (same everything); the FROZEN head (no learning) = raw's bands.
  **Null:** shuffled-word positives (`default_rng(5)`) must open no band (margin ≤ the frozen head's + noise). **Ceiling:**
  the bands of the raw 112-d features on the same held-out, printed first (#231: a front's bands before a life).
- **Mark (life 3, only if the toy passes):** the nine on drawn worlds hold (i)–(xi) with the head ON; BANDS on photographs
  reported with the head; the head's thetas in `STATUS.traits` on every write. Their results are on ImageNet-scale data with a
  ViT; ours is 300 photographs and a 32-d head — the toy decides, not the paper.

## W3-5 · SENTENCE — two-word frames from the record, judged by the record
- **Contract:** `SENTENCE two-word frames is near under-judge`: «*w1* is *w2*» when two standing beliefs share ≥ RECALL-k cells
  (the relation read from cells, its `why` = the shared cells); «*w1* near *w2*» when both words were met on ONE canvas's
  episodes — the maker shows one thing per canvas, so «near» cannot fire before the folder/web door (declared not gradable
  until then). A sentence is a row (`kind: "sentence"`, `frames`, `why`), spoken by the voice on the ask door («say»), never
  by a model, never a template filled from the world's truth.
- **Toy:** the maker's world → «is» sentences among the designed near-pairs (circle/ring, square/diamond — G0b's pairs) and
  none between unrelated words; **null:** shuffled beliefs → sentences at chance. **Mark:** every sentence traceable by `why`;
  precision of «is» against the world's designed pairs ≥ .80 (the key outside him).

## W3-6 · THE DOORS and HANDS — the folder door ON first (G4-6), then the web door, HANDS last
- **The folder door (`--folder`, A12; OFF today):** G4-6 = G4-3 re-run with two senses on the tape (the maker + the folder), then
  ON in life 3 with his pictures under `world/<word>/` — the first wordless sights (a picture with no word file) are what PARK
  (a want with no sense), CURIOSITY's door mark and W3-2's FILE road on sights need. Its rule: a folder picture is an eye row
  with `source: folder`; a sidecar word (`<name>.txt`) is an ear row; no sidecar → sight-only (§11.1 step 2).
- **The web door:** Alpha 2's capture road (a page → frames → the folder door's interface), 6 pages an hour chosen by
  CURIOSITY (`WORLD … web 6 per hour by curiosity`); every fetched page is a tape payload (replayable); the seat's net rules
  apply (AF_INET, timeouts, #184). Not before the folder door has run a day.
- **HANDS (`jail alpha3/hands/jail_run`):** last — it needs a program to run, which needs SENTENCE and the web door; declared,
  toy = the jail's own selftest (#230's textsafe) on a planted program; the crash law (#230) stands.

## Order of building (each: toy → pin (G4-8) → a G4-9-style replay gate on a real tape → ON in the next life)
1. W3-0 (the refusal) · 2. W3-3 (one line) · 3. W3-1 (dedupe + the clash wired) · 4. the folder door ON (G4-6) · 5. W3-2
(INDUCE/DEDUCE → FILE fires) · 6. W3-4's toy OFF the life on the recorded episodes (VISReg vs SIGReg vs frozen) · 7. W3-5 ·
8. the web door · 9. HANDS. Life 3 starts after step 3 at the earliest (the smallest set that changes what the verdict reads);
the rest land one at a time inside it, each behind its gate. Two Sonnet 5 builders on separate clauses; Claude holds the law,
the unit, the gates and the verdict reader.
