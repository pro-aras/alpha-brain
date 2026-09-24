# B1 · BUILDER 1 (Opus 5.5) — arm D, THE RULE LIBRARY — report

*edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:32 +0400 (amended 2026-09-24 16:38 +0400 after the advisor's review: cue-op
cycles, the skip/restart rule, PICK membership, `state_sha`'s scope, R9, §4.1) — §1–§4 written ON PAPER while `brain/protocol.py`
is not yet on `b1-integration` (checked 16:24: `git -C /data/dev/genome-wt-b1int log --oneline -3` → 94546ce, no
`brain/`). No arm code exists yet; nothing below is a measurement of D except where a command is named.*

**Law read whole first:** `docs/brain/B1-PREREG.md` (94546ce), `CONCLUSION.md` §2–§4 and §9, `DEBATE.md` D1/D7/D8,
`RESEARCH-SEAT.md` §1 (item 5) and §3, `RESEARCH-OPUS.md` §2.3 (c), `REVIEW-OF-SEAT-BY-OPUS.md` §B1–B5,
SOLUTIONS #171 #191 #194 #214 #228 #232–#239.
**Builder 2's UNCOMMITTED draft** `brain/protocol.py` / `brain/glance_cache.py` (in `/data/dev/genome-wt-b1-harness`,
untracked) was read at 16:2x for AWARENESS only; every shape this design leans on is re-checked byte for byte against
the FROZEN commit on `b1-integration` before a line of arm code is written (#194, #235).

---

## 1 · What D is (the PREREG's row, restated as the design implements it)

D is a program learner. For every cue mark it has seen, it keeps ONE current program — the best-fitting program
found by an enumerative search over a typed DSL — and a LIBRARY of named operations that grows by compressing
sub-programs that recur across the cues' programs. It learns ONLY in sleep; awake it records and answers.

- **Awake (`fit_event`)** — TEACH → appends `(seq, glance_row, name)` to its data memory (`order`, `taught`);
  training ASK → held as pending; FEEDBACK → pairs the shown RIGHT answer with its ASK into an EXAMPLE of that
  ASK's cue (the valence argument is ignored — D reads the shown answer, never its own valence, so its state
  after every row is a pure function of the tape). `answer(..., learn=True)` changes nothing (D learns from the
  FEEDBACK row, never from its own answer).
- **Asleep (`sleep`)** — (1) SEARCH: for each cue with examples, enumerate programs by size then lexicographic
  order until the first program that reproduces ALL of the cue's examples, or until the cue's share of the
  sleep's CANDIDATE budget is spent; keep the best (most examples reproduced; ties → smaller; then earlier in
  the lexicographic order). (2) COMPRESS: over the corpus of the cues' current programs, add the top-k
  abstractions by compression gain (Stitch-shaped, §3). (3) Write the sleep's record to the library log and,
  when configured, the snapshot E′ and F load.
- **Answering** — a single cue → its program, evaluated on the ask's operands (and candidates); a compound cue
  (CHAIN = [AFTER, OTHER_CASE]) → `compose` of its parts' programs in order (D never sees CHAIN in training);
  no program, a program under the fit floor (§4 R1), a program that raises, or a type that does not match the
  ask's answer kind → NOTHING.
- **`rule(cue)`** → the program's text (library entries named, their definitions listed) and an executable that
  runs exactly that frozen program on an ask row. **`why(ask)`** → the tape seqs of the examples the answering
  program(s) were fitted on (§4 R5 on what this means for U4a).
- **No clock anywhere in a decision.** The search is counted in candidates; `cost()`'s milliseconds (the
  protocol's own `{"events", "ms"}`) are measured outside every decision and never hashed.

## 2 · The DSL — atoms, combinators, grammar, enumeration order

### 2.1 Types
`G` a glyph (a glance-cache row: its 5 × 144 percept) · `N` a name (a heard ear-word) · `Z` an integer · `R` a
real · `B` a truth value · `[G]`, `[N]` finite lists. Every program for a cue has the cue's REQUEST TYPE:
its operands' types in order (`x0`, `x1`, … — `G` for a glyph row, `N` for a heard name), plus `cands : [G]` when
the ask is a PICK, → the answer kind's type (NAME → `N`; PICK → `G`, returned as its index in the ask's own
candidate list; YES/NO → `B`). Programs are keyed by (cue mark, request type), so a cue asked in two shapes
keeps two programs and never applies one to the other's shape.

### 2.2 The atoms — ORGAN-LEVEL only (PREREG §4 row D; DEBATE D8)
| atom | type | what it is — data from the organs or the tape, never a tested relation |
|---|---|---|
| `sim` | `G → G → R` | the trait comparison: the cosine of the two glyphs' **F_pool** vectors — the creature's own BIND pooling (`creature/mind.py:_bind_pool`: the mean of the 5 glances, unit-normalised; PREREG §3.3). Computed in fixed point (each component rounded to a multiple of 2⁻²⁶, the dot product EXACT in int64, then ÷ 2⁵²) so the value of a pair never depends on which batch computed it (the identity law; §4 R7). |
| `taught` | `N → [G]` | the TEACH exemplars of a name, in tape order (data). |
| `order` | `[N]` | the tape's TEACH sequence of names, in tape order, repeats kept (DATA — never an «after» operator). |
| `x0, x1, …`, `cands` | per request | the ask's own operands and candidate sheet. |
| `@C` (the cue kinds seen) | the request type of cue C | the CURRENT program of an already-fitted cue C, callable as an operation (late-bound: always C's current program). This is how «the teacher's marks» enter as atoms: the MEANING of a mark is only ever D's own learned program for it. |

**Why none of them is a tested relation.** The tested relations are AFTER, BEFORE, BETWEEN, TWO_AFTER,
OTHER_CASE, CHAIN, TRANSFER, MIRROR, LOOP, VOWEL (§5.2). `order` is a list of names, not a successor operator —
«after» must be FOUND as `nth(order, add(index_of(order, ·), 1))`; `sim` compares two percepts and names
nothing; `taught` is the teacher's pairing of name and percept (the NAME game's own data); a cue op `@C` exists
only after D has fitted C from C's own shown answers. The numeric constants are `0` and `1` only — `2` is
deliberately absent, so «two after» is not a one-token edit of «after» and must come from composition (the
library's claim, DEBATE D1) or from `add(add(·, 1), 1)`.

### 2.3 The generic combinators (declared; nothing else)
`argmax : [T] → (T → R) → T` and its value twin `maxof : [T] → (T → R) → R` for T ∈ {N, G} (ties → the FIRST
element; an empty list raises) · `eq : N → N → B` (equality on names) · `index_of : [N] → N → Z` (the first
occurrence; absent raises) · `nth : [T] → Z → T` (0-based; negative or past the end raises) · `add, sub : Z → Z → Z`
· the constants `0, 1 : Z` · `not : B → B`, `and, or : B → B → B` (his AND / OR as literal gates) ·
`b2r : B → R` (1.0 / 0.0 — so argmax can select by a truth value) · `compose(F, G)` — a whole-program form over cue
operations: `compose(@C1, @C2)(operands, cands) = @C2(bridge(@C1(operands)), cands)`, nestable
(`compose(@C1, compose(@C2, @C3))`); `bridge` is the identity when the types agree, and for a NAME fed where a
GLYPH is expected it is the name's FIRST TEACH exemplar (`nth(taught(n), 0)`, both atoms); any other mismatch
raises. **Declared absent:** `if`, comparisons on reals (`gt`/`lt`), `2` or any other constant, list length,
map/filter, any access to the teacher's shown answers as data (§4 R4), any access to a cache row's index
record (the index carries the character — only the glance array is ever read).

λ binders appear only as the function argument of `argmax` / `maxof` (one new bound variable of the list's
element type); they are forced by the type and are not counted in a program's size.

### 2.4 The enumeration (by size, then lexicographic — PREREG §4 row D)
- **Size** = the number of symbols (primitives, constants, inputs, bound variables, library entries, cue ops).
- **Order within a size** = the lexicographic order of the program's prefix token sequence under one declared
  token order: the base primitives in the order of §2.3's list (`order, taught, sim, argmaxN, argmaxG, maxofN,
  maxofG, eq, index_of, nthN, nthG, add, sub, 0, 1, not, and, or, b2r`), then library abstractions by creation,
  then cue ops by the seq of their cue's first example, then `compose`, then the inputs (`x0, x1, …, cands`),
  then bound variables by de Bruijn index. Generated token by token (leftmost hole first), a branch pruned the
  moment the remaining size cannot fill the pending holes (a DP table of fillable sizes per type and binding
  environment) — so the generator emits EXACTLY the size-then-lexicographic order, no sort, no set.
- **Scale, before any library** (a design-aid counter over this base grammar, `nice -n 19 /usr/bin/python3
  count_dsl.py 18` in the builder's scratchpad; to be re-derived by the arm's own enumerator): programs of
  request type `G → N`, cumulative to size 8 = 97 (the 1-nearest-exemplar NAME program is size 8:
  `argmaxN(order, λn. maxofG(taught(n), λe. sim(x0, e)))`), to size 14 = 109,058 (AFTER from scratch is size 14),
  to size 16 = 1,355,032 (TWO_AFTER from scratch); `(G, [G]) → G` cumulative to size 15 = 1,406,297 (OTHER_CASE
  from scratch is 15). With the library the same programs are 5–8 symbols (§3), and TWO_AFTER is
  `compose(@AFTER, @AFTER)` — 3 symbols.

### 2.5 The fit, the stop rule, the answer
- **The score** of a program on a cue = the number of the cue's examples it reproduces exactly (a raise on an
  example = not reproduced). **Best** = the highest score; ties → the smaller; then earlier in the order.
- **Stop:** a cue's search stops at the FIRST program reproducing all of its examples (that program is the
  smallest, then lexicographically first, of all perfect programs — nothing later can beat it); otherwise it
  spends its share (§2.6).
- **`fits_all`** (F's router: «D has a program that fits all of the cue's training examples») = score = n.
- **D's own answer floor** — RAISED (§4 R1); implemented as a config value, default a STRICT MAJORITY of the
  cue's examples (the PREREG's own «known» rule, §5.1).
- **A PICK answer is a member of the ask's own sheet, by row identity:** a program of type `G` that returns a glyph
  not in `cands` (e.g. `nth(taught(n), 0)`, a taught exemplar) scores 0 on that example and answers NOTHING.
- **Cue ops never cycle.** When cue C is searched, the available cue ops are those of the OTHER fitted cues whose
  current program does not reference C, directly or through another cue op or a library entry (a reference graph
  kept acyclic by construction) — so C never sees `@C` as a 2-symbol «perfect» program of itself.
- **Which cues a sleep searches, and from where.** A cue is searched iff it has no perfect program AND (it has
  examples it has not been searched with OR the token set — library entries, cue ops — changed since its last
  search); otherwise its search would return the identical program (the search is a pure function of those two
  inputs), so it is skipped and its skip is logged. A searched cue RESTARTS from size 1 under the current library
  (that restart is the library's payoff — AFTER is 8 symbols over `name`, not 14 from scratch); a cue whose
  current program still reproduces every example, new ones included, keeps it untouched. Within ONE sleep, pass 2
  continues a cue's own enumeration where pass 1 stopped (the token set does not change inside a search phase).
- **One sleep = one DreamCoder iteration:** search every cue that needs it, THEN compress once (top-k). The
  consequence is computed, not hoped (to be done on the real tape's SLEEP positions): the first sleep that holds
  relation examples must find AFTER from scratch (size 14; 109,058 candidates cumulative before the library) or
  wait one sleep for the naming abstraction (then 8 symbols). PREREG §2.7 puts a SLEEP every 500 events and L4 is
  ≈ 3,500 events, so ≈ 7 sleeps fall inside L4 before T_L.

### 2.6 The budget — counted in candidates, never seconds
- A **candidate** = one complete, well-typed program handed to the evaluator (pruned partial programs are not
  candidates; every evaluated program is, whether it raises or not).
- `candidates_per_sleep` is a config number — the PREREG's formula ⌊24 CPU-hours ÷ (the probe's seconds per
  candidate) ÷ the number of sleeps⌋ is computed by the seat after §3.5's probe; D never reads a clock to know it.
- **Within a sleep:** the cues with examples, ordered by their first example's seq, each get
  ⌊budget ÷ n_cues⌋ (pass 1); what the cues that stopped early leave is pooled and split equally over the cues
  still without a perfect program, each continuing its own enumeration where it stopped (pass 2); what is left
  after pass 2 is recorded as UNSPENT. Deterministic by construction.
- **On the record, per sleep, as a SERIES** (#233 / #237 / #238): budget · spent per cue · unspent · per cue its
  best score / n and whether it stopped perfect or exhausted its share ("refused": searched to its share with no
  perfect program) · the abstractions added and their gains · the snapshot's sha.

### 2.7 The evaluator (its cost is program-shaped, so its two memos are load-bearing)
- **Column-wise over examples:** a program is evaluated for all of a cue's examples at once; every value is an
  array over examples with a validity mask (a raise on one example marks that example, never the batch). A single
  ask at answer time goes through the SAME code with one column — so an answer never depends on the batch it
  was computed in (a test pins it).
- **Distinct elements once:** `argmax` / `maxof` over a list with repeats evaluate the body once per DISTINCT
  element in first-occurrence order (exact: repeats score identically and ties go to the first) — at letters
  `order` holds 624 entries but 26 names.
- **The sim table:** `sim` values come from one integer table over the glance rows a cue's search touches
  (exact int64 products, so any batch gives the same bits); derived, rebuilt on demand, never hashed.
- **The subtree memo:** within one cue's search, a closed subtree's value under a given binding of its bound
  variables is computed once and reused across candidates (the NAME-shaped resemblance under 26 names is
  shared by every candidate that contains it). §3.5's 100-candidate cost sample prints its SIZE distribution
  and whether the memo was cold or warm beside the seconds, so the number describes the search, not a cold start.

### 2.8 What `state_sha` hashes (and what it must not)
- **Hashed** (canonical JSON, sorted keys, no clock): the data memory (every TEACH row's seq, glance row and name, in
  order); the training ASKs still awaiting their FEEDBACK (a snapshot at event 1,000 can fall between the two — the
  resume leg of §3.1 needs them); every recorded example (ask seq, feedback seq, cue, request type, operands,
  candidate rows, the shown right answer); the library (each abstraction's body text, arity, type, the sleep that
  added it); every cue's current program (text, score, n, size, the sleep it was found in, the token-set version
  and example count it was searched with); the sleep index.
- **Never hashed:** the sim table and every memo (derived from the read-only cache, rebuilt on demand); the F_pool
  vectors; the cost counters; the library LOG (written to `run_dir`, a record, not state).

## 3 · The compressor (Stitch-shaped: top-k by compression gain per sleep)
- **Corpus:** the current program of every cue (as written in the current library).
- **Candidate abstractions:** the anti-unifier of every ordered pair of subtrees in the corpus (the most specific
  pattern: equal heads recurse, differing subtrees become holes, one hole per distinct differing pair). A
  program input (`x0`, `x1`, `cands`) or a bound variable whose binder lies OUTSIDE the subtree always becomes a
  hole (an abstraction is closed); a hole may not sit under an internal binder if its filler would capture that
  binder's variable. Kept only if the body has ≥ 2 non-hole symbols, ≤ 3 holes, and is well-typed.
- **Gain** = (the corpus's total size before − after rewriting every match top-down, leftmost-outermost,
  non-overlapping, by `A(fillers)`) − the size of A's body. **Top-k** (k = 3, declared, not tuned): greedy — take
  the best gain > 0 (ties → smaller body, then its text), rewrite the corpus with it, recompute, repeat. Library
  entries are never removed (growth by compression; nothing is erased for disuse — #227).
- **What it should find at letters (a prediction from the arithmetic, not a measurement):** from NAME, SAME, IS
  and POINT, the resemblance `λg n. maxofG(taught(n), λe. sim(g, e))` and then the naming
  `λg. argmaxN(order, λn. res(g, n))`; from AFTER / BEFORE / BETWEEN, the position `λg. index_of(order, name(g))`
  and `λi. nthN(order, i)`. The relations themselves are then 5–8 symbols and are FOUND, never given.

## 4 · Clauses RAISED to the seat (implementable choices the PREREG does not settle; each a config value or a
## declared default until the seat's word — never worked around)
- **R1 · What «fits» means for D's own answer.** The row says «answers with the best-fitting program … (ties →
  the smallest …)» and «no program fits the cue's examples … → NOTHING»; F's router says «fits ALL». Read as
  «reproduces every example», perception noise on a single training rendering (the 1-nearest-exemplar naming
  inside every relation program) silences D on that cue entirely. Default implemented: D answers when its best
  program reproduces a STRICT MAJORITY of the cue's examples; `fits_all` (score = n) is exposed for F's router.
- **R2 · The probes P1–P4 and the sleep points (#228 (a)).** D learns only in sleep, and E′ and F load D's
  snapshot only at a SLEEP. PREREG §2.7's sleeps are after L1, L2, L4, L5 and every 500th event; L5 is ≈ 36 asks +
  36 FEEDBACK rows (3 pairs × 2 cases × 6 rounds), so at most one sleep can fall between P1 and P4. D's (and
  E′'s and F's) examples-to-bar on TWO_AFTER would then read «> 36» by the SCHEDULE, not by the mechanism.
  To verify on the real tape's printed counts; the remedy is the world's (a SLEEP after each L5 round), or the
  mark reads NOT GRADABLE for the sleep learners — the seat's decision.
- **R3 · §3.1's planted divergence may land outside its window.** «the first TEACH row at or after event 1,234»:
  by PREREG §2.7's counts the TEACH rows are L1 + L2 (624) and `zog` (≈ event 627); L4–L6 carry none, and the digits'
  TEACH rows begin after T_L (≈ event 4,400). If so, the plant falls beyond the first 2,000 events and EVERY
  arm's planted control reads «no divergence» — a control that cannot fire. To verify on the real tape; a
  plant on the first ASK operand at/after 1,234 would land (it changes D's recorded example at once).
- **R4 · The perceptual families have no expressible program over the declared atoms.** MIRROR / LOOP / VOWEL
  answers are properties of a FORM or a category the atoms never carry (only name identity is expressible,
  and a vowel set would need ≈ 50 symbols); D's reading there will be the majority class or NOTHING. An atom
  «the teacher's shown examples as data» would let D compare traits with them — but it would also let D FIT
  every relation by recalling another rendering of the same trained item (each is asked 6 times), and the
  lookup (≈ 6 symbols) beats the relation (≈ 8) on size at an equal, perfect score — D would stop generalising.
  Not implemented; the seat's decision if it wants the designer's «D's comparisons over traits» there.
- **R5 · `why()` and U4a.** Implemented literally: «the tape seqs of the examples the program was fitted on»
  (the FEEDBACK seqs of the answering cue's examples; a compound: both parts'). U4a counts only TEACH rows, so
  D alone reads 0 on U4a BY CONSTRUCTION (E′ and F take `why()` from A0, so no decision moves). A why() that
  cites the TEACH rows the answer READ (the winning exemplar of the naming; the order positions) is buildable;
  not built without the seat's word.
- **R6 · `candidates_per_sleep`** is the seat's number after §3.5's probe; the toys and the identity test run at
  small declared budgets, named beside every number they print.
- **R7 · `sim` in fixed point** (2⁻²⁶, exact integer dot) — the cosine differs from float64's by ≤ ≈ 10⁻⁶ and is
  identical under any batching, order or process (the resume leg of §3.1 needs this). Declared, not a raise.
- **R9 · The snapshot seam with Builder 2 (E′ and F «load D's own snapshot at each SLEEP by sha»).** Neither the
  PREREG nor the protocol draft names WHERE D's per-sleep snapshot lives or where its sha is recorded. Proposed
  (not unilateral): D writes `run_dir/library/sleep-<k>.json` at the end of its k-th sleep and records its sha256
  in the library log's row for that sleep; a config `library_load_from = <that directory>` makes an instance's
  `sleep()` LOAD sleep k's snapshot (verifying the logged sha) instead of searching. The router is Builder 2's;
  the seat settles the path.
- **R8 · The data can wrap.** `order` keeps its repeats (24 rounds of letters), so `nth(order, index_of(order,
  "z") + 1)` = «a» (round 2's first name): D will NOT refuse «AFTER z» or «TWO_AFTER y, z» (U5), while
  «BEFORE a» raises and is refused. A finding of the data atom, recorded, not engineered.

### 4.1 Predicted findings (facts of the design, said before any run — not defects)
- **(a) No refusal road but a raise.** Comparisons on reals are declared absent, so the naming inside every
  program always names SOMETHING: on U2 (never-taught signs) and on most of U5, D will read like FORCED-ANSWER,
  except where an index raises (BEFORE a; a name with no exemplar) — and R8's wrap removes AFTER z / TWO_AFTER y, z.
- **(b) `glyph(x)` is folded into `G`.** The PREREG lists `glyph(x)` (the 5 × 144 matrix) as an atom; the DSL
  reaches a percept ONLY through `sim` on F_pool — per-glance and per-dimension access are gone (a reduction of the
  declared list, chosen because a rule over 144 continuous numbers needs learned thresholds — REVIEW-OF-SEAT §B5 —
  and thresholds are declared absent).
- **(c) D reads its data memory LIVE.** A program reads `order` / `taught` at answer time, so a TEACH row is usable
  the moment it is recorded — the U6 plant `zog`, taught once in L3, is nameable by the same naming program with
  no sleep between; one exemplar, so its ceiling is the 1-exemplar oracle's (§3.3).

## 5 · The toys, the identity test, the cost (to be filled from runs whose commands are named)
*(pending the frozen protocol, the cache, and code)*
